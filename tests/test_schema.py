from pathlib import Path

import httpx
import pytest

import mcp_okn.schema as schema_mod
from mcp_okn.schema import (
    _build_schema_from_metadata,
    _generate_query_template,
    _member_type,
    _should_exclude_uri,
    build_mermaid_diagram,
    infer_edge_labels,
    parse_entity_metadata,
    usage_notes,
)
from mcp_okn.void_schema import void_is_stale


def _parse(csv_text: str) -> dict[str, dict]:
    """fetch_entity_metadata's CSV parsing, without the network."""
    return parse_entity_metadata(csv_text)


SIMPLE_CSV = """\
URI,Label,Description,Type
http://schema.org/Person,Person,A human being.,Class
http://schema.org/name,name,The name of the thing.,Predicate
"""

EDGE_CSV = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
https://ex.org/schema/Gene,Gene,A gene.,Class,,,
https://ex.org/schema/Sample,Sample,A sample.,Class,,,
https://ex.org/schema/MEASURED_EXPR,MEASURED_EXPR,Expression edge.,Predicate,,Sample,Gene
https://ex.org/schema/log2fc,log2fc,Log2 fold change (float).,EdgeProperty,MEASURED_EXPR,,
https://ex.org/schema/pval,pval,P-value (float).,EdgeProperty,MEASURED_EXPR,,
"""


def test_build_schema_classes_and_predicates():
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    assert schema["classes"]["count"] == 1
    assert schema["classes"]["data"][0][0] == "http://schema.org/Person"
    assert schema["predicates"]["count"] == 1
    # No edge properties -> the predicate is not flagged.
    pred_row = schema["predicates"]["data"][0]
    has_edge_props = pred_row[
        schema["predicates"]["columns"].index("has_edge_properties")
    ]
    assert has_edge_props is False
    assert schema["edge_properties"] == {}
    # Compact omits the summary.
    assert "edge_property_summary" not in schema


def test_build_schema_edge_properties_and_template():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=False)
    edges = schema["edge_properties"]
    assert "MEASURED_EXPR" in edges
    edge = edges["MEASURED_EXPR"]
    assert edge["source_class"] == "Sample"
    assert edge["target_class"] == "Gene"
    assert {p["label"] for p in edge["properties"]} == {"log2fc", "pval"}
    # The predicate carrying edge properties is flagged.
    pred_row = next(
        r for r in schema["predicates"]["data"] if r[0].endswith("MEASURED_EXPR")
    )
    idx = schema["predicates"]["columns"].index("has_edge_properties")
    assert pred_row[idx] is True
    # Non-compact prepends the edge-property summary.
    assert "edge_property_summary" in schema
    # The generated template uses RDF reification scoped to the KG schema NS.
    tmpl = edge["query_template"]
    assert "rdf:subject" in tmpl
    # The relationship's own IRI, not schema:<label> in the KG's purl namespace
    # (wildlifekn's https://wildlife.proto-okn.net/kg/OBSERVED_AT was mis-templated).
    assert "rdf:predicate <https://ex.org/schema/MEASURED_EXPR>" in tmpl
    assert "purl.org/okn/frink/kg/demo/schema/" in tmpl


def test_edge_property_of_accumulates_multiple_parents():
    csv_text = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
https://ex.org/schema/adj_p,adj_p,Adjusted p-value.,EdgeProperty,EXPRESSION,,
https://ex.org/schema/adj_p,adj_p,Adjusted p-value.,EdgeProperty,ABUNDANCE,,
"""
    meta = _parse(csv_text)
    assert (
        meta["https://ex.org/schema/adj_p"]["edge_property_of"]
        == "EXPRESSION;ABUNDANCE"
    )


def test_generate_query_template_shape():
    props = [
        {"uri": "https://purl.org/okn/frink/kg/demo/schema/score", "label": "score"}
    ]
    tmpl = _generate_query_template("demo", "RELATES", "Foo", "Bar", props)
    assert "SELECT ?foo ?bar ?score" in tmpl
    assert "schema:RELATES" in tmpl
    assert "GRAPH <https://purl.org/okn/frink/kg/demo>" in tmpl
    assert tmpl.rstrip().endswith("}")


def test_generate_query_template_properties_optional_by_local_name():
    # Edge properties are sparse, so each must be OPTIONAL; a prose label must
    # not leak into the predicate or variable (spoke-okn "Activity Sources").
    ns = "https://purl.org/okn/frink/kg/demo/schema/"
    props = [
        {"uri": ns + "act_sources", "label": "Activity Sources"},
        {"uri": ns + "phase", "label": "Phase"},
    ]
    tmpl = _generate_query_template("demo", "TREATS", "Chem", "Disease", props)
    assert "OPTIONAL { ?stmt schema:act_sources ?act_sources }" in tmpl
    assert "OPTIONAL { ?stmt schema:phase ?phase }" in tmpl
    assert "Activity Sources" not in tmpl
    assert "rdf:object ?disease ." in tmpl


def test_generate_query_template_same_class_gets_distinct_vars():
    props = [{"uri": "https://purl.org/okn/frink/kg/demo/schema/odds", "label": "Odds"}]
    tmpl = _generate_query_template("demo", "RESEMBLES", "Disease", "Disease", props)
    assert "rdf:subject ?disease_1" in tmpl
    assert "rdf:object ?disease_2" in tmpl


def test_should_exclude_rdf_syntax_uris():
    assert _should_exclude_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#_1")
    assert not _should_exclude_uri("http://schema.org/Person")


def test_member_type_extracts_trailing_parenthetical():
    assert _member_type("Log2 fold change (float)") == "float"
    assert _member_type("Adjusted p-value (FDR-corrected). (float)") == "float"
    # No usable type -> empty (don't treat a sentence in parens as a type).
    assert _member_type("Some prose (with several words)") == ""
    assert _member_type("plain description") == ""


def test_build_mermaid_diagram_edges_and_intermediary_classes():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    diagram = build_mermaid_diagram("demo", schema)
    assert diagram.startswith("classDiagram")
    assert "direction TB" in diagram
    # Node classes appear as boxes.
    assert "class Gene" in diagram
    assert "class Sample" in diagram
    # The edge-property predicate becomes an intermediary class with typed fields,
    # wired source --> edge --> target.
    assert "class MEASURED_EXPR {" in diagram
    assert "float log2fc" in diagram
    assert "Sample --> MEASURED_EXPR" in diagram
    assert "MEASURED_EXPR --> Gene" in diagram
    # Node classes are light blue; the edge class is orange.
    assert "style Gene fill:#BBDEFB" in diagram
    assert "style Sample fill:#BBDEFB" in diagram
    assert "style MEASURED_EXPR fill:#FFE0B2" in diagram
    # A two-entry legend (node + edge) is included.
    assert 'class LegendNodeClass["Node class"]' in diagram
    assert 'class LegendEdgeClass["Edge (relationship) class"]' in diagram
    assert "style LegendNodeClass fill:#BBDEFB" in diagram
    assert "style LegendEdgeClass fill:#FFE0B2" in diagram


def test_build_mermaid_diagram_lists_undrawn_predicates():
    # Predicates without source/target metadata are listed as comments, not edges.
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    diagram = build_mermaid_diagram("demo", schema)
    assert "class Person" in diagram
    assert "%%   - name" in diagram
    assert "-->" not in diagram  # no endpoints, so nothing is drawn as an edge
    # No edge classes -> legend has the node entry only.
    assert 'class LegendNodeClass["Node class"]' in diagram
    assert "LegendEdgeClass" not in diagram


def test_inferred_edges_drawn_and_excluded_from_undrawn():
    # SIMPLE_CSV has class Person and predicate `name` with no endpoints — `name`
    # is normally listed as undrawn. An inferred edge draws it and drops the note.
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    diagram = build_mermaid_diagram(
        "demo", schema, inferred_edges=[("Person", "name", "Person")]
    )
    assert "Person --> Person : name" in diagram
    assert "%%   - name" not in diagram


async def test_infer_edge_labels_skips_when_curated_edges_exist():
    # EDGE_CSV declares source/target — inference must be a no-op (and make no
    # network call, since it returns before querying).
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    assert await infer_edge_labels("demo", schema) == []


async def test_infer_edge_labels_maps_uris_to_labels(monkeypatch):
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)

    async def fake_infer(shortname, class_uris, pred_uris, limit=400):
        return [
            (
                "http://schema.org/name",
                "http://schema.org/Person",
                "http://schema.org/Person",
            )
        ]

    monkeypatch.setattr(schema_mod, "infer_curated_edges", fake_infer)
    assert await infer_edge_labels("demo", schema) == [("Person", "name", "Person")]


def test_usage_notes_spoke_genelab_carries_both_rules():
    notes = usage_notes("spoke-genelab")
    assert notes is not None
    assert set(notes) == {"guidance", "query_snippet"}
    guidance = notes["guidance"]
    snippet = notes["query_snippet"]
    # Rule 1 (direction) pins SF arm 1 vs GC arm 2.
    assert 'schema:factor_space_1 "Space Flight"' in snippet
    assert 'schema:factor_space_2 "Ground Control"' in snippet
    # Rule 2 (comparability) strips the spelled-out condition labels (incl. the
    # in-vitro one), case-insensitively...
    for label in (
        "space flight",
        "ground control",
        "basal control",
        "vivarium control",
        "cell culture control",
    ):
        assert label in snippet
    # ...and the short group codes via the anchored regex (GC, FLT_C1, VIV_C2, …).
    assert "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$" in snippet
    assert "material_id_1" in snippet and "material_id_2" in snippet
    # Rule 2 is the WITHIN-assay test: a covariate present on one arm but absent
    # on the other (factors_1 vs factors_2) disqualifies the assay. The snippet
    # must cross-reference the two arms, not just emit two separate signatures.
    assert "schema:factors_1 ?x" in snippet
    assert "FILTER NOT EXISTS { ?assay schema:factors_2 ?x }" in snippet
    assert "schema:factors_2 ?y" in snippet
    assert "FILTER NOT EXISTS { ?assay schema:factors_1 ?y }" in snippet
    # It steers to the vetted-contrast tool rather than the hand-written self-join.
    assert "get_valid_contrasts" in snippet
    # Guidance states both rules, leads with the within-assay case, sign convention.
    assert "DIRECTION" in guidance and "COMPARABILITY" in guidance
    assert "GROUP CODES" in guidance
    assert "WITHIN-assay" in guidance or "within-assay" in guidance


def test_condition_code_regex_matches_codes_not_real_factors():
    import re

    from mcp_okn.contrasts import (
        SPOKE_GENELAB_CONDITION_CODE_REGEX,
        SPOKE_GENELAB_CONDITION_LABELS,
        SPOKE_GENELAB_CONTRAST_SNIPPET,
    )

    assert "Cell Culture Control" in SPOKE_GENELAB_CONDITION_LABELS
    # The snippet uses the same regex constant (no drift).
    assert SPOKE_GENELAB_CONDITION_CODE_REGEX in SPOKE_GENELAB_CONTRAST_SNIPPET
    pat = re.compile(SPOKE_GENELAB_CONDITION_CODE_REGEX)
    # Group codes (with/without cohort suffix) match.
    for code in ("GC", "FLT", "VIV_C2", "BSL_C1", "CC_C1", "GC_C2", "FLT_C1"):
        assert pat.match(code), code
    # Real factors that merely contain a control word must NOT match.
    for real in (
        "Hardware 1G Ground Control",
        "HLU_IR",
        "Euth_C_DI",
        "GCN2 KO",
        "FLTbox",
    ):
        assert not pat.match(real), real


def test_usage_notes_glygenkg_carries_the_record_to_protein_rule():
    """glygenkg's central class is a glycosylation RECORD with no edge to its
    protein; the notes must hand over the PR_ -> UniProt rewrite and warn about the
    two FALDO namespaces, both of which return 0 rows silently when missed."""
    notes = usage_notes("glygenkg")
    assert notes is not None
    guidance, snippet = notes["guidance"], notes["query_snippet"]
    assert "RECORD, NOT A PROTEIN" in guidance
    assert "gly:has_pro_entry" in guidance
    assert "http://www.biohackathon.org/resource/faldo#" in guidance
    assert "http://biohackathon.org/resource/faldo#" in guidance
    assert "get_join_strategy" in guidance
    # the snippet applies the rewrite it describes, in the right FALDO namespace
    assert "http://purl.obolibrary.org/obo/PR_" in snippet
    assert "<http://www.biohackathon.org/resource/faldo#>" in snippet
    assert "/kg/glygenkg>" in snippet


def test_usage_notes_absent_for_other_kgs():
    assert usage_notes("pankgraph") is None
    assert usage_notes("wildlifekn") is None


def test_usage_notes_spoke_okn_location_kind_and_https_trap():
    notes = usage_notes("spoke-okn")
    assert notes is not None
    guidance, snippet = notes["guidance"], notes["query_snippet"]
    # The kind predicate is the bare rdf: namespace, with its counted values.
    assert "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>" in guidance
    assert "Q28575" in guidance and "3,196" in guidance
    # The https schema.org trap and the IRI(CONCAT()) way round it.
    assert 'IRI(CONCAT("https://schema.org/", "State"))' in guidance
    # The snippet uses the kind predicate, never a bracketed https schema.org IRI
    # (this server would rewrite it to http and match nothing).
    assert "?county <http://www.w3.org/1999/02/22-rdf-syntax-ns#>" in snippet
    assert "<https://schema.org/" not in snippet


def test_instructions_include_spaceflight_contrast_section():
    from mcp_okn.app import INSTRUCTIONS

    assert "SPOKE-GENELAB SPACEFLIGHT CONTRASTS" in INSTRUCTIONS
    for label in (
        "Space Flight",
        "Ground Control",
        "Basal Control",
        "Vivarium Control",
    ):
        assert label in INSTRUCTIONS


def test_build_mermaid_diagram_probe_shape_classes_only():
    # Probe-shape schema (bare uri columns) -> class boxes from local names.
    schema = {
        "classes": {
            "columns": ["uri"],
            "data": [["http://schema.org/Person"]],
            "count": 1,
        },
        "predicates": {
            "columns": ["uri"],
            "data": [["http://schema.org/name"]],
            "count": 1,
        },
        "edge_properties": {},
        "node_properties": {"columns": ["uri"], "data": [], "count": 0},
    }
    diagram = build_mermaid_diagram("demo", schema)
    assert "class Person" in diagram
    assert "%%   - name" in diagram


# ── _probe_schema (the fallback for KGs with no curated metadata) ─────────────


def _stub_probe(monkeypatch, by_var, fail=None):
    """Stub run_sparql for _probe_schema, recording the queries it issues.

    `by_var` maps the projected variable ("class"/"predicate") to rows; the two
    class queries are told apart by whether the query asks for declared classes.
    `fail` is an exception raised for the query whose text contains that substring.
    """
    sent = []

    async def fake_run_sparql(query, *a, **kw):
        sent.append(query)
        if fail and fail[0] in query:
            raise fail[1]
        if "?predicate" in query:
            return {"rows": [{"predicate": p} for p in by_var.get("predicate", [])]}
        key = "declared" if "rdf-schema#Class" in query else "instance"
        return {"rows": [{"class": c} for c in by_var.get(key, [])]}

    monkeypatch.setattr(schema_mod, "run_sparql", fake_run_sparql)
    return sent


async def test_probe_schema_merges_both_class_queries(monkeypatch):
    """Instantiated and merely-DECLARED classes are probed separately — combining
    them in one UNION made QLever try to allocate 37.9 GB and fail on every graph.
    The two result sets are merged, de-duplicated, and sorted here instead.
    """
    sent = _stub_probe(
        monkeypatch,
        {
            "instance": ["http://ex.org/Gene", "http://ex.org/Drug"],
            "declared": ["http://ex.org/Drug", "http://ex.org/Unused"],
            "predicate": ["http://ex.org/treats", "http://ex.org/name"],
        },
    )
    out = await schema_mod._probe_schema("demo")

    assert len(sent) == 3  # instance types, declared classes, predicates
    assert not any("UNION" in q and "?s a ?class" in q for q in sent)
    assert out["classes"]["data"] == [
        ["http://ex.org/Drug"],  # in both results, listed once
        ["http://ex.org/Gene"],
        ["http://ex.org/Unused"],  # declared but never instantiated
    ]
    assert out["classes"]["count"] == 3
    assert out["predicates"]["data"] == [
        ["http://ex.org/name"],
        ["http://ex.org/treats"],
    ]


async def test_probe_schema_excludes_rdf_syntax_uris(monkeypatch):
    _stub_probe(
        monkeypatch,
        {
            "instance": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"],
            "declared": ["http://ex.org/Real"],
            "predicate": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#_1"],
        },
    )
    out = await schema_mod._probe_schema("demo")
    assert out["classes"]["data"] == [["http://ex.org/Real"]]
    assert out["predicates"]["data"] == []


async def test_probe_schema_propagates_a_failed_probe(monkeypatch):
    """The probes run concurrently with return_exceptions=True, so a failure must
    still reach the caller rather than being swallowed with the sibling's result."""
    boom = RuntimeError("endpoint said no")
    _stub_probe(
        monkeypatch, {"instance": ["http://ex.org/A"]}, fail=("?predicate", boom)
    )
    with pytest.raises(RuntimeError, match="endpoint said no"):
        await schema_mod._probe_schema("demo")


# ── VoID-built entity files (metadata/void_entities) ─────────────────────────

SG = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"
DE = SG + "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"
STMT = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"
XSD = "http://www.w3.org/2001/XMLSchema#"

#: Trimmed from metadata/void_entities/spoke-genelab_entities.csv (2026-10-15).
VOID_CSV = f"""\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
{SG}Assay,Assay,,Class,,,,13146,
{DE},DE,,Predicate,,http://purl.obolibrary.org/obo/OBI_0000070,https://w3id.org/biolink/vocab/Gene,50208066,direct;reified
{SG}taxonomy,taxonomy,,Predicate,,{SG}Study,,212,direct
{SG}name,name,,Predicate,,{SG}Study,{XSD}string,10,direct
{SG}name,name,,Predicate,,{SG}Mission,{XSD}string,40,direct
{SG}name,name,,Predicate,,{SG}Gene,{XSD}string,30,direct
{SG}name,name,,Predicate,,{SG}Assay,{XSD}string,20,direct
{SG}name,name,,Predicate,,{SG}Organism,{XSD}string,5,direct
{SG}log2fc,log2fc,,Predicate,{DE},{STMT},{XSD}double,50208066,
{SG}log2fc,log2fc,,Predicate,{DE},{STMT},{XSD}string,2,
"""


def test_parse_void_layout_rolls_pairs_up_per_uri():
    meta = parse_entity_metadata(VOID_CSV)
    name = meta[SG + "name"]
    assert name["triples"] == 105
    assert (name["source_class"], name["target_class"]) == (
        SG + "Mission",
        XSD + "string",
    )
    assert [p[2] for p in name["pairs"]] == [40, 30, 20, 10, 5]
    assert meta[SG + "Assay"]["triples"] == 13146


def test_void_edge_property_rows_become_edge_properties_with_iri_parent():
    meta = parse_entity_metadata(VOID_CSV)
    log2fc = meta[SG + "log2fc"]
    assert log2fc["type"] == "EdgeProperty"
    assert log2fc["edge_property_of"] == DE  # deduplicated across datatype rows
    schema = _build_schema_from_metadata("spoke-genelab", meta, compact=True)
    edge = schema["edge_properties"]["MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"]
    assert [p["label"] for p in edge["properties"]] == ["log2fc"]
    assert (
        "rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"
        in (edge["query_template"])
    )
    preds = schema["predicates"]
    flag = preds["columns"].index("has_edge_properties")
    (de_row,) = [r for r in preds["data"] if r[0] == DE]
    assert de_row[flag] is True


def test_void_rollup_adds_counts_and_extra_pairs():
    schema = _build_schema_from_metadata(
        "spoke-genelab", parse_entity_metadata(VOID_CSV), compact=True
    )
    assert schema["classes"]["columns"][-1] == "instances"
    preds = schema["predicates"]
    cols = preds["columns"]
    assert cols[-3:] == ["pattern", "triples", "other_pairs"]
    rows = {r[0]: dict(zip(cols, r, strict=True)) for r in preds["data"]}
    assert rows[SG + "name"]["triples"] == 105
    assert rows[SG + "name"]["other_pairs"] == (
        "Gene → string (30); Assay → string (20); Study → string (10); +1 more"
    )
    assert rows[SG + "taxonomy"]["other_pairs"] == ""
    assert rows[DE]["pattern"] == "direct;reified"
    assert rows[SG + "name"]["pattern"] == "direct"


def test_curated_layout_output_has_no_new_columns():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    assert schema["classes"]["columns"] == ["uri", "label", "description", "type"]
    assert schema["predicates"]["columns"][-1] == "has_edge_properties"


@pytest.mark.parametrize(
    ("fresh", "stale"),
    [
        (None, False),
        ({"matches": True}, False),
        ({"matches": None, "void_triples": 5, "served_triples": None}, False),
        # sawgraph 2026-10-15: 279 triples of 161M — use it.
        (
            {"matches": False, "void_triples": 161265076, "served_triples": 161264797},
            False,
        ),
        # biomarkerkg 2026-10-14: VoID describes another release.
        ({"matches": False, "void_triples": 1820793, "served_triples": 1215057}, True),
        ({"matches": False, "void_triples": 95913, "served_triples": 0}, True),
    ],
)
def test_void_is_stale(fresh, stale):
    assert void_is_stale(fresh) is stale


@pytest.fixture
def no_curated_client():
    """An httpx client that fails the test if any curated file is requested."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"curated file requested: {request.url}")

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_override_dir_is_exclusive_no_curated_fallback(
    tmp_path, no_curated_client
):
    (tmp_path / "built_entities.csv").write_text(VOID_CSV)
    got = {}
    for kg in ("built", "absent"):
        meta = await schema_mod.fetch_entity_metadata(
            kg, client=no_curated_client, refresh=True, override=str(tmp_path)
        )
        got[kg] = (schema_mod.metadata_source(kg), len(meta))
    assert got["built"] == (str(tmp_path), len(parse_entity_metadata(VOID_CSV)))
    # Absent from the override: empty, so get_schema probes the live graph.
    assert got["absent"] == (None, 0)


def test_edge_property_of_on_a_node_class_stays_a_predicate():
    """oard-kg: result-node properties, not reified-edge properties (no rdf:predicate)."""
    bl = "https://w3id.org/biolink/vocab/"
    meta = parse_entity_metadata(
        "URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass\n"
        f"{bl}has_study_results,hsr,,Predicate,,{bl}Study,{bl}LogOddsAnalysisResult\n"
        f"{bl}log_odds_ratio,lor,,Predicate,{bl}has_study_results,"
        f"{bl}LogOddsAnalysisResult,\n"
    )
    assert meta[bl + "log_odds_ratio"]["type"] == "Predicate"
    assert meta[bl + "log_odds_ratio"]["edge_property_of"] == ""
    schema = _build_schema_from_metadata("oard-kg", meta, compact=True)
    assert schema["edge_properties"] == {}


#: Shapes from the curated wildlifekn and scales files (2026-10-15).
MIXED_CSV = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
https://ex.org/OBSERVED_AT,OBSERVED_AT,Seen at.,Predicate,,https://ex.org/Bird,https://ex.org/Location
https://ex.org/OBSERVED_AT,OBSERVED_AT,Seen at.,Predicate,,https://ex.org/Frog,https://ex.org/Location
https://ex.org/date,date,Observation date.,EdgeProperty,OBSERVED_AT,,
https://ex.org/date,date,Date of an observation.,NodeProperty,,https://ex.org/Observation,
https://ex.org/Arrest,Arrest,An arrest.,Class,,,
https://ex.org/Arrest,Arrest,Has arrest.,Predicate,,https://ex.org/Person,https://ex.org/Arrest
"""


def test_uri_with_several_kinds_keeps_each():
    schema = _build_schema_from_metadata("demo", _parse(MIXED_CSV), compact=True)
    classes = [r[0] for r in schema["classes"]["data"]]
    preds = [r[0] for r in schema["predicates"]["data"]]
    assert "https://ex.org/Arrest" in classes and "https://ex.org/Arrest" in preds
    edge = schema["edge_properties"]["OBSERVED_AT"]
    assert [p["label"] for p in edge["properties"]] == ["date"]
    node = schema["node_properties"]["data"]
    assert [(r[0], r[-1]) for r in node] == [
        ("https://ex.org/date", "https://ex.org/Observation")
    ]


def test_curated_repeats_keep_last_row_primary_and_list_the_rest():
    schema = _build_schema_from_metadata("demo", _parse(MIXED_CSV), compact=True)
    cols = schema["predicates"]["columns"]
    assert "triples" not in cols and "pattern" not in cols  # curated file
    rows = {r[0]: dict(zip(cols, r, strict=True)) for r in schema["predicates"]["data"]}
    obs = rows["https://ex.org/OBSERVED_AT"]
    assert obs["source_class"] == "https://ex.org/Frog"
    assert obs["other_pairs"] == "Bird → Location"


AURA = "http://www.projecthalo.com/aura#"

#: bio101 shapes (2026-10-15): axiom-only relations, a declared-only one, structure.
OWL_CSV = f"""\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
{AURA}has-oxidized-form,has-oxidized-form,Axiom only.,Predicate,,{AURA}Chemical-Entity,{AURA}Chemical-Entity,0,axiom
{AURA}latitude,latitude,Unused.,Predicate,,,,0,declared
http://www.w3.org/2000/01/rdf-schema#subClassOf,subClassOf,,Predicate,,http://www.w3.org/2002/07/owl#Class,http://www.w3.org/2002/07/owl#Class,27760,direct
"""


def test_pattern_guidance_for_direct_and_reified_edges():
    schema = _build_schema_from_metadata(
        "spoke-genelab", parse_entity_metadata(VOID_CSV), compact=True
    )
    edge = schema["edge_properties"]["MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"]
    assert edge["pattern"] == "direct;reified"
    assert edge["usage"] == (
        f"Also a direct triple: use `?s <{DE}> ?o` unless you need edge properties."
    )
    guide = schema["pattern_guidance"]
    assert set(guide) == {"direct;reified"}  # plain direct gets no note
    assert guide["direct;reified"]["guidance"].startswith("Stored twice, one-to-one")
    assert guide["direct;reified"]["count"] == 1
    assert "predicates" not in guide["direct;reified"]  # listed in edge_properties


def test_pattern_guidance_axiom_template_and_compact_declared():
    compact = _build_schema_from_metadata("bio101", _parse(OWL_CSV), compact=True)
    preds = [r[0] for r in compact["predicates"]["data"]]
    assert AURA + "latitude" not in preds and compact["predicates"]["count"] == 2
    guide = compact["pattern_guidance"]
    assert guide["declared"]["predicates"] == [AURA + "latitude"]
    assert "Left out of the predicates table" in guide["declared"]["guidance"]
    tmpl = guide["axiom"]["query_template"]
    assert f"?r owl:onProperty <{AURA}has-oxidized-form>" in tmpl
    assert "rdfs:subClassOf|owl:equivalentClass" in tmpl
    assert "GROUP_CONCAT(DISTINCT STR(?subject)" in tmpl  # QLever drops bare IRIs
    assert "See usage_notes" in guide["axiom"]["guidance"]  # bio101 has notes

    full = _build_schema_from_metadata("bio101", _parse(OWL_CSV), compact=False)
    assert AURA + "latitude" in [r[0] for r in full["predicates"]["data"]]
    assert "predicates" not in full["pattern_guidance"]["declared"]


def test_curated_file_gets_no_pattern_guidance():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    assert "pattern_guidance" not in schema
    assert "pattern" not in schema["edge_properties"]["MEASURED_EXPR"]


def test_diagram_schema_draws_void_files_by_label_with_typed_members():
    """spoke-genelab VoID shapes: IRI endpoints, literal targets, reification wiring."""
    obi = "http://purl.obolibrary.org/obo/OBI_0000070"
    bl = "https://w3id.org/biolink/vocab/"
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    csv_text = f"""\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
{obi},Assay,,Class,,,,13146,
{bl}Gene,Gene,,Class,,,,139719,
{STMT},Statement,,Class,,,,50235713,
{DE},DE,,Predicate,,{obi},{bl}Gene,50208066,direct;reified
{SG}symbol,symbol,,Predicate,,{bl}Gene,{XSD}string,139719,direct
{SG}taxonomy,taxonomy,,Predicate,,{bl}Gene,,138948,direct
{rdf}subject,subject,,Predicate,,{STMT},{obi},50235713,direct
{SG}log2fc,log2fc,,Predicate,{DE},{STMT},{XSD}double,50208066,
"""
    meta = parse_entity_metadata(csv_text)
    diagram = build_mermaid_diagram(
        "spoke-genelab", schema_mod.diagram_schema("spoke-genelab", meta)
    )
    assert "Assay --> MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG" in diagram
    assert "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG --> Gene" in diagram
    assert "string symbol" in diagram and "iri taxonomy" in diagram
    assert "double log2fc" in diagram
    for absent in ("OBI_0000070", "Statement", "subject", "--> string"):
        assert absent not in diagram
    assert schema_mod._is_void_metadata(meta)
    assert not schema_mod._is_void_metadata(_parse(EDGE_CSV))  # curated: old path


def test_parallel_arrows_merge_into_one_labelled_arrow():
    lines = [
        "  Assay --> Anatomy : INVESTIGATED_ASiA",
        "  Assay --> EDGE",
        "  Assay --> Anatomy : material_id_1",
        "  Assay --> Anatomy : material_id_1",
        "  Gene --> Gene : IS_ORTHOLOG",
        "  Assay --> EDGE",
    ]
    assert schema_mod._merge_parallel(lines) == [
        "  Assay --> Anatomy : INVESTIGATED_ASiA, material_id_1",
        "  Assay --> EDGE",
        "  Gene --> Gene : IS_ORTHOLOG",
    ]


def test_diagram_leaves_out_owl_structure_and_value_classes_it_alone_reached():
    """bio101 shapes: OWL constructs, a has-value-only *-Constant, a domain relation."""
    owl = "http://www.w3.org/2002/07/owl#"
    aura = "http://www.projecthalo.com/aura#"
    schema = {
        "classes": {
            "columns": ["uri", "label"],
            "data": [
                [owl + "Restriction", "OWL_restriction"],
                [owl + "Class", "OWL_class"],
                [aura + "Size-Constant", "Size-Constant"],
                [aura + "Solution", "Solution"],
                [aura + "Substance", "Substance"],
            ],
        },
        "predicates": {
            "columns": ["uri", "label", "source_class", "target_class"],
            "data": [
                [owl + "hasValue", "has value", "OWL_restriction", "Size-Constant"],
                [owl + "onClass", "on class", "OWL_restriction", "OWL_class"],
                [aura + "has-solute", "has solute", "Solution", "Substance"],
            ],
        },
        "node_properties": {
            "columns": ["uri", "label", "description", "type", "class"],
            "data": [
                [aura + "d", "description", "(string)", "NodeProperty", "OWL_class"]
            ],
        },
    }
    diagram = build_mermaid_diagram("bio101", schema)
    assert "Solution --> Substance : has solute" in diagram
    for absent in ("OWL_restriction", "OWL_class", "Size_Constant", "has value"):
        assert absent not in diagram


def test_large_diagram_keeps_the_most_connected_classes():
    hub = [["u:Hub", "Hub"]]
    leaves = [[f"u:L{i}", f"L{i}"] for i in range(8)]
    lonely = [[f"u:X{i}", f"X{i}"] for i in range(4)]
    schema = {
        "classes": {"columns": ["uri", "label"], "data": hub + leaves + lonely},
        "predicates": {
            "columns": ["uri", "label", "source_class", "target_class"],
            "data": [[f"u:p{i}", f"p{i}", "Hub", f"L{i}"] for i in range(8)],
        },
    }
    info: dict = {}
    diagram = build_mermaid_diagram("demo", schema, max_classes=6, info=info)
    assert info["classes_total"] == 13 and info["classes_drawn"] == 6
    assert info["omitted_classes"] == ["L5", "L6", "L7", "X0", "X1", "X2", "X3"]
    assert "Hub --> L4 : p4" in diagram and "L5" not in diagram.split("%% Showing")[0]
    assert "%% Showing the 6 most-connected of 13 classes; omitted:" in diagram
    small: dict = {}
    build_mermaid_diagram("demo", schema, info=small)  # default limit: all drawn
    assert "omitted_classes" not in small


def test_endpoint_iris_resolve_to_class_labels_and_ids_never_start_with_a_digit():
    """prokn: class snomed 276239002 is labelled Therapy, but some rows name it by IRI."""
    therapy = "http://snomed.info/id/276239002"
    schema = {
        "classes": {
            "columns": ["uri", "label"],
            "data": [[therapy, "Therapy"], ["https://ex.org/Gene", "Gene"]],
        },
        "predicates": {
            "columns": ["uri", "label", "source_class", "target_class"],
            "data": [["https://ex.org/treats", "treats", therapy, "Gene"]],
        },
    }
    diagram = build_mermaid_diagram("prokn", schema)
    assert "Therapy --> Gene : treats" in diagram
    assert "276239002" not in diagram
    assert schema_mod._mermaid_id("276239002") == "n_276239002"
    assert schema_mod._mermaid_id("http://snomed.info/id/276239002") == "n_276239002"


def test_colons_in_arrow_labels_become_entities():
    """geo:hasGeometry broke Mermaid 12 parsing in five KGs; #58; draws as ':'."""
    assert schema_mod._clean_edge_label("geo:hasGeometry") == "geo#58;hasGeometry"
    schema = {
        "classes": {"columns": ["uri", "label"], "data": []},
        "predicates": {
            "columns": ["uri", "label", "source_class", "target_class"],
            "data": [["u:g", "geo:hasGeometry", "Feature", "Geometry"]],
        },
    }
    assert "Feature --> Geometry : geo#58;hasGeometry" in build_mermaid_diagram(
        "x", schema
    )


def test_dense_diagram_is_capped_by_arrows_too():
    """sawgraph: 60 classes still meant 1,741 arrows; the arrow limit trims classes."""
    names = [f"C{i}" for i in range(10)]
    schema = {
        "classes": {
            "columns": ["uri", "label"],
            "data": [[f"u:{n}", n] for n in names],
        },
        "predicates": {
            "columns": ["uri", "label", "source_class", "target_class"],
            "data": [
                [f"u:{a}{b}", f"{a}to{b}", a, b] for a in names for b in names if a != b
            ],
        },
    }
    info: dict = {}
    diagram = schema_mod.build_mermaid_diagram("demo", schema, info=info)  # 90 arrows
    assert "omitted_classes" not in info
    capped: dict = {}
    diagram = build_mermaid_diagram("demo", schema, info=capped, max_arrows=20)
    arrows = [
        line for line in diagram.splitlines() if " --> " in line and "%%" not in line
    ]
    assert len(arrows) <= 20 and capped["classes_drawn"] == 5  # 5 classes -> 20 arrows


def test_merged_arrow_shows_four_labels_then_a_count():
    lines = [f"  Feature --> Feature : p{i}" for i in range(7)]
    assert schema_mod._merge_parallel(lines) == [
        "  Feature --> Feature : p0, p1, p2, p3, +3 more"
    ]


def test_usage_notes_prokn_negated_go_annotations():
    notes = usage_notes("prokn")
    assert notes is not None
    guidance, snippet = notes["guidance"], notes["query_snippet"]
    npa = "<https://www.w3.org/2002/07/owl#NegativePropertyAssertion>"
    assert "1,370" in guidance and "overrides the pattern_guidance" in guidance
    assert npa in guidance and npa in snippet and "FILTER NOT EXISTS" in snippet
    assert len(schema_mod.PROKN_NEGATED_PREDICATES) == 9


#: prokn shapes: the same relationship name in two namespaces, one of them negated.
PROKN_CSV = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
https://biolink.github.io/biolink-model/catalyzes,catalyzes,,Predicate,,u:Protein,u:GO,5,direct;reified
https://w3id.org/biolink/vocab/catalyzes,catalyzes,,Predicate,,u:Protein,u:GO,90713,direct;reified
u:source,source,,Predicate,https://biolink.github.io/biolink-model/catalyzes,http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement,,5,
u:source,source,,Predicate,https://w3id.org/biolink/vocab/catalyzes,http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement,,90713,
"""


def test_same_name_relationships_keep_separate_templates_and_prokn_warning():
    schema = _build_schema_from_metadata(
        "prokn", parse_entity_metadata(PROKN_CSV), True
    )
    edges = schema["edge_properties"]
    assert {e["uri"] for e in edges.values()} == {
        "https://biolink.github.io/biolink-model/catalyzes",
        "https://w3id.org/biolink/vocab/catalyzes",
    }
    w3id = next(e for e in edges.values() if e["uri"].startswith("https://w3id.org"))
    other = next(e for e in edges.values() if e["uri"].startswith("https://biolink"))
    assert "GO NOT (negated)" in w3id["usage"]
    assert other["usage"].startswith("Also a direct triple")


def test_owl_predicates_are_not_drawn_as_relationships():
    """sawgraph: owl:sameAs between multi-typed samples tied every material class together."""
    owl = "http://www.w3.org/2002/07/owl#"
    schema = {
        "classes": {
            "columns": ["uri", "label"],
            "data": [
                ["u:A", "animal_material"],
                ["u:B", "organism_material"],
                ["u:S", "Sample"],
                ["u:O", "Observation"],
            ],
        },
        "predicates": {
            "columns": ["uri", "label", "source_class", "target_class"],
            "data": [
                [owl + "sameAs", "same as", "animal_material", "organism_material"],
                ["u:of", "has feature of interest", "Observation", "Sample"],
            ],
        },
    }
    diagram = build_mermaid_diagram("sawgraph", schema)
    assert "Observation --> Sample : has feature of interest" in diagram
    assert "same as" not in diagram
    assert "animal_material" not in diagram and "organism_material" not in diagram


def test_edge_classes_with_same_ends_and_properties_merge_into_one_box():
    """biohealth: dozens of Entity -> Entity relationships, each with only `source`."""
    names = ["TREATS", "CAUSES", "INHIBITS", "NEG_TREATS", "PREVENTS"]
    edge_properties = {
        n: {
            "source_class": "Entity",
            "target_class": "Entity",
            "properties": [{"label": "source", "description": "(string)"}],
        }
        for n in names
    }
    edge_properties["MEASURED"] = {
        "source_class": "Assay",
        "target_class": "Gene",
        "properties": [{"label": "log2fc", "description": "(float)"}],
    }
    schema = {
        "classes": {
            "columns": ["uri", "label"],
            "data": [["u:E", "Entity"], ["u:A", "Assay"], ["u:G", "Gene"]],
        },
        "edge_properties": edge_properties,
    }
    diagram = build_mermaid_diagram("biohealth", schema)
    box = "Entity_to_Entity_5_relationships"
    assert f"  Entity --> {box}" in diagram and f"  {box} --> Entity" in diagram
    arrows = [line for line in diagram.splitlines() if " --> " in line]
    assert arrows.count(f"  {box} --> Entity") == 1  # one arrow back, not five
    assert len([a for a in arrows if a.endswith("--> Entity")]) == 1
    for n in names:
        assert f"    {n}" in diagram  # each name listed in the box
    assert "Assay --> MEASURED" in diagram  # a lone relationship keeps its own box


def test_schema_files_default_to_the_shipped_void_entities():
    """No setting needed: the VoID-built files ship with the server."""
    base = Path(schema_mod.ENTITY_METADATA_BASE)
    assert base.name == "void_entities"
    assert (base / "prokn_entities.csv").is_file()
    assert "mcp-proto-okn" not in schema_mod.ENTITY_METADATA_BASE


async def test_default_schema_reads_the_shipped_file(monkeypatch):
    monkeypatch.setattr(schema_mod, "ENTITY_METADATA_OVERRIDE", "")
    meta = await schema_mod.fetch_entity_metadata("prokn", refresh=True)
    assert meta
    assert schema_mod.metadata_source("prokn") == schema_mod.ENTITY_METADATA_BASE


def test_biomarkerkg_notes_name_the_protein_predicates():
    notes = usage_notes("biomarkerkg")
    assert notes is not None
    for curie in ("OBCI_1000009", "OBCI_1000015", "OBCI_1000016", "OBCI_1000017"):
        assert curie in notes["guidance"]
        assert curie in notes["query_snippet"]
    # facts only: the note must not tell agents which legs to combine
    assert "UNION" not in notes["guidance"]


def test_rdkg_notes_say_how_to_find_a_disease_by_name():
    notes = usage_notes("rdkg")
    assert notes is not None
    assert '?d rdfs:label "Fabry disease"' in notes["guidance"]
    assert "lookup_term" in notes["guidance"]

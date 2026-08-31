import csv
from io import StringIO

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
    merge_void_partitions,
    usage_notes,
)
from mcp_okn.sparql import SparqlError


def _parse(csv_text: str) -> dict[str, dict[str, str]]:
    """Mirror fetch_entity_metadata's CSV parsing (without the network)."""
    metadata: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(StringIO(csv_text)):
        uri = (row.get("URI") or "").strip()
        if not uri:
            continue
        edge_property_of = (row.get("EdgePropertyOf") or "").strip()
        if uri in metadata and edge_property_of:
            existing = metadata[uri].get("edge_property_of", "")
            metadata[uri]["edge_property_of"] = (
                f"{existing};{edge_property_of}" if existing else edge_property_of
            )
        else:
            metadata[uri] = {
                "label": (row.get("Label") or "").strip(),
                "description": (row.get("Description") or "").strip(),
                "type": (row.get("Type") or "").strip(),
                "edge_property_of": edge_property_of,
                "source_class": (row.get("SourceClass") or "").strip(),
                "target_class": (row.get("TargetClass") or "").strip(),
            }
    return metadata


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
https://ex.org/schema/symbol,symbol,Gene symbol (string).,NodeProperty,,Gene,
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


def test_merge_void_partitions_adds_counts_and_observed_rows():
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    merge_void_partitions(
        schema,
        {
            "classes": [
                {"uri": "http://schema.org/Person", "entity_count": 12},
                {"uri": "http://schema.org/Organization", "entity_count": 3},
                {
                    "uri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement",
                    "entity_count": 99,
                },
            ],
            "predicates": [
                {"uri": "http://schema.org/name", "triple_count": 20},
                {"uri": "http://schema.org/knows", "triple_count": 7},
                {"uri": "http://rdfs.org/ns/void#triples", "triple_count": 1},
            ],
        },
    )

    classes = schema["classes"]
    assert classes["columns"][-1] == "entity_count"
    person = next(row for row in classes["data"] if row[0].endswith("Person"))
    organization = next(
        row for row in classes["data"] if row[0].endswith("Organization")
    )
    assert person[-1] == 12
    assert organization[classes["columns"].index("label")] == ""
    assert organization[-1] == 3
    assert not any("Statement" in row[0] for row in classes["data"])

    predicates = schema["predicates"]
    assert predicates["columns"][-1] == "triple_count"
    name = next(row for row in predicates["data"] if row[0].endswith("name"))
    knows = next(row for row in predicates["data"] if row[0].endswith("knows"))
    assert name[-1] == 20
    assert knows[-1] == 7
    assert not any("void#triples" in row[0] for row in predicates["data"])


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
    assert "schema:MEASURED_EXPR" in tmpl
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
    props = [{"label": "score"}]
    tmpl = _generate_query_template("demo", "RELATES", "Foo", "Bar", props)
    assert "SELECT ?foo ?bar ?score" in tmpl
    assert "schema:RELATES" in tmpl
    assert tmpl.rstrip().endswith("}")


def test_should_exclude_rdf_syntax_uris():
    assert _should_exclude_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#_1")
    assert not _should_exclude_uri("http://schema.org/Person")


def test_member_type_extracts_trailing_parenthetical():
    assert _member_type("Log2 fold change (float)") == "float"
    assert _member_type("Adjusted p-value (FDR-corrected). (float)") == "float"
    # No usable type -> empty (don't treat a sentence in parens as a type).
    assert _member_type("Some prose (with several words)") == ""
    assert _member_type("plain description") == ""


def test_build_mermaid_diagram_uses_observed_endpoints_for_edge_classes():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    # Reverse the curated Sample -> Gene endpoint to prove the diagram uses this
    # observed VoID path rather than the curated SourceClass/TargetClass columns.
    diagram = build_mermaid_diagram(
        "demo",
        schema,
        inferred_edges=[("Gene", "MEASURED_EXPR", "Sample")],
    )
    assert diagram.startswith("classDiagram")
    assert "direction TB" in diagram
    # Node classes appear as boxes.
    assert "class Gene" in diagram
    assert "class Sample" in diagram
    # The edge-property predicate becomes an intermediary class with typed fields,
    # wired only through the observed path.
    assert "class MEASURED_EXPR {" in diagram
    assert "float log2fc" in diagram
    assert "Gene --> MEASURED_EXPR" in diagram
    assert "MEASURED_EXPR --> Sample" in diagram
    assert "Sample --> MEASURED_EXPR" not in diagram
    assert "MEASURED_EXPR --> Gene" not in diagram
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


async def test_infer_edge_labels_uses_void_even_when_curated_edges_exist(monkeypatch):
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)

    async def fake_observed(*args, **kwargs):
        return [
            {
                "predicate": "https://ex.org/schema/MEASURED_EXPR",
                "source_class": "https://ex.org/schema/Sample",
                "target_class": "https://ex.org/schema/Gene",
                "triple_count": 3,
            }
        ]

    monkeypatch.setattr(schema_mod.void_metadata, "fetch_observed_edges", fake_observed)
    assert await infer_edge_labels("demo", schema) == [
        ("Sample", "MEASURED_EXPR", "Gene")
    ]


async def test_infer_edge_labels_maps_uris_to_labels(monkeypatch):
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)

    async def fake_observed(
        shortname, class_uris=None, predicate_uris=None, limit=400, client=None
    ):
        return [
            {
                "predicate": "http://schema.org/name",
                "source_class": "http://schema.org/Person",
                "target_class": "http://schema.org/Person",
                "triple_count": 3,
            }
        ]

    monkeypatch.setattr(schema_mod.void_metadata, "fetch_observed_edges", fake_observed)
    assert await infer_edge_labels("demo", schema) == [("Person", "name", "Person")]


async def test_infer_edge_labels_does_not_fall_back_to_declared_domain_range(
    monkeypatch,
):
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)

    async def unavailable(*args, **kwargs):
        raise SparqlError("no VoID")

    async def should_not_infer(*args, **kwargs):
        raise AssertionError("rdfs:domain/range fallback must not run")

    monkeypatch.setattr(schema_mod.void_metadata, "fetch_observed_edges", unavailable)
    monkeypatch.setattr(schema_mod, "infer_curated_edges", should_not_infer)
    with pytest.raises(SparqlError, match="no VoID"):
        await infer_edge_labels("demo", schema)


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


def test_usage_notes_absent_for_other_kgs():
    assert usage_notes("prokn") is None
    assert usage_notes("spoke-okn") is None


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


# ── get_schema composition ----------------------------------------------------


async def test_get_schema_enriches_only_void_observed_uris(monkeypatch):
    async def fake_metadata(shortname, **kwargs):
        return _parse(
            """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
http://schema.org/Person,Human,A human being.,Class,,,
http://schema.org/Organization,Organization,Not observed.,Class,,,
http://schema.org/name,display name,The name of the thing.,Predicate,,Wrong,Wrong
http://schema.org/knows,knows,Not observed.,Predicate,,Person,Person
"""
        )

    async def fake_partitions(shortname):
        return {
            "classes": [{"uri": "http://schema.org/Person", "entity_count": 5}],
            "predicates": [{"uri": "http://schema.org/name", "triple_count": 8}],
        }

    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", fake_metadata)
    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    out = await schema_mod.get_schema("demo")
    assert out["schema_sources"] == ["okn-void", "curated_metadata"]
    assert set(out["schema"]) == {
        "classes",
        "predicates",
        "edge_properties",
        "unmapped_edge_properties",
        "node_properties",
    }
    assert out["schema"]["classes"] == {
        "columns": [
            "uri",
            "label",
            "description",
            "type",
            "metadata_source",
            "entity_count",
        ],
        "data": [
            [
                "http://schema.org/Person",
                "Human",
                "A human being.",
                "Class",
                "curated_metadata",
                5,
            ]
        ],
        "count": 1,
    }
    predicates = out["schema"]["predicates"]
    assert predicates["data"][0][0:5] == [
        "http://schema.org/name",
        "display name",
        "The name of the thing.",
        "Predicate",
        "curated_metadata",
    ]
    assert "source_class" not in predicates["columns"]
    assert "target_class" not in predicates["columns"]
    assert not any("Organization" in str(row) for row in out["schema"]["classes"]["data"])
    assert not any("knows" in str(row) for row in predicates["data"])
    assert out["metadata_enrichment"] == {
        "source": "curated_metadata",
        "status": "applied",
        "topology_source": "okn-void",
        "curated_predicate_endpoints_used": False,
        "matched_classes": 1,
        "matched_predicates": 1,
        "descriptions": 2,
        "node_properties": 0,
        "node_properties_with_observed_owner": 0,
        "edge_property_relationships": 0,
        "edge_properties": 0,
        "mapped_edge_properties": 0,
        "unmapped_edge_properties": 0,
    }


async def test_get_schema_never_uses_live_probe(monkeypatch):
    async def no_metadata(shortname, **kwargs):
        return {}

    async def fake_partitions(shortname):
        return {
            "classes": [{"uri": "http://ex.org/Gene", "entity_count": 2}],
            "predicates": [{"uri": "http://ex.org/related_to", "triple_count": 4}],
        }

    async def should_not_probe(shortname):
        raise AssertionError("live probe should not run when VoID is available")

    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", no_metadata)
    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    monkeypatch.setattr(schema_mod, "_probe_schema", should_not_probe)
    out = await schema_mod.get_schema("demo")
    assert out["schema_sources"] == ["okn-void"]
    assert out["metadata_enrichment"]["status"] == "not_available"
    assert out["schema"]["classes"]["data"][0][0] == "http://ex.org/Gene"
    assert out["schema"]["classes"]["data"][0][-1] == 2
    assert out["schema"]["predicates"]["data"][0][0] == "http://ex.org/related_to"
    assert out["schema"]["predicates"]["data"][0][-1] == 4


async def test_get_schema_uses_void_for_graph_previously_too_large(monkeypatch):
    async def no_metadata(shortname, **kwargs):
        return {}

    async def fake_partitions(shortname):
        return {
            "classes": [{"uri": "http://ex.org/Term", "entity_count": 100}],
            "predicates": [
                {
                    "uri": "http://www.w3.org/2000/01/rdf-schema#label",
                    "triple_count": 100,
                }
            ],
        }

    async def should_not_probe(shortname):
        raise AssertionError("live probe should not run when VoID is available")

    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", no_metadata)
    monkeypatch.setattr(schema_mod, "_probe_schema", should_not_probe)
    out = await schema_mod.get_schema("ubergraph")
    assert "error" not in out
    assert out["schema_sources"] == ["okn-void"]
    assert out["schema"]["classes"]["count"] == 1


async def test_get_schema_noncompact_includes_void_details(monkeypatch):
    async def no_metadata(shortname, **kwargs):
        return {}

    async def fake_partitions(shortname):
        return {
            "classes": [
                {"uri": "http://ex.org/Gene", "entity_count": 2},
                {"uri": "http://ex.org/Disease", "entity_count": 3},
            ],
            "predicates": [{"uri": "http://ex.org/associated_with", "triple_count": 4}],
        }

    async def fake_edges(*args, **kwargs):
        return [
            {
                "source_class": "http://ex.org/Gene",
                "predicate": "http://ex.org/associated_with",
                "target_class": "http://ex.org/Disease",
                "triple_count": 4,
            }
        ]

    async def fake_shapes(*args, **kwargs):
        return [
            {
                "predicate": "http://ex.org/name",
                "kind": "language",
                "value": "en",
                "triple_count": 2,
            }
        ]

    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", no_metadata)
    monkeypatch.setattr(schema_mod.void_metadata, "fetch_observed_edges", fake_edges)
    monkeypatch.setattr(schema_mod.void_metadata, "fetch_value_shapes", fake_shapes)
    out = await schema_mod.get_schema("demo", compact=False)
    assert set(out["schema"]) == {
        "classes",
        "predicates",
        "observed_edges",
        "value_shapes",
        "edge_properties",
        "unmapped_edge_properties",
        "node_properties",
    }
    assert out["schema"]["observed_edges"]["count"] == 1
    assert out["schema"]["observed_edges"]["data"][0][-1] == 4
    assert out["schema"]["value_shapes"]["count"] == 1
    assert out["schema"]["value_shapes"]["data"][0][1:3] == ["language", "en"]
    assert out["metadata_enrichment"]["status"] == "not_available"


async def test_get_schema_preserves_property_metadata_for_observed_uris(monkeypatch):
    async def fake_metadata(shortname, **kwargs):
        return _parse(EDGE_CSV)

    async def fake_partitions(shortname):
        return {
            "classes": [
                {"uri": "https://ex.org/schema/Gene", "entity_count": 2},
                {"uri": "https://ex.org/schema/Sample", "entity_count": 3},
            ],
            "predicates": [
                {
                    "uri": "https://ex.org/schema/MEASURED_EXPR",
                    "triple_count": 4,
                },
                {"uri": "https://ex.org/schema/log2fc", "triple_count": 4},
                {"uri": "https://ex.org/schema/pval", "triple_count": 4},
                {"uri": "https://ex.org/schema/symbol", "triple_count": 2},
            ],
        }

    async def fake_edges(*args, **kwargs):
        return [
            {
                "source_class": "https://ex.org/schema/Sample",
                "predicate": "https://ex.org/schema/MEASURED_EXPR",
                "target_class": "https://ex.org/schema/Gene",
                "triple_count": 4,
            }
        ]

    async def fake_shapes(*args, **kwargs):
        return []

    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", fake_metadata)
    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    monkeypatch.setattr(schema_mod.void_metadata, "fetch_observed_edges", fake_edges)
    monkeypatch.setattr(schema_mod.void_metadata, "fetch_value_shapes", fake_shapes)

    out = await schema_mod.get_schema("demo", compact=False)
    schema = out["schema"]
    assert out["schema_sources"] == ["okn-void", "curated_metadata"]
    assert schema["node_properties"]["data"] == [
        [
            "https://ex.org/schema/symbol",
            "symbol",
            "Gene symbol (string).",
            "NodeProperty",
            "https://ex.org/schema/Gene",
            "Gene",
            "owner_uri_observed",
            "curated_metadata",
        ]
    ]
    edge = schema["edge_properties"]["MEASURED_EXPR"]
    assert edge["metadata_source"] == "curated_metadata"
    assert edge["endpoint_source"] == "okn-void"
    assert "statement_level_mapping_not_independently_verified" in edge[
        "mapping_validation"
    ]
    assert "source_class" not in edge and "target_class" not in edge
    assert {prop["label"] for prop in edge["properties"]} == {"log2fc", "pval"}
    assert all(
        prop["metadata_source"] == "curated_metadata"
        for prop in edge["properties"]
    )
    assert "rdf:predicate <https://ex.org/schema/MEASURED_EXPR>" in edge[
        "query_template"
    ]
    assert "<https://ex.org/schema/log2fc> ?log2fc" in edge["query_template"]
    assert schema["edge_property_summary"]["mapping_source"] == "curated_metadata"
    assert schema["edge_property_summary"]["topology_source"] == "okn-void"
    assert "statement_level_mapping_not_independently_verified" in schema[
        "edge_property_summary"
    ]["mapping_validation"]
    assert schema["unmapped_edge_properties"]["count"] == 0
    predicate_columns = schema["predicates"]["columns"]
    measured = next(
        row
        for row in schema["predicates"]["data"]
        if row[predicate_columns.index("uri")].endswith("MEASURED_EXPR")
    )
    assert measured[predicate_columns.index("has_edge_properties")] is True


async def test_get_schema_retains_unowned_and_unmapped_property_metadata(monkeypatch):
    async def fake_metadata(shortname, **kwargs):
        return _parse(
            """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
http://ex.org/Assay,Assay,An assay.,Class,,,
http://ex.org/array_design,array_design,Array design (string),NodeProperty,,,
http://ex.org/log2fc,log2fc,Fold change (float),EdgeProperty,,,
"""
        )

    async def fake_partitions(shortname):
        return {
            "classes": [{"uri": "http://ex.org/Assay", "entity_count": 2}],
            "predicates": [
                {"uri": "http://ex.org/array_design", "triple_count": 2},
                {"uri": "http://ex.org/log2fc", "triple_count": 2},
            ],
        }

    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", fake_metadata)
    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    out = await schema_mod.get_schema("demo")
    schema = out["schema"]
    assert schema["node_properties"]["data"][0][-2:] == [
        "not_provided",
        "curated_metadata",
    ]
    assert schema["unmapped_edge_properties"]["data"][0][0:6] == [
        "http://ex.org/log2fc",
        "log2fc",
        "Fold change (float)",
        "EdgeProperty",
        "",
        "not_provided",
    ]
    assert out["metadata_enrichment"]["node_properties"] == 1
    assert out["metadata_enrichment"]["node_properties_with_observed_owner"] == 0
    assert out["metadata_enrichment"]["edge_properties"] == 1
    assert out["metadata_enrichment"]["mapped_edge_properties"] == 0
    assert out["metadata_enrichment"]["unmapped_edge_properties"] == 1
    assert "no reification query template was generated" in out["warnings"][0]


async def test_get_schema_noncompact_propagates_void_detail_failures(monkeypatch):
    async def fake_partitions(shortname):
        return {
            "classes": [{"uri": "http://ex.org/Gene", "entity_count": 2}],
            "predicates": [{"uri": "http://ex.org/associated_with", "triple_count": 4}],
        }

    async def unavailable(*args, **kwargs):
        raise SparqlError("detail query unavailable")

    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    monkeypatch.setattr(schema_mod.void_metadata, "fetch_observed_edges", unavailable)
    monkeypatch.setattr(schema_mod.void_metadata, "fetch_value_shapes", unavailable)
    with pytest.raises(SparqlError, match="detail query unavailable"):
        await schema_mod.get_schema("demo", compact=False)


async def test_get_schema_reports_unavailable_semantic_enrichment(monkeypatch):
    async def fake_partitions(shortname):
        return {
            "classes": [{"uri": "http://ex.org/Gene", "entity_count": 2}],
            "predicates": [{"uri": "http://ex.org/name", "triple_count": 4}],
        }

    async def unavailable(shortname, **kwargs):
        raise httpx.ConnectError(
            "metadata host unavailable",
            request=httpx.Request("GET", "https://example.org/metadata.csv"),
        )

    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", fake_partitions
    )
    monkeypatch.setattr(schema_mod, "fetch_entity_metadata", unavailable)
    out = await schema_mod.get_schema("demo")
    assert out["schema_sources"] == ["okn-void"]
    assert out["metadata_enrichment"]["status"] == "unavailable"
    assert out["metadata_enrichment"]["curated_predicate_endpoints_used"] is False
    assert "metadata host unavailable" in out["metadata_enrichment"]["error"]
    assert "without labels/descriptions/property guidance" in out["warnings"][0]
    assert out["schema"]["classes"]["data"][0][1:5] == ["", "", "", ""]


async def test_get_schema_does_not_fall_back_when_void_is_unavailable(monkeypatch):
    async def unavailable(shortname):
        raise SparqlError("VoID endpoint unavailable")

    async def should_not_fetch_metadata(shortname):
        raise AssertionError("curated metadata must not be fetched")

    async def should_not_probe(shortname):
        raise AssertionError("live probe must not run")

    monkeypatch.setattr(
        schema_mod, "fetch_entity_metadata", should_not_fetch_metadata
    )
    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", unavailable
    )
    monkeypatch.setattr(schema_mod, "_probe_schema", should_not_probe)
    with pytest.raises(SparqlError, match="VoID endpoint unavailable"):
        await schema_mod.get_schema("demo")


async def test_get_schema_reports_missing_void_partitions_without_fallback(monkeypatch):
    async def no_partitions(shortname):
        return {"classes": [], "predicates": []}

    async def should_not_probe(shortname):
        raise AssertionError("live probe must not run")

    monkeypatch.setattr(
        schema_mod.void_metadata, "fetch_schema_partitions", no_partitions
    )
    monkeypatch.setattr(schema_mod, "_probe_schema", should_not_probe)
    out = await schema_mod.get_schema("demo")
    assert out == {
        "shortname": "demo",
        "error": "No observed VoID schema partitions are available for `demo`.",
        "schema_sources": ["okn-void"],
    }


async def test_visualize_schema_draws_only_observed_void_edges(monkeypatch):
    async def fake_get_schema(shortname, compact=True):
        assert compact is False
        return {
            "shortname": shortname,
            "schema_sources": ["okn-void", "curated_metadata"],
            "metadata_enrichment": {
                "status": "applied",
                "topology_source": "okn-void",
                "curated_predicate_endpoints_used": False,
            },
            "schema": {
                "classes": {
                    "columns": ["uri", "entity_count"],
                    "data": [
                        ["http://example.org/Assay", 10],
                        ["http://example.org/AnatomicalEntity", 4],
                    ],
                    "count": 2,
                },
                "predicates": {
                    "columns": ["uri", "triple_count"],
                    "data": [["http://example.org/has_attribute", 11]],
                    "count": 1,
                },
                "observed_edges": {
                    "columns": [
                        "source_class",
                        "predicate",
                        "target_class",
                        "triple_count",
                    ],
                    "data": [
                        [
                            "http://example.org/Assay",
                            "http://example.org/has_attribute",
                            "http://example.org/AnatomicalEntity",
                            11,
                        ]
                    ],
                    "count": 1,
                },
                "value_shapes": {
                    "columns": ["predicate", "kind", "value", "triple_count"],
                    "data": [],
                    "count": 0,
                },
            },
        }

    monkeypatch.setattr(schema_mod, "get_schema", fake_get_schema)
    out = await schema_mod.visualize_schema("gene-expression-atlas-okn")
    assert "Assay --> AnatomicalEntity : has_attribute" in out["mermaid"]
    assert out["schema_sources"] == ["okn-void", "curated_metadata"]
    assert out["metadata_enrichment"]["curated_predicate_endpoints_used"] is False

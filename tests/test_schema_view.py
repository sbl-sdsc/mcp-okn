import copy
import json

import mcp_okn.server as srv
from mcp_okn.schema import _generate_query_template
from mcp_okn.schema_view import (
    compact_iris,
    compact_reply,
    fit_to_budget,
    match_schema,
    reply_size,
)

NS = "https://purl.org/okn/frink/kg/demo/schema/"
BIOLINK = "https://w3id.org/biolink/vocab/"


def _reply(n_classes=5, desc="x" * 40):
    """A get_schema reply shaped like a VoID-built one: IRIs, counts, edges."""
    classes = [
        [f"{BIOLINK}C{i}", f"C{i}", desc, "Class", 1000 - i] for i in range(n_classes)
    ]
    preds = [
        [
            f"{NS}p{i}",
            f"p{i}",
            desc,
            "Predicate",
            f"{BIOLINK}C0",
            f"{BIOLINK}C1",
            i == 0,
            "direct",
            10 * i,
            "",
        ]
        for i in range(20)
    ]
    edge = {
        "uri": f"{NS}p0",
        "label": "p0",
        "description": desc,
        "source_class": f"{BIOLINK}C0",
        "target_class": f"{BIOLINK}C1",
        "properties": [
            {
                "uri": f"{NS}state_abbr",
                "label": "State Abbreviation",
                "description": "two-letter state",
                "type": "EdgeProperty",
            }
        ],
        "query_template": "SELECT * WHERE { ?s ?p ?o }" * 5,
    }
    return {
        "shortname": "demo",
        "schema": {
            "classes": {
                "columns": ["uri", "label", "description", "type", "instances"],
                "data": classes,
                "count": len(classes),
            },
            "predicates": {
                "columns": [
                    "uri",
                    "label",
                    "description",
                    "type",
                    "source_class",
                    "target_class",
                    "has_edge_properties",
                    "pattern",
                    "triples",
                    "other_pairs",
                ],
                "data": preds,
                "count": len(preds),
            },
            "edge_properties": {"p0": edge},
            "node_properties": {
                "columns": ["uri", "label", "description", "type", "class"],
                "data": [],
                "count": 0,
            },
        },
        "next_step": "probe_namespaces before joining",
    }


def test_a_reply_that_fits_is_returned_unchanged():
    reply = _reply()
    assert fit_to_budget(reply, "demo", budget=100_000) is reply


def test_over_budget_trims_detail_before_rows_and_says_what_it_did():
    reply = _reply()
    budget = reply_size(reply) - 200  # just over: lossless steps suffice
    out = fit_to_budget(reply, "demo", budget=budget)
    assert reply_size(out) <= budget
    view = out["schema_view"]
    assert view["budget_chars"] == budget
    assert "edge_properties query_template" in view["trimmed"]
    assert "omitted" not in view  # no row was cut
    assert out["schema"]["predicates"]["count"] == 20
    assert "match=" in view["how_to_get_more"]
    assert out["next_step"] == reply["next_step"]
    # The input is not modified.
    assert "query_template" in reply["schema"]["edge_properties"]["p0"]


def test_short_iris_expand_back_exactly():
    reply = _reply()
    out = fit_to_budget(reply, "demo", budget=reply_size(reply) // 2)
    prefixes = out["schema_view"]["prefixes"]
    assert prefixes["kg"] == NS  # the KG's own namespace is kg:, not schema:
    assert prefixes["biolink"] == BIOLINK
    assert f"PREFIX kg: <{NS}>" in out["schema_view"]["sparql_prefixes"]
    cols = out["schema"]["predicates"]["columns"]
    row = out["schema"]["predicates"]["data"][0]
    name, local = row[cols.index("uri")].split(":", 1)
    original = {r[0] for r in reply["schema"]["predicates"]["data"]}
    assert prefixes[name] + local in original


def test_rows_go_last_largest_first_and_are_counted():
    reply = _reply(n_classes=400)
    budget = 12_000
    out = fit_to_budget(reply, "demo", budget=budget)
    assert reply_size(out) <= budget
    classes = out["schema"]["classes"]
    cut = out["schema_view"]["omitted"]["classes"]
    assert cut > 0 and classes["count"] + cut == 400 == classes["total"]
    counts = [row[classes["columns"].index("instances")] for row in classes["data"]]
    assert counts == sorted(counts, reverse=True)
    # Every predicate survives: classes were cut instead.
    assert out["schema"]["predicates"]["count"] == 20


def test_schema_org_prefix_keeps_its_scheme():
    schema = {
        "classes": {
            "columns": ["uri"],
            "data": [[f"https://schema.org/T{i}"] for i in range(3)]
            + [[f"http://schema.org/T{i}"] for i in range(3)]
            + [[f"https://www.w3.org/2002/07/owl#K{i}"] for i in range(3)]
            + [[f"http://example.org/{i}/schema/T"] for i in range(1)],
        }
    }
    prefixes = compact_iris(schema)
    assert prefixes["schema"] == "http://schema.org/"
    assert prefixes["schema_https"] == "https://schema.org/"
    assert prefixes["owl_https"] == "https://www.w3.org/2002/07/owl#"
    # A namespace used fewer than three times keeps its full IRIs.
    assert ["http://example.org/0/schema/T"] in schema["classes"]["data"]


def test_match_finds_a_relationship_by_its_edge_property():
    out = match_schema(_reply(), "state abbreviation|nothing-like-this")
    preds = [row[0] for row in out["schema"]["predicates"]["data"]]
    assert preds == [f"{NS}p0"]
    assert list(out["schema"]["edge_properties"]) == ["p0"]
    assert "query_template" in out["schema"]["edge_properties"]["p0"]
    # The classes it connects come with it.
    classes = {row[0] for row in out["schema"]["classes"]["data"]}
    assert classes == {f"{BIOLINK}C0", f"{BIOLINK}C1"}
    view = out["schema_view"]
    assert view["found"]["predicates"] == 1 and view["of"]["predicates"] == 20


def test_match_on_a_class_brings_its_predicates():
    out = match_schema(_reply(), "c0")
    assert out["schema"]["predicates"]["count"] == 20  # all run C0 -> C1


def test_match_with_no_hit_says_so():
    out = match_schema(_reply(), "zzz")
    assert not any(out["schema_view"]["found"].values())
    assert "Nothing" in out["schema_view"]["note"]


def test_template_variables_use_the_local_name_of_an_iri_class():
    tmpl = _generate_query_template(
        "demo", "RELATES", f"{BIOLINK}Disease", "https://schema.org/Place", []
    )
    assert "?disease ?place" in tmpl
    assert "httpsw3id" not in tmpl


async def test_tool_applies_match_and_budget(monkeypatch):
    async def fake_schema(shortname, compact=True):
        return _reply(n_classes=2000)

    monkeypatch.setattr(srv.schema, "get_schema", fake_schema)
    monkeypatch.setattr(srv.schema, "usage_notes", lambda kg: None)
    full = await srv.get_schema("demo")
    assert len(json.dumps(full, separators=(",", ":"))) <= 40_000
    assert full["schema_view"]["omitted"]["classes"] > 0
    found = await srv.get_schema("demo", match="C1999")
    rows = found["schema"]["classes"]["data"]
    assert [r[0] for r in rows] == [f"{BIOLINK}C1999"]


def test_match_short_term_is_whole_token():
    reply = {
        "schema": {
            "classes": {
                "columns": ["uri", "label", "instances"],
                "data": [
                    ["http://purl.obolibrary.org/obo/GO_0008150", "process", 5],
                    ["http://example.org/Category", "category", 9],
                    ["http://example.org/GOTerm", "GO term", 3],
                ],
                "count": 3,
            },
            "predicates": {"columns": ["uri", "label"], "data": [], "count": 0},
        }
    }
    out = match_schema(reply, "GO")
    labels = [row[1] for row in out["schema"]["classes"]["data"]]
    assert labels == ["process", "GO term"]
    # longer terms keep substring matching
    out = match_schema(reply, "categ")
    assert [row[1] for row in out["schema"]["classes"]["data"]] == ["category"]


def test_compact_reply_is_lossless():
    """Every IRI comes back exactly from `sparql_prefixes`; only constant or
    repeated cells go; the input is untouched."""
    reply = _reply()
    out = compact_reply(reply)
    assert reply_size(out) < reply_size(reply)
    prefixes = dict(
        line[len("PREFIX ") :].split(": ", 1)
        for line in out["sparql_prefixes"].split("\n")
    )
    prefixes = {k: v.strip("<>") for k, v in prefixes.items()}

    def expand(v):
        name, _, local = v.partition(":")
        return prefixes[name] + local if name in prefixes else v

    for table in ("classes", "predicates"):
        before = reply["schema"][table]
        after = out["schema"][table]
        assert "type" not in after["columns"]  # constant: Class / Predicate
        assert len(after["data"]) == len(before["data"])
        i = after["columns"].index("uri")
        assert [expand(r[i]) for r in after["data"]] == [r[0] for r in before["data"]]
    assert "has_edge_properties" not in out["schema"]["predicates"]["columns"]
    entry = out["schema"]["edge_properties"]["p0"]
    [uri] = entry["properties"]  # each property defined once, listed by IRI
    defn = out["schema"]["edge_property_defs"][uri]
    assert expand(uri) == f"{NS}state_abbr"
    assert "type" not in defn
    assert defn["label"] == "State Abbreviation"  # a real label is kept
    # The relationship's own facts stay in its predicates row, not repeated here.
    for key in ("label", "description", "source_class", "target_class"):
        assert key not in entry
    assert expand(entry["uri"]) == f"{NS}p0"
    assert "type" in reply["schema"]["classes"]["columns"]  # input not modified


def test_compact_reply_drops_label_that_repeats_local_name():
    reply = _reply()
    reply["schema"]["edge_properties"]["p0"]["properties"][0]["label"] = "state_abbr"
    out = compact_reply(reply)
    [uri] = out["schema"]["edge_properties"]["p0"]["properties"]
    assert "label" not in out["schema"]["edge_property_defs"][uri]


def test_compact_reply_keeps_edge_facts_that_differ_from_the_row():
    reply = _reply()
    reply["schema"]["edge_properties"]["p0"]["description"] = "something else"
    out = compact_reply(reply)
    assert out["schema"]["edge_properties"]["p0"]["description"] == "something else"


def test_compact_reply_keeps_conflicting_property_definitions_inline():
    reply = _reply()
    edges = reply["schema"]["edge_properties"]
    other = copy.deepcopy(edges["p0"])
    other["uri"] = f"{NS}p1"
    other["properties"][0]["description"] = "a different meaning"
    edges["p1"] = other
    out = compact_reply(reply)
    first = out["schema"]["edge_properties"]["p0"]["properties"][0]
    second = out["schema"]["edge_properties"]["p1"]["properties"][0]
    assert isinstance(first, str)
    assert second["description"] == "a different meaning"


def test_unmatched_view_shares_one_statement_template():
    reply = _reply()
    reply["schema"]["edge_properties"]["p0"]["pattern"] = "direct;reified"
    reply["schema"]["pattern_guidance"] = {
        "direct;reified": {
            "guidance": "use the relationship's edge_properties query_template "
            "to read edge properties",
            "count": 1,
        }
    }
    out = compact_reply(reply, templates=False)
    assert "query_template" not in out["schema"]["edge_properties"]["p0"]
    guidance = out["schema"]["pattern_guidance"]["direct;reified"]
    assert "statement_template" in guidance
    assert "kg/demo>" in guidance["statement_template"]
    assert "statement_template" in guidance["guidance"]
    # match= views keep the per-relationship template
    kept = compact_reply(reply, templates=True)
    assert "query_template" in kept["schema"]["edge_properties"]["p0"]


def test_generic_usage_line_is_dropped_but_a_specific_one_kept():
    reply = _reply()
    entry = reply["schema"]["edge_properties"]["p0"]
    entry["usage"] = (
        f"Also a direct triple: use `?s <{NS}p0> ?o` unless you need edge properties."
    )
    assert "usage" not in compact_reply(reply)["schema"]["edge_properties"]["p0"]
    entry["usage"] = "The direct triple ALSO holds GO NOT annotations."
    out = compact_reply(reply)["schema"]["edge_properties"]["p0"]
    assert out["usage"] == "The direct triple ALSO holds GO NOT annotations."


def test_labels_that_restate_the_local_name_are_blanked():
    from mcp_okn.schema_view import compact_reply

    reply = {
        "shortname": "x",
        "schema": {
            "predicates": {
                "columns": ["uri", "label"],
                "data": [
                    ["https://w3id.org/biolink/vocab/has_phenotype", "has phenotype"],
                    [
                        "http://purl.obolibrary.org/obo/RO_0002410",
                        "causally related to",
                    ],
                ],
                "count": 2,
            },
            "classes": {
                "columns": ["uri", "label"],
                "data": [["https://w3id.org/biolink/vocab/Gene", "Gene"]],
                "count": 1,
            },
        },
    }
    out = compact_reply(reply)["schema"]
    assert [r[1] for r in out["predicates"]["data"]] == [None, "causally related to"]
    assert "label" not in out["classes"]["columns"]  # every label echoed


def _template_reply(prefixes_extra=None):
    """A matched reply whose one relationship carries a generated template."""
    props = [
        {"uri": f"{NS}weight", "type": "EdgeProperty"},
        {"uri": "http://purl.org/dc/terms/source", "type": "EdgeProperty"},
        {"uri": "http://example.org/odd/ns#flag", "type": "EdgeProperty"},
    ]
    tmpl = _generate_query_template(
        "demo",
        "TREATS",
        f"{BIOLINK}Drug",
        f"{BIOLINK}Disease",
        props,
        f"{BIOLINK}treats",
    )
    schema = {
        "classes": {
            "columns": ["uri", "label"],
            "data": [[f"{BIOLINK}C{i}", f"c {i}"] for i in range(3)]
            + [[f"{NS}K{i}", f"k {i}"] for i in range(3)]
            + (prefixes_extra or []),
        },
        "predicates": {"columns": ["uri"], "data": []},
        "edge_properties": {
            "TREATS": {
                "uri": f"{BIOLINK}treats",
                "properties": props,
                "query_template": tmpl,
            }
        },
    }
    return {"shortname": "demo", "schema": schema}


def test_match_view_templates_use_the_reply_prefixes():
    out = compact_reply(_template_reply(), templates=True)
    tmpl = out["schema"]["edge_properties"]["TREATS"]["query_template"]
    assert (
        "PREFIX" not in tmpl
    )  # kg:, biolink: are in sparql_prefixes; rdf: is standard
    assert "schema:" not in tmpl
    assert "kg:weight" in tmpl and "rdf:predicate biolink:treats" in tmpl
    assert "dcterms:source" in tmpl
    assert "<http://example.org/odd/ns#flag>" in tmpl  # no prefix covers it
    assert "GRAPH <https://purl.org/okn/frink/kg/demo>" in tmpl
    assert f"PREFIX kg: <{NS}>" in out["sparql_prefixes"]


def test_template_keeps_its_own_kg_prefix_when_the_reply_has_none():
    reply = _template_reply()
    reply["schema"]["classes"]["data"] = reply["schema"]["classes"]["data"][:3]
    out = compact_reply(reply, templates=True)
    tmpl = out["schema"]["edge_properties"]["TREATS"]["query_template"]
    assert tmpl.startswith(f"PREFIX kg: <{NS}>\n")
    assert "kg:weight" in tmpl and "schema:" not in tmpl


def test_template_never_borrows_a_standard_name_the_reply_rebinds():
    # The reply calls some other namespace dcterms:, so the template must not
    # write http://purl.org/dc/terms/source as dcterms:source (dct: is safe).
    other = "http://other.example/terms/"
    extra = [[f"{other}T{i}", None] for i in range(3)]
    reply = _template_reply(extra)
    from mcp_okn import schema_view

    original = schema_view.KNOWN_PREFIXES.get(other)
    schema_view.KNOWN_PREFIXES[other] = "dcterms"
    try:
        out = compact_reply(reply, templates=True)
    finally:
        if original is None:
            schema_view.KNOWN_PREFIXES.pop(other)
        else:
            schema_view.KNOWN_PREFIXES[other] = original
    assert f"PREFIX dcterms: <{other}>" in out["sparql_prefixes"]
    tmpl = out["schema"]["edge_properties"]["TREATS"]["query_template"]
    assert "dcterms:source" not in tmpl and "dct:source" in tmpl


async def test_core_tools_load_upfront_in_claude_code():
    tools = {t.name: t for t in await srv.mcp.list_tools()}
    marked = {n for n, t in tools.items() if (t.meta or {}).get("anthropic/alwaysLoad")}
    assert marked == {"sparql_query", "get_schema", "get_join_strategy", "lookup_term"}

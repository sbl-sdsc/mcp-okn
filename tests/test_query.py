"""Tests for the query tools (mcp_okn.tools.query): expand_ontology_term's
query construction and sparql_query's error/logging behavior.

run_sparql is patched on the `query` module (where the tools look it up), and a
capturing fake records the SPARQL it was handed so the generated query can be
asserted on without hitting the network.
"""

import pytest

from mcp_okn import session
from mcp_okn.sparql import SparqlError
from mcp_okn.tools import query as query_mod
from mcp_okn.tools.query import expand_ontology_term, sparql_query


@pytest.fixture(autouse=True)
def clean_log():
    session.reset()
    yield
    session.reset()


def _capturing(result=None):
    """A fake run_sparql that records the query it receives."""
    captured = {}

    async def fake(q, fmt="json", **kw):
        captured["query"] = q
        captured["fmt"] = fmt
        return (
            result if result is not None else {"vars": [], "rows": [], "row_count": 0}
        )

    return fake, captured


# --- expand_ontology_term ----------------------------------------------------


async def test_expand_descendants_reflexive_with_curie(monkeypatch):
    fake, captured = _capturing(
        {"vars": ["term"], "rows": [{"term": "x"}], "row_count": 1}
    )
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await expand_ontology_term("MONDO:0004995")
    q = captured["query"]
    # CURIE expanded to the full OBO purl IRI via _to_uri
    assert "<http://purl.obolibrary.org/obo/MONDO_0004995>" in q
    # descendants + include_self -> reflexive `*` with ?term on the left
    assert (
        "?term rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0004995> ." in q
    )
    assert "kg/ubergraph" in q


async def test_expand_include_self_false_uses_strict_path(monkeypatch):
    fake, captured = _capturing()
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await expand_ontology_term("MONDO:0004995", include_self=False)
    assert "rdfs:subClassOf+ " in captured["query"]
    assert "rdfs:subClassOf* " not in captured["query"]


async def test_expand_ancestors_flips_pattern(monkeypatch):
    fake, captured = _capturing()
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await expand_ontology_term("MONDO:0004995", direction="ancestors")
    # ancestors: the term is on the LEFT, ?term on the right
    assert (
        "<http://purl.obolibrary.org/obo/MONDO_0004995> rdfs:subClassOf* ?term ."
        in (captured["query"])
    )


async def test_expand_partof_uses_bfo_relation(monkeypatch):
    fake, captured = _capturing()
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await expand_ontology_term("UBERON:0000948", relation="partOf")
    assert "<http://purl.obolibrary.org/obo/BFO_0000050>*" in captured["query"]


async def test_expand_passes_limit_through(monkeypatch):
    fake, captured = _capturing()
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await expand_ontology_term("MONDO:0004995", limit=7)
    assert "LIMIT 7" in captured["query"]


async def test_expand_logs_successful_query(monkeypatch):
    fake, _ = _capturing({"vars": ["term"], "rows": [{"term": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await expand_ontology_term("MONDO:0004995")
    assert len(session.entries()) == 1


async def test_expand_wraps_sparql_error_and_does_not_log(monkeypatch):
    async def boom(q, fmt="json", **kw):
        raise SparqlError("scan too broad")

    monkeypatch.setattr(query_mod, "run_sparql", boom)
    out = await expand_ontology_term("MONDO:0004995")
    assert "error" in out and "scan too broad" in out["error"]
    assert "query" in out  # the offending query is echoed back
    assert session.entries() == []


# --- sparql_query ------------------------------------------------------------


async def test_sparql_query_wraps_sparql_error(monkeypatch):
    async def boom(q, fmt="json", **kw):
        raise SparqlError("read-only filesystem")

    monkeypatch.setattr(query_mod, "run_sparql", boom)
    out = await sparql_query("SELECT ?x {}")
    assert set(out) == {"error"}
    assert "read-only filesystem" in out["error"]
    assert session.entries() == []


# --- skipped-query retention -------------------------------------------------


async def test_sparql_query_error_retained_in_skipped(monkeypatch):
    async def boom(q, fmt="json", **kw):
        raise SparqlError("read-only filesystem")

    monkeypatch.setattr(query_mod, "run_sparql", boom)
    await sparql_query("SELECT ?x { GRAPH <https://purl.org/okn/frink/kg/prokn> {} }")
    assert session.entries() == []
    [skip] = session.skipped()
    assert skip["reason"] == "error"
    assert "read-only filesystem" in skip["error"]
    assert skip["graphs"] == ["prokn"]


async def test_sparql_query_empty_result_retained_in_skipped(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [], "row_count": 0})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query("SELECT ?s {}")
    assert session.entries() == []
    [skip] = session.skipped()
    assert skip["reason"] == "empty"
    assert skip["error"] is None


async def test_sparql_query_exploratory_retained_in_skipped_not_logged(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query("SELECT ?s {}", exploratory=True)
    # Productive rows, but exploratory -> kept out of the log, filed under skipped.
    assert session.entries() == []
    [skip] = session.skipped()
    assert skip["reason"] == "exploratory"


async def test_reset_clears_skipped(monkeypatch):
    async def boom(q, fmt="json", **kw):
        raise SparqlError("boom")

    monkeypatch.setattr(query_mod, "run_sparql", boom)
    await sparql_query("SELECT ?x {}")
    assert len(session.skipped()) == 1
    session.reset()
    assert session.skipped() == []


async def test_sparql_query_logs_and_detects_graphs(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query(
        "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s ?p ?o } }"
    )
    [entry] = session.entries()
    assert entry["graphs"] == ["prokn"]


async def test_sparql_query_normalizes_schema_org_before_logging(monkeypatch):
    fake, captured = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query("SELECT ?s WHERE { ?s a <https://schema.org/Person> }")
    # the bracketed https schema.org IRI is canonicalized to http before running
    assert "<http://schema.org/Person>" in captured["query"]
    assert "<https://schema.org/Person>" not in captured["query"]


async def test_sparql_query_csv_passthrough(monkeypatch):
    async def fake(q, fmt="json", **kw):
        return {"format": "csv", "text": "s\nx"}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}", format="csv")
    assert out == {"format": "csv", "text": "s\nx"}


# --- compact format ----------------------------------------------------------


async def test_compact_is_the_default(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}")
    assert out == {"columns": ["s"], "data": [["x"]], "count": 1}


async def test_compact_reshapes_rows_into_positional_arrays(monkeypatch):
    fake, _ = _capturing(
        {
            "vars": ["disease", "mondo"],
            "rows": [
                {"disease": "asthma", "mondo": "MONDO_1"},
                {"disease": "eczema", "mondo": "MONDO_2"},
            ],
            "row_count": 2,
        }
    )
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?disease ?mondo {}", compact=True)
    assert out == {
        "columns": ["disease", "mondo"],
        "data": [["asthma", "MONDO_1"], ["eczema", "MONDO_2"]],
        "count": 2,
    }


async def test_compact_false_keeps_dict_rows(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}", compact=False)
    assert out["rows"] == [{"s": "x"}]
    assert "columns" not in out


async def test_compact_preserves_casting_and_unbound_cells(monkeypatch):
    # n is cast to int by _flatten_bindings upstream; label is unbound (OPTIONAL).
    fake, _ = _capturing({"vars": ["n", "label"], "rows": [{"n": 42}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?n ?label {}", compact=True)
    assert out["data"] == [[42, None]]  # int kept; missing var -> None, not ""


async def test_compact_carries_hint_on_empty_result(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [], "row_count": 0})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}", compact=True)
    assert out["columns"] == ["s"] and out["data"] == [] and out["count"] == 0
    assert "hint" in out


async def test_compact_does_not_affect_transcript_log(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query(
        "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s ?p ?o } }",
        compact=True,
    )
    # the session still stores dict rows, so the transcript renderer is unaffected
    [entry] = session.entries()
    assert entry["results"]["rows"] == [{"s": "x"}]


async def test_compact_passes_csv_through_unchanged(monkeypatch):
    async def fake(q, fmt="json", **kw):
        return {"format": "csv", "text": "s\nx"}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}", format="csv", compact=True)
    assert out == {"format": "csv", "text": "s\nx"}  # csv not reshaped


# --- reply budget -------------------------------------------------------------


async def test_large_result_is_capped_but_logged_whole(monkeypatch):
    rows = [{"s": f"http://example.org/entity/{i:06d}", "n": i} for i in range(5000)]
    fake, _ = _capturing({"vars": ["s", "n"], "rows": rows, "row_count": 5000})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s ?n {}")
    assert out["truncated"] is True
    assert out["count"] == 5000
    assert 0 < out["returned"] == len(out["data"]) < 5000
    assert out["data"][0] == ["http://example.org/entity/000000", 0]  # order kept
    assert "LIMIT" in out["hint"]
    from mcp_okn.budget import REPLY_CHAR_BUDGET, reply_size

    assert reply_size(out) <= REPLY_CHAR_BUDGET
    [entry] = session.entries()
    assert entry["row_count"] == 5000  # transcript keeps the full result


async def test_small_result_is_not_marked_truncated(monkeypatch):
    fake, _ = _capturing({"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}")
    assert "truncated" not in out


async def test_large_csv_is_capped(monkeypatch):
    text = "s\n" + "".join(f"http://example.org/{i:08d}\n" for i in range(5000))

    async def fake(q, fmt="json", **kw):
        return {"format": fmt, "text": text}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s {}", format="csv")
    assert out["truncated"] is True and out["total_rows"] == 5000
    assert out["text"].startswith("s\nhttp://example.org/00000000\n")


# --- lookup_term --------------------------------------------------------------


async def test_lookup_term_builds_exact_literal_lookup(monkeypatch):
    from mcp_okn.tools.query import lookup_term

    rows = [
        {
            "term": "http://purl.obolibrary.org/obo/MONDO_0004995",
            "label": "cardiovascular disorder",
            "matched_on": "exact_synonym",
            "matched_text": "cardiovascular disease",
        },
        {
            "term": "http://purl.obolibrary.org/obo/NCIT_C2931",
            "label": "Cardiovascular Disorder",
            "matched_on": "label",
            "matched_text": "Cardiovascular Disease",
        },
    ]
    fake, captured = _capturing(
        {
            "vars": ["term", "label", "matched_on", "matched_text"],
            "rows": rows,
            "row_count": 2,
        }
    )
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await lookup_term("Cardiovascular  disease", ontology="mondo")
    q = captured["query"]
    # exact literals (case variants, with/without @en) — never a FILTER scan on labels
    assert '"cardiovascular disease"@en' in q and '"Cardiovascular disease"' in q
    assert "CONTAINS" not in q and "LCASE" not in q
    assert "oio:hasExactSynonym" in q and "kg/ubergraph" in q
    assert 'obo/MONDO_"' in q
    # label matches rank ahead of synonym matches
    assert out["columns"] == ["term", "label", "matched_on", "matched_text"]
    assert out["data"][0][2] == "label"
    assert len(session.entries()) == 1  # logged, like expand_ontology_term


async def test_lookup_term_one_row_per_term(monkeypatch):
    from mcp_okn.tools.query import lookup_term

    hp = "http://purl.obolibrary.org/obo/HP_0000707"
    rows = [
        {"term": hp, "label": "Abnormality", "matched_on": "exact_synonym"},
        {"term": hp, "label": "Abnormality", "matched_on": "label"},
    ]
    fake, _ = _capturing(
        {"vars": ["term", "label", "matched_on"], "rows": rows, "row_count": 2}
    )
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await lookup_term("abnormality")
    assert out["count"] == 1 and out["data"][0][2] == "label"


async def test_lookup_term_drops_looser_synonyms_beside_exact_matches(monkeypatch):
    from mcp_okn.tools.query import lookup_term

    obo = "http://purl.obolibrary.org/obo/"
    rows = [
        {"term": obo + "MONDO_0004995", "label": "x", "matched_on": "exact_synonym"},
        {"term": obo + "HP_0001626", "label": "y", "matched_on": "related_synonym"},
        {"term": obo + "NCIT_C2931", "label": "z", "matched_on": "exact_synonym"},
    ]
    fake, _ = _capturing(
        {"vars": ["term", "label", "matched_on"], "rows": rows, "row_count": 3}
    )
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await lookup_term("cardiovascular disease")
    assert [r[0] for r in out["data"]] == [obo + "MONDO_0004995", obo + "NCIT_C2931"]
    assert "Left out 1 term" in out["note"]


async def test_lookup_term_keeps_looser_synonyms_when_nothing_matches_exactly(
    monkeypatch,
):
    from mcp_okn.tools.query import lookup_term

    mondo = "http://purl.obolibrary.org/obo/MONDO_0002081"
    rows = [{"term": mondo, "label": "x", "matched_on": "related_synonym"}]
    fake, _ = _capturing(
        {"vars": ["term", "label", "matched_on"], "rows": rows, "row_count": 1}
    )
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await lookup_term("musculoskeletal disorder")
    assert out["count"] == 1 and "different concept" in out["note"]


async def test_lookup_term_empty_result_hints_without_scan(monkeypatch):
    from mcp_okn.tools.query import lookup_term

    fake, _ = _capturing({"vars": ["term"], "rows": [], "row_count": 0})
    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await lookup_term("neurological involvement")
    assert out["count"] == 0
    assert "formal name" in out["hint"]

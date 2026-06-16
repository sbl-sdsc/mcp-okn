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

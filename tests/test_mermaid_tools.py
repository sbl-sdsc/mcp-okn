"""Tests for the sparql_to_mermaid tool: default vs portable output, and errors."""

from mcp_okn.tools.mermaid_tools import sparql_to_mermaid

# A query whose GRAPH IRI has no known prefix, so portable mode has something to compact.
_Q = (
    "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> "
    "{ ?s <http://purl.obolibrary.org/obo/RO_0002331> ?o } }"
)


async def test_default_keeps_raw_iri_in_graph_title():
    out = await sparql_to_mermaid(_Q)
    assert out["mermaid_block"].startswith("```mermaid")
    # default (portable=False): the unknown IRI stays raw in the GRAPH subgraph title
    assert "GRAPH https://purl.org/okn/frink/kg/spoke-genelab" in out["mermaid"]


async def test_portable_compacts_unknown_iri_to_curie():
    out = await sparql_to_mermaid(_Q, portable=True)
    # portable=True: the unknown IRI is compacted to a `segment:local` CURIE
    assert "kg:spoke-genelab" in out["mermaid"]
    assert "GRAPH https://purl.org/okn/frink/kg/spoke-genelab" not in out["mermaid"]


async def test_unparseable_query_returns_error():
    out = await sparql_to_mermaid("NOT A SPARQL QUERY {{{")
    assert set(out) == {"error"}

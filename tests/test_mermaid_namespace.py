"""Tests for mermaid_namespace: per-diagram id namespacing so many query diagrams
on one page don't collide on shared ids (graph0, v1, bind0, …)."""

import re

from sparql_to_mermaid import to_mermaid

from mcp_okn.mermaid_namespace import namespace_diagram, namespace_document

# Query shapes that exercise every id kind: named GRAPH, OPTIONAL, VALUES, BIND,
# UNION, FILTER, aggregate, and a URI whose PATH literally contains id-looking
# tokens (…/v1/graph0/bind0) that must survive as label text.
_QUERIES = {
    "graph_optional_values_bind": (
        "PREFIX up: <http://purl.uniprot.org/core/> "
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
        "SELECT ?protein ?name WHERE { "
        "GRAPH <https://purl.org/okn/frink/kg/prokn> { "
        "?protein a up:Protein ; rdfs:label ?name . "
        "OPTIONAL { ?protein up:annotation ?ann . } "
        "VALUES ?type { up:Disease up:Chemical up:Gene up:Foo up:Bar } "
        "BIND(STR(?name) AS ?nm) } }"
    ),
    "union_filter": (
        "PREFIX ex: <http://example.org/> "
        "SELECT ?s WHERE { { ?s ex:a ?o } UNION { ?s ex:b ?o } FILTER(?o > 5) }"
    ),
    "aggregate": (
        "PREFIX ex: <http://example.org/> "
        "SELECT ?s (COUNT(?o) AS ?n) WHERE { ?s ex:p ?o } GROUP BY ?s"
    ),
    "id_like_uri_label": (
        "PREFIX ex: <http://example.org/v1/graph0/bind0> "
        "SELECT ?s WHERE { ?s ex:v1 <http://example.org/v1/graph0/bind0> }"
    ),
}

_ID_DECL = re.compile(r"^\s*(?:subgraph\s+|style\s+)?([A-Za-z]\w*)(?:\(|\[|\{|\s|$)")


def _quoted_labels(mermaid: str) -> list[str]:
    return re.findall(r'"(?:[^"\\]|\\.)*"', mermaid)


def test_empty_prefix_is_noop():
    for q in _QUERIES.values():
        raw = to_mermaid(q)
        assert namespace_diagram(raw, "") == raw


def test_non_graph_td_passes_through():
    class_diagram = "classDiagram\n  direction TB\n  class Gene\n  Gene --> Protein"
    assert namespace_diagram(class_diagram, "q0") == class_diagram


def test_labels_are_never_rewritten():
    for name, q in _QUERIES.items():
        for portable in (False, True):
            raw = to_mermaid(q, portable=portable)
            ns = namespace_diagram(raw, "q3")
            assert _quoted_labels(raw) == _quoted_labels(ns), name


def test_every_id_gets_the_prefix_and_none_bare_survive():
    for name, q in _QUERIES.items():
        raw = to_mermaid(q)
        ids = _collect(raw)
        ns = namespace_diagram(raw, "q7")
        # Every declared id in the output now carries the namespace...
        for did in _collect(ns):
            assert did.startswith("q7"), (name, did)
        # ...and no original bare id is reachable outside a label span.
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', "", ns)
        for i in ids:
            assert not re.search(rf"(?<![A-Za-z0-9]){re.escape(i)}(?![A-Za-z0-9])", stripped), (
                name,
                i,
            )


def _collect(mermaid: str) -> set:
    ids = set()
    for line in mermaid.split("\n"):
        s = line.strip()
        if s in ("graph TD", "") or s.startswith("classDef "):
            continue
        m = _ID_DECL.match(line)
        if m and m.group(1) not in {"subgraph", "style", "end", "graph", "classDef"}:
            ids.add(m.group(1))
    return ids


def test_document_gives_each_block_a_distinct_namespace():
    a = to_mermaid(_QUERIES["union_filter"])
    b = to_mermaid(_QUERIES["graph_optional_values_bind"])
    doc = f"intro\n\n```mermaid\n{a}\n```\n\ntext\n\n```mermaid\n{b}\n```\n\nend\n"
    out = namespace_document(doc)
    # Two blocks → two namespaces; the shared bare `v1` no longer collides.
    assert "q0v1" in out and "q1v1" in out
    # Fence count unchanged (namespacing must not add/drop blocks).
    assert out.count("```mermaid") == 2
    # Non-mermaid prose is untouched.
    assert "intro" in out and "text" in out and "end" in out


def test_document_skips_classdiagram_blocks():
    schema = "classDiagram\n  class Gene\n  Gene --> Protein"
    query = to_mermaid(_QUERIES["union_filter"])
    doc = f"```mermaid\n{schema}\n```\n\n```mermaid\n{query}\n```\n"
    out = namespace_document(doc)
    assert schema in out  # classDiagram passed through verbatim
    assert "q1v1" in out  # the graph TD block (2nd) was namespaced

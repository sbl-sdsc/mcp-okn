"""The VALUES-inlining rewrite must be exact, and must leave alone what it cannot prove.

Where it applies, the original and rewritten queries are evaluated by rdflib on a
small dataset with named graphs and must return the same multiset of rows.
"""

from collections import Counter

import pytest
from rdflib import Dataset, Literal, Namespace, URIRef
from rdflib.namespace import RDF

from mcp_okn.query_rewrite import MAX_INLINE_VALUES, inline_values_for_open_predicates

EX = Namespace("http://example.org/")
G1 = URIRef("http://example.org/g1")
G2 = URIRef("http://example.org/g2")


def _dataset() -> Dataset:
    ds = Dataset()
    g1 = ds.graph(G1)
    for s, p, o in [
        (EX.a1, EX.subject, EX.d1),
        (EX.a1, RDF.type, EX.Assoc),
        (EX.a2, EX.subject, EX.d1),
        (EX.a2, EX.object, EX.d2),
        (EX.a2, RDF.type, EX.Assoc),
        (EX.a3, EX.object, EX.d2),
        (EX.a3, RDF.type, EX.Other),
        (EX.a4, EX.subject, EX.d3),
        (EX.d1, EX.label, Literal("one")),
        (EX.d2, EX.label, Literal("two")),
        (EX.d1, EX.related, EX.d2),
    ]:
        g1.add((s, p, o))
    g2 = ds.graph(G2)
    g2.add((EX.x1, EX.mentions, EX.d1))
    g2.add((EX.x2, EX.mentions, EX.d2))
    return ds


def _rows(ds: Dataset, query: str) -> Counter:
    # By variable name: rdflib's column order for SELECT * depends on the hash seed.
    return Counter(frozenset(r.asdict().items()) for r in ds.query(query))


EQUIVALENT = [
    # the motivating shape: VALUES feeding an open predicate, joined to a type
    """SELECT ?cond ?p ?cls (COUNT(*) AS ?n) WHERE {
         VALUES ?cond { <http://example.org/d1> <http://example.org/d2> }
         GRAPH <http://example.org/g1> { ?a ?p ?cond . ?a a ?cls }
       } GROUP BY ?cond ?p ?cls""",
    # one value
    """SELECT * WHERE {
         VALUES ?d { <http://example.org/d2> }
         GRAPH <http://example.org/g1> { ?a ?p ?d }
       }""",
    # prefixed names, a FILTER and a BIND that read ?x, and an OPTIONAL without it
    """PREFIX ex: <http://example.org/>
       SELECT ?x ?p ?a ?lbl ?s WHERE {
         GRAPH <http://example.org/g1> {
           ?a ?p ?x .
           OPTIONAL { ?a a ?t }
         }
         VALUES ?x { ex:d1 ex:d2 ex:d3 }
         FILTER(?x != ex:d3 || ?p = ex:subject)
         BIND(STR(?x) AS ?s)
         OPTIONAL { GRAPH <http://example.org/g1> { ?a ex:nothing ?lbl } }
       }""",
    # ?x as the subject of the open predicate, across two graphs
    """SELECT ?x ?p ?o ?m WHERE {
         VALUES ?x { <http://example.org/d1> <http://example.org/d2> }
         GRAPH <http://example.org/g1> { ?x ?p ?o }
         GRAPH <http://example.org/g2> { ?m ?q ?x }
       }""",
    # a duplicated value duplicates rows in both forms
    """SELECT ?a WHERE {
         VALUES ?d { <http://example.org/d1> <http://example.org/d1> }
         GRAPH <http://example.org/g1> { ?a ?p ?d }
       }""",
    # uses inside UNION branches, one of which does not use ?x
    """SELECT * WHERE {
         VALUES ?d { <http://example.org/d1> <http://example.org/d2> }
         { GRAPH <http://example.org/g1> { ?a ?p ?d } }
         UNION { GRAPH <http://example.org/g2> { ?a ?p ?d } }
         UNION { GRAPH <http://example.org/g2> { ?a <http://example.org/mentions> ?o } }
       }""",
    # a VALUES clause in each UNION branch
    """SELECT ?g ?cond ?p (COUNT(*) AS ?n) WHERE {
         { VALUES ?cond { <http://example.org/d1> <http://example.org/d2> }
           GRAPH <http://example.org/g1> { ?a ?p ?cond } BIND("g1" AS ?g) }
         UNION
         { VALUES ?cond { <http://example.org/d1> <http://example.org/d2> }
           GRAPH <http://example.org/g2> { ?a ?p ?cond } BIND("g2" AS ?g) }
       } GROUP BY ?g ?cond ?p""",
    # a use inside an OPTIONAL written after the VALUES clause, with a FILTER in it
    """SELECT * WHERE {
         VALUES ?d { <http://example.org/d1> <http://example.org/d2> <http://example.org/d3> }
         GRAPH <http://example.org/g2> { ?m <http://example.org/mentions> ?o }
         OPTIONAL { GRAPH <http://example.org/g1> { ?a ?p ?d } }
       }""",
    # an enclosing VALUES clause qualifies once the inner one is inlined
    """SELECT * WHERE {
         { VALUES ?d { <http://example.org/d1> <http://example.org/d2> }
           GRAPH <http://example.org/g1> { ?a ?p ?d } }
         VALUES ?a { <http://example.org/a1> <http://example.org/a2> }
         GRAPH <http://example.org/g1> { ?a ?q ?o }
       }""",
    # more than ten values, all inlined
    "SELECT * WHERE { VALUES ?d { "
    + " ".join(f"<http://example.org/d{i}>" for i in range(MAX_INLINE_VALUES))
    + " } GRAPH <http://example.org/g1> { ?a ?p ?d } }",
    # a further open-predicate hop that joins the bound triple
    """SELECT ?d ?a ?b ?q WHERE {
         VALUES ?d { <http://example.org/d1> <http://example.org/d2> }
         GRAPH <http://example.org/g1> { ?a ?p ?d . ?b ?q ?a }
       }""",
    # VALUES inside a UNION branch: the rewrite stays local to that branch
    """SELECT * WHERE {
         { VALUES ?d { <http://example.org/d1> <http://example.org/d2> }
           GRAPH <http://example.org/g1> { ?a ?p ?d } }
         UNION
         { GRAPH <http://example.org/g2> { ?a ?p ?d } }
       }""",
]


@pytest.mark.parametrize("query", EQUIVALENT)
def test_rewrite_applies_and_returns_the_same_rows(query):
    rewritten = inline_values_for_open_predicates(query)
    assert rewritten != query
    assert "VALUES" not in rewritten
    ds = _dataset()
    assert _rows(ds, rewritten) == _rows(ds, query)


def test_motivating_shape_becomes_a_union_of_constants():
    q = EQUIVALENT[0]
    out = inline_values_for_open_predicates(q)
    assert out.count("UNION") == 1
    assert "?a ?p <http://example.org/d1>" in out
    assert "BIND(<http://example.org/d2> AS ?cond)" in out
    assert out.rstrip().endswith("GROUP BY ?cond ?p ?cls")


def test_single_value_needs_no_union():
    out = inline_values_for_open_predicates(EQUIVALENT[1])
    assert "UNION" not in out
    assert "BIND(<http://example.org/d2> AS ?d)" in out


LEFT_ALONE = {
    "bound predicate": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        GRAPH <http://example.org/g1> { ?a <http://example.org/subject> ?d } }""",
    "use inside OPTIONAL": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        GRAPH <http://example.org/g1> { ?a ?p ?o OPTIONAL { ?a ?q ?d } } }""",
    "use inside MINUS": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        ?a ?p ?o MINUS { ?a ?q ?d } }""",
    "use inside EXISTS": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        ?a ?p ?o FILTER EXISTS { ?a ?q ?d } }""",
    "use inside an OPTIONAL written before the VALUES clause": """SELECT * WHERE {
        GRAPH <http://example.org/g1> { ?a a ?t }
        OPTIONAL { GRAPH <http://example.org/g1> { ?a ?p ?d } }
        VALUES ?d { <http://example.org/d1> } }""",
    "use inside an OPTIONAL nested in a GRAPH group": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        GRAPH <http://example.org/g1> { ?a a ?t OPTIONAL { ?a ?p ?d } } }""",
    "use inside an OPTIONAL inside an OPTIONAL": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        ?a a ?t OPTIONAL { ?a ?q ?b OPTIONAL { ?b ?p ?d } } }""",
    "FILTER in a nested group": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        GRAPH <http://example.org/g1> { ?a ?p ?o FILTER(?o = ?d) } ?b ?q ?d }""",
    "BIND before the VALUES clause": """SELECT * WHERE {
        ?a ?p ?d BIND(STR(?d) AS ?s)
        VALUES ?d { <http://example.org/d1> } }""",
    "subquery": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        ?a ?p ?d { SELECT ?a WHERE { ?a ?q ?o } } }""",
    "two VALUES blocks": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> } VALUES ?e { <http://example.org/d2> }
        ?a ?p ?d . ?a ?q ?e }""",
    "literal values": """SELECT * WHERE {
        VALUES ?d { "one" "two" } ?a ?p ?d }""",
    "UNDEF": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> UNDEF } ?a ?p ?d }""",
    "two variables": """SELECT * WHERE {
        VALUES (?d ?e) { (<http://example.org/d1> <http://example.org/d2>) }
        ?a ?p ?d }""",
    "trailing VALUES clause": """SELECT * WHERE { ?a ?p ?d }
        VALUES ?d { <http://example.org/d1> }""",
    "assigns the variable": """SELECT * WHERE {
        VALUES ?d { <http://example.org/d1> }
        ?a ?p ?d BIND(?a AS ?d) }""",
    "too many values": "SELECT * WHERE { VALUES ?d { "
    + " ".join(f"<http://example.org/d{i}>" for i in range(MAX_INLINE_VALUES + 1))
    + " } ?a ?p ?d }",
    "VALUES feeding a predicate variable": """SELECT * WHERE {
        VALUES ?p { <http://example.org/subject> <http://example.org/object> }
        GRAPH <http://example.org/g1> { ?go ?p ?name . ?go ?q ?other } }""",
    "an all-variable scan the branches would repeat": """SELECT * WHERE {
        GRAPH <http://example.org/g1> {
          VALUES ?a { <http://example.org/a1> <http://example.org/a2> }
          ?a ?p ?o . OPTIONAL { ?o ?p2 ?o2 } } }""",
    "an unconnected all-variable scan": """SELECT * WHERE {
        VALUES ?a { <http://example.org/a1> <http://example.org/a2> }
        ?a ?p ?o . ?m ?q ?n }""",
    "VALUES text inside a string": """SELECT * WHERE {
        ?a ?p ?d FILTER(?d != "VALUES ?d { <http://example.org/d1> }") }""",
}


@pytest.mark.parametrize("name", sorted(LEFT_ALONE))
def test_unsafe_or_unneeded_shapes_are_left_alone(name):
    q = LEFT_ALONE[name]
    assert inline_values_for_open_predicates(q) == q


def test_rewrite_is_idempotent():
    once = inline_values_for_open_predicates(EQUIVALENT[0])
    assert inline_values_for_open_predicates(once) == once

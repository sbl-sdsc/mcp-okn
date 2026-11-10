"""FILTER NOT EXISTS → MINUS and anchors copied into OPTIONALs must be exact.

Where a rewrite applies, rdflib evaluates the original and the rewritten query on a
small dataset with named graphs, and both must return the same multiset of rows.
"""

from collections import Counter

import pytest
from rdflib import Dataset, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

from mcp_okn.group_rewrite import (
    _items,
    _mask,
    _triples,
    anchor_optionals,
    delay_comparison_filters,
    filter_equality_to_join,
    not_exists_to_minus,
)
from mcp_okn.sparql import _exact_rewrite

EX = Namespace("http://example.org/")
G1 = URIRef("http://example.org/g1")
G2 = URIRef("http://example.org/g2")


def _dataset() -> Dataset:
    ds = Dataset()
    g1 = ds.graph(G1)
    for s, p, o in [
        # assays with factors; a2 has an extra factor on one side only
        (EX.a1, EX.factor1, Literal("space flight")),
        (EX.a1, EX.factor2, Literal("ground control")),
        (EX.a2, EX.factor1, Literal("space flight")),
        (EX.a2, EX.factor1, Literal("knockout")),
        (EX.a2, EX.factor2, Literal("ground control")),
        (EX.a3, EX.factor1, Literal("space flight")),
        (EX.a3, EX.factor1, Literal("knockout")),
        (EX.a3, EX.factor2, Literal("knockout")),
        (EX.a3, EX.factor2, Literal("ground control")),
        # reified statements, one negated
        (EX.s1, RDF.subject, EX.a1),
        (EX.s1, RDF.object, EX.g1),
        (EX.s2, RDF.subject, EX.a2),
        (EX.s2, RDF.object, EX.g2),
        (EX.s3, RDF.subject, EX.a3),
        (EX.s3, RDF.object, EX.g1),
        (EX.s3, RDF.type, EX.Negative),
        # genes, labels, cross-references
        (EX.g1, RDFS.label, Literal("GENE1")),
        (EX.g1, RDF.type, EX.Gene),
        (EX.g1, EX.exactMatch, EX.up1),
        (EX.g2, EX.exactMatch, EX.up2),
        (EX.g2, RDF.type, EX.Gene),
        (EX.g2, RDF.type, EX.Thing),
        (EX.ke1, EX.hasGene, EX.g1),
        (EX.ke1, RDF.type, EX.KeyEvent),
        (EX.ke2, EX.hasGene, EX.g1),
        (EX.ke2, EX.hasGene, EX.g2),
        (EX.ke1, EX.title, Literal("Event one")),
    ]:
        g1.add((s, p, o))
    g2 = ds.graph(G2)
    g2.add((EX.g1, RDFS.label, Literal("gene one")))
    g2.add((EX.a1, EX.factor1, Literal("other graph")))
    return ds


def _rows(ds: Dataset, query: str) -> Counter:
    # By variable name: rdflib's column order for SELECT * depends on the hash seed.
    return Counter(frozenset(r.asdict().items()) for r in ds.query(query))


PRE = "PREFIX ex: <http://example.org/>\n"

MINUS_EQUIVALENT = [
    # the motivating shape: clean contrasts, a negation nested in a negation
    PRE
    + """SELECT ?a ?st WHERE { GRAPH <http://example.org/g1> {
         ?st rdf:subject ?a .
         FILTER NOT EXISTS { ?a ex:factor1 ?x . FILTER(?x != "space flight")
                             FILTER NOT EXISTS { ?a ex:factor2 ?x } }
       } }""",
    # two negations on the same group, one on a reified statement
    PRE
    + """SELECT ?st ?g WHERE { GRAPH <http://example.org/g1> {
         ?st rdf:subject ?a ; rdf:object ?g .
         FILTER NOT EXISTS { ?st a ex:Negative }
         FILTER NOT EXISTS { ?n rdf:subject ?a ; rdf:object ?g ; a ex:Negative }
       } }""",
    # the FILTER written first: it still applies to the whole group
    PRE
    + """SELECT ?g WHERE { GRAPH <http://example.org/g1> {
         FILTER NOT EXISTS { ?g a ex:Thing } .
         ?g a ex:Gene .
       } }""",
    # inside an OPTIONAL: the negation's variable is bound by the OPTIONAL itself
    PRE
    + """SELECT ?ke ?g WHERE { GRAPH <http://example.org/g1> {
         ?ke ex:hasGene ?x .
         OPTIONAL { ?ke ex:hasGene ?g FILTER NOT EXISTS { ?g a ex:Thing } }
       } }""",
    # with an aggregate, and a negation that shares two variables
    PRE
    + """SELECT ?a (COUNT(*) AS ?n) WHERE { GRAPH <http://example.org/g1> {
         ?a ex:factor1 ?f .
         FILTER NOT EXISTS { ?a ex:factor2 ?f }
       } } GROUP BY ?a""",
]


@pytest.mark.parametrize("query", MINUS_EQUIVALENT)
def test_minus_rewrite_applies_and_returns_the_same_rows(query):
    rewritten = not_exists_to_minus(query)
    assert rewritten != query
    assert "NOT EXISTS" not in rewritten
    assert "MINUS" in rewritten
    ds = _dataset()
    assert _rows(ds, rewritten) == _rows(ds, query)


MINUS_LEFT_ALONE = {
    # MINUS keeps a row that shares no variable with the negated pattern
    "no shared variable": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene FILTER NOT EXISTS { ?s a ex:Negative } }""",
    # ?t is bound only optionally outside: MINUS would ignore it where unbound
    "shared variable bound only by an OPTIONAL": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene OPTIONAL { ?g ex:other ?t }
         FILTER NOT EXISTS { ?g a ?t } }""",
    # a FILTER that reads an outer variable P does not bind
    "filter reads an outer variable": PRE
    + """SELECT ?a WHERE { ?a ex:factor1 ?f
         FILTER NOT EXISTS { ?a ex:factor2 ?x FILTER(?x = ?f) } }""",
    "OPTIONAL inside": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene
         FILTER NOT EXISTS { ?g ex:exactMatch ?u OPTIONAL { ?u ex:x ?y } } }""",
    "UNION inside": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene
         FILTER NOT EXISTS { { ?g a ex:Thing } UNION { ?g ex:exactMatch ex:up1 } } }""",
    "property path inside": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene FILTER NOT EXISTS { ?g ex:exactMatch/ex:x ?y } }""",
    "blank node inside": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene FILTER NOT EXISTS { ?g ex:exactMatch [] } }""",
    "positive EXISTS": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene FILTER EXISTS { ?g a ex:Thing } }""",
    "negation inside an expression": PRE
    + """SELECT ?g WHERE { ?g a ex:Gene FILTER(!EXISTS { ?g a ex:Thing }) }""",
}


@pytest.mark.parametrize("name", sorted(MINUS_LEFT_ALONE))
def test_minus_rewrite_leaves_inexact_shapes_alone(name):
    q = MINUS_LEFT_ALONE[name]
    assert not_exists_to_minus(q) == q


ANCHOR_EQUIVALENT = [
    # the motivating shape: the anchor pins ?y, the OPTIONALs scan everything
    PRE
    + """SELECT * WHERE { GRAPH <http://example.org/g1> {
         ?y ex:exactMatch ex:up1 .
         OPTIONAL { ?y a ?ty }
         OPTIONAL { ?ke ?p ?y . OPTIONAL { ?ke a ?kty } }
       } }""",
    # a chain of two triples to the constant, and a label OPTIONAL
    PRE
    + """SELECT ?ke ?g ?l WHERE { GRAPH <http://example.org/g1> {
         ?g ex:exactMatch ex:up1 . ?ke ex:hasGene ?g .
         OPTIONAL { ?ke ex:title ?l }
       } }""",
    # a class anchor, allowed because the OPTIONAL holds an all-variable triple
    PRE
    + """SELECT * WHERE { GRAPH <http://example.org/g1> {
         ?ke a ex:KeyEvent ; ex:hasGene ?g .
         OPTIONAL { ?g ?p ?o }
       } }""",
    # several rows of the left side per anchored value
    PRE
    + """SELECT ?ke ?g ?t WHERE { GRAPH <http://example.org/g1> {
         ?ke ex:hasGene ex:g1 , ?g .
         OPTIONAL { ?g a ?t }
       } }""",
    # a constant subject behind a variable predicate, inside UNION branches
    PRE
    + """SELECT ?p ?d ?t WHERE { GRAPH <http://example.org/g1> {
         { ex:ke2 ?p ?d . OPTIONAL { ?d a ?t } }
         UNION { ?d ?p ex:g1 . OPTIONAL { ?d a ?t } }
       } }""",
    # an identifying literal as the anchor
    PRE
    + """SELECT ?ke ?g ?t WHERE { GRAPH <http://example.org/g1> {
         ?ke ex:title "Event one" ; ex:hasGene ?g .
         OPTIONAL { ?g a ?t }
       } }""",
]


@pytest.mark.parametrize("query", ANCHOR_EQUIVALENT)
def test_anchor_rewrite_applies_and_returns_the_same_rows(query):
    rewritten = anchor_optionals(query)
    assert rewritten != query
    ds = _dataset()
    assert _rows(ds, rewritten) == _rows(ds, query)


def test_a_variable_predicate_is_never_copied():
    out = anchor_optionals(ANCHOR_EQUIVALENT[0])
    # the outer OPTIONALs get the anchor; the inner one could only be reached
    # through `?ke ?p ?y`, a scan, which is not copied
    inner = out[out.rindex("OPTIONAL") :]
    assert "ex:exactMatch ex:up1" not in inner
    assert out.count("ex:exactMatch ex:up1") == 3


ANCHOR_LEFT_ALONE = {
    # QLever scopes the FILTER to the OPTIONAL, where ?u is unbound; copying the
    # anchor in would bind it and change what QLever returns
    "FILTER reads a variable bound only outside": PRE
    + """SELECT ?g ?l WHERE { GRAPH <http://example.org/g1> {
         ex:ke2 ex:hasGene ?g . ?g ex:exactMatch ?u .
         OPTIONAL { ?g rdfs:label ?l FILTER(?u = ex:up1) }
       } }""",
    "anchor reached only through a variable predicate": PRE
    + """SELECT * WHERE { ?s ?p "GCK" OPTIONAL { ?s ?q ?o } }""",
    "already anchored": PRE
    + """SELECT * WHERE { ?g ex:exactMatch ex:up1 OPTIONAL { ?g rdfs:label "GENE1" } }""",
    "anchor written after the OPTIONAL": PRE
    + """SELECT * WHERE { ?g a ex:Gene OPTIONAL { ?g rdfs:label ?l } ?g ex:exactMatch ex:up1 }""",
    "anchor only inside a nested group": PRE
    + """SELECT * WHERE { { ?g ex:exactMatch ex:up1 } OPTIONAL { ?g rdfs:label ?l } }""",
    "class anchor, narrow OPTIONAL": PRE
    + """SELECT * WHERE { ?g a ex:Gene OPTIONAL { ?g rdfs:label ?l } }""",
    "category literal, narrow OPTIONAL": PRE
    + """SELECT * WHERE { ?a ex:factor1 "space flight" OPTIONAL { ?a ex:factor2 ?f } }""",
    "nothing shared": PRE
    + """SELECT * WHERE { ?g ex:exactMatch ex:up1 OPTIONAL { ?x rdfs:label ?l } }""",
    "path in the OPTIONAL": PRE
    + """SELECT * WHERE { ?g ex:exactMatch ex:up1 OPTIONAL { ?g ex:a/ex:b ?l } }""",
}


@pytest.mark.parametrize("name", sorted(ANCHOR_LEFT_ALONE))
def test_anchor_rewrite_leaves_other_shapes_alone(name):
    q = ANCHOR_LEFT_ALONE[name]
    assert anchor_optionals(q) == q


DELAY_EQUIVALENT = [
    # the motivating shape: a comparison on a reified statement's value
    PRE
    + """SELECT ?st ?g WHERE { GRAPH <http://example.org/g1> {
         ?st rdf:subject ex:a3 ; rdf:object ?g ; ex:score ?p .
         FILTER(?p <= 0.05)
       } }""",
    # a string comparison; an error in the expression still drops the row
    PRE
    + """SELECT ?g ?l WHERE { GRAPH <http://example.org/g1> {
         ?ke ex:title "Event one" ; ex:hasGene ?g . ?g rdfs:label ?l .
         FILTER(?l != "GENE2" && STRLEN(?l) > 2)
       } }""",
    # IN over an all-variable triple, and a comparison written without spaces
    PRE
    + """SELECT ?st ?p ?o WHERE { GRAPH <http://example.org/g1> {
         ?st rdf:subject ex:a1 ; rdf:object ?g ; ?p ?o .
         FILTER(?p IN (rdf:object, ex:score))
       } }""",
    PRE
    + """SELECT ?st ?g WHERE { GRAPH <http://example.org/g1> {
         ?st rdf:subject ex:a3 ; rdf:object ?g ; ex:score ?p . FILTER(?p<0.05)
       } }""",
    # inside an OPTIONAL: the BOUND variable is bound by the OPTIONAL's own triples
    PRE
    + """SELECT ?ke ?l WHERE { GRAPH <http://example.org/g1> {
         ?ke a ex:KeyEvent .
         OPTIONAL { ?ke ex:hasGene ?g . ?g ex:exactMatch ex:up1 .
                    ?ke ex:title ?l FILTER(?l > "A") }
       } }""",
]


@pytest.mark.parametrize("query", DELAY_EQUIVALENT)
def test_delay_rewrite_applies_and_returns_the_same_rows(query):
    rewritten = delay_comparison_filters(query)
    assert rewritten != query
    assert "BOUND(" in rewritten
    ds = _dataset()
    for st, p in ((EX.s1, 0.01), (EX.s3, 0.04), (EX.s2, 0.5)):
        ds.graph(G1).add((st, EX.score, Literal(p)))
    assert _rows(ds, rewritten) == _rows(ds, query)


def test_delay_uses_a_join_key_bound_outside_the_group():
    q = (
        PRE
        + """SELECT ?gene ?p WHERE {
         GRAPH <http://example.org/g1> { ex:ke2 ex:hasGene ?g . ?g ex:exactMatch ?u }
         BIND(IRI(CONCAT(STR(?u), "")) AS ?gene)
         GRAPH <http://example.org/g1> {
           ?st rdf:object ?gene ; ex:score ?p . FILTER(?p <= 0.05)
         } }"""
    )
    out = delay_comparison_filters(q)
    assert "BOUND(?gene)" in out


DELAY_LEFT_ALONE = {
    "no anchor in the group": PRE
    + """SELECT * WHERE { ?st rdf:object ?g ; ex:score ?p FILTER(?p <= 0.05) }""",
    "only a class anchor": PRE
    + """SELECT * WHERE { ?g a ex:Gene ; ex:score ?p FILTER(?p <= 0.05) }""",
    "the filtered triple is the anchor": PRE
    + """SELECT * WHERE { ex:s1 ex:score ?p ; rdf:object ?g FILTER(?p <= 0.05) }""",
    "not a comparison": PRE
    + """SELECT * WHERE { ex:ke2 ex:hasGene ?g . ?g rdfs:label ?l FILTER(CONTAINS(?l, "G")) }""",
    "variable bound outside the group": PRE
    + """SELECT * WHERE { ?g ex:score ?p { ex:ke2 ex:hasGene ?g FILTER(?p < 1) } }""",
    "the anchored side binds only the filtered triple's variables": PRE
    + """SELECT * WHERE { ex:ke2 ex:hasGene ?g . ?g rdfs:label ?l FILTER(?l != "x") }""",
    "no other variable on the anchored side": PRE
    + """SELECT * WHERE { ?st rdf:subject ex:a3 ; ex:score ?p FILTER(?p <= 0.05) }""",
}


@pytest.mark.parametrize("name", sorted(DELAY_LEFT_ALONE))
def test_delay_rewrite_leaves_other_shapes_alone(name):
    q = DELAY_LEFT_ALONE[name]
    assert delay_comparison_filters(q) == q


def _join_dataset() -> Dataset:
    ds = _dataset()
    g2 = ds.graph(G2)
    for s, o in (
        (EX.r1, Literal("up1")),
        (EX.r2, Literal("up2")),
        (EX.r3, Literal("zz")),
        (EX.r4, EX.up1),  # an IRI: CONCAT is an error, the row must go
    ):
        g2.add((s, EX.acc, o))
    g2.add((EX.r1, EX.factor1, Literal("space flight")))
    return ds


G1_ = "GRAPH <http://example.org/g1>"
G2_ = "GRAPH <http://example.org/g2>"

EQUALITY_EQUIVALENT = [
    # the motivating shape: a key built from one graph, matched in the other
    PRE
    + f"""SELECT ?g ?r WHERE {{
         {G2_} {{ ?r ex:acc ?acc }}
         {G1_} {{ ?g ex:exactMatch ?u }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }}""",
    # written the other way round, in extra parentheses, before the blocks
    PRE
    + f"""SELECT ?g ?r WHERE {{
         FILTER((IRI(CONCAT("http://example.org/", STR(?acc))) = ?u))
         {G2_} {{ ?r ex:acc ?acc }}
         {G1_} {{ ?g ex:exactMatch ?u }} }}""",
    # two variables, one a subject: term equality
    PRE
    + f"""SELECT ?g ?l WHERE {{
         {G2_} {{ ?h rdfs:label ?l }}
         {G1_} {{ ?g a ex:Gene }}
         FILTER(?g = ?h) }}""",
    # an OPTIONAL and an aggregate after both blocks
    PRE
    + f"""SELECT ?u (COUNT(?r) AS ?n) WHERE {{
         {G2_} {{ ?r ex:acc ?acc }}
         {G1_} {{ ?g ex:exactMatch ?u }}
         OPTIONAL {{ {G1_} {{ ?k ex:hasGene ?g }} }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }} GROUP BY ?u""",
]


# rdflib joins by substituting the left side's values into the right side, so a
# BIND of the join key in the right-hand block overwrites the value instead of
# being compared with it (a cross product). SPARQL joins independently computed
# sides, as QLever does: live, the GXA x PanKgraph key bound in the first or the
# second block gave the same 8,333 rows as a reference join. The cases checked
# with rdflib therefore put the block that gets the BIND first.
@pytest.mark.parametrize("query", EQUALITY_EQUIVALENT)
def test_equality_rewrite_applies_and_returns_the_same_rows(query):
    rewritten = filter_equality_to_join(query)
    assert rewritten != query
    assert "BOUND(" in rewritten
    ds = _join_dataset()
    assert _rows(ds, rewritten) == _rows(ds, query)


def test_equality_rewrite_binds_the_key_in_the_block_that_computes_it():
    q = (
        PRE
        + f"""SELECT * WHERE {{ {G1_} {{ ?g ex:exactMatch ?u }}
         {G2_} {{ ?r ex:acc ?acc }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }}"""
    )
    out = filter_equality_to_join(q)
    assert "FILTER(?u =" not in out
    assert (
        '{ ?r ex:acc ?acc  BIND(IRI(CONCAT("http://example.org/", ?acc)) AS ?u)'
        " FILTER(BOUND(?u)) }" in out
    )
    assert "{ ?g ex:exactMatch ?u }" in out


EQUALITY_LEFT_ALONE = {
    "two object variables (literals compare by value)": PRE
    + f"""SELECT * WHERE {{ {G1_} {{ ?a ex:factor1 ?f }} {G2_} {{ ?b ex:factor1 ?h }}
         FILTER(?f = ?h) }}""",
    "?x bound only in an OPTIONAL": PRE
    + f"""SELECT * WHERE {{ {G2_} {{ ?r ex:acc ?acc }}
         OPTIONAL {{ {G1_} {{ ?g ex:exactMatch ?u }} }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }}""",
    "an OPTIONAL reads ?x before the pattern that binds it": PRE
    + f"""SELECT * WHERE {{ {G2_} {{ ?r ex:acc ?acc }}
         OPTIONAL {{ ?k ex:hasGene ?u }}
         {G1_} {{ ?g ex:exactMatch ?u }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }}""",
    "a conjunction": PRE
    + f"""SELECT * WHERE {{ {G2_} {{ ?r ex:acc ?acc }} {G1_} {{ ?g ex:exactMatch ?u }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc)) && ?acc != "zz") }}""",
    "the key and ?x in the same block": PRE
    + f"""SELECT * WHERE {{ {G1_} {{ ?g ex:exactMatch ?u ; rdfs:label ?acc }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }}""",
    "not a variable on either side": PRE
    + f"""SELECT * WHERE {{ {G2_} {{ ?r ex:acc ?acc }} {G1_} {{ ?g ex:exactMatch ?u }}
         FILTER(STR(?u) = CONCAT("http://example.org/", ?acc)) }}""",
    "a UNION branch binds the key": PRE
    + f"""SELECT * WHERE {{ {{ {G2_} {{ ?r ex:acc ?acc }} }} UNION {{ ?r ex:x ?acc }}
         {G1_} {{ ?g ex:exactMatch ?u }}
         FILTER(?u = IRI(CONCAT("http://example.org/", ?acc))) }}""",
}


@pytest.mark.parametrize("name", sorted(EQUALITY_LEFT_ALONE))
def test_equality_rewrite_leaves_other_shapes_alone(name):
    q = EQUALITY_LEFT_ALONE[name]
    assert filter_equality_to_join(q) == q


def test_rewrites_are_idempotent():
    for q in EQUALITY_EQUIVALENT:
        once = filter_equality_to_join(q)
        assert filter_equality_to_join(once) == once
    for q in DELAY_EQUIVALENT:
        once = delay_comparison_filters(q)
        assert delay_comparison_filters(once) == once
    for q in MINUS_EQUIVALENT:
        once = not_exists_to_minus(q)
        assert not_exists_to_minus(once) == once
    for q in ANCHOR_EQUIVALENT:
        once = anchor_optionals(q)
        assert anchor_optionals(once) == once


def test_triples_parser():
    text = 'ex:a ex:p ?x , "lit"@en ; a ex:C ; ex:q 5 . ?x ex:r <http://x/y> .'
    assert _triples(text, 0, len(text)) == [
        ("ex:a", "ex:p", "?x"),
        ("ex:a", "ex:p", '"lit"@en'),
        ("ex:a", "a", "ex:C"),
        ("ex:a", "ex:q", "5"),
        ("?x", "ex:r", "<http://x/y>"),
    ]
    for bad in (
        "?a ex:p/ex:q ?b",
        "?a ex:p [ ex:q ?c ]",
        "?a ex:p ( 1 2 )",
        "_:b ex:p ?o",
    ):
        assert _triples(bad, 0, len(bad)) is None


def test_items_splits_a_group():
    body = " ?a ex:p ?b . FILTER(?b > 1) OPTIONAL { ?b ex:q ?c } GRAPH <http://g> { ?c ex:r ?d } FILTER NOT EXISTS { ?d a ex:X } BIND(1 AS ?e) VALUES ?f { 1 } { ?g ex:s ?h } UNION { ?g ex:t ?h } "
    items = _items(_mask(body), 0, len(body))
    assert items is not None
    assert [it.kind for it in items] == [
        "triples",
        "filter",
        "optional",
        "graph",
        "not_exists",
        "bind",
        "values",
        "group",
        "union",
        "group",
    ]


def test_a_failing_rewrite_sends_the_query_as_written():
    def broken(q: str) -> str:
        raise ValueError("bug")

    assert _exact_rewrite(broken, "SELECT * {}", True) == "SELECT * {}"
    assert _exact_rewrite(str.upper, "q", False) == "q"

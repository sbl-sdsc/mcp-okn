"""The IRI-prefix FILTER rewrite must be exact: same rows, faster scan.

These pin WHERE it applies (positive FILTER positions only) and the shape of the
bounds. The bounds were checked live against the federation endpoint, including
IRIs from VALUES/BIND that are not in QLever's index (see query_rewrite.py).
"""

import pytest

from mcp_okn.query_rewrite import (
    _HIGH,
    _range_for,
    literal_prefix_hint,
    prefilter_prefix_tests,
)

MONDO = "http://purl.obolibrary.org/obo/MONDO_"


def _q(filter_expr: str) -> str:
    return f"SELECT * WHERE {{ ?s ?p ?x FILTER({filter_expr}) }}"


def test_rewrites_a_lone_prefix_filter_and_keeps_the_original_test():
    q = _q(f"STRSTARTS(STR(?x), '{MONDO}')")
    out = prefilter_prefix_tests(q)
    assert out != q
    # The exact test is still there: the range only lets QLever skip blocks.
    assert f"STRSTARTS(STR(?x), '{MONDO}')" in out
    assert "?x >= <http://purl.obolibrary.org/obo/MOND>" in out
    assert f"?x < <{MONDO}{_HIGH}>" in out
    # Literals keep their chance to match, as STR() gives them.
    assert "isLiteral(?x)" in out


def test_bounds_cut_before_the_last_letter_and_end_above_every_character():
    # QLever compares IRIs with their closing '>', and punctuation sorts below
    # '>': `<P>` itself would exclude `<P-x>`. Cutting before a letter avoids it.
    assert _range_for(MONDO) == ("http://purl.obolibrary.org/obo/MOND", MONDO + _HIGH)
    assert _range_for("http://purl.uniprot.org/uniprot/") == (
        "http://purl.uniprot.org/unipro",
        "http://purl.uniprot.org/uniprot/" + _HIGH,
    )


@pytest.mark.parametrize(
    "prefix",
    [
        "MESH:",  # a literal's prefix: STRSTARTS(?x, "MESH:") is the fast form
        "UMLS:C",  # short, and its only letters sit in the "scheme"
        "http://",  # no letter after the scheme
        "http://a.org/x y",  # a space cannot appear in an IRI
        "http://example.org/café/",  # non-ASCII: collation arguments are ASCII
    ],
)
def test_prefixes_without_a_safe_range_are_left_alone(prefix):
    q = _q(f"STRSTARTS(STR(?x), '{prefix}')")
    assert prefilter_prefix_tests(q) == q


def test_each_leaf_of_an_and_or_tree_is_rewritten():
    q = _q(
        f"(STRSTARTS(STR(?x), '{MONDO}') || STRSTARTS(STR(?x), 'https://b.org/y#'))"
        " && ?s != ?x"
    )
    out = prefilter_prefix_tests(q)
    assert out.count("isLiteral(?x)") == 2
    assert out.count(_HIGH) == 2
    assert "&& ?s != ?x" in out


def test_double_quoted_prefix_and_dollar_variable():
    out = prefilter_prefix_tests(_q(f'STRSTARTS(STR($x), "{MONDO}")'))
    assert f"$x < <{MONDO}{_HIGH}>" in out


def test_filter_without_outer_parentheses():
    q = f"SELECT * WHERE {{ ?s ?p ?x FILTER STRSTARTS(STR(?x), '{MONDO}') }}"
    out = prefilter_prefix_tests(q)
    assert "isLiteral(?x)" in out
    assert out.startswith("SELECT * WHERE { ?s ?p ?x FILTER (")


@pytest.mark.parametrize(
    "query",
    [
        # Negated: the added conjunct could turn an error into false, and !false
        # is true. Left alone.
        _q(f"!STRSTARTS(STR(?x), '{MONDO}')"),
        _q(f"IF(STRSTARTS(STR(?x), '{MONDO}'), true, false)"),
        _q(f"STRSTARTS(STR(?x), '{MONDO}') = true"),
        f"SELECT * WHERE {{ ?s ?p ?x BIND(STRSTARTS(STR(?x), '{MONDO}') AS ?b) }}",
        # Inside a string or a comment it is text, not a filter.
        f"SELECT * WHERE {{ ?s ?p \"FILTER(STRSTARTS(STR(?x), '{MONDO}'))\" }}",
        f"SELECT * WHERE {{ ?s ?p ?x # FILTER(STRSTARTS(STR(?x), '{MONDO}'))\n }}",
        # A computed argument, not a variable.
        _q(f"STRSTARTS(STR(IRI(?x)), '{MONDO}')"),
        _q(f"STRSTARTS(LCASE(STR(?x)), '{MONDO}')"),
    ],
)
def test_non_positive_or_non_variable_positions_are_left_alone(query):
    assert prefilter_prefix_tests(query) == query


def test_rewrite_is_idempotent():
    once = prefilter_prefix_tests(_q(f"STRSTARTS(STR(?x), '{MONDO}')"))
    assert prefilter_prefix_tests(once) == once


def test_query_without_strstarts_is_returned_unchanged():
    q = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
    assert prefilter_prefix_tests(q) is q


def test_comparison_operators_beside_the_test_are_not_taken_for_iris():
    # `?n < 5 && …` has a '<' that is an operator, not the start of an IRI.
    out = prefilter_prefix_tests(_q(f"?n < 5 && STRSTARTS(STR(?x), '{MONDO}')"))
    assert out.startswith("SELECT * WHERE { ?s ?p ?x FILTER(?n < 5 && (")
    assert "isLiteral(?x)" in out


@pytest.mark.parametrize("prefix", ["UMLS:", "cas:", "WURCS=", "NCBITaxon_"])
def test_literal_prefix_hint_names_the_curie_prefix(prefix):
    hint = literal_prefix_hint(
        f"SELECT * WHERE {{ ?s ?p ?x FILTER(STRSTARTS(STR(?x), '{prefix}')) }}"
    )
    assert hint and f'STRSTARTS(?x, "{prefix}")' in hint


@pytest.mark.parametrize(
    "query",
    [
        # An IRI prefix: the server rewrite already handles it.
        "SELECT * WHERE { ?s ?p ?x FILTER(STRSTARTS(STR(?x), 'http://purl.obolibrary.org/obo/MONDO_')) }",
        "SELECT * WHERE { ?s ?p ?x FILTER(STRSTARTS(STR(?x), 'http:')) }",
        # Already without STR().
        "SELECT * WHERE { ?s ?p ?x FILTER(STRSTARTS(?x, 'UMLS:')) }",
        # Only inside a string or a comment.
        "SELECT * WHERE { ?s ?p 'STRSTARTS(STR(?x), \"UMLS:\")' }",
        "SELECT * WHERE { ?s ?p ?x } # FILTER(STRSTARTS(STR(?x), 'UMLS:'))",
    ],
)
def test_literal_prefix_hint_stays_quiet(query):
    assert literal_prefix_hint(query) is None


def test_variables_bound_in_babel_are_left_to_the_join():
    # The 2026-11 A/B: a range on a babel-bound ?member made the clique join read
    # the whole namespace (up to 12x slower), so only ?gene is rewritten here.
    q = (
        "SELECT ?member WHERE {\n"
        "  { SELECT DISTINCT ?pref WHERE { GRAPH <https://purl.org/okn/frink/kg/babel> "
        "{ <http://x/a> <http://www.w3.org/2004/02/skos/core#exactMatch> ?pref } } }\n"
        "  GRAPH <https://purl.org/okn/frink/kg/babel> "
        "{ ?member <http://www.w3.org/2004/02/skos/core#exactMatch> ?pref }\n"
        "  FILTER(STRSTARTS(STR(?member), 'http://identifiers.org/ensembl/'))\n"
        "  GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?member <http://x/p> ?gene }\n"
        "  FILTER(STRSTARTS(STR(?gene), 'http://identifiers.org/ncbigene/'))\n"
        "}"
    )
    out = prefilter_prefix_tests(q)
    assert "?member >=" not in out
    assert "?gene >= <http://identifiers.org/ncbigen>" in out


@pytest.mark.parametrize("prefix", ["http://stko-kwg", "https://www.ensembl.org"])
def test_a_host_only_prefix_is_left_alone(prefix):
    # It matches most of a graph: the range selects nothing and turns a join
    # into a scan of every row (spatialkg county joins: 2.8 s -> 51 s).
    assert _range_for(prefix) is None
    q = f"SELECT * WHERE {{ ?s ?p ?x FILTER(STRSTARTS(STR(?x), '{prefix}')) }}"
    assert prefilter_prefix_tests(q) == q

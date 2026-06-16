import pytest

from mcp_okn.server import _to_uri
from mcp_okn.sparql import (
    _flatten_bindings,
    canonicalize_schema_org_iri,
    named_graph,
    normalize_schema_org,
)

JSON_RESULT = {
    "head": {"vars": ["s", "n", "active"]},
    "results": {
        "bindings": [
            {
                "s": {"type": "uri", "value": "http://example.org/x"},
                "n": {
                    "type": "literal",
                    "value": "42",
                    "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                },
                "active": {
                    "type": "literal",
                    "value": "false",
                    "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                },
            }
        ]
    },
}


def test_flatten_bindings_casts_types():
    rows = _flatten_bindings(JSON_RESULT)
    assert rows == [{"s": "http://example.org/x", "n": 42, "active": False}]


def test_flatten_bindings_empty():
    assert _flatten_bindings({"results": {"bindings": []}}) == []


def test_named_graph():
    assert named_graph("prokn") == "https://purl.org/okn/frink/kg/prokn"


def test_normalize_schema_org_rewrites_bracketed_iris():
    q = "SELECT ?x WHERE { ?x a <https://schema.org/Person> ; <https://schema.org/name> ?n }"
    out = normalize_schema_org(q)
    assert "https://schema.org/" not in out
    assert out.count("http://schema.org/") == 2


def test_normalize_schema_org_preserves_literals_and_concat():
    # The escape hatches for reaching https-stored schema.org data (nikg etc.) must
    # NOT be rewritten: only angle-bracketed IRIs are canonicalized.
    q = (
        "SELECT ?o WHERE { ?s ?p ?o . "
        'FILTER(STR(?p) = "https://schema.org/location") . '
        'BIND(IRI(CONCAT("https://schema.org/", "location")) AS ?pred) }'
    )
    assert normalize_schema_org(q) == q  # no bracketed IRI -> untouched
    # a bracketed predicate alongside a literal: only the bracket form flips
    q2 = '{ ?s <https://schema.org/location> ?o . FILTER(STRENDS(STR(?o),"https://schema.org/x")) }'
    out = q2.replace("<https://schema.org/location>", "<http://schema.org/location>")
    assert normalize_schema_org(q2) == out
    assert '"https://schema.org/x"' in normalize_schema_org(q2)  # literal kept


def test_normalize_schema_org_leaves_http_and_other_uris_untouched():
    q = (
        "SELECT ?x WHERE { ?x a <http://schema.org/Person> ; "
        "<https://purl.org/okn/frink/kg/x> ?y }"
    )
    # Already-http schema.org and the unrelated https purl.org URI are unchanged.
    assert normalize_schema_org(q) == q


def test_canonicalize_schema_org_iri_rewrites_bare_iri():
    assert (
        canonicalize_schema_org_iri("https://schema.org/about")
        == "http://schema.org/about"
    )
    # non-schema.org IRIs and the already-http form are untouched
    assert (
        canonicalize_schema_org_iri("http://schema.org/about")
        == "http://schema.org/about"
    )
    assert canonicalize_schema_org_iri("https://w3id.org/x") == "https://w3id.org/x"


@pytest.mark.parametrize(
    "term,expected",
    [
        ("MONDO:0003847", "http://purl.obolibrary.org/obo/MONDO_0003847"),
        ("CHEBI:24431", "http://purl.obolibrary.org/obo/CHEBI_24431"),
        (
            "http://purl.obolibrary.org/obo/GO_0008150",
            "http://purl.obolibrary.org/obo/GO_0008150",
        ),
        ("up:Disease", "up:Disease"),  # non-OBO prefix passes through unchanged
    ],
)
def test_to_uri(term, expected):
    assert _to_uri(term) == expected

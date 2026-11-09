"""The full-scan lint: which query shapes get the short time limit."""

import pytest

from mcp_okn import session
from mcp_okn.query_lint import (
    SCAN_TIMEOUT,
    add_missing_prefixes,
    check_query,
    graph_scoped_prefixes,
    named_kgs,
    scan_problem,
    unambiguous_prefixes,
)
from mcp_okn.sparql import SparqlError
from mcp_okn.tools import query as query_mod
from mcp_okn.tools.query import sparql_query

UB = "<https://purl.org/okn/frink/kg/ubergraph>"
GXA = "<https://purl.org/okn/frink/kg/gene-expression-atlas-okn>"
RDFS = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"


@pytest.mark.parametrize(
    "query",
    [
        # benchmark timeouts, verbatim shapes
        f"SELECT ?s ?p ?o WHERE {{ GRAPH {GXA} {{ ?s ?p ?o . "
        f'FILTER(CONTAINS(STR(?s),"E-MTAB-5477")) }} }} LIMIT 50',
        "SELECT DISTINCT ?p WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> "
        '{ ?s ?p ?o } FILTER(CONTAINS(LCASE(STR(?p)),"negat")) }',
        RDFS + f"SELECT ?t ?label WHERE {{ GRAPH {UB} {{ ?t rdfs:label ?label . "
        'FILTER(LCASE(STR(?label)) = "autoimmune disease") } }',
        RDFS + "SELECT ?g ?d ?l WHERE { GRAPH ?g { ?d rdfs:label ?l . "
        'FILTER(LCASE(STR(?l)) IN ("inborn error of metabolism")) } }',
    ],
)
def test_flags_full_scan_shapes(query):
    assert scan_problem(query)


@pytest.mark.parametrize(
    "query",
    [
        # subject anchored by a class
        "PREFIX up: <http://purl.uniprot.org/core/>\n" + RDFS + "SELECT * WHERE "
        "{ GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d a up:Disease ; ?p ?o . "
        '?d rdfs:label ?l FILTER(CONTAINS(LCASE(?l),"alzheimer")) } }',
        # ubergraph label filter on a closure-bounded set
        RDFS + f"SELECT * WHERE {{ GRAPH {UB} {{ ?t rdfs:subClassOf* "
        "<http://purl.obolibrary.org/obo/MONDO_0004995> . ?t rdfs:label ?l "
        'FILTER(CONTAINS(?l,"heart")) } }',
        # exact literal binding — an index lookup
        RDFS + f'SELECT ?t WHERE {{ GRAPH {UB} {{ ?t rdfs:label "asthma" }} }}',
        # VALUES-bound
        f"SELECT * WHERE {{ VALUES ?s {{ <http://x/1> }} GRAPH {GXA} {{ ?s ?p ?o "
        'FILTER(CONTAINS(STR(?o),"x")) } }',
        # no string filter at all
        f"SELECT ?p (COUNT(*) AS ?n) WHERE {{ GRAPH {GXA} {{ ?s ?p ?o }} }} GROUP BY ?p",
        # unparseable: the endpoint reports it
        "SELECT WHERE {{{",
    ],
)
def test_leaves_anchored_queries_alone(query):
    assert scan_problem(query) is None


SCAN = (
    f"SELECT ?s WHERE {{ GRAPH {GXA} {{ ?s ?p ?o . "
    'FILTER(CONTAINS(STR(?o),"E-MTAB-5477")) } } LIMIT 5'
)


@pytest.fixture(autouse=True)
def clean_log():
    session.reset()
    yield
    session.reset()


async def test_flagged_query_runs_with_short_limit(monkeypatch):
    seen = {}

    async def fake(q, fmt="json", timeout=None, **kw):
        seen["timeout"] = timeout
        return {"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query(SCAN)
    assert seen["timeout"] == SCAN_TIMEOUT
    assert out["count"] == 1  # a fast scan still answers


async def test_flagged_query_timeout_returns_rewrite(monkeypatch):
    async def fake(q, fmt="json", timeout=None, **kw):
        raise SparqlError(
            "SPARQL query stopped by the endpoint after 15s (Operation timed out)."
        )

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query(SCAN)
    assert "stopped after 15s" in out["error"]
    assert "get_schema" in out["error"] and "allow_scan=True" in out["error"]


async def test_allow_scan_uses_normal_limit(monkeypatch):
    seen = {}

    async def fake(q, fmt="json", timeout=None, **kw):
        seen["timeout"] = timeout
        return {"vars": ["s"], "rows": [], "row_count": 0}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query(SCAN, allow_scan=True)
    assert seen["timeout"] is None


async def test_unflagged_query_uses_normal_limit(monkeypatch):
    seen = {}

    async def fake(q, fmt="json", timeout=None, **kw):
        seen["timeout"] = timeout
        return {"vars": ["s"], "rows": [], "row_count": 0}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    await sparql_query("SELECT ?s WHERE { ?s a <http://x/C> }")
    assert seen["timeout"] is None


# ── shapes that QLever evaluates in isolation ────────────────────────────────

AOP = "<https://purl.org/okn/frink/kg/biobricks-aopwiki>"
VALUES_U = "VALUES ?u { <https://identifiers.org/uniprot/P01023> }"


@pytest.mark.parametrize(
    "query",
    [
        # live: HTTP 500 "Tried to allocate 235.1 GB" in under 2 s
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {VALUES_U} "
        "{ ?u ?p ?o } UNION { ?o ?p ?u } } }",
        # the anchor is a class triple outside the union
        f"SELECT * WHERE {{ GRAPH {AOP} {{ ?u a <http://x/C> . "
        "{ ?u ?p ?o } UNION { ?o ?p ?u } } }",
        # live: times out
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {VALUES_U} ?u ?p ?o . "
        "FILTER EXISTS { ?o ?q ?u } } }",
        # GRAPH ?g with the anchor outside it
        "SELECT * WHERE { VALUES ?d { <http://purl.obolibrary.org/obo/MONDO_1> } "
        "GRAPH ?g { { ?d ?p ?o } UNION { ?s ?p ?d } } }",
        # inside a subquery, anchored by a sibling of the union (live: 235 GB)
        "SELECT ?g ?d WHERE { { SELECT ?g ?d WHERE { GRAPH <http://x/rdkg> { "
        "?g a <http://x/Gene> . ?d a <http://x/Disease> . "
        "{ ?g ?p ?d } UNION { ?d ?p2 ?g } } } } }",
        # anchored by a sibling subquery (live: 235 GB in 1 s)
        "SELECT ?s ?p ?o WHERE { GRAPH <http://x/prokn> { { SELECT ?v WHERE "
        "{ ?v a <http://x/Variant> } LIMIT 2 } { ?v ?p ?o BIND(?v AS ?s) } "
        "UNION { ?s ?p ?v BIND(?v AS ?o) } } } LIMIT 40",
    ],
)
def test_blocks_anchor_outside_an_isolated_group(query):
    assert check_query(query).blocked


@pytest.mark.parametrize(
    "query",
    [
        # the same with the anchor repeated inside each branch: 0.8 s live
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {{ {VALUES_U} ?u ?p ?o }} UNION "
        f"{{ {VALUES_U} ?o ?p ?u }} }} }}",
        # constants inside the branches
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {{ <http://a> ?p ?o }} UNION "
        "{ ?o ?p <http://a> } } }",
        # a self-contained branch is lazy under LIMIT (2.6 s live)
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {{ ?s ?p ?o }} UNION {{ ?s a ?t }} }} }} "
        "LIMIT 5",
        # NOT EXISTS anchored inside itself (0.5 s live)
        f"SELECT * WHERE {{ GRAPH {AOP} {{ ?u a <http://x/K> . FILTER NOT EXISTS "
        "{ ?u ?p ?o . ?o a <http://x/S> } } }",
        # a plain nested group and a subquery see the outer VALUES
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {VALUES_U} {{ ?u ?p ?o }} }} }}",
        f"SELECT * WHERE {{ GRAPH {AOP} {{ {VALUES_U} {{ SELECT ?u ?p ?o WHERE "
        "{ ?u ?p ?o } } } }",
    ],
)
def test_leaves_reachable_anchors_alone(query):
    assert not check_query(query).blocked


async def test_blocked_query_is_not_sent(monkeypatch):
    async def fake(*a, **kw):
        raise AssertionError("must not be sent")

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    q = f"SELECT * WHERE {{ GRAPH {AOP} {{ {VALUES_U} {{ ?u ?p ?o }} UNION {{ ?o ?p ?u }} }} }}"
    out = await sparql_query(q)
    assert out["error"].startswith("Not run")
    assert "UNION branch" in out["error"] and "allow_scan=True" in out["error"]


# ── scoping slips ────────────────────────────────────────────────────────────


def test_warns_on_bind_that_cannot_see_its_variable():
    q = (
        f"SELECT ?x WHERE {{ GRAPH {AOP} {{ ?st <http://s> ?s ; <http://o> ?o . "
        "{ BIND(?s AS ?x) } UNION { BIND(?o AS ?x) } } }"
    )
    warnings = check_query(q).warnings
    assert warnings and "BIND(… AS ?x)" in warnings[0]


def test_warns_on_filter_comparing_two_graph_blocks_from_inside_one():
    # live: 0 rows; the same FILTER after both blocks returns the row
    q = (
        f"SELECT * WHERE {{ GRAPH {AOP} {{ <http://e> <http://t> ?t }} "
        f"GRAPH {AOP} {{ ?x <http://t> ?t2 FILTER(?t2 = ?t) }} }}"
    )
    warnings = check_query(q).warnings
    assert warnings and "?t" in warnings[0] and "FILTER" in warnings[0]


@pytest.mark.parametrize("kind", ["EXISTS", "NOT EXISTS"])
def test_warns_on_filter_exists_in_a_graph_block_that_does_not_bind_its_variable(
    kind,
):
    # live (nde-expand_autoimmune): inside the oard-kg block the EXISTS kept every
    # disease, the same rows as no filter; moved after the blocks it gave the key's
    q = (
        f"SELECT ?d WHERE {{ GRAPH {UB} {{ ?d <http://sub> <http://root> }} "
        f"GRAPH {AOP} {{ FILTER {kind} {{ ?a <http://subject> ?d }} }} "
        f"GRAPH {GXA} {{ ?ds <http://cond> ?d }} }}"
    )
    warnings = check_query(q).warnings
    assert len(warnings) == 1
    assert warnings[0].startswith(f"A FILTER {kind} ") and "?d" in warnings[0]
    assert "?a" not in warnings[0]  # local to the EXISTS, not a slip


@pytest.mark.parametrize(
    "query",
    [
        f"SELECT * WHERE {{ GRAPH {AOP} {{ <http://e> <http://t> ?t }} "
        f"GRAPH {AOP} {{ ?x <http://t> ?t2 }} FILTER(?t2 = ?t) }}",
        f"SELECT * WHERE {{ GRAPH {AOP} {{ ?s <http://p> ?o BIND(STR(?o) AS ?x) "
        'BIND("in" AS ?d) } }',
        f'SELECT * WHERE {{ GRAPH {AOP} {{ {{ ?a <http://p> ?b BIND("out" AS ?d) }} '
        'UNION { ?b <http://p> ?a BIND("in" AS ?d) } } }',
        # a FILTER directly in an OPTIONAL sees the outer row (LeftJoin filter)
        f"SELECT * WHERE {{ GRAPH {AOP} {{ ?a <http://p> ?b OPTIONAL "
        "{ ?b <http://q> ?c FILTER(?c != ?a) } } }",
        # aggregates and SELECT expressions
        f"SELECT ?s (COUNT(?o) AS ?n) (STR(?s) AS ?t) WHERE {{ GRAPH {AOP} "
        "{ ?s <http://p> ?o } } GROUP BY ?s",
        # FILTER EXISTS where its variable is bound: after the blocks, or in its own
        f"SELECT * WHERE {{ GRAPH {AOP} {{ ?d a <http://D> }} "
        f"FILTER EXISTS {{ GRAPH {AOP} {{ ?a <http://subject> ?d }} }} }}",
        f"SELECT * WHERE {{ GRAPH {AOP} {{ ?d a <http://D> }} GRAPH {AOP} "
        "{ ?b <http://object> ?d FILTER EXISTS { ?a <http://subject> ?d } } }",
        # an EXISTS variable the outer query also binds cannot reach a subquery
        f"SELECT * WHERE {{ {{ SELECT ?c WHERE {{ GRAPH {AOP} {{ ?c <http://k> ?k }} "
        f"FILTER EXISTS {{ GRAPH {AOP} {{ ?p <http://k> ?k }} }} }} }} "
        f"GRAPH {AOP} {{ ?p <http://q> ?c }} }}",
    ],
)
def test_no_warning_for_correct_scoping(query):
    assert check_query(query).warnings == []


async def test_warnings_ride_along_with_the_result(monkeypatch):
    async def fake(q, fmt="json", timeout=None, **kw):
        return {"vars": ["x"], "rows": [{"x": "1"}], "row_count": 1}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    q = (
        f"SELECT ?x WHERE {{ GRAPH {AOP} {{ ?st <http://s> ?s . "
        "{ BIND(?s AS ?x) } UNION { BIND(1 AS ?x) } } }"
    )
    out = await sparql_query(q)
    assert out["count"] == 1 and out["warnings"]


# ── prefixes ─────────────────────────────────────────────────────────────────


def test_adds_undeclared_standard_prefixes():
    q, added = add_missing_prefixes(
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
        'SELECT ?x WHERE { ?x rdfs:label "a:b" ; <http://x#y> ?v . '
        "FILTER(xsd:integer(?v) > 1) } # owl:Thing"
    )
    assert added == ["xsd"]  # not rdfs (declared), not a: or owl: (string/comment)
    assert q.startswith("PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n")


def test_leaves_ambiguous_and_unknown_prefixes_alone():
    q = "SELECT ?x WHERE { ?x biolink:p ?y ; schema:name ?n ; foo:bar ?z }"
    assert add_missing_prefixes(q) == (q, [])


async def test_sparql_query_reports_added_prefixes(monkeypatch):
    seen = {}

    async def fake(q, fmt="json", timeout=None, **kw):
        seen["q"] = q
        return {"vars": ["x"], "rows": [{"x": "1"}], "row_count": 1}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?x WHERE { ?x rdf:type ?t }")
    assert out["prefixes_added"] == ["rdf"]
    assert seen["q"].startswith("PREFIX rdf: ")


def test_graph_prefixes_fill_in_what_get_schema_printed():
    q = f"SELECT ?g WHERE {{ GRAPH {GXA} {{ ?g a biolink:Gene ; wobd:x ?y }} }}"
    graph = {"biolink": "https://w3id.org/biolink/vocab/", "wobd": "http://w/"}
    out, added = add_missing_prefixes(q, graph)
    assert added == ["biolink", "wobd"]
    assert out.startswith("PREFIX biolink: <https://w3id.org/biolink/vocab/>\n")
    # a standard prefix keeps its standard meaning
    assert add_missing_prefixes("SELECT * { ?s rdf:type ?t }", {"rdf": "http://no/"})[
        0
    ].startswith("PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>")


def test_named_kgs():
    q = f"SELECT * {{ GRAPH {GXA} {{ ?a ?b ?c }} GRAPH {UB} {{ ?c ?d ?e }} GRAPH {GXA} {{}} }}"
    assert named_kgs(q) == ["gene-expression-atlas-okn", "ubergraph"]


def test_unambiguous_prefixes_drop_disagreements_and_numbered_siblings():
    per_kg = {
        "a": {
            "biolink": "https://b/",
            "ex": "http://a/ex/",
            "vocab": "http://a/v/",
            "vocab2": "http://a/w/",
        },
        "b": {"biolink": "https://b/", "ex": "http://b/ex/"},
    }
    assert unambiguous_prefixes(per_kg) == {"biolink": "https://b/"}


async def test_sparql_query_adds_a_prefix_get_schema_printed(monkeypatch):
    seen = {}

    async def fake(q, fmt="json", timeout=None, **kw):
        seen["q"] = q
        return {"vars": ["g"], "rows": [{"g": "x"}], "row_count": 1}

    async def prefixes(kg):
        return {"biolink": "https://w3id.org/biolink/vocab/"} if kg == "rdkg" else {}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    monkeypatch.setattr(query_mod, "_kg_prefixes", prefixes)
    rdkg = "<https://purl.org/okn/frink/kg/rdkg>"
    out = await sparql_query(
        f"SELECT ?g WHERE {{ GRAPH {rdkg} {{ ?g a biolink:Gene }} }}"
    )
    assert out["prefixes_added"] == ["biolink"]
    assert seen["q"].startswith("PREFIX biolink: <https://w3id.org/biolink/vocab/>")


async def test_kg_prefixes_match_the_get_schema_reply():
    from mcp_okn.tools.schema_tools import get_schema

    reply = await get_schema("rdkg")
    printed = dict(
        line.removeprefix("PREFIX ").rstrip(">").split(": <")
        for line in reply.get("sparql_prefixes", "").splitlines()
    )
    query_mod._kg_prefix_cache.pop("rdkg", None)
    assert printed and await query_mod._kg_prefixes("rdkg") == printed


async def test_out_of_memory_error_gets_advice_without_the_echoed_query(monkeypatch):
    async def fake(q, fmt="json", timeout=None, **kw):
        raise SparqlError(
            "SPARQL endpoint returned HTTP 500: Tried to allocate 235.1 GB, but only "
            "30.7 GB were available\nQuery:\n" + q
        )

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query("SELECT ?s WHERE { ?s a <http://x/C> }")
    assert "Query:" not in out["error"]
    assert "UNION branch" in out["hint"]


SPOKE = "<https://purl.org/okn/frink/kg/spoke-okn>"
DIG = "<https://purl.org/okn/frink/kg/digcfdekg>"
KG_PER_GRAPH = {
    "spoke-okn": {"kg": "https://purl.org/okn/frink/kg/spoke-okn/schema/"},
    "digcfdekg": {"kg": "https://purl.org/okn/frink/kg/digcfdekg/schema/"},
}


def test_a_clashing_prefix_takes_the_meaning_of_the_graph_it_is_used_in():
    q = (
        f"SELECT ?g ?t WHERE {{ {{ SELECT DISTINCT ?g WHERE {{ GRAPH {SPOKE} "
        f"{{ <http://d/1> kg:ASSOCIATES_DaG ?g }} }} }} "
        f"GRAPH {DIG} {{ ?st <http://p> ?g ; <http://o> ?t }} }}"
    )
    assert graph_scoped_prefixes(q, KG_PER_GRAPH) == {
        "kg": "https://purl.org/okn/frink/kg/spoke-okn/schema/"
    }


@pytest.mark.parametrize(
    "where",
    [
        # used in both graphs: one PREFIX line cannot mean both
        f"GRAPH {SPOKE} {{ ?a kg:x ?g }} GRAPH {DIG} {{ ?g kg:y ?t }}",
        # used outside every GRAPH block: every named graph must agree
        f"GRAPH {SPOKE} {{ ?a <http://x> ?g }} GRAPH {DIG} {{ ?g <http://y> ?t }} "
        "?t kg:z ?w",
        # inside GRAPH ?g: the graph is unknown
        f"GRAPH {SPOKE} {{ ?a <http://x> ?g }} GRAPH ?h {{ ?g kg:y ?t }} "
        f"GRAPH {DIG} {{ ?t <http://y> ?w }}",
    ],
)
def test_a_clashing_prefix_stays_undeclared_when_its_graph_is_not_settled(where):
    assert graph_scoped_prefixes(f"SELECT * WHERE {{ {where} }}", KG_PER_GRAPH) == {}


def test_graph_scope_ignores_strings_comments_and_declared_names():
    q = (
        "PREFIX ex: <http://ex/>\n"
        f'SELECT * WHERE {{ GRAPH {SPOKE} {{ ?a kg:x "}} kg:y" ; ex:p ?b }} '
        f"# GRAPH {DIG} {{ kg:z\n"
        f"GRAPH {DIG} {{ ?b <http://y> ?c }} }}"
    )
    per_kg = {
        **KG_PER_GRAPH,
        "spoke-okn": {**KG_PER_GRAPH["spoke-okn"], "ex": "http://no/"},
    }
    assert graph_scoped_prefixes(q, per_kg) == {
        "kg": "https://purl.org/okn/frink/kg/spoke-okn/schema/"
    }


def test_graph_scope_keeps_agreeing_prefixes_used_anywhere():
    per_kg = {"a": {"biolink": "https://b/"}, "b": {"biolink": "https://b/"}}
    q = f"SELECT * {{ GRAPH {GXA} {{ ?g a biolink:Gene }} ?g a biolink:Gene }}"
    assert graph_scoped_prefixes(q, per_kg) == {"biolink": "https://b/"}


async def test_timeout_on_a_literal_prefix_test_suggests_dropping_str(monkeypatch):
    async def fake(q, fmt="json", timeout=None, **kw):
        raise SparqlError("SPARQL request timed out after 60s. Narrow it.")

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    q = (
        "SELECT ?m WHERE { GRAPH <https://purl.org/okn/frink/kg/ubergraph> { "
        "?m <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . "
        "FILTER(STRSTARTS(STR(?x), 'UMLS:')) } }"
    )
    out = await sparql_query(q)
    assert 'STRSTARTS(?x, "UMLS:")' in out["hint"]

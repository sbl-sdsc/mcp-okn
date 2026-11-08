"""The zero-row diagnosis: which part of a query lost the rows."""

import re

import pytest

from mcp_okn import diagnose, session
from mcp_okn.tools import query as query_mod
from mcp_okn.tools.query import sparql_query

OARD = "https://purl.org/okn/frink/kg/oard-kg"
RDKG = "https://purl.org/okn/frink/kg/rdkg"
SUBJ = "https://w3id.org/biolink/vocab/subject"
MONDO = "http://purl.obolibrary.org/obo/MONDO_0007179"
LABEL = "http://www.w3.org/2000/01/rdf-schema#label"


class Endpoint:
    """Answers probes by regex; anything unmatched returns no rows."""

    def __init__(self, *rules):
        self.rules = rules
        self.seen: list[str] = []

    async def __call__(self, query, timeout=None, max_retries=0, **kw):
        self.seen.append(query)
        for pattern, rows in self.rules:
            if re.search(pattern, query, re.S):
                if isinstance(rows, Exception):
                    raise rows
                return {"vars": [], "rows": rows, "row_count": len(rows)}
        return {"vars": [], "rows": [], "row_count": 0}


@pytest.fixture
def endpoint(monkeypatch):
    def install(*rules):
        ep = Endpoint(*rules)
        monkeypatch.setattr(diagnose, "run_sparql", ep)
        return ep

    return install


async def test_names_the_pattern_and_the_absent_iri(endpoint):
    endpoint()  # nothing matches anywhere
    q = (
        f"SELECT ?a WHERE {{ VALUES ?d {{ <{MONDO}> }} "
        f"GRAPH <{OARD}> {{ ?a <{SUBJ}> ?d }} }}"
    )
    notes = await diagnose.diagnose_empty(q)
    assert notes[0] == f"No match in oard-kg for `?a <{SUBJ}> <{MONDO}>`."
    assert f"<{MONDO}> occurs nowhere in oard-kg" in notes[1]


async def test_says_where_a_present_iri_does_occur(endpoint):
    endpoint(
        (
            r"GROUP BY \?p \?dir",
            [{"p": "http://x/subclass_of", "dir": "object", "n": 12}],
        ),
        (r"SELECT \?s WHERE", [{"s": "x"}]),  # the predicate is used
    )
    q = f"SELECT ?h WHERE {{ GRAPH <{RDKG}> {{ <{MONDO}> <http://x/has_phenotype> ?h }} }}"
    notes = await diagnose.diagnose_empty(q)
    assert "does occur in rdkg, as object of <http://x/subclass_of> (12)" in notes[1]


async def test_finds_the_stored_form_of_a_literal(endpoint):
    endpoint(
        (r"STR\(\?o\) AS \?text", [{"text": "Fabry disease", "lang": "en", "dt": ""}]),
        (r"SELECT \?s WHERE", [{"s": "x"}]),
    )
    q = f'SELECT ?s WHERE {{ GRAPH <{OARD}> {{ ?s <{LABEL}> "Fabry disease" }} }}'
    notes = await diagnose.diagnose_empty(q)
    assert '"Fabry disease"@en is' in notes[-1]


async def test_samples_both_sides_of_a_join_that_shares_no_value(endpoint):
    ep = endpoint(
        # every single pattern and each block matches...
        (r"LIMIT 1$", [{"x": "1"}]),
        (
            r"DISTINCT \?gene .*digcfdekg",
            [{"gene": "http://www.ncbi.nlm.nih.gov/gene/1"}],
        ),
        (r"DISTINCT \?gene .*rdkg", [{"gene": "http://identifiers.org/ncbigene/1"}]),
    )
    # ...but the joined probe (both GRAPH blocks) finds nothing
    ep.rules = (
        (r"GRAPH <[^>]*digcfdekg>.*GRAPH <[^>]*rdkg>.*LIMIT 1$", []),
        *ep.rules,
    )
    q = (
        "SELECT * WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> "
        "{ ?st <http://x/object> <http://x/T> . ?st <http://x/subject> ?gene } "
        f"GRAPH <{RDKG}> {{ ?gene <http://x/rel> ?d . ?d a <http://x/Disease> }} }}"
    )
    notes = await diagnose.diagnose_empty(q)
    assert (
        "ncbi.nlm.nih.gov/gene/1" in notes[0]
        and "identifiers.org/ncbigene/1" in notes[0]
    )
    assert "share no value" in notes[1]


async def test_a_failed_probe_is_never_reported_as_empty(endpoint):
    endpoint((r".", RuntimeError("429")))
    q = f"SELECT ?a WHERE {{ GRAPH <{OARD}> {{ ?a <{SUBJ}> <{MONDO}> }} }}"
    assert await diagnose.diagnose_empty(q) == []


async def test_untested_union_is_named(endpoint):
    endpoint((r"LIMIT 1$", [{"x": "1"}]))
    q = (
        f"SELECT * WHERE {{ GRAPH <{RDKG}> {{ <{MONDO}> <http://x/p> ?d . "
        "{ ?d <http://x/q> ?e } UNION { ?e <http://x/q> ?d } } }"
    )
    notes = await diagnose.diagnose_empty(q)
    assert notes and "Not tested: UNION" in notes[-1]


async def test_probes_are_capped(endpoint, monkeypatch):
    ep = endpoint((r"LIMIT 1$", [{"x": "1"}]))
    monkeypatch.setattr(diagnose, "MAX_PROBES", 3)
    triples = " . ".join(f"<http://x/s{i}> <http://x/p> ?o{i}" for i in range(10))
    await diagnose.diagnose_empty(
        f"SELECT * WHERE {{ GRAPH <{RDKG}> {{ {triples} }} }}"
    )
    assert len(ep.seen) <= 3


async def test_sparql_query_attaches_the_diagnosis(endpoint, monkeypatch):
    session.reset()
    endpoint()

    async def fake(q, fmt="json", timeout=None, **kw):
        return {"vars": ["a"], "rows": [], "row_count": 0}

    monkeypatch.setattr(query_mod, "run_sparql", fake)
    out = await sparql_query(
        f"SELECT ?a WHERE {{ GRAPH <{OARD}> {{ ?a <{SUBJ}> <{MONDO}> }} }}"
    )
    assert out["count"] == 0
    assert out["diagnosis"][0].startswith("No match in oard-kg")
    assert "hint" in out
    session.reset()


async def test_a_union_whose_branches_all_miss_is_blamed(endpoint):
    # nothing matches: HP_0000707 is written another way in rdkg
    endpoint((r"SELECT \?s WHERE", [{"s": "x"}]))  # the predicate is used
    hp = "http://purl.obolibrary.org/obo/HP_0000707"
    q = (
        f"SELECT ?d WHERE {{ GRAPH <{RDKG}> {{ "
        f"{{ ?d <http://x/has_phenotype> <{hp}> }} UNION "
        f"{{ <{hp}> <http://x/has_phenotype> ?d }} "
        "?v <http://x/causes> ?d } }"
    )
    notes = await diagnose.diagnose_empty(q)
    assert notes[0].startswith("No branch of the UNION matches in rdkg")
    assert f"<{hp}> occurs nowhere in rdkg" in notes[1]
    assert len(notes) == 2  # the shared IRI is looked up once


async def test_a_union_with_a_matching_branch_is_not_blamed(endpoint):
    endpoint((r"<http://x/a> <http://x/p> \?o \}.*LIMIT 1$", [{"o": "1"}]))
    q = (
        f"SELECT * WHERE {{ GRAPH <{RDKG}> {{ "
        "{ <http://x/a> <http://x/p> ?o } UNION { ?o <http://x/p> <http://x/a> } } }"
    )
    notes = await diagnose.diagnose_empty(q)
    assert not any("No branch" in n for n in notes)


async def test_a_values_list_of_absent_iris(endpoint):
    endpoint((r"SELECT \?s WHERE", [{"s": "x"}]))
    q = (
        f"SELECT ?a WHERE {{ VALUES ?d {{ <{MONDO}> <http://x/M2> }} "
        f"GRAPH <{OARD}> {{ ?a <{SUBJ}> ?d }} }}"
    )
    notes = await diagnose.diagnose_empty(q)
    assert "with ?d from its VALUES list (2)" in notes[0]
    assert "None of the 2 IRIs in the VALUES list" in notes[1]


async def test_a_values_list_of_labels_shows_the_stored_form(endpoint):
    endpoint(
        (r"ISLITERAL", [{"text": "Heart disease", "lang": "en", "dt": ""}]),
        (r"SELECT \?s WHERE", [{"s": "x"}]),
    )
    q = (
        f'SELECT ?s WHERE {{ GRAPH <{OARD}> {{ VALUES ?l {{ "cardio a" "cardio b" }} '
        f"?s <{LABEL}> ?l }} }}"
    )
    notes = await diagnose.diagnose_empty(q)
    assert "equals the listed values" in notes[-1]
    assert '"Heart disease"@en' in notes[-1]


async def test_blocks_meeting_on_a_values_variable_are_connected(endpoint):
    endpoint((r".", [{"x": "1"}]))  # every probe matches
    q = (
        f"SELECT ?s WHERE {{ VALUES ?m {{ <{MONDO}> }} "
        f"GRAPH <{OARD}> {{ ?s <{SUBJ}> ?m }} GRAPH <{RDKG}> {{ ?t <{SUBJ}> ?m }} "
        "FILTER(?s != ?t) }"
    )
    notes = await diagnose.diagnose_empty(q)
    assert not any("share no variable" in n or "No variable" in n for n in notes)
    assert "a FILTER" in notes[-1]

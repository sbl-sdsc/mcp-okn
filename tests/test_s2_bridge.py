"""Tests for the S2 spatial-bridge tools (mcp_okn.tools.s2_bridge).

The point->cell primitive is exercised directly (deterministic, no network); the
bridge tools patch `run_sparql` on the module — where the helpers look it up — and
queue per-call results so the fetch->compute->inject pipeline can be asserted on
without hitting FRINK.
"""

import pytest

from mcp_okn.sparql import SparqlError
from mcp_okn.tools import s2_bridge as s2


def _result(rows):
    return {"vars": list(rows[0]) if rows else [], "rows": rows, "row_count": len(rows)}


def _queued(*result_rows):
    """A fake run_sparql returning queued results in order, recording each query."""
    queue = list(result_rows)
    captured = []

    async def fake(q, fmt="json", **kw):
        captured.append(q)
        return _result(queue.pop(0))

    return fake, captured


# --- point primitive ---------------------------------------------------------


def test_point_to_s2_iri_matches_verified_cell():
    # Cary, NC -> the documented spatialkg cell IRI (Wake County).
    iri = s2.point_to_s2_iri(35.7956, -78.7941)
    assert iri == f"{s2.KWG_S2_PREFIX}9920570487421796352"


def test_point_to_s2_iri_accepts_string_coords():
    # SPARQL literals may arrive as strings; the primitive floats them.
    assert s2.point_to_s2_iri("35.7956", "-78.7941") == s2.point_to_s2_iri(
        35.7956, -78.7941
    )


async def test_point_to_s2_tool():
    assert await s2.point_to_s2(35.7956, -78.7941) == (
        f"{s2.KWG_S2_PREFIX}9920570487421796352"
    )


# --- point query construction ------------------------------------------------


def test_sudokn_point_query_plain_selects_geospatialsites():
    q = s2.sudokn_point_query()
    assert "?site a s:GeospatialSite ." in q
    assert "hasPrimaryNAICSClassifier" not in q
    assert f"GRAPH <{s2.SUDOKN_GRAPH}>" in q


def test_sudokn_point_query_naics_drops_type_decl_and_scopes():
    q = s2.sudokn_point_query(naics="332813")
    assert "NAICS%20332813-individual" in q
    # NAICS scoping derives ?site from ?company, so the bare type decl is dropped
    assert "?site a s:GeospatialSite ." not in q


def test_sudokn_point_query_state_filter():
    assert 's:locatedInState/rdfs:label "Maine"' in s2.sudokn_point_query(state="Maine")


# --- VALUES block ------------------------------------------------------------


def test_values_block_escapes_and_pairs():
    block = s2._values_block([("http://x/site1", "http://x/cell1")])
    assert "VALUES (?site ?cell)" in block
    assert "(<http://x/site1> <http://x/cell1>)" in block


# --- bridge pipeline ---------------------------------------------------------


async def test_join_via_s2_computes_and_injects_cell(monkeypatch):
    fake, captured = _queued(
        [{"site": "http://x/site1", "lat": 35.7956, "lng": -78.7941}],  # point fetch
        [{"site": "http://x/site1", "fips": "37183"}],  # final join
    )
    monkeypatch.setattr(s2, "run_sparql", fake)
    out = await s2.join_via_s2("POINTQ", "TARGET", select_vars="?site ?fips")
    # second query carries the computed cell IRI in an injected VALUES block
    final = captured[1]
    assert "VALUES (?site ?cell)" in final
    assert "9920570487421796352" in final
    assert "TARGET" in final
    assert out == [{"site": "http://x/site1", "fips": "37183"}]


async def test_join_via_s2_skips_points_without_coords(monkeypatch):
    fake, captured = _queued(
        [
            {"site": "http://x/a", "lat": None, "lng": None},
            {"site": "http://x/b", "lat": 35.7956, "lng": -78.7941},
        ],
        [{"site": "http://x/b"}],
    )
    monkeypatch.setattr(s2, "run_sparql", fake)
    await s2.join_via_s2("POINTQ", "TARGET")
    # only the coordinate-bearing site is injected
    assert "http://x/b" in captured[1]
    assert "http://x/a" not in captured[1]


async def test_join_via_s2_returns_empty_without_running_final(monkeypatch):
    fake, captured = _queued([])  # no points; final query must NOT run
    monkeypatch.setattr(s2, "run_sparql", fake)
    assert await s2.join_via_s2("POINTQ", "TARGET") == []
    assert len(captured) == 1


async def test_join_via_s2_enforces_max_points(monkeypatch):
    too_many = [
        {"site": f"http://x/{i}", "lat": 35.0, "lng": -78.0}
        for i in range(s2.MAX_POINTS + 1)
    ]
    fake, _ = _queued(too_many)
    monkeypatch.setattr(s2, "run_sparql", fake)
    with pytest.raises(ValueError, match="exceed MAX_POINTS"):
        await s2.join_via_s2("POINTQ", "TARGET")


async def test_sudokn_spatial_join_wraps_sparql_error(monkeypatch):
    async def boom(q, fmt="json", **kw):
        raise SparqlError("scan too broad")

    monkeypatch.setattr(s2, "run_sparql", boom)
    out = await s2.sudokn_spatial_join(naics="332813")
    assert out == {"error": "scan too broad"}

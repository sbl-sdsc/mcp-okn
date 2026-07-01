"""Tests for the VoID provenance tool (mcp_okn.void + get_kg_version).

run_sparql is patched on the `void` module (where the code looks it up), and a
capturing fake records the SPARQL it was handed so the generated query can be
asserted on without hitting the network.
"""

from mcp_okn import void
from mcp_okn.tools.discovery import get_kg_version


def _capturing(rows):
    captured = {}

    async def fake(q, client=None, **kw):
        captured["query"] = q
        return {"vars": ["s", "version", "last_updated", "modified"], "rows": rows}

    return fake, captured


_PROKN_ROW = {
    "s": "https://purl.org/okn/frink/kg/prokn",
    "version": "v0.0.5",
    "last_updated": "2026-06-23T14:26:02.126+00:00",
    "modified": "Jun 2026",
}


def test_version_query_targets_okn_void_and_pav_predicates():
    q = void._version_query(None)
    assert "kg/okn-void" in q
    assert "http://purl.org/pav/version" in q
    assert "http://purl.org/pav/lastUpdatedOn" in q
    assert "http://purl.org/dc/terms/modified" in q
    # No-shortname form scans all subjects.
    assert "?s <http://purl.org/pav/version>" in q


def test_version_query_for_one_kg_anchors_on_its_named_graph():
    q = void._version_query("prokn")
    assert "<https://purl.org/okn/frink/kg/prokn> <http://purl.org/pav/version>" in q


def test_shortname_from_iri_strips_prefix():
    assert (
        void._shortname_from_iri("https://purl.org/okn/frink/kg/spoke-okn")
        == "spoke-okn"
    )


async def test_get_kg_version_single_returns_record(monkeypatch):
    fake, _ = _capturing([_PROKN_ROW])
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("prokn")
    assert out["shortname"] == "prokn"
    assert out["version"] == "v0.0.5"
    assert out["last_updated"].startswith("2026-06-23")
    assert out["modified"] == "Jun 2026"
    assert out["named_graph"] == "https://purl.org/okn/frink/kg/prokn"


async def test_get_kg_version_missing_kg_returns_note(monkeypatch):
    fake, _ = _capturing([])
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("bio101")
    assert out["shortname"] == "bio101"
    assert out["version"] is None
    assert "No VoID provenance" in out["note"]


async def test_get_kg_version_all_sorted_and_counted(monkeypatch):
    rows = [
        {
            "s": "https://purl.org/okn/frink/kg/spoke-okn",
            "version": "v0.0.6",
            "last_updated": "2026-03-16T02:27:00.564+00:00",
            "modified": "Mar 2026",
        },
        _PROKN_ROW,
    ]
    fake, _ = _capturing(rows)
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version()
    assert out["count"] == 2
    # Sorted by shortname regardless of result order.
    assert [r["shortname"] for r in out["versions"]] == ["prokn", "spoke-okn"]


async def test_get_kg_version_filters_excluded_kgs(monkeypatch):
    rows = [
        _PROKN_ROW,
        {
            "s": "https://purl.org/okn/frink/kg/semopenalex",
            "version": "v9",
            "last_updated": None,
            "modified": None,
        },
    ]
    fake, _ = _capturing(rows)
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version()
    assert [r["shortname"] for r in out["versions"]] == ["prokn"]


async def test_get_kg_version_handles_missing_optional_dates(monkeypatch):
    fake, _ = _capturing(
        [{"s": "https://purl.org/okn/frink/kg/maudekg", "version": "v0.0.1"}]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("maudekg")
    assert out["version"] == "v0.0.1"
    assert out["last_updated"] is None
    assert out["modified"] is None

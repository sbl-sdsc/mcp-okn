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
        return {"vars": ["s", "version", "last_updated"], "rows": rows}

    return fake, captured


_PROKN_ROW = {
    "s": "https://purl.org/okn/frink/kg/prokn",
    "version": "v0.0.5",
    "last_updated": "2026-06-23T14:26:02.126+00:00",
}


def test_version_query_targets_okn_void_and_pav_predicates():
    q = void._version_query(None)
    assert "kg/okn-void" in q
    assert "http://purl.org/pav/version" in q
    assert "http://purl.org/pav/lastUpdatedOn" in q
    # No-shortname form scans all subjects.
    assert "?s <http://purl.org/pav/version>" in q


def test_version_query_for_one_kg_anchors_on_its_named_graph():
    q = void._version_query("prokn")
    assert "<https://purl.org/okn/frink/kg/prokn> <http://purl.org/pav/version>" in q


def test_profile_query_counts_top_level_partitions():
    q = void._profile_query("prokn")
    assert "kg/okn-void" in q
    assert "kg/prokn" in q
    assert "void#triples" in q
    assert "void#classPartition" in q
    assert "void#propertyPartition" in q
    assert "COUNT(DISTINCT ?class_partition)" in q
    assert "COUNT(DISTINCT ?property_partition)" in q


def test_observed_edges_query_uses_nested_void_partitions():
    q = void._observed_edges_query(
        "prokn",
        class_uris=["http://ex.org/Gene", "http://ex.org/Disease"],
        predicate_uris=["http://ex.org/associated_with"],
        limit=25,
    )
    assert "void#classPartition" in q
    assert "void#propertyPartition" in q
    assert "void-ext#objectClassPartition" in q
    assert "VALUES ?source_class" in q
    assert "VALUES ?target_class" in q
    assert "VALUES ?predicate" in q
    assert q.rstrip().endswith("LIMIT 25")


def test_value_shapes_query_uses_class_level_property_partitions():
    q = void._value_shapes_query("prokn", limit=25)
    assert "void#classPartition" in q
    assert "void#propertyPartition" in q
    assert "void-ext#datatypePartition" in q
    assert "void-ext#languagePartition" in q
    assert q.rstrip().endswith("LIMIT 25")


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
    assert "modified" not in out
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
        },
    ]
    fake, _ = _capturing(rows)
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version()
    assert [r["shortname"] for r in out["versions"]] == ["prokn"]


async def test_get_kg_version_handles_missing_optional_dates(monkeypatch):
    fake, _ = _capturing(
        [{"s": "https://purl.org/okn/frink/kg/medical-device-kg", "version": "v0.0.1"}]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("medical-device-kg")
    assert out["version"] == "v0.0.1"
    assert out["last_updated"] is None
    assert "modified" not in out


async def test_fetch_profile_projects_dataset_statistics(monkeypatch):
    fake, _ = _capturing(
        [
            {
                "version": "v0.0.5",
                "last_updated": "2026-06-23T14:26:02.126+00:00",
                "triples": 99302327,
                "properties": 218,
                "class_count": 42,
                "predicate_count": 218,
            }
        ]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await void.fetch_profile("prokn")
    assert out == {
        "shortname": "prokn",
        "named_graph": "https://purl.org/okn/frink/kg/prokn",
        "version": "v0.0.5",
        "last_updated": "2026-06-23T14:26:02.126+00:00",
        "triple_count": 99302327,
        "property_count": 218,
        "class_count": 42,
        "predicate_count": 218,
    }


async def test_fetch_profile_returns_none_when_only_zero_counts_exist(monkeypatch):
    fake, _ = _capturing([{"class_count": 0, "predicate_count": 0}])
    monkeypatch.setattr(void, "run_sparql", fake)
    assert await void.fetch_profile("bio101") is None


async def test_fetch_schema_partitions_splits_classes_and_predicates(monkeypatch):
    fake, _ = _capturing(
        [
            {"kind": "class", "uri": "http://ex.org/Gene", "count": 12},
            {
                "kind": "predicate",
                "uri": "http://ex.org/associated_with",
                "count": 34,
            },
        ]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await void.fetch_schema_partitions("demo")
    assert out["classes"] == [{"uri": "http://ex.org/Gene", "entity_count": 12}]
    assert out["predicates"] == [
        {"uri": "http://ex.org/associated_with", "triple_count": 34}
    ]


async def test_fetch_observed_edges_projects_paths(monkeypatch):
    fake, captured = _capturing(
        [
            {
                "source_class": "http://ex.org/Gene",
                "predicate": "http://ex.org/associated_with",
                "target_class": "http://ex.org/Disease",
                "triple_count": 17,
            }
        ]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await void.fetch_observed_edges(
        "demo",
        class_uris=["http://ex.org/Gene", "http://ex.org/Disease"],
        predicate_uris=["http://ex.org/associated_with"],
        limit=10,
    )
    assert out[0]["triple_count"] == 17
    assert "LIMIT 10" in captured["query"]


async def test_fetch_value_shapes_projects_datatypes_and_languages(monkeypatch):
    fake, captured = _capturing(
        [
            {
                "predicate": "http://ex.org/name",
                "kind": "language",
                "value": "en",
                "triple_count": 9,
            }
        ]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await void.fetch_value_shapes("demo", limit=10)
    assert out == [
        {
            "predicate": "http://ex.org/name",
            "kind": "language",
            "value": "en",
            "triple_count": 9,
        }
    ]
    assert "void-ext#languagePartition" in captured["query"]

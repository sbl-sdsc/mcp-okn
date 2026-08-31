from mcp_okn import registry
from mcp_okn.registry import _meta_from_front, _split_frontmatter
from mcp_okn.sparql import SparqlError

SAMPLE = """\
---
template: overrides/kg.html
shortname: prokn
title: Protein Knowledge Network
description: ProKN integrates protein-centric data with CFDE datasets.
homepage: https://research.bioinformatics.udel.edu/ProKN/
sparql: https://apps.okn.us/prokn/sparql
tpf: https://apps.okn.us/ldf/prokn
---
The Protein Knowledge Network (ProKN), developed by the University of Delaware.
"""


def test_split_frontmatter_parses_yaml_and_body():
    front, body = _split_frontmatter(SAMPLE)
    assert front["shortname"] == "prokn"
    assert front["title"] == "Protein Knowledge Network"
    assert body.startswith("The Protein Knowledge Network")


def test_meta_drops_per_kg_endpoints_and_builds_named_graph():
    front, _ = _split_frontmatter(SAMPLE)
    meta = _meta_from_front("prokn", front)
    # The per-KG Jena endpoints must never be surfaced.
    assert "sparql" not in meta
    assert "tpf" not in meta
    assert meta["named_graph"] == "https://purl.org/okn/frink/kg/prokn"
    assert meta["description"].startswith("ProKN integrates")


def test_split_frontmatter_no_fence():
    front, body = _split_frontmatter("just text, no frontmatter")
    assert front == {}
    assert body == "just text, no frontmatter"


async def test_fetch_kg_long_description_returns_body(monkeypatch):
    async def fake_doc(shortname, client=None, refresh=False):
        assert shortname == "prokn"
        return SAMPLE

    monkeypatch.setattr(registry, "fetch_kg_doc", fake_doc)
    body = await registry.fetch_kg_long_description("prokn")
    # The free-text prose, not the YAML frontmatter.
    assert body.startswith("The Protein Knowledge Network")
    assert "shortname:" not in body


async def test_describe_kg_long_description_returns_only_prose(monkeypatch):
    from mcp_okn import server

    async def fake_doc(shortname, client=None, refresh=False):
        return SAMPLE

    monkeypatch.setattr(registry, "fetch_kg_doc", fake_doc)
    full = await server.describe_kg("prokn")
    prose = await server.describe_kg("prokn", long_description=True)
    # Full keeps the frontmatter; the long_description option strips it.
    assert "shortname: prokn" in full
    assert "shortname:" not in prose
    assert prose.startswith("The Protein Knowledge Network")
    # prokn has no usage notes -> nothing appended.
    assert "Assay-comparison rules" not in full


async def test_describe_kg_appends_assay_rules_for_spoke_genelab(monkeypatch):
    from mcp_okn import server

    async def fake_doc(shortname, client=None, refresh=False):
        return "# spoke-genelab\n\nNASA GeneLab spaceflight omics."

    async def fake_long(shortname, client=None, refresh=False):
        return "NASA GeneLab spaceflight omics."

    monkeypatch.setattr(registry, "fetch_kg_doc", fake_doc)
    monkeypatch.setattr(registry, "fetch_kg_long_description", fake_long)

    for kwargs in ({}, {"long_description": True}):
        out = await server.describe_kg("spoke-genelab", **kwargs)
        assert "Assay-comparison rules (spoke-genelab)" in out
        assert "DIRECTION" in out and "COMPARABILITY" in out
        # Points at the reusable snippet without inlining it here.
        assert 'get_schema("spoke-genelab")' in out


async def test_describe_kg_optionally_appends_void_profile(monkeypatch):
    from mcp_okn import server, void

    async def fake_doc(shortname, client=None, refresh=False):
        return "# prokn\n\nProtein knowledge graph."

    async def fake_profile(shortname, client=None):
        return {
            "shortname": "prokn",
            "named_graph": "https://purl.org/okn/frink/kg/prokn",
            "version": "v0.0.5",
            "last_updated": "2026-06-23T14:26:02.126+00:00",
            "triple_count": 99302327,
            "property_count": 218,
            "class_count": 42,
            "predicate_count": 218,
        }

    monkeypatch.setattr(registry, "fetch_kg_doc", fake_doc)
    monkeypatch.setattr(void, "fetch_profile", fake_profile)
    out = await server.describe_kg("prokn", include_profile=True)
    assert "## Dataset profile (VoID)" in out
    assert "**Version:** v0.0.5" in out
    assert "**Triples:** 99,302,327" in out
    assert "**Observed classes:** 42" in out
    assert "**Observed predicates:** 218" in out


async def test_describe_kg_profile_is_opt_in(monkeypatch):
    from mcp_okn import server, void

    async def fake_doc(shortname, client=None, refresh=False):
        return "# prokn"

    async def should_not_fetch(shortname, client=None):
        raise AssertionError("VoID profile should be opt-in")

    monkeypatch.setattr(registry, "fetch_kg_doc", fake_doc)
    monkeypatch.setattr(void, "fetch_profile", should_not_fetch)
    assert await server.describe_kg("prokn") == "# prokn"


async def test_describe_kg_surfaces_profile_failure(monkeypatch):
    from mcp_okn import server, void

    async def fake_doc(shortname, client=None, refresh=False):
        return "# prokn"

    async def unavailable(shortname, client=None):
        raise SparqlError("endpoint unavailable\nQuery: SELECT ...")

    monkeypatch.setattr(registry, "fetch_kg_doc", fake_doc)
    monkeypatch.setattr(void, "fetch_profile", unavailable)
    out = await server.describe_kg("prokn", include_profile=True)
    assert "Dataset profile unavailable: endpoint unavailable" in out
    assert "Query:" not in out

import json

import pytest

import mcp_okn.crosswalks as cw
from mcp_okn.registry import load_snapshot
from mcp_okn.server import _complementary_note, get_join_strategy, list_crosswalks


def test_table_loads_and_is_dated():
    data = cw.load_crosswalks()
    assert isinstance(data, dict)
    assert data.get("verified_crosswalks")
    assert cw.verified_on()  # a YYYY-MM-DD stamp for staleness visibility


def test_join_between_is_order_insensitive():
    a = cw.join_between("biobricks-aopwiki", "rdkg")
    b = cw.join_between("rdkg", "biobricks-aopwiki")
    assert a and a == b


def test_join_recipe_carries_the_fields_needed_to_build_sparql():
    (recipe,) = cw.join_between("biobricks-aopwiki", "rdkg")
    for field in (
        "left_predicate",
        "right_predicate",
        "left_role",
        "right_role",
        "shared_key",
        "key_namespace",
        "verified_count",
    ):
        assert field in recipe


def test_bridged_pair_surfaces_via_bridge_kg():
    # spoke-okn reaches rdkg only through ubergraph (DOID<->MONDO, entry A10).
    joins = cw.join_between("spoke-okn", "rdkg")
    assert any(j.get("bridge_kg") == "ubergraph" for j in joins)


@pytest.mark.asyncio
async def test_verified_pair_returns_recipe():
    out = await get_join_strategy("biobricks-aopwiki", "rdkg")
    assert out["status"] == "verified"
    assert out["joins"]
    assert out["verified_on"]


@pytest.mark.asyncio
async def test_known_non_join_pair_is_flagged_not_verified():
    # SAWGraph owl:sameAs -> geoconnex reference IRIs are not materialized (0 rows).
    out = await get_join_strategy("sawgraph", "geoconnex")
    assert out["status"] == "known_non_join"
    assert out["non_joins"]
    assert "diagnosis" in out["non_joins"][0]


@pytest.mark.asyncio
async def test_single_kg_non_join_blocks_any_pairing():
    # maudekg is a profiled island (single-KG known_non_join record): nothing to
    # join, with anything. The bare-"kg" record must block pairing it with prokn.
    out = await get_join_strategy("maudekg", "prokn")
    assert out["status"] == "known_non_join"


@pytest.mark.asyncio
async def test_unknown_pair_routes_to_find_crosswalks():
    # hydrologykg (water/geospatial) and prokn (protein/disease) are both
    # materialized but share no precomputed crosswalk and neither is an island,
    # so the verdict is "unknown" -> go discover a key live.
    out = await get_join_strategy("hydrologykg", "prokn")
    assert out["status"] == "unknown"
    assert "find_crosswalks" in out["note"]


@pytest.mark.asyncio
async def test_single_kg_listing_returns_all_its_joins():
    out = await get_join_strategy("spoke-okn")
    assert "status" not in out  # listing form, not a pair verdict
    assert out["joins"]
    assert all("spoke-okn" in cw._entry_kgs(j) for j in out["joins"])


@pytest.mark.asyncio
async def test_list_crosswalks_renders_taxon_hub_as_pairwise_rows():
    entries = cw.load_crosswalks()["verified_crosswalks"]
    # every NCBITaxon verified_crosswalk (spokes + the bridged D9) is suppressed
    # from the per-entry rows, replaced by the materialized pairwise rows.
    taxon_entries = [e for e in entries if e.get("shared_key") == "NCBITaxon"]
    assert len(taxon_entries) >= 2

    out = await list_crosswalks()
    rows = out["crosswalks"]
    assert out["count"] == len(rows)
    assert all(row["kgs"] for row in rows)  # every row names KGs

    pairwise = cw.taxon_hub_pairwise()
    taxon_rows = [r for r in rows if r["shared_key"] == "NCBITaxon"]
    # one row per non-zero pair — no single collapsed "hub members" row remains
    assert len(taxon_rows) == len(pairwise) >= 1
    # dropped entries = all NCBITaxon — the id hub joins AND the biohealth
    # label-bridged ones (re-rendered as pairwise) — + bare ubergraph endpoint
    # overlaps (A6/M1); the rest stay 1:1 as rows.
    dropped = [
        e
        for e in entries
        if cw._is_ncbitaxon(e) or cw._is_ubergraph_endpoint_overlap(e)
    ]
    assert len(rows) == (len(entries) - len(dropped)) + len(pairwise)

    members = set(cw.load_crosswalks()["taxon_hub"]["members"])
    for r in taxon_rows:
        assert r["domain"] == "Taxonomy" and r["hub"] == "ubergraph"
        # composed through the hub: bridge sits in the middle of the endpoints
        assert r["bridge_kg"] == "ubergraph"
        assert r["kgs"][1] == "ubergraph" and len(r["kgs"]) == 3
        assert {r["kgs"][0], r["kgs"][2]} <= members
        # id members show exact_id + clade counts; a label-bridged member (e.g.
        # biohealth, no NCBITaxon ids) shows an approximate name-match count instead.
        if r.get("match_type") == "label":
            assert isinstance(r["label_match"], int) and r["label_match"] > 0
            assert isinstance(r["kg_b_taxa"], int)
        else:
            for field in ("exact_id", "clade_a_in_b", "clade_b_in_a"):
                assert isinstance(r[field], int)
            assert any(r[f] > 0 for f in ("exact_id", "clade_a_in_b", "clade_b_in_a"))
        assert "verified_count" not in r  # replaced by the count columns

    # the D9 pair (spoke-genelab/spoke-okn) appears as one of the pairwise rows
    assert any(
        {r["kgs"][0], r["kgs"][2]} == {"spoke-genelab", "spoke-okn"} for r in taxon_rows
    )

    # the clade-membership explanation is surfaced for rendering after the table,
    # and it explains the label-bridged rows (biohealth) too
    assert "taxon_clade_note" in out and "clade" in out["taxon_clade_note"].lower()
    assert "label" in out["taxon_clade_note"].lower()


@pytest.mark.asyncio
async def test_biohealth_label_taxon_pairs_are_verified_joins():
    """biohealth's label-bridged organism overlaps are verified crosswalks, so
    get_join_strategy returns a ready recipe whose join key names the label bridge,
    even though biohealth carries no NCBITaxon id."""
    out = await get_join_strategy("biohealth", "sawgraph")
    assert out["status"] == "verified"
    label = [
        j for j in out["joins"] if j["shared_key"] == "NCBITaxon (biohealth label)"
    ]
    assert label, "no label-bridged taxon recipe surfaced"
    j = label[0]
    assert j["domain"] == "Taxonomy"
    assert j["verified_count"] == 377
    assert "label" in j["key_namespace"].lower()
    assert "COUNT(" in j["skeleton_query"]


@pytest.mark.asyncio
async def test_list_crosswalks_omits_bare_ubergraph_endpoint_rows():
    """ubergraph appears in the listing only as a bridge (middle of kgs), never as a
    bare endpoint — those rows (A6 oard-kg MONDO, M1 biobricks-mesh MeSH) are a KG's
    overlap with the ontology backbone, not a KG-to-KG integration. They stay in the
    table for get_join_strategy."""
    out = await list_crosswalks()
    for r in out["crosswalks"]:
        if "ubergraph" in r["kgs"]:
            # only ever the bridge, sitting between two endpoints
            assert r["bridge_kg"] == "ubergraph" and r["kgs"][1] == "ubergraph"

    # A6 / M1 are gone from the listing but still present in the raw table
    entries = cw.load_crosswalks()["verified_crosswalks"]
    assert any(e["id"].startswith("A6") for e in entries)
    assert any(e["id"].startswith("M1") for e in entries)
    assert all(
        cw._is_ubergraph_endpoint_overlap(e)
        for e in entries
        if e["id"] in ("A6-mondo-expansion", "M1-mesh-ubergraph")
    )


def test_taxon_hub_block_is_well_formed():
    from mcp_okn.server import TAXON_HUB_KGS

    hub = cw.load_crosswalks().get("taxon_hub", {})
    assert hub.get("hub_kg") == "ubergraph"
    members = set(hub.get("members", []))
    # the id/query-source KGs (TAXON_HUB_KGS) are all declared members; the block
    # may also declare label-bridged members (e.g. biohealth) that carry no
    # NCBITaxon ids and so are not query sources.
    assert set(TAXON_HUB_KGS) <= members
    for rec in cw.taxon_hub_pairwise():
        assert rec["kg_a"] in members and rec["kg_b"] in members
        if rec.get("match_type") == "label":
            # oriented label-side-first (the label-bridged KG is kg_a), not sorted
            assert rec["kg_a"] not in TAXON_HUB_KGS
        else:
            assert rec["kg_a"] < rec["kg_b"]


def test_taxon_hub_pair_orients_clade_to_request_order():
    pairs = cw.taxon_hub_pairwise()
    if not pairs:
        pytest.skip("no materialized taxon-hub pairs yet")
    rec = pairs[0]
    a, b = rec["kg_a"], rec["kg_b"]
    forward = cw.taxon_hub_pair(a, b)
    reverse = cw.taxon_hub_pair(b, a)
    assert forward["exact_id"] == reverse["exact_id"] == rec["exact_id"]
    # clade direction is relative to the requested first arg, so it flips on swap
    assert forward["clade_a_in_b"] == rec["clade_a_in_b"] == reverse["clade_b_in_a"]
    assert forward["clade_b_in_a"] == rec["clade_b_in_a"] == reverse["clade_a_in_b"]


@pytest.mark.asyncio
async def test_list_crosswalks_examples_toggle():
    with_ex = await list_crosswalks()  # default include_examples=True
    assert all("example_question" in row for row in with_ex["crosswalks"])
    without_ex = await list_crosswalks(include_examples=False)
    assert all("example_question" not in row for row in without_ex["crosswalks"])


@pytest.mark.asyncio
async def test_list_crosswalks_uses_official_kg_shortnames():
    """Every KG named in the listing must be an official registry shortname (the
    same id `list_kgs`/`describe_kg`/`query` accept), never a table-local alias."""
    official = {k["shortname"] for k in load_snapshot()}
    out = await list_crosswalks()
    used = {kg for row in out["crosswalks"] for kg in row["kgs"]}
    assert used, "no KGs surfaced"
    assert used <= official, f"non-official shortnames: {sorted(used - official)}"
    # The table `id` (e.g. "M2-mesh-spokeokn") embeds non-official KG
    # abbreviations, so it must not appear in the listing.
    assert all("id" not in row for row in out["crosswalks"])


@pytest.mark.asyncio
async def test_list_crosswalks_grouped_by_domain_and_sorted():
    """Rows carry a domain and are sorted by (domain, shared_key) so the listing
    renders as a table grouped by domain. Every shared_key must map to a real
    domain (not the "Other" fallback), so new keys force a mapping update."""
    out = await list_crosswalks()
    rows = out["crosswalks"]
    assert all(r.get("domain") for r in rows)
    assert all(r["domain"] != "Other" for r in rows), "unmapped shared_key domain"
    keys = [(r["domain"], r["shared_key"] or "", r["kgs"]) for r in rows]
    assert keys == sorted(keys), "rows not sorted by (domain, shared_key, kgs)"


@pytest.mark.asyncio
async def test_list_crosswalks_orders_bridge_in_the_middle():
    """For a bridged join the bridge KG sits between the two endpoints, not at an
    alphabetical end (e.g. oard-kg → ubergraph → prokn, not → prokn → ubergraph)."""
    out = await list_crosswalks()
    bridged = [r for r in out["crosswalks"] if r["bridge_kg"]]
    assert bridged, "expected at least one bridged crosswalk"
    for r in bridged:
        kgs = r["kgs"]
        assert kgs[1] == r["bridge_kg"], (r["bridge_kg"], kgs)
        assert len(kgs) == 3


@pytest.mark.asyncio
async def test_list_crosswalks_carries_verified_date():
    out = await list_crosswalks()
    assert out["verified_on"] == cw.verified_on()
    assert out["verified_on"] is not None


@pytest.mark.asyncio
async def test_get_join_strategy_joins_carry_domain_and_group():
    """Joins carry a domain and a multi-join listing is grouped by domain (sorted
    by (domain, shared_key)), consistent with list_crosswalks."""
    listing = await get_join_strategy("spoke-okn")  # touches many domains
    joins = listing["joins"]
    assert len(joins) > 1
    assert all(j.get("domain") and j["domain"] != "Other" for j in joins)
    keys = [(j["domain"], j["shared_key"] or "", j.get("id") or "") for j in joins]
    assert keys == sorted(keys), "single-KG joins not grouped by domain"
    pair = await get_join_strategy("oard-kg", "prokn")
    assert all("domain" in j for j in pair["joins"])


@pytest.mark.asyncio
async def test_get_join_strategy_returns_skeleton_not_recipe():
    """The retrieval tool guides queries with the runnable skeleton_query and
    omits the prose iri_normalization recipe (the skeleton encodes it)."""
    out = await get_join_strategy("biobricks-aopwiki", "biobricks-toxcast")
    assert out["status"] == "verified"
    j = out["joins"][0]
    assert "skeleton_query" in j and "COUNT(" in j["skeleton_query"]
    assert "iri_normalization" not in j
    # The single-KG listing form drops the recipe too.
    listing = await get_join_strategy("biobricks-aopwiki")
    assert all("iri_normalization" not in e for e in listing["joins"])
    assert any("skeleton_query" in e for e in listing["joins"])


def test_complementary_note_fires_only_for_two_tagged_linkages():
    assert _complementary_note([]) is None
    assert (
        _complementary_note([{"shared_key": "MONDO", "complementary_note": "x"}])
        is None
    )
    # An untagged second linkage (e.g. HP phenotypes) must not trigger it.
    assert (
        _complementary_note(
            [{"shared_key": "MONDO", "complementary_note": "x"}, {"shared_key": "HP"}]
        )
        is None
    )
    note = _complementary_note(
        [
            {"shared_key": "MONDO", "complementary_note": "direct"},
            {"shared_key": "MONDO<->OMIM (bridged)", "complementary_note": "bridge"},
        ]
    )
    assert note is not None
    assert "COMPLEMENTARY" in note and "UNION" in note
    assert "MONDO" in note and "OMIM" in note


@pytest.mark.asyncio
async def test_oardkg_prokn_disease_linkages_flagged_complementary():
    """oard-kg↔prokn has a direct MONDO join AND an OMIM-via-ubergraph bridge that
    reach distinct disease sets; the pair result must flag them as complementary
    and each carry its own complementary_note (the cross-link)."""
    out = await get_join_strategy("oard-kg", "prokn")
    assert out["status"] == "verified"
    assert "COMPLEMENTARY" in out["note"] and "UNION" in out["note"]
    tagged = {
        j["shared_key"]: j["complementary_note"]
        for j in out["joins"]
        if j.get("complementary_note")
    }
    assert "MONDO" in tagged
    assert any("OMIM" in k for k in tagged)
    # Each tagged recipe names the other path, so the link is navigable.
    assert "OMIM" in tagged["MONDO"]


def test_island_status_for_island_kg():
    assert cw.island_status("maudekg") is not None
    assert cw.island_status("maudekg")["island"] is True
    assert cw.island_status("prokn") is None  # not an island


def test_thin_thread_kg_surfaces_threads_without_being_an_island():
    status = cw.island_status("ruralkg")
    assert status is not None
    assert status["island"] is False
    assert status["thin_threads"]


def test_skeleton_queries_are_well_formed():
    """Every bundled skeleton_query must be a runnable COUNT join that scopes the
    entry's KGs with named GRAPH blocks, and carry honest verification metadata."""
    data = cw.load_crosswalks()
    skeletons = [e for e in data["verified_crosswalks"] if e.get("skeleton_query")]
    assert len(skeletons) >= 50, f"only {len(skeletons)} skeletons; expected most of 61"
    for e in skeletons:
        q = e["skeleton_query"]
        assert "SELECT" in q and "COUNT(" in q, e["id"]
        # The endpoints it joins must each appear as a scoped named graph.
        for kg in cw._entry_kgs(e):
            if kg in (
                "ubergraph",
                "wikidata",
            ):  # bridges aren't always GRAPH-scoped by id
                continue
            assert f"/kg/{kg}>" in q, f"{e['id']} skeleton omits graph {kg}"
        assert e.get("skeleton_verified") in (True, False), e["id"]
        # Near-misses must disclose what they actually returned.
        if e["skeleton_verified"] is False:
            assert "skeleton_returns" in e, e["id"]


def test_every_referenced_kg_exists_in_the_registry_snapshot():
    """Guard future edits to the table: no recipe may name a KG the server can't
    serve (bridges ubergraph/wikidata included)."""
    known = {k["shortname"] for k in load_snapshot()}
    data = cw.load_crosswalks()
    referenced: set[str] = set()
    for e in data.get("verified_crosswalks", []):
        referenced |= cw._entry_kgs(e)
    assert referenced <= known, f"unknown KGs in table: {sorted(referenced - known)}"


def test_bundled_table_matches_metadata_source(tmp_path):
    """The packaged copy must stay in sync with the editable source of record."""
    import pathlib

    repo = pathlib.Path(__file__).resolve().parent.parent
    source = repo / "metadata" / "crosswalks.json"
    if not source.exists():
        pytest.skip("metadata source not present in this checkout")
    assert json.loads(source.read_text()) == cw.load_crosswalks()


def test_inventory_doc_matches_generator():
    """docs/crosswalks/proto-okn-crosswalk-inventory.md is generated from the
    crosswalk table — guard that it hasn't drifted (regenerate with
    scripts/build_crosswalk_inventory.py)."""
    import importlib.util
    import pathlib

    repo = pathlib.Path(__file__).resolve().parent.parent
    doc = repo / "docs" / "crosswalks" / "proto-okn-crosswalk-inventory.md"
    gen = repo / "scripts" / "build_crosswalk_inventory.py"
    if not doc.exists() or not gen.exists():
        pytest.skip("inventory doc or generator not present in this checkout")
    spec = importlib.util.spec_from_file_location("_inv_gen", gen)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert doc.read_text(encoding="utf-8") == mod.render(), (
        "inventory doc is stale — run scripts/build_crosswalk_inventory.py"
    )


def test_user_facing_crosswalk_count_is_canonical():
    """Every user-facing doc must cite len(all_crosswalks()) as THE crosswalk
    count — the single number list_crosswalks returns. Guards against the
    133-vs-134 drift where docs hardcoded a stale count (or the internal
    verified_crosswalks array length). Add/remove a crosswalk → update these
    docs or this fails."""
    import pathlib
    import re

    repo = pathlib.Path(__file__).resolve().parent.parent
    n = len(cw.all_crosswalks(include_examples=False))
    checks = [
        ("README.md", r"all (\d+) crosswalks across \d+ graphs"),
        ("docs/crosswalks/crosswalks_example.md", r"\((\d+) hand-verified crosswalks"),
        (
            "docs/crosswalks/proto-okn-crosswalk-inventory.md",
            r"Here are all (\d+) precomputed cross-KG crosswalks",
        ),
    ]
    for rel, pat in checks:
        path = repo / rel
        if not path.exists():
            pytest.skip(f"{rel} not present in this checkout")
        m = re.search(pat, path.read_text(encoding="utf-8"))
        assert m, f"{rel}: canonical crosswalk-count phrase not found (pattern {pat!r})"
        assert int(m.group(1)) == n, (
            f"{rel} cites {m.group(1)} crosswalks; canonical len(all_crosswalks()) is {n}"
        )


def test_example_question_count_matches_files():
    """README's '**N example questions**' must equal the actual transcript
    count in docs/crosswalks/crosswalks_examples/ (one .md per question)."""
    import pathlib
    import re

    repo = pathlib.Path(__file__).resolve().parent.parent
    examples = repo / "docs" / "crosswalks" / "crosswalks_examples"
    readme = repo / "README.md"
    if not examples.exists() or not readme.exists():
        pytest.skip("examples dir or README not present in this checkout")
    n_files = len(list(examples.glob("*.md")))
    m = re.search(
        r"\*\*(\d+) example questions\*\*", readme.read_text(encoding="utf-8")
    )
    assert m, "README: '**N example questions**' phrase not found"
    assert int(m.group(1)) == n_files, (
        f"README cites {m.group(1)} example questions; {n_files} transcript files exist"
    )

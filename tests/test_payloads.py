import mcp_okn.payloads as pay
from mcp_okn.registry import load_snapshot
from mcp_okn.server import find_context_sources, list_kgs


def _servable_shortnames() -> set[str]:
    return {k["shortname"] for k in load_snapshot()}


def test_table_loads_and_is_dated():
    data = pay.load_payloads()
    assert isinstance(data, dict)
    assert data.get("payloads")
    assert pay.verified_on()  # a YYYY-MM-DD stamp for staleness visibility


def test_every_tag_is_in_the_vocabulary():
    vocab = set(pay.vocabulary())
    assert vocab
    bad = {
        (sn, t)
        for sn, tags in pay.load_payloads()["payloads"].items()
        for t in tags
        if t not in vocab
    }
    assert not bad, f"payload tags not in vocabulary: {sorted(bad)}"


def test_no_unused_vocabulary_terms():
    used = {t for tags in pay.load_payloads()["payloads"].values() for t in tags}
    assert set(pay.vocabulary()) == used


def test_every_servable_kg_has_a_payload_and_no_phantoms():
    servable = _servable_shortnames()
    tagged = set(pay.load_payloads()["payloads"])
    assert tagged - servable == set(), "payload table names unknown KGs"
    assert servable - tagged == set(), "servable KGs missing a payload entry"


def test_payloads_for_and_kgs_with_payload_are_consistent():
    assert "gene_set" in pay.payloads_for("digcfdekg")
    assert "digcfdekg" in pay.kgs_with_payload("gene_set")
    assert pay.payloads_for("does-not-exist") == []
    assert pay.is_known_type("GO")
    assert not pay.is_known_type("not-a-type")


async def test_list_kgs_carries_payload_field():
    kgs = await list_kgs()
    assert all("payload" in k for k in kgs)
    dig = next(k for k in kgs if k["shortname"] == "digcfdekg")
    assert dig["payload"] == pay.payloads_for("digcfdekg")
    assert "gene_set" in dig["payload"]


async def test_find_context_sources_surfaces_suppliers_by_size():
    out = await find_context_sources(
        want=["GO", "pathway", "gene_set", "trait"], join_key="Entrez"
    )
    assert out["join_key"] == "Entrez"
    assert set(out["sources"]) == {"GO", "pathway", "gene_set", "trait"}

    # prokn supplies GO/pathway and joins on Entrez (via the HGNC bridge).
    go_kgs = [s["kg"] for s in out["sources"]["GO"]]
    assert "prokn" in go_kgs
    # digcfdekg is the gene_set / trait supplier joinable on Entrez.
    assert "digcfdekg" in [s["kg"] for s in out["sources"]["gene_set"]]
    assert "digcfdekg" in [s["kg"] for s in out["sources"]["trait"]]

    # Each source carries the join predicate + key + size, biggest first.
    prokn = next(s for s in out["sources"]["GO"] if s["kg"] == "prokn")
    assert prokn["joins"]
    sizes = [j.get("size") or 0 for j in prokn["joins"]]
    assert sizes == sorted(sizes, reverse=True)
    assert all({"shared_key", "predicate", "size"} <= set(j) for j in prokn["joins"])


async def test_find_context_sources_payload_only_bucket():
    # pankgraph supplies GO but keys genes on Ensembl, not Entrez -> not hidden,
    # surfaced under payload_only so the agent knows to convert the id.
    out = await find_context_sources(want=["GO"], join_key="Entrez")
    assert "pankgraph" not in [s["kg"] for s in out["sources"]["GO"]]
    assert "pankgraph" in out["payload_only"].get("GO", [])


async def test_find_context_sources_empty_list_is_evidence_of_absence():
    # A known type that no KG supplies on this key yields an empty (present) list.
    out = await find_context_sources(want=["software"], join_key="MONDO")
    assert out["sources"]["software"] == []


async def test_find_context_sources_flags_unknown_types():
    out = await find_context_sources(want=["GO", "not-a-real-type"])
    assert out["want"] == ["GO"]
    assert out["unmatched_want"] == ["not-a-real-type"]
    assert "vocabulary" in out


async def test_find_context_sources_without_join_key_lists_all_keys():
    out = await find_context_sources(want=["trait"])
    assert out["join_key"] is None
    assert not out["payload_only"]  # no key filter -> nothing excluded
    dig = next(s for s in out["sources"]["trait"] if s["kg"] == "digcfdekg")
    assert {j["shared_key"] for j in dig["joins"]}  # every key it joins on

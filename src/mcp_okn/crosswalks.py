"""Precomputed, hand-verified cross-KG join recipes for the FRINK federation.

`find_crosswalks` discovers join keys LIVE — it fires federation scans that time
out on large graphs, so it is unreliable. This module instead serves a curated
static table (``data/crosswalks.json``) of join recipes that were verified with
exact ``COUNT(DISTINCT)`` over the named graphs on a known date. For a KG pair it
answers one of three states:

  * ``verified``  — here is the ready join recipe (predicates, roles, shared key,
    IRI-normalization snippet, bridge, verified count);
  * ``known_non_join`` — this pair was checked and does NOT join on the obvious
    key; don't waste a query, here's why;
  * ``unknown`` — nothing precomputed; fall back to `find_crosswalks`.

The file's own consumer contract: keyed by a KG shortname, surface every entry
where it appears as ``left_kg``, ``right_kg``, ``bridge_kg``, or in a ``members``
clique.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

# Process-lifetime cache (the table is static and changes rarely).
_data_cache: dict[str, Any] | None = None


def load_crosswalks() -> dict[str, Any]:
    """Load the bundled static crosswalk table.

    Returns an empty dict if the file is missing or unreadable, so callers
    degrade to the live `find_crosswalks` path instead of erroring.
    """
    global _data_cache
    if _data_cache is not None:
        return _data_cache
    try:
        text = (resources.files("mcp_okn") / "data" / "crosswalks.json").read_text(
            encoding="utf-8"
        )
        data = json.loads(text)
        _data_cache = data if isinstance(data, dict) else {}
    except (FileNotFoundError, ModuleNotFoundError, json.JSONDecodeError, OSError):
        _data_cache = {}
    return _data_cache


def _entry_kgs(entry: dict[str, Any]) -> set[str]:
    """Every KG shortname an entry touches (left/right/bridge + members)."""
    kgs: set[str] = set()
    for key in ("left_kg", "right_kg", "bridge_kg"):
        if entry.get(key):
            kgs.add(entry[key])
    kgs.update(entry.get("members", []))
    return kgs


def _nonjoin_kgs(entry: dict[str, Any]) -> set[str]:
    """Every KG shortname a known-non-join record references."""
    kgs: set[str] = set()
    for key in ("left_kg", "right_kg", "kg"):
        if entry.get(key):
            kgs.add(entry[key])
    return kgs


# The prose recipe is dropped from query-facing output in favour of the runnable
# skeleton_query, which encodes the same IRI-normalization executably.
_RECIPE_ONLY_FIELDS = ("iri_normalization",)


def for_query(entry: dict[str, Any]) -> dict[str, Any]:
    """Project a verified crosswalk for query guidance.

    Returns a copy with the prose recipe (``iri_normalization``) removed: the
    bundled ``skeleton_query`` is a verified, runnable example that already
    encodes the same normalization, so it — not the prose — is what guides a
    caller writing SPARQL. A ``domain`` field is added (see :func:`domain_for`)
    so a multi-join listing groups consistently with ``list_crosswalks``.
    """
    out = {k: v for k, v in entry.items() if k not in _RECIPE_ONLY_FIELDS}
    out["domain"] = domain_of(entry)
    return out


def _listing_sort_key(row: dict[str, Any]) -> tuple[str, str, str]:
    """Sort joins by (domain, shared_key, id) so a listing groups by domain."""
    return (row.get("domain", ""), row.get("shared_key") or "", row.get("id") or "")


def verified_for(shortname: str) -> list[dict[str, Any]]:
    """All verified join entries that touch ``shortname`` (any role).

    Grouped by domain (sorted by ``(domain, shared_key)``).
    """
    data = load_crosswalks()
    out = [
        for_query(e)
        for e in data.get("verified_crosswalks", [])
        if shortname in _entry_kgs(e)
    ]
    out.sort(key=_listing_sort_key)
    return out


def _ordered_kgs(entry: dict[str, Any]) -> list[str]:
    """KGs of an entry in join order: left → bridge → right.

    The bridge graph (e.g. ``ubergraph``) sits in the MIDDLE — it is what the two
    endpoints meet through — so a plain alphabetical sort would misleadingly push
    it to one end. Clique entries (``members``, no left/right) keep sorted order.
    """
    if entry.get("members"):
        return sorted(entry["members"])
    ordered = [entry.get("left_kg"), entry.get("bridge_kg"), entry.get("right_kg")]
    return [kg for kg in ordered if kg]


# Group each crosswalk into a domain by its shared identifier, so the listing
# renders as a table organised by domain. Keep this in sync with the table's
# shared_key vocabulary (a test asserts every key is mapped).
_DOMAIN_BY_SHARED_KEY: dict[str, str] = {
    "DOID": "Disease & phenotype",
    "MONDO": "Disease & phenotype",
    "HP": "Disease & phenotype",
    "DOID<->MONDO": "Disease & phenotype",
    "MONDO<->OMIM (bridged)": "Disease & phenotype",
    "MONDO<->Orphanet (bridged)": "Disease & phenotype",
    "MONDO<->DOID (bridged)": "Disease & phenotype",
    "EFO<->MONDO (bridged)": "Disease & phenotype",
    "MeSH_descriptor_id": "Disease & phenotype",
    "UMLS<->MONDO": "Disease & phenotype",
    "UMLS<->HP": "Disease & phenotype",
    "UMLS<->MONDO<->DOID (two-hop)": "Disease & phenotype",
    "UMLS<->UBERON": "Anatomy & Cell Type",
    "UBERON": "Anatomy & Cell Type",
    "CL": "Anatomy & Cell Type",
    "Ensembl": "Genes",
    "Entrez": "Genes",
    "HGNC -> Entrez (bridged)": "Genes",
    "UniProt": "Proteins",
    "CAS": "Chemicals",
    "CHEBI<->CAS": "Chemicals",
    "PubChem CID": "Chemicals",
    "DrugBank": "Chemicals",
    "NCBITaxon": "Taxonomy",
    "NCBITaxon (biohealth label)": "Taxonomy",
    "S2_L13": "Geospatial",
    "county_FIPS": "Geospatial",
    "state_FIPS": "Geospatial",
    "KWG_county": "Geospatial",
    "ZIP5": "Geospatial",
    "NAICS": "Industry & supply chain",
    "SUDOKN_industry_sector": "Industry & supply chain",
    "GO": "Function & Pathways",
    "Reactome": "Function & Pathways",
    # digcfdekg multi-vocabulary disease joins (verbose composite keys)
    "DOID<->MONDO (+ EFO/Orphanet -> MONDO)": "Disease & phenotype",
    "MONDO (+ EFO/Orphanet -> MONDO bridged)": "Disease & phenotype",
    "EFO / Orphanet / MONDO (direct, multi-vocabulary)": "Disease & phenotype",
    "Entrez -> HGNC (bridged)": "Genes",
}

# Canonical spelling for explicit per-row ``domain`` values that vary only by
# case/wording, so they don't fragment a domain into near-duplicates.
_DOMAIN_ALIASES: dict[str, str] = {
    "Anatomy & cell type": "Anatomy & Cell Type",
}


def domain_for(shared_key: str | None) -> str:
    """The domain a crosswalk belongs to, keyed by its shared identifier."""
    return _DOMAIN_BY_SHARED_KEY.get(shared_key or "", "Other")


def domain_of(entry: dict[str, Any]) -> str:
    """Domain for a crosswalk entry.

    Prefers the entry's own curated ``domain`` field (normalized for casing) —
    needed when the shared key alone is ambiguous, e.g. a ``CAS`` join tagged
    "Environmental toxicology" vs the generic Chemicals default. Falls back to
    the shared-key map when no explicit domain is set.
    """
    explicit: str | None = entry.get("domain")
    if explicit:
        return _DOMAIN_ALIASES.get(explicit, explicit)
    return domain_for(entry.get("shared_key"))


def _is_ncbitaxon(entry: dict[str, Any]) -> bool:
    """True for any NCBITaxon crosswalk.

    Covers the id hub joins AND the biohealth label-bridged ones
    (``shared_key`` ``"NCBITaxon (biohealth label)"``).

    Both are re-rendered in :func:`all_crosswalks` from the materialized
    ``taxon_hub.pairwise`` set (one row per pair), so a single predicate keyed on
    the ``NCBITaxon`` prefix suppresses every per-entry taxon row from the listing.
    """
    return (entry.get("shared_key") or "").startswith("NCBITaxon")


def _is_taxon_hub_spoke(entry: dict[str, Any]) -> bool:
    """True for a KG↔ubergraph NCBITaxon *spoke*.

    Collapsed into a single hub row by :func:`all_crosswalks` so the listing
    speaks in integration terms, not in each KG's (uninteresting) overlap with
    the ubergraph hub.

    A pairwise taxon crosswalk that merely *bridges through* ubergraph (ubergraph
    is the ``bridge_kg``, e.g. spoke-genelab↔spoke-okn / D9) is NOT a spoke: it is a
    real KG-to-KG integration point and keeps its own row.
    """
    return (
        entry.get("shared_key") == "NCBITaxon"
        and not entry.get("bridge_kg")
        and "ubergraph" in (entry.get("left_kg"), entry.get("right_kg"))
    )


def _is_ubergraph_endpoint_overlap(entry: dict[str, Any]) -> bool:
    """True when ``ubergraph`` is a bare ENDPOINT of the entry (no ``bridge_kg``).

    Such a row records a KG's overlap with the ontology BACKBONE — e.g. A6
    (oard-kg's MONDO terms present in ubergraph) or M1 (biobricks-mesh's MeSH
    descriptors in ubergraph) — not a KG-to-KG integration. ubergraph carries no
    data of its own; a join "to ubergraph" is always ontology expansion or a bridge
    half, so these are suppressed from :func:`all_crosswalks` (the listing of
    integration points). They remain in the table, so ``get_join_strategy`` and
    inline ``subClassOf*`` category expansion still use them. The NCBITaxon spokes
    are this shape too but are handled separately (rendered as pairwise rows).
    """
    return not entry.get("bridge_kg") and "ubergraph" in (
        entry.get("left_kg"),
        entry.get("right_kg"),
    )


def all_crosswalks(include_examples: bool = True) -> list[dict[str, Any]]:
    """Compact summary of every verified cross-KG integration point.

    One row per verified crosswalk: its ``domain`` (e.g. "Genes", "Geospatial"),
    the KGs it connects in join order (left → bridge → right, by official registry
    shortname), the shared identifier, the bridge KG if any, and the verified row
    count. ``example_question`` is included unless ``include_examples`` is False.

    The NCBITaxon crosswalks are a HUB (each KG joins ``ubergraph``), but a user
    cares about pairwise integration, not each KG's overlap with the ubergraph
    plumbing. So ALL NCBITaxon entries (the per-KG ``KG↔ubergraph`` spokes and the
    bridged pairwise ones like D9) are dropped and re-rendered as ONE row PER
    non-zero pair from the materialized hub set: ``kgs: [kg_a, "ubergraph", kg_b]``,
    ``bridge_kg: "ubergraph"``, ``hub: "ubergraph"``, and the two-valued counts
    ``exact_id`` plus directional ``clade_a_in_b``/``clade_b_in_a`` (no single
    ``verified_count``). ``taxon_overlap(kg_a, kg_b)`` returns the runnable skeleton.

    Likewise dropped are rows where ``ubergraph`` is a bare ENDPOINT (no bridge) —
    e.g. A6 (oard-kg MONDO) and M1 (biobricks-mesh MeSH): they record a KG's overlap
    with the ontology backbone, not a KG-to-KG integration (see
    :func:`_is_ubergraph_endpoint_overlap`). All these entries are untouched in the
    table and still served by ``get_join_strategy`` / ``verified_for``; only this
    listing suppresses them.

    Rows are sorted by ``(domain, shared_key, kgs)`` so the result reads as a
    table grouped by domain and ordered by ontology within each — ready to render
    directly.

    The internal table ``id`` is deliberately omitted: it embeds KG abbreviations
    (e.g. ``M2-mesh-spokeokn``) that are NOT official shortnames, so a listing
    keyed on it would misname KGs. Callers identify a crosswalk by its ``kgs``
    (official shortnames) and ``shared_key``.
    """
    rows: list[dict[str, Any]] = []
    for e in load_crosswalks().get("verified_crosswalks", []):
        # Every NCBITaxon crosswalk (KG↔ubergraph spokes, the bridged pairwise ones
        # like D9, AND the biohealth label-bridged ones) is rendered instead from
        # the materialized hub pairwise set below, so the listing shows verified
        # PER-PAIR counts, not each KG's (uninteresting) overlap with the ubergraph
        # plumbing — and the new label entries don't duplicate their pairwise rows.
        if _is_ncbitaxon(e):
            continue
        # Drop rows where ubergraph is a bare endpoint (A6 MONDO, M1 MeSH): a KG's
        # overlap with the ontology backbone, not a KG-to-KG integration point.
        if _is_ubergraph_endpoint_overlap(e):
            continue
        row = {
            "domain": domain_of(e),
            "kgs": _ordered_kgs(e),
            "shared_key": e.get("shared_key"),
            "bridge_kg": e.get("bridge_kg"),
            "verified_count": e.get("verified_count"),
        }
        if include_examples:
            row["example_question"] = e.get("example_question")
        rows.append(row)

    # One row per materialized non-zero pair. These are hub joins composed THROUGH
    # ubergraph, so the bridge sits in the middle (kgs = [a, ubergraph, b]) and the
    # count is two-valued: exact_id (same NCBITaxon id, symmetric) plus the two
    # directional clade-membership counts. See TAXON_CLADE_NOTE.
    hub_verified_on = taxon_hub_verified_on()
    for rec in taxon_hub_pairwise():
        a, b = rec["kg_a"], rec["kg_b"]
        row = {
            "domain": domain_for("NCBITaxon"),
            "kgs": [a, "ubergraph", b],
            "shared_key": "NCBITaxon",
            "bridge_kg": "ubergraph",
            "hub": "ubergraph",
            "verified_on": hub_verified_on,
        }
        if rec.get("match_type") == "label":
            # A label-bridged member (e.g. biohealth) carries no NCBITaxon ids, so
            # its organisms are matched to the other side by scientific name only:
            # an approximate, conservative lower bound with no clade expansion.
            row["match_type"] = "label"
            row["label_match"] = rec["label_match"]
            row["kg_b_taxa"] = rec["kg_b_taxa"]
            if include_examples:
                row["example_question"] = (
                    f"How many organisms do {a} and {b} share by name? {a} is "
                    f"label-bridged (no NCBITaxon ids), so {rec['label_match']} of "
                    f"{b}'s {rec['kg_b_taxa']} NCBITaxon organisms match a {a} "
                    "concept by exact scientific name (approximate lower bound; no "
                    "clade expansion)."
                )
        else:
            row["match_type"] = "id"
            row["exact_id"] = rec["exact_id"]
            row["clade_a_in_b"] = rec["clade_a_in_b"]
            row["clade_b_in_a"] = rec["clade_b_in_a"]
            if include_examples:
                row["example_question"] = (
                    f"How many organisms do {a} and {b} share? exact_id="
                    f"{rec['exact_id']} carry the identical NCBITaxon id; clade "
                    f"membership ({rec['clade_a_in_b']} / {rec['clade_b_in_a']}) "
                    "expands through the ubergraph hierarchy."
                )
        rows.append(row)

    rows.sort(key=lambda r: (r["domain"], r["shared_key"] or "", r["kgs"]))
    return rows


def join_between(kg_a: str, kg_b: str) -> list[dict[str, Any]]:
    """Verified entries that connect ``kg_a`` and ``kg_b`` (order-insensitive).

    A bridged entry counts as connecting the two endpoints even when one of them
    is named only as the ``bridge_kg``.
    """
    out: list[dict[str, Any]] = []
    for e in load_crosswalks().get("verified_crosswalks", []):
        kgs = _entry_kgs(e)
        if kg_a in kgs and kg_b in kgs:
            out.append(for_query(e))
    out.sort(key=_listing_sort_key)
    return out


def nonjoin_for(shortname: str) -> list[dict[str, Any]]:
    """Known-non-join records that reference ``shortname``."""
    data = load_crosswalks()
    return [e for e in data.get("known_non_joins", []) if shortname in _nonjoin_kgs(e)]


def nonjoin_between(kg_a: str, kg_b: str) -> list[dict[str, Any]]:
    """Known-non-join records that reference BOTH KGs (order-insensitive).

    Single-KG records (an unmaterialized / schema-only graph) are returned when
    either endpoint is that KG, since they explain why no join is possible.
    """
    out: list[dict[str, Any]] = []
    for e in load_crosswalks().get("known_non_joins", []):
        kgs = _nonjoin_kgs(e)
        if {kg_a, kg_b} <= kgs or ("kg" in e and e["kg"] in (kg_a, kg_b)):
            out.append(e)
    return out


def island_status(shortname: str) -> dict[str, Any] | None:
    """Island / thin-thread context for ``shortname``, or None if neither.

    Returns ``{"island": bool, "thin_threads": [...], "note": ...}`` when the KG
    is a profiled island or has documented thin threads, so a caller can warn
    that public join keys are scarce.
    """
    islands = load_crosswalks().get("islands", {})
    is_island = shortname in islands.get("kgs", [])
    threads = [t for t in islands.get("thin_threads", []) if t.startswith(shortname)]
    if not is_island and not threads:
        return None
    return {
        "island": is_island,
        "thin_threads": threads,
        "note": islands.get("note"),
    }


def verified_on() -> str | None:
    """The date the table's counts were verified, for staleness visibility."""
    return load_crosswalks().get("verified_on")


#: Explanation rendered AFTER the list_crosswalks table for the Taxonomy rows,
#: which carry two materialized counts instead of a single verified_count.
TAXON_CLADE_NOTE = (
    "Taxonomy (NCBITaxon) rows are pairwise organism overlaps composed THROUGH the "
    "ubergraph hub, so each carries two materialized counts rather than one "
    "verified_count. exact_id = taxa with the IDENTICAL NCBITaxon id on both sides "
    "(symmetric). clade_a_in_b / clade_b_in_a = how many of the first / second KG's "
    "taxa fall UNDER the other KG's taxa once expanded through ubergraph's "
    "rdfs:subClassOf* hierarchy (directional, hence two numbers). Clade membership "
    "is the more complete biological overlap and is often far larger than exact_id "
    "when one KG records coarser taxa (e.g. genus) and the other finer ones (e.g. "
    "strain) — e.g. spoke-genelab × spoke-okn is exact_id 2 but 33,313 by clade. "
    "Some rows are LABEL-BRIDGED instead (match_type 'label'): biohealth carries no "
    "NCBITaxon id, so its organisms are matched to the other KG by exact scientific "
    "name (biohealth rdfs:label -> ubergraph NCBITaxon rdfs:label). These rows carry "
    "label_match / kg_b_taxa rather than exact_id/clade — render them as 'label "
    "match: <label_match> of <kg_b_taxa> organisms by name' (an approximate lower "
    "bound; misses synonyms/spelling variants, no clade expansion). "
    "Only non-zero pairs are listed; call taxon_overlap(kg_a, kg_b) for the runnable "
    "skeletons."
)


def taxon_hub_pairwise() -> list[dict[str, Any]]:
    """Materialized pairwise NCBITaxon overlaps between hub members.

    Each record is ``{kg_a, kg_b, exact_id, clade_a_in_b, clade_b_in_a}`` for a
    non-zero pair (zero-overlap pairs are omitted). ``kg_a``/``kg_b`` are sorted;
    ``clade_a_in_b`` counts ``kg_a``'s taxa nested under ``kg_b``'s clades, and
    ``clade_b_in_a`` the reverse. Populated by
    ``scripts/refresh_taxon_overlaps.py``; ``[]`` if absent.
    """
    hub = load_crosswalks().get("taxon_hub", {})
    return hub.get("pairwise", []) if isinstance(hub, dict) else []


def taxon_hub_verified_on() -> str | None:
    """The date the materialized taxon-hub pairwise counts were verified."""
    hub = load_crosswalks().get("taxon_hub", {})
    return hub.get("verified_on") if isinstance(hub, dict) else None


def taxon_hub_pair(kg_a: str, kg_b: str) -> dict[str, Any] | None:
    """The materialized overlap for ``{kg_a, kg_b}``, oriented so ``a`` == ``kg_a``.

    Returns None when the pair has no non-zero materialized overlap. The stored
    records are keyed on a sorted pair; when the request order is reversed the
    directional clade counts are swapped so ``clade_a_in_b`` always means
    ``kg_a``-in-``kg_b``.
    """
    for rec in taxon_hub_pairwise():
        ra, rb = rec.get("kg_a"), rec.get("kg_b")
        if {ra, rb} != {kg_a, kg_b}:
            continue
        if ra == kg_a:
            return dict(rec)
        if rec.get("match_type") == "label":
            # label_match counts shared organisms by name (not directional like the
            # clade counts), so reorienting only swaps the kg labels.
            return {
                "kg_a": kg_a,
                "kg_b": kg_b,
                "match_type": "label",
                "label_match": rec.get("label_match"),
                "kg_b_taxa": rec.get("kg_b_taxa"),
            }
        return {
            "kg_a": kg_a,
            "kg_b": kg_b,
            "exact_id": rec.get("exact_id"),
            "clade_a_in_b": rec.get("clade_b_in_a"),
            "clade_b_in_a": rec.get("clade_a_in_b"),
        }
    return None

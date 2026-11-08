"""Cross-KG join tools.

get_join_strategy, taxon_overlap, list_crosswalks, find_context_sources.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import crosswalks as crosswalk_table
from .. import payloads as payload_table
from .. import taxon as taxon_hub
from ..app import mcp
from ..budget import REPLY_CHAR_BUDGET, cap_items, reply_size
from ..taxon import TAXON_HUB_KGS


def _complementary_note(joins: list[dict[str, Any]]) -> str | None:
    """Flag when a pair has 2+ COMPLEMENTARY linkages.

    These are recipes that link the same entity through different identifier
    systems (e.g. oard-kg↔prokn diseases via direct MONDO AND via the
    OMIM→ubergraph bridge) and so reach overlapping but DISTINCT sets. Presented
    side by side they read as alternatives, and an agent picks one and
    undercounts; this says to UNION them. Driven by the curated
    ``complementary_note`` tag on each recipe (a coarse same-domain heuristic
    would wrongly lump phenotypes in with diseases). None when fewer than two
    tagged linkages are present.
    """
    tagged = [j for j in joins if j.get("complementary_note")]
    if len(tagged) < 2:
        return None
    keys = ", ".join(dict.fromkeys(j.get("shared_key") or "?" for j in tagged))
    return (
        f"{len(tagged)} of these linkages are COMPLEMENTARY ({keys}): they link "
        "the same entity through different identifiers and reach overlapping but "
        "DISTINCT sets, so a complete answer UNIONs them — do not pick just one. "
        "See each recipe's `complementary_note` for what each path uniquely adds."
    )


#: Fields an index row keeps: enough to pick a partner, not to run the join.
_INDEX_FIELDS = (
    "id",
    "domain",
    "left_kg",
    "bridge_kg",
    "right_kg",
    "shared_key",
    "verified_count",
)


def _join_index(full: dict[str, Any]) -> dict[str, Any]:
    """Shrink a single-KG listing to one line per join when it is too big to send.

    Hub KGs list dozens of recipes (ubergraph's full listing is ~235K characters),
    and a reply that size reaches the agent as a spilled file, not data. The index
    keeps every join's partners, key and count. The recipe and skeleton for a pair
    are one ``get_join_strategy(kg_a, kg_b)`` call away.
    """
    out = dict(full)
    out["detail"] = "index"
    out["joins"] = [
        {k: j.get(k) for k in _INDEX_FIELDS if j.get(k) is not None}
        for j in full["joins"]
    ]
    out["known_non_joins"] = [
        {
            k: n.get(k)
            for k in ("left_kg", "right_kg", "attempted_key", "result")
            if n.get(k) is not None
        }
        for n in full.get("known_non_joins") or []
    ]
    total = len(out["joins"])
    out["note"] = (
        f"{total} verified joins touch {full['shortname']!r}, too many to send with "
        "their recipes, so this is an index. Call get_join_strategy(kg_a, kg_b) for "
        "a pair's predicates, roles and runnable skeleton_query."
    )
    joins = out["joins"]

    def put(rows: list[Any]) -> None:
        out["joins"] = rows

    cut = cap_items(out, lambda: joins, put)
    if cut:
        out["joins_omitted"] = cut
        out["note"] += f" {cut} of {total} index rows were left out to fit."
    return out


@mcp.tool()
async def get_join_strategy(kg_a: str, kg_b: str | None = None) -> dict[str, Any]:
    """Look up a PRECOMPUTED, verified recipe for joining two KGs.

    Call this FIRST when a question spans two graphs, before `find_crosswalks`
    (which scans live and often times out) and before writing a federated join;
    call `get_schema` for each KG in the same turn. A recipe gives the predicates
    and roles on each side, the shared identifier and its namespace, any bridge
    graph, and a runnable `skeleton_query`: a verified `COUNT(DISTINCT <shared
    key>)` join that already applies every IRI rewrite (one id often appears in 2-3
    IRI forms, so a naive join silently returns nothing). RUN it non-exploratory,
    so the join lands in the transcript, then extend that same query with your own
    payload. Do NOT split the join into exploratory lookups and hard-code an id
    read off one: the query that establishes the join must be logged, or the
    transcript can't reproduce its own result.

    Args:
        kg_a: a KG shortname (as from `list_kgs`).
        kg_b: optional second shortname. Omit to list everything `kg_a` can join.

    Returns (kg_b given) one of:
      * `{"status": "verified", "joins": [recipe, ...]}`: apply the recipe
        (`list_crosswalks(include_examples=True)` has example questions). A
        predicate of `"node-iri"` means the id IS the entity's own IRI (join on
        it directly). `skeleton_verified: true` means the skeleton reproduced
        `verified_count` on `verified_on`. Recipes that link the same entity
        through different identifiers carry a `complementary_note`, and a
        top-level `note` flags them as COMPLEMENTARY: UNION them for complete
        coverage rather than picking one.
      * `{"status": "known_non_join", "non_joins": [...]}`: this pair was CHECKED
        and does not join on the obvious key. Do NOT attempt it; read `diagnosis`.
      * `{"status": "unknown", ...}`: nothing precomputed. Fall back to
        `find_crosswalks(kg_a)` / `find_crosswalks(kg_b)` to discover a key live.
    Returns (kg_b omitted) every verified join touching `kg_a`, grouped by
    `domain`, with `island` and `known_non_joins`; for hub KGs (ubergraph,
    spoke-okn, prokn) an index (`"detail": "index"`), one line per join. Ask for
    the pair to get the recipe.
    """
    verified_on = crosswalk_table.verified_on()
    if kg_b is None:
        full = {
            "shortname": kg_a,
            "verified_on": verified_on,
            "joins": crosswalk_table.verified_for(kg_a),
            "island": crosswalk_table.island_status(kg_a),
            "known_non_joins": crosswalk_table.nonjoin_for(kg_a),
        }
        return full if reply_size(full) <= REPLY_CHAR_BUDGET else _join_index(full)

    # The catalogue's example questions describe what the join is good for, not
    # how to run it; they were ~17% of a pair reply (list_crosswalks has them).
    joins = [
        {
            k: v
            for k, v in j.items()
            if k not in ("example_questions", "example_question")
        }
        for j in crosswalk_table.join_between(kg_a, kg_b)
    ]
    if joins:
        out = {"status": "verified", "verified_on": verified_on, "joins": joins}
        complementary = _complementary_note(joins)
        if complementary:
            out["note"] = complementary
        return out

    non_joins = crosswalk_table.nonjoin_between(kg_a, kg_b)
    if non_joins:
        return {
            "status": "known_non_join",
            "verified_on": verified_on,
            "non_joins": non_joins,
            "note": (
                "This pair was verified to NOT join on the attempted key — do not "
                "retry it. See each `diagnosis`."
            ),
        }

    islands = [s for s in (kg_a, kg_b) if crosswalk_table.island_status(s) is not None]
    island_ctx = {s: crosswalk_table.island_status(s) for s in islands}
    note = (
        "No precomputed crosswalk for this pair. Fall back to "
        f"`find_crosswalks('{kg_a}')` and `find_crosswalks('{kg_b}')` to discover a "
        "shared id live, then join on it."
    )
    if islands:
        note += (
            f" NOTE: {', '.join(islands)} is a profiled island / thin-thread KG "
            "(scarce public join keys) — see `island` for what little it exposes."
        )
    return {
        "status": "unknown",
        "verified_on": verified_on,
        "note": note,
        "island": island_ctx or None,
    }


@mcp.tool()
async def taxon_overlap(kg_a: str, kg_b: str) -> dict[str, Any]:
    """Build a runnable query for the NCBITaxon overlap between two KGs.

    The taxonomy crosswalks are a HUB: each KG joins `ubergraph` (see
    `list_crosswalks`, domain "Taxonomy"), not each other — so the table stores no
    direct pairwise count. This tool composes two hub spokes THROUGH ubergraph into
    a runnable skeleton you then execute with `query` / federation (it does not run
    it — federated taxonomy joins can be heavy).

    Pairwise taxon overlap is NOT single-valued; two skeletons are returned:
      * `exact_id_skeleton` — taxa carrying the SAME NCBITaxon id in both KGs
        (strict intersection).
      * `clade_membership_skeleton` — `kg_b` taxa nested under `kg_a`'s taxa via
        ubergraph `subClassOf*`. This can be FAR larger when one side is
        coarser-grained (e.g. genus names vs strain-level taxids); it is
        directional, so swap `kg_a`/`kg_b` to flip which side is the clade. The
        exact-id count understating a real biological overlap is the #1 trap here.

    Each side applies its KG's own id normalization (PATRIC genome id, UniProt
    taxonomy IRI, label resolution, …). Materialized counts (exact-id + both clade
    directions) are returned under `materialized_overlap` when the pair has a
    non-zero overlap precomputed in the NCBITaxon hub (see `list_crosswalks`); a
    verified pairwise crosswalk recipe (e.g. spoke-genelab<->spoke-okn, D9) is
    returned under `materialized` so you can use the stored count instead of
    re-running.

    Args:
        kg_a: a KG shortname in the NCBITaxon hub (see `TAXON_HUB_KGS`).
        kg_b: the other KG shortname.

    Returns `{"kg_a", "kg_b", "exact_id_skeleton", "clade_membership_skeleton",
    "note", "materialized_overlap"?, "materialized"?}`, or `{"status":
    "not_in_taxon_hub", ...}` if either KG has no taxon representation that reaches
    the hub.
    """
    missing = [k for k in (kg_a, kg_b) if not taxon_hub.in_taxon_hub(k)]
    if missing:
        return {
            "status": "not_in_taxon_hub",
            "missing": missing,
            "taxon_hub_kgs": TAXON_HUB_KGS,
            "note": (
                f"{missing} not in the NCBITaxon hub, so no taxon overlap can be "
                f"composed. KGs whose taxa reach the hub: {TAXON_HUB_KGS}."
            ),
        }
    out: dict[str, Any] = {
        "kg_a": kg_a,
        "kg_b": kg_b,
        "exact_id_skeleton": taxon_hub.build_exact_skeleton(kg_a, kg_b),
        "clade_membership_skeleton": taxon_hub.build_clade_skeleton(kg_a, kg_b),
        "note": (
            "Pairwise taxon overlap is computed THROUGH the ubergraph hub. "
            "exact_id counts the SAME NCBITaxon id on both sides; clade_membership "
            "counts kg_b taxa under kg_a's clades (subClassOf*) and can be much "
            "larger when one side is coarser-grained. Swap kg_a/kg_b to flip the "
            "clade direction. Run a skeleton with `query`/federation, or use "
            "`materialized_overlap` if present."
        ),
    }
    overlap = crosswalk_table.taxon_hub_pair(kg_a, kg_b)
    if overlap is not None:
        out["materialized_overlap"] = overlap
        out["materialized_overlap_verified_on"] = (
            crosswalk_table.taxon_hub_verified_on()
        )
        out["note"] = (
            f"Materialized overlap (verified {crosswalk_table.taxon_hub_verified_on()}): "
            f"exact_id={overlap.get('exact_id')}, "
            f"{kg_a} taxa in {kg_b} clades={overlap.get('clade_a_in_b')}, "
            f"{kg_b} taxa in {kg_a} clades={overlap.get('clade_b_in_a')}. "
            + out["note"]
        )
    materialized = [
        j
        for j in crosswalk_table.join_between(kg_a, kg_b)
        if j.get("shared_key") == "NCBITaxon"
    ]
    if materialized:
        out["materialized"] = materialized
    return out


@mcp.tool()
async def list_crosswalks(include_examples: bool = False) -> dict[str, Any]:
    """List EVERY precomputed cross-KG integration point in one call.

    The federation ships a curated, hand-verified table of join recipes between
    knowledge graphs. `get_join_strategy` narrows it to one KG or one pair; this
    returns the whole map at once, so you can discover which graphs connect —
    and on what shared identifier — without knowing the pair in advance. Each row
    is a compact summary; call `get_join_strategy(kg_a, kg_b)` for a pair's full
    recipe (predicates, roles, IRI-normalization snippet, counts).

    Args:
        include_examples: when True, each row also carries an
            `example_question` describing what the join answers. Off by default:
            with examples the listing is about 180K characters, more than clients
            deliver, so they are dropped again (with a `note`) whenever the result
            would not fit. `get_join_strategy(kg_a, kg_b)` returns a pair's
            examples.

    Returns:
        `{"verified_on", "count", "crosswalks": [...], "taxon_clade_note"?}`. Rows
        are sorted by `(domain, shared_key)`, so the list reads as a table grouped
        by `domain` (e.g. "Genes", "Geospatial", "Disease & phenotype") and ordered
        by ontology within each — render it directly as such. `kgs` lists every KG
        the join touches in join order (left → bridge → right), each an official
        registry shortname usable directly with `describe_kg`/`get_schema`/`query`.
        Most rows carry a single `verified_count`; `verified_on` dates the counts.

        The NCBITaxon crosswalks are a hub (each KG joins `ubergraph`); rather than
        list each KG's overlap with that plumbing, the listing shows ONE row PER
        non-zero KG pair, composed through the hub (`kgs: [kg_a, "ubergraph",
        kg_b]`, `bridge_kg: "ubergraph"`, `hub: "ubergraph"`). These rows have NO
        single `verified_count`; the overlap is two-valued — `exact_id` (taxa with
        the same NCBITaxon id, symmetric) plus directional `clade_a_in_b` /
        `clade_b_in_a` (taxa nested under the other KG's clades via `subClassOf*`,
        often far larger). Some Taxonomy rows are instead LABEL-BRIDGED
        (`match_type: "label"`): biohealth carries no NCBITaxon id, so its organisms
        are matched to the other KG by exact scientific name, and the row carries
        `label_match` / `kg_b_taxa` (NOT `exact_id`/clade) — render these as
        "label match: <label_match> of <kg_b_taxa> organisms by name". Do NOT drop a
        Taxonomy row just because it lacks the id columns. When the result includes
        Taxonomy rows it also carries a top-level `taxon_clade_note`: RENDER IT as a
        short paragraph AFTER the table so the reader understands both the id columns
        and the label rows. `taxon_overlap(kg_a, kg_b)` returns the runnable
        skeletons.

        Rows where `ubergraph` is a bare endpoint (a KG's overlap with the ontology
        backbone, not a KG-to-KG join — e.g. oard-kg's MONDO terms, biobricks-mesh's
        MeSH terms) are omitted from this listing; they remain available via
        `get_join_strategy` and are what inline `subClassOf*` category expansion
        uses. In the listing ubergraph appears only as a bridge (middle of `kgs`).
    """
    rows = crosswalk_table.all_crosswalks(include_examples=include_examples)
    out: dict[str, Any] = {
        "verified_on": crosswalk_table.verified_on(),
        "count": len(rows),
        "crosswalks": rows,
    }
    if any(r["shared_key"] == "NCBITaxon" for r in rows):
        out["taxon_clade_note"] = crosswalk_table.TAXON_CLADE_NOTE
    if include_examples and reply_size(out) > REPLY_CHAR_BUDGET:
        out["crosswalks"] = crosswalk_table.all_crosswalks(include_examples=False)
        out["note"] = (
            "example_question was dropped from every row: with it the listing is "
            "too large to deliver. get_join_strategy(kg_a, kg_b) returns a pair's "
            "examples."
        )
    rows = out["crosswalks"]

    def put(kept: list[Any]) -> None:
        out["crosswalks"] = kept

    cut = cap_items(out, lambda: rows, put)
    if cut:
        out["rows_omitted"] = cut
        out["note"] = (
            out.get("note", "") + f" {cut} of {len(rows)} rows left out to fit; "
            "get_join_strategy(kg) lists one KG's joins."
        ).strip()
    return out


def _supplier_predicate(
    entry: dict[str, Any], kg: str
) -> tuple[str | None, str | None]:
    """The predicate/role on ``kg``'s OWN side of a verified join recipe.

    Returns ``(None, None)`` when ``kg`` is only the bridge (or a clique member)
    of the entry — it has no single endpoint predicate there.
    """
    if entry.get("left_kg") == kg:
        return entry.get("left_predicate"), entry.get("left_role")
    if entry.get("right_kg") == kg:
        return entry.get("right_predicate"), entry.get("right_role")
    return None, None


def _key_matches(shared_key: str | None, join_key: str) -> bool:
    """Case-insensitive substring match of ``join_key`` against a shared key.

    So ``Entrez`` also matches the bridged keys ``Entrez -> HGNC (bridged)`` and
    ``HGNC -> Entrez (bridged)``.
    """
    return bool(shared_key) and join_key.lower() in str(shared_key).lower()


def _joins_on_key(kg: str, join_key: str | None) -> list[dict[str, Any]]:
    """Project ``kg``'s verified joins, optionally filtered to ``join_key``.

    Each is projected to ``{shared_key, predicate, role, bridge_kg, size}``,
    deduplicated, with the biggest verified count first.
    """
    seen: set[tuple[Any, ...]] = set()
    rows: list[dict[str, Any]] = []
    for entry in crosswalk_table.verified_for(kg):
        sk = entry.get("shared_key")
        if join_key is not None and not _key_matches(sk, join_key):
            continue
        predicate, role = _supplier_predicate(entry, kg)
        sig = (sk, predicate, entry.get("bridge_kg"))
        if sig in seen:
            continue
        seen.add(sig)
        rows.append(
            {
                "shared_key": sk,
                "predicate": predicate,
                "role": role,
                "bridge_kg": entry.get("bridge_kg"),
                "size": entry.get("verified_count"),
            }
        )
    rows.sort(key=lambda r: (r.get("size") is None, -(r.get("size") or 0)))
    return rows


def _best_size(joins: list[dict[str, Any]]) -> int:
    """The largest verified join size in a list (0 if none has a count)."""
    return max((j.get("size") or 0) for j in joins) if joins else 0


@mcp.tool()
async def find_context_sources(
    want: list[str] | None = None,
    join_key: str | None = None,
) -> dict[str, Any]:
    """Reverse capability index: which KGs SUPPLY a given context type, joinably.

    The inverse of `get_join_strategy`. Instead of "how do these two KGs join?",
    this answers "who supplies pathway / GO / trait / disease … for an entity I can
    join on `join_key`?" in ONE deterministic call — so you enumerate every graph
    that adds the context you need BEFORE narrowing, rather than judging a graph by
    its name and concluding a context type is "unavailable" without checking. It
    combines the curated per-KG `payload` tags (what a graph carries; see
    `list_kgs`) with the verified crosswalk table (the predicate, shared key, and
    `COUNT(DISTINCT)` size of each join).

    Args:
        want: context types to look for, from the payload vocabulary — e.g.
            `["GO", "pathway", "gene_set", "trait", "disease"]`. Unknown types are
            echoed back in `unmatched_want` (the rest still run). Omit to consider
            every payload type.
        join_key: optional shared identifier the supplier must be joinable on —
            e.g. `"Entrez"`, `"UniProt"`, `"MONDO"`, `"S2_L13"`. Matched as a
            case-insensitive substring, so `"Entrez"` also matches bridged keys
            like `"Entrez -> HGNC (bridged)"`. Omit to list every key each
            supplier joins on.

    Returns `{"want", "join_key", "payloads_verified_on", "crosswalks_verified_on",
    "sources", "payload_only", "unmatched_want", "note"}`:
      * `sources` — `{context_type: [{"kg", "payloads", "joins": [{shared_key,
        predicate, role, bridge_kg, size}, ...]}, ...]}`. Within each type, KGs are
        sorted by their LARGEST join `size` first, so the biggest join surfaces at
        the top (the trap this defeats: not noticing the biggest gene join). `kg`'s
        full `payloads` list is included so you see everything it adds, not just the
        type you asked for.
      * `payload_only` — `{context_type: [kg, ...]}`: KGs that SUPPLY the type but
        do NOT join on `join_key` (e.g. they key genes on Ensembl, not Entrez).
        They are not hidden — they still warrant a schema check or an id
        conversion. Empty when `join_key` is omitted.
      * `unmatched_want` — requested types that are not in the vocabulary.

    Every requested (known) type appears as a key in `sources` even when its list
    is empty, so an empty list is POSITIVE evidence that nothing supplies it on
    that key — not an unchecked assumption.
    """
    vocab = payload_table.vocabulary()
    requested = list(want) if want else sorted(vocab)
    known = [t for t in requested if t in vocab]
    unmatched = [t for t in requested if t not in vocab]

    sources: dict[str, list[dict[str, Any]]] = {t: [] for t in known}
    payload_only: dict[str, list[str]] = {}
    for ptype in known:
        for kg in payload_table.kgs_with_payload(ptype):
            joins = _joins_on_key(kg, join_key)
            if not joins and join_key is not None:
                # Has the payload but isn't reachable on this key — surface it
                # separately rather than dropping it silently.
                payload_only.setdefault(ptype, []).append(kg)
                continue
            sources[ptype].append(
                {
                    "kg": kg,
                    "payloads": payload_table.payloads_for(kg),
                    "joins": joins,
                }
            )
        sources[ptype].sort(key=lambda s: -_best_size(s["joins"]))

    note = (
        "Each requested type is listed even when empty: an empty `sources[type]` is "
        "verified evidence that no KG supplies it"
        + (f" joinably on '{join_key}'" if join_key else "")
        + ". Check `payload_only` for KGs that carry the type but key it "
        "differently before concluding a context is unavailable. KGs within a type "
        "are sorted by largest join size first."
    )
    out: dict[str, Any] = {
        "want": known,
        "join_key": join_key,
        "payloads_verified_on": payload_table.verified_on(),
        "crosswalks_verified_on": crosswalk_table.verified_on(),
        "sources": sources,
        "payload_only": payload_only,
        "note": note,
    }
    if unmatched:
        out["unmatched_want"] = unmatched
        out["vocabulary"] = vocab
    return _fit_context_sources(out)


def _fit_context_sources(out: dict[str, Any]) -> dict[str, Any]:
    """Trim per-supplier join lists until the reply fits the budget.

    Without a ``join_key`` every supplier lists every key it joins on, and the
    reply reaches 87K-433K characters. Trimming never drops a SUPPLIER: the point
    of the tool is to enumerate them all. It shortens each supplier's ``joins`` to
    its largest few and records ``joins_omitted``. Passing ``join_key`` returns
    the rest.
    """
    if reply_size(out) <= REPLY_CHAR_BUDGET:
        return out
    out["note"] += (
        " To fit, each supplier lists only its largest join(s), with "
        "`joins_omitted` counting the rest. Pass `join_key` (or fewer `want` "
        "types) for the complete join lists."
    )

    def shorten(keep: int) -> None:
        for suppliers in out["sources"].values():
            for supplier in suppliers:
                joins = supplier["joins"]
                if len(joins) > keep:
                    if keep == 0:
                        # Keep the headline even when the list goes.
                        supplier["largest_join"] = {
                            "shared_key": joins[0].get("shared_key"),
                            "size": joins[0].get("size"),
                        }
                    supplier["joins_omitted"] = supplier.get("joins_omitted", 0) + (
                        len(joins) - keep
                    )
                    supplier["joins"] = joins[:keep]

    def drop_payloads() -> None:
        # The payload list repeats for a supplier under every type it appears in.
        for suppliers in out["sources"].values():
            for supplier in suppliers:
                supplier.pop("payloads", None)

    steps: list[Callable[[], None]] = [
        lambda: shorten(5),
        drop_payloads,
        lambda: shorten(1),
        lambda: shorten(0),
    ]
    for step in steps:
        if reply_size(out) <= REPLY_CHAR_BUDGET:
            break
        step()
    return out

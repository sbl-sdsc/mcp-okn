#!/usr/bin/env python3
"""Regenerate docs/crosswalks/proto-okn-crosswalk-inventory.md from crosswalks.json.

The inventory is a per-domain table of every verified cross-KG crosswalk — the
joined KGs, shared identifier, verified overlap count, and an example question.
It is FULLY DATA-DRIVEN off the same source the MCP server serves
(``mcp_okn.crosswalks.all_crosswalks()`` over ``data/crosswalks.json``), so it
never drifts from the table: run this after editing the crosswalk table and the
doc's counts/rows/examples are rebuilt from the source of record.

    python scripts/build_crosswalk_inventory.py            # rewrite the doc
    python scripts/build_crosswalk_inventory.py --check    # exit 1 if out of date

Rendering mirrors ``list_crosswalks``: rows come from ``all_crosswalks()`` already
sorted by ``(domain, shared_key, kgs)``, grouped into ``## Domain`` sections. The
KGs column joins the join-order KGs with ``→`` when the row bridges through a hub
(``bridge_kg`` set), ``+ … (N-way)`` for a bridgeless clique of 3+ co-equal members,
and ``↔`` for a plain pair; the shared-key label is cleaned the same
way the network figure cleans it. Taxonomy is special-cased (two materialized
counts per pair, id-rows then label-bridged ``†`` rows), matching its schema.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "crosswalks" / "proto-okn-crosswalk-inventory.md"
sys.path.insert(0, str(ROOT / "src"))

from mcp_okn import crosswalks as C  # noqa: E402

TAXON_DOMAIN = "Taxonomy"

# Static prose blocks reproduced verbatim (they describe the schema, not the data).
TAXON_INTRO = (
    "These are pairwise organism overlaps composed **through the ubergraph hub**, "
    "so each carries two materialized counts rather than one. `exact_id` = taxa "
    "with the identical NCBITaxon id on both sides (symmetric). `clade_a_in_b` / "
    "`clade_b_in_a` = how many of the first / second KG's taxa fall under the "
    "other's once expanded through ubergraph's `subClassOf*` hierarchy "
    "(directional). Clade membership is the more complete biological overlap and "
    "is often far larger when one KG records coarser taxa (genus) and the other "
    "finer ones (strain). Rows marked **†** are label-bridged (`biohealth`, which "
    "carries no NCBITaxon ids, matched by exact scientific name) — see the note "
    "below the table. Like every other domain, **Examples** carries two questions "
    "per row: the count question (what the `exact_id` / `clade` columns measure) and "
    "the science question the pair answers."
)
TAXON_FOOTNOTE = (
    "† **Label-bridged.** `biohealth` carries no NCBITaxon ids, so these overlaps "
    "are matched by exact scientific **name**, not NCBITaxon id. For these rows the "
    "count is `label_match / partner's total taxa` — how many of the partner KG's "
    "NCBITaxon organisms have a same-name `biohealth` concept, out of that KG's "
    "total — and the `exact_id`/`clade` semantics of the other rows do not apply. "
    "Name-based and conservative (misses synonyms and spelling variants), with no "
    "`subClassOf*` clade expansion."
)
TAXON_CLOSING = (
    "For any pair, call `get_join_strategy(kg_a, kg_b)` to get the full recipe — "
    "predicates, roles, IRI-normalization snippet — or `taxon_overlap(kg_a, kg_b)` "
    "for runnable taxonomy skeletons."
)


def clean_key(shared_key: str | None) -> str:
    """Render a shared_key for display: ASCII arrows -> unicode, drop the trailing
    ``(bridged)``/``(two-hop)`` marker (the bridge shows in the KGs column instead)."""
    base = (
        (shared_key or "").replace("<->", "↔").replace(" -> ", "→").replace("->", "→")
    )
    return re.sub(r"\s*\((?:bridged|two-hop)\)\s*$", "", base)


def fmt_kgs(row: dict) -> str:
    """Join a row's KGs in join order: ``→`` through a bridge hub, else ``↔``.

    A 3-KG row with NO bridge is a CLIQUE — every member carries the shared key
    natively and joins every other directly. Its members are sorted alphabetically,
    so rendering it ``a ↔ b ↔ c`` reads as a path through whichever name happens to
    sort in the middle (it did: pankgraph looked like a bridge between GXA and
    spoke-okn, which it is not). Render cliques with ``+`` so no member can be
    mistaken for a hop.
    """
    if not row.get("bridge_kg") and len(row["kgs"]) > 2:
        return " + ".join(row["kgs"]) + f" ({len(row['kgs'])}-way)"
    sep = " → " if row.get("bridge_kg") else " ↔ "
    return sep.join(row["kgs"])


def _num(n) -> str:
    return f"{n:,}" if isinstance(n, int) else str(n)


def fmt_examples(r: dict) -> str:
    """Render a row's example question(s), joined for a single Markdown cell.

    Prefers the ``example_questions`` list (each crosswalk carries two — a
    high-level and a specific/quantitative angle); falls back to the legacy
    single ``example_question``."""
    qs = r.get("example_questions") or (
        [r["example_question"]] if r.get("example_question") else []
    )
    return "<br><br>".join(q for q in qs if q)


def render_domain_table(domain: str, rows: list[dict]) -> list[str]:
    out = [
        f"## {domain}",
        "",
        "| KGs | Shared key | Count | Examples |",
        "|---|---|---|---|",
    ]
    for r in rows:
        out.append(
            f"| {fmt_kgs(r)} | {clean_key(r['shared_key'])} | "
            f"{_num(r['verified_count'])} | {fmt_examples(r)} |"
        )
    out.append("")
    return out


def render_taxonomy(rows: list[dict]) -> list[str]:
    # id-rows first, then label-bridged rows; each ordered by KGs (a, b).
    id_rows = sorted(
        (r for r in rows if r.get("match_type") == "id"), key=lambda r: r["kgs"]
    )
    label_rows = sorted(
        (r for r in rows if r.get("match_type") == "label"), key=lambda r: r["kgs"]
    )
    out = [
        f"## {TAXON_DOMAIN}",
        "",
        TAXON_INTRO,
        "",
        "| KGs | exact_id | clade A-in-B / B-in-A | Examples |",
        "|---|---|---|---|",
    ]
    for r in id_rows:
        a, b = r["kgs"][0], r["kgs"][-1]
        out.append(
            f"| {a} × {b} | {_num(r['exact_id'])} | "
            f"{_num(r['clade_a_in_b'])} / {_num(r['clade_b_in_a'])} | "
            f"{fmt_examples(r)} |"
        )
    for r in label_rows:
        a, b = r["kgs"][0], r["kgs"][-1]
        out.append(
            f"| {a} × {b} † | {_num(r['label_match'])} / {_num(r['kg_b_taxa'])} | — | "
            f"{fmt_examples(r)} |"
        )
    out += ["", TAXON_FOOTNOTE, "", TAXON_CLOSING, ""]
    return out


def render() -> str:
    rows = C.all_crosswalks(include_examples=True)
    verified_on = C.verified_on() or "unknown"

    # Preserve all_crosswalks' (domain, shared_key, kgs) order; group by domain.
    domains: list[str] = []
    by_domain: dict[str, list[dict]] = {}
    for r in rows:
        by_domain.setdefault(r["domain"], []).append(r)
        if r["domain"] not in domains:
            domains.append(r["domain"])

    lines = [
        "# Proto-OKN Crosswalk Inventory",
        "",
        f"- **Date:** {verified_on}",
        "- **Model:** claude-opus-4-8",
        "- **SPARQL endpoint:** https://apps.okn.us/federation/sparql",
        "",
        "## Knowledge graphs used",
        "",
        "- _None queried._",
        "",
        "## Conversation",
        "",
        "👤 **User**",
        "",
        "list crosswalks with examples",
        "",
        "---",
        "",
        "🧠 **Assistant**",
        "",
        f"Here are all {len(rows)} precomputed cross-KG crosswalks (verified through "
        f"{verified_on}), grouped by domain. Each shows the knowledge graphs joined, "
        "the shared identifier, the verified overlap count, and example questions "
        "the join answers.",
        "",
    ]
    for domain in domains:
        if domain == TAXON_DOMAIN:
            lines += render_taxonomy(by_domain[domain])
        else:
            lines += render_domain_table(domain, by_domain[domain])
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> None:
    check = "--check" in sys.argv
    generated = render()
    if check:
        current = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
        if current != generated:
            print(
                f"OUT OF DATE: {DOC} differs from crosswalks.json — run "
                "scripts/build_crosswalk_inventory.py"
            )
            sys.exit(1)
        print(f"up to date: {DOC.name} matches crosswalks.json")
        return
    DOC.write_text(generated, encoding="utf-8")
    n = len(C.all_crosswalks(include_examples=False))
    print(
        f"wrote {DOC.relative_to(ROOT)} — {n} crosswalks across "
        f"{len({r['domain'] for r in C.all_crosswalks()})} domains"
    )


if __name__ == "__main__":
    main()

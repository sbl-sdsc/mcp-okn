#!/usr/bin/env python3
"""Regenerate docs/crosswalks/crosswalks_sparql_skeletons.md from crosswalks.json.

The skeleton reference lists, for every verified crosswalk, the join key and a
RUNNABLE `COUNT(DISTINCT <key>)` SPARQL skeleton with the IRI normalization
already applied (a naive join on the raw id usually returns 0 rows). Like the
inventory doc, it is FULLY DATA-DRIVEN off the table the MCP server serves, so it
cannot drift from the recipes `get_join_strategy` hands out:

    python scripts/build_skeleton_reference.py            # rewrite the doc
    python scripts/build_skeleton_reference.py --check    # exit 1 if out of date

Structure: `### DOMAIN` → one block per **key family** (the crosswalks sharing a
`shared_key`), each listing its KG pairs with verified counts and the identifier
namespace, then the skeleton(s).

Why every DISTINCT skeleton is rendered, not one per family: the pairs inside a
family routinely need DIFFERENT SPARQL. The CAS family alone carries nine — the
biobricks graphs hang the id off `edam:has_identifier`, MeSH exposes it as
`meshv:registryNumber`, and SAWGraph/SOCKG store it as a bare literal that must be
rebuilt into an IRI. A single "representative" skeleton (what the hand-written
version of this doc shipped) is therefore wrong for most pairs in the family, so
skeletons are deduplicated WITHIN a family and each is labelled with the pairs it
actually applies to.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "crosswalks" / "crosswalks_sparql_skeletons.md"
sys.path.insert(0, str(ROOT / "src"))

from mcp_okn import crosswalks as C  # noqa: E402
from mcp_okn.sparql import named_graph  # noqa: E402

ENDPOINT = "https://apps.okn.us/federation/sparql"


def clean_key(shared_key: str | None) -> str:
    """Render a shared_key for display (ASCII arrows -> unicode)."""
    return (
        (shared_key or "").replace("<->", "↔").replace(" -> ", "→").replace("->", "→")
    )


def _num(n) -> str:
    return f"{n:,}" if isinstance(n, int) else str(n)


def pair_label(entry: dict) -> str:
    """``left × right`` for an entry, with the bridge shown as ``left → hub → right``."""
    left, right = entry.get("left_kg"), entry.get("right_kg")
    bridge = entry.get("bridge_kg")
    return f"{left} → {bridge} → {right}" if bridge else f"{left} × {right}"


def pair_with_count(entry: dict) -> str:
    count = entry.get("verified_count")
    label = pair_label(entry)
    return f"{label}({_num(count)})" if count is not None else label


def kgs_in(entries: list[dict]) -> list[str]:
    """Every KG named by the given entries, in first-seen order."""
    seen: list[str] = []
    for e in entries:
        for kg in (e.get("left_kg"), e.get("bridge_kg"), e.get("right_kg")):
            if kg and kg not in seen:
                seen.append(kg)
    return seen


def render_family(key: str, entries: list[dict]) -> list[str]:
    """One key family: its pairs, its namespace, and each distinct skeleton."""
    namespaces = [e.get("key_namespace") for e in entries if e.get("key_namespace")]
    ns = f" — `{namespaces[0]}`" if namespaces else ""
    pairs = ", ".join(pair_with_count(e) for e in entries)

    out = [f"**{clean_key(key)}**{ns}: {pairs}.", ""]

    # Deduplicate skeletons within the family, keeping first-seen order, and label
    # each with the pairs it covers — the pairs in one family often need different
    # SPARQL (see the module docstring).
    by_skeleton: dict[str, list[dict]] = {}
    missing: list[dict] = []
    for e in entries:
        skel = (e.get("skeleton_query") or "").strip()
        if skel:
            by_skeleton.setdefault(skel, []).append(e)
        else:
            missing.append(e)

    for skel, covered in by_skeleton.items():
        if len(by_skeleton) > 1:
            unverified = [e for e in covered if not e.get("skeleton_verified")]
            note = " (skeleton not re-verified)" if unverified else ""
            out.append(f"_{', '.join(pair_label(e) for e in covered)}_{note}")
            out.append("")
        out += ["```sparql", skel, "```", ""]

    for e in missing:
        out += [
            f"_{pair_label(e)}_ — no static skeleton: the key is COMPUTED at query "
            "time (call the `spatial_bridge` tool, which derives the S2 cell from "
            "the KG's lat/long).",
            "",
        ]
    return out


def render() -> str:
    raw = C.load_crosswalks().get("verified_crosswalks", [])
    verified_on = C.verified_on() or "unknown"
    n_user_facing = len(C.all_crosswalks(include_examples=False))

    # Group by domain, then by shared key, preserving a stable (domain, key) order.
    domains: list[str] = []
    by_domain: dict[str, dict[str, list[dict]]] = {}
    for e in raw:
        domain = C.domain_of(e)
        if domain not in by_domain:
            by_domain[domain] = {}
            domains.append(domain)
        by_domain[domain].setdefault(e.get("shared_key") or "—", []).append(e)
    domains.sort()

    n_families = sum(len(fams) for fams in by_domain.values())

    lines = [
        "# OKN / Proto-OKN Crosswalk Reference — Join Keys & SPARQL Skeletons",
        "",
        f"- **Date:** {verified_on}",
        "- **Model:** claude-opus-4-8",
        f"- **SPARQL endpoint:** {ENDPOINT}",
        "",
        "> **GENERATED FILE — do not edit by hand.** Rebuilt from the crosswalk table"
        " (`metadata/crosswalks.json`) by `scripts/build_skeleton_reference.py`; a test"
        " fails if it drifts. Edit the table (and its `skeleton_query`), then"
        " regenerate.",
        "",
        "## Knowledge graphs used",
        "",
    ]
    lines += [f"- `{kg}` — <{named_graph(kg)}>" for kg in kgs_in(raw)]
    lines += [
        "",
        "## Conversation",
        "",
        "👤 **User**",
        "",
        "For each crosswalk, list the join key and the SPARQL skeleton",
        "",
        "---",
        "",
        "🧠 **Assistant**",
        "",
        f"The OKN federation has **{n_user_facing} crosswalks**, which collapse into "
        f"**{n_families} join-key families** (a domain + a shared identifier). They are "
        "grouped below by domain and key family — each entry lists every KG pair "
        "sharing that key (with its verified `COUNT(DISTINCT)`), the identifier "
        "scheme/namespace, and a runnable `COUNT(DISTINCT)` skeleton with the IRI "
        "normalization already applied (a naive join on the raw id usually returns "
        "0 rows).",
        "",
        "**Pairs in one family often need different SPARQL**, so where a family's "
        "members diverge, every distinct skeleton is shown and labelled with the pairs "
        "it applies to. The CAS family is the clearest case: the biobricks graphs hang "
        "the id off `edam:has_identifier`, MeSH exposes it as `meshv:registryNumber`, "
        "and SAWGraph/SOCKG store it as a bare literal that must be rebuilt into an "
        "IRI. Copy the skeleton for YOUR pair, then extend it with your payload.",
        "",
        f"Counts verified {verified_on}. For any pair, `get_join_strategy(kg_a, kg_b)` "
        "returns the same skeleton plus the full recipe (predicates, roles, "
        "normalization); `taxon_overlap(kg_a, kg_b)` returns runnable skeletons for the "
        "NCBITaxon hub, whose overlaps are two-valued (exact id vs clade membership) "
        "and therefore not a single count.",
        "",
    ]

    for domain in domains:
        lines += [f"### {domain.upper()}", ""]
        for key, entries in by_domain[domain].items():
            lines += render_family(key, entries)

    lines += [
        "### NOTES",
        "",
        "- **Skeletons are COUNT queries by design.** Each proves the key still joins "
        "and reproduces the table's `verified_count`; run it first, then extend it with "
        "your payload rather than rebuilding the normalization boilerplate.",
        "- **The identifier, not the entity, is what matches.** Counts are "
        "`COUNT(DISTINCT <shared key>)` — shared identifiers, not shared rows. A KG may "
        "mint several nodes carrying the same id.",
        f"- **Sources:** the crosswalk table served by `list_crosswalks` / "
        f"`get_join_strategy` (verified {verified_on}).",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        current = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
        if current != text:
            print(f"OUT OF DATE: {DOC.relative_to(ROOT)} — rerun {Path(__file__).name}")
            return 1
        print(f"up to date: {DOC.relative_to(ROOT)}")
        return 0
    DOC.write_text(text, encoding="utf-8")
    n_skeletons = len(re.findall(r"^```sparql$", text, flags=re.M))
    print(
        f"wrote {DOC.relative_to(ROOT)} — "
        f"{len(C.all_crosswalks(include_examples=False))} crosswalks, "
        f"{n_skeletons} skeletons"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

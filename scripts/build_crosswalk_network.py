#!/usr/bin/env python3
"""Regenerate the data embedded in docs/crosswalks/crosswalk-network.html.

The interactive network is fully DATA-DRIVEN: every line of rendering, the
force-directed layout, parallel-edge fanning, dashed/dotted bridge styling,
the legend, tooltips, zoom/drag — all read from three JS constants at the top
of the page's final <script>:

    DOM      domain code -> [label, colour]
    BRIDGES  (kept as-is)
    R        one row per crosswalk: [domainCode, [kgs...], count, "key (bridge)"]

So to refresh the figure after the crosswalk table changes you only regenerate
`R` (and add a `DOM` colour for any brand-new domain) and splice it back in.
Nothing else is touched, so the functionality and visual encoding/layout are
preserved by construction; the D3 force layout simply recomputes positions for
the new data at load time.

This script reads the SAME source the MCP server serves — the local
`mcp_okn.crosswalks.all_crosswalks()` snapshot (data/crosswalks.json) — so the
HTML always matches the local repo. Run after updating the crosswalk table:

    python scripts/build_crosswalk_network.py

Then re-render the static PNG:

    python scripts/render_crosswalk_network_png.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs" / "crosswalks" / "crosswalk-network.html"
sys.path.insert(0, str(ROOT / "src"))

from mcp_okn import crosswalks as C  # noqa: E402

# domain label -> single-letter code used by DOM/R. Add new domains here.
DOMAIN_CODE = {
    "Chemicals": "C",
    "Disease & phenotype": "D",
    "Genes": "G",
    "Geospatial": "S",
    "Industry & supply chain": "I",
    "Proteins": "P",
    "Taxonomy": "T",
    "Anatomy & Cell Type": "A",
    "Function & Pathways": "F",
    "Social Determinants & Services": "L",
    "Environmental toxicology": "E",
    "Other": "O",
}
# fallback colours for domains not already present in the file's DOM
DEFAULT_COLORS = {
    "C": "#E8590C", "D": "#D6336C", "G": "#7048E8", "S": "#1C7ED6",
    "I": "#C9920A", "P": "#2B8A3E", "T": "#82C91E", "A": "#0C8599",
    "F": "#9C36B5", "L": "#15AABF", "E": "#5C940D", "O": "#868E96",
}


def viz_kgs(r: dict) -> list[str]:
    """Endpoints for the figure: a bridge KG is dropped (named in the key);
    a genuine 3-KG join (no bridge, e.g. pankgraph) keeps all three nodes."""
    kgs = r["kgs"]
    if r.get("bridge_kg") and len(kgs) == 3:
        return [kgs[0], kgs[2]]
    return list(kgs)


def viz_count(r):
    if r["shared_key"] == "NCBITaxon":
        if r.get("match_type") == "label":
            return r.get("label_match", 0)
        return [r.get("exact_id", 0), r.get("clade_a_in_b", 0), r.get("clade_b_in_a", 0)]
    return r.get("verified_count", 0)


def viz_key(r) -> str:
    if r["shared_key"] == "NCBITaxon":
        base = "NCBITaxon name-match" if r.get("match_type") == "label" else "NCBITaxon"
    else:
        base = r["shared_key"].replace("<->", "↔").replace(" -> ", "→").replace("->", "→")
        base = re.sub(r"\s*\((?:bridged|two-hop)\)\s*$", "", base)  # re-added as bridge below
    b = r.get("bridge_kg")
    return base + (f" ({b})" if b else "")


def _effective_count(count) -> int:
    """Single count for a row whose viz_count may be a taxon triple (list)."""
    return max(count) if isinstance(count, list) else (count or 0)


def build_rows():
    rows = C.all_crosswalks(include_examples=False)
    out = []
    kept = []
    for r in rows:
        dom = DOMAIN_CODE.get(r["domain"])
        if dom is None:
            raise SystemExit(f"Unknown domain {r['domain']!r}; add it to DOMAIN_CODE")
        count = viz_count(r)
        # Drop count-0 edges: superseded/dead routes (e.g. prokn v0.0.5 bridges
        # that now return 0) are disclosed in the crosswalk table but must not
        # appear as ghost edges in the network figure.
        if _effective_count(count) <= 0:
            continue
        out.append([dom, viz_kgs(r), count, viz_key(r)])
        kept.append(r)
    return out, kept


def parse_dom(html: str) -> dict[str, tuple[str, str]]:
    block = re.search(r"const DOM=\{(.*?)\};", html).group(1)
    return {c: (l, col) for c, l, col in re.findall(r'(\w):\["([^"]+)","(#[0-9A-Fa-f]+)"\]', block)}


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    R, rows = build_rows()

    # nodes shown = distinct KGs across the figure's endpoint arrays (bridges excluded)
    nodes = sorted({kg for row in R for kg in row[1]})
    verified_on = C.verified_on()

    # --- DOM: exactly the domains present, keeping existing colours ---
    existing = parse_dom(html)
    needed = {row[0] for row in R}
    label_for = {v: k for k, v in DOMAIN_CODE.items()}
    dom = {}
    for code in DOMAIN_CODE.values():
        if code in needed:
            color = existing[code][1] if code in existing else DEFAULT_COLORS.get(code, "#868E96")
            dom[code] = (label_for[code], color)
    # emit DOM ordered alphabetically by domain label — the D3 legend and the PNG
    # renderer both follow DOM order, so the legend reads alphabetically.
    ordered = sorted(dom, key=lambda c: dom[c][0].lower())
    dom_js = "const DOM={" + ",".join(
        f'{c}:["{dom[c][0]}","{dom[c][1]}"]' for c in ordered
    ) + "};"
    html = re.sub(r"const DOM=\{.*?\};", lambda _m: dom_js, html, count=1)

    # --- R: one JS array literal per row, grouped by domain for readability ---
    lines, cur = [], None
    for row in R:
        if row[0] != cur:
            lines.append("")  # blank line between domain groups
            cur = row[0]
        lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + ",")
    body = "\n".join(lines).strip().rstrip(",")
    r_js = "const R=[\n" + body + "\n];"
    html = re.sub(r"const R=\[.*?\n\];", lambda _m: r_js, html, count=1, flags=re.S)

    # --- header counts ---
    hdr = f"{len(nodes)} knowledge graphs, {len(R)} verified crosswalks (verified {verified_on})"
    html = re.sub(r"\d+ knowledge graphs, \d+ verified crosswalks \(verified [^)]*\)", hdr, html)

    HTML.write_text(html, encoding="utf-8")
    from collections import Counter
    print(f"updated {HTML.relative_to(ROOT)}")
    print(f"  crosswalks: {len(R)} | nodes: {len(nodes)} | verified_on: {verified_on}")
    print(f"  domains: {dict(Counter(r[0] for r in R))}")
    print(f"  DOM codes: {ordered}")


if __name__ == "__main__":
    main()

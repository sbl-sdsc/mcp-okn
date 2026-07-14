#!/usr/bin/env python3
"""Regenerate docs/crosswalks/proto-okn-crosswalk-inventory.{md,html} from crosswalks.json.

The inventory is a per-domain table of every verified cross-KG crosswalk — the
joined KGs, shared identifier, verified overlap count, and an example question.
It is FULLY DATA-DRIVEN off the same source the MCP server serves
(``mcp_okn.crosswalks.all_crosswalks()`` over ``data/crosswalks.json``), so it
never drifts from the table: run this after editing the crosswalk table and the
doc's counts/rows/examples are rebuilt from the source of record.

    python scripts/build_crosswalk_inventory.py            # rewrite both docs
    python scripts/build_crosswalk_inventory.py --check    # exit 1 if either is stale

Rendering mirrors ``list_crosswalks``: rows come from ``all_crosswalks()`` already
sorted by ``(domain, shared_key, kgs)``, grouped into ``## Domain`` sections. The
KGs column joins the join-order KGs with ``→`` when the row bridges through a hub
(``bridge_kg`` set), ``+ … (N-way)`` for a bridgeless clique of 3+ co-equal members,
and ``↔`` for a plain pair; the shared-key label is cleaned the same
way the network figure cleans it. Taxonomy is special-cased (two materialized
counts per pair, id-rows then label-bridged ``†`` rows), matching its schema.

The HTML sibling is rendered from the SAME rows — it is NOT a conversion of the
Markdown, so the two cannot disagree about counts, rows, or examples. It is a
standalone page (inline CSS/JS, no external assets) with a live filter box, and is
deliberately NOT linked from the README. Both outputs are guarded against drift by
tests/test_crosswalks.py.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "crosswalks" / "proto-okn-crosswalk-inventory.md"
DOC_HTML = DOC.with_suffix(".html")
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


# --------------------------------------------------------------------------- #
# HTML rendering — same rows, same helpers, standalone page.                    #
# --------------------------------------------------------------------------- #

CSS = """\
:root {
  color-scheme: light dark;
  --bg: #fbfaf9; --fg: #1c1a17; --muted: #6b645c; --line: #e3ded7;
  --card: #ffffff; --head: #f3efe9; --accent: #b4530a; --chip: #efeae3;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #171614; --fg: #eae6e0; --muted: #a29a90; --line: #322f2b;
    --card: #1f1e1b; --head: #272521; --accent: #e58a45; --chip: #2b2925;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2.5rem 1.25rem 5rem; background: var(--bg); color: var(--fg);
  font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
main { max-width: 1180px; margin: 0 auto; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0 0 .75rem; letter-spacing: -.01em; }
h2 {
  font-size: 1.2rem; margin: 2.75rem 0 .85rem; padding-bottom: .4rem;
  border-bottom: 2px solid var(--line); scroll-margin-top: 1rem;
}
a { color: var(--accent); }
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .87em;
  background: var(--chip); padding: .1em .35em; border-radius: 4px;
}
.meta { color: var(--muted); font-size: .9rem; margin: 0 0 1.5rem; }
.meta span + span::before { content: "·"; margin: 0 .5rem; }
.lede { font-size: 1.02rem; max-width: 72ch; }
.note { color: var(--muted); font-size: .9rem; max-width: 88ch; }
.toc { display: flex; flex-wrap: wrap; gap: .4rem; margin: 1.5rem 0 .5rem; padding: 0; list-style: none; }
.toc a {
  display: inline-block; padding: .3rem .6rem; border: 1px solid var(--line);
  border-radius: 999px; background: var(--card); text-decoration: none;
  color: var(--fg); font-size: .85rem;
}
.toc a:hover { border-color: var(--accent); color: var(--accent); }
.toc .n { color: var(--muted); }
#filter {
  width: 100%; max-width: 420px; margin: 1.25rem 0 .35rem; padding: .55rem .75rem;
  border: 1px solid var(--line); border-radius: 8px; background: var(--card);
  color: var(--fg); font: inherit; font-size: .95rem;
}
#filter:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
#count { color: var(--muted); font-size: .85rem; }
.tablewrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--card); }
table { border-collapse: collapse; width: 100%; min-width: 720px; }
th, td { text-align: left; vertical-align: top; padding: .7rem .85rem; border-bottom: 1px solid var(--line); }
thead th {
  position: sticky; top: 0; background: var(--head); font-size: .78rem;
  text-transform: uppercase; letter-spacing: .05em; color: var(--muted);
  border-bottom: 1px solid var(--line);
}
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: var(--head); }
td.kgs { font-weight: 600; white-space: nowrap; }
td.key { white-space: nowrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .87em; }
td.count { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
td.examples { color: var(--fg); }
section[hidden], tr[hidden] { display: none; }
"""

JS = """\
const box = document.getElementById('filter');
const rows = Array.from(document.querySelectorAll('tbody tr'));
const sections = Array.from(document.querySelectorAll('section'));
const count = document.getElementById('count');
const total = rows.length;
function apply() {
  const q = box.value.trim().toLowerCase();
  let shown = 0;
  for (const tr of rows) {
    const hit = !q || tr.textContent.toLowerCase().includes(q);
    tr.hidden = !hit;
    if (hit) shown++;
  }
  for (const s of sections) {
    s.hidden = !s.querySelector('tbody tr:not([hidden])');
  }
  count.textContent = q ? `${shown} of ${total} crosswalks match` : `${total} crosswalks`;
}
box.addEventListener('input', apply);
apply();
"""


def esc(text: str) -> str:
    """Escape, then honour the light inline Markdown the prose blocks use
    (``**bold**`` and ``` `code` ```) — the escape runs first so the source can
    never inject markup."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", out)


def fmt_examples_html(r: dict) -> str:
    qs = r.get("example_questions") or (
        [r["example_question"]] if r.get("example_question") else []
    )
    return "<br><br>".join(esc(q) for q in qs if q)


def slug(domain: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")


def _row_html(cells: list[str], classes: list[str]) -> str:
    tds = "".join(
        f'<td class="{c}">{v}</td>' for c, v in zip(classes, cells, strict=True)
    )
    return f"    <tr>{tds}</tr>"


def render_domain_section_html(domain: str, rows: list[dict]) -> list[str]:
    out = [
        f'<section id="{slug(domain)}">',
        f"  <h2>{esc(domain)}</h2>",
        '  <div class="tablewrap"><table>',
        "    <thead><tr><th>KGs</th><th>Shared key</th>"
        '<th class="count">Count</th><th>Examples</th></tr></thead>',
        "    <tbody>",
    ]
    for r in rows:
        out.append(
            _row_html(
                [
                    esc(fmt_kgs(r)),
                    esc(clean_key(r["shared_key"])),
                    _num(r["verified_count"]),
                    fmt_examples_html(r),
                ],
                ["kgs", "key", "count", "examples"],
            )
        )
    out += ["    </tbody>", "  </table></div>", "</section>"]
    return out


def render_taxonomy_html(rows: list[dict]) -> list[str]:
    id_rows = sorted(
        (r for r in rows if r.get("match_type") == "id"), key=lambda r: r["kgs"]
    )
    label_rows = sorted(
        (r for r in rows if r.get("match_type") == "label"), key=lambda r: r["kgs"]
    )
    out = [
        f'<section id="{slug(TAXON_DOMAIN)}">',
        f"  <h2>{esc(TAXON_DOMAIN)}</h2>",
        f'  <p class="note">{esc(TAXON_INTRO)}</p>',
        '  <div class="tablewrap"><table>',
        '    <thead><tr><th>KGs</th><th class="count">exact_id</th>'
        '<th class="count">clade A-in-B / B-in-A</th><th>Examples</th></tr></thead>',
        "    <tbody>",
    ]
    for r in id_rows:
        a, b = r["kgs"][0], r["kgs"][-1]
        out.append(
            _row_html(
                [
                    esc(f"{a} × {b}"),
                    _num(r["exact_id"]),
                    f"{_num(r['clade_a_in_b'])} / {_num(r['clade_b_in_a'])}",
                    fmt_examples_html(r),
                ],
                ["kgs", "count", "count", "examples"],
            )
        )
    for r in label_rows:
        a, b = r["kgs"][0], r["kgs"][-1]
        out.append(
            _row_html(
                [
                    esc(f"{a} × {b} †"),
                    f"{_num(r['label_match'])} / {_num(r['kg_b_taxa'])}",
                    "—",
                    fmt_examples_html(r),
                ],
                ["kgs", "count", "count", "examples"],
            )
        )
    out += [
        "    </tbody>",
        "  </table></div>",
        f'  <p class="note">{esc(TAXON_FOOTNOTE)}</p>',
        f'  <p class="note">{esc(TAXON_CLOSING)}</p>',
        "</section>",
    ]
    return out


def render_html() -> str:
    rows = C.all_crosswalks(include_examples=True)
    verified_on = C.verified_on() or "unknown"

    domains: list[str] = []
    by_domain: dict[str, list[dict]] = {}
    for r in rows:
        by_domain.setdefault(r["domain"], []).append(r)
        if r["domain"] not in domains:
            domains.append(r["domain"])

    toc = "\n".join(
        f'    <li><a href="#{slug(d)}">{esc(d)} '
        f'<span class="n">{len(by_domain[d])}</span></a></li>'
        for d in domains
    )
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Proto-OKN Crosswalk Inventory</title>",
        "<style>",
        CSS.rstrip("\n"),
        "</style>",
        "</head>",
        "<body>",
        "<main>",
        "<h1>Proto-OKN Crosswalk Inventory</h1>",
        '<p class="meta">'
        f"<span>Verified {esc(verified_on)}</span>"
        "<span>claude-opus-4-8</span>"
        '<span><a href="https://apps.okn.us/federation/sparql">'
        "apps.okn.us/federation/sparql</a></span></p>",
        f'<p class="lede">All {len(rows)} precomputed cross-KG crosswalks (verified '
        f"through {esc(verified_on)}), grouped by domain. Each shows the knowledge "
        "graphs joined, the shared identifier, the verified overlap count, and "
        "example questions the join answers.</p>",
        '<ul class="toc">',
        toc,
        "</ul>",
        '<input id="filter" type="search" placeholder="Filter by KG, key, or question…" '
        'aria-label="Filter crosswalks">',
        '<p id="count"></p>',
    ]
    for domain in domains:
        if domain == TAXON_DOMAIN:
            lines += render_taxonomy_html(by_domain[domain])
        else:
            lines += render_domain_section_html(domain, by_domain[domain])
    lines += [
        "</main>",
        "<script>",
        JS.rstrip("\n"),
        "</script>",
        "</body>",
        "</html>",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    check = "--check" in sys.argv
    outputs = [(DOC, render()), (DOC_HTML, render_html())]
    if check:
        stale = [
            path
            for path, generated in outputs
            if (path.read_text(encoding="utf-8") if path.exists() else "") != generated
        ]
        if stale:
            names = ", ".join(str(p.relative_to(ROOT)) for p in stale)
            print(
                f"OUT OF DATE: {names} differs from crosswalks.json — run "
                "scripts/build_crosswalk_inventory.py"
            )
            sys.exit(1)
        print(f"up to date: {DOC.name}, {DOC_HTML.name} match crosswalks.json")
        return
    for path, generated in outputs:
        path.write_text(generated, encoding="utf-8")
    n = len(C.all_crosswalks(include_examples=False))
    print(
        f"wrote {DOC.relative_to(ROOT)} and {DOC_HTML.relative_to(ROOT)} — "
        f"{n} crosswalks across "
        f"{len({r['domain'] for r in C.all_crosswalks()})} domains"
    )


if __name__ == "__main__":
    main()

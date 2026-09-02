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

The HTML additionally links every example question to the transcript of the worked
example that answers it (``crosswalks_examples/*.md``, linked through GitHub's blob
view so the Markdown RENDERS — see :func:`blob_url`). Those links are re-derived
from ``crosswalks_example.md``'s catalog table on every build — see
:func:`transcript_links` — so renaming or dropping a transcript fails the build
loudly instead of shipping a dead link. A crosswalk with NO worked example yet
renders its questions as plain text and is reported on stderr, so a batch of newly
catalogued joins can ship before their transcripts are authored; a stem pointing at
no crosswalk row is still a hard error.
"""

from __future__ import annotations

import html
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "crosswalks" / "proto-okn-crosswalk-inventory.md"
DOC_HTML = DOC.with_suffix(".html")
CATALOG = ROOT / "docs" / "crosswalks" / "crosswalks_example.md"
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


# --------------------------------------------------------------------------- #
# Transcript links — resolved from the example catalog, not stored per row.     #
# --------------------------------------------------------------------------- #
#
# Every crosswalk has a worked, transcript-backed example PAIR (q1 + q2) under
# docs/crosswalks/crosswalks_examples/. The links live in ONE place —
# ``crosswalks_example.md``'s per-domain catalog table — and nothing in
# crosswalks.json points at them, so the inventory re-derives the row→transcript
# mapping here rather than duplicating a second list of paths.
#
# The catalog names a stem's KGs in prose (``BioHealthKG × ubergraph × GXA``) and
# its key descriptively (``UMLS ↔ UBERON (ubergraph)``), so a stem is matched to a
# crosswalk row by (domain, CORE KG set, shared-key tokens): core = the row's KGs
# minus the bridge hubs, which the catalog names inconsistently (some stems list
# ubergraph, some elide it). Ambiguity inside a domain is broken by key tokens
# (``MONDO<->OMIM`` vs ``MONDO<->Orphanet`` on the same KG pair).

CATALOG_KG_ALIAS = {
    "AOP-Wiki": "biobricks-aopwiki",
    "BioHealthKG": "biohealth",
    "BiomarkerKG": "biomarkerkg",
    "ClimateModelsKG": "climatemodelskg",
    "DreamKG": "dreamkg",
    "dreamkg": "dreamkg",
    "FIOKG": "fiokg",
    "GXA": "gene-expression-atlas-okn",
    "HydrologyKG": "hydrologykg",
    "ICE": "biobricks-ice",
    "MeSH": "biobricks-mesh",
    "NASA-GESDISC": "nasa-gesdisc-kg",
    "NCI-PID": "ncipidkg",
    "NDE": "nde",
    "NIKG": "nikg",
    "OARD": "oard-kg",
    "PanKgraph": "pankgraph",
    "ProKN": "prokn",
    "PubChem-annotations": "biobricks-pubchem-annotations",
    "RDKG": "rdkg",
    "RuralKG": "ruralkg",
    "SAWGraph": "sawgraph",
    "SCALES": "scales",
    "SOCKG": "sockg",
    "SPOKE": "spoke-okn",
    "spoke-okn": "spoke-okn",
    "SPOKE-GeneLab": "spoke-genelab",
    "SUDOKN": "sudokn",
    "SecureChainKG": "securechainkg",
    "SpatialKG": "spatialkg",
    "Tox21": "biobricks-tox21",
    "ToxCast": "biobricks-toxcast",
    "UFOKN": "ufokn",
    "Wikidata": "wikidata",
    "Wildlife-KN": "wildlifekn",
    "digcfdekg": "digcfdekg",
    "geoconnex": "geoconnex",
    "phaseskg": "phaseskg",
    "ubergraph": "ubergraph",
    # An illustrative list of downstream KGs in a title cell, not a join member.
    "RDKG/NDE/OARD/SPOKE": None,
}

# Bridge hubs: dropped from both sides before comparing KG sets (see above).
BRIDGE_KGS = {"ubergraph", "wikidata"}

# Catalog stem-id prefix -> crosswalk domain.
CATALOG_DOMAIN = {
    "AN": "Anatomy & Cell Type",
    "C": "Chemicals",
    "CJ": "Justice & Public Safety",
    "D": "Disease & phenotype",
    "EO": "Earth observation",
    "ET": "Environmental toxicology",
    "G": "Genes",
    "GEO": "Geospatial",
    "HY": "Hydrology",
    "I": "Industry & supply chain",
    "MF": "Function & Pathways",
    "P": "Proteins",
    "PUB": "Publications",
    "PW": "Function & Pathways",
    "SDOH": "Social Determinants & Services",
    "T": "Taxonomy",
}

# The three stems the KG-set match cannot resolve, all documented in
# crosswalks_example_notes.md: G03 works a 3-way clique row that was later dropped
# from the table (no row to link it to), and GEO26/GEO28 each work the
# sudokn×spatialkg pair from a wider transcript that also queries a third KG.
CATALOG_OVERRIDE: dict[str, tuple[tuple[str, ...], str] | None] = {
    "G03": None,
    "GEO26": (("spatialkg", "sudokn"), "state_FIPS"),
    "GEO28": (("spatialkg", "sudokn"), "S2_L13"),
}

# Words that describe HOW a key is reached, not WHICH key it is.
_KEY_STOPWORDS = {
    "a",
    "and",
    "assembled",
    "bridge",
    "bridged",
    "cell",
    "computed",
    "digit",
    "direct",
    "hop",
    "id",
    "in",
    "iri",
    "level",
    "literal",
    "name",
    "no",
    "of",
    "scoped",
    "the",
    "to",
    "two",
    "ubergraph",
    "via",
    "wikidata",
}


def _key_tokens(key: str | None) -> set[str]:
    text = (key or "").lower()
    for arrow in ("<->", "->", "↔", "→"):
        text = text.replace(arrow, " ")
    return {t for t in re.split(r"[^a-z0-9]+", text) if t and t not in _KEY_STOPWORDS}


def _core_kgs(kgs) -> tuple[str, ...]:
    return tuple(sorted(set(kgs) - BRIDGE_KGS))


def _parse_catalog() -> dict[str, dict]:
    """``{stem_id: {"domain", "kgs", "key", "paths": (q1, q2)}}`` from the catalog table."""
    stems: dict[str, dict] = defaultdict(dict)
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([A-Z]+)(\d+)-Q(\d)\s*\|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        link = re.search(r"\((crosswalks_examples/[^)]+\.md)\)", line)
        if not link:
            raise SystemExit(f"{CATALOG.name}: no transcript link on row {cells[0]!r}")
        prefix, stem_id, q = m.group(1), m.group(1) + m.group(2), int(m.group(3))
        kgs = []
        for raw in cells[2].split("×"):
            name = raw.strip().split("(")[0].strip().rstrip(")").strip()
            if name not in CATALOG_KG_ALIAS:
                raise SystemExit(
                    f"{CATALOG.name}: unknown KG name {name!r} ({stem_id})"
                )
            if CATALOG_KG_ALIAS[name]:
                kgs.append(CATALOG_KG_ALIAS[name])
        if prefix not in CATALOG_DOMAIN:
            raise SystemExit(f"{CATALOG.name}: unknown stem prefix {prefix!r}")
        stem = stems[stem_id]
        # Match on the Q1 row: a stem's Q2 row sometimes widens the KG cell to the
        # KGs its transcript touches (D18-Q2 lists the whole disease hub), which is
        # not the crosswalk's join membership.
        if q == 1 or "kgs" not in stem:
            stem.update(domain=CATALOG_DOMAIN[prefix], kgs=kgs, key=cells[3])
        stem.setdefault("paths", {})[q] = link.group(1)
    return dict(stems)


def transcript_links(rows: list[dict]) -> dict[tuple, list[tuple[str, str]]]:
    """Map each crosswalk row to its worked transcripts: ``{row_key: [(q1, q2), …]}``.

    ``row_key`` is ``(core KGs, shared_key)``. The value is a LIST because a row can
    carry more than one worked stem (spoke-genelab×spoke-okn on Entrez has two: the
    spaceflight gene-expression and DNA-methylation examples); the first pair is the
    row's primary example, the rest are extra worked examples.
    """
    by_domain_core: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        by_domain_core[(r["domain"], _core_kgs(r["kgs"]))].append(r)

    links: dict[tuple, list[tuple[str, str]]] = defaultdict(list)
    for stem_id, stem in sorted(_parse_catalog().items()):
        paths = stem["paths"]
        if sorted(paths) != [1, 2]:
            raise SystemExit(f"{CATALOG.name}: {stem_id} does not have both Q1 and Q2")
        if stem_id in CATALOG_OVERRIDE:
            target = CATALOG_OVERRIDE[stem_id]
            if target:
                links[target].append((paths[1], paths[2]))
            continue
        cands = by_domain_core.get((stem["domain"], _core_kgs(stem["kgs"])), [])
        if not cands:
            raise SystemExit(
                f"{CATALOG.name}: {stem_id} ({stem['domain']}, "
                f"{'+'.join(_core_kgs(stem['kgs']))}) matches no crosswalk row"
            )
        want = _key_tokens(stem["key"])
        best = max(cands, key=lambda r: len(_key_tokens(r["shared_key"]) & want))
        links[(_core_kgs(best["kgs"]), best["shared_key"])].append((paths[1], paths[2]))

    # A row with no worked example is REPORTED, not fatal: crosswalks are catalogued
    # (verified skeleton + two example questions) as soon as they are discovered, and
    # their transcripts are authored afterwards. The reverse — a catalog stem that
    # matches no row — stays fatal above, since that is a dead link or a dropped row.
    unlinked = [r for r in rows if (_core_kgs(r["kgs"]), r["shared_key"]) not in links]
    if unlinked:
        listing = "; ".join(
            f"{'+'.join(r['kgs'])} on {r['shared_key']}" for r in unlinked
        )
        print(
            f"note: {len(unlinked)} crosswalk(s) have no worked example in "
            f"{CATALOG.name} yet — questions render unlinked: {listing}",
            file=sys.stderr,
        )
    return links


def row_links(links: dict, r: dict) -> list[tuple[str, str]]:
    return links[(_core_kgs(r["kgs"]), r["shared_key"])]


# The page's real home is GitHub Pages, which serves a .md as text/markdown — a
# relative link there DOWNLOADS the transcript instead of showing it. Link to
# GitHub's blob view, which renders the Markdown.
BLOB_BASE = "https://github.com/sbl-sdsc/mcp-okn/blob/main/docs/crosswalks/"


def blob_url(path: str) -> str:
    """``crosswalks_examples/x.md`` (as written in the catalog) -> its blob URL."""
    return BLOB_BASE + path


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
a.q {
  color: inherit; text-decoration: none;
  border-bottom: 1px dotted color-mix(in srgb, var(--accent) 55%, transparent);
}
a.q:hover, a.q:focus { color: var(--accent); border-bottom-style: solid; }
.also { color: var(--muted); font-size: .87em; }
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


def fmt_examples_html(r: dict, links: dict) -> str:
    """Each question is a link to the transcript of the worked example that answers
    it (``crosswalks_examples/<stem>_q<n>_*.md``). A row with more than one worked
    stem gets its extra transcripts on a trailing muted line."""
    qs = r.get("example_questions") or (
        [r["example_question"]] if r.get("example_question") else []
    )
    pairs = row_links(links, r)
    # No worked example yet (a freshly catalogued crosswalk): render the questions
    # as plain text rather than linking them to a transcript that does not exist.
    primary = pairs[0] if pairs else ()
    cells = [
        f'<a class="q" href="{blob_url(p)}">{esc(q)}</a>'
        for q, p in zip(qs, primary, strict=False)
    ]
    cells += [esc(q) for q in qs[len(primary) :] if q]
    for extra in pairs[1:]:
        also = " · ".join(
            f'<a href="{blob_url(p)}">example {i}</a>' for i, p in enumerate(extra, 1)
        )
        cells.append(f'<span class="also">Also worked: {also}</span>')
    return "<br><br>".join(cells)


def slug(domain: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")


def _row_html(cells: list[str], classes: list[str]) -> str:
    tds = "".join(
        f'<td class="{c}">{v}</td>' for c, v in zip(classes, cells, strict=True)
    )
    return f"    <tr>{tds}</tr>"


def render_domain_section_html(domain: str, rows: list[dict], links: dict) -> list[str]:
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
                    fmt_examples_html(r, links),
                ],
                ["kgs", "key", "count", "examples"],
            )
        )
    out += ["    </tbody>", "  </table></div>", "</section>"]
    return out


def render_taxonomy_html(rows: list[dict], links: dict) -> list[str]:
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
                    fmt_examples_html(r, links),
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
                    fmt_examples_html(r, links),
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
    links = transcript_links(rows)

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
        "example questions the join answers. <strong>Every question links to the "
        "transcript</strong> of the worked example that answers it — the federated "
        "SPARQL, the rows it returned, and the reading.</p>",
        '<ul class="toc">',
        toc,
        "</ul>",
        '<input id="filter" type="search" placeholder="Filter by KG, key, or question…" '
        'aria-label="Filter crosswalks">',
        '<p id="count"></p>',
    ]
    for domain in domains:
        if domain == TAXON_DOMAIN:
            lines += render_taxonomy_html(by_domain[domain], links)
        else:
            lines += render_domain_section_html(domain, by_domain[domain], links)
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

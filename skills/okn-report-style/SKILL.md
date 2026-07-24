---
name: okn-report-style
description: >-
  Layout, figure, and style conventions for turning any OKN / mcp-okn federated-SPARQL case study
  into a polished, reproducible report deliverable — interactive HTML + Markdown + multi-sheet Excel
  + figures + maps. Domain-agnostic across the OKN federation's ~12 domains (environment & water,
  climate, agriculture, wildlife, justice, social services, infrastructure, supply chains, health &
  biomedicine, chemicals & toxicology, geospatial). Use when you HAVE analysis results (ranked
  entities, cross-KG hypothesis sets, geospatial or network output) and need to produce the
  write-up: a report or "map", figures with panels and legends, ranked results tables, maps, or an
  HTML report with embedded charts — or to FIX such artifacts (overlapping / tiny-font legends,
  out-of-order figures, a map that just plots raw lat/long, a too-long results table). NOT for
  answering questions about the federation itself (how to cite it, which KGs exist) — only for
  building or fixing the deliverable.
license: BSD-3-Clause
compatibility: >-
  Requires the mcp-okn MCP server (https://apps.okn.us/okn-mcp-dev/mcp) for the analysis it
  presents, plus Python with the plotting, Excel, and mapping libraries the bundled scripts import
  to render the HTML report, figures, workbook, and maps.
metadata:
  author: sbl-sdsc
  version: "0.1.0"
  repository: https://github.com/sbl-sdsc/mcp-okn
---

# OKN report style

Presentation conventions for OKN (`mcp-okn` federated-SPARQL) analysis reports, so every report
looks consistent and avoids the mechanical mistakes that are easy to make by hand (see **Common
failure modes** below). The rules are **domain-neutral** — adapt the section headings, figure
types, and vocabulary to the subject; the structure stays the same.

**Do the analysis first.** This skill is about *presentation*. Gather and verify all facts,
figures, statistics, and provenance before rendering. Then build the deliverables from the finished
numbers.

## Deliverable set

A complete report is a **folder**, not one file. **`<study>` is the folder's own name**, and every
file in it starts with that same token — `MS/MS_report.md`, `Bone-Health/Bone-Health_report.md` —
so the prefix is never something to look up, and a study is renamed by renaming one directory and
its files' first token. Do not use a descriptive variant (`spaceflight_bone_loss_…`) or an
abbreviation (`T2D_…`) that disagrees with the folder.

```
<study>/
├── <study>_report.md            # the written report — the SINGLE source of the prose
├── <study>_report.html          # self-contained interactive version, RENDERED FROM the .md
│                                 #   (same prose + KPI cards, embedded figures, interactive table, maps)
├── <study>_results.xlsx         # machine-readable multi-sheet workbook
├── figures/  fig1_*.png …        # one PNG per figure, numbered in document order
├── data/     *.tsv / *.json      # intermediate extracts (for reproducibility)
├── scripts/  *.py                # the exact scripts used (for reproducibility)
├── <study>_literature_comparison.md      # §8's per-claim record: one entry per checked claim,
│                                  #   its verdict (supported / partially / novel / contradicted)
│                                  #   and citations in the SAME §12 reference format (reuse the
│                                  #   report's §12 entry for any shared paper; every [N] resolves
│                                  #   here). A SIBLING deliverable — never inside data/, which
│                                  #   holds machine extracts, not prose.
└── <study>_reproducibility.md            # ONE file: replicator spec (rules, thresholds, joins,
                                  #   verified quantities, limitations) + verbatim supporting queries
                                  #   & row counts — from create_reproducibility_record (spec via appendix=)
```

Write working files to a scratch dir, then copy final artifacts into the delivered folder. Share
the HTML, MD and XLSX with the user via the file-presentation tool.

**One argument, authored once.** The `.md` is the single source of the report's *prose*; the `.html`
is **rendered from it**, never re-authored (see *Interactive HTML report*). Numbers likewise have a
single source: keep every volatile / headline figure in one **`stats.json`**, write it into the `.md`
as a **`{{key}}` placeholder**, and let the tooling fill it — `fill_stats(text, stats)` fills the
delivered `.md` (so it reads standalone), `build_report_from_markdown(..., stats=…)` fills the same
placeholders when rendering the `.html`, and `kpis_from_stats(stats, spec)` builds the KPI cards from
that dict. One edit in `stats.json` then updates the prose, the HTML, and the KPI cards at once. The
remaining
artifacts are deliberately **not** retellings of the report and must not be collapsed into it: the
`_reproducibility.md` leads with the **originating user prompt** (pass it VERBATIM as
`create_reproducibility_record`'s `prompt=`), then the replicator SPEC (rules, thresholds, joins,
verified quantities, limitations — passed as `appendix=`), then the **verbatim
SPARQL query text** that supports the findings, each with its row count (its unique payload — the
queries exist nowhere else and let the analysis audit standalone; full result data stays in the
`.xlsx` / `data/`), and the `.xlsx` is the **data**, not a narrative. Don't "deduplicate" either away.
The spec and the queries live in this ONE file — do not split them back into two.

## Report structure (Markdown)

Use this section order; **adapt headings and the analysis sections to the domain**. The full
section-by-section template — what each section must contain, the Sources/interactive-table specs, the
title block, and example figure legends — is **`references/report-structure.md`**; **read it before
writing the report.** Begin with a **title block** (a blockquote stating the domain framing — unit of
analysis, coverage, level of inference, the key caveat — plus an **Abbreviations** line). Then this
order, with the rules that must not be skipped. **The last two sections are always Reproducibility
then References, in that order** — Reproducibility sits immediately before References, nothing may
come between them, and nothing follows References:

1. **Executive summary** — headline result, key numbers, top entities.
2. **Sources used** — **REQUIRED in every report; never omit it.** One row per KG *actually queried*,
   and *only* those: a KG credited from an unlogged / exploratory / prior-knowledge source is a
   **phantom — cut it**. Every source must trace to a logged query.
3. **Design & rules** — narrate the selection rules / thresholds / joins for a reader; keep the exact
   replicator spec in the reproducibility file, not restated here.
4. **Confidence tiers** — how results are graded (A / B / C) and the tier distribution.
5. **Findings by axis** — one subsection per analysis axis, each with figure + legend + interpretation.
6. **Domain analyses** — the domain deep dives. **When an analysis is a family (e.g. GO *and* Reactome
   enrichment; several media / centralities), run every member OR state which you RAN vs deliberately
   SKIPPED, each with a one-line reason** — a silently dropped sub-analysis reads as full coverage.
7. **Discussion** — synthesise the axes; state implications / targets and the testable predictions.
8. **Comparison with prior work** — per-finding concordance with citations; needs the PubMed /
   Paperclip connectors (preflight them, or state §8 is omitted — never drop it silently). **Lead with a
   numbered `| # | Claim | Concordance |` table**, each cell a bolded label from the **closed six-term
   set** (SUPPORTED / PARTIALLY SUPPORTED / CONTRADICTED / MIXED / NOVEL / UNRESOLVED — no custom labels;
   qualifiers go in the description); head the column *Concordance*, never *Verdict*. The full per-claim
   record goes in `<study>_literature_comparison.md` (§8 links it as a **relative sibling** in the `.md`;
   the `.html` names companion docs rather than linking). Details + the deliverable-linking rules:
   `references/report-structure.md`.
9. **Full ranked results** — pointer to xlsx / tsv + the interactive HTML table + a prose slice.
10. **Summary of findings & limitations** — **always end the report here**: a findings recap, then the
    caveats as a numbered list. **This is the single home for the caveats list — don't duplicate it.**
11. **Reproducibility** — **one sentence and a link** to the single `_reproducibility.md`, naming
    what it contains; scripts in `scripts/`, extracts in `data/`. Do not restate the spec, list
    script filenames, repeat KG versions or give a timing line — the record holds all of it (it
    carries the header timing; pass `chat_started=` for whole-chat elapsed, else the active-query
    window). Token/cost isn't visible to the tooling — cite client figures or omit.
12. **References** — numbered, one fixed shape: `Author, et al. Title. *Journal*. Year. PMID:… ·
    [doi:…](…)`, plus ` — full-text-verified (<link>)` on entries read in full (the **PMC** id or a
    Paperclip line-anchored URL — never a bare marker). Fields from the NCBI `esummary`, not memory;
    percent-encode `(`/`)` in DOIs; test links (403 = bot-block, 404 = defect). **Preprints**: label
    `*<Server>* (preprint — not peer-reviewed)`, DOI alone is enough — check first for a peer-reviewed
    version. Full shape: `references/report-structure.md`.

**One kind of data, one place.** Group all results of the same kind into a *single* section — never
scatter the same data type (geolocation, an entity type, an enrichment family, a network output)
across sections; consolidate and cross-reference instead. Before finalising, scan the headings/figures
and merge any two that plot or tabulate the same kind of thing.

**Prose tone:** precise and hedged; attribute data sources; keep the framing caveat attached to every
downstream claim; prefer paragraphs over bullet-dumps. **Cross-reference** sections and figures ("see
§5.6", "consistent with Figure 3") so the report reads as one connected argument. Bold key entities and
headline numbers for scannability; never bold running prose.

## Figures — the rules that matter

The complete checklist is **`references/figure-checklist.md`** — run it for every figure. The
essentials:

- **Legend BELOW the figure, not inside the PNG** — reference each panel **(A)/(B)/(C)**, describe
  what's plotted, and state **provenance** (which KG / predicate / table). The PNG holds only a title,
  axis labels, and a compact color/marker key.
- **Interpret every figure and every table** — a 1–3 sentence takeaway after the legend. Legend =
  *what is shown and where from*; interpretation = *what to conclude*; keep it out of the PNG.
- **No in-plot overlap; readable fonts** (ticks ≥ 8 pt, axis labels ≥ 9 pt, titles ≥ 11 pt) — anchor
  legends outside the axes, then look at the rendered PNG and fix any collision.
- **Consistent, accessible encodings** — signed values → diverging map centred at zero (negative =
  blue, positive = red); sequential → single-hue ramp; colourblind-safe Okabe–Ito palette, never
  colour alone; show uncertainty (error bars / CI + sample size **n**).
- **Number figures in document order and match the filename** (`fig1_…`); renumber + rename on reorder.
- **Geographic data → a real OpenStreetMap-tiled map, never a bare lat/long scatter** — static via
  `osm_basemap(...)` (reproject to Web Mercator EPSG:3857), interactive via `folium_osm_map(...)`
  (clickable markers); keep the OSM attribution.
- **Verify:** always `Read` the rendered PNG back before embedding — the first matplotlib layout is
  often wrong.

**Use the bundled helper `scripts/okn_figstyle.py`** — call **`apply_style()`** first (it sets the
rcParams / font floors — importing alone does nothing), then use `legend_outside(ax, ...)`,
`panel_title(ax, "A", "…")`, `diverging_heatmap(...)`,
`ranked_barh(...)`, `osm_basemap(...)` / `folium_osm_map(...)` for maps, and
`finalize(fig, number, filename)` which saves at 150 dpi with tight margins. Reusing it keeps every
figure consistent and prevents the overlap / font mistakes. Run `python scripts/okn_figstyle.py
--demo` to see the chart helpers and `--demo-map` for the map helpers.

## Interactive HTML report

**Render the HTML *from* the Markdown report — never re-author the prose.** `report.md` is the single
source of the narrative; the `.html` is generated from it and adds only what Markdown can't express:
**KPI cards, base64-embedded figures, and the interactive results table.** Restating the report's
sections, figure legends, or interpretations as hand-written HTML is the **prose-drift** failure mode
— edit one file and the other silently disagrees. Rendering makes that drift structurally impossible.

Use **`build_report_from_markdown(md_path, out, kpis=…, table=…)`** in
`scripts/build_report_html.py`. It lifts the title / subtitle / date line from the `.md` title block,
renders the body (headings, tables, lists, blockquotes, inline markup), **base64-embeds every figure**
(a `![alt](figures/figN.png)` line followed by a blockquote becomes an `<img>` + `figcap` legend), and
**splices the interactive table** in wherever the `.md` contains a `<!-- RESULTS_TABLE -->` marker
(put that marker in §9). KPI cards and any maps' inline HTML are passed in / embedded — they are
chrome, not prose, so build the KPI cards from `stats.json` with `kpis_from_stats(stats, spec)` (never
retype the numbers) and pass `stats=` so any `{{key}}` placeholders in the prose are filled too. The result is a
**single self-contained `.html`** (inline CSS + JS, no external files) with a coloured header of **KPI
cards**, every figure as `<img>` + its `figcap` legend, maps embedded inline, and the ranked results
as an **interactive table** that is **sortable (click headers), filterable, and paginated** (default
25 rows/page with Prev/Next) — a 900-row table dumped in full is unreadable, so always paginate long
tables. (For a one-off HTML page with *no* Markdown source, the low-level `build_report(...)` /
`figure_block(...)` helpers remain — but a report always has a `.md`, so a report always renders from it.)

The results table has two required features:

- **A `sources (n)` corroboration column.** For every row show **how many federation KGs support
  it** (the count) plus a **pill per source** — the KG shortnames that contributed (e.g.
  `sawgraph`, `hydrologykg`, `spatialkg` for a water study; `scales`, `nikg` for a justice study;
  `prokn`, `rdkg` for a biomedical one). Make the count numeric-sortable so a reader can rank by
  cross-KG support, and add a one-line tip saying what each source contributes. Provenance at a
  glance is the point.
- **Pull-down menus that select the relevant subsets.** Beyond the free-text search box, give a
  `<select>` drop-down for each axis a reader will want to slice by — e.g. confidence tier,
  category / type, region or state, direction / sign, or any key flag. Each dropdown offers "all" +
  the distinct values and re-filters the table on change.

For **geographic data**, embed an interactive `folium` map (Leaflet + OpenStreetMap tiles) rather than
plotting bare coordinates — inline it with `folium_map_iframe(m)` (an `<iframe srcdoc>` wrapper), NOT
`m.get_root().render()` inlined raw: `render()` returns a whole `<!DOCTYPE><html>…</html>` document,
and splicing that into the body gives the file a second `<html>`/`<body>` that blanks every section
below it (`check_report_parity` now fails on that). Keep **every point
clickable** (a popup showing that point's attributes + source) and a legend below stating the
coordinate source.

**Use the bundled builder `scripts/build_report_html.py`.** Build the table fragment with
**`candidate_table(rows, columns, …)`** — the result rows (list of dicts) + column spec — then pass
it to **`build_report_from_markdown(md_path, out, kpis=…, table=…)`**, which renders the report body
from the `.md` and splices the table in at the `<!-- RESULTS_TABLE -->` marker. For the table, use
**`extra_filters=[(key, label), …]`** to generate the **subset pull-down menus** and
**`sources_col=(count_key, list_key)`** to render the **`sources (n)`** column (count + pills,
sorted by the count). It emits the sortable / filterable / paginated table and the whole page; see
`python scripts/build_report_html.py --demo-md` (render-from-Markdown) or `--demo` (low-level path).

**Never write your own HTML builder — always render through `build_report_from_markdown`.** Bypassing
the renderer (hand-authoring the body, or a one-off script fed raw HTML sections from memory) silently
ships a "highlights reel" that keeps the interesting claims and drops the mandatory sections. **Do not
copy the `docs/examples/*/build_html.py` scripts** — they predate this renderer and are the
anti-pattern (see `references/failure-modes.md`).

**Completeness gate — not "delivered" until you've seen `[check_report_parity] PASS`.**
`build_report_from_markdown` runs `check_report_parity(md_path, html_path)` automatically after writing;
read that line before presenting. If you built the HTML any other way, run it yourself
(`python scripts/build_report_html.py --check report.md report.html`) and see PASS first — it confirms
every heading is present and the visible word count is within `min_word_ratio` (0.85), FAILING and
naming the missing sections on a condensed build. Treat a FAIL (or never having run it) as blocking.

## Excel workbook

One workbook, multiple sheets: **Ranked Results** (the full table, tier-coloured, autofilter,
frozen header), plus one sheet per supporting analysis (inventory / cohort, each enrichment or
sub-analysis, any retrieved items, and a **Methods & Rules** sheet including an Abbreviations row).
Professional font (Arial), header fill, wrapped text. `openpyxl` is sufficient for results data
(not formulas); if you do add formulas, recalculate and check for errors.

## Common failure modes

The full catalog of real report failures and their fixes is **`references/failure-modes.md`** — skim
it before delivering, and read it in full for the two procedures that recur most (the hand-built
"highlights-reel" HTML and the dropped / diagram-bloated reproducibility transcript). The ones to keep
front of mind:

- **Hand-built / "highlights-reel" HTML** that silently drops mandatory sections (§2 Sources, §10
  Limitations, §8 Comparison, References…) → always render from the `.md` with
  `build_report_from_markdown` and see `[check_report_parity] PASS` before presenting. Do **not** copy
  `docs/examples/*/build_html.py` — those are the anti-pattern.
- **Phantom source** — a KG credited with no logged query behind it → cut it, or re-run the bridge
  query non-exploratory so it's in the transcript.
- **Numbers drifting** across `.md` / `.html` / `.xlsx` → single `stats.json` + `{{key}}` placeholders,
  filled by the tooling; grep the three artifacts to confirm they match.
- **Reproducibility transcript stubbed or bloated** — a stub (log too large) is a next step, not a stop:
  re-call with curated `supporting=[…]` indices. If per-query mermaid diagrams cause the bloat/spill,
  generate diagram-free (`include_query_diagrams=False`) then re-add via
  `scripts/readd_query_diagrams.py` — do BOTH halves and end on `[readd_query_diagrams] PASS`. Full
  defer-and-re-add recipe + the `--check` fidelity gate: **`references/failure-modes.md`**.
- **Figure problems** — legend/caption baked into the PNG, in-plot overlap, out-of-order numbering,
  bare lat/long scatter, same data split across sections → legend below, re-read the rendered PNG,
  renumber on reorder, use an OSM basemap, consolidate. (All expanded in the reference.)

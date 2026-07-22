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

A complete report is a **folder**, not one file:

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
│                                  #   and citations. A SIBLING deliverable — never inside data/,
│                                  #   which holds machine extracts, not prose.
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
order, with the rules that must not be skipped:

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
   Paperclip connectors (preflight them, or state §8 is omitted — never drop it silently). The
   full per-claim record goes in `<study>_literature_comparison.md`; §8 summarises it and
   **links to it** (absolute `https://github.com/<org>/<repo>/blob/main/…` URL — a relative
   link dies once the self-contained `.html` travels away from the repo).
9. **Full ranked results** — pointer to xlsx / tsv + the interactive HTML table + a prose slice.
10. **Summary of findings & limitations** — **always end the report here**: a findings recap, then the
    caveats as a numbered list. **This is the single home for the caveats list — don't duplicate it.**
11. **Reproducibility** — pointers to the single `_reproducibility.md`, the scripts, and pinned KG
    versions, plus the header timing line (pass `chat_started=` for whole-chat elapsed, else the
    active-query window). Token/cost isn't visible to the tooling — cite client figures or omit.
12. **References** — numbered; DOI link per literature item, line-anchored full-text link for anything
    verified against full text.

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

**Call `build_report_from_markdown` — do not write your own HTML builder.** This has been the single
most common — and most recurrent — way the deliverable breaks: not editing the `.md` and `.html` out
of sync, but bypassing the renderer entirely — hand-authoring the HTML body, or writing a one-off
script that takes report sections as **raw HTML strings** and fills in a condensed version from
memory. That silently ships a "highlights reel" — the interesting claims kept, and the
unglamorous-but-mandatory parts dropped (the **§2 Sources** table, **§3 Design & rules**, **§4
Confidence tiers**, **§7 Discussion**, **§8 Comparison with prior work** — the whole literature
validation — **§10 Limitations**, **§11 Reproducibility**, **§12 References**). The artifact everyone
opens then lacks exactly the provenance, the adversarial evidence, and the caveats. **There is never a
reason to hand-build:** `build_report_from_markdown` renders the *entire* `.md` faithfully and also
**self-verifies** (below), which a hand-built page does not. If you catch yourself writing `<h2>` tags
or a custom build script for a report, stop — you are about to ship a highlights reel.

> **Do NOT copy the `docs/examples/*/build_html.py` scripts — they are the anti-pattern, not the
> template.** Every one of them predates this renderer, hand-authors the HTML, and **FAILS
> `check_report_parity`** (the shipped example `.html`s carry only 22–71% of their `.md` and each drops
> 4–17 sections — including the mandatory Limitations / Caveats and the contradicting-evidence
> sections). A model that reads `docs/examples/` for a build template learns exactly the failure mode
> above — which is why this recurs. Ignore those `build_html.py` files; the **only** supported way to
> build a report's `.html` is `build_report_from_markdown`, and the same `.md` that fails parity
> hand-built **passes** (0 missing sections) when rendered through it.

**Completeness gate — the report is not "delivered" until you have seen `[check_report_parity] PASS`.**
`build_report_from_markdown` runs **`check_report_parity(md_path, html_path)`** automatically after
writing (it prints `[check_report_parity] PASS …`) — so if you used it, read that line before
presenting the report. If you built the HTML any other way, you MUST run it yourself
(`check_report_parity(md, html)` or `python scripts/build_report_html.py --check report.md
report.html`) and see PASS first. It confirms the HTML is the *same report*: every `##`/`###` heading
from the `.md` is present and the visible word count is within `min_word_ratio` (default 0.85). It
**FAILS**, naming the missing sections, on a dropped-section / condensed build — a check distinct from
self-containment / numbers / markup, all of which pass on an HTML that is a quarter of the report.
Treat a FAIL (or never having run it) as blocking: do not present the `.html` until parity PASSES.

## Excel workbook

One workbook, multiple sheets: **Ranked Results** (the full table, tier-coloured, autofilter,
frozen header), plus one sheet per supporting analysis (inventory / cohort, each enrichment or
sub-analysis, any retrieved items, and a **Methods & Rules** sheet including an Abbreviations row).
Professional font (Arial), header fill, wrapped text. `openpyxl` is sufficient for results data
(not formulas); if you do add formulas, recalculate and check for errors.

## Common failure modes (all seen in real reports)

- Legend overlapping a donut / pie or bar → move it out; regenerate; re-read the PNG.
- Figure caption text baked into the PNG → move to the legend below.
- Geographic points plotted as a bare lon/lat scatter on empty axes → put them on an OpenStreetMap
  basemap (static: `contextily`; interactive: `folium`) so the geography is legible.
- Figures out of numerical order after inserting a new one → renumber captions + files (enforced by
  `check_figure_numbering` inside the `check_report_parity` delivery gate — it FAILs on non-consecutive
  captions or filenames, so this can't ship silently).
- Same kind of data split across two+ sections (e.g. geolocation in two places) → consolidate into
  one section; cross-reference instead of repeating.
- **Sources used** section missing, or a queried KG absent from it → always include the table with a
  row per KG actually queried.
- Phantom source: a KG credited in the Sources table / as a pill though no logged query touched it
  (its "contribution" came from an exploratory or unlogged query) → drop it, or re-run the bridge
  query non-exploratory so it's in the transcript. Every source must trace to a logged query.
- **Reproducibility transcript left missing because `create_reproducibility_record` returned a stub**
  (the log was too large to return inline) → a stub is a next step, not a stopping point. Re-call with
  `supporting=[1, 5, 9, …]` (bare 1-based indices from `get_query_log`) to curate to the
  findings-supporting queries, or batch them (`list(range(1, 41))`, then `range(41, 81)`, …). Curating
  the real logged queries is not the forbidden fabrication — never ship the report with an empty or
  placeholder transcript.
- **Transcript bloated / spilling because of the per-query mermaid diagrams** — each ` ```sparql `
  block is followed by a ` ```mermaid ` diagram that duplicates it, and those diagrams are 25–50%+ of
  the bytes, which is often what pushes the return over the inline limit → **generate diagram-free,
  then re-add the diagrams as a postprocessing step** (both halves — generating lean and *not*
  re-adding silently drops the diagrams; that is an omission, not a choice):
  1. Call `create_chat_transcript` / `create_reproducibility_record` with
     **`include_query_diagrams=False`** (lean return, no stub/spill) and save the markdown.
  2. Re-add the diagrams with **`scripts/readd_query_diagrams.py <transcript.md>`** — the ONE-command
     front door for this half. It auto-selects the path: if `sparql-to-mermaid` is importable (a dev
     checkout) it generates every diagram and injects them in that single call; if not (the usual
     report session, since the package is mcp-okn-internal and **not pip-installable**) it writes the
     exact WORK-LIST of un-diagrammed queries to `<transcript.md>.queries.json` and exits non-zero so
     you can't mistake it for done. Turn that list into diagrams by calling the **`sparql_to_mermaid`
     TOOL** (available over MCP) on **each verbatim** query (never a shortened copy — a diagram under a
     SPARQL block it doesn't match is a fidelity break), save `[{sparql, mermaid}, …]` as
     `diagrams.json`, then re-run `python scripts/readd_query_diagrams.py <transcript.md> --diagrams
     diagrams.json --max-chars 4000` (dependency-free injection, idempotent). (The injection engine is
     `scripts/expand_query_diagrams.py`; the helper is a thin front door over it.)
  **Cap the diagrams** (`--max-chars 4000`, mirroring the server's `diagram_max_chars`): as of
  `sparql-to-mermaid` **v0.5.0** a long `VALUES` list collapses to "3 values + `+N more`" (the
  `max_values` default) **and** node labels are quoted, so the old symbol-list blowup — a 250-symbol
  query → a ~28K-char diagram of ~280 meaningless nodes — no longer happens, and an IRI with special
  characters (e.g. a Reactome / PubChem id containing `(`) no longer breaks Mermaid parsing; the cap
  stays as a backstop for any diagram that is still huge (e.g. very many distinct triples). (v0.5.0
  also adds an opt-in `portable=True` / `--portable` mode that compacts unknown IRIs to CURIEs for
  stricter renderers; the default output used here renders in Claude's Artifact renderer and current
  Mermaid, so you don't need it unless a specific viewer rejects a diagram.) Skipped diagrams get **noted in the transcript** (a one-line
  table), the same rule the server applies inline. Don't
  rasterize the mermaid to SVG/PNG — leave it as source. **This defer-and-re-add flow applies only when
  you still want the diagrams in the final file.** If the user asks for **no** query diagrams at all,
  pass `include_query_diagrams=False` (and `include_visualizations=False` for the schema classDiagrams)
  and **skip the re-add step** — don't re-inject what they asked to omit.
  **Completeness gate — the transcript is not "delivered" until `readd_query_diagrams.py --check
  <transcript.md>` prints `[readd_query_diagrams] PASS`** (every ```sparql block has a diagram). This
  mirrors the HTML's `check_report_parity` gate: `--check` verifies WITHOUT modifying and needs no
  package, so run it as the last step — a **FAIL means you generated lean and skipped the re-add**, the
  exact silent-drop this guards against. Treat FAIL (or never having run it) as blocking. (The only
  clean way to skip the gate is the user asking for no diagrams — then there are no ```sparql-without-
  diagram blocks to flag anyway.)
- No closing recap / limitations → end with **Summary of findings & limitations** (findings recap +
  numbered caveats).
- Undefined acronyms → add the Abbreviations block and expand each at first use.
- 900-row HTML table → paginate, and add the subset pull-downs + a search box.
- **Prose drifting between .md and .html** because the HTML re-states the report instead of rendering
  it (a section, figure legend, or interpretation edited in one file and now disagreeing with the
  other) → generate the `.html` FROM the `.md` with `build_report_from_markdown(...)`; never
  hand-author HTML prose that duplicates the Markdown. The `.md` is the single source of the prose.
- **HTML is a "highlights reel" missing whole sections** — a hand-authored HTML (or a custom builder
  fed raw HTML sections) that keeps the interesting claims but silently drops the mandatory,
  unglamorous ones (**§2 Sources**, **§10 Limitations**, Discussion, Reproducibility, References,
  Abbreviations). Self-containment / numbers / markup checks all pass on it — none asks whether it is
  the *same report* → render from the `.md`, and run **`check_report_parity(md, html)`** as the final
  gate (it FAILS naming the dropped sections when the HTML is shorter than the source).
- Numbers drifting between .md / .html / .xlsx after an edit → keep a single `stats.json`, reference
  each figure as a `{{key}}` placeholder, and let the tooling fill it (`fill_stats` for the delivered
  `.md`, `build_report_from_markdown(stats=…)` for the `.html`, `kpis_from_stats` for the KPI cards) so
  one edit propagates everywhere. Grep the three artifacts for the key figures to confirm they match.

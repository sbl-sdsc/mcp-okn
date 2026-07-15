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
├── <study>_report.md            # the written report (prose, tables, figure legends)
├── <study>_report.html          # self-contained interactive version (embedded figures + table + maps)
├── <study>_results.xlsx         # machine-readable multi-sheet workbook
├── figures/  fig1_*.png …        # one PNG per figure, numbered in document order
├── data/     *.tsv / *.json      # intermediate extracts (for reproducibility)
├── scripts/  *.py                # the exact scripts used (for reproducibility)
├── <study>_reproducibility_appendix.md   # rules, thresholds, joins, verified quantities
└── <study>_reproducibility_transcript.md # verbatim queries (from create_chat_transcript)
```

Write working files to a scratch dir, then copy final artifacts into the delivered folder. Share
the HTML, MD and XLSX with the user via the file-presentation tool.

## Report structure (Markdown)

Use this section order; **adapt headings and the analysis sections to the domain**. Full template +
example legends: **`references/report-structure.md`** (read it before writing the report).

**One kind of data, one place.** Group all results of the same kind into a *single* section — never
scatter the same data type across the report. A common mistake is splitting **geolocation / spatial
data** (or the same entity type, the same enrichment family, the same network output) across two or
three sections; consolidate it so the reader sees all of it together, then cross-reference from
elsewhere instead of repeating it. Before finalising, scan the section headings and figures: if two
sections plot or tabulate the same kind of thing (e.g. two maps, two enrichment tables), merge them.

Begin with a **title block** — a blockquote stating the non-negotiable framing for the domain (unit
of analysis, spatial / temporal coverage, level of inference, and the key caveat, e.g. *"hypothesis
generation, not causal / clinical inference"*, *"observational associations over county-level
data"*, *"model output, not measurements"*) and an **Abbreviations** line defining every acronym.
Then:

1. **Executive summary** — the headline result, the key numbers, the top results / entities.
2. **Sources used** — **REQUIRED in every report; never omit it.** Table of KGs queried (name,
   version, **last-updated date**, role, join key / confidence — `get_kg_version` supplies the
   version + last-updated date for each KG; show the date as **YYYY-MM-DD only**, truncating the
   ISO-8601 timestamp). If the analysis touched a KG, it gets a row — a report with no Sources table,
   or one that omits a KG the queries actually hit, is incomplete. **The rule runs both ways: a KG may
   appear ONLY if it was actually queried** (it has logged queries in the transcript). Do not list a
   KG — in the Sources table or as a `sources (n)` pill — whose contribution came from an
   unlogged / exploratory query or from prior knowledge. Every source and every cross-KG claim must
   trace to a logged query; if a bridge graph (e.g. `ubergraph` supplying a DOID→MONDO equivalence)
   is credited, the query that used it must be in the transcript, or it is a phantom source — cut it.
3. **Design & rules** — the exact selection rules, thresholds, join keys, and an inventory / cohort
   table rebuilt live with verified counts.
4. **Confidence tiers** — how results are graded (A / B / C) and what evidence each tier requires.
5. **Findings by axis** — one subsection per analysis axis, each with its figure + legend + a short
   interpretation of the result. The axes depend on the domain (e.g. per-group signal, spatial
   clustering / hot-spots, temporal trend, cross-KG corroboration, category enrichment, network
   centrality, exposure↔outcome linkage).
6. **Domain analyses** — the domain-specific deep dives with figures. Include only those the
   question needs; examples across the federation: category / functional enrichment; pathway or
   network analysis; geospatial hot-spot mapping; supply-chain or dependency tracing; exposure or
   flood modelling; facility / provider inventories.
7. **Discussion** — synthesise the axes into a coherent picture; state the **implications /
   recommendations / targets** (interventions, priority sites, candidate targets, mitigations,
   at-risk entities — flagged by evidence strength); and name the testable predictions.
8. **Comparison with prior work** — concordance per finding, with citations, wherever a literature
   or reference source is available for the domain. Name the retrieval tool (e.g. PubMed / Paperclip)
   and mark which central claims were **verified against full text**.
9. **Full ranked results** — pointer to xlsx / tsv + the interactive HTML table + a representative
   slice in the prose.
10. **Summary of findings & limitations** — **the closing narrative section; always end the report
    here.** Two parts: (a) a concise recap of the key findings — the headline result and the top
    entities, restated in a few sentences so a reader who skips to the end gets the whole story; and
    (b) the caveats, uncertainties, and likely undercounts as a numbered list, explicit about what
    the data cannot support. This is where the standalone caveats list lives — do not also put one
    elsewhere.
11. **Reproducibility** — pointers to the appendix, the query transcript, the scripts, and the
    pinned KG versions + update dates.
12. **References** — numbered; attribute the retrieval tool, give a **DOI link** per literature item
    (e.g. PubMed) and a **full-text, line-anchored link** (e.g. Paperclip `citations.gxl.ai/…#Lxx`)
    for anything verified against full text.

**Prose tone:** precise and hedged; attribute data sources; keep the framing caveat attached to
every downstream claim; prefer paragraphs over bullet-dumps in the narrative. **Cross-reference**
sections and figures ("see §5.6", "consistent with Figure 3") so the report reads as one connected
argument, not disconnected sections. Use **emphasis sparingly and consistently** — bold key entities
(e.g. genes, sites, chemicals, categories) and headline numbers so they are scannable, but never
bold running prose or whole sentences.

## Figures — the rules that matter

Read **`references/figure-checklist.md`** for the complete checklist. The essentials, and *why*:

- **Every figure gets a legend BELOW it**, not inside it. Reference each panel — **(A)**, **(B)**,
  **(C)** — describe what is plotted, and state **provenance** (which KG / predicate / table the
  data came from). Figures are viewed standalone, so the legend must stand alone too.
- **Do not put explanatory text inside the figure.** A short title + axis labels + a color/marker
  key belong in the plot; the *description + provenance* go in the legend beneath it; the
  *interpretation* goes in a short paragraph after the legend (see next rule). If you catch yourself
  adding a footnote sentence to the PNG, move it out.
- **Interpret every figure and every table.** Immediately after a figure's legend — and immediately
  after every table — add a short interpretation (1–3 sentences) saying what the result *means*: the
  takeaway, the pattern to notice, and any caveat. The legend / caption says *what is shown and where
  it came from*; the interpretation says *what to conclude*. Keep the two separate, and keep
  interpretation out of the PNG.
- **In-plot keys/legends must never overlap the plot.** Anchor legends outside the axes
  (`loc=..., bbox_to_anchor=...`), shrink/shift pies & donuts (`radius`, `center`), widen panels
  (`width_ratios`, `wspace`), and leave margins. After drawing, look at the rendered PNG and fix
  any overlap — don't trust the first layout.
- **Fonts must be readable.** Floors: ticks/annotations ≥ 8 pt, axis labels ≥ 9 pt, titles ≥ 11 pt.
  Small multiples shrink text fast — check the rendered image at final size.
- **Number figures in document order** (Figure 1, 2, 3 … as they appear top-to-bottom) and make the
  **filename match** (`fig1_…`, `fig2_…`). If you reorder sections, renumber the figures and files.
- **Consistent conventions:** for **signed values** (e.g. log2 fold-change, change-vs-baseline,
  anomalies, z-scores) use a diverging map centred at zero (negative = blue, positive = red); for
  sequential magnitudes use a single-hue ramp; label colorbars with units; colour grouped bars by
  category with a legend; annotate bars with the value + counts.
- **Show uncertainty and stay colourblind-safe.** Put error bars / CIs and the sample size **n** on
  estimates; use the colourblind-safe `THEME` palette (Okabe–Ito) for categories and never encode a
  category by colour alone — pair colour with a label, marker, or order.
- **Geographic / spatial data → a real map on an OpenStreetMap basemap, never a bare lat/long
  scatter** (many OKN domains are geospatial). Plot points/polygons over OSM tiles so place context
  is legible: static PNG via `osm_basemap(...)` (`geopandas` + `contextily`, reprojected to Web
  Mercator EPSG:3857), interactive via `folium_osm_map(...)`, whose markers are **clickable** by
  default (a popup of the point's attributes + a hover tooltip). Fit the extent to the data and keep
  the OSM attribution. Full detail: the maps section of `references/figure-checklist.md`.
- **Verify.** Always `Read` the rendered PNG back and confirm no overlaps, legible fonts, correct
  panel letters, and sequential numbers before embedding it.

**Use the bundled helper `scripts/okn_figstyle.py`** — call **`apply_style()`** first (it sets the
rcParams / font floors — importing alone does nothing), then use `legend_outside(ax, ...)`,
`panel_title(ax, "A", "…")`, `diverging_heatmap(...)`,
`ranked_barh(...)`, `osm_basemap(...)` / `folium_osm_map(...)` for maps, and
`finalize(fig, number, filename)` which saves at 150 dpi with tight margins. Reusing it keeps every
figure consistent and prevents the overlap / font mistakes. Run `python scripts/okn_figstyle.py
--demo` to see the chart helpers and `--demo-map` for the map helpers.

## Interactive HTML report

Build a **single self-contained `.html`** (inline CSS + JS, figures embedded as base64 — no
external files). Structure: a coloured header with **KPI cards**, `card`/`note` callout boxes,
each figure as `<img>` + a `figcap` legend div **followed by a short interpretation paragraph**, any
maps embedded inline, and the ranked results as
an **interactive table** that is **sortable (click headers), filterable, and paginated** (default
25 rows/page with Prev/Next) — a 900-row table dumped in full is unreadable, so always paginate long
tables.

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

For **geographic data**, embed an interactive `folium` map (Leaflet + OpenStreetMap tiles) — write
it inline with `m.get_root().render()` rather than plotting bare coordinates — with **every point
clickable** (a popup showing that point's attributes + source) and a legend below stating the
coordinate source.

**Use the bundled builder `scripts/build_report_html.py`** — pass a title, KPI list, section
HTML blocks (figures auto-embedded as base64), and the result rows (list of dicts) + column spec.
Use **`extra_filters=[(key, label), …]`** to generate the **subset pull-down menus** and
**`sources_col=(count_key, list_key)`** to render the **`sources (n)`** column (count + pills,
sorted by the count). It emits the sortable / filterable / paginated table and the whole page; see
`python scripts/build_report_html.py --demo`.

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
- Figures out of numerical order after inserting a new one → renumber captions + files.
- Same kind of data split across two+ sections (e.g. geolocation in two places) → consolidate into
  one section; cross-reference instead of repeating.
- **Sources used** section missing, or a queried KG absent from it → always include the table with a
  row per KG actually queried.
- Phantom source: a KG credited in the Sources table / as a pill though no logged query touched it
  (its "contribution" came from an exploratory or unlogged query) → drop it, or re-run the bridge
  query non-exploratory so it's in the transcript. Every source must trace to a logged query.
- No closing recap / limitations → end with **Summary of findings & limitations** (findings recap +
  numbered caveats).
- Undefined acronyms → add the Abbreviations block and expand each at first use.
- 900-row HTML table → paginate, and add the subset pull-downs + a search box.
- Numbers drifting between .md / .html / .xlsx after an edit → keep a single `stats.json` and
  regenerate; grep the three artifacts for the key figures to confirm they match.

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
├── <study>_reproducibility_appendix.md   # rules, thresholds, joins, verified quantities
└── <study>_reproducibility_transcript.md # verbatim supporting queries + row counts (from create_reproducibility_record)
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
`_reproducibility_transcript.md` carries the **verbatim SPARQL query text** that supports the findings,
each with its row count (its unique payload, from `create_reproducibility_record` — the queries exist
nowhere else and let the analysis audit standalone; full result data stays in the `.xlsx` / `data/`),
and the `.xlsx` is the **data**, not a narrative. Don't "deduplicate" either away.

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
   (When you curate `create_reproducibility_record`'s `supporting` set, keep every query a credited
   source depends on — leaving one out trips the same phantom-source guard.)
3. **Design & rules** — *narrate* the selection rules, headline thresholds, and join keys for a
   reader, plus an inventory / cohort table rebuilt live with verified counts. Keep the exact
   replicator-grade specification (every join key, exact backgrounds, scoring formulas) in the
   reproducibility appendix and cross-reference it — don't restate the thresholds in both places.
4. **Confidence tiers** — how results are graded (A / B / C) and what evidence each tier requires.
5. **Findings by axis** — one subsection per analysis axis, each with its figure + legend + a short
   interpretation of the result. The axes depend on the domain (e.g. per-group signal, spatial
   clustering / hot-spots, temporal trend, cross-KG corroboration, category enrichment, network
   centrality, exposure↔outcome linkage).
6. **Domain analyses** — the domain-specific deep dives with figures. Include those the question
   needs; examples across the federation: category / functional enrichment; pathway or
   network analysis; geospatial hot-spot mapping; supply-chain or dependency tracing; exposure or
   flood modelling; facility / provider inventories. **When an analysis has a natural family of
   members** (e.g. GO *and* Reactome enrichment; multiple exposure media; several network centralities),
   **run all of them, or state explicitly which you RAN and which you deliberately SKIPPED, each with a
   one-line reason.** "Include only those that apply" is not a license to silently drop half a
   deliverable — a missing sub-analysis has no loud tripwire, so make the omission explicit or it reads
   as "covered everything."
7. **Discussion** — synthesise the axes into a coherent picture; state the **implications /
   recommendations / targets** (interventions, priority sites, candidate targets, mitigations,
   at-risk entities — flagged by evidence strength); and name the testable predictions.
8. **Comparison with prior work** — concordance per finding, with citations, wherever a literature
   or reference source is available for the domain. Name the retrieval tool (e.g. PubMed / Paperclip)
   and mark which central claims were **verified against full text**. **Preflight:** this section needs
   the **PubMed** (`https://pubmed.mcp.claude.com/mcp`) and **Paperclip** (`https://paperclip.gxl.ai/mcp`)
   MCP connectors — confirm they're available *before* writing it (look for tools named `pubmed` /
   `paperclip`). If one is missing, either enable it (claude.ai → Settings → Connectors, or Claude Code
   `claude mcp add --transport http <name> <url>` then reconnect) or state §8 is **omitted because the
   connector isn't enabled** — never drop it silently. (okn-bioanalysis carries the full preflight.)
9. **Full ranked results** — pointer to xlsx / tsv + the interactive HTML table + a representative
   slice in the prose.
10. **Summary of findings & limitations** — **the closing narrative section; always end the report
    here.** Two parts: (a) a concise recap of the key findings — the headline result and the top
    entities, restated in a few sentences so a reader who skips to the end gets the whole story; and
    (b) the caveats, uncertainties, and likely undercounts as a numbered list, explicit about what
    the data cannot support. This is where the standalone caveats list lives — do not also put one
    elsewhere.
11. **Reproducibility** — pointers to the appendix, the query transcript, the scripts, and the
    pinned KG versions + update dates. Include the **study active window** — the `- **Study active
    window:**` line `create_reproducibility_record` puts in the record header (first→last logged-query
    wall-clock; a lower bound, it excludes framing before the first query and writing after the last).
    Token/cost usage is **not** visible to the tooling (the server only sees tool calls), so if you
    report it, take the figures from the client (Claude Code `/cost` / the API `usage`) and label them
    as client-measured — never fabricate a token count.
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

For **geographic data**, embed an interactive `folium` map (Leaflet + OpenStreetMap tiles) — write
it inline with `m.get_root().render()` rather than plotting bare coordinates — with **every point
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
- Figures out of numerical order after inserting a new one → renumber captions + files.
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
  2. Re-add the diagrams with **`scripts/expand_query_diagrams.py`**. The `sparql-to-mermaid` package
     is mcp-okn-internal (**not pip-installable**), so it usually can't be imported where you build the
     report — but the **`sparql_to_mermaid` TOOL** is available over MCP. For **each logged query**
     call that tool on the **verbatim** query (never a shortened copy — a diagram under a SPARQL block
     it doesn't match is a fidelity break), collect `[{sparql, mermaid}, …]` into `diagrams.json`, then
     `python scripts/expand_query_diagrams.py <transcript.md> --diagrams diagrams.json --max-chars 4000`
     (dependency-free injection, idempotent).
  **Cap the diagrams** (`--max-chars 4000`, mirroring the server's `diagram_max_chars`): as of
  `sparql-to-mermaid` **v0.4.0** a long `VALUES` list collapses to "5 values + `+N more`" (the
  `max_values` default), so the old symbol-list blowup — a 250-symbol query → a ~28K-char diagram of
  ~280 meaningless nodes — no longer happens; the cap stays as a backstop for any diagram that is still
  huge (e.g. very many distinct triples). Skipped diagrams get **noted in the transcript** (a one-line
  table), the same rule the server applies inline. Don't
  rasterize the mermaid to SVG/PNG — leave it as source. **This defer-and-re-add flow applies only when
  you still want the diagrams in the final file.** If the user asks for **no** query diagrams at all,
  pass `include_query_diagrams=False` (and `include_visualizations=False` for the schema classDiagrams)
  and **skip the re-add step** — don't re-inject what they asked to omit.
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

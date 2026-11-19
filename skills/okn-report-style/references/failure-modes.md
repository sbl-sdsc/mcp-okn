# Common failure modes (all seen in real reports)

Skim this before delivering a report. Each is a mistake that shipped in a real deliverable, with its
fix. The most damaging — a hand-built "highlights-reel" HTML and an incomplete reproducibility
notebook — have their full procedures at the end.

- Legend overlapping a donut / pie or bar → move it out; regenerate; re-read the PNG.
- Figure caption text baked into the PNG → move to the legend below.
- Geographic points plotted as a bare lon/lat scatter on empty axes → put them on a street
  basemap (static: `contextily`; interactive: `folium`) so the geography is legible.
- Map tiles read "Access blocked … OpenStreetMap's volunteer-run servers" → the basemap is OSM's own
  tile server, which rejects Referer-less requests (file:// reports, contextily). Rebuild with the
  helpers' default Esri World Street Map (`okn_figstyle.BASEMAP_TILES`).
- Interactive map shows only a colour bar and attribution, no basemap or shapes (in a saved HTML
  file and in the notebook) → it's a plotly tile map (`Choroplethmap`/`Scattermap`, `*_map`/`*mapbox`),
  whose WebGL worker can't load from file:// or an iframe. Rebuild it with folium on
  `BASEMAP_TILES` (one `GeoJson` + a `setStyle` drop-down for several layers).
- Figures out of numerical order after inserting a new one → renumber captions + files (enforced by
  `check_figure_numbering` inside the `check_report_parity` delivery gate — it FAILs on non-consecutive
  captions or filenames, so this can't ship silently).
- Same kind of data split across two+ sections (e.g. geolocation in two places) → consolidate into
  one section; cross-reference instead of repeating.
- **Sources used** section missing, or a queried KG absent from it → always include the table with a
  row per KG actually queried.
- Phantom source: a KG credited in the Sources table / as a pill though no logged query touched it
  (its "contribution" came from an exploratory or unlogged query) → drop it, or re-run the bridge
  query non-exploratory so it's in the session log (and so in the notebook). Every source must trace
  to a logged query.
- No closing recap / limitations → end with **Summary of findings & limitations** (findings recap +
  numbered caveats).
- Undefined acronyms → add the Abbreviations block and expand each at first use.
- 900-row HTML table → paginate, and add the subset pull-downs + a search box.
- **Prose drifting between .md and .html** because the HTML re-states the report instead of rendering
  it (a section, figure legend, or interpretation edited in one file and now disagreeing with the
  other) → generate the `.html` FROM the `.md` with `build_report_from_markdown(...)`; never
  hand-author HTML prose that duplicates the Markdown. The `.md` is the single source of the prose.
- Numbers drifting between .md / .html / .xlsx after an edit → keep a single `stats.json`, reference
  each figure as a `{{key}}` placeholder, and let the tooling fill it (`fill_stats` for the delivered
  `.md`, `build_report_from_markdown(stats=…)` for the `.html`, `kpis_from_stats` for the KPI cards) so
  one edit propagates everywhere. Grep the three artifacts for the key figures to confirm they match.

## HTML is a "highlights reel" missing whole sections

A hand-authored HTML (or a custom builder fed raw HTML sections) that keeps the interesting claims but
silently drops the mandatory, unglamorous ones (**§2 Sources**, **§3 Design & rules**, **§4 Confidence
tiers**, **§7 Discussion**, **§8 Comparison with prior work**, **§10 Limitations**, **§11
Reproducibility**, **§12 References**, Abbreviations). Self-containment / numbers / markup checks all
pass on it — none asks whether it is the *same report*.

Fix → render from the `.md` with `build_report_from_markdown(...)`, and run
**`check_report_parity(md, html)`** as the final gate (it FAILS naming the dropped sections when the
HTML is shorter than the source).

> **Do NOT copy the `docs/examples/*/build_html.py` scripts — they are the anti-pattern, not the
> template.** Every one of them predates this renderer, hand-authors the HTML, and **FAILS
> `check_report_parity`** (the shipped example `.html`s carry only 22–71% of their `.md` and each drops
> 4–17 sections — including the mandatory Limitations / Caveats and the contradicting-evidence
> sections). A model that reads `docs/examples/` for a build template learns exactly this failure mode
> — which is why it recurs. Ignore those `build_html.py` files; the **only** supported way to build a
> report's `.html` is `build_report_from_markdown`, and the same `.md` that fails parity hand-built
> **passes** (0 missing sections) when rendered through it.

**Completeness gate — the report is not "delivered" until you have seen `[check_report_parity] PASS`.**
`build_report_from_markdown` runs `check_report_parity(md_path, html_path)` automatically after writing
(it prints `[check_report_parity] PASS …`) — so if you used it, read that line before presenting. If
you built the HTML any other way, you MUST run it yourself (`check_report_parity(md, html)` or
`python scripts/build_report_html.py --check report.md report.html`) and see PASS first. It confirms
every `##`/`###` heading from the `.md` is present and the visible word count is within `min_word_ratio`
(default 0.85). Treat a FAIL (or never having run it) as blocking.

## Reproducibility notebook incomplete, unrendered, or not re-runnable

The record is the `<study>_notebook/` folder from `create_jupyter_notebook` (SKILL.md *Deliverable
set*). `validate_okn_report.py` checks it, but these are the ways it goes wrong:

- **`files` withheld because the folder is too large** (hosted server, over `max_inline_chars`) → a
  next step, not a stop. Curate `supporting=[1, 5, 9, …]` (1-based indices from `get_query_log`) to the
  queries the findings rest on, keeping every query a credited source depends on (dropping one trips
  the phantom-source guard). If it is still too large, pass `include_data=False`: the notebook then
  re-runs its queries live, and so does `html_command`. When the server runs locally (stdio), pass
  `output_dir` instead; the server writes the folder itself and there is no size limit.
- **A file not saved, or a figure not copied** (hosted server) → save every `files` entry verbatim
  under `<study>/<study>_notebook/` and copy each `figures_to_copy` image to its path. Never retype or
  summarize a file. The validator checks every file `queries/manifest.json` lists and every image the
  notebook shows.
- **The notebook shows every figure at the end, without legends** (one cell runs a build-all-figures
  script, another loops over `figures/*.png`), **or each figure is a one-line call** (`BF.fig3()`)
  into a script the reader never sees → put each figure's plotting code in its own code cell, in
  report order, ending in `F.finalize(fig, N, path)` (it shows the saved PNG inside Jupyter), and
  follow it with a markdown cell holding the report's numbered legend. Keep only reusable helpers
  (statistics, styling) in `code_files`.
- **The notebook only re-runs the queries.** If the analysis that turns query rows into the reported
  numbers lives only in `scripts/` or in your head, the notebook cannot reproduce the findings. Pass
  that code as `code_files` (e.g. `{"analysis.py": …}`) and the cells that call it on `data["q01"]` …
  as `cells`, so running the notebook recomputes the headline numbers and regenerates the figures.
- **The spec is missing or split off.** The replicator specification (rules, thresholds, joins,
  verified quantities, limitations) goes in the notebook as the first markdown cell of `cells`, headed
  `## Replicator specification`. A separate `_reproducibility.md`, transcript or spec file beside the
  notebook is a second record that drifts from the first; the validator rejects it.
- **No HTML page, or a stale one** → run the tool's `html_command` after the folder is saved. If it
  fails, read the error: it is almost always an analysis cell raising. Fix the code, regenerate the
  notebook (`overwrite=True` for a local write), and run `html_command` again. Never hand-edit the
  `.ipynb` or produce the page any other way. If you cannot run shell commands, give the user
  `html_command` and say the package is incomplete until it has run.
- **Jupyter leftovers** — opening the notebook in Jupyter leaves `__pycache__/` and
  `.ipynb_checkpoints/` in its folder. Delete them before delivering; the validator fails on both.
- **Provenance missing** — the notebook header carries `model=`, `skills=` and
  `external_mcp_servers=` exactly as passed. A forgotten argument is fixed by regenerating the
  notebook, never by editing its header cell.

# Common failure modes (all seen in real reports)

Skim this before delivering a report. Each is a mistake that shipped in a real deliverable, with its
fix. The most damaging — a hand-built "highlights-reel" HTML and a dropped reproducibility
transcript — have their full procedures at the end.

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

## Reproducibility transcript dropped, stubbed, or diagram-bloated

**Left missing because `create_reproducibility_record` returned a stub** (the log was too large to
return inline) → a stub is a next step, not a stopping point. Re-call with `supporting=[1, 5, 9, …]`
(bare 1-based indices from `get_query_log`) to curate to the findings-supporting queries, or batch them
(`list(range(1, 41))`, then `range(41, 81)`, …). Curating the real logged queries is not the forbidden
fabrication — never ship the report with an empty or placeholder transcript.

**Transcript bloated / spilling because of the per-query mermaid diagrams** — each ` ```sparql ` block
is followed by a ` ```mermaid ` diagram that duplicates it, and those diagrams are 25–50%+ of the
bytes, which is often what pushes the return over the inline limit → **generate diagram-free, then
re-add the diagrams as a postprocessing step** (do BOTH halves — generating lean and *not* re-adding
silently drops the diagrams; that is an omission, not a choice):

1. Call `create_chat_transcript` / `create_reproducibility_record` with **`include_query_diagrams=False`**
   (lean return, no stub/spill) and save the markdown.
2. Re-add the diagrams with **`scripts/readd_query_diagrams.py <transcript.md>`** — the ONE-command
   front door for this half. It auto-selects the path: if `sparql-to-mermaid` is importable (a dev
   checkout) it generates every diagram and injects them in that single call; if not (the usual report
   session, since the package is mcp-okn-internal and **not pip-installable**) it writes the exact
   WORK-LIST of un-diagrammed queries to `<transcript.md>.queries.json` and exits non-zero so you can't
   mistake it for done. Turn that list into diagrams by calling the **`sparql_to_mermaid` TOOL**
   (available over MCP) on **each verbatim** query (never a shortened copy, and never a hand-drawn or
   paraphrased diagram — the diagram must be the tool's exact output; anything else is a fidelity break
   the `--check` gate now rejects), save `[{sparql, mermaid}, …]` as `diagrams.json`, then re-run
   `python scripts/readd_query_diagrams.py <transcript.md> --diagrams diagrams.json --max-chars 4000`
   (dependency-free injection, idempotent). (The injection engine is `scripts/expand_query_diagrams.py`;
   the helper is a thin front door over it.) Do **not** write a bespoke per-study script that emits
   diagram strings — that bypass is exactly what once shipped diagrams missing their KG box.

**Cap the diagrams** (`--max-chars 4000`, mirroring the server's `diagram_max_chars`): as of
`sparql-to-mermaid` **v0.5.0** a long `VALUES` list collapses to "3 values + `+N more`" (the
`max_values` default) **and** node labels are quoted, so the old symbol-list blowup — a 250-symbol
query → a ~28K-char diagram of ~280 meaningless nodes — no longer happens, and an IRI with special
characters (e.g. a Reactome / PubChem id containing `(`) no longer breaks Mermaid parsing; the cap stays
as a backstop for any diagram that is still huge (e.g. very many distinct triples). (v0.5.0 also adds an
opt-in `portable=True` / `--portable` mode that compacts unknown IRIs to CURIEs for stricter renderers;
the default output used here renders in Claude's Artifact renderer and current Mermaid, so you don't
need it unless a specific viewer rejects a diagram.) Skipped diagrams get **noted in the transcript** (a
one-line table), the same rule the server applies inline. Don't rasterize the mermaid to SVG/PNG — leave
it as source.

**This defer-and-re-add flow applies only when you still want the diagrams in the final file.** If the
user asks for **no** query diagrams at all, pass `include_query_diagrams=False` (and
`include_visualizations=False` for the schema classDiagrams) and **skip the re-add step** — don't
re-inject what they asked to omit.

**Completeness + fidelity gate — the transcript is not "delivered" until `readd_query_diagrams.py
--check <transcript.md>` prints `[readd_query_diagrams] PASS`.** It checks two things, WITHOUT modifying
and with no package needed: **(a) presence** — every ```sparql block has a ```mermaid diagram (a FAIL
here means you generated lean and skipped the re-add); and **(b) fidelity** — every query scoped to a
named `GRAPH` has a diagram carrying the `subgraph ["GRAPH …"]` box that `sparql_to_mermaid` always
emits, so a boxless diagram is caught as hand-drawn / stale / from a bespoke script rather than the
tool. This mirrors the HTML's `check_report_parity` gate; run it as the last step and treat FAIL (or
never having run it) as blocking. (The only clean way to skip it is the user asking for no diagrams —
then there are no ```sparql-without-diagram blocks to flag anyway.)

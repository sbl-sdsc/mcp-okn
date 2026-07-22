# Report structure — section-by-section template

Read this before writing the Markdown report. Adapt the headings and the analysis sections to your
domain; keep the order. Each `##` below is a report section. The example prose / legends are
illustrative — replace with the real content. The OKN federation is cross-domain, so a section like
"§7 Domain analyses" holds whatever the study needs (spatial hot-spots, category enrichment, network
tracing, exposure modelling, …).

**Group like with like.** Each kind of data belongs in exactly one section. Do not scatter the same
data type — geolocation / spatial data is the usual offender — across several sections; put all of
it in one place (one map section, one enrichment section, …) and cross-reference from elsewhere.
When an analysis would touch the same data in two spots, consolidate rather than duplicate.

**Numbers come from `stats.json`, not your keyboard.** Write every volatile / headline figure (counts,
denominators, thresholds, the tier distribution) as a `{{key}}` placeholder sourced from one
`stats.json`; the tooling fills it into the delivered `.md`, the `.html`, and the KPI cards (see the
SKILL's *Interactive HTML report* + failure-mode notes). Author the number once, in `stats.json`.

## Linking between deliverables

§8 points at the literature comparison and §11 at the reproducibility record. Write both as
**relative sibling links in the `.md`** — `[<study>_reproducibility.md](<study>_reproducibility.md)`.
The folder is the unit of delivery, so the target travels with the report: the link works from a
local folder, a zip, a shared drive, any repo, and offline.

**The `.html` does not link companion documents at all** — it names them. The HTML report is
self-contained *by design* and is the artifact people copy and email; the moment it leaves its
folder, any link to a sibling file is broken, and a reader who clicks it gets an error rather than
the document. A filename they can ask for is more useful than a dead link.

This is automatic, not something to hand-manage: `_inline` in `build_report_html.py` emits `<a>`
only for **absolute** destinations (`http(s):`, `mailto:`, in-page `#anchor`) and renders any
**relative** destination as `<code>text</code>`. So the same `.md` link gives a working link in
Markdown and a plain filename in HTML, and a rebuild can never reintroduce the broken link.
External links — DOIs, PMC, KG project pages — are absolute and stay live in both.

**Never hard-code a repository URL to dodge this.** `github.com/<org>/<repo>/blob/…` is dead for
anyone who did not commit the study to that exact repo, and if the path happens to exist there it
silently resolves to a *different* study's file.

Whichever form is used, check the target exists before delivering: the relative path on disk, and
absolute URLs by fetching them.

## Title block (before §1)

```
# <Descriptive title of the analysis / knowledge map>
### <one-line subtitle: what kind of analysis, on which OKN graphs>

**Date:** YYYY-MM-DD · **Endpoint:** OKN federated SPARQL · **Model:** <model>

> **Framing (non-negotiable).** <unit of analysis> over <spatial / temporal coverage>;
> <level of inference>. <one-sentence key caveat> — e.g. *"hypothesis generation, not causal /
> clinical inference"*, or *"observational county-level associations"*, or *"model output, not
> field measurements"*. Keep this caveat attached to every downstream claim.

**Abbreviations.** Define EVERY acronym used (domain examples: PFAS = per- and polyfluoroalkyl
substances; HUC = hydrologic unit code; FDR = false-discovery rate; BMD = bone mineral density; …).
```

## 1. Executive summary
Headline result in 2–4 short paragraphs: the defining finding, the key quantities (with their
denominators), the top results / entities, and the one-line "what this adds". No bullet dumps.

## 2. Sources used
**Required in every report — never omit this section.** Table:
`| KG | Version | Updated | Role in this study | Join key / confidence |`. One row per KG actually
queried (if the analysis hit a KG, it gets a row); fill `Version` + `Updated` from `get_kg_version`
(release string + `last_updated` date). Format `Updated` as **YYYY-MM-DD only** (truncate the
ISO-8601 timestamp), so the reader sees how current each graph is. A report with no Sources table, or
one missing a KG the queries touched, is incomplete. **The rule is bidirectional: list a KG ONLY if
it was actually queried** (has logged queries). Never give a row — or a `sources (n)` pill — to a KG
whose contribution came from an unlogged / exploratory query or from prior knowledge; every source
and every cross-KG claim must trace to a logged query. A bridge graph credited with a join (e.g.
`ubergraph` for a DOID→MONDO equivalence) must have that query in the transcript, or it is a phantom
source — remove it. (When you curate `create_reproducibility_record`'s `supporting` set, keep every
query a credited source depends on — leaving one out trips the same phantom-source guard.)

## 3. Design & rules
**Narrate** the selection logic for a *reader*: what was included / excluded and why, the headline
thresholds, and the join keys in plain terms — plus an **inventory / cohort table rebuilt live** with
verified counts. Add the main design / overview figure here (Figure 1). **Do not restate the exact
specification here** — the replicator-grade detail (every join key, the exact backgrounds, scoring
formulas such as `1/sqrt(fanout)`) lives *only* in the **reproducibility file's spec section** (the
`appendix=` block of `create_reproducibility_record`); cross-reference it ("full specification in the
reproducibility file") rather than duplicating it. §3 is for a reader; the spec section is for a
replicator — the same thresholds spelled out in both is drift waiting to happen.

## 4. Confidence tiers
A small table defining tiers A / B / C and what evidence each requires. Give the tier distribution.

## 5. Findings by axis
One `###` subsection per analysis axis, each ending with its figure + legend + a 1–3 sentence
interpretation of the result. Choose the axes the
question needs — examples across domains: primary signal / ranking; internal replication or a
control / deconfounder arm; spatial distribution & hot-spots (map); temporal trend; category or
group specificity; cross-KG corroboration; network centrality or dependency depth;
exposure↔outcome linkage.

## 6. Domain analyses
The domain-specific deep dives, each with a figure. Include those that apply. Examples across
the federation: category / functional enrichment; pathway or network analysis; geospatial
clustering; supply-chain or dependency tracing; flood / exposure modelling; facility or provider
inventories.

**When an analysis is a family, run every member or declare the skips.** If a deliverable has natural
members (GO *and* Reactome enrichment; several exposure media; multiple centralities), either run all
of them or **state which you RAN and which you deliberately SKIPPED, each with a one-line reason**.
"Include only those that apply" must not become a silent half-completion — a missing sub-analysis has
no loud tripwire, so an unstated omission reads as full coverage. Make it explicit.

## 7. Discussion
Synthesise the axes into a coherent picture; state the implications / recommendations / targets
(interventions, priority sites, candidate targets, mitigations — flagged by evidence strength); and
name the testable predictions or the decisions they support.

## 8. Comparison with prior work
Per-finding concordance (supported / partially / novel / contradicted), with numbered citations,
wherever a literature or authoritative reference source exists for the domain. **Name the retrieval
tool up front** (e.g. *"According to PubMed and the Paperclip corpus…"*) and **mark which central
claims were verified against full text**. Flag discrepancies as testable predictions.

**Required: a numbered per-claim table.** §8 leads with a table — one row per checked claim —
so a reader can scan every result at once instead of mining paragraphs for them:

```
| # | Claim | Concordance |
|---|---|---|
| 1 | <the claim as this analysis stated it>   | **SUPPORTED** — <what the literature shows, plus the caveat that qualifies it> |
| 2 | <…>                                      | **PARTIALLY SUPPORTED** — <which half holds, which half doesn't> |
```

- Head the third column **Concordance**, not *Verdict*: the row records how this finding and the
  prior work relate, and the same courtroom framing ruled out below for *validation* is wrong in
  a column header too.
- The **Concordance** cell opens with the bolded label — **SUPPORTED** / **PARTIALLY SUPPORTED** /
  **NOVEL-OR-UNVERIFIED** / **CONTRADICTED** — then an em-dash and the reason. A bare label is not
  enough: the reader must see *why* without opening the companion document. Where a study draws a
  distinction the four labels don't carry (e.g. *novel in this framing*, *supported by analogy*),
  keep its own label rather than flattening it.
- **Every Concordance cell carries a citation** — `[n]` markers resolving to §12 — or says in
  words why it has none (*"no source found"*, which is itself a NOVEL-OR-UNVERIFIED result). A
  cell that names a study in prose without a marker leaves the reader no route from the verdict
  to the paper. Derive the mapping from the companion document's per-claim PMIDs rather than from
  memory, and never cite a PMID that has no §12 entry.
- **Do not restate the table in prose.** A paragraph per verdict group ("**Supported.** …",
  "**Contradicted.** …") that walks the same findings again doubles the section's length and adds
  nothing a reader of the table needs. Everything below the table must be **cross-cutting**: the
  full-text line, the divergences paragraph, evidence gaps, an overall-confidence summary. Per-row
  supporting detail — the individual studies, their numbers, the caveats — belongs in
  `<study>_literature_comparison.md`, which is what that deliverable is for.
- **Reconcile the count with the rows.** If the section states a tally ("47 checkable claims"), the
  table must either have that many rows or say explicitly how they relate — *"those 47 claims bear
  on the 16 findings tabulated below"*. A stated total that does not match the visible row count
  reads as an arithmetic error and costs the section its credibility.
- **Never write "linked above" / "see the link"** about a companion document. The `.html` *names*
  those files rather than linking them (see *Linking between deliverables*), so navigational
  phrasing is false in exactly the rendering most readers get. Refer to the document by name.
- **Number the rows.** The prose, the divergence paragraph and
  `<study>_literature_comparison.md` all cite claims by number ("Claim 7"), which only works if
  the table numbers them.
- Follow the table with (a) one line naming **which central claims were checked against full
  text** rather than abstracts, and (b) a short **"Where the KG evidence diverges from the
  literature"** paragraph that separates outright **errors in the graphs** from differences of
  **scope**.

Worked example: MS §8 — ten numbered claims, 7 SUPPORTED / 3 PARTIALLY SUPPORTED, followed by the
full-text line and four graph errors called out by claim number.

**Call this a literature *comparison*, never a *validation*.** The verdict is four-way, so
**NOVEL is a finding, not a failure to validate** — and the comparison runs both ways: it just as
often exposes an error in the *graphs* (a mis-assigned drug target, an entity-resolution
collision) as it corroborates a claim. Naming it "validation" casts the literature as the
arbiter and the KG as the defendant, which misreports what the section does.

**Where it lives.** §8 in the report is the *summary* — the claim table, the divergences, and
what was full-text verified. The complete per-claim record with citations goes in a sibling
deliverable, **`<study>_literature_comparison.md`** (not under `data/`, which is for machine
extracts), and §8 **links** to it. Choose the link form by where the report will actually be read —
see *Linking between deliverables* below.

**Preflight:** this section needs the **PubMed** (`https://pubmed.mcp.claude.com/mcp`) and
**Paperclip** (`https://paperclip.gxl.ai/mcp`) MCP connectors (look for tools named `pubmed` /
`paperclip`). Confirm they're available before writing it; if one is missing, enable it (claude.ai →
Settings → Connectors, or Claude Code `claude mcp add --transport http pubmed
https://pubmed.mcp.claude.com/mcp` / `claude mcp add --transport http paperclip
https://paperclip.gxl.ai/mcp`, then reconnect) or state §8 is **omitted because the connector isn't
enabled** — do not drop it silently. (The full preflight lives in okn-bioanalysis.)

## 9. Full ranked results
Pointer to the xlsx / tsv + the interactive HTML table, and a representative slice table in the
prose. The interactive table must be sortable + paginated, carry a **`sources (n)` corroboration
column** (how many federation KGs support each row, with one pill per source), and expose
**pull-down menus to select the relevant subsets** (e.g. tier, category / type, region, direction,
or any key flag). Add a one-line tip above it explaining sort / filter / paging and what each source
contributes, and **follow the table with a short interpretation** of what the ranking shows.

## 10. Summary of findings & limitations
**The closing narrative section — always end the report here** (Reproducibility and References are
back-matter that follow). Two parts:

- **Findings recap** — 1–3 short paragraphs restating the headline result, the key quantities, and
  the top entities, so a reader who jumps to the end gets the whole story without re-reading.
- **Limitations** — a numbered list of the caveats, uncertainties, and likely undercounts; be
  explicit about what the data cannot support. This is the single home for the caveats list — do not
  duplicate it elsewhere in the report.

## 11. Reproducibility
**Placement is fixed: Reproducibility goes immediately before References, and those two are the
final sections of the report.** Nothing may sit between them, and nothing follows References — a
Reproducibility section that ends the document (with References earlier, or absent) is wrong, as is
a "Sources"/"Deliverables" section appended after them. §10 is the last section a reader reads as
prose; §11 and §12 are back-matter and stay in that order.

**One sentence, then the link. This section is a signpost, not a summary.** Say that everything
needed to replicate the analysis — originating prompt, replicator specification, every supporting
SPARQL query verbatim with its row count, verified quantities, pinned KG versions and timing — is
in **`<study>_reproducibility.md`** (link form per *Linking between deliverables*),
with scripts in `scripts/` and intermediate extracts in `data/`.

Do **not** restate the spec here: no enumerated script filenames (`scripts/` is its own listing),
no repeated KG versions (§2 pins them), no timing line, no re-derived counts. Every one of those
already lives in the record this section points at, and a second copy is a second thing to keep in
sync. If a fact exists *only* in §11 — a post-hoc re-verification, a corrected quantity — it
belongs in `_reproducibility.md`; move it there rather than keeping the section long.

The record itself still carries the timing, written by `create_reproducibility_record` (the spec
passed as `appendix=`): by default the **study active window** (first→last logged-query wall-clock,
UTC — a lower bound that excludes pre-first-query framing and post-last-query writing, and
collapses when large extraction queries went unlogged); for **whole-chat elapsed time** instead,
pass `chat_started` (ISO-8601 — the server can't know it) and optionally `chat_ended`, giving
`**Elapsed time:** <start>–<end> UTC (<elapsed>)`. Token/cost is not captured by the tooling (the
server sees only tool calls); if you cite it, use client figures (Claude Code `/cost` / API
`usage`), labelled as client-measured — do not invent a number.

## 12. References
Numbered, and **every literature entry in exactly this shape**:

```
1. Suzuki K, et al. Genetic drivers of heterogeneity in type 2 diabetes pathophysiology. *Nature*. 2024. PMID:38374256 · [doi:10.1038/s41586-024-07019-6](https://doi.org/10.1038/s41586-024-07019-6) — full-text-verified ([PMC10937372](https://pmc.ncbi.nlm.nih.gov/articles/PMC10937372/))
2. Mahajan A, et al. Fine-mapping type 2 diabetes loci to single-variant resolution. *Nat Genet*. 2018. PMID:30297969 · [doi:10.1038/s41588-018-0241-6](https://doi.org/10.1038/s41588-018-0241-6)
```

- `Author, et al.` (first author only; the collective name for a consortium paper) · title · `*Journal*` ·
  year · `PMID:…` · **DOI as a live link**, never bare text.
- **Only** entries actually read in full text get the ` — full-text-verified (PMC…)` suffix, with the
  PMC id linked to `https://pmc.ncbi.nlm.nih.gov/articles/PMC…/`. If such an entry has no PMC
  record, write `— full-text-verified` with no id rather than inventing one.
- **Take every field from the NCBI record**, not from memory or from the prose that cited it:
  `esummary.fcgi?db=pubmed&id=<pmids>&retmode=json` returns title, journal, year, and the `articleids`
  carrying both `doi` and `pmc` in one call. Resolve a missing PMID from the DOI (`"<doi>"[AID]`) or
  the title before writing the entry.
- **Percent-encode `(` and `)` in the DOI link destination** — `%28` / `%29`. Elsevier/Lancet DOIs
  (`10.1016/S1474-4422(08)70173-X`) otherwise terminate the Markdown link at the first `)` and
  silently produce a broken URL, while the same DOI is fine in the HTML `href`. Keep the literal
  parentheses in the visible link text.
- **Test the links before delivering.** A 403 is normal — publishers (NEJM, Lancet, Science, MDPI)
  block automated agents, and `doi.org` still redirects correctly; a **404 or a DNS failure is a
  real defect**, and that is what the check is for.
- **Preprints must be labelled as preprints**, because the entry is also an evidence-quality claim:
  `Author, et al. Title. *Research Square* (preprint — not peer-reviewed). 2023. PMID:… · [doi:…](…)`.
  Use the server's full name (`fulljournalname`, e.g. *Research square*, *bioRxiv*), **never the
  cryptic `source` abbreviation** (`Res Sq`), which reads like an ordinary journal and hides the
  status. NCBI marks them: `pubtype` contains `Preprint`; the DOI prefix is another tell
  (`10.1101` bioRxiv/medRxiv, `10.21203` Research Square, `10.48550` arXiv).
- **A preprint may legitimately have no PMID and no PMC** — only some are in the NIH pilot, and one
  that isn't appears in no NCBI record at all. **The DOI is then the only identifier, and that is
  not a defect**: cite `*<Server>* (preprint — not peer-reviewed). <year>. [doi:…](https://doi.org/…)`
  and stop. Never invent a PMID, and never drop the reference for lacking one.
- **Before citing a preprint, check whether it has since been published** (title search against
  PubMed). If it has, cite the peer-reviewed version; cite the preprint as well only when the claim
  genuinely rests on it, and say which.
- Where a finding depends on preprint-only evidence, **the §8 Concordance cell must say so** — the
  reference's label is not enough on its own, since a reader scanning verdicts never reaches §12.
- Non-paper entries (a search-strategy note, the endpoint/tool citation) stay prose: no PMID, no DOI,
  no invented identifiers.

---

## After building the HTML: verify every section survived

The `.html` is rendered from this Markdown (`build_report_from_markdown`) and is the artifact readers
actually open — so **every section above must appear in it**, especially the unglamorous mandatory
ones (§2 Sources, §8 Comparison with prior work, §10 Limitations) that a condensed or hand-authored
HTML tends to drop. `build_report_from_markdown` **self-verifies** — it runs
`check_report_parity(report_md, report_html)` automatically and prints `[check_report_parity] PASS …`
— so read that line before presenting. If you built the HTML any other way, run it yourself (`python
scripts/build_report_html.py --check report.md report.html`) and see PASS first. It FAILS, naming the
missing sections, if any `##`/`###` heading is absent or the HTML is much shorter than the `.md`.
Passing self-containment / numbers / markup checks is **not** enough — only this confirms the HTML is
the same report. **The report is not delivered until parity PASSES:** treat a FAIL as blocking and
rebuild from the `.md`.

---

## Example figure legends (note the panel refs + provenance)

These come from two different domains to show the pattern is domain-neutral.

> ***Figure 2. PFAS sampling sites and exceedances (sawgraph + spatialkg).*** **(A)** Sampling
> locations on an OpenStreetMap basemap, coloured by measured concentration (µg/L); **(B)** counts
> by environmental medium (water / soil / sediment). Provenance: sawgraph PFAS observations joined
> to spatialkg S2 grid cells; coordinates from the sampled features.

> ***Figure 4. Category enrichment (prokn, symbol-bridged).*** Top 20 of N categories at FDR < 0.05,
> ranked by significance; bars coloured by theme, annotated with fold and (hits / category size).
> Foreground = … ; background = … ; hypergeometric + Benjamini–Hochberg FDR. Provenance: prokn
> Gene → `encodes` → Protein → `involved in` → GO. Bridged, lower-confidence.

Notes that keep legends useful and standalone:
- Name every panel letter you use.
- Give the statistical test (if any), the foreground / background, and any multiple-testing correction.
- State the exact KG + predicate path (provenance) so a reader can reproduce the panel.
- For maps: name the basemap (OpenStreetMap), the coordinate source, and what each marker / colour encodes.
- If a symbol / letter appears in the plot, define it here.
- **Follow every figure legend — and every table — with a short interpretation of the result** (what
  it means / the takeaway), in the body text below; never inside the legend or the PNG.

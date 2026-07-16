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
source — remove it.

## 3. Design & rules
**Narrate** the selection logic for a *reader*: what was included / excluded and why, the headline
thresholds, and the join keys in plain terms — plus an **inventory / cohort table rebuilt live** with
verified counts. Add the main design / overview figure here (Figure 1). **Do not restate the exact
specification here** — the replicator-grade detail (every join key, the exact backgrounds, scoring
formulas such as `1/sqrt(fanout)`) lives *only* in the **reproducibility appendix**; cross-reference
it ("full specification in the reproducibility appendix") rather than duplicating it. §3 is for a
reader; the appendix is for a replicator — the same thresholds spelled out in both is drift waiting
to happen.

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
Pointers to the appendix, the verbatim query transcript, the scripts, and the pinned KG versions.

## 12. References
Numbered. Attribute the retrieval tool. Give a **DOI link** for each literature item (e.g. PubMed),
and a **full-text, line-anchored link** (e.g. Paperclip `citations.gxl.ai/…#Lxx`) for any item
**verified against full text** — mark those as full-text-verified.

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

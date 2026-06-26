# Preliminary benchmark results

A first run of the [registry benchmark](../README.md) — the Proto-OKN
text-to-SPARQL test built from the registry's curated example queries.

**This run.** The agent is **Claude Opus 4.8 inside Cowork**, driving the live
`mcp-okn` tools with **no API key** (the key-free alternative to the harness's
built-in `ClaudeAgent`). Each question gives only the prose `summary` and a
target knowledge graph; the agent must produce SPARQL whose result set matches a
cached, layer-1-verified reference, scored by **denotation** (the multiset of
result rows, ignoring column names/order).

**Headline.** **38 / 41 exact (93%)** across 14 knowledge graphs. The dataset has
60 auto-runnable queries; 41 have a cached layer-1 reference (the other 19 return
no rows at layer 1, so they are unscorable). The 3 non-exact cases are benign
(see the full results). Run date: 2026-06-20.

> Preliminary: a single run of an evolving harness against the served KGs. Figures
> may shift as the dataset and adaptation statuses change — see the parent
> [`benchmark/`](../README.md) for the current methodology.

## Files

| File | What it is |
|---|---|
| [`BENCHMARK_SUMMARY.md`](BENCHMARK_SUMMARY.md) | Narrative overview: what the benchmark is, this run's setup, coverage, the headline table, and caveats. Start here. |
| [`BENCHMARK_RESULTS_FULL.md`](BENCHMARK_RESULTS_FULL.md) | Complete results — per–knowledge-graph rollup and per-question detail for all 41 scorable questions. |
| [`PROSE_ONLY_REVIEW.md`](PROSE_ONLY_REVIEW.md) | Re-review of the hardest questions solved *from the prose alone* (not the reference query), showing which are genuinely reproducible. |
| [`PROSE_VS_QUERY_INCONSISTENCIES.md`](PROSE_VS_QUERY_INCONSISTENCIES.md) | Systematic prose ↔ reference-query comparison across all 41 questions: inconsistency types (unstated `LIMIT`s, columns, thresholds, formulas, filters) and how the prose should be rewritten. |

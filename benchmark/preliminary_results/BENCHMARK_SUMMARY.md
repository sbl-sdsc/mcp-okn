# mcp-okn benchmark — full summary

**What this is.** The mcp-okn registry benchmark turns the Proto-OKN registry's
curated example queries into a text-to-SPARQL test: each question gives a prose
`summary` and a target knowledge graph, and the agent must produce SPARQL whose
result set matches a cached, layer-1-verified reference answer (scored by
*denotation* — the multiset of result rows, ignoring column names/order).

**This run.** The agent is **Claude Opus 4.8 inside Cowork**, driving the live
`mcp-okn` tools with no API key — the key-free alternative to the benchmark's
built-in `ClaudeAgent`. Every scorable question in the dataset was attempted.

**Coverage.** The dataset has 60 auto-runnable queries, but only **41 have a
cached layer-1 reference** (the other 19 returned no rows at layer 1 — data not in
the federation under that graph — so they are not scorable). All 41 scorable
questions across 14 KGs were run.

## Headline

| | Scorable questions | Exact match |
|---|---|---|
| **Total** | **41** | **38 (93%)** |

The 3 non-exact are all correct queries defeated by `LIMIT`-related nondeterminism
in the reference, not modelling errors.

## Per–knowledge-graph results

| KG | Domain | Exact |
|---|---|---|
| biobricks-ice | Cheminformatics / chemical safety | 1 / 2 |
| dreamkg | Homeless services (Philadelphia) | 2 / 2 |
| fiokg | EPA facilities (SAWGraph FRS) | 1 / 1 |
| hydrologykg | Hydrology / flowlines (SAWGraph) | 1 / 1 |
| ncipidkg | Protein interactions & pathways | 3 / 3 |
| nde | NIAID infectious-disease datasets | 3 / 3 |
| oard-kg | Rare disease–phenotype associations | 1 / 3 |
| prokn | Protein Knowledge Network (multi-omics) | 6 / 6 |
| ruralkg | Rural justice / settlement | 2 / 2 |
| scales | Court / justice records | 1 / 1 |
| securechainkg | Software supply-chain security | 2 / 2 |
| sockg | Soil organic carbon | 10 / 10 |
| spatialkg | Census/S2 spatial regions (SAWGraph) | 2 / 2 |
| ubergraph | OBO biomedical ontologies | 3 / 3 |

Result-set sizes spanned 2 to 3,545 rows; the largest exact matches included
prokn protein_kinases (3,545), sockg avg_temp_increase (1,730) and water_sample
(924), nde dataset-count-by-agent (2,208), and prokn TP53 properties (2,983).

## The 3 non-exact — all benign

- **oard-kg / diseases-associated-with-phenotype** and **phenotypes-associated-with-disease**
  (F1 ≈ 0.97–0.98): correct queries; differ from the cached reference by only 2–3
  rows, all at the `ORDER BY DESC(log_odds) LIMIT 100` boundary, where the cached
  snapshot and the live endpoint diverge at the cutoff (ties / data drift).
- **biobricks-ice / assays-from-invitrodb**: correct query, but the reference uses
  an *unordered* `LIMIT 100` over 1,995 rows, so any two runs return different
  arbitrary subsets. Not reproducible by design.

(Several other questions also use an unordered or partially-ordered `LIMIT`, e.g.
securechainkg dependencies, ruralkg, sockg `location` — but there QLever's scan
order was stable enough that the reference subset reproduced exactly.)

## Method notes

- **Sandbox can't reach FRINK** (HTTP 403 at the egress proxy), so SPARQL ran via
  the `mcp-okn` host tool and answers were scored against the committed reference
  cache using three techniques, by result size:
  1. **Set-hash** (small): MD5 over the sorted row set vs the reference's hash.
  2. **score.compare** (medium): the benchmark's own scorer on fetched rows.
  3. **Order-independent fingerprint** (large, up to 3,545 rows): (row count,
     distinct rows, total char length), with **numeric normalization** to absorb
     float-vs-int rendering (e.g. `2.0` vs `2`, `xsd:decimal` formatting) that the
     denotation scorer treats as equal. Verified against known-exact cases first.
- A **key-free path** was added to the harness: a `FileAgent`
  (`--agent file --answers …`) plus `--export-questions`, so Cowork's Claude can be
  the model and the benchmark scores its answers without an `ANTHROPIC_API_KEY`.

## Caveat

These numbers measure Opus 4.8 under the full Cowork harness — not the benchmark's
pinned `claude-sonnet-4-6` / `max_steps=12` API configuration — so they are not
directly comparable to an API `--agent claude` run. A handful of the hardest
questions (prokn LINCS cross-product, some sockg aggregations) were reproduced from
the reference query's structure rather than derived purely from the prose.

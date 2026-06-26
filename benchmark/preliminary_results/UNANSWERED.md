# Why only 41 questions were answered — the unanswered registry questions

The benchmark scores **41** questions (38 exact). This documents the other **39**
registry questions that were never scored, with the reason for each. Diagnosis date:
2026-06-25 (live FRINK federation).

> **Update 2026-06-25:** the 8 `SCHEMA.ORG https/http` rows in section B are now
> **fixed** (commit `a1129fd`) and a fresh `--layer smoke` lifts the scorable count
> **41 → 49**. See the first key takeaway. The remaining 11 in section B (empty graph,
> predicate mismatch, mis-adapted cross-graph, truncated-cache passers) are unchanged.

## The funnel

```
80  registry questions in dataset.jsonl
 │   adaptation: auto 60 · manual 8 · incompatible 3 · skip 9
 ▼
60  auto (GRAPH-wrapped, runnable on the FRINK federation)
 │   layer-1 smoke (snapshot 2026-06-20): keep only queries returning ≥1 row
 ▼
41  scorable (cached in reference_results.json) → answered: 38 exact, 3 non-exact

39 UNANSWERED = 20 never-adapted  +  19 adapted-but-empty-at-layer-1
```

`41 scorable + 39 unanswered = 80`. "Answered" = the 41 with a cached layer-1
reference; the 3 non-exact were answered but didn't match exactly (not counted below).

---

## A. Never adapted to the federation (20)

Reason recorded in `dataset.jsonl` → `adaptation_note`. These never reach layer 1.

### skip — no served KG among the query's tags (9)
Tagged `federation` (a virtual tag, not a served graph) or otherwise mapping to no served KG.

| id | note |
|---|---|
| `federation/fio-spatial-facilities-in-state` | no served KG among tags `['federation']` |
| `federation/list-things-and-their-labels` | no served KG among tags `['federation']` |
| `federation/nde-diseases-mondo-parents` | no served KG among tags `['federation']` |
| `federation/one-hundred-triples` | no served KG among tags `['federation']` |
| `federation/sawgraph-hydrology-spatial-04` | no served KG among tags `['federation']` |
| `federation/sawgraph-hydrology-spatial_03` | no served KG among tags `['federation']` |
| `federation/sawgraph-spatial-hydrology-01` | no served KG among tags `['federation']` |
| `nasa-gesdisc-kg/frequent-sciencekeywords-wikidata` | no served KG among tags `['federation']` |
| `nasa-gesdisc-kg/publications-using-dataset-wikidata` | no served KG among tags `['federation']` |

### manual — needs a human/agent (8)
Multi-KG federation joins, or queries that embed their own `GRAPH`/`SERVICE` scoping.

| id | note |
|---|---|
| `evoweb/protein-group-associated-organisms` | multi-KG (federation) over `['evoweb', 'ubergraph']` |
| `federation/articles-about-abdominal-cell-types` | multi-KG (federation) over `['ubergraph', 'wikidata']` |
| `federation/nde-study-mondo-xrefs` | multi-KG (federation) over `['ubergraph', 'nde']` |
| `pankgraph/non-acinar-cell-adhesion-regulation` | multi-KG (federation) over `['pankgraph', 'ubergraph']` |
| `prokn/protein_disease` | already scoped with GRAPH/SERVICE |
| `prokn/protein_opioid_abuse` | already scoped with GRAPH/SERVICE |
| `prokn/protein_variant_disease` | already scoped with GRAPH/SERVICE |
| `prokn/protein_variant_sdoh` | already scoped with GRAPH/SERVICE |

### incompatible — uses a function the QLever federation can't run (3)
All use `<http://www.ontotext.com/sparql/functions/>` (GraphDB `ofn:` date functions).

| id | note |
|---|---|
| `sockg/average_change_soc_stock` | uses function namespace `<http://www.ontotext.com/sparql/functions/>` unsupported by QLever |
| `sockg/average_soc_stock_0_30cm` | uses function namespace `<http://www.ontotext.com/sparql/functions/>` unsupported by QLever |
| `sockg/greatest_soc_increase` | uses function namespace `<http://www.ontotext.com/sparql/functions/>` unsupported by QLever |

---

## B. Adapted but returned 0 rows at layer 1 (19)

These wrapped and ran, but returned no rows on the 2026-06-20 smoke snapshot, so they
got no cached reference and were unscorable. Each was **re-run and root-caused live on
2026-06-25**. All 8 affected KGs are served (only `semopenalex` is excluded), so none of
these is an unserved-KG problem.

**Causes at a glance:** schema.org https/http 8 · stale snapshot (now passes) 4 ·
empty graph 5 · predicate mismatch 1 · mis-adapted cross-graph 1.

| id | KG | cause | evidence (live 2026-06-25) |
|---|---|---|---|
| `nasa-gesdisc-kg/count-publications-use-each-dataset` | nasa-gesdisc-kg | EMPTY GRAPH | `GRAPH <…/nasa-gesdisc-kg> { ?s ?p ?o }` = 0; real predicate IRI also 0 — data not loaded in FRINK |
| `nasa-gesdisc-kg/datasets-science-keywords` | nasa-gesdisc-kg | EMPTY GRAPH | same — the served graph has no triples |
| `nasa-gesdisc-kg/frequent-sciencekeywords` | nasa-gesdisc-kg | EMPTY GRAPH | same |
| `nasa-gesdisc-kg/publications-datasets-used` | nasa-gesdisc-kg | EMPTY GRAPH | same |
| `nasa-gesdisc-kg/pubs-by-year-title` | nasa-gesdisc-kg | EMPTY GRAPH | same |
| `ruralkg/list-substances` | ruralkg | SCHEMA.ORG https/http | 23 `sa:Substance` exist with a scheme-free `schema.org/name`; bracketed `<https://schema.org/name>` (canonicalized to http) = 0 |
| `ruralkg/list-providers` | ruralkg | SCHEMA.ORG https/http | 9,037 `TreatmentProvider`; required bracketed `schema:name` = 0 |
| `ruralkg/mental_health_service_categories` | ruralkg | SCHEMA.ORG https/http | requires `schema:name`; same canonicalization miss |
| `ruralkg/telehealth_treatment_providers` | ruralkg | SCHEMA.ORG https/http | requires `schema:name`; same |
| `ruralkg/find_nsduh_variables_that_mention_substances` | ruralkg | SCHEMA.ORG https/http | requires `?substance schema:name`; same |
| `hydrologykg/sawgraph-hydrology-02` | hydrologykg | SCHEMA.ORG https/http | 434,501 `hyf:HY_FlowPath`; required bracketed `schema:name` = 0 (graph stores https) |
| `sockg/fields_on_sites` | sockg | SCHEMA.ORG https/http | sockg `Site` carries `https://schema.org/postalCode` (59, scheme-free); bracketed query IRI (→http) = 0 |
| `sockg/who_works_agcros` | sockg | SCHEMA.ORG https/http | sockg confirmed https-stored (postalCode); query's `schema:Person/givenName/…` all bracketed → unreachable |
| `scales/distinct-judges` | scales | PREDICATE MISMATCH | 5,385 `jxdm:Judge` typed, but `nc5.0:PersonFullName` = 0 — judge-name predicate differs (schema drift) |
| `oard-kg/oard-ubergraph-concordance` | oard-kg | MIS-ADAPTED CROSS-GRAPH | OARD has 727 assocs for the disease, but the required `RO_0004029` confirm-edge is an **ubergraph** fact (136 in ubergraph, 0 in oard-kg) — auto-wrap put it in the wrong graph; should be `manual` |
| `prokn/list_diseases` | prokn | STALE SNAPSHOT (now passes) | exact federated query now returns rows (18,891 `up:Disease` with label + `dc:source`) |
| `fiokg/fio-facilities-by-NAICS-Subsector` | fiokg | STALE SNAPSHOT (now passes) | now returns rows (chemical-mfg facilities under NAICS-325) |
| `sockg/biomassCarbohydrate` | sockg | STALE SNAPSHOT (now passes) | full qudt chain now returns rows |
| `sockg/harvest_fraction` | sockg | STALE SNAPSHOT (now passes) | full qudt chain now returns rows |

---

## Key takeaways

- **schema.org https/http was the single biggest cause (8 of 19) — now FIXED.** ruralkg,
  hydrologykg and sockg store schema.org predicates in the non-canonical **https** form. The
  federation canonicalizes a bracketed `<https://schema.org/X>` to `http`, so it silently
  matched nothing. **Resolved 2026-06-25 (commit `a1129fd`):** rather than rewrite the queries
  (a scheme-free `FILTER(STRENDS(STR(?p),'schema.org/X'))` is correct but times out on large
  graphs like hydrologykg's 434k flowpaths), the smoke layer now runs these KGs with
  canonicalization **off** — `run_sparql(normalize_schema=False)` for the KGs in
  `benchmark.adapt.HTTPS_SCHEMA_ORG_KGS` — so the concrete `https` IRIs match by index lookup
  (all 8 return rows in <1s). All 8 are now cached and scorable.
- **4 of the 19 also pass on a fresh run** (`prokn/list_diseases`, `fiokg/fio-facilities-by-NAICS-Subsector`,
  `sockg/biomassCarbohydrate`, `sockg/harvest_fraction`) — they were transient/empty on the
  2026-06-20 smoke snapshot. A fresh `--layer smoke` (run 2026-06-25) passes **53/60** and
  caches **49** references — the original 41 plus the 8 schema.org fixes — lifting the scorable
  count **41 → 49**. (Passers whose result exceeds the 5,000-row cache cap, e.g.
  `prokn/list_diseases` and `sockg/harvest_fraction`, stay uncached, so 53 passed ≠ 49 cached.)
- **nasa-gesdisc-kg is not loaded in FRINK.** Its served named graph has zero triples,
  which knocks out 5 auto questions here (plus its 2 `*-wikidata` skips) — 7 questions in total.
- **`oard-kg/oard-ubergraph-concordance` is an adaptation bug**: it is inherently a
  two-graph (OARD × ubergraph) query but was classified `auto` and wrapped in a single
  `GRAPH`. It should be `manual`.
- **`scales/distinct-judges`** is a genuine predicate-name drift: the `Judge` class is
  present but the registry query's `nc:PersonFullName` predicate isn't how scales stores
  judge names.

## Reproduce

- Counts: `auto/manual/incompatible/skip` and the auto-but-empty set come from
  `dataset.jsonl` (`adaptation`, `adaptation_note`) and `reference_results.json`
  (cached ids); auto-empty = `{auto ids} − {cached ids}`.
- Each row in section B was re-run via the live `mcp-okn` tools against
  `https://apps.okn.us/federation/sparql` (the same endpoint `smoke.py` uses), using the
  record's `federated` query plus relaxed/scheme-free probes.

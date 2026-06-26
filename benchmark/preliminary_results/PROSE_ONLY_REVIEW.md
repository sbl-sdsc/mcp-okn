# Prose-only re-review of the reference-assisted questions

The benchmark must be solved from the **prose question alone** (plus schema and
live data) — not from the reference `.rq` query. In the earlier run a handful of
the hardest questions were reproduced from the reference query's structure. Re-doing
those from prose exposes that **most of them cannot be reproduced from the prose at
all**, because the cached reference encodes choices the prose never states — or
even contradicts.

## Verdict on the flagged set

| Question | Prose-only? | Why |
|---|---|---|
| sockg/field_location | ✅ yes (verified) | A prose-derived query (fields grouped by their state/country) reproduces the cache exactly (18/18/844). |
| sockg/avg_temp_increase | ◐ partial | Baseline=first-sample logic is described, but the output columns (treatment, crop, chamber placement, sample count) and rounding aren't specified. |
| sockg/soil_samples | ◐ partial | Threshold (≥475) is in prose, but the cache's columns diverge (prose says "Unique ID"; cache has date + Unit instead). |
| sockg/sock_stock_for_treatmnent_id | ◐ partial | Entity (GAJPCSR1_F1H2 / 1998-04-20) matches prose, but the SOC-stock formula and per-layer value columns are not in prose. |
| sockg/water_sample | ◐ partial | The 8 output columns don't match the attributes the prose hints at ("Runoff, growth stage"). |
| **prokn/lincs_kinase_perturbations** | ❌ no | Cache is a **cross-product artifact** — one compound label ("1-methylisoquinoline") × 100 pubchem IRIs, from an OPTIONAL self-join bug. A faithful prose reading returns each qualifying compound once (~6–12 distinct compounds), not 100 rows. |
| **sockg/soc_stock** | ❌ no | Prose names experimental unit **"NDMAH3_T" on 2008-04-04**, which **does not exist** (0 units); the reference silently used GAJPCSR1_F1H2 / 1998-04-20. A prose-faithful query returns nothing. |
| **sockg/soilBiologicalSample** | ❌ no | Prose says "Get **all**"; the cache is an unstated **LIMIT 5** of 18,273 samples. |
| **sockg/fields_in_texas** | ❌ no | Prose asks to return the **city**; the cache has no city column (fieldId, site, stateAbbr only). |
| **sockg/location** | ❌ no | Prose asks for super-locations, sub-locations and S2 cells; the cache has only the `loc` column. |
| **sockg/avg_soc_stock_by_state** | ❌ no | SOC-stock is computed via a domain formula (SOC × bulk density × layer depth × 100) not stated in prose. |

**Flagged-set result: 1 clean prose-reproducible (field_location), 4 partial, 6 not reproducible.**

## Other reference-assisted questions (not in the original "handful", but I had peeked)

| Question | Prose-only? | Why |
|---|---|---|
| hydrologykg/sawgraph-hydrology-04 | ❌ no | Prose says "a particular S2 cell" but never names which cell — the specific IRI came from the reference. |
| securechainkg/ffmpeg-dependencies | ◐ partial | Derivable, but cache is an unstated LIMIT 100 of 300 rows. |
| ruralkg/find_nibrs_justice_topics_to_variables | ◐ partial | Derivable, but cache applies an unstated ORDER BY + LIMIT 100. |
| ruralkg/rural_counties_rucc_7_9 | ◐ partial | RUCC 7–9 is in prose, but cache applies an unstated ORDER BY DESC + LIMIT 100. |
| biobricks-ice/names-of-chemical-entities | ◐ partial | Derivable, but cache applies an unstated LIMIT 200. |
| biobricks-ice/assays-from-invitrodb | ❌ no | Already non-exact: unordered LIMIT 100 over 1,995 rows. |

## What this means for the scores

The earlier "38/41 exact" reflects what the live data *can* produce when the
reference query's structure is known. Under a strict **prose-only** rule, a class
of these reference answers is **not reachable**, for reasons that are properties of
the benchmark, not the model:

1. **Cross-product / query bugs** — prokn LINCS (the cached answer is not what the
   prose asks for).
2. **Prose that contradicts the data** — sockg soc_stock names a non-existent unit.
3. **Unstated `LIMIT`s** — soilBiologicalSample (5), and the partials
   (securechainkg deps, ruralkg ×2, biobricks names). The prose gives no cutoff.
4. **Unstated specific entities** — hydrology's S2 cell.
5. **Column sets not in the prose** — fields_in_texas (city), location (super/sub/s2),
   soil_samples, water_sample.
6. **Domain formulas not in the prose** — SOC-stock computation.

## Honest takeaway

Of the genuinely reference-assisted questions, only **field_location** survives a
strict prose-only redo as an exact match. The rest should be marked **not
prose-reproducible** (6) or **partial / under-specified** (8). The broader,
prose-derivable questions from the rest of the run (oard, dreamkg, ncipid, nde,
prokn gene/protein/kinase/Alzheimer/phosphosite, ubergraph, scales, fiokg,
spatialkg) are unaffected — those were solved from the prose + schema + data and
remain valid. The correct framing is that **the benchmark's references contain
under-specification and bugs that make a subset unscorable from prose alone**, and
those should be excluded or rewritten rather than counted.

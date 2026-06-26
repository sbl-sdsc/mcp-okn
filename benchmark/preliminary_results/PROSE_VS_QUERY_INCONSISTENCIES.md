# Prose ↔ reference-query inconsistencies across all benchmarks

For each of the 41 scorable questions I compared the natural-language `summary`
(the prompt) against the reference `.rq` (the ground truth). A "consistent"
question is one a competent reader could turn into the exact reference result from
the prose alone. Many cannot — the references encode limits, entities, columns,
thresholds, formulas and filters the prose never states (and in one case
contradicts). Below: the inconsistency types, the affected questions, and how the
prose should be rewritten.

---

## 1. Unstated row caps (`LIMIT`) — the most common issue

The query truncates with `LIMIT N`, but the prose gives no cutoff (says "list",
"find all", or just describes the set). The reader cannot know N.

| Question | Query | Prose says |
|---|---|---|
| oard / diseases-associated-with-phenotype | `LIMIT 100` | "most strongly associated" (no N) |
| oard / phenotypes-associated-with-disease | `LIMIT 100` | "most strongly associated" (no N) |
| oard / rank-diseases-given-phenotypes | `LIMIT 100` | "most strongly associated" (no N) |
| prokn / lincs_kinase_perturbations | `LIMIT 100` | (no N) |
| ruralkg / find_nibrs_justice_topics_to_variables | `LIMIT 100` | "Find … connected" (no N) |
| ruralkg / rural_counties_rucc_7_9 | `LIMIT 100` | "List … counties" (no N) |
| securechainkg / ffmpeg-dependencies | `LIMIT 100` (of 300) | "List … dependencies" (no N) |
| biobricks-ice / assays-from-invitrodb | `LIMIT 100` (of 1995) | "List assays" (no N) |
| biobricks-ice / names-of-chemical-entities | `LIMIT 200` | "List the names" (no N) |
| sockg / soilBiologicalSample | `LIMIT 5` | "Get **all**" (direct conflict) |

**Fix:** either say "the top N …" in the prose (when the cap is intentional) or
drop the `LIMIT` (when it's just a sample). For ranking questions, write
"Return the top 100 by descending log-odds." `soilBiologicalSample` should drop
`LIMIT 5` or the prose should say "any 5".

Spurious but harmless: scales (`LIMIT 100`, only 75 exist),
securechainkg/ffmpeg-vulnerabilities (`LIMIT 100`, 17 exist),
prokn/kinase_inhibition_phosphosites (`LIMIT 500`, 31 returned). These limits
never bind — they should still be removed to avoid implying a cap.

## 2. `LIMIT` without a total `ORDER BY` → nondeterministic answer

Worse than (1): the truncation is over an unordered or tie-heavy result, so the
"ground truth" itself changes between runs.

- **biobricks-ice / assays-from-invitrodb** — `LIMIT 100`, no `ORDER BY`, 1995 rows. Unreproducible by design.
- **securechainkg / ffmpeg-dependencies** — `LIMIT 100`, no `ORDER BY`, 300 rows.
- **oard ×2** — `ORDER BY DESC(?dist_to_zero) LIMIT 100`, but ties at the cutoff drift between snapshots.

**Fix:** never pair `LIMIT` with a non-total order. Add a deterministic tie-breaker
(e.g. `ORDER BY DESC(score), ?id`) or remove the limit.

## 3. Hard-coded entities/parameters the prose doesn't name (or contradicts)

| Question | Query hard-codes | Prose |
|---|---|---|
| **sockg / soc_stock** | unit **GAJPCSR1_F1H2**, date **1998-04-20** | says unit **"NDMAH3_T", 2008-04-04** — which **does not exist**. Direct contradiction. |
| prokn / kinase_inhibition_phosphosites | perturbagen **SELUMETINIB**; threshold `log2Ratio < -1` | "a perturbagen", "likely downregulated" — neither named |
| hydrologykg / sawgraph-hydrology-04 | a specific **S2 cell** IRI | "a particular S2 cell" — never says which |
| oard / rank-diseases-given-phenotypes | a specific **3-phenotype list** | "a list of phenotypes" — never lists them |
| prokn / gene_properties / protein_properties | **APOE** gene / **TP53** protein | "(e.g., APOE)" / "(e.g., TP53)" — "e.g." reads as illustrative, not the literal filter |

**Fix:** put the exact entity in the prose ("…for experimental unit GAJPCSR1_F1H2
on 1998-04-20", "…downregulated by selumetinib", "…downstream of S2 cell
`<iri>`"). Replace "e.g., APOE" with "for the gene APOE". **Fix the soc_stock
contradiction** — the prose and query must reference the same unit/date.

## 4. Output columns disagree with the prose

| Question | Prose asks for | Query returns |
|---|---|---|
| sockg / fields_in_texas | "city, state abbreviation" | fieldId, site, stateAbbr — **no city** |
| sockg / location | super-locations, sub-locations, **s2 cells** | only `loc` (the concats are dropped/empty) |
| sockg / soil_samples | "**Unique ID**, Treatment ID, Crop, Plant Fraction, Carbon Concentration" | treatmentId, date, crop, plantFraction, carbon_concentration, **Unit** (no unique ID; adds date+Unit) |
| sockg / water_sample | "date, expUnit, treatmentId, **Runoff, growth stage**, etc." | expUnit, treatment, date, SurfOrLeach, LossOrDep, label, Value, Unit (different attributes) |
| sockg / soilBiologicalSample | "date, depths, expUnit, **etc.**" | also SELECTs `?label`, which is always unbound (dead column) |

**Fix:** make the prose's column list exactly match the `SELECT` (names and order
intent), drop "etc.", and remove dead SELECT variables (`?label` here;
`?us_fl_name`/`?ds_fl_name` in hydrology are likewise always empty).

## 5. Computed quantities / thresholds not defined in prose

- **sockg / soc_stock, sock_stock, avg_soc_stock_by_state** — "SOC stock" is computed as `SOC × bulk_density × layer_thickness × 100`; the formula and unit factor are nowhere in the prose.
- **prokn / kinase_inhibition_phosphosites** — "likely to be downregulated" = `log2Ratio < -1` (and it's the `log2Ratio`, not `deltaLog2Ratio`).
- **oard ×2** — "most strongly associated" = rank by `DESC(dist_to_zero)` (absolute log-odds); the metric, plus the `pair_count`/CI columns, aren't described.

**Fix:** state the formula/threshold/metric, or at least name it
("…ranked by absolute log-odds (distance from zero)", "downregulated = log2 ratio
below −1", "SOC stock = SOC concentration × bulk density × layer thickness").

## 6. Ambiguous domain terms (the query commits to one reading)

- **dreamkg / services-available-weekend** — "available on Saturday or Sunday": the query counts a service as available if it merely **has a weekend opening-hours entry**, even one marked closed (00:00–00:00). 87 services qualify; only 9 are actually open. Define "available".
- **prokn / protein_kinases** — "protein kinases" = proteins whose EC string contains a `2.7` component (this even pulls in a few bifunctional non-kinase ECs). Define the kinase criterion.
- **prokn / lincs_kinase_perturbations** — "kinase gene" = gene whose protein has an EC `2.7`; "perturbed in LINCS P100"; plus a **cross-product bug** (see §7). Define each term.
- **nde / nde-influenza-studies** — "influenza related" is implemented as a **hard-coded list of specific MONDO disease IRIs**, not a text/subclass match. Say which diseases count.
- **ubergraph / abdominal-cell-types** — "abdominal organs" = terms that are `is-a organ` **and** `part-of abdomen`. Define the organ set.
- **prokn / alzheimers_associated_genes** — besides "Alzheimer", the query silently requires **GeneSource starting "DDKG"** (drops UniProtKB/GO/IMEx genes). State the source restriction.

**Fix:** spell out the operational definition the query uses.

## 7. The reference query is itself buggy / wrong

- **prokn / lincs_kinase_perturbations** — the pubchem column is joined from the
  P100 perturbagens while the compound→pubchem link is `OPTIONAL`, producing a
  **cross-product**: all 100 rows share one compound label
  ("1-methylisoquinoline") paired with 100 unrelated pubchem IRIs. This is not what
  the prose asks; a correct query returns each qualifying compound once (~6–12).
  **The query (not the prose) should be fixed.**

## 8. Provenance/source filters not surfaced in prose

Covered above for alzheimers (DDKG), lincs (DDKG_LINCS), nde-influenza (MONDO set).
Generally, any `dc:source`/namespace filter that changes the answer should be
named in the prose.

---

## Questions with **no** prose/query inconsistency (clean)

dreamkg/services-in-more-than-one-language, fiokg/NAICS, ncipidkg ×3, nde/resources-by-count,
nde/dataset-count-by-agent, prokn/protein_kinases*, scales/event-labels,
securechainkg/ffmpeg-vulnerabilities, sockg/field_location, spatialkg ×2,
ubergraph/adrenal-gland, ubergraph/processes-that-output-glucose.
(*protein_kinases is answerable but the kinase definition is implicit — see §6.)

## How to improve the prose — checklist

1. **State every cutoff.** "Top N by <metric>" or no `LIMIT` at all.
2. **Make every `LIMIT` deterministic** with a total `ORDER BY` (add a tie-breaker), or remove it.
3. **Name the concrete inputs** — the exact unit, date, compound, phenotype list, S2 cell. No bare "a particular …".
4. **Turn "e.g., X" into "for X"** when X is the actual filter.
5. **List the exact output columns** in the prose; drop "etc."; remove dead SELECT variables.
6. **Define computed values and thresholds** (SOC-stock formula, "downregulated" cutoff, ranking metric).
7. **Operationalise vague terms** ("available", "protein kinase", "abdominal organ", "influenza related", "kinase gene").
8. **Surface source/provenance filters** that change the result.
9. **Fix the data/prose contradiction** in `sockg/soc_stock`, and **fix the buggy query** in `prokn/lincs_kinase_perturbations`.

## Example rewrites

- **sockg / soc_stock** → "Compute the per-layer Soil Organic Carbon (SOC) stock for
  experimental unit **GAJPCSR1_F1H2** on **1998-04-20**, where SOC stock = SOC
  concentration × bulk density × layer thickness × 100. Return experimental-unit ID,
  treatment ID, date, upper/lower depth, SOC, bulk density, layer thickness, and SOC stock."
- **prokn / kinase_inhibition_phosphosites** → "List phosphorylation sites
  downregulated (log2 ratio < −1) in experiments perturbed by **selumetinib**.
  Return perturbagen, experiment, phosphosite, and log2 ratio."
- **oard / phenotypes-associated-with-disease** → "Return the **top 100**
  phenotypes for **Marfan syndrome** ranked by absolute log-odds (distance from
  zero), with the dataset, pair count, log-odds and 95% CI bounds."
- **biobricks-ice / assays-from-invitrodb** → "List **all** InvitroDB-sourced assays
  (no cap)" — and drop the `LIMIT 100` from the query, or specify a deterministic
  ordering and the cap.

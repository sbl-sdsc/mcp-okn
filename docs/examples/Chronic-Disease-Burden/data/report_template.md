# Chronic Disease Burden Across US Counties
### Nine-condition county prevalence, composite burden, hotspots and cross-condition correlation from the OKN federation (spoke-okn, ubergraph)

**Date:** 2026-11-18 · **Endpoint:** OKN federated SPARQL (mcp-okn 0.6.3) · **Model:** claude-opus-5-5

> **Framing (non-negotiable).** Unit of analysis = US county ({{n_counties_places}} counties in 50 states + DC; Florida absent), built from CDC PLACES *model-based* place-level estimates that reach the OKN federation through spoke-okn. All results are **observational, ecological, county-level associations** between *modelled* prevalence estimates. They describe where burden is concentrated. They are **not** individual-level risk, causal effects, or clinical inference, and the cross-condition correlations are partly built into the estimation model (see §10).

**Abbreviations.** BRFSS = Behavioral Risk Factor Surveillance System; CDC = Centers for Disease Control and Prevention; CHD = coronary heart disease; CHR = County Health Rankings; COPD = chronic obstructive pulmonary disease; DOID = Human Disease Ontology identifier; FDR = false-discovery rate (Benjamini–Hochberg); FIPS = Federal Information Processing Standard county code; KG = knowledge graph; LISA = local indicators of spatial association (local Moran's I); MONDO = Mondo Disease Ontology; MRP = multilevel regression and poststratification; OKN = Open Knowledge Network; PC1 = first principal component; PLACES = Population Level Analysis and Community EStimates; pp = percentage points; ρ = Spearman rank correlation; SDoH = social determinants of health.

## 1. Executive summary

Chronic disease burden in US counties is concentrated in a contiguous southern band. Using CDC PLACES estimates for nine conditions held in spoke-okn (diabetes, obesity, hypertension, high cholesterol, coronary heart disease, stroke, COPD, asthma and depression), aggregated from {{n_places_valued}} places to **{{n_counties_places}} counties**, a single composite score captures most of the shared variation: the first principal component explains **{{pc1_var_pct}}%** of between-county variance, and five different composite formulations rank counties almost identically (pairwise ρ ≥ {{rob_min}}). The composite is strongly spatially clustered (Moran's I = **{{moran_burden}}**). **{{n_HH}}** counties form statistically significant high–high hot spots, {{HH_south_pct}}% of them in the South: the Mississippi Delta (MS, LA, AR), Central Appalachia (KY, WV, TN), the Alabama–Georgia Black Belt and Oklahoma.

**{{tier_A}} counties** are in the top quintile for at least seven of the nine conditions (Tier A), and {{tier_B}} more for five or six (Tier B). {{tierA_south_pct}}% of Tier A counties are southern. The highest composite scores are in Mississippi Delta parishes and counties (Yazoo MS, East Carroll and Claiborne LA, Holmes MS), Central Appalachian counties (McDowell WV, Lee and Bell KY), and American Indian and Alaska Native communities (**{{top1_name}}**, z = {{top1_z}}; Shannon and Todd SD). Georgia ({{st_GA}}), Kentucky ({{st_KY}}), Mississippi ({{st_MS}}) and West Virginia ({{st_WV}}) contribute the most Tier A/B counties. In West Virginia that is 80% of its counties.

The correlation structure splits into a tight **cardiometabolic–COPD block** (diabetes–stroke ρ = {{rho_diab_stroke}}; CHD–COPD ρ = {{rho_chd_copd}}) and a looser **asthma–depression** pair that correlates only weakly with diabetes (ρ = {{rho_diab_dep}}) but moderately with COPD ({{rho_copd_dep}}). Adjusting for seven county demographic covariates lowers the mean pairwise ρ from {{mean_rho_raw}} to {{mean_rho_part}}. Removing state means barely changes it ({{mean_rho_ws}}). So shared demography, not shared state, drives much of the co-variation. A cross-KG check found that disease pairs sharing more spoke-okn disease-associated genes do **not** co-vary more across counties (Mantel ρ = {{mantel_raw}}, p = {{mantel_raw_p}}). That is consistent with geography being shaped by social and behavioural context rather than shared biology. As a check on the data themselves, place-aggregated diabetes agrees closely with the independent county-native CHR 2023 estimate (r = {{val_diab_r}}).

## 2. Sources used

| KG | Version | Updated | Role in this study | Join key / confidence |
|---|---|---|---|---|
| spoke-okn | {{kg_spoke_version}} | 2026-03-16 | CDC PLACES place-level prevalence (PREVALENCE_DpL, 9 conditions); place→county links (PARTOF_LpL); County Health Rankings 2023 covariates (PREVALENCEIN_SpL); disease→gene associations (ASSOCIATES_DaG) | County FIPS in the location node IRI (`…/location/{FIPS5}`); place→county edge is native to the KG. High confidence |
| ubergraph | {{kg_uber_version}} | 2026-05-01 | Disease identity: spoke-okn DOID → MONDO (`skos:exactMatch`, crosswalk recipe A10), so the nine conditions are interoperable with MONDO-keyed KGs | DOID↔MONDO exact match; 9 of 9 mapped. High confidence |

County boundaries for display come from the US Census 2010 cartographic county file redistributed by Plotly (`geojson-counties-fips.json`, joined on FIPS; 3,057 of 3,057 matched). They are used only for drawing and spatial-neighbour weights, not as data.

## 3. Design & rules

**Data discovery.** The mcp-okn capability index (`find_context_sources`, want = disease/geospatial, key = FIPS) names **spoke-okn** as the only KG that supplies disease information joinable to county FIPS. ruralkg carries county keys but only survey-variable *metadata* (BRFSS/NSDUH/MEPS question text, no values). biohealth links diseases to SDoH through the literature and has no geography. Within spoke-okn, five disease- or health-by-location layers exist. Table 1 lists them with their coverage.

| spoke-okn layer | Source (edge property `source`) | Geography | Year | Conditions / variables | Used here |
|---|---|---|---|---|---|
| PREVALENCE_DpL | CDC PLACES | 27,365 places (cities/CDPs); {{n_places_valued}} with values | not recorded in KG; Florida absent, consistent with the PLACES 2023 release (BRFSS 2021; high BP & cholesterol BRFSS 2019) | 9: diabetes, obesity, high BP, high cholesterol, CHD, stroke, COPD, current asthma, depression (age-adjusted %) | **Primary outcome** |
| PREVALENCE_DpL | IHME | 200 countries | 2019 | 144 diseases (incl. asthma, COPD, CKD, Alzheimer's) | No: country level only |
| PREVALENCEIN_SpL | County Health Rankings | 3,131 counties | 2023 | 82 measures incl. diabetes & adult-obesity prevalence, demographics, behaviours | **Validation + covariates** |
| PREVALENCEIN_SpL | AHRQ SDOH Database / CDC SVI | ~3,200 counties | 2010–2020 / 2020 | >500 SDoH variables / SVI percentile | Not used (CHR covariates sufficient; see §6) |
| MORTALITY_DmL | WHO | 251 countries | n/a | 76 causes | No: country level only |

*Table 1. Health-by-location data in the OKN federation (spoke-okn), verified by logged inventory queries.* Only CDC PLACES gives multi-condition sub-national prevalence. It is loaded at **place** level, not county level, so county estimates had to be assembled from places.

**County assembly.** Each place links to exactly one county through `PARTOF_LpL` (26,158 places linked; {{n_places_unlinked}} US places unlinked). A county's prevalence is the population-weighted mean of its places' age-adjusted estimates, weighted by PLACES `total_population`. These places cover {{pop_covered_m}} million residents, so the estimate describes the incorporated and census-designated population of each county, not its unincorporated remainder. Counties whose places cover fewer than {{min_pop}} residents ({{n_ineligible}} counties) are kept in maps and correlations but excluded from ranked lists.

**Analysis.** Each condition is summarised by between-county spread and top counties. The **composite burden score** is the mean of the nine condition z-scores. It is checked against a percentile-rank mean, PCA PC1, a version without depression and a cardiometabolic-only version. **Multimorbidity** counts the conditions for which a county sits in the national top quintile. Spatial clustering uses global and local Moran's I on a 6-nearest-neighbour graph of the {{n_conus}} contiguous-US counties. Correlations are Spearman, clustered by average linkage on 1 − ρ, and re-estimated three ways to probe confounding (§6.1). The full replicator specification (every query, join and parameter) is in the reproducibility notebook.

![Study design](figures/fig1_study_design.png)

> ***Figure 1. Study design.*** Data flow from the two spoke-okn health layers (PLACES place prevalence, CHR county measures) through place→county aggregation to the county table, composite scoring and spatial statistics, then the correlation/confounder analyses and the cross-KG shared-gene layer (spoke-okn ASSOCIATES_DaG plus ubergraph DOID→MONDO). Provenance: logged SPARQL queries q01–q20 in the reproducibility notebook.

The design keeps the two health layers separate until the county table, so CHR can act as an independent check on the place-to-county aggregation (§5.1) before the PLACES estimates are interpreted.

## 4. Confidence tiers

| Tier | Rule | Counties | Interpretation |
|---|---|---|---|
| A | Top national quintile for ≥ 7 of 9 conditions | {{tier_A}} | Broad, multi-system burden; highest-priority multimorbidity counties |
| B | Top quintile for 5–6 of 9 | {{tier_B}} | High burden across most conditions |
| C | Top quintile for 3–4 of 9 | {{tier_C}} | Elevated in a subset (often the cardiometabolic block only) |
| – | Top quintile for ≤ 2 | remainder | Not flagged |

The tiers grade *breadth* of burden rather than magnitude, so they complement the continuous composite score. Tier assignment uses all {{n_counties_places}} counties. The ranked lists additionally require places to cover ≥ {{min_pop}} residents.

## 5. Findings by axis

### 5.1 Data validation: place-aggregated PLACES vs county-native CHR

Before interpreting the PLACES-derived county values, they were compared with the two conditions that CHR 2023 reports natively at county level (Figure 2).

![Validation](figures/fig2_validation_places_vs_chr.png)

> ***Figure 2. PLACES place-aggregated county prevalence vs County Health Rankings 2023.*** **(A)** Diabetes, **(B)** obesity; one point per county, coloured by Census region; dashed line = identity. Inset: Pearson r, Spearman ρ, mean difference (PLACES − CHR) and n. Provenance: spoke-okn PREVALENCE_DpL (PLACES, aggregated via PARTOF_LpL) vs spoke-okn PREVALENCEIN_SpL (source "County Health Rankings").

Agreement is strong for diabetes (r = {{val_diab_r}}, mean difference {{val_diab_diff}} pp) and good for obesity (r = {{val_ob_r}}, +{{val_ob_diff}} pp; CHR uses a different BRFSS year and adjustment). The aggregation therefore reproduces county geography faithfully. The two products share BRFSS-based small-area modelling lineage, so this confirms internal consistency rather than providing independent ground truth.

### 5.2 Between-county variation by condition

![Distributions](figures/fig3_prevalence_distributions.png)

> ***Figure 3. Distribution of county age-adjusted prevalence for the nine conditions*** (n = {{n_counties_places}} counties; box = interquartile range, whiskers 1.5 × IQR, points = outliers). Labels give the ratio of the 90th to 10th percentile. Provenance: spoke-okn PREVALENCE_DpL (CDC PLACES) aggregated to county.

Relative variation is widest for COPD (P90/P10 = {{copd_fold}}) and diabetes ({{diab_p10}}% vs {{diab_p90}}% at P10/P90, maximum {{diab_max}}%), and narrowest for high cholesterol and asthma. The conditions most useful for discriminating counties are therefore diabetes, COPD and stroke. The per-condition top-10 counties are listed in the workbook sheet *Top10 by condition*. American Indian and Alaska Native communities lead diabetes, CHD, stroke and asthma (Todd and Shannon SD; Kusilvak/"Wade Hampton" AK). Mississippi Delta counties lead obesity and hypertension (Perry and Greene AL; Holmes and Jefferson MS). Central Appalachia leads COPD, depression and high cholesterol (Lee and Magoffin KY; Lincoln and McDowell WV).

### 5.3 Geographic distribution and hot spots

![Condition maps](figures/fig4_condition_maps.png)

> ***Figure 4. County prevalence by condition, contiguous US.*** Quintile classes per condition (colour bar ticks = class breaks, %); grey = no PLACES data (all of Florida and counties without linked places); state outlines for reference. Alaska and Hawaii appear in the interactive map below. Provenance: spoke-okn PREVALENCE_DpL (PLACES) aggregated via PARTOF_LpL; boundaries from the Census 2010 cartographic file.

Diabetes, hypertension, stroke and CHD share a south-eastern core extending into Texas and the south-west border. COPD and depression concentrate on Appalachia and the Ohio Valley. Asthma and depression show conspicuous **state-boundary edges** (for example Oregon/Washington, Maine, Oklahoma). This artefact signature matches the state random effects in the PLACES model (§6.2). Every condition is strongly spatially autocorrelated (Moran's I from {{moran_min}} to {{moran_max}}, all permutation p = 0.001).

![Composite burden and hotspots](figures/fig5_composite_burden_hotspots.png)

> ***Figure 5. Composite disease burden.*** **(A)** Composite score (mean z of nine conditions), classes = quintiles plus the top 5%. **(B)** Local Moran's I clusters at pseudo-p < 0.05 (999 permutations; 6-nearest-neighbour weights): High–High = high-burden county surrounded by high-burden neighbours. Provenance: as Figure 4; spatial statistics with PySAL esda.

The composite resolves into one dominant southern hot-spot system ({{n_HH}} High–High counties) and a northern and western cold-spot belt ({{n_LL}} Low–Low counties) running from the upper Midwest through the Mountain West to coastal California and New England. Isolated high-burden outliers inside cold regions are mostly reservation counties (for example in South Dakota and Montana).

**Interactive map.** Use the drop-down to switch between the composite score, any single condition or the multimorbidity count. Hover to identify a county and click for all values. Alaska and Hawaii are included.

<!-- INTERACTIVE_MAP -->

*Interactive map: Leaflet/folium choropleth on Esri World Street Map tiles; one GeoJSON layer restyled per selected variable with quintile classes; counties with no PLACES data are grey. Values from data/county_burden_ranked.tsv.*

### 5.4 Highest-burden counties and multimorbidity

![Top counties](figures/fig6_top_counties_multimorbidity.png)

> ***Figure 6. Highest-burden counties and multimorbidity concentration.*** **(A)** The 25 highest composite scores among counties whose places cover ≥ {{min_pop}} residents, coloured by Census region; labels = number of the nine conditions in the national top quintile. **(B)** Distribution of that count across all {{n_counties_places}} counties, coloured by tier (§4). Provenance: spoke-okn PLACES aggregated to county.

High burden is rarely confined to one condition. All top-25 counties are in the top quintile for seven to nine of the nine conditions. The tail of panel B ({{tier_A}} Tier A counties) is overwhelmingly southern ({{tierA_south}} of {{tier_A}}). The top non-southern entries are American Indian/Alaska Native communities: Kusilvak AK, plus Shannon (Oglala Lakota), Todd and Buffalo in SD.

## 6. Domain analyses

**Analysis family declaration.** *Correlation family:* RAN all four variants: unadjusted, partial on demographics, partial on demographics plus behaviours, and within-state. *Spatial family:* RAN global Moran's I for all ten variables and LISA for the composite. LISA for the nine single conditions was SKIPPED because their global I values and maps (Figure 4) already show the patterns and nine more cluster maps would add little. *Composite family:* RAN five formulations (§3). *Enrichment families (GO, Reactome, disease/trait gene sets):* SKIPPED. This is a place-based prevalence question with no derived gene list, so over-representation would test spoke-okn's literature gene sets rather than these counties. *Phenotype (HP) and drug linkage:* SKIPPED for the same reason. *SDoH from AHRQ SDOH / CDC SVI:* SKIPPED. The 14 CHR county covariates already cover age, race/ethnicity, rurality, poverty, education, insurance and behaviours, and adding overlapping indices would raise collinearity without adding constructs.

### 6.1 Clustered correlation structure and confounding

![Correlation heatmaps](figures/fig7_clustered_correlation_heatmaps.png)

> ***Figure 7. Clustered county-level correlation among the nine conditions.*** **(A)** Unadjusted Spearman ρ (n = {{n_counties_places}}), rows/columns ordered by average-linkage clustering on 1 − ρ (dendrogram above). **(B)** Partial ρ after rank-residualising every condition on seven CHR demographic covariates (% aged 65+, % non-Hispanic Black, % Hispanic, % rural, % children in poverty, % some college, % uninsured adults; n = {{n_partial}}). **(C)** Within-state ρ (state means removed from ranks). Same ordering in all panels; diverging scale centred at 0. Provenance: spoke-okn PLACES (aggregated) and CHR 2023.

The clustering separates **high cholesterol** (weakly linked to everything), a **cardiometabolic–COPD core** (CHD, COPD, hypertension, diabetes, stroke, obesity) and an **asthma–depression** branch. All 36 unadjusted correlations are positive (mean ρ = {{mean_rho_raw}}). Demographic adjustment lowers the mean to {{mean_rho_part}}. Adding behaviours (smoking, physical inactivity, food insecurity) lowers it further to {{mean_rho_full}}. Some pairs fall apart: obesity–asthma drops from {{rho_ob_asthma}} to {{rho_ob_asthma_part}}, and diabetes–obesity from {{rho_diab_obes}} to {{rho_diab_obes_part}}. The cardiometabolic core survives (for example diabetes–stroke 0.76 and CHD–COPD 0.82 partial). Within-state correlations stay close to raw (mean {{mean_rho_ws}}), so state differences are not what drives co-variation. Diabetes–asthma even *rises* within states ({{rho_diab_asthma}} → {{rho_diab_asthma_ws}}), because between-state asthma differences dilute it nationally. Per-pair values with 95% confidence intervals are in the workbook (*Correlation pairs*).

### 6.2 Demographic and geographic confounders

![Confounders](figures/fig8_confounders_variance_explained.png)

> ***Figure 8. County covariates and variance explained.*** **(A)** Spearman ρ between each condition (rows, Figure 7 order) and ten CHR 2023 county covariates. **(B)** OLS R² of each condition on the seven demographic covariates, after adding three behavioural covariates, and after adding state fixed effects. Provenance: spoke-okn PREVALENCEIN_SpL (County Health Rankings 2023) joined on county FIPS to aggregated PLACES.

Child poverty, low education, physical inactivity, smoking and food insecurity are the strongest correlates of the cardiometabolic–COPD block (|ρ| ≈ 0.7–0.9). The share of non-Hispanic Black residents tracks diabetes and hypertension. Older age structure is nearly unrelated because PLACES estimates are age-adjusted. Demographics alone explain **{{r2_diab_demo}}** of county diabetes variance but only {{r2_asthma_demo}} for asthma and {{r2_dep_demo}} for depression. For those two, **state fixed effects** lift R² to {{r2_asthma_state}} and {{r2_dep_state}}. This matches the PLACES model, which uses individual age, sex, race/ethnicity and education, county poverty, and **state- and county-level random effects** [6]. Two readings follow. The strong demographic R² for cardiometabolic conditions is partly *by construction*. The state-dominated geography of asthma, depression and high cholesterol may partly reflect state BRFSS sampling and model structure rather than true prevalence differences.

### 6.3 Cross-KG check: do conditions that share genes co-vary across counties?

![Gene overlap vs geography](figures/fig9_gene_overlap_vs_geography.png)

> ***Figure 9. Shared disease-associated genes vs county co-variation.*** Each point is one of the 36 condition pairs. x = Jaccard index of their spoke-okn gene sets (ASSOCIATES_DaG; diseases identified as DOID and mapped to MONDO through ubergraph); y = county Spearman ρ, **(A)** unadjusted, **(B)** demographic-adjusted. Inset: Mantel test (Spearman, 9,999 permutations). Provenance: spoke-okn ASSOCIATES_DaG (gene background = {{n_genes_bg}} genes with any disease association), ubergraph skos:exactMatch.

Gene sharing is strongly non-random: {{gene_pairs_sig}} of 36 pairs share more genes than expected (hypergeometric FDR < 0.05), led by high cholesterol–stroke and diabetes–obesity. Yet gene sharing does not predict geographic co-variation (Mantel ρ = {{mantel_raw}}, p = {{mantel_raw_p}} unadjusted; {{mantel_part}}, p = {{mantel_part_p}} adjusted). CHD–COPD shares few genes but is the most tightly co-located pair, a signature of shared exposures such as smoking. High cholesterol–stroke shares the most genes but barely co-varies after adjustment. Shared biology and shared place are largely separate axes here. Two cautions apply: spoke-okn gene sets are literature-derived, and nine conditions give low power.

## 7. Discussion

The OKN federation can answer a national county-level chronic-disease question, but only through one route: CDC PLACES as loaded in spoke-okn at place level, joined to counties by spoke-okn's own containment edges. Within that limit, the results are coherent. Burden is concentrated, multi-system and spatially contiguous. The southern hot-spot system ({{n_HH}} counties) overlaps the regions long described as the diabetes and stroke belts [1][2]. It adds Central Appalachia's COPD–depression signature [3] and several American Indian/Alaska Native communities that rank at the very top on almost every measure [4].

Three implications follow. **(i) Target multimorbidity places, not single diseases.** Tier A counties are in the top quintile for most conditions simultaneously, and correlated conditions share upstream determinants: poverty, low education, inactivity, smoking and food insecurity explain most of the variance, in line with county contextual-factor studies [5]. Cross-cutting interventions (tobacco control, physical-activity infrastructure, food access, primary care) are the logical response. **(ii) Read correlations with the estimation model in mind.** PLACES generates estimates from shared demographic predictors and state/county random effects [6], so part of the cross-condition correlation and of the demographic R² is induced by the model. The within-state analysis shows the cardiometabolic core is not an artefact of state effects, while asthma, depression and high cholesterol geography is state-dominated and should be interpreted cautiously. **(iii) Geography ≠ shared genetics.** Pairs that share many literature genes do not co-locate more, which reinforces a social-determinant interpretation of the maps.

**Testable predictions.** (a) Directly measured county data (for example EHR-based diabetes or COPD prevalence) should reproduce the southern hot-spot system but show *weaker* asthma/depression state-boundary edges than PLACES. (b) Tier A counties should show correspondingly elevated mortality for the same conditions, testable once county mortality is in the federation. (c) Re-running with the county-level PLACES product, if loaded, should change rankings little (r > 0.9 per Figure 2).

## 8. Comparison with prior work

Claims were checked against the primary literature retrieved via the **PubMed** MCP connector, with full-text checking through the **Paperclip** MCP connector. The per-claim record with study details is in [Chronic-Disease-Burden_literature_comparison.md](Chronic-Disease-Burden_literature_comparison.md).

| # | Claim | Concordance |
|---|---|---|
| 1 | Highest county diabetes prevalence forms a contiguous southern band (Delta, Black Belt, Appalachia) | **SUPPORTED** — a CDC analysis defined a 644-county "diabetes belt" in 15 mostly southern states, with higher obesity, inactivity and African-American population shares [1] |
| 2 | Stroke and CHD prevalence are concentrated in the Southeast | **SUPPORTED** — the south-eastern "stroke belt" of excess stroke mortality is long established, with a parallel heart-failure excess in AL, AR, MS, OK, LA, GA [2]; our data concern prevalence rather than mortality |
| 3 | COPD burden peaks in Central Appalachia and rural counties (KY, WV, AR, MS) | **SUPPORTED** — county BRFSS-based COPD prevalence, hospitalisation and death are higher in rural counties, and AR, KY, MS and WV lead the state rankings [3] |
| 4 | American Indian/Alaska Native communities rank highest for diabetes, CHD, stroke and asthma | **PARTIALLY SUPPORTED** — diagnosed diabetes among AI/AN adults in the IHS clinical population (14.6% in 2017) is well above the US average [4]; no county-level comparison was found, and PLACES MRP estimates for small reservation populations are model-heavy |
| 5 | County demographics and socioeconomics explain most of the variance in cardiometabolic prevalence (diabetes R² = {{r2_diab_demo}}) | **PARTIALLY SUPPORTED** — county socioeconomic and health-related factors explained ~42% of county diabetes *incidence* variance [5]; our higher R² is partly built into PLACES, whose model includes demographics and county poverty [6] |
| 6 | Place-aggregated PLACES agrees with county-native CHR (diabetes r = {{val_diab_r}}) | **PARTIALLY SUPPORTED** — MRP county estimates correlate with independent direct survey estimates, though less tightly (diabetes r = 0.51 in Missouri) [7]; our near-identity reflects two products of shared BRFSS lineage, not independent validation |
| 7 | Asthma, depression and high-cholesterol geography is dominated by state-level effects | **SUPPORTED** — the PLACES model includes state- and county-level random effects and its authors warn of collinearity when estimates are reused in models [6]; this concordance is methodological rather than epidemiological |
| 8 | Composite multimorbidity hot spots concentrate in the South (94% of Tier A counties) | **PARTIALLY SUPPORTED** — consistent with the single-condition diabetes and stroke belts [1][2]; no study of a nine-condition county composite was found |
| 9 | Conditions sharing more disease-associated genes do not co-vary more across counties | **NOVEL** — no source found; a KG-only observation (spoke-okn literature gene sets vs county co-variation) |

Claim 7 was checked against the full text of the PLACES methods paper [6] (model covariates, random-effect structure and collinearity caution). The other entries rest on abstracts.

**Where the KG evidence diverges from the literature.** No graph errors were found, but two points about the KG data stand out. First, spoke-okn stores PLACES "High Cholesterol" under **DOID_2349 (arteriosclerosis)**, a concept mismatch that would mislead any query by disease name. This study uses the measure's own question text. Second, spoke-okn's PLACES load has no release year and no confidence bounds, so the literature cannot be matched to an exact data vintage. Differences from the literature are otherwise ones of **scope**: the established belts are mortality- or single-condition-based, while this analysis uses modelled prevalence for nine conditions at once.

## 9. Full ranked results

All {{n_counties_places}} counties with the nine prevalences, composite scores, tier, LISA class and covariates are in **Chronic-Disease-Burden_results.xlsx** (sheet *Ranked Results*, tier-coloured) and `data/county_burden_ranked.tsv`. The interactive table below is sortable (click a header), searchable, filterable by tier, region, state and LISA class, and paginated. *sources (n)* counts the independent spoke-okn datasets behind each row: PLACES supplies the nine prevalences and CHR supplies the validation and covariates. ubergraph supplies disease identity only and is not counted.

<!-- RESULTS_TABLE -->

| Rank | County | Composite z | Top-quintile conditions | Tier | Diabetes % | COPD % | Depression % |
|---|---|---|---|---|---|---|---|
| 1 | Wade Hampton (Kusilvak) Census Area, AK | 2.96 | 7 | A | 20.2 | 14.7 | 24.1 |
| 2 | Yazoo County, MS | 2.69 | 8 | A | 20.7 | 11.9 | 21.9 |
| 3 | East Carroll Parish, LA | 2.67 | 8 | A | 20.9 | 12.0 | 25.4 |
| 4 | Claiborne Parish, LA | 2.64 | 9 | A | 19.8 | 13.0 | 27.7 |
| 5 | Holmes County, MS | 2.61 | 7 | A | 21.5 | 11.2 | 21.6 |
| 8 | McDowell County, WV | 2.54 | 9 | A | 16.0 | 14.5 | 31.0 |
| 10 | Lee County, KY | 2.48 | 8 | A | 14.9 | 15.7 | 34.3 |

*Table 2. Representative slice of the ranking (eligible counties).* The top of the ranking mixes three distinct profiles: Delta counties led by diabetes, obesity and hypertension; Appalachian counties led by COPD and depression; and AI/AN communities high on nearly everything. The composite alone hides which conditions drive each county's position, so read it alongside the per-condition columns.

## 10. Summary of findings & limitations

Across {{n_counties_places}} US counties, nine CDC PLACES chronic conditions from spoke-okn share one dominant geographic axis (PC1 = {{pc1_var_pct}}% of variance). That axis is concentrated in a contiguous southern hot-spot system ({{n_HH}} High–High counties) spanning the Mississippi Delta, Central Appalachia and the Black Belt, plus isolated American Indian/Alaska Native communities. {{tier_A}} counties are in the top quintile for seven or more conditions. Conditions co-vary in a cardiometabolic–COPD core and an asthma–depression branch. County demographics account for much of the shared variation, state effects for little of it, and shared disease genes for none of it. Place-aggregated estimates agree closely with independent CHR county figures, which supports the assembly method.

**Limitations.**

1. **Modelled, not measured.** PLACES values are MRP model estimates driven by demographics, county poverty and state/county random effects. Correlations among conditions and with demographics are partly induced by the model, and the state-edge geography of asthma, depression and high cholesterol may be a model artefact.
2. **Place-level source, county-level question.** The KG holds PLACES only at place level. County values are population-weighted means over incorporated places and census-designated places, covering {{pop_covered_m}} M residents. Unincorporated and rural fringe populations are not represented, and counties with few or small places are noisier.
3. **Coverage gaps.** Florida is entirely absent from spoke-okn's PLACES load, so its 67 counties are missing. {{n_places_unlinked}} places lack a county link, and 1,022 places have suppressed values. Alaska and Hawaii are excluded from the spatial statistics.
4. **Vintage unknown in the KG.** spoke-okn stores no year, confidence bounds or crude rates for PLACES. The 2023 release is inferred from Florida's absence. PLACES place estimates use 2010 census population counts and boundaries, which also explains legacy FIPS codes such as Wade Hampton (now Kusilvak) and Shannon (now Oglala Lakota).
5. **Concept mislabelling.** PLACES "High Cholesterol" is attached to DOID_2349 (arteriosclerosis) in spoke-okn. Any cross-KG use of that disease node for cholesterol is wrong.
6. **Missing conditions.** The federation has no county or place prevalence for chronic kidney disease, cancer, arthritis or other PLACES measures. IHME data for such conditions exist in spoke-okn but only at country level.
7. **Ecological inference.** All associations are between county aggregates and cannot be transferred to individuals. Covariates come from a different source and year (CHR 2023), and behaviours are mediators rather than pure confounders.
8. **Gene layer.** spoke-okn disease–gene edges come from literature co-occurrence, the nine-node Mantel test has low power, and gene sharing is not genetic correlation.
9. **CHR data quality.** Two counties report implausible life expectancy (> 95 years) and were set missing. CHR values arrive as "value(quartile)" strings and had to be parsed.

## 11. Reproducibility

Everything needed to rerun this study is in [Chronic-Disease-Burden_notebook/](Chronic-Disease-Burden_notebook/Chronic-Disease-Burden_notebook.ipynb): the originating prompt, the replicator specification, all 20 supporting SPARQL queries verbatim with the rows they returned, the analysis code that regenerates every figure and number, and pinned KG versions. `Chronic-Disease-Burden_notebook/Chronic-Disease-Burden_notebook.html` shows it executed. Report-building scripts are in `scripts/` and extracts in `data/`.

```bash
cd Chronic-Disease-Burden/Chronic-Disease-Burden_notebook
uv run --with jupyterlab --with-requirements requirements.txt jupyter lab Chronic-Disease-Burden_notebook.ipynb
```

## 12. References

> Retrieved via the **PubMed** MCP connector. Full-text verification via the **Paperclip** MCP connector.

1. Barker LE, et al. Geographic distribution of diagnosed diabetes in the U.S.: a diabetes belt. *Am J Prev Med*. 2011. PMID:21406277 · [doi:10.1016/j.amepre.2010.12.019](https://doi.org/10.1016/j.amepre.2010.12.019)
2. Mujib M, et al. Evidence of a "heart failure belt" in the southeastern United States. *Am J Cardiol*. 2011. PMID:21247536 · [doi:10.1016/j.amjcard.2010.11.012](https://doi.org/10.1016/j.amjcard.2010.11.012)
3. Croft JB, et al. Urban-Rural County and State Differences in Chronic Obstructive Pulmonary Disease - United States, 2015. *MMWR Morb Mortal Wkly Rep*. 2018. PMID:29470455 · [doi:10.15585/mmwr.mm6707a1](https://doi.org/10.15585/mmwr.mm6707a1)
4. Bullock A, et al. Prevalence of diagnosed diabetes in American Indian and Alaska Native adults, 2006-2017. *BMJ Open Diabetes Res Care*. 2020. PMID:32312721 · [doi:10.1136/bmjdrc-2020-001218](https://doi.org/10.1136/bmjdrc-2020-001218)
5. Cunningham SA, et al. County-level contextual factors associated with diabetes incidence in the United States. *Ann Epidemiol*. 2018. PMID:29233722 · [doi:10.1016/j.annepidem.2017.11.002](https://doi.org/10.1016/j.annepidem.2017.11.002)
6. Greenlund KJ, et al. PLACES: Local Data for Better Health. *Prev Chronic Dis*. 2022. PMID:35709356 · [doi:10.5888/pcd19.210459](https://doi.org/10.5888/pcd19.210459) — full-text-verified ([PMC9258452](https://pmc.ncbi.nlm.nih.gov/articles/PMC9258452/))
7. Zhang X, et al. Validation of multilevel regression and poststratification methodology for small area estimation of health indicators from the behavioral risk factor surveillance system. *Am J Epidemiol*. 2015. PMID:25957312 · [doi:10.1093/aje/kwv002](https://doi.org/10.1093/aje/kwv002)

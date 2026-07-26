# Urban-Scaling — literature comparison (per-claim record)

Companion to `Urban-Scaling_report.md` §8. One entry per checked claim, with the concordance label, the evidence, and the citations. Retrieval via the **PubMed** and **Paperclip** MCP connectors.

Concordance labels used: **SUPPORTED** · **PARTIALLY SUPPORTED** · **CONTRADICTED** · **MIXED** · **NOVEL** · **UNRESOLVED**.

---

### Claim 1 — All-cause / premature mortality scales sublinearly with city size in the US

**This analysis found:** premature death (YPLL) β = 0.924 (95% CI 0.916–0.933); premature age-adjusted mortality β = 0.955 (0.948–0.962). Both hold direction and significance when restricted to metropolitan counties (β = 0.927 and 0.938). Tier A.

**Concordance: SUPPORTED.** Bilal et al. analysed vital-registration data for 742 cities across 10 Latin American countries and the United States and report that "more populated cities had lower mortality (sublinear scaling), driven by a sublinear pattern in U.S. cities," while Latin American cities showed similar mortality across city sizes [1]. Our US-only county-level estimate sits in the same regime and direction. The caveat that qualifies the agreement is unit mismatch: Bilal et al. fit metropolitan areas with population ≥ 100,000, whereas this analysis fits counties across the full size range; the agreement in direction is therefore more meaningful than the agreement in magnitude.

---

### Claim 2 — Non-communicable chronic disease burden is sublinear-to-linear in the US, not superlinear

**This analysis found:** across all 26,343 census places, β = 0.963–1.002 for nine chronic conditions (sublinear or indistinguishable from linear). Across the 709 places ≥ 50,000, six of nine become superlinear (β up to 1.079 for diabetes). Tier C.

**Concordance: PARTIALLY SUPPORTED.** Bilal et al. report that "deaths due to noncommunicable diseases were generally sublinear in the United States and linear or superlinear in Latin America" [1], which matches our full-sample fits. But the scoping review by McCulley et al., covering 102 studies, characterises NCDs as showing "a heterogeneous pattern that depends on the specific outcome and context" rather than a settled direction [2]. Our own reversal between samples reproduces that heterogeneity within a single dataset, so the literature supports the full-sample direction but does not support treating any single exponent as the chronic-disease scaling law.

---

### Claim 3 — Scaling exponents depend materially on how cities are spatially defined

**This analysis found:** re-fitting the same nine conditions at progressively higher minimum-population cutoffs moves β monotonically upward, e.g. diabetes from 0.996 (all places) to 1.075 (places ≥ ~60,000), a swing far exceeding any individual fit's confidence interval.

**Concordance: SUPPORTED.** Arcaute et al. built thousands of alternative systems of cities for England and Wales using commuting and density thresholds and concluded that "population size alone does not provide us enough information to describe or predict the state of a city as previously proposed, indicating that the expected scaling laws are not corroborated," further noting that where nonlinear correlations exist "the exponent fluctuates considerably" [3]. Cottineau et al. reach the same conclusion, that urban scaling values are not universal and depend non-trivially on how cities are constructed from census areal data [4]. Our threshold ladder is a direct, single-dataset demonstration of the same effect.

---

### Claim 4 — The population–outcome relationship departs from a single power law, with a rural/urban breakpoint

**This analysis found:** binned prevalence curves are U-shaped for diabetes, stroke, hypertension and asthma, with a minimum around 30,000–100,000 population; a quadratic term in ln N is significant for seven of nine conditions.

**Concordance: SUPPORTED.** Sutton et al., analysing 117 indicators across Middle Layer Super Output Areas in England and Wales, found that "the relationship between indicator density and population density is best described by a segmented power law model with a consistent breakpoint (33 ± 5 persons per hectare) for 92 of the 117 indicators" [5]. Hanley et al. earlier found four distinct scaling regimes for crime and property transactions with rural-to-urban transitions occurring universally between 10 and 70 people per hectare [6]. Both are density-space analyses while ours is population-space, so the breakpoint values are not directly comparable; the supported claim is the existence of a regime change, not its location.

---

### Claim 5 — Crime scales superlinearly with city size (β ≈ 1.16)

**This analysis found:** federal criminal case filings scale at β = 0.803 (0.767–0.839) across 2,377 counties, and β = 1.048 (0.990–1.105, indistinguishable from linear) across 1,035 metropolitan counties. Rate-regression R² = 0.047. Tier B.

**Concordance: UNRESOLVED.** The literature consistently reports superlinear scaling for serious crime — Bettencourt et al. place socioeconomic indicators including crime near β ≈ 1.15–1.2 [7], and Oliveira's cross-country study of 12 countries finds theft increasing superlinearly with population and argues per-capita rankings misrepresent city crime levels [8]. Our measure cannot test this. `scales` records federal district-court filings; the overwhelming majority of US crime is prosecuted in state courts, and federal caseload geography is shaped by prosecutorial priorities, southern-border immigration enforcement, and federal jurisdiction over tribal land. The result is therefore a bounded null on a different quantity, not evidence against the literature. Resolving it would require a state-court or police-recorded crime source, which the federation does not currently carry at county level.

---

### Claim 6 — Motor-vehicle / traffic death scaling is steeply sublinear

**This analysis found:** β = 0.736 (0.724–0.747), the steepest gradient in the study, with the highest rate-regression R² (0.439); metro-restricted β = 0.769. Tier A.

**Concordance: PARTIALLY SUPPORTED.** The direction is unambiguous in our data and mechanistically plausible (rural road exposure, higher speeds, longer emergency response times). However McCulley et al. report that "traffic-related injuries show a less clear pattern that differs by context and type of injury" [2], so the literature does not endorse a single steep exponent. Ours is a strong result within one country and one injury type; generalising it would overstate the evidence.

---

### Claim 7 — Larger cities show a protective effect for chronic disease in older populations

**This analysis found:** full-sample coronary artery disease β = 0.975 and stroke β = 0.985, both significantly sublinear — i.e. lower age-adjusted prevalence in larger places.

**Concordance: SUPPORTED.** Sutton et al. report that "stratifying dementia and ischaemic heart disease by older age groups (aged 70 and above) significantly affects these exponents, illustrating a protective urban effect" [5]. The direction agrees with our full-sample cardiovascular fits. The qualification is that our estimates are age-adjusted across all adults rather than stratified to 70+, so we cannot confirm that the protective effect is concentrated in older ages as Sutton et al. specifically report.

---

### Claim 8 — Cross-sectional scaling exponents describe differences between cities, not the trajectory of a growing city

**This analysis found:** framing only — this claim governs the report's interpretation, not a fitted number.

**Concordance: SUPPORTED.** Marquis and Barthelemy investigated how urban scaling laws relate to individual city growth and found that cross-sectional scaling laws reflect city population heterogeneity rather than individual city dynamics [9]. This is the basis of the framing caveat in the report's title block and limitation 1. Note this evidence is **preprint-only** (arXiv, not peer-reviewed); the underlying methodological point, however, is long-standing in the scaling literature and is not controversial.

---

### Claim 9 — Suicide and self-harm mortality are more common in smaller settlements

**This analysis found:** not testable. `spoke-okn` carries a `Suicide (event)` SDoH concept node but no county-level suicide-rate measurement in `PREVALENCEIN_SpL`.

**Concordance: UNRESOLVED.** McCulley et al. report that "suicides are more common in smaller cities" [2], which would imply sublinear scaling and would be consistent with the rest of our mortality family. We could not test it within the federation. This is recorded as a coverage gap rather than a negative result.

---

### Claim 10 — Population size is a weak predictor of outcome *rates* even when the exponent is precisely estimated

**This analysis found:** rate-regression R² across the 18 series ranges from 0.0003 (depression, ≥50k subsample) to 0.439 (motor-vehicle crash deaths); the median is under 0.05. The corresponding count-regression R² values run 0.45–0.998.

**Concordance: NOVEL.** No source found stating this as an explicit result. The underlying mechanism — that regressing ln(rate × N) on ln(N) puts N on both sides and inflates R² toward 1 — is well understood in the spurious-correlation literature and is implicit in Arcaute et al.'s critique that population alone poorly predicts city state [3], but we found no paper reporting the rate-regression R² alongside urban scaling exponents as a routine diagnostic. We flag it as a reporting recommendation rather than a discovery: an exponent's precision and its explanatory power are independent properties, and reporting only the former invites over-reading.

---

## References

1. Bilal U, et al. Scaling of mortality in 742 metropolitan areas of the Americas. *Sci Adv*. 2021. PMID:34878846 · [doi:10.1126/sciadv.abl6325](https://doi.org/10.1126/sciadv.abl6325) — full-text-verified ([PMC8654292](https://pmc.ncbi.nlm.nih.gov/articles/PMC8654292/))
2. McCulley EM, et al. Urban Scaling of Health Outcomes: a Scoping Review. *J Urban Health*. 2022. PMID:35513600 · [doi:10.1007/s11524-021-00577-4](https://doi.org/10.1007/s11524-021-00577-4) — full-text-verified ([PMC9070109](https://pmc.ncbi.nlm.nih.gov/articles/PMC9070109/))
3. Arcaute E, et al. Constructing cities, deconstructing scaling laws. *J R Soc Interface*. 2015. PMID:25411405 · [doi:10.1098/rsif.2014.0745](https://doi.org/10.1098/rsif.2014.0745)
4. Cottineau C, et al. Diverse cities or the systematic paradox of urban scaling laws. *Computers, Environment and Urban Systems*. 2017. [doi:10.1016/j.compenvurbsys.2016.04.006](https://doi.org/10.1016/j.compenvurbsys.2016.04.006)
5. Sutton J, et al. Comprehensive indicators and fine granularity refine density scaling laws in rural-urban systems. *Sci Rep*. 2026. PMID:41741585 · [doi:10.1038/s41598-026-40238-7](https://doi.org/10.1038/s41598-026-40238-7)
6. Hanley QS, et al. Rural to urban population density scaling of crime and property transactions in English and Welsh Parliamentary Constituencies. *PLoS One*. 2016. [doi:10.1371/journal.pone.0149546](https://doi.org/10.1371/journal.pone.0149546)
7. Bettencourt LMA, et al. Growth, innovation, scaling, and the pace of life in cities. *Proc Natl Acad Sci U S A*. 2007. PMID:17438298 · [doi:10.1073/pnas.0610172104](https://doi.org/10.1073/pnas.0610172104) — full-text-verified ([PMC1852329](https://pmc.ncbi.nlm.nih.gov/articles/PMC1852329/))
8. Oliveira M. More crime in cities? On the scaling laws of crime and the inadequacy of per capita rankings. *Crime Science*. 2021. [doi:10.1186/s40163-021-00155-8](https://doi.org/10.1186/s40163-021-00155-8)
9. Marquis U, Barthelemy M. On the Meaning of Urban Scaling. *arXiv* (preprint — not peer-reviewed). 2026. [doi:10.48550/arXiv.2603.30021](https://doi.org/10.48550/arXiv.2603.30021)

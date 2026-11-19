# Chronic-Disease-Burden — literature comparison (per-claim record)

This is the per-claim record behind §8 of the report. Literature was retrieved through the **PubMed** MCP connector. The PLACES methods paper [6] was also read in full through the **Paperclip** MCP connector, and its full text was used to check Claim 7. Each claim is stated as the analysis found it, followed by its concordance label and the evidence. Claim numbers match the §8 table.

## Claim 1 — Southern diabetes band

*Analysis:* county diabetes prevalence (PLACES via spoke-okn) is highest in the Mississippi Delta, Alabama–Georgia Black Belt and Central Appalachia (Figure 4, §5.3), and local Moran's I places 93% of composite hot-spot counties in the South.

**Concordance: SUPPORTED.** Barker et al. combined 2007–2008 BRFSS data with county estimates and defined a "diabetes belt" of 644 counties in 15 mostly southern states. Belt residents were more likely to be non-Hispanic African American, sedentary and obese; about 30% of the excess risk was linked to modifiable and 37% to non-modifiable factors [1]. Our diabetes map, and the strong county correlations of diabetes with inactivity (ρ = 0.84) and % non-Hispanic Black (ρ = 0.52), reproduce this pattern about a decade later.

## Claim 2 — South-eastern concentration of stroke and CHD

*Analysis:* stroke and CHD prevalence share the south-eastern core with diabetes (diabetes–stroke ρ = 0.94).

**Concordance: SUPPORTED.** The south-eastern "stroke belt" of excess stroke mortality is the reference geography; Mujib et al. also documented a "heart failure belt" with 69% higher heart-failure mortality in AL, AR, MS, OK, LA and GA [2]. *Qualifier:* the literature describes mortality, while this analysis uses modelled prevalence.

## Claim 3 — COPD in Central Appalachia and rural counties

*Analysis:* the highest county COPD values are in eastern Kentucky (Lee 15.7%, Bell 14.6%) and West Virginia. COPD correlates with smoking at ρ = 0.88.

**Concordance: SUPPORTED.** A CDC analysis of 2015 BRFSS, Medicare and vital-statistics data found COPD prevalence, hospitalisations and deaths all higher in rural than in urban counties, with Arkansas, Kentucky, Mississippi and West Virginia in the top quartile on all measures and for rural residents [3].

## Claim 4 — American Indian/Alaska Native communities at the top

*Analysis:* Todd and Shannon (Oglala Lakota) SD and Wade Hampton (Kusilvak) AK lead diabetes, CHD, stroke and asthma, and Kusilvak has the highest composite score.

**Concordance: PARTIALLY SUPPORTED.** Diagnosed diabetes in AI/AN adults served by the Indian Health Service was 14.6% in 2017, well above the US average, though it declined after 2013 [4]. No peer-reviewed county-level comparison for these specific counties was found. PLACES estimates for small, demographically distinctive populations rest heavily on the model's race/ethnicity terms, so the extreme values should be treated cautiously.

## Claim 5 — Demographics explain most cardiometabolic variance

*Analysis:* seven CHR demographic covariates explain R² = 0.81 of county diabetes variance (0.83 stroke, 0.79 hypertension).

**Concordance: PARTIALLY SUPPORTED.** Cunningham et al. found that socioeconomic and health-related county characteristics explained about 42% of between-county variation in age-standardised diabetes *incidence* (n = 3,109 counties), with poverty, unemployment and long commutes as risk factors and exercise opportunities, healthy food access and primary care as protective factors [5]. The direction agrees. Our much higher R² is partly built in, because PLACES estimates are generated from demographic predictors and county poverty [6], and prevalence differs from incidence.

## Claim 6 — PLACES place aggregate agrees with CHR county estimates

*Analysis:* diabetes r = 0.94 (mean difference +0.35 pp) and obesity r = 0.83 between the place-aggregated PLACES values and CHR 2023 county values.

**Concordance: PARTIALLY SUPPORTED.** External validation of the CDC MRP method against the Missouri County-Level Study found positive but moderate county correlations (diabetes 0.51, obesity 0.28, COPD 0.69) [7]. Our much tighter agreement shows that the place-to-county aggregation is faithful. It is not independent validation, because both products share BRFSS small-area modelling lineage.

## Claim 7 — State effects dominate asthma, depression and high-cholesterol geography

*Analysis:* adding state fixed effects lifts R² from 0.52 to 0.88 for asthma and from 0.46 to 0.89 for depression. The maps show state-boundary edges.

**Concordance: SUPPORTED.** Read in full: the PLACES methods paper describes a multilevel logistic model with individual age, sex, race/ethnicity and education, county poverty from the American Community Survey, and **state- and county-level random effects**. It warns that because the estimates already incorporate these factors, "some statistical collinearity is possible" when they are reused in other models [6]. *Qualifier:* the concordance is methodological. It explains the pattern as a property of the estimator and does not establish that true prevalence differs by state.

## Claim 8 — Multimorbidity hot spots in the South

*Analysis:* 241 of 256 Tier A counties (top quintile for ≥ 7 of 9 conditions) are southern.

**Concordance: PARTIALLY SUPPORTED.** The pattern agrees with the single-condition diabetes [1] and stroke and heart-failure [2] belts. No study of a nine-condition county composite was found, so the specific composite and tiering are new to this analysis.

## Claim 9 — Shared genes do not predict geographic co-variation

*Analysis:* the Jaccard overlap of spoke-okn disease→gene sets is unrelated to county ρ (Mantel ρ = 0.17, p = 0.25; adjusted 0.05, p = 0.41).

**Concordance: NOVEL.** No source found. This is a KG-only observation that rests on literature-derived gene sets and only nine conditions.

## References

1. Barker LE, et al. Geographic distribution of diagnosed diabetes in the U.S.: a diabetes belt. *Am J Prev Med*. 2011. PMID:21406277 · [doi:10.1016/j.amepre.2010.12.019](https://doi.org/10.1016/j.amepre.2010.12.019)
2. Mujib M, et al. Evidence of a "heart failure belt" in the southeastern United States. *Am J Cardiol*. 2011. PMID:21247536 · [doi:10.1016/j.amjcard.2010.11.012](https://doi.org/10.1016/j.amjcard.2010.11.012)
3. Croft JB, et al. Urban-Rural County and State Differences in Chronic Obstructive Pulmonary Disease - United States, 2015. *MMWR Morb Mortal Wkly Rep*. 2018. PMID:29470455 · [doi:10.15585/mmwr.mm6707a1](https://doi.org/10.15585/mmwr.mm6707a1)
4. Bullock A, et al. Prevalence of diagnosed diabetes in American Indian and Alaska Native adults, 2006-2017. *BMJ Open Diabetes Res Care*. 2020. PMID:32312721 · [doi:10.1136/bmjdrc-2020-001218](https://doi.org/10.1136/bmjdrc-2020-001218)
5. Cunningham SA, et al. County-level contextual factors associated with diabetes incidence in the United States. *Ann Epidemiol*. 2018. PMID:29233722 · [doi:10.1016/j.annepidem.2017.11.002](https://doi.org/10.1016/j.annepidem.2017.11.002)
6. Greenlund KJ, et al. PLACES: Local Data for Better Health. *Prev Chronic Dis*. 2022. PMID:35709356 · [doi:10.5888/pcd19.210459](https://doi.org/10.5888/pcd19.210459) — full-text-verified ([PMC9258452](https://pmc.ncbi.nlm.nih.gov/articles/PMC9258452/))
7. Zhang X, et al. Validation of multilevel regression and poststratification methodology for small area estimation of health indicators from the behavioral risk factor surveillance system. *Am J Epidemiol*. 2015. PMID:25957312 · [doi:10.1093/aje/kwv002](https://doi.org/10.1093/aje/kwv002)

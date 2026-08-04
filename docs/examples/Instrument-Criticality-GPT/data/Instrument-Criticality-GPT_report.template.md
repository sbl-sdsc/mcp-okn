# Instrument-Criticality

### What climate modelling would stop being able to check if observing infrastructure went dark

**Date:** 3 August 2026 · **Endpoint:** OKN federated SPARQL · **Model:** gpt-5.6-sol  
**Scope:** OKN federation snapshot plus primary-source continuity checks

## 1. Question and scope

This case study asks which observing instruments, platforms, and archives the OKN federation describes; how climate-model papers depend on them; where that dependence is concentrated; who spans the modelling and observation communities; and where the literature pays attention. It uses two graphs: `nasa-gesdisc-kg` for observation infrastructure and `climatemodelskg` for model–paper–observation evidence.

“Dependency” is not a single predicate in the federation. Here it means one of four auditable relationships: an instrument named in a model-evaluation context; an instrument named in a model paper; a platform named in a model paper and carrying the instrument; or a DOI-shared paper structurally linked through a NASA dataset and its platform to a carried instrument. Agreement across routes strengthens a claim. None of these routes proves that a model could not be evaluated without the instrument.

The ranking is therefore an **evidence-based scientific-dependence priority**, not an engineering failure-mode analysis and not a recommendation to terminate or extend a mission.

## 2. Sources used

- **OKN federation:** `nasa-gesdisc-kg` v0.0.6 and `climatemodelskg` v0.0.15, queried through the federated SPARQL endpoint.
- **Literature discovery:** Paperclip abstract and arXiv indexes. PubMed was not used because its connector scope excludes climate and remote-sensing literature.
- **Mission and continuity verification:** primary publisher records and official NASA, JAXA, NOAA, and NSIDC pages listed in References.
- **Derived artifacts:** all ranked rows, route extracts, people, places, and variable evidence are bundled under `data/`; exact SPARQL is in the reproducibility record.

## 3. Executive summary

- The NASA catalogue contains **8,058 datasets, 921 instruments, 455 platforms, and 189 archives/data centers**. Restricting the platform taxonomy to spaceborne categories leaves **288 instruments**; 232 of 455 platforms are classified as Earth Observation Satellites and account for 4,626 dataset links.
- The climate graph contains **2,000 papers**, but only 563 papers use a model source and only 110 distinct model sources appear on those links. Its observational vocabulary is much larger—2,521 observational-dataset nodes—but it does not normalize those nodes to instrument identifiers.
- **MODIS, AMSR-E, SSMIS, and SMMR** form the federation-only Tier A. MODIS leads every substantive route. Yet two of the top four are already retired: AMSR-E ended in 2015 and SMMR in 1987. This is the clearest warning that scientific dependence and live decision actionability must be kept separate.
- The most actionable Tier A finding is **SSMIS**. The federation links it to 32 models in evaluation-context papers, and NSIDC independently documents DMSP/SSMIS processing through the expected September 2026 mission retirement while directing users to evaluate AMSR2 alternatives. The published record therefore supports both high dependence and an active continuity risk.
- Dataset footprint is not an adequate proxy for criticality. Criticality score and platform-mediated dataset count are moderately correlated (Spearman 0.64), but the rank reversals are decision-relevant: SSMIS ranks third in dependence but 34th in dataset footprint; SMMR ranks fourth but 73rd; ACE-FTS ranks 12th but 225th. Conversely, four instruments sit above the catalogue’s 75th-percentile footprint with no measured modelling uptake.
- The trustworthy cross-community core is small: **155 exact author names, representing 133 ORCIDs**, occur on DOI-matched papers that are present in both graphs and connect models to NASA datasets. A broader exact-name overlap of 8,391 is only an upper-bound cohort because names are not stable person identifiers.
- Geographic coverage is a text-mention proxy, not a study-site field. China, Germany, Antarctica, India, and Canada lead model-and-instrument paper mentions. City entities contain obvious homonym errors, so the decision map uses countries and flags low-count places as thin evidence rather than presenting city precision the graph cannot support.

## 4. Evidence chain

| Route | Graph path | Meaning of “dependency” | Evidence type | Principal weakness |
|---|---|---|---|---|
| Evaluation-context instrument text | model ← paper → observational dataset; same paper mentions instrument | Instrument is named in a paper that both uses a model and evaluates observations | Textual identification plus structural context | Mention may be background; observational dataset is not normalized to the instrument |
| Direct instrument text | model ← paper → instrument mention | Model paper names the instrument | Textual | Mention is not necessarily use |
| Platform text | model ← paper → platform mention; NASA platform carries instrument | Model paper names a platform that carries the instrument | Textual and platform-mediated | A platform carries multiple instruments |
| DOI–dataset–platform | same DOI in both graphs; NASA publication → dataset → platform → instrument | Same paper uses a model and is structurally connected to a NASA dataset whose platform carries the instrument | Structural but platform-mediated | No NASA dataset→instrument edge; carried instrument may not be the dataset’s actual sensor |
| Direct model–observation–instrument | model → observational dataset, then exact dataset-name match to instrument | Intended structural route | Not usable | The field is not populated with normalized instrument IDs |

The exact DOI crosswalk is the safest bridge: 651 of 1,910 DOI-bearing climate papers also occur in the NASA publication graph. Exact case-normalized instrument names provide 115 shared labels across all platform types; the spaceborne subset contains 82 matches. Author-name joins are used only inside the same DOI-matched paper.

![Catalogue scale, platform shape, and evidence funnel](figures/fig1_catalogue_scale.png)

> **Figure 1. Catalogue scale and coverage.** Panel A uses a log scale because dataset counts dominate the infrastructure counts. Panel B shows the top platform types by linked datasets; “Models” is a NASA platform-type label and is not a climate-model count. Panel C shows the narrowing evidence funnel: 288 spaceborne instruments, 82 exact name matches to the climate graph, and only 30 with variable semantics usable for the substitution proxy. Counts describe graph contents, not an exhaustive inventory of global observing systems.

## 5. Catalogue scale and shape

The catalogue is broad but uneven. All 8,058 NASA dataset nodes link to a platform and a data center, 6,647 link to a project, and 2,581 are used by at least one publication. NASA/JPL/PODAAC is the largest archive by linked datasets (849), followed by other domain archives in the workbook. Spaceborne categories contribute 288 distinct instruments, but the same physical platform often appears under spelling or case variants such as AQUA/Aqua and TERRA/Terra.

What the catalogue does **not** cover is as important as what it does:

- There is no byte-size or file-volume field. “Data footprint” in this report means number of linked dataset records.
- There are zero direct Dataset→Instrument edges. Instrument footprint is assigned through a platform and is therefore an upper bound repeated across every instrument carried by that platform.
- Platform start and end dates are unpopulated. Operational status and remaining life cannot be computed from the federation.
- Spacecraft ownership, funded replacement, calibration overlap, channel equivalence, latency, and recovery time are absent.
- The climate graph is a 2,000-paper corpus, not the full climate literature. Zero measured uptake means “not found in the measured routes,” not “not scientifically used.”

## 6. Comparison with prior work

The checked literature already establishes the scientific importance of MODIS, the AMSR series, and the SMMR→SSM/I→SSMIS passive-microwave record. It also shows why a graph-only rank needs a status layer: AMSR-E and SMMR are retired, while MODIS and SSMIS have current transition plans. What prior work does not provide is a common cross-instrument loss scale independent of dataset footprint; the federation’s contribution is a transparent comparison and an evidence-gap audit, not a causal denial experiment.

## 7. Model dependence through multiple routes

![Route-specific model support](figures/fig2_dependency_routes.png)

> **Figure 2. Independent dependency routes.** Bars count distinct model-source nodes, not model runs or institutions. The four routes overlap and must not be summed. Instrument text is strongest when the same paper also has an observational-dataset edge; DOI–dataset–platform is structurally stronger but sensor attribution is indirect. Route agreement supports priority; disagreement diagnoses extraction or graph-structure uncertainty.

MODIS is linked to 50 models in evaluation-context papers, 52 through direct instrument text, 31 through DOI–dataset–platform, and 55 through platform text. SSMIS has 32, 33, 22, and 34 respectively. SMMR has high text/evaluation support but no platform-text support, consistent with a historical instrument being discussed as part of a long record rather than a current platform. AMSR-E gains substantial support through the platform and DOI routes, but the external record shows that its actionable continuity question belongs to the AMSR series, not to restarting a retired sensor.

A direct structural chain from Model→ObservationalDataset→Instrument could not be computed: exact matching returned only a “NOT APPLICABLE” label rather than real instruments. That failed route is retained as a named limitation instead of being silently converted into a zero.

## 8. Three risk distributions

![Criticality versus dataset footprint](figures/fig3_risk_distribution.png)

> **Figure 3. Scientific-dependence priority versus platform-mediated dataset footprint.** Each point is a named spaceborne instrument. The x-axis is an upper-bound dataset count inherited from carried platforms, shown on a log scale. The y-axis is the visible composite score defined in §11. Grey points have no uptake in the measured routes. The moderate positive association (Spearman 0.64) does not remove the rank reversals that motivate this case study.

The three risks do not collapse into one order:

1. **Many-model dependence.** MODIS, SSMIS, SMMR, and AMSU-A each connect to more than 20 models in evaluation-context papers. This is concentration risk: many modelling claims draw on the same observational family.
2. **Low uptake with a scarce measured variable.** GOME-2 is the only named spaceborne instrument with five or fewer evaluation-linked models and a variable that no other exact-matched space instrument measures in the climate graph. This is a candidate for non-substitutability, not a conclusion: only 30 of 82 exact-matched instruments have any `MEASURES_VARIABLE` edges.
3. **Large record footprint with no measured uptake.** AQUARIUS_SCATTEROMETER and AQUARIUS_RADIOMETER each inherit 173 platform-linked dataset records with no measured modelling uptake; GPS RECEIVERS and GPS P each inherit 91. This may indicate unused observational capacity, corpus omission, or the platform-assignment artifact. It is not evidence of low scientific value.

## 9. People spanning modelling and observation

![Cross-community people and geographic attention](figures/fig4_people_places.png)

> **Figure 4. Human and geographic infrastructure.** Panel A shows people found by exact author name within the same DOI-matched paper that links a model in the climate graph to a NASA dataset. Panel B shows the countries most often mentioned in papers that use a model and mention an instrument. These are literature attention signals, not institutional affiliation or study-site measurements.

The exact-paper method identifies 155 names and 133 ORCIDs. Chris Derksen and Lawrence Mudryk each appear on three shared papers; the high-model cohort also includes researchers working on coordinated model intercomparison and observation-rich evaluation. This core is much smaller than the 10,029 distinct author-name strings in the climate graph.

The exact-name overlap between the two graphs is 8,391 strings, and 6,983 of those reach at least one ORCID in NASA data. It is not used as a people count: 787 of the ORCID-reachable names map ambiguously and exact names can merge different people. The conservative 155-name, 133-ORCID result is the actionable community finding.

## 10. Where the literature pays attention

The map below uses country entities because city entities contain visible homonym and geocoding errors. Marker size follows papers that both use a model and mention an instrument. Click a marker for total papers, model papers, instrument–model papers, and distinct model sources.

<!-- INTERACTIVE_MAP -->

This is a **research-attention map**, not a site map. Country mentions may refer to authors, comparisons, regions, or background. Thin evidence is defined here as fewer than three model-and-instrument papers; such places should not be treated as absent impacts, only as lightly represented in this corpus. The city-level extract is supplied in `data/city_attention_flagged.json` for audit, not decision use.

## 11. Ranked results: observing infrastructure

The federation-only score is:

`100 × [0.45·log1p(E)/max + 0.15·log1p(max(T−E,0))/max + 0.25·log1p(D)/max + 0.10·log1p(P)/max + 0.05·I(U>0)]`

where **E** is evaluation-context model count, **T** direct instrument-text model count, **D** DOI–dataset–platform model count, **P** platform-text model count, and **U** unique-variable count. Each log component is scaled by the maximum observed on that axis. Dataset footprint is deliberately excluded. Tier A is ≥70, Tier B is 40–69.9, and Tier C is below 40. Generic labels are not rankable.

| Rank | Instrument | Score | Tier | Eval models | DOI models | Platform-text models | Dataset footprint | Decision actionability |
|---:|---|---:|:---:|---:|---:|---:|---:|---|
| 1 | MODIS | 88.2 | A | 50 | 31 | 55 | 1,414 | Live through planned Terra/Aqua data stops in 2027; VIIRS is partial, not complete, continuity |
| 2 | AMSR-E | 74.1 | A | 10 | 31 | 52 | 1,305 | Retired in 2015; interpret as AMSR-series record dependence |
| 3 | SSMIS | 72.6 | A | 32 | 22 | 34 | 170 | Live continuity issue through expected DMSP retirement in September 2026 |
| 4 | SMMR | 71.4 | A | 32 | 20 | 0 | 74 | Retired in 1987; historical anchor, not a current retirement choice |
| 5 | AMSU-A | 67.0 | B | 28 | 19 | 49 | 848 | Family-level dependence; platform status not in federation |
| 6 | MISR | 66.6 | B | 14 | 31 | 51 | 864 | Current-status enrichment required |
| 7 | AVHRR | 66.1 | B | 32 | 15 | 32 | Long multi-platform series; instrument-family interpretation |
| 8 | TOVS | 46.4 | B | 27 | 0 | 29 | Historical series; not a live decision target |
| 9 | AIRS | 41.1 | B | 2 | 19 | 49 | Structural routes dominate textual evaluation evidence |
| 10 | VIIRS | 40.5 | B | 1 | 19 | 49 | Large footprint and designated MODIS successor, but climate-KG evaluation uptake is sparse |
| 12 | ACE-FTS | 38.1 | C | 27 | 0 | 0 | 10 | Strong asymmetry: high model dependence, small footprint |

<!-- RESULTS_TABLE -->

The interactive HTML and workbook contain all 277 named, rankable spaceborne instruments, with route counts, criteria, tier, footprint, platforms, and variable evidence.

## 12. The asymmetry and what the literature adds

The user’s asymmetry hypothesis is supported **locally, not universally**. Dataset footprint and score rise together overall, but several instruments are much more critical than their record count suggests. SSMIS, SMMR, and ACE-FTS are the clearest examples. Conversely, VIIRS and CERES Scanner have among the largest platform-mediated footprints but substantially lower measured evaluation dependence.

The published record separates established criticality from federation novelty:

- **MODIS — established criticality, partial continuity.** The federation’s top rank agrees with published use of MODIS-derived cloud classes for climate-model evaluation and with NASA’s transition planning. NASA states that VIIRS lacks several MODIS spectral bands and that some continuity products require other sounders; “VIIRS replaces MODIS” is therefore too strong.
- **AMSR-E — established series value, low live actionability.** JAXA documents that AMSR-E ended in 2015 after cross-calibration with AMSR2. AMSR3 began observations in 2025 as the next series member. The federation correctly detects scientific dependence but cannot represent engineered succession.
- **SSMIS — established and actionable.** NSIDC’s 2026 climate-data-record documentation states that aging DMSP satellites have no planned follow-on SSMIS and that AMSR2 was added as the new input after intercalibration. The federation’s high rank and the continuity record agree.
- **SMMR — established historical dependence, not an unknown live risk.** The SMMR→SSM/I→SSMIS→AMSR2 sea-ice record is well documented. A high rank is scientifically meaningful but operationally stale.
- **Cross-instrument quantitative ordering — federation-led, unresolved in the literature.** The literature evaluates individual continuity chains and calls for mature climate observing-system simulation experiments; it does not supply a common loss metric across MODIS, SSMIS, ACE-FTS, and other instruments. The score is a transparent triage device, not external validation of a universal order.
- **GOME-2 non-substitutability — novel but fragile.** The unique-variable signal is specific to the sparsely populated climate graph. It is a prompt for expert review, not evidence that no physical substitute exists.

## 13. Limitations and decision rules

- **No operational-status field:** retired and active instruments can rank together. Always enrich top results with mission status before a review.
- **No instrument-level data volume:** dataset counts are platform-mediated upper bounds, not bytes, granules, temporal coverage, or independent products.
- **No direct dataset→instrument edge:** DOI-based sensor attribution can be wrong when a platform carries several instruments.
- **Text extraction is evidence, not proof:** mentions can be background, methods, comparison, or future work.
- **Model source semantics:** `Source`, not `Model`, carries the model links; the nominal Model class has zero instances.
- **Sparse substitution semantics:** only 30 of 82 name-matched space instruments have variable edges. Fifty-two comparisons are unsupported.
- **Temporal staleness:** SMMR and AMSR-E demonstrate why an operational-status join is mandatory for decisions.
- **People identity:** exact names are safe only within an exact DOI context; ORCID ambiguity remains.
- **Geographic semantics:** country and city nodes are text mentions, not study sites; city homonyms are visibly unreliable.
- **Corpus scope:** the climate graph contains 2,000 papers. Absence from it is not absence from climate science.
- **No causal loss estimate:** the federation cannot compute forecast degradation, bias growth, time to replacement, calibration drift, or irrecoverable record discontinuity.
- **No observation-system experiment:** a real retirement decision needs OSSE/denial experiments and expert assessment of channels, overlap, calibration, and downstream products.

Decision rule: use Tier A/B as an **evidence-review queue**. Before acting, require current mission status, replacement readiness, channel-level equivalence, calibration overlap, product lineage, and an observing-system denial or sensitivity analysis.

## 14. Reproducibility

The complete rerun specification is in `Instrument-Criticality-GPT_reproducibility.md`. It contains the originating prompt, KG versions, join rules, thresholds, scoring formula, limitations, 18 verbatim SPARQL queries, and a faithful Mermaid diagram for every query. The workbook’s **Methods & Rules** sheet repeats the decision-facing scoring rules, and `scripts/` contains the exact figure, HTML, map, and workbook builders.

## 15. References

1. Fridlind AM, et al. *Toward a Climate Observing System Simulation Experiment Framework for Satellite Mission Design.* Bulletin of the American Meteorological Society. 2026. [doi:10.1175/BAMS-D-24-0242.1](https://doi.org/10.1175/BAMS-D-24-0242.1). Abstract discovered via Paperclip; publisher record checked.
2. Kaps A, et al. *Machine-learned cloud classes from satellite data for process-oriented climate model evaluation.* IEEE Transactions on Geoscience and Remote Sensing. 2023. [doi:10.1109/TGRS.2023.3237008](https://doi.org/10.1109/TGRS.2023.3237008). Abstract discovered via Paperclip.
3. Román MO, et al. *Continuity between NASA MODIS Collection 6.1 and VIIRS Collection 2 land products.* Remote Sensing of Environment. 2024. [doi:10.1016/j.rse.2023.113963](https://doi.org/10.1016/j.rse.2023.113963). Abstract discovered via Paperclip.
4. NASA LAADS DAAC. *MODIS to VIIRS Transition.* Current operational guidance, accessed 3 August 2026. [Full text](https://ladsweb.modaps.eosdis.nasa.gov/learn/modis-to-viirs-transition).
5. JAXA. *Operation of AMSR-E onboard Aqua completed.* 2015. [Full text](https://global.jaxa.jp/press/2015/12/20151207_amsr-e.html).
6. JAXA. *Early observation results of AMSR3 onboard GOSAT-GW.* 2025. [Full text](https://global.jaxa.jp/press/2025/09/20250905-1_e.html).
7. Cavalieri DJ, Parkinson CL, DiGirolamo N, Ivanoff A. *Intersensor Calibration Between F13 SSMI and F17 SSMIS for Global Sea Ice Data Records.* IEEE Geoscience and Remote Sensing Letters. 2012. [doi:10.1109/LGRS.2011.2166754](https://doi.org/10.1109/LGRS.2011.2166754). Abstract discovered via Paperclip.
8. Meier WN, et al. *NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6: changes and intercalibration.* NSIDC. 2026. [Full text](https://nsidc.org/sites/default/files/documents/other/nsidc-special-report-29.pdf).
9. NSIDC DAAC. *SSMIS processing will now continue through September 2026.* 2025 update. [Full text](https://nsidc.org/data/user-resources/data-announcements/user-notice-ssmis-processing-will-now-continue-through-september-2026).

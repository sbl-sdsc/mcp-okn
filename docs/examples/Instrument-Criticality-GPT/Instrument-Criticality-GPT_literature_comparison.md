# Instrument-Criticality — literature comparison

**Comparison date:** 3 August 2026  
**Federation basis:** `nasa-gesdisc-kg` v0.0.6 and `climatemodelskg` v0.0.15  
**Search route:** Paperclip abstract/arXiv discovery followed by primary publisher, NASA, JAXA, NOAA, and NSIDC records. PubMed was not used because its connector scope explicitly excludes climate and remote-sensing literature.

## Concordance rules

- **SUPPORTED** — the published record independently supports the federation claim.
- **PARTIALLY SUPPORTED** — the direction is supported, but the instrument, time, or substitution interpretation needs qualification.
- **NOVEL** — the federation supplies a comparative claim not found in the checked literature.
- **UNRESOLVED** — available fields or literature do not support a defensible comparison.
- **CONTRADICTED** — the checked record directly conflicts with the claim.

## Claim-by-claim comparison

| Federation claim | Concordance | Published record | Decision interpretation |
|---|---|---|---|
| MODIS is the highest-dependence instrument (score 88.2; 50 evaluation-linked models) | **SUPPORTED** | MODIS observations are used explicitly for process-oriented climate-model evaluation; NASA maintains a dedicated MODIS→VIIRS transition plan. | High scientific dependence is established. Its loss is only partly survivable because VIIRS lacks several MODIS bands and some products require co-located sounders. |
| MODIS footprint makes it important | **PARTIALLY SUPPORTED** | NASA documents a very broad MODIS product suite and successor products. | The federation’s 1,414-dataset count is platform-mediated and cannot be interpreted as instrument bytes or independent products. |
| AMSR-E is the second-highest live retirement risk | **CONTRADICTED** | JAXA ended AMSR-E operation on 4 December 2015 after cross-calibration with AMSR2. AMSR3 began observations in 2025 as the next continuity member. | The federation detects dependence on the AMSR record, but the instrument is not a live retirement choice. Reframe the action around AMSR-series calibration and product continuity. |
| SSMIS is a high and current continuity risk (rank 3) | **SUPPORTED** | NSIDC documents SSMIS processing through expected DMSP retirement in September 2026, warns of possible gaps/failures, and directs users to evaluate AMSR2 alternatives. Its 2026 CDR report states that aging DMSP satellites have no planned follow-on SSMIS and adds intercalibrated AMSR2 input. | This is the strongest actionable federation result: multiple KG routes and operational continuity records agree. |
| SMMR is a top live risk (rank 4) | **CONTRADICTED** | SMMR stopped in August 1987. It remains the opening segment of the continuous passive-microwave sea-ice record. | High score means historical record dependence, not a current spacecraft decision. It diagnoses the missing status field. |
| SMMR→SSM/I→SSMIS continuity is scientifically critical | **SUPPORTED** | Published intersensor calibration and NSIDC CDR documentation explicitly construct the long sea-ice record across these sensors. | The critical unit is the calibrated series and downstream products, not any single retired sensor. |
| AMSR-E/AMSR2/AMSR3 form an engineered continuity chain | **SUPPORTED** | JAXA documents AMSR-E/AMSR2 overlap and AMSR3 succession; AMSR3 began observations in August 2025. | The federation rank should be reviewed at instrument-family and product-lineage level. |
| VIIRS is a complete substitute for MODIS | **CONTRADICTED** | NASA states that VIIRS lacks key CO₂ and water-vapor IR absorption bands and that some MODIS algorithms cannot be directly ported. | Continuity is product-specific. A single binary substitute flag would be misleading. |
| SSMIS, SMMR, and ACE-FTS are more critical than their dataset footprint suggests | **NOVEL** | Checked sources discuss individual records and transitions, not a cross-instrument rank that is independent of data volume. | This is the federation’s main comparative contribution, but instrument-level data volume is absent and the footprint denominator is weak. |
| GOME-2 is a low-uptake, low-substitutability concern | **UNRESOLVED** | No comparable channel-level substitution analysis was found in the checked literature, and the graph has variable semantics for only 30 exact-matched space instruments. | Treat as an expert-review lead, not a continuity conclusion. |
| A universal cross-instrument “loss” rank is externally validated | **UNRESOLVED** | Climate OSSE literature argues for a mature framework to quantify observation value for mission design; it does not provide a common validated scale covering this catalogue. | The score is a transparent evidence-review queue, not a causal loss estimate. |

## Top-ranked instruments: status and continuity check

| Rank | Instrument | Federation signal | Current record checked | Actionability |
|---:|---|---|---|---|
| 1 | MODIS | Four-route agreement; 88.2 | Terra data collection planned to stop February 2027; Aqua September 2027; VIIRS continuity is incomplete for some bands/products | **Immediate review** |
| 2 | AMSR-E | Strong DOI/platform evidence; 74.1 | Retired 2015; AMSR2 and AMSR3 successors operating/commissioned | **Series-level review, not mission extension** |
| 3 | SSMIS | Four-route agreement; 72.6 | DMSP retirement expected September 2026; AMSR2 transition underway | **Immediate review** |
| 4 | SMMR | High evaluation/text support; 71.4 | Retired 1987; historical CDR anchor | **Archive/calibration preservation** |
| 5 | AMSU-A | Broad route agreement; 67.0 | Status is platform-specific and not resolved in this comparison | **Status enrichment required** |
| 6 | MISR | DOI/platform-heavy support; 66.6 | Not checked deeply enough for current mission decision | **UNRESOLVED** |
| 7 | AVHRR | Broad series support; 66.1 | Multi-platform instrument family | **Family-level review** |
| 8 | TOVS | Text/evaluation-heavy; 46.4 | Historical sounding system | **Archive/calibration preservation** |
| 9 | AIRS | Structural routes dominate; 41.1 | Current-status and channel-substitute analysis not completed | **UNRESOLVED** |
| 10 | VIIRS | Large footprint, sparse evaluation-context uptake; 40.5 | Designated MODIS continuity instrument with known spectral differences | **Continuity enabler and evidence gap** |

## What the federation adds

The federation’s strongest new signal is not that MODIS, SSMIS, or the passive-microwave record matter; the literature already knows that. It adds a reproducible, cross-instrument comparison showing where dependence evidence and record footprint diverge, and it exposes which continuity questions are represented structurally, textually, or not at all.

That novelty remains bounded. Because operational status, channel equivalence, data bytes, direct dataset–instrument identity, and denial-experiment outcomes are absent, the federation can prioritize reviews but cannot answer the final survivability question alone.

## Sources

1. Fridlind AM, et al. *Toward a Climate Observing System Simulation Experiment Framework for Satellite Mission Design.* BAMS. 2026. [doi:10.1175/BAMS-D-24-0242.1](https://doi.org/10.1175/BAMS-D-24-0242.1).
2. Kaps A, et al. *Machine-learned cloud classes from satellite data for process-oriented climate model evaluation.* IEEE TGRS. 2023. [doi:10.1109/TGRS.2023.3237008](https://doi.org/10.1109/TGRS.2023.3237008).
3. Román MO, et al. *Continuity between NASA MODIS Collection 6.1 and VIIRS Collection 2 land products.* Remote Sensing of Environment. 2024. [doi:10.1016/j.rse.2023.113963](https://doi.org/10.1016/j.rse.2023.113963).
4. NASA LAADS DAAC. *MODIS to VIIRS Transition.* [Full text](https://ladsweb.modaps.eosdis.nasa.gov/learn/modis-to-viirs-transition).
5. JAXA. *Operation of AMSR-E onboard Aqua completed.* [Full text](https://global.jaxa.jp/press/2015/12/20151207_amsr-e.html).
6. JAXA. *Early observation results of AMSR3 onboard GOSAT-GW.* [Full text](https://global.jaxa.jp/press/2025/09/20250905-1_e.html).
7. Cavalieri DJ, et al. *Intersensor Calibration Between F13 SSMI and F17 SSMIS for Global Sea Ice Data Records.* IEEE GRSL. 2012. [doi:10.1109/LGRS.2011.2166754](https://doi.org/10.1109/LGRS.2011.2166754).
8. Meier WN, et al. *NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6.* NSIDC. 2026. [Full text](https://nsidc.org/sites/default/files/documents/other/nsidc-special-report-29.pdf).
9. NSIDC DAAC. *SSMIS processing will now continue through September 2026.* [Full text](https://nsidc.org/data/user-resources/data-announcements/user-notice-ssmis-processing-will-now-continue-through-september-2026).


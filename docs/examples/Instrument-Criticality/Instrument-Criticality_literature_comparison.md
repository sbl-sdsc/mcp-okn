# Instrument-Criticality — literature comparison (per-claim record)

Companion to `Instrument-Criticality_report.md` §8. One entry per checked claim, its
**Concordance** (one of SUPPORTED / PARTIALLY SUPPORTED / CONTRADICTED / MIXED / NOVEL /
UNRESOLVED), the evidence, and citations resolving to the `## References` list at the foot of this
document.

**Retrieval.** Claims were checked by web search against the primary Earth-observation and climate
literature — agency documentation (NASA Earthdata, NSIDC, NOAA NESDIS, GCOS/WMO, ESA CCI), peer-
reviewed journals (*BAMS*, *Geoscientific Model Development*, *Remote Sensing of Environment*,
*Atmospheric Measurement Techniques*), and the National Academies Decadal Survey. The **PubMed**
connector was *not* used as an evidence source: PubMed indexes only biomedical and life-sciences
literature and returns essentially no coverage of satellite Earth observation, climate-model
evaluation, or mission continuity. Recording that as a tool limitation rather than a null result is
the honest framing — the relevant corpus is simply not in that index. The **Paperclip** connector
was likewise not used, for the same domain-coverage reason. No claim below rests on a full-text read;
all are abstract-, documentation-, or landing-page-level checks, and that is stated rather than
disguised.

---

## Claim 1 — MODIS is the single most depended-upon instrument for climate modelling

**As stated:** MODIS ranks first on the composite criticality score (100/100), is the only instrument
with 5/5 corroborating routes at that magnitude, accounts for 29.5% of all
instrument mentions in the climate-modelling corpus, and is, under the strict GCMD-label join, the sole measurer of 4 model-produced
variables (`albsn`, `nppLut`, `tsSprd`, `vegFrac`) and of 7 once its spelled-out aliases are
resolved.

**Concordance: SUPPORTED.** MODIS is treated across the literature as the anchor of the modern
land/atmosphere satellite climate record, and its impending end-of-life is explicitly framed as a
continuity problem to be solved rather than a routine retirement. NASA's transition documentation
states that "the record must continue onto VIIRS beyond the end of the MODIS mission to meet
requirements as a Global Climate Observing System (GCOS) climate data record", and NASA has invested
in dedicated SNPP/JPSS continuity products for exactly this reason [1]. Cross-calibration work on
SNPP and NOAA-20 VIIRS is framed as being "for continuity of the MODIS climate data records" [2],
and land-product continuity between MODIS Collection 6.1 and VIIRS Collection 2 has been assessed as
its own research problem [3]. Science data collection from Terra and Aqua MODIS is planned to stop in
February 2027 and September 2027 respectively, with both platforms already drifting from their design
orbits [1] — so the criticality this analysis measures is attached to an instrument with a dated
end.

**Caveat.** The literature supports *importance*; it does not independently rank MODIS first among
all instruments, and no published ranking exists to compare against. The 29.5% mention share is also
partly an artefact of MODIS's alias-rich naming in an NLP-extracted vocabulary (see report §10,
limitation 4).

---

## Claim 2 — The passive-microwave sea-ice chain (SMMR → SSM/I → SSMIS, with AMSR-E/AMSR2) is
## critical, near-irreplaceable, and facing an active continuity transition

**As stated:** AMSR-E ranks 2nd, SSMIS 8th, SMMR 20th, all on far smaller archives
than the imagers above them; SSMIS carries a +26 criticality-vs-volume rank gap and SMMR +46 on 170
and 74 attributed datasets respectively. None of the three is a *sole* measurer of a sea-ice variable
in this corpus — `sic` and `siextentn` are each measured by several instrument names, which is itself
consistent with the overlapping-sensor design of the record.

**Concordance: SUPPORTED.** This is the strongest independent confirmation in the comparison, and it
is specific. NSIDC states that with the planned retirement of SSMIS in 2026, AMSR2 is being brought in
to maintain coverage, and that "for the first time in nearly 40 years there is a switch to a
distinctly different sensor" — a transition NSIDC itself describes as challenging [4, 5]. The
NOAA/NSIDC Climate Data Record documentation records AMSR2 becoming the input brightness-temperature
source from 1 January 2025 [6], and the risk to the record has been covered as a general-interest
science story [7]. The SMMR–SSM/I–SSMIS series is explicitly identified as the backbone most sea-ice
concentration climate records still employ [5]. The federation's ranking of a 1978-era instrument
(SMMR, 74 datasets) at 20th of 243 — 46 places above its volume rank — is therefore not an artefact;
it reflects a real, currently-live continuity concern.

---

## Claim 3 — CERES / Earth radiation budget is a top-tier record with an identified continuity gap,
## and this analysis under-detects it on the literature route

**As stated:** The CERES family occupies ranks 13, 15, 16 and below. CERES SCANNER carries the
largest raw data footprint in the entire spaceborne catalogue (2,070 attributed datasets) yet reaches
only 3/5 corroborating routes, with **zero** climate-modelling papers naming it in `climatemodelskg`
(R1 = 0) despite 210 NASA-side modelling-title publications citing its data (R4 = 210) — and **zero**
on the irreplaceability axis, even though alias resolution makes "CERES" the joint-largest holder of
sole-measured model-relevant variables in the corpus (7).

**Concordance: PARTIALLY SUPPORTED.** The importance and the continuity gap are strongly confirmed;
the specific route-level pattern is a graph-quality finding, not a scientific one. Earth's radiation
budget is designated an essential climate variable whose continuous observation is described as
critical, and CERES has held the longest continuous ERB record since 2000 [8, 9]. Its successor,
Libera, is slated for launch on JPSS-3 in December 2027, at which point "the probability of a CERES
data gap will be approaching 50%", and continuity beyond Libera is explicitly unresolved [9, 10].
So the literature treats CERES as at least as critical as the federation's own top-ranked
instruments — arguably more so, given the quantified gap probability. The R1 = 0 result is best read
as a **defect in the NLP extraction**: papers overwhelmingly refer to the product or mission ("CERES",
"CERES-EBAF") rather than to the GCMD flight-model labels (`CERES-FM1`…`CERES SCANNER`) that
`nasa-gesdisc-kg` uses, so the label join misses them. Consistent with this, "CERES" does appear as
an `ObservationalDataset` name used by models in `climatemodelskg`, and as an instrument name that is the sole measurer of
7 model-relevant variables — but under a string that matches no GCMD instrument label.

---

## Claim 4 — Stratospheric limb sounding (MLS, ACE-FTS, HIRDLS, TES, SAGE) is a
## higher-criticality-than-volume cluster facing an imminent record break

**As stated:** ACE-FTS shows the third-largest positive rank gap in the study (criticality rank 82 vs
footprint rank 202, gap +120) on only 10 attributed datasets, outranking 120 higher-volume
instruments. The rest of the limb-sounding group is *not* volume-divergent — MLS (+5), TES (+6) and
HIRDLS (−11) sit close to their volume ranks, all reaching 5/5, 5/5 and 4/5 routes respectively in
risk class A. The claim is therefore about **ACE-FTS specifically plus the group's shared platform
risk**, not about a uniform criticality-vs-volume asymmetry across the cluster.

**Concordance: SUPPORTED.** A 2025 *BAMS* article titled "The Imminent Data Desert: The Future of
Stratospheric Monitoring in a Rapidly Changing World" makes precisely this case: Aura (carrying MLS,
TES, HIRDLS, OMI) is near the end of its operational life and SCISAT-1 (ACE-FTS) is over twenty years
old, and their decommissioning "will cause a substantial gap in the measurement of critical
atmospheric components, including water vapor, inorganic chlorine species, and tracers of
stratospheric transport" [11, 12]. MLS provides the best geographic coverage of the group and its
loss is described as producing a "data desert" for satellite stratospheric water vapour, because
ACE-FTS and SAGE III/ISS sample only a few dozen geolocations per day [11]. Mitigations under
development — a Continuity-MLS instrument [13] and neural-network continuation of the MLS water-vapour
record with OMPS-LP [14] — exist precisely because the gap is recognised. That a 10-dataset
instrument outranks 120 higher-volume instruments in this analysis is therefore concordant with the
published view, and is a clean example of the volume/criticality asymmetry.

---

## Claim 5 — Climate-model evaluation in this corpus leans on reanalyses and gridded station
## products more than on satellite instrument products, so instrument dependency is largely indirect

**As stated:** Of the 163 observational datasets that `climatemodelskg` records climate models as
being evaluated against, the highest-usage entries are ERA5 (50 models), CRU (42), GPCC (31), UoD
(31), ERA5/ERA5.1 (26) and CHIRPS (22); satellite-instrument-attributable entries (CERES, CloudSat,
GPCP, MODIS DOD, AERONET, CLARA-A3, GIMMS LAI3g, HadISST/NSIDC, TRMM PR2A25) are a minority.

**Concordance: PARTIALLY SUPPORTED.** The pattern is real and recognised, but the framing needs care.
Community evaluation frameworks do lean heavily on reanalysis: ESMValTool's documented reference sets
pair satellite products with ERA5, ERA-20C/ERA-Interim, MERRA2, BEST and ERSSTv5, and the tool
explicitly offers evaluation against a *multi-observational mean* spanning ERA5, GPCP, MERRA2,
ESACCI-WATERVAPOUR and ISCCP-FH [15, 16]. The obs4MIPs project exists precisely to raise the profile
of satellite data in CMIP evaluation, and its holdings are "primarily from satellite data"; its own
documentation notes that reanalysis "for some variables … is the best observationally based reference
for climate models" while cautioning that reanalysis inclusion in obs4MIPs should be approached
carefully [17, 18]. So the literature confirms that reanalyses are a dominant reference class, but
also that this is a known tension being actively managed rather than an unnoticed one. The stronger
and more defensible version of the finding is structural: because reanalyses assimilate satellite
radiances, an instrument can be load-bearing for a model evaluation *without appearing anywhere in
that evaluation's dataset list* — which is a mechanism this analysis can name but cannot measure.

---

## Claim 6 — Newly launched instruments carry substantial data footprints with no detectable
## modelling uptake, and this is a latency artefact rather than a redundancy signal

**As stated:** Risk class C — large footprint, zero signal on all five dependency routes — contains
9 instruments. Eight have their most recent dataset start in 2021–2025: HARP2, OCI and SPEXone
(PACE, 2024), DDMI (2024), TIRS-PREFIRE (2024), TEMPO (2025) and TMS/TMWS (2023). The ninth, SIRS,
is a 1960s Nimbus instrument.

**Concordance: SUPPORTED.** PACE launched 8 February 2024 carrying OCI, HARP2 and SPEXone, with
public data release beginning 11 April 2024, and reprocessing to OCI V3 / SPEXone and HARP2 V4 has
continued into 2025 with new data lagging roughly a month for calibration refinement [19, 20, 21].
Given that `climatemodelskg` covers 2,000 papers and NASA-side publication linkage depends on citation
crawling, instruments whose calibrated products only stabilised in 2024–25 cannot yet show modelling
uptake. Two members are not latency cases: SIRS, whose record is 1960s-era, and DDMI (CYGNSS), whose
data begin in 2017 and whose datasets already carry 120 publications overall — a genuine uptake gap.

The correct reading of class C is therefore "not yet evaluated" for seven of the nine, and the
operational consequence is that class C membership must be interpreted jointly with **first**-light
date rather than latest dataset start — an instrument that is old *and* in class C (SIRS 1964, DDMI
2017) is a genuinely different case from one that is new and in class C.

---

## Claim 7 — GRACE / GRACE-FO gravimetry scores low in this analysis despite a recognised,
## consequential mission gap

**As stated:** KBR ranks 143, GRACE INTERFEROMETER 146 and GRACE-FO KBR 148 of 243, all with
criticality ≈ 7.4 and only 1/5 corroborating routes; the rest of the payload runs to 223.

**Concordance: CONTRADICTED.** The literature treats the GRACE→GRACE-FO transition as a textbook
continuity failure with quantified consequences: an eleven-month gap from July 2017 to May 2018 that
"disrupts the measurement continuity and limits further applications", severe enough that a distinct
methodological sub-literature exists purely to reconstruct it — hydrological-model bridging [22],
deep-learning and Bayesian CNN reconstruction [23, 24], two-step linear models [25], and singular
spectrum analysis [26]. Multi-decadal terrestrial water storage series are described as required for
climate model evaluation and change attribution [25, 27]. A criticality score in the bottom 40% is
therefore wrong, and the reason is diagnosable: `nasa-gesdisc-kg` splits the GRACE science payload
across several engineering-sounding labels (KBR, ACC, LRI, MWI, SCA, LRR) none of which the
climate-modelling corpus names, and GES DISC is not the primary archive for GRACE mass-change
products. This is a **coverage-and-labelling failure of the federation**, and the clearest single
demonstration in this study that a low criticality score is not evidence of low criticality.

---

## Claim 8 — PALSAR, WINDSAT, ACE-FTS, GLAS and SRTM are "under-recognised": far more critical than
## their data volume implies

**As stated:** PALSAR, WINDSAT, ACE-FTS, GLAS and SRTM show the largest positive
footprint-rank-minus-criticality-rank gaps (+133, +127, +120, +107, +100) at 10–24 attributed
datasets each. Two further instruments sit in the same band — GFO Altimeter (+97) and GOME (+94) —
and are covered by the same claim.

**Concordance: UNRESOLVED.** No published source was found that ranks these instruments against
others on modelling dependence, because — as far as this search could establish — no such published
ranking exists for any instrument. The individual instruments are well documented and several have
recognised continuity stories (GLAS/ICESat → ICESat-2/ATLAS; GOME → GOME-2 → TROPOMI/Sentinel-5P),
but the *relative* claim this analysis makes has no comparator in the literature. It is offered as a
prediction to be tested against expert judgement, not as a confirmed result. The honest statement is
that the rank gap is a property of this federation's evidence, and its scientific validity is
untested.

---

## Claim 9 — Substitutability cannot be resolved at GCMD keyword granularity (only 122 of 1,609
## science keywords tag any dataset; only 5 keywords have ≤5 spaceborne instruments), and 58 of the
## 90 sole-measured model-relevant variables are measured by in-situ instruments, not satellites

**Concordance: NOVEL.** This is a knowledge-graph data-quality observation with no literature
counterpart. It is, however, directly relevant to the community's own gap-analysis machinery: the
CEOS/CGMS ECV Inventory is maintained and published annually precisely "to support Gap Analysis
exercises" [28], GCOS specifies 55 ECVs of which roughly 60% are addressable by satellite [29, 30],
and a 2025 *BAMS* paper responds to GCOS's request for transparent, quantitative information on ECV
product quality and application suitability [31]. Those are the vocabularies at which substitutability
*could* be assessed. `nasa-gesdisc-kg` carries no ECV field, no data-volume field, no launch or
decommission date and no successor-instrument relation, so the substitutability question that the
ECV Inventory is designed to answer cannot be reconstructed from this graph. Naming that gap is
arguably the most actionable output of this study.

---

## Claim 10 — Textual and structural dependency evidence agree only moderately, so a single route
## would misrank the catalogue

**As stated:** Route agreement clusters into a textual family (R1–R2, Spearman ρ = 0.79) and a
structural family (R3–R4, ρ = 0.74), with cross-family agreement of only ρ = 0.32–0.55.

**Concordance: NOVEL.** No prior work was found that measures agreement between bibliometric routes
to instrument dependence, because the multi-route construction itself appears to be new. The general
principle it rests on — that observations must be of known quality with continuity and calibration
essential, and that a gap analysis is needed to identify which observations may be lost to funding
lapses, instrument retirements or mission shutdowns [32, 33] — is well established, but the operational
question of *how you would know* which instruments those are, from evidence rather than expert
judgement, is what this study attempts. The route-disagreement result is the methodological finding
that follows: no single evidence route reproduces the ranking, so agreement across routes, not the
magnitude of any one route, is what should carry weight.

---

## Where the KG evidence diverges from the literature

Three divergences are **errors in the graphs**, not differences of scope:

- **Claim 3 (CERES).** The GCMD flight-model labels (`CERES-FM1`…`CERES-PFM`, `CERES SCANNER`) do not
  match how the literature names the instrument, so the NLP-extracted mention route returns zero for
  the single largest-footprint instrument in the catalogue. Any name-join analysis over this graph
  will inherit that miss.
- **Claim 7 (GRACE).** Payload fragmentation across engineering labels plus GES DISC's partial
  archival coverage of gravimetry places a demonstrably critical mission in the bottom 40%.
- **Claim 9 (keywords).** 92.4% of the ScienceKeyword vocabulary is unattached to any dataset,
  collapsing measurement-capability granularity to a level at which substitutability is
  undetectable.

Two are **differences of scope** rather than error: Claim 5 (reanalysis dominance reflects genuine
community practice, and the indirect satellite→reanalysis dependency is real but unmeasurable here),
and Claim 6 (class C membership measures publication latency, which is a property of the corpus's
time window, not of the instrument).

---

## References

1. NASA LAADS DAAC / Earthdata. *MODIS to VIIRS Transition* — mission end dates, orbital drift, and GCOS climate-data-record continuity requirement. NASA Earthdata, 2025. [https://ladsweb.modaps.eosdis.nasa.gov/learn/modis-to-viirs-transition/](https://ladsweb.modaps.eosdis.nasa.gov/learn/modis-to-viirs-transition/)
2. Calibration of the SNPP and NOAA-20 VIIRS sensors for continuity of the MODIS climate data records. *Remote Sensing of Environment*. 2023. [doi:10.1016/j.rse.2023.113716](https://doi.org/10.1016/j.rse.2023.113716)
3. Continuity between NASA MODIS Collection 6.1 and VIIRS Collection 2 land products. *Remote Sensing of Environment*. 2024. [https://www.sciencedirect.com/science/article/pii/S0034425723005151](https://www.sciencedirect.com/science/article/pii/S0034425723005151)
4. National Snow and Ice Data Center. *SSMIS sunsets, AMSR2 rises*. NSIDC Sea Ice Today, 2025. [https://nsidc.org/sea-ice-today/analyses/ssmis-sunsets-amsr2-rises](https://nsidc.org/sea-ice-today/analyses/ssmis-sunsets-amsr2-rises)
5. National Snow and Ice Data Center. *SMMR and SSM/I-SSMIS and AMSR2* — sensor-series documentation. [https://nsidc.org/data/smmr_ssmi](https://nsidc.org/data/smmr_ssmi)
6. NOAA/NSIDC. *Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6* — AMSR2 as input brightness-temperature source from 1 January 2025. [https://nsidc.org/data/g02202/versions/6](https://nsidc.org/data/g02202/versions/6)
7. *Ageing Satellites Put Crucial Sea Ice Climate Record at Risk*. **Scientific American**. [https://www.scientificamerican.com/article/ageing-satellites-put-crucial-sea-ice-climate-record-at-risk/](https://www.scientificamerican.com/article/ageing-satellites-put-crucial-sea-ice-climate-record-at-risk/)
8. Decades of science results and new technologies related to measurements of Earth's Radiation Budget from space and a pathway for continuity of observations. *Science of Remote Sensing* (Elsevier). 2026. [https://www.sciencedirect.com/science/article/pii/S2950630126000086](https://www.sciencedirect.com/science/article/pii/S2950630126000086)
9. Loeb N, et al. *Risk and Impact of a Data Gap in the Earth Radiation Budget Satellite Record*. AGU 2023. NASA NTRS. [https://ntrs.nasa.gov/api/citations/20230017173/downloads/LOEB_AGU_2023.pdf](https://ntrs.nasa.gov/api/citations/20230017173/downloads/LOEB_AGU_2023.pdf)
10. NOAA NESDIS. *Libera* — CERES follow-on mission page. [https://www.nesdis.noaa.gov/our-satellites/currently-flying/joint-polar-satellite-system/libera](https://www.nesdis.noaa.gov/our-satellites/currently-flying/joint-polar-satellite-system/libera)
11. *The Imminent Data Desert: The Future of Stratospheric Monitoring in a Rapidly Changing World*. **Bulletin of the American Meteorological Society** 106(3). 2025. [https://journals.ametsoc.org/view/journals/bams/106/3/BAMS-D-23-0281.1.xml](https://journals.ametsoc.org/view/journals/bams/106/3/BAMS-D-23-0281.1.xml)
12. UNEP Ozone Secretariat. *The Future of Stratospheric Monitoring in a Rapidly Changing World* (distributed version of [11]). 2025. [https://ozone.unep.org/sites/default/files/2025-04/The%20Future%20of%20Stratospheric%20Monitoring%20in%20a%20Rapidly%20Changing%20World.pdf](https://ozone.unep.org/sites/default/files/2025-04/The%20Future%20of%20Stratospheric%20Monitoring%20in%20a%20Rapidly%20Changing%20World.pdf)
13. Livesey N, et al. *The Continuity Microwave Limb Sounder (C-MLS)*. AGU Fall Meeting. 2022. [https://ui.adsabs.harvard.edu/abs/2022AGUFM.A52Q1224L/abstract](https://ui.adsabs.harvard.edu/abs/2022AGUFM.A52Q1224L/abstract)
14. Continuing the MLS water vapor record with OMPS LP using neural networks. *Atmospheric Measurement Techniques* 19. 2026. [https://amt.copernicus.org/articles/19/3601/2026/](https://amt.copernicus.org/articles/19/3601/2026/)
15. Eyring V, et al. Earth System Model Evaluation Tool (ESMValTool) v2.0 — an extended set of large-scale diagnostics. *Geoscientific Model Development* 13. 2020. [https://gmd.copernicus.org/articles/13/3383/2020/](https://gmd.copernicus.org/articles/13/3383/2020/)
16. Evaluating simulated climate patterns from the CMIP archives using satellite and reanalysis datasets (CMATv1). *Geoscientific Model Development* 13. 2020. [https://gmd.copernicus.org/articles/13/3627/2020/](https://gmd.copernicus.org/articles/13/3627/2020/)
17. Waliser D, et al. Observations for Model Intercomparison Project (Obs4MIPs): status for CMIP6. *Geoscientific Model Development* 13. 2020. [https://gmd.copernicus.org/articles/13/2945/2020/](https://gmd.copernicus.org/articles/13/2945/2020/)
18. Teixeira J, et al. Evolving Obs4MIPs to Support Phase 6 of the Coupled Model Intercomparison Project (CMIP6). *Bulletin of the American Meteorological Society* 96(8). 2015. [https://journals.ametsoc.org/bams/article/96/8/ES131/69444/Evolving-Obs4MIPs-to-Support-Phase-6-of-the](https://journals.ametsoc.org/bams/article/96/8/ES131/69444/Evolving-Obs4MIPs-to-Support-Phase-6-of-the)
19. ESA eoPortal. *PACE (Plankton, Aerosol, Cloud, ocean Ecosystem) Mission* — launch date and payload. [https://www.eoportal.org/satellite-missions/pace-mission](https://www.eoportal.org/satellite-missions/pace-mission)
20. NASA Earthdata. *PACE HARP2, SPEXone, OCI products released*. 2024. [https://www.earthdata.nasa.gov/data/alerts-outages/pace-harp2-spexone-oci-products-released](https://www.earthdata.nasa.gov/data/alerts-outages/pace-harp2-spexone-oci-products-released)
21. NASA Earthdata. *PACE OCI V3.1 Reprocessing Completed* — reprocessing status and data latency. 2025. [https://www.earthdata.nasa.gov/data/alerts-outages/pace-oci-v3-1-reprocessing-completed](https://www.earthdata.nasa.gov/data/alerts-outages/pace-oci-v3-1-reprocessing-completed)
22. Bridging the gap between GRACE and GRACE-FO using a hydrological model. *Science of the Total Environment*. 2022. [https://www.sciencedirect.com/science/article/abs/pii/S0048969722007513](https://www.sciencedirect.com/science/article/abs/pii/S0048969722007513)
23. Bridging the gap between GRACE and GRACE-FO missions with deep learning aided water storage simulations. *Science of the Total Environment*. 2022. [https://www.sciencedirect.com/science/article/abs/pii/S0048969722017946](https://www.sciencedirect.com/science/article/abs/pii/S0048969722017946)
24. Improving prediction of terrestrial water storage anomalies during the GRACE and GRACE-FO gap with Bayesian convolutional neural networks. *arXiv* (preprint — not peer-reviewed). 2021. [https://arxiv.org/pdf/2101.09361](https://arxiv.org/pdf/2101.09361)
25. Yang X, et al. A Two-Step Linear Model to Fill the Data Gap Between GRACE and GRACE-FO Terrestrial Water Storage Anomalies. *Water Resources Research* 59. 2023. [doi:10.1029/2022WR034139](https://doi.org/10.1029/2022WR034139)
26. Bridging Terrestrial Water Storage Anomaly During GRACE/GRACE-FO Gap Using SSA Method: A Case Study in China. *Sensors*. 2019. PMC6806599. [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6806599/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6806599/)
27. Multidecadal reconstruction of terrestrial water storage changes by combining pre-GRACE satellite observations and climate data. *Earth System Science Data* 18. 2026. [https://essd.copernicus.org/articles/18/1747/2026/](https://essd.copernicus.org/articles/18/1747/2026/)
28. Joint CEOS/CGMS Working Group on Climate. *ECV Inventory* — annually published to support gap-analysis exercises. [https://climatemonitoring.info/ecvinventory/](https://climatemonitoring.info/ecvinventory/)
29. GCOS / WMO. *About Essential Climate Variables* — 55 ECVs across atmosphere, ocean and land. [https://gcos.wmo.int/site/global-climate-observing-system-gcos/essential-climate-variables/about-essential-climate-variables](https://gcos.wmo.int/site/global-climate-observing-system-gcos/essential-climate-variables/about-essential-climate-variables)
30. ESA Climate Change Initiative. *What is an Essential Climate Variable?* [https://climate.esa.int/en/about-us-new/climate-change-initiative/what-are-ecvs/](https://climate.esa.int/en/about-us-new/climate-change-initiative/what-are-ecvs/)
31. On the Determination of GCOS ECV Product Requirements for Climate Applications. *Bulletin of the American Meteorological Society* 106(5). 2025. [https://journals.ametsoc.org/view/journals/bams/106/5/BAMS-D-24-0123.1.xml](https://journals.ametsoc.org/view/journals/bams/106/5/BAMS-D-24-0123.1.xml)
32. Observational Data for Next-Generation Climate Model Evaluation. *Bulletin of the American Meteorological Society* 107(4). 2026. [https://journals.ametsoc.org/view/journals/bams/107/4/BAMS-D-25-0079.1.pdf](https://journals.ametsoc.org/view/journals/bams/107/4/BAMS-D-25-0079.1.pdf)
33. National Academies of Sciences, Engineering, and Medicine. *Thriving on Our Changing Planet: A Decadal Strategy for Earth Observation from Space*. National Academies Press, 2018. [https://www.nationalacademies.org/read/24938/chapter/13](https://www.nationalacademies.org/read/24938/chapter/13)

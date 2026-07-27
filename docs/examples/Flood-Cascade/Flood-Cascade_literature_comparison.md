# Flood-Cascade — literature comparison (per-claim record)

Companion to `Flood-Cascade_report.md` §8. Retrieval: **PubMed** MCP connector (searches run
2026-07-26 across flood-induced contaminant mobilisation, flood-exposed Superfund/hazardous-waste
sites, flood sediment redistribution, and post-flood private-well contamination). **No claim was
verified against article full text** — all concordance judgements below rest on the abstracts
returned by PubMed, and no reference therefore carries a full-text-verified marker.

Concordance values are drawn from the closed set: **SUPPORTED / PARTIALLY SUPPORTED / CONTRADICTED /
MIXED / NOVEL / UNRESOLVED**.

---

### Claim 1 — Flood exposure of hazardous/industrial sites is a recognised, consequential risk requiring systems-level assessment

**Concordance: SUPPORTED.** The NIEHS Superfund Research Program review [1] states that
approximately 2,000 official and potential Superfund sites lie within 25 miles of the East or Gulf
coasts, many at rising flood risk as sea levels rise, and that more than 60 million US residents live
within 3 miles of a Superfund site. It argues explicitly for multidisciplinary systems approaches to
disentangle environmental-health problems compounded by climate change — the same premise as this
study, at the same level of framing.

*Where this study differs:* it operationalises the premise for **all** EPA-regulated facilities
(11,085 flood-exposed sites, of which only 12 carry a Superfund interest), not for NPL sites alone,
and it is inland-basin rather than coastal.

### Claim 2 — Floods redistribute contamination from a source location to downstream receiving areas

**Concordance: SUPPORTED.** Singer et al. [2] demonstrate, for the Yuba Fan in California's Sierra
Nevada piedmont, that flood events episodically erode 19th-century gold-mining sediment and prograde
it downstream into the Central Valley, with each major flood delivering to lowlands the equivalent of
~10–30% of the entire post-mining Sierran mercury mass so far conveyed to the San Francisco
Bay-Delta, and that the process will persist for >10⁴ years. This is a direct, quantified instance of
the source→downstream mechanism this study routes topologically.

*Where this study differs:* Singer et al. measure and model transport in one basin; this study
asserts only connectivity, across many basins, with no mass, concentration or travel time.

### Claim 3 — Downstream receiving communities bear contamination generated elsewhere, and this is an equity issue

**Concordance: SUPPORTED.** Chukwuonye et al. [3] characterise PAHs and dioxins in residential soil,
non-residential soil/sediment and indoor dust in the Globe-Miami, Arizona environmental-justice area
after the 2021 Telegraph/Mescal wildfires and subsequent flash floods. Residential soils showed
high-molecular-weight PAH co-correlations (r = 0.87–0.97) consistent with co-deposition and
redistribution of combustion-derived particles; benzo[a]anthracene and benzo[a]pyrene exceeded EPA
soil-to-groundwater screening levels in 40% and 20% of residential samples respectively, and all
samples exceeded the 2,3,7,8-TCDD soil-to-groundwater screening level. The authors frame this as
redistribution "through post-fire runoff and flooding in these climate-vulnerable EJ communities".

*Where this study differs:* the Arizona work is a single community with measurements; this study is a
national accounting with no measurements.

### Claim 4 — Flooded drinking-water wells are a direct contamination pathway warranting separate treatment from routed surface pathways

**Concordance: SUPPORTED.** Pieper et al. [4] sampled 8,822 private wells across 44 Texas counties in
the ten months after Hurricane Harvey: total coliform occurrence was 1.5× and *E. coli* 2.8× baseline
levels, and microbial contamination was 1.7–2.5× more likely where wells were inundated. Mapili et al.
[5] surveyed 211 private-well samples after four flood events (Louisiana 2016; Harvey 2017; Irma 2017;
Florence 2018) and detected *Legionella* spp. and *Mycobacterium* spp. DNA markers in 54.5% and 36.5%
of samples, with *Naegleria fowleri* the only organism more prevalent in submerged than non-submerged
wells. Both establish the flooded well as a distinct, direct pathway.

*Relation to this study:* §6.2 treats the 1,006 flood-exposed wells (356 of them drinking-water
supply) as an unrouted direct pathway for exactly this reason. The literature supports the treatment;
it does not supply the count, which is federation-derived and covers only two states.

### Claim 5 — Post-flood well contamination is under-tested, leaving the pathway largely unmeasured

**Concordance: SUPPORTED.** Pieper et al. [4] estimate that despite the largest post-hurricane well
testing campaign on record, only **4.1%** of potentially affected wells were tested, and note that
disinfection did not always eliminate contamination.

### Claim 6 — Flood-related drinking-water risk falls disproportionately on rural and under-served populations

**Concordance: PARTIALLY SUPPORTED.** Peer et al. [6] construct a Private Well Water Climate Impact
Index (Overall, Drought, Flood, Wildfire) at census-tract resolution for the continental US and find
significant demographic disparities — non-Hispanic American Indian / Alaska Native persons had
increased odds of living in higher-impact tracts for all four index types. Pieper et al. [4] report
that although more wells in urban counties were affected by Harvey, contamination *rates* were higher
in rural-county wells.

*Why only partially:* neither study frames the disparity in the **upstream-generates /
downstream-receives** terms used in §5.4. The literature establishes rural private-well vulnerability;
it does not establish that the rurality gradient arises from hydrologic routing of upstream
industrial exposure, which is what this study claims.

### Claim 7 — Ranking places on within-boundary co-location alone materially misranks flood-contamination burden; adding hydrologic routing changes 31 of the top 50 counties

**Concordance: NOVEL.** No source found. The retrieved literature demonstrates the transport
mechanism (Claims 2–3) and the site-exposure premise (Claim 1), but no study quantifies the ranking
consequence of omitting a routing step from a burden index. The specific quantities (Spearman
ρ = 0.578, Kendall τ = 0.475, 31/50 top-50 churn) are federation-derived.

### Claim 8 — 179 US counties have no flood-exposed regulated facility of their own yet sit downstream of one, covering 18.5 million residents

**Concordance: NOVEL.** No source found; a federation-derived quantity with no literature analogue.

### Claim 9 — Imported-risk counties are markedly more rural and smaller than retained-risk counties (62% vs 33% rural; median population 20,813 vs 107,215)

**Concordance: NOVEL.** No source found for this specific contrast. It is directionally consistent
with the rural private-well disparities in [4] and [6], but those concern well dependence and climate
hazard exposure, not routed industrial burden.

### Claim 10 — Contaminant monitoring coverage is systematically absent at the downstream receiving end (151 of 208 Imported/Compound counties)

**Concordance: PARTIALLY SUPPORTED.** Under-measurement of the flood-contamination pathway is well
documented for private wells [4,5], and both papers argue for routine baseline monitoring and timely
post-flood sampling. But no retrieved study addresses a *downstream-routed* monitoring gap, and a
material part of the gap measured here is federation coverage (`sawgraph` is PFAS-focused and dense
in only a few states) rather than real monitoring absence. The claim is supported in spirit and
unverified in its specific form.

### Claim 11 — PFAS observation coverage and modelled flood footprints are near-disjoint (13 of 88,007 sawgraph cells coincide with a UF-OKN flood cell)

**Concordance: NOVEL.** A knowledge-graph coverage observation with no literature analogue. It is a
property of this federation release — which states each project has loaded — and must **not** be read
as a statement about US PFAS monitoring coverage generally.

---

## Graph-side findings surfaced by the comparison

The comparison ran both ways and exposed two problems in the **graphs**, not in the literature:

1. **`sudokn` coordinate regression.** The federation's verified crosswalk documents ~42,560 SUDOKN
   sites placeable on the S2 grid via computed lat/long. The release queried here exposes
   `hasLatitudeValue`/`hasLongitudeValue` on only **225** sites, and those are dominated by foreign
   semiconductor headquarters rather than US small and medium manufacturers. This blocked the
   manufacturer source family (report §6.4) and should be reported upstream.
2. **`fiokg` NAICS sparsity.** Only 2,270 of 11,085 flood-exposed facilities (20%) carry any NAICS
   code, so the industry composition in §5.1 describes a minority subset. The EPA
   environmental-interest predicates are far more completely populated and are the more robust view
   of what kind of facility is exposed.

---

## References

1. Amolegbe SM, et al. Adapting to Climate Change: Leveraging Systems-Focused Multidisciplinary Research to Promote Resilience. *International journal of environmental research and public health*. 2022. PMID:36429393 · [doi:10.3390/ijerph192214674](https://doi.org/10.3390/ijerph192214674)
2. Singer MB, et al. Enduring legacy of a toxic fan via episodic redistribution of California gold mining debris. *Proceedings of the National Academy of Sciences of the United States of America*. 2013. PMID:24167273 · [doi:10.1073/pnas.1302295110](https://doi.org/10.1073/pnas.1302295110)
3. Chukwuonye GN, et al. Source attribution of polycyclic aromatic hydrocarbons and dioxins in soil and dust following compound climate events in legacy-contaminated environmental justice areas. *The Science of the total environment*. 2026. PMID:42456624 · [doi:10.1016/j.scitotenv.2026.182028](https://doi.org/10.1016/j.scitotenv.2026.182028)
4. Pieper KJ, et al. Microbial Contamination of Drinking Water Supplied by Private Wells after Hurricane Harvey. *Environmental science & technology*. 2021. PMID:34032415 · [doi:10.1021/acs.est.0c07869](https://doi.org/10.1021/acs.est.0c07869)
5. Mapili K, et al. Occurrence of opportunistic pathogens in private wells after major flooding events: A four state molecular survey. *The Science of the total environment*. 2022. PMID:35182640 · [doi:10.1016/j.scitotenv.2022.153901](https://doi.org/10.1016/j.scitotenv.2022.153901)
6. Peer K, et al. The private well water climate impact index: Characterization of community-level climate-related hazards and vulnerability in the continental United States. *The Science of the total environment*. 2024. PMID:39510280 · [doi:10.1016/j.scitotenv.2024.177409](https://doi.org/10.1016/j.scitotenv.2024.177409)

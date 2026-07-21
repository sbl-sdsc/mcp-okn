## Replicator specification

Everything a replicator needs to reproduce the analysis exactly. The narrative version for a reader
is in §3–§4 of `pfas_source_attribution_report.md`; this section is the authoritative specification
and the report deliberately does not restate it.

### S1. Knowledge graphs and pinned versions

| KG | Named graph | Version | Last updated |
|---|---|---|---|
| `sawgraph` | `https://purl.org/okn/frink/kg/sawgraph` | v0.0.15 | 2026-03-16 |
| `fiokg` | `https://purl.org/okn/frink/kg/fiokg` | v0.0.11 | 2026-03-18 |
| `spatialkg` | `https://purl.org/okn/frink/kg/spatialkg` | v0.0.6 | 2026-05-07 |
| `biobricks-ice` | `https://purl.org/okn/frink/kg/biobricks-ice` | v0.0.3 | 2026-03-30 |
| `biobricks-toxcast` | `https://purl.org/okn/frink/kg/biobricks-toxcast` | v0.0.2 | 2026-03-18 |

Versions read from the federation's VoID metadata via `get_kg_version` on 2026-07-20.

### S2. Join keys (the load-bearing decisions)

**Spatial key — S2 Level-13 cell** (`http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.<digits>`).

- `sawgraph` sample point → cell: `?pt a coso:SamplePoint ; kwg:sfWithin ?cell`
  (`coso:` = `http://w3id.org/coso/v1/contaminoso#`, `kwg:` = `http://stko-kwg.geog.ucsb.edu/lod/ontology/`).
- `fiokg` facility → cell: `?f a frs:FRS-Facility ; kwg:sfWithin ?cell`
  (`frs:` = `http://w3id.org/fio/v1/epa-frs#`); PFAS-flagged subset: `?f a frs:EPA-PFAS-Facility`.
- **CRITICAL — do NOT use `owl:sameAs` for facilities.** The federation's join registry records the
  `fiokg`↔`sawgraph` S2 join on `owl:sameAs`, but in `fiokg` `owl:sameAs` on a facility is a self-link
  into `epa-frs-data#`; only the materialised S2 cell nodes carry a self-`sameAs`. Using `owl:sameAs`
  returns **0** PFAS-flagged facilities and silently looks like a real (null) result.
- **1-ring adjacency**: `spatialkg` `spatial:connectedTo` (`spatial:` =
  `http://purl.org/spatialai/spatial/spatial-full#`; `kwg:spatialRelation` and
  `spatial:spatiallyRelatedTo` return the identical object set) with BOTH ends filtered to the
  `s2.level13.` prefix and `FILTER(?neighbor != ?cell)`. Verified: every one of the 2,949 study cells
  has exactly **8** neighbours (23,592 edges) — the full edge+vertex neighbourhood, not the
  4-neighbourhood.
- **Administrative geography**: `?cell kwg:spatialRelation ?county . ?county a kwg:AdministrativeRegion_2 ;
  kwg:administrativePartOf ?state . ?state a kwg:AdministrativeRegion_1`. Two IRI-prefix filters on
  `administrativeRegion.USA.` are **required**: `spatialkg` mirrors every region as a
  `datacommons.org/browser/geoId/*` node carrying the same `rdf:type` and `rdfs:label`, which
  otherwise quadruplicates every row. `kwg:sfWithin` alone is insufficient (boundary cells point only
  at their level-12 parent); `kwg:sfOverlaps` alone matched only 331 of 3,205 cells.

**Chemical key — CAS.** `sawgraph` observation `coso:ofDatasetSubstance` → parameter node carrying
`coso:casNumber`. CAS literals are **mostly undashed digit strings** (`335671` = 335-67-1) and some
are internal Maine DEP codes (`DEP18029`). Normalisation, then IRI construction:

```
BIND(IF(REGEX(STR(?raw),'^[0-9]{5,10}$'),
        REPLACE(STR(?raw),'^([0-9]+)([0-9]{2})([0-9])$','$1-$2-$3'),
        STR(?raw)) AS ?cas)
FILTER(REGEX(?cas,'^[0-9]{2,7}-[0-9]{2}-[0-9]$'))
BIND(IRI(CONCAT('http://identifiers.org/cas/', ?cas)) AS ?casIri)
```

`biobricks-ice` and `biobricks-toxcast` attach that IRI via `<http://edamontology.org/has_identifier>`.
A dashed-only regex silently drops 78 of `sawgraph`'s 131 CAS values.

**Industry.** `fio:ofIndustry` (`fio:` = `http://w3id.org/fio/v1/fio#`) → `http://w3id.org/fio/v1/naics#NAICS-<code>`.
`frs:ofPrimaryIndustry` is entirely unpopulated (0 triples for the co-located set). `fio:ofIndustry`
materialises the whole NAICS hierarchy per facility, so the leaf must be selected with
`FILTER NOT EXISTS { ?f fio:ofIndustry ?i2 . ?i2 fio:subcodeOf ?ind }`. The code comes from the IRI —
`dcterms:identifier` is absent on sector/aggregate nodes.

**ICE functional use.** Prune on the chemical-entity IRI first, then use the cheap inverse:

```
?chem edam:has_identifier <http://identifiers.org/cas/{CAS}> .
FILTER(CONTAINS(STR(?chem),'Chemical_Functional_Use_Categories'))
?rec obo:IAO_0000136 ?chem ; rdfs:label ?useSource ; sio:SIO_000300 ?useCategory .
```

The forward two-hop (`?chem obo:RO_0000056 ?mg . ?mg obo:OBI_0000299 ?rec`) is semantically identical
but fans out across `cHTS2022_invitrodb34` (2,488,499 edges) and OOMs the endpoint.

**ToxCast endpoints.** `?chem edam:has_identifier <cas IRI> ; obo:RO_0000056 ?endpoint`
(`?endpoint a bao:BAO_0000040`).

### S3. Detection semantics

`?obs coso:hasResult ?res . ?res qudt:quantityValue ?qv . ?qv a coso:DetectQuantityValue`
(non-detect: `coso:NonDetectQuantityValue`). Concentration: `?res coso:measurementValue ?v ;
coso:measurementUnit ?u`. The `maxNgL` axis is **restricted to `unit:NanoGM-PER-L`** so values are
comparable; other media (soil, sediment, tissue) contribute to detection counts but not to `maxNgL`.
26 cells returned the sentinel IRI `coso:non-detect` in the `MAX()` position (SPARQL orders IRIs above
numeric literals) and were coerced to missing.

### S4. Cohort construction

| Stage | Rule | n cells |
|---|---|---|
| Universe | ≥1 `coso:SamplePoint` with a `kwg:sfWithin` S2 L13 cell | 2,949 |
| Evaluable | universe ∧ ≥1 observation with `coso:ofDatasetSubstance` | 2,537 |
| Ranked | evaluable ∧ ≥1 `coso:DetectQuantityValue` | 2,102 |
| Control (tier N) | evaluable ∧ 0 detections | 435 |
| Excluded (tier X) | universe ∧ 0 analyte-linked observations | 412 |

Verified counts: 12,714 distinct co-located `FRS-Facility` (exact `COUNT(DISTINCT)`), 435 distinct
co-located `EPA-PFAS-Facility`, 1,304 distinct PFAS-flagged facilities in the 1-ring, 6,992 sample
points with parseable `geo:asWKT` geometry (28 further points carry `POINT EMPTY` and were dropped),
567,538 analyte-linked observations, 128,343 detections.

**Known reconciliation gap.** The per-facility itemised extract covers 12,430 of the 12,714 facilities
the aggregate `COUNT(DISTINCT)` establishes (97.8%) and 432 of the 435 PFAS-flagged. Headline counts
use the exact aggregates; the industry breakdown uses the itemised subset. 90 cells appearing in the
facility extract fall outside the SamplePoint universe (they were reached through non-SamplePoint
`sawgraph` features) and are excluded everywhere.

### S5. Confidence tiers

```
tier(cell) =
  X  if nObs == 0                              # no analyte-linked observation, excluded
  N  elif nDet == 0                            # screened negative, control set, not ranked
  A  elif nPfasFac      > 0                    # EPA-PFAS-Facility in the SAME cell
  B  elif nRingPfasFac  > 0                    # EPA-PFAS-Facility in the 1-ring only
  C  elif nFac > 0 or nRingFac > 0             # only non-PFAS-flagged FRS facilities in the window
  D  else                                      # no regulated facility in the window
```

### S6. Co-location score

Saturating transform `sat(x, k) = min(1, log1p(x) / log1p(k))`.

```
p_same = sat(nPfasFac,      5)
p_ring = sat(nRingPfasFac, 10)
f_same = sat(nFac,         20)
f_ring = sat(nRingFac,     40)

c_proximity      = max(p_same, 0.60*p_ring, 0.25*f_same, 0.10*f_ring)
c_detIntensity   = min(1, log10(1 + maxNgL) / log10(1001))     # NaN if the cell has no ng/L detection
c_detFreq        = nDet / nObs
c_analyteBreadth = min(1, nDetAnalytes / 20)
c_industryPrior  = max(sameTopWeight, ringTopWeight), 0 if no PFAS-flagged facility in the window

WEIGHTS = {proximity 0.35, detIntensity 0.25, detFreq 0.20, analyteBreadth 0.10, industryPrior 0.10}
score = 100 * Σ(wᵢ·cᵢ over AVAILABLE components) / Σ(wᵢ over AVAILABLE components)
```

Renormalising over available components means a cell measured only in a non-aqueous medium is not
penalised for lacking `c_detIntensity`. `score` is set to NaN (unranked) when `nObs == 0` or
`nDet == 0` — the score ranks *detections* by attribution plausibility, so a cell with no detection
has nothing to rank. Ties broken by `nDet` descending.

### S7. NAICS source-strength prior

Longest-prefix match on the leaf NAICS code; grouping follows EPA's PFAS-industry sector list, split
by the directness of the documented release pathway. Unmatched but PFAS-flagged → Low (0.3); no NAICS
on record → Unclassified (weight NaN, excluded from the max).

**High (1.0)** — `3251` basic chemical mfg · `3252`/`32521` resin & synthetic fibre · `3255` paint &
coating · `3259` other chemical products · `3328` metal coating & electroplating · `3221` pulp, paper
& paperboard mills · `32222` paper coating & laminating · `3131`/`3132`/`3133`/`3141`/`3149` textile
mills & finishing · `3161` leather & hide tanning · `4881` airport operations (AFFF fire training) ·
`92811` national security / military installation · `22132` sewage treatment · `5621` waste collection ·
`5622` waste treatment & disposal (landfill, hazardous waste).

**Moderate (0.6)** — `4247`/`42471` petroleum bulk stations & merchant wholesalers · `324` petroleum &
coal products · `326` plastics & rubber products · `3344` semiconductor & electronic components ·
`3345` instruments · `3359` other electrical equipment · `323` printing · `42469` chemical wholesalers ·
`3329` other fabricated metal · `3399` other misc. manufacturing · `2211` electric power generation ·
`22131` water supply · `5629` remediation & other waste services.

### S8. Statistics

Kruskal–Wallis across tiers A/B/C/D for `maxNgL`, `detFreq` and `nDetAnalytes`; one-sided
Mann–Whitney U with rank-biserial effect size for the pairwise tier contrasts; Fisher exact
(one-sided, greater) on the 2×2 of *PFAS-flagged facility in window* × *any detection* over the 2,537
evaluable cells; a 10,000-iteration permutation test resampling the tier-A-sized subset from the 1,349
scored cells with ng/L data (`numpy.random.default_rng(20260720)`); Spearman ρ between `score` and
`maxNgL`. No multiple-testing correction is applied — the tests are confirmatory of one pre-stated
ordering, not a screen.

### S9. Verified quantities

| Quantity | Value |
|---|---|
| S2 L13 cells with a PFAS sample point | 2,949 |
| …co-located with ≥1 FRS facility | 1,297 (12,714 facilities) |
| …co-located with ≥1 EPA-PFAS-Facility | 255 (435 facilities) |
| …with ≥1 PFAS-flagged facility in the 1-ring | 735 (1,304 facilities) |
| Cells with ≥1 detection | 2,102 |
| Tier A / B / C / D / N / X | 184 / 414 / 1,061 / 443 / 435 / 412 |
| Median max ng/L, tiers A / B / C / D | 36.8 / 29.6 / 16.3 / 8.0 |
| Kruskal–Wallis H (max ng/L, A–D) | 53.7, p = 1.3×10⁻¹¹ |
| Fisher OR (detection \| PFAS facility in window) | 2.15, p = 5.8×10⁻⁹ (89.8% vs 80.4%) |
| Permutation p (tier-A median vs shuffled) | 3.0×10⁻⁴ (null median 17.0 ng/L) |
| Spearman ρ (score vs max ng/L, n=1,349) | 0.817 |
| Median analytes detected, tiers A / B / C / D | 9 / 9 / 8 / 8 (monotone non-increasing, not strict) |
| Distinct analytes / with well-formed CAS | 175 / 93 |
| CAS in biobricks-ice / biobricks-toxcast | 39 / 32 |
| ICE predicted functional-use categories | 5, all "Predicted Functional Use" (0 curated OECD) |
| Max ToxCast endpoints (PFOS) | 1,510 |

### S10. Limitations that bear on replication

1. **Ascertainment bias.** Maine's PFAS sampling is risk-targeted by statute (P.L. 2021 c.478), so the
   facility–detection association is an upper bound. Maine supplies 1,286 of 2,949 cells.
2. **Co-location ≠ causation.** No hydrology, groundwater gradient, release record or temporal
   ordering was used; no check that a facility predates the sample.
3. **Extreme tail is not facility-attributable.** 68% of the 50 highest-concentration cells are tier
   C/D; the biosolids/septage land-application pathway is absent from these graphs.
4. **Industry coverage.** Only 2,452 of the 12,714 in-universe co-located facilities (19.7%) carry `fio:ofIndustry`; 76,167 of
   `fiokg`'s `EPA-PFAS-Facility` entities have none at all. Sector counts are lower bounds.
5. **Functional use is predicted, not curated** — QSUR model output; no PFAS in this set carries a
   curated OECD assignment.
6. **Aggregate parameters** (`SUM_PFOA_PFOS`, `SUM_OF_6_PFAS`) carry no CAS and drop out of every
   chemical axis despite being among the most-detected quantities.
7. **Tier A vs tier B is not statistically separable** (Mann–Whitney p = 0.14); treat as one
   facility-proximal class.
8. **Grid artefacts.** S2 cell area varies with latitude; boundary cells straddle counties (first
   county alphabetically taken as primary); a facility just outside the 1-ring is treated identically
   to one 100 km away.
9. **Two data-quality defects observed in `sawgraph`.** `parameter.PFECHS_A` is labelled
   ACETOHYDROXAMIC ACID with CAS 646-83-3 / DTXSID7022546 (mis-annotated at source); `characteristic.2180`
   is CFC-114 (76-14-2), a chlorofluorocarbon rather than a PFAS, and carries through into the ICE and
   functional-use extracts.
10. **Snapshot.** All graphs are pinned releases; both PFAS monitoring and the FRS registry change
    continuously.

### S11. Pipeline

`scripts/01_consolidate.py` → `02_score.py` → `03_tests.py` → `04_figures.py` →
`05_map_and_workbook.py` → `06_build_html.py`. `basemap_vector.py` supplies an offline vector basemap
(GSHHS/WDBII via `basemap-data`) because the execution sandbox has no egress to raster-tile hosts;
the HTML report's interactive map uses real OpenStreetMap tiles, loaded client-side by folium/Leaflet.
Headline numbers live in `data/stats.json` and are substituted into the report, the HTML and the KPI
cards from that single source. Literature validation is in `data/literature_validation.md`.

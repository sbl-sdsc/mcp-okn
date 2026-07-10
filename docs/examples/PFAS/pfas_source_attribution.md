# PFAS Source Prioritization via Knowledge-Graph Integration

*A reproducible Proto-OKN case study — environmental PFAS detections co-located with EPA-regulated facilities likely to handle PFAS, resolved to chemical identity, functional-use, and toxicological coverage, assembled across five Proto-OKN knowledge graphs on the OKN federation.*

- **Date:** 2026-07-04  **·  Model:** claude-opus-4-8
- **Endpoint:** OKN federated SPARQL — `https://apps.okn.us/federation/sparql`
- **KG versions (pinned):** sawgraph v0.0.15 · fiokg v0.0.11 · spatialkg v0.0.6 · biobricks-ice v0.0.3 · biobricks-toxcast v0.0.2
- **Companion files:** `pfas_source_attribution.html` (interactive report), `pfas_map_openstreetmap.html` (OpenStreetMap figure), `PFAS_reproducibility_transcript.md` (queries).

## Key figures

| Metric | Value |
|---|---:|
| Co-located S2 Level-13 cells (PFAS sample **and** EPA-PFAS facility) | 477 |
| PFAS-relevant facilities co-located with a sample | 696 |
| PFAS observations in co-located cells | 24,662 |
| Distinct chemicals (DTXSID) | 79 |
| States with co-location | 12 |

Co-location is defined at **S2 Level-13** (~1 km² grid cell). A "PFAS-relevant facility" is any site carrying EPA's `EPA-PFAS-Facility` designation (from the EPA PFAS Analytic Tools industry list) in fiokg.

---

## 1. Sources used

Five Proto-OKN knowledge graphs on the OKN federated SPARQL endpoint. All cross-KG integration is on **S2 Level-13 grid cells** (geospatial) and **CompTox DTXSID / CAS** (chemical).

| Knowledge graph | Ver. | Role in this analysis | Entity types contributed | Join key |
|---|---|---|---|---|
| **sawgraph** — SAWGraph PFAS KG | v0.0.15 | *Primary:* PFAS observations in water / soil / biota / food — samples & media, concentrations & detect vs. non-detect, sampling time | PFAS samples, substances (CAS + DSSTox DTXSID), sample points | S2 L13 · DTXSID |
| **fiokg** — SAWGraph FRS KG | v0.0.11 | *Primary:* EPA `PFAS-Facility` sites, NAICS industry, permit / enforcement / TRI / RCRA records, point geolocation | facilities, industries, regulatory records | S2 L13 · admin region |
| spatialkg — SAWGraph Spatial KG | v0.0.6 | S2 grid ↔ GADM county / state roll-ups; supplies the county basemap geometry | S2 cells, administrative regions, geometry | S2 L13 (direct) |
| biobricks-ice — BioBricks ICE | v0.0.3 | EPA CompTox identity (DTXSID), functional-use categories, ADME, curated high-throughput screening | chemicals, functional-use categories | DTXSID (CompTox) · CAS |
| biobricks-toxcast — BioBricks ToxCast | v0.0.2 | ToxCast high-throughput *in vitro* assay endpoints per chemical | chemicals, assay endpoints | DTXSID (CompTox) · CAS |

**Verified crosswalks** (against the federation's hand-verified join registry):

| Integration | Shared key | Verified overlap |
|---|---|---|
| fiokg ↔ sawgraph | S2 Level-13 cell | 4,712 co-located cells |
| sawgraph ↔ spatialkg | S2 Level-13 cell | 88,007 cells |
| sawgraph ↔ biobricks-ice | CAS | 12 PFAS chemicals |
| sawgraph ↔ biobricks-toxcast | CAS | 7 PFAS chemicals |

> **Methodological note.** Joining on the DTXSID that SAWGraph carries natively recovers **35** chemicals in ICE and **33** in ToxCast — far more than the CAS crosswalk (12 / 7), because Maine EGAD stores CAS without dashes, silently breaking the `identifiers.org/cas` join. The KG's native DTXSID is the more complete chemical bridge.

---

## 2. Source map — Maine PFAS detections vs. co-located facilities

The interactive figure (`pfas_source_attribution.html`, or the OpenStreetMap version `pfas_map_openstreetmap.html`) plots every EPA PFAS-relevant facility that shares a ~1 km S2 cell with a SAWGraph PFAS sample. Marker colour = source category (from facility name / NAICS); marker size = peak single-compound concentration (ng/L, water) in that cell.

The strongest signals recover Maine's principal PFAS-source sites **purely from graph structure**: military airfields with AFFF firefighting-foam history (Brunswick NAS, Bangor Air National Guard, former Loring AFB, NSA Cutler, Portsmouth Naval Shipyard), pulp & paper mills (Androscoggin / Verso · Pixelle, Woodland, Great Northern), municipal landfills and wastewater-treatment facilities, and textile / tannery mills.

---

## 3. Ranked hotspots — cells by peak single-compound PFAS concentration

Co-located S2 cells in Maine, ranked by the maximum single-compound concentration (ng/L, water) among all samples in the cell.

| # | Facilities in cell | Facilities | PFAS obs | Max ng/L |
|--:|---|--:|--:|--:|
| 1 | US Navy Naval Air Station Brunswick | 1 | 792 | 87,500 |
| 2 | Air National Guard 101st Air Refueling Wing | 2 | 204 | 21,300 |
| 3 | Pixelle · Verso Androscoggin Mill · Specialty Minerals | 3 | 752 | 20,000 |
| 4 | Hatch Hill Solid Waste Disposal Facility | 1 | 426 | 5,100 |
| 5 | Loring Development Authority (former Loring AFB) | 1 | 880 | 3,320 |
| 6 | Lewiston Solid Waste & Recycling Facility | 1 | 717 | 2,700 |
| 7 | South Portland petroleum terminals (Sprague, Global, +3) | 5 | 84 | 1,160 |
| 8 | Soil Preparation, Inc. | 1 | 120 | 1,020 |
| 9 | Bath Wastewater Treatment · Bath Snow Dump | 2 | 1,175 | 970 |
| 10 | Tasman Leather Group · Hartland WWTF | 2 | 318 | 836 |
| 11 | Tex Tech Industries Incorporated | 1 | 747 | 820 |
| 12 | Woodland Pulp Mill | 1 | 301 | 686 |
| 13 | Bath Landfill | 1 | 134 | 618 |
| 14 | Micro Metrics · Elm Street Printing | 2 | 140 | 534 |
| 15 | Presque Isle Landfill · Aroostook Waste Solutions | 2 | 112 | 392 |
| 16 | Aroostook Waste Solutions | 1 | 651 | 318 |
| 17 | ND Paper Inc — Rumford Division | 1 | 306 | 282 |
| 18 | Wiscasset WWTF | 1 | 324 | 248 |
| 19 | Rumford Paper — Farrington Mountain Landfill | 1 | 139 | 215 |
| 20 | Loring WWTF · Limestone Water & Sewer District | 2 | 226 | 193 |
| 21 | Orono CDD Landfill | 1 | 54 | 172 |
| 22 | Portsmouth Naval Shipyard | 1 | 276 | 148 |
| 23 | Belfast Wastewater Treatment Facility | 1 | 325 | 132 |
| 24 | Spinnaker Coating | 1 | 277 | 126 |
| 25 | Buckeye Terminals · Coldbrook Energy Oil Terminal | 2 | 323 | 113 |
| 26 | Kennebec Wastewater Treatment Facility | 1 | 324 | 104 |
| 27 | Eastland Woolen Mills Inc | 1 | 168 | 70 |
| 28 | Great Northern Paper #2 · Ensyn Fuels | 2 | 319 | 55.6 |
| 29 | Southwest Harbor WWTF | 1 | 318 | 51 |
| 30 | Tri-Community Landfill — Fort Fairfield | 1 | 28 | 50.3 |

---

## 4. Candidate source categories (NAICS)

Industry classes of the PFAS-relevant facilities co-located with Maine PFAS samples — a data-driven ranking of candidate source sectors. These are the industry sectors flagged by EPA's PFAS Analytic Tools (the basis of fiokg's `EPA-PFAS-Facility` class), so the prioritisation is internally consistent with the knowledge graph's own source designation.

| NAICS industry | Facilities |
|---|--:|
| Sewage Treatment Facilities | 45 |
| Chemical Manufacturing | 22 |
| Solid Waste Landfill | 21 |
| Petroleum Bulk Stations / Terminals | 19 |
| Paper Mills | 14 |
| National Security (military) | 13 |
| Semiconductor Manufacturing | 12 |
| Coating / Engraving / Heat Treating | 12 |
| Waste Collection | 12 |
| Broadwoven Fabric Mills | 11 |
| Pulp Mills | 10 |

---

## 5. Detected chemicals — identity, use & toxicology coverage

Every PFAS analyte detected in Maine co-located cells, resolved to its CompTox **DTXSID**, with ICE functional-use records and ToxCast assay coverage joined on DTXSID. Concentrations are peak ng/L in water media.

| Abbr. | Chemical | DTXSID | ng/L meas. | Cells | Max ng/L | ICE func-use | ToxCast endpts |
|---|---|---|--:|--:|--:|:--:|--:|
| PFOA | Perfluorooctanoic acid | DTXSID8031865 | 536 | 55 | 8,030 | ✓ | 1,396 |
| PFOS | Perfluorooctanesulfonic acid | DTXSID3031864 | 523 | 50 | 20,000 | ✓ | 1,510 |
| PFHpA | Perfluoroheptanoic acid | DTXSID1037303 | 506 | 52 | 9,630 | ✓ | 1,038 |
| PFHxA | Perfluorohexanoic acid | DTXSID3031862 | 482 | 52 | 28,100 | ✓ | 1,098 |
| PFBA | Perfluorobutanoic acid | DTXSID4059916 | 474 | 51 | 12,700 | — | 506 |
| PFPeA | Perfluoropentanoic acid | DTXSID6062599 | 462 | 47 | 18,200 | ✓ | 461 |
| PFHxS | Perfluorohexanesulfonic acid | DTXSID7040150 | 454 | 44 | 7,000 | ✓ | 461 |
| PFBS | Perfluorobutanesulfonic acid | DTXSID5030030 | 445 | 46 | 87,500 | ✓ | 504 |
| PFNA | Perfluorononanoic acid | DTXSID8031863 | 404 | 44 | 753 | ✓ | 1,124 |
| PFDA | Perfluorodecanoic acid | DTXSID3031860 | 286 | 34 | 857 | ✓ | 1,075 |
| PFPeS | Perfluoropentanesulfonic acid | DTXSID8062600 | 211 | 33 | 141 | ✓ | — |
| 6:2 FTSA | 6:2 Fluorotelomer sulfonic acid | DTXSID6067331 | 203 | 40 | 1,650 | ✓ | 461 |
| N-EtFOSAA | 2-(N-Ethylperfluorooctanesulfonamido)acetic acid | DTXSID5062760 | 133 | 22 | 3,470 | — | — |
| N-MeFOSAA | 2-(N-Methylperfluorooctanesulfonamido)acetic acid | DTXSID10624392 | 131 | 29 | 180 | — | — |
| PFHpS | Perfluoroheptanesulfonic acid | DTXSID8059920 | 118 | 20 | 2,060 | ✓ | 464 |
| 8:2 FTSA | 8:2 Fluorotelomer sulfonic acid | DTXSID00192353 | 78 | 15 | 610 | — | 506 |
| PFOSA | Perfluorooctanesulfonamide | DTXSID3038939 | 67 | 14 | 701 | ✓ | 1,071 |
| PFUnDA | Perfluoroundecanoic acid | DTXSID8047553 | 68 | 18 | 69.4 | ✓ | 1,123 |
| PFTeDA | Perfluorotetradecanoic acid | DTXSID3059921 | 28 | 12 | 3.18 | ✓ | 463 |
| PFTrDA | Perfluorotridecanoic acid | DTXSID90868151 | 16 | 6 | 94.2 | ✓ | 465 |
| PFDoDA | Perfluorododecanoic acid | DTXSID8031861 | 14 | 8 | 21.2 | ✓ | — |
| 4:2 FTSA | 4:2 Fluorotelomer sulfonic acid | DTXSID30891564 | 6 | 3 | 11 | — | 497 |
| HFPO-DA (GenX) | Perfluoro-2-methyl-3-oxahexanoic acid | DTXSID70880215 | 4 | 1 | 750 | — | 506 |
| 5:3 FTCA | 2H,2H,3H,3H-Perfluorooctanoic acid | DTXSID20874028 | 3 | 3 | 10.9 | — | 497 |
| PFDS | Perfluorodecanesulfonic acid | DTXSID3040148 | 3 | 2 | 1.9 | ✓ | — |

*Across all SAWGraph PFAS nationally, 35 chemicals carry an ICE record and 33 carry ToxCast coverage when joined on DTXSID; PFOS and PFOA carry the deepest toxicology (1,510 and 1,396 ToxCast endpoints; 918 and 831 ICE data groups).*

---

## 6. National footprint — where the join fires

Co-located cells (a PFAS sample and an EPA-PFAS facility in the same S2 cell) by state. Maine dominates because SAWGraph's densest campaign is the Maine EGAD program; the same join extends nationally through the SpatialKG hub wherever US-WQP samples fall near facilities.

| State | Co-located cells | PFAS facilities |
|---|--:|--:|
| Maine | 279 | 336 |
| Massachusetts | 44 | 125 |
| Minnesota | 43 | 55 |
| Indiana | 38 | 47 |
| Arizona | 26 | 54 |
| Illinois | 19 | 39 |
| New Hampshire | 13 | 17 |
| South Carolina | 3 | 3 |
| Alabama | 1 | 1 |
| Idaho | 1 | 1 |
| Kentucky | 1 | 1 |
| Wisconsin | 1 | 2 |

---

## 7. KG-internal validation — regulatory footprint (fiokg)

Validation uses **no external data**. Within fiokg, the co-located PFAS-relevant facilities carry exactly the EPA regulatory records expected of PFAS dischargers — Clean Water Act (NPDES) permits, Toxics Release Inventory reporting, RCRA hazardous-waste handling, industrial stormwater, and formal enforcement actions. Counts are Maine co-located EPA-PFAS facilities carrying each interest.

| EPA environmental interest / program (fiokg) | Facilities |
|---|--:|
| Enforcement / compliance activity | 233 |
| ICIS-NPDES discharge permit (non-major) | 217 |
| Industrial stormwater | 156 |
| TRI reporter (Toxics Release Inventory) | 101 |
| NPDES permit | 92 |
| Hazardous-waste biennial reporter | 56 |
| Formal enforcement action | 44 |
| POTW (wastewater treatment) | 42 |
| Large-Quantity Generator (RCRA) | 35 |

---

## 8. Method & reproducibility

**Join backbone.** `EPA-PFAS-Facility —sfWithin→ S2 cell ←owl:sameAs— SAWGraph cell —sfContains→ sample point ←observedAtSamplePoint— PFAS observation` (with `ofDSSToxSubstance`, `hasResult` → value + unit, media, time). Chemical axis: observation DTXSID → ICE / ToxCast on `comptox.epa.gov/dashboard/chemical/details/{DTXSID}`. Roll-ups: S2 cell → SpatialKG county / state.

**Caveats.** Same-cell (~1 km) co-location is *association*, not attribution. SAWGraph's sampling density is Maine-heavy. The concentration axis is single-compound, water-media only (soil, biota, and food are excluded from the concentration ranking). All concentrations are peak single-compound values (summed "total-PFAS" parameters are excluded).

The exact SPARQL queries behind every table above are recorded in **`PFAS_reproducibility_transcript.md`**.

---

*Reproducible knowledge-graph workflow over the Proto-OKN federation. Snapshot verified 2026-07-04.*

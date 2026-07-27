# Flood-Cascade: following flood-mobilised contamination downstream

### A federated-SPARQL case study routing flood-exposed contaminant sources through the NHDPlus network to the communities that receive them

**Date:** 2026-07-26 · **Endpoint:** OKN federated SPARQL · **Model:** claude-opus-5

> **Framing (non-negotiable).** The unit of analysis is the **US county** (5-digit FIPS), built up
> from S2 Level-13 grid cells (~1.2 km) and NHDPlus stream reaches. Coverage is the modelled
> UF-OKN flood footprint (national, {{flooded_buildings}} buildings) intersected with the OKN
> federation's hydrologic network ({{reach_network}} NHDPlus reaches across {{huc8}} HUC8
> subbasins in {{huc2}} HUC2 regions). The level of inference is **spatial-topological
> plausibility**: a routed link means water demonstrably flows from A to B, **not** that a
> contaminant was released, transported, or measured. This is **scenario-based hypothesis
> generation from model output and regulatory inventories — not field measurement and not causal
> inference.** Keep that caveat attached to every downstream claim in this report.

**Abbreviations.** COMID = NHDPlus common identifier for a stream reach; EPA FRS = US Environmental
Protection Agency Facility Registry Service; FIPS = Federal Information Processing Standard county
code; HHI = Herfindahl–Hirschman Index; HUC = hydrologic unit code (HUC2 = region, HUC4 = subregion,
HUC8 = subbasin); KG = knowledge graph; NAICS = North American Industry Classification System;
NHDPlus = National Hydrography Dataset Plus (v2); NPDES = National Pollutant Discharge Elimination
System; PFAS = per- and polyfluoroalkyl substances; PWS = public water system; RCRA = Resource
Conservation and Recovery Act; RUCC = Rural–Urban Continuum Code (1 = metro core … 9 = most rural);
S2 = Google S2 geometry grid; SDWIS = Safe Drinking Water Information System; UF-OKN = Urban
Flooding Open Knowledge Network; WQP = Water Quality Portal.

---

## 1. Executive summary

A flood is a transport event, not a static exposure. Existing burden maps — including the OKN
federation's own environmental-justice work — score a county on what sits inside its own boundary.
This study asks the question that framing cannot: **when the water leaves, where does it go, and who
is standing there?**

Starting from the UF-OKN modelled flood footprint ({{flooded_buildings}} flood-impacted buildings
resolving to {{flood_cells}} S2 Level-13 cells nationally), we found **{{facilities}} EPA-regulated
facilities** sitting inside {{facility_cells}} of those cells — a co-location rate of about 54% of
the flood cells that could be placed on the national grid. Flood exposure of regulated industry is
**moderately concentrated, not diffuse**: of the {{naics_coded}} facilities carrying a NAICS code,
manufacturing (NAICS 31–33) alone accounts for {{manufacturing}} ({{manufacturing_pct}}%), the top
three sectors take {{top3_share}}%, and the sector Herfindahl–Hirschman Index is {{hhi_sector}}.

We then routed the water. Using `hydrologykg`'s precomputed NHDPlus transitive downstream closure,
{{source_reaches}} stream reaches crossing a facility-bearing flood cell reach
{{downstream_reaches}} distinct downstream reaches over {{downstream_links}} routed links, touching
{{downstream_cells}} downstream S2 cells. Rolled up to counties, this produces a **typology** rather
than a ranking: **{{retained}} Retained** counties (their contamination stays home), **{{imported_only}}
Imported** counties (their exposure is generated upstream), **{{compound}} Compound** counties (heavy
on both), and {{low}} Low. **{{zero_local_nonzero_imported}} counties, home to
{{pop_zero_local_m}} million people, have no flood-exposed regulated facility of their own yet sit
downstream of one.** They are invisible to any co-location metric.

The imported-risk group is the point of the exercise, and it has a distinct social signature.
Imported counties are markedly more rural and smaller than Retained ones ({{imported_pct_rural}}% vs
{{retained_pct_rural}}% rural; median RUCC {{imported_med_rucc}} vs {{retained_med_rucc}}; median
population {{imported_med_pop}} vs {{retained_med_pop}}). Dropping the routing step and ranking on
co-location alone changes **{{top50_churn}} of the top 50 counties** (Spearman ρ = {{spearman}},
Kendall τ = {{kendall}}). And {{monitoring_gap_counties}} of the {{imported_only}}+{{compound}}
Imported/Compound counties — {{monitoring_gap_pop_m}} million residents — have **no contaminant
monitoring feature anywhere in their downstream cells** in the federation. What this adds is a
reproducible, federation-native method for turning a static burden map into a directed one.

## 2. Sources used

| KG | Version | Updated | Role in this study | Join key / confidence |
|---|---|---|---|---|
| `ufokn` | v0.0.3 | 2026-03-19 | Modelled flood footprint: per-building flood-depth predictions (National Water Model / HEC-RAS / SWMM derived) | Building lat/long → S2 L13 computed client-side; **model output, not observation** |
| `spatialkg` | v0.0.6 | 2026-05-07 | S2 Level-13 grid → county / state administrative regions; the spatial hub every other layer meets on | `sfWithin` on `s2.level13.{id}`; high confidence (verified crosswalk, 97,087 ufokn cells) |
| `fiokg` | v0.0.11 | 2026-03-18 | EPA FRS regulated facilities: NAICS industry, environmental-programme interests, county | S2 L13 co-location + `sfWithin` county; high confidence |
| `hydrologykg` | v0.0.9 | 2026-03-16 | NHDPlus reach network, `downstreamFlowPathTC` transitive closure, reach↔S2 `sfCrosses`, water wells | COMID node IRI = geoconnex COMID IRI; S2 L13; **the routing engine** |
| `sawgraph` | v0.0.15 | 2026-03-16 | PFAS / contaminant observation and monitoring features (Maine EGAD + national WQP) placed on S2 | `owl:sameAs` S2 L13; **sparse relative to the flood footprint** — see §6.3 |
| `ruralkg` | v0.2.7 | 2026-06-08 | County Rural–Urban Continuum Code and population (2013 vintage) | County FIPS; moderate confidence (vintage lag) |
| `sudokn` | v0.0.10 | 2026-05-08 | Small/medium manufacturer inventory — **attempted and declared insufficient** (§6.4) | Coordinates present on only {{sudokn_coord_sites}} sites in this release |

Every row above traces to a logged, non-exploratory SPARQL query in the reproducibility record.
`geoconnex` was examined during design (its `downstreamWaterbody` mainstem layer and county
predicate) but **contributes no logged result to any finding** and is therefore deliberately absent
from this table; the routing is carried entirely by `hydrologykg`, whose reach subjects are minted as
geoconnex COMID IRIs.

## 3. Design & rules

The design is a four-stage chain, each stage joining on a **geographic key**, never a name.

**Stage 1 — the flood footprint.** UF-OKN publishes flood-depth predictions as `schema:Observation`
records about individual buildings, with a `qudt` Depth property value in metres and the building's
coordinates on a `schema:GeoCoordinates` node. We took every building with a depth prediction
({{flooded_buildings}} distinct buildings; median modelled maximum depth 1.94 m) and computed its S2
Level-13 cell client-side, verified against the server's own `point_to_s2` conversion. That yields
{{flood_cells}} flood cells, of which {{cells_geolocated}} fall inside `spatialkg`'s contiguous-US
grid and resolve to {{flood_counties}} counties.

**Stage 2 — what sits in the footprint.** For each flood cell we asked `fiokg` for every EPA FRS
facility whose `sfWithin` S2 cell is that cell, collecting its NAICS codes (all hierarchy levels) and
its environmental-programme interests. This is deliberately **cell-resolution co-location**, not
county-level: county-level co-location is the naive baseline this study exists to beat.

**Stage 3 — routing.** `hydrologykg` mints each NHDPlus reach as its geoconnex COMID IRI and carries
two things that make routing possible: `sfCrosses` links from a reach to every S2 cell it passes
through, and `downstreamFlowPathTC`, a **precomputed transitive downstream closure**. A reach is a
*source reach* if it crosses a flood cell that contains at least one facility. From each source reach
we take the full downstream closure, map every downstream reach back to its S2 cells and thence to
counties, and label each source→downstream link by hydrologic proximity (§4).

**Stage 4 — who is there.** Receiving counties are profiled on rurality and population (`ruralkg`
RUCC), on whether any contaminant-monitoring feature exists in their downstream cells (`sawgraph`),
and on the flooded-well direct pathway (`hydrologykg`, §6.2).

| Inventory (verified live) | Count |
|---|---|
| Flood-impacted buildings (UF-OKN) | {{flooded_buildings}} |
| Distinct flood S2 L13 cells | {{flood_cells}} |
| Flood cells placed on the spatialkg grid | {{cells_geolocated}} |
| Counties containing ≥1 flood cell | {{flood_counties}} |
| EPA-regulated facilities inside flood cells | {{facilities}} |
| Flood cells containing ≥1 facility | {{facility_cells}} |
| NHDPlus reaches in the federation's network | {{reach_network}} |
| Reaches mapped to a county | {{reach_county_mapped}} |
| Source reaches (crossing a facility-bearing flood cell) | {{source_reaches}} |
| Routed source→downstream links | {{downstream_links}} |
| Distinct downstream reaches | {{downstream_reaches}} |
| Counties in the final typology | {{counties_scope}} |

![Flood footprint and co-located facilities](figures/fig1_flood_footprint_map.png)

> ***Figure 1. The modelled flood footprint and its co-located regulated industry (ufokn + fiokg +
> spatialkg).*** **(A)** UF-OKN flood cells, coloured by log₁₀ flooded buildings per S2 Level-13
> cell. **(B)** The subset of flood cells that contain at least one EPA FRS facility. The pale blue
> underlay in both panels is the federation's own NHDPlus reach network (a 120,000-cell sample of
> `hydrologykg` reach `sfCrosses` cells), which serves as the geographic reference layer — it traces
> the drainage network of the Upper Mississippi, Ohio, Great Lakes and Northeast basins that
> `hydrologykg` covers. Provenance: `ufokn` observation→building→`schema:geo` coordinates, S2 L13
> computed client-side; `fiokg` `sfWithin` S2 cells; `hydrologykg` `sfCrosses`. An interactive
> OpenStreetMap-tiled version of the county-level result is embedded in §5.3.

Two things are visible immediately. The flood footprint is genuinely national (26.1°N–49.3°N,
122.7°W–68.3°W) while the routable network is not, and the facility-bearing subset of flood cells is
concentrated in exactly the industrial river corridors — the Ohio, the Upper Mississippi, the Great
Lakes shore — where the routing question matters most.

## 4. Confidence tiers

Every downstream claim is graded by **how strong the hydrologic connection behind it is**, using the
hydrologic unit hierarchy as a distance proxy (the transitive closure gives connectivity but not
path length, so HUC nesting is the honest available surrogate).

| Tier | Evidence required | Interpretation | Weight | Routed links |
|---|---|---|---|---|
| **A** | Downstream reach in the **same HUC8 subbasin** as the source | Local transport; contaminant residence time short, dilution limited | 1.00 | {{tierA}} |
| **B** | Same **HUC4 subregion**, different HUC8 | Regional transport; plausible but attenuated | 0.50 | {{tierB}} |
| **C** | Same **HUC2 region**, different HUC4 | Long-range mainstem transport; strongly attenuated, retain as connectivity only | 0.25 | {{tierC}} |
| **D** | Different HUC2 region | Cross-region; would be a data artefact — **none observed** | 0.10 | 0 |

Tier C dominates by count ({{tierC}} links), which is exactly what an unbounded transitive closure on
a mainstem network produces and precisely why the tier weighting exists: a county 900 km down the
Ohio is *connected* to a flooded plating shop in Illinois, but that connection should not carry the
same weight as one 15 km downstream in the same subbasin. All imported-risk scores in §5 are
**tier-weighted**; the unweighted counts are also reported in the workbook so a reader can see how
much the weighting changes the picture. The absence of any Tier D link is a useful negative control:
the routing never crosses a continental divide, as it should not.

## 5. Findings by axis

### 5.1 Which industries are flood-exposed, and how concentrated is that exposure

Of {{facilities}} flood-exposed EPA-regulated facilities, {{naics_coded}} carry a NAICS
classification in `fiokg` (a 20% coding rate that is itself a finding — see §10, limitation 4).
Within the coded set, exposure is **moderately concentrated**: manufacturing sectors 33, 32 and 31
together contribute {{manufacturing}} facilities ({{manufacturing_pct}}%), and the three largest
sectors take {{top3_share}}% of the total. The sector-level HHI of {{hhi_sector}} sits in the range
conventionally read as moderate concentration — flood exposure is not spread evenly across the
economy, but neither is it a single-industry story.

The most flood-exposed six-digit industries are revealing in their ordinariness: general automotive
repair (811111, 67 facilities), automotive body and paint shops (811121, 61), dry-cleaning and
laundry services (812320, 55), electrical contractors (237310, 44), natural-gas distribution
(221320, 33), and — the classic PFAS and metals concern — electroplating and anodising (332813, 22).
These are small, widely distributed, chemically active premises, not a handful of mega-sites.
Reading the EPA programme interests rather than NAICS gives the same picture from the regulatory
side: 1,159 flood-exposed facilities are in a hazardous-waste programme, 1,220 are conditionally
exempt small-quantity generators, 594 hold underground storage tanks, 677 hold minor NPDES
discharge permits, 294 are Toxics Release Inventory reporters, 254 are brownfield properties, and 12
carry a Superfund or Superfund-non-NPL interest.

![Industry composition and concentration](figures/fig2_industry_concentration.png)

> ***Figure 2. Sectoral composition and concentration of flood-exposed regulated industry (fiokg ×
> ufokn × spatialkg).*** **(A)** Top 12 NAICS 2-digit sectors by number of flood-exposed facilities.
> **(B)** Cumulative share of flood-exposed facilities against sectors ranked by count; the dashed
> line marks 50%. The HHI and top-3 share are annotated. n = {{naics_coded}} NAICS-coded facilities
> of {{facilities}} total. Provenance: `fiokg` `fio:ofIndustry` (all NAICS hierarchy levels; the
> 2-digit level extracted) for facilities whose `sfWithin` S2 L13 cell is a `ufokn` flood cell.

The takeaway is that a flood-contamination programme aimed only at large NPL sites would miss most
of what is actually in the water's way; the exposed population of facilities is dominated by small
solvent-, fuel- and metal-handling premises whose individual risk is low but whose count is high.

### 5.2 Where does the water go

The routing produces {{downstream_links}} source→downstream reach links from {{source_reaches}}
source reaches — a mean fan-out of 905 downstream reaches per source, with a long right tail. Those
reaches touch {{downstream_cells}} S2 cells. Rolled to counties and restricted to genuinely
*imported* links (downstream county ≠ source county), 266 counties receive at least one routed
connection, and the distribution of upstream contributing counties is heavily skewed: most receiving
counties draw from a handful of upstream counties, while the confluence counties at the bottom of the
Ohio and Upper Mississippi draw from as many as 62.

![Routing structure](figures/fig3_routing_structure.png)

> ***Figure 3. Structure of the routed downstream network (hydrologykg + spatialkg).*** **(A)**
> Routed source→downstream reach links by hydrologic proximity tier (§4); Tier D is absent by
> construction. **(B)** Distribution of downstream fan-out — how many distinct downstream reaches
> each of the {{source_reaches}} source reaches reaches through `downstreamFlowPathTC`. **(C)**
> Distribution of the number of distinct *upstream source counties* contributing to each receiving
> county. Provenance: `hydrologykg` `hyf:downstreamFlowPathTC` from reaches with an
> `sfCrosses` link to a facility-bearing `ufokn` flood cell; downstream reaches mapped to counties
> through `sfCrosses` → `spatialkg` `sfWithin`.

Panel B is the honest picture of what an unbounded transitive closure buys you: enormous reach, and
therefore the necessity of the tier weighting in panel A. Panel C is the finding — a small number of
counties sit at the bottom of very large contributing networks, and those are precisely the places a
co-location map cannot see.

**How far downstream the data actually lets us follow.** Three limits are worth stating plainly.
(i) The closure is **topological, not hydraulic**: it says water flows A→B, with no travel time,
discharge, dilution or decay. (ii) It is **unbounded** — there is no distance cut-off in the graph,
which is why every claim in this report carries a tier label. (iii) It is **geographically
incomplete**: the network is {{reach_network}} reaches across {{huc8}} HUC8 subbasins in {{huc2}}
HUC2 regions, concentrated in the Upper Mississippi, Ohio, Great Lakes, Tennessee and Northeast
basins. Flood cells in the Gulf, South Atlantic, Texas and Pacific regions have **no routable
network in the federation** and appear in this study only as co-location, never as a source. Every
absence in the Southwest and the Southeast is a data-coverage absence, not a finding.

### 5.3 The typology: who keeps their risk, who receives someone else's

Combining the two axes — co-located flood-exposed facilities (retained) and tier-weighted upstream
flood-exposed facilities (imported) — over the {{counties_scope}} counties that appear on either axis
gives four groups.

| Typology | Counties | Median co-located facilities | Median imported facilities | % rural (RUCC ≥ 4) | Median population |
|---|---|---|---|---|---|
| **Retained** — contamination stays home | {{retained}} | 13 | 0 | {{retained_pct_rural}}% | {{retained_med_pop}} |
| **Imported** — risk generated upstream | {{imported_only}} | 0 | 402 | {{imported_pct_rural}}% | {{imported_med_pop}} |
| **Compound** — heavy on both | {{compound}} | 19 | 353 | 53% | 61,976 |
| Low | {{low}} | 0 | 0 | 54% | 35,293 |

![Typology map](figures/fig4_typology_map.png)

> ***Figure 4. Flood-cascade typology by county (all six KGs).*** Counties plotted at the median
> position of their S2 cells, coloured by typology; Compound counties are drawn larger. The pale blue
> underlay is the `hydrologykg` NHDPlus reach network as in Figure 1. Provenance: retained axis =
> `fiokg` facilities co-located with `ufokn` flood cells; imported axis = tier-weighted upstream load
> via `hydrologykg` `downstreamFlowPathTC`; counties from `spatialkg`. A fully interactive
> OpenStreetMap-tiled version of this map, with every county clickable, is embedded below.

The geography is legible at a glance: Imported and Compound counties trace the **Ohio River from
Cincinnati to its mouth, the Upper Mississippi from the Twin Cities south, and the Minnesota–Wisconsin
reach**, while Retained counties are scattered metros. This is the signature of a directed process,
not of a spatial autocorrelation artefact.

<!-- INTERACTIVE_MAP -->

> ***Interactive map. Flood-cascade typology, OpenStreetMap-tiled.*** Every county is a clickable
> marker; the popup gives its typology, co-located flood-exposed facility count, tier-weighted
> imported upstream facility count, number of contributing upstream counties, RUCC, population,
> downstream monitoring coverage, and the federation KGs that contributed. Coordinates are the
> median position of the county's S2 Level-13 cells in `spatialkg`; basemap © OpenStreetMap
> contributors.

### 5.4 Who lives downstream

The imported group is not a random subset of American counties. It is **more rural, smaller, and
poorer-served** than the retained group by every measure available in the federation.

![Who lives downstream](figures/fig5_who_lives_downstream.png)

> ***Figure 5. Social profile of the receiving communities (ruralkg × spatialkg).*** **(A)** RUCC
> distribution by typology (1 = metro core, 9 = most rural); boxes show median and interquartile
> range. **(B)** Share of counties classified rural (RUCC ≥ 4). **(C)** log₁₀ county population.
> n = 516 of {{counties_scope}} counties with a RUCC record. Provenance: `ruralkg`
> `settlementtype:hasRUCC` / `population` (2013 vintage) joined on county FIPS to the typology.

Imported counties are {{imported_pct_rural}}% rural against {{retained_pct_rural}}% for Retained;
their median RUCC is {{imported_med_rucc}} against {{retained_med_rucc}}; their median population is
{{imported_med_pop}} against {{retained_med_pop}} — roughly a fifth the size. In plain terms: **the
places that generate flood-mobilised contamination are metropolitan, and a large share of the places
that receive it are small and rural.** That asymmetry is the substantive result of adding the routing
step, and it is invisible to any within-boundary burden metric.

### 5.5 How much the ranking changes when you drop the routing

The counterfactual the study was built to answer. Ranking the same {{counties_scope}} counties on
**co-located flood-exposed facilities alone** — the co-location baseline — and comparing to the
routing-aware cascade rank:

- **{{top50_churn}} of the top 50 counties change** (19 of 50 survive in both).
- Half of the top 100 change (50/100 overlap).
- Spearman ρ = {{spearman}}, Kendall τ = {{kendall}} — a substantial but far from complete
  correspondence.
- **{{zero_local_nonzero_imported}} counties ({{pop_zero_local_m}} million residents) score exactly
  zero on the baseline and non-zero with routing.** For these places the baseline is not
  approximately wrong; it is structurally blind.

![Rank churn](figures/fig6_rank_churn.png)

> ***Figure 6. What the routing step changes (all six KGs).*** **(A)** Co-location-only rank
> (x, inverted so best is upper-left) against routing-aware cascade rank (y, inverted), one point per
> county, coloured by typology; the dashed diagonal is perfect agreement. Rank statistics annotated.
> **(B)** The twelve counties that gain the most rank positions when routing is added. Provenance:
> baseline = `fiokg` facility count per county; cascade = 50/50 blend of the retained and
> tier-weighted imported percentile scores.

The largest climbers are exactly the places the framing predicted: Lincoln County MO (+174 places, 1
co-located facility, 3,410 upstream), Wabasha County MN (+173), Dakota County MN (+173, **zero**
co-located facilities and 1,885 upstream), Livingston and Ballard Counties KY (+172/+171, zero
co-located, 4,742 upstream from 62 distinct upstream counties). Several are RUCC 8–9 — among the most
rural classifications in the scheme.

## 6. Domain analyses

**Declared coverage of the source families.** The brief named four contaminant-source families. We
**ran** three at cell resolution — regulated industrial facilities (§5.1), PFAS/contaminant
observations (§6.3), water wells as a direct pathway (§6.2) — and **could not run** the fourth,
manufacturers, at any useful resolution (§6.4). Agricultural land is treated in §6.4 as well. Nothing
in this list is silently omitted.

### 6.1 The quadrant view

![Typology quadrants](figures/fig7_typology_quadrants.png)

> ***Figure 7. Retained versus imported risk, with typology cut-points (fiokg × hydrologykg ×
> spatialkg).*** Each point is one of the {{counties_scope}} counties; x = percentile rank of
> co-located flood-exposed facilities, y = percentile rank of tier-weighted upstream flood-exposed
> facilities. Dashed lines mark the 0.60-percentile cut used to define the four groups. Point colour
> encodes the resulting typology; group sizes are in the legend. Provenance: as Figure 4.

The mass along the left edge (retained score ≈ 0, imported score high) is the Imported group and is
the visual statement of the whole study: a large, well-populated band of counties whose entire
flood-contamination exposure comes from somewhere else. The Compound group in the upper right is
small ({{compound}}) but contains the highest-stakes places — Madison County IL, Jefferson County KY,
Ramsey County MN, Hamilton County OH — which are both large emitters and large receivers.

### 6.2 Flooded drinking-water wells — a direct pathway, not a routed one

Wells deserve separate treatment because the pathway is direct: a flooded wellhead is a contamination
route with no transport step to weight or attenuate. `hydrologykg` places **{{flooded_wells}} water
wells inside modelled flood cells** — 982 Illinois State Geological Survey wells and 24 Maine
Geological Survey wells. Their recorded purposes matter:

- **{{water_supply_wells}} Illinois wells with purpose `WATER`** (water supply) and **{{domestic_wells_me}}
  Maine wells with use `Domestic`** — {{water_supply_wells}} + {{domestic_wells_me}} = 356 wells whose
  function is to supply drinking water, sitting inside a modelled flood footprint.
- {{monitoring_wells}} monitoring wells and 211 engineering wells, plus 13 water-test, 3 irrigation
  and a handful of stratigraphic/dry holes.

![Direct pathway and monitoring coverage](figures/fig8_direct_pathway_and_monitoring.png)

> ***Figure 8. The direct well pathway and the downstream monitoring gap (hydrologykg × ufokn ×
> sawgraph).*** **(A)** Wells whose `sfWithin` S2 Level-13 cell is a UF-OKN flood cell, by recorded
> purpose (Illinois ISGS) or use (Maine MGS); the two drinking-water categories are highlighted in
> red. **(B)** Imported and Compound counties split by whether **any** `sawgraph` contaminant
> observation or monitoring feature exists in any of their downstream S2 cells. Provenance:
> `hydrologykg` `il-isgs:wellPurpose` / `me-mgs:hasUse`; `sawgraph` features via `owl:sameAs` S2 L13.

This count is a **floor, and a low one**: `hydrologykg` carries well inventories for only two states,
so 356 flood-exposed drinking-water wells is what two states' worth of coverage yields, not a
national estimate. Read it as a demonstration that the pathway is queryable and materially populated,
not as a national figure.

### 6.3 Downstream monitoring — where the receiving end is unwatched

Of the {{downstream_cells}} downstream S2 cells reached by the routing, only **{{ds_monitored_cells}}
contain a `sawgraph` contaminant-observation or monitoring feature**, spread across
{{ds_monitored_counties}} counties. Turned around: **{{monitoring_gap_counties}} of the 208
Imported and Compound counties — {{monitoring_gap_pop_m}} million residents — have no contaminant
monitoring anywhere in their downstream cells** in this federation.

The mismatch is even starker at the source end. `sawgraph` carries {{sawgraph_cells}} S2 cells with
contaminant features, but only **{{sawgraph_flood_overlap}} of them coincide with a UF-OKN flood
cell**. PFAS observation coverage and modelled flood exposure are, in this release of the federation,
almost disjoint: `sawgraph` is dense in Maine and in scattered WQP sites in Indiana, Minnesota,
Arizona and Illinois, while the flood footprint is dense in Kentucky, Florida, Michigan and
Wisconsin. That is a **monitoring-design finding in its own right** — the places we model as flooding
are not the places we sample for PFAS — but it also means this study cannot corroborate any routed
link with a measurement. Every downstream claim here is topological.

### 6.4 Source families we could not place: manufacturers and agricultural land

**Manufacturers (`sudokn`).** The federation's verified crosswalk documents a computed S2 bridge for
`sudokn` covering ~42,560 sites. In the release queried here, only **{{sudokn_coord_sites}} sites carry
`hasLatitudeValue`/`hasLongitudeValue`**, and those that do are overwhelmingly foreign semiconductor
headquarters rather than US small and medium manufacturers. We therefore **could not place `sudokn`
manufacturers in the flood footprint at cell resolution and have excluded them** rather than
substitute a state-level proxy that would not be comparable to the cell-resolution facility layer.
EPA FRS manufacturing (NAICS 31–33, {{manufacturing}} facilities, §5.1) covers the regulated subset of
the same population.

**Agricultural land (`sockg`).** SOC-KG is a soil-carbon **research-site** graph, not a land-cover
layer: its verified spatial footprint is ~1,069 S2 cells across 62 counties nationally. That is two
orders of magnitude too sparse to characterise agricultural land in a {{flood_cells}}-cell flood
footprint, and we **deliberately did not run** a cell-level agricultural intersection on it. The
agricultural signal that *is* present in this study comes from `fiokg` — 88 flood-exposed facilities
in NAICS 11 (agriculture, forestry, fishing and hunting) and the EPA animal-operations and pesticide
programme interests.

## 7. Discussion

Three things follow from the analysis, in descending order of confidence.

**First, and most securely: the routing step is not a refinement, it is a different map.** Thirty-one
of the top fifty counties change when it is added, and {{zero_local_nonzero_imported}} counties move
from a structural zero to a positive score. Any burden index built on within-boundary co-location
will systematically under-serve the downstream half of a watershed. This claim rests only on graph
topology and is as strong as the NHDPlus network itself.

**Second, with good confidence: imported flood-contamination risk is a rural burden.** The
Imported group is {{imported_pct_rural}}% rural against {{retained_pct_rural}}% for Retained, with a
median population a fifth the size. The mechanism is not mysterious — regulated industry clusters in
metros, metros sit on rivers, and rivers run to smaller places — but the magnitude is worth naming,
and it inverts the usual urban framing of industrial environmental burden. The caveat is that
`ruralkg`'s RUCC and population are a 2013 vintage.

**Third, as a hypothesis to test rather than a conclusion: the receiving end is systematically
unmonitored.** {{monitoring_gap_counties}} Imported/Compound counties have no downstream contaminant
monitoring feature in this federation. Some of that is real monitoring absence and some is federation
coverage — `sawgraph` is a PFAS-focused graph with two dense states — and the two cannot be separated
with the data here. It is nonetheless the sharpest actionable signal the study produces.

**What this supports operationally.** A prioritisation for post-flood sampling would look different
from a prioritisation for site hardening. Hardening should target the Compound and Retained
counties — Madison County IL, Jefferson County KY, Ramsey County MN, Hamilton County OH — where large
numbers of flood-exposed facilities sit. **Sampling** should target the Tier-A Imported counties with
zero downstream monitoring: Wabasha and Dakota Counties MN, Lincoln County MO, Livingston and Ballard
Counties KY. And the 356 flood-exposed drinking-water wells (§6.2) are a discrete, enumerable
population that could be tested directly.

**Testable predictions.** (i) Post-flood surface-water sampling in Tier-A Imported counties should
detect elevated metals, chlorinated solvents and PFAS relative to matched Tier-C counties. (ii) The
electroplating, automotive-repair and dry-cleaning facilities identified in §5.1 should dominate any
source apportionment of a flood-mobilised solvent/metals signal in these corridors. (iii) Flooded
private wells in the Illinois `WATER`-purpose set should show microbial and, near plating and
fuel-handling premises, chemical exceedances after inundation.

## 8. Comparison with prior work

According to PubMed, retrieved via the PubMed MCP connector, the claims below were checked against
the primary literature on flood-induced contaminant mobilisation, flood-exposed hazardous-waste
sites, and post-flood private-well contamination. The full per-claim record with citations is in
`Flood-Cascade_literature_comparison.md`.

| # | Claim | Concordance |
|---|---|---|
| 1 | Flood exposure of hazardous/industrial sites is a recognised and consequential risk requiring systems-level assessment | **SUPPORTED** — NIEHS's Superfund Research Program review documents ~2,000 official and potential Superfund sites within 25 miles of the East or Gulf coasts at rising flood risk, and >60 million US residents living within 3 miles of a Superfund site, and argues explicitly for multidisciplinary systems approaches [1] |
| 2 | Floods redistribute contamination from a source location to downstream receiving areas | **SUPPORTED** — the Yuba Fan study demonstrates episodic flood-driven downstream progradation of mercury-laden legacy sediment into the Central Valley and San Francisco Bay-Delta, with each major flood delivering ~10–30% of the entire post-mining Sierran Hg mass so far conveyed [2] |
| 3 | Downstream receiving communities bear contamination generated elsewhere, and this is an equity issue | **SUPPORTED** — post-fire/flood source-apportionment work in the Globe-Miami environmental-justice area shows legacy PAHs and dioxins redistributed by runoff and flooding into residential soils and indoor dust, with exceedances of EPA soil-to-groundwater screening levels [3] |
| 4 | Flooded drinking-water wells are a direct contamination pathway warranting separate treatment from routed surface pathways | **SUPPORTED** — post-Harvey testing of 8,822 wells found total coliform 1.5× and *E. coli* 2.8× baseline, with contamination 1.7–2.5× more likely in inundated wells [4]; a four-state survey after four flood events found *Legionella* and *Mycobacterium* DNA in 54.5% and 36.5% of private-well samples [5] |
| 5 | Post-flood well contamination is under-tested, leaving the pathway largely unmeasured | **SUPPORTED** — despite the largest such campaign on record, an estimated **4.1%** of potentially affected wells were tested after Hurricane Harvey [4] |
| 6 | Flood-related drinking-water risk falls disproportionately on rural and under-served populations | **PARTIALLY SUPPORTED** — the Private Well Water Climate Impact Index finds elevated flood-related impact for private-well-dependent communities with significant demographic disparities (notably American Indian / Alaska Native populations) [6], and post-Harvey contamination rates were higher in rural-county wells even though more urban wells were affected [4]; neither study frames the disparity in the upstream-generates / downstream-receives terms used here |
| 7 | Ranking places on within-boundary co-location alone materially misranks flood-contamination burden; adding hydrologic routing changes 31 of the top 50 counties | **NOVEL** — no source found. The reviewed literature demonstrates the transport mechanism (Claims 2–3) but no retrieved study quantifies the ranking consequence of omitting routing from a burden index |
| 8 | 179 US counties have no flood-exposed regulated facility of their own yet sit downstream of one, covering 18.5 million residents | **NOVEL** — no source found; this is a federation-derived quantity with no literature analogue |
| 9 | Imported-risk counties are markedly more rural and smaller than retained-risk counties (62% vs 33% rural) | **NOVEL** — no source found for this specific contrast, though it is directionally consistent with the rural private-well disparities in Claims 4 and 6 |
| 10 | Contaminant monitoring coverage is systematically absent at the downstream receiving end (151 of 208 Imported/Compound counties) | **PARTIALLY SUPPORTED** — the under-testing of the pathway is well documented for private wells [4,5], but the specific claim of a *downstream-routed* monitoring gap is not addressed by any retrieved study, and part of the gap here is federation coverage rather than real monitoring absence |
| 11 | PFAS observation coverage and modelled flood footprints are near-disjoint (13 of 88,007 sawgraph cells) | **NOVEL** — a knowledge-graph coverage observation with no literature analogue; it is a property of this federation release, not of US monitoring generally |

Claims 1–6 were checked against the full abstracts returned by PubMed; **none of the eleven claims
was verified against article full text**, so no reference in §12 carries a full-text-verified marker.

**Where the KG evidence diverges from the literature.** The divergences are of **scope**, not of
fact. The literature establishes the *mechanism* — flood waters mobilise and redeposit contamination
(Claim 2), flooded wells become contaminated (Claim 4), and legacy-contaminated environmental-justice
communities receive redistributed pollutants (Claim 3) — but works at the scale of a single event, a
single basin, or a single community. This study contributes the complementary scale: a national,
reproducible, source-to-receptor accounting over a hydrologic network. Two divergences are worth
flagging as **graph** rather than literature problems. First, `sudokn`'s coordinate coverage in this
release (§6.4) contradicts the federation's own verified crosswalk figure of ~42,560 placed sites —
that is a data regression to report upstream, not a finding. Second, the near-disjointness of
`sawgraph` and `ufokn` coverage (Claim 11) is a property of which states each project has loaded, and
should not be read as a statement about US PFAS monitoring.

## 9. Full ranked results

The complete ranked table — all {{counties_scope}} counties with both risk axes, the typology, the
tier label, rurality, population, downstream monitoring coverage and both rankings — is in
**`Flood-Cascade_results.xlsx`** (sheet *Ranked Results*), alongside sheets for the industry
breakdown, the EPA programme inventory, the flooded-well register, a sample of the routing links, and
a *Methods & Rules* sheet. Intermediate extracts are in `data/`.

*Tip: click any header to sort; use the search box for a county or state; use the pull-downs to
isolate a typology, a hydrologic tier, a state, or the rural flag. The `sources (n)` column counts
how many federation KGs contributed to that row — `ufokn` supplies the flood footprint, `fiokg` the
co-located facilities, `hydrologykg` the routing, `spatialkg` the county geography, `ruralkg` the
rurality and population, and `sawgraph` the downstream monitoring.*

<!-- RESULTS_TABLE -->

A representative slice — the ten counties with the highest imported-risk load and **no** co-located
flood-exposed facility at all:

| County | Imported facilities (tier-weighted) | Upstream counties | Strongest tier | RUCC | Population |
|---|---|---|---|---|---|
| Livingston County, Kentucky | 4,742 (1,666.5) | 62 | B | 9 | 9,519 |
| Ballard County, Kentucky | 4,742 (1,520.8) | 62 | B | 9 | 8,249 |
| Union County, Kentucky | 4,159 (1,375.0) | 57 | B | 6 | 15,007 |
| Hardin County, Illinois | 4,159 (1,375.0) | 57 | B | 9 | 4,320 |
| Crittenden County, Kentucky | 4,159 (1,375.0) | 57 | B | 7 | 9,315 |
| Henderson County, Kentucky | 3,845 (1,296.5) | 45 | B | 2 | 46,250 |
| Spencer County, Indiana | 3,341 (1,170.5) | 41 | B | 8 | 20,952 |
| Meade County, Kentucky | 3,337 (1,168.5) | 40 | B | 3 | 28,602 |
| Dakota County, Minnesota | 1,885 (1,758.5) | 10 | **A** | 1 | 398,552 |
| Wabasha County, Minnesota | 2,408 (1,177.8) | 15 | **A** | 3 | 21,676 |

Two patterns stand out. The Kentucky/Illinois cluster at the top is a **Tier B mainstem** signal —
very large upstream loads, many contributing counties, but attenuated by distance down the Ohio; the
routing puts them high, the tier label says treat with care. The Minnesota pair is the opposite and
the more actionable: **Tier A, same-subbasin** connections with fewer upstream counties, which is a
much stronger claim about a much shorter transport path — and Dakota County MN carries 398,552
residents with **zero** flood-exposed facilities of its own.

## 10. Summary of findings & limitations

**Findings recap.** Across a national modelled flood footprint of {{flooded_buildings}} buildings
({{flood_cells}} S2 cells), {{facilities}} EPA-regulated facilities sit inside the water's way, with
exposure moderately concentrated in manufacturing and small chemically-active service premises
(HHI {{hhi_sector}}; top-3 sectors {{top3_share}}%). Routing those sources through the federation's
NHDPlus downstream closure produces {{downstream_links}} links to {{downstream_reaches}} downstream
reaches and a four-way county typology: {{retained}} Retained, {{imported_only}} Imported,
{{compound}} Compound, {{low}} Low. The imported group is the finding — {{zero_local_nonzero_imported}}
counties and {{pop_zero_local_m}} million people carry flood-contamination exposure generated
entirely upstream, they are {{imported_pct_rural}}% rural against {{retained_pct_rural}}% for the
retained group, and {{monitoring_gap_counties}} of the Imported/Compound counties have no downstream
contaminant monitoring at all. Dropping the routing step changes {{top50_churn}} of the top 50
counties. Separately, {{flooded_wells}} water wells — 356 of them drinking-water supply — sit inside
the modelled flood footprint as a direct, unrouted pathway.

**Limitations.**

1. **The flood layer is model output, not observation.** UF-OKN publishes forecast/scenario
   flood-depth predictions for buildings; a "flood cell" is a cell where the model predicts building
   inundation, not a place that has flooded. Nothing here is a record of an actual flood.
2. **The routing is topological, not hydraulic.** `downstreamFlowPathTC` asserts connectivity with no
   travel time, discharge, dilution, sorption or decay. The HUC-based tiers are a *proxy* for
   distance, not a transport model. A Tier A link is a better bet than a Tier C link; neither is a
   concentration estimate.
3. **The routable network is geographically incomplete.** {{reach_network}} reaches across {{huc8}}
   HUC8 subbasins in {{huc2}} HUC2 regions. Flood cells in the Gulf, South Atlantic, Texas, Great
   Plains and Pacific regions have no routable network here, so those states appear only as
   co-location. Absence of imported risk in the Southeast and Southwest is a coverage artefact.
4. **Only 20% of flood-exposed facilities carry a NAICS code** ({{naics_coded}} of {{facilities}}).
   The industry composition in §5.1 describes the coded subset and may not represent the rest; the
   EPA programme-interest counts, which are far more completely populated, are the more robust view.
5. **No contaminant release is asserted or observed.** A facility inside a flood cell is a facility
   that may be inundated; whether it holds anything mobilisable, in what quantity, and whether it
   would be released, is entirely outside this data.
6. **The flooded-well count is a two-state floor.** `hydrologykg` carries well inventories only for
   Illinois and Maine; {{flooded_wells}} wells is what those two states yield, not a national figure.
7. **Monitoring coverage conflates real gaps with federation gaps.** `sawgraph` is a PFAS-focused
   graph dense in Maine with scattered national WQP sites; a county with "no downstream monitoring"
   may be monitored by programmes this federation does not carry.
8. **Manufacturers and agricultural land are not represented at cell resolution** (§6.4) — `sudokn`
   coordinates and `sockg` extent are both far too sparse in these releases.
9. **Rurality and population are 2013 vintage** (`ruralkg` RUCC), so the social profile in §5.4 lags
   the flood and facility layers by more than a decade.
10. **The typology cut (0.60 percentile on each axis) is a analyst choice**, not a natural break. The
    continuous scores are in the workbook; group sizes shift with the cut, though the qualitative
    rural/urban asymmetry is stable across reasonable alternatives.
11. **Both risk axes count facilities, not hazard.** A dry-cleaner and a chemical plant count one
    each. A hazard-weighted version would need release inventories this study did not join.
12. **County centroids in the maps are the median position of a county's S2 cells**, not a
    population-weighted or geometric centroid, because the federation carries no county polygons; use
    them as locators, not as geometry.

## 11. Reproducibility

Everything needed to replicate this analysis — the originating prompt verbatim, the replicator
specification (selection rules, thresholds, join recipes, tier weights, verified quantities and
limitations), every supporting SPARQL query with its row count, and the pinned KG versions and
timing — is in [Flood-Cascade_reproducibility.md](Flood-Cascade_reproducibility.md), with the exact
scripts in `scripts/` and the intermediate extracts in `data/`.

## 12. References

> Retrieved via the **PubMed** MCP connector. Full-text verification via the **Paperclip** MCP connector.

1. Amolegbe SM, et al. Adapting to Climate Change: Leveraging Systems-Focused Multidisciplinary Research to Promote Resilience. *International journal of environmental research and public health*. 2022. PMID:36429393 · [doi:10.3390/ijerph192214674](https://doi.org/10.3390/ijerph192214674)
2. Singer MB, et al. Enduring legacy of a toxic fan via episodic redistribution of California gold mining debris. *Proceedings of the National Academy of Sciences of the United States of America*. 2013. PMID:24167273 · [doi:10.1073/pnas.1302295110](https://doi.org/10.1073/pnas.1302295110)
3. Chukwuonye GN, et al. Source attribution of polycyclic aromatic hydrocarbons and dioxins in soil and dust following compound climate events in legacy-contaminated environmental justice areas. *The Science of the total environment*. 2026. PMID:42456624 · [doi:10.1016/j.scitotenv.2026.182028](https://doi.org/10.1016/j.scitotenv.2026.182028)
4. Pieper KJ, et al. Microbial Contamination of Drinking Water Supplied by Private Wells after Hurricane Harvey. *Environmental science & technology*. 2021. PMID:34032415 · [doi:10.1021/acs.est.0c07869](https://doi.org/10.1021/acs.est.0c07869)
5. Mapili K, et al. Occurrence of opportunistic pathogens in private wells after major flooding events: A four state molecular survey. *The Science of the total environment*. 2022. PMID:35182640 · [doi:10.1016/j.scitotenv.2022.153901](https://doi.org/10.1016/j.scitotenv.2022.153901)
6. Peer K, et al. The private well water climate impact index: Characterization of community-level climate-related hazards and vulnerability in the continental United States. *The Science of the total environment*. 2024. PMID:39510280 · [doi:10.1016/j.scitotenv.2024.177409](https://doi.org/10.1016/j.scitotenv.2024.177409)
7. Proto-OKN federated SPARQL endpoint (FRINK), accessed 2026-07-26 via the `mcp-okn` server. KG versions pinned in §2.

# PFAS Source-Prioritization Study — Reproducibility Transcript

- **Date:** 2026-07-04
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql (Proto-OKN federation)

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph> (v0.0.15) — PFAS observations
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg> (v0.0.11) — EPA FRS facilities + NAICS + PFAS designation
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg> (v0.0.6) — S2 grid, admin regions, geometry
- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice> (v0.0.3) — CompTox ICE identity / functional use
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast> (v0.0.2) — ToxCast assay coverage

### Namespaces

```
coso: <http://w3id.org/coso/v1/contaminoso#>          # SAWGraph contaminant model
kwg:  <http://stko-kwg.geog.ucsb.edu/lod/ontology/>   # KnowWhereGraph / SpatialKG
epa:  <http://w3id.org/fio/v1/epa-frs#>               # fiokg EPA-FRS
fio:  <http://w3id.org/fio/v1/fio#>                   # fiokg facility/industry
geo:  <http://www.opengis.net/ont/geosparql#>
dct:  <http://purl.org/dc/terms/>
rdfs: <http://www.w3.org/2000/01/rdf-schema#>
skos: <http://www.w3.org/2004/02/skos/core#>
owl:  <http://www.w3.org/2002/07/owl#>
```

Co-location key throughout: the canonical S2 Level-13 cell IRI `http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.{id}`, reached by fiokg facilities via `kwg:sfWithin` and by SAWGraph cells via `owl:sameAs`. Maine is scoped by facility county FIPS `administrativeRegion.USA.23…`. All concentrations are single named compounds (`coso:ofDSSToxSubstance`) in ng/L (`unit/NanoGM-PER-L`); summed "total-PFAS" parameters are excluded.

## Conversation

👤 **User** — *PFAS source attribution by integrating environmental samples, regulated facilities, and chemical-use annotations. Can spatial and chemical crosswalks identify PFAS detections plausibly associated with nearby regulated facilities and known chemical-use categories? Use sawgraph (PFAS measurements), fiokg (EPA facilities + industry), spatialkg (S2/county/state rollups), and biobricks-ice / biobricks-toxcast (chemical identity, functional-use, assay coverage). Rank PFAS sample locations by co-location with PFAS-relevant facility types, stratify by compound / CAS / functional use / detection frequency / region, and validate against known monitoring programs.*

🧠 **Assistant** — COMPLETED. Verified the four proposed crosswalks against the federation join registry (fiokg↔sawgraph 4,712 S2 cells; sawgraph↔spatialkg 88,007; sawgraph↔ICE 12 CAS; sawgraph↔ToxCast 7 CAS). Established the co-location backbone `EPA-PFAS-Facility —sfWithin→ S2 cell ←owl:sameAs— SAWGraph cell —sfContains→ point ←observedAtSamplePoint— PFAS obs`. Nationally, 477 S2 cells hold both a PFAS sample and an EPA-PFAS facility (696 facilities, 24,662 single-compound observations, 79 chemicals, 12 states); **Maine dominates (279 cells / 336 facilities)** and is the proof-of-concept region. Ranking co-located cells by peak single-compound concentration recovers Maine's principal PFAS sites purely from graph structure — Brunswick NAS (87,500 ng/L PFBS), Bangor Air National Guard (21,300), the Androscoggin paper mills (20,000), landfills, and wastewater plants. Candidate source sectors (NAICS) are sewage treatment, chemical manufacturing, landfills, paper/pulp, textiles, and military. Chemical identity resolved on DTXSID: joining on SAWGraph's native DTXSID recovers 35 ICE and 33 ToxCast chemicals (vs. 12 / 7 via the dash-less Maine CAS). Validation is KG-internal: co-located facilities carry the expected NPDES / TRI / RCRA / enforcement records in fiokg. The Maine county basemap is SpatialKG geometry.

---

#### Query 1 — National co-location by state: S2 cells (and EPA-PFAS facilities) shared by a PFAS sample and a facility, rolled up to state FIPS

```sparql
SELECT ?stateFips (COUNT(DISTINCT ?cell) AS ?cells) (COUNT(DISTINCT ?fac) AS ?facilities) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a epa:EPA-PFAS-Facility ;
         kwg:sfWithin ?cell ; kwg:sfWithin ?county .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
    FILTER(STRSTARTS(STR(?county),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
    BIND(SUBSTR(STRAFTER(STR(?county),'administrativeRegion.USA.'),1,2) AS ?stateFips)
  }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?sawCell owl:sameAs ?cell . }
} GROUP BY ?stateFips ORDER BY DESC(?cells)
```
_Result: 23 Maine 279/336 · 25 MA 44/125 · 27 MN 43/55 · 18 IN 38/47 · 04 AZ 26/54 · 17 IL 19/39 · 33 NH 13/17 · 45 SC 3/3 · (AL/ID/KY/WI 1 each). Totals ≈ 477 cells / 696 facilities._

#### Query 2 — Payload sizing: PFAS observations, sample points and distinct chemicals inside co-located cells (national)

```sparql
SELECT (COUNT(DISTINCT ?obs) AS ?observations) (COUNT(DISTINCT ?point) AS ?points) (COUNT(DISTINCT ?dtxsid) AS ?chemicals) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
  }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?sawCell owl:sameAs ?cell ; kwg:sfContains ?point .
    ?obs coso:observedAtSamplePoint ?point ; coso:ofDSSToxSubstance ?dtxsid .
  }
}
```
_Result: 24,662 observations · 609 sample points · 79 distinct chemicals._

#### Query 3 — Maine chemical stratification: per-compound ng/L measurements, detections and peak concentration in co-located cells

```sparql
SELECT ?dtxsid (SAMPLE(?abbr) AS ?abbrev) (SAMPLE(?name) AS ?chem)
  (COUNT(DISTINCT ?obs) AS ?total) (SUM(IF(isNumeric(?val),1,0)) AS ?detects)
  (MAX(IF(isNumeric(?val),?val,0)) AS ?maxNgL) (COUNT(DISTINCT ?cell) AS ?cells)
WHERE {
  { SELECT DISTINCT ?cell WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?fac a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell ; kwg:sfWithin ?county .
        FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
        FILTER(STRSTARTS(STR(?county),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.23')) } } }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?sawCell owl:sameAs ?cell ; kwg:sfContains ?point .
    ?obs coso:observedAtSamplePoint ?point ; coso:ofDSSToxSubstance ?dtxsid ; coso:hasResult ?res .
    ?dtxsid rdfs:label ?name . OPTIONAL { ?dtxsid skos:altLabel ?abbr }
    ?res coso:measurementValue ?val ; coso:measurementUnit <http://qudt.org/vocab/unit/NanoGM-PER-L> .
  }
} GROUP BY ?dtxsid ORDER BY DESC(?total)
```
_Result (top): PFOA 536 / max 8,030 · PFOS 523 / 20,000 · PFHpA 506 / 9,630 · PFHxA 482 / 28,100 · PFBA 474 / 12,700 · PFPeA 462 / 18,200 · PFHxS 454 / 7,000 · PFBS 445 / **87,500** · PFNA 404 / 753 · PFDA 286 / 857 … (25 compounds)._

#### Query 4 — Candidate source categories: 6-digit NAICS industries of co-located Maine EPA-PFAS facilities

```sparql
SELECT ?label (COUNT(DISTINCT ?fac) AS ?facilities) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell ; kwg:sfWithin ?county ; fio:ofIndustry ?naics .
    ?naics a <http://w3id.org/fio/v1/naics#NAICS-Industry> ; rdfs:label ?label .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
    FILTER(STRSTARTS(STR(?county),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.23')) }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?sawCell owl:sameAs ?cell . }
} GROUP BY ?label ORDER BY DESC(?facilities)
```
_Result: Sewage Treatment Facilities 45 · Chemical Manufacturing 22 · Solid Waste Landfill 21 · Petroleum Bulk Stations/Terminals 19 · Paper Mills 14 · National Security (military) 13 · Semiconductor Mfg 12 · Coating/Engraving/Heat Treating 12 · Waste Collection 12 · Broadwoven Fabric Mills 11 · Pulp Mills 10._

#### Query 5 — Ranked hotspots: Maine co-located cells by peak single-compound concentration, with the facilities in each cell

```sparql
SELECT ?cell (COUNT(DISTINCT ?fac) AS ?nFac) (GROUP_CONCAT(DISTINCT ?fn;separator=" · ") AS ?facs)
   (COUNT(DISTINCT ?obs) AS ?nObs) (MAX(IF(isNumeric(?val),?val,0)) AS ?maxNgL) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell ; kwg:sfWithin ?county .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
    FILTER(STRSTARTS(STR(?county),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.23'))
    OPTIONAL { ?fac dct:alternative ?fn } }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?sawCell owl:sameAs ?cell ; kwg:sfContains ?point .
    ?obs coso:observedAtSamplePoint ?point ; coso:ofDSSToxSubstance ?dtxsid ; coso:hasResult ?res .
    OPTIONAL { ?res coso:measurementValue ?val ; coso:measurementUnit <http://qudt.org/vocab/unit/NanoGM-PER-L> } }
} GROUP BY ?cell ORDER BY DESC(?maxNgL) LIMIT 30
```
_Result: Brunswick NAS 87,500 (792 obs) · Bangor ANG 101st Refueling Wing 21,300 · Androscoggin mills (Pixelle/Verso) 20,000 · Hatch Hill landfill 5,100 · Loring (former AFB) 3,320 · Lewiston landfill 2,700 · South Portland terminals 1,160 · Bath WWTF 970 …_

#### Query 6 — Facility map: co-located Maine facilities with point geometry and their cell's peak concentration

```sparql
SELECT ?name ?wkt ?cell ?maxNgL ?nObs WHERE {
  { SELECT ?cell (MAX(IF(isNumeric(?v),?v,0)) AS ?maxNgL) (COUNT(DISTINCT ?obs) AS ?nObs) WHERE {
      { SELECT DISTINCT ?cell WHERE { GRAPH <https://purl.org/okn/frink/kg/fiokg> {
          ?f a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell ; kwg:sfWithin ?cty .
          FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
          FILTER(STRSTARTS(STR(?cty),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.23')) } } }
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?sc owl:sameAs ?cell ; kwg:sfContains ?pt .
        ?obs coso:observedAtSamplePoint ?pt ; coso:ofDSSToxSubstance ?dtxsid ; coso:hasResult ?r .
        OPTIONAL { ?r coso:measurementValue ?v ; coso:measurementUnit <http://qudt.org/vocab/unit/NanoGM-PER-L> } } } GROUP BY ?cell }
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell .
    OPTIONAL { ?fac dct:alternative ?name }
    OPTIONAL { ?fac geo:hasGeometry ?g . ?g geo:asWKT ?wkt } }
} ORDER BY DESC(?maxNgL)
```
_Result: ~85 named facilities with `POINT(lon lat)` geometry, e.g. Brunswick NAS `POINT(-69.924608 43.897690)` max 87,500; used for the source map._

#### Query 7 — Chemical → ICE coverage: ICE data groups (incl. functional-use) per SAWGraph PFAS, joined on DTXSID

```sparql
SELECT ?dtxid (COUNT(DISTINCT ?mg) AS ?iceGroups)
  (SUM(IF(CONTAINS(STR(?mg),'Functional_Use'),1,0)) AS ?funcUse) WHERE {
  { SELECT DISTINCT ?dtxsid WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
      ?o coso:ofDSSToxSubstance ?dtxsid . FILTER(STRSTARTS(STR(?dtxsid),'http://w3id.org/DSSTox/')) } } }
  BIND(REPLACE(STR(?dtxsid),'.*/','') AS ?dtxid)
  BIND(IRI(CONCAT('https://comptox.epa.gov/dashboard/chemical/details/',?dtxid)) AS ?comptox)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?ice <http://edamontology.org/has_identifier> ?comptox ; <http://purl.obolibrary.org/obo/RO_0000056> ?mg . }
} GROUP BY ?dtxid ORDER BY DESC(?iceGroups)
```
_Result: 35 SAWGraph PFAS carry ICE records (all with a functional-use group); PFOS 918 groups, PFOA 831, PFUnDA 734, PFDA 722, PFNA 707 … (vs. 12 via the CAS crosswalk)._

#### Query 8 — Chemical → ToxCast coverage: assay endpoints per SAWGraph PFAS, joined on DTXSID

```sparql
SELECT ?dtxid (COUNT(DISTINCT ?mg) AS ?toxEndpoints) WHERE {
  { SELECT DISTINCT ?dtxsid WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
      ?o coso:ofDSSToxSubstance ?dtxsid . FILTER(STRSTARTS(STR(?dtxsid),'http://w3id.org/DSSTox/')) } } }
  BIND(REPLACE(STR(?dtxsid),'.*/','') AS ?dtxid)
  BIND(IRI(CONCAT('https://comptox.epa.gov/dashboard/chemical/details/',?dtxid)) AS ?comptox)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
    ?c <http://edamontology.org/has_identifier> ?comptox ; <http://purl.obolibrary.org/obo/RO_0000056> ?mg . }
} GROUP BY ?dtxid ORDER BY DESC(?toxEndpoints)
```
_Result: 33 SAWGraph PFAS carry ToxCast coverage; PFOS 1,510 endpoints, PFOA 1,396, PFNA 1,124, PFUnDA 1,123, PFHxA 1,098 … (vs. 7 via the CAS crosswalk)._

#### Query 9 — KG-internal validation: EPA environmental-interest / program records of co-located Maine PFAS facilities (fiokg)

```sparql
SELECT ?interest (COUNT(DISTINCT ?fac) AS ?facilities) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a epa:EPA-PFAS-Facility ; kwg:sfWithin ?cell ; kwg:sfWithin ?cty ; epa:hasEnvironmentalInterest ?i .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
    FILTER(STRSTARTS(STR(?cty),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.23'))
    BIND(REPLACE(STR(?i),'.*EnvironmentalInterestType.','') AS ?interest) }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?sc owl:sameAs ?cell . }
} GROUP BY ?interest ORDER BY DESC(?facilities)
```
_Result: Enforcement/compliance 233 · ICIS-NPDES (non-major) 217 · Industrial stormwater 156 · TRI reporter 101 · NPDES permit 92 · Hazardous-waste biennial reporter 56 · Formal enforcement action 44 · POTW 42 · RCRA Large-Quantity Generator 35._

#### Query 10 — Verification: per-compound peak concentration in the top hotspot cell (Brunswick NAS, `s2.level13.5525220494225178624`)

```sparql
SELECT ?abbr ?name (MAX(IF(isNumeric(?v),?v,0)) AS ?maxNgL) (COUNT(DISTINCT ?obs) AS ?meas) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?sc owl:sameAs <http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.5525220494225178624> ; kwg:sfContains ?pt .
    ?obs coso:observedAtSamplePoint ?pt ; coso:ofDSSToxSubstance ?dtxsid ; coso:hasResult ?r .
    ?dtxsid rdfs:label ?name . OPTIONAL { ?dtxsid skos:altLabel ?abbr }
    ?r coso:measurementValue ?v ; coso:measurementUnit <http://qudt.org/vocab/unit/NanoGM-PER-L> .
  }
} GROUP BY ?abbr ?name ORDER BY DESC(?maxNgL)
```
_Result: PFBS 87,500 · PFHxA 28,100 · PFPeA 18,200 · PFBA 12,700 · PFHpA 9,630 · PFOA 8,030 · PFHxS 7,000 · PFOS 4,600. Confirms the hotspot peak (87,500 PFBS) is a single compound, not a summed "total-PFAS" parameter._

#### Query 11 — Basemap: Maine county boundary geometry (SpatialKG), simplified for the map figure

```sparql
SELECT ?r ?wkt WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?r a kwg:AdministrativeRegion_2 .
    FILTER(STRSTARTS(STR(?r),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.23'))
    ?r geo:hasGeometry ?g . ?g geo:asWKT ?wkt .
  }
}
```
_Result: 16 Maine county `POLYGON` geometries; Ramer–Douglas–Peucker-simplified to ~474 vertices for the SpatialKG county basemap (the fallback shown when OpenStreetMap tiles are unavailable)._

---

### Data-model notes (verified during schema profiling)

- SAWGraph observation → `coso:observedAtSamplePoint` → point; the enclosing S2 cell reaches the point via `kwg:sfContains`, and the cell `owl:sameAs` the canonical stko-kwg S2 IRI that fiokg facilities reach via `kwg:sfWithin`. (fiokg facilities are **not** the `owl:sameAs` subjects — those are fiokg's mirrored cell nodes; facility→cell is `kwg:sfWithin`.)
- `coso:measurementValue` is either a numeric literal (**detect**) or the IRI `coso:non-detect` (**non-detect**); detection filters on `isNumeric()`.
- SAWGraph observations carry the DSSTox **DTXSID** directly via `coso:ofDSSToxSubstance`; CAS lives on the parallel dataset-parameter node (`coso:casNumber`), stored dash-less in Maine EGAD — hence the DTXSID join outperforms the CAS crosswalk.
- Units vary by medium (ng/L water, ng/g soil, etc.); the concentration axis is restricted to `unit/NanoGM-PER-L` for comparability.

*All queries executed against the OKN federation on 2026-07-04. KG releases pinned above.*

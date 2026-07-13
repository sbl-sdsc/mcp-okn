# How many US counties on the SAWGraph spatial hub contain a location referenced by climatemodelskg

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation

👤 **User**

Crosswalk: `climatemodelskg` × `spatialkg` on **county FIPS**, bridged through `spoke-okn`. The 5-digit county FIPS is LATENT in climatemodelskg — it has no county entities at all. Its `cm:City` nodes carry a COMPOSITE key: `cm:admin1_code` = USPS state letters (`CA`), `cm:admin2_code` = 3-digit county suffix (`037`). spoke-okn is the bridge that converts the letters to digits: its state node `<.../location/06>` carries `so:abbr "CA"`, so CONCAT(state-FIPS, admin2) assembles `06037`. spatialkg (the SAWGraph spatial hub) stores that exact string as `kwg-ont:hasFIPS` on its `kwg-ont:AdministrativeRegion_2` county nodes.

Research question: how many US counties on the SAWGraph spatial hub contain a location referenced by climatemodelskg, joined on the assembled county FIPS — i.e. what is the size and shape of climatemodelskg's footprint on the federation's spatial hub?

Why the join is required: this is a coverage question about the *integration surface* itself. climatemodelskg alone cannot say how many counties it touches (it has no counties); spatialkg alone cannot say which of its counties the climate literature reaches. Only the assembled key, run through the spoke-okn bridge, measures the overlap — and that overlap is climatemodelskg's first and only attachment to the SAWGraph spatial hub.

---

🧠 **Assistant**

**947 US counties** on the SAWGraph spatial hub contain at least one location referenced by climatemodelskg.

| metric | value |
| --- | --- |
| climatemodelskg US cities that resolve to a hub county | **3,359** |
| distinct county FIPS shared (climatemodelskg → hub) | **947** |
| county FIPS on the SAWGraph hub (denominator) | 3,114 |
| → share of the hub's counties reached by climatemodelskg | **30.4%** |

A caution on the denominator: the hub holds **6,228 `AdministrativeRegion_2` node IRIs but only 3,114 distinct `hasFIPS` values** — every county is represented twice, once as a KWG resource (`administrativeRegion.USA.06037`) and once as a DataCommons `geoId` (`datacommons.org/browser/geoId/06037`), the two sharing one FIPS literal. Counting DISTINCT node IRIs would double the denominator and halve the coverage figure; the FIPS literal is the correct unit.

The counties climatemodelskg reaches most densely are the large metropolitan ones:

| County FIPS | County (spatialkg hub label) | climatemodelskg cities landing in it |
| --- | --- | --- |
| 06037 | Los Angeles County, California | 128 |
| 17031 | Cook County, Illinois | 100 |
| 12086 | Miami-Dade County, Florida | 51 |
| 06059 | Orange County, California | 41 |
| 36081 | Queens County, New York | 37 |
| 36103 | Suffolk County, New York | 36 |
| 36059 | Nassau County, New York | 36 |
| 42101 | Philadelphia County, Pennsylvania | 36 |

**Why it answers the question.** The count is only obtainable across all three graphs. climatemodelskg never stores a county code — it stores `admin1_code="CA"` and `admin2_code="037"` on a city, two halves of a key that has to be assembled. spoke-okn supplies the missing half of the assembly: its state node `<.../location/06>` asserts `so:abbr "CA"`, which is the only thing in the federation that converts the USPS letters into the 2-digit state FIPS. CONCAT then produces the 5-digit code that spatialkg publishes as `kwg-ont:hasFIPS`. Running that assembly end to end returns **947** — the exact hand-verified crosswalk count — and shows the shape of the overlap: it is a city-in-county **attachment**, not a county-to-county equivalence, with 3,359 climatemodelskg US cities landing in 947 of the hub's 3,114 counties (30.4%). The distribution is metropolitan-skewed, as one would expect of a literature graph: Los Angeles County alone absorbs 128 distinct climatemodelskg cities, Cook County 100. That footprint is climatemodelskg's first and only attachment to the SAWGraph spatial hub — and because the hub is where the federation's S2 cells and every other spatial leaf hang, these 947 counties are the whole surface through which climate-modeling literature can now be co-located with PFAS sampling, hydrology, land cover, or any other SAWGraph-anchored data.

**Validation.** Validated by construction on the authoritative shared standard — the US Census/FIPS 5-digit county code, which the assembled climatemodelskg key and spatialkg's `hasFIPS` literal both instantiate exactly — plus the hand-verified crosswalk (`L7-countyfips-climatemodelskg-spatialkg`, verified_count **947**), reproduced exactly by the live query. Spot checks confirm the assembly resolves correctly: `CA`+`037` → `06037` → *Los Angeles County, California*; `IL`+`031` → `17031` → *Cook County, Illinois*; `FL`+`086` → `12086` → *Miami-Dade County, Florida*. **Validated** (shared FIPS standard; counts executed live).

#### Query 1 — How many US counties on the SAWGraph spatial hub contain a climatemodelskg location, and how many climatemodelskg cities resolve to one — joined on the assembled county FIPS via the spoke-okn bridge

```sparql
PREFIX cm: <https://climatepub4kg.github.io/ontology#>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
SELECT (COUNT(DISTINCT ?fips5) AS ?counties) (COUNT(DISTINCT ?city) AS ?cities) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
    ?city cm:country_code "US" ; cm:admin1_code ?a1 ; cm:admin2_code ?a2 .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?st so:abbr ?a1 . }
  BIND(CONCAT(REPLACE(STR(?st), "^.*/location/", ""), ?a2) AS ?fips5)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?ar kwg:hasFIPS ?fips5 ; a kwg:AdministrativeRegion_2 .
  }
}
```

_1 row(s)_

| counties | cities |
| --- | --- |
| 947 | 3359 |

#### Query 2 — The denominator: county FIPS codes on the SAWGraph spatial hub — note each county carries TWO node IRIs (KWG resource + DataCommons geoId) but only one FIPS literal

```sparql
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
SELECT (COUNT(DISTINCT ?f) AS ?hubCountyFips) (COUNT(DISTINCT ?ar) AS ?hubCountyNodes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?ar a kwg:AdministrativeRegion_2 ; kwg:hasFIPS ?f .
  }
}
```

_1 row(s)_

| hubCountyFips | hubCountyNodes |
| --- | --- |
| 3114 | 6228 |

#### Query 3 — The SAWGraph hub counties that climatemodelskg reaches most densely, by number of distinct climate-literature cities landing in them

```sparql
PREFIX cm: <https://climatepub4kg.github.io/ontology#>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?fips5 ?cLabel (COUNT(DISTINCT ?city) AS ?nCities) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
    ?city a cm:City ; cm:country_code "US" ; cm:admin1_code ?a1 ; cm:admin2_code ?a2 .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?st so:abbr ?a1 . }
  BIND(CONCAT(REPLACE(STR(?st), "^.*/location/", ""), ?a2) AS ?fips5)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?ar kwg:hasFIPS ?fips5 ; a kwg:AdministrativeRegion_2 ; rdfs:label ?cLabel .
  }
} GROUP BY ?fips5 ?cLabel ORDER BY DESC(?nCities) LIMIT 8
```

_8 row(s) — showing first 5_

| fips5 | cLabel | nCities |
| --- | --- | --- |
| 06037 | Los Angeles County, California | 128 |
| 17031 | Cook County, Illinois | 100 |
| 12086 | Miami-Dade County, Florida | 51 |
| 06059 | Orange County, California | 41 |
| 36081 | Queens County, New York | 37 |

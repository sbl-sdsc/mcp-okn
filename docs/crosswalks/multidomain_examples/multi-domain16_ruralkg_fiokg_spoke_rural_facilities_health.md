# UC16 — Rural-Urban Classification × Industrial Facilities × Health by County (ruralkg + fiokg + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Rural sociology / settlement classification (ruralkg) × Environmental regulation (fiokg) × Environmental health (SPOKE)
- **Shared join key:** county FIPS (ruralkg `censusCounty` → KWG `administrativeRegion.USA.{FIPS5}`; fiokg `sfWithin` county region; SPOKE `/location/{FIPS5}`)

## Question
For the counties carrying the heaviest EPA Toxic Release Inventory (TRI) facility burden, where do they sit on the Rural-Urban Continuum (ruralkg RUCC code, 1 = most metropolitan → 9 = most rural), and what is their population and ambient pollutant burden (SPOKE)?

## Result (top TRI-facility counties)

| county | RUCC | population | TRI facilities | pollutants |
| --- | --- | --- | --- | --- |
| Los Angeles County | 1 | 9,818,605 | 1,525 | 171 |
| Cook County | 1 | 5,194,675 | 1,285 | 154 |
| Harris County | 1 | 4,092,459 | 650 | 182 |
| Maricopa County | 1 | 3,817,117 | 593 | 153 |
| Cuyahoga County | 1 | 1,280,122 | 512 | 148 |
| Orange County | 1 | 3,010,232 | 502 | 154 |
| Dallas County | 1 | 2,368,139 | 427 | 149 |
| Worcester County | 2 | 798,552 | 313 | 148 |
| San Bernardino County | 1 | 2,035,210 | 284 | 170 |

## Why it answers the question
Each county is jointly described by its rural-urban classification + population (ruralkg), its TRI industrial-facility burden (fiokg), and its ambient pollutant diversity (SPOKE). The result confirms the expected gradient: the heaviest toxic-release-facility burden concentrates almost entirely in RUCC-1 (most metropolitan) high-population counties — an environmental-justice-relevant pattern linking industrial density to urban populations. None of the three graphs alone connects settlement type, facility inventory, and pollutant monitoring; the county FIPS key fuses them.

## Validation
Integration validated by construction on the authoritative county FIPS key (verified ruralkg↔SPOKE and fiokg↔SPOKE county crosswalks; RUCC is the USDA Rural-Urban Continuum Code standard). The urban concentration of industrial facilities is face-valid and consistent with environmental-justice literature; specific health claims are not asserted beyond the joined counts.

## SPARQL
```sparql
PREFIX epa: <http://w3id.org/fio/v1/epa-frs#>
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX st: <http://sail.ua.edu/ruralkg/settlementtype/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?county ?rucc_code ?population ?tri_facilities ?pollutants WHERE {
  { SELECT ?fips (COUNT(DISTINCT ?f) AS ?tri_facilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?f epa:hasEnvironmentalInterest <http://w3id.org/fio/v1/epa-frs-data#d.EnvironmentalInterestType.Trireporter> ; kwgo:sfWithin ?creg .
        FILTER(STRSTARTS(STR(?creg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.')) }
      BIND(REPLACE(STR(?creg),'^.*administrativeRegion\\.USA\\.','') AS ?fips) FILTER(STRLEN(?fips)=5)
    } GROUP BY ?fips ORDER BY DESC(?tri_facilities) LIMIT 15 }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?cs st:censusCounty ?reg ; st:hasRUCC ?r . OPTIONAL { ?cs st:population ?population } BIND(REPLACE(STR(?r),'^.*RUCC_2013_','') AS ?rucc_code) }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } } } GROUP BY ?loc ?county }
}
ORDER BY DESC(?tri_facilities)
```

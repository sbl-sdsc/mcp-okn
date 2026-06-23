# UC17 — Federal Judicial Activity × Rural-Urban Classification × Health by County (SCALES + ruralkg + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Federal judiciary (SCALES) × Rural sociology (ruralkg) × Environmental health (SPOKE)
- **Shared join key:** county FIPS (SCALES `hasIdbCounty`; ruralkg `censusCounty`; SPOKE `/location/{FIPS5}`)

## Question
For the counties with the highest federal court caseload, where do they sit on the Rural-Urban Continuum (ruralkg RUCC), and what is their ambient pollutant burden (SPOKE)? This profiles federal judicial activity against settlement type and environmental context.

## Result (top federal-caseload counties)

| county | RUCC | federal cases | pollutants |
| --- | --- | --- | --- |
| Cook County | 1 | 113,188 | 154 |
| Los Angeles County | 1 | 15,439 | 171 |
| San Diego County | 1 | 11,752 | 155 |
| Miami-Dade County | 1 | 10,387 | 146 |
| Kings County (NY) | 1 | 9,099 | 130 |
| New York County | 1 | 8,009 | 125 |
| Fulton County | 1 | 6,789 | 145 |
| Harris County | 1 | 6,086 | 182 |
| Philadelphia County | 1 | 5,659 | 142 |

## Why it answers the question
SCALES supplies the federal court caseload per county, ruralkg supplies the rural-urban classification, and SPOKE supplies the ambient pollutant diversity — three independent layers fused on county FIPS. Federal caseload, like industrial facility burden (UC16), concentrates overwhelmingly in RUCC-1 metropolitan counties (Cook County's Northern District of Illinois leads at 113k). The shared county key lets a judicial-activity graph be read against settlement type and environmental burden simultaneously. No single graph spans the judiciary, settlement classification, and environmental monitoring.

## Validation
Integration validated by construction on the authoritative county FIPS key (verified SCALES↔SPOKE and ruralkg↔SPOKE county crosswalks; RUCC is the USDA standard). The urban concentration of federal caseload is face-valid (federal district courts sit in metropolitan centers). No causal claims are asserted beyond the joined counts.

## SPARQL
```sparql
PREFIX scales: <http://schemas.scales-okn.org/rdf/scales#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX st: <http://sail.ua.edu/ruralkg/settlementtype/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?county ?rucc_code ?federal_cases ?pollutants WHERE {
  { SELECT ?fips (COUNT(DISTINCT ?x) AS ?federal_cases) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> { ?x scales:hasIdbCounty ?c . FILTER(?c != 88888) }
      BIND(REPLACE(CONCAT('00000',STR(xsd:integer(?c))),'^.*(.{5})$','$1') AS ?fips)
    } GROUP BY ?fips ORDER BY DESC(?federal_cases) LIMIT 15 }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?cs st:censusCounty ?reg ; st:hasRUCC ?r . BIND(REPLACE(STR(?r),'^.*RUCC_2013_','') AS ?rucc_code) }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } } } GROUP BY ?loc ?county }
}
ORDER BY DESC(?federal_cases)
```

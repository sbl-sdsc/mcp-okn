# UC15 — Water Monitoring × Soil-Carbon Agriculture × Health by County (geoconnex + SOCKG + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Hydrology (geoconnex) × Soil-carbon agriculture / climate (SOCKG) × Environmental health (SPOKE)
- **Shared join key:** county FIPS (SOCKG county = KWG `administrativeRegion.USA.{FIPS5}`; geoconnex `gnis:county` → `ref/counties/{FIPS5}`; SPOKE `/location/{FIPS5}`)

## Question
For the counties where SOCKG runs soil-organic-carbon / GHG-flux experiments, how dense is the hydrologic-monitoring network (geoconnex water features) and what is the ambient pollutant burden (SPOKE)? This places agricultural soil-carbon research counties into their water-monitoring and environmental-health context.

## Result (SOCKG soil-carbon counties, by geoconnex water-feature density)

| county | water features (geoconnex) | ambient pollutants (SPOKE) |
| --- | --- | --- |
| Larimer County, CO | 1,207 | 130 |
| Gallatin County, MT | 837 | 143 |
| Umatilla County, OR | 788 | 151 |
| Centre County, PA | 613 | 145 |
| Weld County, CO | 562 | 132 |
| Twin Falls County, ID | 425 | 143 |
| Florence County, SC | 377 | 149 |
| Limestone County, AL | 365 | 141 |
| Laramie County, WY | 281 | 149 |
| Sauk County, WI | 263 | 146 |

## Why it answers the question
Each county hosts a SOCKG soil-carbon experiment, a geoconnex-catalogued set of hydrologic monitoring features (wells, streams, catchments), and a SPOKE record of ambient pollutants detected — three independent data layers fused on county FIPS. The counties are recognizable agricultural-research areas (Larimer/Weld CO, Gallatin MT, Umatilla OR — Mountain-West and Corn-Belt-adjacent farming regions). No single graph supports this: SOCKG has soil-carbon sites but no hydrologic network or pollutant inventory; geoconnex has water features but no agricultural-experiment or pollutant data; SPOKE has pollutants but neither soil-carbon nor hydrologic-feature data.

## Validation
Integration validated by construction on the authoritative county FIPS key (verified SOCKG↔SPOKE and geoconnex↔SPOKE county crosswalks). The result is an environmental data-integration use case; the soil-carbon counties have strong face validity as US agricultural-research sites. Specific environmental-health claims are not asserted beyond the joined counts.

## SPARQL
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX gnis: <http://gnis-ld.org/lod/gnis/ontology/>
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
SELECT ?county (COUNT(DISTINCT ?wf) AS ?water_features) ?pollutants WHERE {
  { SELECT DISTINCT ?fips WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> { ?reg a kwgo:AdministrativeRegion_2 . }
      BIND(REPLACE(STR(?reg),'^.*administrativeRegion\\.USA\\.','') AS ?fips) FILTER(STRLEN(?fips)=5) } }
  BIND(IRI(CONCAT('https://geoconnex.us/ref/counties/',?fips)) AS ?gcounty)
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?wf gnis:county ?gcounty . }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } } } GROUP BY ?loc ?county }
}
GROUP BY ?county ?pollutants ORDER BY DESC(?water_features) LIMIT 12
```

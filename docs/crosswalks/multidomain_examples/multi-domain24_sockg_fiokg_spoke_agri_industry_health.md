# UC24 — Soil-Carbon Agriculture × Industrial Facilities × Health by County (SOCKG + fiokg + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Soil-carbon agriculture / climate (SOCKG) × Environmental regulation (EPA facilities, fiokg) × Environmental health (SPOKE)
- **Shared join key:** county FIPS (SOCKG county = KWG `administrativeRegion.USA.{FIPS5}`; fiokg `sfWithin` county; SPOKE `/location/{FIPS5}`)

## Question
For the counties where SOCKG runs soil-organic-carbon experiments, how heavy is the EPA-regulated industrial-facility presence (fiokg) and the ambient pollutant burden (SPOKE)? This sets agricultural soil-carbon research counties against their industrial-facility and environmental-health context.

## Result (SOCKG soil-carbon counties by EPA facility count)

| county | EPA facilities (fiokg) | ambient pollutants (SPOKE) |
| --- | --- | --- |
| Weld County, CO | 14,636 | 132 |
| Ramsey County, MN | 13,106 | 168 |
| Dakota County, MN | 9,761 | 161 |
| Rice County, MN | 3,664 | 147 |
| Lancaster County, NE | 3,376 | 145 |
| Lubbock County, TX | 3,189 | 143 |
| Laramie County, WY | 2,642 | 149 |
| Larimer County, CO | 2,639 | 130 |
| Tippecanoe County, IN | 2,076 | 148 |
| Gallatin County, MT | 1,810 | 143 |

## Why it answers the question
Each county hosts a SOCKG soil-carbon experiment, an fiokg-registered set of EPA-regulated facilities, and a SPOKE record of ambient pollutants — three independent layers fused on county FIPS. The result is striking: agricultural soil-carbon research counties such as Weld County, CO carry an enormous regulated-facility footprint (14,636 facilities — reflecting Weld's dense oil-and-gas plus agricultural operations), illustrating how agricultural-research geographies overlap heavily with industrial activity. No single graph spans soil-carbon experiments, the facility registry, and pollutant monitoring.

## Validation
Integration validated by construction on the authoritative county FIPS key (verified SOCKG↔SPOKE and fiokg↔SPOKE county crosswalks). The leading counties (Weld CO, Ramsey/Dakota MN — agricultural regions with major industrial/energy activity) have strong face validity. This is an environmental data-integration use case; no causal claim is asserted beyond the joined counts.

## SPARQL
```sparql
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?county (COUNT(DISTINCT ?f) AS ?epa_facilities) ?pollutants WHERE {
  { SELECT DISTINCT ?fips ?reg WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> { ?reg a kwgo:AdministrativeRegion_2 . }
      BIND(REPLACE(STR(?reg),'^.*administrativeRegion\\.USA\\.','') AS ?fips) FILTER(STRLEN(?fips)=5) } }
  GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f kwgo:sfWithin ?reg . }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } } } GROUP BY ?loc ?county }
}
GROUP BY ?county ?pollutants ORDER BY DESC(?epa_facilities) LIMIT 12
```

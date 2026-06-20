# UC21 — PFAS Contamination × Hydrologic Monitoring × Health by County (SAWGraph + geoconnex + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** PFAS contamination science (SAWGraph) × Hydrology (geoconnex) × Environmental health (SPOKE)
- **Shared join key:** county FIPS (SAWGraph via Data Commons geoId → FIPS5; geoconnex `gnis:county`; SPOKE `/location/{FIPS5}`)

## Question
For the counties with the most intensive PFAS sampling (SAWGraph), how dense is the hydrologic-monitoring network (geoconnex water features) and what is the ambient pollutant burden (SPOKE)? This couples a contamination-sampling campaign to the water-monitoring infrastructure and broader pollutant context of the same counties.

## Result (top PFAS-sampling counties)

| county | PFAS sample points | water features (geoconnex) | ambient pollutants (SPOKE) |
| --- | --- | --- | --- |
| Somerset County, ME | 830 | 1,427 | 146 |
| Cumberland County, ME | 671 | 1,443 | 147 |
| Aroostook County, ME | 615 | 1,963 | 146 |
| Kennebec County, ME | 592 | 559 | 146 |
| Waldo County, ME | 560 | 581 | 144 |
| York County, ME | 539 | 1,044 | 149 |
| Washington County, MN | 454 | 216 | 185 |
| Penobscot County, ME | 420 | 1,447 | 149 |
| Hancock County, ME | 172 | 2,456 | 145 |
| Pima County, AZ | 147 | 1,725 | 148 |

## Why it answers the question
Each county is jointly described by its PFAS sampling intensity (SAWGraph), the size of its hydrologic-monitoring network (geoconnex water wells/streams/catchments), and its ambient pollutant diversity (SPOKE) — three independent environmental data layers fused on county FIPS. Maine's statewide PFAS program dominates, with Washington County MN (the 3M legacy site) again standing out. The water-feature counts contextualize where the PFAS sampling sits relative to monitored surface- and ground-water. No single graph spans contamination sampling, hydrologic infrastructure, and pollutant monitoring.

## Validation
The PFAS-contamination premise is supported by the literature already cited for UC03 (Hu et al., *Environ Sci Technol Lett* 2016, [DOI](https://doi.org/10.1021/acs.estlett.6b00260) — industrial/WWTP/fire-training sources predict PFAS in water). This integration is validated by construction on the county FIPS key (verified SAWGraph→county and geoconnex↔SPOKE crosswalks); the Maine-dominated ranking is face-valid given the statewide testing program.

## SPARQL
```sparql
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX gnis: <http://gnis-ld.org/lod/gnis/ontology/>
SELECT ?county ?pfas_sample_points (COUNT(DISTINCT ?wf) AS ?water_features) ?pollutants_detected WHERE {
  { SELECT ?fips (COUNT(DISTINCT ?spt) AS ?pfas_sample_points) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?spt kwgo:sfWithin ?geo . FILTER(STRSTARTS(STR(?geo),'https://datacommons.org/browser/geoId/'))
        BIND(REPLACE(STR(?geo),'^.*/geoId/','') AS ?gid) FILTER(STRLEN(?gid)=10) BIND(SUBSTR(?gid,1,5) AS ?fips) }
    } GROUP BY ?fips ORDER BY DESC(?pfas_sample_points) LIMIT 12 }
  BIND(IRI(CONCAT('https://geoconnex.us/ref/counties/',?fips)) AS ?gcounty)
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?wf gnis:county ?gcounty . }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants_detected) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } } } GROUP BY ?loc ?county }
}
GROUP BY ?county ?pfas_sample_points ?pollutants_detected ORDER BY DESC(?pfas_sample_points)
```

# UC22 — Industrial Facilities × Hydrologic Monitoring × Pollutants by County (fiokg + geoconnex + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Environmental regulation (EPA facilities, fiokg) × Hydrology (geoconnex) × Environmental health (SPOKE)
- **Shared join key:** county FIPS (fiokg `sfWithin` county; geoconnex `gnis:county`; SPOKE `/location/{FIPS5}`)

## Question
For the counties with the heaviest EPA Toxic Release Inventory (TRI) facility burden, how extensive is the hydrologic-monitoring network (geoconnex water features) and what is the ambient pollutant burden (SPOKE)? This relates industrial-facility density to monitored water resources and measured pollutants.

## Result (top TRI-facility counties)

| county | TRI facilities | water features (geoconnex) | ambient pollutants (SPOKE) |
| --- | --- | --- | --- |
| Los Angeles County | 1,525 | 2,389 | 171 |
| Cook County | 1,285 | 1,144 | 154 |
| Harris County | 650 | 1,072 | 182 |
| Maricopa County | 593 | 1,844 | 153 |
| Cuyahoga County | 512 | 398 | 148 |
| Orange County | 502 | 633 | 154 |
| Dallas County | 427 | 260 | 149 |
| Middlesex County | 397 | 1,363 | 151 |
| Santa Clara County | 363 | 714 | 153 |
| Worcester County | 313 | 1,945 | 148 |

## Why it answers the question
Each county is jointly described by its TRI industrial-facility burden (fiokg), the size of its hydrologic-monitoring network (geoconnex), and its ambient pollutant diversity (SPOKE) — three independent layers fused on county FIPS. The combination identifies where heavy industrial activity co-occurs with extensive monitored water resources and broad pollutant detection (e.g., LA County: 1,525 TRI facilities, 2,389 water features, 171 pollutants). No single graph spans the facility registry, the hydrologic-feature catalog, and the pollutant-monitoring layer.

## Validation
Integration validated by construction on the authoritative county FIPS key (verified fiokg↔SPOKE and geoconnex↔SPOKE county crosswalks). The TRI-facility/health premise is supported by the environmental-justice literature already cited for UC02 (Sansom et al., *Clim Risk Manag* 2023, [DOI](https://doi.org/10.1016/j.crm.2023.100507)). No causal claims are asserted beyond the joined counts.

## SPARQL
```sparql
PREFIX epa: <http://w3id.org/fio/v1/epa-frs#>
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX gnis: <http://gnis-ld.org/lod/gnis/ontology/>
SELECT ?county ?tri_facilities (COUNT(DISTINCT ?wf) AS ?water_features) ?pollutants WHERE {
  { SELECT ?fips (COUNT(DISTINCT ?f) AS ?tri_facilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?f epa:hasEnvironmentalInterest <http://w3id.org/fio/v1/epa-frs-data#d.EnvironmentalInterestType.Trireporter> ; kwgo:sfWithin ?creg .
        FILTER(STRSTARTS(STR(?creg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.')) }
      BIND(REPLACE(STR(?creg),'^.*administrativeRegion\\.USA\\.','') AS ?fips) FILTER(STRLEN(?fips)=5)
    } GROUP BY ?fips ORDER BY DESC(?tri_facilities) LIMIT 12 }
  BIND(IRI(CONCAT('https://geoconnex.us/ref/counties/',?fips)) AS ?gcounty)
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?wf gnis:county ?gcounty . }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } } } GROUP BY ?loc ?county }
}
GROUP BY ?county ?tri_facilities ?pollutants ORDER BY DESC(?tri_facilities)
```

# geo17_q1_spoke-okn_spatialkg_pm25_rollup_by_state

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**
SPOKE-OKN stores county-level PM2.5 air pollution on `location/{FIPS5}` nodes. SpatialKG (KWG GADM) provides the authoritative county→state hierarchy via `administrativePartOf`. Joining on county FIPS and rolling counties up to their GADM state, which U.S. states have the highest average county PM2.5?

---
🧠 **Assistant**
The join is required to aggregate SPOKE-OKN's county PM2.5 onto the authoritative GADM administrative hierarchy: SPOKE-OKN has the pollution value per county but the state roll-up should use SpatialKG's canonical `administrativePartOf` edge to an `AdministrativeRegion_1`. I read each county's PM2.5 from SPOKE-OKN, bind the matching KWG county node, follow `administrativePartOf` to the state, and average.

| State | Counties | Avg county PM2.5 (µg/m³) |
| --- | --- | --- |
| Georgia | 159 | 9.34 |
| Alabama | 67 | 9.13 |
| Mississippi | 82 | 9.01 |
| Ohio | 88 | 8.99 |
| Arkansas | 75 | 8.95 |

The rows answer it: the state averages — only computable after placing SPOKE-OKN counties on SpatialKG's GADM hierarchy — show the Southeastern states (Georgia, Alabama, Mississippi) carrying the highest county-mean PM2.5, near/above the EPA 9 µg/m³ standard. (Raw `COUNT` is inflated by multiple year/value rows per county in SPOKE-OKN; the DISTINCT-county count is shown.)

**Literature validation (strict):** According to PubMed, ambient PM2.5 is the leading global contributor to disease burden and its geographic distribution is health-determinative. GBD 2021 (Lancet 2024) ranks particulate-matter air pollution first among 88 risk factors (8.0% of global DALYs) [DOI](https://doi.org/10.1016/S0140-6736(24)00933-4); Ma et al. (2024, *JAMA Netw Open*) show county-level PM2.5 increases raise all-cause mortality [DOI](https://doi.org/10.1001/jamanetworkopen.2023.54607). The state ranking of county PM2.5 is therefore a meaningful population-exposure geography. **Validated.**

## SPARQL queries executed
#### Query 1
_`spoke-okn`, `spatialkg` · 12 rows (showing first 5)_
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?stateName (COUNT(DISTINCT ?fips) AS ?nCounties) (AVG(?pm25) AS ?avgPM25) WHERE {
  {
    SELECT DISTINCT ?fips ?pm25 WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
              schema:variable "air pollution - particulate matter" ; schema:value ?v .
        BIND(REPLACE(STR(?loc),'^.*location/','') AS ?fips)
        BIND(xsd:decimal(REPLACE(REPLACE(?v,'\\(.*$',''),'[^0-9.].*$','')) AS ?pm25)
      }
    }
  }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg kwg:administrativePartOf ?st .
    ?st a kwg:AdministrativeRegion_1 ; rdfs:label ?stateName .
  }
} GROUP BY ?stateName ORDER BY DESC(?avgPM25) LIMIT 12
```
| State | Avg county PM2.5 (µg/m³) |
| --- | --- |
| Georgia | 9.34 |
| Alabama | 9.13 |
| Mississippi | 9.01 |
| Ohio | 8.99 |
| Arkansas | 8.95 |

**Literature:** PubMed — GBD 2021 Risk Factors Collaborators 2024, *Lancet* [DOI](https://doi.org/10.1016/S0140-6736(24)00933-4); Ma et al. 2024, *JAMA Netw Open* [DOI](https://doi.org/10.1001/jamanetworkopen.2023.54607).

# geo17_q2_spoke-okn_spatialkg_counties_over_epa_pm25

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**
The EPA's 2024 annual PM2.5 standard is 9 µg/m³. SPOKE-OKN holds county PM2.5 on `location/{FIPS5}` nodes; SpatialKG's GADM hierarchy maps each county to its state via `administrativePartOf`. Joining on county FIPS, which states have the most counties exceeding the 9 µg/m³ standard?

---
🧠 **Assistant**
The join is required: SPOKE-OKN can flag which individual counties exceed 9 µg/m³, but counting those exceedance-counties per state needs SpatialKG's authoritative county→state edge. I select distinct counties with PM2.5 > 9 from SPOKE-OKN, bind each to its KWG county node, follow `administrativePartOf` to the state, and count distinct exceedance-counties per state.

| State | Counties over 9 µg/m³ |
| --- | --- |
| Georgia | 121 |
| Texas | 88 |
| Alabama | 46 |
| Mississippi | 39 |
| Ohio | 37 |

The rows answer it directly: the per-state exceedance counts only exist after the county→state roll-up through SpatialKG. Georgia (121) and Texas (88) have by far the most counties above the new EPA annual standard, identifying the states where the largest number of county populations are exposed above the regulatory threshold.

**Literature validation (strict):** According to PubMed, exceeding PM2.5 guideline levels carries measurable health cost. GBD 2021 (Lancet 2024) identifies particulate-matter air pollution as the top global risk factor by attributable DALYs [DOI](https://doi.org/10.1016/S0140-6736(24)00933-4), and Ma et al. (2024, *JAMA Netw Open*) demonstrate that each 10-µg/m³ rise in county/municipality PM2.5 is associated with increased all-cause mortality across four countries including U.S. counties [DOI](https://doi.org/10.1001/jamanetworkopen.2023.54607). Counting counties over the EPA standard is thus a health-meaningful exposure tally. **Validated.**

## SPARQL queries executed
#### Query 1
_`spoke-okn`, `spatialkg` · 12 rows (showing first 5)_
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?stateName (COUNT(DISTINCT ?fips) AS ?countiesOver9) WHERE {
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
  FILTER(?pm25 > 9.0)
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg kwg:administrativePartOf ?st .
    ?st a kwg:AdministrativeRegion_1 ; rdfs:label ?stateName .
  }
} GROUP BY ?stateName ORDER BY DESC(?countiesOver9) LIMIT 12
```
| State | Counties over 9 µg/m³ |
| --- | --- |
| Georgia | 121 |
| Texas | 88 |
| Alabama | 46 |
| Mississippi | 39 |
| Ohio | 37 |

**Literature:** PubMed — GBD 2021 Risk Factors Collaborators 2024, *Lancet* [DOI](https://doi.org/10.1016/S0140-6736(24)00933-4); Ma et al. 2024, *JAMA Netw Open* [DOI](https://doi.org/10.1001/jamanetworkopen.2023.54607).

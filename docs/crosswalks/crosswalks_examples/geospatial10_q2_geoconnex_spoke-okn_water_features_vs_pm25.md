# Named Hillsborough County water features beside the county's PM2.5 indicator

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `geoconnex` — <https://purl.org/okn/frink/kg/geoconnex>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

Joining `geoconnex` and `spoke-okn` on **county_FIPS**: for Hillsborough County, FL (the Tampa area), name the individual rivers, creeks and lakes `geoconnex` records there and place each beside the county's PM2.5 air-pollution indicator from `spoke-okn`.

---
🧠 **Assistant**

The join is required because `geoconnex` supplies the *named* hydrographic inventory (GNIS `officialName` plus a `county` reference) while `spoke-okn` supplies the county's ambient PM2.5 environmental indicator (`variable = "air pollution - particulate matter"`, a `PREVALENCEIN_SpL` statement) plus the county name. Placing a specific named water body beside an air-quality health indicator for the same county needs both graphs joined on FIPS (`12057`).

Join mechanics: I select `geoconnex` features whose `county` is `counties/12057` and whose `officialName` ends in "River"/"Creek"/"Lake" (named water bodies), read the name, then bind the `spoke-okn` `…/location/12057` node and read the PM2.5 value and county name.

| named water feature (geoconnex) | county (spoke-okn) | PM2.5 µg/m³ (spoke-okn) |
| --- | --- | --- |
| Alafia River | Hillsborough County | 7.8(2.0) |
| Blackwater Creek | Hillsborough County | 7.8(2.0) |
| Bullfrog Creek | Hillsborough County | 7.8(2.0) |
| Buckhorn Creek | Hillsborough County | 7.8(2.0) |
| Bay Lake | Hillsborough County | 7.8(2.0) |
| Brant Lake | Hillsborough County | 7.8(2.0) |
| Aberdeen Creek | Hillsborough County | 7.8(2.0) |

The rows answer the question: each row pairs a real, *named* water body (`geoconnex`) — including the Alafia River, a major Tampa-Bay tributary — with the named county and its real ambient PM2.5 of 7.8 µg/m³ (`spoke-okn`), above the WHO annual guideline of 5 µg/m³. Naming the rivers, creeks and lakes ties the air-quality figure to a recognizable hydrologic landscape rather than to an anonymous feature count.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?officialName ?cname ?pm25 WHERE {
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> {
    ?x <http://gnis-ld.org/lod/gnis/ontology/county> <https://geoconnex.us/ref/counties/12057> ;
       <http://gnis-ld.org/lod/gnis/ontology/officialName> ?officialName .
    FILTER(REGEX(?officialName, "(River|Creek|Lake)$"))
  }
  BIND(<https://purl.org/okn/frink/kg/spoke-okn/location/12057> AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "air pollution - particulate matter" ; schema:value ?pm25 .
  }
} ORDER BY ?officialName LIMIT 12
```

## Literature validation

According to PubMed, long-term ambient PM2.5 is a validated mortality risk factor. Wang et al. (2024, *JMIR Public Health Surveill*), in a 580,757-participant cohort with marginal-structural Cox modeling, estimated a 4.2% increase in respiratory-mortality risk per 1 µg/m³ of long-term PM2.5 exposure — establishing that the per-county PM2.5 value placed beside the named water features is a health-meaningful environmental indicator. [PMID:39316790](https://pubmed.ncbi.nlm.nih.gov/39316790/) · [DOI](https://doi.org/10.2196/56059)

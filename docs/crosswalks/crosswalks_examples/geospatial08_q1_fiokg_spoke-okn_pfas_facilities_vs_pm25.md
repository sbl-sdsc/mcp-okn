# Named EPA PFAS air-major facilities in Harris County beside the county's PM2.5

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

Using the **county_FIPS** crosswalk between `fiokg` and `spoke-okn`: for Harris County, TX (a high PFAS-facility burden county), name the individual EPA PFAS-relevant facilities that hold an **"Air major"** environmental-interest registration, and place each beside the county's fine-particulate-matter (PM2.5) air-pollution indicator.

---
🧠 **Assistant**

The join is required because the two facts live in different graphs. `fiokg` carries the EPA Facility Registry Service records — each PFAS-relevant facility's **name**, its `hasEnvironmentalInterest` program type, and its county location (`sfWithin` a KWG `administrativeRegion.USA.{FIPS5}`) — but no ambient air measurement. `spoke-okn` carries the county-level PM2.5 indicator (an SDoH `PREVALENCEIN_SpL` statement with `variable = "air pollution - particulate matter"`) and the county's `rdfs:label`, but knows nothing about EPA facilities. Only by joining on county FIPS (`48201`) can we set each *named* air-emitting facility next to the ambient PM2.5 its community breathes.

Join mechanics: I restrict `fiokg` to `EPA-PFAS-Facility` nodes that `sfWithin` `administrativeRegion.USA.48201` and carry the `EnvironmentalInterestType.Airmajor` interest (the Clean-Air-Act "major source" class most relevant to PM2.5), read their `rdfs:label`, then bind the `spoke-okn` `…/location/48201` node and read the PM2.5 value and county name.

| EPA PFAS facility (fiokg, "Air major") | county (spoke-okn) | PM2.5 µg/m³ (spoke-okn) |
| --- | --- | --- |
| AFTON CHEMICAL CORPORATION | Harris County | 10.7(4.0) |
| AGRIFOS FERTILIZER L.L.C. | Harris County | 10.7(4.0) |
| AIR LIQUIDE LARGE INDUSTRIES USLP | Harris County | 10.7(4.0) |
| AIR PRODUCTS BAYTOWN II PLANT | Harris County | 10.7(4.0) |
| AKZO NOBEL SURFACE CHEMISTRY LLC HOUSTON PLANT | Harris County | 10.7(4.0) |
| 69TH ST WASTEWATER TREATMENT PLANT | Harris County | 10.7(4.0) |

The rows answer the question: each row pairs a real, *named* Clean-Air-Act major-source PFAS facility (`fiokg`) with the named county and its real ambient PM2.5 value (`spoke-okn`). Harris County's industrial Ship-Channel corridor — Afton Chemical, Agrifos Fertilizer, the Air Liquide and Air Products gas/chemical plants, Akzo Nobel's Houston surface-chemistry plant — sits beside a county-wide PM2.5 of 10.7 µg/m³, above the WHO annual guideline of 5 µg/m³. Naming the emitters rather than counting them lets the burden be traced to specific Clean-Air-Act major sources.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?facName ?cname ?pm25 WHERE {
  BIND("48201" AS ?fips)
  BIND(<http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.48201> AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a <http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility> ;
         <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?reg ;
         rdfs:label ?facName ;
         <http://w3id.org/fio/v1/epa-frs#hasEnvironmentalInterest>
           <http://w3id.org/fio/v1/epa-frs-data#d.EnvironmentalInterestType.Airmajor> .
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "air pollution - particulate matter" ; schema:value ?pm25 .
  }
} ORDER BY ?facName LIMIT 12
```

## Literature validation

According to PubMed, source-apportionment work shows that ambient PM2.5 in heavily industrialized areas is driven in substantial part by named industrial source categories — ferrous-metal smelting, oil combustion, and other industry — which also dominate the carcinogenic/non-carcinogenic health risk of PM2.5-bound elements. Li et al. (2021, *Sci Total Environ*) apportioned PM2.5 to coal combustion, traffic, ferrous-metal smelting, oil combustion and other industrial sources and found industrial sources carried the highest element-bound health risk, validating that pairing named industrial air-major facilities with a county's PM2.5 burden is health-meaningful. [PMID:34844311](https://pubmed.ncbi.nlm.nih.gov/34844311/) · [DOI](https://doi.org/10.1016/j.scitotenv.2021.150440)

# Sampled officer-involved shooting incidents (nikg) beside Philadelphia's firearm-fatalities indicator

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `nikg` — <https://purl.org/okn/frink/kg/nikg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

Joining `nikg` and `spoke-okn` on **county_FIPS**: for Philadelphia County, list individual **officer-involved** shooting incidents with their date, street block, and offender-outcome flag (`nikg`), and place each beside the county's firearm-fatalities SDoH indicator (`spoke-okn`).

---
🧠 **Assistant**

The join is required because `nikg` holds the incident-level officer-involved records — each flagged `OfficerInvolved = true`, with a `date_of`, a named street-block location (`LOC_…BLOCK_OF_…`), an `OffenderDeceased` flag, and a census-tract location that `sfWithin` a KWG `administrativeRegion.USA.{FIPS5}` — while `spoke-okn` holds the county-level "firearm fatalities" SDoH indicator and the county name. Joining on county FIPS (`42101`) puts each *named-block, dated* officer-involved incident beside the county firearm-death context. Reporting incident-level rows (date + block + offender flag) rather than a single count gives each row a real nikg datum.

Join mechanics: each `nikg` incident has two `schema.org/location` values — a census tract (`CT_…`, used for the FIPS join via `sfWithin`) and a named street block (`LOC_…`, surfaced as the row's location attribute). I filter to `OfficerInvolved = true`, read `date_of` and `OffenderDeceased`, bind the `spoke-okn` `…/location/42101` node and read the "firearm fatalities" value and county name.

| date (nikg) | street block (nikg) | offender deceased (nikg) | county (spoke-okn) | firearm-fatalities indicator (spoke-okn) |
| --- | --- | --- | --- | --- |
| 2023-09-14 | 3100 BLOCK OF EMERALD ST | false | Philadelphia County | 0.023925250879 |
| 2023-08-14 | 100 BLOCK OF E WILLARD ST | true | Philadelphia County | 0.023925250879 |
| 2023-05-04 | 2300 BLOCK OF FAWN ST | true | Philadelphia County | 0.023925250879 |
| 2023-04-29 | 400 BLOCK OF W BRINGHURST ST | false | Philadelphia County | 0.023925250879 |
| 2023-03-24 | 1500 BLOCK OF E JOHNSON ST | false | Philadelphia County | 0.023925250879 |
| 2023-02-08 | 200 BLOCK OF N 60TH ST | false | Philadelphia County | 0.023925250879 |

The rows answer the question: each row carries a real, *incident-level* nikg datum — the officer-involved shooting's date, named street block, and offender-deceased flag — beside the named county and its real firearm-fatalities SDoH indicator (`spoke-okn`, 0.0239). The sampled incidents are concrete, dated, located events rather than an anonymous count, and they sit against the county's firearm-death context that only the cross-graph join can supply.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cname ?date ?block ?offender_deceased ?firearm_indicator WHERE {
  GRAPH <https://purl.org/okn/frink/kg/nikg> {
    ?tract <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?o .
    FILTER(STRSTARTS(STR(?o),'https://metadata.phila.gov/kwgr_administrativeRegion_USA_42101'))
    ?rec ?lp ?tract . FILTER(STRENDS(STR(?lp),'schema.org/location'))
    ?rec <https://metadata.phila.gov/OfficerInvolved> true ;
         <https://metadata.phila.gov/date_of> ?date ;
         <https://metadata.phila.gov/OffenderDeceased> ?offender_deceased ;
         ?lp2 ?locblock .
    FILTER(STRENDS(STR(?lp2),'schema.org/location'))
    FILTER(STRSTARTS(STR(?locblock),'https://metadata.phila.gov/LOC_'))
    BIND(REPLACE(REPLACE(STR(?locblock),'^.*/LOC_',''),'_',' ') AS ?block)
  }
  BIND(<https://purl.org/okn/frink/kg/spoke-okn/location/42101> AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "firearm fatalities" ; schema:value ?firearm_indicator .
  }
} ORDER BY DESC(?date) LIMIT 10
```

## Literature validation

According to PubMed, officer-involved / police killings have documented population-level health consequences. Bor et al. (2018, *The Lancet*) showed in a population-based quasi-experiment that each additional police killing of an unarmed Black American was associated with measurably worse mental-health days among Black Americans in the same state — establishing officer-involved fatal shootings as a community-health exposure with spillover effects, which validates pairing the incident-level officer-involved records with the county firearm-fatalities SDoH indicator. [PMID:29937193](https://pubmed.ncbi.nlm.nih.gov/29937193/) · [DOI](https://doi.org/10.1016/S0140-6736(18)31130-9)

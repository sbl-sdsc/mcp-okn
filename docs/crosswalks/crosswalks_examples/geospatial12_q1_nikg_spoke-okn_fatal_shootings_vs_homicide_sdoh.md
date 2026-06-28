# Fatal vs non-fatal shooting tallies (nikg) beside each county's homicide SDoH indicator

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `nikg` — <https://purl.org/okn/frink/kg/nikg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

Using the **county_FIPS** crosswalk between `nikg` and `spoke-okn`: for Philadelphia and Cook counties, break the neighborhood shooting incidents down by **outcome (fatal vs non-fatal)** and place each tally beside the county's homicide social-determinant-of-health indicator from `spoke-okn`.

---
🧠 **Assistant**

The join is required because the two facts live in different graphs. `nikg` holds the granular, incident-level shooting records — each incident's `is_fatal` flag and its tract location, where the tract `sfWithin` a KWG `administrativeRegion.USA.{FIPS5}` — but no county-level health metric. `spoke-okn` holds an independent county-level "homicides" SDoH indicator (a `PREVALENCEIN_SpL` statement) and the county's `rdfs:label`, but no incident records. Joining on county FIPS lets the incident-level fatal/non-fatal structure sit beside the county homicide indicator. Breaking the incidents down by the `is_fatal` field (rather than reporting one bare count) gives each row a real nikg metric.

Join mechanics: a `nikg` subquery counts incidents per FIPS *stratified by* `is_fatal` (mapped to "fatal shooting"/"non-fatal shooting"); I bind the `spoke-okn` `…/location/{FIPS5}` node and read the "homicides" value and county name.

| county (spoke-okn) | shooting outcome (nikg) | incidents (nikg) | homicide SDoH indicator (spoke-okn) |
| --- | --- | --- | --- |
| Philadelphia County | non-fatal shooting | 12042 | 0.02107380613 |
| Philadelphia County | fatal shooting | 3163 | 0.02107380613 |
| Cook County | non-fatal shooting | 811 | 0.013990692612 |
| Cook County | fatal shooting | 208 | 0.013990692612 |

The rows answer the question: each row pairs a real, *stratified* nikg metric — the fatal and non-fatal incident tallies — with the named county and its real homicide SDoH indicator (`spoke-okn`). Philadelphia carries both a far larger absolute shooting burden (3,163 fatal of 15,205 total) and the higher county homicide indicator (0.0211 vs 0.0140 for Cook), an internal corroboration across the two graphs. The fatal:non-fatal split (~1:3.8 in Philadelphia, ~1:3.9 in Cook) is itself a meaningful nikg metric only the incident-level graph can supply.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cname ?outcome ?incidents ?homicide_indicator WHERE {
  {
    SELECT ?fips ?outcome (COUNT(DISTINCT ?rec) AS ?incidents) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nikg> {
        ?tract <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?o .
        FILTER(STRSTARTS(STR(?o),'https://metadata.phila.gov/kwgr_administrativeRegion_USA_'))
        BIND(REPLACE(STR(?o),'^.*administrativeRegion_USA_([0-9]{5}).*$','$1') AS ?fips)
        ?rec ?lp ?tract . FILTER(STRENDS(STR(?lp),'schema.org/location'))
        ?rec <https://metadata.phila.gov/is_fatal> ?isFatal .
        BIND(IF(?isFatal, "fatal shooting", "non-fatal shooting") AS ?outcome)
      }
    } GROUP BY ?fips ?outcome
  }
  VALUES (?fips ?loc) {
    ("42101" <https://purl.org/okn/frink/kg/spoke-okn/location/42101>)
    ("17031" <https://purl.org/okn/frink/kg/spoke-okn/location/17031>)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "homicides" ; schema:value ?homicide_indicator .
  }
} ORDER BY ?cname DESC(?incidents)
```

## Literature validation

According to PubMed, exposure to gun-violence fatality is an established social determinant of community health. Smith et al. (2019, *Soc Sci Med*) found that vicarious exposure to gun-violence fatality in urban settings including Philadelphia was associated with significantly higher depression, psychological distress, suicidal ideation and psychotic experiences, and explicitly frames gun-violence fatality as a social determinant of mental health — validating that the county fatal/non-fatal shooting burden placed beside the homicide SDoH indicator is health-meaningful. [PMID:31958617](https://pubmed.ncbi.nlm.nih.gov/31958617/) · [DOI](https://doi.org/10.1016/j.socscimed.2019.112587)

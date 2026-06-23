# geo10_q2_geoconnex_spoke-okn_water_features_vs_pm25

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `geoconnex` — <https://purl.org/okn/frink/kg/geoconnex>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**
Joining `geoconnex` and `spoke-okn` on **county_FIPS**: for the counties richest in named water features, report the feature count alongside the county's PM2.5 air-pollution indicator from `spoke-okn`.

---
🧠 **Assistant**
The join is required because `geoconnex` supplies the hydrographic-feature inventory per FIPS and `spoke-okn` supplies the county's ambient PM2.5 environmental indicator plus its name. Placing water-resource density next to an air-quality health indicator for the same named county needs both graphs.

Join mechanics: a `geoconnex` subquery counts features per county; I bind the `spoke-okn` `…/location/{FIPS5}` node and read the "air pollution - particulate matter" value and label.

| county | water features | PM2.5 |
| --- | --- | --- |
| Coconino County | 5750 | 4.8(2.0) |
| Hillsborough County | 4071 | 7.8(2.0) |
| Yavapai County | 3724 | 4.8(2.0) |
| Idaho County | 3247 | 6.7(3.0) |
| Gila County | 2876 | 4.6(2.0) |

The rows answer the question: feature inventory (`geoconnex`) next to the named county's PM2.5 (`spoke-okn`). The mostly rural, water-feature-rich western counties show relatively low PM2.5 — a meaningful environmental contrast surfaced only by the cross-graph join.

**Literature validation (strict):** According to PubMed, county-level ambient PM2.5 is an established mortality risk factor: Wang et al. (2016, *Environ Health Perspect*) found a causal ~3% all-cause mortality increase per 2 µg/m³ of long-term PM2.5, with effect modification by socioeconomic context [DOI](https://doi.org/10.1289/ehp.1409671). This validates that the per-county PM2.5 values placed beside the water-feature inventory are a health-meaningful environmental indicator. The feature count is an administrative rollup; the PM2.5 indicator's health relevance is corroborated. **Validated (PM2.5 indicator); feature count is administrative rollup.**

## SPARQL queries executed
#### Query 1
_`geoconnex`, `spoke-okn` · 6 rows (showing first 5)_
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cname ?water_features ?pm25 WHERE {
  {
    SELECT ?fips (COUNT(DISTINCT ?x) AS ?water_features) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/geoconnex> {
        ?x <http://gnis-ld.org/lod/gnis/ontology/county> ?county .
        FILTER(STRSTARTS(STR(?county),'https://geoconnex.us/ref/counties/'))
        BIND(REPLACE(STR(?county),'^.*/counties/([0-9]{5}).*$','$1') AS ?fips)
      }
    } GROUP BY ?fips
  }
  VALUES ?fips { "04005" "12057" "04025" "16049" "04007" "41045" }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "air pollution - particulate matter" ; schema:value ?pm25 .
  }
} ORDER BY DESC(?water_features)
```
| county | water features | PM2.5 |
| --- | --- | --- |
| Coconino County | 5750 | 4.8(2.0) |
| Hillsborough County | 4071 | 7.8(2.0) |
| Yavapai County | 3724 | 4.8(2.0) |
| Idaho County | 3247 | 6.7(3.0) |
| Gila County | 2876 | 4.6(2.0) |

**Literature:** PubMed — Wang Y et al. 2016, *Environ Health Perspect* [DOI](https://doi.org/10.1289/ehp.1409671).

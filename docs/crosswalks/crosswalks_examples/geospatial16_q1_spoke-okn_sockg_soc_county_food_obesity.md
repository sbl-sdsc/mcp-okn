# Food insecurity & obesity in named soil-carbon experiment counties (sockg × spoke-okn)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `sockg` — <https://purl.org/okn/frink/kg/sockg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

SOCKG (Soil Organic Carbon KG) records named long-term soil-organic-carbon / agricultural field-experiment **sites** (`sockg:Site` individuals with a `dcterms:identifier`, e.g. "ALAuburn") each `spatial:connectedTo` a KWG county node whose FIPS is embedded in the IRI. SPOKE-OKN holds county food-insecurity and adult-obesity prevalence. Joining on county FIPS: what is the food-environment and obesity profile of the agricultural counties that host these named soil-carbon experiment sites?

---
🧠 **Assistant**

The join is required to move from SOCKG's purely agronomic geography (which *named* experiment sites sit in which county) to the human-health context of those same counties, which only SPOKE-OKN carries. I pull each SOCKG `Site` with its identifier, follow `spatial:connectedTo` to the KWG county, extract the FIPS, bind the SPOKE-OKN county node, and read food-insecurity and adult-obesity prevalence.

**Why the join is required:** each row carries a real SOCKG datum (the named experiment site(s) hosted in that county) and real SPOKE-OKN data (county food insecurity % and adult obesity %) for the *same* FIPS — neither KG yields the pairing alone.

| FIPS | County | SOCKG experiment site(s) | Food insecurity % | Adult obesity % |
| --- | --- | --- | --- | --- |
| 01087 | Macon Co AL | ALAuburn, ALAUEVS, ALAUSoil | 16.4 | 47.3 |
| 01067 | Henry Co AL | ALAURye | 13.7 | 42.1 |
| 45041 | Florence Co SC | SCFLSGI | 10.1 | 41.5 |
| 27127 | Redwood Co MN | Lamb | 7.2 | 40.4 |
| 48227 | Howard Co TX | TXBSWEWC | 16.1 | 39.0 |
| 18157 | Tippecanoe Co IN | INACRE, INTPAC, INWQFS, INWLREAP | 12.5 | 37.3 |
| 21227 | Warren Co KY | GHG | 12.9 | 37.2 |
| 38059 | Morton Co ND | NDMABCS, NDMASQMF, NDMAGWP, NDH3 | 4.0 | 35.8 |

**Why it answers the question:** the counties hosting SOCKG soil-carbon experiments are agricultural/rural counties with frequently severe human food-environment burdens — adult obesity up to 47.3% at the ALAuburn site county (Macon Co AL) and food insecurity of 13–16% in several (Macon, Howard, Henry) — alongside lower-burden plains counties such as Morton Co ND (4.0% food insecurity). Naming the SOCKG site (sockg) next to the obesity/food-insecurity value (spoke-okn) puts the agronomy and the public-health backdrop in one frame.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX sockg: <https://idir.uta.edu/sockg-ontology#>
PREFIX spatial: <http://purl.org/spatialai/spatial/spatial-full#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips ?cname (GROUP_CONCAT(DISTINCT ?siteId; separator=", ") AS ?sites) ?foodInsec ?obesity WHERE {
  {
    SELECT DISTINCT ?fips ?siteId WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?site a sockg:Site ; dct:identifier ?siteId ; spatial:connectedTo ?reg .
        FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
        BIND(REPLACE(STR(?reg),'^.*USA\\.','') AS ?fips)
        FILTER(STRLEN(?fips)=5)
      }
    }
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?s1 rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "food insecurity" ; schema:value ?fi .
    BIND(xsd:decimal(REPLACE(?fi,'\\(.*$','')) AS ?foodInsec)
    ?s2 rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "adult obesity" ; schema:value ?ob .
    BIND(xsd:decimal(REPLACE(?ob,'\\(.*$','')) AS ?obesity)
  }
} GROUP BY ?fips ?cname ?foodInsec ?obesity ORDER BY DESC(?obesity) LIMIT 12
```

## Literature validation

According to PubMed, rural high-obesity agricultural counties have measurably degraded food environments. Canales et al. (2021, *Prev Chronic Dis*) assessed retail food outlets in the predominantly rural, high-obesity Mississippi Delta and found that healthy-food availability at the dominant convenience-store format was 70% lower than at supermarkets, with fruit/vegetable prices 35% higher — the food-environment mechanism linking the agricultural-county setting to the elevated obesity and food-insecurity values surfaced here. [PMID:34856116](https://pubmed.ncbi.nlm.nih.gov/34856116/) · [DOI](https://doi.org/10.5888/pcd18.210173)

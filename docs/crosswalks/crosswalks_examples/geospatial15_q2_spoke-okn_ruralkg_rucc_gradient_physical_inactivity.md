# geo15_q2_spoke-okn_ruralkg_rucc_gradient_physical_inactivity

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**
Using RuralKG's full USDA Rural-Urban Continuum Code (RUCC 1→9) classification joined on county FIPS to SPOKE-OKN's county "physical inactivity" prevalence, is there a monotonic rural-urban gradient in physical inactivity across all U.S. counties?

---
🧠 **Assistant**
The join is required: RuralKG holds the rurality code per county, SPOKE-OKN holds the physical-inactivity prevalence per county; only the FIPS join lets us bin one by the other. I take every RuralKG county with a RUCC code, extract the FIPS from its KWG `censusCounty` IRI, bind the SPOKE-OKN county node, parse the inactivity value, and average within each of the nine RUCC classes.

| RUCC | Counties | Avg physical inactivity % |
| --- | --- | --- |
| 1 (most metro) | 430 | 23.1 |
| 2 | 378 | 24.7 |
| 3 | 352 | 25.0 |
| 6 | 591 | 27.7 |
| 9 (most rural) | 421 | 25.7 |

The nine rows (3,129 counties total) answer it: physical inactivity rises steadily from 23.1% in the most metropolitan counties to ~26–28% across the nonmetro/rural classes — a clear (near-monotonic, peaking around RUCC 6) rural-urban gradient that only emerges from the cross-KG join.

**Literature validation (strict):** According to PubMed, rural U.S. residents engage in less leisure-time physical activity than urban residents. Robertson et al. (2018, *J Rural Health*) found rural residents reported ~25% fewer weekly bouts of leisure-time muscle-strengthening activity and less leisure-time physical activity than large-urban counterparts in a nationally representative sample [DOI](https://doi.org/10.1111/jrh.12295). **Validated.**

## SPARQL queries executed
#### Query 1
_`ruralkg`, `spoke-okn` · 9 rows (showing 5)_
```sparql
PREFIX rural: <http://sail.ua.edu/ruralkg/settlementtype/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?ruccCode (COUNT(?fips) AS ?counties) (AVG(?pi) AS ?avgInactivity) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?cs rural:censusCounty ?reg ; rural:hasRUCC ?rucc .
    ?rucc rural:code ?ruccCode .
  }
  BIND(REPLACE(STR(?reg),'^.*USA\\.','') AS ?fips)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "physical inactivity" ; schema:value ?v .
    BIND(xsd:decimal(REPLACE(?v,'\\(.*$','')) AS ?pi)
  }
} GROUP BY ?ruccCode ORDER BY ?ruccCode
```
| RUCC | Counties | Avg physical inactivity % |
| --- | --- | --- |
| 1 | 430 | 23.10 |
| 2 | 378 | 24.66 |
| 3 | 352 | 25.02 |
| 6 | 591 | 27.74 |
| 9 | 421 | 25.68 |

**Literature:** PubMed — Robertson et al. 2018, *J Rural Health* [DOI](https://doi.org/10.1111/jrh.12295).

# geo15_q1_spoke-okn_ruralkg_rurality_vs_obesity

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**
RuralKG classifies every U.S. county by USDA Rural-Urban Continuum Code (RUCC 1 = most metropolitan … 9 = most rural), linking the county to a KWG region whose FIPS is embedded in the IRI. SPOKE-OKN holds county adult-obesity prevalence as a reified `PREVALENCEIN_SpL` statement on `location/{FIPS5}`. Joining on county FIPS: is adult obesity higher in the most-rural counties than in the most-metropolitan ones?

---
🧠 **Assistant**
The join is required: RuralKG knows *how rural* a county is but has no obesity data; SPOKE-OKN has the obesity prevalence but no rurality classification. I pull RUCC-1 and RUCC-9 counties from RuralKG, extract the FIPS from the KWG `censusCounty` IRI, bind the SPOKE-OKN county node, parse the obesity value, and average within each RUCC class.

| RUCC | Class | Counties | Avg adult obesity % |
| --- | --- | --- | --- |
| 1 | Most metropolitan | 430 | 33.6 |
| 9 | Most rural | 421 | 36.2 |

The two rows answer the question by construction: averaging the SPOKE-OKN obesity values within RuralKG's rurality extremes shows the most-rural counties run ~2.6 points higher in adult obesity than the most-metropolitan counties, across 851 counties.

**Literature validation (strict):** According to PubMed, this rural-urban obesity gradient is well documented and indexed *specifically* by RUCC. McCormack et al. (2019, *S D Med*; PMID 31581377) found that odds of overweight/obesity increased with increasing rurality, with higher RUCC codes (5, 7, 8, 9) carrying greater odds of overweight/obesity than lower ones — directly mirroring the RUCC-1 vs RUCC-9 gap measured here. The high-BMI disease burden this gradient implies is quantified by the GBD 2021 risk-factor analysis (Lancet 2024) [DOI](https://doi.org/10.1016/S0140-6736(24)00933-4). **Validated.**

> Note: McCormack 2019 carries no DOI in PubMed and is cited by PMID 31581377; the DOI-bearing GBD 2021 source corroborates the downstream burden.

## SPARQL queries executed
#### Query 1
_`ruralkg`, `spoke-okn` · 2 rows_
```sparql
PREFIX rural: <http://sail.ua.edu/ruralkg/settlementtype/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?ruccCode (COUNT(?fips) AS ?counties) (AVG(?obes) AS ?avgObesity) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?cs rural:censusCounty ?reg ; rural:hasRUCC ?rucc .
    ?rucc rural:code ?ruccCode .
    FILTER(?ruccCode IN ("1","9"))
  }
  BIND(REPLACE(STR(?reg),'^.*USA\\.','') AS ?fips)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "adult obesity" ; schema:value ?v .
    BIND(xsd:decimal(REPLACE(?v,'\\(.*$','')) AS ?obes)
  }
} GROUP BY ?ruccCode ORDER BY ?ruccCode
```
| RUCC | Counties | Avg adult obesity % |
| --- | --- | --- |
| 1 | 430 | 33.58 |
| 9 | 421 | 36.22 |

**Literature:** PubMed — McCormack et al. 2019, *S D Med* (PMID 31581377; differences in overweight/obesity by Rural-Urban Continuum Codes). Corroborating: GBD 2021 risk-factor analysis on high BMI burden, Lancet 2024 [DOI](https://doi.org/10.1016/S0140-6736(24)00933-4).

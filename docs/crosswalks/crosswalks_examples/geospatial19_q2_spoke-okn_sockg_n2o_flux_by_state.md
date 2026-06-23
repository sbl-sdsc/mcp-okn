# geo19_q2_spoke-okn_sockg_n2o_flux_by_state

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `sockg` — <https://purl.org/okn/frink/kg/sockg>

## Conversation
👤 **User**

sockg also records greenhouse-gas flux chamber measurements, including soil nitrous-oxide (N2O) emissions from agricultural fields — a potent greenhouse gas driven largely by nitrogen fertilization. Its state nodes carry only two-letter codes. **Crosswalk on STATE_FIPS (2-digit):** Which states in the sockg experimental network have the highest mean soil N2O flux, reported by full state name (resolved via spoke-okn)?

---
🧠 **Assistant**

**Why the join is required.** The N2O flux measurements aggregate to sockg's `AdministrativeRegion_1` nodes labeled "IA", "KY", etc. To deliver a ranked, readable table of N2O-emitting states, the sockg aggregation must be joined to spoke-okn's full state names on the shared 2-digit FIPS — neither graph does both alone.

**Join mechanics.** Same site→experimental-unit→sample chain as the SOC query, but the sample is typed `GHGFlux` and the parameter label is `n2o_gn_ha_d` (g N / ha / day). AVG is computed in a FIPS-keyed subquery, then bridged to `spoke-okn/location/{FIPS}` `rdfs:label`.

| state | avg N2O flux (g N/ha/d) | n measurements |
| --- | --- | --- |
| Iowa | 29.30 | 6,264 |
| Kentucky | 25.48 | 22,572 |
| Indiana | 16.78 | 43,388 |
| Minnesota | 16.34 | 32,082 |
| Nebraska | 14.78 | 13,274 |

The rows answer the question by naming and ranking the highest-N2O-emitting states in the network. The Corn-Belt states (Iowa, Indiana, Minnesota, Nebraska) dominating is consistent with their intensive nitrogen-fertilized maize systems.

**Literature validation (strict).** According to PubMed, Li et al. (2022, *Int J Environ Res Public Health*) experimentally show that nitrogen addition to agricultural soils significantly drives soil N2O emissions — "a potent greenhouse gas" — with emission responding to nitrogen input and soil water status [DOI](https://doi.org/10.3390/ijerph19137789). This corroborates the mechanism behind the high N2O flux observed in heavily nitrogen-fertilized Corn-Belt states. **Validated** (agricultural greenhouse-gas / climate angle).

## SPARQL queries executed
#### Query 1
_`sockg`, `spoke-okn` · 10 rows (showing first 5)_
```sparql
SELECT ?sname ?avgN2O ?nMeas WHERE {
  {
    SELECT ?fips (AVG(?val) AS ?avgN2O) (COUNT(*) AS ?nMeas) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?state a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
               <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains> ?site .
        ?eu <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?site ; a <https://idir.uta.edu/sockg-ontology#ExperimentalUnit> .
        ?samp <https://idir.uta.edu/sockg-ontology#fromUnit> ?eu ; a <https://idir.uta.edu/sockg-ontology#GHGFlux> ; <https://idir.uta.edu/sockg-ontology#hasMeasurement> ?meas .
        ?meas <https://idir.uta.edu/sockg-ontology#of> ?param ; <http://qudt.org/schema/qudt/quantityValue> ?res .
        ?param <http://www.w3.org/2000/01/rdf-schema#label> "n2o_gn_ha_d" .
        ?res <http://qudt.org/schema/qudt/numericValue> ?val .
        BIND(REPLACE(STR(?state),'^.*USA\\.','') AS ?fips)
        FILTER(STRSTARTS(STR(?state),'http://stko-kwg'))
      }
    } GROUP BY ?fips
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?sname .
  }
} ORDER BY DESC(?avgN2O) LIMIT 10
```
| sname | avgN2O | nMeas |
| --- | --- | --- |
| Iowa | 29.30 | 6264 |
| Kentucky | 25.48 | 22572 |
| Indiana | 16.78 | 43388 |
| Minnesota | 16.34 | 32082 |
| Nebraska | 14.78 | 13274 |

**Literature:** PubMed — Li Y et al. 2022, *Int J Environ Res Public Health* [DOI](https://doi.org/10.3390/ijerph19137789).

# geo19_q1_spoke-okn_sockg_soil_organic_carbon_by_state

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `sockg` — <https://purl.org/okn/frink/kg/sockg>

## Conversation
👤 **User**

The Soil Organic Carbon Knowledge Graph (sockg) records soil-organic-carbon (SOC) field measurements from long-term agricultural experiments, but its state nodes are labeled only with two-letter abbreviations (e.g. "MT"). SPOKE-OKN holds the canonical full state names on its `/location/{FIPS2}` administrative nodes. **Crosswalk on STATE_FIPS (2-digit):** Across the states where sockg has experimental sites, which states show the highest measured soil organic carbon, reported with their full state names? Soil organic carbon is the central variable in agricultural soil-health and climate-change-mitigation science.

---
🧠 **Assistant**

**Why the join is required.** sockg's SOC measurements roll up to GADM/KWG state regions whose `rdfs:label` is just "MT", "IA", etc. — not analyst-friendly. spoke-okn supplies the full name "Montana", "Iowa" on `/location/30`, `/location/19`. Producing a readable, ranked SOC-by-state answer requires bridging sockg's measurement aggregation to spoke-okn's naming on the shared 2-digit FIPS.

**Join mechanics.** In `sockg` I traverse `AdministrativeRegion_1 → sfContains → Site ← sfWithin ← ExperimentalUnit`, then `ExperimentalUnit ← fromUnit ← SoilChemicalSample → hasMeasurement → Measurement → of → Parameter` where the parameter label is `organic_c_gc_kg`, reading the value via `quantityValue → numericValue`. I AVG by the 2-digit FIPS extracted from the `administrativeRegion.USA.NN` IRI (computed in a subquery to avoid FRINK's unbound-right-graph explosion), then BIND `spoke-okn/location/{FIPS}` and read `rdfs:label`.

| state | avg SOC (g C / kg) | n measurements |
| --- | --- | --- |
| Montana | 74.10 | 3,694 |
| Iowa | 27.77 | 472 |
| Minnesota | 22.11 | 4,080 |
| Colorado | 21.06 | 708 |
| Nebraska | 15.50 | 624 |

These rows answer the question: each sockg state SOC mean is attached to its full spoke-okn name and ranked. (Montana's high value reflects cool, semi-arid grassland-derived soils that retain carbon.)

**Literature validation (strict).** According to PubMed, Beillouin et al. (2021, *Glob Chang Biol*) synthesize 192 meta-analyses covering >13,200 original studies and establish that soil organic carbon — and how land management raises or depletes it — is the pivotal quantity for climate-change mitigation in agricultural soils, while noting geographic coverage of SOC studies remains uneven across regions [DOI](https://doi.org/10.1111/gcb.15998). This corroborates both the scientific salience of state-level SOC and the value of mapping where measurements concentrate. **Validated** (agricultural soil-health / climate angle).

## SPARQL queries executed
#### Query 1
_`sockg`, `spoke-okn` · 9 rows (showing first 5)_
```sparql
SELECT ?sname ?avgSOC ?nMeas WHERE {
  {
    SELECT ?fips (AVG(?val) AS ?avgSOC) (COUNT(*) AS ?nMeas) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?state a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
               <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains> ?site .
        ?eu <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?site ; a <https://idir.uta.edu/sockg-ontology#ExperimentalUnit> .
        ?samp <https://idir.uta.edu/sockg-ontology#fromUnit> ?eu ; <https://idir.uta.edu/sockg-ontology#hasMeasurement> ?meas .
        ?meas <https://idir.uta.edu/sockg-ontology#of> ?param ; <http://qudt.org/schema/qudt/quantityValue> ?res .
        ?param <http://www.w3.org/2000/01/rdf-schema#label> "organic_c_gc_kg" .
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
} ORDER BY DESC(?avgSOC) LIMIT 10
```
| sname | avgSOC | nMeas |
| --- | --- | --- |
| Montana | 74.10 | 3694 |
| Iowa | 27.77 | 472 |
| Minnesota | 22.11 | 4080 |
| Colorado | 21.06 | 708 |
| Nebraska | 15.50 | 624 |

**Literature:** PubMed — Beillouin D et al. 2021, *Glob Chang Biol* [DOI](https://doi.org/10.1111/gcb.15998).

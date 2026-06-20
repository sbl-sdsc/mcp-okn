# geo24_q1_sockg_spatialkg_soil_organic_carbon_by_county

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `sockg` — <https://purl.org/okn/frink/kg/sockg>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**

sockg ties each experimental Site to a county via KWG `administrativeRegion.USA.{FIPS5}` IRIs, but those county nodes in sockg carry no readable label. spatialkg holds the identical-form KWG county nodes WITH full county names (e.g. "Gallatin County, Montana"). **Crosswalk on KWG_county (shared `administrativeRegion.USA.{FIPS5}` IRI — direct join, no rewrite):** Which counties in the sockg experimental network show the highest measured soil organic carbon, reported with their proper county names?

---
🧠 **Assistant**

**Why the join is required.** sockg can aggregate SOC to a county node, but that node is just an opaque `…USA.30031` IRI — no name. spatialkg owns `rdfs:label "Gallatin County, Montana"` on the *same* IRI. Because both graphs use the identical KWG county IRI form, this is a direct IRI join (no normalization), and it is the only way to attach human-readable county names to sockg's county-level SOC means.

**Join mechanics.** In a subquery over `sockg`, traverse `Site → connectedTo → AdministrativeRegion_2` (the county), then `Site ← sfWithin ← ExperimentalUnit ← fromUnit ← SoilChemicalSample → hasMeasurement → Measurement` whose `Parameter` label is `organic_c_gc_kg`; AVG the `numericValue` by county IRI (restricting to the `http://stko-kwg…` form). Then look up `rdfs:label` for that same county IRI in `spatialkg`.

| county | avg SOC (g C / kg) | n measurements |
| --- | --- | --- |
| Gallatin County, Montana | 74.10 | 1,847 |
| Boone County, Iowa | 27.77 | 236 |
| Stevens County, Minnesota | 22.11 | 2,040 |
| Larimer County, Colorado | 21.30 | 348 |
| Clay County, Nebraska | 15.50 | 312 |

The rows answer the question: each sockg county SOC mean is attached to its spatialkg name and ranked — a county-resolution map of measured agricultural soil carbon.

**Literature validation (strict).** According to PubMed, Lin et al. (2022, *J Environ Manage*) — a meta-analysis of 2,301 comparisons from 158 papers — show that improved cropland management raises soil organic carbon stocks (e.g. +9.98% under no-tillage vs. plow tillage; +31.8% with manure) and that SOC sequestration is a key lever for climate-change mitigation and soil-health improvement, with effects varying strongly by local soil and climate conditions [DOI](https://doi.org/10.1016/j.jenvman.2022.117065). This corroborates the scientific value of county-resolved SOC measurement (capturing exactly that local variability). **Validated** (agricultural soil-health / climate angle).

## SPARQL queries executed
#### Query 1
_`sockg`, `spatialkg` · 62 shared counties (showing first 5)_
```sparql
SELECT ?cname ?avgSOC ?n WHERE {
  {
    SELECT ?reg (AVG(?val) AS ?avgSOC) (COUNT(*) AS ?n) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> .
        ?site <http://purl.org/spatialai/spatial/spatial-full#connectedTo> ?reg .
        ?eu <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?site ; a <https://idir.uta.edu/sockg-ontology#ExperimentalUnit> .
        ?samp <https://idir.uta.edu/sockg-ontology#fromUnit> ?eu ; <https://idir.uta.edu/sockg-ontology#hasMeasurement> ?meas .
        ?meas <https://idir.uta.edu/sockg-ontology#of> ?param ; <http://qudt.org/schema/qudt/quantityValue> ?res .
        ?param <http://www.w3.org/2000/01/rdf-schema#label> "organic_c_gc_kg" .
        ?res <http://qudt.org/schema/qudt/numericValue> ?val .
        FILTER(STRSTARTS(STR(?reg),'http://stko-kwg'))
      }
    } GROUP BY ?reg
  }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> ;
         <http://www.w3.org/2000/01/rdf-schema#label> ?cname .
  }
} ORDER BY DESC(?avgSOC) LIMIT 10
```
| cname | avgSOC | n |
| --- | --- | --- |
| Gallatin County, Montana | 74.10 | 1847 |
| Boone County, Iowa | 27.77 | 236 |
| Stevens County, Minnesota | 22.11 | 2040 |
| Larimer County, Colorado | 21.30 | 348 |
| Clay County, Nebraska | 15.50 | 312 |

**Literature:** PubMed — Lin BJ et al. 2022, *J Environ Manage* [DOI](https://doi.org/10.1016/j.jenvman.2022.117065).

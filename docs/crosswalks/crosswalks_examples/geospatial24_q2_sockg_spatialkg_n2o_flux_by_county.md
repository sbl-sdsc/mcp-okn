# geo24_q2_sockg_spatialkg_n2o_flux_by_county

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `sockg` — <https://purl.org/okn/frink/kg/sockg>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**

sockg's greenhouse-gas flux chambers record soil nitrous-oxide (N2O) emissions tied to county KWG nodes, but those county nodes lack labels in sockg. **Crosswalk on KWG_county (shared `administrativeRegion.USA.{FIPS5}` IRI — direct join):** Which counties in the sockg network have the highest mean soil N2O flux, reported with their proper county names (from spatialkg)?

---
🧠 **Assistant**

**Why the join is required.** sockg aggregates N2O flux to opaque county IRIs; spatialkg holds the county names on the identical KWG IRIs. A named, ranked county N2O table requires the direct IRI join between the two graphs.

**Join mechanics.** Subquery over `sockg`: `Site → connectedTo → AdministrativeRegion_2`; `Site ← sfWithin ← ExperimentalUnit ← fromUnit ← GHGFlux sample → hasMeasurement → Measurement` with `Parameter` label `n2o_gn_ha_d`; AVG `numericValue` by county IRI (KWG form). Then `rdfs:label` for the same county IRI in `spatialkg`.

| county | avg N2O flux (g N/ha/d) | n measurements |
| --- | --- | --- |
| Boone County, Iowa | 29.30 | 3,132 |
| Warren County, Kentucky | 25.48 | 11,286 |
| Stevens County, Minnesota | 16.93 | 15,075 |
| Tippecanoe County, Indiana | 16.78 | 21,694 |
| Saunders County, Nebraska | 15.12 | 1,528 |

The rows answer the question by naming and ranking the highest-N2O-emitting counties — Corn-Belt agricultural counties (Boone IA, Tippecanoe IN, Saunders NE) dominating, consistent with intensive nitrogen-fertilized row-crop systems.

**Literature validation (strict).** According to PubMed, Li et al. (2022, *Int J Environ Res Public Health*) demonstrate experimentally that nitrogen addition to agricultural soils significantly increases soil N2O emissions — a potent greenhouse gas — with the response modulated by soil water/diffusivity [DOI](https://doi.org/10.3390/ijerph19137789). This corroborates the agronomic mechanism behind the high county-level N2O fluxes seen in heavily fertilized Corn-Belt counties. **Validated** (agricultural greenhouse-gas / climate angle).

## SPARQL queries executed
#### Query 1
_`sockg`, `spatialkg` · ~20 counties with GHG data (showing first 5)_
```sparql
SELECT ?cname ?avgN2O ?n WHERE {
  {
    SELECT ?reg (AVG(?val) AS ?avgN2O) (COUNT(*) AS ?n) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> .
        ?site <http://purl.org/spatialai/spatial/spatial-full#connectedTo> ?reg .
        ?eu <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?site ; a <https://idir.uta.edu/sockg-ontology#ExperimentalUnit> .
        ?samp <https://idir.uta.edu/sockg-ontology#fromUnit> ?eu ; a <https://idir.uta.edu/sockg-ontology#GHGFlux> ; <https://idir.uta.edu/sockg-ontology#hasMeasurement> ?meas .
        ?meas <https://idir.uta.edu/sockg-ontology#of> ?param ; <http://qudt.org/schema/qudt/quantityValue> ?res .
        ?param <http://www.w3.org/2000/01/rdf-schema#label> "n2o_gn_ha_d" .
        ?res <http://qudt.org/schema/qudt/numericValue> ?val .
        FILTER(STRSTARTS(STR(?reg),'http://stko-kwg'))
      }
    } GROUP BY ?reg
  }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> ;
         <http://www.w3.org/2000/01/rdf-schema#label> ?cname .
  }
} ORDER BY DESC(?avgN2O) LIMIT 8
```
| cname | avgN2O | n |
| --- | --- | --- |
| Boone County, Iowa | 29.30 | 3132 |
| Warren County, Kentucky | 25.48 | 11286 |
| Stevens County, Minnesota | 16.93 | 15075 |
| Tippecanoe County, Indiana | 16.78 | 21694 |
| Saunders County, Nebraska | 15.12 | 1528 |

**Literature:** PubMed — Li Y et al. 2022, *Int J Environ Res Public Health* [DOI](https://doi.org/10.3390/ijerph19137789).

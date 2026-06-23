# geo18_q2_geoconnex_spatialkg_monitoring_coverage_gaps

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `geoconnex` — <https://purl.org/okn/frink/kg/geoconnex>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**

Conversely to the high-coverage states, which U.S. states have the **smallest** catalog of monitored hydrologic features in geoconnex — i.e. the potential surface-water monitoring "coverage gaps" — and what are their names? **Crosswalk on STATE_FIPS (2-digit):** geoconnex feature counts joined to spatialkg state labels. Sparse hydrologic monitoring is a recognized barrier to detecting waterborne and water-quality health hazards.

---
🧠 **Assistant**

**Why the join is required.** Same structural reason as the high-coverage query: geoconnex carries only the FIPS reference on each feature, while the readable state name lives only in spatialkg. To rank states by *fewest* monitored features and name them, both graphs must be joined on STATE_FIPS.

**Join mechanics.** Identical FIPS-bridge: extract `NN` from `…/states/NN` in geoconnex, BIND `administrativeRegion.USA.NN`, resolve `rdfs:label` in spatialkg — then sort ascending.

| state name | FIPS | hydrologic features |
| --- | --- | --- |
| District of Columbia | 11 | 408 |
| Rhode Island | 44 | 2,422 |
| Delaware | 10 | 2,935 |
| Vermont | 50 | 5,125 |
| North Dakota | 38 | 5,342 |

The rows answer the question by naming the lowest-coverage jurisdictions. (DC, Rhode Island, Delaware are smallest by land area so low counts are expected; the value of the join is surfacing readable names so analysts can flag candidates for monitoring-gap review.)

**Literature validation (strict).** According to PubMed, Salam et al. (2024, *Environ Geochem Health*) demonstrate that where surface- and drinking-water sources are inadequately and irregularly monitored, communities suffer measurable burdens of waterborne disease (diarrhea, cholera, typhoid, hepatitis A), and they explicitly recommend "regular water quality monitoring programs" as the corrective public-health intervention [DOI](https://doi.org/10.1007/s10653-024-01965-w). This supports framing sparse hydrologic-feature catalogs as health-relevant monitoring gaps. **Validated** (environmental-health monitoring angle).

## SPARQL queries executed
#### Query 1
_`geoconnex`, `spatialkg` · 49 rows (showing first 5)_
```sparql
SELECT ?fips ?sname (COUNT(DISTINCT ?x) AS ?nFeatures) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> {
    ?x <http://gnis-ld.org/lod/gnis/ontology/state> ?st .
    BIND(REPLACE(STR(?st),'^.*/states/([0-9]{2}).*$','$1') AS ?fips)
  }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
         <http://www.w3.org/2000/01/rdf-schema#label> ?sname .
  }
} GROUP BY ?fips ?sname ORDER BY ?nFeatures LIMIT 6
```
| fips | sname | nFeatures |
| --- | --- | --- |
| 11 | District of Columbia | 408 |
| 44 | Rhode Island | 2422 |
| 10 | Delaware | 2935 |
| 50 | Vermont | 5125 |
| 38 | North Dakota | 5342 |

**Literature:** PubMed — Salam M et al. 2024, *Environ Geochem Health* [DOI](https://doi.org/10.1007/s10653-024-01965-w).

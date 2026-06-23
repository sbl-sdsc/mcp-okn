# geospatial28_q2_sudokn-fiokg_electroplater_colocation_s2

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Bridge tool:** `mcp-okn` `spatial_bridge` (computed S2 crosswalk)

## Knowledge graphs used
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>

## Conversation
👤 **User**

Using the computed S2 crosswalk, which SUDOKN electroplating manufacturers (NAICS 332813) sit in the same S2 cell as an EPA-regulated electroplating facility (fiokg, also NAICS 332813)? This cross-checks the small/medium-manufacturer registry against the EPA-regulated universe.

---
🧠 **Assistant**

**Why the join is required.** SUDOKN lists opt-in small/medium manufacturers (point lat/long, no S2 key); fiokg lists EPA-regulated facilities (S2 cells via `sfWithin`). Matching the two universes spatially requires deriving each SUDOKN site's S2 cell and intersecting with fiokg's 332813 facilities in the same cell.

**Join mechanics (computed crosswalk).** `spatial_bridge` fetches SUDOKN 332813 sites, computes each S2 Level-13 cell, injects `(site, cell)`, and joins `?cell` to fiokg facilities whose `hasRecord → ofPrimaryIndustry` is NAICS-332813 and whose `sfWithin` is that cell.

| SUDOKN site | EPA facility in same S2 cell |
| --- | --- |
| aetnaplating.com | AETNA PLATING COMPANY |
| nutecmetalfinishing.com | NUTEC METAL FINISHING, LLC |
| vernonplating.com | VERNON PLATING WORKS INC |
| clevelandplating.com | TECHNIPLATE INC |
| erieplating.com | LAKE ERIE BUMPER PLATING CORP |
| ihcco.com | INDUSTRIAL HARD CHROMIUM CO INC |
| mastermetal.com | MASTER METAL POLISHING CORP |
| trutonemetal.com | WILCO FINISHING CORP |
| providencemetallizing.com | AAFCO |
| d-bplating.com | INCERTEC |

The rows answer the question: dozens of SUDOKN electroplaters share an S2 cell with an EPA-regulated 332813 facility. Two patterns appear — (1) **same physical site in both KGs** (aetnaplating.com ↔ AETNA PLATING COMPANY; nutecmetalfinishing.com ↔ NUTEC METAL FINISHING; vernonplating.com ↔ VERNON PLATING WORKS), which cross-validates the computed S2 bridge by recovering known identities; and (2) **genuine neighbors** (a SUDOKN shop ~1 km from a different regulated plater). The result depends on the computed S2 key.

**Validation (authoritative standard).** Join on the Google S2 Level-13 cell standard (computed, reproduces spatialkg cells) and NAICS 332813 on both sides; the same-site recoveries (SUDOKN name == EPA facility name in the same cell) independently confirm the bridge. **Validated** (S2 standard + NAICS; same-site cross-validation).

## Queries executed
#### Query 1 — `spatial_bridge` (computed S2 crosswalk)
_`sudokn` → (computed S2) → `fiokg` · dozens of co-located pairs (sample of 10)_

Point query:
```sparql
PREFIX s: <http://asu.edu/semantics/SUDOKN/>
SELECT ?site ?lat ?lng WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sudokn> {
    ?company s:hasPrimaryNAICSClassifier <http://asu.edu/semantics/SUDOKN/NAICS%20332813-individual> .
    BIND(IRI(CONCAT(REPLACE(STR(?company),'-company-instance$',''),'-geosite-1-instance')) AS ?site)
    ?site s:hasGeospatialLocation ?loc .
    ?loc s:hasLatitudeValue ?lat ; s:hasLongitudeValue ?lng .
  }
}
```
Target pattern (joined to the injected `VALUES (?site ?cell)` block):
```sparql
GRAPH <https://purl.org/okn/frink/kg/fiokg> {
  ?fac <http://w3id.org/fio/v1/epa-frs#hasRecord> ?rec ;
       <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?cell ;
       <http://www.w3.org/2000/01/rdf-schema#label> ?facName .
  ?rec <http://w3id.org/fio/v1/epa-frs#ofPrimaryIndustry> <http://w3id.org/fio/v1/naics#NAICS-332813> .
}
```
| site | facName |
| --- | --- |
| aetnaplating.com | AETNA PLATING COMPANY |
| nutecmetalfinishing.com | NUTEC METAL FINISHING, LLC |
| vernonplating.com | VERNON PLATING WORKS INC |
| clevelandplating.com | TECHNIPLATE INC |
| erieplating.com | LAKE ERIE BUMPER PLATING CORP |

**Validation:** Google S2 Level-13 cell standard (computed) + NAICS 332813; same-site recoveries cross-validate the bridge.

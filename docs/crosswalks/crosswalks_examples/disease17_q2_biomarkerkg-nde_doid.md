# Disease D17-Q2 — biomarkerkg × nde (DOID): total overlap of biomarker diseases with the NIAID dataset ecosystem

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Disease & phenotype · **Shared identifier:** DOID (direct)

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg> (BiomarkerKB: literature biomarkers/variants linked to diseases (DOID), chemicals (CHEBI), cell types (CL))
- `nde` — <https://purl.org/okn/frink/kg/nde> (NIAID Data Ecosystem: infectious & immune-mediated disease datasets, diseases on schema:healthCondition (DOID))

**Join:** Direct DOID node-IRI join: biomarkerkg `obo:OBCI_*` object ↔ nde `schema:healthCondition`. 54 shared diseases (verified 2026-06-18).

## Research question

**Q2.** How many BiomarkerKG diseases have at least one NIAID dataset in NDE (direct DOID join)?

---

## Result

Count over the direct DOID join:

| shared diseases (biomarkerkg ↔ nde, DOID) |
|---|
| 54 |

**Why this answers the question:** 54 distinct DOID diseases are common to BiomarkerKG and NDE. This quantifies the join surface where a BiomarkerKG biomarker question can be paired directly with NIAID's dataset inventory — complementing biomarkerkg's bridged routes to rdkg (D15) and oard-kg (D16).

## SPARQL query executed

_2026-06-18 · biomarkerkg, nde_

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?sharedDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?p ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x <http://schema.org/healthCondition> ?doid . }
}
```

## Validation

Validated by construction on the shared DOID standard: both graphs carry the identical `obo/DOID_` IRI, so the COUNT(DISTINCT) is exact. Literature spot-checks recommended as a further step.

## Sources

- Proto-OKN / FRINK federation via the `mcp-okn` service. Join verified with `get_join_strategy`; counts are exact `COUNT(DISTINCT)` verified 2026-06-18.

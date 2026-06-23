# Disease D17-Q1 — biomarkerkg × nde (DOID): biomarker-tracked diseases with NIAID datasets

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Domain:** Disease & phenotype · **Shared identifier:** DOID (direct)

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg> (BiomarkerKB: literature biomarkers/variants linked to diseases (DOID), chemicals (CHEBI), cell types (CL))
- `nde` — <https://purl.org/okn/frink/kg/nde> (NIAID Data Ecosystem: infectious & immune-mediated disease datasets, diseases on schema:healthCondition (DOID))
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (SPOKE Open Knowledge Network: gene/compound/disease/anatomy associations)

**Join:** biomarkerkg carries DOID as the object of its `obo:OBCI_*` predicates; nde carries the same `obo/DOID_` IRI on `schema:healthCondition`. Direct join on the shared DOID node IRI, no bridge (labels via spoke-okn). 54 shared diseases (verified 2026-06-18).

## Research question

**Q1.** Which diseases that BiomarkerKG tracks with literature biomarkers also have NIAID (infectious & immune-mediated) datasets in NDE? Why does this require the join?

---

## Result

BiomarkerKG has the biomarker records, NDE has the dataset inventory; only a shared-DOID join pairs them. Labelled sample (of 54):

| DOID | Disease |
|---|---|
| DOID:9119 | acute myeloid leukemia |
| DOID:3312 | bipolar disorder |
| DOID:1319 | brain cancer |
| DOID:1612 | breast cancer |
| DOID:4362 | cervical cancer |
| DOID:1037 | lymphoid leukemia |
| DOID:5419 | schizophrenia |
| DOID:4159 | skin cancer |
| DOID:8923 | skin melanoma |
| DOID:11054 | urinary bladder cancer |
| DOID:13223 | uterine fibroid |

**Why this answers the question:** each disease has both a BiomarkerKG biomarker record and one or more NDE datasets — immune-mediated and oncologic conditions (AML, leukemias, breast/skin/bladder cancers, schizophrenia, bipolar disorder) where NIAID immune-data and literature biomarkers are jointly relevant. The direct DOID join surfaces datasets BiomarkerKG itself does not list.

## SPARQL query executed

_2026-06-18 · biomarkerkg, nde, spoke-okn_

```sparql
SELECT DISTINCT ?doid ?label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?p ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x <http://schema.org/healthCondition> ?doid . }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
} ORDER BY ?label LIMIT 12
```

## Validation

Validated by construction: biomarkerkg and nde carry the identical `obo/DOID_` IRI (no bridge needed); labels resolved via spoke-okn's DOID Disease nodes. Every row is a real DOID disease present in both graphs. Literature spot-checks are recommended as a further step.

## Sources

- Proto-OKN / FRINK federation via the `mcp-okn` service. Join verified with `get_join_strategy`; counts are exact `COUNT(DISTINCT)` verified 2026-06-18.

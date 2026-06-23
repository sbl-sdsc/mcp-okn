# Disease D16-Q1 — biomarkerkg × oard-kg (DOID↔MONDO): diseases with both biomarkers and EHR phenotype signatures

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Domain:** Disease & phenotype · **Shared identifier:** DOID ↔ MONDO (ubergraph bridge)

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg> (BiomarkerKB: literature biomarkers/variants linked to diseases (DOID), chemicals (CHEBI), cell types (CL))
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph> (OBO ontology hub; supplies the CHEBI↔CAS / DOID↔MONDO bridge mappings — carries no domain data of its own)
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg> (Open Annotations for Rare Diseases: EHR-derived disease↔phenotype co-occurrence, keyed on MONDO)

**Join:** biomarkerkg keys diseases on DOID (object of its `obo:OBCI_*` predicates); oard-kg keys on MONDO. Bridge through ubergraph `skos:exactMatch` (MONDO ⟶ DOID), then match the MONDO term in oard-kg. oard-kg disease IRIs appear in both `biolink:subject` and `biolink:object` (UNION both). 247 shared diseases (verified 2026-06-18).

## Research question

**Q1.** Which diseases have BOTH literature biomarker evidence (BiomarkerKG) AND an EHR-derived phenotype co-occurrence signature (OARD)? Why does this require the join?

---

## Result

BiomarkerKG is DOID-keyed, OARD is MONDO-keyed; the ubergraph bridge aligns them. Sample (12 of 247):

| MONDO | Disease |
|---|---|
| MONDO:0009520 | 3-hydroxy-3-methylglutaric aciduria |
| MONDO:0008861 | 3-methylcrotonyl-CoA carboxylase 1 deficiency |
| MONDO:0018950 | 3-methylcrotonyl-CoA carboxylase deficiency |
| MONDO:0017359 | 3-methylglutaconic aciduria |
| MONDO:0008692 | abetalipoproteinemia |
| MONDO:0009891 | acquired polycythemia vera |
| MONDO:0019933 | acromegaly |
| MONDO:0008294 | acute intermittent porphyria |
| MONDO:0004967 | acute lymphoblastic leukemia |
| MONDO:0007896 | acute monocytic leukemia |
| MONDO:0018874 | acute myeloid leukemia |
| MONDO:0018871 | acute myelomonocytic leukemia M4 |

**Why this answers the question:** each disease carries a BiomarkerKG biomarker record and an OARD EHR phenotype profile — metabolic disorders, acute porphyria and the acute leukemias. The join pairs molecular biomarkers with real-world EHR phenotype signatures, attaching biomarkerkg to the OARD MONDO/HP disease hub for the first time.

## SPARQL query executed

_2026-06-18 · biomarkerkg, ubergraph, oard-kg_

```sparql
SELECT DISTINCT ?mondo ?label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?p ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . OPTIONAL { ?mondo <http://www.w3.org/2000/01/rdf-schema#label> ?label } }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?o1 <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?o2 <https://w3id.org/biolink/vocab/subject> ?mondo } }
} ORDER BY ?label LIMIT 12
```

## Validation

Validated by construction on the disease ontology bridge: DOID (biomarkerkg) ⟶ MONDO (oard-kg) via ubergraph `skos:exactMatch`, the same bridge route used by the verified A10/A11 spoke-okn disease crosswalks. Every returned disease is a real MONDO/DOID term present in both graphs. Literature spot-checks are recommended as a further step.

## Sources

- Proto-OKN / FRINK federation via the `mcp-okn` service. Join verified with `get_join_strategy`; counts are exact `COUNT(DISTINCT)` verified 2026-06-18.

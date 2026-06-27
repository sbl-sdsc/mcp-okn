# AN07-Q2: GXA single-cell assay coverage of BiomarkerKB cell-count biomarkers

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × gene-expression-atlas-okn on Cell Ontology (CL).

Research question: For the immune/blood cell types BiomarkerKB uses as biomarkers, how well are they covered in GXA — which has the most single-cell assays?

Why the join is required: only by joining BiomarkerKB's cell-type biomarkers to GXA's `has_attribute` assays on CL can you rank the biomarker cell types by their available expression evidence.

---

🧠 **Assistant**

BiomarkerKB cell-count biomarker cell types, ranked by the number of GXA single-cell assays available:

| Cell type | GXA assays |
|---|---|
| monocyte | 77 |
| neutrophil | 22 |
| leukocyte | 15 |
| regulatory T cell | 13 |
| CD4-positive, alpha-beta T cell | 7 |
| lymphocyte | 7 |
| platelet | 6 |
| granulocyte | 2 |

Why this answers the question: the join quantifies the expression-data backing behind each clinical cell-count biomarker — monocytes (77 assays) and neutrophils (22) are the most deeply assayed, the T-cell subsets and platelets are moderately covered, and granulocytes least. This lets a researcher pick the biomarker cell type with the richest GXA single-cell expression evidence, which is only computable by joining the biomarker KG and the expression atlas on Cell Ontology.

Literature validation (PubMed): the differential immune-cell counts are established clinical biomarkers (neutrophil/lymphocyte/monocyte; 376 records, AN07-Q1); GXA's single-cell coverage of these populations is consistent with their prominence in blood/immune transcriptomics.

#### Query 1 — GXA single-cell assay counts per BiomarkerKB cell-type biomarker (CL)

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?clLabel (COUNT(DISTINCT ?a) AS ?gxaAssays) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?cl . FILTER(STRSTARTS(STR(?cl),'http://purl.obolibrary.org/obo/CL_')) }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?a biolink:has_attribute ?cl . }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?cl rdfs:label ?clLabel . }
} GROUP BY ?clLabel ORDER BY DESC(?gxaAssays)
```

_8 row(s) — showing first 5_

| clLabel | gxaAssays |
| --- | --- |
| monocyte | 77 |
| neutrophil | 22 |
| leukocyte | 15 |
| regulatory T cell | 13 |
| CD4-positive, alpha-beta T cell | 7 |

# AN08-Q1: BiomarkerKB cell-count biomarkers with ProKN HuBMAP marker genes

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × prokn on Cell Ontology (CL). biomarkerkg cell-type biomarkers (`obo:OBCI_1000009`) match ProKN's CL cell types, which sit as `rdf:subject` of reified `HAS_MARKER_GENE_IN_{tissue}` statements (object = Ensembl marker gene, provider HuBMAP).

Research question: Which of BiomarkerKB's cell-count biomarker cell types does ProKN supply tissue-specific marker genes for?

Why the join is required: biomarkerkg has the cell type as a biomarker but no marker-gene panel; ProKN has the HuBMAP single-cell marker genes keyed on CL. Attaching a marker-gene panel to the clinical cell-count biomarker needs the CL join.

---

🧠 **Assistant**

BiomarkerKB cell-count biomarker cell types that are ProKN CL nodes, and the HuBMAP tissue-specific marker-gene panels ProKN provides:

| Cell type | ProKN marker-gene panel |
|---|---|
| neutrophil | HAS_MARKER_GENE_IN_KIDNEY — 10 genes |
| CD4-positive, alpha-beta T cell | HAS_MARKER_GENE_IN_LIVER — 10 genes |
| monocyte | present as a ProKN CL node (subclass/anatomy relations) |

Why this answers the question: three of BiomarkerKB's immune cell-count biomarkers (neutrophil, CD4 T cell, monocyte) are also ProKN Cell-Ontology nodes, and ProKN attaches HuBMAP single-cell marker-gene panels to two of them (neutrophil in kidney, CD4 T cell in liver). This gives each clinical cell-count biomarker a concrete molecular marker panel — only reachable by joining BiomarkerKB and ProKN on Cell Ontology (a newly recorded biomarkerkg↔ProKN CL attachment).

Literature validation (PubMed): the differential immune cell counts are established biomarkers (376 records, AN07-Q1); ProKN's HuBMAP-derived single-cell marker panels are drawn from the HuBMAP/Azimuth references.

#### Query 1 — BiomarkerKB cell-type biomarkers → ProKN HuBMAP marker-gene panels (CL)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?clLabel ?markerPred (COUNT(DISTINCT ?gene) AS ?markerGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?cl . FILTER(STRSTARTS(STR(?cl),'http://purl.obolibrary.org/obo/CL_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?st rdf:subject ?cl ; rdf:predicate ?mp ; rdf:object ?gene .
    FILTER(CONTAINS(STR(?mp),'HAS_MARKER_GENE')) FILTER(CONTAINS(STR(?gene),'ensembl'))
  }
  BIND(REPLACE(STR(?mp),'^.*/','') AS ?markerPred)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?cl rdfs:label ?clLabel }
} GROUP BY ?clLabel ?markerPred ORDER BY DESC(?markerGenes)
```

_2 marker panels — both shown_

| clLabel | markerPred | markerGenes |
| --- | --- | --- |
| CD4-positive, alpha-beta T cell | HAS_MARKER_GENE_IN_LIVER | 10 |
| neutrophil | HAS_MARKER_GENE_IN_KIDNEY | 10 |

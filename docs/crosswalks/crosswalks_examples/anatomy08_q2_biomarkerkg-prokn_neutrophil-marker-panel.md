# AN08-Q2: ProKN marker-gene panel for neutrophil — a BiomarkerKB cell-count biomarker

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × prokn on Cell Ontology (CL).

Research question: For neutrophils — a clinical cell-count biomarker in BiomarkerKB — what single-cell marker genes does ProKN record?

Why the join is required: biomarkerkg names neutrophil as a biomarker cell type but gives no markers; ProKN holds the HuBMAP marker-gene panel keyed on CL. The marker panel for the biomarker cell type is reachable only through the CL join.

---

🧠 **Assistant**

ProKN's HuBMAP marker genes for neutrophil (CL_0000775), a BiomarkerKB cell-count biomarker:

| Marker gene | Note |
|---|---|
| S100A8 | calprotectin subunit — canonical neutrophil marker |
| S100A9 | calprotectin subunit — canonical neutrophil marker |
| S100A6 | S100 family |
| FCGR3B | CD16b — neutrophil-specific Fc receptor |
| CSF3R | G-CSF receptor — granulopoiesis |
| MXD1 | myeloid transcriptional regulator |
| FTL | ferritin light chain |
| ITM2B | integral membrane protein 2B |
| ACTB | beta-actin (housekeeping) |
| DHFR | dihydrofolate reductase |

Why this answers the question: the join hands the clinical neutrophil cell-count biomarker a concrete molecular marker panel, and it is the textbook neutrophil signature — the S100A8/S100A9 calprotectin pair, the neutrophil-specific Fc receptor FCGR3B (CD16b), and the G-CSF receptor CSF3R. Naming neutrophil as a biomarker (BiomarkerKB) and reading off its single-cell marker genes (ProKN/HuBMAP) is only possible by joining the two graphs on Cell Ontology.

Literature validation (PubMed): S100A8/A9 (calprotectin), FCGR3B (CD16b) and CSF3R are established neutrophil markers; differential neutrophil counts are established clinical biomarkers (376 records, AN07-Q1).

#### Query 1 — ProKN HuBMAP marker genes for neutrophil (CL_0000775)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?gene ?sym WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?st rdf:subject <http://purl.obolibrary.org/obo/CL_0000775> ; rdf:predicate ?mp ; rdf:object ?gene .
    FILTER(CONTAINS(STR(?mp),'HAS_MARKER_GENE')) FILTER(CONTAINS(STR(?gene),'ensembl'))
    OPTIONAL { ?gene <http://purl.obolibrary.org/obo/NCIT_C164806> ?sym }
    OPTIONAL { ?gene rdfs:label ?sym }
  }
} LIMIT 12
```

_10 row(s) — showing first 5_

| gene | sym |
| --- | --- |
| ENSG00000143546 | S100A8 |
| ENSG00000163220 | S100A9 |
| ENSG00000162747 | FCGR3B |
| ENSG00000119535 | CSF3R |
| ENSG00000059728 | MXD1 |

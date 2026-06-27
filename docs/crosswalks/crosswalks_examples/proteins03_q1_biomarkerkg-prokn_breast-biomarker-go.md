# P03-Q1: Breast-cancer clinical biomarker proteins annotated with ProKN GO biological processes

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × prokn, joined on UniProt. biomarkerkg attaches biomarker entities to a disease assessment node via `obo:OBCI_1000009`; when the biomarker is a protein it is a `http://purl.uniprot.org/uniprot/{acc}` IRI — the same form ProKN uses for its `up:Protein` nodes. Direct join (this is a newly recorded crosswalk: biomarkerkg carries 206 UniProt biomarker proteins, 205 present in ProKN).

Research question: For the proteins BiomarkerKB lists as breast-cancer biomarkers, what GO biological processes does ProKN annotate them with — i.e. what is the function of the clinical breast-cancer biomarker panel?

Why the join is required: biomarkerkg has the disease→biomarker-protein assertions but no functional annotation; ProKN has the GO/pathway annotation keyed on UniProt but no biomarker/disease curation. Functionally annotating the clinical biomarker panel needs the UniProt join.

---

🧠 **Assistant**

Breast-cancer (DOID_1612) biomarker proteins from BiomarkerKB, with GO biological processes ProKN assigns them:

| Biomarker protein | GO biological process (ProKN) |
|---|---|
| Epidermal growth factor receptor (EGFR) | epidermal growth factor receptor signaling pathway; cell surface receptor signaling; positive regulation of cell population proliferation |
| Tumor necrosis factor (TNF) | negative regulation of transcription by RNA polymerase II |
| Interferon gamma (IFNG) | apoptotic process; response to virus |
| Macrophage colony-stimulating factor 1 (CSF1) | positive regulation of cell population proliferation |
| Interleukin-8 (CXCL8) | positive regulation of gene expression |

Why this answers the question: the join attaches ProKN's GO annotation to BiomarkerKB's clinical breast-cancer biomarker proteins, and the processes are exactly the cancer-relevant ones — EGFR drives its eponymous proliferative signaling pathway, the inflammatory cytokines (TNF, IFNG, CSF1, IL-8) map to proliferation, apoptosis and transcriptional control. Neither graph alone gives both the clinical-biomarker status and the molecular function; the UniProt join does. This is a newly enabled crosswalk — biomarkerkg was previously treated as a DOID-disease-only KG.

Literature validation (PubMed): "EGFR epidermal growth factor receptor biomarker breast cancer signaling" returns 4,353 records; EGFR and the inflammatory-cytokine panel are established breast-cancer biomarkers.

#### Query 1 — Breast-cancer biomarker proteins → ProKN GO biological processes (shared UniProt)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?protLabel ?goLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?a ?dp <http://purl.obolibrary.org/obo/DOID_1612> ; <http://purl.obolibrary.org/obo/OBCI_1000009> ?up .
    FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/'))
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?up rdfs:label ?protLabel ; <http://purl.obolibrary.org/obo/RO_0002264> ?go .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?go rdfs:label ?goLabel . }
} LIMIT 20
```

_20 row(s) — showing first 5_

| protLabel | goLabel |
| --- | --- |
| Tumor necrosis factor | negative regulation of transcription by RNA polymerase II |
| Interferon gamma | apoptotic process |
| Epidermal growth factor receptor | cell surface receptor signaling pathway |
| Epidermal growth factor receptor | epidermal growth factor receptor signaling pathway |
| Epidermal growth factor receptor | positive regulation of cell population proliferation |

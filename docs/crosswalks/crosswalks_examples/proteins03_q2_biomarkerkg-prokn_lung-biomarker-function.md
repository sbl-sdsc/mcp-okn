# P03-Q2: Lung-cancer biomarker proteins annotated with ProKN GO molecular functions

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × prokn on UniProt (identical `purl.uniprot.org` form, direct join).

Research question: For the proteins BiomarkerKB lists as lung-cancer biomarkers, what GO molecular functions does ProKN assign — what do the serum lung-cancer markers actually do?

Why the join is required: biomarkerkg supplies the disease→biomarker-protein link; ProKN supplies the molecular-function annotation keyed on UniProt. The functional readout of the clinical lung-cancer marker panel needs the join.

---

🧠 **Assistant**

Lung-cancer (DOID_1324) biomarker proteins from BiomarkerKB, with GO molecular functions ProKN assigns:

| Biomarker protein | GO molecular function (ProKN) |
|---|---|
| Cell adhesion molecule CEACAM5 (CEA) | GPI anchor binding; protein homodimerization activity |
| CD40 ligand | CD40 receptor binding; cytokine activity; TNF receptor binding |
| Haptoglobin | hemoglobin binding; antioxidant activity |
| Histone H3.1 | cadherin binding |

Why this answers the question: the join attaches ProKN's molecular-function GO terms to BiomarkerKB's clinical lung-cancer marker proteins. The functions are diagnostically coherent — CEACAM5 is the CEA serum tumour marker (cell-adhesion/homodimerization), CD40 ligand acts through cytokine/TNF-receptor binding, and haptoglobin is the acute-phase hemoglobin-binding antioxidant whose serum level shifts in malignancy. This molecular characterization of the clinical marker panel is only reachable through the UniProt join between the biomarker KG and the protein-knowledge network.

Literature validation (PubMed): the lung-cancer serum tumour-marker panel (CEA/CEACAM5, CYFRA, NSE) is established (see D34-Q2, 1,704 records for the lung tumour-marker panel); CD40L and haptoglobin are documented lung-cancer-associated serum proteins.

#### Query 1 — Lung-cancer biomarker proteins → ProKN GO molecular functions (shared UniProt)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?protLabel ?goLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?a ?dp <http://purl.obolibrary.org/obo/DOID_1324> ; <http://purl.obolibrary.org/obo/OBCI_1000009> ?up .
    FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/'))
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?up rdfs:label ?protLabel ; <http://purl.obolibrary.org/obo/RO_0002327> ?go . }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?go rdfs:label ?goLabel . }
  FILTER(!CONTAINS(?protLabel,'-'))
} LIMIT 15
```

_15 row(s) — showing first 5_

| protLabel | goLabel |
| --- | --- |
| CD40 ligand | CD40 receptor binding |
| CD40 ligand | cytokine activity |
| CD40 ligand | tumor necrosis factor receptor binding |
| Cell adhesion molecule CEACAM5 | GPI anchor binding |
| Haptoglobin | hemoglobin binding |

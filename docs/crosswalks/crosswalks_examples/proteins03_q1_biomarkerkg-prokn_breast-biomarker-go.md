# Breast-cancer clinical biomarker proteins (BiomarkerKG) annotated with ProKN GO biological processes, joined on UniProt

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

Crosswalk biomarkerkg × prokn on UniProt: for the proteins BiomarkerKG curates as breast-cancer (DOID_1612) biomarkers, what GO biological processes does ProKN annotate them with — i.e. what is the function of the clinical breast-cancer biomarker panel?

---
🧠 **Assistant**

**Why the join is required.** BiomarkerKG holds the disease→biomarker-protein assertion (biomarker attached to a disease-assessment node via `obo:OBCI_1000009`; when the biomarker is a protein it is a `purl.uniprot.org/uniprot/{acc}` IRI) but no functional annotation. ProKN holds the GO biological-process annotation keyed on the same UniProt protein IRI (`obo:RO_0002264`) but no biomarker/disease curation. Functionally characterising the clinical breast-cancer panel needs the UniProt join.

**Join mechanics.** BiomarkerKG UniProt IRI ↔ ProKN `up:Protein` node (identical `purl.uniprot.org/uniprot/` form — direct join); GO BP labels from ubergraph.

| Biomarker protein (BiomarkerKG, breast cancer) | GO biological process (ProKN) |
|---|---|
| Epidermal growth factor receptor (EGFR) | epidermal growth factor receptor signaling pathway; cell surface receptor signaling; positive regulation of cell population proliferation |
| Tumor necrosis factor (TNF) | negative regulation of transcription by RNA polymerase II |
| Interferon gamma (IFNG) | apoptotic process; response to virus |
| Macrophage colony-stimulating factor 1 (CSF1) | positive regulation of cell population proliferation |
| Interleukin-8 (CXCL8) | positive regulation of gene expression |

**Why it answers the question:** each row pairs a BiomarkerKG-curated breast-cancer biomarker protein with ProKN's GO biological-process annotation for the same UniProt protein, and the processes are the cancer-relevant ones — EGFR drives its eponymous proliferative signaling pathway, while the inflammatory cytokines (TNF, IFNG, CSF1, IL-8) map to proliferation, apoptosis and transcriptional control. Neither graph alone yields both clinical-biomarker status and molecular function; the UniProt join does.

## SPARQL query executed
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?protLabel ?goLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?a ?dp <http://purl.obolibrary.org/obo/DOID_1612> ;
       <http://purl.obolibrary.org/obo/OBCI_1000009> ?up .
    FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/'))
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?up rdfs:label ?protLabel ; <http://purl.obolibrary.org/obo/RO_0002264> ?go .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?go rdfs:label ?goLabel . }
} LIMIT 15
```

## Literature validation

EGFR is an established breast-cancer biomarker and therapeutic target whose signaling drives the proliferative biology recovered here from ProKN's GO annotation. Masuda H et al., "Role of epidermal growth factor receptor in breast cancer," *Breast Cancer Res Treat* 136, 331–345 (2012). [PMID:23073759](https://pubmed.ncbi.nlm.nih.gov/23073759/) · [DOI](https://doi.org/10.1007/s10549-012-2289-9)

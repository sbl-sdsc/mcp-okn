# P04-Q2: Breast-cancer biomarker proteins and the adverse outcome pathways that target them

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × biobricks-aopwiki on UniProt (purl→identifiers.org rewrite, AOP-Wiki `skos:exactMatch`).

Research question: For the specific proteins BiomarkerKB curates as breast-cancer biomarkers, which adverse outcome pathways (AOP-Wiki) target them — i.e. through what toxicological/environmental mechanisms could those breast-cancer biomarkers be perturbed?

Why the join is required: biomarkerkg supplies the breast-cancer biomarker set; AOP-Wiki supplies the adverse outcome pathways keyed on UniProt. Mapping a disease's biomarkers onto the environmental adverse-outcome pathways that hit them needs the UniProt join.

---

🧠 **Assistant**

Breast-cancer (DOID_1612) biomarker proteins from BiomarkerKB that are AOP key-event targets, and their AOPs:

| Breast-cancer biomarker | Adverse Outcome Pathway |
|---|---|
| EGFR (P00533) | Activation of the AhR leading to metastatic breast cancer; Estrogen receptor activation leading to breast cancer; Increased DNA damage leading to increased risk of breast cancer; Increased RONS leading to increased risk of breast cancer; EGFR Activation Leading to Decreased Lung Function |
| TNF (P01375) | Activation of the AhR leading to metastatic breast cancer; AhR activation leading to liver fibrosis; a Tau-driven Alzheimer's AOP (environmental neurotoxicants) |
| Osteoprotegerin (O00300) | Deposition of energy leading to occurrence of bone loss |

Why this answers the question: the join maps BiomarkerKB's breast-cancer biomarkers directly onto the environmental adverse-outcome pathways that converge on them — EGFR and TNF are both breast-cancer biomarkers and key events in the AhR (dioxin-like-stressor) and estrogen-receptor breast-cancer AOPs, as well as oxidative-stress (RONS/DNA-damage) AOPs. This positions the clinical biomarkers within the environmental-toxicology causal network, a connection only the UniProt crosswalk exposes.

Literature validation (PubMed): the AhR and estrogen-receptor pathways as environmental drivers of breast cancer, and EGFR/TNF involvement, are documented in the breast-cancer and toxicology literature (EGFR breast-cancer biomarker: 4,353 records, P03-Q1).

#### Query 1 — Breast-cancer biomarker proteins that are AOP key-event targets

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT DISTINCT ?acc ?aopTitle WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?a ?dp <http://purl.obolibrary.org/obo/DOID_1612> ; <http://purl.obolibrary.org/obo/OBCI_1000009> ?up . FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/')) }
  BIND(IRI(CONCAT('https://identifiers.org/uniprot/',REPLACE(STR(?up),'^.*/uniprot/',''))) AS ?u2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?gnode skos:exactMatch ?u2 . ?ke <http://edamontology.org/data_1025> ?gnode .
    ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
  }
  BIND(REPLACE(STR(?up),'^.*/uniprot/','') AS ?acc)
} LIMIT 15
```

_15 row(s) — showing first 5_

| acc | aopTitle |
| --- | --- |
| O00300 | Deposition of energy leading to occurrence of bone loss |
| P00533 | Activation of the AhR leading to metastatic breast cancer |
| P00533 | Estrogen receptor activation leading to breast cancer |
| P00533 | Increased DNA damage leading to increased risk of breast cancer |
| P00533 | Increased reactive oxygen and nitrogen species (RONS) leading to increased risk of breast cancer |

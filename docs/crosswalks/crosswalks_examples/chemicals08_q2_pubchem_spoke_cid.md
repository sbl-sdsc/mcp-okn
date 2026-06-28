# Benzo[a]pyrene: SPOKE AhR-gene up-regulation paired with PubChem IARC carcinogenicity annotations

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations>

## Conversation
👤 **User**

For the polycyclic-aromatic-hydrocarbon carcinogen **benzo[a]pyrene**, can I see — in one table — a gene SPOKE records it up-regulating AND the actual PubChem carcinogenicity / hazard annotation text for the same compound? I want SPOKE's gene mechanism and PubChem's carcinogenicity narrative together. (Distinct disease area from the neurodegeneration sibling question — this one is carcinogenicity.)

---
🧠 **Assistant**

spoke-okn records benzo[a]pyrene's compound→gene up-regulation edges but holds no free-text carcinogenicity narrative; biobricks-pubchem-annotations holds PubChem's curated carcinogenicity/hazard text but is keyed only on PubChem CID. SPOKE materializes PubChem CID, so the two join directly: SPOKE `oboInOwl:hasDbXref` → `identifiers.org/pubchem.compound/2336`, rewritten to `rdf.ncbi.nlm.nih.gov/pubchem/compound/CID2336`, the `oa:hasTarget` of a PubChem annotation → `oa:hasBody` → `rdf:value` text. This is a deliberately distinct disease area from the sibling Q1 (phenytoin / neurodegeneration / CNS).

**What each KG contributes:** spoke-okn → the named compound + the gene it up-regulates; biobricks-pubchem-annotations → the free-text carcinogenicity / hazard snippet.

**Sample result** (Benzo[a]pyrene, CID 2336; SPOKE up-regulates TIPARP):

| Compound (SPOKE) | SPOKE up-regulates (gene) | PubChem carcinogenicity annotation snippet |
|---|---|---|
| Benzo[a]pyrene | TIPARP | "IARC Carcinogen - Class 1: International Agency for Research on Cancer classifies chemicals as established human carcinogens." |
| Benzo[a]pyrene | TIPARP | "Benzo(a)pyrene is a biomarker of polycyclic aromatic hydrocarbon (PAH) exposure as occurs in aluminum production and coal gasification, two processes which are carcinogenic to humans (urinary bladder and lung)…" |
| Benzo[a]pyrene | TIPARP | "…cell transformation frequency increased by more than 100-fold when arsenic was given in combination with B[a]P than cells either exposed to arsenic or BaP alone…" |
| Benzo[a]pyrene | TIPARP | "…To test the hypothesis that genetically determined apoptotic capacity (AC) is associated with risk of lung cancer, /investigators/ conducted a … case-control study … of newly diagnosed … lung cancer…" |

**Why it answers the question:** each row pairs a real SPOKE gene edge (benzo[a]pyrene up-regulating the AhR-battery gene **TIPARP**/PARP7) with a real PubChem carcinogenicity annotation for the same CID — the **IARC Group 1 (established human carcinogen)** classification, the PAH-exposure / bladder-and-lung-cancer narrative, a co-carcinogenesis finding, and a lung-cancer epidemiology study. The CID bridge is the only thing connecting SPOKE's gene mechanism to PubChem's carcinogenicity narrative, which SPOKE does not store.

## SPARQL query executed
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sk: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?compound ?spokeGene (SUBSTR(?text,1,240) AS ?pubchemCarcinogenicityAnnotation) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref <http://identifiers.org/pubchem.compound/2336> ; rdfs:label ?compound ; sk:UPREGULATES_CuG ?g .
    ?g rdfs:label ?spokeGene . FILTER(?spokeGene = "TIPARP")
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID2336> ; oa:hasBody ?body .
    ?body rdf:value ?text .
    FILTER(CONTAINS(LCASE(?text),'carcinog') || CONTAINS(LCASE(?text),'tumor') || CONTAINS(LCASE(?text),'iarc'))
    FILTER(STRLEN(?text) > 120)
  }
} LIMIT 6
```

## Literature validation

According to PubMed, Rawal et al. (2026), *Med Sci (Basel)* — describes benzo[a]pyrene as "a ubiquitous polycyclic aromatic hydrocarbon from tobacco smoke, combustion, and dietary sources … a known carcinogen" and studies its effects on non-small-cell lung cancer behaviour, corroborating the PubChem IARC-Group-1 carcinogenicity annotations surfaced for the same compound. [PMID:42346841](https://pubmed.ncbi.nlm.nih.gov/42346841/) · [DOI](https://doi.org/10.3390/medsci14020301)

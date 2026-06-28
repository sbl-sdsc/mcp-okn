# Phenytoin: SPOKE epilepsy treatment edge paired with PubChem neuropharmacology / hepatotoxicity annotations

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations>

## Conversation
👤 **User**

For the anticonvulsant **phenytoin**, can I see — in one table — the neurological disease SPOKE records it treating AND the actual PubChem free-text pharmacology / toxicity annotation snippets for the same compound? I want the SPOKE clinical association and the PubChem hazard narrative together, on a CNS/neurodegeneration theme.

---
🧠 **Assistant**

spoke-okn places phenytoin in its clinical network via a `TREATS_CtD` edge to epilepsy but stores no free-text safety narrative; biobricks-pubchem-annotations holds PubChem's curated pharmacology/toxicity text but is keyed only on PubChem CID. SPOKE is the only federation KG that materializes PubChem CID, so the two join directly: SPOKE `oboInOwl:hasDbXref` → `identifiers.org/pubchem.compound/1775`, rewritten to `rdf.ncbi.nlm.nih.gov/pubchem/compound/CID1775`, the target of PubChem `oa:hasTarget` → `oa:hasBody` → `rdf:value` text.

**What each KG contributes:** spoke-okn → the named compound + its disease-treatment edge; biobricks-pubchem-annotations → the free-text pharmacology/hazard snippet SPOKE cannot express.

**Sample result** (Phenytoin, CID 1775):

| Compound (SPOKE) | SPOKE treats (disease) | PubChem annotation snippet |
|---|---|---|
| Phenytoin | epilepsy | "Phenytoin, formerly known as diphenylhydantoin, is a potent anticonvulsant used to treat and prevent generalized grand mal seizures, complex partial seizures and status epilepticus…" |
| Phenytoin | epilepsy | "Phenytoin is an Anti-epileptic Agent. The mechanism of action of phenytoin is as a Cytochrome P450 1A2 Inducer, and Cytochrome P450 2B6 Inducer…" |
| Phenytoin | epilepsy | "…phenytoin is one of the most common causes of clinically apparent drug induced liver disease and acute liver failure. More than 100 cases of liver injury due to phenytoin…" |
| Phenytoin | epilepsy | "…Murine cerebellar slice cultures /were used/ to study the influence of phenytoin on postnatal Purkinje cell axon differentiation…" |

**Why it answers the question:** each row pairs a real SPOKE clinical association (phenytoin TREATS epilepsy) with a real PubChem free-text annotation for the same CID — the anticonvulsant indication and seizure spectrum, the CYP-induction pharmacology, the well-documented hepatotoxicity hazard, and a CNS developmental-neurotoxicity study. The CID bridge is the only thing connecting "SPOKE epilepsy drug" to "its PubChem pharmacology/hazard narrative," which SPOKE itself does not hold.

## SPARQL query executed
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sk: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?compound ?disease (SUBSTR(?text,1,240) AS ?pubchemAnnotation) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref <http://identifiers.org/pubchem.compound/1775> ; rdfs:label ?compound ; sk:TREATS_CtD ?d .
    ?d rdfs:label ?disease . FILTER(?disease = "epilepsy")
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID1775> ; oa:hasBody ?body .
    ?body rdf:value ?text .
    FILTER(CONTAINS(LCASE(?text),'seizure') || CONTAINS(LCASE(?text),'neuro') || CONTAINS(LCASE(?text),'epilep') || CONTAINS(LCASE(?text),'toxic'))
    FILTER(STRLEN(?text) > 120)
  }
} LIMIT 6
```

## Literature validation

According to PubMed, Shlobin et al. (2025), *Neurology* — a Canadian Longitudinal Study on Aging analysis confirming phenytoin's use as a sodium-channel-blocker antiseizure medication in people with active epilepsy (and quantifying its cardiac-conduction-delay risk), validating SPOKE's phenytoin → epilepsy treatment edge and the PubChem anticonvulsant/safety annotations. [PMID:39899787](https://pubmed.ncbi.nlm.nih.gov/39899787/) · [DOI](https://doi.org/10.1212/WNL.0000000000210302)

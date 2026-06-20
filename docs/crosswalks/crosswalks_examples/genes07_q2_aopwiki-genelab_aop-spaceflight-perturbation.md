# CW7-Q2: AOPs ranked by spaceflight-differentially-expressed gene content

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>

## Conversation

👤 **User**

Crosswalk: biobricks-aopwiki × spoke-genelab on the shared Entrez gene id.

Research question: Rank adverse outcome pathways by how many of their key-event target genes are significantly differentially expressed in NASA GeneLab spaceflight assays. Which toxicity/disease pathways are most perturbed by spaceflight?

Why the join is required: the per-AOP count of spaceflight-responsive genes requires both AOP membership (AOP-Wiki) and the spaceflight differential-expression measurements (spoke-genelab); only the Entrez join lets you tally them.

---

🧠 **Assistant**

AOPs ranked by number of key-event genes significantly differentially expressed in spaceflight (adj. p < 0.05; top 15):

| AOP | # spaceflight-DE genes |
|---|---|
| Dysregulated prolonged TLR9 activation -> Multi Organ Failure / ARDS | 128 |
| SARS-CoV-2 binding to ACE2 -> acute respiratory distress mortality | 112 |
| SARS-CoV-2 binding to ACE2 -> hyperinflammation | 99 |
| Binding to ACE2 -> thrombosis and DIC | 83 |
| DNA damage and mutations -> Metastatic Breast Cancer | 75 |
| Deposition of energy -> abnormal vascular remodeling | 57 |

Why this answers the question: each AOP is paired with a count of its genes perturbed in spaceflight. The ranking is dominated by immune/inflammatory pathways (TLR9, multiple SARS-CoV-2/ACE2 AOPs) — consistent with the well-documented immune dysregulation of spaceflight — and includes the radiation-relevant "Deposition of energy -> abnormal vascular remodeling" AOP, fitting cosmic-radiation exposure. Computable only by the Entrez join between AOP membership and GeneLab expression.

Literature validation (PubMed): spaceflight immune dysregulation / altered gene expression in astronauts returns 7 records (e.g. PMIDs 31552089, 36203395); the TLR9/inflammatory lead AOP is itself literature-curated. The spaceflight-immune-perturbation theme is supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `biobricks-aopwiki`, `spoke-genelab`_

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?aopTitle (COUNT(DISTINCT ?gene) AS ?nSpaceflightDEGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
    ?ke <http://edamontology.org/data_1025> ?gnode .
    ?gnode skos:exactMatch ?e .
    FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?e),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.05)
  }
} GROUP BY ?aopTitle ORDER BY DESC(?nSpaceflightDEGenes) LIMIT 15
```

_15 row(s) — showing first 5_

| aopTitle | nSpaceflightDEGenes |
| --- | --- |
| Dysregulated prolonged Toll Like Receptor 9 (TLR9) activation leading to Multi Organ Failure involving Acute Respiratory Distress Syndrome (ARDS) | 128 |
| Binding of SARS-CoV-2 to ACE2 receptor leading to acute respiratory distress associated mortality | 112 |
| Binding of SARS-CoV-2 to ACE2 leads to hyperinflammation (via cell death) | 99 |
| Binding to ACE2 leading to thrombosis and disseminated intravascular coagulation | 83 |
|  DNA damage and mutations leading to Metastatic Breast Cancer | 75 |

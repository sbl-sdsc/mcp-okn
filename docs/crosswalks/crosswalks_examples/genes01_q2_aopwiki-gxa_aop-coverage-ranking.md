# CW1-Q2: Adverse outcome pathways ranked by target genes measured in GXA

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation

👤 **User**

Crosswalk: biobricks-aopwiki × gene-expression-atlas-okn on the shared Ensembl id.

Research question: Which adverse outcome pathways (AOPs) have the most key-event target genes that are actually catalogued/measured in the Gene Expression Atlas? This tells a toxicologist which AOPs are best covered by transcriptomic data for follow-up.

Why the join is required: AOP membership (which gene belongs to which adverse outcome pathway) lives only in AOP-Wiki; the catalog of genes actually measured in expression assays lives only in GXA. The coverage ranking is computable only by joining the two on the shared Ensembl id.

---

🧠 **Assistant**

Ranking of AOPs by the number of their key-event target genes present in the Gene Expression Atlas gene catalog (top 15):

| AOP | # target genes in GXA |
|---|---|
| Dysregulated prolonged TLR9 activation leading to Multi Organ Failure involving ARDS | 126 |
| Binding of SARS-CoV-2 to ACE2 leading to acute respiratory distress associated mortality | 94 |
| Binding of SARS-CoV-2 to ACE2 leads to hyperinflammation (via cell death) | 83 |
| DNA damage and mutations leading to Metastatic Breast Cancer | 73 |
| Binding to ACE2 leading to thrombosis and disseminated intravascular coagulation | 66 |
| Electrophilic binding to thiol/seleno-proteins impairing learning and memory | 64 |
| Interference with transthyretin causing neurodevelopmental toxicity | 61 |

Why this answers the question: each row is an adverse outcome pathway (from AOP-Wiki) paired with a count of its key-event genes that exist in the GXA expression catalog (from GXA) — a direct measure of transcriptomic coverage per pathway, obtainable only by the Ensembl join. The immune/inflammatory (TLR9, SARS-CoV-2/ACE2) and breast-cancer DNA-damage AOPs are the best-covered.

Literature validation (PubMed): the lead AOP's biology (TLR9 activation in acute respiratory distress syndrome) is supported by 17 PubMed records (e.g. PMIDs 35338116, 35354111). The AOPs themselves are literature-curated entries in AOP-Wiki.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `biobricks-aopwiki`, `gene-expression-atlas-okn`_

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?aopTitle (COUNT(DISTINCT ?gene) AS ?nGenesInGXA) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
    ?ke <http://edamontology.org/data_1025> ?gnode .
    ?gnode skos:exactMatch ?e .
    FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ensembl/'))
  }
  BIND(IRI(REPLACE(STR(?e),'https://identifiers.org/ensembl/','http://identifiers.org/ensembl/')) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?gene a biolink:Gene .
  }
} GROUP BY ?aopTitle ORDER BY DESC(?nGenesInGXA) LIMIT 15
```

_15 row(s) — showing first 5_

| aopTitle | nGenesInGXA |
| --- | --- |
| Dysregulated prolonged Toll Like Receptor 9 (TLR9) activation leading to Multi Organ Failure involving Acute Respiratory Distress Syndrome (ARDS) | 126 |
| Binding of SARS-CoV-2 to ACE2 receptor leading to acute respiratory distress associated mortality | 94 |
| Binding of SARS-CoV-2 to ACE2 leads to hyperinflammation (via cell death) | 83 |
|  DNA damage and mutations leading to Metastatic Breast Cancer | 73 |
| Binding to ACE2 leading to thrombosis and disseminated intravascular coagulation | 66 |

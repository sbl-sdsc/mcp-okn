# CW1-Q1: AOP target genes differentially expressed in GXA disease studies

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation

👤 **User**

Crosswalk: biobricks-aopwiki × gene-expression-atlas-okn, joined on the shared Ensembl gene identifier.

Research question: For genes that AOP-Wiki flags as key-event targets in adverse outcome pathways (toxicology/disease mechanisms), which are significantly differentially expressed in human disease studies in the Gene Expression Atlas, and in which direction?

Why the join is required: AOP-Wiki provides the mechanistic pathway membership of each gene (which adverse outcome pathway it belongs to) but contains no expression measurements. GXA provides differential-expression measurements (log2 fold-change, adjusted p-value, direction, disease context) but no AOP pathway annotation. Only by joining the two graphs on the shared Ensembl gene id can we ask "are the mechanistic AOP target genes actually dysregulated in disease?"

---

🧠 **Assistant**

Two AOP key-event target genes are significantly differentially expressed (adj. p < 0.01) in Gene Expression Atlas human disease studies, both upregulated in breast cancer:

| AOP | Gene | Disease | Direction | log2FC | adj. p |
|---|---|---|---|---|---|
| Binding to ACE2 leading to thrombosis and disseminated intravascular coagulation | F3 (tissue factor) | breast cancer | up | 1.0 | 1.9e-7 |
| Disruption of VEGFR Signaling Leading to Developmental Defects | FLT1 (VEGFR1) | breast cancer | up | 1.2 | 4.7e-5 |

Why these answer the question: F3 (coagulation-pathway tissue factor, the molecular anchor of the thrombosis/DIC AOP) and FLT1/VEGFR1 (the receptor at the center of the VEGFR-signaling AOP) are both pulled directly from AOP key events, and the join shows each is significantly upregulated in breast cancer expression contrasts in GXA — a result obtainable only by bridging mechanistic pathway membership (AOP-Wiki) to measured expression (GXA) on the Ensembl id.

Literature validation (PubMed): tissue factor / F3 over-expression in breast cancer is well documented (e.g. PMIDs 23534079, 34066023); FLT1/VEGFR1 expression in breast cancer returns 41 PubMed hits (e.g. PMIDs 23904188, 26261265). Both biological claims are literature-supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `biobricks-aopwiki`, `gene-expression-atlas-okn`_

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX wobd: <http://purl.org/okn/wobd/>
SELECT DISTINCT ?aopTitle ?symbol ?disName ?direction ?log2fc ?adjp WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
    ?ke <http://edamontology.org/data_1025> ?gnode .
    ?gnode skos:exactMatch ?e .
    FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ensembl/'))
  }
  BIND(IRI(REPLACE(STR(?e),'https://identifiers.org/ensembl/','http://identifiers.org/ensembl/')) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?gene biolink:symbol ?symbol .
    ?assoc biolink:object ?gene ; biolink:subject ?assay ;
           wobd:direction ?direction ; wobd:log2fc ?log2fc ; wobd:adj_p_value ?adjp .
    ?study biolink:has_output ?assay ; biolink:studies ?dis .
    ?dis biolink:name ?disName .
    FILTER(?adjp < 0.01)
  }
} ORDER BY ?adjp LIMIT 25
```

_2 row(s)_

| aopTitle | symbol | disName | direction | log2fc | adjp |
| --- | --- | --- | --- | --- | --- |
| Binding to ACE2 leading to thrombosis and disseminated intravascular coagulation | F3 | breast cancer | up | 1.0 | 1.866551e-07 |
| Disruption of VEGFR Signaling Leading to Developmental Defects | FLT1 | breast cancer | up | 1.2 | 4.67626e-05 |

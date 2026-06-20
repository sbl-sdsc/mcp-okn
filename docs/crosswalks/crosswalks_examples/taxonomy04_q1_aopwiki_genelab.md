# Taxonomy Crosswalk 4 Q1 — AOP-Wiki × SPOKE-GeneLab (toxicology meets spaceflight omics)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Which model organisms are used BOTH as AOP-Wiki toxicology test species AND in NASA GeneLab spaceflight omics (spoke-genelab)? For each, how many AOP key events apply and how many genes were profiled in spaceflight experiments? Join biobricks-aopwiki and spoke-genelab on the shared NCBITaxon id.

---

🧠 **Assistant**

Joining AOP-Wiki key-event taxonomic applicability to spoke-genelab model-organism genes (`schema:taxonomy` NCBITaxon) on the shared id returns **7 organisms in both graphs** (matching the exact-id overlap of 7):

- **Homo sapiens** — 94 AOP key events; 29,069 GeneLab spaceflight genes
- **Mus musculus** — 207 AOP key events; 27,519 genes
- **Arabidopsis thaliana** — 1 AOP key event; 25,466 genes
- **Caenorhabditis elegans** — 3 AOP key events; 17,464 genes
- **Danio rerio** — 8 AOP key events; 17,143 genes
- **Rattus norvegicus** — 182 AOP key events; 6,254 genes
- **Saccharomyces cerevisiae** — 3 AOP key events; 86 genes

These are the model species where terrestrial mechanistic toxicology (AOP-Wiki adverse outcome pathways) and spaceflight functional genomics (NASA GeneLab) describe the SAME organism, so the two evidence bases can be cross-analyzed (e.g. whether spaceflight-perturbed genes map onto AOP key events). The result depends entirely on the NCBITaxon join.

**Literature validation (PubMed):** NASA GeneLab / Open Science Data Repository spaceflight transcriptomics in mouse and other model organisms is an established literature — a PubMed search returns 7 articles (e.g. PMID 33080015, 30688299, 38862516, 29520055). Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?taxName (COUNT(DISTINCT ?ke) AS ?aopKEs) (COUNT(DISTINCT ?gene) AS ?geneLabSpaceflightGenes)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ke a aop:KeyEvent ; <http://purl.obolibrary.org/obo/NCBITaxon_131567> ?te . ?te dc:identifier ?tax .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene gls:taxonomy ?taxStr . BIND(IRI(?taxStr) AS ?tax)
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?tax rdfs:label ?taxName }
}
GROUP BY ?tax ?taxName ORDER BY DESC(?geneLabSpaceflightGenes)
```

### Results (7 rows)

| taxName | aopKEs | geneLabSpaceflightGenes |
| --- | --- | --- |
| Homo sapiens | 94 | 29069 |
| Mus musculus | 207 | 27519 |
| Arabidopsis thaliana | 1 | 25466 |
| Caenorhabditis elegans | 3 | 17464 |
| Danio rerio | 8 | 17143 |
| Rattus norvegicus | 182 | 6254 |
| Saccharomyces cerevisiae | 3 | 86 |

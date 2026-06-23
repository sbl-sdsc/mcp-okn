# Taxonomy Crosswalk 7 Q1 — Gene Expression Atlas × SPOKE-GeneLab (ground vs space)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Which model organisms have gene-expression data in BOTH the (terrestrial) Gene Expression Atlas AND NASA GeneLab spaceflight omics (spoke-genelab)? For each, how many GXA studies and how many GeneLab spaceflight genes? Join gene-expression-atlas-okn and spoke-genelab on the shared NCBITaxon id.

---

🧠 **Assistant**

Joining GXA (`biolink:in_taxon`) to spoke-genelab (`schema:taxonomy`) on the shared NCBITaxon id returns **8 model organisms** present in both expression resources (matching the exact-id overlap of 8):

- **Homo sapiens** — 1,671 GXA studies; 29,069 GeneLab spaceflight genes
- **Mus musculus** — 1,323 GXA studies; 27,519 genes
- **Arabidopsis thaliana** — 638 GXA studies; 25,466 genes
- **Rattus norvegicus** — 188 GXA studies; 6,254 genes
- **Drosophila melanogaster** — 150 GXA studies; 15,946 genes
- **Saccharomyces cerevisiae** — 54 GXA studies; 86 genes
- **Caenorhabditis elegans** — 34 GXA studies; 17,464 genes
- **Danio rerio** — 27 GXA studies; 17,143 genes

These eight organisms have transcriptomic coverage both on the ground (GXA) and in spaceflight (GeneLab), so for each one a researcher can directly compare baseline/terrestrial expression with spaceflight-perturbed expression. The result depends entirely on the shared NCBITaxon organism id.

**Literature validation (PubMed):** spaceflight transcriptomics in these model organisms is established — e.g. Arabidopsis spaceflight gene-expression returns 22 PubMed articles (PMID 33668919, 30866818, 32265943, 35007950). Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?taxName ?gxaStudies ?genelabSpaceflightGenes WHERE {
  { SELECT ?tax (COUNT(DISTINCT ?study) AS ?gxaStudies) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?study biolink:in_taxon ?tax } }
    GROUP BY ?tax }
  { SELECT ?tax (COUNT(DISTINCT ?gene) AS ?genelabSpaceflightGenes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?gene gls:taxonomy ?ts . BIND(IRI(?ts) AS ?tax) } }
    GROUP BY ?tax }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?tax rdfs:label ?taxName }
}
ORDER BY DESC(?gxaStudies)
```

### Results (8 rows)

| taxName | gxaStudies | genelabSpaceflightGenes |
| --- | --- | --- |
| Homo sapiens | 1671 | 29069 |
| Mus musculus | 1323 | 27519 |
| Arabidopsis thaliana | 638 | 25466 |
| Rattus norvegicus | 188 | 6254 |
| Drosophila melanogaster | 150 | 15946 |
| Saccharomyces cerevisiae | 54 | 86 |
| Caenorhabditis elegans | 34 | 17464 |
| Danio rerio | 27 | 17143 |

# Taxonomy Crosswalk 4 Q2 — Mouse AOP coverage + spaceflight DE genes

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>

## Conversation

👤 **User**

Mouse (Mus musculus, NCBITaxon:10090) is both an AOP-Wiki toxicology test species and a NASA GeneLab spaceflight model. How many AOP key events apply to mouse, and what are the top spaceflight differentially-expressed mouse genes (largest |log2FC|, FDR<1e-4)? Join biobricks-aopwiki and spoke-genelab on NCBITaxon:10090.

---

🧠 **Assistant**

Joining on NCBITaxon:10090 confirms mouse is the integration point: AOP-Wiki assigns **207 key events** to mouse, and spoke-genelab records its spaceflight differential-expression measurements. The most strongly spaceflight-perturbed mouse genes (|log2FC| ranked, FDR < 1e-4) are: **Gvin-ps4** (|log2FC| 51.8, adj-p 5e-205), **Fam177a** (51.1), **Pde2a** (51.0), **Rpl7a-ps11** (50.7), **Gm44502** (50.0), **Gm32687** (50.0, adj-p 7e-291), **Fam177a2** (49.8), **Snord3b3** (49.3).

The rows answer the question and demonstrate the value of the join: the same organism carries 207 mechanistic toxicology key events (AOP-Wiki) AND concrete spaceflight transcriptomic responses (spoke-genelab). A researcher can now ask whether spaceflight-responsive genes (e.g. the cyclic-nucleotide phosphodiesterase *Pde2a*) intersect AOP key-event mechanisms — a question neither KG can answer alone. The result depends entirely on the shared NCBITaxon organism id.

**Literature validation (PubMed):** NASA GeneLab mouse spaceflight transcriptomics is established (e.g. PMID 33080015, 30688299, 38862516); the differential-expression measurements joined here come from that program. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mouseAOPkeyEvents ?spaceflightGene (MAX(ABS(?log2fc)) AS ?maxAbsLog2FC) (MIN(?adj_p_value) AS ?bestAdjP) WHERE {
  { SELECT (COUNT(DISTINCT ?ke) AS ?mouseAOPkeyEvents) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?ke a aop:KeyEvent ; <http://purl.obolibrary.org/obo/NCBITaxon_131567> ?te .
        ?te dc:identifier <http://purl.obolibrary.org/obo/NCBITaxon_10090> . } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene gls:taxonomy ?t ; gls:symbol ?spaceflightGene .
    FILTER(STR(?t) = 'http://purl.obolibrary.org/obo/NCBITaxon_10090')
    ?stmt rdf:subject ?assay ; rdf:predicate gls:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          gls:log2fc ?log2fc ; gls:adj_p_value ?adj_p_value .
    FILTER(?adj_p_value < 0.0001)
  }
}
GROUP BY ?mouseAOPkeyEvents ?spaceflightGene
ORDER BY DESC(?maxAbsLog2FC) LIMIT 8
```

### Results (8 rows)

| mouseAOPkeyEvents | spaceflightGene | maxAbsLog2FC | bestAdjP |
| --- | --- | --- | --- |
| 207 | Gvin-ps4 | 51.79 | 4.96e-205 |
| 207 | Fam177a | 51.08 | 9.63e-86 |
| 207 | Pde2a | 50.95 | 2.28e-20 |
| 207 | Rpl7a-ps11 | 50.72 | 4.74e-50 |
| 207 | Gm44502 | 50.02 | 9.06e-75 |
| 207 | Gm32687 | 49.97 | 7.05e-291 |
| 207 | Fam177a2 | 49.76 | 3.78e-37 |
| 207 | Snord3b3 | 49.31 | 3.37e-58 |

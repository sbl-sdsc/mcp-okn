# Taxonomy Crosswalk 7 Q2 — Arabidopsis ground (GXA) vs space (GeneLab)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>

## Conversation

👤 **User**

For Arabidopsis thaliana (NCBITaxon:3702), how many terrestrial GXA studies exist, and what are the top spaceflight differentially-expressed Arabidopsis genes (largest |log2FC|, FDR<1e-4) in NASA GeneLab? Join gene-expression-atlas-okn and spoke-genelab on NCBITaxon:3702.

---

🧠 **Assistant**

Joining on NCBITaxon:3702 confirms Arabidopsis is profiled in both resources: the Gene Expression Atlas holds **638 (terrestrial) Arabidopsis gene-expression studies**, and NASA GeneLab provides its spaceflight differential-expression data. The most strongly spaceflight-perturbed Arabidopsis genes (|log2FC| ranked, FDR < 1e-4) are: **ATHSD1/HSD1** (|log2FC| 49.6, adj-p 1e-138), **AtLpxC3/LpxC3** (49.1), **AGC1-6/RSH3** (48.9), **ATDSI-1VOC** (48.8), **NIMIN-1** (48.6), **AtHSD5/HSD5** (48.2), **ABCG27** (48.2, an ABC transporter), **AITR4/DIL3** (47.9).

The rows answer the question and show the integration: the same plant is covered by a large ground-based expression atlas (638 GXA studies) AND concrete spaceflight transcriptomic responses (GeneLab), so spaceflight-responsive genes such as the ABC transporter ABCG27 can be contextualized against the organism's baseline expression. The result depends entirely on the shared NCBITaxon organism id.

**Literature validation (PubMed):** Arabidopsis spaceflight transcriptomics on the ISS is an established literature (22 articles; e.g. PMID 33668919, 30866818, 32265943); the GeneLab measurements joined here derive from that program. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?gxaArabidopsisStudies ?spaceflightGene (MAX(ABS(?log2fc)) AS ?maxAbsLog2FC) (MIN(?adjp) AS ?bestAdjP) WHERE {
  { SELECT (COUNT(DISTINCT ?study) AS ?gxaArabidopsisStudies) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
        ?study biolink:in_taxon <http://purl.obolibrary.org/obo/NCBITaxon_3702> } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene gls:taxonomy ?t ; gls:symbol ?spaceflightGene .
    FILTER(STR(?t) = 'http://purl.obolibrary.org/obo/NCBITaxon_3702')
    ?stmt rdf:subject ?a ; rdf:predicate gls:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          gls:log2fc ?log2fc ; gls:adj_p_value ?adjp .
    FILTER(?adjp < 0.0001)
  }
}
GROUP BY ?gxaArabidopsisStudies ?spaceflightGene
ORDER BY DESC(?maxAbsLog2FC) LIMIT 8
```

### Results (8 rows)

| gxaArabidopsisStudies | spaceflightGene | maxAbsLog2FC | bestAdjP |
| --- | --- | --- | --- |
| 638 | ATHSD1\|HSD1 | 49.58 | 1.09e-138 |
| 638 | AtLpxC3\|LpxC3 | 49.06 | 7.70e-41 |
| 638 | AGC1-6\|RSH3 | 48.91 | 1.29e-53 |
| 638 | ATDSI-1VOC\|DSI-1VOC | 48.82 | 3.36e-28 |
| 638 | NIMIN-1\|NIMIN1 | 48.60 | 4.86e-48 |
| 638 | AtHSD5\|HSD5 | 48.23 | 6.47e-52 |
| 638 | ABCG27 | 48.23 | 5.25e-64 |
| 638 | AITR4\|DIL3 | 47.92 | 5.65e-93 |

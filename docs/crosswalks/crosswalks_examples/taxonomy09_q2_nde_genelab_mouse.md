# Taxonomy Crosswalk 9 Q2 — Mouse spaceflight omics + NDE disease datasets

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `nde` — <https://purl.org/okn/frink/kg/nde>

## Conversation

👤 **User**

Mouse (Mus musculus, NCBITaxon:10090) is NASA's primary mammalian spaceflight model and a major biomedical disease model. How many mouse genes are measured as significantly differentially expressed in spaceflight (spoke-genelab, FDR<0.05), and how many NDE disease datasets / which conditions involve mouse? Join spoke-genelab and nde on NCBITaxon:10090.

---

🧠 **Assistant**

Joining on NCBITaxon:10090 gives the integrated mouse profile bridging space and disease data: spoke-genelab records **26,540 mouse genes** significantly differentially expressed in spaceflight (FDR < 0.05), and the NIAID Data Ecosystem holds **84,069 mouse disease datasets**. The NDE health-condition annotations span a very wide disease ontology (examples returned alphabetically include 2-hydroxyglutaric aciduria, 22q11.2 deletion syndrome, abdominal aortic aneurysm, and many others).

The row answers the question: the same organism carries a massive spaceflight transcriptomic response (26,540 DE genes) AND an enormous terrestrial disease-dataset collection (84,069 datasets). The join lets astronaut-health and disease-modeling researchers connect spaceflight-perturbed mouse genes to the disease datasets defined for the same species — a question neither KG answers alone. The result depends entirely on the shared NCBITaxon organism id.

**Literature validation (PubMed):** spaceflight immune dysregulation and disease-relevant changes in the mouse model are documented (e.g. PMID 30018614, 24462949); NASA GeneLab mouse spaceflight transcriptomics (e.g. PMID 33080015) underlies the differential-expression measurements. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mouseSpaceflightDEgenes ?mouseNDEdatasets ?exampleConditions WHERE {
  { SELECT (COUNT(DISTINCT ?gene) AS ?mouseSpaceflightDEgenes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?gene gls:taxonomy ?t . FILTER(STR(?t)='http://purl.obolibrary.org/obo/NCBITaxon_10090')
        ?stmt rdf:predicate gls:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ; gls:adj_p_value ?adjp .
        FILTER(?adjp < 0.05) } } }
  { SELECT (COUNT(DISTINCT ?ds) AS ?mouseNDEdatasets) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nde> { ?ds schema:species ?sp . FILTER(REGEX(STR(?sp),'/taxonomy/10090($|[^0-9])')) } } }
  { SELECT (GROUP_CONCAT(?c; separator=" | ") AS ?exampleConditions) WHERE {
      { SELECT DISTINCT ?c WHERE {
          GRAPH <https://purl.org/okn/frink/kg/nde> {
            ?ds schema:species ?sp . FILTER(REGEX(STR(?sp),'/taxonomy/10090($|[^0-9])'))
            ?ds schema:healthCondition ?hc . ?hc schema:name ?c } } LIMIT 10 } } }
}
```

### Result (1 row)

| mouseSpaceflightDEgenes | mouseNDEdatasets | exampleConditions |
| --- | --- | --- |
| 26540 | 84069 | 2-hydroxyglutaric aciduria \| 22q11.2 deletion syndrome \| 3MC syndrome 2 \| 3q26 microduplication syndrome \| 4-layered lissencephaly \| 46,XY sex reversal 11 \| 49,XXXXY syndrome \| 7q11.23 microduplication syndrome \| Aarskog-Scott syndrome, X-linked \| abdominal aortic aneurysm |

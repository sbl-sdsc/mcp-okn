# Oxidative-stress / ROS / DNA-damage / genotoxicity AOP key-event genes (clean spaceflight contrast)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>

## Conversation
👤 **User**

Which key-event genes of AOPs for **oxidative stress, reactive-oxygen-species toxicity, and DNA-damage genotoxicity** (including the ionizing-radiation → DNA-damage pathway) are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction? This targets the cosmic-radiation / oxidative axis of astronaut risk without the confounded assays.

---
🧠 **Assistant**

AOP-Wiki defines which genes are mechanistic key events of oxidative/genotoxic pathways but has no spaceflight data; spoke-genelab has the spaceflight differential-expression measurements but no AOP annotation. Only the Entrez join links a genotoxicity pathway target to a measured, unconfounded spaceflight stress response.

**Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.

**Sample result** (6 of 15):

| AOP | Gene | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| Ionizing radiation-induced DNA damage → microcephaly via apoptosis | CDKN1A | -3.05 (down) | 2.1e-132 |
| Chronic reactive oxygen species → treatment-resistant gastric cancer | CYP1B1 | -2.48 (down) | 6.1e-63 |
| DNA damage & mutations → metastatic breast cancer | SNAI1 | +2.52 (up) | 3.8e-45 |
| Increased DNA damage → increased risk of breast cancer | CENPJ | +3.21 (up) | 5.8e-44 |
| DNA damage & mutations → metastatic breast cancer | RHOB | -2.21 (down) | 2.7e-40 |
| Activation of reactive oxygen species → atherosclerosis | CCL2 | -2.58 (down) | 6.4e-38 |

**Why it answers the question:** every gene is a curated key event in an oxidative-stress / ROS / DNA-damage AOP — including the **ionizing-radiation → DNA-damage** pathway directly relevant to cosmic radiation, whose effector **CDKN1A (p21)**, the canonical p53/DNA-damage cell-cycle-arrest gene, is strongly DE — and each is significantly DE in an unconfounded Space-Flight-vs-Ground-Control contrast, so the genotoxic/redox signal (CENPJ, RHOB, CYP1B1, SNAI1, CCL2) is microgravity-driven, not a co-varying factor.

## SPARQL query executed
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT DISTINCT ?aopTitle ?symbol (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  {
    SELECT DISTINCT ?gene ?aopTitle WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
        ?ke <http://edamontology.org/data_1025> ?gnode .
        ?gnode skos:exactMatch ?e .
        FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/'))
        FILTER(CONTAINS(LCASE(?aopTitle),'oxidative') || CONTAINS(LCASE(?aopTitle),'dna damage')
            || CONTAINS(LCASE(?aopTitle),'genotox') || CONTAINS(LCASE(?aopTitle),'reactive oxygen'))
      }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?e),'^.*/ncbigene/',''))) AS ?gene)
    }
  }
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    ?gene sg:symbol ?symbol .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?aopTitle ?symbol ORDER BY ?minAdjP LIMIT 15
```

## Literature validation

Beck et al., 2014, *Int J Mol Med* — chronic simulated space conditions (microgravity + low-dose ionizing radiation) predominantly induce oxidative-stress-responsive (Nrf2-target) genes and alter DNA-damage-response pathways in mammalian cells. [PMID:24859186](https://pubmed.ncbi.nlm.nih.gov/24859186/) · [DOI](https://doi.org/10.3892/ijmm.2014.1785)

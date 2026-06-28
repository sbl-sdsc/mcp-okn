# Immune / inflammatory / autoimmune disease genes (clean spaceflight contrast)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

Which genes most strongly differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast are associated in SPOKE with **immune, inflammatory and autoimmune disease** (rheumatoid arthritis, psoriasis, asthma, inflammatory bowel disease, lupus, multiple sclerosis)? This probes the immune-dysregulation system using only confounder-free assays.

---
🧠 **Assistant**

spoke-genelab has clean spaceflight expression but no curated gene–disease associations; spoke-okn has the gene–disease associations but no spaceflight data. The direct Entrez join links an unconfounded spaceflight transcriptional response to its immune-disease relevance.

**Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.

**Sample result** (8 of 15):

| Gene | SPOKE immune/inflammatory disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| MMP3 | rheumatoid arthritis; osteoarthritis | -7.94 (down) | 7.9e-201 |
| DPP4 | asthma; rheumatoid arthritis | -5.16 (down) | 2.7e-111 |
| NEFL | multiple sclerosis | -6.97 (down) | 2.5e-62 |
| RCAN1 | rheumatoid arthritis | -2.44 (down) | 2.2e-54 |
| FAS | rheumatoid arthritis; inflammatory bowel disease | -2.26 (down) | 4.8e-52 |
| ADAMTS5 | osteoarthritis | -3.18 (down) | 7.4e-52 |
| TFRC | asthma | -2.34 (down) | 3.2e-51 |
| CARD11 | asthma; inflammatory bowel disease | +3.29 (up) | 1.1e-50 |

**Why it answers the question:** under a confounder-free Space-Flight-vs-Ground-Control contrast, the most strongly perturbed genes carrying SPOKE immune-disease associations are bona-fide inflammatory effectors — the matrix metalloproteinase MMP3 and aggrecanase ADAMTS5 (joint-destruction enzymes in arthritis, strongly down), DPP4, the death receptor FAS (RA/IBD), the MS axonal marker NEFL, and the NF-κB-activating CBM-complex scaffold CARD11 (up; asthma/IBD) — mapping a clean spaceflight transcriptional response onto autoimmune/inflammatory disease, consistent with documented spaceflight immune dysregulation. (Note: MMP3 here is strongly *down* in clean contrasts — the opposite sign to the earlier confounded version, illustrating why the contrast matters.)

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?spokeDisease (MAX(?lfc) AS ?maxLog2fc) (MIN(?lfc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
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
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 1.0e-10)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?gene rdfs:label ?sym .
    ?d spoke:ASSOCIATES_DaG ?gene ; rdfs:label ?spokeDisease .
    FILTER(CONTAINS(LCASE(?spokeDisease),'arthritis') || CONTAINS(LCASE(?spokeDisease),'lupus')
        || CONTAINS(LCASE(?spokeDisease),'psoriasis') || CONTAINS(LCASE(?spokeDisease),'asthma')
        || CONTAINS(LCASE(?spokeDisease),'inflammatory bowel') || CONTAINS(LCASE(?spokeDisease),'crohn')
        || CONTAINS(LCASE(?spokeDisease),'colitis') || CONTAINS(LCASE(?spokeDisease),'multiple sclerosis')
        || CONTAINS(LCASE(?spokeDisease),'autoimmune'))
  }
} GROUP BY ?sym ?spokeDisease ORDER BY ?minAdjP LIMIT 15
```

## Literature validation

Cools et al., 2026, *Prog Biophys Mol Biol* — review of microgravity effects on human physiology documents immune dysregulation as a core, persistent spaceflight adaptation across organ systems. [PMID:42162925](https://pubmed.ncbi.nlm.nih.gov/42162925/) · [DOI](https://doi.org/10.1016/j.pbiomolbio.2026.05.004)

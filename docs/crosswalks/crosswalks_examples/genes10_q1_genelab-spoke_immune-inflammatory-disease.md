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

**Spaceflight contrast:** Space Flight vs Ground Control on the same material, with all other factors *balanced* across the two arms — the `mcp-okn` server's `spoke-genelab` Rule 1 (direction via `factor_space_1/2`) + Rule 2 (comparability — arms differ only in the condition after stripping balanced shared factors/group codes), replacing the earlier strict "factor arrays contain only the condition label" filter. Rule 2 grows the genome-wide clean-contrast pool from 56 to 127 assays and surfaces three additional asthma-associated genes (TSPAN8, CYFIP2, SUGCT, all strongly down) in the top eight.

**Sample result** (8 of 15):

| Gene | SPOKE immune/inflammatory disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| MMP3 | rheumatoid arthritis; osteoarthritis | -7.94 (down) | 7.9e-201 |
| DPP4 | asthma; rheumatoid arthritis | -5.16 (down) | 2.7e-111 |
| TSPAN8 | asthma | -4.68 (down) | 3.6e-78 |
| CYFIP2 | asthma | -3.25 (down) | 6.5e-74 |
| NEFL | multiple sclerosis | -6.97 (down) | 2.5e-62 |
| SUGCT | asthma | -4.80 (down) | 1.3e-56 |
| RCAN1 | rheumatoid arthritis | -2.44 (down) | 2.2e-54 |
| FAS | rheumatoid arthritis; inflammatory bowel disease | -2.26 (down) | 4.8e-52 |

**Why it answers the question:** under confounder-free, *balanced* Space-Flight-vs-Ground-Control contrasts (the server's Rule 2), the most strongly perturbed genes carrying SPOKE immune-disease associations are bona-fide inflammatory effectors — the matrix metalloproteinase MMP3 and aggrecanase ADAMTS5 (joint-destruction enzymes in arthritis, strongly down), the dipeptidyl-peptidase DPP4, the death receptor FAS (RA/IBD), the MS axonal marker NEFL, and the asthma-associated set TSPAN8/CYFIP2/SUGCT (all down, newly surfaced once Rule 2 admits the balanced contrasts) — mapping a clean spaceflight transcriptional response onto autoimmune/inflammatory disease, consistent with documented spaceflight immune dysregulation. (Note: MMP3 here is strongly *down* in clean contrasts — the opposite sign to the earlier confounded version, illustrating why the contrast matters.)

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
        # Rule 2 comparability: arms differ ONLY in the condition (extra factors balanced across both arms)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?x .
          FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
            && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay sg:factors_2 ?x } }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?y .
          FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
            && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay sg:factors_1 ?y } }
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

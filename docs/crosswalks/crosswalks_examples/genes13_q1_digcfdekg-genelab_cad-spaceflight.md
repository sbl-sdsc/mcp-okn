# Coronary-artery-disease (CAD) factor genes (clean spaceflight contrast)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>

## Conversation
👤 **User**

Long-duration spaceflight raises cardiovascular-disease concern. Which genes CFDE REVEAL infers as relevant to **coronary artery disease (CAD)** (trait `449de16e8049af35333b`) are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction — do the genes underlying CAD genetic risk show up as genuinely microgravity-responsive?

---
🧠 **Assistant**

digcfdekg supplies the PIGEAN CAD gene-relevance scores; spoke-genelab supplies clean spaceflight differential expression but has no disease-relevance concept. Identifying which CAD-relevant genes are genuinely microgravity-responsive needs the Entrez join plus the confounder-free contrast.

**Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.

**Sample result** (8 of 15):

| Gene | PIGEAN (CAD) | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| APOE | 10.9 | +2.05 (up) | 2.6e-12 |
| SCARB1 | 9.73 | +0.92 (up) | 5.7e-7 |
| PCSK9 | 8.86 | -1.15 (down) | 1.7e-4 |
| LIPA | 7.88 | -1.13 (down) | 7.1e-14 |
| SMAD3 | 7.62 | +1.61 (up) | 1.7e-32 |
| EDNRA | 5.67 | -2.05 (down) | 8.9e-13 |
| TCF21 | 5.63 | -2.03 (down) | 1.0e-13 |
| LIPG | 5.56 | -2.21 (down) | 8.5e-16 |

**Why it answers the question:** the intersection is the canonical lipid/atherosclerosis machinery — the highest-confidence CFDE CAD genes APOE, SCARB1, PCSK9, LIPA, LIPG — joined by the vascular-remodeling factors SMAD3 (TGF-β), EDNRA (endothelin receptor) and the coronary-artery transcription factor TCF21, every one significantly DE in an unconfounded Space-Flight-vs-Ground-Control contrast (APOE up, PCSK9 down), giving confounder-free molecular evidence that microgravity perturbs the genetic circuitry of coronary disease.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?sym ?pigeanScore (MAX(?lfc) AS ?maxLog2fc) (MIN(?lfc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) (COUNT(DISTINCT ?assay) AS ?nCleanAssays) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <https://purl.org/okn/frink/kg/digcfdekg/node/trait/449de16e8049af35333b> ;
        rdf:subject ?gene ; dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 3.0)
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
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 15
```

## Literature validation

Robin et al., 2023, *Nat Commun* — dry-immersion microgravity simulation rapidly induced a metabolic-syndrome-like shift with an increased atherogenic index of plasma and impaired lipid profile, alongside cardiovascular deconditioning. [PMID:37813884](https://pubmed.ncbi.nlm.nih.gov/37813884/) · [DOI](https://doi.org/10.1038/s41467-023-41990-4)

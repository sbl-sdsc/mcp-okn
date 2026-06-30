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

**Spaceflight contrast:** Space Flight vs Ground Control on the same material, with all other factors *balanced* across the two arms — the `mcp-okn` server's `spoke-genelab` Rule 1 (direction via `factor_space_1/2`) + Rule 2 (comparability — arms differ only in the condition after stripping balanced shared factors/group codes), replacing the earlier strict "factor arrays contain only the condition label" filter. Rule 2 grows the clean-contrast pool from 56 to 127 assays and now shows **LDLR (9.48), VEGFA (7.9) and TGFB1 (7.2)** — among the highest-confidence CFDE CAD genes — to be microgravity-responsive, so the full LDL/cholesterol-handling axis (APOE, LDLR, PCSK9, LIPA, SCARB1) is recovered.

**Sample result** (8 of 15):

| Gene | PIGEAN (CAD) | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| APOE | 10.9 | +2.05 (up) | 2.6e-12 |
| SCARB1 | 9.73 | +0.92 (up) | 5.7e-7 |
| LDLR | 9.48 | +1.04 / -1.43 | 8.1e-5 |
| PCSK9 | 8.86 | -1.15 (down) | 1.7e-4 |
| VEGFA | 7.9 | +3.85 / +0.92 | 2.9e-7 |
| LIPA | 7.88 | -1.13 (down) | 7.1e-14 |
| SMAD3 | 7.62 | +1.86 / -0.59 | 1.7e-32 |
| TGFB1 | 7.2 | +1.41 (up) | 5.4e-3 |

**Why it answers the question:** the intersection is the canonical lipid/atherosclerosis machinery — the highest-confidence CFDE CAD genes of the LDL/cholesterol axis (APOE, LDLR, PCSK9, LIPA, SCARB1) — joined by the vascular-remodeling/angiogenesis factors SMAD3 and TGFB1 (TGF-β) and VEGFA, every one significantly DE in confounder-free, *balanced* Space-Flight-vs-Ground-Control contrasts (APOE up, PCSK9 down), giving evidence that microgravity perturbs the genetic circuitry of coronary disease. Adopting the server's Rule 2 (which restores the balanced contrasts the strict filter dropped) brings the top-ranked LDLR, VEGFA and TGFB1 into view alongside the lower-ranked EDNRA/TCF21/LIPG seen before.

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
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 15
```

## Literature validation

Robin et al., 2023, *Nat Commun* — dry-immersion microgravity simulation rapidly induced a metabolic-syndrome-like shift with an increased atherogenic index of plasma and impaired lipid profile, alongside cardiovascular deconditioning. [PMID:37813884](https://pubmed.ncbi.nlm.nih.gov/37813884/) · [DOI](https://doi.org/10.1038/s41467-023-41990-4)

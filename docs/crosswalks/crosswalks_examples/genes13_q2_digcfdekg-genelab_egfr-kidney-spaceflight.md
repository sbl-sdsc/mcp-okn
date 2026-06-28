# Glomerular-filtration-rate (eGFR / kidney-function) factor genes responsive to clean spaceflight

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>

## Conversation
👤 **User**

"Cosmic kidney disease" and microgravity fluid shifts make renal function a priority risk. Which genes CFDE REVEAL infers as relevant to **glomerular filtration rate (eGFR / kidney function, OBA_0003747)** are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction?

---
🧠 **Assistant**

digcfdekg supplies the PIGEAN eGFR gene-relevance scores; spoke-genelab supplies clean spaceflight differential expression but has no trait-relevance concept. Identifying which kidney-function genes are genuinely microgravity-responsive needs the Entrez join plus the confounder-free contrast.

**Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.

**Sample result** (8 of 15):

| Gene | PIGEAN (eGFR) | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| SALL1 | 6.27 | -1.18 (down) | 3.4e-5 |
| SLC15A2 | 6.15 | +3.25 (up) | 1.4e-10 |
| SHH | 6.11 | -2.48 (down) | 3.5e-5 |
| SLC47A1 | 5.98 | -2.38 (down) | 2.7e-5 |
| REN | 4.56 | +6.44 (up) | 4.2e-10 |
| MAF | 4.48 | -6.49 (down) | 4.2e-13 |
| PAX8 | 4.34 | -3.78 (down) | 3.3e-39 |
| PKD1 | 4.20 | +0.48 (up) | 1.2e-3 |

**Why it answers the question:** the intersection is the core kidney-function machinery — **REN (renin) strongly up (+6.44)** in the clean contrast, renal solute transporters SLC15A2/SLC47A1, kidney developmental factors SALL1/PAX8/SHH, and the polycystic-kidney gene PKD1 — tying eGFR genetics to confounder-free microgravity perturbation; the renin up-regulation is the expected direction for spaceflight RAAS activation.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?sym ?pigeanScore (MAX(?lfc) AS ?maxLog2fc) (MIN(?lfc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) (COUNT(DISTINCT ?assay) AS ?nCleanAssays) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/OBA_0003747> ;
        rdf:subject ?gene ; dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 4.0)
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

Norsk, 2000, *Pflügers Archiv* ("Renal adjustments to microgravity") — spaceflight attenuates renal fluid excretion and elevates the renin–angiotensin–aldosterone axis, the physiological correlate of the up-regulated REN seen here. [PMID:11200982](https://pubmed.ncbi.nlm.nih.gov/11200982/) · [DOI](https://doi.org/10.1007/s004240000332)

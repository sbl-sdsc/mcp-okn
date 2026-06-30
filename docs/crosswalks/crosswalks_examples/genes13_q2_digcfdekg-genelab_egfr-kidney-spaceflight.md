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

**Spaceflight contrast:** Space Flight vs Ground Control on the same material, with all other factors *balanced* across the two arms — the `mcp-okn` server's `spoke-genelab` Rule 1 (direction via `factor_space_1/2`) + Rule 2 (comparability — arms differ only in the condition after stripping balanced shared factors/group codes), replacing the earlier strict "factor arrays contain only the condition label" filter. Rule 2 grows the clean-contrast pool from 56 to 127 assays and brings the highest-confidence kidney-function genes **PKHD1 (7.55, the autosomal-recessive polycystic-kidney gene), VEGFA (7.03) and CYP24A1** into the top eight; the renin gene **REN** (PIGEAN 4.56, +6.44 up) remains, lower in the ranking.

**Sample result** (8 of 15):

| Gene | PIGEAN (eGFR) | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| PKHD1 | 7.55 | -1.01 (down) | 1.6e-5 |
| VEGFA | 7.03 | +3.85 / +0.92 | 2.9e-7 |
| SALL1 | 6.27 | -1.18 (down) | 3.4e-5 |
| SLC15A2 | 6.15 | +3.25 (up) | 1.4e-10 |
| CDKN1C | 6.12 | +0.96 (up) | 9.1e-4 |
| SHH | 6.11 | -2.48 (down) | 3.5e-5 |
| SLC47A1 | 5.98 | -2.38 (down) | 2.7e-5 |
| CYP24A1 | 5.91 | +1.30 (up) | 9.1e-6 |

**Why it answers the question:** the intersection is the core kidney-function machinery — the polycystic-kidney genes **PKHD1** and PKD1, the angiogenesis factor VEGFA, renal solute transporters SLC15A2/SLC47A1, the vitamin-D hydroxylase CYP24A1, kidney developmental factors SALL1/PAX8/SHH/CDKN1C, and **REN (renin) strongly up (+6.44)** — tying eGFR genetics to confounder-free, balanced microgravity perturbation; the renin up-regulation is the expected direction for spaceflight RAAS activation. Adopting the server's Rule 2 (restoring the balanced contrasts the strict filter dropped) lifts the top-ranked PKHD1/VEGFA/CYP24A1 into view alongside the renin/transporter signal.

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

Norsk, 2000, *Pflügers Archiv* ("Renal adjustments to microgravity") — spaceflight attenuates renal fluid excretion and elevates the renin–angiotensin–aldosterone axis, the physiological correlate of the up-regulated REN seen here. [PMID:11200982](https://pubmed.ncbi.nlm.nih.gov/11200982/) · [DOI](https://doi.org/10.1007/s004240000332)

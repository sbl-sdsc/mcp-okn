# UC8 — Spaceflight-Responsive Genes × Clinical Disease Associations (NASA GeneLab + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Space biology (NASA GeneLab spaceflight omics) × Clinical / literature medicine (SPOKE)
- **Knowledge graphs:** `spoke-genelab` <https://purl.org/okn/frink/kg/spoke-genelab> · `spoke-okn` <https://purl.org/okn/frink/kg/spoke-okn>
- **Shared join key:** Entrez gene id (GeneLab maps model-organism genes to their human ortholog `IS_ORTHOLOG_MGiG`; both graphs use `ncbi.nlm.nih.gov/gene/{entrez}`)

## Question
Which human genes have a model-organism ortholog that NASA GeneLab found **differentially expressed in spaceflight**, and what **diseases does SPOKE associate** those genes with? This couples spaceflight transcriptomics to terrestrial clinical knowledge.

## Result (top 20 by spaceflight differential-expression measurements)

| gene | spaceflight DE measurements | SPOKE associated diseases (sample) |
| --- | --- | --- |
| NR1D1 (Rev-erbα) | 35,276 | multiple sclerosis |
| RORA | 35,094 | asthma, IBD, epilepsy, nervous system disease |
| PPARG | 35,052 | diabetes mellitus, obesity, NAFLD, CAD, hypertension |
| PPARD | 35,002 | obesity, diabetes mellitus, nutrition disease |
| RARB | 34,896 | COPD, nervous system disease |
| NR1H3 (LXRα) | 34,876 | hypertension |
| NR1H2 (LXRβ) | 34,844 | COVID-19 |
| PPARA | 34,836 | arteriosclerosis, diabetes, obesity, liver disease |
| THRA | 34,828 | asthma, COPD, bipolar disorder |
| RORC | 34,678 | IBD, dermatitis, asthma, liver disease |
| RARA | 33,964 | acute myeloid leukemia, leukemia |
| VDR | 33,730 | epilepsy |

## Why it answers the question and is biologically coherent
The ranking is dominated by **nuclear-receptor and circadian-clock genes** — NR1D1/Rev-erbα, the RORs, the PPARs, RARs, THRs, LXRs (NR1H2/3), VDR — which is exactly the gene class spaceflight is known to perturb: spaceflight disrupts circadian timing and lipid/energy metabolism. SPOKE then attaches each gene's terrestrial disease profile, which lands on the expected metabolic, immune/inflammatory and neurological conditions. Neither graph alone suffices: GeneLab has the spaceflight expression but no disease attribution; SPOKE has disease associations but no spaceflight data. The Entrez ortholog key fuses them.

## Validation
According to PubMed, long-duration spaceflight produces **clock-dependent** skeletal-muscle gene-expression dysregulation (the core-clock network includes NR1D1 and the RORs) that mirrors aging and drives musculoskeletal atrophy — Malhan et al., *NPJ Microgravity* 2023, [DOI](https://doi.org/10.1038/s41526-023-00273-4). The dominance of circadian/nuclear-receptor genes in the joined result is therefore consistent with the spaceflight biology literature; the use case is retained as valid.

## SPARQL
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?sym ?spaceflight_DE_measurements ?spoke_associated_diseases WHERE {
  { SELECT ?hg (COUNT(DISTINCT ?stmt) AS ?spaceflight_DE_measurements) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mg .
        ?mg gl:IS_ORTHOLOG_MGiG ?hg . }
    } GROUP BY ?hg }
  { SELECT ?hg ?sym (GROUP_CONCAT(DISTINCT ?dl; separator="; ") AS ?spoke_associated_diseases) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?dis sp:ASSOCIATES_DaG ?hg ; rdfs:label ?dl . ?hg rdfs:label ?sym . }
    } GROUP BY ?hg ?sym }
}
ORDER BY DESC(?spaceflight_DE_measurements) LIMIT 20
```
*(The measurement count reflects ortholog-mapped spaceflight differential-expression statements and is used as a ranking metric.)*

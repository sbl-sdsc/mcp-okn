# UC20 — AOP Chemical Stressors × HTS Screening × Safety Curation (AOP-Wiki + ToxCast + ICE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Predictive toxicology / mechanistic (AOP-Wiki) × High-throughput screening (EPA ToxCast) × Chemical safety curation (NICEATM ICE)
- **Shared join key:** CAS Registry Number (AOP-Wiki `has_chemical_entity`; ToxCast & ICE `edam:has_identifier`)

## Question
Which chemicals are simultaneously (a) **adverse-outcome-pathway stressors** in AOP-Wiki, (b) **high-throughput-screened** in EPA ToxCast (and how many assay endpoints test them), and (c) **curated** in NICEATM's Integrated Chemical Environment (ICE)? This aligns the mechanistic, screening, and regulatory-safety views of a chemical.

## Result (top AOP-stressor chemicals by ToxCast assay endpoints)

| CAS number | chemical (identity) | AOP stressor links | ToxCast endpoints |
| --- | --- | --- | --- |
| 1763-23-1 | **PFOS** (perfluorooctanesulfonic acid) | 1 | 1,510 |
| 80-05-7 | **Bisphenol A (BPA)** | 1 | 1,414 |
| 8018-01-7 | **Mancozeb** (fungicide) | 1 | 1,351 |
| 3380-34-5 | **Triclosan** | 1 | 1,316 |
| 56-53-1 | **Diethylstilbestrol (DES)** | 1 | 1,237 |
| 115-29-7 | **Endosulfan** | 1 | 1,208 |
| 298-00-0 | **Methyl parathion** | 1 | 1,203 |

## Why it answers the question
Every returned chemical is an AOP-Wiki adverse-outcome-pathway stressor, is heavily assayed in ToxCast (1,200–1,500 endpoints each), and is curated in ICE — three independent toxicology resources fused on the CAS number. The list is a roll-call of canonical endocrine disruptors and pesticides (PFOS, BPA, DES, triclosan, endosulfan, mancozeb, methyl parathion) — exactly the chemicals that anchor adverse-outcome-pathway research and high-throughput endocrine/toxicity screening. No single graph supports this: AOP-Wiki has mechanistic pathways but no assay-endpoint counts or safety curation; ToxCast has bioactivity data but no AOP or curation layer; ICE has safety curation but neither.

## Validation
According to PubMed, EPA's ToxCast estrogen-receptor (ER) model — built from 18 ToxCast ER high-throughput assays and validated against reference chemicals including bisphenol A — operationalizes high-throughput endocrine screening for the Endocrine Disruptor Screening Program (Browne et al., *Environ Sci Technol* 2015, [DOI](https://doi.org/10.1021/acs.est.5b02641)). This supports both the ToxCast-screening and the AOP-stressor (endocrine) characterization that the join surfaces for BPA and the other returned chemicals; the use case is retained as valid.

## SPARQL
```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX edam: <http://edamontology.org/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
SELECT ?cas_number ?aop_stressor_links ?toxcast_endpoints WHERE {
  { SELECT ?casH (COUNT(DISTINCT ?s) AS ?aop_stressor_links) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s aop:has_chemical_entity ?cas . }
      BIND(IRI(REPLACE(STR(?cas),'https://identifiers.org/cas/','http://identifiers.org/cas/')) AS ?casH)
    } GROUP BY ?casH }
  { SELECT ?casH (COUNT(DISTINCT ?mg) AS ?toxcast_endpoints) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t edam:has_identifier ?casH ; obo:RO_0000056 ?mg . FILTER(STRSTARTS(STR(?casH),'http://identifiers.org/cas/')) }
    } GROUP BY ?casH }
  FILTER EXISTS { GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?i edam:has_identifier ?casH } }
  BIND(REPLACE(STR(?casH),'^.*/cas/','') AS ?cas_number)
}
ORDER BY DESC(?toxcast_endpoints) LIMIT 12
```
*(Chemical identities annotated from CAS numbers; AOP stressor links counts distinct AOP-Wiki entities citing the chemical as a stressor.)*

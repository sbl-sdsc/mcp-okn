# UC18 — Research Datasets × EHR Phenotypes × Protein Evidence by Disease (NDE + OARD + ProKN)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Research data resources (NDE — NIAID/ImmPort datasets) × Clinical EHR observation (OARD) × Proteomics (ProKN)
- **Shared join key:** MONDO disease id (NDE `schema:healthCondition`; OARD `biolink:subject/object`; ProKN `up:Disease rdfs:seeAlso`)

## Question
Which diseases are richly characterized across three independent layers at once — the volume of NIAID/ImmPort **research datasets** (NDE), the number of **EHR-derived disease-phenotype associations** (OARD), and the count of **proteins** linked to the disease (ProKN)?

## Result (top diseases by NDE dataset count)

| disease | NDE datasets | OARD phenotype assoc. | ProKN proteins |
| --- | --- | --- | --- |
| metastatic prostate cancer | 2,974 | 1,415 | 518 |
| Tuberculosis | 954 | 883 | 101 |
| amyotrophic lateral sclerosis | 740 | 2,882 | 122 |
| systemic lupus erythematosus | 594 | 1,010 | 107 |
| cystic fibrosis | 290 | 624 | 112 |
| graft-versus-host disease | 255 | 709 | 107 |
| Duchenne muscular dystrophy | 190 | 136 | 42 |

## Why it answers the question
Every returned disease carries substantial evidence in all three layers: research-dataset depth (NDE), real-world clinical phenotype breadth (OARD's EHR-derived associations), and molecular characterization (ProKN proteins). The leaders are exactly the diseases one expects to be data-rich across translational, clinical, and molecular dimensions — metastatic prostate cancer, TB, ALS, lupus, cystic fibrosis. No single graph supports this: NDE is a dataset catalog with no phenotype or protein layer; OARD is EHR co-occurrence with no datasets or proteins; ProKN is proteomics with no dataset or EHR-frequency layer. The MONDO key fuses a data-resource, a clinical-observational, and a molecular view of disease.

## Validation
Integration joins three authoritative, ontology-grounded resources on MONDO (verified NDE↔OARD and OARD↔ProKN MONDO crosswalks). The returned diseases have strong face validity as heavily studied conditions across NIAID research, EHR systems, and proteomics. This is a data-resource-integration use case; no novel biomedical claim is asserted beyond the joined evidence counts.

## SPARQL
```sparql
PREFIX schema: <http://schema.org/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
SELECT ?disease ?nde_datasets ?oard_phenotype_assoc ?prokn_proteins WHERE {
  { SELECT ?mondo (COUNT(DISTINCT ?ds) AS ?nde_datasets) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nde> { ?ds schema:healthCondition ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } GROUP BY ?mondo }
  { SELECT ?mondo (COUNT(DISTINCT ?a) AS ?oard_phenotype_assoc) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?a biolink:object ?mondo } UNION { ?a biolink:subject ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } GROUP BY ?mondo }
  { SELECT ?mondo (SAMPLE(?dl) AS ?disease) (COUNT(DISTINCT ?prot) AS ?prokn_proteins) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d a up:Disease ; rdfs:seeAlso ?mondo . OPTIONAL { ?d rdfs:label ?dl } ?prot obo:NCIT_C41184 ?d . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } GROUP BY ?mondo }
}
ORDER BY DESC(?nde_datasets) LIMIT 15
```

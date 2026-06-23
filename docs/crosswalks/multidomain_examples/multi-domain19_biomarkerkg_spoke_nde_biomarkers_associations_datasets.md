# UC19 — Literature Biomarkers × Multimodal Associations × Research Datasets by Disease (BiomarkerKG + SPOKE + NDE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Biomarker discovery (BiomarkerKG) × Network/clinical associations (SPOKE) × Research data resources (NDE)
- **Shared join key:** DOID disease id (SPOKE disease node-IRI; BiomarkerKG object position; NDE `schema:healthCondition`)

## Question
For a disease, how do its **literature-curated biomarkers** (BiomarkerKG), its **disease-gene associations** (SPOKE), and its **NIAID/ImmPort research datasets** (NDE) line up — surfacing diseases rich across biomarker, network, and data-resource layers?

## Result (top diseases by biomarker count)

| disease | SPOKE assoc. genes | biomarkers (BiomarkerKG) | NDE datasets |
| --- | --- | --- | --- |
| breast cancer | 248 | 14,661 | 79 |
| skin melanoma | 57 | 1,880 | 21 |
| acute myeloid leukemia | 123 | 972 | 133 |
| urinary bladder cancer | 69 | 266 | 1 |
| skin cancer | 223 | 222 | 129 |
| cervical cancer | 31 | 81 | 6 |
| lymphoid leukemia | 72 | 16 | 126 |

## Why it answers the question
Each disease is jointly characterized by literature biomarkers (BiomarkerKG), disease-gene associations (SPOKE `ASSOCIATES_DaG`), and research-dataset depth (NDE). The result is dominated by cancers — breast cancer leads with 14,661 curated biomarkers, 248 SPOKE-associated genes, and 79 NIAID datasets — reflecting BiomarkerKG's oncology focus and the intensive multi-omic study of these malignancies. No single graph supplies all three: BiomarkerKG has biomarkers but no gene-network or dataset layer; SPOKE has associations but no curated biomarker catalog; NDE has datasets but neither. The DOID key fuses a biomarker-discovery, a network-medicine, and a data-resource view.

## Validation
Integration joins three resources on the authoritative DOID standard (verified BiomarkerKG↔SPOKE and SPOKE↔NDE DOID crosswalks). The cancer-dominated result has strong face validity (breast cancer, melanoma, and AML are among the most biomarker-studied diseases). This is a data-resource-integration use case; biomarker/association counts are reported as evidence depth, not as novel claims.

## SPARQL
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX schema: <http://schema.org/>
SELECT ?disease ?spoke_assoc_genes ?biomarkers ?nde_datasets WHERE {
  { SELECT ?doid ?disease (COUNT(DISTINCT ?g) AS ?spoke_assoc_genes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a biolink:Disease ; rdfs:label ?disease .
        FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) OPTIONAL { ?doid sp:ASSOCIATES_DaG ?g } } } GROUP BY ?doid ?disease }
  { SELECT ?doid (COUNT(DISTINCT ?bm) AS ?biomarkers) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?bm ?p ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) } } GROUP BY ?doid }
  { SELECT ?doid (COUNT(DISTINCT ?ds) AS ?nde_datasets) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nde> { ?ds schema:healthCondition ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) } } GROUP BY ?doid }
}
ORDER BY DESC(?biomarkers) LIMIT 15
```

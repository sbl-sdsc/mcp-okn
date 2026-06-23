# UC23 — Disease Molecular Dossier: Biomarkers × Protein Evidence × Associations (BiomarkerKG + ProKN + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Biomarker discovery (BiomarkerKG) × Proteomics (ProKN) × Network/clinical associations (SPOKE)
- **Shared join key:** DOID disease id (BiomarkerKG object position; ProKN `up:Disease rdfs:seeAlso`; SPOKE disease node-IRI)

## Question
Which diseases carry **triple molecular evidence** — literature-curated biomarkers (BiomarkerKG), disease-associated proteins (ProKN), and disease-gene associations (SPOKE) — all at once? This is the strictest three-way molecular intersection and surfaces diseases evidenced across biomarker, proteomic, and network layers.

## Result (diseases present in all three molecular layers)

| disease | biomarkers (BiomarkerKG) | ProKN proteins | SPOKE assoc. genes |
| --- | --- | --- | --- |
| Parkinson's disease | 6 | 21 | 207 |
| cerebrovascular disease | 14 | 3 | 88 |
| anxiety disorder | 1 | 2 | 32 |

## Why it answers the question
The query returns only diseases that appear in all three molecular graphs on DOID — a deliberately strict intersection. Parkinson's disease is the strongest case: 6 curated biomarkers, 21 disease-associated proteins, and 207 SPOKE-associated genes, giving a compact cross-resource molecular dossier. The small result size is itself informative: it is the precise set of diseases for which biomarker, proteomic, and network evidence coincide across these three independent KGs on the DOID key. No single graph supplies all three molecular views.

## Validation
Integration joins three molecular resources on the authoritative DOID standard (verified BiomarkerKG↔SPOKE and SPOKE↔ProKN DOID crosswalks). Parkinson's disease, cerebrovascular disease, and anxiety disorder are all heavily studied at the biomarker/protein level, giving the result strong face validity. This is a molecular-evidence-integration use case; the counts report evidence depth rather than novel claims.

## SPARQL
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
SELECT ?disease ?biomarkers ?prokn_proteins ?spoke_assoc_genes WHERE {
  { SELECT ?doid ?disease (COUNT(DISTINCT ?g) AS ?spoke_assoc_genes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a biolink:Disease ; rdfs:label ?disease .
        FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) OPTIONAL { ?doid sp:ASSOCIATES_DaG ?g } } } GROUP BY ?doid ?disease }
  { SELECT ?doid (COUNT(DISTINCT ?bm) AS ?biomarkers) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?bm ?p ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) } } GROUP BY ?doid }
  { SELECT ?doid (COUNT(DISTINCT ?prot) AS ?prokn_proteins) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d a up:Disease ; rdfs:seeAlso ?doid . ?prot obo:NCIT_C41184 ?d . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) } } GROUP BY ?doid }
}
ORDER BY DESC(?prokn_proteins)
```

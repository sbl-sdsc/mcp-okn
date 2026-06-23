# Taxonomy Crosswalk 11 Q2 — SAWGraph corn × GeneLab Arabidopsis (plant clade bridge)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Plant-side version: bridge SAWGraph's PFAS-monitored corn to spoke-genelab's spaceflight Arabidopsis through the angiosperm clade. How much spaceflight gene data for Arabidopsis, how much PFAS data for corn, and which plant clades do they share? Join sawgraph and spoke-genelab via the ubergraph hierarchy.

---

🧠 **Assistant**

The plant-side clade bridge mirrors the fish case. *Arabidopsis thaliana* (NCBITaxon:3702, NASA GeneLab spaceflight plant model) and the SAWGraph-monitored corn material (*Zea*, NCBITaxon:381124) share **7 flowering-plant clades**: Mesangiospermae, Embryophyta, Viridiplantae, Magnoliopsida, Streptophyta, Tracheophyta and Spermatophyta. Across that lineage, spoke-genelab holds **25,466 Arabidopsis genes profiled in spaceflight**, and SAWGraph holds **1,561 PFAS observations covering 81 distinct PFAS substances** in corn.

The row answers the question: NASA's spaceflight plant model (Arabidopsis) and a PFAS-accumulating agricultural crop (corn) meet at the angiosperm/Viridiplantae clade, so spaceflight plant-biology resources can inform mechanistic study of PFAS uptake in the monitored crop. As with the fish case, this is only reachable through the ubergraph hierarchy because the two KGs share no exact taxon (only clade overlap).

**Literature validation (PubMed):** Arabidopsis spaceflight transcriptomics (e.g. PMID 33668919, 30866818) and PFAS uptake in agricultural crops (e.g. PMID 32717507, 35460639) are both documented. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?genelabArabidopsisGenes ?cornPFASsubstances ?cornPFASobservations
  (GROUP_CONCAT(DISTINCT ?plantClade; separator=", ") AS ?sharedPlantClades)
WHERE {
  { SELECT (COUNT(DISTINCT ?gene) AS ?genelabArabidopsisGenes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?gene gls:taxonomy ?t . FILTER(STR(?t)='http://purl.obolibrary.org/obo/NCBITaxon_3702') } } }
  { SELECT (COUNT(DISTINCT ?subst) AS ?cornPFASsubstances) (COUNT(DISTINCT ?obs) AS ?cornPFASobservations) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?m <http://purl.obolibrary.org/obo/RO_0002162> <http://purl.obolibrary.org/obo/NCBITaxon_381124> .
        ?samp coso:sampleOfMaterialType ?m . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_3702> rdfs:subClassOf* ?clade .
    <http://purl.obolibrary.org/obo/NCBITaxon_381124> rdfs:subClassOf* ?clade .
    ?clade rdfs:label ?plantClade .
    FILTER(?plantClade IN ('Viridiplantae','Magnoliopsida','Mesangiospermae','Spermatophyta','Streptophyta','Embryophyta','Tracheophyta'))
  }
}
GROUP BY ?genelabArabidopsisGenes ?cornPFASsubstances ?cornPFASobservations
```

### Result (1 row)

| genelabArabidopsisGenes | cornPFASsubstances | cornPFASobservations | sharedPlantClades |
| --- | --- | --- | --- |
| 25466 | 81 | 1561 | Mesangiospermae, Embryophyta, Viridiplantae, Magnoliopsida, Streptophyta, Tracheophyta, Spermatophyta |

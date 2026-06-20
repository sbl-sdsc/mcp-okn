# Taxonomy Crosswalk 6 Q2 — GXA Arabidopsis × SAWGraph corn (shared plant clade)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Same clade-bridge idea on the plant side: Arabidopsis (GXA model plant) and corn/maize (SAWGraph PFAS-monitored crop). How much GXA expression data for Arabidopsis, how much PFAS data for corn, and which plant clades do they share? Join gene-expression-atlas-okn and sawgraph via the ubergraph NCBITaxon hierarchy.

---

🧠 **Assistant**

The plant-side clade bridge mirrors the fish case. *Arabidopsis thaliana* (NCBITaxon:3702) and the SAWGraph-monitored corn material (*Zea*, NCBITaxon:381124) share **7 flowering-plant clades**: Mesangiospermae, Embryophyta, Viridiplantae, Magnoliopsida, Streptophyta, Tracheophyta and Spermatophyta. Across that shared lineage, GXA holds **638 Arabidopsis gene-expression studies**, while SAWGraph holds **1,561 PFAS observations covering 81 distinct PFAS substances** in corn.

The row answers the question: corn (a PFAS-accumulating agricultural crop in SAWGraph) and Arabidopsis (the reference plant transcriptomic model in GXA) meet at the angiosperm/Viridiplantae clade, so the rich Arabidopsis expression resource can inform mechanistic study of PFAS uptake in the monitored crop. Like the fish case, this is only reachable through the ubergraph hierarchy because GXA and SAWGraph share no exact taxon.

**Literature validation (PubMed):** PFAS uptake and accumulation in agricultural crops/plants is documented — a PubMed search returns 16 articles (e.g. PMID 32717507, 35460639, 42240289, 38555786). Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
SELECT ?gxaArabidopsisStudies ?cornPFASsubstances ?cornPFASobservations
  (GROUP_CONCAT(DISTINCT ?plantClade; separator=", ") AS ?sharedPlantClades)
WHERE {
  { SELECT (COUNT(DISTINCT ?study) AS ?gxaArabidopsisStudies) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
        ?study biolink:in_taxon <http://purl.obolibrary.org/obo/NCBITaxon_3702> } } }
  { SELECT (COUNT(DISTINCT ?subst) AS ?cornPFASsubstances) (COUNT(DISTINCT ?obs) AS ?cornPFASobservations) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?m <http://purl.obolibrary.org/obo/RO_0002162> <http://purl.obolibrary.org/obo/NCBITaxon_381124> .
        ?samp coso:sampleOfMaterialType ?m . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_3702> rdfs:subClassOf* ?clade .
    <http://purl.obolibrary.org/obo/NCBITaxon_381124> rdfs:subClassOf* ?clade .
    ?clade rdfs:label ?plantClade .
    FILTER(?plantClade IN ('Viridiplantae','Magnoliopsida','Mesangiospermae','Spermatophyta','Streptophyta','Embryophyta','Tracheophyta','eudicotyledons','Pentapetalae'))
  }
}
GROUP BY ?gxaArabidopsisStudies ?cornPFASsubstances ?cornPFASobservations
```

### Result (1 row)

| gxaArabidopsisStudies | cornPFASsubstances | cornPFASobservations | sharedPlantClades |
| --- | --- | --- | --- |
| 638 | 81 | 1561 | Mesangiospermae, Embryophyta, Viridiplantae, Magnoliopsida, Streptophyta, Tracheophyta, Spermatophyta |

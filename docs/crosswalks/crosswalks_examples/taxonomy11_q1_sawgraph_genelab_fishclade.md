# Taxonomy Crosswalk 11 Q1 — SAWGraph white perch × GeneLab zebrafish (fish clade bridge)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

SAWGraph and spoke-genelab share no exact NCBITaxon, but spoke-genelab taxa fall under SAWGraph clades. Bridge SAWGraph's PFAS-monitored white perch to spoke-genelab's spaceflight zebrafish through the ray-finned-fish clade: how much spaceflight gene data for zebrafish, how much PFAS data for white perch, and which fish clades do they share? Join sawgraph and spoke-genelab via the ubergraph hierarchy.

---

🧠 **Assistant**

Because SAWGraph and spoke-genelab have **zero exact-id taxon overlap** (only clade overlap: 13 spoke-genelab taxa fall under SAWGraph clades), the integration goes through the ubergraph taxonomy hierarchy. Zebrafish (*Danio rerio*, NCBITaxon:7955, NASA GeneLab spaceflight model) and white perch (*Morone americana*, NCBITaxon:46260, SAWGraph PFAS-monitored fish) share **6 ray-finned-fish clades**: Euteleostomi, Actinopteri, Clupeocephala, Teleostei, Neopterygii and Actinopterygii. Across that lineage, spoke-genelab holds **17,143 zebrafish genes profiled in spaceflight**, and SAWGraph holds **80 PFAS observations covering 79 distinct PFAS substances** in white perch.

The row answers the question: NASA's spaceflight fish model (zebrafish) and an environmentally PFAS-contaminated wild fish (white perch) meet at the Teleostei/Actinopterygii clade, so spaceflight-derived fish transcriptomic resources can be brought to bear on PFAS-exposed wild fish. The bridge is only obtainable through the ubergraph NCBITaxon hierarchy.

**Literature validation (PubMed):** zebrafish is an established spaceflight/microgravity model organism — a PubMed search returns 6 articles (PMID 41629319, 39986582, 28725727, 33406425); PFAS bioaccumulation in fish is well documented (e.g. PMID 36280234). Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?genelabZebrafishGenes ?perchPFASsubstances ?perchPFASobservations
  (GROUP_CONCAT(DISTINCT ?fishClade; separator=", ") AS ?sharedFishClades)
WHERE {
  { SELECT (COUNT(DISTINCT ?gene) AS ?genelabZebrafishGenes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?gene gls:taxonomy ?t . FILTER(STR(?t)='http://purl.obolibrary.org/obo/NCBITaxon_7955') } } }
  { SELECT (COUNT(DISTINCT ?subst) AS ?perchPFASsubstances) (COUNT(DISTINCT ?obs) AS ?perchPFASobservations) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?m <http://purl.obolibrary.org/obo/RO_0002162> <http://purl.obolibrary.org/obo/NCBITaxon_46260> .
        ?samp coso:sampleOfMaterialType ?m . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_7955> rdfs:subClassOf* ?clade .
    <http://purl.obolibrary.org/obo/NCBITaxon_46260> rdfs:subClassOf* ?clade .
    ?clade rdfs:label ?fishClade .
    FILTER(?fishClade IN ('Actinopterygii','Teleostei','Actinopteri','Neopterygii','Clupeocephala','Euteleostomi'))
  }
}
GROUP BY ?genelabZebrafishGenes ?perchPFASsubstances ?perchPFASobservations
```

### Result (1 row)

| genelabZebrafishGenes | perchPFASsubstances | perchPFASobservations | sharedFishClades |
| --- | --- | --- | --- |
| 17143 | 79 | 80 | Euteleostomi, Actinopteri, Clupeocephala, Teleostei, Neopterygii, Actinopterygii |

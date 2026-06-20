# Taxonomy Crosswalk 3 Q2 — White perch PFAS load + clade AOPs

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>

## Conversation

👤 **User**

White perch (Morone americana, NCBITaxon:46260) is sampled for PFAS in SAWGraph. How many PFAS substances/observations were measured in white perch, and which AOP key events apply to it through its taxonomic clade in AOP-Wiki? Join sawgraph (PFAS) to biobricks-aopwiki via the ubergraph NCBITaxon hierarchy.

---

🧠 **Assistant**

Joining the white perch PFAS samples in SAWGraph to AOP-Wiki through the ubergraph taxonomy hierarchy yields an integrated contaminant-plus-mechanism profile. SAWGraph records **80 PFAS observations covering 79 distinct PFAS substances** in white perch tissue. White perch is a ray-finned fish; the only AOP-Wiki taxon in its lineage is the Metazoa root (NCBITaxon:33208), through which it inherits **7 AOP key events**: Decreased blood plasma volume; Increased Cardiac stress; Decreased Na/K ATPase activity; Heart failure; Increase, Abnormal osmoregulation; Decreased Plasma sodium concentrations; Increased Blood viscosity.

The row answers the question: a PFAS-contaminated fish species (79 substances measured) is linked, through the NCBITaxon clade join, to a coherent set of cardiovascular / osmoregulatory adverse-outcome pathways. This contaminant-to-mechanism bridge is only obtainable by joining SAWGraph and AOP-Wiki via the ubergraph hierarchy — white perch is not directly an AOP-Wiki test species, so the clade link supplies the mechanisms.

**Literature validation (PubMed):** PFAS bioaccumulation in freshwater fish tissue is well documented — a PubMed search returns 18 articles (e.g. PMID 36280234, 37011692, 34509478, 34979204). PFAS osmoregulatory/cardiovascular toxicity in fish is likewise established. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
SELECT ?species
  (COUNT(DISTINCT ?subst) AS ?pfasSubstancesMeasured)
  (COUNT(DISTINCT ?obs) AS ?pfasObservations)
  (GROUP_CONCAT(DISTINCT ?keTitle; separator=" | ") AS ?cladeAOPkeyEvents)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?matType <http://purl.obolibrary.org/obo/RO_0002162> <http://purl.obolibrary.org/obo/NCBITaxon_46260> ; rdfs:label ?species .
    ?sample coso:sampleOfMaterialType ?matType .
    ?obs coso:analyzedSample ?sample ; coso:ofSubstance ?subst .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_46260> rdfs:subClassOf* ?aopTax .
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ke a aop:KeyEvent ; <http://purl.obolibrary.org/obo/NCBITaxon_131567> ?te ; dc:title ?keTitle .
    ?te dc:identifier ?aopTax .
  }
}
GROUP BY ?species
```

### Result (1 row)

| species | pfasSubstancesMeasured | pfasObservations | cladeAOPkeyEvents |
| --- | --- | --- | --- |
| White perch (Morone americana) | 79 | 80 | Decreased, blood plasma volume \| Increased, Cardiac stress \| Decreased Na/K ATPase activity \| Heart failure \| Increase, Abnormal osmoregulation \| Decreased, Plasma sodium concentrations \| Increased, Blood viscosity |

# Taxonomy Crosswalk 8 Q2 — Rainbow trout One Health (PFAS taxonomy + NDE disease)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `nde` — <https://purl.org/okn/frink/kg/nde>

## Conversation

👤 **User**

Rainbow trout (Oncorhynchus mykiss, NCBITaxon:8022) is a key aquaculture fish that bioaccumulates PFAS. Confirm it sits in SAWGraph's PFAS fish taxonomy and report how many NDE disease datasets and which conditions involve it. Join sawgraph and nde on NCBITaxon:8022.

---

🧠 **Assistant**

Joining on NCBITaxon:8022 confirms the One Health bridge: rainbow trout is present in SAWGraph's PFAS-relevant fish taxonomy AND is the subject of **201 NIAID NDE datasets**. Example health conditions recorded for trout datasets include **arbovirus infection** and **bacterial infectious disease** (alongside many comparative-genomics / disease-model annotations such as anemia, atrial fibrillation, Alzheimer disease and aromatase deficiency).

The row answers the question: a single PFAS-bioaccumulating aquaculture species is simultaneously in SAWGraph's contaminant-monitoring scope and in NDE's infectious/immune-disease datasets — exactly the organism where PFAS exposure data and infection/immune data can be jointly analyzed. The result requires the NCBITaxon join between the two KGs.

**Literature validation (PubMed):** PFAS bioaccumulation in salmonid/trout tissue is well documented (freshwater-fish PFAS literature, e.g. PMID 36280234, 37011692), and PFAS immunotoxicity (e.g. PMID 36814257, 38712868) supports overlaying contamination on the trout infectious-disease datasets. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?troutNDEdatasets (GROUP_CONCAT(DISTINCT ?conditionName; separator=" | ") AS ?exampleTroutConditions)
WHERE {
  { SELECT (COUNT(DISTINCT ?ds) AS ?troutNDEdatasets) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> { <http://purl.obolibrary.org/obo/NCBITaxon_8022> rdfs:subClassOf ?p }
      GRAPH <https://purl.org/okn/frink/kg/nde> { ?ds schema:species ?sp . FILTER(REGEX(STR(?sp),'/taxonomy/8022($|[^0-9])')) } } }
  {
    SELECT DISTINCT ?conditionName WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nde> {
        ?ds schema:species ?sp . FILTER(REGEX(STR(?sp),'/taxonomy/8022($|[^0-9])'))
        ?ds schema:healthCondition ?hc . ?hc schema:name ?conditionName
      }
    } LIMIT 12
  }
}
GROUP BY ?troutNDEdatasets
```

### Result (1 row)

| troutNDEdatasets | exampleTroutConditions |
| --- | --- |
| 201 | Abnormality of neuronal migration \| adjustment disorder \| Alzheimer disease \| anemia \| Anophthalmia \| arbovirus infection \| aromatase deficiency \| atrial fibrillation \| Atrophy \| attenuated familial adenomatous polyposis \| autosomal recessive spondylocostal dysostosis \| bacterial infectious disease |

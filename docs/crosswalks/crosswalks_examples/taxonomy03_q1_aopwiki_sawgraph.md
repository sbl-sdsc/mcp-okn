# Taxonomy Crosswalk 3 Q1 — AOP-Wiki × SAWGraph (PFAS-relevant agricultural taxa)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

SAWGraph monitors PFAS contamination in agricultural products and biota. Which organisms in SAWGraph's taxonomy also have adverse-outcome-pathway key events in AOP-Wiki, and what are those toxicology mechanisms? Join sawgraph and biobricks-aopwiki on the shared NCBITaxon id.

---

🧠 **Assistant**

Joining SAWGraph's NCBITaxon taxonomy (taxa it references for PFAS sampling / agricultural products) to AOP-Wiki key-event taxonomic applicability on the exact NCBITaxon id returns **5 shared taxa**, all agriculturally relevant:

- **Sus scrofa** (pig) — 8 AOP key events (example: *Inhibition, Deiodinase 2*, a thyroid-hormone mechanism directly relevant to PFAS endocrine disruption)
- **Metazoa** (animal root clade) — 7 AOP key events (e.g. *Heart failure*)
- **Bos taurus** (cattle) — 4 AOP key events (e.g. *Inadequate DNA repair*)
- **Ovis aries** (sheep) — 4 AOP key events (e.g. *Mucociliary Clearance, Decreased*)
- **Sus scrofa domesticus** (domestic pig) — 1 AOP key event (*Mucociliary Clearance, Decreased*)

The rows answer the question: these livestock species (plus the Metazoa root) are integration points where PFAS environmental-monitoring data (SAWGraph) can be combined with mechanistic toxicology (AOP-Wiki). The pig thyroid-deiodinase key event is especially salient because PFAS are established thyroid-axis disruptors. The result depends entirely on the NCBITaxon join.

**Literature validation (PubMed):** PFAS-induced thyroid-hormone disruption involving deiodinase / T4→T3 conversion is documented (e.g. PMID 32474277, 39556482), supporting the relevance of the pig deiodinase-2 key event to PFAS exposure in agricultural species. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?taxName (COUNT(DISTINCT ?ke) AS ?aopKeyEvents) (SAMPLE(?keTitle) AS ?exampleKE) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?sgTax rdfs:subClassOf ?x .
    FILTER(STRSTARTS(STR(?sgTax),'http://purl.obolibrary.org/obo/NCBITaxon_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ke a aop:KeyEvent ; <http://purl.obolibrary.org/obo/NCBITaxon_131567> ?te ; dc:title ?keTitle .
    ?te dc:identifier ?sgTax .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?sgTax rdfs:label ?taxName }
}
GROUP BY ?sgTax ?taxName ORDER BY DESC(?aopKeyEvents)
```

### Results (5 rows)

| taxName | aopKeyEvents | exampleKE |
| --- | --- | --- |
| Sus scrofa | 8 | Inhibition, Deiodinase 2 |
| Metazoa | 7 | Heart failure |
| Bos taurus | 4 | Inadequate DNA repair |
| Ovis aries | 4 | Mucociliary Clearance, Decreased |
| Sus scrofa domesticus | 1 | Mucociliary Clearance, Decreased |

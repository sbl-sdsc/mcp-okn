# Taxonomy Crosswalk 1 Q2 — Zebrafish AOP + GXA dossier

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation

👤 **User**

Build an integrated dossier for zebrafish (Danio rerio, NCBITaxon:7955): list every AOP key event whose taxonomic applicability includes zebrafish (AOP-Wiki) and report how many Gene Expression Atlas studies were run in zebrafish, with an example study PubMed ID. This requires joining biobricks-aopwiki and gene-expression-atlas-okn on NCBITaxon:7955.

---

🧠 **Assistant**

Joining the two KGs on NCBITaxon:7955 yields a single integrated zebrafish dossier. AOP-Wiki defines **8 key events** with zebrafish taxonomic applicability: GSK3beta inactivation; Acetylcholine accumulation in synapses; Binding, Thiol/seleno-proteins involved in protection against oxidative stress; **Activation, AhR**; Decrease of Thyroidal iodide; Inhibition, VegfR2; reduction in ovarian granulosa cells, Aromatase (Cyp19a1); Inhibition, Na+/I- symporter (NIS). The Gene Expression Atlas contains **27 zebrafish gene-expression studies** that could supply transcriptomic evidence for these mechanisms; an example carries PubMed id 29144233.

These rows answer the question: zebrafish is a real bridge node where mechanistic toxicology (AOP key events such as AhR activation, aromatase reduction, NIS/thyroid inhibition) meets transcriptomic data (27 GXA expression studies). The result is only obtainable by joining the two graphs on the shared NCBITaxon organism id.

**Literature validation (PubMed):** the AhR-activation key event in zebrafish is well supported — a PubMed search for *aryl hydrocarbon receptor activation zebrafish adverse outcome pathway* returns 9 articles (e.g. PMID 39092785, 37341548, 36860045). The thyroid-axis key events (NIS inhibition / decreased thyroidal iodide) are likewise established zebrafish AOP endpoints. Evidence exists, so this query is retained.

## SPARQL query executed

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
SELECT
  (GROUP_CONCAT(DISTINCT ?keTitle; separator=" | ") AS ?zebrafishAOPkeyEvents)
  (COUNT(DISTINCT ?study) AS ?gxaZebrafishStudies)
  (SAMPLE(?pmid) AS ?exampleStudyPMID)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ke a aop:KeyEvent ; <http://purl.obolibrary.org/obo/NCBITaxon_131567> ?te ; dc:title ?keTitle .
    ?te dc:identifier <http://purl.obolibrary.org/obo/NCBITaxon_7955> .
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?study biolink:in_taxon <http://purl.obolibrary.org/obo/NCBITaxon_7955> ; wobd:project_title ?t .
    OPTIONAL { ?study wobd:pubmed_id ?pmid }
  }
}
```

### Result (1 row)

| zebrafishAOPkeyEvents | gxaZebrafishStudies | exampleStudyPMID |
| --- | --- | --- |
| GSK3beta inactivation \| Acetylcholine accumulation in synapses \| Binding, Thiol/seleno-proteins… \| Activation, AhR \| Decrease of Thyroidal iodide \| Inhibition, VegfR2 \| reduction in ovarian granulosa cells, Aromatase (Cyp19a1) \| Inhibition, Na+/I- symporter (NIS) | 27 | 29144233 |

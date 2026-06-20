# Taxonomy Crosswalk 5 Q2 — Drosophila GXA + NDE dossier

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `nde` — <https://purl.org/okn/frink/kg/nde>

## Conversation

👤 **User**

For Drosophila melanogaster (NCBITaxon:7227), how many Gene Expression Atlas studies exist, and how many NIAID NDE datasets / distinct health conditions involve it? Join gene-expression-atlas-okn and nde on NCBITaxon:7227.

---

🧠 **Assistant**

Joining on NCBITaxon:7227 gives an integrated *Drosophila* profile: the Gene Expression Atlas holds **150 gene-expression studies** in *Drosophila melanogaster*, and the NIAID Data Ecosystem holds **6,728 datasets spanning 422 distinct health conditions** for the same species (example condition: ovarian cancer).

The row answers the question and shows the integration value: *Drosophila* is simultaneously a heavily-used transcriptomic model (150 GXA studies) and a major immune/infection/disease-modeling organism (6,728 NDE datasets, 422 conditions). The join on the shared NCBITaxon id lets a researcher pull both evidence types for the same organism in one query.

**Literature validation (PubMed):** *Drosophila* is a foundational model for innate immunity, infection and many human-disease processes (89+ articles for innate-immunity/infection; e.g. PMID 35911716, 37793051), consistent with both the GXA expression studies and the broad NDE health-condition coverage. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX schema: <http://schema.org/>
SELECT ?gxaDrosophilaStudies (COUNT(DISTINCT ?ds) AS ?ndeDrosophilaDatasets) (COUNT(DISTINCT ?hcName) AS ?distinctHealthConditions) (SAMPLE(?hcName) AS ?exampleCondition)
WHERE {
  { SELECT (COUNT(DISTINCT ?study) AS ?gxaDrosophilaStudies) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
        ?study biolink:in_taxon <http://purl.obolibrary.org/obo/NCBITaxon_7227> } } }
  GRAPH <https://purl.org/okn/frink/kg/nde> {
    ?ds schema:species ?sp . FILTER(REGEX(STR(?sp),'/taxonomy/7227($|[^0-9])'))
    OPTIONAL { ?ds schema:healthCondition ?hc . ?hc schema:name ?hcName }
  }
}
GROUP BY ?gxaDrosophilaStudies
```

### Result (1 row)

| gxaDrosophilaStudies | ndeDrosophilaDatasets | distinctHealthConditions | exampleCondition |
| --- | --- | --- | --- |
| 150 | 6728 | 422 | ovarian cancer |

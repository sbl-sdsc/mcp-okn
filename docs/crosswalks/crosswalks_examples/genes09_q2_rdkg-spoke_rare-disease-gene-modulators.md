# CW9-Q2: SPOKE chemical modulators of rare-disease genes

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: rdkg × spoke-okn on the shared Entrez gene id. Rare-disease (MONDO) labels via ubergraph.

Research question: For genes that rdkg classifies as rare-disease genes, which chemical compounds does SPOKE record as up- or down-regulating them? This surfaces chemicals that perturb rare-disease genes (candidate therapeutic modulators or environmental risk factors).

Why the join is required: rdkg supplies the rare-disease gene-condition link but no compound pharmacology; SPOKE supplies compound->gene regulation edges but no rare-disease context. The Entrez join connects rare-disease genes to the chemicals that modulate them.

---

🧠 **Assistant**

Rare-disease genes paired with SPOKE compound regulators. Clear example:

| Gene | rdkg rare disease | Regulation | Compound |
|---|---|---|---|
| A2M | alpha-2-macroglobulin deficiency (also Wilson disease, hemochromatosis, liver cirrhosis) | downregulates | Dioxane |

Why this answers the question: A2M (alpha-2-macroglobulin) is the gene of alpha-2-macroglobulin deficiency, and SPOKE records the industrial solvent 1,4-dioxane as down-regulating it; rdkg additionally links A2M to liver conditions (cirrhosis, hepatocellular carcinoma, hemochromatosis), consistent with dioxane being a hepatotoxic/hepatocarcinogenic solvent. The chemical-modulator-of-a-rare-disease-gene relationship only exists by joining rdkg's rare-disease gene set with SPOKE's compound-gene edges on Entrez.

Literature validation (PubMed): alpha-2-macroglobulin (A2M) deficiency returns 10 records (e.g. PMIDs 14678766, 28449136). The A2M rare-disease identity is literature-supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `rdkg`, `ubergraph`, `spoke-okn`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?rareDisease ?regulation ?compound WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?r a biolink:Gene ; rdfs:label ?sym ; biolink:related_to ?mondo .
    FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
    FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo rdfs:label ?rareDisease . }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?cmpd spoke:UPREGULATES_CuG ?gene . BIND("upregulates" AS ?regulation) }
    UNION
    { ?cmpd spoke:DOWNREGULATES_CdG ?gene . BIND("downregulates" AS ?regulation) }
    ?cmpd rdfs:label ?compound .
  }
} ORDER BY ?sym LIMIT 20
```

_20 row(s) — showing first 5_

| sym | rareDisease | regulation | compound |
| --- | --- | --- | --- |
| A2M | Alzheimer disease without neurofibrillary tangles | downregulates | Dioxane |
| A2M | acute kidney injury | downregulates | Dioxane |
| A2M | Wilson disease | downregulates | Dioxane |
| A2M | undifferentiated carcinoma of liver and intrahepatic biliary tract | downregulates | Dioxane |
| A2M | squamous cell carcinoma of liver and intrahepatic biliary tract | downregulates | Dioxane |

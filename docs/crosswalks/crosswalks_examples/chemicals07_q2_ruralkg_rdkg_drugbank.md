# Chemicals Crosswalk 7 — ruralkg × rdkg (DrugBank)

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `rdkg` (Rare Disease KG) — <https://purl.org/okn/frink/kg/rdkg>

## Conversation

**User**

Do the substance-use / controlled-substance drugs that ruralkg references actually appear in rdkg's drug-disease graph, and if so what indications and contraindications does rdkg record for them? (Join ruralkg to rdkg on DrugBank ID.)

---

**Assistant**

**Use case:** ruralkg references a small set of controlled/substance-use-relevant drugs by DrugBank URL but holds no clinical drug-disease knowledge; rdkg holds curated `treats`/`contraindicated_for` edges with the DrugBank IRI as node identity. Verifying that ruralkg's drugs are represented in rdkg — and pulling rdkg's clinical context for them — requires joining on DrugBank. This is a deliberately thin thread: ruralkg has only **7** DrugBank-linked drugs, of which **2** join rdkg (and 0 join SPOKE).

**KGs joined:** ruralkg (`owl:sameAs` → `go.drugbank.com/drugs/DB...`, rewritten to `identifiers.org/drugbank/DB...`) × rdkg (Drug node IRI = DrugBank IRI; `biolink:treats`/`contraindicated_for` → Disease). Shared key: **DrugBank**.

**Result — both joining drugs, with rdkg clinical edges:**

| ruralkg drug | DrugBank | rdkg relation | example diseases |
|---|---|---|---|
| Cocaine | DB00907 | contraindicated_for | epilepsy, hyperthyroidism, heart conduction disease, sudden cardiac arrest, thyrotoxicosis |
| Ketamine | DB01221 | treats | major depressive disorder, complex regional pain syndrome, anxiety disorder, alcohol withdrawal |
| Ketamine | DB01221 | contraindicated_for | hypertension, myocardial infarction, stroke disorder, intracranial hypertension |

**Why this answers the question:** the join returns exactly the 2 ruralkg drugs (Cocaine, Ketamine) that exist in rdkg, each enriched with rdkg's clinical indication/contraindication edges. The associations are clinically correct: ketamine is an established treatment for treatment-resistant depression and complex regional pain syndrome and is contraindicated in uncontrolled hypertension / raised intracranial pressure; cocaine (a sympathomimetic) is contraindicated in hyperthyroidism and cardiac-conduction disease. The query directly answers "yes, and here is what rdkg knows about them" — and honestly exposes how thin this particular crosswalk is (2 of 7).

**Literature validation (PubMed):** Anand et al., *N Engl J Med* 2023 (ELEKT-D trial) found intravenous ketamine non-inferior to electroconvulsive therapy for treatment-resistant major depression ([DOI](https://doi.org/10.1056/NEJMoa2302399)) — corroborating rdkg's Ketamine → major depressive disorder `treats` edge surfaced by this crosswalk.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT DISTINCT ?ruralLabel ?db ?rdkgLabel ?relation ?diseaseName WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?s owl:sameAs ?o . FILTER(CONTAINS(STR(?o),'drugbank'))
    BIND(IRI(CONCAT('http://identifiers.org/drugbank/',REPLACE(STR(?o),'^.*/(DB[0-9]+).*$','$1'))) AS ?db)
    OPTIONAL { ?s rdfs:label ?ruralLabel }
  }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?db a biolink:Drug .
    OPTIONAL { ?db rdfs:label ?rdkgLabel }
    OPTIONAL {
      ?db ?rel ?disease .
      FILTER(?rel IN (biolink:treats, biolink:contraindicated_for))
      BIND(REPLACE(STR(?rel),'^.*/vocab/','') AS ?relation)
      OPTIONAL { ?disease rdfs:label ?dl }
      OPTIONAL { ?disease skos:prefLabel ?dp }
      BIND(COALESCE(?dl,?dp,STR(?disease)) AS ?diseaseName)
    }
  }
}
LIMIT 40
```

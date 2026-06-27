# SDOH02-Q2: Pollution — spoke-okn environmental SDoH bridged to biohealth by concept label

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>

## Conversation

👤 **User**

Crosswalk: spoke-okn × biohealth on SDoH, label-bridge route (SNOMED preferred term = UMLS concept name, suffix stripped).

Research question: For pollution — an environmental SDoH that spoke-okn catalogues (and tracks as air/water pollution events) — what diseases does biohealth's literature graph say it causes?

Why the join is required: spoke-okn has the pollution concept and its environmental/geographic context but no disease links; biohealth has the SemMedDB causal relationships keyed on UMLS. The label bridge connects them.

---

🧠 **Assistant**

Diseases biohealth says pollution **causes** (spoke `Pollution (event)` → biohealth `Pollution`, matched by label):

| Relationship | Disease (biohealth) |
|---|---|
| causes | Asthma |
| causes | Bronchitis |
| causes | Bronchitis, Chronic |
| causes | Acute bronchiolitis |
| causes | Bronchial Spasm |
| causes | Coronary heart disease |
| causes | Coronary Arteriosclerosis |
| causes | Cardiovascular Diseases |
| causes | Malignant Neoplasms / Carcinoma |
| causes | Alzheimer's Disease |
| causes | Diabetes Mellitus |
| causes | Dermatitis / Eczema |

Why this answers the question: spoke-okn records pollution as an environmental exposure but says nothing about its disease burden; biohealth, reached by the label bridge, supplies the established causal map — respiratory disease (asthma, acute and chronic bronchitis, bronchospasm, bronchiolitis), cardiovascular disease (coronary heart disease, atherosclerosis), cancer, neurodegeneration (Alzheimer's) and metabolic/skin disease. This is the textbook air-pollution health-effects profile, attached to spoke's SDoH concept only through the join on the concept label.

Literature validation (PubMed): "air pollution asthma chronic bronchitis cardiovascular disease risk" returns 20 records (e.g. PMIDs 41418336, 37183431); air pollution as a cause of asthma, chronic bronchitis/COPD and cardiovascular disease is extensively documented.

#### Query 1 — Pollution → biohealth causal diseases, via the concept-label bridge

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?rel ?targetLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s a spoke:SDoH ; rdfs:label "Pollution (event)" . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh rdfs:label "Pollution" .
    ?bh ?rel ?t . ?t rdfs:label ?targetLabel .
    FILTER(?rel IN (biolink:causes, biolink:affects, biolink:contributes_to, biolink:predisposes_to_condition))
  }
} LIMIT 30
```

_30 row(s) — showing first 5_

| rel | targetLabel |
| --- | --- |
| causes | Acute bronchiolitis |
| causes | Asthma |
| causes | Bronchitis |
| causes | Bronchitis, Chronic |
| causes | Cardiovascular Diseases |

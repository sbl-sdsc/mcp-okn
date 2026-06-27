# SDOH02-Q1: Sedentary lifestyle — spoke-okn SDoH bridged to biohealth by concept label

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>

## Conversation

👤 **User**

Crosswalk: spoke-okn × biohealth on SDoH, label-bridge route. spoke-okn's SDoH concepts are SNOMED-CT-keyed with `rdfs:label` = "Preferred term (semantic tag)"; biohealth's nodes are UMLS-CUI-keyed with `rdfs:label` = the UMLS concept name. Since no federation graph maps SNOMED→UMLS, the practical bridge matches the concept label (after stripping the SNOMED " (finding)" suffix).

Research question: For sedentary lifestyle — a behavioural SDoH spoke-okn catalogues — what health conditions does biohealth's literature graph say it causes?

Why the join is required: spoke-okn has the SDoH concept (and, for many SDoH, geographic prevalence) but no causal disease links; biohealth has the SemMedDB causal relationships keyed on UMLS. Matching the concept by label connects spoke's SDoH inventory to biohealth's disease consequences.

---

🧠 **Assistant**

Conditions biohealth says sedentary lifestyle **causes** (spoke `Sedentary lifestyle (finding)` → biohealth `Sedentary lifestyle`, matched by label):

| Relationship | Condition (biohealth) |
|---|---|
| causes | Insulin Resistance |
| causes | Chronic inflammation |
| causes | Inflammation |
| causes | inflammatory response |
| causes | Muscular Atrophy |
| causes | Fatty deposition |
| causes | Dysbiosis |
| causes | Insulin Sensitivity |
| causes | Pathogenesis |

Why this answers the question: spoke-okn would only tell you how common physical inactivity is by location; biohealth, reached by the label bridge, supplies the mechanistic disease consequences — insulin resistance, chronic low-grade inflammation, muscular atrophy, ectopic fat deposition and gut dysbiosis. These are precisely the established pathophysiological sequelae of a sedentary lifestyle, and they are only attached to spoke's SDoH concept by joining to biohealth's UMLS concept graph on the label.

Literature validation (PubMed): "sedentary lifestyle physical inactivity insulin resistance chronic inflammation" returns 36 records (e.g. PMIDs 42105870, 42081165); physical inactivity driving insulin resistance, chronic inflammation and muscle atrophy is well established.

#### Query 1 — Sedentary lifestyle → biohealth causal conditions, via the concept-label bridge

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?rel ?targetLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s a spoke:SDoH ; rdfs:label "Sedentary lifestyle (finding)" . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh rdfs:label "Sedentary lifestyle" .
    VALUES ?rel { biolink:causes biolink:predisposes biolink:contributes_to biolink:affects }
    ?bh ?rel ?t . ?t rdfs:label ?targetLabel .
  }
} LIMIT 30
```

_15 row(s) — showing first 5_

| rel | targetLabel |
| --- | --- |
| causes | Complication |
| causes | Inflammation |
| causes | Chronic inflammation |
| causes | Insulin Resistance |
| causes | Muscular Atrophy |

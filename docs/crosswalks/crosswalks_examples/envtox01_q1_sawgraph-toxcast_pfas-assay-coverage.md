# ET01-Q1: PFAS measured in the environment (SAWGraph) mapped to ToxCast assay coverage

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast>

## Conversation

👤 **User**

Crosswalk: sawgraph (SAWGraph PFAS contamination KG) × biobricks-toxcast, joined on **CAS number**. SAWGraph stores CAS as a dashed string literal (`coso:casNumber`); ToxCast uses `http://identifiers.org/cas/{cas}` IRIs (`edam:has_identifier`, then `RO_0000056` → assay endpoint). Build the IRI from SAWGraph's literal and inner-join. (Newly recorded — first environmental↔toxicology crosswalk; 7 shared PFAS.)

Research question: For the PFAS that SAWGraph measures in environmental water samples, how many ToxCast high-throughput assay endpoints exist for each?

Why the join is required: SAWGraph has the environmental measurements (where/when a PFAS was detected) but no toxicology; ToxCast has the high-throughput screening data keyed on CAS but no environmental context. Linking a measured environmental contaminant to its toxicological screening profile needs the CAS join.

---

🧠 **Assistant**

PFAS that SAWGraph measures environmentally, with their ToxCast high-throughput assay-endpoint coverage:

| CAS | Chemical | ToxCast assay endpoints |
|---|---|---|
| 13252-13-6 | HFPO-DA (GenX) | 506 |
| 863090-89-5 | PFAS | 506 |
| 914637-49-3 | PFAS | 497 |
| 812-70-4 | PFAS | 472 |
| 377-73-1 | PFAS | 470 |
| 375-92-8 | Perfluoroheptanesulfonic acid | 464 |
| 113507-82-7 | Perfluoro-2-ethoxyethanesulfonic acid | 299 |

Why this answers the question: the join shows that the PFAS SAWGraph detects in the environment are extensively characterized in ToxCast — GenX (HFPO-DA), the high-profile PFOA replacement, carries 506 high-throughput assay endpoints, and the others 299–506. This turns an environmental detection into an immediately interrogable toxicological profile (which assays, targets and hazards). Neither graph alone connects the contaminant to its screening data; the CAS join does. It is the first bridge from SAWGraph's environmental/geospatial data into the Biobricks toxicology cluster.

Literature validation (PubMed): PFAS drinking-water toxicity and health effects are extensively documented (56 records, e.g. PMIDs 41966494, 41926058); GenX/HFPO-DA is a recognised emerging PFAS contaminant.

#### Query 1 — SAWGraph PFAS → ToxCast assay-endpoint coverage (CAS)

```sparql
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX edam: <http://edamontology.org/>
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT ?cas (COUNT(DISTINCT ?mg) AS ?toxcastEndpoints) WHERE {
  { SELECT DISTINCT ?cas WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s coso:casNumber ?cas . FILTER(REGEX(STR(?cas),'^[0-9]+-[0-9]+-[0-9]$')) } } }
  BIND(IRI(CONCAT('http://identifiers.org/cas/', STR(?cas))) AS ?casIri)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t edam:has_identifier ?casIri ; ro:RO_0000056 ?mg . }
} GROUP BY ?cas ORDER BY DESC(?toxcastEndpoints)
```

_7 row(s) — showing first 5_

| cas | toxcastEndpoints |
| --- | --- |
| 13252-13-6 | 506 |
| 863090-89-5 | 506 |
| 914637-49-3 | 497 |
| 812-70-4 | 472 |
| 377-73-1 | 470 |

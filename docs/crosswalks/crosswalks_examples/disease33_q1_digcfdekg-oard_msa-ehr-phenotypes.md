# D33-Q1: CFDE-modelled multiple system atrophy + OARD real-world EHR phenotype profile

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × oard-kg (Open Annotations for Rare Diseases), joined on the shared MONDO disease (EFO/Orphanet→MONDO bridge available for non-MONDO-coded CFDE diseases). OARD carries disease→phenotype associations mined from real-world EHR cohorts, each with a log-odds ratio.

Research question: For multiple system atrophy — a disease CFDE REVEAL models genetically — what is its real-world clinical phenotype profile in OARD's EHR cohorts (most-enriched phenotypes by log-odds ratio)?

Why the join is required: digcfdekg has the genetic (PIGEAN gene→trait) model but no clinical phenotype data; OARD has the EHR phenotype enrichment but no genetics. Pairing CFDE's genetic model of a disease with its real-world clinical signature requires joining the two graphs on the shared MONDO disease.

---

🧠 **Assistant**

OARD's most EHR-enriched phenotypes (by log-odds ratio) for multiple system atrophy (MONDO_0007803), a disease CFDE REVEAL also models genetically:

| EHR phenotype (OARD) | log-odds ratio |
|---|---|
| Orthostatic hypotension | 10.88 |
| Hypotension | 6.71 |
| Olivopontocerebellar atrophy | 6.47 |
| Orthostatic syncope | 5.73 |
| Hot cross bun sign | 5.70 |
| Autonomic erectile dysfunction | 5.03 |
| Hypermetric saccades | 4.85 |
| Anhidrosis | 4.80 |
| Abnormal autonomic nervous system physiology | 4.62 |
| Hypometric saccades | 4.43 |
| Abnormal pyramidal sign | 4.22 |
| Orthostatic tachycardia | 4.16 |

On the CFDE side, PIGEAN infers genes including CRHR1, EDN1 (endothelin-1, vascular/autonomic tone), GAB1, RABGEF1 and FBXO47 for the same disease.

Why this answers the question: OARD's EHR signature is the textbook MSA clinical picture — autonomic failure (orthostatic hypotension at the top, orthostatic syncope, anhidrosis, autonomic erectile dysfunction) plus cerebellar/parkinsonian features (olivopontocerebellar atrophy, the pathognomonic "hot cross bun sign" on MRI, hyper-/hypometric saccades, pyramidal signs). Pairing this real-world clinical signature with CFDE's inferred genetic drivers (e.g. EDN1 in autonomic vascular control) is only possible by joining the genetic and clinical graphs on the shared MONDO disease.

Literature validation (PubMed): "multiple system atrophy AND (orthostatic hypotension OR hot cross bun sign OR autonomic failure)" returns 1,214 records (e.g. PMIDs 42318805, 42296842), confirming this clinical signature.

#### Query 1 — OARD EHR phenotypes for multiple system atrophy (gated by CFDE coverage)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
# digcfdekg x oard-kg on the shared MONDO disease (multiple system atrophy, MONDO_0007803).
# OARD's most EHR-enriched phenotypes (log-odds ratio) for the disease CFDE REVEAL also models genetically.
SELECT ?hpLabel ?lor WHERE {
  FILTER EXISTS { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?st rdf:predicate dig:geneToTrait ; rdf:object <http://purl.obolibrary.org/obo/MONDO_0007803> } }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
    ?assoc biolink:category biolink:DiseaseToPhenotypicFeatureAssociation ;
           biolink:subject <http://purl.obolibrary.org/obo/MONDO_0007803> ;
           biolink:predicate biolink:positively_correlated_with ;
           biolink:object ?hp ;
           biolink:has_supporting_studies ?study .
    ?study biolink:has_study_results ?res . ?res biolink:log_odds_ratio ?lor .
    FILTER(?lor < 100)
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?hp rdfs:label ?hpLabel . }
} ORDER BY DESC(?lor) LIMIT 12
```

_12 row(s) — showing first 5_

| hpLabel | lor |
| --- | --- |
| Orthostatic hypotension | 10.879 |
| Hypotension | 6.71216 |
| Olivopontocerebellar atrophy | 6.46725 |
| Orthostatic syncope | 5.72913 |
| Hot cross bun sign | 5.70148 |

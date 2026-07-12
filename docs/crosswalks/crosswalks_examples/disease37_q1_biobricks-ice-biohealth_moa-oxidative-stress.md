# An ICE toxicological mode-of-action, resolved to the clinical conditions biohealth attaches

- **Date:** 2026-07-11
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice>
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>

## Conversation

👤 **User**

Crosswalk: `biobricks-ice` × `biohealth` on **UMLS** (new cross-domain link). BioBricks-ICE tags each assay's NCI mechanistic target with a UMLS concept via `ice:throughMechanisticTarget_NCIm` (a URL-encoded `identifiers.org/umls:...C{cui}` value). BioHealthKG's nodes ARE their UMLS CUIs (`biohealthkg.proto-okn.net/kg/node/C{cui}`) and carry clinical edges (`biolink:causes`, `coexists_with`, `affects`). Extract the C{cui} and rebuild the biohealth node IRI.

Research question: for a toxicological mode-of-action ICE assays report on — **oxidative stress** (UMLS C0242606) — what clinical conditions does biohealth's literature graph attach to that same concept?

Why the join is required: ICE knows *which mechanism an assay probes*; biohealth knows that mechanism's clinical consequences. The shared UMLS concept connects a tox mode-of-action to disease.

---

🧠 **Assistant**

The UMLS bridge carries an ICE mode-of-action into clinical health: ICE's mechanistic-target concept *Oxidative Stress* resolves to the biohealth concept, whose clinical edges name the conditions. Every row carries BOTH graphs — the ICE mechanistic target and a biohealth-linked condition:

| ICE mechanistic target (UMLS) | biohealth relation | biohealth linked condition |
| --- | --- | --- |
| Oxidative Stress (C0242606) | causes | Congenital Abnormality |
| Oxidative Stress (C0242606) | causes | Spontaneous abortion |
| Oxidative Stress (C0242606) | causes | Acidosis, Lactic |
| Oxidative Stress (C0242606) | coexists_with | Abetalipoproteinemia |
| Oxidative Stress (C0242606) | affects / causes | Acne Vulgaris |

**Why it answers the question.** Oxidative stress is a mechanistic target ICE assays measure (e.g. Nrf2/ARE, redox-stress endpoints); biohealth's literature graph attaches the clinical consequences of that same concept — it **causes** congenital abnormality and spontaneous abortion and lactic acidosis, and **coexists with** metabolic disorders. So a chemical that triggers oxidative stress in ICE screening is, through the shared UMLS concept, mechanistically tied to these documented reproductive/developmental and metabolic outcomes. This adverse-outcome context is exactly what a tox assay result lacks and biohealth supplies.

#### Query 1 — ICE's oxidative-stress mechanism joined to biohealth conditions

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ice: <https://ice.ntp.niehs.nih.gov/property/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?rel ?condition WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?a ice:throughMechanisticTarget_NCIm ?u . FILTER(CONTAINS(STR(?u),'C0242606')) }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    <https://biohealthkg.proto-okn.net/kg/node/C0242606> ?r ?t . ?t rdfs:label ?condition .
    FILTER(?r IN (biolink:causes, biolink:coexists_with, biolink:affects))
    BIND(REPLACE(STR(?r),'.*/','') AS ?rel) }
} LIMIT 20
```

_Both-graph rows: *Oxidative Stress* (C0242606) is an ICE `throughMechanisticTarget_NCIm` concept AND a biohealth node whose clinical edges include causes → Congenital Abnormality / Spontaneous abortion._

## Literature validation

According to PubMed, oxidative stress is a well-established mechanism in adverse pregnancy outcomes including spontaneous abortion and congenital malformation — corroborating the biohealth *Oxidative Stress* → Spontaneous abortion / Congenital Abnormality edges joined to ICE's oxidative-stress mechanistic target (Agarwal A, Aponte-Mellado A, Premkumar BJ, Shaman A, Gupta S, "The effects of oxidative stress on female reproduction: a review," *Reproductive Biology and Endocrinology* 10:49, 2012; [DOI](https://doi.org/10.1186/1477-7827-10-49)). **Validated** (literature-corroborated; shared UMLS bridge; both-KG rows executed).

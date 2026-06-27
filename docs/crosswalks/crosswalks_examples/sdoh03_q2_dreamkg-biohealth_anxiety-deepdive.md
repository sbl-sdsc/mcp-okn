# SDOH03-Q2: Anxiety — a DREAM-KG service target resolved to biohealth's clinical network

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>

## Conversation

👤 **User**

Crosswalk: dreamkg × biohealth on the concept label. Take a single DREAM-KG service audience — **anxiety** — and resolve it through biohealth to the clinical concept network: what does biohealth say *Anxiety* coexists with, and what does it cause?

Research question: For a mental-health condition that DREAM-KG offers local services for, what comorbidities and downstream effects does biohealth's UMLS graph attach to it?

Why the join is required: DREAM-KG records only that a mental-health service targets "anxiety"; it has no clinical context. biohealth carries the UMLS concept *Anxiety* and its `biolink:coexists_with` / `biolink:causes` edges but no service listings. Turning "there is a service for anxiety here" into "and here is the clinical company anxiety keeps" needs the label join.

---

🧠 **Assistant**

DREAM-KG targets **anxiety** with mental-health services (its mental-health listings derive from the AuntBertha Philadelphia directory). Resolving that term to biohealth's *Anxiety* concept exposes a dense clinical network:

- **coexists_with:** Anxiety Disorders, Separation Anxiety Disorder, Agoraphobia, Affective Disorders (Psychotic), alcohol use disorder, Chronic Alcoholic Intoxication, Alexithymia, Antisocial Personality Disorder, Anorexia Nervosa, Alzheimer's Disease, Anemia (incl. Sickle Cell), Alopecia, Acne Vulgaris, Psoriatic Arthritis…
- **causes:** Alkalosis, Anemia, Arthritis, Alzheimer's Disease…

Why this answers the question: the bridge turns a single local-service tag into a clinically grounded profile. biohealth situates *Anxiety* among its psychiatric comorbidities (agoraphobia, separation-anxiety and other anxiety disorders, alexithymia, antisocial personality disorder), its substance-use overlap (alcohol use disorder, chronic alcoholic intoxication), and even somatic associations (anemia, alkalosis) — the kind of context a social-service navigator or researcher would want when designing or studying support for the population DREAM-KG serves. None of this clinical structure exists in DREAM-KG; it is reachable only by joining the social-services term to biohealth's concept graph on the label.

Literature validation (PubMed): the comorbidity of anxiety with alcohol-use disorder and with other anxiety/affective disorders is a well-established clinical finding; anxiety–depression and anxiety–substance-use co-occurrence are among the most documented comorbidity patterns in psychiatry.

#### Query 1 — DREAM-KG audience "anxiety" → biohealth *Anxiety* clinical network

```sparql
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?rel ?targetLabel WHERE {
  # confirm DREAM-KG offers a service for this audience
  { SELECT DISTINCT ?aud WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?s schema:audienceType ?aud . FILTER(?aud = "anxiety") } } }
  BIND(CONCAT(UCASE(SUBSTR(?aud,1,1)), SUBSTR(?aud,2)) AS ?cap)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh rdfs:label ?cap .
    VALUES ?rel { biolink:coexists_with biolink:causes }
    ?bh ?rel ?t . ?t rdfs:label ?targetLabel .
  }
} ORDER BY ?targetLabel LIMIT 20
```

_20 row(s) — showing first 5_

| rel | targetLabel |
| --- | --- |
| coexists_with | Acne Vulgaris |
| coexists_with | Affective Disorders, Psychotic |
| coexists_with | Agoraphobia |
| coexists_with | alcohol use disorder |
| coexists_with | Alcoholic Intoxication, Chronic |

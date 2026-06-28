# CW14-Q1 biobricks-mesh×spoke-okn (MeSH) — SDoH nodes resolved to authoritative MeSH definitions

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biobricks-mesh` — <https://purl.org/okn/frink/kg/biobricks-mesh>

## Conversation

👤 **User**

CW14 (biobricks-mesh × spoke-okn, shared key MeSH descriptor id), Q1: For each spoke-okn social-determinants-of-health (SDoH) node, what is its MeSH descriptor and the authoritative NLM definition (scopeNote)? Why the join, and what is the IRI gotcha?

---

🧠 **Assistant**

**Crosswalk:** biobricks-mesh × spoke-okn · **Shared identifier:** MeSH descriptor id. spoke-okn tags its County-Health-Rankings SDoH nodes with MeSH via `schema/mesh_ids` (HTTPS IRIs); biobricks-mesh stores each descriptor as an HTTP node IRI whose `preferredConcept` carries the authoritative `vocab#scopeNote` definition.

**Why the join is required:** spoke-okn holds the SDoH node (its County-Health-Rankings label) but no formal semantics; biobricks-mesh holds NLM's controlled-vocabulary definition but does not know spoke's nodes. Crucially, these SDoH concepts have *no MONDO/DOID equivalent*, so they are invisible to every other disease crosswalk — only the MeSH join reaches them and attaches a real, authoritative definition.

**IRI gotcha (iteration):** spoke-okn stores `https://id.nlm.nih.gov/mesh/...` while biobricks-mesh uses `http://...`. A naive join silently returns nothing; the query rewrites HTTPS→HTTP with `BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/', ?id)))` before matching. A second hop is also needed: the definition lives on the descriptor's `mv:preferredConcept`, not the descriptor node itself.

**Result (verified):** 10 rows, non-empty, each a real spoke-okn SDoH node paired with its MeSH descriptor and the authoritative MeSH definition. Sample:

| spoke-okn SDoH node | MeSH descriptor | authoritative MeSH definition (scopeNote) |
|---|---|---|
| CHR_children_in_poverty | Child Poverty | A situation of children (ages 0-17 inclusive) living in households with income below the U.S. Department of Health and Human Services Federal Poverty Threshold, often leading to a lack of food, sanitation, shelter, health care and education needed to survive and thrive. |
| CHR_uninsured | Medically Uninsured | Individuals or groups with no or inadequate health insurance coverage. Those falling into this category usually comprise three primary groups: the medically indigent; those whose clinical condition makes them medically uninsurable; and the working uninsured. |
| CHR_limited_access_to_healthy_foods | Access to Healthy Foods | Convenient availability to affordable foods that support healthy eating patterns. Access may be limited due to having a limited income or living far away from sources of healthful and affordable food. |
| CHR_preventable_hospital_stays | Ambulatory Care Sensitive Conditions | Various health conditions in OUTPATIENT CARE settings for which adequate management, treatment and interventions delivered in the ambulatory care setting could potentially prevent HOSPITALIZATION. |
| CDCSVI | Social Vulnerability | The characteristics of a person or community that affect their capacity to anticipate, confront, repair, and recover from the effects of a natural or human-caused disaster. |

**Why these rows answer the question:** each spoke-okn SDoH indicator is resolved to its formal MeSH descriptor and its full authoritative NLM definition — real semantics on both sides of the row, not a count, and a layer no MONDO/DOID route can reach.

## SPARQL query executed

#### Query 1

_2026-06-27 · `spoke-okn`, `biobricks-mesh`_

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX mv: <http://id.nlm.nih.gov/mesh/vocab#>
# CW14 (biobricks-mesh <-> spoke-okn, shared key MeSH descriptor id) Q1 (SDoH layer):
# For each spoke-okn SDoH node (mesh_ids), pull its MeSH descriptor + the authoritative
# NLM definition (scopeNote on the preferredConcept). Mandatory HTTPS->HTTP rewrite.
SELECT DISTINCT ?spokeNode ?meshLabel ?scopeNote WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?node <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_ids> ?mo .
    BIND(REPLACE(STR(?node),'^.*/','') AS ?spokeNode)
  }
  BIND(REPLACE(STR(?mo),'^https://id.nlm.nih.gov/mesh/','') AS ?id)
  BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/',?id)) AS ?m)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m rdfs:label ?meshLabel ; mv:preferredConcept ?c .
    ?c mv:scopeNote ?scopeNote .
  }
} ORDER BY ?meshLabel LIMIT 15
```

_10 row(s) — showing first 5_

| spokeNode | meshLabel | scopeNote |
| --- | --- | --- |
| CHR_limited_access_to_healthy_foods | Access to Healthy Foods | Convenient availability to affordable foods that support healthy eating patterns… |
| CHR_primary_care_physicians | Access to Primary Care | The degree to which individuals are inhibited or facilitated in their ability to gain entry to and to receive PRIMARY CARE. |
| CHR_teen_births | Adolescent Mothers | Mothers aged less than 19 years at the time of child's conception or birth. |
| CHR_preventable_hospital_stays | Ambulatory Care Sensitive Conditions | Various health conditions in OUTPATIENT CARE settings for which adequate management… could potentially prevent HOSPITALIZATION. |
| CHR_children_in_poverty | Child Poverty | A situation of children (ages 0-17 inclusive) living in households with income below the U.S. … Federal Poverty Threshold… |

## Literature validation

According to PubMed, Nassar et al., *Ear and Hearing* 2025, show that CDC Social Vulnerability Index factors (socioeconomic status, household composition, housing/transportation) are associated with diagnosis, time-to-presentation, and treatment response in a tertiary clinic cohort — confirming the spoke-okn SDoH nodes (Social Vulnerability, Child Poverty, Medically Uninsured) are MeSH-anchored, outcome-relevant health concepts. [PMID:40660454](https://pubmed.ncbi.nlm.nih.gov/40660454/) · [DOI](https://doi.org/10.1097/AUD.0000000000001665) **Kept.**

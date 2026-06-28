# CW14-Q2 biobricks-mesh×spoke-okn (MeSH) — DOID disease nodes resolved to authoritative MeSH definitions

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biobricks-mesh` — <https://purl.org/okn/frink/kg/biobricks-mesh>

## Conversation

👤 **User**

CW14 (biobricks-mesh × spoke-okn, shared key MeSH descriptor id), Q2: For spoke-okn DOID disease nodes, what is their MeSH descriptor and the authoritative NLM definition (scopeNote)? Why the join?

---

🧠 **Assistant**

**Crosswalk:** biobricks-mesh × spoke-okn · **Shared identifier:** MeSH descriptor id. spoke-okn's DOID-identified disease nodes carry a MeSH tag via `schema/mesh_list` (HTTPS); biobricks-mesh stores the descriptor with `rdfs:label` and an authoritative `vocab#scopeNote` definition on its `preferredConcept`. The query applies the HTTPS→HTTP rewrite and the descriptor→preferredConcept hop.

**Why the join is required:** spoke-okn knows the disease as a DOID but holds no MeSH semantics; biobricks-mesh holds the canonical NLM definition but not spoke's DOID nodes. The join materializes a verified MeSH↔DOID correspondence *and* attaches the authoritative MeSH definition — turning a bare disease node into a literature-indexable, fully-defined concept.

**Result (verified):** 15 rows, non-empty, each a real spoke-okn DOID disease paired with its MeSH descriptor and the authoritative MeSH definition. Sample:

| spoke-okn disease | MeSH descriptor | authoritative MeSH definition (scopeNote) |
|---|---|---|
| Alzheimer's disease | Alzheimer Disease | A degenerative disease of the BRAIN characterized by the insidious onset of DEMENTIA … marked pathologically by severe cortical atrophy and the triad of SENILE PLAQUES; NEUROFIBRILLARY TANGLES; and NEUROPIL THREADS. |
| asthma | Asthma | A form of bronchial disorder with three distinct components: airway hyper-responsiveness, airway INFLAMMATION, and intermittent AIRWAY OBSTRUCTION … WHEEZING, and dyspnea. |
| appendicitis | Appendicitis | Acute inflammation of the APPENDIX. Acute appendicitis is classified as simple, gangrenous, or perforated. |
| acute myeloid leukemia | Leukemia, Myeloid, Acute | Clonal expansion of myeloid blasts in bone marrow, blood, and other tissue … develop from changes in cells that normally produce NEUTROPHILS; BASOPHILS; EOSINOPHILS; and MONOCYTES. |
| arteriosclerosis | Arteriosclerosis | Thickening and loss of elasticity of the walls of ARTERIES of all sizes … such as ATHEROSCLEROSIS with fatty lesions in the ARTERIAL INTIMA. |

**Why these rows answer the question:** each DOID disease is resolved to its canonical NLM MeSH descriptor and its full authoritative definition — real semantics on both sides of the row, and a reusable MeSH↔DOID bridge for MeSH-indexed literature retrieval keyed off a DOID disease.

## SPARQL query executed

#### Query 1

_2026-06-27 · `spoke-okn`, `biobricks-mesh`_

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX mv: <http://id.nlm.nih.gov/mesh/vocab#>
# CW14 (biobricks-mesh <-> spoke-okn, shared key MeSH descriptor id) Q2 (disease layer):
# For spoke-okn DOID disease nodes (mesh_list), pull their MeSH descriptor + the
# authoritative NLM definition (scopeNote on preferredConcept). Mandatory HTTPS->HTTP rewrite.
SELECT DISTINCT ?diseaseLabel ?meshLabel ?scopeNote WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?doid a <https://w3id.org/biolink/vocab/Disease> ; rdfs:label ?diseaseLabel ;
          <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_list> ?mo .
    FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_'))
  }
  BIND(REPLACE(STR(?mo),'^https://id.nlm.nih.gov/mesh/','') AS ?id)
  BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/',?id)) AS ?m)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m rdfs:label ?meshLabel ; mv:preferredConcept ?c .
    ?c mv:scopeNote ?scopeNote .
  }
} ORDER BY ?diseaseLabel LIMIT 15
```

_15 row(s) — showing first 5_

| diseaseLabel | meshLabel | scopeNote |
| --- | --- | --- |
| acne | Acne Vulgaris | A chronic disorder of the pilosebaceous apparatus associated with an increase in sebum secretion … open comedones (blackheads), closed comedones (whiteheads), and pustular nodules. |
| acute myeloid leukemia | Leukemia, Myeloid, Acute | Clonal expansion of myeloid blasts in bone marrow, blood, and other tissue … |
| alcohol use disorder | Alcoholism | A primary, chronic disease with genetic, psychosocial, and environmental factors … impaired control over drinking, preoccupation with the drug alcohol … |
| Alzheimer's disease | Alzheimer Disease | A degenerative disease of the BRAIN characterized by the insidious onset of DEMENTIA … |
| anxiety disorder | Anxiety Disorders | Persistent and disabling ANXIETY. |

## Literature validation

According to PubMed, Bramer et al., *Journal of the Medical Library Association* 2018, describe a replicable method for building exhaustive biomedical literature searches built on MeSH thesaurus terms and controlled vocabulary — validating that the authoritative MeSH descriptor + definition attached to each spoke-okn DOID disease is the canonical anchor for MeSH-indexed literature retrieval. [PMID:30271302](https://pubmed.ncbi.nlm.nih.gov/30271302/) · [DOI](https://doi.org/10.5195/jmla.2018.283) **Kept.**

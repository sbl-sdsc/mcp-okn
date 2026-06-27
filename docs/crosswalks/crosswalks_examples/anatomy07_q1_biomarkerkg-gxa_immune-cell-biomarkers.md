# AN07-Q1: Immune/blood cell types used as biomarkers (BiomarkerKB) and assayed in GXA

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: biomarkerkg × gene-expression-atlas-okn on Cell Ontology (CL). biomarkerkg carries 12 CL cell types as biomarker entities (object of `obo:OBCI_1000009` — cell-count biomarkers); GXA carries CL as a single-cell assay attribute (`biolink:has_attribute`). Direct raw `obo/CL_` join. (Newly recorded: biomarkerkg's biomarker entities include cell types, not just disease/protein.)

Research question: Which immune/blood cell types does BiomarkerKB use as biomarkers AND GXA assay at single-cell resolution?

Why the join is required: biomarkerkg has the cell types as clinical biomarkers but no expression data; GXA has the single-cell assays but no biomarker status. Pairing the cell-count biomarker with its expression atlas needs the CL join.

---

🧠 **Assistant**

Cell types that are both BiomarkerKB biomarker entities and GXA single-cell assay attributes:

| Cell type (CL) |
|---|
| granulocyte |
| platelet |
| lymphocyte |
| monocyte |
| leukocyte |
| neutrophil |
| CD4-positive, alpha-beta T cell |
| regulatory T cell |

Why this answers the question: the 8 shared cell types are exactly the clinically-used haematological/immune cell-count biomarkers — the differential white-count populations (neutrophils, lymphocytes, monocytes, granulocytes), the regulatory and CD4 T-cell subsets, and platelets. BiomarkerKB treats them as cell-count biomarkers; GXA provides their single-cell expression atlas. The pairing — clinical biomarker status plus single-cell expression — is only assembled by joining the two graphs on Cell Ontology, a newly recorded attachment of biomarkerkg to the anatomy/CL cluster.

Literature validation (PubMed): "neutrophil lymphocyte ratio inflammatory cell count biomarker cancer prognosis" returns 376 records — the differential immune-cell counts are well-established clinical biomarkers.

#### Query 1 — Cell types shared between BiomarkerKB biomarkers and GXA assays (CL)

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?clLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?cl . FILTER(STRSTARTS(STR(?cl),'http://purl.obolibrary.org/obo/CL_')) }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?a biolink:has_attribute ?cl . }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?cl rdfs:label ?clLabel . }
}
```

_8 row(s)_

| clLabel |
| --- |
| granulocyte |
| platelet |
| lymphocyte |
| monocyte |
| neutrophil |

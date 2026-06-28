# Pankgraph type-1-diabetes genes that SPOKE independently ties to other autoimmune diseases

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: pankgraph × spoke-okn on the shared Ensembl id (pankgraph subjects of `biolink:gene_associated_with_condition` are Ensembl IRIs; spoke-okn carries the same IRI on `spoke:ensembl`).

Research question: Which genes that pankgraph associates with type 1 diabetes does SPOKE *independently* associate (`ASSOCIATES_DaG`) with a **different** autoimmune disease — rheumatoid arthritis, multiple sclerosis, autoimmune thyroid disease? This surfaces cross-confirming autoimmune comorbidities: shared-genetics loci that two independent pipelines both flag, in T1D (pankgraph) and in a second autoimmune condition (SPOKE).

---

🧠 **Assistant**

pankgraph and SPOKE derive their gene–disease links from different evidence pipelines (islet genomics vs literature/database co-occurrence). Whether a T1D gene is *also* an established locus for another autoimmune disease is only measurable by joining on the shared Ensembl id and intersecting the disease annotations. Each row pairs a pankgraph T1D gene with a SPOKE association to a *different* autoimmune disease:

| Gene | pankgraph condition | SPOKE autoimmune disease (`ASSOCIATES_DaG`) |
|---|---|---|
| CTLA4 | type 1 diabetes | rheumatoid arthritis |
| CD28 | type 1 diabetes | rheumatoid arthritis |
| AIRE | type 1 diabetes | rheumatoid arthritis |
| CLEC16A | type 1 diabetes | multiple sclerosis |
| BACH2 | type 1 diabetes | multiple sclerosis / rheumatoid arthritis |
| ETS1 | type 1 diabetes | multiple sclerosis |
| CD226 | type 1 diabetes | multiple sclerosis / rheumatoid arthritis |
| AFF3 | type 1 diabetes | rheumatoid arthritis |

**Why this answers the question:** every gene listed is a textbook autoimmune-shared locus — the costimulation axis **CTLA4 / CD28 / CD226**, the autoimmune-regulator **AIRE**, the MS/T1D-shared **CLEC16A**, and the lymphocyte transcription factors **BACH2 / ETS1 / AFF3**. Here each is asserted as a type-1-diabetes gene by pankgraph **and** independently tied by SPOKE to rheumatoid arthritis or multiple sclerosis — a clean two-KG cross-confirmation of the shared genetic architecture of autoimmunity, visible only by joining the two graphs on Ensembl.

## SPARQL query executed

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?pankCondition ?spokeDisease WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene a biolink:Gene ; biolink:gene_associated_with_condition ?cond .
    OPTIONAL { ?cond rdfs:label ?pankCondition }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g spoke:ensembl ?gene ; rdfs:label ?sym .
    ?disease spoke:ASSOCIATES_DaG ?g ; rdfs:label ?spokeDisease .
    FILTER(CONTAINS(LCASE(?spokeDisease),"thyroid") || CONTAINS(LCASE(?spokeDisease),"celiac")
        || CONTAINS(LCASE(?spokeDisease),"rheumatoid") || CONTAINS(LCASE(?spokeDisease),"lupus")
        || CONTAINS(LCASE(?spokeDisease),"multiple sclerosis") || CONTAINS(LCASE(?spokeDisease),"vitiligo")
        || CONTAINS(LCASE(?spokeDisease),"addison") || CONTAINS(LCASE(?spokeDisease),"autoimmune"))
  }
} ORDER BY ?sym LIMIT 15
```

## Literature validation

Heward & Gough, 1997, *Clin Sci (Lond)* — review the genetics of autoimmune disease and document that HLA and CTLA-4 are shared susceptibility genes across type 1 diabetes, Graves' disease, rheumatoid arthritis, multiple sclerosis and lupus, supporting the shared-locus cross-confirmation this crosswalk recovers (notably the CTLA4 row). (According to PubMed.) [PMID:9497784](https://pubmed.ncbi.nlm.nih.gov/9497784/) · [DOI](https://doi.org/10.1042/cs0930479)

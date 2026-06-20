# CW3-Q1: Three-way gene dossier (pankgraph T1D + GXA + SPOKE)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: gene-expression-atlas-okn × pankgraph × spoke-okn, all joined on the shared Ensembl gene id (pankgraph and GXA genes ARE Ensembl IRIs; spoke-okn carries the Ensembl IRI as the object of schema:ensembl).

Research question: For genes that pankgraph (PanKbase islet/pancreas resource) associates with type 1 diabetes, and that are also measured in the Gene Expression Atlas, what independent human disease associations does SPOKE record? In other words, build a one-query cross-KG dossier for diabetes genes.

Why the join is required: pankgraph holds the islet/diabetes gene-condition associations, GXA holds the expression catalog, and SPOKE holds the broader gene-disease association network. No single graph has all three. The dossier is only assemblable by a 3-way Ensembl join.

---

🧠 **Assistant**

Three-way dossier for pankgraph T1D-associated genes that are GXA-measured, showing their SPOKE disease associations. Coherent autoimmune highlights:

| Gene | pankgraph condition | SPOKE disease associations |
|---|---|---|
| AIRE | type 1 diabetes | diabetes mellitus, rheumatoid arthritis, pancreatitis, alopecia areata, hepatitis, dermatitis |
| BACH2 | type 1 diabetes | multiple sclerosis, rheumatoid arthritis, asthma |
| ADCY3 | type 1 diabetes | obesity, inflammatory bowel disease, multiple sclerosis |
| AFF3 | type 1 diabetes | rheumatoid arthritis, COPD, endometriosis |

Why this answers the question: AIRE (the Autoimmune Regulator, mutated in APECED) is pankgraph-linked to T1D and SPOKE independently links it to diabetes mellitus plus a cluster of autoimmune conditions (RA, alopecia areata, dermatitis) — exactly the autoimmune-polyendocrine phenotype AIRE is known for. BACH2 (a T1D/autoimmunity transcription factor) shows the same autoimmune cluster. The dossier — diabetes gene + expression presence + autoimmune disease network — is only assemblable by joining all three KGs on Ensembl.

Literature validation (PubMed): AIRE in type 1 diabetes / autoimmunity returns 89 records (e.g. PMIDs 35690244, 25905375); BACH2 in type 1 diabetes returns 17 records (e.g. PMIDs 34127860, 30970177). Both gene-disease links are well supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `pankgraph`, `gene-expression-atlas-okn`, `spoke-okn`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?geneLabel ?pankCondition ?spokeDisease WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene a biolink:Gene ; biolink:gene_associated_with_condition ?cond .
    OPTIONAL { ?cond rdfs:label ?pankCondition }
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?gene a biolink:Gene ; biolink:symbol ?geneLabel .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g2 spoke:ensembl ?gene .
    ?disease spoke:ASSOCIATES_DaG ?g2 ; rdfs:label ?spokeDisease .
  }
} ORDER BY ?geneLabel LIMIT 25
```

_25 row(s) — showing first 5_

| geneLabel | pankCondition | spokeDisease |
| --- | --- | --- |
| ADCY3 | type 1 diabetes | inflammatory bowel disease |
| ADCY3 | type 1 diabetes | multiple sclerosis |
| ADCY3 | type 1 diabetes | nutrition disease |
| ADCY3 | type 1 diabetes | obesity |
| ADCY3 | type 1 diabetes | breast carcinoma |

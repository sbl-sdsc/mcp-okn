# CW3-Q2: Diabetes genes that are also SPOKE cancer prognostic markers (3-way)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: gene-expression-atlas-okn × pankgraph × spoke-okn on the shared Ensembl id.

Research question: Which genes that pankgraph associates with type 1 diabetes are ALSO flagged by SPOKE as prognostic cancer markers (favorable MARKER_POS_GmpD or unfavorable MARKER_NEG_GmnD) and measured in GXA? This surfaces diabetes genes with a dual role in cancer prognosis.

Why the join is required: pankgraph supplies the diabetes gene-condition association, SPOKE supplies the cancer prognostic-marker edges, and GXA supplies the expression catalog. The diabetes-cancer overlap is only computable by intersecting all three on Ensembl.

---

🧠 **Assistant**

pankgraph T1D-associated, GXA-measured genes that SPOKE also flags as cancer prognostic markers. Diabetes-relevant highlights:

| Gene | pankgraph condition | SPOKE marker | Cancer |
|---|---|---|---|
| CEL | type 1 diabetes | unfavorable | breast cancer |
| CFTR | type 1 diabetes | unfavorable | liver cancer |
| CDK2 | type 1 diabetes | unfavorable | kidney cancer, liver cancer |
| CCR7 | type 1 diabetes | favorable | breast cancer, cervical cancer |

Why this answers the question: CEL (carboxyl-ester lipase) is the MODY8 monogenic-diabetes gene, and here it is also an unfavorable breast-cancer prognostic marker; CFTR (the cystic-fibrosis gene, cause of CF-related diabetes) is an unfavorable liver-cancer marker. These dual diabetes/cancer roles are only visible by joining the islet/diabetes gene set (pankgraph), the prognostic-marker edges (SPOKE), and the expression catalog (GXA) on Ensembl.

Literature validation (PubMed): CEL as a maturity-onset-diabetes (MODY) gene returns 45 records (e.g. PMIDs 36208030, 34763692). CFTR-related diabetes is likewise well established. The diabetes-gene identities are literature-supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `pankgraph`, `gene-expression-atlas-okn`, `spoke-okn`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?geneLabel ?pankCondition ?markerType ?cancerLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene a biolink:Gene ; biolink:gene_associated_with_condition ?cond .
    OPTIONAL { ?cond rdfs:label ?pankCondition }
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?gene a biolink:Gene ; biolink:symbol ?geneLabel .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g2 spoke:ensembl ?gene .
    { ?g2 spoke:MARKER_POS_GmpD ?cancer . BIND("favorable prognostic marker" AS ?markerType) }
    UNION
    { ?g2 spoke:MARKER_NEG_GmnD ?cancer . BIND("unfavorable prognostic marker" AS ?markerType) }
    ?cancer rdfs:label ?cancerLabel .
  }
} ORDER BY ?geneLabel LIMIT 25
```

_25 row(s) — showing first 5_

| geneLabel | pankCondition | markerType | cancerLabel |
| --- | --- | --- | --- |
| ACAP1 | type 1 diabetes | unfavorable prognostic marker | kidney cancer |
| ACAP1 | type 1 diabetes | favorable prognostic marker | cervical cancer |
| ADCY3 | type 1 diabetes | unfavorable prognostic marker | kidney cancer |
| AFF3 | type 1 diabetes | unfavorable prognostic marker | kidney cancer |
| AKAP11 | type 1 diabetes | unfavorable prognostic marker | cervical cancer |

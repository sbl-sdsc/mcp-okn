# CW5-Q1: SPOKE chemical modulators of pankgraph diabetes-associated genes

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: pankgraph × spoke-okn on the shared Ensembl id.

Research question: For genes pankgraph associates with type 1 diabetes, which chemical compounds does SPOKE record as up- or down-regulating them? This surfaces candidate chemical modulators (and environmental exposures) of diabetes-associated genes.

Why the join is required: pankgraph supplies the diabetes gene-condition link but no compound pharmacology; SPOKE supplies compound->gene regulation edges but no diabetes context. The 'what chemicals modulate diabetes genes' question requires the Ensembl join.

---

🧠 **Assistant**

pankgraph T1D-associated genes paired with SPOKE compound regulators. Highlights:

| Gene | pankgraph condition | Regulation | Compound |
|---|---|---|---|
| HLA-DRA | type 1 diabetes | up/down | Thiabendazole, Resorcinol, Phenytoin, Pentobarbital |
| ERBB3 | type 1 diabetes | up | Tributyltin chloride, Phenytoin, Fluorouracil |
| CDK2 | type 1 diabetes | up/down | Fluorouracil, Hexachlorophene |
| ETS1 | type 1 diabetes | up/down | Fluorouracil, Hexachlorophene |

Why this answers the question: HLA-DRA (the MHC class-II gene central to T1D autoimmunity) and ERBB3 (a well-replicated T1D risk locus) are both pankgraph T1D genes, and SPOKE lists specific compounds that modulate their expression — directly answering 'what chemicals modulate diabetes genes'. The mapping only exists by joining pankgraph's diabetes gene set to SPOKE's compound-gene edges on Ensembl.

Literature validation (PubMed): ERBB3 as a type-1-diabetes risk locus returns 5 PubMed records (e.g. PMIDs 29109006, 19956108); HLA class II (HLA-DRA) is the canonical T1D susceptibility region. The diabetes-gene identities are literature-supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `pankgraph`, `spoke-okn`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?pankCondition ?regulation ?compound WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene a biolink:Gene ; biolink:gene_associated_with_condition ?cond .
    OPTIONAL { ?cond rdfs:label ?pankCondition }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g spoke:ensembl ?gene ; rdfs:label ?sym .
    { ?cmpd spoke:UPREGULATES_CuG ?g . BIND("upregulates" AS ?regulation) }
    UNION
    { ?cmpd spoke:DOWNREGULATES_CdG ?g . BIND("downregulates" AS ?regulation) }
    ?cmpd rdfs:label ?compound .
  }
} ORDER BY ?sym LIMIT 25
```

_25 row(s) — showing first 5_

| sym | pankCondition | regulation | compound |
| --- | --- | --- | --- |
| BCL2L11 | type 1 diabetes | upregulates | Pentobarbital |
| CDK2 | type 1 diabetes | downregulates | Hexachlorophene |
| CDK2 | type 1 diabetes | downregulates | Pentobarbital |
| CDK2 | type 1 diabetes | upregulates | Fluorouracil |
| DYRK3 | type 1 diabetes | upregulates | Fluorouracil |

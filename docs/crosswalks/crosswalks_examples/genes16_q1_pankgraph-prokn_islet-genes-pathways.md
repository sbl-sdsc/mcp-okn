# G16-Q1: pankgraph islet genes annotated with ProKN MSigDB pathways (Ensembl join)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: pankgraph (PanKbase islet KG) × prokn, joined on the Ensembl gene id. **Important:** pankgraph stores its cross-references as **string literals** on `rdfs:seeAlso` (not IRIs), so a naive join returns 0 — convert with `BIND(IRI(STR(?lit)))` and match ProKN's Ensembl gene node. (Newly recorded crosswalk: 37,835 shared Ensembl genes.)

Research question: For the canonical pancreatic-islet genes pankgraph catalogues (INS, PDX1, MAFA, NKX6-1, GCG, ISL1, PAX6, NEUROD1), what MSigDB pathways does ProKN annotate?

Why the join is required: pankgraph supplies the islet gene catalogue (Ensembl + genomic/cell-type context) but no pathway annotation; ProKN supplies MSigDB pathway membership keyed on the Ensembl gene. Attaching pathways to the islet genes needs the Ensembl join.

---

🧠 **Assistant**

Pancreatic-islet genes from pankgraph, with the number of ProKN MSigDB pathways each belongs to (joined on Ensembl, literal→IRI converted):

| Islet gene | # ProKN pathways | Representative pathway |
|---|---|---|
| INS (insulin) | 66 | BRIDEAU_IMPRINTED_GENES |
| PAX6 | 47 | BENPORATH_ES_CORE_NINE_CORRELATED |
| ISL1 | 35 | HCMV / developmental programs |
| GCG (glucagon) | 32 | REACTOME_G_ALPHA_S_SIGNALLING_EVENTS |
| NEUROD1 | 27 | erythroid/neuronal differentiation |
| PDX1 | 27 | developmental / cancer-prognosis programs |
| NKX6-1 | 21 | BENPORATH_ES_WITH_H3K27ME3 |
| MAFA | 15 | REACTOME_DEVELOPMENTAL_BIOLOGY |

Why this answers the question: the join attaches ProKN's pathway knowledge to pankgraph's islet gene set, and the pathways are biologically coherent — GCG (glucagon) sits in the G-alpha-S signalling pathway (the glucagon-receptor cascade), the islet master transcription factors (PDX1, NKX6-1, MAFA, NEUROD1) map to developmental/chromatin programs, and INS to imprinted-gene programs. Neither graph alone gives both the islet-gene catalogue and the pathway membership; the Ensembl join does. The result is only obtainable after converting pankgraph's literal Ensembl ids to IRIs.

Literature validation (PubMed): "(PDX1 OR MAFA OR NKX6-1 OR NEUROD1) pancreatic beta cell identity transcription factor" returns 94 records (e.g. PMIDs 42002316, 41959739); these are the established β-cell identity transcription factors.

#### Query 1 — pankgraph islet genes → ProKN MSigDB pathways (Ensembl, literal→IRI)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym (COUNT(DISTINCT ?pw) AS ?proknPathways) (SAMPLE(?pathway) AS ?examplePathway) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene rdfs:label ?sym ; rdfs:seeAlso ?ensLit .
    FILTER(?sym IN ("PDX1","NKX6-1","MAFA","NEUROD1","INS","GCG","PAX6","ISL1"))
    FILTER(STRSTARTS(STR(?ensLit),'https://www.ensembl.org/id/ENSG'))
  }
  BIND(IRI(STR(?ensLit)) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens <http://purl.obolibrary.org/obo/RO_0002431> ?pw . }
  BIND(REPLACE(STR(?pw),'^.*/MSigDB_','') AS ?pathway)
} GROUP BY ?sym ORDER BY DESC(?proknPathways)
```

_8 row(s) — showing first 5_

| sym | proknPathways | examplePathway |
| --- | --- | --- |
| INS | 66 | BRIDEAU_IMPRINTED_GENES |
| PAX6 | 47 | BENPORATH_ES_CORE_NINE_CORRELATED |
| ISL1 | 35 | BROWNE_HCMV_INFECTION_16HR_UP |
| GCG | 32 | REACTOME_G_ALPHA_S_SIGNALLING_EVENTS |
| NEUROD1 | 27 | RIZ_ERYTHROID_DIFFERENTIATION_6HR |

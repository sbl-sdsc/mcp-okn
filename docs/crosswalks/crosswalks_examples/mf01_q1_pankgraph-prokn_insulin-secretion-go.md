# MF01-Q1: Insulin-secretion GO function shared by pankgraph genes and ProKN proteins

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: pankgraph × prokn on **GO term**. pankgraph annotates its islet genes with GO via `biolink:functional_association` (OBO form) and `rdfs:seeAlso` (QuickGO literal); ProKN annotates its proteins with GO (obo IRIs on RO_0002264/2327/...). The GO term is the shared key (function axis). (Newly recorded: 16,970 shared GO terms.)

Research question: For the GO function "insulin secretion" (GO:0030073), which pancreatic-islet genes (pankgraph) and which proteins (ProKN) are annotated with it?

Why the join is required: pankgraph gives the gene→function annotation, ProKN the protein→function annotation; collecting both the islet genes and the proteins that carry a given function needs the shared GO term.

---

🧠 **Assistant**

Entities annotated with **insulin secretion** (GO:0030073) across the two graphs:

- **pankgraph islet genes (27):** PTPRN, SLC30A8, HNF1A, HNF1B, NEUROD1, MAFA, LEP, FFAR1, RAB3A, RIMS2, CPLX1, SYTL4, STXBP3, CAMK2G, ILDR2, ACVR1C, GAL, VGF, SREBF1, ANXA1, IL1RN, PARK7, FKBP1B, SNX19, SERP1, ACVR2B, CPLX3
- **ProKN proteins:** 21 distinct proteins carry the same GO annotation.

Why this answers the question: the GO join collects, under one function, both pankgraph's islet genes and ProKN's proteins — and the pankgraph set is exactly the insulin-secretion machinery: the granule/exocytosis genes (RAB3A, RIMS2, CPLX1/3, SYTL4, STXBP3), the β-cell transcription factors (HNF1A, HNF1B, NEUROD1, MAFA), the zinc transporter SLC30A8 (ZnT8) and the autoantigen PTPRN (IA-2). Linking islet genes and proteins by shared function — rather than by gene identity — is exactly what the GO crosswalk enables.

Literature validation (PubMed): SLC30A8, PTPRN, HNF1A and the granule-exocytosis genes are established insulin-secretion / type-2-diabetes genes (the T2D gene set returns 1,626 records, see G12-Q1).

#### Query 1 — pankgraph genes + ProKN proteins annotated with insulin secretion (GO:0030073)

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX up: <http://purl.uniprot.org/core/>
SELECT
  (GROUP_CONCAT(DISTINCT ?pankGene; separator=", ") AS ?pankgraphGenes)
  (COUNT(DISTINCT ?prot) AS ?proknProteins) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?g biolink:functional_association ?go . FILTER(STR(?go)='http://purl.obolibrary.org/obo/GO_0030073')
    ?g rdfs:label ?pankGene .
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?prot a up:Protein ; ?pred <http://purl.obolibrary.org/obo/GO_0030073> . }
}
```

_1 aggregate row_

| pankgraphGenes (excerpt) | proknProteins |
| --- | --- |
| PTPRN, SLC30A8, HNF1A, NEUROD1, MAFA, LEP, FFAR1, HNF1B, RAB3A, RIMS2, … | 21 |

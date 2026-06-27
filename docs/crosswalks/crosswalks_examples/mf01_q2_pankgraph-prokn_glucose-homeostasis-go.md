# MF01-Q2: Glucose-homeostasis GO function shared by pankgraph genes and ProKN proteins

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: pankgraph × prokn on **GO term** (function axis; pankgraph `biolink:functional_association` ↔ ProKN protein GO annotations).

Research question: For the GO process "glucose homeostasis" (GO:0042593), which islet genes (pankgraph) and proteins (ProKN) share the annotation?

Why the join is required: pankgraph holds the gene→function side and ProKN the protein→function side; assembling both for a given metabolic process needs the shared GO term.

---

🧠 **Assistant**

Entities annotated with **glucose homeostasis** (GO:0042593):

- **pankgraph islet/metabolic genes (selected):** GCK, WFS1, TCF7L2, G6PC2, MTNR1B, INS, GCG, GCGR, PPARG, HNF1A, IRS1, STAT3, SLC2A4, AKT1, STK11, PRKAA1/2, LEPR, LEP, POMC, ADIPOR1/2, FFAR1/2, TSC22D4 …
- **ProKN proteins:** 92 distinct proteins carry the same GO annotation.

Why this answers the question: the GO join gathers, under "glucose homeostasis," pankgraph's glucose-regulatory genes and ProKN's proteins. The pankgraph set is the canonical glucose-homeostasis / type-2-diabetes panel — the glucose sensor GCK, the strongest T2D GWAS gene TCF7L2, the β-cell genes G6PC2 / MTNR1B / WFS1, the insulin-signalling node IRS1/AKT1, and the master metabolic regulators PPARG, PRKAA1/2 (AMPK), STK11 (LKB1). Connecting these genes to ProKN's 92 functionally-matched proteins is exactly the value of the GO (function) crosswalk.

Literature validation (PubMed): GCK, TCF7L2, WFS1, MTNR1B, G6PC2 are established glucose-homeostasis / type-2-diabetes genes (the T2D gene set returns 1,626 records, G12-Q1; MODY genes 2,237, G14-Q1).

#### Query 1 — pankgraph genes + ProKN proteins annotated with glucose homeostasis (GO:0042593)

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX up: <http://purl.uniprot.org/core/>
SELECT (GROUP_CONCAT(DISTINCT ?pankGene; separator=", ") AS ?pankgraphGenes) (COUNT(DISTINCT ?prot) AS ?proknProteins) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?g biolink:functional_association ?go . FILTER(STR(?go)='http://purl.obolibrary.org/obo/GO_0042593') ?g rdfs:label ?pankGene . }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?prot a up:Protein ; ?pred <http://purl.obolibrary.org/obo/GO_0042593> . }
}
```

_1 aggregate row_

| pankgraphGenes (excerpt) | proknProteins |
| --- | --- |
| GCK, WFS1, TCF7L2, G6PC2, MTNR1B, INS, GCG, PPARG, HNF1A, IRS1, STK11, PRKAA1, … | 92 |

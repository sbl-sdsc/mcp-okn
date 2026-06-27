# G16-Q2: pankgraph islet genes mapped to their protein and HGNC identity via ProKN (Ensembl join)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: pankgraph × prokn on the Ensembl gene id (pankgraph stores Ensembl as a string literal on `rdfs:seeAlso`; convert with `IRI(STR(?lit))`).

Research question: pankgraph identifies its islet genes only by Ensembl gene id — what is the encoded protein (UniProt) and the HGNC identity that ProKN supplies for them?

Why the join is required: pankgraph is Ensembl-only at the gene level; ProKN holds the Ensembl→UniProt→HGNC identity mapping. Resolving a pankgraph islet gene to its protein and HGNC id (so it can be linked to protein-level resources) needs the Ensembl join.

---

🧠 **Assistant**

pankgraph islet genes resolved through ProKN to their encoded protein (UniProt) and HGNC id:

| Islet gene (pankgraph) | UniProt (ProKN) | HGNC (ProKN) |
|---|---|---|
| WFS1 (wolframin) | O76024 | HGNC:12762 |
| GCG (glucagon) | P01275 | HGNC:4191 |

Why this answers the question: pankgraph names the gene and its Ensembl id but stops there; ProKN, reached on the shared Ensembl gene, supplies the encoded protein accession (UniProt) and the HGNC identifier. This turns pankgraph's Ensembl-only islet gene into a fully cross-referenced entity — WFS1 → wolframin (O76024), GCG → glucagon (P01275) — enabling onward links to any UniProt- or HGNC-keyed resource in the federation. The bridge is only available through the Ensembl join (after the literal→IRI conversion).

Literature validation (PubMed): WFS1 (Wolfram syndrome / diabetes) and GCG (glucagon) are well-established islet genes; the type-2-diabetes / MODY islet gene set is extensively documented (see G14-Q1, 2,237 records for MODY genes).

#### Query 1 — pankgraph islet genes → ProKN UniProt protein + HGNC (Ensembl, literal→IRI)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?sym ?uniprot ?hgnc WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene rdfs:label ?sym ; rdfs:seeAlso ?ensLit .
    FILTER(?sym IN ("INS","GCG","SLC30A8","PDX1","TCF7L2","WFS1"))
    FILTER(STRSTARTS(STR(?ensLit),'https://www.ensembl.org/id/ENSG'))
  }
  BIND(IRI(STR(?ensLit)) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?ens sio:SIO_010078 ?uniprot ; skos:exactMatch ?hgnc .
    FILTER(CONTAINS(STR(?uniprot),'uniprot')) FILTER(CONTAINS(STR(?hgnc),'hgnc'))
  }
} LIMIT 12
```

_rows (genes carrying both a ProKN UniProt and HGNC link)_

| sym | uniprot | hgnc |
| --- | --- | --- |
| WFS1 | http://purl.uniprot.org/uniprot/O76024 | http://identifiers.org/hgnc/12762 |
| GCG | http://purl.uniprot.org/uniprot/P01275 | http://identifiers.org/hgnc/4191 |

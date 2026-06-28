# pankgraph islet genes paired with their named ProKN β-cell / islet pathway (Ensembl join)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: pankgraph (PanKbase islet KG) × prokn (Protein Knowledge Network / ProteinKG), joined on the Ensembl gene id. **Important:** pankgraph stores its cross-references as **string literals** on `rdfs:seeAlso` (not IRIs), so a naive join returns 0 — convert with `BIND(IRI(STR(?lit)))` and match ProKN's Ensembl gene node. (Verified crosswalk: 37,835 shared Ensembl genes.)

Research question: For the canonical pancreatic-islet genes pankgraph catalogues (INS, PDX1, MAFA, NKX6-1, GCG, NEUROD1, ISL1, PAX6, HNF1A, SLC30A8), which specific β-cell / islet MSigDB or Reactome pathway does ProKN annotate? I want each pankgraph gene paired with a named ProKN pathway, not a count.

Why the join is required: pankgraph supplies the islet gene catalogue (Ensembl + genomic/cell-type context) but no pathway annotation; ProKN supplies MSigDB/Reactome pathway membership keyed on the Ensembl gene. Pairing each islet gene with its pathway needs the Ensembl join.

---

🧠 **Assistant**

pankgraph islet genes, each paired with a named, islet-relevant ProKN pathway (joined on Ensembl, literal→IRI converted):

| Islet gene (pankgraph) | ProKN pathway (MSigDB/Reactome) |
|---|---|
| INS (insulin) | WP_LEPTIN_INSULIN_OVERLAP |
| GCG (glucagon) | REACTOME_SYNTHESIS_SECRETION_AND_INACTIVATION_OF_GLP_1 |
| PDX1 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| NKX6-1 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| NEUROD1 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| MAFA | ZHOU_PANCREATIC_ENDOCRINE_PROGENITOR |
| HNF1A | ZHOU_PANCREATIC_BETA_CELL |
| ISL1 | ZHOU_PANCREATIC_BETA_CELL |
| PAX6 | REACTOME_INCRETIN_SYNTHESIS_SECRETION_AND_INACTIVATION |
| SLC30A8 (ZnT8) | REACTOME_INSULIN_PROCESSING |

Why this answers the question: every row carries both KGs — a pankgraph islet gene and the named ProKN pathway its protein belongs to. The pairings are biologically coherent islet biology: the β-cell master transcription factors PDX1, NKX6-1 and NEUROD1 sit in the β-cell development pathway, MAFA and HNF1A/ISL1 in pancreatic-endocrine/β-cell programs, GCG (glucagon) and PAX6 in the GLP-1 / incretin synthesis-secretion pathways, SLC30A8 (ZnT8) in insulin processing, and INS in the leptin/insulin overlap. Neither graph alone gives both the islet-gene catalogue and the pathway membership; the Ensembl join does — and only after converting pankgraph's literal Ensembl ids to IRIs.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# pankgraph islet genes -> ONE named islet-relevant ProKN MSigDB/Reactome pathway per gene.
# pankgraph stores Ensembl as a string LITERAL on rdfs:seeAlso -> convert with IRI(STR(?lit)).
SELECT ?sym (SAMPLE(?pathway) AS ?proknPathway) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene rdfs:label ?sym ; rdfs:seeAlso ?ensLit .
    FILTER(?sym IN ("PDX1","NKX6-1","MAFA","NEUROD1","INS","GCG","PAX6","ISL1","SLC30A8","HNF1A"))
    FILTER(STRSTARTS(STR(?ensLit),'https://www.ensembl.org/id/ENSG'))
  }
  BIND(IRI(STR(?ensLit)) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens <http://purl.obolibrary.org/obo/RO_0002431> ?pw . }
  BIND(REPLACE(STR(?pw),'^.*/MSigDB_','') AS ?pathway)
  FILTER(CONTAINS(?pathway,'INSULIN') || CONTAINS(?pathway,'GLUCOSE') || CONTAINS(?pathway,'BETA_CELL')
      || CONTAINS(?pathway,'PANCREAT') || CONTAINS(?pathway,'GLUCAGON') || CONTAINS(?pathway,'ISLET')
      || CONTAINS(?pathway,'SECRETION') || CONTAINS(?pathway,'ZINC') || CONTAINS(?pathway,'DIABET'))
} GROUP BY ?sym
```

_10 row(s)_

| sym | proknPathway |
| --- | --- |
| GCG | REACTOME_SYNTHESIS_SECRETION_AND_INACTIVATION_OF_GLUCAGON_LIKE_PEPTIDE_1_GLP_1 |
| HNF1A | ZHOU_PANCREATIC_BETA_CELL |
| INS | WP_LEPTIN_INSULIN_OVERLAP |
| ISL1 | ZHOU_PANCREATIC_BETA_CELL |
| MAFA | ZHOU_PANCREATIC_ENDOCRINE_PROGENITOR |
| NEUROD1 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| NKX6-1 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| PAX6 | REACTOME_INCRETIN_SYNTHESIS_SECRETION_AND_INACTIVATION |
| PDX1 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| SLC30A8 | REACTOME_INSULIN_PROCESSING |

## Literature validation

Based on articles retrieved from PubMed: Zhang et al., 2026, *Carbohydr Polym* — show that ameliorating β-cell dysfunction in type 2 diabetes upregulates the key β-cell identity/function markers PDX1, NKX6.1, MAFA and NeuroD1 in pancreatic islets, validating these genes as the canonical β-cell-development transcription factors paired here with ProKN's β-cell development pathway. [PMID:42002316](https://pubmed.ncbi.nlm.nih.gov/42002316/) · [DOI](https://doi.org/10.1016/j.carbpol.2026.125227)

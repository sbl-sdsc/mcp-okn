# Fibroblast marker genes (ProKN) with GXA single-cell expression, joined on Cell Ontology CL_0000057

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation
👤 **User**

Drill into the fibroblast (CL_0000057). Crosswalk gene-expression-atlas-okn × prokn on CL: which marker genes does ProKN curate for the fibroblast, and what single-cell differential-expression evidence does GXA hold for each of those same genes in fibroblast assays?

---
🧠 **Assistant**

**Why the join is required.** ProKN curates the fibroblast's marker-gene panel (reified `HAS_MARKER_GENE_IN_{HEART/KIDNEY}` statements on `CL_0000057`, `rdf:object` = Ensembl gene); GXA holds the quantitative single-cell expression (log2FC, adj p) for those genes in assays tagged `has_attribute CL_0000057`. Pairing the curated marker with its measured expression in the same cell type requires the CL + gene-symbol join — neither KG holds both halves.

**Join mechanics.** ProKN marker gene (symbol via `rdfs:label`) on `CL_0000057` ↔ GXA expression gene (`biolink:symbol`) in an assay with `has_attribute CL_0000057`; aggregated over GXA assays per gene.

| Fibroblast marker gene (ProKN, tissue) | GXA assays | GXA log2FC range | GXA min adj. p |
|---|---|---|---|
| DCN / decorin (heart) | 7 | -3.5 … +8.4 | 1.4e-81 |
| KAZN / kazrin (heart) | 7 | -1.6 … +8.0 | 7.4e-46 |
| CDH11 / OB-cadherin (kidney) | 5 | -3.3 … +3.2 | 9.3e-26 |
| FBLN5 / fibulin-5 (kidney) | 13 | -5.1 … +6.5 | 1.9e-22 |
| LAMA2 / laminin α2 (heart) | 5 | -2.4 … +2.4 | 1.9e-16 |
| NID1 / nidogen-1 (kidney) | 6 | -4.1 … +2.9 | 4.4e-10 |
| C7 / complement C7 (kidney) | 3 | -3.1 … +4.2 | 2.7e-8 |

**Why it answers the question:** ProKN's curated fibroblast markers are the textbook extracellular-matrix repertoire of the cell — the proteoglycan decorin (DCN), the basement-membrane laminin/nidogen/fibulin scaffold (LAMA2, NID1, FBLN5) and the mesenchymal adhesion molecule CDH11 — and GXA supplies measured single-cell differential expression for each across multiple assays, confirming these genes are both fibroblast-defining (ProKN) and strongly regulated in fibroblast assays (GXA).

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
SELECT ?sym ?tissue (COUNT(DISTINCT ?assay) AS ?nAssays)
       (MIN(?log2fc) AS ?minLog2fc) (MAX(?log2fc) AS ?maxLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?stmt rdf:subject <http://purl.obolibrary.org/obo/CL_0000057> ;
          rdf:predicate ?mp ; rdf:object ?gene .
    FILTER(STRSTARTS(STR(?mp),'https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN'))
    ?gene rdfs:label ?sym .
    BIND(REPLACE(STR(?mp),'^.*HAS_MARKER_GENE_IN_','') AS ?tissue)
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?assay biolink:has_attribute <http://purl.obolibrary.org/obo/CL_0000057> .
    ?assoc biolink:subject ?assay ; biolink:object ?gxaGene ;
           wobd:log2fc ?log2fc ; wobd:adj_p_value ?adjp .
    ?gxaGene biolink:symbol ?sym .
  }
} GROUP BY ?sym ?tissue ORDER BY ?minAdjP LIMIT 15
```

## Literature validation

The adult-human-heart single-cell atlas resolves a distinct cardiac fibroblast population whose canonical markers include decorin (DCN), matching the ProKN-curated fibroblast marker panel paired here with GXA expression. Litviňuková M et al., "Cells of the adult human heart," *Nature* 588, 466–472 (2020). [PMID:32971526](https://pubmed.ncbi.nlm.nih.gov/32971526/) · [DOI](https://doi.org/10.1038/s41586-020-2797-4)

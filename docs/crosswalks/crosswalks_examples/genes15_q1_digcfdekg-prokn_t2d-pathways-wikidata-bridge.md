# CFDE REVEAL type-2-diabetes genes named with their ProKN diabetes pathway, via the Wikidata Entrez→HGNC bridge

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × prokn (Protein Knowledge Network / ProteinKG), bridged on the shared gene. digcfdekg keys genes on Entrez (`http://www.ncbi.nlm.nih.gov/gene/{entrez}`); ProKN keys its gene node on HGNC (reached by `skos:exactMatch` → `http://identifiers.org/hgnc/{n}`). The two identifier schemes are joined through Wikidata: `?item wdt:P351 {entrez} ; wdt:P354 {hgnc}`. Both digcfdekg and prokn are CFDE projects.

Research question: For the genes CFDE REVEAL infers (PIGEAN) as most relevant to **type 2 diabetes**, which specific diabetes-relevant biological pathway (MSigDB / Reactome) does ProKN annotate the gene's protein with? I want each CFDE gene paired with a named ProKN pathway, not a count.

Why the join is required: digcfdekg supplies the PIGEAN type-2-diabetes gene-relevance weight but no pathway annotation; ProKN supplies MSigDB/Reactome pathway membership keyed on HGNC but no CFDE trait inference. Pairing a CFDE diabetes gene with its ProKN pathway is only possible by bridging Entrez→HGNC through Wikidata.

---

🧠 **Assistant**

CFDE REVEAL's top type-2-diabetes (MONDO_0005148) genes, each paired with a named, diabetes-relevant ProKN pathway reached through the Wikidata Entrez→HGNC bridge:

| Gene (digcfdekg) | PIGEAN weight | ProKN pathway (MSigDB/Reactome) |
|---|---|---|
| INS | 10.30 | REACTOME_REGULATION_OF_INSULIN_SECRETION |
| LEP | 9.77 | WP_DIFFERENTIATION_OF_WHITE_AND_BROWN_ADIPOCYTE |
| GCK | 9.73 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| GCKR | 8.97 | REACTOME_GLUCOSE_METABOLISM |
| WFS1 | 8.62 | REACTOME_..._IGF_TRANSPORT_AND_UPTAKE_BY_IGFBPS |
| HNF1A | 8.60 | REACTOME_REGULATION_OF_GENE_EXPRESSION_IN_BETA_CELLS |
| GIPR | 8.34 | REACTOME_GLUCAGON_TYPE_LIGAND_RECEPTORS |
| SLC2A2 (GLUT2) | 8.18 | REACTOME_REGULATION_OF_INSULIN_SECRETION |
| KCNJ11 | 8.13 | REACTOME_REGULATION_OF_INSULIN_SECRETION |
| PPARG | 8.06 | REACTOME_TRANSCRIPTIONAL_REGULATION_OF_WHITE_ADIPOCYTE_DIFFERENTIATION |
| SLC30A8 (ZnT8) | 7.67 | REACTOME_ZINC_TRANSPORTERS |
| HNF4A | 7.54 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |

Why this answers the question: every row carries data from **both** KGs in the same line — a CFDE-inferred diabetes gene with its PIGEAN weight (digcfdekg) and the specific ProKN pathway its protein belongs to (prokn) — and the pathways are exactly the diabetes biology: INS, SLC2A2 (GLUT2) and KCNJ11 in insulin secretion; GCK, HNF1A and HNF4A in pancreatic-β-cell development/gene-expression programs; SLC30A8 (ZnT8) in the zinc-transporter pathway (β-cell zinc handling); PPARG/LEP in adipocyte differentiation; GIPR in the glucagon/incretin receptor family. Neither graph yields this alone — digcfdekg has no pathways, ProKN has no CFDE trait inference — and the Entrez→HGNC Wikidata bridge is the only path between them.

## SPARQL query executed

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
# digcfdekg x prokn via Wikidata Entrez->HGNC bridge.
# CFDE type-2-diabetes genes (PIGEAN >= 7.0) each paired with ONE named diabetes-relevant
# ProKN MSigDB/Reactome pathway (RO_0002431) the gene's protein belongs to.
SELECT ?sym ?pigeanScore (SAMPLE(?pwName) AS ?proknPathway) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/MONDO_0005148> ;
        rdf:subject ?gene ;
        dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 7.0)
  }
  BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item wdt:P351 ?entrez ; wdt:P354 ?hgnc . }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?pg skos:exactMatch ?h ; <http://purl.obolibrary.org/obo/RO_0002431> ?pathway .
  }
  BIND(REPLACE(STR(?pathway),'^.*/rdf/MSigDB_','') AS ?pwName)
  FILTER(CONTAINS(?pwName,'INSULIN') || CONTAINS(?pwName,'GLUCOSE') || CONTAINS(?pwName,'DIABET')
      || CONTAINS(?pwName,'BETA_CELL') || CONTAINS(?pwName,'PANCREAT') || CONTAINS(?pwName,'LEPTIN')
      || CONTAINS(?pwName,'ZINC') || CONTAINS(?pwName,'METAL_ION') || CONTAINS(?pwName,'HNF')
      || CONTAINS(?pwName,'GLUCAGON') || CONTAINS(?pwName,'ADIPO'))
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 15
```

_15 row(s) — showing 12 named gene→pathway pairs_

| sym | pigeanScore | proknPathway |
| --- | --- | --- |
| INS | 10.3 | REACTOME_REGULATION_OF_INSULIN_SECRETION |
| LEP | 9.77 | WP_DIFFERENTIATION_OF_WHITE_AND_BROWN_ADIPOCYTE |
| GCK | 9.73 | REACTOME_REGULATION_OF_BETA_CELL_DEVELOPMENT |
| GCKR | 8.97 | REACTOME_GLUCOSE_METABOLISM |
| HNF1A | 8.6 | REACTOME_REGULATION_OF_GENE_EXPRESSION_IN_BETA_CELLS |
| SLC30A8 | 7.67 | REACTOME_ZINC_TRANSPORTERS |

## Literature validation

Based on articles retrieved from PubMed: Ghafouri-Taleghani & Bahadoran, 2026, *Curr Nutr Rep* — review of zinc homeostasis and T2D risk shows the ZnT8 transporter (SLC30A8) controls zinc accumulation in β-cell insulin secretory granules and that SLC30A8 risk and loss-of-function alleles alter insulin secretion and clearance, validating the SLC30A8 → REACTOME_ZINC_TRANSPORTERS row and the broader insulin-secretion biology of this gene set. [PMID:42033606](https://pubmed.ncbi.nlm.nih.gov/42033606/) · [DOI](https://doi.org/10.1007/s13668-026-00762-4)

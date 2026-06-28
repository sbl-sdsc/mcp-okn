# Blood-lymphocyte ProKN markers that are themselves spaceflight-responsive

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation
👤 **User**

Microgravity dysregulates circulating lymphocytes. Which ProKN canonical **lymphocyte-subtype marker genes** (NK, B, CD8/CD4 T) are *themselves* differentially expressed in a clean Space-Flight-vs-Ground-Control GeneLab assay in an immune organ — i.e. which of the genes that define each lymphocyte population are also directly spaceflight-responsive?

---
🧠 **Assistant**

ProKN supplies the cell-type→marker-gene assignment (which gene defines which lymphocyte subtype) but holds no spaceflight data; GeneLab supplies the confounder-free spaceflight immune-tissue log2fc but no marker-gene/cell-type annotation. Each row therefore needs ProKN (cell type + marker gene) AND GeneLab (the same gene's clean spaceflight log2fc + tissue).

**Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression in an immune tissue (thymus `UBERON_0002370` / spleen `UBERON_0002106`).

**Sample result** (8 of 12) — each row shows prokn + GeneLab data (GeneLab tissue: thymus `UBERON_0002370` unless noted):

| Lymphocyte subtype (ProKN, CL) | ProKN marker gene | GeneLab gene | GeneLab log2FC (SF vs GC, immune tissue) | GeneLab adj. p |
|---|---|---|---|---|
| CD4-positive, alpha-beta T cell | IL7R | Il7r | +1.16 (up) | 7.2e-7 |
| natural killer cell | KLRD1 | Klrd1 | +1.53 (up) | 3.6e-4 |
| natural killer cell | GZMB | Gzmb | -1.11 (down) | 2.2e-3 |
| CD4-positive, alpha-beta T cell | CD69 | Cd69 | +0.46 (up) | 4.6e-3 |
| natural killer cell | CMC1 | Cmc1 | +0.84 (up) | 4.9e-3 |
| natural killer cell | AOAH | Aoah | +0.89 (up, spleen) | 8.5e-3 |
| B cell | FCRL1 | Fcrl1 | -2.86 (down) | 2.6e-2 |
| CD8-positive, alpha-beta T cell | CD8A | Cd8a | -0.38 (down) | 4.4e-2 |

**Why it answers the question:** every row pairs a ProKN cell-type→marker-gene assignment with that exact gene's clean GeneLab spaceflight log2fc in an immune organ — surfacing lymphocyte-defining genes that are themselves microgravity-responsive (NK markers **KLRD1**/**GZMB**, CD4-T markers **IL7R**/**CD69**, B-cell marker **FCRL1**, CD8 marker **CD8A**), a both-KG result neither graph yields alone.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# Each VALUES row = (lymphocyte CL IRI, ProKN marker symbol [human], GeneLab gene symbol [mouse], cell-type label).
# ProKN must record the gene as a marker of that cell type AND GeneLab must hold a clean SF-vs-GC immune-tissue DE value.
SELECT ?cellType ?markerSym ?genelabSymbol (SAMPLE(?lfc) AS ?glLog2fc) (MIN(?adjp) AS ?glAdjp) (SAMPLE(?tissue) AS ?glTissue) WHERE {
  VALUES (?ct ?markerSym ?genelabSymbol ?cellType) {
    (<http://purl.obolibrary.org/obo/CL_0000624> "IL7R"  "Il7r"  "CD4-positive, alpha-beta T cell")
    (<http://purl.obolibrary.org/obo/CL_0000623> "KLRD1" "Klrd1" "natural killer cell")
    (<http://purl.obolibrary.org/obo/CL_0000623> "GZMB"  "Gzmb"  "natural killer cell")
    (<http://purl.obolibrary.org/obo/CL_0000624> "CD69"  "Cd69"  "CD4-positive, alpha-beta T cell")
    (<http://purl.obolibrary.org/obo/CL_0000623> "CMC1"  "Cmc1"  "natural killer cell")
    (<http://purl.obolibrary.org/obo/CL_0000623> "AOAH"  "Aoah"  "natural killer cell")
    (<http://purl.obolibrary.org/obo/CL_0000236> "FCRL1" "Fcrl1" "B cell")
    (<http://purl.obolibrary.org/obo/CL_0000236> "GNG7"  "Gng7"  "B cell")
    (<http://purl.obolibrary.org/obo/CL_0000236> "ARHGAP24" "Arhgap24" "B cell")
    (<http://purl.obolibrary.org/obo/CL_0000625> "CD8A"  "Cd8a"  "CD8-positive, alpha-beta T cell")
    (<http://purl.obolibrary.org/obo/CL_0000624> "LTB"   "Ltb"   "CD4-positive, alpha-beta T cell")
    (<http://purl.obolibrary.org/obo/CL_0000236> "INPP5D" "Inpp5d" "B cell")
  }
  # ProKN: confirm this gene is a recorded marker of that lymphocyte cell type
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?stmt rdf:subject ?ct ; rdf:object ?marker .
    ?marker rdfs:label ?markerSym .
    FILTER(STRSTARTS(STR(?marker),'https://www.ensembl.org/id/'))
  }
  # GeneLab: clean SF-vs-GC immune-tissue DE of that same gene
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene schema:symbol ?genelabSymbol .
    ?stmt2 rdf:subject ?assay ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
           rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?adjp .
    ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
           schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
           schema:INVESTIGATED_ASiA ?tissue .
    VALUES ?tissue {
      <http://purl.obolibrary.org/obo/UBERON_0002370>
      <http://purl.obolibrary.org/obo/UBERON_0002106>
      <http://purl.obolibrary.org/obo/UBERON_0000029>
      <http://purl.obolibrary.org/obo/UBERON_0002371>
    }
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
    FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
    FILTER(?adjp < 0.05)
  }
} GROUP BY ?cellType ?markerSym ?genelabSymbol ORDER BY ?glAdjp LIMIT 15
```

## Literature validation

Stratis et al., 2023, *Front Immunol* — RNA-seq of astronaut leukocytes across ~6-month ISS missions shows spaceflight immune modulation with 276 differentially expressed transcripts (immune suppression entering space, reactivation on return). [PMID:37426644](https://pubmed.ncbi.nlm.nih.gov/37426644/) · [DOI](https://doi.org/10.3389/fimmu.2023.1171103)

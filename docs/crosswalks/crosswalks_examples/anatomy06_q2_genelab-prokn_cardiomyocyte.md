# Cardiomyocyte ProKN markers that are themselves spaceflight-responsive

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation
👤 **User**

Cardiovascular deconditioning is a core microgravity risk. Which ProKN canonical **cardiomyocyte marker genes** are *themselves* differentially expressed in a clean Space-Flight-vs-Ground-Control GeneLab assay in heart or muscle — i.e. which of the genes that define the cardiac-muscle cell are also directly spaceflight-responsive?

---
🧠 **Assistant**

ProKN supplies the cardiomyocyte→marker-gene assignment but no spaceflight data; GeneLab supplies the confounder-free spaceflight heart/muscle log2fc but no marker-gene/cell-type annotation. Each row needs ProKN (cardiomyocyte + marker gene) AND GeneLab (the same gene's clean spaceflight log2fc + tissue).

**Spaceflight contrast:** Space Flight vs Ground Control on the same material, with all other factors *balanced* across the two arms — the `mcp-okn` server's `spoke-genelab` Rule 1 (direction via `factor_space_1/2`) + Rule 2 (comparability — arms differ only in the condition after stripping balanced shared factors/group codes), replacing the earlier strict "factor arrays contain only the condition label" filter; gene expression in heart `UBERON_0000948` / skeletal-muscle tissues. (Rule 2 also admits the genotype-matched OSD-347 *Drosophila* contrasts, but those carry no mouse cardiomyocyte-marker genes, so the eight markers below are unchanged.)

**Sample result** (all 8) — each row shows prokn + GeneLab data (GeneLab tissue: heart `UBERON_0000948`, soleus `UBERON_0001389`, or quadriceps `UBERON_0001377`):

| Cardiomyocyte subtype (ProKN, CL) | ProKN marker gene | GeneLab gene | GeneLab log2FC (SF vs GC) | GeneLab tissue | GeneLab adj. p |
|---|---|---|---|---|---|
| regular atrial cardiac myocyte | CMYA5 | Cmya5 | +0.34 (up) | soleus | 2.0e-17 |
| regular atrial cardiac myocyte | MYL7 | Myl7 | -11.99 (down) | heart | 1.6e-12 |
| regular atrial cardiac myocyte | ANKRD1 | Ankrd1 | -1.37 (down) | quadriceps | 4.1e-8 |
| regular atrial cardiac myocyte | FGF12 | Fgf12 | -7.64 (down) | heart | 8.4e-5 |
| regular atrial cardiac myocyte | NPPA | Nppa | -6.67 (down) | heart | 8.7e-5 |
| regular atrial cardiac myocyte | TTN | Ttn | +0.42 (up) | soleus | 1.3e-4 |
| regular atrial cardiac myocyte | MYH6 | Myh6 | -1.51 (down) | quadriceps | 1.1e-3 |
| regular atrial cardiac myocyte | ERBB4 | Erbb4 | +0.75 (up) | quadriceps | 1.4e-2 |

**Why it answers the question:** every row pairs a ProKN cardiomyocyte→marker-gene assignment with that exact gene's clean GeneLab spaceflight log2fc in heart or muscle — the sarcomere/contractility marker set (**MYL7**, **MYH6**, **TTN**, **NPPA**, **ANKRD1**, **CMYA5**) that *defines* the cardiac muscle cell is shown to be directly microgravity-responsive (notably MYL7, NPPA and FGF12 strongly down in heart), a both-KG result neither graph yields alone.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# Each VALUES row = (cardiomyocyte CL IRI, ProKN marker symbol [human], GeneLab gene symbol [mouse], cell-type label).
# ProKN must record the gene as a cardiomyocyte marker AND GeneLab must hold a clean SF-vs-GC heart/muscle DE value.
SELECT ?cellType ?markerSym ?genelabSymbol (SAMPLE(?lfc) AS ?glLog2fc) (MIN(?adjp) AS ?glAdjp) (SAMPLE(?tissue) AS ?glTissue) WHERE {
  VALUES (?ct ?markerSym ?genelabSymbol ?cellType) {
    (<http://purl.obolibrary.org/obo/CL_0002129> "MYL7"   "Myl7"   "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "NPPA"   "Nppa"   "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "FGF12"  "Fgf12"  "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "MYH6"   "Myh6"   "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "TTN"    "Ttn"    "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "ANKRD1" "Ankrd1" "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "CMYA5"  "Cmya5"  "regular atrial cardiac myocyte")
    (<http://purl.obolibrary.org/obo/CL_0002129> "ERBB4"  "Erbb4"  "regular atrial cardiac myocyte")
  }
  # ProKN: confirm this gene is a recorded cardiomyocyte marker
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?stmt rdf:subject ?ct ; rdf:object ?marker .
    ?marker rdfs:label ?markerSym .
    FILTER(STRSTARTS(STR(?marker),'https://www.ensembl.org/id/'))
  }
  # GeneLab: clean SF-vs-GC heart/muscle DE of that same gene
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene schema:symbol ?genelabSymbol .
    ?stmt2 rdf:subject ?assay ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
           rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?adjp .
    ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
           schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
           schema:INVESTIGATED_ASiA ?tissue .
    VALUES ?tissue {
      <http://purl.obolibrary.org/obo/UBERON_0000948>
      <http://purl.obolibrary.org/obo/UBERON_0001389>
      <http://purl.obolibrary.org/obo/UBERON_0001134>
      <http://purl.obolibrary.org/obo/UBERON_0001385>
      <http://purl.obolibrary.org/obo/UBERON_0001386>
      <http://purl.obolibrary.org/obo/UBERON_0001377>
    }
    FILTER(?m1 = ?m2)
    # Rule 2 comparability: arms differ ONLY in the condition (any extra factor must be balanced, i.e. present on BOTH arms)
    FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 .
      FILTER(LCASE(STR(?f1)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f1), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay schema:factors_2 ?f1 } }
    FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 .
      FILTER(LCASE(STR(?f2)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f2), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay schema:factors_1 ?f2 } }
    FILTER(?adjp < 0.05)
  }
} GROUP BY ?cellType ?markerSym ?genelabSymbol ORDER BY ?glAdjp LIMIT 15
```

## Literature validation

Wnorowski et al., 2019, *Stem Cell Reports* — human iPSC-derived cardiomyocytes cultured 5.5 weeks aboard the ISS showed altered calcium handling and 2,635 differentially expressed genes versus ground controls. [PMID:31708475](https://pubmed.ncbi.nlm.nih.gov/31708475/) · [DOI](https://doi.org/10.1016/j.stemcr.2019.10.006)

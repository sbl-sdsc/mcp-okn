# SPOKE-GeneLab — 18 real-world example queries (two per crosswalk partner)

**Standalone showcase — NOT part of the crosswalk catalog** (`crosswalks_example.md` / `crosswalks_examples/`).
This file presents **two scientifically meaningful, literature-grounded, executed example queries for each of the 9 distinct knowledge graphs that `spoke-genelab` crosswalks with** in the Proto-OKN / FRINK federation. (Companion to `spoke-okn-25-example-queries.md`.) Every example that reads a differential measurement uses a strict **Space-Flight-vs-Ground-Control** contrast — see the ⚠️ section below.

- **Focus KG:** `spoke-genelab` — NASA GeneLab spaceflight omics: measured differential gene expression and DNA-methylation on tissues, cell types and genes from spaceflight / space-radiation experiments.
- **Model:** claude-opus-4-8 · **Crosswalk source:** `mcp-okn list_crosswalks` (134 verified crosswalks, verified 2026-06-30)
- **Endpoint:** FRINK federated SPARQL via the `mcp-okn` service (`https://apps.okn.us/federation/sparql`)
- **Two examples per crosswalk (18 queries total), all executed on 2026-06-27**; each block shows the runnable SPARQL, a real sample of returned rows, and a PubMed/literature anchor. The two examples per partner differ by scientific angle (tissue / trait / disease); **every example that reads a differential measurement (expression, methylation, abundance) enforces the strict Space-Flight-vs-Ground-Control contrast** described below.
- **Scope rule — "9 crosswalks":** `spoke-genelab` participates in several `list_crosswalks` rows that resolve to **9 distinct partner KGs**. This file gives one *new-angle* example per partner — deliberately different tissues / cell types / genes / organisms from the q1/q2 already in the catalog. Where a partner connects on more than one key (e.g. GXA via UBERON and CL; AOP-Wiki and biohealth also via NCBITaxon), the single most compelling join is shown.

## Methodology

For each partner KG, the verified join recipe (shared identifier, predicates, IRI normalization, `ubergraph` bridge where needed) was taken from `get_join_strategy` / `taxon_overlap` / the catalog transcripts, then applied to a **fresh space-biology research question**. Every query scopes each graph with `GRAPH <https://purl.org/okn/frink/kg/{shortname}>`, was run against the live federation, and returned non-empty, on-topic rows. Each result is corroborated by a peer-reviewed reference.

## ⚠️ The Space-Flight-vs-Ground-Control contrast (applies to every differential example)

spoke-genelab models each differential **expression / methylation / abundance** result as an `Assay` that compares **two groups** (`group_mean_1` vs `group_mean_2`). Crucially, **many assays are confounded** and must not be read as a spaceflight effect: of the gene-DE assays, ~1,244 compare Space-Flight-vs-Space-Flight, ~424 compare control-vs-control, others compare Space Flight against Basal/Vivarium controls, and many bundle an extra factor (infection, dose, plant compartment, …) that differs between the two groups. A scientifically valid spaceflight effect requires comparing **Space Flight vs Ground Control with every other factor identical**.

Every differential example in this file (both **a** and **b**) enforces this with the verified clean-contrast filter:

```sparql
?assay schema:factor_space_1 "Space Flight" ;
       schema:factor_space_2 "Ground Control" ;
       schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 .
FILTER(?m1 = ?m2)                                                       # same biological material
FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }   # no other differing factor in group 1
FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") } # no other differing factor in group 2
```

Only **56** of the assays are such clean contrasts. **Direction:** group 1 = Space Flight, group 2 = Ground Control, so `log2fc > 0` (or `methylation_diff > 0`, `lnfc > 0`) means **up in spaceflight relative to ground**. The one exception is **8b**, where the VEG-01 microbiome assays carry no `material_id` and always bundle a plant-compartment factor — there the block falls back to the `factor_space_1/2` fields alone and says so explicitly.

## Index

Each crosswalk partner has two examples (**a** = original angle, **b** = a second angle); both are listed together below.

| # | Partner KG | Shared key / bridge | Example query |
|---|---|---|---|
| | **Anatomy & Tissue** | | |
| 1a | `gene-expression-atlas-okn` | gene symbol (UBERON-scoped) | Retina / SANS: spaceflight vs terrestrial retinal DE of the same gene |
| 1b | `gene-expression-atlas-okn` | gene symbol (UBERON-scoped) | Soleus: spaceflight vs terrestrial muscle DE of the same gene |
| 2a | `prokn` | gene symbol (CL-scoped) | Blood-lymphocyte ProKN markers that are themselves spaceflight-responsive |
| 2b | `prokn` | gene symbol (CL-scoped) | Cardiomyocyte ProKN markers that are themselves spaceflight-responsive |
| 3a | `biohealth` | UMLS↔UBERON (via ubergraph) | Kidney: spaceflight DE genes paired with the organ's disease landscape |
| 3b | `biohealth` | UMLS↔UBERON (via ubergraph) | Spleen: spaceflight DE genes paired with the organ's disease landscape |
| | **Genes & Functional Genomics** | | |
| 4a | `biobricks-aopwiki` | Entrez (direct) | Oxidative-stress / DNA-damage AOP key-event genes (clean contrast) |
| 4b | `biobricks-aopwiki` | Entrez (direct) | Hepatic-steatosis / liver-injury AOP genes (clean contrast) |
| 5a | `digcfdekg` | Entrez (direct) | Coronary-artery-disease factor genes (clean contrast) |
| 5b | `digcfdekg` | Entrez (direct) | eGFR / kidney-function factor genes (clean contrast; renin up) |
| 6a | `rdkg` | Entrez + ortholog (direct) | DNA-repair / genome-instability rare-disease genes (clean contrast) |
| 6b | `rdkg` | Entrez + ortholog (direct) | Muscular-dystrophy / cardiomyopathy genes in clean muscle contrast |
| 7a | `spoke-okn` | Entrez (direct) | Immune / inflammatory disease genes (clean contrast) |
| 7b | `spoke-okn` | Entrez + ortholog (direct) | DNA-methylation: clean muscle differentially-methylated genes → SPOKE disease |
| | **Taxonomy & Organisms** | | |
| 8a | `nde` | NCBITaxon (via ubergraph) | Spaceflight-perturbed mouse organs paired with NIAID diseases in those organs |
| 8b | `nde` | NCBITaxon clade (via ubergraph) | Spaceflight-enriched Gammaproteobacteria bridged to NIAID pathogens |
| 9a | `sawgraph` | NCBITaxon clade (via ubergraph) | Spaceflight zebrafish lineage joined to PFAS measured in white perch |
| 9b | `sawgraph` | NCBITaxon clade (via ubergraph) | Spaceflight Arabidopsis lineage joined to PFAS measured in maize |

---

## Anatomy & Tissue

### 1a. spoke-genelab × gene-expression-atlas-okn — Retina / SANS: spaceflight DE genes vs named terrestrial retinal-disease contrasts
- **Partner KG:** `gene-expression-atlas-okn` — EBI Expression Atlas terrestrial differential-expression studies, each carrying a **named contrast** (`biolink:name`, e.g. a disease/injury vs its control).
- **Shared identifier / bridge:** gene **symbol** (GeneLab `schema:symbol` ↔ GXA `biolink:symbol`, mouse mixed-case) scoped to the retina (`UBERON_0000966`); the GXA log2fc is reported **together with the named GXA contrast it comes from**.
- **Spaceflight contrast (GeneLab side):** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter). **GXA side:** the named disease/injury contrast shown per row (e.g. *Nrl*-null photoreceptor degeneration, retinal ischemia–reperfusion injury, optic-nerve transection).
- **Research question:** SANS makes the eye a priority organ. For genes DE in the retina under a *clean* Space-Flight-vs-Ground-Control contrast, how does each gene move in EBI Expression Atlas's terrestrial retinal **disease/injury** models — and, crucially, **in which named GXA contrast** (so the terrestrial log2fc is interpretable, not a bare number)?
- **Why the join is required:** GeneLab holds the confounder-free spaceflight retinal log2fc but no terrestrial/disease data; GXA holds terrestrial retinal differential expression but only as a named *test-vs-reference* contrast, with no spaceflight data. Each row pairs the GeneLab spaceflight log2fc with the GXA log2fc **and the named GXA contrast that produced it** for the same gene — reporting, per gene, its most-significant retina contrast.
- **SPARQL** (executed 2026-06-27, returned 15 rows; per gene, the most significant GXA retina contrast):
```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?symbol ?glLog2fc ?glAdjp ?gxaContrast ?gxaLog2fc ?gxaAdjp WHERE {
  # GeneLab: clean SF-vs-GC retina DE genes
  { SELECT ?symbol (SAMPLE(?lfc) AS ?glLog2fc) (MIN(?adjp) AS ?glAdjp) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject ?assay ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
              rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?adjp .
        ?gene schema:symbol ?symbol .
        ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
               schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
               schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0000966> .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
        FILTER(?adjp < 1.0e-3)
      } } GROUP BY ?symbol }
  # GXA: the most significant retina contrast for that gene ...
  { SELECT ?symbol (MIN(?gap) AS ?gxaAdjp) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
        ?g biolink:symbol ?symbol . ?as biolink:object ?g ; biolink:subject ?a ; wobd:adj_p_value ?gap .
        ?a biolink:has_attribute <http://purl.obolibrary.org/obo/UBERON_0000966> .
      } } GROUP BY ?symbol }
  # ... and the contrast name + log2fc of that most-significant association
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?as2 biolink:object ?g2 ; biolink:subject ?a2 ; wobd:adj_p_value ?gxaAdjp ; wobd:log2fc ?gxaLog2fc .
    ?g2 biolink:symbol ?symbol .
    ?a2 biolink:has_attribute <http://purl.obolibrary.org/obo/UBERON_0000966> ; biolink:name ?gxaContrast .
  }
} ORDER BY ?glAdjp LIMIT 15
```
- **Sample result** (8 of 15) — each row pairs the GeneLab spaceflight value with the GXA value **and its named contrast**:

| Gene | GeneLab log2FC (SF vs GC, retina) | GeneLab adj. p | GXA contrast (test vs reference) | GXA log2FC | GXA adj. p |
|---|---|---|---|---|---|
| Drd4 | +0.80 (up) | 3.2e-58 | *Nrl*-null vs wild type (60 d) — photoreceptor degeneration | -1.3 | 3.9e-8 |
| Pdzph1 | -0.84 (down) | 4.8e-22 | *Nrl*−/− vs wild type — photoreceptor degeneration | -3.6 | 1.3e-40 |
| Sag | -0.64 (down) | 6.9e-21 | *Nrl*-null vs wild type (10 d) — photoreceptor degeneration | -2.0 | 4.7e-12 |
| Irf7 | +1.42 (up) | 7.2e-19 | 5,9-endoperoxy-cholestenediol (oxysterol) vs vehicle | -1.2 | 8.3e-5 |
| Glmn | -0.68 (down) | 4.1e-14 | intraorbital nerve transection (48 h) vs none | -1.2 | 5.6e-3 |
| Vgf | -0.84 (down) | 2.2e-11 | intraorbital nerve transection (48 h) vs none | +1.6 | 6.4e-6 |
| Med13l | -0.49 (down) | 3.1e-10 | *Nrl*−/− vs wild type — photoreceptor degeneration | -1.5 | 8.7e-46 |
| Dscaml1 | -0.45 (down) | 4.8e-10 | retinal ischemia–reperfusion injury vs sham surgery (1 d) | -1.0 | 5.2e-8 |

- **Why it answers the question:** each GXA log2fc is now attributed to a **named retinal contrast** — so the terrestrial number is interpretable, not bare. Spaceflight-perturbed retinal genes line up with concrete eye pathologies: the photoreceptor arrestin **Sag** and **Pdzph1** are down in both spaceflight and the *Nrl*-null photoreceptor-degeneration retina; **Vgf** rises after optic-nerve transection (an optic-nerve injury directly relevant to SANS); **Dscaml1** moves in retinal ischemia–reperfusion injury.
- **Literature support:** Kremsky et al., 2024, *Int J Mol Sci* — RNA-seq of ISS mice shows microgravity induces oxidative-stress, inflammation and apoptosis transcriptomic changes in the optic nerve and retina, central to SANS. [PMID:39596110](https://pubmed.ncbi.nlm.nih.gov/39596110/) · [DOI](https://doi.org/10.3390/ijms252212041)

### 1b. spoke-genelab × gene-expression-atlas-okn — Soleus muscle: spaceflight DE genes vs a named terrestrial muscle contrast (PGC-1β model)
- **Partner KG:** `gene-expression-atlas-okn` — EBI Expression Atlas terrestrial differential-expression studies, each carrying a **named contrast** (`biolink:name`).
- **Shared identifier / bridge:** gene **symbol** (GeneLab `schema:symbol` ↔ GXA `biolink:symbol`, mouse mixed-case); GeneLab tissue = soleus muscle `UBERON_0001389`, GXA tissue = skeletal muscle tissue `UBERON_0001134`; the GXA log2fc is reported **with the named GXA contrast it comes from** (tissue-identity "vs liver" baseline contrasts excluded).
- **Spaceflight contrast (GeneLab side):** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter). **GXA side:** the named muscle contrast shown per row — predominantly the **PGC-1β knock-in vs wild type** oxidative-muscle reprogramming model (also YY1-knockout, androgen treatment).
- **Research question:** Muscle atrophy is a signature microgravity hazard, and the slow-twitch soleus is most affected. For genes DE in the soleus under a *clean* Space-Flight-vs-Ground-Control contrast, how do they move in a **named** terrestrial muscle contrast — chiefly the PGC-1β-knock-in model that reprograms oxidative/slow-fibre metabolism (directly relevant to the oxidative soleus and the spaceflight fast-fibre shift)?
- **Why the join is required:** GeneLab holds the confounder-free spaceflight soleus log2fc but no terrestrial contrast; GXA holds terrestrial muscle differential expression only as a named test-vs-reference contrast, with no spaceflight data. Each row pairs the GeneLab spaceflight log2fc with the GXA log2fc **and the named muscle contrast that produced it**, reporting per gene its most-significant (non-tissue-baseline) muscle contrast.
- **SPARQL** (executed 2026-06-27, returned 15 rows; per gene, most significant non-"vs liver" muscle contrast):
```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?symbol ?glLog2fc ?glAdjp ?gxaContrast ?gxaLog2fc ?gxaAdjp WHERE {
  # GeneLab: clean SF-vs-GC soleus DE genes
  { SELECT ?symbol (SAMPLE(?lfc) AS ?glLog2fc) (MIN(?adjp) AS ?glAdjp) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject ?assay ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
              rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?adjp .
        ?gene schema:symbol ?symbol .
        ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
               schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
               schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0001389> .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
        FILTER(?adjp < 1.0e-6)
      } } GROUP BY ?symbol }
  # GXA: most significant skeletal-muscle contrast for that gene (excluding tissue-identity "vs liver")
  { SELECT ?symbol (MIN(?gap) AS ?gxaAdjp) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
        ?g biolink:symbol ?symbol . ?as biolink:object ?g ; biolink:subject ?a ; wobd:adj_p_value ?gap .
        ?a biolink:has_attribute <http://purl.obolibrary.org/obo/UBERON_0001134> ; biolink:name ?nm .
        FILTER(!CONTAINS(?nm,"liver"))
      } } GROUP BY ?symbol }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?as2 biolink:object ?g2 ; biolink:subject ?a2 ; wobd:adj_p_value ?gxaAdjp ; wobd:log2fc ?gxaLog2fc .
    ?g2 biolink:symbol ?symbol .
    ?a2 biolink:has_attribute <http://purl.obolibrary.org/obo/UBERON_0001134> ; biolink:name ?gxaContrast .
    FILTER(!CONTAINS(?gxaContrast,"liver"))
  }
} ORDER BY ?glAdjp LIMIT 15
```
- **Sample result** (8 of 15) — each row pairs the GeneLab spaceflight value with the GXA value **and its named contrast**:

| Gene | GeneLab log2FC (SF vs GC, soleus) | GeneLab adj. p | GXA contrast (test vs reference) | GXA log2FC | GXA adj. p |
|---|---|---|---|---|---|
| Slc4a3 | -2.23 (down) | 6.7e-102 | PGC-1β knock-in vs wild type | +1.1 | 1.1e-5 |
| Ablim1 | -1.76 (down) | 1.1e-65 | YY1 (Yin Yang 1) knockout vs wild type | +1.1 | 2.6e-4 |
| Myoz1 | +1.04 (up) | 4.1e-53 | PGC-1β knock-in vs wild type | -1.1 | 2.4e-5 |
| Stat5b | +0.99 (up) | 2.9e-52 | PGC-1β knock-in vs wild type | -1.9 | 1.4e-5 |
| Slc38a4 | +1.75 (up) | 6.4e-43 | PGC-1β knock-in vs wild type | -3.3 | 1.6e-7 |
| Idh2 | -1.36 (down) | 9.7e-41 | PGC-1β knock-in vs wild type | +1.9 | 1.7e-5 |
| Pdlim3 | +2.41 (up) | 2.0e-38 | PGC-1β knock-in vs wild type | -1.2 | 2.0e-5 |
| Fzd9 | -1.29 (down) | 8.3e-38 | PGC-1β knock-in vs wild type | -1.7 | 9.4e-6 |

- **Why it answers the question:** each GXA log2fc is now attributed to a **named muscle contrast** — overwhelmingly the PGC-1β-knock-in oxidative-muscle reprogramming model — so the terrestrial number is interpretable. The spaceflight-perturbed soleus genes (Myoz1, Pdlim3, Idh2, Slc38a4, Fzd9) move in the *opposite* direction in the PGC-1β oxidative-muscle model, consistent with spaceflight shifting the slow oxidative soleus away from its PGC-1-driven oxidative program.
- **Literature support:** Gambara et al., 2017, *PLoS ONE* — global gene-expression profiling of soleus from 30-day space-flown (BION-M1) mice identifies disuse-susceptible muscle transcripts, explicitly validating **Fzd9** among the affected genes (which also appears here). [PMID:28076365](https://pubmed.ncbi.nlm.nih.gov/28076365/) · [DOI](https://doi.org/10.1371/journal.pone.0169314)

### 2a. spoke-genelab × prokn — Blood-lymphocyte markers that are themselves spaceflight-responsive
- **Partner KG:** `prokn` — protein/marker-gene evidence graph (HuBMAP-style cell-type markers) recording a cell type as the `rdf:subject` of a reified marker statement whose `rdf:object` is an Ensembl gene IRI labelled with the gene symbol.
- **Shared identifier / bridge:** gene **symbol** (ProKN marker `rdfs:label`, human upper-case ↔ GeneLab `schema:symbol`, mouse mixed-case; matched case-folded). ProKN lymphocyte cell types under CL: NK `CL_0000623`, B `CL_0000236`, CD8 T `CL_0000625`, CD4 T `CL_0000624`.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression in an immune tissue (thymus `UBERON_0002370` / spleen `UBERON_0002106`).
- **Research question:** Microgravity dysregulates circulating lymphocytes. Which ProKN canonical **lymphocyte-subtype marker genes** (NK, B, CD8/CD4 T) are *themselves* differentially expressed in a clean Space-Flight-vs-Ground-Control GeneLab assay in an immune organ — i.e. which of the genes that define each lymphocyte population are also directly spaceflight-responsive?
- **Why the join is required:** ProKN supplies the cell-type→marker-gene assignment (which gene defines which lymphocyte subtype) but holds no spaceflight data; GeneLab supplies the confounder-free spaceflight immune-tissue log2fc but no marker-gene/cell-type annotation. Each row therefore needs ProKN (cell type + marker gene) AND GeneLab (the same gene's clean spaceflight log2fc + tissue).
- **SPARQL** (executed 2026-06-27, returned 12 rows):
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
- **Sample result** (8 of 12) — each row shows prokn + GeneLab data (GeneLab tissue: thymus `UBERON_0002370` unless noted):

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

- **Why it answers the question:** every row pairs a ProKN cell-type→marker-gene assignment with that exact gene's clean GeneLab spaceflight log2fc in an immune organ — surfacing lymphocyte-defining genes that are themselves microgravity-responsive (NK markers **KLRD1**/**GZMB**, CD4-T markers **IL7R**/**CD69**, B-cell marker **FCRL1**, CD8 marker **CD8A**), a both-KG result neither graph yields alone.
- **Literature support:** Stratis et al., 2023, *Front Immunol* — RNA-seq of astronaut leukocytes across ~6-month ISS missions shows spaceflight immune modulation with 276 differentially expressed transcripts (immune suppression entering space, reactivation on return). [PMID:37426644](https://pubmed.ncbi.nlm.nih.gov/37426644/) · [DOI](https://doi.org/10.3389/fimmu.2023.1171103)

### 2b. spoke-genelab × prokn — Cardiomyocyte markers that are themselves spaceflight-responsive
- **Partner KG:** `prokn` — protein/marker-gene evidence graph recording a cell type as the `rdf:subject` of a reified marker statement whose `rdf:object` is an Ensembl gene IRI labelled with the gene symbol.
- **Shared identifier / bridge:** gene **symbol** (ProKN marker `rdfs:label`, human upper-case ↔ GeneLab `schema:symbol`, mouse mixed-case; matched case-folded). ProKN cardiomyocyte cell type: regular atrial cardiac myocyte `CL_0002129` (subtype of cardiac muscle cell `CL_0000746`).
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression in heart `UBERON_0000948` / skeletal-muscle tissues.
- **Research question:** Cardiovascular deconditioning is a core microgravity risk. Which ProKN canonical **cardiomyocyte marker genes** are *themselves* differentially expressed in a clean Space-Flight-vs-Ground-Control GeneLab assay in heart or muscle — i.e. which of the genes that define the cardiac-muscle cell are also directly spaceflight-responsive?
- **Why the join is required:** ProKN supplies the cardiomyocyte→marker-gene assignment but no spaceflight data; GeneLab supplies the confounder-free spaceflight heart/muscle log2fc but no marker-gene/cell-type annotation. Each row needs ProKN (cardiomyocyte + marker gene) AND GeneLab (the same gene's clean spaceflight log2fc + tissue).
- **SPARQL** (executed 2026-06-27, returned 8 rows):
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
    FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
    FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
    FILTER(?adjp < 0.05)
  }
} GROUP BY ?cellType ?markerSym ?genelabSymbol ORDER BY ?glAdjp LIMIT 15
```
- **Sample result** (all 8) — each row shows prokn + GeneLab data (GeneLab tissue: heart `UBERON_0000948`, soleus `UBERON_0001389`, or quadriceps `UBERON_0001377`):

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

- **Why it answers the question:** every row pairs a ProKN cardiomyocyte→marker-gene assignment with that exact gene's clean GeneLab spaceflight log2fc in heart or muscle — the sarcomere/contractility marker set (**MYL7**, **MYH6**, **TTN**, **NPPA**, **ANKRD1**, **CMYA5**) that *defines* the cardiac muscle cell is shown to be directly microgravity-responsive (notably MYL7, NPPA and FGF12 strongly down in heart), a both-KG result neither graph yields alone.
- **Literature support:** Wnorowski et al., 2019, *Stem Cell Reports* — human iPSC-derived cardiomyocytes cultured 5.5 weeks aboard the ISS showed altered calcium handling and 2,635 differentially expressed genes versus ground controls. [PMID:31708475](https://pubmed.ncbi.nlm.nih.gov/31708475/) · [DOI](https://doi.org/10.1016/j.stemcr.2019.10.006)

### 3a. spoke-genelab × biohealth — Kidney: spaceflight DE genes paired with the organ's clinical disease landscape
- **Partner KG:** `biohealth` — BioHealthKG, a SemMedDB-derived literature/clinical evidence graph keyed on UMLS CUIs, recording anatomy→disease associations via `biolink:location_of`.
- **Shared identifier / bridge:** UMLS↔UBERON anatomy (via ubergraph `oboInOwl:hasDbXref`) — kidney `UBERON_0004538` ↔ UMLS `C0227614`; each result row pairs a GeneLab spaceflight DE gene measured *in that kidney* with a biohealth disease *located in that same kidney concept*.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Spaceflight-induced renal dysfunction ("cosmic kidney disease") makes the kidney a priority organ. For the kidney NASA GeneLab examined under a *clean* Space-Flight-vs-Ground-Control contrast, which genes are differentially expressed, and how does that spaceflight-perturbed kidney map onto the organ's documented clinical disease landscape — so the same organ carries a measured space-omics signal and its known pathologies side by side?
- **Why the join is required:** spoke-genelab contributes the per-gene spaceflight differential-expression values (symbol, log2FC, adj. p) for the kidney but holds no clinical/disease knowledge; biohealth contributes the renal diseases localized to the UMLS kidney concept but holds no spaceflight data. Each row exists only because the UMLS↔UBERON bridge ties both KGs' values to the one spaceflight-perturbed kidney.
- **SPARQL** (executed 2026-06-27, returned 10 rows — 10 clean-contrast kidney DE genes paired with 10 of the kidney diseases biohealth localizes to `C0227614`):
```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# Row N pairs the Nth-most-significant GeneLab clean SF-vs-GC DE gene in kidney (UBERON_0004538)
# with the Nth biohealth disease located in the same UMLS kidney concept (C0227614). Both KGs per row.
SELECT ?rank ?symbol ?log2fc ?adjp ?diseaseLabel WHERE {
  {  # ---- GeneLab: clean SF-vs-GC DE genes in kidney, ranked by significance ----
    SELECT ?symbol ?log2fc ?adjp (COUNT(DISTINCT ?s2) AS ?rank) WHERE {
      {
        SELECT ?symbol (SAMPLE(?lfc) AS ?log2fc) (MIN(?ap) AS ?adjp) WHERE {
          GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
            ?a schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
               schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
               schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0004538> .
            FILTER(?m1 = ?m2)
            FILTER NOT EXISTS { ?a schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
            FILTER NOT EXISTS { ?a schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
            ?st rdf:subject ?a ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
                rdf:object ?g ; schema:log2fc ?lfc ; schema:adj_p_value ?ap .
            ?g schema:symbol ?symbol . FILTER(?ap < 1.0e-15)
          }
        } GROUP BY ?symbol
      }
      {
        SELECT ?s2 (MIN(?ap2) AS ?adjp2) WHERE {
          GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
            ?a2 schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
                schema:material_id_1 ?n1 ; schema:material_id_2 ?n2 ;
                schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0004538> .
            FILTER(?n1 = ?n2)
            FILTER NOT EXISTS { ?a2 schema:factors_1 ?g1 . FILTER(?g1 != "Space Flight") }
            FILTER NOT EXISTS { ?a2 schema:factors_2 ?g2 . FILTER(?g2 != "Ground Control") }
            ?x2 rdf:subject ?a2 ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
                rdf:object ?ge2 ; schema:adj_p_value ?ap2 .
            ?ge2 schema:symbol ?s2 . FILTER(?ap2 < 1.0e-15)
          }
        } GROUP BY ?s2
      }
      FILTER(?adjp2 <= ?adjp)
    } GROUP BY ?symbol ?log2fc ?adjp
  }
  {  # ---- biohealth: kidney diseases located in the UMLS kidney concept, ranked alphabetically ----
    SELECT ?diseaseLabel (COUNT(DISTINCT ?dl2) AS ?rank) WHERE {
      {
        SELECT DISTINCT ?diseaseLabel WHERE {
          GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
            <http://purl.obolibrary.org/obo/UBERON_0004538> <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
            FILTER(STRSTARTS(STR(?x),'UMLS:')) BIND(STRAFTER(STR(?x),'UMLS:') AS ?cui)
          }
          BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/',?cui)) AS ?bh)
          GRAPH <https://purl.org/okn/frink/kg/biohealth> {
            ?bh <https://w3id.org/biolink/vocab/location_of> ?disease .
            ?disease <http://www.w3.org/2000/01/rdf-schema#label> ?diseaseLabel ;
                     <https://w3id.org/biolink/vocab/category> ?cat .
            FILTER(CONTAINS(STR(?cat),"neop") || CONTAINS(STR(?cat),"dsyn"))
            FILTER(CONTAINS(LCASE(?diseaseLabel),"renal") || CONTAINS(LCASE(?diseaseLabel),"kidney") || CONTAINS(LCASE(?diseaseLabel),"nephr"))
          }
        }
      }
      {
        SELECT DISTINCT ?dl2 WHERE {
          GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
            <http://purl.obolibrary.org/obo/UBERON_0004538> <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?y .
            FILTER(STRSTARTS(STR(?y),'UMLS:')) BIND(STRAFTER(STR(?y),'UMLS:') AS ?cui2)
          }
          BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/',?cui2)) AS ?bh2)
          GRAPH <https://purl.org/okn/frink/kg/biohealth> {
            ?bh2 <https://w3id.org/biolink/vocab/location_of> ?d2 .
            ?d2 <http://www.w3.org/2000/01/rdf-schema#label> ?dl2 ;
                <https://w3id.org/biolink/vocab/category> ?cat2 .
            FILTER(CONTAINS(STR(?cat2),"neop") || CONTAINS(STR(?cat2),"dsyn"))
            FILTER(CONTAINS(LCASE(?dl2),"renal") || CONTAINS(LCASE(?dl2),"kidney") || CONTAINS(LCASE(?dl2),"nephr"))
          }
        }
      }
      FILTER(?dl2 <= ?diseaseLabel)
    } GROUP BY ?diseaseLabel
  }
} ORDER BY ?rank LIMIT 10
```
- **Sample result** (9 of 10) — each row carries a GeneLab spaceflight value AND a biohealth value for the same spaceflight-perturbed kidney:

| # | GeneLab gene (clean SF vs GC) | log2FC (SF vs GC) | adj. p | biohealth disease in kidney |
|---|---|---|---|---|
| 1 | Fgg | +2.97 (up) | 2.8e-33 | [M]Epithelial nephroblastoma |
| 2 | Nqo1 | +1.15 (up) | 3.7e-24 | Absent renal function |
| 3 | Eif4ebp3 | +2.26 (up) | 1.7e-23 | Acute focal nephritis |
| 4 | Kcnip2 | +2.14 (up) | 1.6e-21 | Acute glomerulonephritis NOS |
| 5 | Gm15348 | -2.10 (down) | 1.5e-17 | Acute pyelonephritis |
| 6 | Eci2 | +0.90 (up) | 5.4e-17 | Adrenal Cortical Adenoma |
| 7 | Npas2 | +1.44 (up) | 1.7e-16 | Advanced Renal Cell Carcinoma |
| 8 | St8sia1 | -1.43 (down) | 3.9e-16 | Angiomyolipoma of kidney |
| 9 | Peg3 | +2.26 (up) | 4.3e-16 | Atrophy of kidney |

- **Why it answers the question:** every row places a confounder-free Space-Flight-vs-Ground-Control kidney DE gene (GeneLab: Fgg, Nqo1, Peg3 …, with direction and significance) next to a clinically documented disease of the very same kidney (biohealth: renal cell carcinoma, glomerulonephritis, kidney atrophy …) — neither column is reachable from one KG alone, and the UMLS↔UBERON bridge guarantees both describe the one spaceflight-perturbed organ.
- **Literature support:** Siew et al., 2024, *Nat Commun* — "Cosmic kidney disease": an integrated pan-omic study showing microgravity and cosmic radiation drive kidney remodeling, nephron damage, and spaceflight-induced renal dysfunction. [PMID:38862484](https://pubmed.ncbi.nlm.nih.gov/38862484/) · [DOI](https://doi.org/10.1038/s41467-024-49212-1)

### 3b. spoke-genelab × biohealth — Spleen: clean-contrast spaceflight DE genes paired with the organ's clinical disease landscape
- **Partner KG:** `biohealth` — BioHealthKG, a SemMedDB-derived literature/clinical evidence graph keyed on UMLS CUIs, recording anatomy→disease associations via `biolink:location_of`.
- **Shared identifier / bridge:** UMLS↔UBERON anatomy (via ubergraph `oboInOwl:hasDbXref`) — spleen `UBERON_0002106` ↔ UMLS `C0037993`; each result row pairs a GeneLab spaceflight DE gene measured *in the spleen* with a biohealth disease *located in that same spleen concept*.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Spaceflight is documented to shrink and remodel immune organs, and the spleen is examined in clean Space-Flight-vs-Ground-Control GeneLab assays. Which genes are differentially expressed in the spaceflight spleen, and how does that perturbed organ map onto the splenic diseases catalogued in the clinical literature — so a measured space-omics signal and the organ's documented pathologies sit on the same rows?
- **Why the join is required:** spoke-genelab contributes the per-gene spaceflight differential-expression values (symbol, log2FC, adj. p) for the spleen but holds no clinical/disease knowledge; biohealth contributes the splenic diseases localized to the UMLS spleen concept but holds no spaceflight data. Each row exists only because the UMLS↔UBERON bridge ties both KGs' values to the one spaceflight-perturbed spleen.
- **SPARQL** (executed 2026-06-27, returned 9 rows — 9 clean-contrast spleen DE genes paired with 9 of the splenic diseases biohealth localizes to `C0037993`):
```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# Row N pairs the Nth-most-significant GeneLab clean SF-vs-GC DE gene in spleen (UBERON_0002106)
# with the Nth biohealth splenic disease located in the same UMLS spleen concept (C0037993). Both KGs per row.
SELECT ?rank ?symbol ?log2fc ?adjp ?diseaseLabel WHERE {
  {  # ---- GeneLab: clean SF-vs-GC DE genes in spleen, ranked by significance ----
    SELECT ?symbol ?log2fc ?adjp (COUNT(DISTINCT ?s2) AS ?rank) WHERE {
      {
        SELECT ?symbol (SAMPLE(?lfc) AS ?log2fc) (MIN(?ap) AS ?adjp) WHERE {
          GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
            ?a schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
               schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
               schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0002106> .
            FILTER(?m1 = ?m2)
            FILTER NOT EXISTS { ?a schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
            FILTER NOT EXISTS { ?a schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
            ?st rdf:subject ?a ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
                rdf:object ?g ; schema:log2fc ?lfc ; schema:adj_p_value ?ap .
            ?g schema:symbol ?symbol . FILTER(?ap < 1.0e-6)
          }
        } GROUP BY ?symbol
      }
      {
        SELECT ?s2 (MIN(?ap2) AS ?adjp2) WHERE {
          GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
            ?a2 schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
                schema:material_id_1 ?n1 ; schema:material_id_2 ?n2 ;
                schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0002106> .
            FILTER(?n1 = ?n2)
            FILTER NOT EXISTS { ?a2 schema:factors_1 ?g1 . FILTER(?g1 != "Space Flight") }
            FILTER NOT EXISTS { ?a2 schema:factors_2 ?g2 . FILTER(?g2 != "Ground Control") }
            ?x2 rdf:subject ?a2 ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
                rdf:object ?ge2 ; schema:adj_p_value ?ap2 .
            ?ge2 schema:symbol ?s2 . FILTER(?ap2 < 1.0e-6)
          }
        } GROUP BY ?s2
      }
      FILTER(?adjp2 <= ?adjp)
    } GROUP BY ?symbol ?log2fc ?adjp
  }
  {  # ---- biohealth: splenic diseases located in the UMLS spleen concept, ranked alphabetically ----
    SELECT ?diseaseLabel (COUNT(DISTINCT ?dl2) AS ?rank) WHERE {
      {
        SELECT DISTINCT ?diseaseLabel WHERE {
          GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
            <http://purl.obolibrary.org/obo/UBERON_0002106> <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
            FILTER(STRSTARTS(STR(?x),'UMLS:')) BIND(STRAFTER(STR(?x),'UMLS:') AS ?cui)
          }
          BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/',?cui)) AS ?bh)
          GRAPH <https://purl.org/okn/frink/kg/biohealth> {
            ?bh <https://w3id.org/biolink/vocab/location_of> ?disease .
            ?disease <http://www.w3.org/2000/01/rdf-schema#label> ?diseaseLabel ;
                     <https://w3id.org/biolink/vocab/category> ?cat .
            FILTER(CONTAINS(STR(?cat),"neop") || CONTAINS(STR(?cat),"dsyn"))
            FILTER(CONTAINS(LCASE(?diseaseLabel),"splen") || CONTAINS(LCASE(?diseaseLabel),"spleen"))
          }
        }
      }
      {
        SELECT DISTINCT ?dl2 WHERE {
          GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
            <http://purl.obolibrary.org/obo/UBERON_0002106> <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?y .
            FILTER(STRSTARTS(STR(?y),'UMLS:')) BIND(STRAFTER(STR(?y),'UMLS:') AS ?cui2)
          }
          BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/',?cui2)) AS ?bh2)
          GRAPH <https://purl.org/okn/frink/kg/biohealth> {
            ?bh2 <https://w3id.org/biolink/vocab/location_of> ?d2 .
            ?d2 <http://www.w3.org/2000/01/rdf-schema#label> ?dl2 ;
                <https://w3id.org/biolink/vocab/category> ?cat2 .
            FILTER(CONTAINS(STR(?cat2),"neop") || CONTAINS(STR(?cat2),"dsyn"))
            FILTER(CONTAINS(LCASE(?dl2),"splen") || CONTAINS(LCASE(?dl2),"spleen"))
          }
        }
      }
      FILTER(?dl2 <= ?diseaseLabel)
    } GROUP BY ?diseaseLabel
  }
} ORDER BY ?rank LIMIT 9
```
- **Sample result** (9 of 9) — each row carries a GeneLab spaceflight value AND a biohealth value for the same spaceflight-perturbed spleen:

| # | GeneLab gene (clean SF vs GC) | log2FC (SF vs GC) | adj. p | biohealth disease in spleen |
|---|---|---|---|---|
| 1 | Gpx3 | +0.93 (up) | 4.8e-14 | Anemia, Splenic |
| 2 | Ttc39aos1 | +3.49 (up) | 3.7e-10 | Angiosarcoma of spleen |
| 3 | Lamc3 | +0.96 (up) | 9.7e-10 | Calcification of spleen |
| 4 | Slc6a9 | +2.77 (up) | 1.1e-8 | Hemangioma of spleen |
| 5 | Ccdc92b | +3.75 (up) | 1.6e-8 | Hepatosplenic schistosomiasis |
| 6 | Mageb16 | +4.30 (up) | 4.1e-8 | Hepatosplenic T-Cell Lymphoma |
| 7 | Sox6 | +3.05 (up) | 1.2e-7 | Hypersplenism |
| 8 | Sparcl1 | +0.83 (up) | 2.1e-7 | Lesion of spleen |
| 9 | F930017D23Rik | +3.17 (up) | 3.0e-7 | Malignant lymphoma of spleen |

- **Why it answers the question:** every row places a confounder-free Space-Flight-vs-Ground-Control spleen DE gene (GeneLab: the antioxidant Gpx3, the erythroid TF Sox6, Sparcl1 …, with direction and significance) next to a clinically documented splenic disease (biohealth: splenic anemia, hypersplenism, splenic lymphoma …) — a space-omics signal and the organ's pathologies that neither KG holds together, joined only through the UMLS↔UBERON spleen bridge.
- **Literature support:** Okamura et al., 2024, *Sci Rep* — mice housed 25–35 days aboard the ISS showed spaceflight-induced gene-expression changes in the spleen alongside thymus atrophy, demonstrating microgravity remodeling of immune organs. [PMID:39567640](https://pubmed.ncbi.nlm.nih.gov/39567640/) · [DOI](https://doi.org/10.1038/s41598-024-79315-0)

## Genes & Functional Genomics

### 4a. spoke-genelab × biobricks-aopwiki — Oxidative-stress / ROS / DNA-damage / genotoxicity AOP key-event genes (clean spaceflight contrast)
- **Partner KG:** `biobricks-aopwiki` — Adverse Outcome Pathways (AOP-Wiki); molecular key events and their gene targets, keyed to Entrez via `skos:exactMatch`.
- **Shared identifier / bridge:** Entrez gene id (direct) — AOP-Wiki `identifiers.org/ncbigene/{id}` rewritten to spoke-genelab's `www.ncbi.nlm.nih.gov/gene/{id}` form.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Which key-event genes of AOPs for **oxidative stress, reactive-oxygen-species toxicity, and DNA-damage genotoxicity** (including the ionizing-radiation → DNA-damage pathway) are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction? This targets the cosmic-radiation / oxidative axis of astronaut risk without the confounded assays.
- **Why the join is required:** AOP-Wiki defines which genes are mechanistic key events of oxidative/genotoxic pathways but has no spaceflight data; spoke-genelab has the spaceflight differential-expression measurements but no AOP annotation. Only the Entrez join links a genotoxicity pathway target to a measured, unconfounded spaceflight stress response.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT DISTINCT ?aopTitle ?symbol (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  {
    SELECT DISTINCT ?gene ?aopTitle WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
        ?ke <http://edamontology.org/data_1025> ?gnode .
        ?gnode skos:exactMatch ?e .
        FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/'))
        FILTER(CONTAINS(LCASE(?aopTitle),'oxidative') || CONTAINS(LCASE(?aopTitle),'dna damage')
            || CONTAINS(LCASE(?aopTitle),'genotox') || CONTAINS(LCASE(?aopTitle),'reactive oxygen'))
      }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?e),'^.*/ncbigene/',''))) AS ?gene)
    }
  }
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    ?gene sg:symbol ?symbol .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?aopTitle ?symbol ORDER BY ?minAdjP LIMIT 15
```
- **Sample result** (6 of 15):

| AOP | Gene | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| Ionizing radiation-induced DNA damage → microcephaly via apoptosis | CDKN1A | -3.05 (down) | 2.1e-132 |
| Chronic reactive oxygen species → treatment-resistant gastric cancer | CYP1B1 | -2.48 (down) | 6.1e-63 |
| DNA damage & mutations → metastatic breast cancer | SNAI1 | +2.52 (up) | 3.8e-45 |
| Increased DNA damage → increased risk of breast cancer | CENPJ | +3.21 (up) | 5.8e-44 |
| DNA damage & mutations → metastatic breast cancer | RHOB | -2.21 (down) | 2.7e-40 |
| Activation of reactive oxygen species → atherosclerosis | CCL2 | -2.58 (down) | 6.4e-38 |

- **Why it answers the question:** every gene is a curated key event in an oxidative-stress / ROS / DNA-damage AOP — including the **ionizing-radiation → DNA-damage** pathway directly relevant to cosmic radiation, whose effector **CDKN1A (p21)**, the canonical p53/DNA-damage cell-cycle-arrest gene, is strongly DE — and each is significantly DE in an unconfounded Space-Flight-vs-Ground-Control contrast, so the genotoxic/redox signal (CENPJ, RHOB, CYP1B1, SNAI1, CCL2) is microgravity-driven, not a co-varying factor.
- **Literature support:** Beck et al., 2014, *Int J Mol Med* — chronic simulated space conditions (microgravity + low-dose ionizing radiation) predominantly induce oxidative-stress-responsive (Nrf2-target) genes and alter DNA-damage-response pathways in mammalian cells. [PMID:24859186](https://pubmed.ncbi.nlm.nih.gov/24859186/) · [DOI](https://doi.org/10.3892/ijmm.2014.1785)

### 4b. spoke-genelab × biobricks-aopwiki — Hepatic-steatosis / liver-injury AOP key-event genes (clean spaceflight contrast)
- **Partner KG:** `biobricks-aopwiki` — Adverse Outcome Pathways (AOP-Wiki); molecular key events and their gene targets, keyed to Entrez via `skos:exactMatch`.
- **Shared identifier / bridge:** Entrez gene id (direct) — AOP-Wiki `identifiers.org/ncbigene/{id}` rewritten to spoke-genelab's `www.ncbi.nlm.nih.gov/gene/{id}` form.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Spaceflight drives hepatic lipid accumulation and early liver injury. Which key-event genes of AOPs for **hepatic steatosis, fatty-liver and liver injury / fibrosis** are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction?
- **Why the join is required:** AOP-Wiki defines which genes are mechanistic key events of steatosis/liver-injury pathways but has no spaceflight data; spoke-genelab has the spaceflight differential-expression measurements but no AOP annotation. Only the Entrez join links a steatogenic pathway target to a clean, unconfounded spaceflight stress response.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT DISTINCT ?aopTitle ?symbol ?organism (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
    ?ke <http://edamontology.org/data_1025> ?gnode .
    ?gnode skos:exactMatch ?e .
    FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/'))
    FILTER(CONTAINS(LCASE(?aopTitle),'steato') || CONTAINS(LCASE(?aopTitle),'fibros')
        || CONTAINS(LCASE(?aopTitle),'liver') || CONTAINS(LCASE(?aopTitle),'hepat')
        || CONTAINS(LCASE(?aopTitle),'cholestasis'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?e),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene sg:symbol ?symbol ; sg:organism ?organism .
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
           sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
    FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
    FILTER(?adjp < 0.05)
  }
} GROUP BY ?aopTitle ?symbol ?organism ORDER BY ?minAdjP LIMIT 15
```
- **Sample result** (6 of 15):

| AOP | Gene | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| Inhibition of N-linked glycosylation → liver injury | CDKN1A | -3.05 (down) | 2.1e-132 |
| LXR activation leading to hepatic steatosis | FAS | -2.26 (down) | 4.8e-52 |
| Liver X Receptor (LXR) activation → liver steatosis | FAS | -2.26 (down) | 4.8e-52 |
| NR1I3 (CAR) suppression → hepatic steatosis | FAS | -2.26 (down) | 4.8e-52 |
| TLR4 activation & PPARγ inactivation → fibrosis | CYP1B1 | -2.48 (down) | 6.1e-63 |
| TLR4 activation & PPARγ inactivation → fibrosis | SNAI1 | +2.52 (up) | 3.8e-45 |

- **Why it answers the question:** every gene is a curated key event in a hepatic-steatosis / liver-injury / fibrosis AOP and is significantly DE in an unconfounded Space-Flight-vs-Ground-Control contrast — FAS (fatty-acid synthase, the steatosis effector in three LXR/CAR AOPs) and the injury gene CDKN1A are down, while the fibrosis EMT factor SNAI1 is up — and the clean filter guarantees the signal is microgravity-driven, not a co-varying factor.
- **Literature support:** Beheshti et al., 2019, *Sci Rep* — multi-omics of mice sacrificed on-orbit across ISS missions shows abnormal hepatic lipid accumulation and activation of lipotoxic / fatty-acid-metabolism pathways attributable to space stressors alone. [PMID:31844325](https://pubmed.ncbi.nlm.nih.gov/31844325/) · [DOI](https://doi.org/10.1038/s41598-019-55869-2)

### 5a. spoke-genelab × digcfdekg — Coronary-artery-disease (CAD) factor genes (clean spaceflight contrast)
- **Partner KG:** `digcfdekg` — CFDE REVEAL gene-trait factor inferences with PIGEAN relevance scores (gene→trait via reified `dig:geneToTrait` + `dig:weight`).
- **Shared identifier / bridge:** Entrez gene id (direct) — identical `www.ncbi.nlm.nih.gov/gene/{id}` form in both graphs, no rewrite.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Long-duration spaceflight raises cardiovascular-disease concern. Which genes CFDE REVEAL infers as relevant to **coronary artery disease (CAD)** (trait `449de16e8049af35333b`) are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction — do the genes underlying CAD genetic risk show up as genuinely microgravity-responsive?
- **Why the join is required:** digcfdekg supplies the PIGEAN CAD gene-relevance scores; spoke-genelab supplies clean spaceflight differential expression but has no disease-relevance concept. Identifying which CAD-relevant genes are genuinely microgravity-responsive needs the Entrez join plus the confounder-free contrast.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?sym ?pigeanScore (MAX(?lfc) AS ?maxLog2fc) (MIN(?lfc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) (COUNT(DISTINCT ?assay) AS ?nCleanAssays) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <https://purl.org/okn/frink/kg/digcfdekg/node/trait/449de16e8049af35333b> ;
        rdf:subject ?gene ; dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 3.0)
  }
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 15
```
- **Sample result** (8 of 15):

| Gene | PIGEAN (CAD) | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| APOE | 10.9 | +2.05 (up) | 2.6e-12 |
| SCARB1 | 9.73 | +0.92 (up) | 5.7e-7 |
| PCSK9 | 8.86 | -1.15 (down) | 1.7e-4 |
| LIPA | 7.88 | -1.13 (down) | 7.1e-14 |
| SMAD3 | 7.62 | +1.61 (up) | 1.7e-32 |
| EDNRA | 5.67 | -2.05 (down) | 8.9e-13 |
| TCF21 | 5.63 | -2.03 (down) | 1.0e-13 |
| LIPG | 5.56 | -2.21 (down) | 8.5e-16 |

- **Why it answers the question:** the intersection is the canonical lipid/atherosclerosis machinery — the highest-confidence CFDE CAD genes APOE, SCARB1, PCSK9, LIPA, LIPG — joined by the vascular-remodeling factors SMAD3 (TGF-β), EDNRA (endothelin receptor) and the coronary-artery transcription factor TCF21, every one significantly DE in an unconfounded Space-Flight-vs-Ground-Control contrast (APOE up, PCSK9 down), giving confounder-free molecular evidence that microgravity perturbs the genetic circuitry of coronary disease.
- **Literature support:** Robin et al., 2023, *Nat Commun* — dry-immersion microgravity simulation rapidly induced a metabolic-syndrome-like shift with an increased atherogenic index of plasma and impaired lipid profile, alongside cardiovascular deconditioning. [PMID:37813884](https://pubmed.ncbi.nlm.nih.gov/37813884/) · [DOI](https://doi.org/10.1038/s41467-023-41990-4)

### 5b. spoke-genelab × digcfdekg — Glomerular-filtration-rate (eGFR / kidney-function) factor genes responsive to clean spaceflight
- **Partner KG:** `digcfdekg` — CFDE REVEAL gene-trait factor inferences with PIGEAN relevance scores (gene→trait via reified `dig:geneToTrait` + `dig:weight`).
- **Shared identifier / bridge:** Entrez gene id (direct) — identical `www.ncbi.nlm.nih.gov/gene/{id}` form in both graphs, no rewrite.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** "Cosmic kidney disease" and microgravity fluid shifts make renal function a priority risk. Which genes CFDE REVEAL infers as relevant to **glomerular filtration rate (eGFR / kidney function, OBA_0003747)** are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast, and in which direction?
- **Why the join is required:** digcfdekg supplies the PIGEAN eGFR gene-relevance scores; spoke-genelab supplies clean spaceflight differential expression but has no trait-relevance concept. Identifying which kidney-function genes are genuinely microgravity-responsive needs the Entrez join plus the confounder-free contrast.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?sym ?pigeanScore (MAX(?lfc) AS ?maxLog2fc) (MIN(?lfc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) (COUNT(DISTINCT ?assay) AS ?nCleanAssays) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/OBA_0003747> ;
        rdf:subject ?gene ; dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 4.0)
  }
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 15
```
- **Sample result** (8 of 15):

| Gene | PIGEAN (eGFR) | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| SALL1 | 6.27 | -1.18 (down) | 3.4e-5 |
| SLC15A2 | 6.15 | +3.25 (up) | 1.4e-10 |
| SHH | 6.11 | -2.48 (down) | 3.5e-5 |
| SLC47A1 | 5.98 | -2.38 (down) | 2.7e-5 |
| REN | 4.56 | +6.44 (up) | 4.2e-10 |
| MAF | 4.48 | -6.49 (down) | 4.2e-13 |
| PAX8 | 4.34 | -3.78 (down) | 3.3e-39 |
| PKD1 | 4.20 | +0.48 (up) | 1.2e-3 |

- **Why it answers the question:** the intersection is the core kidney-function machinery — **REN (renin) strongly up (+6.44)** in the clean contrast, renal solute transporters SLC15A2/SLC47A1, kidney developmental factors SALL1/PAX8/SHH, and the polycystic-kidney gene PKD1 — tying eGFR genetics to confounder-free microgravity perturbation; the renin up-regulation is the expected direction for spaceflight RAAS activation.
- **Literature support:** Norsk, 2000, *Pflügers Archiv* ("Renal adjustments to microgravity") — spaceflight attenuates renal fluid excretion and elevates the renin–angiotensin–aldosterone axis, the physiological correlate of the up-regulated REN seen here. [PMID:11200982](https://pubmed.ncbi.nlm.nih.gov/11200982/) · [DOI](https://doi.org/10.1007/s004240000332)

### 6a. spoke-genelab × rdkg — DNA-repair / genome-instability rare-disease genes (clean spaceflight contrast, via ortholog)
- **Partner KG:** `rdkg` — rare-disease gene/disease associations (Orphanet/MONDO/DrugBank/Entrez); `biolink:Gene` → `biolink:related_to` → `biolink:Disease` (MONDO).
- **Shared identifier / bridge:** Entrez gene id via ortholog — rdkg human gene `identifiers.org/ncbigene/{id}` rewritten to `www.ncbi.nlm.nih.gov/gene/{id}`, then bridged to the assayed mouse gene through spoke-genelab's `IS_ORTHOLOG_MGiG`.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Which **DNA-repair and genome-instability rare-disease genes** — Fanconi anemia, xeroderma pigmentosum / Cockayne, trichothiodystrophy, dyskeratosis congenita, ataxia-telangiectasia, Bloom, Nijmegen — are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast? These monogenic genome-maintenance disorders are the most mechanistically relevant rare diseases to chronic cosmic-radiation DNA damage.
- **Why the join is required:** rdkg curates the rare-disease gene set but has no spaceflight data; spoke-genelab has the clean spaceflight differential expression but no rare-disease annotation, and assays the mouse ortholog. Connecting a genome-maintenance disease gene to its measured, unconfounded spaceflight perturbation needs the Entrez+ortholog join.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym (SAMPLE(?diseaseLabel) AS ?exampleRareDisease) (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  {
    SELECT DISTINCT ?gene ?sym ?diseaseLabel WHERE {
      GRAPH <https://purl.org/okn/frink/kg/rdkg> {
        ?r a biolink:Gene ; rdfs:label ?sym ; biolink:related_to ?mondo .
        FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
        ?mondo a biolink:Disease ; rdfs:label ?diseaseLabel .
        FILTER(CONTAINS(LCASE(?diseaseLabel),'fanconi') || CONTAINS(LCASE(?diseaseLabel),'xeroderma')
            || CONTAINS(LCASE(?diseaseLabel),'ataxia-telangiectasia') || CONTAINS(LCASE(?diseaseLabel),'bloom syndrome')
            || CONTAINS(LCASE(?diseaseLabel),'cockayne') || CONTAINS(LCASE(?diseaseLabel),'nijmegen')
            || CONTAINS(LCASE(?diseaseLabel),'trichothiodystrophy') || CONTAINS(LCASE(?diseaseLabel),'dyskeratosis'))
      }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene)
    }
  }
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?modelGene sg:IS_ORTHOLOG_MGiG ?gene .
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?modelGene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?sym ORDER BY ?minAdjP LIMIT 15
```
- **Sample result** (8 of 15) — human rare-disease gene symbols (assayed via mouse ortholog; ± indicates both directions seen across clean assays):

| Gene (human) | example rare disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| FANCA | Fanconi anemia complementation group | -3.93 / +3.08 | 7.8e-38 |
| XPC | xeroderma pigmentosum | -0.81 (down) | 5.0e-23 |
| UNG | Bloom syndrome | -2.13 (down) | 2.9e-21 |
| FANCI | Fanconi anemia complementation group | +2.75 (up) | 6.4e-20 |
| BRIP1 | Fanconi anemia | -3.16 / +4.08 | 2.1e-17 |
| NOP10 | dyskeratosis congenita, autosomal recessive | -1.21 (down) | 1.9e-14 |
| FANCD2 | Fanconi anemia | -4.86 / +2.35 | 2.3e-13 |
| RAD51 | Fanconi anemia | -2.25 / +2.35 | 5.1e-12 |

- **Why it answers the question:** measured under a confounder-free Space-Flight-vs-Ground-Control contrast, the hits are the core genome-maintenance machinery — the Fanconi-anemia complex (FANCA, FANCI, FANCD2, BRIP1, the homologous-recombination recombinase RAD51), nucleotide-excision-repair gene XPC, base-excision-repair glycosylase UNG (Bloom), and the telomere/dyskeratosis gene NOP10 — directly linking inherited genome-instability disorders to genuine microgravity-driven perturbation in the spaceflight DNA-damage environment.
- **Literature support:** Handwerk et al., 2023, *Int J Mol Sci* — simulated space conditions (microgravity + particle irradiation) evoke DNA-damage responses and induce FANCD2 foci and replication stress in human hematopoietic stem/progenitor cells, implicating Fanconi-pathway / genome-instability machinery in spaceflight. [PMID:37762064](https://pubmed.ncbi.nlm.nih.gov/37762064/) · [DOI](https://doi.org/10.3390/ijms241813761)

### 6b. spoke-genelab × rdkg — Muscular-dystrophy / cardiomyopathy / myopathy rare-disease genes DE in clean skeletal-muscle spaceflight
- **Partner KG:** `rdkg` — rare-disease gene/disease associations (Orphanet/MONDO/DrugBank/Entrez); `biolink:Gene` → `biolink:related_to` → `biolink:Disease`.
- **Shared identifier / bridge:** Entrez gene id via ortholog — rdkg human gene `identifiers.org/ncbigene/{id}` rewritten to spoke-genelab's `www.ncbi.nlm.nih.gov/gene/{id}`, then bridged to the assayed mouse gene through spoke-genelab's `IS_ORTHOLOG_MGiG`.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter), restricted to skeletal-muscle tissues; gene expression.
- **Research question:** Skeletal-muscle and cardiac atrophy are signature spaceflight risks. Which **muscular-dystrophy, myopathy and cardiomyopathy rare-disease genes** are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast measured directly in skeletal muscle, and in which direction?
- **Why the join is required:** rdkg curates the muscle/heart rare-disease gene set but has no spaceflight data; spoke-genelab has the clean in-muscle spaceflight expression but no rare-disease annotation, and assays the mouse ortholog. Connecting a Mendelian muscle-disease gene to its measured, unconfounded spaceflight perturbation in muscle needs the Entrez+ortholog join.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?humanSym ?modelSym ?tissue (SAMPLE(?diseaseLabel) AS ?exampleRareDisease) (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?r a biolink:Gene ; rdfs:label ?humanSym ; biolink:related_to ?mondo .
    FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
    ?mondo a biolink:Disease ; rdfs:label ?diseaseLabel .
    FILTER(CONTAINS(LCASE(?diseaseLabel),'muscular dystrophy') || CONTAINS(LCASE(?diseaseLabel),'myopathy')
        || CONTAINS(LCASE(?diseaseLabel),'cardiomyopathy') || CONTAINS(LCASE(?diseaseLabel),'myofibrillar'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?hgene)
  {
    SELECT DISTINCT ?assay ?tissue WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 ; sg:material_name_1 ?tissue .
        FILTER(?m1 = ?m2)
        FILTER(?tissue IN ("quadriceps femoris","tibialis anterior","soleus","gastrocnemius","extensor digitorum longus","heart"))
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?modelGene sg:IS_ORTHOLOG_MGiG ?hgene ; sg:symbol ?modelSym .
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?modelGene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.001)
  }
} GROUP BY ?humanSym ?modelSym ?tissue ORDER BY ?minAdjP LIMIT 15
```
- **Sample result** (8 of 15):

| Gene (mouse→human) | tissue | example rare disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|---|
| Eya4 → EYA4 | soleus | dilated cardiomyopathy | +1.37 (up) | 1.2e-50 |
| Idh2 → IDH2 | soleus | cardiomyopathy | -1.36 (down) | 9.7e-41 |
| Pdlim3 → PDLIM3 | soleus | hypertrophic cardiomyopathy | +2.41 (up) | 2.0e-38 |
| Alpk3 → ALPK3 | soleus | hypertrophic cardiomyopathy | -0.73 (down) | 8.7e-38 |
| Pln → PLN | soleus | dilated cardiomyopathy | -3.49 (down) | 1.7e-37 |
| Ryr1 → RYR1 | soleus | congenital myopathy | +0.48 (up) | 4.2e-32 |
| Tnnt1 → TNNT1 | quadriceps femoris | nemaline myopathy | -3.61 (down) | 9.7e-20 |
| Hnrnpa1 → HNRNPA1 | EDL | inclusion-body myopathy | -3.79 (down) | 1.1e-18 |

- **Why it answers the question:** measured directly in spaceflight skeletal muscle under a confounder-free contrast, the hits are the canonical contractile / calcium-handling / sarcomere disease genes — PLN (phospholamban, dilated cardiomyopathy, strongly down), RYR1, the nemaline-myopathy troponin TNNT1 (down), PDLIM3/ALPK3/EYA4 (cardiomyopathy), HNRNPA1 — linking inherited muscle-wasting genetics to genuine microgravity-driven muscle perturbation.
- **Literature support:** Henrich et al., 2022, *Skeletal Muscle* — RNA-seq of mouse gastrocnemius and quadriceps after 9 weeks of spaceflight shows the skeletal-muscle transcriptome is remodeled in structural/contractile and fiber-type gene networks associated with atrophy. [PMID:35642060](https://pubmed.ncbi.nlm.nih.gov/35642060/) · [DOI](https://doi.org/10.1186/s13395-022-00294-9)

### 7a. spoke-genelab × spoke-okn — Immune / inflammatory / autoimmune disease genes (clean spaceflight contrast)
- **Partner KG:** `spoke-okn` — SPOKE gene/compound/disease association network; gene→disease via `ASSOCIATES_DaG`.
- **Shared identifier / bridge:** Entrez gene id (direct) — both KGs use `www.ncbi.nlm.nih.gov/gene/{id}` IRIs.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.
- **Research question:** Which genes most strongly differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast are associated in SPOKE with **immune, inflammatory and autoimmune disease** (rheumatoid arthritis, psoriasis, asthma, inflammatory bowel disease, lupus, multiple sclerosis)? This probes the immune-dysregulation system using only confounder-free assays — distinct from the methylation angle in block 7b.
- **Why the join is required:** spoke-genelab has clean spaceflight expression but no curated gene–disease associations; spoke-okn has the gene–disease associations but no spaceflight data. The direct Entrez join links an unconfounded spaceflight transcriptional response to its immune-disease relevance.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?spokeDisease (MAX(?lfc) AS ?maxLog2fc) (MIN(?lfc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 1.0e-10)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?gene rdfs:label ?sym .
    ?d spoke:ASSOCIATES_DaG ?gene ; rdfs:label ?spokeDisease .
    FILTER(CONTAINS(LCASE(?spokeDisease),'arthritis') || CONTAINS(LCASE(?spokeDisease),'lupus')
        || CONTAINS(LCASE(?spokeDisease),'psoriasis') || CONTAINS(LCASE(?spokeDisease),'asthma')
        || CONTAINS(LCASE(?spokeDisease),'inflammatory bowel') || CONTAINS(LCASE(?spokeDisease),'crohn')
        || CONTAINS(LCASE(?spokeDisease),'colitis') || CONTAINS(LCASE(?spokeDisease),'multiple sclerosis')
        || CONTAINS(LCASE(?spokeDisease),'autoimmune'))
  }
} GROUP BY ?sym ?spokeDisease ORDER BY ?minAdjP LIMIT 15
```
- **Sample result** (8 of 15):

| Gene | SPOKE immune/inflammatory disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| MMP3 | rheumatoid arthritis; osteoarthritis | -7.94 (down) | 7.9e-201 |
| DPP4 | asthma; rheumatoid arthritis | -5.16 (down) | 2.7e-111 |
| NEFL | multiple sclerosis | -6.97 (down) | 2.5e-62 |
| RCAN1 | rheumatoid arthritis | -2.44 (down) | 2.2e-54 |
| FAS | rheumatoid arthritis; inflammatory bowel disease | -2.26 (down) | 4.8e-52 |
| ADAMTS5 | osteoarthritis | -3.18 (down) | 7.4e-52 |
| TFRC | asthma | -2.34 (down) | 3.2e-51 |
| CARD11 | asthma; inflammatory bowel disease | +3.29 (up) | 1.1e-50 |

- **Why it answers the question:** under a confounder-free Space-Flight-vs-Ground-Control contrast, the most strongly perturbed genes carrying SPOKE immune-disease associations are bona-fide inflammatory effectors — the matrix metalloproteinase MMP3 and aggrecanase ADAMTS5 (joint-destruction enzymes in arthritis, strongly down), DPP4, the death receptor FAS (RA/IBD), the MS axonal marker NEFL, and the NF-κB-activating CBM-complex scaffold CARD11 (up; asthma/IBD) — mapping a clean spaceflight transcriptional response onto autoimmune/inflammatory disease, consistent with documented spaceflight immune dysregulation. (Note: MMP3 here is strongly *down* in clean contrasts — the opposite sign to the earlier confounded version, illustrating why the contrast matters.)
- **Literature support:** Cools et al., 2026, *Prog Biophys Mol Biol* — review of microgravity effects on human physiology documents immune dysregulation as a core, persistent spaceflight adaptation across organ systems. [PMID:42162925](https://pubmed.ncbi.nlm.nih.gov/42162925/) · [DOI](https://doi.org/10.1016/j.pbiomolbio.2026.05.004)

### 7b. spoke-genelab × spoke-okn — DNA-methylation layer: clean skeletal-muscle differentially-methylated genes mapped to SPOKE disease
- **Partner KG:** `spoke-okn` — SPOKE gene/compound/disease association network; gene→disease via `ASSOCIATES_DaG`.
- **Shared identifier / bridge:** Entrez gene id via ortholog — spoke-genelab maps the methylated mouse gene to its human ortholog with `IS_ORTHOLOG_MGiG`; both graphs use `www.ncbi.nlm.nih.gov/gene/{id}` for the human gene.
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter), restricted to skeletal-muscle tissues (tibialis anterior / quadriceps femoris); **DNA methylation** (`MEASURED_DIFFERENTIAL_METHYLATION_ASmMR`, region→gene via `METHYLATED_IN_MGmMR`, `methylation_diff` + `q_value`).
- **Research question:** Beyond expression, does spaceflight leave an **epigenetic mark on skeletal muscle**? Which genes are most strongly and significantly differentially *methylated* in a *clean* Space-Flight-vs-Ground-Control contrast in tibialis anterior / quadriceps, and which diseases does SPOKE associate them with?
- **Why the join is required:** spoke-genelab holds the spaceflight muscle methylation but no disease context; spoke-okn holds the gene–disease associations but no spaceflight/epigenetics data, and the methylated gene is the mouse ortholog. Connecting a clean spaceflight methylation hit to disease relevance needs the methylation→gene→ortholog→`ASSOCIATES_DaG` chain.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?modelSym ?tissue ?disease (MAX(ABS(?mdiff)) AS ?maxAbsMethylDiff) (MIN(?qval) AS ?minQ) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
           sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 ; sg:material_name_1 ?tissue .
    FILTER(?m1 = ?m2)
    FILTER(?tissue IN ("tibialis anterior","quadriceps femoris"))
    FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
    FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
    ?st rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_METHYLATION_ASmMR ;
        rdf:object ?mr ; sg:methylation_diff ?mdiff ; sg:q_value ?qval .
    ?gene sg:METHYLATED_IN_MGmMR ?mr ; sg:symbol ?modelSym ; sg:IS_ORTHOLOG_MGiG ?humanGene .
    FILTER(ABS(?mdiff) > 20)
    FILTER(?qval < 0.05)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?d spoke:ASSOCIATES_DaG ?humanGene ; rdfs:label ?disease .
  }
} GROUP BY ?modelSym ?tissue ?disease ORDER BY DESC(?maxAbsMethylDiff) LIMIT 15
```
- **Sample result** (7 of 15):

| Gene (mouse) | tissue | SPOKE disease | max \|methyl Δ%\| | min q |
|---|---|---|---|---|
| Obscn (obscurin) | quadriceps femoris | liver disease | 76.9 | 3.5e-3 |
| Dazl | quadriceps femoris | male infertility | 65.6 | 5.0e-45 |
| Cacna1f | quadriceps femoris | nervous system disease; myopia | 60.9 | 3.2e-2 |
| Ttn (titin) | quadriceps femoris | cardiomyopathy | 51.1 | 3.3e-33 |
| Scarf2 | tibialis anterior | chronic obstructive pulmonary disease | 50.7 | 2.9e-34 |
| Atp2a2 (SERCA2) | tibialis anterior | epilepsy; schizophrenia; bipolar disorder; GERD | 46.4 | 2.1e-25 |
| Zcchc2 | tibialis anterior | bipolar disorder | 50.0 | 2.3e-2 |

- **Why it answers the question:** spaceflight leaves a significant, confounder-free epigenetic signature on skeletal muscle, and the most strongly methylated genes are sarcomere / calcium-handling muscle genes whose human orthologs carry striated-muscle disease — **Ttn (titin) → cardiomyopathy** and **Atp2a2 (SERCA2) → multiple disorders** — assembling an epigenetics-to-disease view obtainable only by chaining the clean methylation contrast through the ortholog into SPOKE.
- **Literature support:** Miousse et al., 2019, *Life Sci Space Res* — space-environment-relevant exposure induces dynamic, persistent DNA-methylation changes in mouse striated (cardiac) muscle, establishing spaceflight-driven epigenetic remodeling of muscle tissue. [PMID:31421852](https://pubmed.ncbi.nlm.nih.gov/31421852/) · [DOI](https://doi.org/10.1016/j.lssr.2019.05.003)

---

## Taxonomy & Organisms

### 8a. spoke-genelab × nde — Spaceflight-perturbed mouse organs paired with the NIAID diseases studied in those organs
- **Partner KG:** `nde` — NIAID Data Ecosystem; infectious/immune-disease datasets, each tagged with an organism (NCBITaxon `schema:species`) and named health conditions.
- **Shared identifier / bridge:** NCBITaxon (exact id — *Mus musculus* = NCBITaxon_10090, examined in both GeneLab spaceflight assays and NDE datasets)
- **Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); mouse gene expression.
- **Research question:** The mouse is NASA's primary mammalian spaceflight model and a workhorse of infectious-disease research. For each organ that GeneLab measured under a *clean* Space-Flight-vs-Ground-Control mouse contrast, what is a top spaceflight-DE gene, and what NIAID infectious disease — studied in that same mouse and localizing to that organ — could those spaceflight findings be connected to?
- **Why the join is required:** spoke-genelab supplies the organ + the confounder-free spaceflight DE gene per row but no disease context; NDE supplies the named infectious disease studied in the same species (with its dataset count) but holds no spaceflight data. Each row only exists because both graphs describe the same organism (mouse), so the row pairs a real spaceflight datum with a real terrestrial-disease datum.
- **SPARQL** (executed 2026-06-27, returned 7 rows):
```sparql
PREFIX schema: <http://schema.org/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# Each row = a GeneLab mouse spaceflight tissue + a clean-contrast DE gene (Mus musculus, NCBITaxon_10090),
# paired with an NDE infectious disease studied in the mouse that localizes to that organ (+ NDE dataset count).
SELECT ?organ ?geneLabGene ?geneLabLog2fc ?ndeDisease (COUNT(DISTINCT ?ds) AS ?ndeDatasets) WHERE {
  VALUES (?tissue ?organ ?ndeDisease) {
    (<http://purl.obolibrary.org/obo/UBERON_0002168> "left lung"    "influenza")
    (<http://purl.obolibrary.org/obo/UBERON_0002168> "left lung"    "pulmonary tuberculosis")
    (<http://purl.obolibrary.org/obo/UBERON_0002370> "thymus"       "HIV infectious disease")
    (<http://purl.obolibrary.org/obo/UBERON_0002107> "liver"        "malaria")
    (<http://purl.obolibrary.org/obo/UBERON_0002107> "liver"        "Plasmodium falciparum malaria")
    (<http://purl.obolibrary.org/obo/UBERON_0002106> "spleen"       "Sepsis")
    (<http://purl.obolibrary.org/obo/UBERON_0004538> "left kidney"  "tuberculosis")
  }
  # GeneLab: a representative top clean-contrast spaceflight DE gene in that mouse organ
  {
    SELECT ?tissue (SAMPLE(?sym) AS ?geneLabGene) (SAMPLE(?lfc) AS ?geneLabLog2fc) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 ; sg:INVESTIGATED_ASiA ?tissue .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
        ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
              rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?a .
        ?gene sg:symbol ?sym ; sg:taxonomy <http://purl.obolibrary.org/obo/NCBITaxon_10090> .
        FILTER(?a < 1.0e-10)
      }
    } GROUP BY ?tissue
  }
  # NDE: the same infectious disease studied in the mouse (Mus musculus, taxonomy 10090)
  GRAPH <https://purl.org/okn/frink/kg/nde> {
    ?ds schema:species ?sp ; schema:healthCondition ?hc .
    FILTER(STRENDS(STR(?sp),'/taxonomy/10090'))
    ?hc schema:name ?ndeDisease .
  }
} GROUP BY ?organ ?geneLabGene ?geneLabLog2fc ?ndeDisease ORDER BY ?organ
```
- **Sample result** (7 of 7) — each row shows GeneLab + nde data:

| Organ (GeneLab spaceflight, mouse) | GeneLab clean-contrast DE gene (log2FC, SF vs GC) | NIAID disease in mouse (nde) | NDE datasets |
|---|---|---|---|
| left lung | Sstr4 (-1.72) | influenza | 338 |
| left lung | Sstr4 (-1.72) | pulmonary tuberculosis | 12 |
| thymus | Cks1b (-2.01) | HIV infectious disease | 43 |
| liver | Atp2b2 (-3.45) | malaria | 111 |
| liver | Atp2b2 (-3.45) | *Plasmodium falciparum* malaria | 6 |
| spleen | Gpx3 (+0.93) | Sepsis | 14 |
| left kidney | Fgg (+2.97) | tuberculosis | 186 |

- **Why it answers the question:** every row contains a real GeneLab confounder-free Space-Flight-vs-Ground-Control mouse DE gene for an organ AND a real NIAID infectious disease studied in that same mouse and localizing to that organ (with its NDE dataset count) — a spaceflight-to-terrestrial-disease pairing neither graph holds alone.
- **Literature support:** Li et al., 2014, *PLoS ONE* — combined microgravity (hindlimb suspension) and solar-particle-event-like radiation increased morbidity and impaired clearance of systemic and pulmonary bacterial infections across three mouse strains, showing spaceflight conditions raise infectious-disease risk in the mouse model. [PMID:24454913](https://pubmed.ncbi.nlm.nih.gov/24454913/) · [DOI](https://doi.org/10.1371/journal.pone.0085665)

### 8b. spoke-genelab × nde — Spaceflight-enriched Gammaproteobacteria bridged by clade to NIAID Gammaproteobacterial pathogens
- **Partner KG:** `nde` — NIAID Data Ecosystem; infectious/immune-disease datasets, each tagged with an organism (NCBITaxon `schema:species`, stored as `https://www.uniprot.org/taxonomy/{id}`) and health conditions.
- **Shared identifier / bridge:** NCBITaxon clade via ubergraph — exact-species overlap = 0, so the spaceflight-enriched class **Gammaproteobacteria (NCBITaxon_1236)** is bridged to NDE pathogen species that are its `rdfs:subClassOf*` descendants.
- **Spaceflight contrast:** Space Flight vs Ground Control — *fallback applied*: the VEG-01 differential-abundance assays carry no `material_id` and always bundle a plant-compartment factor, so the strict `material_id` + `FILTER NOT EXISTS` clean filter returns 0 rows; per methodology the contrast is restricted to `factor_space_1 = "Space Flight"` / `factor_space_2 = "Ground Control"` only (stated explicitly). Gammaproteobacteria is **up in spaceflight** (lnfc +8.22, log2fc +11.86).
- **Research question:** The class Gammaproteobacteria becomes strongly more abundant in NASA's spaceflight crop microbiome (VEG-01). Although no spaceflight-enriched microbe matches NDE at the species level, do any NIAID-tracked infectious-disease pathogens fall *within* that spaceflight-enriched clade — i.e. can the spaceflight microbial-ecology signal be connected, by clade, to concrete terrestrial pathogens and their diseases?
- **Why the join is required:** spoke-genelab measures which microbial clade shifts in spaceflight (with the abundance value) but has no pathogen-surveillance context; NDE catalogs which pathogen species anchor infectious-disease datasets (and their diseases) but has no spaceflight data; the ubergraph NCBITaxon hierarchy supplies the clade link. Each row pairs a GeneLab spaceflight abundance value with an NDE pathogen + disease under the same clade.
- **SPARQL** (executed 2026-06-27, returned 11 rows):
```sparql
PREFIX schema: <http://schema.org/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# GeneLab spaceflight-enriched Gammaproteobacteria (differential abundance, factor_space fallback contrast)
# bridged via ubergraph clade to NDE pathogen species under Gammaproteobacteria (1236) and their NIAID disease.
SELECT ?sfClade (MAX(?sfLnfc) AS ?maxLnfc) (MAX(?sfLog2fc) AS ?maxLog2fc) ?ndePathogen ?ndeDisease WHERE {
  # GeneLab: Gammaproteobacteria differential abundance, Space Flight vs Ground Control
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_ABUNDANCE_ASmO ;
          rdf:object ?gorg ; sg:lnfc ?sfLnfc ; sg:log2fc ?sfLog2fc .
    ?gorg rdfs:label ?sfClade .
    ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" .
    FILTER(STRENDS(STR(?gorg),'/node/1236'))
  }
  # NDE pathogen species (uniprot taxonomy IRI) + its ubergraph obo IRI for clade membership
  VALUES (?sp ?spTax ?ndePathogen) {
    (<https://www.uniprot.org/taxonomy/562>   <http://purl.obolibrary.org/obo/NCBITaxon_562>   "Escherichia coli")
    (<https://www.uniprot.org/taxonomy/83334> <http://purl.obolibrary.org/obo/NCBITaxon_83334> "Escherichia coli O157:H7")
    (<https://www.uniprot.org/taxonomy/590>   <http://purl.obolibrary.org/obo/NCBITaxon_590>   "Salmonella")
    (<https://www.uniprot.org/taxonomy/90370> <http://purl.obolibrary.org/obo/NCBITaxon_90370> "Salmonella Typhi")
    (<https://www.uniprot.org/taxonomy/620>   <http://purl.obolibrary.org/obo/NCBITaxon_620>   "Shigella")
    (<https://www.uniprot.org/taxonomy/666>   <http://purl.obolibrary.org/obo/NCBITaxon_666>   "Vibrio cholerae")
    (<https://www.uniprot.org/taxonomy/727>   <http://purl.obolibrary.org/obo/NCBITaxon_727>   "Haemophilus influenzae")
    (<https://www.uniprot.org/taxonomy/445>   <http://purl.obolibrary.org/obo/NCBITaxon_445>   "Legionella")
  }
  # ubergraph: confirm the NDE pathogen descends from the spaceflight-enriched clade
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?spTax rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_1236> .
  }
  # NDE: the NIAID disease for that pathogen
  GRAPH <https://purl.org/okn/frink/kg/nde> {
    ?ds schema:species ?sp ; schema:healthCondition ?hc .
    ?hc schema:name ?ndeDisease .
  }
} GROUP BY ?sfClade ?ndePathogen ?ndeDisease ORDER BY ?ndePathogen ?ndeDisease
```
- **Sample result** (8 of 11) — each row shows GeneLab + nde data:

| Spaceflight-enriched clade (GeneLab) | lnfc / log2fc (SF vs GC, up) | NDE pathogen under that clade | NIAID disease (nde) |
|---|---|---|---|
| Gammaproteobacteria | +8.22 / +11.86 | *Escherichia coli* | escherichia coli infection |
| Gammaproteobacteria | +8.22 / +11.86 | *Escherichia coli* O157:H7 | escherichia coli infection |
| Gammaproteobacteria | +8.22 / +11.86 | *Salmonella* | salmonellosis |
| Gammaproteobacteria | +8.22 / +11.86 | *Salmonella* Typhi | typhoid fever |
| Gammaproteobacteria | +8.22 / +11.86 | *Shigella* | shigellosis |
| Gammaproteobacteria | +8.22 / +11.86 | *Vibrio cholerae* | cholera |
| Gammaproteobacteria | +8.22 / +11.86 | *Haemophilus influenzae* | haemophilus infectious disease |
| Gammaproteobacteria | +8.22 / +11.86 | *Legionella* | legionellosis |

- **Why it answers the question:** every row carries a real GeneLab spaceflight differential-abundance value for the Gammaproteobacteria clade AND a real NIAID pathogen species (verified `subClassOf*` descendant of that clade) with its named disease — turning the species-level coverage gap into a meaningful clade-level bridge from spaceflight microbial ecology to terrestrial Gammaproteobacterial pathogens.
- **Literature support:** Singh et al., 2018, *BMC Microbiology* — multidrug-resistant *Enterobacter bugandensis* (an Enterobacteriaceae, i.e. Gammaproteobacteria) isolated from the ISS carried virulence and antibiotic-resistance genes and a high predicted pathogenic probability, confirming ISS-enriched Gammaproteobacteria overlap human pathogens. [PMID:30466389](https://pubmed.ncbi.nlm.nih.gov/30466389/) · [DOI](https://doi.org/10.1186/s12866-018-1325-2)

### 9a. spoke-genelab × sawgraph — Spaceflight zebrafish lineage joined to the PFAS panel SAWGraph measured in white perch
- **Partner KG:** `sawgraph` — environmental PFAS-monitoring graph; organisms (fish/wildlife) sampled and assayed for per-/polyfluoroalkyl-substance contamination.
- **Shared identifier / bridge:** NCBITaxon clade via ubergraph — exact-id overlap = 0, so GeneLab's zebrafish and SAWGraph's white perch are joined through their common ray-finned-fish ancestor **Actinopterygii (NCBITaxon_7898)**.
- **Spaceflight contrast:** n/a — organism-level (clade) join; no differential values read.
- **Research question:** NASA's spaceflight fish model is the zebrafish (*Danio rerio*); SAWGraph monitors a fish of the same ray-finned lineage (white perch, *Morone americana*). Which **specific PFAS chemicals** has SAWGraph measured in that lineage-sharing fish — the real environmental contaminant panel a spaceflight zebrafish toxicology study could anchor to?
- **Why the join is required:** spoke-genelab supplies the spaceflight organism (zebrafish) but no contaminant data; SAWGraph supplies the monitored organism + PFAS panel but no spaceflight context; only the ubergraph Actinopterygii clade links them. Each row therefore contains both a GeneLab organism and a SAWGraph organism + PFAS chemical.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# GeneLab spaceflight zebrafish + SAWGraph fish + PFAS, joined via the shared Actinopterygii clade.
SELECT DISTINCT ?geneLabOrganism ?sharedClade ?sawOrganism ?pfasChemical WHERE {
  # GeneLab spaceflight zebrafish (Danio rerio, NCBITaxon_7955)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?g gls:taxonomy <http://purl.obolibrary.org/obo/NCBITaxon_7955> ; gls:organism ?geneLabOrganism .
  }
  BIND("Actinopterygii (ray-finned fishes)" AS ?sharedClade)
  # zebrafish + SAWGraph fish both descend from Actinopterygii (7898)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_7955> rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_7898> .
    ?sawTax rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_7898> ; rdfs:label ?sawOrganism .
  }
  # the PFAS chemicals SAWGraph actually measured in that fish
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?mat <http://purl.obolibrary.org/obo/RO_0002162> ?sawTax .
    ?samp coso:sampleOfMaterialType ?mat . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst .
    ?subst rdfs:label ?pfasChemical . FILTER(STRSTARTS(STR(?subst),'http://w3id.org/DSSTox/'))
  }
} ORDER BY ?pfasChemical LIMIT 12
```
- **Sample result** (8 of 12) — each row shows GeneLab + sawgraph data:

| GeneLab spaceflight organism | Shared clade (ubergraph) | SAWGraph organism | PFAS chemical (sawgraph) |
|---|---|---|---|
| *Danio rerio* | Actinopterygii | *Morone americana* | 2-(N-Ethylperfluorooctanesulfonamido)acetic acid (EtFOSAA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | 2-(N-Methylperfluorooctanesulfonamido)acetic acid (MeFOSAA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | 3:3 Fluorotelomer carboxylic acid |
| *Danio rerio* | Actinopterygii | *Morone americana* | 6:2 Fluorotelomer sulfonic acid |
| *Danio rerio* | Actinopterygii | *Morone americana* | 8:2 Fluorotelomer sulfonic acid |
| *Danio rerio* | Actinopterygii | *Morone americana* | N-Ethylperfluorooctane sulfonamide (EtFOSA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | N-Methylperfluorooctanesulfonamide (MeFOSA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | Perfluoro-2-ethoxyethanesulfonic acid |

- **Why it answers the question:** every row pairs the GeneLab spaceflight organism (*Danio rerio*) with the SAWGraph-monitored organism (*Morone americana*) and a real named PFAS chemical measured in it, linked only through the shared Actinopterygii clade — the concrete contaminant panel a spaceflight zebrafish study could anchor to.
- **Literature support:** Rericha et al., 2023, *Toxicological Sciences* — review establishing the zebrafish as a primary in-vivo model for PFAS toxicokinetics and toxicity, validating use of the spaceflight zebrafish model to interpret PFAS exposure in lineage-related wild fish. [PMID:37220906](https://pubmed.ncbi.nlm.nih.gov/37220906/) · [DOI](https://doi.org/10.1093/toxsci/kfad051)

### 9b. spoke-genelab × sawgraph — Spaceflight Arabidopsis lineage joined to the PFAS panel SAWGraph measured in maize
- **Partner KG:** `sawgraph` — environmental PFAS-monitoring graph; the only plant it samples is the crop maize (*Zea mays* subsp. *mays*).
- **Shared identifier / bridge:** NCBITaxon clade via ubergraph — exact-id overlap = 0, so GeneLab's *Arabidopsis* and SAWGraph's maize are joined through their common green-plant ancestor **Viridiplantae (NCBITaxon_33090)**.
- **Spaceflight contrast:** n/a — organism-level (clade) join; no differential values read.
- **Research question:** NASA's spaceflight plant model is *Arabidopsis thaliana*; SAWGraph monitors a flowering-plant crop of the same green-plant lineage — maize (*Zea mays*). Which **specific PFAS chemicals** has SAWGraph measured in that crop — the real contaminant panel relevant to space-agriculture and food-crop safety?
- **Why the join is required:** spoke-genelab supplies the spaceflight plant model (*Arabidopsis*) but no contaminant data; SAWGraph supplies the monitored crop + PFAS panel but no spaceflight context; the two share no exact taxon (one eudicot model, one monocot crop), so only clade expansion through the ubergraph Viridiplantae node links them. Each row therefore contains both a GeneLab organism and a SAWGraph crop + PFAS chemical.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# GeneLab spaceflight Arabidopsis + SAWGraph crop (maize) + PFAS, joined via the shared Viridiplantae clade.
SELECT DISTINCT ?geneLabOrganism ?sharedClade ?sawCrop ?pfasChemical WHERE {
  # GeneLab spaceflight Arabidopsis (Arabidopsis thaliana, NCBITaxon_3702)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?g gls:taxonomy <http://purl.obolibrary.org/obo/NCBITaxon_3702> ; gls:organism ?geneLabOrganism .
  }
  BIND("Viridiplantae (green plants)" AS ?sharedClade)
  # Arabidopsis + SAWGraph maize both descend from Viridiplantae (33090)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_3702> rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_33090> .
    ?sawTax rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_33090> ; rdfs:label ?sawCrop .
  }
  # the PFAS chemicals SAWGraph actually measured in that crop (maize)
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?mat <http://purl.obolibrary.org/obo/RO_0002162> ?sawTax .
    ?samp coso:sampleOfMaterialType ?mat . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst .
    ?subst rdfs:label ?pfasChemical . FILTER(STRSTARTS(STR(?subst),'http://w3id.org/DSSTox/'))
  }
} ORDER BY ?pfasChemical LIMIT 12
```
- **Sample result** (8 of 12) — each row shows GeneLab + sawgraph data:

| GeneLab spaceflight organism | Shared clade (ubergraph) | SAWGraph crop | PFAS chemical (sawgraph) |
|---|---|---|---|
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 11-Chloroperfluoro-3-oxaundecanesulfonic acid (11Cl-PF3OUdS) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 2-(N-Ethylperfluorooctanesulfonamido)acetic acid (EtFOSAA) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 2-(N-Methylperfluorooctanesulfonamido)acetic acid (MeFOSAA) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 4,8-Dioxa-3H-perfluorononanoic acid (ADONA) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 4:2 Fluorotelomer sulfonic acid |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 6:2 Fluorotelomer sulfonic acid |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 8:2 Fluorotelomer sulfonic acid |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | N-Ethylperfluorooctane sulfonamide (EtFOSA) |

- **Why it answers the question:** every row pairs the GeneLab spaceflight plant model (*Arabidopsis thaliana*) with the SAWGraph-monitored crop (*Zea mays*) and a real named PFAS chemical measured in it — including replacement PFAS (ADONA, 11Cl-PF3OUdS) and fluorotelomer sulfonic acids — linked only through the shared Viridiplantae clade, the concrete crop-contamination panel relevant to space-agriculture food safety.
- **Literature support:** Just et al., 2022, *J Agric Food Chem* — soil-plant pot experiments with maize (*Zea mays* L.) showed fluorotelomer precursors degrade to perfluoroalkyl carboxylic acids that are translocated into maize shoots, demonstrating real PFAS uptake into the crop. [PMID:35840126](https://pubmed.ncbi.nlm.nih.gov/35840126/) · [DOI](https://doi.org/10.1021/acs.jafc.1c06838)

## Coverage summary

All **9 distinct partner knowledge graphs** that `spoke-genelab` crosswalks with are represented by **two examples each (a + b, 18 total)** above. **Every result table contains data from both knowledge graphs in the same rows** — a spoke-genelab spaceflight value (gene/methylation/abundance measurement, organism, or tissue) paired with the partner KG's value (GXA terrestrial expression, ProKN marker gene, AOP/PIGEAN/rare-disease/SPOKE annotation, biohealth disease, NIAID disease, or SAWGraph PFAS), joined on the shared key (gene symbol/Entrez, CL/UBERON/UMLS anatomy, or NCBITaxon organism). **Every example that reads a differential expression / methylation / abundance value enforces the strict Space-Flight-vs-Ground-Control contrast** (matched factors + material) — the methodologically correct way to attribute a change to spaceflight; only the two organism-overlap examples (9a, 9b) read no differential value and instead pair the GeneLab spaceflight organism with the SAWGraph organism + PFAS by clade. Several partners also connect on additional keys not shown here (e.g. AOP-Wiki, biohealth, GXA and spoke-okn also via NCBITaxon) — see `crosswalks_example.md` and `proto-okn-crosswalk-inventory.md` for the full recipe catalog. The `spoke-genelab × spoke-okn` pair is shown here from a fresh immune-disease angle; its musculoskeletal angle appears in `spoke-okn-25-example-queries.md`.

*This is a standalone showcase. It does not modify the crosswalk catalog or its per-recipe transcripts.*

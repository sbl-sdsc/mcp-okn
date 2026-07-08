# SPOKE-OKN ↔ SPOKE-GeneLab — 10 real-world cross-graph queries

**Standalone showcase — NOT part of the crosswalk catalog** (`crosswalks_example.md` / `crosswalks_examples/` / `proto-okn-crosswalk-inventory.md` / `metadata/crosswalks.json`).
This file presents **10 scientifically meaningful, literature-grounded, executed cross-graph queries that put `spoke-okn` and `spoke-genelab` at the center** and link them to *each other* and to the additional Proto-OKN / FRINK knowledge graphs that share crosswalks with them. Several queries span **3 or 4 KGs in a single federated query**. It is a companion to `spoke-genelab-9-example-queries.md` and `spoke-okn-25-example-queries.md`, but is organized by **translational use case** (reproduce / extend a published spaceflight-omics result), not by crosswalk partner.

- **Focus KGs:** `spoke-genelab` (NASA OSDR/GeneLab spaceflight omics — differential gene expression, DNA methylation, microbial abundance) **×** `spoke-okn` (UCSF SPOKE — genes, diseases, compounds, organisms, geography).
- **Model:** claude-opus-4-8 · **Crosswalk source:** `mcp-okn` `list_crosswalks` / `get_join_strategy` (134 verified crosswalks, verified 2026-06-30)
- **Endpoint:** FRINK federated SPARQL via the `mcp-okn` service (`https://frink.apps.renci.org/federation/sparql`)
- **All 10 queries executed on 2026-07-07**; each block shows the runnable SPARQL, a real sample of returned rows, an interpretation, and a PubMed/literature anchor (literature retrieved via PubMed; DOIs linked).

---

## ⚠️ Reproducibility: the Space-Flight-vs-Ground-Control clean contrast (applies to every query)

`spoke-genelab` models each differential **expression / methylation / abundance** result as an `Assay` comparing **two groups** (`group_mean_1` vs `group_mean_2`). **Most assays are confounded** and must not be read as a spaceflight effect: many compare Space-Flight-vs-Space-Flight or control-vs-control, compare Space Flight against Basal/Vivarium controls, or bundle a second factor (infection, dose, plant compartment, time point) that differs between the two groups.

To make every query **reproducible and confounder-free**, each one restricts `spoke-genelab` to the **clean Space-Flight-vs-Ground-Control contrast** — *the only difference between the two groups is spaceflight, on the same biological material*:

```sparql
?assay gl:factor_space_1 "Space Flight" ;     # group 1 = Space Flight
       gl:factor_space_2 "Ground Control" ;    # group 2 = Ground Control
       gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
FILTER(?m1 = ?m2)                                                                   # SAME biological material/condition
# WITHIN-ASSAY covariate matching: after stripping the condition labels/codes, the flight arm
# (factors_1) and the ground arm (factors_2) must carry the SAME covariate set. A covariate
# SHARED by both arms is allowed; a covariate present on only one arm confounds the contrast.
FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
  FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
    && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
  FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
  FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
    && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
  FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
```

Under this within-assay covariate matching, **117** gene-expression assays with matched material qualify (re-verified 2026-07-07). This is broader than the old zero-covariate filter (~50 assays) because it keeps assays where both arms **share** a covariate — a shared covariate cancels out of the flight-vs-ground contrast, so it is not a confounder. Prefer the `get_valid_contrasts` tool, which returns exactly these vetted assays flagged `is_clean_contrast`. **Direction:** group 1 = Space Flight, group 2 = Ground Control, so **`log2fc > 0` / `methylation_diff > 0` / `lnfc > 0` = up in spaceflight relative to ground control.** Every prompt below states this constraint explicitly so the query is reproducible. **Exception:** the microbiome differential-abundance assays (Q8) carry no `material_id` (VEG-01 plant studies always bundle a root/leaf compartment factor), so Q8 falls back to the `factor_space_1/2` Space-Flight-vs-Ground-Control fields alone and says so.

### The integration spine
`spoke-genelab` model-organism genes are mapped to **human orthologs** (`schema:IS_ORTHOLOG_MGiG`); the human ortholog carries the **same Entrez gene IRI** (`http://www.ncbi.nlm.nih.gov/gene/{id}`) used by `spoke-okn` (verified join **C4**, 16,326 shared genes). **Always traverse the ortholog edge before joining `spoke-okn`** — the majority of clean-contrast assays are mouse (Mus musculus = 219 gene-assay links, vs 115 human), and their mouse Entrez IDs do *not* match `spoke-okn` directly. The same human Entrez id then fans out to the other gene-keyed KGs (`rdkg`, `digcfdekg`, `biobricks-aopwiki`, `gene-expression-atlas-okn`). The microbiome axis (Q8) instead bridges `spoke-genelab` → `ubergraph` (NCBITaxon clade) → `spoke-okn` bacterial strains (verified join **D9**).

### Crosswalk axes used

| Axis | Shared key / bridge | KGs reachable from the spoke-genelab × spoke-okn core | Verified recipe |
|---|---|---|---|
| Genes | Entrez (+ `IS_ORTHOLOG_MGiG`) | `spoke-okn`, `rdkg`, `digcfdekg`, `biobricks-aopwiki` | C4, C6, C7, C11 |
| Genes (terrestrial expression) | gene symbol / Ensembl, UBERON-scoped | `gene-expression-atlas-okn` | AN1, Genes/Ensembl |
| Taxonomy (microbiome) | NCBITaxon clade via `ubergraph` | `spoke-okn` bacterial strains | D9, D10 |

---

## Index

| # | Use case | KGs (beyond the spoke-okn × spoke-genelab core) | Literature anchor |
|---|---|---|---|
| 1 | Spaceflight transcriptomic signature → systemic disease landscape | — (2 KG) | da Silveira 2020 (mitochondrial/metabolic/immune hub) |
| 2 | Muscle-atrophy genes → cardiomyopathy / muscular-disease program | — (2 KG) | Henrich 2022; Vitry 2022 |
| 3 | Candidate countermeasure compounds that reverse the muscle signature | — (2 KG) | Caicedo 2023 (OSD-52 muscle-loss treatments) |
| 4 | Spaceflight DE genes that are rare-disease / cancer-predisposition genes | + `rdkg` (3 KG) | da Silveira 2020 (DNA damage) |
| 5 | Spaceflight DE genes as Adverse-Outcome-Pathway key-event molecules | + `biobricks-aopwiki` (3 KG) | space-radiation toxicology |
| 6 | Spaceflight DE genes in CFDE-REVEAL inferred gene sets / pathways | + `digcfdekg` (3 KG) | systems-genomics re-use |
| 7 | Immune-organ (spleen) spaceflight DE genes vs terrestrial expression | + `gene-expression-atlas-okn` (3 KG) | Wu 2024 (immune dysfunction) |
| 8 | Spaceflight-enriched microbiome genera → SPOKE bacterial strains + AMR | + `ubergraph` (3 KG) | Checinska Sielaff 2019 (ISS microbiome) |
| 9 | Spaceflight differentially-**methylated** genes → disease | — (2 KG) | da Silveira 2020 (epigenome) |
| 10 | 4-KG capstone: spaceflight genes that are SPOKE + rare-disease + AOP genes | + `rdkg` + `biobricks-aopwiki` (4 KG) | da Silveira 2020 (chronic inflammation) |

---

## 1. Spaceflight transcriptomic signature → systemic disease landscape
**KGs:** `spoke-genelab` × `spoke-okn` · **Shared key:** Entrez (via `IS_ORTHOLOG_MGiG`, recipe C4)

**Prompt (reproducible):** *Using only the 117 clean Space-Flight-vs-Ground-Control GeneLab assays (factor_space_1 = "Space Flight", factor_space_2 = "Ground Control", material_id_1 = material_id_2, and each covariate matched across the flight and ground arms), take every significantly differentially expressed gene (|log2FC| ≥ 1, adj. p ≤ 0.05), map it to its human ortholog, and rank the SPOKE diseases associated with those genes. Which human disease categories does the confounder-free spaceflight transcriptome touch most?*

**Why the join is required:** GeneLab holds the spaceflight differential expression but no disease knowledge; SPOKE holds gene→disease associations but no spaceflight data. The shared Entrez id (after ortholog mapping) is the only bridge.

**SPARQL** (executed 2026-07-07, 18 rows shown):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?diseaseLabel (COUNT(DISTINCT ?human) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.05 && ABS(?lfc) >= 1.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?human a bl:Gene .
    ?disease so:ASSOCIATES_DaG ?human ; rdfs:label ?diseaseLabel .
  }
} GROUP BY ?diseaseLabel ORDER BY DESC(?nGenes) LIMIT 18
```

**Sample result** (top SPOKE diseases by # of spaceflight-DE ortholog genes):

| SPOKE disease | # spaceflight-DE genes |
|---|---|
| liver disease | 918 |
| diabetes mellitus | 512 |
| hypertension | 485 |
| cardiomyopathy | 446 |
| gastroesophageal reflux disease | 413 |
| obesity | 394 |
| coronary artery disease | 284 |
| inflammatory bowel disease | 258 |
| epilepsy / nervous system disease | 1369 / 1260 |

**Interpretation & validation:** The non-neural top hits — **liver disease, diabetes, obesity, cardiomyopathy, coronary artery disease** — recapitulate the metabolic/cardiovascular axis that the GeneLab multi-omics consortium identified as the dominant spaceflight phenotype: **mitochondrial stress, lipid-metabolism disruption and chronic inflammation**. *According to PubMed:* da Silveira et al., *Cell* 2020 — "Comprehensive Multi-omics Analysis Reveals Mitochondrial Stress as a Central Biological Hub for Spaceflight Impact," enrichment for mitochondrial processes, innate immunity, chronic inflammation and **lipid metabolism**. [PMID 33242417](https://pubmed.ncbi.nlm.nih.gov/33242417/) · [DOI](https://doi.org/10.1016/j.cell.2020.11.002). (The large neurological counts reflect SPOKE's dense epilepsy/CNS gene curation and are expected for any broad gene set.)

---

## 2. Muscle-atrophy genes → cardiomyopathy / muscular-disease gene program
**KGs:** `spoke-genelab` × `spoke-okn` · **Shared key:** Entrez (ortholog, C4)

**Prompt (reproducible):** *Restrict GeneLab to the clean Space-Flight-vs-Ground-Control contrast (same material, covariates matched across arms) **and to skeletal-muscle tissues** (material_name_1 ∈ {quadriceps femoris, gastrocnemius, soleus, tibialis anterior, extensor digitorum longus}). For the significant DE genes (|log2FC| ≥ 1, adj. p ≤ 0.05), map to human orthologs and intersect with SPOKE genes associated with muscle / muscular-dystrophy / cardiomyopathy diseases. Does spaceflight muscle atrophy engage the genetic program of inherited muscle disease?*

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?diseaseLabel (COUNT(DISTINCT ?human) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    VALUES ?mat { "quadriceps femoris" "gastrocnemius" "soleus" "tibialis anterior" "extensor digitorum longus" }
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 ; gl:material_name_1 ?mat .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.05 && ABS(?lfc) >= 1.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?human a bl:Gene .
    ?disease so:ASSOCIATES_DaG ?human ; rdfs:label ?diseaseLabel .
    FILTER(CONTAINS(LCASE(?diseaseLabel),"muscle") || CONTAINS(LCASE(?diseaseLabel),"muscular")
        || CONTAINS(LCASE(?diseaseLabel),"myopathy") || CONTAINS(LCASE(?diseaseLabel),"cardiomyopathy")
        || CONTAINS(LCASE(?diseaseLabel),"atrophy"))
  }
} GROUP BY ?diseaseLabel ORDER BY DESC(?nGenes) LIMIT 12
```

**Sample result:** **cardiomyopathy → 76 spaceflight muscle-DE ortholog genes**, including the sarcomeric/contractile core **Myh6, Myl2, Myl3, Tnnc1, Tpm1, Tpm3, Pln, Csrp3, Ankrd1, Flnc, Lmod2, Nexn, Trdn, Kcnj2, Dsp**.

**Interpretation & validation:** Clean spaceflight muscle contrasts converge on the **sarcomere and excitation-contraction machinery** that defines inherited cardiomyopathy/myopathy — i.e., disuse-like atrophy in microgravity perturbs the same contractile genes. *According to PubMed:* Henrich et al., *Skeletal Muscle* 2022 — prolonged spaceflight remodels the skeletal-muscle transcriptome (DGE + alternative splicing) in atrophy- and fiber-type genes [PMID 35642060](https://pubmed.ncbi.nlm.nih.gov/35642060/) · [DOI](https://doi.org/10.1186/s13395-022-00294-9); Vitry et al., *iScience* 2022 — muscle-atrophy gene expression in spaceflight (RR-1) [PMID 36267920](https://pubmed.ncbi.nlm.nih.gov/36267920/) · [DOI](https://doi.org/10.1016/j.isci.2022.105213).

---

## 3. Candidate countermeasure compounds that reverse the spaceflight muscle signature
**KGs:** `spoke-genelab` × `spoke-okn` · **Shared key:** Entrez (ortholog, C4) · **SPOKE edge:** `DOWNREGULATES_CdG`

**Prompt (reproducible):** *From the clean Space-Flight-vs-Ground-Control **skeletal-muscle** contrast (same material, covariates matched across arms), take the genes **up-regulated** in spaceflight (log2FC ≥ 1, adj. p ≤ 0.05), map to human orthologs, and ask SPOKE which compounds **down-regulate** those same genes — i.e., signature-reversal countermeasure candidates for muscle atrophy. Rank compounds by the number of spaceflight-up genes they would push back down.*

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?drug (COUNT(DISTINCT ?human) AS ?nUpGenesReversed)
       (GROUP_CONCAT(DISTINCT ?sym; separator=", ") AS ?genes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    VALUES ?mat { "quadriceps femoris" "gastrocnemius" "soleus" "tibialis anterior" "extensor digitorum longus" }
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 ; gl:material_name_1 ?mat .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.05 && ?lfc >= 1.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human ; gl:symbol ?sym .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?cmp so:DOWNREGULATES_CdG ?human ; rdfs:label ?drug . }
} GROUP BY ?drug ORDER BY DESC(?nUpGenesReversed) LIMIT 10
```

**Sample result:**

| Compound (SPOKE) | # spaceflight-up genes it down-regulates | notable reversed genes |
|---|---|---|
| Fluorouracil | 49 | Sesn1, Eif4ebp1 (4E-BP1), Serpine1, Igfbp3, Spp1, Hspb1, Ccnd1, Myc, Cdk1, Top2a |
| Pentobarbital | 40 | Ddit4, Eif4ebp1, Fos, Pparg, Elovl6, Smad3, Igf2bp2 |
| Hexachlorophene | 32 | Gadd45b, Serpine1, Elovl6, Smad3, Cdk1, Cdc20 |

**Interpretation & validation:** The reversed genes include canonical **atrophy / mTOR-stress effectors** — **Ddit4 (REDD1), Eif4ebp1 (4E-BP1), Trib3, Sesn1, Gadd45b, Foxo targets** — exactly the program a muscle-loss countermeasure should oppose. These are **connectivity-map-style signature-reversal hypotheses** from SPOKE's compound→gene regulatory edges (CMap/LINCS), *not* validated drugs (several are tox-screen chemicals); the value is the ranked, mechanism-anchored candidate list. This reproduces the workflow of *According to PubMed:* Caicedo et al., 2023, "Key Genes, Altered Pathways and Potential Treatments for Muscle Loss in Astronauts and Sarcopenic Patients" (GeneLab OSD-52) [DOI](https://doi.org/10.21203/rs.3.rs-2819258/v1).

---

## 4. Spaceflight DE genes that are rare-disease / cancer-predisposition genes
**KGs:** `spoke-genelab` × `spoke-okn` × **`rdkg`** (3 KG) · **Shared key:** Entrez (ortholog → `http://identifiers.org/ncbigene/{id}`, recipe C6)

**Prompt (reproducible):** *From the 117 clean Space-Flight-vs-Ground-Control assays (same material, covariates matched across arms), take the strongly DE genes (|log2FC| ≥ 2, adj. p ≤ 0.01), map to human orthologs, require the gene to be a SPOKE gene, then look it up in the Rare Disease KG (`rdkg`, `biolink:related_to` → MONDO). Which rare diseases are most enriched among confounder-free spaceflight-responsive genes?*

**Why 3 KGs:** `spoke-genelab` supplies the spaceflight effect, `spoke-okn` confirms the human gene, and `rdkg` adds the curated rare-disease/genome-instability layer that neither of the others holds.

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?rareDisease (COUNT(DISTINCT ?human) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.01 && ABS(?lfc) >= 2.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?human a bl:Gene . }
  BIND(IRI(CONCAT('http://identifiers.org/ncbigene/', REPLACE(STR(?human),'^.*/gene/',''))) AS ?rg)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?rg bl:related_to ?dis . ?dis rdfs:label ?rareDisease . }
} GROUP BY ?rareDisease ORDER BY DESC(?nGenes) LIMIT 15
```

**Sample result:** **hereditary breast-ovarian cancer syndrome (293)**, hereditary breast carcinoma (275), breast cancer (272), colorectal cancer (271), **hepatocellular carcinoma / liver cancer (267)**, adenocarcinoma of liver & intrahepatic biliary tract (245), fibrolamellar HCC (241) — with schizophrenia (289) also near the top.

**Interpretation & validation:** The top rare diseases are **DNA-repair / genome-instability cancer-predisposition syndromes** (HBOC, hereditary breast and liver/colorectal cancers). This matches the GeneLab consortium's finding that spaceflight produces **DNA damage** alongside mitochondrial stress, and the recurring **liver-injury** phenotype in flown rodents. (Schizophrenia's high count reflects `rdkg`'s dense neuropsychiatric gene curation and is expected for any broad gene set, as in Q1.) *According to PubMed:* da Silveira et al., *Cell* 2020 — evidence of DNA damage as a consistent spaceflight phenotype [DOI](https://doi.org/10.1016/j.cell.2020.11.002); Beheshti et al., *Sci Rep* 2019 — multi-mission liver lipotoxicity/injury in flown mice [PMID 31844325](https://pubmed.ncbi.nlm.nih.gov/31844325/) · [DOI](https://doi.org/10.1038/s41598-019-55869-2).

---

## 5. Spaceflight DE genes as Adverse-Outcome-Pathway key-event molecules
**KGs:** `spoke-genelab` × `spoke-okn` × **`biobricks-aopwiki`** (3 KG) · **Shared key:** Entrez (ortholog ↔ AOP-Wiki `skos:exactMatch` → `https://identifiers.org/ncbigene/{id}`, recipe C7)

**Prompt (reproducible):** *From the clean Space-Flight-vs-Ground-Control contrast (same material, covariates matched across arms; |log2FC| ≥ 2, adj. p ≤ 0.01), map DE genes to human orthologs, keep those that are SPOKE disease genes, and count how many **AOP-Wiki Key Events** each gene is a molecular component of. Which confounder-free spaceflight genes are the busiest nodes in adverse-outcome pathways (the toxicology framework relevant to space-radiation risk)?*

**SPARQL** (executed 2026-07-07; AOP-Wiki gene objects are `https://identifiers.org/hgnc/{SYMBOL}` carrying a `skos:exactMatch` to the NCBI gene; Key Events reference them via `edamontology:data_1025`):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym (COUNT(DISTINCT ?ke) AS ?nAOP_KeyEvents) (SAMPLE(?spokeDisease) AS ?exampleDisease) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.01 && ABS(?lfc) >= 2.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human ; gl:symbol ?sym .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?dz so:ASSOCIATES_DaG ?human ; rdfs:label ?spokeDisease . }
  BIND(REPLACE(STR(?human),'^.*/gene/','') AS ?eid)
  BIND(IRI(CONCAT('https://identifiers.org/ncbigene/',?eid)) AS ?nbg)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ag skos:exactMatch ?nbg . ?ke ?kp ?ag . ?ke a <http://aopkb.org/aop_ontology#KeyEvent> .
  }
} GROUP BY ?sym ORDER BY DESC(?nAOP_KeyEvents) LIMIT 12
```

**Sample result:** **IL6 / Il6** (18 Key Events), the *Drosophila* ortholog **ple** (18), **CG31693 / CG13801 / CG11262** (15 each), **Alb** (12), **AR** (11), **Slc22a3** (9) — each also a SPOKE disease gene.

**Interpretation & validation:** The busiest AOP node is **IL6**, the central inflammatory-cytokine hub — it alone touches 18 Key Events and connects the spaceflight transcriptome to **mechanistic toxicology pathways**, the framework used to reason about ionizing-space-radiation health risk. The remaining top nodes are largely **model-organism orthologs** (the *Drosophila* pale/`ple` and CG-series genes, mouse albumin `Alb`) plus the androgen receptor **AR** — reflecting that the within-assay-matched contrast now spans fly and mouse studies alongside the classic mouse muscle/liver work. The IL6-centred inflammation signal echoes the chronic-inflammation / cell-cycle / apoptosis enrichment reported by *According to PubMed:* da Silveira et al., *Cell* 2020 [DOI](https://doi.org/10.1016/j.cell.2020.11.002). The join lets a space-radiation risk analyst pivot from a GeneLab DE gene straight into curated AOP key events.

---

## 6. Spaceflight DE genes in CFDE-REVEAL inferred gene sets / pathways
**KGs:** `spoke-genelab` × `spoke-okn` × **`digcfdekg`** (3 KG) · **Shared key:** Entrez (ortholog, identical IRI form, recipe C11)

**Prompt (reproducible):** *From the clean Space-Flight-vs-Ground-Control contrast (same material, covariates matched across arms; |log2FC| ≥ 2, adj. p ≤ 0.01), map DE genes to human orthologs that are SPOKE genes, then pull the **CFDE-REVEAL** statistically-inferred gene sets / pathway signatures each gene belongs to (`digcfdekg:geneInGeneSet`). Which inferred functional gene sets (drug-perturbation and pathway signatures) are the spaceflight genes embedded in?*

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?geneSet (COUNT(DISTINCT ?sym) AS ?nSpaceflightGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.01 && ABS(?lfc) >= 2.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human ; gl:symbol ?sym .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?human a bl:Gene . }
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?human dig:geneInGeneSet ?gs . ?gs rdfs:label ?geneSet . }
} GROUP BY ?geneSet ORDER BY DESC(?nSpaceflightGenes) LIMIT 15
```

**Sample (top gene sets by # spaceflight genes):** the confounder-free spaceflight genes are most densely embedded in broad **metabolic / homeostatic** sets (`GOBP_SMALL_MOLECULE_METABOLIC_PROCESS` 815, `GOBP_HOMEOSTATIC_PROCESS` 784, `GOBP_REGULATION_OF_TRANSPORT` 681, `GOBP_TRANSMEMBRANE_TRANSPORT` 628), **MAPK / stress-signalling** sets (`YOSHIMURA_MAPK8_TARGETS_UP` 688, `TGGAAA_NFAT_Q4_01` 663), **cancer signatures** (`LIU_OVARIAN_CANCER_TUMORS_AND_XENOGRAFTS_XDGS_DN` 872, `DODD_NASOPHARYNGEAL_CARCINOMA_UP` 819) and **mouse-phenotype** sets (`mp_decreased_body_weight` 767, `mp_premature_death` 644) — the CFDE-REVEAL vocabulary mixes MSigDB pathway/motif sets, drug-perturbation signatures and IMPC phenotype sets.

**Interpretation & validation:** `digcfdekg` (the CFDE REVEAL statistically-inferred genomic-evidence graph) lets the confounder-free spaceflight gene list be projected onto **independently-derived, cross-Common-Fund gene sets and drug-perturbation signatures**, providing orthogonal functional context (and signature-reversal leads) for the same Entrez genes SPOKE and GeneLab share. This is the federated, KG-native analogue of the systems-biology / SPOKE re-use described by *According to PubMed:* Morris et al., *Bioinformatics* 2023 (SPOKE) [DOI](https://doi.org/10.1093/bioinformatics/btad080).

---

## 7. Immune-organ (spleen) spaceflight DE genes vs terrestrial expression atlases
**KGs:** `spoke-genelab` × `spoke-okn` × **`gene-expression-atlas-okn`** (3 KG) · **Shared keys:** gene **symbol** + UBERON tissue (`INVESTIGATED_ASiA`, recipe AN1) and Entrez ortholog (C4)

**Prompt (reproducible):** *Restrict GeneLab to the clean Space-Flight-vs-Ground-Control contrast (same material, covariates matched across arms) on the **spleen** (`INVESTIGATED_ASiA UBERON_0002106`). For each strongly DE gene (adj. p < 1e-3), report its EBI Expression Atlas (`gene-expression-atlas-okn`) terrestrial differential-expression value **in a named immune contrast**, and its SPOKE disease association. How do spaceflight spleen genes behave in Earth-based immune/inflammatory perturbation models?*

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?symbol ?glLog2fc ?gxaContrast ?gxaLog2fc ?disease WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 ;
           gl:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0002106> .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?glLog2fc ; gl:adj_p_value ?p .
    FILTER(?p < 1.0e-3)
    ?mgene gl:symbol ?symbol ; gl:IS_ORTHOLOG_MGiG ?human .
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?g bl:symbol ?symbol . ?as bl:object ?g ; bl:subject ?a ; wobd:log2fc ?gxaLog2fc .
    ?a bl:has_attribute <http://purl.obolibrary.org/obo/UBERON_0002106> ; bl:name ?gxaContrast .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?d so:ASSOCIATES_DaG ?human ; rdfs:label ?disease . }
} LIMIT 12
```

**Sample result:**

| Gene | GeneLab log2FC (SF vs GC, spleen) | GXA terrestrial contrast (spleen) | GXA log2FC | SPOKE disease |
|---|---|---|---|---|
| Samd11 | +3.62 (up) | Nix knock-out vs wild type | +1.9 | nervous system disease |
| Cstdc4 | −2.56 (down) | Zfp36⁻/⁻;TNFR1⁻/⁻;TNFR2⁻/⁻ triple-KO vs WT | +3.4 | dermatitis / acne |
| Cstdc4 | −2.56 (down) | ABIN1[D485N] knock-in vs WT (neutrophil) | −1.6 | dermatitis / acne |

**Interpretation & validation:** Spaceflight-perturbed spleen genes line up with **terrestrial TNF/inflammation knockout models** (TNFR triple-KO, ABIN1 autoinflammation), pairing the spaceflight value with a *named* Earth contrast and a SPOKE disease — the three-graph join makes the terrestrial number interpretable. This supports the **immune-dysfunction** signature of spaceflight. *According to PubMed:* Wu et al., *Nat Commun* 2024 — single-cell analysis of conserved immune dysfunction in simulated microgravity and spaceflight (GeneLab OSD-420) [DOI](https://doi.org/10.1038/s41467-023-42013-y).

---

## 8. Spaceflight-enriched microbiome genera → SPOKE bacterial strains + antimicrobial resistance
**KGs:** `spoke-genelab` × **`ubergraph`** × `spoke-okn` (3 KG) · **Shared key:** NCBITaxon clade via `ubergraph` `subClassOf*` (verified join D9)

**Prompt (reproducible):** *In the GeneLab microbial differential-abundance assays, keep the Space-Flight-vs-Ground-Control comparisons (`factor_space_1 = "Space Flight"`, `factor_space_2 = "Ground Control"`; these VEG-01 plant assays carry no `material_id`, so the contrast is defined by `factor_space` only — stated for reproducibility) with q ≤ 0.05, and rank genera/families by mean log-fold enrichment in flight. Then, for an enriched genus, expand its NCBITaxon clade through `ubergraph` and pull the SPOKE bacterial strains nested under it (with antimicrobial-resistance metadata). Which spaceflight-enriched microbes does SPOKE already profile at strain level?*

**SPARQL — part A** (enriched genera; executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?taxid ?taxLabel (COUNT(*) AS ?nObs) (AVG(?lnfc) AS ?avgLnFC) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_ABUNDANCE_ASmO ;
          rdf:object ?org ; gl:q_value ?q ; gl:lnfc ?lnfc .
    ?assay gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" .
    FILTER(?q <= 0.05)
    BIND(REPLACE(STR(?org),'^.*/node/([0-9]+).*$','$1') AS ?taxid)
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',?taxid)) AS ?taxon)
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon rdfs:label ?taxLabel . }
} GROUP BY ?taxid ?taxLabel ORDER BY DESC(?avgLnFC) LIMIT 15
```
Top flight-enriched: **Chitinophagaceae (+8.8), Xanthobacteraceae (+8.5), Ralstonia (+7.9), Mesorhizobium (+7.8), Bradyrhizobium (+7.7), Acinetobacter (+7.4), Gammaproteobacteria (+6.1), Comamonadaceae (+5.9), Cupriavidus (+5.8)**.

**SPARQL — part B** (SPOKE strains under an enriched genus, e.g. *Ralstonia* = NCBITaxon_48736; executed 2026-07-07):
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?strainLabel ?amr WHERE {
  { SELECT DISTINCT ?desc ?strainLabel ?amr WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?strain a <https://w3id.org/biolink/vocab/OrganismTaxon> ; rdfs:label ?strainLabel .
        OPTIONAL { ?strain so:antimicrobial_resistance ?amr }
        BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',
              REPLACE(STR(?strain),'^.*/organism/([0-9]+).*$','$1'))) AS ?desc)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?desc rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_48736> . }
} LIMIT 12
```
Returns the SPOKE **Ralstonia mannitolilytica** strains (SN82F48, NCTC12379, WCHRM065694, AU11682, …) nested under the spaceflight-enriched genus.

**Interpretation & validation:** The flight-enriched taxa (**Acinetobacter, Ralstonia, Cupriavidus, Methylobacterium/Methylorubrum, Sphingomonadaceae**) are classic **built-environment / ISS opportunists** — the same Proteobacteria-dominated groups catalogued on ISS surfaces, several of them opportunistic pathogens. Bridging the genus to SPOKE's genome-level strain records (with AMR/`RESPONDS_TO_OrC` drug-response data) turns a spaceflight abundance shift into actionable strain-level risk. *According to PubMed:* Checinska Sielaff et al., *Microbiome* 2019 — ISS surface bacterial/fungal communities dominated by Proteobacteria, Actinobacteria, Firmicutes including opportunistic pathogens [PMID 30955503](https://pubmed.ncbi.nlm.nih.gov/30955503/) · [DOI](https://doi.org/10.1186/s40168-019-0666-x).

---

## 9. Spaceflight differentially-**methylated** genes → disease
**KGs:** `spoke-genelab` × `spoke-okn` (2 KG) · **Shared key:** Entrez (methylation region → gene → ortholog, C4) · **Epigenome axis**

**Prompt (reproducible):** *Restrict GeneLab to the clean Space-Flight-vs-Ground-Control **DNA-methylation** assays (`measurement = "DNA methylation profiling"`, same material, covariates matched across arms). Keep differentially-methylated 1 kb regions (|methylation_diff| ≥ 25 %, q ≤ 0.05), map each region to its gene (`METHYLATED_IN_MGmMR`) and then to the human ortholog, and rank the SPOKE diseases of the differentially-methylated genes. Does the spaceflight epigenome point at the same disease axes as the transcriptome (Q1)?*

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?diseaseLabel (COUNT(DISTINCT ?human) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:measurement "DNA methylation profiling" ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_METHYLATION_ASmMR ;
          rdf:object ?region ; gl:methylation_diff ?md ; gl:q_value ?q .
    FILTER(?q <= 0.05 && ABS(?md) >= 25)
    ?mgene gl:METHYLATED_IN_MGmMR ?region ; gl:IS_ORTHOLOG_MGiG ?human .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?human a bl:Gene .
    ?disease so:ASSOCIATES_DaG ?human ; rdfs:label ?diseaseLabel .
  }
} GROUP BY ?diseaseLabel ORDER BY DESC(?nGenes) LIMIT 12
```

**Sample result:** epilepsy (28), nervous system disease (24), **liver disease (15)**, **diabetes mellitus (12)**, myopia (11), hypertension (11), depressive disorder (10), COPD (9), obesity (8), **male infertility (7)**, glaucoma (7).

**Interpretation & validation:** The spaceflight **methylome** independently re-surfaces the **liver / metabolic** axis seen in the transcriptome (Q1), plus reproductive (male infertility) and neuro-ocular signals — consistent with epigenetic regulation being part of the spaceflight response. *According to PubMed:* da Silveira et al., *Cell* 2020 included **epigenetic (methylation) responses** among the multi-omic spaceflight signatures and confirmed findings in the NASA Twin Study [DOI](https://doi.org/10.1016/j.cell.2020.11.002). (Methylation regions are 1 kb genomic intervals with no cross-KG identifier, so they reach the federation only through their `Gene` (Entrez) — this query *is* that bridge.)

---

## 10. Capstone (4 KG): spaceflight genes that are SPOKE disease + rare-disease + AOP genes
**KGs:** `spoke-genelab` × `spoke-okn` × **`rdkg`** × **`biobricks-aopwiki`** (4 KG) · **Shared key:** one human Entrez id, three independent annotations

**Prompt (reproducible):** *From the 117 clean Space-Flight-vs-Ground-Control assays (same material, covariates matched across arms; |log2FC| ≥ 2, adj. p ≤ 0.01), find the human-ortholog genes that are **simultaneously** (a) SPOKE disease genes, (b) Rare-Disease-KG genes, and (c) AOP-Wiki Key-Event molecules. Rank these high-confidence, multiply-annotated translational targets by how many AOP key events, SPOKE diseases and rare diseases each carries.*

**Why 4 KGs:** the single shared Entrez id lets four independently-built graphs vote on the same spaceflight gene — the intersection is far more selective and translationally credible than any one KG alone.

**SPARQL** (executed 2026-07-07):
```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym (COUNT(DISTINCT ?ke) AS ?nAOP_KEs)
            (COUNT(DISTINCT ?spokeDisease) AS ?nSpokeDiseases)
            (COUNT(DISTINCT ?rareDisease) AS ?nRareDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay a <http://purl.obolibrary.org/obo/OBI_0000070> ;
           gl:factor_space_1 "Space Flight" ; gl:factor_space_2 "Ground Control" ;
           gl:material_id_1 ?m1 ; gl:material_id_2 ?m2 .
    FILTER(?m1 = ?m2)
    FILTER NOT EXISTS { ?assay gl:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay gl:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay gl:factors_1 ?y } }
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?mgene ; gl:log2fc ?lfc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.01 && ABS(?lfc) >= 2.0)
    ?mgene gl:IS_ORTHOLOG_MGiG ?human ; gl:symbol ?sym .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?dz so:ASSOCIATES_DaG ?human ; rdfs:label ?spokeDisease . }
  BIND(REPLACE(STR(?human),'^.*/gene/','') AS ?eid)
  BIND(IRI(CONCAT('http://identifiers.org/ncbigene/',?eid)) AS ?rg)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?rg bl:related_to ?rd . ?rd rdfs:label ?rareDisease . }
  BIND(IRI(CONCAT('https://identifiers.org/ncbigene/',?eid)) AS ?nbg)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ag skos:exactMatch ?nbg . ?ke ?kp ?ag . ?ke a <http://aopkb.org/aop_ontology#KeyEvent> . }
} GROUP BY ?sym ORDER BY DESC(?nAOP_KEs) LIMIT 15
```

**Sample result:**

| Gene | # AOP Key Events | # SPOKE diseases | # rare diseases |
|---|---|---|---|
| IL6 | 18 | 54 | 208 |
| ple | 18 | 4 | 44 |
| CG31693 | 15 | 10 | 7 |
| Alb | 12 | 33 | 71 |
| AR | 11 | 10 | 59 |
| SLC22A | 9 | 3 | 12 |
| CG7333 | 9 | 3 | 12 |

**Interpretation & validation:** The 4-graph intersection elevates a short list of **multiply-validated spaceflight targets** dominated by the **inflammation hub IL6** — the single strongest multiply-annotated gene, carrying 54 SPOKE diseases, 208 rare diseases and 18 AOP key events — plus the endocrine androgen receptor **AR** and mouse albumin **Alb**. The remaining hits are **model-organism orthologs** (the *Drosophila* pale/`ple` and CG-series genes) that the broader within-assay-matched contrast now admits. IL6 remains the **chronic-inflammation** core the GeneLab consortium named as a central spaceflight response, here cross-referenced to rare-disease genetics and adverse-outcome pathways in a single federated query. *According to PubMed:* da Silveira et al., *Cell* 2020 [DOI](https://doi.org/10.1016/j.cell.2020.11.002).

---

## Literature references (retrieved via PubMed)

1. da Silveira WA, et al. *Comprehensive Multi-omics Analysis Reveals Mitochondrial Stress as a Central Biological Hub for Spaceflight Impact.* Cell, 2020. [PMID 33242417](https://pubmed.ncbi.nlm.nih.gov/33242417/) · [DOI](https://doi.org/10.1016/j.cell.2020.11.002) — Q1, Q4, Q5, Q9, Q10
2. Beheshti A, et al. *Multi-omics analysis of multiple missions to space reveal a theme of lipid dysregulation in mouse liver.* Sci Rep, 2019. [PMID 31844325](https://pubmed.ncbi.nlm.nih.gov/31844325/) · [DOI](https://doi.org/10.1038/s41598-019-55869-2) — Q1, Q4
3. Vitry G, et al. *Muscle atrophy phenotype gene expression during spaceflight is linked to a metabolic crosstalk in both the liver and the muscle in mice.* iScience, 2022. [PMID 36267920](https://pubmed.ncbi.nlm.nih.gov/36267920/) · [DOI](https://doi.org/10.1016/j.isci.2022.105213) — Q2, Q3
4. Henrich M, et al. *Alternative splicing diversifies the skeletal muscle transcriptome during prolonged spaceflight.* Skelet Muscle, 2022. [PMID 35642060](https://pubmed.ncbi.nlm.nih.gov/35642060/) · [DOI](https://doi.org/10.1186/s13395-022-00294-9) — Q2
5. Caicedo A, et al. *Key Genes, Altered Pathways and Potential Treatments for Muscle Loss in Astronauts and Sarcopenic Patients* (GeneLab OSD-52). Research Square, 2023. [DOI](https://doi.org/10.21203/rs.3.rs-2819258/v1) — Q3
6. Wu F, et al. *Single-cell analysis identifies conserved features of immune dysfunction in simulated microgravity and spaceflight* (GeneLab OSD-420). Nat Commun, 2024. [DOI](https://doi.org/10.1038/s41467-023-42013-y) — Q7
7. Checinska Sielaff A, et al. *Characterization of the total and viable bacterial and fungal communities associated with the International Space Station surfaces.* Microbiome, 2019. [PMID 30955503](https://pubmed.ncbi.nlm.nih.gov/30955503/) · [DOI](https://doi.org/10.1186/s40168-019-0666-x) — Q8
8. Morris JH, et al. *The scalable precision medicine open knowledge engine (SPOKE).* Bioinformatics, 2023. [PMID 36759942](https://pubmed.ncbi.nlm.nih.gov/36759942/) · [DOI](https://doi.org/10.1093/bioinformatics/btad080) — SPOKE background (Q6)
9. Casaletto JA, et al. *Analyzing the relationship between gene expression and phenotype in space-flown mice using a causal inference machine learning ensemble.* Sci Rep, 2025. [PMID 39824847](https://pubmed.ncbi.nlm.nih.gov/39824847/) · [DOI](https://doi.org/10.1038/s41598-024-81394-y) — Q3 (liver-phenotype gene workflow)
10. Finch RH, et al. *Spaceflight causes strain-dependent gene expression changes in the kidneys of mice* (GeneLab OSD-102, OSD-163). npj Microgravity, 2025. [DOI](https://doi.org/10.1038/s41526-025-00465-0) — tissue-specific extension of Q1/Q7

*Source data: NASA OSDR/GeneLab publications archive (https://science.nasa.gov/reference/osdr-publications-archive/) and PubMed. Knowledge graphs and verified crosswalk recipes via the `mcp-okn` FRINK federation service.*


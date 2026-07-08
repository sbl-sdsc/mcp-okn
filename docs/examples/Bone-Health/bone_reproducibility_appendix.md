# Reproducibility Appendix — Bone Health Spaceflight-Omics Study

- **Date:** 2026-07-08 · **Model:** claude-opus-4-8
- **Endpoint:** OKN federated SPARQL (`https://apps.okn.us/federation/sparql`)
- **KG versions (pinned via `get_kg_version`):** spoke-genelab **v0.0.2** (2026-03-13) · spoke-okn **v0.0.6** (2026-03-16) · rdkg **v0.0.1** (2026-05-04) · digcfdekg **v0.0.1** (2026-06-21) · prokn **v0.0.5** (2026-06-23) · biobricks-aopwiki **v0.0.4** (2026-03-18) · gene-expression-atlas-okn **v0.0.3** (2026-03-18) · biohealth **v0.0.4** (2026-03-16) · ubergraph **v0.0.2** (2026-05-01)

All 35 substantive SPARQL queries (verbatim, with graphs hit and row counts; merged across log scopes) are in **`bone_reproducibility_transcript.md`** (from `create_chat_transcript` / the `mcp-okn` query log). This appendix records the rules, thresholds, joins, and downstream computation so the pipeline is re-runnable end-to-end.

## Rules, thresholds and joins

- **Direction rule (spoke-genelab).** Keep an assay only when `factor_space_1 = "Space Flight"` AND `factor_space_2 = "Ground Control"` (group 1 = spaceflight ⇒ `log2FC > 0` = up in flight). Reverse / Basal / Vivarium / SF-vs-SF dropped.
- **Comparability rule.** Arms must match on every covariate after stripping condition labels/group codes. Verified with `get_valid_contrasts(kg="spoke-genelab", tissue=…)`, which flags each assay `is_clean_contrast`. For OSD-690 bone marrow this yields exactly **two clean contrasts** — Wild-Type (SF vs GC) and Nrf2-KO (SF vs GC), each genotype-internal (not WT-vs-KO).
- **Cohort (rebuilt live).** Bone tissues in spoke-genelab v0.0.2 = **bone marrow** (UBERON:0002371) and **cortical bone** (UBERON:0001439) only. In-flight bone data = OSD-690 bone marrow (WT + Nrf2-KO). Ground disuse = OSD-467 cortical bone (Hindlimb Unloaded vs Normal Loading) and OSD-214 bone marrow (HLU ± CpG/tetanus immunization). No femur/tibia/vertebra/calvaria; no human bone data.
- **Assay IRIs.** WT flight = `OSD-690-f82a89dc82f2903149d2d11cbd6a130d`; Nrf2-KO flight = `OSD-690-d89cbb20c4b7855f3f955e4adbb6515d`; cortical-bone HLU (Unloaded vs Loaded) = `OSD-467-4d3703d7504fd48caceedadb36799194`; marrow HLU no-injection = `OSD-214-0092f94d01682ca951bc130ab667111a`.
- **Thresholds.** Significance `adj_p_value ≤ 0.05` (primary); effect-size cut `|log2FC| ≥ 1` reported alongside; `|log2FC| ≥ 10` flagged as near-zero-count artefact (e.g. the OSD-214 UGT1A hits at |log2FC| > 18).
- **Ortholog collapsing.** mouse→human via `IS_ORTHOLOG_MGiG`; keep max |log2FC| for 1:many / many:1 with an ambiguity flag (`n_mouse_map`); mean-rule carried as sensitivity.
- **Cross-KG joins (Entrez only; OSD accessions are a federation island).** spoke-okn / digcfdekg on `http://www.ncbi.nlm.nih.gov/gene/{entrez}` (direct, verified 16,326 / 19,747 shared with spoke-genelab); rdkg on `http://identifiers.org/ncbigene/{entrez}` (direct, 9,034). prokn's Entrez→HGNC gene-symbol bridge is lower-confidence and is used **only** for the GO biological-process enrichment (see below), flagged accordingly.

## Key verified quantities

| Quantity | Value |
|---|---|
| OSD-690 WT flight signature (adj p≤0.05) | 3,161 mouse genes → 3,112 human orthologs (221 mouse at \|log2FC\|≥1) |
| OSD-690 Nrf2-KO flight signature | 3,517 mouse genes → 3,537 human orthologs (297 at \|log2FC\|≥1) |
| WT ∩ Nrf2-KO significant (human) | 1,754 genes; 1,726 same-direction (98.4 %) |
| Cortical-bone HLU (OSD-467) | 8 measured genes total (5 at \|log2FC\|≥1); no flight concordance |
| Non-marrow SF-vs-GC comparator | 311 assays across 33 tissues |
| Tissue specificity (221 high-effect) | 210 systemic · 41 intermediate · 5 marrow-selective |
| digcfdekg bone-loss universe | 3,412 Entrez genes (BMD 2,605 · osteoporosis 747 · fracture 1,197 · OI 37); background 21,052 |
| rdkg curated Mendelian bone-loss | 148 genes (Osteoporosis 111 · Osteopenia 141 · Reduced-BMD 8 · fractures) |
| Enrichment — digcfdekg GWAS | 492 observed vs 489.6 expected → 1.00×, hypergeometric p = 0.46 (null) |
| Enrichment — rdkg Mendelian | 31 observed vs 21.2 expected → 1.46×, hypergeometric p = 0.018 |

## Nrf2-dependent bone-remodeling set (KO-only significant)

COL1A1 (−1.35, p=0.050, trend), MMP9 (−0.67, p=0.038), NFATC1 (−0.60, p=0.028), LRP5 (−0.51, p=0.046), CSF1 (−0.38, p=0.048); LRP4 (−0.33, p=0.082, trend). Shared/Nrf2-independent (both arms): ALPL, IBSP, CA2, CXCL2, metallothioneins.

## Downstream computation (Python / pandas / scipy)

Signature loading and ortholog collapsing (`analyze1.py`), cross-genotype merge and robust-core (`analyze1.py`), tissue-specificity recurrence (`annotate.py` + non-marrow recurrence query), bone-loss annotation and hypergeometric enrichment against a **numeric-Entrez-only** digcfdekg background of 21,052 (`annotate.py`, re-verified after removing 658 non-Entrez node IRIs), integrated priority score and tiering (`rank.py`), summary stats (`stats.py`), figures (`build_figs.py`, `fig1.py`, `fig2.py`, `fig3.py`). Intermediate extracts are in `./data/*.json` / `*.tsv`; the ranked table is `RANKED_bone_candidates.tsv` and `bone_spaceflight_candidates.xlsx`.

## prokn GO + Reactome enrichment (bridged join)

- **Bridge:** human ortholog **HGNC gene symbol** → prokn Gene (`rdfs:label`) → `encodes` (SIO_010078) → UniProt Protein → `involved in` (RO_0002331) → GO biological-process term. This is a **gene-symbol-level (Entrez→HGNC) bridge — lower-confidence** than the direct-Entrez joins; symbol/alias mismatches undercount mapping.
- **Universe:** prokn GO-annotated genes = **7,663** (background N); WT signature genes mapped = **1,495** (of ~3,112 human orthologs; symbol-alias attrition).
- **Test:** per-GO-term hypergeometric over-representation with Benjamini–Hochberg FDR → **69 terms at FDR < 0.05**. Themes: translation/ribosome (cytoplasmic translation 4.3×, FDR≈10⁻³¹), mitochondrial OXPHOS & respiration (12 terms), immune/inflammatory (15), ubiquitin–proteasome (9), cell cycle (9), heme/erythroid (5), oxidative-stress response & oxidant detoxification (2 — corroborating the Nrf2 axis). Bone-specific processes (ossification, bone mineralization, osteoblast differentiation, Wnt) are present gene-level but **not** over-represented.
- **Artifacts (GO):** raw pairs `data/prokn_geneGO_raw.json`; enrichment `data/prokn_go_enrichment_labeled.tsv`; figure `figures/bone_fig4_go_enrichment.png`; script `scripts/go_process.py`.
- **Reactome (same bridge; Gene → `encodes` → Protein → `participates in` [RO_0000056] → Reactome `R-HSA` pathway):** background = **6,032** genes; **1,221** signature genes mapped; **110 pathways enriched at FDR < 0.05** (hypergeometric + BH) — translation/ribosome, ubiquitin–proteasome, neutrophil degranulation (myeloid), respiratory electron transport, HIF proline-hydroxylation. Artifacts: `data/prokn_reactome_raw.json`, `data/prokn_reactome_enrichment_labeled.tsv`, `figures/bone_fig5_reactome.png`, `scripts/reactome_process.py`.

## Countermeasures (mechanism-derived — not medical advice)

Derived from the gene-level signature + GO pathways (spoke-okn has no usable bone drug edges; compound→gene is toxicogenomic). Ranked by data support: **Nrf2 activation / antioxidants** (High — genetic Nrf2-KO worsening + enriched oxidative-stress/OXPHOS GO), **mechanical loading / resistive exercise** (High, established), **sclerostin inhibition / Wnt agonism** (LRP5/WIF1/LGR5 ↓), **PTH anabolics** (ALPL/IBSP/COL1A1/FAM20A ↓), **anti-resorptives** (NFATC1/CSF1/MMP9/CA2 ↓), **anti-inflammatory / cytokine modulation** (CXCL2/CCL2 ↑; exploratory), **mitochondrial / metabolic support** (exploratory). Full table: `data/countermeasures.tsv` and xlsx sheet *Countermeasures*.

**Retrieved curated drugs (rdkg `treats`).** A cross-KG drug search found the productive layer in **rdkg**: `Drug → treats → Disease` edges for bone diseases (osteoporosis and its subtypes, osteogenesis imperfecta, hypophosphatasia, Paget, osteomalacia, rickets), curated to bone-loss indications and mapped to signature genes — bisphosphonates, denosumab, teriparatide/PTH, **romosozumab**, **asfotase alfa** (ALPL enzyme replacement), calcitonin, SERMs, vitamin D/calcium/mineral, burosumab, bortezomib. Coverage of the other bio-KGs: spoke-okn `TREATS_CtD` has no osteoporosis edges; prokn's Compound `activity` layer is medicinal-chemistry bioactivity probes (CA2/MMP9 inhibitor scaffolds), not named drugs; biobricks ICE/Tox21/ToxCast are toxicology screens. Table: `data/retrieved_drugs.tsv` / xlsx sheet *Retrieved drugs*.

## Known limitations affecting reproducibility

- **Single flight study / cross-genotype reproducibility only** — no independent second bone spaceflight cohort.
- **Unloading attribution not possible** — the direct-bone HLU data are 8 genes (cortical) and near-zero-count artefacts (marrow).
- **spoke-okn bone coverage is thin** — `ASSOCIATES_DaG` returns osteoarthritis only (90 genes); `TREATS_CtD` has no osteoporosis edges; compound→gene is toxicogenomic. Bone-disease/phenotype linkage therefore rests on digcfdekg (GWAS traits) and rdkg (HPO phenotypes).
- **Mouse-only, ortholog-inferred throughout.**

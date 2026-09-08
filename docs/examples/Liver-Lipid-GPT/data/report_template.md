# Spaceflight and mouse liver lipid dysregulation: a partial reproduction
### Beheshti et al. (2019), tested with SPOKE-GeneLab and augmented through OKN

**Date:** 2026-09-08 · **Endpoint:** OKN federated SPARQL · **Model:** GPT-6-Astra

> **Framing.** Individual mouse-liver assay contrasts from STS-135, RR1-CASIS and RR3; a reanalysis of retained differential-expression summaries with human-ortholog annotations. This is a partial thematic reproduction and hypothesis-generating augmentation. Pre-filtered graph records cannot recreate the paper's complete experimental or statistical analysis.

**Abbreviations.** OKN = Open Knowledge Network; KG = knowledge graph; OSD/GLDS = Open Science Data/GeneLab Dataset accession; STS = Space Transportation System; RR = Rodent Research; ISS = International Space Station; CASIS = Center for the Advancement of Science in Space; RNA = ribonucleic acid; DE = differential expression; GO BP = Gene Ontology biological process; ORA = over-representation analysis; GSEA = gene set enrichment analysis; NES = normalized enrichment score; FDR = false discovery rate; BH = Benjamini–Hochberg; IPA = Ingenuity Pathway Analysis; ORO = Oil Red O; PCA = principal component analysis; t-SNE = t-distributed stochastic neighbor embedding; NAFLD = non-alcoholic fatty liver disease, the source's terminology; HDL/LDL = high/low-density lipoprotein; HGNC = HUGO Gene Nomenclature Committee.

## 1. Executive summary

**A limited lipid-related signal can be recovered, strongest in STS-135; uniform reproduction across missions is not established.** The three selected clean contrasts contain **{{retained_total:,}} retained gene–assay records**. Applying adjusted p ≤ 0.05 and |log₂ fold change| ≥ 1 gives **{{strict25}}**, **{{strict47}}**, and **{{strict137}}** mouse genes in OSD-25, OSD-47, and OSD-137, respectively.

The STS-135 1.2-fold sensitivity analysis recovers an excess of upregulated genes annotated to fatty acid β-oxidation in ProKN: **{{beta_k}}/{{beta_K}} genes, {{beta_fold:.2f}}× enrichment, BH FDR {{beta_fdr:.3g}}**, against all mapped GO-annotated genes. This signal disappears after FDR correction when the background is restricted to graph-retained genes. It is therefore **threshold- and background-dependent concordance**, not a numerical reproduction of the paper's GSEA.

The clearest augmentation is the association of the strict STS-135 human-ortholog signature with lipid traits in **digcfdekg**. The fatty-liver trait contains **{{fatty_k}} of {{fatty_n}} signature genes**; enrichment persists against the retained-gene background (**{{fatty_fold:.2f}}×; FDR {{fatty_fdr:.3g}}**). These are inferred human gene–trait associations, not evidence that these mice or astronauts have the disease.

## 2. Sources used

| Queried KG | Version | Contribution |
|---|---|---|
| spoke-genelab | v0.0.2 | Assay metadata, precomputed mouse expression effects, mouse→human orthologs |
| wikidata | No version returned by the registry | Entrez→Ensembl/HGNC mappings; identifier bridge only |
| prokn | v0.0.5 | Human gene→protein→GO and Reactome membership |
| digcfdekg | v0.0.1 | Human gene→lipid and fatty-liver trait associations |
| rdkg | v0.0.1 | Disease annotation and a separate explicitly genetic association test |

Every source above is represented by a supporting query in the reproducibility record. Source counts in the ranked table count biological annotation KGs; Wikidata is recorded as an identifier bridge and does not count as independent biological corroboration. The reference paper was identified via PubMed and its relevant full-text and supplementary passages were read through Paperclip [1].

The capability catalog also lists alternative suppliers. ProKN was selected to give both GO and Reactome through the same protein layer; digcfdekg supplies the trait test; rdkg separates general disease links from explicit genetic associations. The complete use-or-drop reconciliation, including payload-only suppliers, is recorded in the reproducibility specification. Other suppliers were outside this bounded reproduction, not shown to lack data.

## 3. Design and rules

### 3.1 Match datasets before interpreting effects

The paper's Methods identify GLDS-25 as STS-135, GLDS-47 as RR1-CASIS, GLDS-137 as RR3, and GLDS-168 as the NASA analysis [1]. We use that explicit Methods mapping because the Results text describes the accessions inconsistently. The graph study titles support the selected mappings. GLDS and OSD accession numbers serve only to select studies within SPOKE-GeneLab; cross-KG joins use gene identifiers.

{{coverage_table}}

OSD-168 has no contrast passing the supplied validator: its flight and ground factor strings disagree about mission labels and spike-in status. This is a **metadata-based exclusion**, not a demonstration that every underlying NASA experiment was confounded. OSD-48 was audited because it also represents RR1, but was not substituted for the paper's OSD-168 processing. Other liver studies were excluded because they are not the paper's selected datasets. No assays were pooled across missions or strains.

Only Space Flight in arm 1 versus Ground Control in arm 2 was kept, with matching tissue IDs and matching non-condition covariates. Positive log₂ fold change means higher expression in flight. The original paper reports cohort sizes of six per arm for STS-135 and RR3 and three per arm for RR1-CASIS [1]; these were not inferred as effective sample sizes from the KG.

### 3.2 Reproduce what the data support

SPOKE-GeneLab retains expression edges at adjusted p ≤ 0.1 [2]. The extract includes all retained records for each selected contrast; an omitted gene is **unobserved in this filtered extract**, not a measured zero or proof of unchanged expression.

The primary rule is adjusted p ≤ 0.05 and |log₂ fold change| ≥ 1. A separate sensitivity rule uses |log₂ fold change| ≥ log₂(1.2), approximately 0.263, with the same adjusted-p threshold. The paper used a 1.2-fold cutoff in part of its pathway work, but used differing significance rules and analysis pipelines across datasets, including a three-group ANOVA for STS-135 and nominal p-values for CASIS [1]. Our sensitivity rule is consequently **paper-like**, not identical.

Human orthologs are collapsed separately within each assay using the largest absolute effect, retaining the matching adjusted p-value and recording the mean-effect alternative and mapping ambiguity. Many-to-one and one-to-many mappings are flagged. GO and Reactome annotations are normalized to unique human Entrez IDs before testing; HGNC and Ensembl aliases do not count as separate genes.

Functional tests use the retrieved direct GO BP and Reactome memberships; no additional ontology propagation is applied. Disease tests likewise use exact annotated disease nodes, not descendant-expanded categories.

ORA uses a one-sided hypergeometric test and BH correction over every eligible category, including zero-overlap categories. We run each assay, direction (all/up/down), threshold and background separately. The primary annotation backgrounds are all uniquely mapped genes with the relevant annotation; a conditional sensitivity background intersects those genes with the assay's retained signature. Neither is the missing original tested-gene universe. These exploratory FDR values control each stated family, not every analysis in this report jointly.

## 4. Confidence tiers

Tier A would require independently reproduced, method-matched evidence across comparable experiments; **{{tier_a}}** rows qualify. Tier B identifies strict-rule genes with a retrieved lipid/circadian functional annotation, unambiguous orthology in the retrieved mapping and consistent max/mean sign: **{{tier_b}}** rows. Tier C contains the remaining strict-rule candidates or ambiguous mappings: **{{tier_c}}** rows. These are prioritization tiers, not probabilities or clinical evidence grades.

The score is 10 for a retrieved lipid/circadian term, plus the number of biological source KGs, plus min(|log₂FC|, 5)/10; ties sort by adjusted p. It intentionally prioritizes relevance to this paper. Recurrence, druggability and causal effects are not silently assumed. The human ranked table contains **{{human_rows}} assay–human-gene rows**, which differs from the mouse count because orthology can expand, merge or omit genes.

## 5. Findings by axis

### 5.1 Coverage and expression burden

![Retained and strict-rule results](figures/fig1_assay_coverage.png)

> ***Figure 1. Assay coverage and strict differential-expression results.*** **(A)** All retained expression records, with a logarithmic count axis. **(B)** Numbers of up/down mouse genes at adjusted p ≤ 0.05 and |log₂FC| ≥ 1. Provenance: spoke-genelab reified MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG statements. Counts are genes, not biological replicates, and have no sampling error bars.

STS-135 dominates the usable signature. The tiny retained RR3 set cannot establish absence of lipid biology or explain the difference from the paper's originally reported gene counts. Processing differences, significance definitions and the graph's input selection remain unresolved contributors.

### 5.2 Retained lipid-related transcripts

![Selected transcript effects](figures/fig2_gene_effects.png)

> ***Figure 2. Selected STS-135 lipid-related transcript effects.*** Bars show retrieved mouse log₂FC; q labels show the stored adjusted p-value. Ppara is included as a paper-relevant regulator passing the sensitivity rule; the other displayed genes pass the strict rule. Provenance: spoke-genelab expression statements. The figure is a selected mechanistic illustration, not a ranked statistical discovery plot. Effect standard errors and usable per-assay sample counts were not retrieved, so confidence intervals are not reconstructed.

**Pnpla2, Plin5, Apoa4 and Crat** increase, while **Mlxipl and Elovl6** decrease. **Ppara** also increases at the transcript level. This mixed direction supports lipid remodeling rather than uniform activation of every lipid process. A Ppara transcript change cannot be substituted for IPA's inferred PPARα activity, and transcript Apoa4 cannot reproduce protein abundance in a different cohort.

## 6. Functional and disease analyses

### 6.1 GO and Reactome, with explicit background sensitivity

GO BP tests used **{{go_genes:,}}** mapped genes across **{{go_terms:,}}** terms; Reactome used **{{reactome_genes:,}}** genes across **{{reactome_terms:,}}** pathways. At the strict threshold, no lipid GO or Reactome enrichment survives FDR correction. RR1-CASIS instead yields a sparse muscle-contraction GO hit driven by a few mapped genes; it is not a recovered liver-lipid mechanism.

![GO background sensitivity](figures/fig3_background_sensitivity.png)

> ***Figure 3. Background dependence of the STS-135 GO result.*** **(A)** Upregulated human orthologs under the 1.2-fold sensitivity rule against all mapped GO-annotated genes. **(B)** The same signature against only retained, GO-annotated genes. Bars show −log₁₀(BH FDR); the dashed line is FDR 0.05. Labels report observed/expected fold and k/K, where k is signature overlap and K is category size in that background. Provenance: spoke-genelab orthologs→Wikidata identifiers→ProKN encodes→RO_0002331. These are ORA results, not GSEA NES or pathway activation scores.

The fatty-acid oxidation result agrees directionally with the paper's STS-135 Supplementary Table 1, which reports positive NES for fatty acid β-oxidation and fatty acid metabolism [1]. However, conditioning on the retained genes removes significance. This distinguishes a recoverable theme in the selected gene set from a robust reproduction of the original test.

Reactome was also run. The all-direction STS-135 sensitivity analysis identifies **cytosolic tRNA aminoacylation** and **mitochondrial protein import** against all annotated genes; neither remains significant against the retained background. It does not reproduce a significant Reactome lipid pathway at the selected cutoffs. GO enrichment therefore does not stand in for Reactome replication.

### 6.2 Human trait and curated disease augmentation

![Trait enrichment](figures/fig4_trait_enrichment.png)

> ***Figure 4. Lipid-trait enrichment in the strict STS-135 human signature.*** Hypergeometric ORA with BH correction across four explicitly selected trait sets: fatty liver disease, triglycerides, LDL and HDL cholesterol. Background: **{{fatty_N}}** retained genes annotated in digcfdekg; foreground: **{{fatty_n}}** strict-rule human genes. Labels give k/K and FDR. Provenance: logged spoke-genelab→human Entrez→digcfdekg geneToTrait joins. Associations are computationally inferred and have no intervention or disease-risk interpretation.

{{trait_table}}

The associations remain enriched under the conditional background. In this dataset the broad trait family is informative; broad sets are not necessarily null. RR1-CASIS and RR3 do not show significant enrichment for these four traits. General rdkg related_to links add disease context, but they are not uniformly Mendelian or causal evidence. A separate test using only explicit rdkg genetic_association edges yields no significant disease enrichment in either threshold analysis; the small annotated foreground limits interpretation. Exact disease-node sets were tested, not expanded disease categories.

### 6.3 Analyses run and deliberately omitted

| Family | Status and reason |
|---|---|
| GO BP ORA | Run at strict and 1.2-fold thresholds, with direction and background sensitivity |
| Reactome ORA | Run separately with the same sensitivity design |
| Broad lipid/NAFLD trait ORA | Run using digcfdekg; four biologically selected endpoints, not an all-trait screen |
| Curated genetic disease ORA | Run using rdkg genetic_association; general related_to links kept as annotations |
| Original GSEA, PCA and t-SNE | Not reproduced: full unfiltered rankings or sample-level matrices are absent from the assay extract |
| Original histology and proteomics | Not reproduced: selected KG assays do not supply the paper's image quantification or protein matrix |
| IPA upstream regulators | Not reproduced: proprietary regulator model and original inputs unavailable; gene expression cannot replace activation z-scores |
| GO molecular function/cellular component | Skipped to keep the functional reproduction focused on the paper's biological-process comparison |
| Phenotype, drug and exposure analysis | Skipped: not needed for this lipid-transcript reproduction; disease/trait augmentation supplies the selected translational context |
| Methylation | Skipped: some assays exist, but this was not a tested molecular layer in the target paper |
| Taxonomic, geographic and drug-mechanism maps | Skipped: no organism alignment, spatial question or retrieved drug layer to synthesize |

These omissions define the boundary of the reproduction; they are not claims that the wider federation lacks such information.

Individual tests with no annotated foreground are explicitly marked in the workbook's Analysis Status sheet and `data/analysis_status.tsv`. In particular, RR3 has no mapped foreground for Reactome or the curated genetic-disease family; a significance test is not computed for those empty sets. Up/down subsets can also be empty. The complete status table distinguishes an untestable combination from a tested nonsignificant result.

## 7. Discussion

The useful result is a candidate mechanism in the retained STS-135 signature, together with an explicit accounting of what does not reproduce. Lipid handling, oxidation and transport annotations connect altered mouse transcripts to human functions. Enrichment for inferred human lipid traits adds orthogonal annotation, but the KGs may reuse underlying databases and source counts must not be read as independent experimental replications.

A testable next step is to recover the original unfiltered count matrices and sample metadata for all paper cohorts, resolve OSD-168's factor encoding, and rerun the original rank-based analysis with a common documented pipeline. The specific prediction is that the fatty-acid oxidation theme should persist in STS-135 without relying on a preselected graph universe. Uniformity across strains, duration effects, insulin/glucagon regulator activity and on-orbit independence need their own reproduced evidence.

## 8. Comparison with prior work

| # | Claim | Concordance |
|---|---|---|
| 1 | Retained STS-135 results recover fatty-acid oxidation themes | **PARTIALLY SUPPORTED** — paper Supplementary Table 1 has positive NES; our sensitivity ORA agrees against the annotation background, but not the retained background [1] |
| 2 | Lipid dysregulation is reproduced across all flight missions | **UNRESOLVED** — the retained ISS signatures and excluded OSD-168 contrasts do not establish the paper's cross-mission result [1] |
| 3 | Human fatty-liver trait links support a lipid-related hypothesis | **PARTIALLY SUPPORTED** — agrees with the paper's disease-pathway framing, but the added human gene–trait associations do not demonstrate disease [1] |
| 4 | Insulin activation and glucagon inhibition are reproduced | **UNRESOLVED** — those are IPA regulator predictions in the paper and were not regenerated here [1] |
| 5 | ORO staining was significant in every cohort and increased significantly with duration | **CONTRADICTED** — the Results state RR3 was not significant and the 21-versus-37-day comparison had p=0.07, despite stronger wording in the caption and discussion [1] |
| 6 | Significant STS-135 circadian-rhythm enrichment is established by Supplementary Table 1 | **CONTRADICTED** — that table reports circadian rhythm FDR 0.3056; a positive score is not significance at 0.05 [1] |

According to PubMed metadata and the Paperclip full text, the comparison concerns the same 2019 article. Claims 1, 4, 5 and 6 were checked against the relevant original methods, results and supplement. The per-claim evidence is in [Liver-Lipid-GPT_literature_comparison.md](Liver-Lipid-GPT_literature_comparison.md).

Where the KG evidence diverges from the literature: sparse retained signatures and mismatched OSD-168 factor labels are data-scope or metadata issues, not proof that the original measurements were wrong. Claims 5 and 6 expose tensions within the paper's narrative and displayed statistics; they are not failures inferred from absent KG rows. The comparison is targeted to this paper, not an exhaustive search of subsequent literature.

## 9. Full ranked results

The full mouse extracts, human mapping results and enrichment analyses are in **Liver-Lipid-GPT_results.xlsx** and `data/`. The ranked table contains one row per strict-rule assay–human-gene pair. Sort by rank or source count; filter by study, direction, tier or mapping ambiguity. Source pills identify expression evidence (spoke-genelab), functional annotation (prokn), disease links (rdkg) and the four selected trait links (digcfdekg).

{{ranked_slice}}

<!-- RESULTS_TABLE -->

The ranking prioritizes lipid relevance, so candidates such as Pnpla2, Apoa4 and Elovl6 rise above large but poorly annotated effects. An ambiguous Acot-family projection retains its flag and stays in Tier C. Ranking does not establish causal roles or suggest a treatment.

## 10. Summary of findings and limitations

The available assays support a **partial thematic reproduction concentrated in STS-135**, with **{{strict_total}} strict-rule mouse gene–assay results** across the selected contrasts. GO findings are sensitive to the threshold and background. The human lipid-trait augmentation persists within the retained STS-135 universe. The full multi-mission, multi-omics conclusion is not reproduced.

1. The graph is filtered at adjusted p ≤ 0.1. Missing genes, complete tested backgrounds and full sample matrices cannot be reconstructed from these records.
2. Original pipelines and significance rules differ. Neither the strict threshold nor the sensitivity rule reproduces the paper's complete DE/GSEA/IPA procedure.
3. Annotation-background ORA can reflect measurement and selection bias; conditional ORA asks a narrower question within retained genes. Neither estimates an unbiased whole-experiment pathway effect.
4. OSD-168 is excluded on stored metadata. The apparent covariate mismatch may include encoding artifacts. OSD-137 is supported by the paper's Methods, but is not presumed numerically equivalent to every NASA reprocessed RR3 result.
5. Effects are kept separate by assay; species, strain, duration and sample handling prevent a causal pooled spaceflight interpretation. STS-135 also includes live-return stress.
6. Human orthology and identifier mappings lose and expand genes. Max-effect and mean-sign agreement cannot prove functional conservation. Missing annotations are not evidence of biological absence.
7. Trait links are inferred associations; rdkg related_to is broad context. No clinical risk, disease diagnosis, treatment efficacy or causal phenotype claim follows from these results.
8. FDR correction is within each named family and analysis setting; the multiple exploratory settings are not a single confirmatory test. Gene-level confidence intervals cannot be reconstructed from the retrieved fields.
9. Full-text comparison was limited to the target paper. Conflicting narrative and tabulated statistics are reported explicitly. Versions are pinned for registered KGs, but the Wikidata graph has no version in the returned registry inventory.

## 11. Reproducibility

The originating request, specification, versions and verbatim supporting queries with row counts are in [Liver-Lipid-GPT_reproducibility.md](Liver-Lipid-GPT_reproducibility.md), with scripts in `scripts/` and extracts in `data/`.

## 12. References

Retrieved via the **PubMed** MCP connector. Full-text verification via the **Paperclip** MCP connector; KG selection policy checked against its source repository.

1. Beheshti A, et al. Multi-omics analysis of multiple missions to space reveal a theme of lipid dysregulation in mouse liver. *Scientific Reports*. 2019. PMID:31844325 · [doi:10.1038/s41598-019-55869-2](https://doi.org/10.1038/s41598-019-55869-2) — full-text-verified ([PMC6915713](https://pmc.ncbi.nlm.nih.gov/articles/PMC6915713/)).
2. BaranziniLab. NASA SPOKE-GeneLab Knowledge Graph, supported data types and statistical selection criteria. [Source repository](https://github.com/BaranziniLab/spoke_genelab). Accessed 2026-09-08.

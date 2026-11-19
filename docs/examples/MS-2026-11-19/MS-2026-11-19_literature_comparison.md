# MS-2026-11-19 — Literature comparison

Companion to `MS-2026-11-19_report.md` §8. Each claim below is a finding as the OKN knowledge-graph analysis stated it, compared against primary literature retrieved through the **PubMed** MCP connector. Comparison used titles, abstracts and NCBI metadata (no full-text reading; the Paperclip connector was not used in this run). The **Concordance** value is one of SUPPORTED / PARTIALLY SUPPORTED / CONTRADICTED / MIXED / NOVEL / UNRESOLVED. A literature comparison is not a validation: several rows below expose errors or gaps in the graphs rather than confirming them.

## Claim 1 — HLA class II plus a polygenic immune architecture dominate MS genetic risk
**KG finding.** Tier-A genes are led by IL2RA, IFNG, CD86, CD6, IL17A, CD58, IL7R, TNFRSF1A; the HLA class II genes HLA-DRB1, HLA-DQB1 and HLA-DRA are tier A and HLA-DPB1 tier B (spoke-okn, rdkg, digcfdekg, wikidata). The digcfdekg PIGEAN list (1,056 genes) is headed by CD28, IL7R, IKZF3, HLA-A and CD27.
**Literature.** The IMSGC genomic map of 47,429 cases and 68,374 controls reports 200 autosomal non-MHC variants, 32 variants within the extended MHC and one X-chromosome variant. It prioritises 551 genes spread across innate and adaptive immune pathways [1].
**Concordance: SUPPORTED.** The KGs reproduce the MHC-plus-immune architecture. Their curated gene sets (164 spoke-okn genes, 45 rdkg genes) are much smaller than the 551 prioritised genes, so tiering undercounts loci that are supported by GWAS but not curated.

## Claim 2 — Microglia are implicated alongside peripheral immunity
**KG finding.** Over-representation of GO "microglial cell activation" (k=7 of K=20; FDR ≈ 2e-6) in the MS signature, together with the dominant T-cell, B-cell and cytokine terms.
**Literature.** In the IMSGC study, MS susceptibility genes were enriched in purified human microglia, while initiation was attributed mainly to peripheral immune perturbation [1].
**Concordance: SUPPORTED.** Both point to a peripheral-immune signal with a CNS-resident microglial component.

## Claim 3 — Prevalence follows a latitude gradient and peaks in Northern Europe and North America
**KG finding.** spoke-okn IHME 2019 prevalence correlates with |latitude| across 200 countries (Spearman ρ = 0.84). The highest values are Sweden, Canada and Norway.
**Literature.** In GBD 2016, the highest age-standardised prevalence was in high-income North America, western Europe and Australasia, and the lowest in sub-Saharan Africa and Oceania [4]. The Atlas of MS estimates 2.8 million people with MS, a global prevalence of 35.9 per 100,000 [3].
**Concordance: SUPPORTED.** The regional ranking agrees. The KG's country values are on the same scale (up to about 217 per 100,000).

## Claim 4 — Prevalence also tracks national income
**KG finding.** Prevalence correlates with GDP per capita (ρ = 0.70, n=165). The latitude association survives adjustment for GDP (partial ρ = 0.74).
**Literature.** GBD used the Socio-demographic Index to relate MS burden to development level and noted that many regions have few or no epidemiological data [4]. The Atlas also reports persistent gaps in surveillance [3].
**Concordance: PARTIALLY SUPPORTED.** The literature recognises that development level and ascertainment matter. Neither source gives the specific income-adjusted latitude estimate computed here, so that part remains a KG-derived result.

## Claim 5 — EBV is a leading environmental risk factor
**KG finding.** biohealth lists Epstein–Barr virus and "human gammaherpesvirus" under `causes`, and viral infection is the largest literature-derived risk-factor category (Figure 7C).
**Literature.** In more than 10 million US military personnel, MS risk rose 32-fold after EBV infection. Serum NfL increased only after EBV seroconversion [2].
**Concordance: SUPPORTED.**

## Claim 6 — Many other viruses, including CMV, "cause" MS
**KG finding.** biohealth also asserts `causes` for cytomegalovirus, measles, mumps, rubella, HHV-6, HERV-W, rhinovirus, rabies virus and others (42 viral entities in total).
**Literature.** The same cohort found no increase in MS risk after infection with other viruses, including the similarly transmitted cytomegalovirus [2].
**Concordance: CONTRADICTED.** This is a KG error of kind: SemMedDB-style predications extracted from text, without effect sizes or negation handling, flatten hypotheses and null results into `causes` edges.

## Claim 7 — Vitamin D is a risk-modifying exposure, with VDR/CYP24A1/CYP27B1 genetic support
**KG finding.** biohealth links vitamin D both to `predisposes` and to `preventative`. VDR and CYP24A1 are tier A, CYP27B1 is tier B, and prokn lists cholecalciferol (target VDR) among MS-indicated compounds.
**Literature.** In a Mendelian-randomisation study, a one-SD genetically lower 25OHD was associated with about 2-fold higher odds of MS [6].
**Concordance: SUPPORTED.** The literature supports a causal direction that the KG's mixed predicates leave ambiguous.

## Claim 8 — Females are predisposed
**KG finding.** biohealth: "Females" / "sex" `predisposes_to_condition`.
**Literature.** Atlas of MS: females are twice as likely as males to live with MS [3].
**Concordance: SUPPORTED.**

## Claim 9 — Neurofilament light chain is absent from the KG biomarker set
**KG finding.** biomarkerkg's 29 MS diagnostic biomarkers cover S1PR1/S1PR5, SPHK1/2, APOA1, IFNG, IL17A, RMRP, immunoglobulin increases and quinolinic acid. No NEFL / NfL record was retrieved.
**Literature.** Age- and BMI-adjusted serum NfL Z-scores above 1.5 predicted future disease activity (OR 3.15) and tracked response to therapy [5].
**Concordance: NOVEL.** No prior work describes this gap. It is a KG coverage finding: the most validated MS fluid biomarker is missing from the federation's biomarker graph.

## Claim 10 — CSF immunoglobulin / plasma-cell activity marks MS
**KG finding.** biomarkerkg lists increased immunoglobulins (IgG/IgA/IgM, gamma fraction) in CSF. Gene Expression Atlas CSF leukocytes (E-MTAB-69) show up-regulation of IGHM, JCHAIN, TNFRSF17, MZB1 and POU2AF1.
**Literature.** The 2017 McDonald criteria allow CSF-specific oligoclonal bands to substitute for dissemination in time [8].
**Concordance: PARTIALLY SUPPORTED.** Intrathecal immunoglobulin synthesis is established, but no KG encodes oligoclonal bands as a named biomarker. The KG evidence is indirect: immunoglobulin increase plus a plasma-cell transcript signature.

## Claim 11 — Subtype ontology: PRMS is a live term and CIS has no exact term
**KG finding.** ubergraph carries PRMS (MONDO_0000452 = DOID_0050785) with 22 rdkg `treats` edges, and has no exact term for clinically isolated syndrome.
**Literature.** The 2013 revision of MS clinical courses eliminated PRMS as a category and added CIS to the disease spectrum [9].
**Concordance: CONTRADICTED.** The ontologies lag the clinical classification. Drug–subtype edges attached to PRMS reflect trial-registry wording, not current phenotypes.

## Claim 12 — Anti-CD20 B-cell depletion acts in progressive MS
**KG finding.** prokn maps ocrelizumab, ofatumumab, ublituximab and rituximab to MS4A1 (tier B). rdkg links ocrelizumab to the progressive-MS group.
**Literature.** In ORATORIO (PPMS, n=732), ocrelizumab lowered 12-week confirmed disability progression (32.9% vs 39.3%; HR 0.76) [7].
**Concordance: SUPPORTED.**

## Claim 13 — BTK inhibitors are an emerging B-cell/microglia-directed class
**KG finding.** prokn records tolebrutinib, evobrutinib and fenebrutinib (max phase 3) and pirtobrutinib (phase 2) against BTK. rdkg links tolebrutinib and remibrutinib to MS. BTK is tier C (digcfdekg plus drug target) and a PPI hub (degree 34).
**Literature.** In HERCULES (nrSPMS), tolebrutinib reduced 6-month confirmed disability progression (HR 0.69) [10]. In GEMINI 1/2 (relapsing MS), it was not superior to teriflunomide on annualised relapse rate [11].
**Concordance: PARTIALLY SUPPORTED.** The class is supported for progression in non-relapsing SPMS but not for relapse suppression. The KG does not distinguish these outcomes.

## Claim 14 — IFN-β induces a type-I interferon gene signature in blood
**KG finding.** Gene Expression Atlas E-GEOD-26104 (IFN-β-1a, 3 months, PBMC) shows IFI27, CCL2, CCL8, CXCL10, SERPING1, RSAD2, IFI44L and IFIT1 up. E-GEOD-14386 shows IFI27, CXCL11, OAS1 and ZBP1 up.
**Literature.** IFN-β therapy induces IFN-response genes in a patient-dependent way, and baseline IFN-signature level predicts the pharmacological response [13]. A treated-RRMS signature of 104 genes was enriched for IFN signalling [14].
**Concordance: SUPPORTED.**

## Claim 15 — The KGs encode no gene–environment interaction
**KG finding.** No queried KG links HLA genotype to EBV (or to smoking/vitamin D) as an interaction. Risk factors (biohealth, rdkg) and risk genes (spoke-okn, rdkg) sit in separate layers.
**Literature.** Antibodies to EBNA1 fragment 385–420 interacted with HLA-DRB1*15 and with absence of A*02 (attributable proportions 0.60 and 0.39) [12].
**Concordance: NOVEL.** No prior work describes this gap. It is a KG-structure finding: a well-documented G×E interaction is not representable in the current graphs.

## References

1. International Multiple Sclerosis Genetics Consortium, et al. Multiple sclerosis genomic map implicates peripheral immune cells and microglia in susceptibility. *Science*. 2019. PMID:31604244 · [doi:10.1126/science.aav7188](https://doi.org/10.1126/science.aav7188)
2. Bjornevik K, et al. Longitudinal analysis reveals high prevalence of Epstein-Barr virus associated with multiple sclerosis. *Science*. 2022. PMID:35025605 · [doi:10.1126/science.abj8222](https://doi.org/10.1126/science.abj8222)
3. Walton C, et al. Rising prevalence of multiple sclerosis worldwide: Insights from the Atlas of MS, third edition. *Mult Scler*. 2020. PMID:33174475 · [doi:10.1177/1352458520970841](https://doi.org/10.1177/1352458520970841)
4. GBD 2016 Multiple Sclerosis Collaborators, et al. Global, regional, and national burden of multiple sclerosis 1990-2016: a systematic analysis for the Global Burden of Disease Study 2016. *Lancet Neurol*. 2019. PMID:30679040 · [doi:10.1016/S1474-4422(18)30443-5](https://doi.org/10.1016/S1474-4422%2818%2930443-5)
5. Benkert P, et al. Serum neurofilament light chain for individual prognostication of disease activity in people with multiple sclerosis: a retrospective modelling and validation study. *Lancet Neurol*. 2022. PMID:35182510 · [doi:10.1016/S1474-4422(22)00009-6](https://doi.org/10.1016/S1474-4422%2822%2900009-6)
6. Mokry LE, et al. Vitamin D and Risk of Multiple Sclerosis: A Mendelian Randomization Study. *PLoS Med*. 2015. PMID:26305103 · [doi:10.1371/journal.pmed.1001866](https://doi.org/10.1371/journal.pmed.1001866)
7. Montalban X, et al. Ocrelizumab versus Placebo in Primary Progressive Multiple Sclerosis. *N Engl J Med*. 2017. PMID:28002688 · [doi:10.1056/NEJMoa1606468](https://doi.org/10.1056/NEJMoa1606468)
8. Thompson AJ, et al. Diagnosis of multiple sclerosis: 2017 revisions of the McDonald criteria. *Lancet Neurol*. 2018. PMID:29275977 · [doi:10.1016/S1474-4422(17)30470-2](https://doi.org/10.1016/S1474-4422%2817%2930470-2)
9. Lublin FD, et al. Defining the clinical course of multiple sclerosis: the 2013 revisions. *Neurology*. 2014. PMID:24871874 · [doi:10.1212/WNL.0000000000000560](https://doi.org/10.1212/WNL.0000000000000560)
10. Fox RJ, et al. Tolebrutinib in Nonrelapsing Secondary Progressive Multiple Sclerosis. *N Engl J Med*. 2025. PMID:40202696 · [doi:10.1056/NEJMoa2415988](https://doi.org/10.1056/NEJMoa2415988)
11. Oh J, et al. Tolebrutinib versus Teriflunomide in Relapsing Multiple Sclerosis. *N Engl J Med*. 2025. PMID:40202623 · [doi:10.1056/NEJMoa2415985](https://doi.org/10.1056/NEJMoa2415985)
12. Sundqvist E, et al. Epstein-Barr virus and multiple sclerosis: interaction with HLA. *Genes Immun*. 2012. PMID:21776012 · [doi:10.1038/gene.2011.42](https://doi.org/10.1038/gene.2011.42)
13. van Baarsen LG, et al. Pharmacogenomics of interferon-beta therapy in multiple sclerosis: baseline IFN signature determines pharmacological differences between patients. *PLoS One*. 2008. PMID:18382694 · [doi:10.1371/journal.pone.0001927](https://doi.org/10.1371/journal.pone.0001927)
14. Gurevich M, et al. Transcriptional response to interferon beta-1a treatment in patients with secondary progressive multiple sclerosis. *BMC Neurol*. 2015. PMID:26589141 · [doi:10.1186/s12883-015-0495-x](https://doi.org/10.1186/s12883-015-0495-x)

# Comparison with Prior Work: KG-Derived MS Claims vs. the Published Literature

**Scope.** Ten claims derived from the OKN federated multi-KG analysis of multiple sclerosis (MS) were checked against the primary literature. Searches were run against PubMed (via the PubMed MCP connector) and against full-text papers, regulatory documents and trial registries via Paperclip. Every citation below was resolved to a real PMID and its title/journal/year/volume/page verified against PubMed metadata; **no citation in this document is reconstructed from memory**. Where a claim could not be corroborated, that is stated explicitly.

*Attribution: bibliographic records and abstracts in this section were retrieved from **PubMed**; DOI links are given for each cited article as required by the data source's terms of use.*

Concordance vocabulary: **SUPPORTED** / **PARTIALLY SUPPORTED** / **NOVEL-OR-UNVERIFIED** / **CONTRADICTED**.

---

## Claim 1 — Genetics/immunology: the consensus MS gene core

> The top consensus MS genes recovered across KGs are dominated by adaptive-immune costimulation and cytokine-receptor signalling: HLA-DRB1, HLA-DQA1, IL2RA, IL7R, CD58, CD6, CD40, CD86, CD28, CLEC16A, TNFRSF1A, TYK2, STAT3/STAT4, EVI5, BATF, IKZF3, SOCS1, RGS1, MERTK.

**Concordance: SUPPORTED.**

This is essentially the canonical MS GWAS gene core. The 2011 IMSGC/WTCCC2 GWAS (9,772 cases) refined the HLA-DRB1 risk alleles, confirmed independent HLA class I (HLA-A) protection, and reported that "immunologically relevant genes are significantly overrepresented among those mapping close to the identified loci", particularly implicating T-helper-cell differentiation. The ImmunoChip study extended this to 110 established non-MHC risk variants at 103 loci, overwhelmingly immune genes. The definitive 2019 map (47,429 cases / 68,374 controls) established 200 autosomal non-MHC variants, one X variant and 32 MHC variants, prioritising 551 putative susceptibility genes across innate and adaptive immune compartments. Every gene named in the KG claim (costimulatory receptors CD40/CD58/CD6/CD86/CD28, cytokine receptors IL2RA/IL7R, JAK-STAT components TYK2/STAT3/STAT4/SOCS1, and CLEC16A/EVI5/TNFRSF1A/BATF/IKZF3/RGS1/MERTK) falls inside these published sets. The only nuance is emphasis: HLA-DRB1*15:01 dwarfs all non-MHC effects, and the KG's flat "consensus gene" ranking does not convey that effect-size hierarchy.

- International Multiple Sclerosis Genetics Consortium. Multiple sclerosis genomic map implicates peripheral immune cells and microglia in susceptibility. *Science*. 2019. PMID:31604244 · [doi:10.1126/science.aav7188](https://doi.org/10.1126/science.aav7188)
- Sawcer S, et al. Genetic risk and a primary role for cell-mediated immune mechanisms in multiple sclerosis. *Nature*. 2011. PMID:21833088 · [doi:10.1038/nature10251](https://doi.org/10.1038/nature10251)
- Beecham AH, et al. Analysis of immune-related loci identifies 48 new susceptibility variants for multiple sclerosis. *Nat Genet*. 2013. PMID:24076602 · [doi:10.1038/ng.2770](https://doi.org/10.1038/ng.2770)

---

## Claim 2 — Pathway mechanism: JAK-STAT and interleukin signalling

> ORA of the MS gene set gives "cell surface receptor signaling pathway via JAK-STAT" as the single most enriched GO BP term (16/47, 30-fold, FDR 2.3e-18), and Reactome "Interleukin-10 signalling" (9/31, 25-fold, FDR 2.0e-9), IL-4/IL-13, IFN-gamma, IL-12/-23/-21/-27, and "RUNX1 and FOXP3 control the development of regulatory T lymphocytes". Are JAK-STAT / IL-cytokine signalling established core MS mechanisms, and are BTK/JAK inhibitors pursued on that basis?

**Concordance: PARTIALLY SUPPORTED** — the biology is established; the therapeutic inference is only half right.

Cytokine-receptor/JAK-STAT signalling is unambiguously a core MS mechanism: the MS risk gene set is built from cytokine receptors and their downstream JAK-STAT machinery (IL2RA, IL7R, TYK2, STAT3, STAT4, SOCS1), and MS progression correlates with abnormal cytokine expression across Th1/Th17/Treg and myeloid axes. The direct pharmacological instantiation of the IL-2/CD25 arm was daclizumab (anti-CD25, i.e. IL2RA), which was superior to interferon beta-1a on relapse rate in the phase 3 DECIDE trial — though it was later withdrawn for immune-mediated toxicity. However, **no JAK inhibitor is approved or in late-phase development for MS** (JAK blockade in MS remains preclinical/EAE-level), and the IL-12/IL-23 axis highlighted by the Reactome result was directly tested and **failed**: ustekinumab (anti-IL-12/23 p40) showed no reduction in gadolinium-enhancing lesions in RRMS. The therapy class actually being pursued on a "signalling-hub" rationale is BTK inhibition, which sits on BCR/Fc-receptor/TLR signalling rather than JAK-STAT (see Claim 9).

- International Multiple Sclerosis Genetics Consortium. Multiple sclerosis genomic map implicates peripheral immune cells and microglia in susceptibility. *Science*. 2019. PMID:31604244 · [doi:10.1126/science.aav7188](https://doi.org/10.1126/science.aav7188)
- Palle P, et al. Cytokine Signaling in Multiple Sclerosis and Its Therapeutic Applications. *Med Sci (Basel)*. 2017. PMID:29099039 · [doi:10.3390/medsci5040023](https://doi.org/10.3390/medsci5040023)
- Kappos L, et al. Daclizumab HYP versus Interferon Beta-1a in Relapsing Multiple Sclerosis. *N Engl J Med*. 2015. PMID:26444729 · [doi:10.1056/NEJMoa1501481](https://doi.org/10.1056/NEJMoa1501481)
- Segal BM, et al. Repeated subcutaneous injections of IL12/23 p40 neutralising antibody, ustekinumab, in patients with relapsing-remitting multiple sclerosis: a phase II, double-blind, placebo-controlled, randomised, dose-ranging study. *Lancet Neurol*. 2008. PMID:18703004 · [doi:10.1016/S1474-4422(08)70173-X](https://doi.org/10.1016/S1474-4422%2808%2970173-X)

---

## Claim 3 — Vitamin D metabolism (CYP27B1 / CYP24A1)

> The MS gene set is significantly enriched for GO "response to vitamin D" (4/15, 24-fold, FDR 1.2e-4), driven by CYP27B1 and CYP24A1.

**Concordance: SUPPORTED.**

Both genes are genuine MS susceptibility loci, and the causal direction has independent genetic support. Whole-exome sequencing of MS multiplex families identified rare loss-of-function CYP27B1 variants (including known vitamin-D-dependent rickets type I mutations) that were over-transmitted to affected offspring (Peto OR 4.7; transmitted 35/35 in heterozygous parents), directly implicating the 1-alpha-hydroxylase. Two-sample Mendelian randomisation using 25OHD-lowering instruments found that each genetically determined 1-SD decrease in log-25OHD roughly doubled the odds of MS (OR 2.0, 95% CI 1.7-2.5), replicated in an independent MR that also isolated childhood BMI as a separate causal factor. Interventional evidence is more mixed — supplementation trials in established MS have largely been neutral — but the recent D-Lay MS randomised trial showed that 100,000 IU cholecalciferol every 2 weeks reduced combined clinical/MRI disease activity in clinically isolated syndrome (HR 0.66, p = 0.004). So the KG's vitamin-D signal reflects real, causally-supported biology, not an annotation artefact.

- Ramagopalan SV, et al. Rare variants in the CYP27B1 gene are associated with multiple sclerosis. *Ann Neurol*. 2011. PMID:22190362 · [doi:10.1002/ana.22678](https://doi.org/10.1002/ana.22678)
- Mokry LE, et al. Vitamin D and Risk of Multiple Sclerosis: A Mendelian Randomization Study. *PLoS Med*. 2015. PMID:26305103 · [doi:10.1371/journal.pmed.1001866](https://doi.org/10.1371/journal.pmed.1001866)
- Jacobs BM, et al. BMI and low vitamin D are causal factors for multiple sclerosis: A Mendelian Randomization study. *Neurol Neuroimmunol Neuroinflamm*. 2020. PMID:31937597 · [doi:10.1212/NXI.0000000000000662](https://doi.org/10.1212/NXI.0000000000000662)
- Thouvenot E, et al. High-Dose Vitamin D in Clinically Isolated Syndrome Typical of Multiple Sclerosis: The D-Lay MS Randomized Clinical Trial. *JAMA*. 2025. PMID:40063041 · [doi:10.1001/jama.2025.1604](https://doi.org/10.1001/jama.2025.1604)

---

## Claim 4 — Microglial activation

> The MS gene set is enriched for GO "microglial cell activation" (4/20, 18-fold, FDR 2.6e-4) and "macrophage differentiation" (4/16, 22-fold).

**Concordance: SUPPORTED.**

This recapitulates one of the headline findings of the 2019 genomic map, which reported enrichment of MS susceptibility genes in expression profiles of purified human microglia and concluded these brain-resident immune cells may help target the autoimmune process to the CNS. On the pathology side, MRI-informed single-nucleus RNA-seq of the rim of chronic active ("paramagnetic rim") lesions defined a "microglia inflamed in MS" (MIMS) state with neurodegenerative transcriptional programming, and identified C1q as a critical mediator whose blockade improved chronic EAE. The current mechanistic framework for MS progression explicitly attributes non-relapsing disability accrual to compartmentalised, innate-immune-driven "smouldering" inflammation rather than to new focal relapses. The KG claim is therefore aligned with, not ahead of, the field.

- International Multiple Sclerosis Genetics Consortium. Multiple sclerosis genomic map implicates peripheral immune cells and microglia in susceptibility. *Science*. 2019. PMID:31604244 · [doi:10.1126/science.aav7188](https://doi.org/10.1126/science.aav7188)
- Absinta M, et al. A lymphocyte-microglia-astrocyte axis in chronic active multiple sclerosis. *Nature*. 2021. PMID:34497421 · [doi:10.1038/s41586-021-03892-7](https://doi.org/10.1038/s41586-021-03892-7)
- Kuhlmann T, et al. Multiple sclerosis progression: time for a new mechanism-driven framework. *Lancet Neurol*. 2023. PMID:36410373 · [doi:10.1016/S1474-4422(22)00289-7](https://doi.org/10.1016/S1474-4422%2822%2900289-7)

---

## Claim 5 — Peripheral blood interferon signature

> In Gene Expression Atlas MS contrasts, DE enrichment is overwhelmingly type I / type II interferon signalling, antiviral response and ISG15/OAS mechanisms across CD4, CD8, B cells, monocytes, neutrophils and whole blood, both before and after IFN-beta treatment.

**Concordance: PARTIALLY SUPPORTED** — the signature is real and well documented, but the KG's contrast design conflates two different things.

An endogenous type I IFN signature in peripheral blood is established in a **subset** of MS patients independent of treatment: whole-blood microarray profiling of untreated RRMS defined a subgroup (roughly half of patients) with an activated immune-defence/"virus response" transcriptional programme. That signature has a specific, replicated clinical meaning — high baseline type I IFN-induced gene expression in monocytes, with elevated pSTAT1 and IFNAR1, marks patients who respond **poorly** to interferon beta. However, in cohorts sampled *after* IFN-beta exposure the ISG/OAS/ISG15 signal is dominated by the pharmacodynamic effect of the drug itself. The KG's observation that the same interferon modules appear "both before and after IFN-beta treatment" is consistent with the literature, but the KG as constructed cannot separate treatment effect from endogenous disease biology; the biologically informative reading (a response-predictive endogenous IFN subtype) requires treatment-naive stratification that the federation does not currently expose.

- van Baarsen LG, et al. A subtype of multiple sclerosis defined by an activated immune defense program. *Genes Immun*. 2006. PMID:16837931 · [doi:10.1038/sj.gene.6364324](https://doi.org/10.1038/sj.gene.6364324)
- Comabella M, et al. A type I interferon signature in monocytes is associated with poor response to interferon-beta in multiple sclerosis. *Brain*. 2009. PMID:19741051 · [doi:10.1093/brain/awp228](https://doi.org/10.1093/brain/awp228)

---

## Claim 6 — Epstein-Barr virus

> The NIAID Data Ecosystem KG links MS to EBV (NCBI taxid 10376) via GEO dataset GSE221624, "Unstable EBV latency drives inflammation in multiple sclerosis patient derived spontaneous B cells". Is EBV now regarded as a necessary/near-necessary cause of MS?

**Concordance: SUPPORTED** (for the underlying biology), **with a provenance caveat about the specific KG edge.**

The key large-cohort study is the US military serology cohort: among >10 million young adults on active duty, 955 of whom developed MS, EBV seroconversion raised MS risk **32-fold**, with no comparable effect for other viruses including the similarly transmitted cytomegalovirus, and serum neurofilament light rose only after EBV seroconversion. The authors concluded EBV is "the leading cause of MS", and near-universal EBV seropositivity in MS supports a necessary-but-not-sufficient causal model. A plausible molecular mechanism followed weeks later: high-affinity molecular mimicry between EBNA1 and the CNS protein GlialCAM, with structural and in vivo validation. The field-level synthesis in *Nature Reviews Microbiology* treats EBV as a prerequisite risk factor.

**Caveat on the KG edge specifically:** GSE221624 corresponds to Soldan et al., a mechanistic study of spontaneous lymphoblastoid cell lines showing dysregulated EBV latency and increased lytic gene expression in MS-derived B cells (PMID 36778367, a *Research Square* preprint, [DOI](https://doi.org/10.21203/rs.3.rs-2398872/v1)). It supports the mechanism but is **not** the epidemiological evidence base. The federation's MS–EBV link therefore rests on a weaker, non-peer-reviewed source than the field's decisive evidence, which is not represented in the KG at all.

- Bjornevik K, et al. Longitudinal analysis reveals high prevalence of Epstein-Barr virus associated with multiple sclerosis. *Science*. 2022. PMID:35025605 · [doi:10.1126/science.abj8222](https://doi.org/10.1126/science.abj8222)
- Lanz TV, et al. Clonally expanded B cells in multiple sclerosis bind EBV EBNA1 and GlialCAM. *Nature*. 2022. PMID:35073561 · [doi:10.1038/s41586-022-04432-7](https://doi.org/10.1038/s41586-022-04432-7) — full-text-verified ([PMC9382663](https://pmc.ncbi.nlm.nih.gov/articles/PMC9382663/))
- Soldan SS, et al. Epstein-Barr virus and multiple sclerosis. *Nat Rev Microbiol*. 2023. PMID:35931816 · [doi:10.1038/s41579-022-00770-5](https://doi.org/10.1038/s41579-022-00770-5)

---

## Claim 7 — Latitude gradient

> Joining spoke-okn IHME GBD-2019 MS prevalence for 200 countries to Wikidata country centroids gives Spearman rho = 0.836 (p = 2e-53) between |latitude| and MS prevalence; median prevalence rises ~40-fold from 3.1/100,000 at 0-10 degrees to 125/100,000 at 50-60 degrees, holding separately in both hemispheres.

**Concordance: SUPPORTED**, with important methodological caveats that the KG analysis should state.

The gradient is one of the most robust findings in MS epidemiology. A meta-regression of 650 prevalence estimates from 321 studies found a significant positive association between age-standardised prevalence and latitude (1.04 per degree, p < 0.001; 2.60 per degree after adjusting for prevalence year), with the Italian and northern Scandinavian exceptions explained by HLA-DRB1 allele distribution and behavioural/cultural variation; crucially, the European gradient **persisted after adjustment for HLA-DRB1 allele frequencies**, arguing for latitude-varying environmental factors (UVR/vitamin D). The 2019 update (880 prevalence points) confirmed the gradient and found it had **increased** over time (5.27/100,000 per degree; 4.34 age-standardised), persisting after adjustment for ascertainment method. Global prevalence itself continues to rise (Atlas of MS, 3rd edition).

**Criticisms and confounders to report honestly:** (i) *Ascertainment* — prevalence and incidence surveys are affected by diagnostic accuracy, ascertainment completeness and survival, and a major review argued these sources of error challenge the latitudinal gradient in Europe and North America while it remained apparent for Australia/New Zealand; (ii) *Ancestry* — HLA-DRB1*15:01 frequency itself varies with latitude, so genetics and environment are collinear at country level; (iii) *Ecological design* — a country-centroid join is an ecological analysis, and IHME GBD prevalence figures are **modelled** estimates that borrow strength across geographies, so part of rho = 0.836 reflects model structure and health-system data availability rather than independent measurement; (iv) *Mechanism* — the two leading explanations (UVR/vitamin D, see Claim 3; and EBV/infection-timing, see Claim 6) are not separable from country-level data.

- Simpson S Jr, et al. Latitude is significantly associated with the prevalence of multiple sclerosis: a meta-analysis. *J Neurol Neurosurg Psychiatry*. 2011. PMID:21478203 · [doi:10.1136/jnnp.2011.240432](https://doi.org/10.1136/jnnp.2011.240432)
- Simpson S Jr, et al. Latitude continues to be significantly associated with the prevalence of multiple sclerosis: an updated meta-analysis. *J Neurol Neurosurg Psychiatry*. 2019. PMID:31217172 · [doi:10.1136/jnnp-2018-320189](https://doi.org/10.1136/jnnp-2018-320189)
- Koch-Henriksen N, et al. The changing demographic pattern of multiple sclerosis epidemiology. *Lancet Neurol*. 2010. PMID:20398859 · [doi:10.1016/S1474-4422(10)70064-8](https://doi.org/10.1016/S1474-4422%2810%2970064-8)
- Walton C, et al. Rising prevalence of multiple sclerosis worldwide: Insights from the Atlas of MS, third edition. *Mult Scler*. 2020. PMID:33174475 · [doi:10.1177/1352458520970841](https://doi.org/10.1177/1352458520970841)

---

## Claim 8 — Biomarkers: NfL and oligoclonal bands are the clinically dominant markers

> BiomarkerKB gives 373 MS biomarkers dominated by "indicates risk of developing" dbSNP entries plus CSF/serum analytes including decreased urate and increased quinolinic acid; NfL and OCB were NOT retrievable from the federation.

**Concordance: SUPPORTED** — NfL and OCB are indeed the clinically dominant MS biomarkers, so their absence is a genuine KG coverage gap, not an absence of knowledge.

**Oligoclonal bands** are embedded in the diagnostic standard: the 2017 McDonald criteria allow CSF-specific OCBs to substitute for dissemination in time in a typical clinically isolated syndrome. A meta-analysis of 71 studies (12,253 MS and 2,685 CIS patients) found OCBs in 87.7% of MS and 68.6% of CIS, with OCB-positive CIS patients carrying an odds ratio of 9.88 for conversion to MS (and, notably for Claim 7, OCB prevalence itself varies with latitude). **Neurofilament light chain** is the dominant fluid biomarker of neuroaxonal injury; the reference-database study of 10,133 control and 7,769 MS samples showed that age- and BMI-adjusted sNfL Z-scores above 1.5 predict future clinical/MRI activity even in patients classed as having no evidence of disease activity (OR 3.15), validated in an independent Swedish registry cohort. NfL is also the biomarker that carried the EBV causal argument (Claim 6).

On the KG's own analytes: **decreased urate** in MS is a real and replicated observational finding, but Mendelian randomisation does **not** support a causal effect of serum urate on MS risk (pooled OR 1.05, 95% CI 0.92-1.19) or of MS on urate — so BiomarkerKB's urate entry should be read as a correlate, not a mechanism. I did not find, and therefore do not assert, a comparable large-cohort or MR-level source for increased quinolinic acid; that entry remains **NOVEL-OR-UNVERIFIED** at the level of evidence checked here.

- Thompson AJ, et al. Diagnosis of multiple sclerosis: 2017 revisions of the McDonald criteria. *Lancet Neurol*. 2018. PMID:29275977 · [doi:10.1016/S1474-4422(17)30470-2](https://doi.org/10.1016/S1474-4422%2817%2930470-2)
- Dobson R, et al. Cerebrospinal fluid oligoclonal bands in multiple sclerosis and clinically isolated syndromes: a meta-analysis of prevalence, prognosis and effect of latitude. *J Neurol Neurosurg Psychiatry*. 2013. PMID:23431079 · [doi:10.1136/jnnp-2012-304695](https://doi.org/10.1136/jnnp-2012-304695)
- Benkert P, et al. Serum neurofilament light chain for individual prognostication of disease activity in people with multiple sclerosis: a retrospective modelling and validation study. *Lancet Neurol*. 2022. PMID:35182510 · [doi:10.1016/S1474-4422(22)00009-6](https://doi.org/10.1016/S1474-4422%2822%2900009-6)
- Khalil M, et al. Neurofilaments as biomarkers in neurological disorders. *Nat Rev Neurol*. 2018. PMID:30171200 · [doi:10.1038/s41582-018-0058-z](https://doi.org/10.1038/s41582-018-0058-z)
- Niu PP, et al. Serum Uric Acid Level and Multiple Sclerosis: A Mendelian Randomization Study. *Front Genet*. 2020. PMID:32292418 · [doi:10.3389/fgene.2020.00254](https://doi.org/10.3389/fgene.2020.00254)

---

## Claim 9 — Therapeutics: subtype assignment and target wiring

> RDKG assigns the standard DMTs to RRMS and puts BTK inhibitors (tolebrutinib, remibrutinib, fenebrutinib) on progressive/pediatric MS. ProKN target wiring: fingolimod/siponimod/ozanimod/ponesimod -> S1PR1/3/4/5; teriflunomide -> DHODH; dimethyl fumarate -> KEAP1; ocrelizumab/ofatumumab/rituximab -> MS4A1; mitoxantrone -> TOP2A; dalfampridine -> KCNA/KCNB.

**Concordance: PARTIALLY SUPPORTED.** Most target assignments are correct; the S1P receptor selectivity is over-broad, and the BTK-inhibitor subtype assignment is only correct for tolebrutinib.

*Targets that are right:* teriflunomide -> DHODH, dimethyl fumarate -> KEAP1 (the electrophilic target whose modification releases NRF2), anti-CD20 antibodies -> MS4A1, mitoxantrone -> TOP2A, and dalfampridine (4-aminopyridine) -> voltage-gated Kv channels (KCNA/KCNB/KCNC/KCND families in the extracted table) are all standard, correct pharmacology.

*Target that is over-assigned:* the S1P modulators are not interchangeable. The primary mechanism of the whole class is S1PR1 binding, internalisation and loss of the S1P gradient driving lymphocyte egress from lymph nodes — but the second-generation agents are receptor-**selective**: siponimod and ozanimod act on S1P1 and S1P5, and ponesimod is S1P1-selective, whereas fingolimod-phosphate is the broad agent binding S1P1, S1P3, S1P4 and S1P5. The federation's table assigns S1PR3/S1PR4 to siponimod and ponesimod and additionally S1PR2 to ozanimod, which is **not** supported. Teriflunomide -> DHFR in the same table is likewise a weak off-target, not the therapeutic mechanism.

*Subtype assignment is wrong for two of the three BTK inhibitors.* Only tolebrutinib has a positive progressive-MS readout: in the phase 3 HERCULES trial in **non-relapsing secondary progressive MS** (1,131 participants), 6-month confirmed disability progression occurred in 22.6% vs 30.7% on placebo (HR 0.69, p = 0.003), at the cost of ALT elevations >3x ULN in 4.0% vs 1.6%. In **relapsing** MS the same drug missed: in GEMINI 1 and 2 (1,873 participants) tolebrutinib was not superior to teriflunomide on annualised relapse rate (rate ratios 1.06 and 1.00), though pooled 6-month confirmed disability worsening favoured tolebrutinib (8.3% vs 11.3%). Fenebrutinib and remibrutinib are being developed **principally in relapsing MS** — fenebrutinib's phase 2 FENopta trial in relapsing MS showed a 69% relative reduction in new T1 Gd+ lesions, and its registry record (NCT05119569) is a relapsing-MS study; remibrutinib's phase 3 programme (REMODEL I/II) is in relapsing MS. Fenebrutinib does additionally have a primary-progressive programme (FENtrepid). Evobrutinib, the other class member, **failed** its phase 3 relapsing-MS trials. A 2026 review by the HERCULES lead investigator summarises the current position: tolebrutinib has shown efficacy against disability progression in non-relapsing SPMS while fenebrutinib "has recently shown promise in both relapsing and primary progressive MS", with hepatotoxicity the class-limiting risk.

**Explicitly unverified:** results for tolebrutinib's PPMS trial (PERSEUS) and fenebrutinib's FENtrepid have been reported at conferences and in sponsor communications and are discussed in review articles, and the current regulatory approval status of any BTK inhibitor in MS could not be confirmed from a peer-reviewed primary source in this search. I therefore do not assert either outcome or any approval status here. I also found **no** peer-reviewed trial evidence for BTK inhibitors in **pediatric** MS; the RDKG pediatric-MS assignment appears to be an ontology-propagation artefact.

- Fox RJ, et al. Tolebrutinib in Nonrelapsing Secondary Progressive Multiple Sclerosis. *N Engl J Med*. 2025. PMID:40202696 · [doi:10.1056/NEJMoa2415988](https://doi.org/10.1056/NEJMoa2415988)
- Oh J, et al. Tolebrutinib versus Teriflunomide in Relapsing Multiple Sclerosis. *N Engl J Med*. 2025. PMID:40202623 · [doi:10.1056/NEJMoa2415985](https://doi.org/10.1056/NEJMoa2415985)
- FENopta Study Group. Safety and efficacy of fenebrutinib in relapsing multiple sclerosis (FENopta): a multicentre, double-blind, randomised, placebo-controlled, phase 2 trial and open-label extension study. *Lancet Neurol*. 2025. PMID:40683275 · [doi:10.1016/S1474-4422(25)00174-7](https://doi.org/10.1016/S1474-4422%2825%2900174-7)
- Lambe J, et al. Bruton's Tyrosine Kinase Inhibitors in Multiple Sclerosis. *Drugs*. 2026. PMID:42126690 · [doi:10.1007/s40265-026-02324-y](https://doi.org/10.1007/s40265-026-02324-y)
- McGinley MP, et al. Sphingosine 1-phosphate receptor modulators in multiple sclerosis and other conditions. *Lancet*. 2021. PMID:34175020 · [doi:10.1016/S0140-6736(21)00244-0](https://doi.org/10.1016/S0140-6736%2821%2900244-0)

---

## Claim 10 — Negative/gap claim: adult MS has no HPO phenotype annotation in the federation

> oard-kg returns HP terms only for pediatric MS (209) and Marburg acute MS (2), and those look like EHR co-occurrence artefacts (otitis media, microcephaly, polyuria, high palate) rather than MS clinical phenotypes. Is the canonical MS phenotype set well established, i.e. is this a KG coverage gap?

**Concordance: SUPPORTED** — this is a knowledge-graph coverage gap, not an absence of clinical knowledge.

The MS clinical phenotype is textbook-level established and codified in guidelines. Standard reviews describe the characteristic syndromes — optic neuritis, internuclear ophthalmoplegia and other brainstem/oculomotor syndromes, partial myelitis with Lhermitte sign, spasticity, cerebellar ataxia, neurogenic bladder, fatigue and heat-sensitivity (Uhthoff phenomenon) — and the diagnostic criteria are explicitly built on clinically isolated syndromes of exactly these kinds (supratentorial, infratentorial and spinal cord syndromes, with a research call-out for optic nerve involvement). Progressive disability accrual independent of relapses is likewise a defined clinical construct. Inspection of the federation's phenotype export confirms the gap: the only rows retrieved for MS subtypes are `Non-Mendelian inheritance` and `Embryonal onset` (rdkg, Marburg acute MS) and oard-kg terms such as `Polyuria`, `Hydronephrosis` and `High palate` for pediatric MS — i.e. EHR co-occurrence statistics, not curated disease phenotypes. **Adult MS (the main MONDO term) carries no HPO annotation at all.** This should be reported as a federation limitation with the canonical phenotype list supplied from the clinical literature.

- Reich DS, et al. Multiple Sclerosis. *N Engl J Med*. 2018. PMID:29320652 · [doi:10.1056/NEJMra1401483](https://doi.org/10.1056/NEJMra1401483)
- Thompson AJ, et al. Diagnosis of multiple sclerosis: 2017 revisions of the McDonald criteria. *Lancet Neurol*. 2018. PMID:29275977 · [doi:10.1016/S1474-4422(17)30470-2](https://doi.org/10.1016/S1474-4422%2817%2930470-2)
- Kuhlmann T, et al. Multiple sclerosis progression: time for a new mechanism-driven framework. *Lancet Neurol*. 2023. PMID:36410373 · [doi:10.1016/S1474-4422(22)00289-7](https://doi.org/10.1016/S1474-4422%2822%2900289-7)

---

## Where the KG evidence diverges from the literature

**Direct contradictions / errors in the KG**

1. **S1P receptor selectivity is over-assigned (Claim 9).** ProKN gives siponimod and ponesimod S1PR3/S1PR4 and ozanimod S1PR2/3/4. Published pharmacology makes siponimod and ozanimod S1P1/S1P5-selective and ponesimod S1P1-selective; only fingolimod is genuinely broad (S1P1/3/4/5). Any repurposing inference built on shared S1PR3/4 targets is unsound.
2. **BTK inhibitors are not "progressive/pediatric MS" drugs as a class (Claim 9).** Only tolebrutinib has a positive progressive-MS phase 3 result (HERCULES, nrSPMS); it *missed* its relapsing-MS primary endpoint (GEMINI). Remibrutinib and fenebrutinib are principally in relapsing-MS programmes. No peer-reviewed pediatric-MS BTK trial evidence was found — that RDKG edge looks like ontology propagation.
3. **Teriflunomide -> DHFR** appears alongside DHODH in the extracted target table; DHFR is a weak off-target and not the mechanism of action.
4. **Entity-resolution noise in the drug layer.** The extracted ProKN/RDKG drug table names several MS-indicated agents only as opaque CHEMBL/SID identifiers (MS4A1, KEAP1 and ITGA4 targets are present but not attached to readable drug names), while `Dimethyl Ether` is carried as an MS-indicated chemical — almost certainly a name collision with dimethyl fumarate. Alemtuzumab and glatiramer acetate resolve with **zero** targets. Drug-target counts from this layer should not be quoted without manual curation.

**Pathway claims that survive as biology but fail as therapeutic inference**

5. **IL-12/IL-23 signalling (Claim 2)** is enriched in the KG's Reactome result, but ustekinumab (anti-p40) was tested in RRMS and showed no effect on gadolinium-enhancing lesions. Genetic/pathway enrichment is not drug-target validation.
6. **JAK-STAT (Claim 2)** is the KG's single strongest GO term and is genuinely core MS biology, but there is no approved or late-phase JAK inhibitor for MS; the IL-2R arm was drugged (daclizumab) and then withdrawn for toxicity. The "BTK/JAK inhibitors follow from JAK-STAT enrichment" narrative should be rewritten: BTK sits on BCR/Fc-receptor/TLR signalling, not JAK-STAT.

**Notable coverage gaps in the federation**

7. **No NfL, no oligoclonal bands (Claim 8).** The two biomarkers that actually drive MS diagnosis and prognosis in clinical practice are absent from BiomarkerKB's 373 MS entries, which are dominated by dbSNP "indicates risk of developing" rows. This is a large, reportable gap.
8. **No adult-MS phenotype annotation (Claim 10).** The canonical semiology is entirely absent; what is present (otitis media, microcephaly, polyuria, high palate on *pediatric* MS) is EHR co-occurrence noise that could mislead downstream phenotype-similarity analyses.
9. **The MS–EBV edge rests on a preprint (Claim 6).** GSE221624 maps to a *Research Square* preprint on B-cell EBV latency. The decisive evidence — the 10-million-person military serology cohort showing a 32-fold risk increase, and the EBNA1/GlialCAM mimicry work — is not represented in the federation.
10. **Interferon contrasts conflate drug effect with disease biology (Claim 5).** GXA MS contrasts include IFN-beta-treated cohorts; without treatment-naive stratification the "interferon signature" cannot be interpreted mechanistically.
11. **The latitude analysis is ecological and partly circular (Claim 7).** IHME GBD country prevalence is modelled, and country centroids ignore within-country population distribution, ancestry (HLA-DRB1 frequency) and ascertainment intensity. The correlation is real and matches the meta-analytic literature, but rho = 0.836 should not be presented as an independent confirmation.

**Where the KG adds nothing new**

12. Claims 1, 3, 4, 6 and 7 all recover findings that are already canonical (2011-2022 IMSGC genetics; CYP27B1/vitamin D Mendelian randomisation; microglial enrichment — which is literally in the title of the 2019 *Science* paper; EBV; the latitude gradient). The value of the multi-KG analysis here is **convergent reproduction across independent resources**, plus the explicit statistical framing (hypergeometric test with a declared ProKN background), not novel discovery. No claim examined was **CONTRADICTED** at the level of core biology, and only one item — the BiomarkerKB analyte "increased quinolinic acid" — is left **NOVEL-OR-UNVERIFIED**, because no corroborating large-cohort or causal-inference source was found in this search.

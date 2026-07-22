# Literature verification of the T2D federated-KG study findings

**Method.** Each finding below was checked against the published literature using PubMed
(NCBI E-utilities) and the Paperclip full-text corpus (PubMed Central / bioRxiv / medRxiv,
clinical-trial and regulatory collections). Central claims were verified against article full
text where available (e.g. the loci list in Suzuki *Nature* 2024 was grepped directly; the
rural–urban adjustment result was read from the Khavjou *Prev Chronic Dis* 2025 full text).
Citations are formatted `Author et al., Journal Year, PMID:xxxxxxxx`. Where no evidence was
found this is stated explicitly as **"no supporting citation found"** — no citation in this
document is inferred or reconstructed from memory.

Classification key:
- **SUPPORTED** — the finding reproduces an established, independently published result.
- **NOVEL / UNDER-STUDIED** — plausible and consistent with adjacent biology, but no direct
  published evidence for the specific claim; treat as hypothesis-generating.
- **CONTRADICTED** — published evidence points the other way.

---

## A. Consensus gene core

### A1. Tier-A consensus genes are established T2D genes — **SUPPORTED**

The bulk of the Tier-A list (TCF7L2, PPARG, KCNJ11, ABCC8, SLC30A8, IGF2BP2, HNF1A, HNF1B,
HNF4A, GCK, FTO, IRS1, ADCY5, HMGA2, JAZF1, ZMIZ1) is directly recoverable from the two
largest T2D genetic studies. The gene-name list in the Suzuki 2024 multi-ancestry meta-analysis
full text was checked directly and contains TCF7L2, HNF1B, KCNJ11, ABCC8, HNF4A, HNF1A, GCK,
FTO, IRS1, PPARG, SLC30A8, ZMIZ1, HMGA2, IGF2BP2, JAZF1 and CAMK1D.

- Suzuki K et al., *Nature* 2024, PMID:38374256
- Mahajan A et al., *Nature Genetics* 2018, PMID:30297969

### A2. Monogenic / MODY subset (GCK, HNF1A, HNF4A, HNF1B, PDX1, INS, ABCC8, KCNJ11, WFS1) — **SUPPORTED**

These are canonical monogenic-diabetes genes that also carry common T2D risk signals; the
Mahajan fine-mapping paper explicitly highlights coding-variant-attributable signals at such
genes, and Suzuki 2019 shows "monogenic diabetes" as an enriched pathway in T2D GWAS.

- Mahajan A et al., *Nature Genetics* 2018, PMID:30297969
- Suzuki K et al., *Nature Genetics* 2019, PMID:30718926

### A3. **CASR** — **NOVEL / UNDER-STUDIED**

CASR has genuine, well-described β-cell biology (regulation of insulin exocytosis, cell–cell
adhesion and coupling in islets, and increased islet expression under compensatory secretory
demand), but it is **not** an established T2D GWAS locus and no genome-wide T2D association is
reported for it. Its Tier-A rank is best read as mechanistic/curation-driven, not genetic.

- Squires PE et al., *Vitamins and Hormones* 2014, PMID:24559921
- Oh YS et al., *PLoS ONE* 2016, PMID:27441644

### A4. **BRAF** — **NOVEL / UNDER-STUDIED (probable KG hub artefact)**

No supporting citation found linking BRAF to type 2 diabetes risk or β-cell/insulin
physiology. BRAF does not appear in the Suzuki 2024 loci list. BRAF is an extremely
high-degree node in most biomedical KGs (oncology curation), so a high cross-KG agreement
score for BRAF most likely reflects graph topology rather than T2D biology. **Recommend
demoting or annotating as a hub-bias candidate.**

### A5. **RPS6KB1 (S6K1)** — **SUPPORTED (mechanistic), not a T2D risk locus**

S6K1 is a well-established node of nutrient-driven insulin resistance: loss of S6K1 in mice
improves glucose tolerance and reduces muscle oxidative stress, phenocopying endurance
exercise. Note this is mechanistic/mTOR-axis support, not genetic association — RPS6KB1 does
not appear in the Suzuki 2024 T2D loci list.

- Binsch C et al., *Molecular Metabolism* 2017, PMID:29107291

### A6. **BCL2** — **SUPPORTED (mechanistic), not a T2D risk locus**

BCL2-family control of β-cell apoptosis and ER-stress-induced β-cell death is a large,
well-established literature (>300 PubMed records for BCL2 + β-cell + apoptosis + diabetes).
Same caveat as RPS6KB1: mechanistic, not a genetic T2D signal.

- Danilova T & Lindahl M, *Frontiers in Physiology* 2018, PMID:30386256 (β-cell ER stress / apoptosis context)
- Hakonen E et al., *Diabetologia* 2018, PMID:30032427

### A7. **ZMIZ1** — **SUPPORTED**

ZMIZ1 is present in the T2D locus list of the Suzuki 2024 multi-ancestry meta-analysis
(verified in full text).

- Suzuki K et al., *Nature* 2024, PMID:38374256

### A8. **JAZF1** — **SUPPORTED**

JAZF1 is a long-established T2D locus (originally from the DIAGRAM-era GWAS) and appears in
the Suzuki 2024 locus list (verified in full text).

- Suzuki K et al., *Nature* 2024, PMID:38374256
- Mahajan A et al., *Nature Genetics* 2018, PMID:30297969

### A9. **POC5** — **NOVEL / UNDER-STUDIED**

No supporting citation found for a POC5–T2D link. POC5 is primarily reported in
height/idiopathic-scoliosis genetics. Not present in the Suzuki 2024 loci list.

### A10. **ANKH** — **NOVEL / UNDER-STUDIED — and check for a symbol-mapping error**

No supporting citation found for ANKH (progressive ankylosis protein homolog, pyrophosphate
transporter) in T2D. **Important caveat: ANK1 — a different gene — *is* an established T2D
locus** (the NKX6-3/ANK1 cluster carries T2D GWAS variants). If ANKH entered the consensus
list via a symbol crosswalk, verify it is not an ANK1 mis-mapping.

- Chalhoub N et al., *bioRxiv (preprint)* 2026, PMID:41509304 (NKX6-3/ANK1 T2D GWAS cluster)

### A11. **TLE1** — **NOVEL / UNDER-STUDIED (paralog substitution likely)**

No direct TLE1–T2D publication found. The T2D-annotated Groucho/TLE family member in the
literature is **TLE4** (WNT-signalling annotation, chr9 T2D locus region). As with ANKH,
check whether TLE1 is a paralog/mapping substitution for TLE4.

- Hindy G et al., *Genes & Nutrition* 2016, PMID:27551309 (TLE4 among T2D-associated WNT-annotated genes)

### A12. **KL (klotho)** — **NOVEL / UNDER-STUDIED**

Klotho has emerging diabetes-relevant biology — protection of INS-1 β-cells from senescence,
and a proposed role in diabetic retinopathy — but it is not an established T2D susceptibility
gene and the evidence base is small.

- Wang Z et al., *Frontiers in Aging* 2025, PMID:40018267
- Puddu A et al., *World Journal of Diabetes* 2023, PMID:37547589

### A13. **SLC16A11** — **SUPPORTED**

The SLC16A11 risk haplotype is a well-replicated T2D locus first found in Mexican/Latino
populations and replicated in the Mexican-origin stratum of HCHS/SOL (with explicit failure to
replicate in non-Mexican Hispanic/Latino groups — a genuine ancestry-specific effect).

- Hidalgo BA et al., *Scientific Reports* 2019, PMID:30696834

### A14. **SLC16A13** — **NOVEL / UNDER-STUDIED**

Only sparse evidence: a single reported variant association (rs312457) and characterisation of
the transporter (MCT13) as a ketone-body transporter. It is adjacent to SLC16A11 on 17p13, so
the KG signal may be linkage/annotation spillover from the SLC16A11 locus.

- Zheng H et al., *Computational and Mathematical Methods in Medicine* 2021, PMID:34257700
- Higuchi K et al., *Nutrients* 2023, PMID:37630718

### A15. **ERO1B** — **NOVEL / UNDER-STUDIED**

ERO1B (ERO1β) is an islet/β-cell-enriched oxidoreductase relevant to proinsulin disulphide
folding and appears in recent single-cell islet transcriptomic profiling, but there is no
established T2D genetic association and the literature is very thin (<10 PubMed records for
ERO1B + diabetes).

- Grenko CM et al., *Diabetologia* 2024, PMID:38967666

### A16. **GP2** — **SUPPORTED**

A GP2 missense variant with a Japanese-enriched allele frequency was identified as a novel T2D
signal in the Japanese GWAS meta-analysis (36,614 cases / 155,150 controls), alongside a GLP1R
missense variant. GP2 also appears in the Suzuki 2024 full text.

- Suzuki K et al., *Nature Genetics* 2019, PMID:30718926
- Zhang T et al., *Frontiers in Endocrinology* 2021, PMID:34326813

### A17. **MANF** — **SUPPORTED (mechanistic)**

MANF deficiency causes diabetes in mice through ER stress, β-cell death and impaired β-cell
proliferation, and exogenous MANF protects human β-cells against cytokine- and ER-stress-induced
death. Strong β-cell biology; not a T2D GWAS locus.

- Danilova T & Lindahl M, *Frontiers in Physiology* 2018, PMID:30386256
- Hakonen E et al., *Diabetologia* 2018, PMID:30032427

---

## B. Pathway / mechanism result

### B1. Core GO/Reactome hits are the canonical T2D mechanisms — **SUPPORTED**

Glucose homeostasis, regulation of insulin secretion (positive and negative), cellular response
to insulin stimulus, insulin receptor signalling, IRS-mediated signalling, PI3K cascade,
PIP3→AKT, FOXO-mediated transcription, glycogen biosynthesis and regulation of gene expression
in β cells are precisely the two axes (β-cell function and insulin action/adiposity) that the
large T2D genetic studies resolve. The negative-regulation-of-fat-cell-differentiation and
white-adipocyte-differentiation hits map onto the PPARG axis.

- Suzuki K et al., *Nature* 2024, PMID:38374256
- Mahajan A et al., *Nature Genetics* 2018, PMID:30297969

### B2. MLL3/MLL4 complexes regulate PPARG target genes — **SUPPORTED**

MLL3/MLL4 (KMT2C/KMT2D) are required for CBP/p300 enhancer binding and super-enhancer formation
during adipogenesis, i.e. they are bona-fide co-activators of the PPARG adipocyte programme.

- Lai B et al., *Nucleic Acids Research* 2017, PMID:28398509
- Lee JE et al., *eLife* 2013, PMID:24368734 (MLL4 required for enhancer activation during adipocyte differentiation)

### B3. **IL-4 / IL-13 signalling (fold 5.3, FDR 7e-7)** — **NOVEL / EMERGING, not a canonical T2D axis**

This is a genuine but non-canonical result. Type-2 (Th2) cytokine signalling is an established
part of obesity-associated immunometabolism — IL-4 improves insulin sensitivity and drives
adipose browning, IL-13 acts on muscle energy metabolism and systemic glucose control, adipose
eosinophil/IL-4 tone is reduced in human insulin resistance, and hyperinsulinaemia suppresses
macrophage IRS2 to blunt IL-4-driven M2a polarisation. However, IL-4/IL-13 is **not** a pathway
that standard T2D GWAS enrichment recovers, so this should be reported as an
**under-recognised axis surfaced by the federated analysis**, worth flagging.

- Méndez-García LA et al., *Biomedicines* 2025, PMID:41007770
- Hernandez JD et al., *JCI Insight* 2024, PMID:38206766
- Kubota T et al., *Nature Communications* 2018, PMID:30451856

### B4. **Positive regulation of cold-induced thermogenesis (fold 6.9)** — **SUPPORTED as biology, NOVEL as a T2D enrichment result**

Brown-adipose/cold-induced thermogenesis is causally linked to whole-body glucose disposal and
insulin sensitivity in humans (cold-activated BAT improves whole-body glucose homeostasis and
insulin sensitivity; cold acclimation reversibly increases BAT activity and improves insulin
sensitivity). But, like IL-4/IL-13, it is not a term that appears in canonical T2D gene-set
enrichments, so its appearance here is a distinctive result of the ProKN GO background.

- Chondronikola M et al., *Diabetes* 2014, PMID:25056438
- Lee P et al., *Diabetes* 2014, PMID:24954193

### B5. Cholesterol homeostasis / cellular response to hypoxia

**Not separately verified.** Cholesterol homeostasis is plausible given the well-documented
lipid–glycaemia interface (see G1: LDL-lowering by statins raises incident diabetes), and
adipose-tissue hypoxia is an established obesity mechanism, but neither term was checked
against a primary source in this pass. Treat as unverified rather than supported.

---

## C. Islet single-cell / chromatin result

### C1. Islet inflammation is increased in T2D (LIF, CXCL8, CCL20, IL1B, CXCL1, MMP3, ICAM1 up) — **SUPPORTED**

Islet inflammation in T2D — IL-1β-driven, with chemokine induction and macrophage involvement —
is a mature literature. Recent work also shows islet-macrophage signalling (FFAR4→IL-6) is
specifically compromised in T2D.

- Böni-Schnetzler M & Meier DT, *Seminars in Immunopathology* 2019, PMID:30989320
- Chen X et al., *Nature Communications* 2025, PMID:40210633

### C2. β-cell dedifferentiation / loss of identity in T2D — **SUPPORTED**

- Hunter CS & Stein RW, *Frontiers in Genetics* 2017, PMID:28424732
- Aigha II & Abdelalim EM, *Stem Cell Research & Therapy* 2020, PMID:33121533 (NKX6.1 as identity regulator)

### C3. SLC2A2 (GLUT2) down in T2D islets — **SUPPORTED**

Loss of GLUT2/SLC2A2 in diabetic islets is part of the classical dedifferentiation/identity-loss
signature, and cell-type-resolved islet expression maps show disease-associated expression
changes concentrated in β cells.

- Hunter CS & Stein RW, *Frontiers in Genetics* 2017, PMID:28424732
- Elgamal RM et al., *Diabetes* 2023, PMID:37582230

### C4. NKX6-3 down in T2D islets — **SUPPORTED (locus-level), plausible (expression-level)**

The NKX6-3/ANK1 cluster carries T2D GWAS variants and is being functionally dissected in hiPSC
models; the closely related NKX6.1 is the canonical β-cell identity factor whose loss defines
dedifferentiation. Direct published evidence for *NKX6-3 transcript down-regulation* in T2D
islets specifically is thin.

- Chalhoub N et al., *bioRxiv (preprint)* 2026, PMID:41509304
- Aigha II & Abdelalim EM, *Stem Cell Research & Therapy* 2020, PMID:33121533

### C5. Chromatin accessibility is altered in T2D islets in a cell-type-specific way — **SUPPORTED**

Bulk ATAC-seq shows T2D alters the islet open-chromatin landscape; single-cell ATAC-seq shows
T2D GWAS variants are enriched in β-cell-specific and shared islet open chromatin; single-cell
multiome and sex-stratified islet atlases confirm cell-type-specific regulatory change in T2D.

- Bysani M et al., *Scientific Reports* 2019, PMID:31123324
- Rai V et al., *Molecular Metabolism* 2020, PMID:32029221
- Qadir MMF et al., *EMBO Journal* 2024, PMID:39567827

### C6. The specific gene-level accessibility calls — **NOVEL / no supporting citation found**

No supporting citation found for reduced β-cell accessibility at **A1CF, RASSF10, TMED6,
ST8SIA4, FOXE1, DACT2**; increased ductal accessibility at **CCDC9, MAP2K7, LMF2, NCF1**;
endothelial **CYP1B1** up; or macrophage **WASF3 / NDUFAF2** down in T2D. TMED6 is at least an
islet/β-cell-enriched gene (PMID:22129529, PMID:35383192) but nothing links its chromatin state
to T2D. These are the most genuinely novel items in the study and should be presented as
hypothesis-generating, ideally with replication in an independent islet snATAC cohort
(HumanIslets, Ewald JD et al. 2024, PMID:38948734, or the Elgamal islet map above).

---

## D. Non-coding RNA layer

### D0. "184 non-coding/lncRNA loci carry T2D risk variants" — **SUPPORTED in principle**

The great majority of T2D GWAS signals are non-coding and regulatory, which is the core premise
of the islet-epigenome fine-mapping work; lncRNA involvement in diabetes is a recognised field
with systematic reviews.

- Mahajan A et al., *Nature Genetics* 2018, PMID:30297969
- Dieter C et al., *Frontiers in Endocrinology* 2021, PMID:33815273
- Leti F & DiStefano JK, *Genes* 2017, PMID:28829354

### D1. **CDKN2B-AS1 (ANRIL)** — **SUPPORTED**

Direct T2D genetic-association evidence, including a recent case–control study reporting the
rs10757278 G allele/GG genotype increasing T2DM risk with serum ANRIL of diagnostic value.

- Li X et al., *Diabetology & Metabolic Syndrome* 2025, PMID:40148977

### D2. **KCNQ1-AS1 / KCNQ1OT1** — **SUPPORTED**

The imprinted KCNQ1 locus and its antisense transcript are among the best-characterised
lncRNA-implicated β-cell/T2D loci; isogenic hiPSC editing at these loci is now used to dissect
the causal variants.

- Kameswaran V & Kaestner KH, *Frontiers in Genetics* 2014, PMID:25071830
- Nair AK et al., *Cells* 2022, PMID:35563754

### D3. **MEG3** — **SUPPORTED**

The imprinted DLK1-MEG3 locus is repeatedly implicated in β-cell lncRNA biology, and MEG3
variants have been associated with diabetic kidney disease and HbA1c in T2D patients.

- Kameswaran V & Kaestner KH, *Frontiers in Genetics* 2014, PMID:25071830
- Ting KH et al., *Diabetology & Metabolic Syndrome* 2024, PMID:39487551

### D4. **HNF1A-AS1** — **NOVEL / UNDER-STUDIED for T2D**

HNF1A-AS1 has a substantial literature, but predominantly in oesophageal/gastric cancer and
mucosal inflammation, not T2D. No supporting citation found for a functional HNF1A-AS1 role in
β-cell failure or insulin resistance. Its presence in the layer is best explained as an
antisense transcript at the HNF1A (MODY3) locus.

### D5. **LINC01122, PROX1-AS1, ADAMTS9-AS2, CCND2-AS1, MIR4435-2HG, SOX2-OT** — **NOVEL / no supporting citation found**

These are antisense/lincRNA transcripts at *bona-fide* T2D GWAS loci (PROX1, ADAMTS9, CCND2 are
established T2D genes), but no published functional T2D evidence was found for the non-coding
transcripts themselves. Report as *positional* non-coding candidates, not as validated effectors.
Genetic regulation of RNA processing in human islets is an appropriate follow-up framework.

- Atla G et al., *Genome Biology* 2022, PMID:36109769

---

## E. Exposure convergence (PFAS)

### E1. A PFAS→T2D / insulin-resistance link is reported epidemiologically — **SUPPORTED, with an important caveat**

Prospective evidence exists: higher plasma PFOS and PFOA were associated with increased T2D risk
in U.S. women; in the Diabetes Prevention Program baseline PFOS/PFOA were associated with worse
insulin resistance and β-cell function (but **not** with diabetes incidence); a 30-year
Norwegian study links PFAS trajectories to T2D status.

**Caveat / partial contradiction:** the most recent systematic review and meta-analysis
concludes that PFAS are most consistently associated with *gestational* diabetes and with
insulin-resistance markers, while **evidence for type 2 diabetes specifically "remains limited"**.
The study's exposure-convergence claim should therefore be stated as *mechanistically coherent
and epidemiologically suggestive*, not as an established causal risk factor.

- Sun Q et al., *Environmental Health Perspectives* 2018, PMID:29498927
- Cardenas A et al., *Environmental Health Perspectives* 2017, PMID:28974480
- India Aldana S et al., *eClinicalMedicine* 2026, PMID:41768983
- Roth K & Petriello MC, *Frontiers in Endocrinology* 2022, PMID:35992116

### E2. PFOS acts on PPARG/PPARA and drives a lipid-dysregulation→steatosis AOP — **SUPPORTED**

PFOS induces both PPARα-dependent and PPARα-independent changes in lipid metabolism,
inflammation and xenobiotic metabolism; PFAS more broadly induce steatosis in liver cells.
This is consistent with AOP 529-type reasoning (PFOS→PPAR→lipid dysregulation→steatosis).

- Rosen MB et al., *PPAR Research* 2010, PMID:20936131
- Attema B et al., *Molecular Metabolism* 2022, PMID:36115532

### E3. The PFOS-vs-PFOA divergence at INSR / GSK3B / PIK3CA — **CONTRADICTED**

The study reports PFOA as **INACTIVE** at INSR, GSK3B and PIK3CA. Published mechanistic work
reports the opposite: PFOA exposure of a human hepatocyte line **uncouples insulin signalling
upstream**, impairing insulin-receptor activation and GLUT4 translocation; PFOA also disrupts
the AKT/GSK3β/β-catenin axis in hepatocytes. The PFOS/PFOA "divergence" is therefore most
plausibly an **assay-coverage artefact of the EPA/NTP ICE (ToxCast) panel** — an *inactive*
call means "not active in the assays run", not "no biological effect" — rather than a real
chemical-specific difference. **Recommend rewording this finding in the report.**

- De Toni L et al., *Frontiers in Endocrinology* 2021, PMID:34539566
- Feng Y et al., *ACS Omega* 2025, PMID:39895706 (PFOA disrupts the AKT/GSK3β/β-catenin axis in hepatocytes)

---

## F. Epidemiology (US county model, n=3,073, R²=0.862)

### F1. The "diabetes belt" pattern — **SUPPORTED**

The diabetes belt is a formally defined CDC construct (644 counties across 15 mostly southern
states), and independent state-level survey analyses put the highest diagnosed prevalence in
Southern and Appalachian states — consistent with the study's Mississippi / South Carolina /
Georgia / Louisiana / West Virginia top ranking and Massachusetts / Colorado / Vermont /
New Hampshire bottom ranking (Colorado is the lowest-prevalence state in both rural and urban
strata of the 2021 BRFSS analysis).

- Barker LE et al., *American Journal of Preventive Medicine* 2011, PMID:21406277
- Danaei G et al., *Population Health Metrics* 2009, PMID:19781056
- Khavjou O et al., *Preventing Chronic Disease* 2025, PMID:39819894

### F2. Poverty, physical inactivity, low education, uninsurance and food access as county-level predictors — **SUPPORTED**

County-level analyses consistently identify poverty/income, physical inactivity, obesity and
education as the dominant correlates of diabetes prevalence; food insecurity is associated with
higher diabetes rates, especially in the southern US; neighbourhood socioeconomic disadvantage
predicts prevalent diabetes in both urban and rural strata.

- Hipp JA & Chalise N, *Preventing Chronic Disease* 2015, PMID:25611797
- Alemi F et al., *Cureus* 2023, PMID:37905243
- Uddin J et al., *SSM - Population Health* 2022, PMID:35295743

### F3. Short sleep (<7 h) as an independent risk factor — **SUPPORTED (at individual level); population-level extension is an extrapolation**

Short sleep duration is an established independent predictor of incident T2D in prospective
meta-analyses (RR ≈ 1.3 for <5–6 h/night), confirmed in updated meta-analyses and in large
cohort analyses showing the risk is not offset by a healthy diet. Note that all of this evidence
is **individual-level and prospective**; the study's contribution is that the association
survives adjustment in an *ecological, cross-sectional* county model, which is consistent with
but not the same as the published designs.

- Cappuccio FP et al., *Diabetes Care* 2010, PMID:19910503
- Liu H et al., *Annals of Medicine* 2025, PMID:39748566
- Nôga DA et al., *JAMA Network Open* 2024, PMID:38441893

### F4. Rurality reverses sign after adjustment (crude ≈ 0 / slightly positive → adjusted β = −0.25) — **SUPPORTED, with one dissenting analysis**

This is a published phenomenon. O'Connor & Wellenius found that at national level, after
adjusting for household income, education, age, sex, BMI, race and ethnicity, the likelihood of
diabetes was **significantly lower in rural than urban areas (OR 0.94, P<0.05)** — i.e. exactly
the crude-positive → adjusted-negative reversal the study reports. The 2021 BRFSS replication
found unadjusted rural>urban ORs significant in 19 states, reduced to 2 states after full
adjustment, with the pooled 41-state OR no longer significant and **Ohio flipping to a
significant OR of 0.77** (verified in the Khavjou full text).

**Dissenting evidence:** a CDC analysis of 2019–2022 data reports that nonmetropolitan residence
*in the South* remained significantly associated with higher diabetes prevalence even after
adjusting for socioeconomic and weight status. So the reversal is regionally heterogeneous —
the study's single national β for rurality masks a South-specific residual effect.

- O'Connor A & Wellenius G, *Public Health* 2012, PMID:22922043
- Khavjou O et al., *Preventing Chronic Disease* 2025, PMID:39819894
- Onufrak S et al., *Preventing Chronic Disease* 2024, PMID:39418173 (dissenting)

### F5. PM2.5 is NOT a significant predictor — **CONTRADICTED**

This is the study's clearest contradiction of the published literature. The Global Burden of
Disease analysis attributes roughly **one-fifth of the global T2D burden (≈20%)** to ambient
PM2.5, with a ~50% increase since 1990; equivalent US-specific and global analyses reach the
same conclusion.

The null is most plausibly a **design artefact rather than a refutation**: county-level
cross-sectional PM2.5 in the contemporary US has a restricted range, is collinear with
urbanicity and poverty, and is being conditioned on rurality and six SES covariates in the same
model — a classic setting for an ecological null. The report should state that the county model
cannot detect the PM2.5 effect rather than that PM2.5 is unrelated to diabetes.

- Burkart K et al., *The Lancet Planetary Health* 2022, PMID:35809588
- Raina M et al., *Physiological Reports* 2024, PMID:39375175
- Sha Y & Wang S, *Frontiers in Public Health* 2024, PMID:38832227

---

## G. Repurposing shortlist (weak evidence layer)

### G1. Statins (pravastatin, LPL/PPARG rationale) — **CONTRADICTED as a naive repurposing read**

Statins **increase** the risk of new-onset diabetes. The Cholesterol Treatment Trialists'
individual-participant-data meta-analysis of large blinded randomised statin trials found
low/moderate-intensity statin therapy raised new-onset diabetes by ~10% (and high-intensity by
~36%), with additional worsening of glycaemia in people with existing diabetes; earlier
trial-level meta-analyses reached the same directional conclusion, and lower LDL-C targets
associate with higher incident diabetes. The cardiovascular benefit still outweighs this risk,
but a comorbidity-adjacency layer that surfaces statins as *pro-glycaemic* candidates is
inverted relative to the evidence. **Flag explicitly in the report.**

No supporting citation found for pravastatin specifically as a glucose-lowering or
diabetes-preventing agent.

- Reith C et al. (Cholesterol Treatment Trialists' Collaboration), *The Lancet Diabetes & Endocrinology* 2024, PMID:38554713
- Rajpathak SN et al., *Diabetes Care* 2009, PMID:19794004
- Rikhi R & Shapiro MD, *Current Cardiology Reports* 2024, PMID:39302589

### G2. Sirolimus / everolimus (mTOR) — **CONTRADICTED**

mTOR inhibitors are diabetogenic, not antidiabetic: rapamycin is directly toxic to pancreatic
β cells (impairing function and survival via mTOR inhibition), and mTOR inhibitors are
implicated in post-transplant diabetes mellitus. Their appearance on a T2D repurposing shortlist
is a false positive of target-based reasoning (mTOR is central to insulin signalling, but
inhibiting it worsens glycaemia).

- Barlow AD et al., *Diabetes* 2013, PMID:23881200
- Granata S et al., *Frontiers in Medicine* 2023, PMID:37250653

### G3. Testosterone — **SUPPORTED**

The strongest candidate on the list. The T4DM randomised placebo-controlled trial showed
2 years of testosterone treatment on top of a lifestyle programme reduced T2D incidence in men
at high risk; long-term registry data report diabetes remission in a substantial fraction of
hypogonadal men with T2D on testosterone undecanoate (observational, lower evidence grade).

- Wittert G et al., *The Lancet Diabetes & Endocrinology* 2021, PMID:33338415
- Haider KS et al., *Diabetes, Obesity and Metabolism* 2020, PMID:32558149

### G4. Spironolactone (ESR1 rationale) — **NOVEL / no supporting glycaemic citation found; mechanistic rationale questionable**

No supporting citation found for spironolactone improving glycaemia or preventing T2D.
Mineralocorticoid-receptor antagonists in diabetes have an established **renal and blood-pressure**
indication (reduced albuminuria and BP in hypertensive diabetic patients), not a glycaemic one;
MR activation actually *impairs* vascular insulin signalling. Note also that the study's stated
target rationale (ESR1) does not match spironolactone's primary pharmacology (mineralocorticoid
receptor antagonism with off-target anti-androgen activity) — worth auditing the target
attribution.

- Takahashi S et al., *Journal of Human Hypertension* 2016, PMID:26674759

### G5. Celecoxib — **NOVEL / no supporting citation found**

No supporting citation found for celecoxib improving glycaemia or diabetes outcomes. The
class-adjacent evidence is for **salicylates**, not COX-2-selective inhibitors: salsalate lowers
HbA1c in T2D (TINSAL programme) and salicylic acid has a long-recognised antihyperglycaemic
action via mitochondrial uncoupling / AMPK / NF-κB. Do not present celecoxib as supported.

- Rena G & Sakamoto K, *Diabetology International* 2014, PMID:27656338

### G6. Colchicine — **NOVEL / UNDER-STUDIED**

Colchicine reduces systemic inflammation in obesity/metabolic syndrome and improves some
lipolysis measures, but a pilot randomised trial found **no significant improvement in insulin
sensitivity**; reviews conclude that human trials are still needed. Reasonable hypothesis,
not established.

- de Bulhões FV et al., *Metabolites* 2024, PMID:39590865

---

## Summary table

| Group | SUPPORTED | NOVEL / UNDER-STUDIED | CONTRADICTED |
|---|---|---|---|
| A. Consensus gene core | A1, A2, A5*, A6*, A7, A8, A13, A16, A17 (9) | A3, A4, A9, A10, A11, A12, A14, A15 (8) | – |
| B. Pathways | B1, B2, B4† (3) | B3 (1) | – |
| C. Islet single-cell | C1, C2, C3, C4, C5 (5) | C6 (1) | – |
| D. Non-coding RNA | D0, D1, D2, D3 (4) | D4, D5 (2) | – |
| E. Exposure (PFAS) | E1‡, E2 (2) | – | E3 (1) |
| F. Epidemiology | F1, F2, F3, F4§ (4) | – | F5 (1) |
| G. Repurposing | G3 (1) | G4, G5, G6 (3) | G1, G2 (2) |
| **Total** | **28** | **15** | **4** |

\* mechanistic support only — not T2D genetic-association loci.
† supported as human physiology, novel as a T2D gene-set enrichment result.
‡ supported but qualified: the most recent meta-analysis finds T2D-specific evidence limited.
§ supported nationally; one published analysis dissents for the nonmetropolitan South.

**Not verified in this pass:** GO terms "cholesterol homeostasis" and "cellular response to
hypoxia" (B5) were not checked against primary sources. The specific numeric enrichment
statistics (fold-enrichments, FDRs, background size 8,290 / signature 252) are internal to the
study and cannot be verified against literature; only the biological identity of the terms was
assessed.


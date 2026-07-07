"""Other MS entity data from Proto-OKN, 2026-07-03."""

# gene-expression-atlas-okn (measured differential expression) for MONDO_0005301.
# 475 distinct DE genes across 4 assays (E-MTAB-69, E-MTAB-2973, ...): MS before/after
# IFN-beta treatment vs normal, in peripheral immune cells. Top ~150 by |log2fc| below.
# cols: sym, cell(CL/UBERON), direction, log2fc, adj_p
GXA_TOTAL_GENES = 475
GXA_TOTAL_ASSAYS = 4
GXA_CSV = """sym,cell,dir,log2fc,adjp
RPS4Y1,CL_0000576,down,-7.9,0.0
DDX3Y,CL_0000576,down,-7.5,0.0
XIST,CL_0000576,up,7.2,3.1653e-301
KDM5D,CL_0000576,down,-7.1,1.72356e-281
UTY,CL_0000576,down,-6.4,2.08067e-204
TXLNGY,CL_0000576,down,-6.3,9.38194e-192
EIF1AY,CL_0000576,down,-6.2,5.65735e-179
PRKY,CL_0000576,down,-5.6,1.64715e-157
ZFY,CL_0000576,down,-5.3,7.20887e-115
IGKC,CL_0000542,up,4.7,7.92903e-09
USP9Y,CL_0000576,down,-4.7,2.97413e-85
TTTY15,CL_0000576,down,-4.2,1.61678e-67
RSAD2,UBERON_0000178,up,4.1,0.00302774
IFI44L,UBERON_0000178,up,4.0,0.00235586
IGHM,CL_0000542,up,3.9,2.98275e-06
IFIT1,UBERON_0000178,up,3.5,0.0031987
LINC00278,CL_0000576,down,-3.5,2.72671e-41
IFI44,UBERON_0000178,up,3.4,0.00441357
TNFRSF17,CL_0000542,up,3.3,3.2392e-06
IFI27,UBERON_0000178,up,3.1,0.00344979
MX1,UBERON_0000178,up,3.1,0.00251293
POU2AF1,CL_0000542,up,3.0,3.22861e-05
OAS3,UBERON_0000178,up,3.0,0.00748946
HERC5,UBERON_0000178,up,2.8,0.00377855
OASL,UBERON_0000178,up,2.7,0.00683929
IFIT2,UBERON_0000178,up,2.6,0.00780129
OAS2,UBERON_0000178,up,2.5,0.00641923
JCHAIN,CL_0000542,up,2.3,3.24198e-05
DDX60,UBERON_0000178,up,2.2,0.00259704
GBP1,UBERON_0000178,up,2.2,0.00212448
TNFAIP6,UBERON_0000178,up,2.2,0.00895545
RRM2,CL_0000542,up,2.2,0.00100596
CD14,CL_0000542,down,-1.9,0.00210864
CD163,CL_0000542,down,-1.9,0.00139444
MZB1,CL_0000542,up,1.9,1.59284e-05
C3,CL_0000542,down,-1.8,0.00025682
SNCA,CL_0000542,down,-1.8,0.000108583
FN1,CL_0000542,down,-1.8,0.000948559
CD38,CL_0000542,up,1.8,7.6844e-05
TRIM22,UBERON_0000178,up,1.8,0.00413347
PARP9,UBERON_0000178,up,2.0,0.000918551
VSIG4,CL_0000542,down,-1.5,0.00206752
P2RY12,CL_0000542,down,-1.7,0.00483019
MX2,UBERON_0000178,up,1.7,0.00711457
PAX5,CL_0000542,up,1.7,6.59378e-05
C1QB,CL_0000542,down,-1.7,0.00535935
PTGS2,CL_0000542,down,-1.6,0.000454429
IFITM3,UBERON_0000178,up,1.6,0.00156208
MSR1,CL_0000542,down,-2.0,0.00120377
CXCL8,CL_0000542,down,-2.0,0.000829461
VEGFA,CL_0000542,down,-2.0,3.07293e-05
IL1RN,CL_0000542,down,-1.5,0.000422856
AIF1,CL_0000542,down,-1.5,8.65589e-05
MAFB,CL_0000542,down,-1.5,0.00652663
MERTK,UBERON_0000178,up,1.5,4.53611e-11
LINC00926,CL_0000542,up,1.4,0.0
LINC01094,CL_0000542,down,-1.6,0.00361178
FAM30A,CL_0000542,up,1.9,2.83285e-05
CD79A,CL_0000542,up,1.4,0.0
MS4A1,CL_0000542,up,1.3,0.0"""

# Cell Ontology / UBERON labels used by GXA MS assays
CL_LABELS = {
    "CL_0000576": "monocyte",
    "CL_0000542": "lymphocyte",
    "CL_0000624": "CD4+ T cell",
    "CL_0000625": "CD8+ T cell",
    "CL_0000775": "neutrophil",
    "CL_0000236": "B cell",
    "CL_0000623": "natural killer cell",
    "UBERON_0000178": "whole blood",
}

# prokn ChEMBL "Indication" (NCIT_C41184) for MONDO_0005301 — 180 compounds.
# Named subset resolvable in prokn (rest are ChEMBL-ID-only -> readable-name undercount).
PROKN_DRUG_TOTAL = 180
PROKN_DRUGS_NAMED = [
    "Alemtuzumab",
    "Baclofen",
    "Amantadine",
    "Amantadine hydrochloride",
    "Biotin",
    "Amifampridine",
    "Armodafinil",
    "Cannabidiol",
    "Cannabinol",
    "Arbaclofen placarbil",
    "Atorvastatin",
    "Celecoxib",
    "Acetazolamide",
    "Aspirin",
    "Acetaminophen",
    "Acetylcysteine",
    "Azithromycin",
    "Acyclovir sodium",
    "Cetirizine",
    "Carbidopa",
    "Briakinumab",
    "Belimumab",
    "Bryostatin 1",
    "BIIB-091",
    "Alfuzosin",
    "Butylated hydroxytoluene",
    "Charcoal, activated",
]

# rdkg drug relationships for MS
RDKG_CONTRA = [
    "Ascorbic acid",
    "Zinc gluconate",
]  # biolink:contraindicated_for (DrugBank)
RDKG_RISK = [
    "Teriflunomide",
    "Lead",
    "Mercury",
    "Solvents",
    "Tobacco Smoke Pollution",
]  # contributes_to (ChemicalExposure)

# spoke-okn TREATS_CtD for MS DOID terms — only 3 (non-therapeutic artifacts)
SPOKE_TREATS = ["Carbonic acid", "Isopropyl alcohol", "Methane"]

# digcfdekg gene sets predicting MS (geneSetToTrait) — top 40 by weight
DIGCFDE_GENESETS = [
    ("BIOCARTA_CTLA4_PATHWAY", 3.0),
    ("GOBP_T_HELPER_17_CELL_LINEAGE_COMMITMENT", 2.89),
    ("KEGG_ALLOGRAFT_REJECTION", 2.83),
    ("WP_GENES_ASSOCIATED_WITH_THE_DEVELOPMENT_OF_RHEUMATOID_ARTHRITIS", 2.8),
    ("BIOCARTA_TH1TH2_PATHWAY", 2.69),
    ("PID_IL27_PATHWAY", 2.64),
    ("GOBP_T_CELL_SELECTION", 2.63),
    ("GOBP_REGULATION_OF_B_CELL_DIFFERENTIATION", 2.62),
    ("GOBP_POSITIVE_REGULATION_OF_ALPHA_BETA_T_CELL_PROLIFERATION", 2.54),
    ("WP_MODULATORS_OF_TCR_SIGNALING_AND_T_CELL_ACTIVATION", 2.53),
    ("REACTOME_INTERLEUKIN_2_SIGNALING", 2.5),
    ("GOBP_T_CELL_ACTIVATION_INVOLVED_IN_IMMUNE_RESPONSE", 2.51),
    ("mp_decreased_memory_T_cell_number", 2.72),
    ("mp_abnormal_T_cell_proliferation", 2.65),
    ("mp_decreased_CD4-positive_regulatory_T_cell_number", 2.73),
    ("DURANTE_ADULT_OLFACTORY_NEUROEPITHELIUM_CD4_T_CELLS", 2.83),
    ("DESCARTES_FETAL_STOMACH_LYMPHOID_CELLS", 2.57),
]

# digcfdekg latent Factors modeling MS mechanism (traitToFactor) — top by weight (probabilities)
DIGCFDE_FACTORS = [
    ("absent spleen germinal center", 0.977),
    ("Lung and thyroid immune genes", 0.96),
    ("TH1/TH2 T cell pathway", 0.957),
    ("CD4 T cell activation genes", 0.952),
    ("regulatory T cell signaling", 0.948),
    ("Decreased regulatory T cell numbers", 0.917),
    ("T and B cell signaling", 0.874),
    ("Naive CD8 T cell program", 0.832),
    ("B and T cell changes", 0.736),
    ("Lymphoid tissue and B cells", 0.726),
    ("IL-2/JAK-STAT signaling pathway", 0.645),
    ("MHC II and alloimmune signaling", 0.499),
    ("T cell activation and NF-kB", 0.494),
    ("Lipoprotein Metabolism", 0.494),
    ("B cell receptor signaling pathway", 0.347),
    ("TCR signaling and activation", 0.29),
]

# rdkg clinical features (has_phenotype HP terms + onset/inheritance) for MS
RDKG_CLINICAL = [
    ("Spasticity", "HP:0001257"),
    ("Paresthesia", "HP:0003401"),
    ("Muscle weakness", "HP:0001324"),
    ("Incoordination", "HP:0002311"),
    ("Diplopia", "HP:0000651"),
    ("CNS demyelination", "HP:0007305"),
    ("Urinary incontinence", "HP:0000020"),
    ("Urinary hesitancy", "HP:0000019"),
    ("Depressivity", "HP:0000716"),
    ("Emotional lability", "HP:0000712"),
    ("Adult onset", "HP:0003581"),
    ("Multifactorial inheritance", "HP:0001426"),
]

# biomarkerkg records for DOID_2377 (MS): specimen-tagged; only 1 record analyte-resolved
BIOMARKER_TOTAL_RECORDS = 53
BIOMARKER_SPECIMENS = {
    "UBERON_0001359": "cerebrospinal fluid",
    "UBERON_0001969": "blood plasma",
    "UBERON_0001977": "blood serum",
    "UBERON_0001088": "urine",
    "UBERON_0006314": "body fluid",
    "UBERON_0000178": "blood",
}
# AN6263-1 assessed molecules (sphingosine-1-phosphate / IFN-IL17 axis)
BIOMARKER_ANALYTES = ["SPHK1", "SPHK2", "S1PR1", "S1PR5", "IL17A", "IFNG", "APOA1"]

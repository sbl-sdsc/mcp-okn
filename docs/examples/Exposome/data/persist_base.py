"""Write the base chemical, target, and AOP-backbone CSVs for the exposome demo."""

import csv
from pathlib import Path

D = "/sessions/nifty-festive-gauss/mnt/outputs/exposome/data"

# --- Chemical master (13 bisphenols) ---
chem_cols = [
    "abbrev",
    "name",
    "cas",
    "pubchem_cid",
    "dtxsid",
    "chebi",
    "in_aopwiki",
    "in_toxcast",
    "in_tox21",
    "in_ice",
    "toxcast_tested",
    "toxcast_active",
]
chem = [
    [
        "BPA",
        "Bisphenol A",
        "80-05-7",
        "6623",
        "DTXSID7020182",
        "CHEBI:33216",
        1,
        1,
        1,
        1,
        1414,
        375,
    ],
    [
        "BPS",
        "Bisphenol S (4,4'-sulfonyldiphenol)",
        "80-09-1",
        "",
        "DTXSID3022409",
        "",
        0,
        1,
        1,
        1,
        558,
        72,
    ],
    [
        "BPF",
        "Bisphenol F (bis(4-hydroxyphenyl)methane)",
        "620-92-8",
        "",
        "DTXSID9022445",
        "",
        0,
        1,
        1,
        1,
        665,
        51,
    ],
    [
        "BPAF",
        "Bisphenol AF (hexafluoro)",
        "1478-61-1",
        "",
        "DTXSID7037717",
        "",
        0,
        1,
        1,
        1,
        1189,
        484,
    ],
    ["BPB", "Bisphenol B", "77-40-7", "", "DTXSID4022442", "", 0, 1, 1, 1, 991, 309],
    ["BPAP", "Bisphenol AP", "1571-75-1", "", "DTXSID5051444", "", 0, 1, 1, 1, 273, 80],
    ["BPE", "Bisphenol E", "2081-08-5", "", "DTXSID3047891", "", 0, 1, 1, 1, 398, 62],
    [
        "BPC",
        "Bisphenol C (3,3'-dimethyl BPA)",
        "79-97-0",
        "",
        "DTXSID8047890",
        "",
        0,
        1,
        1,
        1,
        662,
        229,
    ],
    ["BPZ", "Bisphenol Z", "843-55-0", "", "DTXSID4047963", "", 0, 1, 1, 1, 238, 119],
    ["BPP", "Bisphenol P", "2167-51-3", "", "DTXSID0058693", "", 0, 0, 0, 1, "", ""],
    ["BPM", "Bisphenol M", "13595-25-0", "", "DTXSID7065548", "", 0, 0, 0, 1, "", ""],
    [
        "TBBPA",
        "Tetrabromobisphenol A",
        "79-94-7",
        "6618",
        "DTXSID1026081",
        "",
        1,
        1,
        1,
        1,
        1138,
        377,
    ],
    [
        "TCBPA",
        "Tetrachlorobisphenol A",
        "79-95-8",
        "",
        "DTXSID3021770",
        "",
        0,
        1,
        1,
        1,
        808,
        297,
    ],
]
with Path(f"{D}/chemicals.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(chem_cols)
    w.writerows(chem)

# --- Target gene ID table (verified from aopwiki HGNC crosswalk nodes) ---
tgt_cols = ["symbol", "name", "ensembl", "entrez", "role_in_bisphenol_MoA"]
targets = [
    [
        "ESR1",
        "Estrogen receptor alpha",
        "ENSG00000091831",
        "2099",
        "Primary estrogenic MIE target (AOP314/522); ToxCast ER assays",
    ],
    [
        "ESR2",
        "Estrogen receptor beta",
        "ENSG00000140009",
        "2100",
        "Estrogenic target; ERalpha/beta heterodimer (AOP535 KE)",
    ],
    [
        "GPER1",
        "G-protein coupled estrogen receptor 1",
        "ENSG00000164850",
        "2852",
        "MIE of AOP535 (GPER activation -> memory impairment)",
    ],
    [
        "AR",
        "Androgen receptor",
        "ENSG00000169083",
        "367",
        "Anti-androgen activity in ToxCast/ICE AR assays",
    ],
    [
        "TTR",
        "Transthyretin",
        "ENSG00000118271",
        "7276",
        "MIE of AOP152 (TTR binding -> neurodevelopmental tox); TBBPA",
    ],
    [
        "THRA",
        "Thyroid hormone receptor alpha",
        "ENSG00000126351",
        "7067",
        "Thyroid axis (TBBPA/halogenated bisphenols)",
    ],
    [
        "THRB",
        "Thyroid hormone receptor beta",
        "ENSG00000151090",
        "7068",
        "Thyroid axis (TBBPA/halogenated bisphenols)",
    ],
    [
        "ESRRA",
        "Estrogen-related receptor alpha",
        "",
        "",
        "BPA high-affinity receptor (literature); not in aopwiki HGNC set",
    ],
    [
        "ESRRG",
        "Estrogen-related receptor gamma",
        "",
        "",
        "BPA very high-affinity receptor (literature); not in aopwiki HGNC set",
    ],
    [
        "NR1I2",
        "Pregnane X receptor (PXR)",
        "ENSG00000144852",
        "8856",
        "Xenobiotic nuclear receptor; ToxCast actives",
    ],
    [
        "NR1I3",
        "Constitutive androstane receptor (CAR)",
        "ENSG00000143257",
        "9970",
        "Xenobiotic nuclear receptor",
    ],
    [
        "NR3C1",
        "Glucocorticoid receptor",
        "ENSG00000113580",
        "2908",
        "Steroid receptor cross-talk",
    ],
    ["PGR", "Progesterone receptor", "ENSG00000082175", "5241", "Steroid receptor"],
    [
        "PPARG",
        "Peroxisome proliferator-activated receptor gamma",
        "ENSG00000132170",
        "5468",
        "Metabolic/adipogenic target (obesogen hypothesis)",
    ],
    [
        "AHR",
        "Aryl hydrocarbon receptor",
        "ENSG00000106546",
        "196",
        "Xenobiotic sensing",
    ],
    [
        "GATA3",
        "GATA binding protein 3",
        "ENSG00000107485",
        "2625",
        "KE in AOP314 (GATA3 induction -> Th2/IL-4 -> SLE)",
    ],
]
with Path(f"{D}/targets.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(tgt_cols)
    w.writerows(targets)

# --- AOP backbone (BPA + TBBPA) ---
aop_cols = [
    "chemical",
    "cas",
    "aop_id",
    "aop_title",
    "mie_title",
    "adverse_outcome",
    "n_key_events",
    "curated_target",
]
aops = [
    [
        "BPA",
        "80-05-7",
        "314",
        "Binding to ER-alpha in immune cells leading to exacerbation of systemic lupus erythematosus (SLE)",
        "Binding to estrogen receptor (ER)-alpha in immune cells",
        "Exacerbation of systemic lupus erythematosus (SLE)",
        5,
        "ESR1/GATA3",
    ],
    [
        "BPA",
        "80-05-7",
        "522",
        "Estrogen antagonism leading to increased risk of autism-like behavior",
        "Antagonism, Estrogen receptor",
        "autism-like behavior",
        6,
        "ESR1/ESR2",
    ],
    [
        "BPA",
        "80-05-7",
        "535",
        "Binding and activation of GPER leading to learning and memory impairments",
        "protein-coupled estrogen receptor 1 (GPER) activation",
        "Impairment, Learning and memory",
        9,
        "GPER1/ESR1/ESR2",
    ],
    [
        "TBBPA",
        "79-94-7",
        "152",
        "Interference with thyroid serum binding protein transthyretin and subsequent adverse human neurodevelopmental toxicity",
        "Binding, Transthyretin in serum",
        "Cognitive function, decreased",
        11,
        "TTR",
    ],
]
with Path(f"{D}/aop_backbone.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(aop_cols)
    w.writerows(aops)

print("Base CSVs written:")
for fn in ["chemicals.csv", "targets.csv", "aop_backbone.csv"]:
    with Path(f"{D}/{fn}").open() as f:
        n = sum(1 for _ in f) - 1
    print(f"  {fn}: {n} rows")

"""
Recreate key results of Nelson et al. 2021 (Life 11(1):42, doi:10.3390/life11010042)
from spoke-genelab + cross-graph queries (spoke-okn, digcfdekg) on the FRINK federation.

Generates:
  figures/fig1_spaceflight_disease_associations.png   -> recreation of the paper's central
        "spaceflight transcriptomics -> terrestrial disease" result (cf. paper Fig 5).
  figures/fig2_top_DE_genes.png                        -> recreation of differential-expression
        signatures per immune organ (cf. paper Fig 3, Section 3.1).
  figures/fig3_nasa_hazard_recovery.png                -> mapping of recovered shared diseases
        onto NASA's spaceflight-hazard physiology.
  data/*.csv                                           -> the underlying retrieved tables.

All numbers are copied verbatim from MCP `sparql_query` results against
https://frink.apps.renci.org (named graphs spoke-genelab / spoke-okn / digcfdekg).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
DATA = os.path.join(HERE, "data")
os.makedirs(FIG, exist_ok=True)
os.makedirs(DATA, exist_ok=True)

# ---- NASA spaceflight-hazard colour scheme -------------------------------------------
HAZARD_COLORS = {
    "CNS / Psychiatric":      "#3b6fb5",
    "Cardiovascular":         "#c0392b",
    "Immune / Inflammatory":  "#27ae60",
    "Ocular (SANS)":          "#8e44ad",
    "Metabolic / GI / Liver": "#e08e0b",
    "Cancer (radiation)":     "#7f8c8d",
    "Musculoskeletal":        "#16a085",
}

# =====================================================================================
# Figure 1 — top terrestrial diseases associated with the combined spaceflight DE gene set
#   spoke-genelab (thymus OSD-244 30d-LAR + liver OSD-245 60d + spleen OSD-246 60d,
#   Space Flight vs Ground Control, adj_p<0.05) -> human ortholog -> spoke-okn ASSOCIATES_DaG
# =====================================================================================
disease_assoc = [
    ("epilepsy", 615, "CNS / Psychiatric"),
    ("nervous system disease", 482, "CNS / Psychiatric"),
    ("liver disease", 368, "Metabolic / GI / Liver"),
    ("hypertension", 189, "Cardiovascular"),
    ("gastroesophageal reflux disease", 164, "Metabolic / GI / Liver"),
    ("diabetes mellitus", 159, "Metabolic / GI / Liver"),
    ("obesity", 159, "Metabolic / GI / Liver"),
    ("cardiomyopathy", 157, "Cardiovascular"),
    ("dermatitis", 145, "Immune / Inflammatory"),
    ("myopia", 137, "Ocular (SANS)"),
    ("depressive disorder", 137, "CNS / Psychiatric"),
    ("schizophrenia", 130, "CNS / Psychiatric"),
    ("asthma", 123, "Immune / Inflammatory"),
    ("coronary artery disease", 121, "Cardiovascular"),
    ("glaucoma", 107, "Ocular (SANS)"),
    ("leukemia", 105, "Cancer (radiation)"),
    ("inflammatory bowel disease", 101, "Immune / Inflammatory"),
    ("chronic obstructive pulmonary disease", 90, "Immune / Inflammatory"),
    ("breast carcinoma", 90, "Cancer (radiation)"),
    ("migraine", 78, "CNS / Psychiatric"),
    ("Parkinson's disease", 64, "CNS / Psychiatric"),
    ("rheumatoid arthritis", 62, "Immune / Inflammatory"),
]
df1 = pd.DataFrame(disease_assoc, columns=["disease", "n_spaceflight_genes", "nasa_hazard"])
df1.to_csv(os.path.join(DATA, "disease_associations_spoke_okn.csv"), index=False)

df1s = df1.sort_values("n_spaceflight_genes")
fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(df1s["disease"], df1s["n_spaceflight_genes"],
        color=[HAZARD_COLORS[h] for h in df1s["nasa_hazard"]], edgecolor="white")
for y, v in enumerate(df1s["n_spaceflight_genes"]):
    ax.text(v + 5, y, str(v), va="center", fontsize=8, color="#333")
ax.set_xlabel("Number of spaceflight-responsive genes linked to the disease\n"
              "(spoke-genelab DE genes -> human ortholog -> spoke-okn ASSOCIATES_DaG)", fontsize=9)
ax.set_title("Recreation of Nelson et al. 2021 central result:\n"
             "spaceflight mouse transcriptomics → terrestrial disease\n"
             "associations recovered via cross-graph query",
             fontsize=11, fontweight="bold")
handles = [Patch(facecolor=c, label=h) for h, c in HAZARD_COLORS.items() if h in set(df1["nasa_hazard"])]
ax.legend(handles=handles, title="NASA spaceflight-hazard physiology", fontsize=8,
          title_fontsize=8, loc="lower right", frameon=True)
ax.margins(y=0.01)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig1_spaceflight_disease_associations.png"), dpi=150)
plt.close()

# =====================================================================================
# Figure 2 — top differential-expression signatures per immune organ (cf. paper Fig 3)
# =====================================================================================
de = {
    "Thymus (OSD-244 / GLDS-244, 30d LAR)": [
        ("Itga2b", 2.92), ("Gp5", 3.24), ("Ifi27l2a", 2.82), ("Csf3r", 1.90),
        ("Parvb", 3.21), ("Pcsk1", -2.24), ("Foxb1", -3.68), ("Nabp1", -1.50),
    ],
    "Liver (OSD-245 / GLDS-245, 60d)": [
        ("Dhrs9", 2.86), ("Dtx4", 1.94), ("Mcu", 1.27), ("Trim2", 1.52),
        ("Usp2", -2.50), ("Nmrk1", -1.72), ("Lingo4", -1.65), ("Cnmd", -1.51),
    ],
    "Spleen (OSD-246 / GLDS-246, 60d)": [
        ("Npas2", 1.67), ("Adamts4", 1.40), ("Nr1d2", -0.49), ("Per3", -0.79),
        ("Tef", -0.58), ("Hlf", -0.97), ("Dbp", -0.90), ("Cys1", -1.00),
    ],
}
fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), sharex=False)
for ax, (tissue, genes) in zip(axes, de.items()):
    genes_sorted = sorted(genes, key=lambda x: x[1])
    names = [g[0] for g in genes_sorted]
    vals = [g[1] for g in genes_sorted]
    colors = ["#c0392b" if v > 0 else "#3b6fb5" for v in vals]
    ax.barh(names, vals, color=colors, edgecolor="white")
    ax.axvline(0, color="#555", lw=0.8)
    ax.set_title(tissue, fontsize=9.5, fontweight="bold")
    ax.set_xlabel("log2 fold-change (Space Flight / Ground Control)", fontsize=8)
    ax.tick_params(axis="y", labelsize=9)
fig.suptitle("Recreation of spaceflight differential-expression signatures in three immune organs "
             "(spoke-genelab, adj_p<0.05)\n"
             "Spleen = circadian-clock genes (Dbp/Nr1d2/Per3/Tef/Hlf/Npas2); "
             "Liver = mito-Ca/NAD/retinoid metabolism; Thymus = platelet/interferon",
             fontsize=10.5, fontweight="bold")
up = Patch(facecolor="#c0392b", label="Up in spaceflight")
down = Patch(facecolor="#3b6fb5", label="Down in spaceflight")
axes[2].legend(handles=[up, down], fontsize=8, loc="lower right")
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(os.path.join(FIG, "fig2_top_DE_genes.png"), dpi=150)
plt.close()

# =====================================================================================
# Figure 3 — NASA hazard recovery: representative diseases shared by ALL THREE tissues
#   (3-way intersection of the per-tissue disease-association sets; 81 diseases total)
# =====================================================================================
hazard_recovery = {
    "CNS / Psychiatric\n(NASA: CNS deficits)": [
        "Alzheimer's disease", "Parkinson's disease", "multiple sclerosis",
        "epilepsy", "schizophrenia", "depressive disorder", "migraine", "bipolar disorder"],
    "Cardiovascular\n(NASA: CV deconditioning)": [
        "cardiomyopathy", "coronary artery disease", "hypertension",
        "arteriosclerosis", "cerebrovascular disease", "myocarditis"],
    "Immune / Infection\n(NASA: immune dysfunction)": [
        "asthma", "COPD", "inflammatory bowel disease", "rheumatoid arthritis",
        "psoriasis", "tuberculosis", "HIV infection", "COVID-19"],
    "Ocular (SANS)\n(spaceflight neuro-ocular)": [
        "myopia"],
    "Metabolic / Nutrition\n(NASA: metabolic shift)": [
        "diabetes mellitus", "obesity", "nutrition disease", "liver disease", "pancreatitis"],
    "Cancer\n(NASA: ionizing radiation)": [
        "leukemia", "breast cancer", "colorectal cancer", "lung cancer",
        "skin melanoma", "liver cancer", "multiple myeloma"],
}
fig, ax = plt.subplots(figsize=(12, 6.6))
ax.axis("off")
n = len(hazard_recovery)
colW = 1.0 / n
cat_colors = ["#3b6fb5", "#c0392b", "#27ae60", "#8e44ad", "#e08e0b", "#7f8c8d"]
for i, ((cat, diseases), col) in enumerate(zip(hazard_recovery.items(), cat_colors)):
    x = i * colW + colW / 2
    ax.add_patch(plt.Rectangle((i*colW+0.005, 0.86), colW-0.01, 0.10,
                               color=col, transform=ax.transAxes, clip_on=False))
    ax.text(x, 0.91, cat, ha="center", va="center", color="white",
            fontsize=8.6, fontweight="bold", transform=ax.transAxes)
    for j, d in enumerate(diseases):
        ax.text(x, 0.80 - j*0.083, "• " + d, ha="center", va="center",
                fontsize=8.4, color="#222", transform=ax.transAxes)
ax.text(0.5, 0.005,
        "81 terrestrial diseases are linked to spaceflight-responsive genes in ALL THREE immune organs "
        "(thymus ∩ liver ∩ spleen).\nThe recovered categories reproduce NASA's recognised spaceflight "
        "health hazards — without any embedding step, using explicit cross-graph joins.",
        ha="center", va="bottom", fontsize=8.8, style="italic", transform=ax.transAxes)
ax.set_title("Cross-graph recovery of NASA spaceflight-hazard physiology from shared disease associations\n"
             "(spoke-genelab ∩ spoke-okn; diseases shared by thymus, liver and spleen gene sets)",
             fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig3_nasa_hazard_recovery.png"), dpi=150)
plt.close()

# ---- supporting CSV tables -----------------------------------------------------------
pd.DataFrame([
    ["GLDS-4",   "OSD-4",   "Effects of Vector-Averaged Gravity on T-cell development", "thymus", "DNA microarray", "STS-118"],
    ["GLDS-244", "OSD-244", "Rodent Research-6", "thymus", "RNA-Seq", "RR-6 / SpaceX-13"],
    ["GLDS-245", "OSD-245", "Rodent Research-6", "liver",  "RNA-Seq", "RR-6 / SpaceX-13"],
    ["GLDS-246", "OSD-246", "Rodent Research-6", "spleen", "RNA-Seq", "RR-6 / SpaceX-13"],
    ["GLDS-288", "OSD-288", "Mouse Habitat Unit-1", "spleen", "RNA-Seq", "MHU / SpaceX-12"],
    ["GLDS-289", "OSD-289", "Mouse Habitat Unit-1/2", "thymus", "RNA-Seq", "MHU / SpaceX-12"],
], columns=["paper_GLDS", "spoke_genelab_OSD", "project_title", "tissue", "platform", "mission"]
).to_csv(os.path.join(DATA, "dataset_mapping.csv"), index=False)

pd.DataFrame([
    ["thymus", "OSD-244", "30d LAR (Upon euthanasia)", 6281, 3597],
    ["thymus", "OSD-244", "60d ISS-terminal (Carcass)", 2885, 1699],
    ["liver",  "OSD-245", "30d LAR (Upon euthanasia)", 136, 61],
    ["liver",  "OSD-245", "60d ISS-terminal (Carcass)", 2036, 1431],
    ["spleen", "OSD-246", "60d ISS-terminal (Carcass)", 101, 52],
], columns=["tissue", "OSD", "matched_comparison", "genes_measured", "genes_sig_adjp_lt_0.05"]
).to_csv(os.path.join(DATA, "de_gene_counts.csv"), index=False)

pd.DataFrame([(g, fc, t) for t, gs in de.items() for g, fc in gs],
             columns=["mouse_gene", "log2fc_SF_vs_GC", "tissue_assay"]
).to_csv(os.path.join(DATA, "top_de_genes.csv"), index=False)

pd.DataFrame([
    ["Pentobarbital", 272], ["Fluorouracil", 224], ["Hexachlorophene", 198],
    ["Thiabendazole", 79], ["Tributyltin chloride", 71], ["Phenytoin", 63],
    ["Resorcinol", 49], ["Phenolphthalein", 30], ["Phenothiazine", 24],
], columns=["compound", "n_spaceflight_genes_regulated"]
).to_csv(os.path.join(DATA, "compound_perturbations_spoke_okn.csv"), index=False)

pd.DataFrame([
    ["Hypertension", 541], ["Rare bone disease", 481], ["Rare genetic bone disease", 463],
    ["Rare genetic eye disease", 461], ["Rare ophthalmic disorder", 458],
    ["mean corpuscular hemoglobin concentration", 455], ["Rare neurologic disease", 910],
    ["Rare inborn errors of metabolism", 523],
], columns=["trait", "n_spaceflight_genes"]
).to_csv(os.path.join(DATA, "traits_digcfdekg.csv"), index=False)

# =====================================================================================
# Figure 4 — GO biological processes shared by ALL THREE tissues (direct Fig 3d analog)
#   spoke-genelab DE genes -> Entrez -> wikidata(P351/P354) -> HGNC -> prokn
#   (gene -encodes-> protein -involved_in(RO_0002331)-> GO biological process)
#   Federated query returns 245 shared GO biological-process terms. Curated themes below.
#   ★ = the three gene sets the paper named as shared across the three tissues.
# =====================================================================================
go_themes = {
    "★ Apoptosis / programmed cell death": [
        "apoptotic process", "intrinsic apoptotic signaling (p53)",
        "extrinsic apoptotic signaling pathway", "programmed cell death",
        "release of cytochrome c from mitochondria", "necroptotic signaling pathway"],
    "★ Cell metabolic process": [
        "lipid metabolic process", "fatty acid beta-oxidation",
        "DNA / RNA / mRNA metabolic process", "reactive oxygen species metabolism",
        "gluconeogenesis", "lipid & energy homeostasis"],
    "★ Cell-membrane integrity": [
        "protein localization to plasma membrane", "extracellular matrix organization",
        "extracellular matrix disassembly", "endomembrane system organization",
        "tight-junction assembly (neg. reg.)", "endothelial barrier establishment"],
    "DNA damage / radiation\n(NASA: ionizing radiation)": [
        "cellular response to ionizing radiation", "cellular response to gamma radiation",
        "DNA damage response", "double-strand break repair",
        "nucleotide-excision repair", "cellular senescence"],
    "Circadian rhythm\n(validates spleen clock genes)": [
        "circadian rhythm", "circadian regulation of gene expression",
        "entrainment of clock by photoperiod", "locomotor rhythm",
        "regulation of circadian rhythm", "rhythmic process"],
    "Immune / inflammatory\n(NASA: immune dysfunction)": [
        "immune / innate immune response", "inflammatory response",
        "B-cell & T-cell differentiation", "type II interferon signaling",
        "defense response to virus", "interleukin-6 production"],
    "Oxidative / hypoxic stress": [
        "response to oxidative stress", "cellular response to H2O2",
        "response to hypoxia", "response to unfolded protein",
        "response to xenobiotic stimulus", "response to nutrient levels"],
    "Vascular & musculoskeletal\n(NASA: CV / bone-muscle)": [
        "regulation of vasoconstriction", "VEGF production",
        "vascular smooth-muscle proliferation", "skeletal system development",
        "osteoblast differentiation (neg. reg.)", "skeletal muscle contraction"],
}
fig, axes = plt.subplots(2, 4, figsize=(16, 8.2))
theme_colors = ["#c0392b", "#e08e0b", "#16a085", "#7f8c8d",
                "#2c3e50", "#27ae60", "#2980b9", "#8e44ad"]
for ax, (theme, terms), col in zip(axes.ravel(), go_themes.items(), theme_colors):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0.88), 1, 0.13, color=col, transform=ax.transAxes, clip_on=False))
    ax.text(0.5, 0.945, theme, ha="center", va="center", color="white",
            fontsize=9, fontweight="bold", transform=ax.transAxes)
    for j, t in enumerate(terms):
        ax.text(0.02, 0.80 - j*0.135, "• " + t, ha="left", va="center",
                fontsize=8.3, color="#222", transform=ax.transAxes)
fig.suptitle("Direct recreation of Nelson et al. Fig 3d — GO biological processes shared across "
             "thymus, liver and spleen spaceflight genes\n"
             "245 shared GO terms via spoke-genelab → wikidata → prokn; ★ = the 3 sets the paper named "
             "(apoptosis, cell metabolic process, cell-membrane integrity) — all recovered",
             fontsize=11, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig(os.path.join(FIG, "fig4_shared_GO_processes.png"), dpi=150)
plt.close()

pd.DataFrame([(t, theme) for theme, ts in go_themes.items() for t in ts],
             columns=["representative_shared_GO_BP", "theme"]
).to_csv(os.path.join(DATA, "shared_GO_processes.csv"), index=False)

print("Wrote figures to", FIG)
print("Wrote data to", DATA)
for f in sorted(os.listdir(FIG)):
    print("  figure:", f)
for f in sorted(os.listdir(DATA)):
    print("  data:", f)

"""Render the exposome figures (PNG) from the assembled CSVs."""

import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

D = "/sessions/nifty-festive-gauss/mnt/outputs/exposome"
FIG = f"{D}/figures"


def load(fn):
    """Load a CSV file (data/ then top-level) as a list of dict rows."""
    p = f"{D}/data/{fn}"
    if not Path(p).exists():
        p = f"{D}/{fn}"
    with Path(p).open() as f:
        return list(csv.DictReader(f))


plt.rcParams.update(
    {
        "font.size": 9,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "figure.dpi": 150,
    }
)
TEAL = "#1b7a7a"
CORAL = "#d1495b"
NAVY = "#20365b"
AMBER = "#e0a458"
GREY = "#8a8f98"

# ---- FIG 1: assay coverage matrix (ToxCast) ----
chem = [r for r in load("chemicals.csv") if r["toxcast_tested"]]
chem.sort(key=lambda r: int(r["toxcast_active"]), reverse=True)
labels = [f"{r['abbrev']}" for r in chem]
tested = [int(r["toxcast_tested"]) for r in chem]
active = [int(r["toxcast_active"]) for r in chem]
pct = [100 * a / t for a, t in zip(active, tested, strict=False)]
y = np.arange(len(chem))
fig, ax = plt.subplots(figsize=(8.2, 5.2))
ax.barh(y, tested, color="#d9e4e4", label="Endpoints tested", zorder=2)
ax.barh(y, active, color=TEAL, label="Active (hitcall=1)", zorder=3)
for i, (t, a, p) in enumerate(zip(tested, active, pct, strict=False)):
    ax.text(t + 12, i, f"{a}/{t} ({p:.0f}%)", va="center", fontsize=8, color=NAVY)
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel("ToxCast high-throughput assay endpoints")
ax.set_xlim(0, 1650)
ax.set_title("Per-bisphenol ToxCast assay coverage & activity")
ax.legend(loc="lower right", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{FIG}/fig1_assay_coverage.png", bbox_inches="tight")
plt.close()

# ---- FIG 2: expression matrix (GXA targets) ----
gx = load("gxa_expression.csv")
gx.sort(key=lambda r: int(r["n_sig_contrasts"]), reverse=True)
sym = [r["symbol"] for r in gx]
up = [int(r["n_up"]) for r in gx]
dn = [int(r["n_down"]) for r in gx]
mlfc = [float(r["max_abs_log2fc"]) for r in gx]
y = np.arange(len(gx))
fig, ax = plt.subplots(figsize=(8.4, 5.6))
ax.barh(y, up, color=CORAL, label="Up-regulated contrasts", zorder=3)
ax.barh(y, [-d for d in dn], color=TEAL, label="Down-regulated contrasts", zorder=3)
for i, m in enumerate(mlfc):
    ax.text(up[i] + 6, i, f"|log2FC|≤{m:g}", va="center", fontsize=7, color=GREY)
ax.axvline(0, color="#333", lw=0.8)
ax.set_yticks(y)
ax.set_yticklabels(sym)
ax.invert_yaxis()
ax.set_xlabel(
    "← down-regulated    significant GXA contrasts (adj p<0.05)    up-regulated →"
)
ax.set_title(
    "Differential expression of bisphenol molecular targets (Gene Expression Atlas)"
)
ax.legend(loc="lower right", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{FIG}/fig2_expression_matrix.png", bbox_inches="tight")
plt.close()

# ---- FIG 3: target x disease heatmap (spoke gene-disease) ----
spoke = load("spoke_gene_disease.csv")
tset = [r["symbol"] for r in load("gxa_expression.csv")]

dcount = Counter(r["disease"] for r in spoke)
top_dis = [d for d, _ in dcount.most_common(20)]
genes = sorted({r["symbol"] for r in spoke})
M = np.zeros((len(genes), len(top_dis)))
gd = {(r["symbol"], r["disease"]) for r in spoke}
for i, g in enumerate(genes):
    for j, d in enumerate(top_dis):
        M[i, j] = 1 if (g, d) in gd else 0
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.imshow(M, aspect="auto", cmap="BuGn", vmin=0, vmax=1)
ax.set_xticks(range(len(top_dis)))
ax.set_xticklabels(top_dis, rotation=55, ha="right", fontsize=8)
ax.set_yticks(range(len(genes)))
ax.set_yticklabels(genes, fontsize=8)
for i in range(len(genes)):
    for j in range(len(top_dis)):
        if M[i, j]:
            ax.text(j, i, "●", ha="center", va="center", color=NAVY, fontsize=7)
ax.set_title("Bisphenol target gene → disease associations (SPOKE-OKN, DOID)")
plt.tight_layout()
plt.savefig(f"{FIG}/fig3_target_disease_matrix.png", bbox_inches="tight")
plt.close()

# ---- FIG 4: corroboration bars (top chemical->disease) ----
rank = load("corroboration_ranking.csv")
# choose a spread: top BPA + best non-BPA
top = [r for r in rank if r["chemical"] == "BPA"][:10]
others = [r for r in rank if r["chemical"] != "BPA"][:8]
sel = top + others
sel.sort(key=lambda r: (int(r["corroboration_score"]), r["chemical"]))
lab = [f"{r['chemical']} → {r['disease']}" for r in sel]
sc = [int(r["corroboration_score"]) for r in sel]
aop = [int(r["aop_anchored"]) for r in sel]
cols = [NAVY if a else TEAL for a in aop]
y = np.arange(len(sel))
fig, ax = plt.subplots(figsize=(9.2, 7.6))
ax.barh(y, sc, color=cols, zorder=3)
for i, r in enumerate(sel):
    ax.text(
        sc[i] + 0.05,
        i,
        r["sources"]
        .replace("_", " ")
        .replace("aop structure", "AOP")
        .replace("assay activity", "assay")
        .replace("disease assoc", "disease")
        .replace("rare disease", "rare")
        .replace("protein annot", "protein"),
        va="center",
        fontsize=6,
        color="#555",
    )
ax.set_yticks(y)
ax.set_yticklabels(lab, fontsize=8)
ax.set_xlabel("Corroboration score (# independent evidence sources, max 7)")
ax.set_xlim(0, 9.5)
ax.set_title("Cross-source corroboration of chemical → disease links")
ax.legend(
    handles=[
        Patch(color=NAVY, label="AOP-anchored (curated pathway)"),
        Patch(color=TEAL, label="Assay/target-based"),
    ],
    loc="lower right",
    frameon=False,
)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{FIG}/fig4_corroboration_bars.png", bbox_inches="tight")
plt.close()
print("Static figures written:", *list(__import__("os").listdir(FIG)))

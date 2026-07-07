#!/usr/bin/env python3
"""Figures for the MS Proto-OKN knowledge map (matches AD analysis style)."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "/sessions/stoic-charming-ride/mnt/MS"
FIG = f"{OUT}/figures"
BLUE = "#2E86AB"
GREEN = "#3B8C4D"
ORANGE = "#F18F01"
PURPLE = "#A23B72"
RED = "#C0392B"
INK = "#1c2733"
GRAY = "#95a5a6"
MUTED = "#6b7783"
plt.rcParams.update(
    {"font.family": "DejaVu Sans", "axes.edgecolor": "#c9d3dc", "axes.linewidth": 0.8}
)

stats = json.loads(Path(f"{OUT}/ms_stats.json").read_text())
with Path(f"{OUT}/MS_gene_source_matrix.csv").open() as f:
    matrix = list(csv.DictReader(f))

# ================= FIG 1: cross-source corroboration =================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
nsrc = stats["gene_by_nsources"]
xs = [1, 2, 3]
ys = [nsrc.get(str(i), 0) for i in xs]
cols = [GRAY, BLUE, RED]
bars = ax1.bar([str(x) for x in xs], ys, color=cols, edgecolor="#333", width=0.62)
for b, y in zip(bars, ys, strict=False):
    ax1.text(
        b.get_x() + b.get_width() / 2,
        y + 3,
        str(y),
        ha="center",
        fontsize=12,
        fontweight="bold",
    )
ax1.set_title(
    "MS-associated genes by number of corroborating sources",
    fontsize=13,
    fontweight="bold",
)
ax1.set_xlabel(
    "# independent association sources (spoke-okn / rdkg / digcfdekg)", fontsize=10.5
)
ax1.set_ylabel("number of genes", fontsize=10.5)
ax1.set_ylim(0, max(ys) * 1.16)
t1 = stats["tier1_genes_3sources"]
box = (
    "13 genes in all 3 sources (T1 high-confidence core):\n"
    "HLA-DRB1, IL2RA, IL7R, TYK2, STAT4, CD6, CD40,\nCD58, CBLB, IL12A, IFNG, TNFRSF1A, TNFSF14"
)
ax1.text(
    0.97,
    0.93,
    box,
    transform=ax1.transAxes,
    ha="right",
    va="top",
    fontsize=9.2,
    style="italic",
    bbox={"boxstyle": "round,pad=0.5", "fc": "#FFF6E6", "ec": ORANGE, "lw": 1.2},
)
for s in ["top", "right"]:
    ax1.spines[s].set_visible(False)

srct = stats["source_gene_totals"]
order = sorted(srct.items(), key=lambda kv: kv[1])
labels = [k for k, _ in order]
vals = [v for _, v in order]
cmap = {"spoke-okn": BLUE, "rdkg": PURPLE, "digcfdekg": GREEN}
barh = ax2.barh(
    labels, vals, color=[cmap[lbl] for lbl in labels], edgecolor="#333", height=0.6
)
for b, v in zip(barh, vals, strict=False):
    ax2.text(
        v + 3,
        b.get_y() + b.get_height() / 2,
        str(v),
        va="center",
        fontsize=11.5,
        fontweight="bold",
    )
ax2.set_title("MS-associated genes per source", fontsize=13, fontweight="bold")
ax2.set_xlabel("number of MS genes", fontsize=10.5)
ax2.set_xlim(0, max(vals) * 1.16)
ax2.text(
    0.97,
    0.12,
    "spoke-okn: curated links\nrdkg: curated (immune/rare)\ndigcfdekg: statistical (GWAS/PIGEAN)",
    transform=ax2.transAxes,
    ha="right",
    va="bottom",
    fontsize=8.8,
    style="italic",
    color=MUTED,
)
for s in ["top", "right"]:
    ax2.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig(f"{FIG}/fig1_cross_source_corroboration.png", dpi=140, bbox_inches="tight")
plt.close()

# ================= FIG 2: evidence + entity breakdown =================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
ev = stats["evidence_counts"]
ev_order = [
    "curated_link",
    "statistical_association",
    "measured_activity_change",
    "pathway_membership",
]
ev_lab = [
    "curated link",
    "statistical /\ngenetic assoc.",
    "measured\nactivity change",
    "pathway\nmembership",
]
ev_col = [BLUE, GREEN, ORANGE, PURPLE]
ev_val = [ev[k] for k in ev_order]
bars = ax1.bar(ev_lab, ev_val, color=ev_col, edgecolor="#333", width=0.66)
for b, v in zip(bars, ev_val, strict=False):
    ax1.text(
        b.get_x() + b.get_width() / 2,
        v + 3,
        str(v),
        ha="center",
        fontsize=12,
        fontweight="bold",
    )
ax1.set_title(
    "Findings by evidence type (kept separate)", fontsize=13, fontweight="bold"
)
ax1.set_ylabel("number of findings", fontsize=10.5)
ax1.set_ylim(0, max(ev_val) * 1.16)
for s in ["top", "right"]:
    ax1.spines[s].set_visible(False)
ax1.tick_params(axis="x", labelsize=9)

ent = stats["entity_counts"]
ent_map = [
    ("gene (association)", "gene", BLUE),
    ("gene: altered activity", "gene_altered_activity", ORANGE),
    ("drug / therapeutic", "drug", PURPLE),
    ("pathway / gene set", "pathway_or_geneset", GREEN),
    ("clinical feature", "clinical_feature", RED),
    ("biomarker", "biomarker", "#16a085"),
    ("genetic variant", "genetic_variant", GRAY),
]
elabels = [m[0] for m in ent_map]
evals = [ent.get(m[1], 0) for m in ent_map]
ecols = [m[2] for m in ent_map]
order = np.argsort(evals)
elabels = [elabels[i] for i in order]
evals = [evals[i] for i in order]
ecols = [ecols[i] for i in order]
barh = ax2.barh(elabels, evals, color=ecols, edgecolor="#333", height=0.66)
for b, v in zip(barh, evals, strict=False):
    ax2.text(
        v + 3,
        b.get_y() + b.get_height() / 2,
        str(v),
        va="center",
        fontsize=11,
        fontweight="bold",
    )
ax2.set_title("Findings by entity type", fontsize=13, fontweight="bold")
ax2.set_xlabel("number of findings", fontsize=10.5)
ax2.set_xlim(0, max(evals) * 1.17)
for s in ["top", "right"]:
    ax2.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig(f"{FIG}/fig2_evidence_entity_breakdown.png", dpi=140, bbox_inches="tight")
plt.close()

# ================= FIG 4: top gene x source matrix =================
weight = {r["gene"]: r["digcfdekg_weight"] for r in matrix}
tier = {r["gene"]: r["confidence_tier"] for r in matrix}


def keyf(r):
    """Sort key: most association sources first, then highest weight."""
    w = float(r["digcfdekg_weight"]) if r["digcfdekg_weight"] else -1
    return (-int(r["n_assoc_sources"]), -w)


top = sorted(matrix, key=keyf)[:30]
srcs = ["spoke-okn", "rdkg", "digcfdekg", "gxa_DE"]
M = np.array([[int(r[s]) for s in srcs] for r in top])
fig, ax = plt.subplots(figsize=(7.6, 10.6))
for i, r in enumerate(top):
    for j, s in enumerate(srcs):
        val = int(r[s])
        color = {0: "#eef3f7"}.get(val, [BLUE, PURPLE, GREEN, ORANGE][j])
        ax.add_patch(
            plt.Rectangle(
                (j, i), 0.94, 0.94, facecolor=color, edgecolor="white", lw=1.4
            )
        )
ax.set_xlim(0, 4)
ax.set_ylim(0, len(top))
ax.set_xticks([j + 0.47 for j in range(4)])
ax.set_xticklabels(
    [
        "spoke-okn\n(curated)",
        "rdkg\n(curated)",
        "digcfdekg\n(statistical)",
        "GXA\n(measured DE)",
    ],
    fontsize=9,
)
ax.set_yticks([i + 0.47 for i in range(len(top))])
lab = []
for r in top:
    w = r["digcfdekg_weight"]
    t = r["confidence_tier"].split()[0]
    lab.append(f"{r['gene']}  ({t}{', w=' + w if w else ''})")
ax.set_yticklabels(lab, fontsize=8.6)
ax.invert_yaxis()
ax.xaxis.tick_top()
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title("Top MS genes × evidence source", fontsize=13, fontweight="bold", pad=26)
ax.tick_params(length=0)
plt.tight_layout()
plt.savefig(f"{FIG}/fig4_top_gene_matrix.png", dpi=140, bbox_inches="tight")
plt.close()
print("fig1, fig2, fig4 done")

#!/usr/bin/env python3
"""Reproduce key figures from spoke-genelab spaceflight-vs-ground-control cross-graph queries.

All values are taken verbatim from OKN SPARQL query results (Space Flight vs Ground Control assays,
matched material and factors_1/2). See the accompanying report for the exact queries.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = "/sessions/stoic-optimistic-bohr/mnt/mcp-okn/spoke-genelab-crossgraph/figures"

# ----------------------------------------------------------------------------
# FIGURE 1 — OSD-102 spaceflight kidney (SF vs GC), reproduces Finch et al. 2025
# (npj Microgravity 10.1038/s41526-025-00465-0) lipid-metabolism + circadian-clock signature.
genes = [
    "Npas2",
    "Arntl",
    "Adamts8",
    "Slc10a1",
    "Hmgcr",
    "Tef",
    "Nr1d1",
    "Nr1d2",
    "Per3",
    "Hmgcs2",
]
lfc = [
    1.43671,
    1.03969,
    1.32843,
    1.22955,
    0.559931,
    -0.652129,
    -0.740493,
    -0.891053,
    -1.1996,
    -1.65554,
]
# Genes named in the paper text and their reported direction
paper = {
    "Npas2": "up",
    "Arntl": "up",
    "Slc10a1": "up",
    "Adamts8": "up (ECM)",
    "Hmgcs2": "down, log2FC -1.68",
}
colors = ["#c0392b" if v > 0 else "#2471a3" for v in lfc]
fig, ax = plt.subplots(figsize=(9, 5.2))
y = np.arange(len(genes))
ax.barh(y, lfc, color=colors)
ax.set_yticks(y)
ax.set_yticklabels(genes)
ax.invert_yaxis()
ax.axvline(0, color="k", lw=0.8)
for i, (g, v) in enumerate(zip(genes, lfc, strict=False)):
    ax.text(
        v + (0.04 if v > 0 else -0.04),
        i,
        f"{v:+.2f}",
        va="center",
        ha="left" if v > 0 else "right",
        fontsize=8,
    )
    if g in paper:
        ax.text(
            0.02 if v < 0 else -0.02,
            i - 0.32,
            f"paper: {paper[g]}",
            fontsize=6.5,
            color="#555",
            ha="left" if v < 0 else "right",
        )
ax.set_xlabel("log2 fold change (Space Flight vs Ground Control)")
ax.set_title(
    "Fig 1 — OSD-102 spaceflight kidney: KG reproduces Finch 2025\n"
    "lipid-metabolism (Slc10a1, Hmgcs2) + circadian-clock (Npas2, Arntl, Per3, Nr1d1/2, Tef) signature",
    fontsize=10,
)
ax.text(
    0.99,
    0.02,
    "Hmgcs2 KG -1.66 vs paper -1.68",
    transform=ax.transAxes,
    ha="right",
    fontsize=7.5,
    style="italic",
    color="#2471a3",
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig1_osd102_kidney_clock_lipid.png", dpi=150)
plt.close()

# ----------------------------------------------------------------------------
# FIGURE 2 — OSD-207 Drosophila CNS (SF vs GC): rdgA / diacylglycerol kinase consistently
# DOWNregulated across all microarray contrasts. Reproduces Samson et al. 2024 (10.2478/gsr-2024-0002).
rdga_lfc = [
    -1.90546,
    -1.53501,
    -1.42486,
    -1.394,
    -1.32006,
    -1.27469,
    -1.07836,
    -1.05441,
    -1.02355,
    -0.83946,
    -0.808601,
    -0.794089,
    -0.76323,
    -0.707912,
    -0.492962,
]
fig, ax = plt.subplots(figsize=(8, 4.6))
x = np.arange(len(rdga_lfc))
ax.bar(x, sorted(rdga_lfc), color="#2471a3")
ax.axhline(0, color="k", lw=0.8)
ax.axhline(
    np.mean(rdga_lfc),
    color="#c0392b",
    ls="--",
    lw=1,
    label=f"mean log2FC = {np.mean(rdga_lfc):+.2f}",
)
ax.set_xlabel("rdgA differential-expression records (assay contrasts / probes)")
ax.set_ylabel("log2 fold change (SF vs GC)")
ax.set_title(
    "Fig 2 — OSD-207 Drosophila CNS: rdgA (diacylglycerol kinase) is consistently\n"
    "DOWN-regulated in spaceflight — reproduces Samson et al. 2024",
    fontsize=10,
)
ax.legend(loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT}/fig2_osd207_rdgA_dgk.png", dpi=150)
plt.close()

# ----------------------------------------------------------------------------
# FIGURE 3 — OSD-239 spaceflight skin DEGs (SF vs GC) that are ALSO differentially expressed in
# terrestrial Gene Expression Atlas skin assays (UBERON_0001003). ECM/collagen genes (LOX, COL5A1)
# support the skin-barrier / ECM disruption of Cope et al. 2024 (10.1038/s43856-024-00532-9).
sk_genes = ["MNS1", "ACKR2", "CCDC3", "MRC2", "LOX", "COL5A1"]
sk_lfc = [2.55175, 1.70081, -1.66542, -1.32965, -1.61486, -1.93349]
order = np.argsort(sk_lfc)
sk_genes = [sk_genes[i] for i in order]
sk_lfc = [sk_lfc[i] for i in order]
colors = ["#c0392b" if v > 0 else "#2471a3" for v in sk_lfc]
fig, ax = plt.subplots(figsize=(8, 4.4))
y = np.arange(len(sk_genes))
ax.barh(y, sk_lfc, color=colors)
ax.set_yticks(y)
ax.set_yticklabels(sk_genes)
ax.axvline(0, color="k", lw=0.8)
for i, v in enumerate(sk_lfc):
    ax.text(
        v + (0.04 if v > 0 else -0.04),
        i,
        f"{v:+.2f}",
        va="center",
        ha="left" if v > 0 else "right",
        fontsize=8,
    )
ax.set_xlabel("log2 fold change (Space Flight vs Ground Control)")
ax.set_title(
    "Fig 3 — OSD-239 spaceflight skin DEGs shared with terrestrial GXA skin assays\n"
    "ECM/collagen genes (LOX, COL5A1) — skin-barrier disruption (Cope 2024)",
    fontsize=10,
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig3_osd239_skin_gxa_ecm.png", dpi=150)
plt.close()

print("figures written to", OUT)

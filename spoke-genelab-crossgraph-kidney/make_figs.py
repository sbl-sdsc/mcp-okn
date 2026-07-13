"""Generate figures for the spoke-genelab cross-graph kidney case study."""

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 140,
        "font.family": "DejaVu Sans",
    }
)
C_UP, C_DN, C_NS = "#c0392b", "#2471a3", "#b8b8b8"
OUT = "/sessions/dreamy-intelligent-euler/mnt/outputs/"

# ---------- load C57BL/6J (OSD-102, SF vs GC) ----------
df = pd.read_csv(OUT + "osd102_c57_deg.csv").drop_duplicates()
df["base"] = df["symbol"].str.split("|").str[0]
df = df.sort_values("adj_p_value").drop_duplicates("base")
df["nlp"] = -np.log10(df["adj_p_value"])
sig = df["adj_p_value"] <= 0.1

# ======== FIG 1: Volcano C57BL/6J ========
fig, ax = plt.subplots(figsize=(7.4, 5.6))
up = df[sig & (df.log2fc > 1)]
dn = df[sig & (df.log2fc < -1)]
mid = df[sig & (df.log2fc.abs() <= 1)]
ns = df[~sig]
ax.scatter(ns.log2fc, ns.nlp, s=10, c=C_NS, alpha=0.5, label="not sig (adj p>0.1)")
ax.scatter(
    mid.log2fc, mid.nlp, s=14, c="#7f8c8d", alpha=0.8, label="adj p≤0.1, |log2FC|≤1"
)
ax.scatter(
    up.log2fc,
    up.nlp,
    s=34,
    c=C_UP,
    edgecolor="k",
    lw=0.3,
    label="up  (adj p≤0.1, log2FC>1)",
)
ax.scatter(
    dn.log2fc,
    dn.nlp,
    s=34,
    c=C_DN,
    edgecolor="k",
    lw=0.3,
    label="down (adj p≤0.1, log2FC<-1)",
)
ax.axhline(-np.log10(0.1), ls="--", c="k", lw=0.7, alpha=0.6)
ax.axvline(1, ls=":", c="k", lw=0.6, alpha=0.5)
ax.axvline(-1, ls=":", c="k", lw=0.6, alpha=0.5)
lab = [
    "Ccl28",
    "Hmgcs2",
    "Wnt11",
    "Npas2",
    "Dbp",
    "Arntl",
    "Adamts8",
    "Gulo",
    "Bhlhe41",
    "Per3",
    "Slc10a1",
    "Hmgcr",
    "Sqle",
    "Kap",
]
for g in lab:
    r = df[df.base == g]
    if len(r):
        r = r.iloc[0]
        ax.annotate(
            g,
            (r.log2fc, r.nlp),
            fontsize=8.5,
            fontstyle="italic",
            xytext=(4, 3),
            textcoords="offset points",
        )
ax.set_xlabel("log2 fold change  (Spaceflight / Ground Control)")
ax.set_ylabel("-log10(adjusted p-value)")
ax.set_title(
    "Recreated C57BL/6J kidney DEG signature (OSD-102 / RR-1)\nfrom spoke-genelab — compare to Finch et al. Fig. 1a",
    fontsize=11,
)
ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
fig.tight_layout()
fig.savefig(OUT + "fig1_volcano_c57.png")
plt.close(fig)

# ======== FIG 2: strain x method DEG counts (paper vs KG) ========
groups = [
    "C57BL/6J\nSF vs GC\n(OSD-102)",
    "BALB/c\nSF vs GC\n(OSD-163)",
    "BALB/c\nSF-vs-Basal\nminus GC-vs-Basal",
]
paper = [638, 0, 671]
kg = [467, 2, 581]
x = np.arange(len(groups))
w = 0.38
fig, ax = plt.subplots(figsize=(7.6, 5.0))
b1 = ax.bar(
    x - w / 2, paper, w, label="Finch et al. (DESeq2, adj p≤0.1)", color="#34495e"
)
b2 = ax.bar(
    x + w / 2, kg, w, label="spoke-genelab (pre-computed, adj p≤0.1)", color="#16a085"
)
for b in list(b1) + list(b2):
    ax.annotate(
        f"{int(b.get_height())}",
        (b.get_x() + b.get_width() / 2, b.get_height()),
        ha="center",
        va="bottom",
        fontsize=10,
    )
ax.set_xticks(x)
ax.set_xticklabels(groups, fontsize=9)
ax.set_ylabel("number of differentially expressed genes")
ax.set_title(
    "Strain-dependent spaceflight response is reproduced\nStrong in C57BL/6J, near-absent by SF-vs-GC in BALB/c",
    fontsize=11,
)
ax.legend(fontsize=9)
ax.set_ylim(0, 760)
fig.tight_layout()
fig.savefig(OUT + "fig2_strain_counts.png")
plt.close(fig)

# ======== FIG 3: cholesterol biosynthesis pathway (C57) ========
chol = {
    "Mvd": 0.352495,
    "Sqle": 0.368773,
    "Srebf1": 0.470407,
    "Fdps": 0.413706,
    "Nsdhl": 0.375446,
    "Mvk": 0.389212,
    "Idi1": 0.532544,
    "Insig1": 0.403764,
    "Hmgcr": 0.559931,
    "Dhcr7": 0.319923,
    "Acat2": 0.239251,
    "Hmgcs2": -1.655540,
}
cs = pd.Series(chol).sort_values()
fig, ax = plt.subplots(figsize=(7.2, 5.0))
cols = [C_UP if v > 0 else C_DN for v in cs.values]
ax.barh(range(len(cs)), cs.values, color=cols, edgecolor="k", lw=0.3)
ax.set_yticks(range(len(cs)))
ax.set_yticklabels([f"$\\it{{{g}}}$" for g in cs.index])
ax.axvline(0, c="k", lw=0.8)
ax.set_xlabel("log2 fold change (Spaceflight / Ground Control)")
ax.set_title(
    "Cholesterol / sterol-biosynthesis genes in C57BL/6J kidney\nRecovered from spoke-genelab DEGs (paper's top enriched pathway)",
    fontsize=11,
)
ax.text(
    0.30, 0.5, "mevalonate → sterol\npathway UP", color=C_UP, fontsize=9, ha="center"
)
fig.tight_layout()
fig.savefig(OUT + "fig3_cholesterol.png")
plt.close(fig)

# ======== FIG 4: paper vs KG log2FC for marker genes ========
val = [  # gene, strain, paper, kg
    ("Ccl28", "C57BL/6J", 2.05, 2.03113),
    ("Hmgcs2", "C57BL/6J", -1.68, -1.65554),
    ("Wnt11", "C57BL/6J", -1.15, -1.36882),
    ("Egr1", "BALB/c", 1.59, 1.59338),
    ("Fos", "BALB/c", 1.60, 1.60151),
    ("Hmgcr", "BALB/c", -1.13, -1.11270),
]
vd = pd.DataFrame(val, columns=["gene", "strain", "paper", "kg"])
fig, ax = plt.subplots(figsize=(6.4, 6.0))
mk = {"C57BL/6J": "o", "BALB/c": "s"}
for st, m in mk.items():
    s = vd[vd.strain == st]
    ax.scatter(
        s.paper,
        s.kg,
        marker=m,
        s=90,
        edgecolor="k",
        c="#8e44ad" if st == "C57BL/6J" else "#e67e22",
        label=st,
        zorder=3,
    )
for _, r in vd.iterrows():
    ax.annotate(
        f"$\\it{{{r.gene}}}$",
        (r.paper, r.kg),
        xytext=(6, -3),
        textcoords="offset points",
        fontsize=9,
    )
lim = [-2.2, 2.4]
ax.plot(lim, lim, "k--", lw=0.8, alpha=0.6, label="y = x")
ax.set_xlim(lim)
ax.set_ylim(lim)
ax.axhline(0, c="#ccc", lw=0.6)
ax.axvline(0, c="#ccc", lw=0.6)
ax.set_xlabel("log2FC reported by Finch et al.")
ax.set_ylabel("log2FC from spoke-genelab")
ax.set_title("Per-gene agreement: publication vs knowledge graph", fontsize=11)
ax.legend(fontsize=9, loc="upper left")
r = np.corrcoef(vd.paper, vd.kg)[0, 1]
ax.text(0.05, -1.9, f"Pearson r = {r:.3f}", fontsize=10)
fig.tight_layout()
fig.savefig(OUT + "fig4_validation.png")
plt.close(fig)
print("wrote 4 figures; per-gene Pearson r =", round(r, 4))
print(
    "C57 distinct DEGs adjp<=0.1:",
    int(sig.sum()),
    "| up:",
    int((df[sig].log2fc > 0).sum()),
    "down:",
    int((df[sig].log2fc < 0).sum()),
)

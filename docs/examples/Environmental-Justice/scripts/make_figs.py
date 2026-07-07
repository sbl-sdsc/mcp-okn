#!/usr/bin/env python3
"""Generate the visualizations for the cumulative EJ-burden analysis (all data from Proto-OKN)."""

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": "#888",
        "axes.linewidth": 0.7,
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    }
)
OUT = "/sessions/amazing-focused-bardeen/mnt/outputs"
FIG = OUT + "/figs"
SRC = "Data: Proto-OKN federated knowledge graphs (spoke-okn, fiokg, scales, ruralkg, sawgraph, geoconnex, nikg) via FRINK SPARQL"
m = pd.read_csv(OUT + "/master_county.csv", dtype={"fips": str})
corr = pd.read_csv(OUT + "/correlations.csv")

# ============ FIG 1: burden x source county matrix (top 30) ============
top = (
    m[m["in_us50"]]
    .sort_values(["burden_agreement", "burden_index"], ascending=False)
    .head(30)
    .copy()
)
dims = ["r_fac", "r_svi", "r_court", "r_rural", "r_servscarce"]
dimlab = [
    "EPA facilities\n(per capita)",
    "Social\nVulnerability",
    "Federal court\n(per capita)",
    "Rurality\n(RUCC)",
    "Service scarcity\n(few SUD tx)",
]
M = top[dims].values.astype(float)
fig, ax = plt.subplots(figsize=(9.2, 11))
cmap = LinearSegmentedColormap.from_list(
    "burd", ["#f7fbff", "#fdd49e", "#e34a33", "#7f0000"]
)
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(dims)))
ax.set_xticklabels(dimlab, fontsize=9)
ax.set_yticks(range(len(top)))
ax.set_yticklabels(
    [
        f"{r['name']}, {r['state']}  (agr {int(r['burden_agreement'])})"
        for _, r in top.iterrows()
    ],
    fontsize=8.5,
)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M[i, j]
        if not np.isnan(v):
            ax.text(
                j,
                i,
                f"{v:.2f}",
                ha="center",
                va="center",
                fontsize=7.3,
                color="white" if v > 0.55 else "#333",
            )
cb = fig.colorbar(im, ax=ax, fraction=0.030, pad=0.02)
cb.set_label("Within-source burden percentile (1 = worst nationally)", fontsize=9)
ax.set_title(
    "Cumulative environmental-justice burden × source, top 30 U.S. counties\nby cross-source agreement (each cell = that county's national percentile on that stressor)",
    fontsize=11.5,
    pad=12,
)
ax.set_xlabel("Burden source (knowledge graph layer)", fontsize=9.5)
fig.text(0.01, 0.005, SRC, fontsize=6.6, color="#666")
plt.savefig(FIG + "/fig1_burden_source_matrix.png")
plt.close()

# ============ FIG 2: indicator correlation heatmap ============
preds = [
    "epa_fac_pc",
    "pfas_fac_pc",
    "enforce_pc",
    "court_pc",
    "rucc",
    "svi",
    "water_pc",
]
predL = {
    "epa_fac_pc": "EPA facilities /10k",
    "pfas_fac_pc": "PFAS-type fac /10k",
    "enforce_pc": "Enforcement /10k",
    "court_pc": "Fed. court /10k",
    "rucc": "Rurality (RUCC)",
    "svi": "Social Vulnerability",
    "water_pc": "Water monitors /10k",
}
outs = [
    "diabetes",
    "obesity",
    "asthma",
    "copd",
    "stroke",
    "cad",
    "hypertension",
    "depression",
    "arteriosclerosis",
    "poverty",
    "uninsured",
    "food_insecurity",
    "unemploy",
    "lt_hs",
]
outL = {
    "diabetes": "Diabetes",
    "obesity": "Obesity",
    "asthma": "Asthma",
    "copd": "COPD",
    "stroke": "Stroke",
    "cad": "Coronary AD",
    "hypertension": "Hypertension",
    "depression": "Depression",
    "arteriosclerosis": "Arteriosclerosis",
    "poverty": "Poverty%",
    "uninsured": "Uninsured%",
    "food_insecurity": "Food insec.%",
    "unemploy": "Unempl.%",
    "lt_hs": "<HS educ.%",
}
P = corr.pivot(index="predictor", columns="outcome", values="r").reindex(
    index=preds, columns=outs
)
fig, ax = plt.subplots(figsize=(12.5, 5.2))
im = ax.imshow(P.values, cmap="RdBu_r", vmin=-0.75, vmax=0.75, aspect="auto")
ax.set_xticks(range(len(outs)))
ax.set_xticklabels([outL[o] for o in outs], rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(len(preds)))
ax.set_yticklabels([predL[p] for p in preds], fontsize=9.5)
for i in range(P.shape[0]):
    for j in range(P.shape[1]):
        v = P.values[i, j]
        if not np.isnan(v):
            ax.text(
                j,
                i,
                f"{v:.2f}",
                ha="center",
                va="center",
                fontsize=7.6,
                color="white" if abs(v) > 0.45 else "#222",
            )
cb = fig.colorbar(im, ax=ax, fraction=0.020, pad=0.015)
cb.set_label("Pearson r (ecological, across counties)", fontsize=9)
ax.set_title(
    "Ecological correlations: environmental / justice / vulnerability burden  vs.  health & SDoH outcomes\n(~3,050–3,130 U.S. counties; blue = positive, red = negative)",
    fontsize=11.5,
    pad=10,
)
ax.axhline(4.5, color="k", lw=1.1)  # separate SVI/rurality from exposure counts
fig.text(
    0.01,
    0.01,
    SRC
    + "  |  Correlations are ecological (county-level); not individual-level causal.",
    fontsize=6.6,
    color="#666",
)
plt.savefig(FIG + "/fig2_correlation_heatmap.png")
plt.close()

# ============ FIG 3: ranked-county bars ============
tb = (
    m[m["in_us50"]]
    .sort_values(["burden_agreement", "burden_index"], ascending=False)
    .head(25)
    .copy()
)
tb = tb.iloc[::-1]
labels = [f"{r['name']}, {r['state']}" for _, r in tb.iterrows()]
colors = plt.cm.YlOrRd(0.35 + 0.6 * (tb["burden_index"].values))
fig, ax = plt.subplots(figsize=(9.6, 8.2))
bars = ax.barh(
    range(len(tb)),
    tb["burden_index"].values,
    color=colors,
    edgecolor="#7f0000",
    linewidth=0.5,
)
ax.set_yticks(range(len(tb)))
ax.set_yticklabels(labels, fontsize=8.6)
for i, (_, r) in enumerate(tb.iterrows()):
    ax.text(
        r["burden_index"] + 0.005,
        i,
        f"agr {int(r['burden_agreement'])}",
        va="center",
        fontsize=7.6,
        color="#7f0000",
    )
ax.set_xlabel(
    "Cumulative burden index (mean of 5 stressor percentiles, 0–1)", fontsize=9.5
)
ax.set_xlim(0, 1.02)
ax.set_title(
    "Top 25 highest cumulative-burden U.S. counties\n(ranked by cross-source agreement, then composite burden index)",
    fontsize=11.5,
    pad=10,
)
ax.grid(axis="x", ls=":", alpha=0.5)
fig.text(0.01, 0.005, SRC, fontsize=6.6, color="#666")
plt.savefig(FIG + "/fig3_ranked_counties.png")
plt.close()

# ============ FIG 4: agreement distribution + coverage ============
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6))
vc = m[m["in_us50"]]["burden_agreement"].value_counts().sort_index()
ax1.bar(vc.index, vc.values, color="#e34a33", edgecolor="#7f0000")
for x, y in zip(vc.index, vc.values, strict=False):
    ax1.text(x, y + 8, str(int(y)), ha="center", fontsize=9)
ax1.set_xlabel("Number of burden sources flagging the county (0–5)")
ax1.set_ylabel("Counties")
ax1.set_title("Cross-source burden agreement across 3,158 U.S. counties", fontsize=11)
cov = {
    "EPA facilities": m["epa_fac"].notna().sum(),
    "PFAS-type fac": m["pfas_fac"].notna().sum(),
    "Enforcement": m["enforce_records"].notna().sum(),
    "Fed. court": m["court_cases"].notna().sum(),
    "RUCC rural": m["rucc"].notna().sum(),
    "SUD services": m["sud_providers"].notna().sum(),
    "Water monitors": m["water_features"].notna().sum(),
    "SVI": m["svi"].notna().sum(),
    "Poverty": m["poverty"].notna().sum(),
    "Disease prev.": m["diabetes"].notna().sum(),
    "PFAS samples": m["pfas_mean_ngL"].notna().sum(),
}
ck = list(cov.keys())
cvv = [cov[k] for k in ck]
cols = ["#2c7fb8"] * 10 + ["#d95f0e"]
ax2.barh(range(len(ck)), cvv, color=cols)
ax2.set_yticks(range(len(ck)))
ax2.set_yticklabels(ck, fontsize=8.8)
for i, v in enumerate(cvv):
    ax2.text(v + 20, i, str(int(v)), va="center", fontsize=8)
ax2.axvline(3143, color="#555", ls="--", lw=0.9)
ax2.text(3143, -0.8, "~3,143 US counties", fontsize=7, color="#555", ha="right")
ax2.set_xlabel("Counties with data")
ax2.set_title(
    "County coverage by Proto-OKN layer\n(orange = state-limited: PFAS = Maine only, 16)",
    fontsize=11,
)
ax2.invert_yaxis()
fig.text(0.01, 0.005, SRC, fontsize=6.6, color="#666")
plt.savefig(FIG + "/fig4_agreement_coverage.png")
plt.close()
print("figures written:", __import__("os").listdir(FIG))

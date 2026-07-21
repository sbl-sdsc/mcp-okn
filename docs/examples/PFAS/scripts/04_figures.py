#!/usr/bin/env python3
"""04_figures.py -- all report figures. Run from the study root."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/sessions/busy-happy-edison/mnt/.claude/skills/okn-report-style/scripts")
from okn_figstyle import apply_style, panel_title, legend_outside, finalize, THEME, UP, DOWN, NEUTRAL
from basemap_vector import draw_basemap

apply_style()
D = os.path.abspath(os.path.join(HERE, "..", "data"))
F = os.path.abspath(os.path.join(HERE, "..", "figures"))
os.makedirs(F, exist_ok=True)

S = json.load(open(os.path.join(D, "stats.json")))
cells = pd.read_csv(os.path.join(D, "cells_scored.tsv"), sep="\t", dtype={"cid": str})
ranked = pd.read_csv(os.path.join(D, "cells_ranked.tsv"), sep="\t", dtype={"cid": str})
tests = pd.read_csv(os.path.join(D, "tests.tsv"), sep="\t")
ind = pd.read_csv(os.path.join(D, "strat_industry.tsv"), sep="\t")
state = pd.read_csv(os.path.join(D, "strat_state.tsv"), sep="\t")
chem = pd.read_csv(os.path.join(D, "strat_analytes.tsv"), sep="\t")
fu = pd.read_csv(os.path.join(D, "strat_functional_use.tsv"), sep="\t")
top20 = pd.read_csv(os.path.join(D, "top20_named.tsv"), sep="\t", dtype={"cid": str})
top20 = top20.merge(cells[["cid", "lon", "lat"]], on="cid", how="left")

TIER_COL = {"A": "#c0392b", "B": "#E69F00", "C": "#0072B2", "D": "#7f8c8d", "N": "#b9bfc7"}
TIER_LAB = {"A": "A  PFAS facility, same cell", "B": "B  PFAS facility, adjacent cell",
            "C": "C  only unflagged facilities", "D": "D  no facility in window",
            "N": "N  screened, no detection"}

# ===================================================================== Figure 1
fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.1),
                         gridspec_kw=dict(width_ratios=[1.15, 1.0, 1.0], wspace=0.42))

ax = axes[0]
steps = ["S2 cells with a\nPFAS sample point", "…with analyte-linked\nobservations",
         "…with ≥1 detection", "…with a regulated\nfacility in window",
         "…with a PFAS-flagged\nfacility in window"]
vals = [S["universe_cells"], S["evaluable_cells"], S["cells_with_detection"],
        S["tierA"] + S["tierB"] + S["tierC"], S["tierAB"]]
bars = ax.barh(range(len(vals))[::-1], vals, color=[NEUTRAL, NEUTRAL, "#0072B2", "#E69F00", "#c0392b"],
               height=0.62)
for i, v in enumerate(vals):
    ax.text(v + 45, len(vals) - 1 - i, f"{v:,}", va="center", fontsize=8.5)
ax.set_yticks(range(len(vals))[::-1])
ax.set_yticklabels(steps, fontsize=8)
ax.set_xlim(0, max(vals) * 1.22)
ax.set_xlabel("S2 Level-13 cells (~1.3 km² each)")
panel_title(ax, "A", "Evidence funnel")

ax = axes[1]
order = ["A", "B", "C", "D", "N"]
cnt = [S[f"tier{t}"] for t in order]
b = ax.bar(range(5), cnt, color=[TIER_COL[t] for t in order], width=0.66)
for i, v in enumerate(cnt):
    ax.text(i, v + 14, f"{v:,}", ha="center", fontsize=8.5)
ax.set_xticks(range(5))
ax.set_xticklabels(order)
ax.set_xlabel("confidence tier")
ax.set_ylabel("cells")
ax.set_ylim(0, max(cnt) * 1.18)
panel_title(ax, "B", "Confidence-tier distribution")
legend_outside(ax, handles=[plt.Rectangle((0, 0), 1, 1, color=TIER_COL[t]) for t in order],
               labels=[TIER_LAB[t] for t in order], where="below", ncol=1, fontsize=7.4)

ax = axes[2]
det = cells[cells["nDet"] > 0]
w = np.array([S["tierA"], S["tierB"], S["tierC"], S["tierD"]], dtype=float)
ax.pie(w, colors=[TIER_COL[t] for t in "ABCD"], radius=0.84, center=(0, 0.10),
       autopct=lambda p: f"{p:.0f}%", pctdistance=0.72,
       textprops=dict(fontsize=8, color="white", weight="bold"),
       wedgeprops=dict(width=0.44, edgecolor="white"))
ax.set_xlim(-1.15, 1.15)
ax.set_ylim(-1.15, 1.30)
ax.set_aspect("equal")
ax.axis("off")
ax.text(0, 0.10, f"{S['cells_with_detection']:,}\ndetection\ncells", ha="center", va="center", fontsize=8.5)
panel_title(ax, "C", "Attribution window of detections")
legend_outside(ax, handles=[plt.Rectangle((0, 0), 1, 1, color=TIER_COL[t]) for t in "ABCD"],
               labels=[TIER_LAB[t] for t in "ABCD"], where="below", ncol=1, fontsize=7.4)
finalize(fig, 1, os.path.join(F, "fig1_evidence_funnel_and_tiers.png"))

# ===================================================================== Figure 2
fig = plt.figure(figsize=(13.0, 6.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.20)

ax = fig.add_subplot(gs[0])
draw_basemap(ax, (-116, 29.5, -66.5, 49.5))
for t in ["D", "C", "B", "A"]:
    sub = cells[cells["tier"] == t]
    ax.scatter(sub["lon"], sub["lat"], s=9 if t in "CD" else 17, c=TIER_COL[t],
               marker="o" if t in "AB" else "s", lw=0.25, edgecolor="white",
               alpha=0.9 if t in "AB" else 0.55, zorder=4 if t in "AB" else 3,
               label=TIER_LAB[t])
ax.set_xlabel("longitude (°E)")
ax.set_ylabel("latitude (°N)")
panel_title(ax, "A", "PFAS sample cells, coterminous US")
legend_outside(ax, where="below", ncol=2, fontsize=7.6)

ax = fig.add_subplot(gs[1])
draw_basemap(ax, (-71.3, 43.0, -66.9, 47.6))
me = cells[cells["stateName"] == "Maine"]
for t in ["D", "C", "B", "A"]:
    sub = me[me["tier"] == t]
    ax.scatter(sub["lon"], sub["lat"], s=11 if t in "CD" else 22, c=TIER_COL[t],
               marker="o" if t in "AB" else "s", lw=0.25, edgecolor="white",
               alpha=0.9 if t in "AB" else 0.5, zorder=4 if t in "AB" else 3)
lab = top20[top20["stateName"] == "Maine"].head(8)
key = []
for _, r in lab.iterrows():
    n = int(r["rank"])
    ax.scatter([r["lon"]], [r["lat"]], s=118, facecolor="none", edgecolor="black",
               lw=0.9, zorder=7)
    ax.annotate(str(n), (r["lon"], r["lat"]), fontsize=7.0, weight="bold", zorder=8,
                ha="center", va="center", color="black",
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
    nm = str(r["colocatedFacilities"]).replace("[ring] ", "").split(";")[0].strip()
    key.append(f"{n}  {nm.title()[:38]}")
ax.set_xlabel("longitude (°E)")
panel_title(ax, "B", "Maine — top-ranked cells (numbered)")
legend_outside(ax, handles=[plt.Line2D([], [], ls="", marker="$%d$" % int(l.split()[0]),
                                       color="black", ms=6) for l in key],
               labels=[l.split("  ", 1)[1] for l in key], where="below", ncol=2, fontsize=6.9,
               title="rank  •  nearest PFAS-flagged facility")
finalize(fig, 3, os.path.join(F, "fig3_map_detection_cells.png"))

# ===================================================================== Figure 3
fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.3), gridspec_kw=dict(wspace=0.36))
order = list("ABCD")


def boxpanel(ax, col, ylab, logy, letter, title):
    data = [ranked.loc[ranked["tier"] == t, col].dropna().values for t in order]
    bp = ax.boxplot(data, positions=range(4), widths=0.55, showfliers=False,
                    patch_artist=True, medianprops=dict(color="black", lw=1.3))
    for patch, t in zip(bp["boxes"], order):
        patch.set_facecolor(TIER_COL[t])
        patch.set_alpha(0.75)
    for i, d in enumerate(data):
        x = np.random.default_rng(7).normal(i, 0.075, size=min(len(d), 400))
        ax.scatter(x, np.random.default_rng(9).choice(d, size=min(len(d), 400), replace=False),
                   s=3, c="#333333", alpha=0.18, zorder=3)
        ax.text(i, ax.get_ylim()[1], "", ha="center")
    if logy:
        ax.set_yscale("log")
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"{t}\nn={len(d)}" for t, d in zip(order, data)], fontsize=8)
    ax.set_xlabel("confidence tier")
    ax.set_ylabel(ylab)
    panel_title(ax, letter, title)
    return data


d1 = boxpanel(axes[0], "maxNgL", "max concentration (ng/L, log)", True, "A",
              "Peak aqueous concentration")
for i, d in enumerate(d1):
    axes[0].text(i, np.median(d) * 1.25, f"{np.median(d):.0f}", ha="center", fontsize=7.6,
                 color="black", weight="bold")
boxpanel(axes[1], "detFreq", "detections / observations", False, "B", "Detection frequency")
boxpanel(axes[2], "nDetAnalytes", "distinct PFAS analytes detected", False, "C", "Analyte breadth")
kw = tests.loc[tests["test"].str.startswith("Kruskal-Wallis, max"), "p"].iloc[0]
axes[0].text(0.5, 0.965, f"Kruskal–Wallis H={S['kw_H_conc']}, p={kw}", transform=axes[0].transAxes,
             ha="center", va="top", fontsize=7.6, color="#444444")
finalize(fig, 2, os.path.join(F, "fig2_proximity_gradient.png"))

# ===================================================================== Figure 4
same = ind[ind["window"] == "same-cell"].sort_values("nCells", ascending=False).head(14)
ring = ind[ind["window"] == "1-ring"].set_index("industryGroup")["nCells"]
same = same[same["industryGroup"] != "No NAICS on record"]
labels = same["industryGroup"].str[:46].tolist()
y = np.arange(len(same))[::-1]
PRIOR_COL = {"High": "#c0392b", "Moderate": "#E69F00", "Low": "#0072B2", "Unclassified": NEUTRAL}
fig, ax = plt.subplots(figsize=(10.4, 5.4))
ax.barh(y + 0.19, same["nCells"], height=0.36,
        color=[PRIOR_COL.get(p, NEUTRAL) for p in same["priorClass"]], label="same cell")
ax.barh(y - 0.19, [ring.get(g, 0) for g in same["industryGroup"]], height=0.36,
        color=[PRIOR_COL.get(p, NEUTRAL) for p in same["priorClass"]], alpha=0.45,
        hatch="///", label="adjacent cell (1-ring)")
for i, (_, r) in enumerate(same.iterrows()):
    ax.text(r["nCells"] + 2, y[i] + 0.19, f"{int(r['nCells'])}", va="center", fontsize=7.6)
    rv = int(ring.get(r["industryGroup"], 0))
    ax.text(rv + 2, y[i] - 0.19, f"{rv}", va="center", fontsize=7.6, color="#555555")
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("PFAS sample cells with ≥1 facility of this industry group")
ax.set_title("PFAS-flagged industry groups co-located with PFAS sample cells", fontsize=11.5)
h = [plt.Rectangle((0, 0), 1, 1, color=PRIOR_COL[k]) for k in ["High", "Moderate", "Low"]]
h += [plt.Rectangle((0, 0), 1, 1, fc="#888888"), plt.Rectangle((0, 0), 1, 1, fc="#888888", alpha=0.45, hatch="///")]
legend_outside(ax, handles=h,
               labels=["source prior: High", "Moderate", "Low", "same cell", "adjacent cell (1-ring)"],
               where="below", ncol=5, fontsize=7.8)
finalize(fig, 5, os.path.join(F, "fig5_industry_colocation.png"))

# ===================================================================== Figure 5
fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.6), gridspec_kw=dict(width_ratios=[1.25, 1.0, 1.0], wspace=0.45))

ax = axes[0]
c = chem[chem["dssLabel"].notna()].head(14).iloc[::-1]
ax.barh(range(len(c)), c["detFreq"] * 100, color="#0072B2", height=0.66)
for i, (_, r) in enumerate(c.iterrows()):
    ax.text(r["detFreq"] * 100 + 0.8, i, f"{r['detFreq']*100:.0f}%  (n={int(r['nObs']):,})", va="center", fontsize=7.2)
ax.set_yticks(range(len(c)))
ax.set_yticklabels([str(x)[:38] for x in c["dssLabel"]], fontsize=7.4)
ax.set_xlim(0, 82)
ax.set_xlabel("detection frequency (% of observations)")
panel_title(ax, "A", "Most-detected PFAS analytes")

ax = axes[1]
f2 = fu.sort_values("nDet", ascending=False)
ax.bar(range(len(f2)), f2["detFreq"] * 100, color=[THEME[i] for i in range(len(f2))], width=0.62)
for i, (_, r) in enumerate(f2.iterrows()):
    ax.text(i, r["detFreq"] * 100 + 2.4, f"{r['detFreq']*100:.1f}%", ha="center", fontsize=7.6)
    ax.text(i, r["detFreq"] * 100 + 0.5, f"{int(r['nAnalytes'])} analyte" + ("s" if int(r["nAnalytes"]) != 1 else ""), ha="center",
            fontsize=6.6, color="#555555")
ax.set_xticks(range(len(f2)))
ax.set_xticklabels([s.replace(" ", "\n") for s in f2["functionalUse"]], fontsize=7.2)
ax.set_ylabel("detection frequency (%)")
ax.set_ylim(0, 34)
ax.set_xlabel("ICE predicted functional-use category")
panel_title(ax, "B", "Detection by predicted use")

ax = axes[2]
cc = chem[chem["nAssayEndpoints"].notna() & chem["dssLabel"].notna()]
sc = ax.scatter(cc["nAssayEndpoints"], cc["detFreq"] * 100, s=22 + cc["nCells"] / 12,
                c=["#c0392b" if isinstance(u, str) else NEUTRAL for u in cc["functionalUse"]],
                alpha=0.8, lw=0.3, edgecolor="white")
offs = [(-8, 7), (-8, -13), (7, -13), (-8, 8)]
for k, (_, r) in enumerate(cc.nlargest(4, "detFreq").iterrows()):
    ax.annotate(str(r["dssLabel"])[:26], (r["nAssayEndpoints"], r["detFreq"] * 100),
                fontsize=6.6, xytext=offs[k], textcoords="offset points",
                ha="left" if offs[k][0] > 0 else "right",
                bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.75))
ax.set_xlim(150, 1750)
ax.set_ylim(-4, 68)
ax.set_xlabel("ToxCast assay endpoints (biobricks-toxcast)")
ax.set_ylabel("detection frequency (%)")
panel_title(ax, "C", "Environmental vs toxicological coverage")
legend_outside(ax, handles=[plt.Line2D([], [], marker="o", ls="", color="#c0392b"),
                            plt.Line2D([], [], marker="o", ls="", color=NEUTRAL)],
               labels=["has ICE predicted use", "no use annotation"], where="below", ncol=1, fontsize=7.4)
finalize(fig, 4, os.path.join(F, "fig4_chemistry_axes.png"))

# ===================================================================== Figure 6
st = state[state["nCells"] >= 5].copy().sort_values("nCells", ascending=False)
fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.4), gridspec_kw=dict(wspace=0.32))
ax = axes[0]
x = np.arange(len(st))
ax.bar(x - 0.2, st["nTierA"], width=0.38, color=TIER_COL["A"], label="tier A (same cell)")
ax.bar(x + 0.2, st["nTierB"], width=0.38, color=TIER_COL["B"], label="tier B (adjacent cell)")
for i, (_, r) in enumerate(st.iterrows()):
    ax.text(i - 0.2, r["nTierA"] + 1.2, int(r["nTierA"]), ha="center", fontsize=7)
    ax.text(i + 0.2, r["nTierB"] + 1.2, int(r["nTierB"]), ha="center", fontsize=7)
ax.set_xticks(x)
ax.set_xticklabels(st["stateName"], rotation=38, ha="right", fontsize=7.8)
ax.set_ylabel("cells")
panel_title(ax, "A", "Facility-attributable detections by state")
ax.legend(loc="upper right", frameon=False, fontsize=8.2)

ax = axes[1]
ax.bar(x, st["detRate"] * 100, color="#0072B2", width=0.6)
for i, (_, r) in enumerate(st.iterrows()):
    ax.text(i, r["detRate"] * 100 + 0.9, f"{r['detRate']*100:.0f}%", ha="center", fontsize=7.2)
    ax.text(i, 1.5, f"{int(r['nCells'])}", ha="center", fontsize=6.8, color="white", weight="bold")
ax.set_xticks(x)
ax.set_xticklabels(st["stateName"], rotation=38, ha="right", fontsize=7.8)
ax.set_ylabel("detections / observations (%)")
ax.set_ylim(0, max(st["detRate"] * 100) * 1.2)
panel_title(ax, "B", "Detection rate by state (n cells in bar)")
finalize(fig, 6, os.path.join(F, "fig6_regional_stratification.png"))

# ===================================================================== Figure 7
t = top20.head(18).iloc[::-1].copy()
t["lab"] = [f"#{int(r['rank'])}  {str(r['colocatedFacilities']).replace('[ring] ','').title()[:52]}"
            for _, r in t.iterrows()]
fig, ax = plt.subplots(figsize=(12.4, 6.0))
cols = [TIER_COL[x] for x in t["tier"]]
ax.barh(range(len(t)), t["score"], color=cols, height=0.68)
for i, (_, r) in enumerate(t.iterrows()):
    conc = "n/a" if pd.isna(r["maxNgL"]) else f"{r['maxNgL']:,.0f} ng/L"
    ax.text(r["score"] + 0.7, i, f"{r['score']:.0f}  •  {conc}  •  {int(r['nDet'])} det",
            va="center", fontsize=7.4)
ax.set_yticks(range(len(t)))
ax.set_yticklabels(t["lab"], fontsize=7.6)
ax.set_xlim(0, 118)
ax.set_xlabel("co-location score (0–100)")
ax.set_title("Top-ranked PFAS sample cells and their co-located regulated facilities", fontsize=11.5)
legend_outside(ax, handles=[plt.Rectangle((0, 0), 1, 1, color=TIER_COL[k]) for k in "AB"],
               labels=[TIER_LAB["A"], TIER_LAB["B"]], where="below", ncol=2, fontsize=7.8)
finalize(fig, 7, os.path.join(F, "fig7_top_ranked_cells.png"))

print("figures written:", sorted(os.listdir(F)))

#!/usr/bin/env python3
"""Instrument-Criticality — all report figures (fig1..fig8)."""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "/sessions/gifted-adoring-thompson/mnt/.claude/skills/"
                   "okn-report-style/scripts")
from okn_figstyle import (THEME, UP, DOWN, NEUTRAL, apply_style, finalize,  # noqa: E402
                          legend_outside, panel_title, ranked_barh,
                          osm_basemap, folium_osm_map, save_map_html)

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG = ROOT / "data", ROOT / "figures"
FIG.mkdir(exist_ok=True)
apply_style()

sci = pd.read_csv(DATA / "instrument_criticality.csv")
full = pd.read_csv(DATA / "instrument_catalogue_full.csv")
stats = json.loads((DATA / "stats.json").read_text())
rc = json.loads((DATA / "risk_classes.json").read_text())
ragree = pd.read_csv(DATA / "route_agreement_matrix.csv", index_col=0)
geo = pd.read_csv(DATA / "geo_paper_country_mentions.csv")
reg = pd.read_csv(DATA / "geo_study_regions.csv")
coh = pd.read_csv(DATA / "cohort_institution_countries.csv")

ROUTES = ["R1_cmMentionPapers", "R1b_platMentionPapers", "R2_cmModelPapers",
          "R3_doiPapers", "R4_modelTitlePubs"]
RLAB = ["R1 instrument\nnamed in paper", "R1b platform\nnamed in paper",
        "R2 named +\nmodel used", "R3 DOI-matched\ndataset use",
        "R4 NASA-side\nmodelling title"]
RSHORT = ["R1", "R1b", "R2", "R3", "R4"]

# ------------------------------------------------------------------ Figure 1
fig, axes = plt.subplots(2, 2, figsize=(12.4, 8.6))

ptype = pd.DataFrame({
    "type": ["Earth Obs.\nSatellites", "Jet /\nPropeller", "Permanent\nLand Sites",
             "Vessels /\nOcean", "UAV /\nVehicles", "Space Stations\n& other space",
             "Balloons /\nRockets", "Models /\nAnalyses"],
    "platforms": [232, 50, 15, 31, 15, 22, 5, 52],
    "instruments": [262, 553, 280, 115, 57, 34, 22, 14]})
x = np.arange(len(ptype))
ax = axes[0, 0]
ax.bar(x - 0.2, ptype["platforms"], 0.4, color=THEME[0], label="platforms")
ax.bar(x + 0.2, ptype["instruments"], 0.4, color=THEME[1], label="instruments")
ax.set_xticks(x)
ax.set_xticklabels(ptype["type"], rotation=40, ha="right", fontsize=8)
ax.set_ylabel("count")
panel_title(ax, "A", "Catalogue by platform type")
legend_outside(ax, where="upper right")

ax = axes[0, 1]
buck = pd.DataFrame({"bucket": ["1", "2", "3-5", "6-10", "11-50", "51-200", "200+"],
                     "n": [28, 15, 24, 42, 202, 163, 447]})
ax.bar(buck["bucket"], buck["n"], color=THEME[4])
ax.set_xlabel("datasets attributed to the instrument (all platforms)")
ax.set_ylabel("instruments")
panel_title(ax, "B", "Dataset attribution is heavy-tailed")
for i, v in enumerate(buck["n"]):
    ax.text(i, v + 6, str(v), ha="center", fontsize=8)

ax = axes[1, 0]
cat = full["category"].value_counts().reindex(
    ["science instrument", "generic GCMD class", "platform/bus subsystem"])
ax.bar(["science\ninstrument", "generic GCMD\nclass label",
        "platform / bus\nsubsystem"], cat.values,
       color=[THEME[2], NEUTRAL, THEME[7]])
ax.set_ylabel("spaceborne instrument labels")
panel_title(ax, "C", "What the 288 spaceborne labels actually are")
for i, v in enumerate(cat.values):
    ax.text(i, v + 3, str(v), ha="center", fontsize=9)

ax = axes[1, 1]
counts = [stats[f"n_route_{r}"] for r in ["R1", "R1b", "R2", "R3", "R4"]]
ax.barh(RSHORT[::-1], counts[::-1], color=[THEME[3], THEME[5], THEME[3],
                                           THEME[0], THEME[0]][::-1])
ax.set_xlabel("science instruments with non-zero signal (of 243)")
panel_title(ax, "D", "Reach of each dependency route")
for i, v in enumerate(counts[::-1]):
    ax.text(v + 1.5, i, str(v), va="center", fontsize=8)
finalize(fig, 1, FIG / "fig1_catalogue_shape.png")

# ------------------------------------------------------------------ Figure 2
fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.0),
                         gridspec_kw={"width_ratios": [1.05, 1]})
ax = axes[0]
m = ragree.values.astype(float)
im = ax.imshow(m, cmap="RdYlBu_r", vmin=0, vmax=1)
ax.set_xticks(range(5)); ax.set_xticklabels(RSHORT, fontsize=9)
ax.set_yticks(range(5)); ax.set_yticklabels(RSHORT, fontsize=9)
for i in range(5):
    for j in range(5):
        ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=8.5,
                color="white" if m[i, j] > 0.62 or m[i, j] < 0.2 else "black")
ax.add_patch(plt.Rectangle((-0.5, -0.5), 3, 3, fill=False, ec="k", lw=1.6, ls=":"))
ax.add_patch(plt.Rectangle((2.5, 2.5), 2, 2, fill=False, ec="k", lw=1.6, ls="--"))
fig.colorbar(im, ax=ax, shrink=0.75, label="Spearman ρ")
panel_title(ax, "A", "Route agreement (··· textual · --- structural)")

ax = axes[1]
cc = sci["corroboration"].value_counts().reindex(range(6)).fillna(0)
cols = [NEUTRAL, THEME[7], THEME[4], THEME[0], THEME[2], THEME[3]]
ax.bar(cc.index, cc.values, color=cols)
ax.set_xlabel("number of independent routes showing dependency (0–5)")
ax.set_ylabel("science instruments")
panel_title(ax, "B", "Corroboration across routes")
for i, v in zip(cc.index, cc.values):
    ax.text(i, v + 1.5, int(v), ha="center", fontsize=9)
finalize(fig, 2, FIG / "fig2_route_agreement.png")

# ------------------------------------------------------------------ Figure 3
top = sci.head(25).copy()
tier_col = {"A": THEME[0], "B": THEME[4], "C": NEUTRAL}
fig, ax = plt.subplots(figsize=(9.6, 8.2))
ranked_barh(ax, top["instr"].tolist(), top["criticality"].tolist(),
            themes=top["tier"].tolist(), theme_colors=tier_col,
            annots=[f"{int(c)}/5 routes · {int(d)} datasets"
                    for c, d in zip(top["corroboration"], top["nDs"])],
            xlabel="criticality score (0–100, MODIS = 100)")
legend_outside(ax, handles=[plt.Rectangle((0, 0), 1, 1, color=tier_col[t])
                            for t in "ABC"],
               labels=["tier A", "tier B", "tier C"], where="lower right",
               title="confidence tier")
finalize(fig, 3, FIG / "fig3_ranked_criticality.png")

# ------------------------------------------------------------------ Figure 4
fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6),
                         gridspec_kw={"width_ratios": [1.15, 1]})
ax = axes[0]
sc = ax.scatter(sci["nDs"], sci["criticality"], s=26,
                c=sci["corroboration"], cmap="viridis", vmin=0, vmax=5,
                edgecolor="white", linewidth=0.4)
ax.set_xscale("log")
ax.set_xlabel("data footprint — datasets attributed (log scale)")
ax.set_ylabel("criticality score")
fig.colorbar(sc, ax=ax, shrink=0.8, label="corroborating routes")
lab = {"MODIS": (-46, 4), "AMSR-E": (-56, 2), "VIIRS": (-42, -12),
       "CERES SCANNER": (-96, 6), "SMMR": (8, 4), "GOME": (-40, 8),
       "WINDSAT": (-58, -4), "GLAS": (-34, 8), "PALSAR": (-46, -4),
       "AQUARIUS_RADIOMETER": (-30, -14), "HARP2": (-46, 6),
       "TEMPO": (-46, -12), "CERES-FM5": (10, -4), "ATLAS": (8, -2)}
for _, r in sci[sci["instr"].isin(lab)].iterrows():
    ax.annotate(r["instr"], (r["nDs"], r["criticality"]), fontsize=7.4,
                xytext=lab[r["instr"]], textcoords="offset points",
                color="#111",
                bbox=dict(fc="white", ec="none", alpha=0.7, pad=0.6))
ax.set_ylim(-6, 112)
panel_title(ax, "A", f"Footprint vs criticality  (ρ = {stats['spearman_rho_footprint_criticality']}, n = 243)")

ax = axes[1]
gap = pd.concat([sci.nlargest(8, "rank_gap"), sci.nsmallest(8, "rank_gap")])
gap = gap.sort_values("rank_gap")
cols = [DOWN if v < 0 else UP for v in gap["rank_gap"]]
ax.barh(range(len(gap)), gap["rank_gap"], color=cols)
ax.set_yticks(range(len(gap)))
ax.set_yticklabels(gap["instr"], fontsize=8)
ax.axvline(0, color="k", lw=0.8)
ax.set_xlabel("footprint rank − criticality rank")
ax.set_xlim(-185, 165)
panel_title(ax, "B", "Where volume and criticality disagree")
legend_outside(ax, handles=[plt.Rectangle((0, 0), 1, 1, color=UP),
                            plt.Rectangle((0, 0), 1, 1, color=DOWN)],
               labels=["more critical than its volume implies",
                       "large volume, little modelling uptake"],
               where="below", ncol=1)
finalize(fig, 4, FIG / "fig4_asymmetry.png")

# ------------------------------------------------------------------ Figure 6
fig, axes = plt.subplots(1, 3, figsize=(14.2, 5.4),
                         gridspec_kw={"width_ratios": [1.15, 1, 1]})
a = pd.DataFrame(rc["A"]).head(12)
ax = axes[0]
ax.barh(range(len(a)), a["criticality"], color=THEME[0])
ax.set_yticks(range(len(a))); ax.set_yticklabels(a["instr"], fontsize=8)
ax.invert_yaxis(); ax.set_xlabel("criticality score")
panel_title(ax, "A", f"Broadly relied on (n={stats['n_class_A']})")

b = pd.DataFrame(rc["B"]).sort_values("criticality", ascending=False
                                      ).reset_index(drop=True)
ax = axes[1]
ax.barh(range(len(b)), b["criticality"], color=THEME[3])
ax.set_xlim(0, b["criticality"].max() * 1.9)
ax.set_yticks(range(len(b))); ax.set_yticklabels(b["instr"], fontsize=9)
ax.invert_yaxis(); ax.set_xlabel("criticality score")
for i, r in b.iterrows():
    note = (r["R5_soleVars"] or r["soleKeyword"] or "")
    note = (note[:26] + "…") if len(str(note)) > 27 else note
    ax.text(r["criticality"] + 0.6, i, str(note), va="center", fontsize=7.5,
            color="#333")
panel_title(ax, "B", f"Narrow but irreplaceable (n={stats['n_class_B']})")

c = pd.DataFrame(rc["C"])
ax = axes[2]
ax.barh(range(len(c)), c["nDs"], color=DOWN)
ax.set_yticks(range(len(c))); ax.set_yticklabels(c["instr"], fontsize=8.5)
ax.invert_yaxis(); ax.set_xlabel("datasets attributed")
for i, r in c.iterrows():
    ax.text(r["nDs"] + 1, i, f"latest {int(r['lastStartYear'])}", va="center",
            fontsize=7.5, color="#333")
panel_title(ax, "C", f"Footprint, no uptake (n={stats['n_class_C']})")
finalize(fig, 6, FIG / "fig6_risk_classes.png")

# ------------------------------------------------------------------ Figure 5
fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.0))
ax = axes[0]
vb = pd.DataFrame({"b": ["1\n(sole)", "2", "3–5", "6–10", "11–25", "26+"],
                   "n": [90, 36, 31, 17, 9, 1]})
cols = [UP] + [THEME[4]] * 5
ax.bar(vb["b"], vb["n"], color=cols)
ax.set_xlabel("distinct instrument names measuring the variable")
ax.set_ylabel("model-produced variables (n = 184)")
panel_title(ax, "A", "Half of model-relevant variables have one measurer")
for i, v in enumerate(vb["n"]):
    ax.text(i, v + 1.5, str(v), ha="center", fontsize=9)

ax = axes[1]
sr = pd.read_csv(DATA / "sole_measured_variables_resolved.csv")
fam = (sr.dropna(subset=["aliasFamily"]).groupby("aliasFamily")["variable"]
         .nunique().sort_values(ascending=True))
strict = dict(zip(sci["instr"], sci["R5_nSoleVars"]))
STRICT_NAME = {"MODIS": "MODIS", "GOME-2": "GOME-2", "GEDI": "GEDI"}
cols = [THEME[2] if f in STRICT_NAME else NEUTRAL for f in fam.index]
ax.barh(range(len(fam)), fam.values, color=cols)
for i, f in enumerate(fam.index):
    if f in STRICT_NAME:
        ax.barh(i, strict.get(STRICT_NAME[f], 0), color=THEME[0])
ax.set_yticks(range(len(fam)))
ax.set_yticklabels(fam.index, fontsize=8.5)
ax.set_xlabel("model-produced variables this instrument alone measures")
panel_title(ax, "B", "Irreplaceable capability: strict vs alias-resolved")
legend_outside(ax, handles=[plt.Rectangle((0, 0), 1, 1, color=THEME[0]),
                            plt.Rectangle((0, 0), 1, 1, color=THEME[2]),
                            plt.Rectangle((0, 0), 1, 1, color=NEUTRAL)],
               labels=["visible to the strict GCMD-label join (scored)",
                       "same instrument, additional aliases",
                       "visible only after alias resolution (not scored)"],
               where="below")
finalize(fig, 5, FIG / "fig5_substitutability.png")

# ------------------------------------------------------------------ Figure 7
fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.4))
ax = axes[0]
ct = coh.nlargest(15, "nAuthorOrcids").sort_values("nAuthorOrcids")
ax.barh(ct["iso2"], ct["nAuthorOrcids"], color=THEME[0])
ax.set_xlabel("ORCID-identified authors on the 651 shared papers")
panel_title(ax, "A", "Where the boundary-spanning cohort sits")
for i, (_, r) in enumerate(ct.iterrows()):
    ax.text(r["nAuthorOrcids"] + 12, i, int(r["nAuthorOrcids"]), va="center",
            fontsize=8)

ax = axes[1]
tail = coh.sort_values("nAuthorOrcids")
ax.plot(np.arange(1, len(tail) + 1),
        np.cumsum(tail["nAuthorOrcids"].values[::-1]) /
        tail["nAuthorOrcids"].sum(), color=THEME[5], lw=2)
ax.axhline(0.8, color=NEUTRAL, ls=":", lw=1)
n80 = int(np.searchsorted(np.cumsum(tail["nAuthorOrcids"].values[::-1]) /
                          tail["nAuthorOrcids"].sum(), 0.8) + 1)
ax.axvline(n80, color=NEUTRAL, ls=":", lw=1)
ax.set_xlabel("countries ranked by cohort size")
ax.set_ylabel("cumulative share of cohort")
ax.text(n80 + 2, 0.55, f"{n80} of {len(coh)} countries\nhold 80% of the cohort",
        fontsize=8.5)
panel_title(ax, "B", "Concentration of the cohort")
finalize(fig, 7, FIG / "fig7_community.png")

# ------------------------------------------------------------------ Figure 8
reg2 = reg[reg["nPapers"] >= 1].copy()
fig, ax = plt.subplots(figsize=(13.0, 6.8))
basemap = "OpenStreetMap"
try:
    osm_basemap(ax, lons=reg2["lon"], lats=reg2["lat"],
                values=reg2["nPapers"], size=(reg2["nPapers"] ** 0.62) * 11,
                cmap="YlOrRd",
                colorbar_label="climate-modelling papers naming the region")
except Exception as exc:  # OSM tile server unreachable from the sandbox
    print("[fig8] OSM tiles unavailable, using bundled land mask:", exc)
    plt.close(fig)
    basemap = "land mask"
    from global_land_mask import globe
    lat_g = np.arange(-89.75, 90, 0.5)
    lon_g = np.arange(-179.75, 180, 0.5)
    LO, LA = np.meshgrid(lon_g, lat_g)
    land = globe.is_land(LA, LO).astype(float)
    fig, ax = plt.subplots(figsize=(13.0, 6.8))
    ax.imshow(land, extent=[-180, 180, -90, 90], origin="lower",
              cmap=plt.matplotlib.colors.ListedColormap(["#dbe9f2", "#e9e5dc"]),
              interpolation="nearest", aspect="auto", zorder=0)
    ax.contour(lon_g, lat_g, land, levels=[0.5], colors="#8a9aa5",
               linewidths=0.6, zorder=1)
    sc = ax.scatter(reg2["lon"], reg2["lat"],
                    s=(reg2["nPapers"] ** 0.62) * 13, c=reg2["nPapers"],
                    cmap="YlOrRd", norm=plt.matplotlib.colors.LogNorm(vmin=1),
                    edgecolor="#333", lw=0.5, zorder=3)
    fig.colorbar(sc, ax=ax, shrink=0.72,
                 label="climate-modelling papers naming the region")
    ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
    ax.set_xlabel("longitude (°E)"); ax.set_ylabel("latitude (°N)")
    ax.grid(alpha=0.18, lw=0.5, zorder=2)
    off = {"Southern Ocean": (8, 8), "Pacific Ocean": (10, 6),
           "Arctic": (10, 6), "Mediterranean Sea": (14, 16),
           "Atlantic Ocean": (8, -16), "Middle East": (16, -12),
           "South Eastern Asia": (12, 8), "Sahel": (-16, -16),
           "Sahara": (-8, 12), "Northern Africa": (-70, 10)}
    for _, r in reg2.nlargest(10, "nPapers").iterrows():
        ax.annotate(r["name"], (r["lon"], r["lat"]), fontsize=8.2, zorder=5,
                    xytext=off.get(r["name"], (6, 6)),
                    textcoords="offset points", color="#111",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color="#444"),
                    bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.0))
print(f"[fig8] basemap = {basemap}")
finalize(fig, 8, FIG / "fig8_study_regions_map.png")

# interactive folium map (embedded in the HTML report)
m = folium_osm_map(reg2.to_dict("records"), lat_key="lat", lon_key="lon",
                   popup_keys=["name", "fcode", "nPapers"],
                   value_key="nPapers", tooltip_key="name")
save_map_html(m, DATA / "study_regions_map.html")
print("[map] wrote data/study_regions_map.html")

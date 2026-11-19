"""Build all figures, data extracts and stats.json for the Chronic-Disease-Burden study.

Usage: python scripts/build_figures.py <raw_query_csv_dir> <counties_geojson>
The raw dir holds data/qNN.csv exactly as written by create_jupyter_notebook.
"""
import glob
import json
import os
import sys

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm
from scipy.cluster.hierarchy import dendrogram

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis as A  # noqa: E402
import okn_figstyle as F  # noqa: E402

ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, "figures")
DAT = os.path.join(ROOT, "data")
if os.environ.get("OKN_OUT"):  # notebook mode: write figures/ and outputs/ beside the notebook
    FIG = os.path.join(os.environ["OKN_OUT"], "figures")
    DAT = os.path.join(os.environ["OKN_OUT"], "outputs")
os.makedirs(FIG, exist_ok=True)
os.makedirs(DAT, exist_ok=True)

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
GEO = sys.argv[2] if len(sys.argv) > 2 else "counties.json"
data = {os.path.basename(f)[:-4]: pd.read_csv(f, dtype={"fips": str}) for f in glob.glob(os.path.join(RAW, "q*.csv"))}

F.apply_style()
OI = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000", "#999999"]
REGCOL = {"South": "#D55E00", "Midwest": "#0072B2", "West": "#009E73", "Northeast": "#CC79A7"}

# ------------------------------------------------------------------ data
m, chr_ = A.build_county_table(data)
m, pc1_var, pc1_load = A.add_scores(m)
val = A.validate_against_chr(m)
summ = A.summary_stats(m)
rob = A.robustness(m)
top10 = A.top_by_disease(m, 10)
statec = A.state_concentration(m)

geo = gpd.read_file(GEO)
geo["fips"] = geo["id"].astype(str).str.zfill(5)
g = geo.merge(m, on="fips", how="inner")
conus = g[~g["state"].isin(["AK", "HI"])].to_crs(5070)
states = conus.dissolve(by="state")[["geometry"]]

mor, w = A.morans(conus, A.DKEYS + ["burden_z"])
lisa, lisa_p = A.local_hotspots(conus, "burden_z", w)
conus["lisa"] = lisa
m = m.merge(conus[["fips", "lisa"]], on="fips", how="left")
m["lisa"] = m["lisa"].fillna("n/a (AK/HI)")

raw = A.spearman_matrix(m)
order, Z = A.cluster_order(raw)
part, n_part = A.partial_spearman(m, A.DEMOGRAPHIC)
part_full, _ = A.partial_spearman(m, A.DEMOGRAPHIC + A.BEHAVIOURAL)
ws = A.within_state(m)
pairs = A.pair_table(raw, part, ws, len(m))
conf = A.confounder_matrix(m)
r2 = A.variance_explained(m)
gene_t, J, NG, gsize = A.gene_overlap(data)
mantel_raw = A.mantel(J, raw.loc[A.DKEYS, A.DKEYS])
mantel_part = A.mantel(J, part.loc[A.DKEYS, A.DKEYS])
mondo = A.mondo_map(data)

# ------------------------------------------------------------------ extracts
keep = ["fips", "name", "state", "region", "pop_places", "n_places", "eligible"] + A.DKEYS + [
    "burden_z", "burden_pct", "burden_pc1", "cardiometabolic_z", "respiratory_z", "burden_no_dep_z",
    "n_top_quintile", "tier", "burden_rank", "burden_rank_eligible", "lisa", "chr_diabetes", "chr_obesity"] + list(A.CONFOUNDERS)
ranked = m[keep].sort_values("burden_z", ascending=False)
ranked.to_csv(os.path.join(DAT, "county_burden_ranked.tsv"), sep="\t", index=False)
top10.to_csv(os.path.join(DAT, "top10_by_condition.tsv"), sep="\t", index=False)
summ.to_csv(os.path.join(DAT, "condition_summary.tsv"), sep="\t", index=False)
val.to_csv(os.path.join(DAT, "validation_places_vs_chr.tsv"), sep="\t", index=False)
pairs.to_csv(os.path.join(DAT, "correlation_pairs.tsv"), sep="\t", index=False)
mor.to_csv(os.path.join(DAT, "morans_I.tsv"), sep="\t", index=False)
gene_t.to_csv(os.path.join(DAT, "shared_gene_overlap.tsv"), sep="\t", index=False)
r2.to_csv(os.path.join(DAT, "variance_explained.tsv"), sep="\t", index=False)
statec.to_csv(os.path.join(DAT, "state_concentration.tsv"), sep="\t")
mondo.to_csv(os.path.join(DAT, "doid_mondo_map.tsv"), sep="\t", index=False)

# ------------------------------------------------------------------ figure 1: design
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.axis("off")
boxes = [
    (0.02, 0.58, 0.22, 0.32, "spoke-okn\nPREVALENCE_DpL\nCDC PLACES, 9 measures\n27,365 places (26,343 valued)", "#E8F1FA"),
    (0.02, 0.10, 0.22, 0.32, "spoke-okn\nPREVALENCEIN_SpL\nCounty Health Rankings 2023\n14 county measures", "#FBEFE3"),
    (0.30, 0.58, 0.20, 0.32, "PARTOF_LpL place→county\npopulation-weighted mean\n3,057 counties / 50 states + DC", "#E8F1FA"),
    (0.30, 0.10, 0.20, 0.32, "CHR county table\n3,131 counties\n(diabetes, obesity +\n10 covariates)", "#FBEFE3"),
    (0.56, 0.34, 0.20, 0.32, "County table\n(validation: PLACES vs CHR)\ncomposite burden score\nMoran's I / LISA", "#EAF6EE"),
    (0.82, 0.58, 0.17, 0.32, "Correlation clustering\n+ partial / within-state\nconfounder checks", "#F3ECF7"),
    (0.82, 0.10, 0.17, 0.32, "spoke-okn ASSOCIATES_DaG\n+ ubergraph DOID→MONDO\nshared-gene overlap", "#F3ECF7"),
]
for x, y, wd, ht, txt, col in boxes:
    ax.add_patch(mpatches.FancyBboxPatch((x, y), wd, ht, boxstyle="round,pad=0.01", fc=col, ec="#555", lw=0.8))
    ax.text(x + wd / 2, y + ht / 2, txt, ha="center", va="center", fontsize=8.5)
for (x1, y1, x2, y2) in [(0.24, 0.74, 0.30, 0.74), (0.24, 0.26, 0.30, 0.26), (0.50, 0.74, 0.56, 0.56),
                         (0.50, 0.26, 0.56, 0.44), (0.76, 0.56, 0.82, 0.70), (0.76, 0.44, 0.82, 0.30)]:
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="->", color="#444", lw=1))
ax.set_title("Study design: OKN county chronic-disease burden", fontsize=11.5, loc="left")
F.finalize(fig, 1, os.path.join(FIG, "fig1_study_design.png"))

# ------------------------------------------------------------------ figure 2: validation
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
for ax, (k, ck, letter) in zip(axes, [("diabetes", "chr_diabetes", "A"), ("obesity", "chr_obesity", "B")]):
    d = m[[k, ck, "region"]].dropna()
    for reg, col in REGCOL.items():
        s = d[d.region == reg]
        ax.scatter(s[ck], s[k], s=6, alpha=0.45, color=col, label=reg, lw=0)
    lim = [min(d[k].min(), d[ck].min()) - 1, max(d[k].max(), d[ck].max()) + 1]
    ax.plot(lim, lim, color="#333", lw=0.8, ls="--")
    v = val[val.condition == A.LABEL[k]].iloc[0]
    ax.text(0.03, 0.96, f"r = {v.pearson_r:.2f}, ρ = {v.spearman_rho:.2f}\nmean diff = {v.mean_diff_pp:+.1f} pp\nn = {int(v.n):,}",
            transform=ax.transAxes, va="top", fontsize=8.5)
    ax.set_xlabel(f"CHR 2023 county {A.LABEL[k].lower()} (%)")
    ax.set_ylabel(f"PLACES place-aggregated {A.LABEL[k].lower()} (%)")
    F.panel_title(ax, letter, A.LABEL[k])
F.legend_outside(axes[1], where="right", title="Census region")
F.finalize(fig, 2, os.path.join(FIG, "fig2_validation_places_vs_chr.png"))

# ------------------------------------------------------------------ figure 3: distributions
fig, ax = plt.subplots(figsize=(10, 4.6))
ordk = summ.sort_values("median", ascending=False)["condition"].tolist()
keys = [k for lab in ordk for k in A.DKEYS if A.LABEL[k] == lab]
bp = ax.boxplot([m[k].dropna() for k in keys], vert=False, patch_artist=True, widths=0.6,
                flierprops=dict(markersize=2, alpha=0.4), medianprops=dict(color="#000"))
for patch, k in zip(bp["boxes"], keys):
    patch.set_facecolor("#9ecae1")
ax.set_yticks(range(1, len(keys) + 1))
ax.set_yticklabels([f"{A.LABEL[k]}  (P90/P10 = {summ.set_index('condition').loc[A.LABEL[k], 'fold_p90_p10']:.2f})" for k in keys])
ax.invert_yaxis()
ax.set_xlabel("County age-adjusted prevalence (%), n = 3,057 counties")
ax.set_title("Between-county spread of nine chronic conditions (CDC PLACES via spoke-okn)", loc="left")
F.finalize(fig, 3, os.path.join(FIG, "fig3_prevalence_distributions.png"))

# ------------------------------------------------------------------ figure 4: small-multiple maps
fig, axes = plt.subplots(3, 3, figsize=(13, 8.6))
for ax, k in zip(axes.flat, A.DKEYS):
    q = np.nanquantile(conus[k], [0, .2, .4, .6, .8, 1])
    norm = BoundaryNorm(q, 256)
    conus.plot(column=k, ax=ax, cmap="YlOrRd", norm=norm, linewidth=0, edgecolor="none")
    states.boundary.plot(ax=ax, color="#555", linewidth=0.25)
    ax.set_axis_off()
    ax.set_title(A.LABEL[k], fontsize=10.5)
    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=norm)
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.04, pad=0.01, ticks=q)
    cb.ax.set_xticklabels([f"{v:.1f}" for v in q], fontsize=7)
fig.suptitle("County prevalence by condition, quintile classes (%), contiguous US", fontsize=11.5, x=0.01, ha="left")
F.finalize(fig, 4, os.path.join(FIG, "fig4_condition_maps.png"))

# ------------------------------------------------------------------ figure 5: composite + LISA
fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
q = np.nanquantile(conus["burden_z"], [0, .2, .4, .6, .8, .95, 1])
norm = BoundaryNorm(q, 256)
conus.plot(column="burden_z", ax=axes[0], cmap="RdPu", norm=norm, linewidth=0)
states.boundary.plot(ax=axes[0], color="#555", linewidth=0.3)
sm = plt.cm.ScalarMappable(cmap="RdPu", norm=norm)
cb = fig.colorbar(sm, ax=axes[0], orientation="horizontal", fraction=0.045, pad=0.02, ticks=q)
cb.ax.set_xticklabels([f"{v:.2f}" for v in q], fontsize=7)
cb.set_label("composite burden (mean z of 9 conditions); classes = quintiles + top 5%", fontsize=8)
F.panel_title(axes[0], "A", "Composite disease-burden score")
lc = {"HH": "#b2182b", "LL": "#2166ac", "HL": "#f4a582", "LH": "#92c5de", "ns": "#eeeeee"}
for lab, col in lc.items():
    s = conus[conus.lisa == lab]
    if len(s):
        s.plot(ax=axes[1], color=col, linewidth=0)
states.boundary.plot(ax=axes[1], color="#555", linewidth=0.3)
F.panel_title(axes[1], "B", "Local Moran's I clusters (pseudo-p < 0.05)")
names = {"HH": "High–High (hot spot)", "LL": "Low–Low (cold spot)", "HL": "High–Low outlier", "LH": "Low–High outlier", "ns": "not significant"}
F.legend_outside(axes[1], [mpatches.Patch(color=lc[k]) for k in lc], [f"{names[k]} (n={int((conus.lisa == k).sum())})" for k in lc],
                 where="below", ncol=3)
for ax in axes:
    ax.set_axis_off()
F.finalize(fig, 5, os.path.join(FIG, "fig5_composite_burden_hotspots.png"))

# ------------------------------------------------------------------ figure 6: top counties + multimorbidity
fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw={"width_ratios": [1.5, 1]})
t = m[m.eligible].nlargest(25, "burden_z").iloc[::-1]
axes[0].barh(range(len(t)), t["burden_z"], color=[REGCOL[r] for r in t.region])
axes[0].set_yticks(range(len(t)))
axes[0].set_yticklabels(t["name"], fontsize=8)
for i, (_, r) in enumerate(t.iterrows()):
    axes[0].text(r.burden_z + 0.02, i, f"{int(r.n_top_quintile)}/9", va="center", fontsize=7.5)
axes[0].set_xlabel("composite burden score (mean z); label = conditions in top quintile")
F.panel_title(axes[0], "A", "Top 25 counties (places cover ≥ 1,000 residents)")
F.theme_legend(axes[0], REGCOL, where="lower right", title="region")
cnt = m["n_top_quintile"].value_counts().sort_index()
cols = ["#bbbbbb" if i < 3 else ("#fdae6b" if i < A.MULTI_K else ("#e6550d" if i < 7 else "#a63603")) for i in cnt.index]
axes[1].bar(cnt.index, cnt.values, color=cols)
for x, y in cnt.items():
    axes[1].text(x, y + 15, str(y), ha="center", fontsize=7.5)
axes[1].set_xlabel("number of the 9 conditions with county in top quintile")
axes[1].set_ylabel("counties")
axes[1].set_xticks(range(0, 10))
F.panel_title(axes[1], "B", "Multimorbidity concentration")
F.theme_legend(axes[1], {"Tier A (7–9)": "#a63603", "Tier B (5–6)": "#e6550d", "Tier C (3–4)": "#fdae6b", "below tiers": "#bbbbbb"},
               where="upper right", title="tier")
F.finalize(fig, 6, os.path.join(FIG, "fig6_top_counties_multimorbidity.png"))

# ------------------------------------------------------------------ figure 7: clustered heatmaps
fig = plt.figure(figsize=(15, 5.6))
gs = fig.add_gridspec(2, 3, height_ratios=[0.6, 3], hspace=0.05, wspace=0.42)
labs = [A.LABEL[k] for k in order]
axd = fig.add_subplot(gs[0, 0])
dendrogram(Z, ax=axd, labels=None, color_threshold=0, above_threshold_color="#555", no_labels=True)
axd.set_axis_off()
for j, (mat, title, letter) in enumerate([(raw, "Unadjusted Spearman ρ", "A"),
                                          (part, "Partial ρ | demographics", "B"),
                                          (ws, "Within-state ρ", "C")]):
    ax = fig.add_subplot(gs[1, j])
    M = mat.loc[order, order].to_numpy()
    im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(9))
    ax.set_yticks(range(9))
    ax.set_xticklabels(labs, rotation=60, ha="right", fontsize=8)
    ax.set_yticklabels(labs if j == 0 else [""] * 9, fontsize=8)
    for a in range(9):
        for b in range(9):
            ax.text(b, a, f"{M[a, b]:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(M[a, b]) > 0.6 else "black")
    ax.set_title(f"{letter}   {title}", fontsize=10, loc="left", fontweight="bold")
cax = fig.add_axes([0.935, 0.2, 0.01, 0.55])
fig.colorbar(im, cax=cax, label="Spearman ρ")
F.finalize(fig, 7, os.path.join(FIG, "fig7_clustered_correlation_heatmaps.png"))

# ------------------------------------------------------------------ figure 8: confounders
fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
C = conf.loc[order]
im = axes[0].imshow(C.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
axes[0].set_xticks(range(C.shape[1]))
axes[0].set_xticklabels([A.CONFOUNDERS[c] for c in C.columns], rotation=40, ha="right", fontsize=8)
axes[0].set_yticks(range(9))
axes[0].set_yticklabels(labs, fontsize=8)
for a in range(C.shape[0]):
    for b in range(C.shape[1]):
        axes[0].text(b, a, f"{C.iloc[a, b]:.2f}", ha="center", va="center", fontsize=6.5,
                     color="white" if abs(C.iloc[a, b]) > 0.6 else "black")
fig.colorbar(im, ax=axes[0], fraction=0.03, label="Spearman ρ")
F.panel_title(axes[0], "A", "Condition × county covariate (CHR 2023)")
R = r2.set_index("condition").loc[labs]
y = np.arange(9)
axes[1].barh(y - 0.27, R["R2_demographic"], 0.27, color="#0072B2", label="demographic (7)")
axes[1].barh(y, R["R2_demo_behavioural"], 0.27, color="#E69F00", label="+ behavioural (3)")
axes[1].barh(y + 0.27, R["R2_demo_behav_state"], 0.27, color="#009E73", label="+ state fixed effects")
axes[1].set_yticks(y)
axes[1].set_yticklabels(labs, fontsize=8)
axes[1].invert_yaxis()
axes[1].set_xlim(0, 1)
axes[1].set_xlabel("OLS R²")
F.panel_title(axes[1], "B", "Variance explained")
F.legend_outside(axes[1], where="below", ncol=3)
F.finalize(fig, 8, os.path.join(FIG, "fig8_confounders_variance_explained.png"))

# ------------------------------------------------------------------ figure 9: genes vs geography
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
gt = gene_t.merge(pairs[["a", "b", "rho_raw", "rho_partial_demo"]], on=["a", "b"])
for ax, col, letter, ttl, mt in [(axes[0], "rho_raw", "A", "unadjusted", mantel_raw),
                                 (axes[1], "rho_partial_demo", "B", "demographic-adjusted", mantel_part)]:
    ax.scatter(gt["jaccard"], gt[col], s=28, color="#0072B2", alpha=0.8)
    LAB = {("diabetes", "obesity"): (-60, 8), ("high_chol", "stroke"): (-40, 8), ("diabetes", "stroke"): (4, 3),
           ("chd", "copd"): (4, -9), ("obesity", "depression"): (4, 3), ("diabetes", "hypertension"): (4, 3)}
    for _, r in gt.iterrows():
        off = LAB.get((r.a, r.b))
        if col == "rho_partial_demo" and (r.a, r.b) == ("chd", "copd"):
            off = (6, 2)
        if col == "rho_partial_demo" and (r.a, r.b) == ("diabetes", "stroke"):
            off = (5, -11)
        if off:
            ax.annotate(r.pair, (r.jaccard, r[col]), fontsize=7, xytext=off, textcoords="offset points")
    ax.set_xlabel("shared-gene Jaccard index (spoke-okn ASSOCIATES_DaG)")
    ax.set_ylabel(f"geographic Spearman ρ ({ttl})")
    ax.text(0.97, 0.04, f"Mantel ρ = {mt[0]:.2f}, p = {mt[1]:.2f}\n36 condition pairs", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=8.5)
    F.panel_title(ax, letter, f"Gene sharing vs county co-variation ({ttl})")
F.finalize(fig, 9, os.path.join(FIG, "fig9_gene_overlap_vs_geography.png"))

# ------------------------------------------------------------------ stats.json
tierc = m["tier"].value_counts()
hh = conus[conus.lisa == "HH"]
top1 = m[m.eligible].nlargest(1, "burden_z").iloc[0]
pt = pairs.set_index("pair")


def pr(a, b, col="rho_raw"):
    return round(float(pairs[((pairs.a == a) & (pairs.b == b)) | ((pairs.a == b) & (pairs.b == a))][col].iloc[0]), 2)


S = {
    "n_places_total": 27365, "n_places_valued": 26343, "n_places_unlinked": 1207,
    "n_counties_places": int(len(m)), "n_counties_chr": int(chr_["fips"].nunique()),
    "n_counties_eligible": int(m.eligible.sum()), "n_states": int(m.state.nunique()),
    "n_conditions": 9, "min_pop": A.MIN_POP,
    "val_diab_r": round(float(val.iloc[0].pearson_r), 2), "val_diab_diff": round(float(val.iloc[0].mean_diff_pp), 2),
    "val_ob_r": round(float(val.iloc[1].pearson_r), 2), "val_ob_diff": round(float(val.iloc[1].mean_diff_pp), 2),
    "pc1_var_pct": round(100 * pc1_var, 1),
    "rob_min": round(float(rob.to_numpy()[np.triu_indices(5, 1)].min()), 3),
    "tier_A": int(tierc.get("A", 0)), "tier_B": int(tierc.get("B", 0)), "tier_C": int(tierc.get("C", 0)),
    "tier_AB": int(tierc.get("A", 0) + tierc.get("B", 0)),
    "n_HH": int((conus.lisa == "HH").sum()), "n_LL": int((conus.lisa == "LL").sum()),
    "HH_south_pct": round(100 * (hh.region == "South").mean(), 1),
    "moran_burden": round(float(mor.set_index("variable").loc["burden_z", "morans_I"]), 2),
    "moran_min": round(float(mor.morans_I.min()), 2), "moran_max": round(float(mor.morans_I.max()), 2),
    "top1_name": top1["name"], "top1_z": round(float(top1.burden_z), 2),
    "rho_diab_stroke": pr("diabetes", "stroke"), "rho_chd_copd": pr("chd", "copd"),
    "rho_diab_obes": pr("diabetes", "obesity"), "rho_diab_obes_part": pr("diabetes", "obesity", "rho_partial_demo"),
    "rho_ob_asthma": pr("obesity", "asthma"), "rho_ob_asthma_part": pr("obesity", "asthma", "rho_partial_demo"),
    "rho_diab_dep": pr("diabetes", "depression"), "rho_copd_dep": pr("copd", "depression"),
    "rho_diab_asthma": pr("diabetes", "asthma"), "rho_diab_asthma_ws": pr("diabetes", "asthma", "rho_within_state"),
    "mean_atten": round(float(pairs.attenuation.mean()), 2),
    "r2_diab_demo": round(float(r2.set_index("condition").loc["Diabetes", "R2_demographic"]), 2),
    "r2_asthma_demo": round(float(r2.set_index("condition").loc["Asthma", "R2_demographic"]), 2),
    "r2_asthma_state": round(float(r2.set_index("condition").loc["Asthma", "R2_demo_behav_state"]), 2),
    "r2_dep_demo": round(float(r2.set_index("condition").loc["Depression", "R2_demographic"]), 2),
    "r2_dep_state": round(float(r2.set_index("condition").loc["Depression", "R2_demo_behav_state"]), 2),
    "n_genes_bg": NG, "gene_pairs_sig": int((gene_t.fdr < 0.05).sum()),
    "mantel_raw": round(mantel_raw[0], 2), "mantel_raw_p": round(mantel_raw[1], 2),
    "mantel_part": round(mantel_part[0], 2), "mantel_part_p": round(mantel_part[1], 2),
    "diab_p10": round(float(summ.iloc[0].p10), 1), "diab_p90": round(float(summ.iloc[0].p90), 1),
    "diab_max": round(float(summ.iloc[0]["max"]), 1), "copd_fold": round(float(summ.set_index("condition").loc["COPD", "fold_p90_p10"]), 2),
    "life_exp_flagged": int(chr_.life_exp_flag.sum()),
    "tierA_south": int((m[m.tier == "A"].region == "South").sum()),
    "tierA_south_pct": round(100 * (m[m.tier == "A"].region == "South").mean(), 1),
    "pop_covered_m": round(float(m.pop_places.sum()) / 1e6, 1),
    "n_conus": int(len(conus)),
    "mean_rho_raw": round(float(raw.to_numpy()[np.triu_indices(9, 1)].mean()), 2),
    "mean_rho_part": round(float(part.to_numpy()[np.triu_indices(9, 1)].mean()), 2),
    "mean_rho_full": round(float(part_full.to_numpy()[np.triu_indices(9, 1)].mean()), 2),
    "mean_rho_ws": round(float(ws.to_numpy()[np.triu_indices(9, 1)].mean()), 2),
    "n_partial": int(n_part),
    "n_ineligible": int((~m.eligible).sum()),
    "kg_spoke_version": "v0.0.6", "kg_uber_version": "v0.0.2",
}
for s_, n_ in statec.head(5)["n_high"].items():
    S[f"st_{s_}"] = int(n_)
json.dump(S, open(os.path.join(DAT, "stats.json"), "w"), indent=1)
print(json.dumps({k: S[k] for k in list(S)[:30]}, indent=1))
print(mor.round(3).to_string())
print(statec.head(10))
print(pairs.round(2).head(8).to_string())

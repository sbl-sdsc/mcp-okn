"""Render every report figure through the shared okn_figstyle helpers."""
import json, sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
sys.path.insert(0, __file__.rsplit('/',1)[0])
from okn_figstyle import (apply_style, panel_title, legend_outside, finalize,
                          diverging_heatmap, ranked_barh, UP, DOWN, NEUTRAL, THEME, FONT)
apply_style()
F = 'Liver-Lipid/figures'
S = json.load(open('Liver-Lipid/data/stats.json'))
core = pd.read_csv('Liver-Lipid/data/ranked_candidates.tsv', sep='\t')
de   = pd.read_csv('Liver-Lipid/data/liver_de_measured.tsv', sep='\t', dtype={'entrez':str})
go   = pd.read_csv('Liver-Lipid/data/enrichment_go_bp.tsv', sep='\t')
rx   = pd.read_csv('Liver-Lipid/data/enrichment_reactome.tsv', sep='\t')
sens = pd.read_csv('Liver-Lipid/data/enrichment_threshold_sensitivity.tsv', sep='\t')

# ---------------- Figure 1: the reproducible slice ----------------
fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.3))
ax = axes[0]
rows = [("GLDS-25\nSTS-135 · 13 d\nC57BL/6 · array", 1, "clean"),
        ("GLDS-47\nRR-1 CASIS · 21 d\nC57BL/6 · RNA-seq", 1, "clean"),
        ("GLDS-137\nRR-3 · 42 d\nBALB/c · RNA-seq", 1, "clean"),
        ("GLDS-168\nRR-1 NASA · 37 d\nC57BL/6 · RNA-seq", 9, "confounded")]
cols = {"clean": "#009E73", "confounded": "#D55E00"}
y = np.arange(len(rows))[::-1]
ax.barh(y, [r[1] for r in rows], color=[cols[r[2]] for r in rows], height=.55)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=FONT["tick"])
ax.set_xlabel("liver Space-Flight vs Ground-Control assays"); ax.set_xlim(0, 11)
for yy, r in zip(y, rows):
    ax.text(r[1] + .25, yy, "clean" if r[2] == "clean" else "all 9 confounded",
            va="center", fontsize=FONT["caption"], color="#333")
panel_title(ax, "A", "Contrast vetting of the paper's 4 datasets")
from matplotlib.patches import Patch
legend_outside(ax, [Patch(color=cols[k], label=k) for k in cols], list(cols), where="below", ncol=2)

ax = axes[1]
lab = ["GLDS-25\n(OSD-25)", "GLDS-47\n(OSD-47)", "GLDS-137\n(OSD-137)"]
val = [S["osd25_measured"], S["osd47_measured"], S["osd137_measured"]]
b = ax.bar(lab, val, color=THEME[0], width=.55)
ax.set_yscale("log"); ax.set_ylabel("genes with a stored DE result (log scale)")
ax.set_ylim(1, 2e4)
for r, v in zip(b, val):
    ax.text(r.get_x() + r.get_width()/2, v*1.25, f"{v:,}", ha="center", fontsize=FONT["annot"])
panel_title(ax, "B", "Depth of the stored liver DE payload")

ax = axes[2]
x = np.arange(3); w = .38
up   = [S["deg_osd25"] - 30, S["deg_osd47"] - 8, S["deg_osd137"]]
down = [30, 8, 0]
ax.bar(x - w/2, up, w, color=UP, label="up in flight")
ax.bar(x + w/2, down, w, color=DOWN, label="down in flight")
ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=FONT["tick"])
ax.set_ylabel("differentially expressed genes")
for i, (u, d) in enumerate(zip(up, down)):
    ax.text(i - w/2, u + 1.5, str(u), ha="center", fontsize=FONT["annot"])
    ax.text(i + w/2, d + 1.5, str(d), ha="center", fontsize=FONT["annot"])
panel_title(ax, "C", "DEGs at adj-p ≤ 0.05, |log2FC| ≥ 1")
legend_outside(ax, where="below", ncol=2)
finalize(fig, 1, f"{F}/fig1_reproducible_slice.png")

# ---------------- Figure 2: effect landscape ----------------
fig, ax = plt.subplots(figsize=(9.6, 5.8))
d = de.copy(); d["nlp"] = -np.log10(d.adj_p_value.clip(lower=1e-12))
ax.scatter(d.log2fc, d.nlp, s=8, color="#d4dade", zorder=1)
deg = d[(d.adj_p_value <= .05) & (d.log2fc.abs() >= 1)]
MK = {"OSD-25": "o", "OSD-47": "s", "OSD-137": "^"}
for osd, mk in MK.items():
    g = deg[deg.osd == osd]
    ax.scatter(g.log2fc, g.nlp, s=34, marker=mk, zorder=3,
               color=[UP if v > 0 else DOWN for v in g.log2fc], edgecolor="k", linewidth=.35)
named = {"Pnpla3": (6, -10), "Pnpla2": (7, 3), "Cidec": (7, 0), "Fgf21": (7, -3),
         "Mlxipl": (-42, -9), "Sult1e1": (7, 0), "Acot2": (8, 3), "Depp1": (-44, -9),
         "Apoa4": (-40, -4), "Plin5": (-34, 12), "Pex11a": (7, 3), "Elovl6": (-42, 8)}
seen = set()
for _, r in deg.iterrows():
    if r.symbol in named and r.symbol not in seen:
        seen.add(r.symbol)
        ax.annotate(r.symbol, (r.log2fc, r.nlp), textcoords="offset points",
                    xytext=named[r.symbol], fontsize=FONT["annot"], color="#111")
ax.axvline(1, ls=":", c="#888", lw=.9); ax.axvline(-1, ls=":", c="#888", lw=.9)
ax.axhline(-np.log10(.05), ls=":", c="#888", lw=.9)
ax.set_xlabel("log2 fold change (Space Flight vs Ground Control)")
ax.set_ylabel("\u2212log10 adjusted p")
from matplotlib.lines import Line2D
h = [Line2D([], [], ls="", marker="o", ms=5, color="#d4dade", label="measured, below threshold"),
     Line2D([], [], ls="", marker="o", ms=6, mfc="w", mec="k", label="GLDS-25 (OSD-25)"),
     Line2D([], [], ls="", marker="s", ms=6, mfc="w", mec="k", label="GLDS-47 (OSD-47)"),
     Line2D([], [], ls="", marker="^", ms=6, mfc="w", mec="k", label="GLDS-137 (OSD-137)"),
     Line2D([], [], ls="", marker="o", ms=6, color=UP,   label="up in flight"),
     Line2D([], [], ls="", marker="o", ms=6, color=DOWN, label="down in flight")]
legend_outside(ax, h, [x.get_label() for x in h], where="right",
               title="shape = dataset · colour = direction")
finalize(fig, 2, f"{F}/fig2_effect_landscape.png")

# ---------------- Figure 3: GO + Reactome ----------------
fig, axes = plt.subplots(1, 2, figsize=(13.8, 4.6))
g = go.head(9).copy()
ranked_barh(axes[0], [(str(l)[:43] + "…") if len(str(l)) > 44 else str(l) for l in g.label], (-np.log10(g.p)).tolist(),
            annots=[f"{f:.1f}× · k={k}/{K} · FDR {q:.3f}" for f, k, K, q in zip(g.fold, g.k, g.K, g.fdr)],
            xlabel="−log10 p")
axes[0].axvline(-np.log10(.05), ls=":", c="#555", lw=1)
panel_title(axes[0], "A", "GO biological process (prokn)")
r = rx.copy()
ranked_barh(axes[1], [(str(l)[:56] + "…") if len(str(l)) > 57 else str(l) for l in r.label], (-np.log10(r.p)).tolist(),
            annots=[f"{f:.1f}× · k={k}/{K} · FDR {q:.3f}" for f, k, K, q in zip(r.fold, r.k, r.K, r.fdr)],
            xlabel="−log10 p")
axes[1].axvline(-np.log10(.05), ls=":", c="#555", lw=1)
panel_title(axes[1], "B", "Reactome pathway (prokn)")
finalize(fig, 3, f"{F}/fig3_enrichment.png")

# ---------------- Figure 4: three disease suppliers ----------------
fig, axes = plt.subplots(1, 2, figsize=(13.6, 4.8))
ax = axes[0]
sets = [("rdkg\ncurated MONDO\nliver disease", S["rdkg_fold"], S["rdkg_K"], S["rdkg_k"], "0.0074", "#009E73"),
        ("digcfdekg\nEFO 'NAFLD'\ntrait set",    S["nafld_fold"], S["nafld_K"], S["nafld_k"], S["nafld_p"], "#0072B2"),
        ("spoke-okn\nDOID:409 bucket",           S["sok_fold"],  S["sok_K"],  S["sok_k"],  "0.72",   "#D55E00")]
x = np.arange(3)
ax.bar(x, [s[1] for s in sets], color=[s[5] for s in sets], width=.5)
ax.axhline(1, ls="--", c="#555", lw=1)
ax.set_xticks(x); ax.set_xticklabels([s[0] for s in sets], fontsize=FONT["tick"])
ax.set_ylabel("fold enrichment (observed / expected)"); ax.set_ylim(0, 4.4)
for i, s in enumerate(sets):
    ax.text(i, s[1] + .12, f"k={s[3]}/{s[2]}\np={s[4]}", ha="center", fontsize=FONT["annot"])
panel_title(ax, "A", "Liver-disease gene-set over-representation, by supplier")

ax = axes[1]
top = core.head(16)
axes_lbl = ["rdkg\ndisease", "digcfdekg\nNAFLD", "spoke-okn\nDOID", "prokn\nlipid", "oard-kg\nHP"]
cols_bool = ["liver_disease_rdkg", "nafld_trait_digcfdekg", "liver_disease_spokeokn",
             "lipid_pathway", "phenotype_linked"]
colr = ["#009E73", "#0072B2", "#D55E00", "#CC79A7", "#E69F00"]
for j, (c, cc) in enumerate(zip(cols_bool, colr)):
    for i, present in enumerate(top[c].tolist()):
        ax.add_patch(plt.Rectangle((j - .40, i - .40), .80, .80,
                     facecolor=cc if present else "#f2f4f6",
                     edgecolor="#ffffff", linewidth=1.4))
ax.set_xlim(-.5, len(axes_lbl) - .5); ax.set_ylim(len(top) - .5, -.5)
ax.set_xticks(range(len(axes_lbl))); ax.set_xticklabels(axes_lbl, fontsize=FONT["tick"])
ax.set_yticks(range(len(top))); ax.set_yticklabels(list(top.humanSymbol), fontsize=FONT["tick"] + 1)
ax.set_ylabel(""); ax.tick_params(length=0)
for sp in ax.spines.values(): sp.set_visible(False)
panel_title(ax, "B", "Evidence axes for the top-16 ranked genes")
finalize(fig, 4, f"{F}/fig4_disease_evidence.png")

# ---------------- Figure 5: threshold sensitivity ----------------
fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.4))
ax = axes[0]
lbls = ["workflow rule\n|log2FC| ≥ 1", "paper's rule\nFC ≥ 1.2"]
sig  = [S["sig_in_go_bg"], S["paper_sig_in_go_bg"]]
ax.bar(lbls, sig, color=[THEME[2], THEME[5]], width=.5)
ax.axhline(S["bg_go"], ls="--", c="#555", lw=1)
ax.text(1.42, S["bg_go"] * .96, f"annotated background\nN = {S['bg_go']:,}",
        fontsize=FONT["annot"], ha="right", va="top", color="#444")
ax.set_ylabel("signature genes inside the GO background"); ax.set_ylim(0, 2500)
for i, v in enumerate(sig):
    ax.text(i, v + 55, f"{v:,}  ({v/S['bg_go']:.0%})", ha="center", fontsize=FONT["annot"])
panel_title(ax, "A", "Signature size against the testable universe")

ax = axes[1]
for (name, colr) in [("workflow rule  |log2FC| >= 1", THEME[2]), ("paper's rule   FC >= 1.2 (|log2FC| >= 0.263)", THEME[5])]:
    s = sens[(sens.threshold == name) & (sens.family == "GO")]
    ax.scatter(s.fold, -np.log10(s.p), s=16, alpha=.65, color=colr,
               label="workflow rule" if colr == THEME[2] else "paper's rule")
ax.axhline(-np.log10(.05), ls=":", c="#555", lw=1); ax.axvline(1, ls="--", c="#555", lw=1)
ax.set_xscale("log"); ax.set_xlabel("fold enrichment (log scale)"); ax.set_ylabel("−log10 p")
panel_title(ax, "B", "Every GO term tested, at both thresholds")
legend_outside(ax, where="below", ncol=2)
finalize(fig, 5, f"{F}/fig5_threshold_sensitivity.png")

# ---------------- Figure 6: ranked candidates ----------------
fig, ax = plt.subplots(figsize=(9.6, 6.4))
top = core.head(20)
tc = {"A": "#009E73", "B": "#0072B2", "C": NEUTRAL}
ranked_barh(ax, list(top.humanSymbol), top.score.tolist(),
            themes=list(top.tier), theme_colors=tc,
            annots=[f"log2FC {v:+.2f} · {n} KG{'s' if n > 1 else ''}" for v, n in zip(top.log2fc, top.n_sources)],
            xlabel="integrated evidence score")
from okn_figstyle import theme_legend
theme_legend(ax, tc, where="below", title="confidence tier")
finalize(fig, 6, f"{F}/fig6_ranked_candidates.png")

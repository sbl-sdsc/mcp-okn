"""Figures for the Alzheimer's disease OKN cross-KG knowledge map."""
import sys, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/scripts")
sys.path.insert(0, "/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/data")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from okn_figstyle import (apply_style, panel_title, legend_outside, ranked_barh,
                          finalize, THEME, UP, DOWN, NEUTRAL, osm_basemap)
import rdkg_ad_layers as R, prokn_drug_targets as P

apply_style()
D = "/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/data/"
F = "/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/figures/"
rank = pd.read_csv(D + "ad_ranked_genes.csv")

# ---------------------------------------------------------------- Figure 1
def fig1():
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.2), gridspec_kw=dict(wspace=0.55, width_ratios=[1.25, 1, 1]))
    ax = axes[0]
    contrib = [("spoke-okn", 180, "curated"), ("digcfdekg", 842, "genetic"),
               ("prokn", 90, "genetic"), ("biomarkerkg", 919, "genetic"),
               ("gene-expr-atlas", 964, "differential"), ("rdkg", 101, "curated")]
    contrib.sort(key=lambda t: t[1])
    cmap = {"curated": THEME[0], "genetic": THEME[1], "differential": THEME[2]}
    ax.barh([c[0] for c in contrib], [c[1] for c in contrib],
            color=[cmap[c[2]] for c in contrib], edgecolor="white")
    for i, c in enumerate(contrib):
        ax.text(c[1] + 15, i, str(c[1]), va="center", fontsize=8)
    ax.set_xlabel("distinct genes contributed to the AD gene space")
    ax.set_xlim(0, 1120)
    panel_title(ax, "A", "Gene contribution per knowledge graph")
    h = [plt.Rectangle((0, 0), 1, 1, color=cmap[k]) for k in cmap]
    legend_outside(ax, h, list(cmap.keys()), where="below", title="evidence type", ncol=3)

    ax = axes[1]
    ns = rank.n_sources.value_counts().sort_index()
    ax.bar(ns.index.astype(str), ns.values, color=[THEME[7]] * 2 + [THEME[0]] * 6, edgecolor="white")
    for x, v in zip(range(len(ns)), ns.values):
        ax.text(x, v * 1.06, str(v), ha="center", fontsize=8)
    ax.set_yscale("log"); ax.set_ylim(0.8, 6000)
    ax.set_xlabel("number of independent KG sources supporting the gene")
    ax.set_ylabel("genes (log scale)")
    panel_title(ax, "B", "Cross-KG corroboration")

    ax = axes[2]
    td = rank.tier.value_counts().reindex(["A", "B", "C"])
    cols = [UP, THEME[1], NEUTRAL]
    ax.bar(td.index, td.values, color=cols, edgecolor="white")
    for x, v in zip(range(3), td.values):
        ax.text(x, v * 1.06, f"{v}", ha="center", fontsize=8)
    ax.set_yscale("log"); ax.set_ylim(0.8, 6000)
    ax.set_ylabel("genes (log scale)"); ax.set_xlabel("confidence tier")
    panel_title(ax, "C", "Confidence-tier distribution")
    finalize(fig, 1, F + "fig1_design_overview.png")

# ---------------------------------------------------------------- Figure 2
def fig2():
    top = rank[rank.tier == "A"].head(28).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(15, 8.4), gridspec_kw=dict(wspace=0.42, width_ratios=[1.15, 1]))
    ax = axes[0]
    themes = np.where(top.druggable == 1, "has drug/probe in prokn", "no drug edge")
    tc = {"has drug/probe in prokn": THEME[5], "no drug edge": THEME[0]}
    ranked_barh(ax, list(top.gene), list(top.score), themes=list(themes), theme_colors=tc,
                annots=[f"{s} KG · {e} ev-types" for s, e in zip(top.n_sources, top.n_evidence_types)],
                xlabel="composite consensus score")
    panel_title(ax, "A", "Top 28 Tier-A consensus AD genes")

    ax = axes[1]
    mat = top[["n_sources", "n_evidence_types", "n_secondary", "de_regions"]].copy()
    mat["variants"] = np.minimum(top.n_uniprot_variants, 12)
    mat["PIGEAN"] = top.pigean_score.fillna(0)
    m = mat.values.astype(float)
    m = m / np.nanmax(m, axis=0)
    im = ax.imshow(m, aspect="auto", cmap="magma", vmin=0, vmax=1)
    ax.set_yticks(range(len(top))); ax.set_yticklabels(top.gene, fontsize=8)
    ax.set_xticks(range(mat.shape[1]))
    ax.set_xticklabels(["KG\nsources", "evidence\ntypes", "secondary\nsupport", "DE brain\nregions",
                        "UniProt\nvariants", "PIGEAN\nscore"], fontsize=8)
    cb = plt.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    cb.set_label("column-normalised evidence (0–1)", fontsize=8); cb.ax.tick_params(labelsize=7)
    panel_title(ax, "B", "Evidence axes kept separate (not merged)")
    finalize(fig, 2, F + "fig2_consensus_genes.png")

# ---------------------------------------------------------------- Figure 3
def fig3():
    go = pd.read_csv(D + "enrichment_GO.csv")
    fig, axes = plt.subplots(1, 3, figsize=(17.5, 7.6), gridspec_kw=dict(wspace=1.25))
    for ax, ns, letter, ttl in zip(axes,
            ["Biological Process", "Molecular Function", "Cellular Component"],
            "ABC", ["GO Biological Process", "GO Molecular Function", "GO Cellular Component"]):
        d = go[(go.ns == ns) & (go.fdr < 0.05)].head(14).iloc[::-1]
        ax.barh(range(len(d)), d.fold, color=THEME[0] if ns == "Biological Process" else
                (THEME[2] if ns == "Molecular Function" else THEME[3]), edgecolor="white")
        ax.set_yticks(range(len(d)))
        ax.set_yticklabels([l if len(l) < 42 else l[:40] + "…" for l in d.goLabel], fontsize=8)
        for i, (f, k, K, q) in enumerate(zip(d.fold, d.k, d.K, d.fdr)):
            ax.text(f + max(d.fold) * 0.02, i, f"{f:.0f}× ({k}/{K})", va="center", fontsize=7)
        ax.set_xlim(0, max(d.fold) * 1.36)
        ax.set_xlabel("fold enrichment (observed / expected)")
        panel_title(ax, letter, ttl)
    finalize(fig, 3, F + "fig3_go_enrichment.png")

# ---------------------------------------------------------------- Figure 4
def fig4():
    rx = pd.read_csv(D + "enrichment_Reactome.csv")
    d = rx[rx.fdr < 0.05].head(20).iloc[::-1]
    def theme(l):
        if "NOTCH" in l.upper(): return "Notch / γ-secretase substrate"
        if "Amyloid" in l: return "amyloid"
        if any(t in l for t in ["p75NTR", "NRIF", "NTRK2", "ERBB4", "EPH", "EGFR"]): return "neurotrophin / RTK"
        if any(t in l for t in ["MHC", "Neutrophil", "CSF1"]): return "immune / microglial"
        return "other"
    th = [theme(l) for l in d.pwLabel]
    tc = {"amyloid": UP, "Notch / γ-secretase substrate": THEME[1], "neurotrophin / RTK": THEME[2],
          "immune / microglial": THEME[0], "other": NEUTRAL}
    fig, ax = plt.subplots(figsize=(11.5, 8.2))
    ranked_barh(ax, [l if len(l) < 62 else l[:60] + "…" for l in d.pwLabel], list(d.fold),
                themes=th, theme_colors=tc,
                annots=[f"{k}/{K}, FDR {q:.1e}" for k, K, q in zip(d.k, d.K, d.fdr)],
                xlabel="fold enrichment (observed / expected)")
    panel_title(ax, "A", "Reactome pathway over-representation (FDR < 0.05)")
    finalize(fig, 4, F + "fig4_reactome_enrichment.png")

# ---------------------------------------------------------------- Figure 5
def fig5():
    de = pd.read_csv(D + "gxa_ad_de.csv")
    cons = pd.read_csv(D + "gxa_ad_de_consensus.csv")
    core = ["entorhinal cortex", "hippocampus", "middle temporal gyrus",
            "posterior cingulate cortex", "superior frontal gyrus"]
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6), gridspec_kw=dict(wspace=0.5, width_ratios=[1.15, 1, 1.1]))
    ax = axes[0]
    g = de[de.region.isin(core)].groupby(["region", "dir"]).sym.nunique().unstack().fillna(0)
    g = g.loc[core]
    y = np.arange(len(g))
    ax.barh(y - 0.2, g["up"], height=0.38, color=UP, edgecolor="white", label="up-regulated")
    ax.barh(y + 0.2, g["down"], height=0.38, color=DOWN, edgecolor="white", label="down-regulated")
    ax.set_yticks(y); ax.set_yticklabels([r.replace(" ", "\n") for r in g.index], fontsize=8)
    ax.set_xlabel("differentially expressed genes (adj. p ≤ 0.05)")
    panel_title(ax, "A", "DE burden by brain region")
    legend_outside(ax, where="below", ncol=2, title="direction")

    ax = axes[1]
    b = cons[cons.consistent >= 2].groupby("consistent").size()
    ax.bar(b.index.astype(int).astype(str), b.values, color=THEME[0], edgecolor="white")
    for x, v in zip(range(len(b)), b.values):
        ax.text(x, v * 1.05, str(v), ha="center", fontsize=8)
    ax.set_yscale("log"); ax.set_ylim(0.8, 3000)
    ax.set_xlabel("brain regions with concordant direction")
    ax.set_ylabel("genes (log scale)")
    panel_title(ax, "B", "Regional replication of DE")

    ax = axes[2]
    five = cons[cons.consistent >= 5].copy()
    five["net"] = np.where(five.up > five.down, 1, -1)
    five = five.sort_values("net")
    ax.barh(range(len(five)), five.net * five.consistent,
            color=[UP if n > 0 else DOWN for n in five.net], edgecolor="white")
    ax.set_yticks(range(len(five))); ax.set_yticklabels(five.sym, fontsize=8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("regions concordant  (blue = down, red = up)")
    panel_title(ax, "C", "Genes DE in all 5 limbic/cortical regions")
    finalize(fig, 5, F + "fig5_expression.png")

# ---------------------------------------------------------------- Figure 6
def fig6():
    tiers = pd.read_csv(D + "prokn_ad_drug_tiers.csv")
    tgt = pd.DataFrame(P.PAIRS, columns=["drug", "target"])
    MECH = {"APP": "amyloid", "BACE1": "amyloid", "MAPT": "tau", "GSK3B": "tau",
            "ACHE": "cholinergic", "CHRNA7": "cholinergic", "CHRM1": "cholinergic",
            "CHRM2": "cholinergic", "CHRM3": "cholinergic",
            "HTR6": "monoamine / neuropsychiatric", "HTR1A": "monoamine / neuropsychiatric",
            "HTR2A": "monoamine / neuropsychiatric", "HTR2C": "monoamine / neuropsychiatric",
            "HTR4": "monoamine / neuropsychiatric", "DRD1": "monoamine / neuropsychiatric",
            "DRD2": "monoamine / neuropsychiatric", "SLC6A2": "monoamine / neuropsychiatric",
            "SLC6A3": "monoamine / neuropsychiatric", "SLC6A4": "monoamine / neuropsychiatric",
            "MAOB": "monoamine / neuropsychiatric", "HRH3": "monoamine / neuropsychiatric",
            "PTGS2": "neuroinflammation", "AGER": "neuroinflammation", "MAPK14": "neuroinflammation",
            "SEMA4D": "neuroinflammation", "CD38": "neuroinflammation", "PLA2G7": "neuroinflammation",
            "MMP1": "neuroinflammation", "MMP7": "neuroinflammation", "MMP8": "neuroinflammation",
            "MMP13": "neuroinflammation", "CSF1R": "neuroinflammation",
            "HMGCR": "lipid / vascular", "CETP": "lipid / vascular", "PPARA": "lipid / vascular",
            "PPARG": "lipid / vascular", "AGTR1": "lipid / vascular", "SLC5A2": "lipid / vascular",
            "SLC12A1": "lipid / vascular", "VDR": "lipid / vascular",
            "ABL1": "kinase / proteostasis", "SRC": "kinase / proteostasis", "KIT": "kinase / proteostasis",
            "PDGFRB": "kinase / proteostasis", "EPHA2": "kinase / proteostasis",
            "FGFR3": "kinase / proteostasis", "FKBP1A": "kinase / proteostasis",
            "HDAC1": "epigenetic", "HDAC2": "epigenetic", "HDAC3": "epigenetic", "HDAC6": "epigenetic",
            "SV2A": "synaptic", "CACNA1B": "synaptic", "GABRB3": "synaptic", "FLNA": "synaptic",
            "PDE4D": "synaptic", "PDE5A": "synaptic", "PDE9A": "synaptic", "IMPA1": "synaptic"}
    tgt["mech"] = tgt.target.map(MECH).fillna("other / hormonal")
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.4), gridspec_kw=dict(wspace=0.5, width_ratios=[1, 1.1]))
    ax = axes[0]
    m = tgt.groupby("mech").drug.nunique().sort_values()
    ax.barh(m.index, m.values, color=[THEME[i % 10] for i in range(len(m))], edgecolor="white")
    for i, v in enumerate(m.values):
        ax.text(v + 0.4, i, str(v), va="center", fontsize=8)
    ax.set_xlabel("distinct AD-indicated compounds with a target in this class")
    ax.set_xlim(0, m.max() * 1.2)
    panel_title(ax, "A", "Therapeutic mechanism classes")

    ax = axes[1]
    ap = tiers[tiers.approval.notna()].copy()
    bins = np.arange(1940, 2031, 5)
    ax.hist(ap.approval, bins=bins, color=THEME[0], edgecolor="white")
    ax.set_xlabel("year of first regulatory approval (any indication)")
    ax.set_ylabel("AD-indicated compounds")
    ax.axvline(1996, color=UP, ls="--", lw=1.2)
    ax.text(1996.5, ax.get_ylim()[1] * 0.92, "donepezil (1996)", fontsize=7.5, color=UP)
    ax.axvline(2003, color=UP, ls="--", lw=1.2)
    ax.text(2003.5, ax.get_ylim()[1] * 0.80, "memantine (2003)", fontsize=7.5, color=UP)
    panel_title(ax, "B", "Approval vintage of the repurposing pool (n=%d)" % len(ap))
    finalize(fig, 6, F + "fig6_therapeutics.png")

# ---------------------------------------------------------------- Figure 7
def fig7():
    bm = pd.read_csv(D + "biomarkerkg_ad_raw.csv")
    import re as _re
    risk = bm[bm.rel == "indicates_risk_of_developing"].drop_duplicates("bLabel")
    genes = [m.group(1) for m in (_re.search(r"in gene ([^/]+)/", str(s)) for s in risk.bLabel) if m]
    gs = pd.Series(genes).value_counts().head(18).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.6), gridspec_kw=dict(wspace=0.62, width_ratios=[1, 1.1]))
    ax = axes[0]
    apoe = {"NECTIN2", "TOMM40", "APOC1", "APOE", "BCAM", "CBLC", "RELB", "BCL3", "CEACAM16-AS1", "CLPTM1"}
    cols = [UP if g in apoe else THEME[0] for g in gs.index]
    ax.barh(range(len(gs)), gs.values, color=cols, edgecolor="white")
    ax.set_yticks(range(len(gs))); ax.set_yticklabels(gs.index, fontsize=8)
    for i, v in enumerate(gs.values):
        ax.text(v + 0.6, i, str(v), va="center", fontsize=8)
    ax.set_xlabel("distinct dbSNP risk variants annotated to the gene")
    ax.set_xlim(0, gs.max() * 1.2)
    h = [plt.Rectangle((0, 0), 1, 1, color=UP), plt.Rectangle((0, 0), 1, 1, color=THEME[0])]
    legend_outside(ax, h, ["APOE region (chr19q13)", "elsewhere in the genome"], where="below", ncol=2)
    panel_title(ax, "A", "Genetic risk markers (biomarkerkg)")

    ax = axes[1]
    prog = ["TSPO", "CHI3L1", "GFAP", "ICAM1", "TREM2", "S100B", "CCL2", "VCAM1"]
    prog_cls = ["microglial", "astroglial", "astroglial", "endothelial", "microglial",
                "astroglial", "chemokine", "endothelial"]
    diag = ["Aβ42 (plasma)", "Aβ40 (plasma)", "p-tau181 (plasma)", "quinolinic acid (urine)",
            "CRH (plasma)", "testosterone (plasma/urine)"]
    y = list(range(len(prog)))
    ccl = {"microglial": THEME[0], "astroglial": THEME[1], "endothelial": THEME[2], "chemokine": THEME[3]}
    ax.barh(y, [1] * len(prog), color=[ccl[c] for c in prog_cls], edgecolor="white")
    ax.set_yticks(y); ax.set_yticklabels(prog, fontsize=9)
    ax.set_xticks([]); ax.set_xlim(0, 2.6)
    for i, c in enumerate(prog_cls):
        ax.text(1.05, i, c, va="center", fontsize=8)
    ax.set_xlabel("all 8 are 'prognostic for' AD in biomarkerkg (n = 8 of 8)")
    panel_title(ax, "B", "Prognostic biomarker panel is entirely neuroinflammatory")
    h = [plt.Rectangle((0, 0), 1, 1, color=ccl[k]) for k in ccl]
    legend_outside(ax, h, list(ccl.keys()), where="below", ncol=4, title="cell-type origin")
    finalize(fig, 7, F + "fig7_biomarkers.png")

# ---------------------------------------------------------------- Figure 8
REGION = {
 "Western Europe":"AT BE CH DE DK FI FR GB IE IS IT LI LU MC MT NL NO PT SE ES SM AD GR CY",
 "Central & Eastern Europe":"AL BA BG BY CZ EE HR HU LT LV MD ME MK PL RO RS RU SI SK UA GE AM AZ",
 "North America":"US CA BM GL PM",
 "Latin America & Caribbean":"AR BO BR BS BZ CL CO CR CU DM DO EC GD GT GY HN HT JM MX NI PA PE PR PY SR SV TT UY VC VE KN LC VI AG BB",
 "East & South-East Asia":"CN JP KR KP TW HK MO MN SG MY TH VN PH ID KH LA MM BN TL",
 "South & Central Asia":"IN PK BD LK NP BT MV AF KZ KG TJ TM UZ",
 "Middle East & North Africa":"AE BH DZ EG IL IQ IR JO KW LB LY MA OM QA SA SY TN TR YE",
 "Sub-Saharan Africa":"AO BF BI BJ BW CD CF CG CI CM CV DJ ER ET GA GH GM GN GQ GW KE KM LR LS MG ML MR MU MW MZ NA NE NG RW SC SD SL SN SO SS ST SZ TD TG TZ UG ZA ZM ZW",
 "Oceania":"AU NZ FJ PG SB VU WS TO TV KI NR PW FM MH CK NU TK AS GU MP",
}
ISO2REG = {c: r for r, cs in REGION.items() for c in cs.split()}

def fig8():
    pv = pd.read_csv(D + "spoke_ad_prevalence_2019.csv")
    pv["region"] = pv.iso.map(ISO2REG).fillna("unassigned")
    fig, axes = plt.subplots(1, 2, figsize=(15.8, 6.6), gridspec_kw=dict(wspace=0.62, width_ratios=[1.1, 1]))
    ax = axes[0]
    g = pv[pv.region != "unassigned"].groupby("region").mid
    order = g.median().sort_values().index
    data = [pv[pv.region == r].mid.values for r in order]
    bp = ax.boxplot(data, vert=False, widths=0.62, patch_artist=True,
                    medianprops=dict(color="black", lw=1.4), flierprops=dict(marker="o", ms=3, mfc=NEUTRAL, mec="none"))
    for i, b in enumerate(bp["boxes"]):
        b.set(facecolor=THEME[i % 10], alpha=0.85, edgecolor="white")
    ax.set_yticklabels([f"{r}\n(n={len(pv[pv.region==r])})" for r in order], fontsize=8)
    ax.set_xlabel("age-standardised AD prevalence, 2019 (%)")
    ax.axvline(pv.mid.median(), color=NEUTRAL, ls="--", lw=1.1)
    ax.text(pv.mid.median() + 0.04, 0.55, f"global median {pv.mid.median():.2f}%", fontsize=7.5, color="#444")
    panel_title(ax, "A", "Prevalence by world region (200 countries)")

    ax = axes[1]
    t = pv.head(16).iloc[::-1]
    err = np.vstack([t.mid - t.lower, t.upper - t.mid])
    cols = [THEME[list(REGION).index(ISO2REG.get(i, "Oceania")) % 10] for i in t.iso]
    ax.barh(range(len(t)), t.mid, xerr=err, color=cols, edgecolor="white",
            error_kw=dict(ecolor="#333", lw=1, capsize=2.5))
    ax.set_yticks(range(len(t))); ax.set_yticklabels(t.label, fontsize=8)
    ax.set_xlabel("prevalence (%), midpoint with reported 95% interval")
    ax.axvline(pv.mid.median(), color=NEUTRAL, ls="--", lw=1.1)
    panel_title(ax, "B", "16 highest-prevalence countries")
    finalize(fig, 8, F + "fig8_prevalence.png")

def fig8_map_html():
    """Interactive OSM map for the HTML report (tiles load in the reader's browser)."""
    import folium
    pv = pd.read_csv(D + "spoke_ad_prevalence_2019.csv")
    cen = json.load(open(D + "country_centroids.json"))
    m = folium.Map(location=[20, 10], zoom_start=2, tiles="OpenStreetMap")
    lo, hi = pv.mid.min(), pv.mid.max()
    import matplotlib.cm as cm, matplotlib.colors as mc
    norm = mc.Normalize(vmin=lo, vmax=hi); sm = cm.ScalarMappable(norm=norm, cmap="magma_r")
    n = 0
    for _, r in pv.iterrows():
        c = cen.get(r.iso)
        if not c: continue
        n += 1
        col = mc.to_hex(sm.to_rgba(r.mid))
        folium.CircleMarker(
            location=c, radius=4 + 7 * (r.mid - lo) / (hi - lo), color="#333", weight=0.6,
            fill=True, fill_color=col, fill_opacity=0.85,
            tooltip=f"{r.label}: {r.mid:.2f}%",
            popup=folium.Popup(
                f"<b>{r.label}</b> ({r.iso})<br>AD prevalence {r.mid:.3f}%"
                f"<br>reported interval {r.lower:.3f}–{r.upper:.3f}%"
                f"<br>year {int(r.year)}<br><i>source: spoke-okn PREVALENCE_DpL</i>", max_width=280),
        ).add_to(m)
    print("folium markers:", n)
    return m

# ---------------------------------------------------------------- Figure 9
def fig9():
    bh = pd.read_csv(D + "biohealth_ad_risk_protective.csv")
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.0), gridspec_kw=dict(wspace=0.45))
    ax = axes[0]
    SDOH = {"socb","inbe","bhvr","popg","orgf","edac","ocdi","famg","age","humn","idcn","qlco","mnob","resa","hcro","shro","prog","ocac","eehu","npop"}
    CLIN = {"dsyn","fndg","sosy","patf","neop","inpo","mobd","anab","comd","acab","cgab","emod","clna","lbtr"}
    MOL  = {"aapp","gngm","bacs","orch","lipd","carb","nnon","horm","enzy","imft","strd","elii","opco","phsu","topp","antb","vita","irda"}
    def grp(c):
        t = set(str(c).split("_"))
        if t & SDOH: return "social / behavioural"
        if t & MOL: return "molecular / chemical / drug"
        if t & CLIN: return "clinical condition / finding"
        return "other"
    bh["grp"] = bh.cat.map(grp)
    ct = pd.crosstab(bh.grp, bh.rel).reindex(columns=["predisposes_to_condition", "NEG_PREDISPOSES",
                                                      "preventative_for_condition", "NEG_PREVENTS"]).fillna(0)
    x = np.arange(len(ct)); w = 0.2
    cols = [UP, "#e8a89e", THEME[2], "#a8d8c5"]
    for i, c in enumerate(ct.columns):
        ax.bar(x + (i - 1.5) * w, ct[c], width=w, color=cols[i], edgecolor="white",
               label=c.replace("_", " ").replace("condition", "").strip())
    ax.set_xticks(x); ax.set_xticklabels([s.replace(" / ", "/\n") for s in ct.index], fontsize=8)
    ax.set_ylabel("distinct entities (PubMed-derived assertions)")
    panel_title(ax, "A", "Risk / protective assertions for AD (biohealth)")
    legend_outside(ax, where="below", ncol=2, title="assertion type")

    ax = axes[1]
    conf = [("risk AND protective", 219), ("predisposes AND\nnegated-predisposes", 115),
            ("prevents AND\nnegated-prevents", 26)]
    ax.barh([c[0] for c in conf][::-1], [c[1] for c in conf][::-1],
            color=[THEME[5], THEME[1], THEME[3]][::-1], edgecolor="white")
    for i, c in enumerate(conf[::-1]):
        ax.text(c[1] + 3, i, str(c[1]), va="center", fontsize=8.5)
    ax.set_xlabel("entities carrying mutually contradictory AD assertions")
    ax.set_xlim(0, 260)
    panel_title(ax, "B", "Literature-derived contradictions")
    finalize(fig, 9, F + "fig9_risk_conflict.png")

if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9):
        f(); print("ok", f.__name__)

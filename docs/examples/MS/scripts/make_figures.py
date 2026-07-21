#!/usr/bin/env python3
"""Figures 1-9 for the OKN federated-SPARQL Multiple Sclerosis study.

Usage:  python3 make_figures.py [--only 1 2 7 ...]

All figures follow the okn-report-style checklist: apply_style() first, legends OUTSIDE the axes,
Okabe-Ito categorical palette, red/blue diverging for signed values, font floors (tick >= 8 pt,
axis >= 9 pt, title >= 11 pt), no caption text baked into the PNG, saved through finalize() at
150 dpi. Long category labels are truncated to ~55 characters.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import re
import sys

sys.path.insert(0, "/sessions/vibrant-kind-heisenberg/mnt/.claude/skills/okn-report-style/scripts")
sys.path.insert(0, "/sessions/vibrant-kind-heisenberg/mnt/.claude/skills/okn-bioanalysis/scripts")

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from okn_figstyle import (  # noqa: E402
    DOWN,
    FONT,
    NEUTRAL,
    THEME,
    UP,
    apply_style,
    finalize,
    folium_map_iframe,
    folium_osm_map,
    legend_outside,
    osm_basemap,
    panel_title,
    ranked_barh,
    save_map_html,
    theme_legend,
)

WD = "/sessions/vibrant-kind-heisenberg/mnt/outputs/ms_work"
DATA = f"{WD}/data"
FIG = f"{WD}/study/figures"

apply_style()


def trunc(s, n=55):
    s = str(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# --------------------------------------------------------------------------------------
# Figure 1 — study design / federation inventory
# --------------------------------------------------------------------------------------
def fig1():
    # (A) logged-query-backed evidence rows contributed per knowledge graph
    rows = [
        ("biohealth", 12033, "SDoH + comorbidity edges"),
        ("prokn", 945 + 2321, "drug-indication + GO/Reactome"),
        ("digcfdekg", 1548, "PIGEAN gene-trait"),
        ("gene-expression-atlas-okn", 790 + 332, "DE + contrast enrichment"),
        ("nde", 853, "dataset records"),
        ("spoke-okn", 164 + 200 + 178, "disease-gene + prevalence + mortality"),
        ("biomarkerkg", 394, "biomarker assertions"),
        ("oard-kg", 211, "phenotype associations"),
        ("wikidata", 200, "country centroids"),
        ("ubergraph", 105, "identifier cross-references"),
        ("rdkg", 93, "subtype-resolved drug edges"),
        ("pankgraph", 0, "no MS disease node"),
        ("ncipidkg", 0, "demo subgraph, no MS"),
        ("evoweb", 0, "prokaryotic only"),
    ]
    rows.sort(key=lambda r: -r[1])
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    FLOOR = 0.7
    used = [v > 0 for v in vals]

    fig = plt.figure(figsize=(15.0, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.12], wspace=0.55)

    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(labels))
    plotted = [max(v, FLOOR * 1.45) for v in vals]
    cols = [THEME[0] if u else THEME[5] for u in used]
    ax.barh(y, [p - FLOOR for p in plotted], left=FLOOR, color=cols,
            hatch=["" if u else "///" for u in used], edgecolor="white", linewidth=0.4)
    ax.set_xscale("log")
    ax.set_xlim(FLOOR, 34000)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=FONT["tick"] + 1)
    ax.invert_yaxis()
    ax.set_xlabel("evidence rows returned by logged SPARQL queries (log scale)", fontsize=FONT["axis"])
    for i, (v, p) in enumerate(zip(vals, plotted, strict=False)):
        ax.text(p * 1.25, i, f"{v:,}" if v else "0", va="center",
                fontsize=FONT["annot"], color="#333")
    ax.grid(axis="x", ls=":", lw=0.6, color="#cccccc", zorder=0)
    ax.set_axisbelow(True)
    panel_title(ax, "A", "Evidence rows contributed per knowledge graph")
    legend_outside(
        ax,
        [mpatches.Patch(color=THEME[0]), mpatches.Patch(color=THEME[5], hatch="///")],
        ["used in the analysis", "queried, dropped (0 MS rows)"],
        where="below", ncol=2,
    )

    # (B) entity coverage per KG by payload type actually used
    bh = json.load(open(f"{DATA}/biohealth_ms.json"))
    pheno_bh = len({e["neighbour"] for e in bh["all_edges"]
                    if any(t in (e.get("neighbour_semtype") or "") for t in ("dsyn", "sosy", "patf"))})
    payload_order = ["gene", "variant", "drug", "biomarker", "phenotype",
                     "expression", "epidemiology", "SDoH", "ontology", "dataset metadata"]
    # Okabe-Ito, but give "epidemiology" the orange slot freed by the (empty) "variant" class —
    # the pale yellow #F0E442 has too little contrast on white for a thin bar.
    pcol_override = {"epidemiology": THEME[1]}
    cov = {
        "biohealth": {"phenotype": pheno_bh, "SDoH": 460},
        "prokn": {"gene": 88, "drug": 249, "ontology": 4},
        "digcfdekg": {"gene": 1581},
        "gene-expression-atlas-okn": {"expression": 777, "ontology": 4},
        "nde": {"dataset metadata": 853},
        "spoke-okn": {"gene": 164, "epidemiology": 200, "ontology": 1},
        "biomarkerkg": {"biomarker": 373, "gene": 257},
        "oard-kg": {"phenotype": 211},
        "wikidata": {"epidemiology": 200},
        "ubergraph": {"ontology": 105},
        "rdkg": {"drug": 78, "ontology": 4},
    }
    pcol = dict(zip(payload_order, THEME[:10], strict=False))
    pcol.update(pcol_override)

    axb = fig.add_subplot(gs[0, 1])
    kg_order = [k for k in labels if k in cov]
    ypos, ylab, bars = [], [], []
    cur = 0.0
    for kg in kg_order:
        items = [(p, cov[kg][p]) for p in payload_order if p in cov[kg]]
        for j, (p, v) in enumerate(items):
            bars.append((cur + j * 0.72, v, p))
        ylab.append((cur + (len(items) - 1) * 0.72 / 2, kg))
        cur += len(items) * 0.72 + 0.85
    for yy, v, p in bars:
        axb.barh(yy, v, height=0.64, color=pcol[p], edgecolor="white", linewidth=0.4)
        axb.text(v * 1.18, yy, f"{v:,}", va="center", fontsize=FONT["annot"], color="#333")
    axb.set_xscale("log")
    axb.set_xlim(0.7, 25000)
    ypos = [p[0] for p in ylab]
    axb.set_yticks(ypos)
    axb.set_yticklabels([p[1] for p in ylab], fontsize=FONT["tick"] + 1)
    axb.set_ylim(cur - 0.85, -0.6)
    axb.set_xlabel("distinct entities retrieved (log scale)", fontsize=FONT["axis"])
    axb.grid(axis="x", ls=":", lw=0.6, color="#cccccc")
    axb.set_axisbelow(True)
    panel_title(axb, "B", "Entity coverage per knowledge graph, by payload type")
    handles = [mpatches.Patch(color=pcol[p], label=p) for p in payload_order if p != "variant"]
    handles.insert(1, mpatches.Patch(facecolor="white", edgecolor="#999999", hatch="xxx",
                                     label="variant (none retrieved)"))
    legend_outside(axb, handles, [h.get_label() for h in handles], where="below", ncol=4)
    finalize(fig, 1, f"{FIG}/fig1_study_design.png")


# --------------------------------------------------------------------------------------
# Figure 2 — cross-KG consensus / evidence tiering
# --------------------------------------------------------------------------------------
TIER_COL = {"A": THEME[2], "B": THEME[1], "C": THEME[7]}


def fig2():
    g = pd.read_csv(f"{DATA}/gene_evidence_master.csv")
    fig = plt.figure(figsize=(14.6, 8.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.95, 1.15], wspace=0.42)

    ax = fig.add_subplot(gs[0, 0])
    counts = g.n_evidence_types.value_counts().sort_index()
    xs = list(range(1, 6))
    ys = [int(counts.get(i, 0)) for i in xs]
    tier_of = {1: "C", 2: "C", 3: "B", 4: "A", 5: "A"}
    ax.bar(xs, ys, color=[TIER_COL[tier_of[i]] for i in xs], width=0.68,
           edgecolor="white", linewidth=0.6)
    ax.set_yscale("log")
    ax.set_ylim(0.7, 9000)
    ax.set_xticks(xs)
    ax.set_xlabel("independent evidence types supporting the gene", fontsize=FONT["axis"])
    ax.set_ylabel("genes (log scale)", fontsize=FONT["axis"])
    for x, v in zip(xs, ys, strict=False):
        ax.text(x, v * 1.18, f"{v:,}", ha="center", fontsize=FONT["annot"], color="#333")
    bands = [("Tier C  ≤ 2 types", 0.5, 2.5, "C", 2265),
             ("Tier B  = 3 types", 2.5, 3.5, "B", 80),
             ("Tier A  ≥ 4 types", 3.5, 5.5, "A", 52)]
    for lab, x0, x1, t, n in bands:
        ax.axvspan(x0, x1, color=TIER_COL[t], alpha=0.10, zorder=0)
        ax.text((x0 + x1) / 2, 3800, f"{lab}\nn = {n:,}", ha="center", va="center",
                fontsize=FONT["annot"], color="#333", fontweight="bold")
    ax.set_xlim(0.5, 5.5)
    panel_title(ax, "A", "Genes by number of independent evidence types")
    legend_outside(ax, [mpatches.Patch(color=TIER_COL[t]) for t in "ABC"],
                   ["Tier A", "Tier B", "Tier C"], where="below", ncol=3, title="consensus tier")

    axb = fig.add_subplot(gs[0, 1])
    top = g.sort_values(["n_evidence_types", "n_sources", "pigean_score"],
                        ascending=False, na_position="last").head(30)
    ranked_barh(axb, list(top.gene), list(top.n_evidence_types),
                themes=list(top.tier), theme_colors=TIER_COL,
                annots=[f"{int(s)} KGs" for s in top.n_sources],
                xlabel="independent evidence types")
    axb.set_xlim(0, 6.6)
    axb.set_xticks([0, 1, 2, 3, 4, 5])
    panel_title(axb, "B", "Top 30 genes by cross-KG consensus")
    legend_outside(axb, [mpatches.Patch(color=TIER_COL[t]) for t in "ABC"],
                   ["Tier A (≥ 4 types)", "Tier B (3 types)", "Tier C (≤ 2 types)"],
                   where="below", ncol=3, title="consensus tier  ·  bar annotation = number of source KGs")
    finalize(fig, 2, f"{FIG}/fig2_consensus.png")


# --------------------------------------------------------------------------------------
# Figure 3 — GO enrichment (BP / MF / CC)
# --------------------------------------------------------------------------------------
def _enrich_panel(ax, d, letter, title, n, color):
    d = d[d.fdr < 0.05].copy()
    d["nlp"] = -np.log10(d.fdr)
    d = d.sort_values("nlp", ascending=False).head(n)
    ranked_barh(ax, [trunc(t) for t in d.term], list(d.nlp),
                annots=[f"{f:.1f}×  ({int(k)}/{int(K)})"
                        for f, k, K in zip(d.fold, d.k, d.K, strict=False)],
                xlabel="−log10(FDR)")
    for b in ax.patches:
        b.set_color(color)
    ax.axvline(-math.log10(0.05), color="#666666", ls="--", lw=0.9, zorder=0)
    panel_title(ax, letter, title)
    return len(d)


def fig3():
    bp = pd.read_csv(f"{DATA}/enrichment_go_bp.csv")
    mfcc = pd.read_csv(f"{DATA}/enrichment_go_mfcc.csv")
    fig = plt.figure(figsize=(16.4, 9.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1.0], height_ratios=[1, 1],
                          wspace=0.55, hspace=0.40)
    axa = fig.add_subplot(gs[:, 0])
    _enrich_panel(axa, bp, "A", "GO biological process — top 20 (FDR < 0.05)", 20, THEME[0])
    axb = fig.add_subplot(gs[0, 1])
    _enrich_panel(axb, mfcc[mfcc.aspect == "MF"], "B",
                  "GO molecular function — top 10", 10, THEME[2])
    axc = fig.add_subplot(gs[1, 1])
    _enrich_panel(axc, mfcc[mfcc.aspect == "CC"], "C",
                  "GO cellular component — top 10", 10, THEME[3])
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.075)
    fig.text(0.5, 0.018, "bar annotation: fold enrichment ×  (k / K)   ·   dashed line: FDR = 0.05",
             ha="center", va="bottom", fontsize=FONT["caption"] + 0.5, color="#555")
    finalize(fig, 3, f"{FIG}/fig3_go_enrichment.png", tight=False)


# --------------------------------------------------------------------------------------
# Figure 4 — Reactome enrichment by theme
# --------------------------------------------------------------------------------------
REACTOME_THEME = {
    "Interleukin-10 signaling": "interleukin signalling",
    "Interleukin-4 and Interleukin-13 signaling": "interleukin signalling",
    "Interferon gamma signaling": "interferon signalling",
    "Interleukin receptor SHC signaling": "interleukin signalling",
    "IFNG signaling activates MAPKs": "interferon signalling",
    "Interleukin-35 Signalling": "interleukin signalling",
    "MAPK1 (ERK2) activation": "MAPK/RAF cascade",
    "Interleukin-6 signaling": "interleukin signalling",
    "RAF/MAP kinase cascade": "MAPK/RAF cascade",
    "Interleukin-20 family signaling": "interleukin signalling",
    "Signaling by CSF3 (G-CSF)": "other",
    "Interleukin-7 signaling": "interleukin signalling",
    "Interleukin-12 signaling": "interleukin signalling",
    "Interleukin-23 signaling": "interleukin signalling",
    "Interferon alpha/beta signaling": "interferon signalling",
    "Phosphorylation of CD3 and TCR zeta chains": "TCR / immune synapse",
    "RUNX1 and FOXP3 control the development of regulatory T lymphocytes (Tregs)":
        "Treg / transcription",
    "Interleukin-27 signaling": "interleukin signalling",
    "Interleukin-21 signaling": "interleukin signalling",
    "Regulation of IFNG signaling": "interferon signalling",
}
THEME_COL = {
    "interleukin signalling": THEME[0],
    "interferon signalling": THEME[1],
    "MAPK/RAF cascade": THEME[2],
    "TCR / immune synapse": THEME[3],
    "Treg / transcription": THEME[5],
    "other": THEME[7],
}


def fig4():
    r = pd.read_csv(f"{DATA}/enrichment_reactome.csv")
    r = r[r.fdr < 0.05].copy()
    r["nlp"] = -np.log10(r.fdr)
    r = r.sort_values("nlp", ascending=False).head(20)
    themes = [REACTOME_THEME.get(p, "other") for p in r.pathway]
    fig, ax = plt.subplots(figsize=(11.2, 7.6))
    ranked_barh(ax, [trunc(p) for p in r.pathway], list(r.nlp),
                themes=themes, theme_colors=THEME_COL,
                annots=[f"{f:.1f}×  ({int(k)}/{int(K)})"
                        for f, k, K in zip(r.fold, r.k, r.K, strict=False)],
                xlabel="−log10(FDR)")
    ax.axvline(-math.log10(0.05), color="#666666", ls="--", lw=0.9, zorder=0)
    panel_title(ax, "", "Reactome pathways enriched in the MS gene set — top 20 (FDR < 0.05)")
    used = {t: THEME_COL[t] for t in THEME_COL if t in set(themes)}
    handles = [mpatches.Patch(color=c, label=lab) for lab, c in used.items()]
    legend_outside(ax, handles, [h.get_label() for h in handles], where="below", ncol=3,
                   title="pathway theme (manually assigned)   ·   "
                         "bar annotation: fold enrichment ×  (k / K)   ·   dashed line: FDR = 0.05")
    finalize(fig, 4, f"{FIG}/fig4_reactome.png")


# --------------------------------------------------------------------------------------
# GXA contrast metadata (shared by figures 5 and 6)
# --------------------------------------------------------------------------------------
COMPARTMENT = {
    "CD4": "CD4+ T cells", "CD8": "CD8+ T cells", "B-Cells": "B cells",
    "monocytes": "monocytes", "neutrophils": "neutrophils", "whole blood": "whole blood",
}
COMP_ORDER = ["CD4+ T cells", "CD8+ T cells", "B cells", "monocytes", "neutrophils",
              "whole blood", "peripheral blood", "cerebrospinal fluid", "cerebral cortex"]


def contrast_meta():
    """Short label, compartment (UBERON/CL-backed) and subtype for each MS contrast."""
    g = json.load(open(f"{DATA}/gxa_ms_filtered.json"))
    meta = {}
    for a in g["assays"]:
        name = a["name"]
        m = re.search(r"in '([^']+)'$", name)
        comp = COMPARTMENT.get(m.group(1)) if m else None
        if "cerebrospinal fluid" in name:
            comp = "cerebrospinal fluid"
        elif "peripheral blood" in name:
            comp = "peripheral blood"
        if comp is None:
            if a["study"] == "E-GEOD-32645":
                comp = "cerebral cortex"          # UBERON_0000956
            elif a["study"] == "E-GEOD-77598":
                comp = "monocytes"                # CL_0000576
            elif a["study"] == "E-GEOD-66573":
                comp = "whole blood"              # UBERON_0000178
            else:
                comp = "whole blood"              # E-MTAB-2973, UBERON_0000178
        sub = ("SPMS" if "secondary progressive" in name
               else "RRMS" if "relapsing-remitting" in name else "MS")
        short = name
        short = short.replace("'multiple sclerosis; before IFN-beta treatment' vs 'normal'",
                              "MS pre-IFNβ vs normal")
        short = short.replace("'multiple sclerosis; after IFN-beta treatment' vs 'normal'",
                              "MS post-IFNβ vs normal")
        short = short.replace("'secondary progressive multiple sclerosis' vs 'normal'",
                              "SPMS vs normal")
        short = short.replace("'relapsing-remitting multiple sclerosis' vs 'normal'",
                              "RRMS vs normal")
        short = short.replace("'multiple sclerosis; cerebrospinal fluid' vs "
                              "'neurological disease, non-inflammatory; cerebrospinal fluid'",
                              "MS vs non-inflammatory neuro. disease")
        short = short.replace("'multiple sclerosis; peripheral blood' vs "
                              "'neurological disease, non-inflammatory; peripheral blood'",
                              "MS vs non-inflammatory neuro. disease")
        short = short.replace("'multiple sclerosis' vs 'normal' in 'no physical activity program'",
                              "MS vs normal (no exercise programme)")
        short = short.replace("'physical activity program' vs 'no physical activitiy program' "
                              "in 'multiple sclerosis'", "exercise vs no exercise (within MS)")
        short = short.replace("'multiple sclerosis' vs 'normal'", "MS vs normal")
        short = re.sub(r" in '[^']+'$", "", short)
        meta[a["assay"]] = {"study": a["study"], "name": name, "short": short,
                            "comp": comp, "sub": sub, "tech": a["tech"]}
    return g, meta


# --------------------------------------------------------------------------------------
# Figure 5 — differential expression context
# --------------------------------------------------------------------------------------
def fig5():
    g, meta = contrast_meta()
    up = collections.Counter()
    dn = collections.Counter()
    for r in g["genes"]:
        (up if r["dir"] == "up" else dn)[r["assay"]] += 1
    nenr = collections.Counter(r["assay"] for r in g["enrichment"])
    order = sorted(meta, key=lambda a: (COMP_ORDER.index(meta[a]["comp"]), meta[a]["short"]))

    fig = plt.figure(figsize=(13.8, 12.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.05, 1.0], hspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(order))
    u = np.array([up[a] for a in order], float)
    d = np.array([dn[a] for a in order], float)
    ax.barh(y, u, color=UP, height=0.66)
    ax.barh(y, -d, color=DOWN, height=0.66)
    lim = max(u.max(), d.max()) * 1.20
    ax.set_xlim(-lim, lim * 1.62)
    for i, (uu, dd) in enumerate(zip(u, d, strict=False)):
        if uu:
            ax.text(uu + lim * 0.02, i, f"{int(uu)}", va="center", fontsize=FONT["annot"], color=UP)
        if dd:
            ax.text(-dd - lim * 0.02, i, f"{int(dd)}", va="center", ha="right",
                    fontsize=FONT["annot"], color=DOWN)
        if not uu and not dd:
            ax.text(lim * 0.02, i, "no DE genes retrieved", va="center",
                    fontsize=FONT["annot"], color="#999999", style="italic")
    # alternating compartment bands + subtype / enrichment tag columns
    xs = lim * 1.16
    xe = lim * 1.42
    ax.axvline(lim * 1.05, color="#dddddd", lw=0.8)
    blocks, prev, start = [], None, 0
    for i, a in enumerate(order):
        c = meta[a]["comp"]
        if c != prev:
            if prev is not None:
                blocks.append((start, i - 1, prev))
            prev, start = c, i
    blocks.append((start, len(order) - 1, prev))
    for k, (i0, i1, _c) in enumerate(blocks):
        if k % 2 == 0:
            ax.axhspan(i0 - 0.5, i1 + 0.5, color="#000000", alpha=0.035, zorder=0)
    for i, a in enumerate(order):
        ax.text(xs, i, meta[a]["sub"], va="center", ha="center", fontsize=FONT["annot"],
                color="#333", fontweight="bold")
        ax.text(xe, i, str(nenr.get(a, 0)), va="center", ha="center", fontsize=FONT["annot"],
                color="#333")
    ax.text(xs, -1.05, "subtype", va="center", ha="center", fontsize=FONT["annot"],
            color="#555", fontweight="bold")
    ax.text(xe, -1.05, "enriched\nterms", va="center", ha="center", fontsize=FONT["annot"],
            color="#555", fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([trunc(f"{meta[a]['short']} — {meta[a]['comp']}") for a in order],
                       fontsize=FONT["tick"] + 0.5)
    ax.invert_yaxis()
    ax.set_ylim(len(order) - 0.4, -1.9)
    tk = np.arange(-300, 301, 100)
    ax.set_xticks(tk)
    ax.set_xticklabels([str(abs(int(t))) for t in tk])
    ax.set_xlabel("differentially expressed genes per contrast", fontsize=FONT["axis"])
    ax.axvline(0, color="#888888", lw=0.8)
    panel_title(ax, "A", "MS-specific contrasts in gene-expression-atlas-okn (n = 19)")
    # the far left of the axes is empty for the eight top rows, so an inside corner is safe here
    legend_outside(ax, [mpatches.Patch(color=DOWN), mpatches.Patch(color=UP)],
                   ["down-regulated in MS", "up-regulated in MS"], where="upper left")

    # (B) genes recurring in >= 2 MS contrasts
    cnt = collections.Counter(r["sym"] for r in g["genes"])
    multi = sorted([s for s, n in cnt.items() if n >= 2])
    sub = [r for r in g["genes"] if r["sym"] in multi]
    cassays = sorted({r["assay"] for r in sub},
                     key=lambda a: (COMP_ORDER.index(meta[a]["comp"]), meta[a]["short"]))
    axb = fig.add_subplot(gs[1, 0])
    for r in sub:
        xi, yi = multi.index(r["sym"]), cassays.index(r["assay"])
        axb.scatter(xi, yi, s=170, marker="o" if r["dir"] == "up" else "s",
                    color=UP if r["dir"] == "up" else DOWN, edgecolor="white", linewidth=0.8,
                    zorder=3)
    axb.set_xticks(range(len(multi)))
    axb.set_xticklabels(multi, rotation=55, ha="right", fontsize=FONT["tick"] + 1)
    axb.set_yticks(range(len(cassays)))
    axb.set_yticklabels([trunc(f"{meta[a]['short']} — {meta[a]['comp']}", 55) for a in cassays],
                        fontsize=FONT["tick"] + 0.5)
    axb.set_xlim(-0.7, len(multi) - 0.3)
    axb.set_ylim(len(cassays) - 0.5, -0.5)
    axb.grid(True, ls=":", lw=0.6, color="#dddddd", zorder=0)
    axb.set_axisbelow(True)
    axb.set_xlabel("gene (recurrent in ≥ 2 MS contrasts)", fontsize=FONT["axis"])
    panel_title(axb, "B", "Recurrent DE genes across MS contrasts")
    legend_outside(axb,
                   [Line2D([0], [0], marker="o", color="w", markerfacecolor=UP, markersize=10),
                    Line2D([0], [0], marker="s", color="w", markerfacecolor=DOWN, markersize=10)],
                   ["up-regulated", "down-regulated"], where="right")
    finalize(fig, 5, f"{FIG}/fig5_expression_context.png")


# --------------------------------------------------------------------------------------
# Figure 6 — recurrent enrichment themes across MS contrasts
# --------------------------------------------------------------------------------------
def gxa_theme(term):
    t = term.lower()
    if re.search(r"translat|ribosom|peptide chain elongation|nonsense mediated decay|"
                 r"selenocysteine|40s|43s|eif2ak4|srp-dependent|ternary complex", t):
        return "translation / ribosome"
    if re.search(r"type ii interferon|interferon-gamma|interferon gamma|ifng", t):
        return "type II interferon (IFN-γ)"
    if re.search(r"antiviral|virus|viral|isg15|oas |ifn-stimulated|interferon-stimulated", t):
        return "antiviral / ISG effector"
    if re.search(r"type i interferon|interferon alpha|interferon-alpha|interferon-beta|"
                 r"interferon beta|ifn-alpha|alpha/beta|irf|rig-i|mda5|ddx58|ifih1", t):
        return "type I interferon (IFN-α/β)"
    return "other"


GXA_THEME_COL = {
    "type I interferon (IFN-α/β)": THEME[0],
    "type II interferon (IFN-γ)": THEME[1],
    "antiviral / ISG effector": THEME[2],
    "translation / ribosome": THEME[5],
    "other": THEME[7],
}


def _gxa_panel(ax, enrich, src, letter, title, n=20):
    d = collections.defaultdict(set)
    for r in enrich:
        if r["src"] == src:
            d[r["termName"]].add(r["assayName"])
    top = sorted(d.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:n]
    labels = [trunc(t) for t, _ in top]
    vals = [len(s) for _, s in top]
    themes = [gxa_theme(t) for t, _ in top]
    ranked_barh(ax, labels, vals, themes=themes, theme_colors=GXA_THEME_COL,
                annots=[f"{v} / 19" for v in vals], xlabel="MS contrasts with the term enriched")
    ax.set_xlim(0, max(vals) * 1.30)
    ax.set_xticks(range(0, max(vals) + 1, 2))
    panel_title(ax, letter, title)
    return themes


def fig6():
    g = json.load(open(f"{DATA}/gxa_ms_filtered.json"))
    e = g["enrichment"]
    fig = plt.figure(figsize=(15.6, 8.6))
    gs = fig.add_gridspec(1, 2, wspace=0.62)
    axa = fig.add_subplot(gs[0, 0])
    t1 = _gxa_panel(axa, e, "GXA:GO", "A", "GO terms recurrently enriched in MS contrasts")
    axb = fig.add_subplot(gs[0, 1])
    t2 = _gxa_panel(axb, e, "GXA:Reactome", "B", "Reactome pathways recurrently enriched")
    used = {k: v for k, v in GXA_THEME_COL.items() if k in set(t1) | set(t2)}
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.115)
    fig.legend([mpatches.Patch(color=c) for c in used.values()], list(used),
               loc="lower center", ncol=len(used), frameon=False, fontsize=FONT["legend"],
               title="theme (manually assigned)   ·   bar annotation: contrasts enriched / 19 MS contrasts")
    finalize(fig, 6, f"{FIG}/fig6_gxa_enrichment_themes.png", tight=False)


# --------------------------------------------------------------------------------------
# Figure 7 — epidemiology / latitude gradient
# --------------------------------------------------------------------------------------
BANDS = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 90)]


def band_label(a):
    for lo, hi in BANDS:
        if lo <= a < hi:
            return "60+" if lo == 60 else f"{lo}–{hi}"
    return "60+"


def fig7():
    from scipy import stats as sst
    d = pd.read_csv(f"{DATA}/ms_prevalence_latitude.csv")
    rho, pv = sst.spearmanr(d.abslat, d.per100k)
    print(f"[fig7] recomputed Spearman rho={rho:.3f} p={pv:.3g} n={len(d)}")

    fig = plt.figure(figsize=(16.2, 10.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.35, 1.0], width_ratios=[1, 1],
                          hspace=0.30, wspace=0.26)

    # (A) OSM-tiled basemap; falls back to Natural Earth polygons when the tile server is
    # unreachable (this build environment's proxy blocks every tile host).
    axa = fig.add_subplot(gs[0, :])
    vals = np.log10(d.per100k.values)
    sizes = 14 + 120 * (d.per100k.values / d.per100k.max()) ** 0.6
    before = list(fig.axes)
    basemap = "OpenStreetMap tiles"
    try:
        osm_basemap(axa, lons=d.lon.values, lats=d.lat.values, values=vals,
                    size=sizes, cmap="YlGnBu", edgecolor="#333333", linewidth=0.35,
                    colorbar_label="MS prevalence per 100 000 (log scale)")
    except Exception as exc:                                  # noqa: BLE001
        print(f"[fig7] OSM tiles unavailable ({type(exc).__name__}); "
              f"falling back to Natural Earth polygons in EPSG:3857")
        basemap = "Natural Earth 1:110m (public domain)"
        for extra in [a for a in fig.axes if a not in before]:
            extra.remove()
        axa.clear()
        import geopandas as gpd
        world = gpd.read_file(f"{DATA}/basemap/naturalearth_lowres.shp").to_crs(epsg=3857)
        world.plot(ax=axa, color="#eef1f3", edgecolor="#b7c0c7", linewidth=0.45, zorder=0)
        pts = gpd.GeoDataFrame({"v": vals},
                               geometry=gpd.points_from_xy(d.lon, d.lat),
                               crs="EPSG:4326").to_crs(epsg=3857)
        pts.plot(ax=axa, column="v", cmap="YlGnBu", markersize=sizes, edgecolor="#333333",
                 linewidth=0.35, legend=True, zorder=3,
                 legend_kwds={"label": "MS prevalence per 100 000 (log scale)", "shrink": 0.72})
        axa.set_ylim(-7.4e6, 1.42e7)   # ~ 55°S – 72°N: covers every country centroid in the data
        axa.set_axis_off()
    cax = [a for a in fig.axes if a not in before and a is not axa]
    if cax:
        cb = cax[-1]
        ticks = [1, 3, 10, 30, 100, 200]
        cb.set_yticks(np.log10(ticks))
        cb.set_yticklabels([str(t) for t in ticks], fontsize=FONT["tick"])
        cb.yaxis.label.set_size(FONT["axis"])
    axa.text(0.995, 0.012, f"basemap: {basemap}", transform=axa.transAxes, ha="right",
             va="bottom", fontsize=FONT["caption"], color="#555")
    panel_title(axa, "A", "MS prevalence by country centroid (Web Mercator, EPSG:3857)")

    # (B) |latitude| vs prevalence
    axb = fig.add_subplot(gs[1, 0])
    for lab, mask, col, mk in [("Northern hemisphere", d.lat >= 0, THEME[0], "o"),
                               ("Southern hemisphere", d.lat < 0, THEME[1], "^")]:
        s = d[mask]
        axb.scatter(s.abslat, s.per100k, s=26, color=col, marker=mk, alpha=0.85,
                    edgecolor="white", linewidth=0.4, label=f"{lab} (n = {len(s)})")
    xs = np.linspace(0, d.abslat.max(), 60)
    b, a = np.polyfit(d.abslat, np.log10(d.per100k), 1)
    axb.plot(xs, 10 ** (a + b * xs), color="#222222", lw=1.8, ls="--", zorder=5)
    axb.set_yscale("log")
    axb.set_xlabel("absolute latitude of country centroid (°)", fontsize=FONT["axis"])
    axb.set_ylabel("MS prevalence per 100 000 (log scale)", fontsize=FONT["axis"])
    axb.text(0.03, 0.97, "Spearman ρ = 0.836\np = 2.1 × 10⁻⁵³\nn = 200 countries",
             transform=axb.transAxes, va="top", ha="left", fontsize=FONT["annot"],
             bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": "#bbbbbb", "lw": 0.7})
    axb.grid(ls=":", lw=0.6, color="#dddddd")
    axb.set_axisbelow(True)
    panel_title(axb, "B", "Latitude gradient")
    legend_outside(axb, where="below", ncol=2)

    # (C) prevalence by |latitude| band
    axc = fig.add_subplot(gs[1, 1])
    d["band"] = d.abslat.map(band_label)
    labs = ["0–10", "10–20", "20–30", "30–40", "40–50", "50–60", "60+"]
    groups = [d[d.band == b].per100k.values for b in labs]
    bp = axc.boxplot(groups, labels=labs, patch_artist=True, widths=0.62,
                     medianprops={"color": "#222222", "lw": 1.4},
                     flierprops={"marker": ".", "markersize": 4, "markerfacecolor": "#888888",
                                 "markeredgecolor": "none"})
    cmap = plt.get_cmap("YlGnBu")
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(cmap(0.22 + 0.68 * i / (len(labs) - 1)))
        patch.set_edgecolor("#555555")
    axc.set_yscale("log")
    axc.set_ylim(0.8, 700)
    for i, gvals in enumerate(groups, start=1):
        axc.text(i, 430, f"n = {len(gvals)}", ha="center", fontsize=FONT["annot"], color="#333")
    axc.set_xlabel("absolute latitude band (°)", fontsize=FONT["axis"])
    axc.set_ylabel("MS prevalence per 100 000 (log scale)", fontsize=FONT["axis"])
    axc.grid(axis="y", ls=":", lw=0.6, color="#dddddd")
    axc.set_axisbelow(True)
    panel_title(axc, "C", "Prevalence by latitude band")
    finalize(fig, 7, f"{FIG}/fig7_epidemiology.png")

    # interactive OSM map + inline-embeddable fragment
    rows = []
    for _, r in d.iterrows():
        rows.append({
            "country": r.country, "ISO3": r.iso3,
            "prevalence per 100k": f"{r.per100k:,.1f}",
            "95% uncertainty interval": f"{r.lo:,.1f} – {r.hi:,.1f}",
            "GBD year": int(r.year),
            "source": "spoke-okn PREVALENCE_DpL (IHME GBD 2019); coordinates wikidata P625",
            "lat": float(r.lat), "lon": float(r.lon), "_size": float(r.per100k),
        })
    m = folium_osm_map(
        rows, popup_keys=["country", "ISO3", "prevalence per 100k",
                          "95% uncertainty interval", "GBD year", "source"],
        tooltip_key="country", value_key="_size", radius=3, zoom_start=2)
    save_map_html(m, f"{FIG}/map_ms_prevalence.html")
    with open(f"{FIG}/map_ms_prevalence_iframe.html", "w") as fh:
        fh.write(folium_map_iframe(m, height=560,
                                  title="MS prevalence per 100 000 by country (OpenStreetMap)"))
    print(f"[fig7] wrote {FIG}/map_ms_prevalence_iframe.html")


# --------------------------------------------------------------------------------------
# Figure 8 — therapeutics
# --------------------------------------------------------------------------------------
NORMALISE = [
    (r"ocrelizumab", "Ocrelizumab"),
    (r"rituximab", "Rituximab"),
    (r"^tysabri$|natalizumab", "Natalizumab"),
    (r"^bg00012$|dimethyl fumarate", "Dimethyl fumarate"),
    (r"diroximel fumarate", "Diroximel fumarate"),
    (r"copaxone|glatiramer|bioactivated gra", "Glatiramer acetate"),
    (r"alemtuzumab", "Alemtuzumab"),
    (r"fingolimod", "Fingolimod"),
    (r"biib041|fampridine|dalfampridine", "Dalfampridine (fampridine)"),
    (r"clemastine", "Clemastine"),
    (r"imu-838", "IMU-838 (vidofludimus)"),
    (r"peginterferon beta-1a|biib017", "Peginterferon beta-1a"),
    # note: one CTDRUG label uses a Greek beta ("Interferon Β-1a"), which lower-cases to "β"
    (r"rebif|interferon beta-1a|interferon β-1a|interferon beta type 1a|beta-interferon",
     "Interferon beta-1a"),
    (r"interferon beta-1b", "Interferon beta-1b"),
    (r"peg-liposomal prednisolone", "Prednisolone (PEG-liposomal)"),
    (r"extended-release quetiapine fumarate", "Quetiapine fumarate"),
]
SUBTYPES = [("MONDO_0005301", "MS"), ("MONDO_0005314", "RRMS"),
            ("MONDO_0000452", "PRMS"), ("MONDO_0018784", "pediatric MS")]
KEY_TARGETS = ["S1PR1", "S1PR5", "MS4A1", "DHODH", "KEAP1", "BTK", "TOP2A", "NR3C1"]


def normalise_drug(lab):
    low = str(lab).lower().strip()
    for pat, out in NORMALISE:
        if re.search(pat, low):
            return out
    return str(lab).strip().strip("®").capitalize() if low.isupper() else str(lab).strip()


def fig8():
    r = pd.read_csv(f"{DATA}/rdkg_ms_drugs.csv")
    r["norm"] = [normalise_drug(x) for x in r.drugLabel]
    cell = collections.defaultdict(set)
    for _, x in r.iterrows():
        cell[(x.norm, x.mondo)].add(x.rel)
    drugs = sorted({n for n, _ in cell}, key=lambda s: s.lower())
    print(f"[fig8] {len(r)} rdkg rows -> {r.drugLabel.nunique()} raw labels -> {len(drugs)} normalised drugs")

    fig = plt.figure(figsize=(15.4, 13.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.52)
    ax = fig.add_subplot(gs[0, 0])
    for i, dn in enumerate(drugs):
        for j, (mid, _lab) in enumerate(SUBTYPES):
            rel = cell.get((dn, mid))
            if not rel:
                continue
            if "treats" in rel:
                ax.scatter(j, i, s=115, marker="s", color=THEME[0], edgecolor="white",
                           linewidth=0.7, zorder=3)
            if "contraindicated_for" in rel:
                ax.scatter(j, i, s=145, marker="X", color=THEME[5], edgecolor="white",
                           linewidth=0.7, zorder=4)
    ax.set_xticks(range(len(SUBTYPES)))
    ax.set_xticklabels([s[1] for s in SUBTYPES], fontsize=FONT["tick"] + 2)
    ax.set_yticks(range(len(drugs)))
    ax.set_yticklabels([trunc(x, 46) for x in drugs], fontsize=FONT["tick"])
    ax.set_xlim(-0.6, len(SUBTYPES) - 0.4)
    ax.set_ylim(len(drugs) - 0.4, -0.6)
    ax.grid(True, ls=":", lw=0.55, color="#dddddd", zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlabel("MONDO multiple-sclerosis subtype in rdkg", fontsize=FONT["axis"])
    panel_title(ax, "A", "rdkg drug → MS subtype assertions")
    legend_outside(ax,
                   [Line2D([0], [0], marker="s", color="w", markerfacecolor=THEME[0], markersize=10),
                    Line2D([0], [0], marker="X", color="w", markerfacecolor=THEME[5], markersize=11)],
                   ["biolink:treats", "biolink:contraindicated_for"], where="below", ncol=2)

    # (B) top molecular targets among prokn MS-indicated drugs
    dt = pd.read_csv(f"{DATA}/ms_drugs_targets.csv")
    cnt = collections.Counter()
    for t in dt.targets.dropna():
        for s in str(t).split("|"):
            s = s.strip()
            if s and not s.upper().startswith("CHEMBL"):
                cnt[s] += 1
    ranked = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0] not in KEY_TARGETS, kv[0]))[:20]
    pk = {x["symbol"]: x["n_drugs"] for x in
          json.load(open(f"{DATA}/prokn_target_drugs.json"))["per_symbol_drug_counts"]}
    axb = fig.add_subplot(gs[0, 1])
    labs = [s for s, _ in ranked]
    vals = [v for _, v in ranked]
    cols = [THEME[3] if s in KEY_TARGETS else NEUTRAL for s in labs]
    yy = np.arange(len(labs))
    axb.barh(yy, vals, color=cols, height=0.68)
    axb.set_yticks(yy)
    axb.set_yticklabels([f"{s} ★" if s in KEY_TARGETS else s for s in labs],
                        fontsize=FONT["tick"] + 2)
    for t, s in zip(axb.get_yticklabels(), labs, strict=False):
        if s in KEY_TARGETS:
            t.set_fontweight("bold")
    axb.invert_yaxis()
    axb.set_xlim(0, max(vals) * 1.45)
    axb.set_xlabel("MS-indicated drugs acting on the target (prokn)", fontsize=FONT["axis"])
    for i, (s, v) in enumerate(ranked):
        extra = f"   · {pk[s]:,} drugs in prokn" if s in pk else ""
        axb.text(v + max(vals) * 0.02, i, f"{v}{extra}", va="center",
                 fontsize=FONT["caption"], color="#333")
    axb.grid(axis="x", ls=":", lw=0.6, color="#dddddd")
    axb.set_axisbelow(True)
    panel_title(axb, "B", "Top 20 molecular targets of MS-indicated drugs")
    legend_outside(axb,
                   [mpatches.Patch(color=THEME[3]), mpatches.Patch(color=NEUTRAL)],
                   ["★ established MS drug target", "other target"],
                   where="below", ncol=2)
    finalize(fig, 8, f"{FIG}/fig8_therapeutics.png")


# --------------------------------------------------------------------------------------
# Figure 9 — mechanistic map
# --------------------------------------------------------------------------------------
# Modules are ordered so that the two largest fans (13 and 10 genes) are never adjacent on the
# ring — otherwise the outermost gene labels of neighbouring modules collide.
MODULES = {
    "T-cell co-stimulation /\nactivation": ["CD28", "CD86", "CD80", "CD58", "CD6", "CD40",
                                            "CD226", "PTPRC", "MALT1", "CARD11", "TAGAP",
                                            "SKAP2", "TXK"],
    "Vitamin D metabolism": ["CYP27B1", "CYP24A1", "MTHFR"],
    "JAK-STAT /\ncytokine receptor": ["IL2RA", "IL7R", "JAK1", "TYK2", "STAT3", "STAT4",
                                      "SOCS1", "IL6", "IFNGR2", "CSF2RB"],
    "Antigen presentation\n(MHC)": ["HLA-DRB1", "HLA-DQA1", "HLA-A", "HLA-F", "NLRC5",
                                    "BTNL2", "IFI30"],
    "Innate /\nmicroglial-myeloid": ["TLR4", "AIF1", "ITGAM", "CCL2", "IL1B", "NCF4",
                                     "TNF", "MERTK"],
    "Myelin / neuroaxonal": ["MBP", "MOG", "GFAP", "NEFL", "GALC", "PLEKHG5", "BDNF"],
    "T-helper differentiation /\nTreg": ["FOXP3", "RUNX3", "BATF", "GATA3", "IKZF3", "LEF1",
                                         "IL17A", "IL10", "IL12A", "TGFB1"],
    "B-cell / humoral": ["MS4A1", "CXCR5", "FCRL1", "BACH2", "SP140"],
}
DRUGS = {
    "JAK-STAT /\ncytokine receptor": ["Interferon β-1a / β-1b†\n→ IFNAR"],
    "Antigen presentation\n(MHC)": ["Glatiramer acetate†\n→ HLA-DR"],
    "T-cell co-stimulation /\nactivation": ["Alemtuzumab†\n→ CD52", "Natalizumab†\n→ ITGA4",
                                            "Teriflunomide†\n→ DHODH*", "Cladribine†"],
    "T-helper differentiation /\nTreg": ["Methylprednisolone‡\n→ NR3C1",
                                         "Mitoxantrone†\n→ TOP2A"],
    "B-cell / humoral": ["Anti-CD20 mAbs† → MS4A1\n(ocrelizumab, ofatumumab, ublituximab)",
                         "BTK inhibitors§ → BTK\n"
                         "(tolebrutinib, fenebrutinib, remibrutinib, evobrutinib)"],
    "Innate /\nmicroglial-myeloid": ["Dimethyl fumarate† → KEAP1 / NFE2L2*"],
    "Myelin / neuroaxonal": ["S1P modulators† → S1PR1 / S1PR5\n"
                             "(fingolimod, siponimod, ozanimod, ponesimod)",
                             "Dalfampridine‡ → KCNA* / KCNB*"],
}


def fig9():
    import mechanistic_map as mm
    from mechanistic_map import render_mechanistic_map

    # The renderer's default 15.5 x 11 in canvas puts the 8-pt gene labels of a 13-member fan on
    # top of each other. Node positions are in data units and text is in points, so enlarging the
    # canvas (only) shrinks every label relative to the layout and clears the collisions.
    _subplots = mm.plt.subplots
    mm.plt.subplots = lambda *a, **k: _subplots(*a, **{**k, "figsize": (21.5, 15.2)})
    master = set(pd.read_csv(f"{DATA}/gene_evidence_master.csv").gene)
    mods, dropped = {}, []
    for m, genes in MODULES.items():
        keep = [g for g in genes if g in master]
        dropped += [(m, g) for g in genes if g not in master]
        mods[m] = keep
    print(f"[fig9] module genes kept={sum(len(v) for v in mods.values())} dropped={dropped}")
    out = render_mechanistic_map(
        anchor="Multiple\nsclerosis",
        modules=mods,
        drugs=DRUGS,
        out_path=f"{FIG}/fig9_mechanistic_map.png",
        title="Multiple sclerosis — gene / pathway / drug mechanistic map",
        subtitle="modules = analyst synthesis of the significant GO-BP and Reactome themes "
                 "(FDR < 0.05); every gene is present in the retrieved cross-KG evidence set",
        gene_legend="Gene (spoke-okn / digcfdekg / prokn / GXA / biomarkerkg)",
        module_legend="Mechanistic module (synthesis over enrichment)",
        drug_legend="Drug  † approved DMT  ‡ symptomatic / acute  § investigational",
        footnote="Drug→module edges are assigned via the named molecular target "
                 "(prokn drug–target, rdkg treats). * target not in the MS evidence set.",
        dpi=150,
    )
    mm.plt.subplots = _subplots
    print("[fig9] wrote", out)


FIGS = {1: fig1, 2: fig2, 3: fig3, 4: fig4, 5: fig5, 6: fig6, 7: fig7, 8: fig8, 9: fig9}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", type=int, default=sorted(FIGS))
    a = ap.parse_args()
    for n in a.only:
        FIGS[n]()

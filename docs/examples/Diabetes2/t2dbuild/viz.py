#!/usr/bin/env python3
"""Figures for the Type 2 Diabetes Proto-OKN evidence map (matches Alzheimers style)."""

import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

OUT = str(Path(__file__).resolve().parent)
FIG = f"{OUT}/figures"
Path(FIG).mkdir(parents=True, exist_ok=True)
BLUE, GREEN, ORANGE, PURPLE, RED, GREY = (
    "#2E86AB",
    "#3B8C4D",
    "#F18F01",
    "#A23B72",
    "#C0392B",
    "#95a5a6",
)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
S = json.loads(Path(f"{OUT}/t2d_stats.json").read_text())
PREV = json.loads(Path(f"{OUT}/map_state_prevalence.json").read_text())

# ---------------- fig1: cross-source corroboration
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
d = S["gene_by_nsources"]
ks = sorted(d, key=int)
vals = [d[k] for k in ks]
cols = [GREY, BLUE, ORANGE, RED][: len(ks)]
b = ax[0].bar(ks, vals, color=cols, edgecolor="#333")
for r, v in zip(b, vals, strict=False):
    ax[0].text(
        r.get_x() + r.get_width() / 2,
        v + max(vals) * 0.01,
        str(v),
        ha="center",
        va="bottom",
        fontsize=10,
    )
ax[0].set_title("T2D genes by number of corroborating sources", fontweight="bold")
ax[0].set_xlabel("# independent sources reporting the gene")
ax[0].set_ylabel("number of genes")
n3 = len(S["tier1_genes"]) + len(S["tier2_genes"])
ax[0].text(
    0.97,
    0.95,
    f"{n3} genes ≥3 sources (high-confidence core)\n{len(S['tier1_genes'])} genes in all 4 sources",
    transform=ax[0].transAxes,
    ha="right",
    va="top",
    fontsize=9.5,
    style="italic",
    bbox={"boxstyle": "round", "fc": "#FFF6E6", "ec": ORANGE},
)
sg = S["source_gene_totals"]
order = sorted(sg, key=lambda k: sg[k])
names = {
    "spoke_okn": "spoke-okn",
    "digcfdekg": "digcfdekg",
    "rdkg": "rdkg",
    "prokn": "prokn",
}
cmap = {"spoke_okn": BLUE, "digcfdekg": GREEN, "rdkg": PURPLE, "prokn": ORANGE}
b2 = ax[1].barh(
    [names[k] for k in order],
    [sg[k] for k in order],
    color=[cmap[k] for k in order],
    edgecolor="#333",
)
for r, k in zip(b2, order, strict=False):
    ax[1].text(
        sg[k] + 5, r.get_y() + r.get_height() / 2, str(sg[k]), va="center", fontsize=10
    )
ax[1].set_title("Diabetes-associated genes per source", fontweight="bold")
ax[1].set_xlabel("number of genes")
ax[1].text(
    0.97,
    0.05,
    "spoke-okn/rdkg/prokn: curated\ndigcfdekg: statistical (GWAS/PIGEAN)\nspoke-okn = parent term (diabetes mellitus)",
    transform=ax[1].transAxes,
    ha="right",
    va="bottom",
    fontsize=8.5,
    style="italic",
)
plt.tight_layout()
plt.savefig(f"{FIG}/fig1_cross_source_corroboration.png", dpi=140, bbox_inches="tight")
plt.close()

# ---------------- fig2: evidence + entity breakdown
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
ev = S["evidence_counts"]
lab = {
    "curated_link": "curated link",
    "statistical_association": "statistical /\ngenetic",
    "measured_activity_change": "measured\nactivity",
    "pathway_membership": "pathway\nmembership",
    "epidemiological": "epidemiological\n(geo)",
}
ek = sorted(ev, key=lambda k: -ev[k])
ecol = {
    "curated_link": BLUE,
    "statistical_association": GREEN,
    "measured_activity_change": ORANGE,
    "pathway_membership": PURPLE,
    "epidemiological": RED,
}
b = ax[0].bar(
    [lab[k] for k in ek],
    [ev[k] for k in ek],
    color=[ecol[k] for k in ek],
    edgecolor="#333",
)
for r, k in zip(b, ek, strict=False):
    ax[0].text(
        r.get_x() + r.get_width() / 2, ev[k] + 8, str(ev[k]), ha="center", fontsize=10
    )
ax[0].set_title("Findings by evidence type (kept separate)", fontweight="bold")
ax[0].set_ylabel("findings")
et = S["entity_counts"]
elab = {
    "gene": "genes",
    "drug": "drugs",
    "environmental_factor": "environmental",
    "altered_activity_gene": "altered-activity\ngenes",
    "pathway_or_geneset": "pathways/\ngene sets",
    "genetic_variant": "variants\n(islet eQTL)",
    "prevalence_geolocation": "prevalence\ngeolocations",
    "sdoh_correlation": "SDoH\ncorrelations",
    "clinical_feature": "clinical",
    "altered_activity_program": "activity\nprograms",
    "biomarker": "biomarker",
}
ek2 = [k for k in sorted(et, key=lambda k: -et[k]) if k in elab]
b = ax[1].barh(
    [elab[k] for k in ek2][::-1],
    [et[k] for k in ek2][::-1],
    color=BLUE,
    edgecolor="#333",
)
for r, k in zip(b, ek2[::-1], strict=False):
    ax[1].text(
        et[k] + 3, r.get_y() + r.get_height() / 2, str(et[k]), va="center", fontsize=9
    )
ax[1].set_title("Findings by entity type", fontweight="bold")
ax[1].set_xlabel("findings")
plt.tight_layout()
plt.savefig(f"{FIG}/fig2_evidence_entity_breakdown.png", dpi=140, bbox_inches="tight")
plt.close()

# ---------------- fig3: gene-pathway-drug mechanistic network
modules = {
    "β-cell K_ATP / insulin secretion": [
        "ABCC8",
        "KCNJ11",
        "GCK",
        "SLC30A8",
        "G6PC2",
        "ADCY5",
        "KCNQ1",
        "SLC2A2",
        "INS",
        "IAPP",
    ],
    "MODY / islet transcription factors": [
        "HNF1A",
        "HNF4A",
        "HNF1B",
        "PDX1",
        "NEUROD1",
        "PAX4",
        "WFS1",
        "RFX6",
        "MAFA",
        "NKX6-1",
    ],
    "Insulin signaling / resistance": [
        "IRS1",
        "IRS2",
        "INSR",
        "PIK3R1",
        "AKT2",
        "PTEN",
        "ENPP1",
        "SLC2A4",
        "PPARG",
        "TBC1D4",
    ],
    "Incretin / GPCR axis": ["GLP1R", "GIPR", "GCGR", "GCG", "DPP4", "FFAR1"],
    "Obesity / adipo-lipid": [
        "FTO",
        "MC4R",
        "LEP",
        "LEPR",
        "ADIPOQ",
        "PPARGC1A",
        "LPL",
        "CEBPA",
    ],
}
drugs = {
    "β-cell K_ATP / insulin secretion": ["Glimepiride", "Repaglinide"],
    "Insulin signaling / resistance": ["Metformin", "Pioglitazone"],
    "Incretin / GPCR axis": ["Sitagliptin", "Semaglutide*", "Empagliflozin"],
    "Obesity / adipo-lipid": ["Orforglipron"],
    "MODY / islet transcription factors": ["Sulfonylurea"],
}
G = nx.Graph()
pos = {}
_m = math

cen = (0, 0)
G.add_node("Type 2 diabetes", kind="disease")
pos["Type 2 diabetes"] = cen
ang = [90, 162, 234, 306, 18]
for i, (mod, genes) in enumerate(modules.items()):
    a = _m.radians(ang[i])
    mx, my = 2.6 * _m.cos(a), 2.6 * _m.sin(a)
    G.add_node(mod, kind="module")
    pos[mod] = (mx, my)
    G.add_edge("Type 2 diabetes", mod)
    for j, g in enumerate(genes):
        gx = mx + 1.35 * _m.cos(a + (j - len(genes) / 2) * 0.22)
        gy = my + 1.35 * _m.sin(a + (j - len(genes) / 2) * 0.22)
        G.add_node(g, kind="gene")
        pos[g] = (gx, gy)
        G.add_edge(mod, g)
    for j, dn in enumerate(drugs.get(mod, [])):
        dx = mx + 2.5 * _m.cos(a + (j - 0.5) * 0.3)
        dy = my + 2.5 * _m.sin(a + (j - 0.5) * 0.3)
        G.add_node(dn, kind="drug")
        pos[dn] = (dx, dy)
        G.add_edge(mod, dn)
fig, ax = plt.subplots(figsize=(15.5, 11))
ax.axis("off")
nx.draw_networkx_edges(G, pos, edge_color="#ccc", width=1.1, ax=ax)


def draw(kind, shape, color, size):
    """Draw all graph nodes of the given kind with a shared shape and style."""
    nl = [n for n, d in G.nodes(data=True) if d["kind"] == kind]
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=nl,
        node_shape=shape,
        node_color=color,
        node_size=size,
        edgecolors="#222",
        linewidths=1,
        ax=ax,
    )


draw("gene", "o", BLUE, 900)
draw("module", "s", GREEN, 2600)
draw("drug", "^", ORANGE, 900)
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=["Type 2 diabetes"],
    node_shape="*",
    node_color=RED,
    node_size=2600,
    edgecolors="#222",
    ax=ax,
)
for n, (x, y) in pos.items():
    d = G.nodes[n]["kind"]
    fs = 8 if d == "gene" else (9 if d == "drug" else 10)
    fw = "bold" if d in ("module", "disease") else "normal"
    ax.text(x, y, n, ha="center", va="center", fontsize=fs, fontweight=fw, zorder=5)
ax.set_title(
    "T2D gene–pathway–drug mechanistic map (entities retrieved from Proto-OKN sources)",
    fontsize=14,
    fontweight="bold",
)
leg = [
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor=BLUE,
        markersize=13,
        label="Gene (spoke/rdkg/digcfdekg/prokn)",
    ),
    Line2D(
        [0],
        [0],
        marker="s",
        color="w",
        markerfacecolor=GREEN,
        markersize=13,
        label="Pathway / mechanistic module",
    ),
    Line2D(
        [0],
        [0],
        marker="^",
        color="w",
        markerfacecolor=ORANGE,
        markersize=13,
        label="Drug (prokn indication)",
    ),
    Line2D(
        [0],
        [0],
        marker="*",
        color="w",
        markerfacecolor=RED,
        markersize=17,
        label="Disease",
    ),
]
ax.legend(handles=leg, loc="lower left", fontsize=10, frameon=True)
ax.text(
    0.99,
    0.01,
    "*GLP-1 class shown for context",
    transform=ax.transAxes,
    ha="right",
    fontsize=8,
    style="italic",
)
plt.tight_layout()
plt.savefig(f"{FIG}/fig3_gene_pathway_drug_network.png", dpi=135, bbox_inches="tight")
plt.close()

# ---------------- fig4: top gene x source matrix
with Path(f"{OUT}/T2D_gene_source_matrix.csv").open() as _f:
    rows = list(csv.reader(_f))[1:]
top = [r for r in rows if int(r[6]) >= 3][:34]
srcs = ["spoke-okn", "rdkg", "prokn", "digcfdekg"]
fig, ax = plt.subplots(figsize=(8.6, 12))
for i, r in enumerate(top):
    for j, val in enumerate(r[2:6]):
        ax.add_patch(
            plt.Rectangle(
                (j, i),
                0.92,
                0.92,
                facecolor=(BLUE if val == "1" else "#eef3f7"),
                edgecolor="#fff",
            )
        )
    w = r[7]
    if w != "":
        ax.text(
            4.15, i + 0.46, f"w={float(w):.1f}", va="center", fontsize=8, color="#555"
        )
ax.set_xlim(0, 5.2)
ax.set_ylim(len(top), 0)
ax.set_xticks([j + 0.46 for j in range(4)])
ax.set_xticklabels(srcs, rotation=30, ha="right", fontsize=9)
ax.set_yticks([i + 0.46 for i in range(len(top))])
ax.set_yticklabels([r[0] for r in top], fontsize=8.5)
ax.set_title(
    "Top T2D genes × source (≥3 sources)\nblue = reported; w = digcfdekg weight",
    fontweight="bold",
    fontsize=11,
)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
plt.tight_layout()
plt.savefig(f"{FIG}/fig4_top_gene_matrix.png", dpi=140, bbox_inches="tight")
plt.close()

# ---------------- fig5: SDoH correlations
sd = S["sdoh_correlations"]
sd = sorted(sd, key=lambda x: x[1])
labels = [v for v, r, n in sd]
rs = [r for v, r, n in sd]
cols = [
    "#95a5a6" if v == "excessive drinking" else (RED if r > 0 else BLUE)
    for v, r, n in sd
]
fig, ax = plt.subplots(figsize=(11, 8))
b = ax.barh(labels, rs, color=cols, edgecolor="#333")
for r, val in zip(b, rs, strict=False):
    ax.text(
        val + (0.02 if val >= 0 else -0.02),
        r.get_y() + r.get_height() / 2,
        f"{val:+.2f}",
        va="center",
        ha="left" if val >= 0 else "right",
        fontsize=9,
    )
ax.axvline(0, color="#333", lw=1)
ax.set_xlim(-1, 1.05)
ax.set_title(
    "County-level SDoH correlates of diabetes prevalence (Pearson r, n≈"
    + str(sd[0][2])
    + " counties)\nspoke-okn × County Health Rankings",
    fontweight="bold",
    fontsize=12,
)
ax.set_xlabel(
    "Pearson r  (red = higher SDoH burden → higher diabetes; blue = protective; "
    "grey = confounded, see note)"
)
plt.tight_layout()
plt.savefig(f"{FIG}/fig5_sdoh_correlations.png", dpi=140, bbox_inches="tight")
plt.close()

# ---------------- fig6: ranked state prevalence bar (the 'diabetes belt') — NO lat/long axes.
#   The geographic view is the interactive OpenStreetMap layer (report HTML + T2D_prevalence_map.html).
pv = sorted(PREV, key=lambda p: p["prev"])
names = [p["name"] for p in pv]
vals = [p["prev"] for p in pv]
norm = mcolors.Normalize(vmin=7, vmax=14.5)
cmap = cm.get_cmap("YlOrRd")
fig, ax = plt.subplots(figsize=(10.5, 12))
b = ax.barh(
    names, vals, color=[cmap(norm(v)) for v in vals], edgecolor="#333", linewidth=0.5
)
for r, v in zip(b, vals, strict=False):
    ax.text(
        v + 0.06, r.get_y() + r.get_height() / 2, f"{v:.1f}", va="center", fontsize=8
    )
ax.set_xlim(0, 15.6)
ax.set_xlabel("Age-adjusted diabetes prevalence (%)")
ax.set_title(
    "Diabetes prevalence by U.S. state (CDC PLACES via spoke-okn) — the 'diabetes belt'\n(interactive OpenStreetMap version in the HTML report)",
    fontweight="bold",
    fontsize=12,
)
sm = cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cb = plt.colorbar(sm, ax=ax, shrink=0.5, pad=0.01)
cb.set_label("prevalence (%)")
ax.margins(y=0.005)
plt.tight_layout()
plt.savefig(f"{FIG}/fig6_prevalence_by_state.png", dpi=140, bbox_inches="tight")
plt.close()
_stale_map = Path(f"{FIG}/fig6_prevalence_map.png")
if _stale_map.exists():
    _stale_map.unlink()

print("figures written to", FIG)
for f in sorted(p.name for p in Path(FIG).iterdir()):
    print("  ", f)

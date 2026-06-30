"""Rendered diagrams that replace the ASCII art in README §5 and §8.

  figures/fig0_crossgraph_strategy.png  -> the cross-graph join architecture (§5)
  figures/fig_go_bridge.png             -> the 4-graph spoke-genelab→wikidata→prokn GO path (§8)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

GENELAB = ("#dbe7f6", "#14397d")   # spoke-genelab (blue)
OKN     = ("#f7dcd8", "#c0392b")   # spoke-okn (red)
DIG     = ("#fdebd0", "#cf8420")   # digcfdekg (orange)
PROKN   = ("#d3efe8", "#138d75")   # prokn (teal)
KEY     = ("#fdf3c4", "#b7950b")   # shared join key (gold)
WIKI    = ("#e6e6ea", "#5d6d7e")   # wikidata (grey)


def box(ax, cx, cy, w, h, title, lines, palette, title_fs=10.5, line_fs=8.6):
    fc, ec = palette
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.10",
                 linewidth=1.8, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(cx, cy + h / 2 - 0.30, title, ha="center", va="center",
            fontsize=title_fs, fontweight="bold", color=ec, zorder=3)
    for i, ln in enumerate(lines):
        ax.text(cx, cy + h / 2 - 0.62 - i * 0.34, ln, ha="center", va="center",
                fontsize=line_fs, color="#1f2933", zorder=3)


def arrow(ax, p1, p2, label="", color="#34495e", rad=0.0, fs=8.0, dy=0.12, lblcolor=None):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=16,
                 lw=1.7, color=color, connectionstyle=f"arc3,rad={rad}", zorder=1))
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my + dy, label, ha="center", va="bottom",
                fontsize=fs, color=lblcolor or color, style="italic", zorder=4)


# =====================================================================================
# fig0 — cross-graph strategy / architecture  (replaces §5 ASCII)
# =====================================================================================
fig, ax = plt.subplots(figsize=(13, 6.6))
ax.set_xlim(0, 13); ax.set_ylim(0, 6.6); ax.axis("off")

box(ax, 2.7, 3.75, 4.6, 3.0, "spoke-genelab",
    ["NASA OSDR spaceflight omics", "",
     "Mission → Study → Assay",
     "Assay –DIFFERENTIAL_EXPRESSION→",
     "mouse Gene  (log2fc, adj_p)",
     "mouse Gene –IS_ORTHOLOG→ human Gene"],
    GENELAB)

box(ax, 6.5, 3.75, 2.3, 1.5, "human ortholog",
    ["Entrez / NCBI", "Gene IRI", "(shared key)"], KEY, title_fs=9.5, line_fs=8.2)

box(ax, 10.4, 5.35, 4.6, 1.55, "spoke-okn  (SPOKE)",
    ["Disease  (ASSOCIATES_DaG)", "Compound (UP/DOWNREGULATES)",
     "direct Entrez · 16,326 genes"], OKN, line_fs=8.3)
box(ax, 10.4, 3.55, 4.6, 1.4, "digcfdekg  (CFDE REVEAL)",
    ["Trait / gene-set (geneToTrait)", "direct Entrez · 19,747 genes"], DIG, line_fs=8.3)
box(ax, 10.4, 1.75, 4.6, 1.55, "prokn  (Protein KN)",
    ["GO biological process", "Protein-level annotation",
     "via wikidata Entrez→HGNC bridge"], PROKN, line_fs=8.3)

arrow(ax, (5.0, 3.75), (5.35, 3.75))                       # genelab -> key
arrow(ax, (7.65, 3.95), (8.1, 5.2), label="", rad=-0.15)   # key -> spoke-okn
arrow(ax, (7.65, 3.75), (8.1, 3.55))                       # key -> digcfdekg
arrow(ax, (7.65, 3.55), (8.1, 1.95), rad=0.15)             # key -> prokn

ax.text(6.5, 0.42,
        "OSD / GLDS study & mission axis = NASA-internal island (no cross-KG join) — "
        "federation happens at the gene level, via the human ortholog.",
        ha="center", va="center", fontsize=8.6, style="italic", color="#555")
ax.set_title("Cross-graph query strategy: spaceflight genes joined to terrestrial biology on the shared Entrez key",
             fontsize=11.5, fontweight="bold", color="#14397d")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig0_crossgraph_strategy.png"), dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================================
# fig_go_bridge — 4-graph GO path  (replaces §8 ASCII)
# =====================================================================================
fig, ax = plt.subplots(figsize=(13.5, 3.5))
ax.set_xlim(0, 13.5); ax.set_ylim(0, 3.5); ax.axis("off")

cy = 1.7; w = 2.05; h = 1.05
xs = [1.25, 3.75, 6.25, 8.75, 11.95]
box(ax, xs[0], cy, w, h, "spoke-genelab", ["DE gene (sig.)", "human ortholog"], GENELAB, 9.5, 8.2)
box(ax, xs[1], cy, w, h, "wikidata", ["Entrez (P351)", "→ HGNC (P354)"], WIKI, 9.5, 8.2)
box(ax, xs[2], cy, w, h, "prokn", ["uniprot:Gene", "(HGNC exactMatch)"], PROKN, 9.5, 8.2)
box(ax, xs[3], cy, w, h, "prokn", ["Protein", "(UniProt)"], PROKN, 9.5, 8.2)
box(ax, xs[4], cy, 2.45, h, "prokn", ["GO biological", "process"], PROKN, 9.5, 8.2)

arrow(ax, (xs[0] + w / 2, cy), (xs[1] - w / 2, cy), "Entrez ortholog", fs=7.6)
arrow(ax, (xs[1] + w / 2, cy), (xs[2] - w / 2, cy), "skos:exactMatch", fs=7.6)
arrow(ax, (xs[2] + w / 2, cy), (xs[3] - w / 2, cy), "SIO_010078\n(encodes)", fs=7.6, dy=0.10)
arrow(ax, (xs[3] + w / 2, cy), (xs[4] - 2.45 / 2, cy), "RO_0002331\n(involved in)", fs=7.6, dy=0.10)

ax.set_title("§8 GO bridge: reaching prokn Gene-Ontology biological processes from a spaceflight gene (four graphs)",
             fontsize=10.5, fontweight="bold", color="#138d75")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_go_bridge.png"), dpi=150, bbox_inches="tight")
plt.close()

print("wrote figures/fig0_crossgraph_strategy.png and figures/fig_go_bridge.png")

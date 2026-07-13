"""Generate figure 5 for the spoke-genelab cross-graph kidney case study."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 140,
        "font.family": "DejaVu Sans",
    }
)
OUT = "/sessions/dreamy-intelligent-euler/mnt/outputs/"

# term, source, n genes, member list
rows = [
    ("cholesterol biosynthetic process", "GO biological process — pankgraph", 8),
    ("GOBP sterol biosynthetic process", "curated gene set — digcfdekg", 8),
    ("isoprenoid biosynthetic process", "GO biological process — pankgraph", 6),
    ("HALLMARK cholesterol homeostasis", "curated gene set — digcfdekg", 6),
    ("KEGG mevalonate pathway", "curated gene set — digcfdekg", 5),
    ("sterol biosynthetic process", "GO biological process — pankgraph", 4),
]
rows = sorted(rows, key=lambda r: r[2])
col = {
    "GO biological process — pankgraph": "#2471a3",
    "curated gene set — digcfdekg": "#16a085",
}
fig, ax = plt.subplots(figsize=(8.6, 4.8))
y = range(len(rows))
ax.barh(
    list(y),
    [r[2] for r in rows],
    color=[col[r[1]] for r in rows],
    edgecolor="k",
    lw=0.3,
)
ax.set_yticks(list(y))
ax.set_yticklabels([r[0] for r in rows])
for i, r in enumerate(rows):
    ax.text(r[2] + 0.08, i, str(r[2]), va="center", fontsize=10)
ax.set_xlabel("number of C57BL/6J cholesterol-pathway DEGs annotated to the term")
ax.set_xlim(0, 9)
ax.set_title(
    "Pathway / GO recovery by cross-graph annotation\nKidney spaceflight DEGs → human orthologs → GO terms (pankgraph) & pathway gene sets (digcfdekg)",
    fontsize=10.5,
)
ax.legend(
    handles=[Patch(facecolor=c, edgecolor="k", label=lbl) for lbl, c in col.items()],
    fontsize=9,
    loc="lower right",
)
fig.tight_layout()
fig.savefig(OUT + "fig5_pathway_go.png")
plt.close(fig)
print("wrote fig5")

"""Generate schematic diagrams for the spoke-genelab cross-graph kidney case study."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 160})
OUT = "/sessions/dreamy-intelligent-euler/mnt/outputs/"

ENT, ENT_E = "#dbe9f6", "#2471a3"  # entity (blue)
KEY, KEY_E = "#d4efdb", "#1e8449"  # join key (green)
GL, GL_E = "#eaf3fb", "#5a8fbf"  # spoke-genelab panel
OKN, OKN_E = "#fdf2e3", "#d68910"  # companion KGs (amber)
EDGE = "#56606a"


def box(
    ax,
    x,
    y,
    w,
    h,
    text,
    fc=ENT,
    ec=ENT_E,
    fs=10,
    bold=False,
    tcol="#10212e",
    lw=1.6,
    align="center",
):
    """Draw a rounded rectangle box with centered text on the axes."""
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.015,rounding_size=0.12",
            fc=fc,
            ec=ec,
            lw=lw,
            zorder=2,
        )
    )
    ax.text(
        x,
        y,
        text,
        ha=align,
        va="center",
        fontsize=fs,
        color=tcol,
        fontweight="bold" if bold else "normal",
        zorder=3,
        linespacing=1.25,
    )


def arrow(
    ax,
    p1,
    p2,
    label="",
    fs=8,
    color=EDGE,
    lw=1.8,
    loff=(0, 0.2),
    italic=True,
    style="-|>",
):
    """Draw an annotated arrow between two points on the axes."""
    ax.annotate(
        "",
        xy=p2,
        xytext=p1,
        zorder=1,
        arrowprops={
            "arrowstyle": style,
            "color": color,
            "lw": lw,
            "shrinkA": 3,
            "shrinkB": 3,
            "connectionstyle": "arc3,rad=0",
        },
    )
    if label:
        ax.text(
            (p1[0] + p2[0]) / 2 + loff[0],
            (p1[1] + p2[1]) / 2 + loff[1],
            label,
            ha="center",
            va="center",
            fontsize=fs,
            color="#3a4750",
            style="italic" if italic else "normal",
            zorder=4,
        )


# ============================================================ FIGURE 1: schema
fig, ax = plt.subplots(figsize=(13.6, 4.7))
ax.set_xlim(0, 13.6)
ax.set_ylim(0, 4.7)
ax.axis("off")
ax.text(
    0.2,
    4.45,
    "spoke-genelab schema (entities and the edges used in this study)",
    fontsize=12.5,
    fontweight="bold",
    color="#10212e",
)

yr = 2.95
box(ax, 1.65, yr, 2.5, 1.0, "Study\n(OSD-102 / OSD-163)", fs=10)
box(
    ax,
    5.05,
    yr,
    2.7,
    1.0,
    "Assay\n(left kidney, RNA-Seq,\nSpace Flight vs Ground)",
    fs=9,
)
box(ax, 8.75, yr, 2.1, 1.0, "Gene\n(mouse, Entrez)", fs=9.5)
box(ax, 11.95, yr, 2.3, 1.0, "Gene\n(human ortholog,\nEntrez)", fs=9, fc=KEY, ec=KEY_E)
box(ax, 5.05, 1.0, 2.7, 0.82, "Anatomy\n(UBERON: kidney)", fs=9)

arrow(ax, (2.90, yr), (3.70, yr), "PERFORMED_SpAS", fs=8, loff=(0, 0.66))
arrow(
    ax,
    (6.40, yr),
    (7.70, yr),
    "MEASURED_DIFFERENTIAL_\nEXPRESSION_ASmMG",
    fs=7.6,
    loff=(0, 0.72),
)
arrow(ax, (9.80, yr), (10.80, yr), "IS_ORTHOLOG_\nMGiG", fs=7.6, loff=(0, 0.72))
arrow(
    ax,
    (5.05, 2.45),
    (5.05, 1.41),
    "INVESTIGATED_ASiA",
    fs=7.6,
    loff=(1.2, 0),
    italic=True,
)
ax.text(
    11.95,
    2.30,
    "→ joins spoke-okn / digcfdekg / pankgraph",
    ha="center",
    va="top",
    fontsize=7.6,
    color=KEY_E,
    style="italic",
)
ax.text(
    6.8,
    0.30,
    "edge properties on the differential-expression edge:   "
    "log2fc · adj_p_value · group_mean_1/2 · group_stdev_1/2",
    ha="center",
    va="center",
    fontsize=8.4,
    color="#7a8893",
)
fig.tight_layout()
fig.savefig(OUT + "fig_schema.png", bbox_inches="tight")
plt.close(fig)

# ============================================================ FIGURE 2: cross-graph strategy
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.2)
ax.axis("off")

# left panel (spoke-genelab)
ax.add_patch(
    FancyBboxPatch(
        (0.25, 1.5),
        4.5,
        4.2,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        fc=GL,
        ec=GL_E,
        lw=1.8,
        zorder=0,
    )
)
ax.text(0.45, 5.45, "spoke-genelab", fontsize=12, fontweight="bold", color=GL_E)
box(
    ax, 2.5, 4.75, 3.5, 0.8, "OSD-102 / OSD-163\n(kidney, Space Flight vs Ground)", fs=9
)
box(ax, 2.5, 3.35, 3.0, 0.85, "mouse Gene\n(log2fc, adj_p_value)", fs=9)
box(
    ax,
    2.5,
    2.05,
    3.0,
    0.85,
    "human Gene\n(Entrez)",
    fs=9.5,
    fc=KEY,
    ec=KEY_E,
    bold=True,
)
arrow(
    ax,
    (2.5, 4.32),
    (2.5, 3.8),
    "MEASURED_DIFFERENTIAL_EXPRESSION",
    fs=7.0,
    loff=(0, 0.0),
    style="-|>",
)
arrow(ax, (2.5, 2.9), (2.5, 2.5), "IS_ORTHOLOG_MGiG", fs=7.2, loff=(1.35, 0))

# join key (dashed vertical)
ax.plot([5.55, 5.55], [1.7, 5.3], ls=(0, (6, 4)), color="#1e8449", lw=2.0, zorder=1)
ax.text(
    5.55,
    5.55,
    "join on shared\nEntrez / Ensembl gene id",
    ha="center",
    va="bottom",
    fontsize=8.2,
    color="#1e8449",
    fontweight="bold",
)

# right panels (companion KGs)
box(
    ax,
    9.05,
    4.78,
    5.0,
    1.0,
    "spoke-okn\nASSOCIATES_DaG  →  Disease\nUP / DOWNREGULATES  ←  Compound",
    fs=8.6,
    fc=OKN,
    ec=OKN_E,
    align="center",
)
box(
    ax,
    9.05,
    3.30,
    5.0,
    1.0,
    "digcfdekg\ngeneToTrait  →  Trait / phenotype\ngeneInGeneSet  →  Pathway gene set",
    fs=8.6,
    fc=OKN,
    ec=OKN_E,
)
box(
    ax,
    9.05,
    1.95,
    5.0,
    0.9,
    "pankgraph\nfunctional_association  →  GO term\n(labels via ubergraph)",
    fs=8.6,
    fc=OKN,
    ec=OKN_E,
)

# fan of join arrows from human Gene to the three KGs
for ty in (4.78, 3.30, 1.95):
    arrow(ax, (4.0, 2.05), (6.55, ty), "", color="#1e8449", lw=1.6)

# bottom step strip
for x, t, c in [
    (2.5, "Step 1 — reproduce differential\nexpression in spoke-genelab", GL_E),
    (5.55, "Step 2 — map mouse DEG to\nhuman ortholog (Entrez)", "#1e8449"),
    (9.05, "Step 3 — add disease / pathway /\nGO / trait context", OKN_E),
]:
    ax.text(
        x,
        0.75,
        t,
        ha="center",
        va="center",
        fontsize=8.4,
        color=c,
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": c, "lw": 1.2},
    )
ax.annotate(
    "",
    xy=(4.6, 0.75),
    xytext=(4.0, 0.75),
    arrowprops={"arrowstyle": "-|>", "color": "#9aa6b0", "lw": 1.5},
)
ax.annotate(
    "",
    xy=(7.4, 0.75),
    xytext=(6.7, 0.75),
    arrowprops={"arrowstyle": "-|>", "color": "#9aa6b0", "lw": 1.5},
)

fig.tight_layout()
fig.savefig(OUT + "fig_strategy.png", bbox_inches="tight")
plt.close(fig)
print("wrote fig_schema.png and fig_strategy.png")

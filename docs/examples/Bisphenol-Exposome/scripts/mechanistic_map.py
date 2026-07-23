"""
mechanistic_map.py — render an anchor→module→gene→drug **mechanistic map**: a radial network that
places the entities you actually retrieved (genes, pathway/mechanistic modules, drugs) around a
central disease/anchor, so a reader sees the mechanism at a glance. Generalises the hand-built T2D
fig8 (docs/examples/Diabetes). Use it for a "map the biology of X" synthesis (see
references/mechanistic-map.md); it is a SYNTHESIS view, not a query result.

    from mechanistic_map import render_mechanistic_map
    render_mechanistic_map(
        anchor="Type 2 diabetes",
        modules={                       # module label -> member entities (genes/proteins)
            "β-cell K_ATP / insulin secretion": ["ABCC8", "KCNJ11", "GCK", "SLC30A8", ...],
            "MODY / islet transcription factors": ["HNF1A", "HNF4A", "PDX1", ...],
            ...
        },
        drugs={                         # module label -> drugs that ACT ON that module (optional)
            "β-cell K_ATP / insulin secretion": ["Glimepiride", "Repaglinide"],
            ...
        },
        out_path="figures/fig3_mechanistic_map.png",
        title="T2D gene–pathway–drug mechanistic map (entities retrieved from Proto-OKN sources)",
    )

Design (honesty is the point — see the reference):
- Every node is an entity you RETRIEVED. The modules are the analyst's grouping of the tiered gene
  core (step 12) into mechanistic themes — usually the enrichment result (step 6); genes are placed
  by curated pathway membership. State that grouping basis in the legend/caption; do not invent
  members to fill a module.
- Shapes carry the entity kind (star=anchor, square=module, circle=gene, triangle=drug) so the map
  survives greyscale / colour-vision deficiency — colour is redundant, never the sole cue.
- Label the drug evidence layer in the caption (approved > investigational > probe > tox
  perturbation); only draw a drug that a KG edge actually ties to a gene in that module.

Any entity kind works, not just genes: swap `gene_legend`/`drug_legend` for proteins, chemicals,
phenotypes, etc. `subtitle`/`footnote` add context lines. CLI: `python mechanistic_map.py --demo`
renders the T2D example to /tmp; `python mechanistic_map.py spec.json out.png` renders from a JSON
spec ({"anchor":..., "modules":{...}, "drugs":{...}, "title":..., ...}).
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

# Okabe–Ito, colour-vision-deficiency-safe. Shape is the primary cue; colour is redundant.
GENE = "#0072B2"  # blue circle
MODULE = "#009E73"  # bluish-green square
DRUG = "#E69F00"  # orange triangle
ANCHOR = "#D55E00"  # vermillion star
EDGE = "#cccccc"


def render_mechanistic_map(
    anchor,
    modules,
    drugs=None,
    out_path="fig_mechanistic_map.png",
    title="Mechanistic map",
    subtitle=None,
    footnote=None,
    anchor_kind="Disease",
    gene_legend="Gene",
    module_legend="Pathway / mechanistic module",
    drug_legend="Drug",
    dpi=135,
):
    """Render a radial anchor→module→gene→drug map to a PNG. Returns the output path.

    - anchor: central label (disease / gene / chemical the map is anchored on).
    - modules: dict {module label -> list of member entity labels} (order preserved; fanned outward).
    - drugs: optional dict {module label -> list of drug labels acting on that module}.
    Angles are distributed evenly, so any number of modules lays out cleanly.
    """
    drugs = drugs or {}
    modules = {m: list(members) for m, members in modules.items()}
    n_mod = len(modules)
    if n_mod == 0:
        raise ValueError("need at least one module")

    G = nx.Graph()
    pos = {}
    G.add_node(anchor, kind="anchor")
    pos[anchor] = (0.0, 0.0)

    r_mod = 2.6  # module ring radius
    r_gene = 1.5  # gene fan radius (from its module)
    r_drug = 2.6  # drug radius (from its module, beyond the genes)
    for i, (mod, members) in enumerate(modules.items()):
        a = math.radians(90 - i * 360.0 / n_mod)  # start at top, go clockwise
        mx, my = r_mod * math.cos(a), r_mod * math.sin(a)
        G.add_node(mod, kind="module")
        pos[mod] = (mx, my)
        G.add_edge(anchor, mod)

        # fan the genes in an arc centred on the outward radial direction; tighten spacing as the
        # module gets crowded so labels stay legible.
        step = min(0.30, 2.4 / max(len(members), 1))
        for j, g in enumerate(members):
            ga = a + (j - (len(members) - 1) / 2) * step
            G.add_node(g, kind="gene")
            pos[g] = (mx + r_gene * math.cos(ga), my + r_gene * math.sin(ga))
            G.add_edge(mod, g)

        mod_drugs = drugs.get(mod, [])
        dstep = min(0.32, 1.6 / max(len(mod_drugs), 1))
        for j, dn in enumerate(mod_drugs):
            da = a + (j - (len(mod_drugs) - 1) / 2) * dstep
            G.add_node(dn, kind="drug")
            pos[dn] = (mx + r_drug * math.cos(da), my + r_drug * math.sin(da))
            G.add_edge(mod, dn)

    _fig, ax = plt.subplots(figsize=(15.5, 11))
    ax.axis("off")
    nx.draw_networkx_edges(G, pos, edge_color=EDGE, width=1.1, ax=ax)

    def _draw(kind, shape, color, size):
        nl = [n for n, d in G.nodes(data=True) if d["kind"] == kind]
        if nl:
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

    _draw("gene", "o", GENE, 900)
    _draw("module", "s", MODULE, 2600)
    _draw("drug", "^", DRUG, 900)
    _draw("anchor", "*", ANCHOR, 2600)

    for n, (x, y) in pos.items():
        kind = G.nodes[n]["kind"]
        fs = 8 if kind == "gene" else (9 if kind == "drug" else 10)
        fw = "bold" if kind in ("module", "anchor") else "normal"
        ax.text(x, y, n, ha="center", va="center", fontsize=fs, fontweight=fw, zorder=5)

    full_title = title if not subtitle else f"{title}\n{subtitle}"
    ax.set_title(full_title, fontsize=14, fontweight="bold")
    legend = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=GENE,
            markersize=13,
            label=gene_legend,
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            color="w",
            markerfacecolor=MODULE,
            markersize=13,
            label=module_legend,
        ),
        Line2D(
            [0],
            [0],
            marker="^",
            color="w",
            markerfacecolor=DRUG,
            markersize=13,
            label=drug_legend,
        ),
        Line2D(
            [0],
            [0],
            marker="*",
            color="w",
            markerfacecolor=ANCHOR,
            markersize=17,
            label=anchor_kind,
        ),
    ]
    if not drugs:
        legend = [h for h in legend if h.get_label() != drug_legend]
    ax.legend(handles=legend, loc="lower left", fontsize=10, frameon=True)
    if footnote:
        ax.text(
            0.99,
            0.01,
            footnote,
            transform=ax.transAxes,
            ha="right",
            fontsize=8,
            style="italic",
        )

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    return out_path


def _demo():
    out = render_mechanistic_map(
        anchor="Type 2 diabetes",
        modules={
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
        },
        drugs={
            "β-cell K_ATP / insulin secretion": ["Glimepiride", "Repaglinide"],
            "Insulin signaling / resistance": ["Metformin", "Pioglitazone"],
            "Incretin / GPCR axis": ["Sitagliptin", "Semaglutide*", "Empagliflozin"],
            "Obesity / adipo-lipid": ["Orforglipron"],
            "MODY / islet transcription factors": ["Sulfonylurea"],
        },
        out_path="/tmp/fig_mechanistic_map_demo.png",
        title="T2D gene–pathway–drug mechanistic map (entities retrieved from Proto-OKN sources)",
        gene_legend="Gene (spoke/rdkg/digcfdekg/prokn)",
        drug_legend="Drug (prokn indication)",
        footnote="*GLP-1 class shown for context",
    )
    print("wrote", out)


if __name__ == "__main__":
    import json
    import sys

    if "--demo" in sys.argv:
        _demo()
    elif len(sys.argv) >= 2 and sys.argv[1].endswith(".json"):
        spec = json.loads(Path(sys.argv[1]).read_text())
        out = (
            sys.argv[2]
            if len(sys.argv) >= 3
            else spec.get("out_path", "fig_mechanistic_map.png")
        )
        spec.pop("out_path", None)
        print("wrote", render_mechanistic_map(out_path=out, **spec))
    else:
        print(__doc__)

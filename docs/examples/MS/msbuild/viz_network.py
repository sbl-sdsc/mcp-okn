#!/usr/bin/env python3
"""Fig 3: MS gene–pathway–drug mechanistic map (entities retrieved from Proto-OKN)."""
import csv, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, RegularPolygon, Circle
from matplotlib.lines import Line2D

OUT = "/sessions/stoic-charming-ride/mnt/MS"
BLUE="#2E86AB"; GREEN="#3B8C4D"; ORANGE="#F18F01"; PURPLE="#A23B72"; RED="#C0392B"; INK="#1c2733"
matrix = list(csv.DictReader(open(f"{OUT}/MS_gene_source_matrix.csv")))
tier = {r["gene"]: r["confidence_tier"].split()[0] for r in matrix}
def gcol(g): return {"T1":RED,"T2":ORANGE,"T3":BLUE}.get(tier.get(g,"T4"), BLUE)

MODULES = [
    ("HLA / antigen\npresentation", 90,
     ["DRB1","DQA1","DQB1","DRA","HLA-A","TAP1"], []),
    ("Cytokine /\nJAK–STAT", 35,
     ["TYK2","JAK1","STAT3","STAT4","IL12A","IFNG","IL2RA","IL7R","SOCS1","TNF"],
     [("Briakinumab","anti-IL12/23")]),
    ("B-cell /\nantibody", -35,
     ["MS4A1","CD19","CD79A","TNFRSF17","POU2AF1","PAX5","BACH2"],
     [("Alemtuzumab","anti-CD52"),("BIIB-091","BTK inhib.")]),
    ("Interferon ↑\n(GXA measured)", -90,
     ["MX1","MX2","OAS2","OAS3","RSAD2","IFI44","IFIT1","IFITM3"], []),
    ("Myelin / CNS", -145,
     ["MBP","MOG","GALC","NEFL","GFAP","CLDN11","KCNJ10"],
     [("Baclofen","spasticity"),("Biotin","progressive")]),
    ("T-cell /\nco-stimulation", 145,
     ["CD28","CD40","CD58","CD6","CD86","CTLA4","ICOS","CD80"], []),
]

fig, ax = plt.subplots(figsize=(16, 12))
R = 6.6
mod_pos = {}
for name, ang, genes, drugs in MODULES:
    a = math.radians(ang); mod_pos[name] = (R*math.cos(a), R*math.sin(a))
    ax.plot([0,mod_pos[name][0]],[0,mod_pos[name][1]], color="#cfd8e0", lw=1.5, zorder=1)

ax.scatter([0],[0], marker="*", s=2800, color=RED, edgecolor="#7b241c", lw=1.5, zorder=6)
ax.text(0,-1.05,"Multiple sclerosis", ha="center", va="top", fontsize=13.5, fontweight="bold", color=INK, zorder=7)

for name, ang, genes, drugs in MODULES:
    mx,my = mod_pos[name]; a = math.radians(ang)
    ax.add_patch(FancyBboxPatch((mx-1.25,my-0.72),2.5,1.44, boxstyle="round,pad=0.02,rounding_size=0.14",
                 fc=GREEN, ec="#2c6b3a", lw=1.5, zorder=5))
    ax.text(mx,my,name, ha="center", va="center", fontsize=10, color="white", fontweight="bold", zorder=6)
    n = len(genes); span = math.radians(96)
    for i,g in enumerate(genes):
        off = 0 if n==1 else (-span/2 + span*i/(n-1))
        ring = 2.85 + (1.02 if i%2 else 0)
        ga = a + off
        gx = mx + ring*math.cos(ga); gy = my + ring*math.sin(ga)
        ax.plot([mx+0.9*math.cos(ga),gx],[my+0.9*math.sin(ga),gy], color="#dce4eb", lw=0.8, zorder=2)
        ax.add_patch(Circle((gx,gy),0.47, fc=gcol(g), ec="#2b3a46", lw=1.0, zorder=4))
        ax.text(gx,gy,g, ha="center", va="center", fontsize=6.4, color="white", fontweight="bold", zorder=5)
    for k,(dname,dnote) in enumerate(drugs):
        da = a + (k-(len(drugs)-1)/2)*0.52
        dx = (R+5.0)*math.cos(da); dy=(R+5.0)*math.sin(da)
        ax.add_patch(RegularPolygon((dx,dy),3, radius=0.55, orientation=0, fc=ORANGE, ec="#a9690b", lw=1.1, zorder=4))
        lx = dx + (0.9 if math.cos(da)>=0 else -0.9)
        ax.text(lx, dy, f"{dname}\n({dnote})", ha=("left" if math.cos(da)>=0 else "right"),
                va="center", fontsize=8, color="#7a4a06", zorder=5)

leg = [
    Line2D([0],[0],marker="*",color="w",markerfacecolor=RED,markersize=20,label="Disease (MS)"),
    Line2D([0],[0],marker="s",color="w",markerfacecolor=GREEN,markersize=13,label="Mechanistic module / pathway"),
    Line2D([0],[0],marker="o",color="w",markerfacecolor=RED,markersize=12,label="Gene — T1 (3 sources)"),
    Line2D([0],[0],marker="o",color="w",markerfacecolor=ORANGE,markersize=12,label="Gene — T2 (2 sources)"),
    Line2D([0],[0],marker="o",color="w",markerfacecolor=BLUE,markersize=12,label="Gene — single source / GXA"),
    Line2D([0],[0],marker="^",color="w",markerfacecolor=ORANGE,markersize=13,label="Drug (prokn indication)"),
]
ax.legend(handles=leg, loc="lower left", fontsize=9.5, frameon=True, framealpha=0.95, edgecolor="#c9d3dc")
ax.set_xlim(-13,13); ax.set_ylim(-12.5,11.5)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("MS gene–pathway–drug mechanistic map  (entities retrieved from Proto-OKN sources)",
             fontsize=15, fontweight="bold", pad=10)
plt.tight_layout()
plt.savefig(f"{OUT}/figures/fig3_gene_pathway_drug_network.png", dpi=140, bbox_inches="tight")
plt.close()
print("fig3 done")

import sys, numpy as np, pandas as pd
sys.path.insert(0,'scripts')
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from okn_figstyle import apply_style, finalize, panel_title
apply_style()
OK=["#0072B2","#D55E00","#009E73","#CC79A7","#E69F00","#56B4E9"]

fig=plt.figure(figsize=(12.6,5.4))
gs=fig.add_gridspec(1,2,width_ratios=[1.32,1],wspace=0.22)

# --- Panel A : study design / KG join schematic ---
ax=fig.add_subplot(gs[0,0]); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis("off")
def box(x,y,w,h,txt,c,fs=8.2):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.12",lw=1.4,
                 edgecolor=c,facecolor=c+"22"))
    ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=fs,color="#111")
def arrow(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=11,
                 lw=1.2,color="0.4",shrinkA=2,shrinkB=2))
box(0.2,7.5,4.3,1.5,"spoke-okn  PREVALENCE_DpL\nCDC PLACES · 9 chronic diseases\n26,343 census places + population",OK[0])
box(0.2,5.0,4.3,1.5,"spoke-okn  PREVALENCEIN_SpL\nCounty Health Rankings 2023\n8 mortality measures · county",OK[1])
box(0.2,2.5,4.3,1.5,"scales  hasIdbCounty\n121,785 federal criminal cases\n2,380 counties",OK[2])
box(0.2,0.2,4.3,1.4,"ruralkg  settlementtype\ncounty population + RUCC\n(census 2013)",OK[4])
box(5.9,5.2,3.8,1.6,"place-level fit\nln Y = ln Y₀ + β ln N\n(population is its own\ndenominator)",OK[5],8.0)
box(5.9,1.9,3.8,1.9,"county-level fit\nvia K2 crosswalk\ncounty FIPS5\n(verified, 3,196 counties)",OK[5],8.0)
arrow(4.5,8.25,5.9,6.4); arrow(4.5,5.75,5.9,3.4); arrow(4.5,3.25,5.9,3.0); arrow(4.5,0.9,5.9,2.3)
ax.text(5.0,9.55,"A   Data streams and joins",fontsize=10.5,fontweight="bold",ha="center")

# --- Panel B : population coverage ---
axb=fig.add_subplot(gs[0,1])
b=pd.read_csv("data/band_stats_place.csv")
g=b[b.dlabel=="obesity"].sort_values("band")
axb.bar(np.exp(g.band+0.5),g.n,width=np.exp(g.band+1)-np.exp(g.band),
        color=OK[0],alpha=.8,edgecolor="white",lw=.6)
axb.set_xscale("log"); axb.set_yscale("log")
axb.set_xlabel("place population (log scale)",fontsize=10)
axb.set_ylabel("number of places",fontsize=10)
axb.axvline(50000,color=OK[1],ls="--",lw=1.5)
axb.text(56000,3200,"50,000\ncutoff",fontsize=8,color=OK[1])
axb.grid(alpha=.3)
panel_title(axb,"B","Population coverage of the place sample")
finalize(fig,1,"figures/fig1_design.png")

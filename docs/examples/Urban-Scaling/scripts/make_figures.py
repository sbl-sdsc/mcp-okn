import sys, numpy as np, pandas as pd
sys.path.insert(0,'scripts')
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from okn_figstyle import apply_style, finalize, legend_outside, panel_title
apply_style()
OK=["#0072B2","#D55E00","#009E73","#CC79A7","#E69F00","#56B4E9","#F0E442","#000000","#8B4513"]

exp=pd.read_csv("data/scaling_exponents.csv")
rob=pd.read_csv("data/scaling_exponents_robustness.csv")
lad=pd.read_csv("data/threshold_ladder.csv")
bin_=pd.read_csv("data/binned_place_lnrate.csv")

# ---------------- Figure 2: main exponent forest plot ----------------
d=exp.sort_values("beta")
fig,ax=plt.subplots(figsize=(9.2,7.4))
cmap={"Chronic disease":OK[0],"Mortality":OK[1],"Crime / justice":OK[2]}
y=np.arange(len(d))
for i,(_,r) in enumerate(d.iterrows()):
    ax.plot([r.ci_lo,r.ci_hi],[i,i],color=cmap[r.domain],lw=2.4,solid_capstyle="round",zorder=2)
    ax.plot(r.beta,i,"o",ms=6.5,color=cmap[r.domain],zorder=3)
ax.axvline(1.0,color="0.35",ls="--",lw=1.3,zorder=1)
ax.set_yticks(y); ax.set_yticklabels([f"{s}  (n={n:,})" for s,n in zip(d.series,d.n)],fontsize=8.5)
ax.set_xlabel("scaling exponent  β   [ Y ∝ N^β ]",fontsize=10)
ax.set_title("Urban scaling exponents for disease, mortality and crime",fontsize=12)
ax.text(1.002,-1.35,"linear (β=1)",fontsize=8,color="0.35")
ax.set_xlim(0.68,1.06); ax.set_ylim(-1.8,len(d)-0.3)
h=[plt.Line2D([],[],color=c,lw=2.4,marker="o",ms=6,label=k) for k,c in cmap.items()]
legend_outside(ax,h,[x.get_label() for x in h],title="domain")
ax.grid(axis="x",alpha=.3)
finalize(fig,2,"figures/fig2_exponent_forest.png")

# ---------------- Figure 3: threshold ladder ----------------
fig,axes=plt.subplots(1,2,figsize=(11.6,5.0),gridspec_kw={"width_ratios":[1.35,1]})
ax=axes[0]
for i,(s,g) in enumerate(lad.groupby("series")):
    g=g.sort_values("threshold")
    ax.plot(g.threshold,g.beta,"o-",ms=4,lw=1.5,color=OK[i%len(OK)],label=s.replace("chronic obstructive pulmonary disease","COPD").replace("cerebrovascular disease","stroke").replace("arteriosclerosis","high cholesterol"))
ax.axhline(1.0,color="0.35",ls="--",lw=1.2)
ax.set_xscale("log"); ax.set_xlabel("minimum population cutoff defining a “city”",fontsize=10)
ax.set_ylabel("scaling exponent  β",fontsize=10)
panel_title(ax,"A","Exponent vs city-size cutoff")
ax.grid(alpha=.3)
legend_outside(ax,where="right",fontsize=7.4,title="outcome")

ax=axes[1]
sub=lad[lad.series=="diabetes mellitus"].sort_values("threshold")
ax.fill_between(sub.threshold,sub.ci_lo,sub.ci_hi,color=OK[0],alpha=.22,label="95% CI")
ax.plot(sub.threshold,sub.beta,"o-",color=OK[0],ms=5,lw=1.8,label="β (diabetes)")
ax.axhline(1.0,color="0.35",ls="--",lw=1.2)
ax.set_xscale("log"); ax.set_xlabel("minimum population cutoff",fontsize=10)
ax.set_ylabel("scaling exponent  β",fontsize=10)
panel_title(ax,"B","Diabetes, with confidence band")
ax.grid(alpha=.3); ax.legend(fontsize=8,loc="upper left",frameon=True)
fig.tight_layout()
finalize(fig,3,"figures/fig3_threshold_ladder.png")

# ---------------- Figure 4: binned prevalence curves (the U-shape) ----------------
cols=["diabetes","stroke","copd","depression","obesity","hypertension","coronary_heart_disease","asthma","high_cholesterol"]
b=bin_[bin_.n>=20]
fig,axes=plt.subplots(3,3,figsize=(11.4,9.0),sharex=True)
for i,c in enumerate(cols):
    ax=axes[i//3][i%3]
    v=b[c]-b[c].iloc[0]
    ax.plot(np.exp(b.mean_lnpop),v,"o-",ms=4,lw=1.6,color=OK[i%len(OK)])
    ax.axhline(0,color="0.6",lw=.9,ls=":")
    ax.set_xscale("log"); ax.grid(alpha=.3)
    ax.set_title(c.replace("_"," "),fontsize=9.5)
    ax.tick_params(labelsize=8)
    if i%3==0: ax.set_ylabel("Δ ln(prevalence)",fontsize=9)
    if i//3==2: ax.set_xlabel("place population",fontsize=9)
fig.suptitle("Age-adjusted prevalence vs place population — binned means (relative to smallest bin)",fontsize=12,y=0.995)
fig.tight_layout(rect=[0,0,1,0.975])
finalize(fig,4,"figures/fig4_binned_prevalence.png")

# ---------------- Figure 5: robustness — all vs restricted ----------------
fig,axes=plt.subplots(1,2,figsize=(12.2,5.6))
ax=axes[0]
place=exp[exp.level=="place"][["series","beta","ci_lo","ci_hi"]].set_index("series")
r50=rob[rob.subset=="pop>=50k"][["series","beta","ci_lo","ci_hi"]].set_index("series")
idx=[s for s in place.index if s in r50.index]
yy=np.arange(len(idx))
for j,s in enumerate(idx):
    ax.plot([place.loc[s,"ci_lo"],place.loc[s,"ci_hi"]],[j-.16]*2,color=OK[5],lw=2.2)
    ax.plot(place.loc[s,"beta"],j-.16,"o",ms=5.5,color=OK[5])
    ax.plot([r50.loc[s,"ci_lo"],r50.loc[s,"ci_hi"]],[j+.16]*2,color=OK[1],lw=2.2)
    ax.plot(r50.loc[s,"beta"],j+.16,"s",ms=5.5,color=OK[1])
ax.axvline(1,color="0.35",ls="--",lw=1.2)
ax.set_yticks(yy); ax.set_yticklabels([s.replace("chronic obstructive pulmonary disease","COPD") for s in idx],fontsize=8.4)
ax.set_xlabel("scaling exponent  β",fontsize=10)
panel_title(ax,"A","Chronic disease: all places vs places ≥50k")
h=[plt.Line2D([],[],color=OK[5],lw=2.2,marker="o",ms=5.5,label="all 26,343 places"),
   plt.Line2D([],[],color=OK[1],lw=2.2,marker="s",ms=5.5,label="709 places ≥ 50,000")]
ax.legend(handles=h,fontsize=8,loc="upper center",bbox_to_anchor=(0.5,-0.13),frameon=False,ncol=2); ax.grid(axis="x",alpha=.3)

ax=axes[1]
cty=exp[exp.level=="county"][["series","beta","ci_lo","ci_hi"]].set_index("series")
met=rob[rob.subset=="metro (RUCC 1-3)"][["series","beta","ci_lo","ci_hi"]].set_index("series")
idx2=[s for s in cty.index if s in met.index]
yy=np.arange(len(idx2))
for j,s in enumerate(idx2):
    ax.plot([cty.loc[s,"ci_lo"],cty.loc[s,"ci_hi"]],[j-.16]*2,color=OK[5],lw=2.2)
    ax.plot(cty.loc[s,"beta"],j-.16,"o",ms=5.5,color=OK[5])
    ax.plot([met.loc[s,"ci_lo"],met.loc[s,"ci_hi"]],[j+.16]*2,color=OK[2],lw=2.2)
    ax.plot(met.loc[s,"beta"],j+.16,"s",ms=5.5,color=OK[2])
ax.axvline(1,color="0.35",ls="--",lw=1.2)
ax.set_yticks(yy); ax.set_yticklabels(idx2,fontsize=8.4)
ax.set_xlabel("scaling exponent  β",fontsize=10)
panel_title(ax,"B","County outcomes: all counties vs metro only")
h=[plt.Line2D([],[],color=OK[5],lw=2.2,marker="o",ms=5.5,label="all counties"),
   plt.Line2D([],[],color=OK[2],lw=2.2,marker="s",ms=5.5,label="metro counties (RUCC 1–3)")]
ax.legend(handles=h,fontsize=8,loc="upper center",bbox_to_anchor=(0.5,-0.13),frameon=False,ncol=2); ax.grid(axis="x",alpha=.3)
fig.tight_layout()
finalize(fig,5,"figures/fig5_robustness.png")
print("figures written")

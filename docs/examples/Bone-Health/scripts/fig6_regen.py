import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
D="data"; F="figures"
c=pd.read_csv(f"{D}/RANKED_bone_candidates.tsv",sep="\t"); top=c.head(20).copy()
ev_cols=['both\narms','Nrf2\ndep','canonical','Mendelian\nbone','GWAS\nBMD/frac','down\n(bone loss)']
def row_ev(r):
    return [1 if r.n_arms==2 else 0,1 if r.nrf2_dependent else 0,1 if pd.notna(r.bone_role) else 0,
            1 if r.bone_evidence=='mendelian' else 0,1 if r.bone_evidence in ('gwas_strong','gwas_bmd') else 0,1 if r.direction=='↓' else 0]
M=np.array([row_ev(r) for _,r in top.iterrows()],dtype=float)
fig,ax=plt.subplots(figsize=(8.8,7.6))
ax.imshow(M,cmap='Greens',vmin=0,vmax=1.6,aspect='auto')
ax.set_xticks(range(len(ev_cols))); ax.set_xticklabels(ev_cols,fontsize=8.5)
ax.set_yticks(range(len(top))); ax.set_yticklabels([f"{r.humanSymbol}  ({r.tier})" for _,r in top.iterrows()],fontsize=8.5)
for i in range(len(top)):
    for j in range(len(ev_cols)):
        if M[i,j]: ax.text(j,i,"+",ha='center',va='center',fontsize=11,fontweight='bold',color='#145a32')
ax.set_title("Figure 6. Evidence matrix — top 20 ranked bone candidates\n(mouse-derived, ortholog-inferred)",fontweight='bold',fontsize=11,loc='left')
plt.savefig(f"{F}/bone_fig6_top_matrix.png",dpi=150,bbox_inches='tight'); plt.close(); print('fig6 regenerated without footnote')

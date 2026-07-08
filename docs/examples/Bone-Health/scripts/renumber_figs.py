import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patches as mp
D="data"; F="figures"
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})

# ---- Figure 4: GO enrichment (was fig5) ----
sig=pd.read_csv(f"{D}/prokn_go_enrichment_labeled.tsv",sep="\t")
sig['neglog']=-np.log10(sig.fdr.clip(lower=1e-300))
top=sig.sort_values('p').drop_duplicates('label').head(20).sort_values('neglog')
tcg={'Translation & ribosome':'#8e44ad','Mitochondrial OXPHOS & respiration':'#2980b9','Oxidative-stress response (Nrf2)':'#c0392b','Proteostasis (ubiquitin-proteasome)':'#16a085','Immune / inflammatory':'#e67e22','Cell cycle & division':'#7f8c8d','Heme / erythroid':'#c39bd3','Muscle (minor)':'#bdc3c7','Metabolic / signaling':'#27ae60','Other':'#95a5a6'}
fig,ax=plt.subplots(figsize=(11.5,7.2)); y=np.arange(len(top))
ax.barh(y,top.neglog,color=[tcg.get(t,'#999') for t in top.theme])
ax.set_yticks(y); ax.set_yticklabels(top.label,fontsize=9)
for i,(nl,f,k,K) in enumerate(zip(top.neglog,top.fold,top.k,top.K)):
    ax.text(nl+0.4,i,f"{f:.1f}x  ({int(k)}/{int(K)} genes)",va='center',fontsize=7.8,color='#333')
ax.set_xlabel("-log10(FDR)"); ax.set_xlim(0,top.neglog.max()*1.28)
ax.set_title("Figure 4. GO biological-process enrichment of the flight bone-marrow signature\n(prokn, Entrez->HGNC-bridged join; top 20 of 69 terms at FDR<0.05, ranked by significance)",fontweight='bold',fontsize=10.5,loc='left')
seen=[t for t in tcg if t in set(top.theme)]
ax.legend([mp.Patch(color=tcg[t]) for t in seen],seen,fontsize=7.8,loc='lower right',frameon=False,title='functional theme',title_fontsize=8)
plt.tight_layout(); plt.savefig(f"{F}/bone_fig4_go_enrichment.png",dpi=150,bbox_inches='tight'); plt.close()

# ---- Figure 5: Reactome (was fig6) ----
sig=pd.read_csv(f"{D}/prokn_reactome_enrichment_labeled.tsv",sep="\t")
sig['neglog']=-np.log10(sig.fdr.clip(lower=1e-300))
top=sig.sort_values('p').drop_duplicates('pathway').head(20).sort_values('neglog')
tcr={'Translation & ribosome':'#8e44ad','Mitochondrial OXPHOS & respiration':'#2980b9','Oxidative-stress response (Nrf2)':'#c0392b','Proteostasis (ubiquitin-proteasome)':'#16a085','Immune / inflammatory':'#e67e22','Cell cycle & division':'#7f8c8d','Hypoxia (HIF)':'#c0392b','ECM / bone / signaling':'#27ae60','Other':'#95a5a6'}
fig,ax=plt.subplots(figsize=(12,7.2)); y=np.arange(len(top))
ax.barh(y,top.neglog,color=[tcr.get(t,'#999') for t in top.theme])
ax.set_yticks(y); ax.set_yticklabels([p[:52] for p in top.pathway],fontsize=8.6)
for i,(nl,f,k,K) in enumerate(zip(top.neglog,top.fold,top.k,top.K)):
    ax.text(nl+0.5,i,f"{f:.1f}x  ({int(k)}/{int(K)})",va='center',fontsize=7.6,color='#333')
ax.set_xlabel("-log10(FDR)"); ax.set_xlim(0,top.neglog.max()*1.30)
ax.set_title("Figure 5. Reactome pathway enrichment of the flight bone-marrow signature\n(prokn, Entrez->HGNC-bridged join; top 20 of 110 pathways at FDR<0.05, ranked by significance)",fontweight='bold',fontsize=10.5,loc='left')
seen=[t for t in tcr if t in set(top.theme)]
ax.legend([mp.Patch(color=tcr[t]) for t in seen],seen,fontsize=7.6,loc='lower right',frameon=False,title='theme',title_fontsize=8)
plt.tight_layout(); plt.savefig(f"{F}/bone_fig5_reactome.png",dpi=150,bbox_inches='tight'); plt.close()

# ---- Figure 6: evidence matrix (was fig4) ----
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
plt.tight_layout(); plt.savefig(f"{F}/bone_fig6_top_matrix.png",dpi=150,bbox_inches='tight'); plt.close()
print("regenerated: bone_fig4_go_enrichment.png, bone_fig5_reactome.png, bone_fig6_top_matrix.png")

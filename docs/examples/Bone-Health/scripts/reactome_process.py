import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patches as mp
D="data"; F="figures"
df=pd.read_csv(f"{D}/prokn_reactome_enrichment.tsv",sep="\t")
def theme(l):
    t=l.lower()
    if any(k in t for k in ['translation','ribosom','rrna','nonsense mediated','cotranslational','elongation','codon','40s','60s','srp','eif2','ternary complex','selenocystein','slits and robos']): return 'Translation & ribosome'
    if any(k in t for k in ['proteasom','ubiquitin','degradation','trcp','apobec','cdc25','emi1','er-phagosome','antigen processing']): return 'Proteostasis (ubiquitin-proteasome)'
    if any(k in t for k in ['electron transport','respiratory','oxidative','atp synth','tca']): return 'Mitochondrial OXPHOS & respiration'
    if any(k in t for k in ['neutrophil','interferon','interleukin','immune','antigen','notch','tnf','cytokine']): return 'Immune / inflammatory'
    if any(k in t for k in ['mitotic','cell cycle','aurka','kinetochore','spindle','g1/s','g2/m','chromosome']): return 'Cell cycle & division'
    if 'hypoxia' in t or 'proline hydroxylation' in t: return 'Hypoxia (HIF)'
    if any(k in t for k in ['collagen','ecm','integrin','fibril','matrix','runx2','osteoblast','wnt','tcf','nfat','calcineurin']): return 'ECM / bone / signaling'
    return 'Other'
df['theme']=df.pathway.apply(theme)
sig=df[df.fdr<0.05].copy().sort_values('p')
sig.to_csv(f"{D}/prokn_reactome_enrichment_labeled.tsv",sep="\t",index=False)
print("Reactome significant:",len(sig),"| themes:"); print(sig.theme.value_counts().to_string())

sig['neglog']=-np.log10(sig.fdr.clip(lower=1e-300))
top=sig.sort_values('p').drop_duplicates('pathway').head(20).sort_values('neglog')
tc={'Translation & ribosome':'#8e44ad','Mitochondrial OXPHOS & respiration':'#2980b9','Proteostasis (ubiquitin-proteasome)':'#16a085','Immune / inflammatory':'#e67e22','Cell cycle & division':'#7f8c8d','Hypoxia (HIF)':'#c0392b','ECM / bone / signaling':'#27ae60','Other':'#95a5a6'}
fig,ax=plt.subplots(figsize=(12,7.2)); y=np.arange(len(top))
ax.barh(y,top.neglog,color=[tc.get(t,'#999') for t in top.theme])
ax.set_yticks(y); ax.set_yticklabels([p[:52] for p in top.pathway],fontsize=8.6)
for i,(nl,f,k,K) in enumerate(zip(top.neglog,top.fold,top.k,top.K)):
    ax.text(nl+0.5,i,f"{f:.1f}x  ({int(k)}/{int(K)})",va='center',fontsize=7.6,color='#333')
ax.set_xlabel("-log10(FDR)"); ax.set_xlim(0,top.neglog.max()*1.30)
ax.set_title("Figure 6. Reactome pathway enrichment of the flight bone-marrow signature\n(prokn, Entrez->HGNC-bridged join; top 20 of 110 pathways at FDR<0.05, ranked by significance)",fontweight='bold',fontsize=10.5,loc='left')
seen=[t for t in tc if t in set(top.theme)]
ax.legend([mp.Patch(color=tc[t]) for t in seen],seen,fontsize=7.6,loc='lower right',frameon=False,title='theme',title_fontsize=8)
plt.tight_layout(); plt.savefig(f"{F}/bone_fig6_reactome.png",dpi=150,bbox_inches='tight'); plt.close(); print("fig6 saved")

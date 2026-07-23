import pandas as pd, numpy as np, matplotlib, sys, re
matplotlib.use('Agg'); import matplotlib.pyplot as plt; import matplotlib.patches as mp
sys.path.insert(0,'.')
from okn_figstyle import apply_style, finalize, legend_outside, ranked_barh, panel_title
apply_style()
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','grey':'#666666'}
enr=pd.read_csv('data/enrichment.csv')
BONE=r'ossif|extracellular matrix|collagen|mineralis|mineraliz|RUNX2|PPARG target|calcium ion|cytoskelet'
theme_kw={'bone / matrix / calcium':BONE,
 'immune / inflammation':r'immun|inflamm|cytokine|interleukin|interferon|MHC|antigen|neutrophil|natural killer|T cell|chemokine|degranulation|TAP binding',
 'metabolic / mitochondrial':r'insulin|glucose|fatty acid|lipid|mitochond|oxidoreduct|metabolic|bile|retino|dehydrogenase|carbon dioxide|oxygen|monooxygenase',
 'stress / proteostasis':r'unfolded|heat|chaperone|stress|toxic|HSP|oxidat|EIF2AK1|Attenuation|jasmonic',
 'transcription / signalling':r'transcription|DNA binding|signal|kinase|receptor|NGF|PI3K|IRS|RING finger'}
tcol={'bone / matrix / calcium':OK['orange'],'immune / inflammation':OK['purple'],
      'metabolic / mitochondrial':OK['green'],'stress / proteostasis':OK['red'],
      'transcription / signalling':OK['blue'],'other':OK['grey']}
def theme(l):
    for k,p in theme_kw.items():
        if re.search(p,str(l),re.I): return k
    return 'other'
sigtag={'all':'S','core':'C','bone_marrow':'M'}
fig=plt.figure(figsize=(17.5,8.0))
gs=fig.add_gridspec(1,3,wspace=1.05)
axes=[fig.add_subplot(gs[i]) for i in range(3)]
for ax,(fam,ttl,letter) in zip(axes,[('GO_BP','GO biological process','A'),('GO_MF','GO molecular function','B'),('Reactome','Reactome pathway','C')]):
    f=enr[(enr.family==fam)&(enr.fdr<=0.05)].copy()
    f['theme']=f.label.map(theme)
    core=f[f.signature=='core'].nsmallest(10,'fdr')
    boney=f[f.theme=='bone / matrix / calcium'].nsmallest(6,'fdr')
    s=pd.concat([core,boney]).drop_duplicates(subset=['category','signature']).drop_duplicates(subset=['label'])
    s2=s.sort_values('fold')
    labs=[("%s  [%s]"%((str(l)[:40]+"...") if len(str(l))>40 else str(l), sigtag[g])) for l,g in zip(s2.label,s2.signature)]
    ranked_barh(ax,labs,s2.fold.values,themes=list(s2.theme),theme_colors=tcol,
                annots=[f"{int(k)}/{int(K)} q={q:.0e}" for k,K,q in zip(s2.k,s2.K,s2.fdr)],xlabel='fold enrichment')
    panel_title(ax,letter,ttl); ax.set_xlim(0,s2.fold.max()*1.75)
legend_outside(axes[1],handles=[mp.Patch(color=c) for c in tcol.values()],labels=list(tcol.keys()),
               where='below',ncol=3,title='theme   ·   signature tag: [S] full 2,686-gene signature   [C] 777-gene core (DE in ≥2 assays)   [M] 395-gene bone-marrow signature')
finalize(fig,4,'fig/fig4_enrichment.png')
print('fig4 done')

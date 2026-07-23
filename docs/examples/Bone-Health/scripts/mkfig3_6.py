import json, pandas as pd, numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt; import matplotlib.patches as mp
sys.path.insert(0,'.')
from okn_figstyle import apply_style, finalize, legend_outside, ranked_barh, panel_title, diverging_heatmap
apply_style()
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','sky':'#56B4E9','yellow':'#F0E442','grey':'#666666'}

agg=pd.read_csv('data/genelab_human_recurrence.csv')
rank=pd.read_csv('data/consensus_ranking.csv')

# ---------- Figure 3: spaceflight signature — recurrence + top consistent genes ----------
fig=plt.figure(figsize=(13.8,6.8))
gs=fig.add_gridspec(1,3,width_ratios=[1,1.2,1.2],wspace=.62)
ax=fig.add_subplot(gs[0])
d=agg.n_assays.value_counts().sort_index()
ax.bar(d.index.astype(str),d.values,color=OK['blue'])
for x,v in zip(range(len(d)),d.values): ax.text(x,v*1.12,str(v),ha='center',fontsize=7.6)
ax.set_yscale('log'); ax.set_xlabel('clean assays in which the gene is DE'); ax.set_ylabel('human orthologs (log scale)')
panel_title(ax,'A','Recurrence across 14 assays')

top=agg[(agg.consistent_direction=='consistent')].nlargest(18,'n_assays').sort_values('n_assays')
ax=fig.add_subplot(gs[1])
cols=[OK['red'] if r.net_direction=='up' else OK['blue'] for r in top.itertuples()]
ax.barh(top.humanSymbol,top.n_assays,color=cols)
for i,r in enumerate(top.itertuples()): ax.text(r.n_assays+0.12,i,f"{r.max_abs_log2fc:+.1f}",va='center',fontsize=7.4)
ax.set_xlabel('number of clean assays (label = max log2FC)'); ax.set_xlim(0,13.2)
panel_title(ax,'B','Most recurrent (consistent direction)')

bone=['ALPL','RUNX2','SP7','IBSP','BGLAP','DMP1','MEPE','SPP1','COL1A1','SERPINH1','MMP13','MMP14','MMP2','MMP9','CTSK','ACP5','ATP6V0D2','PTH1R','SOX9','WNT16','WNT4','PPARG','POSTN','SLC34A1']
bd=agg[agg.humanSymbol.isin(bone)].copy().sort_values('max_abs_log2fc')
ax=fig.add_subplot(gs[2])
cols=[OK['red'] if v>0 else OK['blue'] for v in bd.max_abs_log2fc]
ax.barh(bd.humanSymbol,bd.max_abs_log2fc,color=cols)
ax.axvline(0,color='#333',lw=.8)
for i,r in enumerate(bd.itertuples()):
    off=0.12 if r.max_abs_log2fc>0 else -0.12
    ax.text(r.max_abs_log2fc+off,i,f"{r.n_assays}a",va='center',ha='left' if r.max_abs_log2fc>0 else 'right',fontsize=7)
ax.set_xlabel('max |log2FC| in spaceflight (signed; label = n assays)'); ax.set_xlim(-4.2,5.8)
panel_title(ax,'C','Canonical bone genes')
legend_outside(ax,handles=[mp.Patch(color=OK['red']),mp.Patch(color=OK['blue'])],
               labels=['up in spaceflight','down in spaceflight'],where='below',ncol=2)
finalize(fig,3,'fig/fig3_spaceflight_signature.png')

# ---------- Figure 4: GO BP / GO MF / Reactome enrichment ----------
enr=pd.read_csv('data/enrichment.csv')
fig,axes=plt.subplots(1,3,figsize=(15.5,7.0))
theme_kw={'bone / matrix':'ossif|extracellular matrix|collagen|mineral|bone',
          'immune / inflammation':'immun|inflamm|cytokine|interleukin|interferon|MHC|antigen|neutrophil|natural killer|T cell|chemokine|degranulation',
          'metabolic / mitochondrial':'insulin|glucose|fatty acid|lipid|mitochond|oxidoreduct|metabolic|bile|retino|dehydrogenase|carbon dioxide|oxygen',
          'stress / proteostasis':'unfolded|heat|chaperone|stress|toxic|HSP|oxidat|EIF2AK1|Attenuation',
          'transcription / signalling':'transcription|DNA binding|signal|kinase|receptor|RUNX2|PPARG|adipogen|NGF|PI3K|IRS'}
def theme(lbl):
    import re
    for k,p in theme_kw.items():
        if re.search(p,str(lbl),re.I): return k
    return 'other'
tcol={'bone / matrix':OK['orange'],'immune / inflammation':OK['purple'],'metabolic / mitochondrial':OK['green'],
      'stress / proteostasis':OK['red'],'transcription / signalling':OK['blue'],'other':OK['grey']}
for ax,(fam,sig,ttl,letter) in zip(axes,[('GO_BP','core','GO biological process','A'),
                                          ('GO_MF','core','GO molecular function','B'),
                                          ('Reactome','core','Reactome pathway','C')]):
    s=enr[(enr.family==fam)&(enr.signature==sig)&(enr.fdr<=0.05)].nsmallest(14,'fdr').sort_values('fold')
    labs=[str(l)[:52] for l in s.label]
    ranked_barh(ax,labs,s.fold.values,themes=[theme(l) for l in s.label],theme_colors=tcol,
                annots=[f"{int(k)}/{int(K)}  q={q:.1e}" for k,K,q in zip(s.k,s.K,s.fdr)],xlabel='fold enrichment')
    panel_title(ax,letter,ttl)
    ax.set_xlim(0,max(s.fold)*1.9)
h=[mp.Patch(color=c) for k,c in tcol.items()]; l=list(tcol.keys())
legend_outside(axes[1],handles=h,labels=l,where='below',ncol=3,title='theme')
finalize(fig,4,'fig/fig4_enrichment.png')

# ---------- Figure 5: upstream regulators ----------
reg=pd.read_csv('data/upstream_regulators.csv')
keep=reg[reg.regLabel.str.contains('AP1|AP_1|NFAT|MEF2|LEF1|SRF|HSF|STAT5|ERR1|TCF4|NFKB',case=False,regex=True)&(reg.fdr<=0.05)].nsmallest(9,'p')
reg=pd.concat([reg[reg.fdr<=0.05].nsmallest(16,'p'),keep]).drop_duplicates('reg').sort_values('fold')
fig,ax=plt.subplots(figsize=(10.4,8.0))
def rtheme(l):
    import re
    m={'osteoclast / immune (NFAT, AP-1, STAT)':'NFAT|AP1|AP-1|STAT|NFKB|TGANTCA',
       'Wnt / TCF-LEF':'LEF1|TCF4|TCF7',
       'muscle / mechanotransduction (MEF2, SRF)':'MEF2|SRF|MYOD|E12|E47',
       'stress / heat shock':'HSF|PSMB|ATF',
       'metabolic / nuclear receptor':'ERR|T3R|HNF4|PPAR|PAX4|FREAC|NF1'}
    for k,p in m.items():
        if re.search(p,str(l),re.I): return k
    return 'other / motif'
rc={'osteoclast / immune (NFAT, AP-1, STAT)':OK['red'],'Wnt / TCF-LEF':OK['green'],
    'muscle / mechanotransduction (MEF2, SRF)':OK['blue'],'stress / heat shock':OK['purple'],
    'metabolic / nuclear receptor':OK['orange'],'other / motif':OK['grey']}
ranked_barh(ax,list(reg.regLabel),reg.fold.values,themes=[rtheme(x) for x in reg.regLabel],theme_colors=rc,
            annots=[f"{int(k)}/{int(K)}  q={q:.1e}" for k,K,q in zip(reg.k,reg.K,reg.fdr)],
            xlabel='fold enrichment (observed / expected)')
ax.set_xlim(0,reg.fold.max()*1.5)
legend_outside(ax,handles=[mp.Patch(color=c) for c in rc.values()],labels=list(rc.keys()),where='below',ncol=2,title='regulator family')
finalize(fig,5,'fig/fig5_upstream_regulators.png')

# ---------- Figure 6: cross-KG bone-trait convergence ----------
sfb=pd.read_csv('data/sf_x_bmd.csv')
te=pd.read_csv('data/trait_enrichment.csv')
fig=plt.figure(figsize=(15.2,7.6))
gs=fig.add_gridspec(1,2,width_ratios=[1.35,1],wspace=.55)
ax=fig.add_subplot(gs[0])
t=te[te.signature=='all'].nsmallest(12,'p').sort_values('fold')
cols=[OK['green'] if f<=0.05 else OK['grey'] for f in t.fdr]
ax.barh([str(x)[:46] for x in t.trait],t.fold.values,color=cols)
ax.axvline(1,color='#333',lw=.9,ls='--')
for i,r in enumerate(t.itertuples()): ax.text(r.fold+0.02,i,f"{int(r.k)}/{int(r.K)}  q={r.fdr:.1e}",va='center',fontsize=7.4)
ax.set_xlabel('fold enrichment vs digcfdekg background (N = 21,710 genes)'); ax.set_xlim(0,2.35)
panel_title(ax,'A','Bone-trait gene-set enrichment of the spaceflight signature')
ax=fig.add_subplot(gs[1])
tg=sfb.groupby('humanSymbol').agg(nt=('trait','nunique'),w=('weight','max')).nlargest(20,'nt').sort_values('nt')
ax.barh(tg.index,tg.nt,color=OK['orange'])
for i,(g,r) in enumerate(tg.iterrows()): ax.text(r.nt+0.15,i,f"w={r.w:.1f}",va='center',fontsize=7.4)
ax.set_xlabel('distinct bone traits (of 25) with a CFDE REVEAL gene→trait edge'); ax.set_xlim(0,21)
panel_title(ax,'B','Top spaceflight genes by bone-trait breadth')
finalize(fig,6,'fig/fig6_bone_trait_convergence.png')
print('figs 3-6 done')

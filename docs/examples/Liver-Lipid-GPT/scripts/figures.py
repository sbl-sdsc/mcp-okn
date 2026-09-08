from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from okn_figstyle import apply_style, panel_title, finalize, legend_outside
apply_style()
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data';F=ROOT/'figures'
s=pd.read_csv(D/'assay_summary.tsv',sep='\t');e=pd.read_csv(D/'enrichment.tsv',sep='\t');m=pd.read_csv(D/'mouse_results.tsv',sep='\t')
labels=['STS-135\nOSD-25','RR1-CASIS\nOSD-47','RR3\nOSD-137']
fig,axs=plt.subplots(1,2,figsize=(11,4.2),gridspec_kw={'wspace':.36})
ax=axs[0];x=np.arange(3)
ax.bar(x,s.retained,color='#486D96');ax.set_yscale('log');ax.set_ylim(1,12000);ax.set_xticks(x,labels);ax.set_ylabel('Retained gene results (log scale)')
for j,v in enumerate(s.retained):ax.text(j,v*1.15,f'{v:,}',ha='center',fontsize=10)
panel_title(ax,'A','Available expression records')
ax=axs[1];ax.bar(x-.17,s.up,.34,label='Up in flight',color='#C65555');ax.bar(x+.17,s.down,.34,label='Down in flight',color='#427CB3');ax.set_xticks(x,labels);ax.set_ylim(0,105);ax.set_ylabel('Genes passing strict rule')
for j,(up,down) in enumerate(zip(s.up,s.down)):
    ax.text(j-.17,up+2,str(up),ha='center',fontsize=9);ax.text(j+.17,down+2,str(down),ha='center',fontsize=9)
legend_outside(ax,where='below',ncol=2);panel_title(ax,'B','Twofold change and adjusted p ≤ 0.05');finalize(fig,1,F/'fig1_assay_coverage.png');plt.close(fig)

genes=['Plin5','Pnpla2','Apoa4','Crat','Ppara','Mlxipl','Elovl6']
g=m[(m.study=='OSD-25')&m.symbol.isin(genes)].set_index('symbol').loc[genes].reset_index()
fig,ax=plt.subplots(figsize=(9,4.2));y=np.arange(len(g));ax.barh(y,g.lfc,color=['#C65555' if v>0 else '#427CB3' for v in g.lfc]);ax.set_yticks(y,g.symbol);ax.invert_yaxis();ax.axvline(0,color='#333',lw=.7);ax.set_xlim(-1.8,2.1);ax.set_xlabel('Flight / ground log₂ fold change')
for j,row in g.iterrows():ax.text(1.7,j,f'q={row.p:.2g}',va='center',fontsize=9)
ax.set_title('Selected STS-135 lipid-related transcripts');finalize(fig,2,F/'fig2_gene_effects.png');plt.close(fig)

terms=['fatty acid beta-oxidation','fatty acid metabolic process','lipid metabolic process']
fig,axs=plt.subplots(1,2,figsize=(12,4),gridspec_kw={'wspace':.58})
for ax,bg,letter,title in zip(axs,['all annotated','retained conditional'],['A','B'],['All GO-annotated genes','Only retained, GO-annotated genes']):
    z=e[(e.study=='OSD-25')&(e.rule=='sensitivity')&(e.direction=='up')&(e.family=='GO BP')&(e.background==bg)&e.label.isin(terms)].set_index('label').loc[terms]
    vals=-np.log10(z.fdr.clip(lower=1e-300));ax.barh(np.arange(3),vals,color='#486D96');ax.set_yticks(np.arange(3),['Fatty acid β-oxidation','Fatty acid metabolism','Lipid metabolism']);ax.invert_yaxis();ax.axvline(-np.log10(.05),color='#777',ls='--');ax.set_xlim(0,5.4);ax.set_xlabel('−log₁₀(BH FDR)')
    for j,(_,r) in enumerate(z.iterrows()):ax.text(max(vals.iloc[j],.02)+.12,j,f'{r.fold:.2f}×; {r.k}/{r.K}',va='center',fontsize=9,bbox=dict(facecolor='white',edgecolor='none',pad=1.5))
    panel_title(ax,letter,title)
finalize(fig,3,F/'fig3_background_sensitivity.png');plt.close(fig)

z=e[(e.study=='OSD-25')&(e.rule=='strict')&(e.direction=='all')&(e.family=='DIG lipid traits')&(e.background=='retained conditional')].sort_values('fold',ascending=False)
fig,ax=plt.subplots(figsize=(10,4));ax.barh(np.arange(len(z)),z.fold,color='#486D96');ax.set_yticks(np.arange(len(z)),z.label.str.replace('non-alcoholic fatty liver disease','Fatty liver disease').str.replace('triglyceride measurement','Triglycerides'));ax.invert_yaxis();ax.set_xlabel('Observed / expected overlap');ax.set_xlim(0,5.7)
for j,(_,r) in enumerate(z.iterrows()):ax.text(r.fold+.1,j,f'{r.k}/{r.K}; FDR={r.fdr:.2g}',va='center',fontsize=9)
ax.set_title('Human lipid-trait links within the retained STS-135 signature');finalize(fig,4,F/'fig4_trait_enrichment.png');plt.close(fig)

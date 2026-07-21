import sys, json, csv, collections, re
sys.path.insert(0,'scripts')
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import okn_figstyle as F
F.apply_style()
D='data'; FIG='figures'
S=json.load(open('stats.json'))
rd=lambda f: pd.read_csv(D+'/'+f, low_memory=False)
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7',
    'sky':'#56B4E9','yellow':'#F0E442','grey':'#7f7f7f'}

# ---------- FIG 1 : design overview ----------
g=rd('ranked_genes_tiered.csv')
fig,axes=plt.subplots(1,3,figsize=(13.5,4.3))
ax=axes[0]
streams={'digcfdekg\n(PIGEAN stat.)':849,'spoke-okn\n(curated D-G)':678,'biomarkerkg\n(GWAS variants)':1028,
         'prokn\n(ClinVar curated)':13,'GXA\n(differential expr.)':74,'pankgraph\n(islet eQTL)':8371}
ks=list(streams); vs=[streams[k] for k in ks]
b=ax.barh(range(len(ks)),vs,color=[OK['blue'],OK['green'],OK['orange'],OK['red'],OK['purple'],OK['sky']])
ax.set_yticks(range(len(ks))); ax.set_yticklabels(ks,fontsize=8); ax.invert_yaxis()
ax.set_xscale('log'); ax.set_xlabel('genes contributed (log scale)')
for i,v in enumerate(vs): ax.text(v*1.1,i,str(v),va='center',fontsize=8)
F.panel_title(ax,'A','Evidence streams')
ax=axes[1]
ns=g.n_disease_streams.value_counts().sort_index()
ax.bar([str(i) for i in ns.index],ns.values,color=OK['blue'])
for i,v in enumerate(ns.values): ax.text(i,v*1.03,str(v),ha='center',fontsize=8)
ax.set_yscale('log'); ax.set_xlabel('disease-anchored evidence streams supporting the gene')
ax.set_ylabel('genes (log scale)')
F.panel_title(ax,'B','Cross-source corroboration')
ax=axes[2]
tc=g.tier.value_counts().reindex(['A','B','C'])
cols=[OK['red'],OK['orange'],OK['grey']]
ax.bar(tc.index,tc.values,color=cols)
for i,v in enumerate(tc.values): ax.text(i,v*1.03,str(v),ha='center',fontsize=9)
ax.set_ylabel('genes'); ax.set_xlabel('confidence tier')
F.panel_title(ax,'C','Tier distribution')
F.finalize(fig,1,f'{FIG}/fig1_design_overview.png')

# ---------- FIG 2 : ranked consensus genes ----------
top=g.head(30).iloc[::-1]
fig,ax=plt.subplots(figsize=(9.2,8.2))
comp={'curated knowledge':top.ev_curated*3.0,'genetic association':top.ev_genetic*2.5,
      'statistical (PIGEAN)':np.clip(top.pigean_weight.fillna(0)/10*2,0,2)*2.0,
      'differential activity':top.ev_diffexpr*1.5,'molecular QTL':top.ev_qtl*1.0,
      'druggable target':top.ev_druggable*1.5,'AOP / exposure':top.ev_aop*1.0+top.ev_exposure*0.5}
colors=[OK['green'],OK['blue'],OK['sky'],OK['orange'],OK['purple'],OK['red'],OK['yellow']]
left=np.zeros(len(top))
for (lab,val),c in zip(comp.items(),colors):
    ax.barh(range(len(top)),val,left=left,color=c,label=lab,height=0.72)
    left=left+val.values
ax.set_yticks(range(len(top))); ax.set_yticklabels(top.symbol,fontsize=9)
ax.set_xlabel('integrated evidence score (stacked by evidence type)')
for i,(v,t) in enumerate(zip(left,top.tier)): ax.text(v+0.12,i,t,va='center',fontsize=8,color='#333')
F.legend_outside(ax,where='below',ncol=4,title='evidence type (weight)')
ax.set_title('Top 30 consensus Type 2 Diabetes genes')
F.finalize(fig,2,f'{FIG}/fig2_ranked_genes.png')

# ---------- FIG 3 : GO + Reactome enrichment ----------
go=rd('enrichment_GO.csv'); rx=rd('enrichment_Reactome.csv')
fig,axes=plt.subplots(1,2,figsize=(15.5,7.4))
def enr(ax,df,labcol,title,color):
    d=df.head(18).iloc[::-1]
    labs=[(s[:52]+'…' if len(s)>52 else s) for s in d[labcol]]
    ax.barh(range(len(d)),-np.log10(d.fdr.clip(lower=1e-300)),color=color,height=0.72)
    ax.set_yticks(range(len(d))); ax.set_yticklabels(labs,fontsize=8)
    ax.set_xlabel('$-\\log_{10}$ FDR')
    for i,(f_,k,K) in enumerate(zip(d.fold,d.k,d.K)):
        ax.text(-np.log10(d.fdr.clip(lower=1e-300)).iloc[i]+0.3,i,f'{f_:.1f}× ({k}/{K})',va='center',fontsize=7.5)
    ax.set_xlim(0,ax.get_xlim()[1]*1.28); ax.set_title(title,fontsize=11)
enr(axes[0],go,'category',f'GO over-representation (n={S["go_n"]}, N={S["go_N"]})',OK['blue'])
F.panel_title(axes[0],'A','')
enr(axes[1],rx,'category',f'Reactome over-representation (n={S["rx_n"]}, N={S["rx_N"]})',OK['green'])
F.panel_title(axes[1],'B','')
F.finalize(fig,3,f'{FIG}/fig3_enrichment.png')

# ---------- FIG 4 : islet molecular activity ----------
gxa=rd('gxa_t2d_expression.csv'); ocr=rd('pankgraph_t2d_ocr.csv')
fig,axes=plt.subplots(1,2,figsize=(14.2,6.4))
ax=axes[0]
gx=gxa.dropna(subset=['log2fc']).copy(); gx['log2fc']=pd.to_numeric(gx.log2fc,errors='coerce')
gx=gx.dropna(subset=['log2fc']).sort_values('log2fc')
sel=pd.concat([gx.head(10),gx.tail(10)]).drop_duplicates('gene_symbol')
cols=[OK['blue'] if v<0 else OK['red'] for v in sel.log2fc]
ax.barh(range(len(sel)),sel.log2fc,color=cols,height=0.72)
ax.set_yticks(range(len(sel))); ax.set_yticklabels([f"{s}  ({t[:22]})" for s,t in zip(sel.gene_symbol,sel.anatomy_label.fillna('n/a'))],fontsize=8)
ax.axvline(0,color='#444',lw=0.8); ax.set_xlabel('log$_2$ fold change (T2D vs control)')
F.panel_title(ax,'A','Differential expression — gene-expression-atlas-okn')
ax=axes[1]
o=ocr.copy(); o['lr']=pd.to_numeric(o.t2d_vs_nondiabetic_log2ratio_mean,errors='coerce')
o=o.dropna(subset=['lr'])
order=o.groupby('cell_label')['lr'].median().sort_values().index.tolist()
data=[o[o.cell_label==c]['lr'].values for c in order]
bp=ax.boxplot(data,vert=False,labels=order,showfliers=False,patch_artist=True,widths=0.6)
for p in bp['boxes']: p.set_facecolor(OK['sky']); p.set_alpha(0.75)
for med in bp['medians']: med.set_color('#222')
ax.axvline(0,color=OK['red'],lw=1.0,ls='--')
ax.set_xlabel('log$_2$ (T2D / non-diabetic) open-chromatin gene-activity')
ax.tick_params(axis='y',labelsize=8.5)
F.panel_title(ax,'B','Chromatin accessibility by islet cell type — pankgraph')
F.finalize(fig,4,f'{FIG}/fig4_islet_activity.png')

# ---------- FIG 5 : therapeutic landscape ----------
rl=rd('rdkg_t2d_relations.csv'); tc=rd('prokn_core_target_compounds.csv'); ind=rd('prokn_t2d_indications.csv')
fig,axes=plt.subplots(1,2,figsize=(14.2,5.8))
ax=axes[0]
classes={'DPP-4 inhibitor':(20,26),'Biguanide':(18,2),'GLP-1 receptor agonist':(16,4),'SGLT2 inhibitor':(15,17),
 'Sulfonylurea':(14,7),'Thiazolidinedione (PPARG)':(14,13),'Insulin / analogue':(10,0),
 'α-glucosidase inhibitor':(3,2),'Glinide':(3,3),'Other (GKA, imeglimin…)':(1,3),'Dual/triple incretin':(1,0)}
ks=list(classes)[::-1]; a=[classes[k][0] for k in ks]; b_=[classes[k][1] for k in ks]
y=np.arange(len(ks))
ax.barh(y-0.2,a,height=0.38,color=OK['green'],label='rdkg — DrugBank `treats` (approved)')
ax.barh(y+0.2,b_,height=0.38,color=OK['blue'],label='prokn — ChEMBL indication (incl. investigational)')
ax.set_yticks(y); ax.set_yticklabels(ks,fontsize=8.5); ax.set_xlabel('distinct agents')
F.legend_outside(ax,where='below',ncol=1)
F.panel_title(ax,'A','Antidiabetic classes by supplier')
ax=axes[1]
d=tc[tc.interaction_predicate.astype(str).str.contains('RO_0002436')]
cnt=d.groupby('target_gene_symbol').compound.nunique().sort_values(ascending=False).head(14).iloc[::-1]
ax.barh(range(len(cnt)),cnt.values,color=OK['orange'],height=0.72)
ax.set_yticks(range(len(cnt))); ax.set_yticklabels(cnt.index,fontsize=9)
ax.set_xlabel('distinct compounds with direct target binding (prokn)')
for i,v in enumerate(cnt.values): ax.text(v+0.4,i,str(v),va='center',fontsize=8)
F.panel_title(ax,'B','Druggability of the consensus core')
F.finalize(fig,5,f'{FIG}/fig5_therapeutics.png')
print('figs 1-5 done')

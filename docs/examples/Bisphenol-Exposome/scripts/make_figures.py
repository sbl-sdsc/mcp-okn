#!/usr/bin/env python3
"""Generate all figures for the Bisphenol-Exposome OKN report."""
import sys, json, math
sys.path.insert(0, "/sessions/vibrant-inspiring-edison/mnt/.claude/skills/okn-report-style/scripts")
sys.path.insert(0, ".")
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import okn_figstyle as ok
from okn_figstyle import apply_style, ranked_barh, legend_outside, panel_title, finalize, THEME
from mechanistic_map import render_mechanistic_map
apply_style()
D="data"; F="figures"

# ---- functional theme map for target genes ----
THEMES={
 'Estrogen / ER':['ESR1','ESR2','ESRRA'],
 'Androgen / steroid':['AR','PGR','NR3C1','CYP19A1','SULT2A1','CYP17A1'],
 'Thyroid axis':['THRA','THRB','DIO1','DIO2','DIO3','TSHR','TRHR','SLC5A5','THRSP'],
 'Metabolic / PPAR (obesogen)':['PPARA','PPARD','PPARG','RXRA','RXRB','NR1H4','SREBF1','FASN','LPL','FABP1','HNF4A','PDK4','ACOX1','HMGCS2'],
 'Xenobiotic / PXR-CAR-AhR':['NR1I2','NR1I3','AHR','CYP1A1','CYP1A2','CYP3A4','CYP2B6','CYP2C9','CYP2C19','CYP2E1','ABCG2','ABCB11','ABCC3','UGT1A1'],
 'Oxidative / ER stress':['NFE2L2','NQO1','GCLC','HSF1','HSPA1A','ATF6','XBP1','DDIT3','CAT','GSTA2','SIRT3'],
 'Apoptosis / DNA-damage / proliferation':['TP53','BAX','CASP3','CDKN1A','MYC','CCND1','H2AX','BCL2L11','FAS','PTEN','PIK3CA'],
 'Inflammation / vascular':['TNF','IL6','IL1A','CXCL8','ICAM1','VCAM1','SERPINE1','SELE','SELP','CCL2','PLAT','PLAU','F3','THBD','KDR'],
 'Developmental / other':['SHH','GLI1','PAX6','SOX1','FOXA2','VDR','RARA','RORA','RORC','SP1','EGR1','FOS','JUN'],
}
g2theme={}
for t,gs in THEMES.items():
    for g in gs: g2theme[g]=t
theme_order=list(THEMES.keys())
tcolors={t:THEME[i%len(THEME)] for i,t in enumerate(theme_order)}

def theme_of(sym): return g2theme.get(sym,'Developmental / other')

# ============ FIG 1: per-chemical mechanistic breadth ============
chem=pd.read_csv(f"{D}/chem_summary.csv")
inv=pd.read_csv(f"{D}/bisphenol_inventory.csv")
cls={r.abbr:r.chem_class for _,r in inv.iterrows()}
# class -> color
classes=sorted(set(cls.get(a,'other') for a in chem.abbr))
ccol={c:THEME[i%len(THEME)] for i,c in enumerate(classes)}
chem=chem.sort_values('n_target_genes',ascending=False)
fig,ax=plt.subplots(figsize=(8.6,5.4))
labels=list(chem.abbr); vals=list(chem.n_target_genes)
themes=[cls.get(a,'other') for a in labels]
annots=[f"{int(n)} assays · AC50 {a:.3g} µM" for n,a in zip(chem.n_active_assays,chem.min_ac50_uM)]
ranked_barh(ax,labels,vals,themes=themes,theme_colors=ccol,annots=annots,xlabel="distinct human target genes (ICE active hits)")
ok.theme_legend(ax,ccol,where="below",title="chemical class")
panel_title(ax,"","")
finalize(fig,1,f"{F}/fig1_chemical_breadth.png")

# ============ FIG 2: molecular target landscape ============
gs=pd.read_csv(f"{D}/gene_target_summary_human.csv").sort_values(['n_bisphenols','n_assays'],ascending=False).head(28)
fig,ax=plt.subplots(figsize=(8.8,7.2))
labels=list(gs.symbol); vals=list(gs.n_bisphenols)
themes=[theme_of(s) for s in labels]
annots=[f"{int(a)} assays · {v:.3g} µM" for a,v in zip(gs.n_assays,gs.min_ac50_uM)]
ranked_barh(ax,labels,vals,themes=themes,theme_colors=tcolors,annots=annots,xlabel="number of bisphenols active on target (of 15)")
ok.theme_legend(ax,{t:tcolors[t] for t in theme_order},where="below",title="functional theme")
finalize(fig,2,f"{F}/fig2_target_landscape.png")

# ============ FIG 3: chemical x adverse-outcome domain heatmap ============
ed=pd.read_csv(f"{D}/effect_domain_by_chem.csv")
dom_order=['Cancer','AcuteTox','DART','CardioTox','Endothelial Injury/Coagulation','Estrogen',
           'Other Steroid Hormone','Androgen','Thyroid Hormone','Change in Vasoactivity','Cardiomyocyte/Myocardial Injury']
piv=ed.pivot_table(index='abbr',columns='effect_domain',values='n_assays',aggfunc='sum',fill_value=0)
piv=piv.reindex(columns=[d for d in dom_order if d in piv.columns])
piv=piv.reindex(index=chem.abbr)  # order by breadth
fig,ax=plt.subplots(figsize=(9.4,6.2))
m=piv.values.astype(float)
im=ax.imshow(m,cmap="YlOrRd",aspect="auto")
ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels([c.replace(' Injury/Coagulation','').replace('Cardiomyocyte/Myocardial Injury','Cardiomyocyte inj.').replace('Change in ','') for c in piv.columns],rotation=40,ha='right',fontsize=9)
ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index,fontsize=9)
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        if m[i,j]>0: ax.text(j,i,int(m[i,j]),ha='center',va='center',fontsize=7,color='black' if m[i,j]<m.max()*0.6 else 'white')
cb=fig.colorbar(im,ax=ax,fraction=0.03,pad=0.02); cb.set_label('active assay endpoints (n)',fontsize=9)
ax.set_xlabel('adverse-outcome / toxicity domain (ICE mayInformOn)',fontsize=10)
finalize(fig,3,f"{F}/fig3_effect_domains.png")

# ============ FIG 4: GO + Reactome enrichment ============
react=pd.read_csv(f"{D}/reactome_enrichment.csv"); react=react[react.FDR<0.05].sort_values('FDR').head(14)
go=pd.read_csv(f"{D}/go_enrichment.csv"); go=go[go.FDR<0.05].sort_values('FDR').head(14)
fig,axes=plt.subplots(1,2,figsize=(15,7))
def enr_bar(ax,df,labelcol,title):
    df=df.iloc[::-1]
    labs=[str(l)[:46] for l in df[labelcol]]; vals=list(-np.log10(df.FDR))
    ann=[f"{f:.0f}× ({int(k)}/{int(K)})" for f,k,K in zip(df.fold,df.k,df.K)]
    y=np.arange(len(labs)); ax.barh(y,vals,color=ok.UP)
    ax.set_yticks(y); ax.set_yticklabels(labs,fontsize=9)
    ax.set_xlabel('-log10(FDR)',fontsize=10); ax.set_xlim(0,max(vals)*1.32)
    for i,(v,a) in enumerate(zip(vals,ann)): ax.text(v+max(vals)*0.01,i,a,va='center',fontsize=7.5,color='#333')
    ax.set_title(title,fontsize=11,weight='bold')
panel_title(axes[0],"A","Reactome pathways"); enr_bar(axes[0],react,'pwLabel','')
panel_title(axes[1],"B","GO biological process"); enr_bar(axes[1],go,'goLabel','')
finalize(fig,5,f"{F}/fig5_enrichment.png")

# ============ FIG 5: disease enrichment (rdkg) ============
de=pd.read_csv(f"{D}/rdkg_disease_enrichment.csv"); de=de[de.FDR<0.05]
# curate representative (dedupe near-identical), rank by fold
keep=['ischemia reperfusion injury','non-alcoholic steatohepatitis','brain ischemia','thyroid cancer',
 'thyroid tumor','transient ischemic attack (disease)','coronary artery disease','myocardial ischemia',
 'inherited obesity','unipolar depression','breast carcinoma','prostate cancer','liver cancer',
 'endometrial carcinoma (disease)','pulmonary fibrosis','type 2 diabetes mellitus','end stage renal failure']
de2=de[de.dlabel.isin(keep)].drop_duplicates('dlabel').sort_values('fold',ascending=False).head(16)
catmap={'ischemia reperfusion injury':'Cardiovascular','brain ischemia':'Cardiovascular','transient ischemic attack (disease)':'Cardiovascular','coronary artery disease':'Cardiovascular','myocardial ischemia':'Cardiovascular','pulmonary fibrosis':'Other','end stage renal failure':'Other',
 'non-alcoholic steatohepatitis':'Metabolic','inherited obesity':'Metabolic','type 2 diabetes mellitus':'Metabolic','liver cancer':'Cancer',
 'thyroid cancer':'Thyroid/Endocrine','thyroid tumor':'Thyroid/Endocrine','breast carcinoma':'Hormone cancer','prostate cancer':'Hormone cancer','endometrial carcinoma (disease)':'Hormone cancer','unipolar depression':'Neuro-behavioral'}
dcat_order=['Cardiovascular','Metabolic','Thyroid/Endocrine','Hormone cancer','Cancer','Neuro-behavioral','Other']
dcol={c:THEME[i%len(THEME)] for i,c in enumerate(dcat_order)}
fig,ax=plt.subplots(figsize=(9.2,6.8))
de2=de2.sort_values('fold')
labs=[str(l)[:40] for l in de2.dlabel]; vals=list(de2.fold)
themes=[catmap.get(l,'Other') for l in de2.dlabel]
ann=[f"{f:.0f}× ({int(k)}/{int(K)}) FDR {fd:.0e}" for f,k,K,fd in zip(de2.fold,de2.k,de2.K,de2.FDR)]
ranked_barh(ax,labs[::-1],vals[::-1],themes=themes[::-1],theme_colors=dcol,annots=ann[::-1],xlabel="fold enrichment (observed / expected)")
ok.theme_legend(ax,dcol,where="below",title="disease category")
finalize(fig,6,f"{F}/fig6_disease_enrichment.png")

# ============ FIG 6: AOP chains schematic ============
aopk=pd.read_csv(f"{D}/aop_key_events.csv")
aops=[('aop/152','TBBPA','AOP 152 · thyroid-hormone / neurodevelopment'),
      ('aop/314','BPA','AOP 314 · ER-alpha in immune cells / lupus'),
      ('aop/522','BPA','AOP 522 · ER antagonism / autism-like behavior'),
      ('aop/535','BPA','AOP 535 · GPER activation / memory')]
fig,axes=plt.subplots(len(aops),1,figsize=(15.5,9.0))
etypecol={'MIE':'#0072B2','KE':'#E69F00','AO':'#D55E00'}
for ax,(aid,chem_,title) in zip(axes,aops):
    kes=aopk[aopk.aop==aid]
    seq=pd.concat([kes[kes.event_type=='MIE'],kes[kes.event_type=='KE'],kes[kes.event_type=='AO']])
    n=len(seq); xs=np.linspace(0.03,0.97,n)
    ys=[0.62 if i%2==0 else 0.30 for i in range(n)]   # zig-zag to avoid overlap
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    ax.text(0.0,1.04,title,fontsize=10.5,weight='bold',va='bottom',transform=ax.transAxes)
    for x,yy,(_,r) in zip(xs,ys,seq.iterrows()):
        c=etypecol[r.event_type]
        lab=r.key_event.strip()
        lab=(lab[:20]+'…') if len(lab)>21 else lab
        ax.text(x,yy,lab,fontsize=7.0,ha='center',va='center',
                bbox=dict(boxstyle='round,pad=0.30',fc=c,ec='none',alpha=0.9),color='white')
    for i in range(n-1):
        ax.annotate('',xy=(xs[i+1],ys[i+1]),xytext=(xs[i],ys[i]),arrowprops=dict(arrowstyle='->',color='#888',lw=1.0))
# legend
from matplotlib.patches import Patch
axes[-1].legend(handles=[Patch(fc=etypecol[k],label={'MIE':'Molecular initiating event','KE':'Key event','AO':'Adverse outcome'}[k]) for k in ['MIE','KE','AO']],
                loc='lower center',bbox_to_anchor=(0.5,-0.55),ncol=3,frameon=False,fontsize=9)
fig.suptitle('Curated adverse-outcome pathways for bisphenols (AOP-Wiki)',fontsize=12,weight='bold',y=0.995)
finalize(fig,4,f"{F}/fig4_aop_chains.png")

# ============ FIG 7: mechanistic map (radial synthesis) ============
gsall=pd.read_csv(f"{D}/gene_target_summary_human.csv")
top_by_theme={}
for t,gsyms in THEMES.items():
    sub=gsall[gsall.symbol.isin(gsyms)].sort_values('n_bisphenols',ascending=False)
    mem=list(sub.symbol.head(5))
    if mem: top_by_theme[t]=mem
modules={
 'ER / estrogen':top_by_theme.get('Estrogen / ER',[]),
 'AR / steroid':top_by_theme.get('Androgen / steroid',[]),
 'Thyroid axis':top_by_theme.get('Thyroid axis',[]),
 'Metabolic / PPAR':top_by_theme.get('Metabolic / PPAR (obesogen)',[]),
 'Xenobiotic / PXR-AhR':top_by_theme.get('Xenobiotic / PXR-CAR-AhR',[]),
 'Oxidative / ER stress':top_by_theme.get('Oxidative / ER stress',[]),
 'Apoptosis / DNA damage':top_by_theme.get('Apoptosis / DNA-damage / proliferation',[]),
 'Inflammation / vascular':top_by_theme.get('Inflammation / vascular',[]),
}
outcomes={
 'ER / estrogen':['Breast cancer','Endometrial ca.'],
 'AR / steroid':['Prostate cancer'],
 'Thyroid axis':['Cognitive decline','Thyroid tumor'],
 'Metabolic / PPAR':['Obesity','NASH','T2D'],
 'Oxidative / ER stress':['Liver injury'],
 'Apoptosis / DNA damage':['Carcinogenesis'],
 'Inflammation / vascular':['Ischemia','CAD'],
}
render_mechanistic_map(
 anchor="Bisphenol\nexposome", modules=modules, drugs=outcomes,
 out_path=f"{F}/fig7_mechanistic_map.png",
 title="Bisphenol exposome → molecular targets → adverse outcomes",
 subtitle="modules = functional themes (enrichment / curation); genes = multiply-corroborated ICE targets; outer = enriched outcomes",
 anchor_kind="Chemical class", gene_legend="Target gene (ICE/ToxCast)",
 module_legend="Mechanistic module", drug_legend="Adverse outcome (AOP-Wiki / rdkg)")

# ============ FIG 8: consensus chemical x disease matrix ============
cons=pd.read_csv(f"{D}/consensus_chem_disease.csv")
piv=cons.pivot_table(index='chemical',columns='disease',values='genes_ICE_x_rdkg',aggfunc='max',fill_value=0)
dorder=['ischemia reperfusion injury','myocardial ischemia','coronary artery disease','brain ischemia',
 'non-alcoholic steatohepatitis','obesity disorder','type 2 diabetes mellitus','liver cancer',
 'breast carcinoma','prostate cancer','endometrial carcinoma','thyroid cancer','unipolar depression']
piv=piv.reindex(columns=[d for d in dorder if d in piv.columns])
corder=['BPAF','TBBPA','BPB','TBBPA-DHEE','TCBPA','BPA','3,3-diMe-BPA','BADGE','BisGMA','BPZ','BPAP','BPF','BPE','BPS','TBu-EBP']
piv=piv.reindex(index=[c for c in corder if c in piv.index])
fig,ax=plt.subplots(figsize=(10.2,6.6))
m=piv.values.astype(float); im=ax.imshow(m,cmap="PuBuGn",aspect="auto")
ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels(piv.columns,rotation=40,ha='right',fontsize=8.5)
ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index,fontsize=9)
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        if m[i,j]>0: ax.text(j,i,int(m[i,j]),ha='center',va='center',fontsize=7,color='black' if m[i,j]<m.max()*0.6 else 'white')
cb=fig.colorbar(im,ax=ax,fraction=0.028,pad=0.02); cb.set_label('shared target genes (ICE ∩ rdkg)',fontsize=9)
ax.set_xlabel('disease (enriched among bisphenol targets)',fontsize=10)
finalize(fig,8,f"{F}/fig8_consensus_matrix.png")
print("ALL FIGURES DONE")

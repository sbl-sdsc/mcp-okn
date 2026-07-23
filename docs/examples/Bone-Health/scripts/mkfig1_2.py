import json, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import sys; sys.path.insert(0,'.')
from okn_figstyle import apply_style, finalize, legend_outside, ranked_barh, panel_title
apply_style()
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','sky':'#56B4E9','yellow':'#F0E442','grey':'#666666'}

# ---------------- Figure 1: design / evidence-flow schematic ----------------
fig,ax=plt.subplots(figsize=(11.5,6.6)); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis('off')
def box(x,y,w,h,txt,fc,fs=8.5,tc='black'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.6",fc=fc,ec='#333333',lw=1.0,alpha=.92))
    ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs,color=tc,linespacing=1.35)
def arrow(x1,y1,x2,y2,label=None,rad=0.0):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=13,lw=1.3,color='#444444',
                                 connectionstyle=f"arc3,rad={rad}"))
    if label: ax.text((x1+x2)/2,(y1+y2)/2+2.2,label,ha='center',fontsize=7.4,color='#222222',style='italic')
ax.text(50,96,'Evidence flow: NASA GeneLab spaceflight omics → human bone biology',ha='center',fontsize=11.5,weight='bold')
box(2,72,26,17,'spoke-genelab (NASA GeneLab)\n14 clean Space-Flight-vs-\nGround-Control assays\nbone marrow + 5 antigravity muscles',OK['sky'])
box(2,50,26,15,'get_valid_contrasts\nRule 1 direction · Rule 2 covariate\ncomparability\n188 clean / 492 confounded',OK['yellow'])
box(2,28,26,15,'DE filter\nadj p ≤ 0.05 · |log2FC| ≥ 1\n3,157 model-organism genes',OK['yellow'])
box(2,7,26,14,'Ortholog projection\nIS_ORTHOLOG_MGiG → human Entrez\n2,686 human genes (574 dropped)',OK['yellow'])
box(37,63,26,17,'digcfdekg (CFDE REVEAL)\n26 bone traits · BMD sites,\nfracture, EHR osteoporosis\nJOIN: Entrez',OK['green'])
box(37,41,26,17,'prokn (Protein Knowledge Network)\nGO BP/MF · Reactome ·\nMSigDB regulons · curated\nMendelian bone genes',OK['green'])
box(37,19,26,17,'rdkg · oard-kg · biomarkerkg\nDrugBank therapy · HP phenotypes\n· biomarkers\nJOIN: MONDO / HP',OK['green'])
box(72,63,26,17,'Bone-trait convergence\n502 spaceflight genes with\nBMD / fracture evidence\n(Figure 6)',OK['orange'])
box(72,41,26,17,'Mechanism\nossification · ECM · RUNX2 ·\nNFAT / LEF1 / MEF2 / AP-1\n(Figures 4–5, 7)',OK['orange'])
box(72,19,26,17,'Countermeasure & biomarker\nlandscape\n169 drugs · 28 biomarkers\n(Figures 8–9)',OK['orange'])
box(37,2,61,12,'Consensus ranking — 8 evidence axes kept SEPARATE, summed to one transparent score\nTier A 41 · Tier B 196 · Tier C 2,449   (Figure 3, §9)',OK['purple'])
for y in (79,57,35,14): pass
arrow(15,72,15,65.5); arrow(15,50,15,43.5); arrow(15,28,15,21.5)
arrow(28,14,37,50,'Entrez',rad=-0.18)
arrow(28,14,37,28,'Entrez / symbol',rad=-0.1)
arrow(28,14,37,71,'Entrez',rad=-0.25)
arrow(63,71.5,72,71.5); arrow(63,49.5,72,49.5); arrow(63,27.5,72,27.5)
# (removed stray connector)
arrow(85,19,80,14,rad=0.0)
ax.text(15,92.5,'SPACEFLIGHT EVIDENCE',ha='center',fontsize=9,weight='bold',color=OK['blue'])
ax.text(50,84.5,'HUMAN BONE CONTEXT (join on shared identifiers)',ha='center',fontsize=9,weight='bold',color=OK['green'])
ax.text(85,84.5,'INTEGRATED OUTPUT',ha='center',fontsize=9,weight='bold',color=OK['red'])
finalize(fig,1,'fig/fig1_design_evidence_flow.png')

# ---------------- Figure 2: GeneLab assay landscape ----------------
vc=json.load(open('data/valid_contrasts_all.json'))
cons=pd.DataFrame(vc['contrasts'])
de=pd.read_csv('data/genelab_de_clean.csv')
fig,axes=plt.subplots(1,2,figsize=(12.2,5.4))
ax=axes[0]
cnt=pd.Series({'clean\n(vetted)':vc['clean_count'],'confounded\n(excluded)':vc['confounded_count']})
b=ax.bar(cnt.index,cnt.values,color=[OK['green'],OK['red']],width=.55)
for r,v in zip(b,cnt.values): ax.text(r.get_x()+r.get_width()/2,v+8,str(v),ha='center',fontsize=9,weight='bold')
ax.set_ylabel('Space-Flight-vs-Ground-Control assays'); ax.set_ylim(0,560)
panel_title(ax,'A','Contrast vetting (all tissues)')
ax=axes[1]
g=de.groupby(['tissue','osd']).symbol.nunique().groupby('tissue').agg(['sum'])
order=de.groupby('tissue').symbol.nunique().sort_values()
cols=[OK['orange'] if t=='bone marrow' else OK['blue'] for t in order.index]
ax.barh(order.index,order.values,color=cols)
for i,(t,v) in enumerate(order.items()): ax.text(v+25,i,str(v),va='center',fontsize=8.5)
ax.set_xlabel('distinct differentially expressed genes (adj p ≤ 0.05, |log2FC| ≥ 1)')
ax.set_xlim(0,2100)
panel_title(ax,'B','DE genes per bone-relevant tissue')
import matplotlib.patches as mp
legend_outside(ax,handles=[mp.Patch(color=OK['orange']),mp.Patch(color=OK['blue'])],
               labels=['bone marrow (osteoprogenitor / osteoclast niche)','antigravity skeletal muscle (mechanical-unloading proxy)'],
               where='below',ncol=1)
finalize(fig,2,'fig/fig2_genelab_assay_landscape.png')
print('figs 1-2 done')

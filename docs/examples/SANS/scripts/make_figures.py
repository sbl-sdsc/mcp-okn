import sys, json, textwrap
sys.path.insert(0,'/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics/scripts')
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from okn_figstyle import apply_style, legend_outside, panel_title, ranked_barh, finalize
apply_style()
D='/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics'
F=f'{D}/figures'
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','vermillion':'#D55E00',
    'purple':'#CC79A7','sky':'#56B4E9','yellow':'#F0E442','grey':'#666666'}
R=pd.read_csv(f'{D}/data/ranked_genes.csv'); M=pd.read_csv(f'{D}/data/de_master.csv')
H=pd.read_csv(f'{D}/data/human_projected_de.csv'); E=pd.read_csv(f'{D}/data/enrichment_results.csv')
T=pd.read_csv(f'{D}/data/trait_enrichment.csv'); DR=pd.read_csv(f'{D}/data/prokn_core_drugs.csv')

# ---------- FIGURE 1: study design / cohort ----------
fig,axs=plt.subplots(1,3,figsize=(13.5,4.3))
lab={'OCULAR':'Ocular','CNS':'CNS','CARDIOVASC':'Cardio-\nvascular','FLYHEAD':'Fly\nhead'}
nice={'OCULAR':'Ocular','CNS':'CNS','CARDIOVASC':'Cardiovascular','FLYHEAD':'Fly head'}
a=axs[0]
c=M.groupby('system').osd.nunique().reindex(['OCULAR','CNS','CARDIOVASC','FLYHEAD'])
cols=[OK['vermillion'],OK['blue'],OK['green'],OK['orange']]
a.bar(range(len(c)),c.values,color=cols)
a.set_xticks(range(len(c))); a.set_xticklabels([lab[i] for i in c.index],fontsize=9)
a.set_ylabel('OSDR studies'); panel_title(a,'A','Studies per organ system')
for i,v in enumerate(c.values): a.text(i,v+0.08,str(v),ha='center',fontsize=9)
a=axs[1]
g=M.groupby(['system','species']).entrez.nunique().unstack(fill_value=0).reindex(['OCULAR','CNS','CARDIOVASC','FLYHEAD'])
x=np.arange(len(g)); w=0.38
for j,(sp,col) in enumerate([('mouse',OK['blue']),('fly',OK['orange'])]):
    if sp in g: a.bar(x+(j-0.5)*w,g[sp].values,w,label=f'{sp} (Mus musculus)' if sp=='mouse' else 'fly (D. melanogaster)',color=col)
a.set_xticks(x); a.set_xticklabels([nice[i] for i in g.index],fontsize=9,rotation=20)
a.set_ylabel('DE genes (model organism)'); panel_title(a,'B','Differentially expressed genes')
legend_outside(a,where='below',ncol=2)
a=axs[2]
v=[R.hEntrez.nunique(),int((R.mouse_systems>=2).sum()),int(R.xspecies_ok.sum()),len(R[(R.mouse_systems>=2)|(R.xspecies_ok)])]
n=['All human\northologues','Mouse\n2+ systems','Cross-species\n(1:1 orthologue)','Conserved\nSANS core']
a.bar(range(4),v,color=[OK['grey'],OK['blue'],OK['orange'],OK['vermillion']])
a.set_yscale('log'); a.set_xticks(range(4)); a.set_xticklabels(n,fontsize=8)
a.set_ylabel('human genes (log scale)'); panel_title(a,'C','Conservation filter')
for i,val in enumerate(v): a.text(i,val*1.15,str(val),ha='center',fontsize=9)
finalize(fig,1,f'{F}/fig1_study_design.png')

# ---------- FIGURE 2: top ranked conserved genes ----------
top=R.head(30).copy()
top['lab']=top.humanSymbol.str.slice(0,14)
fig,axs=plt.subplots(1,2,figsize=(13.5,7.2),gridspec_kw={'width_ratios':[1.25,1]})
a=axs[0]
y=np.arange(len(top))[::-1]
cmap={'ocular':OK['vermillion'],'CNS':OK['blue'],'cardio':OK['green'],'flyhead':OK['orange']}
a.barh(y,top.score,color=[OK['vermillion'] if r.in_ocular else OK['blue'] for _,r in top.iterrows()])
a.set_yticks(y); a.set_yticklabels(top.lab,fontsize=8)
a.set_xlabel('consistency score'); panel_title(a,'A','Top 30 conserved genes')
import matplotlib.patches as mp
a.legend(handles=[mp.Patch(color=OK['vermillion'],label='detected in ocular tissue'),
                  mp.Patch(color=OK['blue'],label='not detected in ocular tissue')],
         loc='lower right',fontsize=8,frameon=True)
a=axs[1]
mat=top[['in_ocular','in_cns','in_cardio','in_flyhead']].astype(int).values
a.imshow(mat,cmap=matplotlib.colors.ListedColormap(['#f2f2f2',OK['sky']]),aspect='auto',vmin=0,vmax=1)
a.set_xticks(range(4)); a.set_xticklabels(['ocular','CNS','cardio','fly head'],fontsize=8,rotation=30)
a.set_yticks(range(len(top))); a.set_yticklabels(top.lab,fontsize=8)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if mat[i,j]: a.text(j,i,'●',ha='center',va='center',fontsize=7,color='white')
panel_title(a,'B','Tissue / system coverage')
a.set_xticks(np.arange(-.5,4,1),minor=True); a.set_yticks(np.arange(-.5,len(top),1),minor=True)
a.grid(which='minor',color='white',linewidth=1.2); a.tick_params(which='minor',length=0)
finalize(fig,2,f'{F}/fig2_ranked_genes.png')
print('fig1, fig2 done')

# ---------- FIGURE 3: GO + Reactome enrichment ----------
theme_of=lambda l:('Mitochondrial / OXPHOS' if any(k in l.lower() for k in ['atp synth','proton','mitochond','cristae','chemiosmotic','atp bio'])
   else 'Proteostasis / ER stress' if any(k in l.lower() for k in ['folding','chaperone','endoplasmic','amyloid','proteasome','ubiquitin'])
   else 'Ion transport / excitability' if any(k in l.lower() for k in ['ion ','channel','potassium','membrane potential','synap','neurotransmitter','homeostasis'])
   else 'Neural / retinal' if any(k in l.lower() for k in ['neuron','axon','melanosome','dendrit'])
   else 'Stress / hypoxia' if any(k in l.lower() for k in ['hypoxia','mechanical','camp','damage','g2/m','replicative','cdc6','orc1','gtse1'])
   else 'Other')
TC={'Mitochondrial / OXPHOS':OK['vermillion'],'Proteostasis / ER stress':OK['purple'],
    'Ion transport / excitability':OK['blue'],'Neural / retinal':OK['green'],
    'Stress / hypoxia':OK['orange'],'Other':OK['grey']}
sig=E[E.fdr<0.05].copy(); sig['theme']=sig.label.map(theme_of)
sig=sig.sort_values('p').head(26)[::-1]
fig,ax=plt.subplots(figsize=(11.5,8.6))
ranked_barh(ax,[f"{r.label[:52]}  [{r.family}{('/'+r.aspect) if isinstance(r.aspect,str) and r.aspect else ''}]" for _,r in sig.iterrows()],
            (-np.log10(sig.fdr)).values, themes=sig.theme.tolist(), theme_colors=TC,
            annots=[f"{r.fold:.1f}x  ({int(r.k)}/{int(r.K)})" for _,r in sig.iterrows()],
            xlabel='-log10 FDR')
ax.set_title('Functional enrichment of the conserved SANS core (GO + Reactome, FDR < 0.05)',fontsize=12)
import matplotlib.patches as mp
used=[t for t in ['Mitochondrial / OXPHOS','Proteostasis / ER stress','Ion transport / excitability',
                  'Neural / retinal','Stress / hypoxia','Other'] if t in set(sig.theme)]
legend_outside(ax,handles=[mp.Patch(color=TC[t],label=t) for t in used],labels=used,where='below',ncol=3,title='theme')
finalize(fig,3,f'{F}/fig3_enrichment.png')

# ---------- FIGURE 4: disease / trait linkage ----------
fig,axs=plt.subplots(1,2,figsize=(14.5,6.6),gridspec_kw={'width_ratios':[1.15,1]})
ts=T[T.fdr<0.05].sort_values('p').head(18)[::-1]
ocpat=r'(?i)optic|retin|macul|eye|visual|refract|glaucoma|ciliopath'
a=axs[0]
cols=[OK['vermillion'] if pd.Series([l]).str.contains(ocpat)[0] else
      (OK['blue'] if any(k in l.lower() for k in ['mitochond','energy','oxidative phosph']) else OK['grey']) for l in ts.trait_label]
yy=np.arange(len(ts))
a.barh(yy,-np.log10(ts.fdr),color=cols)
a.set_yticks(yy); a.set_yticklabels([textwrap.shorten(l,46,placeholder='…') for l in ts.trait_label],fontsize=8)
for i,(_,r) in enumerate(ts.iterrows()): a.text(-np.log10(r.fdr)+0.15,i,f"{r.fold:.1f}x",va='center',fontsize=7.5)
a.set_xlabel('-log10 FDR'); panel_title(a,'A','Trait gene-set enrichment (digcfdekg)')
a.legend(handles=[mp.Patch(color=OK['vermillion'],label='ocular / visual'),
                  mp.Patch(color=OK['blue'],label='mitochondrial / energy'),
                  mp.Patch(color=OK['grey'],label='other')],loc='lower right',fontsize=8)
a=axs[1]
OCD=pd.read_csv(f'{D}/data/rdkg_ocular_diseases.csv')
cnt=OCD.groupby('symbol').disease.nunique().sort_values()
a.barh(np.arange(len(cnt)),cnt.values,color=OK['green'])
a.set_yticks(np.arange(len(cnt))); a.set_yticklabels(cnt.index,fontsize=9)
a.set_xlabel('distinct ocular / neuro-ocular diseases (rdkg)')
for i,v in enumerate(cnt.values): a.text(v+0.12,i,str(v),va='center',fontsize=8)
panel_title(a,'B','Curated disease links of core genes')
finalize(fig,4,f'{F}/fig4_disease_trait.png')

# ---------- FIGURE 5: countermeasure / druggability ----------
fig,axs=plt.subplots(1,2,figsize=(14,6.2),gridspec_kw={'width_ratios':[1,1.1]})
a=axs[0]
d=DR.groupby('symbol').compound.nunique().sort_values(ascending=False).head(18)[::-1]
a.barh(np.arange(len(d)),d.values,color=OK['sky'])
a.set_yticks(np.arange(len(d))); a.set_yticklabels(d.index,fontsize=9)
a.set_xlabel('distinct modulating compounds (prokn, bioactivity layer)')
for i,v in enumerate(d.values): a.text(v+2,i,str(v),va='center',fontsize=8)
panel_title(a,'A','Druggable core targets')
a=axs[1]
tiers={'Approved drug reached via a curated\ndisease link (rdkg treats)':(9,OK['green']),
       'Investigational / clinical-stage agent\nfor the same disease axis':(4,OK['blue']),
       'Med-chem probe with measured\nbioactivity (prokn)':(40,OK['orange']),
       'Toxicogenomic perturbation only\n(spoke-okn CuG/CdG)':(7,OK['vermillion'])}
names=list(tiers)[::-1]; vals=[tiers[n][0] for n in names]; cs=[tiers[n][1] for n in names]
a.barh(np.arange(len(names)),vals,color=cs)
a.set_yticks(np.arange(len(names))); a.set_yticklabels(names,fontsize=8)
a.set_xlabel('count of targets / compounds at that evidence layer')
for i,v in enumerate(vals): a.text(v+0.5,i,str(v),va='center',fontsize=8)
panel_title(a,'B','Evidence layer of the countermeasure hits')
finalize(fig,5,f'{F}/fig5_countermeasures.png')
print('fig3, fig4, fig5 done')

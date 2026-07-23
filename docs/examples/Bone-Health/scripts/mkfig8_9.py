import pandas as pd, numpy as np, matplotlib, sys, re, json
matplotlib.use('Agg'); import matplotlib.pyplot as plt; import matplotlib.patches as mp
sys.path.insert(0,'.')
from okn_figstyle import apply_style, finalize, legend_outside, panel_title
apply_style()
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','grey':'#666666','sky':'#56B4E9'}

# ---------------- Figure 8: countermeasure / therapeutic landscape ----------------
d=pd.read_csv('data/rdkg_drugs.csv')
CLS=[('Bisphosphonate',r'alendron|risedron|zoledron|ibandron|pamidron|neridron|minodron|incadron|etidron|tiludron|bisphosphonate|fosamax|mk0217'),
     ('RANKL mAb (denosumab)',r'denosumab|prolia|jmt103|ql1206|dmab'),
     ('PTH / PTHrP analogue',r'teriparatide|parathyroid hormone|hpth|pth 1-34|parathyroid hormone-related'),
     ('Sclerostin mAb',r'romosozumab|evenity|bps804|setrusumab'),
     ('Vitamin D / analogue',r'cholecalciferol|ergocalciferol|calcitriol|calcifediol|alfacalcidol|eldecalcitol|dihydrotachysterol|vitamin d'),
     ('Calcium / mineral',r'calcium|magnesium|strontium|phylloquinone'),
     ('SERM / hormone',r'raloxifene|bazedoxifene|lasofoxifene|tibolone|estradiol|ethinylestradiol|norethisterone|norgestimate|levonorgestrel|medroxyprogesterone|progesterone|ipriflavone|tocotrienol'),
     ('Calcitonin',r'calcitonin'),
     ('Enzyme replacement / FGF23',r'asfotase|alxn|krn23|burosumab|bgj398'),
     ('Anti-TGF-beta / other biologic',r'fresolimumab|aga2115|actimmune|rituximab|ivig|mesenchymal stromal'),
     ('Glucocorticoid (bone-adverse)',r'prednis|dexamethasone|methylprednisolone|hydrocortisone|betamethasone|budesonide|triamcinolone|cortisone|desonide|ciclesonide|mometasone|fluticasone'),
     ('Proton-pump inhibitor (bone-adverse)',r'prazole'),
     ('Heparin / anticoagulant (bone-adverse)',r'heparin|parin$|dalteparin|enoxaparin|ardeparin|adomiparin|parnaparin'),
     ('Aromatase inhib. / retinoid / other adverse',r'letrozole|isotretinoin|tretinoin|elagolix|nafarelin|rosiglitazone|thyroxine|liothyronine|metformin|glimepiride|phenobarbital|phenytoin'),
    ]
def cls(n):
    n=str(n).lower()
    for k,p in CLS:
        if re.search(p,n): return k
    return 'other / unclassified'
d['class']=d.drugLabel.map(cls)
piv=d.groupby(['class','relation']).drug.nunique().unstack(fill_value=0)
for c in ['treats','contraindicated_for']:
    if c not in piv: piv[c]=0
piv=piv.loc[piv.sum(axis=1).sort_values().index]
fig,axes=plt.subplots(1,2,figsize=(14.6,7.0),gridspec_kw={'width_ratios':[1.25,1],'wspace':.42})
ax=axes[0]
y=np.arange(len(piv))
ax.barh(y-0.2,piv['treats'],height=.4,color=OK['green'],label='treats')
ax.barh(y+0.2,piv['contraindicated_for'],height=.4,color=OK['red'],label='contraindicated for')
ax.set_yticks(y); ax.set_yticklabels(piv.index)
for i,(t,c) in enumerate(zip(piv['treats'],piv['contraindicated_for'])):
    if t: ax.text(t+0.4,i-0.2,str(t),va='center',fontsize=7.6)
    if c: ax.text(c+0.4,i+0.2,str(c),va='center',fontsize=7.6)
ax.set_xlabel('distinct DrugBank agents (rdkg)'); ax.set_xlim(0,max(piv.max())*1.22)
panel_title(ax,'A','Countermeasure classes for the bone-loss disease family')
legend_outside(ax,where='below',ncol=2)
ax=axes[1]
dz=d.groupby(['diseaseLabel','relation']).drug.nunique().unstack(fill_value=0)
for c in ['treats','contraindicated_for']:
    if c not in dz: dz[c]=0
dz=dz.loc[dz.sum(axis=1).sort_values().index].tail(12)
y=np.arange(len(dz))
ax.barh(y-0.2,dz['treats'],height=.4,color=OK['green'])
ax.barh(y+0.2,dz['contraindicated_for'],height=.4,color=OK['red'])
ax.set_yticks(y); ax.set_yticklabels([str(x)[:40] for x in dz.index])
ax.set_xlabel('distinct DrugBank agents (rdkg)')
panel_title(ax,'B','Agents per disease node')
finalize(fig,8,'fig/fig8_countermeasure_landscape.png')

# ---------------- Figure 9: biomarkers + clinical phenotypes ----------------
bm=pd.read_csv('data/biomarkers.csv')
op=bm[bm.diseaseLabel=='osteoporosis'].copy()
op['kind']=np.where(op.bmLabel.astype(str).str.contains('sequence variation'),'genomic variant','biochemical / metabolite')
op['analyte']=op.bmLabel.astype(str).str.replace(r'^(Increased|Decreased) (level of metabolite )?','',regex=True).str.replace(r'/LOINC.*|\[.*\]','',regex=True).str.strip()
op['dirn']=np.where(op.bmLabel.astype(str).str.startswith('Increased'),'increased',
             np.where(op.bmLabel.astype(str).str.startswith('Decreased'),'decreased','presence'))
bio=op[op.kind=='biochemical / metabolite'].groupby(['analyte','dirn']).agg(n=('sampleLabel','nunique'),samples=('sampleLabel',lambda s:', '.join(sorted(set(str(x) for x in s if str(x)!='nan'))))).reset_index()
gen=op[op.kind=='genomic variant'].bmLabel.astype(str).str.extract(r'dbSNP:(\w+) sequence variation in gene ([A-Z0-9\-]+)')
gen.columns=['rsid','gene']; gen=gen.dropna()
ph=pd.read_csv('data/oard_phenotypes.csv') if False else None
fig,axes=plt.subplots(1,2,figsize=(14.4,6.2),gridspec_kw={'width_ratios':[1,1],'wspace':.5})
ax=axes[0]
lab=[f"{r.analyte} ({r.dirn})" for r in bio.itertuples()]
cols=[OK['red'] if r.dirn=='increased' else OK['blue'] for r in bio.itertuples()]
o=np.argsort(bio.n.values)
ax.barh([lab[i] for i in o],[bio.n.values[i] for i in o],color=[cols[i] for i in o])
for i,idx in enumerate(o): ax.text(bio.n.values[idx]+0.06,i,str(bio.samples.values[idx])[:46],va='center',fontsize=7.2)
ax.set_xlabel('distinct biospecimen types with a LOINC-coded assay'); ax.set_xlim(0,7.2)
panel_title(ax,'A','Biochemical osteoporosis biomarkers (biomarkerkg)')
legend_outside(ax,handles=[mp.Patch(color=OK['red']),mp.Patch(color=OK['blue'])],labels=['above-normal level indicates disease','below-normal level indicates disease'],where='below',ncol=1)
ax=axes[1]
g=gen.groupby('gene').rsid.nunique().sort_values()
ax.barh(g.index,g.values,color=OK['purple'])
for i,(k,v) in enumerate(g.items()):
    rs=', '.join(sorted(gen[gen.gene==k].rsid))
    ax.text(v+0.02,i,rs,va='center',fontsize=7.2)
ax.set_xlabel('risk variants (dbSNP) flagged as indicating risk of osteoporosis'); ax.set_xlim(0,2.4)
ax.set_xticks([0,1,2])
panel_title(ax,'B','Genomic osteoporosis risk biomarkers (biomarkerkg)')
finalize(fig,9,'fig/fig9_biomarkers.png')
print('figs 8-9 done')

import json, pandas as pd, numpy as np, sys, re
sys.path.insert(0,'.')
from collapse_orthologs import collapse

d=json.load(open('data/genelab_de_ortho_raw.json'))
df=pd.DataFrame(d['rows'])
df['osd']=df.assay.str.extract(r'node/(OSD-\d+)')
tis={'OSD-690':'bone marrow','OSD-101':'gastrocnemius','OSD-103':'quadriceps femoris','OSD-104':'soleus',
     'OSD-105':'tibialis anterior','OSD-326':'quadriceps femoris','OSD-419':'gastrocnemius','OSD-422':'gastrocnemius',
     'OSD-576':'tibialis anterior','OSD-665':'extensor digitorum longus','OSD-666':'quadriceps femoris',
     'OSD-770':'soleus','OSD-99':'extensor digitorum longus'}
df['tissue']=df.osd.map(tis)
df['hEntrez']=df.humanGene.str.extract(r'gene/(\d+)')
df=df.rename(columns={'adj_p':'adj_p_value'})

# collapse per-assay so each assay contributes one row per human gene
parts=[]
for a,g in df.groupby('assay'):
    c=collapse(g[['hEntrez','humanSymbol','symbol','log2fc','adj_p_value']])
    c['assay']=a; c['osd']=g.osd.iloc[0]; c['tissue']=g.tissue.iloc[0]; c['organism']=g.organism.iloc[0]
    parts.append(c)
per=pd.concat(parts,ignore_index=True)
per.to_csv('data/genelab_human_per_assay.csv',index=False)

# recurrence across assays / tissues / studies
agg=per.groupby(['hEntrez','humanSymbol']).agg(
    n_assays=('assay','nunique'), n_studies=('osd','nunique'), n_tissues=('tissue','nunique'),
    tissues=('tissue',lambda s:'; '.join(sorted(set(s)))),
    studies=('osd',lambda s:'; '.join(sorted(set(s)))),
    organisms=('organism',lambda s:'; '.join(sorted(set(s)))),
    n_up=('log2fc',lambda s:(s>0).sum()), n_down=('log2fc',lambda s:(s<0).sum()),
    max_abs_log2fc=('log2fc',lambda s: s.loc[s.abs().idxmax()]),
    min_adj_p=('adj_p_value','min'), mean_log2fc=('log2fc','mean'),
    ambiguous=('n_mouse_map',lambda s:(s>1).any())
).reset_index()

agg['consistent_direction']=np.where((agg.n_up==0)|(agg.n_down==0),'consistent','mixed')
agg['net_direction']=np.where(agg.n_up>agg.n_down,'up',np.where(agg.n_down>agg.n_up,'down','mixed'))
agg=agg.sort_values(['n_assays','n_tissues'],ascending=False)
agg.to_csv('data/genelab_human_recurrence.csv',index=False)
print('unique human orthologs:', len(agg))
print('mouse/rat genes with NO human ortholog dropped:')
raw=pd.DataFrame(json.load(open('data/genelab_de_raw.json'))['rows'])
print('  DE model-organism genes total:', raw.symbol.nunique(), '| with ortholog:', df.symbol.nunique(), '| dropped:', raw.symbol.nunique()-df.symbol.nunique())
print()
print('recurrence distribution (n_assays):'); print(agg.n_assays.value_counts().sort_index(ascending=False).to_string())
print()
print('TOP 40 by assay recurrence:')
print(agg.head(40)[['humanSymbol','n_assays','n_studies','n_tissues','n_up','n_down','net_direction','consistent_direction','max_abs_log2fc','min_adj_p','tissues']].to_string(index=False))

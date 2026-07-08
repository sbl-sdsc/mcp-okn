import json,pandas as pd,numpy as np
D="data"
st={}
st['cohort']={'OSD-690_WT_sig':3161,'OSD-690_WT_orth':3112,'OSD-690_KO_sig':3517,'OSD-690_KO_orth':3537,
  'OSD-690_WT_measured':4100,'OSD-690_KO_measured':4588,'cortbone_HLU_sig':8,'cortbone_HLU_measured':8,
  'marrow_HLU_sig':2,'WT_he':221,'KO_he':297}
m=pd.read_csv(f"{D}/wt_ko_human_merged.tsv",sep="\t")
both=m[m.log2fc_wt.notna()&m.log2fc_ko.notna()]
sd=(np.sign(both.log2fc_wt)==np.sign(both.log2fc_ko))
st['wtko']={'both':int(len(both)),'same_dir':int(sd.sum()),'same_dir_pct':round(100*sd.mean(),1),
  'wt_only':int((m.log2fc_wt.notna()&m.log2fc_ko.isna()).sum()),'ko_only':int((m.log2fc_wt.isna()&m.log2fc_ko.notna()).sum())}
st['enrich']={'digcfde_obs':492,'digcfde_exp':476.5,'digcfde_fold':1.03,'digcfde_p':0.209,
  'rdkg_obs':31,'rdkg_exp':20.6,'rdkg_fold':1.51,'rdkg_p':0.012,'rdkg_K':148,'N':21710}
sp=pd.read_csv(f"{D}/wt_he_specificity.tsv",sep="\t")
st['specificity']=sp.specificity.value_counts().to_dict()
c=pd.read_csv(f"{D}/RANKED_bone_candidates.tsv",sep="\t")
st['tiers']=c.tier.value_counts().to_dict(); st['n_candidates']=int(len(c))
json.dump(st,open(f"{D}/stats.json","w"),indent=2)
print(json.dumps(st,indent=1))

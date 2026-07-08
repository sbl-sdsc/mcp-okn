import pandas as pd, numpy as np
D="data"
wa=pd.read_csv(f'{D}/wt_human_annotated.tsv',sep='\t'); wa['hEntrez']=wa['hEntrez'].astype(str); wa['mEntrez']=wa['mEntrez'].astype(str)
ka=pd.read_csv(f"{D}/ko_human_annotated.tsv",sep="\t"); ka['hEntrez']=ka['hEntrez'].astype(str)
spec=pd.read_csv(f"{D}/wt_he_specificity.tsv",sep="\t"); spec['mEntrez']=spec['mEntrez'].astype(str)
spec_by_h = wa.merge(spec[['mEntrez','nTissues','specificity']],on='mEntrez',how='left')[['hEntrez','nTissues','specificity']].drop_duplicates('hEntrez')

# merge WT + KO on human gene
w=wa[['hEntrez','humanSymbol','symbol','log2fc','adj_p_value','digcfde_bonecat','rdkg_pheno','osteoarthritis','bone_loss_gene']].rename(columns={'log2fc':'l2fc_WT','adj_p_value':'p_WT'})
k=ka[['hEntrez','log2fc','adj_p_value']].rename(columns={'log2fc':'l2fc_KO','adj_p_value':'p_KO'})
m=w.merge(k,on='hEntrez',how='outer')
# carry symbols from KO where WT missing
ksym=ka[['hEntrez','humanSymbol','symbol','digcfde_bonecat','rdkg_pheno','osteoarthritis','bone_loss_gene']]
m=m.merge(ksym,on='hEntrez',how='left',suffixes=('','_k'))
for c in ['humanSymbol','symbol','digcfde_bonecat','rdkg_pheno']:
    m[c]=m[c].fillna(m[c+'_k'])
m['osteoarthritis']=m['osteoarthritis'].fillna(m['osteoarthritis_k']).fillna(False)
m['bone_loss_gene']=m['bone_loss_gene'].fillna(m['bone_loss_gene_k']).fillna(False)
m=m.drop(columns=[c for c in m.columns if c.endswith('_k')])
m=m.merge(spec_by_h,on='hEntrez',how='left')

# canonical bone-remodeling panel (mouse-level values; sig flags)
panel={ # hEntrez: (symbol, l2fc_WT,p_WT, l2fc_KO,p_KO, role)
 '249':('ALPL',-1.086,0.00085,-1.142,0.00179,'osteoblast/mineralization'),
 '3381':('IBSP',-0.811,0.0137,-0.649,0.0489,'bone matrix (osteoblast)'),
 '54757':('FAM20A',-2.014,0.00541,None,None,'biomineralization kinase'),
 '1277':('COL1A1',None,None,-1.347,0.0502,'type I collagen (bone matrix)'),
 '4041':('LRP5',None,None,-0.511,0.0465,'Wnt co-receptor (bone mass)'),
 '4038':('LRP4',None,None,-0.331,0.0818,'Wnt co-receptor/sclerostin'),
 '4772':('NFATC1',None,None,-0.598,0.0278,'master osteoclast TF'),
 '1435':('CSF1',None,None,-0.379,0.0485,'osteoclast differentiation (M-CSF)'),
 '4318':('MMP9',None,None,-0.672,0.0381,'osteoclast MMP'),
 '760':('CA2',-0.419,0.0297,-0.402,0.0376,'osteoclast carbonic anhydrase'),
 '2920':('CXCL2',1.901,0.00539,1.992,0.00257,'inflammatory chemokine'),
}
pan=pd.DataFrame([{'hEntrez':e,'humanSymbol':v[0],'l2fc_WT':v[1],'p_WT':v[2],'l2fc_KO':v[3],'p_KO':v[4],'bone_role':v[5]} for e,v in panel.items()])
m=m.merge(pan[['hEntrez','bone_role']],on='hEntrez',how='left')
# overlay panel values where present (mouse-level curated)
for _,r in pan.iterrows():
    idx=m.hEntrez==r.hEntrez
    if idx.any():
        for col in ['l2fc_WT','p_WT','l2fc_KO','p_KO']:
            if pd.notna(r[col]): m.loc[idx,col]=r[col]
        m.loc[idx,'humanSymbol']=r.humanSymbol
    else:
        m=pd.concat([m,pd.DataFrame([{'hEntrez':r.hEntrez,'humanSymbol':r.humanSymbol,'l2fc_WT':r.l2fc_WT,'p_WT':r.p_WT,'l2fc_KO':r.l2fc_KO,'p_KO':r.p_KO,'bone_role':r.bone_role,'bone_loss_gene':True}])],ignore_index=True)

def sig(p): return pd.notna(p) and p<=0.05
m['sig_WT']=m.p_WT.apply(sig); m['sig_KO']=m.p_KO.apply(sig)
m['n_arms']=m.sig_WT.astype(int)+m.sig_KO.astype(int)
def dirn(r):
    v=r.l2fc_WT if pd.notna(r.l2fc_WT) else r.l2fc_KO
    return '↑' if v is not None and v>0 else ('↓' if v is not None and v<0 else '')
m['direction']=m.apply(dirn,axis=1)
m['maxabs']=m[['l2fc_WT','l2fc_KO']].abs().max(axis=1)
def samedir(r):
    if sig(r.p_WT) and sig(r.p_KO): return np.sign(r.l2fc_WT)==np.sign(r.l2fc_KO)
    return None
m['both_samedir']=m.apply(samedir,axis=1)
m['nrf2_dependent']=(m.sig_KO)&(~m.sig_WT)&(m.bone_role.notna()|m.bone_loss_gene)

# bone relevance tier
def bonecat(r):
    rd=str(r.rdkg_pheno) if pd.notna(r.rdkg_pheno) else ''
    if pd.notna(r.bone_role): return 'canonical'
    if rd and rd!='nan': return 'mendelian'
    dc=str(r.digcfde_bonecat) if pd.notna(r.digcfde_bonecat) else ''
    if 'osteoporosis' in dc or 'fracture' in dc: return 'gwas_strong'
    if 'BMD' in dc: return 'gwas_bmd'
    return 'none'
m['bone_evidence']=m.apply(bonecat,axis=1)

# SCORE
def score(r):
    s=0
    if r.both_samedir==True: s+=25
    elif r.n_arms==1: s+=10
    s+= min(r.maxabs if pd.notna(r.maxabs) else 0,3)/3*20
    be={'canonical':25,'mendelian':25,'gwas_strong':15,'gwas_bmd':8,'none':0}[r.bone_evidence]
    s+=be
    if r.nrf2_dependent: s+=8
    if r.specificity in ('marrow-selective','intermediate'): s+=5
    return round(s,1)
m['priority']=m.apply(score,axis=1)

# tier
def tier(r):
    if r.both_samedir==True and r.bone_evidence in ('canonical','mendelian'): return 'A'
    if r.bone_evidence in ('canonical','mendelian','gwas_strong'): return 'B'
    if r.n_arms>=1: return 'C'
    return 'D'
m['tier']=m.apply(tier,axis=1)

# keep candidates: any bone evidence OR high-effect robust
cand=m[(m.bone_evidence!='none')|((m.maxabs>=1)&(m.both_samedir==True))].copy()
cand=cand.sort_values(['priority','maxabs'],ascending=False)
cols=['humanSymbol','symbol','hEntrez','direction','l2fc_WT','p_WT','l2fc_KO','p_KO','n_arms','both_samedir','nrf2_dependent','bone_role','bone_evidence','digcfde_bonecat','rdkg_pheno','osteoarthritis','specificity','nTissues','priority','tier']
cand=cand[cols]
cand.to_csv(f"{D}/RANKED_bone_candidates.tsv",sep="\t",index=False)
m.to_csv(f"{D}/all_genes_scored.tsv",sep="\t",index=False)
print("candidates:",len(cand)," tiers:",cand.tier.value_counts().to_dict())
print("\n=== TOP 32 RANKED BONE CANDIDATES ===")
pd.set_option('display.width',240,'display.max_columns',30)
show=cand.head(32)[['humanSymbol','direction','l2fc_WT','l2fc_KO','n_arms','nrf2_dependent','bone_role','bone_evidence','rdkg_pheno','tier','priority']]
print(show.to_string(index=False))

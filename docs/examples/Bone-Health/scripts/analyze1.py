import json, math
import pandas as pd, numpy as np
BASE="/sessions/affectionate-jolly-ramanujan/mnt/outputs/bone"
D=f"{BASE}/data"

def load(fn):
    with open(fn) as f: j=json.load(f)
    df=pd.DataFrame(j["rows"])
    for c in ["mEntrez","symbol","hEntrez","humanSymbol"]:
        if c not in df: df[c]=None
    df["log2fc"]=pd.to_numeric(df["log2fc"])
    df["adj_p_value"]=pd.to_numeric(df["adj_p_value"])
    return df

wt=load(f"{D}/wt_full_raw.json"); ko=load(f"{D}/ko_full_raw.json")
print("RAW rows  WT",len(wt),"KO",len(ko))
print("distinct mouse genes  WT",wt.mEntrez.nunique(),"KO",ko.mEntrez.nunique())

def human_collapse(df):
    # keep only ortholog-mapped rows; collapse to human Entrez by MAX |log2fc| (carry sign), rule=max
    h=df[df.hEntrez.notna() & (df.hEntrez!="")].copy()
    h["absl"]=h.log2fc.abs()
    # per (hEntrez) pick row with max |log2fc|
    idx=h.groupby("hEntrez")["absl"].idxmax()
    top=h.loc[idx].copy()
    # ambiguity: how many distinct mouse genes map to this human gene (within sig set)
    nmouse=h.groupby("hEntrez")["mEntrez"].nunique().rename("n_mouse_map")
    top=top.merge(nmouse,on="hEntrez")
    # also mean-rule log2fc for sensitivity
    meanl=h.groupby("hEntrez")["log2fc"].mean().rename("log2fc_mean")
    top=top.merge(meanl,on="hEntrez")
    return top[["hEntrez","humanSymbol","symbol","mEntrez","log2fc","log2fc_mean","adj_p_value","n_mouse_map"]]

wh=human_collapse(wt); kh=human_collapse(ko)
print("human orthologs (sig, collapsed)  WT",len(wh),"KO",len(kh))
# mouse genes with NO human ortholog
print("mouse-only (no ortholog) sig genes WT",wt[wt.hEntrez.isna()|(wt.hEntrez=='')].mEntrez.nunique(),
      "KO",ko[ko.hEntrez.isna()|(ko.hEntrez=='')].mEntrez.nunique())

# high-effect subsets
whe=wh[wh.log2fc.abs()>=1]; khe=kh[kh.log2fc.abs()>=1]
print("high-effect |log2fc|>=1 human  WT",len(whe),"KO",len(khe))

# WT/KO merge on human gene
m=wh.merge(kh,on="hEntrez",suffixes=("_wt","_ko"),how="outer")
m["sig_wt"]=m.log2fc_wt.notna(); m["sig_ko"]=m.log2fc_ko.notna()
both=m[m.sig_wt&m.sig_ko].copy()
both["same_dir"]=np.sign(both.log2fc_wt)==np.sign(both.log2fc_ko)
print("\n=== WT vs Nrf2KO (human orthologs, adj_p<=0.05) ===")
print("WT sig",m.sig_wt.sum(),"| KO sig",m.sig_ko.sum(),"| BOTH",len(both),
      "| same-direction",int(both.same_dir.sum()),f"({100*both.same_dir.mean():.1f}%)")
print("WT-only",int((m.sig_wt&~m.sig_ko).sum()),"| KO-only",int((~m.sig_wt&m.sig_ko).sum()))

# robust core = significant in both, same direction, and high effect in at least one
robust=both[both.same_dir & ((both.log2fc_wt.abs()>=1)|(both.log2fc_ko.abs()>=1))].copy()
robust["meanabs"]=robust[["log2fc_wt","log2fc_ko"]].abs().mean(axis=1)
print("robust core (both, same-dir, |l2fc|>=1 in >=1 arm):",len(robust))

# save
wh.to_csv(f"{D}/wt_human_sig.tsv",sep="\t",index=False)
kh.to_csv(f"{D}/ko_human_sig.tsv",sep="\t",index=False)
m.to_csv(f"{D}/wt_ko_human_merged.tsv",sep="\t",index=False)
wt.to_csv(f"{D}/wt_mouse_sig.tsv",sep="\t",index=False)
ko.to_csv(f"{D}/ko_mouse_sig.tsv",sep="\t",index=False)
# human Entrez lists for federation VALUES
open(f"{D}/wt_human_entrez.txt","w").write("\n".join(sorted(wh.hEntrez.unique(),key=int)))
open(f"{D}/whe_human_entrez.txt","w").write("\n".join(sorted(whe.hEntrez.unique(),key=int)))
print("\nsaved tables. WT high-effect human genes:",sorted(whe.humanSymbol.dropna().unique().tolist())[:0] or len(whe))

import json, pandas as pd, numpy as np
from scipy.stats import hypergeom
D="data"
def loadj(fn):
    return pd.DataFrame(json.load(open(fn))["rows"])

wh=pd.read_csv(f"{D}/wt_human_sig.tsv",sep="\t"); wh['hEntrez']=wh['hEntrez'].astype(str)
kh=pd.read_csv(f"{D}/ko_human_sig.tsv",sep="\t"); kh['hEntrez']=kh['hEntrez'].astype(str)

# digcfde background + bone cats
bg=loadj(f"{D}/digcfde_allgenes_raw.json"); bg['geneEntrez']=bg['geneEntrez'].astype(str)
BG=set(bg.geneEntrez); print("digcfde background genes:",len(BG))
gc=pd.read_csv(f"{D}/digcfde_gene_bonecats.tsv",sep="\t"); gc['geneEntrez']=gc['geneEntrez'].astype(str)
boneloss=set(gc.geneEntrez); print("digcfde bone-LOSS universe:",len(boneloss))
g2cat=dict(zip(gc.geneEntrez,gc.digcfde_bonecats))

# rdkg curated HPO sets
rd={
 'Osteoporosis':"6095,8294,1024,6934,8567,6942,775,7453,7750,90416,8314,2623,84842,55148,56896,51132,4858,4123,6045,6874,57466,3720,54828,51399,374879,56098,4849,80155,10087,6578,9051,7046,10492,10075,8936,83475,92255,9757,7701,84065,9969,9442,80267,7390,86,84148,9739,9320,7074,84628,8452,8364,9130,3183,23291,283209,1182,1742,22859,26523,10847,26115,254065,2783,1457,164,1795,55593,23030,23162,22854,26040,26038,3064,116115,3248,10594,860,10079,55811,55252,7048,284361,55621,5515,63035,490,51692,54517,4076,51412,57178,55904,374969,5881,6711,4897,64398,23001,2893,253738,26057,10716,27161,23112,5718,10771,1656,1984,25930,1974".split(","),
 'Osteopenia':"5718,86,56098,374879,51399,51412,5515,54828,3720,63035,5881,4076,23314,79797,90416,4693,51692,6874,55593,55148,374969,55621,6711,4858,490,4897,6095,6934,64398,56896,55904,51132,2628,1499,7701,9320,8364,83475,92255,9969,80267,4041,7074,84628,84842,6942,7750,2623,84148,8567,9442,775,23554,80155,8452,8322,9130,8294,84065,7390,7453,8936,9757,8314,9739,9414,9742,6554,6578,570,10492,729238,51124,1024,2052,26160,10144,23250,653509,7015,6440,79991,7012,1656,81555,91039,1832,5073,10079,6569,137682,51750,10594,727897,57466,10075,10056,860,3248,1962,3190,55811,10087,26040,22859,2783,10847,22854,1457,283209,116115,23291,284361,25930,2893,10771,253738,54517,57178,4849,6045,4123,23030,23001,1795,1182,1742,26523,26115,27161,254065,164,3183,26038,3064,1974,23112,1984,23162,26057,10716".split(","),
 'Reduced_BMD':"10056,56172,79797,4041,4693,23554,1499,8322".split(","),
 'Fracture':"2628,6569,137682,249,860,23554,4041,1962,8322,79797,4952,4693,1499,2623,81555,51124,7390".split(","),
}
rd_union=set().union(*[set(v) for v in rd.values()])
print("rdkg bone-loss union:",len(rd_union))
# spoke-okn osteoarthritis genes
oa=set("57153,7124,7040,7039,6662,654,65059,650,64116,632,57605,5743,7884,5530,55245,55206,55083,55024,54460,51390,5017,4322,4314,8738,9910,9508,9507,93986,92822,91574,9129,9101,8854,8814,4312,8600,860,85019,84552,84444,8347,8202,8200,816,80274,1301,23245,221955,2202,1800,1780,176,169792,152877,1401,1311,1302,23248,1300,1280,11280,11096,11052,11014,10795,10216,10198,10180,29969,4137,406,4052,387893,3576,3569,3553,3552,3115,3113,10165,29945,2983,29785,286046,2765,26354,25987,23355,23293,23263".split(","))

def annotate(df):
    df=df.copy()
    df['digcfde_bonecat']=df.hEntrez.map(g2cat).fillna("")
    df['rdkg_pheno']=df.hEntrez.apply(lambda e:'|'.join([k for k,v in rd.items() if e in set(v)]))
    df['osteoarthritis']=df.hEntrez.isin(oa)
    df['bone_loss_gene']=df.hEntrez.isin(boneloss)|df.hEntrez.isin(rd_union)
    df['in_digcfde_bg']=df.hEntrez.isin(BG)
    return df
wa=annotate(wh); ka=annotate(kh)

# ENRICHMENT (WT signature within digcfde universe)
N=len(BG); K=len(boneloss & BG)
sig_in_bg=set(wa[wa.in_digcfde_bg].hEntrez); n=len(sig_in_bg)
k=len(sig_in_bg & (boneloss & BG))
exp=n*K/N; fold=k/exp; p=hypergeom.sf(k-1,N,K,n)
print(f"\n=== ENRICHMENT: WT flight signature vs digcfde bone-LOSS universe ===")
print(f"N(background digcfde)={N}  K(bone-loss)={K}  n(signature in bg)={n}  k(overlap)={k}")
print(f"expected={exp:.1f}  fold={fold:.2f}x  hypergeom p={p:.2e}")

# enrichment vs rdkg curated osteoporosis (Mendelian, specific) with same background
Kr=len(rd_union & BG); kr=len(sig_in_bg & (rd_union & BG)); expr=n*Kr/N
pr=hypergeom.sf(kr-1,N,Kr,n)
print(f"\nvs rdkg curated bone-loss (Mendelian): K={Kr} overlap={kr} expected={expr:.1f} fold={kr/expr:.2f}x p={pr:.2e}")

# save annotated
wa.to_csv(f"{D}/wt_human_annotated.tsv",sep="\t",index=False)
ka.to_csv(f"{D}/ko_human_annotated.tsv",sep="\t",index=False)

# high-effect bone-loss candidates
whe=wa[(wa.log2fc.abs()>=1)&wa.bone_loss_gene].sort_values('log2fc',key=abs,ascending=False)
print(f"\nHigh-effect WT signature genes that are BONE-LOSS genes: {len(whe)}")
print(whe[['humanSymbol','symbol','log2fc','adj_p_value','digcfde_bonecat','rdkg_pheno']].head(30).to_string(index=False))

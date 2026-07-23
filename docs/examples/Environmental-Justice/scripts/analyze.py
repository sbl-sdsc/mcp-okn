#!/usr/bin/env python3
"""Environmental Justice consensus analysis — integrate independent OKN axes on county FIPS."""
import pandas as pd, numpy as np, json, io, os
D="/sessions/keen-charming-hypatia/mnt/Environmental-Justice/data"

def rd(f):
    return pd.read_csv(os.path.join(D,f),dtype={'fips':str})

# ---- sawgraph PFAS (regional; embedded fips:n_pfas_obs) ----
saw="""01001:1,01007:1,01021:2,01025:1,01033:3,01047:2,01051:2,01057:1,01063:1,01065:3,01073:2,01075:3,01079:3,01083:4,01087:3,01089:9,01107:4,01115:2,01121:1,01125:3,04001:2,04003:3,04005:34,04007:7,04009:4,04011:4,04012:1,04013:46,04015:5,04017:3,04019:22,04021:1,04023:1,04025:26,04027:14,05011:1,05017:1,05023:1,05047:1,05077:2,05101:4,05111:1,05119:1,05135:1,05143:1,05149:1,17003:1,17011:1,17017:1,17027:1,17031:22,17059:1,17063:2,17075:1,17083:1,17089:3,17091:5,17095:1,17097:5,17099:5,17111:9,17125:1,17127:1,17143:1,17153:1,17157:1,17195:1,17197:3,17201:1,18001:3,18003:8,18005:3,18009:6,18011:1,18015:2,18017:8,18023:2,18027:1,18029:2,18031:1,18033:5,18035:4,18037:2,18039:12,18045:1,18047:2,18049:1,18051:1,18053:1,18055:1,18057:6,18061:1,18063:2,18065:1,18067:6,18069:5,18071:2,18073:5,18077:1,18079:2,18081:4,18083:1,18085:6,18087:5,18089:20,18091:8,18093:10,18095:3,18097:14,18099:1,18101:5,18103:3,18105:9,18107:7,18109:4,18111:6,18113:7,18117:2,18119:2,18121:4,18125:2,18127:13,18129:1,18133:2,18135:4,18137:1,18141:7,18143:1,18145:5,18147:1,18149:1,18151:5,18153:5,18157:8,18161:1,18165:2,18167:7,18169:8,18171:1,18175:1,18177:9,18179:2,18181:2,18183:3,20027:1,20055:1,20067:1,20069:2,20097:1,20111:1,20129:1,20141:1,20155:1,20171:1,20173:4,20191:1,20199:1,20203:1,23001:1135,23003:15241,23005:2888,23007:4001,23009:5443,23011:2205,23013:2665,23015:1594,23017:5101,23019:8067,23021:10014,23023:825,23025:9385,23027:1949,23029:7477,23031:3080,25001:5,25003:5,25005:10,25009:12,25011:7,25013:15,25015:6,25017:23,25021:4,25023:33,25027:21,27001:2,27003:32,27005:1,27007:15,27009:1,27011:1,27013:2,27017:18,27019:5,27021:10,27025:5,27027:2,27029:2,27031:41,27033:1,27035:42,27037:18,27041:1,27043:1,27045:3,27049:1,27051:1,27053:51,27057:8,27059:2,27061:11,27063:1,27065:1,27067:1,27069:3,27071:2,27075:16,27077:1,27083:1,27085:3,27091:1,27093:1,27095:5,27097:6,27099:4,27107:2,27109:5,27111:3,27115:8,27117:3,27119:2,27123:29,27125:1,27127:1,27129:1,27131:2,27137:52,27139:4,27141:4,27145:15,27149:1,27151:2,27153:2,27159:3,27163:166,27167:1,27169:1,27171:3,33003:2,33007:3,33011:2,33013:5,33015:4,45013:1,45019:3,45041:1,45043:2,45051:1,45055:2,45091:1,50007:1,50023:1,50027:3,55079:1"""
saw_d={p.split(':')[0]:int(p.split(':')[1]) for p in saw.split(',')}
saw_df=pd.DataFrame([{'fips':k,'n_pfas_obs':v} for k,v in saw_d.items()])

# ---- load axes ----
dim=rd("county_dim.csv")[['fips','label','stateName']]
chem=rd("chem_foundin.csv")[['fips','n_chem']]
chr_=rd("chr_wide.csv")
fac=rd("fac_total.csv")[['fips','n_fac']]
pfas=rd("fac_pfas.csv")[['fips','n_pfas_fac']]
scal=rd("scales_cases.csv")[['fips','n_case']]
dis=rd("disease_county.csv")
prov=rd("ruralkg_providers.csv")[['fips','n_prov']]

m=dim.copy()
for df in [chem,fac,pfas,scal,prov,saw_df,dis,chr_]:
    m=m.merge(df,on='fips',how='left')
m['state_fips']=m['fips'].str[:2]
# restrict to 50 states + DC (drop territories 60/66/69/72/74/78)
m=m[pd.to_numeric(m['state_fips'])<=56].reset_index(drop=True)
print("master counties:",len(m))

# fill service counts (absence = 0 known facilities)
m['n_prov']=m['n_prov'].fillna(0)
m['n_pfas_obs_cov']=m['n_pfas_obs'].notna()   # coverage flag
# ---- indicator registry: (col, evidence_type, source_kg, geo, direction[+1 worse-high]) ----
REG={
 'n_fac':('facility inventory','fiokg (EPA FRS)','county',+1),
 'n_pfas_fac':('facility inventory','fiokg (EPA FRS)','county',+1),
 'n_chem':('measured contamination','spoke-okn','county',+1),
 'n_pfas_obs':('measured contamination','sawgraph','county(S2)',+1),
 'n_case':('justice-system activity','scales','county',+1),
 'air pollution - particulate matter':('modeled exposure','spoke-okn/CHR','county',+1),
 'drinking water violations':('regulatory indicator','spoke-okn/CHR','county',+1),
 'Overall(Socioeconomic Status,Household Characteristics,Racial & Ethnic Minority Status,Housing Type & Transportation)':('social determinant','spoke-okn/CHR (CDC SVI)','county',+1),
 'children in poverty':('social determinant','spoke-okn/CHR','county',+1),
 'income inequality':('social determinant','spoke-okn/CHR','county',+1),
 'unemployment':('social determinant','spoke-okn/CHR','county',+1),
 'severe housing cost burden':('social determinant','spoke-okn/CHR','county',+1),
 'food insecurity':('social determinant','spoke-okn/CHR','county',+1),
 'uninsured':('healthcare access','spoke-okn/CHR','county',+1),
 'firearm fatalities':('public safety','spoke-okn/CHR','county',+1),
 'homicides':('public safety','spoke-okn/CHR','county',+1),
 'drug overdose deaths':('public safety','spoke-okn/CHR','county',+1),
 'motor vehicle crash deaths':('public safety','spoke-okn/CHR','county',+1),
 'premature death':('health outcome','spoke-okn/CHR','county',+1),
 'poor or fair health':('health outcome','spoke-okn/CHR','county',+1),
 'frequent mental distress':('health outcome','spoke-okn/CHR','county',+1),
 'low birthweight':('health outcome','spoke-okn/CHR','county',+1),
 'prev_asthma':('health outcome','spoke-okn (CDC PLACES)','county(place-rollup)',+1),
 'prev_chronic_obstructive_pulmonary_disease':('health outcome','spoke-okn (CDC PLACES)','county(place-rollup)',+1),
 'prev_coronary_artery_disease':('health outcome','spoke-okn (CDC PLACES)','county(place-rollup)',+1),
 'prev_diabetes_mellitus':('health outcome','spoke-okn (CDC PLACES)','county(place-rollup)',+1),
 'prev_cerebrovascular_disease':('health outcome','spoke-okn (CDC PLACES)','county(place-rollup)',+1),
 'primary care physicians':('healthcare access','spoke-okn/CHR','county',+1),  # pop per provider, higher worse
 'mental health providers':('healthcare access','spoke-okn/CHR','county',+1),
 'preventable hospital stays':('healthcare access','spoke-okn/CHR','county',+1),
 'n_prov':('service availability','ruralkg (SAMHSA)','county',-1),  # more providers better
}
def z(s):
    s=pd.to_numeric(s,errors='coerce'); mu=s.mean(); sd=s.std(ddof=0)
    return (s-mu)/sd if sd and sd>0 else s*0

# direction-adjusted z (higher = more burden)
Z=pd.DataFrame({'fips':m['fips']})
for c,(et,src,geo,d) in REG.items():
    if c in m.columns:
        Z[c]=z(m[c])*d

# ---- domains ----
DOM={
 'D1_pollution_sources':['n_fac','n_pfas_fac'],
 'D2_chemical_exposure':['n_chem','n_pfas_obs'],
 'D3_ambient_quality':['air pollution - particulate matter','drinking water violations'],
 'D4_socioeconomic':['Overall(Socioeconomic Status,Household Characteristics,Racial & Ethnic Minority Status,Housing Type & Transportation)','children in poverty','income inequality','unemployment','severe housing cost burden','food insecurity','uninsured'],
 'D5_public_safety':['firearm fatalities','homicides','drug overdose deaths','motor vehicle crash deaths'],
 'D6_health_outcomes':['premature death','poor or fair health','frequent mental distress','low birthweight','prev_asthma','prev_chronic_obstructive_pulmonary_disease','prev_coronary_artery_disease','prev_diabetes_mellitus','prev_cerebrovascular_disease'],
 'D7_service_scarcity':['primary care physicians','mental health providers','preventable hospital stays','n_prov'],
}
dom_idx=pd.DataFrame({'fips':m['fips']})
for dom,cols in DOM.items():
    cc=[c for c in cols if c in Z.columns]
    dom_idx[dom]=Z[cc].mean(axis=1,skipna=True)   # mean of available z (already direction-adj)
# domain high-burden flag = top quintile (>=80th pct) among counties with a value
flags=pd.DataFrame({'fips':m['fips']})
for dom in DOM:
    v=dom_idx[dom]; thr=v.quantile(0.80)
    flags[dom]=(v>=thr).astype('float'); flags.loc[v.isna(),dom]=np.nan
burden_doms=['D1_pollution_sources','D2_chemical_exposure','D3_ambient_quality','D4_socioeconomic','D5_public_safety','D6_health_outcomes']
flags['consensus']=flags[burden_doms].sum(axis=1,min_count=1)   # 0-6 independent burden domains
flags['service_scarce']=flags['D7_service_scarcity']
# coverage: how many burden domains had data
flags['domains_with_data']=dom_idx[burden_doms].notna().sum(axis=1)

# tiers
def tier(x):
    if pd.isna(x): return 'NA'
    if x>=5: return 'A (very high)'
    if x>=3: return 'B (high)'
    if x>=1: return 'C (moderate)'
    return 'D (low)'
flags['tier']=flags['consensus'].map(tier)

# ---- environmental & social sub-scores + mismatch ----
env_doms=['D1_pollution_sources','D2_chemical_exposure','D3_ambient_quality']
soc_doms=['D4_socioeconomic','D5_public_safety','D6_health_outcomes']
flags['env_burden']=flags[env_doms].sum(axis=1,min_count=1)
flags['soc_burden']=flags[soc_doms].sum(axis=1,min_count=1)
# continuous burden index (mean of burden-domain z) and service capacity
m2=m.merge(dom_idx,on='fips').merge(flags[['fips','consensus','env_burden','soc_burden','service_scarce','tier','domains_with_data']],on='fips')
m2['burden_index']=dom_idx[burden_doms].mean(axis=1,skipna=True)
m2['service_capacity']=-dom_idx['D7_service_scarcity']   # higher = better access
# mismatch: high burden minus service capacity (both z); high = burdened + underserved
m2['mismatch_index']=m2['burden_index']-z(m2['service_capacity'])

# ---- save master ----
keep_ind=[c for c in REG if c in m2.columns]
out=m2[['fips','label','stateName']+keep_ind+list(dom_idx.columns[1:])+['burden_index','consensus','env_burden','soc_burden','service_scarce','service_capacity','mismatch_index','domains_with_data','tier']]
out.to_csv(os.path.join(D,"master_county.csv"),index=False)

# ---- evidence-long (preserve each evidence type separately) ----
rows=[]
for _,r in m.iterrows():
    for c,(et,src,geo,d) in REG.items():
        if c in m.columns and pd.notna(r[c]):
            rows.append({'fips':r['fips'],'county':r['label'],'state':r['stateName'],
                         'indicator':c,'value':r[c],'evidence_type':et,'source_kg':src,
                         'geo_level':geo,'direction':'higher=more burden' if d>0 else 'higher=more service'})
ev=pd.DataFrame(rows); ev.to_csv(os.path.join(D,"evidence_long.csv"),index=False)
print("evidence_long rows:",len(ev))

# ---- rankings ----
rank=m2.sort_values(['consensus','burden_index'],ascending=False)
rank_top=rank.head(40)[['fips','label','stateName','consensus','tier','env_burden','soc_burden','service_scarce','burden_index','mismatch_index']]
rank_top.to_csv(os.path.join(D,"top_burden_counties.csv"),index=False)
mism=m2[(m2['consensus']>=4)].sort_values('mismatch_index',ascending=False).head(40)
mism[['fips','label','stateName','consensus','burden_index','service_capacity','mismatch_index','n_prov','primary care physicians','mental health providers']].to_csv(os.path.join(D,"top_mismatch_counties.csv"),index=False)

# ---- correlations among domain indices + key indicators ----
cor_cols=burden_doms+['D7_service_scarcity']
cm=dom_idx[cor_cols].corr(method='spearman').round(3)
cm.to_csv(os.path.join(D,"domain_correlations.csv"))

# key-indicator spearman correlation matrix
ki=['air pollution - particulate matter','n_fac','n_pfas_fac','n_chem',
    'Overall(Socioeconomic Status,Household Characteristics,Racial & Ethnic Minority Status,Housing Type & Transportation)',
    'children in poverty','uninsured','firearm fatalities','drug overdose deaths',
    'premature death','poor or fair health','prev_asthma','prev_diabetes_mellitus',
    'primary care physicians','mental health providers','n_prov']
ki=[k for k in ki if k in m.columns]
kim=m[ki].apply(pd.to_numeric,errors='coerce').corr(method='spearman').round(3)
kim.to_csv(os.path.join(D,"indicator_correlations.csv"))

# ---- summary stats ----
dist=flags['consensus'].value_counts(dropna=False).sort_index()
tierc=flags['tier'].value_counts()
summ={
 'n_counties':int(len(m)),
 'consensus_distribution':{str(k):int(v) for k,v in dist.items()},
 'tier_counts':{k:int(v) for k,v in tierc.items()},
 'domain_coverage':{d:int(dom_idx[d].notna().sum()) for d in DOM},
 'sawgraph_counties':int(m['n_pfas_obs'].notna().sum()),
 'total_facilities':int(m['n_fac'].sum()),
 'total_pfas_facilities':int(m['n_pfas_fac'].sum()),
}
json.dump(summ,open(os.path.join(D,"summary.json"),"w"),indent=2)

print("\n=== consensus distribution (0-6 burden domains) ===")
print(dist.to_string())
print("\n=== tiers ===")
print(tierc.to_string())
print("\n=== TOP 20 cumulative-burden counties ===")
print(rank.head(20)[['fips','label','stateName','consensus','env_burden','soc_burden','service_scarce','burden_index']].to_string(index=False))
print("\n=== TOP 15 burden<->service MISMATCH (consensus>=4) ===")
print(mism.head(15)[['label','stateName','consensus','burden_index','service_capacity','mismatch_index']].to_string(index=False))
print("\n=== domain correlations (spearman) ===")
print(cm.to_string())

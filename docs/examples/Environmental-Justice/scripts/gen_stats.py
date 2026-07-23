#!/usr/bin/env python3
import pandas as pd, numpy as np, json
D="/sessions/keen-charming-hypatia/mnt/Environmental-Justice/data"
m=pd.read_csv(f"{D}/master_county.csv",dtype={'fips':str})
cm=pd.read_csv(f"{D}/domain_correlations.csv",index_col=0)
st=pd.read_csv(f"{D}/state_rollup.csv")

def tiern(p): return int(m['tier'].str.startswith(p).sum())
dist={int(k):int(v) for k,v in m['consensus'].value_counts().items()}
S={}
S['n_counties']=len(m)
S['n_states']=m['fips'].str[:2].nunique()
S['n_domains']=6
S['n_indicators']=int(sum(c in m.columns for c in ['n_fac','n_pfas_fac','n_chem','n_pfas_obs','air pollution - particulate matter','drinking water violations','Overall(Socioeconomic Status,Household Characteristics,Racial & Ethnic Minority Status,Housing Type & Transportation)','children in poverty','income inequality','unemployment','severe housing cost burden','food insecurity','uninsured','firearm fatalities','homicides','drug overdose deaths','motor vehicle crash deaths','premature death','poor or fair health','frequent mental distress','low birthweight','prev_asthma','prev_chronic_obstructive_pulmonary_disease','prev_coronary_artery_disease','prev_diabetes_mellitus','prev_cerebrovascular_disease','primary care physicians','mental health providers','preventable hospital stays','n_prov','n_case']))
S['tierA']=tiern('A'); S['tierB']=tiern('B'); S['tierC']=tiern('C'); S['tierD']=tiern('D')
S['n_high']=S['tierA']+S['tierB']
S['pct_high']=round(100*S['n_high']/len(m),1)
S['cons6']=dist.get(6,0); S['cons5']=dist.get(5,0); S['cons4']=dist.get(4,0)
S['n_double']=int(((m['env_burden']>=2)&(m['soc_burden']>=2)).sum())
S['total_facilities']=int(m['n_fac'].sum())
S['total_pfas_facilities']=int(m['n_pfas_fac'].sum())
S['total_fed_cases']=int(m['n_case'].sum())
S['sawgraph_counties']=int(m['n_pfas_obs'].notna().sum())
S['ruralkg_providers']=int(m['n_prov'].sum())
# correlations
S['corr_soc_health']=float(cm.loc['D4_socioeconomic','D6_health_outcomes'])
S['corr_pub_health']=float(cm.loc['D5_public_safety','D6_health_outcomes'])
S['corr_poll_pub']=float(cm.loc['D1_pollution_sources','D5_public_safety'])
S['corr_poll_serv']=float(cm.loc['D1_pollution_sources','D7_service_scarcity'])
S['corr_health_serv']=float(cm.loc['D6_health_outcomes','D7_service_scarcity'])
S['corr_poll_chem']=float(cm.loc['D1_pollution_sources','D2_chemical_exposure'])
# top entities
top=m.sort_values(['consensus','burden_index'],ascending=False)
S['top1']=f"{top.iloc[0]['label']}, {top.iloc[0]['stateName']}"
S['top2']=f"{top.iloc[1]['label']}, {top.iloc[1]['stateName']}"
mis=m[m['consensus']>=4].sort_values('mismatch_index',ascending=False)
S['mis1']=f"{mis.iloc[0]['label']}, {mis.iloc[0]['stateName']}"
S['mis2']=f"{mis.iloc[1]['label']}, {mis.iloc[1]['stateName']}"
S['mis3']=f"{mis.iloc[2]['label']}, {mis.iloc[2]['stateName']}"
# state pattern
la=st[st.stateName=='Louisiana'].iloc[0]; ms=st[st.stateName=='Mississippi'].iloc[0]
S['la_mean']=round(float(la['mean_consensus']),2); S['la_high']=int(la['n_high']); S['la_n']=int(la['n'])
S['ms_high']=int(ms['n_high']); S['ms_n']=int(ms['n'])
S['pfos_endpoints']=1510; S['pfoa_endpoints']=1396; S['n_pfas_toxcast']=32
S['saw_top']="Aroostook County, Maine"; S['saw_top_n']=15241
json.dump(S,open(f"{D}/stats.json","w"),indent=2)

# ---- results-table rows (for interactive HTML table) ----
SRC={'n_fac':'fiokg','n_pfas_fac':'fiokg','n_chem':'spoke-okn','n_pfas_obs':'sawgraph','air pollution - particulate matter':'spoke-okn','n_case':'scales','n_prov':'ruralkg'}
def sources_for(r):
    s=set(['spoke-okn','spatialkg'])  # CHR/SVI + geo backbone always
    if pd.notna(r['n_fac']) and r['n_fac']>0: s.add('fiokg')
    if pd.notna(r['n_case']) and r['n_case']>0: s.add('scales')
    if pd.notna(r['n_prov']) and r['n_prov']>0: s.add('ruralkg')
    if pd.notna(r['n_pfas_obs']): s.add('sawgraph')
    return sorted(s)
rows=[]
for _,r in top.iterrows():
    src=sources_for(r)
    rows.append({
      'FIPS':r['fips'],'County':r['label'],'State':r['stateName'],
      'Tier':r['tier'].split(' ')[0],'Consensus':int(r['consensus']) if pd.notna(r['consensus']) else 0,
      'Env domains':int(r['env_burden']) if pd.notna(r['env_burden']) else 0,
      'Social domains':int(r['soc_burden']) if pd.notna(r['soc_burden']) else 0,
      'Service scarce':'yes' if r['service_scarce']==1 else ('no' if pd.notna(r['service_scarce']) else 'n/a'),
      'Burden index':round(float(r['burden_index']),3) if pd.notna(r['burden_index']) else None,
      'Mismatch':round(float(r['mismatch_index']),3) if pd.notna(r['mismatch_index']) else None,
      'Facilities':int(r['n_fac']) if pd.notna(r['n_fac']) else None,
      'PFAS facilities':int(r['n_pfas_fac']) if pd.notna(r['n_pfas_fac']) else None,
      'sources_list':src,'sources_n':len(src),
    })
json.dump(rows,open(f"{D}/table_rows.json","w"))
print("stats + %d table rows written"%len(rows))
print(json.dumps(S,indent=1))

#!/usr/bin/env python3
"""Assemble Proto-OKN county-level cumulative environmental-justice burden dataset,
compute burden scores/ranking and ecological correlations, and emit deliverable CSVs.
All DATA is sourced exclusively from Proto-OKN knowledge graphs (extracted via SPARQL)."""
import os, json, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings("ignore")

D = "/sessions/amazing-focused-bardeen/mnt/outputs/data"
OUT = "/sessions/amazing-focused-bardeen/mnt/outputs"
def p(f): return os.path.join(D, f)

STATE = {'01':'AL','02':'AK','04':'AZ','05':'AR','06':'CA','08':'CO','09':'CT','10':'DE',
'11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN','19':'IA','20':'KS',
'21':'KY','22':'LA','23':'ME','24':'MD','25':'MA','26':'MI','27':'MN','28':'MS','29':'MO',
'30':'MT','31':'NE','32':'NV','33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND',
'39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN','48':'TX',
'49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI','56':'WY','72':'PR'}

def clean_fips(s):
    s = str(s).strip()
    s = ''.join(ch for ch in s if ch.isdigit())
    if s == '' : return None
    s = s.zfill(5)[-5:]
    return s

def load2(fn, val, dtype=float):
    df = pd.read_csv(p(fn), dtype=str)
    df.columns = ['fips', val]
    df['fips'] = df['fips'].map(clean_fips)
    df = df.dropna(subset=['fips'])
    df[val] = pd.to_numeric(df[val], errors='coerce')
    df = df[~df['fips'].str.endswith('000')]           # drop state aggregates
    df = df.groupby('fips', as_index=False)[val].mean()
    return df

# ---------- load layers ----------
fac  = load2('fiokg_facilities.csv','epa_fac')
pfac = load2('fiokg_pfas.csv','pfas_fac')
enf  = load2('fiokg_enforcement.csv','enforce_records')
wat  = load2('geoconnex_water.csv','water_features')
rucc = load2('rucc.csv','rucc')
sud  = load2('sud_county.csv','sud_providers')
pop  = load2('county_pop.csv','pop')

# scales court cases: drop sentinels
court = pd.read_csv(p('scales_county.csv'), dtype=str); court.columns=['fips','court_cases']
court['fips'] = court['fips'].map(clean_fips)
court['court_cases'] = pd.to_numeric(court['court_cases'], errors='coerce')
court = court[~court['fips'].isin(['66666','99999'])]
court = court[court['fips'].str[:2].isin(STATE.keys())]
court = court.groupby('fips',as_index=False)['court_cases'].sum()

names = pd.read_csv(p('county_names.csv'), dtype=str).dropna()
names['fips']=names['fips'].map(clean_fips); names=names.dropna(subset=['fips']).drop_duplicates('fips')

# SDoH wide
sd = pd.read_csv(p('sdoh_long.csv'), dtype=str)
sd['fips']=sd['fips'].map(clean_fips); sd=sd.dropna(subset=['fips'])
sd['value']=pd.to_numeric(sd['value'],errors='coerce')
sdw = sd.pivot_table(index='fips', columns='indicator', values='value', aggfunc='mean').reset_index()

# health wide
hl = pd.read_csv(p('health_long.csv'), dtype=str)
hl['fips']=hl['fips'].map(clean_fips); hl=hl.dropna(subset=['fips'])
hl['prevalence']=pd.to_numeric(hl['prevalence'],errors='coerce')
hw = hl.pivot_table(index='fips', columns='disease', values='prevalence', aggfunc='mean').reset_index()

# PFAS (Maine)
pf = pd.read_csv(p('sawgraph_pfas.csv'), dtype=str)
pf['fips']=pf['fips'].map(clean_fips)
for c in ['pfas_mean_ngL','pfas_max_ngL','pfas_measurements']: pf[c]=pd.to_numeric(pf[c],errors='coerce')

# nikg (2 counties)
nik = pd.read_csv(p('nikg.csv'), dtype=str)
nik['fips']=nik['fips'].map(clean_fips); nik['value']=pd.to_numeric(nik['value'],errors='coerce')
nikw = nik.pivot_table(index='fips',columns='metric',values='value',aggfunc='sum').reset_index()

# ---------- master merge ----------
m = names.copy()
for df in [fac,pfac,enf,wat,rucc,sud,pop,court,sdw,hw]:
    m = m.merge(df, on='fips', how='outer')
m = m.merge(pf[['fips','pfas_mean_ngL','pfas_max_ngL','pfas_measurements']], on='fips', how='left')
m = m.merge(nikw, on='fips', how='left')
m['fips']=m['fips'].map(clean_fips)
m = m.dropna(subset=['fips']).drop_duplicates('fips')
m['state']=m['fips'].str[:2].map(STATE)
m = m[m['state'].notna()]                      # keep 50 states + DC + PR
m['name']=m['name'].fillna('FIPS '+m['fips'])

# analysis universe = 50 states + DC (exclude PR/territories for national ranking)
m['in_us50'] = ~m['fips'].str[:2].isin(['72','78','60','66','69'])

# ---------- per-capita rates ----------
m['pop']=pd.to_numeric(m['pop'],errors='coerce')
for raw,rate in [('epa_fac','epa_fac_pc'),('pfas_fac','pfas_fac_pc'),('enforce_records','enforce_pc'),
                 ('court_cases','court_pc'),('sud_providers','sud_pc'),('water_features','water_pc')]:
    m[rate]=np.where((m['pop']>0), m[raw]/m['pop']*10000.0, np.nan)

# ---------- burden dimensions (national, US50) ----------
U = m[m['in_us50']].copy()
def pct(col):
    return U[col].rank(pct=True)
U['r_fac']   = pct('epa_fac_pc')      # many facilities per capita
U['r_svi']   = U['svi'].rank(pct=True)
U['r_court'] = pct('court_pc')
U['r_rural'] = U['rucc'].rank(pct=True)
U['r_servscarce'] = 1 - U['sud_pc'].rank(pct=True)   # few services -> high scarcity
TOP=2/3.0
U['f_facilities'] = (U['r_fac']>=TOP).astype('Int64')
U['f_vulnerability']=(U['r_svi']>=TOP).astype('Int64')
U['f_court']      = (U['r_court']>=TOP).astype('Int64')
U['f_rural']      = (U['rucc']>=4).astype('Int64')                 # nonmetro RUCC>=4
U['f_fewservices']= (U['r_servscarce']>=TOP).astype('Int64')
NAT_DIMS=['f_facilities','f_vulnerability','f_court','f_rural','f_fewservices']
U['burden_agreement'] = U[NAT_DIMS].sum(axis=1, min_count=1)

# continuous composite index: robust percentile-mean of the 5 burden dimensions [0-1]
U['burden_index'] = np.nanmean(np.vstack([
    U['r_fac'].values, U['r_svi'].values, U['r_court'].values,
    U['r_rural'].values, U['r_servscarce'].values]), axis=0)

# PFAS dimension (Maine only) -> agreement_plus
U['f_pfas'] = np.where(U['pfas_mean_ngL'].notna() & (U['pfas_mean_ngL']>0), 1, np.nan)
U['burden_agreement_pfas'] = U['burden_agreement'] + U['f_pfas'].fillna(0)

# merge burden back
bcols=['fips']+NAT_DIMS+['f_pfas','burden_agreement','burden_agreement_pfas','burden_index',
       'r_fac','r_svi','r_court','r_rural','r_servscarce']
m = m.merge(U[bcols], on='fips', how='left')

# ---------- correlations (ecological, across counties) ----------
predictors = {'epa_fac_pc':'EPA facilities /10k','pfas_fac_pc':'PFAS-type facilities /10k',
 'enforce_pc':'Enforcement records /10k','court_pc':'Federal court cases /10k','rucc':'Rurality (RUCC)',
 'svi':'Social Vulnerability Index','water_pc':'Water-monitoring features /10k'}
outcomes = {'diabetes':'Diabetes','obesity':'Obesity','asthma':'Asthma','copd':'COPD','stroke':'Stroke',
 'cad':'Coronary artery disease','depression':'Depression','hypertension':'Hypertension',
 'arteriosclerosis':'Arteriosclerosis','poverty':'Poverty %','uninsured':'Uninsured %',
 'food_insecurity':'Food insecurity %','unemploy':'Unemployment %','lt_hs':'< High school %'}
rows=[]
MM=m[m['in_us50']]
for pk,pl in predictors.items():
    for ok,ol in outcomes.items():
        if pk not in MM or ok not in MM: continue
        d=MM[[pk,ok]].apply(pd.to_numeric,errors='coerce').dropna()
        if len(d)<30: continue
        r,pv=stats.pearsonr(d[pk],d[ok])
        rows.append(dict(predictor=pk,predictor_label=pl,outcome=ok,outcome_label=ol,
                         r=round(r,3),p_value=pv,n=len(d)))
corr=pd.DataFrame(rows)
corr.to_csv(os.path.join(OUT,'correlations.csv'),index=False)

# full corr matrix for heatmap (predictors + key outcomes + burden)
heat_cols=['burden_index','epa_fac_pc','pfas_fac_pc','enforce_pc','court_pc','rucc','svi','sud_pc',
 'poverty','uninsured','food_insecurity','unemploy','lt_hs','diabetes','obesity','asthma','copd',
 'stroke','cad','depression','hypertension']
heat_cols=[c for c in heat_cols if c in m]
cm=m[m['in_us50']][heat_cols].apply(pd.to_numeric,errors='coerce').corr(method='pearson')
cm.to_csv(os.path.join(OUT,'corr_matrix.csv'))

# ---------- master + ranking ----------
m_sorted=m.sort_values(['burden_agreement','burden_index'],ascending=False)
m.to_csv(os.path.join(OUT,'master_county.csv'),index=False)
rank_cols=['fips','name','state','pop','burden_agreement','burden_agreement_pfas','burden_index',
 'f_facilities','f_vulnerability','f_court','f_rural','f_fewservices','f_pfas',
 'epa_fac','epa_fac_pc','pfas_fac','enforce_records','court_cases','court_pc','svi','rucc',
 'sud_providers','sud_pc','poverty','uninsured','food_insecurity','diabetes','obesity']
rank_cols=[c for c in rank_cols if c in m]
m_sorted[m_sorted['in_us50']][rank_cols].to_csv(os.path.join(OUT,'burden_ranking.csv'),index=False)

# ---------- findings_long (one row per finding) ----------
META={
 'epa_fac':('fiokg','facility located in county (FRS, sfWithin)','county','regulatory record','count'),
 'pfas_fac':('fiokg','EPA-PFAS-Facility (industry-flagged) in county','county','regulatory record','count'),
 'enforce_records':('fiokg','enforcement/compliance record for in-county facility','county','regulatory record','count'),
 'water_features':('geoconnex','hydrologic monitoring feature in county (GNIS)','county','monitoring feature','count'),
 'court_cases':('scales','federal court case filed in county (FJC IDB hasIdbCounty)','county','court record','count'),
 'court_pc':('scales','federal court cases per 10k residents','county','court record','per 10k'),
 'rucc':('ruralkg','Rural-Urban Continuum Code (1 urban-9 rural)','county','survey/ranking indicator','code 1-9'),
 'sud_providers':('ruralkg','substance-use treatment providers in county (ZIP->place->county)','county','service listing','count'),
 'poverty':('spoke-okn (SAIPE)','SDoH poverty prevalence in county','county','survey/ranking indicator','%'),
 'lt_hs':('spoke-okn (ACS/AHRQ)','adults < high school in county','county','survey/ranking indicator','%'),
 'food_insecurity':('spoke-okn (County Health Rankings)','food insecurity in county','county','survey/ranking indicator','%'),
 'unemploy':('spoke-okn (ACS/AHRQ)','unemployment in county','county','survey/ranking indicator','%'),
 'uninsured':('spoke-okn (ACS/AHRQ)','uninsured in county','county','survey/ranking indicator','%'),
 'svi':('spoke-okn (CDC SVI)','social vulnerability index in county','county','survey/ranking indicator','0-1'),
 'diabetes':('spoke-okn (CDC PLACES)','age-adjusted diabetes prevalence (places->county)','county','survey/ranking indicator','%'),
 'obesity':('spoke-okn (CDC PLACES)','age-adjusted obesity prevalence (places->county)','county','survey/ranking indicator','%'),
 'asthma':('spoke-okn (CDC PLACES)','age-adjusted asthma prevalence (places->county)','county','survey/ranking indicator','%'),
 'copd':('spoke-okn (CDC PLACES)','age-adjusted COPD prevalence (places->county)','county','survey/ranking indicator','%'),
 'stroke':('spoke-okn (CDC PLACES)','age-adjusted stroke prevalence (places->county)','county','survey/ranking indicator','%'),
 'cad':('spoke-okn (CDC PLACES)','age-adjusted coronary-artery-disease prevalence (places->county)','county','survey/ranking indicator','%'),
 'depression':('spoke-okn (CDC PLACES)','age-adjusted depression prevalence (places->county)','county','survey/ranking indicator','%'),
 'hypertension':('spoke-okn (CDC PLACES)','age-adjusted hypertension prevalence (places->county)','county','survey/ranking indicator','%'),
 'arteriosclerosis':('spoke-okn (CDC PLACES)','age-adjusted arteriosclerosis prevalence (places->county)','county','survey/ranking indicator','%'),
}
frows=[]
for _,r in m.iterrows():
    for ind,(src,rel,geo,ev,unit) in META.items():
        if ind in m and pd.notna(r.get(ind)):
            frows.append([r['fips'],r['name'],r['state'],ind,round(float(r[ind]),4),unit,src,rel,geo,ev])
# PFAS Maine finding rows
for _,r in pf.dropna(subset=['fips']).iterrows():
    nm=names.set_index('fips')['name'].get(r['fips'],'FIPS '+str(r['fips']))
    frows.append([r['fips'],nm,STATE.get(str(r['fips'])[:2],''),'pfas_mean_ngL',round(float(r['pfas_mean_ngL']),3),'ng/L','sawgraph','PFAS water-sample mean, S2->county rollup','county','measured environmental sample'])
    frows.append([r['fips'],nm,STATE.get(str(r['fips'])[:2],''),'pfas_max_ngL',round(float(r['pfas_max_ngL']),3),'ng/L','sawgraph','PFAS water-sample max, S2->county rollup','county','measured environmental sample'])
    frows.append([r['fips'],nm,STATE.get(str(r['fips'])[:2],''),'pfas_measurements',int(r['pfas_measurements']),'count','sawgraph','PFAS water measurements, S2->county rollup','county','measured environmental sample'])
# nikg finding rows (2 counties)
for _,r in nik.dropna(subset=['fips']).iterrows():
    nm=names.set_index('fips')['name'].get(r['fips'],'FIPS '+str(r['fips']))
    frows.append([r['fips'],nm,STATE.get(str(r['fips'])[:2],''),'nikg_'+r['metric'],int(r['value']),'count','nikg','neighborhood incident count in county','county','incident record'])
# scales NIBRS national finding rows
nibrs=pd.read_csv(p('scales_nibrs.csv'),dtype=str); nibrs['charges']=pd.to_numeric(nibrs['charges'],errors='coerce')
for _,r in nibrs.iterrows():
    frows.append(['US','United States','US','nibrs:'+str(r['offense']),int(r['charges']),'charges','scales','federal charges by NIBRS offense category (national)','national','court record'])
# dreamkg Philadelphia ZIP service finding rows
dk=pd.read_csv(p('dreamkg_services.csv'),dtype=str); dk['nservices']=pd.to_numeric(dk['nservices'],errors='coerce')
for _,r in dk.iterrows():
    frows.append([str(r['zip']),'Philadelphia ZIP '+str(r['zip']),'PA','dreamkg_services',int(r['nservices']),'count','dreamkg','homelessness/social services in ZIP','zip','service listing'])
find=pd.DataFrame(frows,columns=['fips','county_name','state','indicator','value','unit','source_kg','relationship','geo_level','evidence_kind'])
find.to_csv(os.path.join(OUT,'findings_long.csv'),index=False)

# ---------- burden x source matrix (top counties) ----------
topN=m_sorted[m_sorted['in_us50']].head(40).copy()
mat_cols=['fips','name','state','burden_agreement','f_facilities','f_vulnerability','f_court','f_rural','f_fewservices']
topN[mat_cols].to_csv(os.path.join(OUT,'burden_matrix_top40.csv'),index=False)

# ---------- summary.json ----------
def cov(col): return int(m[col].notna().sum()) if col in m else 0
summ={
 'n_counties_master':int(m['fips'].nunique()),
 'n_us50':int(m['in_us50'].sum()),
 'coverage':{k:cov(k) for k in ['epa_fac','pfas_fac','enforce_records','water_features','court_cases',
    'rucc','sud_providers','pop','svi','poverty','uninsured','food_insecurity','unemploy','lt_hs',
    'diabetes','obesity','asthma','copd','stroke','cad','depression','hypertension','pfas_mean_ngL']},
 'pfas_counties':int(pf['fips'].notna().sum()),
 'nibrs_categories':int(len(nibrs)),
 'dreamkg_zips':int(len(dk)),
 'burden_agreement_dist':{int(k):int(v) for k,v in U['burden_agreement'].value_counts().sort_index().items()},
 'top_burden':m_sorted[m_sorted['in_us50']].head(20)[['fips','name','state','burden_agreement','burden_index','epa_fac','court_cases','svi','rucc','sud_providers','poverty']].round(3).to_dict('records'),
 'top_correlations':corr.reindex(corr['r'].abs().sort_values(ascending=False).index).head(25).to_dict('records'),
}
json.dump(summ, open(os.path.join(OUT,'summary.json'),'w'), indent=1, default=str)

print("counties (master):", m['fips'].nunique(), "| US50:", int(m['in_us50'].sum()))
print("coverage:", summ['coverage'])
print("agreement dist:", summ['burden_agreement_dist'])
print("findings rows:", len(find))
print("\nTOP 15 BURDEN COUNTIES (US50):")
print(m_sorted[m_sorted['in_us50']].head(15)[['fips','name','state','burden_agreement','burden_index','epa_fac','court_cases','svi','rucc','sud_providers']].to_string(index=False))
print("\nTOP correlations:")
print(corr.reindex(corr['r'].abs().sort_values(ascending=False).index).head(15)[['predictor','outcome','r','p_value','n']].to_string(index=False))

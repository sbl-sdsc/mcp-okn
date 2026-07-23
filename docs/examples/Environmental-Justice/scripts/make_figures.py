#!/usr/bin/env python3
"""Generate all report figures + interactive county map for the EJ study."""
import sys, os, json
sys.path.insert(0, "/sessions/keen-charming-hypatia/mnt/.claude/skills/okn-report-style/scripts")
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import okn_figstyle as F
F.apply_style()

BASE="/sessions/keen-charming-hypatia/mnt/Environmental-Justice"
D=f"{BASE}/data"; FIG=f"{BASE}/figures"
os.makedirs(FIG, exist_ok=True)
m=pd.read_csv(f"{D}/master_county.csv", dtype={'fips':str})
SVI='Overall(Socioeconomic Status,Household Characteristics,Racial & Ethnic Minority Status,Housing Type & Transportation)'

OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','yellow':'#F0E442','sky':'#56B4E9','grey':'#999999','black':'#333333'}

# ---------- Fig 1: multi-source coverage by axis ----------
cov=[('Industrial facilities','n_fac','fiokg'),
     ('PFAS facilities','n_pfas_fac','fiokg'),
     ('Chemical diversity','n_chem','spoke-okn'),
     ('PFAS sampling (regional)','n_pfas_obs','sawgraph'),
     ('Air pollution (PM2.5)','air pollution - particulate matter','spoke-okn'),
     ('Socioeconomic / SVI','Overall(Socioeconomic Status,Household Characteristics,Racial & Ethnic Minority Status,Housing Type & Transportation)','spoke-okn'),
     ('Public safety (overdose)','drug overdose deaths','spoke-okn'),
     ('Health outcomes (asthma)','prev_asthma','spoke-okn'),
     ('Federal court caseload','n_case','scales'),
     ('Treatment services','n_prov','ruralkg')]
kgc={'fiokg':OK['red'],'spoke-okn':OK['blue'],'sawgraph':OK['orange'],'scales':OK['purple'],'ruralkg':OK['green']}
labels=[c[0] for c in cov]; vals=[int(m[c[1]].notna().sum()) if c[1]!='n_prov' else int((m[c[1]]>0).sum()) for c in cov]
themes=[c[2] for c in cov]
order=np.argsort(vals)
fig,ax=plt.subplots(figsize=(8.2,5.2))
F.ranked_barh(ax,[labels[i] for i in order],[vals[i] for i in order],
              themes=[themes[i] for i in order],theme_colors=kgc,
              annots=[str(vals[i]) for i in order],xlabel="U.S. counties with data")
ax.set_title("Evidence-axis coverage across the OKN federation")
F.finalize(fig,1,f"{FIG}/fig1_coverage.png")

# ---------- Fig 2: consensus distribution + tiers ----------
dist=m['consensus'].value_counts().sort_index()
tcol={0:OK['grey'],1:OK['sky'],2:OK['sky'],3:OK['yellow'],4:OK['orange'],5:OK['red'],6:OK['black']}
fig,ax=plt.subplots(figsize=(7.6,4.6))
bars=ax.bar(dist.index.astype(int).astype(str),dist.values,
            color=[tcol[int(k)] for k in dist.index],edgecolor='white')
for b,v in zip(bars,dist.values): ax.text(b.get_x()+b.get_width()/2,v+8,str(int(v)),ha='center',fontsize=9)
ax.set_xlabel("Consensus burden score (independent domains flagged, 0–6)")
ax.set_ylabel("Number of counties")
ax.set_title("Cumulative-burden consensus across %d U.S. counties"%len(m))
import matplotlib.patches as mp
leg=[mp.Patch(color=OK['grey'],label='D — low (0)'),mp.Patch(color=OK['sky'],label='C — moderate (1–2)'),
     mp.Patch(color=OK['yellow'],label='B — high (3–4)'),mp.Patch(color=OK['red'],label='A — very high (5–6)')]
ax.legend(handles=leg,fontsize=8,frameon=False,loc='upper right')
F.finalize(fig,2,f"{FIG}/fig2_consensus.png")

# ---------- Fig 3: top-20 cumulative-burden counties ----------
top=m.sort_values(['consensus','burden_index'],ascending=False).head(20).copy()
top['name']=top['label'].str.replace(' County','').str.replace(' Parish','').str.replace(' city',' (city)')+", "+top['stateName'].map({
 'Louisiana':'LA','Michigan':'MI','Missouri':'MO','Maryland':'MD','Arkansas':'AR','Alabama':'AL','Mississippi':'MS','Oklahoma':'OK','Georgia':'GA','Florida':'FL','Tennessee':'TN','Arizona':'AZ','California':'CA','Texas':'TX','South Carolina':'SC','Kentucky':'KY'})
def ttheme(t): return 'A' if t.startswith('A') else ('B' if t.startswith('B') else 'C')
themes=[ttheme(t) for t in top['tier']]
fig,ax=plt.subplots(figsize=(8.4,6.4))
F.ranked_barh(ax,top['name'][::-1].tolist(),top['burden_index'][::-1].tolist(),
              themes=themes[::-1],theme_colors={'A':OK['red'],'B':OK['orange'],'C':OK['yellow']},
              annots=[f"cons {int(c)} (E{int(e)}/S{int(s)})" for c,e,s in zip(top['consensus'][::-1],top['env_burden'][::-1],top['soc_burden'][::-1])],
              xlabel="Composite burden index (mean z across 6 domains)")
ax.set_title("Top 20 counties by cumulative environmental–social burden")
F.finalize(fig,3,f"{FIG}/fig3_top_counties.png")

# ---------- Fig 4: national state-level burden map ----------
SC={'Alabama':(32.8,-86.8),'Arizona':(34.3,-111.7),'Arkansas':(34.9,-92.4),'California':(37.2,-119.4),'Colorado':(39.0,-105.5),'Connecticut':(41.6,-72.7),'Delaware':(39.0,-75.5),'District of Columbia':(38.9,-77.0),'Florida':(28.6,-82.4),'Georgia':(32.6,-83.4),'Idaho':(44.2,-114.5),'Illinois':(40.0,-89.2),'Indiana':(39.9,-86.3),'Iowa':(42.0,-93.5),'Kansas':(38.5,-98.3),'Kentucky':(37.5,-85.3),'Louisiana':(31.0,-92.0),'Maine':(45.4,-69.2),'Maryland':(39.0,-76.8),'Massachusetts':(42.3,-71.8),'Michigan':(44.3,-85.4),'Minnesota':(46.3,-94.3),'Mississippi':(32.7,-89.7),'Missouri':(38.4,-92.5),'Montana':(46.9,-110.0),'Nebraska':(41.5,-99.8),'Nevada':(39.3,-116.6),'New Hampshire':(43.7,-71.6),'New Jersey':(40.2,-74.7),'New Mexico':(34.4,-106.1),'New York':(42.9,-75.5),'North Carolina':(35.5,-79.4),'North Dakota':(47.5,-100.5),'Ohio':(40.3,-82.8),'Oklahoma':(35.6,-97.5),'Oregon':(43.9,-120.6),'Pennsylvania':(40.9,-77.8),'Rhode Island':(41.7,-71.6),'South Carolina':(33.9,-80.9),'South Dakota':(44.4,-100.2),'Tennessee':(35.9,-86.4),'Texas':(31.5,-99.3),'Utah':(39.3,-111.7),'Vermont':(44.1,-72.7),'Virginia':(37.5,-78.9),'Washington':(47.4,-120.5),'West Virginia':(38.6,-80.6),'Wisconsin':(44.6,-89.9),'Wyoming':(43.0,-107.5)}
STAB={'Alabama':'AL','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','District of Columbia':'DC','Florida':'FL','Georgia':'GA','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
st=pd.read_csv(f"{D}/state_rollup.csv")
st=st[st['stateName'].isin(SC)]
st['lat']=st['stateName'].map(lambda s:SC[s][0]); st['lon']=st['stateName'].map(lambda s:SC[s][1])
fig,ax=plt.subplots(figsize=(9.2,5.8))
sc=ax.scatter(st['lon'],st['lat'],s=(40+st['n_high']*5.0),c=st['mean_consensus'],cmap='YlOrRd',
              edgecolor='#333',linewidth=0.5,zorder=3,vmin=0)
for _,r in st.iterrows(): ax.annotate(STAB[r['stateName']],(r['lon'],r['lat']),fontsize=6.5,ha='center',va='center',zorder=4)
ax.set_xlim(-125,-66); ax.set_ylim(24,50); ax.set_aspect(1.28)
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.grid(alpha=0.18)
plt.colorbar(sc,ax=ax,label="Mean consensus burden (0–6)",shrink=0.75)
ax.set_title("Mean county burden by state (marker size ∝ high-burden county count)")
F.finalize(fig,4,f"{FIG}/fig4_state_map.png")

# ---------- Fig 5: county hot-spot map (83 counties) ----------
cen=pd.read_csv(f"{D}/county_centroids.csv",dtype={'fips':str})
h=m.merge(cen,on='fips')
fig,ax=plt.subplots(figsize=(9.2,5.8))
for _,r in st.iterrows(): ax.annotate(STAB[r['stateName']],(r['lon'],r['lat']),fontsize=6,ha='center',va='center',color='#bbb',zorder=1)
sc=ax.scatter(h['lon'],h['lat'],s=(35+h['mismatch_index'].clip(lower=0).fillna(0).values*16),
              c=h['consensus'],cmap='YlOrRd',edgecolor='#333',linewidth=0.5,zorder=3,vmin=0,vmax=6)
ax.set_xlim(-107,-66); ax.set_ylim(24,48); ax.set_aspect(1.28)
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.grid(alpha=0.18)
plt.colorbar(sc,ax=ax,label="Consensus burden (0–6)",shrink=0.75)
ax.set_title("Highest-burden & greatest-mismatch counties (size ∝ burden↔service mismatch)")
F.finalize(fig,5,f"{FIG}/fig5_county_hotspots.png")

# ---------- interactive folium county map for HTML ----------
rows=[]
for _,r in h.sort_values('consensus',ascending=False).iterrows():
    rows.append({'lat':r['lat'],'lon':r['lon'],
                 'County':f"{r['label']}, {r['stateName']}",'Consensus (0-6)':int(r['consensus']),
                 'Tier':r['tier'],'Env domains':int(r['env_burden']),'Social domains':int(r['soc_burden']),
                 'Mismatch index':round(float(r['mismatch_index']),2) if pd.notna(r['mismatch_index']) else None,
                 'value':int(r['consensus'])})
mp_=F.folium_osm_map(rows,lat_key='lat',lon_key='lon',value_key='value',
    popup_keys=['County','Consensus (0-6)','Tier','Env domains','Social domains','Mismatch index'],
    tooltip_key='County',zoom_start=5,radius=7)
F.save_map_html(mp_, f"{D}/county_map.html")
iframe=F.folium_map_iframe(mp_, height=520, title="County burden hot-spots (spatialkg centroids)")
open(f"{D}/county_map_iframe.html","w").write(iframe)

# ---------- Fig 6: domain correlation heatmap ----------
cm=pd.read_csv(f"{D}/domain_correlations.csv",index_col=0)
short={'D1_pollution_sources':'D1 Pollution src','D2_chemical_exposure':'D2 Chem exposure','D3_ambient_quality':'D3 Ambient qual','D4_socioeconomic':'D4 Socioecon','D5_public_safety':'D5 Public safety','D6_health_outcomes':'D6 Health','D7_service_scarcity':'D7 Service gap'}
labs=[short[c] for c in cm.columns]
fig,ax=plt.subplots(figsize=(7.4,6.0))
F.diverging_heatmap(ax,cm.values,labs,labs,vmax=1.0)  # long x labels auto-tilt (okn_figstyle)
ax.set_title("Spearman correlation among burden domains")
F.finalize(fig,6,f"{FIG}/fig6_correlations.png")

# ---------- Fig 7: top mismatch counties ----------
mis=m[m['consensus']>=4].sort_values('mismatch_index',ascending=False).head(15).copy()
mis['name']=mis['label'].str.replace(' County','').str.replace(' Parish','')+", "+mis['stateName'].map({'Georgia':'GA','Alabama':'AL','Mississippi':'MS','Texas':'TX','Oklahoma':'OK','Kentucky':'KY','Arkansas':'AR','Louisiana':'LA','South Carolina':'SC','Tennessee':'TN'})
fig,ax=plt.subplots(figsize=(8.2,5.6))
F.ranked_barh(ax,mis['name'][::-1].tolist(),mis['mismatch_index'][::-1].tolist(),
              themes=['mis']*len(mis),theme_colors={'mis':OK['purple']},
              annots=[f"burden {b:+.2f} | access {a:+.2f}" for b,a in zip(mis['burden_index'][::-1],mis['service_capacity'][::-1])],
              xlabel="Mismatch index (burden z − service-capacity z)")
ax.set_title("Greatest burden↔service mismatch (high burden, low access)")
F.finalize(fig,7,f"{FIG}/fig7_mismatch.png")

# ---------- Fig 8: PFAS ToxCast bioactivity + AOP529 ----------
pf=pd.read_csv(f"{D}/mechanistic_pfas.csv").sort_values('toxcast_endpoints')
fig,ax=plt.subplots(figsize=(8.2,5.4))
F.ranked_barh(ax,pf['chemical'].tolist(),pf['toxcast_endpoints'].tolist(),
              themes=['pfas']*len(pf),theme_colors={'pfas':OK['orange']},
              annots=[str(int(v)) for v in pf['toxcast_endpoints']],xlabel="ToxCast assay endpoints")
ax.set_title("Toxicological bioactivity of PFAS measured in SAWGraph water samples")
F.finalize(fig,8,f"{FIG}/fig8_pfas_toxcast.png")

print("figures written:", sorted(os.listdir(FIG)))

import sys, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0,"/sessions/affectionate-festive-ramanujan/mnt/.claude/skills/okn-report-style/scripts")
from okn_figstyle import apply_style, finalize, legend_outside, panel_title, ranked_barh
apply_style()
NB=pd.read_csv('data/network_basemap_points.csv.gz')
def netbase(ax, xlim=(-125,-66), ylim=(24,50)):
    ax.scatter(NB.lng, NB.lat, s=.06, color='#C8D8E4', linewidths=0, zorder=0, rasterized=True)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect(1/np.cos(np.radians(38)))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
OK={'blue':'#0072B2','orange':'#E69F00','green':'#009E73','red':'#D55E00','purple':'#CC79A7','sky':'#56B4E9','yellow':'#F0E442','grey':'#666666'}

T=pd.read_csv('data/county_typology.csv', dtype={'fips':str})
cen=pd.read_csv('data/county_centroids.csv', dtype={'fips':str})
T=T.merge(cen,on='fips',how='left')
cells=pd.read_csv('data/ufokn_flood_cells.csv')
j=pd.read_csv('data/flood_cells_joined.csv', dtype={'id':str,'fips':str})
sec=pd.read_csv('data/industry_sectors.csv', dtype={'sector':str})
prog=pd.read_csv('data/epa_programs.csv')
link=pd.read_csv('data/routing_links_tiered.csv.gz', dtype={'srcc':str,'dsc':str,'ds_fips':str,'src_fips':str})
wells=pd.read_csv('data/flooded_wells.csv')
S=json.load(open('data/headline_stats.json'))

# ---- FIG 1: flood footprint + co-located facility cells (national OSM map) ----
fig,axs=plt.subplots(1,2,figsize=(13.5,6.4))
facc=set(j[j.frs.notna()].id.unique())
c=cells.copy(); c['has_fac']=c.s2_l13.astype(str).isin(facc)
netbase(axs[0])
sc=axs[0].scatter(c.lng, c.lat, c=np.log10(c.n_buildings), s=14, cmap='YlOrRd', edgecolor='none', alpha=.9, zorder=3)
fig.colorbar(sc, ax=axs[0], orientation='horizontal', fraction=.045, pad=.02, label='log10 flooded buildings per cell')
axs[0].set_title("A   Modelled flood footprint (UF-OKN)", loc='left', fontweight='bold', fontsize=11)
sub=c[c.has_fac]
netbase(axs[1])
axs[1].scatter(sub.lng, sub.lat, s=14, color=OK['red'], edgecolor='none', alpha=.9, zorder=3)
axs[1].set_title("B   Flood cells with an EPA-regulated facility", loc='left', fontweight='bold', fontsize=11)
finalize(fig,1,'figures/fig1_flood_footprint_map.png')

# ---- FIG 2: industry composition + concentration ----
fig,axs=plt.subplots(1,2,figsize=(13.5,5.6))
s=sec.head(12).iloc[::-1]
axs[0].barh(s.sector_name.fillna(s.sector), s.facilities, color=OK['blue'])
axs[0].set_xlabel('flood-exposed facilities'); panel_title(axs[0],"A","Top NAICS sectors (2-digit)")
axs[0].tick_params(axis='y', labelsize=8)
sh=np.sort(sec.facilities.values)[::-1]; cum=np.cumsum(sh)/sh.sum()
axs[1].plot(np.arange(1,len(cum)+1), cum*100, marker='o', color=OK['red'], lw=2)
axs[1].axhline(50, ls='--', color=OK['grey'], lw=1); axs[1].set_ylim(0,101)
axs[1].set_xlabel('sectors ranked by facility count'); axs[1].set_ylabel('cumulative share (%)')
axs[1].annotate(f"HHI = {S['hhi_sector']:.0f}\ntop-3 = 45.1%", xy=(0.55,0.25), xycoords='axes fraction', fontsize=10)
panel_title(axs[1],"B","Concentration of flood exposure across sectors")
finalize(fig,2,'figures/fig2_industry_concentration.png')

# ---- FIG 3: routing structure ----
fig,axs=plt.subplots(1,3,figsize=(15,4.8))
tv=link.tier.value_counts().reindex(['A_same_HUC8','B_same_HUC4','C_same_HUC2','D_cross_region']).fillna(0)
axs[0].bar([t.split('_',1)[1] for t in tv.index], tv.values,
           color=[OK['green'],OK['sky'],OK['orange'],OK['red']])
axs[0].set_ylabel('source→downstream reach links'); axs[0].tick_params(axis='x',labelsize=8)
panel_title(axs[0],"A","Routed links by hydrologic proximity tier")
fan=link.groupby('srcc').dsc.nunique()
axs[1].hist(fan, bins=40, color=OK['blue']); axs[1].set_xlabel('downstream reaches per source reach'); axs[1].set_ylabel('source reaches')
panel_title(axs[1],"B","Downstream fan-out")
nc=link[link.ds_fips!=link.src_fips].groupby('ds_fips').src_fips.nunique()
axs[2].hist(nc, bins=30, color=OK['purple']); axs[2].set_xlabel('distinct upstream source counties'); axs[2].set_ylabel('receiving counties')
panel_title(axs[2],"C","Upstream contributing counties")
finalize(fig,3,'figures/fig3_routing_structure.png')

# ---- FIG 4: typology map ----
COL={'Compound':OK['red'],'Imported':OK['orange'],'Retained':OK['blue'],'Low':'#BBBBBB'}
fig,ax=plt.subplots(figsize=(12,7))
Tm=T.dropna(subset=['lat','lng'])
netbase(ax, xlim=(-105,-66), ylim=(28,49.5))
for t in ['Low','Retained','Imported','Compound']:
    d=Tm[Tm.typology==t]
    if len(d)==0: continue
    ax.scatter(d.lng, d.lat, s=(78 if t=='Compound' else 34), color=COL[t], edgecolor='white', lw=.4,
               label=f"{t} (n={len(d)})", zorder=3)
ax.set_title("Flood-cascade typology by county")
legend_outside(ax, where='below', ncol=4, title='typology')
finalize(fig,4,'figures/fig4_typology_map.png')

# ---- FIG 5: retained vs imported quadrants ----
fig,ax=plt.subplots(figsize=(8.2,6.6))
for t in ['Low','Retained','Imported','Compound']:
    d=T[T.typology==t]
    ax.scatter(d.retained_score, d.imported_score, s=22, color=COL[t], label=f"{t} (n={len(d)})", edgecolor='none', alpha=.85)
ax.axvline(0.60, ls='--', color=OK['grey'], lw=1); ax.axhline(0.60, ls='--', color=OK['grey'], lw=1)
ax.set_xlabel('retained-risk score (percentile of co-located flood-exposed facilities)')
ax.set_ylabel('imported-risk score (percentile of tier-weighted upstream load)')
ax.set_title('Retained vs imported flood-contamination risk')
legend_outside(ax, where='right', title='typology')
finalize(fig,7,'figures/fig7_typology_quadrants.png')

# ---- FIG 6: who lives downstream ----
fig,axs=plt.subplots(1,3,figsize=(14.5,4.8))
order=['Retained','Compound','Imported','Low']
d=T[T.rucc.notna()]
axs[0].boxplot([d[d.typology==t].rucc.values for t in order], labels=order, patch_artist=True,
               boxprops=dict(facecolor=OK['sky']), medianprops=dict(color='black'))
axs[0].set_ylabel('RUCC (1 = metro core … 9 = most rural)'); axs[0].tick_params(axis='x',labelsize=8)
panel_title(axs[0],"A","Rurality by typology")
pr=[100*d[d.typology==t].rural.mean() for t in order]
axs[1].bar(order, pr, color=[COL[t] for t in order]); axs[1].set_ylabel('% counties rural (RUCC ≥ 4)')
axs[1].tick_params(axis='x',labelsize=8); panel_title(axs[1],"B","Share rural")
axs[2].boxplot([np.log10(d[d.typology==t]['pop'].clip(lower=1).values) for t in order], labels=order,
               patch_artist=True, boxprops=dict(facecolor=OK['yellow']), medianprops=dict(color='black'))
axs[2].set_ylabel('log10 county population'); axs[2].tick_params(axis='x',labelsize=8)
panel_title(axs[2],"C","Population size")
finalize(fig,5,'figures/fig5_who_lives_downstream.png')

# ---- FIG 7: rank churn ----
fig,axs=plt.subplots(1,2,figsize=(13.5,5.8))
axs[0].scatter(T.baseline_rank, T.cascade_rank, s=16, c=[COL[t] for t in T.typology], edgecolor='none', alpha=.85)
axs[0].plot([0,len(T)],[0,len(T)], ls='--', color=OK['grey'], lw=1)
axs[0].set_xlabel('rank on co-location alone (baseline)'); axs[0].set_ylabel('rank with hydrologic routing')
axs[0].invert_xaxis(); axs[0].invert_yaxis()
axs[0].annotate(f"Spearman ρ = {S['spearman']}\nKendall τ = {S['kendall']}\ntop-50 churn = {S['top50_churn']}/50",
                xy=(0.05,0.06), xycoords='axes fraction', fontsize=10)
panel_title(axs[0],"A","Ranking with vs without routing")
cl=T.nlargest(12,'rank_shift').iloc[::-1]
axs[1].barh(cl.label.str.replace(' County','').str.replace(', ',', '), cl.rank_shift, color=OK['orange'])
axs[1].set_xlabel('places gained when routing is added'); axs[1].tick_params(axis='y',labelsize=8)
panel_title(axs[1],"B","Largest climbers (imported risk)")
finalize(fig,6,'figures/fig6_rank_churn.png')

# ---- FIG 8: direct pathway + monitoring gap ----
fig,axs=plt.subplots(1,2,figsize=(13,5.2))
lab={'d.ISGS-WellPurpose.MONIT':'Monitoring (IL)','d.ISGS-WellPurpose.WATER':'Water supply (IL)',
     'd.ISGS-WellPurpose.ENG':'Engineering (IL)','d.ISGS-WellPurpose.WTST':'Water test (IL)',
     'd.ISGS-WellPurpose.CROP':'Irrigation (IL)'}
wp=wells.purpose.value_counts()
wu=wells.use.value_counts()
names=[lab.get(k,k.split('.')[-1]) for k in wp.index[:6]]+['Domestic (ME)','Commercial (ME)']
vals=list(wp.values[:6])+[int(wu.get('d.wellUse.Domestic',0)), int(wu.get('d.wellUse.Commercial',0))]
cols=[OK['red'] if ('Water supply' in n or 'Domestic' in n) else OK['grey'] for n in names]
axs[0].barh(names[::-1], vals[::-1], color=cols[::-1]); axs[0].set_xlabel('wells inside modelled flood cells')
axs[0].tick_params(axis='y',labelsize=8); panel_title(axs[0],"A","Flooded wells by purpose (direct pathway)")
IC=T[T.typology.isin(['Imported','Compound'])]
mg=[(IC.ds_monitored_cells==0).sum(), (IC.ds_monitored_cells>0).sum()]
axs[1].bar(['no downstream\nmonitoring','has downstream\nmonitoring'], mg, color=[OK['red'],OK['green']])
for i,v in enumerate(mg): axs[1].text(i, v+3, str(v), ha='center', fontsize=10)
axs[1].set_ylabel('Imported / Compound counties'); axs[1].tick_params(axis='x',labelsize=8)
panel_title(axs[1],"B","Downstream monitoring coverage")
finalize(fig,8,'figures/fig8_direct_pathway_and_monitoring.png')
print("figures done")

import sys, json, pandas as pd, numpy as np, re
sys.path.insert(0,"/sessions/affectionate-festive-ramanujan/mnt/.claude/skills/okn-report-style/scripts")
from build_report_html import build_report_from_markdown, candidate_table, kpis_from_stats, load_stats, fill_stats
from okn_figstyle import folium_map_iframe
import folium

S=load_stats('data/stats.json')
T=pd.read_csv('data/county_typology.csv', dtype={'fips':str})
cen=pd.read_csv('data/county_centroids.csv', dtype={'fips':str})
T=T.drop(columns=[c for c in ['lat','lng'] if c in T.columns]).merge(cen,on='fips',how='left')
T['sources']=T.apply(lambda r: [s for s,ok in [('ufokn',r.flood_cells>0),('fiokg',r.local_fac>0),
    ('hydrologykg',(r.imported_fac>0) or (r.ds_reaches>0)),('spatialkg',True),('ruralkg',pd.notna(r.rucc)),
    ('sawgraph',r.ds_monitored_cells>0)] if ok], axis=1)
T['n_sources']=T.sources.apply(len)
T['tier']=T.strongest_tier.fillna('—').astype(str).str.replace('_',' ',regex=False)
T['rural_flag']=np.where(T.rural.fillna(False),'rural','not rural')
rows=[]
for _,r in T.sort_values('cascade_rank').iterrows():
    rows.append(dict(county=r.label if isinstance(r.label,str) else r.fips, fips=r.fips, state=r.st if isinstance(r.st,str) else '',
        typology=r.typology, tier=r.tier, rural=r.rural_flag,
        local_fac=int(r.local_fac), imported_fac=int(r.imported_fac), imported_wt=round(float(r.imported_fac_wt),1),
        upstream_counties=int(r.upstream_src_counties), ds_monitoring=int(r.ds_monitored_cells),
        flood_cells=int(r.flood_cells), rucc=('' if pd.isna(r.rucc) else int(r.rucc)),
        population=('' if pd.isna(r['pop']) else int(r['pop'])),
        cascade_rank=int(r.cascade_rank), baseline_rank=int(r.baseline_rank), rank_shift=int(r.rank_shift),
        n_sources=int(r.n_sources), sources=r.sources))
cols=[('cascade_rank','cascade rank'),('county','county'),('state','st'),('typology','typology'),
      ('tier','strongest tier'),('local_fac','co-located facilities'),('imported_fac','imported facilities'),
      ('imported_wt','imported (tier-wt)'),('upstream_counties','upstream counties'),
      ('ds_monitoring','downstream monitoring cells'),('flood_cells','flood cells'),('rucc','RUCC'),
      ('rural','rurality'),('population','population'),('baseline_rank','co-location rank'),
      ('rank_shift','rank shift'),('n_sources','sources (n)')]
table=candidate_table(rows, cols,
    search_keys=['county','state','typology','tier'],
    numeric_keys=['cascade_rank','local_fac','imported_fac','imported_wt','upstream_counties','ds_monitoring',
                  'flood_cells','rucc','population','baseline_rank','rank_shift','n_sources'],
    page_size=25, default_sort='cascade_rank',
    extra_filters=[('typology','typology'),('tier','tier'),('state','state'),('rural','rurality')],
    sources_col=('n_sources','sources'))

COL={'Compound':'#D55E00','Imported':'#E69F00','Retained':'#0072B2','Low':'#BBBBBB'}
Tm=T.dropna(subset=['lat','lng'])
m=folium.Map(location=[float(Tm.lat.median()), float(Tm.lng.median())], zoom_start=5, tiles='OpenStreetMap')
for _,r in Tm.iterrows():
    pop="<br>".join([f"<b>{k}</b>: {v}" for k,v in [
        ('county', r.label),('typology', r.typology),('strongest tier', r.tier),
        ('co-located facilities', int(r.local_fac)),('imported facilities', int(r.imported_fac)),
        ('imported (tier-weighted)', round(float(r.imported_fac_wt),1)),
        ('upstream counties', int(r.upstream_src_counties)),
        ('RUCC', '' if pd.isna(r.rucc) else int(r.rucc)),('population','' if pd.isna(r['pop']) else int(r['pop'])),
        ('downstream monitoring cells', int(r.ds_monitored_cells)),('sources', ", ".join(r.sources))]])
    folium.CircleMarker([float(r.lat),float(r.lng)], radius=7 if r.typology=='Compound' else 4.5,
        color=COL[r.typology], fill=True, fill_color=COL[r.typology], fill_opacity=.85, weight=1,
        popup=folium.Popup(pop, max_width=340), tooltip=str(r.label)).add_to(m)
legend=("<div style='margin:6px 0 2px 0;font-size:13px'>"
        + " ".join(f"<span style='display:inline-block;width:11px;height:11px;border-radius:50%;background:{c};margin-right:4px'></span>{k}"
                   for k,c in COL.items()) + "</div>")
map_html = legend + folium_map_iframe(m, height=560, title="Flood-cascade typology (interactive)")

md=open('scripts/report_template.md').read()
md=md.replace('<!-- INTERACTIVE_MAP -->', '<!-- MAPSLOT -->')
open('/tmp/_report_with_map.md','w').write(md)
import shutil, os
shutil.copy('/tmp/_report_with_map.md','_tmp_report.md')
build_report_from_markdown('_tmp_report.md','Flood-Cascade_report.html',
    kpis=kpis_from_stats(S,[('counties_scope','counties in scope'),('facilities','flood-exposed facilities'),
        ('imported_only','Imported counties'),('compound','Compound counties'),
        ('zero_local_nonzero_imported','zero-local, non-zero imported'),('top50_churn','top-50 rank churn')]),
    table=table, stats=S, verify=False)
h=open('Flood-Cascade_report.html').read()
h=h.replace('&lt;!-- MAPSLOT --&gt;', map_html).replace('<!-- MAPSLOT -->', map_html)
open('Flood-Cascade_report.html','w').write(h)
from build_report_html import check_report_parity
check_report_parity('_tmp_report.md','Flood-Cascade_report.html')
# fill the delivered .md so it reads standalone
_md=fill_stats(open('scripts/report_template.md').read(), S).replace('<!-- INTERACTIVE_MAP -->',
  '*(An interactive OpenStreetMap-tiled version of this map, with every county clickable, is embedded in `Flood-Cascade_report.html`.)*')
open('Flood-Cascade_report.md','w').write(_md)

print("html ok")

import sys, json
sys.path.insert(0,'scripts')
import numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import okn_figstyle as F; F.apply_style()
import contextily as cx
D='data'; FIG='figures'
gdf=gpd.read_file(D+'/counties_simplified.geojson')
gdf['county_FIPS']=gdf.county_FIPS.astype(str).str.zfill(5)
cm=pd.read_csv(D+'/county_analysis_matrix.csv',dtype={'county_FIPS':str})
g=gdf.merge(cm[['county_FIPS','CHR_diabetes_prevalence','SAIPE_PCT_POV','ACS_PCT_LT_HS','CDCP_NO_PHY_ACTV_ADULT_A']],on='county_FIPS',how='left')
g=g[g.CHR_diabetes_prevalence.notna()]
print('mapped counties',len(g))
conus=g.cx[-127:-66,24:50].to_crs(3857)
fig,ax=plt.subplots(figsize=(13.2,7.6))
vmin,vmax=float(conus.CHR_diabetes_prevalence.quantile(0.02)),float(conus.CHR_diabetes_prevalence.quantile(0.98))
conus.plot(column='CHR_diabetes_prevalence',cmap='YlOrRd',ax=ax,linewidth=0.08,edgecolor='#666',
           vmin=vmin,vmax=vmax,alpha=0.86)
try: cx.add_basemap(ax,source=cx.providers.OpenStreetMap.Mapnik,attribution_size=6,zoom=5)
except Exception as e: print('basemap failed:',e)
ax.set_axis_off()
sm=plt.cm.ScalarMappable(cmap='YlOrRd',norm=mcolors.Normalize(vmin=vmin,vmax=vmax))
cb=fig.colorbar(sm,ax=ax,fraction=0.028,pad=0.01)
cb.set_label('adult diagnosed-diabetes prevalence (%)',fontsize=9)
ax.set_title(f'County-level diagnosed-diabetes prevalence, contiguous US (n={len(conus)} counties)',fontsize=12)
F.finalize(fig,6,f'{FIG}/fig6_prevalence_map.png')
# interactive folium
import folium
gj=g[['county_FIPS','label','CHR_diabetes_prevalence','SAIPE_PCT_POV','geometry']].copy()
gj['CHR_diabetes_prevalence']=gj.CHR_diabetes_prevalence.round(1)
gj['SAIPE_PCT_POV']=gj.SAIPE_PCT_POV.round(1)
m=folium.Map(location=[38.5,-96],zoom_start=4,tiles='OpenStreetMap')
folium.Choropleth(geo_data=gj.to_json(),data=gj,columns=['county_FIPS','CHR_diabetes_prevalence'],
    key_on='feature.properties.county_FIPS',fill_color='YlOrRd',fill_opacity=0.78,line_weight=0.15,
    legend_name='Adult diagnosed-diabetes prevalence (%) — spoke-okn / County Health Rankings 2023').add_to(m)
folium.GeoJson(gj.to_json(),style_function=lambda x:{'fillOpacity':0,'weight':0},
    tooltip=folium.GeoJsonTooltip(fields=['label','CHR_diabetes_prevalence','SAIPE_PCT_POV'],
    aliases=['County','Diabetes prevalence (%)','Poverty (%)'],sticky=True)).add_to(m)
open(D+'/county_map.html','w').write(m.get_root().render())
print('folium written', len(open(D+'/county_map.html').read()))

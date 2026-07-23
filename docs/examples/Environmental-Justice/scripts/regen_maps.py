#!/usr/bin/env python3
"""Regenerate Fig 4 (state choropleth) and Fig 5 (state boundaries + hotspot counties)
as real polygon-geometry maps (Albers EPSG:5070) from spatialkg geometries — OSM tiles are
unreachable in the build sandbox, so we draw true geographic boundaries rather than a scatter."""
import sys, os, io, csv, json
csv.field_size_limit(sys.maxsize)
sys.path.insert(0,"/sessions/keen-charming-hypatia/mnt/.claude/skills/okn-report-style/scripts")
import pandas as pd, numpy as np, geopandas as gpd
from shapely import wkt as shwkt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import okn_figstyle as F; F.apply_style()

BASE="/sessions/keen-charming-hypatia/mnt/Environmental-Justice"; D=f"{BASE}/data"; FIG=f"{BASE}/figures"
TR="/sessions/keen-charming-hypatia/mnt/.claude/projects/-Users-peter-Library-Application-Support-Claude-local-agent-mode-sessions-add4cb4c-ea1e-402a-94dc-95fef2a8a1da-a3f85abe-537c-4d9f-9d6d-83586c51feaa-local-d5a1282f-3c6b-4688-a451-0af4ebb90a18-outputs/3da1a630-a4eb-4154-88d7-0c76099450a7/tool-results"
OK={'blue':'#0072B2','orange':'#E69F00','red':'#D55E00','grey':'#999999'}

# ---- parse state polygons ----
def latest(glob_pat, needle):
    import glob
    for p in sorted(glob.glob(os.path.join(TR,glob_pat)),key=os.path.getmtime,reverse=True):
        t=open(p).read()
        if needle in t[:400] or needle in t[:5000]: return t
    return None
raw=open(os.path.join(TR,"mcp-mcp-okn-sparql_query-1784792058144.txt")).read()
text=json.loads(raw)['text']
rows=list(csv.reader(io.StringIO(text)))
seen={}
for r in rows[1:]:
    if len(r)<2: continue
    f,w=r[0],r[1]
    if f in seen: continue
    try: seen[f]=shwkt.loads(w)
    except Exception: pass
states=gpd.GeoDataFrame({'state_fips':list(seen.keys())},geometry=list(seen.values()),crs="EPSG:4326").to_crs(5070)
states['geometry']=states.geometry.simplify(2000)
print("state polygons:",len(states))

# state_fips -> stateName from county_dim
dim=pd.read_csv(f"{D}/county_dim.csv",dtype={'fips':str}); dim['state_fips']=dim['fips'].str[:2]
sf2name=dim.dropna(subset=['stateName']).drop_duplicates('state_fips').set_index('state_fips')['stateName'].to_dict()
states['stateName']=states['state_fips'].map(sf2name)
st=pd.read_csv(f"{D}/state_rollup.csv")
states=states.merge(st,on='stateName',how='left')

# ---- Fig 4: state choropleth ----
fig,ax=plt.subplots(figsize=(9.4,6.0))
states.plot(ax=ax,column='mean_consensus',cmap='YlOrRd',edgecolor='white',linewidth=0.5,
            legend=True,legend_kwds={'label':'Mean consensus burden (0–6)','shrink':0.6},
            missing_kwds={'color':'#eeeeee','label':'no data'},vmin=0)
ax.set_xlim(-2350000,2300000); ax.set_ylim(250000,3200000)  # CONUS extent (Albers)
ax.set_axis_off(); ax.set_title("Mean county environmental–social burden by state")
ax.annotate("Boundaries: spatialkg AdministrativeRegion_1 geometries · contiguous U.S. · Albers EPSG:5070",
            xy=(0.5,-0.02),xycoords='axes fraction',ha='center',fontsize=7,color='#666')
F.finalize(fig,4,f"{FIG}/fig4_state_map.png")

# ---- Fig 5: state boundaries + hotspot county points ----
cen=pd.read_csv(f"{D}/county_centroids.csv",dtype={'fips':str})
m=pd.read_csv(f"{D}/master_county.csv",dtype={'fips':str})
h=m.merge(cen,on='fips')
pts=gpd.GeoDataFrame(h,geometry=gpd.points_from_xy(h['lon'],h['lat']),crs="EPSG:4326").to_crs(5070)
fig,ax=plt.subplots(figsize=(9.4,6.0))
states.plot(ax=ax,color='#f2f2f2',edgecolor='#bcbcbc',linewidth=0.5)
sizes=35+pts['mismatch_index'].clip(lower=0).fillna(0).values*16
sc=ax.scatter(pts.geometry.x,pts.geometry.y,s=sizes,c=pts['consensus'],cmap='YlOrRd',
              vmin=0,vmax=6,edgecolor='#333',linewidth=0.5,zorder=5)
ax.set_xlim(-2350000,2300000); ax.set_ylim(250000,3200000)  # CONUS extent (Albers)
ax.set_axis_off(); ax.set_title("Highest-burden & greatest-mismatch counties (size ∝ burden↔service mismatch)")
plt.colorbar(sc,ax=ax,label="Consensus burden (0–6)",shrink=0.6)
ax.annotate("State boundaries: spatialkg geometries · county centroids: spatialkg AdministrativeRegion_2 WKT · Albers EPSG:5070",
            xy=(0.5,-0.02),xycoords='axes fraction',ha='center',fontsize=7,color='#666')
F.finalize(fig,5,f"{FIG}/fig5_county_hotspots.png")
print("regenerated fig4 + fig5 as polygon maps")

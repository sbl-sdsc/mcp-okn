import json
import shapely.wkt as swkt
import geopandas as gpd
F="/sessions/cool-peaceful-ritchie/mnt/.claude/projects/-Users-peter-Library-Application-Support-Claude-local-agent-mode-sessions-add4cb4c-ea1e-402a-94dc-95fef2a8a1da-a3f85abe-537c-4d9f-9d6d-83586c51feaa-local-c7cfba1c-ec68-4427-9cfe-31d478a8d42c-outputs/010cd1ec-89c7-4b99-a7b0-f408ca7eab4a/tool-results/toolu_0194obr8VoBFD9WbtpZRDNyH.json"
raw=json.load(open(F)); data=json.loads(raw[0]['text']); rows=data['rows']
recs=[]
for r in rows:
    try: geom=swkt.loads(r['wkt'])
    except Exception: continue
    recs.append(dict(county_FIPS=r['county_FIPS'],label=r.get('label'),
                     geometry=geom.simplify(0.01,preserve_topology=True)))
gdf=gpd.GeoDataFrame(recs,crs='EPSG:4326')
gdf.to_file('data/counties_simplified.geojson',driver='GeoJSON')
print('rows',len(rows),'geoms',len(gdf))

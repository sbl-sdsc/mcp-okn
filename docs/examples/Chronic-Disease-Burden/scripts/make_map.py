"""Interactive folium county choropleth with a variable drop-down (one GeoJson layer + setStyle).

Usage: python scripts/make_map.py <county_burden_ranked.tsv> <counties_geojson> <out_fragment.html>
Writes an <iframe srcdoc> fragment (folium_map_iframe) to embed in the HTML report.
"""
import json
import sys
import os

import folium
import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okn_figstyle as F  # noqa: E402
import analysis as A  # noqa: E402

tsv, geo_path, out = sys.argv[1:4]
m = pd.read_csv(tsv, sep="\t", dtype={"fips": str})
g = gpd.read_file(geo_path)
g["fips"] = g["id"].astype(str).str.zfill(5)
g = g.merge(m, on="fips", how="left")
g = g[~g["fips"].str[:2].isin(["72"])]  # drop Puerto Rico (outside PLACES scope here)
g["name"] = g["name"].fillna(g["NAME"] + " (no PLACES data)")
g["tier"] = g["tier"].fillna("n/a")
g["geometry"] = g.geometry.simplify(0.01, preserve_topology=True)

VARS = [("burden_z", "Composite burden score (mean z)")] + [(k, A.LABEL[k] + " (%)") for k in A.DKEYS] + [
    ("n_top_quintile", "Conditions in top quintile (0–9)")]
props = ["fips", "name", "tier", "pop_places"] + [v for v, _ in VARS]
for v, _ in VARS:
    g[v] = g[v].astype(float).round(2)
gj = json.loads(g[props + ["geometry"]].to_json())
breaks = {v: [float(x) for x in np.nanquantile(g[v], [0.2, 0.4, 0.6, 0.8])] for v, _ in VARS}
breaks["n_top_quintile"] = [1, 3, 5, 7]
COLORS = ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]

fm = folium.Map(location=[38.5, -96], zoom_start=4, tiles=F.BASEMAP_TILES, attr=F.BASEMAP_ATTR, control_scale=True)
layer = folium.GeoJson(
    gj, name="counties",
    style_function=lambda f: {"fillColor": "#cccccc", "color": "#666", "weight": 0.2, "fillOpacity": 0.75},
    highlight_function=lambda f: {"weight": 1.5, "color": "#000"},
    tooltip=folium.GeoJsonTooltip(fields=["name", "burden_z", "tier"], aliases=["County", "Composite z", "Tier"]),
    popup=folium.GeoJsonPopup(fields=props[1:], aliases=["County", "Tier", "Pop. in PLACES places"] + [l for _, l in VARS]),
).add_to(fm)
lname, mname = layer.get_name(), fm.get_name()
opts = "".join(f'<option value="{v}">{l}</option>' for v, l in VARS)
ctrl = f"""
<div id="ctrl" style="position:absolute;top:10px;right:10px;z-index:9999;background:white;padding:8px 10px;
 border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,.3);font:12px sans-serif;max-width:250px">
 <b>Map variable</b><br><select id="varsel" style="margin:4px 0;font-size:12px;max-width:230px">{opts}</select>
 <div id="leg"></div><div style="color:#555;margin-top:4px">Quintile classes · grey = no PLACES data
 (incl. all of Florida). Click a county for all values.</div></div>
<script>
(function(){{
 var B={json.dumps(breaks)}, C={json.dumps(COLORS)}, L={json.dumps(dict(VARS))};
 function col(v,b){{ if(v===null||v===undefined||isNaN(v)) return '#cccccc';
   for(var i=0;i<b.length;i++){{ if(v<=b[i]) return C[i]; }} return C[4]; }}
 function apply(){{
   var k=document.getElementById('varsel').value, b=B[k];
   {lname}.setStyle(function(f){{return {{fillColor:col(f.properties[k],b),color:'#666',weight:0.2,fillOpacity:0.75}};}});
   var h='<div style="margin-top:4px">'+L[k]+'</div>', lo='min';
   for(var i=0;i<5;i++){{ var hi=(i<4)?b[i].toFixed(2):'max';
     h+='<div><span style="display:inline-block;width:14px;height:10px;background:'+C[i]+';margin-right:5px"></span>'+lo+' – '+hi+'</div>';
     lo=(i<4)?b[i].toFixed(2):''; }}
   document.getElementById('leg').innerHTML=h; }}
 document.getElementById('varsel').addEventListener('change',apply);
 var t=setInterval(function(){{ if(typeof {lname}!=='undefined'){{ clearInterval(t); apply(); }} }},100);
}})();
</script>"""
fm.get_root().html.add_child(folium.Element(ctrl))
frag = F.folium_map_iframe(fm, height=620, title="Interactive county chronic-disease map")
open(out, "w").write(frag)
print(out, round(len(frag) / 1e6, 2), "MB")

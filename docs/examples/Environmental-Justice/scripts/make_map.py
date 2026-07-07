#!/usr/bin/env python3
"""Build a self-contained OpenStreetMap-based county choropleth of cumulative EJ burden.

Burden data = Proto-OKN (master_county.csv). County polygons = us-atlas TopoJSON fetched
client-side from a CDN (cartographic base only); OSM tile layer as basemap.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = "/sessions/amazing-focused-bardeen/mnt/outputs"
m = pd.read_csv(OUT + "/master_county.csv", dtype={"fips": str})
m = m[m["in_us50"]]
B = {}
for _, r in m.iterrows():
    idx = r["burden_index"]
    if pd.isna(idx):
        continue

    def g(k, nd=1, r=r):
        """Return county field ``k`` from row ``r``, rounded or int-cast, else None."""
        v = r.get(k)
        return None if pd.isna(v) else (round(float(v), nd) if nd else int(v))

    B[r["fips"]] = [
        round(float(idx), 3),
        (int(r["burden_agreement"]) if pd.notna(r["burden_agreement"]) else None),
        str(r["name"]),
        str(r["state"]),
        g("epa_fac", 0),
        g("court_cases", 0),
        g("svi", 3),
        g("rucc", 0),
        g("poverty", 1),
        g("sud_providers", 0),
    ]
brk = np.round(
    m["burden_index"].quantile([0.15, 0.35, 0.55, 0.7, 0.82, 0.92]).values, 3
).tolist()
data = json.dumps(B, separators=(",", ":"))
html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Cumulative Environmental-Justice Burden by U.S. County — Proto-OKN</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
 html,body{{margin:0;height:100%;font-family:'Segoe UI',system-ui,sans-serif}}
 #map{{height:100%;width:100%;background:#aad3df}}
 .panel{{position:absolute;top:10px;right:10px;z-index:1000;background:rgba(255,255,255,.94);
   padding:12px 14px;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.3);max-width:290px;font-size:12.5px}}
 .panel h3{{margin:0 0 4px;font-size:14.5px}} .panel .sub{{color:#555;font-size:11px;margin-bottom:8px}}
 .legend i{{width:16px;height:16px;float:left;margin-right:6px;opacity:.85}}
 .legend div{{clear:both;line-height:18px}}
 .info{{position:absolute;bottom:14px;left:10px;z-index:1000;background:rgba(255,255,255,.94);
   padding:9px 12px;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.3);max-width:330px;font-size:12px;min-height:34px}}
 .cred{{position:absolute;bottom:0;right:0;z-index:1000;background:rgba(255,255,255,.8);font-size:9.5px;padding:2px 6px;color:#444}}
</style></head><body>
<div id="map"></div>
<div class="panel"><h3>Cumulative EJ Burden by County</h3>
 <div class="sub">Composite of 5 Proto-OKN stressor percentiles: EPA facilities, social vulnerability, federal-court activity, rurality, treatment-service scarcity. 1 = highest burden.</div>
 <div class="legend" id="legend"></div></div>
<div class="info" id="info">Hover a county for its burden profile.</div>
<div class="cred">Burden data: Proto-OKN KGs (spoke-okn/fiokg/scales/ruralkg) · polygons: us-atlas · basemap: © OpenStreetMap</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js"></script>
<script>
var B={data};
var brk={brk};
var colors=['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#f03b20','#bd0026'];
function col(v){{ if(v==null) return '#e0e0e0';
  for(var i=0;i<brk.length;i++){{ if(v<brk[i]) return colors[i]; }} return colors[colors.length-1]; }}
var map=L.map('map',{{center:[38,-96],zoom:5,minZoom:4,maxZoom:12,worldCopyJump:false}});
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
  {{attribution:'© OpenStreetMap contributors',opacity:0.55}}).addTo(map);
var info=document.getElementById('info');
function show(p){{ var b=B[p]; if(!b){{info.innerHTML='<b>FIPS '+p+'</b> — no Proto-OKN burden data';return;}}
  info.innerHTML='<b>'+b[2]+', '+b[3]+'</b> (FIPS '+p+')<br>'+
   'Burden index <b>'+b[0]+'</b> · sources flagged <b>'+(b[1]==null?'–':b[1])+'/5</b><br>'+
   'EPA facilities: '+(b[4]==null?'–':b[4])+' · Fed. court cases: '+(b[5]==null?'–':b[5])+'<br>'+
   'SVI: '+(b[6]==null?'–':b[6])+' · RUCC: '+(b[7]==null?'–':b[7])+' · Poverty: '+(b[8]==null?'–':b[8]+'%')+
   ' · SUD providers: '+(b[9]==null?'0/none':b[9]); }}
function style(f){{ var b=B[f.id]; return {{fillColor:col(b?b[0]:null),weight:0.3,color:'#666',
   fillOpacity:b?0.78:0.25}}; }}
function onEach(f,l){{ l.on({{mouseover:function(e){{e.target.setStyle({{weight:1.6,color:'#111'}});e.target.bringToFront();show(f.id);}},
  mouseout:function(e){{gj.resetStyle(e.target);}},
  click:function(e){{show(f.id);map.fitBounds(e.target.getBounds());}} }}); }}
var gj;
fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json').then(r=>r.json()).then(function(us){{
  var geo=topojson.feature(us,us.objects.counties);
  gj=L.geoJSON(geo,{{style:style,onEachFeature:onEach}}).addTo(map);
  // state borders
  var st=topojson.mesh(us,us.objects.states,function(a,b){{return a!==b;}});
  L.geoJSON(st,{{style:{{color:'#333',weight:0.9,fill:false}}}}).addTo(map);
}});
var lg=document.getElementById('legend'); var lb=[0].concat(brk);
for(var i=0;i<colors.length;i++){{ var a=lb[i], z=(i<brk.length?brk[i]:1);
  lg.innerHTML+='<div><i style="background:'+colors[i]+'"></i>'+a.toFixed(2)+' – '+z.toFixed(2)+'</div>'; }}
lg.innerHTML+='<div><i style="background:#e0e0e0"></i>no data</div>';
</script></body></html>"""
Path(OUT + "/report/choropleth_burden.html").write_text(html)
print("map written; counties embedded:", len(B), "| breaks:", brk)

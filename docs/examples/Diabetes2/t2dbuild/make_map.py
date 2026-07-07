#!/usr/bin/env python3
"""Standalone interactive OpenStreetMap of U.S. state diabetes prevalence (Leaflet + OSM tiles)."""

import json
from pathlib import Path

OUT = str(Path(__file__).resolve().parent)
PREV = json.loads(Path(f"{OUT}/map_state_prevalence.json").read_text())
PREVJS = json.dumps(PREV, separators=(",", ":"))
html = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Type 2 Diabetes Prevalence — OpenStreetMap</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html,body{margin:0;height:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif}
#bar{position:absolute;top:0;left:0;right:0;z-index:1000;background:linear-gradient(135deg,#123,#2E86AB);color:#fff;padding:10px 16px}
#bar h1{margin:0;font-size:16px} #bar p{margin:2px 0 0;font-size:12px;opacity:.9}
#map{position:absolute;top:52px;bottom:0;left:0;right:0}
.legend{background:#fff;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.3);font-size:12px;line-height:1.7}
.legend i{display:inline-block;width:14px;height:14px;margin-right:6px;border-radius:3px;vertical-align:-2px}
</style></head><body>
<div id="bar"><h1>Type 2 Diabetes — age-adjusted prevalence by U.S. state</h1>
<p>CDC PLACES via Proto-OKN <code>spoke-okn</code> · basemap © OpenStreetMap contributors · marker size &amp; colour ∝ prevalence · click for detail</p></div>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const PREV=__PREV__;
function col(v){return v>=13?'#7f0000':v>=12?'#b30000':v>=11?'#d7301f':v>=10?'#ef6548':v>=9?'#fc8d59':v>=8?'#fdbb84':'#fdd49e';}
const map=L.map('map').setView([39.5,-96],4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:12,attribution:'© OpenStreetMap contributors'}).addTo(map);
PREV.forEach(p=>{ if(p.lat==null)return;
  L.circleMarker([p.lat,p.lng],{radius:6+(p.prev-7)*2.4,fillColor:col(p.prev),color:'#222',weight:1,fillOpacity:.85})
   .addTo(map).bindPopup('<b>'+p.name+'</b><br>Age-adjusted diabetes prevalence: <b>'+p.prev.toFixed(1)+'%</b>')
   .bindTooltip(p.state+' '+p.prev.toFixed(1)+'%',{permanent:false});});
const lg=L.control({position:'bottomright'});
lg.onAdd=function(){const d=L.DomUtil.create('div','legend');d.innerHTML='<b>Diabetes prevalence</b><br>'+
 '<i style="background:#7f0000"></i>≥13%<br><i style="background:#d7301f"></i>11–13%<br>'+
 '<i style="background:#fc8d59"></i>9–11%<br><i style="background:#fdd49e"></i>&lt;9%';return d;};
lg.addTo(map);
</script></body></html>"""
Path(f"{OUT}/T2D_prevalence_map.html").write_text(html.replace("__PREV__", PREVJS))
print("wrote T2D_prevalence_map.html")

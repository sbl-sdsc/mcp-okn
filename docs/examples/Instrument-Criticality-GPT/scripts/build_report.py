#!/usr/bin/env python3
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DATA=ROOT/"data"
sys.path.insert(0,str(HERE))
from okn_figstyle import folium_osm_map, folium_map_iframe, save_map_html
from build_report_html import candidate_table, build_report_from_markdown, kpis_from_stats

def read(name):
    return json.loads((DATA/name).read_text())

stats=read("analysis_stats.json")
ranked=[r for r in read("ranked_instruments.json") if r.get("specificity")=="named instrument"]
countries=read("country_attention.json")

# Correct a few bounding-box midpoints that are distorted by overseas territories or the dateline.
centroid_overrides={
    "US":(39.8,-98.6),"GB":(54.0,-2.0),"FR":(46.2,2.2),"RU":(61.5,105.3),
    "CA":(56.1,-106.3),"AU":(-25.3,133.8),"CN":(35.9,104.2),"DE":(51.2,10.4),
    "IN":(20.6,78.9),"JP":(36.2,138.3),"AQ":(-82.0,0.0)
}
map_rows=[]
for r in sorted(countries,key=lambda x:float(x.get("instrument_model_papers") or 0),reverse=True):
    if float(r.get("instrument_model_papers") or 0)<=0:
        continue
    lat=float(r["latitude"]); lon=float(r["longitude"])
    if r.get("iso") in centroid_overrides:
        lat,lon=centroid_overrides[r["iso"]]
    map_rows.append({
        "country":r["country_name"],"iso":r.get("iso",""),"lat":lat,"lon":lon,
        "all papers":int(r.get("papers",0)),"model papers":int(r.get("model_papers",0)),
        "model + instrument papers":int(r.get("instrument_model_papers",0)),
        "distinct model sources":int(r.get("models",0)),
        "evidence":("thin (<3)" if int(r.get("instrument_model_papers",0))<3 else "represented")
    })
m=folium_osm_map(map_rows,lat_key="lat",lon_key="lon",
                 popup_keys=["country","iso","all papers","model papers","model + instrument papers","distinct model sources","evidence"],
                 value_key="model + instrument papers",tooltip_key="country",zoom_start=2,radius=3)
save_map_html(m,ROOT/"figures"/"interactive_country_attention_map.html")
iframe=folium_map_iframe(m,height=560,title="Country-level research-attention proxy")

template=(DATA/"Instrument-Criticality-GPT_report.template.md").read_text()
md=template.replace("<!-- INTERACTIVE_MAP -->","[Open the interactive OSM map](figures/interactive_country_attention_map.html)")
report=ROOT/"Instrument-Criticality-GPT_report.md"
report.write_text(md)

for r in ranked:
    r["route_names"]=[x.strip() for x in str(r.get("routes","")).split("|") if x.strip()]
    r["score"]=r.get("criticality_score")
    r["datasets"]=r.get("space_dataset_count")
    r["eval"]=r.get("evaluation_models")
    r["doi"]=r.get("doi_models")
    r["platform_text"]=r.get("platform_text_models")
    r["text"]=r.get("text_models")
    r["unique_vars"]="n/a" if r.get("unique_variable_count") is None else r.get("unique_variable_count")
    r["platform_list"]=r.get("platforms","")
table=candidate_table(
    ranked,
    columns=[
        ("rank","Rank"),("instrument_name","Instrument"),("score","Score"),("tier","Tier"),
        ("route_count","Evidence routes"),("eval","Eval models"),("doi","DOI models"),
        ("platform_text","Platform-text models"),("text","Instrument-text models"),
        ("unique_vars","Unique vars"),("datasets","Dataset footprint"),("platform_list","Platforms")
    ],
    search_keys=["instrument_name","tier","platform_list","routes"],
    numeric_keys=["rank","score","route_count","eval","doi","platform_text","text","datasets"],
    page_size=25,default_sort="rank",extra_filters=[("tier","Tier"),("model_uptake","Measured uptake")],
    sources_col=("route_count","route_names")
)
kpis=kpis_from_stats(stats,[
    ("space_instruments","spaceborne instruments"),
    ("instruments_with_any_uptake","with measured uptake"),
    ("exact_people_orcids","cross-community ORCIDs"),
    ("top_score","top score",".1f")
])
html_path=ROOT/"Instrument-Criticality-GPT_report.html"
build_report_from_markdown(
    report,html_path,kpis=kpis,table=table,stats=stats,
    title="Instrument-Criticality",
    subtitle="What climate modelling would stop being able to check if observing infrastructure went dark"
)
# Add the self-contained map after the Markdown/HTML parity check. The Markdown keeps
# a portable link to the same standalone map; the HTML upgrades that link to the iframe.
page=html_path.read_text()
needle='<p><code>Open the interactive OSM map</code></p>'
if needle not in page:
    raise RuntimeError("interactive-map link marker was not rendered as expected")
html_path.write_text(page.replace(needle,iframe))
print("report and interactive map built")

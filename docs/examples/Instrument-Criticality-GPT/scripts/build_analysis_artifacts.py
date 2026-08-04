#!/usr/bin/env python3
import json, math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
import sys
sys.path.insert(0, str(HERE))
from okn_figstyle import apply_style, finalize

def read(name):
    return json.loads((DATA / name).read_text())

def num(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0

stats = read("analysis_stats.json")
ranked = [r for r in read("ranked_instruments.json") if r.get("specificity") == "named instrument"]
ptypes = read("platform_types.json")
people = read("cross_side_people.json")
countries = read("country_attention.json")
archives = read("catalog_archives.json")

stats.update({
    "nasa_datasets": 8058,
    "nasa_instruments": 921,
    "nasa_platforms": 455,
    "nasa_archives": 189,
    "nasa_publications": 457085,
    "climate_papers": 2000,
    "climate_models": 110,
    "climate_observational_datasets": 2521,
    "space_name_matches": 82,
    "space_matches_with_variables": 30,
    "direct_dataset_instrument_links": 0,
    "platforms_with_start_date": 0,
    "platforms_with_end_date": 0,
    "matched_doi_papers": 651,
    "exact_name_overlap_people_upper_bound": 8391,
    "country_mentions": len(countries),
    "top_archive": max(archives, key=lambda x: num(x.get("dataset_count")))["center_name"],
    "top_archive_datasets": int(max(num(a.get("dataset_count")) for a in archives)),
    "evaluation_route_instruments": sum(1 for r in ranked if num(r.get("evaluation_models")) > 0),
    "doi_route_instruments": sum(1 for r in ranked if num(r.get("doi_models")) > 0),
    "platform_text_route_instruments": sum(1 for r in ranked if num(r.get("platform_text_models")) > 0),
    "text_route_instruments": sum(1 for r in ranked if num(r.get("text_models")) > 0),
})
(DATA / "analysis_stats.json").write_text(json.dumps(stats, indent=2) + "\n")

apply_style()

# Figure 1: catalogue scale and coverage.
fig = plt.figure(figsize=(15.5, 5.2))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.45, 1.0], wspace=0.68)
ax = fig.add_subplot(gs[0,0])
names = ["Datasets", "Instruments", "Platforms", "Archives"]
vals = [8058, 921, 455, 189]
bars=ax.bar(names, vals, color=["#3366CC","#5B8FF9","#8DB4E2","#B8CCE4"])
ax.set_yscale("log"); ax.set_ylabel("Catalogue count (log scale)"); ax.tick_params(axis="x", rotation=28)
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v*1.10,f"{v:,}",ha="center",fontsize=9)
ax.set_title("A  NASA observation catalogue")

ax = fig.add_subplot(gs[0,1])
good=[p for p in ptypes if p.get("platform_type")]
good=sorted(good,key=lambda x:num(x.get("datasets")),reverse=True)[:9][::-1]
ax.barh([p["platform_type"] for p in good],[num(p["datasets"]) for p in good],color="#5B8FF9")
ax.set_xlabel("Datasets linked to platform type")
ax.set_title("B  Shape of the platform catalogue")

ax = fig.add_subplot(gs[0,2])
labs=["Spaceborne instruments","Exact climate-KG name matches","With variable semantics"][::-1]
vv=[288,82,30][::-1]
bars=ax.barh(labs,vv,color=["#59A14F","#F28E2B","#3366CC"])
ax.set_xlabel("Instrument count"); ax.set_title("C  Cross-graph evidence funnel")
for b,v in zip(bars,vv): ax.text(v+5,b.get_y()+b.get_height()/2,str(v),va="center",fontsize=10)
finalize(fig,1,FIG/"fig1_catalogue_scale.png")

# Figure 2: route-specific model support.
top=sorted(ranked,key=lambda r:num(r.get("criticality_score")),reverse=True)[:15][::-1]
route_cols=[("evaluation_models","Evaluation-context text"),("doi_models","DOI + dataset/platform"),("platform_text_models","Platform text"),("text_models","Instrument text")]
fig,ax=plt.subplots(figsize=(11.5,7.2))
y=np.arange(len(top)); h=0.18
colors=["#3366CC","#59A14F","#F28E2B","#B07AA1"]
for j,((k,label),c) in enumerate(zip(route_cols,colors)):
    ax.barh(y+(j-1.5)*h,[num(r.get(k)) for r in top],height=h,label=label,color=c)
ax.set_yticks(y); ax.set_yticklabels([r["instrument_name"] for r in top])
ax.set_xlabel("Distinct climate-model sources linked by route")
ax.set_title("Independent routes agree on leaders, but not on magnitude")
ax.legend(loc="lower center",bbox_to_anchor=(0.5,-0.20),ncol=2,frameon=False)
finalize(fig,2,FIG/"fig2_dependency_routes.png")

# Figure 3: score versus footprint, with risk classes.
fig,ax=plt.subplots(figsize=(11.5,7.0))
for label,color,selector in [
    ("Measured modelling uptake","#3366CC",lambda r:num(r.get("union_models"))>0),
    ("No measured uptake","#B8B8B8",lambda r:num(r.get("union_models"))==0),
]:
    rows=[r for r in ranked if selector(r)]
    ax.scatter([max(1,num(r.get("space_dataset_count"))) for r in rows],[num(r.get("criticality_score")) for r in rows],
               s=36,alpha=.72,color=color,label=label,edgecolors="white",linewidths=.3)
ax.set_xscale("log"); ax.set_xlabel("Platform-mediated dataset count (upper bound; log scale)")
ax.set_ylabel("Evidence-based criticality score (0–100)")
ax.set_title("Data footprint and model dependence are related—but not interchangeable")
labels={"MODIS","AMSR-E","SSMIS","SMMR","ACE-FTS","CERES SCANNER","VIIRS","GOME-2","AQUARIUS_RADIOMETER"}
for r in ranked:
    if str(r.get("instrument_name","")).upper() in labels or r.get("instrument_name") in labels:
        ax.annotate(r["instrument_name"],(max(1,num(r.get("space_dataset_count"))),num(r.get("criticality_score"))),
                    xytext=(5,5),textcoords="offset points",fontsize=8)
ax.legend(loc="lower center",bbox_to_anchor=(0.5,-0.16),ncol=2,frameon=False)
finalize(fig,3,FIG/"fig3_risk_distribution.png")

# Figure 4: people and geographic attention.
fig=plt.figure(figsize=(13.5,5.6)); gs=fig.add_gridspec(1,2,wspace=.46)
ax=fig.add_subplot(gs[0,0])
pp=sorted(people,key=lambda r:(num(r.get("models")),num(r.get("shared_doi_papers"))),reverse=True)[:12][::-1]
ax.barh([p["author_name"] for p in pp],[num(p.get("models")) for p in pp],color="#59A14F")
ax.set_xlabel("Distinct model sources on exact DOI-matched papers"); ax.set_title("A  People spanning observation and modelling")
ax=fig.add_subplot(gs[0,1])
cc=sorted(countries,key=lambda r:num(r.get("instrument_model_papers")),reverse=True)[:15][::-1]
ax.barh([c["country_name"] for c in cc],[num(c.get("instrument_model_papers")) for c in cc],color="#F28E2B")
ax.set_xlabel("Model + instrument papers mentioning country"); ax.set_title("B  Country-attention proxy")
finalize(fig,4,FIG/"fig4_people_places.png")
print("analysis artifacts built")

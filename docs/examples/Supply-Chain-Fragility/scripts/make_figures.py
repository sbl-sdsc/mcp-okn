#!/usr/bin/env python3
"""Figures for the Supply-Chain-Fragility OKN study."""
import json, sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from okn_figstyle import (apply_style, panel_title, legend_outside, ranked_barh,
                          finalize, osm_basemap, UP, DOWN, NEUTRAL, FONT)

R = Path(__file__).resolve().parent.parent
D, F = R/"data", R/"figures"
apply_style()
OK = ["#0072B2","#D55E00","#009E73","#CC79A7","#E69F00","#56B4E9","#F0E442","#999999"]

M    = pd.read_csv(D/"industry_master.csv", dtype={"naics":str})
ind  = pd.read_csv(D/"sudokn_industry_national.csv", dtype={"naics":str})
age  = pd.read_csv(D/"sudokn_firm_age.csv")
sw   = pd.read_csv(D/"software_fragility_scored.csv")
ist  = pd.read_csv(D/"industrial_stack.csv")
cl   = pd.read_csv(D/"software_restrictive_licences.csv")
st   = pd.read_csv(D/"state_burden_vs_employment.csv", dtype={"stateFips":str})
pc   = pd.read_csv(D/"county_burden_percapita.csv", dtype={"fips":str})
cnt  = pd.read_csv(D/"county_burden_count.csv", dtype={"fips":str})
smmc = pd.read_csv(D/"county_smm_employment.csv", dtype={"fips":str})
sdp  = pd.read_csv(D/"sdoh_by_intensity_percapita.csv")
sds  = pd.read_csv(D/"sdoh_by_intensity_share.csv")
slc  = pd.read_csv(D/"shortlist_counties.csv", dtype={"naics":str,"fips":str})
cen  = pd.read_csv(D/"county_centroids.csv", dtype={"fips":str})
S    = json.load(open(D/"stats_numeric.json"))

def short(lbl, n=30):
    return lbl if len(lbl) <= n else lbl[:n-1]+"…"

# ---------------------------------------------------------------- Figure 1
fig = plt.figure(figsize=(13.2, 6.0))
gs  = fig.add_gridspec(1, 2, width_ratios=[1.42, 1.0], wspace=0.42)
ax = fig.add_subplot(gs[0, 0]); ax.set_axis_off()
panel_title(ax, "A", "how the three layers are joined")
boxes = {
 "sudokn":   (0.06, 0.72, "sudokn\nSMM capacity\n15,571 firms", OK[0]),
 "fiokg":    (0.06, 0.44, "fiokg\nEPA FRS facilities\n27,200 in NAICS 332", OK[1]),
 "secure":   (0.06, 0.16, "securechainkg\n803,769 packages\n29.6M dependsOn", OK[3]),
 "naics":    (0.44, 0.58, "NAICS 332xxx\nindustry key\n(36 codes)", NEUTRAL),
 "geo":      (0.44, 0.30, "county FIPS\n+ ZIP5 crosswalk\n(1,705 counties)", NEUTRAL),
 "spatial":  (0.78, 0.72, "spatialkg\ncounty / state\nadmin regions", OK[2]),
 "spoke":    (0.78, 0.44, "spoke-okn\n84 county SDoH\nvariables", OK[4]),
 "rural":    (0.78, 0.16, "ruralkg\nRUCC + county\npopulation", OK[5]),
}
for k,(x,y,t,c) in boxes.items():
    ax.add_patch(FancyBboxPatch((x,y), 0.19, 0.19, boxstyle="round,pad=0.012",
                 linewidth=1.4, edgecolor=c, facecolor=c+"22", transform=ax.transAxes))
    ax.text(x+0.095, y+0.095, t, ha="center", va="center", fontsize=8.0,
            transform=ax.transAxes)
def arrow(a, b, style="-|>", ls="-", col="#555"):
    (x1,y1,_,_), (x2,y2,_,_) = boxes[a], boxes[b]
    ax.add_patch(FancyArrowPatch((x1+0.19, y1+0.095), (x2, y2+0.095),
        arrowstyle=style, linestyle=ls, color=col, mutation_scale=11,
        linewidth=1.2, transform=ax.transAxes, shrinkA=2, shrinkB=2))
for a in ("sudokn","fiokg","secure"): arrow(a, "naics")
arrow("sudokn","geo"); arrow("fiokg","geo")
for b in ("spatial","spoke","rural"): arrow("geo", b)
ax.text(0.62, 0.10, "no KG edge joins the software\ndependency graph to NAICS\n(name bridge only, 20 firms)",
        ha="center", va="center", fontsize=7.6, color=OK[1], style="italic",
        transform=ax.transAxes)
ax.add_patch(FancyArrowPatch((0.25,0.255),(0.44,0.20), arrowstyle="-|>", linestyle=":",
    color=OK[1], mutation_scale=11, linewidth=1.4, transform=ax.transAxes))

ax = fig.add_subplot(gs[0, 1])
panel_title(ax, "B", "records reaching the analysis")
lay = ["SMM firms","… placed in a county","EPA facilities\nNAICS 332",
       "counties w/ a\nNAICS-332 facility","packages / 100\n(securechainkg)",
       "pkgs w/ maintainer\ndata"]
val = [S["smm_firms_total"], S["smm_firms_placed"], S["frs_facilities_332"],
       S["frs_counties_332"], S["sw_packages"]//100, S["sw_pkgs_with_contributors"]]
cols = [OK[0],OK[0],OK[1],OK[1],OK[3],OK[3]]
y = np.arange(len(lay))
ax.barh(y, val, color=cols); ax.set_yticks(y); ax.set_yticklabels(lay, fontsize=7.6)
ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlabel("records (log scale)")
for i,v in enumerate(val):
    ax.text(v*1.15, i, f"{v:,}", va="center", fontsize=7.4, color="#333")
ax.set_xlim(right=max(val)*9)
finalize(fig, 1, F/"fig1_design_and_coverage.png")

# ---------------------------------------------------------------- Figure 2
fig, axes = plt.subplots(1, 3, figsize=(14.2, 5.3), gridspec_kw={"wspace":0.42,
                          "width_ratios":[1.5,1.0,1.0]})
ax = axes[0]; panel_title(ax, "A", "largest SMM industries (NAICS 332)")
t = ind.merge(M[["naics","label"]], on="naics").nlargest(14, "firms")
y = np.arange(len(t))
ax.barh(y-0.2, t.firms, height=0.4, color=OK[0], label="firms")
ax.barh(y+0.2, t.empSum/20, height=0.4, color=OK[4], label="employees / 20")
ax.set_yticks(y); ax.set_yticklabels([short(l,32) for l in t.label], fontsize=7.4)
ax.invert_yaxis(); ax.set_xlabel("count")
legend_outside(ax, where="below", ncol=2)

ax = axes[1]; panel_title(ax, "B", "firm founding decade")
ax.bar(range(len(age)), age.firms, color=NEUTRAL)
ax.set_xticks(range(len(age))); ax.set_xticklabels(age.decade, rotation=90, fontsize=7.2)
ax.set_ylabel("firms"); ax.set_xlabel("decade of establishment")
ax.text(0.03, 0.95, f"n={S['firms_with_year']:,} of {S['smm_firms_total']:,}\n({S['pct_firms_with_year']}% recorded)",
        transform=ax.transAxes, va="top", fontsize=7.6, color=OK[1])

ax = axes[2]; panel_title(ax, "C", "mean employees per firm")
t2 = M.dropna(subset=["empPerFirm"]).nlargest(14, "empPerFirm")
ax.barh(np.arange(len(t2)), t2.empPerFirm, color=OK[2])
ax.set_yticks(np.arange(len(t2))); ax.set_yticklabels([short(l,30) for l in t2.label], fontsize=7.2)
ax.invert_yaxis(); ax.set_xlabel("mean employees per firm")
finalize(fig, 2, F/"fig2_manufacturing_base.png")

# ---------------------------------------------------------------- Figure 3
fig, axes = plt.subplots(1, 3, figsize=(15.4, 5.2), gridspec_kw={"wspace":0.50,
                          "width_ratios":[1.15,1.25,1.0]})
ax = axes[0]; panel_title(ax, "A", "concentration vs observed firm base")
e = M[M.placed >= 20]
ax.scatter(e.placed, e.concIndex, s=34, c=[OK[1] if s else OK[0] for s in e.shortList],
           edgecolor="white", linewidth=0.6, zorder=3)
ax.axhline(1.0, color="#888", ls="--", lw=1.0)
ax.axhline(1.5, color=OK[1], ls=":", lw=1.0)
ax.set_xscale("log"); ax.set_xlabel("SMM firms placed in a county (log)")
ax.set_ylabel("concentration index (obs / expected HHI)")
offs = {"332996":(6,-10), "332811":(6,6), "332111":(6,4), "332919":(-30,4),
        "332911":(6,2), "332912":(6,2), "332913":(6,2), "332991":(6,2)}
for _, r in e.nlargest(8, "concIndex").iterrows():
    ax.annotate(r.naics, (r.placed, r.concIndex), fontsize=7.2,
                xytext=offs.get(r.naics,(6,3)), textcoords="offset points")
hl = [plt.Line2D([0],[0], marker="o", ls="", color=OK[1], label="short-listed"),
      plt.Line2D([0],[0], marker="o", ls="", color=OK[0], label="other")]
ax.text(0.03, 0.04, "dashed = sector-typical (1.0)\ndotted = concentrated threshold (1.5)",
        transform=ax.transAxes, fontsize=7.2, color="#555")

ax = axes[1]; panel_title(ax, "B", "effective number of counties")
t3 = e.nsmallest(14, "effCounties").sort_values("effCounties")
y = np.arange(len(t3))
ax.barh(y, t3.effCounties, color=[OK[1] if s else OK[0] for s in t3.shortList])
ax.set_yticks(y); ax.set_yticklabels([f"{n} {short(l,26)}" for n,l in zip(t3.naics,t3.label)], fontsize=7.2)
ax.axvline(1/0.00644361, color="#888", ls="--", lw=1.0)
ax.set_xlabel("1 / county HHI  (lower = more concentrated)")
ax.legend(handles=hl, loc="lower right", fontsize=7.2, frameon=False)
ax.text(1/0.00644361, len(t3)-0.4, " sector = 155", fontsize=7.2, color="#555", va="top")

ax = axes[2]; panel_title(ax, "C", "county vs state concentration")
ax.scatter(e.hhiState, e.hhiCounty, s=32, c=[OK[1] if s else OK[0] for s in e.shortList],
           edgecolor="white", linewidth=0.6)
ax.set_xlabel("state-grain HHI"); ax.set_ylabel("county-grain HHI")
ax.set_xscale("log"); ax.set_yscale("log")
lim = [min(e.hhiCounty.min(), e.hhiState.min())*0.8, e.hhiState.max()*1.2]
ax.plot(lim, lim, color="#888", ls="--", lw=1.0)
hl3 = hl + [plt.Line2D([0],[0], ls="--", color="#888",
            label="equal concentration at both grains")]
ax.legend(handles=hl3, loc="upper left", fontsize=7.0, frameon=False)
finalize(fig, 3, F/"fig3_geographic_concentration.png")

# ---------------------------------------------------------------- Figure 4 (map)
# OpenStreetMap raster tiles are unreachable from the analysis sandbox (the HTTP
# proxy blocks tile.openstreetmap.org), so the static basemap is built FROM THE
# FEDERATION instead: every county that hosts at least one NAICS-332 EPA facility
# is drawn as a faint grey dot at its ZIP-centroid-derived centre, which renders
# the coastline, the Great Lakes and the Plains gap.  The HTML report carries a
# genuine OSM-tiled interactive map of the same data (tiles load in the reader's
# browser).
base = pd.read_csv(D/"county_basemap_points.csv", dtype={"fips":str})
fig, ax = plt.subplots(figsize=(12.6, 7.6))
ax.scatter(base.lng, base.lat, s=6, color="#c9ced6", linewidth=0, zorder=1,
           label=f"county with >=1 NAICS-332 facility (n={len(base):,})")
mp = pc.merge(cen, on="fips")
sc = ax.scatter(mp.lng, mp.lat, s=26+mp.facPer100k*2.2, c=mp.facPer100k,
                cmap="YlOrRd", edgecolor="#333", linewidth=0.5, zorder=3,
                vmin=20, vmax=100)
cb = fig.colorbar(sc, ax=ax, shrink=0.62, pad=0.01)
cb.set_label("NAICS-332 facilities per 100,000 residents", fontsize=9)
lab_off = {"Brooke County":(-70,-16), "Elk County":(10,12), "Jefferson County":(14,-2),
           "DeKalb County":(-52,10), "Ouachita County":(8,-2), "Creek County":(-58,4),
           "Douglas County":(8,4), "Iberia Parish":(8,-10)}
for _, r in mp.nlargest(8, "facPer100k").iterrows():
    nm = r.county.split(",")[0]
    ax.annotate(nm, (r.lng, r.lat), fontsize=7.4,
                xytext=lab_off.get(nm,(6,4)), textcoords="offset points",
                arrowprops=dict(arrowstyle="-", lw=0.6, color="#666"),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
ax.set_xlim(-126, -66); ax.set_ylim(24, 50)
ax.set_aspect(1/np.cos(np.deg2rad(38)))
ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
ax.set_title("Where the fabricated-metal sector is the local economy", fontsize=12.5)
ax.legend(loc="lower left", fontsize=7.6, frameon=False, markerscale=2.2)
finalize(fig, 4, F/"fig4_intensity_map.png")

# ---------------------------------------------------------------- Figure 5
fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.6), gridspec_kw={"wspace":0.28})
ax = axes[0]; panel_title(ax, "A", "regulated footprint vs observed employment (states)")
ax.scatter(st.smmEmployment, st.facilities332, s=40, color=OK[0], edgecolor="white", zorder=3)
for _, r in st.iterrows():
    if r.state in ("Illinois","Connecticut","Florida","Georgia","California","Ohio","Texas",
                   "Michigan","Colorado","Wisconsin","Rhode Island","Idaho","Minnesota"):
        ax.annotate(r.state, (r.smmEmployment, r.facilities332), fontsize=7.2,
                    xytext=(4,3), textcoords="offset points")
ax.set_xlabel("SMM employment recorded in sudokn"); ax.set_ylabel("EPA NAICS-332 facilities (fiokg)")
ax.set_xscale("log")
z = np.polyfit(np.log10(st.smmEmployment), st.facilities332, 1)
xs = np.logspace(np.log10(st.smmEmployment.min()), np.log10(st.smmEmployment.max()), 50)
ax.plot(xs, np.polyval(z, np.log10(xs)), color="#888", ls="--", lw=1.0)

ax = axes[1]; panel_title(ax, "B", "burden-to-employment ratio")
st2 = st.assign(ratio=st.facilities332/(st.smmEmployment/1000)).sort_values("ratio")
t4 = pd.concat([st2.head(8), st2.tail(8)])
y = np.arange(len(t4))
ax.barh(y, t4.ratio, color=[OK[2]]*8 + [OK[1]]*8)
ax.set_yticks(y); ax.set_yticklabels(t4.state, fontsize=7.6)
ax.invert_yaxis()
ax.set_xlabel("EPA NAICS-332 facilities per 1,000 recorded SMM employees")
ax.text(0.98, 0.03, "green = employment-rich relative to burden\norange = burden-rich relative to recorded employment\n(partly a sudokn coverage artefact)",
        transform=ax.transAxes, ha="right", fontsize=7.0, color="#555")
finalize(fig, 5, F/"fig5_burden_vs_employment.png")

# ---------------------------------------------------------------- Figure 6
fig, axes = plt.subplots(1, 3, figsize=(14.6, 5.4), gridspec_kw={"wspace":0.36,
                          "width_ratios":[1.15,1.2,1.1]})
ax = axes[0]; panel_title(ax, "A", "blast radius — top 20 packages")
t5 = sw.nlargest(20, "dependentPkgs")
ecols = {"PyPI":OK[0], "Cargo":OK[1]}
ranked_barh(ax, list(t5.name), list(t5.dependentPkgs),
            themes=list(t5.ecosystem), theme_colors=ecols,
            annots=[f"{v/1000:.0f}k" for v in t5.dependentPkgs],
            xlabel="distinct downstream packages")
h = [plt.Line2D([0],[0], marker="s", ls="", color=c, label=k) for k,c in ecols.items()]
ax.legend(handles=h, loc="lower right", fontsize=7.4, frameon=False)

ax = axes[1]; panel_title(ax, "B", "blast radius vs vulnerability load")
ax.scatter(sw.dependentPkgs, sw.cves+0.5, s=30+sw.fragilityScore,
           c=[ecols.get(e, NEUTRAL) for e in sw.ecosystem], edgecolor="white", linewidth=0.6)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("downstream packages (log)"); ax.set_ylabel("recorded CVEs + 0.5 (log)")
for _, r in sw.nlargest(9, "fragilityScore").iterrows():
    ax.annotate(r["name"], (r.dependentPkgs, r.cves+0.5), fontsize=7.0,
                xytext=(4,3), textcoords="offset points")

ax = axes[2]; panel_title(ax, "C", "copyleft-licensed high-blast packages")
t6 = cl.nlargest(12, "dependentPkgs")
ax.barh(np.arange(len(t6)), t6.dependentPkgs, color=OK[3])
ax.set_yticks(np.arange(len(t6)))
ax.set_yticklabels([f"{n}  ({l.split('|')[0]})" for n,l in zip(t6.name, t6.copyleftLicenses)], fontsize=7.0)
ax.invert_yaxis(); ax.set_xlabel("distinct downstream packages")
finalize(fig, 6, F/"fig6_software_fragility.png")

# ---------------------------------------------------------------- Figure 8
fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.8), gridspec_kw={"wspace":0.34,
                          "width_ratios":[1.2,1.0]})
ax = axes[0]; panel_title(ax, "A", "the manufacturing-relevant software slice")
t7 = ist.sort_values("dependentPkgs", ascending=False)
y = np.arange(len(t7))
cols = [OK[1] if h else OK[0] for h in (t7.upstreamHubDeps > 0)]
ax.barh(y, t7.dependentPkgs.clip(lower=1), color=cols)
ax.set_yticks(y); ax.set_yticklabels(t7.name, fontsize=7.0)
ax.invert_yaxis(); ax.set_xscale("log")
ax.set_xlabel("distinct downstream packages (log)")
for i, (v, c) in enumerate(zip(t7.dependentPkgs, t7.cves)):
    if c > 0: ax.text(max(v,1)*1.2, i, f"{int(c)} CVE", va="center", fontsize=6.8, color=DOWN)
h = [plt.Line2D([0],[0], marker="s", ls="", color=OK[1], label="depends on a top-blast hub"),
     plt.Line2D([0],[0], marker="s", ls="", color=OK[0], label="no recorded hub dependency")]
ax.legend(handles=h, loc="lower right", fontsize=7.2, frameon=False)

ax = axes[1]; panel_title(ax, "B", "hardware CVE load by industry (name bridge)")
hb = pd.read_csv(D/"industry_hardware_cve_bridge.csv", dtype={"naics":str}).nlargest(12, "cves")
y = np.arange(len(hb))
is332 = hb.naics.str.startswith("332")
ax.barh(y, hb.cves, color=[OK[1] if f else NEUTRAL for f in is332])
ax.set_yticks(y); ax.set_yticklabels([f"{n} {f}" for n,f in zip(hb.naics, hb.firmName)], fontsize=7.0)
ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlabel("distinct CVEs on the firm's hardware (log)")
h = [plt.Line2D([0],[0], marker="s", ls="", color=OK[1], label="NAICS 332 (in scope)"),
     plt.Line2D([0],[0], marker="s", ls="", color=NEUTRAL, label="other NAICS")]
ax.legend(handles=h, loc="lower right", fontsize=7.2, frameon=False)
finalize(fig, 8, F/"fig8_industrial_stack.png")

# ---------------------------------------------------------------- Figure 7
ADVERSE_UP = {"adult obesity","adult smoking","air pollution - particulate matter",
 "children in poverty","diabetes prevalence","drug overdose deaths","food insecurity",
 "frequent mental distress","injury deaths","poor or fair health",
 "premature age-adjusted mortality","preventable hospital stays","primary care physicians",
 "mental health providers","severe housing problems","unemployment","uninsured",
 "CDC SVI overall percentile"}
FAVOUR_UP = {"broadband access","life expectancy","some college","social associations",
 "voter turnout"}
def dirmark(v):
    if v in ADVERSE_UP: return f"{v}  [+ = worse]"
    if v in FAVOUR_UP:  return f"{v}  [+ = better]"
    return f"{v}  [context]"

def gradient(ax, df, tiers, title, letter):
    piv = df.pivot(index="variable", columns="tier", values="mean")
    piv = piv[tiers]
    rel = piv.div(piv[tiers[-1]], axis=0) - 1.0
    order = rel[tiers[0]].sort_values().index
    rel = rel.loc[order]
    im = ax.imshow(rel.values*100, cmap="RdBu_r", vmin=-25, vmax=25, aspect="auto")
    ax.set_yticks(range(len(rel))); ax.set_yticklabels([short(dirmark(v),52) for v in rel.index], fontsize=6.8)
    ax.set_xticks(range(len(tiers)))
    ax.set_xticklabels([t.split("_",1)[1] for t in tiers], fontsize=7.6)
    for i in range(len(rel)):
        for j in range(len(tiers)):
            ax.text(j, i, f"{rel.values[i,j]*100:+.0f}", ha="center", va="center", fontsize=6.4)
    panel_title(ax, letter, title)
    return im

fig, axes = plt.subplots(1, 2, figsize=(15.2, 8.4), gridspec_kw={"wspace":0.78})
im = gradient(axes[0], sdp, ["A_high","B_mid","C_low"],
              "by facilities per 100k residents", "A")
gradient(axes[1], sds, ["A_dependent","B_moderate","C_marginal"],
         "by NAICS-332 share of the county's regulated base", "B")
cb = fig.colorbar(im, ax=axes, shrink=0.55, pad=0.02)
cb.set_label("% difference from the lowest-intensity tier", fontsize=8.5)
finalize(fig, 7, F/"fig7_population_gradient.png")

# ---------------------------------------------------------------- Figure 9
fig, axes = plt.subplots(1, 2, figsize=(14.6, 5.8), gridspec_kw={"wspace":0.46})
ax = axes[0]; panel_title(ax, "A", "the intersection: both axes at once")
e = M[M.placed >= 60]
ax.scatter(e.swFragility, e.concIndex, s=44,
           c=[OK[1] if s else OK[0] for s in e.shortList], edgecolor="white", linewidth=0.7, zorder=3)
ax.axhline(1.5, color="#888", ls=":", lw=1.0); ax.axvline(S["conc_q67"], color="#888", ls=":", lw=1.0)
for _, r in e[e.shortList].iterrows():
    ax.annotate(f"{r.naics}", (r.swFragility, r.concIndex), fontsize=7.2,
                xytext=(5,3), textcoords="offset points", color=OK[1])
ax.set_xlabel("industry software-fragility score (0–100)")
ax.set_ylabel("geographic concentration index")
ax.text(0.03, 0.04, f"Spearman ρ = {S['spearman_conc_vs_sw']}  (n = {S['eligible_industries']} industries, firm base ≥ 60)",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=7.8, color="#333")
hl2 = [plt.Line2D([0],[0], marker="o", ls="", color=OK[1], label="short-listed (top 8 joint risk)"),
       plt.Line2D([0],[0], marker="o", ls="", color=OK[0], label="other")]
ax.legend(handles=hl2, loc="upper right", fontsize=7.2, frameon=False)
ax.set_ylim(top=e.concIndex.max()*1.10)

ax = axes[1]; panel_title(ax, "B", "joint-risk ranking (top 12)")
t8 = M.dropna(subset=["jointRisk"]).nlargest(12, "jointRisk")
y = np.arange(len(t8))
ax.barh(y, t8.jointRisk, color=[OK[1] if s else OK[0] for s in t8.shortList])
ax.set_yticks(y); ax.set_yticklabels([f"{n} {short(l,24)}" for n,l in zip(t8.naics,t8.label)], fontsize=7.2)
ax.invert_yaxis(); ax.set_xlabel("joint-risk score (concentration pct × software pct × 100)")
for i,(v,t) in enumerate(zip(t8.jointRisk, t8.evidenceTier)):
    ax.text(v+1, i, f"tier {t}", va="center", fontsize=7.0, color="#333")
ax.set_xlim(right=t8.jointRisk.max()*1.22)
finalize(fig, 9, F/"fig9_intersection.png")

# ---------------------------------------------------------------- Figure 10
fig, axes = plt.subplots(1, 2, figsize=(14.6, 7.4), gridspec_kw={"wspace":0.44,
                         "width_ratios":[1.25,1.0]})
ax = axes[0]; panel_title(ax, "A", "concentrated / fragile industry × exposed county")
piv = slc.pivot_table(index="county", columns="naics", values="firms", aggfunc="sum")
piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index]
im = ax.imshow(piv.values, cmap="YlOrRd", aspect="auto")
ax.set_yticks(range(len(piv))); ax.set_yticklabels([short(c,34) for c in piv.index], fontsize=7.0)
ax.set_xticks(range(len(piv.columns))); SL = set(M[M.shortList].naics)
ax.set_xticklabels([f"{c}*" if c in SL else c for c in piv.columns], rotation=90, fontsize=7.0)
ax.set_xlabel("NAICS  (* = short-listed)", fontsize=8.5)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.values[i,j]
        if not np.isnan(v): ax.text(j, i, int(v), ha="center", va="center", fontsize=6.2)
cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02); cb.set_label("SMM firms", fontsize=8)

ax = axes[1]; panel_title(ax, "B", "counties by candidate industries present")
cc = slc.groupby("county").agg(inds=("naics","nunique"), firms=("firms","sum"),
                               emp=("employment","sum")).nlargest(12,"inds")
y = np.arange(len(cc))
ax.barh(y, cc.inds, color=OK[1])
ax.set_yticks(y); ax.set_yticklabels([short(c,32) for c in cc.index], fontsize=7.2)
ax.invert_yaxis(); ax.set_xlabel("candidate industries in which this county is a top cluster")
for i,(a,b) in enumerate(zip(cc.firms, cc.emp)):
    ax.text(cc.inds.iloc[i]+0.1, i, f"{int(a)} firms / {int(b):,} jobs", va="center", fontsize=6.8, color="#333")
ax.set_xlim(right=cc.inds.max()*1.9)
finalize(fig, 10, F/"fig10_shortlist_counties.png")
print("figures done")

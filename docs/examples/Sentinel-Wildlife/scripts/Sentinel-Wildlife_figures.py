#!/usr/bin/env python3
"""Sentinel-Wildlife: render figures 1-7 and the interactive county map."""
import json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
sys.path.insert(0, "/sessions/eager-brave-pascal/mnt/.claude/skills/okn-report-style/scripts")
from okn_figstyle import (apply_style, panel_title, legend_outside, ranked_barh,
                          finalize, folium_osm_map, save_map_html, folium_map_iframe,
                          UP, DOWN, NEUTRAL, THEME)
apply_style()
D, F = "data", "figures"
st = json.load(open("data/stats.json"))
OK = list(THEME)
C = {"bird": OK[1], "amph": OK[2], "A": OK[5], "B": OK[1], "C": NEUTRAL,
     "measured": OK[5], "inferred": OK[1], "none": NEUTRAL, "gap": OK[3]}

# ---------------------------------------------------- Fig 1 design / inventory
yr  = pd.read_csv(f"{D}/wl_obs_by_year.csv")
ck  = pd.read_csv(f"{D}/wl_clade_placekind.csv")
fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6))
ax = axes[0]
layers = [("Wildlife observations\n(wildlifekn)", 5205),
          ("Host-pathogen links\n(biohealth)", 22),
          ("Human-evidence edges\nfor those diseases (biohealth)", 3157),
          ("Contaminant body-burden\nsamples (sawgraph)", 0),
          ("Contaminant samples,\nany medium (sawgraph)", 0)]
vals = [v for _, v in layers]
cols = [UP if v > 0 else DOWN for v in vals]
y = np.arange(len(layers))
ax.barh(y, [max(v, 0.6) for v in vals], color=cols)
ax.set_yticks(y); ax.set_yticklabels([l for l, _ in layers], fontsize=8)
ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(0.5, 2e4)
ax.set_xlabel("records available for the Florida study area (log scale)")
for i, v in enumerate(vals):
    ax.text(max(v, 0.6) * 1.25, i, f"{v:,}" + ("  (none)" if v == 0 else ""),
            va="center", fontsize=8, color="#333")
panel_title(ax, "A", "federation coverage of the Florida study area")
ax = axes[1]
w = 0.38
labs = ["taxa in record", "records", "individuals"]
b = [st["bird_species"], int(ck[ck.clade == "Bird"].records.sum()),
     int(ck[ck.clade == "Bird"].individuals.sum())]
a = [st["amph_species"], int(ck[ck.clade == "Amphibian"].records.sum()),
     int(ck[ck.clade == "Amphibian"].individuals.sum())]
x = np.arange(3)
ax.bar(x - w/2, b, w, color=C["bird"], label="birds")
ax.bar(x + w/2, a, w, color=C["amph"], label="amphibians")
ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(labs)
ax.set_ylabel("count (log scale)")
for xi, v in zip(x - w/2, b): ax.text(xi, v*1.12, f"{v:,}", ha="center", fontsize=8)
for xi, v in zip(x + w/2, a): ax.text(xi, v*1.12, f"{v:,}", ha="center", fontsize=8)
ax.set_ylim(1, max(b + a) * 4)
panel_title(ax, "B", "observation inventory by clade")
legend_outside(ax, where="below", ncol=2)
finalize(fig, 1, f"{F}/fig1_design_inventory.png")

# ---------------------------------------------------- Fig 2 temporal
fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.4))
ax = axes[0]
for cl, col, mk in [("Bird", C["bird"], "o"), ("Amphibian", C["amph"], "s")]:
    d = yr[yr.clade == cl]
    ax.plot(d.year, d.records, marker=mk, ms=3.5, color=col, label=cl.lower() + "s")
ax.set_yscale("log"); ax.set_xlabel("year of record"); ax.set_ylabel("records (log scale)")
ax.axvspan(2018.5, 2024.5, color=C["amph"], alpha=.10)
ax.text(2021.5, 1.6, "no amphibian\nrecords after 2018", ha="center", fontsize=8, color="#444")
panel_title(ax, "A", "records per year")
legend_outside(ax, where="below", ncol=2)
ax = axes[1]
for cl, col, mk in [("Bird", C["bird"], "o"), ("Amphibian", C["amph"], "s")]:
    d = yr[yr.clade == cl]
    ax.plot(d.year, d.species_n, marker=mk, ms=3.5, color=col, label=cl.lower() + "s")
ax.set_xlabel("year of record"); ax.set_ylabel("distinct species recorded that year")
panel_title(ax, "B", "species recorded per year")
legend_outside(ax, where="below", ncol=2)
finalize(fig, 2, f"{F}/fig2_temporal_record.png")

# ---------------------------------------------------- Fig 3 contaminant record
bt = pd.read_csv(f"{D}/sawgraph_biota_taxa.csv")
ss = pd.read_csv(f"{D}/sawgraph_sampling_states.csv", dtype={"stateFIPS": str})
bp = pd.read_csv(f"{D}/bird_pfas_detects.csv")
GRP = {"Anas platyrhynchos": "birds", "Branta canadensis": "birds",
       "Odocoileus virginianus": "mammals", "Mya arenaria": "molluscs",
       "Mytilus edulis": "molluscs"}
bt["group"] = [GRP.get(t, "fish") for t in bt.taxonLabel]
g = bt.groupby("group").agg(taxa=("taxonLabel", "nunique"), samples=("samples", "sum")).reset_index()
g = g.sort_values("samples", ascending=False)
fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.4))
ax = axes[0]
x = np.arange(len(g)); w = .38
ax.bar(x - w/2, g.taxa, w, color=OK[1], label="taxa")
ax.bar(x + w/2, g.samples, w, color=OK[2], label="taxon-sample assignments")
ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(g.group)
ax.set_ylabel("count (log scale)")
for xi, v in zip(x - w/2, g.taxa): ax.text(xi, v*1.15, f"{v}", ha="center", fontsize=8)
for xi, v in zip(x + w/2, g.samples): ax.text(xi, v*1.15, f"{v:,}", ha="center", fontsize=8)
ax.set_ylim(1, g.samples.max()*6)
ax.text(0.98, 0.96, "amphibians: 0 taxa, 0 samples", transform=ax.transAxes,
        ha="right", va="top", fontsize=8.5, color=DOWN, weight="bold")
panel_title(ax, "A", "who is in the body-burden record")
legend_outside(ax, where="below", ncol=2)
ax = axes[1]
ss2 = ss.sort_values("biota_samples", ascending=False)
cols = [DOWN if s == "Florida" else UP for s in ss2.state]
ax.barh(np.arange(len(ss2)), [max(v, .5) for v in ss2.biota_samples], color=cols)
ax.set_yticks(np.arange(len(ss2))); ax.set_yticklabels(ss2.state, fontsize=8)
ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(.4, 4e3)
ax.set_xlabel("biota samples (log scale)")
for i, v in enumerate(ss2.biota_samples):
    ax.text(max(v, .5)*1.3, i, f"{v:,}" + ("  (study area)" if v == 0 else ""),
            va="center", fontsize=7.5, color=DOWN if v == 0 else "#333")
panel_title(ax, "B", "where body burden has been measured")
ax = axes[2]
pf = bp[bp.analyte == "PFOS"]
data = [pf[pf.taxonLabel == "Anas platyrhynchos"].value_ng_per_g.values,
        pf[pf.taxonLabel == "Branta canadensis"].value_ng_per_g.values]
parts = ax.boxplot(data, labels=["mallard\n(n=4)", "Canada goose\n(n=6)"], widths=.5,
                   patch_artist=True, medianprops=dict(color="black"))
for p, c in zip(parts["boxes"], [OK[5], OK[1]]): p.set_facecolor(c); p.set_alpha(.75)
for i, d in enumerate(data, start=1):
    ax.scatter(np.full(len(d), i) + np.random.uniform(-.07, .07, len(d)), d,
               color="black", s=14, zorder=3)
ax.set_yscale("log"); ax.set_ylabel("PFOS in tissue (ng/g)")
panel_title(ax, "C", "the only avian measurements in the federation")
finalize(fig, 3, f"{F}/fig3_contaminant_record.png")

# ---------------------------------------------------- Fig 4 phylogenetic ladder
sp = pd.read_csv(f"{D}/species_priority_ranking.csv")
TIER_ORDER = ["M", "I1", "I2", "I3", "I4", "N", "Z"]
TIER_TXT = {"M": "M  measured body burden", "I1": "I1  same genus as measured",
            "I2": "I2  same subfamily", "I3": "I3  same family (Anatidae)",
            "I4": "I4  same superorder (Galloanserae)",
            "N": "N  class Aves only", "Z": "Z  no measured relative in Amphibia"}
cnt = {t: int((sp.tier == t).sum()) for t in TIER_ORDER}
# class-level / amphibian totals come from the full observation inventory
# class-level counts are over the NCBITaxon-RESOLVED taxa (263 Aves, 76 Amphibia)
cnt["N"] = st["aves_resolved"] - sum(cnt[t] for t in ["M", "I1", "I2", "I3", "I4"])
cnt["Z"] = st["amphibia_resolved"]
fig, ax = plt.subplots(figsize=(9.4, 4.6))
vals = [cnt[t] for t in TIER_ORDER]
cols = [C["measured"]] + [C["inferred"]]*4 + [NEUTRAL, DOWN]
y = np.arange(len(TIER_ORDER))
ax.barh(y, vals, color=cols)
ax.set_yticks(y); ax.set_yticklabels([TIER_TXT[t] for t in TIER_ORDER], fontsize=8.5)
ax.invert_yaxis(); ax.set_xscale("log"); ax.set_xlim(.8, 700)
ax.set_xlabel("NCBITaxon-resolved taxa in this proximity tier (log scale); 61 of 400 labels unresolved")
for i, v in enumerate(vals): ax.text(v*1.15, i, f"{v}", va="center", fontsize=9)
ax.axhline(0.5, color="black", lw=.8, ls="--")
ax.text(0.98, 0.03, "below the dashed line: hypotheses, never sampled",
        transform=ax.transAxes, ha="right", fontsize=8.5, color="#444", style="italic")
finalize(fig, 4, f"{F}/fig4_phylogenetic_tiers.png")

# ---------------------------------------------------- Fig 5 host-pathogen chain
hp = pd.read_csv(f"{D}/host_pathogen_biohealth.csv")
hm = pd.read_csv(f"{D}/human_evidence_by_disease.csv")
dm = pd.read_csv(f"{D}/disease_label_map.csv")
dm["biohealth_label"] = dm.biohealth_label.str.strip('"')
hp = hp.merge(dm, left_on="disease", right_on="biohealth_label")
mat = pd.crosstab(hp.binom, hp.mondo_disease)
order_d = hm.sort_values("biohealth_edges", ascending=False).disease.tolist()
order_d = [d for d in order_d if d in mat.columns]
mat = mat.reindex(columns=order_d)
mat = mat.loc[mat.sum(1).sort_values(ascending=False).index]
fig, axes = plt.subplots(1, 2, figsize=(13.2, 4.9),
                         gridspec_kw={"width_ratios": [1.55, 1]})
ax = axes[0]
ax.imshow(mat.values, cmap="Blues", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(mat.columns)))
ax.set_xticklabels(mat.columns, rotation=38, ha="right", fontsize=8)
ax.set_yticks(range(len(mat.index)))
ax.set_yticklabels(mat.index, fontsize=8, style="italic")
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if mat.values[i, j]:
            ax.text(j, i, "*", ha="center", va="center", fontsize=11, color="white")
panel_title(ax, "A", "observed taxon x infectious disease (* = host link)")
ax = axes[1]
h = hm.set_index("disease").reindex(order_d)
yy = np.arange(len(h))
ax.barh(yy, h.biohealth_edges, color=OK[1], label="biohealth human-evidence edges")
ax.barh(yy, h.oard_ehr_phenotypes + h.biomarkerkg_biomarkers, color=DOWN,
        label="oard-kg EHR phenotypes + biomarkerkg biomarkers")
ax.set_yticks(yy); ax.set_yticklabels(h.index, fontsize=8); ax.invert_yaxis()
ax.set_xscale("log"); ax.set_xlim(.5, 4e3)
ax.set_xlabel("evidence items (log scale)")
for i, (a_, b_) in enumerate(zip(h.biohealth_edges, h.oard_ehr_phenotypes + h.biomarkerkg_biomarkers)):
    ax.text(a_*1.25, i, f"{a_:,}" + ("" if b_ else "  | clinical: 0"), va="center", fontsize=7.5,
            color="#333")
panel_title(ax, "B", "human evidence for the mapped disease")
legend_outside(ax, where="below", ncol=1)
finalize(fig, 5, f"{F}/fig5_host_pathogen_human.png")

# ---------------------------------------------------- Fig 6 county ranking
c = pd.read_csv(f"{D}/county_priority_ranking.csv", dtype={"fips5": str})
top = c.head(20)
fig, ax = plt.subplots(figsize=(10.6, 6.4))
ranked_barh(ax, [f"{r.rank}. {r.county_name}" for r in top.itertuples()],
            top.priority.tolist(),
            themes=top.conf_tier.tolist(),
            theme_colors={"A": C["A"], "B": C["B"], "C": C["C"]},
            annots=[f"{int(r.sentinel_species)} sentinel sp. / {int(r.host_species)} host sp."
                    f" / {int(r.total_species)} spp. / {int(r.frs_facilities):,} facilities"
                    for r in top.itertuples()],
            xlabel="sampling-priority score (0-1)")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=C[t], label=f"tier {t}") for t in "ABC"],
          loc="lower right", frameon=False, fontsize=8.5, title="confidence tier")
finalize(fig, 6, f"{F}/fig6_county_priority.png")

# ---------------------------------------------------- Fig 7 species value
spp = sp[sp.taxon_level == "species"].head(15)
fig, ax = plt.subplots(figsize=(10.6, 5.4))
ranked_barh(ax, [f"{r.rank}. {r.binom}" for r in spp.itertuples()],
            spp.value.tolist(),
            themes=["gap" if g == 1 else ("measured" if m == "yes" else "none")
                    for g, m in zip(spp.gap, spp.measured)],
            theme_colors={"gap": C["gap"], "measured": C["measured"], "none": NEUTRAL},
            annots=[f"tier {r.tier} / {int(r.pathogen_diseases)} disease(s)"
                    f" / {int(r.fl_records)} FL records" for r in spp.itertuples()],
            xlabel="sentinel information value (0-1)")
ax.legend(handles=[Patch(color=C["gap"], label="pathogen host, never sampled (the gap)"),
                   Patch(color=C["measured"], label="body burden measured (out of state)"),
                   Patch(color=NEUTRAL, label="no host-pathogen link")],
          loc="lower right", frameon=False, fontsize=8.5)
finalize(fig, 7, f"{F}/fig7_species_value.png")

# ---------------------------------------------------- interactive county map
rows = []
for r in c.itertuples():
    if pd.isna(r.lat): continue
    rows.append({"county": r.county_name, "FIPS": r.fips5, "rank": int(r.rank),
                 "priority score": round(float(r.priority), 3), "tier": r.conf_tier,
                 "sentinel-capable species": int(r.sentinel_species),
                 "best proximity tier": r.best_tier,
                 "pathogen-host species": int(r.host_species),
                 "species observed": int(r.total_species),
                 "bird / amphibian species": f"{int(r.species_n_bird)} / {int(r.species_n_amphibian)}",
                 "EPA FRS facilities": int(r.frs_facilities),
                 "adult asthma %": r.adult_asthma_pct,
                 "contaminant samples in county": 0,
                 "sources": ", ".join(eval(r.sources)) if isinstance(r.sources, str) else "",
                 "lat": float(r.lat), "lon": float(r.lon)})
m = folium_osm_map(rows, value_key="priority score", tooltip_key="county",
                   popup_keys=[k for k in rows[0] if k not in ("lat", "lon")],
                   zoom_start=7, radius=7)
save_map_html(m, f"{F}/Sentinel-Wildlife_county_map.html")
open(f"{F}/_map_iframe.html", "w").write(folium_map_iframe(m, height=560,
        title="Sampling-priority score by Florida county (OpenStreetMap)"))
print("figures + map written;", len(rows), "county markers")

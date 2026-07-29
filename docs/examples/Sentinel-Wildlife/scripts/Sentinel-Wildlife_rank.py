#!/usr/bin/env python3
"""Sentinel-Wildlife: build the county and species sampling-gap rankings.
All inputs in data/ are extracts from logged mcp-okn federated SPARQL queries."""
import json, math
import pandas as pd

D = "data"
minmax = lambda s: (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else s * 0

# ---------------------------------------------------------------- inputs
wl_cc   = pd.read_csv(f"{D}/wl_county_clade.csv")
bridge  = pd.read_csv(f"{D}/fl_county_bridge.csv", dtype={"fips5": str})
repair  = pd.read_csv(f"{D}/fl_county_bridge_repair.csv", dtype={"fips5": str})
ctx     = pd.read_csv(f"{D}/fl_place_context.csv", dtype={"fips5": str})
sent_cc = pd.read_csv(f"{D}/sentinel_species_county.csv")
tiers   = pd.read_csv(f"{D}/phylo_tiers.csv")
hostpat = pd.read_csv(f"{D}/host_pathogen_biohealth.csv")
nde     = pd.read_csv(f"{D}/nde_taxon_overlap.csv")
hum     = pd.read_csv(f"{D}/human_evidence_by_disease.csv")
spec    = pd.read_csv(f"{D}/wl_species_summary.csv")
anchors = pd.read_csv(f"{D}/fl_county_anchor_points.csv", dtype={"fips5": str})
biota   = pd.read_csv(f"{D}/sawgraph_biota_taxa.csv")

# Florida study area = verified 63-county label bridge + 2 declared repairs
fl = pd.concat([bridge.assign(bridge="verified L8"),
                repair[["county", "fips5"]].assign(bridge="repaired Saint->St.")])
fl = fl.merge(ctx[["fips5", "county"]].rename(columns={"county": "county_name"}), on="fips5")

# ---------------------------------------------------------------- county axes
piv = (wl_cc.pivot_table(index="county", columns="clade",
                         values=["species_n", "records", "individuals"], aggfunc="sum")
       .fillna(0))
piv.columns = [f"{a}_{b.lower()}" for a, b in piv.columns]
piv = piv.reset_index()

TIERW = {"M": 5, "I1": 4, "I2": 3, "I3": 2, "I4": 1}
sent = sent_cc.merge(tiers[["binom", "tier"]], on="binom", how="left")
sent["tier_w"] = sent.tier.map(TIERW)
inferred = (sent.dropna(subset=["tier"])
            .groupby("county")
            .agg(sentinel_species=("binom", "nunique"),
                 best_tier_w=("tier_w", "max"),
                 sentinel_records=("records", "sum"))
            .reset_index())
inferred["best_tier"] = inferred.best_tier_w.map({v: k for k, v in TIERW.items()})

hosts = set(hostpat.binom)
hostc = (sent_cc[sent_cc.binom.isin(hosts)]
         .groupby("county").agg(host_species=("binom", "nunique")).reset_index())

c = (fl.merge(piv, on="county", how="left")
       .merge(inferred, on="county", how="left")
       .merge(hostc, on="county", how="left")
       .merge(ctx.drop(columns=["county"]), on="fips5", how="left")
       .merge(anchors, on="fips5", how="left")).fillna(
    {"species_n_bird": 0, "species_n_amphibian": 0, "records_bird": 0,
     "records_amphibian": 0, "individuals_bird": 0, "individuals_amphibian": 0,
     "sentinel_species": 0, "best_tier_w": 0, "sentinel_records": 0, "host_species": 0})
c["best_tier"] = c.best_tier.fillna("none")
c["total_species"] = c.species_n_bird + c.species_n_amphibian
c["total_records"] = c.records_bird + c.records_amphibian
# every Florida county has zero contaminant samples of any medium (sawgraph): uniform deficit
c["pfas_samples_in_county"] = 0
c["log_facilities"] = c.frs_facilities.apply(lambda x: math.log10(max(x, 1)))

W = {"sentinel_species": .30, "best_tier_w": .20, "host_species": .20,
     "log_facilities": .12, "total_species": .13, "adult_asthma_pct": .05}
for k in W:
    c[f"n_{k}"] = minmax(c[k].astype(float))
c["priority"] = sum(W[k] * c[f"n_{k}"] for k in W)
c = c.sort_values("priority", ascending=False).reset_index(drop=True)
c["rank"] = c.index + 1
q = c.priority.quantile([.75, .40])
c["conf_tier"] = ["A" if p >= q[.75] else "B" if p >= q[.40] else "C" for p in c.priority]
c["evidence"] = [
    (f"{int(r.sentinel_species)} sentinel-capable sp. (best tier {r.best_tier}); "
     f"{int(r.host_species)} pathogen-host sp.; "
     f"{int(r.total_species)} spp. observed ({int(r.species_n_bird)} bird / "
     f"{int(r.species_n_amphibian)} amphibian); {int(r.frs_facilities):,} EPA FRS facilities; "
     f"adult asthma {r.adult_asthma_pct}%; contaminant samples in county: 0")
    for r in c.itertuples()]
c["sources_n"] = 5
c["sources"] = [["wildlifekn", "spatialkg", "sawgraph", "fiokg", "spoke-okn"]] * len(c)
c.loc[c.cm_cities > 0, "sources_n"] = 6
c.loc[c.cm_cities > 0, "sources"] = pd.Series(
    [["wildlifekn", "spatialkg", "sawgraph", "fiokg", "spoke-okn", "climatemodelskg"]] *
    int((c.cm_cities > 0).sum()), index=c.index[c.cm_cities > 0])
c.to_csv(f"{D}/county_priority_ranking.csv", index=False)

# ---------------------------------------------------------------- species axes
sp = tiers.copy()
extra = pd.DataFrame([{"binom": b, "tier": "N", "tier_label": "no measured relative below class Aves",
                       "anchor": "Aves", "measured": "no"}
                      for b in sorted(set(hostpat[hostpat.clade == "Bird"].binom) - set(tiers.binom))]
                     + [{"binom": b, "tier": "Z",
                         "tier_label": "no measured relative anywhere in Amphibia",
                         "anchor": "Amphibia", "measured": "no"}
                        for b in sorted(set(hostpat[hostpat.clade == "Amphibian"].binom))])
sp = pd.concat([sp, extra], ignore_index=True)

dmap = pd.read_csv(f"{D}/disease_label_map.csv")
dmap["biohealth_label"] = dmap.biohealth_label.str.strip('"')
hostpat = hostpat.merge(dmap, left_on="disease", right_on="biohealth_label", how="left")
assert hostpat.mondo_disease.notna().all(), hostpat[hostpat.mondo_disease.isna()]
npath = hostpat.groupby("binom").agg(pathogen_diseases=("mondo_disease", "nunique")).reset_index()
dis_ev = hum.set_index("disease")
def human_ev(b):
    ds = hostpat[hostpat.binom == b].mondo_disease.tolist()
    tot = sum(int(dis_ev.biohealth_edges.get(d, 0)) for d in ds)
    clin = sum(int(dis_ev.oard_ehr_phenotypes.get(d, 0)) +
               int(dis_ev.biomarkerkg_biomarkers.get(d, 0)) for d in ds)
    return tot, clin
sp = sp.merge(npath, on="binom", how="left").fillna({"pathogen_diseases": 0})
sp[["biohealth_edges", "clinical_biomarker_items"]] = [human_ev(b) for b in sp.binom]

spec["binom"] = spec.species.str.replace(r"^(\S+\s+\S+).*$", r"\1", regex=True)
foot = spec.groupby("binom").agg(fl_records=("records", "sum"),
                                 fl_individuals=("individuals", "sum")).reset_index()
cnty = sent_cc.groupby("binom").agg(fl_counties=("county", "nunique")).reset_index()
extra_c = pd.read_csv(f"{D}/extra_county_counts.csv").rename(columns={"county_labels": "fl_counties"})
cnty = pd.concat([cnty, extra_c[["binom", "fl_counties"]]], ignore_index=True)
sp = sp.merge(foot, on="binom", how="left").merge(cnty, on="binom", how="left")
sp = sp.fillna({"fl_records": 0, "fl_individuals": 0, "fl_counties": 0})
sp["nde_datasets"] = sp.binom.map(nde.set_index("binom").nde_datasets).fillna(0)

TW = {"M": 5, "I1": 4, "I2": 3, "I3": 2, "I4": 1, "N": 0.5, "Z": 0}
sp["tier_w"] = sp.tier.map(TW)
HIGHER = {"Anura", "Amphibia", "Bufonidae", "Hylidae", "Ranidae", "Sirenidae", "Hylinae"}
sp["taxon_level"] = ["higher taxon" if b in HIGHER else "species" for b in sp.binom]
# flagged as probable literature-extraction artefacts in the biohealth SemMedDB-style layer
ARTEFACT = {("Anura", "influenza"), ("Amphibia", "salmonellosis")}
sp["artefact_flag"] = ["biohealth host-pathogen edge is a probable text-mining artefact"
                       if any((b, d) in ARTEFACT for d in hostpat[hostpat.binom == b].mondo_disease)
                       else "" for b in sp.binom]
# GAP = pathogen host AND no measured body burden -> the information a first sample would add
sp["gap"] = ((sp.pathogen_diseases > 0) & (sp.measured == "no")).astype(int)
for k in ["tier_w", "pathogen_diseases", "biohealth_edges", "fl_records", "fl_counties"]:
    sp[f"n_{k}"] = minmax(sp[k].astype(float))
sp["value"] = (.28 * sp.n_pathogen_diseases + .22 * sp.n_tier_w + .18 * sp.n_biohealth_edges
               + .16 * sp.n_fl_records + .10 * sp.n_fl_counties + .06 * (sp.nde_datasets > 0))
sp["value"] = sp.value * (1 + .35 * sp.gap)          # unsampled hosts are worth more
sp["_lvl"] = (sp.taxon_level == "higher taxon").astype(int)
sp = sp.sort_values(["_lvl", "value"], ascending=[True, False]).reset_index(drop=True)
n_sp = int((sp.taxon_level == "species").sum())
sp["rank"] = [str(i + 1) if i < n_sp else "-" for i in range(len(sp))]
sp = sp.drop(columns=["_lvl"])
qs = sp[sp.taxon_level == "species"].value.quantile([.75, .40])
sp["conf_tier"] = ["A" if v >= qs[.75] else "B" if v >= qs[.40] else "C" for v in sp.value]
sp["evidence"] = [
    (f"{r.tier_label}; " +
     (f"host for {int(r.pathogen_diseases)} infectious disease(s) "
      f"({int(r.biohealth_edges):,} biohealth human-evidence edges)"
      if r.pathogen_diseases else "no host-pathogen link in the federation") +
     f"; {int(r.fl_records)} FL records in {int(r.fl_counties)} counties" +
     ("; MEASURED body burden (out of state)" if r.measured == "yes"
      else "; NO contaminant measurement anywhere"))
    for r in sp.itertuples()]
sp["sources_n"] = [len({"wildlifekn", "ubergraph"} |
                       ({"sawgraph"} if r.measured == "yes" else set()) |
                       ({"biohealth"} if r.pathogen_diseases else set()) |
                       ({"nde"} if r.nde_datasets else set())) for r in sp.itertuples()]
sp["sources"] = [sorted({"wildlifekn", "ubergraph"} |
                        ({"sawgraph"} if r.measured == "yes" else set()) |
                        ({"biohealth"} if r.pathogen_diseases else set()) |
                        ({"nde"} if r.nde_datasets else set())) for r in sp.itertuples()]
sp.to_csv(f"{D}/species_priority_ranking.csv", index=False)

spp = sp[sp.taxon_level == "species"].reset_index(drop=True)
# ---------------------------------------------------------------- stats.json
amph_sp = int(spec[spec.clade == "Amphibian"].species.nunique())
bird_sp = int(spec[spec.clade == "Bird"].species.nunique())
stats = {
  "records_total": int(spec.records.sum()),
  "species_total": amph_sp + bird_sp, "bird_species": bird_sp, "amph_species": amph_sp,
  "individuals_total": int(spec.individuals.sum()),
  "locations_total": 657,
  "record_start": "1974-06-10", "record_end": "2024-05-13",
  "bird_last_year": 2024, "amph_last_year": 2018,
  "amph_2018_records": 1709, "bird_2023_records": 575,
  "taxa_resolved": 339,
  "fl_counties_bridged": int(len(bridge)), "fl_counties_total": 67,
  "l8_published_count": 63, "l8_true_count": 62,
  "fl_counties_studied": int(len(fl)),
  "measured_species": int((tiers.measured == "yes").sum()),
  "biota_taxa_total": int(len(biota)),
  "biota_bird_taxa": 2, "biota_amph_taxa": 0,
  "biota_samples_total": 2269, "biota_states": 12,
  "fl_biota_samples": 0, "fl_any_pfas_samples": 0,
  "mallard_pfos_max": 1990, "goose_pfos_max": 137,
  "inferred_species": int((tiers.measured == "no").sum()),
  "nde_shared_taxa": int(nde.binom.nunique()),
  "nde_bird_taxa": int((nde.clade == "Bird").sum()),
  "nde_amph_taxa": int((nde.clade == "Amphibian").sum()),
  "wnv_datasets": 43, "wnv_avian_host_datasets": 0, "bd_datasets": 2,
  "host_species": int(hostpat.binom.nunique()),
  "host_disease_pairs": int(len(hostpat)),
  "diseases_checked": int(len(hum)),
  "diseases_with_biohealth": int((hum.biohealth_edges > 0).sum()),
  "diseases_with_oard": int((hum.oard_ehr_phenotypes > 0).sum()),
  "diseases_with_biomarker": int((hum.biomarkerkg_biomarkers > 0).sum()),
  "diseases_in_spoke": 0,
  "county_tierA": int((c.conf_tier == "A").sum()),
  "county_tierB": int((c.conf_tier == "B").sum()),
  "county_tierC": int((c.conf_tier == "C").sum()),
  "species_tierA": int(((sp.conf_tier == "A") & (sp.taxon_level == "species")).sum()),
  "species_tierB": int(((sp.conf_tier == "B") & (sp.taxon_level == "species")).sum()),
  "species_tierC": int(((sp.conf_tier == "C") & (sp.taxon_level == "species")).sum()),
  "species_ranked": int((sp.taxon_level == "species").sum()),
  "gap_species": int(sp[(sp.gap == 1) & (sp.taxon_level == "species")].gap.sum()),
  "higher_taxa_flagged": int((sp.taxon_level == "higher taxon").sum()),
  "top_county": c.iloc[0].county_name, "top_county_score": round(float(c.iloc[0].priority), 3),
  "top2_county": c.iloc[1].county_name, "top3_county": c.iloc[2].county_name,
  "top_species": spp.iloc[0].binom, "top2_species": spp.iloc[1].binom,
  "top3_species": spp.iloc[2].binom, "top4_species": spp.iloc[3].binom,
  "top5_species": spp.iloc[4].binom,
  "top_species_diseases": int(spp.iloc[0].pathogen_diseases),
  "top_species_edges": int(spp.iloc[0].biohealth_edges),
  "top_species_records": int(spp.iloc[0].fl_records),
  "top_species_counties": int(spp.iloc[0].fl_counties),
  "cm_counties": int((c.cm_cities > 0).sum()),
  "frs_facilities_total": int(ctx.frs_facilities.sum()),
  "kgs_queried": 9,
}
json.dump(stats, open("data/stats.json", "w"), indent=2)
print(c[["rank","county_name","fips5","sentinel_species","best_tier","host_species",
         "total_species","frs_facilities","priority","conf_tier"]].head(15).to_string(index=False))
print()
print(sp[["rank","binom","taxon_level","tier","measured","pathogen_diseases","biohealth_edges",
          "fl_records","fl_counties","gap","value","conf_tier"]].head(20).to_string(index=False))
print(sp[sp.taxon_level=="higher taxon"][["binom","pathogen_diseases","artefact_flag","value"]].to_string(index=False))
print()
print(json.dumps({k: stats[k] for k in list(stats)[:20]}, indent=0))

#!/usr/bin/env python3
"""
Instrument-Criticality — core analysis.

Builds the spaceborne-instrument criticality table from five independent
dependency routes plus an irreplaceability axis, assigns three risk classes,
and tests the data-footprint / criticality asymmetry.

Inputs : data/*.csv (extracted from the OKN federated SPARQL endpoint)
Outputs: data/instrument_criticality.csv, data/stats.json,
         data/risk_classes.json
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


# ---------------------------------------------------------------- taxonomy
# GCMD "instrument" labels that are not a specific flight instrument.
GENERIC_CLASS = {
    "not applicable", "cameras", "camera", "altimeters", "radiometers",
    "imaging radiometers", "infrared radiometers", "scatterometers",
    "radar altimeters", "photometers", "sun photometers", "sounders", "sar",
    "wind profilers", "satellites", "gps", "gps p", "gps receiver",
    "gps receivers", "gnss", "gnss receiver", "gnss-ro receiver", "ro",
    "ccd imager", "soundings", "transponders", "radio transponders",
}
# Spacecraft-bus / engineering subsystems, not science instruments.
BUS_SUBSYSTEM = {
    "computer", "gyros", "star tracker", "laser reflector", "optical beacon",
    "grace sca", "grace-fo sca", "grace lrr", "lra", "gis", "pc", "cd", "la",
    "mr", "doris ground station beacon", "ps0", "ps1", "ps2", "ps2.sd",
    "psb.sd",
}


def category(k: str) -> str:
    if k in GENERIC_CLASS:
        return "generic GCMD class"
    if k in BUS_SUBSYSTEM:
        return "platform/bus subsystem"
    return "science instrument"


# ---------------------------------------------------------------- load
plat = pd.read_csv(DATA / "instr_platforms.csv")
plat["k"] = plat["instr"].str.lower()

prof = pd.read_csv(DATA / "instr_profile.csv")
pubs = pd.read_csv(DATA / "instr_allpubs.csv")
cov = pd.read_csv(DATA / "instr_coverage_years.csv")
cov["k"] = cov["instr"].str.lower()
cov = cov.drop(columns=["instr"])

r123 = pd.read_csv(DATA / "routes_R1_R2_R3.csv")
r4 = pd.read_csv(DATA / "route_R4_nasa_title.csv")
r1b = pd.read_csv(DATA / "route_R1b_platform_mentions.csv")
frac = pd.read_csv(DATA / "instr_fractional_footprint.csv")

# ---- R5, recomputed from the sole-measurer table ------------------------
# A variable is SOLE-MEASURED when exactly one distinct instrument NAME
# measures it, counted per variable NAME (the same denominator as the 184
# model-produced-and-measured variables). `sole_measured_variables.csv` is
# that set, verbatim from the endpoint.
sole = pd.read_csv(DATA / "sole_measured_variables.csv")
sole["k"] = sole["measurerName"].str.lower()

# Alias resolution: the mention vocabulary is free text, so an instrument's
# sole-measured variables are split across its acronym and its spelled-out
# name. This map is a DECLARED, hand-built supplement — it is reported
# separately from the strict GCMD-label join and never feeds the score.
ALIAS = {
    "moderate resolution imaging spectroradiometer (modis)": "MODIS",
    "modis": "MODIS",
    "advanced very high resolution radiometer (avhrr)": "AVHRR",
    "ceres": "CERES (family)",
    "clouds and earths radiant energy system (ceres) mission": "CERES (family)",
    "sea-viewing wide field-of-view sensor (seawifs)": "SeaWiFS",
    "earth radiation budget experiment (erbe)": "ERBE",
    "tmi (trmm microwave imager)": "TMI",
    "grace": "GRACE (family)",
    "calipso": "CALIOP/CALIPSO",
    "cryosat-2": "SIRAL/CryoSat-2",
    "landsat": "Landsat (family)",
    "gome-2": "GOME-2",
    "gedi": "GEDI",
    "ssmi: special sensor microwave imager": "SSM/I",
    "mipas (the michelson interferometer for passive atmospheric sounding)": "MIPAS",
    "the cloudsat spaceborne cloud-profiling radar": "CloudSat-CPR",
    "the cloud profiling radar": "CloudSat-CPR",
}
sole["aliasFamily"] = sole["k"].map(ALIAS)
sole.to_csv(DATA / "sole_measured_variables_resolved.csv", index=False)

r5 = (sole.groupby("k")
          .agg(R5_nSoleVars=("variable", "nunique"),
               R5_soleVars=("variable", lambda s: " | ".join(sorted(s))))
          .reset_index())

df = plat[["k", "instr", "nPlat", "nDs"]].copy()
for extra in (prof, pubs, cov, r123, r4, r1b, r5, frac):
    df = df.merge(extra, on="k", how="left")

route_cols = [
    "R1_cmMentionPapers", "R1b_platMentionPapers", "R2_cmModelPapers",
    "R3_doiPapers", "R4_modelTitlePubs",
]
df["R5_nModelVars"] = 0  # superseded by the sole-measurer axis; kept for schema stability
fill0 = route_cols + [
    "R2_cmDistinctModels", "R3_doiDatasets", "R4_modelTitleDatasets",
    "R5_nModelVars", "R5_nSoleVars", "nKeywords", "nProjects", "nDaacs",
    "allPubs", "dsWithPubs", "nDsDated", "fracDs",
]
for c in fill0:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
df["R5_soleVars"] = df["R5_soleVars"].fillna("")
df["category"] = df["k"].map(category)

# GCMD science keywords for which a spaceborne instrument is the only source.
SOLE_KEYWORD = {
    "atlas": "BATHYMETRY/SEAFLOOR TOPOGRAPHY",
    "sar": "TERRESTRIAL ECOSYSTEMS",
    "ddmi": "WATER QUALITY",
}
df["soleKeyword"] = df["k"].map(SOLE_KEYWORD).fillna("")


# ---------------------------------------------------------------- scoring
def norm(s: pd.Series) -> pd.Series:
    """log1p then min-max to [0, 1] over the scored universe."""
    v = np.log1p(s.astype(float))
    rng = v.max() - v.min()
    return (v - v.min()) / rng if rng > 0 else v * 0.0


sci = df[df["category"] == "science instrument"].copy()

for c in route_cols:
    sci["z_" + c] = norm(sci[c])

# Dependency breadth: unweighted mean of the five normalised route scores.
sci["DB"] = sci[["z_" + c for c in route_cols]].mean(axis=1)

# Irreplaceability: sole measurer of model-produced variables (+ sole GCMD keyword).
sci["IR_raw"] = sci["R5_nSoleVars"] + (sci["soleKeyword"] != "").astype(int)
sci["IR"] = norm(sci["IR_raw"])

# Route corroboration: how many of the five independent routes are non-zero.
sci["corroboration"] = (sci[route_cols] > 0).sum(axis=1)

sci["criticality"] = (
    0.55 * sci["DB"] + 0.30 * sci["IR"] + 0.15 * (sci["corroboration"] / 5.0)
)
sci["criticality"] = 100 * sci["criticality"] / sci["criticality"].max()

# Data footprint. The KG stores no byte volume, so dataset count is the proxy.
# Datasets attach to PLATFORMS, not instruments, so the raw count double-counts
# every co-flying instrument; `fracDs` divides each platform's datasets evenly
# among the instruments it carries. Both are reported.
sci["footprint"] = norm(sci["nDs"])
sci["footprint_score"] = 100 * sci["footprint"] / sci["footprint"].max()
sci["footprint_frac"] = norm(sci["fracDs"])
sci["footprint_frac_score"] = (100 * sci["footprint_frac"]
                               / sci["footprint_frac"].max())

# Rank divergence: how far criticality rank departs from footprint rank.
sci["rank_crit"] = sci["criticality"].rank(ascending=False, method="min")
sci["rank_foot"] = sci["nDs"].rank(ascending=False, method="min")
sci["rank_foot_frac"] = sci["fracDs"].rank(ascending=False, method="min")
sci["rank_gap"] = sci["rank_foot"] - sci["rank_crit"]


# ---------------------------------------------------------------- tiers
def tier(row) -> str:
    if row["corroboration"] >= 4 and row["criticality"] >= 30:
        return "A"
    if row["corroboration"] >= 2:
        return "B"
    return "C"


sci["tier"] = sci.apply(tier, axis=1)

# Which federation KGs support each row.
def sources(row):
    s = ["nasa-gesdisc-kg"]
    if (row["R1_cmMentionPapers"] > 0 or row["R1b_platMentionPapers"] > 0
            or row["R2_cmModelPapers"] > 0 or row["R3_doiPapers"] > 0
            or row["R5_nModelVars"] > 0):
        s.append("climatemodelskg")
    return s


sci["sourceList"] = sci.apply(sources, axis=1)
sci["nSources"] = sci["sourceList"].apply(len)


# ---------------------------------------------------------------- risk classes
med_ds = sci["nDs"].median()
q75_db = sci["DB"].quantile(0.75)
med_db = sci["DB"].median()

q75_crit = sci["criticality"].quantile(0.75)
classA = sci[(sci["DB"] >= q75_db) & (sci["corroboration"] >= 3)]
classB = sci[(sci["IR_raw"] > 0) & (sci["criticality"] < q75_crit)]
classC = sci[(sci["nDs"] >= med_ds) & (sci[route_cols].sum(axis=1) == 0)]

sci["riskClass"] = "—"
sci.loc[classC.index, "riskClass"] = "C: footprint, no uptake"
sci.loc[classB.index, "riskClass"] = "B: narrow, irreplaceable"
sci.loc[classA.index, "riskClass"] = "A: broadly relied on"


# ---------------------------------------------------------------- asymmetry
rho, p_rho = sps.spearmanr(sci["nDs"], sci["criticality"])
rho_frac, p_frac = sps.spearmanr(sci["fracDs"], sci["criticality"])
rho_pub, p_pub = sps.spearmanr(sci["allPubs"], sci["criticality"])

top10_crit = set(sci.nlargest(10, "criticality")["instr"])
top10_foot = set(sci.nlargest(10, "nDs")["instr"])
overlap = sorted(top10_crit & top10_foot)
top25_crit = set(sci.nlargest(25, "criticality")["instr"])
top25_foot = set(sci.nlargest(25, "nDs")["instr"])
overlap25 = sorted(top25_crit & top25_foot)

under = sci.nlargest(12, "rank_gap")[["instr", "rank_crit", "rank_foot",
                                      "rank_gap", "nDs", "criticality"]]
over = sci.nsmallest(12, "rank_gap")[["instr", "rank_crit", "rank_foot",
                                      "rank_gap", "nDs", "criticality"]]

# Route pairwise agreement (Spearman on the scored universe).
TEXTUAL = ["R1_cmMentionPapers", "R1b_platMentionPapers", "R2_cmModelPapers"]
STRUCTURAL = ["R3_doiPapers", "R4_modelTitlePubs"]
route_corr = pd.DataFrame(index=route_cols, columns=route_cols, dtype=float)
for a in route_cols:
    for b in route_cols:
        route_corr.loc[a, b] = sps.spearmanr(sci[a], sci[b]).statistic

sci = sci.sort_values("criticality", ascending=False).reset_index(drop=True)
sci["rank"] = np.arange(1, len(sci) + 1)


# ---------------------------------------------------------------- geography
geo = pd.read_csv(DATA / "geo_paper_country_mentions.csv")
reg = pd.read_csv(DATA / "geo_study_regions.csv")
coh = pd.read_csv(DATA / "cohort_institution_countries.csv")
geo_total = int(geo["nPapers"].sum())
geo_top10_share = float(geo.nlargest(10, "nPapers")["nPapers"].sum() / geo_total)
geo_thin = geo[geo["nPapers"] <= 10]

coh_total = int(coh["nAuthorOrcids"].sum())
coh_top5_share = float(coh.nlargest(5, "nAuthorOrcids")["nAuthorOrcids"].sum()
                       / coh_total)


# ---------------------------------------------------------------- outputs
out_cols = [
    "rank", "instr", "k", "category", "tier", "riskClass", "criticality",
    "footprint_score", "footprint_frac_score", "rank_gap", "corroboration",
    "DB", "IR", "nPlat", "nDs", "fracDs", "allPubs",
    "nKeywords", "nProjects", "nDaacs", "firstStartYear", "lastStartYear",
    "R1_cmMentionPapers", "R1b_platMentionPapers", "R2_cmModelPapers",
    "R2_cmDistinctModels", "R3_doiPapers", "R4_modelTitlePubs",
    "R5_nModelVars", "R5_nSoleVars", "R5_soleVars", "soleKeyword",
    "nSources",
]
sci_out = sci[out_cols].round(4)
sci_out.to_csv(DATA / "instrument_criticality.csv", index=False)
df.to_csv(DATA / "instrument_catalogue_full.csv", index=False)
route_corr.round(3).to_csv(DATA / "route_agreement_matrix.csv")

stats = {
    # catalogue scale
    "n_kg_instruments_all": 921,
    "n_kg_platforms_all": 455,
    "n_kg_datasets": 8058,
    "n_kg_publications": 457085,
    "n_kg_authors": 905086,
    "n_kg_institutions": 35435,
    "n_kg_projects": 415,
    "n_kg_datacenters": 189,
    "n_kg_sciencekeywords": 1609,
    "n_sciencekeywords_used": 122,
    "n_space_platforms": 254,
    "n_space_instruments": 288,
    "n_space_datasets": 4931,
    "n_datasets_with_pub": 2581,
    "pct_datasets_with_pub": round(100 * 2581 / 8058, 1),
    "n_pubs_using_datasets": 27076,
    # climatemodelskg scale
    "n_cm_papers": 2000,
    "n_cm_papers_doi": 1910,
    "n_cm_instruments": 1490,
    "n_cm_platforms": 584,
    "n_cm_obsdatasets": 2521,
    "n_cm_models": 394,
    "n_cm_variables": 3144,
    "n_cm_authors": 10437,
    "n_cm_papers_naming_instrument": 843,
    "n_cm_papers_using_model": 563,
    "n_cm_papers_both": 220,
    # joins
    "n_doi_shared_papers": 651,
    "pct_doi_shared": round(100 * 651 / 1910, 1),
    "n_gcmd_instrument_match": 115,
    "n_gcmd_platform_match": 70,
    "n_author_name_match": 8391,
    # routes
    "n_route_R1": int((sci["R1_cmMentionPapers"] > 0).sum()),
    "n_route_R1b": int((sci["R1b_platMentionPapers"] > 0).sum()),
    "n_route_R2": int((sci["R2_cmModelPapers"] > 0).sum()),
    "n_route_R3": int((sci["R3_doiPapers"] > 0).sum()),
    "n_route_R4": int((sci["R4_modelTitlePubs"] > 0).sum()),
    "n_scored_instruments": int(len(sci)),
    "n_generic_class": int((df["category"] == "generic GCMD class").sum()),
    "n_bus_subsystem": int((df["category"] == "platform/bus subsystem").sum()),
    "n_corrob_0": int((sci["corroboration"] == 0).sum()),
    "n_corrob_1": int((sci["corroboration"] == 1).sum()),
    "n_corrob_2plus": int((sci["corroboration"] >= 2).sum()),
    "n_corrob_4plus": int((sci["corroboration"] >= 4).sum()),
    "n_corrob_5": int((sci["corroboration"] == 5).sum()),
    # variables / irreplaceability
    "n_model_relevant_variables": 184,
    "n_sole_measured_variables": 90,
    "pct_sole_measured": round(100 * 90 / 184, 1),
    "n_obs_datasets_model_evaluated": 163,
    "n_models_with_obs": 72,
    # tiers & classes
    "n_tier_A": int((sci["tier"] == "A").sum()),
    "n_tier_B": int((sci["tier"] == "B").sum()),
    "n_tier_C": int((sci["tier"] == "C").sum()),
    "n_class_A": int(len(classA)),
    "n_class_B": int(len(classB)),
    "n_class_C": int(len(classC)),
    "median_nDs": float(med_ds),
    # asymmetry
    "spearman_rho_footprint_criticality": round(float(rho), 3),
    "spearman_p_footprint_criticality": float(p_rho),
    "spearman_rho_fracfootprint_criticality": round(float(rho_frac), 3),
    "spearman_p_fracfootprint_criticality": float(p_frac),
    "spearman_rho_pubs_criticality": round(float(rho_pub), 3),
    "spearman_p_pubs_criticality": float(p_pub),
    "top10_overlap_n": len(overlap),
    "top10_overlap": overlap,
    "top25_overlap_n": len(overlap25),
    "max_rank_gap": int(sci["rank_gap"].max()),
    "min_rank_gap": int(sci["rank_gap"].min()),
    "route_agree_textual": round(float(route_corr.loc["R1_cmMentionPapers",
                                                     "R2_cmModelPapers"]), 2),
    "route_agree_structural": round(float(route_corr.loc["R3_doiPapers",
                                                        "R4_modelTitlePubs"]), 2),
    # Cross-family = every textual (R1, R1b, R2) x structural (R3, R4) pair.
    "route_agree_cross_min": round(float(min(
        route_corr.loc[t, s] for t in TEXTUAL for s in STRUCTURAL)), 2),
    "route_agree_cross_max": round(float(max(
        route_corr.loc[t, s] for t in TEXTUAL for s in STRUCTURAL)), 2),
    "route_agree_R1b_R3": round(float(route_corr.loc["R1b_platMentionPapers",
                                                     "R3_doiPapers"]), 2),
    "route_agree_R1b_R4": round(float(route_corr.loc["R1b_platMentionPapers",
                                                     "R4_modelTitlePubs"]), 2),
    "route_agree_R1_R1b": round(float(route_corr.loc["R1_cmMentionPapers",
                                                     "R1b_platMentionPapers"]), 2),
    "top_instrument": sci.iloc[0]["instr"],
    "top_instrument_score": round(float(sci.iloc[0]["criticality"]), 1),
    # community
    "n_boundary_author_names": 4397,
    "n_boundary_author_orcids": 3169,
    "n_boundary_countries": int(len(coh)),
    "boundary_top5_share": round(100 * coh_top5_share, 1),
    "n_cm_author_names": 10029,
    "pct_cm_authors_in_nasa": round(100 * 8391 / 10029, 1),
    # Alias-resolved supplement: how much the strict GCMD-label join misses.
    "n_sole_vars_strict_gcmd": int(
        sci.loc[sci["R5_nSoleVars"] > 0, "R5_nSoleVars"].sum()),
    "n_instr_sole_strict_gcmd": int((sci["R5_nSoleVars"] > 0).sum()),
    "n_sole_vars_alias_resolved": int(sole["aliasFamily"].notna().sum()),
    "n_families_alias_resolved": int(sole["aliasFamily"].nunique()),
    # geography
    "n_geo_countries": int(len(geo)),
    "geo_top10_share": round(100 * geo_top10_share, 1),
    "n_geo_thin": int(len(geo_thin)),
    "geo_top_country": geo.nlargest(1, "nPapers").iloc[0]["country"],
    "geo_top_country_n": int(geo.nlargest(1, "nPapers").iloc[0]["nPapers"]),
    "n_geo_regions": int(len(reg)),
    "geo_top_region": reg.nlargest(1, "nPapers").iloc[0]["name"],
    "geo_top_region_n": int(reg.nlargest(1, "nPapers").iloc[0]["nPapers"]),
    # concentration / zero-signal
    "n_zero_route": int((sci[route_cols].sum(axis=1) == 0).sum()),
    "zero_route_datasets": int(sci.loc[sci[route_cols].sum(axis=1) == 0,
                                       "nDs"].sum()),
    "zero_route_dataset_share": round(float(
        100 * sci.loc[sci[route_cols].sum(axis=1) == 0, "nDs"].sum()
        / sci["nDs"].sum()), 1),
    "modis_share_of_mentions": round(float(
        100 * sci["R1_cmMentionPapers"].max() / sci["R1_cmMentionPapers"].sum()), 1),
    "median_criticality": round(float(sci["criticality"].median()), 1),
    "n_zero_criticality": int((sci["criticality"] == 0).sum()),
    "n_class_B_also_C": int(len(set(classB.index) & set(classC.index))),
    "modis_sole_vars": int(sci.loc[sci["instr"] == "MODIS",
                                   "R5_nSoleVars"].iloc[0]),
}

(DATA / "stats.json").write_text(json.dumps(stats, indent=2))
(DATA / "risk_classes.json").write_text(json.dumps({
    "A": classA.sort_values("criticality", ascending=False)[
        ["instr", "criticality", "corroboration", "nDs"]].to_dict("records"),
    "B": classB.sort_values("IR_raw", ascending=False)[
        ["instr", "criticality", "IR_raw", "R5_soleVars", "soleKeyword",
         "nDs"]].to_dict("records"),
    "C": classC.sort_values("nDs", ascending=False)[
        ["instr", "nDs", "allPubs", "nKeywords", "lastStartYear"]
    ].to_dict("records"),
}, indent=2, default=str))

print(f"scored science instruments : {len(sci)}")
print(f"  generic GCMD class       : {stats['n_generic_class']}")
print(f"  bus subsystem            : {stats['n_bus_subsystem']}")
print(f"tiers  A/B/C               : {stats['n_tier_A']}/{stats['n_tier_B']}/{stats['n_tier_C']}")
print(f"classes A/B/C              : {len(classA)}/{len(classB)}/{len(classC)}")
print(f"Spearman footprint~crit    : rho={rho:.3f}  p={p_rho:.3g}")
print(f"Spearman allPubs~crit      : rho={rho_pub:.3f}  p={p_pub:.3g}")
print(f"top-10 overlap             : {len(overlap)}  {overlap}")
print("\nTop 15 by criticality:")
print(sci_out.head(15)[["rank", "instr", "criticality", "footprint_score",
                        "corroboration", "tier", "riskClass"]].to_string(index=False))
print("\nClass C (footprint, no uptake) top 12:")
print(classC.nlargest(12, "nDs")[["instr", "nDs", "allPubs", "nKeywords"]]
      .to_string(index=False))
print("\nClass B (narrow, irreplaceable):")
print(classB.sort_values("IR_raw", ascending=False)
      [["instr", "criticality", "IR_raw", "nDs", "R5_soleVars"]]
      .to_string(index=False))
print("\nRoute agreement (Spearman):")
print(route_corr.round(2).to_string())
print("\nUnder-recognised (criticality rank far ahead of footprint rank):")
print(under.to_string(index=False))
print("\nVolume-heavy, dependency-light (footprint rank far ahead of criticality):")
print(over.to_string(index=False))
print(f"\nSpearman fracFootprint~crit : rho={rho_frac:.3f} p={p_frac:.3g}")
print(f"top-25 overlap             : {len(overlap25)}")

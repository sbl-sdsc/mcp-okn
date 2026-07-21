#!/usr/bin/env python3
"""
02_score.py -- Confidence tiers, co-location score and stratifications.

Inputs : data/cells_master.tsv, data/colocated_facilities_all.tsv,
         data/ring_pfas_facilities_named.csv, data/analyte*.csv, data/cas_to_*.csv,
         data/ice_functional_use.csv
Outputs: data/cells_ranked.tsv      the ranked results table (one row per cell)
         data/strat_*.tsv           stratification tables
         data/stats.json            every headline number used in the report
"""
import json
import os
import numpy as np
import pandas as pd

D = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# --------------------------------------------------------------------------
# NAICS -> PFAS source-strength prior.
# Grouping follows the sector list EPA uses to flag "industries that may be
# handling PFAS" in the PFAS Analytic Tools, split by the directness of the
# documented release pathway. Prefix match, longest prefix wins.
# --------------------------------------------------------------------------
NAICS_PRIOR = {
    # --- HIGH: PFAS manufacture, formulation, or a documented primary release route
    "3252": ("High", 1.0, "Resin / synthetic fibre manufacturing"),
    "3251": ("High", 1.0, "Basic chemical manufacturing"),
    "3255": ("High", 1.0, "Paint, coating & adhesive manufacturing"),
    "3259": ("High", 1.0, "Other chemical product manufacturing"),
    "32521": ("High", 1.0, "Plastics material & resin manufacturing"),
    "3328": ("High", 1.0, "Metal coating & electroplating"),
    "3221": ("High", 1.0, "Pulp, paper & paperboard mills"),
    "32222": ("High", 1.0, "Paper coating & laminating"),
    "3131": ("High", 1.0, "Textile fibre & yarn mills"),
    "3132": ("High", 1.0, "Fabric mills"),
    "3133": ("High", 1.0, "Textile & fabric finishing / coating"),
    "3141": ("High", 1.0, "Textile furnishings mills"),
    "3149": ("High", 1.0, "Other textile product mills"),
    "3161": ("High", 1.0, "Leather & hide tanning and finishing"),
    "4881": ("High", 1.0, "Airport operations (AFFF fire training)"),
    "92811": ("High", 1.0, "National security / military installation (AFFF)"),
    "22132": ("High", 1.0, "Sewage treatment (effluent & biosolids)"),
    "5622": ("High", 1.0, "Waste treatment & disposal (landfill, hazardous waste)"),
    "5621": ("High", 1.0, "Waste collection"),
    # --- MODERATE: plausible PFAS handling or secondary release
    "42471": ("Moderate", 0.6, "Petroleum bulk stations & terminals"),
    "4247": ("Moderate", 0.6, "Petroleum merchant wholesalers"),
    "324": ("Moderate", 0.6, "Petroleum & coal products manufacturing"),
    "326": ("Moderate", 0.6, "Plastics & rubber products manufacturing"),
    "3344": ("Moderate", 0.6, "Semiconductor & electronic component manufacturing"),
    "3345": ("Moderate", 0.6, "Instrument manufacturing"),
    "3359": ("Moderate", 0.6, "Other electrical equipment manufacturing"),
    "323": ("Moderate", 0.6, "Printing & related support activities"),
    "42469": ("Moderate", 0.6, "Chemical & allied products wholesalers"),
    "3329": ("Moderate", 0.6, "Other fabricated metal product manufacturing"),
    "3399": ("Moderate", 0.6, "Other miscellaneous manufacturing"),
    "2211": ("Moderate", 0.6, "Electric power generation"),
    "22131": ("Moderate", 0.6, "Water supply systems"),
    "5629": ("Moderate", 0.6, "Remediation & other waste services"),
}


def naics_prior(code):
    code = ("" if pd.isna(code) else str(code)).strip()
    if not code:
        return ("Unclassified", np.nan, "No NAICS on record")
    for n in range(min(6, len(code)), 1, -1):
        k = code[:n]
        if k in NAICS_PRIOR:
            return NAICS_PRIOR[k]
    return ("Low", 0.3, "Other EPA PFAS-flagged industry")


cells = pd.read_csv(os.path.join(D, "cells_master.tsv"), sep="\t", dtype={"cid": str,
                                                                          "stateFips": str,
                                                                          "countyFips": str})
cofac = pd.read_csv(os.path.join(D, "colocated_facilities_all.tsv"), sep="\t", dtype=str)
cofac["isPfas"] = cofac["isPfas"].astype(int)
ring = pd.read_csv(os.path.join(D, "ring_pfas_facilities_named.csv"), dtype=str)

universe = set(cells["cid"])
cofac = cofac[cofac["cid"].isin(universe)].copy()
ring = ring[ring["cid"].isin(universe)].copy()

# ---------------------------------------------------------------- industry prior per cell
def apply_prior(df, code_col):
    p = df[code_col].apply(naics_prior)
    df["priorClass"] = [x[0] for x in p]
    df["priorWeight"] = [x[1] for x in p]
    df["industryGroup"] = [x[2] for x in p]
    return df


cofac = apply_prior(cofac, "naicsCode")
ring = apply_prior(ring, "naics")

same_pfas = cofac[cofac["isPfas"] == 1]
# strongest same-cell PFAS-flagged industry
best_same = (same_pfas.dropna(subset=["priorWeight"])
             .sort_values("priorWeight", ascending=False)
             .groupby("cid")
             .agg(sameTopWeight=("priorWeight", "first"),
                  sameTopIndustry=("industryGroup", "first"),
                  sameTopNaics=("naicsCode", "first"),
                  sameTopFacility=("facName", "first") if "facName" in same_pfas else ("naicsLabel", "first"))
             .reset_index())
# facility names for same-cell PFAS facilities come from a separate extract
named = pd.read_csv(os.path.join(D, "pfas_facilities_named.csv"), dtype=str)
named = named[named["cid"].isin(universe)].copy()
named = apply_prior(named, "naicsCode")
best_named = (named.dropna(subset=["priorWeight"])
              .sort_values("priorWeight", ascending=False)
              .groupby("cid")
              .agg(sameTopFacilityName=("facName", "first"))
              .reset_index())

best_ring = (ring.dropna(subset=["priorWeight"])
             .sort_values("priorWeight", ascending=False)
             .groupby("cid")
             .agg(ringTopWeight=("priorWeight", "first"),
                  ringTopIndustry=("industryGroup", "first"),
                  ringTopNaics=("naics", "first"),
                  ringTopFacilityName=("facName", "first"))
             .reset_index())

cells = (cells.merge(best_same.drop(columns=[c for c in best_same.columns if c == "sameTopFacility"]),
                     on="cid", how="left")
              .merge(best_named, on="cid", how="left")
              .merge(best_ring, on="cid", how="left"))

# ---------------------------------------------------------------- score components
def sat(x, k):
    return np.minimum(1.0, np.log1p(x) / np.log1p(k))


p_same = sat(cells["nPfasFac"], 5)
p_ring = sat(cells["nRingPfasFac"], 10)
f_same = sat(cells["nFac"], 20)
f_ring = sat(cells["nRingFac"], 40)
cells["c_proximity"] = np.maximum.reduce([p_same, 0.60 * p_ring, 0.25 * f_same, 0.10 * f_ring])

cells["detFreq"] = np.where(cells["nObs"] > 0, cells["nDet"] / cells["nObs"].replace(0, np.nan), np.nan)
cells["c_detFreq"] = cells["detFreq"]

cells["c_detIntensity"] = np.where(
    cells["maxNgL"].notna(),
    np.minimum(1.0, np.log10(1 + cells["maxNgL"].fillna(0)) / np.log10(1001.0)),
    np.nan)

cells["c_analyteBreadth"] = np.minimum(1.0, cells["nDetAnalytes"] / 20.0)

cells["c_industryPrior"] = cells[["sameTopWeight", "ringTopWeight"]].max(axis=1)
cells.loc[(cells["nPfasFac"] == 0) & (cells["nRingPfasFac"] == 0), "c_industryPrior"] = 0.0

WEIGHTS = {"c_proximity": 0.35, "c_detIntensity": 0.25, "c_detFreq": 0.20,
           "c_analyteBreadth": 0.10, "c_industryPrior": 0.10}

comp = cells[list(WEIGHTS)]
w = pd.Series(WEIGHTS)
avail = comp.notna()
num = (comp.fillna(0) * w).sum(axis=1)
den = (avail * w).sum(axis=1)
cells["score"] = 100.0 * num / den.replace(0, np.nan)
cells["scoreComponentsUsed"] = avail.sum(axis=1)
# The score ranks DETECTIONS by attribution plausibility. A cell with no
# analyte-linked observation, or with observations but no detection, carries no
# detection to attribute, so it is not scored (it is reported separately).
cells.loc[(cells["nObs"] == 0) | (cells["nDet"] == 0), "score"] = np.nan

# ---------------------------------------------------------------- confidence tiers
def tier(r):
    if r["nObs"] == 0:
        return "X"                      # sample point present but no analyte-linked observation
    if r["nDet"] == 0:
        return "N"                      # screened, no detection
    if r["nPfasFac"] > 0:
        return "A"                      # PFAS-relevant facility in the SAME cell
    if r["nRingPfasFac"] > 0:
        return "B"                      # PFAS-relevant facility in an ADJACENT cell
    if r["nFac"] > 0 or r["nRingFac"] > 0:
        return "C"                      # only non-PFAS-flagged regulated facilities nearby
    return "D"                          # detection with no regulated facility in the window


cells["tier"] = cells.apply(tier, axis=1)
cells["window"] = np.where(cells["nPfasFac"] > 0, "same-cell",
                   np.where(cells["nRingPfasFac"] > 0, "1-ring",
                   np.where(cells["nFac"] > 0, "same-cell (unflagged)",
                   np.where(cells["nRingFac"] > 0, "1-ring (unflagged)", "none"))))

# corroborating KGs per row (for the HTML sources column)
def sources(r):
    s = ["sawgraph", "spatialkg"]
    if r["nFac"] > 0 or r["nRingFac"] > 0:
        s.append("fiokg")
    return s


cells["sourceList"] = cells.apply(lambda r: ";".join(sources(r)), axis=1)
cells["nSources"] = cells["sourceList"].str.count(";") + 1

cells.to_csv(os.path.join(D, "cells_scored.tsv"), sep="\t", index=False)

ranked = (cells[cells["score"].notna()]
          .sort_values(["score", "nDet"], ascending=False).reset_index(drop=True))
ranked.insert(0, "rank", np.arange(1, len(ranked) + 1))
ranked.to_csv(os.path.join(D, "cells_ranked.tsv"), sep="\t", index=False)

# Screened-negative control set: co-located but no detection -- the false-positive
# check on the co-location hypothesis.
neg = (cells[cells["tier"] == "N"]
       .sort_values(["nPfasFac", "nRingPfasFac", "nFac"], ascending=False)
       .reset_index(drop=True))
neg.to_csv(os.path.join(D, "cells_screened_negative.tsv"), sep="\t", index=False)

# ---------------------------------------------------------------- stratifications
strat = {}

# by tier
strat["tier"] = (cells.groupby("tier")
                 .agg(nCells=("cid", "size"), medScore=("score", "median"),
                      medDetFreq=("detFreq", "median"), medMaxNgL=("maxNgL", "median"),
                      nDetections=("nDet", "sum"))
                 .reset_index())

# by state
strat["state"] = (cells.groupby("stateName")
                  .agg(nCells=("cid", "size"),
                       nTierA=("tier", lambda s: (s == "A").sum()),
                       nTierB=("tier", lambda s: (s == "B").sum()),
                       nDetCells=("nDet", lambda s: (s > 0).sum()),
                       nObs=("nObs", "sum"), nDet=("nDet", "sum"),
                       medMaxNgL=("maxNgL", "median"), maxNgL=("maxNgL", "max"),
                       nPfasFac=("nPfasFac", "sum"))
                  .reset_index().sort_values("nCells", ascending=False))
strat["state"]["detRate"] = strat["state"]["nDet"] / strat["state"]["nObs"]

# by county (top)
strat["county"] = (cells[cells["tier"].isin(["A", "B"])]
                   .groupby(["stateName", "countyName"])
                   .agg(nCells=("cid", "size"), nTierA=("tier", lambda s: (s == "A").sum()),
                        medScore=("score", "median"), maxNgL=("maxNgL", "max"),
                        nPfasFac=("nPfasFac", "sum"), nRingPfasFac=("nRingPfasFac", "sum"))
                   .reset_index().sort_values(["nTierA", "nCells"], ascending=False))

# by industry group -- how often each PFAS-relevant sector is the top co-located industry
ind_same = same_pfas.groupby("industryGroup").agg(nFacilities=("frsId", "nunique"),
                                                  nCells=("cid", "nunique")).reset_index()
ind_same["window"] = "same-cell"
ind_ring = ring.groupby("industryGroup").agg(nFacilities=("frsId", "nunique"),
                                             nCells=("cid", "nunique")).reset_index()
ind_ring["window"] = "1-ring"
strat["industry"] = pd.concat([ind_same, ind_ring], ignore_index=True)
strat["industry"]["priorClass"] = strat["industry"]["industryGroup"].map(
    {v[2]: v[0] for v in NAICS_PRIOR.values()}).fillna("Low")

# NAICS detail for PFAS-flagged co-located facilities
naics_detail = (same_pfas.groupby(["naicsCode", "naicsLabel", "industryGroup", "priorClass"])
                .agg(nFacilities=("frsId", "nunique"), nCells=("cid", "nunique"))
                .reset_index().sort_values("nFacilities", ascending=False))
strat["naics_same_cell"] = naics_detail

# ---------------------------------------------------------------- chemistry
an = pd.read_csv(os.path.join(D, "analytes.csv"), dtype=str)
freq = pd.read_csv(os.path.join(D, "analyte_detection_freq.csv"))
for c in ("nObs", "nDet", "nCells"):
    freq[c] = pd.to_numeric(freq[c], errors="coerce").fillna(0).astype(int)
an_ok = an[an["cas"].notna() & (an["cas"] != "")].drop_duplicates("param")
an_lab = an.drop_duplicates("param")[["param", "paramLabel", "dtxsid", "dssLabel"]]
chem = (freq.merge(an_lab, on="param", how="left")
            .merge(an_ok[["param", "cas"]], on="param", how="left"))
chem["detFreq"] = chem["nDet"] / chem["nObs"]

ice = pd.read_csv(os.path.join(D, "cas_to_ice.csv"), dtype=str)
tox = pd.read_csv(os.path.join(D, "cas_to_toxcast.csv"), dtype=str).astype({"nAssayEndpoints": int})
use = pd.read_csv(os.path.join(D, "ice_functional_use.csv"), dtype=str)
use_agg = (use.groupby("cas")["useCategory"].apply(lambda s: "; ".join(sorted(set(s)))).reset_index()
             .rename(columns={"useCategory": "functionalUse"}))

chem = (chem.merge(ice[["cas", "iceLabel"]], on="cas", how="left")
            .merge(tox, on="cas", how="left")
            .merge(use_agg, on="cas", how="left"))
chem["inICE"] = chem["iceLabel"].notna()
chem["inToxCast"] = chem["nAssayEndpoints"].notna()
chem = chem.sort_values("nDet", ascending=False)
strat["analytes"] = chem

# functional-use x detection cross-tab
uf = chem[chem["functionalUse"].notna()].copy()
rows = []
for _, r in uf.iterrows():
    for u in r["functionalUse"].split("; "):
        rows.append({"functionalUse": u, "param": r["param"], "nObs": r["nObs"],
                     "nDet": r["nDet"], "nCells": r["nCells"]})
fu = pd.DataFrame(rows)
strat["functional_use"] = (fu.groupby("functionalUse")
                           .agg(nAnalytes=("param", "nunique"), nObs=("nObs", "sum"),
                                nDet=("nDet", "sum"), maxCells=("nCells", "max"))
                           .reset_index())
strat["functional_use"]["detFreq"] = strat["functional_use"]["nDet"] / strat["functional_use"]["nObs"]

for k, v in strat.items():
    v.to_csv(os.path.join(D, f"strat_{k}.tsv"), sep="\t", index=False)

# ---------------------------------------------------------------- headline stats
tc = cells["tier"].value_counts().to_dict()
S = {
    "kg_count": 5,
    "universe_cells": int(len(cells)),
    "sample_points": int(cells["nPts"].sum()),
    "sample_points_geo": int(cells["nPtsGeo"].sum()),
    "states": int(cells["stateName"].nunique()),
    "counties": int(cells["countyFips"].nunique()),
    "total_obs": int(cells["nObs"].sum()),
    "total_det": int(cells["nDet"].sum()),
    "overall_det_rate": round(100 * cells["nDet"].sum() / cells["nObs"].sum(), 1),
    "cells_with_detection": int((cells["nDet"] > 0).sum()),
    "cells_same_cell_fac": int((cells["nFac"] > 0).sum()),
    "colocated_facilities": 12714,
    "cells_same_cell_pfas_fac": int((cells["nPfasFac"] > 0).sum()),
    "same_cell_pfas_facilities": 435,
    "cells_ring_pfas_fac": int((cells["nRingPfasFac"] > 0).sum()),
    "ring_pfas_facilities": int(ring["frsId"].nunique()),
    "tierA": int(tc.get("A", 0)), "tierB": int(tc.get("B", 0)),
    "tierC": int(tc.get("C", 0)), "tierD": int(tc.get("D", 0)),
    "tierN": int(tc.get("N", 0)), "tierX": int(tc.get("X", 0)),
    "evaluable_cells": int((cells["nObs"] > 0).sum()),
    "tierAB": int(tc.get("A", 0) + tc.get("B", 0)),
    "attributable_pct": round(100 * (tc.get("A", 0) + tc.get("B", 0)) / max(1, (cells["nDet"] > 0).sum()), 1),
    "tierN_with_pfas_fac": int(((cells["tier"] == "N") &
                                ((cells["nPfasFac"] > 0) | (cells["nRingPfasFac"] > 0))).sum()),
    "analytes": int(chem["param"].nunique()),
    "analytes_with_cas": int(chem["cas"].notna().sum()),
    "distinct_cas": int(chem["cas"].nunique()),
    "cas_in_ice": int(chem.loc[chem["inICE"], "cas"].nunique()),
    "cas_in_toxcast": int(chem.loc[chem["inToxCast"], "cas"].nunique()),
    "analytes_in_ice": int(chem["inICE"].sum()),
    "analytes_in_toxcast": int(chem["inToxCast"].sum()),
    "cas_with_use": int(chem.loc[chem["functionalUse"].notna(), "cas"].nunique()),
    "use_categories": int(fu["functionalUse"].nunique()),
    "max_conc_ngL": float(cells["maxNgL"].max()),
    "median_maxconc_tierA": round(float(cells.loc[cells["tier"] == "A", "maxNgL"].median()), 1),
    "median_maxconc_tierB": round(float(cells.loc[cells["tier"] == "B", "maxNgL"].median()), 1),
    "median_maxconc_tierC": round(float(cells.loc[cells["tier"] == "C", "maxNgL"].median()), 1),
    "median_maxconc_tierD": round(float(cells.loc[cells["tier"] == "D", "maxNgL"].median()), 1),
    "top_score": round(float(ranked["score"].max()), 1),
    "top_cell": ranked.iloc[0]["cid"],
    "top_county": f"{ranked.iloc[0]['countyName']}, {ranked.iloc[0]['stateName']}",
    "toxcast_max_endpoints": int(tox["nAssayEndpoints"].max()),
    "pfoa_det": int(chem.loc[chem["param"] == "parameter.PFOA_A", "nDet"].iloc[0]),
    "pfos_det": int(chem.loc[chem["param"] == "parameter.PFOS_A", "nDet"].iloc[0]),
}
with open(os.path.join(D, "stats.json"), "w") as fh:
    json.dump(S, fh, indent=2)

print(json.dumps(S, indent=2))
print("\n--- tier table ---")
print(strat["tier"].to_string(index=False))
print("\n--- top 15 ---")
print(ranked.head(15)[["rank", "cid", "score", "tier", "stateName", "countyName",
                       "nDet", "detFreq", "maxNgL", "nDetAnalytes", "nPfasFac",
                       "nRingPfasFac", "sameTopIndustry", "ringTopIndustry"]].to_string(index=False))

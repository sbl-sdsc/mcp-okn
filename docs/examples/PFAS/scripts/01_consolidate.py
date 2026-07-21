#!/usr/bin/env python3
"""
01_consolidate.py -- Consolidate the SPARQL extracts into one cell-level table.

Inputs : data/*.csv  (verbatim CSV results of the logged federated SPARQL queries)
Outputs: data/cells_master.tsv          one row per S2 Level-13 cell with a PFAS sample point
         data/reconciliation.json       row/entity counts used in the report
"""
import json
import glob
import os
import numpy as np
import pandas as pd

D = os.path.join(os.path.dirname(__file__), "..", "data")
D = os.path.abspath(D)


def load(pattern, **kw):
    files = sorted(glob.glob(os.path.join(D, pattern)))
    if not files:
        raise FileNotFoundError(pattern)
    return pd.concat([pd.read_csv(f, dtype=str, **kw) for f in files], ignore_index=True)


rec = {}

# ---------------------------------------------------------------- sample points
pts = load("sample_point_coords_p*.csv")
pts = pts[pts["cid"].notna() & (pts["cid"] != "")]
pts["lat"] = pts["lat"].astype(float)
pts["lon"] = pts["lon"].astype(float)
rec["sample_points_with_coords"] = int(pts["pt"].nunique())
rec["sample_points_egad"] = int((pts["layer"] == "EGAD").sum())
rec["sample_points_wqp"] = int((pts["layer"] == "WQP").sum())

# The authoritative universe: cells that contain a SAWGraph sample point.
universe = sorted(pts["cid"].unique())
rec["universe_cells"] = len(universe)
cells = pd.DataFrame({"cid": universe})

# per-cell layer mix + centroid (mean of its sample points) for mapping
agg = pts.groupby("cid").agg(
    lat=("lat", "mean"), lon=("lon", "mean"),
    nPtsGeo=("pt", "nunique"),
    layers=("layer", lambda s: "+".join(sorted(set(s)))),
)
cells = cells.merge(agg.reset_index(), on="cid", how="left")

# ---------------------------------------------------------------- observations
obs = load("cell_observations_p*.csv")
obs = obs.astype({"nPts": int, "nObs": int, "nAnalytes": int})
rec["cells_with_observations"] = int(obs["cid"].nunique())
cells = cells.merge(obs, on="cid", how="left")

# ---------------------------------------------------------------- detections
det = pd.read_csv(os.path.join(D, "cell_detections.csv"), dtype=str)   # ng/L only, has maxNgL
det_all = load("cell_detections_allunits_p*.csv").astype({"nDet": int, "nDetAnalytes": int})
rec["cells_with_detection_any_unit"] = int(det_all["cid"].nunique())

# maxNgL sentinel: some rows carry the coso:non-detect IRI instead of a number
det["maxNgL_num"] = pd.to_numeric(det["maxNgL"], errors="coerce")
rec["maxNgL_sentinel_rows"] = int(det["maxNgL_num"].isna().sum())
det = det[["cid", "maxNgL_num"]].rename(columns={"maxNgL_num": "maxNgL"})

cells = cells.merge(det_all, on="cid", how="left").merge(det, on="cid", how="left")
for c in ("nDet", "nDetAnalytes"):
    cells[c] = cells[c].fillna(0).astype(int)

# ---------------------------------------------------------------- facilities (same cell)
fac = pd.read_csv(os.path.join(D, "cell_facilities.csv")).astype({"nFac": int})
pfac = pd.read_csv(os.path.join(D, "cell_pfas_facilities.csv")).astype({"nPfasFac": int})
fac["cid"] = fac["cid"].astype(str)
pfac["cid"] = pfac["cid"].astype(str)
cells = cells.merge(fac, on="cid", how="left").merge(pfac, on="cid", how="left")

# ---------------------------------------------------------------- facilities (1-ring)
rfac = pd.read_csv(os.path.join(D, "ring_facilities_all.csv")).astype({"nRingFac": int})
rpfac = pd.read_csv(os.path.join(D, "ring_facilities_pfas.csv")).astype({"nRingPfasFac": int})
rfac["cid"] = rfac["cid"].astype(str)
rpfac["cid"] = rpfac["cid"].astype(str)
cells = cells.merge(rfac, on="cid", how="left").merge(rpfac, on="cid", how="left")

for c in ("nFac", "nPfasFac", "nRingFac", "nRingPfasFac", "nPts", "nObs", "nAnalytes"):
    cells[c] = cells[c].fillna(0).astype(int)

# ---------------------------------------------------------------- geography
geo = load("cell_geography_p*.csv")
geo = geo[geo["cid"].isin(universe)]
# a boundary cell can straddle 2+ counties: keep the alphabetically-first as primary,
# and record the full set.
geo_primary = (geo.sort_values(["cid", "countyFips"])
                  .groupby("cid")
                  .agg(stateFips=("stateFips", "first"),
                       stateName=("stateName", "first"),
                       countyFips=("countyFips", "first"),
                       countyName=("countyName", "first"),
                       nCounties=("countyFips", "nunique"))
                  .reset_index())
rec["cells_with_geography"] = int(geo_primary["cid"].nunique())
cells = cells.merge(geo_primary, on="cid", how="left")
cells["countyName"] = cells["countyName"].str.replace(r",\s*[A-Za-z ]+$", "", regex=True)

# ---------------------------------------------------------------- industry of co-located facilities
cofac = load("colocated_facilities_p*.csv")
cofac["isPfas"] = pd.to_numeric(cofac["isPfas"], errors="coerce").fillna(0).astype(int)
cofac["naicsCode"] = cofac["naicsCode"].fillna("").str.strip()
cofac["naicsLabel"] = cofac["naicsLabel"].fillna("").str.strip()
rec["colocated_facility_rows"] = len(cofac)
rec["colocated_facilities_distinct"] = int(cofac["frsId"].nunique())
rec["colocated_facilities_with_naics"] = int(cofac.loc[cofac["naicsCode"] != "", "frsId"].nunique())

ring_named = pd.read_csv(os.path.join(D, "ring_pfas_facilities_named.csv"), dtype=str)
ring_named["naics"] = ring_named["naics"].fillna("").str.strip()
rec["ring_pfas_facility_rows"] = len(ring_named)
rec["ring_pfas_facilities_distinct"] = int(ring_named["frsId"].nunique())

cells.to_csv(os.path.join(D, "cells_master.tsv"), sep="\t", index=False)
cofac.to_csv(os.path.join(D, "colocated_facilities_all.tsv"), sep="\t", index=False)

rec["cells_with_same_cell_facility"] = int((cells["nFac"] > 0).sum())
rec["cells_with_same_cell_pfas_facility"] = int((cells["nPfasFac"] > 0).sum())
rec["cells_with_ring_facility"] = int((cells["nRingFac"] > 0).sum())
rec["cells_with_ring_pfas_facility"] = int((cells["nRingPfasFac"] > 0).sum())
rec["cells_with_detection"] = int((cells["nDet"] > 0).sum())
rec["total_observations"] = int(cells["nObs"].sum())
rec["total_detections"] = int(cells["nDet"].sum())

with open(os.path.join(D, "reconciliation.json"), "w") as fh:
    json.dump(rec, fh, indent=2)

print(json.dumps(rec, indent=2))
print("\ncells_master.tsv:", cells.shape)
print(cells.head(3).to_string())

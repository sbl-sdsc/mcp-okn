#!/usr/bin/env python3
"""
03_tests.py -- Statistical tests on the proximity->contamination gradient,
plus identification of the top-ranked cells' co-located facilities.
Appends results to data/stats.json and writes data/tests.tsv.
"""
import json
import os
import numpy as np
import pandas as pd
from scipy import stats

D = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
rng = np.random.default_rng(20260720)

cells = pd.read_csv(os.path.join(D, "cells_ranked.tsv"), sep="\t", dtype={"cid": str})
allc = pd.read_csv(os.path.join(D, "cells_master.tsv"), sep="\t", dtype={"cid": str})
S = json.load(open(os.path.join(D, "stats.json")))

rows = []

# ---- 1. Kruskal-Wallis across the four detection tiers on max ng/L -----------
groups = [cells.loc[cells["tier"] == t, "maxNgL"].dropna().values for t in "ABCD"]
H, p = stats.kruskal(*groups)
rows.append(dict(test="Kruskal-Wallis, max ng/L across tiers A/B/C/D",
                 statistic=round(H, 2), p=p,
                 n="/".join(str(len(g)) for g in groups)))

# ---- 2. Pairwise Mann-Whitney (one-sided: closer tier > farther tier) --------
for a, b in [("A", "C"), ("A", "D"), ("B", "D"), ("A", "B"), ("C", "D")]:
    ga = cells.loc[cells["tier"] == a, "maxNgL"].dropna()
    gb = cells.loc[cells["tier"] == b, "maxNgL"].dropna()
    U, p = stats.mannwhitneyu(ga, gb, alternative="greater")
    # rank-biserial effect size
    rb = 2 * U / (len(ga) * len(gb)) - 1
    rows.append(dict(test=f"Mann-Whitney one-sided, max ng/L  {a} > {b}",
                     statistic=round(U, 1), p=p, n=f"{len(ga)}/{len(gb)}",
                     effect=f"rank-biserial {rb:.3f}"))

# ---- 3. Detection frequency across tiers ------------------------------------
groups = [cells.loc[cells["tier"] == t, "detFreq"].dropna().values for t in "ABCD"]
H, p = stats.kruskal(*groups)
rows.append(dict(test="Kruskal-Wallis, detection frequency across tiers A/B/C/D",
                 statistic=round(H, 2), p=p, n="/".join(str(len(g)) for g in groups)))

# ---- 4. Analyte breadth across tiers ----------------------------------------
groups = [cells.loc[cells["tier"] == t, "nDetAnalytes"].dropna().values for t in "ABCD"]
H, p = stats.kruskal(*groups)
rows.append(dict(test="Kruskal-Wallis, distinct analytes detected across tiers A/B/C/D",
                 statistic=round(H, 2), p=p, n="/".join(str(len(g)) for g in groups)))

# ---- 5. Does a PFAS-flagged facility predict DETECTION at all? ---------------
ev = allc[allc["nObs"] > 0].copy()
ev["hasDet"] = ev["nDet"] > 0
ev["nearPfas"] = (ev["nPfasFac"] > 0) | (ev["nRingPfasFac"] > 0)
ct = pd.crosstab(ev["nearPfas"], ev["hasDet"])
odds, pf = stats.fisher_exact(ct.values, alternative="greater")
rows.append(dict(test="Fisher exact, P(detection) | PFAS-flagged facility within 1-ring",
                 statistic=f"OR {odds:.2f}", p=pf,
                 n=f"{int(ct.values.sum())} evaluable cells",
                 effect=f"det rate {100*ev.loc[ev.nearPfas,'hasDet'].mean():.1f}% vs "
                        f"{100*ev.loc[~ev.nearPfas,'hasDet'].mean():.1f}%"))

# ---- 6. Permutation test: is the tier-A median concentration higher than
#         expected if PFAS-facility labels were shuffled across detection cells?
det = cells[cells["maxNgL"].notna()].copy()
obs_med = det.loc[det["tier"] == "A", "maxNgL"].median()
nA = int((det["tier"] == "A").sum())
vals = det["maxNgL"].values
null = np.array([np.median(rng.choice(vals, nA, replace=False)) for _ in range(10000)])
p_perm = (1 + (null >= obs_med).sum()) / (1 + len(null))
rows.append(dict(test="Permutation (10,000x), tier-A median max ng/L vs shuffled labels",
                 statistic=f"observed {obs_med:.1f} ng/L, null median {np.median(null):.1f}",
                 p=p_perm, n=f"{nA} tier-A / {len(det)} scored cells with ng/L"))

# ---- 7. Spearman: score vs max concentration (internal coherence) -----------
rho, p_rho = stats.spearmanr(det["score"], det["maxNgL"])
rows.append(dict(test="Spearman, co-location score vs max ng/L (scored cells)",
                 statistic=f"rho {rho:.3f}", p=p_rho, n=str(len(det))))
kw_H_conc = float(stats.kruskal(*[cells.loc[cells["tier"] == t, "maxNgL"].dropna().values
                                  for t in "ABCD"])[0])

tests = pd.DataFrame(rows)
tests["p"] = tests["p"].apply(lambda v: f"{v:.2e}" if isinstance(v, float) and v < 1e-3
                              else (f"{v:.4f}" if isinstance(v, float) else v))
tests.to_csv(os.path.join(D, "tests.tsv"), sep="\t", index=False)
print(tests.to_string(index=False))

# ---- named facilities for the top cells -------------------------------------
named = pd.read_csv(os.path.join(D, "pfas_facilities_named.csv"), dtype=str)
ring = pd.read_csv(os.path.join(D, "ring_pfas_facilities_named.csv"), dtype=str)
top = cells.head(20)[["rank", "cid", "score", "tier", "stateName", "countyName",
                      "nDet", "maxNgL", "nDetAnalytes", "nPfasFac", "nRingPfasFac"]]
det_named = []
for _, r in top.iterrows():
    s = named[named["cid"] == r["cid"]]["facName"].dropna().unique()[:4]
    g = ring[ring["cid"] == r["cid"]]["facName"].dropna().unique()[:4]
    det_named.append("; ".join(s) if len(s) else ("[ring] " + "; ".join(g) if len(g) else ""))
top = top.copy()
top["colocatedFacilities"] = det_named
top.to_csv(os.path.join(D, "top20_named.tsv"), sep="\t", index=False)
print("\n--- top 20 with facility names ---")
print(top[["rank", "countyName", "stateName", "maxNgL", "nDet", "colocatedFacilities"]].to_string(index=False))

# ---- tier N false positives --------------------------------------------------
S["fisher_or"] = round(float(odds), 2)
S["det_rate_near_pfas"] = round(100 * ev.loc[ev.nearPfas, "hasDet"].mean(), 1)
S["det_rate_far"] = round(100 * ev.loc[~ev.nearPfas, "hasDet"].mean(), 1)
S["perm_p"] = float(p_perm)
S["spearman_rho"] = round(float(rho), 3)
S["kw_H_conc"] = round(kw_H_conc, 1)
S["perm_null_median"] = round(float(np.median(null)), 1)
json.dump(S, open(os.path.join(D, "stats.json"), "w"), indent=2)
print("\nstats.json updated")

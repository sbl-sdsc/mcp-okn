#!/usr/bin/env python3
"""Compute N-corrected geographic concentration, software fragility, and the
intersection short list for the Supply-Chain-Fragility study."""
import json, pandas as pd, numpy as np
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"

ind   = pd.read_csv(D/"sudokn_industry_national.csv")
lab   = pd.read_csv(D/"naics_labels.csv", dtype={"naics":str})
cs    = pd.read_csv(D/"conc_state.csv")
cz    = pd.read_csv(D/"conc_zip3.csv")
cc    = pd.read_csv(D/"conc_county.csv")
fio   = pd.read_csv(D/"fiokg_industry_national.csv")
for df in (ind, cs, cz, cc, fio):
    df["naics"] = df["naics"].astype(str)

BASE_HHI_COUNTY = 0.00644361     # whole 332 sector, county grain (logged query)
BASE_PLACED     = 13277
BASE_COUNTIES   = 1705

m = (ind.merge(lab, on="naics", how="left")
        .merge(cs[["naics","hhiState","topStateFirms","nStates"]], on="naics", how="left")
        .merge(cz[["naics","hhiZip3","topZip3Firms","nZip3"]], on="naics", how="left")
        .merge(cc, on="naics", how="left")
        .merge(fio, on="naics", how="left"))

# --- N-corrected concentration -------------------------------------------------
# Under a null where an industry's n firms are drawn from the whole-sector county
# distribution p, E[HHI] = 1/n + (1 - 1/n) * sum(p^2).  The ratio observed/expected
# is therefore ~1 for an industry no more clustered than the sector as a whole.
n = m["placed"].astype(float)
m["expHhiCounty"] = 1.0/n + (1.0 - 1.0/n) * BASE_HHI_COUNTY
m["concIndex"]    = m["hhiCounty"] / m["expHhiCounty"]
m["effCounties"]  = 1.0 / m["hhiCounty"]
m["topCountyShare"] = m["topCountyFirms"] / m["placed"]
m["empPerFirm"]   = m["empSum"] / m["empN"]
m["facPerFirm"]   = m["facilities"] / m["firms"]

# --- software fragility --------------------------------------------------------
blast = pd.read_csv(D/"software_blast_radius.csv")
vuln  = pd.read_csv(D/"software_vuln_load.csv")
sw = blast.merge(vuln, on="name", how="left")
TOTAL_SW = 803769
sw["pctOfEcosystemDependent"] = 100.0*sw["dependentPkgs"]/TOTAL_SW
sw["vulnVersionShare"] = sw["vulnVersions"]/sw["versions"]
# fragility = log-blast x (1 + cve load) ; rank-normalised to 0-100
r_blast = sw["dependentPkgs"].rank(pct=True)
r_cve   = sw["cves"].rank(pct=True)
r_vshare= sw["vulnVersionShare"].rank(pct=True)
sw["fragilityScore"] = (100*(0.5*r_blast + 0.3*r_cve + 0.2*r_vshare)).round(1)
sw = sw.sort_values("fragilityScore", ascending=False)

istack = pd.read_csv(D/"industrial_stack.csv")
istack["hubExposed"] = istack["upstreamHubDeps"] > 0

# --- intersection short list ---------------------------------------------------
# Software-fragility inheritance per industry, two evidence routes:
#  R1 (direct, KG edge): NAICS -> named manufacturer -> hardware -> CVE
#  R2 (inferred, labelled): process-technology software stack for that industry
bridge = pd.read_csv(D/"industry_hardware_cve_bridge.csv", dtype={"naics":str})
b332 = bridge[bridge.naics.str.startswith("332")].groupby("naics").agg(
    bridgeFirms=("firmName","count"), bridgeCves=("cves","sum"),
    bridgeHardware=("hwProducts","sum")).reset_index()
m = m.merge(b332, on="naics", how="left")
m[["bridgeFirms","bridgeCves","bridgeHardware"]] = m[["bridgeFirms","bridgeCves","bridgeHardware"]].fillna(0)

# Labelled inference: which process-software families each industry depends on.
# Mapping is analyst-assigned from NAICS process definitions, NOT a KG edge.
STACK = {
 "332710":["ezdxf","pyserial","pygcode","cadquery","trimesh","pymodbus","pylogix","opencv-python"],
 "332721":["ezdxf","pyserial","pygcode","pymodbus","pylogix","opencv-python"],
 "332722":["ezdxf","pyserial","pygcode","pymodbus","opencv-python"],
 "332117":["numpy-stl","trimesh","meshio","pymodbus","opencv-python"],
 "332111":["meshio","pymodbus","python-snap7","opencv-python"],
 "332112":["meshio","pymodbus","python-snap7"],
 "332114":["ezdxf","pymodbus","pylogix"],
 "332119":["ezdxf","pyserial","pymodbus","pylogix","opencv-python"],
 "332216":["ezdxf","pyserial","pygcode","opencv-python"],
 "332215":["ezdxf","opencv-python"],
 "332311":["ezdxf","ifcopenshell","shapely","pymodbus"],
 "332312":["ezdxf","ifcopenshell","shapely","pyserial","pymodbus"],
 "332313":["ezdxf","shapely","pyserial","pymodbus"],
 "332321":["ezdxf","ifcopenshell","shapely"],
 "332322":["ezdxf","pyserial","pymodbus","shapely"],
 "332323":["ezdxf","ifcopenshell","shapely"],
 "332410":["meshio","ezdxf","asyncua","pymodbus"],
 "332420":["meshio","ezdxf","asyncua","pymodbus"],
 "332431":["opencv-python","pymodbus","pylogix","asyncua"],
 "332439":["opencv-python","pymodbus","pylogix"],
 "332510":["ezdxf","pyserial","opencv-python"],
 "332613":["pyserial","pymodbus","opencv-python"],
 "332618":["pyserial","pymodbus","opencv-python"],
 "332811":["asyncua","pymodbus","python-snap7","pyads","opcua"],
 "332812":["asyncua","pymodbus","python-snap7","pyads","opcua","opencv-python"],
 "332813":["asyncua","pymodbus","python-snap7","pyads","opcua","bacpypes","opencv-python"],
 "332911":["ezdxf","meshio","asyncua","pymodbus","pylogix"],
 "332912":["ezdxf","meshio","asyncua","pymodbus","pylogix"],
 "332913":["ezdxf","meshio","pymodbus"],
 "332919":["ezdxf","meshio","asyncua","pymodbus"],
 "332991":["opencv-python","pyserial","pymodbus"],
 "332992":["opencv-python","pymodbus","pylogix","asyncua"],
 "332993":["opencv-python","pymodbus","pylogix","asyncua"],
 "332994":["ezdxf","cadquery","opencv-python","pymodbus"],
 "332996":["ezdxf","shapely","asyncua","pymodbus","python-snap7"],
 "332999":["ezdxf","pyserial","pymodbus","opencv-python"],
}
ist = istack.set_index("name")
OT = {"pymodbus","python-snap7","pylogix","pycomm3","pyads","asyncua","opcua",
      "canopen","python-can","bacpypes"}
def stack_metrics(code):
    pkgs = [p for p in STACK.get(code, []) if p in ist.index]
    if not pkgs:
        return pd.Series({"stackPkgs":0,"stackOT":0,"stackCves":0,
                          "stackHubExposed":0,"stackBlast":0})
    s = ist.loc[pkgs]
    return pd.Series({"stackPkgs":len(pkgs),
                      "stackOT":len([p for p in pkgs if p in OT]),
                      "stackCves":int(s.cves.sum()),
                      "stackHubExposed":int((s.upstreamHubDeps>0).sum()),
                      "stackBlast":int(s.dependentPkgs.max())})
m = pd.concat([m, m["naics"].apply(stack_metrics)], axis=1)

# --- industry software-fragility score ----------------------------------------
# Four additive components, each defensible from a logged query except the
# stack->industry mapping itself, which is an analyst-assigned inference (see
# report S3/S6 and the reproducibility spec):
#   OT depth      how many distinct industrial-protocol / PLC-facing packages the
#                 industry's process technology needs (continuous, recipe-driven
#                 automation needs more than discrete job-shop machining)
#   CVE load      recorded CVEs on those packages (securechainkg)
#   hub exposure  how many of them rest directly on a top-blast-radius hub
#   hardware CVE  a KG-grounded NAICS->vendor->hardware->CVE path exists
raw = (3.0*m["stackOT"] + 1.5*m["stackCves"] + 2.0*m["stackHubExposed"]
       + 8.0*(m["bridgeCves"]>0).astype(int))
m["swFragility"] = (100.0*raw/raw.max()).round(1)
q33, q67 = m["swFragility"].quantile([1/3, 2/3])
m["swTier"] = np.select([m.swFragility>=q67, m.swFragility>=q33],
                        ["high","moderate"], default="low")
m["concTier"] = np.select([m.concIndex>=2.0, m.concIndex>=1.5],
                          ["concentrated","moderate"], default="diffuse")

# --- evidence tiers -----------------------------------------------------------
def tier(r):
    if r.placed >= 100 and r.concIndex >= 1.5: return "A"
    if r.placed >= 40  and r.concIndex >= 1.3: return "B"
    return "C"
m["evidenceTier"] = m.apply(tier, axis=1)

# --- joint risk: BOTH axes, rank-combined ------------------------------------
# A hard AND on both axes yields almost nothing, because the two axes are
# NEGATIVELY correlated (see report S5.4): the most software-exposed processes
# are the most ubiquitous ones.  So rank on both and multiply the percentiles,
# restricting to industries with an adequate observed firm base.
elig = m.placed >= 60
m["concPct"] = m.loc[elig,"concIndex"].rank(pct=True)
m["swPct"]   = m.loc[elig,"swFragility"].rank(pct=True)
m["jointRisk"] = (100*m["concPct"]*m["swPct"]).round(1)
m["jointRank"] = m["jointRisk"].rank(ascending=False, method="min")
m["shortList"] = m["jointRank"] <= 8
rho = m.loc[elig,["concIndex","swFragility"]].corr(method="spearman").iloc[0,1]
m = m.sort_values(["shortList","jointRisk"], ascending=[False,False])

out = m[["naics","label","firms","placed","empSum","empPerFirm","facilities",
         "facPerFirm","hhiCounty","expHhiCounty","concIndex","effCounties",
         "topCountyFirms","topCountyShare","nCounties","hhiZip3","hhiState",
         "stackPkgs","stackOT","stackCves","stackHubExposed","stackBlast","bridgeFirms",
         "bridgeCves","swFragility","swTier","concTier","jointRisk","jointRank","evidenceTier","shortList"]]
out.to_csv(D/"industry_master.csv", index=False)
sw.to_csv(D/"software_fragility_scored.csv", index=False)

stats = {
 "n_kgs": 6,
 "smm_firms_total": int(ind.firms.sum()),
 "smm_emp_total": int(ind.empSum.sum()),
 "smm_industries": int(len(ind)),
 "smm_firms_placed": BASE_PLACED,
 "smm_counties": BASE_COUNTIES,
 "base_hhi_county": BASE_HHI_COUNTY,
 "eff_counties_sector": round(1/BASE_HHI_COUNTY,0),
 "firms_with_year": 574,
 "pct_firms_with_year": round(100*574/int(ind.firms.sum()),1),
 "median_founding_decade": "2000s",
 "frs_facilities_332": 27200,
 "frs_counties_332": 2130,
 "sw_packages": 803769,
 "sw_versions": 8545123,
 "sw_dep_edges": 29574574,
 "sw_cves": 312388,
 "sw_cwe_types": 741,
 "sw_vuln_versions": 79476,
 "sw_pkgs_with_contributors": 679,
 "pct_pkgs_with_contributors": round(100*679/803769,3),
 "numpy_dependents": 70032,
 "numpy_dependent_pct": round(100*70032/803769,1),
 "requests_dependents": 64097,
 "pandas_dependents": 45991,
 "hardware_bridge_names": 20,
 "hardware_bridge_naics": 21,
 "hardware_bridge_hw": 10373,
 "hw_vuln_versions": 58836,
 "hw_cves": 22668,
 "industrial_pkgs_checked": int(len(istack)),
 "industrial_pkgs_hub_exposed": int(istack.hubExposed.sum()),
 "shortlist_n": int(m.shortList.sum()),
 "tierA": int((m.evidenceTier=="A").sum()),
 "tierB": int((m.evidenceTier=="B").sum()),
 "tierC": int((m.evidenceTier=="C").sum()),
 "spearman_conc_vs_sw": round(float(rho),2),
 "eligible_industries": int(elig.sum()),
 "naics_shared_sudokn_secchain": 35,
 "naics_shared_fiokg_secchain": 301,
 "sectors_shared_sudokn_secchain": 58,
 "naics_shared_fiokg_sudokn": 60,
 "sw_ecosystems": 6,
 "pypi_packages": 603111,
 "cargo_packages": 180196,
 "copyleft_top_blast": 2613,
 "harris_industries": 9,
 "harris_firms": 141,
 "sdoh_variables": 84,
 "top_conc_naics": m.sort_values("concIndex",ascending=False).iloc[0].naics,
 "top_conc_label": m.sort_values("concIndex",ascending=False).iloc[0].label,
 "conc_q67": round(float(q67),1),
 "concentrated_n": int((m.concTier=="concentrated").sum()),
 "hi_sw_n": int((m.swTier=="high").sum()),
}
sl = m[m.shortList]
stats["shortlist_firms"] = int(sl.placed.sum())
stats["shortlist_emp"] = int(sl.empSum.sum())
stats["shortlist_facilities"] = int(sl.facilities.sum())
# Display formatting: the report interpolates these straight into prose and KPI cards,
# so store them thousands-separated. Keys used in arithmetic stay numeric.
COMMA = ["smm_firms_total","smm_emp_total","smm_firms_placed","smm_counties",
 "frs_facilities_332","frs_counties_332","sw_packages","sw_versions","sw_dep_edges",
 "sw_cves","sw_cwe_types","sw_vuln_versions","sw_pkgs_with_contributors","numpy_dependents",
 "requests_dependents","pandas_dependents","hw_vuln_versions","hw_cves","hardware_bridge_hw",
 "shortlist_firms","shortlist_emp","shortlist_facilities","firms_with_year","pypi_packages",
 "cargo_packages","copyleft_top_blast","harris_firms"]
stats_num = dict(stats)
for k in COMMA:
    if k in stats: stats[k] = f"{int(stats[k]):,}"
json.dump(stats, open(D/"stats.json","w"), indent=1)
json.dump(stats_num, open(D/"stats_numeric.json","w"), indent=1)

print("=== SHORT LIST ===")
print(sl[["naics","label","placed","empSum","concIndex","effCounties","topCountyShare","swFragility","stackOT","stackCves","jointRisk","evidenceTier"]].to_string(index=False))
print("\n=== all industries, concentration index ===")
print(m[["naics","label","placed","concIndex","swFragility","swTier","concTier","jointRisk","evidenceTier","shortList"]].to_string(index=False))
print("\n=== top software fragility ===")
print(sw.head(15)[["name","ecosystem","dependentPkgs","cves","fragilityScore"]].to_string(index=False))
print("\nstats:", json.dumps(stats, indent=1))

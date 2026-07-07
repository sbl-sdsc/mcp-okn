"""Compute cross-source corroboration detail and ranking CSVs for chemicals."""

import csv
from collections import defaultdict
from pathlib import Path

D = "/sessions/nifty-festive-gauss/mnt/outputs/exposome/data"


def load(fn):
    """Load a CSV file from the data directory as a list of dict rows."""
    with Path(f"{D}/{fn}").open() as f:
        return list(csv.DictReader(f))


chem = load("chemicals.csv")
gxa = {r["symbol"] for r in load("gxa_expression.csv")}
rdkg = {r["symbol"] for r in load("rdkg_rare_disease.csv")}
prokn = {r["symbol"] for r in load("prokn_protein.csv")}
spoke = load("spoke_gene_disease.csv")
bridge = {
    r["doid"].replace(":", "_"): r["mondo"]
    for r in load("disease_bridge_doid_mondo.csv")
}
oard_mondo = {r["mondo"] for r in load("oard_disease_phenotype.csv")}

# spoke gene->disease map
g2d = defaultdict(list)  # symbol -> [(doid,disease)]
for r in spoke:
    g2d[r["symbol"]].append((r["doid"], r["disease"]))

# AOP-curated targets per chemical (from aopwiki AOP structure)
AOP = {
    "BPA": {"ESR1": "MIE", "ESR2": "KE", "GPER1": "MIE", "GATA3": "KE"},
    "TBBPA": {"TTR": "MIE", "THRA": "KE", "THRB": "KE"},
}
# estrogenic class targets shared by active bisphenols (assay/literature)
ER_CLASS = ["ESR1", "ESR2"]
active = {
    r["abbrev"]: (int(r["toxcast_active"]) if r["toxcast_active"] else 0) for r in chem
}
tested = {
    r["abbrev"]: (int(r["toxcast_tested"]) if r["toxcast_tested"] else 0) for r in chem
}
HAZ = {"BPA"}  # chemicals with extracted PubChem hazard annotations

detail = []  # chemical,target,aop_role,doid,disease,mondo,in_oard,aop,assay,expr,spoke,rare,protein,hazard,score
for r in chem:
    ab = r["abbrev"]
    tset = {}
    for t, role in AOP.get(ab, {}).items():
        tset[t] = role
    if active.get(ab, 0) > 0:
        for t in ER_CLASS:
            tset.setdefault(t, "assay/lit")
    for t, role in tset.items():
        for doid, dis in g2d.get(t, []):
            f_aop = 1 if t in AOP.get(ab, {}) else 0
            f_assay = 1 if active.get(ab, 0) > 0 else 0
            f_expr = 1 if t in gxa else 0
            f_spoke = 1
            f_rare = 1 if t in rdkg else 0
            f_prot = 1 if t in prokn else 0
            f_haz = 1 if ab in HAZ else 0
            mondo = bridge.get(doid, "")
            score = f_aop + f_assay + f_expr + f_spoke + f_rare + f_prot + f_haz
            detail.append(
                {
                    "chemical": ab,
                    "target": t,
                    "aop_role": role,
                    "doid": doid,
                    "disease": dis,
                    "mondo": mondo,
                    "in_oard": (1 if mondo in oard_mondo else 0),
                    "aop_structure": f_aop,
                    "assay_activity": f_assay,
                    "expression": f_expr,
                    "disease_assoc": f_spoke,
                    "rare_disease": f_rare,
                    "protein_annot": f_prot,
                    "hazard": f_haz,
                    "score": score,
                }
            )

with Path(f"{D}/../corroboration_detail.csv").open("w", newline="") as f:
    cols = [
        "chemical",
        "target",
        "aop_role",
        "disease",
        "doid",
        "mondo",
        "in_oard",
        "aop_structure",
        "assay_activity",
        "expression",
        "disease_assoc",
        "rare_disease",
        "protein_annot",
        "hazard",
        "score",
    ]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for d in detail:
        w.writerow({c: d[c] for c in cols})

# aggregate to (chemical, disease): union of source types, list targets
agg = defaultdict(
    lambda: {
        "targets": set(),
        "src": set(),
        "aop": 0,
        "maxscore": 0,
        "doid": "",
        "mondo": "",
        "in_oard": 0,
    }
)
SRC = [
    "aop_structure",
    "assay_activity",
    "expression",
    "disease_assoc",
    "rare_disease",
    "protein_annot",
    "hazard",
]
for d in detail:
    k = (d["chemical"], d["disease"])
    a = agg[k]
    a["targets"].add(d["target"])
    a["doid"] = d["doid"]
    a["mondo"] = d["mondo"]
    a["in_oard"] = max(a["in_oard"], d["in_oard"])
    for s in SRC:
        if d[s]:
            a["src"].add(s)
    a["aop"] = max(a["aop"], d["aop_structure"])
    a["maxscore"] = max(a["maxscore"], d["score"])

rows = []
for (chem_, dis), a in agg.items():
    rows.append(
        {
            "chemical": chem_,
            "disease": dis,
            "doid": a["doid"],
            "mondo": a["mondo"],
            "n_independent_sources": len(a["src"]),
            "corroboration_score": a["maxscore"],
            "aop_anchored": a["aop"],
            "mediating_targets": "|".join(sorted(a["targets"])),
            "sources": "|".join(sorted(a["src"])),
            "ehr_phenotypes_in_oard": a["in_oard"],
        }
    )
rows.sort(
    key=lambda x: (
        -x["aop_anchored"],
        -x["corroboration_score"],
        -x["n_independent_sources"],
        x["chemical"],
    )
)
with Path(f"{D}/../corroboration_ranking.csv").open("w", newline="") as f:
    cols = [
        "chemical",
        "disease",
        "doid",
        "mondo",
        "corroboration_score",
        "n_independent_sources",
        "aop_anchored",
        "mediating_targets",
        "sources",
        "ehr_phenotypes_in_oard",
    ]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"corroboration_detail.csv: {len(detail)} (chemical,target,disease) rows")
print(f"corroboration_ranking.csv: {len(rows)} (chemical,disease) links")
print("\nTop 18 best-corroborated chemical->disease links:")
print(f"{'chem':6}{'disease':34}{'score':6}{'AOP':4}  targets")
for r in rows[:18]:
    print(
        f"{r['chemical']:6}{r['disease'][:33]:34}{r['corroboration_score']:<6}{('Y' if r['aop_anchored'] else '-'):4}  {r['mediating_targets']}"
    )

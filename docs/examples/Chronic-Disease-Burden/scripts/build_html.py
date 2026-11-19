"""Thin per-study driver: fill the {{key}} template from stats.json -> <study>_report.md, build the
interactive table + KPI cards, render the HTML with build_report_from_markdown, and splice in the
interactive county map fragment (made by make_map.py) at the <!-- INTERACTIVE_MAP --> marker.

Usage: python scripts/build_html.py <map_fragment.html>
"""
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_report_html as B  # noqa: E402

ROOT = os.path.dirname(HERE)
STUDY = "Chronic-Disease-Burden"
S = json.load(open(os.path.join(ROOT, "data", "stats.json")))
S = {k: (f"{v:.2f}" if isinstance(v, float) and (k.startswith(("rho_", "mean_rho", "mantel", "r2_", "val_", "moran"))) else v)
     for k, v in S.items()}
tmpl = open(os.path.join(ROOT, "data", "report_template.md"), encoding="utf-8").read()
md_path = os.path.join(ROOT, f"{STUDY}_report.md")
open(md_path, "w", encoding="utf-8").write(B.fill_stats(tmpl, S))

r = pd.read_csv(os.path.join(ROOT, "data", "county_burden_ranked.tsv"), sep="\t", dtype={"fips": str})
r["rank"] = range(1, len(r) + 1)
rows = []
for _, x in r.iterrows():
    src = ["spoke-okn·PLACES"] + (["spoke-okn·CHR"] if pd.notna(x.chr_diabetes) else [])
    rows.append({
        "rank": int(x["rank"]), "county": x["name"], "fips": x.fips, "state": x.state, "region": x.region,
        "tier": x.tier, "lisa": x.lisa, "burden_z": round(x.burden_z, 2), "n_top": int(x.n_top_quintile),
        **{k: x[k] for k in ["diabetes", "obesity", "hypertension", "high_chol", "chd", "stroke", "copd", "asthma", "depression"]},
        "pop": int(x.pop_places), "n_src": len(src), "sources": src,
    })
cols = [("rank", "rank"), ("county", "county"), ("state", "state"), ("tier", "tier"), ("burden_z", "composite z"),
        ("n_top", "top-quintile (of 9)"), ("diabetes", "diabetes %"), ("obesity", "obesity %"),
        ("hypertension", "hypertension %"), ("high_chol", "high chol. %"), ("chd", "CHD %"), ("stroke", "stroke %"),
        ("copd", "COPD %"), ("asthma", "asthma %"), ("depression", "depression %"), ("lisa", "LISA"),
        ("pop", "pop. in places"), ("n_src", "sources (n)")]
table = (
    '<p class="tip">Tip: click a header to sort; type to search; use the drop-downs to filter by tier, region, '
    "state or LISA class; 25 rows per page. <b>sources (n)</b>: spoke-okn·PLACES supplies the nine prevalences; "
    "spoke-okn·CHR (County Health Rankings 2023) supplies the validation values and covariates.</p>"
    + B.candidate_table(rows, cols, search_keys=["county", "state", "fips"],
                        numeric_keys=["rank", "burden_z", "n_top", "diabetes", "obesity", "hypertension", "high_chol",
                                      "chd", "stroke", "copd", "asthma", "depression", "pop"],
                        page_size=25, default_sort="rank",
                        extra_filters=[("tier", "tier"), ("region", "region"), ("state", "state"), ("lisa", "LISA class")],
                        sources_col=("n_src", "sources"))
)
kpis = B.kpis_from_stats(S, [("n_counties_places", "counties analysed", ","), ("n_conditions", "chronic conditions"),
                             ("tier_A", "Tier A counties (≥7/9 top quintile)"), ("n_HH", "hot-spot counties (LISA High–High)"),
                             ("moran_burden", "Moran's I, composite"), ("val_diab_r", "PLACES vs CHR diabetes r")])
out = os.path.join(ROOT, f"{STUDY}_report.html")
B.build_report_from_markdown(md_path, out, kpis=kpis, table=table, stats=S,
                             footer="Rendered from Chronic-Disease-Burden_report.md · OKN / mcp-okn · model claude-opus-5-5")
frag = open(sys.argv[1], encoding="utf-8").read()
h = open(out, encoding="utf-8").read()
assert "<!-- INTERACTIVE_MAP -->" in h, "map marker not passed through"
h = h.replace("<!-- INTERACTIVE_MAP -->", frag)
open(out, "w", encoding="utf-8").write(h)
res = B.check_report_parity(md_path, out)
print("parity after map splice:", res["ok"])

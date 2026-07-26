import sys, json, ast, pandas as pd
sys.path.insert(0,'scripts')
from build_report_html import build_report_from_markdown, candidate_table, kpis_from_stats

stats=json.load(open("data/stats.json"))
res=pd.read_csv("data/ranked_results.csv")
res["sources"]=res["sources"].apply(ast.literal_eval)
res["beta_restricted"]=res["beta_restricted"].fillna("—")
rows=res.to_dict("records")

cols=[("series","outcome"),("domain","domain"),("level","unit"),("n","n"),
      ("beta","β (full sample)"),("ci","95% CI"),("classification","classification"),
      ("beta_restricted","β (restricted)"),("classification_restricted","classification (restricted)"),
      ("rate_elasticity","rate elasticity β−1"),("R2_rate","R² (rate)"),
      ("tier","tier"),("tier_reason","why this tier")]

table=candidate_table(
    rows, cols,
    search_keys=["series","domain","level","classification","tier","tier_reason"],
    numeric_keys=["n","beta","rate_elasticity","R2_rate"],
    page_size=25, default_sort="tier",
    extra_filters=[("tier","tier"),("domain","domain"),("level","unit"),("classification","classification")],
    sources_col=("n_sources","sources"),
)

kpis=kpis_from_stats(stats,[
 ("n_series","outcomes fitted"),
 ("n_places","census places"),
 ("n_kgs","OKN graphs"),
 ("beta_ypll","β premature death"),
 ("beta_mvd","β road deaths"),
 ("n_tierC","Tier C (definition-dependent)"),
])

build_report_from_markdown("Urban-Scaling_report.md","Urban-Scaling_report.html",
    kpis=kpis, table=table, stats=stats)

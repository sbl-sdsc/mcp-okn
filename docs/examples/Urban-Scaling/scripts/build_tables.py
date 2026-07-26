import pandas as pd, numpy as np, json
exp=pd.read_csv("data/scaling_exponents.csv")
rob=pd.read_csv("data/scaling_exponents_robustness.csv")
r_place=rob[rob.subset=="pop>=50k"].set_index("series")
r_cty  =rob[rob.subset=="metro (RUCC 1-3)"].set_index("series")

def tier(r):
    alt = r_place if r.level=="place" else r_cty
    if r.series not in alt.index: return "C","no restricted-sample comparison available"
    a=alt.loc[r.series]
    c1,c2=r.classification,a.classification
    if c1==c2 and "linear (n.s.)" not in c1:
        return "A",f"same direction and significant in both samples (β={r.beta:.3f} → {a.beta:.3f})"
    if {"sublinear","superlinear"}=={c1,c2}:
        return "C",f"direction REVERSES with city definition (β={r.beta:.3f} → {a.beta:.3f})"
    return "B",f"direction stable but significance changes (β={r.beta:.3f} → {a.beta:.3f})"

rows=[]
for _,r in exp.iterrows():
    t,why=tier(r)
    alt = r_place if r.level=="place" else r_cty
    b2 = float(alt.loc[r.series,"beta"]) if r.series in alt.index else None
    c2 = alt.loc[r.series,"classification"] if r.series in alt.index else "n/a"
    srcs = ["spoke-okn"] + (["ruralkg"] if r.level=="county" else []) + (["scales"] if "criminal" in r.series else [])
    rows.append(dict(series=r.series, domain=r.domain, level=r.level, n=int(r.n),
        beta=round(r.beta,4), ci=f"{r.ci_lo:.3f} – {r.ci_hi:.3f}",
        rate_elasticity=round(r.rate_elasticity,4), R2_rate=round(r.R2_rate,4),
        classification=r.classification,
        beta_restricted=(round(b2,4) if b2 is not None else None),
        classification_restricted=c2, tier=t, tier_reason=why,
        sources=srcs, n_sources=len(srcs)))
res=pd.DataFrame(rows).sort_values(["tier","beta"])
res.to_csv("data/ranked_results.csv",index=False)
print(res[["series","level","n","beta","ci","beta_restricted","tier"]].to_string(index=False))
print("\ntier distribution:"); print(res.tier.value_counts().sort_index().to_string())

stats=dict(
  n_places=26343, n_diseases=9, pop_min=50, pop_max=8175111,
  n_county_nodes=3196, n_mortality_measures=8, n_crime_cases=121785,
  n_crime_counties=2380, n_crime_joined=2377, n_kgs=3,
  n_series=len(res), n_tierA=int((res.tier=="A").sum()), n_tierB=int((res.tier=="B").sum()),
  n_tierC=int((res.tier=="C").sum()),
  beta_mvd=round(float(exp.loc[exp.series=="motor vehicle crash deaths","beta"].iloc[0]),3),
  beta_crime=round(float(exp.loc[exp.series=="federal criminal case filings","beta"].iloc[0]),3),
  beta_crime_metro=round(float(r_cty.loc["federal criminal case filings","beta"]),3),
  beta_ypll=round(float(exp.loc[exp.series=="premature death (YPLL)","beta"].iloc[0]),3),
  beta_diab_all=round(float(exp.loc[exp.series=="diabetes mellitus","beta"].iloc[0]),3),
  beta_diab_50k=round(float(r_place.loc["diabetes mellitus","beta"]),3),
  beta_stroke_50k=round(float(r_place.loc["cerebrovascular disease (stroke)","beta"]),3),
  n_places_50k=709, n_metro_counties_max=1159,
  max_R2_rate=round(float(exp.R2_rate.max()),3), min_R2_rate=round(float(exp.R2_rate.min()),4),
)
json.dump(stats,open("data/stats.json","w"),indent=2)
print("\nstats.json:", json.dumps(stats,indent=1)[:400])

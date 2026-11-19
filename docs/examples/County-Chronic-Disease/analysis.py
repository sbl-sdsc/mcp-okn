"""analysis.py - county chronic-disease burden from the OKN federation (spoke-okn + ruralkg).

Every function takes the query results the notebook loads into ``data["qNN"]`` (pandas DataFrames)
and returns tables / figures, so the notebook stays readable and the logic stays testable.

Query map (see the notebook's SPARQL cells):
  q01  inventory of spoke-okn disease-prevalence statements (source x geography level)
  q02  the nine CDC PLACES measures stored as place-level (City) prevalence
  q03  coverage/range of the native county measures used here
  q04-q07  native county measures (CHR 2023, AHRQ SDOH 2018-2020) + RUCC (ruralkg), by state-FIPS band
  q08-q11  CDC PLACES place-level prevalence rolled up to counties (population-weighted), by band
"""
from __future__ import annotations

import json
import math
import os
import urllib.request

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from okn_figstyle import THEME, apply_style, finalize, legend_outside, panel_title

# ----------------------------------------------------------------------------------------------
# Measure catalogue
# ----------------------------------------------------------------------------------------------
# key: (label, unit, tier, source, data year as recorded in the KG, spoke-okn node / DOID term)
CONDITIONS = {
    "diabetes": ("Diabetes", "%", "A", "County Health Rankings (CHR)", "2023 release", "sdoh/CHR_diabetes_prevalence"),
    "obesity": ("Obesity", "%", "A", "County Health Rankings (CHR)", "2023 release", "sdoh/414916001 (SNOMED Obesity)"),
    "asthma": ("Asthma", "%", "A", "AHRQ SDOH (CDC PLACES county)", "2019", "sdoh/CDCP_ASTHMA_ADULT_A"),
    "copd": ("COPD", "%", "A", "AHRQ SDOH (CDC PLACES county)", "2019", "sdoh/CDCP_PULMONARY_ADULT_A"),
    "arthritis": ("Arthritis", "%", "A", "AHRQ SDOH (CDC PLACES county)", "2019", "sdoh/CDCP_ARTHRITIS_ADULT_A"),
    "ckd": ("Chronic kidney disease", "%", "A", "AHRQ SDOH (CDC PLACES county)", "2019", "sdoh/CDCP_KIDNEY_DISEASE_ADULT_A"),
    "high_chol": ("High cholesterol", "%", "A", "AHRQ SDOH (CDC PLACES county)", "2019", "sdoh/CDCP_CHOLES_ADULT_A"),
    "hypertension": ("Hypertension", "%", "B", "CDC PLACES place-level, rolled up to county", "not recorded", "DOID:10763"),
    "chd": ("Coronary heart disease", "%", "B", "CDC PLACES place-level, rolled up to county", "not recorded", "DOID:3393"),
    "stroke": ("Stroke", "%", "B", "CDC PLACES place-level, rolled up to county", "not recorded", "DOID:6713"),
    "depression": ("Depression", "%", "B", "CDC PLACES place-level, rolled up to county", "not recorded", "DOID:1596"),
}
OUTCOMES = {
    "heart_mort": ("Heart-disease mortality (35+)", "per 100k", "AHRQ SDOH (CDC Atlas)", "2019"),
    "stroke_mort": ("Stroke mortality (35+)", "per 100k", "AHRQ SDOH (CDC Atlas)", "2019"),
    "heart_hosp": ("Heart-disease hospitalization (65+)", "per 1k Medicare", "AHRQ SDOH (CDC Atlas)", "2018"),
    "stroke_hosp": ("Stroke hospitalization (65+)", "per 1k Medicare", "AHRQ SDOH (CDC Atlas)", "2018"),
    "mental_distress": ("Frequent mental distress", "%", "County Health Rankings (CHR)", "2023 release"),
    "physical_distress": ("Frequent physical distress", "%", "County Health Rankings (CHR)", "2023 release"),
}
COVARIATES = {
    "age65": ("% age 65+", "ACS via AHRQ SDOH", "2020"),
    "black": ("% Black non-Hispanic", "ACS via AHRQ SDOH", "2020"),
    "hispanic": ("% Hispanic", "ACS via AHRQ SDOH", "2020"),
    "poverty": ("% in poverty", "SAIPE via AHRQ SDOH", "2020"),
    "bachelor": ("% bachelor's degree", "ACS via AHRQ SDOH", "2020"),
    "log_income": ("log median household income", "ACS via AHRQ SDOH", "2020"),
    "rural": ("% rural population", "County Health Rankings (CHR)", "2023 release"),
    "smoking": ("% adult smoking", "County Health Rankings (CHR)", "2023 release"),
    "inactivity": ("% physically inactive", "AHRQ SDOH (CDC PLACES county)", "2019"),
    "food_env": ("Food environment index (0-10)", "County Health Rankings (CHR)", "2023 release"),
}
COND_ALL = list(CONDITIONS)
COND_NATIVE = [k for k, v in CONDITIONS.items() if v[2] == "A"]
COND_PLACE = [k for k, v in CONDITIONS.items() if v[2] == "B"]
RISK_FACTORS = ["obesity", "high_chol", "hypertension"]
CONFOUND_DEMO = ["age65", "black", "hispanic", "poverty", "bachelor", "log_income", "rural"]
CONFOUND_BEHAV = ["smoking", "inactivity"]
MIN_PLACE_COVERAGE = 0.10  # place-derived (tier B) values used only if places hold >=10% of county pop
LABEL = {**{k: v[0] for k, v in CONDITIONS.items()}, **{k: v[0] for k, v in OUTCOMES.items()},
         **{k: v[0] for k, v in COVARIATES.items()},
         "cbs11": "Composite burden score (11 conditions)", "cbs7": "Composite burden score (7 native)", "cbs_avail": "Composite burden (available conditions)",
         "n_top_quintile": "Conditions in national top quintile (of 11)"}
GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"


def _fips(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


# ----------------------------------------------------------------------------------------------
# 1. Assemble + validate
# ----------------------------------------------------------------------------------------------
def load_county_table(data: dict) -> pd.DataFrame:
    """One row per county: native measures (q04-q07) left-joined to the place roll-ups (q08-q11)."""
    nat = pd.concat([data[f"q{i:02d}"] for i in range(4, 8)], ignore_index=True)
    pl = pd.concat([data[f"q{i:02d}"] for i in range(8, 12)], ignore_index=True)
    nat["fips"], pl["fips"] = _fips(nat["fips"]), _fips(pl["fips"])
    df = nat.merge(pl, on="fips", how="left", validate="one_to_one")
    df.attrs = {}
    df["state_fips"] = df["fips"].str[:2]
    df["rucc"] = pd.to_numeric(df["rucc"], errors="coerce")
    df["metro"] = np.where(df["rucc"] <= 3, "Metro (RUCC 1-3)", "Nonmetro (RUCC 4-9)")
    df["log_income"] = np.log(df["income"])
    df["place_coverage"] = (df["pop_places"] / df["pop"]).clip(upper=1.0)
    # tier-B (place-derived) columns are kept only where places cover enough of the county
    ok = df["place_coverage"] >= MIN_PLACE_COVERAGE
    for k in COND_PLACE:
        df[k] = df[k].where(ok)
    return df


def qc_report(df: pd.DataFrame):
    """Range/missingness/duplicate checks for every analysed measure."""
    rows = []
    for k in COND_ALL + list(OUTCOMES) + list(COVARIATES):
        s = df[k]
        pct = CONDITIONS.get(k, OUTCOMES.get(k, ("", "")))[1] == "%" if k in CONDITIONS or k in OUTCOMES else k in (
            "age65", "black", "hispanic", "poverty", "bachelor", "rural", "smoking", "inactivity")
        rows.append({
            "measure": k, "label": LABEL[k], "n_counties": int(s.notna().sum()),
            "missing": int(s.isna().sum()), "min": s.min(), "median": s.median(), "max": s.max(),
            "out_of_range_0_100": int(((s < 0) | (s > 100)).sum()) if pct else np.nan,
        })
    qc = pd.DataFrame(rows)
    summary = {"counties": len(df), "states_incl_DC": int(df["state_fips"].nunique()),
               "duplicate_fips": int(df["fips"].duplicated().sum())}
    return qc, summary


def national_summary(df: pd.DataFrame) -> pd.DataFrame:
    """County distribution + population-weighted mean for each condition."""
    out = []
    for k, (lab, unit, tier, src, yr, node) in CONDITIONS.items():
        s = df[[k, "pop"]].dropna()
        out.append({"condition": lab, "key": k, "tier": tier, "source": src, "year": yr, "kg_node": node,
                    "n_counties": len(s), "pop_weighted_mean_%": round(np.average(s[k], weights=s["pop"]), 2),
                    "county_median_%": s[k].median(), "p10": s[k].quantile(.1), "p90": s[k].quantile(.9),
                    "min": s[k].min(), "max": s[k].max()})
    return pd.DataFrame(out)


def validate_place_vs_native(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-check: place roll-ups vs. native county estimates for the 5 measures available both ways."""
    pairs = [("diabetes", "diabetes_pl"), ("obesity", "obesity_pl"), ("asthma", "asthma_pl"),
             ("copd", "copd_pl"), ("high_chol", "high_chol_pl")]
    rows = []
    for a, b in pairs:
        s = df[[a, b, "place_coverage"]].dropna()
        for lab, sub in [("all counties", s), ("coverage < 25%", s[s.place_coverage < .25]),
                         ("coverage >= 50%", s[s.place_coverage >= .5])]:
            d = sub[b] - sub[a]
            rows.append({"measure": LABEL[a], "subset": lab, "n": len(sub),
                         "pearson_r": round(sub[a].corr(sub[b]), 3),
                         "spearman_rho": round(sub[a].corr(sub[b], method="spearman"), 3),
                         "mean_diff_place_minus_native": round(d.mean(), 2),
                         "limits_of_agreement_95": f"{d.mean() - 1.96 * d.std():.1f} to {d.mean() + 1.96 * d.std():.1f}"})
    return pd.DataFrame(rows)


def plot_validation(df: pd.DataFrame, path: str, number: int = 1):
    apply_style()
    pairs = [("diabetes", "diabetes_pl"), ("obesity", "obesity_pl"), ("asthma", "asthma_pl"),
             ("copd", "copd_pl"), ("high_chol", "high_chol_pl")]
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.4))
    fig.subplots_adjust(left=.06, right=.88, top=.93, bottom=.08, wspace=.32, hspace=.38)
    for ax, (a, b), letter in zip(axes.flat, pairs, "ABCDE"):
        s = df[[a, b, "place_coverage"]].dropna()
        sc = ax.scatter(s[a], s[b], c=s["place_coverage"], cmap="viridis", s=5, alpha=.6, vmin=0, vmax=1)
        lo, hi = np.nanmin(s[[a, b]].values), np.nanmax(s[[a, b]].values)
        ax.plot([lo, hi], [lo, hi], color="#555", lw=1, ls="--")
        panel_title(ax, letter, LABEL[a], fontsize=11)
        ax.text(.03, .97, f"r = {s[a].corr(s[b]):.2f}\nn = {len(s):,}", transform=ax.transAxes, va="top", fontsize=8.5)
        ax.set_xlabel("native county estimate (%)")
        ax.set_ylabel("place roll-up (%)")
    ax = axes.flat[5]
    ax.hist(df["place_coverage"].dropna(), bins=40, color=THEME[0])
    ax.axvline(MIN_PLACE_COVERAGE, color=THEME[5], ls="--", lw=1.2)
    panel_title(ax, "F", "Place coverage", fontsize=11)
    ax.set_xlabel("place population / county population")
    ax.set_ylabel("counties")
    cax = fig.add_axes([.905, .56, .015, .33])
    cb = fig.colorbar(sc, cax=cax)
    cb.set_label("place coverage (A-E)")
    return finalize(fig, number, path, tight=False)


# ----------------------------------------------------------------------------------------------
# 2. Composite burden score
# ----------------------------------------------------------------------------------------------
def zscores(df: pd.DataFrame, cols) -> pd.DataFrame:
    return (df[cols] - df[cols].mean()) / df[cols].std(ddof=0)


SCORE_INFO: dict = {}  # PCA loadings / variance explained from the last build_scores() call


def build_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add composite scores and multimorbidity flags.

    cbs11  mean z-score over the 11 conditions (equal weights; county is the unit, unweighted);
           requires all 11 present.
    cbs7   same over the 7 native (tier-A) conditions; covers nearly every county (sensitivity).
    cbs_rank  mean national percentile rank over the 11 (robust to skew; sensitivity).
    cbs_pc1   first principal component of the 11 z-scores, sign-aligned to cbs11 (sensitivity).
    cbs_avail  mean z over the conditions available (>= 6 of 11) - keeps New Jersey / Florida on the map.
    cbs_disease_only  cbs11 without the risk-factor measures obesity / high cholesterol / hypertension.
    n_top_quintile  number of the 11 conditions on which the county is in the national top 20%.
    """
    df = df.copy()
    z = zscores(df, COND_ALL)
    df["n_conditions"] = z.notna().sum(axis=1)
    df["cbs11"] = z.mean(axis=1).where(df["n_conditions"] == len(COND_ALL))
    # coverage-maximising variant: mean z over whatever is available, if >= 6 of 11 (flag n_conditions)
    df["cbs_avail"] = z.mean(axis=1).where(df["n_conditions"] >= 6)
    zn = zscores(df, COND_NATIVE)
    df["cbs7"] = zn.mean(axis=1).where(zn.notna().all(axis=1))
    pr = df[COND_ALL].rank(pct=True)
    df["cbs_rank"] = (100 * pr.mean(axis=1)).where(df["n_conditions"] == len(COND_ALL))
    comp = z.dropna()
    u, s, vt = np.linalg.svd(comp.values - comp.values.mean(0), full_matrices=False)
    pc1 = pd.Series(u[:, 0] * s[0], index=comp.index)
    if np.corrcoef(pc1, df.loc[comp.index, "cbs11"])[0, 1] < 0:
        pc1, vt[0] = -pc1, -vt[0]
    df["cbs_pc1"] = pc1
    SCORE_INFO["pc1_loadings"] = pd.Series(vt[0], index=COND_ALL).round(3)
    SCORE_INFO["pc1_var_explained"] = float(s[0] ** 2 / (s ** 2).sum())
    keep = [c for c in COND_ALL if c not in RISK_FACTORS]
    df["cbs_disease_only"] = z[keep].mean(axis=1).where(df["n_conditions"] == len(COND_ALL))
    q80 = df[COND_ALL].quantile(.8)
    top = df[COND_ALL].ge(q80) & df[COND_ALL].notna()
    df["n_top_quintile"] = top.sum(axis=1).where(df["n_conditions"] == len(COND_ALL))
    df["cbs11_rank"] = df["cbs11"].rank(ascending=False, method="min")
    df["cbs11_pctile"] = 100 * df["cbs11"].rank(pct=True)
    return df


def score_agreement(df: pd.DataFrame, top_n: int = 100) -> pd.DataFrame:
    """Do the sensitivity composites rank counties like cbs11?"""
    base = df.dropna(subset=["cbs11"])
    top_base = set(base.nlargest(top_n, "cbs11")["fips"])
    rows = []
    for c in ["cbs7", "cbs_avail", "cbs_rank", "cbs_pc1", "cbs_disease_only"]:
        s = base.dropna(subset=[c])
        rows.append({"alternative": c, "spearman_vs_cbs11": round(s["cbs11"].corr(s[c], method="spearman"), 3),
                     f"top{top_n}_overlap": len(top_base & set(s.nlargest(top_n, c)["fips"]))})
    return pd.DataFrame(rows)


def top_counties(df: pd.DataFrame, col: str, n: int = 20, min_pop: float = 0) -> pd.DataFrame:
    cols = ["fips", "county", "state", "pop", "rucc", col]
    extra = [c for c in ["cbs11", "n_top_quintile"] if c != col]
    out = df[df["pop"] >= min_pop].dropna(subset=[col]).nlargest(n, col)[cols + extra]
    out.insert(0, "rank", range(1, len(out) + 1))
    return out.reset_index(drop=True)


def data_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """Per measure: counties without a value, and states with no value for any county (systematic gaps)."""
    rows = []
    for k in COND_ALL + list(OUTCOMES):
        miss = df[df[k].isna()]
        tot = df.groupby("state").size()
        gone = miss.groupby("state").size().reindex(tot.index, fill_value=0)
        full = sorted(gone[gone == tot].index)
        part = gone[(gone > 0) & (gone < tot)].sort_values(ascending=False)
        rows.append({"measure": LABEL[k], "counties_missing": len(miss),
                     "states_entirely_missing": ", ".join(full) or "-",
                     "states_partly_missing (n)": ", ".join(f"{st} ({n})" for st, n in part.head(6).items()) or "-"})
    return pd.DataFrame(rows)


def top_by_condition(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    rows = []
    for k in COND_ALL:
        t = df.dropna(subset=[k]).nlargest(n, k)
        for r, (_, x) in enumerate(t.iterrows(), 1):
            rows.append({"condition": LABEL[k], "rank": r, "fips": x["fips"], "county": x["county"],
                         "state": x["state"], "prevalence_%": x[k], "pop": x["pop"]})
    return pd.DataFrame(rows)


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.dropna(subset=["cbs11"]).groupby("state")
    out = pd.DataFrame({
        "counties_scored": g.size(),
        "median_cbs11": g["cbs11"].median().round(3),
        "counties_in_national_top_decile": g["cbs11_pctile"].apply(lambda s: int((s >= 90).sum())),
        "counties_high_multimorbidity_ge8": g["n_top_quintile"].apply(lambda s: int((s >= 8).sum())),
    }).sort_values("median_cbs11", ascending=False)
    return out.reset_index()


def plot_top_counties(df: pd.DataFrame, path: str, number: int):
    apply_style()
    a = top_counties(df, "cbs11", 20)
    b = top_counties(df, "cbs11", 20, min_pop=50_000)
    fig, axes = plt.subplots(1, 2, figsize=(13, 7.2))
    for ax, t, letter, ttl in [(axes[0], a, "A", "All counties"), (axes[1], b, "B", "Counties with population >= 50,000")]:
        lab = [f"{c.replace(' County', '').replace(' Parish', ' Par.')}, {s}" for c, s in zip(t.county, t.state)][::-1]
        cols = [THEME[5] if m < 4 else THEME[0] for m in t.rucc][::-1]
        ax.barh(lab, t.cbs11[::-1], color=cols)
        for y, (v, k) in enumerate(zip(t.cbs11[::-1], t.n_top_quintile[::-1])):
            ax.text(v + .02, y, f"{int(k)}/11", va="center", fontsize=8)
        panel_title(ax, letter, ttl, fontsize=11)
        ax.set_xlabel("composite burden score (mean z over 11 conditions)")
        ax.set_xlim(0, max(a.cbs11.max(), b.cbs11.max()) * 1.15)
    from matplotlib.patches import Patch
    legend_outside(axes[1], [Patch(color=THEME[0]), Patch(color=THEME[5])],
                   ["nonmetro (RUCC 4-9)", "metro (RUCC 1-3)"], where="below", ncol=2)
    return finalize(fig, number, path)


# ----------------------------------------------------------------------------------------------
# 3. Correlations, confounders
# ----------------------------------------------------------------------------------------------
CORR_VARS = COND_ALL + ["mental_distress", "physical_distress", "heart_mort", "stroke_mort", "heart_hosp", "stroke_hosp"]


def _residualize(df: pd.DataFrame, cols, covars, state_fe: bool) -> pd.DataFrame:
    """Rank-transform every variable, regress on (rank) covariates [+ state dummies], return residuals.
    Correlating the residuals gives partial Spearman correlations."""
    need = cols + covars + (["state_fips"] if state_fe else [])
    d = df[need].dropna()
    R = d[cols + covars].rank(pct=True)
    X = [np.ones(len(d))] + [R[c].values for c in covars]
    X = np.column_stack(X)
    if state_fe:
        X = np.column_stack([X, pd.get_dummies(d["state_fips"], drop_first=True).values.astype(float)])
    beta, *_ = np.linalg.lstsq(X, R[cols].values, rcond=None)
    res = R[cols].values - X @ beta
    return pd.DataFrame(res, index=d.index, columns=cols)


def correlation_sets(df: pd.DataFrame, cols=None) -> dict:
    cols = cols or CORR_VARS
    base = df[cols + CONFOUND_DEMO + CONFOUND_BEHAV + ["state_fips"]].dropna()
    out = {"raw": base[cols].corr(method="spearman")}
    out["adj_demographic"] = _residualize(base, cols, CONFOUND_DEMO, False).corr()
    out["adj_demo_state"] = _residualize(base, cols, CONFOUND_DEMO, True).corr()
    out["adj_demo_state_behav"] = _residualize(base, cols, CONFOUND_DEMO + CONFOUND_BEHAV, True).corr()
    out["n"] = len(base)
    return out


def corr_pairs(cs: dict, cols=None) -> pd.DataFrame:
    cols = cols or COND_ALL
    rows = []
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            rows.append({"var_a": LABEL[a], "var_b": LABEL[b], "rho_raw": cs["raw"].loc[a, b],
                         "rho_adj_demographic": cs["adj_demographic"].loc[a, b],
                         "rho_adj_demo_state": cs["adj_demo_state"].loc[a, b],
                         "rho_adj_full": cs["adj_demo_state_behav"].loc[a, b]})
    p = pd.DataFrame(rows)
    p["attenuation_raw_to_full"] = p["rho_raw"] - p["rho_adj_full"]
    return p.round(3).sort_values("rho_raw", ascending=False).reset_index(drop=True)


def clustered_heatmap(corr: pd.DataFrame, path: str, number: int, title: str, order=None):
    """Average-linkage clustering on 1 - rho; returns the leaf order so a second heatmap can reuse it."""
    import seaborn as sns
    from scipy.cluster.hierarchy import leaves_list, linkage
    from scipy.spatial.distance import squareform
    apply_style()
    if order is None:
        dist = squareform(1 - corr.values, checks=False)
        Z = linkage(dist, "average")
        order = [corr.index[i] for i in leaves_list(Z)]
        g = sns.clustermap(corr.rename(index=LABEL, columns=LABEL), row_linkage=Z, col_linkage=Z,
                           cmap="RdBu_r", vmin=-1, vmax=1, center=0, annot=True, fmt=".2f",
                           annot_kws={"size": 7}, figsize=(12.5, 11.5), dendrogram_ratio=.12,
                           cbar_pos=(1.0, .35, .02, .3), linewidths=.3,
                           cbar_kws={"label": "Spearman rho"})
        g.ax_heatmap.tick_params(labelsize=8.5)
        g.fig.suptitle(title, fontsize=12, fontweight="bold", y=1.01)
        g.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(g.fig)
        return order
    fig, ax = plt.subplots(figsize=(12, 10.5))
    m = corr.loc[order, order].rename(index=LABEL, columns=LABEL)
    sns.heatmap(m, cmap="RdBu_r", vmin=-1, vmax=1, center=0, annot=True, fmt=".2f", annot_kws={"size": 7},
                linewidths=.3, ax=ax, cbar_kws={"label": "partial Spearman rho", "shrink": .6})
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
    ax.tick_params(labelsize=8.5)
    finalize(fig, number, path)
    return order


def covariate_associations(df: pd.DataFrame) -> pd.DataFrame:
    cov = list(COVARIATES) + ["rucc"]
    m = pd.DataFrame(index=COND_ALL + ["cbs11"], columns=cov, dtype=float)
    for k in m.index:
        for c in cov:
            s = df[[k, c]].dropna()
            m.loc[k, c] = s[k].corr(s[c], method="spearman")
    return m


def plot_covariate_heatmap(m: pd.DataFrame, path: str, number: int):
    import seaborn as sns
    apply_style()
    fig, ax = plt.subplots(figsize=(11.5, 6.8))
    lab = {**LABEL, "rucc": "RUCC (1 metro - 9 remote)"}
    sns.heatmap(m.rename(index=lab, columns=lab), cmap="RdBu_r", vmin=-1, vmax=1, center=0, annot=True,
                fmt=".2f", annot_kws={"size": 7.5}, linewidths=.3, ax=ax, cbar_kws={"label": "Spearman rho", "shrink": .7})
    ax.set_title("Condition prevalence vs. county demographic, socioeconomic, geographic and behavioural covariates",
                 fontsize=11.5, fontweight="bold", loc="left")
    ax.tick_params(labelsize=8.5)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    return finalize(fig, number, path)


def composite_regression(df: pd.DataFrame):
    """cbs11 ~ standardized covariates + state fixed effects; SEs clustered by state."""
    import statsmodels.formula.api as smf
    cov = CONFOUND_DEMO + CONFOUND_BEHAV
    d = df[["cbs11", "state_fips"] + cov].dropna().copy()
    for c in cov:
        d[c] = (d[c] - d[c].mean()) / d[c].std()
    out = {}
    for name, rhs in [("covariates", " + ".join(cov)), ("covariates + state FE", " + ".join(cov) + " + C(state_fips)"),
                      ("state FE only", "C(state_fips)")]:
        mod = smf.ols(f"cbs11 ~ {rhs}", data=d).fit(cov_type="cluster", cov_kwds={"groups": d["state_fips"]})
        out[name] = mod
    tab = pd.DataFrame({
        "covariate": [LABEL[c] for c in cov],
        "beta_per_SD": [out["covariates + state FE"].params[c] for c in cov],
        "ci_low": [out["covariates + state FE"].conf_int().loc[c, 0] for c in cov],
        "ci_high": [out["covariates + state FE"].conf_int().loc[c, 1] for c in cov],
        "p_value": [out["covariates + state FE"].pvalues[c] for c in cov],
    }).round(4)
    r2 = pd.DataFrame({"model": list(out), "r2": [round(m.rsquared, 3) for m in out.values()],
                       "n": [int(m.nobs) for m in out.values()]})
    return tab, r2


def plot_confounders(df: pd.DataFrame, tab: pd.DataFrame, path: str, number: int):
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    t = tab.iloc[::-1]
    ax.errorbar(t.beta_per_SD, range(len(t)), xerr=[t.beta_per_SD - t.ci_low, t.ci_high - t.beta_per_SD],
                fmt="o", color=THEME[0], ecolor="#888", capsize=3)
    ax.axvline(0, color="#555", lw=.8)
    ax.set_yticks(range(len(t)), t.covariate)
    ax.set_xlabel("change in composite score per 1 SD of covariate (95% CI)")
    panel_title(ax, "A", "Adjusted associations (state fixed effects)", fontsize=11)
    ax = axes[1]
    d = df.dropna(subset=["cbs11", "rucc"])
    groups = [d.loc[d.rucc == r, "cbs11"].values for r in range(1, 10)]
    bp = ax.boxplot(groups, positions=range(1, 10), widths=.6, patch_artist=True, showfliers=False,
                    medianprops={"color": "black", "lw": 1.5})
    for i, p in enumerate(bp["boxes"]):
        p.set_facecolor(THEME[5] if i < 3 else THEME[0])
        p.set_alpha(.75)
    ax.axhline(0, color="#555", lw=.8, ls="--")
    ax.set_xlabel("Rural-Urban Continuum Code (ruralkg; 1 = large metro, 9 = remote rural)")
    ax.set_ylabel("composite burden score")
    ns = [len(g) for g in groups]
    ax.set_xticks(range(1, 10), [f"{r}\n(n={n})" for r, n in zip(range(1, 10), ns)])
    panel_title(ax, "B", "Composite burden by urbanicity", fontsize=11)
    return finalize(fig, number, path)


# ----------------------------------------------------------------------------------------------
# 4. Geography: boundaries, spatial autocorrelation, maps
# ----------------------------------------------------------------------------------------------
def load_geojson(path: str = "geo/us_counties_fips.geojson") -> dict:
    """US county polygons keyed by 5-digit FIPS (plotly/datasets, Census 2010 cartographic boundaries)."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(GEOJSON_URL, path)
    with open(path) as f:
        return json.load(f)


def counties_gdf(geo: dict):
    import geopandas as gpd
    g = gpd.GeoDataFrame.from_features(geo["features"], crs="EPSG:4326")
    g["fips"] = [f["id"] for f in geo["features"]]
    return g


def morans_i(gdf, df: pd.DataFrame, col: str, perms: int = 999, seed: int = 7):
    """Global Moran's I + local Moran (LISA) with queen contiguity, row-standardized weights."""
    g = gdf.merge(df[["fips", col]], on="fips").dropna(subset=[col]).reset_index(drop=True)
    src, dst = g.sindex.query(g.geometry, predicate="intersects")
    m = src != dst
    src, dst = src[m], dst[m]
    nb = pd.DataFrame({"i": src, "j": dst}).drop_duplicates()
    x = g[col].values
    zx = (x - x.mean()) / x.std()
    deg = nb.groupby("i").size().reindex(range(len(g)), fill_value=0).values
    lag = np.zeros(len(g))
    np.add.at(lag, nb["i"].values, zx[nb["j"].values])
    has = deg > 0
    lag[has] /= deg[has]
    I = float((zx[has] * lag[has]).sum() / (zx[has] ** 2).sum())
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(perms):
        p = rng.permutation(zx)
        l2 = np.zeros(len(g))
        np.add.at(l2, nb["i"].values, p[nb["j"].values])
        l2[has] /= deg[has]
        sims.append((p[has] * l2[has]).sum() / (p[has] ** 2).sum())
    p_global = (1 + np.sum(np.array(sims) >= I)) / (perms + 1)
    # local Moran, conditional permutation
    Ii = zx * lag
    nbr = nb.groupby("i")["j"].apply(np.array).reindex(range(len(g)))
    p_local = np.ones(len(g))
    for i in np.where(has)[0]:
        k = deg[i]
        others = np.delete(zx, i)
        draws = rng.choice(others, size=(199, k), replace=True).mean(axis=1) * zx[i]
        p_local[i] = (1 + np.sum(np.abs(draws) >= abs(Ii[i]))) / 200
    quad = np.select([(zx > 0) & (lag > 0), (zx < 0) & (lag < 0), (zx > 0) & (lag < 0), (zx < 0) & (lag > 0)],
                     ["High-High", "Low-Low", "High-Low", "Low-High"], "none")
    g["lisa"] = np.where((p_local < .05) & has, quad, "not significant")
    return {"I": I, "p": float(p_global), "n": int(has.sum()), "lisa": g[["fips", "lisa"]]}


def static_small_multiples(gdf, df: pd.DataFrame, path: str, number: int):
    """Contiguous-US small multiples (11 conditions + composite)."""
    apply_style()
    g = gdf.merge(df, on="fips", how="left")
    g = g[~g.fips.str[:2].isin(["02", "15", "72"])].to_crs("EPSG:5070")
    cols = COND_ALL + ["cbs11"]
    fig, axes = plt.subplots(4, 3, figsize=(14, 13.5))
    for ax, c, letter in zip(axes.flat, cols, "ABCDEFGHIJKL"):
        if c == "cbs11":
            vmax = np.nanpercentile(np.abs(g[c]), 98)
            g.plot(column=c, ax=ax, cmap="RdBu_r", vmin=-vmax, vmax=vmax, linewidth=0, legend=True,
                   missing_kwds={"color": "#dddddd"}, legend_kwds={"shrink": .55, "label": "mean z"})
        else:
            lo, hi = np.nanpercentile(g[c], [2, 98])
            g.plot(column=c, ax=ax, cmap="YlOrRd", vmin=lo, vmax=hi, linewidth=0, legend=True,
                   missing_kwds={"color": "#dddddd"}, legend_kwds={"shrink": .55, "label": "%"})
        ax.set_axis_off()
        panel_title(ax, letter, LABEL[c] if c != "cbs11" else "Composite burden (11)", fontsize=10.5)
    return finalize(fig, number, path)


def _simplify_geojson(geo: dict, tol: float = 0.005, ndig: int = 3) -> dict:
    from shapely.geometry import mapping, shape
    feats = []
    for f in geo["features"]:
        geom = shape(f["geometry"]).simplify(tol, preserve_topology=True)
        gj = json.loads(json.dumps(mapping(geom)), parse_float=lambda v: round(float(v), ndig))
        feats.append({"type": "Feature", "id": f["id"], "properties": {"NAME": f["properties"]["NAME"]}, "geometry": gj})
    return {"type": "FeatureCollection", "features": feats}


def interactive_map(df: pd.DataFrame, geo: dict, out_html: str | None = None):
    """Leaflet county choropleth on Esri World Street Map tiles, with a drop-down to switch layers.

    folium/Leaflet rather than plotly's tile maps (`Choroplethmap`): those render through MapLibre,
    which needs WebGL2 and a web worker that fails to start in a saved HTML file and in the
    notebook's iframe, leaving an empty map. Leaflet draws SVG and works offline from disk (only the
    street tiles need the network). One GeoJSON layer carries every county's colour for every
    layer (computed here), so switching layers in the drop-down only restyles it.
    """
    import html as _html

    import folium
    from branca.element import Element
    from matplotlib import colormaps
    from matplotlib.colors import Normalize, to_hex

    from okn_figstyle import BASEMAP_ATTR, BASEMAP_TILES

    layers = [("cbs11", "Composite burden score (11 conditions, mean z)", "RdBu_r", True)]
    layers += [("cbs_avail", "Composite burden, coverage-maximising (mean z over >= 6 available conditions)", "RdBu_r", True)]
    layers += [("n_top_quintile", "No. of conditions in national top quintile (0-11)", "Reds", False),
               ("cbs7", "Composite burden score (7 native measures, mean z)", "RdBu_r", True)]
    layers += [(k, f"{v[0]} prevalence (%) - {v[3]}", "YlOrRd", False) for k, v in CONDITIONS.items()]
    layers += [(k, f"{v[0]} ({v[1]}) - {v[2]} {v[3]}", "YlOrRd", False) for k, v in OUTCOMES.items()]
    no_data = "#d9d9d9"

    d = df.set_index("fips")
    meta, legends = [], []
    colours: dict[str, list[str]] = {f: [] for f in d.index}
    values: dict[str, list] = {f: [] for f in d.index}
    for k, title, cmap_name, diverging in layers:
        z = d[k].astype(float)
        if diverging:
            v = float(np.nanpercentile(np.abs(z), 98))
            lo, hi = -v, v
        else:
            lo, hi = (float(x) for x in np.nanpercentile(z, [2, 98]))
        cmap, norm = colormaps[cmap_name], Normalize(lo, hi, clip=True)
        for f, val in z.items():
            ok = np.isfinite(val)
            colours[f].append(to_hex(cmap(norm(val))) if ok else no_data)
            values[f].append(round(float(val), 2) if ok else None)
        unit = "mean z" if diverging else ("count" if k == "n_top_quintile" else title.split("(")[1].split(")")[0])
        stops = ", ".join(to_hex(cmap(i / 8)) for i in range(9))
        legends.append({"lo": f"{lo:.2f}", "hi": f"{hi:.2f}", "unit": unit, "gradient": stops})
        meta.append(title.split(" - ")[0])

    feats = []
    for feat in _simplify_geojson(geo)["features"]:
        f = feat["id"]
        if f not in d.index:
            continue
        r = d.loc[f]
        feat["properties"] = {
            "n": f"{r['county']}, {r['state']}", "p": f"{int(r['pop']) if pd.notna(r['pop']) else 0:,}",
            "u": int(r["rucc"]) if pd.notna(r["rucc"]) else -1,
            "k": int(r["cbs11_rank"]) if pd.notna(r["cbs11_rank"]) else -1,
            "a": int(r["n_conditions"]), "c": colours[f], "v": values[f],
        }
        feats.append(feat)
    scored = int(d["cbs11"].notna().sum())

    m = folium.Map(location=[38.5, -96], zoom_start=4, tiles=None, control_scale=True, prefer_canvas=False)
    folium.TileLayer(BASEMAP_TILES, attr=BASEMAP_ATTR, name="Esri World Street Map").add_to(m)
    gj = folium.GeoJson(
        {"type": "FeatureCollection", "features": feats}, name="counties",
        style_function=lambda f: {"fillColor": f["properties"]["c"][0], "color": "#666", "weight": 0.2, "fillOpacity": 0.8},
        highlight_function=lambda f: {"weight": 1.5, "color": "#222"},
    ).add_to(m)
    m.fit_bounds([[24.4, -125.0], [49.5, -66.9]])

    options = "".join(f'<option value="{i}">{_html.escape(t)}</option>' for i, t in enumerate(meta))
    panel = f"""
<div id="okn-layer-panel" style="position:absolute;top:10px;left:54px;z-index:1000;background:#fff;
     padding:6px 8px;border:1px solid #999;border-radius:4px;font:12px sans-serif;max-width:60%">
  <select id="okn-layer" style="font:12px sans-serif;max-width:100%">{options}</select>
  <div style="margin-top:6px"><span id="okn-unit"></span>
    <div id="okn-ramp" style="height:10px;width:220px;margin:3px 0;border:1px solid #999"></div>
    <div style="display:flex;justify-content:space-between;width:222px"><span id="okn-lo"></span><span id="okn-hi"></span></div>
    <div style="margin-top:3px"><span style="display:inline-block;width:10px;height:10px;background:{no_data};border:1px solid #999"></span> not available / place coverage &lt; 10%</div>
  </div>
</div>
<div style="position:absolute;bottom:52px;left:10px;z-index:1000;background:rgba(255,255,255,.8);padding:2px 6px;font:10px sans-serif;color:#444">
  Data: OKN spoke-okn (CHR 2023, AHRQ SDOH, CDC PLACES) + ruralkg RUCC</div>"""
    script = f"""
window.addEventListener("load", function () {{
  var layer = {gj.get_name()}, legends = {json.dumps(legends)}, titles = {json.dumps(meta)};
  var sel = document.getElementById("okn-layer"), cur = 0;
  function tip(l) {{
    var p = l.feature.properties, v = p.v[cur];
    return "<b>" + p.n + "</b><br>" + titles[cur] + ": " + (v === null ? "n/a" : v) +
      "<br>population " + p.p + " · RUCC " + p.u + "<br>conditions available " + p.a +
      "/11 · 11-condition rank " + p.k + " of {scored} (-1 = not scored)";
  }}
  function show(i) {{
    cur = i;
    layer.setStyle(function (f) {{ return {{fillColor: f.properties.c[i]}}; }});
    var g = legends[i];
    document.getElementById("okn-unit").textContent = g.unit;
    document.getElementById("okn-ramp").style.background = "linear-gradient(to right, " + g.gradient + ")";
    document.getElementById("okn-lo").textContent = g.lo;
    document.getElementById("okn-hi").textContent = g.hi;
  }}
  layer.eachLayer(function (l) {{ l.bindTooltip(function () {{ return tip(l); }}, {{sticky: true}}); }});
  L.DomEvent.disableClickPropagation(document.getElementById("okn-layer-panel"));
  sel.addEventListener("change", function () {{ show(+sel.value); }});
  show(0);
}});"""
    m.get_root().html.add_child(Element(panel))
    m.get_root().script.add_child(Element(script))
    if out_html:
        m.save(out_html)
    return m


# ----------------------------------------------------------------------------------------------
# 5. Workbook
# ----------------------------------------------------------------------------------------------
def write_workbook(path: str, sheets: dict):
    """One sheet per table (Arial, bold shaded header, frozen header row, autofilter)."""
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, t in sheets.items():
            t.to_excel(xw, sheet_name=name[:31], index=False)
            ws = xw.sheets[name[:31]]
            for cell in ws[1]:
                cell.font = Font(name="Arial", bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="2F5597")
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.font = Font(name="Arial", size=10)
            for i, col in enumerate(t.columns, 1):
                width = min(60, max(10, int(t[col].astype(str).str.len().quantile(.9)) + 2, len(str(col)) + 2))
                ws.column_dimensions[get_column_letter(i)].width = width
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
    return path

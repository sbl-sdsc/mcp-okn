"""County chronic-disease burden analysis over OKN (spoke-okn) query results.

Every function takes ``data`` = {"qNN": DataFrame} exactly as the reproducibility
notebook exposes it (data["q08"] ...), so the notebook and the report build share
one code path. Query map (see the notebook's query cells):

  q08,q10,q11,q12,q13  CDC PLACES place-level age-adjusted prevalence, population-
                        weighted to county (spoke-okn PREVALENCE_DpL + PARTOF_LpL)
  q14..q17             County Health Rankings 2023 county measures (PREVALENCEIN_SpL)
  q18                  pairwise shared genes among the 9 conditions (ASSOCIATES_DaG)
  q19                  gene background for the overlap test
  q20                  DOID -> MONDO identities via ubergraph skos:exactMatch
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

PLACES_Q = ["q08", "q10", "q11", "q12", "q13"]
CHR_Q = ["q14", "q15", "q16", "q17"]

# PLACES measure -> (display label, DOID used by spoke-okn, PLACES short question text)
DISEASES = {
    "diabetes": ("Diabetes", "DOID_9351", "Diabetes"),
    "obesity": ("Obesity", "DOID_9970", "Obesity"),
    "hypertension": ("Hypertension", "DOID_10763", "High Blood Pressure"),
    "high_chol": ("High cholesterol", "DOID_2349", "High Cholesterol"),
    "chd": ("Coronary heart disease", "DOID_3393", "Coronary Heart Disease"),
    "stroke": ("Stroke", "DOID_6713", "Stroke"),
    "copd": ("COPD", "DOID_3083", "COPD"),
    "asthma": ("Asthma", "DOID_2841", "Current Asthma"),
    "depression": ("Depression", "DOID_1596", "Depression"),
}
DKEYS = list(DISEASES)
LABEL = {k: v[0] for k, v in DISEASES.items()}
DOID2KEY = {"http://purl.obolibrary.org/obo/" + v[1]: k for k, v in DISEASES.items()}

CONFOUNDERS = {
    "age65": "% aged 65+",
    "nh_black": "% non-Hispanic Black",
    "hispanic": "% Hispanic",
    "rural": "% rural",
    "child_poverty": "% children in poverty",
    "some_college": "% some college",
    "uninsured": "% uninsured adults",
    "smoking": "% adult smoking",
    "inactivity": "% physically inactive",
    "food_insec": "% food insecure",
}
# Behavioural factors sit on the causal path (mediators) rather than being pure confounders;
# the "demographic" set below excludes them for the primary adjustment.
DEMOGRAPHIC = ["age65", "nh_black", "hispanic", "rural", "child_poverty", "some_college", "uninsured"]
BEHAVIOURAL = ["smoking", "inactivity", "food_insec"]

STATES = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
    "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
    "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}
# US Census regions (for the geographic-confounding check)
REGION = {}
for st, reg in [
    ("CT ME MA NH RI VT NJ NY PA", "Northeast"),
    ("IL IN MI OH WI IA KS MN MO NE ND SD", "Midwest"),
    ("DE DC FL GA MD NC SC VA WV AL KY MS TN AR LA OK TX", "South"),
    ("AZ CO ID MT NV NM UT WY AK CA HI OR WA", "West"),
]:
    for s in st.split():
        REGION[s] = reg

MIN_POP = 1000  # eligibility for ranked lists: PLACES places must cover >= this many residents
TOP_Q = 0.80    # "high prevalence" = county in the top quintile for that condition
MULTI_K = 5     # "high across multiple conditions" = top quintile in >= MULTI_K of 9


def _fips(s):
    return s.astype(str).str.zfill(5)


def load_places(data):
    df = pd.concat([data[q] for q in PLACES_Q], ignore_index=True)
    df["fips"] = _fips(df["fips"])
    for k in DKEYS + ["pop_places", "n_places"]:
        df[k] = pd.to_numeric(df[k], errors="coerce")
    df = df.drop_duplicates("fips")
    df["state"] = df["fips"].str[:2].map(STATES)
    df["region"] = df["state"].map(REGION)
    df["name"] = df["county"] + ", " + df["state"]
    return df


def load_chr(data):
    df = pd.concat([data[q] for q in CHR_Q], ignore_index=True)
    df["fips"] = _fips(df["fips"])
    num = [c for c in df.columns if c != "fips"]
    df[num] = df[num].apply(pd.to_numeric, errors="coerce").replace(-999, np.nan)
    # QC: CHR life expectancy > 95 y is implausible for a county mean (small-number artefacts)
    df["life_exp_flag"] = df["life_exp"] > 95
    df.loc[df["life_exp_flag"], "life_exp"] = np.nan
    return df.drop_duplicates("fips")


def build_county_table(data):
    p = load_places(data)
    c = load_chr(data)
    m = p.merge(c, on="fips", how="left")
    m["eligible"] = m["pop_places"] >= MIN_POP
    return m, c


# ---------------------------------------------------------------- validation
def validate_against_chr(m):
    """PLACES-place aggregate vs CHR county-native estimate for the two shared conditions."""
    out = []
    for k, ck in [("diabetes", "chr_diabetes"), ("obesity", "chr_obesity")]:
        d = m[[k, ck]].dropna()
        r, _ = stats.pearsonr(d[k], d[ck])
        rho, _ = stats.spearmanr(d[k], d[ck])
        diff = d[k] - d[ck]
        out.append({"condition": LABEL[k], "n": len(d), "pearson_r": r, "spearman_rho": rho,
                    "mean_diff_pp": diff.mean(), "loa_low": diff.mean() - 1.96 * diff.std(),
                    "loa_high": diff.mean() + 1.96 * diff.std()})
    return pd.DataFrame(out)


# ---------------------------------------------------------------- composite burden
def composite_scores(m, keys=DKEYS):
    X = m[keys].astype(float)
    Z = (X - X.mean()) / X.std(ddof=0)
    comp = Z.mean(axis=1)
    pct = X.rank(pct=True).mean(axis=1) * 100
    # PCA first component on standardized data (sign oriented to correlate positively)
    Zc = Z.fillna(0).to_numpy()
    u, s, vt = np.linalg.svd(Zc - Zc.mean(0), full_matrices=False)
    pc1 = Zc @ vt[0]
    if np.corrcoef(pc1, comp.fillna(0))[0, 1] < 0:
        pc1, vt0 = -pc1, -vt[0]
    else:
        vt0 = vt[0]
    var_expl = s[0] ** 2 / (s ** 2).sum()
    top = X.ge(X.quantile(TOP_Q)).sum(axis=1)
    return comp, pct, pd.Series(pc1, index=m.index), top, var_expl, dict(zip(keys, vt0))


def add_scores(m):
    comp, pct, pc1, top, ve, load = composite_scores(m)
    m["burden_z"] = comp
    m["burden_pct"] = pct
    m["burden_pc1"] = pc1
    m["n_top_quintile"] = top
    cm = ["diabetes", "obesity", "hypertension", "high_chol", "chd", "stroke"]
    m["cardiometabolic_z"] = composite_scores(m, cm)[0]
    m["respiratory_z"] = composite_scores(m, ["copd", "asthma"])[0]
    m["burden_no_dep_z"] = composite_scores(m, [k for k in DKEYS if k != "depression"])[0]
    m["burden_rank"] = m["burden_z"].rank(ascending=False, method="min").astype(int)
    elig = m["eligible"]
    m["burden_rank_eligible"] = np.nan
    m.loc[elig, "burden_rank_eligible"] = m.loc[elig, "burden_z"].rank(ascending=False, method="min")
    m["tier"] = np.select(
        [m["n_top_quintile"] >= 7, m["n_top_quintile"] >= MULTI_K, m["n_top_quintile"] >= 3],
        ["A", "B", "C"], default="-")
    return m, ve, load


def robustness(m):
    cols = ["burden_z", "burden_pct", "burden_pc1", "burden_no_dep_z", "cardiometabolic_z"]
    return m[cols].corr(method="spearman")


def top_by_disease(m, n=10):
    e = m[m["eligible"]]
    rows = []
    for k in DKEYS:
        t = e.nlargest(n, k)
        for i, (_, r) in enumerate(t.iterrows(), 1):
            rows.append({"condition": LABEL[k], "rank": i, "fips": r.fips, "county": r["name"],
                         "prevalence_pct": r[k], "pop_places": int(r.pop_places)})
    return pd.DataFrame(rows)


def summary_stats(m):
    rows = []
    for k in DKEYS:
        x = m[k].dropna()
        rows.append({"condition": LABEL[k], "n_counties": len(x), "mean": x.mean(), "median": x.median(),
                     "p10": x.quantile(.1), "p90": x.quantile(.9), "min": x.min(), "max": x.max(),
                     "fold_p90_p10": x.quantile(.9) / x.quantile(.1),
                     "pop_weighted_mean": np.average(m.loc[x.index, k], weights=m.loc[x.index, "pop_places"])})
    return pd.DataFrame(rows)


def state_concentration(m, col="tier", levels=("A", "B")):
    t = m[m[col].isin(levels)].groupby("state").size().rename("n_high").to_frame()
    t["n_counties"] = m.groupby("state").size()
    t["share_pct"] = 100 * t["n_high"] / t["n_counties"]
    return t.sort_values("n_high", ascending=False)


# ---------------------------------------------------------------- correlations
def spearman_matrix(df, keys=DKEYS):
    return df[keys].corr(method="spearman")


def cluster_order(corr):
    d = 1 - corr.to_numpy()
    np.fill_diagonal(d, 0)
    Z = linkage(squareform(d, checks=False), method="average")
    return [corr.index[i] for i in leaves_list(Z)], Z


def _rank_residuals(df, ys, xs):
    """Residualize rank-transformed ys on rank-transformed xs (OLS) -> partial Spearman inputs."""
    d = df[ys + xs].dropna()
    R = d.rank()
    X = np.column_stack([np.ones(len(R)), R[xs].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, R[ys].to_numpy(), rcond=None)
    res = R[ys].to_numpy() - X @ beta
    return pd.DataFrame(res, columns=ys, index=d.index), d


def partial_spearman(df, xs, keys=DKEYS):
    res, d = _rank_residuals(df, keys, xs)
    return res.corr(), len(d)


def within_state(df, keys=DKEYS):
    """Correlation after removing state means (state fixed effects) -> geographic confounding check."""
    d = df[keys + ["state"]].dropna()
    R = d[keys].rank()
    R = R - R.groupby(d["state"]).transform("mean")
    return R.corr()


def confounder_matrix(df, keys=DKEYS, conf=CONFOUNDERS):
    return pd.DataFrame({c: [stats.spearmanr(df[k], df[c], nan_policy="omit")[0] for k in keys]
                         for c in conf}, index=keys)


def variance_explained(df, keys=DKEYS):
    """R^2 of each condition on demographics alone, + behaviours, + state fixed effects (OLS on raw %)."""
    rows = []
    for k in keys:
        d = df[[k] + DEMOGRAPHIC + BEHAVIOURAL + ["state"]].dropna()
        y = d[k].to_numpy()

        def r2(X):
            X = np.column_stack([np.ones(len(d)), X])
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
            return 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()

        S = pd.get_dummies(d["state"], drop_first=True).to_numpy(float)
        rows.append({"condition": LABEL[k], "n": len(d),
                     "R2_demographic": r2(d[DEMOGRAPHIC].to_numpy()),
                     "R2_demo_behavioural": r2(d[DEMOGRAPHIC + BEHAVIOURAL].to_numpy()),
                     "R2_demo_behav_state": r2(np.column_stack([d[DEMOGRAPHIC + BEHAVIOURAL].to_numpy(), S]))})
    return pd.DataFrame(rows)


def fisher_ci(r, n, alpha=0.05):
    z = np.arctanh(np.clip(r, -0.999999, 0.999999))
    se = 1 / np.sqrt(n - 3)
    q = stats.norm.ppf(1 - alpha / 2)
    return np.tanh(z - q * se), np.tanh(z + q * se)


def pair_table(raw, part, ws, n, keys=DKEYS):
    rows = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            lo, hi = fisher_ci(raw.loc[a, b], n)
            rows.append({"pair": f"{LABEL[a]} – {LABEL[b]}", "a": a, "b": b, "rho_raw": raw.loc[a, b],
                         "ci_low": lo, "ci_high": hi, "rho_partial_demo": part.loc[a, b],
                         "rho_within_state": ws.loc[a, b],
                         "attenuation": raw.loc[a, b] - part.loc[a, b]})
    return pd.DataFrame(rows).sort_values("rho_raw", ascending=False)


# ---------------------------------------------------------------- spatial autocorrelation
def morans(gdf, cols, k=6, seed=0):
    """Global Moran's I on a k-nearest-neighbour graph of county centroids (999 permutations)."""
    import libpysal
    from esda.moran import Moran
    pts = np.column_stack([gdf.geometry.centroid.x, gdf.geometry.centroid.y])
    w = libpysal.weights.KNN.from_array(pts, k=k)
    w.transform = "r"
    np.random.seed(seed)
    rows = []
    for c in cols:
        mi = Moran(gdf[c].to_numpy(float), w, permutations=999)
        rows.append({"variable": c, "morans_I": mi.I, "p_sim": mi.p_sim, "z_sim": mi.z_sim})
    return pd.DataFrame(rows), w


def local_hotspots(gdf, col, w, seed=0):
    """Local Moran (LISA) clusters: HH hot spots, LL cold spots at pseudo-p < 0.05 (999 perms)."""
    from esda.moran import Moran_Local
    np.random.seed(seed)
    lm = Moran_Local(gdf[col].to_numpy(float), w, permutations=999)
    lab = np.array(["ns"] * len(gdf), dtype=object)
    sig = lm.p_sim < 0.05
    lab[(lm.q == 1) & sig] = "HH"
    lab[(lm.q == 3) & sig] = "LL"
    lab[(lm.q == 2) & sig] = "LH"
    lab[(lm.q == 4) & sig] = "HL"
    return lab, lm.p_sim


# ---------------------------------------------------------------- shared-gene layer (q18/q19/q20)
def gene_overlap(data):
    g = data["q18"].copy()
    g["a"] = g["d1"].map(DOID2KEY)
    g["b"] = g["d2"].map(DOID2KEY)
    M = g.pivot(index="a", columns="b", values="shared").reindex(index=DKEYS, columns=DKEYS)
    N = int(data["q19"]["n_genes"].iloc[0])
    size = pd.Series(np.diag(M), index=DKEYS)
    rows = []
    for i, a in enumerate(DKEYS):
        for b in DKEYS[i + 1:]:
            k = int(M.loc[a, b])
            na, nb = int(size[a]), int(size[b])
            exp = na * nb / N
            p = stats.hypergeom.sf(k - 1, N, na, nb)
            rows.append({"a": a, "b": b, "pair": f"{LABEL[a]} – {LABEL[b]}", "shared": k,
                         "n_a": na, "n_b": nb, "expected": exp, "fold": k / exp,
                         "jaccard": k / (na + nb - k), "p": p})
    t = pd.DataFrame(rows)
    t["fdr"] = bh(t["p"].to_numpy())
    J = pd.DataFrame(np.eye(len(DKEYS)), index=DKEYS, columns=DKEYS)
    for _, r in t.iterrows():
        J.loc[r.a, r.b] = J.loc[r.b, r.a] = r.jaccard
    return t, J, N, size


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.minimum(q, 1)
    return out


def mantel(A, B, perms=9999, seed=0):
    """Mantel test (Spearman) between two symmetric matrices' upper triangles."""
    rng = np.random.default_rng(seed)
    a = A.to_numpy()
    b = B.to_numpy()
    iu = np.triu_indices_from(a, 1)
    obs = stats.spearmanr(a[iu], b[iu])[0]
    cnt = 0
    for _ in range(perms):
        p = rng.permutation(len(a))
        if stats.spearmanr(a[iu], b[p][:, p][iu])[0] >= obs:
            cnt += 1
    return obs, (cnt + 1) / (perms + 1)


def mondo_map(data):
    t = data["q20"].copy()
    t["key"] = t["doid"].map(DOID2KEY)
    return t

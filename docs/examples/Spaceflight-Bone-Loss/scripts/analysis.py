"""analysis.py — reusable helpers for the Spaceflight-Bone-Loss OKN study.

Every function takes the notebook's ``data`` dict (``data["qNN"]`` = rows of logged query NN) and
returns pandas objects. Query numbers refer to the reproducibility notebook's query cells.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import hypergeom

# spoke-genelab assay -> short contrast label (direction: arm 1 vs arm 2; log2FC > 0 = up in arm 1)
CONTRASTS = {
    "OSD-690-f82a89dc82f2903149d2d11cbd6a130d": "SF_BM_WT",        # bone marrow, WT, Space Flight vs Ground Control
    "OSD-690-d89cbb20c4b7855f3f955e4adbb6515d": "SF_BM_Nrf2KO",    # bone marrow, Nrf2-KO, Space Flight vs Ground Control
    "OSD-546-7d689d4277a131607670c3e624202a44": "SF_hMSC_osteo",   # human MSC, osteogenic medium, Space Flight vs Ground Control
    "OSD-214-0092f94d01682ca951bc130ab667111a": "HLU_BM",          # bone marrow, hindlimb unloaded vs loaded (analog)
    "OSD-467-4d3703d7504fd48caceedadb36799194": "HLU_cortical",    # cortical bone, hindlimb unloaded vs normal loading (analog)
}
SF = ["SF_BM_WT", "SF_BM_Nrf2KO", "SF_hMSC_osteo"]


def _short(a):
    return str(a).split("/")[-1]


def signatures(data):
    """Long table contrast / human Entrez / log2FC from the compact signature queries (q08, q09).
    Mouse genes were projected to human orthologs server-side; many:1 collisions keep max |log2FC|."""
    rows = []
    for q in ("q08", "q09"):
        for _, r in data[q].iterrows():
            for tok in str(r["genes"]).split(";"):
                g, l = tok.split(":")
                rows.append((CONTRASTS[_short(r["a"])], str(g), float(l)))
    s = pd.DataFrame(rows, columns=["contrast", "entrez", "lfc"])
    s["abs"] = s.lfc.abs()
    s = s.sort_values("abs", ascending=False).drop_duplicates(["contrast", "entrez"]).drop(columns="abs")
    return s.reset_index(drop=True)


def symbol_map(data):
    """Human Entrez -> symbol, from the gene-level DE pulls (q05 cortical bone, q06 bone marrow, q07 hMSC/BM)."""
    m = {}
    for _, r in data["q05"].iterrows():
        if isinstance(r.get("hgene"), str) and isinstance(r.get("hsym"), str):
            m[_short(r["hgene"])] = r["hsym"]
    for _, r in data["q06"].iterrows():
        if isinstance(r.get("hgene"), str) and isinstance(r.get("hsym"), str):
            m[_short(r["hgene"])] = r["hsym"]
    for _, r in data["q07"].iterrows():
        if pd.notna(r.get("h")) and isinstance(r.get("hsym"), str):
            m[str(int(r["h"])) if not isinstance(r["h"], str) else r["h"]] = r["hsym"]
    return m


def bone_sets(data):
    """Curated (rdkg, q12) and broad GWAS-style (digcfdekg, q15) bone gene sets + backgrounds (q16, q17)."""
    rd = data["q12"].copy(); rd["entrez"] = rd.entrez.astype(str)
    dg = data["q15"].copy(); dg["entrez"] = dg.entrez.astype(str)
    return dict(
        rdkg=dict(zip(rd.entrez, rd.nDiseases.astype(int))),
        dig=dict(zip(dg.entrez, dg.nTraits.astype(int))),
        N_dig=int(data["q16"].N.iloc[0]),
        N_rdkg=int(data["q17"].N.iloc[0]),
    )


def bh(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)
    q = np.empty(m); q[o] = np.minimum.accumulate((p[o] * m / np.arange(1, m + 1))[::-1])[::-1]
    return np.clip(q, 0, 1)


def boneset_enrichment(data):
    """Hypergeometric test: is each spaceflight DE signature over-represented for bone gene sets?
    n = DE genes inside the supplier's universe (server-side counts, q20 rdkg / q22 digcfdekg)."""
    s = signatures(data); b = bone_sets(data)
    n_rd = {CONTRASTS[_short(a)]: int(n) for a, n in data["q20"].values}
    n_dg = {CONTRASTS[_short(a)]: int(n) for a, n in data["q22"].values}
    core = {g for g, t in b["dig"].items() if t >= 3}
    sets = [("rdkg", "rdkg rare-disease low-BMD genes (curated)", set(b["rdkg"]), b["N_rdkg"], n_rd),
            ("digcfdekg", "digcfdekg BMD/osteoporosis genes (any trait)", set(b["dig"]), b["N_dig"], n_dg),
            ("digcfdekg", "digcfdekg BMD/osteoporosis genes (>=3 traits)", core, b["N_dig"], n_dg)]
    out = []
    for c in SF:
        sig = set(s[s.contrast == c].entrez)
        for sup, name, cat, N, nmap in sets:
            n, K, k = nmap[c], len(cat), len(sig & cat)
            exp = n * K / N
            out.append(dict(contrast=c, gene_set=name, supplier=sup, N=N, K=K, n=n, k=k,
                            expected=round(exp, 1), fold=round(k / exp, 2), p=hypergeom.sf(k - 1, N, K, n)))
    e = pd.DataFrame(out); e["fdr"] = bh(e.p)
    return e.sort_values("p").reset_index(drop=True)


def term_enrichment(data):
    """GO-BP (q25/q26) and Reactome (q23/q24) over-representation from server-side k/K counts.
    BH-FDR within family x signature over the terms returned (k >= 4 Reactome, k >= 5 GO)."""
    out = []
    for fam, qk, qb in (("Reactome", "q23", "q24"), ("GO-BP", "q25", "q26")):
        d = data[qk]; nb = dict(data[qb].values); N = int(nb["ALL_prokn"])
        idcol = d.columns[1]
        for sig, g in d.groupby("sigset"):
            n = int(nb[sig])
            for _, r in g.iterrows():
                K, k = int(r.K), int(r.k); exp = n * K / N
                out.append(dict(family=fam, signature=sig, term=_short(r[idcol]), label=str(r.label).strip(),
                                k=k, K=K, n=n, N=N, expected=round(exp, 2), fold=round(k / exp, 2),
                                p=hypergeom.sf(k - 1, N, K, n)))
    o = pd.DataFrame(out)
    o["fdr"] = np.nan
    for (f, s), idx in o.groupby(["family", "signature"]).groups.items():
        o.loc[idx, "fdr"] = bh(o.loc[idx, "p"])
    return o.sort_values(["family", "signature", "p"]).reset_index(drop=True)


def gene_matrix(data):
    """One row per human gene DE in >=1 spaceflight contrast, with per-contrast log2FC and bone-set annotations."""
    s = signatures(data); m = symbol_map(data); b = bone_sets(data)
    w = s[s.contrast.isin(SF)].pivot_table(index="entrez", columns="contrast", values="lfc", aggfunc="first")
    for c in SF:
        if c not in w: w[c] = np.nan
    lf = w[SF]
    w["symbol"] = w.index.map(m)
    w["n_sf"] = lf.notna().sum(axis=1)
    w["concordant"] = lf.apply(lambda r: bool(np.sign(r.dropna()).nunique() == 1) if r.notna().sum() > 1 else np.nan, axis=1)
    w["max_abs_lfc"] = lf.abs().max(axis=1)
    w["rdkg_lowBMD_diseases"] = w.index.map(lambda g: b["rdkg"].get(g, 0))
    w["dig_BMD_traits"] = w.index.map(lambda g: b["dig"].get(g, 0))
    hlu = s[~s.contrast.isin(SF)]
    w["analog_HLU_DE"] = w.index.isin(set(hlu.entrez))
    return w


def druggability(data):
    """prokn compound -> protein evidence (q29) + named phase>=3 agents (q30) + rdkg osteoporosis-drug targets (q19)."""
    d = data["q29"].copy(); d["maxPhase"] = pd.to_numeric(d.maxPhase, errors="coerce")
    names = data["q30"].copy(); names["phase"] = pd.to_numeric(names.phase, errors="coerce")
    top = {}
    for sym, g in names.sort_values("phase", ascending=False).groupby("sym"):
        top[sym] = "; ".join(f"{n.title()} (ph{int(p)})" for n, p in list(zip(g["name"], g["phase"]))[:4])
    optarget = data["q19"].groupby("sym").drugLabel.apply(lambda x: "; ".join(sorted(set(x)))).to_dict()
    return dict(phase=dict(zip(d.sym, d.maxPhase)), ncomp=dict(zip(d.sym, d.nCompounds)), names=top, op_drugs=optarget)


def score_and_tier(data):
    """Integrate evidence axes into one score and A/B/C tiers for bone-linked spaceflight DE genes."""
    w = gene_matrix(data); dr = druggability(data)
    c = w[((w.rdkg_lowBMD_diseases > 0) | (w.dig_BMD_traits >= 1)) & w.symbol.notna()].copy()
    c["drug_max_phase"] = c.symbol.map(dr["phase"])
    c["osteoporosis_drug_target"] = c.symbol.map(dr["op_drugs"])
    c["phase3plus_agents"] = c.symbol.map(dr["names"])
    c["s_recurrence"] = (c.n_sf - 1) / 2                          # 0 (1 contrast) .. 1 (3 contrasts)
    c["s_effect"] = (c.max_abs_lfc / 3).clip(upper=1)
    c["s_mendelian"] = (c.rdkg_lowBMD_diseases > 0).astype(float)
    c["s_gwas"] = (c.dig_BMD_traits / 5).clip(upper=1)
    c["s_drug"] = np.where(c.osteoporosis_drug_target.notna(), 1.0,
                   np.where(c.drug_max_phase >= 4, 0.75, np.where(c.drug_max_phase >= 3, 0.5, 0.0)))
    c["score"] = c[["s_recurrence", "s_effect", "s_mendelian", "s_gwas", "s_drug"]].sum(axis=1).round(3)
    both = (c.rdkg_lowBMD_diseases > 0) & (c.dig_BMD_traits >= 3)
    strong_genetic = (c.rdkg_lowBMD_diseases > 0) | (c.dig_BMD_traits >= 3)
    c["tier"] = np.where(both | ((c.n_sf >= 2) & strong_genetic), "A",
                np.where(strong_genetic | ((c.n_sf >= 2) & (c.dig_BMD_traits >= 1)), "B", "C"))
    srcs = []
    for _, r in c.iterrows():
        s = ["spoke-genelab"]
        if r.rdkg_lowBMD_diseases > 0: s.append("rdkg")
        if r.dig_BMD_traits > 0: s.append("digcfdekg")
        if pd.notna(r.drug_max_phase) or pd.notna(r.osteoporosis_drug_target): s.append("prokn")
        srcs.append(s)
    c["sources"] = [", ".join(s) for s in srcs]; c["n_sources"] = [len(s) for s in srcs]
    c = c.sort_values(["tier", "score"], ascending=[True, False])
    c.index.name = "entrez"
    return c.reset_index()


# ---- mechanistic-map modules (analyst synthesis over prokn GO-BP membership, q31) ----
MODULES = {
    "Osteoblast differentiation / BMP–SMAD": ["GO_0001649", "GO_0045669", "GO_0030509", "GO_0060391", "GO_0001503",
                                               "GO_0030501", "GO_0001501", "GO_0060348"],
    "Wnt signalling & antagonists": ["GO_0016055", "GO_0090090", "GO_0090263", "GO_0060070"],
    "Collagen/ECM & mechanoresponse": ["GO_0030199", "GO_0007160", "GO_0009612", "GO_0071260"],
    "TGF-β response": ["GO_0071560", "GO_0007179"],
    "Inflammation / cytokines": ["GO_0006954", "GO_0032496", "GO_0071356", "GO_0032755"],
    "Hypoxia / angiogenesis": ["GO_0001666", "GO_0071456", "GO_0001525"],
}


def module_membership(data, tiers, max_per_module=7):
    """Assign each Tier-A gene to the module where it carries the most distinct GO-BP annotations (q31);
    ties go to the earlier module. Returns {module: [genes ranked by tier score]}."""
    q = data["q31"].copy(); q["go"] = q.go.map(_short)
    term2mod = {t: m for m, ts in MODULES.items() for t in ts}
    q["module"] = q.go.map(term2mod)
    cnt = q.drop_duplicates(["sym", "go"]).groupby(["sym", "module"]).size().reset_index(name="n")
    order = {m: i for i, m in enumerate(MODULES)}
    cnt["o"] = cnt.module.map(order)
    best = cnt.sort_values(["sym", "n", "o"], ascending=[True, False, True]).drop_duplicates("sym")
    score = dict(zip(tiers.symbol, tiers.score))
    out = {}
    for m in MODULES:
        g = sorted(best[best.module == m].sym, key=lambda s: -score.get(s, 0))
        if g: out[m] = g[:max_per_module]
    return out

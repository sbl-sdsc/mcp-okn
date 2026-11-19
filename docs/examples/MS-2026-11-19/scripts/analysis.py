"""MS multi-KG study: reusable helpers that turn logged OKN query rows into the
report's tables.  Every function takes pandas DataFrames exactly as the
reproducibility notebook loads them (``data["qNN"]``) via the name map Q.

Q maps a short logical name to the logged query's rows, e.g.
    Q = {"spoke_genes": data["q09"], ...}
"""
import re
import numpy as np
import pandas as pd
from scipy.stats import hypergeom, spearmanr

# ---------------------------------------------------------------- utilities
def tail(s):
    return str(s).rstrip("/").split("/")[-1].split("#")[-1]

def entrez_of(iri):
    m = re.search(r"(\d+)$", str(iri))
    return m.group(1) if m else None

def bh(p):
    p = np.asarray(p, float); n = len(p)
    if n == 0:
        return p
    o = np.argsort(p); r = np.empty(n); r[o] = np.arange(1, n + 1)
    q = p * n / r
    qs = np.minimum.accumulate(q[o][::-1])[::-1]
    out = np.empty(n); out[o] = np.minimum(qs, 1)
    return out

# Disease-vs-control GXA contrasts (MS / RRMS / SPMS) and treatment contrasts
GXA_DISEASE = {
    "E-GEOD-66573-g1_g2": ("RRMS vs healthy", "whole blood", "RRMS"),
    "E-GEOD-77598-g2_g1": ("MS vs healthy", "blood CD14+ monocytes", "MS"),
    "E-MTAB-2973-g3_g2": ("MS vs healthy (no exercise arm)", "whole blood", "MS"),
    "E-MTAB-69-g3_g1": ("MS vs non-inflammatory neuro. disease", "CSF leukocytes", "MS"),
}
GXA_TREAT = {
    "E-GEOD-26104-g7_g3": ("IFN-beta-1a 3 mo vs baseline", "PBMC", "MS"),
    "E-GEOD-14386-g2_g1": ("IFN-beta-1a vs none", "whole blood", "MS"),
}
Y_GENES = {"RPS4Y1", "KDM5D", "USP9Y", "DDX3Y", "ZFY", "EIF1AY", "UTY", "NLGN4Y", "TXLNGY"}

# ---------------------------------------------------------------- gene layer
def gene_symbol_map(Q):
    sym = {}
    sp = Q["spoke_genes"]
    for g, s in zip(sp.gene, sp.symbol):
        sym[entrez_of(g)] = s
    rd = Q["rdkg_edges"]; rg = rd[rd.x.astype(str).str.contains("ncbigene")]
    for g, s in zip(rg.x, rg.xlabel):
        sym.setdefault(entrez_of(g), s)
    for k in ("dig_main", "dig_tail1", "dig_tail2"):
        d = Q[k]
        for e, s in zip(d.entrez.astype(str), d.s):
            if e.isdigit():
                sym.setdefault(e, s)
    for e, s in zip(Q["gxa_symbols"].entrez.astype(str), Q["gxa_symbols"].symbol):
        sym.setdefault(e, s)
    return sym

def digcfdekg_table(Q):
    d = pd.concat([Q["dig_main"][["entrez", "s", "maxw"]], Q["dig_tail1"], Q["dig_tail2"]])
    d["entrez"] = d.entrez.astype(str)
    d = d[d.entrez.str.isdigit()]
    return d.groupby("entrez", as_index=False).agg(symbol=("s", "first"), pigean=("maxw", "max"))

def gxa_de_table(Q, sym):
    g = Q["gxa_de"].copy()
    g = g[~g.ens.astype(str).str.startswith("ENSG")]
    g["entrez"] = g.ens.astype(str)
    g["symbol"] = g.entrez.map(sym)
    meta = {**{k: v + ("disease",) for k, v in GXA_DISEASE.items()},
            **{k: v + ("treatment",) for k, v in GXA_TREAT.items()}}
    g["contrast"] = g.a.map(lambda a: meta[a][0])
    g["compartment"] = g.a.map(lambda a: meta[a][1])
    g["subtype"] = g.a.map(lambda a: meta[a][2])
    g["kind"] = g.a.map(lambda a: meta[a][3])
    g["direction"] = np.where(g.l2fc > 0, "up", "down")
    g["sex_chrom_Y"] = g.symbol.isin(Y_GENES)
    return g[["a", "contrast", "compartment", "subtype", "kind", "entrez", "symbol", "l2fc", "direction", "sex_chrom_Y"]]

def prokn_targets(Q):
    """drug -> target gene symbols (prokn indication + drug-target layer)."""
    t = Q["prokn_targets"].copy()
    u2s = dict(zip(Q["uniprot_symbols"].uniprot, Q["uniprot_symbols"].symbol))
    # proteins absent from the prokn gene->protein label layer: named from the
    # target's own prokn rdfs:label (see target_labels column)
    u2s.update({"P31358": "CD52", "Q9UQF0": "ERVW-1", "Q9Y275": "TNFSF13B"})
    # ChEMBL protein-complex / family targets -> member genes (analyst mapping
    # from the prokn target label; declared in Methods)
    complex_map = {
        "Integrin alpha-4/beta-1": ["ITGA4", "ITGB1"], "Integrin alpha-4/beta-7": ["ITGA4", "ITGB7"],
        "Interleukin-2 receptor": ["IL2RA"], "Interleukin-12": ["IL12A", "IL12B"],
        "Interleukin-23": ["IL23A", "IL12B"], "Sphingosine 1-phosphate receptor": ["S1PR1"],
        "Voltage-gated potassium channel": ["KCNA1", "KCNA2"], "Glucocorticoid receptor": ["NR3C1"],
        "Inosine-5'-monophosphate dehydrogenase (IMPDH)": ["IMPDH1", "IMPDH2"],
        "DNA topoisomerase II": ["TOP2A"], "Cyclooxygenase": ["PTGS1", "PTGS2"],
        "GABA-B receptor": ["GABBR1"], "Glutamate [NMDA] receptor": ["GRIN1"],
        "Opioid receptors; mu/kappa/delta": ["OPRM1"], "Thyroid hormone receptor": ["THRA", "THRB"],
        "Platelet-derived growth factor receptor": ["PDGFRB"],
    }
    rows = []
    for _, r in t.dropna(subset=["target"]).iterrows():
        acc = tail(r.target)
        labels = str(r.target_labels).split("|")
        name = [x for x in labels if not x.startswith(("CHEMBL", "DRUG_")) and not re.match(r"^[OPQ]\d", x)]
        genes = []
        if acc in u2s:
            genes = [u2s[acc]]
        else:
            for n in name:
                genes += complex_map.get(n, [])
        dl = [x for x in str(r.labels).split("|") if not x.startswith(("CHEMBL", "DRUG_"))]
        for gsym in genes:
            rows.append(dict(drug=(dl[0] if dl else tail(r.drug)).split("_")[0].title(), drug_iri=r.drug,
                             max_phase=r.max_phase, target_gene=gsym,
                             action=str(r.actions).split("|")[0], target_label="|".join(name)))
    return pd.DataFrame(rows).drop_duplicates(["drug", "target_gene"])

def ppi_edges(Q):
    e = pd.concat([Q["ppi_a"], Q["ppi_b"]]).drop_duplicates()
    return e.rename(columns={"a": "gene_a", "b": "gene_b"})

def evidence_matrix(Q):
    sym = gene_symbol_map(Q)
    sp = Q["spoke_genes"].copy(); sp["entrez"] = sp.gene.map(entrez_of)
    rd = Q["rdkg_edges"]; rg = rd[(rd.dir == "in") & rd.x.astype(str).str.contains("ncbigene")]
    rd_e = set(rg.x.map(entrez_of))
    dig = digcfdekg_table(Q); digw = dict(zip(dig.entrez, dig.pigean))
    wd = Q["wikidata_ms"]; wd_sym = set(wd[wd.prop.str.endswith("P2293")].label)
    bm = Q["biomarker"]; bm_e = set(bm.entity.dropna().astype(str).str.extract(r"GID(\d+)")[0].dropna())
    gx = gxa_de_table(Q, sym); gd = gx[gx.kind == "disease"]
    gx_up = gd[gd.direction == "up"].groupby("entrez").a.nunique()
    gx_dn = gd[gd.direction == "down"].groupby("entrez").a.nunique()
    gx_tr = gx[gx.kind == "treatment"].groupby("entrez").a.nunique()
    tg = prokn_targets(Q); tg_sym = tg.groupby("target_gene").drug.apply(lambda s: "; ".join(sorted(set(s))))
    tg_phase = tg.groupby("target_gene").max_phase.max()
    pe = ppi_edges(Q); deg = pd.concat([pe.gene_a, pe.gene_b]).value_counts()
    universe = set(sp.entrez) | rd_e | set(dig.entrez) | set(gd.entrez) | bm_e
    sym2e = {}
    for e, s in sym.items():
        if s is not None:
            sym2e.setdefault(s, e)
    universe |= {sym2e[s] for s in wd_sym if s in sym2e}
    universe |= {sym2e[s] for s in tg_sym.index if s in sym2e}
    rows = []
    for e in universe:
        s = sym.get(e)
        r = dict(entrez=e, symbol=s,
                 spoke_okn=e in set(sp.entrez), rdkg=e in rd_e,
                 digcfdekg=e in digw, pigean_score=digw.get(e, np.nan),
                 wikidata=s in wd_sym, biomarkerkg=e in bm_e,
                 gxa_up=int(gx_up.get(e, 0)), gxa_down=int(gx_dn.get(e, 0)),
                 gxa_ifn_response=int(gx_tr.get(e, 0)),
                 prokn_drug_target=s in tg_sym.index,
                 drugs=tg_sym.get(s, ""), max_drug_phase=tg_phase.get(s, np.nan),
                 ppi_degree_core=int(deg.get(s, 0)))
        r["gene_expression_atlas"] = (r["gxa_up"] + r["gxa_down"]) > 0
        rows.append(r)
    # drug-target genes with no Entrez bridge in the other sources (e.g. DHODH, LINGO1, ERVW-1)
    seen = {r["symbol"] for r in rows}
    for s in tg_sym.index:
        if s not in seen:
            rows.append(dict(entrez=None, symbol=s, spoke_okn=False, rdkg=False, digcfdekg=False,
                             pigean_score=np.nan, wikidata=s in wd_sym, biomarkerkg=False, gxa_up=0, gxa_down=0,
                             gxa_ifn_response=0, prokn_drug_target=True, drugs=tg_sym[s],
                             max_drug_phase=tg_phase.get(s, np.nan), ppi_degree_core=int(deg.get(s, 0)),
                             gene_expression_atlas=False))
    m = pd.DataFrame(rows)
    # biomarkerkg analytes carry full names, not symbols (analyst mapping of 4 labels, declared in Methods)
    bm_names = {"335": "APOA1", "8877": "SPHK1", "56848": "SPHK2", "6023": "RMRP"}
    m["symbol"] = [s if isinstance(s, str) else bm_names.get(str(e), f"Entrez:{e}") for s, e in zip(m.symbol, m.entrez)]
    src = ["spoke_okn", "rdkg", "digcfdekg", "wikidata", "biomarkerkg", "gene_expression_atlas", "prokn_drug_target"]
    m["n_sources"] = m[src].sum(axis=1)
    m["curated"] = m.spoke_okn | m.rdkg
    m["genetic"] = m.digcfdekg | m.wikidata
    m["score"] = (m.n_sources + 0.25 * np.log1p(m.ppi_degree_core)
                  + 0.1 * m.pigean_score.fillna(0).clip(upper=10) / 2)
    def tier(r):
        if r.n_sources >= 4 or (r.n_sources >= 3 and r.curated and r.genetic):
            return "A"
        if r.n_sources == 3 or (r.n_sources == 2 and r.curated and r.genetic):
            return "B"
        if r.n_sources == 2:
            return "C"
        return "D"
    m["tier"] = m.apply(tier, axis=1)
    def kgs(r):
        names = {"spoke_okn": "spoke-okn", "rdkg": "rdkg", "digcfdekg": "digcfdekg", "wikidata": "wikidata",
                 "biomarkerkg": "biomarkerkg", "gene_expression_atlas": "gene-expression-atlas-okn",
                 "prokn_drug_target": "prokn"}
        return [names[c] for c in src if r[c]]
    m["sources"] = m.apply(kgs, axis=1)
    m["ncRNA"] = m.symbol.astype(str).str.match(r"^(LINC|MIR\d|SNHG|SNOR|RMRP|RPPH1|.*-AS\d|LOC\d)")
    return m.sort_values(["score", "symbol"], ascending=[False, True], kind="mergesort").reset_index(drop=True), src

# ---------------------------------------------------------------- enrichment
def ora(k_df, K_df, N, n, id_col, k_col="k", K_col="K"):
    d = k_df.merge(K_df, on=id_col)
    d["N"] = N; d["n"] = n
    d["expected"] = d[K_col] * n / N
    d["fold"] = d[k_col] / d.expected
    d["p"] = [hypergeom.sf(k - 1, N, K, n) for k, K in zip(d[k_col], d[K_col])]
    d["fdr"] = bh(d.p)
    return d.sort_values("p").reset_index(drop=True)

# ---------------------------------------------------------------- drugs
DMT = {
    "interferon beta": ("Interferon", "IFNAR1/IFNAR2 signalling", "approved DMT"),
    "glatiramer": ("Immunomodulator", "MHC-II peptide competition / Th2 shift", "approved DMT"),
    "fingolimod": ("S1P receptor modulator", "S1PR1 lymphocyte sequestration", "approved DMT"),
    "siponimod": ("S1P receptor modulator", "S1PR1/S1PR5", "approved DMT"),
    "ozanimod": ("S1P receptor modulator", "S1PR1/S1PR5", "approved DMT"),
    "ponesimod": ("S1P receptor modulator", "S1PR1", "approved DMT"),
    "natalizumab": ("Anti-integrin mAb", "ITGA4 (VLA-4) blockade of BBB transmigration", "approved DMT"),
    "ocrelizumab": ("Anti-CD20 mAb", "MS4A1 B-cell depletion", "approved DMT"),
    "ofatumumab": ("Anti-CD20 mAb", "MS4A1 B-cell depletion", "approved DMT"),
    "ublituximab": ("Anti-CD20 mAb", "MS4A1 B-cell depletion", "approved DMT"),
    "rituximab": ("Anti-CD20 mAb (off-label)", "MS4A1 B-cell depletion", "off-label"),
    "alemtuzumab": ("Anti-CD52 mAb", "CD52 lymphocyte depletion", "approved DMT"),
    "cladribine": ("Purine analogue", "ADA-resistant lymphocyte depletion", "approved DMT"),
    "dimethyl fumarate": ("Fumarate", "KEAP1/NRF2 activation", "approved DMT"),
    "diroximel fumarate": ("Fumarate", "KEAP1/NRF2 activation", "approved DMT"),
    "monomethyl fumarate": ("Fumarate", "KEAP1/NRF2 activation", "approved DMT"),
    "teriflunomide": ("DHODH inhibitor", "pyrimidine synthesis in activated lymphocytes", "approved DMT"),
    "mitoxantrone": ("Cytotoxic", "TOP2A inhibition", "approved DMT (legacy)"),
    "daclizumab": ("Anti-CD25 mAb", "IL2RA (withdrawn 2018)", "withdrawn"),
    "dalfampridine": ("K+ channel blocker", "symptomatic gait", "symptomatic"),
    "fampridine": ("K+ channel blocker", "symptomatic gait", "symptomatic"),
    "baclofen": ("GABA-B agonist", "spasticity", "symptomatic"),
    "dantrolene": ("RyR antagonist", "spasticity", "symptomatic"),
    "methylprednisolone": ("Corticosteroid", "relapse treatment (NR3C1)", "relapse"),
    "tolebrutinib": ("BTK inhibitor", "BTK (B cells + microglia)", "investigational"),
    "evobrutinib": ("BTK inhibitor", "BTK", "investigational"),
    "fenebrutinib": ("BTK inhibitor", "BTK", "investigational"),
    "remibrutinib": ("BTK inhibitor", "BTK", "investigational"),
    "clemastine": ("Remyelination candidate", "HRH1 / M1 muscarinic antagonism", "investigational"),
    "opicinumab": ("Remyelination candidate", "LINGO1", "investigational"),
    "elezanumab": ("Remyelination candidate", "RGMA", "investigational"),
    "temelimab": ("Anti-HERV-W ENV mAb", "ERVW-1 (syncytin-1)", "investigational"),
    "vidofludimus": ("DHODH inhibitor", "DHODH", "investigational"),
    "masitinib": ("Tyrosine kinase inhibitor", "KIT/mast cells, microglia", "investigational"),
    "ibudilast": ("PDE inhibitor", "PDE4/10, glial", "investigational"),
    "frexalimab": ("Anti-CD40L mAb", "CD40LG co-stimulation", "investigational"),
    "cholecalciferol": ("Vitamin D", "VDR", "supplement/trial"),
}

def classify_drug(name):
    n = name.lower()
    for k, v in DMT.items():
        if k in n:
            return k, v
    return None, (None, None, None)

def drug_table(Q):
    rows = []
    rd = Q["rdkg_edges"]; t = rd[(rd.dir == "in") & (rd.p.str.endswith("treats"))]
    for _, r in t.iterrows():
        rows.append(("rdkg", r.xlabel, tail(r.d)))
    g = Q["rdkg_groups"]; g = g[g.p.str.endswith("treats")]
    for _, r in g.iterrows():
        rows.append(("rdkg", r.xlabel, "progressive MS group"))
    pk = Q["prokn_indications"]
    for _, r in pk.iterrows():
        nm = [x for x in str(r.label).split("|") if not x.startswith(("CHEMBL", "DRUG_"))]
        rows.append(("prokn", (nm[0] if nm else tail(r.drug)).split("_")[0], f"phase {r.max_phase}"))
    wd = Q["wikidata_ms"]; w = wd[wd.prop.str.endswith("P2176")]
    for _, r in w.iterrows():
        rows.append(("wikidata", r.label, "drug used for treatment"))
    sp = Q["spoke_treats"]
    for _, r in sp.iterrows():
        rows.append(("spoke-okn", r["name"], "TREATS_CtD (flagged)"))
    d = pd.DataFrame(rows, columns=["kg", "drug", "context"])
    d["drug_norm"] = (d.drug.astype(str).str.lower().str.replace(r"\(.*?\)|®|hydrochloride|sodium succinate|sodium phosphate|acetate|fumaric acid|lauryl sulfate|hemisuccinate|dose.*", "", regex=True)
                      .str.replace(r"[^a-z0-9 \-]", "", regex=True).str.strip())
    d["class_key"], cls = zip(*d.drug_norm.map(classify_drug))
    d["drug_class"], d["mechanism"], d["status"] = zip(*cls)
    d["key"] = d.class_key.fillna(d.drug_norm)
    agg = d.groupby("key").agg(name=("drug", "first"), kgs=("kg", lambda s: sorted(set(s))), n_kg=("kg", "nunique"),
                               drug_class=("drug_class", "first"), mechanism=("mechanism", "first"), status=("status", "first"),
                               contexts=("context", lambda s: "; ".join(sorted(set(map(str, s))))[:200]))
    return d, agg.sort_values(["n_kg"], ascending=False).reset_index()

# ---------------------------------------------------------------- epidemiology
def epi_table(Q, world=None):
    pr = Q["prevalence"][["iso3", "name", "value"]].copy()
    pr["prev_per_100k"] = pr.value.astype(float) * 1000  # percent -> per 100k
    co = Q["country_coords"].copy()
    xy = co.wkt.str.extract(r"POINT\(([-\d\.]+) ([-\d\.]+)\)").astype(float)
    co["lon"], co["lat"] = xy[0], xy[1]
    mo = Q["mortality"][["iso3", "value", "population"]].copy()
    mo["deaths"] = pd.to_numeric(mo.value, errors="coerce")
    mo["pop"] = pd.to_numeric(mo.population.astype(str).str.replace(",", ""), errors="coerce")
    mo["mort_per_100k"] = mo.deaths / mo["pop"] * 1e5
    e = pr.merge(co[["iso3", "lat", "lon"]], on="iso3", how="left").merge(mo[["iso3", "deaths", "pop", "mort_per_100k"]], on="iso3", how="left")
    e["abs_lat"] = e.lat.abs()
    if world is not None:
        e = e.merge(world, on="iso3", how="left")
    return e

def latitude_stats(e):
    out = {}
    rho, p = spearmanr(e.abs_lat, e.prev_per_100k, nan_policy="omit")
    out["rho_lat"], out["p_lat"], out["n_lat"] = rho, p, int(e.abs_lat.notna().sum())
    if "gdp_pc" in e:
        s = e.dropna(subset=["gdp_pc"])
        rho, p = spearmanr(s.gdp_pc, s.prev_per_100k)
        out["rho_gdp"], out["p_gdp"], out["n_gdp"] = rho, p, len(s)
        # partial: latitude effect controlling GDP via rank-residuals
        r = s[["abs_lat", "gdp_pc", "prev_per_100k"]].rank()
        def resid(y, x):
            b = np.polyfit(x, y, 1); return y - np.polyval(b, x)
        rp, pp = spearmanr(resid(r.prev_per_100k, r.gdp_pc), resid(r.abs_lat, r.gdp_pc))
        out["rho_lat_given_gdp"], out["p_lat_given_gdp"] = rp, pp
    return out

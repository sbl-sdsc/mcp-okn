"""Re-run the MS-2026-11-19 analysis outside Jupyter: regenerates figures/ and data/ from the
cached query rows in MS-2026-11-19_notebook/data/qNN.csv.  The code below is the notebook's
analysis cells concatenated in report order (the notebook is the primary record).
Run from the study folder:  python scripts/run_analysis.py
"""
import glob, os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("OKN_EXTRACTS", "data")
os.environ.setdefault("OKN_GEOJSON", os.path.join("data", "ne_countries.geojson"))
data = {os.path.basename(f)[:-4]: pd.read_csv(f) for f in sorted(glob.glob("MS-2026-11-19_notebook/data/q*.csv"))}

# ---- c00_setup.py
import os, json, numpy as np, pandas as pd
import matplotlib.pyplot as plt
import analysis as A
import okn_figstyle as F
F.apply_style()
QMAP = {"subtypes": "q06", "xrefs": "q07", "spoke_genes": "q09", "spoke_treats": "q10", "resembles": "q11",
        "prev_summary": "q12", "prevalence": "q13", "mortality": "q14", "rdkg_bridge": "q16", "rdkg_edges": "q17",
        "rdkg_groups": "q18", "prokn_nodes": "q19", "prokn_entities": "q20", "prokn_indications": "q21",
        "prokn_targets": "q22", "dig_main": "q24", "oard": "q25", "biomarker": "q26", "biomarker_dx": "q27",
        "gxa_assays": "q28", "gxa_counts": "q29", "gxa_de": "q30", "go_k": "q31", "go_K": "q32", "go_N": "q33",
        "sig_n": "q35", "re_k": "q36", "re_K": "q37", "re_N": "q38", "wikidata_ms": "q39", "country_coords": "q40",
        "wd_bridge": "q41", "biohealth_cat": "q42", "biohealth_risk": "q43", "nde": "q44", "ppi_a": "q45",
        "ppi_b": "q46", "dig_tail1": "q47", "dig_tail2": "q48", "uniprot_symbols": "q49", "gxa_symbols": "q50"}
Q = {k: data[v] for k, v in QMAP.items() if v in data}
EXTRACTS = os.environ.get("OKN_EXTRACTS", "extracts")          # where tables are written
GEOJSON = os.environ.get("OKN_GEOJSON") or next(p for p in ["ne_countries.geojson", "../data/ne_countries.geojson", "data/ne_countries.geojson"] if os.path.exists(p))  # Natural Earth boundaries + GDP covariate (study data/)
os.makedirs("figures", exist_ok=True); os.makedirs(EXTRACTS, exist_ok=True)
STATS = {}

# ---- c01_fig1.py
# Figure 1 — subtype identifier crosswalk (ubergraph) + per-KG contribution
xr = Q["xrefs"].copy()
xr["scheme"] = xr.xref.str.split(":").str[0].replace({"MESH": "MeSH", "SCTID": "SNOMED CT", "icd11.foundation": "ICD-11",
                                                     "ICD10CM": "ICD-10-CM", "ICD10WHO": "ICD-10", "MEDGEN": "MedGen", "ICD9": "ICD-9"})
xr = xr.drop_duplicates(["term", "scheme", "xref"])
order_terms = ["multiple sclerosis", "relapsing-remitting multiple sclerosis", "secondary progressive multiple sclerosis",
               "primary progressive multiple sclerosis", "progressive relapsing multiple sclerosis"]
schemes = ["DOID", "UMLS", "MeSH", "EFO", "NCIT", "SNOMED CT", "ICD-10", "ICD-10-CM", "ICD-11", "ICD-9", "Orphanet", "MedGen", "NANDO"]
cross = (xr.groupby(["label", "scheme"]).xref.apply(lambda s: "; ".join(sorted(set(s)))).unstack()
           .reindex(index=order_terms, columns=schemes))
cross.to_csv(f"{EXTRACTS}/subtype_crosswalk.csv")
# entities each KG contributed (counts from the logged queries)
pe = A.ppi_edges(Q)
contrib = pd.DataFrame([
    ("ubergraph", len(xr), "subtype xrefs (DOID/UMLS/MeSH/EFO/ICD…)"),
    ("spoke-okn", len(Q["spoke_genes"]) + len(Q["prevalence"]) + len(Q["mortality"]), "164 genes + 200 prevalence + 178 mortality rows"),
    ("rdkg", len(Q["rdkg_edges"]) + len(Q["rdkg_groups"]), "gene, drug, exposure, phenotype edges"),
    ("prokn", len(Q["prokn_indications"]) + len(Q["prokn_targets"]), "indicated compounds + drug→target rows"),
    ("digcfdekg", A.digcfdekg_table(Q).shape[0], "PIGEAN gene→trait scores"),
    ("gene-expression-atlas-okn", Q["gxa_de"].ens.nunique(), "DE genes across 6 contrasts"),
    ("oard-kg", len(Q["oard"]), "co-occurring HP phenotypes"),
    ("biomarkerkg", len(Q["biomarker"]), "risk + diagnostic biomarkers"),
    ("wikidata", len(Q["wikidata_ms"]), "Q8277 statements (genes, drugs, prevalence)"),
    ("biohealth", len(Q["biohealth_risk"]), "literature risk / protective factors"),
    ("nde", int(Q["nde"].n_datasets.sum()), "datasets indexed to MS terms"),
    ("nestkg", len(pe), "protein–protein interactions in core"),
], columns=["kg", "n", "what"]).sort_values("n")
contrib.to_csv(f"{EXTRACTS}/kg_contributions.csv", index=False)
STATS["n_kgs"] = len(contrib)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [1.15, 1]})
pres = cross.notna().astype(float).values
ax1.imshow(pres, cmap="Blues", vmin=0, vmax=1.4, aspect="auto")
ax1.set_xticks(range(len(schemes))); ax1.set_xticklabels(schemes, rotation=45, ha="right")
short = ["MS (MONDO_0005301)", "RRMS (MONDO_0005314)", "SPMS (MONDO_0000450)", "PPMS (MONDO_0000451)", "PRMS (MONDO_0000452)"]
ax1.set_yticks(range(len(short))); ax1.set_yticklabels(short)
for i in range(pres.shape[0]):
    for j in range(pres.shape[1]):
        ax1.text(j, i, "✓" if pres[i, j] else "–", ha="center", va="center", fontsize=10, color="white" if pres[i, j] else "#999")
F.panel_title(ax1, "A", "Subtype cross-references (ubergraph)")
ax2.barh(contrib.kg, contrib.n, color="#0072B2")
ax2.set_xscale("log"); ax2.set_xlabel("records contributed (log scale)")
for y, (n, w) in enumerate(zip(contrib.n, contrib.what)):
    ax2.text(n * 1.08, y, f"{n:,}", va="center", fontsize=8)
ax2.set_xlim(1, contrib.n.max() * 6)
F.panel_title(ax2, "B", "Records contributed per KG")
F.finalize(fig, 1, "figures/fig1_crosswalk_sources.png")

# ---- c02_fig2.py
# Figure 2 — evidence integration: tiers, source overlap, top-gene evidence matrix
m, SRC = A.evidence_matrix(Q)
m.to_csv(f"{EXTRACTS}/gene_evidence_matrix.csv", index=False)
tiers = m.tier.value_counts().reindex(list("ABCD")).fillna(0).astype(int)
STATS.update({"n_genes": len(m), "tier_A": int(tiers.A), "tier_B": int(tiers.B), "tier_C": int(tiers.C), "tier_D": int(tiers.D)})
SRC_LABEL = {"spoke_okn": "spoke-okn (curated)", "rdkg": "rdkg (curated)", "digcfdekg": "digcfdekg (GWAS/PIGEAN)",
             "wikidata": "wikidata (genetic assoc.)", "biomarkerkg": "biomarkerkg", "gene_expression_atlas": "GXA (differential expr.)",
             "prokn_drug_target": "prokn (drug target)"}
fig = plt.figure(figsize=(15, 7.5))
gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.6], height_ratios=[1, 1])
ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[1, 0]); ax3 = fig.add_subplot(gs[:, 1])
TC = {"A": "#D55E00", "B": "#E69F00", "C": "#56B4E9", "D": "#BBBBBB"}
ax1.bar(tiers.index, tiers.values, color=[TC[t] for t in tiers.index])
for x, v in enumerate(tiers.values):
    ax1.text(x, v * 1.15, f"{v:,}", ha="center", fontsize=9)
ax1.set_yscale("log"); ax1.set_ylabel("genes (log)"); ax1.set_ylim(1, tiers.max() * 4)
F.panel_title(ax1, "A", "Confidence-tier distribution")
cnt = pd.Series({SRC_LABEL[c]: int(m[c].sum()) for c in SRC}).sort_values()
ax2.barh(cnt.index, cnt.values, color="#009E73"); ax2.set_xscale("log"); ax2.set_xlabel("genes supported (log)")
for y, v in enumerate(cnt.values):
    ax2.text(v * 1.1, y, f"{v:,}", va="center", fontsize=8)
ax2.set_xlim(1, cnt.max() * 5)
F.panel_title(ax2, "B", "Genes per evidence source")
top = m[~m.ncRNA].head(30)
mat = top[SRC].astype(float).values
ax3.imshow(mat, cmap="Greens", vmin=0, vmax=1.3, aspect="auto")
ax3.set_xticks(range(len(SRC))); ax3.set_xticklabels([SRC_LABEL[c].split(" (")[0] for c in SRC], rotation=35, ha="right")
ax3.set_yticks(range(len(top))); ax3.set_yticklabels([f"{s}  [{t}]" for s, t in zip(top.symbol, top.tier)], fontsize=8.5)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if mat[i, j]:
            ax3.text(j, i, "●", ha="center", va="center", fontsize=8, color="#05391F")
ax3.set_xlim(-0.5, len(SRC) + 1.6)
for i, (sc, dg) in enumerate(zip(top.score, top.ppi_degree_core)):
    ax3.text(len(SRC) - 0.3, i, f"{sc:.2f} | deg {dg}", va="center", fontsize=7.5, color="#333")
F.panel_title(ax3, "C", "Top 30 genes: evidence by source (score | PPI degree)")
F.finalize(fig, 2, "figures/fig2_evidence_tiers.png")

# ---- c03_expression.py
# Figure 3 — disease-associated expression (gene-expression-atlas-okn): recurrent DE genes across contrasts
sym = A.gene_symbol_map(Q)
gx = A.gxa_de_table(Q, sym)
gx.to_csv(f"{EXTRACTS}/gxa_differential_expression.csv", index=False)
cnt = Q["gxa_counts"].copy(); STATS["gxa_contrasts_with_de"] = int(((cnt.n_up + cnt.n_down) > 0).sum())
dis = gx[(gx.kind == "disease") & ~gx.sex_chrom_Y]
rec = dis.groupby("symbol").agg(n_contrasts=("a", "nunique"), n_up=("direction", lambda s: (s == "up").sum()),
                                n_down=("direction", lambda s: (s == "down").sum())).reset_index()
rec["consistent"] = (rec.n_up == 0) | (rec.n_down == 0)
rec = rec.sort_values(["n_contrasts", "symbol"], ascending=[False, True])
rec.to_csv(f"{EXTRACTS}/gxa_recurrent_genes.csv", index=False)
STATS.update({"gxa_rec2": int((rec.n_contrasts >= 2).sum()), "gxa_rec2_consistent": int(((rec.n_contrasts >= 2) & rec.consistent).sum()),
              "gxa_de_genes": int(gx.entrez.nunique()), "gxa_y_genes": int(gx[gx.sex_chrom_Y].symbol.nunique())})
ifn = gx[gx.kind == "treatment"]
# rows: recurrent disease genes (>=2 contrasts) + top IFN-response genes also DE in disease
r2 = rec[rec.n_contrasts >= 2].symbol.tolist()
ifn_top = (ifn.groupby("symbol").l2fc.max().sort_values(ascending=False).head(14).index.tolist())
rows = list(dict.fromkeys(r2 + ifn_top))
cols = list(A.GXA_DISEASE) + list(A.GXA_TREAT)
colnames = ["RRMS blood\n66573", "MS mono\n77598", "MS blood\nMTAB-2973", "MS CSF\nMTAB-69", "IFNβ PBMC\n26104", "IFNβ blood\n14386"]
piv = gx[gx.symbol.isin(rows)].pivot_table(index="symbol", columns="a", values="l2fc", aggfunc="first").reindex(index=rows, columns=cols)
STATS["fig4_rows"] = len(rows)
fig, ax = plt.subplots(figsize=(10, max(6, 0.3 * len(rows) + 1.5)))
notes = [f"{int(rec.set_index('symbol').n_contrasts.get(s, 0))} dis." for s in rows]
im = F.diverging_heatmap(ax, piv.values, rows, colnames, row_notes=notes, vmax=3.0, na="·", rotate_x=False)
ax.axvline(3.5, color="k", lw=1.2)
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.12); cb.set_label("log2 fold-change")
F.panel_title(ax, "", "Recurrent MS-dysregulated genes and IFN-β response genes")
F.finalize(fig, 3, "figures/fig3_expression_heatmap.png")

# ---- c04_drugs.py
# Figure 4 — therapeutic landscape: requested DMT classes across KGs, prokn phase profile, target genetic support
tg = A.prokn_targets(Q); tg.to_csv(f"{EXTRACTS}/prokn_drug_targets.csv", index=False)
dlong, dagg = A.drug_table(Q)
dagg.to_csv(f"{EXTRACTS}/drug_landscape.csv", index=False)
rd_txt = dlong[dlong.kg == "rdkg"].drug.str.lower().tolist()
wd_txt = dlong[dlong.kg == "wikidata"].drug.str.lower().tolist()
pk_txt = (Q["prokn_indications"].label.astype(str).str.lower().tolist()
          + Q["prokn_targets"].labels.astype(str).str.lower().tolist())  # q22 = targets of the same MS-indicated set
DMT_ROWS = [("Interferon-β", ["interferon beta", "interferon β", "rebif", "beta-interferon", "peginterferon"]),
            ("Glatiramer acetate", ["glatiramer", "copaxone"]), ("Fingolimod", ["fingolimod", "fty720"]),
            ("Siponimod", ["siponimod"]), ("Ozanimod", ["ozanimod"]), ("Ponesimod", ["ponesimod"]),
            ("Natalizumab", ["natalizumab", "tysabri"]), ("Ocrelizumab", ["ocrelizumab"]), ("Ofatumumab", ["ofatumumab"]),
            ("Ublituximab", ["ublituximab"]), ("Alemtuzumab", ["alemtuzumab"]), ("Cladribine", ["cladribine"]),
            ("Fumarates (DMF/DRF/MMF)", ["dimethyl fumarate", "diroximel", "monomethyl fumarate", "bg00012"]),
            ("Teriflunomide", ["teriflunomide"]), ("Mitoxantrone", ["mitoxantrone"]),
            ("BTK inhibitors", ["tolebrutinib", "evobrutinib", "fenebrutinib", "remibrutinib"])]
hit = lambda txts, keys: any(k in t for t in txts for k in keys)
rows = []
for name, keys in DMT_ROWS:
    tgt = tg[tg.drug.str.lower().apply(lambda s: any(k in s for k in keys))]
    genes = sorted(set(tgt.target_gene))
    rows.append(dict(dmt=name, rdkg=hit(rd_txt, keys), prokn_indication=hit(pk_txt, keys), prokn_target=bool(genes),
                     wikidata=hit(wd_txt, keys), target_genes=", ".join(genes) or "—",
                     target_tiers=", ".join(f"{g}:{m.set_index('symbol').tier.get(g, '–')}" for g in genes) or "—"))
dmt = pd.DataFrame(rows); dmt.to_csv(f"{EXTRACTS}/dmt_kg_coverage.csv", index=False)
STATS["dmt_rows"] = len(dmt); STATS["dmt_all4"] = int(dmt[["rdkg", "prokn_indication", "prokn_target", "wikidata"]].all(axis=1).sum())
STATS["dmt_target_missing"] = ", ".join(dmt[~dmt.prokn_target].dmt)
pk = Q["prokn_indications"]
STATS.update({"prokn_compounds": len(pk), "prokn_phase4": int((pk.max_phase == 4).sum()), "prokn_phase3": int((pk.max_phase == 3).sum()),
              "prokn_targets_n": tg.target_gene.nunique(), "drug_names_total": len(dagg)})
# repurposing: prokn MS-trial drugs acting on tier A–C genes that are not approved MS DMTs
appr = {"daclizumab", "alemtuzumab", "ocrelizumab", "ofatumumab", "rituximab", "ublituximab", "natalizumab", "fingolimod", "siponimod",
        "ozanimod", "ponesimod", "dimethyl", "diroximel", "monomethyl", "teriflunomide", "cholecalciferol", "ergocalciferol", "mitoxantrone"}
tt = tg.merge(m[["symbol", "tier", "n_sources"]], left_on="target_gene", right_on="symbol", how="left")
rep = tt[tt.tier.isin(["A", "B", "C"]) & ~tt.drug.str.lower().apply(lambda s: any(a in s for a in appr))]
rep = (rep.groupby("drug").agg(targets=("target_gene", lambda s: ", ".join(sorted(set(s)))), best_tier=("tier", "min"),
                               max_phase=("max_phase", "max"), action=("action", "first")).reset_index()
          .sort_values(["best_tier", "max_phase"], ascending=[True, False]))
rep.to_csv(f"{EXTRACTS}/repurposing_candidates.csv", index=False)
STATS["repurpose_n"] = len(rep)
fig = plt.figure(figsize=(16, 8.5))
gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], height_ratios=[1, 1.1])
ax1 = fig.add_subplot(gs[:, 0]); ax2 = fig.add_subplot(gs[0, 1]); ax3 = fig.add_subplot(gs[1, 1])
cols = ["rdkg", "prokn_indication", "prokn_target", "wikidata"]
mat = dmt[cols].astype(float).values
ax1.imshow(mat, cmap="Oranges", vmin=0, vmax=1.5, aspect="auto")
ax1.set_xticks(range(4)); ax1.set_xticklabels(["rdkg\ntreats", "prokn\nindication", "prokn\ndrug→target", "wikidata\nP2176"])
ax1.set_yticks(range(len(dmt))); ax1.set_yticklabels(dmt.dmt)
for i in range(mat.shape[0]):
    for j in range(4):
        ax1.text(j, i, "✓" if mat[i, j] else "–", ha="center", va="center", color="white" if mat[i, j] else "#999", fontsize=10)
    ax1.text(3.65, i, dmt.target_tiers[i], va="center", fontsize=8.5)
ax1.set_xlim(-0.5, 6.6); ax1.text(3.65, -0.9, "target gene : tier", fontsize=9, fontweight="bold")
F.panel_title(ax1, "A", "Disease-modifying therapies across KGs")
ph = pk.max_phase.fillna(-1).value_counts().sort_index()
ax2.bar([("n/a" if p == -1 else f"{p:g}") for p in ph.index], ph.values, color="#E69F00")
for x, v in enumerate(ph.values):
    ax2.text(x, v + 1, str(v), ha="center", fontsize=9)
ax2.set_xlabel("max clinical phase (prokn / ChEMBL)"); ax2.set_ylabel("MS-indicated compounds")
F.panel_title(ax2, "B", f"prokn MS-indicated compounds (n={len(pk)})")
tc = tt.groupby("target_gene").agg(n=("drug", "nunique"), tier=("tier", "first")).sort_values("n", ascending=False).head(18)
TC = {"A": "#D55E00", "B": "#E69F00", "C": "#56B4E9", "D": "#BBBBBB"}
ax3.barh(tc.index[::-1], tc.n[::-1], color=[TC.get(t, "#BBBBBB") for t in tc.tier[::-1]])
ax3.set_xlabel("distinct drugs targeting gene (prokn)")
F.theme_legend(ax3, {f"tier {k}": v for k, v in TC.items()}, where="right", title="gene tier")
F.panel_title(ax3, "C", "Most-targeted genes and their evidence tier")
F.finalize(fig, 4, "figures/fig4_drug_landscape.png")

# ---- c05_phenotypes.py
# Figure 5 — clinical phenotypes (rdkg curated, oard-kg EHR co-occurrence) and biomarkers (biomarkerkg, wikidata)
rg = Q["rdkg_groups"]; cur = rg[rg.p.str.endswith("has_phenotype")].drop_duplicates("x").copy()
cur["hpo"] = cur.x.map(A.tail)
oa = Q["oard"].copy()
cur = cur.merge(oa[["hpo", "max_lor", "max_pair"]], on="hpo", how="left")
cur.to_csv(f"{EXTRACTS}/phenotypes_curated.csv", index=False)
oa["in_rdkg"] = oa.hpo.isin(cur.hpo)
oa.sort_values("max_lor", ascending=False).to_csv(f"{EXTRACTS}/phenotypes_oard.csv", index=False)
NEURO = r"spastic|weak|gait|ataxi|tremor|paresthes|numb|vision|optic|diplop|nystag|bladder|urin|incontin|fatigue|depress|cognit|seizure|hypertonia|vertigo|neuralgia|demyelin|dysarthria|neuropath|pain|headache|incoordination"
import re as _re
oa["neuro"] = oa.label.str.contains(NEURO, flags=_re.I)
STATS.update({"pheno_rdkg": len(cur), "pheno_rdkg_in_oard": int(cur.max_lor.notna().sum()), "pheno_oard": len(oa),
              "pheno_oard_neuro": int(oa.neuro.sum())})
bm = Q["biomarker"]; dx = Q["biomarker_dx"]
spec = dx[dx.pred == "OBCI_1000018"][["olabel", "n"]].groupby("olabel").n.sum().sort_values()
analytes = dx[dx.pred == "OBCI_1000009"].olabel.tolist()
STATS.update({"bm_total": len(bm), "bm_risk": int(((bm.role_ == "OBCI_1000008") & bm.entity.notna()).sum()), "bm_dx": int(dx[dx.obj == "OBCI_0000002"].n.max()),
              "bm_gene_analytes": len(analytes)})
fig = plt.figure(figsize=(16, 8))
gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.1], height_ratios=[1, 1])
ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[:, 1]); ax3 = fig.add_subplot(gs[1, 0])
c = cur.sort_values("max_lor", na_position="first")
ax1.barh(c.xlabel, c.max_lor.fillna(0), color=["#0072B2" if v == v else "#FFFFFF" for v in c.max_lor], edgecolor="#0072B2")
for y, v in enumerate(c.max_lor):
    ax1.text((v if v == v else 0) + 0.05, y, f"LOR {v:.2f}" if v == v else "not in oard-kg (≥20 pairs, LOR≥1.5)", va="center", fontsize=8)
ax1.set_xlabel("oard-kg max log-odds ratio"); ax1.set_xlim(0, 5.5)
F.panel_title(ax1, "A", f"Curated MS phenotypes (rdkg, n={len(cur)})")
t = pd.concat([oa[oa.neuro], oa[~oa.neuro].sort_values("max_lor", ascending=False).head(8)]).sort_values("max_lor")
ax2.barh(t.label, t.max_lor, color=["#D55E00" if n else "#BBBBBB" for n in t.neuro], hatch=None)
for y, (v, p, r) in enumerate(zip(t.max_lor, t.max_pair, t.in_rdkg)):
    ax2.text(v + 0.04, y, f"{p} pts" + ("  ★rdkg" if r else ""), va="center", fontsize=8)
ax2.set_xlabel("max log-odds ratio (EHR co-occurrence)"); ax2.set_xlim(0, t.max_lor.max() * 1.25)
F.theme_legend(ax2, {"neurological / symptom (keyword match)": "#D55E00", "other (comorbidity / likely noise)": "#BBBBBB"}, where="below", title="")
F.panel_title(ax2, "B", f"oard-kg: {int(oa.neuro.sum())} neurological + top-8 other of {len(oa)} HP terms")
ax3.barh(spec.index, spec.values, color="#009E73")
ax3.set_xlabel("diagnostic biomarker records")
ax3.text(1.02, 0.95, "Gene/protein analytes:\n" + "\n".join(f"• {a}" for a in analytes) +
         f"\n\nRisk biomarkers: {STATS['bm_risk']} (mostly SNPs)\nwikidata diagnostics: MRI, PET,\nlumbar puncture",
         transform=ax3.transAxes, va="top", fontsize=8)
F.panel_title(ax3, "C", f"biomarkerkg diagnostic biomarkers by specimen (n={STATS['bm_dx']})")
F.finalize(fig, 5, "figures/fig5_phenotypes_biomarkers.png")

# ---- c06_map.py
# Figure 6 — global MS prevalence map (spoke-okn IHME 2019 prevalence; wikidata P625 coordinates; Natural Earth boundaries)
import geopandas as gpd, folium
world = gpd.read_file(GEOJSON)
world = world[world.continent != "Antarctica"]
e = A.epi_table(Q, pd.DataFrame(world.drop(columns=["geometry", "name"])))
e.to_csv(f"{EXTRACTS}/epidemiology_by_country.csv", index=False)
g = world.merge(e[["iso3", "prev_per_100k", "mort_per_100k", "deaths", "lat"]], on="iso3", how="left")
STATS.update({"prev_countries": int(e.prev_per_100k.notna().sum()), "mort_countries": int(e.deaths.notna().sum()),
              "prev_max_country": e.loc[e.prev_per_100k.idxmax(), "name"], "prev_max": round(float(e.prev_per_100k.max()), 1),
              "prev_min": round(float(e.prev_per_100k.min()), 2), "prev_median": round(float(e.prev_per_100k.median()), 1),
              "map_matched": int(g.prev_per_100k.notna().sum())})
top3 = e.sort_values("prev_per_100k", ascending=False).head(3)
STATS["prev_top3"] = ", ".join(f"{n} ({v:.0f})" for n, v in zip(top3.name, top3.prev_per_100k))
# Country polygons on a plain background (no tile download); the interactive map below carries the street tiles.
fig, ax = plt.subplots(figsize=(15, 7.5))
g3 = g.to_crs(epsg=3857)
g3[g3.prev_per_100k.isna()].plot(ax=ax, color="#EEEEEE", edgecolor="#999", linewidth=0.3)
g3[g3.prev_per_100k.notna()].plot(ax=ax, column="prev_per_100k", cmap="YlOrRd", edgecolor="#555", linewidth=0.3, legend=True,
                                  legend_kwds={"label": "MS prevalence per 100,000 (IHME 2019)", "shrink": 0.6})
ax.set_axis_off()
STATS["map_basemap"] = "none (Natural Earth country polygons on a plain background)"
F.panel_title(ax, "", "Multiple sclerosis prevalence by country")
F.finalize(fig, 6, "figures/fig6_prevalence_map.png")

# ---- c06b_map_interactive.py
# Interactive map — folium choropleth on Esri World Street Map tiles; every country is clickable
fm = folium.Map(location=[25, 10], zoom_start=2, tiles=F.BASEMAP_TILES, attr=F.BASEMAP_ATTR)
gj = g[g.prev_per_100k.notna()].copy()
gj["prev_txt"] = gj.prev_per_100k.round(1).astype(str)
gj["mort_txt"] = gj.mort_per_100k.round(2).astype(str).replace("nan", "n/a")
import branca.colormap as bcm
cmap = bcm.linear.YlOrRd_09.scale(0, float(gj.prev_per_100k.max())); cmap.caption = "MS prevalence per 100,000 (IHME 2019, spoke-okn)"
folium.GeoJson(gj[["name", "iso3", "prev_txt", "mort_txt", "geometry"] + ["prev_per_100k"]].to_json(),
               style_function=lambda f: {"fillColor": cmap(f["properties"]["prev_per_100k"]), "color": "#555", "weight": 0.4, "fillOpacity": 0.75},
               popup=folium.GeoJsonPopup(fields=["name", "iso3", "prev_txt", "mort_txt"],
                                         aliases=["Country", "ISO3", "Prevalence /100k (spoke-okn IHME 2019)", "MS deaths /100k (spoke-okn WHO GHE)"])).add_to(fm)
cmap.add_to(fm)
F.save_map_html(fm, f"{EXTRACTS}/prevalence_map.html")
if F._in_jupyter():
    from IPython.display import HTML, display
    display(HTML(F.folium_map_iframe(fm, height=480, title="MS prevalence by country")))

# ---- c07_epi.py
# Figure 7 — prevalence correlates (latitude, GDP, continent) and literature risk/protective factors (biohealth, rdkg)
from scipy.stats import spearmanr, kruskal
ls = A.latitude_stats(e)
STATS.update({"rho_lat": round(float(ls["rho_lat"]), 3), "p_lat": f"{ls['p_lat']:.1e}", "n_lat": ls["n_lat"],
              "rho_gdp": round(float(ls["rho_gdp"]), 3), "p_gdp": f"{ls['p_gdp']:.1e}", "n_gdp": ls["n_gdp"],
              "rho_lat_gdp": round(float(ls["rho_lat_given_gdp"]), 3), "p_lat_gdp": f"{ls['p_lat_given_gdp']:.1e}"})
mo = e.dropna(subset=["mort_per_100k"])
r_m, p_m = spearmanr(mo.prev_per_100k, mo.mort_per_100k)
STATS.update({"rho_mort": round(float(r_m), 3), "p_mort": f"{p_m:.1e}", "n_mort": len(mo)})
cont = e.dropna(subset=["continent"]).groupby("continent").prev_per_100k.agg(["median", "count"]).sort_values("median", ascending=False)
cont.to_csv(f"{EXTRACTS}/prevalence_by_continent.csv")
kw = kruskal(*[gr.prev_per_100k.values for _, gr in e.dropna(subset=["continent"]).groupby("continent") if len(gr) > 2])
STATS.update({"kw_p": f"{kw.pvalue:.1e}", "cont_europe": round(float(cont.loc["Europe", "median"]), 1),
              "cont_africa": round(float(cont.loc["Africa", "median"]), 1)})
# risk / protective factors: biohealth (literature-derived SemMedDB-style predications) + rdkg contributes_to
RF = {"Viral infection (EBV, HHV-6, HERV-W, CMV, measles…)": r"virus|viral|herpes|retrovir|measles|rubella|mumps|picorna|coronav|morbilli|rhinovir|spumavir|HTLV|T-Cell Leukemia",
      "Tobacco smoke / nicotine": r"smok|tobacco|nicotine|cigarette",
      "Vitamin D / sunlight": r"vitamin d|calcitriol|cholecalciferol|ergocalciferol|cod liver",
      "Adiposity / body size / diet": r"adipos|body weight|body size|obes|diet|food|meat|milk|dairy|salt|sodium chloride|fruit|vegetable|soft drink|coffee|fish",
      "Physical activity": r"exercise|physical activ|fitness|walking|leisure",
      "Air pollution / chemicals / metals": r"pollut|pesticide|solvent|lead|mercury|bisphenol|rodenticide|irritant",
      "Sex / age / genetics": r"female|male|sex|gender|age$|genetic|genotype|haplotype|trait|proband",
      "Bacteria / microbes": r"bacteri|streptococc|pseudomonas|helicobacter|acinetobacter|mycobacter|spirochaet"}
br = Q["biohealth_risk"].copy()
rdx = Q["rdkg_edges"]; rdx = rdx[rdx.p.str.endswith("contributes_to")].drop_duplicates("xlabel")
br = pd.concat([br.assign(kg="biohealth"), pd.DataFrame({"pred": "contributes_to", "entity": rdx.xlabel, "kg": "rdkg"})])
import re as _re
br["factor"] = br.entity.map(lambda s: next((k for k, p in RF.items() if _re.search(p, str(s), _re.I)), "Other"))
br.to_csv(f"{EXTRACTS}/risk_factors.csv", index=False)
rf = br[br.factor != "Other"].groupby(["factor", "pred"]).entity.nunique().unstack(fill_value=0)
rf = rf.loc[rf.sum(axis=1).sort_values().index]
STATS.update({"rf_entities": int(br.entity.nunique()), "rf_viral": int(rf.loc[[i for i in rf.index if i.startswith("Viral")]].sum(axis=1).iloc[0])})
fig = plt.figure(figsize=(16, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])
ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[0, 1]); ax3 = fig.add_subplot(gs[1, :])
CC = {"Europe": "#0072B2", "Asia": "#E69F00", "Africa": "#009E73", "North America": "#D55E00", "South America": "#CC79A7",
      "Oceania": "#56B4E9", "Seven seas (open ocean)": "#999999"}
MK = {"Europe": "o", "Asia": "s", "Africa": "^", "North America": "D", "South America": "v", "Oceania": "P", "Seven seas (open ocean)": "X"}
for c_, gr in e.dropna(subset=["continent"]).groupby("continent"):
    ax1.scatter(gr.abs_lat, gr.prev_per_100k, s=28, c=CC.get(c_, "#999"), marker=MK.get(c_, "o"), label=c_, edgecolor="white", linewidth=0.4)
ax1.set_yscale("log"); ax1.set_xlabel("|latitude| of country centroid (wikidata P625), degrees"); ax1.set_ylabel("prevalence per 100,000 (log)")
for (_, r), off in zip(e.sort_values("prev_per_100k", ascending=False).head(3).iterrows(), [(-40, 8), (-55, -4), (6, -12)]):
    ax1.annotate(r["name"], (r.abs_lat, r.prev_per_100k), fontsize=7.5, xytext=off, textcoords="offset points",
                 arrowprops=dict(arrowstyle="-", lw=0.5, color="#666"))
ax1.text(0.02, 0.97, f"Spearman ρ = {ls['rho_lat']:.2f} (n={ls['n_lat']})\npartial ρ | GDP = {ls['rho_lat_given_gdp']:.2f}",
         transform=ax1.transAxes, va="top", fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))
F.legend_outside(ax1, where="right", title="continent")
F.panel_title(ax1, "A", "Prevalence rises with distance from the equator")
s = e.dropna(subset=["gdp_pc"])
ax2.scatter(s.gdp_pc, s.prev_per_100k, s=24, c="#0072B2", alpha=0.75, edgecolor="white", linewidth=0.4)
ax2.set_xscale("log"); ax2.set_yscale("log"); ax2.set_xlabel("GDP per capita, USD (Natural Earth; external covariate)"); ax2.set_ylabel("prevalence per 100,000 (log)")
ax2.text(0.02, 0.97, f"Spearman ρ = {ls['rho_gdp']:.2f} (n={ls['n_gdp']})", transform=ax2.transAxes, va="top", fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))
F.panel_title(ax2, "B", "Prevalence vs national income (diagnostic access confound)")
predc = {"predisposes_to_condition": "#D55E00", "causes": "#E69F00", "contributes_to": "#CC79A7", "preventative_for_condition": "#009E73"}
left = np.zeros(len(rf))
for p_ in [c for c in predc if c in rf.columns]:
    ax3.barh(rf.index, rf[p_], left=left, color=predc[p_], label=p_.replace("_", " ") + (" (rdkg)" if p_ == "contributes_to" else " (biohealth)"))
    left += rf[p_].values
ax3.set_xlabel("distinct literature-derived entities")
F.legend_outside(ax3, where="right", title="predicate (KG)")
F.panel_title(ax3, "C", "Environmental and lifestyle risk / protective factors")
F.finalize(fig, 7, "figures/fig7_epidemiology_risk.png")

# ---- c08_enrichment.py
# Figure 8 — GO BP and Reactome over-representation (prokn), hypergeometric + BH FDR
n_bp, n_re = int(Q["sig_n"].n_bp[0]), int(Q["sig_n"].n_reactome[0])
go = A.ora(Q["go_k"], Q["go_K"], int(Q["go_N"].N_bp[0]), n_bp, "term")
re_ = A.ora(Q["re_k"], Q["re_K"], int(Q["re_N"].N_reactome[0]), n_re, "pathway")
go.to_csv(f"{EXTRACTS}/enrichment_go_bp.csv", index=False); re_.to_csv(f"{EXTRACTS}/enrichment_reactome.csv", index=False)
STATS.update({"go_n": n_bp, "go_N": int(Q["go_N"].N_bp[0]), "go_tested": len(go), "go_sig": int((go.fdr < 0.05).sum()),
              "re_n": n_re, "re_N": int(Q["re_N"].N_reactome[0]), "re_tested": len(re_), "re_sig": int((re_.fdr < 0.05).sum()),
              "sig_in_prokn": int(Q["sig_n"].n_in_prokn[0])})
THEMES = {"Interferon / JAK-STAT": r"interferon|JAK|STAT|type I|type II", "T-cell activation / TCR": r"T cell|T-cell|TCR|CD28|PD-1|ZAP|co-stimul|Costimulation|alpha-beta",
          "B cell / antigen presentation": r"B cell|antigen|MHC|immunoglobulin|BCR", "Innate / inflammasome": r"inflamma|NLRP|Toll|TLR|innate|NK|natural killer|microglia|IL-1|Interleukin-1 ",
          "Cytokine signalling": r"cytokine|interleukin|Interleukin|IL-|chemokine|TNF|tumor necrosis"}
TCOL = {"Interferon / JAK-STAT": "#D55E00", "T-cell activation / TCR": "#0072B2", "B cell / antigen presentation": "#009E73",
        "Innate / inflammasome": "#CC79A7", "Cytokine signalling": "#E69F00", "Other": "#999999"}
import re as _re
def theme_of(lbl):
    for t, pat in THEMES.items():
        if _re.search(pat, lbl, _re.I):
            return t
    return "Other"
fig, axes = plt.subplots(1, 2, figsize=(16, 8.2))
for ax, d, letter, ttl in [(axes[0], go, "A", f"GO biological process (top 20 of {len(go)} tested)"),
                           (axes[1], re_, "B", f"Reactome pathways (top 20 of {len(re_)} tested)")]:
    t = d.head(20)
    labs = [l if len(l) <= 48 else l[:46] + "…" for l in t.label]
    th = [theme_of(l) for l in t.label]
    F.ranked_barh(ax, labs, list(-np.log10(t.fdr)), themes=th, theme_colors=TCOL,
                  annots=[f"×{f:.1f} ({k}/{K})" for f, k, K in zip(t.fold, t.k, t.K)], xlabel="−log10(FDR)")
    F.panel_title(ax, letter, ttl)
F.theme_legend(axes[1], {k: v for k, v in TCOL.items()}, where="below", title="theme")
F.finalize(fig, 8, "figures/fig8_enrichment.png")

# ---- c09_ppi.py
# Figure 9 — protein–protein interaction network among the MS core signature (nestkg)
import networkx as nx
pe = A.ppi_edges(Q)
G = nx.Graph(); G.add_edges_from(zip(pe.gene_a, pe.gene_b))
tier_of = dict(zip(m.symbol, m.tier))
deg = dict(G.degree())
STATS.update({"ppi_edges": G.number_of_edges(), "ppi_nodes": G.number_of_nodes(),
              "ppi_hub1": max(deg, key=deg.get), "ppi_hub1_deg": max(deg.values())})
hubs = pd.DataFrame({"symbol": list(deg), "degree": list(deg.values())})
hubs["tier"] = hubs.symbol.map(tier_of).fillna("–")
hubs["betweenness"] = hubs.symbol.map(nx.betweenness_centrality(G))
hubs = hubs.sort_values("degree", ascending=False); hubs.to_csv(f"{EXTRACTS}/ppi_hubs.csv", index=False)
core = [n for n in G if deg[n] >= 8]
H = G.subgraph(core).copy()
H = H.subgraph(max(nx.connected_components(H), key=len)).copy()
STATS["ppi_shown_nodes"] = H.number_of_nodes()
pos = nx.spring_layout(H, seed=7, k=0.55, iterations=200)
TC = {"A": "#D55E00", "B": "#E69F00", "C": "#56B4E9", "D": "#BBBBBB", "–": "#BBBBBB"}
fig, ax = plt.subplots(figsize=(12, 10))
nx.draw_networkx_edges(H, pos, ax=ax, alpha=0.12, width=0.6)
for t, shape in [("A", "o"), ("B", "s"), ("C", "^"), ("D", "D"), ("–", "D")]:
    nl = [n for n in H if tier_of.get(n, "–") == t]
    if nl:
        nx.draw_networkx_nodes(H, pos, nodelist=nl, node_shape=shape, node_color=TC[t], ax=ax,
                               node_size=[25 + 6 * deg[n] for n in nl], edgecolors="white", linewidths=0.5,
                               label=f"tier {t}" if t != "–" else "not tiered")
lab = sorted(H, key=lambda n: -deg[n])[:30]
nx.draw_networkx_labels(H, pos, labels={n: n for n in lab}, font_size=8.5, ax=ax,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
ax.axis("off")
F.legend_outside(ax, where="below", title="confidence tier (size ∝ degree)", ncol=5)
F.panel_title(ax, "", f"PPI network of MS core genes (degree ≥ 8; {H.number_of_nodes()} nodes, {H.number_of_edges()} edges)")
F.finalize(fig, 9, "figures/fig9_ppi_network.png")

# ---- c10_mechmap.py
# Figure 10 — mechanistic map: MS → mechanistic module → tier A–C gene → drug (prokn drug→target edges only)
import tempfile
from mechanistic_map import render_mechanistic_map
MODULES = {
    "HLA class II / antigen presentation": ["HLA-DRB1", "HLA-DQB1", "HLA-DRA", "HLA-DPB1", "CD40", "CD86"],
    "T-cell activation & co-stimulation": ["IL2RA", "IL7R", "CD58", "CD6", "CBLB", "TAGAP", "PTPRC", "MALT1", "CD52", "DHODH"],
    "Cytokine / JAK–STAT / Th1–Th17": ["IFNG", "IL17A", "IL12A", "IL12B", "TYK2", "STAT3", "STAT4", "TNFRSF1A", "CSF2"],
    "B cell / plasma cell": ["MS4A1", "CD19", "CXCR5", "TNFSF13B", "IKZF3", "BTK"],
    "Innate / microglia / inflammasome": ["NLRP3", "IL1B", "TLR4", "ITGAM", "MERTK", "CASP1", "KIT", "CCR2"],
    "Lymphocyte trafficking / BBB": ["ITGA4", "S1PR1", "S1PR5"],
    "Redox / remyelination / conduction": ["KEAP1", "LINGO1", "RGMA", "HRH1", "KCNA1", "VDR"],
}
genes_in_kg = set(m.symbol)
assert all(g in genes_in_kg for v in MODULES.values() for g in v), [g for v in MODULES.values() for g in v if g not in genes_in_kg]
drug_short = lambda d: d.replace(" Fumaric Acid", "").replace(" Hydrochloride", "").replace(" Lauryl Sulfate", "").replace(" Fumarate", "") if "Dimethyl" not in d and "Diroximel" not in d and "Monomethyl" not in d else d
DRUGS = {}
for mod, gl in MODULES.items():
    d = tg[tg.target_gene.isin(gl) & (tg.max_phase.fillna(0) >= 2)].copy()
    d["short"] = d.drug.map(drug_short)
    d = d.sort_values(["max_phase", "short"], ascending=[False, True]).drop_duplicates("short")
    DRUGS[mod] = d.short.head(8).tolist()
mod_rows = [(mod, g, m.set_index("symbol").tier.get(g), "; ".join(sorted(set(tg[tg.target_gene == g].drug))))
            for mod, gl in MODULES.items() for g in gl]
pd.DataFrame(mod_rows, columns=["module", "gene", "tier", "prokn_drugs"]).to_csv(f"{EXTRACTS}/mechanistic_modules.csv", index=False)
STATS["mech_modules"] = len(MODULES); STATS["mech_genes"] = sum(len(v) for v in MODULES.values())
STATS["mech_drugs"] = len({d for v in DRUGS.values() for d in v})
tmp_png = render_mechanistic_map("Multiple sclerosis", MODULES, DRUGS, out_path=os.path.join(tempfile.gettempdir(), "ms_mechanistic_map_raw.png"),
                       title="MS gene–module–drug mechanistic map (entities retrieved from OKN KGs)",
                       subtitle="modules = analyst grouping of tier A–C genes guided by GO/Reactome enrichment; drugs = prokn drug→target, max phase ≥ 2",
                       gene_legend="Gene (tier A–C or drug target)", drug_legend="Drug (prokn, phase ≥ 2)")
img = plt.imread(tmp_png)  # place the rendered network on a report-style figure and save it
fig, ax = plt.subplots(figsize=(img.shape[1] / 150, img.shape[0] / 150))
ax.imshow(img); ax.axis("off")
F.finalize(fig, 10, "figures/fig10_mechanistic_map.png")

# ---- c11_stats.py
# Summary quantities for the report (written to stats.json) + subtype table + ranked-results extract
nde = Q["nde"].set_index("condition").n_datasets
sub_lbl = dict(zip(Q["subtypes"].term.map(A.tail), Q["subtypes"].label))
tr = Q["rdkg_edges"]; tr = tr[(tr.dir == "in") & tr.p.str.endswith("treats")].drop_duplicates(["d", "xlabel"])
subtab = pd.DataFrame({"mondo": list(sub_lbl), "label": list(sub_lbl.values())})
subtab["nde_datasets"] = subtab.mondo.map(nde).fillna(0).astype(int)
subtab["rdkg_treats_edges"] = subtab.mondo.map(tr.d.map(A.tail).value_counts()).fillna(0).astype(int)
subtab["n_xrefs"] = subtab.label.map(xr.groupby("label").xref.nunique()).fillna(0).astype(int)
subtab.to_csv(f"{EXTRACTS}/subtypes.csv", index=False)
for k, v in zip(subtab.mondo, subtab.nde_datasets):
    STATS[f"nde_{k}"] = int(v)
STATS["nde_total"] = int(nde.sum())
STATS["rdkg_treats_total"] = int(len(tr)); STATS["rdkg_group_treats"] = int(Q["rdkg_groups"].p.str.endswith("treats").sum())
gc = Q["gxa_counts"].set_index("a")
for a in list(A.GXA_DISEASE) + list(A.GXA_TREAT):
    k = a.replace("-", "_")
    STATS[f"up_{k}"] = int(gc.n_up.get(a, 0)); STATS[f"dn_{k}"] = int(gc.n_down.get(a, 0))
STATS.update({"gxa_assays": int(Q["gxa_assays"].assay.nunique()), "gxa_studies": int(Q["gxa_assays"].study.nunique()),
              "spoke_genes": len(Q["spoke_genes"]),
              "rdkg_genes": int(m.rdkg.sum()), "dig_genes": int(m.digcfdekg.sum()), "wd_assoc": int(Q["wikidata_ms"].prop.str.endswith("P2293").sum()),
              "wd_drugs": int(Q["wikidata_ms"].prop.str.endswith("P2176").sum()), "oard_n": len(Q["oard"]),
              "n_ncRNA": int(m.ncRNA.sum()), "ncRNA_list": ", ".join(m[m.ncRNA].symbol),
              "top10": ", ".join(m.head(10).symbol), "n_targets_tierAB": int(m[m.tier.isin(["A", "B"]) & m.prokn_drug_target].shape[0]),
              "tierA_targets": ", ".join(m[(m.tier == "A") & m.prokn_drug_target].symbol)})
pig = A.digcfdekg_table(Q).sort_values("pigean", ascending=False)
STATS["pigean_top"] = ", ".join(f"{s} ({p:.1f})" for s, p in zip(pig.symbol.head(6), pig.pigean.head(6)))
STATS["n_pigean_ge3"] = int((pig.pigean >= 3).sum())
cols = ["symbol", "entrez", "tier", "score", "n_sources", "sources", "spoke_okn", "rdkg", "digcfdekg", "pigean_score", "wikidata",
        "biomarkerkg", "gxa_up", "gxa_down", "gxa_ifn_response", "prokn_drug_target", "drugs", "max_drug_phase", "ppi_degree_core", "ncRNA"]
ranked = m[cols].copy(); ranked["sources"] = ranked.sources.map(lambda l: "; ".join(l)); ranked.insert(0, "rank", range(1, len(ranked) + 1))
ranked.to_csv(f"{EXTRACTS}/ranked_results.csv", index=False)
json.dump(STATS, open(f"{EXTRACTS}/stats.json", "w"), indent=1, default=str)
print({k: STATS[k] for k in ["tier_A", "tier_B", "go_sig", "re_sig", "rho_lat", "top10"]})

"""build_package.py — build the Spaceflight-Bone-Loss deliverables from the notebook's cached query rows.

Usage (from the study folder):  python scripts/build_package.py
Reads  Spaceflight-Bone-Loss_notebook/data/qNN.csv  (the logged query rows), recomputes the analysis with
scripts/analysis.py, writes data/*.tsv + data/stats.json, the workbook, the filled report .md (from
data/report_template.md) and renders the HTML with build_report_from_markdown.
"""
import glob, json, os, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import analysis as A
from build_report_html import build_report_from_markdown, candidate_table, kpis_from_stats, fill_stats

STUDY = "Spaceflight-Bone-Loss"
data = {os.path.basename(f)[:-4]: pd.read_csv(f) for f in sorted(glob.glob(f"{ROOT}/{STUDY}_notebook/data/q*.csv"))}

sig = A.signatures(data); bone = A.boneset_enrichment(data); terms = A.term_enrichment(data)
tiers = A.score_and_tier(data); gm = A.gene_matrix(data)
inv = sig.assign(direction=sig.lfc.gt(0).map({True: "up", False: "down"})).pivot_table(
    index="contrast", columns="direction", values="entrez", aggfunc="nunique", fill_value=0)
inv["total"] = inv.sum(axis=1)
be = bone.set_index(["contrast", "gene_set"])
R, D = "rdkg rare-disease low-BMD genes (curated)", "digcfdekg BMD/osteoporosis genes (>=3 traits)"
stats = {
    "n_contrasts_flight": 3, "n_contrasts_analog": 2,
    "de_bm_wt": int(inv.loc["SF_BM_WT", "total"]), "de_bm_ko": int(inv.loc["SF_BM_Nrf2KO", "total"]),
    "de_hmsc": int(inv.loc["SF_hMSC_osteo", "total"]), "de_hlu_bm": int(inv.loc["HLU_BM", "total"]),
    "de_hlu_cort": int(inv.loc["HLU_cortical", "total"]),
    "sf_union": int(len(gm)), "sf_recurrent": int((gm.n_sf >= 2).sum()), "sf_all3": int((gm.n_sf == 3).sum()),
    "sf_all3_concordant": int((gm.query("n_sf == 3").concordant == True).sum()),
    "n_candidates": int(len(tiers)), "tierA": int((tiers.tier == "A").sum()), "tierB": int((tiers.tier == "B").sum()),
    "tierC": int((tiers.tier == "C").sum()), "tierA_recurrent": int((tiers[tiers.tier == "A"].n_sf >= 2).sum()),
    "rdkg_set": int(bone.K[bone.supplier == "rdkg"].iloc[0]), "dig_set": int(bone[bone.gene_set.str.contains("any")].K.iloc[0]),
    "dig_core": int(bone[bone.gene_set.str.contains(">=3")].K.iloc[0]),
    "hmsc_rdkg_fold": float(be.loc[("SF_hMSC_osteo", R), "fold"]), "hmsc_rdkg_k": int(be.loc[("SF_hMSC_osteo", R), "k"]),
    "hmsc_rdkg_fdr": f'{be.loc[("SF_hMSC_osteo", R), "fdr"]:.1e}',
    "hmsc_dig_core_fold": float(be.loc[("SF_hMSC_osteo", D), "fold"]), "hmsc_dig_core_k": int(be.loc[("SF_hMSC_osteo", D), "k"]),
    "hmsc_dig_core_fdr": f'{be.loc[("SF_hMSC_osteo", D), "fdr"]:.1e}',
    "go_sig_hmsc": int(((terms.family == "GO-BP") & (terms.signature == "SF_hMSC_osteo") & (terms.fdr < 0.05)).sum()),
    "re_sig_hmsc": int(((terms.family == "Reactome") & (terms.signature == "SF_hMSC_osteo") & (terms.fdr < 0.05)).sum()),
    "go_sig_bm": int(((terms.family == "GO-BP") & (terms.signature == "SF_BM") & (terms.fdr < 0.05)).sum()),
    "re_sig_bm": int(((terms.family == "Reactome") & (terms.signature == "SF_BM") & (terms.fdr < 0.05)).sum()),
    "n_op_drugs_rdkg": int(data["q18"].drug.nunique()), "n_op_drugbank": int(data["q18"].drug.str.contains("drugbank").sum()),
    "n_op_targets": int(data["q19"].sym.nunique()),
    "n_druggable_ph3": int((tiers.drug_max_phase >= 3).sum()), "n_druggable_ph4": int((tiers.drug_max_phase >= 4).sum()),
    "n_biomarker_snps": int(data["q28"].entity.nunique()),
}
json.dump(stats, open(f"{ROOT}/data/stats.json", "w"), indent=1)

# ---- extracts ----
cols = ["entrez", "symbol", "tier", "score", "n_sf", "SF_BM_WT", "SF_BM_Nrf2KO", "SF_hMSC_osteo", "concordant",
        "rdkg_lowBMD_diseases", "dig_BMD_traits", "drug_max_phase", "phase3plus_agents", "osteoporosis_drug_target",
        "analog_HLU_DE", "n_sources", "sources"]
rank = tiers[cols].copy(); rank.insert(0, "rank", range(1, len(rank) + 1))
rank.to_csv(f"{ROOT}/data/ranked_candidates.tsv", sep="\t", index=False)
bone.to_csv(f"{ROOT}/data/boneset_enrichment.tsv", sep="\t", index=False)
terms.to_csv(f"{ROOT}/data/go_reactome_enrichment.tsv", sep="\t", index=False)
inv.to_csv(f"{ROOT}/data/contrast_inventory.tsv", sep="\t")
sig.to_csv(f"{ROOT}/data/spaceflight_signatures.tsv", sep="\t", index=False)

# ---- workbook ----
wb = Workbook(); hdr = PatternFill("solid", fgColor="1F4E79"); tierfill = {"A": "C6EFCE", "B": "FFEB9C", "C": "F2F2F2"}
def sheet(ws, df, tier_col=None):
    ws.append(list(df.columns))
    for c in ws[1]: c.font = Font(name="Arial", bold=True, color="FFFFFF"); c.fill = hdr; c.alignment = Alignment(wrap_text=True)
    for r in df.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in r])
    for row in ws.iter_rows(min_row=2):
        for c in row: c.font = Font(name="Arial", size=10)
        if tier_col is not None:
            t = row[tier_col].value
            for c in row: c.fill = PatternFill("solid", fgColor=tierfill.get(t, "FFFFFF"))
    for i, col in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = min(48, max(10, len(str(col)) + 2))
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
ws = wb.active; ws.title = "Ranked Results"; sheet(ws, rank, tier_col=list(rank.columns).index("tier"))
sheet(wb.create_sheet("Contrasts"), inv.reset_index())
sheet(wb.create_sheet("Bone-set enrichment"), bone)
sheet(wb.create_sheet("GO-Reactome"), terms[terms.fdr < 0.05])
sheet(wb.create_sheet("Osteoporosis drugs (rdkg)"), data["q18"])
sheet(wb.create_sheet("Drug targets (prokn)"), data["q19"])
sheet(wb.create_sheet("Repurposing agents"), data["q30"])
sheet(wb.create_sheet("Phenotypes (rdkg)"), data["q27"])
sheet(wb.create_sheet("Biomarkers"), data["q28"])
mr = pd.DataFrame([
    ("DE call", "spoke-genelab reified DE, adj_p <= 0.05 and |log2FC| >= 1; mouse -> human orthologs (IS_ORTHOLOG_MGiG), max |log2FC| on collisions"),
    ("Flight contrasts", "OSD-690 marrow WT and Nrf2-KO; OSD-546 hMSC osteogenic (vetted Space Flight vs Ground Control)"),
    ("Analog contrasts", "OSD-467 cortical bone HLU vs normal loading; OSD-214 marrow HLU vs loaded"),
    ("Curated bone set", "rdkg genes of MONDO diseases with HP_0000939 / HP_0000938 / HP_0004349 (related_to, genetic_association)"),
    ("Broad bone set", "digcfdekg geneToTrait, 10 BMD / osteoporosis traits; core = >= 3 traits"),
    ("Enrichment", "Hypergeometric vs explicit KG universe; BH-FDR. GO-BP + Reactome via prokn (symbol join)"),
    ("Tiers", "A: rdkg and >=3 traits, or >=2 flight contrasts with rdkg/>=3 traits; B: rdkg or >=3 traits, or >=2 contrasts with any trait; C: other"),
    ("Score", "recurrence + effect + Mendelian + GWAS + druggability (0-5)"),
    ("Abbreviations", "BM bone marrow; BMD bone mineral density; DE differentially expressed; FDR false-discovery rate; GO-BP Gene Ontology biological process; "
                      "HLU hindlimb unloading; hMSC human mesenchymal stem cell; KG knowledge graph; KO knockout; SF spaceflight; UPR unfolded protein response"),
    ("Framing", "Hypothesis generation; rodent / cell-culture transcriptomes, ortholog-inferred; associations not causal"),
], columns=["item", "rule"])
sheet(wb.create_sheet("Methods & Rules"), mr)
wb.save(f"{ROOT}/{STUDY}_results.xlsx")

# ---- report .md (filled) and HTML ----
tmpl = open(f"{ROOT}/data/report_template.md").read()
open(f"{ROOT}/{STUDY}_report.md", "w").write(fill_stats(tmpl, stats))
rows = []
for r in rank.itertuples():
    lf = {k: getattr(r, k) for k in ("SF_BM_WT", "SF_BM_Nrf2KO", "SF_hMSC_osteo")}
    hm = lf["SF_hMSC_osteo"]
    rows.append(dict(rank=r.rank, symbol=r.symbol, tier=r.tier, score=r.score, n_sf=int(r.n_sf),
                     bm_wt="" if pd.isna(lf["SF_BM_WT"]) else f'{lf["SF_BM_WT"]:+.2f}',
                     bm_ko="" if pd.isna(lf["SF_BM_Nrf2KO"]) else f'{lf["SF_BM_Nrf2KO"]:+.2f}',
                     hmsc="" if pd.isna(hm) else f"{hm:+.2f}",
                     hmsc_dir="not DE" if pd.isna(hm) else ("up" if hm > 0 else "down"),
                     rdkg=int(r.rdkg_lowBMD_diseases), dig=int(r.dig_BMD_traits),
                     phase="" if pd.isna(r.drug_max_phase) else int(r.drug_max_phase),
                     agents=r.phase3plus_agents if isinstance(r.phase3plus_agents, str) else "",
                     n_sources=int(r.n_sources), sources=r.sources.split(", ")))
table = candidate_table(
    rows,
    [("rank", "#"), ("symbol", "Gene"), ("tier", "Tier"), ("score", "Score"), ("n_sf", "Flight contrasts"),
     ("bm_wt", "BM WT log2FC"), ("bm_ko", "BM Nrf2-KO log2FC"), ("hmsc", "hMSC log2FC"), ("rdkg", "rdkg low-BMD diseases"),
     ("dig", "digcfdekg traits"), ("phase", "Max drug phase"), ("agents", "Phase ≥3 agents"), ("n_sources", "sources (n)")],
    search_keys=["symbol", "agents"], numeric_keys=["rank", "score", "n_sf", "rdkg", "dig", "phase"], default_sort="rank",
    extra_filters=[("tier", "Tier"), ("n_sf", "Flight contrasts"), ("hmsc_dir", "hMSC direction")],
    sources_col=("n_sources", "sources"))
kpis = kpis_from_stats(stats, [("n_candidates", "bone-linked flight DE genes"), ("tierA", "Tier-A genes"),
                               ("hmsc_dig_core_fold", "× BMD-GWAS enrichment (hMSC)"), ("hmsc_rdkg_fold", "× Mendelian low-BMD enrichment"),
                               ("go_sig_hmsc", "GO-BP terms FDR<0.05"), ("n_druggable_ph3", "targets with phase ≥3 agents")])
build_report_from_markdown(f"{ROOT}/{STUDY}_report.md", f"{ROOT}/{STUDY}_report.html", kpis=kpis, table=table, stats=stats)

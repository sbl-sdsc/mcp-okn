"""Render the interactive HTML report FROM the Markdown, and fill the delivered .md
from the same stats.json so prose, cards and table can never disagree."""
import json, sys, pandas as pd
sys.path.insert(0, __file__.rsplit('/',1)[0])
from build_report_html import (build_report_from_markdown, candidate_table,
                               kpis_from_stats, fill_stats)

MD, HTML = 'Liver-Lipid/Liver-Lipid_report.md', 'Liver-Lipid/Liver-Lipid_report.html'
stats = json.load(open('Liver-Lipid/data/stats.json'))
core  = pd.read_csv('Liver-Lipid/data/ranked_candidates.tsv', sep='\t')
core['sources_list'] = core.sources.apply(lambda s: [x.strip(" '") for x in s.strip('[]').split(',')])

rows = [{
  "rank": int(r["rank"]), "gene": r.humanSymbol, "mouse": r.mouse_symbols,
  "log2FC": round(float(r.log2fc), 2), "adj_p": f"{r.adj_p_value:.1e}",
  "direction": r.direction, "datasets": r.osd_sources, "n_datasets": int(r.n_datasets),
  "liver_disease": "yes" if r.liver_disease_rdkg else "no",
  "nafld_trait": "yes" if r.nafld_trait_digcfdekg else "no",
  "lipid_pathway": "yes" if r.lipid_pathway else "no",
  "diseases": (r.rdkg_diseases if isinstance(r.rdkg_diseases, str) else ""),
  "tier": r.tier, "score": float(r.score),
  "n_sources": int(r.n_sources), "sources_list": r.sources_list,
} for _, r in core.iterrows()]

table = candidate_table(
    rows,
    columns=[("rank","#"),("gene","human gene"),("mouse","mouse gene(s)"),("log2FC","log2FC"),
             ("adj_p","adj p"),("direction","direction"),("datasets","dataset(s)"),
             ("liver_disease","liver disease (rdkg)"),("nafld_trait","NAFLD trait (digcfdekg)"),
             ("lipid_pathway","lipid pathway (prokn)"),("diseases","curated disease terms"),
             ("n_sources","sources (n)"),("score","score"),("tier","tier")],
    search_keys=["gene","mouse","diseases","datasets"],
    numeric_keys=["rank","log2FC","score","n_sources","n_datasets"],
    default_sort="rank", page_size=25,
    extra_filters=[("tier","tier"),("direction","direction"),("datasets","dataset"),
                   ("liver_disease","liver disease"),("nafld_trait","NAFLD trait")],
    sources_col=("n_sources","sources_list"),
)

kpis = kpis_from_stats(stats, [
    ("datasets_matched","of 4 datasets reproduced"),
    ("deg_mouse","liver DEGs (adj-p ≤ 0.05, |log2FC| ≥ 1)"),
    ("human_core","human ortholog core"),
    ("lipcat_fold","× lipid catabolic process (FDR 0.027)"),
    ("nafld_fold","× NAFLD trait set (FDR 0.0074)"),
    ("tier_a","tier-A candidates"),
])

_src = open(MD).read()                    # READ first — writing first would truncate it
open(MD, 'w').write(fill_stats(_src, stats))   # deliver a standalone .md
build_report_from_markdown(MD, HTML, kpis=kpis, table=table, stats=stats,
                           footer="OKN federated SPARQL · reproduction of Beheshti et al. 2019 "
                                  "(doi:10.1038/s41598-019-55869-2) · hypothesis generation, not causal inference")

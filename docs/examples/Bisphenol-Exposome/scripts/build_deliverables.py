#!/usr/bin/env python3
import sys, json
sys.path.insert(0,"/sessions/vibrant-inspiring-edison/mnt/.claude/skills/okn-report-style/scripts")
import build_report_html as B

MD="Bisphenol-Exposome_report.md"; HTML="Bisphenol-Exposome_report.html"
stats=json.load(open("stats.json"))

# 1) fill stats into the delivered .md so it reads standalone
md=open(MD).read()
md_filled=B.fill_stats(md, stats, strict=False)
open(MD,"w").write(md_filled)

# 2) results table
rows=json.load(open("data/results_table.json"))
columns=[("chemical","Chemical"),("disease","Disease"),("category","Category"),("tier","Tier"),
 ("shared_genes","Shared genes"),("effect_domain","Effect domain"),("aop","Curated AOP"),
 ("n_evidence","Evidence types"),("min_AC50_uM","Min AC50 (µM)"),("key_genes","Key linking genes")]
table=B.candidate_table(
 rows, columns,
 search_keys=["chemical","disease","category","key_genes"],
 numeric_keys=["shared_genes","n_evidence","min_AC50_uM","n_sources"],
 page_size=25,
 default_sort=("shared_genes","desc") if True else None,
 extra_filters=[("tier","Tier"),("category","Category"),("aop","Curated AOP")],
 sources_col=("n_sources","sources"),
)

# 3) KPI cards from stats
kpis=B.kpis_from_stats(stats,[
 ("n_chem_ice_active","bisphenols (active HTS)"),
 ("n_target_genes","human target genes"),
 ("n_disease_sig","enriched diseases (FDR<0.05)"),
 ("n_tierA","Tier-A chemical–disease links"),
 ("n_aops","curated AOP chains"),
 ("n_kgs","knowledge graphs integrated"),
])

# 4) render HTML from the (now filled) markdown
B.build_report_from_markdown(MD, HTML, kpis=kpis, table=table, stats=stats)
print("built", HTML)

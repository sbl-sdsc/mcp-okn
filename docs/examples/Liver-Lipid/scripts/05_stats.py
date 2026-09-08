"""Single source of truth for every headline number in the report (stats.json)."""
import json, pandas as pd
de   = pd.read_csv('Liver-Lipid/data/liver_de_measured.tsv', sep='\t', dtype={'entrez':str})
core = pd.read_csv('Liver-Lipid/data/ranked_candidates.tsv', sep='\t')
rdkg = pd.read_csv('Liver-Lipid/data/rdkg_liver_disease_genes.tsv', sep='\t')
dig  = pd.read_csv('Liver-Lipid/data/enrichment_digcfdekg_traits.tsv', sep='\t')
sok  = pd.read_csv('Liver-Lipid/data/spokeokn_liver_disease_genes.tsv', sep='\t')
go   = pd.read_csv('Liver-Lipid/data/enrichment_go_bp.tsv', sep='\t')
rx   = pd.read_csv('Liver-Lipid/data/enrichment_reactome.tsv', sep='\t')
oard = pd.read_csv('Liver-Lipid/data/oard_liver_phenotypes.tsv', sep='\t')
sens = pd.read_csv('Liver-Lipid/data/enrichment_threshold_sensitivity.tsv', sep='\t')
nafld = dig[dig.category == 'non-alcoholic fatty liver disease'].iloc[0]
lipcat = go[go.label == 'lipid catabolic process'].iloc[0]
mll = rx[rx.label.str.contains('MLL4 and MLL3')].iloc[0]
paper_go = sens[(sens.family=='GO') & (sens.threshold.str.startswith("paper"))]

S = {
 "paper_datasets": 4, "datasets_matched": 3, "datasets_excluded": 1,
 "clean_liver_contrasts": 13, "confounded_liver_contrasts": 20,
 "osd168_liver_sfgc_assays": 9,
 "measured_rows": int(len(de)), "measured_genes": int(de.entrez.nunique()),
 "osd25_measured": int((de.osd=='OSD-25').sum()), "osd47_measured": int((de.osd=='OSD-47').sum()),
 "osd137_measured": int((de.osd=='OSD-137').sum()),
 "deg_mouse": 130, "deg_osd25": 116, "deg_osd47": 13, "deg_osd137": 2,
 "deg_up": 93, "deg_down": 38, "recurrent_genes": 1,
 "human_core": int(len(core)), "orthologs_dropped": 8,
 "bg_human": 4604, "bg_go": 2160, "bg_rx": 1720, "sig_in_go_bg": 61, "sig_in_rx_bg": 48,
 "go_tested": int(len(go)), "go_fdr05": int((go.fdr<=0.05).sum()),
 "rx_tested": int(len(rx)), "rx_fdr05": int((rx.fdr<=0.05).sum()),
 "lipcat_fold": round(float(lipcat.fold),2), "lipcat_k": int(lipcat.k), "lipcat_K": int(lipcat.K),
 "lipcat_fdr": f"{float(lipcat.fdr):.3f}",
 "mll_fold": round(float(mll.fold),2), "mll_fdr": f"{float(mll.fdr):.3f}", "mll_k": int(mll.k), "mll_K": int(mll.K),
 "rdkg_liver_terms": int(rdkg.mondo.nunique()), "rdkg_liver_genes": int(rdkg.entrez.nunique()),
 "rdkg_K": 279, "rdkg_k": 15, "rdkg_expected": 7.51, "rdkg_fold": 2.0, "rdkg_p": "0.0074",
 "nafld_K": int(nafld.K), "nafld_k": int(nafld.k), "nafld_fold": round(float(nafld.fold),2),
 "nafld_p": f"{float(nafld.p):.1e}", "nafld_fdr": f"{float(nafld.fdr):.4f}",
 "sok_genes": int(sok.gene_symbol.nunique()), "sok_K": 426, "sok_k": 10,
 "sok_fold": 0.87, "sok_p": "0.72",
 "oard_diseases": int(oard.mondo.nunique()), "oard_hp": int(oard.hp.nunique()),
 "oard_steatosis_diseases": 21,
 "tier_a": int((core.tier=='A').sum()), "tier_b": int((core.tier=='B').sum()), "tier_c": int((core.tier=='C').sum()),
 "paper_sig": 3216, "paper_sig_in_go_bg": 1560, "paper_go_fdr05": int((paper_go.fdr<=0.05).sum()),
 "kg_count": 6,
}
json.dump(S, open('Liver-Lipid/data/stats.json','w'), indent=1)
print(json.dumps(S, indent=1))

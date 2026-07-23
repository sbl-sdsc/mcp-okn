"""Build stats.json - the single source of every headline number in the SANS report."""
import pandas as pd, numpy as np, json
D='/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics'
R=pd.read_csv(f'{D}/data/ranked_genes.csv'); H=pd.read_csv(f'{D}/data/human_projected_de.csv')
M=pd.read_csv(f'{D}/data/de_master.csv'); core=pd.read_csv(f'{D}/data/core_set.csv')
E=pd.read_csv(f'{D}/data/enrichment_results.csv'); T=pd.read_csv(f'{D}/data/trait_enrichment.csv')
DR=pd.read_csv(f'{D}/data/prokn_core_drugs.csv'); RD=pd.read_csv(f'{D}/data/rdkg_core.csv')
OC=pd.read_csv(f'{D}/data/rdkg_ocular_diseases.csv'); HP=pd.read_csv(f'{D}/data/oard_hp.csv')
s={
 "clean_contrasts_total":188,"confounded_excluded":492,
 "panel_assays":26,"panel_studies":int(M.osd.nunique()),
 "ocular_assays":5,"cns_assays":12,"cardio_assays":5,"flyhead_assays":4,
 "de_rows":int(len(M)),"mouse_genes_de":int(M[M.species=='mouse'].entrez.nunique()),
 "fly_genes_de":int(M[M.species=='fly'].entrez.nunique()),
 "ortho_mouse_edges":22899,"ortho_fly_edges":19324,
 "human_genes_projected":int(R.hEntrez.nunique()),
 "projection_rows":int(len(H)),
 "core_genes":int(len(core)),
 "xspecies_genes":int(R.xspecies_ok.sum()),
 "multisystem_genes":int((R.mouse_systems>=2).sum()),
 "ocular_genes":int(R.in_ocular.sum()),
 "bridge_shared_genes":16326,
 "go_terms_tested":int((E.family=='GO').sum()),"reactome_tested":int((E.family=='Reactome').sum()),
 "go_sig":int(((E.family=='GO')&(E.fdr<0.05)).sum()),
 "reactome_sig":int(((E.family=='Reactome')&(E.fdr<0.05)).sum()),
 "enrich_sig_total":int((E.fdr<0.05).sum()),
 "go_background":8290,"go_n":75,"reactome_background":6032,"reactome_n":61,
 "trait_tested":int(len(T)),"trait_sig":int((T.fdr<0.05).sum()),
 "trait_background":21710,"trait_n":166,
 "top_go_fold":float(E[E.family=='GO'].sort_values('p').iloc[0].fold),
 "top_go_fdr":float(E[E.family=='GO'].sort_values('p').iloc[0].fdr),
 "lhon_fold":float(T[T.trait_label=='Leber hereditary optic neuropathy'].iloc[0].fold),
 "lhon_fdr":float(T[T.trait_label=='Leber hereditary optic neuropathy'].iloc[0].fdr),
 "drug_targets":int(DR.symbol.nunique()),"drug_compounds":int(DR.compound.nunique()),
 "rdkg_genes":int(RD.symbol.nunique()),"rdkg_diseases":int(RD.disease.nunique()),
 "rdkg_drugs":int(RD.drug.dropna().nunique()),
 "ocular_disease_genes":int(OC.symbol.nunique()),"ocular_diseases":int(OC.disease.nunique()),
 "hp_terms":int(HP.hp.nunique()),
 "spoke_okn_perturb_compounds":7,"spoke_okn_perturb_rows":44,
 "tier_a":int((R.tier=='A').sum()),"tier_b":int((R.tier=='B').sum()),"tier_c":int((R.tier=='C').sum()),
 "kgs_used":6,
}
json.dump(s,open(f'{D}/data/stats.json','w'),indent=1)
print(json.dumps(s,indent=1))

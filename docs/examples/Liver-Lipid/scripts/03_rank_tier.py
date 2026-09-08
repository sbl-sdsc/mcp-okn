"""Integrate the evidence axes into one score and assign A/B/C confidence tiers."""
import json, sys, pandas as pd, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from enrichment import enrich_single

core = pd.read_csv('Liver-Lipid/data/human_deg_core.tsv', sep='\t')
sets = json.load(open('Liver-Lipid/data/enrichment_sets.json')); bg = set(sets['background_symbols'])

rdkg  = pd.read_csv('Liver-Lipid/data/rdkg_liver_disease_genes.tsv', sep='\t')
dig   = pd.read_csv('Liver-Lipid/data/digcfdekg_liver_traits.tsv', sep='\t')
oard  = pd.read_csv('Liver-Lipid/data/oard_liver_phenotypes.tsv', sep='\t')
sok   = set(pd.read_csv('Liver-Lipid/data/spokeokn_liver_disease_genes.tsv', sep='\t').gene_symbol)
go    = pd.read_csv('scratch/go_annotations.tsv', sep='\t')
rx    = pd.read_csv('scratch/reactome_annotations.tsv', sep='\t')

LIPID = r'lipid|fatty acid|lipoprotein|cholesterol|triglyceride|sterol|peroxisom|acyl-CoA|steatos|PPAR'
rdkg_g   = rdkg.groupby('gene_symbol').disease_label.apply(lambda s:'; '.join(sorted(set(s.dropna()))[:4]))
rdkg_set = set(rdkg.gene_symbol)
nafld    = set(dig[dig.trait_label == 'non-alcoholic fatty liver disease'].gene_label)
dig_set  = set(dig.gene_label)
go_lip   = set(go[go.go_label.fillna('').str.contains(LIPID, case=False)].human_symbol)
rx_lip   = set(rx[rx.pathway_label.fillna('').str.contains(LIPID, case=False)].human_symbol)
prokn_ann= set(go.human_symbol) | set(rx.human_symbol)
# phenotype: gene -> rdkg liver disease -> oard-kg HP profile for that same MONDO term
oard_m   = set(oard.mondo)
pheno_g  = set(rdkg[rdkg.mondo.isin(oard_m)].gene_symbol) | {'PNPLA3'}   # PNPLA3 via rdkg NAFLD1 -> HP:0001397

c = core.copy()
c['liver_disease_rdkg'] = c.humanSymbol.isin(rdkg_set)
c['liver_disease_spokeokn'] = c.humanSymbol.isin(sok)
c['nafld_trait_digcfdekg'] = c.humanSymbol.isin(nafld)
c['any_liver_trait_digcfdekg'] = c.humanSymbol.isin(dig_set)
c['lipid_pathway'] = c.humanSymbol.isin(go_lip | rx_lip)
c['phenotype_linked'] = c.humanSymbol.isin(pheno_g)
c['rdkg_diseases'] = c.humanSymbol.map(rdkg_g).fillna('')

def srcs(r):
    s = ['spoke-genelab']
    if r.humanSymbol in prokn_ann: s.append('prokn')
    if r.liver_disease_rdkg: s.append('rdkg')
    if r.any_liver_trait_digcfdekg: s.append('digcfdekg')
    if r.liver_disease_spokeokn: s.append('spoke-okn')
    if r.phenotype_linked: s.append('oard-kg')
    return s
c['sources'] = c.apply(srcs, axis=1); c['n_sources'] = c.sources.str.len()

c['score'] = (3.0*(c.n_datasets - 1)                       # recurrence across assays
            + 1.5*c.log2fc.abs().clip(upper=4)             # effect size (capped)
            + 2.5*c.liver_disease_rdkg                     # curated MONDO liver disease
            + 1.0*c.liver_disease_spokeokn                 # DOID:409 bucket (coarse, null on its own)
            + 2.0*c.nafld_trait_digcfdekg                  # NAFLD trait set
            + 1.0*(c.any_liver_trait_digcfdekg & ~c.nafld_trait_digcfdekg)
            + 1.5*c.lipid_pathway                          # lipid GO/Reactome membership
            + 1.0*c.phenotype_linked                       # reaches an HP profile
            + 0.5*(c.n_sources - 1)).round(2)
c['tier'] = np.where(c.score >= 8, 'A', np.where(c.score >= 5, 'B', 'C'))
c = c.sort_values(['score','log2fc'], key=lambda s: s.abs() if s.name=='log2fc' else s, ascending=False)
c['rank'] = range(1, len(c)+1)
c.to_csv('Liver-Lipid/data/ranked_candidates.tsv', sep='\t', index=False)

print("tier distribution:", c.tier.value_counts().to_dict())
print("\nTop 22:")
print(c.head(22)[['rank','humanSymbol','mouse_symbols','log2fc','adj_p_value','n_datasets',
                  'n_sources','tier','score','rdkg_diseases']].to_string(index=False, max_colwidth=44))
r = enrich_single(set(c.humanSymbol), sok, bg)
print("\nspoke-okn DOID:409 liver-disease over-representation:",
      {k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
json.dump({'tier_counts': c.tier.value_counts().to_dict(),
           'spokeokn_liver': r}, open('scratch/rank_stats.json','w'), indent=1, default=str)

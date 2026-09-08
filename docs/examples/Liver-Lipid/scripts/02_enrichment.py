"""GO biological-process AND Reactome over-representation (two separate families),
hypergeometric + Benjamini-Hochberg FDR against the explicit prokn-annotated background."""
import json, sys, pandas as pd
sys.path.insert(0, __file__.rsplit('/',1)[0])
from enrichment import enrich

sets = json.load(open('Liver-Lipid/data/enrichment_sets.json'))
sig  = set(sets['signature_symbols']); bg0 = set(sets['background_symbols'])

def run(ann_tsv, cat_col, lab_col, name):
    a = pd.read_csv(ann_tsv, sep='\t')
    a = a[a.human_symbol.isin(bg0)]
    bg = set(a.human_symbol)                       # annotated background only
    cat2genes = a.groupby(cat_col).human_symbol.apply(set).to_dict()
    labels    = a.drop_duplicates(cat_col).set_index(cat_col)[lab_col].to_dict()
    df = enrich(sig, cat2genes, bg, kmin=3, Kmin=5)
    df.insert(1, 'label', df.category.map(labels))
    df['id'] = df.category.str.rsplit('/', n=1).str[-1]
    df.to_csv(f'Liver-Lipid/data/enrichment_{name}.tsv', sep='\t', index=False)
    sig_n = len(sig & bg)
    print(f"\n=== {name.upper()}  background N={len(bg)}  signature n={sig_n}  "
          f"categories tested={len(df)}  FDR<=0.05: {(df.fdr<=0.05).sum()}")
    print(df.head(18)[['id','label','K','k','expected','fold','p','fdr']].to_string(index=False))
    return df

go = run('scratch/go_annotations.tsv',       'go',      'go_label',      'go_bp')
rx = run('scratch/reactome_annotations.tsv', 'pathway', 'pathway_label', 'reactome')

# targeted check of the paper's named claims
for name, df, pat in [('GO', go, 'lipid|fatty acid|circadian|lipoprotein|cholesterol|triglyceride|steroid'),
                      ('Reactome', rx, 'lipid|fatty acid|circadian|lipoprotein|cholesterol|triglyceride|PPAR|Metabolism of lipids')]:
    h = df[df.label.fillna('').str.contains(pat, case=False)]
    print(f"\n--- {name}: paper-claimed themes, top 12 by p ---")
    print(h.head(12)[['id','label','K','k','fold','p','fdr']].to_string(index=False))

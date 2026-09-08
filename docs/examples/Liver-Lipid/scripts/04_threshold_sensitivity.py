"""Sensitivity analysis: re-run both enrichment families at the ORIGINAL paper's own
selection rule (fold-change >= 1.2, i.e. |log2FC| >= 0.263, with adj_p <= 0.05) alongside
the workflow's stricter rule (|log2FC| >= 1). Separates 'the finding does not reproduce'
from 'the finding reproduces only under the original's more permissive cut-off'."""
import json, sys, pandas as pd, numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0]); from enrichment import enrich

DE  = pd.read_csv('Liver-Lipid/data/liver_de_measured.tsv', sep='\t', dtype={'entrez':str})
OM  = (pd.read_csv('Liver-Lipid/data/ortholog_map.tsv', sep='\t', dtype={'mouse_entrez':str})
         .drop_duplicates(['mouse_entrez','human_symbol'])[['mouse_entrez','human_symbol']])
go  = pd.read_csv('scratch/go_annotations.tsv', sep='\t')
rx  = pd.read_csv('scratch/reactome_annotations.tsv', sep='\t')
bg0 = set(json.load(open('Liver-Lipid/data/enrichment_sets.json'))['background_symbols'])
LIPID = r'lipid|fatty acid|lipoprotein|cholesterol|triglyceride|sterol|peroxisom|acyl-CoA|steatos|PPAR'

def sig_for(lfc_cut):
    d = DE[(DE.adj_p_value <= 0.05) & (DE.log2fc.abs() >= lfc_cut)]
    return set(OM[OM.mouse_entrez.isin(set(d.entrez))].human_symbol), d

rows = []
for name, cut in [("workflow rule  |log2FC| >= 1", 1.0), ("paper's rule   FC >= 1.2 (|log2FC| >= 0.263)", 0.263)]:
    sig, d = sig_for(cut)
    print(f"\n########## {name}   mouse DEGs={d.entrez.nunique()}  human signature={len(sig)}")
    for fam, ann, cat, lab in [('GO', go, 'go', 'go_label'), ('Reactome', rx, 'pathway', 'pathway_label')]:
        a = ann[ann.human_symbol.isin(bg0)]
        bg = set(a.human_symbol)
        e = enrich(sig, a.groupby(cat).human_symbol.apply(set).to_dict(), bg, kmin=3, Kmin=5)
        e['label'] = e.category.map(a.drop_duplicates(cat).set_index(cat)[lab].to_dict())
        e['id'] = e.category.str.rsplit('/', n=1).str[-1]
        e['family'], e['threshold'] = fam, name
        rows.append(e)
        lip = e[e.label.fillna('').str.contains(LIPID, case=False)]
        print(f"  {fam}: N={len(bg)} n={len(sig&bg)} tested={len(e)} FDR<=0.05={(e.fdr<=0.05).sum()} "
              f"| lipid-themed FDR<=0.05={(lip.fdr<=0.05).sum()}")
        print(lip.head(10)[['id','label','K','k','fold','p','fdr']].to_string(index=False))
        circ = e[e.label.fillna('').str.contains('circadian|rhythm|clock', case=False)]
        if len(circ): print("  circadian:\n" + circ[['id','label','K','k','fold','p','fdr']].to_string(index=False))
        else: print("  circadian: no term reached k>=3")
pd.concat(rows).to_csv('Liver-Lipid/data/enrichment_threshold_sensitivity.tsv', sep='\t', index=False)

"""Collapse mouse liver DEGs to human orthologs and build the enrichment sets."""
import json, sys, pandas as pd
sys.path.insert(0, __file__.rsplit('/',1)[0])
from collapse_orthologs import collapse

DE   = pd.read_csv('Liver-Lipid/data/liver_de_measured.tsv', sep='\t', dtype={'entrez':str})
ORTH = pd.read_csv('Liver-Lipid/data/ortholog_map.tsv', sep='\t',
                   dtype={'mouse_entrez':str,'human_entrez':str})
om = ORTH.drop_duplicates(['mouse_entrez','human_entrez'])[
        ['mouse_entrez','mouse_symbol','human_entrez','human_symbol']]

deg = DE[(DE.adj_p_value <= 0.05) & (DE.log2fc.abs() >= 1)].copy()
mrg = deg.merge(om, left_on='entrez', right_on='mouse_entrez', how='inner')
human = collapse(mrg.rename(columns={'human_entrez':'hEntrez','human_symbol':'humanSymbol'}))
# recurrence across the three assays, carried on the human row
rec = (deg.groupby('entrez').osd.nunique().rename('n_datasets').reset_index()
         .merge(om, left_on='entrez', right_on='mouse_entrez')
         .groupby('human_entrez').n_datasets.max())
human['n_datasets'] = human.hEntrez.map(rec).fillna(1).astype(int)
human['direction']  = human.log2fc.apply(lambda x: 'up in flight' if x > 0 else 'down in flight')
human['osd_sources'] = human.hEntrez.map(
    mrg.groupby('human_entrez').osd.apply(lambda s: '|'.join(sorted(set(s)))))
human.to_csv('Liver-Lipid/data/human_deg_core.tsv', sep='\t', index=False)

bg_sym = set(om[om.mouse_entrez.isin(set(DE.entrez))].human_symbol.dropna())
sig_sym = set(human.humanSymbol.dropna())
json.dump({'background_symbols': sorted(bg_sym), 'signature_symbols': sorted(sig_sym)},
          open('Liver-Lipid/data/enrichment_sets.json','w'), indent=1)
print(f"mouse DEG {deg.entrez.nunique()} -> human {len(human)} "
      f"(dropped {deg.entrez.nunique()-mrg.entrez.nunique()} without ortholog)")
print(f"ambiguous (n_mouse_map>1): {(human.n_mouse_map>1).sum()}   sign_flip: {human.sign_flip.sum()}")
print(f"background symbols {len(bg_sym)}   signature symbols {len(sig_sym)}")
print(human.sort_values('log2fc', key=abs, ascending=False).head(15)
      [['humanSymbol','mouse_symbols','log2fc','adj_p_value','n_datasets','osd_sources']].to_string(index=False))

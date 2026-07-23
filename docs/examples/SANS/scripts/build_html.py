import sys, json, math
sys.path.insert(0,'/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics/scripts')
import pandas as pd, numpy as np
from build_report_html import build_report_from_markdown, candidate_table, kpis_from_stats
D='/sessions/magical-intelligent-maxwell/mnt/SANS/SANS_cross_species_transcriptomics'
stats=json.load(open(f'{D}/data/stats.json'))
fmt=lambda v: (f"{v:.2g}" if isinstance(v,float) and (v<0.01 or v>=1000) else (f"{v:,.1f}" if isinstance(v,float) else f"{v:,}"))
stats_fmt={k:fmt(v) for k,v in stats.items()}

R=pd.read_csv(f'{D}/data/ranked_genes.csv')
RD=pd.read_csv(f'{D}/data/rdkg_core.csv'); DR=pd.read_csv(f'{D}/data/prokn_core_drugs.csv')
TRT=pd.read_csv(f'{D}/data/digcfdekg_traits.csv'); GO=pd.read_csv(f'{D}/data/prokn_go_core.csv')
rd_g=set(RD.symbol.dropna()); dr_g=set(DR.symbol.dropna()); tr_g=set(TRT.symbol.dropna()); go_g=set(GO.symbol.dropna())
rows=[]
for _,r in R.head(200).iterrows():
    sym=str(r.humanSymbol).split('|')[0]
    src=['spoke-genelab','spoke-okn']  # measurement + verified human-gene bridge
    if sym in go_g or sym in dr_g: src.append('prokn')
    if sym in rd_g: src.append('rdkg')
    if sym in tr_g: src.append('digcfdekg')
    rows.append({'rank':int(r['rank']),'tier':r.tier,'gene':sym,'entrez':int(r.hEntrez),
      'systems':r.systems if isinstance(r.systems,str) else '',
      'primary_system':('ocular' if r.in_ocular else ('CNS' if r.in_cns else ('cardiovascular' if r.in_cardio else 'fly head'))),
      'direction':r.consensus_dir,
      'cross_species':'yes' if r.xspecies_ok else 'no',
      'studies':int(r.n_studies),'tissues':int(r.n_tissues),
      'max_abs_lfc':round(float(r.max_abs_lfc),2),
      'min_padj':f"{float(r.min_padj):.2g}",
      'score':round(float(r.score),1),
      'n_sources':len(src),'src':src})
cols=[('rank','rank'),('tier','tier'),('gene','gene'),('entrez','human Entrez'),
      ('primary_system','primary system'),('systems','systems detected'),('direction','direction in flight'),
      ('cross_species','cross-species'),('studies','OSDR studies'),('tissues','tissues'),
      ('max_abs_lfc','max |log2FC|'),('min_padj','min adj. p'),('score','consistency score')]
table=candidate_table(rows,cols,search_keys=['gene','systems','tier','primary_system'],
  numeric_keys=['rank','entrez','studies','tissues','max_abs_lfc','score','n_sources'],
  page_size=25, default_sort=('rank','asc'),
  extra_filters=[('tier','confidence tier'),('primary_system','organ system'),
                 ('direction','direction'),('cross_species','cross-species')],
  sources_col=('n_sources','src'))
kpis=kpis_from_stats(stats_fmt,[
  ('panel_assays','vetted spaceflight assays'),
  ('human_genes_projected','human orthologues'),
  ('core_genes','conserved SANS core genes'),
  ('enrich_sig_total','enriched categories (FDR<0.05)'),
  ('top_go_fold','fold: ATP-synthase enrichment'),
  ('kgs_used','knowledge graphs queried'),
])
build_report_from_markdown(f'{D}/SANS_cross_species_transcriptomics_report.md',
  f'{D}/SANS_cross_species_transcriptomics_report.html', kpis=kpis, table=table, stats=stats_fmt)

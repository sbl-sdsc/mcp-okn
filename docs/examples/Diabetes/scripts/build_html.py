import sys, json; sys.path.insert(0,'scripts')
import pandas as pd, numpy as np
from build_report_html import build_report_from_markdown, candidate_table, kpis_from_stats, load_stats, fill_stats
S=json.load(open('stats.json'))
g=pd.read_csv('data/ranked_genes_tiered.csv')
SRC={'digcfdekg_PIGEAN':'digcfdekg','spokeokn_DaG':'spoke-okn','biomarkerkg_GWAS':'biomarkerkg',
     'prokn_ClinVar':'prokn','gxa_DE':'GXA','pankgraph_eQTL':'pankgraph','pankgraph_OCR':'pankgraph'}
rows=[]
for r in g[g.tier.isin(['A','B'])].itertuples():
    srcs=[]
    for k in str(r.sources).split('|'):
        v=SRC.get(k)
        if v and v not in srcs: srcs.append(v)
    ev=[]
    if r.ev_curated>0: ev.append('curated')
    if r.ev_genetic>0: ev.append('genetic')
    if r.ev_statistical>0: ev.append('statistical')
    if r.ev_diffexpr>0: ev.append('differential activity')
    if r.ev_qtl>0: ev.append('molecular QTL')
    rows.append(dict(symbol=r.symbol, tier=r.tier, score=round(float(r.score),2),
        streams=int(r.n_disease_streams),
        curated=int(r.ev_curated), genetic='yes' if r.ev_genetic else 'no',
        pigean='' if pd.isna(r.pigean_weight) else round(float(r.pigean_weight),2),
        variants=int(r.n_gwas_variants or 0),
        diffexpr='yes' if r.ev_diffexpr else 'no', qtl='yes' if r.ev_qtl else 'no',
        druggable='yes' if r.ev_druggable else 'no',
        compounds=0 if pd.isna(r.n_direct_compounds) else int(r.n_direct_compounds),
        exposure='yes' if r.ev_exposure else 'no',
        evidence_types=', '.join(ev),
        sources=srcs, n_sources=len(srcs)))
cols=[('symbol','gene'),('tier','tier'),('score','score'),('streams','disease streams'),
      ('curated','curated'),('genetic','genetic assoc.'),('pigean','PIGEAN'),('variants','risk variants'),
      ('diffexpr','diff. activity'),('qtl','molecular QTL'),('druggable','druggable'),('compounds','compounds'),
      ('exposure','exposure hit'),('evidence_types','evidence types')]
table=candidate_table(rows, cols,
    search_keys=['symbol','evidence_types'],
    numeric_keys=['score','streams','curated','pigean','variants','compounds','n_sources'],
    page_size=25, default_sort=('score','desc'),
    extra_filters=[('tier','Confidence tier'),('druggable','Druggable target'),
                   ('genetic','Genetic association'),('diffexpr','Differential activity'),('exposure','Exposure hit')],
    sources_col=('n_sources','sources'))
kpis=kpis_from_stats(S,[
 ('kg_queried','Knowledge graphs queried',''),
 ('genes_universe','Genes with disease evidence',''),
 ('genes_core','Corroborated ≥2 streams',''),
 ('tier_a','Tier A consensus genes',''),
 ('go_sig','GO terms FDR<0.05',''),
 ('rx_sig','Reactome pathways FDR<0.05',''),
 ('drugs_rdkg','Approved T2D drugs',''),
 ('counties','US counties mapped',''),
 ('model_r2','County model R²',''),
])
build_report_from_markdown('T2D_OKN_report.md','T2D_OKN_report.html',kpis=kpis,table=table,stats=S,
   footer='OKN federated SPARQL via mcp-okn · hypothesis generation, not causal or clinical inference.')

# splice the interactive OpenStreetMap choropleth in as chrome (not prose) at the marker
iframe=open('data/county_map_iframe.html').read()
html=open('T2D_OKN_report.html').read()
n=0
for marker in ('<!-- INTERACTIVE_MAP -->','&lt;!-- INTERACTIVE_MAP --&gt;','<p><!-- INTERACTIVE_MAP --></p>'):
    if marker in html:
        html=html.replace(marker,'<div class="mapwrap">'+iframe+'</div>'); n+=1; break
open('T2D_OKN_report.html','w').write(html)
print('map spliced:',n)

# fill {{key}} placeholders in the DELIVERED markdown (read first, then write)
md=open('T2D_OKN_report.md').read()
open('T2D_OKN_report.md','w').write(fill_stats(md,S))
from build_report_html import check_report_parity
print(check_report_parity('T2D_OKN_report.md','T2D_OKN_report.html'))
print('done')

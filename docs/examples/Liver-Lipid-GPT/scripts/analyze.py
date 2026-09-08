from pathlib import Path
import json, sys
import pandas as pd
import numpy as np
from enrichment import enrich
from collapse_orthologs import collapse

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'
def read(name):
    j=json.loads((D/(name+'.json')).read_text()); return pd.DataFrame(j['data'],columns=j['columns'])
def save(df,name): df.to_csv(D/(name+'.tsv'),sep='\t',index=False)
ort=read('orthologs')
bridge=pd.concat([read('functional_bridge'),read('functional_hgnc')]).drop_duplicates()
go=read('go_annotations'); react=read('reactome')
maps=[]
for name,prefix in [('map_ensembl','https://www.ensembl.org/id/'),('map_hgnc','http://identifiers.org/hgnc/')]:
    z=read(name);z['g2']=prefix+z['key'].astype(str);z['human']='http://www.ncbi.nlm.nih.gov/gene/'+z.entrez.astype(str);maps.append(z[['g2','human']])
mapping=pd.concat(maps).drop_duplicates()
go=go.merge(mapping,on='g2');react=react.merge(mapping,on='g2')
rd=read('disease_sets'); rd['human']=rd.gene.str.replace('http://identifiers.org/ncbigene/','http://www.ncbi.nlm.nih.gov/gene/',regex=False)
traits=read('trait_sets'); tbg=read('trait_bg')
human=[]; summary=[]; mouse=[]
for i in [25,47,137]:
    d=read('de'+str(i)).drop_duplicates('gene');d['study']='OSD-'+str(i)
    d['strict']=(d.p<=.05)&(d.lfc.abs()>=1)
    d['sensitivity']=(d.p<=.05)&(d.lfc.abs()>=np.log2(1.2))
    mouse.append(d)
    h=d.merge(ort,on='gene').rename(columns={'human':'hEntrez','lfc':'log2fc','p':'adj_p_value'})
    c=collapse(h.reset_index(drop=True));c['study']='OSD-'+str(i)
    c['strict']=(c.adj_p_value<=.05)&(c.log2fc.abs()>=1)
    c['sensitivity']=(c.adj_p_value<=.05)&(c.log2fc.abs()>=np.log2(1.2))
    c['unique_mapping']=c.n_mouse_map.eq(1)&~c.hEntrez.isin(set(ort[ort.gene.isin(ort.groupby('gene').human.nunique().loc[lambda s:s>1].index)].human))
    human.append(c)
    summary.append(dict(study='OSD-'+str(i),retained=len(d),fdr05=int((d.p<=.05).sum()),strict=int(d.strict.sum()),up=int((d.strict&(d.lfc>0)).sum()),down=int((d.strict&(d.lfc<0)).sum()),sensitivity=int(d.sensitivity.sum()),mapped_mouse=int(h.gene.nunique()),human_retained=len(c),human_strict=int(c.strict.sum()),ambiguous=int((c.n_mouse_map>1).sum()),sign_flips=int(c.sign_flip.sum())))
mouse=pd.concat(mouse);human=pd.concat(human);summary=pd.DataFrame(summary)
save(mouse,'mouse_results');save(human,'human_results');save(summary,'assay_summary')
all_enr=[]
families={
 'GO BP':(go,'human','term','label'),
 'Reactome':(react,'human','term','label'),
 'RDKG curated genetic':(rd[rd.relation.str.endswith('genetic_association')],'human','disease','label'),
 'DIG lipid traits':(traits,'gene','trait','label')}
for family,(ann,gene,cat,label) in families.items():
    sets=ann.groupby(cat)[gene].agg(set).to_dict();labels=ann.drop_duplicates(cat).set_index(cat)[label].to_dict()
    bg=set(tbg.gene) if family=='DIG lipid traits' else set(ann[gene])
    for study,h in human.groupby('study'):
        for rule in ['strict','sensitivity']:
            for direction in ['all','up','down']:
                hs=h[h[rule]].copy()
                if direction!='all':hs=hs[hs.log2fc.gt(0) if direction=='up' else hs.log2fc.lt(0)]
                sig=set(bridge[bridge.human.isin(hs.hEntrez)].g2) if gene=='g2' else set(hs.hEntrez)
                # Include zero-overlap categories in BH; do not filter on observed hits.
                if not (sig&bg): continue
                e=enrich(sig,sets,bg,kmin=0,Kmin=1)
                e['label']=e.category.map(labels);e['family']=family;e['study']=study;e['rule']=rule;e['direction']=direction;e['background']='all annotated'
                all_enr.append(e)
                retained=set(bridge[bridge.human.isin(h.hEntrez)].g2) if gene=='g2' else set(h.hEntrez)
                cbg=bg&retained
                if sig&cbg:
                    e=enrich(sig,sets,cbg,kmin=0,Kmin=1)
                    e['label']=e.category.map(labels);e['family']=family;e['study']=study;e['rule']=rule;e['direction']=direction;e['background']='retained conditional'
                    all_enr.append(e)
enr=pd.concat(all_enr,ignore_index=True);save(enr,'enrichment')
keys=['study','family','rule','direction','background']
idx=pd.MultiIndex.from_product([['OSD-25','OSD-47','OSD-137'],list(families),['strict','sensitivity'],['all','up','down'],['all annotated','retained conditional']],names=keys)
status=enr.groupby(keys).agg(tests=('category','count'),n=('n','first'),N=('N','first'),significant=('fdr',lambda a:int((a<.05).sum()))).reindex(idx).reset_index()
status['status']=status.tests.apply(lambda a:'skipped: no mapped foreground' if pd.isna(a) else 'run')
save(status,'analysis_status')
anns=go[['g2','term','label']].copy();anns['family']='GO BP'
ra=react[['g2','term','label']].copy();ra['family']='Reactome';anns=pd.concat([anns,ra])
lipid=anns[anns.label.str.contains('lipid|fatty acid|cholesterol|triglyceride|lipoprotein|circadian',case=False,na=False)]
links=bridge.merge(lipid,on='g2').drop_duplicates(['human','term'])
save(links,'lipid_annotations')
rows=[]
for _,h in human[human.strict].iterrows():
    f=bridge[bridge.human==h.hEntrez];l=links[links.human==h.hEntrez]
    d=rd[rd.human==h.hEntrez];t=traits[traits.gene==h.hEntrez]
    sources=['spoke-genelab']+(['prokn'] if len(f) else [])+(['rdkg'] if len(d) else [])+(['digcfdekg'] if len(t) else [])
    tier='B' if len(l) and not h.sign_flip and h.unique_mapping else 'C'
    rows.append(dict(study=h.study,mouse_genes=h.mouse_symbols,human_entrez=h.hEntrez.rsplit('/',1)[-1],log2fc=h.log2fc,adj_p=h.adj_p_value,direction='up' if h.log2fc>0 else 'down',tier=tier,score=10*bool(len(l))+len(sources)+min(abs(h.log2fc),5)/10,lipid_terms='; '.join(sorted(set(l.label))),diseases='; '.join(sorted(set(d.label.dropna()))),traits='; '.join(sorted(set(t.label.dropna()))),sources_n=len(sources),sources=sources,ambiguity='one-to-one' if h.unique_mapping else 'ambiguous'))
ranked=pd.DataFrame(rows).sort_values(['score','adj_p'],ascending=[False,True]);ranked['rank']=range(1,len(ranked)+1)
save(ranked,'ranked_results');(D/'ranked_results.json').write_text(ranked.to_json(orient='records',indent=2))
stats={'assays':len(summary),'retained_total':int(summary.retained.sum()),'strict_total':int(summary.strict.sum()),'human_rows':len(ranked),'tier_b':int((ranked.tier=='B').sum()),'tier_c':int((ranked.tier=='C').sum()),'tier_a':0,'go_genes':go.human.nunique(),'go_terms':go.term.nunique(),'reactome_genes':react.human.nunique(),'reactome_terms':react.term.nunique(),'trait_genes':tbg.gene.nunique(),'trait_sets':traits.trait.nunique(),'curated_genes':rd[rd.relation.str.endswith('genetic_association')].human.nunique()}
for row in summary.to_dict('records'):
    i=row.pop('study').split('-')[1]
    for k,v in row.items():stats[k+i]=v
(D/'stats.json').write_text(json.dumps(stats,indent=2))
print(summary.to_string(index=False));print('\nTOP ENRICHMENT')
e=enr[(enr.rule=='strict')&(enr.direction=='all')&(enr.background=='all annotated')]
print(e[e.fdr<.05].groupby(['study','family']).size().to_string())
print(e[(e.fdr<.05)&e.label.str.contains('lipid|fatty|cholesterol|triglyceride',case=False,na=False)][['study','family','label','k','K','n','N','fold','fdr']].to_string(index=False))
print('\nTOP CANDIDATES');print(ranked[['study','mouse_genes','log2fc','tier','sources_n']].head(15).to_string(index=False))
print('\nTRAITS');print(e[e.family=='DIG lipid traits'][['study','label','k','K','n','N','fold','fdr']].to_string(index=False))

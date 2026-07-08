import pandas as pd, base64, json
D="data"; F="figures"; OUT="/sessions/affectionate-jolly-ramanujan/mnt/bone-health/bone_health_spaceflight_report.html"
def b64(p): return "data:image/png;base64,"+base64.b64encode(open(p,'rb').read()).decode()
figs={k:b64(f"{F}/{v}") for k,v in {'f1':'bone_fig1_cohort.png','f2':'bone_fig2_nrf2.png','f3':'bone_fig3_bonerelevance.png','f4':'bone_fig6_top_matrix.png','f5':'bone_fig4_go_enrichment.png','f6':'bone_fig5_reactome.png'}.items()}
c=pd.read_csv(f"{D}/RANKED_bone_candidates.tsv",sep="\t")
c=c.rename(columns={'humanSymbol':'gene','symbol':'mouse','l2fc_WT':'WT','l2fc_KO':'KO','n_arms':'arms',
  'nrf2_dependent':'Nrf2dep','bone_role':'role','rdkg_pheno':'HPO','digcfde_bonecat':'GWAS'})
def cl(v): return "" if pd.isna(v) or str(v)=='nan' else v
def srcs(r):
    s=['spoke-genelab']
    if cl(r.HPO): s.append('rdkg')
    if cl(r.GWAS): s.append('digcfdekg')
    if str(r.osteoarthritis).lower() in ('true','1'): s.append('spoke-okn')
    return s
rows=[]
for _,r in c.iterrows():
    S=srcs(r)
    rows.append({'gene':cl(r.gene),'mouse':cl(r.mouse),'dir':cl(r.direction),
     'WT':(round(r.WT,2) if pd.notna(r.WT) else ''),'KO':(round(r.KO,2) if pd.notna(r.KO) else ''),
     'arms':int(r.arms),'Nrf2dep':'yes' if r.Nrf2dep else '','role':cl(r.role),'HPO':cl(r.HPO),'GWAS':cl(r.GWAS),
     'sources':S,'nsrc':len(S),'spec':cl(r.specificity),'score':round(r.priority,1),'tier':cl(r.tier)})
J=json.dumps(rows)
S=[("spoke-genelab","v0.0.2","PRIMARY: mouse bone-marrow DE + mouse to human ortholog","source"),
   ("digcfdekg","v0.0.1","Gene to trait: BMD / osteoporosis / fracture (PIGEAN/EAGGL)","Entrez direct (19,747)"),
   ("rdkg","v0.0.1","HPO bone phenotype to gene; curated drug->bone-disease (treats)","Entrez direct (9,034)"),
   ("spoke-okn","v0.0.6","Disease-gene, compound-gene, drug-disease","Entrez direct (16,326)"),
   ("biobricks-aopwiki","v0.0.4","Adverse Outcome Pathways","Entrez exactMatch (sparse)"),
   ("prokn","v0.0.5","GO + Reactome pathway enrichment (Gene->Protein->GO/Reactome)","Entrez->HGNC symbol bridge (bridged, lower-conf)")]
SRC="".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c2}</td><td>{d}</td></tr>" for a,b,c2,d in S)

TPL=open('/dev/stdin').read() if False else None
cmdf=pd.read_csv('data/countermeasures.tsv',sep='\t')
cm_rows="".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r.countermeasure,r.target_axis,r.supporting_signature_genes,r.supporting_GO_pathway,r.example_agents,r.confidence) for _,r in cmdf.iterrows())
CM='<div style="overflow-x:auto"><table><thead><tr><th>Countermeasure</th><th>Target axis</th><th>Supporting signature genes</th><th>Supporting GO / pathway</th><th>Example agents</th><th>Confidence</th></tr></thead><tbody>'+cm_rows+'</tbody></table></div>'
dg=pd.read_csv('data/retrieved_drugs.tsv',sep='\t')
dg_rows="".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r.drug_class,r.example_agents_retrieved,r.treats_bone_disease_rdkg,r.linked_signature_genes_axis) for _,r in dg.iterrows())
DRUGS='<div style="overflow-x:auto"><table><thead><tr><th>Drug class</th><th>Example agents (retrieved, rdkg)</th><th>Treats (rdkg bone disease)</th><th>Linked signature genes / axis</th></tr></thead><tbody>'+dg_rows+'</tbody></table></div>'
tpl=open('tpl.html').read()
tpl=tpl.replace('__CM__',CM).replace('__DRUGS__',DRUGS).replace('__F5__',figs['f5']).replace('__F6__',figs['f6']).replace('__SRC__',SRC).replace('__F1__',figs['f1']).replace('__F2__',figs['f2']).replace('__F3__',figs['f3']).replace('__F4__',figs['f4']).replace('__J__',J)
open(OUT,'w').write(tpl)
print("saved",OUT,"|",len(tpl),"bytes | candidates:",len(rows))

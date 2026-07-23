import pandas as pd, sys
sys.path.insert(0,'.')
from mechanistic_map import render_mechanistic_map
r=pd.read_csv('data/consensus_ranking.csv').set_index('humanSymbol')
def pick(genes,n=6):
    g=[x for x in genes if x in r.index]
    g=sorted(g,key=lambda x:-r.loc[x,'evidence_score'])[:n]
    return g
modules={
 'Osteoblast / mineralisation\n(GO ossification · Reactome RUNX2)':pick(['RUNX2','SP7','ALPL','COL1A1','IBSP','BGLAP','DMP1','MEPE','SPP1','MMP14','SLC34A1','MSX2','SMAD3','SOX9','SOX4','BMP7','BMPR1B']),
 'ECM organisation &\ncollagen chaperoning':pick(['SERPINH1','ADAMTS2','ADAMTSL2','P4HA1','POSTN','THBS1','MMP2','MMP13','COL3A1','LTBP2','CTHRC1','SMOC1']),
 'Osteoclast / resorption\n(NFAT + AP-1 regulons)':pick(['CTSK','ACP5','ATP6V0D2','MMP9','FOS','FOSB','JUNB','IL1B','TNF','S100A8','S100A9','CCL2']),
 'Wnt / TCF-LEF\n(LEF1 · TCF4 regulons)':pick(['WNT16','WNT4','RSPO3','AMER1','FZD7','FZD4','FZD9','DKK2','WIF1','GREM2','MYC','CCND1']),
 'MSC lineage switch to\nadipogenesis (MLL3/4-PPARG)':pick(['PPARG','CEBPD','CEBPA','ADIPOQ','PLIN1','LEP','CIDEA','CIDEC','LGALS12','RETN']),
 'Mechanotransduction &\ncytoskeleton (MEF2 · SRF)':pick(['CCN1','CCN5','LMNA','ITGA5','ANKRD1','CSRP3','MYOD1','TRIM63','FBXO32','MSTN','SYNM']),
 'PTH / oestrogen /\ncalcium–phosphate':pick(['PTH1R','PTHLH','SLC34A1','CYP19A1','ESR2','TRPM6','SLC20A1']),
 'Oxidative stress &\nmitochondrial (metallothioneins)':pick(['MT2A','MT1X','MT1A','MT1E','NQO1','SRXN1','PPARGC1A','UCP3','IDH1','SESN1']),
 'Circadian clock':pick(['DBP','PER2','CIART','NPAS2','PER3','ARNTL','NR1D1','NFIL3','NOCT']),
 'Glucocorticoid / heat-shock\n(HSP90-SHR cycle)':pick(['FKBP5','HSPA1A','HSPA1B','HSP90AA1','CDKN1A','DDIT4','DDIT3','TRIB3']),
}
drugs={
 'Osteoblast / mineralisation\n(GO ossification · Reactome RUNX2)':['Teriparatide','Romosozumab','Asfotase alfa'],
 'ECM organisation &\ncollagen chaperoning':['Fresolimumab'],
 'Osteoclast / resorption\n(NFAT + AP-1 regulons)':['Alendronate','Zoledronic acid','Denosumab','Salmon calcitonin'],
 'Wnt / TCF-LEF\n(LEF1 · TCF4 regulons)':['Romosozumab','BPS804'],
 'MSC lineage switch to\nadipogenesis (MLL3/4-PPARG)':['Rosiglitazone*'],
 'PTH / oestrogen /\ncalcium–phosphate':['Teriparatide','Raloxifene','Cholecalciferol','Eldecalcitol','KRN23'],
 'Glucocorticoid / heat-shock\n(HSP90-SHR cycle)':['Prednisone*','Dexamethasone*'],
}
render_mechanistic_map(
 anchor='Spaceflight-induced\nbone loss',
 modules=modules, drugs=drugs,
 out_path='fig/fig7_mechanistic_map.png',
 title='Spaceflight bone-loss mechanistic map — modules, genes and agents retrieved from the OKN federation',
 subtitle='genes: spoke-genelab spaceflight DE (mouse/rat -> human ortholog), Tier A/B core; modules: significant GO / Reactome / MSigDB-regulon themes (FDR <= 0.05)',
 footnote='Drugs: rdkg DrugBank disease-level treats/contraindicated_for edges, assigned to a module by documented mechanism of action (analyst assignment, NOT a KG gene-drug edge).  * = contraindicated / bone-adverse agent.',
)
print('fig7 done')

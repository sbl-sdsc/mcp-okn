import pandas as pd, numpy as np, json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
D="data"; F="figures"
labels={"GO:0002181":"cytoplasmic translation","GO:1901740":"negative regulation of myoblast fusion","GO:0006412":"translation","GO:0006941":"striated muscle contraction","GO:0160165":"CD8+ alpha-beta T cell homeostasis","GO:0071357":"cellular response to type I interferon","GO:0042776":"mitochondrial ATP synthesis (PMF)","GO:0045063":"T-helper 1 cell differentiation","GO:0045061":"thymic T cell selection","GO:0043374":"CD8+ alpha-beta T cell differentiation","GO:0010499":"proteasomal ubiquitin-independent catabolism","GO:0072539":"T-helper 17 cell differentiation","GO:0045590":"neg. reg. regulatory T cell differentiation","GO:0043161":"proteasome ubiquitin-dependent catabolism","GO:0009060":"aerobic respiration","GO:0042274":"ribosomal small subunit biogenesis","GO:0022904":"respiratory electron transport chain","GO:0061136":"reg. of proteasomal protein catabolism","GO:2000045":"reg. of G1/S transition (mitotic)","GO:0006779":"porphyrin biosynthesis","GO:0006785":"heme B biosynthesis","GO:1902600":"proton transmembrane transport","GO:0032743":"positive reg. of interleukin-2 production","GO:0007283":"spermatogenesis","GO:0051321":"meiotic cell cycle","GO:1901798":"pos. reg. p53-mediated signal transduction","GO:0006979":"response to oxidative stress","GO:0006915":"apoptotic process","GO:0006511":"ubiquitin-dependent protein catabolism","GO:0010498":"proteasomal protein catabolism","GO:0070585":"protein localization to mitochondrion","GO:0006119":"oxidative phosphorylation","GO:0015986":"proton motive force-driven ATP synthesis","GO:0006120":"mito electron transport NADH->ubiquinone","GO:0006782":"protoporphyrinogen IX biosynthesis","GO:0015670":"carbon dioxide transport","GO:0008286":"insulin receptor signaling","GO:0044597":"daunorubicin metabolic process","GO:0006784":"heme A biosynthesis","GO:0044598":"doxorubicin metabolic process","GO:0032729":"pos. reg. type II interferon production","GO:0034314":"Arp2/3 actin nucleation","GO:0000278":"mitotic cell cycle","GO:0032760":"pos. reg. TNF production","GO:0034341":"response to type II interferon","GO:0008654":"phospholipid biosynthesis","GO:0038094":"Fc-gamma receptor signaling","GO:0006783":"heme biosynthesis","GO:0002715":"reg. NK cell mediated immunity","GO:0002477":"antigen presentation via MHC class Ib","GO:0010591":"reg. of lamellipodium assembly","GO:0044839":"cell cycle G2/M transition","GO:0071395":"cellular response to jasmonic acid","GO:0098901":"reg. cardiac muscle action potential","GO:0007051":"spindle organization","GO:0051301":"cell division","GO:0045333":"cellular respiration","GO:0051604":"protein maturation","GO:0030317":"flagellated sperm motility","GO:0006099":"tricarboxylic acid (TCA) cycle","GO:1901796":"reg. p53-mediated signal transduction","GO:0098869":"cellular oxidant detoxification","GO:0031146":"SCF ubiquitin-dependent catabolism","GO:0000070":"mitotic sister chromatid segregation","GO:0007059":"chromosome segregation","GO:0051988":"reg. spindle attachment to kinetochore","GO:1901750":"leukotriene D4 biosynthesis","GO:0006123":"mito electron transport cyt c->O2","GO:0031204":"post-translational protein targeting"}
df=pd.read_csv(f"{D}/prokn_go_enrichment.tsv",sep="\t")
df['label']=df.go.map(labels).fillna(df.go)
def theme(l):
    t=l.lower()
    if 'translation' in t or 'ribosom' in t: return 'Translation & ribosome'
    if any(k in t for k in ['oxidative phosphor','electron transport','respiration','atp synth','tricarboxylic','proton','mitochond','carbon dioxide']): return 'Mitochondrial OXPHOS & respiration'
    if 'oxidative stress' in t or 'oxidant detox' in t: return 'Oxidative-stress response (Nrf2)'
    if any(k in t for k in ['ubiquitin','proteasom','protein catabol','protein maturation','p53']): return 'Proteostasis (ubiquitin-proteasome)'
    if any(k in t for k in ['interferon','interleukin','tnf','t cell','nk cell','immun','antigen','fc-gamma','helper','regulatory t','leukotriene']): return 'Immune / inflammatory'
    if any(k in t for k in ['mitotic','cell cycle','chromosome','spindle','cell division','g1/s','g2/m','kinetochore','sister chromatid']): return 'Cell cycle & division'
    if 'heme' in t or 'porphyrin' in t: return 'Heme / erythroid'
    if any(k in t for k in ['muscle','myoblast','cardiac']): return 'Muscle (minor)'
    if any(k in t for k in ['insulin','phospholipid','lamellipod','actin','apopto']): return 'Metabolic / signaling'
    return 'Other'
df['theme']=df.label.apply(theme)
sig=df[df.fdr<0.05].copy().sort_values('p')
sig.to_csv(f"{D}/prokn_go_enrichment_labeled.tsv",sep="\t",index=False)
print("themes among 69 significant:")
print(sig.theme.value_counts().to_string())
# save theme summary for report
summ=sig.groupby('theme').agg(nterms=('go','size'),top=('label','first'),maxfold=('fold','max')).sort_values('nterms',ascending=False)
summ.to_csv(f"{D}/go_theme_summary.tsv",sep="\t")
print(); print(summ.to_string())

# FIGURE 5: top enriched GO terms grouped by theme
top=sig.sort_values('fold',ascending=False).drop_duplicates('label').head(20).sort_values('fold')
themecol={'Translation & ribosome':'#8e44ad','Mitochondrial OXPHOS & respiration':'#2980b9','Oxidative-stress response (Nrf2)':'#c0392b','Proteostasis (ubiquitin-proteasome)':'#16a085','Immune / inflammatory':'#e67e22','Cell cycle & division':'#7f8c8d','Heme / erythroid':'#c39bd3','Muscle (minor)':'#bdc3c7','Metabolic / signaling':'#27ae60','Other':'#95a5a6'}
fig,ax=plt.subplots(figsize=(11,7))
y=np.arange(len(top))
ax.barh(y,top.fold,color=[themecol.get(t,'#999') for t in top.theme])
ax.set_yticks(y); ax.set_yticklabels([f"{l}  ({t.split()[0]})" for l,t in zip(top.label,top.theme)],fontsize=8.5)
for i,(f,k,K) in enumerate(zip(top.fold,top.k,top.K)):
    ax.text(f+0.05,i,f"{f:.1f}x  ({int(k)}/{int(K)})",va='center',fontsize=7.8,color='#333')
ax.set_xlabel("fold enrichment (observed / expected)"); ax.set_xlim(0,top.fold.max()*1.22)
ax.set_title("Figure 5. GO biological-process enrichment of the flight bone-marrow signature\n(prokn, Entrez->HGNC-bridged; all terms FDR<0.05)",fontweight='bold',fontsize=11,loc='left')
import matplotlib.patches as mp
seen=[t for t in themecol if t in set(top.theme)]
ax.legend([mp.Patch(color=themecol[t]) for t in seen],seen,fontsize=7.6,loc='lower right',frameon=False)
plt.tight_layout(); plt.savefig(f"{F}/bone_fig5_go_enrichment.png",dpi=150,bbox_inches='tight'); plt.close()
print("\nfig5 saved")

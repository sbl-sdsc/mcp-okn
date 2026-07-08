import json, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
D="data"; F="figures"
st=json.load(open(f"{D}/stats.json"))
BONE="#c0392b"; UP="#c0392b"; DOWN="#2471a3"; NEU="#7f8c8d"; ACC="#8e44ad"; GRN="#27ae60"; KO="#7b241c"

# ================= FIG 1: cohort & design =================
fig=plt.figure(figsize=(12.4,5.4)); gs=fig.add_gridspec(1,2,width_ratios=[1.28,1],wspace=0.26)
ax=fig.add_subplot(gs[0,0]); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,10)
ax.set_title("A   Bone-health spaceflight cohort (spoke-genelab, mouse RNA-Seq)",loc='left',fontweight='bold',fontsize=11)
def box(x,y,w,h,t,c,fs=9,tc='white'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08,rounding_size=0.12",fc=c,ec='none'))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',color=tc,fontsize=fs,fontweight='bold')
box(0.2,8.4,9.6,1.1,"NASA OSDR / GeneLab  —  spaceflight omics (all mouse, transcriptomic)","#34495e",10)
box(0.3,5.8,4.5,2.0,"SPACEFLIGHT  (in-orbit)\nOSD-690 bone marrow\nSpace Flight vs Ground Control",BONE,9)
box(0.5,4.75,2.0,0.85,"Wild-Type\n3,161 DEG\n3,112 orthologs","#a93226",8)
box(2.7,4.75,2.0,0.85,"Nrf2-KO\n3,517 DEG\n3,537 orthologs",KO,8)
box(5.1,5.8,4.6,2.0,"GROUND UNLOADING (disuse analog)\nHindlimb Unloaded vs Loaded",DOWN,9)
box(5.3,4.75,2.1,0.85,"OSD-467 cortical bone\n8 DE genes (sparse)","#1f618d",8)
box(7.55,4.75,2.0,0.85,"OSD-214 marrow\n~0 (artefact)","#5d6d7e",8)
box(0.3,3.05,9.4,0.85,"mouse to human orthologs (IS_ORTHOLOG_MGiG)  ->  human-ortholog signature","#16a085",9)
box(0.3,1.35,9.4,1.15,"Federation on Entrez gene:  spoke-okn (disease/drug) . rdkg (HPO bone phenotypes)\ndigcfdekg (BMD / osteoporosis / fracture traits) . aopwiki . prokn","#8e44ad",8.5)
ax.annotate("",xy=(5,3.9),xytext=(5,4.7),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.6))
ax.annotate("",xy=(5,2.5),xytext=(5,3.05),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.6))
ax.text(0.25,0.55,"Mouse-derived, ortholog-inferred - hypothesis generation, not clinical inference",fontsize=8.5,style='italic',color=BONE)
ax2=fig.add_subplot(gs[0,1])
labels=["OSD-690\nmarrow WT","OSD-690\nmarrow Nrf2-KO","OSD-467\ncortical HLU","OSD-214\nmarrow HLU"]
vals=[3161,3517,8,2]; cols=[BONE,KO,DOWN,NEU]
ax2.bar(range(4),vals,color=cols); ax2.set_yscale('log'); ax2.set_ylim(1,9000)
ax2.set_xticks(range(4)); ax2.set_xticklabels(labels,fontsize=8)
for i,v in enumerate(vals): ax2.text(i,v*1.18,f"{v:,}",ha='center',fontsize=9,fontweight='bold')
ax2.set_ylabel("significant DE genes (adj p <= 0.05)")
ax2.set_title("B   Signal asymmetry",loc='left',fontweight='bold',fontsize=11)
ax2.text(0.03,0.03,"Only in-flight bone tissue = marrow;\nonly mineralized-bone data = 8-gene\nground HLU study.",transform=ax2.transAxes,fontsize=8,style='italic',color='#555')
plt.savefig(f"{F}/bone_fig1_cohort.png",dpi=150,bbox_inches='tight'); plt.close()

# ================= FIG 2: WT vs Nrf2-KO =================
m=pd.read_csv(f"{D}/wt_ko_human_merged.tsv",sep="\t")
both=m[m.log2fc_wt.notna()&m.log2fc_ko.notna()].copy()
fig,(axA,axB)=plt.subplots(1,2,figsize=(12.4,5.2),gridspec_kw={'width_ratios':[1.15,1]})
same=np.sign(both.log2fc_wt)==np.sign(both.log2fc_ko)
axA.axhline(0,color='#ccc',lw=.8); axA.axvline(0,color='#ccc',lw=.8)
axA.plot([-6,6],[-6,6],'--',color='#bbb',lw=1)
axA.scatter(both.log2fc_wt[same],both.log2fc_ko[same],s=8,c=GRN,alpha=.45,label=f"same direction ({int(same.sum())})")
axA.scatter(both.log2fc_wt[~same],both.log2fc_ko[~same],s=12,c=BONE,alpha=.7,label=f"opposite ({int((~same).sum())})")
axA.set_xlim(-4,4); axA.set_ylim(-4,4)
axA.set_xlabel("log2FC  Wild-Type (Space Flight vs Ground)"); axA.set_ylabel("log2FC  Nrf2-KO")
axA.set_title("A   Robust core: 1,754 genes significant in both\ngenotype arms, 98.4% same direction",loc='left',fontweight='bold',fontsize=11)
axA.legend(loc='lower right',fontsize=8,frameon=False)
# B: Nrf2-dependent bone-remodeling genes (KO-only)
genes=['MMP9','NFATC1','LRP5','CSF1','COL1A1','LRP4']; kv=[-0.672,-0.598,-0.511,-0.379,-1.347,-0.331]
roles=['osteoclast MMP','osteoclast TF','Wnt co-receptor','osteoclast M-CSF','type I collagen','Wnt/sclerostin']
y=np.arange(len(genes))[::-1]
axB.barh(y,kv,color=KO,alpha=.9)
axB.axvline(0,color='#333',lw=.8)
for i,(g,v,r) in enumerate(zip(genes,kv,roles)):
    axB.text(0.05,y[i],f"  {g}",va='center',ha='left',fontsize=9,fontweight='bold',color='white' if v< -0.5 else '#333')
    axB.text(v-0.03,y[i],r,va='center',ha='right',fontsize=7.5,color='#444')
axB.set_yticks([]); axB.set_xlim(-1.6,0.5); axB.set_xlabel("log2FC in Nrf2-KO flight marrow")
axB.set_title("B   Nrf2-dependent bone-remodeling suppression\n(significant only when Nrf2 is knocked out)",loc='left',fontweight='bold',fontsize=11)
plt.tight_layout(); plt.savefig(f"{F}/bone_fig2_nrf2.png",dpi=150,bbox_inches='tight'); plt.close()

# ================= FIG 3: bone relevance =================
fig=plt.figure(figsize=(12.4,4.6)); gs=fig.add_gridspec(1,3,width_ratios=[1,0.8,1.25],wspace=0.42)
# A enrichment
axa=fig.add_subplot(gs[0,0])
x=np.arange(2); axa.bar(x-0.19,[476.5,20.6],0.36,label='expected',color='#bdc3c7')
axa.bar(x+0.19,[492,31],0.36,label='observed',color=BONE)
axa.set_xticks(x); axa.set_xticklabels(["digcfde GWAS\n(3,424 genes)","rdkg Mendelian\n(148 genes)"],fontsize=8.5)
axa.set_ylabel("signature genes in bone set")
for xi,(e,o,f,p) in zip(x,[(476.5,492,1.03,'0.21'),(20.6,31,1.51,'0.012')]):
    axa.text(xi,o+ (18 if xi==0 else 2),f"{f}x\np={p}",ha='center',fontsize=8.5,fontweight='bold',color=BONE)
axa.legend(fontsize=8,frameon=False,loc='upper right'); axa.set_title("A   Bone-loss over-representation",loc='left',fontweight='bold',fontsize=10.5)
# B specificity donut
axb=fig.add_subplot(gs[0,1])
sp=st['specificity']; vals=[sp.get('systemic',0),sp.get('intermediate',0),sp.get('marrow-selective',0)]
axb.pie(vals,colors=['#5d6d7e','#e67e22',BONE],startangle=90,wedgeprops=dict(width=0.42,edgecolor='w'),
        autopct=lambda p:f"{int(round(p*sum(vals)/100))}",pctdistance=0.78,textprops={'fontsize':8,'color':'white','fontweight':'bold'})
axb.text(0,0,"tissue\nspecificity",ha='center',va='center',fontsize=8.5,fontweight='bold')
axb.legend(['systemic','intermediate','marrow-selective'],fontsize=7.5,loc='lower center',bbox_to_anchor=(0.5,-0.22),frameon=False)
axb.set_title("B   Mostly systemic\nspaceflight stress",loc='left',fontweight='bold',fontsize=10.5)
# C canonical bone panel heatmap
axc=fig.add_subplot(gs[0,2])
panel=[('ALPL',-1.086,-1.142,'osteoblast/mineral.'),('IBSP',-0.811,-0.649,'bone matrix'),
 ('FAM20A',-2.014,np.nan,'mineralization kinase'),('COL1A1',np.nan,-1.347,'type I collagen'),
 ('LRP5',np.nan,-0.511,'Wnt/bone mass'),('NFATC1',np.nan,-0.598,'osteoclast TF'),
 ('MMP9',np.nan,-0.672,'osteoclast MMP'),('CSF1',np.nan,-0.379,'M-CSF'),
 ('CA2',-0.419,-0.402,'osteoclast CA'),('CXCL2',1.901,1.992,'inflammation')]
mat=np.array([[p[1],p[2]] for p in panel],dtype=float)
im=axc.imshow(mat,cmap='RdBu_r',vmin=-2,vmax=2,aspect='auto')
axc.set_xticks([0,1]); axc.set_xticklabels(['WT','Nrf2-KO'],fontsize=9)
axc.set_yticks(range(len(panel))); axc.set_yticklabels([f"{p[0]}" for p in panel],fontsize=8.5)
for i,p in enumerate(panel):
    for j,v in enumerate([p[1],p[2]]):
        if not np.isnan(v): axc.text(j,i,f"{v:+.2f}",ha='center',va='center',fontsize=7.5,color='white' if abs(v)>1 else '#222')
        else: axc.text(j,i,"ns",ha='center',va='center',fontsize=7,color='#999')
    axc.text(2.05,i,p[3],va='center',fontsize=7,color='#444')
axc.set_xlim(-0.5,3.4)
axc.set_title("C   Canonical bone-remodeling genes (log2FC)\nformation/matrix down, inflammation up",loc='left',fontweight='bold',fontsize=10.5)
plt.savefig(f"{F}/bone_fig3_bonerelevance.png",dpi=150,bbox_inches='tight'); plt.close()

# ================= FIG 4: top-candidate evidence matrix =================
c=pd.read_csv(f"{D}/RANKED_bone_candidates.tsv",sep="\t")
top=c.head(20).copy()
ev_cols=['both\narms','Nrf2\ndep','canonical','Mendelian\nbone','GWAS\nBMD/frac','down\n(bone loss)']
def row_ev(r):
    return [1 if r.n_arms==2 else 0,
            1 if r.nrf2_dependent else 0,
            1 if pd.notna(r.bone_role) else 0,
            1 if r.bone_evidence=='mendelian' else 0,
            1 if r.bone_evidence in ('gwas_strong','gwas_bmd') else 0,
            1 if r.direction=='↓' else 0]
M=np.array([row_ev(r) for _,r in top.iterrows()],dtype=float)
fig,ax=plt.subplots(figsize=(8.8,7.6))
ax.imshow(M,cmap='Greens',vmin=0,vmax=1.6,aspect='auto')
ax.set_xticks(range(len(ev_cols))); ax.set_xticklabels(ev_cols,fontsize=8.5)
tierlab=[f"{r.humanSymbol}  ({r.tier})" for _,r in top.iterrows()]
ax.set_yticks(range(len(top))); ax.set_yticklabels(tierlab,fontsize=8.5)
for i in range(len(top)):
    for j in range(len(ev_cols)):
        if M[i,j]: ax.text(j,i,"+",ha='center',va='center',fontsize=11,fontweight='bold',color='#145a32')
ax.set_title("Top 20 ranked bone candidates — evidence matrix\n(mouse-derived, ortholog-inferred)",fontweight='bold',fontsize=11,loc='left')
plt.tight_layout(); plt.savefig(f"{F}/bone_fig4_top_matrix.png",dpi=150,bbox_inches='tight'); plt.close()
print("all figures built"); import os
for f in sorted(os.listdir(F)): print("  ",f, os.path.getsize(f'{F}/{f}'),"bytes")

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
F="figures"; BONE="#c0392b"; DOWN="#2471a3"; NEU="#7f8c8d"; KO="#7b241c"
fig=plt.figure(figsize=(13.8,5.8)); gs=fig.add_gridspec(1,2,width_ratios=[1.55,1],wspace=0.18)
ax=fig.add_subplot(gs[0,0]); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,10)
ax.text(0,9.75,"A   Bone-health spaceflight cohort  (spoke-genelab, mouse RNA-Seq)",fontweight='bold',fontsize=12)
def box(x,y,w,h,t,c,fs=8.5,tc='white'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05,rounding_size=0.09",fc=c,ec='none'))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',color=tc,fontsize=fs,fontweight='bold',linespacing=1.2)
# Row1
box(0.5,8.7,9.0,0.7,"NASA OSDR / GeneLab  —  spaceflight omics  (all mouse, transcriptomic)","#34495e",9.5)
# Row2 headers
box(0.5,7.35,4.3,0.95,"SPACEFLIGHT (in-orbit)\nOSD-690 marrow · SF vs Ground",BONE,8.6)
box(5.2,7.35,4.3,0.95,"GROUND UNLOADING (disuse)\nHindlimb Unloaded vs Loaded",DOWN,8.6)
# Row3 sub
box(0.6,6.05,2.05,1.05,"Wild-Type\n3,161 DEG\n3,112 orth",'#a93226',8)
box(2.75,6.05,2.05,1.05,"Nrf2-KO\n3,517 DEG\n3,537 orth",KO,8)
box(5.3,6.05,2.05,1.05,"OSD-467\ncortical bone\n8 genes",'#1f618d',8)
box(7.45,6.05,2.05,1.05,"OSD-214\nmarrow\n~0 (artefact)",'#5d6d7e',8)
# Row4 ortholog
box(0.5,4.55,9.0,0.85,"mouse → human orthologs  (IS_ORTHOLOG_MGiG)","#16a085",9.5)
# Row5 federation
box(0.5,2.75,9.0,1.25,"Federation on Entrez gene\nspoke-okn · rdkg (HPO bone phenotypes) · digcfdekg (BMD /\nosteoporosis / fracture) · aopwiki · prokn","#8e44ad",8.5)
ax.annotate("",xy=(5,6.05),xytext=(5,5.9),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.4))
ax.annotate("",xy=(2.7,5.9),xytext=(2.7,6.05),arrowprops=dict(arrowstyle='-',color='#999',lw=0))
ax.annotate("",xy=(5,4.4),xytext=(5,4.55),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.4))
ax.annotate("",xy=(5,4.0),xytext=(5,4.55),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.4))
ax.annotate("",xy=(5,5.4),xytext=(5,6.05),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.4))
ax.text(0.5,1.95,"Mouse-derived, ortholog-inferred — hypothesis generation, not clinical inference",
        fontsize=9,style='italic',color=BONE)
ax2=fig.add_subplot(gs[0,1])
labels=["OSD-690\nmarrow WT","OSD-690\nmarrow\nNrf2-KO","OSD-467\ncortical\nHLU","OSD-214\nmarrow\nHLU"]
vals=[3161,3517,8,2]; cols=[BONE,KO,DOWN,NEU]
ax2.bar(range(4),vals,color=cols); ax2.set_yscale('log'); ax2.set_ylim(1,9000)
ax2.set_xticks(range(4)); ax2.set_xticklabels(labels,fontsize=8)
for i,v in enumerate(vals): ax2.text(i,v*1.2,f"{v:,}",ha='center',fontsize=9.5,fontweight='bold')
ax2.set_ylabel("significant DE genes (adj p <= 0.05)")
ax2.set_title("B   Signal asymmetry: rich flight marrow,\n      near-empty ground-disuse bone",loc='left',fontweight='bold',fontsize=11)
plt.savefig(f"{F}/bone_fig1_cohort.png",dpi=150,bbox_inches='tight'); plt.close(); print("ok")

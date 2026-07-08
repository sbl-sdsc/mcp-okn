import json, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
D="data"; F="figures"; BONE="#c0392b"
st=json.load(open(f"{D}/stats.json"))
fig=plt.figure(figsize=(14.2,4.7))
gs=fig.add_gridspec(1,3,width_ratios=[1,0.82,1.5],wspace=0.4)

# A enrichment
axa=fig.add_subplot(gs[0,0])
x=np.arange(2); axa.bar(x-0.19,[489.6,21.2],0.36,label='expected (by chance)',color='#bdc3c7')
axa.bar(x+0.19,[492,31],0.36,label='observed (actual overlap)',color=BONE)
axa.set_xticks(x); axa.set_xticklabels(["vs GWAS BMD/\nfracture set","vs Mendelian\nbone-loss set"],fontsize=9)
axa.set_ylabel("signature genes that are\nalso bone-loss genes",fontsize=9.5); axa.set_ylim(0,640)
axa.text(0,525,"1.00x\n(ns)",ha='center',fontsize=9,fontweight='bold',color='#777')
axa.text(1,120,"1.46x\np=0.018",ha='center',fontsize=9,fontweight='bold',color=BONE)
axa.legend(fontsize=8.5,frameon=False,loc='upper right',bbox_to_anchor=(1.03,1.03))
axa.set_title("A   Bone-loss over-representation",loc='left',fontweight='bold',fontsize=11.5,pad=8)

# B specificity
axb=fig.add_subplot(gs[0,1])
sp=st['specificity']; vals=[sp.get('systemic',0),sp.get('intermediate',0),sp.get('marrow-selective',0)]
axb.pie(vals,colors=['#5d6d7e','#e67e22',BONE],startangle=90,radius=0.86,center=(0,0.1),wedgeprops=dict(width=0.40,edgecolor='w'),
        autopct=lambda p:f"{int(round(p*sum(vals)/100))}",pctdistance=0.80,textprops={'fontsize':10,'color':'white','fontweight':'bold'})
axb.text(0,0.1,"221 high-\neffect genes",ha='center',va='center',fontsize=9.5,fontweight='bold')
axb.legend(['systemic (210)','intermediate (41)','marrow-selective (5)'],fontsize=8.7,loc='upper center',bbox_to_anchor=(0.5,-0.02),frameon=False)
axb.set_ylim(-1.15,1.15)
axb.set_title("B   Tissue specificity",loc='left',fontweight='bold',fontsize=11.5)

# C canonical panel
axc=fig.add_subplot(gs[0,2])
panel=[('ALPL',-1.086,-1.142,'osteoblast / mineralization'),('IBSP',-0.811,-0.649,'bone matrix protein'),
 ('FAM20A',-2.014,np.nan,'biomineralization kinase'),('COL1A1',np.nan,-1.347,'type I collagen (matrix)'),
 ('LRP5',np.nan,-0.511,'Wnt co-receptor / bone mass'),('NFATC1',np.nan,-0.598,'master osteoclast TF'),
 ('MMP9',np.nan,-0.672,'osteoclast MMP'),('CSF1',np.nan,-0.379,'M-CSF (osteoclast)'),
 ('CA2',-0.419,-0.402,'osteoclast carbonic anhydrase'),('CXCL2',1.901,1.992,'inflammatory chemokine')]
mat=np.array([[p[1],p[2]] for p in panel],dtype=float)
im=axc.imshow(mat,cmap='RdBu_r',vmin=-2,vmax=2,aspect='auto')
axc.set_xticks([0,1]); axc.set_xticklabels(['WT\nflight','Nrf2-KO\nflight'],fontsize=9.3)
axc.set_yticks(range(len(panel))); axc.set_yticklabels([p[0] for p in panel],fontsize=9.3)
for i,p in enumerate(panel):
    for j,v in enumerate([p[1],p[2]]):
        if not np.isnan(v): axc.text(j,i,f"{v:+.2f}",ha='center',va='center',fontsize=8.2,color='white' if abs(v)>1 else '#222',fontweight='bold')
        else: axc.text(j,i,"ns",ha='center',va='center',fontsize=8,color='#999')
    axc.text(1.62,i,p[3],va='center',fontsize=8,color='#444')
axc.set_xlim(-0.5,3.95)
cb=fig.colorbar(im,ax=axc,fraction=0.032,pad=0.02); cb.set_label('log2FC (flight vs ground)',fontsize=8); cb.ax.tick_params(labelsize=7.5)
axc.set_title("C   Canonical bone-remodeling genes",loc='left',fontweight='bold',fontsize=11.5)
plt.savefig(f"{F}/bone_fig3_bonerelevance.png",dpi=150,bbox_inches='tight'); plt.close(); print("fig3 rebuilt (plots only)")

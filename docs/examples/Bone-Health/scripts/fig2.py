import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
D="data"; F="figures"; BONE="#c0392b"; GRN="#27ae60"; KO="#7b241c"
m=pd.read_csv(f"{D}/wt_ko_human_merged.tsv",sep="\t")
both=m[m.log2fc_wt.notna()&m.log2fc_ko.notna()].copy()
fig,(axA,axB)=plt.subplots(1,2,figsize=(12.6,5.3),gridspec_kw={'width_ratios':[1.1,1]})
same=np.sign(both.log2fc_wt)==np.sign(both.log2fc_ko)
axA.axhline(0,color='#ccc',lw=.8); axA.axvline(0,color='#ccc',lw=.8)
axA.plot([-6,6],[-6,6],'--',color='#bbb',lw=1)
axA.scatter(both.log2fc_wt[same],both.log2fc_ko[same],s=8,c=GRN,alpha=.4,label=f"same direction ({int(same.sum())})")
axA.scatter(both.log2fc_wt[~same],both.log2fc_ko[~same],s=14,c=BONE,alpha=.75,label=f"opposite ({int((~same).sum())})")
axA.set_xlim(-4,4); axA.set_ylim(-4,4)
axA.set_xlabel("log2FC  Wild-Type  (Space Flight vs Ground)"); axA.set_ylabel("log2FC  Nrf2-KO")
axA.set_title("A   Robust core: 1,754 genes significant in both\n      genotype arms, 98.4% same direction",loc='left',fontweight='bold',fontsize=11)
axA.legend(loc='lower right',fontsize=8.5,frameon=False)
genes=['MMP9','NFATC1','LRP5','CSF1','COL1A1','LRP4']; kv=[-0.672,-0.598,-0.511,-0.379,-1.347,-0.331]
roles=['osteoclast MMP','master osteoclast TF','Wnt co-receptor (bone mass)','osteoclast M-CSF','type I collagen','Wnt/sclerostin']
y=np.arange(len(genes))[::-1]
axB.barh(y,kv,color=KO,alpha=.92,height=0.62)
axB.axvline(0,color='#333',lw=.9)
for i in range(len(genes)):
    axB.text(0.03,y[i],f"  {roles[i]}",va='center',ha='left',fontsize=8,color='#555')
    axB.text(kv[i]-0.03,y[i],f"{kv[i]:.2f}",va='center',ha='right',fontsize=8,color=KO,fontweight='bold')
axB.set_yticks(y); axB.set_yticklabels(genes,fontsize=10,fontweight='bold')
axB.set_xlim(-1.65,0.95); axB.set_xlabel("log2FC in Nrf2-KO flight marrow")
axB.set_title("B   Nrf2-dependent bone-remodeling suppression\n      (significant only when Nrf2 is knocked out)",loc='left',fontweight='bold',fontsize=11)
plt.tight_layout(); plt.savefig(f"{F}/bone_fig2_nrf2.png",dpi=150,bbox_inches='tight'); plt.close(); print("ok")

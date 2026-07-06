import csv, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from collections import Counter
D="/sessions/nifty-festive-gauss/mnt/outputs/exposome"
def load(fn):
    p=f"{D}/data/{fn}"; p=p if os.path.exists(p) else f"{D}/{fn}"
    return list(csv.DictReader(open(p)))
detail=load("corroboration_detail.csv")
CATMAP={"breast cancer":"Hormone-sensitive cancers","breast carcinoma":"Hormone-sensitive cancers","ovarian cancer":"Hormone-sensitive cancers","uterine cancer":"Hormone-sensitive cancers","prostate cancer":"Hormone-sensitive cancers","testicular cancer":"Hormone-sensitive cancers","liver cancer":"Hormone-sensitive cancers","lung cancer":"Hormone-sensitive cancers","colorectal cancer":"Hormone-sensitive cancers","endometriosis":"Reproductive & endocrine","polycystic ovary syndrome":"Reproductive & endocrine","uterine fibroid":"Reproductive & endocrine","male infertility":"Reproductive & endocrine","obesity":"Metabolic & cardiometabolic","diabetes mellitus":"Metabolic & cardiometabolic","arteriosclerosis":"Metabolic & cardiometabolic","coronary artery disease":"Metabolic & cardiometabolic","hypertension":"Metabolic & cardiometabolic","cardiomyopathy":"Metabolic & cardiometabolic","nutrition disease":"Metabolic & cardiometabolic","pancreatitis":"Metabolic & cardiometabolic","cerebrovascular disease":"Metabolic & cardiometabolic","major depressive disorder":"Neuro & psychiatric","depressive disorder":"Neuro & psychiatric","anxiety disorder":"Neuro & psychiatric","bipolar disorder":"Neuro & psychiatric","migraine":"Neuro & psychiatric","nervous system disease":"Neuro & psychiatric","epilepsy":"Neuro & psychiatric","motor neuron disease":"Neuro & psychiatric","multiple sclerosis":"Neuro & psychiatric","Parkinson's disease":"Neuro & psychiatric","asthma":"Immune & inflammatory","dermatitis":"Immune & inflammatory","psoriasis":"Immune & inflammatory","rheumatoid arthritis":"Immune & inflammatory","inflammatory bowel disease":"Immune & inflammatory","Hodgkin's lymphoma":"Immune & inflammatory","lymphoid leukemia":"Immune & inflammatory"}
KEEPC=["BPA","TBBPA","BPAF","BPB","TCBPA","BPS","BPF","BPC","BPZ"]
ct=Counter(); tc=Counter()
for r in detail:
    if r["chemical"] not in KEEPC: continue
    cat=CATMAP.get(r["disease"])
    if not cat: continue
    ct[(r["chemical"],r["target"])]+=1; tc[(r["target"],cat)]+=1
chems=[c for c in KEEPC if any(k[0]==c for k in ct)]
targs=sorted({k[1] for k in ct})
cats=["Hormone-sensitive cancers","Reproductive & endocrine","Metabolic & cardiometabolic","Neuro & psychiatric","Immune & inflammatory"]
cats=[c for c in cats if any(k[1]==c for k in tc)]
def stack(items,weightf,gap=0.6):
    tot=sum(weightf(i) for i in items); pos={}; y=0
    for i in items:
        h=weightf(i); pos[i]=(y,y+h); y+=h+gap
    return pos,y-gap
cw=lambda c:max(1,sum(v for k,v in ct.items() if k[0]==c))
tw=lambda t:max(1,sum(v for k,v in ct.items() if k[1]==t))
zw=lambda z:max(1,sum(v for k,v in tc.items() if k[1]==z))
pc,hc=stack(chems,cw); pt,ht=stack(targs,tw); pz,hz=stack(cats,zw)
H=max(hc,ht,hz)
def center(p,H_): 
    lo=min(v[0] for v in p.values()); hi=max(v[1] for v in p.values()); off=(H_-(hi-lo))/2-lo; return {k:(a+off,b+off) for k,(a,b) in p.items()}
pc=center(pc,H);pt=center(pt,H);pz=center(pz,H)
X0,X1,X2=0,4,8; W=0.5
NAVY="#20365b";TEAL="#1b7a7a";CORAL="#d1495b"
fig,ax=plt.subplots(figsize=(13,7.6))
def band(x_l,x_r,yl0,yl1,yr0,yr1,color,a=0.32):
    v=[(x_l,yl0),(x_l+(x_r-x_l)*.5,yl0),(x_l+(x_r-x_l)*.5,yr0),(x_r,yr0),(x_r,yr1),(x_l+(x_r-x_l)*.5,yr1),(x_l+(x_r-x_l)*.5,yl1),(x_l,yl1),(x_l,yl0)]
    c=[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.LINETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.CLOSEPOLY]
    ax.add_patch(patches.PathPatch(Path(v,c),facecolor=color,edgecolor="none",alpha=a))
# chem->target bands
outc={c:pc[c][0] for c in chems}; intg={t:pt[t][0] for t in targs}
for (c,t),v in sorted(ct.items()):
    yl0=outc[c]; yl1=yl0+v; yr0=intg[t]; yr1=yr0+v
    outc[c]=yl1; intg[t]=yr1
    band(X0+W,X1,yl0,yl1,yr0,yr1,NAVY)
outt={t:pt[t][0] for t in targs}; inz={z:pz[z][0] for z in cats}
for (t,z),v in sorted(tc.items()):
    if z not in inz: continue
    yl0=outt[t]; yl1=yl0+v; yr0=inz[z]; yr1=yr0+v
    outt[t]=yl1; inz[z]=yr1
    band(X1+W,X2,yl0,yl1,yr0,yr1,TEAL)
def boxes(pos,x,color,align="left"):
    for n,(a,b) in pos.items():
        ax.add_patch(patches.Rectangle((x,a),W,b-a,facecolor=color,edgecolor="white",lw=.7))
        if align=="left": ax.text(x-0.15,(a+b)/2,n,ha="right",va="center",fontsize=8.5,color="#222")
        elif align=="rightlab": ax.text(x+W+0.15,(a+b)/2,n,ha="left",va="center",fontsize=8.5,color="#222")
        else: ax.text(x+W/2,(a+b)/2,n,ha="center",va="center",fontsize=8,color="white",fontweight="bold")
boxes(pc,X0,NAVY,"left")
for t,(a,b) in pt.items(): 
    ax.add_patch(patches.Rectangle((X1,a),W,b-a,facecolor=TEAL,edgecolor="white",lw=.7)); ax.text(X1+W/2,(a+b)/2,t,ha="center",va="center",fontsize=7.5,color="white",fontweight="bold")
boxes(pz,X2,CORAL,"rightlab")
ax.text(X0+W/2,H+1.5,"CHEMICAL",ha="center",fontweight="bold",fontsize=10,color=NAVY)
ax.text(X1+W/2,H+1.5,"MOLECULAR TARGET",ha="center",fontweight="bold",fontsize=10,color=TEAL)
ax.text(X2+W/2,H+1.5,"DISEASE CATEGORY",ha="center",fontweight="bold",fontsize=10,color=CORAL)
ax.set_xlim(-2.2,10.8); ax.set_ylim(-1,H+2.6); ax.axis("off")
ax.set_title("Bisphenol exposome flow: chemical → molecular target → disease category\n(Proto-OKN: AOP-Wiki stressors, SPOKE-OKN gene–disease; BPA/TBBPA AOP-anchored, analogues via shared ER targets)",fontsize=11,fontweight="bold")
plt.tight_layout(); plt.savefig(f"{D}/figures/fig5_sankey.png",bbox_inches="tight",dpi=150); plt.close()
print("fig5_sankey.png written")

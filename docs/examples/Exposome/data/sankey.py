import csv, os
from collections import defaultdict, Counter
D="/sessions/nifty-festive-gauss/mnt/outputs/exposome"
def load(fn):
    p=f"{D}/data/{fn}"; p=p if os.path.exists(p) else f"{D}/{fn}"
    return list(csv.DictReader(open(p)))
detail=load("corroboration_detail.csv")

CAT={ # disease -> category
 "breast cancer":"Hormone-sensitive cancers","breast carcinoma":"Hormone-sensitive cancers",
 "ovarian cancer":"Hormone-sensitive cancers","uterine cancer":"Hormone-sensitive cancers",
 "prostate cancer":"Hormone-sensitive cancers","testicular cancer":"Hormone-sensitive cancers",
 "liver cancer":"Hormone-sensitive cancers","lung cancer":"Hormone-sensitive cancers","colorectal cancer":"Hormone-sensitive cancers",
 "endometriosis":"Reproductive & endocrine","polycystic ovary syndrome":"Reproductive & endocrine",
 "uterine fibroid":"Reproductive & endocrine","male infertility":"Reproductive & endocrine",
 "obesity":"Metabolic & cardiometabolic","diabetes mellitus":"Metabolic & cardiometabolic",
 "arteriosclerosis":"Metabolic & cardiometabolic","coronary artery disease":"Metabolic & cardiometabolic",
 "hypertension":"Metabolic & cardiometabolic","cardiomyopathy":"Metabolic & cardiometabolic",
 "nutrition disease":"Metabolic & cardiometabolic","pancreatitis":"Metabolic & cardiometabolic","cerebrovascular disease":"Metabolic & cardiometabolic",
 "major depressive disorder":"Neuro & psychiatric","depressive disorder":"Neuro & psychiatric",
 "anxiety disorder":"Neuro & psychiatric","bipolar disorder":"Neuro & psychiatric","migraine":"Neuro & psychiatric",
 "nervous system disease":"Neuro & psychiatric","epilepsy":"Neuro & psychiatric","motor neuron disease":"Neuro & psychiatric",
 "multiple sclerosis":"Neuro & psychiatric","Parkinson's disease":"Neuro & psychiatric",
 "asthma":"Immune & inflammatory","dermatitis":"Immune & inflammatory","psoriasis":"Immune & inflammatory",
 "rheumatoid arthritis":"Immune & inflammatory","inflammatory bowel disease":"Immune & inflammatory",
 "Hodgkin's lymphoma":"Immune & inflammatory","lymphoid leukemia":"Immune & inflammatory",
 "liver disease":"Other","glaucoma":"Other","myopia":"Other","skin melanoma":"Other",
 "squamous cell carcinoma":"Other","chronic obstructive pulmonary disease":"Other",
}
# keep representative chemicals
KEEPC=["BPA","TBBPA","BPAF","BPB","TCBPA","BPS","BPF","BPC","BPZ"]
flow_ct=Counter(); flow_td=Counter()
for r in detail:
    if r["chemical"] not in KEEPC: continue
    cat=CAT.get(r["disease"]); 
    if not cat: continue
    flow_ct[(r["chemical"],r["target"])]+=1
    flow_td[(r["target"],cat)]+=1

chems=[c for c in KEEPC if any(k[0]==c for k in flow_ct)]
targs=sorted({k[1] for k in flow_ct})
cats=["Hormone-sensitive cancers","Reproductive & endocrine","Metabolic & cardiometabolic","Neuro & psychiatric","Immune & inflammatory","Other"]
cats=[c for c in cats if any(k[1]==c for k in flow_td)]
nodes=chems+targs+cats
idx={n:i for i,n in enumerate(nodes)}
CT="#20365b"; TG="#1b7a7a"; DZ="#d1495b"
ncol=[CT]*len(chems)+[TG]*len(targs)+[DZ]*len(cats)
src=[];tgt=[];val=[];lc=[]
for (c,t),v in flow_ct.items():
    src.append(idx[c]);tgt.append(idx[t]);val.append(v);lc.append("rgba(32,54,91,0.35)")
# target->category weight = number of chem-target flows * td unique; use count of (target,cat) pairs from detail
tc=Counter()
for r in detail:
    if r["chemical"] not in KEEPC: continue
    cat=CAT.get(r["disease"])
    if cat: tc[(r["target"],cat)]+=1
for (t,cat),v in tc.items():
    src.append(idx[t]);tgt.append(idx[cat]);val.append(v);lc.append("rgba(27,122,122,0.30)")

try:
    import plotly.graph_objects as go
    fig=go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=nodes,color=ncol,pad=14,thickness=16,
                  line=dict(color="white",width=0.5)),
        link=dict(source=src,target=tgt,value=val,color=lc)))
    fig.update_layout(title_text="Bisphenol exposome: chemical → molecular target → disease category (Proto-OKN)",
                      font_size=11,width=1120,height=640,paper_bgcolor="white")
    fig.write_html(f"{D}/figures/sankey_chemical_target_disease.html",include_plotlyjs="cdn")
    print("Sankey HTML written")
    try:
        fig.write_image(f"{D}/figures/fig5_sankey.png",scale=2)
        print("Sankey PNG written")
    except Exception as e:
        print("PNG export skipped:",str(e)[:120])
except Exception as e:
    print("plotly failed:",e)

import pandas as pd, numpy as np
from scipy import stats

D = "/sessions/funny-fervent-davinci/mnt/outputs/urban_scaling"
df = pd.read_csv(f"{D}/data/sufficient_stats.csv")

rows=[]
for _,r in df.iterrows():
    n,sx,sy,sxx,sxy,syy = r.n, r.sx, r.sy, r.sxx, r.sxy, r.syy
    Sxx = sxx - sx*sx/n
    Sxy = sxy - sx*sy/n
    Syy = syy - sy*sy/n
    beta = Sxy/Sxx
    SSE  = Syy - beta*Sxy
    s2   = SSE/(n-2)
    se   = np.sqrt(s2/Sxx)
    R2   = Sxy**2/(Sxx*Syy)
    tcrit= stats.t.ppf(0.975, n-2)
    lo,hi= beta-tcrit*se, beta+tcrit*se
    t1   = (beta-1)/se                       # H0: beta = 1 (linear scaling)
    p1   = 2*stats.t.sf(abs(t1), n-2)
    if lo>1: cls="superlinear"
    elif hi<1: cls="sublinear"
    else: cls="linear (indistinguishable)"
    rows.append(dict(series=r.series, domain=r.domain, level=r.level, source=r.source,
        n=int(n), beta=beta, se=se, ci_lo=lo, ci_hi=hi, rate_elasticity=beta-1,
        R2=R2, t_vs_1=t1, p_vs_1=p1, classification=cls))

out = pd.DataFrame(rows).sort_values("beta", ascending=False)
out.to_csv(f"{D}/data/scaling_exponents.csv", index=False)
pd.set_option("display.width",200,"display.max_columns",20)
print(out[["series","level","n","beta","se","ci_lo","ci_hi","R2","p_vs_1","classification"]].to_string(index=False,
      float_format=lambda v: f"{v:.4f}" if abs(v)>1e-4 else f"{v:.2e}"))

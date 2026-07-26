import numpy as np, pandas as pd
from scipy import stats

def fit(n,sx,sy,sxx,sxy,syy):
    """OLS of y=ln(Y) on x=ln(N) from sufficient statistics.
    Also returns the RATE regression (ln(Y/N) on ln(N)), whose slope is beta-1 and
    whose R^2 is the honest one: R^2 of the count regression is mechanically ~1
    because Y = rate * N shares ln(N) on both sides."""
    Sxx = sxx - sx*sx/n
    Sxy = sxy - sx*sy/n
    Syy = syy - sy*sy/n
    beta = Sxy/Sxx
    SSE  = Syy - beta*Sxy
    se   = np.sqrt((SSE/(n-2))/Sxx)
    tcrit= stats.t.ppf(0.975, n-2)
    lo,hi= beta-tcrit*se, beta+tcrit*se
    t1   = (beta-1)/se
    p1   = 2*stats.t.sf(abs(t1), n-2)
    # rate regression: v = y - x
    Svv  = Syy - 2*Sxy + Sxx
    Sxv  = Sxy - Sxx
    R2r  = (Sxv**2)/(Sxx*Svv) if Svv>0 else np.nan
    cls  = "superlinear" if lo>1 else ("sublinear" if hi<1 else "linear (n.s.)")
    return dict(n=int(n), beta=beta, se=se, ci_lo=lo, ci_hi=hi,
                rate_elasticity=beta-1, R2_count=Sxy**2/(Sxx*Syy),
                R2_rate=R2r, t_vs_1=t1, p_vs_1=p1, classification=cls)

def fit_table(df, keys):
    out=[]
    for _,r in df.iterrows():
        rec={k:r[k] for k in keys}
        rec.update(fit(r.n,r.sx,r.sy,r.sxx,r.sxy,r.syy))
        out.append(rec)
    return pd.DataFrame(out)

"""
enrichment.py — hypergeometric over-representation with Benjamini-Hochberg FDR against an EXPLICIT
background. Reuse for GO terms, Reactome pathways, and disease/trait gene-sets.

    from enrichment import enrich
    df = enrich(signature_genes, category_to_genes, background, kmin=4, Kmin=3)

- signature_genes: iterable of gene ids (same id space as the categories/background, e.g. Entrez or
  HGNC symbol).
- category_to_genes: dict {category_id/label -> set(gene ids)} (e.g. GO term -> its genes in the KG).
- background: iterable of gene ids that COULD be drawn (the universe; see references/enrichment-methods.md).
Returns a pandas DataFrame sorted by p, with columns: category, K, k, n, N, expected, fold, p, fdr.

Notes: everything is intersected with `background` first (a category gene not in the background can't
be sampled, and a signature gene not in the background doesn't count toward n). Fold = k / expected.
CLI demo: `python enrichment.py --demo`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import hypergeom


def enrich(signature_genes, category_to_genes, background, kmin=3, Kmin=3):
    bg = set(map(str, background))
    N = len(bg)
    sig = set(map(str, signature_genes)) & bg
    n = len(sig)
    if N == 0 or n == 0:
        raise ValueError("empty background or no signature genes in background")
    rows = []
    for cat, genes in category_to_genes.items():
        cg = set(map(str, genes)) & bg
        K = len(cg)
        k = len(cg & sig)
        if k < kmin or Kmin > K:
            continue
        exp = n * K / N
        p = float(hypergeom.sf(k - 1, N, K, n))
        rows.append(
            (cat, K, k, n, N, round(exp, 2), round(k / exp, 2) if exp else np.nan, p)
        )
    df = pd.DataFrame(
        rows, columns=["category", "K", "k", "n", "N", "expected", "fold", "p"]
    )
    if len(df):
        df = df.sort_values("p").reset_index(drop=True)
        m = len(df)
        df["fdr"] = (
            (df.p * m / (df.index + 1)).clip(upper=1.0)[::-1].cummin()[::-1]
        )  # BH, monotone
    else:
        df["fdr"] = []
    return df


def enrich_single(signature_genes, category_genes, background):
    """Convenience: one category (e.g. a curated Mendelian bone-loss set). Returns a dict."""
    d = enrich(
        signature_genes, {"set": set(category_genes)}, background, kmin=1, Kmin=1
    )
    return d.iloc[0].to_dict() if len(d) else None


def _demo():
    rng = np.random.default_rng(0)
    background = [str(i) for i in range(1, 20001)]
    # a "signature" of 3000 genes, seeded to be enriched for category C1
    c1 = {str(i) for i in range(1, 151)}  # small curated set (150)
    c2 = {str(i) for i in range(1, 3201)}  # broad permissive set (~16%)
    sig = set(rng.choice(background, 3000, replace=False).tolist()) | set(list(c1)[:31])
    df = enrich(
        sig, {"C1_curated(150)": c1, "C2_broad(3200)": c2}, background, kmin=1, Kmin=1
    )
    print(df.to_string(index=False))


if __name__ == "__main__":
    import sys

    _demo() if "--demo" in sys.argv else print(__doc__)

"""
collapse_orthologs.py — collapse a model-organism differential-expression table to human orthologs.

A model-organism source (e.g. spoke-genelab, mouse) maps its genes to human orthologs (e.g.
IS_ORTHOLOG_MGiG), which is 1:many / many:1.
This collapses to one row per human gene using the max |log2FC| rule (the standard choice: keep the
strongest effect), carries an ambiguity flag (how many mouse genes mapped in), and computes the
mean-rule value as a sensitivity check.

    from collapse_orthologs import collapse
    human_df = collapse(mouse_rows)   # mouse_rows: list of dicts or a DataFrame

Expected input columns (rename to match, or pass a column map):
  hEntrez (human Entrez id), humanSymbol, symbol (mouse), log2fc, adj_p_value
Only rows WITH a human ortholog (non-empty hEntrez) are collapsed; mouse-only genes are dropped for
the human analysis (report how many were dropped). Output columns:
  hEntrez, humanSymbol, mouse_symbols, log2fc (max|.|, signed), log2fc_mean, adj_p_value,
  n_mouse_map (ambiguity), sign_flip (True if the max-rule and mean-rule disagree in sign).
CLI demo: `python collapse_orthologs.py --demo`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def collapse(rows, col_map=None):
    df = pd.DataFrame(rows).copy()
    if col_map:
        df = df.rename(columns=col_map)
    for c in ["hEntrez", "humanSymbol", "symbol", "log2fc", "adj_p_value"]:
        if c not in df.columns:
            df[c] = np.nan
    df["hEntrez"] = df["hEntrez"].astype("string")
    df = df[df.hEntrez.notna() & (df.hEntrez.str.len() > 0)].copy()
    df["log2fc"] = pd.to_numeric(df["log2fc"], errors="coerce")
    df["adj_p_value"] = pd.to_numeric(df["adj_p_value"], errors="coerce")
    df["absl"] = df.log2fc.abs()

    out = []
    for h, g in df.groupby("hEntrez"):
        top = g.loc[g.absl.idxmax()]  # max |log2FC| representative
        mean_l = g.log2fc.mean()  # mean-rule sensitivity
        out.append(
            {
                "hEntrez": h,
                "humanSymbol": top.get("humanSymbol"),
                "mouse_symbols": "|".join(sorted(set(g.symbol.dropna().astype(str)))),
                "log2fc": round(float(top.log2fc), 4),
                "log2fc_mean": round(float(mean_l), 4),
                "adj_p_value": float(top.adj_p_value),
                "n_mouse_map": int(g.symbol.nunique()),
                "sign_flip": bool(
                    np.sign(top.log2fc) != np.sign(mean_l) and mean_l != 0
                ),
            }
        )
    res = (
        pd.DataFrame(out)
        .sort_values("log2fc", key=lambda s: s.abs(), ascending=False)
        .reset_index(drop=True)
    )
    nflip = int(res.sign_flip.sum()) if len(res) else 0
    print(
        f"[collapse_orthologs] {len(res)} human genes; {res.n_mouse_map.gt(1).sum() if len(res) else 0} "
        f"ambiguous (>=2 mouse genes); mean-rule sign flips: {nflip}"
    )
    return res


def _demo():
    rows = [
        {
            "hEntrez": "249",
            "humanSymbol": "ALPL",
            "symbol": "Alpl",
            "log2fc": -1.09,
            "adj_p_value": 0.0009,
        },
        {
            "hEntrez": "2920",
            "humanSymbol": "CXCL1",
            "symbol": "Cxcl2",
            "log2fc": 1.90,
            "adj_p_value": 0.005,
        },
        {
            "hEntrez": "2920",
            "humanSymbol": "CXCL1",
            "symbol": "Cxcl1",
            "log2fc": 1.20,
            "adj_p_value": 0.02,
        },
        {
            "hEntrez": "",
            "humanSymbol": "",
            "symbol": "Gm12345",
            "log2fc": -2.3,
            "adj_p_value": 0.01,
        },
    ]
    print(collapse(rows).to_string(index=False))


if __name__ == "__main__":
    import sys

    _demo() if "--demo" in sys.argv else print(__doc__)

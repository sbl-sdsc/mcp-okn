#!/usr/bin/env python3
"""06_build_html.py -- render the interactive HTML report FROM the Markdown report.

The .md is the single source of the prose. This script adds only what Markdown
cannot express: KPI cards, the interactive results table, and the folium map,
then fills the {{stat}} placeholders in the delivered .md from stats.json.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/sessions/busy-happy-edison/mnt/.claude/skills/okn-report-style/scripts")
from build_report_html import (build_report_from_markdown, candidate_table, check_report_parity,
                               check_figure_numbering, check_html_structure, fill_stats,
                               kpis_from_stats, load_stats)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
D = os.path.join(ROOT, "data")
MD = os.path.join(ROOT, "PFAS_report.md")
HTML = os.path.join(ROOT, "PFAS_report.html")

S = load_stats(os.path.join(D, "stats.json"))
ranked = pd.read_csv(os.path.join(D, "cells_ranked.tsv"), sep="\t", dtype={"cid": str})
named = pd.read_csv(os.path.join(D, "pfas_facilities_named.csv"), dtype=str)
ringn = pd.read_csv(os.path.join(D, "ring_pfas_facilities_named.csv"), dtype=str)

# ------------------------------------------------------------------ results table
name_same = named.groupby("cid")["facName"].apply(lambda s: "; ".join(sorted(set(s.dropna()))[:3]))
name_ring = ringn.groupby("cid")["facName"].apply(lambda s: "; ".join(sorted(set(s.dropna()))[:3]))

rows = []
for _, r in ranked.iterrows():
    fac = name_same.get(r["cid"], "")
    if not fac:
        g = name_ring.get(r["cid"], "")
        fac = f"(adjacent) {g}" if g else "—"
    ind = r["sameTopIndustry"] if isinstance(r["sameTopIndustry"], str) else (
        r["ringTopIndustry"] if isinstance(r["ringTopIndustry"], str) else "—")
    rows.append({
        "rank": int(r["rank"]),
        "score": round(float(r["score"]), 1),
        "tier": r["tier"],
        "window": r["window"],
        "state": r["stateName"],
        "county": r["countyName"],
        "s2_cell": r["cid"],
        "detections": int(r["nDet"]),
        "observations": int(r["nObs"]),
        "det_freq": round(float(r["detFreq"]), 3) if pd.notna(r["detFreq"]) else "",
        "analytes_detected": int(r["nDetAnalytes"]),
        "max_ngL": round(float(r["maxNgL"]), 1) if pd.notna(r["maxNgL"]) else "",
        "pfas_fac_same": int(r["nPfasFac"]),
        "pfas_fac_ring": int(r["nRingPfasFac"]),
        "all_fac_same": int(r["nFac"]),
        "top_industry": ind,
        "nearest_pfas_facilities": fac,
        "n_sources": int(r["nSources"]),
        "sources": r["sourceList"].split(";"),
    })

COLUMNS = [
    ("rank", "rank"), ("score", "score"), ("tier", "tier"), ("window", "attribution window"),
    ("state", "state"), ("county", "county"), ("s2_cell", "S2 L13 cell"),
    ("detections", "detections"), ("observations", "obs"), ("det_freq", "det. freq"),
    ("analytes_detected", "analytes"), ("max_ngL", "max ng/L"),
    ("pfas_fac_same", "PFAS fac. (cell)"), ("pfas_fac_ring", "PFAS fac. (ring)"),
    ("all_fac_same", "all fac. (cell)"), ("top_industry", "top co-located industry"),
    ("nearest_pfas_facilities", "nearest PFAS-flagged facilities"),
]
table = candidate_table(
    rows, COLUMNS,
    search_keys=["county", "state", "top_industry", "nearest_pfas_facilities", "s2_cell"],
    numeric_keys=["rank", "score", "detections", "observations", "det_freq",
                  "analytes_detected", "max_ngL", "pfas_fac_same", "pfas_fac_ring",
                  "all_fac_same", "n_sources"],
    page_size=25, default_sort=("rank", "asc"),
    extra_filters=[("tier", "confidence tier"), ("state", "state"),
                   ("window", "attribution window"), ("top_industry", "industry group")],
    sources_col=("n_sources", "sources"),
)

# ------------------------------------------------------------------ KPI cards
KPI_SPEC = [
    ("universe_cells", f"S2 cells sampled ({S['states']} states)", ","),
    ("cells_with_detection", "cells with a PFAS detection", ","),
    ("tierAB", f"facility-attributable ({S['attributable_pct']}%)", ","),
    ("colocated_facilities", f"co-located EPA facilities ({S['same_cell_pfas_facilities']} PFAS-flagged)", ","),
    ("median_maxconc_tierA", f"median peak ng/L tier A (vs {S['median_maxconc_tierD']} tier D)"),
    ("fisher_or", "× odds of a detection near a PFAS facility"),
]
kpis = kpis_from_stats(S, KPI_SPEC)

# ------------------------------------------------------------------ fill the delivered .md
raw = open(MD).read()
filled = fill_stats(raw, S, strict=False)
open(MD, "w").write(filled)

# ------------------------------------------------------------------ render
build_report_from_markdown(
    MD, HTML, kpis=kpis, table=table, stats=S,
    footer="Built from the OKN federated SPARQL endpoint (mcp-okn). "
           "Spatial co-occurrence only — not an attribution of responsibility. "
           "Map tiles © OpenStreetMap contributors.",
)

# ------------------------------------------------------------------ splice the folium map
frag = open(os.path.join(D, "map_fragment.html")).read()
html = open(HTML).read()
assert "<!-- INTERACTIVE_MAP -->" in html, "map marker missing from rendered HTML"
html = html.replace("<!-- INTERACTIVE_MAP -->", frag)
open(HTML, "w").write(html)

print("\n=== delivery gates ===")
print("figure numbering:", check_figure_numbering(MD))
print("html structure  :", check_html_structure(HTML))
print("parity          :", check_report_parity(MD, HTML))

#!/usr/bin/env python3
"""Instrument-Criticality — render the HTML report FROM the Markdown source.

Builds only the chrome the Markdown cannot express (KPI cards from stats.json,
the interactive ranked table) and hands everything to
`build_report_from_markdown`, which renders the prose, embeds the figures, fills
the {{key}} placeholders and runs the parity gate.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/sessions/gifted-adoring-thompson/mnt/.claude/skills/"
                   "okn-report-style/scripts")
from build_report_html import (build_report_from_markdown, candidate_table,  # noqa: E402
                               fill_stats, kpis_from_stats, load_stats)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MD = ROOT / "Instrument-Criticality_report.md"
HTML = ROOT / "Instrument-Criticality_report.html"

stats = load_stats(DATA / "stats.json")
sci = pd.read_csv(DATA / "instrument_criticality.csv")

kpis = kpis_from_stats(stats, [
    ("n_space_instruments", "spaceborne instrument labels"),
    ("n_scored_instruments", "scored science instruments"),
    ("n_corrob_5", "corroborated on all 5 routes"),
    ("n_corrob_0", "no signal on any route"),
    ("spearman_rho_footprint_criticality", "footprint ~ criticality (Spearman ρ)"),
    ("top10_overlap_n", "top-10 overlap, volume vs criticality"),
    ("n_sole_measured_variables", "variables with a single measurer"),
    ("n_boundary_author_orcids", "boundary-spanning researchers (ORCID)"),
])

rows = []
for _, r in sci.iterrows():
    rows.append({
        "rank": int(r["rank"]),
        "instrument": r["instr"],
        "criticality": round(float(r["criticality"]), 1),
        "tier": r["tier"],
        "riskclass": r["riskClass"],
        "routes": f'{int(r["corroboration"])}/5',
        "datasets": int(r["nDs"]),
        "fracds": round(float(r["fracDs"]), 1),
        "rankgap": int(r["rank_gap"]),
        "r1": int(r["R1_cmMentionPapers"]),
        "r1b": int(r["R1b_platMentionPapers"]),
        "r2": int(r["R2_cmModelPapers"]),
        "r3": int(r["R3_doiPapers"]),
        "r4": int(r["R4_modelTitlePubs"]),
        "solevars": int(r["R5_nSoleVars"]),
        "sources_n": int(r["nSources"]),
        "sources_list": (["nasa-gesdisc-kg", "climatemodelskg"]
                         if r["nSources"] == 2 else ["nasa-gesdisc-kg"]),
    })

COLUMNS = [
    ("rank", "rank"), ("instrument", "instrument"),
    ("criticality", "criticality"), ("tier", "tier"),
    ("riskclass", "risk class"), ("routes", "routes"),
    ("datasets", "datasets"), ("fracds", "datasets (fractional)"),
    ("rankgap", "rank gap"), ("r1", "R1 named"), ("r1b", "R1b platform"),
    ("r2", "R2 + model"), ("r3", "R3 DOI use"), ("r4", "R4 NASA title"),
    ("solevars", "sole-measured vars"),
]

table = candidate_table(
    rows, COLUMNS,
    search_keys=["instrument", "tier", "riskclass"],
    numeric_keys=["rank", "criticality", "datasets", "fracds", "rankgap",
                  "r1", "r1b", "r2", "r3", "r4", "solevars"],
    page_size=25,
    extra_filters=[("tier", "confidence tier"), ("riskclass", "risk class"),
                   ("routes", "corroborating routes")],
    sources_col=("sources_n", "sources_list"),
)

build_report_from_markdown(MD, HTML, kpis=kpis, table=table, stats=stats)

# Fill the delivered .md too, so it reads standalone (no {{key}} left behind).
MD.write_text(fill_stats(MD.read_text(), stats))
print(f"wrote {HTML} and filled placeholders in {MD.name}")

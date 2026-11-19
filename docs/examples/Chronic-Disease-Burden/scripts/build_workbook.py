"""Build Chronic-Disease-Burden_results.xlsx from the data/ extracts."""
import json
import os

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "Chronic-Disease-Burden_results.xlsx")
S = json.load(open(os.path.join(D, "stats.json")))


def rd(name):
    return pd.read_csv(os.path.join(D, name), sep="\t", dtype={"fips": str})


ranked = rd("county_burden_ranked.tsv")
ranked.insert(0, "rank", range(1, len(ranked) + 1))
methods = pd.DataFrame([
    ("Unit of analysis", f"US county (n = {S['n_counties_places']:,}; 50 states + DC; Florida absent from the spoke-okn PLACES load)"),
    ("Prevalence source", "CDC PLACES place-level age-adjusted prevalence, spoke-okn PREVALENCE_DpL (9 conditions); inferred 2023 release (BRFSS 2021; high BP & cholesterol BRFSS 2019)"),
    ("Place→county", "spoke-okn PARTOF_LpL; county value = population-weighted mean of its places' estimates (weights = PLACES total_population)"),
    ("Eligibility for ranked lists", f"places in the county cover ≥ {S['min_pop']:,} residents"),
    ("County covariates", "County Health Rankings 2023 via spoke-okn PREVALENCEIN_SpL (14 measures); values parsed from 'value(quartile)'; life expectancy > 95 y set missing"),
    ("Composite burden", "mean of z-scores of the 9 conditions (primary); sensitivity: percentile mean, PCA PC1, without depression, cardiometabolic-only"),
    ("Tiers", "A: county in top quintile for ≥7 of 9 conditions; B: 5–6; C: 3–4"),
    ("Spatial statistics", "Moran's I and Local Moran (LISA) on 6-nearest-neighbour row-standardised weights, contiguous US, 999 permutations"),
    ("Correlation", "Spearman; clustering = average linkage on 1−ρ; partial ρ = rank residuals on 7 demographic covariates; within-state = state-demeaned ranks"),
    ("Gene overlap", "spoke-okn ASSOCIATES_DaG gene sets; hypergeometric vs 6,666-gene background; BH FDR; Mantel test (Spearman, 9,999 permutations)"),
    ("Disease identity", "DOID (spoke-okn) → MONDO via ubergraph skos:exactMatch"),
    ("Abbreviations", "BRFSS = Behavioral Risk Factor Surveillance System; CHR = County Health Rankings; COPD = chronic obstructive pulmonary disease; CHD = coronary heart disease; DOID = Disease Ontology ID; FDR = false-discovery rate; FIPS = Federal Information Processing Standard code; KG = knowledge graph; LISA = local indicators of spatial association; MONDO = Mondo Disease Ontology; MRP = multilevel regression and poststratification; OKN = Open Knowledge Network; PCA = principal component analysis; PLACES = Population Level Analysis and Community Estimates; pp = percentage points"),
], columns=["item", "description"])

sheets = {
    "Ranked Results": ranked,
    "Top10 by condition": rd("top10_by_condition.tsv"),
    "Condition summary": rd("condition_summary.tsv"),
    "Validation PLACES vs CHR": rd("validation_places_vs_chr.tsv"),
    "Correlation pairs": rd("correlation_pairs.tsv"),
    "Variance explained": rd("variance_explained.tsv"),
    "Moran's I": rd("morans_I.tsv"),
    "State concentration": rd("state_concentration.tsv"),
    "Shared-gene overlap": rd("shared_gene_overlap.tsv"),
    "DOID-MONDO map": rd("doid_mondo_map.tsv"),
    "Methods & Rules": methods,
}
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    for name, df in sheets.items():
        df.round(4).to_excel(xw, sheet_name=name[:31], index=False)

wb = load_workbook(OUT)
TIER = {"A": "F4B183", "B": "F8CBAD", "C": "FCE4D6"}
for ws in wb.worksheets:
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name="Arial", size=10)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        w = max(len(str(c.value or "")) for c in col[:200])
        ws.column_dimensions[col[0].column_letter].width = min(max(10, w + 2), 60)
ws = wb["Ranked Results"]
tcol = [c.value for c in ws[1]].index("tier") + 1
for r in range(2, ws.max_row + 1):
    t = ws.cell(r, tcol).value
    if t in TIER:
        for c in ws[r]:
            c.fill = PatternFill("solid", fgColor=TIER[t])
m = wb["Methods & Rules"]
m.column_dimensions["B"].width = 120
for row in m.iter_rows(min_row=2):
    row[1].alignment = Alignment(wrap_text=True, vertical="top")
wb.save(OUT)
print(OUT)

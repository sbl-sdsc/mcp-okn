"""Build the delivered MS-2026-11-19 report package from data/ (written by run_analysis.py):
fills the {{key}} template from data/stats.json, renders the HTML with
build_report_from_markdown (KPI cards + interactive ranked table + inline folium map),
and writes the multi-sheet Excel workbook.  Run from the study folder:
    python scripts/build_report.py
"""
import json, os, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build_report_html import build_report_from_markdown, candidate_table, kpis_from_stats, fill_stats, check_report_parity

STUDY = "MS-2026-11-19"
stats = json.load(open("data/stats.json"))
tmpl = open(f"data/{STUDY}_report.template.md", encoding="utf-8").read()
refs = open("data/references.md", encoding="utf-8").read().strip()
md = fill_stats(tmpl.replace("{{REFERENCES}}", refs), stats)
md_path = f"{STUDY}_report.md"
open(md_path, "w", encoding="utf-8").write(md)

# ---- interactive ranked table
r = pd.read_csv("data/ranked_results.csv")
r["sources_list"] = r.sources.fillna("").map(lambda s: [x for x in s.split("; ") if x])
r["drug_target"] = r.prokn_drug_target.map({True: "yes", False: "no"})
r["ncRNA_flag"] = r.ncRNA.map({True: "ncRNA", False: "protein-coding"})
r["score"] = r.score.round(2)
r["pigean_score"] = r.pigean_score.round(2)
r["gxa"] = r.gxa_up.astype(str) + "↑ / " + r.gxa_down.astype(str) + "↓"
rows = r.fillna("").to_dict("records")
for d in rows:
    d["sources_list"] = d["sources_list"] or []
cols = [("rank", "rank"), ("symbol", "gene"), ("tier", "tier"), ("score", "score"), ("n_sources", "sources (n)"),
        ("pigean_score", "PIGEAN"), ("gxa", "GXA disease DE"), ("gxa_ifn_response", "IFN-β DE"),
        ("drug_target", "drug target"), ("drugs", "prokn drugs"), ("max_drug_phase", "max phase"),
        ("ppi_degree_core", "PPI degree"), ("ncRNA_flag", "class")]
table = candidate_table(rows, cols, search_keys=["symbol", "drugs", "sources"], numeric_keys=["rank", "score", "pigean_score", "ppi_degree_core", "max_drug_phase", "gxa_ifn_response"],
                        page_size=25, default_sort="rank", extra_filters=[("tier", "tier"), ("drug_target", "drug target"), ("ncRNA_flag", "class")],
                        sources_col=("n_sources", "sources_list"))
kpis = kpis_from_stats(stats, [("n_kgs", "OKN KGs integrated"), ("n_genes", "genes with MS evidence"), ("tier_A", "tier-A genes"),
                               ("go_sig", "GO BP terms FDR<0.05"), ("re_sig", "Reactome pathways FDR<0.05"),
                               ("prokn_compounds", "MS-indicated compounds"), ("prev_countries", "countries with prevalence"),
                               ("rho_lat", "ρ prevalence vs |latitude|")])
html_path = f"{STUDY}_report.html"
build_report_from_markdown(md_path, html_path, kpis=kpis, table=table, stats=stats)
# splice the interactive folium map (an <iframe srcdoc>) at its marker
import html as _h
doc = open("data/prevalence_map.html", encoding="utf-8").read()
iframe = ('<div class="okn-map"><iframe title="MS prevalence by country" srcdoc="' + _h.escape(doc, quote=True) +
          '" loading="lazy" style="width:100%;height:480px;border:1px solid #e5e7eb;border-radius:9px;margin:10px 0"></iframe></div>')
page = open(html_path, encoding="utf-8").read()
assert "<!-- PREVALENCE_MAP -->" in page
open(html_path, "w", encoding="utf-8").write(page.replace("<!-- PREVALENCE_MAP -->", iframe))
check_report_parity(md_path, html_path)

# ---- workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
sheets = [("Ranked Results", "ranked_results.csv"), ("Subtypes", "subtypes.csv"), ("ID crosswalk", "subtype_crosswalk.csv"),
          ("KG contributions", "kg_contributions.csv"), ("Gene evidence", "gene_evidence_matrix.csv"),
          ("GXA DE", "gxa_differential_expression.csv"), ("GXA recurrent", "gxa_recurrent_genes.csv"),
          ("DMT coverage", "dmt_kg_coverage.csv"), ("Drug landscape", "drug_landscape.csv"), ("Drug targets", "prokn_drug_targets.csv"),
          ("Repurposing", "repurposing_candidates.csv"), ("Phenotypes curated", "phenotypes_curated.csv"),
          ("Phenotypes oard", "phenotypes_oard.csv"), ("Epidemiology", "epidemiology_by_country.csv"),
          ("Prevalence by continent", "prevalence_by_continent.csv"), ("Risk factors", "risk_factors.csv"),
          ("GO BP enrichment", "enrichment_go_bp.csv"), ("Reactome enrichment", "enrichment_reactome.csv"),
          ("PPI hubs", "ppi_hubs.csv"), ("Mechanistic modules", "mechanistic_modules.csv")]
methods = pd.DataFrame([
    ("Study", "Integrative multi-KG map of multiple sclerosis (MS-2026-11-19); model claude-opus-5-5; OKN federated SPARQL (FRINK)."),
    ("Framing", "Hypothesis generation from curated, genetic, text-mined and observational associations; not causal or clinical inference."),
    ("Disease anchor", "MONDO_0005301 (= DOID:2377, UMLS C0026769, MeSH D009103, ICD-10 G35) + ubergraph subclass closure (RRMS, SPMS, PPMS, PRMS, chronic progressive, Marburg, paediatric)."),
    ("Joins", "DOID<->MONDO via ubergraph skos:exactMatch; UMLS via oboInOwl:hasDbXref; genes on Entrez/Ensembl; prokn gene symbol rdfs:label -> UniProt (SIO_010078); countries on ISO3 (wikidata P298/P625); wikidata MS via P699 DOID:2377."),
    ("Evidence sources (7)", "spoke-okn, rdkg (curated); digcfdekg PIGEAN, wikidata P2293 (genetic); biomarkerkg (analyte); gene-expression-atlas-okn disease contrasts (adj p<=0.05, |log2FC|>=1); prokn drug->target. nestkg PPI degree is a ranking weight only."),
    ("Tiers", "A: >=4 sources, or >=3 incl. curated+genetic; B: 3 sources, or curated+genetic (2); C: other 2-source; D: 1 source."),
    ("Score", "n_sources + 0.25*log1p(PPI degree) + 0.05*min(PIGEAN,10)."),
    ("Enrichment", "Hypergeometric + BH FDR; foreground = spoke-okn U rdkg U digcfdekg PIGEAN>=3 symbols resolving to prokn genes; background = prokn genes with GO BP (N=7663) or Reactome (N=6032) annotation; terms tested if k>=5 (GO) / k>=6 (Reactome)."),
    ("Expression", "GXA disease contrasts: E-GEOD-66573, E-GEOD-77598, E-MTAB-2973, E-MTAB-69; IFN-beta contrasts E-GEOD-26104, E-GEOD-14386 (kept separate). Y-chromosome genes removed."),
    ("Epidemiology", "spoke-okn IHME 2019 prevalence (percent x 1000 = per 100k); WHO GHE deaths/population x 1e5; Spearman correlations; partial correlation via rank residuals on GDP (Natural Earth, external)."),
    ("Analyst mappings", "ChEMBL complex targets -> member genes; biomarkerkg analyte names APOA1/SPHK1/SPHK2/RMRP; mechanistic modules; risk-factor themes (keyword grouping)."),
    ("Excluded queries", "q15 and q34 (BIND scoping error), q23 (superseded by q24)."),
    ("Abbreviations", "BH Benjamini-Hochberg; CIS clinically isolated syndrome; CSF cerebrospinal fluid; DE differential expression; DMT disease-modifying therapy; EHR electronic health record; FDR false-discovery rate; GO BP Gene Ontology biological process; GXA Gene Expression Atlas; HP Human Phenotype Ontology; IFN interferon; IHME Institute for Health Metrics and Evaluation; KG knowledge graph; LOR log-odds ratio; MS multiple sclerosis; NfL neurofilament light; PIGEAN polygenic gene prioritisation score; PPI protein-protein interaction; PPMS/PRMS/RRMS/SPMS MS clinical courses; SDoH social determinants of health; WHO GHE World Health Organization Global Health Estimates."),
], columns=["item", "rule"])
xlsx = f"{STUDY}_results.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as xw:
    for name, f in sheets:
        pd.read_csv(f"data/{f}").to_excel(xw, sheet_name=name[:31], index=False)
    methods.to_excel(xw, sheet_name="Methods & Rules", index=False)
    lit = [l for l in open(f"{STUDY}_literature_comparison.md", encoding="utf-8").read().split("\n## Claim ")[1:]]
    pd.DataFrame([dict(claim=int(b.split(" ")[0]), title=b.split("\n")[0].split(" — ", 1)[1],
                       concordance=b.split("**Concordance: ")[1].split(".**")[0]) for b in lit]).to_excel(xw, sheet_name="Literature comparison", index=False)
    TF = {"A": "F8CBAD", "B": "FFE699", "C": "BDD7EE", "D": "EDEDED"}
    for ws in xw.book.worksheets:
        for c in ws[1]:
            c.font = Font(name="Arial", bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F4E78")
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = Font(name="Arial", size=10)
        for i, col in enumerate(ws.columns, 1):
            w = max(len(str(c.value or "")) for c in list(col)[:200])
            ws.column_dimensions[get_column_letter(i)].width = min(max(10, w + 2), 60 if ws.title != "Methods & Rules" else 120)
        ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    ws = xw.book["Ranked Results"]
    tcol = [c.value for c in ws[1]].index("tier") + 1
    for row in ws.iter_rows(min_row=2):
        t = row[tcol - 1].value
        if t in TF:
            for c in row[:4]:
                c.fill = PatternFill("solid", fgColor=TF[t])
    for c in xw.book["Methods & Rules"]["B"]:
        c.alignment = Alignment(wrap_text=True, vertical="top")
print("[build_report] wrote", md_path, html_path, xlsx)

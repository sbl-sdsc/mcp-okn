"""Build the multi-sheet Excel workbook."""
import json, pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

S = json.load(open('Liver-Lipid/data/stats.json'))
core = pd.read_csv('Liver-Lipid/data/ranked_candidates.tsv', sep='\t')
core['sources'] = core.sources.str.replace(r"[\[\]']", "", regex=True)
ranked = core[['rank','humanSymbol','hEntrez','mouse_symbols','log2fc','log2fc_mean','adj_p_value',
               'direction','n_datasets','osd_sources','liver_disease_rdkg','nafld_trait_digcfdekg',
               'any_liver_trait_digcfdekg','liver_disease_spokeokn','lipid_pathway','phenotype_linked',
               'rdkg_diseases','n_mouse_map','sign_flip','n_sources','sources','score','tier']].rename(columns={
    'humanSymbol':'human_symbol','hEntrez':'human_entrez','log2fc':'log2FC (max-rule)',
    'log2fc_mean':'log2FC (mean-rule)','adj_p_value':'adj_p','osd_sources':'datasets',
    'n_mouse_map':'n_mouse_orthologs'})

inventory = pd.DataFrame([
 ["GLDS-25","STS-135","C57BL/6","13 d","DNA microarray","OSD-25","yes",S['osd25_measured'],S['deg_osd25']],
 ["GLDS-47","RR-1 CASIS (SpaceX-4)","C57BL/6","21 d","RNA-seq","OSD-47","yes",S['osd47_measured'],S['deg_osd47']],
 ["GLDS-137","RR-3 (SpaceX-8)","BALB/c","42 d","RNA-seq","OSD-137","yes",S['osd137_measured'],S['deg_osd137']],
 ["GLDS-168","RR-1 + RR-3 pooled","C57BL/6","37 d","RNA-seq","OSD-168",
  f"no - all {S['osd168_liver_sfgc_assays']} liver SF-vs-GC assays confounded (cross-mission / spike-in)","excluded","excluded"],
], columns=["paper dataset","mission","strain","duration","platform","spoke-genelab study",
            "clean liver contrast","stored DE rows","DEGs"])

methods = pd.DataFrame([
 ["Study", "Reproduction of Beheshti et al. 2019, Sci Rep 9:19195 (PMID 31844325, doi 10.1038/s41598-019-55869-2)"],
 ["Endpoint", "OKN federated SPARQL (mcp-okn)"],
 ["Knowledge graphs", "spoke-genelab v0.0.2 · prokn v0.0.5 · rdkg v0.0.1 · digcfdekg v0.0.1 · spoke-okn v0.0.6 · oard-kg v0.0.3 · ubergraph v0.0.2"],
 ["Contrast rule", "Space Flight (arm 1) vs Ground Control (arm 2); flight and ground arms must carry identical covariates after stripping condition labels/codes; material_id_1 = material_id_2. Positive log2FC = up in flight."],
 ["DEG threshold", "adj_p <= 0.05 AND |log2FC| >= 1 (the original used FC >= 1.2; see the threshold-sensitivity sheet)"],
 ["Tissue", "liver, UBERON:0002107"],
 ["Ortholog rule", "spoke-genelab IS_ORTHOLOG_MGiG; collapsed one row per human gene by max |log2FC|, mean-rule carried as a sensitivity check"],
 ["Enrichment", "Hypergeometric over-representation + Benjamini-Hochberg FDR, k >= 3, K >= 5, against an EXPLICIT background: measured genes that prokn annotates (GO N=2160, Reactome N=1720)"],
 ["Disease gene sets", "curated: rdkg biolink:related_to under ubergraph MONDO:0005154 closure. broad: digcfdekg reified geneToTrait. third supplier: spoke-okn ASSOCIATES_DaG under ubergraph DOID:409 closure"],
 ["Phenotype route", "gene -> disease -> HP (no direct gene->HP edge in the federation); oard-kg queried with biolink:subject and biolink:object UNIONed"],
 ["Scoring", "3.0*(n_datasets-1) + 1.5*min(|log2FC|,4) + 2.5*rdkg_liver + 2.0*spoke-okn_liver_DOID(1.0 after correction) + 2.0*NAFLD_trait + 1.0*other_liver_trait + 1.5*lipid_pathway + 1.0*phenotype + 0.5*(n_sources-1)"],
 ["Tiers", "A: score >= 8 · B: 5 <= score < 8 · C: score < 5"],
 ["Level of inference", "Hypothesis generation. Mouse-to-human claims are ortholog-inferred; disease/trait/phenotype links are observational associations, not causal."],
 ["Analyses skipped", "drug/target linkage (scope decision) · chemical/adverse-outcome (no exposure in the question) · microbiome/taxon (no liver assay in the paper-matched studies) · geospatial (no geography for a mouse liver assay)"],
 ["Abbreviations", "ORA over-representation analysis · GSEA gene set enrichment analysis · DEG differentially expressed gene · FDR false-discovery rate (Benjamini-Hochberg) · log2FC log2 fold change · FC fold change · GO Gene Ontology · BP biological process · NAFLD non-alcoholic fatty liver disease · MASLD/MASH metabolic dysfunction-associated steatotic liver disease/steatohepatitis · HP Human Phenotype Ontology · MONDO Mondo Disease Ontology · DOID Disease Ontology · EFO Experimental Factor Ontology · UBERON Uber-anatomy ontology · OSD/GLDS NASA Open Science Data Repository / GeneLab Data System accession · RR Rodent Research · STS Space Transportation System · CASIS Center for the Advancement of Science in Space · IPA Ingenuity Pathway Analysis · KG knowledge graph · PPAR peroxisome proliferator-activated receptor"],
], columns=["item","specification"])

go   = pd.read_csv('Liver-Lipid/data/enrichment_go_bp.tsv', sep='\t')[['id','label','K','k','n','N','expected','fold','p','fdr']]
rx   = pd.read_csv('Liver-Lipid/data/enrichment_reactome.tsv', sep='\t')[['id','label','K','k','n','N','expected','fold','p','fdr']]
dis  = pd.DataFrame([
 ["rdkg — curated MONDO liver disease (MONDO:0005154 subtree)", S['rdkg_K'], S['rdkg_k'], S['human_core'], S['bg_human'], S['rdkg_expected'], S['rdkg_fold'], 0.0074, "significant"],
 ["digcfdekg — EFO 'non-alcoholic fatty liver disease' trait set", S['nafld_K'], S['nafld_k'], S['human_core'], S['bg_human'], 2.83, S['nafld_fold'], 0.000462, "significant (FDR 0.0074 over 16 trait sets)"],
 ["spoke-okn — DOID:409 'liver disease' association bucket", S['sok_K'], S['sok_k'], S['human_core'], S['bg_human'], 11.47, S['sok_fold'], 0.7238, "null — a coarse, permissive set"],
], columns=["gene set (supplier)","K","k","n","N","expected","fold","p","reading"])
trait = pd.read_csv('Liver-Lipid/data/enrichment_digcfdekg_traits.tsv', sep='\t')[['category','K','k','n','N','expected','fold','p','fdr']]
sens  = pd.read_csv('Liver-Lipid/data/enrichment_threshold_sensitivity.tsv', sep='\t')[['threshold','family','id','label','K','k','n','N','expected','fold','p','fdr']]
de    = pd.read_csv('Liver-Lipid/data/liver_de_measured.tsv', sep='\t')[['osd','symbol','entrez','log2fc','adj_p_value','group_mean_1','group_mean_2']]
pheno = pd.read_csv('Liver-Lipid/data/oard_liver_phenotypes.tsv', sep='\t')[['mondo','disease_label','hp','phenotype_label']]

SHEETS = [("Ranked Results", ranked), ("Dataset Inventory", inventory),
          ("Enrichment GO BP", go), ("Enrichment Reactome", rx),
          ("Liver Disease Sets", dis), ("digcfdekg Trait Sets", trait),
          ("Threshold Sensitivity", sens), ("Liver Phenotypes HP", pheno),
          ("Measured DE Payload", de), ("Methods & Rules", methods)]

with pd.ExcelWriter('Liver-Lipid/Liver-Lipid_results.xlsx', engine='openpyxl') as xw:
    for name, df in SHEETS:
        df.to_excel(xw, sheet_name=name[:31], index=False)
    wb = xw.book
    hdr_fill = PatternFill("solid", fgColor="1F3864")
    tier_fill = {"A": PatternFill("solid", fgColor="C6E7D8"),
                 "B": PatternFill("solid", fgColor="D6E4F5"),
                 "C": PatternFill("solid", fgColor="EFEFEF")}
    for name, df in SHEETS:
        ws = wb[name[:31]]
        for c in ws[1]:
            c.font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
            c.fill = hdr_fill
            c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 30
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for j, col in enumerate(df.columns, start=1):
            width = min(max(12, int(df[col].astype(str).str.len().head(300).max() or 12) + 2), 62)
            ws.column_dimensions[get_column_letter(j)].width = width
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = Font(name="Arial", size=10)
                c.alignment = Alignment(vertical="top", wrap_text=(name == "Methods & Rules"))
        if name == "Ranked Results":
            ti = list(df.columns).index("tier") + 1
            for r in range(2, ws.max_row + 1):
                t = ws.cell(row=r, column=ti).value
                if t in tier_fill:
                    for c in ws[r]:
                        c.fill = tier_fill[t]
        if name == "Methods & Rules":
            ws.column_dimensions["B"].width = 110
print("[workbook] sheets:", [n for n, _ in SHEETS])

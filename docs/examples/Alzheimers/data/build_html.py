import sys, json, warnings; warnings.filterwarnings("ignore")
ROOT="/sessions/focused-magical-ramanujan/mnt/outputs/Alzheimers_OKN/"
sys.path.insert(0, ROOT+"scripts"); sys.path.insert(0, ROOT+"data")
import pandas as pd, numpy as np
from build_report_html import (build_report_from_markdown, candidate_table,
                               kpis_from_stats, fill_stats)
from make_figures import fig8_map_html

stats = json.load(open(ROOT+"data/stats.json"))
rank  = pd.read_csv(ROOT+"data/ad_ranked_genes.csv").fillna("")

SRC_SHORT = {"spoke-okn":"spoke-okn","digcfdekg":"digcfdekg","prokn":"prokn",
             "biomarkerkg":"biomarkerkg","gene-expression-atlas-okn":"gene-expr-atlas","rdkg":"rdkg"}
rows=[]
for _,r in rank.iterrows():
    srcs=[SRC_SHORT.get(s,s) for s in str(r.sources).split(";") if s]
    rows.append(dict(
        gene=r.gene, tier=r.tier, biotype=r.biotype,
        n_sources=int(r.n_sources), src_list=srcs,
        evidence_types=str(r.evidence_types).replace(";", " · "),
        n_evidence_types=int(r.n_evidence_types),
        pigean=("" if r.pigean_score=="" else round(float(r.pigean_score),2)),
        variants=int(r.n_uniprot_variants),
        de_regions=int(r.de_regions),
        de_direction=(r.de_direction if r.de_direction else "—"),
        druggable=("yes" if int(r.druggable)==1 else "no"),
        drugs=(str(r.drugs)[:70] if r.drugs else "—"),
        score=float(r.score)))

columns=[("gene","gene"),("tier","tier"),("biotype","biotype"),("n_sources","sources (n)"),
         ("evidence_types","evidence types"),("n_evidence_types","ev. types"),
         ("pigean","PIGEAN"),("variants","UniProt variants"),("de_regions","DE regions"),
         ("de_direction","DE direction"),("druggable","drugged"),("drugs","drug / probe"),
         ("score","score")]
table = candidate_table(
    rows, columns,
    search_keys=["gene","evidence_types","drugs","biotype"],
    numeric_keys=["n_sources","n_evidence_types","pigean","variants","de_regions","score"],
    page_size=25, default_sort=("score","desc"),
    extra_filters=[("tier","confidence tier"),("biotype","biotype"),
                   ("druggable","drugged"),("de_direction","DE direction")],
    sources_col=("n_sources","src_list"))

kpis = kpis_from_stats(stats, [
    ("n_kgs_queried","knowledge graphs integrated"),
    ("n_genes_total","AD-implicated genes",","),
    ("n_tierA","Tier-A consensus genes"),
    ("n_go_sig","GO terms at FDR<0.05"),
    ("n_rx_sig","Reactome pathways at FDR<0.05"),
    ("n_drugs","AD-indicated compounds"),
    ("n_biomarkers","biomarkers",","),
    ("n_countries","countries with prevalence"),
])

# --- interactive OSM map, spliced into §6.5 ---
m = fig8_map_html()
# folium's get_root().render() returns a COMPLETE html document (<!DOCTYPE><html><head><body>).
# Splicing that into the report body produces nested <html>/<head>/<body>, which browsers mangle —
# it silently truncated the report at this point. Wrap it in an iframe srcdoc instead, which is the
# only safe way to inline a self-contained Leaflet document.
import html as _html
_doc = _html.escape(m.get_root().render(), quote=True)
map_html = ('<div class="figure"><div style="border:1px solid #ddd;border-radius:6px;overflow:hidden">'
            + f'<iframe srcdoc="{_doc}" style="width:100%;height:520px;border:0" '
              'loading="lazy" title="Global AD prevalence, 2019 (OpenStreetMap)"></iframe>' +
            '</div><div class="figcap"><b>Interactive Figure 8C. Global AD prevalence, 2019 '
            '(OpenStreetMap).</b> Every country is clickable: the popup gives the point estimate, '
            'the reported interval, the year and the source predicate; marker size and colour both '
            'encode prevalence (magma_r ramp, darker = higher). Coordinate source: author-supplied '
            'ISO-3166 country centroids; prevalence values from <code>spoke-okn</code> reified '
            '<code>PREVALENCE_DpL</code> statements for <code>DOID:10652</code>. '
            'Tiles © OpenStreetMap contributors.</div></div>')

md = ROOT+"Alzheimers_report.md"
# keep the delivered .md standalone (numbers filled in place)
raw = open(md).read()
open(md,"w").write(fill_stats(raw, stats))

out = ROOT+"Alzheimers_report.html"
html = build_report_from_markdown(md, out, kpis=kpis, table=table, stats=stats)
# splice the interactive map right after Figure 8's caption
s = open(out).read()
anchor = "Tiles © OpenStreetMap" if False else "interactive OpenStreetMap version of these data"
i = s.find("</div>", s.find(anchor))
if i > 0:
    s = s[:i+6] + map_html + s[i+6:]
    open(out,"w").write(s)
    print("interactive map spliced into §6.5")
else:
    print("WARNING: map anchor not found")

#!/usr/bin/env python3
"""Build the self-contained interactive HTML MS knowledge-map report."""

import base64
import csv
import json
from pathlib import Path

OUT = "/sessions/stoic-charming-ride/mnt/MS"


def b64(p):
    """Return a PNG file encoded as a base64 data URI."""
    with Path(p).open("rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


fig = {
    n: b64(f"{OUT}/figures/{n}.png")
    for n in [
        "fig1_cross_source_corroboration",
        "fig2_evidence_entity_breakdown",
        "fig3_gene_pathway_drug_network",
        "fig4_top_gene_matrix",
    ]
}
with Path(f"{OUT}/MS_knowledge_map_findings.csv").open() as f:
    rows = list(csv.DictReader(f))
stats = json.loads(Path(f"{OUT}/ms_stats.json").read_text())
DATA = json.dumps(rows)

html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Multiple Sclerosis Knowledge Map — Proto-OKN</title>
<style>
:root{{--blue:#2E86AB;--green:#3B8C4D;--orange:#F18F01;--purple:#A23B72;--red:#C0392B;--ink:#1c2733;--muted:#6b7783;--line:#e3e8ee;--bg:#f7f9fb}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}}
header{{background:linear-gradient(135deg,#1c2733,#2E86AB);color:#fff;padding:34px 40px}}
header h1{{margin:0 0 6px;font-size:26px}}
header p{{margin:2px 0;opacity:.9;font-size:14px}}
.wrap{{max-width:1180px;margin:0 auto;padding:26px 40px 70px}}
h2{{font-size:20px;margin:34px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--line)}}
h3{{font-size:16px;margin:22px 0 8px;color:#22303c}}
.kpis{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:22px 0}}
.kpi{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.kpi .n{{font-size:26px;font-weight:700;color:var(--blue)}}
.kpi .l{{font-size:11.5px;color:var(--muted);margin-top:3px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.badge{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;color:#fff}}
.b-cur{{background:var(--blue)}}.b-stat{{background:var(--green)}}.b-meas{{background:var(--orange)}}.b-path{{background:var(--purple)}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{background:#eef3f7;position:sticky;top:0;cursor:pointer;user-select:none;white-space:nowrap}}
th:hover{{background:#e0e9f0}}
tr:hover td{{background:#f2f7fb}}
img{{max-width:100%;border:1px solid var(--line);border-radius:10px;background:#fff}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0;align-items:center}}
input,select{{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px}}
input#q{{flex:1;min-width:220px}}
.tier1{{color:var(--red);font-weight:700}}.tier2{{color:var(--orange);font-weight:600}}
.pill{{font-size:11px;padding:1px 7px;border-radius:10px;background:#eef3f7;color:#33566b;margin-right:3px;white-space:nowrap}}
.muted{{color:var(--muted);font-size:12.5px}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:900px){{.kpis{{grid-template-columns:repeat(3,1fr)}}.two{{grid-template-columns:1fr}}.wrap{{padding:20px}}}}
.note{{background:#FFF6E6;border:1px solid var(--orange);border-radius:10px;padding:12px 14px;font-size:13px}}
#tablebox{{max-height:620px;overflow:auto;border:1px solid var(--line);border-radius:10px}}
code{{background:#eef3f7;padding:1px 5px;border-radius:5px;font-size:12px}}
</style></head><body>
<header>
<h1>An Evidence-Backed Map of Multiple Sclerosis Biology</h1>
<p>Integrated across seven Proto-OKN federated knowledge graphs · anchored on multiple sclerosis (MONDO:0005301) + 7 subtypes</p>
<p>Prepared for Peter · 2026-07-03 · model claude-opus-4-8 · Proto-OKN federated SPARQL</p>
</header>
<div class="wrap">

<div class="kpis">
<div class="kpi"><div class="n">474</div><div class="l">total findings</div></div>
<div class="kpi"><div class="n">323</div><div class="l">MS-associated genes</div></div>
<div class="kpi"><div class="n">475</div><div class="l">differentially-active genes</div></div>
<div class="kpi"><div class="n">33</div><div class="l">pathways / gene sets</div></div>
<div class="kpi"><div class="n">180</div><div class="l">indicated compounds</div></div>
<div class="kpi"><div class="n">8</div><div class="l">biomarker findings</div></div>
</div>

<div class="card">
<b>Highest-confidence core.</b> <span class="tier1">HLA-DRB1, IL2RA, IL7R, TYK2, STAT4, CD6, CD40, CD58, CBLB, IL12A, IFNG, TNFRSF1A, TNFSF14</span> are each corroborated by all three independent gene sources (Tier&nbsp;1). A further 60 genes are supported by two sources.
Strongest statistical signals (digcfdekg PIGEAN/EAGGL, GWAS): CD28 (10.6), IL7R (10.0), IKZF3 (9.76), HLA-A (9.26), CD27 (9.07).
Evidence types are kept separate: <span class="badge b-cur">curated link 247</span>
<span class="badge b-stat">statistical/genetic 234</span>
<span class="badge b-meas">measured activity 83</span>
<span class="badge b-path">pathway membership 17</span>
</div>

<h2>Sources used</h2>
<div class="muted">Seven KGs supplied MS evidence; <code>ubergraph</code> was the ontology bridge only. Versions are the exact Proto-OKN releases queried 2026-07-03.</div>
<table style="margin-top:10px"><thead><tr><th>KG</th><th>Ver</th><th>Role</th><th>Entity types</th><th>Disease ID</th></tr></thead><tbody>
<tr><td>spoke-okn</td><td>v0.0.6</td><td>curated disease→gene, drug→disease</td><td>genes, drugs</td><td>DOID</td></tr>
<tr><td>rdkg</td><td>v0.0.1</td><td>curated gene / phenotype / contraindicated &amp; risk drug</td><td>genes, clinical, drugs</td><td>MONDO / grouped nodes</td></tr>
<tr><td>digcfdekg</td><td>v0.0.1</td><td><b>statistical</b> gene–trait + gene sets + factors (PIGEAN/EAGGL, GWAS)</td><td>genes, gene sets</td><td>MONDO / EFO</td></tr>
<tr><td>prokn</td><td>v0.0.5</td><td><b>drug indications</b> (ChEMBL); pathway hub (no curated MS genes)</td><td>drugs</td><td>MONDO/Orphanet (exactMatch)</td></tr>
<tr><td>gene-expression-atlas-okn</td><td>v0.0.3</td><td><b>measured</b> differential activity + cell type</td><td>altered activity</td><td>MONDO/EFO</td></tr>
<tr><td>biomarkerkg</td><td>v0.0.2</td><td>clinical biomarkers + specimen</td><td>biomarkers</td><td>DOID</td></tr>
<tr><td>ubergraph</td><td>v0.0.2</td><td>subtype expansion + ID crosswalks (bridge)</td><td>ontology</td><td>all</td></tr>
</tbody></table>
<div class="muted" style="margin-top:8px">Checked but not contributory: <code>oard-kg</code> (no MS phenotype edges), <code>pankgraph</code> (no MS node), <code>ncipidkg</code>, <code>biobricks-aopwiki</code>, <code>nde</code>, <code>biohealth</code>.</div>

<h2>Cross-source corroboration</h2>
<img src="{fig["fig1_cross_source_corroboration"]}" alt="corroboration">
<div class="two" style="margin-top:16px">
<div><img src="{fig["fig4_top_gene_matrix"]}" alt="matrix"></div>
<div><img src="{fig["fig2_evidence_entity_breakdown"]}" alt="evidence"></div>
</div>

<h2>Gene–pathway–drug mechanistic map</h2>
<div class="muted">Entities are those actually retrieved from the sources (genes: spoke/rdkg/digcfdekg; drugs: prokn indications; interferon module: GXA measured), placed onto the established MS immune modules.</div>
<img style="margin-top:10px" src="{fig["fig3_gene_pathway_drug_network"]}" alt="network">

<h2>Findings by entity type</h2>
<div class="card"><b>Genes (association).</b> 3 sources → Tier-1 immune core (HLA-DRB1, IL2RA, IL7R, TYK2, STAT4, CD6, CD40, CD58…); CD28 carries the strongest statistical weight (10.6). Non-coding involvement is minimal in the association layer (one lncRNA) — an MS/AD contrast — and appears mostly in the measured layer.</div>
<div class="card"><b>Genes with altered activity (GXA, measured, with cell type).</b> 475 differentially-expressed genes in MS <b>peripheral immune cells</b> (CD4⁺/CD8⁺ T cells, monocytes, neutrophils, B cells, whole blood). Type-I-interferon genes UP (MX1/2, OAS2/3, RSAD2, IFI44/IFIT1), B-cell/plasma genes UP (IGHM, TNFRSF17, MZB1, PAX5), monocyte/complement genes DOWN (CD14, CD163, C1QB, C3).</div>
<div class="card"><b>Pathways / gene sets (digcfdekg).</b> Adaptive-immune throughout: CTLA4, TH17 commitment, TH1/TH2, TCR-signalling, IL-2 signalling, allograft rejection, B-cell differentiation — plus a lipoprotein-metabolism factor.</div>
<div class="card"><b>Drugs.</b> Kept separate by relationship: <b>180 indicated/investigated</b> compounds (prokn/ChEMBL — alemtuzumab, briakinumab, BIIB-091/BTK, baclofen, amantadine, high-dose biotin, cannabinoids); <b>2 contraindicated</b> (rdkg); <b>environmental risk factors</b> (tobacco, solvents, lead, mercury); <b>3 "treats"</b> artifacts in spoke-okn (a limitation).</div>
<div class="card"><b>Clinical features &amp; biomarkers.</b> rdkg: CNS demyelination, spasticity, paraesthesia, ataxia, diplopia, bladder dysfunction, depression (12 HP terms). biomarkerkg: 53 specimen-tagged records (CSF/plasma/serum/urine) + an S1P/IFN-γ/IL-17 analyte panel (SPHK1, SPHK2, S1PR1, S1PR5).</div>
<div class="note"><b>Flagged undercount — genetic variants.</b> No MS-anchored variant-entity layer exists in these KGs; variant signal survives only at gene level via digcfdekg's GWAS-derived statistics. HLA-DRB1*15:01, TYK2 P1104A, and IL7R/TNFRSF1A functional variants are represented by their genes, not as variant records.</div>

<h2>Full annotated findings — interactive (474 rows)</h2>
<div class="muted">Search, filter by entity type / evidence type, and click any column header to sort. Full CSV: <code>MS_knowledge_map_findings.csv</code>.</div>
<div class="controls">
<input id="q" placeholder="Search entity, relationship, notes…">
<select id="fType"><option value="">All entity types</option></select>
<select id="fEv"><option value="">All evidence types</option></select>
<select id="fTier"><option value="">All tiers</option></select>
<span class="muted" id="count"></span>
</div>
<div id="tablebox"><table id="tbl"><thead><tr id="hdr"></tr></thead><tbody></tbody></table></div>

<h2 style="margin-top:34px">Caveats &amp; reproducibility</h2>
<div class="muted">
Variants are severely undercounted (no variant-entity layer); non-coding genes are undercounted in the association layer; the GXA measured layer is peripheral blood only and confounded by IFN-β treatment and sex-chromosome artifacts; prokn contributes no curated MS genes (3-source ceiling) and its drug names are mostly ChEMBL-ID-only; spoke-okn TREATS is near-empty; biomarkerkg analytes are unlabelled for 52 of 53 records; oard-kg / pankgraph / ncipidkg / biobricks-aopwiki / nde / biohealth added no MS rows in scope.
Every SPARQL query (verbatim, with graphs hit and row counts) is preserved in <code>MS_analysis_transcript.md</code>.
</div>

</div>
<script>
const DATA={DATA};
const COLS=["entity_type","entity","biotype","relationship","sources","n_sources","evidence_types","best_score","score_type","tissue_celltype","confidence_tier","notes"];
const hdr=document.getElementById('hdr');
COLS.forEach(c=>{{const th=document.createElement('th');th.textContent=c;th.onclick=()=>sortBy(c);hdr.appendChild(th);}});
const tbody=document.querySelector('#tbl tbody');
const fType=document.getElementById('fType'),fEv=document.getElementById('fEv'),fTier=document.getElementById('fTier'),q=document.getElementById('q'),count=document.getElementById('count');
[...new Set(DATA.map(r=>r.entity_type))].sort().forEach(v=>fType.add(new Option(v,v)));
[...new Set(DATA.flatMap(r=>r.evidence_types.split(';')).filter(Boolean))].sort().forEach(v=>fEv.add(new Option(v,v)));
[...new Set(DATA.map(r=>r.confidence_tier))].sort().forEach(v=>fTier.add(new Option(v,v)));
let sortCol='n_sources',sortDir=-1;
function sortBy(c){{sortDir=(sortCol===c)?-sortDir:1;sortCol=c;render();}}
function render(){{
 let r=DATA.filter(x=>(!fType.value||x.entity_type===fType.value)&&(!fEv.value||x.evidence_types.includes(fEv.value))&&(!fTier.value||x.confidence_tier===fTier.value));
 const s=q.value.toLowerCase();
 if(s)r=r.filter(x=>(x.entity+x.relationship+x.notes+x.sources+x.tissue_celltype).toLowerCase().includes(s));
 r.sort((a,b)=>{{let x=a[sortCol],y=b[sortCol];const nx=parseFloat(x),ny=parseFloat(y);
   if(!isNaN(nx)&&!isNaN(ny)){{x=nx;y=ny;}}return (x<y?-1:x>y?1:0)*sortDir;}});
 tbody.innerHTML='';
 for(const x of r){{const tr=document.createElement('tr');
   COLS.forEach(c=>{{const td=document.createElement('td');let v=x[c]||'';
     if(c==='sources')v=v.split(';').filter(Boolean).map(s=>`<span class="pill">${{s}}</span>`).join('');
     else if(c==='evidence_types')v=v.split(';').filter(Boolean).map(s=>`<span class="pill">${{s}}</span>`).join('');
     else if(c==='confidence_tier'){{const cl=v.startsWith('T1')?'tier1':v.startsWith('T2')?'tier2':'';td.className=cl;}}
     td.innerHTML=v;tr.appendChild(td);}});
   tbody.appendChild(tr);}}
 count.textContent=r.length+' / '+DATA.length+' findings';
}}
[q,fType,fEv,fTier].forEach(e=>e.addEventListener('input',render));
render();
</script>
</body></html>"""
with Path(f"{OUT}/MS_knowledge_map_report.html").open("w") as f:
    f.write(html)
print("HTML written:", len(html), "chars")

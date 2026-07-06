#!/usr/bin/env python3
import csv, json, base64, os
OUT=os.path.dirname(os.path.abspath(__file__)); FIG=f"{OUT}/figures"
S=json.load(open(f"{OUT}/t2d_stats.json"))
PREV=json.load(open(f"{OUT}/map_state_prevalence.json"))
rows=list(csv.DictReader(open(f"{OUT}/T2D_knowledge_map_findings.csv")))
def b64(p):
    with open(p,"rb") as f: return "data:image/png;base64,"+base64.b64encode(f.read()).decode()
figs={k:b64(f"{FIG}/{k}.png") for k in ["fig1_cross_source_corroboration","fig2_evidence_entity_breakdown",
 "fig3_gene_pathway_drug_network","fig4_top_gene_matrix","fig5_sdoh_correlations","fig6_prevalence_by_state"]}
DATA=json.dumps(rows,separators=(",",":"))
PREVJS=json.dumps(PREV,separators=(",",":"))
sdoh=S["sdoh_correlations"]
sdoh_rows="".join(f"<tr><td>{v}</td><td class='num'>{r:+.3f}</td><td class='num'>{n}</td></tr>" for v,r,n in sdoh)
t1=", ".join(S["tier1_genes"]); t2=", ".join(S["tier2_genes"])
topw="".join(f"<tr><td>{g}</td><td class='num'>{w}</td></tr>" for g,w in S["top_digcfdekg"][:15])
SOURCES=[
 ("spoke-okn","v0.0.6","Curated disease→gene; prevalence by location (CDC PLACES); SDoH by county (County Health Rankings)","genes, prevalence, SDoH"),
 ("rdkg","v0.0.1","Curated T2D-subtype genes + microRNAs; contraindicated drugs; environmental contributors; phenotypes","genes (coding+non-coding), drugs, clinical, exposures"),
 ("digcfdekg (CFDE REVEAL)","v0.0.1","Statistical gene–trait weights + gene sets (PIGEAN/EAGGL, GWAS-derived)","genes, gene sets"),
 ("prokn (Protein KN)","v0.0.5","Curated T2D genes/proteins; drug indications (ChEMBL)","genes/proteins, drugs"),
 ("pankgraph (PanKbase, NIDDK)","v0.0.1","Islet cell-type open-chromatin gene-activity (T2D vs non-diabetic); islet cis-eQTL variants","altered-activity genes, variants, cell types"),
 ("gene-expression-atlas-okn","v0.0.3","Measured differential expression by tissue (islet, retina, liver)","altered-activity genes/programs"),
 ("biomarkerkg","v0.0.2","Curated clinical biomarker records + specimen","biomarkers"),
 ("oard-kg","v0.0.3","Checked — no rows for T2D (rare-disease EHR corpus)","— (none)"),
 ("ubergraph","v0.0.2","Subtype expansion + cross-ontology ID crosswalks (bridge only)","ontology"),
]
src_rows="".join(f"<tr><td><b>{k}</b></td><td class='num'>{v}</td><td>{d}</td><td>{e}</td></tr>" for k,v,d,e in SOURCES)
prevtop="".join(f"<tr><td>{n}</td><td class='num'>{v:.1f}%</td></tr>" for _,n,v in S["prevalence_state"][:8])

html=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Type 2 Diabetes Knowledge Map — Proto-OKN</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
:root{{--blue:#2E86AB;--green:#3B8C4D;--orange:#F18F01;--purple:#A23B72;--red:#C0392B;--ink:#1c2733;--muted:#6b7783;--line:#e3e8ee;--bg:#f7f9fb}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}}
header{{background:linear-gradient(135deg,#123,#2E86AB);color:#fff;padding:34px 40px}}
header h1{{margin:0 0 6px;font-size:26px}} header p{{margin:2px 0;opacity:.9;font-size:14px}}
.wrap{{max-width:1180px;margin:0 auto;padding:26px 40px 70px}}
h2{{font-size:20px;margin:34px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--line)}}
h3{{font-size:16px;margin:22px 0 8px;color:#22303c}}
.kpis{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:22px 0}}
.kpi{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.kpi .n{{font-size:24px;font-weight:700;color:var(--blue)}} .kpi .l{{font-size:11px;color:var(--muted);margin-top:3px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.badge{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;color:#fff}}
.b-cur{{background:var(--blue)}}.b-stat{{background:var(--green)}}.b-meas{{background:var(--orange)}}.b-path{{background:var(--purple)}}.b-epi{{background:var(--red)}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
td.num{{text-align:right;font-variant-numeric:tabular-nums}}
th{{background:#eef3f7;position:sticky;top:0;cursor:pointer;user-select:none;white-space:nowrap}}
th:hover{{background:#e0e9f0}} tr:hover td{{background:#f2f7fb}}
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
#map{{height:520px;border-radius:12px;border:1px solid var(--line);z-index:0}}
code{{background:#eef3f7;padding:1px 5px;border-radius:5px;font-size:12px}}
.legend{{background:#fff;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.2);font-size:12px;line-height:1.6}}
.legend i{{display:inline-block;width:14px;height:14px;margin-right:6px;border-radius:3px;vertical-align:-2px}}
</style></head><body>
<header>
<h1>An Evidence-Backed Map of Type 2 Diabetes Biology</h1>
<p>Integrated across nine Proto-OKN / FRINK federated knowledge graphs · anchored on type 2 diabetes mellitus (MONDO:0005148) + 6 subtypes</p>
<p>Prepared for Peter · 2026-07-05 · model claude-opus-4-8 · FRINK federated SPARQL</p>
</header>
<div class="wrap">

<div class="kpis">
<div class="kpi"><div class="n">{S['n_findings']:,}</div><div class="l">total findings</div></div>
<div class="kpi"><div class="n">{S['n_genes']}</div><div class="l">genes ({S['n_genes_noncoding']} non-coding)</div></div>
<div class="kpi"><div class="n">{S['n_drugs']}</div><div class="l">drug findings</div></div>
<div class="kpi"><div class="n">{S['n_altered_activity']}</div><div class="l">altered-activity</div></div>
<div class="kpi"><div class="n">{S['n_prevalence']}</div><div class="l">geo prevalence</div></div>
<div class="kpi"><div class="n">{S['n_sdoh']}</div><div class="l">SDoH correlations</div></div>
</div>

<div class="card">
<b>Highest-confidence core.</b> <span class="tier1">{t1}</span> are corroborated by all four gene sources (Tier&nbsp;1) — the β-cell K‑ATP / glucokinase / MODY core.
A further {len(S['tier2_genes'])} genes are supported by 3 sources (Tier&nbsp;2): {t2}.
<div style="margin-top:8px">Evidence types kept separate:
<span class="badge b-cur">curated {S['evidence_counts'].get('curated_link',0)}</span>
<span class="badge b-stat">statistical {S['evidence_counts'].get('statistical_association',0)}</span>
<span class="badge b-meas">measured {S['evidence_counts'].get('measured_activity_change',0)}</span>
<span class="badge b-path">pathway {S['evidence_counts'].get('pathway_membership',0)}</span>
<span class="badge b-epi">geospatial {S['evidence_counts'].get('epidemiological',0)}</span></div>
</div>

<h2>Knowledge graphs used</h2>
<div class="muted">Nine Proto-OKN / FRINK knowledge graphs queried on 2026-07-05 (versions from VoID provenance). <code>ubergraph</code> is the ontology bridge only; <code>oard-kg</code> was checked but returned no T2D rows.</div>
<div style="overflow:auto"><table style="margin-top:10px"><thead><tr><th>KG (shortname)</th><th>Version</th><th>Kind of data used in this map</th><th>Entity types supplied</th></tr></thead><tbody>{src_rows}</tbody></table></div>

<h2>Prevalence across the U.S. — interactive OpenStreetMap</h2>
<div class="muted">CDC PLACES age-adjusted diabetes prevalence via <code>spoke-okn</code>, aggregated to state level (parent term "diabetes mellitus", ≈90–95% T2D), rendered on an <b>OpenStreetMap</b> basemap. Marker size &amp; colour ∝ prevalence. Click a marker for detail. A full-screen version is in <code>T2D_prevalence_map.html</code>.</div>
<div id="map" style="margin-top:10px"></div>

<h3 style="margin-top:18px">Prevalence by state (ranked)</h3>
<div class="muted">Static ranking companion to the interactive OpenStreetMap above (no lat/long scatter).</div>
<img src="{figs['fig6_prevalence_by_state']}" alt="prevalence by state" style="margin-top:6px">

<div class="two" style="margin-top:16px">
<div class="card"><h3>Highest-prevalence states ("diabetes belt")</h3>
<table><thead><tr><th>State</th><th class="num">Age-adj. prevalence</th></tr></thead><tbody>{prevtop}</tbody></table></div>
<div class="card"><h3>Strongest social-determinant correlates</h3>
<div class="muted">County-level Pearson r vs diabetes prevalence (n≈3,100 counties)</div>
<table><thead><tr><th>SDoH variable</th><th class="num">r</th><th class="num">n</th></tr></thead>
<tbody>{sdoh_rows}</tbody></table></div>
</div>
<img src="{figs['fig5_sdoh_correlations']}" alt="sdoh" style="margin-top:6px">

<h2>Cross-source corroboration</h2>
<img src="{figs['fig1_cross_source_corroboration']}" alt="corroboration">
<div class="two" style="margin-top:16px">
<div><img src="{figs['fig4_top_gene_matrix']}" alt="matrix"></div>
<div><img src="{figs['fig2_evidence_entity_breakdown']}" alt="evidence">
<div class="card" style="margin-top:14px"><h3>Top statistical signals (digcfdekg PIGEAN weight)</h3>
<table><thead><tr><th>Gene</th><th class="num">weight</th></tr></thead><tbody>{topw}</tbody></table></div></div>
</div>

<h2>Gene–pathway–drug mechanistic map</h2>
<div class="muted">Entities actually retrieved from the sources, placed onto established T2D modules (β-cell K‑ATP/secretion, MODY/islet TFs, insulin signaling/resistance, incretin/GPCR, obesity/adipo-lipid).</div>
<img style="margin-top:10px" src="{figs['fig3_gene_pathway_drug_network']}" alt="network">

<h2>Findings by entity type</h2>
<div class="card"><b>Genes (coding + non-coding).</b> 4 sources → Tier-1 β-cell/MODY core (ABCC8, KCNJ11, GCK, HNF1A/4A/1B, PDX1, SLC2A2, PPARG, IRS1, WFS1); INS carries the strongest statistical weight (10.3); TCF7L2 is the top common-variant gene. 61 non-coding genes — chiefly islet microRNAs (MIR375, MIR29 family).</div>
<div class="card"><b>Drugs.</b> Kept separate by relationship: <b>295 indicated/investigated</b> compounds (prokn/ChEMBL — metformin, SGLT2i, DPP-4i, GLP-1-axis, sulfonylureas, TZDs, α-glucosidase inhibitors); <b>20 contraindicated / caution</b> drugs (rdkg — thiazides, β-blockers, reserpine).</div>
<div class="card"><b>Altered activity + cell type/tissue.</b> pankgraph islet β-cells (CL:0000169): loss of β-cell-identity genes (HNF1A, MTNR1B, FFAR4, GPR119 ↓), gain of stress/inflammation (NUPR1, IRF8, RETN ↑). GXA: inflammatory up-regulation in <b>islet of Langerhans</b> (66↑), <b>retina</b> (13↑), <b>liver</b> (5↑).</div>
<div class="card"><b>Variants.</b> pankgraph supplies ~19,400 islet cis-eQTL SNPs (variant→gene expression) with fine-mapping — a real islet variant layer. But no T2D disease-anchored risk-variant catalogue exists in the federation; GWAS variant signal survives at gene level (digcfdekg).</div>
<div class="card"><b>Environmental contributors (rdkg).</b> 44 exposures linked to diabetes risk — arsenic, cadmium, lead, mercury, bisphenol A, PFOA/PFOS, PCBs, air pollutants.</div>
<div class="note"><b>Scope flags.</b> spoke-okn resolves diabetes only at the <b>parent</b> term (all diagnosed diabetes), inflating single-source gene counts and making the geo/SDoH layers a T2D proxy. pankgraph's curated gene–condition layer is type-1. See report §8.</div>

<h2>Full annotated findings — interactive ({S['n_findings']:,} rows)</h2>
<div class="muted">Search, filter by entity type / evidence type / tier, and click any column header to sort. Full CSV: <code>T2D_knowledge_map_findings.csv</code>.</div>
<div class="controls">
<input id="q" placeholder="Search entity, relationship, notes…">
<select id="fType"><option value="">All entity types</option></select>
<select id="fEv"><option value="">All evidence types</option></select>
<select id="fTier"><option value="">All tiers</option></select>
<span class="muted" id="count"></span>
</div>
<div id="tablebox"><table id="tbl"><thead><tr id="hdr"></tr></thead><tbody></tbody></table></div>

<h2 style="margin-top:34px">Caveats &amp; reproducibility</h2>
<div class="muted">spoke-okn = parent "diabetes mellitus" (T2D proxy); T2D risk-variants undercounted (pankgraph gives islet eQTLs, not disease-anchored variants); pankgraph curated gene–condition layer is type-1; non-coding genes undercounted (symbol heuristic); EFO:0004541 = HbA1c excluded; spoke-okn TREATS layer unreliable (prokn indications used); SDoH/prevalence are ecological (county/state). Every SPARQL query (verbatim) is in <code>T2D_analysis_transcript.md</code>; integration in <code>integrate.py</code>; figures in <code>viz.py</code>.</div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const PREV={PREVJS};
function col(v){{return v>=13?'#7f0000':v>=12?'#b30000':v>=11?'#d7301f':v>=10?'#ef6548':v>=9?'#fc8d59':v>=8?'#fdbb84':'#fdd49e';}}
const map=L.map('map',{{scrollWheelZoom:false}}).setView([39.5,-96],4);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:10,attribution:'© OpenStreetMap contributors'}}).addTo(map);
PREV.forEach(p=>{{ if(p.lat==null)return;
  L.circleMarker([p.lat,p.lng],{{radius:5+(p.prev-7)*2.1,fillColor:col(p.prev),color:'#333',weight:1,fillOpacity:.85}})
   .addTo(map).bindPopup('<b>'+p.name+'</b><br>Age-adjusted diabetes prevalence: <b>'+p.prev.toFixed(1)+'%</b>');}});
const lg=L.control({{position:'bottomright'}});
lg.onAdd=function(){{const d=L.DomUtil.create('div','legend');d.innerHTML='<b>Diabetes prevalence</b><br>'+
 '<i style="background:#7f0000"></i>≥13%<br><i style="background:#d7301f"></i>11–13%<br><i style="background:#fc8d59"></i>9–11%<br><i style="background:#fdd49e"></i>&lt;9%';return d;}};
lg.addTo(map);

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
 tbody.innerHTML='';const frag=document.createDocumentFragment();
 for(const x of r.slice(0,1400)){{const tr=document.createElement('tr');
   COLS.forEach(c=>{{const td=document.createElement('td');let v=x[c]||'';
     if(c==='sources'||c==='evidence_types')v=v.split(';').filter(Boolean).map(s=>`<span class="pill">${{s}}</span>`).join('');
     else if(c==='confidence_tier'){{td.className=v.startsWith('T1')?'tier1':v.startsWith('T2')?'tier2':'';}}
     td.innerHTML=v;tr.appendChild(td);}});
   frag.appendChild(tr);}}
 tbody.appendChild(frag);
 count.textContent=r.length+' / '+DATA.length+' findings';
}}
[q,fType,fEv,fTier].forEach(e=>e.addEventListener('input',render));
render();
</script>
</body></html>"""
open(f"{OUT}/T2D_knowledge_map_report.html","w").write(html)
print("HTML written:", len(html), "bytes")

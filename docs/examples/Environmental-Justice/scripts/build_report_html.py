#!/usr/bin/env python3
"""Render report.html in the Alzheimer's-report visual style.

Gradient header, KPI cards, white content cards, evidence badges, sources table,
embedded figures, and an interactive searchable/sortable/filterable county-burden
explorer. Self-contained (figures base64).
"""

import base64
import json
from pathlib import Path

import pandas as pd

DEST = "/sessions/amazing-focused-bardeen/mnt/Environmental-Justice/EJ_Burden_ProtoOKN"
m = pd.read_csv(DEST + "/data/master_county.csv", dtype={"fips": str})
U = m[m["in_us50"]].copy()


def b64(p):
    """Return a base64 PNG data URI for the image file at path ``p``."""
    return "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()


F1 = b64(DEST + "/figures/fig1_burden_source_matrix.png")
F2 = b64(DEST + "/figures/fig2_correlation_heatmap.png")
F3 = b64(DEST + "/figures/fig3_ranked_counties.png")
F4 = b64(DEST + "/figures/fig4_agreement_coverage.png")


# interactive DATA: one row per US50 county
def num(v, nd=2):
    """Return ``v`` as a float rounded to ``nd`` decimals, or None if missing."""
    return None if pd.isna(v) else round(float(v), nd)


rows = []
for _, r in U.iterrows():
    agr = None if pd.isna(r["burden_agreement"]) else int(r["burden_agreement"])
    rows.append(
        {
            "county": str(r["name"]),
            "state": str(r["state"]),
            "agreement": (agr if agr is not None else 0),
            "burden_index": num(r["burden_index"], 3),
            "epa_fac": (None if pd.isna(r["epa_fac"]) else int(r["epa_fac"])),
            "court_cases": (
                None if pd.isna(r["court_cases"]) else int(r["court_cases"])
            ),
            "svi": num(r["svi"], 3),
            "rucc": (None if pd.isna(r["rucc"]) else int(r["rucc"])),
            "sud_providers": (
                None if pd.isna(r["sud_providers"]) else int(r["sud_providers"])
            ),
            "poverty": num(r["poverty"], 1),
            "uninsured": num(r["uninsured"], 1),
            "diabetes": num(r["diabetes"], 1),
            "obesity": num(r["obesity"], 1),
            "tier": ("T1" if agr == 5 else "T2" if agr == 4 else ""),
        }
    )
rows.sort(key=lambda x: (-x["agreement"], -(x["burden_index"] or 0)))
DATA = json.dumps(rows, separators=(",", ":"))

CSS = """
:root{--blue:#2E86AB;--green:#3B8C4D;--orange:#F18F01;--purple:#A23B72;--red:#C0392B;--teal:#1B7A7A;--ink:#1c2733;--muted:#6b7783;--line:#e3e8ee;--bg:#f7f9fb}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
header{background:linear-gradient(135deg,#1c2733,#2E86AB);color:#fff;padding:34px 40px}
header h1{margin:0 0 6px;font-size:26px}
header p{margin:2px 0;opacity:.9;font-size:14px}
.wrap{max-width:1180px;margin:0 auto;padding:26px 40px 70px}
h2{font-size:20px;margin:34px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--line)}
h3{font-size:16px;margin:22px 0 8px;color:#22303c}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:22px 0}
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.kpi .n{font-size:25px;font-weight:700;color:var(--blue)}
.kpi .l{font-size:11.5px;color:var(--muted);margin-top:3px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;color:#fff;margin:1px 2px}
.b-surv{background:var(--blue)}.b-reg{background:var(--orange)}.b-court{background:var(--purple)}.b-mon{background:var(--green)}.b-serv{background:var(--teal)}.b-meas{background:var(--red)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#eef3f7;position:sticky;top:0;cursor:pointer;user-select:none;white-space:nowrap}
th:hover{background:#e0e9f0}
tr:hover td{background:#f2f7fb}
img{max-width:100%;border:1px solid var(--line);border-radius:10px;background:#fff;display:block;margin:6px 0}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0;align-items:center}
input,select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px}
input#q{flex:1;min-width:220px}
.tier1{color:var(--red);font-weight:700}.tier2{color:var(--orange);font-weight:600}
.pill{font-size:11px;padding:1px 7px;border-radius:10px;background:#eef3f7;color:#33566b;margin-right:3px;white-space:nowrap}
.muted{color:var(--muted);font-size:12.5px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:900px){.kpis{grid-template-columns:repeat(3,1fr)}.two{grid-template-columns:1fr}.wrap{padding:20px}}
.note{background:#FFF6E6;border:1px solid var(--orange);border-radius:10px;padding:12px 14px;font-size:13px;margin:14px 0}
#tablebox{max-height:640px;overflow:auto;border:1px solid var(--line);border-radius:10px}
code{background:#eef3f7;padding:1px 5px;border-radius:5px;font-size:12px}
.figcap{font-size:12px;color:var(--muted);margin:4px 0 18px}
a{color:var(--blue)}
"""

HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cumulative Environmental-Justice Burden by U.S. County — Proto-OKN</title>
<style>__CSS__</style></head><body>
<header>
<h1>A County-Level Map of Cumulative Environmental-Justice Burden</h1>
<p>Integrated across twelve Proto-OKN / OKN federated knowledge graphs · 3,158 U.S. counties (50 states + DC) · joined on county FIPS, S2 Level-13, ZIP5 &amp; NIBRS offense category</p>
<p>Prepared for Peter · 2026-07-06 · model claude-opus-4-8 · OKN federated SPARQL · <b>data exclusively from Proto-OKN graphs</b></p>
</header>
<div class="wrap">
<div class="kpis">
<div class="kpi"><div class="n">70,839</div><div class="l">total findings</div></div>
<div class="kpi"><div class="n">3,158</div><div class="l">counties profiled</div></div>
<div class="kpi"><div class="n">12</div><div class="l">knowledge graphs</div></div>
<div class="kpi"><div class="n">4</div><div class="l">counties flagged by all 5 sources</div></div>
<div class="kpi"><div class="n">r=0.71</div><div class="l">SVI ↔ diabetes (ecological)</div></div>
<div class="kpi"><div class="n">16</div><div class="l">PFAS counties (Maine only)</div></div>
</div>

<div class="card">
<b>Highest-burden core.</b> Four counties are flagged as high-burden by <b>all five</b> nationally-available sources (Tier&nbsp;1): <span class="tier1">Williamsburg&nbsp;County&nbsp;SC, Lea&nbsp;County&nbsp;NM, Pike&nbsp;County&nbsp;KY, Sullivan&nbsp;County&nbsp;NY</span>. A further <b>147</b> counties are flagged by four sources (Tier&nbsp;2) — dominated by Great Plains reservation counties (Buffalo/Dewey/Corson&nbsp;SD, Blaine&nbsp;MT, Benson&nbsp;ND, Thurston&nbsp;NE) and Texas/New-Mexico oil-and-border counties (McMullen, Dimmit, Wheeler, Live&nbsp;Oak&nbsp;TX; Union&nbsp;NM).<br>
Evidence kinds are kept separate:
<span class="badge b-surv">survey/ranking 49,763</span>
<span class="badge b-reg">regulatory record 9,250</span>
<span class="badge b-court">court record 6,353</span>
<span class="badge b-mon">monitoring feature 3,222</span>
<span class="badge b-serv">service listing 2,197</span>
<span class="badge b-meas">measured PFAS sample 48</span>
</div>

<h2>Knowledge graphs used</h2>
<div class="muted">Twelve Proto-OKN graphs supplied county-level evidence; <code>spatialkg</code> is the S2/administrative spatial hub and <code>ubergraph</code>/<code>hydrologykg</code> are supporting. Versions are the exact OKN releases queried 2026-07-06.</div>
<table style="margin-top:10px"><thead><tr><th>Knowledge graph</th><th>Ver</th><th>Contribution (entity type)</th><th>Join key</th></tr></thead><tbody>
<tr><td>spoke-okn</td><td>v0.0.6</td><td>SDoH (SAIPE, ACS/AHRQ), CDC SVI, CDC PLACES disease prevalence, geography</td><td>county FIPS; place→county</td></tr>
<tr><td>fiokg</td><td>v0.0.11</td><td>EPA facilities, PFAS-facility flag, enforcement records</td><td>facility <code>sfWithin</code> county</td></tr>
<tr><td>scales</td><td>v0.0.22</td><td>federal court case volume; NIBRS offense categories</td><td><code>hasIdbCounty</code></td></tr>
<tr><td>ruralkg</td><td>v0.2.7</td><td>RUCC rural class, substance-use treatment, population</td><td>county FIPS; ZIP→place→county</td></tr>
<tr><td>sawgraph</td><td>v0.0.15</td><td>PFAS water-sample concentration (ng/L)</td><td>sample→S2→county</td></tr>
<tr><td>geoconnex</td><td>v0.0.4</td><td>hydrologic water-monitoring features</td><td>GNIS county</td></tr>
<tr><td>spatialkg</td><td>v0.0.6</td><td>S2 grid, county/state geometry, admin hierarchy (spatial hub)</td><td><code>sfWithin</code> / FIPS</td></tr>
<tr><td>ufokn</td><td>v0.0.3</td><td>urban-flood-risk S2 cells <span class="muted">(not resolved to county — see caveats)</span></td><td>S2 L13</td></tr>
<tr><td>dreamkg</td><td>v0.0.5</td><td>homelessness/social services (Philadelphia)</td><td>ZIP5</td></tr>
<tr><td>nikg</td><td>v0.0.6</td><td>neighborhood incident / gun-violence counts (2 counties)</td><td>incident→county</td></tr>
<tr><td>hydrologykg</td><td>v0.0.9</td><td>streams/wells (spatial-hub support)</td><td>S2 L13</td></tr>
<tr><td>ubergraph</td><td>v0.0.2</td><td>ontology backbone (support)</td><td>—</td></tr>
</tbody></table>

<h2>How cumulative burden is scored</h2>
<div class="muted">Count stressors (EPA facilities, federal court cases, treatment providers) are normalized per 10,000 residents, ranked into national percentiles, and flagged in the worst national tertile. A county's <b>cross-source agreement</b> (0–5) counts how many of five independent stressor sources flag it: many facilities, high social vulnerability, high federal-court activity, nonmetro rurality (RUCC ≥ 4), and treatment-service scarcity. The <b>burden index</b> (0–1) is the mean of the five stressor percentiles. Read agreement as primary; the index breaks ties.</div>

<h2>Burden × source, and the highest-burden counties</h2>
<img src="__F1__" alt="Burden by source matrix, top 30 counties">
<div class="figcap">Each cell = a county's national percentile on that stressor; rows are the 30 highest-agreement counties. Blank service-scarcity cells = counties with no mapped substance-use-treatment providers at all.</div>
<img src="__F3__" alt="Top 25 ranked counties">
<div class="figcap">Top 25 counties by cross-source agreement, then composite burden index.</div>

<h2>Findings by entity type</h2>
<div class="card"><b>Places (spatial backbone).</b> spatialkg supplies the S2 Level-13 grid and GADM county/state hierarchy (FIPS + geometry) for the contiguous U.S.; spoke-okn resolves ~42,700 ZIPs and ~27,500 places, with <code>PARTOF_LpL</code> linking place→county — the join that makes county-level health aggregation possible.</div>
<div class="card"><b>Environmental burden.</b> <span class="badge b-reg">regulatory</span> 3.6 M facility-county records (162,254 PFAS-flagged; 643,975 enforcement). <span class="badge b-mon">monitoring</span> 964,897 water features. <span class="badge b-meas">measured</span> PFAS is Maine-only: 117,320 samples over 16 counties, county means to <b>1,192 ng/L</b> (max 480,000) — 100–300× the 4 ng/L limit. Facility density (per capita) peaks in Permian/Eagle-Ford extraction counties.</div>
<div class="card"><b>Social determinants of health.</b> <span class="badge b-surv">survey/ranking</span> county poverty (SAIPE), &lt;HS education, food insecurity (County Health Rankings), unemployment, uninsured (ACS/AHRQ), and CDC Social Vulnerability Index — the vulnerability backbone of the score.</div>
<div class="card"><b>Justice.</b> <span class="badge b-court">court</span> 684,069 federal cases over 3,122 counties (Cook 113,188; LA 15,439). NIBRS offense charges are national-only (111 categories; disjoint from the court-county key). nikg gun violence (2 counties): Philadelphia 15,205 shootings / 3,163 fatal; Cook 89,367 incidents.</div>
<div class="card"><b>Rural-urban classification.</b> <span class="badge b-surv">survey/ranking</span> RUCC for 3,221 counties; <b>1,985 (62%) are nonmetro</b> (RUCC ≥ 4) — the decisive dimension in the high-agreement tail.</div>
<div class="card"><b>Social services.</b> <span class="badge b-serv">service listing</span> 8,820 substance-use-treatment providers mapped to 2,144 counties (ZIP→place→county); many top-burden counties have <b>zero</b>. DREAM-KG adds 662 Philadelphia services (Mental Health 213, Counseling 192, Food Pantry 140).</div>
<div class="card"><b>Health outcomes.</b> <span class="badge b-surv">survey/ranking</span> nine CDC PLACES chronic conditions aggregated to 3,057 counties: obesity 37.4%, hypertension 32.6%, depression 23.7%, diabetes 10.5%, asthma 10.6%, COPD 7.5%, coronary disease 5.9%, stroke 3.1%.</div>

<h2>Ecological correlations with health &amp; SDoH</h2>
<img src="__F2__" alt="Correlation heatmap">
<div class="figcap">Pearson r across ~3,050–3,130 counties. All correlations are ecological (county aggregates), not individual-level or causal.</div>
<div class="card"><b>Social Vulnerability</b> is the strongest correlate of adverse outcomes (diabetes r=0.71, poverty 0.70, food insecurity 0.70, stroke 0.69, low education 0.67). <b>Rurality</b> carries a moderate, consistent health penalty (coronary disease 0.28, poverty 0.26, COPD/obesity 0.22–0.23). Per-capita <b>EPA-facility density</b> correlates <i>negatively</i> with disease (−0.16 to −0.23) — a small-denominator / ecological artifact (density peaks in tiny extraction counties), not a protective effect, and the reason exposure counts and vulnerability rates are scored as separate dimensions.</div>

<h2>Coverage by layer</h2>
<img src="__F4__" alt="Agreement distribution and coverage">
<div class="figcap">Agreement distribution (0–5) and county coverage per Proto-OKN layer; PFAS is the lone state-limited layer (Maine, 16).</div>

<div class="note"><b>Uncertainties.</b> All correlations are ecological. PFAS is Maine-only (absence elsewhere ≠ absence of PFAS). ufokn urban-flood risk could not be resolved to county within endpoint query limits. nikg = 2 counties and dreamkg = Philadelphia ZIPs are illustrative and excluded from the ranking. NIBRS offense data is national-only. Per-capita rates favor tiny counties, so read the 0–5 agreement as primary. County counts vary by layer (3,052–3,222). Map polygons are standard cartographic boundaries — the only non-Proto-OKN input; every burden/health/social value is from Proto-OKN.</div>

<h2>County burden explorer — interactive (3,158 counties)</h2>
<div class="muted">Search by county, filter by state or agreement tier, and click any column header to sort. Full per-finding data: <code>data/findings_long.csv</code> (70,839 rows); ranked table: <code>data/burden_ranking.csv</code>. Interactive OpenStreetMap choropleth: <a href="choropleth_burden.html">choropleth_burden.html</a>.</div>
<div class="controls">
<input id="q" placeholder="Search county…">
<select id="fState"><option value="">All states</option></select>
<select id="fAgr"><option value="">All agreement levels</option><option value="5">5 sources</option><option value="4">4 sources</option><option value="3">3 sources</option><option value="2">2 sources</option><option value="1">1 source</option><option value="0">0 sources</option></select>
<span class="muted" id="count"></span>
</div>
<div id="tablebox"><table id="tbl"><thead><tr id="hdr"></tr></thead><tbody></tbody></table></div>

<h2>Caveats &amp; reproducibility</h2>
<div class="muted">
Every canonical SPARQL query (verbatim, per layer) is preserved in <code>transcript.md</code>; the assembly/scoring/correlation pipeline is <code>scripts/build_master.py</code>, figures <code>scripts/make_figs.py</code>, map <code>scripts/make_map.py</code>. Re-running each query against the listed KG versions and then the pipeline reproduces every count and correlation. A plain-Markdown version of this report is <code>report.md</code>.
</div>
</div>
<script>
const DATA=__DATA__;
const COLS=[["county","County"],["state","St"],["agreement","Agr"],["burden_index","Burden idx"],["epa_fac","EPA fac"],["court_cases","Fed. court"],["svi","SVI"],["rucc","RUCC"],["sud_providers","SUD tx"],["poverty","Pov %"],["uninsured","Unins %"],["diabetes","Diab %"],["obesity","Obes %"]];
const hdr=document.getElementById('hdr');
COLS.forEach(c=>{const th=document.createElement('th');th.textContent=c[1];th.onclick=()=>sortBy(c[0]);hdr.appendChild(th);});
const tbody=document.querySelector('#tbl tbody');
const fState=document.getElementById('fState'),fAgr=document.getElementById('fAgr'),q=document.getElementById('q'),count=document.getElementById('count');
[...new Set(DATA.map(r=>r.state))].sort().forEach(v=>fState.add(new Option(v,v)));
let sortCol='agreement',sortDir=-1;
function sortBy(c){sortDir=(sortCol===c)?-sortDir:1;sortCol=c;render();}
function fmt(v){return (v===null||v===undefined)?'<span class="muted">–</span>':v;}
function render(){
 let r=DATA.filter(x=>(!fState.value||x.state===fState.value)&&(fAgr.value===''||String(x.agreement)===fAgr.value));
 const s=q.value.toLowerCase();
 if(s)r=r.filter(x=>(x.county+' '+x.state).toLowerCase().includes(s));
 r.sort((a,b)=>{let x=a[sortCol],y=b[sortCol];
   if(x===null||x===undefined)x=(typeof y==='number'?-Infinity:'');
   if(y===null||y===undefined)y=(typeof x==='number'?-Infinity:'');
   return (x<y?-1:x>y?1:0)*sortDir;});
 tbody.innerHTML='';
 const frag=document.createDocumentFragment();
 for(const x of r){const tr=document.createElement('tr');
   COLS.forEach(c=>{const td=document.createElement('td');const k=c[0];
     if(k==='county'){td.innerHTML=(x.tier==='T1'?'<span class="tier1">':x.tier==='T2'?'<span class="tier2">':'<span>')+x.county+'</span>';}
     else if(k==='agreement'){td.innerHTML='<span class="pill">'+x.agreement+'/5</span>';}
     else td.innerHTML=fmt(x[k]);
     tr.appendChild(td);});
   frag.appendChild(tr);}
 tbody.appendChild(frag);
 count.textContent=r.length+' / '+DATA.length+' counties';
}
[q,fState,fAgr].forEach(e=>e.addEventListener('input',render));
render();
</script>
</body></html>"""

html = (
    HEAD.replace("__CSS__", CSS)
    .replace("__F1__", F1)
    .replace("__F2__", F2)
    .replace("__F3__", F3)
    .replace("__F4__", F4)
    .replace("__DATA__", DATA)
)
Path(DEST + "/report.html").write_text(html)
print("report.html bytes:", len(html), "| counties in explorer:", len(rows))

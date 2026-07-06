#!/usr/bin/env python3
"""Generate the HTML + Markdown bisphenol exposome report from the assembled CSVs."""
import csv, os, base64
from collections import Counter, defaultdict
BASE = "/sessions/nifty-festive-gauss/mnt/outputs/exposome"
def load(fn):
    p = f"{BASE}/data/{fn}"; p = p if os.path.exists(p) else f"{BASE}/{fn}"
    return list(csv.DictReader(open(p)))
def b64(fn):
    with open(f"{BASE}/figures/{fn}", "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

chem = load("chemicals.csv"); targets = load("targets.csv"); aop = load("aop_backbone.csv")
fuse = load("ice_functional_use.csv"); haz = load("pubchem_hazards.csv")
gxa = load("gxa_expression.csv"); rdkg = load("rdkg_rare_disease.csv")
prokn = load("prokn_protein.csv"); spoke = load("spoke_gene_disease.csv")
rank = load("corroboration_ranking.csv"); det = load("corroboration_detail.csv")
oard = load("oard_disease_phenotype.csv")
fuse_by = defaultdict(list)
for r in fuse: fuse_by[r["cas"]].append(r["category"])
cas2ab = {r["cas"]: r["abbrev"] for r in chem}

nfind = sum(1 for _ in open(f"{BASE}/findings_master.csv")) - 1
ndis = len({r["disease"] for r in spoke})
bpa7 = sorted({r["disease"] for r in rank if r["chemical"]=="BPA" and r["corroboration_score"]=="7"})
tbbpa = sorted({r["disease"] for r in rank if r["chemical"]=="TBBPA"})
sc = Counter(int(r["corroboration_score"]) for r in rank)

KGV = {r["shortname"]: r for r in [
 {"shortname":"biobricks-aopwiki","version":"v0.0.4"},{"shortname":"biobricks-toxcast","version":"v0.0.2"},
 {"shortname":"biobricks-tox21","version":"v0.0.3"},{"shortname":"biobricks-ice","version":"v0.0.3"},
 {"shortname":"biobricks-pubchem-annotations","version":"v0.0.2"},{"shortname":"gene-expression-atlas-okn","version":"v0.0.3"},
 {"shortname":"spoke-okn","version":"v0.0.6"},{"shortname":"rdkg","version":"v0.0.1"},{"shortname":"prokn","version":"v0.0.5"},
 {"shortname":"oard-kg","version":"v0.0.3"},{"shortname":"ubergraph","version":"v0.0.2"},{"shortname":"sudokn","version":"v0.0.10"},
 {"shortname":"sawgraph","version":"v0.0.15"},{"shortname":"fiokg","version":"v0.0.11"}]}

# ---------------- Markdown ----------------
M = []
M.append("# The Chemical Exposome of Bisphenols\n")
M.append("### An evidence-backed exposure→disease map built exclusively from Proto-OKN knowledge graphs\n")
M.append(f"*Generated {os.popen('date +%Y-%m-%d').read().strip()} · FRINK federated SPARQL endpoint · {nfind} findings across 14 knowledge graphs*\n")
M.append("\n---\n")
M.append("## Executive summary\n")
M.append(
"This map traces bisphenol A (BPA) and 12 structural analogues from **exposure and industrial use**, "
"through **curated adverse outcome pathways (AOPs)**, **molecular targets**, **high-throughput assay activity**, "
"and **differential gene expression**, to **resulting diseases and phenotypes** — using only Proto-OKN graphs "
"joined on reconciled chemical (CAS/CID/DTXSID/ChEBI), gene (Ensembl/Entrez), protein (UniProt) and "
"disease (DOID↔MONDO) identifiers.\n")
M.append("\n**Headline results**\n")
M.append(
"- **13 bisphenols** resolved and cross-walked: all 13 in ICE, 11 in ToxCast & Tox21, and **only 2 (BPA, TBBPA) carry curated AOPs** in AOP-Wiki.\n"
"- The mechanistic spine is **estrogen-receptor signalling**: every one of BPA's three AOPs initiates at an estrogen receptor (ERα/ERβ/GPER), converging on adverse outcomes in **immune (lupus), neurodevelopmental (autism-like), and cognitive (learning/memory)** domains. TBBPA instead initiates at **transthyretin (thyroid axis) → neurodevelopmental toxicity**.\n"
f"- **16 molecular targets** (ESR1, ESR2, ESRRA/G, AR, GPER1, PGR, thyroid receptors, PXR/CAR, PPARG, AHR, GATA3, TTR) link to **{ndis} distinct diseases** in SPOKE-OKN and hundreds of rare diseases in RDKG; all 16 are **differentially expressed** across GXA disease contrasts.\n"
f"- **{sc.get(7,0)} chemical→disease links reach the maximum corroboration score (7/7 independent sources)** — all BPA, led by **breast cancer** (uniquely supported by three converging targets: ERα, ERβ and GATA3).\n"
"- **Best-supported pathway:** BPA → ERα (AOP-Wiki MIE + ToxCast-active + ERα differentially expressed + ERα→breast/ovarian/uterine cancer, endometriosis, PCOS in SPOKE + rare-disease genetics in RDKG + curated protein annotation in ProKN + PubChem 'reproductive toxicity cat. 2 / endocrine disruptor' hazard).\n")
M.append("\n> **Read the uncertainties section carefully.** AOP coverage is curated and sparse; assay activity is *in-vitro*, not *in-vivo* effect; several joins are ontology-bridged; and AOP-Wiki's automated key-event→gene annotations are unreliable (documented below), so molecular targets were taken from the *curated molecular-initiating-event biology*, not those automated links.\n")

M.append("\n## 1. Data provenance & method\n")
M.append("All data come from the Proto-OKN FRINK federation. Knowledge graphs and versions used:\n\n")
M.append("| Layer | Knowledge graph | Version | Role in the map |\n|---|---|---|---|\n")
tbl_rows=[("biobricks-aopwiki","curated AOPs: MIE→KE→AO & chemical stressors"),
 ("biobricks-toxcast","HTS assay endpoints + binary hitcalls"),
 ("biobricks-tox21","chemical coverage (registry only)"),
 ("biobricks-ice","functional-use categories & assay/safety curation"),
 ("biobricks-pubchem-annotations","GHS / toxicity / hazard literature annotations"),
 ("gene-expression-atlas-okn","differential expression by disease & tissue"),
 ("spoke-okn","gene↔disease associations (DOID)"),
 ("rdkg","gene↔rare-disease associations (MONDO)"),
 ("prokn","protein GO / Reactome annotations (UniProt)"),
 ("oard-kg","EHR disease↔phenotype associations"),
 ("ubergraph","CHEBI↔CAS, DOID↔MONDO bridges & category expansion"),
 ("sudokn","US manufacturers of BPA-derived polycarbonate/epoxy"),
 ("sawgraph","PFAS environmental graph (no bisphenols)"),
 ("fiokg","EPA facilities + NAICS (no chemical identifiers)")]
for sn,role in tbl_rows:
    v=KGV.get(sn,{}).get("version","—")
    M.append(f"| | `{sn}` | {v} | {role} |\n")
M.append("\n**Identifier reconciliation (joins).** Chemical layers joined on **CAS** (`identifiers.org/cas/`; AOP-Wiki uses the `https` form, ToxCast/ICE/Tox21 the `http` form — rewritten on join). Genes joined on **Ensembl** (AOP-Wiki `skos:exactMatch` ↔ GXA node-IRI ↔ SPOKE `ensembl`) and **Entrez** (SPOKE/rdkg gene node-IRIs `…/gene/{id}`). Proteins joined on **UniProt** (ProKN node-IRIs). Diseases bridged **DOID↔MONDO** through Ubergraph `oboInOwl:hasDbXref` (45/45 SPOKE diseases mapped).\n")
M.append("\n**Evidence typing (kept separate).** Every finding is tagged with its source graph, relationship type (`has-molecular-initiating-event`, `has-key-event`, `has-adverse-outcome`, `chemical-stressor-of`, `target-gene-of`, `assayed-in`, `differentially-expressed-in`, `associated-with-disease`, `disease-phenotype`, `functional-use-of`, `hazard-annotation`) and evidence kind (*curated AOP link*, *HTS assay measurement*, *measured differential expression*, *literature annotation*, *curated/statistical disease association*, *ontology bridge*). These are never merged.\n")

M.append("\n## 2. Chemicals — identity, cross-walk & functional use\n")
M.append("![Assay coverage](figures/fig1_assay_coverage.png)\n\n")
M.append("| Abbr | Name | CAS | PubChem CID | DTXSID | AOP-Wiki | ToxCast | Tox21 | ICE | ICE functional use |\n|---|---|---|---|---|:--:|:--:|:--:|:--:|---|\n")
for r in chem:
    fu = ", ".join(sorted(set(fuse_by.get(r["cas"],[])))) or "—"
    M.append(f"| **{r['abbrev']}** | {r['name']} | {r['cas']} | {r['pubchem_cid'] or '—'} | {r['dtxsid']} | "
             f"{'✓' if r['in_aopwiki']=='1' else '·'} | {'✓' if r['in_toxcast']=='1' else '·'} | "
             f"{'✓' if r['in_tox21']=='1' else '·'} | {'✓' if r['in_ice']=='1' else '·'} | {fu} |\n")
M.append("\nFunctional-use profiles cleanly separate the family: **BPA** = *binder / catalyst / hardener* (polycarbonate & epoxy monomer); the halogenated **TBBPA/TCBPA** = *flame retardant*; the newer analogues (BPS, BPF, BPAF, BPB…) = *antioxidant / UV-absorber / colorant* substitutes.\n")

M.append("\n## 3. Adverse outcome pathways (AOP-Wiki)\n")
M.append("Only **BPA** and **TBBPA** exist as AOP chemical stressors. Their curated pathways:\n\n")
M.append("| Chemical | AOP | Molecular initiating event | Adverse outcome | #KEs | Target |\n|---|---|---|---|:--:|---|\n")
for r in aop:
    M.append(f"| {r['chemical']} | AOP {r['aop_id']} | {r['mie_title']} | {r['adverse_outcome']} | {r['n_key_events']} | {r['curated_target']} |\n")
M.append("\nBPA's three pathways **all initiate at an estrogen receptor** (ERα binding, ER antagonism, GPER activation) and diverge to immune, neurodevelopmental and cognitive outcomes. TBBPA initiates at **transthyretin** (thyroid-hormone distribution) leading to decreased cognitive function.\n")

M.append("\n## 4. Molecular targets\n")
M.append("Targets were taken from the **curated MIE biology** and verified against AOP-Wiki HGNC cross-reference nodes (see *Uncertainties* for why the automated key-event→gene links were **not** used). Identifiers:\n\n")
M.append("| Gene | Protein | Ensembl | Entrez | UniProt | Role |\n|---|---|---|---|---|---|\n")
for r in targets:
    M.append(f"| **{r['symbol']}** | {r['name']} | {r['ensembl'] or '—'} | {r['entrez'] or '—'} | {r['uniprot']} | {r['role_in_bisphenol_MoA']} |\n")

M.append("\n## 5. High-throughput assay evidence (ToxCast)\n")
M.append("ToxCast hitcalls are **binary** in this release (active = hitcall 1). Coverage and activity per chemical are in Figure 1. **BPAF is the most active** analogue (484/1189 endpoints, 41%), followed by TBBPA, BPB, TCBPA and BPA; the popular substitutes **BPS (13%) and BPF (8%) are the least active** of those tested. *Assay activity is in-vitro and does not by itself establish an in-vivo adverse effect.*\n")

M.append("\n## 6. Differential expression (Gene Expression Atlas)\n")
M.append("![Expression](figures/fig2_expression_matrix.png)\n\n")
M.append("All 16 targets are significantly differentially expressed (adj p<0.05) across many GXA disease/tissue contrasts — **PPARG (399), GATA3 (374), AHR (290), GPER1 (284)** lead by breadth, while **TTR** shows the largest single effect size (|log2FC| up to 17.1).\n")

M.append("\n## 7. From targets to disease (SPOKE-OKN, RDKG, ProKN, OARD)\n")
M.append("![Target-disease matrix](figures/fig3_target_disease_matrix.png)\n\n")
M.append(f"SPOKE-OKN supplies **{len(spoke)} gene→disease associations** across {ndis} DOID diseases; the estrogen/androgen receptors and PPARG dominate the hormone-sensitive-cancer, reproductive and cardiometabolic clusters. RDKG adds curated **rare-disease** associations (ESR1 124, PPARG 104, ESR2 73, AR 59 MONDO diseases). ProKN confirms every target protein with GO/Reactome annotations (ESR1: 15 Reactome pathways, 31 GO terms). OARD contributes **EHR disease→phenotype** profiles for the rare-disease subset — most relevantly **precocious puberty (1,639 phenotypes)** and **prostate cancer (1,218)**, both classic endocrine-disruption outcomes.\n")

M.append("\n## 8. Integrated exposome flow\n")
M.append("![Sankey](figures/fig5_sankey.png)\n\n")
M.append("The flow reads left→right: **chemical → molecular target → disease category**. BPA and TBBPA are AOP-anchored; analogues enter through the shared estrogen-receptor axis (ERα/ERβ), supported by assay activity and target→disease evidence rather than a curated pathway of their own.\n")

M.append("\n## 9. Cross-source corroboration ranking\n")
M.append("![Corroboration](figures/fig4_corroboration_bars.png)\n\n")
M.append(f"Each **chemical→disease** link was scored by the number of *independent* Proto-OKN sources that agree on the chain (AOP structure · assay activity · differential expression · disease association · rare-disease genetics · protein annotation · hazard annotation; max 7). Of {len(rank)} links: **{sc.get(7,0)} score 7** (all BPA), **{sc.get(6,0)} score 6** (TBBPA, thyroid axis), **{sc.get(5,0)} score 5** (analogues via the ER axis — differentiated further by assay potency).\n\n")
M.append("**Best-supported BPA links (7/7 independent sources):**\n\n")
M.append(", ".join(bpa7) + ".\n\n")
M.append("**Breast cancer** is the single best-corroborated outcome: it is the only disease reached through **three converging BPA targets — ERα, ERβ and GATA3** — with all seven evidence types agreeing.\n\n")
M.append("**TBBPA (6/7, thyroid/transthyretin axis):** " + ", ".join(tbbpa) + ".\n")

M.append("\n## 10. Industrial & exposure context\n")
M.append("BPA is the monomer of **polycarbonate plastic** and **epoxy resins**; TBBPA is a **flame retardant**. Among the industrial Proto-OKN graphs, **SUDOKN** catalogues numerous US small/medium manufacturers of BPA-derived polycarbonate and epoxy-resin products (e.g. TUFFAK polycarbonate sheet, IMPEX panels, epoxy-resin work surfaces) — a *material-based* link, since SUDOKN keys on products, not CAS. **SAWGraph** (PFAS-only) and **FIOKG** (facilities/NAICS) carry no bisphenol chemical identifiers, so no direct chemical join exists there.\n")

M.append("\n## 11. Uncertainties & limitations (flagged)\n")
M.append(
"1. **AOP coverage is curated and sparse.** Only BPA and TBBPA have AOPs; the 11 analogues have *no* curated pathway and are placed on the map through the shared ER axis by assay + target→disease inference (lower-tier evidence).\n"
"2. **AOP-Wiki automated gene links are unreliable.** The KG's key-event→gene annotations (`edam:data_1025`) are machine-derived and frequently wrong — e.g. the ERα-binding MIE maps to *MDK/MVK/PPIB* and ER antagonism to *EREG/GCNT2*, none of which is ESR1; downstream key events (oxidative stress, apoptosis) each pull in *thousands* of genes. Molecular targets were therefore taken from the **curated MIE biology**, not these links. TTR was the one correctly captured target.\n"
"3. **Assay activity ≠ in-vivo effect.** ToxCast hitcalls are in-vitro; potency and toxicokinetics are not modelled here.\n"
"4. **Ontology-bridged joins.** DOID↔MONDO (SPOKE↔RDKG/OARD) rely on Ubergraph cross-references; CAS formatting differs between graphs and was rewritten on join.\n"
"5. **CAS/CID gaps.** PubChem CIDs were verified from the graph only for BPA (6623) and TBBPA (6618); analogue CIDs were left blank rather than asserted. PubChem hazard annotations were extracted for BPA (richest coverage); the KG stores no annotation *heading*, so hazards were recovered by text-filtering annotation bodies.\n"
"6. **Disease-association evidence is largely statistical/literature-derived** (SPOKE MeSH co-occurrence, RDKG curation) — associative, not causal, and target-level rather than chemical-specific.\n"
"7. **Tox21** in this federation is a chemical registry (CAS + name) with no endpoint-level activity; ToxCast provides the quantitative assay layer.\n")

M.append("\n## 12. Reproducibility\n")
M.append(
"- **Data tables** (one row per finding): `findings_master.csv` (216 rows) plus 12 per-layer CSVs in `data/`.\n"
"- **Corroboration:** `corroboration_detail.csv` (275 chemical–target–disease triples) and `corroboration_ranking.csv` (234 ranked links).\n"
"- **Figures:** `figures/` (5 PNGs + interactive `sankey_chemical_target_disease.html`).\n"
"- **Query transcript:** `bisphenol_exposome_transcript.md` — every SPARQL query that produced a finding, verbatim, with results.\n"
"- All queries ran against `https://frink.apps.renci.org` named graphs listed in §1.\n")

M.append("\n## Sources\n")
M.append("All findings derive from the Proto-OKN FRINK federation. Primary graphs (with homepages):\n\n")
for sn,url in [("biobricks-aopwiki","https://github.com/biobricks-ai/aopwikirdf-kg"),
 ("biobricks-toxcast","https://github.com/biobricks-ai/biobricks-okg"),
 ("biobricks-ice","https://github.com/biobricks-ai/biobricks-okg"),
 ("biobricks-pubchem-annotations","https://github.com/biobricks-ai/pubchem-annotations-kg"),
 ("gene-expression-atlas-okn","https://www.ebi.ac.uk/gxa/home"),
 ("spoke-okn","https://spoke.ucsf.edu"),("rdkg","https://registry.okn.us"),
 ("prokn","https://research.bioinformatics.udel.edu/ProKN/"),
 ("oard-kg","https://github.com/WengLab-InformaticsResearch/oard-react"),
 ("ubergraph","https://github.com/INCATools/ubergraph/"),("sudokn","https://projects.engineering.asu.edu/sudokn/")]:
    M.append(f"- [{sn}]({url})\n")

with open(f"{BASE}/bisphenol_exposome_report.md","w") as f:
    f.write("".join(M).replace("/sessions/nifty-festive-gauss/mnt/outputs/exposome/",""))
print("Markdown report written:", sum(1 for _ in open(f'{BASE}/bisphenol_exposome_report.md')), "lines")

# ---------------- HTML ----------------
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def chk(v): return '<span class="y">✓</span>' if v=="1" else '<span class="n">·</span>'
CSS = """
:root{--navy:#20365b;--teal:#1b7a7a;--coral:#d1495b;--amber:#e0a458;--ink:#1c2230;--mut:#5a6474;--line:#e4e8ee;--bg:#f7f9fb;--card:#fff}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.62;font-size:16px}
.wrap{max-width:1080px;margin:0 auto;padding:0 26px 90px}
header{background:linear-gradient(135deg,#182a4a 0%,#20365b 55%,#1b7a7a 130%);color:#fff;padding:52px 26px 40px;margin-bottom:8px}
header .in{max-width:1080px;margin:0 auto}
header h1{margin:0 0 6px;font-size:31px;letter-spacing:-.4px;line-height:1.15}
header .sub{font-size:18px;opacity:.94;font-weight:500}
header .meta{margin-top:14px;font-size:13.5px;opacity:.8}
h2{color:var(--navy);font-size:23px;margin:44px 0 12px;padding-bottom:7px;border-bottom:2px solid var(--line)}
h3{color:var(--teal);font-size:17px;margin:26px 0 8px}
p{margin:10px 0}
.callout{background:#eef5f5;border-left:5px solid var(--teal);border-radius:0 8px 8px 0;padding:16px 20px;margin:18px 0}
.warn{background:#fbeef0;border-left:5px solid var(--coral)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 14px;text-align:center;box-shadow:0 1px 3px rgba(30,50,90,.05)}
.stat .num{font-size:30px;font-weight:800;color:var(--navy);line-height:1}
.stat .lab{font-size:12.5px;color:var(--mut);margin-top:6px}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.4px;background:var(--card);border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(30,50,90,.05)}
th{background:var(--navy);color:#fff;text-align:left;padding:9px 11px;font-weight:600;font-size:12.5px}
td{padding:8px 11px;border-top:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#fafbfc}
.y{color:var(--teal);font-weight:800}.n{color:#c3c9d2}
figure{margin:22px 0;text-align:center}
figure img{max-width:100%;border:1px solid var(--line);border-radius:10px;box-shadow:0 2px 10px rgba(30,50,90,.08)}
figcaption{font-size:13px;color:var(--mut);margin-top:8px;font-style:italic}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;background:#eef2f7;color:var(--navy)}
.s7{background:var(--navy);color:#fff}.s6{background:var(--teal);color:#fff}.s5{background:#e7edf2;color:var(--navy)}
code{background:#eef2f7;padding:1px 6px;border-radius:5px;font-size:13px;color:#324}
ol li,ul li{margin:6px 0}
.foot{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:13px;color:var(--mut)}
a{color:var(--teal)}
"""
H=['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
   '<title>The Chemical Exposome of Bisphenols — Proto-OKN Evidence Map</title><style>',CSS,'</style></head><body>']
H.append('<header><div class="in"><h1>The Chemical Exposome of Bisphenols</h1>'
 '<div class="sub">An evidence-backed exposure→disease map built exclusively from Proto-OKN knowledge graphs</div>'
 f'<div class="meta">FRINK federated SPARQL · {nfind} findings · 14 knowledge graphs · generated {os.popen("date +%Y-%m-%d").read().strip()}</div></div></header>')
H.append('<div class="wrap">')
# stats
H.append('<div class="grid">'
 '<div class="stat"><div class="num">13</div><div class="lab">bisphenols mapped</div></div>'
 '<div class="stat"><div class="num">4</div><div class="lab">curated AOPs (BPA×3, TBBPA×1)</div></div>'
 '<div class="stat"><div class="num">16</div><div class="lab">molecular targets</div></div>'
 f'<div class="stat"><div class="num">{ndis}</div><div class="lab">linked diseases (DOID)</div></div></div>')
H.append('<div class="callout"><b>Mechanistic spine — estrogen-receptor signalling.</b> All three BPA AOPs initiate at an estrogen receptor (ERα binding, ER antagonism, GPER activation), diverging to immune (lupus), neurodevelopmental (autism-like) and cognitive (learning/memory) outcomes; TBBPA initiates at transthyretin (thyroid axis)→neurodevelopmental toxicity. '
 f'<b>{sc.get(7,0)} chemical→disease links reach the maximum corroboration score (7/7 independent sources)</b> — all BPA, led by <b>breast cancer</b> (uniquely supported by three converging targets: ERα, ERβ and GATA3).</div>')
H.append('<div class="callout warn"><b>Read with care.</b> AOP coverage is curated & sparse; assay activity is <i>in-vitro</i>, not <i>in-vivo</i> effect; several joins are ontology-bridged; and AOP-Wiki\'s automated key-event→gene links are unreliable (see §11), so targets were taken from the curated MIE biology.</div>')

H.append('<h2>1 · Data provenance &amp; method</h2><table><tr><th>Knowledge graph</th><th>Ver.</th><th>Role in the map</th></tr>')
for sn,role in tbl_rows:
    H.append(f'<tr><td><code>{sn}</code></td><td>{KGV.get(sn,{}).get("version","—")}</td><td>{role}</td></tr>')
H.append('</table>')
H.append('<p><b>Joins.</b> Chemicals on <b>CAS</b> (http/https CAS-IRI forms reconciled); genes on <b>Ensembl</b> &amp; <b>Entrez</b>; proteins on <b>UniProt</b>; diseases bridged <b>DOID↔MONDO</b> via Ubergraph (45/45 SPOKE diseases mapped). Each finding keeps its source, relationship type and evidence kind separate.</p>')

H.append('<h2>2 · Chemicals — identity, cross-walk &amp; functional use</h2>')
H.append(f'<figure><img src="{b64("fig1_assay_coverage.png")}"><figcaption>Figure 1 · Per-bisphenol ToxCast assay coverage and activity (binary hitcalls).</figcaption></figure>')
H.append('<table><tr><th>Abbr</th><th>Name</th><th>CAS</th><th>CID</th><th>DTXSID</th><th>AOP</th><th>ToxCast</th><th>Tox21</th><th>ICE</th><th>ICE functional use</th></tr>')
for r in chem:
    fu=", ".join(sorted(set(fuse_by.get(r["cas"],[])))) or "—"
    H.append(f'<tr><td><b>{r["abbrev"]}</b></td><td>{esc(r["name"])}</td><td>{r["cas"]}</td><td>{r["pubchem_cid"] or "—"}</td>'
             f'<td>{r["dtxsid"].split("/")[-1] if r["dtxsid"] else "—"}</td><td>{chk(r["in_aopwiki"])}</td><td>{chk(r["in_toxcast"])}</td>'
             f'<td>{chk(r["in_tox21"])}</td><td>{chk(r["in_ice"])}</td><td>{fu}</td></tr>')
H.append('</table><p>Functional use separates the family: <b>BPA</b> = binder/catalyst/hardener (polycarbonate &amp; epoxy monomer); halogenated <b>TBBPA/TCBPA</b> = flame retardant; newer analogues = antioxidant/UV-absorber/colorant substitutes.</p>')

H.append('<h2>3 · Adverse outcome pathways (AOP-Wiki)</h2><table><tr><th>Chemical</th><th>AOP</th><th>Molecular initiating event</th><th>Adverse outcome</th><th>KEs</th><th>Target</th></tr>')
for r in aop:
    H.append(f'<tr><td>{r["chemical"]}</td><td>AOP {r["aop_id"]}</td><td>{esc(r["mie_title"])}</td><td>{esc(r["adverse_outcome"])}</td><td>{r["n_key_events"]}</td><td>{r["curated_target"]}</td></tr>')
H.append('</table>')

H.append('<h2>4 · Molecular targets</h2><table><tr><th>Gene</th><th>Protein</th><th>Ensembl</th><th>Entrez</th><th>UniProt</th><th>Role</th></tr>')
for r in targets:
    H.append(f'<tr><td><b>{r["symbol"]}</b></td><td>{esc(r["name"])}</td><td>{r["ensembl"] or "—"}</td><td>{r["entrez"] or "—"}</td><td>{r["uniprot"]}</td><td>{esc(r["role_in_bisphenol_MoA"])}</td></tr>')
H.append('</table>')

H.append('<h2>5 · Differential expression (Gene Expression Atlas)</h2>')
H.append(f'<figure><img src="{b64("fig2_expression_matrix.png")}"><figcaption>Figure 2 · Significant differential-expression contrasts (adj p&lt;0.05) per target; red=up, teal=down.</figcaption></figure>')
H.append('<p>All 16 targets are differentially expressed across many disease contrasts — PPARG (399), GATA3 (374), AHR (290), GPER1 (284) lead by breadth; TTR shows the largest single effect (|log2FC|≤17.1).</p>')

H.append('<h2>6 · Targets → disease</h2>')
H.append(f'<figure><img src="{b64("fig3_target_disease_matrix.png")}"><figcaption>Figure 3 · Target gene → disease associations (SPOKE-OKN, DOID; top 20 diseases).</figcaption></figure>')
H.append(f'<p>SPOKE-OKN supplies {len(spoke)} gene→disease associations across {ndis} diseases; RDKG adds rare-disease genetics (ESR1 124, PPARG 104, ESR2 73, AR 59 MONDO diseases); ProKN annotates every target protein (ESR1: 15 Reactome, 31 GO); OARD gives EHR phenotypes for <b>precocious puberty (1,639)</b> and <b>prostate cancer (1,218)</b> — both endocrine-disruption outcomes.</p>')

H.append('<h2>7 · Integrated exposome flow</h2>')
H.append(f'<figure><img src="{b64("fig5_sankey.png")}"><figcaption>Figure 4 · Chemical → molecular target → disease category. Interactive version: <code>figures/sankey_chemical_target_disease.html</code>.</figcaption></figure>')

H.append('<h2>8 · Cross-source corroboration ranking</h2>')
H.append(f'<figure><img src="{b64("fig4_corroboration_bars.png")}"><figcaption>Figure 5 · Chemical→disease links scored by number of independent agreeing sources (max 7).</figcaption></figure>')
H.append(f'<p>Of {len(rank)} chemical→disease links: <span class="tag s7">{sc.get(7,0)} score 7 (BPA)</span> <span class="tag s6">{sc.get(6,0)} score 6 (TBBPA)</span> <span class="tag s5">{sc.get(5,0)} score 5 (analogues)</span>. <b>Breast cancer</b> is the best-corroborated outcome — the only disease reached through three converging BPA targets (ERα, ERβ, GATA3) with all seven evidence types agreeing.</p>')
H.append('<h3>Best-supported links</h3><table><tr><th>Chemical</th><th>Disease</th><th>Score</th><th>Mediating targets</th><th>Agreeing sources</th></tr>')
show=[r for r in rank if r["chemical"] in ("BPA","TBBPA") and int(r["corroboration_score"])>=6]
show=sorted(show,key=lambda r:(-int(r["corroboration_score"]),r["chemical"],r["disease"]))[:16]
for r in show:
    cls="s7" if r["corroboration_score"]=="7" else "s6"
    srcs=r["sources"].replace("_"," ").replace("aop structure","AOP").replace("disease assoc","disease").replace("assay activity","assay").replace("rare disease","rare-disease").replace("protein annot","protein")
    H.append(f'<tr><td>{r["chemical"]}</td><td>{esc(r["disease"])}</td><td><span class="tag {cls}">{r["corroboration_score"]}/7</span></td><td>{r["mediating_targets"].replace("|",", ")}</td><td style="font-size:12px">{srcs.replace("|"," · ")}</td></tr>')
H.append('</table><p style="font-size:13px;color:var(--mut)">Analogues (BPS, BPF, BPAF, BPB, BPAP, BPE, BPC, BPZ, TCBPA) share the ERα/ERβ→disease evidence at score 5 and are further ranked by assay potency (BPAF &gt; BPB &gt; TCBPA &gt; … &gt; BPS &gt; BPF).</p>')

H.append('<h2>9 · Industrial &amp; exposure context</h2>'
 '<p>BPA is the monomer of <b>polycarbonate</b> and <b>epoxy resins</b>; TBBPA is a <b>flame retardant</b>. <b>SUDOKN</b> lists many US manufacturers of BPA-derived polycarbonate/epoxy products (TUFFAK sheet, IMPEX panels, epoxy work surfaces) — a material-based link (no CAS). <b>SAWGraph</b> (PFAS) and <b>FIOKG</b> (facilities/NAICS) carry no bisphenol identifiers.</p>')

H.append('<h2>10 · Uncertainties &amp; limitations</h2><div class="callout warn"><ol>'
 '<li><b>AOP coverage is sparse</b> — only BPA &amp; TBBPA; the 11 analogues have no curated pathway and are inferred via the shared ER axis.</li>'
 '<li><b>AOP-Wiki automated gene links are unreliable</b> — the ERα-binding MIE maps to MDK/MVK/PPIB (not ESR1); downstream KEs pull in thousands of genes. Targets were taken from curated MIE biology instead; TTR was the one correctly captured.</li>'
 '<li><b>Assay activity ≠ in-vivo effect</b> (ToxCast is in-vitro).</li>'
 '<li><b>Ontology-bridged joins</b> (DOID↔MONDO) and reconciled CAS formats introduce bridge dependence.</li>'
 '<li><b>CAS/CID gaps</b> — CIDs verified only for BPA/TBBPA; PubChem hazards extracted for BPA (no annotation headings in the KG).</li>'
 '<li><b>Disease associations are statistical/literature-derived</b> (associative, target-level, not chemical-specific).</li>'
 '<li><b>Tox21</b> here is a registry (no endpoint activity); ToxCast is the quantitative assay layer.</li></ol></div>')

H.append('<h2>11 · Reproducibility</h2><p><code>findings_master.csv</code> (216 findings) · <code>corroboration_detail.csv</code> (275 triples) · <code>corroboration_ranking.csv</code> (234 links) · 12 per-layer CSVs in <code>data/</code> · 5 figures + interactive Sankey · <code>bisphenol_exposome_transcript.md</code> (verbatim SPARQL). Queries ran against the FRINK federation named graphs in §1.</p>')

H.append('<div class="foot">Built with the Proto-OKN MCP over the FRINK federated SPARQL endpoint. Evidence types (curated AOP link · HTS assay measurement · measured differential expression · literature annotation · curated/statistical disease association · ontology bridge) are recorded separately for every finding and never merged.</div>')
H.append('</div></body></html>')
with open(f"{BASE}/bisphenol_exposome_report.html","w") as f:
    f.write("".join(H))
print("HTML report written:", os.path.getsize(f"{BASE}/bisphenol_exposome_report.html")//1024, "KB")

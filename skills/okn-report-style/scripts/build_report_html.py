"""
build_report_html.py — assemble a self-contained interactive HTML report for an OKN analysis.

Everything is inlined (CSS, JS, figures as base64) so the .html is a single portable file.
Import the helpers and compose a page:

    from build_report_html import embed_img, figure_block, candidate_table, build_report
    body = []
    body.append("<h2>Cohort</h2>")
    body.append(figure_block("figures/fig1_overview.png",
        "<b>Figure 1. Overview.</b> (A) design; (B) counts. Provenance: <KG / predicate>."))
    tbl = candidate_table(rows,
        columns=[("name","entity"),("region","region"),("nsrc","sources (n)"),
                 ("score","score"),("tier","tier")],
        search_keys=["name","region"], numeric_keys=["score"],
        extra_filters=[("tier","tier"),("region","region")],  # subset pull-down menus
        sources_col=("nsrc","sources"))                       # corroboration count + source pills
    build_report("My Study", "subtitle", "Date · Endpoint · Model",
                 kpis=[("128","entities"),("4","source KGs")],
                 body_blocks=body, table=tbl, out="study_report.html")

The candidate table is sortable (click any header), filterable (search box + subset pull-down
menus), and PAGINATED (default 25/page, Prev/Next) — never dump a 900-row table in full. It also
carries a `sources (n)` corroboration column (count of federation KGs supporting each candidate +
one pill per source). Run `python build_report_html.py --demo` to emit a demo report.
"""
from __future__ import annotations
import base64, html, json, os

CSS = """
:root{--accent:#c0392b;--ink:#1f2a37;--muted:#667085;--line:#e5e7eb;--bg:#f7f8fa}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
header{background:linear-gradient(120deg,#3a1414,var(--accent));color:#fff;padding:30px 22px 24px}
header h1{margin:0 0 4px;font-size:24px}header .sub{font-size:15px;opacity:.93}header .meta{font-size:12.5px;opacity:.85;margin-top:8px}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px 60px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:20px 0}
.kpi{background:#fff;border:1px solid var(--line);border-radius:11px;padding:12px 8px;text-align:center}
.kpi .n{font-size:21px;font-weight:700;color:var(--accent)}.kpi .l{font-size:10.5px;color:var(--muted);margin-top:2px}
h2{margin:34px 0 8px;font-size:19px;border-bottom:2px solid var(--line);padding-bottom:6px}
.card{background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:9px;padding:12px 15px;margin:10px 0;font-size:14px}
.note{background:#fff8f5;border:1px solid #f3c9bd;border-left:4px solid var(--accent);border-radius:9px;padding:12px 15px;margin:12px 0;font-size:13.5px}
.muted{color:var(--muted);font-size:13px}
.figcap{font-size:12.5px;color:#3a4452;background:#fafbfc;border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:2px 0 8px;line-height:1.55}
img{max-width:100%;border:1px solid var(--line);border-radius:9px;margin:10px 0;background:#fff}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden}
th,td{padding:7px 9px;text-align:left;border-bottom:1px solid var(--line)}
thead th{background:#1f3864;color:#fff;font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
thead th:hover{background:#28457a}tbody tr:hover{background:#f3f6fb}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:12px 0}
.controls input,.controls select{padding:7px 10px;border:1px solid var(--line);border-radius:7px;font-size:13px}
.pager{display:flex;gap:12px;align-items:center;margin:10px 0 4px}
.pager button{padding:6px 13px;border:1px solid var(--line);border-radius:7px;background:#fff;font-size:13px;cursor:pointer}
.pager button:disabled{opacity:.4;cursor:default}.pager button:hover:not(:disabled){background:#f3f6fb}
.badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11.5px;font-weight:600}
.pill{display:inline-block;background:#eef2f7;border-radius:12px;padding:1px 7px;font-size:11px;margin:1px}
footer{color:var(--muted);font-size:12px;text-align:center;padding:24px}
"""


def embed_img(path):
    """Return a base64 data URI for a PNG so it can be inlined in the HTML."""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def figure_block(img_path, caption_html, alt="figure"):
    """<img> (base64) + a caption legend div BELOW it. Put the full scientific legend here.
    Pass `alt` for a descriptive accessibility label (screen readers)."""
    return f'<img src="{embed_img(img_path)}" alt="{html.escape(alt)}">\n<div class="figcap">{caption_html}</div>'


def kpi_row(kpis):
    cells = "".join(f'<div class="kpi"><div class="n">{html.escape(str(v))}</div>'
                    f'<div class="l">{html.escape(str(l))}</div></div>' for v, l in kpis)
    return f'<div class="kpis">{cells}</div>'


def candidate_table(rows, columns, search_keys=None, numeric_keys=None, page_size=25,
                    default_sort=None, extra_filters=None, sources_col=None):
    """
    Build a sortable / filterable / paginated table.
    rows: list of dicts. columns: list of (key, header). search_keys: keys the search box scans.
    numeric_keys: keys sorted numerically. extra_filters: list of (key, label) -> one pull-down
    menu per axis (pick a subset; auto-populated with "all" + the distinct values).
    sources_col=(count_key, list_key): render the corroboration column keyed on count_key as
    "<count>" + a pill per source in list_key, and sort it by the (numeric) count.
    Returns an HTML fragment (controls + table + pager + <script>).
    """
    search_keys = search_keys or [c[0] for c in columns]
    numeric_keys = list(numeric_keys or [])
    src_count, src_list = sources_col if sources_col else (None, None)
    if src_count and src_count not in numeric_keys:
        numeric_keys.append(src_count)        # rank by cross-KG support
    default_sort = default_sort or columns[0][0]
    tid = "tbl"
    filt_html = ('<input id="q" placeholder="search…" oninput="resetPage()">')
    for key, label in (extra_filters or []):
        vals = sorted({str(r.get(key, "")) for r in rows if r.get(key, "") != ""})
        opts = "".join(f"<option>{html.escape(v)}</option>" for v in vals)
        filt_html += f'<select id="f_{key}" onchange="resetPage()"><option value="">{html.escape(label)}: all</option>{opts}</select>'
    sizes = sorted({25, 50, 100, int(page_size)} - {0})
    psize_opts = "".join(f'<option value="{s}"{" selected" if s == page_size else ""}>{s} / page</option>'
                         for s in sizes)
    psize_opts += f'<option value="0"{" selected" if not page_size else ""}>show all</option>'
    filt_html += (f'<select id="psize" onchange="resetPage()">{psize_opts}</select>'
                  '<span class="muted" id="count"></span>')
    cfg = json.dumps({"columns": columns, "search": search_keys, "numeric": numeric_keys,
                      "sort": default_sort, "filters": [f[0] for f in (extra_filters or [])],
                      "sources": ({"count": src_count, "list": src_list} if src_count else None)})
    data = json.dumps(rows)
    js = """
<script>
(function(){
const DATA=__DATA__, CFG=__CFG__;
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
let sortk=CFG.sort, asc=false, page=1;
const hdr=document.getElementById('hdr');
CFG.columns.forEach(function(c){var th=document.createElement('th');th.textContent=c[1];
  th.onclick=function(){if(sortk===c[0])asc=!asc;else{sortk=c[0];asc=false;}resetPage();};hdr.appendChild(th);});
function rows(){
  var q=(document.getElementById('q').value||'').toLowerCase();
  var r=DATA.filter(function(d){
    for(var i=0;i<CFG.filters.length;i++){var k=CFG.filters[i];var el=document.getElementById('f_'+k);
      if(el&&el.value&&String(d[k])!==el.value)return false;}
    if(!q)return true;
    return CFG.search.some(function(k){return String(d[k]||'').toLowerCase().indexOf(q)>=0;});
  });
  var num=CFG.numeric.indexOf(sortk)>=0;
  r.sort(function(a,b){var x=a[sortk],y=b[sortk];
    if(num){x=parseFloat(x);y=parseFloat(y);x=isNaN(x)?-1e9:x;y=isNaN(y)?-1e9:y;return asc?x-y:y-x;}
    x=String(x==null?'':x).toLowerCase();y=String(y==null?'':y).toLowerCase();
    return asc?x.localeCompare(y):y.localeCompare(x);});
  return r;
}
function render(){
  var r=rows(), ps=parseInt(document.getElementById('psize').value,10); if(!ps)ps=r.length||1;
  var pages=Math.max(1,Math.ceil((r.length||1)/ps)); if(page>pages)page=pages; if(page<1)page=1;
  var start=(page-1)*ps, end=Math.min(start+ps,r.length);
  var tb=document.querySelector('#__TID__ tbody'); tb.innerHTML='';
  r.slice(start,end).forEach(function(d){var tr=document.createElement('tr');
    tr.innerHTML=CFG.columns.map(function(c){var k=c[0];
      if(CFG.sources&&k===CFG.sources.count){
        var pills=(d[CFG.sources.list]||[]).map(function(x){return '<span class="pill">'+esc(x)+'</span>';}).join(' ');
        return '<td><b>'+esc(d[k]==null?'':d[k])+'</b> '+pills+'</td>';}
      return '<td>'+esc(d[k])+'</td>';}).join('');
    tb.appendChild(tr);});
  document.getElementById('count').textContent=(r.length?(start+1):0)+'\\u2013'+end+' of '+r.length+
     (r.length!==DATA.length?' (of '+DATA.length+' total)':'')+' shown';
  document.getElementById('pageinfo').textContent='page '+page+' / '+pages;
  document.getElementById('prev').disabled=(page<=1); document.getElementById('next').disabled=(page>=pages);
}
window.resetPage=function(){page=1;render();}; window.go=function(d){page+=d;render();};
render();
})();
</script>"""
    js = (js.replace("__DATA__", data.replace("</", "<\\/"))
            .replace("__CFG__", cfg.replace("</", "<\\/"))
            .replace("__TID__", tid))
    return (f'<div class="controls">{filt_html}</div>'
            f'<div style="overflow-x:auto"><table id="{tid}"><thead><tr id="hdr"></tr></thead><tbody></tbody></table></div>'
            f'<div class="pager"><button id="prev" onclick="go(-1)">&lsaquo; Prev</button>'
            f'<span class="muted" id="pageinfo"></span><button id="next" onclick="go(1)">Next &rsaquo;</button></div>'
            + js)


def build_report(title, subtitle, meta, kpis, body_blocks, out, table=None, footer=""):
    body = "\n".join(body_blocks)
    tbl = table or ""
    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header><h1>{html.escape(title)}</h1><div class="sub">{html.escape(subtitle)}</div>
<div class="meta">{meta}</div></header>
<div class="wrap">{kpi_row(kpis)}
{body}
{tbl}
</div>
<footer>{footer}</footer></body></html>"""
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[build_report_html] wrote {out} ({len(page):,} bytes)")
    return out


def _demo():
    # Example is a water / PFAS site ranking, but the builder is domain-neutral — swap in any
    # entities, columns, subset filters, and source KGs (justice, supply chain, biomedicine, …).
    raw = [  # site, state, medium, priority score, tier, corroborating KGs
        ("Wellfield A-12", "ME", "groundwater",   63.3, "A", ["sawgraph", "hydrologykg", "spatialkg"]),
        ("Intake B-4",     "NH", "surface water", 57.6, "A", ["sawgraph", "spatialkg"]),
        ("Lagoon C-1",     "ME", "sediment",      54.1, "A", ["sawgraph", "fiokg", "spatialkg"]),
        ("Spring D-7",     "VT", "groundwater",   52.0, "B", ["sawgraph", "hydrologykg"]),
        ("Reservoir E-2",  "MA", "surface water", 49.8, "B", ["sawgraph"]),
        ("Field F-9",      "NH", "soil",          47.2, "B", ["sawgraph", "fiokg"]),
        ("Creek G-3",      "ME", "surface water", 44.9, "C", ["sawgraph"]),
        ("Well H-6",       "VT", "groundwater",   41.5, "C", ["sawgraph", "spatialkg"]),
    ]
    rows = [{"name": s, "region": st, "medium": md, "score": sc, "tier": t,
             "sources": src, "nsrc": len(src)} for s, st, md, sc, t, src in raw]
    tbl = candidate_table(
        rows,
        columns=[("name", "site"), ("region", "state"), ("medium", "medium"),
                 ("nsrc", "sources (n)"), ("score", "priority"), ("tier", "tier")],
        search_keys=["name", "region", "medium"], numeric_keys=["score"], default_sort="score",
        extra_filters=[("tier", "tier"), ("region", "state"), ("medium", "medium")],  # subset pull-downs
        sources_col=("nsrc", "sources"))                                              # count + source pills
    tip = ('<div class="muted" style="margin:8px 0 2px"><b>Tip:</b> click a header to sort; use the '
           'pull-down menus to filter by tier, state, or medium; <b>sources (n)</b> = number of '
           'federation KGs corroborating each row (pills show which).</div>')
    build_report("Demo OKN Report", "self-contained interactive report (example: PFAS in water)",
                 "Date · OKN federated SPARQL · Model",
                 kpis=[("8", "priority sites"), ("3", "media"), ("4", "source KGs")],
                 body_blocks=['<div class="note"><b>Framing.</b> observational; hypothesis generation, '
                              'not a regulatory determination.</div>',
                              "<h2>Ranked results</h2>", tip],
                 table=tbl, out="demo_report.html", footer="OKN federation · demo")


if __name__ == "__main__":
    import sys
    _demo() if "--demo" in sys.argv else print(__doc__)

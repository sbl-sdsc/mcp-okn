"""
build_report_html.py — assemble a self-contained interactive HTML report for an OKN analysis.

Everything is inlined (CSS, JS, figures as base64) so the .html is a single portable file.

PREFERRED: render the HTML FROM the finished Markdown report, so the prose is authored ONCE and
the two files can never disagree. The .html adds only what Markdown cannot express — KPI cards,
base64-embedded figures, and the interactive results table:

    from build_report_html import (candidate_table, build_report_from_markdown,
                                    load_stats, kpis_from_stats)
    stats = load_stats("stats.json")             # the single source of the NUMBERS
    tbl = candidate_table(rows,
        columns=[("name","entity"),("region","region"),("nsrc","sources (n)"),
                 ("score","score"),("tier","tier")],
        search_keys=["name","region"], numeric_keys=["score"],
        extra_filters=[("tier","tier"),("region","region")],  # subset pull-down menus
        sources_col=("nsrc","sources"))                       # corroboration count + source pills
    build_report_from_markdown("study_report.md", out="study_report.html", stats=stats,
        kpis=kpis_from_stats(stats, [("n_entities","entities"),("n_source_kgs","source KGs")]),
        table=tbl)                                       # spliced in at the <!-- RESULTS_TABLE --> marker
    # In study_report.md: numbers are `{{key}}` placeholders (filled from stats.json), figures are
    # `![alt](figures/figN.png)` + a blockquote legend beneath, and `<!-- RESULTS_TABLE -->` in §9
    # marks where the interactive table belongs. Fill the delivered .md with `fill_stats` so it reads
    # standalone; the .html then inherits those numbers by rendering it, and the KPI cards come from
    # the same `stats` dict — one edit in stats.json updates all three.

`build_report_from_markdown` SELF-VERIFIES: after writing it runs
`check_report_parity(md, html)` and prints `[check_report_parity] PASS …` — the report is not
delivered until you have seen that PASS. It FAILS, naming the sections, if any `##`/`###` heading is
missing or the HTML is much shorter than the .md (self-containment/numbers/markup checks do not catch
a dropped-section build). If you build the HTML any other way, run the check yourself
(`check_report_parity(md, html)` or `--check report.md report.html`) and see PASS before delivering.

Do NOT re-author the report's prose as HTML `body_blocks`, and do NOT write your own builder that
takes raw HTML sections — that is the prose-drift / highlights-reel failure mode. The low-level
`build_report(...)` / `figure_block(...)` path below still exists for HTML-only one-offs that have no
Markdown source, but reports must use the render-from-Markdown path above.

The candidate table is sortable (click any header), filterable (search box + subset pull-down
menus), and PAGINATED (default 25/page, Prev/Next) — never dump a 900-row table in full. It also
carries a `sources (n)` corroboration column (count of federation KGs supporting each candidate +
one pill per source). Run `python build_report_html.py --demo-md` for the render-from-Markdown demo
(or `--demo` for the low-level path).
"""

from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path

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
h3{margin:22px 0 6px;font-size:16px}h4{margin:16px 0 4px;font-size:14px}
blockquote{background:#fff8f5;border-left:4px solid var(--accent);border-radius:9px;padding:10px 15px;margin:12px 0;font-size:13.5px;color:#3a4452}
blockquote p{margin:0}a{color:var(--accent)}
code{background:#eef2f7;border-radius:5px;padding:1px 5px;font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
pre{background:#1f2a37;color:#e5e7eb;border-radius:9px;padding:12px 15px;overflow-x:auto;font-size:12.5px}
pre code{background:none;color:inherit;padding:0}
ul,ol{margin:8px 0;padding-left:24px}li{margin:3px 0}
hr{border:none;border-top:1px solid var(--line);margin:22px 0}
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
    with Path(path).open("rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def figure_block(img_path, caption_html, alt="figure"):
    """<img> (base64) + a caption legend div BELOW it. Put the full scientific legend here.
    Pass `alt` for a descriptive accessibility label (screen readers)."""
    return f'<img src="{embed_img(img_path)}" alt="{html.escape(alt)}">\n<div class="figcap">{caption_html}</div>'


def kpi_row(kpis):
    cells = "".join(
        f'<div class="kpi"><div class="n">{html.escape(str(v))}</div>'
        f'<div class="l">{html.escape(str(label))}</div></div>'
        for v, label in kpis
    )
    return f'<div class="kpis">{cells}</div>'


def candidate_table(
    rows,
    columns,
    search_keys=None,
    numeric_keys=None,
    page_size=25,
    default_sort=None,
    extra_filters=None,
    sources_col=None,
):
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
        numeric_keys.append(src_count)  # rank by cross-KG support
    default_sort = default_sort or columns[0][0]
    tid = "tbl"
    filt_html = '<input id="q" placeholder="search…" oninput="resetPage()">'
    for key, label in extra_filters or []:
        vals = sorted({str(r.get(key, "")) for r in rows if r.get(key, "") != ""})
        opts = "".join(f"<option>{html.escape(v)}</option>" for v in vals)
        filt_html += f'<select id="f_{key}" onchange="resetPage()"><option value="">{html.escape(label)}: all</option>{opts}</select>'
    sizes = sorted({25, 50, 100, int(page_size)} - {0})
    psize_opts = "".join(
        f'<option value="{s}"{" selected" if s == page_size else ""}>{s} / page</option>'
        for s in sizes
    )
    psize_opts += (
        f'<option value="0"{" selected" if not page_size else ""}>show all</option>'
    )
    filt_html += (
        f'<select id="psize" onchange="resetPage()">{psize_opts}</select>'
        '<span class="muted" id="count"></span>'
    )
    cfg = json.dumps(
        {
            "columns": columns,
            "search": search_keys,
            "numeric": numeric_keys,
            "sort": default_sort,
            "filters": [f[0] for f in (extra_filters or [])],
            "sources": ({"count": src_count, "list": src_list} if src_count else None),
        }
    )
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
    js = (
        js.replace("__DATA__", data.replace("</", "<\\/"))
        .replace("__CFG__", cfg.replace("</", "<\\/"))
        .replace("__TID__", tid)
    )
    return (
        f'<div class="controls">{filt_html}</div>'
        f'<div style="overflow-x:auto"><table id="{tid}"><thead><tr id="hdr"></tr></thead><tbody></tbody></table></div>'
        f'<div class="pager"><button id="prev" onclick="go(-1)">&lsaquo; Prev</button>'
        f'<span class="muted" id="pageinfo"></span><button id="next" onclick="go(1)">Next &rsaquo;</button></div>'
        + js
    )


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
    with Path(out).open("w", encoding="utf-8") as f:
        f.write(page)
    print(f"[build_report_html] wrote {out} ({len(page):,} bytes)")
    return out


# ---------------------------------------------------------------------------
# Render the HTML report FROM the Markdown report — one narrative, two renderings.
#
# The .md is the single source of the prose; the .html is generated from it and
# adds only what Markdown cannot express: KPI cards, base64-embedded figures, and
# the interactive results table. Never hand-author HTML that restates the .md —
# that is the prose-drift failure mode this path exists to make impossible.
# ---------------------------------------------------------------------------


def _img_tag(src, alt, base_dir=""):
    """<img> for a Markdown image ref. Local PNGs are base64-embedded so the page
    stays self-contained; data:/http(s) URIs pass through unchanged."""
    if src.startswith(("data:", "http://", "https://")):
        uri = src
    else:
        uri = embed_img(str(Path(base_dir) / src) if base_dir else src)
    return f'<img src="{uri}" alt="{html.escape(alt)}">'


def _inline(text, base_dir=""):
    """Inline Markdown → HTML: code spans, images, links, bold, italic. Text is
    HTML-escaped first so literals like `FDR < 0.05` render correctly; the markup
    tags are inserted after escaping."""
    codes = []
    text = re.sub(
        r"`([^`]+)`",
        lambda m: (codes.append(m.group(1)), f"\x00{len(codes) - 1}\x00")[1],
        text,
    )
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: _img_tag(m.group(2), m.group(1), base_dir),
        text,
    )
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<![_\w])_([^_\n]+)_(?![_\w])", r"<em>\1</em>", text)
    return re.sub(
        r"\x00(\d+)\x00",
        lambda m: "<code>" + html.escape(codes[int(m.group(1))]) + "</code>",
        text,
    )


def md_to_html(md, base_dir=""):
    """Minimal, dependency-free Markdown → HTML for report bodies. Handles ATX
    headings, GFM tables, unordered/ordered lists, blockquotes, fenced code,
    horizontal rules, images (base64-embedded), and paragraphs with inline markup.
    A line that begins with `<` is passed through as raw HTML (so an inline
    `<!-- RESULTS_TABLE -->` marker or a hand-written callout survives verbatim).
    A standalone image followed by a blockquote becomes an <img> + `figcap` legend."""

    def is_li(s):
        return bool(re.match(r"^[-*+]\s+", s) or re.match(r"^\d+\.\s+", s))

    def is_hr(s):
        return bool(re.match(r"^(-{3,}|\*{3,}|_{3,})$", s))

    lines = md.split("\n")
    n = len(lines)
    out = []
    i = 0
    while i < n:
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):  # fenced code
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            esc = (
                "\n".join(code)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            out.append(f"<pre><code>{esc}</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)  # heading
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2), base_dir)}</h{lvl}>")
            i += 1
            continue
        if is_hr(s):  # horizontal rule
            out.append("<hr>")
            i += 1
            continue
        if s.startswith("<"):  # raw HTML / table marker
            out.append(raw)
            i += 1
            continue
        mi = re.match(
            r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", s
        )  # standalone image (+ legend)
        if mi:
            img = _img_tag(mi.group(2), mi.group(1), base_dir)
            i += 1
            j = i
            while j < n and not lines[j].strip():
                j += 1
            if j < n and lines[j].strip().startswith(">"):
                bq = []
                while j < n and lines[j].strip().startswith(">"):
                    bq.append(re.sub(r"^\s*>\s?", "", lines[j]))
                    j += 1
                cap = _inline(" ".join(x.strip() for x in bq), base_dir)
                out.append(f'{img}\n<div class="figcap">{cap}</div>')
                i = j
            else:
                out.append(img)
            continue
        if (
            "|" in s
            and i + 1 < n
            and "-" in lines[i + 1]
            and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1])
        ):  # GFM table
            header = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{_inline(h, base_dir)}</th>" for h in header)
            trs = "".join(
                "<tr>"
                + "".join(f"<td>{_inline(c, base_dir)}</td>" for c in r)
                + "</tr>"
                for r in body
            )
            out.append(
                f'<div style="overflow-x:auto"><table><thead><tr>{th}</tr>'
                f"</thead><tbody>{trs}</tbody></table></div>"
            )
            continue
        if s.startswith(">"):  # blockquote
            bq = []
            while i < n and lines[i].strip().startswith(">"):
                bq.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(
                f"<blockquote>{_inline(' '.join(x.strip() for x in bq), base_dir)}</blockquote>"
            )
            continue
        if is_li(s):  # list
            ordered = bool(re.match(r"^\d+\.\s+", s))
            items = []
            while i < n and lines[i].strip() and is_li(lines[i].strip()):
                items.append(
                    "<li>"
                    + _inline(
                        re.sub(r"^([-*+]|\d+\.)\s+", "", lines[i].strip()), base_dir
                    )
                    + "</li>"
                )
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        buf = []  # paragraph
        while i < n:
            t = lines[i].strip()
            if (
                not t
                or t.startswith(("#", ">", "```", "<", "|"))
                or is_hr(t)
                or is_li(t)
                or re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", t)
            ):
                break
            buf.append(t)
            i += 1
        out.append("<p>" + _inline(" ".join(buf), base_dir) + "</p>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Single-source the NUMBERS the way we single-source the prose: canonical values
# live in one stats.json, and every appearance is filled from it rather than
# retyped. `{{key}}` placeholders in the Markdown are substituted at render time;
# the KPI cards are built from the same dict — so a figure edited in stats.json
# updates the .md prose, the .html, and the KPI cards at once.
# ---------------------------------------------------------------------------


def load_stats(path="stats.json"):
    """Load the canonical numbers for a report from a single stats.json."""
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def _stat_lookup(stats, key):
    if key in stats:
        return stats[key]
    val = stats  # dotted path into nested dicts (a.b.c)
    for part in key.split("."):
        val = val[part]
    return val


_STAT_TOKEN = re.compile(r"\{\{\s*([\w.]+)\s*(?::([^}]+))?\}\}")


def fill_stats(text, stats, strict=True):
    """Substitute `{{key}}` / `{{key:fmt}}` placeholders in `text` from `stats`.
    `fmt` is a Python format spec — `{{n:,}}` → `1,234`, `{{p:.1f}}` → `3.1`.
    Nested keys use dots (`{{cohort.n}}`). An unknown key raises KeyError under the
    default strict=True (a silent miss would defeat the single-source guarantee);
    set strict=False to leave unmatched tokens in place."""

    def sub(m):
        key, fmt = m.group(1), m.group(2)
        try:
            val = _stat_lookup(stats, key)
        except (KeyError, TypeError):
            if strict:
                raise KeyError(
                    f"stats.json has no key {key!r} for placeholder {m.group(0)!r}"
                ) from None
            return m.group(0)
        return format(val, fmt) if fmt else str(val)

    return _STAT_TOKEN.sub(sub, text)


def kpis_from_stats(stats, spec):
    """Build the KPI card list `[(value, label), …]` from stats.json so the header
    numbers are never retyped. `spec` is `[(key, label) | (key, label, fmt), …]`."""
    out = []
    for item in spec:
        key, label = item[0], item[1]
        fmt = item[2] if len(item) > 2 else None
        val = _stat_lookup(stats, key)
        out.append((format(val, fmt) if fmt else str(val), label))
    return out


def build_report_from_markdown(
    md_path,
    out,
    kpis=None,
    table=None,
    stats=None,
    table_marker="<!-- RESULTS_TABLE -->",
    title=None,
    subtitle=None,
    meta=None,
    footer="",
    verify=True,
):
    """Render a self-contained interactive HTML report FROM the Markdown report.

    The Markdown IS the single source of the prose — pass the finished
    `<study>_report.md` and this renders it, so the .html can never disagree with
    the .md. It adds only the non-prose extras:
      * `stats` (a dict or a path to stats.json) → the single source of the NUMBERS.
        Any `{{key}}` placeholder in the Markdown is filled from it before rendering,
        so a value edited in stats.json updates the .md prose and the .html together.
        (Fill the delivered .md the same way — `fill_stats` — so it reads standalone.)
      * `kpis=[(value, label), …]`  → the KPI cards in the header (chrome, not prose).
        Build them from the same dict with `kpis_from_stats(stats, spec)` so the header
        numbers are never retyped.
      * `table` → the sortable/filterable/paginated results fragment from
        `candidate_table(...)`, spliced in wherever the .md contains the
        `<!-- RESULTS_TABLE -->` marker (put that marker in §9). Without a marker it
        is appended at the end (a warning is printed).
    Figures embed automatically: a standalone `![alt](figures/figN.png)` becomes a
    base64 <img>; a blockquote right after it becomes the figure's `figcap` legend.
    Title / subtitle / meta are lifted from the .md title block (the first `# `,
    the first `### `, and the `**Date:** …` line) unless overridden.

    Self-verifies by default (`verify=True`): after writing, it runs
    `check_report_parity(md_path, out)` and prints PASS/FAIL, so the completeness gate
    is not a separate step to forget. A faithful render always PASSES; a FAIL warns
    that content was dropped and the page must not be shipped.
    """
    with Path(md_path).open(encoding="utf-8") as f:
        md = f.read()
    base_dir = str(Path(md_path).resolve().parent)
    if stats is not None:
        if isinstance(stats, str):
            stats = load_stats(stats)
        md = fill_stats(md, stats)  # single-source the numbers
    lines = md.split("\n")

    def _pop(pattern):
        for idx, line in enumerate(lines):
            m = re.match(pattern, line.strip())
            if m:
                del lines[idx]
                return m
        return None

    if title is None:
        m = _pop(r"^#\s+(.*)$")
        title = m.group(1).strip() if m else "OKN Report"
    if subtitle is None:
        m = _pop(r"^#{3}\s+(.*)$")
        subtitle = m.group(1).strip() if m else ""
    if meta is None:
        m = _pop(r"^(\*\*Date:.*)$")
        meta = m.group(1).strip() if m else ""

    body_html = md_to_html("\n".join(lines).strip(), base_dir)
    if table:
        if table_marker in body_html:
            body_html = body_html.replace(table_marker, table)
        else:
            print(
                f"[build_report_html] WARNING: table_marker {table_marker!r} not found in "
                f"{Path(md_path).name}; appending the results table at the end."
            )
            body_html += "\n" + table

    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header><h1>{html.escape(title)}</h1><div class="sub">{_inline(subtitle, base_dir)}</div>
<div class="meta">{_inline(meta, base_dir)}</div></header>
<div class="wrap">{kpi_row(kpis or [])}
{body_html}
</div>
<footer>{footer}</footer></body></html>"""
    with Path(out).open("w", encoding="utf-8") as f:
        f.write(page)
    print(
        f"[build_report_html] wrote {out} ({len(page):,} bytes) from {Path(md_path).name}"
    )
    # Self-verify: a report is not delivered until it is the WHOLE report. Running
    # the completeness gate here means no separate "remember to check" step to skip —
    # a rendered-from-Markdown page always passes; a FAIL means something dropped
    # content (bad marker, wrong source) and the page must NOT be shipped.
    if verify:
        parity = check_report_parity(md_path, out)
        if not parity["ok"]:
            print(
                "[build_report_html] WARNING: the rendered HTML is NOT a faithful copy "
                "of the Markdown (see the check_report_parity FAIL above). Do NOT deliver "
                "it — fix the source/marker and rebuild."
            )
    return out


# ---------------------------------------------------------------------------
# Completeness gate: is the delivered .html the SAME report as the .md?
#
# Rendering from the .md (build_report_from_markdown) guarantees parity — but only
# if it is actually used. A model that hand-authors the HTML, or writes its own
# builder that takes raw HTML sections, can quietly ship a "highlights" version
# that drops whole sections (typically the unglamorous mandatory ones: §2 Sources,
# §10 Limitations) while keeping the interesting claims. A self-containment / markup
# / numbers check passes on such a file — it never asks whether the HTML contains
# the same report. This check does, independent of how the HTML was built.
# ---------------------------------------------------------------------------


def _visible_text(html_str):
    """Approximate the visible text of an HTML document: drop <script>/<style>
    payloads (JS/CSS, embedded table JSON), then all tags and entities."""
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html_str)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"&[a-zA-Z#0-9]+;", " ", s)


def _word_count(text):
    return len(re.findall(r"\w+", text))


def _norm(text):
    """Lowercase and reduce to words + single spaces, so heading matching is robust
    to punctuation and entities (e.g. `&` vs `&amp;` vs a stripped entity)."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text)).strip().lower()


def check_report_parity(md_path, html_path, min_word_ratio=0.85, ignore_sections=()):
    """Verify the delivered `.html` is the SAME report as `.md` — the completeness gate.

    Method-independent (works whether the HTML was rendered or hand-authored), it
    catches the "condensed highlights" failure: an HTML that drops sections or shrinks
    the prose. Two checks — (1) every Markdown section heading (`##` / `###`) appears
    in the HTML's visible text, and (2) the HTML's visible word count is at least
    `min_word_ratio` of the Markdown's. Prints a PASS/FAIL summary and returns a dict
    `{ok, missing_sections, md_words, html_words, word_ratio, min_word_ratio}`. Run it
    as the final step before delivering — passing self-containment/markup/number checks
    is NOT enough; this confirms the HTML is the whole report. `ignore_sections` skips
    heading texts you deliberately omit (rare).
    """
    md = Path(md_path).read_text(encoding="utf-8")
    html_str = Path(html_path).read_text(encoding="utf-8")
    html_text = _visible_text(html_str)
    html_norm = _norm(html_text)

    missing = []
    for line in md.split("\n"):
        m = re.match(r"^(#{2,3})\s+(.*\S)\s*$", line.strip())
        if not m:
            continue
        heading = m.group(2).strip()
        if heading in ignore_sections:
            continue
        # Match on the heading TEXT, ignoring its section number, so a section that
        # is present but renumbered (e.g. `## 2. Sources used` -> `1. Sources used`)
        # is not falsely reported missing — only genuinely absent content is flagged.
        needle = _norm(re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", heading))
        if needle and needle not in html_norm:
            missing.append(heading)

    md_plain = re.sub(r"<!--.*?-->", " ", md, flags=re.S)  # drop the table marker etc.
    md_plain = re.sub(r"[#>*_`|\-]", " ", md_plain)
    md_words = _word_count(md_plain)
    html_words = _word_count(html_text)
    ratio = html_words / md_words if md_words else 1.0

    ok = not missing and ratio >= min_word_ratio
    print(
        f"[check_report_parity] {'PASS' if ok else 'FAIL'}: "
        f"{html_words}/{md_words} words (ratio {ratio:.2f}, min {min_word_ratio}); "
        f"{len(missing)} missing section(s)"
        + (": " + "; ".join(missing) if missing else "")
    )
    return {
        "ok": ok,
        "missing_sections": missing,
        "md_words": md_words,
        "html_words": html_words,
        "word_ratio": round(ratio, 3),
        "min_word_ratio": min_word_ratio,
    }


def _demo():
    # Example is a water / PFAS site ranking, but the builder is domain-neutral — swap in any
    # entities, columns, subset filters, and source KGs (justice, supply chain, biomedicine, …).
    raw = [  # site, state, medium, priority score, tier, corroborating KGs
        (
            "Wellfield A-12",
            "ME",
            "groundwater",
            63.3,
            "A",
            ["sawgraph", "hydrologykg", "spatialkg"],
        ),
        ("Intake B-4", "NH", "surface water", 57.6, "A", ["sawgraph", "spatialkg"]),
        ("Lagoon C-1", "ME", "sediment", 54.1, "A", ["sawgraph", "fiokg", "spatialkg"]),
        ("Spring D-7", "VT", "groundwater", 52.0, "B", ["sawgraph", "hydrologykg"]),
        ("Reservoir E-2", "MA", "surface water", 49.8, "B", ["sawgraph"]),
        ("Field F-9", "NH", "soil", 47.2, "B", ["sawgraph", "fiokg"]),
        ("Creek G-3", "ME", "surface water", 44.9, "C", ["sawgraph"]),
        ("Well H-6", "VT", "groundwater", 41.5, "C", ["sawgraph", "spatialkg"]),
    ]
    rows = [
        {
            "name": s,
            "region": st,
            "medium": md,
            "score": sc,
            "tier": t,
            "sources": src,
            "nsrc": len(src),
        }
        for s, st, md, sc, t, src in raw
    ]
    tbl = candidate_table(
        rows,
        columns=[
            ("name", "site"),
            ("region", "state"),
            ("medium", "medium"),
            ("nsrc", "sources (n)"),
            ("score", "priority"),
            ("tier", "tier"),
        ],
        search_keys=["name", "region", "medium"],
        numeric_keys=["score"],
        default_sort="score",
        extra_filters=[
            ("tier", "tier"),
            ("region", "state"),
            ("medium", "medium"),
        ],  # subset pull-downs
        sources_col=("nsrc", "sources"),
    )  # count + source pills
    tip = (
        '<div class="muted" style="margin:8px 0 2px"><b>Tip:</b> click a header to sort; use the '
        "pull-down menus to filter by tier, state, or medium; <b>sources (n)</b> = number of "
        "federation KGs corroborating each row (pills show which).</div>"
    )
    build_report(
        "Demo OKN Report",
        "self-contained interactive report (example: PFAS in water)",
        "Date · OKN federated SPARQL · Model",
        kpis=[("8", "priority sites"), ("3", "media"), ("4", "source KGs")],
        body_blocks=[
            '<div class="note"><b>Framing.</b> observational; hypothesis generation, '
            "not a regulatory determination.</div>",
            "<h2>Ranked results</h2>",
            tip,
        ],
        table=tbl,
        out="demo_report.html",
        footer="OKN federation · demo",
    )


def _demo_md():
    # Same PFAS example, but the prose is authored ONCE as Markdown and the HTML is
    # RENDERED from it — the pattern every real report should follow. The .md below
    # stands in for `<study>_report.md`; only the KPI cards and the interactive table
    # are supplied separately (they are not prose).
    raw = [
        (
            "Wellfield A-12",
            "ME",
            "groundwater",
            63.3,
            "A",
            ["sawgraph", "hydrologykg", "spatialkg"],
        ),
        ("Intake B-4", "NH", "surface water", 57.6, "A", ["sawgraph", "spatialkg"]),
        ("Lagoon C-1", "ME", "sediment", 54.1, "A", ["sawgraph", "fiokg", "spatialkg"]),
        ("Spring D-7", "VT", "groundwater", 52.0, "B", ["sawgraph", "hydrologykg"]),
    ]
    rows = [
        {
            "name": s,
            "region": st,
            "medium": md,
            "score": sc,
            "tier": t,
            "sources": src,
            "nsrc": len(src),
        }
        for s, st, md, sc, t, src in raw
    ]
    tbl = candidate_table(
        rows,
        columns=[
            ("name", "site"),
            ("region", "state"),
            ("medium", "medium"),
            ("nsrc", "sources (n)"),
            ("score", "priority"),
            ("tier", "tier"),
        ],
        search_keys=["name", "region", "medium"],
        numeric_keys=["score"],
        default_sort="score",
        extra_filters=[("tier", "tier"), ("region", "state"), ("medium", "medium")],
        sources_col=("nsrc", "sources"),
    )
    # Canonical numbers live in one stats.json; the Markdown references them as {{key}}
    # placeholders and the KPI cards are built from the same dict — edit a number once.
    stats = {
        "n_sites": 4,
        "n_media": 3,
        "n_source_kgs": 4,
        "n_rows_scanned": 1240,
        "top_site": "Wellfield A-12",
    }
    with Path("demo_stats.json").open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    md = """# Demo OKN Report
### self-contained interactive report, rendered from Markdown (example: PFAS in water)

**Date:** 2026-07-16 · **Endpoint:** OKN federated SPARQL · **Model:** demo

> **Framing (non-negotiable).** Observational, county-level associations; hypothesis
> generation, not a regulatory determination. FDR < 0.05 throughout.

**Abbreviations.** PFAS = per- and polyfluoroalkyl substances; KG = knowledge graph.

## 1. Executive summary
Of **{{n_rows_scanned:,}}** candidate sites scanned, **{{n_sites}}** rank above the tier-A
threshold, led by **{{top_site}}** (ME, groundwater). The ranking is corroborated across up to
three federation KGs per site — see §9.

## 9. Full ranked results
Full workbook: `demo_results.xlsx`. Click a header to sort; use the pull-downs to filter by
tier, state, or medium; **sources (n)** counts the federation KGs corroborating each row.

<!-- RESULTS_TABLE -->

The tier-A sites cluster in northern New England, consistent with the sampling density there.
"""
    md_path = "demo_report_from_md.md"
    # The delivered .md must read standalone → fill its placeholders from stats too.
    with Path(md_path).open("w", encoding="utf-8") as f:
        f.write(fill_stats(md, stats))
    build_report_from_markdown(
        md_path,
        out="demo_report_from_md.html",
        stats=stats,
        kpis=kpis_from_stats(
            stats,
            [
                ("n_sites", "priority sites"),
                ("n_media", "media"),
                ("n_source_kgs", "source KGs"),
            ],
        ),
        table=tbl,
        footer="OKN federation · demo (rendered from Markdown)",
    )


if __name__ == "__main__":
    import sys

    if "--demo-md" in sys.argv:
        _demo_md()
    elif "--demo" in sys.argv:
        _demo()
    elif "--check" in sys.argv:
        # python build_report_html.py --check report.md report.html
        args = [a for a in sys.argv[1:] if a != "--check"]
        if len(args) != 2:
            print("usage: build_report_html.py --check <report.md> <report.html>")
            sys.exit(2)
        result = check_report_parity(args[0], args[1])
        sys.exit(0 if result["ok"] else 1)
    else:
        print(__doc__)

"""Render README.md -> a print-ready PDF with the figures embedded inline.

markdown (tables + fenced code) -> styled HTML -> weasyprint PDF.
Relative figure paths (figures/*.png) resolve via base_url, so images embed inline.
"""
import os, markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "README.md")
OUT = os.path.join(HERE, "spoke-genelab-nelson2021-reproduction.pdf")

with open(SRC, encoding="utf-8") as f:
    md_text = f.read()

body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "sane_lists", "toc"],
    output_format="html5",
)

CSS = """
@page { size: A4; margin: 15mm 13mm 16mm 13mm;
        @bottom-center { content: "Reproducing Nelson et al. 2021  ·  spoke-genelab cross-graph use case  ·  p. " counter(page);
                         font-family: 'DejaVu Sans', sans-serif; font-size: 7.5pt; color: #888; } }
* { box-sizing: border-box; }
body { font-family: 'DejaVu Sans', 'Noto Sans', sans-serif; font-size: 10pt; line-height: 1.45;
       color: #1b1b1b; }
h1 { font-size: 19pt; color: #14397d; margin: 0 0 6px; line-height: 1.2;
     border-bottom: 3px solid #14397d; padding-bottom: 6px; }
h2 { font-size: 13.5pt; color: #14397d; margin: 18px 0 6px; padding-bottom: 3px;
     border-bottom: 1px solid #c9d4ea; page-break-after: avoid; }
h3 { font-size: 11pt; color: #333; margin: 12px 0 4px; page-break-after: avoid; }
p { margin: 6px 0; }
a { color: #1a5fb4; text-decoration: none; word-break: break-word; }
strong { color: #111; }
blockquote { border-left: 3px solid #14397d; background: #f3f6fc; margin: 8px 0;
             padding: 5px 12px; font-style: italic; color: #2a2a2a; }
ul, ol { margin: 6px 0 6px 0; padding-left: 20px; }
li { margin: 2px 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 8.6pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #c4ccd8; padding: 4px 7px; text-align: left; vertical-align: top; }
th { background: #eaf0fa; color: #14397d; font-weight: bold; }
tr:nth-child(even) td { background: #f7f9fc; }
pre { background: #f5f6f8; border: 1px solid #dde1e8; border-radius: 4px; padding: 8px 10px;
      font-family: 'DejaVu Sans Mono', monospace; font-size: 7.6pt; line-height: 1.35;
      white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; page-break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt;
       background: #eef0f3; padding: 0.5px 3px; border-radius: 3px; word-break: break-word; }
pre code { background: none; padding: 0; font-size: 7.6pt; }
img { max-width: 100%; height: auto; display: block; margin: 10px auto; border: 1px solid #e2e2e2; }
hr { border: none; border-top: 1px solid #d0d0d0; margin: 14px 0; }
"""

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>{body}</body></html>"""

HTML(string=html, base_url=HERE).write_pdf(OUT)
print("Wrote", OUT, "(", round(os.path.getsize(OUT) / 1024), "KB )")

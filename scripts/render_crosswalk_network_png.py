#!/usr/bin/env python3
"""Render docs/crosswalks/crosswalk-network.png from the .html (single source).

Parses the SAME `DOM` + `R` data embedded in crosswalk-network.html and draws a
static version with the identical visual encoding the interactive page uses:
domain colour, edge width proportional to log10(verified count), one edge per
crosswalk (parallel crosswalks fan out), and bridge line-style (dashed =
ubergraph, dotted = wikidata). Run after build_crosswalk_network.py so the PNG
stays in lock-step with the HTML.

    python scripts/render_crosswalk_network_png.py
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs" / "crosswalks" / "crosswalk-network.html"
PNG = ROOT / "docs" / "crosswalks" / "crosswalk-network.png"

html = HTML.read_text(encoding="utf-8")
DOM = {
    c: (label, col)
    for c, label, col in re.findall(
        r'(\w):\["([^"]+)","(#[0-9A-Fa-f]+)"\]',
        re.search(r"const DOM=\{(.*?)\};", html).group(1),
    )
}
i0 = html.find("const R=[")
i1 = html.find("\n];", i0)
R = json.loads(html[i0 + len("const R=") : i1].rstrip() + "]")
hdr = re.search(
    r"(\d+) knowledge graphs, (\d+) verified crosswalks \(verified ([^)]*)\)", html
)
n_kg, n_xw, date = hdr.group(1), hdr.group(2), hdr.group(3)


def eff(w):
    return max(w) if isinstance(w, list) else w


def style(key):
    k = (key or "").lower()
    return (
        (0, (6, 3)) if "ubergraph" in k else ((0, (1, 2)) if "wikidata" in k else "-")
    )


# one edge per crosswalk; a genuine 3-KG row (no bridge) routes as two segments
links = []
for dom, kgs, w, key in R:
    st = style(key)
    if len(kgs) == 3:
        links.append([kgs[0], kgs[1], dom, eff(w), st])
        links.append([kgs[1], kgs[2], dom, eff(w), st])
    else:
        links.append([kgs[0], kgs[1], dom, eff(w), st])
pg = defaultdict(list)
for L in links:
    pg[tuple(sorted((L[0], L[1])))].append(L)
for grp in pg.values():
    n = len(grp)
    for i, L in enumerate(grp):
        L.append(0.0 if n == 1 else (i - (n - 1) / 2) / max(1, (n - 1)))  # curv
        L.append(n)
nodeset = {x for L in links for x in (L[0], L[1])}
nbr = defaultdict(set)
for L in links:
    nbr[L[0]].add(L[1])
    nbr[L[1]].add(L[0])
deg = {n: len(nbr[n]) for n in nodeset}

maxlog = math.log10(681045)


def lw(w):
    return 0.8 + 6.2 * (math.log10(max(w, 1))) / maxlog


def nr(n):
    return min(13, 5 + math.sqrt(deg[n]) * 2)


G = nx.Graph()
G.add_nodes_from(nodeset)
for pr, grp in pg.items():
    G.add_edge(pr[0], pr[1], weight=0.3 + lw(max(L[3] for L in grp)) * 0.12)
pos = nx.spring_layout(G, k=0.62, iterations=600, weight="weight", seed=11)


def bez(s, c, t, n=26):
    ts = np.linspace(0, 1, n)
    return (
        (1 - ts) ** 2 * s[0] + 2 * (1 - ts) * ts * c[0] + ts**2 * t[0],
        (1 - ts) ** 2 * s[1] + 2 * (1 - ts) * ts * c[1] + ts**2 * t[1],
    )


fig, ax = plt.subplots(figsize=(14.5, 10.5), dpi=150)
fig.patch.set_facecolor("#faf9f5")
ax.set_facecolor("#faf9f5")
for a, b, dom, w, st, curv, par in sorted(links, key=lambda L: lw(L[3])):
    s = np.array(pos[a])
    t = np.array(pos[b])
    d = t - s
    dl = np.hypot(*d) or 1
    u = np.array([-d[1] / dl, d[0] / dl])
    kw = {
        "color": DOM[dom][1],
        "lw": lw(w) * 1.2,
        "alpha": 0.65,
        "linestyle": st,
        "solid_capstyle": "round",
        "dash_capstyle": "round",
        "zorder": 1,
    }
    if abs(curv) < 1e-9:
        ax.plot([s[0], t[0]], [s[1], t[1]], **kw)
    else:
        c = (s + t) / 2 + u * curv * (0.10 + dl * 0.34) * min(3, par / 2)
        bx, by = bez(s, c, t)
        ax.plot(bx, by, **kw)
for n in nodeset:
    x, y = pos[n]
    ax.scatter(
        [x],
        [y],
        s=(nr(n) * 2.3) ** 2,
        facecolor="#ffffff",
        edgecolor="#cfccc2",
        linewidths=1,
        zorder=3,
    )
    ax.annotate(
        n,
        (x, y),
        xytext=(0, nr(n) * 1.5 + 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#1a1a18",
        alpha=0.72,
        zorder=4,
    )
dom_h = [Line2D([0], [0], color=c, lw=4, label=label) for (label, c) in DOM.values()]
sty_h = [
    Line2D([0], [0], color="#5f5e5a", lw=2, linestyle="-", label="direct join"),
    Line2D(
        [0],
        [0],
        color="#5f5e5a",
        lw=2,
        linestyle=(0, (6, 3)),
        label="bridged via ubergraph",
    ),
    Line2D(
        [0],
        [0],
        color="#5f5e5a",
        lw=2,
        linestyle=(0, (1, 2)),
        dash_capstyle="round",
        label="bridged via wikidata",
    ),
]
leg1 = ax.legend(
    handles=dom_h,
    loc="lower center",
    ncol=5,
    frameon=False,
    fontsize=9,
    bbox_to_anchor=(0.5, -0.035),
    handlelength=1.6,
    columnspacing=1.4,
)
ax.add_artist(leg1)
ax.legend(
    handles=sty_h,
    loc="lower center",
    ncol=3,
    frameon=False,
    fontsize=8.5,
    bbox_to_anchor=(0.5, -0.08),
    handlelength=2.4,
    columnspacing=1.8,
)
ax.set_title(
    f"Proto-OKN cross-KG crosswalk network — {n_kg} knowledge graphs, {n_xw} verified crosswalks (verified {date})\n"
    "one edge per crosswalk (parallel crosswalks fan out) · colour = domain · width ∝ log₁₀(verified count) · "
    "dashed = ubergraph-bridged, dotted = wikidata-bridged",
    fontsize=11.5,
    color="#1a1a18",
    pad=14,
)
ax.axis("off")
ax.margins(0.06)
plt.tight_layout()
plt.savefig(PNG, dpi=150, facecolor="#faf9f5", bbox_inches="tight")
print(f"wrote {PNG.relative_to(ROOT)} — {len(links)} edges, {len(nodeset)} nodes")

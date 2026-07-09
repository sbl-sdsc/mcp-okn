"""
okn_figstyle.py — matplotlib conventions for OKN analysis-report figures.

Why this exists: hand-built report figures repeatedly hit the same problems — legends overlapping
the plot, fonts too small to read, inconsistent colours, figure numbers that drift out of order.
This module makes those hard to get wrong. Import it at the top of every figure script:

    from okn_figstyle import apply_style, panel_title, legend_outside, diverging_heatmap, finalize
    apply_style()

Then build panels as usual and call finalize(fig, number, path) to save. Colour convention for
signed values (e.g. a change-vs-baseline / anomaly / z-score field, or a log2 fold-change):
negative = blue, positive = red (diverging). Run `python okn_figstyle.py --demo` to render a figure that
exercises every helper (bars + legend + donut + diverging heatmap).

Geographic data: use `osm_basemap(ax, lons, lats, ...)` (static, geopandas + contextily) or
`folium_osm_map(rows, ...)` (interactive, folium) — always plot on an OpenStreetMap-tiled basemap,
never a bare longitude/latitude scatter on empty axes. `python okn_figstyle.py --demo-map` shows both.

All helpers keep legends OUTSIDE the axes and enforce font floors. After saving, always open the
PNG and confirm there is no overlap and the text is legible at final size.
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import html

# ---- font floors (points). Small multiples shrink text fast; do not go below these. ----
FONT = dict(tick=8, annot=8, axis=9.5, legend=8.5, title=11.5, caption=8)
# ---- palette ----
UP = "#c0392b"       # up / positive signed value (red)
DOWN = "#2471a3"     # down / negative signed value (blue) — red/blue diverging is CVD-safe
NEUTRAL = "#7f8c8d"
# Categorical THEME palette: colourblind-safe (Okabe–Ito). Still pair colour with another channel
# (labels, hatching, order) — never encode a category by colour alone.
THEME = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9",
         "#D55E00", "#F0E442", "#999999", "#000000", "#6A3D9A"]


def apply_style():
    """Set global rcParams: readable fonts, clean spines, sane defaults."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": FONT["axis"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": FONT["title"],
        "axes.labelsize": FONT["axis"],
        "xtick.labelsize": FONT["tick"],
        "ytick.labelsize": FONT["tick"],
        "legend.fontsize": FONT["legend"],
        "figure.dpi": 110,
    })


def panel_title(ax, letter, text, fontsize=None):
    """Bold 'A   Title' at the top-left of a panel (paper convention)."""
    ax.set_title(f"{letter}   {text}", loc="left", fontweight="bold",
                 fontsize=fontsize or FONT["title"], pad=8)


def legend_outside(ax, handles=None, labels=None, where="below", title=None, ncol=1, fontsize=None):
    """
    Place a legend OUTSIDE the axes so it can never overlap the plot.
    where: 'below' (under the axes) or 'right' (to the right) keep it fully outside. Any matplotlib
    corner string ('upper right', 'lower left', …) places it AT that corner INSIDE the axes — use
    only when that corner is provably empty (e.g. a bar chart with a tall left bar).
    """
    fs = fontsize or FONT["legend"]
    kw = dict(frameon=False, fontsize=fs, title=title, ncol=ncol)
    if where == "below":
        kw["bbox_to_anchor"] = (0.5, -0.12); loc = "upper center"
    elif where == "right":
        kw["bbox_to_anchor"] = (1.02, 0.5); loc = "center left"
    else:
        loc = where   # a named inside corner; matplotlib anchors it correctly with no bbox override
    if handles is not None:
        return ax.legend(handles, labels, loc=loc, **kw)
    return ax.legend(loc=loc, **kw)


def theme_legend(ax, mapping, where="below", title="theme"):
    """Legend from a {label: color} mapping (for theme-coloured bars). Defaults to BELOW the axes
    (outside) so it never overlaps the bars; pass where='upper right' etc. only if that corner is empty."""
    handles = [mpatches.Patch(color=c, label=l) for l, c in mapping.items()]
    return legend_outside(ax, handles, [h.get_label() for h in handles], where=where, title=title)


def diverging_heatmap(ax, matrix, row_labels, col_labels, row_notes=None, vmax=2.0, na="n/a"):
    """
    Diverging heatmap for SIGNED values centred at zero (negative=blue, positive=red) — e.g. a
    change-vs-baseline / anomaly / z-score field, or a log2 fold-change. `matrix` may contain
    np.nan, shown as `na` (default "n/a"). row_notes: optional short strings to the right of each row.
    """
    m = np.array(matrix, dtype=float)
    im = ax.imshow(m, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(col_labels))); ax.set_xticklabels(col_labels, fontsize=FONT["tick"] + 1)
    ax.set_yticks(range(len(row_labels))); ax.set_yticklabels(row_labels, fontsize=FONT["tick"] + 1)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m[i, j]
            if np.isnan(v):
                ax.text(j, i, na, ha="center", va="center", fontsize=FONT["annot"], color="#999")
            else:
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                        fontsize=FONT["annot"], fontweight="bold",
                        color="white" if abs(v) > vmax * 0.55 else "#222")
    if row_notes:
        ax.set_xlim(-0.5, len(col_labels) - 0.5 + 1.8)
        for i, note in enumerate(row_notes):
            ax.text(len(col_labels) - 0.4, i, note, va="center", fontsize=FONT["caption"], color="#444")
    return im


def ranked_barh(ax, labels, values, themes=None, theme_colors=None, annots=None, xlabel="value"):
    """Ranked horizontal bar chart, coloured by category, with per-bar annotations. Generic — use
    for scores, counts, enrichment (pass xlabel="-log10(FDR)"), or any ranked magnitude in any
    domain. The first label is drawn at the TOP (rank #1 on top)."""
    y = np.arange(len(labels))
    colors = [theme_colors.get(t, NEUTRAL) for t in themes] if (themes and theme_colors) else UP
    ax.barh(y, values, color=colors)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=FONT["tick"] + 1)
    ax.invert_yaxis()   # first label / rank #1 on top
    ax.set_xlabel(xlabel, fontsize=FONT["axis"]); ax.set_xlim(0, max(values) * 1.28)
    if annots:
        for i, (v, a) in enumerate(zip(values, annots)):
            ax.text(v + max(values) * 0.01, i, a, va="center", fontsize=FONT["caption"], color="#333")


# backwards-compatible aliases (older scripts may import the earlier, bio-flavoured names)
heatmap_logfc = diverging_heatmap
barh_enrichment = ranked_barh


def osm_basemap(ax, lons=None, lats=None, gdf=None, values=None, size=45, cmap="viridis",
                edgecolor="white", crs_in="EPSG:4326", source=None, colorbar_label=None,
                **plot_kw):
    """
    Plot geographic points/polygons on an OpenStreetMap-tiled basemap (static figure).

    Never draw bare longitude/latitude on empty axes — without a basemap there are no coastlines,
    borders or place names, so a reader can't tell where anything is. This reprojects the data to
    Web Mercator (EPSG:3857, what the OSM tiles use) and draws the OSM basemap under it.

    Pass either a GeoDataFrame (`gdf=`) or matched `lons=`/`lats=` sequences (+ optional `values=`
    to colour points). `source` defaults to contextily's OpenStreetMap.Mapnik (keep the © OSM
    attribution it adds). Needs `pip install geopandas contextily` and network access for the tiles.
    """
    try:
        import geopandas as gpd
        import contextily as cx
    except ImportError as e:  # pragma: no cover - depends on optional install
        raise ImportError("osm_basemap needs geopandas + contextily "
                          "(`pip install geopandas contextily`).") from e
    if gdf is None:
        if lons is None or lats is None:
            raise ValueError("pass either gdf= or both lons= and lats=")
        gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(list(lons), list(lats)), crs=crs_in)
    if values is not None:                       # works for BOTH the gdf= and lons/lats paths
        gdf = gdf.copy()
        gdf["__value"] = list(values)
    g = gdf.to_crs(epsg=3857)
    col = "__value" if "__value" in getattr(g, "columns", []) else None
    if col is not None:
        g.plot(ax=ax, column=col, markersize=size, cmap=cmap, edgecolor=edgecolor,
               legend=True, legend_kwds={"label": colorbar_label, "shrink": 0.6}, **plot_kw)
    else:
        g.plot(ax=ax, markersize=size, color=UP, edgecolor=edgecolor, **plot_kw)
    cx.add_basemap(ax, crs=g.crs.to_string(),
                   source=source or cx.providers.OpenStreetMap.Mapnik)
    ax.set_axis_off()
    return ax


def folium_osm_map(rows, lat_key="lat", lon_key="lon", popup_keys=None, value_key=None,
                   tooltip_key=None, tiles="OpenStreetMap", zoom_start=4, radius=6, color=UP):
    """
    Build an interactive OpenStreetMap (Leaflet) map for the HTML report and return the folium.Map.

    **Every marker is CLICKABLE**: it carries a popup listing the point's attributes, so a reader can
    click any point to see what it is. `rows` is a list of dicts with numeric `lat_key`/`lon_key`.
    - popup_keys: which fields to show in the click popup; DEFAULTS to every field except the
      coordinates (so points are informative out of the box). Pass a list to curate / order them.
    - tooltip_key: field shown on hover (defaults to the first popup field) so a point is
      identifiable without clicking.
    - value_key: optional numeric field that scales the marker radius.

    Fits the view to the data's bounding box; keeps the © OpenStreetMap attribution and a scale bar.
    Embed inline with `map.get_root().render()` (don't link a separate file). Needs `pip install folium`.
    """
    try:
        import folium
    except ImportError as e:  # pragma: no cover - depends on optional install
        raise ImportError("folium_osm_map needs folium (`pip install folium`).") from e
    pts = [(float(r[lat_key]), float(r[lon_key]), r) for r in rows
           if r.get(lat_key) is not None and r.get(lon_key) is not None]
    if not pts:
        raise ValueError("no rows had usable coordinates")
    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    center = (sum(lats) / len(lats), sum(lons) / len(lons))
    m = folium.Map(location=center, tiles=tiles, zoom_start=zoom_start, control_scale=True)
    for lat, lon, r in pts:
        keys = popup_keys or [k for k in r if k not in (lat_key, lon_key)]   # default: all attributes
        popup_html = "<br>".join(f"<b>{html.escape(str(k))}</b>: {html.escape(str(r.get(k)))}"
                                 for k in keys if r.get(k) not in (None, ""))
        tip = r.get(tooltip_key) if tooltip_key else (r.get(keys[0]) if keys else None)
        val = r.get(value_key) if value_key else None
        rscale = 0 if val is None else min(max(float(val), 0.0) ** 0.5, 12)   # non-negative radius
        folium.CircleMarker(
            [lat, lon], radius=radius + rscale,
            color=color, fill=True, fill_color=color, fill_opacity=0.75, weight=1,
            popup=folium.Popup(popup_html, max_width=280) if popup_html else None,
            tooltip=(html.escape(str(tip)) if tip is not None else None),
        ).add_to(m)
    if len(pts) > 1:
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    return m


def save_map_html(m, path):
    """Save a folium map to a standalone HTML file (for embedding, use m.get_root().render())."""
    m.save(path)
    print(f"[okn_figstyle] saved interactive OSM map: {path}")
    return path


def finalize(fig, number, path, tight=True):
    """Save a figure at 150 dpi with tight margins. `number` is for the log/print only — the visible
    "Figure N." belongs in the caption BELOW the image (with the interpretive legend), NOT inside the
    PNG (see references/figure-checklist.md). Keep the PNG to panels, axis labels, and a compact key."""
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[okn_figstyle] saved Figure {number}: {path}")


def _demo():
    apply_style()
    fig = plt.figure(figsize=(13.5, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 0.82, 1.4], wspace=0.42)
    # A: enrichment bars with legend placed in the empty top-right (tall left bar)
    axa = fig.add_subplot(gs[0, 0])
    x = np.arange(2)
    axa.bar(x - 0.19, [490, 21], 0.36, color="#bdc3c7", label="expected")
    axa.bar(x + 0.19, [492, 31], 0.36, color=UP, label="observed")
    axa.set_xticks(x); axa.set_xticklabels(["broad set", "curated set"], fontsize=FONT["tick"])
    legend_outside(axa, where="upper right")
    panel_title(axa, "A", "Over-representation")
    # B: donut with legend BELOW, donut shrunk+raised so nothing overlaps
    axb = fig.add_subplot(gs[0, 1])
    axb.pie([210, 41, 5], colors=[NEUTRAL, "#e67e22", UP], startangle=90, radius=0.86,
            center=(0, 0.1), wedgeprops=dict(width=0.4, edgecolor="w"),
            autopct=lambda p: f"{int(round(p*256/100))}", pctdistance=0.8,
            textprops={"fontsize": FONT["annot"], "color": "white", "fontweight": "bold"})
    axb.set_ylim(-1.15, 1.15)
    legend_outside(axb, [mpatches.Patch(color=NEUTRAL), mpatches.Patch(color="#e67e22"), mpatches.Patch(color=UP)],
                   ["systemic", "intermediate", "selective"], where="below")
    panel_title(axb, "B", "Specificity")
    # C: diverging heatmap of signed values (domain-neutral demo)
    axc = fig.add_subplot(gs[0, 2])
    diverging_heatmap(axc, [[-1.09, -1.14], [-0.81, np.nan], [1.90, 1.99]],
                      ["Indicator 1", "Indicator 2", "Indicator 3"], ["Group A", "Group B"],
                      row_notes=["decrease", "n/a", "increase"])
    panel_title(axc, "C", "Signed change (log2)")
    finalize(fig, 3, "okn_figstyle_demo.png")


def _demo_map():
    """Interactive folium map always renders offline; the static contextily PNG needs tiles."""
    rows = [
        {"site": "Ames Research Center", "lat": 37.41, "lon": -122.06, "n": 9},
        {"site": "JSC Houston", "lat": 29.56, "lon": -95.09, "n": 8},
        {"site": "Kennedy Space Center", "lat": 28.57, "lon": -80.65, "n": 5},
        {"site": "UC San Diego", "lat": 32.88, "lon": -117.23, "n": 12},
    ]
    m = folium_osm_map(rows, popup_keys=["site", "n"], value_key="n", radius=6)
    save_map_html(m, "okn_figstyle_demo_map.html")
    try:
        apply_style()
        fig, ax = plt.subplots(figsize=(6.2, 6.2))
        osm_basemap(ax, lons=[r["lon"] for r in rows], lats=[r["lat"] for r in rows],
                    values=[r["n"] for r in rows], size=110, colorbar_label="samples (n)")
        panel_title(ax, "A", "Sampling sites (OSM basemap)")
        finalize(fig, 1, "okn_figstyle_demo_map.png")
    except Exception as e:
        print(f"[okn_figstyle] static OSM basemap skipped ({type(e).__name__}: {e}). "
              f"The interactive folium map was written; for the static PNG install "
              f"geopandas+contextily and ensure network access to the OSM tile server.")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        _demo()
    elif "--demo-map" in sys.argv:
        _demo_map()
    else:
        print(__doc__)

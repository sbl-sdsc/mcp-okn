# Figure checklist

Run through this for **every** figure before embedding it. Most items are enforced by
`scripts/okn_figstyle.py`; the last item (read the rendered PNG) is the backstop that catches what
code can't predict.

## Layout & legends
- [ ] **Interpretive legend goes BELOW the figure in the report text**, not inside the PNG. The PNG
      holds only: panel titles, axis labels, and a compact color/marker key.
- [ ] **Panels are labelled (A), (B), (C)…** with `panel_title(ax, "A", "…")`, and the legend text
      references those letters.
- [ ] **No in-plot legend/key overlaps the plotted data.** Use `legend_outside(ax, where="below"|
      "right")`. Only use an inside corner ("upper right") when that corner is provably empty.
- [ ] **Pies / donuts:** shrink (`radius≈0.85`) and/or raise (`center=(0,0.1)`), widen the y-limits,
      and put the legend below — donuts are the most common overlap offender.
- [ ] **Multi-panel:** give panels room with `width_ratios` and `wspace≈0.4`; don't let a colorbar or
      right-hand annotations collide with the next panel (`set_xlim` with headroom).

## Fonts (floors — small multiples shrink text fast)
- [ ] ticks / annotations ≥ 8 pt · axis labels ≥ 9 pt · titles ≥ 11 pt.
- [ ] Long category labels: wrap or shorten; don't let them get tiny to fit.

## Numbering & files
- [ ] Figures numbered in the order they appear in the document (1, 2, 3 … top to bottom).
- [ ] **Filename matches the number** (`fig1_overview.png`, `fig2_map.png` …).
- [ ] If you insert or reorder a figure, **renumber captions AND rename files** (and delete the old
      ones — you may need the file-delete permission tool if a delete is refused).

## Conventions
- [ ] **Signed values** (log2 fold-change, change-vs-baseline, anomaly, z-score) → diverging map
      centred at zero, **negative = blue, positive = red**; colorbar labelled with units.
      Sequential magnitudes → a single-hue ramp.
- [ ] Grouped / ranked bars coloured by category with a legend; annotate each bar with its value +
      counts (e.g. `4.3× (64 / 76)`).
- [ ] Define every acronym in the figure (in the legend) the first time it appears.

## Uncertainty & accessibility
- [ ] **Show uncertainty** where the plot implies it: error bars / confidence intervals on estimates
      and means, and the sample size **n** (in the bar, axis, or legend). A bare point estimate with
      no spread overstates precision.
- [ ] **Colourblind-safe palette.** Use the module's Okabe–Ito `THEME` for categories (the old
      red+green pairing is CVD-unsafe); the red/blue diverging map for signed values is fine.
- [ ] **Never encode a category by colour alone** — pair colour with a label, marker, hatch, or
      order, so the figure survives greyscale printing and colour-vision deficiency.

## Maps & geographic data (never a bare lat/long scatter)
- [ ] Anything with coordinates — sampling sites, regions, county/ZIP data, or lat/long / S2 cells
      from the spatial tools (`point_to_s2`, `spatial_bridge`) — goes on an **OpenStreetMap-tiled
      basemap**, not plotted onto empty axes. Points on blank axes carry no coastlines, borders, or
      place names, so the reader cannot tell where anything is.
- [ ] **Static PNG:** reproject the data to **Web Mercator (EPSG:3857)** to match the tiles, plot the
      points/choropleth, then add the basemap (`geopandas` + `contextily`;
      `osm_basemap(ax, ...)` does this). Do not draw lon/lat degrees straight onto a Mercator basemap.
- [ ] **Interactive (HTML report):** use `folium` (Leaflet + OSM tiles); `folium_osm_map(rows, ...)`
      returns the map. Embed it inline in the HTML (`m.get_root().render()`), don't link a file.
- [ ] **Every mapped point is clickable.** Each marker carries a popup showing the point's id / name
      and key attributes (+ source), plus a hover tooltip — so a reader can click any point to see
      what it is. `folium_osm_map` adds a popup built from all fields by default.
- [ ] **Extent/zoom** fit the data's bounding box with a small margin — not the whole world, not so
      tight that markers touch the edge. Cluster or size markers by value if points overlap.
- [ ] **Keep the OpenStreetMap attribution** (tiles are © OpenStreetMap contributors); contextily and
      folium add it by default — don't strip it.
- [ ] Legend below states the **coordinate source** (which KG/predicate supplied lat/long or the S2
      cell) and what each marker/colour encodes, same as any other figure.

## Verify (do not skip)
- [ ] `Read` the rendered PNG back and look at it. Confirm: no overlaps, legible fonts, correct
      panel letters, sequential numbering, and that any letters/symbols in the plot are defined in
      the legend. Fix and re-render if not — the first matplotlib layout is often wrong.

## Provenance
- [ ] The legend states where the data came from: the KG(s), the predicate path, the statistical
      test, and the foreground/background for any enrichment. A figure a reader can't trace is a
      figure they can't trust.

## Interpretation (say what it means)
- [ ] After the legend, add a **1–3 sentence interpretation** of the result — the takeaway, the
      pattern to notice, any caveat — in the body text below the figure. Do the same after **every
      table**. The legend says *what is shown and where it came from*; the interpretation says *what
      to conclude*. Keep interpretation out of the legend and out of the PNG.

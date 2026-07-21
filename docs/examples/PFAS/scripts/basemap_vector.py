"""
basemap_vector.py -- offline vector basemap (coastlines, country and US state
boundaries) read directly from the `basemap-data` package's GSHHS/WDBII assets.

The sandbox has no egress to any raster-tile host, so `contextily`/OSM tiles cannot
be fetched for the STATIC figures. The interactive map in the HTML report uses real
OpenStreetMap tiles via folium (they load in the reader's browser). For the static
PNGs this module supplies genuine geographic context -- coastlines, national and
US state borders -- so points are locatable, rather than a bare lon/lat scatter.

Data: GSHHS coastlines and WDBII political boundaries, redistributed in
`basemap-data` (LGPL-3.0), (c) matplotlib/basemap.
"""
import os
import struct

import numpy as np

def _find_data():
    import glob
    import site
    roots = list(site.getsitepackages()) + [site.getusersitepackages()]
    roots.append(os.path.abspath(os.path.join(os.path.dirname(np.__file__), "..")))
    for r in roots:
        cand = os.path.join(r, "mpl_toolkits", "basemap_data")
        if os.path.isdir(cand):
            return cand
    hits = glob.glob(os.path.expanduser("~/.local/lib/python*/site-packages/mpl_toolkits/basemap_data"))
    if hits:
        return hits[0]
    raise RuntimeError("basemap_data not found -- pip install basemap-data")


DATA = _find_data()

ATTRIBUTION = "Coastlines & boundaries: GSHHS / WDBII via basemap-data (LGPL-3.0)"


def _segments(name, res="i", bbox=None):
    """Yield (lon, lat) arrays for each boundary segment of `name` at resolution `res`."""
    meta = os.path.join(DATA, f"{name}meta_{res}.dat")
    binf = os.path.join(DATA, f"{name}_{res}.dat")
    if not (os.path.exists(meta) and os.path.exists(binf)):
        return
    with open(meta) as fh, open(binf, "rb") as bf:
        for line in fh:
            p = line.split()
            if len(p) < 7:
                continue
            npts, south, north, offset, nbytes = (int(p[2]), float(p[3]), float(p[4]),
                                                  int(p[5]), int(p[6]))
            if bbox and (north < bbox[1] or south > bbox[3]):
                continue
            bf.seek(offset)
            raw = bf.read(nbytes)
            if len(raw) < npts * 8:
                continue
            arr = np.array(struct.unpack(f"<{npts * 2}f", raw[: npts * 8])).reshape(-1, 2)
            lon, lat = arr[:, 0], arr[:, 1]
            if bbox:
                if lon.max() < bbox[0] or lon.min() > bbox[2]:
                    continue
            yield lon, lat


def draw_basemap(ax, bbox, coast_kw=None, border_kw=None, state_kw=None, res="i"):
    """Draw coastlines + country + US state boundaries clipped to bbox=(W,S,E,N)."""
    coast_kw = dict(color="#8a9099", lw=0.55, zorder=1) | (coast_kw or {})
    border_kw = dict(color="#6d747d", lw=0.7, zorder=1) | (border_kw or {})
    state_kw = dict(color="#b9bfc7", lw=0.45, zorder=1) | (state_kw or {})
    for lon, lat in _segments("gshhs", res, bbox):
        ax.plot(lon, lat, **coast_kw)
    for lon, lat in _segments("countries", res, bbox):
        ax.plot(lon, lat, **border_kw)
    for lon, lat in _segments("states", res, bbox):
        ax.plot(lon, lat, **state_kw)
    ax.set_xlim(bbox[0], bbox[2])
    ax.set_ylim(bbox[1], bbox[3])
    # equal-area-ish aspect for mid-latitudes
    ax.set_aspect(1.0 / np.cos(np.radians((bbox[1] + bbox[3]) / 2)))
    ax.set_facecolor("#f7f9fb")
    return ax

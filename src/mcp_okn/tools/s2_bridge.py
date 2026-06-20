"""On-the-fly lat/long -> S2 cell bridging: point_to_s2 + spatial_bridge tools.

Some KGs carry POINT coordinates (lat/long literals) but no S2 cell key, so they
cannot be joined live to spatialkg's S2 grid (FRINK/QLever has no point-in-polygon).
SUDOKN is the first such graph. Rather than materialize a new named graph, this
module supplies the missing join key AT QUERY TIME:

1. fetch the (scoped) set of point-bearing entities  -> [(site, lat, lng), ...]
2. compute each point's S2 Level-13 cell IRI in Python (deterministic, cheap)
3. inject the (site, cell) pairs as a VALUES block into a second federated query
   that joins ?cell to spatialkg (county/state) and onward to fiokg/sawgraph/...

Nothing is persisted; the computed key lives only inside the request.

Verified: point (35.7956, -78.7941) -> s2.level13.9920570487421796352, which exists
in spatialkg and sfWithin Wake County, NC (FIPS 37183).

Requires the ``s2sphere`` package.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import s2sphere

from ..app import mcp
from ..sparql import SparqlError, run_sparql

#: spatialkg/KWG S2 Level-13 cell IRI prefix.
KWG_S2_PREFIX = "http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13."
SPATIALKG_GRAPH = "https://purl.org/okn/frink/kg/spatialkg"
SUDOKN_GRAPH = "https://purl.org/okn/frink/kg/sudokn"
DEFAULT_LEVEL = 13
#: Hard cap on how many points get injected into one VALUES block. Keep queries
#: from blowing up; callers should scope (NAICS/state/bbox) before bridging.
MAX_POINTS = 5000


# --------------------------------------------------------------------------- #
# Pure primitives (no network)
# --------------------------------------------------------------------------- #
def point_to_s2_iri(lat: float, lng: float, level: int = DEFAULT_LEVEL) -> str:
    """Return the spatialkg cell IRI for a point, via the standard S2 scheme.

    Computes the Google S2 ``CellId`` from ``(lat, lng)``, truncates it to
    ``level``, and formats it as the spatialkg/KWG cell IRI — the exact scheme
    spatialkg stores.
    """
    ll = s2sphere.LatLng.from_degrees(float(lat), float(lng))
    cid = s2sphere.CellId.from_lat_lng(ll).parent(int(level))
    return f"{KWG_S2_PREFIX}{cid.id()}"


def sudokn_point_query(
    naics: str | None = None,
    state: str | None = None,
    limit: int = MAX_POINTS,
) -> str:
    """Build the SUDOKN point-fetch query: ``SELECT ?site ?lat ?lng``.

    Optionally scoped by a primary-NAICS code and/or a state name; scoping
    narrows the VALUES block that gets injected downstream.
    """
    filters = ""
    if naics:
        # company carries NAICS; site shares the company's web-domain prefix
        filters += (
            f"    ?company s:hasPrimaryNAICSClassifier "
            f"<http://asu.edu/semantics/SUDOKN/NAICS%20{naics}-individual> .\n"
            f'    BIND(IRI(CONCAT(REPLACE(STR(?company),"-company-instance$",""),'
            f'"-geosite-1-instance")) AS ?site)\n'
        )
    if state:
        filters += f'    ?site s:locatedInState/rdfs:label "{state}" .\n'
    site_decl = "" if naics else "    ?site a s:GeospatialSite .\n"
    return f"""PREFIX s: <http://asu.edu/semantics/SUDOKN/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?site ?lat ?lng WHERE {{
  GRAPH <{SUDOKN_GRAPH}> {{
{site_decl}{filters}    ?site s:hasGeospatialLocation ?loc .
    ?loc s:hasLatitudeValue ?lat ; s:hasLongitudeValue ?lng .
  }}
}} LIMIT {int(limit)}"""


def _values_block(pairs: Sequence[tuple[str, str]]) -> str:
    """Build a ``VALUES (?site ?cell) { (<s> <c>) ... }`` block with IRI escaping."""

    def iri(u: str) -> str:
        return "<" + u.replace(">", "%3E") + ">"

    rows = " ".join(f"({iri(s)} {iri(c)})" for s, c in pairs)
    return f"VALUES (?site ?cell) {{ {rows} }}"


# --------------------------------------------------------------------------- #
# The bridge: fetch -> compute -> inject -> run
# --------------------------------------------------------------------------- #
async def _rows(query: str) -> list[dict[str, Any]]:
    """Run a SPARQL query via the shared async executor and return flat rows.

    Adapts this server's ``run_sparql`` (async, returning
    ``{"vars", "rows", "row_count"}``) to the ``list[dict]`` shape this module
    works in.
    """
    rows: list[dict[str, Any]] = (await run_sparql(query))["rows"]
    return rows


async def join_via_s2(
    point_query: str,
    target_pattern: str,
    select_vars: str = "*",
    level: int = DEFAULT_LEVEL,
    extra_prefixes: str = "",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Generic point->S2 join.

    Args:
        point_query: SPARQL SELECT returning ``?site ?lat ?lng`` (the scoped points).
        target_pattern: A graph pattern that uses ``?site`` and/or ``?cell`` to
            join the S2 cell to spatialkg / fiokg / sawgraph and select payload
            vars. It is dropped in AFTER the injected VALUES block.
        select_vars: Projection for the final query (e.g. ``"?site ?county ?fips"``).
        level: S2 level for the computed cell IRIs (default 13, spatialkg's grid).
        extra_prefixes: PREFIX declarations the target pattern needs.
        limit: Optional LIMIT on the final query.

    Returns:
        The final query's rows. Empty if no points (or none with coordinates) match.

    Raises:
        ValueError: If more than ``MAX_POINTS`` points match — scope the
            point_query (NAICS/state/bbox) before bridging.
    """
    points = await _rows(point_query)
    pairs: list[tuple[str, str]] = []
    for r in points:
        lat, lng = r.get("lat"), r.get("lng")
        if lat is None or lng is None or lat == "" or lng == "":
            continue
        pairs.append((r["site"], point_to_s2_iri(lat, lng, level)))
    if not pairs:
        return []
    if len(pairs) > MAX_POINTS:
        raise ValueError(
            f"{len(pairs)} points exceed MAX_POINTS={MAX_POINTS}; "
            f"scope the point_query (NAICS/state/bbox) before bridging."
        )

    final = f"""{extra_prefixes}
SELECT {select_vars} WHERE {{
  {_values_block(pairs)}
  {target_pattern}
}}{f" LIMIT {int(limit)}" if limit else ""}"""
    return await _rows(final)


async def sudokn_to_county(
    naics: str | None = None,
    state: str | None = None,
    limit: int | None = 1000,
) -> list[dict[str, Any]]:
    """Return each (scoped) SUDOKN site's S2 cell and spatialkg county + FIPS.

    For (optionally NAICS/state-scoped) SUDOKN sites, computes the S2 cell from
    the site's lat/long and joins it to the spatialkg county
    (``AdministrativeRegion_2``) it sits in.
    """
    # spatialkg carries TWO region nodes per county — the KWG
    # `.../resource/administrativeRegion.USA.*` node and a mirrored
    # `datacommons.org/.../geoId/*` node — both typed AdministrativeRegion_2 with
    # the same label/FIPS. Without the namespace FILTER (and SELECT DISTINCT) every
    # row comes back duplicated. Restrict to the KWG resource namespace.
    target = f"""GRAPH <{SPATIALKG_GRAPH}> {{
    ?cell a kwgo:S2Cell_Level13 ; kwgo:sfWithin ?county .
    ?county a kwgo:AdministrativeRegion_2 ; rdfs:label ?countyName ; kwgo:hasFIPS ?fips .
    FILTER(STRSTARTS(STR(?county), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
  }}"""
    return await join_via_s2(
        point_query=sudokn_point_query(naics=naics, state=state),
        target_pattern=target,
        select_vars="DISTINCT ?site ?cell ?countyName ?fips",
        extra_prefixes=(
            "PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>\n"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
        ),
        limit=limit,
    )


# --------------------------------------------------------------------------- #
# MCP tools
# --------------------------------------------------------------------------- #
@mcp.tool()
async def point_to_s2(lat: float, lng: float, level: int = DEFAULT_LEVEL) -> str:
    """Convert a lat/long point to its spatialkg S2 cell IRI (level 13 default)."""
    return point_to_s2_iri(lat, lng, level)


async def sudokn_spatial_join(
    naics: str | None = None,
    state: str | None = None,
    limit: int = 1000,
) -> Any:
    """Place SUDOKN manufacturers on the spatial hub via on-the-fly S2 cells.

    Internal convenience helper — **not** exposed as an MCP tool, to keep the tool
    surface free of KG-specific entries. SUDOKN's join runs through the generic
    ``spatial_bridge`` tool (supply ``sudokn_point_query()`` as its ``point_query``);
    this wrapper just hard-codes that point query and the spatialkg county target.

    Computes each site's S2 cell from its lat/long and joins to spatialkg
    county/FIPS — SUDOKN has no S2 key, so this is the only live join path. Scope
    with a NAICS code (e.g. ``'332813'``) and/or a state name to keep the set
    small (the bridge caps at MAX_POINTS).
    """
    try:
        return await sudokn_to_county(naics=naics, state=state, limit=limit)
    except SparqlError as exc:
        return {"error": str(exc)}


@mcp.tool()
async def spatial_bridge(
    point_query: str,
    target_pattern: str,
    select_vars: str = "*",
    extra_prefixes: str = "",
    limit: int | None = 500,
) -> Any:
    """Generic point->S2 bridge for ANY point-bearing graph.

    ``point_query`` must SELECT ``?site ?lat ?lng``; ``target_pattern`` uses
    ``?site``/``?cell`` to join the computed S2 cell to spatialkg/fiokg/sawgraph
    and select payload.
    """
    try:
        return await join_via_s2(
            point_query,
            target_pattern,
            select_vars=select_vars,
            extra_prefixes=extra_prefixes,
            limit=limit,
        )
    except SparqlError as exc:
        return {"error": str(exc)}

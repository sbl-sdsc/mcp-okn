"""KG discovery tools: list_kgs, describe_kg, get_server_info."""

from __future__ import annotations

from typing import Any

from .. import __version__, payloads, registry, schema, void
from ..app import mcp
from ..build_info import build_id
from ..sparql import FEDERATION_ENDPOINT


@mcp.tool()
async def get_server_info() -> dict[str, Any]:
    """Identify THIS server: `{service, version, build, sparql_endpoint, schema_files}`.

    `build` is the deployed commit (`unknown` if unidentifiable). `schema_files` is
    how many per-KG schema files `get_schema` can read (0 means every schema is
    probed live, so the deployment is missing them). The version alone
    can't tell two deployments apart, so call this when a tool or argument seems to
    be missing — a hosted server can lag the repo — or to record exactly which build
    produced a result.
    """
    return {
        "service": mcp.name,
        "version": __version__,
        "build": build_id(),
        "sparql_endpoint": FEDERATION_ENDPOINT,
        "schema_files": schema.schema_file_count(),
    }


@mcp.tool()
async def list_kgs() -> dict[str, Any]:
    """List all Proto-OKN knowledge graphs available on the OKN federation.

    Returns a table, one row per KG: `shortname`, `title`, a one-line
    `description`, and a `payload` list, the curated context types that KG
    SUPPLIES (e.g. `digcfdekg` → `["gene", "gene_set", "trait", "disease"]`,
    `prokn` → `["protein", "gene", "GO", "Reactome", "pathway", ...]`). Judge a
    graph by its `payload` tags, NOT by its name: a graph named for one thing
    often carries much more. To go the other way ("which KGs SUPPLY pathway/GO/
    trait for a gene I can join on Entrez?"), call
    `find_context_sources(want=[...], join_key=...)`. Every KG's named graph is
    `https://purl.org/okn/frink/kg/{shortname}` (given once as `named_graph`).

    Use the descriptions to decide which graph(s) to query. If these one-line
    descriptions are too terse to tell which KG a question targets, call
    `describe_kg(shortname, long_description=True)` on the candidates for the
    registry's ~150-word prose description (and its homepage) before choosing.

    Returns `{"named_graph", "columns": ["shortname", "title", "description",
    "payload"], "data": [[...], ...], "count"}`.
    """
    kgs = await registry.list_kgs()
    # Enrich at serve time rather than baking into the snapshot: kgs.json is
    # regenerated from the live registry, which would wipe a hand-curated field.
    # Columnar, without the per-row homepage (in describe_kg) and named_graph
    # (derivable from the shortname): about a third shorter than dict rows.
    cols = ["shortname", "title", "description", "payload"]
    rows = [
        [
            kg.get("shortname"),
            kg.get("title"),
            kg.get("description"),
            payloads.payloads_for(kg["shortname"]),
        ]
        for kg in kgs
    ]
    return {
        "named_graph": "https://purl.org/okn/frink/kg/{shortname}",
        "columns": cols,
        "data": rows,
        "count": len(rows),
    }


@mcp.tool()
async def describe_kg(shortname: str, long_description: bool = False) -> str:
    """Return registry documentation for one KG.

    Args:
        shortname: The KG shortname (e.g. `prokn`, `sawgraph`, `ubergraph`),
            as returned by `list_kgs`.
        long_description: If True, return the registry's free-text description
            — the ~150-word prose below the YAML frontmatter — instead of the full
            markdown. Reach for this when the one-line `list_kgs`
            descriptions are too terse to tell which KG a question belongs to:
            the longer prose usually names the entities, sources, and scope that
            disambiguate near-overlapping graphs.

    Returns the registry markdown (title, description, and prose) for deeper
    context before writing a query — or just the long description when
    `long_description` is set. Either way, a `Summary` section follows when this
    server has its own description of the KG. For KGs with query-time domain rules
    the registry prose does not cover (e.g. `spoke-genelab`'s spaceflight
    assay-comparison rules), the relevant guidance is appended to the returned text.
    """
    if long_description:
        doc = await registry.fetch_kg_long_description(shortname)
    else:
        doc = await registry.fetch_kg_doc(shortname)

    summary = registry.kg_summary(shortname)
    if summary:
        doc = f"{doc.rstrip()}\n\n## Summary\n\n{summary}"

    notes = schema.usage_notes(shortname)
    if notes is not None:
        doc = (
            f"{doc}\n\n## {notes.get('title', 'Assay-comparison rules')} "
            f"({shortname})\n\n"
            f"{notes['guidance']}\n\n"
            f"(A reusable SPARQL query is returned as "
            f'`usage_notes.query_snippet` by `get_schema("{shortname}")`.)'
        )
    return doc


@mcp.tool()
async def get_kg_version(shortname: str | None = None) -> dict[str, Any]:
    """Return a KG's release version and last-updated date (from the VoID metadata).

    The `okn-void` meta-graph records provenance for each loaded KG. This tool
    reads it live and returns, per KG:
      * `version` — the release string, e.g. `"v0.0.5"` (`pav:version`);
      * `last_updated` — an ISO-8601 timestamp of the last load
        (`pav:lastUpdatedOn`), e.g. `"2026-06-23T14:26:02.126+00:00"`;
      * `named_graph` — the KG's federation named-graph URI.

    Use it to check how current a graph is, cite the exact version behind an
    analysis, or compare release freshness across graphs.

    Args:
        shortname: a KG shortname (as from `list_kgs`). Omit to return the
            provenance for EVERY KG that records it, sorted by shortname.

    Returns (shortname given) a single record dict, or `{"shortname", "version":
    None, "note": ...}` when that KG records no VoID provenance (a few, e.g.
    `okn-void` and `wikidata`, do not). Returns (shortname omitted) `{"count",
    "versions": [record, ...]}`.

    Only KGs in the registry (those `list_kgs` returns) count as versions. A VoID
    record whose shortname is NOT in the registry is a stale entry, not another KG:
    it is left out of `versions` / `count` and listed under `unregistered` instead
    (the key is present only when there is one), and a single-KG lookup of such a
    name returns its record with `"registered": False` and a `note`.
    """
    records = await void.fetch_versions(shortname)
    # Fail open: with no registry listing to check against, flag nothing.
    known = {kg["shortname"] for kg in await registry.list_kgs()}
    stale = [r for r in records if known and r["shortname"] not in known]
    if shortname is not None:
        if stale:
            return {
                **stale[0],
                "registered": False,
                "note": (
                    f"'{shortname}' has VoID provenance in the okn-void graph but "
                    "is not in the KG registry — a stale entry, not a KG this "
                    "server serves. See `list_kgs` for the available graphs."
                ),
            }
        if records:
            return records[0]
        return {
            "shortname": shortname,
            "version": None,
            "note": (
                f"No VoID provenance recorded for '{shortname}' in the okn-void "
                "graph (some KGs, e.g. okn-void and wikidata, do not publish version "
                "metadata). Check the shortname with `list_kgs` if unexpected."
            ),
        }
    versions = [r for r in records if r not in stale]
    out: dict[str, Any] = {"count": len(versions), "versions": versions}
    if stale:
        out["unregistered"] = stale
    return out

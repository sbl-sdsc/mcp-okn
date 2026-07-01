"""KG discovery tools: list_kgs, describe_kg."""

from __future__ import annotations

from typing import Any

from .. import payloads, registry, schema, void
from ..app import mcp


@mcp.tool()
async def list_kgs() -> list[dict[str, Any]]:
    """List all Proto-OKN knowledge graphs available on the FRINK federation.

    Returns one entry per KG with its `shortname`, `title`, `description`,
    `homepage`, the `named_graph` URI to use inside `GRAPH <...> { ... }` blocks,
    and a `payload` list — the curated context types that KG SUPPLIES (e.g.
    `digcfdekg` → `["gene", "gene_set", "trait", "disease"]`, `prokn` → `["protein",
    "gene", "GO", "Reactome", "pathway", ...]`). The `payload` tags say what a graph
    adds, not just how it joins — judge a graph by them, NOT by its name (a graph
    named for one thing often carries much more). To go the other way — "which KGs
    SUPPLY pathway/GO/trait for a gene I can join on Entrez?" — call
    `find_context_sources(want=[...], join_key=...)`.

    Use the descriptions to decide which graph(s) to query. If these one-line
    descriptions are too terse to tell which KG a question targets, call
    `describe_kg(shortname, long_description=True)` on the candidates for the
    registry's ~150-word prose description before choosing.
    """
    kgs = await registry.list_kgs()
    # Enrich at serve time rather than baking into the snapshot: kgs.json is
    # regenerated from the live registry, which would wipe a hand-curated field.
    return [{**kg, "payload": payloads.payloads_for(kg["shortname"])} for kg in kgs]


@mcp.tool()
async def describe_kg(shortname: str, long_description: bool = False) -> str:
    """Return registry documentation for one KG.

    Args:
        shortname: The KG shortname (e.g. `prokn`, `sawgraph`, `ubergraph`),
            as returned by `list_kgs`.
        long_description: If True, return ONLY the registry's free-text
            description — the ~150-word prose below the YAML frontmatter — instead
            of the full markdown. Reach for this when the one-line `list_kgs`
            descriptions are too terse to tell which KG a question belongs to:
            the longer prose usually names the entities, sources, and scope that
            disambiguate near-overlapping graphs.

    Returns the registry markdown (title, description, and prose) for deeper
    context before writing a query — or just the long description when
    `long_description` is set. For KGs with query-time domain rules the registry
    prose does not cover (e.g. `spoke-genelab`'s spaceflight assay-comparison
    rules), the relevant guidance is appended to the returned text.
    """
    if long_description:
        doc = await registry.fetch_kg_long_description(shortname)
    else:
        doc = await registry.fetch_kg_doc(shortname)

    notes = schema.usage_notes(shortname)
    if notes is not None:
        doc = (
            f"{doc}\n\n## Assay-comparison rules ({shortname})\n\n"
            f"{notes['guidance']}\n\n"
            f'(A reusable comparability-signature SPARQL query is returned as '
            f'`usage_notes.query_snippet` by `get_schema(\"{shortname}\")`.)'
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
      * `modified` — a coarse `"Mon YYYY"` month stamp (`dcterms:modified`);
      * `named_graph` — the KG's federation named-graph URI.

    Use it to check how current a graph is, cite the exact version behind an
    analysis, or compare release freshness across graphs.

    Args:
        shortname: a KG shortname (as from `list_kgs`). Omit to return the
            provenance for EVERY KG that records it, sorted by shortname.

    Returns (shortname given) a single record dict, or `{"shortname", "version":
    None, "note": ...}` when that KG records no VoID provenance (a few, e.g.
    `bio101` and `wikidata`, do not). Returns (shortname omitted) `{"count",
    "versions": [record, ...]}`.
    """
    records = await void.fetch_versions(shortname)
    if shortname is not None:
        if records:
            return records[0]
        return {
            "shortname": shortname,
            "version": None,
            "note": (
                f"No VoID provenance recorded for '{shortname}' in the okn-void "
                "graph (some KGs, e.g. bio101 and wikidata, do not publish version "
                "metadata). Check the shortname with `list_kgs` if unexpected."
            ),
        }
    return {"count": len(records), "versions": records}

"""KG discovery tools: list_kgs, describe_kg."""

from __future__ import annotations

from typing import Any

from .. import registry, schema
from ..app import mcp


@mcp.tool()
async def list_kgs() -> list[dict[str, Any]]:
    """List all Proto-OKN knowledge graphs available on the FRINK federation.

    Returns one entry per KG with its `shortname`, `title`, `description`,
    `homepage`, and the `named_graph` URI to use inside
    `GRAPH <...> { ... }` blocks. Use the descriptions to decide which graph(s)
    to query. If these one-line descriptions are too terse to tell which KG a
    question targets, call `describe_kg(shortname, long_description=True)` on the
    candidates for the registry's ~150-word prose description before choosing.
    """
    return await registry.list_kgs()


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

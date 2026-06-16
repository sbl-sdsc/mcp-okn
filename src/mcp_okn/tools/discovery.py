"""KG discovery tools: list_kgs, describe_kg."""

from __future__ import annotations

from typing import Any

from .. import registry
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
    `long_description` is set.
    """
    if long_description:
        return await registry.fetch_kg_long_description(shortname)
    return await registry.fetch_kg_doc(shortname)

"""Query visualization: sparql_to_mermaid."""

from __future__ import annotations

from typing import Any

from sparql_to_mermaid import SparqlToMermaidError, to_mermaid

from ..app import mcp


@mcp.tool()
async def sparql_to_mermaid(
    query: str, well_known: bool = True, portable: bool = False
) -> dict[str, Any]:
    """Render a SPARQL query as a Mermaid flowchart diagram of its graph pattern.

    Turns the query's WHERE clause into a `graph TD` diagram: variables and
    constants become nodes, triple patterns become labeled edges, and
    OPTIONAL / UNION / FILTER / BIND / VALUES / SERVICE / MINUS / EXISTS blocks
    and property paths are drawn as their own shapes/subgraphs. Projected
    variables are highlighted. Use this to help a reader understand the shape of
    a query you wrote or are about to run with `sparql_query` — it complements
    `visualize_schema` (which diagrams a KG's schema, not a specific query).

    IRIs are shortened using the query's own `PREFIX` declarations; by default a
    curated set of well-known life-science / semantic-web prefixes (MONDO, CHEBI,
    GO, HP, NCIT, biolink, up, efo, …) also shortens common IRIs the query did
    not declare.

    Args:
        query: The SPARQL query text (SELECT/ASK/CONSTRUCT/DESCRIBE). May include
            federation `GRAPH <...> { ... }` blocks and its own `PREFIX` lines.
        well_known: If True (default), also shorten common bio/semantic-web IRIs
            the query did not declare a prefix for. Set False to shorten only
            against the query's own `PREFIX` declarations.
        portable: If True, emit a stricter-renderer-compatible diagram — any IRI
            with no known prefix is compacted to a synthetic `segment:local` CURIE
            (e.g. `kg:spoke-genelab`, `reactome:R-HSA-163210`) instead of a raw
            `https://…` in a node or `GRAPH` title, and the aggregate edge uses the
            conventional pipe-label form. Default False; the default output already
            renders in Claude's Artifact renderer and current Mermaid, so only set
            this if a specific viewer rejects a diagram.

    Returns:
        `{"mermaid": ..., "mermaid_block": ...}`, where `mermaid_block` is the
        diagram ALREADY wrapped in a ```mermaid fenced code block and `mermaid`
        is the same diagram fence-free (for saving as a `.mermaid` file). On a
        query that cannot be parsed, returns `{"error": ...}` instead.

    PRESENTATION (required): output `mermaid_block` VERBATIM, and nothing else.
    Do NOT redraw, re-render, or convert it — no SVG, PNG, HTML, image, artifact,
    or hand-built diagram. Mermaid clients render the fenced block natively;
    producing your own graphic yields a messy, incorrect picture.
    """
    try:
        diagram = to_mermaid(query, well_known=well_known, portable=portable)
    except SparqlToMermaidError as exc:
        return {"error": f"Could not render query as a Mermaid diagram: {exc}"}
    return {"mermaid": diagram, "mermaid_block": f"```mermaid\n{diagram}\n```"}

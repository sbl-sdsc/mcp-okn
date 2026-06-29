"""Schema tools: get_schema, visualize_schema."""

from __future__ import annotations

from typing import Any

from .. import schema, session
from ..app import mcp


@mcp.tool()
async def get_schema(shortname: str, compact: bool = True) -> dict[str, Any]:
    """Get the schema (classes, predicates, edge/node properties) for one KG.

    Call this BEFORE writing a `sparql_query` for a KG, to learn its specific
    entity types, predicates, and property names. Prefers curated metadata and
    falls back to probing the federation endpoint for the distinct classes and
    predicates used in the KG's named graph.

    Args:
        shortname: The KG shortname (e.g. `prokn`, `sawgraph`), as returned by
            `list_kgs`.
        compact: If True (default), return the compact schema. Set False to also
            include an `edge_property_summary` highlighting relationships that
            carry edge properties (with ready-to-use reification query templates).

    Returns:
        `{"shortname": ..., "schema": {"classes", "predicates",
        "edge_properties", "node_properties"}}`. Each of `classes`/`predicates`/
        `node_properties` is a `{"columns", "data", "count"}` table;
        `edge_properties` maps relationship names to their properties and a
        `query_template` showing the RDF reification pattern to query them.
        Also includes `next_step` reminding you to `probe_namespaces` for any
        predicate whose objects are ontology terms before writing the query. For
        KGs with domain rules the schema alone does not convey (e.g.
        `spoke-genelab`), also includes `usage_notes` with `guidance` prose and a
        reusable `query_snippet`.
    """
    result = await schema.get_schema(shortname, compact=compact)
    if isinstance(result, dict) and "schema" in result:
        notes = schema.usage_notes(shortname)
        if notes is not None:
            result["usage_notes"] = notes
        # Surface the value-space step at the point of decision: the model is
        # holding the schema and about to write SPARQL, which is exactly when it
        # tends to assume an ontology (DOID) instead of checking (MONDO).
        result["next_step"] = (
            "Before joining on a predicate whose objects are ontology terms "
            "(diseases, chemicals, genes, anatomy), call "
            f"probe_namespaces({shortname!r}, <predicate>) to see which identifier "
            "scheme actually populates it (e.g. MONDO vs DOID vs NCIT) and how "
            "many of each. Pick the richest namespace — do NOT infer the ontology "
            "from the predicate or KG name, and do not give up if your first guess "
            f"has no hierarchy in ubergraph. If the id you need isn't on an obvious "
            f"predicate, call find_crosswalks({shortname!r}): ontology ids are "
            "often attached via rdfs:seeAlso / owl:sameAs / skos:exactMatch rather "
            "than a domain predicate."
        )
    return result


@mcp.tool()
async def visualize_schema(shortname: str) -> dict[str, Any]:
    """Generate a Mermaid class diagram of a KG's schema.

    Builds the diagram deterministically from `get_schema` (no drafting needed):
    node classes become class boxes (with node properties as members), edge
    predicates become labeled arrows, and predicates that carry edge properties
    become intermediary classes with typed fields wired `source --> edge -->
    target`. Node (entity) classes are colored light blue and edge
    (relationship) classes orange, with a legend showing both. When the curated
    metadata names predicates but not their endpoints (e.g. `sawgraph`), edges
    are recovered from the graph's `rdfs:domain`/`rdfs:range`, scoped to the
    curated classes; any predicate still without endpoints is listed as a `%%`
    comment rather than guessed at.

    Args:
        shortname: The KG shortname (e.g. `spoke-genelab`), as returned by
            `list_kgs`.

    Returns:
        `{"shortname": ..., "mermaid": ..., "mermaid_block": ...}`.
        `mermaid_block` is the diagram ALREADY wrapped in a ```mermaid fenced
        code block; `mermaid` is the same diagram fence-free (for saving as a
        `.mermaid` file).

    PRESENTATION (required): output `mermaid_block` VERBATIM, and nothing else.
    Do NOT redraw, re-render, or convert it — in particular do NOT emit SVG, PNG,
    HTML, an image, an artifact, or a hand-built diagram. Mermaid clients render
    the fenced block natively; producing your own graphic yields a messy,
    incorrect picture.

    The diagram is logged to the session automatically (like queries), so
    `create_chat_transcript` renders it without you re-supplying it.
    """
    result = await schema.visualize_schema(shortname)
    if "mermaid" in result:
        session.record_visualization(shortname, result["mermaid"])
        # Pre-fenced form so the model can echo it verbatim without redrawing.
        result["mermaid_block"] = f"```mermaid\n{result['mermaid']}\n```"
    return result

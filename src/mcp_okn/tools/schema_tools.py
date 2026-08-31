"""Schema tools: get_schema, visualize_schema."""

from __future__ import annotations

from typing import Any

from .. import schema, session
from ..app import mcp


@mcp.tool()
async def get_schema(shortname: str, compact: bool = True) -> dict[str, Any]:
    """Get a VoID-authoritative, semantically enriched schema for one KG.

    Call this BEFORE writing a `sparql_query` for a KG, to learn its specific
    entity types and predicates. The `okn-void` graph is the sole topology
    authority: it determines which classes/predicates exist, their counts, and
    observed source → predicate → target paths. Curated metadata enriches only
    matching observed URIs with labels, descriptions, node-property ownership,
    and RDF reification guidance. Curated predicate SourceClass/TargetClass
    endpoints are ignored and direct graph probing is not used.

    Args:
        shortname: The KG shortname (e.g. `prokn`, `sawgraph`), as returned by
            `list_kgs`.
        compact: If True (default), return classes/predicates with their observed
            `entity_count` / `triple_count` columns plus semantic enrichment.
            Set False to also include observed source-class → predicate →
            target-class paths, datatype/language value shapes, and an
            edge-property summary.

    Returns:
        `schema_sources` names the layers used, normally `["okn-void",
        "curated_metadata"]`. `metadata_enrichment` reports match counts and
        explicitly confirms that curated predicate endpoints were not used.
        Every enriched row/property carries `metadata_source`. With
        `compact=False`, `observed_edges` carries source class, predicate, target
        class, and edge count, while `value_shapes` carries each predicate's
        observed datatype/language. Node/edge properties whose curated owner or
        `EdgePropertyOf` mapping is missing remain visible with an explicit
        unresolved status; no endpoint or query template is invented. Mapped
        edge properties explicitly state that both URIs were observed in VoID but
        the statement-level association remains curated and was not independently
        verified. If semantic metadata cannot be fetched, the observed VoID
        schema is returned with a warning rather than silently appearing fully
        enriched.
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
async def visualize_schema(shortname: str, scope: str | None = None) -> dict[str, Any]:
    """Generate a semantically enriched Mermaid diagram with observed topology.

    Builds the diagram deterministically from `get_schema` (no drafting needed):
    observed classes become class boxes and observed source-class → predicate →
    target-class paths become labeled arrows. Curated labels, node properties,
    and edge-property/reification metadata enrich those observed elements.
    Curated predicate endpoints and declared `rdfs:domain`/`rdfs:range` are not
    used. Predicates without an observed object-class path are listed as a `%%`
    comment rather than guessed at.

    Args:
        shortname: The KG shortname (e.g. `spoke-genelab`), as returned by
            `list_kgs`.
        scope: OPTIONAL log scope — the same string passed to `sparql_query` and
            `create_chat_transcript`. Omit for a normal single analysis; pass a
            unique label when several analyses run concurrently against this
            server (parallel subagents share one MCP session, so an unscoped log
            mixes their entries).

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
    `create_chat_transcript` renders it without you re-supplying it. Pass the same
    `scope` you pass to `sparql_query` / `create_chat_transcript` when several
    analyses run concurrently against this server (e.g. parallel subagents, which
    share one MCP session); omit it otherwise.
    """
    result = await schema.visualize_schema(shortname)
    if "mermaid" in result:
        session.record_visualization(shortname, result["mermaid"], scope=scope)
        # Pre-fenced form so the model can echo it verbatim without redrawing.
        result["mermaid_block"] = f"```mermaid\n{result['mermaid']}\n```"
    return result

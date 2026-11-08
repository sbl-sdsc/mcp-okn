"""Schema tools: get_schema, visualize_schema."""

from __future__ import annotations

from typing import Any

from .. import schema, schema_view, session
from ..app import mcp


@mcp.tool()
async def get_schema(
    shortname: str, compact: bool = True, match: str | None = None
) -> dict[str, Any]:
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
        match: Optional search term. Returns only the classes, predicates and
            properties whose IRI, label or description contains it (case-
            insensitive; separate alternatives with `|`, e.g.
            `"prevalence|population"`), with full detail, plus the classes they
            connect. Use it when the overview was trimmed to fit (`schema_view`
            says so) or to find where a concept lives before writing SPARQL —
            it reads the schema metadata, so it is instant, unlike scanning the
            live graph's predicates.

    Returns:
        `{"shortname": ..., "schema": {"classes", "predicates",
        "edge_properties", "node_properties"}, "sparql_prefixes": ...}`. IRIs
        are written `prefix:local`; `sparql_prefixes` holds the PREFIX lines to
        paste into your query. Each of `classes`/`predicates`/
        `node_properties` is a `{"columns", "data", "count"}` table;
        `edge_properties` maps relationship names to their properties and a
        `query_template` showing the RDF reification pattern to query them.
        When the predicates table has a `pattern` column (how each predicate is
        stored: `direct`, `reified`, `axiom`, `declared`, `;`-joined), check it
        before writing `?s <p> ?o`: `pattern_guidance` says what each
        non-direct pattern means for the query and gives an OWL-restriction
        `query_template` for `axiom` predicates, which have no direct triples.
        Also includes `next_step` reminding you to `probe_namespaces` for any
        predicate whose objects are ontology terms before writing the query. For
        KGs with domain rules the schema alone does not convey (e.g.
        `spoke-genelab`), also includes `usage_notes` with `guidance` prose and a
        reusable `query_snippet`.

        The reply is kept under about 40,000 characters so clients deliver it
        whole. When the full schema is larger, detail is trimmed (repeated
        sections, then descriptions, then the smallest rows) and `schema_view`
        lists what was trimmed and how many rows were left out; call again with
        `match` for the rest.
    """
    result = await schema.get_schema(shortname, compact=compact)
    notes = schema.usage_notes(shortname)
    # Attach notes even when no schema is enumerated: for a too-large bridge KG
    # (babel) the notes ARE the schema.
    if isinstance(result, dict) and notes is not None:
        result["usage_notes"] = notes
    if isinstance(result, dict) and "schema" in result:
        # Surface the value-space step at the point of decision: the model is
        # holding the schema and about to write SPARQL, which is exactly when it
        # tends to assume an ontology (DOID) instead of checking (MONDO).
        result["next_step"] = (
            "Before joining on a predicate whose objects are ontology terms "
            "(diseases, chemicals, genes, anatomy), check which identifier scheme "
            f"fills it with probe_namespaces({shortname!r}, <predicate>) and pick the "
            "richest; don't infer it from names. If the id you need isn't on an "
            f"obvious predicate, try find_crosswalks({shortname!r}) (rdfs:seeAlso / "
            "owl:sameAs / skos:exactMatch)."
        )
    if match and match.strip():
        result = schema_view.match_schema(result, match)
    result = schema_view.compact_reply(result, templates=bool(match))
    return schema_view.fit_to_budget(result, shortname)


@mcp.tool()
async def visualize_schema(shortname: str, scope: str | None = None) -> dict[str, Any]:
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
    comment rather than guessed at. OWL/RDF constructs (owl:Class,
    owl:Restriction, …) are left out. A schema with more than 60 classes is
    drawn as its 60 most-connected classes, with a `note` in the result and the
    omitted classes listed as `%%` comments; use `get_schema` for the full list.

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

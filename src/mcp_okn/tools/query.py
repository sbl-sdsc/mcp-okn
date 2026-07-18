"""SPARQL query tools: sparql_query, expand_ontology_term."""

from __future__ import annotations

from typing import Any

from .. import session
from ..app import mcp
from ..sparql import (
    SparqlError,
    named_graph,
    normalize_schema_org,
    run_sparql,
)
from ._shared import _to_uri


def _compact(result: dict[str, Any]) -> dict[str, Any]:
    """Reshape a json result's dict rows into positional arrays.

    ``{"vars", "rows", "row_count"}`` (rows keyed by variable) becomes
    ``{"columns", "data", "count"}`` (one ``columns`` header, each row an array in
    ``columns`` order), dropping the per-row repetition of variable names. Unbound
    cells are ``None``. Sidecar fields (e.g. ``hint``) are carried through. Numeric/
    boolean values keep the casting :func:`_flatten_bindings` already applied.
    """
    cols = result.get("vars", [])
    out: dict[str, Any] = {
        "columns": cols,
        "data": [[row.get(c) for c in cols] for row in result.get("rows", [])],
        "count": result.get("row_count", 0),
    }
    if "hint" in result:
        out["hint"] = result["hint"]
    return out


@mcp.tool()
async def sparql_query(
    query: str,
    format: str = "json",
    exploratory: bool = False,
    compact: bool = False,
    scope: str | None = None,
) -> Any:
    """Run a SPARQL query against the OKN federation endpoint.

    Scope each knowledge graph with its named graph, e.g.::

        PREFIX up: <http://purl.uniprot.org/core/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?mondo ?label WHERE {
          GRAPH <https://purl.org/okn/frink/kg/prokn> {
            ?d a up:Disease ; rdfs:seeAlso ?mondo .
          }
        }

    BEFORE joining a target KG on an ontology term (the `<...MONDO_...>` IRIs
    below), confirm which namespace that KG actually stores for the predicate by
    calling `probe_namespaces(shortname, predicate)` first. KGs routinely carry
    several ontologies for the same field (e.g. NDE's `schema:healthCondition`
    holds MONDO, DOID, HP and NCIT), and picking the sparse one — or one with no
    `subClassOf*` hierarchy in ubergraph — yields a fraction of the results.

    For category/subtype questions ("all cardiovascular diseases", "any asthma",
    "subtypes of X"), expand the category INLINE using ubergraph's precomputed
    transitive closure and join it to the target KG in the SAME query — do not
    walk the hierarchy level by level or fetch the tree separately::

        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?disease ?label WHERE {
          GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
            ?disease rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0004995> .
            OPTIONAL { ?disease rdfs:label ?label }
          }
          GRAPH <https://purl.org/okn/frink/kg/SOME_TARGET_KG> {
            ?record some:predicate ?disease .
          }
        }

    Args:
        query: A complete SPARQL query string.
        format: `json` (default; parsed into rows), `csv`, or `tsv` (raw text).
        exploratory: Set True for schema-probing, sampling, or trial-and-error
            queries you don't want in the transcript. Exploratory queries are
            never logged. (Queries that error or return no rows are skipped
            automatically, exploratory or not.)
        compact: Set True to return json results in a token-efficient shape that
            lists the column names ONCE instead of repeating them on every row —
            useful for large, wide result sets. `{"columns": [...], "data":
            [[...], ...], "count": N}` where each `data` row is an array in
            `columns` order (unbound cells are `null`). Default False returns the
            self-describing dict-row shape below. Only affects json (csv/tsv and
            errors are unchanged) and only the returned payload — the transcript
            log is unaffected.
        scope: OPTIONAL log scope. Omit it for a normal single analysis. Pass a
            unique label when SEVERAL ANALYSES RUN CONCURRENTLY against this
            server — most importantly parallel subagents, which all share ONE MCP
            session. Without it their queries interleave in a single log and one
            agent's SPARQL ends up in another's transcript. Use the SAME scope
            string in `reset_query_log`, `sparql_query` and
            `create_chat_transcript` for a given analysis.

    Returns:
        For json (default): `{"vars": [...], "rows": [...], "row_count": N}`.
        For json with `compact=True`: `{"columns": [...], "data": [[...], ...],
        "count": N}`.
        For csv/tsv: `{"format": ..., "text": "..."}`.
        A zero-row json result also carries a `hint` field — DON'T conclude the
        data is absent; the join term's identifier scheme is the usual culprit.

    Note: The endpoint runs on a read-only filesystem, so queries needing a
    large external sort over a full-graph scan may fail; add a `LIMIT`, narrow
    the pattern, or scope to a named graph.
    """
    # Normalize up front so the logged/transcript query matches what executes
    # (run_sparql normalizes again; the substitution is idempotent).
    query = normalize_schema_org(query)
    try:
        result = await run_sparql(query, fmt=format)
        # Always hand the query to the logger: it adds a productive query to the
        # log and files an exploratory/empty one into the skipped list (tagged
        # with the reason) so it is visible rather than silently dropped.
        session.record(
            query, format, result=result, exploratory=exploratory, scope=scope
        )
        # Rescue the common "got lost on an empty result" failure: an
        # ontology-id join most often returns nothing because the predicate uses
        # a different namespace than assumed, or the id is only reachable via a
        # crosswalk predicate. Point at the diagnostics at the moment of need.
        if isinstance(result, dict) and result.get("row_count") == 0:
            result["hint"] = (
                "0 rows — do NOT assume the data is absent. If you joined on an "
                "ontology/identifier term, likely causes: (1) the predicate uses a "
                "different namespace than you assumed — run probe_namespaces(kg, "
                "predicate); (2) the id is reachable only via a crosswalk predicate "
                "like rdfs:seeAlso / owl:sameAs / skos:exactMatch / "
                "oboInOwl:hasDbXref — run find_crosswalks(kg); (3) the IRI FORM "
                "differs across graphs (subdomain e.g. www.omim.org vs omim.org, "
                "http vs https, trailing slash) so it silently matches nothing — "
                "rewrite with BIND(IRI(REPLACE(...))); (4) you joined on a "
                "schema.org predicate and this KG stores the non-canonical https "
                "form (nikg/ruralkg/ufokn do) — a bracketed <https://schema.org/X> "
                "is canonicalized to http, so name the predicate as a VARIABLE and "
                "match it scheme-free: ?s ?p ?o . "
                "FILTER(STRENDS(STR(?p),'schema.org/X')). Check, then retry."
            )
        # Compact LAST — after logging the dict-row result, so the transcript is
        # unaffected. Only json results (those with `rows`) reshape; csv/tsv pass
        # through.
        if compact and isinstance(result, dict) and "rows" in result:
            result = _compact(result)
        return result
    except SparqlError as exc:
        # Retain the failed query (with its error) in the skipped list so it is
        # not lost — this is the read-only-filesystem / oversized-sort case that
        # silently vanished before.
        session.record(query, format, error=str(exc), scope=scope)
        return {"error": str(exc)}


@mcp.tool()
async def expand_ontology_term(
    term: str,
    relation: str = "subClassOf",
    direction: str = "descendants",
    include_self: bool = True,
    limit: int = 1000,
    scope: str | None = None,
) -> Any:
    """Expand an ontology term to its full subtree/closure via `ubergraph`.

    USE THIS (or the equivalent inline `rdfs:subClassOf*` pattern) for any
    "all X under category Y" / "subtypes of" / "descendants of" question, e.g.
    "all cardiovascular diseases". Ubergraph stores precomputed inferred edges,
    so this returns the COMPLETE subtree in one call. Do not walk the hierarchy
    level by level or fetch the tree separately.

    Args:
        term: The ontology term as a full URI
            (e.g. `http://purl.obolibrary.org/obo/MONDO_0003847`) or a CURIE
            with an OBO prefix (e.g. `MONDO:0003847`, `CHEBI:24431`).
        relation: `subClassOf` (default) or `partOf`.
        direction: `descendants` (terms under `term`) or `ancestors`.
        include_self: If True (default), include `term` itself in the results
            (reflexive `*` path); if False, return only strict descendants/
            ancestors (non-reflexive `+` path).
        limit: Max rows to return.
        scope: OPTIONAL log scope — the same string passed to `sparql_query` and
            `create_chat_transcript`. Omit for a normal single analysis; pass a
            unique label when several analyses run concurrently against this
            server (parallel subagents share one MCP session, so an unscoped log
            mixes their entries).

    Returns the matching terms with their `rdfs:label`.
    """
    term_uri = _to_uri(term)
    rel = {
        "subClassOf": "rdfs:subClassOf",
        "partof": "<http://purl.obolibrary.org/obo/BFO_0000050>",
        "partOf": "<http://purl.obolibrary.org/obo/BFO_0000050>",
    }.get(relation, "rdfs:subClassOf")

    # `*` is reflexive (includes `term`); `+` is strict (excludes it).
    op = "*" if include_self else "+"
    if direction == "ancestors":
        pattern = f"<{term_uri}> {rel}{op} ?term ."
    else:
        pattern = f"?term {rel}{op} <{term_uri}> ."

    graph = named_graph("ubergraph")
    query = f"""\
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?term ?label WHERE {{
  GRAPH <{graph}> {{
    {pattern}
    OPTIONAL {{ ?term rdfs:label ?label . }}
  }}
}} LIMIT {int(limit)}"""
    try:
        result = await run_sparql(query)
        session.record(query, "json", result=result, scope=scope)
        return result
    except SparqlError as exc:
        session.record(query, "json", error=str(exc), scope=scope)
        return {"error": str(exc), "query": query}

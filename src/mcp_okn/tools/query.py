"""SPARQL query tools: sparql_query, expand_ontology_term."""

from __future__ import annotations

import copy
import re
from typing import Any

from .. import schema, schema_view, session
from ..app import mcp
from ..budget import fit_sparql_result
from ..diagnose import diagnose_empty
from ..query_lint import (
    SCAN_TIMEOUT,
    add_missing_prefixes,
    check_query,
    graph_scoped_prefixes,
    named_kgs,
    undeclared_prefixes,
)
from ..sparql import (
    SparqlError,
    error_summary,
    named_graph,
    normalize_schema_org,
    run_sparql,
)
from ._shared import _to_uri

#: ``{name: namespace}`` that ``get_schema`` prints for each KG's full schema.
_kg_prefix_cache: dict[str, dict[str, str]] = {}
_PREFIX_LINE = re.compile(r"PREFIX\s+([\w.\-]+):\s*<([^>]+)>")


async def _kg_prefixes(shortname: str) -> dict[str, str]:
    if shortname not in _kg_prefix_cache:
        prefixes: dict[str, str] = {}
        try:
            result = await schema.get_schema(shortname, compact=True)
            if isinstance(result, dict) and isinstance(result.get("schema"), dict):
                # The same rewrite get_schema replies get, so the names match.
                reply = schema_view.compact_reply(copy.deepcopy(result))
                for line in str(reply.get("sparql_prefixes") or "").splitlines():
                    m = _PREFIX_LINE.match(line)
                    if m:
                        prefixes[m.group(1)] = m.group(2)
        except Exception:
            prefixes = {}
        _kg_prefix_cache[shortname] = prefixes
    return _kg_prefix_cache[shortname]


async def _graph_prefixes(query: str) -> dict[str, str]:
    """Prefixes from ``get_schema`` that the query uses undeclared, if unambiguous.

    Agents copy ``biolink:Gene`` from a schema reply and leave out the
    ``sparql_prefixes`` block, a guaranteed HTTP 400. Only the graphs the query
    names are consulted. A name two of them define differently (``kg:``) is
    resolved by the GRAPH blocks it is used in, and left out when that does not
    settle it.
    """
    if not undeclared_prefixes(query):
        return {}
    kgs = named_kgs(query)
    if not kgs:
        return {}
    return graph_scoped_prefixes(query, {kg: await _kg_prefixes(kg) for kg in kgs})


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
    # Sidecar fields (hint, diagnosis, warnings, prefixes_added) ride along.
    out.update(
        {k: v for k, v in result.items() if k not in ("vars", "rows", "row_count")}
    )
    return out


@mcp.tool()
async def sparql_query(
    query: str,
    format: str = "json",
    exploratory: bool = False,
    compact: bool = True,
    scope: str | None = None,
    allow_scan: bool = False,
) -> Any:
    """Run a SPARQL query against the OKN federation endpoint.

    AVOID FULL SCANS; they are what times out (queries stop after about 60 s). Bind
    known values exactly (`?s rdfs:label "asthma"@en`, `?s ?p "E-MTAB-5477"`): an
    all-variable `?s ?p ?o` constrained only by a string FILTER reads every triple
    in the graph. Find a predicate by name with `get_schema(kg, match="term")`, and
    an ontology term's IRI with `lookup_term("term")`. Scope a COUNT/GROUP BY to one
    class. Each UNION branch, MINUS and EXISTS is evaluated on its own: repeat the
    anchor (VALUES, `?x a <Class>`) inside each. A FILTER or BIND sees only its own
    group, so put one that compares two GRAPH blocks after both blocks.

    Scope each KG with its named graph:
    `GRAPH <https://purl.org/okn/frink/kg/prokn> { ... }`. Before joining a KG on
    ontology terms, check which namespace it stores for the predicate with
    `probe_namespaces(shortname, predicate)`: KGs often carry several (NDE's
    `schema:healthCondition` holds MONDO, DOID, HP and NCIT), and the sparse one,
    or one with no `subClassOf*` hierarchy in ubergraph, gives a fraction of the
    results.

    For category questions ("all cardiovascular diseases", "subtypes of X"), expand
    the category INLINE with ubergraph's transitive closure, joined to the target KG
    in the SAME query, not level by level::

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
        query: A complete SPARQL query. Undeclared standard prefixes (rdf, rdfs,
            xsd, owl, skos, ...) and those `get_schema` printed for the GRAPHs it
            names (biolink, ...) are added for you.
        format: `json` (default), `csv` or `tsv` (raw text).
        exploratory: True for probes and trial-and-error to keep out of the
            transcript. Queries that error or return no rows are skipped anyway.
        compact: False gives `{"vars", "rows": [{...}], "row_count"}`.
        scope: Log scope, only for SEVERAL analyses on one server at once
            (parallel subagents): pass the same label to `reset_query_log`,
            `sparql_query` and `create_chat_transcript`.
        allow_scan: Give a known scan shape the full time limit (otherwise 15 s
            and a rewrite), and send one the server would refuse as certain to
            fail.

    Returns:
        `{"columns", "data", "count"}`, or `{"format", "text"}` for csv/tsv. Over
        about 40,000 characters the rows are cut (`truncated`, `returned`, full
        `count`): aggregate or LIMIT instead of re-running. A zero-row reply adds a
        `diagnosis` (what matched nothing, or the join values on each side) and a
        `hint`; `warnings` flag a BIND/FILTER that cannot see its variable;
        `prefixes_added` lists declarations added.
    """
    # Normalize up front so the logged/transcript query matches what executes
    # (run_sparql normalizes again; the substitution is idempotent).
    query = normalize_schema_org(query)
    # An undeclared standard prefix (xsd: above all) is a guaranteed 400; declare
    # it, and say so, so the logged query is the one that ran.
    query, prefixes_added = add_missing_prefixes(query, await _graph_prefixes(query))
    check = check_query(query)
    if check.blocked and not allow_scan:
        # Certain to fail (out of memory or a timeout); say how to rewrite it.
        session.record(query, format, error=check.blocked, scope=scope)
        return {"error": check.blocked}
    # A known full-scan shape gets a short limit: the ones that finish do so in a
    # few seconds, and the rest stop quickly with a rewrite instead of minutes in.
    problem = None if allow_scan else check.scan
    try:
        result = await run_sparql(
            query, fmt=format, timeout=SCAN_TIMEOUT if problem else None
        )
    except SparqlError as exc:
        # Retain the failed query (with its error) in the skipped list so it is
        # not lost.
        session.record(query, format, error=str(exc), scope=scope)
        if problem and _is_timeout(exc):
            return {"error": problem}
        reply: dict[str, Any] = {"error": error_summary(exc)}
        if _is_out_of_memory(exc):
            reply["hint"] = MEMORY_ADVICE
        if check.warnings:
            reply["warnings"] = check.warnings
        if prefixes_added:
            reply["prefixes_added"] = prefixes_added
        return reply
    # Always hand the query to the logger: it adds a productive query to the
    # log and files an exploratory/empty one into the skipped list (tagged
    # with the reason) so it is visible rather than silently dropped.
    session.record(query, format, result=result, exploratory=exploratory, scope=scope)
    if isinstance(result, dict) and result.get("row_count") == 0:
        # Locate where the rows were lost (a missing term, a block that doesn't
        # join), so the agent doesn't spend its next turns probing for it.
        diagnosis = await diagnose_empty(query)
        if diagnosis:
            result["diagnosis"] = diagnosis
        result["hint"] = ZERO_ROW_SHORT_HINT if diagnosis else ZERO_ROW_HINT
    if check.warnings:
        result["warnings"] = check.warnings
    if prefixes_added:
        result["prefixes_added"] = prefixes_added
    # Compact LAST — after logging the dict-row result, so the transcript is
    # unaffected. Only json results (those with `rows`) reshape; csv/tsv pass
    # through.
    if compact and isinstance(result, dict) and "rows" in result:
        result = _compact(result)
    # Cap the inline reply (leading rows, full count, a hint). Also after
    # logging, so the transcript keeps every row.
    if isinstance(result, dict):
        result = fit_sparql_result(result)
    return result


#: Appended to every zero-row reply.
ZERO_ROW_HINT = (
    "0 rows. Don't assume the data is absent. Usual causes: (1) the "
    "predicate uses another id namespace (probe_namespaces(kg, pred)); "
    "(2) the id sits on a crosswalk predicate such as rdfs:seeAlso / "
    "owl:sameAs / skos:exactMatch / oboInOwl:hasDbXref "
    "(find_crosswalks(kg)); (3) the IRI form differs (www., http vs "
    "https, trailing slash), so rewrite with BIND(IRI(REPLACE(...))); "
    "(4) a schema.org predicate stored as https (nikg/ruralkg/ufokn): "
    "match ?p with FILTER(STRENDS(STR(?p),'schema.org/X'))."
)

#: The hint beside a diagnosis, which already names the likely cause.
ZERO_ROW_SHORT_HINT = (
    "0 rows; the diagnosis says where they were lost. An id written in another "
    "namespace is the usual cause (probe_namespaces, find_crosswalks, "
    "get_join_strategy), so rule that out before concluding the data is absent."
)

#: Added to QLever's "Tried to allocate … GB" error.
MEMORY_ADVICE = (
    "QLever ran out of memory: some part of the query was evaluated without its "
    "anchor and produced a huge intermediate result. Usual causes: (1) an "
    "all-variable triple such as `?x ?p ?o` inside a UNION branch, OPTIONAL, "
    "MINUS or EXISTS whose anchor (VALUES, `?x a <Class>`) sits outside it; QLever "
    "evaluates such a group on its own, so repeat the anchor inside it; (2) a "
    "variable predicate `?s ?p ?o` whose subject comes only from a BIND, which "
    "does not anchor a triple; (3) two GRAPH blocks with no shared variable "
    "(a cross product)."
)


def _is_out_of_memory(exc: SparqlError) -> bool:
    text = str(exc)
    return "Tried to allocate" in text or "memory limit" in text


def _is_timeout(exc: SparqlError) -> bool:
    text = str(exc)
    return "timed out after" in text or "Operation timed out" in text


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

    USE THIS (or the inline `rdfs:subClassOf*` pattern) for any "all X under
    category Y" / "subtypes of" / "descendants of" question. Ubergraph stores
    precomputed inferred edges, so this returns the COMPLETE subtree in one call.
    Do not walk the hierarchy level by level.

    Args:
        term: A full URI (`http://purl.obolibrary.org/obo/MONDO_0003847`) or an
            OBO CURIE (`MONDO:0003847`, `CHEBI:24431`).
        relation: `subClassOf` (default) or `partOf`.
        direction: `descendants` (terms under `term`) or `ancestors`.
        include_self: True (default) includes `term` itself (`*` path); False
            returns only strict descendants/ancestors (`+` path).
        limit: Max rows to return.
        scope: Optional log scope, as for `sparql_query`.

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
        return fit_sparql_result(result)
    except SparqlError as exc:
        session.record(query, "json", error=str(exc), scope=scope)
        return {"error": str(exc), "query": query}


#: Synonym predicates searched after rdfs:label, best match first.
_LOOKUP_PREDICATES = (
    ("label", "rdfs:label"),
    ("exact_synonym", "oio:hasExactSynonym"),
    ("related_synonym", "oio:hasRelatedSynonym"),
    ("narrow_synonym", "oio:hasNarrowSynonym"),
    ("broad_synonym", "oio:hasBroadSynonym"),
)


def _case_variants(label: str) -> list[str]:
    """The label as given plus its common capitalizations, deduplicated."""
    text = " ".join(label.split())
    forms = [text, text.lower(), text[:1].upper() + text[1:].lower(), text.title()]
    return list(dict.fromkeys(f for f in forms if f))


def _sparql_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _lookup_query(label: str, ontology: str | None, limit: int) -> str:
    values = " ".join(
        f"{lit} {lit}@en" for lit in map(_sparql_string, _case_variants(label))
    )
    branches = "\n    UNION\n    ".join(
        f'{{ ?term {pred} ?lit . BIND("{name}" AS ?matched_on) }}'
        for name, pred in _LOOKUP_PREDICATES
    )
    scope = ""
    if ontology:
        prefix = ontology.strip().rstrip(":_").upper()
        scope = (
            "\n  FILTER(STRSTARTS(STR(?term), "
            f'"http://purl.obolibrary.org/obo/{prefix}_"))'
        )
    graph = named_graph("ubergraph")
    return f"""\
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX oio: <http://www.geneontology.org/formats/oboInOwl#>
SELECT DISTINCT ?term ?label ?matched_on ?matched_text WHERE {{
  GRAPH <{graph}> {{
    VALUES ?lit {{ {values} }}
    {branches}
    OPTIONAL {{ ?term rdfs:label ?label }}
  }}
  BIND(STR(?lit) AS ?matched_text){scope}
}} LIMIT {int(limit)}"""


@mcp.tool()
async def lookup_term(
    label: str,
    ontology: str | None = None,
    limit: int = 25,
    scope: str | None = None,
) -> Any:
    """Find an ontology term's IRI from its name. A fast index lookup in ubergraph.

    Use this to resolve a category name ("autoimmune disease", "hormone
    secretion", "inborn errors of metabolism") to the IRI you then expand with
    `rdfs:subClassOf*` or `expand_ontology_term`. Do NOT search labels with
    `FILTER(CONTAINS(...))` or `LCASE(STR(?label)) = ...` over ubergraph: that
    scans every label in the federation's largest graph and times out.

    Matching is EXACT on the whole name (ignoring case), against `rdfs:label` and
    the OBO exact, related, narrow and broad synonyms, with or without an `@en`
    tag. Rows are ranked label first, then exact synonym, and so on. A name can
    match terms in several ontologies (MONDO, NCIT, DOID, …). Pass `ontology` to
    keep one, and pick the ontology the target KG actually stores (see
    `probe_namespaces`).

    Args:
        label: The term's name, e.g. `"cardiovascular disease"`.
        ontology: Optional OBO prefix to restrict to, e.g. `"MONDO"`, `"HP"`,
            `"GO"`, `"CHEBI"`.
        limit: Max rows.
        scope: OPTIONAL log scope, as for `sparql_query`.

    Returns `{"columns": ["term", "label", "matched_on", "matched_text"], "data":
    [...], "count": N}`. `label` is the term's own rdfs:label, which can differ
    from the name you searched (MONDO_0004995 is labelled "cardiovascular
    disorder" and matches "cardiovascular disease" as an exact synonym). An empty
    result means no term carries that exact name: try the formal name or a synonym
    (e.g. HP's "Abnormality of the nervous system" for "neurological
    involvement").
    """
    query = _lookup_query(label, ontology, limit)
    try:
        result = await run_sparql(query)
    except SparqlError as exc:
        session.record(query, "json", error=str(exc), scope=scope)
        return {"error": str(exc), "query": query}
    session.record(query, "json", result=result, scope=scope)
    rank = {name: i for i, (name, _) in enumerate(_LOOKUP_PREDICATES)}
    result["rows"].sort(
        key=lambda r: (rank.get(r.get("matched_on"), 99), str(r.get("term")))
    )
    # One row per term, keeping its best match (a term whose label and exact
    # synonym are the same text would otherwise appear twice).
    best: dict[Any, dict[str, Any]] = {}
    for row in result["rows"]:
        best.setdefault(row.get("term"), row)
    result["rows"] = list(best.values())
    result["row_count"] = len(result["rows"])
    out = _compact(result)
    if not out["count"]:
        out["hint"] = (
            f"No term in ubergraph is named exactly {label!r}"
            + (f" in {ontology}" if ontology else "")
            + ". Try the formal name or a synonym, or drop `ontology`. Do not fall "
            "back to a CONTAINS/REGEX scan over ubergraph labels: it times out."
        )
    return fit_sparql_result(out)

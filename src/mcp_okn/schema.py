"""Schema discovery for Proto-OKN knowledge graphs.

The public schema and visualization tools use only observed schema statistics
from the federation's ``okn-void`` graph. Legacy curated-metadata helpers remain
in this module for the separate payload-drift checker, but they are not runtime
schema sources.
"""

from __future__ import annotations

import asyncio
import csv
import re
from io import StringIO
from typing import Any

import httpx

from . import void as void_metadata
from .contrasts import (
    SPOKE_GENELAB_CONTRAST_GUIDANCE,
    SPOKE_GENELAB_CONTRAST_SNIPPET,
)
from .sparql import SparqlError, named_graph, run_sparql

#: Where the curated per-KG entity metadata CSVs live.
ENTITY_METADATA_BASE = (
    "https://raw.githubusercontent.com/sbl-sdsc/mcp-proto-okn/main/metadata/entities"
)

#: Provenance / dataset-summary vocabularies (VOID and friends) that some upstream
#: ``*_entities.csv`` files now embed as schema rows. These describe the dataset
#: (triple counts, class/property partitions, last-updated timestamps) rather than
#: the KG's queryable *domain* schema, so surfacing them in ``get_schema`` would
#: mislead a client into writing SPARQL against ``void:triples`` and the like. We
#: expose that provenance properly via ``get_kg_version`` / the ``okn-void`` graph,
#: so drop these rows at the CSV-parsing layer — that keeps both ``get_schema`` and
#: the drift-check fingerprint (:mod:`scripts.check_payload_drift`) domain-only.
_PROVENANCE_NAMESPACES = (
    "http://rdfs.org/ns/void#",  # VOID
    "http://ldf.fi/void-ext#",  # VOID-ext
    "http://purl.org/pav/",  # PAV provenance (e.g. pav:lastUpdatedOn)
)
_PROVENANCE_URIS = frozenset(
    {
        "http://purl.org/dc/terms/modified",
        "https://research.bioinformatics.udel.edu/ProKN/rdf/topClassName",
    }
)


def _is_provenance_uri(uri: str) -> bool:
    """True for provenance/dataset-summary vocabulary (VOID, PAV, …).

    Such terms describe the dataset rather than its queryable domain schema, so
    they are filtered out of the returned schemas.
    """
    return uri in _PROVENANCE_URIS or uri.startswith(_PROVENANCE_NAMESPACES)


#: Per-KG usage notes surfaced on ``get_schema`` (attached by the tool wrapper in
#: :mod:`mcp_okn.tools.schema_tools`), delivered exactly when a client is about to
#: write SPARQL for that KG. Only KGs with domain rules that the schema alone does
#: not convey are listed.
_KG_USAGE_NOTES: dict[str, dict[str, str]] = {
    "spoke-genelab": {
        "guidance": SPOKE_GENELAB_CONTRAST_GUIDANCE,
        "query_snippet": SPOKE_GENELAB_CONTRAST_SNIPPET,
    },
}


def usage_notes(shortname: str) -> dict[str, str] | None:
    """Return curated usage notes for a KG, or None if it has none."""
    return _KG_USAGE_NOTES.get(shortname)


#: Schema namespace template used inside generated edge-property templates.
_SCHEMA_NS = "https://purl.org/okn/frink/kg/{shortname}/schema/"

#: KGs too large to enumerate a schema for via brute-force SPARQL probing. `wikidata`
#: was measured: its probe spends ~62s hitting the endpoint's operation timeout twice
#: and learns nothing, so the caller is better served by the message below immediately.
_TOO_LARGE = {"ubergraph", "wikidata"}

#: Mermaid `style` declarations distinguishing the two kinds of class box. Node
#: (entity) classes are light blue; edge (relationship) classes are orange. The
#: per-class `style` statement is the form that actually renders fills in
#: `classDiagram` (a `classDef` + `:::` assignment parses but emits no fill in
#: current Mermaid).
_NODE_CLASS_STYLE = "fill:#BBDEFB,stroke:#1565C0,color:#000"
_EDGE_CLASS_STYLE = "fill:#FFE0B2,stroke:#E65100,color:#000"

# Process-lifetime cache of parsed entity metadata, keyed by shortname.
_metadata_cache: dict[str, dict[str, dict[str, str]]] = {}


async def fetch_entity_metadata(
    shortname: str,
    client: httpx.AsyncClient | None = None,
    refresh: bool = False,
) -> dict[str, dict[str, str]]:
    """Fetch and parse the curated entity metadata CSV for a KG (cached).

    Returns a dict mapping each URI to ``{label, description, type,
    edge_property_of, source_class, target_class}``. Returns an empty dict when
    no curated CSV exists for the KG. This legacy inventory is used by the
    payload-drift checker, not by the public schema tools.
    """
    if shortname in _metadata_cache and not refresh:
        return _metadata_cache[shortname]

    url = f"{ENTITY_METADATA_BASE}/{shortname}_entities.csv"
    owns = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            _metadata_cache[shortname] = {}
            return {}
        content = resp.text
    except httpx.HTTPError:
        _metadata_cache[shortname] = {}
        return {}
    finally:
        if owns:
            await client.aclose()

    metadata: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(StringIO(content)):
        uri = (row.get("URI") or "").strip()
        if not uri or _is_provenance_uri(uri):
            continue
        edge_property_of = (row.get("EdgePropertyOf") or "").strip()
        if uri in metadata and edge_property_of:
            # A single edge-property URI can belong to several relationships
            # (e.g. adj_p_value on both EXPRESSION and ABUNDANCE). Accumulate
            # the parents semicolon-separated so the join below finds them all.
            existing = metadata[uri].get("edge_property_of", "")
            metadata[uri]["edge_property_of"] = (
                f"{existing};{edge_property_of}" if existing else edge_property_of
            )
        else:
            metadata[uri] = {
                "label": (row.get("Label") or "").strip(),
                "description": (row.get("Description") or "").strip(),
                "type": (row.get("Type") or "").strip(),
                "edge_property_of": edge_property_of,
                "source_class": (row.get("SourceClass") or "").strip(),
                "target_class": (row.get("TargetClass") or "").strip(),
            }

    _metadata_cache[shortname] = metadata
    return metadata


def _generate_query_template(
    shortname: str,
    relationship_label: str,
    source_class: str,
    target_class: str,
    properties: list[dict[str, Any]],
) -> str:
    """Generate a SPARQL template for a reified relationship with edge properties."""
    source_var = source_class.lower() if source_class else "source"
    target_var = target_class.lower() if target_class else "target"
    schema_ns = _SCHEMA_NS.format(shortname=shortname)

    prop_selects = [f"?{p['label']}" for p in properties]
    prop_patterns = [f"        schema:{p['label']} ?{p['label']} ;" for p in properties]
    if prop_patterns:
        prop_patterns[-1] = prop_patterns[-1].rstrip(" ;") + " ."

    return (
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
        f"PREFIX schema: <{schema_ns}>\n\n"
        f"SELECT ?{source_var} ?{target_var} {' '.join(prop_selects)}\n"
        "WHERE {\n"
        f"  ?stmt rdf:subject ?{source_var} ;\n"
        f"        rdf:predicate schema:{relationship_label} ;\n"
        f"        rdf:object ?{target_var} ;\n"
        f"{chr(10).join(prop_patterns)}\n"
        "}"
    )


def _build_schema_from_metadata(
    shortname: str, entity_metadata: dict[str, dict[str, str]], compact: bool
) -> dict[str, Any]:
    """Build the schema response from curated entity metadata."""
    classes: list[dict[str, str]] = []
    predicates: list[dict[str, Any]] = []
    edge_properties_dict: dict[str, list[dict[str, str]]] = {}
    node_properties: list[dict[str, str]] = []

    for uri, meta in entity_metadata.items():
        entity_type = (meta.get("type") or "").lower()
        if entity_type == "class":
            classes.append(
                {
                    "uri": uri,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                }
            )
        elif entity_type == "predicate":
            short_name = uri.split("/")[-1] if "/" in uri else uri
            predicates.append(
                {
                    "uri": uri,
                    "short_name": short_name,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                    "source_class": meta.get("source_class", ""),
                    "target_class": meta.get("target_class", ""),
                    "has_edge_properties": False,
                }
            )
        elif entity_type == "edgeproperty":
            parents = meta.get("edge_property_of", "")
            for parent in (p.strip() for p in parents.split(";") if p.strip()):
                edge_properties_dict.setdefault(parent, []).append(
                    {
                        "uri": uri,
                        "label": meta.get("label", ""),
                        "description": meta.get("description", ""),
                        "type": meta.get("type", ""),
                    }
                )
        elif entity_type == "nodeproperty":
            node_properties.append(
                {
                    "uri": uri,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                    "class": meta.get("source_class", ""),
                }
            )

    # Flag predicates that carry edge properties (match on short name).
    for pred in predicates:
        if pred["short_name"] in edge_properties_dict:
            pred["has_edge_properties"] = True

    edge_properties_output: dict[str, Any] = {}
    for relationship_label, props in edge_properties_dict.items():
        rel = next(
            (p for p in predicates if p["short_name"] == relationship_label), None
        )
        if rel is None:
            continue
        edge_properties_output[relationship_label] = {
            "uri": rel["uri"],
            "label": relationship_label,
            "description": rel["description"],
            "source_class": rel["source_class"],
            "target_class": rel["target_class"],
            "properties": props,
            "query_template": _generate_query_template(
                shortname,
                relationship_label,
                rel["source_class"],
                rel["target_class"],
                props,
            ),
        }

    result: dict[str, Any] = {
        "classes": {
            "columns": ["uri", "label", "description", "type"],
            "data": [
                [c["uri"], c["label"], c["description"], c["type"]] for c in classes
            ],
            "count": len(classes),
        },
        "predicates": {
            "columns": [
                "uri",
                "label",
                "description",
                "type",
                "source_class",
                "target_class",
                "has_edge_properties",
            ],
            "data": [
                [
                    p["uri"],
                    p["label"],
                    p["description"],
                    p["type"],
                    p["source_class"],
                    p["target_class"],
                    p["has_edge_properties"],
                ]
                for p in predicates
            ],
            "count": len(predicates),
        },
        "edge_properties": edge_properties_output,
        "node_properties": {
            "columns": ["uri", "label", "description", "type", "class"],
            "data": [
                [n["uri"], n["label"], n["description"], n["type"], n["class"]]
                for n in node_properties
            ],
            "count": len(node_properties),
        },
    }

    if not compact and edge_properties_output:
        result = {
            "edge_property_summary": {
                "CRITICAL_NOTE": (
                    "Some relationships have edge properties (data stored on the "
                    "relationship itself). To query these, use the RDF reification "
                    "pattern shown in each edge's query_template."
                ),
                "edges_with_properties": [
                    {
                        "relationship": label,
                        "uri": info["uri"],
                        "properties": [
                            {
                                "name": p.get("label", ""),
                                "type": p.get("description", "")
                                .split("(")[-1]
                                .rstrip(")"),
                            }
                            for p in info.get("properties", [])
                        ],
                        "example_query": info.get("query_template", ""),
                    }
                    for label, info in edge_properties_output.items()
                ],
            },
            **result,
        }

    return result


def _should_exclude_uri(uri: str) -> bool:
    """Filter out RDF-syntax-namespace URIs (e.g. container props rdf:_1, rdf:_2)."""
    return uri.startswith(
        (
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "https://www.w3.org/1999/02/22-rdf-syntax-ns#",
        )
    )


def _include_domain_uri(uri: str) -> bool:
    """Whether an observed VoID class/predicate belongs in the domain schema."""
    return bool(uri) and not _is_provenance_uri(uri) and not _should_exclude_uri(uri)


def _empty_schema() -> dict[str, Any]:
    """Return the VoID-only schema table shape."""
    return {
        "classes": {"columns": ["uri"], "data": [], "count": 0},
        "predicates": {"columns": ["uri"], "data": [], "count": 0},
    }


def _merge_partition_table(
    table: dict[str, Any],
    observed: list[dict[str, Any]],
    count_column: str,
) -> None:
    """Append an observed count column and any missing URI rows to one table."""
    columns = table.setdefault("columns", ["uri"])
    data = table.setdefault("data", [])
    if "uri" not in columns:
        return
    uri_idx = columns.index("uri")
    if count_column not in columns:
        columns.append(count_column)
        for row in data:
            row.append(None)
    count_idx = columns.index(count_column)

    by_uri = {
        str(item["uri"]): item.get(count_column)
        for item in observed
        if _include_domain_uri(str(item.get("uri") or ""))
    }
    existing: set[str] = set()
    for row in data:
        if len(row) <= uri_idx:
            continue
        uri = str(row[uri_idx])
        existing.add(uri)
        while len(row) < len(columns):
            row.append(None)
        row[count_idx] = by_uri.get(uri)

    for uri in sorted(set(by_uri) - existing):
        new_row: list[Any] = []
        for column in columns:
            if column == "uri":
                new_row.append(uri)
            elif column == count_column:
                new_row.append(by_uri[uri])
            elif column == "has_edge_properties":
                new_row.append(False)
            else:
                new_row.append("")
        data.append(new_row)
    table["count"] = len(data)


def merge_void_partitions(
    schema: dict[str, Any],
    partitions: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Merge observed VoID class/property partitions into a schema table."""
    _merge_partition_table(
        schema["classes"], partitions.get("classes", []), "entity_count"
    )
    _merge_partition_table(
        schema["predicates"], partitions.get("predicates", []), "triple_count"
    )
    return schema


def _table_uris(table: dict[str, Any]) -> list[str]:
    """Return non-empty URI values from a compact schema table."""
    columns = table.get("columns", [])
    if "uri" not in columns:
        return []
    idx = columns.index("uri")
    return [
        str(row[idx]) for row in table.get("data", []) if len(row) > idx and row[idx]
    ]


def _observed_edges_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Format VoID observed edge paths as a compact table."""
    kept = [
        row
        for row in rows
        if all(
            _include_domain_uri(str(row.get(key) or ""))
            for key in ("source_class", "predicate", "target_class")
        )
    ]
    columns = ["source_class", "predicate", "target_class", "triple_count"]
    return {
        "columns": columns,
        "data": [[row.get(column) for column in columns] for row in kept],
        "count": len(kept),
    }


def _value_shapes_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Format VoID datatype/language partitions as a compact table."""
    kept = [row for row in rows if _include_domain_uri(str(row.get("predicate") or ""))]
    columns = ["predicate", "kind", "value", "triple_count"]
    return {
        "columns": columns,
        "data": [[row.get(column) for column in columns] for row in kept],
        "count": len(kept),
    }


async def _probe_schema(shortname: str) -> dict[str, Any]:
    """Legacy helper that probes classes and predicates in a named graph.

    The public schema tools do not call this; they require observed VoID
    partitions.
    """
    graph = named_graph(shortname)
    # Classes are probed by TWO separate queries, not one UNION. Combining the
    # unbound `?s a ?class` with the declared-class branches made QLever's planner
    # try to allocate 37.9 GB and fail with HTTP 500 — instantly, for EVERY graph,
    # so this whole path was dead. Split, each part runs fine (measured on
    # identifier-mappings: ~5s for the instance types, ~0.1s for the declarations).
    instance_class_query = f"""\
SELECT DISTINCT ?class WHERE {{
  GRAPH <{graph}> {{
    ?s a ?class .
  }}
}}"""

    # Classes DECLARED but possibly never instantiated. (`a` already IS rdf:type, so
    # the old query's separate rdf:type branch was a duplicate of the one above.)
    declared_class_query = f"""\
SELECT DISTINCT ?class WHERE {{
  GRAPH <{graph}> {{
    {{ ?class a <http://www.w3.org/2000/01/rdf-schema#Class> . }}
    UNION {{ ?class a <http://www.w3.org/2002/07/owl#Class> . }}
  }}
}}"""

    predicate_query = f"""\
SELECT DISTINCT ?predicate WHERE {{
  GRAPH <{graph}> {{
    ?s ?predicate ?o .
  }}
}}"""

    # Independent probes of the same graph — run them together rather than paying
    # every round trip in series (the same pattern as probe.find_crosswalks).
    # `return_exceptions=True` so ALL results are consumed before we raise: a bare
    # gather would surface the first failure and leave a sibling's exception
    # unretrieved. Ordering is done below rather than by the endpoint — the results
    # are merged anyway, so an ORDER BY would just be work the server repeats.
    probed: list[Any] = await asyncio.gather(
        run_sparql(instance_class_query),
        run_sparql(declared_class_query),
        run_sparql(predicate_query),
        return_exceptions=True,
    )
    for outcome in probed:
        if isinstance(outcome, BaseException):
            raise outcome
    instance_classes, declared_classes, predicates = probed

    class_uris = {
        r["class"]
        for result in (instance_classes, declared_classes)
        for r in result.get("rows", [])
        if r.get("class") and not _should_exclude_uri(r["class"])
    }
    class_data = [[uri] for uri in sorted(class_uris)]
    predicate_data = [
        [r["predicate"]]
        for r in sorted(
            predicates.get("rows", []), key=lambda r: r.get("predicate") or ""
        )
        if r.get("predicate") and not _should_exclude_uri(r["predicate"])
    ]

    return {
        "classes": {"columns": ["uri"], "data": class_data, "count": len(class_data)},
        "predicates": {
            "columns": ["uri"],
            "data": predicate_data,
            "count": len(predicate_data),
        },
        "edge_properties": {},
        "node_properties": {"columns": ["uri"], "data": [], "count": 0},
    }


async def get_schema(shortname: str, compact: bool = True) -> dict[str, Any]:
    """Return the observed VoID schema for a KG.

    Args:
        shortname: The KG shortname (e.g. ``prokn``, ``spoke``), as returned by
            ``list_kgs``.
        compact: If True (default), return classes/predicates with observed
            entity/triple counts. Set False to also include observed edge paths
            and literal datatype/language value shapes.
    """
    partitions = await void_metadata.fetch_schema_partitions(shortname)
    has_partitions = bool(partitions["classes"] or partitions["predicates"])
    if not has_partitions:
        return {
            "shortname": shortname,
            "error": f"No observed VoID schema partitions are available for `{shortname}`.",
            "schema_sources": ["okn-void"],
        }

    schema = merge_void_partitions(_empty_schema(), partitions)

    if not compact:
        class_uris = _table_uris(schema["classes"])
        predicate_uris = _table_uris(schema["predicates"])
        details = await asyncio.gather(
            void_metadata.fetch_observed_edges(
                shortname,
                class_uris=class_uris,
                predicate_uris=predicate_uris,
            ),
            void_metadata.fetch_value_shapes(shortname),
            return_exceptions=True,
        )
        for outcome in details:
            if isinstance(outcome, BaseException):
                raise outcome
        edge_rows, value_rows = details
        schema["observed_edges"] = _observed_edges_table(edge_rows)
        schema["value_shapes"] = _value_shapes_table(value_rows)

    return {
        "shortname": shortname,
        "schema": schema,
        "schema_sources": ["okn-void"],
    }


# ── Mermaid class-diagram generation ─────────────────────────────────────────


def _local_name(uri: str) -> str:
    """Return the last path/fragment segment of a URI."""
    return re.split(r"[/#]", uri.rstrip("/#"))[-1] if uri else uri


def _mermaid_id(name: str) -> str:
    """Sanitize a label or URI into a Mermaid-safe class identifier."""
    if name.startswith(("http://", "https://")):
        name = _local_name(name)
    ident = re.sub(r"\W+", "_", name or "").strip("_")
    return ident or "Node"


def _member_type(description: str) -> str:
    """Extract a field type from a trailing ``(type)`` in a property description.

    Returns "" when the description has no such marker — we deliberately do NOT
    fall back to the entity ``type`` (which is always "EdgeProperty"/
    "NodeProperty" and useless as a data type).
    """
    m = re.search(r"\(([^()]+)\)[.\s]*$", (description or "").strip())
    if m:
        candidate = m.group(1).strip()
        if candidate and " " not in candidate and len(candidate) <= 20:
            return candidate.lower()
    return ""


def _clean_edge_label(label: str) -> str:
    """Strip characters that would break a Mermaid relationship label."""
    return re.sub(
        r"\s+", " ", (label or "").replace("|", " ").replace("\n", " ")
    ).strip()


def _col(table: dict[str, Any], name: str) -> int | None:
    cols = table.get("columns", [])
    return cols.index(name) if name in cols else None


def _row_value(row: list[Any], idx: int | None) -> str:
    return row[idx] if idx is not None and len(row) > idx and row[idx] else ""


async def infer_curated_edges(
    shortname: str,
    class_uris: list[str],
    pred_uris: list[str],
    limit: int = 400,
) -> list[tuple[str, str, str]]:
    """Infer ``(predicate, domain, range)`` URI triples from declared domain/range.

    Read from the graph's ``rdfs:domain``/``rdfs:range``, restricted to the given
    curated class and predicate URIs.

    This legacy helper is retained for compatibility tests. The public schema
    visualization does not call it because declared endpoints are not observed
    VoID paths. Returns ``[]`` on error or when nothing matches.
    """
    if not class_uris or not pred_uris:
        return []
    graph = named_graph(shortname)
    values_d = " ".join(f"<{u}>" for u in class_uris)
    values_p = " ".join(f"<{u}>" for u in pred_uris)
    query = f"""\
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?p ?d ?r WHERE {{
  GRAPH <{graph}> {{
    ?p rdfs:domain ?d ; rdfs:range ?r .
    VALUES ?p {{ {values_p} }}
    VALUES ?d {{ {values_d} }}
    VALUES ?r {{ {values_d} }}
  }}
}} LIMIT {int(limit)}"""
    try:
        rows = (await run_sparql(query)).get("rows", [])
    except SparqlError:
        return []
    return [
        (r["p"], r["d"], r["r"])
        for r in rows
        if r.get("p") and r.get("d") and r.get("r")
    ]


async def infer_edge_labels(
    shortname: str, schema: dict[str, Any]
) -> list[tuple[str, str, str]]:
    """Return observed VoID edges as label triples for a schema."""
    classes_tbl = schema.get("classes", {})
    predicates_tbl = schema.get("predicates", {})
    class_uris = _table_uris(classes_tbl)
    predicate_uris = _table_uris(predicates_tbl)
    if not class_uris or not predicate_uris:
        return []

    observed = await void_metadata.fetch_observed_edges(
        shortname,
        class_uris=class_uris,
        predicate_uris=predicate_uris,
    )
    observed_schema = {
        **schema,
        "observed_edges": _observed_edges_table(observed),
    }
    return _edge_labels_from_observed_table(observed_schema)


def _edge_labels_from_observed_table(
    schema: dict[str, Any],
) -> list[tuple[str, str, str]]:
    """Map a VoID ``observed_edges`` table to Mermaid label triples."""
    classes_tbl = schema.get("classes", {})
    predicates_tbl = schema.get("predicates", {})
    observed_tbl = schema.get("observed_edges", {})

    class_uri = _col(classes_tbl, "uri")
    class_label = _col(classes_tbl, "label")
    predicate_uri = _col(predicates_tbl, "uri")
    predicate_label = _col(predicates_tbl, "label")
    source_class = _col(observed_tbl, "source_class")
    edge_predicate = _col(observed_tbl, "predicate")
    target_class = _col(observed_tbl, "target_class")

    uri_to_class = {
        _row_value(row, class_uri): (
            _row_value(row, class_label) or _local_name(_row_value(row, class_uri))
        )
        for row in classes_tbl.get("data", [])
        if _row_value(row, class_uri)
    }
    uri_to_predicate = {
        _row_value(row, predicate_uri): (
            _row_value(row, predicate_label)
            or _local_name(_row_value(row, predicate_uri))
        )
        for row in predicates_tbl.get("data", [])
        if _row_value(row, predicate_uri)
    }

    edges: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in observed_tbl.get("data", []):
        src = uri_to_class.get(_row_value(row, source_class))
        label = uri_to_predicate.get(_row_value(row, edge_predicate))
        tgt = uri_to_class.get(_row_value(row, target_class))
        if not (src and tgt and label):
            continue
        key = (src, label, tgt)
        if key not in seen:
            seen.add(key)
            edges.append(key)
    return edges


def build_mermaid_diagram(
    shortname: str,
    schema: dict[str, Any],
    inferred_edges: list[tuple[str, str, str]] | None = None,
) -> str:
    """Render a KG's schema as a Mermaid ``classDiagram`` (deterministic).

    Node classes become class boxes (with node properties as members), edge
    predicates with source/target metadata become labeled arrows, and predicates
    carrying edge properties become intermediary classes with typed fields
    wired ``source --> edge --> target``. ``inferred_edges`` (optional
    ``(source_label, predicate_label, target_label)`` triples recovered from VoID
    observed paths) are drawn as labeled arrows. Predicates without observed
    object-class paths are listed as ``%%`` comments rather than guessed at.
    """
    classes_tbl = schema.get("classes", {})
    predicates_tbl = schema.get("predicates", {})
    node_props_tbl = schema.get("node_properties", {})
    edge_properties = schema.get("edge_properties", {}) or {}

    declared: dict[str, list[str]] = {}  # class id -> member lines (insertion order)
    relationships: list[str] = []
    undrawn: list[str] = []
    edge_class_ids: list[str] = []  # intermediary classes (styled distinctly)

    def ensure_class(label: str) -> str:
        cid = _mermaid_id(label)
        declared.setdefault(cid, [])
        return cid

    # Node classes (column layout: [uri, label, ...] for metadata, [uri] for probe).
    cls_cols = classes_tbl.get("columns", [])
    label_idx = cls_cols.index("label") if "label" in cls_cols else None
    for row in classes_tbl.get("data", []):
        if not row:
            continue
        label = row[label_idx] if label_idx is not None and len(row) > label_idx else ""
        ensure_class(label or _local_name(row[0]))

    # Node properties become members of their owning class.
    np_cols = node_props_tbl.get("columns", [])
    np_label = np_cols.index("label") if "label" in np_cols else None
    np_desc = np_cols.index("description") if "description" in np_cols else None
    np_class = np_cols.index("class") if "class" in np_cols else None
    for row in node_props_tbl.get("data", []):
        if not row or np_label is None or np_class is None:
            continue
        owner = row[np_class] if len(row) > np_class else ""
        name = row[np_label] if len(row) > np_label else ""
        if not owner or not name:
            continue
        cid = ensure_class(owner)
        desc = row[np_desc] if np_desc is not None and len(row) > np_desc else ""
        member = f"{_member_type(desc)} {_mermaid_id(name)}".strip()
        if member not in declared[cid]:
            declared[cid].append(member)

    # Edge predicates with properties → intermediary classes.
    for rel_label, info in edge_properties.items():
        edge_id = _mermaid_id(rel_label)
        members = []
        for prop in info.get("properties", []):
            mtype = _member_type(prop.get("description", ""))
            member = f"{mtype} {_mermaid_id(prop.get('label', ''))}".strip()
            if member and member not in members:
                members.append(member)
        declared[edge_id] = members
        if edge_id not in edge_class_ids:
            edge_class_ids.append(edge_id)
        src, tgt = info.get("source_class", ""), info.get("target_class", "")
        if src:
            relationships.append(f"  {ensure_class(src)} --> {edge_id}")
        if tgt:
            relationships.append(f"  {edge_id} --> {ensure_class(tgt)}")

    # Observed VoID object-class paths. Their predicate labels are excluded from
    # the "undrawn" list.
    inferred_labels: set[str] = set()
    for src, pred, tgt in inferred_edges or []:
        relationships.append(
            f"  {ensure_class(src)} --> {ensure_class(tgt)} : {_clean_edge_label(pred)}"
        )
        inferred_labels.add(pred)

    # Plain predicates (no edge properties) with source/target → labeled arrows.
    pred_cols = predicates_tbl.get("columns", [])
    p_label = pred_cols.index("label") if "label" in pred_cols else None
    p_src = pred_cols.index("source_class") if "source_class" in pred_cols else None
    p_tgt = pred_cols.index("target_class") if "target_class" in pred_cols else None
    p_has = (
        pred_cols.index("has_edge_properties")
        if "has_edge_properties" in pred_cols
        else None
    )
    for row in predicates_tbl.get("data", []):
        if not row:
            continue
        if p_has is not None and len(row) > p_has and row[p_has]:
            continue  # already drawn as an intermediary class
        label = row[p_label] if p_label is not None and len(row) > p_label else ""
        label = label or _local_name(row[0])
        src = row[p_src] if p_src is not None and len(row) > p_src else ""
        tgt = row[p_tgt] if p_tgt is not None and len(row) > p_tgt else ""
        if src and tgt:
            relationships.append(
                f"  {ensure_class(src)} --> {ensure_class(tgt)} : {_clean_edge_label(label)}"
            )
        elif label not in inferred_labels:
            undrawn.append(_clean_edge_label(label))

    lines = ["classDiagram", "  direction TB"]
    for cid, members in declared.items():
        if members:
            lines.append(f"  class {cid} {{")
            lines += [f"    {m}" for m in members]
            lines.append("  }")
        else:
            lines.append(f"  class {cid}")
    lines += relationships

    node_class_ids = [cid for cid in declared if cid not in edge_class_ids]

    # Legend: one labelled box per class type actually present in the diagram.
    legend: list[tuple[str, str, str]] = []  # (class id, label, style)
    if declared:
        legend.append(("LegendNodeClass", "Node class", _NODE_CLASS_STYLE))
        if edge_class_ids:
            legend.append(
                ("LegendEdgeClass", "Edge (relationship) class", _EDGE_CLASS_STYLE)
            )
    if legend:
        lines.append("  %% Legend")
        lines += [f'  class {lid}["{label}"]' for lid, label, _ in legend]

    # Styling: node classes light blue, edge classes orange (per-class `style`
    # is the form that actually renders fills in classDiagram).
    lines += [f"  style {cid} {_NODE_CLASS_STYLE}" for cid in node_class_ids]
    lines += [f"  style {cid} {_EDGE_CLASS_STYLE}" for cid in edge_class_ids]
    lines += [f"  style {lid} {style}" for lid, _, style in legend]

    if undrawn:
        lines.append("  %% Predicates without source/target metadata (not drawn):")
        lines += [f"  %%   - {p}" for p in undrawn]

    return "\n".join(lines)


async def visualize_schema(shortname: str) -> dict[str, Any]:
    """Build a Mermaid ``classDiagram`` from observed VoID schema paths.

    Returns ``{"shortname", "mermaid"}`` on success, or ``{"shortname",
    "error"}`` when the KG has no observed VoID schema.
    """
    result = await get_schema(shortname, compact=False)
    if "error" in result:
        return {"shortname": shortname, "error": result["error"]}
    schema = result["schema"]
    observed_edges = _edge_labels_from_observed_table(schema)
    diagram = build_mermaid_diagram(
        shortname,
        schema,
        inferred_edges=observed_edges,
    )
    return {"shortname": shortname, "mermaid": diagram}

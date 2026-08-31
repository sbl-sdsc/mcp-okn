"""Per-KG provenance and observed schema statistics from ``okn-void``.

The Proto-OKN meta-graph ``okn-void`` records, for each loaded KG, a small set of
provenance facts on a subject IRI that IS the KG's federation named graph
(``https://purl.org/okn/frink/kg/{shortname}``):

  * ``pav:version``        — the release string, e.g. ``"v0.0.5"``;
  * ``pav:lastUpdatedOn``  — an ISO-8601 timestamp of the last load.

(The graph also carries a coarse ``dcterms:modified`` ``"Mon YYYY"`` month stamp,
but we surface the exact ``pav:lastUpdatedOn`` timestamp instead.)

The same graph also carries VoID class/property partitions and VoID-ext nested
partitions. Those describe what is OBSERVED in each loaded graph:

* classes and their entity counts;
* properties and their triple counts;
* source-class -> property -> target-class paths and their triple counts;
* datatypes and languages used by literal-valued properties.

This module queries those live from the federation and parses them into plain
dicts. It is the data layer behind ``get_kg_version``, ``describe_kg`` profiles,
and the authoritative topology used by ``get_schema`` / ``visualize_schema``.
"""

from __future__ import annotations

from typing import Any

import httpx

from .registry import EXCLUDED_KGS
from .sparql import named_graph, run_sparql

#: The meta-graph holding the VoID provenance for every loaded KG.
OKN_VOID_GRAPH = named_graph("okn-void")

#: VoID and VoID-ext predicates used by the profile/schema queries.
VOID = "http://rdfs.org/ns/void#"
VOID_EXT = "http://ldf.fi/void-ext#"

#: Provenance predicates (see module docstring).
PAV_VERSION = "http://purl.org/pav/version"
PAV_LAST_UPDATED_ON = "http://purl.org/pav/lastUpdatedOn"

#: Subject IRIs are the federation named graphs; strip this to recover a shortname.
_GRAPH_IRI_PREFIX = "https://purl.org/okn/frink/kg/"


def _shortname_from_iri(iri: str) -> str:
    """Recover a KG shortname from its named-graph subject IRI."""
    return iri.removeprefix(_GRAPH_IRI_PREFIX)


def _version_query(shortname: str | None) -> str:
    """A SPARQL query for one KG's (or every KG's) VoID provenance.

    Anchors on ``pav:version`` (present for every KG that records provenance) and
    left-joins the last-updated timestamp, which a KG may omit.
    """
    subject = f"<{named_graph(shortname)}>" if shortname else "?s"
    # For a single KG the subject is a fixed IRI, so bind it back into ?s to keep
    # the result shape identical to the all-KGs scan.
    bind_line = f"\n    BIND({subject} AS ?s)" if shortname else ""
    return f"""\
SELECT ?s ?version ?last_updated WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    {subject} <{PAV_VERSION}> ?version .
    OPTIONAL {{ {subject} <{PAV_LAST_UPDATED_ON}> ?last_updated }}{bind_line}
  }}
}}
ORDER BY ?s"""


def _profile_query(shortname: str) -> str:
    """A compact dataset profile for one KG.

    Counts the top-level class/property partitions separately so their Cartesian
    product cannot inflate either count.
    """
    dataset = named_graph(shortname)
    return f"""\
SELECT ?version ?last_updated ?triples ?properties ?class_count ?predicate_count WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    OPTIONAL {{ <{dataset}> <{PAV_VERSION}> ?version }}
    OPTIONAL {{ <{dataset}> <{PAV_LAST_UPDATED_ON}> ?last_updated }}
    OPTIONAL {{ <{dataset}> <{VOID}triples> ?triples }}
    OPTIONAL {{ <{dataset}> <{VOID}properties> ?properties }}
    {{
      SELECT (COUNT(DISTINCT ?class_partition) AS ?class_count) WHERE {{
        <{dataset}> <{VOID}classPartition> ?class_partition .
      }}
    }}
    {{
      SELECT (COUNT(DISTINCT ?property_partition) AS ?predicate_count) WHERE {{
        <{dataset}> <{VOID}propertyPartition> ?property_partition .
      }}
    }}
  }}
}}"""


def _schema_partitions_query(shortname: str) -> str:
    """Observed classes/properties and their counts for one KG."""
    dataset = named_graph(shortname)
    return f"""\
SELECT ?kind ?uri ?count WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    {{
      <{dataset}> <{VOID}classPartition> ?partition .
      ?partition <{VOID}class> ?uri ;
                 <{VOID}entities> ?count .
      BIND("class" AS ?kind)
    }}
    UNION
    {{
      <{dataset}> <{VOID}propertyPartition> ?partition .
      ?partition <{VOID}property> ?uri ;
                 <{VOID}triples> ?count .
      BIND("predicate" AS ?kind)
    }}
  }}
}}
ORDER BY ?kind ?uri"""


def _values(variable: str, uris: list[str] | None) -> str:
    """Render an optional SPARQL ``VALUES`` restriction."""
    if not uris:
        return ""
    values = " ".join(f"<{uri}>" for uri in dict.fromkeys(uris))
    return f"\n    VALUES ?{variable} {{ {values} }}"


def _observed_edges_query(
    shortname: str,
    class_uris: list[str] | None = None,
    predicate_uris: list[str] | None = None,
    limit: int = 400,
) -> str:
    """Observed source-class/property/target-class paths for one KG."""
    dataset = named_graph(shortname)
    class_values = _values("source_class", class_uris)
    target_values = _values("target_class", class_uris)
    predicate_values = _values("predicate", predicate_uris)
    return f"""\
SELECT ?source_class ?predicate ?target_class
       (SUM(?partition_triples) AS ?triple_count)
WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    <{dataset}> <{VOID}classPartition> ?class_partition .
    ?class_partition <{VOID}class> ?source_class ;
                     <{VOID}propertyPartition> ?property_partition .
    ?property_partition <{VOID}property> ?predicate ;
                        <{VOID_EXT}objectClassPartition> ?object_partition .
    ?object_partition <{VOID}class> ?target_class ;
                      <{VOID}triples> ?partition_triples .{class_values}{predicate_values}{target_values}
  }}
}}
GROUP BY ?source_class ?predicate ?target_class
ORDER BY DESC(?triple_count) ?source_class ?predicate ?target_class
LIMIT {int(limit)}"""


def _value_shapes_query(shortname: str, limit: int = 400) -> str:
    """Observed datatype/language partitions for one KG's properties."""
    dataset = named_graph(shortname)
    return f"""\
SELECT ?predicate ?kind ?value (SUM(?partition_triples) AS ?triple_count) WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    <{dataset}> <{VOID}classPartition> ?class_partition .
    ?class_partition <{VOID}propertyPartition> ?property_partition .
    ?property_partition <{VOID}property> ?predicate .
    {{
      ?property_partition <{VOID_EXT}datatypePartition> ?partition .
      ?partition <{VOID_EXT}datatype> ?value ;
                 <{VOID}triples> ?partition_triples .
      BIND("datatype" AS ?kind)
    }}
    UNION
    {{
      ?property_partition <{VOID_EXT}languagePartition> ?partition .
      ?partition <{VOID_EXT}language> ?value ;
                 <{VOID}triples> ?partition_triples .
      BIND("language" AS ?kind)
    }}
  }}
}}
GROUP BY ?predicate ?kind ?value
ORDER BY ?predicate ?kind DESC(?triple_count)
LIMIT {int(limit)}"""


def _row_to_record(row: dict[str, Any]) -> dict[str, Any]:
    """Project one result row to a provenance record.

    Keys: ``{shortname, version, last_updated, named_graph}``.
    """
    iri = row.get("s", "")
    return {
        "shortname": _shortname_from_iri(iri),
        "version": row.get("version"),
        "last_updated": row.get("last_updated"),
        "named_graph": iri,
    }


async def fetch_profile(
    shortname: str,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any] | None:
    """Fetch one KG's compact VoID dataset profile.

    Returns ``None`` when the graph has no VoID record. Zero partition counts alone
    do not count as a record; at least one root statistic/provenance value must be
    present.
    """
    result = await run_sparql(_profile_query(shortname), client=client)
    rows = result.get("rows", [])
    if not rows:
        return None
    row = rows[0]
    meaningful = ("version", "last_updated", "triples", "properties")
    if not any(row.get(key) is not None for key in meaningful):
        return None
    return {
        "shortname": shortname,
        "named_graph": named_graph(shortname),
        "version": row.get("version"),
        "last_updated": row.get("last_updated"),
        "triple_count": row.get("triples"),
        "property_count": row.get("properties"),
        "class_count": row.get("class_count", 0),
        "predicate_count": row.get("predicate_count", 0),
    }


async def fetch_schema_partitions(
    shortname: str,
    client: httpx.AsyncClient | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Fetch observed class/property partitions for one KG."""
    result = await run_sparql(_schema_partitions_query(shortname), client=client)
    classes: list[dict[str, Any]] = []
    predicates: list[dict[str, Any]] = []
    for row in result.get("rows", []):
        uri = row.get("uri")
        if not uri:
            continue
        item = {"uri": uri}
        if row.get("kind") == "class":
            item["entity_count"] = row.get("count")
            classes.append(item)
        elif row.get("kind") == "predicate":
            item["triple_count"] = row.get("count")
            predicates.append(item)
    return {"classes": classes, "predicates": predicates}


async def fetch_observed_edges(
    shortname: str,
    class_uris: list[str] | None = None,
    predicate_uris: list[str] | None = None,
    limit: int = 400,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Fetch observed source-class/property/target-class paths for one KG."""
    result = await run_sparql(
        _observed_edges_query(
            shortname,
            class_uris=class_uris,
            predicate_uris=predicate_uris,
            limit=limit,
        ),
        client=client,
    )
    return [
        {
            "source_class": row["source_class"],
            "predicate": row["predicate"],
            "target_class": row["target_class"],
            "triple_count": row.get("triple_count"),
        }
        for row in result.get("rows", [])
        if row.get("source_class") and row.get("predicate") and row.get("target_class")
    ]


async def fetch_value_shapes(
    shortname: str,
    limit: int = 400,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Fetch observed datatype/language partitions for one KG."""
    result = await run_sparql(
        _value_shapes_query(shortname, limit=limit), client=client
    )
    return [
        {
            "predicate": row["predicate"],
            "kind": row["kind"],
            "value": row["value"],
            "triple_count": row.get("triple_count"),
        }
        for row in result.get("rows", [])
        if row.get("predicate") and row.get("kind") and row.get("value")
    ]


async def fetch_versions(
    shortname: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Fetch VoID provenance records, one per KG that records it.

    With ``shortname`` set, returns 0 or 1 records for that KG; otherwise every
    KG's, sorted by shortname. Excluded KGs (see ``registry.EXCLUDED_KGS``) are
    filtered out.
    """
    result = await run_sparql(_version_query(shortname), client=client)
    records = [_row_to_record(r) for r in result.get("rows", [])]
    records = [r for r in records if r["shortname"] not in EXCLUDED_KGS]
    records.sort(key=lambda r: r["shortname"])
    return records

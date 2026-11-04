"""Build a per-KG schema table from the ``okn-void`` VoID descriptions.

``get_schema`` reads these tables from ``metadata/void_entities``, which ships with
the server. Their structure — every class, predicate and
(source class, predicate, target) edge, with exact counts — comes from the
precomputed VoID statistics the federation publishes, or, for a KG whose VoID
describes a different release than the one served, from the same statistics
counted on the live graph (:func:`introspect_partitions`). Nothing structural comes
from the legacy curated ``sbl-sdsc/mcp-proto-okn`` files.

VoID layout in ``okn-void`` (one graph for every KG; partition IRIs embed the KG
shortname)::

    <…/kg/{kg}> void:classPartition ?cp .
    ?cp void:class ?cls ; void:entities ?n ; void:propertyPartition ?pp .
    ?pp void:property ?p ; void:triples ?n ;
        void-ext:objectClassPartition [ void:class ?target ; void:triples ?n ] ;
        void-ext:datatypePartition   [ void-ext:datatype ?dt ; void:triples ?n ] .

Three things VoID cannot supply are filled by small live queries against the KG:

* **Reified edge properties.** VoID lists them only as properties of the reifying
  class (``rdf:Statement``), never split by the ``rdf:predicate`` they qualify.
* **OWL axiom properties.** In an OWL ontology most relations appear only inside
  class axioms (``?r owl:onProperty ex:has-part``) or as bare declarations, never as
  the predicate of a triple, so VoID shows one ``owl:onProperty`` partition and no
  row for the relations themselves (bio101: 22 of 382 curated predicates).
* **Labels and descriptions.** VoID carries none. They come from the KG's own named
  graph, then ubergraph for OBO IRIs (tagged ``(source: … via ubergraph)``), then
  the IRI's local name; the build then fills the rest (:mod:`mcp_okn.void_text`).
"""

from __future__ import annotations

import asyncio
import csv
import re
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .registry import EXCLUDED_KGS
from .schema import _is_provenance_uri, _local_name
from .sparql import SparqlError, named_graph, run_sparql
from .void import OKN_VOID_GRAPH

#: Output columns, in order.
COLUMNS = [
    "URI",
    "Label",
    "Description",
    "Type",
    "EdgePropertyOf",
    "SourceClass",
    "TargetClass",
    "Triples",
    "Pattern",
]

#: Per-KG schema metadata that is not domain schema, left out of the files.
#: spoke-genelab describes its own schema in-graph: 9 ``MetaNode`` instances (one
#: per node type, carrying sample property values) linked by 9 reified
#: ``MetaRelationship`` statements (one per edge type, with sample edge values).
#: Excluding a class drops its Class row and every row with it as source or target;
#: excluding a predicate drops its rows and its edge properties, and subtracts its
#: statements from the ``rdf:Statement`` / ``rdf:predicate`` counts.
_SG_SCHEMA = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"
EXCLUDED_SCHEMA_CLASSES: dict[str, frozenset[str]] = {
    "spoke-genelab": frozenset({_SG_SCHEMA + "MetaNode"}),
}
EXCLUDED_SCHEMA_PREDICATES: dict[str, frozenset[str]] = {
    "spoke-genelab": frozenset({_SG_SCHEMA + "MetaRelationship"}),
}

#: How a predicate is stored, which decides the query shape (``Pattern`` column):
#: ``direct`` asserted triples (``?s <p> ?o``); ``reified`` the subject of
#: ``rdf:Statement``s with ``rdf:predicate <p>`` (edge properties hang off them);
#: ``axiom`` only as ``owl:onProperty`` of OWL restrictions; ``declared`` declared
#: and used nowhere. Several are joined with ``;`` in this order (spoke-genelab's
#: expression edge is ``direct;reified``). Class and edge-property rows carry none.
PATTERNS = ("direct", "reified", "axiom", "declared")

VOID = "http://rdfs.org/ns/void#"
VOID_EXT = "http://ldf.fi/void-ext#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDF_TYPE = RDF + "type"
RDF_PREDICATE = RDF + "predicate"
RDF_STATEMENT = RDF + "Statement"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
OWL = "http://www.w3.org/2002/07/owl#"
OWL_ON_PROPERTY = OWL + "onProperty"
#: Declaration types whose instances are schema predicates.
OWL_PROPERTY_TYPES = (
    OWL + "ObjectProperty",
    OWL + "DatatypeProperty",
    OWL + "AnnotationProperty",
)
#: The reification scaffolding itself — never an edge property.
REIFICATION_PROPERTIES = frozenset(
    {RDF + "subject", RDF_PREDICATE, RDF + "object", RDF_TYPE}
)

_KG_PREFIX = "https://purl.org/okn/frink/kg/"
_OBO_PREFIX = "http://purl.obolibrary.org/obo/"
_DATATYPE_PREFIXES = ("http://www.w3.org/2001/XMLSchema#", RDF)

#: Text predicates, in preference order (proto-okn's extract_entities.py order, plus
#: the OBO definition annotation).
LABEL_PREDICATES = ("http://www.w3.org/2000/01/rdf-schema#label",)
DESCRIPTION_PREDICATES = (
    "http://www.w3.org/2000/01/rdf-schema#comment",
    "http://www.w3.org/2004/02/skos/core#definition",
    "http://purl.org/dc/terms/description",
    "http://purl.org/dc/elements/1.1/description",
    "http://purl.obolibrary.org/obo/IAO_0000115",
    # bio101 (AURA) carries its definitions here and nowhere else.
    "http://www.projecthalo.com/aura#user-description",
    # Industrial Ontologies Foundry annotations: SUDOKN (and the IOF ontologies it
    # builds on) define terms with these; the okn-registry entry declares iof-av.
    "https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/"
    "naturalLanguageDefinition",
    # Non-standard, but sudokn's own definition of GrindingCapability uses it.
    "http://www.w3.org/2000/01/rdf-schema#definition",
    "https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/"
    "explanatoryNote",
)

#: URIs per ``VALUES`` block in a text lookup.
TEXT_BATCH = 25
#: Timeout for the one heavy query (exact edge-property counts over every statement).
EDGE_COUNT_TIMEOUT = 300.0
#: Timeout for one live-introspection partition query (one property, one kind).
INTROSPECT_TIMEOUT = 900.0
#: Pause before retrying a per-class introspection query (endpoint memory pressure).
INTROSPECT_RETRY_S = 30.0
#: Statements sampled per reified predicate when the exact count times out.
EDGE_SAMPLE_LIMIT = 1000
#: Objects sampled to name a (property, class) datatype the exact split cannot count.
DATATYPE_SAMPLE_LIMIT = 10000
#: Retries of one builder query whose connection dropped (an httpx transport error).
TRANSPORT_RETRIES = 2

Log = Callable[[str], None]


@dataclass
class SchemaRow:
    """One output row. ``triples`` is None when no exact count is available."""

    uri: str
    type: str
    label: str = ""
    description: str = ""
    edge_property_of: str = ""
    source_class: str = ""
    target_class: str = ""
    triples: int | None = None
    #: Data-derived usage text appended to the description (not a CSV column).
    note: str = ""
    #: :data:`PATTERNS` values, ``;``-joined.
    pattern: str = ""

    def as_record(self) -> list[str]:
        """The row as CSV cells, in :data:`COLUMNS` order."""
        return [
            self.uri,
            self.label,
            self.description,
            self.type,
            self.edge_property_of,
            self.source_class,
            self.target_class,
            "" if self.triples is None else str(self.triples),
            self.pattern,
        ]


def kg_iri(kg: str) -> str:
    """The KG's federation named graph — also its VoID dataset IRI."""
    return named_graph(kg)


def is_datatype(uri: str) -> bool:
    """True for a literal datatype IRI (xsd:*, rdf:langString, …), not a class."""
    return uri.startswith(_DATATYPE_PREFIXES)


def _clean(text: str) -> str:
    """Collapse whitespace and drop control characters (as proto-okn does)."""
    return re.sub(r"\s+", " ", re.sub(r"[\x00-\x1f\x7f]", " ", text)).strip()


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


async def _run(query: str, **kw: Any) -> dict[str, Any]:
    """:func:`run_sparql` with the IRIs left exactly as the graph stores them.

    run_sparql rewrites ``<https://schema.org/…>`` to ``http`` for hand-written
    queries; the builder queries IRIs it read from the data, and several KGs store
    the https form (phaseskg's schema:alternateName matched nothing before this).

    A dropped connection (an httpx transport error, which run_sparql does not turn
    into a SparqlError) is retried and then raised as a SparqlError, so one reset
    socket degrades a single partition instead of aborting an hours-long build
    (medical-device-kg, 2026-11-04: a bare ``httpx`` error after ~4 h wrote nothing).
    """
    for attempt in range(TRANSPORT_RETRIES + 1):
        try:
            return await run_sparql(query, normalize_schema=False, **kw)
        except httpx.TransportError as exc:
            if attempt == TRANSPORT_RETRIES:
                raise SparqlError(
                    f"connection failed {attempt + 1} times: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            await asyncio.sleep(INTROSPECT_RETRY_S)
    raise AssertionError("unreachable")


# --------------------------------------------------------------------------- queries


def datasets_query() -> str:
    """Every KG with a VoID description.

    Partition nodes are ALSO typed ``void:Dataset``, so keep only IRIs of the exact
    ``…/kg/{shortname}`` form.
    """
    return f"""\
PREFIX void: <{VOID}>
SELECT ?ds WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    ?ds a void:Dataset .
    FILTER(REGEX(STR(?ds), "^{_KG_PREFIX}[^/]+$"))
  }}
}}"""


def edge_partition_counts_query() -> str:
    """Object-class partition count per KG — the size of its per-edge table."""
    return f"""\
PREFIX void-ext: <{VOID_EXT}>
SELECT ?kg (COUNT(*) AS ?n) WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    ?pp void-ext:objectClassPartition ?ocp .
    BIND(STRBEFORE(STRAFTER(STR(?pp), "{_KG_PREFIX}"), "/") AS ?kg)
  }}
}}
GROUP BY ?kg"""


def class_partitions_query(kg: str) -> str:
    """Every class partition of a KG with its instance count."""
    return f"""\
PREFIX void: <{VOID}>
SELECT ?cls ?entities WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    <{kg_iri(kg)}> void:classPartition ?cp .
    ?cp void:class ?cls .
    OPTIONAL {{ ?cp void:entities ?entities }}
  }}
}}"""


def property_partitions_query(kg: str) -> str:
    """Every class→property partition with its total, object-class and datatype splits.

    ``?kind`` is ``total`` (the property partition itself), ``class`` (an object
    class partition; ``?target`` = class) or ``datatype`` (``?target`` = datatype).
    """
    return f"""\
PREFIX void: <{VOID}>
PREFIX void-ext: <{VOID_EXT}>
SELECT ?cls ?prop ?kind ?target ?n WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    <{kg_iri(kg)}> void:classPartition ?cp .
    ?cp void:class ?cls ; void:propertyPartition ?pp .
    ?pp void:property ?prop .
    {{ ?pp void:triples ?n . BIND("total" AS ?kind) }}
    UNION
    {{ ?pp void-ext:objectClassPartition ?x . ?x void:class ?target ; void:triples ?n .
       BIND("class" AS ?kind) }}
    UNION
    {{ ?pp void-ext:datatypePartition ?x . ?x void-ext:datatype ?target ; void:triples ?n .
       BIND("datatype" AS ?kind) }}
  }}
}}"""


def dataset_properties_query(kg: str) -> str:
    """Dataset-level property partitions: the per-predicate totals."""
    return f"""\
PREFIX void: <{VOID}>
SELECT ?prop ?n WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    <{kg_iri(kg)}> void:propertyPartition ?pp .
    ?pp void:property ?prop .
    OPTIONAL {{ ?pp void:triples ?n }}
  }}
}}"""


def void_summary_query(kg: str) -> str:
    """VoID's own whole-KG triple count and the release it describes."""
    return f"""\
PREFIX void: <{VOID}>
PREFIX pav: <http://purl.org/pav/>
SELECT ?triples ?version ?updated WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    <{kg_iri(kg)}> void:triples ?triples .
    OPTIONAL {{ <{kg_iri(kg)}> pav:version ?version }}
    OPTIONAL {{ <{kg_iri(kg)}> pav:lastUpdatedOn ?updated }}
  }}
}}"""


def served_triples_query(kg: str) -> str:
    """The served graph's actual triple count (slow on the largest KGs: ~100 s)."""
    return f"SELECT (COUNT(*) AS ?n) WHERE {{ GRAPH <{kg_iri(kg)}> {{ ?s ?p ?o }} }}"


def reified_predicates_query(kg: str) -> str:
    """Each predicate used as an ``rdf:predicate`` value, with its statement count."""
    return f"""\
PREFIX rdf: <{RDF}>
SELECT ?pred (COUNT(*) AS ?n) WHERE {{
  GRAPH <{kg_iri(kg)}> {{ ?st rdf:predicate ?pred }}
}}
GROUP BY ?pred"""


def edge_property_counts_query(kg: str) -> str:
    """Exact triple count per (reified predicate, property). Heavy on big KGs."""
    return f"""\
PREFIX rdf: <{RDF}>
SELECT ?pred ?prop (COUNT(*) AS ?n) WHERE {{
  GRAPH <{kg_iri(kg)}> {{ ?st rdf:predicate ?pred ; ?prop ?o }}
}}
GROUP BY ?pred ?prop"""


def edge_property_sample_query(
    kg: str, pred: str, limit: int = EDGE_SAMPLE_LIMIT
) -> str:
    """Properties seen on a sample of one reified predicate's statements."""
    return f"""\
PREFIX rdf: <{RDF}>
SELECT DISTINCT ?prop WHERE {{
  GRAPH <{kg_iri(kg)}> {{
    {{ SELECT ?st WHERE {{ ?st rdf:predicate <{pred}> }} LIMIT {limit} }}
    ?st ?prop ?o .
  }}
}}"""


def reified_endpoints_query(kg: str, pred: str) -> str:
    """Source/target classes of a predicate that exists only in reified form."""
    return f"""\
PREFIX rdf: <{RDF}>
SELECT ?sc ?oc (COUNT(DISTINCT ?st) AS ?n) WHERE {{
  GRAPH <{kg_iri(kg)}> {{
    ?st rdf:predicate <{pred}> ; rdf:subject ?s ; rdf:object ?o .
    ?s a ?sc .
    ?o a ?oc .
  }}
}}
GROUP BY ?sc ?oc"""


def axiom_properties_query(kg: str) -> str:
    """Each property used as an ``owl:onProperty`` value, with its restriction count."""
    return f"""\
PREFIX owl: <{OWL}>
SELECT ?prop (COUNT(?r) AS ?n) WHERE {{
  GRAPH <{kg_iri(kg)}> {{ ?r owl:onProperty ?prop . FILTER(isIRI(?prop)) }}
}}
GROUP BY ?prop"""


def declared_properties_query(kg: str) -> str:
    """Declared object/datatype/annotation properties with named domain and range."""
    kinds = " ".join(f"<{t}>" for t in OWL_PROPERTY_TYPES)
    return f"""\
PREFIX rdfs: <{RDFS}>
SELECT DISTINCT ?prop ?domain ?range WHERE {{
  GRAPH <{kg_iri(kg)}> {{
    VALUES ?kind {{ {kinds} }}
    ?prop a ?kind .
    FILTER(isIRI(?prop))
    OPTIONAL {{ ?prop rdfs:domain ?domain . FILTER(isIRI(?domain)) }}
    OPTIONAL {{ ?prop rdfs:range ?range . FILTER(isIRI(?range)) }}
  }}
}}"""


def graph_classes_query(kg: str) -> str:
    """Live equivalent of the class partitions: instances per class."""
    return f"""\
SELECT ?cls (COUNT(?s) AS ?entities) WHERE {{
  GRAPH <{kg_iri(kg)}> {{ ?s a ?cls }}
}}
GROUP BY ?cls"""


def graph_properties_query(kg: str) -> str:
    """Live equivalent of the dataset-level property partitions."""
    return f"""\
SELECT ?prop (COUNT(*) AS ?n) WHERE {{
  GRAPH <{kg_iri(kg)}> {{ ?s ?prop ?o }}
}}
GROUP BY ?prop"""


def graph_partition_query(kg: str, prop: str, kind: str, cls: str = "") -> str:
    """Live equivalent of one property's class→property partitions.

    ``kind`` is ``total`` (triples whose subject has the class), ``class`` (split
    by the object's class) or ``datatype`` (split by the literal's datatype),
    returned in the same shape as :func:`property_partitions_query`. Checked on
    phaseskg and nestkg (fresh VoID): identical rows except that QLever reports
    integer subtypes such as ``xsd:nonNegativeInteger`` as ``xsd:int``. One property
    and one kind per query keeps each under the endpoint's time and memory limits
    on the largest graphs (spatialkg, ~430M triples).
    """
    pattern = {
        "total": "?s <{p}> ?o . ?s a ?cls .",
        "class": "?s <{p}> ?o . ?s a ?cls . ?o a ?target .",
        # QLever's DATATYPE() is unbound for a language-tagged literal; VoID
        # (and SPARQL 1.1) call that rdf:langString.
        "datatype": "?s <{p}> ?o . FILTER(isLiteral(?o)) ?s a ?cls . "
        f'BIND(IF(LANG(?o) != "", <{RDF}langString>, DATATYPE(?o)) AS ?target)',
    }[kind].format(p=prop)
    if cls:  # one subject class, for a property too big to split in one query
        pattern = f"VALUES ?cls {{ <{cls}> }} {pattern}"
    target = "" if kind == "total" else " ?target"
    return f"""\
SELECT ?cls{target} (COUNT(*) AS ?n) WHERE {{
  GRAPH <{kg_iri(kg)}> {{ {pattern} }}
}}
GROUP BY ?cls{target}"""


def datatype_sample_query(kg: str, prop: str, cls: str) -> str:
    """Datatypes of a sample of ``prop``'s objects on subjects of ``cls``.

    The fallback when the exact datatype split of a huge literal property cannot
    finish (medical-device-kg's MAUDE narratives, ~10^8 literals). IRIs and blank
    nodes come back as ``?kind`` "node" so a mixed property is recognisable.
    """
    return f"""\
SELECT ?target (COUNT(*) AS ?n) WHERE {{
  {{ SELECT ?o WHERE {{
    GRAPH <{kg_iri(kg)}> {{ VALUES ?cls {{ <{cls}> }} ?s <{prop}> ?o . ?s a ?cls . }}
  }} LIMIT {DATATYPE_SAMPLE_LIMIT} }}
  BIND(IF(!isLiteral(?o), "node",
       IF(LANG(?o) != "", <{RDF}langString>, DATATYPE(?o))) AS ?target)
}}
GROUP BY ?target"""


def text_lookup_query(graph: str, uris: Iterable[str]) -> str:
    """English/untagged label and description literals for a batch of URIs."""
    values = " ".join(f"<{u}>" for u in uris)
    preds = " ".join(f"<{p}>" for p in (*LABEL_PREDICATES, *DESCRIPTION_PREDICATES))
    return f"""\
SELECT ?u ?p ?o WHERE {{
  GRAPH <{graph}> {{
    VALUES ?u {{ {values} }}
    VALUES ?p {{ {preds} }}
    ?u ?p ?o .
    FILTER(isLiteral(?o) && (LANG(?o) = "" || LANGMATCHES(LANG(?o), "en")))
  }}
}}"""


# ---------------------------------------------------------------------- row building


def shortnames_from_datasets(rows: Iterable[dict[str, Any]]) -> list[str]:
    """KG shortnames from :func:`datasets_query` rows, minus excluded/meta graphs."""
    names = set()
    for r in rows:
        ds = r.get("ds", "")
        if re.fullmatch(re.escape(_KG_PREFIX) + r"[^/]+", ds):
            names.add(ds.removeprefix(_KG_PREFIX))
    return sorted(n for n in names if n not in EXCLUDED_KGS and n != "okn-void")


def class_rows(bindings: Iterable[dict[str, Any]]) -> list[SchemaRow]:
    """One Class row per class partition; Triples = instance count (void:entities)."""
    out: dict[str, SchemaRow] = {}
    for b in bindings:
        cls = b.get("cls", "")
        if not cls or _is_provenance_uri(cls):
            continue
        n = _int(b.get("entities"))
        row = out.setdefault(cls, SchemaRow(uri=cls, type="Class", triples=n))
        if row.triples is None:
            row.triples = n
    return sorted(out.values(), key=lambda r: r.uri)


@dataclass
class _PropertyPartition:
    total: int | None = None
    classes: dict[str, int] | None = None
    datatypes: dict[str, int] | None = None


def _group_partitions(
    bindings: Iterable[dict[str, Any]],
) -> dict[tuple[str, str], _PropertyPartition]:
    parts: dict[tuple[str, str], _PropertyPartition] = {}
    for b in bindings:
        cls, prop, kind = b.get("cls", ""), b.get("prop", ""), b.get("kind", "")
        if not cls or not prop:
            continue
        part = parts.setdefault(
            (cls, prop), _PropertyPartition(classes={}, datatypes={})
        )
        n = _int(b.get("n"))
        if kind == "total":
            part.total = n
        elif kind == "class" and b.get("target") and n is not None:
            assert part.classes is not None
            part.classes[b["target"]] = n
        elif kind == "datatype" and b.get("target") and n is not None:
            assert part.datatypes is not None
            part.datatypes[b["target"]] = n
    return parts


def predicate_rows(
    partition_bindings: Iterable[dict[str, Any]],
    dataset_properties: Iterable[dict[str, Any]] = (),
) -> list[SchemaRow]:
    """One Predicate row per (source class, predicate, target) VoID edge.

    A property partition whose total exceeds its typed splits (objects that are
    untyped IRIs) gets one extra row with an empty TargetClass carrying the remainder.
    A predicate that appears ONLY at dataset level (its subjects are untyped) gets a
    single row with empty Source/Target and the dataset total.
    """
    rows: list[SchemaRow] = []
    seen_props: set[str] = set()
    for (cls, prop), part in sorted(_group_partitions(partition_bindings).items()):
        seen_props.add(prop)
        if prop == RDF_TYPE or _is_provenance_uri(prop) or _is_provenance_uri(cls):
            continue
        assigned = 0
        for target, n in sorted((part.classes or {}).items()):
            rows.append(
                SchemaRow(
                    prop,
                    "Predicate",
                    source_class=cls,
                    target_class=target,
                    triples=n,
                    pattern="direct",
                )
            )
            assigned += n
        for target, n in sorted((part.datatypes or {}).items()):
            rows.append(
                SchemaRow(
                    prop,
                    "Predicate",
                    source_class=cls,
                    target_class=target,
                    triples=n,
                    pattern="direct",
                )
            )
            assigned += n
        if part.total is not None and part.total > assigned:
            rows.append(
                SchemaRow(
                    prop,
                    "Predicate",
                    source_class=cls,
                    triples=part.total - assigned,
                    pattern="direct",
                )
            )
    for b in dataset_properties:
        prop = b.get("prop", "")
        if (
            not prop
            or prop in seen_props
            or prop == RDF_TYPE
            or _is_provenance_uri(prop)
        ):
            continue
        seen_props.add(prop)
        rows.append(
            SchemaRow(prop, "Predicate", triples=_int(b.get("n")), pattern="direct")
        )
    return rows


def reifying_classes(partition_bindings: Iterable[dict[str, Any]]) -> list[str]:
    """Classes whose instances carry ``rdf:predicate`` — the reified statement nodes."""
    return sorted(
        {
            b["cls"]
            for b in partition_bindings
            if b.get("prop") == RDF_PREDICATE
            and b.get("kind") == "total"
            and b.get("cls")
        }
    )


def _reifying_profile(
    partition_bindings: list[dict[str, Any]], reifiers: list[str]
) -> tuple[dict[str, int], dict[str, str]]:
    """Per property on the reifying classes: VoID total, and its dominant target.

    VoID's datatype/object-class splits for a reifying class are pooled across every
    reified predicate, so a stray minority type (spoke-genelab's 3 ``xsd:string``
    log2fc values, all on ``MetaRelationship``) can't be attributed to a predicate.
    The target is therefore the datatype/class with the most triples.
    """
    totals: dict[str, int] = defaultdict(int)
    target_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for (cls, prop), part in _group_partitions(partition_bindings).items():
        if cls not in reifiers or prop in REIFICATION_PROPERTIES:
            continue
        totals[prop] += part.total or 0
        for target, n in {**(part.datatypes or {}), **(part.classes or {})}.items():
            target_counts[prop][target] += n
    dominant = {
        prop: max(sorted(counts), key=lambda t: counts[t])
        for prop, counts in target_counts.items()
        if counts
    }
    return dict(totals), dominant


def edge_property_rows(
    partition_bindings: list[dict[str, Any]],
    reified: dict[str, int],
    pair_counts: dict[tuple[str, str], int] | None,
    sampled: dict[str, set[str]] | None = None,
) -> tuple[list[SchemaRow], list[str]]:
    """Rows for reified edge properties, plus notes on counts that are unavailable.

    ``reified`` maps each reified predicate to its statement count. Counts come
    from ``pair_counts`` (exact live (pred, prop) counts) when given; with a single
    reified predicate VoID's reifying-class totals are already exact; otherwise
    (``sampled`` props only) a count is filled only for a property that occurs under
    one predicate. SourceClass is the reifying class when there is exactly one, and
    TargetClass the property's dominant VoID target (datatype or class), else empty.
    """
    reifiers = reifying_classes(partition_bindings)
    totals, targets = _reifying_profile(partition_bindings, reifiers)
    source = reifiers[0] if len(reifiers) == 1 else ""
    notes: list[str] = []

    pairs: dict[tuple[str, str], int | None] = {}
    if pair_counts is not None:
        pairs = {
            (pred, prop): n
            for (pred, prop), n in pair_counts.items()
            if pred in reified and prop not in REIFICATION_PROPERTIES
        }
    elif len(reified) == 1:
        (pred,) = reified
        pairs = {(pred, prop): n for prop, n in totals.items()}
    else:
        owners: dict[str, list[str]] = defaultdict(list)
        for pred, props in (sampled or {}).items():
            for prop in props - REIFICATION_PROPERTIES:
                owners[prop].append(pred)
        for prop, preds in owners.items():
            for pred in preds:
                n = totals.get(prop) if len(preds) == 1 else None
                pairs[(pred, prop)] = n
                if n is None:
                    notes.append(f"count unavailable: {prop} on {pred} (sampled)")

    rows = []
    for (pred, prop), n in sorted(pairs.items()):
        if _is_provenance_uri(prop):
            continue
        target = targets.get(prop, "")
        rows.append(
            SchemaRow(
                prop,
                "Predicate",
                edge_property_of=pred,
                source_class=source,
                target_class=target,
                triples=n,
            )
        )
    return rows, notes


def drop_aggregated_edge_rows(
    rows: list[SchemaRow], edge_rows: list[SchemaRow], reifiers: Iterable[str]
) -> list[SchemaRow]:
    """Remove the VoID reifying-class rows that the per-predicate edge rows replace."""
    reifier_set = set(reifiers)
    edge_props = {r.uri for r in edge_rows}
    return [
        r
        for r in rows
        if not (
            r.source_class in reifier_set
            and r.uri in edge_props
            and not r.edge_property_of
        )
    ]


def reified_only_rows(
    pred: str, bindings: list[dict[str, Any]], statements: int
) -> list[SchemaRow]:
    """Predicate rows for a predicate present only as ``rdf:predicate`` values."""
    rows = [
        SchemaRow(
            pred,
            "Predicate",
            source_class=b["sc"],
            target_class=b["oc"],
            triples=_int(b.get("n")),
            pattern="reified",
        )
        for b in bindings
        if b.get("sc") and b.get("oc")
    ]
    return rows or [SchemaRow(pred, "Predicate", triples=statements, pattern="reified")]


def axiom_property_rows(
    axiom_bindings: Iterable[dict[str, Any]],
    declared_bindings: Iterable[dict[str, Any]],
    present: Iterable[str],
) -> list[SchemaRow]:
    """Predicate rows for OWL properties that VoID cannot see.

    A property is covered when it is an ``owl:onProperty`` value or a declared
    :data:`OWL_PROPERTY_TYPES` property but never the predicate of a
    triple (not in ``present``). Its domain and range become Source/Target, Triples is
    0 (no direct triples) and the note says how it is used, since a query that asks
    for ``?s <prop> ?o`` returns nothing.
    """
    axioms = {b["prop"]: _int(b.get("n")) or 0 for b in axiom_bindings if b.get("prop")}
    declared: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for b in declared_bindings:
        if b.get("prop"):
            declared[b["prop"]].add((b.get("domain") or "", b.get("range") or ""))
    skip = set(present) | {RDF_TYPE}
    rows: list[SchemaRow] = []
    for prop in sorted((set(axioms) | set(declared)) - skip):
        if _is_provenance_uri(prop):
            continue
        n = axioms.get(prop, 0)
        note = (
            f"Used only inside class axioms, as owl:onProperty of {n:,} "
            f"owl:Restriction{'s' if n != 1 else ''}; never asserted as a direct triple."
            if n
            else "Declared in the schema but used in no triple or class axiom."
        )
        for domain, rng in sorted(declared.get(prop) or {("", "")}):
            rows.append(
                SchemaRow(
                    prop,
                    "Predicate",
                    source_class=domain,
                    target_class=rng,
                    triples=0,
                    note=note,
                    pattern="axiom" if n else "declared",
                )
            )
    return rows


def add_patterns(
    rows: list[SchemaRow], reified: Iterable[str], axioms: dict[str, int]
) -> None:
    """Mark asserted predicates that are ALSO reified or used in OWL axioms.

    Rows built from VoID partitions are ``direct``; this adds ``reified`` for a
    predicate that also appears as ``rdf:predicate`` and ``axiom`` (with a note on
    the restriction count) for one that is also an ``owl:onProperty`` value.
    """
    reified_set = set(reified)
    for row in rows:
        if row.type != "Predicate" or row.edge_property_of or not row.pattern:
            continue
        found = set(row.pattern.split(";"))
        if row.uri in reified_set:
            found.add("reified")
        n = axioms.get(row.uri, 0)
        if n and "axiom" not in found:
            found.add("axiom")
            row.note = (
                f"Also used inside class axioms, as owl:onProperty of {n:,} "
                f"owl:Restriction{'s' if n != 1 else ''}."
            )
        row.pattern = ";".join(p for p in PATTERNS if p in found)


def drop_excluded(
    rows: list[SchemaRow],
    classes: Iterable[str],
    predicates: Iterable[str],
    reified: dict[str, int],
) -> list[SchemaRow]:
    """Remove excluded metadata classes/predicates (see :data:`EXCLUDED_SCHEMA_CLASSES`).

    Rows are split per (source, target) pair, so dropping the pairs that touch an
    excluded class keeps the other counts exact. An excluded predicate's reified
    statements are subtracted from the ``rdf:Statement`` class count and from the
    target-less ``rdf:predicate`` row, the only rows that pool them.
    """
    cls_set, pred_set = set(classes), set(predicates)
    statements = sum(reified.get(p, 0) for p in pred_set)
    out = []
    for row in rows:
        if row.uri in cls_set and row.type == "Class":
            continue
        if row.source_class in cls_set or row.target_class in cls_set:
            continue
        if row.uri in pred_set or row.edge_property_of in pred_set:
            continue
        if statements and row.triples is not None:
            pooled_class = row.type == "Class" and row.uri == RDF_STATEMENT
            pooled_pred = (
                row.uri == RDF_PREDICATE
                and row.source_class == RDF_STATEMENT
                and not row.target_class
            )
            if pooled_class or pooled_pred:
                row.triples -= statements
        out.append(row)
    return out


# ---------------------------------------------------------------------------- text


def local_label(uri: str) -> str:
    """The fallback label: the IRI's local name, verbatim."""
    return _local_name(uri)


def pick_text(bindings: Iterable[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """``{uri: {"label", "description"}}`` from text-lookup rows, by predicate preference."""
    best: dict[str, dict[str, tuple[int, str]]] = defaultdict(dict)
    for b in bindings:
        u, p, o = b.get("u", ""), b.get("p", ""), _clean(str(b.get("o", "")))
        if not (u and o):
            continue
        for field, order in (
            ("label", LABEL_PREDICATES),
            ("description", DESCRIPTION_PREDICATES),
        ):
            if p in order:
                rank = order.index(p)
                cur = best[u].get(field)
                if cur is None or rank < cur[0] or (rank == cur[0] and o < cur[1]):
                    best[u][field] = (rank, o)
    return {u: {f: v[1] for f, v in fields.items()} for u, fields in best.items()}


def source_tag(source: str) -> str:
    """The suffix marking a description taken from another ontology or graph."""
    return f" (source: {source})"


def obo_ontology(uri: str) -> str:
    """The OBO ontology an IRI belongs to: ``…/obo/GO_0008150`` → ``GO``."""
    local = uri.removeprefix(_OBO_PREFIX)
    return re.split(r"[_#/]", local, maxsplit=1)[0].upper()


def apply_text(
    rows: list[SchemaRow],
    kg_text: dict[str, dict[str, str]],
    ontology_text: dict[str, dict[str, str]] | None = None,
) -> None:
    """Fill Label/Description: the KG's own text, then ubergraph, then the local name.

    A description taken from ubergraph is tagged with its ontology (``(source: GO
    via ubergraph)``): it is not the KG's own text.
    """
    ontology_text = ontology_text or {}
    for row in rows:
        own, onto = kg_text.get(row.uri, {}), ontology_text.get(row.uri, {})
        row.label = row.label or own.get("label", "") or onto.get("label", "")
        if not row.description:
            if own.get("description"):
                row.description = own["description"]
            elif onto.get("description"):
                row.description = onto["description"] + source_tag(
                    f"{obo_ontology(row.uri)} via ubergraph"
                )
        row.label = row.label or local_label(row.uri)
        if row.note and row.note not in row.description:
            row.description = f"{row.description} {row.note}".strip()


async def _lookup_text(
    graph: str, uris: list[str], client: httpx.AsyncClient | None, log: Log
) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for i in range(0, len(uris), TEXT_BATCH):
        batch = uris[i : i + TEXT_BATCH]
        try:
            res = await _run(text_lookup_query(graph, batch), client=client)
        except SparqlError as exc:
            log(f"  text lookup failed for a batch in {graph}: {str(exc)[:120]}")
            continue
        out.update(pick_text(res["rows"]))
    return out


# --------------------------------------------------------------------------- driver


async def fetch_edge_partition_counts(
    client: httpx.AsyncClient | None = None,
) -> dict[str, int]:
    """Object-class partition count per KG (see :func:`edge_partition_counts_query`)."""
    res = await _run(edge_partition_counts_query(), client=client)
    return {r["kg"]: _int(r["n"]) or 0 for r in res["rows"] if r.get("kg")}


async def list_void_kgs(client: httpx.AsyncClient | None = None) -> list[str]:
    """Shortnames of every servable KG with a VoID description."""
    res = await _run(datasets_query(), client=client)
    return shortnames_from_datasets(res["rows"])


#: Largest relative VoID-vs-served triple-count gap at which VoID is still used.
#: The 2026-10-15 small drifts (dreamkg, sawgraph, securechainkg) are under 0.001%;
#: the stale releases (biomarkerkg, nikg, spatialkg) are >1%.
STALE_VOID_TOLERANCE = 0.001


def void_is_stale(freshness: dict[str, Any] | None) -> bool:
    """True when VoID and the served graph differ by more than the tolerance.

    A failed live count (``served_triples`` None) is not proof of staleness: VoID
    is kept. A missing VoID count with a served graph is stale.
    """
    if not freshness:
        return False
    void, served = freshness.get("void_triples"), freshness.get("served_triples")
    if not isinstance(served, int):
        return False
    if not isinstance(void, int) or not void:
        return served > 0
    return bool(abs(void - served) / void > STALE_VOID_TOLERANCE)


async def check_freshness(
    kg: str, client: httpx.AsyncClient | None = None, timeout: float = 300.0
) -> dict[str, Any]:
    """Does the VoID describe the graph actually being served?

    VoID is NOT guaranteed to match the loaded release: on 2026-10-14 biomarkerkg's
    VoID (v0.0.4, 1,820,793 triples) described different predicate IRIs than the
    served graph (1,215,057 triples). Compares VoID's ``void:triples`` with a live
    ``COUNT(*)``; ``served`` is None when that count times out.
    """
    res = await _run(void_summary_query(kg), client=client)
    row = res["rows"][0] if res["rows"] else {}
    out: dict[str, Any] = {
        "void_triples": _int(row.get("triples")),
        "version": row.get("version"),
        "last_updated": row.get("updated"),
        "served_triples": None,
    }
    try:
        res = await _run(served_triples_query(kg), client=client, timeout=timeout)
        out["served_triples"] = _int(res["rows"][0]["n"]) if res["rows"] else None
    except SparqlError as exc:
        out["error"] = str(exc)[:200]
    v, n = out["void_triples"], out["served_triples"]
    out["matches"] = None if v is None or n is None else v == n
    return out


async def introspect_partitions(
    kg: str, client: httpx.AsyncClient | None = None, log: Log = print
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """``(classes, partitions, dataset properties, notes)`` counted from the live graph.

    The same three binding sets the VoID queries return, for a KG whose VoID
    describes a different release than the one served (see :func:`check_freshness`).
    A partition query the endpoint cannot answer whole (spatialkg's S2-cell
    relations need more memory than it has free) is retried one subject class at a
    time, over only the classes the property's total split found; a class that
    still fails is left out and named in ``notes``. A datatype partition that still
    fails is filled from a sample instead when every sampled object is a literal of
    one datatype: the count is then that class's total for the property.
    """
    classes = (await _run(graph_classes_query(kg), client=client))["rows"]
    ds_props = (await _run(graph_properties_query(kg), client=client))["rows"]
    class_iris = sorted(r["cls"] for r in classes if r.get("cls"))
    partitions: list[dict[str, Any]] = []
    notes: list[str] = []
    props = sorted(r["prop"] for r in ds_props if r.get("prop"))
    log(f"  introspecting {len(classes)} classes, {len(props)} properties")

    async def rows(prop: str, kind: str, cls: str = "") -> list[dict[str, Any]]:
        res = await _run(
            graph_partition_query(kg, prop, kind, cls),
            client=client,
            timeout=INTROSPECT_TIMEOUT,
        )
        return [{**r, "prop": prop, "kind": kind} for r in res["rows"] if r.get("cls")]

    async def sampled_datatype(prop: str, cls: str, total: int | None) -> str:
        """Fill one failed datatype partition from a sample; return a note."""
        try:
            res = await _run(
                datatype_sample_query(kg, prop, cls),
                client=client,
                timeout=INTROSPECT_TIMEOUT,
            )
        except SparqlError as exc:
            return f"sample failed too ({str(exc)[:80]}); left out"
        seen = sorted({str(r.get("target") or "") for r in res["rows"]})
        if total is None:
            return "no class total to scale a sample by; left out"
        if len(seen) != 1 or seen[0] in ("", "node"):
            return f"sample is not one literal datatype ({seen}); left out"
        dt = seen[0]
        partitions.append(
            {"cls": cls, "target": dt, "n": total, "prop": prop, "kind": "datatype"}
        )
        return f"datatype {dt} from a {DATATYPE_SAMPLE_LIMIT:,}-object sample"

    for prop in props:
        totals: dict[str, int | None] | None = None  # subject classes carrying prop
        for kind in ("total", "class", "datatype"):
            try:
                found = await rows(prop, kind)
                partitions.extend(found)
                if kind == "total":
                    totals = {r["cls"]: _int(r.get("n")) for r in found}
                continue
            except SparqlError as exc:
                log(
                    f"  {kind} split of {prop} failed whole ({str(exc)[:80]}); retrying per class"
                )
            # Every pattern requires `?s a ?cls`, so only the classes the total split
            # found can contribute; querying the others just spends endpoint time.
            split: dict[str, int | None] = {}
            complete = True
            for cls in class_iris if totals is None else sorted(totals):
                for attempt in (1, 2):
                    try:
                        found = await rows(prop, kind, cls)
                        partitions.extend(found)
                        split.update((r["cls"], _int(r.get("n"))) for r in found)
                        break
                    except SparqlError as exc:
                        if attempt == 2:
                            complete = False
                            why = f"failed ({str(exc)[:80]})"
                            if kind == "datatype":
                                n = (totals or {}).get(cls)
                                why += "; " + await sampled_datatype(prop, cls, n)
                            else:
                                why += "; left out"
                            notes.append(
                                f"introspection: {kind} split of {prop} on {cls} {why}"
                            )
                            log(f"    {notes[-1]}")
                        else:
                            await asyncio.sleep(INTROSPECT_RETRY_S)
            if kind == "total" and complete:
                totals = split
    return classes, partitions, ds_props, notes


async def build_kg_schema(
    kg: str,
    client: httpx.AsyncClient | None = None,
    log: Log = print,
    source: str = "void",
) -> tuple[list[SchemaRow], list[str]]:
    """Build the schema rows for one KG. Returns ``(rows, notes)``.

    ``source`` is ``"void"`` (the ``okn-void`` statistics) or ``"graph"`` (the same
    statistics counted from the served graph, for a KG whose VoID is stale).
    """
    notes: list[str] = []
    if source == "graph":
        classes, partitions, ds_props, intro_notes = await introspect_partitions(
            kg, client, log
        )
        notes.extend(intro_notes)
        notes.append("schema counted from the served graph: its VoID is stale")
    else:
        classes = (await _run(class_partitions_query(kg), client=client))["rows"]
        partitions = (await _run(property_partitions_query(kg), client=client))["rows"]
        ds_props = (await _run(dataset_properties_query(kg), client=client))["rows"]

    rows = class_rows(classes)
    preds = predicate_rows(partitions, ds_props)

    # Reified edge properties: only for KGs whose VoID shows rdf:predicate in use.
    void_props = {b.get("prop") for b in ds_props} | {b.get("prop") for b in partitions}
    reified: dict[str, int] = {}
    axiom_counts: dict[str, int] = {}
    if RDF_PREDICATE in void_props:
        res = await _run(reified_predicates_query(kg), client=client)
        reified = {r["pred"]: _int(r["n"]) or 0 for r in res["rows"] if r.get("pred")}
        log(f"  {len(reified)} reified predicate(s)")
        pair_counts: dict[tuple[str, str], int] | None = None
        sampled: dict[str, set[str]] | None = None
        if len(reified) > 1:
            try:
                res = await _run(
                    edge_property_counts_query(kg),
                    client=client,
                    timeout=EDGE_COUNT_TIMEOUT,
                )
                pair_counts = {
                    (r["pred"], r["prop"]): _int(r["n"]) or 0 for r in res["rows"]
                }
            except SparqlError as exc:
                log(f"  exact edge-property count failed, sampling: {str(exc)[:120]}")
                notes.append("edge-property counts: exact query failed; sampled")
                sampled = {}
                for pred in reified:
                    res = await _run(
                        edge_property_sample_query(kg, pred), client=client
                    )
                    sampled[pred] = {r["prop"] for r in res["rows"] if r.get("prop")}
        edge_rows, edge_notes = edge_property_rows(
            partitions, reified, pair_counts, sampled
        )
        notes.extend(edge_notes)
        preds = drop_aggregated_edge_rows(
            preds, edge_rows, reifying_classes(partitions)
        )
        preds.extend(edge_rows)

        # Predicates that exist only in reified form have no VoID partition of their own.
        for pred in sorted(set(reified) - void_props):
            try:
                res = await _run(reified_endpoints_query(kg, pred), client=client)
                found = res["rows"]
            except SparqlError as exc:
                log(
                    f"  endpoint classes failed for reified-only {pred}: {str(exc)[:120]}"
                )
                notes.append(f"reified-only predicate without classes: {pred}")
                found = []
            preds.extend(reified_only_rows(pred, found, reified[pred]))

    # OWL ontologies: relations that live only in class axioms or declarations.
    void_classes = {b.get("cls") for b in classes}
    if OWL_ON_PROPERTY in void_props or void_classes & set(OWL_PROPERTY_TYPES):
        try:
            axioms = (await _run(axiom_properties_query(kg), client=client))["rows"]
            declared = (await _run(declared_properties_query(kg), client=client))[
                "rows"
            ]
        except SparqlError as exc:
            log(f"  OWL axiom-property lookup failed: {str(exc)[:120]}")
            notes.append("OWL axiom properties: live lookup failed; omitted")
        else:
            axiom_counts = {
                b["prop"]: _int(b.get("n")) or 0 for b in axioms if b.get("prop")
            }
            owl_rows = axiom_property_rows(axioms, declared, {r.uri for r in preds})
            log(f"  {len({r.uri for r in owl_rows})} axiom-only/declared propert(ies)")
            preds.extend(owl_rows)

    add_patterns(preds, reified, axiom_counts)
    rows.extend(preds)
    rows = drop_excluded(
        rows,
        EXCLUDED_SCHEMA_CLASSES.get(kg, ()),
        EXCLUDED_SCHEMA_PREDICATES.get(kg, ()),
        reified,
    )
    uris = sorted({r.uri for r in rows})
    kg_text = await _lookup_text(kg_iri(kg), uris, client, log)
    missing_obo = [
        u
        for u in uris
        if u.startswith(_OBO_PREFIX) and not kg_text.get(u, {}).get("description")
    ]
    obo_text = (
        await _lookup_text(named_graph("ubergraph"), missing_obo, client, log)
        if missing_obo
        else {}
    )
    apply_text(rows, kg_text, obo_text)
    return rows, notes


# ------------------------------------------------------------------------------ io


def write_csv(rows: Iterable[SchemaRow], path: Path) -> None:
    """Write rows under the :data:`COLUMNS` header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow(row.as_record())


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV into header-keyed dicts."""
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def validate_rows(records: list[dict[str, str]], header: list[str]) -> list[str]:
    """Problems with a written file: header, Type values, Triples integers."""
    problems = []
    if header != COLUMNS:
        problems.append(f"header {header} != {COLUMNS}")
    for i, r in enumerate(records, start=2):
        if None in r or len(r) != len(COLUMNS):
            problems.append(f"line {i}: wrong column count")
        if r.get("Type") not in ("Class", "Predicate"):
            problems.append(f"line {i}: Type {r.get('Type')!r}")
        pat = r.get("Pattern") or ""
        if pat and any(p not in PATTERNS for p in pat.split(";")):
            problems.append(f"line {i}: Pattern {pat!r}")
        t = r.get("Triples") or ""
        if t and not t.isdigit():
            problems.append(f"line {i}: Triples {t!r}")
    return problems


# ------------------------------------------------------------- curated text


def _split_classes(value: str) -> list[str]:
    return [v.strip() for v in re.split(r"[|;]", value or "") if v.strip()]


@dataclass
class CuratedEntry:
    """One curated row, mapped onto the VoID file's vocabulary."""

    uri: str
    type: str  # Class or Predicate (EdgeProperty/NodeProperty folded in)
    original_type: str
    label: str
    description: str
    edge_property_of: str  # URI when resolvable, else the curated text
    sources: list[str]
    targets: list[str]


def normalize_curated(
    records: list[dict[str, str]],
) -> tuple[list[CuratedEntry], list[str]]:
    """Map a curated file onto the new vocabulary. Returns ``(entries, unresolved)``.

    Curated Source/TargetClass hold class LABELS and EdgePropertyOf a predicate's
    short name; both are resolved to URIs through the file's own Class and predicate
    rows. ``EdgeProperty``/``NodeProperty`` fold into ``Predicate``.
    """
    records = [
        r for r in records if r.get("URI") and not _is_provenance_uri(r["URI"].strip())
    ]
    label_to_class: dict[str, str] = {}
    short_to_pred: dict[str, str] = {}
    for r in records:
        uri = r["URI"].strip()
        if (r.get("Type") or "").strip() == "Class":
            for key in (r.get("Label") or "", local_label(uri)):
                if key.strip():
                    label_to_class.setdefault(key.strip(), uri)
                    label_to_class.setdefault(key.strip().casefold(), uri)
        elif (r.get("Type") or "").strip() == "Predicate":
            short_to_pred.setdefault(local_label(uri), uri)
            if (r.get("Label") or "").strip():
                short_to_pred.setdefault(r["Label"].strip(), uri)

    unresolved: set[str] = set()

    def resolve_class(value: str) -> str:
        if value.startswith(("http://", "https://")):
            return value
        hit = label_to_class.get(value) or label_to_class.get(value.casefold())
        if hit is None:
            unresolved.add(value)
            return value
        return hit

    entries = []
    for r in records:
        orig = (r.get("Type") or "").strip()
        parent = (r.get("EdgePropertyOf") or "").strip()
        if parent and not parent.startswith(("http://", "https://")):
            resolved = short_to_pred.get(parent)
            if resolved is None:
                unresolved.add(parent)
            parent = resolved or parent
        entries.append(
            CuratedEntry(
                uri=r["URI"].strip(),
                type="Class" if orig == "Class" else "Predicate",
                original_type=orig,
                label=(r.get("Label") or "").strip(),
                description=(r.get("Description") or "").strip(),
                edge_property_of=parent,
                sources=[
                    resolve_class(v) for v in _split_classes(r.get("SourceClass", ""))
                ],
                targets=[
                    resolve_class(v) for v in _split_classes(r.get("TargetClass", ""))
                ],
            )
        )
    return entries, sorted(unresolved)

"""NCBITaxon hub: per-KG taxon normalization and pairwise overlap skeletons.

The taxonomy crosswalks are a HUB — each member KG maps its organisms to the
canonical ``obo/NCBITaxon_`` form and joins ``ubergraph`` (crosswalks D3-D10), not
each other. So a pairwise overlap between two member KGs is COMPOSED from their two
hub spokes, and it is two-valued:

  * **exact-id** — taxa carrying the SAME NCBITaxon id on both sides (a symmetric,
    strict intersection);
  * **clade-membership** — one KG's taxa nested under the other's taxa via
    ubergraph ``rdfs:subClassOf*`` (directional, and often FAR larger when one side
    is coarser-grained — e.g. genus names vs strain-level taxids).

This module owns the per-KG normalization (:func:`_taxon_source`) and the skeleton
builders (:func:`build_exact_skeleton`, :func:`build_clade_skeleton`). Both the
``taxon_overlap`` MCP tool and the offline ``scripts/refresh_taxon_overlaps.py``
materializer import them, so there is one source of truth for the join SPARQL.
"""

from __future__ import annotations

from .sparql import named_graph

#: NCBITaxon obo IRI prefix, the canonical key every hub spoke normalizes to.
_NCBITAXON = "http://purl.obolibrary.org/obo/NCBITaxon_"

#: rdfs:subClassOf, used both for sawgraph's normalization and the clade walk.
_SUBCLASSOF = "http://www.w3.org/2000/01/rdf-schema#subClassOf"

#: KGs whose taxa reach the ubergraph NCBITaxon hub (have a `_taxon_source`).
TAXON_HUB_KGS = [
    "spoke-okn",
    "nde",
    "sawgraph",
    "biobricks-aopwiki",
    "spoke-genelab",
    "gene-expression-atlas-okn",
]


def _taxon_source(kg: str, var: str) -> str | None:
    """A SPARQL fragment binding ``?{var}`` to ``kg``'s distinct NCBITaxon IRIs.

    Each fragment applies that KG's own normalization (mirroring crosswalks D3-D10)
    so the two sides meet on the canonical ``obo/NCBITaxon_`` form. Internal helper
    variables are derived from ``var`` so two fragments compose without collision.
    Returns None when ``kg`` is not in the NCBITaxon hub.
    """
    g = f"<{named_graph(kg)}>"
    v, h = f"?{var}", f"?_{var}"
    if kg == "sawgraph":
        return (
            f"GRAPH {g} {{ {v} <{_SUBCLASSOF}> {h}1 . "
            f"FILTER(STRSTARTS(STR({v}),'{_NCBITAXON}')) }}"
        )
    if kg == "biobricks-aopwiki":
        return (
            f"GRAPH {g} {{ {h}1 <http://purl.org/dc/elements/1.1/identifier> {v} . "
            f"FILTER(STRSTARTS(STR({v}),'{_NCBITAXON}')) }}"
        )
    if kg == "gene-expression-atlas-okn":
        return (
            f"GRAPH {g} {{ {h}1 <https://w3id.org/biolink/vocab/in_taxon> {v} . "
            f"FILTER(STRSTARTS(STR({v}),'{_NCBITAXON}')) }}"
        )
    if kg == "spoke-okn":
        return (
            f"GRAPH {g} {{ {h}1 a <https://w3id.org/biolink/vocab/OrganismTaxon> }} "
            f"BIND(IRI(CONCAT('{_NCBITAXON}',"
            f"REPLACE(STR({h}1),'^.*/organism/([0-9]+).*$','$1'))) AS {v})"
        )
    if kg == "nde":
        return (
            f"GRAPH {g} {{ {h}1 <http://schema.org/species> {h}2 . "
            f"FILTER(CONTAINS(STR({h}2),'/taxonomy/')) }} "
            f"BIND(IRI(CONCAT('{_NCBITAXON}',"
            f"REPLACE(STR({h}2),'^.*/taxonomy/([0-9]+).*$','$1'))) AS {v})"
        )
    if kg == "spoke-genelab":
        sch = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"
        # model organisms: obo NCBITaxon string literal on Gene.taxonomy (D4)
        model = (
            f"{{ GRAPH {g} {{ {h}1 <{sch}taxonomy> {h}2 . "
            f"FILTER(STRSTARTS(STR({h}2),'{_NCBITAXON}')) }} BIND(IRI(STR({h}2)) AS {v}) }}"
        )
        # microbiome: NCBI taxon id embedded in the Organism node IRI .../node/{id} (D10)
        micro = (
            f"{{ GRAPH {g} {{ {h}3 a <{sch}Organism> . }} "
            f"BIND(IRI(CONCAT('{_NCBITAXON}',"
            f"REPLACE(STR({h}3),'^.*/node/([0-9]+).*$','$1'))) AS {v}) }}"
        )
        return f"{{ {model} UNION {micro} }}"
    return None


def in_taxon_hub(kg: str) -> bool:
    """True when ``kg`` has a taxon representation that reaches the hub."""
    return _taxon_source(kg, "a") is not None


def _sub(kg: str, var: str) -> str:
    """Wrap a KG's taxon source in a DISTINCT subquery.

    That isolates its BIND-constructed taxon (a constructed IRI cannot also be
    pattern-matched in the outer query — reusing the var would be a SPARQL syntax
    error) and collapses each KG's taxa before the join, so the outer pattern is a
    bounded set-membership check, not a cross product.
    """
    return f"{{ SELECT DISTINCT ?{var} WHERE {{ {_taxon_source(kg, var)} }} }}"


def build_exact_skeleton(kg_a: str, kg_b: str) -> str:
    """COUNT of taxa carrying the SAME NCBITaxon id in both KGs (symmetric)."""
    return (
        "SELECT (COUNT(DISTINCT ?t) AS ?shared) WHERE {\n"
        f"  {_sub(kg_a, 't')}\n  {_sub(kg_b, 't')}\n}}"
    )


def build_clade_skeleton(kg_a: str, kg_b: str) -> str:
    """COUNT of ``kg_b`` taxa nested under ``kg_a``'s taxa via ubergraph
    ``subClassOf*`` (directional — swap ``kg_a``/``kg_b`` to flip the clade)."""
    ub = f"<{named_graph('ubergraph')}>"
    return (
        "SELECT (COUNT(DISTINCT ?b) AS ?shared) WHERE {\n"
        f"  {_sub(kg_a, 'a')}\n  {_sub(kg_b, 'b')}\n"
        f"  GRAPH {ub} {{ ?b <{_SUBCLASSOF}>* ?a . }}\n}}"
    )

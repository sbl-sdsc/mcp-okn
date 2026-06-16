"""FastMCP server exposing the FRINK federated SPARQL endpoint.

All queries go to the single federation endpoint
(https://frink.apps.renci.org/federation/sparql) and are scoped to named graphs
of the form https://purl.org/okn/frink/kg/{shortname}. The per-KG endpoints in
the registry are never used.

This module is the assembly point. The ``mcp`` application instance lives in
:mod:`mcp_okn.app`; the tools themselves are grouped by concern under
:mod:`mcp_okn.tools`. Importing those modules here triggers their ``@mcp.tool()``
registration, and their public symbols are re-exported below so existing
``from mcp_okn.server import ...`` imports (and the ``srv.<name>`` access tests
rely on) keep working.
"""

from __future__ import annotations

from . import registry, schema, session
from .app import INSTRUCTIONS, mcp
from .sparql import SparqlError
from .taxon import TAXON_HUB_KGS, _taxon_source
from .tools._shared import _OBO_PREFIXES, _to_uri
from .tools.discovery import describe_kg, list_kgs
from .tools.joins import (
    _complementary_note,
    get_join_strategy,
    list_crosswalks,
    taxon_overlap,
)
from .tools.probe import (
    _CROSSWALK_PREDICATES,
    _NODE_ID_IRI_PREFIXES,
    _crosswalk_query,
    _namespace_query,
    _ontology_id_query,
    _predicate_to_iri,
    _split_predicate_note,
    _undercount_note,
    find_crosswalks,
    probe_namespaces,
)
from .tools.query import expand_ontology_term, sparql_query
from .tools.schema_tools import get_schema, visualize_schema
from .tools.transcript import (
    _clean_description,
    _rows_to_table,
    create_chat_transcript,
    get_query_log,
    latest_transcript_resource,
    reset_query_log,
)

# Re-exported public surface (and a few tested private helpers / shared modules).
# Listing them in __all__ keeps the re-exports from being flagged as unused.
__all__ = [
    "INSTRUCTIONS",
    "SparqlError",
    "TAXON_HUB_KGS",
    "_CROSSWALK_PREDICATES",
    "_NODE_ID_IRI_PREFIXES",
    "_OBO_PREFIXES",
    "_clean_description",
    "_complementary_note",
    "_crosswalk_query",
    "_namespace_query",
    "_ontology_id_query",
    "_predicate_to_iri",
    "_rows_to_table",
    "_split_predicate_note",
    "_taxon_source",
    "_to_uri",
    "_undercount_note",
    "create_chat_transcript",
    "describe_kg",
    "expand_ontology_term",
    "find_crosswalks",
    "get_join_strategy",
    "get_query_log",
    "get_schema",
    "latest_transcript_resource",
    "list_crosswalks",
    "list_kgs",
    "main",
    "mcp",
    "probe_namespaces",
    "registry",
    "reset_query_log",
    "schema",
    "session",
    "sparql_query",
    "taxon_overlap",
    "visualize_schema",
]


def main() -> None:
    """Console entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()

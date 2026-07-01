"""Per-KG provenance (version + last-updated) from the ``okn-void`` graph.

The Proto-OKN meta-graph ``okn-void`` records, for each loaded KG, a small set of
provenance facts on a subject IRI that IS the KG's federation named graph
(``https://purl.org/okn/frink/kg/{shortname}``):

  * ``pav:version``        — the release string, e.g. ``"v0.0.5"``;
  * ``pav:lastUpdatedOn``  — an ISO-8601 timestamp of the last load;
  * ``dcterms:modified``   — a coarse ``"Mon YYYY"`` month stamp.

This module queries those live from the federation and parses them into plain
dicts keyed by shortname. It is the data layer behind the ``get_kg_version`` tool.
"""

from __future__ import annotations

from typing import Any

import httpx

from .registry import EXCLUDED_KGS
from .sparql import named_graph, run_sparql

#: The meta-graph holding the VoID provenance for every loaded KG.
OKN_VOID_GRAPH = named_graph("okn-void")

#: Provenance predicates (see module docstring).
PAV_VERSION = "http://purl.org/pav/version"
PAV_LAST_UPDATED_ON = "http://purl.org/pav/lastUpdatedOn"
DCTERMS_MODIFIED = "http://purl.org/dc/terms/modified"

#: Subject IRIs are the federation named graphs; strip this to recover a shortname.
_GRAPH_IRI_PREFIX = "https://purl.org/okn/frink/kg/"


def _shortname_from_iri(iri: str) -> str:
    """Recover a KG shortname from its named-graph subject IRI."""
    return iri.removeprefix(_GRAPH_IRI_PREFIX)


def _version_query(shortname: str | None) -> str:
    """A SPARQL query for one KG's (or every KG's) VoID provenance.

    Anchors on ``pav:version`` (present for every KG that records provenance) and
    left-joins the two date stamps, which a KG may omit.
    """
    subject = f"<{named_graph(shortname)}>" if shortname else "?s"
    # For a single KG the subject is a fixed IRI, so bind it back into ?s to keep
    # the result shape identical to the all-KGs scan.
    bind_line = f"\n    BIND({subject} AS ?s)" if shortname else ""
    return f"""\
SELECT ?s ?version ?last_updated ?modified WHERE {{
  GRAPH <{OKN_VOID_GRAPH}> {{
    {subject} <{PAV_VERSION}> ?version .
    OPTIONAL {{ {subject} <{PAV_LAST_UPDATED_ON}> ?last_updated }}
    OPTIONAL {{ {subject} <{DCTERMS_MODIFIED}> ?modified }}{bind_line}
  }}
}}
ORDER BY ?s"""


def _row_to_record(row: dict[str, Any]) -> dict[str, Any]:
    """Project one result row to a provenance record.

    Keys: ``{shortname, version, last_updated, modified, named_graph}``.
    """
    iri = row.get("s", "")
    return {
        "shortname": _shortname_from_iri(iri),
        "version": row.get("version"),
        "last_updated": row.get("last_updated"),
        "modified": row.get("modified"),
        "named_graph": iri,
    }


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

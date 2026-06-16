"""Helpers shared by more than one tool module."""

from __future__ import annotations

_OBO_PREFIXES = (
    "MONDO",
    "CHEBI",
    "GO",
    "HP",
    "UBERON",
    "CL",
    "PR",
    "NCBITaxon",
    "DOID",
    "SO",
    "PATO",
    "BFO",
    "ENVO",
    "FOODON",
    "OBI",
)


def _to_uri(term: str) -> str:
    """Convert an OBO CURIE (PREFIX:1234567) to a full purl URI; pass URIs through."""
    if term.startswith(("http://", "https://")):
        return term
    if ":" in term:
        prefix, _, local = term.partition(":")
        if prefix in _OBO_PREFIXES:
            return f"http://purl.obolibrary.org/obo/{prefix}_{local}"
    return term

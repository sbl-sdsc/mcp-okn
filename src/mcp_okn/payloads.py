"""Per-KG payload tags: WHAT each knowledge graph supplies, not just how it joins.

`get_join_strategy` / `list_crosswalks` already expose the *join* half of a KG
(shared key, predicates, verified count). The value a graph actually adds — the
entity and annotation types it carries — was previously buried in prose, so an
agent would judge a graph by its name and miss, say, that ``digcfdekg`` supplies
gene→trait inferences or that ``pankgraph`` carries GO annotations.

This module serves a curated, controlled-vocabulary tag set (``data/kg_payloads``
``.json``) mapping each servable KG shortname to the list of context types it
supplies. The editable source of record lives in ``metadata/kg_payloads.json``
and is synced into the package by ``scripts/refresh_snapshot.py`` (same lifecycle
as ``crosswalks.json``).
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

# Process-lifetime cache (the table is static and changes rarely).
_data_cache: dict[str, Any] | None = None


def load_payloads() -> dict[str, Any]:
    """Load the bundled static payload table.

    Returns an empty dict if the file is missing or unreadable, so callers
    degrade gracefully (no payload tags) instead of erroring.
    """
    global _data_cache
    if _data_cache is not None:
        return _data_cache
    try:
        text = (resources.files("mcp_okn") / "data" / "kg_payloads.json").read_text(
            encoding="utf-8"
        )
        data = json.loads(text)
        _data_cache = data if isinstance(data, dict) else {}
    except (FileNotFoundError, ModuleNotFoundError, json.JSONDecodeError, OSError):
        _data_cache = {}
    return _data_cache


def vocabulary() -> dict[str, str]:
    """The controlled payload vocabulary: ``{type: human-readable gloss}``."""
    vocab = load_payloads().get("vocabulary", {})
    return vocab if isinstance(vocab, dict) else {}


def payloads_for(shortname: str) -> list[str]:
    """The payload tags a KG supplies (``[]`` if none / unknown)."""
    tags = load_payloads().get("payloads", {}).get(shortname, [])
    return list(tags) if isinstance(tags, list) else []


def kgs_with_payload(ptype: str) -> list[str]:
    """Every KG shortname whose payload tags include ``ptype`` (sorted)."""
    payloads = load_payloads().get("payloads", {})
    return sorted(sn for sn, tags in payloads.items() if ptype in tags)


def is_known_type(ptype: str) -> bool:
    """True if ``ptype`` is a defined payload vocabulary term."""
    return ptype in vocabulary()


def verified_on() -> str | None:
    """The date the payload tags were last curated, for staleness visibility."""
    return load_payloads().get("verified_on")

"""Discovery of Proto-OKN knowledge graphs via the okn-registry.

Each KG has a markdown file with YAML frontmatter in the frink-okn/okn-registry
repo. We use those descriptions purely to help choose which named graph(s) to
query on the *federation* endpoint. The per-KG ``sparql:``/``tpf:`` endpoints in
the frontmatter are intentionally NOT exposed as query targets.
"""

from __future__ import annotations

import asyncio
import json
from importlib import resources
from typing import Any

import httpx
import yaml

from .sparql import named_graph

_CONTENTS_API = (
    "https://api.github.com/repos/frink-okn/okn-registry/contents/docs/registry/kgs"
)
_RAW_BASE = (
    "https://raw.githubusercontent.com/frink-okn/okn-registry/"
    "refs/heads/main/docs/registry/kgs/{shortname}.md"
)

# KGs listed in the registry but excluded from results — e.g. not loaded in the
# federation under their expected named graph (queries return no rows).
# `babel` (Translator Babel identifier cliques) joined the registry in the
# 2026-09-01 refresh while still empty and was excluded here; it was loaded by
# 2026-09-26 and restored, now as an identifier-mapping bridge KG (see the
# `babel` usage notes in schema.py).
# `bio101` (KB Bio 101) was empty from at least 2026-06-18 (recorded in
# crosswalks.json `known_non_joins` as "unmaterialized") and was excluded on
# 2026-09-02, which also retired its only payload tag `biology_concept`. It was
# loaded as v0.0.1 by 2026-10-05 and restored together with that tag: a pure
# OWL2 ontology (~6,300 owl:Class concepts, relations only inside
# owl:Restriction axioms) with no external identifiers.
# `glygenkg` (GlyGen: glycans, glycoproteins, glycosylation sites) joined the
# registry by 2026-09-26 but is NOT loaded: LIMIT 1 returns no row under every
# candidate graph IRI (.../kg/glygenkg, .../kg/glygenkg/, frink.renci.org/kg/
# glygenkg), checked serially on 2026-09-26. Excluded so `refresh_snapshot.py`
# does not abort on its missing payload entry while we wait for the upload;
# integrating it (payload tags, schema, crosswalks — likely UniProt/Entrez into
# the protein and gene clusters) is its own pass once it is served.
# Drop a name from this set once the federation loads it.
EXCLUDED_KGS = {"semopenalex", "glygenkg"}

# Process-lifetime caches (the registry changes rarely).
_shortnames_cache: list[str] | None = None
_meta_cache: dict[str, dict[str, Any]] = {}
_doc_cache: dict[str, str] = {}


def load_snapshot() -> list[dict[str, Any]]:
    """Load the bundled static KG snapshot (for instant cold starts).

    Returns an empty list if the snapshot is missing or unreadable, so callers
    can fall back to a live registry fetch.
    """
    try:
        text = (resources.files("mcp_okn") / "data" / "kgs.json").read_text(
            encoding="utf-8"
        )
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, ModuleNotFoundError, json.JSONDecodeError, OSError):
        return []


def _raw_url(shortname: str) -> str:
    return _RAW_BASE.format(shortname=shortname)


def _split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body) from a markdown file with `---` fences."""
    if markdown.startswith("---"):
        parts = markdown.split("---", 2)
        if len(parts) == 3:
            front = _safe_load_yaml(parts[1])
            return (front if isinstance(front, dict) else {}, parts[2].strip())
    return {}, markdown.strip()


def _safe_load_yaml(text: str) -> dict[str, Any]:
    """Parse YAML frontmatter, tolerating stray trailing whitespace.

    Some registry entries carry trailing tabs/spaces after a value (e.g. a tab
    after a contact email), which YAML rejects with a scanner error. A raw tab
    never carries meaning in these flat key-value blocks, so on failure we retry
    with each line right-stripped before giving up.
    """
    for candidate in (text, "\n".join(line.rstrip() for line in text.splitlines())):
        try:
            front = yaml.safe_load(candidate) or {}
        except yaml.YAMLError:
            continue
        if isinstance(front, dict):
            return front
    return {}


def _meta_from_front(shortname: str, front: dict[str, Any]) -> dict[str, Any]:
    """Project frontmatter to the safe, query-relevant metadata surface.

    Note: ``sparql`` and ``tpf`` are deliberately dropped so the per-KG Jena
    endpoints are never surfaced as query targets.
    """
    return {
        "shortname": front.get("shortname", shortname),
        "title": front.get("title", shortname),
        "description": (front.get("description") or "").strip(),
        "homepage": front.get("homepage"),
        "named_graph": named_graph(front.get("shortname", shortname)),
    }


async def list_kg_shortnames(
    client: httpx.AsyncClient | None = None, refresh: bool = False
) -> list[str]:
    """List KG shortnames from the registry directory (cached)."""
    global _shortnames_cache
    if _shortnames_cache is not None and not refresh:
        return _shortnames_cache

    owns = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
    try:
        resp = await client.get(
            _CONTENTS_API, headers={"Accept": "application/vnd.github+json"}
        )
        resp.raise_for_status()
        entries = resp.json()
    finally:
        if owns:
            await client.aclose()

    names = sorted(
        e["name"][:-3]
        for e in entries
        if isinstance(e, dict)
        and e.get("name", "").endswith(".md")
        and e["name"][:-3] not in EXCLUDED_KGS
    )
    _shortnames_cache = names
    return names


async def fetch_kg_meta(
    shortname: str, client: httpx.AsyncClient | None = None, refresh: bool = False
) -> dict[str, Any]:
    """Fetch and parse one KG's frontmatter into safe metadata (cached)."""
    if shortname in _meta_cache and not refresh:
        return _meta_cache[shortname]

    owns = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
    try:
        resp = await client.get(_raw_url(shortname))
        resp.raise_for_status()
        raw = resp.text
        front, _body = _split_frontmatter(raw)
    finally:
        if owns:
            await client.aclose()

    meta = _meta_from_front(shortname, front)
    _meta_cache[shortname] = meta
    _doc_cache[shortname] = raw  # populate doc cache opportunistically
    return meta


async def list_kgs(refresh: bool = False) -> list[dict[str, Any]]:
    """Return metadata for every KG.

    By default this serves the bundled static snapshot for an instant cold
    start. Pass ``refresh=True`` to re-fetch the live registry (and rebuild the
    in-process caches). If the snapshot is unavailable, falls back to a live
    fetch automatically.
    """
    if not refresh:
        snapshot = load_snapshot()
        if snapshot:
            return snapshot

    async with httpx.AsyncClient(timeout=30.0) as client:
        names = await list_kg_shortnames(client=client, refresh=refresh)
        metas = await asyncio.gather(
            *(fetch_kg_meta(n, client=client, refresh=refresh) for n in names),
            return_exceptions=True,
        )
    result: list[dict[str, Any]] = []
    for name, meta in zip(names, metas, strict=True):
        if isinstance(meta, BaseException):
            result.append(
                {
                    "shortname": name,
                    "title": name,
                    "description": f"(failed to load registry entry: {meta})",
                    "named_graph": named_graph(name),
                }
            )
        else:
            result.append(meta)
    return result


async def fetch_kg_doc(
    shortname: str, client: httpx.AsyncClient | None = None, refresh: bool = False
) -> str:
    """Return the full registry markdown (frontmatter + prose) for one KG."""
    if shortname in _doc_cache and not refresh:
        return _doc_cache[shortname]

    owns = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
    try:
        resp = await client.get(_raw_url(shortname))
        resp.raise_for_status()
    finally:
        if owns:
            await client.aclose()

    _doc_cache[shortname] = resp.text
    return resp.text


async def fetch_kg_long_description(
    shortname: str, client: httpx.AsyncClient | None = None, refresh: bool = False
) -> str:
    """Return a KG's free-text description: the markdown body after the YAML.

    Each registry entry carries a ~150-word prose description below its
    frontmatter — richer than the one-line ``description`` field exposed by
    ``list_kgs``. Useful for disambiguating which KG a question targets when the
    short descriptions aren't enough. Returns an empty string if the entry has no
    body. Reuses the document cache populated by :func:`fetch_kg_doc`.
    """
    doc = await fetch_kg_doc(shortname, client=client, refresh=refresh)
    _front, body = _split_frontmatter(doc)
    return body

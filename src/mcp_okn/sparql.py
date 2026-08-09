"""Client for the OKN federated SPARQL endpoint.

This is the ONLY network path used to run queries. The per-KG SPARQL endpoints
listed in the registry (Apache Jena instances) are deliberately never used: they
time out or run out of memory on complex queries. Every query is sent to the
QLever-backed federation endpoint and scoped to named graphs.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import random
import re
import weakref
from typing import Any

import httpx

#: The single federation endpoint. Do not query per-KG endpoints.
FEDERATION_ENDPOINT = "https://apps.okn.us/federation/sparql"

#: Statuses worth retrying: the endpoint's server-side operation limit (429) and the
#: gateway/overload family. QLever's own query errors come back as 400 with an
#: `exception` body — deterministic, so retrying one only doubles the wait.
_RETRY_STATUSES = frozenset({429, 502, 503, 504})

#: 429 is QLever's "Operation timed out", and it does not fail fast: measured at ~30s
#: per attempt against the live endpoint. Retrying is still right — crosswalks.json
#: records skeletons sitting right at the limit that failed two runs in three and
#: passed the third — but each try is expensive, so it gets ONE, where a
#: gateway/overload status (which returns immediately) gets the full `max_retries`.
_SLOW_STATUS_RETRIES = {429: 1}

#: Backoff before retry N (jittered).
_BACKOFF_SECONDS = (0.5, 2.0)

#: Cap on an honoured `Retry-After`, so a large one can't stall a tool call for minutes.
_MAX_RETRY_AFTER = 30.0


async def _sleep(seconds: float) -> None:
    """Sleep between retries. Patched in tests so the suite doesn't actually wait."""
    await asyncio.sleep(seconds)


def _retry_delay(resp: httpx.Response, attempt: int) -> float:
    """Seconds to wait before retry ``attempt`` (1-based), honouring ``Retry-After``."""
    header = resp.headers.get("retry-after", "")
    with contextlib.suppress(TypeError, ValueError):
        if header:
            return min(float(header), _MAX_RETRY_AFTER)
    base = _BACKOFF_SECONDS[min(attempt, len(_BACKOFF_SECONDS)) - 1]
    # Jitter so concurrent queries don't retry in lockstep (not a crypto use).
    return base * (1.0 + random.random() * 0.25)


# One client per event loop, so a keep-alive connection is reused across queries
# instead of paying a TLS handshake each time (find_crosswalks alone fires three
# concurrent queries). Keyed by loop — and weakly — because the test suite runs each
# test in a fresh loop, and a pooled connection belonging to a closed loop is unusable.
_clients: weakref.WeakKeyDictionary[Any, httpx.AsyncClient] = (
    weakref.WeakKeyDictionary()
)


def _shared_client(timeout: float) -> httpx.AsyncClient:
    """Return this event loop's shared client, creating it on first use."""
    try:
        loop: Any = asyncio.get_running_loop()
    except RuntimeError:  # no loop (sync caller) — hand back a throwaway client
        return httpx.AsyncClient(timeout=timeout)
    client = _clients.get(loop)
    if client is None or client.is_closed:
        client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=10),
        )
        _clients[loop] = client
    return client


async def aclose_shared_client() -> None:
    """Close this event loop's shared client, if one was created. For teardown."""
    with contextlib.suppress(RuntimeError):
        loop = asyncio.get_running_loop()
        client = _clients.pop(loop, None)
        if client is not None and not client.is_closed:
            await client.aclose()


#: Template for a KG's federation named graph URI.
GRAPH_URI = "https://purl.org/okn/frink/kg/{shortname}"

_ACCEPT = {
    "json": "application/sparql-results+json",
    "csv": "text/csv",
    "tsv": "text/tsv",
}


def named_graph(shortname: str) -> str:
    """Return the federation named-graph URI for a KG shortname."""
    return GRAPH_URI.format(shortname=shortname)


# schema.org's canonical RDF namespace is `http://schema.org/`, which most Proto-OKN
# KGs store, but models routinely write the `https://` website form. The two are
# distinct IRIs to a SPARQL engine, so an `https://schema.org/...` term silently
# matches nothing. We canonicalize the `https` form to `http` — but ONLY where it
# appears as an angle-bracketed IRI (`<https://schema.org/...>`), never inside a
# string literal or `IRI(CONCAT("https://schema.org/", ...))`. A few KGs actually
# STORE the `https` form (nikg's schema:location, ruralkg's schema:postalCode,
# ufokn's schema:value); leaving literals intact preserves the only way to reach
# them — bind the predicate as a variable and match it scheme-free, e.g.
# `FILTER(STRENDS(STR(?p), "schema.org/location"))`, or rebuild the IRI with
# `IRI(CONCAT("https://schema.org/", ...))`.
_SCHEMA_ORG_HTTPS_IRI = re.compile(r"<https://schema\.org/")
_SCHEMA_ORG_HTTPS_BARE = re.compile(r"https://schema\.org/")


def normalize_schema_org(query: str) -> str:
    """Canonicalize bracketed ``<https://schema.org/…>`` IRIs to the ``http`` form.

    Scoped to angle-bracketed IRIs (and so PREFIX declarations), so string literals
    and ``IRI(CONCAT(…))`` fragments are left untouched — see the module comment.
    """
    return _SCHEMA_ORG_HTTPS_IRI.sub("<http://schema.org/", query)


def canonicalize_schema_org_iri(iri: str) -> str:
    """Canonicalize a single bare schema.org IRI string to the ``http`` form.

    No angle brackets. For resolving one predicate/term IRI, not a whole query.
    """
    return _SCHEMA_ORG_HTTPS_BARE.sub("http://schema.org/", iri)


class SparqlError(RuntimeError):
    """Raised when the endpoint returns an error for a query."""


def _flatten_bindings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Turn SPARQL JSON results bindings into compact {var: value} rows."""
    rows: list[dict[str, Any]] = []
    for binding in payload.get("results", {}).get("bindings", []):
        row: dict[str, Any] = {}
        for var, cell in binding.items():
            value = cell.get("value")
            # Cast common numeric/boolean datatypes for convenience.
            dtype = cell.get("datatype", "")
            if dtype.endswith(("integer", "int", "long", "decimal", "double", "float")):
                with contextlib.suppress(TypeError, ValueError):
                    value = (
                        float(value)
                        if "." in value or "e" in value.lower()
                        else int(value)
                    )
            elif dtype.endswith("boolean"):
                value = value == "true"
            row[var] = value
        rows.append(row)
    return rows


async def run_sparql(
    query: str,
    fmt: str = "json",
    timeout: float = 120.0,
    client: httpx.AsyncClient | None = None,
    normalize_schema: bool = True,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Run a SPARQL query against the OKN federation endpoint.

    Args:
        query: A complete SPARQL query string. Scope to a KG with
            ``GRAPH <https://purl.org/okn/frink/kg/{shortname}> { ... }``.
        fmt: Output format: ``json`` (default, parsed into rows), ``csv`` or
            ``tsv`` (returned as raw text).
        timeout: Request timeout in seconds.
        client: Optional httpx.AsyncClient to use instead of this event loop's
            shared one. A caller-supplied client is never closed here.
        normalize_schema: Canonicalize bracketed ``<https://schema.org/…>`` IRIs
            to the ``http`` form (default True). Set False to leave them as
            written — required for the KGs that STORE the ``https`` form
            (``ruralkg``, ``sockg``, ``hydrologykg``, ``nikg``, ``ufokn``),
            where canonicalizing to ``http`` would silently match nothing.
        max_retries: How many times to retry a TRANSIENT failure (the
            gateway/overload statuses), with jittered backoff. Default 2; pass 0
            to disable. A 429 gets at most ONE retry however high this is — each
            attempt costs a full ~30s server-side operation timeout. Query errors
            and request timeouts are never retried: they are deterministic, so a
            retry only doubles the wait.

    Returns:
        For ``json``: ``{"vars": [...], "rows": [...], "row_count": N}``.
        For ``csv``/``tsv``: ``{"format": fmt, "text": "..."}``.

    Raises:
        SparqlError: If the endpoint reports a query error (including the
            read-only-filesystem error QLever raises for large external sorts) or
            the request times out — a scan too broad to finish in ``timeout``s.
    """
    if fmt not in _ACCEPT:
        raise ValueError(f"Unsupported format {fmt!r}; use one of {sorted(_ACCEPT)}")

    if normalize_schema:
        query = normalize_schema_org(query)
    headers = {"Accept": _ACCEPT[fmt]}
    data = {"query": query}

    # A caller-supplied client belongs to the caller; the shared one is reused across
    # queries. Either way this call never closes it.
    if client is None:
        client = _shared_client(timeout)

    attempts = 0
    while True:
        attempts += 1
        try:
            resp = await client.post(
                FEDERATION_ENDPOINT, data=data, headers=headers, timeout=timeout
            )
        except httpx.TimeoutException as exc:
            # Surface as SparqlError so callers degrade uniformly instead of crashing
            # on a raw httpx traceback. A timeout means the scan was too broad to
            # finish in time — narrow it (e.g. add a `sample`/`LIMIT`). Not retried:
            # the same query would scan the same ground and burn another `timeout`s.
            raise SparqlError(
                f"SPARQL request timed out after {timeout}s — the query scanned too "
                f"much; narrow it with a sample/LIMIT.\nQuery:\n{query}"
            ) from exc
        # The endpoint's operation limit (429) and the gateway/overload family are
        # transient: the same query commonly succeeds moments later. Back off and
        # retry rather than handing the caller a failure it can do nothing about.
        budget = min(
            max_retries, _SLOW_STATUS_RETRIES.get(resp.status_code, max_retries)
        )
        if resp.status_code in _RETRY_STATUSES and attempts <= budget:
            await _sleep(_retry_delay(resp, attempts))
            continue
        break

    text = resp.text

    # QLever returns HTTP 400 with a JSON body containing an "exception" field
    # (e.g. the "Read-only file system" sort error) on query failure.
    if resp.status_code != 200:
        message = text
        try:
            err = json.loads(text)
            message = err.get("exception", text)
        except (json.JSONDecodeError, ValueError):
            pass
        # Name the retries when there were any, so an exhausted transient failure
        # ("still overloaded after 3 tries") reads differently from a bad query.
        tried = f" after {attempts} attempts" if attempts > 1 else ""
        raise SparqlError(
            f"SPARQL endpoint returned HTTP {resp.status_code}{tried}: "
            f"{message.strip()}\nQuery:\n{query}"
        )

    if fmt != "json":
        return {"format": fmt, "text": text}

    payload = resp.json()
    rows = _flatten_bindings(payload)
    return {
        "vars": payload.get("head", {}).get("vars", []),
        "rows": rows,
        "row_count": len(rows),
    }

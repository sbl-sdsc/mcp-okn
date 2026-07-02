"""Per-session log of SPARQL queries executed during a session.

Every query run through the server is appended here so `create_chat_transcript`
can render a faithful, ground-truth record of what actually hit the endpoint —
rather than relying on the model to re-supply queries from memory.

The log is scoped to the current MCP session. Under stdio (a single local
client) there is effectively one log; but when the server is run as a REMOTE
(HTTP/SSE) server, several chats share one process, each on its own
`ServerSession`. Keying the log by that session keeps one chat's queries,
diagrams, and transcript from leaking into another's. Call `reset()` (exposed as
the `reset_query_log` tool) at the start of a new analysis to scope a transcript
to just that session's work so far.

State for a session is dropped automatically when its connection closes and the
`ServerSession` is garbage-collected (the store is held in a `WeakKeyDictionary`).
"""

from __future__ import annotations

import re
import weakref
from datetime import datetime, timezone
from typing import Any

#: Cap on rows stored per query, so a huge result set can't grow the log without
#: bound. The true row count is always kept; only the stored sample is capped.
MAX_LOGGED_ROWS = 1000

_GRAPH_RE = re.compile(r"GRAPH\s*<https://purl\.org/okn/frink/kg/([^>]+)>")


class _Store:
    """The mutable per-session state: query log, diagrams, last transcript."""

    __slots__ = ("last_transcript", "log", "visualizations")

    def __init__(self) -> None:
        self.log: list[dict[str, Any]] = []
        self.visualizations: list[dict[str, Any]] = []
        self.last_transcript: str | None = None


# Fallback store used when there is no active MCP request (direct calls in tests,
# or any code path outside a request). All such callers share this one store, so
# behavior matches the previous process-global log.
_default_store = _Store()

# Per-session stores, keyed by the live `ServerSession` object. Weak keys so a
# store is reclaimed when its connection closes — no manual cleanup, no unbounded
# growth on a long-running remote server.
_stores: weakref.WeakKeyDictionary[Any, _Store] = weakref.WeakKeyDictionary()


def _current_store() -> _Store:
    """Return the store for the current MCP session (or the shared fallback).

    Resolves the active `ServerSession` via the FastMCP request context. Outside
    a request — or if the context is unavailable for any reason — falls back to a
    single process-wide store so non-request callers (e.g. tests) keep working.
    """
    session_obj = _current_session()
    if session_obj is None:
        return _default_store
    store = _stores.get(session_obj)
    if store is None:
        store = _Store()
        _stores[session_obj] = store
    return store


def _current_session() -> Any | None:
    """The active MCP `ServerSession`, or None when outside a request.

    Imported lazily to avoid a hard import cycle and to keep this module usable
    without a running server (the app instance pulls in the tool modules).
    """
    try:
        from .app import mcp

        return mcp.get_context().session
    except Exception:
        # No request context (stdio startup, tests, background tasks) or the
        # session isn't available yet — use the shared fallback store.
        return None


def graphs_in(query: str) -> list[str]:
    """Return the KG shortnames referenced via ``GRAPH <.../kg/{name}>``, in order."""
    seen: list[str] = []
    for name in _GRAPH_RE.findall(query):
        if name not in seen:
            seen.append(name)
    return seen


def _result_row_count(result: Any) -> int:
    """Number of rows a `run_sparql` result holds (0 if empty/unknown)."""
    if not isinstance(result, dict):
        return 0
    if "rows" in result:
        return result.get("row_count") or len(result.get("rows") or [])
    if "text" in result:
        # csv/tsv: a header line plus at least one data line means rows.
        lines = [ln for ln in str(result.get("text") or "").splitlines() if ln.strip()]
        return max(len(lines) - 1, 0)
    return 0


def record(query: str, fmt: str, result: Any = None, error: str | None = None) -> bool:
    """Append one executed query to the session log if it returned results.

    Queries that errored or returned zero rows are NOT logged — the transcript
    is meant to record only the queries that produced findings. Exploratory
    queries are skipped at the call site (they are never passed here).

    Args:
        query: The exact SPARQL text that was sent.
        fmt: The requested result format (``json``/``csv``/``tsv``).
        result: The value returned by ``run_sparql`` on success.
        error: The error message if the query failed.

    Returns:
        True if the query was logged, False if it was skipped (error/empty).
    """
    if error is not None or _result_row_count(result) == 0:
        return False

    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sparql": query,
        "graphs": graphs_in(query),
        "format": fmt,
        "row_count": None,
        "results": None,
    }
    if isinstance(result, dict) and "rows" in result:
        rows = result.get("rows") or []
        total = result.get("row_count", len(rows))
        sample = rows[:MAX_LOGGED_ROWS]
        entry["row_count"] = total
        entry["results"] = {
            "vars": result.get("vars", []),
            "rows": sample,
            "row_count": total,
            "truncated": len(rows) > len(sample),
        }
    elif isinstance(result, dict) and "text" in result:
        entry["row_count"] = _result_row_count(result)
        entry["results"] = {
            "format": result.get("format", fmt),
            "text": result.get("text", ""),
        }
    _current_store().log.append(entry)
    return True


def entries() -> list[dict[str, Any]]:
    """Return a shallow copy of the logged queries, in execution order."""
    return list(_current_store().log)


def record_visualization(shortname: str, mermaid: str) -> None:
    """Record a schema visualization (Mermaid diagram) for the transcript.

    Like queries, diagrams are logged automatically as they are produced so
    `create_chat_transcript` can render them without the model re-supplying the
    diagram. Re-visualizing the same KG replaces its earlier diagram (keeping
    the original position) so only the latest diagram per KG is kept.
    """
    if not mermaid:
        return
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "shortname": shortname,
        "mermaid": mermaid,
    }
    visualizations = _current_store().visualizations
    for i, existing in enumerate(visualizations):
        if existing.get("shortname") == shortname:
            visualizations[i] = entry
            return
    visualizations.append(entry)


def visualizations() -> list[dict[str, Any]]:
    """Return a shallow copy of the logged schema visualizations, in order."""
    return list(_current_store().visualizations)


def set_last_transcript(markdown: str) -> None:
    """Store the most recently rendered transcript markdown.

    Exposed read-only via the ``transcript://session/latest`` MCP resource so a
    client can fetch/save the document directly, independent of how (or whether)
    the model re-emits it.
    """
    _current_store().last_transcript = markdown


def last_transcript() -> str | None:
    """Return the most recently rendered transcript markdown, or None."""
    return _current_store().last_transcript


def reset() -> int:
    """Clear the session log (queries, visualizations, last transcript).

    Returns the number of logged queries removed.
    """
    store = _current_store()
    n = len(store.log)
    store.log.clear()
    store.visualizations.clear()
    store.last_transcript = None
    return n

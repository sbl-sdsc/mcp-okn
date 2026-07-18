"""Per-session, per-scope log of SPARQL queries executed during a session.

Every query run through the server is appended here so `create_chat_transcript`
can render a faithful, ground-truth record of what actually hit the endpoint —
rather than relying on the model to re-supply queries from memory.

State is keyed by TWO things:

1. The current MCP session. Under stdio (a single local client) there is
   effectively one session; but when the server is run as a REMOTE (HTTP/SSE)
   server, several chats share one process, each on its own `ServerSession`.
   Keying by that session keeps one chat's queries out of another's.

2. A caller-supplied `scope` label, defaulting to ``"default"``.

The session key alone is NOT enough, which is why (2) exists. Several concurrent
ANALYSES routinely share one `ServerSession` — most importantly parallel
subagents, which all speak to the server over their parent's single client
connection. To the server these are one session, so without a scope their queries
interleave in one log and `create_chat_transcript` renders whatever happens to be
there: an agent's transcript silently ships another agent's SPARQL and drops its
own. (This bit us for real while authoring the crosswalk catalog on 2026-07-13 —
every parallel authoring agent hit it independently.) MCP carries no agent
identity, so the server cannot separate them on its own; the caller must say which
analysis a query belongs to by passing a unique `scope`.

Call `reset()` (the `reset_query_log` tool) at the start of an analysis to clear
its scope. Scopes are independent: resetting one never touches another.

State for a session is dropped automatically when its connection closes and the
`ServerSession` is garbage-collected (the stores are held in a
`WeakKeyDictionary`).
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

    __slots__ = ("last_transcript", "log", "skipped", "visualizations")

    def __init__(self) -> None:
        self.log: list[dict[str, Any]] = []
        # Queries that ran but were NOT added to `log` (errored / empty / marked
        # exploratory), each tagged with the reason. Purely diagnostic — never
        # rendered into a transcript — so a caller can see WHY a query is missing
        # from the log instead of it vanishing silently.
        self.skipped: list[dict[str, Any]] = []
        self.visualizations: list[dict[str, Any]] = []
        self.last_transcript: str | None = None


#: Scope used when the caller doesn't name one. A single (non-parallel) analysis
#: never has to think about scopes; it just uses this one.
DEFAULT_SCOPE = "default"

# Fallback scope table used when there is no active MCP request (direct calls in
# tests, or any code path outside a request). All such callers share this table,
# so behavior matches the previous process-global log.
_default_scopes: dict[str, _Store] = {}

# Per-session scope tables, keyed by the live `ServerSession` object. Weak keys so
# a session's stores are reclaimed when its connection closes — no manual cleanup,
# no unbounded growth on a long-running remote server.
_stores: weakref.WeakKeyDictionary[Any, dict[str, _Store]] = weakref.WeakKeyDictionary()


def _scope_table() -> dict[str, _Store]:
    """The ``{scope: _Store}`` table for the current MCP session.

    Resolves the active `ServerSession` via the FastMCP request context. Outside
    a request — or if the context is unavailable for any reason — falls back to a
    single process-wide table so non-request callers (e.g. tests) keep working.
    """
    session_obj = _current_session()
    if session_obj is None:
        return _default_scopes
    table = _stores.get(session_obj)
    if table is None:
        table = {}
        _stores[session_obj] = table
    return table


def _current_store(scope: str | None = None) -> _Store:
    """Return the store for ``scope`` within the current session, creating it if new."""
    table = _scope_table()
    key = scope or DEFAULT_SCOPE
    store = table.get(key)
    if store is None:
        store = _Store()
        table[key] = store
    return store


def scopes() -> list[str]:
    """Names of the scopes that currently hold state in this session."""
    return sorted(_scope_table())


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


def record(
    query: str,
    fmt: str,
    result: Any = None,
    error: str | None = None,
    exploratory: bool = False,
    scope: str | None = None,
) -> bool:
    """Append one executed query to the session log if it returned results.

    Queries that errored, returned zero rows, or were marked ``exploratory`` are
    NOT logged — the transcript is meant to record only the queries that produced
    findings. Such queries are still retained in the ``skipped`` list (tagged with
    the reason) so a caller can see WHY a query is absent from the log; call
    :func:`skipped` to read them.

    Args:
        query: The exact SPARQL text that was sent.
        fmt: The requested result format (``json``/``csv``/``tsv``).
        result: The value returned by ``run_sparql`` on success.
        error: The error message if the query failed.
        exploratory: True if the caller marked this query exploratory (schema
            probing / sampling). Recorded as a skip with reason ``exploratory``.
        scope: Which analysis this query belongs to. Concurrent analyses sharing
            one MCP session (e.g. parallel subagents) MUST each pass their own
            scope, or their queries interleave in one log.

    Returns:
        True if the query was logged, False if it was skipped
        (error/empty/exploratory).
    """
    # Precedence: an error is the most diagnostic reason, then the caller's
    # exploratory intent, then an empty result. Anything else gets logged.
    reason: str | None = None
    if error is not None:
        reason = "error"
    elif exploratory:
        reason = "exploratory"
    elif _result_row_count(result) == 0:
        reason = "empty"
    if reason is not None:
        _current_store(scope).skipped.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "sparql": query,
                "graphs": graphs_in(query),
                "format": fmt,
                "reason": reason,
                "error": error,
                "row_count": _result_row_count(result),
            }
        )
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
    _current_store(scope).log.append(entry)
    return True


def entries(scope: str | None = None) -> list[dict[str, Any]]:
    """Return a shallow copy of ``scope``'s logged queries, in execution order."""
    return list(_current_store(scope).log)


def skipped(scope: str | None = None) -> list[dict[str, Any]]:
    """Return ``scope``'s skipped queries (error/empty/exploratory), in order.

    Each entry carries ``sparql``, ``graphs``, ``format``, ``reason``
    (``error``/``exploratory``/``empty``), ``error`` (the message when
    ``reason == "error"``, else None), and ``row_count``. Diagnostic only — these
    never enter a transcript.
    """
    return list(_current_store(scope).skipped)


def record_visualization(
    shortname: str, mermaid: str, scope: str | None = None
) -> None:
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
    visualizations = _current_store(scope).visualizations
    for i, existing in enumerate(visualizations):
        if existing.get("shortname") == shortname:
            visualizations[i] = entry
            return
    visualizations.append(entry)


def visualizations(scope: str | None = None) -> list[dict[str, Any]]:
    """Return a shallow copy of ``scope``'s schema visualizations, in order."""
    return list(_current_store(scope).visualizations)


def set_last_transcript(markdown: str, scope: str | None = None) -> None:
    """Store the most recently rendered transcript markdown.

    Exposed read-only via the ``transcript://session/latest`` MCP resource so a
    client can fetch/save the document directly, independent of how (or whether)
    the model re-emits it.
    """
    _current_store(scope).last_transcript = markdown


def last_transcript(scope: str | None = None) -> str | None:
    """Return the most recently rendered transcript markdown, or None."""
    return _current_store(scope).last_transcript


def reset(scope: str | None = None) -> int:
    """Clear ONE scope's log (queries, visualizations, last transcript).

    Other scopes are untouched, so one analysis resetting its own log can never
    wipe a concurrently-running analysis's.

    Returns the number of logged queries removed.
    """
    store = _current_store(scope)
    n = len(store.log)
    store.log.clear()
    store.skipped.clear()
    store.visualizations.clear()
    store.last_transcript = None
    return n

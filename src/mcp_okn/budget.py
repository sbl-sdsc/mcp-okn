"""A size budget shared by every tool whose reply can grow without bound.

Clients cap a tool reply. Claude Code saves anything over 25,000 tokens to a file and
hands the agent a pointer. An agent that cannot read files (the benchmark disables
Read) gets no data at all; one that can spends extra turns reading the file back. In
the v0.3.0 benchmark, replies of 60K to 670K characters went that way:
``get_valid_contrasts`` with no tissue, ``list_crosswalks`` with examples,
``get_join_strategy`` with one KG, ``find_context_sources`` with no join key, and
SPARQL results of up to 2.2M characters. In the GXA case, the agent re-ran the same
query with ``LIMIT 25`` after its 623-row reply was spilled.

Every tool therefore keeps its reply under :data:`REPLY_CHAR_BUDGET` characters of
compact JSON. That is the form a client receives (see :mod:`compact_output`). When a
reply is cut, the tool says so in the reply: the full count, what was left out, and
the narrower call that gets the rest.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

#: Characters of compact JSON a reply may use. Claude Code delivered a 43,920-
#: character schema and spilled a 49,800-character one; 40,000 leaves room for
#: clients that count more conservatively.
REPLY_CHAR_BUDGET = 40_000


def reply_size(reply: Any) -> int:
    """Length of ``reply`` as compact JSON, the form a client receives."""
    return len(json.dumps(reply, separators=(",", ":"), default=str))


def cap_items(
    reply: Any,
    get: Callable[[], list[Any]],
    put: Callable[[list[Any]], None],
    budget: int = REPLY_CHAR_BUDGET,
    floor: int = 0,
) -> int:
    """Keep the longest prefix of ``get()`` (never below ``floor``) that fits.

    ``put`` writes a candidate prefix into ``reply``; the size is measured on the
    whole reply, so any notes already in it count. Returns how many items were cut.
    """
    items = get()
    if reply_size(reply) <= budget or len(items) <= floor:
        return 0
    lo, hi = floor, len(items)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        put(items[:mid])
        if reply_size(reply) <= budget:
            lo = mid
        else:
            hi = mid - 1
    put(items[:lo])
    return len(items) - lo


#: Appended to a SPARQL reply that was cut to fit.
SPARQL_TRUNCATED_HINT = (
    "Only the first {returned} of {total} rows are shown (the reply is capped at "
    "about {budget:,} characters; the rows follow your ORDER BY). Don't re-run the "
    "query to see the rest. Instead, aggregate (COUNT/GROUP BY), add a LIMIT, or "
    "select fewer columns. The transcript log keeps the complete result."
)


def fit_sparql_result(
    result: dict[str, Any], budget: int = REPLY_CHAR_BUDGET
) -> dict[str, Any]:
    """Cut a ``sparql_query`` reply to ``budget``, keeping the leading rows.

    Handles all three reply shapes: dict rows (``rows``/``row_count``), columnar
    (``data``/``count``) and csv/tsv text (``text``). The returned dict reports
    ``truncated``, ``returned`` and the full count, plus a hint. A reply that
    already fits is returned unchanged (the same object).
    """
    if reply_size(result) <= budget:
        return result
    out = dict(result)
    if "text" in out and isinstance(out["text"], str):
        lines = out["text"].splitlines(keepends=True)
        header, body = lines[:1], lines[1:]
        total = len(body)
        out.update(truncated=True, returned=0, total_rows=total)
        out["hint"] = SPARQL_TRUNCATED_HINT.format(
            returned=total, total=total, budget=budget
        )

        def put_text(rows: list[str]) -> None:
            out["text"] = "".join(header + rows)
            out["returned"] = len(rows)
            out["hint"] = SPARQL_TRUNCATED_HINT.format(
                returned=len(rows), total=total, budget=budget
            )

        cap_items(out, lambda: body, put_text, budget)
        return out

    key = "data" if "data" in out else "rows"
    count_key = "count" if key == "data" else "row_count"
    rows = list(out.get(key) or [])
    total = out.get(count_key, len(rows))
    out.update(truncated=True, returned=len(rows))
    out["hint"] = SPARQL_TRUNCATED_HINT.format(
        returned=len(rows), total=total, budget=budget
    )

    def put_rows(kept: list[Any]) -> None:
        out[key] = kept
        out["returned"] = len(kept)
        out["hint"] = SPARQL_TRUNCATED_HINT.format(
            returned=len(kept), total=total, budget=budget
        )

    cap_items(out, lambda: rows, put_rows, budget)
    return out

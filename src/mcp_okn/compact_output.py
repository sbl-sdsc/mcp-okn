"""Serialize tool replies as compact JSON instead of FastMCP's indented JSON.

FastMCP turns a non-string tool return value into its text content with
``pydantic_core.to_json(result, indent=2)``. Every nested value then sits on its own
line behind its indentation, and a ``{"columns", "data"}`` table puts each cell on a
separate line. In the v0.3.0 benchmark (360 episodes) compact JSON was 26% shorter
for ``get_schema`` replies and 24% shorter for ``sparql_query`` replies. The agent
reads the reply again on every later turn, so that whitespace was paid for many
times over.

The text block is the only part this changes. ``structuredContent`` is produced from
the same value elsewhere and is left alone.

``_convert_to_content`` is private to the MCP SDK, so the override is defensive: if
a future SDK renames it, :func:`install` does nothing and replies are indented as
before. ``tests/test_compact_output.py`` checks that the override is in place.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import pydantic_core


def dumps(value: Any) -> str:
    """Compact JSON text, matching FastMCP's serializer apart from the indent."""
    return pydantic_core.to_json(value, fallback=str).decode()


def _make_converter(original: Callable[[Any], Sequence[Any]]) -> Callable[..., Any]:
    def convert(result: Any) -> Sequence[Any]:
        # Anything FastMCP handles specially (strings, content blocks, images, and
        # lists of those) goes to the original. Everything else (dicts, models,
        # numbers) is turned into a string here, and FastMCP passes a string
        # through unchanged.
        if result is None or isinstance(result, str):
            return original(result)
        if isinstance(result, list | tuple):
            # A list of plain JSON values is serialized as ONE compact block,
            # which is what FastMCP's indented path effectively produced too.
            # Lists of content blocks still go item by item.
            if all(isinstance(x, dict | str | int | float | bool) for x in result):
                return original(dumps(list(result)))
            return original(result)
        if isinstance(result, dict):
            return original(dumps(result))
        return original(result)

    convert.__wrapped__ = original  # type: ignore[attr-defined]
    return convert


def install() -> bool:
    """Make FastMCP serialize dict replies compactly. Returns True if installed."""
    try:
        from mcp.server.fastmcp.utilities import func_metadata
    except ImportError:  # pragma: no cover - SDK layout changed
        return False
    original = getattr(func_metadata, "_convert_to_content", None)
    if original is None:  # pragma: no cover - SDK renamed it
        return False
    if getattr(original, "__wrapped__", None) is not None:
        return True  # already installed
    func_metadata._convert_to_content = _make_converter(original)
    return True

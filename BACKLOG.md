# Backlog

Non-urgent improvements, roughly in priority order. See the git history for
what's already landed (CI, ruff/mypy, the `tools/` package split).

## Tighten ruff / mypy

Both linters were adopted in a deliberately lenient mode so the first run wasn't
a wall of findings (see `pyproject.toml`). Tighten incrementally now that the
baseline is clean:

- **mypy** — ✅ done. Now runs `strict = true` (reached incrementally, one flag
  at a time; every step passed with no source changes — the code was already
  thoroughly typed). `ignore_missing_imports` stays on for the untyped third-party
  surface (`mcp`, `httpx`, `yaml`).
- **ruff** lints `F/E/W/I/UP/B/C4/SIM/RET/PTH/RUF` with `E501` deferred to the
  formatter and the `RUF001/002/003` ambiguous-unicode rules ignored (intentional
  prose typography). `SIM`, `RET`, `PTH`, and `RUF` were added and their findings
  cleared. Still open: a docstring convention (`D`) if we want enforced docstrings
  on the public tool surface.

## Broader test coverage on the tool layer

`tools/taxon.py` has no dedicated test module, and the `sparql_query`
hint/error-wrapping and `expand_ontology_term` URI-building branches in
`tools/query.py` aren't directly exercised. Add `tests/test_taxon.py` and a few
`tools/query.py` cases.

## Opt-in compact result format

A `compact: bool` flag on `query` (and `multi_graph_query`) that returns
`{columns, data, count}` positional rows instead of repeated-key dicts, to cut
tokens on large LLM-facing result sets. Apply it at the tool boundary only —
internal consumers (crosswalk scans, transcript rendering) rely on dict rows.
Reuse the existing numeric/boolean casting in `_flatten_bindings`; represent
unbound cells as `None`, not `""`; pass `hint`/`error` through untouched.

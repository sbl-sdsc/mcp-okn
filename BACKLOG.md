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
- **ruff** — ✅ done. Lints `F/E/W/I/UP/B/C4/SIM/RET/PTH/RUF/D` (pydocstyle on
  the Google convention). `E501` is deferred to the formatter; `RUF001/002/003`
  (ambiguous-unicode) are ignored for the intentional prose typography; and `D`
  is scoped to `src/` via per-file-ignores (tests, scripts, and the benchmark
  harness don't require docstrings).

## Broader test coverage on the tool layer

✅ done. Added `tests/test_taxon.py` (the NCBITaxon hub module's skeleton
builders and per-KG normalization fragments) and `tests/test_query.py`
(`expand_ontology_term` query construction — CURIE expansion, reflexive vs
strict path, ancestors/descendants, partOf, limit, logging — and `sparql_query`
error-wrapping, schema.org normalization, graph detection, csv passthrough).

## Opt-in compact result format

A `compact: bool` flag on `query` (and `multi_graph_query`) that returns
`{columns, data, count}` positional rows instead of repeated-key dicts, to cut
tokens on large LLM-facing result sets. Apply it at the tool boundary only —
internal consumers (crosswalk scans, transcript rendering) rely on dict rows.
Reuse the existing numeric/boolean casting in `_flatten_bindings`; represent
unbound cells as `None`, not `""`; pass `hint`/`error` through untouched.

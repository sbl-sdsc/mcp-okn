"""
readd_query_diagrams.py — ONE command for the SECOND half of the defer-and-re-add diagram flow.

Background: a reproducibility transcript / chat transcript is generated with `include_query_diagrams=
False` so the per-query mermaid diagrams (25–50%+ of the bytes) don't push the return over the inline
limit and spill. That is HALF the flow. The diagrams must then be RE-ADDED — generating lean and not
re-adding silently drops them, which is an omission, not a "concision" choice. This script is that
second half, made as close to one command as the environment allows:

    python readd_query_diagrams.py transcript.md

It picks the right path automatically:

1. `--diagrams diagrams.json` given  → inject those diagrams (the tool-path second step). Use this in a
   report session after calling the `sparql_to_mermaid` TOOL on each verbatim query.

2. else, `sparql-to-mermaid` importable → generate every diagram locally AND inject, in this one call.
   Works in an mcp-okn dev checkout (or any env where the package is installed). Nothing else to run.

3. else (report session: package not importable, no diagrams.json yet) → this is where the ritual used
   to get forgotten. Instead of erroring, write the exact WORK-LIST of un-diagrammed queries to
   `<transcript>.queries.json` and print the next command. Turn that list into diagrams.json by calling
   the `sparql_to_mermaid` TOOL on each verbatim query, then re-run with `--diagrams diagrams.json`.
   Exits non-zero so a caller can tell the file is NOT done yet.

Injection, matching, the size cap, and idempotency all come from expand_query_diagrams.py — this is a
single front door over that logic, not a second copy of it. FIDELITY: every diagram is generated from
the query EXACTLY as logged; a too-big diagram is skipped (see --max-chars), never shortened to fit.

    python readd_query_diagrams.py transcript.md                          # dev checkout: one and done
    python readd_query_diagrams.py transcript.md --diagrams diagrams.json # report session: inject
    python readd_query_diagrams.py transcript.md --out out.md --max-chars 4000
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Single-source the injection logic: reuse expand_query_diagrams.py rather than reimplement it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from expand_query_diagrams import (
    DEFAULT_MAX_CHARS,
    _map_generate,
    expand,
    queries_needing_diagrams,
)


def _try_library():
    """Return the `try_to_mermaid` callable if `sparql-to-mermaid` is importable here, else None.

    The package is mcp-okn-internal and NOT on PyPI, so it is importable in a dev checkout but usually
    NOT where a report is built — that split is exactly why path 3 (the work-list) exists.
    """
    try:
        from sparql_to_mermaid import try_to_mermaid
    except ModuleNotFoundError:
        return None
    return try_to_mermaid


def _emit_worklist(src: Path, text: str) -> int:
    """Path 3: write the un-diagrammed queries to a work-list JSON and print the next command.

    Returns a process exit code: 0 if the file already has every diagram (nothing to do), else 2 to
    signal "not done yet — feed the work-list to the sparql_to_mermaid tool and re-run".
    """
    queries = queries_needing_diagrams(text)
    if not queries:
        print(f"{src}: every ```sparql block already has a diagram — nothing to re-add.")
        return 0
    work = src.with_name(src.name + ".queries.json")
    work.write_text(json.dumps([{"sparql": q} for q in queries], indent=2))
    print(
        f"{src}: {len(queries)} query(ies) still need a diagram, and `sparql-to-mermaid` is not "
        f"importable here (expected in a report session).\n"
        f"Wrote the work-list to: {work}\n\n"
        f"NEXT — turn it into diagrams.json, then re-run:\n"
        f"  1. For EACH verbatim query in {work.name}, call the mcp-okn `sparql_to_mermaid` TOOL\n"
        f"     (never a shortened copy — a diagram under a query it doesn't match is a fidelity break).\n"
        f'  2. Save the results as diagrams.json — a list of {{"sparql": …, "mermaid": …}} objects.\n'
        f"  3. python {Path(__file__).name} {src} --diagrams diagrams.json\n"
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="transcript markdown file to re-add diagrams to")
    ap.add_argument("--out", help="write result here (default: edit PATH in place)")
    ap.add_argument(
        "--diagrams",
        help="JSON of diagrams from the sparql_to_mermaid tool (list of {sparql,mermaid} or "
        "{sparql: mermaid}). Omit to generate locally when sparql-to-mermaid is importable, or to "
        "emit a work-list when it is not.",
    )
    ap.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"skip any diagram whose mermaid text exceeds this (default {DEFAULT_MAX_CHARS}; mirrors "
        "the server's diagram_max_chars). Pass 0 for no cap.",
    )
    args = ap.parse_args(argv)

    src = Path(args.path)
    text = src.read_text()
    cap = None if args.max_chars == 0 else args.max_chars

    if args.diagrams:
        generate = _map_generate(args.diagrams)  # path 1: inject supplied diagrams
    else:
        library = _try_library()
        if library is None:
            return _emit_worklist(src, text)  # path 3: no package, no diagrams.json → work-list
        generate = library  # path 2: generate locally AND inject in this call

    new_text, st = expand(text, generate, max_chars=cap)
    dst = Path(args.out) if args.out else src
    dst.write_text(new_text)
    print(
        f"{dst}: {st['sparql']} sparql blocks → {st['added']} diagrams added, "
        f"{st['already']} already present, {st['absent']} absent-skipped, "
        f"{st['oversized']} oversized-skipped (>{cap})"
    )
    for snip, ln in st["oversized_queries"]:
        print(f"  oversized ({ln} chars, skipped): {snip}…")
    for snip in st["absent_queries"]:
        print(f"  no diagram (skipped): {snip}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

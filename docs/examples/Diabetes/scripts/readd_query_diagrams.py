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
    python readd_query_diagrams.py transcript.md --portable              # dev checkout, portable mode
    python readd_query_diagrams.py transcript.md --check                  # DELIVERY GATE (verify only)

DELIVERY GATE: `--check` verifies WITHOUT modifying — PASS if every ```sparql block already has a
diagram, else FAIL + exit 1. It needs no package and no diagrams.json, so run it as the last step
before delivering: a FAIL means the re-add half was skipped. This mirrors report-style's
`check_report_parity` gate for the HTML — the transcript is not delivered until `--check` PASSes
(unless the user asked for no diagrams).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Single-source the injection logic: reuse expand_query_diagrams.py rather than reimplement it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from expand_query_diagrams import (
    _MCP_NOTICE_RE,
    DEFAULT_MAX_CHARS,
    _map_generate,
    diagrams_missing_graph_box,
    expand,
    queries_needing_diagrams,
    strip_mcp_notices,
)


def _try_library(portable: bool = False):
    """Return a `sparql -> mermaid|None` callable if `sparql-to-mermaid` is importable here, else None.

    The package is mcp-okn-internal and NOT on PyPI, so it is importable in a dev checkout but usually
    NOT where a report is built — that split is exactly why path 3 (the work-list) exists. ``portable``
    is forwarded to ``try_to_mermaid`` (unknown IRIs -> ``segment:local`` CURIEs, pipe-label aggregate
    edges) for stricter/older Mermaid renderers.
    """
    try:
        from sparql_to_mermaid import try_to_mermaid
    except ModuleNotFoundError:
        return None
    return lambda sparql: try_to_mermaid(sparql, portable=portable)


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


def check(src: Path, text: str) -> int:
    """Completeness + fidelity gate: verify every ```sparql block has a diagram AND that each
    diagram is faithful `sparql_to_mermaid` output, WITHOUT modifying.

    Mirrors report-style's `check_report_parity` gate for the HTML: prints a single PASS/FAIL line and
    exits 0 (all present and faithful) or 1 otherwise. Works in ANY environment — it never generates, so
    it needs neither the sparql-to-mermaid package nor a diagrams.json. Run it as the last step before
    delivering a transcript. Two failure modes:
      - PRESENCE: a ```sparql block has no ```mermaid diagram — the re-add half was skipped.
      - FIDELITY: a query scoped to a named GRAPH has a diagram with no `subgraph ["GRAPH …"]` box, so
        the diagram is not what `sparql_to_mermaid` produces (hand-authored, stale, or from a bespoke
        script). Regenerate it from the verbatim query with the tool/library — never hand-draw one.
    """
    missing = queries_needing_diagrams(text)
    unfaithful = diagrams_missing_graph_box(text)
    total = text.count("```sparql")
    # Backstop: a stale `<!-- mcp-okn WARNING: … -->` notice must never ship in the artifact. The
    # re-add pass strips it, but a file that already had its diagrams (so re-add was skipped) can still
    # carry it — catch that here, at the last gate before delivery.
    stale_notice = bool(_MCP_NOTICE_RE.search(text))
    if not missing and not unfaithful and not stale_notice:
        print(
            f"[readd_query_diagrams] PASS — all {total} sparql block(s) have a faithful diagram: {src}"
        )
        return 0
    if missing:
        print(
            f"[readd_query_diagrams] FAIL — {len(missing)} of {total} sparql block(s) have NO diagram: "
            f"{src}\n  The diagram re-add step was skipped. Run "
            f"`python {Path(__file__).name} {src}` (no --check) to add them; do NOT deliver until PASS."
        )
        for q in missing[:5]:
            print(f"  missing: {' '.join(q.split())[:70]}…")
    if unfaithful:
        print(
            f"[readd_query_diagrams] FAIL — {len(unfaithful)} of {total} diagram(s) are NOT faithful "
            f"sparql_to_mermaid output: {src}\n  A query scoped to a named GRAPH has a diagram with no "
            f'`subgraph ["GRAPH …"]` box, so it was hand-authored, is stale, or came from a bespoke '
            f"script. Regenerate it from the VERBATIM query with the `sparql_to_mermaid` tool/library "
            f"(never hand-draw a diagram); do NOT deliver until PASS."
        )
        for q in unfaithful[:5]:
            print(f"  unfaithful (no GRAPH box): {' '.join(q.split())[:70]}…")
    if stale_notice:
        print(
            f"[readd_query_diagrams] FAIL — a stale `<!-- mcp-okn WARNING: … -->` notice is baked into "
            f"{src}\n  That caller-facing nudge must not ship in the artifact. Run "
            f"`python {Path(__file__).name} {src}` (no --check) to strip it; do NOT deliver until PASS."
        )
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="transcript markdown file to re-add diagrams to")
    ap.add_argument(
        "--check",
        action="store_true",
        help="VERIFY only (never modify): PASS if every sparql block has a diagram, else FAIL + exit 1. "
        "Works with no package / no diagrams.json. Use as the delivery gate.",
    )
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
    ap.add_argument(
        "--portable",
        action="store_true",
        help="generate stricter-renderer-compatible diagrams (unknown IRIs -> segment:local CURIEs, "
        "pipe-label aggregate edges). Only affects LOCAL generation (path 2); ignored with --diagrams "
        "(pass portable=True to the sparql_to_mermaid tool when building diagrams.json instead).",
    )
    args = ap.parse_args(argv)

    src = Path(args.path)
    text = src.read_text()
    cap = None if args.max_chars == 0 else args.max_chars

    if args.check:
        return check(src, text)

    # Strip any stale `<!-- mcp-okn WARNING: … -->` notice up front and persist it now, so it is
    # removed even when the paths below write nothing (all diagrams already present, or the work-list
    # branch). expand() also strips, so the injection paths stay correct on their own.
    dst = Path(args.out) if args.out else src
    text, n_notices = strip_mcp_notices(text)
    if n_notices:
        dst.write_text(text)
        print(f"{dst}: stripped {n_notices} stale mcp-okn notice(s).")

    if args.diagrams:
        if args.portable:
            print(
                "note: --portable is ignored with --diagrams (supplied diagrams are used as-is; pass "
                "portable=True to the sparql_to_mermaid tool when building diagrams.json)."
            )
        generate = _map_generate(args.diagrams)  # path 1: inject supplied diagrams
    else:
        library = _try_library(portable=args.portable)
        if library is None:
            return _emit_worklist(src, text)  # path 3: no package, no diagrams.json → work-list
        generate = library  # path 2: generate locally AND inject in this call

    new_text, st = expand(text, generate, max_chars=cap)
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

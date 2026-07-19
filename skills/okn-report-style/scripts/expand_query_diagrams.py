"""
expand_query_diagrams.py — postprocessing step that injects a ```mermaid diagram after every
```sparql block in a transcript, so the transcript can be GENERATED diagram-free (small, no stub /
harness spill) and made diagram-rich locally afterward.

Why defer: the per-query mermaid diagram duplicates the adjacent SPARQL and is 25–50%+ of a
transcript's bytes, so generating with diagrams inline is what makes `create_chat_transcript` /
`create_reproducibility_record` overflow the inline limit and spill. Keeping the re-add local keeps
the large blob off the tool round-trip.

TWO ways to supply the diagrams — injection itself needs NO third-party package:

1. `--diagrams diagrams.json` (the PORTABLE path — use this in a report session). The
   `sparql-to-mermaid` package is mcp-okn-internal and NOT pip-installable, so it usually cannot be
   imported where reports are built — but the mcp-okn **`sparql_to_mermaid` TOOL** is available over
   MCP. Call that tool on each **verbatim** logged query, collect the results into a JSON, and inject:

       # in the report session, for each logged query q (VERBATIM — see fidelity note):
       #   diagrams.append({"sparql": q, "mermaid": sparql_to_mermaid(q)["mermaid"]})
       # write that list (or a {sparql: mermaid} dict) to diagrams.json, then:
       python expand_query_diagrams.py transcript.md --diagrams diagrams.json --max-chars 4000

   diagrams.json is either a list of {"sparql","mermaid"} objects or a {sparql: mermaid} dict; a block
   is matched to its diagram by whitespace-normalized SPARQL, so injection needs no rdflib/mermaid lib.

2. No `--diagrams`: falls back to importing `try_to_mermaid` from `sparql-to-mermaid` and generating
   locally — works only in a dev checkout of mcp-okn where that package is installed.

FIDELITY: generate every diagram from the query EXACTLY as logged. Do not strip a `VALUES` clause or
otherwise shorten the query to make the diagram smaller — a diagram that sits under a ```sparql block
it does not match misrepresents it. If a diagram is too big, SKIP it (below), don't fake a small one.

SIZE CAP (`--max-chars`, default 4000, mirroring the server's `diagram_max_chars`): as of
`sparql-to-mermaid` v0.4.2 a long `VALUES` list collapses to "3 values + `+N more`" (the `max_values`
default), so the old symbol-list blowup — a 250-symbol query → a ~28,000-char diagram of ~280 useless
nodes — no longer happens. (v0.4.2 also quotes node labels, so an IRI containing special characters —
e.g. a Reactome/PubChem id with `(` — no longer breaks Mermaid parsing.) The cap stays as a general
backstop for any diagram that is still huge (e.g.
a query with very many distinct triples); over-cap diagrams are skipped, informative ones
(~500–3,500 chars) kept. The script prints which queries were skipped so you can note them in the
transcript, exactly as the server does inline.

Idempotent: a ```sparql block already immediately followed by a ```mermaid block is left alone, so
re-running (or expanding a partially-expanded file) never double-injects.

    python expand_query_diagrams.py transcript.md --diagrams diagrams.json   # portable, edit in place
    python expand_query_diagrams.py transcript.md --diagrams d.json --out o.md
    python expand_query_diagrams.py transcript.md                            # dev checkout only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_MAX_CHARS = 4000


def _normalize(sparql: str) -> str:
    """Whitespace-normalized key so a ```sparql block matches its diagrams.json entry regardless of
    incidental reflow (both are the same logged query, so this matches exactly)."""
    return re.sub(r"\s+", " ", sparql).strip()


def _library_generate():
    """Return a `sparql -> mermaid|None` callable backed by the local sparql-to-mermaid package,
    or exit with guidance if it (the dev-only, non-PyPI package) is not importable."""
    try:
        from sparql_to_mermaid import try_to_mermaid
    except ModuleNotFoundError:
        sys.exit(
            "sparql-to-mermaid is not importable (it is mcp-okn-internal, not on PyPI), so diagrams "
            "cannot be generated here.\nGenerate them with the mcp-okn `sparql_to_mermaid` TOOL on "
            "each verbatim logged query, write [{'sparql':…,'mermaid':…}, …] to diagrams.json, and "
            "re-run with:\n  python expand_query_diagrams.py <transcript.md> --diagrams diagrams.json"
        )
    return try_to_mermaid


def _map_generate(diagrams_path: str):
    """Return a `sparql -> mermaid|None` callable backed by a diagrams.json produced from the
    `sparql_to_mermaid` tool. Accepts a list of {sparql, mermaid} (or {query, diagram}) objects or a
    {sparql: mermaid} dict; keys are whitespace-normalized for matching."""
    raw = json.loads(Path(diagrams_path).read_text())
    table: dict[str, str] = {}
    if isinstance(raw, dict):
        items = raw.items()
    else:
        items = (
            (d.get("sparql") or d.get("query"), d.get("mermaid") or d.get("diagram"))
            for d in raw
        )
    for sparql, mermaid in items:
        if sparql and mermaid:
            table[_normalize(sparql)] = mermaid
    return lambda sparql: table.get(_normalize(sparql))


def queries_needing_diagrams(text: str) -> list[str]:
    """Return the verbatim SPARQL of every ```sparql block NOT already followed by a ```mermaid block.

    This is the work-list to hand to the `sparql_to_mermaid` TOOL when the `sparql-to-mermaid` package
    can't be imported locally (the report-session case): generate a diagram per query, collect them into
    diagrams.json, then inject with :func:`expand`. Uses the same fence walk and already-present rule as
    :func:`expand`, so a block that already carries a diagram is never listed.
    """
    lines = text.split("\n")
    todo: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        if _fence_kind(lines[i]) == "sparql":
            body: list[str] = []
            j = i + 1
            while j < n and lines[j].strip() != "```":
                body.append(lines[j])
                j += 1
            i = j + 1
            k = i  # already followed by a ```mermaid block (allowing blank lines)?
            while k < n and lines[k].strip() == "":
                k += 1
            if k < n and _fence_kind(lines[k]) == "mermaid":
                continue
            sparql = "\n".join(body).strip()
            if sparql:
                todo.append(sparql)
        else:
            i += 1
    return todo


def _fence_kind(line: str) -> str | None:
    """Return the language of an opening code fence (e.g. 'sparql', 'mermaid'), else None."""
    s = line.strip()
    if s.startswith("```") and len(s) > 3:
        return s[3:].strip().lower()
    return None


def expand(
    text: str, generate, max_chars: int | None = DEFAULT_MAX_CHARS
) -> tuple[str, dict]:
    """Insert a ```mermaid block after each ```sparql block that lacks one.

    `generate` is a `sparql -> mermaid str | None` callable (library- or tool-backed). A query with no
    diagram (generate returns falsy) is skipped like the server skips an unparseable one; a diagram
    over `max_chars` is skipped and recorded. Returns (new_text, stats); stats['oversized_queries'] and
    ['absent_queries'] carry a short SPARQL snippet per skip so you can log them in the transcript.
    """
    lines = text.split("\n")
    out: list[str] = []
    stats = {
        "sparql": 0,
        "added": 0,
        "already": 0,
        "absent": 0,
        "oversized": 0,
        "oversized_queries": [],
        "absent_queries": [],
    }
    i, n = 0, len(lines)
    while i < n:
        if _fence_kind(lines[i]) == "sparql":
            stats["sparql"] += 1
            body: list[str] = []
            j = i + 1
            while j < n and lines[j].strip() != "```":
                body.append(lines[j])
                j += 1
            out.extend(lines[i : j + 1])  # emit the sparql block verbatim
            i = j + 1
            k = i  # already followed by a ```mermaid block (allowing blank lines)?
            while k < n and lines[k].strip() == "":
                k += 1
            if k < n and _fence_kind(lines[k]) == "mermaid":
                stats["already"] += 1
                continue
            sparql = "\n".join(body).strip()
            snippet = _normalize(sparql)[:70]
            mermaid = generate(sparql) if sparql else None
            if not mermaid:
                stats["absent"] += 1
                stats["absent_queries"].append(snippet)
                continue
            if max_chars is not None and len(mermaid) > max_chars:
                stats["oversized"] += 1
                stats["oversized_queries"].append((snippet, len(mermaid)))
                continue
            out.extend(["", "```mermaid", mermaid.strip(), "```"])
            stats["added"] += 1
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="transcript markdown file to expand")
    ap.add_argument("--out", help="write result here (default: edit PATH in place)")
    ap.add_argument(
        "--diagrams",
        help="JSON of diagrams from the sparql_to_mermaid tool (list of {sparql,mermaid} or "
        "{sparql: mermaid}); enables dependency-free injection. Omit to generate locally (dev only).",
    )
    ap.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"skip any diagram whose mermaid text exceeds this (default {DEFAULT_MAX_CHARS}; "
        "mirrors the server's diagram_max_chars — drops the uninformative symbol-list monsters). "
        "Pass 0 for no cap.",
    )
    args = ap.parse_args(argv)
    generate = _map_generate(args.diagrams) if args.diagrams else _library_generate()
    cap = None if args.max_chars == 0 else args.max_chars
    src = Path(args.path)
    new_text, st = expand(src.read_text(), generate, max_chars=cap)
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

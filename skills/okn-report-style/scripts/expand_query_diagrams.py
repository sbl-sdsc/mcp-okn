"""
expand_query_diagrams.py — postprocessing step that injects a ```mermaid diagram after every
```sparql block in a transcript, so the transcript can be GENERATED diagram-free (small, no stub /
harness spill) and made diagram-rich locally afterward.

Why a local script and not a server tool: the per-query mermaid diagram duplicates the adjacent
SPARQL and is 25–50%+ of a transcript's bytes, so generating with diagrams inline is what makes the
`create_chat_transcript` / `create_reproducibility_record` return overflow the inline limit and spill.
A server tool that returned the expanded doc would just re-spill. Keeping the expansion local keeps
the large blob off the tool round-trip entirely.

Workflow:
    create_chat_transcript(..., include_query_diagrams=False)   # lean return, never spills
    # save the returned markdown to <study>_reproducibility_transcript.md, then:
    .venv/bin/python skills/okn-report-style/scripts/expand_query_diagrams.py <transcript.md>

The diagram text is byte-identical to what the server would have emitted inline: it reuses the same
`try_to_mermaid` from the `sparql-to-mermaid` package the server uses (src/mcp_okn/tools/transcript.py),
so a query that doesn't parse is silently skipped exactly as inline generation skips it.

Idempotent: a ```sparql block that is already immediately followed by a ```mermaid block is left
alone, so re-running (or expanding a partially-expanded file) never double-injects.

    .venv/bin/python .../expand_query_diagrams.py transcript.md              # edit in place
    .venv/bin/python .../expand_query_diagrams.py transcript.md --out out.md # write elsewhere
    .venv/bin/python .../expand_query_diagrams.py transcript.md --max-chars 1500  # skip huge diagrams
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from sparql_to_mermaid import try_to_mermaid
except ModuleNotFoundError:
    sys.exit(
        "sparql-to-mermaid not importable — run this with the project venv, e.g.\n"
        "  .venv/bin/python skills/okn-report-style/scripts/expand_query_diagrams.py <file>"
    )


def _fence_kind(line: str) -> str | None:
    """Return the language of an opening code fence (e.g. 'sparql', 'mermaid'), else None."""
    s = line.strip()
    if s.startswith("```") and len(s) > 3:
        return s[3:].strip().lower()
    return None


def expand(text: str, max_chars: int | None = None) -> tuple[str, dict]:
    """Insert a ```mermaid block after each ```sparql block that lacks one.

    Returns (new_text, stats). Reuses the server's `try_to_mermaid`, so output matches inline
    generation; unparseable queries are skipped like the server does.
    """
    lines = text.split("\n")
    out: list[str] = []
    stats = {"sparql": 0, "added": 0, "already": 0, "unparseable": 0, "oversized": 0}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if _fence_kind(line) == "sparql":
            # collect the sparql block body until its closing fence
            stats["sparql"] += 1
            body: list[str] = []
            j = i + 1
            while j < n and lines[j].strip() != "```":
                body.append(lines[j])
                j += 1
            # j is the closing fence (or EOF); emit the sparql block verbatim
            out.extend(lines[i : j + 1])
            i = j + 1
            # does a ```mermaid block already follow (allowing blank lines)?
            k = i
            while k < n and lines[k].strip() == "":
                k += 1
            if k < n and _fence_kind(lines[k]) == "mermaid":
                stats["already"] += 1
                continue
            sparql = "\n".join(body).strip()
            mermaid = try_to_mermaid(sparql) if sparql else None
            if not mermaid:
                stats["unparseable"] += 1
                continue
            if max_chars is not None and len(mermaid) > max_chars:
                stats["oversized"] += 1
                continue
            out.extend(["", "```mermaid", mermaid.strip(), "```"])
            stats["added"] += 1
        else:
            out.append(line)
            i += 1
    return "\n".join(out), stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="transcript markdown file to expand")
    ap.add_argument("--out", help="write result here (default: edit PATH in place)")
    ap.add_argument(
        "--max-chars",
        type=int,
        default=None,
        help="skip any diagram whose mermaid text exceeds this many chars (mirrors diagram_max_chars)",
    )
    args = ap.parse_args(argv)
    src = Path(args.path)
    new_text, stats = expand(src.read_text(), max_chars=args.max_chars)
    dst = Path(args.out) if args.out else src
    dst.write_text(new_text)
    print(
        f"{dst}: {stats['sparql']} sparql blocks → "
        f"{stats['added']} diagrams added, {stats['already']} already present, "
        f"{stats['unparseable']} unparseable-skipped, {stats['oversized']} oversized-skipped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Re-run the SPARQL embedded in every worked-example transcript.

A transcript is a historical record, but its queries are also a standing claim
that the analysis still reproduces — and nothing else in this repo checks that
claim. The doc builders only read ``crosswalks.json``; ``verify_skeletons.py``
re-runs the catalog's join skeletons, not the prose transcripts that cite them.
So when a KG redeploy moves a namespace, or a crosswalk recipe is repaired, the
transcripts built on the old recipe are left behind SILENTLY: they keep
rendering, keep being linked from the inventory, and keep asserting counts their
own SPARQL no longer returns.

That is not hypothetical. ncipidkg v0.0.2 moved ``owl:sameAs`` off
``http://identifiers.org/uniprot/``, and the two ``proteins02`` transcripts went
on quoting "~12 shared UniProt ids" for two months while their queries returned
0 rows. They were caught by an unrelated schema audit, not by any check. This
script is the tripwire for that class of rot.

WHY ZERO ROWS IS THE FAILURE SIGNAL. Every query in the corpus is a SELECT that
returned rows when it was written — there is no ASK, no CONSTRUCT, and not one
``_0 row(s)_`` marker in any of the 366 files. A transcript query that returns
zero rows today is therefore broken by construction, not merely stale. A
*changed* row count is a much weaker signal (KGs grow between releases), so it
is reported as drift and does not fail the run.

Only about half the corpus records a row count at all: the newer
``create_chat_transcript`` format emits a ``_N row(s)_`` marker under each
query, the older hand-written transcripts do not. Files without markers are
still checked for errors and empty results, which is the part that matters.

Usage:
    uv run python scripts/verify_transcripts.py              # whole corpus (slow)
    uv run python scripts/verify_transcripts.py proteins02   # filter by filename
    uv run python scripts/verify_transcripts.py --problems   # print only failures
    uv run python scripts/verify_transcripts.py --summary    # re-read cached results

Exit status is 1 if any query errored or returned zero rows, so this can gate a
scheduled job. It is deliberately NOT wired into CI: it needs the live
federation endpoint, and a full pass runs ~450 queries against it.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from mcp_okn.sparql import run_sparql

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = ROOT / "docs" / "crosswalks" / "crosswalks_examples"
RESULTS = ROOT / "scripts" / ".transcript_results.json"

#: A fenced ``sparql`` block. Every transcript format uses these, whether or not
#: the file has a ``## SPARQL queries executed`` heading (104 of 366 do not — the
#: older ones jump straight to ``#### Query 1 — ...``), so match the fence itself
#: rather than trying to locate a section.
FENCE = re.compile(r"```sparql\n(.*?)\n```\n", re.S)
#: The row-count marker the transcript builder writes under a query, e.g.
#: ``_12 row(s) — showing first 3_``. Anchored to the text immediately after the
#: closing fence so it cannot pick up a later query's marker.
ROW_MARKER = re.compile(r"\A\s*_(\d+) row\(s\)")

OK, DRIFT, ZERO, ERR = "OK", "DRIFT", "ZERO", "ERR"
FAILING = (ZERO, ERR)


@dataclass
class Check:
    """One SPARQL block from one transcript, plus the verdict on re-running it."""

    stem: str
    index: int
    sparql: str
    expected: int | None
    got: int | None = None
    status: str = ""
    detail: str = ""


@dataclass
class FileReport:
    stem: str
    checks: list[Check] = field(default_factory=list)

    @property
    def failed(self) -> list[Check]:
        return [c for c in self.checks if c.status in FAILING]

    @property
    def drifted(self) -> list[Check]:
        return [c for c in self.checks if c.status == DRIFT]


def parse_transcript(path: Path) -> list[Check]:
    """Extract each SPARQL block and the row count recorded beneath it."""
    text = path.read_text()
    checks: list[Check] = []
    for i, m in enumerate(FENCE.finditer(text), start=1):
        marker = ROW_MARKER.match(text[m.end() : m.end() + 200])
        checks.append(
            Check(
                stem=path.stem,
                index=i,
                sparql=m.group(1),
                expected=int(marker.group(1)) if marker else None,
            )
        )
    return checks


async def run_check(
    check: Check,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    timeout: float,
) -> Check:
    async with sem:
        try:
            r = await run_sparql(check.sparql, timeout=timeout, client=client)
        except Exception as exc:  # any failure is a finding to report, not a crash
            check.status = ERR
            check.detail = str(exc)[:200].replace("\n", " ")
            return check

    check.got = r.get("row_count", len(r.get("rows", [])))
    if check.got == 0:
        # No transcript in the corpus records a 0-row result, so this is broken,
        # not merely stale. Almost always a namespace or IRI-form change that the
        # endpoint reports as an empty result rather than an error.
        check.status = ZERO
    elif check.expected is not None and check.got != check.expected:
        check.status = DRIFT
    else:
        check.status = OK
    return check


def select_files(patterns: list[str]) -> list[Path]:
    files = sorted(TRANSCRIPTS.glob("*.md"))
    if not patterns:
        return files
    return [f for f in files if any(p in f.stem for p in patterns)]


def print_report(reports: list[FileReport], problems_only: bool) -> None:
    for rep in reports:
        interesting = rep.failed or rep.drifted
        if problems_only and not interesting:
            continue
        print(f"\n{rep.stem}")
        for c in rep.checks:
            if problems_only and c.status == OK:
                continue
            exp = "—" if c.expected is None else str(c.expected)
            got = "—" if c.got is None else str(c.got)
            line = f"  {c.status:<5} query {c.index}: got={got} recorded={exp}"
            print(line + (f"  {c.detail}" if c.detail else ""))


def summarize(reports: list[FileReport]) -> int:
    checks = [c for r in reports for c in r.checks]
    by = {s: [c for c in checks if c.status == s] for s in (OK, DRIFT, ZERO, ERR)}
    bad_files = sorted({c.stem for c in by[ZERO] + by[ERR]})

    print(
        f"\n{len(reports)} transcript(s), {len(checks)} quer(ies): "
        f"ok={len(by[OK])} drift={len(by[DRIFT])} zero={len(by[ZERO])} err={len(by[ERR])}"
    )
    if by[DRIFT]:
        print(
            "\ndrift (row count changed — usually the KG grew, review but not a failure):"
        )
        for c in by[DRIFT]:
            print(f"  {c.stem} q{c.index}: {c.expected} -> {c.got}")
    if bad_files:
        print(
            f"\nBROKEN — {len(bad_files)} transcript(s) whose SPARQL no longer works:"
        )
        for stem in bad_files:
            marks = [
                f"q{c.index} {c.status}"
                for c in checks
                if c.stem == stem and c.status in FAILING
            ]
            print(f"  {stem}: {', '.join(marks)}")
        print(
            "\nRegenerate these with create_chat_transcript against the current "
            "recipe — never hand-edit a transcript's queries or results."
        )
        return 1
    print("\nall transcript queries still return rows")
    return 0


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patterns", nargs="*", help="only check filenames containing these")
    ap.add_argument(
        "--jobs", type=int, default=4, help="concurrent queries (default 4)"
    )
    ap.add_argument(
        "--timeout", type=float, default=90.0, help="per-query seconds (default 90)"
    )
    ap.add_argument("--problems", action="store_true", help="print only non-OK queries")
    ap.add_argument(
        "--summary", action="store_true", help="re-read cached results, run nothing"
    )
    args = ap.parse_args()

    if args.summary:
        if not RESULTS.exists():
            print(f"no cached results at {RESULTS} — run without --summary first")
            return 1
        cached = json.loads(RESULTS.read_text())
        reports = [
            FileReport(stem=stem, checks=[Check(**c) for c in checks])
            for stem, checks in cached.items()
        ]
        return summarize(reports)

    files = select_files(args.patterns)
    if not files:
        print(f"no transcripts matched {args.patterns!r} in {TRANSCRIPTS}")
        return 1

    reports = [FileReport(stem=f.stem, checks=parse_transcript(f)) for f in files]
    todo = [c for r in reports for c in r.checks]
    if not todo:
        print(f"{len(files)} file(s) matched but none contain a ```sparql block")
        return 1

    print(
        f"re-running {len(todo)} quer(ies) from {len(files)} transcript(s), "
        f"{args.jobs} at a time — this hits the live federation endpoint"
    )
    started = time.monotonic()
    sem = asyncio.Semaphore(args.jobs)
    async with httpx.AsyncClient(timeout=args.timeout) as client:
        await asyncio.gather(*(run_check(c, client, sem, args.timeout) for c in todo))
    print(f"done in {time.monotonic() - started:.0f}s")

    print_report(reports, args.problems)
    RESULTS.write_text(
        json.dumps(
            {r.stem: [vars(c) for c in r.checks] for r in reports},
            indent=2,
        )
        + "\n"
    )
    print(f"\nwrote results for {len(reports)} transcript(s) to {RESULTS}")
    return summarize(reports)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

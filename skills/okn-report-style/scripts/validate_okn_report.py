#!/usr/bin/env python3
"""
validate_okn_report.py — the ONE blocking, package-level gate for an okn-report-style deliverable.

A complete report is a FOLDER (see SKILL.md "Deliverable set"), and the skill's rules for what may and
may not appear in it were, until this script, enforced only piecemeal by two content-level gates
(`check_report_parity` for the HTML, `readd_query_diagrams --check` for the transcript). Nothing checked
the PACKAGE: that the top-level file set is exactly right, that `data/` holds only machine extracts, that
no anti-pattern builder or scratch/QA artifact leaked in, that the workbook and section order are as
mandated. Working files kept leaking into delivered folders because each defect was only ever caught by
eye. This script closes that: run it on the finished folder and it either PASSes or names every violation.

    python validate_okn_report.py <study_dir>

`<study>` is the folder's own name and every top-level file is prefixed with it (SKILL.md). The token is
derived from the directory basename, so this is domain-neutral — it validates `Bone-Health/`, `SANS/`, or
any study folder identically. Exit code 0 = PASS (no errors), 1 = FAIL (≥1 error). Warnings never fail the
build; they flag things worth a look that aren't hard violations.

It COMPOSES the existing content gates rather than reimplementing them:
  - `build_report_html.check_report_parity`     — HTML is the same report as the .md (headings, words, one
                                                   well-formed doc, consecutive figures).
  - `build_report_html.check_figure_numbering`  — captions/filenames consecutive 1..N (also inside parity).
  - `readd_query_diagrams.check`                — every ```sparql block has a faithful ```mermaid diagram.
And ADDS the package-level checks that had no home: the top-level allowlist, naming prefix, single
reproducibility file, `data/` = flat CSV/TSV/JSON only, `scripts/` anti-pattern rejection, workbook sheet
names, report section order (…Reproducibility → References last), figure file/reference cross-check, and a
recursive scan for QA/temp/scratch junk. Stdlib-only (an .xlsx is a zip — sheet names are read straight
from `xl/workbook.xml`), so it runs wherever a report is built, exactly like the sibling gates.
"""

from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path

# Reuse the sibling skill scripts (present here and copied into every study's scripts/), so this runs
# both from the skill dir and from inside a delivered package. build_report_html is stdlib-only.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_report_html as _brh
import readd_query_diagrams as _rqd

# ── The mandated package (SKILL.md "Deliverable set") ────────────────────────────────────────────────
REQUIRED_FILE_SUFFIXES = [
    "_report.md",
    "_report.html",
    "_results.xlsx",
    "_reproducibility.md",
]
# Present only when §8 (Comparison with prior work) was done — the skill allows §8 to be omitted (stated,
# not silently dropped), in which case there is no companion. Allowed at the top level, never required.
OPTIONAL_FILE_SUFFIXES = ["_literature_comparison.md"]
REQUIRED_DIRS = ["figures", "data", "scripts"]

# data/ holds machine extracts and reproducibility intermediates (SKILL.md: "*.tsv / *.json — intermediate
# extracts (for reproducibility)"). That legitimately includes diagram caches (diagrams.json), mermaid/
# sources, the {{key}} report template, and subset extracts — SANS keeps these and is a clean example. The
# one thing the skill explicitly bars from data/ is the literature comparison (a top-level sibling); genuine
# junk (previews, worklists, temp/QA files, __pycache__) is caught by the recursive junk scan.
DATA_ALLOWED_EXT = {".csv", ".tsv", ".json", ".mmd", ".md", ".txt"}


# scripts/ is "the exact scripts used". The anti-pattern is BEHAVIORAL, not a filename: a script that
# emits the report .html WITHOUT going through build_report_from_markdown is the hand-built
# "highlights-reel" builder that drops sections and fails parity (SKILL.md / failure-modes.md). A thin
# per-study driver that builds the table/KPIs and CALLS build_report_from_markdown is exactly right, even
# if it is named build_html.py — so match on what the script does, never on its name.
def _is_antipattern_builder(text: str) -> bool:
    # The signal is writing the REPORT file (`<study>_report.html`) — a folium MAP script that writes
    # `*_map.html` / `*_iframe.html` is NOT this. A script that touches `_report.html` but goes through
    # build_report_from_markdown is the correct thin driver (SANS/scripts/build_html.py).
    emits_report_html = re.search(r"_report\.html", text) is not None
    uses_renderer = "build_report_from_markdown" in text
    return emits_report_html and not uses_renderer


# QA / temp / scratch junk that must never ship inside the folder.
_JUNK_SUFFIXES = (".tmp", "~", ".queries.json")
_JUNK_SUBSTRINGS = ("_old", "copy")
_JUNK_PREFIXES = ("preview", "worklist", "inspect", "qa_")
_JUNK_EXACT = {".DS_Store"}
_JUNK_DIRS = {"__pycache__"}


def _is_junk(name: str) -> bool:
    if name in _JUNK_EXACT:
        return True
    low = name.lower()
    if any(low.endswith(s) for s in _JUNK_SUFFIXES):
        return True
    if any(s in low for s in _JUNK_SUBSTRINGS):
        return True
    return any(low.startswith(p) for p in _JUNK_PREFIXES)


# ── Report section order (SKILL.md §1..§12) ──────────────────────────────────────────────────────────
# Headings are domain-adapted, so we anchor only on the stable, distinctive ones and check their RELATIVE
# order is monotonic. The two hard rules: Sources must be present, and the last two sections are always
# Reproducibility then References, with nothing after References.
_SECTION_ANCHORS = [  # (canon name, keyword tested as a substring of the normalized heading), in order
    ("sources", "sources"),
    ("comparison", "prior work"),
    ("ranked", "ranked results"),
    ("limitations", "limitations"),
    ("reproducibility", "reproducibility"),
    ("references", "references"),
]


def _norm_heading(text: str) -> str:
    """Lowercase and strip a leading section number (``2.`` / ``5.6``) so ``## 2. Sources used`` and
    ``## Sources used`` normalize the same."""
    return re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text.strip()).lower()


def _level2_headings(md_text: str) -> list[str]:
    """The normalized text of each ``##`` (exactly level-2) heading, in document order — the report's
    section headers. ``###`` subsections are intentionally excluded."""
    out = []
    for line in md_text.splitlines():
        m = re.match(r"^##\s+(.*\S)\s*$", line)  # exactly two hashes
        if m:
            out.append(_norm_heading(m.group(1)))
    return out


class _Report:
    """Accumulates errors (blocking) and warnings (advisory) for one package."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _workbook_sheet_names(xlsx: Path) -> list[str]:
    """Sheet names read straight from the xlsx package (a zip) — no openpyxl needed. Names are
    XML-escaped in the archive (``Methods &amp; Rules``), so unescape them."""
    with zipfile.ZipFile(xlsx) as z:
        wb = z.read("xl/workbook.xml").decode("utf-8")
    return [html.unescape(n) for n in re.findall(r'<sheet\b[^>]*\bname="([^"]*)"', wb)]


def _workbook_has_abbreviations(xlsx: Path) -> bool:
    """True if the text ``abbreviation`` appears anywhere in the workbook cells — a cheap proxy for the
    required Abbreviations row on the Methods & Rules sheet. Cells live either in xl/sharedStrings.xml or
    inline in the worksheet XML (openpyxl uses inline strings), so scan both."""
    with zipfile.ZipFile(xlsx) as z:
        for member in z.namelist():
            if (
                member == "xl/sharedStrings.xml" or member.startswith("xl/worksheets/")
            ) and "abbreviation" in z.read(member).decode("utf-8", "ignore").lower():
                return True
    return False


def _check_toplevel(study: Path, token: str, r: _Report) -> dict:
    """Check the top-level allowlist + naming, and return the resolved required paths for later checks."""
    required_files = {f"{token}{suf}": suf for suf in REQUIRED_FILE_SUFFIXES}
    optional_files = {f"{token}{suf}" for suf in OPTIONAL_FILE_SUFFIXES}
    allowed = set(required_files) | optional_files | set(REQUIRED_DIRS)

    present = {p.name for p in study.iterdir()}
    for fname in required_files:
        fp = study / fname
        if not fp.is_file():
            r.err(f"missing required file: {fname}")
    for d in REQUIRED_DIRS:
        dp = study / d
        if not dp.is_dir():
            r.err(f"missing required directory: {d}/")

    for name in sorted(present):
        entry = study / name
        if name in allowed:
            # A required name that is the wrong kind (dir where a file belongs, or vice-versa).
            if name in required_files and not entry.is_file():
                r.err(f"'{name}' must be a file")
            if name in REQUIRED_DIRS and not entry.is_dir():
                r.err(f"'{name}/' must be a directory")
            continue
        kind = "directory" if entry.is_dir() else "file"
        if entry.is_file() and not name.startswith(f"{token}_"):
            r.err(
                f"unexpected top-level {kind}: '{name}' — not in the allowlist, and its name is not "
                f"prefixed with the study token '{token}_'"
            )
        else:
            r.err(
                f"unexpected top-level {kind}: '{name}' — not in the deliverable allowlist"
            )

    return {
        "report_md": study / f"{token}_report.md",
        "report_html": study / f"{token}_report.html",
        "xlsx": study / f"{token}_results.xlsx",
        "repro_md": study / f"{token}_reproducibility.md",
        "litcomp_md": study / f"{token}_literature_comparison.md",
    }


def _check_single_reproducibility(study: Path, token: str, r: _Report) -> None:
    """Exactly ONE reproducibility file — spec + verbatim queries live together (SKILL.md: "do not split
    them back into two"). Any second reproducibility/transcript/spec file is the split anti-pattern."""
    hits = []
    for p in study.rglob("*"):
        if not p.is_file():
            continue
        low = p.name.lower()
        if any(k in low for k in ("reproducibility", "transcript", "_spec")):
            hits.append(p.relative_to(study).as_posix())
    canonical = f"{token}_reproducibility.md"
    extra = [h for h in hits if Path(h).name != canonical]
    if extra:
        r.err(
            "more than one reproducibility/transcript/spec file — the spec + verbatim queries must be "
            f"ONE file ({canonical}); also found: {', '.join(sorted(extra))}"
        )


def _check_data_dir(study: Path, r: _Report) -> None:
    data = study / "data"
    if not data.is_dir():
        return
    for p in sorted(data.rglob("*")):
        if p.is_dir() or _is_junk(p.name):  # junk handled by the recursive junk scan
            continue
        rel = p.relative_to(study).as_posix()
        # The literature comparison is a top-level sibling deliverable — the skill bars it from data/.
        if p.name.endswith("_literature_comparison.md"):
            r.err(
                f"the literature comparison must be a top-level sibling, not inside data/: {rel}"
            )
            continue
        if p.suffix.lower() not in DATA_ALLOWED_EXT:
            r.warn(
                f"unusual file in data/: {rel} — data/ is for machine extracts / reproducibility "
                f"intermediates ({', '.join(sorted(DATA_ALLOWED_EXT))}); scripts belong in scripts/"
            )


def _check_scripts_dir(study: Path, r: _Report) -> None:
    scripts = study / "scripts"
    if not scripts.is_dir():
        return
    for p in sorted(scripts.rglob("*")):
        if p.suffix != ".py" or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _is_antipattern_builder(text):
            rel = p.relative_to(study).as_posix()
            r.err(
                f"anti-pattern HTML builder in scripts/: {rel} — it emits the report .html WITHOUT "
                "calling build_report_from_markdown, the hand-built highlights-reel that drops sections "
                "and fails parity; render the .html from the .md via build_report_from_markdown instead"
            )


def _check_figures(study: Path, report_md: Path, r: _Report) -> None:
    figs = study / "figures"
    if not (figs.is_dir() and report_md.is_file()):
        return
    # check_figure_numbering already validates consecutiveness (also folded into parity); run it here so
    # the package gate reports it too.
    res = _brh.check_figure_numbering(str(report_md))
    for issue in res.get("issues", []):
        r.err(f"figure numbering: {issue}")

    md = report_md.read_text(encoding="utf-8")
    referenced = set(re.findall(r"figures/(fig\d+_[^)\s\"']*\.png)", md))
    on_disk = {
        p.name
        for p in figs.iterdir()
        if p.is_file() and re.match(r"fig\d+_.*\.png$", p.name)
    }
    for missing in sorted(referenced - on_disk):
        r.err(f"figure referenced in the report but missing on disk: figures/{missing}")
    for orphan in sorted(on_disk - referenced):
        r.err(f"orphan figure on disk, not referenced in the report: figures/{orphan}")


def _check_workbook(xlsx: Path, r: _Report) -> None:
    if not xlsx.is_file():
        return
    try:
        sheets = _workbook_sheet_names(xlsx)
    except (zipfile.BadZipFile, KeyError) as e:
        r.err(f"could not read workbook sheets from {xlsx.name}: {e}")
        return
    for required in ("Ranked Results", "Methods & Rules"):
        if required not in sheets:
            r.err(
                f"workbook {xlsx.name} is missing the required sheet '{required}' "
                f"(has: {', '.join(sheets) or '—'})"
            )
    if "Methods & Rules" in sheets and not _workbook_has_abbreviations(xlsx):
        r.warn(
            f"workbook {xlsx.name}: no 'Abbreviation' text found — the Methods & Rules sheet should "
            "include an Abbreviations row"
        )


def _check_section_order(report_md: Path, r: _Report) -> None:
    if not report_md.is_file():
        return
    headings = _level2_headings(report_md.read_text(encoding="utf-8"))
    if not headings:
        r.err("report has no ## section headings — cannot verify section order")
        return

    # Map each heading to the first anchor whose keyword it contains; keep document order.
    matched = []  # (canon_index, canon_name)
    for h in headings:
        for i, (name, kw) in enumerate(_SECTION_ANCHORS):
            if kw in h:
                matched.append((i, name))
                break
    found_names = {name for _, name in matched}

    if "sources" not in found_names:
        r.err(
            "missing required section: 'Sources used' (§2) — every report must credit its sources"
        )

    # Relative order of recognized anchors must be monotonic (a subsequence of the canonical order).
    idxs = [i for i, _ in matched]
    if idxs != sorted(idxs):
        seq = " → ".join(name for _, name in matched)
        r.err(f"sections are out of the required order: {seq}")

    # The last two SECTION headings must be Reproducibility then References, nothing after References.
    if "reproducibility" not in found_names or "references" not in found_names:
        r.err(
            "the report must end with '## Reproducibility' then '## References' (§11, §12)"
        )
    else:
        if (
            headings[-1] != _norm_heading("references")
            and "references" not in headings[-1]
        ):
            r.err(
                f"'References' is not the last section — the last heading is '{headings[-1]}'; "
                "nothing may follow References"
            )
        if "reproducibility" not in headings[-2]:
            r.err(
                "'Reproducibility' must be the second-to-last section, immediately before References — "
                f"but the second-to-last heading is '{headings[-2]}'"
            )


def _check_junk(study: Path, r: _Report) -> None:
    """Recursive scan of the subdirectories for QA/temp/scratch junk (the top level is covered by the
    allowlist). __pycache__ is gitignored/excluded from the skill zip but must not ship in a package."""
    for d in REQUIRED_DIRS:
        base = study / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            name = p.name
            if p.is_dir() and name in _JUNK_DIRS:
                r.err(
                    f"scratch/QA artifact in the package: {p.relative_to(study).as_posix()}/"
                )
            elif p.is_file() and _is_junk(name):
                r.err(
                    f"scratch/QA/temp file in the package: {p.relative_to(study).as_posix()}"
                )


def _check_parity(paths: dict, r: _Report) -> None:
    md, htmlp = paths["report_md"], paths["report_html"]
    if md.is_file() and htmlp.is_file():
        res = _brh.check_report_parity(str(md), str(htmlp))
        if not res["ok"]:
            missing = res.get("missing_sections") or []
            detail = f" — missing/short: {', '.join(missing)}" if missing else ""
            r.err(
                f"HTML/Markdown parity FAILED (see [check_report_parity] line){detail}"
            )


def _check_diagrams(paths: dict, r: _Report) -> None:
    repro = paths["repro_md"]
    if repro.is_file():
        code = _rqd.check(repro, repro.read_text(encoding="utf-8"))
        if code != 0:
            r.err(
                "SPARQL→Mermaid gate FAILED (see [readd_query_diagrams] line) — every ```sparql block "
                "must have a faithful ```mermaid diagram and no stale warning notice"
            )


def validate(study_dir: str) -> _Report:
    study = Path(study_dir)
    r = _Report()
    if not study.is_dir():
        r.err(f"not a directory: {study_dir}")
        return r
    token = study.name

    paths = _check_toplevel(study, token, r)
    _check_single_reproducibility(study, token, r)
    _check_data_dir(study, r)
    _check_scripts_dir(study, r)
    _check_figures(study, paths["report_md"], r)
    _check_workbook(paths["xlsx"], r)
    _check_section_order(paths["report_md"], r)
    _check_junk(study, r)
    # Content gates last (they each print their own PASS/FAIL line).
    _check_parity(paths, r)
    _check_diagrams(paths, r)
    return r


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print("usage: python validate_okn_report.py <study_dir>", file=sys.stderr)
        return 2
    study_dir = argv[0].rstrip("/")
    r = validate(study_dir)

    for w in r.warnings:
        print(f"  [warn] {w}")
    token = Path(study_dir).name
    if r.errors:
        print(f"[validate_okn_report] FAIL: {len(r.errors)} error(s) in {token}/")
        for e in r.errors:
            print(f"  - {e}")
        return 1
    extra = f" ({len(r.warnings)} warning(s))" if r.warnings else ""
    print(
        f"[validate_okn_report] PASS: {token}/ is a compliant okn-report-style package{extra}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

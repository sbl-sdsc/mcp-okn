#!/usr/bin/env python3
"""
validate_okn_report.py — the ONE blocking, package-level gate for an okn-report-style deliverable.

A complete report is a FOLDER (see SKILL.md "Deliverable set"), and the skill's rules for what may and
may not appear in it were, until this script, enforced only piecemeal by a content-level gate
(`check_report_parity` for the HTML). Nothing checked
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
And ADDS the package-level checks that had no home: the top-level allowlist, naming prefix, the
`<study>_notebook/` reproducibility folder from `create_jupyter_notebook` (complete, executed to HTML, and
not shadowed by a stale `_reproducibility.md` / transcript / spec), `data/` = flat CSV/TSV/JSON only,
`scripts/` anti-pattern rejection, workbook sheet names, report section order (…Reproducibility →
References last), the notebook header's `Skills` provenance line, an exact model id recorded identically
in the .md / .html / notebook, figure
file/reference cross-check, a recursive scan for QA/temp/scratch junk, and no map tiles from OpenStreetMap's
own server (blocked when the report is opened from disk) and no plotly tile maps (blank from disk).
Stdlib-only (an .xlsx is a zip — sheet names are read straight from `xl/workbook.xml`), so it runs
wherever a report is built, exactly like the sibling gates.
"""

from __future__ import annotations

import html
import json
import re
import sys
import zipfile
from pathlib import Path

# Reuse the sibling skill scripts (present here and copied into every study's scripts/), so this runs
# both from the skill dir and from inside a delivered package. build_report_html is stdlib-only.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_report_html as _brh

# ── The mandated package (SKILL.md "Deliverable set") ────────────────────────────────────────────────
REQUIRED_FILE_SUFFIXES = [
    "_report.md",
    "_report.html",
    "_results.xlsx",
]
# Present only when §8 (Comparison with prior work) was done — the skill allows §8 to be omitted (stated,
# not silently dropped), in which case there is no companion. Allowed at the top level, never required.
OPTIONAL_FILE_SUFFIXES = ["_literature_comparison.md"]
REQUIRED_DIRS = ["figures", "data", "scripts"]

# The reproducibility record is the folder `create_jupyter_notebook(folder_name="<study>_notebook")`
# builds: the notebook, its query files, the cached rows, the helper module — plus the HTML page the
# caller renders with the tool's `html_command`. These are the files that make it re-runnable.
NOTEBOOK_SUFFIX = "_notebook"
NOTEBOOK_REQUIRED = ["okn_sparql.py", "requirements.txt", "queries/manifest.json"]

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
_JUNK_DIRS = {"__pycache__", ".ipynb_checkpoints"}


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


# ── The notebook header (the first cell create_jupyter_notebook writes) ──────────────────────────────
# `skills=` and `model=` are the two header fields the server cannot derive on its own: it knows its own
# version, the endpoint and the query log, but NOT which skills the session loaded and NOT which model is
# calling it — `model` is a caller-supplied string it stores verbatim without inspecting. So an absent
# `- **Skills:**` line means the tool call omitted the argument — the header is generated and saved
# verbatim, so it cannot go missing any other way — and the record then silently claims no methodology.
# This is checkable precisely because the validator only ever runs on an okn-report-style package: that
# skill was used BY DEFINITION, so the line must exist and must name it.
_SKILLS_LINE = re.compile(r"^-\s+\*\*Skills:\*\*[ \t]*(.+?)[ \t]*$", re.M)
_VERSIONED = re.compile(r"\sv\d+(?:\.\d+)*\b")  # the " v1.2.3" in "<skill> v1.2.3"

# ── Model provenance (SKILL.md "Exact model provenance") ─────────────────────────────────────────────
# The model id is written into THREE artifacts by three different paths — hand-authored in the report
# `.md` title block, lifted verbatim from that line into the `.html` header by build_report_from_markdown,
# and passed as `create_jupyter_notebook(model=…)` into the notebook header — and NOTHING reconciles
# them. Nor does anything check the value itself: the server stores whatever string it is handed, so a
# family name ("Claude"), a product name, an inferred id, or a placeholder is indistinguishable from the
# real thing. Reproducibility metadata that names the wrong model is worse than none, so this gate
# requires all three to be present, specific, and identical.
#
# Matched markup-agnostically (`**Model:** x` in Markdown, `<strong>Model:</strong> x` in HTML once tags
# are stripped) and stopping at the `·` / `|` that separate the title block's other meta fields.
_MODEL_VALUE = re.compile(r"Model:\s*(?:\*\*)?[ \t]*([^\n·|]+)")
_TAGS = re.compile(r"<[^>]+>")
# Bare family / product names and placeholders: specific enough to look filled in, too generic to
# identify what actually ran. Compared case-insensitively against the whole value.
_GENERIC_MODELS = {
    "",
    "claude",
    "anthropic",
    "anthropic model",
    "opus",
    "sonnet",
    "haiku",
    "gpt",
    "gpt-4",
    "gpt-5",
    "chatgpt",
    "codex",
    "openai",
    "openai model",
    "gemini",
    "llama",
    "mistral",
    "grok",
    "llm",
    "model",
    "<model>",
    "latest model",
    "latest",
    "unknown",
    "n/a",
    "na",
    "none",
    "tbd",
    "todo",
}


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
    notebook_dir = f"{token}{NOTEBOOK_SUFFIX}"
    required_dirs = [*REQUIRED_DIRS, notebook_dir]
    allowed = set(required_files) | optional_files | set(required_dirs)

    present = {p.name for p in study.iterdir()}
    for fname in required_files:
        fp = study / fname
        if not fp.is_file():
            r.err(f"missing required file: {fname}")
    for d in required_dirs:
        dp = study / d
        if not dp.is_dir() and d == notebook_dir:
            r.err(
                f"missing required directory: {d}/ — the reproducibility notebook; build it with "
                f"create_jupyter_notebook(folder_name='{notebook_dir}', ...) into this folder"
            )
        elif not dp.is_dir():
            r.err(f"missing required directory: {d}/")

    for name in sorted(present):
        entry = study / name
        if name in allowed:
            # A required name that is the wrong kind (dir where a file belongs, or vice-versa).
            if name in required_files and not entry.is_file():
                r.err(f"'{name}' must be a file")
            if name in required_dirs and not entry.is_dir():
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
        "litcomp_md": study / f"{token}_literature_comparison.md",
        "notebook_dir": study / notebook_dir,
        "notebook": study / notebook_dir / f"{notebook_dir}.ipynb",
        "notebook_html": study / notebook_dir / f"{notebook_dir}.html",
    }


#: Names of a prose record that the notebook folder replaces. `_spec` needs the lookahead: a bare
#: substring test matched `_species`, so a study with `wl_species_summary.csv` in `data/` failed on a CSV.
#: `transcript` deliberately has no lookahead — a plural `_transcripts.md` is caught too.
_SPLIT_DOC_RE = re.compile(r"reproducibility|transcript|_spec(?![a-z])", re.I)

#: Only prose documents can BE a spec or a record; data and figures never are.
_DOC_SUFFIXES = {".md", ".html", ".htm", ".txt", ".pdf", ".docx"}


def _check_single_record(study: Path, r: _Report) -> None:
    """The notebook folder is the ONE reproducibility record. A `_reproducibility.md`, a transcript or a
    separate spec document beside it is a second copy of the queries and the spec, which drifts from the
    first — the spec belongs in the notebook's markdown cells."""
    hits = sorted(
        p.relative_to(study).as_posix()
        for p in study.rglob("*")
        if p.is_file()
        and p.suffix.lower() in _DOC_SUFFIXES
        and _SPLIT_DOC_RE.search(p.name)
    )
    if hits:
        r.err(
            "a second reproducibility/transcript/spec document — the notebook folder is the record "
            "(queries, results, spec in its markdown cells); remove: " + ", ".join(hits)
        )


def _notebook_cells(nb_path: Path) -> list[dict] | None:
    """The notebook's cells, or None when the file is not a readable nbformat-4 notebook."""
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    cells = nb.get("cells") if isinstance(nb, dict) else None
    if not isinstance(cells, list) or nb.get("nbformat") != 4:
        return None
    return cells


def _cell_text(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else str(src)


def _notebook_header(nb_path: Path) -> str | None:
    """The provenance header: the notebook's FIRST cell, as create_jupyter_notebook writes it, cut at its
    first ``##`` (Prompt / Notes follow there). None when the notebook is unreadable or starts otherwise."""
    cells = _notebook_cells(nb_path) if nb_path.is_file() else None
    if not cells or cells[0].get("cell_type") != "markdown":
        return None
    return re.split(r"^##\s", _cell_text(cells[0]), maxsplit=1, flags=re.M)[0]


def _check_notebook(paths: dict, r: _Report) -> None:
    """The notebook folder is complete, re-runnable, and rendered.

    Hosted servers hand the folder back as a file map that the agent saves, so a file can be missed or
    an image never copied; this catches both. The HTML is the executed notebook (`html_command`), which
    the tool cannot make itself; a page older than the notebook was rendered before its last edit.
    """
    nb_dir, nb = paths["notebook_dir"], paths["notebook"]
    if not nb_dir.is_dir():
        return  # already a top-level error
    label = nb_dir.name
    if not nb.is_file():
        r.err(
            f"{label}/: missing the notebook {nb.name} — pass folder_name='{label}' so the notebook "
            "is named after its folder"
        )
        return
    cells = _notebook_cells(nb)
    if cells is None:
        r.err(
            f"{label}/{nb.name} is not a valid nbformat-4 notebook — save the tool's file verbatim"
        )
        return
    for rel in NOTEBOOK_REQUIRED:
        if not (nb_dir / rel).is_file():
            r.err(
                f"{label}/: missing {rel} — save every entry of the tool's `files` verbatim"
            )

    manifest_path = nb_dir / "queries" / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except ValueError:
            manifest = None
        if not isinstance(manifest, list):
            r.err(
                f"{label}/queries/manifest.json is not the tool's query list — save it verbatim"
            )
        elif not manifest:
            r.err(
                f"{label}/: the notebook records no queries — every finding needs a logged, "
                "non-exploratory query behind it; check `scope=` and the session log"
            )
        else:
            for q in manifest:
                if not isinstance(q, dict):
                    continue
                for rel in (f"queries/{q.get('name')}.rq", q.get("cache")):
                    if rel and not (nb_dir / rel).is_file():
                        r.err(
                            f"{label}/: missing {rel} (listed in queries/manifest.json)"
                        )

    # Figures the notebook embeds (`![caption](figures/x.png)`) must be in its folder.
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        for dest in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", _cell_text(cell)):
            if (
                not re.match(r"(?:https?:|data:)", dest)
                and not (nb_dir / dest).is_file()
            ):
                r.err(
                    f"{label}/: the notebook shows {dest}, which is not in the folder — copy each "
                    "`figures_to_copy` image to its path"
                )

    html_path = paths["notebook_html"]
    if not html_path.is_file():
        r.err(
            f"{label}/: missing {html_path.name} — run the tool's `html_command` (it executes the "
            "notebook from the cached rows and writes the page beside it)"
        )
    elif html_path.stat().st_mtime < nb.stat().st_mtime:
        r.warn(
            f"{label}/{html_path.name} is older than the notebook — re-run `html_command` so the page "
            "shows the current version"
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


def _check_repro_skills(nb_path: Path, r: _Report) -> None:
    """The notebook header must record the skills the run followed.

    Only the HEADER counts (the first cell, above its first ``##``): the line is provenance, and a
    mention down in the spec or a query description is not the tool-generated header field. Naming
    `okn-report-style` is mandatory — this validator is running, so the package was built with it. An
    entry carrying no version is a warning, not an error: it still identifies the methodology, it just
    doesn't pin it.
    """
    header = _notebook_header(nb_path)
    if header is None:
        return  # a missing or unreadable notebook is already an error
    label = nb_path.name
    m = _SKILLS_LINE.search(header)
    if not m:
        r.err(
            f"{label}: the header has no '- **Skills:**' line — pass `skills=[...]` to "
            "create_jupyter_notebook (e.g. `skills=['okn-bioanalysis v0.1.3', "
            "'okn-report-style v0.2.2']`, versions from each skill's frontmatter `metadata.version`). "
            "The server cannot see which skills your session loaded, so an omitted list leaves the "
            "record claiming no methodology at all; do NOT hand-edit the cell — regenerate the notebook"
        )
        return
    entries = [e.strip() for e in m.group(1).split("·") if e.strip()]
    if not any(e.startswith("okn-report-style") for e in entries):
        r.err(
            f"{label}: the header's Skills line does not name okn-report-style "
            f"(has: {', '.join(entries) or '—'}) — this package was built with it, so it belongs in "
            "the record; add it to `skills=` and regenerate"
        )
    unversioned = [e for e in entries if not _VERSIONED.search(e)]
    if unversioned:
        r.warn(
            f"{label}: Skills entries without a version: {', '.join(unversioned)} — give each "
            "as '<name> v<version>' (from the skill's frontmatter `metadata.version`) so the "
            "methodology is pinned, not just named"
        )


def _model_in(text: str, *, header_only: bool) -> str | None:
    """The model id recorded in one artifact, or None if there is no `Model:` field at all.

    `header_only` slices to the provenance block (everything above the first ``##``) for the two
    Markdown files, so a `Model:` mentioned down in the prose or a query description can never stand in
    for the real field. HTML has no ``##``, so it is searched whole after its tags are stripped — which
    is what makes the match builder-agnostic rather than tied to `<strong>`.
    """
    if header_only:
        text = re.split(r"^##\s", text, maxsplit=1, flags=re.M)[0]
    else:
        text = _TAGS.sub(" ", text)
    m = _MODEL_VALUE.search(text)
    return m.group(1).strip().strip("*").strip() if m else None


def _check_model(paths: dict, r: _Report) -> None:
    """The report `.md`, the report `.html`, and the notebook header must all name the SAME
    exact model id, and it must actually identify a model.

    Three separate authoring paths write this value (see the `_MODEL_VALUE` note above), so the gate is
    a three-way reconciliation plus a specificity test. A value is rejected when it is a bare family or
    product name from `_GENERIC_MODELS`, or when it carries no version token at all — "claude-opus-5"
    and "gpt-5.6-sol" identify a run; "Claude" and "the latest model" do not.
    """
    texts = []
    for label, path, header_only in (
        ("report .md", paths["report_md"], True),
        ("report .html", paths["report_html"], False),
    ):
        if path.is_file():  # a missing artifact is already a top-level error
            texts.append(
                (label, path.read_text(encoding="utf-8", errors="ignore"), header_only)
            )
    nb_header = _notebook_header(paths["notebook"])
    if nb_header is not None:
        texts.append((paths["notebook"].name, nb_header, True))

    found: dict[str, str] = {}
    for label, text, header_only in texts:
        value = _model_in(text, header_only=header_only)
        if value is None:
            r.err(
                f"{label}: no model recorded — the title block needs "
                "'**Date:** … · **Endpoint:** … · **Model:** <exact model id>' and the notebook needs a "
                "'- **Model:**' line from `create_jupyter_notebook(model=...)`. Record the exact "
                "runtime model identifier from session metadata (e.g. `claude-opus-5`); if you cannot "
                "determine it, ASK the user rather than guessing or omitting it"
            )
            continue
        found[label] = value

    for label, value in found.items():
        if value.lower() in _GENERIC_MODELS or not any(c.isdigit() for c in value):
            r.err(
                f"{label}: '{value}' is a model family or product name, not an exact model id — record "
                "the exact runtime identifier from session metadata (`claude-opus-5`, `gpt-5.6-sol`), "
                "never a family name, a product name, or one inferred from wording like 'based on "
                "GPT-5'. If it is unavailable or ambiguous, ASK the user for it"
            )

    distinct = set(found.values())
    if len(distinct) > 1:
        detail = " · ".join(f"{label}: '{value}'" for label, value in found.items())
        r.err(
            f"the recorded model differs across the package ({detail}) — the Markdown title block, the "
            "rendered HTML header, and the notebook header must carry the IDENTICAL identifier"
        )


def _check_junk(study: Path, r: _Report) -> None:
    """Recursive scan of the subdirectories for QA/temp/scratch junk (the top level is covered by the
    allowlist). __pycache__ is gitignored/excluded from the skill zip but must not ship in a package;
    running the notebook in Jupyter leaves one (and .ipynb_checkpoints/) in the notebook folder."""
    for d in [*REQUIRED_DIRS, f"{study.name}{NOTEBOOK_SUFFIX}"]:
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


#: OpenStreetMap's own tile server. It answers requests without an HTTP Referer with an "Access blocked"
#: image (HTTP 200), and a report opened from disk (file://) sends none — so a map built on it renders fine
#: once hosted but shows "Access blocked" in every tile locally. Matches the URL inside an escaped
#: `<iframe srcdoc>` too. Use okn_figstyle.BASEMAP_TILES (Esri World Street Map) instead.
_OSM_TILE_RE = re.compile(r"tile\.openstreetmap\.org", re.I)


#: plotly's tile-map traces (MapLibre since plotly 6; the `*mapbox` names are the older Mapbox GL ones).
#: Both start a WebGL web worker that never loads from a file:// page or a notebook's iframe, so the
#: figure shows only its colour bar and attribution over a blank map. Plotly's `choropleth` /
#: `scattergeo` (SVG) render, but have no street basemap either. Use folium on BASEMAP_TILES.
_PLOTLY_TILE_TRACES = r"(?:choropleth|scatter|density)map(?:box)?"
_PLOTLY_TYPE_RE = re.compile(
    r'\\?"type\\?"\s*:\s*\\?"(' + _PLOTLY_TILE_TRACES + r')\\?"'
)


def _plotly_tile_traces(text: str) -> set[str]:
    """Tile-map trace types drawn in an HTML page (or HTML-in-JSON string).

    Every plotly figure carries a template that styles each trace type by name (compact JSON:
    `"scattermap":[{"type":"scattermap",…`), so a bar chart's page mentions `scattermap` too; a
    `"type"` that opens such a template entry is not a drawn trace and is skipped."""
    found = set()
    for m in _PLOTLY_TYPE_RE.finditer(text):
        name = m.group(1)
        before = text[max(0, m.start() - 80) : m.start()]
        if re.search(r'\\?"' + name + r'\\?"\s*:\s*\[\s*\{\s*$', before):
            continue
        found.add(name)
    return found


def _notebook_plotly_tile_traces(nb: Path) -> set[str]:
    """Tile-map traces in a notebook's saved outputs (plotly JSON and its HTML fallback)."""
    try:
        cells = json.loads(nb.read_text(encoding="utf-8")).get("cells", [])
    except (OSError, ValueError):
        return set()
    found: set[str] = set()
    for cell in cells:
        for out in cell.get("outputs", []) or []:
            data = out.get("data") or {}
            fig = data.get("application/vnd.plotly.v1+json")
            if isinstance(fig, dict):
                for trace in fig.get("data") or []:
                    t = trace.get("type", "") if isinstance(trace, dict) else ""
                    if re.fullmatch(_PLOTLY_TILE_TRACES, t):
                        found.add(t)
            page = data.get("text/html")
            if page:
                found |= _plotly_tile_traces(
                    "".join(page) if isinstance(page, list) else str(page)
                )
    return found


def _check_basemap(study: Path, paths: dict, r: _Report) -> None:
    nb_dir = paths["notebook_dir"]
    nb_files = (
        [
            p
            for p in sorted(nb_dir.rglob("*"))
            if p.suffix in (".html", ".ipynb")
            and not any(part in _JUNK_DIRS for part in p.relative_to(nb_dir).parts)
        ]
        if nb_dir.is_dir()
        else []
    )
    pages = [
        paths["report_html"],
        *sorted((study / "figures").glob("*.html")),
        *nb_files,
    ]
    for h in pages:
        if not h.is_file():
            continue
        rel = h.relative_to(study).as_posix()
        text = h.read_text(encoding="utf-8")
        if _OSM_TILE_RE.search(text):
            r.err(
                f"{rel} loads tiles from tile.openstreetmap.org, which shows "
                "'Access blocked' when the report is opened from disk — rebuild the map with "
                "okn_figstyle.BASEMAP_TILES / BASEMAP_ATTR (folium_osm_map's default)"
            )
        traces = (
            _notebook_plotly_tile_traces(h)
            if h.suffix == ".ipynb"
            # A map inlined with folium_map_iframe sits HTML-escaped in srcdoc; unescape to see it.
            else _plotly_tile_traces(html.unescape(text))
        )
        if traces:
            r.err(
                f"{rel} draws a plotly tile map ({', '.join(sorted(traces))}) — plotly's MapLibre/Mapbox "
                "map traces render an empty map when opened from disk or inside a notebook iframe; "
                "rebuild it with folium on okn_figstyle.BASEMAP_TILES (folium_osm_map for points, "
                "folium.Map + GeoJson for a choropleth)"
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


def validate(study_dir: str) -> _Report:
    study = Path(study_dir)
    r = _Report()
    if not study.is_dir():
        r.err(f"not a directory: {study_dir}")
        return r
    token = study.name

    paths = _check_toplevel(study, token, r)
    _check_single_record(study, r)
    _check_notebook(paths, r)
    _check_data_dir(study, r)
    _check_scripts_dir(study, r)
    _check_figures(study, paths["report_md"], r)
    _check_workbook(paths["xlsx"], r)
    _check_section_order(paths["report_md"], r)
    _check_repro_skills(paths["notebook"], r)
    _check_model(paths, r)
    _check_junk(study, r)
    _check_basemap(study, paths, r)
    # Content gate last (it prints its own PASS/FAIL line).
    _check_parity(paths, r)
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

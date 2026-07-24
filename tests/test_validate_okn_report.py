"""Tests for the package-level report gate (validate_okn_report).

The skill mandates an exact deliverable folder — a fixed top-level file set, flat machine-extract data/,
no anti-pattern builders or scratch/QA artifacts, a workbook with named sheets, and a section order that
ends Reproducibility → References. This is the automated gate that enforces all of that at once; here we
build a minimal COMPLIANT package (which must PASS) and then inject one violation at a time, asserting
each is caught."""

import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

# validate_okn_report is a report-style skill script (stdlib-only), not part of the mcp_okn package.
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "skills/okn-report-style/scripts")
)
import validate_okn_report as v  # noqa: E402

TOKEN = "Demo"

# A minimal report whose ## sections satisfy the order rules: Sources present, and the last two sections
# are Reproducibility then References.
_REPORT_MD = """# Demo study

> Unit of analysis: demo. Coverage: demo. Abbreviations: n/a.

## Executive summary

The headline result is a demonstration with enough prose to clear the parity word-ratio floor easily.

## Sources used

One row per knowledge graph actually queried in this demonstration package for the parity gate.

## Comparison with prior work

Concordance of each demonstration claim against the imaginary prior literature for this fixture.

## Full ranked results

<!-- RESULTS_TABLE -->

![Figure 1](figures/fig1_demo.png)

> ***Figure 1. A demonstration panel showing nothing in particular for the fixture package.***

## Summary of findings & limitations

A recap of the demonstration findings followed by the usual caveats for a fixture of this kind.

## Reproducibility

See Demo_reproducibility.md for the spec and verbatim queries backing this demonstration package.

## References

1. Demo Author, et al. A demonstration. *Demo Journal*. 2026.
"""


def _md_to_html(md: str) -> str:
    """A trivial, parity-passing render: strip Markdown markup and wrap each line in <p> inside ONE
    well-formed document, so every heading text is present and the visible word count matches the .md."""
    body = []
    for line in md.splitlines():
        s = re.sub(r"^[#>\s]+", "", line).replace("*", "").strip()
        if s:
            body.append(f"<p>{escape(s)}</p>")
    return (
        "<!DOCTYPE html><html><head><title>Demo</title></head><body>\n"
        + "\n".join(body)
        + "\n</body></html>"
    )


def _write_xlsx(path: Path, sheets=("Ranked Results", "Methods & Rules"), abbrev=True) -> None:
    """A minimal xlsx (a zip) carrying just what the validator reads: sheet names in xl/workbook.xml and,
    optionally, the word 'Abbreviations' as an inline cell string."""
    sheets_xml = "".join(
        f'<sheet name="{escape(n)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>'
        for i, n in enumerate(sheets)
    )
    workbook = (
        '<?xml version="1.0"?><workbook '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets_xml}</sheets></workbook>"
    )
    cell = "<row><c t=\"inlineStr\"><is><t>Abbreviations</t></is></c></row>" if abbrev else ""
    ws = f"<worksheet><sheetData>{cell}</sheetData></worksheet>"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/worksheets/sheet1.xml", ws)


def _build(tmp_path: Path) -> Path:
    """Create a fully compliant Demo/ package under tmp_path and return its path."""
    study = tmp_path / TOKEN
    (study / "figures").mkdir(parents=True)
    (study / "data").mkdir()
    (study / "scripts").mkdir()

    (study / f"{TOKEN}_report.md").write_text(_REPORT_MD)
    (study / f"{TOKEN}_report.html").write_text(_md_to_html(_REPORT_MD))
    (study / f"{TOKEN}_literature_comparison.md").write_text("# Lit comparison\n\n1. Demo. 2026.\n")
    # No ```sparql blocks → the diagram gate passes trivially (nothing to diagram).
    (study / f"{TOKEN}_reproducibility.md").write_text("# Reproducibility\n\nSpec and queries.\n")
    _write_xlsx(study / f"{TOKEN}_results.xlsx")

    (study / "figures" / "fig1_demo.png").write_bytes(b"\x89PNG\r\n")
    (study / "data" / "ranked.csv").write_text("id,score\n1,0.9\n")
    (study / "scripts" / "make_figures.py").write_text("# demo\n")
    return study


def test_valid_package_passes(tmp_path):
    study = _build(tmp_path)
    r = v.validate(str(study))
    assert r.errors == [], r.errors
    assert v.main([str(study)]) == 0


def test_missing_literature_comparison_passes(tmp_path):
    # The companion is OPTIONAL — absent when §8 (Comparison with prior work) wasn't done.
    study = _build(tmp_path)
    (study / f"{TOKEN}_literature_comparison.md").unlink()
    r = v.validate(str(study))
    assert r.errors == [], r.errors


def test_unexpected_toplevel_file_fails(tmp_path):
    study = _build(tmp_path)
    (study / "notes.txt").write_text("stray")
    r = v.validate(str(study))
    assert any("unexpected top-level" in e for e in r.errors)
    assert v.main([str(study)]) == 1


def test_missing_required_file_fails(tmp_path):
    study = _build(tmp_path)
    (study / f"{TOKEN}_results.xlsx").unlink()
    r = v.validate(str(study))
    assert any("missing required file" in e for e in r.errors)


def test_data_reproducibility_intermediates_pass(tmp_path):
    # Diagram cache, mermaid/ sources, the {{key}} template, and subset extracts are legitimate
    # reproducibility intermediates (SANS keeps them) — they must NOT be errors.
    study = _build(tmp_path)
    (study / "data" / "diagrams.json").write_text("[]")
    (study / "data" / "mermaid").mkdir()
    (study / "data" / "mermaid" / "1.mmd").write_text("graph TD;")
    (study / "data" / "report_template.md").write_text("# {{title}}\n")
    (study / "data" / "de_ocular_small.csv").write_text("id\n1\n")
    r = v.validate(str(study))
    assert r.errors == [], r.errors


def test_data_literature_comparison_misplaced_fails(tmp_path):
    # The one thing the skill explicitly bars from data/: the literature comparison (a top-level sibling).
    study = _build(tmp_path)
    (study / "data" / f"{TOKEN}_literature_comparison.md").write_text("# stray\n")
    r = v.validate(str(study))
    assert any("literature comparison" in e for e in r.errors)


def test_scripts_antipattern_builder_fails(tmp_path):
    # The anti-pattern is BEHAVIORAL: it writes the report .html without the renderer.
    study = _build(tmp_path)
    (study / "scripts" / "make_html.py").write_text(
        "body = ['<h1>highlights</h1>']\n"
        "open('Demo_report.html', 'w').write('<html>' + ''.join(body) + '</html>')\n"
    )
    r = v.validate(str(study))
    assert any("anti-pattern" in e for e in r.errors)


def test_renderer_driver_named_build_html_passes(tmp_path):
    # A thin per-study driver that CALLS build_report_from_markdown is correct even named build_html.py
    # (this is exactly SANS/scripts/build_html.py) — it must NOT be flagged.
    study = _build(tmp_path)
    (study / "scripts" / "build_html.py").write_text(
        "from build_report_html import build_report_from_markdown, candidate_table\n"
        "build_report_from_markdown('Demo_report.md', 'Demo_report.html', table=None)\n"
    )
    r = v.validate(str(study))
    assert not any("anti-pattern" in e for e in r.errors), r.errors


def test_missing_workbook_sheet_fails(tmp_path):
    study = _build(tmp_path)
    _write_xlsx(study / f"{TOKEN}_results.xlsx", sheets=("Ranked Results",))  # drop Methods & Rules
    r = v.validate(str(study))
    assert any("Methods & Rules" in e for e in r.errors)


def test_workbook_missing_abbreviations_warns(tmp_path):
    study = _build(tmp_path)
    _write_xlsx(study / f"{TOKEN}_results.xlsx", abbrev=False)
    r = v.validate(str(study))
    assert r.errors == []  # a warning, not an error
    assert any("Abbreviation" in w for w in r.warnings)


def test_section_order_references_not_last_fails(tmp_path):
    study = _build(tmp_path)
    md = _REPORT_MD + "\n## Appendix\n\nSomething after References.\n"
    (study / f"{TOKEN}_report.md").write_text(md)
    (study / f"{TOKEN}_report.html").write_text(_md_to_html(md))
    r = v.validate(str(study))
    assert any("References" in e and "last" in e for e in r.errors)


def test_reproducibility_and_references_swapped_fails(tmp_path):
    study = _build(tmp_path)
    md = _REPORT_MD.replace(
        "## Reproducibility\n\nSee Demo_reproducibility.md for the spec and verbatim queries backing this demonstration package.\n\n## References\n\n1. Demo Author, et al. A demonstration. *Demo Journal*. 2026.\n",
        "## References\n\n1. Demo Author, et al. A demonstration. *Demo Journal*. 2026.\n\n## Reproducibility\n\nSee Demo_reproducibility.md for the spec and verbatim queries.\n",
    )
    assert md != _REPORT_MD  # guard: the replace actually fired
    (study / f"{TOKEN}_report.md").write_text(md)
    (study / f"{TOKEN}_report.html").write_text(_md_to_html(md))
    r = v.validate(str(study))
    assert r.errors  # order / last-two rule violated


def test_duplicate_reproducibility_file_fails(tmp_path):
    study = _build(tmp_path)
    (study / f"{TOKEN}_transcript.md").write_text("# stray transcript\n")
    r = v.validate(str(study))
    # Caught either as a split-reproducibility error or as an unexpected top-level file — both are correct.
    assert any("reproducibility" in e.lower() or "transcript" in e.lower() for e in r.errors)


def test_junk_file_in_subdir_fails(tmp_path):
    study = _build(tmp_path)
    (study / "data" / "scratch.tmp").write_text("junk")
    r = v.validate(str(study))
    assert any("scratch/QA/temp" in e for e in r.errors)

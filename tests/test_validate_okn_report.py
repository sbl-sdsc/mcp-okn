"""Tests for the package-level report gate (validate_okn_report).

The skill mandates an exact deliverable folder — a fixed top-level file set, flat machine-extract data/,
no anti-pattern builders or scratch/QA artifacts, a workbook with named sheets, and a section order that
ends Reproducibility → References. This is the automated gate that enforces all of that at once; here we
build a minimal COMPLIANT package (which must PASS) and then inject one violation at a time, asserting
each is caught. The reproducibility notebook in the fixture is built by the real
`mcp_okn.notebook.build_study`, so the gate is tested against what `create_jupyter_notebook` writes."""

import json
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

# validate_okn_report is a report-style skill script (stdlib-only), not part of the mcp_okn package.
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "skills/okn-report-style/scripts")
)
import validate_okn_report as v

from mcp_okn import session
from mcp_okn.notebook import build_study

TOKEN = "Demo"
NB = f"{TOKEN}_notebook"

# A minimal report whose ## sections satisfy the order rules: Sources present, and the last two sections
# are Reproducibility then References.
_REPORT_MD = """# Demo study

**Date:** 2026-07-25 · **Endpoint:** OKN federated SPARQL · **Model:** claude-opus-5

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

Everything needed to rerun the analysis is in the Demo_notebook folder backing this demonstration package.

## References

1. Demo Author, et al. A demonstration. *Demo Journal*. 2026.
"""


DEFAULT_SKILLS = ["okn-bioanalysis v0.1.1", "okn-report-style v0.2.0"]
# The analysis tells a story: question first, a why before each step, conclusions last. The notebook
# draws each report figure in its own code cell, its numbered legend right after.
QUESTION_CELL = {
    "type": "markdown",
    "source": "## Question and approach\n\nWhat does the demo show, and how was it computed?",
}
WHY_CELL = {"type": "markdown", "source": "Plot the demo panel to show its shape."}
FIGURE_CODE = {
    "type": "code",
    "source": 'fig, ax = plt.subplots()\nF.finalize(fig, 1, "figures/fig1_demo.png")',
}
LEGEND_CELL = {
    "type": "markdown",
    "source": "> ***Figure 1. A demonstration panel showing nothing in particular.***",
}
CONCLUSIONS_CELL = {
    "type": "markdown",
    "source": "## Conclusions\n\n- The demo panel has 1 of 1 rows.\n\n"
    "The demo shows nothing in particular.",
}
FIGURE_CELLS = [QUESTION_CELL, WHY_CELL, FIGURE_CODE, LEGEND_CELL, CONCLUSIONS_CELL]
_QUERY = "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s a ?t } } LIMIT 1"


def _write_notebook(
    study: Path, *, skills=DEFAULT_SKILLS, model="claude-opus-5", cells=None
) -> Path:
    """Write <study>/Demo_notebook/ as create_jupyter_notebook builds it, plus the HTML page that the
    tool's `html_command` renders (faked here: rendering needs Jupyter)."""
    scope = "validator-fixture"
    session.reset(scope)
    session.record(
        _QUERY,
        "json",
        result={"vars": ["s"], "rows": [{"s": "x"}], "row_count": 1},
        scope=scope,
    )
    folder = build_study(
        title="Demo",
        when="2026-07-25",
        model=model,
        entries=session.entries(scope),
        kgs=[{"shortname": "sawgraph"}],
        endpoint="https://example.org/sparql",
        generated_by="mcp-okn test",
        skills=skills,
        folder_name=NB,
        cells=FIGURE_CELLS if cells is None else cells,
    )
    session.reset(scope)
    root = study / NB
    for rel, text in folder.files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    (root / f"{NB}.html").write_text("<html><body>executed</body></html>")
    return root


def _header(study: Path) -> str:
    nb = json.loads((study / NB / f"{NB}.ipynb").read_text())
    return "".join(nb["cells"][0]["source"])


def _set_header(study: Path, header: str) -> None:
    """Replace the notebook's first (header) cell, keeping the HTML newer than the notebook."""
    path = study / NB / f"{NB}.ipynb"
    nb = json.loads(path.read_text())
    nb["cells"][0]["source"] = header
    path.write_text(json.dumps(nb))
    html_page = study / NB / f"{NB}.html"
    os.utime(html_page, (path.stat().st_mtime + 1,) * 2)


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


def _write_xlsx(
    path: Path, sheets=("Ranked Results", "Methods & Rules"), abbrev=True
) -> None:
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
    cell = (
        '<row><c t="inlineStr"><is><t>Abbreviations</t></is></c></row>'
        if abbrev
        else ""
    )
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
    (study / f"{TOKEN}_literature_comparison.md").write_text(
        "# Lit comparison\n\n1. Demo. 2026.\n"
    )
    _write_notebook(study)
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
    _write_xlsx(
        study / f"{TOKEN}_results.xlsx", sheets=("Ranked Results",)
    )  # drop Methods & Rules
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
        "## Reproducibility\n\nEverything needed to rerun the analysis is in the Demo_notebook folder backing this demonstration package.\n\n## References\n\n1. Demo Author, et al. A demonstration. *Demo Journal*. 2026.\n",
        "## References\n\n1. Demo Author, et al. A demonstration. *Demo Journal*. 2026.\n\n## Reproducibility\n\nEverything needed to rerun the analysis is in the Demo_notebook folder.\n",
    )
    assert md != _REPORT_MD  # guard: the replace actually fired
    (study / f"{TOKEN}_report.md").write_text(md)
    (study / f"{TOKEN}_report.html").write_text(_md_to_html(md))
    r = v.validate(str(study))
    assert r.errors  # order / last-two rule violated


def test_stale_reproducibility_record_fails(tmp_path):
    # The notebook folder replaces the old _reproducibility.md; a leftover one is a second record.
    study = _build(tmp_path)
    (study / f"{TOKEN}_reproducibility.md").write_text("# old record\n")
    r = v.validate(str(study))
    assert any("second reproducibility/transcript/spec" in e for e in r.errors), (
        r.errors
    )


def test_transcript_beside_notebook_fails(tmp_path):
    study = _build(tmp_path)
    (study / "data" / f"{TOKEN}_transcript.md").write_text("# stray transcript\n")
    r = v.validate(str(study))
    assert any("transcript" in e.lower() for e in r.errors)


def test_species_filenames_are_not_mistaken_for_a_spec_file(tmp_path):
    """`_spec` used to be a bare substring test, so `_species` matched it: a study with
    `wl_species_summary.csv` in `data/` failed the record check on a CSV.
    Data and figures can never BE a spec document, and `_spec` must end the word."""
    study = _build(tmp_path)
    (study / "data" / "wl_species_summary.csv").write_text("taxon,n\nAves,3\n")
    (study / "data" / "sentinel_species_county.csv").write_text("fips,n\n12086,4\n")
    (study / "figures" / "fig9_species_value.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    r = v.validate(str(study))
    assert not any("second reproducibility" in e for e in r.errors), r.errors

    # A prose file whose stem genuinely ends in `_spec` is still a second record.
    (study / "data" / "extra_spec.md").write_text("# a second spec\n")
    r2 = v.validate(str(study))
    assert any("second reproducibility" in e for e in r2.errors)


# ── The notebook folder ──────────────────────────────────────────────────────────────────────────────


def test_missing_notebook_folder_fails(tmp_path):
    study = _build(tmp_path)
    for p in sorted((study / NB).rglob("*"), reverse=True):
        p.unlink() if p.is_file() else p.rmdir()
    (study / NB).rmdir()
    r = v.validate(str(study))
    assert any(f"missing required directory: {NB}/" in e for e in r.errors), r.errors


def test_notebook_folder_with_another_name_fails(tmp_path):
    # A slugged folder (`demo-notebook`) breaks the study-token prefix and is not the record.
    study = _build(tmp_path)
    (study / NB).rename(study / "demo-notebook")
    r = v.validate(str(study))
    assert any("unexpected top-level directory: 'demo-notebook'" in e for e in r.errors)
    assert any(f"missing required directory: {NB}/" in e for e in r.errors)


def test_missing_notebook_html_fails(tmp_path):
    study = _build(tmp_path)
    (study / NB / f"{NB}.html").unlink()
    r = v.validate(str(study))
    assert any("html_command" in e for e in r.errors), r.errors


def test_html_older_than_notebook_warns(tmp_path):
    study = _build(tmp_path)
    nb = study / NB / f"{NB}.ipynb"
    os.utime(study / NB / f"{NB}.html", (nb.stat().st_mtime - 60,) * 2)
    r = v.validate(str(study))
    assert r.errors == [], r.errors
    assert any("older than the notebook" in w for w in r.warnings)


def test_missing_cached_rows_fail(tmp_path):
    # A hosted server returns a file map; a file the agent forgot to save is caught via the manifest.
    study = _build(tmp_path)
    (study / NB / "data" / "q01.csv").unlink()
    (study / NB / "okn_sparql.py").unlink()
    r = v.validate(str(study))
    assert any("missing data/q01.csv" in e for e in r.errors), r.errors
    assert any("missing okn_sparql.py" in e for e in r.errors), r.errors


def test_invalid_notebook_fails(tmp_path):
    study = _build(tmp_path)
    (study / NB / f"{NB}.ipynb").write_text("# not json")
    r = v.validate(str(study))
    assert any("not a valid nbformat-4 notebook" in e for e in r.errors), r.errors


def test_notebook_figure_not_copied_fails(tmp_path):
    study = _build(tmp_path)
    _write_notebook(
        study,
        cells=[
            *FIGURE_CELLS,
            {"type": "markdown", "source": "![Figure 1](figures/fig1_demo.png)"},
        ],
    )
    os.utime(study / NB / f"{NB}.html", None)
    r = v.validate(str(study))
    assert any("figures_to_copy" in e for e in r.errors), r.errors

    (study / NB / "figures").mkdir()
    (study / NB / "figures" / "fig1_demo.png").write_bytes(b"\x89PNG\r\n")
    assert v.validate(str(study)).errors == []


# ── Notebook story (question → why per step → conclusions) ──────────────────────────────────────────


def test_notebook_without_question_cell_fails(tmp_path):
    study = _build(tmp_path)
    _write_notebook(study, cells=[WHY_CELL, FIGURE_CODE, LEGEND_CELL, CONCLUSIONS_CELL])
    r = v.validate(str(study))
    assert any("no `## Question and approach` cell" in e for e in r.errors), r.errors


def test_notebook_without_conclusions_cell_fails(tmp_path):
    study = _build(tmp_path)
    _write_notebook(study, cells=[QUESTION_CELL, WHY_CELL, FIGURE_CODE, LEGEND_CELL])
    r = v.validate(str(study))
    assert any("no `## Conclusions` cell" in e for e in r.errors), r.errors


def test_conclusions_without_summary_of_findings_fails(tmp_path):
    # A heading over prose alone: the reader can't pick out what was found.
    study = _build(tmp_path)
    prose_only = {
        "type": "markdown",
        "source": "## Conclusions\n\nThe demo shows nothing in particular.",
    }
    _write_notebook(
        study, cells=[QUESTION_CELL, WHY_CELL, FIGURE_CODE, LEGEND_CELL, prose_only]
    )
    r = v.validate(str(study))
    assert any("no summary of findings" in e for e in r.errors), r.errors


def test_notebook_story_out_of_order_fails(tmp_path):
    # Conclusions before the code it concludes, and the question after it: both headings present,
    # neither doing its job.
    study = _build(tmp_path)
    _write_notebook(
        study,
        cells=[WHY_CELL, CONCLUSIONS_CELL, FIGURE_CODE, LEGEND_CELL, QUESTION_CELL],
    )
    r = v.validate(str(study))
    assert any("comes after analysis code" in e for e in r.errors), r.errors
    assert any("analysis code follows `## Conclusions`" in e for e in r.errors), (
        r.errors
    )


def test_notebook_without_analysis_cells_fails(tmp_path):
    # No `cells` at all: the notebook only reruns the queries. (No report figures, so the legend
    # check stays quiet and only the story check speaks.)
    study = _build(tmp_path)
    _write_notebook(study, cells=[])
    r = v.validate(str(study))
    assert any("no analysis cells" in e for e in r.errors), r.errors


def test_code_cell_without_why_cell_warns_only(tmp_path):
    # The figure cell right after another code cell, and a code cell right after a figure legend:
    # neither has its own why cell. (The first setup cell follows the question, which explains it.)
    study = _build(tmp_path)
    setup = {"type": "code", "source": "import analysis as A"}
    _write_notebook(
        study,
        cells=[QUESTION_CELL, setup, FIGURE_CODE, LEGEND_CELL, setup, CONCLUSIONS_CELL],
    )
    os.utime(study / NB / f"{NB}.html", None)
    r = v.validate(str(study))
    assert r.errors == [], r.errors
    assert any("2 analysis code cell(s)" in w for w in r.warnings), r.warnings


def test_jupyter_leftovers_in_notebook_folder_fail(tmp_path):
    study = _build(tmp_path)
    (study / NB / "__pycache__").mkdir()
    (study / NB / ".ipynb_checkpoints").mkdir()
    r = v.validate(str(study))
    assert any("__pycache__" in e for e in r.errors)
    assert any(".ipynb_checkpoints" in e for e in r.errors)


# ── Skills provenance (the notebook header) ──────────────────────────────────────────────────────────


def test_missing_skills_header_line_fails(tmp_path):
    # `skills=` is caller-supplied — the server can't see which skills a session loaded — so a notebook
    # with no Skills line is a forgotten argument, and the package silently claims no methodology.
    study = _build(tmp_path)
    _write_notebook(study, skills=[])
    r = v.validate(str(study))
    assert any("no '- **Skills:**' line" in e for e in r.errors)
    assert v.main([str(study)]) == 1


def test_skills_line_without_report_style_fails(tmp_path):
    # This validator only runs on an okn-report-style package, so that skill was used by definition.
    study = _build(tmp_path)
    _write_notebook(study, skills=["okn-bioanalysis v0.1.1"])
    r = v.validate(str(study))
    assert any("does not name okn-report-style" in e for e in r.errors)


def test_unversioned_skills_entry_warns_only(tmp_path):
    # Naming the skill without pinning its version still identifies the methodology — advisory, not blocking.
    study = _build(tmp_path)
    _write_notebook(study, skills=["okn-report-style"])
    r = v.validate(str(study))
    assert r.errors == [], r.errors
    assert any("without a version" in w for w in r.warnings)


def test_skills_mentioned_outside_header_does_not_satisfy_gate(tmp_path):
    # Only the tool-generated header counts; a mention in a later cell (the spec) is not provenance.
    study = _build(tmp_path)
    _write_notebook(
        study,
        skills=[],
        cells=[
            *FIGURE_CELLS,
            {"type": "markdown", "source": "- **Skills:** okn-report-style v0.2.0"},
        ],
    )
    r = v.validate(str(study))
    assert any("no '- **Skills:**' line" in e for e in r.errors)


# ── Model provenance ─────────────────────────────────────────────────────────────────────────────────
# The model id is written by three different paths (hand-authored title block → lifted into the .html by
# the renderer; `model=` into the notebook header) and nothing reconciles them, so the gate checks all three are
# present, specific, and identical.


def _set_model(study: Path, *, md=None, html=None, repro=None) -> None:
    """Rewrite the model id in one or more artifacts (None = leave alone, "" = drop the field)."""
    if repro is not None:
        old = "- **Model:** claude-opus-5"
        header = _header(study)
        assert (
            old in header
        )  # guard: the fixture still carries the field we mean to rewrite
        _set_header(
            study,
            header.replace(old, old.replace("claude-opus-5", repro) if repro else ""),
        )
    for value, path, old in (
        (md, study / f"{TOKEN}_report.md", "**Model:** claude-opus-5"),
        (html, study / f"{TOKEN}_report.html", "Model: claude-opus-5"),
    ):
        if value is None:
            continue
        text = path.read_text()
        assert (
            old in text
        )  # guard: the fixture still carries the field we mean to rewrite
        path.write_text(
            text.replace(old, old.replace("claude-opus-5", value) if value else "")
        )


def test_missing_model_in_report_fails(tmp_path):
    study = _build(tmp_path)
    _set_model(study, md="")
    r = v.validate(str(study))
    assert any("no model recorded" in e for e in r.errors), r.errors
    assert v.main([str(study)]) == 1


def test_missing_model_in_record_fails(tmp_path):
    study = _build(tmp_path)
    _set_model(study, repro="")
    r = v.validate(str(study))
    assert any("no model recorded" in e for e in r.errors), r.errors


def test_generic_model_family_name_fails(tmp_path):
    # "Claude" reads as filled-in provenance while identifying nothing that ran.
    study = _build(tmp_path)
    _set_model(study, md="Claude", html="Claude", repro="Claude")
    r = v.validate(str(study))
    assert any("not an exact model id" in e for e in r.errors), r.errors
    assert not any("differs across the package" in e for e in r.errors)


def test_placeholder_model_fails(tmp_path):
    study = _build(tmp_path)
    _set_model(study, md="unknown", html="unknown", repro="unknown")
    r = v.validate(str(study))
    assert any("not an exact model id" in e for e in r.errors), r.errors


def test_model_mismatch_between_md_and_record_fails(tmp_path):
    study = _build(tmp_path)
    _set_model(study, repro="claude-opus-4-8")
    r = v.validate(str(study))
    assert any("differs across the package" in e for e in r.errors), r.errors


def test_model_mismatch_between_md_and_html_fails(tmp_path):
    # A hand-built .html can disagree with the .md; parity is heading/word-count based and misses it.
    study = _build(tmp_path)
    _set_model(study, html="claude-opus-4-8")
    r = v.validate(str(study))
    assert any("differs across the package" in e for e in r.errors), r.errors


def test_non_anthropic_model_id_passes(tmp_path):
    # The rule is domain-neutral: any specific vendor id is fine, only generic ones are rejected.
    study = _build(tmp_path)
    _set_model(study, md="gpt-5.6-sol", html="gpt-5.6-sol", repro="gpt-5.6-sol")
    r = v.validate(str(study))
    assert r.errors == [], r.errors


def test_model_mentioned_outside_header_does_not_satisfy_gate(tmp_path):
    # Only the provenance header counts — a `Model:` in a later cell is not the tool-written field.
    study = _build(tmp_path)
    _write_notebook(
        study,
        cells=[
            *FIGURE_CELLS,
            {"type": "markdown", "source": "- **Model:** claude-opus-5"},
        ],
    )
    _set_model(study, repro="")
    r = v.validate(str(study))
    assert any("no model recorded" in e for e in r.errors), r.errors


def test_junk_file_in_subdir_fails(tmp_path):
    study = _build(tmp_path)
    (study / "data" / "scratch.tmp").write_text("junk")
    r = v.validate(str(study))
    assert any("scratch/QA/temp" in e for e in r.errors)


def test_osm_tile_server_in_report_fails(tmp_path):
    study = _build(tmp_path)
    html_path = study / f"{TOKEN}_report.html"
    # The map document sits HTML-escaped inside <iframe srcdoc>, as folium_map_iframe emits it.
    srcdoc = "&lt;script&gt;L.tileLayer(&quot;https://tile.openstreetmap.org/{z}/{x}/{y}.png&quot;)&lt;/script&gt;"
    html_path.write_text(
        html_path.read_text().replace(
            "</body>", f'<iframe srcdoc="{srcdoc}"></iframe></body>'
        )
    )
    r = v.validate(str(study))
    assert any("tile.openstreetmap.org" in e for e in r.errors), r.errors


def test_osm_tile_server_in_figure_html_fails(tmp_path):
    study = _build(tmp_path)
    (study / "figures" / "map.html").write_text(
        '<script>L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png")</script>'
    )
    r = v.validate(str(study))
    assert any("figures/map.html" in e for e in r.errors), r.errors


# A plotly figure page, cut down: the drawn trace, then the default template that styles every trace
# type by name (so even a bar chart's page mentions "scattermap").
_PLOTLY_TEMPLATE = (
    '"template":{"data":{"scattermap":[{"type":"scattermap","marker":{"colorbar":'
    '{"outlinewidth":0}}}],"bar":[{"type":"bar"}]}}'
)


def _plotly_page(trace_type: str) -> str:
    return (
        '<script>Plotly.newPlot("fig", [{"z":[1],"type":"'
        + trace_type
        + '"}], {'
        + _PLOTLY_TEMPLATE
        + "})</script>"
    )


def test_plotly_tile_map_in_figure_html_fails(tmp_path):
    study = _build(tmp_path)
    (study / "figures" / "map.html").write_text(_plotly_page("choroplethmap"))
    r = v.validate(str(study))
    assert any(
        "figures/map.html" in e and "plotly tile map (choroplethmap)" in e
        for e in r.errors
    ), r.errors


def test_plotly_tile_map_inlined_in_report_fails(tmp_path):
    study = _build(tmp_path)
    html_path = study / f"{TOKEN}_report.html"
    srcdoc = (
        _plotly_page("scattermapbox")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    html_path.write_text(
        html_path.read_text().replace(
            "</body>", f'<iframe srcdoc="{srcdoc}"></iframe></body>'
        )
    )
    r = v.validate(str(study))
    assert any("plotly tile map (scattermapbox)" in e for e in r.errors), r.errors


def test_plotly_non_map_figure_passes(tmp_path):
    # The template's "scattermap" entry is styling, not a drawn map; plotly's SVG geo maps also render.
    study = _build(tmp_path)
    (study / "figures" / "bars.html").write_text(_plotly_page("bar"))
    (study / "figures" / "geo.html").write_text(_plotly_page("choropleth"))
    r = v.validate(str(study))
    assert not any("plotly tile map" in e for e in r.errors), r.errors


def test_plotly_tile_map_in_notebook_output_fails(tmp_path):
    study = _build(tmp_path)
    nb_path = study / NB / f"{NB}.ipynb"
    nb = json.loads(nb_path.read_text())
    nb["cells"].append(
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": 1,
            "source": ["fig"],
            "outputs": [
                {
                    "output_type": "display_data",
                    "metadata": {},
                    # Pretty-printed with sorted keys, as Jupyter saves it: "type" comes last.
                    "data": {
                        "application/vnd.plotly.v1+json": {
                            "data": [{"locations": ["06"], "type": "densitymap"}],
                            "layout": {
                                "template": {
                                    "data": {"scattermap": [{"type": "scattermap"}]}
                                }
                            },
                        }
                    },
                }
            ],
        }
    )
    nb_path.write_text(json.dumps(nb, indent=1, sort_keys=True))
    r = v.validate(str(study))
    errs = [e for e in r.errors if "plotly tile map" in e]
    assert errs and "(densitymap)" in errs[0] and f"{NB}/{NB}.ipynb" in errs[0], (
        r.errors
    )


def _with_cells(tmp_path: Path, cells: list) -> Path:
    study = _build(tmp_path)
    _write_notebook(study, cells=cells)
    os.utime(study / NB / f"{NB}.html", None)
    return study


def test_notebook_figure_without_legend_fails(tmp_path):
    """All figures drawn in one cell and shown at the end: no per-figure legend → error."""
    study = _with_cells(tmp_path, [{"type": "code", "source": "build_all_figures()"}])
    r = v.validate(str(study))
    assert any("no legend for Figure 1" in e for e in r.errors), r.errors


def test_notebook_figure_legend_not_after_code_fails(tmp_path):
    cells = [
        {"type": "markdown", "source": "Intro."},
        {"type": "markdown", "source": "**Figure 1. Demo.** Drawn somewhere else."},
    ]
    r = v.validate(str(_with_cells(tmp_path, cells)))
    assert any("Figure 1 legend does not follow a code cell" in e for e in r.errors), (
        r.errors
    )


def test_notebook_figure_behind_a_call_fails(tmp_path):
    """A one-line call into a script hides the plotting code the notebook exists to show."""
    cells = [
        {"type": "code", "source": "BF.fig1()"},
        {"type": "markdown", "source": "**Figure 1. Demo.** Drawn in a script."},
    ]
    r = v.validate(str(_with_cells(tmp_path, cells)))
    assert any("does not draw the figure itself" in e for e in r.errors), r.errors

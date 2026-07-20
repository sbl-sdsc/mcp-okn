"""Tests for the report-style figure-numbering gate (check_figure_numbering).

The skill requires figures numbered consecutively 1..N in document order with filenames to match;
this is the automated check that enforces it (folded into check_report_parity)."""

import sys
from pathlib import Path

# build_report_html is a report-style skill script (stdlib-only), not part of the mcp_okn package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills/okn-report-style/scripts"))
import build_report_html as b


def _md(pairs):
    """A minimal report .md: for each (caption_n, file_n) emit an image + a ***Figure N.*** caption."""
    out = ["# Report", ""]
    for cap, fnum in pairs:
        out += [
            f"![Figure {cap}](figures/fig{fnum}_panel.png)",
            "",
            f"> ***Figure {cap}. A panel.***",
            "",
        ]
    return "\n".join(out)


def _write(tmp_path, text):
    p = tmp_path / "r.md"
    p.write_text(text)
    return str(p)


def test_consecutive_captions_and_files_pass(tmp_path):
    md = _write(tmp_path, _md([(1, 1), (2, 2), (3, 3)]))
    r = b.check_figure_numbering(md)
    assert r["ok"] and r["captions"] == [1, 2, 3] and r["files"] == [1, 2, 3]


def test_no_figures_passes(tmp_path):
    r = b.check_figure_numbering(_write(tmp_path, "# Report\n\nNo figures here.\n"))
    assert r["ok"] and r["captions"] == [] and r["files"] == []


def test_out_of_order_captions_fail(tmp_path):
    # The exact MS breakage: figures reordered for narrative flow, numbers not updated.
    md = _write(tmp_path, _md([(1, 1), (2, 2), (5, 5), (7, 7), (3, 3)]))
    r = b.check_figure_numbering(md)
    assert not r["ok"]
    assert r["captions"] == [1, 2, 5, 7, 3]
    assert any("caption" in i for i in r["issues"])


def test_captions_fixed_but_files_not_renamed_fail(tmp_path):
    # Display renumbered to 1..N but filenames left behind — must still FAIL (filename-match rule).
    md = _write(tmp_path, _md([(1, 1), (2, 2), (3, 5), (4, 7), (5, 3)]))
    r = b.check_figure_numbering(md)
    assert not r["ok"]
    assert r["captions"] == [1, 2, 3, 4, 5]
    assert r["files"] == [1, 2, 5, 7, 3]
    assert any("filename" in i for i in r["issues"])


def test_mid_caption_cross_reference_is_not_counted(tmp_path):
    # A caption that cross-references another figure must not add a spurious number.
    md = "# R\n\n![Figure 1](figures/fig1_a.png)\n\n> ***Figure 1. First.***\n\n"
    md += "![Figure 2](figures/fig2_b.png)\n\n> ***Figure 2. Second — a separate family from Figure 1.***\n"
    r = b.check_figure_numbering(_write(tmp_path, md))
    assert r["ok"] and r["captions"] == [1, 2] and r["files"] == [1, 2]

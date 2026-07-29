"""Skill version self-references must match the skill's frontmatter.

A bump means editing the same number in four places — `metadata.version`, the SKILL.md
body ("this skill is `okn-bioanalysis v0.1.2`"), the example header in
`references/report-structure.md`, and the example in the validator's error message —
and nothing checked that they agreed. Missing one is not cosmetic: the SKILL.md body is
what tells an agent which version string to pass to `create_reproducibility_record`, so a
stale number there is copied verbatim into every record's provenance header, where it
then PASSES `validate_okn_report` (which checks that a version is present, not which).

Both directions are checked: a skill naming itself, and one skill naming its sibling
(report-structure.md's example header cites both). Only `skills/` is scanned —
`docs/examples/` records state the versions that actually ran and must never be
"corrected" to today's.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

#: "okn-report-style v0.1.4". `\s+` because the mention wraps across a line break in
#: report-structure.md — a line-by-line scan would miss exactly the one that drifted.
_MENTION = re.compile(r"\b(okn-[a-z0-9-]+)\s+v(\d+(?:\.\d+)*)")


def _declared_versions() -> dict[str, str]:
    """`{skill name: frontmatter metadata.version}` for every bundled skill."""
    versions = {}
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        front = yaml.safe_load(skill_md.read_text(encoding="utf-8").split("---")[1])
        versions[front["name"]] = str(front["metadata"]["version"])
    return versions


def _mentions():
    """Every `<skill> v<version>` written anywhere in the skill sources."""
    for path in sorted(SKILLS_DIR.rglob("*")):
        if path.suffix not in {".md", ".py"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for m in _MENTION.finditer(text):
            line = text[: m.start()].count("\n") + 1
            yield path, line, m.group(1), m.group(2)


def test_skills_are_discovered():
    """Guard the guard: a scan that silently found no skills would pass vacuously."""
    declared = _declared_versions()
    assert set(declared) == {"okn-bioanalysis", "okn-report-style"}
    assert list(_mentions()), "no version mentions found — the regex or layout changed"


def test_version_mentions_match_frontmatter():
    declared = _declared_versions()
    stale = [
        f"{path.relative_to(SKILLS_DIR.parent)}:{line} says {name} v{found}, "
        f"but its frontmatter is v{declared[name]}"
        for path, line, name, found in _mentions()
        if name in declared and found != declared[name]
    ]
    assert not stale, "stale skill version reference(s):\n  " + "\n  ".join(stale)


@pytest.mark.parametrize("skill", ["okn-bioanalysis", "okn-report-style"])
def test_frontmatter_version_is_a_release_number(skill):
    """A non-numeric or absent version would make every comparison above vacuous."""
    assert re.fullmatch(r"\d+(\.\d+)*", _declared_versions()[skill])

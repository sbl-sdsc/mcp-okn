"""Skill version self-references must match the skill's frontmatter.

A bump means editing the same number in four places — `metadata.version`, the SKILL.md
body ("this skill is `okn-bioanalysis v0.1.2`"), the example header in
`references/report-structure.md`, and the example in the validator's error message —
and nothing checked that they agreed. Missing one is not cosmetic: the SKILL.md body is
what tells an agent which version string to pass to `create_jupyter_notebook`, so a
stale number there is copied verbatim into every notebook's provenance header, where it
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


# ── The server's copy of the versions, and the outdated-skill notice built on it ─────────────

import json  # noqa: E402

from mcp_okn import session  # noqa: E402
from mcp_okn.app import INSTRUCTIONS  # noqa: E402
from mcp_okn.server import create_chat_transcript, reset_query_log  # noqa: E402
from mcp_okn.skill_versions import (  # noqa: E402
    bundled_skill_versions,
    check_skills,
    download_url,
)

BUNDLED_JSON = SKILLS_DIR.parent / "src" / "mcp_okn" / "data" / "skill_versions.json"


def test_bundled_versions_match_frontmatter():
    """The Docker image has no `skills/`, so the server reads a generated copy. A skill bump
    without regenerating it would make the server call the NEW skill "newer than server"."""
    bundled = json.loads(BUNDLED_JSON.read_text(encoding="utf-8"))
    assert bundled == _declared_versions(), (
        "src/mcp_okn/data/skill_versions.json is stale — run scripts/package_skills.sh"
    )
    assert bundled_skill_versions() == bundled


def _older(version: str) -> str:
    """A version strictly below `version` ("0.2.7" -> "0.2.6", "0.2.0" -> "0.1.99")."""
    parts = [int(p) for p in version.split(".")]
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] > 0:
            parts[i] -= 1
            parts[i + 1 :] = [99] * (len(parts) - i - 1)
            return ".".join(map(str, parts))
    raise AssertionError(f"no version below {version}")


def test_current_and_foreign_skills_are_silent():
    current = [f"{n} v{v}" for n, v in bundled_skill_versions().items()]
    assert check_skills(current) == []
    assert check_skills(["some-other-skill v0.0.1", "okn-unknown v0.1.0"]) == []
    assert check_skills(None) == []


def test_outdated_skill_names_the_update():
    current = bundled_skill_versions()["okn-report-style"]
    old = _older(current)
    (warning,) = check_skills([f"okn-report-style v{old}"])
    assert warning.startswith("OUTDATED SKILL")
    assert f"v{old}" in warning and f"v{current}" in warning
    assert "TELL THE USER" in warning
    assert download_url("okn-report-style") in warning


@pytest.mark.parametrize(
    "spelling", ["okn-bioanalysis {v}", "okn-bioanalysis v{v}", "okn-bioanalysis@{v}"]
)
def test_version_spellings_are_parsed(spelling):
    old = _older(bundled_skill_versions()["okn-bioanalysis"])
    (warning,) = check_skills([spelling.format(v=old)])
    assert warning.startswith("OUTDATED SKILL")


def test_short_version_compares_numerically():
    """'0.2' equals '0.2.0', and '0.10.0' is newer than '0.9.0' (not a string compare)."""
    assert check_skills(["okn-report-style v999"])[0].startswith(
        "SERVER OLDER THAN SKILL"
    )
    current = bundled_skill_versions()["okn-report-style"]
    major, minor, *_ = current.split(".")
    padded = f"{major}.{minor}"
    if current == f"{padded}.0":
        assert check_skills([f"okn-report-style v{padded}"]) == []


def test_unversioned_bundled_skill_is_flagged():
    (warning,) = check_skills(["okn-bioanalysis"])
    assert "without a version" in warning


async def test_reset_query_log_returns_the_notice():
    session.reset()
    old = _older(bundled_skill_versions()["okn-bioanalysis"])
    out = await reset_query_log(skills=[f"okn-bioanalysis v{old}"])
    assert out["warnings"][0].startswith("OUTDATED SKILL")
    clean = await reset_query_log(
        skills=[f"okn-bioanalysis v{bundled_skill_versions()['okn-bioanalysis']}"]
    )
    assert "warnings" not in clean
    assert "warnings" not in await reset_query_log()


async def test_transcript_carries_the_notice():
    session.reset()
    old = _older(bundled_skill_versions()["okn-report-style"])
    payload = await create_chat_transcript(
        model="m", format="json", skills=[f"okn-report-style v{old}"]
    )
    assert any(w.startswith("OUTDATED SKILL") for w in payload["warnings"])
    session.reset()


def test_instructions_list_current_versions_near_the_top():
    """Clients truncate long server instructions, so the line must sit at the start."""
    head = INSTRUCTIONS[:1500]
    assert "SKILL VERSIONS" in head
    for name, version in bundled_skill_versions().items():
        assert f"{name} v{version}" in head

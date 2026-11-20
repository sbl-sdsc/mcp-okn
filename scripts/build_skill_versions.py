#!/usr/bin/env python3
"""Write src/mcp_okn/data/skill_versions.json from each skills/<name>/SKILL.md frontmatter.

The server compares the `skills=` a client passes against this file to tell the user when
their uploaded skill is out of date (see `mcp_okn.skill_versions`). The Docker image copies
only `src/` and `metadata/`, so the server cannot read `skills/` at runtime — hence the
generated copy. Called by scripts/package_skills.sh; tests/test_skill_versions.py fails
when the file disagrees with the frontmatter.

Standard library only (no PyYAML), so package_skills.sh can run it with any python3.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "src" / "mcp_okn" / "data" / "skill_versions.json"

_NAME = re.compile(r"^name:\s*[\"']?([^\"'\s]+)", re.M)
#: `version:` indented under `metadata:` in the frontmatter.
_VERSION = re.compile(r"^\s+version:\s*[\"']?([0-9][0-9.]*)", re.M)


def collect() -> dict[str, str]:
    versions: dict[str, str] = {}
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        front = skill_md.read_text(encoding="utf-8").split("---")[1]
        name, version = _NAME.search(front), _VERSION.search(front)
        if not (name and version):
            sys.exit(f"{skill_md}: frontmatter lacks name or metadata.version")
        versions[name.group(1)] = version.group(1)
    return versions


def main() -> None:
    OUT.write_text(
        json.dumps(collect(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

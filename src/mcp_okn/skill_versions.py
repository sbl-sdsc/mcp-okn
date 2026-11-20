"""Tell the user when the skill they loaded is not the one this server ships with.

A skill is text in the client's context: the server never sees which skills a session
loaded, and nothing updates an uploaded copy (claude.ai / Claude Desktop keep whatever
`.skill` the user uploaded until they upload a new one). The only way a version reaches
the server is the `skills=["<name> v<version>", …]` list the skills tell the model to pass
to `reset_query_log` (start of an analysis), `create_jupyter_notebook` and
`create_chat_transcript` (end). Those tools compare it with the versions bundled here and
return a warning the model relays to the user.

The reference versions are the skills in THIS build (``data/skill_versions.json``,
generated from each ``skills/<name>/SKILL.md`` by ``scripts/build_skill_versions.py``),
not the latest on GitHub: a skill has to match the tools the server actually exposes, and
a hosted server can lag the repository. So a mismatch in either direction is reported —
an older skill may call tools or arguments that were since removed, a newer one may call
tools this deployment does not have yet. For the same reason the download link names the
build commit (`raw/<sha>/skills/<name>.skill`) when the build id is a sha, not `main`.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib import resources

from .build_info import build_id

#: Where users get the current packages, and the per-client install/update table.
REPOSITORY = "https://github.com/sbl-sdsc/mcp-okn"
UPDATE_DOCS = f"{REPOSITORY}#skills"

#: "okn-report-style v0.2.6", also tolerating "okn-report-style 0.2.6" / "@0.2.6".
_ENTRY = re.compile(
    r"^\s*(okn-[a-z0-9-]+?)(?:\s+v?|\s*@\s*v?|\s+version\s+v?)(\d+(?:\.\d+)*)\b"
)
_NAME_ONLY = re.compile(r"^\s*(okn-[a-z0-9-]+)\s*$")


@lru_cache(maxsize=1)
def bundled_skill_versions() -> dict[str, str]:
    """`{skill name: version}` of the skills shipped with this server build ({} if absent)."""
    try:
        text = (resources.files("mcp_okn") / "data" / "skill_versions.json").read_text(
            encoding="utf-8"
        )
    except (FileNotFoundError, OSError):
        return {}
    return {str(k): str(v) for k, v in json.loads(text).items()}


#: A git commit sha (short or full). `MCP_OKN_BUILD` may instead hold a tag or a CI
#: build number, which is not a ref we can build a download link from.
_SHA = re.compile(r"[0-9a-f]{7,40}")


def download_url(name: str, ref: str = "main") -> str:
    """The `.skill` package of `name` at git `ref` (uploadable to claude.ai/Desktop)."""
    return f"{REPOSITORY}/raw/{ref}/skills/{name}.skill"


def build_commit() -> str | None:
    """The commit this server was built from, if `build_id()` is a sha; else None."""
    build = build_id()
    return build if _SHA.fullmatch(build) else None


def _download_hint(name: str) -> str:
    """Where to get the copy of `name` that matches THIS server.

    The build commit's copy is the one `bundled_skill_versions()` was generated from, so
    it always clears the warning — `main` can be behind an unmerged branch or ahead of a
    lagging hosted server. `main` stays as the fallback for an unpushed local build, whose
    commit link 404s.
    """
    main = download_url(name)
    commit = build_commit()
    if commit is None:
        return main
    return (
        f"{download_url(name, commit)} (the copy this server build, {commit}, ships; if "
        f"that link returns 404 the build was never pushed — use {main})"
    )


def _as_tuple(version: str) -> tuple[int, ...]:
    """'0.2.6' -> (0, 2, 6), padded so '0.2' == '0.2.0'."""
    parts = [int(p) for p in version.split(".")]
    return tuple(parts + [0] * (3 - len(parts)))


def check_skills(entries: list[str] | None) -> list[str]:
    """Return one warning per bundled skill in `entries` whose version differs from ours.

    Entries naming skills this server does not ship (third-party skills) are ignored, as
    are entries for our skills that match. An entry naming one of our skills WITHOUT a
    version gets a warning too: it cannot be checked, and it will fail the report
    validator's provenance check later.
    """
    bundled = bundled_skill_versions()
    if not bundled:
        return []
    warnings: list[str] = []
    for entry in entries or []:
        text = str(entry)
        match = _ENTRY.match(text)
        if match is None:
            bare = _NAME_ONLY.match(text)
            if bare and bare.group(1) in bundled:
                name = bare.group(1)
                warnings.append(
                    f"skill `{name}` was passed without a version, so it cannot be checked "
                    f"against the current v{bundled[name]}. Pass `'{name} v<version>'` with "
                    "the version from the skill's frontmatter `metadata.version`."
                )
            continue
        name, version = match.group(1), match.group(2)
        current = bundled.get(name)
        if current is None or _as_tuple(version) == _as_tuple(current):
            continue
        if _as_tuple(version) < _as_tuple(current):
            warnings.append(
                f"OUTDATED SKILL: the loaded `{name}` is v{version}, but this server ships "
                f"v{current}. TELL THE USER, in your reply: their copy of `{name}` is out of "
                f"date and they should install v{current} — download {_download_hint(name)} and "
                "upload it as a new version of the skill (claude.ai / Claude Desktop: Settings → "
                f"Capabilities → Skills; other clients: see {UPDATE_DOCS}). Meanwhile, where the "
                "old skill's instructions disagree with a tool's own description (a tool or "
                "argument that no longer exists), follow the tool description."
            )
        else:
            warnings.append(
                f"SERVER OLDER THAN SKILL: the loaded `{name}` is v{version}, but this server "
                f"ships v{current}, so the skill may call tools or arguments this deployment "
                "does not have yet. TELL THE USER, in your reply: the mcp-okn server they are "
                f"connected to lags the skill (see {UPDATE_DOCS}); to match the server instead, "
                f"install v{current} from {_download_hint(name)}. Where a tool the skill names "
                "is missing or rejects an argument, follow the tool's own description."
            )
    return warnings


def instructions_line() -> str:
    """The server-instructions paragraph listing the current skill versions ('' if none)."""
    bundled = bundled_skill_versions()
    if not bundled:
        return ""
    listed = ", ".join(
        f"{name} v{version}" for name, version in sorted(bundled.items())
    )
    return (
        f"SKILL VERSIONS: this server ships {listed}. If a skill you loaded (its frontmatter "
        "`metadata.version`) is OLDER, tell the user at the start of your reply that their "
        f"copy is out of date and how to update it ({UPDATE_DOCS}). Pass every skill you "
        "follow as `skills=['<name> v<version>', …]` to `reset_query_log` at the start of an "
        "analysis; it returns the same check as `warnings`."
    )

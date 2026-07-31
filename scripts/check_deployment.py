"""Check whether a hosted mcp-okn deployment matches this checkout.

The server at https://apps.okn.us/okn-mcp-dev/mcp is deployed by an external
operator — the pipeline is not in this repo — so it can, and does, lag ``main``
silently. In July 2026 it served 19 tools against 23 in the repo for 17 days;
nothing in CI or at runtime noticed, and the gap only surfaced when a
reproducibility record could not be generated. The reported ``version`` cannot
expose that: it is the MCP SDK's version, not this project's, and ``__version__``
has been 0.1.0 across the whole history.

So ask the endpoint directly. This speaks MCP over streamable HTTP, enumerates
what the server actually exposes, and diffs it against what this working tree
registers:

  build      get_server_info().build vs `git rev-parse --short HEAD`
  surface    the tool names and resource URIs the server lists vs those registered here
  data       the bundled crosswalk table (count + verified_on) and the KG count

Usage:
    uv run python scripts/check_deployment.py                # the hosted dev endpoint
    uv run python scripts/check_deployment.py --url URL      # any MCP endpoint
    uv run python scripts/check_deployment.py --strict        # also fail on prose drift
    uv run python scripts/check_deployment.py --json          # machine-readable

Exit codes: 0 in sync, 1 drift, 2 endpoint unreachable or not an MCP server — so it
can gate a "did the redeploy land?" check (a deploy in progress returns 502, which
must read as neither "in sync" nor "drifted").
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_URL = "https://apps.okn.us/okn-mcp-dev/mcp"
DEFAULT_TIMEOUT = 30.0
#: Shortest sha prefix accepted as a build match (git's own short form is 7).
MIN_SHA_PREFIX = 7
_SHA_RE = re.compile(r"[0-9a-f]{7,40}")


@dataclass(frozen=True)
class Surface:
    """What a server exposes, in comparable form."""

    tools: frozenset[str]
    resources: frozenset[str]
    instructions_sha: str
    #: tool name -> digest of its description + input schema
    tool_digests: dict[str, str] = field(default_factory=dict)


@dataclass
class Hosted:
    """One probe of a live endpoint."""

    surface: Surface
    #: get_server_info().build; None when that tool is absent (a build predating it)
    build: str | None = None
    service: str | None = None
    #: serverInfo.version — the MCP SDK's version, never a build signal
    sdk_version: str = ""
    crosswalks: tuple[int, str] | None = None
    kg_count: int | None = None


def _digest(*parts: str) -> str:
    return hashlib.sha256("\x00".join(parts).encode()).hexdigest()[:12]


def _quiet_transport_logs() -> None:
    """Keep the report readable.

    The SDK client and httpx narrate every request, the session id, and a routine
    "GET stream disconnected" on teardown — none of which is a finding. Handshake
    failures are reported by ``diagnose`` instead, which says more than the logs do.
    """
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.ERROR)


# --- pure comparisons (unit-tested offline) ----------------------------------


def diff_surface(hosted: Surface, local: Surface) -> dict[str, Any]:
    """Tool/resource/prose deltas between a live server and this checkout.

    ``missing_*`` are registered here but absent there — the lagging-deployment
    case. ``extra_*`` are the reverse: this checkout is behind, or on a branch.
    ``changed_tools`` are names on both sides whose description or input schema
    differ; that and ``instructions_match`` are advisory unless ``--strict``.
    """
    shared = hosted.tools & local.tools
    return {
        "missing_tools": sorted(local.tools - hosted.tools),
        "extra_tools": sorted(hosted.tools - local.tools),
        "missing_resources": sorted(local.resources - hosted.resources),
        "extra_resources": sorted(hosted.resources - local.resources),
        "changed_tools": sorted(
            name
            for name in shared
            if hosted.tool_digests.get(name, "")
            and local.tool_digests.get(name, "")
            and hosted.tool_digests[name] != local.tool_digests[name]
        ),
        "instructions_match": hosted.instructions_sha == local.instructions_sha,
    }


def build_status(hosted: str | None, local: str) -> str:
    """``absent`` | ``unknown`` | ``match`` | ``drift`` for the build comparison.

    ``absent`` means the server has no ``get_server_info`` tool at all; ``unknown``
    means it has one but could not identify itself (deployed without
    ``MCP_OKN_BUILD``, in a container with no git metadata). Matching is
    prefix-tolerant in both directions, so a short sha matches the full one.
    """
    if hosted is None:
        return "absent"
    hosted, local = hosted.strip(), local.strip()
    if not hosted or hosted == "unknown":
        return "unknown"
    if not local or local == "unknown":
        return "unknown"
    if hosted == local:
        return "match"
    shortest = min(len(hosted), len(local))
    if shortest >= MIN_SHA_PREFIX and (
        hosted.startswith(local) or local.startswith(hosted)
    ):
        return "match"
    return "drift"


def has_drift(deltas: dict[str, Any], status: str, data: dict[str, Any]) -> bool:
    """Whether the gating signals disagree (prose drift is not gating here).

    ``absent`` is deliberately not gated on its own: ``get_server_info`` is in the
    local tool set, so its absence already shows up as a missing tool. ``unknown``
    is a nudge to set ``MCP_OKN_BUILD``, not a verdict.
    """
    surface = any(
        deltas[key]
        for key in (
            "missing_tools",
            "extra_tools",
            "missing_resources",
            "extra_resources",
        )
    )
    return surface or status == "drift" or bool(data["mismatches"])


def compare_data(hosted: Hosted, local: dict[str, Any]) -> dict[str, Any]:
    """Compare the bundled data that only moves on a redeploy.

    A hosted value of ``None`` means the tool was absent or errored — reported as
    ``n/a`` and never counted as a mismatch, so this survives being pointed at an
    arbitrary MCP server.
    """
    mismatches = []
    if hosted.crosswalks is not None and hosted.crosswalks != local["crosswalks"]:
        mismatches.append("crosswalks")
    if hosted.kg_count is not None and hosted.kg_count != local["kg_count"]:
        mismatches.append("kgs")
    return {"mismatches": mismatches}


# --- local side (offline) -----------------------------------------------------


def _git(*args: str) -> str | None:
    """``git -C ROOT <args>`` stdout, or None when git fails or is absent."""
    try:
        # Fixed argv, no shell, no user input.
        out = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def local_build() -> str:
    """This checkout's short HEAD sha, or ``unknown``.

    Deliberately not ``build_info.build_id()``: that prefers ``MCP_OKN_BUILD``,
    which is the *deploy's* override, and would compare a server against an env
    var rather than against the tree you are looking at.
    """
    return _git("rev-parse", "--short", "HEAD") or "unknown"


def _commit_date(rev: str) -> str | None:
    return _git("log", "-1", "--format=%cs", rev) or None


def commits_behind(hosted_sha: str) -> tuple[int, int] | None:
    """``(commits, days)`` that ``hosted_sha`` trails HEAD, if it is known here.

    None when the build id is not a sha (a deploy may set ``MCP_OKN_BUILD`` to a
    tag or a CI build number) or names a commit this clone doesn't have — better
    to say "fetch first" than to print a bogus "0 commits behind".
    """
    if not _SHA_RE.fullmatch(hosted_sha):
        return None
    if _git("cat-file", "-e", f"{hosted_sha}^{{commit}}") is None:
        return None
    count = _git("rev-list", "--count", f"{hosted_sha}..HEAD")
    if count is None or not count.isdigit():
        return None
    days = 0
    then, now = _commit_date(hosted_sha), _commit_date("HEAD")
    if then and now:
        try:
            days = (date.fromisoformat(now) - date.fromisoformat(then)).days
        except ValueError:
            days = 0
    return int(count), days


def worktree_notes() -> list[str]:
    """Caveats about comparing a server against *this* tree."""
    notes = []
    if _git("status", "--porcelain"):
        notes.append("this working tree has uncommitted changes")
    head, upstream = _git("rev-parse", "HEAD"), _git("rev-parse", "origin/main")
    if head and upstream and head != upstream:
        notes.append(
            "HEAD is not origin/main — operators deploy from origin/main, and the "
            "local remote-tracking ref is only as fresh as your last `git fetch`"
        )
    return notes


async def local_surface() -> Surface:
    """Everything this working tree registers.

    Imports ``mcp_okn.server`` for its side effect — that module imports every tool
    module, which is what runs the ``@mcp.tool()`` decorators — then reads the
    FastMCP instance's own listings, so this can never drift from what the server
    would actually serve. Nothing is hard-coded, including the tool count.
    """
    from mcp_okn.server import mcp as server_app

    tools = await server_app.list_tools()
    resources = await server_app.list_resources()
    return Surface(
        tools=frozenset(t.name for t in tools),
        resources=frozenset(str(r.uri) for r in resources),
        instructions_sha=_digest(server_app.instructions or ""),
        tool_digests={
            t.name: _digest(
                t.description or "", json.dumps(t.inputSchema, sort_keys=True)
            )
            for t in tools
        },
    )


async def local_data() -> dict[str, Any]:
    """The bundled figures, read from the package rather than over the wire."""
    from mcp_okn import registry
    from mcp_okn.tools import joins

    crosswalks = await joins.list_crosswalks(include_examples=False)
    return {
        "crosswalks": (
            int(crosswalks["count"]),
            str(crosswalks.get("verified_on") or "?"),
        ),
        "kg_count": len(registry.load_snapshot()),
    }


# --- hosted side (network) ----------------------------------------------------


def _payload(result: Any) -> Any:
    """A tool result as plain Python, or None when the server flagged an error.

    Prefers ``structuredContent``; FastMCP wraps non-dict returns in a
    ``{"result": ...}`` envelope (``list_kgs`` does), so that is unwrapped. Falls
    back to JSON in the first text block for a server too old to emit structured
    output.
    """
    if getattr(result, "isError", False):
        return None
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        if set(structured) == {"result"}:
            return structured["result"]
        return structured
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                continue
    return None


async def probe(url: str, timeout: float) -> Hosted:
    """Handshake with a live MCP endpoint and read its surface.

    Uses the MCP SDK's streamable-HTTP client rather than raw HTTP: it already
    handles SSE-vs-JSON response framing, the ``Mcp-Session-Id`` round-trip, the
    initialized notification, protocol negotiation, and session teardown.
    """
    async with (
        streamablehttp_client(url, timeout=timeout) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        init = await session.initialize()
        tools = (await session.list_tools()).tools
        resources = (await session.list_resources()).resources
        names = {t.name for t in tools}
        hosted = Hosted(
            surface=Surface(
                tools=frozenset(names),
                resources=frozenset(str(r.uri) for r in resources),
                instructions_sha=_digest(init.instructions or ""),
                tool_digests={
                    t.name: _digest(
                        t.description or "", json.dumps(t.inputSchema, sort_keys=True)
                    )
                    for t in tools
                },
            ),
            sdk_version=init.serverInfo.version,
        )
        # Every call is gated on the tool being listed: an absent tool comes back
        # as isError, not an exception, and an old build has several of these.
        if "get_server_info" in names:
            info = _payload(await session.call_tool("get_server_info"))
            if isinstance(info, dict):
                hosted.build = str(info.get("build") or "") or None
                hosted.service = info.get("service")
        if "list_crosswalks" in names:
            data = _payload(
                await session.call_tool("list_crosswalks", {"include_examples": False})
            )
            if isinstance(data, dict) and isinstance(data.get("count"), int):
                hosted.crosswalks = (
                    data["count"],
                    str(data.get("verified_on") or "?"),
                )
        if "list_kgs" in names:
            kgs = _payload(await session.call_tool("list_kgs"))
            if isinstance(kgs, list):
                hosted.kg_count = len(kgs)
        return hosted


def _root_cause(exc: BaseException) -> BaseException:
    """Innermost exception of a possibly nested group.

    anyio wraps client failures in ExceptionGroups; ``except*`` is 3.11+ and this
    repo targets 3.10, so walk ``.exceptions`` instead.
    """
    inner = getattr(exc, "exceptions", None)
    return _root_cause(inner[0]) if inner else exc


async def diagnose(url: str, timeout: float) -> str:
    """One plain POST, described in one line — why the handshake failed.

    The SDK reports a 200-that-isn't-MCP as a bare "Session terminated", which
    tells a reader nothing. Report the status, content type, and first bytes so an
    HTML proxy error page or a wrong path is unmistakable.
    """
    body = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                url,
                json=body,
                headers={"Accept": "application/json, text/event-stream"},
            )
    except httpx.HTTPError as exc:
        return f"POST failed: {type(exc).__name__}: {exc}"
    ctype = resp.headers.get("content-type", "?").split(";")[0]
    snippet = " ".join(resp.text[:160].split())
    return f"POST returned HTTP {resp.status_code}, content-type {ctype}: {snippet}"


# --- reporting ----------------------------------------------------------------


def _build_lines(hosted: Hosted, local: str, status: str) -> list[str]:
    if status == "absent":
        return [
            "BUILD       no build reported — this deployment predates get_server_info,",
            "            so it cannot identify itself. That absence is itself drift.",
        ]
    if status == "unknown":
        return [
            f"BUILD       hosted reports {hosted.build!r} / local {local}",
            "            set MCP_OKN_BUILD to the deployed sha so records can name it",
        ]
    if status == "match":
        return [f"BUILD       {hosted.build} == {local}"]
    behind = commits_behind(hosted.build or "")
    lines = [f"BUILD       hosted {hosted.build}  /  local {local}   DRIFT"]
    if behind:
        commits, days = behind
        lines.append(
            f"            hosted is {commits} commits and {days} days behind HEAD"
        )
    else:
        lines.append(
            f"            cannot locate {hosted.build} in this clone — try `git fetch`"
        )
    return lines


def render(
    url: str,
    hosted: Hosted,
    local: Surface,
    local_figures: dict[str, Any],
    deltas: dict[str, Any],
    data: dict[str, Any],
    status: str,
    local_head: str,
    strict: bool,
) -> tuple[str, int]:
    """The report text and the exit code."""
    lines = [
        "mcp-okn deployment check",
        f"  endpoint  {url}",
        f"  checkout  {ROOT} @ {local_head}",
        "",
    ]
    lines += _build_lines(hosted, local_head, status)
    lines.append(
        f'            (serverInfo.version is "{hosted.sdk_version}": the MCP SDK\'s '
        "version,"
    )
    lines.append("            not mcp-okn's. It is never a build signal.)")
    lines.append("")

    n_hosted, n_local = len(hosted.surface.tools), len(local.tools)
    verdict = "in sync" if n_hosted == n_local and not deltas["missing_tools"] else ""
    lines.append(
        f"TOOLS       {n_hosted} hosted / {n_local} local"
        + (" — in sync" if verdict and not deltas["extra_tools"] else "")
    )
    for key, label in (
        ("missing_tools", "missing on the hosted server"),
        ("extra_tools", "only on the hosted server (this checkout may be behind)"),
    ):
        if deltas[key]:
            lines.append(f"            {label} ({len(deltas[key])}):")
            lines += [f"              {name}" for name in deltas[key]]
    lines.append("")

    r_hosted, r_local = len(hosted.surface.resources), len(local.resources)
    same = not deltas["missing_resources"] and not deltas["extra_resources"]
    lines.append(
        f"RESOURCES   {r_hosted} hosted / {r_local} local"
        + (" — in sync" if same else "")
    )
    for key, label in (
        ("missing_resources", "missing"),
        ("extra_resources", "extra"),
    ):
        if deltas[key]:
            lines.append(f"            {label}: {', '.join(deltas[key])}")
    lines.append("")

    lines.append("DATA")
    cw_local = local_figures["crosswalks"]
    if hosted.crosswalks is None:
        lines.append("            crosswalks   n/a (list_crosswalks unavailable)")
    else:
        flag = "   DRIFT" if "crosswalks" in data["mismatches"] else ""
        lines.append(
            f"            crosswalks   {hosted.crosswalks[0]} "
            f"(verified_on {hosted.crosswalks[1]})  /  {cw_local[0]} "
            f"({cw_local[1]}){flag}"
        )
    if hosted.kg_count is None:
        lines.append("            KGs          n/a (list_kgs unavailable)")
    else:
        flag = "   DRIFT" if "kgs" in data["mismatches"] else ""
        lines.append(
            f"            KGs          {hosted.kg_count}  /  "
            f"{local_figures['kg_count']}{flag}"
        )
    prose = "identical" if deltas["instructions_match"] else "DIFFER"
    advisory = "" if strict else "   advisory — pass --strict to fail on this"
    lines.append(
        f"            instructions {prose}{'' if deltas['instructions_match'] else advisory}"
    )
    if deltas["changed_tools"]:
        lines.append(
            f"            {len(deltas['changed_tools'])} tool description(s)/schema(s) "
            f"differ: {', '.join(deltas['changed_tools'])}"
        )
    lines.append("")

    drift = has_drift(deltas, status, data)
    if strict and (not deltas["instructions_match"] or deltas["changed_tools"]):
        drift = True
    for note in worktree_notes():
        lines.append(f"NOTE: {note}")
    if drift:
        lines.append(
            "OUT OF SYNC. Ask the operators to redeploy from origin/main, then re-run."
        )
    else:
        lines.append(f"IN SYNC with {local_head}.")
    return "\n".join(lines), (1 if drift else 0)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"MCP endpoint to check (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT, help="seconds (default: 30)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail on instructions / tool-description drift, not just report it",
    )
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args()
    _quiet_transport_logs()

    local = await local_surface()
    figures = await local_data()
    head = local_build()

    try:
        hosted = await probe(args.url, args.timeout)
    except Exception as exc:  # the client raises through an anyio task group
        cause = _root_cause(exc)
        detail = await diagnose(args.url, args.timeout)
        print(
            f"mcp-okn deployment check\n  endpoint  {args.url}\n\n"
            f"ERROR: no MCP handshake.\n"
            f"  cause  {type(cause).__name__}: {cause}\n"
            f"  probe  {detail}\n"
            "  A proxy error page, a wrong path, or a deployment mid-restart all look\n"
            f"  like this. Check the URL, or retry in a minute (--timeout is "
            f"{args.timeout:g}s)."
        )
        return 2

    deltas = diff_surface(hosted.surface, local)
    data = compare_data(hosted, figures)
    status = build_status(hosted.build, head)

    if args.json:
        drift = has_drift(deltas, status, data)
        if args.strict and (
            not deltas["instructions_match"] or deltas["changed_tools"]
        ):
            drift = True
        print(
            json.dumps(
                {
                    "url": args.url,
                    "local_build": head,
                    "hosted_build": hosted.build,
                    "build_status": status,
                    "sdk_version": hosted.sdk_version,
                    "hosted_tools": sorted(hosted.surface.tools),
                    "local_tools": sorted(local.tools),
                    "data": {
                        "hosted_crosswalks": hosted.crosswalks,
                        "local_crosswalks": figures["crosswalks"],
                        "hosted_kgs": hosted.kg_count,
                        "local_kgs": figures["kg_count"],
                        "mismatches": data["mismatches"],
                    },
                    "notes": worktree_notes(),
                    "drift": drift,
                    **deltas,
                },
                indent=2,
                default=list,
            )
        )
        return 1 if drift else 0

    text, code = render(
        args.url, hosted, local, figures, deltas, data, status, head, args.strict
    )
    print(text)
    return code


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

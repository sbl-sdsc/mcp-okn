"""Transcript/logging tools.

reset_query_log, get_query_log, create_chat_transcript, and the
latest-transcript MCP resource.
"""

from __future__ import annotations

import re
import tempfile
from datetime import date as _date
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.types import ResourceLink, TextContent
from sparql_to_mermaid import try_to_mermaid

from .. import __version__, session
from ..app import mcp
from ..build_info import build_id, build_suffix
from ..mermaid_namespace import namespace_document
from ..skill_versions import check_skills
from ..sparql import PUBLIC_ENDPOINT, named_graph
from ..transcript_render import (
    MERMAID_LABEL,
    PdfRendererUnavailable,
    html_to_pdf,
    markdown_to_html,
)

#: `create_chat_transcript` formats that render the Markdown document; `json` is
#: the structured alternative. `html`/`pdf` are conversions of the Markdown.
_DOCUMENT_FORMATS = ("markdown", "html", "pdf")
LATEST_URI = "transcript://session/latest"
LATEST_HTML_URI = "transcript://session/latest.html"
LATEST_PDF_URI = "transcript://session/latest.pdf"

# NOTE: the server deliberately does NOT prepend a reminder to a document generated with
# include_query_diagrams=False: it was an HTML comment the caller saved verbatim, so it stayed baked
# into the artifact.


@mcp.tool()
async def reset_query_log(
    scope: str | None = None, skills: list[str] | None = None
) -> dict[str, Any]:
    """Clear this analysis's query log (and logged diagrams) for a fresh start.

    Call this at the START of a new analysis. Every subsequent `sparql_query`
    (and `expand_ontology_term`) call is logged automatically, as is every
    `visualize_schema` diagram, and `create_chat_transcript` renders them as the
    ground-truth record of what actually ran — so you don't have to re-supply
    queries or diagrams from memory.

    Args:
        scope: OPTIONAL log scope. Omit for a normal single analysis. If SEVERAL
            ANALYSES RUN CONCURRENTLY against this server — most importantly
            parallel subagents, which all share ONE MCP session — each MUST pass
            its own unique scope, and pass the SAME string to `sparql_query` and
            `create_chat_transcript`. Without it, their queries interleave in one
            log and one agent's SPARQL lands in another's transcript. Resetting
            one scope never touches another.
        skills: OPTIONAL — every skill you are following, each `"<name> v<version>"`
            with the version from the skill's frontmatter `metadata.version` (e.g.
            `["okn-bioanalysis v0.1.3"]`). The server checks them against the skill
            versions it ships with; the server cannot see your loaded skills otherwise.

    Returns:
        `{"cleared": N, "scope": ..., "active_scopes": [...]}`, plus `warnings` when
        a passed skill is older (or newer) than this server's — RELAY those to the
        user in your reply, they say how to update. If `active_scopes` shows scopes
        you did not create, other analyses ARE running concurrently in this session
        — pass a `scope` from here on.
    """
    removed = session.reset(scope)
    out: dict[str, Any] = {
        "cleared": removed,
        "scope": scope or session.DEFAULT_SCOPE,
        "active_scopes": session.scopes(),
    }
    if skill_warnings := check_skills(_clean_entries(skills)):
        out["warnings"] = skill_warnings
    return out


@mcp.tool()
async def get_query_log(scope: str | None = None) -> list[dict[str, Any]]:
    """Return the SPARQL queries logged so far for this analysis, in order.

    Only queries that returned rows and were not marked exploratory are present.
    Each entry has `timestamp`, `sparql` (verbatim), `graphs` (KG shortnames),
    `format`, `row_count`, and `results` (capped sample). Useful to inspect what
    will appear in `create_chat_transcript`.

    A query that ran but is ABSENT here (it errored, returned zero rows, or was
    marked exploratory) is NOT lost — call `get_skipped_queries` to see it with
    the reason it was skipped.

    Args:
        scope: OPTIONAL log scope — the same one passed to `sparql_query`. Omit
            for a normal single analysis.
    """
    return session.entries(scope)


@mcp.tool()
async def get_skipped_queries(scope: str | None = None) -> list[dict[str, Any]]:
    """Return queries that RAN but were kept OUT of the transcript log, in order.

    The counterpart to `get_query_log`: a query is skipped — and appears here
    instead of in the log — when it errored, returned zero rows, or was marked
    `exploratory`. This is where an "empty auto-log" gets explained: if your
    substantive pulls hit the endpoint's read-only-filesystem / oversized-sort
    error, they land here with `reason: "error"` rather than in the log.

    Each entry has `timestamp`, `sparql` (verbatim), `graphs` (KG shortnames),
    `format`, `reason` (`error` / `empty` / `exploratory`), `error` (the endpoint
    message when `reason == "error"`, else null), and `row_count`. These entries
    never enter `create_chat_transcript` — they are diagnostic only.

    Args:
        scope: OPTIONAL log scope — the same one passed to `sparql_query`. Omit
            for a normal single analysis.
    """
    return session.skipped(scope)


def _clean_entries(entries: list[str] | None) -> list[str]:
    """Normalise a caller-supplied provenance list (skills, external MCP servers).

    Strips blanks and de-duplicates while preserving the caller's order. The server cannot
    observe what was active in the client's session — neither the loaded skills nor the other
    MCP servers it called — so the entries are rendered verbatim: whatever the caller passes
    (ideally ``name vX.Y.Z``) is what the record claims.
    """
    seen: list[str] = []
    for entry in entries or []:
        text = str(entry).strip()
        if text and text not in seen:
            seen.append(text)
    return seen


def _skills_warning(noun: str) -> str:
    """Return the provenance warning for a document generated without ``skills=``.

    ``skills`` is the one header field the server cannot derive — it knows the model,
    its own version, the endpoint and the query log, but not which skills the client's
    session loaded. So an omitted list is indistinguishable from "no methodology", and
    a silently absent line is only ever noticed later (if at all). Both document tools
    say this at the moment of generation, while regenerating is still a single call.

    Args:
        noun: What the caller is generating ("record" / "transcript"), so the warning
            names the thing in front of them.
    """
    return (
        f"no `skills=` passed, so the header has no `- **Skills:**` line and the {noun} "
        "claims no methodology at all. If any skill shaped this analysis "
        "(okn-report-style, okn-bioanalysis, …), call again with "
        "`skills=['<name> v<version>', …]` — version from each skill's frontmatter "
        "`metadata.version` — and save THAT result. Do not hand-add the line to the "
        "saved file. If no skill was used, this warning is correctly ignored."
    )


def _plural(count: int, singular: str, plural: str | None = None) -> str:
    """Format a count with its noun for the header manifest.

    E.g. "1 query" / "3 queries". Pass `plural` for irregular forms; defaults to
    `singular + 's'`.
    """
    word = singular if count == 1 else (plural or f"{singular}s")
    return f"{count} {word}"


def _render_stub(
    *,
    title: str,
    when: str,
    model: str,
    kgs: list[dict[str, Any]],
    n_chars: int,
    n_lines: int,
    n_queries: int,
    n_viz: int,
    skills: list[str] | None = None,
    mcp_servers: list[str] | None = None,
    resource: str = LATEST_URI,
    kind: str = "markdown",
) -> str:
    """Return a compact stand-in when the full transcript is too large to hand back.

    Over `max_inline_chars`, the complete document is published verbatim at the
    resource `transcript://session/latest`; this stub carries the provenance + size
    and points the caller there, so it never reconstructs a truncated one. ``resource`` and
    ``kind`` name where the full document lives and what it is (the HTML rendering
    is published at its own resource).
    """
    kg_list = ", ".join(f"`{k['shortname']}`" for k in kgs) or "_none_"
    lines = [
        f"# {title} — full transcript delivered via resource",
        "",
        f"- **Date:** {when}",
        f"- **Model:** {model}",
        *([f"- **Skills:** {' · '.join(skills)}"] if skills else []),
        *(
            [f"- **External MCP servers:** {' · '.join(mcp_servers)}"]
            if mcp_servers
            else []
        ),
        f"- **Generated by:** {mcp.name} v{__version__}{build_suffix()}",
        f"- **Knowledge graphs used:** {kg_list}",
        f"- **Size:** {n_chars:,} characters · {n_lines:,} lines · "
        f"{n_queries} queries · {n_viz} visualizations",
        "",
        f"> This transcript ({n_chars:,} chars) exceeds the inline result size, "
        "so the full body was NOT returned here — returning it risks a harness "
        "spill/truncation and a fabricated substitute. The COMPLETE, verbatim "
        f"{kind} is published at the read-only MCP resource "
        f"`{resource}`: the client can fetch/save it DIRECTLY, "
        "bypassing the size limit and the model's context (this works even when "
        "the server is hosted remotely). Point the user there — do NOT "
        "hand-write, summarize, or reconstruct a substitute transcript.",
    ]
    return "\n".join(lines)


def _resolve_sources(
    log: list[dict[str, Any]],
    visualizations: list[dict[str, Any]],
    kgs_used: list[str] | None,
    *,
    check_phantom: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Resolve the KGs a transcript is about and guard its provenance.

    Shared by ``create_chat_transcript`` and ``create_jupyter_notebook``.
    Returns ``(log, kgs, warnings)`` where ``log`` has any FOREIGN auto-logged
    queries removed (entries touching none of an explicitly named ``kgs_used`` —
    almost always another concurrent subagent's work leaking through a shared,
    unscoped session), ``kgs`` is the ``[{shortname, named_graph}]`` list (inferred
    from the log + visualizations when ``kgs_used`` is None), and ``warnings`` holds
    any foreign-drop or phantom-source notices.

    A phantom source — a KG named in ``kgs_used`` that no kept query or
    visualization actually touched — is flagged (not dropped) only when
    ``check_phantom`` is True; its "contribution" came from an unlogged/exploratory
    query the record cannot reproduce, so the caller must re-run it non-exploratory
    or drop the KG from the sources.
    """
    caller_named_kgs = kgs_used is not None
    warnings: list[str] = []

    # Drop foreign queries: entries touching none of the named KGs (a sibling
    # subagent's work in a shared, unscoped session), warning rather than silently
    # including/dropping. Entries whose graphs we can't determine are kept.
    dropped_foreign: list[dict[str, Any]] = []
    if log and kgs_used:
        wanted = set(kgs_used)
        kept: list[dict[str, Any]] = []
        for entry in log:
            graphs = entry.get("graphs") or []
            if graphs and not (set(graphs) & wanted):
                dropped_foreign.append(entry)
            else:
                kept.append(entry)
        log = kept

    # Infer KGs from the log (and any diagrams) when not passed explicitly.
    if kgs_used is None:
        names: list[str] = []
        for entry in log:
            for name in entry.get("graphs", []):
                if name not in names:
                    names.append(name)
        for viz in visualizations:
            name = viz.get("shortname")
            if name and name not in names:
                names.append(name)
        kgs_used = names
    kgs = [{"shortname": name, "named_graph": named_graph(name)} for name in kgs_used]

    if dropped_foreign:
        foreign_graphs = sorted(
            {g for e in dropped_foreign for g in (e.get("graphs") or [])}
            - set(kgs_used)
        )
        n = len(dropped_foreign)
        noun = "query that touches" if n == 1 else "queries that touch"
        warnings.append(
            f"Dropped {n} auto-logged {noun} none of "
            f"`kgs_used` (graphs: {', '.join(foreign_graphs)}). That is almost "
            "certainly ANOTHER concurrently-running analysis's work — parallel "
            "subagents share one MCP session, so an unscoped log mixes them. They "
            "are NOT in the transcript. To make this deterministic, pass a unique "
            "`scope` to reset_query_log / sparql_query / the transcript tool."
        )

    if caller_named_kgs and check_phantom:
        evidenced = {g for e in log for g in (e.get("graphs") or [])}
        evidenced |= {v.get("shortname") for v in visualizations if v.get("shortname")}
        phantom = [name for name in kgs_used if name not in evidenced]
        if phantom:
            named = ", ".join(f"`{p}`" for p in phantom)
            was = "was" if len(phantom) == 1 else "were"
            warnings.append(
                f"Named in `kgs_used` but no logged query (or visualization) in "
                f"this transcript touched {named} — so {named} {was} NOT actually "
                "used here as far as the record shows. Credit a KG as a source only "
                "if a logged query used it; a 'contribution' read off an "
                "exploratory / unlogged query or from prior knowledge is a phantom "
                "source the transcript can't reproduce. Either re-run the "
                "establishing query non-exploratory so it lands in the log, or drop "
                "the KG from the sources."
            )

    return log, kgs, warnings


def _as_utc(dt: datetime) -> datetime:
    """Coerce a datetime to timezone-aware UTC (a naive value is assumed to be UTC).

    Keeps span arithmetic from raising on a naive-vs-aware mix — logged timestamps carry ``+00:00``
    but a caller-supplied chat start/end may be naive.
    """
    return (
        dt.replace(tzinfo=timezone.utc)
        if dt.tzinfo is None
        else dt.astimezone(timezone.utc)
    )


def _parse_iso(s: str) -> datetime:
    """Parse an ISO-8601 timestamp, tolerating a trailing ``Z`` (UTC designator).

    Python 3.10's ``datetime.fromisoformat`` rejects ``Z`` (only 3.11+ accepts it), so normalise it
    to ``+00:00`` first — a caller may pass e.g. ``2026-07-18T09:03:00Z``. Raises ``ValueError`` on
    unparseable input, exactly like ``fromisoformat``, so existing callers' fallbacks still fire.
    """
    if isinstance(s, str) and s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def _format_span(first: datetime, last: datetime) -> str:
    """Format a "<start>–<end> UTC (<elapsed>)" window string for two instants (start ≤ end)."""
    first, last = _as_utc(first), _as_utc(last)
    secs = max(int((last - first).total_seconds()), 0)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    elapsed = f"{h}h {m}m" if h else (f"{m}m {s}s" if m else f"{s}s")
    if first.date() == last.date():
        span = f"{first:%Y-%m-%d %H:%M}–{last:%H:%M} UTC"
    else:
        span = f"{first:%Y-%m-%dT%H:%MZ} → {last:%Y-%m-%dT%H:%MZ}"
    return f"{span} ({elapsed})"


def _active_window(entries: list[dict[str, Any]]) -> str:
    """Return a "first → last (elapsed)" string from the log's query timestamps, or "" if none.

    This is the study's ACTIVE QUERY WINDOW — wall-clock from the first logged SPARQL to the last. It
    is a lower bound on true study time: it excludes framing/reading before the first query and
    writing/figures after the last, and is skewed if the log was reset mid-study. Timestamps are UTC,
    to the second (see ``session.record``); token/cost usage is NOT visible to the server and cannot be
    included here (record it from the client, e.g. Claude Code ``/cost``).
    """
    stamps = [ts for e in entries if isinstance(ts := e.get("timestamp"), str)]
    if not stamps:
        return ""
    try:
        times = sorted(_parse_iso(s) for s in stamps)
    except ValueError:
        return ""
    return _format_span(times[0], times[-1])


def _chat_window(started: str, ended: str | None) -> str | None:
    """Format the WHOLE-CHAT elapsed window from caller-supplied ISO-8601 start/end timestamps.

    The server sees only query timestamps, so full-chat duration can't be computed here — the caller
    (which knows when the conversation began) must pass ``started``; ``ended`` defaults to now (UTC),
    i.e. the moment the record is generated, a stand-in for chat end. Returns None if ``started`` (or a
    supplied ``ended``) can't be parsed, so the caller can fall back to the active-query window.
    """
    try:
        start = _parse_iso(started)
    except (ValueError, TypeError):
        return None
    if ended:
        try:
            end = _parse_iso(ended)
        except (ValueError, TypeError):
            return None
    else:
        end = datetime.now(timezone.utc)
    return _format_span(start, end)


def _finalize_document(
    *,
    title: str,
    when: str,
    model: str,
    kgs: list[dict[str, Any]],
    body: list[str],
    warnings: list[str],
    n_schema_diagrams: int,
    n_queries_for_stub: int,
    n_viz_for_stub: int,
    scope: str | None,
    max_inline_chars: int | None,
    active_window: str = "",
    window_label: str = "Study active window",
    prompt: str = "",
    notes: str = "",
    skills: list[str] | None = None,
    mcp_servers: list[str] | None = None,
) -> str:
    """Assemble header + Contents manifest + body, publish, and return the document.

    Used by ``create_chat_transcript``. The Contents manifest is derived from what actually rendered (fenced-block counts),
    so it is a checkable invariant. The full markdown is always published to the
    ``transcript://session/latest`` resource; the return value is that markdown, or
    a compact stub when it exceeds ``max_inline_chars`` (the full body still on the
    resource), with any ``warnings`` prepended as HTML comments.

    Args:
        title: Document title (H1).
        when: Date string for the header.
        model: Model id for the header.
        kgs: ``[{shortname, named_graph}]`` for the "Knowledge graphs used" list.
        body: The rendered body lines (queries, and for the full transcript any
            conversation and schema diagrams).
        warnings: Provenance warnings to prepend as HTML comments (may be empty).
        n_schema_diagrams: How many ```mermaid blocks are schema diagrams (the rest
            are per-query diagrams); 0 for the lean record.
        n_queries_for_stub: Query count reported in the stub.
        n_viz_for_stub: Visualization count reported in the stub.
        scope: Log scope the document is published under.
        max_inline_chars: Return a stub above this size (None = never).
        active_window: Optional "first → last (elapsed)" window string; added as a
            header line when non-empty. Either the study active-query window (from
            ``_active_window``) or the whole-chat window (from ``_chat_window``).
        window_label: Header label for ``active_window`` (default "Study active
            window"); pass "Elapsed time" when ``active_window`` is the whole-chat span.
        prompt: Optional originating user prompt, rendered as a ``## Prompt`` section
            at the TOP of the content (above ``notes``). Empty = omitted.
        notes: Optional caller-supplied methodology note. Rendered as a visible
            ``## Notes`` section between the header and "Knowledge graphs used" —
            the legitimate home for context a caller would otherwise be tempted to
            hand-edit into the saved ``.md`` (e.g. why the logged queries are compact
            re-registrations and where the full extractions live). Empty = omitted.
        skills: Optional agent skills that shaped the analysis, already normalised by
            ``_clean_entries``. Rendered verbatim as a ``- **Skills:**`` header line
            directly beneath "Model" — the two together are the agent's configuration
            (which model, following which methodology), where the endpoint and
            "Generated by" describe the service. Empty = the line is omitted entirely.
        mcp_servers: Optional OTHER MCP servers the session actually called (PubMed,
            Paperclip, …), already normalised by ``_clean_entries``. Rendered as an
            ``- **External MCP servers:**`` line under "Skills", completing the picture
            of where the analysis's evidence came from: this server's KGs are listed
            below, but literature and other outside sources reached the study through
            connectors only the client can see. Empty = the line is omitted entirely.
    """
    # Give each embedded query diagram a unique node-id namespace so many `graph TD`
    # blocks on one page don't collide on shared ids (graph0, v1, bind0, …) and stop
    # rendering. Fence lines are preserved, so the block counts below are unaffected.
    body_md = namespace_document("\n".join(body))
    n_queries = body_md.count("```sparql")
    n_query_diagrams = body_md.count("```mermaid") - n_schema_diagrams
    # Only list components that are actually present — a trailing "· 0 schema
    # diagrams" reads like something is missing rather than absent.
    parts = [
        _plural(n_queries, "query", "queries") if n_queries else "",
        _plural(n_query_diagrams, "query diagram") if n_query_diagrams else "",
        _plural(n_schema_diagrams, "schema diagram") if n_schema_diagrams else "",
    ]
    parts = [p for p in parts if p]
    contents = "- **Contents:** " + (
        " · ".join(parts) if parts else "no queries or diagrams"
    )

    header = [
        f"# {title}",
        "",
        f"- **Date:** {when}",
        f"- **Model:** {model}",
        *([f"- **Skills:** {' · '.join(skills)}"] if skills else []),
        *(
            [f"- **External MCP servers:** {' · '.join(mcp_servers)}"]
            if mcp_servers
            else []
        ),
        f"- **SPARQL endpoint:** {PUBLIC_ENDPOINT}",
        f"- **Generated by:** {mcp.name} v{__version__}{build_suffix()}",
        *([f"- **{window_label}:** {active_window}"] if active_window else []),
        contents,
        "",
        *(["## Prompt", "", prompt.strip(), ""] if prompt.strip() else []),
        *(["## Notes", "", notes.strip(), ""] if notes.strip() else []),
        "## Knowledge graphs used",
        "",
    ]
    if kgs:
        header += [f"- `{kg['shortname']}` — <{kg['named_graph']}>" for kg in kgs]
    else:
        header.append("- _None queried._")

    markdown = "\n".join([*header, "", body_md])
    # Publish for direct client fetch/save via the transcript resource. The stored
    # document is the clean one — warnings are for the caller, not the artifact.
    session.set_last_transcript(markdown, scope)

    # If the rendered body is large enough that the harness would spill/truncate it
    # (which invites a fabricated substitute), return a compact STUB instead. Nothing
    # is lost: the full markdown was just published verbatim to the resource.
    if max_inline_chars is not None and len(markdown) > max_inline_chars:
        out = _render_stub(
            title=title,
            when=when,
            model=model,
            kgs=kgs,
            n_chars=len(markdown),
            n_lines=markdown.count("\n") + 1,
            n_queries=n_queries_for_stub,
            n_viz=n_viz_for_stub,
            skills=skills,
            mcp_servers=mcp_servers,
        )
    else:
        out = markdown

    if warnings:
        # Surfaced as an HTML comment: the markdown path must return a plain string
        # (that contract is what lets the caller save the result verbatim), and a
        # comment renders invisibly if the document is written to a .md as-is — while
        # still being right there in the tool result for the caller to act on.
        note = "\n".join(f"<!-- mcp-okn WARNING: {w} -->" for w in warnings)
        return f"{note}\n{out}"
    return out


@mcp.tool()
async def create_chat_transcript(
    model: str,
    exchanges: list[dict[str, Any]] | None = None,
    kgs_used: list[str] | None = None,
    date: str | None = None,
    format: str = "markdown",
    title: str = "Proto-OKN Chat Transcript",
    include_query_log: bool = True,
    include_intermediate_rows: bool = False,
    include_visualizations: bool = True,
    include_query_diagrams: bool = True,
    diagram_max_chars: int | None = None,
    max_result_rows: int | None = 5,
    scope: str | None = None,
    max_inline_chars: int | None = 100_000,
    skills: list[str] | None = None,
    external_mcp_servers: list[str] | None = None,
) -> Any:
    """Build a reproducible, detailed transcript of a Proto-OKN session.

    Captures the FULL working detail — not just a summary — so the session can
    be reproduced and audited: the user prompts and your answers, every SPARQL
    query that actually ran (verbatim) with the rows it returned, plus session
    provenance (date, model version, knowledge graphs, endpoint).

    Queries come from the automatic session log: each `sparql_query` /
    `expand_ontology_term` call is recorded as it runs, and (when
    `include_query_log` is true) rendered here as ground truth — you do NOT need
    to re-supply them. Call `reset_query_log` at the start of an analysis to
    scope the log to that session. You still supply the prompts and your
    full answer text (verbatim, not summarized) via `exchanges`.

    Args:
        model: The EXACT runtime model identifier that produced the analysis
            (e.g. `claude-opus-4-8`, `gpt-5.6-sol`), taken from trusted session
            metadata or supplied by the user — never a family or product name
            (`Claude`, `GPT-5`, `Codex`), a placeholder, or an id inferred from
            wording like "based on GPT-5". The server stores this verbatim and
            cannot see which model is calling it, so it can neither derive the
            value nor tell a right one from a wrong one. If you cannot determine
            it, ASK the user rather than guessing.
        exchanges: The conversation turns, in order. Each is a dict with
            `prompt` (str) and optional `answer` (str). The `answer` MUST be your
            full response for that turn, reproduced verbatim as the user saw it —
            the complete report text, findings, and any inline tables or lists —
            NOT a high-level summary or paraphrase. The server cannot see your
            prose (only tool calls are logged), so whatever you omit here is gone
            from the transcript. Err toward including too much. You may also attach an
            explicit `queries` list per turn (same shape as the log entries) if
            you want queries shown inline with a specific prompt instead of —
            or in addition to — the auto-logged appendix. Attach ONLY queries
            that produced findings; never attach exploratory/schema-probing
            queries. A query's optional `description` is a plain, user-facing
            label of what the query finds (e.g. "Diseases linked to PFAS") —
            never internal bookkeeping such as "(exploratory, not logged)",
            "(intermediate)", or notes about logging state.
        kgs_used: Shortnames of the knowledge graphs queried. If omitted, they
            are inferred from the logged queries. Each is expanded to its
            federation named-graph URI. As a backstop, any name you pass that no
            logged query (or schema visualization) actually touched is flagged as
            a phantom source in the returned warnings — credit a KG only if a
            logged query used it.
        date: ISO date (`YYYY-MM-DD`) of the session. Defaults to today.
        format: `markdown` (default) for a rendered document string; `html` or
            `pdf` when the user asks for an .html or .pdf transcript; or `json`
            for the structured fields. `html` and `pdf` are conversions of the
            same markdown document, with every ```mermaid block drawn as an image
            by the latest Mermaid 12.x instead of shown as source. `html` returns
            a standalone page (string) to save verbatim as `.html`; it loads
            Mermaid from jsDelivr when opened. `pdf` prints that page in
            headless Chromium on the server and returns a short summary plus a
            link to `transcript://session/latest.pdf` (and a server-local file
            path) — the PDF bytes are not inlined. If the server has no Chromium,
            `pdf` returns an `error` naming the fix; fall back to `html`.
        title: Heading for the transcript.
        include_query_log: If true (default), append the auto-logged queries
            as a "SPARQL queries executed" section.
        include_intermediate_rows: If false (default), only the FINAL logged
            query renders its result table; earlier (intermediate) queries
            show their SPARQL, row count, and a compact PREVIEW of the rows (a
            single-row result in full, otherwise the first 3 rows), to keep the
            transcript focused on the queries that produced the findings. Set
            true to render result rows for every logged query (each still capped
            at `max_result_rows`).
        max_result_rows: Cap on how many result rows each rendered table shows —
            for the final logged query, any inline-attached `queries`, and (with
            `include_intermediate_rows=True`) every query. The true row count is
            always preserved, with a "showing first N" note when capped; this
            applies to csv/tsv results too. Defaults to 5 so a large deliverable
            doesn't bloat the transcript (the full data belongs in the separate
            output file). Pass `None` to render every row.
        include_visualizations: If true (default), append a "Schema
            visualizations" section with every `visualize_schema` diagram logged
            this session, each in a fenced ```mermaid block. These are recorded
            automatically — you do NOT need to re-supply them.
        include_query_diagrams: If true (default), render a Mermaid `graph TD`
            diagram of each SPARQL query directly beneath its ```sparql block
            (both the inline queries and the "SPARQL queries executed" appendix),
            so the transcript shows the shape of every query. A query that cannot
            be parsed into a diagram is skipped silently (its text still shows).
            Set false to omit the per-query diagrams (right when a large record
            would otherwise spill); the `sparql_to_mermaid` tool draws any of them
            on request.
        diagram_max_chars: OPTIONAL cap on a per-query diagram's size. When set,
            a diagram longer than this many characters is dropped (its query text
            still shows) so a huge diagram never bloats the transcript. Default
            None = no cap.
        scope: OPTIONAL log scope — the same string passed to `reset_query_log`
            and `sparql_query`. Omit for a normal single analysis. Pass a unique
            label when SEVERAL ANALYSES RUN CONCURRENTLY against this server
            (parallel subagents share ONE MCP session, so an unscoped log mixes
            their queries and this transcript would render whichever happened to
            be logged). As a backstop, when `kgs_used` is given, any auto-logged
            query touching NONE of those KGs is dropped from the transcript and
            reported — so a forgotten scope is loud, not silent.
        max_inline_chars: Guard against handing back a body so large the harness
            spills/truncates it (which invites a fabricated substitute). If the
            rendered markdown exceeds this many characters, the tool returns a
            compact STUB — provenance, size, and a pointer to
            `transcript://session/latest` — instead of the full body; the complete
            document is still published verbatim to that resource, so nothing is
            lost. Default 100_000 (≈25k tokens). Pass `None` to always return the
            full body inline (for clients that handle large results and want to
            save it verbatim). Applies to `markdown` only. When you get a stub,
            deliver the transcript from the resource — do not treat the stub AS the
            transcript.
        skills: The agent skills that shaped this analysis, each as
            `"<name> v<version>"` (e.g. `["okn-bioanalysis v0.1.0",
            "okn-report-style v0.1.1"]`) — the version is the skill's frontmatter
            `metadata.version`. Rendered as a `- **Skills:**` header line directly
            beneath "Model". Technically optional, but PASS IT whenever a skill was
            followed: the server CANNOT see which skills your session loaded, so
            omitting it silently publishes a transcript claiming no methodology —
            the tool returns a WARNING when you do, and the fix is to call again
            with `skills=[...]`, never to hand-add the line to the saved file. List
            only skills you actually followed, exactly as `model` names the model
            that actually ran. Naming a skill you did not use is a phantom source,
            same as an unqueried KG.
        external_mcp_servers: OTHER MCP servers this session actually CALLED —
            connectors the user enabled that supplied evidence beyond this server's
            KGs (e.g. `["PubMed", "Paperclip", "Open Targets"]`; append a version
            when the connector reports one). Rendered as an
            `- **External MCP servers:**` header line beneath "Skills". Like `skills`,
            the server cannot see your other connectors, so this is caller-supplied —
            and the same two rules apply: list a server only if a call to it fed the
            analysis (an enabled-but-unused connector is a phantom source, exactly
            like an unqueried KG), and don't leave a used one off (the transcript's KG
            list then reads as the whole evidence base when it wasn't).

    Returns:
        For `markdown`: the transcript string (or, when it exceeds
        `max_inline_chars`, a compact stub pointing at
        `transcript://session/latest`). Each conversation turn is
        rendered in the mcp-proto-okn style — a "👤 **User**" block (the prompt)
        and a "🧠 **Assistant**" block (the answer), separated by a rule — with
        queries in fenced ```sparql blocks (each followed, by default, by a
        Mermaid diagram of the query — see `include_query_diagrams`), their
        result tables, and schema diagrams in fenced ```mermaid blocks under the
        answer.
        For `html`: the transcript as one standalone HTML page (or a stub
        pointing at `transcript://session/latest.html` when it exceeds
        `max_inline_chars`). SAVE IT VERBATIM to a `.html` file, exactly like
        the markdown.
        For `pdf`: a summary line with the PDF's resource link
        (`transcript://session/latest.pdf`) and server-local path; deliver that
        file, never a PDF you produce yourself.
        For `json`: a dict with `title`, `date`, `model`, `exchanges`,
        `knowledge_graphs`, `query_log`, `visualizations`, and
        `sparql_endpoint`.

    OUTPUT HANDLING (required): SAVE the transcript as a downloadable file.
    Write the full markdown returned by this tool — verbatim and in its
    entirety — to a `.md` file using your file-creation capability (the same
    thing that happens when a user says "save the transcript as a file": the
    `.md` is written and shown in the preview panel, downloadable directly from
    the chat). A Markdown ARTIFACT / document achieves the same result (Claude
    Desktop and claude.ai render it in a side panel the user can save as `.md`
    or export to PDF; a hosted `present_files`-style tool also works). Creating
    the file is the goal — a sentence describing or summarizing the transcript
    is NOT a substitute.

    COPY THE RETURN VALUE BYTE-FOR-BYTE — DO NOT RETYPE IT. Pass this tool's exact
    returned string to your file/artifact writer. Do NOT re-type it, restructure
    it, reorder or rename sections, tidy the formatting, or regenerate it from your
    understanding of what it said. This transcript is already the final, formatted
    deliverable; it needs no editing. Every query carries a fenced ```mermaid
    diagram and a result table directly beneath its ```sparql block — a hand-typed
    "cleaned up" version silently DROPS exactly those diagrams and tables, which is
    the whole point of the transcript. If you find yourself reading the transcript
    and re-emitting it, stop: write the original string instead. SELF-CHECK: the
    header's `- **Contents:**` bullet states how many queries and diagrams the
    document has — after saving, confirm your file has that many ```mermaid blocks
    (and ```sparql blocks); if fewer, you dropped some, so rewrite it from the exact
    tool output. When in doubt the canonical copy is the resource
    `transcript://session/latest` (below) — deliver from there.

    IF THIS RESULT IS SPILLED TO A FILE (it is large and often exceeds the
    harness result-size limit, so the harness may save it to a temp file and hand
    you a notice instead of the text): this output is a DELIVERABLE ARTIFACT, not
    analysis input. The spill notice is usually phrased as a comprehension task
    ("read the content in chunks to summarize / analyze / review") — ignore that
    framing. Your job is not to understand the transcript, it is to deliver it
    verbatim, and you must NOT hand-write, summarize, truncate, or reconstruct a
    substitute from memory — an authoritative-looking incomplete transcript is
    worse than no file at all. Two ways to deliver it, in order:
      1. PRIMARY (works even when this server is hosted REMOTELY): the full
         markdown is republished every run at the read-only MCP resource
         `transcript://session/latest`. Point the user to it — their client
         fetches/saves it DIRECTLY, bypassing both the result-size limit and your
         context. This is the reliable path on a hosted server, where the spilled
         temp file lives on the client and you may have no filesystem access to
         the server at all.
      2. Only if your client exposes the spilled temp file to your file tools
         (e.g. a local CLI): `Read` it and `Write` its exact bytes to the report
         folder. (This routes the full content through your context — costly — so
         prefer 1 when available.)
    Note the size limit is enforced by the HARNESS after this tool returns, so a
    tool/notice cannot lift it — these are the delivery paths that work around it.

    Only if you genuinely cannot write a file or artifact, fall back to
    outputting the complete markdown in a fenced ```markdown block in your reply
    so the user can copy/save it.

    NEVER claim the transcript is "ready", "in the preview panel", or "saved"
    unless you actually wrote the file (or emitted its full content) — do not
    fabricate a preview. Either the file exists / the document content is present
    in your response, or you state plainly that you could not produce it.

    The rendered markdown is also published as the read-only MCP resource
    `transcript://session/latest`, so a client can fetch/save it directly
    (transport-agnostic; works for remote servers) regardless of how you present
    it. You may point the user there.
    """
    when = date or _date.today().isoformat()
    exchanges = exchanges or []
    skill_list = _clean_entries(skills)
    server_list = _clean_entries(external_mcp_servers)
    log = session.entries(scope) if include_query_log else []
    visualizations = session.visualizations(scope) if include_visualizations else []
    # Drop foreign queries, infer/verify the KGs, and collect provenance warnings.
    log, kgs, warnings = _resolve_sources(
        log, visualizations, kgs_used, check_phantom=include_query_log
    )
    if not skill_list:
        warnings.append(_skills_warning("transcript"))
    warnings += check_skills(skill_list)

    if format == "json":
        payload: dict[str, Any] = {
            "title": title,
            "date": when,
            "model": model,
            "exchanges": exchanges,
            "knowledge_graphs": kgs,
            "query_log": log,
            "visualizations": visualizations,
            "sparql_endpoint": PUBLIC_ENDPOINT,
            "generated_by": {
                "service": mcp.name,
                "version": __version__,
                "build": build_id(),
            },
        }
        if skill_list:
            payload["skills"] = skill_list
        if server_list:
            payload["external_mcp_servers"] = server_list
        if warnings:
            payload["warnings"] = warnings
        return payload

    if format not in _DOCUMENT_FORMATS:
        return {
            "error": f"Unsupported format {format!r}; use 'markdown', 'html', "
            "'pdf', or 'json'."
        }

    # Build the BODY first (conversation + query appendix + schema diagrams), then
    # derive the header's Contents manifest from what actually rendered — so the
    # counts always match the document. The manifest is a checkable invariant: a
    # reader (or the model, after saving) can confirm the file has that many
    # ```sparql / ```mermaid blocks, turning a silently dropped diagram into a
    # one-line check.
    body: list[str] = ["## Conversation", ""]
    if not exchanges:
        body += ["_No prompts recorded._", ""]
    for exchange in exchanges:
        # mcp-proto-okn style: each turn is a 👤 User block and a 🧠 Assistant
        # block separated by a rule; queries/diagrams render under the answer.
        body += [
            "👤 **User**",
            "",
            exchange.get("prompt", "(no prompt)"),
            "",
            "---",
            "",
            "🧠 **Assistant**",
            "",
        ]
        answer = (exchange.get("answer") or "").strip()
        if answer:
            body += [answer, ""]
        # Only findings-producing queries belong in the transcript; drop any
        # the model flagged exploratory so schema-probing never leaks in.
        shown = [q for q in (exchange.get("queries") or []) if not q.get("exploratory")]
        for j, q in enumerate(shown, start=1):
            body += _render_query(
                q,
                f"Query {j}",
                max_rows=max_result_rows,
                diagram=include_query_diagrams,
                diagram_max_chars=diagram_max_chars,
            )
        # Optional Mermaid diagram(s) attached inline to this turn.
        inline = exchange.get("mermaid")
        for diagram in [inline] if isinstance(inline, str) else (inline or []):
            if (diagram or "").strip():
                body += ["```mermaid", diagram.strip(), "```", ""]

    if log:
        body += ["## SPARQL queries executed", ""]
        for k, entry in enumerate(log, start=1):
            ctx = entry.get("timestamp", "")
            graphs = entry.get("graphs") or []
            if graphs:
                ctx += " · " + ", ".join(f"`{g}`" for g in graphs)
            # By default only the final query's rows are shown; intermediate
            # queries list their text and row count but omit the result table.
            show_results = include_intermediate_rows or k == len(log)
            body += _render_query(
                entry,
                f"Query {k}",
                subheading=ctx,
                show_results=show_results,
                max_rows=max_result_rows,
                diagram=include_query_diagrams,
                diagram_max_chars=diagram_max_chars,
            )

    if visualizations:
        body += ["## Schema visualizations", ""]
        for viz in visualizations:
            shortname = viz.get("shortname", "")
            ctx = viz.get("timestamp", "")
            body += [f"### `{shortname}` schema", ""]
            if ctx:
                body += [f"_{ctx}_", ""]
            body += ["```mermaid", (viz.get("mermaid") or "").strip(), "```", ""]

    rendered = format != "markdown"
    document = _finalize_document(
        title=title,
        when=when,
        model=model,
        kgs=kgs,
        body=body,
        # html/pdf convert the CLEAN, complete markdown (also published at
        # transcript://session/latest); their own size guard and warnings apply below.
        warnings=[] if rendered else warnings,
        n_schema_diagrams=len(visualizations),
        n_queries_for_stub=len(log),
        n_viz_for_stub=len(visualizations),
        scope=scope,
        max_inline_chars=None if rendered else max_inline_chars,
        skills=skill_list,
        mcp_servers=server_list,
    )
    if not rendered:
        return document
    page = markdown_to_html(document, title)
    session.set_last_transcript_rendering(html=page, scope=scope)
    if format == "html":
        if max_inline_chars is not None and len(page) > max_inline_chars:
            page = _render_stub(
                title=title,
                when=when,
                model=model,
                kgs=kgs,
                n_chars=len(page),
                n_lines=page.count("\n") + 1,
                n_queries=len(log),
                n_viz=len(visualizations),
                skills=skill_list,
                mcp_servers=server_list,
                resource=LATEST_HTML_URI,
                kind="HTML page",
            )
        if warnings:
            note = "\n".join(f"<!-- mcp-okn WARNING: {w} -->" for w in warnings)
            return f"{note}\n{page}"
        return page
    return await _deliver_pdf(
        page, title=title, when=when, warnings=warnings, scope=scope
    )


def _pdf_path(title: str, when: str) -> Path:
    """Return where a rendered PDF is written on the machine running the server.

    A fixed directory under the system temp dir and a filename slugged from the title
    and date: the caller never chooses the path, so a remote client cannot make a
    hosted server write anywhere else.
    """
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").lower()[:60] or "transcript"
    folder = Path(tempfile.gettempdir()) / "mcp-okn-transcripts"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{slug}-{when}.pdf"


async def _deliver_pdf(
    page: str,
    *,
    title: str,
    when: str,
    warnings: list[str],
    scope: str | None,
) -> Any:
    """Print the HTML transcript to PDF and return a summary plus a link to it.

    The PDF itself is NOT inlined in the tool result — a multi-megabyte base64 blob
    would flood the model's context. It is published at
    ``transcript://session/latest.pdf`` (returned as a resource link the client can
    fetch) and written to a server-local file, which a client running mcp-okn on
    its own machine can copy directly.
    """
    try:
        pdf = await html_to_pdf(page)
    except PdfRendererUnavailable as exc:
        return {
            "error": str(exc),
            "html_resource": LATEST_HTML_URI,
            "warnings": warnings,
        }
    session.set_last_transcript_rendering(pdf=pdf, scope=scope)
    path = _pdf_path(title, when)
    path.write_bytes(pdf)
    lines = [
        f"PDF transcript rendered ({len(pdf):,} bytes; diagrams drawn by "
        f"{MERMAID_LABEL}).",
        f"- Resource: `{LATEST_PDF_URI}` — fetch/save it from there (works when the "
        "server is hosted remotely).",
        f"- Server-local file: `{path}` — usable only when mcp-okn runs on the same "
        "machine as you; copy it to the user's folder.",
        "Deliver this file as-is; do not regenerate the PDF yourself.",
        *(f"WARNING: {w}" for w in warnings),
    ]
    return [
        TextContent(type="text", text="\n".join(lines)),
        ResourceLink(
            type="resource_link",
            name=path.name,
            title=title,
            uri=LATEST_PDF_URI,  # type: ignore[arg-type]
            mimeType="application/pdf",
            size=len(pdf),
        ),
    ]


@mcp.resource(
    "transcript://session/latest",
    name="Latest chat transcript",
    description=(
        "The most recent transcript rendered by create_chat_transcript this "
        "session, as Markdown. Lets a client fetch/save the document directly, "
        "independent of how the model re-emits it — including when the tool "
        "result was too large to return inline and got spilled/truncated by the "
        "harness. On a remotely hosted server this is the reliable way to retrieve "
        "the full transcript verbatim without any filesystem access."
    ),
    mime_type="text/markdown",
)
def latest_transcript_resource() -> str:
    """Return the last rendered transcript, or a placeholder if none yet."""
    md = session.last_transcript()
    if not md:
        return (
            "# No transcript yet\n\n"
            "Call the `create_chat_transcript` tool (markdown format) first; the "
            "rendered document then appears here."
        )
    return md


@mcp.resource(
    LATEST_HTML_URI,
    name="Latest chat transcript (HTML)",
    description=(
        "The most recent create_chat_transcript rendering in format='html' or "
        "'pdf': a standalone HTML page whose diagrams are drawn by "
        f"{MERMAID_LABEL}. Fetch/save it directly as a .html file."
    ),
    mime_type="text/html",
)
def latest_transcript_html_resource() -> str:
    """Return the last HTML transcript rendering, or a placeholder if none yet."""
    page = session.last_transcript_html()
    if not page:
        return (
            "<!doctype html><title>No transcript yet</title><p>Call "
            "<code>create_chat_transcript</code> with <code>format='html'</code> "
            "first; the rendered page then appears here.</p>"
        )
    return page


@mcp.resource(
    LATEST_PDF_URI,
    name="Latest chat transcript (PDF)",
    description=(
        "The most recent create_chat_transcript rendering in format='pdf'. "
        "Fetch/save it directly as a .pdf file."
    ),
    mime_type="application/pdf",
)
def latest_transcript_pdf_resource() -> bytes:
    """Return the last PDF transcript rendering.

    Raises:
        ValueError: No PDF has been rendered yet this session (an empty "PDF"
            would be saved as a broken file, so this fails loudly instead).
    """
    pdf = session.last_transcript_pdf()
    if not pdf:
        raise ValueError(
            "No PDF transcript yet: call create_chat_transcript with format='pdf' first."
        )
    return pdf


# Internal bookkeeping the model sometimes buries in a query `description`
# (e.g. "Explore NDE schema (exploratory, not logged)"). It has no value to the
# user, so strip it from the rendered heading. Matches a parenthetical/bracketed
# group, or a trailing dash/comma note, containing a bookkeeping keyword.
_DESC_NOISE_RE = re.compile(
    r"\s*[\(\[][^\)\]]*\b(?:exploratory|not\s+logged|intermediate|logging)\b[^\)\]]*[\)\]]"
    r"|\s*[—–\-,]\s*(?:exploratory|not\s+logged|intermediate)\b[^.;]*",
    re.IGNORECASE,
)


def _clean_description(desc: str | None) -> str:
    """Strip internal bookkeeping noise from a query description for display."""
    text = _DESC_NOISE_RE.sub("", desc or "")
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text.rstrip(" —–-,;:").strip()


def _render_query(
    q: dict[str, Any],
    label: str,
    subheading: str = "",
    show_results: bool = True,
    max_rows: int | None = None,
    diagram: bool = False,
    diagram_max_chars: int | None = None,
) -> list[str]:
    """Render one query (verbatim text + results or error) as markdown lines.

    When ``show_results`` is True the result table is rendered, capped at ``max_rows``
    (``None`` = uncapped); when False, a compact PREVIEW of the rows is shown (a
    single-row result in full, otherwise the first 3 rows) — used for intermediate
    queries in the log appendix.

    When ``diagram`` is True, a Mermaid ``graph TD`` diagram of the query is
    inserted directly beneath its ```sparql block; a query that cannot be parsed
    is skipped silently (its text still shows). ``diagram_max_chars`` (``None`` =
    no limit) drops the diagram when it would exceed that many characters — the
    "diagram only if it fits" gate — so an oversized diagram never bloats the record.
    """
    desc = _clean_description(q.get("description"))
    heading = f"#### {label}" + (f" — {desc}" if desc else "")
    lines = [heading, ""]
    if subheading:
        lines += [f"_{subheading}_", ""]
    sparql = (q.get("sparql") or "").strip()
    lines += ["```sparql", sparql, "```", ""]
    if diagram and sparql:
        mermaid = try_to_mermaid(sparql)
        if mermaid and (diagram_max_chars is None or len(mermaid) <= diagram_max_chars):
            lines += ["```mermaid", mermaid, "```", ""]
    if q.get("error"):
        lines += [f"**Error:** {q['error']}", ""]
    elif show_results:
        lines += _render_results(q.get("results"), max_rows=max_rows)
    else:
        # Compact preview: a single-row result renders in full, a larger one
        # shows just its first 3 rows (enough to see the shape without bloating
        # the appendix). Fall back to a bare count note if no rows were stored.
        preview = _render_results(q.get("results"), max_rows=3)
        if preview:
            lines += preview
        else:
            count = q.get("row_count")
            note = (
                f"{count} row(s) — results omitted"
                if count is not None
                else "results omitted"
            )
            lines += [f"_{note}_", ""]
    return lines


def _render_results(results: Any, max_rows: int | None = None) -> list[str]:
    """Render a query's results as markdown lines (table, code block, or note).

    ``max_rows`` caps how many rows are tabulated — a preview — while the row
    count stays the true total, with a "showing first N" note when the table is
    capped below it. None (default) tabulates every stored row.
    """
    if results is None:
        return []
    # SPARQL json shape from `sparql_query`: {"vars", "rows", "row_count"}.
    if isinstance(results, dict) and "rows" in results:
        rows = results.get("rows") or []
        cols = results.get("vars") or (list(rows[0].keys()) if rows else [])
        count = results.get("row_count", len(rows))
        return _rows_section(cols, rows, count, max_rows)
    # csv/tsv shape: {"format", "text"}.
    if isinstance(results, dict) and "text" in results:
        fmt = results.get("format", "")
        text = str(results["text"]).strip()
        fence = f"```{fmt}".rstrip()
        lines = text.split("\n")
        # First line is the header row (SPARQL csv/tsv always carries one); cap the
        # DATA rows at max_rows so a large export doesn't dump verbatim. Leave the
        # block untouched when uncapped or already within the cap.
        data = lines[1:]
        if max_rows is None or len(data) <= max_rows:
            return [fence, text, "```", ""]
        block = "\n".join(lines[: 1 + max_rows])
        note = f"_{len(data)} row(s) — showing first {max_rows}_"
        return [note, "", fence, block, "```", ""]
    # A bare list of row dicts.
    if isinstance(results, list):
        cols = (
            list(results[0].keys()) if results and isinstance(results[0], dict) else []
        )
        return _rows_section(cols, results, len(results), max_rows)
    # Anything else: show as text.
    return ["```", str(results).strip(), "```", ""]


def _rows_section(
    cols: list[str], rows: list[dict[str, Any]], count: int, max_rows: int | None
) -> list[str]:
    """Build a row-count label plus the rows as a table, capping at ``max_rows``.

    A preview: a single-row result thus shows in full; a larger one shows its
    first ``max_rows`` with a note that the table was trimmed.
    """
    shown = rows[:max_rows] if max_rows is not None else rows
    label = (
        f"_{count} row(s) — showing first {len(shown)}_"
        if len(shown) < count
        else f"_{count} row(s)_"
    )
    return [label, "", *_rows_to_table(cols, shown)]


def _rows_to_table(cols: list[str], rows: list[dict[str, Any]]) -> list[str]:
    """Render rows (list of {col: value}) as a GitHub-flavored markdown table."""
    if not cols or not rows:
        return ["_(no rows)_", ""]

    def cell(value: Any) -> str:
        return (
            "" if value is None else str(value).replace("|", "\\|").replace("\n", " ")
        )

    out = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    out += ["| " + " | ".join(cell(r.get(c)) for c in cols) + " |" for r in rows]
    out.append("")
    return out

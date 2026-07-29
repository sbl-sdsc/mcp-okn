"""Transcript/logging tools.

reset_query_log, get_query_log, create_chat_transcript, and the
latest-transcript MCP resource.
"""

from __future__ import annotations

import re
from datetime import date as _date
from datetime import datetime, timezone
from typing import Any

from sparql_to_mermaid import try_to_mermaid

from .. import __version__, session
from ..app import mcp
from ..mermaid_namespace import namespace_document
from ..sparql import FEDERATION_ENDPOINT, named_graph

# NOTE: turning per-query diagrams OFF (include_query_diagrams=False) is only HALF the defer-and-re-add
# flow — the diagrams must be re-added before delivering (see the `include_query_diagrams` arg doc and
# report-style's expand_query_diagrams.py / `readd_query_diagrams.py --check` delivery gate). The server
# deliberately does NOT prepend a re-add reminder to the returned document: it was an HTML comment the
# caller saved verbatim, so it stayed baked into the artifact (and read stale once diagrams were added).


@mcp.tool()
async def reset_query_log(scope: str | None = None) -> dict[str, Any]:
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

    Returns:
        `{"cleared": N, "scope": ..., "active_scopes": [...]}`. If `active_scopes`
        shows scopes you did not create, other analyses ARE running concurrently
        in this session — pass a `scope` from here on.
    """
    removed = session.reset(scope)
    return {
        "cleared": removed,
        "scope": scope or session.DEFAULT_SCOPE,
        "active_scopes": session.scopes(),
    }


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


def _clean_skills(skills: list[str] | None) -> list[str]:
    """Normalise a caller-supplied skills list for the provenance header.

    Strips blanks and de-duplicates while preserving the caller's order. The server cannot
    observe which skills were active in the client's session, so the entries are rendered
    verbatim — whatever the caller passes (ideally ``name vX.Y.Z``) is what the record claims.
    """
    seen: list[str] = []
    for skill in skills or []:
        text = str(skill).strip()
        if text and text not in seen:
            seen.append(text)
    return seen


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
    recovery: str = "",
) -> str:
    """Return a compact stand-in when the full transcript is too large to hand back.

    Over `max_inline_chars`, the complete document is published verbatim at the
    resource `transcript://session/latest`; this stub carries the provenance + size
    and points the caller there, so it never reconstructs a truncated one. When
    ``recovery`` is given, it is appended as a second blockquote — a tool-specific,
    ACTIONABLE way to obtain an inline-fitting document (e.g. curating a lean record's
    `supporting` set), so the stub is a next step, not a dead end.
    """
    kg_list = ", ".join(f"`{k['shortname']}`" for k in kgs) or "_none_"
    lines = [
        f"# {title} — full transcript delivered via resource",
        "",
        f"- **Date:** {when}",
        f"- **Model:** {model}",
        *([f"- **Skills:** {' · '.join(skills)}"] if skills else []),
        f"- **Generated by:** {mcp.name} v{__version__}",
        f"- **Knowledge graphs used:** {kg_list}",
        f"- **Size:** {n_chars:,} characters · {n_lines:,} lines · "
        f"{n_queries} queries · {n_viz} visualizations",
        "",
        f"> This transcript ({n_chars:,} chars) exceeds the inline result size, "
        "so the full body was NOT returned here — returning it risks a harness "
        "spill/truncation and a fabricated substitute. The COMPLETE, verbatim "
        "markdown is published at the read-only MCP resource "
        "`transcript://session/latest`: the client can fetch/save it DIRECTLY, "
        "bypassing the size limit and the model's context (this works even when "
        "the server is hosted remotely). Point the user there — do NOT "
        "hand-write, summarize, or reconstruct a substitute transcript.",
    ]
    if recovery:
        lines += ["", f"> **To return it inline instead:** {recovery}"]
    return "\n".join(lines)


def _resolve_sources(
    log: list[dict[str, Any]],
    visualizations: list[dict[str, Any]],
    kgs_used: list[str] | None,
    *,
    check_phantom: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Resolve the KGs a transcript is about and guard its provenance.

    Shared by ``create_chat_transcript`` and ``create_reproducibility_record``.
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
    stub_recovery: str = "",
    active_window: str = "",
    window_label: str = "Study active window",
    prompt: str = "",
    notes: str = "",
    skills: list[str] | None = None,
) -> str:
    """Assemble header + Contents manifest + body, publish, and return the document.

    Shared by ``create_chat_transcript`` and ``create_reproducibility_record``. The
    Contents manifest is derived from what actually rendered (fenced-block counts),
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
        stub_recovery: Optional actionable recovery hint appended to the stub (e.g.
            how to curate a lean record so it fits inline), so an over-size result is
            a next step rather than a dead end.
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
            ``_clean_skills``. Rendered verbatim as a ``- **Skills:**`` header line
            directly beneath "Model" — the two together are the agent's configuration
            (which model, following which methodology), where the endpoint and
            "Generated by" describe the service. Empty = the line is omitted entirely.
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
        f"- **SPARQL endpoint:** {FEDERATION_ENDPOINT}",
        f"- **Generated by:** {mcp.name} v{__version__}",
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
            recovery=stub_recovery,
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
        model: The model version that produced the analysis
            (e.g. `claude-opus-4-8`). Use the exact model ID.
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
        format: `markdown` (default) for a rendered document string, or `json`
            for the structured fields.
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
            would otherwise spill) — but that is only HALF the flow: RE-ADD the
            diagrams before delivering, via report-style's
            `scripts/expand_query_diagrams.py`, and verify with
            `readd_query_diagrams.py --check` (the delivery gate). Skip the re-add
            only if the user asked for no diagrams.
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
        skills: OPTIONAL agent skills that shaped this analysis, each as
            `"<name> v<version>"` (e.g. `["okn-bioanalysis v0.1.0",
            "okn-report-style v0.1.1"]`) — the version is the skill's frontmatter
            `metadata.version`. Rendered as a `- **Skills:**` header line directly
            beneath "Model", omitted when not passed. The server CANNOT see which skills your session
            loaded, so this is caller-supplied: list only skills you actually
            followed, exactly as `model` names the model that actually ran. Naming
            a skill you did not use is a phantom source, same as an unqueried KG.

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
    skill_list = _clean_skills(skills)
    log = session.entries(scope) if include_query_log else []
    visualizations = session.visualizations(scope) if include_visualizations else []
    # Drop foreign queries, infer/verify the KGs, and collect provenance warnings.
    log, kgs, warnings = _resolve_sources(
        log, visualizations, kgs_used, check_phantom=include_query_log
    )

    if format == "json":
        payload: dict[str, Any] = {
            "title": title,
            "date": when,
            "model": model,
            "exchanges": exchanges,
            "knowledge_graphs": kgs,
            "query_log": log,
            "visualizations": visualizations,
            "sparql_endpoint": FEDERATION_ENDPOINT,
            "generated_by": {"service": mcp.name, "version": __version__},
        }
        if skill_list:
            payload["skills"] = skill_list
        if warnings:
            payload["warnings"] = warnings
        return payload

    if format != "markdown":
        return {"error": f"Unsupported format {format!r}; use 'markdown' or 'json'."}

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

    return _finalize_document(
        title=title,
        when=when,
        model=model,
        kgs=kgs,
        body=body,
        warnings=warnings,
        n_schema_diagrams=len(visualizations),
        n_queries_for_stub=len(log),
        n_viz_for_stub=len(visualizations),
        scope=scope,
        max_inline_chars=max_inline_chars,
        skills=skill_list,
    )


@mcp.tool()
async def create_reproducibility_record(
    model: str,
    kgs_used: list[str] | None = None,
    supporting: list[dict[str, Any] | int] | None = None,
    date: str | None = None,
    format: str = "markdown",
    title: str = "Proto-OKN Reproducibility Record",
    include_query_diagrams: bool = True,
    diagram_max_chars: int = 1500,
    scope: str | None = None,
    max_inline_chars: int | None = 100_000,
    notes: str | None = None,
    chat_started: str | None = None,
    chat_ended: str | None = None,
    appendix: str | None = None,
    prompt: str | None = None,
    skills: list[str] | None = None,
) -> Any:
    """Build the reproducibility record: header + replicator spec + supporting queries.

    The SINGLE reproducibility deliverable (`<study>_reproducibility.md`): it merges
    what were two files — the replicator SPEC (rules, thresholds, joins, verified
    quantities, limitations) you pass as `appendix`, and the verbatim query record
    this tool generates. A compact alternative to `create_chat_transcript`, it keeps
    only what lets someone RE-RUN the analysis — a provenance header, your `appendix`
    spec, and the SPARQL queries that support the reported findings (verbatim, pulled
    from the session log, NOT re-typed), each query's row COUNT, and a per-query
    diagram when it fits — and drops the conversation prose, the full result tables,
    and schema visualizations. That keeps it small enough to return INLINE in the
    common case, so you save the returned string DIRECTLY to the `.md` file — no
    resource round-trip, no stub.

    Run the analysis first: the queries come from the auto-log (every
    non-exploratory, row-returning `sparql_query`), so DO NOT hand-write this record.
    The full result data belongs in the workbook / `data/` extracts, not here.

    Args:
        model: The exact model id producing the analysis (e.g. `claude-opus-4-8`).
        kgs_used: Shortnames of the knowledge graphs this record is about. If
            omitted, inferred from the selected queries. When given, drives the same
            guards as `create_chat_transcript`: a logged query touching none of them
            is dropped as foreign (a concurrent subagent's leak — pass a unique
            `scope`), and a named KG that no selected query touched is flagged a
            phantom source (its contribution cannot be reproduced — re-run the
            establishing query non-exploratory, or drop the KG).
        supporting: OPTIONAL curation. None = all logged queries in log order.
            Otherwise a list where each item is either a bare 1-based index (e.g.
            `supporting=[1, 5, 9]`) or a `{"index": int, "description": str | None}`
            dict (the `description` is an optional heading label); `index` is a
            position into the log in the order `get_query_log` shows. Use it to keep
            only the queries that underpin reported findings, in the order given — the
            lever for shrinking a large log so the record fits inline. **If the record
            comes back as a stub (over `max_inline_chars`), that is not a stopping
            point: you know there are N queries, so re-call with `supporting` to curate
            to the findings-supporting subset, or batch (`list(range(1, 41))`, then
            `range(41, 81)`, …) — never leave the transcript missing.** An out-of-range
            index is skipped with a warning.
        date: ISO date for the header; defaults to today.
        format: `markdown` (default) or `json`.
        title: Document title.
        include_query_diagrams: If true (default), render a Mermaid `graph TD`
            diagram beneath each query, subject to `diagram_max_chars`. Set false
            when a large record would spill — but then RE-ADD the diagrams before
            delivering (report-style's `scripts/expand_query_diagrams.py`; verify
            with `readd_query_diagrams.py --check`), unless the user asked for none.
        diagram_max_chars: Drop a per-query diagram longer than this many characters
            (default 1500) so an oversized diagram never bloats the record; the
            query's SPARQL text still shows.
        scope: OPTIONAL log scope — the same string passed to `reset_query_log` /
            `sparql_query`. Pass a unique label when parallel subagents share one
            MCP session.
        max_inline_chars: Return a compact stub above this size (default 100_000),
            with the full body published to `transcript://session/latest`. A record
            of many verbatim queries with large `VALUES` lists can still exceed this
            — curate `supporting` to fewer queries, or raise this on a client that
            can handle a larger inline result.
        chat_started: OPTIONAL ISO-8601 timestamp of when the CHAT began (e.g.
            `2026-07-18T09:00:00Z`). When given, the header's timing line shows the
            WHOLE-CHAT elapsed time — `- **Elapsed time:** <start>–<end> UTC
            (<elapsed>)` — INSTEAD of the "Study active window" (which spans only the
            first-to-last logged query and so undercounts, badly if large extraction
            queries went unlogged). The server cannot know the chat's duration on its
            own, so YOU must pass this — the caller is the only party that knows when
            the conversation started. Omit it to keep the active-query-window line.
        chat_ended: OPTIONAL ISO-8601 end timestamp for the whole-chat window; only
            used with `chat_started`. Defaults to now (UTC) — the record's generation
            moment, a fair stand-in for the end of the chat.
        notes: OPTIONAL methodology note, rendered as a VISIBLE `## Notes` section
            just under the header. This is the SANCTIONED place for provenance
            context — e.g. that the logged queries are compact COUNT/aggregate
            re-registrations while the full extraction SELECTs (auto-saved to
            tool-result files, hence unlogged) live in `scripts/`. Put such context
            HERE rather than hand-editing the saved `.md` after the fact: the record
            must be saved exactly as returned, so any note added outside the tool
            (e.g. an HTML-comment preamble) both breaks that contract and, being an
            HTML comment, is invisible to a reader anyway.
        prompt: OPTIONAL originating user prompt — the request that kicked off the
            study — rendered as a `## Prompt` section at the TOP of the record so the
            document is self-contained (a replicator sees the question the analysis
            answered). Paste the user's prompt VERBATIM; don't paraphrase it.
        appendix: OPTIONAL replicator SPEC in Markdown — the rules, thresholds, join
            definitions, key verified quantities, downstream computation, and
            reproducibility limitations that used to be a SEPARATE
            `<study>_reproducibility_appendix.md`. Passing it here merges the two
            reproducibility files into ONE: the content is rendered as its own
            section(s) between the header and the `## SPARQL queries` record (author
            it with your own `##` headings; it is inserted verbatim). This is the
            human-readable spec; the queries below are the machine-checkable evidence.
            Unlike `notes` (a short caption), this is the full multi-section document.
            It is authored by you (the queries can't express thresholds/limitations),
            so — like `notes` — put it here, never by hand-editing the saved file.
        skills: The agent skills that shaped this study, each as `"<name> v<version>"`
            (e.g. `["okn-bioanalysis v0.1.0", "okn-report-style v0.1.1"]`) — the version
            is the skill's frontmatter `metadata.version`. Rendered as a `- **Skills:**`
            header line directly beneath "Model" (together they are the agent's
            configuration: which model, following which methodology). Technically
            optional, but PASS IT whenever a skill was followed: the server cannot see
            which skills your session loaded, so omitting it silently publishes a record
            that claims no methodology — the tool returns a WARNING when you do, and the
            fix is to call again with `skills=[...]`, never to hand-add the line to the
            saved file. List only skills you actually followed — naming one you didn't
            is a phantom source, same as an unqueried KG.

    Returns:
        A Markdown string (or a dict when `format="json"`): the header, any `appendix`
        spec, a `## SPARQL queries` section (one verbatim query + row count + optional
        diagram each), and a Contents manifest. Provenance warnings, if any, are
        prepended as HTML comments (invisible in a saved `.md`).
    """
    when = date or _date.today().isoformat()
    skill_list = _clean_skills(skills)
    log = session.entries(scope)

    # Curate to the supporting subset (1-based indices into the log), in the order
    # given, attaching any per-item heading label. None -> the whole log in order.
    warnings: list[str] = []
    # `skills` is the one header field the server cannot derive — it knows the model,
    # its own version, the endpoint and the query log, but not which skills the client's
    # session loaded. So an omitted list is indistinguishable from "no methodology", and
    # a silently absent line is only ever noticed later (if at all). Say so HERE, at the
    # moment the record is generated, while regenerating is still a single call.
    if not skill_list:
        warnings.append(
            "no `skills=` passed, so the header has no `- **Skills:**` line and the "
            "record claims no methodology at all. If any skill shaped this analysis "
            "(okn-report-style, okn-bioanalysis, …), call again with "
            "`skills=['<name> v<version>', …]` — version from each skill's frontmatter "
            "`metadata.version` — and save THAT result. Do not hand-add the line to the "
            "saved file. If no skill was used, this warning is correctly ignored."
        )
    if supporting is None:
        selected = list(log)
    else:
        selected = []
        for item in supporting:
            # An item may be a bare 1-based index (easy batching:
            # `supporting=[1, 2, 3]`) or a `{"index": int, "description": str}` dict.
            if isinstance(item, dict):
                idx = item.get("index")
                desc = item.get("description")
            else:
                idx, desc = item, None
            if (
                not isinstance(idx, int)
                or isinstance(idx, bool)
                or not (1 <= idx <= len(log))
            ):
                plural = "y" if len(log) == 1 else "ies"
                warnings.append(
                    f"`supporting` index {idx!r} is out of range for a log of "
                    f"{len(log)} quer{plural} — skipped."
                )
                continue
            entry = dict(log[idx - 1])
            if desc:
                entry["description"] = desc
            selected.append(entry)

    # Same foreign-drop / KG-inference / phantom guards as the full transcript, run
    # against the SELECTED queries (the record is about those). No visualizations.
    selected, kgs, guard_warnings = _resolve_sources(
        selected, [], kgs_used, check_phantom=True
    )
    warnings += guard_warnings

    # Choose the header timing line. When the caller supplied a chat start, show the
    # WHOLE-CHAT elapsed window (only the caller knows when the chat began); otherwise
    # fall back to the active-query window, which spans the whole scoped log (not just
    # the curated `supporting` subset) — the study took that long regardless of which
    # queries the record keeps.
    window = _chat_window(chat_started, chat_ended) if chat_started else None
    if chat_started and window is None:
        warnings.append(
            f"chat_started={chat_started!r} (or chat_ended) is not a parseable ISO-8601 "
            "timestamp — fell back to the active-query window for the timing line."
        )
    if window is not None:
        window_label = "Elapsed time"
    else:
        window, window_label = _active_window(log), "Study active window"

    if format == "json":
        payload: dict[str, Any] = {
            "title": title,
            "date": when,
            "model": model,
            "knowledge_graphs": kgs,
            "query_log": selected,
            "sparql_endpoint": FEDERATION_ENDPOINT,
            "generated_by": {"service": mcp.name, "version": __version__},
        }
        if prompt and prompt.strip():
            payload["prompt"] = prompt.strip()
        if skill_list:
            payload["skills"] = skill_list
        if window:
            payload["elapsed_window"] = {"label": window_label, "value": window}
        if notes and notes.strip():
            payload["notes"] = notes.strip()
        if appendix and appendix.strip():
            payload["appendix"] = appendix.strip()
        if warnings:
            payload["warnings"] = warnings
        return payload

    if format != "markdown":
        return {"error": f"Unsupported format {format!r}; use 'markdown' or 'json'."}

    # The authored replicator spec (former separate appendix file) leads, then the
    # machine-checkable query record. Inserted verbatim, with the author's own headings.
    body: list[str] = []
    if appendix and appendix.strip():
        body += [appendix.strip(), ""]
    body += ["## SPARQL queries", ""]
    if not selected:
        body += ["_No queries logged._", ""]
    for k, entry in enumerate(selected, start=1):
        ctx = entry.get("timestamp", "")
        graphs = entry.get("graphs") or []
        if graphs:
            ctx += " · " + ", ".join(f"`{g}`" for g in graphs)
        body += _render_query(
            entry,
            f"Query {k}",
            subheading=ctx,
            counts_only=True,
            diagram=include_query_diagrams,
            diagram_max_chars=diagram_max_chars,
        )

    return _finalize_document(
        title=title,
        when=when,
        model=model,
        kgs=kgs,
        body=body,
        warnings=warnings,
        n_schema_diagrams=0,
        n_queries_for_stub=len(selected),
        n_viz_for_stub=0,
        scope=scope,
        max_inline_chars=max_inline_chars,
        active_window=window,
        window_label=window_label,
        prompt=prompt or "",
        notes=notes or "",
        skills=skill_list,
        stub_recovery=(
            "a too-large record is NOT a reason to leave the transcript missing. "
            "The queries are all logged, so CURATE (not fabricate) an inline-fitting "
            "record: call again with `supporting=[1, 5, 9, …]` — bare 1-based "
            f"positions into the log (there are {len(selected)}; `get_query_log` "
            "lists them in order, so you always know the indices) — keeping the "
            "queries that support your reported findings. If you genuinely need every "
            "query, split into batches (`supporting=list(range(1, 41))`, then "
            "`range(41, 81)`, …) and save each. Don't just point at the resource and stop."
        ),
    )


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
    counts_only: bool = False,
) -> list[str]:
    """Render one query (verbatim text + results or error) as markdown lines.

    When ``counts_only`` is True, no result table or preview is rendered — only a
    ``_N row(s)_`` line from the entry's ``row_count`` — for a lean reproducibility
    record where the queries (not their data) are the point. Otherwise, when
    ``show_results`` is True the result table is rendered, capped at ``max_rows``
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
    elif counts_only:
        count = q.get("row_count")
        lines += [f"_{count} row(s)_" if count is not None else "_results omitted_", ""]
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

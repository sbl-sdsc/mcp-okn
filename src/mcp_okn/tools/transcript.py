"""Transcript/logging tools: reset_query_log, get_query_log,
create_chat_transcript, and the latest-transcript MCP resource."""

from __future__ import annotations

import re
from datetime import date as _date
from typing import Any

from .. import session
from ..app import mcp
from ..sparql import FEDERATION_ENDPOINT, named_graph


@mcp.tool()
async def reset_query_log() -> dict[str, Any]:
    """Clear the session's query log (and logged diagrams) for a fresh scope.

    Call this at the START of a new analysis. Every subsequent `sparql_query`
    (and `expand_ontology_term`) call is logged automatically, as is every
    `visualize_schema` diagram, and `create_chat_transcript` renders them as the
    ground-truth record of what actually ran — so you don't have to re-supply
    queries or diagrams from memory.
    """
    removed = session.reset()
    return {"cleared": removed}


@mcp.tool()
async def get_query_log() -> list[dict[str, Any]]:
    """Return the SPARQL queries logged so far this session, in execution order.

    Only queries that returned rows and were not marked exploratory are present.
    Each entry has `timestamp`, `sparql` (verbatim), `graphs` (KG shortnames),
    `format`, `row_count`, and `results` (capped sample). Useful to inspect what
    will appear in `create_chat_transcript`.
    """
    return session.entries()


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
    max_result_rows: int | None = 5,
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
            federation named-graph URI.
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

    Returns:
        For `markdown`: the transcript string. Each conversation turn is
        rendered in the mcp-proto-okn style — a "👤 **User**" block (the prompt)
        and a "🧠 **Assistant**" block (the answer), separated by a rule — with
        queries in fenced ```sparql blocks (plus result tables) and schema
        diagrams in fenced ```mermaid blocks under the answer.
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
    log = session.entries() if include_query_log else []
    visualizations = session.visualizations() if include_visualizations else []

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

    if format == "json":
        return {
            "title": title,
            "date": when,
            "model": model,
            "exchanges": exchanges,
            "knowledge_graphs": kgs,
            "query_log": log,
            "visualizations": visualizations,
            "sparql_endpoint": FEDERATION_ENDPOINT,
        }

    if format != "markdown":
        return {"error": f"Unsupported format {format!r}; use 'markdown' or 'json'."}

    lines = [
        f"# {title}",
        "",
        f"- **Date:** {when}",
        f"- **Model:** {model}",
        f"- **SPARQL endpoint:** {FEDERATION_ENDPOINT}",
        "",
        "## Knowledge graphs used",
        "",
    ]
    if kgs:
        lines += [f"- `{kg['shortname']}` — <{kg['named_graph']}>" for kg in kgs]
    else:
        lines.append("- _None queried._")

    lines += ["", "## Conversation", ""]
    if not exchanges:
        lines += ["_No prompts recorded._", ""]
    for exchange in exchanges:
        # mcp-proto-okn style: each turn is a 👤 User block and a 🧠 Assistant
        # block separated by a rule; queries/diagrams render under the answer.
        lines += [
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
            lines += [answer, ""]
        # Only findings-producing queries belong in the transcript; drop any
        # the model flagged exploratory so schema-probing never leaks in.
        shown = [q for q in (exchange.get("queries") or []) if not q.get("exploratory")]
        for j, q in enumerate(shown, start=1):
            lines += _render_query(q, f"Query {j}", max_rows=max_result_rows)
        # Optional Mermaid diagram(s) attached inline to this turn.
        inline = exchange.get("mermaid")
        for diagram in [inline] if isinstance(inline, str) else (inline or []):
            if (diagram or "").strip():
                lines += ["```mermaid", diagram.strip(), "```", ""]

    if log:
        lines += ["## SPARQL queries executed", ""]
        for k, entry in enumerate(log, start=1):
            ctx = entry.get("timestamp", "")
            graphs = entry.get("graphs") or []
            if graphs:
                ctx += " · " + ", ".join(f"`{g}`" for g in graphs)
            # By default only the final query's rows are shown; intermediate
            # queries list their text and row count but omit the result table.
            show_results = include_intermediate_rows or k == len(log)
            lines += _render_query(
                entry,
                f"Query {k}",
                subheading=ctx,
                show_results=show_results,
                max_rows=max_result_rows,
            )

    if visualizations:
        lines += ["## Schema visualizations", ""]
        for viz in visualizations:
            shortname = viz.get("shortname", "")
            ctx = viz.get("timestamp", "")
            lines += [f"### `{shortname}` schema", ""]
            if ctx:
                lines += [f"_{ctx}_", ""]
            lines += ["```mermaid", (viz.get("mermaid") or "").strip(), "```", ""]

    markdown = "\n".join(lines)
    # Publish for direct client fetch/save via the transcript resource.
    session.set_last_transcript(markdown)
    return markdown


@mcp.resource(
    "transcript://session/latest",
    name="Latest chat transcript",
    description=(
        "The most recent transcript rendered by create_chat_transcript this "
        "session, as Markdown. Lets a client fetch/save the document directly, "
        "independent of how the model re-emits it."
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
) -> list[str]:
    """Render one query (verbatim text + results or error) as markdown lines.

    When ``show_results`` is True the result table is rendered, capped at
    ``max_rows`` (``None`` = uncapped). When ``show_results`` is False, only a
    compact PREVIEW of the rows is shown (a single-row result in full, otherwise
    the first 3 rows) instead of the full table — used for intermediate queries in
    the log appendix to keep it focused while still surfacing small results that
    cost almost no space.
    """
    desc = _clean_description(q.get("description"))
    heading = f"#### {label}" + (f" — {desc}" if desc else "")
    lines = [heading, ""]
    if subheading:
        lines += [f"_{subheading}_", ""]
    lines += ["```sparql", (q.get("sparql") or "").strip(), "```", ""]
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
    """A row-count label plus the rows as a table, capping at ``max_rows`` (a
    preview). A single-row result thus shows in full; a larger one shows its
    first ``max_rows`` with a note that the table was trimmed."""
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

"""Build a re-runnable Jupyter study folder from a session's query log.

The ``create_jupyter_notebook`` tool turns the logged queries — the server's ground
truth of what ran — plus the code, cells and figures the agent produced on its side
into one self-contained folder::

    <study>/
      <study>.ipynb       provenance header, one cell per query, the analysis cells
      okn_sparql.py       run_query()/verify_all(): stdlib HTTP + pandas, no mcp-okn
      queries/qNN.rq      each query verbatim, as logged
      queries/sent/qNN.rq the text the server actually POSTed, when its rewrites changed it
      queries/manifest.json  per query: graphs, timestamp, logged row count, cache file
      data/qNN.csv        the logged rows (capped at session.MAX_LOGGED_ROWS)
      <code files>        the agent's own modules, importable from the notebook
      figures/…           named here, copied in by the agent (or by a local server)
      requirements.txt
      README.md

Everything here is a pure function of its inputs, so the folder is the same whether
the hosted server returns it as a file map or a local server writes it to disk.

The notebook loads ``data/`` by default and executes nothing against the endpoint,
so it opens with the session's results already in place; ``RERUN = True`` replays
every query live and ``verify_all()`` reports each query's row count against the
logged one. A drifted count means the graph was redeployed, not that the study
is wrong — see the README this writes.
"""

from __future__ import annotations

import csv
import html
import io
import json
import re
import shlex
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from .sparql import prepare_query

#: Rows of each query's logged result shown as the cached cell output. The full
#: logged sample is in ``data/``; this only keeps the .ipynb small.
PREVIEW_ROWS = 10

#: Files and folders the builder writes itself; caller files may not land on them.
_RESERVED_FILES = ("okn_sparql.py", "requirements.txt", "README.md")
_RESERVED_DIRS = ("queries",)

#: Always in requirements.txt; the caller's extras are appended after these.
BASE_REQUIREMENTS = ("pandas>=1.5",)


@dataclass
class StudyFolder:
    """The built folder: relative path → text, plus what the caller must add."""

    name: str
    notebook: str
    files: dict[str, str] = field(default_factory=dict)
    #: Figures the notebook embeds but the server cannot see: ``{path, source?}``.
    figures: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def slugify(text: str, default: str = "okn-study") -> str:
    """A lowercase, hyphenated folder/file name (at most 60 characters)."""
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()[:60].strip("-")
    return slug or default


def safe_relative_path(path: str) -> str | None:
    """``path`` as a clean relative POSIX path inside the folder, or None if unsafe.

    Rejects absolute paths, ``..`` segments, backslashes and empty names, so a
    caller-supplied name can never point outside the study folder.
    """
    if not isinstance(path, str) or not path.strip() or "\\" in path:
        return None
    p = PurePosixPath(path.strip())
    if p.is_absolute() or any(part in ("..", "") for part in p.parts):
        return None
    clean = str(p)
    return None if clean in (".", "") else clean


def _is_reserved(path: str, notebook: str) -> bool:
    top = path.split("/", 1)[0]
    return path in (*_RESERVED_FILES, notebook) or top in _RESERVED_DIRS


def _lines(text: str) -> list[str]:
    """Notebook ``source``: a list of lines, each but the last ending in a newline."""
    return text.splitlines(keepends=True) if text else []


def _cell_id(n: int) -> str:
    return f"cell-{n:03d}"


def _markdown_cell(n: int, text: str) -> dict[str, Any]:
    return {
        "cell_type": "markdown",
        "id": _cell_id(n),
        "metadata": {},
        "source": _lines(text),
    }


def _code_cell(
    n: int,
    text: str,
    outputs: list[dict[str, Any]] | None = None,
    count: int | None = None,
) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "id": _cell_id(n),
        "metadata": {},
        "execution_count": count if outputs else None,
        "outputs": outputs or [],
        "source": _lines(text),
    }


def _cell_text(value: Any) -> str:
    return "" if value is None else str(value)


def _preview_output(
    columns: list[str], rows: list[dict[str, Any]], total: int, count: int
) -> dict[str, Any]:
    """An ``execute_result`` showing the first logged rows as an HTML + text table."""
    shown = rows[:PREVIEW_ROWS]
    head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
    body = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(_cell_text(r.get(c)))}</td>" for c in columns)
        + "</tr>"
        for r in shown
    )
    note = f"<p>{len(shown)} of {total:,} rows (cached from the session log)</p>"
    table = f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
    widths = {
        c: max([len(c), *(len(_cell_text(r.get(c))) for r in shown)]) for c in columns
    }
    plain = [
        "  ".join(c.ljust(widths[c]) for c in columns),
        *(
            "  ".join(_cell_text(r.get(c)).ljust(widths[c]) for c in columns)
            for r in shown
        ),
        f"[{len(shown)} of {total:,} rows]",
    ]
    return {
        "output_type": "execute_result",
        "execution_count": count,
        "metadata": {},
        "data": {
            "text/html": _lines(table + note),
            "text/plain": _lines("\n".join(line.rstrip() for line in plain)),
        },
    }


def _rows_csv(columns: list[str], rows: list[dict[str, Any]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_cell_text(row.get(c)) for c in columns])
    return buf.getvalue()


def _header_markdown(
    *,
    title: str,
    when: str,
    model: str,
    skills: list[str],
    mcp_servers: list[str],
    endpoint: str,
    generated_by: str,
    kgs: list[dict[str, Any]],
    n_queries: int,
    prompt: str,
    notes: str,
) -> str:
    lines = [
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
        f"- **SPARQL endpoint:** {endpoint}",
        f"- **Generated by:** {generated_by}",
        f"- **Queries:** {n_queries}",
        "- **Knowledge graphs used:** "
        + (", ".join(f"`{k['shortname']}`" for k in kgs) or "_none_"),
    ]
    if prompt.strip():
        lines += ["", "## Prompt", "", prompt.strip()]
    if notes.strip():
        lines += ["", "## Notes", "", notes.strip()]
    return "\n".join(lines)


_RERUN_MARKDOWN = """\
## Re-running this study

Every query cell loads the rows the session logged (`data/`), so the notebook runs \
offline and shows the original results. Set `RERUN = True` in the next cell (or \
start Jupyter with `OKN_RERUN=1`) to re-execute every query live against the OKN \
federation instead, or run the last cell (`verify_all()`) to compare each query's \
live row count with the logged one. \
A changed count usually means the knowledge graph was redeployed since the study \
ran, not that the analysis is wrong."""

_SETUP_CODE = """\
import os

import pandas as pd

from okn_sparql import run_query, verify_all

# False: load the rows logged during the session (data/). True: re-run each query live.
# Starting Jupyter with OKN_RERUN=1 sets it without editing the notebook.
RERUN = os.environ.get("OKN_RERUN", "") == "1"
data: dict[str, pd.DataFrame] = {}"""


def run_commands(folder: str, notebook: str) -> dict[str, str]:
    """Shell commands that open the notebook in JupyterLab, and rerun it headless.

    The folder is self-contained (its ``requirements.txt`` lists everything the
    notebook imports), so ``uv run`` builds a throwaway environment from it; no
    mcp-okn checkout or install is needed. ``folder`` is where the study folder
    is on the user's machine; the notebook's own directory must be the working
    directory, because its cells import ``okn_sparql`` and the caller's modules.
    """
    q = shlex.quote
    stem = notebook.removesuffix(".ipynb")
    cd = f"cd {q(folder)}"
    return {
        "jupyter": f"{cd}\nuv run --with jupyterlab --with-requirements "
        f"requirements.txt jupyter lab {q(notebook)}",
        "nbconvert": f"{cd}\nOKN_RERUN=1 uv run --with nbconvert --with ipykernel "
        "--with-requirements requirements.txt jupyter nbconvert --to notebook "
        f"--execute --output {q(stem + '-rerun.ipynb')} {q(notebook)}",
    }


def build_study(
    *,
    title: str,
    when: str,
    model: str,
    entries: list[dict[str, Any]],
    kgs: list[dict[str, Any]],
    endpoint: str,
    generated_by: str,
    skills: list[str] | None = None,
    mcp_servers: list[str] | None = None,
    prompt: str = "",
    notes: str = "",
    folder_name: str | None = None,
    code_files: dict[str, str] | None = None,
    cells: list[dict[str, Any]] | None = None,
    figures: list[dict[str, Any]] | None = None,
    requirements: list[str] | None = None,
    include_data: bool = True,
) -> StudyFolder:
    """Assemble the study folder. See the module docstring for the layout.

    Args:
        title: Notebook and README title.
        when: Date for the header.
        model: Model id for the header.
        entries: The selected session-log entries, in order; each may carry a
            ``description`` (a heading label).
        kgs: ``[{shortname, named_graph}]`` the study is about.
        endpoint: The SPARQL endpoint the helper module queries.
        generated_by: The "Generated by" provenance string.
        skills: Skills for the header, already cleaned.
        mcp_servers: External MCP servers for the header, already cleaned.
        prompt: Originating prompt, rendered verbatim (empty = omitted).
        notes: Methodology note (empty = omitted).
        folder_name: Folder/notebook name before slugging (default: ``title``).
        requirements: Extra pip requirements after :data:`BASE_REQUIREMENTS`.
        code_files: The agent's own text files (``analysis.py`` …), relative path →
            content, written verbatim. The notebook's folder is its working
            directory, so a module at the top level is importable from a cell.
        cells: Analysis cells appended after the query cells, each
            ``{"type": "markdown" | "code", "source": str}``. Code cells carry no
            outputs (the server never saw them run); they can use
            ``data["q01"]`` … and import ``code_files`` modules.
        figures: ``{"path": "figures/x.png", "caption": str, "source"?: str}``;
            embedded as Markdown images. The files themselves are the caller's.
        include_data: Write each query's logged rows to ``data/``. Without them the
            notebook re-runs every query live on first execution.
    """
    name = slugify(folder_name or title)
    notebook = f"{name}.ipynb"
    study = StudyFolder(name=name, notebook=notebook)
    skills = skills or []
    mcp_servers = mcp_servers or []

    nb_cells: list[dict[str, Any]] = []

    def add(cell_fn: Any, *args: Any, **kw: Any) -> None:
        nb_cells.append(cell_fn(len(nb_cells) + 1, *args, **kw))

    add(
        _markdown_cell,
        _header_markdown(
            title=title,
            when=when,
            model=model,
            skills=skills,
            mcp_servers=mcp_servers,
            endpoint=endpoint,
            generated_by=generated_by,
            kgs=kgs,
            n_queries=len(entries),
            prompt=prompt,
            notes=notes,
        ),
    )
    add(_markdown_cell, _RERUN_MARKDOWN)
    add(_code_cell, _SETUP_CODE)
    add(
        _markdown_cell,
        "## SPARQL queries" if entries else "## SPARQL queries\n\n_No queries logged._",
    )

    manifest: list[dict[str, Any]] = []
    exec_count = 0
    for k, entry in enumerate(entries, start=1):
        qname = f"q{k:02d}"
        sparql = entry.get("sparql", "")
        study.files[f"queries/{qname}.rq"] = sparql.rstrip("\n") + "\n"
        try:
            sent = prepare_query(sparql)
        except Exception:
            sent = sparql
        rewritten = sent.strip() != sparql.strip()
        if rewritten:
            study.files[f"queries/sent/{qname}.rq"] = sent.rstrip("\n") + "\n"

        results = entry.get("results") or {}
        columns = list(results.get("vars") or [])
        rows = list(results.get("rows") or [])
        total = entry.get("row_count") or results.get("row_count") or len(rows)
        cache: str | None = None
        if include_data:
            if columns or rows:
                if not columns and rows:
                    columns = list(rows[0])
                cache = f"data/{qname}.csv"
                study.files[cache] = _rows_csv(columns, rows)
            elif results.get("text"):
                ext = "tsv" if results.get("format") == "tsv" else "csv"
                cache = f"data/{qname}.{ext}"
                study.files[cache] = str(results["text"])

        graphs = entry.get("graphs") or []
        manifest.append(
            {
                "name": qname,
                "description": entry.get("description") or "",
                "timestamp": entry.get("timestamp", ""),
                "graphs": graphs,
                "row_count": total,
                "cached_rows": len(rows) if cache and rows else (total if cache else 0),
                "truncated": bool(results.get("truncated")),
                "cache": cache,
                "sent": f"queries/sent/{qname}.rq" if rewritten else None,
            }
        )

        heading = f"### {qname}" + (
            f" — {entry['description']}" if entry.get("description") else ""
        )
        meta = [entry.get("timestamp", "")]
        if graphs:
            meta.append(", ".join(f"`{g}`" for g in graphs))
        meta.append(f"{total:,} rows logged" if isinstance(total, int) else "")
        md = [
            heading,
            "",
            " · ".join(m for m in meta if m),
            "",
            "```sparql",
            sparql.strip(),
            "```",
        ]
        if rewritten:
            md += [
                "",
                f"Runs as `queries/sent/{qname}.rq`: the server's result-neutral "
                "plan rewrites, which the endpoint needs to answer it quickly.",
            ]
        if results.get("truncated"):
            md += [
                "",
                f"The cached rows are the first {len(rows):,} of {total:,}; "
                "`RERUN = True` fetches them all.",
            ]
        add(_markdown_cell, "\n".join(md))

        code = f'data["{qname}"] = run_query("{qname}", rerun=RERUN)\ndata["{qname}"].head({PREVIEW_ROWS})'
        outputs = None
        if columns and rows:
            exec_count += 1
            outputs = [_preview_output(columns, rows, total, exec_count)]
        add(_code_cell, code, outputs, exec_count)

    study.files["queries/manifest.json"] = json.dumps(manifest, indent=2) + "\n"

    # The caller's own files: verbatim, inside the folder, never over ours.
    for raw_path, content in (code_files or {}).items():
        path = safe_relative_path(raw_path)
        if path is None:
            study.warnings.append(
                f"code_files path {raw_path!r} is not a safe relative path — skipped."
            )
            continue
        if _is_reserved(path, notebook) or path in study.files:
            study.warnings.append(
                f"code_files path {path!r} collides with a generated file — skipped."
            )
            continue
        study.files[path] = str(content)

    if cells:
        add(_markdown_cell, "## Analysis")
    for i, cell in enumerate(cells or [], start=1):
        kind = (cell or {}).get("type") if isinstance(cell, dict) else None
        source = _cell_text(
            (cell or {}).get("source") if isinstance(cell, dict) else None
        )
        if kind == "markdown":
            add(_markdown_cell, source)
        elif kind == "code":
            add(_code_cell, source)
        else:
            study.warnings.append(
                f"cells[{i}] has type {kind!r}; use 'markdown' or 'code' — skipped."
            )

    figure_md: list[str] = []
    for i, fig in enumerate(figures or [], start=1):
        raw = fig.get("path") if isinstance(fig, dict) else None
        path = safe_relative_path(raw) if isinstance(raw, str) else None
        if path is None or _is_reserved(path, notebook):
            study.warnings.append(f"figures[{i}] path {raw!r} is not usable — skipped.")
            continue
        caption = _cell_text(fig.get("caption")).strip()
        figure_md += [f"![{caption or path}]({path})", ""]
        if caption:
            figure_md += [f"*{caption}*", ""]
        item = {"path": path}
        if fig.get("source"):
            item["source"] = str(fig["source"])
        study.figures.append(item)
    if figure_md:
        add(_markdown_cell, "## Figures\n\n" + "\n".join(figure_md).rstrip())

    add(_markdown_cell, "## Verify against the live graphs")
    add(_code_cell, "verify_all()")

    study.files[notebook] = (
        json.dumps(
            {
                "cells": nb_cells,
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3",
                    },
                    "language_info": {"name": "python"},
                    "okn": {"generated_by": generated_by, "endpoint": endpoint},
                },
                "nbformat": 4,
                "nbformat_minor": 5,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n"
    )
    study.files["okn_sparql.py"] = _HELPER.replace("__ENDPOINT__", endpoint).replace(
        "__GENERATED_BY__", generated_by
    )
    reqs: list[str] = []
    for req in [*BASE_REQUIREMENTS, *(requirements or [])]:
        req = str(req).strip()
        if req and req not in reqs:
            reqs.append(req)
    study.files["requirements.txt"] = "\n".join(reqs) + "\n"
    study.files["README.md"] = _readme(
        title=title,
        when=when,
        model=model,
        generated_by=generated_by,
        kgs=kgs,
        study=study,
        n_queries=len(entries),
        include_data=include_data,
        any_truncated=any(m["truncated"] for m in manifest),
    )
    # Present the map in a stable, readable order: notebook first, then by path.
    study.files = dict(
        sorted(study.files.items(), key=lambda kv: (kv[0] != notebook, kv[0]))
    )
    return study


def _readme(
    *,
    title: str,
    when: str,
    model: str,
    generated_by: str,
    kgs: list[dict[str, Any]],
    study: StudyFolder,
    n_queries: int,
    include_data: bool,
    any_truncated: bool,
) -> str:
    kg_list = ", ".join(f"`{k['shortname']}`" for k in kgs) or "_none_"
    commands = run_commands(f"/path/to/{study.name}", study.notebook)
    own = [
        p
        for p in study.files
        if not _is_reserved(p, study.notebook)
        and not p.startswith("data/q")
        and p != study.notebook
    ]
    layout = [
        f"- `{study.notebook}`: the notebook (provenance, one cell per query, analysis)",
        "- `okn_sparql.py`: `run_query()` / `verify_all()`; needs only pandas",
        "- `queries/`: each query verbatim (`qNN.rq`), the text actually sent when the "
        "server rewrote it (`sent/qNN.rq`), and `manifest.json`",
        *(
            ["- `data/`: the rows each query returned during the session"]
            if include_data
            else []
        ),
        *(f"- `{p}`" for p in own),
        *(f"- `{f['path']}`" for f in study.figures),
        "- `requirements.txt`",
    ]
    caveats = [
        "- The cached rows are what the endpoint returned when the study ran. The "
        "graphs are redeployed from time to time, so a live re-run can differ; "
        "`verify_all()` reports which queries changed.",
    ]
    if any_truncated:
        caveats.append(
            "- Some queries returned more rows than the session log keeps; their "
            "cache holds the first rows only (see `cached_rows` in "
            "`queries/manifest.json`). `RERUN = True` fetches every row."
        )
    if study.figures:
        caveats.append(
            "- Figures are the images the study produced; re-running the analysis "
            "cells regenerates them only if those cells write them."
        )
    return "\n".join(
        [
            f"# {title}",
            "",
            f"Re-runnable study: {n_queries} SPARQL "
            f"{'query' if n_queries == 1 else 'queries'} over {kg_list}, "
            f"run {when} by {model}. Generated by {generated_by}.",
            "",
            "## Run it",
            "",
            "With [uv](https://docs.astral.sh/uv/), from this folder (it builds the "
            "environment from `requirements.txt`):",
            "",
            "```bash",
            commands["jupyter"],
            "```",
            "",
            "Then choose **Run → Run All Cells**. The query cells load the cached "
            "rows; set `RERUN = True` in the setup cell (or start with `OKN_RERUN=1`) "
            "to query the live endpoint instead. To rerun every query live without "
            "opening Jupyter, writing a copy with the new results:",
            "",
            "```bash",
            commands["nbconvert"],
            "```",
            "",
            "Without uv: `pip install -r requirements.txt jupyterlab`, then "
            f"`jupyter lab {study.notebook}` from this folder.",
            "",
            "## Contents",
            "",
            *layout,
            "",
            "## Caveats",
            "",
            *caveats,
            "",
        ]
    )


_HELPER = '''\
"""Run this study's SPARQL queries against the OKN federation endpoint.

Generated by __GENERATED_BY__. Needs only pandas: the HTTP request uses the
standard library, so mcp-okn does not have to be installed.

    run_query("q01")               # cached rows from data/ (live if none are cached)
    run_query("q01", rerun=True)   # run it live and compare the row count
    verify_all()                   # every query, live vs logged row counts

The endpoint is shared and answers HTTP 429 when it is busy, so a request that
fails quickly with 429 (or a 502/503/504 gateway error) is retried after a short,
growing pause, as mcp-okn itself does. A 429 that arrives only after the whole
time limit means the query itself ran out of time, and is not retried.
"""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

ENDPOINT = "__ENDPOINT__"
HERE = Path(__file__).resolve().parent
QUERIES = HERE / "queries"

_NUMERIC = ("integer", "int", "long", "decimal", "double", "float")

#: Statuses that mean "busy, try again": QLever's overload 429 and the gateway's.
RETRY_STATUSES = (429, 502, 503, 504)
#: Pause before retry 1, 2, 3 … (seconds, before jitter); also the retry budget.
BACKOFF_SECONDS = (2.0, 5.0, 15.0, 30.0)
#: Longest Retry-After header honoured.
MAX_RETRY_AFTER = 60.0

#: Row counts of the queries run live in this session, for verify_all().
_live_counts: dict[str, int] = {}


class EndpointError(RuntimeError):
    """The endpoint refused or failed a query; the message carries its reason."""


def manifest() -> list[dict[str, Any]]:
    """Per query: name, description, graphs, timestamp, row_count, cache, sent."""
    return json.loads((QUERIES / "manifest.json").read_text(encoding="utf-8"))


def _entry(name: str) -> dict[str, Any]:
    for item in manifest():
        if item["name"] == name:
            return item
    raise KeyError(f"no query {name!r} in queries/manifest.json")


def query_text(name: str, sent: bool = True) -> str:
    """The query's text: the form the server sent (default), or as logged."""
    entry = _entry(name)
    path = HERE / entry["sent"] if sent and entry.get("sent") else QUERIES / f"{name}.rq"
    return path.read_text(encoding="utf-8")


def _value(cell: dict[str, Any]) -> Any:
    """A binding's value, numbers and booleans cast the way mcp-okn casts them."""
    value = cell.get("value")
    dtype = cell.get("datatype", "")
    if dtype.endswith(_NUMERIC):
        try:
            return float(value) if "." in value or "e" in value.lower() else int(value)
        except (TypeError, ValueError):
            return value
    if dtype.endswith("boolean"):
        return value == "true"
    return value


def _reason(error: urllib.error.HTTPError) -> str:
    """The endpoint's own explanation of a failed request (QLever's ``exception``)."""
    try:
        text = error.read().decode("utf-8", "replace")
    except Exception:  # the body is a courtesy; the status is enough
        return error.reason or ""
    try:
        return str(json.loads(text).get("exception") or text).strip()[:300]
    except (ValueError, AttributeError):
        return text.strip()[:300]


def _pause(error: urllib.error.HTTPError, attempt: int) -> float:
    """Seconds to wait before retry ``attempt``, honouring Retry-After."""
    try:
        return min(float(error.headers.get("Retry-After", "")), MAX_RETRY_AFTER)
    except (TypeError, ValueError):
        return BACKOFF_SECONDS[attempt - 1] * (1 + random.random() * 0.25)


def _post(query: str, timeout: int) -> dict[str, Any]:
    """POST ``query``, retrying while the endpoint is busy; the parsed JSON reply."""
    body = urllib.parse.urlencode({"query": query, "timeout": f"{timeout}s"}).encode()
    attempt = 0
    while True:
        request = urllib.request.Request(
            ENDPOINT,
            data=body,
            headers={
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "okn-study-notebook",
            },
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=timeout + 30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            attempt += 1
            reason = _reason(error)
            took = time.monotonic() - started
            if error.code == 429 and took >= 0.9 * timeout:
                raise EndpointError(
                    f"query stopped by the endpoint after {timeout}s ({reason}); "
                    "pass a larger timeout= to run_query/verify_all"
                ) from None
            if error.code not in RETRY_STATUSES or attempt > len(BACKOFF_SECONDS):
                tries = f" after {attempt} attempts" if attempt > 1 else ""
                raise EndpointError(
                    f"HTTP {error.code}{tries}: {reason or error.reason}"
                ) from None
            wait = _pause(error, attempt)
            print(f"endpoint busy (HTTP {error.code}); retrying in {wait:.0f}s")
            time.sleep(wait)


def run_sparql(query: str, timeout: int = 300) -> pd.DataFrame:
    """POST ``query`` to the federation and return the bindings as a DataFrame."""
    payload = _post(query, timeout)
    if isinstance(payload.get("boolean"), bool):
        return pd.DataFrame({"boolean": [payload["boolean"]]})
    columns = payload.get("head", {}).get("vars", [])
    rows = [
        {var: _value(cell) for var, cell in (binding or {}).items()}
        for binding in payload.get("results", {}).get("bindings", [])
    ]
    return pd.DataFrame(rows, columns=columns)


def load_cached(name: str) -> pd.DataFrame:
    """The rows the session logged for query ``name``."""
    entry = _entry(name)
    if not entry.get("cache"):
        raise FileNotFoundError(f"{name} has no cached rows; run it with rerun=True")
    sep = "\\t" if entry["cache"].endswith(".tsv") else ","
    return pd.read_csv(HERE / entry["cache"], sep=sep)


def run_query(name: str, rerun: bool = False, timeout: int = 300) -> pd.DataFrame:
    """Query ``name``'s rows: cached unless ``rerun`` (or nothing is cached).

    A live run prints a note when its row count differs from the logged one.
    """
    entry = _entry(name)
    if not rerun and entry.get("cache"):
        if entry.get("truncated"):
            print(
                f"{name}: cached {entry['cached_rows']:,} of {entry['row_count']:,} "
                "rows; rerun=True fetches all of them"
            )
        return load_cached(name)
    frame = run_sparql(query_text(name), timeout=timeout)
    _live_counts[name] = len(frame)
    logged = entry.get("row_count")
    if isinstance(logged, int) and len(frame) != logged:
        print(
            f"{name}: {len(frame):,} rows now vs {logged:,} logged; the graph may "
            "have been redeployed since the study ran"
        )
    return frame


def verify_all(timeout: int = 300, fresh: bool = False) -> pd.DataFrame:
    """Logged vs live row counts, one row per query.

    A query already run live in this session (``RERUN = True``) is not sent
    again unless ``fresh``; the others are run now, one at a time.
    """
    report = []
    for entry in manifest():
        name = entry["name"]
        try:
            if not fresh and name in _live_counts:
                live: Any = _live_counts[name]
            else:
                live = len(run_sparql(query_text(name), timeout=timeout))
                _live_counts[name] = live
            status = "ok" if live == entry["row_count"] else "drift"
        except Exception as exc:  # report and keep going
            live, status = None, f"error: {str(exc)[:160]}"
        report.append(
            {
                "query": entry["name"],
                "graphs": ", ".join(entry.get("graphs") or []),
                "logged_rows": entry["row_count"],
                "live_rows": live,
                "status": status,
            }
        )
    return pd.DataFrame(report).astype({"live_rows": "Int64"})
'''

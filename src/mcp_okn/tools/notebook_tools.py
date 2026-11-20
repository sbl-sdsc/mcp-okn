"""create_jupyter_notebook: a re-runnable study folder built from the query log."""

from __future__ import annotations

import os
import shutil
from datetime import date as _date
from pathlib import Path
from typing import Any

from .. import __version__, session, void
from ..app import mcp
from ..build_info import build_suffix
from ..notebook import build_study, run_commands
from ..skill_versions import check_skills
from ..sparql import FEDERATION_ENDPOINT
from .transcript import (
    _active_window,
    _chat_window,
    _clean_entries,
    _resolve_sources,
    _skills_warning,
)

#: Set by the stdio entry point (`mcp_okn.server.main`), where the server runs on
#: the user's own machine. A hosted (HTTP) server never writes a caller-chosen
#: path: a remote client could otherwise make it write anywhere on its disk.
_local_writes = False


def enable_local_writes() -> None:
    """Allow `output_dir` writes; called when the server runs over stdio."""
    global _local_writes
    _local_writes = True


def local_writes_enabled() -> bool:
    """True under stdio, or when ``MCP_OKN_LOCAL_WRITES=1`` opts a local HTTP run in."""
    return _local_writes or os.environ.get("MCP_OKN_LOCAL_WRITES", "") == "1"


def _select(
    log: list[dict[str, Any]], supporting: list[dict[str, Any] | int] | None
) -> tuple[list[dict[str, Any]], list[str]]:
    """The curated subset of the log named by `supporting`, in the order given."""
    if supporting is None:
        return list(log), []
    selected: list[dict[str, Any]] = []
    warnings: list[str] = []
    for item in supporting:
        if isinstance(item, dict):
            idx, desc = item.get("index"), item.get("description")
        else:
            idx, desc = item, None
        if (
            not isinstance(idx, int)
            or isinstance(idx, bool)
            or not 1 <= idx <= len(log)
        ):
            warnings.append(
                f"`supporting` index {idx!r} is out of range for a log of {len(log)} "
                "queries — skipped."
            )
            continue
        entry = dict(log[idx - 1])
        if desc:
            entry["description"] = desc
        selected.append(entry)
    return selected, warnings


def _write_folder(
    root: Path, files: dict[str, str], figures: list[dict[str, str]], overwrite: bool
) -> tuple[list[str], list[dict[str, str]]]:
    """Write the folder; copy each figure that names a readable `source`.

    Returns ``(warnings, figures still to copy)``.
    """
    if root.exists() and any(root.iterdir()) and not overwrite:
        raise FileExistsError(
            f"{root} exists and is not empty; pass overwrite=True or another output_dir"
        )
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    warnings: list[str] = []
    pending: list[dict[str, str]] = []
    for fig in figures:
        source = Path(fig["source"]).expanduser() if fig.get("source") else None
        if source is not None and source.is_file():
            dest = root / fig["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        else:
            if source is not None:
                warnings.append(
                    f"figure source {str(source)!r} not found — copy it in."
                )
            pending.append(fig)
    return warnings, pending


async def _kg_versions(
    kgs: list[dict[str, Any]], warnings: list[str]
) -> dict[str, str]:
    """``{shortname: release}`` for the study's KGs, from the VoID metadata.

    Read when the notebook is built, normally minutes after the queries ran. Fails
    open: without the metadata the header lists the KGs by name only.
    """
    if not kgs:
        return {}
    try:
        records = await void.fetch_versions()
    except Exception as exc:  # provenance is a courtesy; never block the notebook
        warnings.append(
            f"KG versions unavailable ({str(exc)[:120]}); the header lists the "
            "knowledge graphs by name only."
        )
        return {}
    wanted = {k["shortname"] for k in kgs}
    return {
        r["shortname"]: str(r["version"])
        for r in records
        if r["shortname"] in wanted and r.get("version")
    }


def _show_command(folder: str, notebook: str, saved_by_you: bool) -> dict[str, str]:
    """The run commands, and the instructions to render the HTML and show the first."""
    commands = run_commands(folder, notebook)
    html = notebook.removesuffix(".ipynb") + ".html"
    where = (
        f" Replace `{folder}` in these commands with the absolute path of the "
        "folder you saved."
        if saved_by_you
        else ""
    )
    return {
        "run_command": commands["jupyter"],
        "rerun_command": commands["nbconvert"],
        "html_command": commands["html"],
        # The server never executes the notebook itself: its cells hold
        # caller-written code, which belongs in the client's sandbox and under
        # the user's permission prompts, not in the server process.
        "show_user": (
            f"Add the executed notebook as HTML: if you can run shell commands, run "
            f"`html_command` now; it executes the notebook from the cached rows and "
            f"writes `{html}` beside it (one self-contained page). Tell the user it "
            "is there, or report the error if the command fails; if you have no "
            "shell, give the user `html_command` instead. Then show the user how to "
            "run the notebook: at the END of your reply, give `run_command` in a "
            "bash code block, as given, and say to choose Run → Run All Cells once "
            "JupyterLab opens. It needs only uv; the folder's requirements.txt "
            "supplies the rest." + where
        ),
    }


@mcp.tool()
async def create_jupyter_notebook(
    model: str,
    title: str = "OKN Study",
    folder_name: str | None = None,
    kgs_used: list[str] | None = None,
    supporting: list[dict[str, Any] | int] | None = None,
    code_files: dict[str, str] | None = None,
    cells: list[dict[str, Any]] | None = None,
    figures: list[dict[str, Any]] | None = None,
    requirements: list[str] | None = None,
    include_data: bool = True,
    prompt: str | None = None,
    notes: str | None = None,
    skills: list[str] | None = None,
    external_mcp_servers: list[str] | None = None,
    date: str | None = None,
    chat_started: str | None = None,
    chat_ended: str | None = None,
    scope: str | None = None,
    output_dir: str | None = None,
    overwrite: bool = False,
    max_inline_chars: int | None = 150_000,
) -> dict[str, Any]:
    """Build a re-runnable Jupyter study folder: notebook, queries, data, code.

    The session's reproducibility record. The queries and
    their results come from the session log (every non-exploratory, row-returning
    `sparql_query`), verbatim, so do not hand-write them. The parts only YOU have —
    your analysis code, the cells that use it, your figures — you pass in. Folder:

        <folder>/<folder>.ipynb   provenance header, a cell per query (cached
                                  results shown), then your `cells`
        okn_sparql.py             run_query("q01") / verify_all(); needs only pandas
        queries/qNN.rq            each query verbatim (+ sent/qNN.rq: the text the
                                  server POSTed, when its plan rewrites changed it)
        queries/manifest.json     graphs, timestamp, logged row count per query
        data/qNN.csv              the logged rows (up to 1,000 per query)
        <your code_files>         e.g. analysis.py, importable from the notebook
        requirements.txt, README.md
        okn_notebook.html.j2      template `html_command` renders with
        <folder>.html             the executed notebook, once you run
                                  `html_command` (see Returns)

    In the notebook, query k's rows are `data["qNN"]` (a pandas DataFrame, k
    zero-padded), loaded from `data/` unless `RERUN = True`.

    DELIVERY. On a hosted server the result's `files` maps each relative path to
    its content: save every entry VERBATIM under `<folder>/` (never retype or
    summarize one), then copy each `figures_to_copy` image to its `path`. When
    the server runs on your machine (stdio) and you pass `output_dir`, it writes
    the folder itself, copies figures that name a `source`, and returns only the
    manifest.

    Args:
        model: The EXACT runtime model id (e.g. `claude-opus-4-8`), as for
            `create_chat_transcript`. If you cannot determine it, ASK.
        title: Notebook title (H1); also the folder name unless `folder_name`.
        folder_name: Folder (and notebook) name. Used as given when it is letters,
            digits, `-` and `_` (e.g. `MS_notebook`); anything else is slugged.
        kgs_used: KG shortnames the study is about; inferred from the queries if
            omitted. Same guards as the transcript tools: a query touching none of
            them is dropped as foreign, a named KG no query touched is flagged.
        supporting: OPTIONAL curation of the log: 1-based indices into it (the
            order `get_query_log` shows), or
            `{"index": int, "description": str}` dicts (the description becomes the
            query's heading). None = every logged query, in order.
        code_files: Your generated text files, relative path → content (e.g.
            `{"analysis.py": "<source>"}`), written verbatim. Only reusable
            helpers that cells call by name like a library (statistics, data
            shaping, plot styling). The analysis steps and each figure's plotting
            code belong in `cells`, where the reader sees them, never in a script
            a cell merely runs or calls (`build_figures.py`, `fig3()`).
        cells: Analysis cells after the query cells, in order, each
            `{"type": "markdown" | "code", "source": str}`. Code cells can use
            `data["q01"]` … and your `code_files` modules; they are saved without
            outputs. Draw each figure in its OWN code cell, in report order,
            holding its plotting code and saving it to its `figures` path (and
            showing it), then follow it with a markdown cell holding the report's
            numbered legend verbatim (`**Figure N. Title.** …`). Never one cell
            that builds every figure plus another that shows them all.
        figures: Images the study produced, each `{"path": "figures/fig1.png",
            "caption": str, "source": str?}`; listed in the README and copied in.
            A "Figures" gallery of them is added only when `cells` has no code
            cell; with code cells, the cell that draws a figure shows it.
            `source` is the image's current location, used by a local write.
        requirements: Extra pip requirements your code needs (pandas is always
            listed; the run command adds JupyterLab), e.g. `["matplotlib>=3.7"]`.
        include_data: Cache each query's logged rows under `data/` (default True).
            False makes the notebook re-run every query live, and keeps the result
            small when the log holds large results.
        prompt: The originating user prompt, verbatim, for the header.
        notes: A short methodology note for the header.
        skills: Skills that shaped the study, each `"<name> v<version>"`; the
            server cannot see them, so pass them (a warning says when you don't).
        external_mcp_servers: Other MCP servers whose calls fed the analysis.
        date: ISO date for the header; defaults to today.
        chat_started: OPTIONAL ISO-8601 time the CHAT began (only you know it): the
            header then shows the whole-chat "Elapsed time" instead of the "Study
            active window" (first → last logged query).
        chat_ended: OPTIONAL ISO-8601 end for `chat_started`; defaults to now.
        scope: The log scope passed to `sparql_query`, when subagents share a session.
        output_dir: Absolute directory to write `<folder>/` into. Only honored
            when the server runs locally; a hosted server returns `files` instead.
        overwrite: Allow writing into an existing non-empty `<folder>/`.
        max_inline_chars: When the files total more than this, `files` is left out
            and the result says how to shrink it (`include_data=False`, or curate
            `supporting`). None = no limit.

    Returns:
        `{"folder", "notebook", "files" | "written_to", "manifest" (path, chars),
        "figures_to_copy", "instructions", "run_command", "rerun_command",
        "html_command", "show_user", "warnings"?}`. Follow `show_user`: run
        `html_command` to add `<folder>.html` (the executed notebook), then end
        your reply with `run_command` in a bash block.
    """
    when = date or _date.today().isoformat()
    skill_list = _clean_entries(skills)
    server_list = _clean_entries(external_mcp_servers)

    log = session.entries(scope)
    selected, warnings = _select(log, supporting)
    selected, kgs, guard_warnings = _resolve_sources(
        selected, [], kgs_used, check_phantom=True
    )
    warnings += guard_warnings
    kg_versions = await _kg_versions(kgs, warnings)
    if not skill_list:
        warnings.append(_skills_warning("notebook"))
    warnings += check_skills(skill_list)
    # Timing: the whole chat when the caller knows its start, else the active-query
    # window over the whole scoped log.
    window = _chat_window(chat_started, chat_ended) if chat_started else None
    window_label = "Elapsed time"
    if chat_started and window is None:
        warnings.append(
            f"chat_started={chat_started!r} (or chat_ended) is not a parseable ISO-8601 "
            "timestamp; fell back to the active-query window for the timing line."
        )
    if window is None:
        window, window_label = _active_window(log), "Study active window"

    study = build_study(
        title=title,
        when=when,
        model=model,
        entries=selected,
        kgs=kgs,
        endpoint=FEDERATION_ENDPOINT,
        generated_by=f"{mcp.name} v{__version__}{build_suffix()}",
        skills=skill_list,
        mcp_servers=server_list,
        prompt=prompt or "",
        notes=notes or "",
        folder_name=folder_name,
        code_files=code_files,
        cells=cells,
        figures=figures,
        requirements=requirements,
        include_data=include_data,
        window=window,
        window_label=window_label,
        kg_versions=kg_versions,
    )
    warnings += study.warnings
    manifest: list[dict[str, Any]] = [
        {"path": p, "chars": len(t)} for p, t in study.files.items()
    ]
    total = sum(m["chars"] for m in manifest)
    out: dict[str, Any] = {
        "folder": study.name,
        "notebook": f"{study.name}/{study.notebook}",
        "queries": len(selected),
        "manifest": manifest,
    }

    if output_dir:
        if not local_writes_enabled():
            warnings.append(
                "output_dir ignored: this server is hosted, so it cannot write to your "
                "machine. Save the returned `files` yourself."
            )
        elif not Path(output_dir).expanduser().is_absolute():
            warnings.append("output_dir must be an absolute path — nothing written.")
        else:
            root = Path(output_dir).expanduser() / study.name
            try:
                write_warnings, pending = _write_folder(
                    root, study.files, study.figures, overwrite
                )
            except (OSError, FileExistsError) as exc:
                warnings.append(f"could not write {root}: {exc}")
            else:
                warnings += write_warnings
                out["written_to"] = str(root)
                out["figures_to_copy"] = pending
                out.update(_show_command(str(root), study.notebook, saved_by_you=False))
                out["instructions"] = f"Wrote {len(study.files)} files to {root}. " + (
                    "Copy each `figures_to_copy` image to its path in the folder."
                    if pending
                    else "Nothing left to copy."
                )
                if warnings:
                    out["warnings"] = warnings
                return out

    out["figures_to_copy"] = study.figures
    if max_inline_chars is not None and total > max_inline_chars:
        biggest = sorted(manifest, key=lambda m: -m["chars"])[:5]
        out["instructions"] = (
            f"The folder is {total:,} characters, over max_inline_chars "
            f"({max_inline_chars:,}), so `files` was left out rather than risk a "
            "truncated copy. Largest files: "
            + ", ".join(f"{m['path']} ({m['chars']:,})" for m in biggest)
            + ". Call again with include_data=False (the notebook then re-runs the "
            "queries live), curate `supporting`, or raise max_inline_chars."
        )
    else:
        out["files"] = study.files
        out["instructions"] = (
            f"Save every entry of `files` VERBATIM under `{study.name}/` (paths are "
            "relative to it; create subfolders as needed). Do not retype or "
            "summarize any file. Then copy each `figures_to_copy` image to its path."
        )
    if "files" in out:
        out.update(_show_command(study.name, study.notebook, saved_by_you=True))
    if warnings:
        out["warnings"] = warnings
    return out

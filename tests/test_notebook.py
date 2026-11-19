"""create_jupyter_notebook: the study folder it builds, and that the notebook runs."""

from __future__ import annotations

import importlib
import io
import json
import os
import sys
from pathlib import Path

import pytest

from mcp_okn import session
from mcp_okn.notebook import build_study, folder_slug, safe_relative_path, slugify
from mcp_okn.sparql import prepare_query
from mcp_okn.tools import notebook_tools
from mcp_okn.tools.notebook_tools import create_jupyter_notebook

nbformat = pytest.importorskip("nbformat")
pd = pytest.importorskip("pandas")

G = "https://purl.org/okn/frink/kg"

Q_DISEASE = (
    "SELECT ?disease ?label WHERE { GRAPH <" + G + "/spoke-okn> "
    "{ ?disease <http://www.w3.org/2000/01/rdf-schema#label> ?label } } LIMIT 2"
)
Q_MINUS = (
    "SELECT ?g WHERE { GRAPH <" + G + "/prokn> { ?g a ?t "
    "FILTER NOT EXISTS { ?g <http://example.org/neg> ?x } } } LIMIT 1"
)
ROWS = {
    "vars": ["disease", "label"],
    "rows": [
        {"disease": "MONDO:0005240", "label": "kidney cancer"},
        {"disease": "MONDO:0005089", "label": "testicular <cancer>"},
    ],
    "row_count": 2,
}


@pytest.fixture(autouse=True)
def clean_log(monkeypatch):
    session.reset()
    monkeypatch.setattr(notebook_tools, "_local_writes", False)
    monkeypatch.delenv("MCP_OKN_LOCAL_WRITES", raising=False)
    yield
    session.reset()


def _log_two():
    session.record(Q_DISEASE, "json", result=ROWS)
    session.record(
        Q_MINUS, "json", result={"vars": ["g"], "rows": [{"g": "x"}], "row_count": 1}
    )


ANALYSIS = '''\
def count_labels(frame):
    """Number of distinct labels."""
    return frame["label"].nunique()
'''


async def _build(**kw):
    kw.setdefault("model", "claude-test-1")
    kw.setdefault("skills", ["okn-bioanalysis v0.1.0"])
    return await create_jupyter_notebook(**kw)


async def test_folder_layout_and_valid_notebook():
    _log_two()
    out = await _build(
        title="Kidney Cancer Study",
        supporting=[{"index": 1, "description": "disease labels"}, 2],
        code_files={"analysis.py": ANALYSIS},
        cells=[
            {"type": "markdown", "source": "Count the labels."},
            {
                "type": "code",
                "source": "from analysis import count_labels\n"
                'n = count_labels(data["q01"])',
            },
            {"type": "markdown", "source": "**Figure 1. Overlap.** Labels per KG."},
        ],
        figures=[
            {
                "path": "figures/fig1.png",
                "caption": "**Figure 1. Overlap.** Labels per KG.",
            }
        ],
        requirements=["matplotlib>=3.7", "pandas>=1.5"],
    )
    assert "warnings" not in out
    files = out["files"]
    assert out["folder"] == "kidney-cancer-study"
    assert next(iter(files)) == "kidney-cancer-study.ipynb"  # notebook listed first
    for path in (
        "okn_sparql.py",
        "requirements.txt",
        "README.md",
        "analysis.py",
        "queries/q01.rq",
        "queries/q02.rq",
        "queries/manifest.json",
        "data/q01.csv",
        "data/q02.csv",
    ):
        assert path in files, path

    # Queries are verbatim; only the rewritten one gets a sent/ form.
    assert files["queries/q01.rq"].strip() == Q_DISEASE
    assert "queries/sent/q01.rq" not in files
    assert "MINUS" in files["queries/sent/q02.rq"]

    manifest = json.loads(files["queries/manifest.json"])
    assert [m["name"] for m in manifest] == ["q01", "q02"]
    assert manifest[0]["graphs"] == ["spoke-okn"] and manifest[0]["row_count"] == 2
    assert manifest[0]["description"] == "disease labels"
    assert manifest[1]["sent"] == "queries/sent/q02.rq"

    nb = nbformat.reads(files["kidney-cancer-study.ipynb"], as_version=4)
    nbformat.validate(nb)
    text = "".join("".join(c.source) for c in nb.cells)
    assert "**Model:** claude-test-1" in text and "okn-bioanalysis v0.1.0" in text
    assert "### q01 — disease labels" in text
    # A code cell shows its own figures, so no static gallery repeats them.
    assert "## Figures" not in text and "![Overlap](figures/fig1.png)" not in text
    assert "`figures/fig1.png`" in files["README.md"]
    # Cached preview output is escaped HTML.
    q1 = next(c for c in nb.cells if 'run_query("q01"' in "".join(c.source))
    html = "".join(q1.outputs[0]["data"]["text/html"])
    assert "testicular &lt;cancer&gt;" in html

    reqs = files["requirements.txt"].splitlines()
    assert reqs.count("pandas>=1.5") == 1 and "matplotlib>=3.7" in reqs
    assert out["figures_to_copy"] == [{"path": "figures/fig1.png"}]


async def test_notebook_cells_execute_offline(tmp_path, monkeypatch):
    """Write the folder locally and run every code cell but the live verify."""
    _log_two()
    notebook_tools.enable_local_writes()
    out = await _build(
        title="Run Me",
        code_files={"analysis.py": ANALYSIS},
        cells=[
            {
                "type": "code",
                "source": 'from analysis import count_labels\nn = count_labels(data["q01"])',
            }
        ],
        output_dir=str(tmp_path),
    )
    root = Path(out["written_to"])
    assert "files" not in out and (root / "run-me.ipynb").is_file()

    nb = nbformat.read(root / "run-me.ipynb", as_version=4)
    monkeypatch.chdir(root)
    monkeypatch.syspath_prepend(str(root))
    sys.modules.pop("okn_sparql", None)
    sys.modules.pop("analysis", None)
    ns: dict = {}
    for cell in nb.cells:
        src = "".join(cell.source)
        if cell.cell_type == "code" and src.strip() != "verify_all()":
            exec(src, ns)  # the generated notebook under test
    assert list(ns["data"]) == ["q01", "q02"]
    assert ns["data"]["q01"]["label"].tolist() == [
        "kidney cancer",
        "testicular <cancer>",
    ]
    assert ns["n"] == 2

    # verify_all() re-runs live; stub the HTTP call and check it reports drift.
    helper = importlib.import_module("okn_sparql")
    monkeypatch.setattr(
        helper, "run_sparql", lambda q, timeout=300: pd.DataFrame({"x": [1]})
    )
    report = helper.verify_all()
    assert report["status"].tolist() == ["drift", "ok"]
    # The live run sends the server's rewritten form, not the verbatim text.
    assert "MINUS" in helper.query_text("q02") and "MINUS" not in helper.query_text(
        "q02", sent=False
    )
    sys.modules.pop("okn_sparql", None)
    sys.modules.pop("analysis", None)


async def test_hosted_server_ignores_output_dir(tmp_path):
    _log_two()
    out = await _build(output_dir=str(tmp_path))
    assert "files" in out and "written_to" not in out
    assert any("output_dir ignored" in w for w in out["warnings"])
    assert not any(tmp_path.iterdir())


async def test_env_opt_in_and_no_overwrite(tmp_path, monkeypatch):
    _log_two()
    monkeypatch.setenv("MCP_OKN_LOCAL_WRITES", "1")
    src = tmp_path / "plot.png"
    src.write_bytes(b"\x89PNG")
    first = await _build(
        title="S",
        output_dir=str(tmp_path / "out"),
        figures=[{"path": "figures/plot.png", "source": str(src)}],
    )
    root = Path(first["written_to"])
    assert (root / "figures" / "plot.png").read_bytes() == b"\x89PNG"
    assert first["figures_to_copy"] == []
    again = await _build(title="S", output_dir=str(tmp_path / "out"))
    assert "written_to" not in again
    assert any("not empty" in w for w in again["warnings"])


async def test_unsafe_and_reserved_paths_skipped():
    _log_two()
    out = await _build(
        code_files={
            "../escape.py": "x",
            "/abs.py": "x",
            "okn_sparql.py": "x",
            "queries/q01.rq": "x",
            "pkg/util.py": "ok",
        },
        cells=[{"type": "raw", "source": "x"}],
    )
    files = out["files"]
    assert files["pkg/util.py"] == "ok"
    assert files["queries/q01.rq"].strip() == Q_DISEASE
    assert "def run_query" in files["okn_sparql.py"]
    assert not any("escape" in p or p == "abs.py" for p in files)
    assert sum("skipped" in w for w in out["warnings"]) == 5


async def test_size_limit_withholds_files():
    _log_two()
    out = await _build(max_inline_chars=100)
    assert "files" not in out
    assert "include_data=False" in out["instructions"]
    lean = await _build(include_data=False)
    assert not any(p.startswith("data/") for p in lean["files"])
    manifest = json.loads(lean["files"]["queries/manifest.json"])
    assert all(m["cache"] is None for m in manifest)


async def test_provenance_guards_shared_with_record():
    _log_two()
    out = await _build(skills=None, kgs_used=["spoke-okn", "rdkg"])
    warnings = " ".join(out["warnings"])
    assert "Dropped 1 auto-logged" in warnings  # the prokn query is foreign
    assert "`rdkg`" in warnings  # phantom source
    assert "no `skills=` passed" in warnings
    assert out["queries"] == 1


def test_truncated_cache_is_flagged():
    entry = {
        "sparql": Q_DISEASE,
        "graphs": ["spoke-okn"],
        "row_count": 5000,
        "results": {**ROWS, "row_count": 5000, "truncated": True},
    }
    study = build_study(
        title="T",
        when="2026-11-18",
        model="m",
        entries=[entry],
        kgs=[],
        endpoint="https://example.org/sparql",
        generated_by="mcp-okn test",
    )
    m = json.loads(study.files["queries/manifest.json"])[0]
    assert m["truncated"] and m["cached_rows"] == 2 and m["row_count"] == 5000
    assert "first rows only" in study.files["README.md"]


def test_helpers():
    assert slugify("Kidney Cancer: Study #2") == "kidney-cancer-study-2"
    assert slugify("!!!") == "okn-study"
    assert folder_slug("MS_notebook", "ignored") == "MS_notebook"  # kept as given
    assert folder_slug("My notebook!", "ignored") == "my-notebook"
    assert folder_slug(None, "Kidney Study") == "kidney-study"
    assert safe_relative_path("figures/a.png") == "figures/a.png"
    for bad in ("../a", "/a", "a\\b", "", "a//b/../c"):
        assert safe_relative_path(bad) is None, bad


def test_prepare_query_matches_run_sparql_rewrites():
    sent = prepare_query(Q_MINUS)
    assert "MINUS" in sent and "NOT EXISTS" not in sent
    plain = "SELECT ?s WHERE { ?s ?p ?o } LIMIT 1"
    assert prepare_query(plain) == plain
    assert "http://schema.org/name" in prepare_query(
        "SELECT ?n WHERE { ?s <https://schema.org/name> ?n }"
    )


def test_server_registers_tool():
    from mcp_okn import server

    assert "create_jupyter_notebook" in server.__all__
    names = {t.name for t in server.mcp._tool_manager.list_tools()}
    assert "create_jupyter_notebook" in names
    assert os.environ.get("MCP_OKN_LOCAL_WRITES") is None


async def test_run_command_shown_to_user(tmp_path):
    _log_two()
    hosted = await _build(title="My Study")
    assert hosted["run_command"] == (
        "cd my-study\nuv run --with jupyterlab --with-requirements requirements.txt "
        "jupyter lab my-study.ipynb"
    )
    assert "OKN_RERUN=1" in hosted["rerun_command"]
    assert "--output my-study-rerun.ipynb" in hosted["rerun_command"]
    assert hosted["html_command"].endswith(
        "jupyter nbconvert --to html --execute --embed-images "
        "--output my-study.html my-study.ipynb"
    )
    assert "OKN_RERUN" not in hosted["html_command"]  # renders the cached rows
    assert "PYTHONDONTWRITEBYTECODE=1 uv run" in hosted["html_command"]
    assert "run `html_command`" in hosted["show_user"]
    assert hosted["html_command"].split("\n")[1] in hosted["files"]["README.md"]
    assert "END of your reply" in hosted["show_user"]
    assert "absolute path of the folder you saved" in hosted["show_user"]
    assert hosted["run_command"].split("\n")[1] in hosted["files"]["README.md"]

    notebook_tools.enable_local_writes()
    local = await _build(title="My Study", output_dir=str(tmp_path / "a b"))
    assert local["run_command"].startswith(f"cd '{tmp_path / 'a b' / 'my-study'}'\n")
    assert "absolute path" not in local["show_user"]

    # Withheld files: nothing saved yet, so no command to show.
    big = await _build(max_inline_chars=10)
    assert "run_command" not in big
    assert "html_command" not in big


def test_rerun_env_switch(monkeypatch):
    from mcp_okn.notebook import _SETUP_CODE

    ns: dict = {}
    monkeypatch.setitem(sys.modules, "okn_sparql", type(sys)("okn_sparql"))
    sys.modules["okn_sparql"].run_query = sys.modules["okn_sparql"].verify_all = None
    monkeypatch.setenv("OKN_RERUN", "1")
    exec(_SETUP_CODE, ns)
    assert ns["RERUN"] is True
    monkeypatch.delenv("OKN_RERUN")
    exec(_SETUP_CODE, ns)
    assert ns["RERUN"] is False


@pytest.fixture
def helper(tmp_path, monkeypatch):
    """The generated okn_sparql module, imported from a freshly written folder."""
    _log_two()
    notebook_tools.enable_local_writes()
    out = asyncio_run(_build(title="H", output_dir=str(tmp_path)))
    monkeypatch.syspath_prepend(out["written_to"])
    sys.modules.pop("okn_sparql", None)
    module = importlib.import_module("okn_sparql")
    monkeypatch.setattr(module.time, "sleep", lambda s: None)
    yield module
    sys.modules.pop("okn_sparql", None)


def asyncio_run(coro):
    import asyncio

    return asyncio.new_event_loop().run_until_complete(coro)


class _Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _ok(n):
    rows = [{"x": {"type": "literal", "value": str(i)}} for i in range(n)]
    payload = {"head": {"vars": ["x"]}, "results": {"bindings": rows}}
    return _Reply(json.dumps(payload).encode())


def _http_error(code, body=b""):
    import urllib.error

    return urllib.error.HTTPError("u", code, "Too Many Requests", {}, io.BytesIO(body))


def test_helper_retries_a_busy_429(helper, monkeypatch):
    replies = [_http_error(429), _http_error(503), _ok(2)]
    calls = []

    def fake(request, timeout):
        calls.append(1)
        reply = replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(helper.urllib.request, "urlopen", fake)
    frame = helper.run_query("q01", rerun=True)
    assert len(frame) == 2 and len(calls) == 3


def test_helper_does_not_retry_a_timeout_429(helper, monkeypatch):
    clock = iter([0.0, 400.0])
    monkeypatch.setattr(helper.time, "monotonic", lambda: next(clock))
    body = json.dumps({"exception": "Operation timed out"}).encode()

    def fake(request, timeout):
        raise _http_error(429, body)

    monkeypatch.setattr(helper.urllib.request, "urlopen", fake)
    with pytest.raises(helper.EndpointError, match=r"Operation timed out.*timeout="):
        helper.run_sparql("SELECT 1", timeout=300)


def test_helper_reports_the_endpoint_reason(helper, monkeypatch):
    body = json.dumps({"exception": "Invalid SPARQL: bad token"}).encode()

    def fake(request, timeout):
        raise _http_error(400, body)

    monkeypatch.setattr(helper.urllib.request, "urlopen", fake)
    with pytest.raises(helper.EndpointError, match="HTTP 400: Invalid SPARQL"):
        helper.run_sparql("SELECT 1")
    # Gives up after the backoff budget on a 429 that never clears.
    attempts = []

    def busy(request, timeout):
        attempts.append(1)
        raise _http_error(429)

    monkeypatch.setattr(helper.urllib.request, "urlopen", busy)
    with pytest.raises(helper.EndpointError, match="after 5 attempts"):
        helper.run_sparql("SELECT 1")
    assert len(attempts) == 1 + len(helper.BACKOFF_SECONDS)


def test_verify_all_reuses_live_runs(helper, monkeypatch):
    sent = []

    def fake(request, timeout):
        sent.append(1)
        return _ok(2 if len(sent) == 1 else 1)

    monkeypatch.setattr(helper.urllib.request, "urlopen", fake)
    helper.run_query("q01", rerun=True)  # live: 2 rows
    report = helper.verify_all()  # q01 reused, only q02 sent
    assert len(sent) == 2
    assert report["status"].tolist() == ["ok", "ok"]
    assert str(report["live_rows"].dtype) == "Int64"
    helper.verify_all(fresh=True)
    assert len(sent) == 4


async def test_header_timing_line():
    _log_two()
    out = await _build(title="Timed")
    header = "".join(json.loads(out["files"]["timed.ipynb"])["cells"][0]["source"])
    assert "- **Study active window:** " in header

    out = await _build(title="Timed", chat_started="2026-07-25T10:00:00Z")
    header = "".join(json.loads(out["files"]["timed.ipynb"])["cells"][0]["source"])
    assert "- **Elapsed time:** 2026-07-25" in header
    assert "Study active window" not in header

    out = await _build(title="Timed", chat_started="not a time")
    assert any("chat_started" in w for w in out["warnings"])


async def test_notebook_figures_gallery_only_without_code_cells():
    """Markdown-only cells can't render figures, so the static gallery shows them."""
    _log_two()
    out = await _build(
        title="Gallery Study",
        cells=[{"type": "markdown", "source": "Notes only."}],
        figures=[{"path": "figures/fig1.png", "caption": "Overlap"}],
    )
    nb = nbformat.reads(out["files"]["gallery-study.ipynb"], as_version=4)
    text = "".join("".join(c.source) for c in nb.cells)
    assert text.count("![Overlap](figures/fig1.png)") == 1 and "## Figures" in text


async def test_notebook_warns_when_caption_not_in_a_cell():
    """With code cells, each figure's legend belongs in a markdown cell after its code."""
    _log_two()
    out = await _build(
        title="Legend Study",
        cells=[{"type": "code", "source": "build_all_figures()"}],
        figures=[
            {"path": "figures/fig1.png", "caption": "**Figure 1. Overlap.** Labels."}
        ],
    )
    assert any("caption is in no markdown cell" in w for w in out.get("warnings", []))


async def test_sparql_folded_by_default():
    """The query section opens folded in JupyterLab; each query's text folds everywhere."""
    _log_two()
    out = await _build(title="Fold Study")
    nb = nbformat.reads(out["files"]["fold-study.ipynb"], as_version=4)
    head = next(
        c for c in nb.cells if "".join(c.source).startswith("## SPARQL queries")
    )
    assert head.metadata.get("jp-MarkdownHeadingCollapsed") is True
    q1 = next(c for c in nb.cells if "".join(c.source).startswith("### q01"))
    text = "".join(q1.source)
    assert "<details><summary>SPARQL (" in text and text.rstrip().endswith("</details>")
    assert '</summary>\n<pre><code class="language-sparql">' in text
    assert "</code></pre>\n</details>" in text and "&lt;https://purl.org" in text
    # One raw-HTML block: no blank line inside the fold (that would end it early).
    fold = text[text.index("<details>") :]
    assert "\n\n" not in fold.rstrip()


def test_sparql_fold_keeps_blank_query_lines_inside():
    from mcp_okn.notebook import _sparql_details

    fold = "\n".join(_sparql_details("SELECT ?s WHERE {\n\n  ?s a <x> .\n}"))
    assert "\n\n" not in fold and "\n<span></span>\n" in fold and "&lt;x&gt;" in fold

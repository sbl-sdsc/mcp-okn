"""The server's build identity.

`__version__` has been "0.1.0" across the whole history, so it cannot tell two
deployments apart — and the hosted server routinely lags the repo. The build id is
what lets a reproducibility record (and a confused caller) say WHICH code answered.
"""

import pytest

from mcp_okn import __version__, build_info
from mcp_okn.server import get_server_info
from mcp_okn.sparql import FEDERATION_ENDPOINT


@pytest.fixture(autouse=True)
def clear_build_cache():
    """build_id() is cached for the process; each test resolves it fresh."""
    build_info.build_id.cache_clear()
    yield
    build_info.build_id.cache_clear()


def test_env_var_wins(monkeypatch):
    """The deploy sets MCP_OKN_BUILD — the only path that works in a container with
    no git metadata, so it outranks every fallback."""
    monkeypatch.setenv("MCP_OKN_BUILD", "deadbee")
    monkeypatch.setattr(build_info, "_from_git", lambda: "ignored")
    assert build_info.build_id() == "deadbee"
    assert build_info.build_suffix() == " (build deadbee)"


def test_falls_back_to_git_in_a_checkout(monkeypatch):
    monkeypatch.delenv("MCP_OKN_BUILD", raising=False)
    monkeypatch.setattr(build_info, "_from_git", lambda: "abc1234")
    assert build_info.build_id() == "abc1234"


def test_unknown_when_nothing_identifies_the_build(monkeypatch):
    """Never guess: a tarball with no env var and no git says so, and the header
    then omits the parenthetical rather than printing "(build unknown)"."""
    monkeypatch.delenv("MCP_OKN_BUILD", raising=False)
    monkeypatch.setattr(build_info, "_from_git", lambda: "")
    assert build_info.build_id() == build_info.UNKNOWN
    assert build_info.build_suffix() == ""


def test_git_lookup_is_skipped_without_a_checkout(monkeypatch, tmp_path):
    """No `.git` beside the package -> no subprocess at all (deployed containers)."""
    monkeypatch.setattr(build_info, "__file__", str(tmp_path / "pkg" / "mod.py"))
    monkeypatch.setattr(
        build_info.subprocess,
        "run",
        lambda *a, **k: pytest.fail("git must not be invoked without a checkout"),
    )
    assert build_info._from_git() == ""


async def test_get_server_info_reports_the_running_build(monkeypatch):
    monkeypatch.setenv("MCP_OKN_BUILD", "cafe123")
    info = await get_server_info()
    assert info == {
        "service": "mcp-okn",
        "version": __version__,
        "build": "cafe123",
        "sparql_endpoint": FEDERATION_ENDPOINT,
    }

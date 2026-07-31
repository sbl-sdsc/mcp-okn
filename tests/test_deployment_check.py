import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_deployment", ROOT / "scripts" / "check_deployment.py"
)
assert _spec and _spec.loader
check = importlib.util.module_from_spec(_spec)
# Register before exec: @dataclass resolves its own module out of sys.modules.
sys.modules["check_deployment"] = check
_spec.loader.exec_module(check)

# The four tools the hosted server was missing in July 2026.
LAGGING = [
    "create_reproducibility_record",
    "get_server_info",
    "get_skipped_queries",
    "sparql_to_mermaid",
]
SERVED = ["list_kgs", "sparql_query", "get_schema"]


def _surface(tools, resources=("transcript://session/latest",), instructions="i", **kw):
    return check.Surface(
        tools=frozenset(tools),
        resources=frozenset(resources),
        instructions_sha=check._digest(instructions),
        tool_digests=kw.get("digests", {}),
    )


def test_no_deltas_when_identical():
    local = _surface(SERVED + LAGGING)
    deltas = check.diff_surface(_surface(SERVED + LAGGING), local)
    assert deltas["missing_tools"] == []
    assert deltas["extra_tools"] == []
    assert deltas["missing_resources"] == deltas["extra_resources"] == []
    assert deltas["instructions_match"]
    assert not check.has_drift(deltas, "match", {"mismatches": []})


def test_lagging_deployment_july_2026():
    # The incident: hosted served 19 tools against 23 registered in the repo.
    deltas = check.diff_surface(_surface(SERVED), _surface(SERVED + LAGGING))
    assert deltas["missing_tools"] == LAGGING
    assert deltas["extra_tools"] == []
    assert check.has_drift(deltas, "absent", {"mismatches": []})


def test_extra_hosted_tool_is_flagged():
    deltas = check.diff_surface(_surface([*SERVED, "future_tool"]), _surface(SERVED))
    assert deltas["extra_tools"] == ["future_tool"]
    assert check.has_drift(deltas, "match", {"mismatches": []})


def test_resource_drift_is_flagged():
    hosted = _surface(SERVED, resources=())
    deltas = check.diff_surface(hosted, _surface(SERVED))
    assert deltas["missing_resources"] == ["transcript://session/latest"]
    assert check.has_drift(deltas, "match", {"mismatches": []})


def test_changed_tool_digest_is_advisory_not_gating():
    hosted = _surface(SERVED, digests={"get_schema": "aaa"})
    local = _surface(SERVED, digests={"get_schema": "bbb"})
    deltas = check.diff_surface(hosted, local)
    assert deltas["changed_tools"] == ["get_schema"]
    # Description drift alone does not fail the check (--strict opts into that).
    assert not check.has_drift(deltas, "match", {"mismatches": []})


def test_missing_digest_on_either_side_is_not_a_change():
    hosted = _surface(SERVED, digests={})
    local = _surface(SERVED, digests={"get_schema": "bbb"})
    assert check.diff_surface(hosted, local)["changed_tools"] == []


def test_instructions_drift_is_reported():
    deltas = check.diff_surface(
        _surface(SERVED, instructions="old"), _surface(SERVED, instructions="new")
    )
    assert not deltas["instructions_match"]
    assert not check.has_drift(deltas, "match", {"mismatches": []})


def test_build_status_exact_and_prefix():
    assert check.build_status("f8e27c1", "f8e27c1") == "match"
    full = "f8e27c1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert check.build_status(full, "f8e27c1") == "match"
    assert check.build_status("f8e27c1", full) == "match"


def test_build_status_short_prefix_does_not_match():
    # A 4-char prefix is too weak to call a match; git's short form is 7.
    assert check.build_status("f8e2", "f8e27c1") == "drift"


def test_build_status_absent_unknown_and_drift():
    assert check.build_status(None, "f8e27c1") == "absent"
    assert check.build_status("unknown", "f8e27c1") == "unknown"
    assert check.build_status("", "f8e27c1") == "unknown"
    assert check.build_status("f8e27c1", "unknown") == "unknown"
    assert check.build_status("d0c2cc9", "f8e27c1") == "drift"


def test_build_drift_alone_gates():
    deltas = check.diff_surface(_surface(SERVED), _surface(SERVED))
    assert check.has_drift(deltas, "drift", {"mismatches": []})
    # ...but an unidentifiable build is a nudge, not a verdict.
    assert not check.has_drift(deltas, "unknown", {"mismatches": []})


def test_compare_data_flags_stale_bundled_tables():
    local = {"crosswalks": (162, "2026-07-12"), "kg_count": 42}
    hosted = check.Hosted(
        surface=_surface(SERVED), crosswalks=(161, "2026-07-12"), kg_count=42
    )
    assert check.compare_data(hosted, local)["mismatches"] == ["crosswalks"]


def test_compare_data_tolerates_unavailable_tools():
    # Pointed at an arbitrary MCP server: n/a, never a mismatch.
    local = {"crosswalks": (162, "2026-07-12"), "kg_count": 42}
    hosted = check.Hosted(surface=_surface(SERVED), crosswalks=None, kg_count=None)
    assert check.compare_data(hosted, local)["mismatches"] == []


async def test_local_surface_enumerates_the_registered_tools():
    # Structural, offline: catches a FastMCP upgrade breaking the enumeration path.
    surface = await check.local_surface()
    assert "get_server_info" in surface.tools
    assert len(surface.tools) > 20
    assert surface.instructions_sha
    assert surface.tool_digests.keys() == set(surface.tools)

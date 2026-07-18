import pytest

from mcp_okn import __version__, session
from mcp_okn.server import (
    _clean_description,
    _rows_to_table,
    create_chat_transcript,
    create_reproducibility_record,
    latest_transcript_resource,
)
from mcp_okn.sparql import FEDERATION_ENDPOINT
from mcp_okn.tools.transcript import _render_query


@pytest.fixture(autouse=True)
def clean_log():
    """Each test starts and ends with an empty session log."""
    session.reset()
    yield
    session.reset()


JSON_RESULT = {
    "vars": ["disease", "label"],
    "rows": [
        {"disease": "MONDO:0005240", "label": "kidney cancer"},
        {"disease": "MONDO:0005089", "label": "testicular cancer"},
    ],
    "row_count": 2,
}


def test_session_records_query_and_detects_graphs():
    logged = session.record(
        "SELECT * WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s ?p ?o } }",
        "json",
        result=JSON_RESULT,
    )
    assert logged is True
    [entry] = session.entries()
    assert entry["graphs"] == ["sawgraph"]
    assert entry["row_count"] == 2
    assert entry["results"]["rows"][0]["label"] == "kidney cancer"


def test_query_log_is_isolated_per_session(monkeypatch):
    """Concurrent MCP sessions must not see each other's queries/diagrams.

    Regression for the remote-server bug where the log was a single process
    global, so one chat's queries leaked into another chat's transcript.
    """

    class FakeSession:  # a distinct object per simulated connection
        pass

    session_a, session_b = FakeSession(), FakeSession()
    current = {"s": session_a}
    monkeypatch.setattr(session, "_current_session", lambda: current["s"])

    # Session A records a query and a diagram.
    current["s"] = session_a
    assert session.record(
        "SELECT * WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s ?p ?o } }",
        "json",
        result=JSON_RESULT,
    )
    session.record_visualization("sawgraph", "classDiagram\n  class A")
    session.set_last_transcript("transcript-A")

    # Session B sees a clean, independent log.
    current["s"] = session_b
    assert session.entries() == []
    assert session.visualizations() == []
    assert session.last_transcript() is None
    session.record(
        "SELECT * WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke> { ?s ?p ?o } }",
        "json",
        result=JSON_RESULT,
    )
    assert [e["graphs"] for e in session.entries()] == [["spoke"]]

    # Session A is unaffected by B's activity, and reset() only clears A.
    current["s"] = session_a
    assert [e["graphs"] for e in session.entries()] == [["sawgraph"]]
    assert session.last_transcript() == "transcript-A"
    assert session.reset() == 1
    assert session.entries() == []
    current["s"] = session_b
    assert [e["graphs"] for e in session.entries()] == [["spoke"]]


def _q(kg: str) -> str:
    return f"SELECT * WHERE {{ GRAPH <https://purl.org/okn/frink/kg/{kg}> {{ ?s ?p ?o }} }}"


def test_query_log_is_isolated_per_scope():
    """Concurrent analyses in ONE session must not see each other's queries.

    Regression for the real bug: parallel subagents all speak over their parent's
    single MCP client connection, so keying the log by `ServerSession` alone put
    every agent in one log — and `create_chat_transcript` then rendered whichever
    queries happened to be there. Each analysis names its own `scope` instead.
    """
    try:
        session.record(_q("sawgraph"), "json", result=JSON_RESULT, scope="agent-a")
        session.record_visualization(
            "sawgraph", "classDiagram\n  class A", scope="agent-a"
        )
        session.record(_q("prokn"), "json", result=JSON_RESULT, scope="agent-b")

        # Neither agent sees the other's work.
        assert [e["graphs"] for e in session.entries("agent-a")] == [["sawgraph"]]
        assert [e["graphs"] for e in session.entries("agent-b")] == [["prokn"]]
        assert [v["shortname"] for v in session.visualizations("agent-a")] == [
            "sawgraph"
        ]
        assert session.visualizations("agent-b") == []
        # ...and the unscoped default log stays empty: scoped work never bleeds into it.
        assert session.entries() == []

        # One agent resetting its own log must not wipe a sibling's mid-run.
        assert session.reset("agent-a") == 1
        assert session.entries("agent-a") == []
        assert [e["graphs"] for e in session.entries("agent-b")] == [["prokn"]]
    finally:
        session.reset("agent-a")
        session.reset("agent-b")


@pytest.mark.asyncio
async def test_transcript_renders_only_its_own_scope():
    """A scoped transcript carries that scope's queries and no one else's."""
    try:
        session.record(_q("sawgraph"), "json", result=JSON_RESULT, scope="agent-a")
        session.record(_q("prokn"), "json", result=JSON_RESULT, scope="agent-b")

        md = await create_chat_transcript(model="claude-opus-4-8", scope="agent-a")
        assert "kg/sawgraph" in md
        assert "kg/prokn" not in md  # the sibling agent's query must not appear
    finally:
        session.reset("agent-a")
        session.reset("agent-b")


@pytest.mark.asyncio
async def test_transcript_drops_foreign_queries_when_kgs_used_given():
    """Safety net: even with NO scope, a query touching none of `kgs_used` is
    dropped and reported — never silently shipped as if it were ours.

    This is what makes a forgotten `scope` a loud, recoverable mistake instead of
    a transcript that authoritatively presents another analysis's SPARQL.
    """
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)  # ours
    session.record(_q("prokn"), "json", result=JSON_RESULT)  # a sibling agent's

    md = await create_chat_transcript(model="claude-opus-4-8", kgs_used=["sawgraph"])
    assert "kg/sawgraph" in md
    assert "kg/prokn" not in md
    assert "mcp-okn WARNING" in md
    assert "prokn" in md.split("\n")[0]  # the warning names the foreign graph

    # The warning is an HTML comment, so a transcript saved verbatim to .md is
    # still a clean document.
    assert md.startswith("<!--")


@pytest.mark.asyncio
async def test_transcript_keeps_queries_that_touch_kgs_used():
    """The safety net must not eat legitimate queries (no false positives).

    Both listed KGs are actually queried, so neither the foreign-drop nor the
    phantom-source backstop fires.
    """
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record(_q("prokn"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8", kgs_used=["sawgraph", "prokn"]
    )
    assert "kg/sawgraph" in md
    assert "kg/prokn" in md
    assert "mcp-okn WARNING" not in md


@pytest.mark.asyncio
async def test_transcript_flags_phantom_source():
    """A KG named in `kgs_used` that no logged query touched is a phantom source —
    warned about, never silently presented as if it contributed."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)  # the only query
    md = await create_chat_transcript(
        model="claude-opus-4-8", kgs_used=["sawgraph", "ubergraph"]
    )
    # the real query is kept...
    assert "kg/sawgraph" in md
    # ...but the un-queried KG is flagged as phantom in the warning comment
    assert "mcp-okn WARNING" in md
    assert "ubergraph" in md.split("\n")[0]
    assert "sawgraph" not in md.split("\n")[0]  # the queried KG is not flagged
    assert md.startswith("<!--")


@pytest.mark.asyncio
async def test_visualized_kg_is_not_a_phantom_source():
    """A KG with a schema visualization (but no query) still counts as touched —
    it is legitimately in the transcript, so it must not be flagged."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record_visualization("spoke-genelab", "classDiagram\n  class Gene")
    md = await create_chat_transcript(
        model="claude-opus-4-8", kgs_used=["sawgraph", "spoke-genelab"]
    )
    assert "mcp-okn WARNING" not in md


@pytest.mark.asyncio
async def test_phantom_check_skipped_when_query_log_excluded():
    """With the query log suppressed there is nothing to check against, so the
    phantom backstop must not fire (avoids false positives)."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        kgs_used=["sawgraph", "ubergraph"],
        include_query_log=False,
    )
    assert "mcp-okn WARNING" not in md


@pytest.mark.asyncio
async def test_large_transcript_returns_stub_pointing_at_resource():
    """When the rendered body exceeds max_inline_chars, return a compact stub —
    not the full body — so the harness can't spill it into a fabricated substitute.
    The complete transcript is still published verbatim to the resource."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[
            {
                "prompt": "Which diseases relate to PFAS?",
                "answer": "Two cancers are associated.",
            }
        ],
        max_inline_chars=50,  # tiny threshold -> force the stub
    )
    # a compact stub, not the full document
    assert "transcript://session/latest" in md
    assert "characters" in md  # the size line
    assert "## Conversation" not in md
    assert "Two cancers are associated." not in md
    # ...but the resource holds the complete transcript verbatim
    full = session.last_transcript()
    assert "## Conversation" in full
    assert "Two cancers are associated." in full
    assert "GRAPH <https://purl.org/okn/frink/kg/sawgraph>" in full


@pytest.mark.asyncio
async def test_small_transcript_stays_inline():
    """A normal-sized transcript (under the default threshold) is returned in full."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8", exchanges=[{"prompt": "q", "answer": "a"}]
    )
    assert "## Conversation" in md
    assert "delivered via resource" not in md  # not the stub


@pytest.mark.asyncio
async def test_max_inline_chars_none_forces_full_body():
    """max_inline_chars=None disables stubbing — the same input that stubs at a
    tiny threshold is returned in full."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[{"prompt": "q", "answer": "a"}],
        max_inline_chars=None,
    )
    assert "## Conversation" in md
    assert "delivered via resource" not in md


@pytest.mark.asyncio
async def test_stub_still_carries_warnings():
    """A stubbed result must still surface warnings (e.g. a phantom source)."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[{"prompt": "q", "answer": "a"}],
        kgs_used=["sawgraph", "ubergraph"],  # ubergraph un-queried -> phantom warning
        max_inline_chars=50,  # -> stub
    )
    assert md.startswith("<!--")  # warning comment leads
    assert "mcp-okn WARNING" in md
    assert "ubergraph" in md.split("\n")[0]
    assert "transcript://session/latest" in md  # stub body follows


@pytest.mark.asyncio
async def test_manifest_bullet_matches_rendered_counts():
    """The header Contents bullet must match the document's actual ```sparql /
    ```mermaid block counts — it's the invariant a reader checks against."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record(_q("prokn"), "json", result=JSON_RESULT)  # two distinct queries
    session.record_visualization("spoke-genelab", "classDiagram\n  class Gene")
    md = await create_chat_transcript(
        model="claude-opus-4-8", exchanges=[{"prompt": "q", "answer": "a"}]
    )
    # ground-truth fence counts
    assert md.count("```sparql") == 2
    assert md.count("```mermaid") == 3  # 2 query diagrams + 1 schema diagram
    # the manifest reports exactly those, with correct plurals
    assert "- **Contents:** 2 queries · 2 query diagrams · 1 schema diagram" in md


def _contents_line(md: str) -> str:
    return next(ln for ln in md.splitlines() if ln.startswith("- **Contents:**"))


@pytest.mark.asyncio
async def test_manifest_singular_forms_and_suppresses_zero_schema():
    """One query, one diagram, no schema visualizations — singular wording, and the
    zero schema-diagram component is omitted (not shown as '· 0 schema diagrams')."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8", exchanges=[{"prompt": "q", "answer": "a"}]
    )
    assert md.count("```sparql") == 1
    assert md.count("```mermaid") == 1
    assert _contents_line(md) == "- **Contents:** 1 query · 1 query diagram"
    assert "schema diagram" not in md  # zero component suppressed


@pytest.mark.asyncio
async def test_manifest_suppresses_zero_query_diagrams_when_disabled():
    """With query diagrams disabled, only the query count remains — no zeros."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[{"prompt": "q", "answer": "a"}],
        include_query_diagrams=False,
    )
    assert md.count("```mermaid") == 0
    assert _contents_line(md) == "- **Contents:** 1 query"


@pytest.mark.asyncio
async def test_manifest_all_zero_fallback():
    """A prose-only transcript with nothing to count gets a readable fallback."""
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[{"prompt": "q", "answer": "a"}],
        include_query_log=False,
    )
    assert _contents_line(md) == "- **Contents:** no queries or diagrams"


def test_session_skips_errored_queries():
    assert session.record("BAD QUERY", "json", error="boom") is False
    assert session.entries() == []


def test_session_skips_empty_json_results():
    empty = {"vars": ["x"], "rows": [], "row_count": 0}
    assert session.record("SELECT ?x {}", "json", result=empty) is False
    assert session.entries() == []


def test_session_skips_header_only_csv():
    header_only = {"format": "csv", "text": "x\n"}
    assert session.record("SELECT ?x {}", "csv", result=header_only) is False
    csv_with_rows = {"format": "csv", "text": "x\n1\n2\n"}
    assert session.record("SELECT ?x {}", "csv", result=csv_with_rows) is True
    [entry] = session.entries()
    assert entry["row_count"] == 2


async def test_transcript_renders_logged_queries_as_ground_truth():
    query = (
        "SELECT ?disease ?label WHERE {\n"
        "  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?x :linkedTo ?disease }\n"
        "}"
    )
    session.record(query, "json", result=JSON_RESULT)

    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[
            {
                "prompt": "Which diseases relate to PFAS?",
                "answer": "Two cancers are associated.",
            }
        ],
        date="2026-05-31",
    )
    # provenance
    assert "**Date:** 2026-05-31" in md
    assert FEDERATION_ENDPOINT in md
    assert f"**Generated by:** mcp-okn v{__version__}" in md
    # KGs inferred from the log, not supplied by the caller
    assert "`sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>" in md
    # conversation — mcp-proto-okn style (👤 User / 🧠 Assistant)
    assert "👤 **User**" in md
    assert "Which diseases relate to PFAS?" in md
    assert "🧠 **Assistant**" in md
    assert "Two cancers are associated." in md
    # ground-truth query section with the verbatim query and a results table
    assert "## SPARQL queries executed" in md
    assert "GRAPH <https://purl.org/okn/frink/kg/sawgraph>" in md
    assert "| disease | label |" in md
    assert "| MONDO:0005240 | kidney cancer |" in md


async def test_answer_text_rendered_verbatim_and_in_full():
    """A turn's answer is reproduced byte-for-byte — the renderer never
    truncates, summarizes, or escapes the model-supplied report prose. This is
    the contract the docstring leans on when it tells the model to paste its
    COMPLETE response (not a recap) into `answer`."""
    answer = (
        "## PFAS-associated cancers\n"
        "\n"
        "I queried `sawgraph` and found **two** cancers linked to PFAS exposure.\n"
        "\n"
        "| Disease | MONDO ID |\n"
        "| --- | --- |\n"
        "| kidney cancer | MONDO:0005240 |\n"
        "| testicular cancer | MONDO:0005089 |\n"
        "\n"
        "Notes:\n"
        "- Kidney cancer had the strongest signal (p < 0.01 & odds-ratio > 2).\n"
        "- Pipes in data such as a|b are preserved as-is in prose.\n"
        "- This paragraph runs long on purpose to prove nothing is clipped: "
        + "detail " * 40
        + "end."
    )
    md = await create_chat_transcript(
        model="claude-opus-4-8",
        exchanges=[{"prompt": "Which diseases relate to PFAS?", "answer": answer}],
    )
    # The entire answer appears as one contiguous, unmodified block — not a
    # paraphrase, and with no per-character escaping of its markdown.
    assert answer in md


async def test_sparql_query_does_not_log_exploratory(monkeypatch):
    import mcp_okn.server as srv
    from mcp_okn.tools import query as query_mod

    async def fake_run(query, fmt="json", **kw):
        return {"vars": ["x"], "rows": [{"x": 1}], "row_count": 1}

    monkeypatch.setattr(query_mod, "run_sparql", fake_run)
    await srv.sparql_query("SELECT ?x {}", exploratory=True)
    assert session.entries() == []
    await srv.sparql_query("SELECT ?x {}")
    assert len(session.entries()) == 1


async def test_sparql_query_does_not_log_empty_result(monkeypatch):
    import mcp_okn.server as srv
    from mcp_okn.tools import query as query_mod

    async def fake_run(query, fmt="json", **kw):
        return {"vars": ["x"], "rows": [], "row_count": 0}

    monkeypatch.setattr(query_mod, "run_sparql", fake_run)
    await srv.sparql_query("SELECT ?x {}")
    assert session.entries() == []


async def test_sparql_query_hints_on_empty_result(monkeypatch):
    import mcp_okn.server as srv
    from mcp_okn.tools import query as query_mod

    async def empty(query, fmt="json", **kw):
        return {"vars": ["x"], "rows": [], "row_count": 0}

    async def nonempty(query, fmt="json", **kw):
        return {"vars": ["x"], "rows": [{"x": 1}], "row_count": 1}

    monkeypatch.setattr(query_mod, "run_sparql", empty)
    out = await srv.sparql_query("SELECT ?x {}")
    assert "hint" in out
    assert "probe_namespaces" in out["hint"] and "find_crosswalks" in out["hint"]

    # Non-empty results carry no hint.
    monkeypatch.setattr(query_mod, "run_sparql", nonempty)
    out = await srv.sparql_query("SELECT ?x {}")
    assert "hint" not in out


async def test_include_query_log_false_omits_section():
    session.record(
        "SELECT * WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> {} }",
        "json",
        result={"vars": [], "rows": [], "row_count": 0},
    )
    md = await create_chat_transcript(
        model="m",
        exchanges=[{"prompt": "hi", "answer": "hello"}],
        include_query_log=False,
    )
    assert "## SPARQL queries executed" not in md
    assert "👤 **User**" in md and "hi" in md


async def test_explicit_kgs_override_inference():
    session.record(
        "SELECT * WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> {} }",
        "json",
        result={"vars": [], "rows": [], "row_count": 0},
    )
    md = await create_chat_transcript(model="m", kgs_used=["prokn"])
    assert "`prokn` —" in md
    assert "`sawgraph` —" not in md


async def test_inline_queries_on_a_turn_still_render():
    md = await create_chat_transcript(
        model="m",
        exchanges=[
            {
                "prompt": "q",
                "queries": [
                    {
                        "sparql": "SELECT * {}",
                        "description": "inline",
                        "results": {"format": "csv", "text": "a,b\n1,2"},
                    }
                ],
            }
        ],
    )
    assert "#### Query 1 — inline" in md
    assert "```csv\na,b\n1,2\n```" in md


async def test_inline_exploratory_queries_are_dropped():
    md = await create_chat_transcript(
        model="m",
        exchanges=[
            {
                "prompt": "q",
                "queries": [
                    {
                        "sparql": "SELECT * { ?s a ?t }",
                        "description": "Explore NDE schema",
                        "exploratory": True,
                    },
                    {
                        "sparql": "SELECT * {}",
                        "description": "real finding",
                        "results": {"format": "csv", "text": "a\n1"},
                    },
                ],
            }
        ],
    )
    assert "Explore NDE schema" not in md
    # The findings query still renders, renumbered as Query 1.
    assert "#### Query 1 — real finding" in md


def test_clean_description_strips_buried_bookkeeping():
    cases = {
        "Explore NDE schema (exploratory, not logged)": "Explore NDE schema",
        "Diseases in NDE (intermediate)": "Diseases in NDE",
        "Schema probe — exploratory, not logged": "Schema probe",
        "Find PFAS sites (not logged)": "Find PFAS sites",
        # Legitimate parentheticals are left intact.
        "Diseases (PFAS-linked)": "Diseases (PFAS-linked)",
        "Plain label": "Plain label",
    }
    for raw, expected in cases.items():
        assert _clean_description(raw) == expected


async def test_buried_exploratory_text_stripped_in_render():
    md = await create_chat_transcript(
        model="m",
        exchanges=[
            {
                "prompt": "q",
                "queries": [
                    {
                        "sparql": "SELECT * {}",
                        "description": "Explore NDE schema (exploratory, not logged)",
                        "results": {"format": "csv", "text": "a\n1"},
                    }
                ],
            }
        ],
    )
    assert "exploratory" not in md.lower()
    assert "#### Query 1 — Explore NDE schema" in md


async def test_intermediate_single_row_query_is_shown_in_full():
    # A one-row intermediate result costs almost no space, so show it rather
    # than omitting it.
    intermediate = {
        "vars": ["x"],
        "rows": [{"x": "step-1-value"}],
        "row_count": 1,
    }
    session.record(
        "SELECT ?x WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?o } }",
        "json",
        result=intermediate,
    )
    session.record(
        "SELECT ?disease ?label WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?x :linkedTo ?disease } }",
        "json",
        result=JSON_RESULT,
    )

    md = await create_chat_transcript(model="m")
    # Intermediate (first) query: single row rendered, no omission note.
    assert "results omitted" not in md
    assert "_1 row(s)_" in md
    assert "step-1-value" in md
    # Final query: full result table rendered.
    assert "| disease | label |" in md
    assert "| MONDO:0005240 | kidney cancer |" in md


async def test_intermediate_multi_row_query_previews_first_three():
    # A larger intermediate result is capped to its first 3 rows.
    intermediate = {
        "vars": ["x"],
        "rows": [{"x": f"row-{i}"} for i in range(5)],
        "row_count": 5,
    }
    session.record(
        "SELECT ?x WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?o } }",
        "json",
        result=intermediate,
    )
    session.record(
        "SELECT ?disease ?label WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?x :linkedTo ?disease } }",
        "json",
        result=JSON_RESULT,
    )

    md = await create_chat_transcript(model="m")
    # First three rows shown, the rest withheld, with a "showing first 3" note.
    assert "_5 row(s) — showing first 3_" in md
    assert "row-0" in md and "row-2" in md
    assert "row-3" not in md and "row-4" not in md


async def test_include_intermediate_rows_true_renders_all():
    intermediate = {
        "vars": ["x"],
        "rows": [{"x": "step-1-value"}],
        "row_count": 1,
    }
    session.record(
        "SELECT ?x WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?o } }",
        "json",
        result=intermediate,
    )
    session.record(
        "SELECT ?disease ?label WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?x :linkedTo ?disease } }",
        "json",
        result=JSON_RESULT,
    )

    md = await create_chat_transcript(model="m", include_intermediate_rows=True)
    assert "results omitted" not in md
    assert "step-1-value" in md
    assert "| MONDO:0005240 | kidney cancer |" in md


async def test_date_defaults_to_today():
    from datetime import date

    md = await create_chat_transcript(model="m")
    assert f"**Date:** {date.today().isoformat()}" in md


async def test_no_queries_renders_placeholder():
    md = await create_chat_transcript(model="m")
    assert "_None queried._" in md
    assert "_No prompts recorded._" in md


async def test_json_format_includes_log():
    session.record(
        "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s ?p ?o } }",
        "json",
        result={"vars": ["s"], "rows": [{"s": "urn:x"}], "row_count": 1},
    )
    out = await create_chat_transcript(
        model="claude-opus-4-8", date="2026-05-31", format="json"
    )
    assert out["model"] == "claude-opus-4-8"
    assert out["sparql_endpoint"] == FEDERATION_ENDPOINT
    assert len(out["query_log"]) == 1
    assert out["knowledge_graphs"] == [
        {"shortname": "prokn", "named_graph": "https://purl.org/okn/frink/kg/prokn"}
    ]
    assert out["generated_by"] == {"service": "mcp-okn", "version": __version__}


async def test_unsupported_format_returns_error():
    out = await create_chat_transcript(model="m", format="pdf")
    assert "error" in out


def test_rows_to_table_escapes_pipes():
    table = _rows_to_table(["c"], [{"c": "a|b"}])
    assert "| a\\|b |" in table


def test_session_records_and_dedupes_visualizations():
    session.record_visualization("dreamkg", "classDiagram\n  class A")
    session.record_visualization("spoke-genelab", "classDiagram\n  class B")
    # Re-visualizing the same KG replaces its diagram, keeping position + count.
    session.record_visualization("dreamkg", "classDiagram\n  class A2")
    viz = session.visualizations()
    assert [v["shortname"] for v in viz] == ["dreamkg", "spoke-genelab"]
    assert viz[0]["mermaid"].endswith("class A2")
    assert (
        session.record_visualization("x", "") is None
        and len(session.visualizations()) == 2
    )


async def test_transcript_renders_logged_visualization():
    session.record_visualization("spoke-genelab", "classDiagram\n  class Gene")
    md = await create_chat_transcript(model="m")
    assert "## Schema visualizations" in md
    assert "### `spoke-genelab` schema" in md
    assert "```mermaid" in md
    assert "classDiagram" in md
    # The diagram's KG is inferred into the knowledge-graphs section.
    assert "`spoke-genelab`" in md


async def test_visualization_kg_inference_and_json():
    session.record_visualization("dreamkg", "classDiagram\n  class Place")
    out = await create_chat_transcript(model="m", format="json")
    assert len(out["visualizations"]) == 1
    assert out["visualizations"][0]["shortname"] == "dreamkg"
    assert out["knowledge_graphs"] == [
        {"shortname": "dreamkg", "named_graph": "https://purl.org/okn/frink/kg/dreamkg"}
    ]


async def test_include_visualizations_false_omits_section():
    session.record_visualization("dreamkg", "classDiagram\n  class Place")
    md = await create_chat_transcript(model="m", include_visualizations=False)
    assert "## Schema visualizations" not in md


async def test_visualize_schema_returns_fenced_block_and_logs_raw(monkeypatch):
    import mcp_okn.server as srv

    async def fake_viz(shortname):
        return {"shortname": shortname, "mermaid": "classDiagram\n  class Gene"}

    monkeypatch.setattr(srv.schema, "visualize_schema", fake_viz)
    out = await srv.visualize_schema("demo")
    # Pre-fenced block for verbatim presentation; raw mermaid kept fence-free.
    assert out["mermaid_block"] == "```mermaid\nclassDiagram\n  class Gene\n```"
    assert not out["mermaid"].startswith("```")
    # The session logs the RAW diagram, so the transcript fences it exactly once.
    [viz] = session.visualizations()
    assert viz["mermaid"] == "classDiagram\n  class Gene"
    md = await create_chat_transcript(model="m")
    assert md.count("```mermaid") == 1


async def test_transcript_resource_publishes_last_markdown():
    # Before generating anything, the resource is a placeholder.
    assert "No transcript yet" in latest_transcript_resource()
    # After generating a markdown transcript, the resource serves it verbatim.
    md = await create_chat_transcript(
        model="m", exchanges=[{"prompt": "hi", "answer": "hello"}]
    )
    assert latest_transcript_resource() == md
    assert "👤 **User**" in latest_transcript_resource()
    # reset() clears it back to the placeholder.
    session.reset()
    assert "No transcript yet" in latest_transcript_resource()


async def test_json_transcript_does_not_publish_resource():
    # Only the markdown rendering is published to the resource.
    await create_chat_transcript(model="m", format="json")
    assert "No transcript yet" in latest_transcript_resource()


async def test_inline_mermaid_on_a_turn_renders():
    md = await create_chat_transcript(
        model="m",
        exchanges=[{"prompt": "show schema", "mermaid": "classDiagram\n  class Foo"}],
    )
    assert "```mermaid" in md
    assert "class Foo" in md


async def test_final_json_query_capped_to_max_result_rows():
    # The final logged query no longer dumps a huge table: it caps at
    # max_result_rows (default 5), preserving the true count.
    big = {
        "vars": ["d"],
        "rows": [{"d": f"row-{i}"} for i in range(20)],
        "row_count": 20,
    }
    session.record(
        "SELECT ?d WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d ?p ?o } }",
        "json",
        result=big,
    )
    md = await create_chat_transcript(model="m")
    assert "_20 row(s) — showing first 5_" in md
    assert "row-4" in md and "row-5" not in md


async def test_max_result_rows_none_renders_all():
    big = {
        "vars": ["d"],
        "rows": [{"d": f"row-{i}"} for i in range(20)],
        "row_count": 20,
    }
    session.record(
        "SELECT ?d WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d ?p ?o } }",
        "json",
        result=big,
    )
    md = await create_chat_transcript(model="m", max_result_rows=None)
    assert "_20 row(s)_" in md
    assert "row-19" in md and "showing first" not in md


async def test_csv_result_respects_row_cap():
    # The bug behind the reported transcript: a csv result previously dumped every
    # row, bypassing the cap. A many-row final csv now caps at max_result_rows...
    csv_rows = "acc\n" + "\n".join(f"P{i:05d}" for i in range(30))
    session.record(
        "SELECT ?acc WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?p ?x ?acc } }",
        "csv",
        result={"format": "csv", "text": csv_rows},
    )
    md = await create_chat_transcript(model="m")
    assert "_30 row(s) — showing first 5_" in md
    assert "P00004" in md and "P00005" not in md
    assert "```csv" in md


async def test_intermediate_csv_query_previews_first_three():
    # An intermediate csv query is now held to the 3-row preview (previously the
    # csv shape ignored the preview cap and dumped everything).
    inter = {
        "format": "csv",
        "text": "acc\n" + "\n".join(f"Q{i:05d}" for i in range(40)),
    }
    session.record(
        "SELECT ?acc WHERE { GRAPH <https://purl.org/okn/frink/kg/prokn> { ?a ?b ?acc } }",
        "csv",
        result=inter,
    )
    session.record(
        "SELECT ?disease ?label WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?x :linkedTo ?disease } }",
        "json",
        result=JSON_RESULT,
    )
    md = await create_chat_transcript(model="m")
    assert "_40 row(s) — showing first 3_" in md
    assert "Q00002" in md and "Q00003" not in md


_DIAGRAM_QUERY = (
    "PREFIX ex: <http://example.org/>\n"
    "SELECT ?disease ?label WHERE { "
    "GRAPH <https://purl.org/okn/frink/kg/sawgraph> { "
    "?x ex:linkedTo ?disease OPTIONAL { ?disease ex:label ?label } } }"
)


async def test_query_diagram_rendered_by_default():
    """Each query gets a Mermaid diagram right after its sparql block."""
    session.record(_DIAGRAM_QUERY, "json", result=JSON_RESULT)
    md = await create_chat_transcript(model="m")
    assert "```mermaid" in md
    assert "graph TD" in md
    assert "subgraph optional" in md  # the OPTIONAL block is drawn
    # the diagram follows the query text
    assert md.index("```sparql") < md.index("```mermaid")


async def test_query_diagram_can_be_disabled():
    session.record(_DIAGRAM_QUERY, "json", result=JSON_RESULT)
    md = await create_chat_transcript(model="m", include_query_diagrams=False)
    assert "```sparql" in md
    assert "```mermaid" not in md


@pytest.mark.asyncio
async def test_diagrams_off_reminds_to_readd():
    """Turning per-query diagrams OFF (right for keeping a large record from spilling) is only HALF
    the flow — the tool nudges the caller to re-add them, as a caller-facing comment kept OUT of the
    stored artifact. Fires only when diagrams are off, so a normal (diagrams-on) call never nags."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    off = await create_reproducibility_record(model="m", include_query_diagrams=False)
    assert "include_query_diagrams=False" in off and "expand_query_diagrams" in off
    assert off.startswith("<!--")  # a caller-facing comment, not body prose
    # ...but the reminder is NOT baked into the canonical stored transcript
    assert "OMITTED" not in (session.last_transcript() or "")

    session.reset()
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    on = await create_reproducibility_record(model="m")  # diagrams on by default
    assert "OMITTED" not in on  # no spurious nag


async def test_unparseable_query_skips_diagram_but_keeps_text():
    """A query that can't be parsed still renders its text; the diagram is skipped."""
    md = await create_chat_transcript(
        model="m",
        exchanges=[
            {
                "prompt": "p",
                "answer": "a",
                "queries": [{"sparql": "this is not valid sparql"}],
            }
        ],
    )
    assert "this is not valid sparql" in md
    assert "```mermaid" not in md


# --- create_reproducibility_record (the lean record) --------------------------


@pytest.mark.asyncio
async def test_record_fits_inline_with_counts_not_tables():
    """The lean record returns an inline string with row COUNTS, not result tables
    or conversation prose."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record(_q("prokn"), "json", result=JSON_RESULT)
    md = await create_reproducibility_record(model="claude-opus-4-8")
    assert isinstance(md, str)
    assert "# Proto-OKN Reproducibility Record" in md
    assert "## SPARQL queries" in md
    assert "## Conversation" not in md
    # row counts kept, full result table + its cell values dropped
    assert "_2 row(s)_" in md
    assert "| disease |" not in md
    assert "kidney cancer" not in md
    assert "**Contents:** 2 queries" in md


@pytest.mark.asyncio
async def test_record_diagram_gate_drops_and_keeps():
    """`diagram_max_chars` drops an oversized query diagram (its SPARQL still shows)
    and keeps one under a large budget."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    tiny = await create_reproducibility_record(model="m", diagram_max_chars=10)
    assert "```mermaid" not in tiny
    assert "query diagram" not in tiny  # manifest reflects the drop
    assert "```sparql" in tiny  # the query text still shows
    big = await create_reproducibility_record(model="m", diagram_max_chars=100_000)
    assert "```mermaid" in big
    assert "1 query diagram" in big


@pytest.mark.asyncio
async def test_record_curation_subset_and_order():
    """`supporting` selects a subset by 1-based index, in the order given."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)  # 1
    session.record(_q("prokn"), "json", result=JSON_RESULT)  # 2
    session.record(_q("hydrologykg"), "json", result=JSON_RESULT)  # 3
    md = await create_reproducibility_record(
        model="m", supporting=[{"index": 3}, {"index": 1}]
    )
    assert md.count("```sparql") == 2
    assert "kg/prokn" not in md  # index 2 excluded
    # order honored: hydrologykg (3) appears before sawgraph (1)
    assert md.index("kg/hydrologykg") < md.index("kg/sawgraph")


@pytest.mark.asyncio
async def test_record_curation_description_label():
    """A `supporting` item's `description` becomes the query heading label."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_reproducibility_record(
        model="m", supporting=[{"index": 1, "description": "the disease join"}]
    )
    assert "#### Query 1 — the disease join" in md


@pytest.mark.asyncio
async def test_record_out_of_range_index_warns():
    """An out-of-range `supporting` index is skipped with a warning, not an error."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_reproducibility_record(model="m", supporting=[{"index": 9}])
    assert md.startswith("<!--")
    assert "out of range" in md.split("\n")[0]
    assert md.count("```sparql") == 0  # nothing selected


@pytest.mark.asyncio
async def test_record_stub_when_oversized_publishes_full_to_resource():
    """Over `max_inline_chars`, the record returns a stub; the full body is on the
    resource (the delivery path that survives a size limit)."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_reproducibility_record(model="m", max_inline_chars=50)
    assert "delivered via resource" in md
    assert "transcript://session/latest" in md
    assert "kg/sawgraph" not in md  # body withheld inline
    full = latest_transcript_resource()
    assert "kg/sawgraph" in full  # ...but present on the resource


@pytest.mark.asyncio
async def test_record_empty_log_placeholder():
    """An empty log renders a placeholder and an empty Contents manifest."""
    md = await create_reproducibility_record(model="m")
    assert "_No queries logged._" in md
    assert "**Contents:** no queries or diagrams" in md


@pytest.mark.asyncio
async def test_record_manifest_matches_fence_counts():
    """The Contents manifest is a checkable invariant: its counts equal the actual
    fenced-block counts in the document."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record(_q("prokn"), "json", result=JSON_RESULT)
    md = await create_reproducibility_record(model="m")
    assert f"**Contents:** {md.count('```sparql')} queries" in md
    assert f"{md.count('```mermaid')} query diagrams" in md


@pytest.mark.asyncio
async def test_record_publishes_to_resource():
    """A normal (inline) run still publishes the full markdown to the resource."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_reproducibility_record(model="m")
    assert latest_transcript_resource() == md


@pytest.mark.asyncio
async def test_record_json_format():
    """`format='json'` returns a structured payload (queries + KGs), no tables."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    out = await create_reproducibility_record(model="m", format="json")
    assert isinstance(out, dict)
    assert out["model"] == "m"
    assert [e["graphs"] for e in out["query_log"]] == [["sawgraph"]]
    assert out["knowledge_graphs"][0]["shortname"] == "sawgraph"
    assert out["generated_by"]["version"] == __version__


@pytest.mark.asyncio
async def test_record_drops_foreign_and_flags_phantom():
    """The shared provenance guards apply: a foreign query is dropped, and a named
    KG no selected query touched is flagged phantom."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record(_q("prokn"), "json", result=JSON_RESULT)  # foreign
    md = await create_reproducibility_record(
        model="m", kgs_used=["sawgraph", "ubergraph"]
    )
    warn_block = md.split("# Proto-OKN")[0]  # the HTML-comment warnings, one per line
    assert "prokn" in warn_block  # foreign-drop warning names it
    assert "ubergraph" in warn_block  # phantom warning names it
    assert "kg/prokn" not in md  # dropped from the body


def test_render_query_counts_only_unit():
    """`_render_query(counts_only=True)` emits a row-count line and no table."""
    lines = _render_query(
        {"sparql": _q("sawgraph"), "row_count": 7, "results": JSON_RESULT},
        "Query 1",
        counts_only=True,
    )
    text = "\n".join(lines)
    assert "_7 row(s)_" in text
    assert "| disease |" not in text


@pytest.mark.asyncio
async def test_chat_transcript_diagram_gate():
    """Step 4: create_chat_transcript honors `diagram_max_chars` too."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    md = await create_chat_transcript(model="m", diagram_max_chars=10)
    assert "```mermaid" not in md
    assert "```sparql" in md


@pytest.mark.asyncio
async def test_record_supporting_accepts_bare_ints():
    """`supporting` accepts bare 1-based indices (easy batching), not only dicts."""
    session.record(_q("sawgraph"), "json", result=JSON_RESULT)  # 1
    session.record(_q("prokn"), "json", result=JSON_RESULT)  # 2
    session.record(_q("hydrologykg"), "json", result=JSON_RESULT)  # 3
    md = await create_reproducibility_record(model="m", supporting=[3, 1])
    assert md.count("```sparql") == 2
    assert md.index("kg/hydrologykg") < md.index("kg/sawgraph")  # order honored
    assert "kg/prokn" not in md


@pytest.mark.asyncio
async def test_record_stub_surfaces_supporting_recovery():
    """An over-size record's stub must be actionable — it points to the `supporting`
    recovery (curate / batch), not just the resource, so the caller never gives up."""
    for _ in range(3):
        session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    stub = await create_reproducibility_record(model="m", max_inline_chars=50)
    assert "transcript://session/latest" in stub  # still points to the resource
    assert "supporting=" in stub  # ...but also the actionable recovery
    assert "get_query_log" in stub
    assert "missing" in stub.lower()  # framed as "never leave it missing"


def test_active_window_elapsed_from_timestamps():
    """`_active_window` reports first→last span + elapsed from the log timestamps, and
    is empty when no timestamp is present (so no header line is emitted)."""
    from datetime import datetime, timedelta, timezone

    from mcp_okn.tools.transcript import _active_window

    assert _active_window([]) == ""
    assert _active_window([{"sparql": "x"}]) == ""  # no timestamp -> no window
    start = datetime(2026, 7, 17, 14, 2, 0, tzinfo=timezone.utc)
    entries = [
        {"timestamp": start.isoformat(timespec="seconds")},
        {
            "timestamp": (start + timedelta(hours=1, minutes=45)).isoformat(
                timespec="seconds"
            )
        },
    ]
    win = _active_window(entries)
    assert win == "2026-07-17 14:02–15:47 UTC (1h 45m)"


@pytest.mark.asyncio
async def test_record_header_has_study_active_window():
    """The reproducibility record's header carries the study active window, spanning the
    WHOLE scoped log even when `supporting` curates the shown queries to a subset."""
    from datetime import datetime, timedelta, timezone

    session.record(_q("sawgraph"), "json", result=JSON_RESULT)
    session.record(_q("prokn"), "json", result=JSON_RESULT)
    ents = session.entries()
    base = datetime(2026, 7, 17, 9, 0, 0, tzinfo=timezone.utc)
    ents[0]["timestamp"] = base.isoformat(timespec="seconds")
    ents[1]["timestamp"] = (base + timedelta(minutes=30)).isoformat(timespec="seconds")
    md = await create_reproducibility_record(
        model="m", supporting=[1], max_inline_chars=None
    )
    assert "- **Study active window:** 2026-07-17 09:00–09:30 UTC (30m 0s)" in md
    assert (
        "**Contents:** 1 query" in md
    )  # window spans the log; contents is the curated subset

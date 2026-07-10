"""Layer 2 agents — turn a natural-language ``summary`` into a result set.

An :class:`Agent` is given a dataset record (its ``summary`` and the served KG(s)
the question targets) and must return the rows it believes answer the question.
Those rows are scored against the cached reference results (see ``score.py``).

Two implementations:

- :class:`ReferenceAgent` — runs the adapted *reference* query. It should score a
  perfect 1.0, so it's the harness's end-to-end self-check (no LLM, no API key).
- :class:`ClaudeAgent` — drives the real mcp-okn tools (`get_schema`,
  `sparql_query`) through the Anthropic SDK to discover and answer from scratch,
  given only the prose summary and which KG(s) to use. This is the actual
  text-to-SPARQL measurement.
- :class:`FileAgent` — scores answers produced *outside* the harness (e.g. by
  Cowork's Claude, which is itself the model and calls the mcp-okn tools live).
  Reads a JSON map of {record_id: sparql} and runs each query. No API key — use
  this to benchmark text-to-SPARQL without an ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from mcp_okn import server as srv
from mcp_okn import sparql


@dataclass
class AgentResult:
    rows: list[dict[str, Any]]
    sparql: str | None = None
    steps: int = 0
    error: str | None = None
    transcript: list[dict[str, Any]] = field(default_factory=list)


class Agent(Protocol):
    name: str

    async def solve(self, record: dict[str, Any]) -> AgentResult: ...


class ReferenceAgent:
    """Runs the adapted reference query — the harness's 100%-accuracy control."""

    name = "reference"

    async def solve(self, record: dict[str, Any]) -> AgentResult:
        query = record.get("federated")
        if not query:
            return AgentResult(rows=[], error="record has no federated query")
        try:
            out = await sparql.run_sparql(query, fmt="json")
        except Exception as e:
            return AgentResult(rows=[], sparql=query, error=str(e).splitlines()[0])
        return AgentResult(rows=out.get("rows", []), sparql=query)


# --- File agent (key-free, e.g. Cowork) ------------------------------------


class FileAgent:
    """Scores answers produced outside the harness — no LLM call, no API key.

    Expects a JSON file mapping record id -> final SPARQL query, e.g. the
    ``answers.json`` Cowork's Claude writes after solving the exported questions
    with the live ``mcp-okn`` tools. Each query is run against the federation
    exactly like :class:`ReferenceAgent`, but with the supplied query instead of
    the curated reference.
    """

    name = "file"

    def __init__(self, answers_path: str) -> None:
        path = Path(answers_path)
        if not path.exists():
            raise SystemExit(
                f"answers file {path} not found — export questions, answer them, "
                "then point --answers at the resulting JSON."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        # Accept either {id: query} or [{"id": ..., "query"/"sparql": ...}].
        if isinstance(data, list):
            data = {
                r["id"]: r.get("query") or r.get("sparql") for r in data if r.get("id")
            }
        self._answers: dict[str, Any] = data
        self.name = f"file:{path.name}"

    async def solve(self, record: dict[str, Any]) -> AgentResult:
        query = self._answers.get(record["id"])
        if not query:
            return AgentResult(rows=[], error="no answer for id")
        try:
            out = await sparql.run_sparql(query, fmt="json")
        except Exception as e:
            return AgentResult(rows=[], sparql=query, error=str(e).splitlines()[0])
        return AgentResult(rows=out.get("rows", []), sparql=query)


# --- Claude agent ----------------------------------------------------------

_SYSTEM = """\
You answer questions by querying the Proto-OKN knowledge graphs through a single \
OKN federation SPARQL endpoint. Every triple pattern MUST be scoped to a named \
graph: GRAPH <https://purl.org/okn/frink/kg/{shortname}> {{ ... }}.

You are told which knowledge graph(s) to use. Workflow:
1. Call get_schema for each target KG to learn its classes, predicates, and the \
   exact IRIs it uses.
2. Draft a SPARQL query, scoping patterns to the KG's named graph, and test it \
   with run_sparql. Iterate until it returns sensible rows.
3. When confident, call submit_answer with your final query.

Be efficient: a handful of schema/probe calls, then answer. Do not give up early \
— if a query returns nothing, inspect the schema and adjust the IRIs/predicates."""

_TOOLS = [
    {
        "name": "get_schema",
        "description": "Get a knowledge graph's schema (classes, predicates, sample IRIs) by shortname.",
        "input_schema": {
            "type": "object",
            "properties": {"shortname": {"type": "string"}},
            "required": ["shortname"],
        },
    },
    {
        "name": "run_sparql",
        "description": "Run a SPARQL query against the federation endpoint and return up to a few rows. Use to test queries.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "submit_answer",
        "description": "Submit your final SPARQL query as the answer. Its full result set is taken as your answer.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

_PREVIEW_ROWS = 20


class ClaudeAgent:
    """Drives the mcp-okn tools via the Anthropic SDK to answer from prose."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        max_steps: int = 12,
        max_tokens: int = 4096,
    ) -> None:
        self.model = model
        self.name = f"claude:{model}"
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        # Lazy import so the dataset/smoke layers don't need anthropic installed.
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic()

    async def _dispatch(self, name: str, args: dict[str, Any]) -> tuple[str, Any]:
        """Run a tool call; return (text_for_model, final_rows_or_None)."""
        if name == "get_schema":
            schema = await srv.get_schema(args["shortname"])
            return json.dumps(schema)[:6000], None
        if name in ("run_sparql", "submit_answer"):
            query = args["query"]
            try:
                out = await sparql.run_sparql(query, fmt="json")
            except Exception as e:
                return f"ERROR: {str(e).splitlines()[0]}", None
            rows = out.get("rows", [])
            if name == "submit_answer":
                return "", {"query": query, "rows": rows}
            preview = rows[:_PREVIEW_ROWS]
            return (
                json.dumps(
                    {"row_count": out.get("row_count", len(rows)), "rows": preview}
                )[:6000],
                None,
            )
        return f"unknown tool {name}", None

    async def solve(self, record: dict[str, Any]) -> AgentResult:
        kgs = record.get("mapped_kgs") or record.get("tags") or []
        user = (
            f"Question: {record['summary']}\n\n"
            f"Knowledge graph(s) to use: {', '.join(kgs)}.\n"
            "Find the rows that answer this question, then submit_answer."
        )
        messages: list[dict[str, Any]] = [{"role": "user", "content": user}]

        for step in range(1, self.max_steps + 1):
            resp = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=_SYSTEM,
                tools=_TOOLS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": resp.content})

            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            if not tool_uses:
                # Model stopped without submitting — no answer.
                return AgentResult(rows=[], steps=step, error="no answer submitted")

            tool_results = []
            for tu in tool_uses:
                text, final = await self._dispatch(tu.name, tu.input)
                if final is not None:
                    return AgentResult(
                        rows=final["rows"], sparql=final["query"], steps=step
                    )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": text or "(empty)",
                    }
                )
            messages.append({"role": "user", "content": tool_results})

        return AgentResult(rows=[], steps=self.max_steps, error="max steps reached")

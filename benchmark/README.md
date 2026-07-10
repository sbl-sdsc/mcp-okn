# Registry benchmark

A benchmark for the mcp-okn federation query path, built from the curated example
queries in [frink-okn/okn-registry](https://github.com/frink-okn/okn-registry/tree/main/docs/registry/queries).

Each registry `.rq` file pairs a natural-language `summary` with a hand-written
SPARQL query for one knowledge graph. We turn those into two layered tests:

1. **Smoke (layer 1)** — adapt each reference query to the OKN *federation*
   endpoint (scope its `WHERE` in the KG's `GRAPH <…/kg/{shortname}>`) and run it.
   A query *passes* if it still returns rows. Passing results are the ground
   truth, cached for layer 2.
2. **Agent (layer 2)** — give the prose `summary` (and which KG to use) to an
   agent driving the real mcp-okn tools, and score the rows it returns against
   the cached reference. Only questions whose reference passed layer 1 are scored.

Scope is **only the KGs the mcp-okn server serves**. Every registry query is kept
in the dataset with an `adaptation` status:

- `auto` — GRAPH-wrapped and runnable (the benchmark set).
- `manual` — needs a human/agent: cross-KG `federation` query, or one that embeds
  its own `SERVICE`/`GRAPH`, or a non-`SELECT`/`ASK` form.
- `incompatible` — uses a function the QLever federation endpoint can't run
  (e.g. GraphDB's `ofn:asDays`); unrunnable however it's adapted, so excluded
  from the pass-rate denominator rather than counted as a failure.
- `skip` — tags map to no served KG (e.g. the generic `federation` tag).

## Files

| File | Role |
|------|------|
| `fetch_registry.py` | Download the registry, parse/adapt every `.rq`, write `dataset.jsonl`. |
| `adapt.py` | Pure parsing + SPARQL-aware GRAPH-wrapping (no network). |
| `dataset.jsonl` | The extracted corpus (committed; one JSON record per query). |
| `smoke.py` | Layer 1 — run references, cache results to `reference_results.json`. |
| `agents.py` | Layer 2 agents: `ReferenceAgent` (self-check), `ClaudeAgent` (API), `FileAgent` (scores externally-produced answers — key-free). |
| `score.py` | Execution-match scoring (exact + F1, column-name/order independent). |
| `run_benchmark.py` | CLI that runs the layers and prints a scored report. |

## Usage

```bash
# 0. See which KGs have runnable queries (offline; use any name with --kg)
python -m benchmark.run_benchmark --list-kgs

# 1. Build / refresh the dataset from the live registry (offline except the fetch)
python -m benchmark.fetch_registry --report

# 2. Layer 1 only — do the curated queries still return data?
python -m benchmark.run_benchmark --layer smoke

# 3. Harness self-check — the reference agent re-runs the reference query and
#    should score ~1.0 (proves smoke + scoring are wired correctly). No API key.
python -m benchmark.run_benchmark --agent reference

# 4. The real text-to-SPARQL measurement (needs the optional dep + a key):
uv sync --group benchmark
export ANTHROPIC_API_KEY=...
python -m benchmark.run_benchmark --agent claude --model claude-sonnet-4-6 \
    --out results.json
```

Handy flags: `--list-kgs` to list runnable KGs and exit, `--kg <shortname>` to
restrict to one graph, `--limit N` for a quick slice, `--concurrency`,
`--timeout`, `--out results.json` for a detailed dump.

### Key-free run (Cowork is the model)

`ClaudeAgent` needs an `ANTHROPIC_API_KEY` because it spins up its *own* agent
loop against the Anthropic API. Inside Cowork that's unnecessary — Cowork's Claude
is already the model and can call the live `mcp-okn` tools (`get_schema`,
`sparql_query`) directly. `FileAgent` closes the loop by scoring answers produced
that way, so no key is required:

```bash
# 1. Build the layer-1 reference cache (ground truth to score against).
python -m benchmark.run_benchmark --layer smoke          # add --kg / --limit to scope

# 2. Export the runnable questions for the model to answer.
python -m benchmark.run_benchmark --export-questions questions.json   # respects --kg / --limit

# 3. In Cowork: read questions.json. For each question, use the mcp-okn tools
#    (get_schema, then sparql_query to test) to write a final SPARQL query, and
#    save the results as answers.json — a JSON object of {id: sparql}. (A list of
#    {"id", "query"} objects is also accepted.)

# 4. Score those answers — no API key, reuses all the normal scoring/reporting.
python -m benchmark.run_benchmark --agent file --answers answers.json --out results.json
```

The system prompt and workflow `ClaudeAgent` uses (`_SYSTEM` in `agents.py`) is a
good brief for step 3. Note this measures whichever model wrote `answers.json`
(e.g. Cowork's Claude under its own harness), not the pinned
`claude-sonnet-4-6` / `max_steps=12` config of `ClaudeAgent`, so the two aren't
directly comparable.

## Scoring

Answers are compared by **denotation**, not by SELECT clause: each row becomes the
sorted tuple of its cell values (column names and row/column order ignored), and
the result is the multiset of those tuples. `exact` = identical multisets; `f1` /
`jaccard` give partial credit. Numeric/string forms that print equally compare
equal (`1` == `1.0` == `"1"`). See `score.py`.

## Tests

- `tests/test_benchmark.py` — offline logic (parse, adapt, GRAPH-wrap, scoring,
  dataset integrity). Always runs.
- `tests/test_benchmark_smoke.py` — opt-in live layer-1 gate:
  `RUN_BENCHMARK_SMOKE=1 pytest tests/test_benchmark_smoke.py`.

## Status / notes

- **Layer 1 + scoring are verified** end-to-end against the live endpoint
  (reference agent scores 100% exact on the validated slice).
- **`ClaudeAgent` is scaffolded but not yet live-tested** here (needs `anthropic`
  + an API key). The tool loop exposes `get_schema`, `run_sparql`, and
  `submit_answer`; review/iterate before trusting its numbers. For a key-free
  text-to-SPARQL run, use the `FileAgent` / Cowork path above instead.
- Coverage today (`--report`): **60 runnable** (`auto`) queries across 15 KGs,
  plus 8 `manual`, 3 `incompatible`, 9 `skip` retained for visibility. A full
  smoke pass currently runs ~71% green; the failures are genuine (data not in the
  federation under that graph, or schema drift), not harness bugs — `nasa-gesdisc-kg`
  is notably 0/5. Re-run `fetch_registry` to refresh as the registry grows;
  `sockg` dominates the count, so prefer per-KG reporting (`--kg`) over aggregates.

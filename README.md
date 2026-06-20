# mcp-okn

An MCP server for querying the **federated SPARQL endpoint**
(`https://frink.apps.renci.org/federation/sparql`) over the
[Proto-OKN](https://www.proto-okn.net/) knowledge graphs.

It lets an LLM discover which knowledge graphs are relevant (from the
[okn-registry](https://registry.okn.us/registry/) descriptions), then run
SPARQL queries scoped to one or more named graphs of the form
`https://purl.org/okn/frink/kg/{shortname}`.

---

## About Proto-OKN

[Proto-OKN](https://www.proto-okn.net/) — the **Prototype Open Knowledge
Network** — is a National Science Foundation initiative (with NASA, NIH, the
National Institute of Justice, NOAA, and the U.S. Geological Survey) that funds
research teams to build a publicly accessible, interconnected set of data
repositories and knowledge graphs. The graphs span domains such as health, the
environment, criminal justice, space exploration, and supply-chain security, and
are served together over the **FRINK** federated SPARQL endpoint that this server
queries. The [okn-registry](https://registry.okn.us/registry/) catalogs
the participating knowledge graphs.

---

## Examples

### Example prompts

Once the server is configured in your MCP client (see
[Configuration](#configuration)), just ask in natural language — the assistant
picks the graphs, writes the SPARQL, and combines the results for you. Some
prompts to try:

- *"List all Proto-OKN knowledge graphs as a table of shortname and description."* — [Result](docs/crosswalks/proto-okn-knowledge-graphs.md)
- *"List all verified crosswalks, grouped by domain, with an example of what each answers."* — [Result](docs/crosswalks/proto-okn-crosswalk-inventory.md)
- *"Give a high-level overview of the spoke-genelab knowledge graph — its main classes and relationships — and draw the schema diagram."* — [Result](docs/spoke-genelab-schema.png)
- *"Which genes does rdkg associate with autism spectrum disorder?"* — [Result](docs/crosswalks/crosswalks_examples/disease06_q1_spoke-rdkg_autism-genes.md)
- *"What is the maximum PFAS measurement in each county?"* — [Result](docs/crosswalks/crosswalks_examples/geospatial04_q1_sawgraph_spatialkg_pfas_max_by_county.md)
- *"How do I join spoke-okn and prokn? Show the verified recipe and shared identifier."* — [Result](docs/crosswalks/spoke-prokn-join.md)
- *"Create a chat transcript of this analysis."* — downloads as Markdown and is served as the `transcript://session/latest` resource
- *"Create a chat transcript of this analysis in PDF format."* — the server returns Markdown and the client converts the `.md` to a `.pdf` file (Claude Desktop / claude.ai)

### Crosswalk queries & transcripts

A **crosswalk** is a verified way to join two (or three) Proto-OKN knowledge
graphs on a shared identifier — for example linking a disease in one graph to the
genes another graph associates with it via a common MONDO or DOID id. Because the
graphs are built by different teams on different ontologies, the value of the
federation is in these connections: a crosswalk is an *integration opportunity*
where a question one graph can't answer alone becomes answerable by combining two.
This section catalogs the verified crosswalks and shows the queries that exercise
them.

A visual map of the whole network — all 92 crosswalks across 32 graphs, with
`ubergraph` and `wikidata` as bridge hubs (edge width ∝ log of the verified join
count). See the [session transcript](docs/crosswalks/crosswalk-transcript.md) for
how it was built.

> **▶ Click the image to open the interactive, zoomable network.**

[![Proto-OKN crosswalk network](docs/crosswalks/crosswalk-network.png)](https://rawcdn.githack.com/sbl-sdsc/mcp-okn/2bdca84de443a0573dff07f0ce341cdccf6bb3a3/docs/crosswalks/crosswalk-network.html)

Three resources, each backed by live federated SPARQL joins verified to actually
answer the question (biomedical claims checked against PubMed / Paperclip;
geospatial and industrial joins against their authoritative shared standard):

- **[Proto-OKN Crosswalk Inventory](docs/crosswalks/proto-okn-crosswalk-inventory.md)**
  — a single-page map of all **92 verified crosswalks**: the joined KGs, shared
  key, row count, and a one-line note on what each answers. Start here to see which
  graphs connect and on what identifier.
- **[Cross-KG crosswalk catalog](docs/crosswalks/crosswalks_example.md)** — the
  same 92 crosswalks worked into 184 example questions (two per recipe) across 7
  domains (Genes, Proteins, Chemicals, Disease & Phenotype, Taxonomy, Geospatial,
  Industry & Supply Chain), each with a full transcript.
- **[Multi-domain integration catalog](docs/crosswalks/multi-domain-examples.md)**
  — 24 use cases that fuse *different* domains (e.g. toxicology × transcriptomics
  × clinical disease, or PFAS sampling × hydrology × public health).

Every catalog row links to a standalone, replayable transcript — the prompt, the
answer, and every verbatim SPARQL query with its result. Here are a few examples
from the crosswalk catalog:

| Question | Knowledge graphs | Transcript |
|---|---|---|
| Which genes does rdkg associate with autism spectrum disorder (bridged DOID↔MONDO via ubergraph)? | spoke-okn × rdkg × ubergraph | [md](docs/crosswalks/crosswalks_examples/disease06_q1_spoke-rdkg_autism-genes.md) |
| AOP target genes differentially expressed in gene-expression-atlas-okn disease studies | biobricks-aopwiki × gene-expression-atlas-okn | [md](docs/crosswalks/crosswalks_examples/genes01_q1_aopwiki-gxa_aop-targets-de-disease.md) |
| Maximum PFAS measurement by county | sawgraph × spatialkg | [md](docs/crosswalks/crosswalks_examples/geospatial04_q1_sawgraph_spatialkg_pfas_max_by_county.md) |
| Diabetes gene dossier — pankgraph genes × gene-expression-atlas-okn expression × spoke-okn disease | gene-expression-atlas-okn × pankgraph × spoke-okn | [md](docs/crosswalks/multidomain_examples/multi-domain01_diabetes_gene_dossier.md) |

These transcripts are produced by `create_chat_transcript` and can be re-run
against the endpoint with `scripts/replay_transcript.py`.
The catalogs were generated by driving the model with the
[crosswalk generation prompt](docs/crosswalks/crosswalks_prompt.md) — list every
`list_crosswalks` recipe, write two research questions per crosswalk, run and
verify each as live SPARQL, and validate the findings against the literature.

---

## Configuration

### Requirements

Install **[uv](https://docs.astral.sh/uv/)** (see the
[installation guide](https://docs.astral.sh/uv/getting-started/installation/)),
then clone this repo:

```bash
git clone https://github.com/sbl-sdsc/mcp-okn.git
```

### Register the server

For Claude Code, register it from the CLI:

```bash
claude mcp add mcp-okn -- uv --directory /path/to/mcp-okn run mcp-okn
```

Or add it to any MCP client's config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-okn": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-okn", "run", "mcp-okn"]
    }
  }
}
```

Replace `/path/to/mcp-okn` with the absolute path to your checkout.

---

## Tools and resources

### Tools

The tools follow a typical analysis arc — **discover → inspect → plan a join →
query → record**. The single table below is grouped in that order.

| Tool | Purpose |
| --- | --- |
| **1. Discover graphs** | |
| `list_kgs` | List all KGs with `shortname`, `title`, `description`, `homepage`, and `named_graph`. Served from a bundled snapshot for instant cold start. |
| `describe_kg(shortname, long_description=False)` | Full registry doc (frontmatter + prose) for one KG, for deeper context. Set `long_description=True` for the registry's ~150-word prose body — useful for picking among near-overlapping KGs. |
| **2. Inspect a graph's schema and identifiers** | |
| `get_schema(shortname, compact=True)` | Schema for one KG — classes, predicates, edge properties (with reification query templates), and node properties. Uses curated metadata when available, else probes the endpoint for distinct classes/predicates. Call **before** writing a query. |
| `visualize_schema(shortname)` | Deterministic Mermaid `classDiagram` of a KG's schema, built server-side from `get_schema` — class boxes, labeled edges, and edge-property predicates as intermediary classes with typed fields (node classes light blue, edge classes orange, with a legend). When the curated metadata names predicates but not their endpoints, edges are recovered from the graph's `rdfs:domain`/`rdfs:range` scoped to the curated classes. Returns `mermaid_block` (already wrapped in a ` ```mermaid ` fence) — output it **verbatim**; don't redraw it as SVG/an image. Rendered examples: [spoke-genelab](docs/spoke-genelab-schema.png), [dreamkg](docs/dreamkg-schema.png), [rdkg](docs/rdkg-schema.png) ([details](docs/verification-visualize-schema.md)). |
| `probe_namespaces(shortname, predicate, sample=0)` | Report which identifier/ontology namespaces populate a predicate's objects. `get_schema` lists a KG's predicates but not which controlled vocabularies fill their values — call this before the main query whenever a predicate's objects are ontology terms (diseases, chemicals, genes, anatomy) to see the actual namespace distribution and pick the best identifier to join on. Exploratory — not logged. |
| `find_crosswalks(shortname, sample=0)` | Find ontology/database ids in a KG however they are encoded, profiling all three places at once: mapping predicates (`rdfs:seeAlso`, `owl:sameAs`, SKOS `*Match`, `oboInOwl:hasDbXref`), node IRIs that *are* the ontology term (`role="subject"`), and domain-specific predicates carrying an id (`role="object"`). The latter two are invisible to a mapping-predicate-only scan. Use whenever a KG seems to lack the identifier you need on its obvious predicates. |
| **3. Plan a cross-graph join** | |
| `list_crosswalks(include_examples=True)` | List **every** verified cross-KG integration point in one call — a global map of which graphs connect and on what shared key. Rows are grouped by `domain` (Genes, Geospatial, Disease & phenotype, …) and sorted by ontology, ready to render as a table. Each row is a compact summary (`domain`, connected `kgs` in join order by official shortname, `shared_key`, `bridge_kg`, `verified_count`, and an `example_question` by default; set `include_examples=False` for a terser list). Use `get_join_strategy(kg_a, kg_b)` for a single pair's full recipe. |
| `get_join_strategy(kg_a, kg_b=None)` | Look up a precomputed, hand-verified recipe for joining two KGs — predicates, roles, shared identifier, bridge graph, verified count, and a runnable `skeleton_query` (the example SPARQL to copy and build on; it already encodes the IRI rewrites). Call **before** writing a federated join. Returns `verified` / `known_non_join` / `unknown`; with `kg_b` omitted, lists every join touching `kg_a`. |
| `taxon_overlap(kg_a, kg_b)` | Compose the NCBITaxon overlap between two hub KGs *through* `ubergraph`. Returns two runnable skeletons — `exact_id` (same taxon id) and `clade_membership` (kg_b taxa under kg_a's clades via `subClassOf*`, which can be far larger when one side is coarser-grained) — plus, for a pair with a precomputed non-zero overlap, the materialized counts under `materialized_overlap` (the same per-pair counts `list_crosswalks` surfaces in the NCBITaxon hub row). Run a skeleton with `sparql_query`. |
| `point_to_s2(lat, lng, level=13)` | Convert a lat/long point to its spatialkg/KWG S2 cell IRI (Level-13 default) — the deterministic primitive behind the spatial bridge. Use when a KG carries POINT coordinates but no S2 key and you need the cell IRI spatialkg stores. |
| `spatial_bridge(point_query, target_pattern, select_vars="*", extra_prefixes="", limit=500)` | Generic point→S2 bridge for **any** point-bearing graph that lacks a stored S2 key (sudokn is the first such graph). `point_query` must `SELECT ?site ?lat ?lng`; the server computes each cell in Python and injects `(?site ?cell)` as a `VALUES` block into a federated query whose `target_pattern` joins `?cell` to spatialkg/fiokg/sawgraph (e.g. county/FIPS). Nothing is persisted — the computed key lives only inside the request. |
| **4. Run queries** | |
| `sparql_query(query, format="json", exploratory=False, compact=False)` | Run a SPARQL query on the federation endpoint. Substantive results are logged for the transcript unless `exploratory=True`. Pass `compact=True` for a token-efficient json shape — `{"columns", "data", "count"}` with positional rows — instead of the default repeated-key `{"vars", "rows", "row_count"}` (affects only the returned payload, not the transcript). A bracketed `<https://schema.org/…>` IRI is canonicalized to the `http://` form most KGs store (string literals and `IRI(CONCAT(…))` are left as written). A few KGs store the `https://` form (nikg, ruralkg, ufokn); reach those predicates by binding the predicate as a variable and matching scheme-free, e.g. `FILTER(STRENDS(STR(?p),'schema.org/location'))`. |
| `expand_ontology_term(term, relation="subClassOf", direction="descendants", include_self=True, limit=1000)` | Expand an ontology term to its full subtree/closure via the `ubergraph` graph. |
| **5. Record a reproducible transcript** | |
| `reset_query_log()` | Clear the session query log. Call at the **start** of an analysis to scope a transcript. |
| `get_query_log()` | Return the queries logged so far this session (only those that returned rows and weren't exploratory). |
| `create_chat_transcript(model, exchanges, ...)` | Emit a reproducible markdown (or JSON) record of a session — prompts, answers, the verbatim queries + results that produced findings, and any `visualize_schema` diagrams. Call at the **end** of an analysis. |

### Resources

| Resource | Purpose |
| --- | --- |
| `transcript://session/latest` (`text/markdown`) | The most recent transcript rendered by `create_chat_transcript`, so a client can fetch/save the document directly (transport-agnostic; works for remote servers). Cleared by `reset_query_log`. |

---

## Development

### Module layout

The package is organized by concern. `server.py` is a thin assembly point: it
imports the tool modules to trigger their `@mcp.tool()` registration and
re-exports their public symbols (so `from mcp_okn.server import ...` keeps
working). The shared `mcp` application instance lives in `app.py`, separate from
`server.py`, so the tool modules can import it without a circular dependency.

```
src/mcp_okn/
├── app.py            # the shared FastMCP `mcp` instance + INSTRUCTIONS
├── server.py         # assembly point: registers tools, re-exports, main()
├── registry.py       # KG discovery from the okn-registry (+ bundled snapshot)
├── schema.py         # get_schema / visualize_schema logic
├── sparql.py         # federation endpoint client + schema.org normalization
├── crosswalks.py     # curated cross-KG join table (data/crosswalks.json)
├── taxon.py          # NCBITaxon hub: taxon-overlap skeleton composition
├── session.py        # in-memory query/diagram log for transcripts
├── data/             # bundled snapshots: kgs.json, crosswalks.json
└── tools/            # one module per concern; each registers via @mcp.tool()
    ├── _shared.py        # helpers used by >1 tool module (_to_uri, …)
    ├── discovery.py      # list_kgs, describe_kg
    ├── schema_tools.py   # get_schema, visualize_schema
    ├── probe.py          # probe_namespaces, find_crosswalks
    ├── joins.py          # get_join_strategy, taxon_overlap, list_crosswalks
    ├── query.py          # sparql_query, expand_ontology_term
    └── transcript.py     # reset/get_query_log, create_chat_transcript, resource
```

```bash
uv run python -m pytest       # unit tests (offline)
uv run ruff check .           # lint
uv run ruff format .          # auto-format (use --check in CI)
uv run mypy                   # type-check src/mcp_okn
# live smoke test:
uv run python -c "import asyncio; from mcp_okn.sparql import run_sparql; \
print(asyncio.run(run_sparql('SELECT ?s WHERE { ?s ?p ?o } LIMIT 3')))"
```

CI (`.github/workflows/ci.yml`) runs ruff lint, ruff format-check, and mypy on
every push/PR, plus the offline test suite on Python 3.10 and 3.12.

Deferred improvements are tracked in [BACKLOG.md](BACKLOG.md) — currently empty.

### Verification notes

Reproducible checks of behaviors that aren't covered by the offline unit tests:

- [schema.org http/https normalization](docs/verification-schema-org-normalization.md)
  — a bracketed `<https://schema.org/…>` IRI is canonicalized to `http`, so a query
  written with the `https` form still hits `http`-stored data (dreamkg `schema:Rating`
  → 3762), while string literals / `IRI(CONCAT(…))` are left intact (see below).
- [visualize_schema rendering](docs/verification-visualize-schema.md) — the
  generated Mermaid renders cleanly as a class diagram via `mermaid-cli` across
  all three schema paths (curated, class-only, probe fallback), and survives the
  `create_chat_transcript` round-trip.
- [transcript MCP resource](docs/verification-transcript-resource.md) — the
  `transcript://session/latest` resource serves the full document via the
  resource API, with its embedded diagram still rendering.

#### schema.org predicates stored under the non-canonical `https` form

A few graphs store schema.org terms under the `https://` form. The canonicalization
hits **only bracketed IRIs**, so those predicates are unreachable by IRI (the bracketed
`https` form is rewritten to `http`, which the data isn't), but match when the predicate
is bound as a variable or the IRI is rebuilt from a string literal (now preserved).
Verified live against the federation:

| Graph (predicate) | `<https://schema.org/X>` (bracketed) | `IRI(CONCAT('https://schema.org/','X'))` | `STRENDS(STR(?p),'schema.org/X')` |
| --- | --- | --- | --- |
| `nikg` (`location`) | 0 | 296,189 | 296,189 |
| `ruralkg` (`postalCode`) | 0 | 9,037 | 9,037 |
| `ufokn` (`value`, level-13 sample) | 0 | 5/5 (`LIMIT 5`) | 5/5 |

In each case the `IRI(CONCAT)` and `STRENDS` forms agree (same rows / same decimal S2
ids for ufokn) while the bracketed IRI returns 0 — confirming the literal-preservation
fix and the variable-predicate workaround documented in the `ruralkg`/`ufokn` crosswalk
notes.

### KG snapshot

`list_kgs` serves a static snapshot bundled at `src/mcp_okn/data/kgs.json` (~41
KGs), so the first call returns instantly without fetching the individual
registry files. The live registry is only contacted when the snapshot is missing
(or when an internal `refresh=True` is passed). To refresh the snapshot after the
registry changes:

```bash
uv run python scripts/refresh_snapshot.py
```

KGs that are in the registry but not actually loaded under their expected
federation named graph (currently `semopenalex` and `biohealth`) are filtered
out, so `list_kgs` only returns graphs that are queryable.

The curated crosswalk table is edited at `metadata/crosswalks.json` and bundled to
`src/mcp_okn/data/crosswalks.json` by the same `refresh_snapshot.py` run. Two helpers
recompute its live-verified counts against the federation and write them back:
`scripts/verify_skeletons.py` (per-crosswalk `skeleton_query` counts) and
`scripts/refresh_taxon_overlaps.py` (the NCBITaxon hub's pairwise `exact_id` + clade
counts — `--inject` to write, `--pair A B` for one pair). Run `refresh_snapshot.py`
afterwards to sync the bundled copy.

---

## Citation

`mcp-okn` is the next-generation successor to
[`mcp-proto-okn`](https://github.com/sbl-sdsc/mcp-proto-okn). If you use this
software, please cite the paper describing that predecessor:

> Rose, P. W., Good, B. M., Saravia-Butler, A. M., Nelson, C. A., Balhoff, J. P.,
> Kebede, Y., Whetzel, P. L., Bizon, C., Su, A. I., & Baranzini, S. E. (2026).
> *mcp-proto-okn: Natural-language access to open scientific knowledge graphs
> through the Model Context Protocol*. arXiv:2605.30283.
> <https://arxiv.org/abs/2605.30283>

```bibtex
@misc{rose2026mcpprotookn,
  title         = {mcp-proto-okn: Natural-language access to open scientific knowledge graphs through the Model Context Protocol},
  author        = {Rose, Peter W. and Good, Benjamin M. and Saravia-Butler, Amanda M. and Nelson, Charlotte A. and Balhoff, James P. and Kebede, Yaphet and Whetzel, Patricia L. and Bizon, Christopher and Su, Andrew I. and Baranzini, Sergio E.},
  year          = {2026},
  eprint        = {2605.30283},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2605.30283}
}
```

---

## Funding

- **National Science Foundation** Award [#2333819](https://www.nsf.gov/awardsearch/show-award?AWD_ID=2333819): "Proto-OKN Theme 1: Connecting Biomedical information on Earth and in Space via the SPOKE knowledge graph"
- **National Science Foundation** Award [#2535091](https://www.nsf.gov/awardsearch/show-award?AWD_ID=2535091): "Proto-OKN Theme 2: OKN-Fabric"

---

## License

This project is licensed under the [BSD 3-Clause License](LICENSE).

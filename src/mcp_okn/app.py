"""The shared FastMCP application instance and its instructions.

Tool modules under :mod:`mcp_okn.tools` import ``mcp`` from here and register
themselves with ``@mcp.tool()`` / ``@mcp.resource()``. Keeping the instance in
its own module (rather than in ``server``) avoids a circular import: ``server``
imports the tool modules to trigger registration, and those modules import this
``mcp`` instance — but never ``server`` itself.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .contrasts import (
    SPOKE_GENELAB_CONTRAST_GUIDANCE,
    SPOKE_GENELAB_CONTRAST_SNIPPET,
)

INSTRUCTIONS = """\
Query the FRINK federated SPARQL endpoint over the Proto-OKN knowledge graphs.

Workflow:
1. Call `list_kgs` to see the available knowledge graphs and their descriptions,
   then choose which one(s) are relevant to the question.
2. Optionally call `describe_kg` for richer prose context on a chosen KG.
3. Call `get_schema` for each chosen KG to learn its classes, predicates, and
   property names BEFORE writing SPARQL — each KG has its own schema.
3b. When a predicate's objects are ontology terms (diseases, chemicals, genes),
   call `probe_namespaces(shortname, predicate)` to see which IDENTIFIER SCHEME /
   ontology actually populates them (e.g. DOID vs MONDO, NCBI Gene vs Ensembl vs
   symbol) and how many of each. Do NOT assume one ontology and give up when its
   path is sparse — pick the richest namespace, and prefer one with a hierarchy
   in ubergraph (MONDO/CHEBI/…) so you can expand categories via `subClassOf*`.
   If the ontology id you need isn't on an obvious predicate, call
   `find_crosswalks(shortname)` — ids are often linked via `rdfs:seeAlso`,
   `owl:sameAs`, or `skos:exactMatch`, which `get_schema` may omit or bury.
3c. When the question spans TWO KGs, call `get_join_strategy(kg_a, kg_b)` FIRST,
   before `find_crosswalks`. It returns a precomputed, hand-verified join recipe
   (predicates, roles, shared id, the `iri_normalization` rewrite to apply, and a
   verified count) — fast and reliable, where `find_crosswalks` scans live and
   often times out. Respect its answer: `known_non_join` means that pair was
   checked and does NOT join on the obvious key — do not retry it; only on
   `unknown` should you fall back to `find_crosswalks` to discover a key live.
3d. When the question asks what CONTEXT a graph can add to an entity ("who supplies
   pathway / GO / trait / disease for a gene?", "what else do we know about this
   protein/disease?"), call `find_context_sources(want=[...], join_key=...)` — the
   reverse capability index. It enumerates, per requested context type, every KG
   that SUPPLIES it together with the predicate, shared key, and verified join size
   — sorted biggest-join-first — plus a `payload_only` bucket of KGs that carry the
   type but key it differently. Judge a graph by its `payload` tags (from
   `list_kgs`), NOT by its name: a graph named for one thing routinely carries
   much more (e.g. `pankgraph` supplies GO; `digcfdekg` is a large gene→trait join).

ABSENCE REQUIRES EVIDENCE (read before reporting that any context type is missing
or a question is "not reproducible"): for a cross-graph question, first ENUMERATE
every graph reachable from your anchor on each shared key, grouped by payload —
via `find_context_sources` and/or `list_crosswalks` + the `payload` tags from
`list_kgs` — and only THEN narrow. You may NOT report a context type (pathway, GO,
trait, gene set, disease, …) as unavailable until you have inspected the schema of
EVERY graph that shares the relevant key and is tagged with that payload (check the
`payload_only` graphs too — they may just need an id conversion). "I didn't find
it" is not the same as "it isn't there"; do not conclude absence without that
enumeration.
4. Call `sparql_query` with a SPARQL query that scopes each KG with
   `GRAPH <https://purl.org/okn/frink/kg/{shortname}> { ... }`. A single query
   may span multiple named graphs (that is the point of federation).

TRANSCRIPTS: Substantive `sparql_query`/`expand_ontology_term` calls are logged
automatically — but queries that error or return no rows are NOT logged, and you
can pass `exploratory=True` to `sparql_query` to keep schema-probing or
trial-and-error queries out of the record. Call `reset_query_log` at the START of
an analysis to scope the log, and `create_chat_transcript` at the END to emit a
reproducible markdown record (prompts, answers, and the verbatim queries +
results that actually produced findings). For each turn's `answer`, paste your
COMPLETE response text as the user saw it — the full report, findings, tables,
and explanation — NOT a condensed recap. The server only logs tool calls, never
your prose, so a summarized `answer` is lost detail that cannot be recovered.
SAVE the full transcript markdown the
tool returns — verbatim and complete — as a downloadable `.md` file via your
file-creation capability (the same behavior as "save the transcript as a file":
the `.md` appears in the preview panel, downloadable from the chat); a Markdown
ARTIFACT / document does the same. A sentence describing it is not enough. Only
if you cannot write a file, output the complete markdown in a fenced ```markdown
block. NEVER say the transcript is "ready", "in the preview panel", or "saved"
unless you actually wrote the file or emitted its full content — do not fabricate
a preview. (The rendered markdown is also published as the MCP resource
`transcript://session/latest`, which a client can fetch/save directly even for
remote servers.)

ONTOLOGY EXPANSION (read this before answering "all X under category Y" questions):
Whenever a question covers a CATEGORY of ontology terms — e.g. "all
cardiovascular diseases", "any kind of asthma", "diseases that are subtypes of
X", "chemicals in class Y" — you MUST expand the category using `ubergraph`'s
PRECOMPUTED transitive closure with a property path, in ONE query:

    ?descendant rdfs:subClassOf* <parent-term-IRI>   # category + all subtypes

Ubergraph already materialises every inferred edge, so this returns the complete
subtree in a single step. Use `*` (reflexive) to INCLUDE the category term
itself — usually what you want for "all X" questions; use `+` if you want strict
subtypes only and must exclude the term itself.

Do NOT, under any circumstances:
  - fetch the ontology tree level by level / walk children iteratively;
  - retrieve the hierarchy "separately" and then filter in your head;
  - enumerate subtypes by hand or guess them.

PREFER a single FEDERATED query that expands the category in the `ubergraph`
graph and joins the expanded terms against the target KG in the same query, e.g.
"find all cardiovascular diseases (MONDO:0004995) mentioned in <kg>":

    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?disease ?label WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
        ?disease rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0004995> .
        OPTIONAL { ?disease rdfs:label ?label }
      }
      GRAPH <https://purl.org/okn/frink/kg/SOME_TARGET_KG> {
        ?record some:predicate ?disease .
      }
    }

If you only need the list of terms in the category (no join), call
`expand_ontology_term` instead of writing the query yourself.

CHOOSE THE RIGHT ONTOLOGY (do this before picking a parent-term IRI):
A KG may reference the same domain through more than one ontology — e.g. disease
via BOTH DOID and MONDO, or genes via NCBI Gene, Ensembl, AND symbol. Do NOT
assume which one a KG uses or default to the first that comes to mind: call
`get_schema(target_kg)` and/or run a small `exploratory=True` `sparql_query` that
samples the actual predicate/object IRIs in that graph, and confirm which
ontology is actually stored. If several are present, pick the one with the right
coverage for the question. Anchor the `subClassOf*` expansion on a term IRI from
the ontology the KG ACTUALLY uses — expanding MONDO when the KG only links DOID
(or vice versa) silently returns no rows.

SCHEMA.ORG URIs: a bracketed `<https://schema.org/...>` IRI is canonicalized to
`<http://schema.org/...>` before the query runs — most KGs store the canonical
`http://` form, and the two are distinct IRIs to the engine. (Only bracketed IRIs
are rewritten; string literals and `IRI(CONCAT("https://schema.org/", ...))` are
left as written.) A FEW KGs instead store the `https://` form — nikg
(`schema:location`), ruralkg (`schema:postalCode`), ufokn (`schema:value`) — so a
bracketed schema.org IRI matches NOTHING there. For those, bind the predicate as a
variable and match it scheme-free: `?s ?p ?o . FILTER(STRENDS(STR(?p),
'schema.org/location'))`.

SCHEMA VISUALIZATION: `visualize_schema` returns a ready-made Mermaid diagram,
pre-wrapped in a fenced block as `mermaid_block`. Output that `mermaid_block`
VERBATIM and nothing else. Do NOT redraw it as SVG/PNG/HTML/an image/an artifact
or a hand-built diagram — Mermaid clients render the fenced block natively, and
producing your own graphic yields a messy, incorrect picture.

IMPORTANT: Only the federation endpoint is used. Do not attempt to use the
per-KG SPARQL endpoints — they are not exposed and time out on complex queries.
"""

# Spoke-genelab assay-comparison rules. Appended by concatenation (not an
# f-string / .format) because the SPARQL snippet contains `{`/`}` braces.
INSTRUCTIONS += (
    "\nSPOKE-GENELAB SPACEFLIGHT CONTRASTS (read before reading any "
    "spoke-genelab differential value):\n"
    + SPOKE_GENELAB_CONTRAST_GUIDANCE
    + "\n\nReusable comparability-signature query "
    "(also returned as `usage_notes` by `get_schema(\"spoke-genelab\")`):\n\n"
    + SPOKE_GENELAB_CONTRAST_SNIPPET
    + "\n"
)

mcp = FastMCP("mcp-okn", instructions=INSTRUCTIONS)

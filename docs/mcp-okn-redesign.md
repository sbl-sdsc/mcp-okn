# mcp-okn: redesign of mcp-proto-okn

Cleaner multi-graph querying, automated registry/schema handling, deterministic diagrams, and reproducible transcripts.

| Change area | mcp-proto-okn (current) | mcp-okn (new) |
|---|---|---|
| **Query model** | Single-graph queries; multi-graph answers merged outside the endpoint. | Native multi-graph & cross-graph bridge queries with explicit named-graph scoping (`purl.org/okn/frink/kg/{shortname}`). |
| **KG coverage** | Subset of 35 KGs plus Ubergraph. | All OKN-loaded KGs. |
| **Registry + schema** | Registry built semi-automatically from GitHub metadata; curated repo schemas. | Auto-built from the OKN registry, cached at startup; topology read from `okn-void`, with URI-matched curated labels, descriptions, and property guidance. |
| **Schema diagrams** | LLM-generated Mermaid schema diagrams, so output may vary. | Server-generated Mermaid diagrams from the schema — deterministic and reproducible. |
| **Ontology expansion** | Ontology subtree traversal in Ubergraph is iterative. | Full-subtree expansion using precomputed Ubergraph closures. |
| **Cross-graph joins** | Each graph queried separately; results merged server-side. | Precomputed, verified join recipes: `list_crosswalks` / `find_crosswalks` and `get_join_strategy` (shared key, predicates, runnable skeleton query). |
| **Geospatial** | No spatial helpers. | `point_to_s2` maps a lat/long to its S2 cell IRI for geospatial joins. |
| **Reproducibility** | No explicit query logging; transcripts summarize work, not verbatim. | Explicit query-log controls; transcripts include executable queries for replay. |

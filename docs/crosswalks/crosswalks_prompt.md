## Prerequisites
Activate mcp-okn, pubmed, and paperclip MCP servers

## Prompt for Claude Cowork to generate two exmaple Q&A for each crosswalk for a specified domain

Goal: Demonstrate and validate a "insert domain name here" data-integration use case across the Proto-OKN knowledge graphs using the mcp-okn service. Steps:

1. Call mcp-okn list_crosswalks to retrieve all precomputed cross-KG integration points.
2. For each relevant crosswalk write two realistic natural-language research question that a researcher would actually ask AND that genuinely requires joining the two KGs on their shared identifier to answer. For each, state the two KGs and the shared identifier the question depends on.
3. Translate each question into a runnable SPARQL query. Then execute with sparql_query.
4. Verify each result actually answers its question. A result counts as valid only if the query (a) runs without error, (b) returns non-empty results, and (c) returns rows that plausibly answer the natural-language question — not just any rows. Show me a sample of results and one line on why they answer the question.
5. Use the PubMed and PaperClip MCP servers to validate the results. Keep only queries where evidence exists in the literature.
6. If a query errors, returns nothing, or returns irrelevant data, iterate: adjust the query, identifiers, or join, or swap to a different crosswalk. Cap at ~3–4 iterations per question. If you still can't get one working, report what you tried and where it broke.
7. Use the create_chat_transcript tool to create a chat transcript in .md and .pdf format for each query and save it in the project folder. IMPORTANT, create a separate transcript for each query, so the query log can be captured.
   IF YOU RUN SEVERAL AUTHORING AGENTS IN PARALLEL: they all share ONE MCP session, so the auto query log mixes their queries together — without care, an agent's transcript ships a sibling's SPARQL and drops its own. Give each agent a unique `scope` string and have it pass that same scope to `reset_query_log`, `sparql_query` AND `create_chat_transcript`. (Belt and braces: always pass `kgs_used`; the server then drops any logged query touching none of those KGs and warns, so a forgotten scope can't corrupt a transcript silently.)
8. Create an "examples.md" file that lists each use cases (very short title, kgs, used, ontologies or identifiers used to bridge., and link to the .md transcript. Success criterion: at least one fully working, verified query for each crosswalk.
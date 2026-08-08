# Verification: visualize_schema renders

Confirms that the Mermaid produced by `visualize_schema` (generated server-side
in `src/mcp_okn/schema.py`) is valid and renders as a class diagram — not just
syntactically plausible text.

## Method

`visualize_schema` calls `get_schema(shortname, compact=False)` and separates
topology from semantic enrichment:

- `okn-void` classes supply the class boxes;
- `okn-void` observed edges supply every source-class → predicate →
  target-class connection;
- URI-matched curated metadata supplies labels, descriptions, typed node
  properties, and RDF-reification property mappings;
- predicates without an observed object-class path are emitted as `%%` comments.

Curated predicate `SourceClass` / `TargetClass` values are ignored. The
implementation also does not probe the target graph or infer edges from declared
`rdfs:domain` / `rdfs:range`.

```bash
# write the diagram (no fences) to a .mermaid file, then:
npx -y @mermaid-js/mermaid-cli -i schema.mermaid -o schema.png -s 2
```

## Current Result

Live local verification on 2026-08-08 confirmed:

- `gene-expression-atlas-okn` restored 41 curated descriptions, all 18 observed
  node-property annotations, and both edge-property annotations while retaining
  the VoID-observed `Assay → has_attribute → AnatomicalEntity` path. Its two edge
  properties lack `EdgePropertyOf` values, so they are reported as unmapped and
  no query template is invented.
- `spoke-genelab` restored 28 typed node properties and 20 edge properties
  across three reified relationship types. The relationship classes are wired
  through VoID-observed endpoints, and their query templates use full predicate
  URIs rather than assuming every term is in the KG schema namespace.
- Both tool results explicitly report `topology_source: okn-void` and
  `curated_predicate_endpoints_used: false`.

The automated tests also reverse a curated endpoint pair and confirm the diagram
still follows the opposite VoID-observed direction.

The PNGs stored beside this document predate this combined topology/enrichment
implementation and remain historical artifacts.

## Result — transcript round-trip (end-to-end)

Confirms a `visualize_schema` diagram survives into `create_chat_transcript` and
still renders — i.e. the diagram is auto-logged to the session and embedded in
the transcript markdown, not dropped.

Steps:

1. `visualize_schema("spoke-genelab")` — logs the diagram to the session.
2. `create_chat_transcript(...)` — emits markdown with a **Schema
   visualizations** section.
3. Extract the ` ```mermaid ` block **from the transcript markdown** (not from
   the tool output) and render it with `mermaid-cli`.

![spoke-genelab schema rendered from the transcript](spoke-genelab-from-transcript.png)

## Reproduce

```python
import asyncio
from mcp_okn import schema

m = asyncio.run(schema.visualize_schema("spoke-genelab"))["mermaid"]
open("spoke-genelab.mermaid", "w").write(m)  # then render with mermaid-cli (above)
```

End-to-end transcript round-trip:

```python
import asyncio, re
from mcp_okn import server, session
import mcp_okn.schema as sch

async def main():
    session.reset()
    r = await sch.visualize_schema("spoke-genelab")
    session.record_visualization("spoke-genelab", r["mermaid"])
    md = await server.create_chat_transcript(model="claude-opus-4-8")
    block = re.search(r"```mermaid\n(.*?)\n```", md, re.S).group(1)
    open("from_transcript.mermaid", "w").write(block)  # render with mermaid-cli

asyncio.run(main())
```

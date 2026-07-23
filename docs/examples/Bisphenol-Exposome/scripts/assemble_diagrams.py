#!/usr/bin/env python3
"""Build diagrams.json for readd_query_diagrams.py: pair each verbatim logged query
(data/qN.rq) with its `sparql_to_mermaid` diagram.

Each diagram is rendered from the query EXACTLY as logged, using the `sparql-to-mermaid`
library — the same renderer behind the mcp-okn `sparql_to_mermaid` TOOL, so the output
matches (GRAPH clauses become `subgraph ["GRAPH …"]` boxes, VALUES lists collapse to the
first few + `+N more`, OPTIONAL/FILTER get their own shapes). Run this in an mcp-okn dev
checkout where the package is importable; in a report session where it is NOT, call the
`sparql_to_mermaid` TOOL on each verbatim query instead and assemble diagrams.json by hand.

    python scripts/assemble_diagrams.py        # writes diagrams.json beside the study
"""
import glob
import json
import os
import re

from sparql_to_mermaid import try_to_mermaid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rq_files = sorted(
    glob.glob(os.path.join(ROOT, "data", "q*.rq")),
    key=lambda p: int(re.search(r"q(\d+)\.rq$", p).group(1)),
)

out = []
for path in rq_files:
    sparql = open(path).read().strip()
    mermaid = try_to_mermaid(sparql)
    if not mermaid:
        raise SystemExit(f"{os.path.basename(path)}: sparql_to_mermaid returned no diagram")
    out.append({"sparql": sparql, "mermaid": mermaid})

json.dump(out, open(os.path.join(ROOT, "diagrams.json"), "w"), indent=1)
print(f"wrote diagrams.json with {len(out)} pairs")

# Proto-OKN crosswalk network — session transcript

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `hydrologykg` — <https://purl.org/okn/frink/kg/hydrologykg>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `ufokn` — <https://purl.org/okn/frink/kg/ufokn>
- `sockg` — <https://purl.org/okn/frink/kg/sockg>
- `geoconnex` — <https://purl.org/okn/frink/kg/geoconnex>
- `scales` — <https://purl.org/okn/frink/kg/scales>
- `nikg` — <https://purl.org/okn/frink/kg/nikg>
- `wildlifekn` — <https://purl.org/okn/frink/kg/wildlifekn>
- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `nde` — <https://purl.org/okn/frink/kg/nde>
- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `ncipidkg` — <https://purl.org/okn/frink/kg/ncipidkg>
- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice>
- `biobricks-tox21` — <https://purl.org/okn/frink/kg/biobricks-tox21>
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast>
- `biobricks-mesh` — <https://purl.org/okn/frink/kg/biobricks-mesh>
- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>

## Conversation

👤 **User**

Create an interactive network diagram of the crosswalks. Include bridging KGs (ubergraph, wikidata) as nodes. The width of edge should be proportional to the log of the number of verified counts.

---

🧠 **Assistant**

This is a verified join table — 92 crosswalks across 32 knowledge graphs, with `ubergraph` and `wikidata` acting as bridge hubs. Here's the network. Edge color encodes the data domain, edge width is proportional to log of the verified join count (for the taxonomy edges, which carry no single `verified_count`, I use the largest of the exact-id / clade-membership counts). Hover any node or edge for details; drag to rearrange; scroll to zoom; click a graph to pull its full set of join recipes.

[interactive force-directed network diagram: 32 KG nodes, edges colored by domain (Chemicals, Disease & phenotype, Genes, Geospatial, Industry & supply chain, Proteins, Taxonomy), edge width proportional to log10 of the verified count, ubergraph and wikidata rendered as enlarged bridge hubs]

A few things the layout makes visible:

`spatialkg` is the dominant geospatial hub — the thickest edge in the whole graph is `fiokg ↔ spatialkg` (681,045 shared S2 cells), and nearly every geospatial KG joins through it on `S2_L13` or `county_FIPS`. `spoke-okn` is the overall connector, tying together chemicals, disease, genes and geospatial.

The two bridge nodes behave differently. `ubergraph` is a true ontology backbone — it brokers the disease crosswalks (DOID↔MONDO, EFO↔MONDO), the CHEBI↔CAS chemical joins, and all 14 NCBITaxon overlaps. `wikidata` bridges exactly one crosswalk: `prokn → spoke-okn` via HGNC→Entrez (16,298 genes).

One caveat on the taxonomy edges: those rows don't carry a single verified count, so their width uses the larger of the exact-id and clade-membership numbers. That's why `nde ↔ ubergraph ↔ spoke-okn` looks heavy — it's 23 exact taxon matches but 33,601 by clade once expanded through `subClassOf*`.

If you'd like, I can recolor nodes by their home domain instead of edges, collapse the bridge segments so bridged pairs show as a single dashed edge, or export this as a standalone HTML file.

👤 **User**

Create a chat transcript. Render the image as .png.

---

🧠 **Assistant**

Generated this transcript of the session and rendered the crosswalk network to a static PNG, preserving the same visual encoding: nodes are the 32 knowledge graphs (ubergraph and wikidata enlarged as bridge hubs), edge color encodes the data domain, and edge width is proportional to log10 of the verified join count. Source data: the curated cross-KG join table (92 crosswalks, verified 2026-06-12).

![Crosswalk network](crosswalk-network.png)

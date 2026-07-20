# Mechanistic map (anchor → module → gene → drug)

When the question is **"map the biology of X"** — a disease, a gene, a chemical — the payoff figure is
a **mechanistic map**: a radial network that places the entities you *retrieved from the federation*
around the anchor so a reader sees the mechanism at a glance. It is the synthesis view that ties the
analysis together; the T2D example (`docs/examples/Diabetes3`, report §7, fig8) is the model.

Build it with **`scripts/mechanistic_map.py`** (`render_mechanistic_map(...)`, or a JSON spec) — don't
hand-write the layout each time. `python scripts/mechanistic_map.py --demo` renders the T2D example.

## When it fits (and when it doesn't)

- **Fits:** the analysis produced a **tiered gene/protein core** (menu step 12) that falls into a few
  **mechanistic themes** (from enrichment, step 6, or curated pathway membership), and you have a
  **drug/target layer** (step 10) tying agents to those themes. Disease-anchored is the common case,
  but the anchor can be any entity (a gene's interactors, a chemical's targets).
- **Doesn't fit:** a purely geospatial result (use the OpenStreetMap map instead — see
  [[geolocation-use-real-map]] / the report-style figure checklist), a single flat ranked list with no
  module structure, or an analysis with no drug/pathway layer. Don't force a map onto a table.

## Structure — four layers, four shapes

A radial layout, anchor at the centre. **Shape carries the entity kind** (so the map survives
greyscale and colour-vision deficiency; colour is redundant, never the sole cue):

| Layer | Shape | What it is | Comes from |
|---|---|---|---|
| **Anchor** | ★ star | the disease / gene / chemical the map is about | menu step 1 |
| **Module** | ■ square | a mechanistic theme / pathway (β-cell K-ATP, insulin resistance, …) | enrichment (step 6) or curated pathway grouping |
| **Gene** | ● circle | a member gene/protein of that module | the tiered core (step 12), placed by pathway membership |
| **Drug** | ▲ triangle | an agent that acts on that module | drug/target linkage (step 10) |

Modules ring the anchor; each module's genes fan outward from it; drugs sit beyond the genes on the
module they act on. `render_mechanistic_map` distributes any number of modules evenly and fans genes
adaptively, so you only supply `modules={label: [genes]}` and `drugs={label: [drugs]}`.

## Honesty rules (the whole point — a pretty map that overstates evidence is worse than a table)

1. **Every node is an entity you actually retrieved.** Never add a gene/drug to round out a module —
   if a canonical member wasn't returned by any source, it isn't on the map (or is drawn distinctly
   and named in the caption as context-only, like the T2D `Semaglutide*` GLP-1 placeholder).
2. **The modules are a synthesis, so say so.** Grouping the core into themes is analyst judgment on
   top of the enrichment/curation. State the grouping basis in the caption ("modules = significant
   Reactome/GO themes at FDR<0.05" or "curated pathway membership"), so a reader knows the squares are
   interpretation, not a query result.
3. **Prefer the tiered core for the gene layer.** Draw the multiply-corroborated genes (Tier 1/2,
   step 12), not the long single-source tail — the map is a high-confidence backbone, not the full
   list. Note the tier cut in the caption.
4. **Label the drug evidence layer honestly** (step 10): approved therapeutic > investigational >
   med-chem probe > toxicogenomic perturbation. Only draw a drug a KG edge ties to a gene/target in
   that module — a `drug` payload (DrugBank therapeutic) and a `chemical` payload (tox/probe substance)
   are different rungs; don't blur them. The legend names the supplier (e.g. "Drug — prokn indication").
5. **Carry the standing caveats** — observational-not-causal for association edges, species/ortholog
   for model-organism sources — into the caption, exactly as elsewhere in the report.

## Presentation

- Follow the report-style **figure checklist**: interpretive legend/caption *below* the figure in the
  report text (not baked into the PNG); acronyms defined; provenance (which KGs supplied genes,
  pathways, drugs) stated; then a 1–3 sentence interpretation of what the map shows.
- `Read` the rendered PNG back and check it: no label collisions in a crowded module, every shape in
  the legend, drugs attached to the right module. Re-render if a fan is too tight (trim the module to
  its top members, or split one overloaded module into two themes).
- Embed the PNG in the Markdown report and the HTML (via the report-style build), numbered in document
  order like any other figure.

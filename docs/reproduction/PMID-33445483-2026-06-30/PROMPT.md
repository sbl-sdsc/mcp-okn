# Originating prompt

This reproduction was produced in response to the prompt below (reproduced verbatim), using the `mcp-okn` MCP service against the FRINK federated SPARQL endpoint. Model: `claude-opus-4-8`. Date: 2026‑06‑30.

---

## Task prompt

> Reproduce the main results from this paper:
> Nelson, C.A., Acuna, A.U., Paul, A.M., Scott, R.T., Butte, A.J., Cekanaviciute, E, Baranzini, S.E., and Costes, S.V., (2021). Knowledge Network Embedding of Transcriptomic Data from Spaceflown Mice Uncovers Signs and Symptoms Associated with Terrestrial Diseases, Life. doi.org/10.3390/life11010042
>
> Use data from spoke-genelab together with other relevant OKN KGs that can add biological context, such as pathways, GO terms, gene sets, diseases, phenotypes, chemicals, or other functional annotations.
>
> 1. Identify the main biological question and the key results reported in the paper.
> 2. Determine which OSDR/GeneLab dataset IDs are used in the publication.
> 3. Match the relevant dataset ID(s) to the corresponding study, assay, samples, genes, or differential-expression results in spoke-genelab.
> 4. Use the MCP service to query spoke-genelab and any additional KGs needed to reproduce or approximate the publication's main findings.
> 5. Where useful, include cross-graph queries that connect GeneLab results to additional biological context, such as:
>    * pathways
>    * GO terms
>    * gene sets
>    * diseases or phenotypes
>    * orthologs
>    * chemicals or perturbations
>    * literature or external identifiers
> 6. Examine the publication's tables, figures, and plots. Identify any results that can be recreated from the data available through the MCP service.
> 7. Recreate, where possible, comparable tables or plots using data retrieved from spoke-genelab and the connected KGs.
> 8. Compare the recreated results with the original publication. The final output should include:
>
> * The selected publication, including title, citation, and URL.
> * The dataset ID(s) used and how they map to spoke-genelab.
> * The MCP tools and KGs used.
> * The cross-graph query strategy.
> * Example natural-language prompts and, where applicable, the generated SPARQL/Cypher queries.
> * Recreated tables or plots, if possible.
> * A comparison between the reproduced results and the publication's reported results.
> * A clear summary of:
>    * what could be reproduced,
>    * what could only be approximated,
>    * what could not be reproduced,
>    * and what data, schema, or crosswalk limitations caused any differences. The example should be realistic and suitable for demonstrating the value of cross-graph querying with spoke-genelab in a scientific use case.

---

## Follow‑up refinements

The deliverable was then iteratively refined through these follow‑up requests:

1. **Directly recreate the Fig 3d GO gene‑set overlap** — add the `prokn` GO‑term cross‑graph query (worked out the four‑graph `spoke-genelab → wikidata → prokn` bridge; 245 shared GO biological processes; §8).
2. **Create a PDF version with the figures embedded inline** — `spoke-genelab-nelson2021-reproduction.pdf` (`make_pdf.py`).
3. **Replace the ASCII diagrams** with rendered figures — `fig0_crossgraph_strategy.png` (§5) and `fig_go_bridge.png` (§8), via `make_diagrams.py`.
4. **Organize and version the deliverable** — moved into `docs/reproduction/PMID-33445483-2026-06-30/` and committed.

See `README.md` for the full write‑up and `spoke-genelab-nelson2021-reproduction.pdf` for the rendered report.

# Common failure modes (bio-analysis)

Recurring mistakes in cross-KG biomedical analyses, each with its fix. Skim before finalising an
analysis — every one is the inverse of an Operating rule or Analysis-menu step in `SKILL.md`.

- **Joining across KGs on study / dataset accessions** (e.g. OSD / GLDS — a federation island) →
  integrate on shared entity IDs (gene, protein, disease, phenotype, chemical, taxon) or geography.
- **Enrichment against an implicit / all-genome background** → inflated significance. Use an explicit
  background: all entities annotated in the target KG, in the right id scheme.
- **GO enrichment done, Reactome silently skipped** (or half of any compound deliverable) → they are
  separate families; run both, and declare in the report which you RAN vs deliberately SKIPPED, each
  with a one-line reason. A missing analysis has no loud tripwire (unlike an absurd result), so the
  omission must be made explicit.
- **Using only the KGs with prominent write-ups here and missing one named in a parenthetical** (e.g.
  `digcfdekg`) → that is pattern-matching on this doc's layout, not reading the capability index.
  Reconcile against what `find_context_sources` RETURNS: list every supplier per `want`, use-or-drop
  each with a reason.
- **Reaching place-based data by name instead of a geographic key** → join on FIPS / ZIP / S2 (find
  the bridge KG with `find_context_sources` / `get_join_strategy`), never on a place name.
- **A single combined query pushing a big reified pattern + OPTIONAL joins** → timeout; go one piece
  at a time, and never use a global `ORDER BY` (rank client-side).
- **Exact-id taxon match taken as the real overlap** → coarse genus vs fine strain badly understates
  it; clade-expand with ubergraph `rdfs:subClassOf*` (see Analysis-menu step 8).
- **Hard-coding a bridge id** read off an exploratory lookup (e.g. a MONDO IRI pasted as a constant) →
  establish the join by RUNNING the `skeleton_query` so the bridge is in the logged transcript.

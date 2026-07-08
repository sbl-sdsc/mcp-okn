# Data files — Bone Health Spaceflight-Omics Study

Primary extracts (spoke-genelab v0.0.2, OKN federation):
- `wt_full_raw.json` / `ko_full_raw.json` — OSD-690 bone-marrow Space-Flight-vs-Ground significant DE (adj_p<=0.05), WT and Nrf2-KO arms, projected to human orthologs. Columns: mEntrez, symbol, hEntrez, humanSymbol, log2fc (>0 = up in flight), adj_p_value.

Processed tables:
- `RANKED_bone_candidates.tsv` — 953 ranked bone candidates (the deliverable table).
- `all_genes_scored.tsv` — every scored gene.
- `wt_human_annotated.tsv` / `ko_human_annotated.tsv` — human-ortholog signatures with bone annotations.
- `wt_ko_human_merged.tsv` — WT vs Nrf2-KO merged (robust-core / Nrf2-dependence).
- `wt_he_specificity.tsv` — per-gene cross-tissue recurrence (systemic vs marrow-selective).
- `digcfde_gene_bonecats.tsv` — digcfdekg bone-loss trait categories per gene.
- `stats.json` — summary statistics used by the report and figures.

See ../bone_reproducibility_appendix.md and ../bone_reproducibility_transcript.md for rules, joins, and all 29 SPARQL queries.

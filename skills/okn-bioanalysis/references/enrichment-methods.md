# Enrichment & over-representation methods

How to test whether an entity set (usually genes, but also proteins or chemicals) is enriched for a
category — a GO term, Reactome pathway, disease / trait / phenotype gene-set, or a chemical /
adverse-outcome target set — correctly and interpretably. Use `scripts/enrichment.py` to compute it.

## The test

Hypergeometric (one-sided, over-representation) per category, then Benjamini–Hochberg FDR across
all categories tested:

- **N** = background: the universe of genes that *could* be drawn. Use an **explicit** set — e.g.
  all human genes annotated in the target KG (restricted to real Entrez ids), or all
  ortholog-mapped genes in your analysis space. Never an implicit "all genes in the genome" unless
  that is genuinely the sampling frame.
- **K** = genes in the category ∩ background.
- **n** = signature genes ∩ background (only signature genes that *could* be annotated count).
- **k** = signature genes ∩ category ∩ background (the observed overlap).
- p = `hypergeom.sf(k-1, N, K, n)`; **fold = k / (n·K/N)** (observed / expected).
- Report **k/K, expected, fold, p, and FDR** for every category; keep only FDR < 0.05.

## Backgrounds (the part people get wrong)

The background must match the KG you drew the category from. Examples:
- prokn GO: N = distinct prokn GO-annotated genes; n = signature genes that map to a prokn gene.
- digcfdekg trait: N = distinct genes with any `geneToTrait` (numeric Entrez only — strip malformed
  node ids); n = signature ∩ that set.
- biobricks tox / aopwiki: N = distinct chemicals (or target genes) assayed in that KG; n = your set
  ∩ that universe.
Re-verify N by removing malformed / wrong-scheme ids from an auto-saved id dump before using it.

## Disease / trait / phenotype gene-set enrichment

Same hypergeometric test, but each **category is a disease (or trait / phenotype) and its associated
gene set** — the question is "which diseases' gene sets are over-represented in my signature?". A few
disease-specific rules:

- **Get the disease→gene edge from the tools, don't hard-code it.** The predicate and id scheme differ
  by KG, so ask `find_context_sources(want=["disease"], join_key="gene")` (or `get_join_strategy` /
  `list_crosswalks`) for the actual edge + IRI normalization. Disease→gene sets come from
  **pankgraph / spoke-okn / prokn / rdkg**; gene→trait from **digcfdekg** (`geneToTrait`).
- **MONDO is the pivot; expand subtypes.** Build each disease's gene set over its subtype closure —
  join through ubergraph `rdfs:subClassOf*` so a parent disease ("any asthma", "all cardiovascular
  disease") includes its subtypes' genes; DOID / EFO / OMIM / Orphanet / UMLS all bridge to MONDO via
  ubergraph. Skip this and a parent-term category is artificially small, understating enrichment.
- **Background** N = distinct genes with ANY disease / trait association in the chosen KG (numeric
  Entrez only — strip malformed node ids, exactly as for the digcfdekg trait example above); n =
  signature ∩ that set.
- **Interpretation.** Common, polygenic diseases have **broad** gene sets → they look null for the
  same reason a GWAS / PIGEAN set does (see *Interpretation* below); **rare / Mendelian** disease sets
  (e.g. rdkg) are the discriminating test. Disease enrichment is **associational, not causal** — carry
  that caveat to every downstream claim.

## Interpretation (report both, and be honest)

- A **broad, permissive** category (e.g. a GWAS/PIGEAN gene-set covering ~15–20% of the genome) will
  look **null even for a real signal** — any large gene list overlaps it near the chance rate. A
  null here reflects the set's size, not absence of biology. Report it, but don't over-read it.
- A **small, curated (Mendelian / high-penetrance)** category is the discriminating test. Enrichment
  there means the signature concentrates in causal genes, not the diffuse background.
- Enrichment is **descriptive, not causal.** With small k the estimate is noisy. State the caveats;
  carry the appropriate caveat to every downstream claim (species / ortholog-inferred for
  model-organism data; observational-not-causal for association / GWAS data).

## Practical

- Pull `(gene, category)` pairs from the KG as raw rows (no GROUP BY, no ORDER BY — see the workflow
  reference), aggregate to `category -> set(genes)` in pandas, then call the enricher.
- For GO, separate biological-process / molecular-function / cellular-component (different predicates
  in prokn); enrich BP for "what programs", CC for localisation.
- Theme the significant terms (translation, OXPHOS, immune, proteostasis, …) for the figure; rank
  the figure by significance (−log10 FDR), annotate bars with fold and (k/K).

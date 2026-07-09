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

# Target-paper literature comparison

The originating request concerned Beheshti et al. (2019) [1]. PubMed identified PMID 31844325 and DOI 10.1038/s41598-019-55869-2. Paperclip supplied the full-text passages and supplementary table. This is a targeted comparison with the requested paper; no claim of a comprehensive subsequent-literature search is made. Line numbers below refer to Paperclip's `/papers/PMC6915713/content.lines`.

## Claim 1: The retained STS-135 signature recovers fatty-acid oxidation themes

**Concordance: PARTIALLY SUPPORTED.** Supplementary Table 1 reports fatty acid beta oxidation with size 43, NES 2.24 and displayed FDR 0.0000 (line 247); fatty acid metabolic process has size 237, NES 1.92 and FDR 0.0062 (line 413) [1]. Displayed 0.0000 is rounded, not a literal zero probability. The new GO over-representation analysis uses human-ortholog annotations and thresholded gene lists, so its fold enrichment and FDR must not be numerically equated with NES and GSEA q-values. The positive thematic result against the annotation universe disappears after BH adjustment under the retained-only background. This is limited concordance, not exact reproduction.

## Claim 2: Lipid dysregulation is reproduced across all flight missions

**Concordance: UNRESOLVED.** Results lines 31–34 describe shared lipid/fatty-acid pathways across the paper's cohorts [1]. The current graph signatures for OSD-47 and OSD-137 are much smaller than the paper's stated significant-gene lists. OSD-168 comparisons fail the supplied metadata-matching rule. These constraints do not permit confirmation or falsification of the paper's broad cross-mission conclusion. No pooled causal or strain-independent estimate was calculated.

## Claim 3: Human fatty-liver associations support a lipid-related hypothesis

**Concordance: PARTIALLY SUPPORTED.** The paper's discussion (lines 45–50) links lipid-pathway perturbation to possible NAFLD-related mechanisms and future risks [1]. The new digcfdekg test adds a specific human gene–trait annotation result to that framing; it is not an independent animal experiment and cannot validate liver disease. The reported enrichment is descriptive, survives the retained-background comparison for STS-135, and does not show the sign of any human disease effect.

## Claim 4: Insulin activation and glucagon inhibition are reproduced

**Concordance: UNRESOLVED.** Figure 3B and the associated text (lines 33–34), together with Methods line 67, attribute these results to IPA upstream-regulator activation z-scores [1]. The KG query retrieves differential-expression summaries. Absence of Gcg/Ins1/Ins2 from the retained extract cannot establish their absence of expression or activity. A Ppara transcript effect is likewise not an IPA PPARα score. No substitute regulator activation score was invented.

## Claim 5: ORO was significant in every cohort and increased significantly with duration

**Concordance: CONTRADICTED.** The Results prose at line 24 explicitly states that RR3 flight versus ground was not significant and that the 21-versus-37-day comparison had p=0.07 [1]. Figure 1's caption uses stronger wording, and the broader discussion interprets a consistent lipid response. The article also reports a significant overall flight factor and interaction in an ANOVA (line 25); that does not make every pairwise contrast significant. This discrepancy comes from the paper itself, not a failed KG reconstruction of histology.

## Claim 6: Supplementary Table 1 establishes significant STS-135 circadian-rhythm enrichment

**Concordance: CONTRADICTED.** The table's circadian rhythm row has NES 1.26 and FDR 0.3056 (line 1672), and regulation of circadian rhythm has FDR 0.3170 (line 1714) [1]. Neither passes 0.05. This conflicts with interpreting broad narrative claims of common circadian upregulation as statistically significant STS-135 enrichment at that threshold. It does not rule out other circadian gene sets, different analyses or clock-related biological effects.

## Accession and method reconciliation

Methods line 53 identifies GLDS-25 as STS-135, GLDS-47 as RR1-CASIS, GLDS-137 as RR3 and GLDS-168 as RR1-NASA [1]. Results line 27 and RNA-seq Methods line 64 describe the NASA/ISS accessions less consistently. The report therefore states which Methods mapping was used and avoids asserting identical processing of every overlapping cohort. Methods lines 63–67 specify the three-group STS-135 ANOVA, differing nominal/adjusted significance thresholds, GSEA, and a 1.2-fold threshold for pathway/regulator work. These differences explain why the KG reanalysis is deliberately called partial.

## References

Retrieved via the **PubMed** MCP connector. Full-text verification via the **Paperclip** MCP connector.

1. Beheshti A, et al. Multi-omics analysis of multiple missions to space reveal a theme of lipid dysregulation in mouse liver. *Scientific Reports*. 2019. PMID:31844325 · [doi:10.1038/s41598-019-55869-2](https://doi.org/10.1038/s41598-019-55869-2) — full-text-verified ([PMC6915713](https://pmc.ncbi.nlm.nih.gov/articles/PMC6915713/)).

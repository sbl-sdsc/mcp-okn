# Literature comparison — per-claim record

Companion to `Liver-Lipid_report.md` §8. Ten claims from the knowledge-graph reproduction of
Beheshti et al. 2019, each checked against the primary literature retrieved through the **PubMed**
and **Paperclip** MCP connectors. Concordance is one of the closed six: SUPPORTED / PARTIALLY
SUPPORTED / CONTRADICTED / MIXED / NOVEL / UNRESOLVED.

This is a *comparison*, not a validation. NOVEL is a finding, and the check runs both ways: it can
expose an error in the graphs as readily as it corroborates a claim. Every DOI below was taken from
the NCBI record returned by the PubMed connector; the links could not be resolution-tested because
this session's network policy blocks outbound HTTP to `doi.org`.

---

## Claim 1 — Spaceflight up-regulates lipid metabolic and lipid catabolic processes in mouse liver

**Concordance: SUPPORTED.** The original states that transcriptomic analysis "revealed several
pathways that were affected in both strains related to increased lipid metabolism, fatty acid
metabolism, lipid and fatty acid processing, lipid catabolic processing, and lipid localization"
[1]. This reproduction recovers *lipid catabolic process* as the single most enriched GO biological
process (7.08×, k = 4/20, FDR = 0.027) with *lipid metabolic process* (2.15×) and *fatty acid
metabolic process* (2.78×) following, from a signature and background built independently of the
original's pathway tooling. Independent Shuttle-mission work reaches the same conclusion by
different instruments: Jonscher et al. show hepatic lipid droplet accumulation and elevated
triglycerides after STS-135 [2], and Blaber et al. find glycerophospholipid and sphingolipid
pathway changes in the same tissue [3]. A liver-and-muscle crosstalk analysis of RR-1 concludes
that "lipid metabolism is the most affected biological process between the two organs" [8].

*Caveat:* the reproduction's lipid signal is carried almost entirely by GLDS-25 (STS-135), so it
does not independently confirm the original's specific claim that the effect is present *without*
the live-return confound.

## Claim 2 — The lipid response implicates PPAR signalling and hepatic steatosis

**Concordance: SUPPORTED.** Jonscher et al. link flight-induced hepatic lipid accumulation and
retinol loss from stellate-cell lipid droplets to activation of PPARα-mediated pathways, and warn
that longer exposure may increase NAFLD risk [2]. The original extends this, reporting PPARα-mediated
pathways activated in its proteomic data and predicted down in its transcriptomic data [1]. Here the
only Reactome pathway to survive FDR correction alongside interleukin signalling is *MLL4 and MLL3
complexes regulate expression of PPARG target genes in adipogenesis and hepatic steatosis* (4.48×,
k = 3/24, FDR = 0.027; *PEX11A, PNPLA2, TBL1XR1*), and the canonical PPARα target classes —
peroxisomal biogenesis (*PEX3, PEX11A, PEX19*) and acyl-CoA thioesterases (*ACOT1, ACOT2*) — are
coordinately up in flight. *Ppara* and *Pparg* themselves are significantly changed in GLDS-25
(log2FC +0.67, adj-p 3.7e-5; +0.84, adj-p 0.014) but fall below the |log2FC| ≥ 1 selection cut.

*Caveat:* the Reactome term names PPARG, not PPARα; the two receptors share many target genes and
the pathway label is not evidence for a specific isoform.

## Claim 3 — Flight-responsive liver genes are over-represented for NAFLD/liver-disease genes

**Concordance: PARTIALLY SUPPORTED.** The original argues at length that its results are "consistent
with NAFLD" and proposes that spaceflight drives NAFLD pathogenesis, but the argument rests on
pathway membership and IPA prediction, not on a gene-set enrichment test against a disease gene
set [1]. The quantitative test here is therefore new: 15 of 124 core genes fall in the curated
rdkg MONDO liver-disease set against 7.51 expected (2.0×, p = 0.0074), and 10 of 124 fall in the
EFO *non-alcoholic fatty liver disease* set in digcfdekg (3.54×, k = 10/105, p = 4.6e-4, FDR =
0.0074). The direction agrees with independent work reporting flight-induced hepatic steatosis and
insulin resistance in mice [4].

*Caveat:* against a deliberately coarse third set — spoke-okn's undifferentiated 1,289-gene
`DOID:409` bucket — the same core shows no enrichment (0.87×, p = 0.72). The result is a property
of specific, curated sets, not of any liver-labelled gene list.

## Claim 4 — *PNPLA3* is a flight-responsive liver gene and the top-ranked candidate

**Concordance: NOVEL.** No source found. *PNPLA3* is not named anywhere in the original [1], and a
corpus-wide full-text boolean search for `"PNPLA3" AND ("spaceflight" OR "microgravity")` returns
only incidental co-occurrence — reference lists, unrelated pathway member lists, and one
spaceflight *muscle* gene-metabolite network in which *PNPLA3* appears as an ordinary member of a
retinol-biosynthesis set [5]. Here *Pnpla3* is down in flight in GLDS-25 (log2FC −1.15, adj-p
0.032), carries corroboration from five graphs, and is the only gene in the core to complete a
gene → disease → phenotype path to *Hepatic steatosis* (HP:0001397), via NAFLD1 (MONDO:0021105) in
rdkg. Its status as the strongest common human genetic risk factor for fatty liver disease is
independently well established but was reached here through the knowledge graph, not from the
spaceflight literature.

## Claim 5 — *DEPP1* is the only gene recurring across two independent vetted flight assays

**Concordance: NOVEL.** No source found reporting *DEPP1* (mouse *Depp1*, human C10ORF10) in
spaceflight liver transcriptomics. It is down in flight in both GLDS-25 (log2FC −1.73, adj-p
2.8e-4) and GLDS-47 (log2FC −1.02, adj-p 5.8e-3) — the only such gene in this reproduction. Its
identity as a FOXO3 transcriptional target that localises to peroxisomes and mitochondria, drives
ROS accumulation and is required for autophagy induction under starvation and genotoxic stress is
established separately [6], which makes its coordinate suppression in two flight livers a specific
and testable observation rather than a coincidence of two sparse gene lists.

*Caveat:* with only 68 and 4 genes stored for GLDS-47 and GLDS-137, the intersection available for
replication is tiny; "the only recurrent gene" is a statement about payload depth as much as about
biology.

## Claim 6 — Apolipoproteins are dysregulated in flight liver

**Concordance: MIXED.** The original reports the apolipoproteins ApoC1, ApoA2 and ApoA5 **down** in
flight at the protein level in RR-3, and interprets their inhibition as increasing NAFLD risk [1].
The transcriptomic slice available here disagrees in part and is silent for the rest: *APOA4* is
**up** (log2FC +1.20, adj-p 2.4e-5) in GLDS-25, *Apoa5* is present but unchanged (log2FC +0.19,
adj-p 0.063), and *Apoa2* and *Apoc1* have no stored liver DE record at all. Transcript and protein
abundance need not agree, and the two measurements come from different datasets (RR-3 proteomics
versus STS-135 microarray), so this is a divergence of instrument and dataset rather than a
contradiction of the original's measurement.

## Claim 7 — Circadian-clock pathways are up-regulated in flight liver

**Concordance: UNRESOLVED.** The original reports circadian clock pathways commonly up-regulated
across STS-135, RR-1 and RR-3 by GSEA, and builds a substantial argument on it — linking circadian
disruption in microgravity to liver hyperplasia and NAFLD progression [1]. Circadian disruption is
independently recognised as a spaceflight stressor [4]. The over-representation analysis used here
cannot adjudicate the claim: circadian terms are present and testable in the background (15 GO
terms over 41 annotated genes; 6 Reactome pathways over 15 genes), but at the original's permissive
threshold they sit at fold 1.06–1.08 with FDR ≈ 1, and at the strict threshold only *ADORA1*
(GO) and *TBL1XR1* (Reactome) fall on any of them. Directionally, the two core clock genes with
stored records move oppositely — *Per2* down (log2FC −0.96, adj-p 2.5e-4), *Dbp* up (+0.68,
adj-p 0.031) — and *Clock*, *Arntl*, *Nr1d1*, *Per1* and *Cry2* have no record.

## Claim 8 — GCG and INS are commonly regulated upstream regulators of the flight liver response

**Concordance: UNRESOLVED.** The original's finding — glucagon commonly down and insulin commonly
up across all datasets — is derived from Ingenuity Pathway Analysis activation-score statistics on
predicted upstream regulators, a proprietary method with no counterpart in the federation [1].
Independent work does report flight-induced inhibition of hepatic insulin receptor signalling with
concomitant insulin resistance and steatosis in mice [4], which is consistent with the original's
direction. But neither *Gcg* nor *Ins1*/*Ins2* has any stored liver differential-expression record
in spoke-genelab, and predicted regulator activation is in any case not a measured transcript, so
the claim is untestable in this reproduction rather than unsupported by it.

## Claim 9 — GLDS-168's liver flight-vs-ground contrasts pool two missions and cannot be read as a clean spaceflight effect

**Concordance: NOVEL.** A knowledge-graph data-quality observation, with no prior source. All nine
of OSD-168's liver Space-Flight-vs-Ground-Control assays fail within-assay comparability: their
flight and ground arms are drawn from different missions (SpaceX-4 / RR-1 versus SpaceX-8 / RR-3)
and different library preparations (with versus without spike-in). This is consistent with the
original's own reporting, which gives separate DEG counts "for the RR1 and RR3 data from the
GLDS-168" and thereby acknowledges the dataset contains both missions [1], and with the study's
dual mission linkage in spoke-genelab. The observation describes how the dataset was packaged, not
an error introduced by graph construction.

## Claim 10 — Over-representation analysis at the original's FC ≥ 1.2 cut-off is uninformative

**Concordance: NOVEL.** A methodological observation about reusing the original's selection rule
with a different statistic. The original justifies FC ≥ 1.2 as standard practice, noting that low
cut-offs are "less affected by different data normalization schemes" and "less likely to eliminate
key genes operating under very tight level regulation" [1] — a reasonable choice for the rank-based
GSEA and IPA workflows it actually ran, neither of which forms a signature/background split.
Applied to over-representation here, that rule admits 3,216 human genes, 1,560 of which fall inside
the 2,160-gene annotated background — 72% of the testable universe — and every fold enrichment
collapses towards 1, with zero GO terms and zero Reactome pathways surviving FDR correction. No
prior source makes this observation about this dataset. Independent flight-liver analyses that used
rank-based or causal-inference methods rather than over-representation [3,7,8] are consistent with
the reading that the choice of statistic, not the data, is what changes here.

---

## References

1. Beheshti A, et al. Multi-omics analysis of multiple missions to space reveal a theme of lipid dysregulation in mouse liver. *Scientific Reports*. 2019. PMID:31844325 · [doi:10.1038/s41598-019-55869-2](https://doi.org/10.1038/s41598-019-55869-2) — full-text-verified ([PMC6915713](https://pmc.ncbi.nlm.nih.gov/articles/PMC6915713/))
2. Jonscher KR, et al. Spaceflight Activates Lipotoxic Pathways in Mouse Liver. *PLoS One*. 2016. PMID:27097220 · [doi:10.1371/journal.pone.0152877](https://doi.org/10.1371/journal.pone.0152877)
3. Blaber EA, Pecaut MJ, Jonscher KR. Spaceflight Activates Autophagy Programs and the Proteasome in Mouse Liver. *International Journal of Molecular Sciences*. 2017. PMID:28953266 · [doi:10.3390/ijms18102062](https://doi.org/10.3390/ijms18102062)
4. Mathyk BA, et al. Spaceflight induces changes in gene expression profiles linked to insulin and estrogen. *Communications Biology*. 2024. PMID:38862620 · [doi:10.1038/s42003-023-05213-2](https://doi.org/10.1038/s42003-023-05213-2)
5. Chakraborty N, et al. Gene-Metabolite Network Linked to Inhibited Bioenergetics in Association With Spaceflight-Induced Loss of Male Mouse Quadriceps Muscle. *Journal of Bone and Mineral Research*. 2020. PMID:32511780 · [doi:10.1002/jbmr.4102](https://doi.org/10.1002/jbmr.4102) — full-text-verified ([PMC7689867](https://pmc.ncbi.nlm.nih.gov/articles/PMC7689867/))
6. Salcher S, et al. C10ORF10/DEPP-mediated ROS accumulation is a critical modulator of FOXO3-induced autophagy. *Molecular Cancer*. 2017. PMID:28545464 · [doi:10.1186/s12943-017-0661-4](https://doi.org/10.1186/s12943-017-0661-4)
7. Casaletto JA, et al. Analyzing the relationship between gene expression and phenotype in space-flown mice using a causal inference machine learning ensemble. *Scientific Reports*. 2025. PMID:39824847 · [doi:10.1038/s41598-024-81394-y](https://doi.org/10.1038/s41598-024-81394-y)
8. Vitry G, et al. Muscle atrophy phenotype gene expression during spaceflight is linked to a metabolic crosstalk in both the liver and the muscle in mice. *iScience*. 2022. PMID:36267920 · [doi:10.1016/j.isci.2022.105213](https://doi.org/10.1016/j.isci.2022.105213)

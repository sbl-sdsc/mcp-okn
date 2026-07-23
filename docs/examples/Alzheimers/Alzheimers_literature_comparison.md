# Literature Comparison — Alzheimer's Disease Knowledge-Graph Analysis

Per-finding comparison of this analysis against the primary literature, retrieved via the **PubMed** MCP connector and the **Paperclip** full-text corpus. §8 of the report tabulates these findings and their concordance; this document is the supporting detail behind each row, in the same order. Verdicts: **SUPPORTED** / **PARTIALLY SUPPORTED** / **CONSISTENT WITH THE LITERATURE'S OWN STATE** / **NOVEL**.

---

## Finding 1 — Consensus gene core

**Verdict: SUPPORTED.**

The consensus core recovered across the knowledge graphs — APOE, APP, PSEN1/2, SORL1, ABCA7, ABCA1, ADAM10, CD2AP, CLU, CR1, PICALM, TREM2, BIN1, MS4A, EPHA1, CASS4, INPP5D — is essentially the canonical AD GWAS panel. Jansen *et al.* 2019 (29 loci, 215 genes) [1] and Bellenguez *et al.* 2022 (75 loci, 42 new) [2] recover essentially this panel from GWAS alone. The value here is reconstruction from independent graph sources, not novelty.

## Finding 2 — Dominant enriched processes

**Verdict: SUPPORTED.**

Microglia, lipid metabolism and APP degradation are the dominant enriched processes. Jansen *et al.* [1] report associated genes "strongly expressed in immune-related tissues and cell types (spleen, liver, and **microglia**)" and gene-set analyses implicating "**lipid-related processes and degradation of amyloid precursor proteins**" — the same three axes this study recovers at 15.4×, 15.5× and 30.7×. Bellenguez *et al.* [2] independently confirm "amyloid/tau pathways and highlighted **microglia** implication".

## Finding 3 — LUBAC / TNF-α arm

**Verdict: SUPPORTED — and non-obvious.**

The LUBAC / TNF-α arm (SHARPIN, RBCK1 in the Tier-A/B core, proteostasis module) is corroborated by Bellenguez *et al.* [2], who name "the tumor necrosis factor alpha pathway through the **linear ubiquitin chain assembly complex**" among their *new* genetically associated processes. Both LUBAC components surfaced here independently.

## Finding 4 — Notch as a γ-secretase off-target liability

**Verdict: SUPPORTED (verified against full text).**

Yang *et al.* 2008 quantified γ-secretase inhibitor selectivity between the two substrates, showing compounds differ in potency for "Aβ generation from APP than NICD generation from Notch" [3]; Hyde *et al.* 2013 characterised strategies "for managing Notch-related side effects" [4]; Yang *et al.* 2024 review secretases "simultaneously cleav[ing] Notch and APP" [5].

## Finding 5 — Neuroinflammatory prognostic panel

**Verdict: SUPPORTED.**

The neuroinflammatory prognostic panel (GFAP, YKL-40/CHI3L1, TSPO, TREM2, S100B, ICAM1, VCAM1, CCL2) is well grounded: plasma GFAP as a marker of astrocyte reactivity in AD is an active and well-populated literature (30 PubMed records for the narrow query used) [6].

## Finding 6 — SEMA4D and RBFOX-family involvement

**Verdict: PARTIALLY SUPPORTED / convergent.**

An all-cause-dementia GWAS meta-analysis reports novel loci including **SEMA4D** (energy transport) and **RBFOX1** (brain amyloid deposition) [7]. This study independently surfaces **SEMA4D** as the target of pepinemab in the AD drug layer and **RBFOX3** in the DE consensus — convergent evidence on the family rather than an exact locus match.

## Finding 7 — Contradictory evidence for HRT/oestrogen, NSAIDs, statins, vitamin E, ginkgo, metformin

**Verdict: CONSISTENT WITH THE LITERATURE'S OWN STATE.**

`biohealth` carries both asserted and negated edges for these interventions, reproducing the disagreement rather than resolving it. The trial and observational literature itself was **not checked against primary sources here**, so no citation is claimed for that characterisation.

## Finding 8 — `oard-kg` binding AD associations to the *familial type-1* MONDO term

**Verdict: NOVEL (data-quality finding).**

Not a biological claim; recorded here as an ontology mismatch that would silently zero out a naive parent-term query.

---

**Overall.** No finding in this study contradicts the cited literature. The genuinely new contributions are methodological and negative: the ontology mismatches (§5.2), the coverage gaps (§6.3, §6.5), and the machine-readable contradiction inventory (§6.7).

## References

1. Jansen IE, et al. Genome-wide meta-analysis identifies new loci and functional pathways influencing Alzheimer's disease risk. *Nat Genet*. 2019. PMID:30617256 · [doi:10.1038/s41588-018-0311-9](https://doi.org/10.1038/s41588-018-0311-9)
2. Bellenguez C, et al. New insights into the genetic etiology of Alzheimer's disease and related dementias. *Nat Genet*. 2022. PMID:35379992 · [doi:10.1038/s41588-022-01024-z](https://doi.org/10.1038/s41588-022-01024-z)
3. Yang T, et al. Quantification of gamma-secretase modulation differentiates inhibitor compound selectivity between two substrates Notch and amyloid precursor protein. *Mol Brain*. 2008. PMID:18983676 · [doi:10.1186/1756-6606-1-15](https://doi.org/10.1186/1756-6606-1-15) — full-text-verified ([PMC2637266](https://pmc.ncbi.nlm.nih.gov/articles/PMC2637266/))
4. Hyde LA, et al. In Vivo Characterization of a Novel γ-Secretase Inhibitor SCH 697466 in Rodents and Investigation of Strategies for Managing Notch-Related Side Effects. *Int J Alzheimers Dis*. 2013. PMID:23573456 · [doi:10.1155/2013/823528](https://doi.org/10.1155/2013/823528) — full-text-verified ([PMC3612465](https://pmc.ncbi.nlm.nih.gov/articles/PMC3612465/))
5. Yang KF, et al. Secretase promotes AD progression: simultaneously cleave Notch and APP. *Front Aging Neurosci*. 2024. PMID:39634655 · [doi:10.3389/fnagi.2024.1445470](https://doi.org/10.3389/fnagi.2024.1445470) — full-text-verified ([PMC11615878](https://pmc.ncbi.nlm.nih.gov/articles/PMC11615878/))
6. PubMed query "plasma glial fibrillary acidic protein astrocyte reactivity Alzheimer biomarker" (30 records, retrieved 2026-07-19) — cited as a body of evidence rather than a single paper.
7. Mega Vascular Cognitive Impairment and Dementia (MEGAVCID) consortium. A genome-wide association meta-analysis of all-cause and vascular dementia. *Alzheimers Dement*. 2024. PMID:39046104 · [doi:10.1002/alz.14115](https://doi.org/10.1002/alz.14115)

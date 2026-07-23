# Literature comparison — bisphenol chemical-exposome KG study

Central findings from the federated knowledge-graph analysis, checked against full-text literature
(Paperclip corpus: PMC + preprints). Each claim is labelled **Supported**, **Novel**, or
**Contradicted / nuanced**. This is a comparison, not a validation — a *Novel* label is a finding, and
the check exposes graph limitations as readily as it corroborates them.

> Connector note: the comparison was run over the **Paperclip** full-text corpus (PMC, bioRxiv,
> medRxiv). A dedicated PubMed connector was reported enabled but did not surface as a callable tool in
> this session; because Paperclip indexes the full text of PubMed Central papers, the central claims
> below are verified against primary full text rather than abstracts alone.

---

## 1. BPA analogues share BPA's endocrine-disrupting activity — **Supported**

KG result: 14–15 of the 15 assayed bisphenols are active on the estrogen receptor (ESR1/ESR2), androgen
receptor (AR), PGR and other nuclear receptors in the ICE/ToxCast screens; nuclear-receptor transcription
is the single most enriched Reactome pathway (fold ≈ 20, FDR 6.8×10⁻²³).

Rochester & Bolden's systematic review concludes that "BPS and BPF are as hormonally active as BPA, and
they have endocrine-disrupting effects" [1]. They report the mean *in vitro* estrogenic potency of BPF as
1.07 ± 1.20× BPA (range 0.10–4.83) and BPS as 0.32 ± 0.28× BPA, i.e. "in the same order of magnitude as
… BPA" [1]. Both compounds also show androgenic/antiandrogenic activity of the same order [1] — matching
the KG observation that bisphenols act as ER agonists **and** AR antagonists.

## 2. Several analogues equal or exceed BPA; substitution is "regrettable" — **Supported**

KG result: BPAF and TBBPA are the most promiscuous and potent compounds (127 and 105 human target genes;
AC50 down to 0.002 µM), each carrying 6 Tier-A chemical–disease links — more than BPA itself (1 Tier-A
link, 55 targets).

Srebny et al. compared BPA with 26 alternatives across six *in vitro* bioassays and found that "several
alternatives with close structural resemblance showed similar or stronger activation of the estrogen
receptor α (ERα) than BPA," concluding that "many BPA alternatives are regrettable substitutes" [2].
Thoene et al. likewise report that BPS "causes hormonal and obesogenic effects comparable to or worse
than bisphenol A" [3]. The KG-derived ranking that places the analogues **above** the parent compound is
therefore consistent with the experimental literature.

## 3. TBBPA → transthyretin/thyroid-hormone disruption → neurodevelopmental harm — **Supported**

KG result: the only AOP-Wiki adverse-outcome pathway curated for TBBPA (AOP 152) runs from the molecular
initiating event "Binding, Transthyretin (TTR) in serum" through decreased serum/neuronal thyroxine and
altered hippocampal biology to "Cognitive function, decreased."

Ren et al. show that TBBPA and its mono-ether analogues "bind to TTR and TRs, potentially disrupting the
thyroid hormone system" [4], directly corroborating the molecular initiating event and thyroid-axis key
events of AOP 152.

## 4. Convergence on nuclear-receptor / PPARγ / xenobiotic-metabolism programs — **Supported**

KG result: enriched Reactome/GO programs include Nuclear Receptor transcription, SUMOylation of
intracellular receptors, PPARA gene expression, "Transcriptional regulation of white adipocyte
differentiation," Xenobiotics, and steroid metabolism.

Srebny et al. specifically note that for some alternatives the loss of estrogenicity "was accompanied by a
shift toward peroxisome proliferator-activated receptor γ (PPARγ) activation" [2]; Longo et al. show BPA
"reduces Pparγ promoter methylation" in adipose precursors [5]. Both support the PPARγ/adipogenic arm of
the KG signature.

## 5. Target genes enrich for hormone-dependent cancers — **Supported**

KG result: rdkg disease-gene enrichment is significant for breast carcinoma (fold 4.4), prostate cancer
(3.9), endometrial and liver cancer; BPA→breast and BPA→prostate are Tier-A/B consensus links.

Gao et al. review BPA's role in "hormone-associated cancers," concluding BPA "mimics estrogen … contributing
to breast, ovarian, and prostate cancer development" [6]; Wang et al. argue low-dose BPA can instigate
breast-cancer initiation [7]. Supported.

## 6. Metabolic-disruptor / obesogen axis (obesity, NASH, T2D) — **Supported**

KG result: strongest disease-fold enrichments include non-alcoholic steatohepatitis (10×), obesity (7×) and
ischemia; PPARG is a top target (AC50 0.002 µM in 13 bisphenols).

Thoene et al. (obesogenic effects of BPS ≥ BPA) [3], Longo et al. (BPA→PPARγ epigenetics) [5] and Singh et
al. (bisphenol-F analogue is a potent obesogen, "increasing lipid accumulation more than BPA") [8] all
support a metabolic-disruptor interpretation.

## 7. Integrated cross-KG ranking of analogue hazard — **Novel (synthesis)**

The specific, reproducible result — that a *federated* evidence framework spanning tox screens (ICE/ToxCast),
adverse-outcome pathways (AOP-Wiki), curated disease genetics (rdkg) and pathway enrichment (prokn) ranks
**BPAF and TBBPA above BPA** on breadth of mechanistic disease support — is a synthesis not stated as such
in any single reviewed paper. It is consistent with the regrettable-substitution literature [1,2,3] but
extends it by quantifying cross-source consensus per chemical–disease pair. Treat as hypothesis-generating.

## 8. Apparent low activity of BPS in the curated screen — **Nuanced / graph limitation**

KG result: BPS (4,4'-sulfonyldiphenol) shows the fewest ICE active-target genes (10) of the core set. Taken
alone this could be misread as "BPS is safer."

The literature cautions against that reading: Rochester & Bolden give BPS an estrogenic potency of 0.32× BPA
(lower than BPF but still the same order of magnitude) with equivalent membrane-ER (nongenomic) potency to
estradiol in some assays [1], and Thoene et al. rate BPS obesogenic effects as "comparable to or worse than"
BPA [3]. The sparse BPS signal here reflects the **coverage of the curated ICE ER/AR assay set**, not an
absence of hazard — an important limitation of screen-derived breadth counts, carried into the report's
caveats.

---

## References

[1] Rochester JR, Bolden AL. "Bisphenol S and F: A Systematic Review and Comparison of the Hormonal Activity
of Bisphenol A Substitutes." *Environmental Health Perspectives* 123:643–650 (2015). doi:10.1289/ehp.1408989
https://citations.gxl.ai/papers/PMC4492270#L14,L36

[2] Srebny V, Henneberger L, König M, et al. "Beyond Estrogenicity: A Comparative Assessment of Bisphenol A
and Its Alternatives in In Vitro Assays Questions Safety of Replacements." *Environmental Science &
Technology* (2025). doi:10.1021/acs.est.5c07018 https://citations.gxl.ai/papers/PMC12392461#L6

[3] Thoene M, Dzika E, Gonkowski S, Wojtkiewicz J. "Bisphenol S in Food Causes Hormonal and Obesogenic
Effects Comparable to or Worse than Bisphenol A: A Literature Review." *Nutrients* 12:532 (2020).
doi:10.3390/nu12020532 https://citations.gxl.ai/papers/PMC7071457

[4] Ren X-M, Yao L, Xue Q, et al. "Binding and Activity of Tetrabromobisphenol A Mono-Ether Structural
Analogs to Thyroid Hormone Transport Proteins and Receptors." *Environmental Health Perspectives* (2020).
doi:10.1289/EHP6498 https://citations.gxl.ai/papers/PMC7584160

[5] Longo M, Zatterale F, Naderi J, et al. "Low-dose Bisphenol-A Promotes Epigenetic Changes at Pparγ
Promoter in Adipose Precursor Cells." *Nutrients* 12:3498 (2020). doi:10.3390/nu12113498
https://citations.gxl.ai/papers/PMC7696502

[6] Gao H, Yang B-J, Li N, et al. "Bisphenol A and Hormone-Associated Cancers: Current Progress and
Perspectives." *Medicine* 94:e211 (2015). doi:10.1097/MD.0000000000000211
https://citations.gxl.ai/papers/PMC4602822

[7] Wang Z, Liu H, Liu S. "Low-Dose Bisphenol A Exposure: A Seemingly Instigating Carcinogenic Effect on
Breast Cancer." *Advanced Science* 4:1600248 (2016). doi:10.1002/advs.201600248
https://citations.gxl.ai/papers/PMC5323866

[8] Singh M, Crosthwait J, Sorisky A, Atlas E. "Tetra methyl bisphenol F: another potential obesogen."
*International Journal of Obesity* (2024). doi:10.1038/s41366-024-01496-5
https://citations.gxl.ai/papers/PMC11216980

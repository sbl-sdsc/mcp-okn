# Spaceflight-Bone-Loss — literature comparison

Companion to `Spaceflight-Bone-Loss_report.md` §8. Each claim made by the cross-KG analysis was compared with the primary literature retrieved through the **PubMed** MCP connector (searches and NCBI metadata) and the **Paperclip** MCP connector (full-text corpus search). Abstracts were read for every cited paper; no claim was verified against full text in this run. Concordance labels: SUPPORTED · PARTIALLY SUPPORTED · CONTRADICTED · MIXED · NOVEL · UNRESOLVED.

## Claim 1 — Spaceflight suppresses osteoblast-lineage programmes in marrow progenitors

**KG finding.** ALPL is down in all three flight contrasts (marrow WT −1.09, marrow Nrf2-KO −1.14, osteogenic hMSC −1.02); GO-BP *osteoblast differentiation* (20/78 genes, 2.5×) and *positive regulation of osteoblast differentiation* are enriched in the hMSC signature. Several osteogenic genes (RUNX2 +2.17, COL1A1 +2.12, BMP4 +1.06) are, however, up in the flown hMSC.

**Concordance: PARTIALLY SUPPORTED.** Simulated microgravity inhibited osteogenic differentiation and favoured adipogenesis in human marrow MSCs [1], and lowered bone-development genes in hMSCs under osteogenic induction [2]. The lineage involvement agrees; the up-regulation of RUNX2 / COL1A1 in the flown cells does not fit a simple suppression model and may reflect culture-in-flight conditions.

## Claim 2 — ECM and ER / secretory-stress programmes dominate the flown hMSC signature, with UPR effectors down

**KG finding.** Top GO-BP term *response to ER stress* (24/66, 3.5×); Reactome *cargo concentration in the ER*, *XBP1(S) activates chaperone genes*, *COPII-mediated transport*, *elastic fibres* and *collagen assembly*; HSPA5 (−1.89) and XBP1 (−1.69) are down.

**Concordance: PARTIALLY SUPPORTED.** ISS-flown MSCs changed extracellular-matrix organisation and cell-division pathways [3]. Clinostat rotation increased ER-stress markers (GRP78/BiP, IRE1α, p-PERK) in pre-osteoblasts [4], the opposite direction to HSPA5 / XBP1 here.

## Claim 3 — The Wnt-antagonist axis links unloading to reduced bone formation

**KG finding.** DKK1 up (+2.35) and SFRP4 / WNT5A down in flown hMSC; WIF1 down in both marrow genotypes; LRP5 up. GO *negative regulation of canonical Wnt signalling* membership places DKK1, SFRP4 and CAV1 in one module.

**Concordance: SUPPORTED.** In the 60-day Berlin bed-rest study serum sclerostin rose, with DKK1 following a similar but non-significant pattern [5]. Opening osteocyte connexin hemichannels suppressed sclerostin and rescued unloading-induced bone loss in mice [6]. Antibodies against sclerostin and DKK1 are established anabolic strategies for osteoporosis [7].

## Claim 4 — IL-6 is a countermeasure target

**KG finding.** IL6 is Tier A (4 rdkg low-BMD diseases, 5 digcfdekg traits, approved antagonist siltuximab in prokn) but is down (−2.80) in flown hMSC.

**Concordance: MIXED.** Anti-IL-6-receptor antibody reduced unloading-associated pain markers but did not prevent bone loss in hindlimb-unloaded mice [8]. IL-6-positive osteocytes decreased in the unloaded rat femur [9]. A systematic review lists an IL-6 monoclonal antibody among agents that reduced bone resorption in microgravity models [10].

## Claim 5 — COX-2 inhibitors are repurposing candidates

**KG finding.** PTGS2 (COX-2) is a bone-linked DE gene with many approved inhibitors in prokn (celecoxib, etoricoxib, meloxicam…), but is down 4.15 log2 units in flown hMSC.

**Concordance: CONTRADICTED.** Reduced PGE2-mediated skeletal interoceptive signalling drives unloading-induced bone loss in mice [11], and PGE2 release from osteocyte hemichannels is anabolic during unloading [6]. Inhibiting COX-2 would therefore reinforce, not oppose, the flight change — a direction-blind drug–target join would rank these agents wrongly.

## Claim 6 — Antiresorptive osteoporosis drugs are relevant countermeasures although their targets are not DE in flight

**KG finding.** rdkg lists 41 DrugBank osteoporosis drugs; their prokn targets (VDR, PGR, ESR1, CYP19A1, NR3C1, FDPS, SOST, TNFSF11) are not DE in any flight contrast, but TNFRSF11B (osteoprotegerin) is up in flown hMSC.

**Concordance: SUPPORTED.** Alendronate combined with resistive exercise prevented hip BMD loss and suppressed resorption markers in ISS crew, whereas exercise alone only partially protected [12]. Reviews of astronaut bone loss report efficacy of bisphosphonates and RANKL antibody in microgravity models [10] and call for agents with both antiresorptive and anabolic action [13].

## Claim 7 — Cathepsin K inhibition is a spaceflight repurposing lead

**KG finding.** CTSK is up (+1.29) in flown hMSC; odanacatib (phase 3) acts on it in prokn; Reactome *collagen degradation* is enriched (13/52).

**Concordance: NOVEL.** Odanacatib was developed as a cathepsin-K-specific antiresorptive for osteoporosis [7], but the search found no spaceflight or unloading study of cathepsin-K inhibition.

## Claim 8 — Nrf2 deficiency amplifies the marrow spaceflight response

**KG finding.** Nrf2-KO marrow has 297 flight DE genes vs 202 in WT; chemokines CXCL1/2/3 and CCL2 rise in both genotypes.

**Concordance: SUPPORTED.** In the MHU-3 mission, Nrf2-knockout mice showed stronger flight-induced inflammatory marker expression, immunosuppression and thrombotic microangiopathy than wild-type mice [14].

## Claim 9 — The federation's unloading bone transcriptomes are nearly empty

**KG finding.** Hindlimb-unloaded cortical bone (OSD-467) has 3 DE genes and unloaded marrow (OSD-214) has 7 at the standard thresholds.

**Concordance: NOVEL.** This is a KG coverage observation. Hindlimb unloading robustly shifts osteocyte sclerostin, IL-6 and IGF-I and reduces bone density [9], and causes bone loss rescued by sclerostin suppression [6], so the sparse signatures reflect the processed contrasts, not the model.

## Claim 10 — In-vivo marrow and flown hMSC move shared genes in opposite directions

**KG finding.** Of the 10 genes DE in all three flight contrasts, only ALPL changes in the same direction in marrow and hMSC; CXCL1/2/3 and CCL2 are up in marrow and down in hMSC.

**Concordance: NOVEL.** No source comparing these two systems was found.

## References

1. Li L, et al. Effects of simulated microgravity on the expression profiles of RNA during osteogenic differentiation of human bone marrow mesenchymal stem cells. *Cell Prolif*. 2019. PMID:30397970 · [doi:10.1111/cpr.12539](https://doi.org/10.1111/cpr.12539)
2. Gershovich PM, et al. The effects of simulated microgravity on the pattern of gene expression in human bone marrow mesenchymal stem cells under osteogenic differentiation. *Fiziol Cheloveka*. 2013. PMID:25509878
3. Huang P, et al. Impact of spaceflight on gene expression in cultured human mesenchymal stem/stromal cells. *PLoS One*. 2025. PMID:40080486 · [doi:10.1371/journal.pone.0315285](https://doi.org/10.1371/journal.pone.0315285)
4. Yoo YM, et al. Melatonin suppresses autophagy induced by clinostat in preosteoblast MC3T3-E1 cells. *Int J Mol Sci*. 2016. PMID:27070587 · [doi:10.3390/ijms17040526](https://doi.org/10.3390/ijms17040526)
5. Belavý DL, et al. Serum sclerostin and DKK1 in relation to exercise against bone loss in experimental bed rest. *J Bone Miner Metab*. 2016. PMID:26056021 · [doi:10.1007/s00774-015-0681-3](https://doi.org/10.1007/s00774-015-0681-3)
6. Zhao D, et al. Activation of connexin hemichannels enhances mechanosensitivity and anabolism in disused and aged bone. *JCI Insight*. 2024. PMID:39641271 · [doi:10.1172/jci.insight.177557](https://doi.org/10.1172/jci.insight.177557)
7. Rachner TD, et al. Osteoporosis: now and the future. *Lancet*. 2011. PMID:21450337 · [doi:10.1016/S0140-6736(10)62349-5](https://doi.org/10.1016/S0140-6736%2810%2962349-5)
8. Wakabayashi H, et al. Functional block of interleukin-6 reduces a bone pain marker but not bone loss in hindlimb-unloaded mice. *Int J Mol Sci*. 2020. PMID:32429268 · [doi:10.3390/ijms21103521](https://doi.org/10.3390/ijms21103521)
9. Metzger CE, et al. Differential responses of mechanosensitive osteocyte proteins in fore- and hindlimbs of hindlimb-unloaded rats. *Bone*. 2017. PMID:28782619 · [doi:10.1016/j.bone.2017.08.002](https://doi.org/10.1016/j.bone.2017.08.002)
10. Baran R, et al. Microgravity-related changes in bone density and treatment options: a systematic review. *Int J Mol Sci*. 2022. PMID:35955775 · [doi:10.3390/ijms23158650](https://doi.org/10.3390/ijms23158650)
11. Guo Q, et al. Unloading-induced skeletal interoception alters hypothalamic signaling to promote bone loss and fat metabolism. *Adv Sci (Weinh)*. 2023. PMID:37880864 · [doi:10.1002/advs.202305042](https://doi.org/10.1002/advs.202305042)
12. Sibonga J, et al. Resistive exercise in astronauts on prolonged spaceflights provides partial protection against spaceflight-induced bone loss. *Bone*. 2019. PMID:31400472 · [doi:10.1016/j.bone.2019.07.013](https://doi.org/10.1016/j.bone.2019.07.013)
13. Iwamoto J, et al. Interventions to prevent bone loss in astronauts during space flight. *Keio J Med*. 2005. PMID:16077253 · [doi:10.2302/kjm.54.55](https://doi.org/10.2302/kjm.54.55)
14. Shimizu R, et al. Nrf2 alleviates spaceflight-induced immunosuppression and thrombotic microangiopathy in mice. *Commun Biol*. 2023. PMID:37626149 · [doi:10.1038/s42003-023-05251-w](https://doi.org/10.1038/s42003-023-05251-w)

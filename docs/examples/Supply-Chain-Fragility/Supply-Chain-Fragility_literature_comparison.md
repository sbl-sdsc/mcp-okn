# Supply-Chain-Fragility — per-claim literature comparison

Companion to `Supply-Chain-Fragility_report.md` §8. One entry per checked claim, numbered to match
the report's Concordance table. Occupational- and community-health sources retrieved via the
**PubMed** MCP connector; supply-chain security and regulatory sources retrieved by web search of
vendor, agency and industry publications. Concordance values are drawn from the closed six-term set:
SUPPORTED / PARTIALLY SUPPORTED / CONTRADICTED / MIXED / NOVEL / UNRESOLVED.

---

## Claim 1 — Dependency count is the real attack surface

*As stated in this analysis:* a handful of packages are direct dependencies of a large fraction of an
entire ecosystem — **numpy** is a direct dependency of 70,032 of `securechainkg`'s 803,769 packages
(8.7%), **requests** of 64,097, **pandas** of 45,991 — so dependency in-degree, not vulnerability
count, is the primary measure of blast radius.

**Concordance: SUPPORTED.** Sonatype's 2026 State of the Software Supply Chain report attributes
registry traffic growth directly to transitive dependency sprawl and records PyPI at 50.6%
year-on-year download growth with >743,000 packages [7]. Independent analysis places roughly 95% of
open-source vulnerabilities in transitive rather than direct dependencies, and notes that frameworks
with 1,000+ transitive dependencies face exponential exposure [8]. Both corroborate the structural
claim; neither uses the same graph, so the specific in-degree figures are this study's own.

*Caveat:* our figures are **direct** in-degree only (see report limitation 6), so they are a strict
lower bound on the exposure the cited sources describe.

---

## Claim 2 — Vulnerability load and blast radius are only loosely coupled

*As stated in this analysis:* the highest-blast packages carry modest CVE counts (numpy 8, requests
6, pandas 1) while the highest-CVE packages have moderate blast radii (django 120 CVEs / 9,083
dependents; pillow 55 / 13,962), so single-axis triage misprioritises.

**Concordance: SUPPORTED.** The transitive-dependency blind-spot literature makes the same argument
for the same reason — direct-dependency scanning surfaces the wrong set, and the packages that
actually propagate risk are not the ones with the longest advisory histories [8].

---

## Claim 3 — Hub compromise propagates into industrial toolchains by the ordinary registry path

*As stated in this analysis:* 13 of 26 profiled CAD, metrology, fieldbus and PLC packages depend
directly on a top-blast hub, so a compromise or breaking change in numpy, setuptools or pyserial
reaches shop-floor toolchains by exactly the path it reaches a web service.

**Concordance: SUPPORTED.** The Shai-Hulud npm worm, first published 2025-09-15, was the first
successful self-propagating attack in a major package registry: it harvested credentials with
TruffleHog and used any npm tokens it found to publish malicious versions of every package the
compromised identity could reach [9]. The Shai-Hulud 2.0 variant disclosed 2025-11-24 added
pre-install execution, runner persistence and destructive fallback, and backdoored 796 unique
packages totalling >20 million weekly downloads [10]. CISA issued an ecosystem-wide alert [11]. The
mechanism — registry-mediated, indifferent to the downstream application domain — is precisely the
one this claim asserts.

*Caveat:* the demonstrated attacks were in npm; `securechainkg`'s manufacturing-relevant slice is
PyPI and Cargo. The propagation mechanism transfers, the specific incident does not.

---

## Claim 4 — The industrial-control vendors reached by the hardware bridge carry the sector's concentrated equipment risk

*As stated in this analysis:* of the 20 organisation names bridging NAICS codes to hardware products
in `securechainkg`, the industrially relevant ones are **Rockwell Automation** (NAICS 335314, 109
distinct CVEs across 47 CWE types), **ABB** (335313, 87 CVEs / 50 CWE types) and **Johnson Controls**
(333415 / 336360, 16 CVEs), plus Trane and Vertiv at 4 each.

**Concordance: SUPPORTED.** CISA's 2026 ICS advisory stream names these same vendors repeatedly:
Rockwell ThinManager (SSRF, versions 13.0–14.0, critical manufacturing sector), Rockwell 432ES-IG3
Series A (CVE-2025-9368, CVSS v3 7.5, resource-exhaustion denial of service), ABB ASPECT / NEXUS /
MATRIX (authentication bypass via alternate path, missing authentication for critical functions,
classic buffer overflow, with device takeover possible), and Johnson Controls C-CURE 9000 / victor
application server (SSRF permitting unauthenticated remote code execution on adjacent networks)
[13]. CISA's advisory AA26-097A, updated 2026-07-22, adds guidance on detecting malicious changes to
reusable code modules inside Rockwell PLC programs and expands vendor scope to Schneider Electric and
Siemens [12] — i.e. the exposure is being actively exploited, not merely catalogued.

*Caveat:* the bridge reaches these vendors as *hardware manufacturers*, not as suppliers to any
specific NAICS 332 firm. The inference that a heat-treating or valve shop operates this equipment is
domain knowledge, not a graph edge.

---

## Claim 5 — Small and medium manufacturers are the weak link in the industrial software supply chain

*As stated in this analysis:* the observed base is dominated by firms averaging 16 employees, for
which software supply-chain hygiene is a fixed cost that does not scale down.

**Concordance: SUPPORTED.** CMMC readiness reporting finds that although small businesses account
for more than 70% of DoD suppliers, many are materially behind on the 110 NIST 800-171 Rev. 2
controls that CMMC Level 2 verifies, with cost cited as the binding constraint; the distance between
intent and demonstrable readiness is described as wider than anticipated as Phase 2 approached [14].
DoD suspended CMMC Phase 2 implementation on 2026-07-13, which removes the near-term forcing function
without changing the underlying gap.

*Caveat:* CMMC concerns information security controls, not open-source dependency management. The
claim is supported as an inference about capacity, not as a measured finding about dependency
practice.

---

## Claim 6 — Electroplating (332813) is the most software- and automation-exposed NAICS 332 industry

*As stated in this analysis:* 332813 scores 100 on the industry software-fragility index — six
distinct OT/PLC-facing packages in its mapped stack, 18 recorded CVEs across that stack, continuous
recipe-driven bath and rectifier control.

**Concordance: NOVEL.** No prior source found that ranks fabricated-metal sub-industries by software
dependency exposure. This is the study's own construction and it rests on the analyst-assigned
process-technology mapping of report §6.3, not on any graph edge. A different mapping would produce a
correlated but different ranking; the mapping is enumerated in full in
`Supply-Chain-Fragility_reproducibility.md` so it can be substituted and re-run. No source found.

---

## Claim 7 — Geographic concentration and software fragility are anti-correlated across these industries

*As stated in this analysis:* across the 26 industries with ≥60 placed firms, Spearman ρ between the
sample-corrected county concentration index and the industry software-fragility score is **−0.16**.

**Concordance: NOVEL.** No prior work joins an industrial-geography concentration measure to a
software-dependency exposure measure at the industry level, so there is nothing to agree or disagree
with. The correlation is weak and the sample is 26 industries, so it should be read as "the two axes
are not positively related" rather than as a quantified negative relationship. No source found.

---

## Claim 8 — Electroplating's regulated footprint is a community-health as well as a supply-chain concern

*As stated in this analysis:* 332813 has the largest regulated footprint of any NAICS 332 industry —
3,874 EPA-registered facilities across 834 counties — and its characteristic exposures are known
carcinogens.

**Concordance: SUPPORTED.** In a cohort of 2,991 Italian electroplaters with cumulative exposure
reconstructed from measured tank concentrations × employment duration, nickel exposure significantly
increased mortality from lung, rectal and kidney cancer after adjustment for chromium, and the authors
conclude the lung-cancer excess appears **below the occupational exposure limit** [1]. The SYNERGY
pooled analysis of 14 European and Canadian case-control studies (16,901 lung-cancer cases, 20,965
controls, measurement-based job-exposure matrix) found odds ratios of 1.32 (95% CI 1.19–1.47) for the
highest quartile of cumulative Cr(VI) exposure and 1.29 (1.15–1.45) for nickel in men, with excess
risk present in never-, former- and current-smoker strata [2].

*Caveat:* both studies measure *worker* exposure. This analysis measures *facility density* in a
county. The link between the two is plausible but unmeasured here, and report limitation 8 states
that county indicators cannot support occupational attribution.

---

## Claim 9 — Welding- and fabrication-intensive industries carry a distinctive neurological hazard

*As stated in this analysis:* the injury and health burden observed in manufacturing-intensive
counties (§5.5) is consistent with recognised fabrication hazards, of which welding-fume manganese
neurotoxicity is the most distinctive.

**Concordance: PARTIALLY SUPPORTED.** The literature review applying IRSST expert-panel criteria
identified 78 probable/possible and 19 additional possible cases of occupational manganism among
manganese-exposed workers in welding processes, and documents abnormal manganese accumulation in the
globus pallidus; but it concludes explicitly that **epidemiological evidence linking welding exposure
to Parkinson's disease remains controversial** [3]. Manganism as an occupational entity is supported;
a population-level Parkinson's signal is not.

*Caveat:* nothing in the county-level SDoH data used here measures neurological outcomes, so this
claim is contextual support for the plausibility of an occupational contribution, not a test of it.

---

## Claim 10 — Machine shops expose workers to a documented respiratory and cancer hazard

*As stated in this analysis:* machine shops (332710) are the sector's largest industry by firm count
(5,262 firms, 85,375 recorded employees), so their characteristic exposure — metalworking fluid
aerosol — reaches the largest worker population in the sector.

**Concordance: SUPPORTED.** A systematic review of the 227 peer-reviewed reports published after the
1999 OSHA Metalworking Fluids Standards Advisory Committee report identified three major studies
showing excess lung, liver, pancreatic and laryngeal cancer and leukaemia associated with
metalworking-fluid exposure, and found the post-1998 evidence **strengthened** associations of asthma
and hypersensitivity pneumonitis with recent exposure; the author concludes the new evidence
demonstrates material impairment of health at prevailing exposure levels [4].

*Caveat:* OSHA declined to promulgate a metalworking-fluid standard in 2003 and the Third Circuit
rejected the union suit to compel one, so the regulatory position and the epidemiological position
diverge. This analysis makes no regulatory claim.

---

## Claim 11 — Counties where fabricated metal dominates the regulated industrial base show +26% drug-overdose mortality

*As stated in this analysis:* in the tier of 223–278 counties where NAICS 332 accounts for ≥2% of all
EPA-regulated facilities, mean drug-overdose mortality is 26% above the marginal tier, and the
gradient is monotonic across all three tiers.

**Concordance: CONTRADICTED.** A county-level negative-binomial analysis of 2018–2021 overdose
mortality (NCHS Multiple Cause of Death, linked to industry-specific job shares, drug-supply and
sociodemographic data, with tests for fentanyl-seizure moderation) found **negative** associations
between manufacturing job share and overdose mortality, alongside positive associations for
arts/entertainment/recreation and public administration [5]. The direction of that finding is opposite
to ours.

*Reconciliation.* The two studies measure different things. Oh et al. use **manufacturing employment
share** across all manufacturing; this analysis uses **fabricated metal's share of the county's
permitted facility base** — a permitting-intensity measure that upweights small, rural, dirty
operations and is not an employment measure at all. Both results can hold simultaneously
(manufacturing employment protective; fabricated-metal permitting intensity adverse). Because of this,
report §7 relies on the more conservative per-capita operationalisation (+14%) and the finding is
never stated as "manufacturing counties have more overdoses". This claim should be treated as
unresolved pending an employment-based replication (report §7, prediction 3).

---

## Claim 12 — Manufacturing-intensive counties carry excess working-age mortality attributable to the industrial economy

*As stated in this analysis:* the manufacturing-intensity gradient in §5.5 shows premature
age-adjusted mortality 13% above the marginal tier and life expectancy 1.4 years lower.

**Concordance: PARTIALLY SUPPORTED.** The causal evidence attaches to manufacturing **decline**, not
presence. Using exogenous variation in industrial-robot adoption over 1993–2007, increases in
automation caused substantive increases in all-cause mortality for both sexes aged 45–54; each
additional robot per 1,000 workers produced roughly 8 additional deaths per 100,000 men and nearly 4
per 100,000 women in that age band, with effects on drug overdose, suicide, homicide and
cardiovascular mortality, and automation explaining about 12% of the rise in working-age overdose
mortality [6].

*Caveat and reconciliation.* This is a scope divergence in the same direction as claim 11. A
cross-sectional county association cannot distinguish "these places are unhealthy because of the
work" from "these places retained the work because they had no alternative, and the same conditions
produce both". Report limitation 8 states this, and §7 does not claim causality.

---

## Claim 13 — Maintenance thinness can be assessed for the packages that matter

*As stated in this analysis (as a question the brief asked):* the fragility of a package should
account for how thinly it is maintained.

**Concordance: CONTRADICTED** — by the knowledge graph's own contents, not by any external source.
Only **679 of 803,769 packages (0.084%)** in `securechainkg` carry any `schema:contributor` data. That
slice is a disjoint set of GitHub-hosted C/C++ projects (flatbuffers, llama.cpp, xgboost, OpenRCT2,
spdlog, ceph, grpc, wxWidgets …) whose contributor counts are rounded to the nearest hundred (400,
300, 200), and **not one** of the high-blast PyPI or Cargo hubs appears in it — a query joining the
contributor-bearing slice to the dependency graph returns zero rows, because the contributor-bearing
Software nodes carry no `hasSoftwareVersion` edges into it.

This is a **KG data-quality finding** and is reported as one: the maintenance-thinness axis is
unmeasurable in this federation as currently loaded, and the report substitutes no proxy in its place.
No external source is at issue. Related and separate: `securechainkg` records **matplotlib** as
`AGPL-3.0-only`, which is incorrect (matplotlib is distributed under a PSF-derived BSD-style licence),
so the licence axis contains at least one confirmed error and its copyleft inventory should be treated
as a lower bound.

---

## References

Format matches report §12; entries shared with the report reuse the identical entry.

1. Sciannameo V, et al. Cancer mortality and exposure to nickel and chromium compounds in a cohort of Italian electroplaters. *American journal of industrial medicine*. 2019. PMID:30615207 · [doi:10.1002/ajim.22941](https://doi.org/10.1002/ajim.22941)
2. Behrens T, et al. Occupational exposure to nickel and hexavalent chromium and the risk of lung cancer in a pooled analysis of case-control studies (SYNERGY). *International journal of cancer*. 2022. PMID:36054442 · [doi:10.1002/ijc.34272](https://doi.org/10.1002/ijc.34272)
3. Flynn MR, Susi P. Neurological risks associated with manganese exposure from welding operations — a literature review. *International journal of hygiene and environmental health*. 2009. PMID:19181573 · [doi:10.1016/j.ijheh.2008.12.003](https://doi.org/10.1016/j.ijheh.2008.12.003)
4. Mirer FE. New evidence on the health hazards and control of metalworking fluids since completion of the OSHA advisory committee report. *American journal of industrial medicine*. 2010. PMID:20623659 · [doi:10.1002/ajim.20853](https://doi.org/10.1002/ajim.20853)
5. Oh S, Cano M, Kim Y. County-level industrial composition of the labor force and drug overdose mortality rates in the United States in 2018-2021. *American journal of industrial medicine*. 2024. PMID:38770905 · [doi:10.1002/ajim.23612](https://doi.org/10.1002/ajim.23612)
6. O'Brien R, Bair EF, Venkataramani AS. Death by Robots? Automation and Working-Age Mortality in the United States. *Demography*. 2022. PMID:35195250 · [doi:10.1215/00703370-9774819](https://doi.org/10.1215/00703370-9774819)
7. Sonatype. *Software Infrastructure Strain — 2026 State of the Software Supply Chain Report*. 2026. [https://www.sonatype.com/state-of-the-software-supply-chain/2026/software-infrastructure-growth](https://www.sonatype.com/state-of-the-software-supply-chain/2026/software-infrastructure-growth)
8. Kusari. *The 95% Problem: Why Transitive Dependencies Are Your Biggest Software Supply Chain Blind Spot in 2026*. 2026. [https://www.kusari.dev/blog/why-transitive-dependencies-biggest-software-supply-chain-blind-spot-2026](https://www.kusari.dev/blog/why-transitive-dependencies-biggest-software-supply-chain-blind-spot-2026)
9. Palo Alto Networks Unit 42. *"Shai-Hulud" Worm Compromises npm Ecosystem in Supply Chain Attack*. 2025–2026. [https://unit42.paloaltonetworks.com/npm-supply-chain-attack/](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)
10. Microsoft Security. *Shai-Hulud 2.0: guidance for detecting, investigating, and defending against the supply chain attack*. 2025-12-09. [https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/](https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/)
11. CISA. *Widespread Supply Chain Compromise Impacting npm Ecosystem*. 2025-09-23. [https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem)
12. CISA. *Iranian-Affiliated Cyber Actors Exploit Programmable Logic Controllers Across US Critical Infrastructure* (advisory AA26-097A, updated 2026-07-22). [https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a](https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a)
13. Industrial Cyber. *CISA flags critical ICS vulnerabilities across Rockwell and ABB systems, exposing OT networks to potential exploits*. 2026. [https://industrialcyber.co/industrial-cyber-attacks/cisa-flags-critical-ics-vulnerabilities-across-rockwell-and-abb-systems-exposing-ot-networks-to-potential-exploits/](https://industrialcyber.co/industrial-cyber-attacks/cisa-flags-critical-ics-vulnerabilities-across-rockwell-and-abb-systems-exposing-ot-networks-to-potential-exploits/)
14. Federal News Network. *The CMMC readiness gap: why many small manufacturers are unprepared*. 2026-04. [https://federalnewsnetwork.com/commentary/2026/04/the-cmmc-readiness-gap-why-many-small-manufacturers-are-unprepared/](https://federalnewsnetwork.com/commentary/2026/04/the-cmmc-readiness-gap-why-many-small-manufacturers-are-unprepared/)

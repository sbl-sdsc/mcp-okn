# Sentinel-Wildlife — literature comparison (per-claim record)

Companion to `Sentinel-Wildlife_report.md` §8. One entry per checked claim, with the concordance
label and the citations it rests on. Retrieved via the **PubMed** MCP connector; entries marked
*full-text-verified* were read beyond the abstract. Concordance is one of six values —
**SUPPORTED**, **PARTIALLY SUPPORTED**, **CONTRADICTED**, **MIXED**, **NOVEL**, **UNRESOLVED** —
and every qualifier lives in the prose, not in the label. This is a *comparison*, not a
validation: NOVEL is a finding, and the check exposes errors in the knowledge graphs as often as
it corroborates a claim.

---

## Claim 1 — Birds are established sentinel species for environmental contaminant burden, including PFAS

**Concordance: SUPPORTED.**

The sentinel framing this study assumes is standard in avian ecotoxicology. Livers from
road-killed owls of five species were screened for 81 organic contaminants; PFOS was the only PFAS
detected and ranged 2.88–848 ng/g wet weight, and the paper opens by stating that raptors are
recognised as valuable sentinel species for monitoring environmental contaminants because of their
foraging across terrestrial and aquatic food webs and their high trophic position [1]. PFAS
profiling in peregrine falcon nestling blood (n = 57) and sibling eggs (n = 9) across rural and
urban Great Lakes sites likewise describes the species explicitly as a "sentinel apex species" and
resolves urban–rural differences in ∑PFCA exposure [2].

The qualification matters for how this analysis should be read: the *established* avian sentinels
are raptors, chosen for trophic position, whereas the federation's only avian contaminant data are
two waterfowl species chosen because they were shot near a PFAS-contaminated site. The sentinel
concept transfers; the specific taxa do not.

## Claim 2 — Mallard (*Anas platyrhynchos*) is an avian-influenza reservoir host

**Concordance: SUPPORTED.**

Three seasons of Atlantic Flyway sampling (1,821 cloacal/oropharyngeal samples, 2015–2017) yielded
109 influenza A virus isolates from mallards and American black ducks, and the authors describe
both species as host reservoirs of IAV with ecological and conservation importance in the flyway;
the study also demonstrates virus gene flow between breeding and wintering ends of the flyway
consistent with banded-bird movements [3]. This corroborates both the `nde` mallard→avian-influenza
link and the `biohealth` mallard→"Influenza in Birds" edge, and supports the flyway framing that
motivated choosing Florida as the study area.

## Claim 3 — Muscovy duck (*Cairina moschata*) is an avian-influenza host, and a better one than mallard

**Concordance: SUPPORTED.**

Experimental intranasal inoculation of Pekin duck, mallard and Muscovy duck with several genotypes
of chicken-origin H9N2 found Pekin and mallard ducks generally resistant, while Muscovy ducks were
relatively susceptible, with virus isolated from oropharynx, trachea and lung tissues in all tested
viruses; genotype 57 H9N2 showed increased replication in Muscovy duck specifically, and the
authors conclude that more surveillance attention should be paid to this host [4].

This is the strongest independent support for the analysis's rank-2 species, and it inverts the
usual emphasis: for H9N2 the Muscovy duck is the more competent of the two, even though the mallard
is the species with a measured contaminant burden. It is also the reason Muscovy duck, not mallard,
is nominated in report §7 as the best single contaminant-sentinel target — subfamily proximity to
the measured mallard plus an independently corroborated host role.

## Claim 4 — Wild turkey (*Meleagris gallopavo*) is a West Nile virus host

**Concordance: CONTRADICTED.**

Two age groups of juvenile wild turkeys were subcutaneously inoculated with WNV and sampled daily.
No clinical signs and only minimal gross lesions were attributable to infection; peak viraemia
titres were below 10^5 PFU/ml, viraemia lasted 0–4 days depending on age, no infectious virus was
recoverable from heart, brain, kidney, skeletal muscle, spleen or feathers at 14 days
post-inoculation, and the authors state explicitly that the viraemias observed suggest
WNV-infected wild turkeys do not play a role in WNV transmission [5]. — full-text-verified.

The `biohealth` turkey→West Nile fever edge is therefore a faithful record of a *literature
co-occurrence* (turkeys are studied in a WNV context, and they do seroconvert) but not of host
competence. Because wild turkey is this analysis's rank-1 species and eight asserted diseases drive
that rank, this single edge measurably over-weights it: the WNV component of the turkey's score
should be discounted, and the report's §6.2 and §7 say so. The species remains a defensible
pathogen-surveillance target on the influenza evidence in Claim 5.

## Claim 5 — Wild turkey is a host for avian influenza

**Concordance: SUPPORTED.**

Forty-one wild turkeys were found dead in Johnson County, Wyoming, adjacent to a property with
confirmed HPAI in a backyard flock; avian influenza virus RNA was detected in all 11 birds swabbed,
and necropsy of seven found acute multi-organ necrosis most consistently in lung, spleen, liver,
gastrointestinal tract and gonads, indicating high virulence of subclade 2.3.4.4b H5N1 in this
species [6]. — full-text-verified.

Two caveats travel with the support. The authors note that documented HPAI cases in wild turkeys
are *rare*, and they interpret this event as spillback from domestic poultry rather than as
maintenance in a wild reservoir. The turkey is therefore a high-consequence, low-frequency host —
which is a good argument for surveillance but not for treating it as a maintenance population.

## Claim 6 — European starling (*Sturnus vulgaris*) is a pathogen host relevant to wildlife–human disease surveillance

**Concordance: PARTIALLY SUPPORTED.**

A three-part experimental assessment found that inoculated starlings all shed viral RNA and
seroconverted; that starlings exposed only to water shared with IAV-infected mallards in a purpose
built transmission cage all became infected and shed at similar levels; and that no
starling-to-starling contact transmission occurred. The authors conclude starlings can act as
avian-influenza **bridge** hosts between reservoir waterfowl and poultry but are unlikely to be
maintenance hosts, and note that their antibody response is relatively brief, which matters when
interpreting field serology [7].

The half that holds is the species' role as an epidemiologically meaningful host in exactly the
wild-bird/agriculture interface this study is about. The half that does not is the *pathogen*: the
federation asserts starling→eastern equine encephalitis and starling→conjunctivitis, neither of
which this search corroborated, while the corroborated influenza edge is one the federation does
not carry for this species. The graph has the right animal attached to the wrong disease.

## Claim 7 — Birds are the amplifying hosts of West Nile virus, so avian WNV surveillance is the informative arm

**Concordance: SUPPORTED.**

WNV is amplified in an enzootic cycle involving birds as amplifying hosts, with humans and horses
considered dead-end hosts because they do not develop high viraemia; the paper's comparative design
across avian, mammalian and insect hosts, and its finding that virulence determinants are
host-dependent, both rest on that cycle [8]. — full-text-verified. The same amplifying-host
structure is restated for the closely related Usutu virus, where birds are the amplifying hosts and
mammals incidental [14].

The divergence is entirely on the graph side. `nde` holds 43 West Nile virus datasets;
their `schema:species` hosts are *Homo sapiens*, *Mus musculus*, *Rattus norvegicus*, *Macaca
mulatta*, *Bos taurus*, *Equus caballus*, *Aedes aegypti*, *Culex* and *Drosophila melanogaster* —
and no bird at all. The federation therefore contains the pathogen, the human disease and the
vector, and omits the amplifying host, which is precisely the link a wildlife-sentinel programme
would need.

## Claim 8 — No amphibian anywhere in the federation has a measured contaminant body burden

**Concordance: NOVEL.**

The claim is an observation about graph coverage, so there is no prior literature for it as stated;
no source found. Its significance, however, comes from what the literature *does* contain, because
that is what makes the gap a coverage failure rather than a knowledge failure. Amphibian PFAS body
burdens are measured and published: 39 PFAS were quantified across tissues of Chinese toads from
Chaohu Lake with liver ∑PFAS of 215.97 ng/g dry weight, gonads 135.42 and intestine 114.08, and the
paper opens by stating that amphibians are sensitive biomonitors of environmental pollutants for
which PFAS reports remain limited [9]. Frogs exposed through skin showed chain-length-dependent
bioaccumulation, tissue-specific distribution and >80% maternal transfer of some PFAS to eggs, with
hibernation causing measurable bioamplification [10]. Chronic exposure studies in northern leopard
frog tadpoles quantified PFBS/PFHxS and PFBA/PFHxA in liver and whole-body tissue with
bioconcentration factors ≤10 L/kg [11][12], the second of which is full-text-verified.

So the federation's amphibian body-burden count of zero is not a statement about amphibian
toxicology; it is a statement about which datasets have been ingested. That is why report §7
predicts that Florida amphibian PFAS burdens will be non-zero and measurable, and why the amphibian
tier in Figure 4 is labelled "no measured relative *in this federation*" rather than "no data
exists".

## Claim 9 — Amphibian disease is an active Florida-relevant problem that the federation cannot connect to any host

**Concordance: SUPPORTED.**

Museum tissues from 12 widespread taxa in three co-distributed frog families (Bufonidae, Hylidae,
Ranidae) across the eastern two-thirds of the USA were screened by qPCR for three generalist
pathogens. About 20% of individuals carried at least one pathogen (231 single infections, 25
coinfections); Bd prevalence was 16.9% (95% CI 14.9–19%), ranavirus 4.38% and *Amphibian Perkinsea*
1.06%, with Ranidae accounting for 74.3% of all infections and carrying significantly higher Bd
intensities than the other two families [13]. — full-text-verified. Two of the authors are based in
Florida, and the sampling frame includes the state.

Against that, the federation holds *Batrachochytrium dendrobatidis* as an infectious agent in
2 `nde` datasets, neither of which records a host species, and holds no amphibian
pathogen edge for any Florida-recorded species other than the flagged artefacts of Claim 10. The
host–pathogen link that the amphibian half of a sentinel programme would rest on is absent from the
graphs while being well established in the literature — and the family the literature identifies as
most affected, Ranidae, is well represented in the Florida record (*Lithobates* spp., 9 taxa).

## Claim 10 — The `biohealth` assertion Anura → influenza is a text-mining artefact

**Concordance: CONTRADICTED.**

No literature supports influenza A infection in anurans. The competent-host literature for avian
influenza is confined to birds and mammals: the duck-susceptibility comparison covers three
galloanserine hosts [4] and the starling work covers a passerine bridge host exposed via infected
mallards [7], and neither, nor any source found in this search, extends IAV host range to
amphibians. Influenza A's receptor biology and the absence of any amphibian isolate make the
assertion implausible on its face.

The edge is therefore read here as an extraction error in a literature-mined layer — most likely a
co-mention of anurans and influenza in a text where the two are not in a host relation — and the
taxon is held out of the species ranking on that basis, alongside the sibling assertion
Amphibia → salmonellosis, which is at least biologically possible (reptile and amphibian
*Salmonella* carriage is real) but is asserted at class rank and so is not a sampling target.

## Claim 11 — Great horned owl (*Bubo virginianus*) is a contaminant sentinel as well as the conjunctivitis host the federation asserts

**Concordance: PARTIALLY SUPPORTED.**

Owls are established contaminant sentinels and PFOS was quantified in owl liver across five species
— eagle owl, long-eared owl, little owl, tawny owl and barn owl — with the highest ∑OCP, ∑PCB and
PFOS burdens in the two species of highest trophic position [1]. That supports the general
proposition for the family and the trophic logic behind it.

It does not support the specific claim. *Bubo virginianus* was not among the species sampled (its
Palaearctic congener *B. bubo* was), so the transfer is itself a phylogenetic inference of the same
kind this report tiers explicitly — genus-level, therefore tier I1 reasoning applied to a
contaminant class rather than to a measured individual. The `biohealth` great horned
owl→conjunctivitis edge was not corroborated by this search and remains UNRESOLVED as a
host-competence claim.

## Claim 12 — A first Florida measurement is required before any exposure statement can be made for the study area

**Concordance: NOVEL.**

No source found, and none should be expected: this is a statement about the coverage of a specific
federated knowledge graph on a specific date, not about the world. It is recorded here because it
is the operative conclusion of the report — with `sawgraph` holding zero samples of any medium in
Florida and `spoke-okn`'s county chemical layer containing no PFAS for any Florida county, there is
no basis in the federation for any Florida exposure, risk or trend statement, and the correct next
action is measurement rather than further analysis.

---

## References

1. Dulsat-Masvidal M, et al. Assessing Contamination Profiles in Livers from Road-Killed Owls. *Environ Toxicol Chem*. 2024. PMID:38146916 · [doi:10.1002/etc.5816](https://doi.org/10.1002/etc.5816)
2. Sun J, et al. Perfluoroalkyl acids and sulfonamides and dietary, biological and ecological associations in peregrine falcons from the Laurentian Great Lakes Basin, Canada. *Environ Res*. 2020. PMID:32882236 · [doi:10.1016/j.envres.2020.110151](https://doi.org/10.1016/j.envres.2020.110151)
3. Prosser DJ, et al. Maintenance and dissemination of avian-origin influenza A virus within the northern Atlantic Flyway of North America. *PLoS Pathog*. 2022. PMID:35666770 · [doi:10.1371/journal.ppat.1010605](https://doi.org/10.1371/journal.ppat.1010605) — full-text-verified ([PMC9203021](https://pmc.ncbi.nlm.nih.gov/articles/PMC9203021/))
4. Wang C, et al. Infection of chicken H9N2 influenza viruses in different species of domestic ducks. *Vet Microbiol*. 2019. PMID:31176393 · [doi:10.1016/j.vetmic.2019.04.018](https://doi.org/10.1016/j.vetmic.2019.04.018)
5. Kunkel MR, et al. Susceptibility of wild turkeys (*Meleagris gallopavo*) to experimental West Nile virus infection. *Avian Pathol*. 2022. PMID:36102057 · [doi:10.1080/03079457.2022.2123732](https://doi.org/10.1080/03079457.2022.2123732)
6. Malmberg JL, et al. Mortality in Wild Turkeys (*Meleagris gallopavo*) Associated with Natural Infection with H5N1 Highly Pathogenic Avian Influenza Virus (HPAIV) Subclade 2.3.4.4. *J Wildl Dis*. 2023. PMID:37486883 · [doi:10.7589/JWD-D-22-00161](https://doi.org/10.7589/JWD-D-22-00161)
7. Ellis JW, et al. Avian influenza A virus susceptibility, infection, transmission, and antibody kinetics in European starlings. *PLoS Pathog*. 2021. PMID:34460868 · [doi:10.1371/journal.ppat.1009879](https://doi.org/10.1371/journal.ppat.1009879) — full-text-verified ([PMC8432794](https://pmc.ncbi.nlm.nih.gov/articles/PMC8432794/))
8. Fiacre L, et al. Evaluation of NS4A, NS4B, NS5 and 3'UTR Genetic Determinants of WNV Lineage 1 Virulence in Birds and Mammals. *Viruses*. 2023. PMID:37243180 · [doi:10.3390/v15051094](https://doi.org/10.3390/v15051094) — full-text-verified ([PMC10222181](https://pmc.ncbi.nlm.nih.gov/articles/PMC10222181/))
9. Shu Y, et al. Legacy and Emerging Per- and Polyfluoroalkyl Substances Surveillance from Inlet Watersheds of Chaohu Lake, China: Tissue Distribution and Bioaccumulation Potential. *Environ Sci Technol*. 2023. PMID:37565447 · [doi:10.1021/acs.est.3c02660](https://doi.org/10.1021/acs.est.3c02660)
10. Zhu CH, et al. Effects of hibernation on the bioaccumulation and tissue distribution of per- and polyfluoroalkyl substances in frogs (*Rana tigrina cantor*) via skin exposure. *Environ Pollut*. 2025. PMID:40681077 · [doi:10.1016/j.envpol.2025.126842](https://doi.org/10.1016/j.envpol.2025.126842)
11. Rohonczy J, et al. Effects of perfluoroalkyl sulfonic acids on developmental, physiological, and immunological measures in northern leopard frog tadpoles. *Chemosphere*. 2024. PMID:39271078 · [doi:10.1016/j.chemosphere.2024.143333](https://doi.org/10.1016/j.chemosphere.2024.143333)
12. Rohonczy J, et al. The effects of two short-chain perfluoroalkyl carboxylic acids (PFCAs) on northern leopard frog (*Rana pipiens*) tadpole development. *Ecotoxicology*. 2024. PMID:38315267 · [doi:10.1007/s10646-024-02737-z](https://doi.org/10.1007/s10646-024-02737-z) — full-text-verified ([PMC10940426](https://pmc.ncbi.nlm.nih.gov/articles/PMC10940426/))
13. Wiley DLF, et al. Leveraging machine learning to uncover multi-pathogen infection dynamics across co-distributed frog families. *PeerJ*. 2025. PMID:39897487 · [doi:10.7717/peerj.18901](https://doi.org/10.7717/peerj.18901) — full-text-verified ([PMC11786709](https://pmc.ncbi.nlm.nih.gov/articles/PMC11786709/))
14. Vilibic-Cavlek T, et al. Epidemiology of Usutu Virus: The European Scenario. *Pathogens*. 2020. PMID:32858963 · [doi:10.3390/pathogens9090699](https://doi.org/10.3390/pathogens9090699) — full-text-verified ([PMC7560012](https://pmc.ncbi.nlm.nih.gov/articles/PMC7560012/))

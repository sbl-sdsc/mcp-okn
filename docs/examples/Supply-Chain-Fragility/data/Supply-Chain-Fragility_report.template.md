# Supply-Chain Fragility: joining physical manufacturing capacity, regulated industrial burden, software dependency risk and community vulnerability
### A cross-domain OKN federated-SPARQL case study over six Proto-OKN knowledge graphs

**Date:** 2026-07-29 · **Endpoint:** OKN federated SPARQL · **Model:** claude-opus-5

> **Framing (non-negotiable).** The unit of analysis is the **6-digit NAICS industry** (fabricated
> metal product manufacturing, NAICS 332xxx) crossed with the **US county**, over the 48 contiguous
> states plus DC, using knowledge-graph snapshots pinned in §2. Every result is an **observational
> association within the coverage of these graphs** — a directory of small and medium manufacturers
> that self-report on the open web, a federal facility registry, a package-registry dependency
> graph, and county-level public-health indicators. Nothing here is a causal claim, a firm-level
> risk assessment, or a security finding about any named company. Critically, **the software layer
> and the industry layer are not joined by any edge in the federation**: their linkage in §6.3 is
> an explicitly labelled analyst inference, not a graph traversal. Keep both caveats attached to
> every downstream claim.

**Abbreviations.** CVE = Common Vulnerabilities and Exposures identifier; CWE = Common Weakness
Enumeration (vulnerability type); CHR = County Health Rankings; CMMC = Cybersecurity Maturity Model
Certification; EPA FRS = Environmental Protection Agency Facility Registry Service; FIPS = Federal
Information Processing Standard (county/state code); HHI = Herfindahl–Hirschman Index (sum of squared
shares); ICS = industrial control system; KG = knowledge graph; MES = manufacturing execution system;
NAICS = North American Industry Classification System; OPC-UA = Open Platform Communications Unified
Architecture; OT = operational technology; PLC = programmable logic controller; PM2.5 = fine
particulate matter; PyPI = Python Package Index; RUCC = Rural–Urban Continuum Code; S2 = Google S2
geometry cell; SDoH = social determinants of health; SMM = small and medium manufacturer;
SVI = Social Vulnerability Index; ZIP5 = five-digit US postal code.

---

## 1. Executive summary

Three literatures describe the same industrial base and never cite each other. Economic-geography
work asks who can physically make things and where. Software-supply-chain security work asks which
packages everything depends on and how badly they are maintained. Community-health work asks who
lives with the consequences. This study joins all three over the OKN federation and finds that the
two fragility conversations point at **different industries**, which is precisely why neither
surfaces the systemic risk on its own.

The observed base is **{{smm_firms_total}} small and medium manufacturers** across
**{{smm_industries}}** six-digit NAICS 332 industries, employing **{{smm_emp_total}}** people as
recorded in `sudokn`; **{{smm_firms_placed}}** of them resolve to one of **{{smm_counties}}**
counties. The wider fabricated-metal sector — every six-digit NAICS 332 code, including the 25
that `sudokn` does not carry — accounts for **{{frs_facilities_332}}** EPA-regulated facilities
across **{{frs_counties_332}}** counties in `fiokg`. On the software side, `securechainkg` holds
**{{sw_packages}}** packages, **{{sw_dep_edges}}** dependency edges and **{{sw_cves}}** CVEs; a
single package, **numpy**, is a direct dependency of **{{numpy_dependents}}** others —
**{{numpy_dependent_pct}}%** of every package in the graph — with **requests**
({{requests_dependents}}) and **pandas** ({{pandas_dependents}}) close behind.

Geographic concentration, measured as observed county-grain HHI divided by the HHI expected if an
industry's firms were drawn from the whole sector's county distribution, identifies
**{{concentrated_n}}** industries at least twice as clustered as the sector norm. The extreme case
is **NAICS {{top_conc_naics}} ({{top_conc_label}})**, whose {{eligible_industries}}-industry-adjusted
concentration index is 3.68 with an effective breadth of just **18 counties**. Software fragility,
scored from operational-technology protocol depth, recorded CVEs and dependency-hub exposure, ranks
**{{hi_sw_n}}** industries in the high tertile. The two rankings are **weakly negatively correlated
(Spearman ρ = {{spearman_conc_vs_sw}}, n = {{eligible_industries}})**: the most software-exposed
processes — electroplating, coating, machining — are the most ubiquitous, and the most
geographically concentrated ones sit in the middle of the software distribution. A hard conjunction
of both axes therefore yields almost nothing, and the short list must be built from a joint rank.

That short list is **{{shortlist_n}} industries** covering **{{shortlist_firms}}** placed firms,
**{{shortlist_emp}}** recorded jobs and **{{shortlist_facilities}}** regulated facilities, led by
**metal heat treating (332811)**, **iron and steel forging (332111)** and **bolt, nut, screw, rivet
and washer manufacturing (332722)**. The counties that would absorb a shock concentrate hard: **Harris
County, Texas** is a top cluster in **{{harris_industries}}** of the fourteen candidate industries
examined, with {{harris_firms}} firms — followed by Cuyahoga (OH), Macomb, Wayne, Oakland and Kent
(MI), Maricopa (AZ), Tulsa (OK), Erie (PA) and Monroe (NY). On population vulnerability the answer
depends on how "manufacturing county" is defined, and the divergence is itself the finding: measured
by facilities per capita, these counties are markedly more rural, older, and thinner on providers and
broadband, with **+14% drug-overdose mortality** and **+11% injury deaths** — but *less* socially
vulnerable on the composite CDC SVI. Measured by the sector's share of the county's regulated
industrial base, the health penalty becomes monotonic across all three tiers: **−1.4 years life
expectancy**, **+13% premature age-adjusted mortality**, **+26% overdose deaths**.

What this adds: an industry short list that neither an economic-concentration analysis nor a
vulnerability-scanning analysis would produce, together with the named counties that inherit it —
and an honest map of where the federation's own wiring runs out.

## 2. Sources used

| KG | Version | Updated | Role in this study | Join key / confidence |
|---|---|---|---|---|
| `sudokn` | v0.0.10 | 2026-05-08 | Small and medium manufacturer capacity: firm counts, employment, year of establishment, primary NAICS, address | NAICS 332xxx on `hasPrimaryNAICSClassifier`; ZIP5 on `schema:postalCode`; state label on `locatedInState`. High for firms/employment, **low for firm age** ({{pct_firms_with_year}}% coverage) |
| `fiokg` | v0.0.11 | 2026-03-18 | EPA Facility Registry Service: regulated industrial footprint by NAICS, county FIPS and street address; supplies the ZIP5→county crosswalk | `ofPrimaryIndustry` on permit/registration **records**, reached from the facility via `hasRecord`/`hasSupplementalRecord`; county via `kwg:sfWithin`. High |
| `securechainkg` | v0.0.11 | 2026-03-23 | Software dependency graph, package versions, CVEs, CWE types, licences, contributor counts; hardware products and their CVEs | `dependsOn`, `vulnerableTo`, `schema:license`, `schema:contributor`. High for the dependency graph; **very low for maintainer thinness** ({{pct_pkgs_with_contributors}}% coverage) and thin for the industry bridge ({{hardware_bridge_names}} organisation names) |
| `spatialkg` | v0.0.6 | 2026-05-07 | County and state administrative regions, FIPS codes and human-readable labels | `AdministrativeRegion_1`/`_2`, `hasFIPS`, `rdfs:label`. High |
| `spoke-okn` | v0.0.6 | 2026-03-16 | County-level social determinants of health: {{sdoh_variables}} County Health Rankings variables plus the CDC/ATSDR SVI composite; ZIP centroids used to derive county centres | `PREVALENCEIN_SpL` reified statements on `/location/{FIPS5}`; ZIP latitude/longitude on `/location/{ST}-{ZIP}`. High |
| `ruralkg` | v0.2.7 | 2026-06-08 | County population and Rural–Urban Continuum Code, used to build the per-capita manufacturing-intensity measure | `censusCounty` → KWG county IRI, `population`, `hasRUCC`. High |

All {{n_kgs}} graphs were queried directly; every count in this report traces to a logged SPARQL
query in the reproducibility record. No graph is credited for a contribution that came from prior
knowledge.

## 3. Design & rules

**Which industries.** `sudokn` carries 62 distinct NAICS codes, but only the 36 six-digit `332xxx`
codes are a national sample. The remaining 2- and 3-digit codes (`333`, `326`, `3231`, `339`, …) are
almost entirely North Carolina firms — an artefact of a state-specific ingest — and would register as
perfectly concentrated for a reason that has nothing to do with industrial geography. They are
excluded, and the exclusion matters: had they been kept, the concentration ranking would have been
topped by data-collection provenance rather than by manufacturing.

**Which geography.** `sudokn` does not populate `locatedInCounty`, and the federation's registered
route to county grain for it is a computed S2-cell bridge that must be run point-by-point. This study
instead derives a **ZIP5→county crosswalk from `fiokg` itself**: EPA facility addresses carry the ZIP
inline and the facility carries its county FIPS, so grouping manufacturing-sector facilities by ZIP
and keeping only ZIPs where every facility agrees on one county yields an unambiguous, fully
in-SPARQL crosswalk. It places {{smm_firms_placed}} of {{smm_firms_total}} firms (85%); the missing
15% are firms in ZIPs that straddle a county line or that host no NAICS-33 facility.

**How concentration is measured.** Raw HHI rewards small samples — an industry with six observed
firms is mechanically concentrated. Each industry's observed county HHI is therefore divided by the
HHI expected if its *n* firms were drawn at random from the whole sector's county distribution
(sector HHI = {{base_hhi_county}}, i.e. **{{eff_counties_sector}} effective counties**). An index near
1.0 means "no more clustered than fabricated metal manufacturing generally"; 2.0 means twice as
clustered as chance. Industries with fewer than 60 placed firms are excluded from the joint ranking.

**How software fragility is measured, and where the inference is.** Package-level fragility —
dependency in-degree, CVE count, share of versions vulnerable, licence family — is read directly from
`securechainkg`. Attaching it to an *industry* is the hard part, because **no edge in the federation
connects the software dependency graph to a NAICS code**. Two routes exist and both are reported
separately: a **KG-grounded hardware bridge** (organisation-name match between NAICS-classified
manufacturers and hardware vendors, {{hardware_bridge_names}} names reaching
{{hardware_bridge_naics}} NAICS/vendor pairs), and an **analyst-assigned process-technology map**
from each NAICS definition to the CAD, CNC, metrology and PLC-protocol packages that process
requires. The second is an inference, is labelled as such throughout, and is the single largest
source of uncertainty in the short list.

**Inventory rebuilt live.**

| Layer | Records | Reaching a county | Coverage note |
|---|---|---|---|
| SMM firms (`sudokn`, NAICS 332xxx) | {{smm_firms_total}} | {{smm_firms_placed}} in {{smm_counties}} counties | employment on all; establishment year on {{firms_with_year}} ({{pct_firms_with_year}}%) |
| EPA-regulated facilities (`fiokg`, all six-digit NAICS 332xxx) | {{frs_facilities_332}} | {{frs_facilities_332}} in {{frs_counties_332}} counties | county FIPS native; per-industry tables use only the 36 codes `sudokn` shares |
| Software packages (`securechainkg`) | {{sw_packages}} | n/a | {{pypi_packages}} PyPI, {{cargo_packages}} Cargo, {{sw_ecosystems}} ecosystems |
| Dependency edges | {{sw_dep_edges}} | n/a | version→version |
| Vulnerabilities | {{sw_cves}} CVEs / {{sw_cwe_types}} CWE types | n/a | on {{sw_vuln_versions}} package versions |
| County SDoH variables (`spoke-okn`) | {{sdoh_variables}} | up to 3,192 counties | CHR + CDC/ATSDR SVI |

![Design and coverage](figures/fig1_design_and_coverage.png)

> ***Figure 1. Study design and record coverage (all six graphs).*** **(A)** How the three layers
> are joined: `sudokn`, `fiokg` and `securechainkg` share the NAICS 332xxx industry key; `sudokn` and
> `fiokg` additionally share geography (county FIPS via the ZIP5 crosswalk), which is what reaches
> `spatialkg`, `spoke-okn` and `ruralkg`. The dotted orange arrow marks the **missing** edge: nothing
> joins the software dependency graph to an industry code except a 20-name organisation bridge.
> **(B)** Records surviving into the analysis, log scale. Provenance: counts from the logged
> establishing queries against each named graph.

The figure makes the structural gap visible. The federation is well wired on geography and on
industry classification, and completely unwired between the dependency graph and everything else —
which is a fair machine-readable rendering of the disciplinary gap this study set out to cross.
Full specification, thresholds and join predicates are in
[Supply-Chain-Fragility_reproducibility.md](Supply-Chain-Fragility_reproducibility.md).

## 4. Confidence tiers

| Tier | Requirement | Industries |
|---|---|---|
| **A** | ≥100 firms placed in a county **and** concentration index ≥1.5 — the concentration claim rests on a substantial observed base | {{tierA}} |
| **B** | ≥40 firms placed **and** concentration index ≥1.3 — directionally sound, sample thin enough that the index could move | {{tierB}} |
| **C** | Below either threshold, or concentration at or under the sector norm — reported for completeness, not for action | {{tierC}} |

Tiers grade the **concentration** axis only, because that axis is measured end-to-end inside the
graphs. The software axis carries a separate, uniform caveat: its package-level components are
KG-grounded, its attachment to an industry is not. No industry in this study qualifies as
"both axes independently verified", and the report never claims one does.

## 5. Findings by axis

### 5.1 Where small and medium manufacturing capacity is, and how old it is

Fabricated metal manufacturing in `sudokn` is dominated by a long tail of very small shops.
**Machine shops (332710)** alone account for 5,262 firms and 85,375 recorded employees — a third of
the observed base — at a mean of 16 employees per firm. **Fabricated structural metal (332312)**
follows with 2,331 firms and 49,073 employees, then **sheet metal work (332322)** with 1,261 firms.
The largest single recorded establishment in any 332 industry has 497 employees, consistent with a
directory built around small and medium firms rather than plants.

Firm age is the weakest measurement in the study and must be read as such: only
**{{firms_with_year}} of {{smm_firms_total}} firms ({{pct_firms_with_year}}%)** record a year of
establishment. Within that 3.7% sample the modal founding decade is the **{{median_founding_decade}}**
(131 firms), with 104 in the 1980s and 98 in the 1990s, and a thin pre-war tail reaching 1852. The
honest statement is that the *recorded* subset skews toward firms founded in the last forty years;
whether that reflects the sector or reflects which firms maintain a website with a founding date on
it cannot be determined from these graphs.

![Manufacturing base](figures/fig2_manufacturing_base.png)

> ***Figure 2. The observed small and medium manufacturing base (sudokn).*** **(A)** The fourteen
> largest NAICS 332 industries by firm count (blue) with recorded employment scaled by 1/20 (yellow).
> **(B)** Founding-decade histogram for the {{firms_with_year}} firms that record
> `hasOrganizationYearOfEstablishment` — {{pct_firms_with_year}}% of the base, annotated on the panel.
> **(C)** Mean employees per firm, top fourteen industries. Provenance: `sudokn`
> `hasPrimaryNAICSClassifier`, `hasNumberOfEmployees`, `hasOrganizationYearOfEstablishment`.

Panels A and C together explain why "which industries are systemically important" cannot be answered
by firm counts: machine shops dominate the count but sit near the middle on employment per firm,
while forging, valve and pipe-fitting industries have far fewer firms at substantially larger average
scale — meaning fewer, larger, harder-to-substitute plants.

### 5.2 Which industries are geographically concentrated enough that one county failing takes the sector

After the sample-size correction, seven industries are at least twice as clustered as the sector norm.
**Industrial valve manufacturing (332911)** is the outlier: 120 placed firms with a concentration
index of **3.68** and an effective breadth of **18.5 counties**, of which Harris County, Texas alone
holds **18.3%** of all observed firms. **Fluid power valve and hose fitting (332912)** follows at
2.70 (16.9 effective counties), then **fabricated pipe and pipe fitting (332996)** at 2.55, **metal
heat treating (332811)** at 2.53, and **other metal valve and pipe fitting (332919)** at 2.23. At the
other end, machine shops (0.85), fabricated structural metal (0.89) and metal coating (0.91) are
*less* concentrated than chance — they are everywhere, which is exactly why a single county failing
would not take them with it.

![Geographic concentration](figures/fig3_geographic_concentration.png)

> ***Figure 3. Geographic concentration of NAICS 332 industries (sudokn × fiokg × spatialkg).***
> **(A)** Concentration index (observed ÷ expected county HHI) against the observed firm base, log
> x-axis; dashed line = sector-typical (1.0), dotted = the concentrated threshold (1.5); short-listed
> industries in orange. **(B)** Effective number of counties (1 ÷ county HHI) for the fourteen
> narrowest industries, with the whole-sector value ({{eff_counties_sector}}) marked. **(C)** County-
> against state-grain HHI, log–log; the dashed identity line shows that every industry is more
> concentrated at county than at state grain, i.e. clustering is metropolitan, not regional.
> Provenance: `sudokn` NAICS + ZIP5, joined to county FIPS via the `fiokg`-derived crosswalk, labelled
> from `spatialkg`.

Panel C carries a methodological warning worth stating plainly: every point sits below the identity
line, so a state-level concentration analysis — the grain most industrial-policy work uses —
systematically *understates* how narrow these industries are. The valve cluster looks like a Texas
story at state grain and a Houston story at county grain.

### 5.3 Where the regulated industrial footprint sits, and where it decouples from employment

The EPA facility registry sees a different shape of the same sector. **Electroplating and anodizing
(332813)** is the single largest regulated footprint — 3,874 facilities across 834 counties — despite
ranking fifth by firm count, because plating is a permitted, monitored process wherever it happens.
Cook County (IL) leads on absolute facility count with 647 NAICS-332 facilities spanning 41 of the 36
industries' permit categories, then Harris (TX, 451) and Maricopa (AZ, 324).

Absolute counts, however, mostly measure county population. Two scale-free intensity measures give a
different and more useful list. By **NAICS-332 share of the county's entire regulated industrial
base**, the leaders are Rogers County OK (10.4%), Brooke County WV (8.9%) and Elk County PA (7.4%) —
places where fabricated metal *is* the industrial base. By **facilities per 100,000 residents**,
Brooke County WV (133), Elk County PA (94, RUCC 7) and Ouachita County AR (80, RUCC 7) lead, and the
list turns visibly rural.

![Intensity map](figures/fig4_intensity_map.png)

> ***Figure 4. Counties most intensively dependent on fabricated-metal manufacturing (fiokg ×
> ruralkg × spoke-okn).*** Coloured points: the 45 counties with ≥20 NAICS-332 facilities, ranked by
> facilities per 100,000 residents (colour and size); grey points: all {{frs_counties_332}} counties
> hosting at least one NAICS-332 facility, which render the coastline and the Plains gap. Coordinate
> source: county centres computed as the mean of `spoke-okn` ZIP centroids for the ZIPs the
> `fiokg`-derived crosswalk assigns to that county; population and RUCC from `ruralkg`.
> **Basemap note:** OpenStreetMap raster tiles are unreachable from the analysis sandbox, so the
> static basemap is built from the federation's own county coverage; the HTML report carries a
> genuine OSM-tiled interactive version of the same data in §6.4.

The map shows the intensity leaders sitting in a band from western Pennsylvania and the Ohio Valley
through Michigan and Wisconsin into Minnesota, with satellite clusters in Oklahoma and south
Louisiana — the classic metal-fabrication belt, plus the oilfield-equipment corridor.

The burden-versus-employment question has a real answer and a real confound. At state grain,
Illinois carries 1,428 NAICS-332 regulated facilities against only 187 observed `sudokn` firms;
Connecticut 801 against 56; Florida 842 against 170; Georgia 479 against 97. Ohio, by contrast,
shows 1,649 facilities against 1,499 firms and Texas 1,480 against 1,848. Read naively this says
Illinois and Connecticut bear industrial burden without capturing the employment. **The more likely
explanation is `sudokn` coverage**: Illinois and Connecticut are major fabricated-metal states in
every official statistic, and a web-crawled directory under-samples them. This is reported as a
**data-coverage finding, not an economic one** — and it is a useful one, because the same ratio is
the natural screening statistic once employment data with uniform coverage is substituted.

![Burden vs employment](figures/fig5_burden_vs_employment.png)

> ***Figure 5. Regulated footprint against recorded employment, by state (fiokg × sudokn ×
> spatialkg).*** **(A)** EPA NAICS-332 facilities against `sudokn` recorded SMM employment, log
> x-axis, with a log-linear fit; states far above the line carry facilities without recorded
> employment. **(B)** The ratio — facilities per 1,000 recorded SMM employees — for the eight lowest
> and eight highest states. Provenance: `fiokg` records → facility → `kwg:sfWithin` county FIPS,
> rolled to state by FIPS prefix and labelled via `spatialkg` `AdministrativeRegion_1`; employment
> from `sudokn` `hasNumberOfEmployees`.

Panel B should be read as a coverage diagnostic first and an economic one second: the orange tail
(Idaho, Colorado, Delaware, Connecticut, Illinois, Georgia, Florida, California) is dominated by
states where `sudokn` sees few firms, and the green tail (Texas, Michigan, Wisconsin, Ohio,
Pennsylvania, Minnesota) by states where it sees many.

### 5.4 How fragile the software layer is

`securechainkg` describes a dependency graph with the classic scale-free hazard: **numpy** is a direct
dependency of **{{numpy_dependents}}** distinct packages, **{{numpy_dependent_pct}}%** of the entire
{{sw_packages}}-package graph, and it is the *direct* in-degree — the transitive figure is larger
still. **requests** ({{requests_dependents}}), **pandas** ({{pandas_dependents}}), **serde**
(33,531, Cargo) and **matplotlib** (28,959) complete a top five on which effectively every Python or
Rust build rests.

Vulnerability load and blast radius are only loosely coupled, which is what makes a combined score
worth computing. **django** carries 120 recorded CVEs across 371 vulnerable versions; **pillow** 55
CVEs across 935 vulnerable versions out of 953; **aiohttp** 13; **urllib3**, **opencv-python** and
**cryptography** 12 each. Meanwhile the highest-blast packages carry modest CVE counts — numpy 8,
requests 6, pandas 1 — so a pure-CVE ranking misses the hubs and a pure-in-degree ranking misses the
loaded packages. On the combined score the top five are **requests** (90.3), **numpy** (89.2),
**pillow** (86.7), **pyyaml** (85.0) and **pandas** (83.1).

Two axes the question asked for are **not answerable from this graph and are reported as gaps rather
than as zeros**. Maintenance thinness is effectively absent: only **{{sw_pkgs_with_contributors}} of
{{sw_packages}} packages ({{pct_pkgs_with_contributors}}%)** carry any `schema:contributor` data, and
that slice is a disjoint set of GitHub-hosted C/C++ projects (flatbuffers, llama.cpp, xgboost, ceph,
grpc …) with contributor counts rounded to the nearest hundred; not one of the high-blast PyPI or
Cargo hubs has a contributor record. Licensing is present but sparse and locally wrong — matplotlib
is recorded as AGPL-3.0-only, which it is not. What licensing *can* support is a restrictive-licence
inventory: the highest-blast copyleft package is **pyqt5** (GPL-3.0) with {{copyleft_top_blast}}
downstream dependents, followed by pylint, pyfiglet, pyside6, pymupdf and gensim — a real
compliance-and-substitutability exposure independent of any CVE.

![Software fragility](figures/fig6_software_fragility.png)

> ***Figure 6. Package-level fragility in the dependency graph (securechainkg).*** **(A)** The
> twenty largest blast radii — distinct downstream packages depending on the named package — coloured
> by ecosystem. **(B)** Blast radius against recorded CVE count, log–log, marker size proportional to
> the combined fragility score; the nine highest-scoring packages are labelled. **(C)** The twelve
> highest-blast packages carrying a copyleft licence, annotated with the licence family. Provenance:
> `securechainkg` `hasSoftwareVersion` / `dependsOn` for in-degree, `vulnerableTo` for CVEs,
> `schema:license` for licences.

Panel B is the argument for a combined index: the upper-left region (high blast, few CVEs) and the
lower-right (few dependents, many CVEs) are both under-prioritised by single-axis triage, and the
packages that matter most — pillow, jinja2, urllib3, aiohttp — sit in neither corner.

### 5.5 Who lives in the manufacturing counties

The population layer gives two defensible answers depending on how "manufacturing county" is
operationalised, and reporting only one would misrepresent the evidence.

**By facilities per 100,000 residents**, the high-intensity tier (669 counties) is **56.7% rural**
against 37.3% in the low tier, **20.0% aged 65+** against 18.5%, and thinner on services — 2,634
residents per primary care physician against 2,282, 1,334 per mental health provider against 973,
81.2% broadband access against 84.1%. Health behaviour and injury run adverse: **+11% injury deaths**,
**+12% adult smoking**, **+14% drug overdose deaths**, **+7% adult obesity**. But the composite
**CDC SVI is 24% lower** and severe housing problems 24% lower, unemployment 16% lower and the
uninsured rate 13% lower. Civic density is higher (social associations +32%).

**By the sector's share of the county's regulated industrial base**, the gradient becomes monotonic
across all three tiers and unambiguously adverse on outcomes: life expectancy **76.0 vs 77.4 years**,
premature age-adjusted mortality **+13%**, poor-or-fair health **+5%**, preventable hospital stays
**+9%**, frequent mental distress **+8%**, injury deaths **+13%**, drug overdose deaths **+26%**,
adult smoking **+12%**, PM2.5 **+3%** — while housing affordability, unemployment and insurance
coverage remain *better* than in marginal counties.

![Population gradient](figures/fig7_population_gradient.png)

> ***Figure 7. County health, service and civic indicators by manufacturing intensity (fiokg ×
> ruralkg × spoke-okn).*** Both panels show the percentage difference of each tier's mean from the
> lowest-intensity tier, diverging colour scale centred at zero. **(A)** Tiers defined by NAICS-332
> facilities per 100,000 residents (high ≥15, mid 5–15, low <5). **(B)** Tiers defined by the
> NAICS-332 share of the county's regulated facility base (dependent ≥2%, moderate 0.8–2%, marginal
> <0.8%). Each variable is annotated `[+ = worse]`, `[+ = better]` or `[context]` because the
> indicators do not share a polarity — "primary care physicians" and "mental health providers" are
> *population per provider*, so higher is worse. n per tier is in the workbook; counties without a
> `spoke-okn` match are dropped per variable. Provenance: `spoke-okn` `PREVALENCEIN_SpL` reified
> statements (County Health Rankings and CDC/ATSDR SVI), keyed on county FIPS.

The interpretation that survives both operationalisations is narrow and worth stating precisely:
**fragility geography aligns with a health-and-access vulnerability, not with a
socioeconomic-deprivation vulnerability.** These are working counties with jobs, insurance and
affordable housing whose residents die earlier, smoke more, overdose more and have fewer clinicians
within reach. A screening tool built on composite social vulnerability — the standard instrument for
targeting resilience investment — would rank them as *low* priority, and would be wrong for the
reason that composite indices average deprivation with the very employment that these counties still
have.

## 6. Domain analyses

Six analyses were available for this design. Five were **run**: geographic concentration (§5.2),
regulated-burden decoupling (§5.3), package-level dependency fragility (§5.4), the industry↔software
attachment (§6.3), and the county population gradient (§5.5). One was **deliberately skipped**:
transitive dependency-closure depth per package, because reachability over
{{sw_dep_edges}} edges exceeds the endpoint's query budget — direct in-degree is used throughout and
is a strict lower bound on blast radius.

### 6.1 The manufacturing-relevant slice of the dependency graph

Twenty-six packages covering CAD exchange, mesh and metrology, serial and fieldbus links, and PLC
protocols were profiled. They are individually tiny by dependency-graph standards — **pymodbus** has
151 dependents, **ezdxf** 60, **cadquery** 29, **asyncua** 22, **pylogix** 7, **pyads** 2 — and
several carry CVEs: **opcua** and **asyncua** three each, **scapy** and **vtk** one each,
**opencv-python** twelve. The important number is not their own blast radius but their **upstream
exposure**: **{{industrial_pkgs_hub_exposed}} of {{industrial_pkgs_checked}}** depend directly on one
of the same handful of hubs. `open3d` pulls in eight of them (pandas, tqdm, scikit-learn, pillow,
numpy, pyyaml, matplotlib, setuptools); `pyvista` four; `pymodbus` three (pyserial, six, setuptools);
`ezdxf`, `ifcopenshell`, `trimesh`, `meshio`, `numpy-stl` and `shapely` all rest on numpy.

![Industrial stack](figures/fig8_industrial_stack.png)

> ***Figure 8. The industrial software slice and the hardware CVE bridge (securechainkg).***
> **(A)** The 26 profiled CAD / metrology / fieldbus / PLC packages by blast radius (log x-axis),
> orange where the package depends directly on a top-blast hub, annotated with recorded CVE counts.
> **(B)** Recorded CVEs on the hardware products of the {{hardware_bridge_names}} organisations that
> bridge to a NAICS code by name, log x-axis; orange = NAICS 332 (in study scope). Provenance:
> `securechainkg` `dependsOn` and `vulnerableTo`; the NAICS attachment is the organisation-name
> bridge described in §6.3.

Panel A closes the loop the study was built to close: the shop-floor software layer is not a separate
ecosystem with its own risk profile. It is a thin veneer of protocol adapters sitting on the same five
or six packages as everything else, so a compromise or a breaking change in numpy, setuptools or
pyserial propagates into CAD-to-CNC and PLC-polling toolchains by the same path it reaches a web
service.

### 6.2 The hardware CVE bridge — real, and very thin

The only industry↔vulnerability path that exists as graph structure runs
NAICS → organisation name → hardware product → CVE. It works, and it is small: **{{hardware_bridge_names}}
normalised organisation names** match between `securechainkg`'s NAICS-classified manufacturer slice
and its hardware-vendor slice, reaching {{hardware_bridge_naics}} NAICS/vendor pairs and
{{hardware_bridge_hw}} hardware products. The load is dominated by information-technology codes —
HP (NAICS 334111) with 903 CVEs across 19,194 hardware versions, Western Digital (334112) with 64 —
but the industrial-control vendors are exactly the ones a manufacturing analyst would want: **Rockwell
Automation (335314) with 109 CVEs spanning 47 CWE types**, **ABB (335313) with 87 CVEs / 50 CWE
types**, **Johnson Controls (333415, 336360) with 16**, Trane (333415) with 4, Vertiv (335314) with 4.
Inside NAICS 332 itself the bridge reaches only Baxter and GE HealthCare (both 332710, 25 and 10 CVEs
on medical hardware), Avery Dennison (332999, 1) and General Dynamics (332994, 0).

Graph-wide, hardware carries **{{hw_cves}} distinct CVEs across {{hw_vuln_versions}} vulnerable
hardware versions** — a comparable order of magnitude to the software side — so the bridge's
narrowness is a *linkage* limitation, not a data limitation. The conclusion this supports is about
the automation vendors that every fabricated-metal plant buys from, not about the plants: an
industrial-valve or heat-treating shop does not appear in the graph, but the Rockwell and ABB
controllers on its floor do.

### 6.3 Attaching industry to software: the labelled inference

Because no edge exists, each of the 36 industries was mapped by hand from its NAICS process
definition to the packages that process needs — G-code and CAD exchange for machining, OPC-UA and
S7/ADS polling for furnace and bath recipe control, machine vision for inspection, mesh and FEA I/O
for pressure vessels. The industry software-fragility score then sums, with fixed weights, the count
of distinct OT/PLC-facing packages, their recorded CVEs, their hub exposure, and a bonus where the
§6.2 hardware bridge fires.

The ranking that results is led by **electroplating (332813, score 100)** — six OT-facing packages,
18 recorded CVEs in its stack, continuous recipe-driven bath and rectifier control — then **metal
coating (332812, 93.9)**, **machine shops (332710, 81.6)**, **small-arms ammunition (332992, 72.4)**
and **metal can (332431, 72.4)**. This mapping is the study's weakest link and it is deliberately
transparent: the weights are arbitrary within an order of magnitude, the package sets are defensible
but not unique, and a different analyst would produce a correlated but not identical ranking. What the
mapping cannot be is *hidden* — it is enumerated in full in the reproducibility record so that a
reader who disagrees can substitute their own and re-run.

### 6.4 Interactive map of the exposed counties

The counties named in §5.3 and §7, on OpenStreetMap tiles, every marker clickable for its
facility count, per-capita intensity, RUCC and population.

<!-- INTERACTIVE_MAP -->

> ***Interactive map. NAICS-332 intensity leaders (fiokg × ruralkg × spoke-okn).*** Marker radius
> scales with facilities per 100,000 residents; click any marker for the county's facility count,
> population, RUCC class and intensity. Coordinate source: mean `spoke-okn` ZIP centroid over the
> ZIPs assigned to that county by the `fiokg`-derived crosswalk. Basemap © OpenStreetMap
> contributors.

## 7. Discussion

The single most useful result is a negative one. **Geographic concentration and software fragility
are weakly *anti*-correlated across these industries (ρ = {{spearman_conc_vs_sw}}).** Electroplating
and metal coating — the most automation-dependent, most CVE-exposed processes — are also the most
geographically diffuse, with 94 and 144 effective counties respectively; industrial valve and fluid
power manufacturing — the narrowest geographies in the sector, 18 and 17 effective counties — sit in
the middle of the software distribution. This is why the two literatures do not meet: each one's
worst cases are the other one's unremarkable middle, so neither's top-ten list contains the
industries that are moderately bad on both.

The joint ranking recovers those industries. **Metal heat treating (332811)** tops it: tier A,
concentration index 2.53 (32 effective counties), five OT-facing packages including S7 and ADS
furnace control, six recorded CVEs in that stack. **Iron and steel forging (332111)** is second
(index 2.15, 38 effective counties, twelve stack CVEs, mean 38 employees per firm — the largest
average scale in the short list). **Bolt, nut, screw, rivet and washer (332722)** is third, and
matters out of proportion to its size because it is a fastener supplier to everything else.
**Industrial valve (332911)** is fourth on joint risk but first on concentration, and is the clearest
single-point-of-failure candidate in the sector: 18.3% of all observed US firms in one county.

The geography of who absorbs it is startlingly narrow. **Harris County, Texas** is a top cluster in
{{harris_industries}} of the fourteen candidate industries examined, holding 22 of 120 observed
industrial-valve firms, 19 of 187 pipe-fitting firms, 21 of 571 electroplaters and 15 of 170 forging
firms — {{harris_firms}} firms and 3,963 recorded jobs in the candidate set alone. Cuyahoga County OH
appears in five, the three Detroit-area counties (Macomb, Wayne, Oakland) in four each, then Maricopa
AZ, Tulsa OK, Erie PA, Monroe NY and Kent MI. A disruption to valve or pipe-fitting capacity is, in
the first instance, a Houston event; a disruption to heat treating, precision turning or fasteners is
a Detroit-and-Cleveland event.

**What follows for practice.** Three actions are supported at different confidence. *Strongly
supported:* the concentration screen itself — county-grain, sample-corrected — should replace
state-grain screening in industrial-resilience work, because Figure 3C shows state grain understates
narrowness for every industry in the sector. *Moderately supported:* dependency-hub hardening
(numpy, requests, pandas, setuptools, pyserial, pillow) is the highest-leverage software intervention
for manufacturing, because {{industrial_pkgs_hub_exposed}} of {{industrial_pkgs_checked}} shop-floor
packages rest directly on those hubs — this rests on KG-grounded package data with an inferred
industry attachment. *Suggestive only:* the industry short list's ordering, which would move if the
process-technology mapping in §6.3 changed.

**Testable predictions.** (1) Substituting Census County Business Patterns employment for `sudokn`
employment should preserve the concentration ranking of §5.2 while eliminating the Illinois /
Connecticut anomaly of §5.3 — if it does not, the concentration finding is a coverage artefact too.
(2) The short-listed industries should show higher-than-baseline rates of CISA ICS advisories
affecting equipment classes they operate, an independently checkable prediction against the KEV and
ICS-advisory catalogues. (3) The §5.5 health gradient should strengthen when intensity is measured
with employment rather than facility counts, because facility counts weight permitting intensity
rather than headcount.

## 8. Comparison with prior work

Claims were checked against the primary literature retrieved through the **PubMed** MCP connector for
the occupational- and community-health results, and against current supply-chain security reporting
and CISA advisories retrieved by web search for the software results. The Paperclip connector was
available but not required, as no claim depended on paywalled full text. The complete per-claim record
with citations is in `Supply-Chain-Fragility_literature_comparison.md`.

| # | Claim | Concordance |
|---|---|---|
| 1 | A handful of packages (numpy, requests, pandas) are direct dependencies of a large fraction of an entire ecosystem, making dependency count the real attack surface | **SUPPORTED** — the 2026 industry reporting independently documents the same structure, with ~95% of open-source vulnerabilities residing in transitive rather than direct dependencies and registry traffic driven by dependency sprawl [7][8] |
| 2 | Vulnerability load and blast radius are only loosely coupled, so single-axis triage misses the packages that matter | **SUPPORTED** — matches the transitive-dependency blind-spot analyses, which argue explicitly that direct-dependency scanning misprioritises [8] |
| 3 | A compromise in a high-blast-radius package propagates into industrial toolchains by the same path it reaches web services | **SUPPORTED** — the Shai-Hulud npm worm (Sept 2025) and its Shai-Hulud 2.0 variant (Nov 2025–2026) demonstrated exactly this self-propagating registry path, backdooring 796 packages with >20M weekly downloads; CISA issued an ecosystem-wide alert [9][10][11] |
| 4 | Industrial-control vendors reachable through the hardware bridge — Rockwell Automation (109 CVEs), ABB (87), Johnson Controls (16) — carry the manufacturing sector's concentrated equipment risk | **SUPPORTED** — CISA's 2026 ICS advisories name these same three vendors repeatedly, and its July 2026 advisory update specifically addresses malicious modification of reusable code modules in Rockwell PLC programs across US critical manufacturing [12][13] |
| 5 | Small and medium manufacturers are the weak link in the industrial software supply chain | **SUPPORTED** — CMMC readiness reporting finds small firms, >70% of DoD suppliers, materially behind on the 110 NIST 800-171 controls as Phase 2 approached [14] |
| 6 | Electroplating (332813) is the most software- and automation-exposed 332 industry | **NOVEL** — no prior source ranks fabricated-metal sub-industries by software dependency exposure; this is the study's own construction and rests on the labelled inference of §6.3, not on a graph edge |
| 7 | Geographic concentration and software fragility are anti-correlated across these industries | **NOVEL** — no prior work joins the two axes; no source found |
| 8 | Electroplating and anodizing workers face elevated cancer risk from nickel and hexavalent chromium exposure, making 332813's large regulated footprint a community-health as well as a supply-chain concern | **SUPPORTED** — a 2,991-worker Italian electroplater cohort found nickel exposure significantly increased lung, rectal and kidney cancer mortality even below the occupational limit [1]; the 14-study SYNERGY pooled analysis (16,901 cases) found ORs of 1.32 for Cr(VI) and 1.29 for nickel in the highest exposure quartile [2] |
| 9 | Welding- and fabrication-intensive industries carry a distinctive neurological hazard consistent with the elevated injury and health burden in §5.5 | **PARTIALLY SUPPORTED** — 78 probable/possible occupational manganism cases are documented among welding-exposed workers, but the review concludes the epidemiological link to Parkinson's disease specifically remains controversial [3] |
| 10 | Machine shops (332710), the sector's largest industry by firm count, expose workers to a documented respiratory and cancer hazard | **SUPPORTED** — the post-1998 metalworking-fluid evidence review identified three major studies showing excess lung, liver, pancreatic and laryngeal cancer and leukaemia, and strengthened asthma and hypersensitivity-pneumonitis associations, at prevailing exposure levels [4] |
| 11 | Counties where fabricated-metal manufacturing dominates the regulated industrial base show elevated drug-overdose mortality (+26%) | **CONTRADICTED** — a county-level analysis of 2018–2021 overdose mortality found a *negative* association between manufacturing job share and overdose deaths, with positive associations for arts/entertainment and public administration instead [5]. The divergence is discussed below |
| 12 | Manufacturing-intensive counties carry excess working-age mortality attributable to the industrial economy | **PARTIALLY SUPPORTED** — the causal evidence attaches to manufacturing *decline* rather than manufacturing presence: each additional robot per 1,000 workers produced ~8 excess deaths per 100,000 men aged 45–54, and automation explained ~12% of the rise in working-age overdose mortality [6] |
| 13 | Maintenance thinness can be assessed for the packages that matter | **CONTRADICTED** — by the graph's own contents: only {{sw_pkgs_with_contributors}} of {{sw_packages}} packages ({{pct_pkgs_with_contributors}}%) carry contributor data, and that slice is disjoint from the dependency hubs; the axis the question asked for is unmeasurable here. No external source is at issue — this is a KG data-quality finding |

Claims 1–5 and 8–12 were checked against abstracts and, for claims 1, 3 and 4, against the full text
of the vendor and agency advisories; no claim required paywalled full text, so no entry is marked
full-text-verified.

**Where the KG evidence diverges from the literature.** Two divergences are *scope*, one is a
*graph error*, and one is a genuine contradiction that should change how the finding is read.
Claim 11 is the contradiction: Oh et al. measure manufacturing as a **share of employment** across
all manufacturing, while this study measures fabricated metal as a **share of the county's regulated
facility base** — a permitting-intensity measure that upweights small, dirty, rural operations. Both
can be true (manufacturing employment protective, fabricated-metal permitting intensity adverse), but
the finding must not be reported as "manufacturing counties have more overdoses"; §5.5's per-capita
operationalisation, which shows a weaker +14%, is the more conservative reading and the one the
discussion relies on. Claim 12 is a scope divergence in the same direction: the causal literature
identifies deindustrialisation, not industry, as the mortality driver, so §5.5's cross-section cannot
distinguish "these places are unhealthy because of the work" from "these places retained the work
because they had nothing else". Claim 9 is a scope divergence within the health literature itself. The
graph error is separate and internal: `securechainkg` records **matplotlib** as `AGPL-3.0-only`, which
is wrong (matplotlib uses a PSF-derived BSD-style licence), so the §5.4 copyleft inventory excludes it
and any licence-based conclusion from this graph needs independent verification.

## 9. Full ranked results

The complete ranking of all {{smm_industries}} industries — firm and employment counts, both
concentration measures at three geographic grains, software-fragility components, evidence tier and
short-list flag — is in **Supply-Chain-Fragility_results.xlsx** (`Ranked Results` sheet) and in
`data/industry_master.csv`. Supporting extracts for every panel are in `data/`.

<!-- RESULTS_TABLE -->

The short list, in joint-risk order:

| Rank | NAICS | Industry | Firms placed | Recorded jobs | Concentration index | Effective counties | Software score | Tier |
|---|---|---|---|---|---|---|---|---|
| 1 | 332811 | Metal heat treating | 166 | 4,555 | 2.53 | 31.9 | 57.1 | A |
| 2 | 332111 | Iron & steel forging | 170 | 7,632 | 2.15 | 37.9 | 57.1 | A |
| 3 | 332722 | Bolt, nut, screw, rivet & washer | 118 | 3,664 | 1.99 | 33.8 | 55.1 | A |
| 4 | 332911 | Industrial valve | 120 | 4,116 | 3.68 | 18.5 | 43.9 | A |
| 5 | 332912 | Fluid power valve & hose fitting | 64 | 2,379 | 2.70 | 16.9 | 43.9 | B |
| 6 | 332996 | Fabricated pipe & pipe fitting | 187 | 7,022 | 2.55 | 33.3 | 43.9 | A |
| 7 | 332813 | Electroplating, plating, anodizing | 571 | 14,026 | 1.30 | 93.9 | 100.0 | B |
| 8 | 332721 | Precision turned product | 191 | 6,324 | 1.34 | 63.9 | 61.2 | B |

![Intersection](figures/fig9_intersection.png)

> ***Figure 9. The intersection of both fragility axes (all six graphs).*** **(A)** Concentration
> index against industry software-fragility score for the {{eligible_industries}} industries with ≥60
> placed firms; dotted lines mark the concentrated threshold (1.5) and the software upper-tertile
> ({{conc_q67}}); short-listed industries in orange and labelled. **(B)** The joint-risk ranking
> (concentration percentile × software percentile × 100), top twelve, annotated with evidence tier.
> Provenance: concentration from `sudokn` × `fiokg` × `spatialkg`; software score from
> `securechainkg` with the §6.3 process-technology mapping.

Panel A is the whole argument in one frame. The upper-left quadrant (concentrated, low software
exposure) is what an economic-resilience study would flag; the lower-right (diffuse, high software
exposure) is what a security study would flag; the short list is drawn from the sparsely populated
middle that neither would reach.

![Short-list counties](figures/fig10_shortlist_counties.png)

> ***Figure 10. Which counties inherit the short-listed industries (sudokn × fiokg × spatialkg).***
> **(A)** Firm counts by candidate industry (columns, `*` = short-listed) and exposed county (rows,
> ordered by total), for counties holding at least five firms in an industry (eight for 332813 and
> 332618). **(B)** Counties ranked by how many candidate industries they are a top cluster in,
> annotated with total firms and recorded jobs. Provenance: `sudokn` firms placed in counties via the
> `fiokg`-derived ZIP5 crosswalk, labelled from `spatialkg`.

Panel B is the operational output: nine counties account for the top clusters of every short-listed
industry, and one of them — Harris County — appears in {{harris_industries}}.

## 10. Summary of findings & limitations

**Findings recap.** Across {{smm_industries}} fabricated-metal industries, {{smm_firms_total}} small
and medium manufacturers ({{smm_emp_total}} recorded jobs), against a sector-wide
{{frs_facilities_332}} EPA-regulated facilities in {{frs_counties_332}} counties, seven industries are at least twice as geographically
clustered as the sector norm — led by industrial valve manufacturing, where one county holds 18.3% of
all observed US firms and the effective national breadth is 18 counties. Twelve industries fall in
the high tertile of software fragility, led by electroplating. The two sets barely overlap
(ρ = {{spearman_conc_vs_sw}}), which is the structural reason the economic and cybersecurity
literatures do not converge, and the short list of **{{shortlist_n}} industries** must therefore be
built from a joint rank rather than a conjunction. Underneath it all, {{industrial_pkgs_hub_exposed}}
of {{industrial_pkgs_checked}} shop-floor CAD, metrology and PLC packages depend directly on the same
few hubs — numpy above all, with {{numpy_dependents}} direct dependents, {{numpy_dependent_pct}}% of
an {{sw_packages}}-package graph.

The counties that would absorb a failure are few and named: Harris (TX), Cuyahoga (OH), Macomb, Wayne,
Oakland and Kent (MI), Maricopa (AZ), Tulsa (OK), Erie (PA), Monroe (NY). They are more rural and
older than the country, thinner on clinicians and broadband, and worse on life expectancy, premature
mortality, smoking, injury and overdose death — while being *better* on employment, insurance and
housing cost, so that a composite social-vulnerability screen ranks them low. **Strongly supported**
by these data: the concentration ranking at county grain, the dependency-hub structure, and the
health-versus-deprivation divergence. **Suggestive only**: the industry-level software scores and
therefore the short list's ordering, which rest on a 26-package process-technology mapping the analyst
supplied; and every burden-versus-employment comparison, which is confounded by `sudokn` coverage.

**Limitations.**

1. **`sudokn` is a web-crawled directory, not a census.** It sees 187 fabricated-metal firms in
   Illinois against 1,428 EPA-regulated facilities. Every cross-state comparison of employment, and
   the whole of §5.3's burden-to-employment ratio, is confounded by this. Within-industry
   concentration is less exposed, because the sampling bias would have to be industry-specific to
   move it, but it is not immune.
2. **Firm age is essentially unmeasured.** {{pct_firms_with_year}}% of firms record a founding year.
   The §5.1 decade distribution describes that 3.7%, not the sector.
3. **The software layer is not joined to industry by any edge.** The §6.3 mapping is an analyst
   inference with arbitrary weights; the §6.2 hardware bridge is real but rests on
   {{hardware_bridge_names}} organisation-name matches and reaches only four NAICS 332 firms. Any
   industry-level software conclusion is one substitution away from changing.
4. **Maintainer thinness could not be measured at all.** {{pct_pkgs_with_contributors}}% package
   coverage, on a disjoint slice. The question was asked and the honest answer is that this graph
   cannot support it.
5. **Licence data is sparse and contains at least one confirmed error** (matplotlib recorded as
   AGPL-3.0-only). The copyleft inventory is a lower bound and needs independent verification.
6. **Blast radius is direct in-degree, not transitive closure.** Transitive reachability over
   {{sw_dep_edges}} edges exceeded the endpoint budget. All blast-radius figures are lower bounds,
   and the ratio between direct and transitive exposure is not uniform across packages, so the
   *ranking* could shift as well as the magnitudes.
7. **The ZIP5→county crosswalk drops ambiguous ZIPs.** 15% of firms are unplaced — those in ZIPs
   straddling a county line or hosting no NAICS-33 facility. Firms in multi-county ZIPs are
   systematically urban-fringe, so county-grain concentration may be slightly overstated.
8. **County health indicators are cross-sectional and ecological.** They describe county
   populations, not manufacturing workers. Nothing here supports an individual-level or occupational
   attribution, and the causal literature (§8, claim 12) attributes excess mortality to industrial
   *decline* rather than industrial presence.
9. **CVE counts reflect disclosure, not risk.** django's 120 CVEs partly reflect scrutiny; a
   package with none may simply be unexamined. The §5.4 score inherits this asymmetry.
10. **Facility counts are permits, not plants or output.** A county with many small permitted
    platers scores above one with a single large plant of equivalent capacity, which is why the
    per-capita and share measures of §5.5 disagree in places.
11. **Coverage is the 48 contiguous states plus DC.** `spatialkg` does not load Alaska, Hawaii or the
    territories, so firms and facilities there are absent from all county-grain results.
12. **Graph snapshots differ in age by five months** (`fiokg` 2026-03-18 to `ruralkg` 2026-06-08),
    and `ruralkg`'s population and RUCC values are 2013 vintage. Rates computed across them mix
    reference periods.

## 11. Reproducibility

Everything needed to replicate this analysis — the originating prompt verbatim, the replicator
specification (selection rules, thresholds, join predicates, the full §6.3 process-technology
mapping, verified quantities and limitations), every supporting SPARQL query verbatim with its row
count, and the pinned knowledge-graph versions and timing — is in
[Supply-Chain-Fragility_reproducibility.md](Supply-Chain-Fragility_reproducibility.md), with the
analysis scripts in `scripts/` and the intermediate extracts in `data/`.

## 12. References

Occupational- and community-health references retrieved via the **PubMed** MCP connector.
Supply-chain security and regulatory references retrieved by web search of vendor, agency and
industry sources.

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
15. OKN federated SPARQL endpoint, accessed via the `mcp-okn` MCP server, 2026-07-29. Knowledge-graph versions as pinned in §2.

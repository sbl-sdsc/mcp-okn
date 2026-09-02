# Proto-OKN entity types, ontologies, and unexplored crosswalks

_Survey date: 2026-06-14 · 41 served KGs · federation endpoint
`https://apps.okn.us/federation/sparql`_

> **Dated snapshot — three findings below are superseded (2026-09-01).** This page is
> kept as the 2026-06-14 survey, not rewritten. Since then: (1) **medical-device-kg is
> no longer an island** — the v0.0.3 redeploy (2026-07-28) added establishment,
> facility, applicant and recalling-firm addresses, so it joins the ZIP5 cluster on five
> pairs (J7–J11); (2) **biomarkerkg's non-protein axes are now catalogued** — the class
> lists that timed out here hide 147,386 dbSNP variants, 201 PubChem gene IRIs (whose
> GID number is the Entrez id), 63 PubChem compounds and 53 UBERON sample sources,
> yielding C18–C21, AN7 and V1; (3) a **new KG, nestkg**, is served (43 KGs now) and
> joins the UniProt cluster (G5–G8) and the MONDO axis (A30). See
> `metadata/crosswalks.json` for the current table.

**What this is.** An exhaustive sweep of the entity types and ontologies/identifier
schemes carried by every served Proto-OKN KG, cross-referenced against the curated
crosswalk table (`metadata/crosswalks.json`) to find **crosswalks that have not yet
been explored** — KG pairs that share an identifier scheme but appear in neither
`verified_crosswalks` nor `known_non_joins`/`islands`.

**Method.** Per-KG ontology presence was probed live with bounded SPARQL (LIMIT-sampled
class lists, distinct predicates, and the objects of `rdfs:seeAlso` / `owl:sameAs` /
`skos:exactMatch` / `oboInOwl:hasDbXref` / biolink `object`/`subject`/`in_taxon`), then
**merged** with each KG's authoritative crosswalk-table participation. Headline claims
were spot-checked with COUNT queries (see §D). **Caveat:** live detection is sampled, so
*absence* of a signal is not proof of absence; *presence* of the ranked candidates below
was verified.

---

## A. Coverage today (what is already mapped)

The table maps ~22 identifier dimensions across these clusters:

| Cluster | Keys | Hub / mechanism |
|---|---|---|
| Disease & phenotype | MONDO, DOID, HP, OMIM, Orphanet, MeSH | `oard-kg` MONDO/HP hub; ubergraph DOID→MONDO / OMIM / Orphanet bridges |
| Genes | Ensembl, NCBI Gene (Entrez), HGNC | bare-id rebuild; HGNC→Entrez via wikidata |
| Proteins | UniProt | direct |
| Chemicals | CAS, CHEBI, PubChem CID | direct / ubergraph CHEBI |
| Taxonomy | NCBITaxon | ubergraph `subClassOf*` hub (6 members) |
| Geospatial | county/state FIPS, S2 L13, KWG county, ZIP | `spatialkg`/`spoke-okn` spatial hub |
| Industry | NAICS, SUDOKN sector | direct |

**Hub-mediated pairs are considered explored:** geographic leaves meet through the
`spatialkg` spatial hub; disease KGs through `oard-kg`; taxon KGs through `ubergraph`
(`taxon_overlap`). Apparent "missing" leaf-to-leaf or member-to-member pairs in those
clusters are not genuine gaps — they connect through the hub by design.

---

## B. Per-KG inventory (entity types + identifier schemes carried)

Schemes merge curated participation with live detection. **bold** = carried but **not
yet used as a join key for that KG** (the unexplored signal).

| KG | Representative entity types | Identifier schemes |
|---|---|---|
| biobricks-aopwiki | KeyEventRelationship, AOP data | CAS, Ensembl, NCBIGene, NCBITaxon, UniProt, **GO**, **NCIT** |
| biobricks-ice | CHEMINF/BAO assay | CAS |
| biobricks-mesh | Term, Concept, Descriptor | MeSH |
| biobricks-pubchem-annotations | Annotation | PubChem |
| biobricks-tox21 | CHEMINF substance | CAS |
| biobricks-toxcast | BAO/CHEMINF assay | CAS, CHEBI |
| biomarkerkg | Biomarker, Disease, Drug _(types not enumerated — timeout)_ | DOID, **CHEBI**, **CL** |
| climatemodelskg | City, Country_Subdivision, Member | **FIPS** (`equivalent_fips_code` literal), GeoNames |
| dreamkg | Rating, Review, ServiceChannel | ZIP |
| evoweb | Collection (co-evolving genes) | _none off-the-shelf (custom gene IRIs)_ |
| fiokg | EPA facility / Record | FIPS, S2 L13, NAICS, KWG |
| gene-expression-atlas-okn | Gene, Association, Assay | Ensembl, NCBITaxon, **NCBIGene** |
| geoconnex | Place, Dataset, PropertyValue | FIPS |
| hydrologykg | Feature, Region, SpatialObject | S2 L13, KWG |
| identifier-mappings | _(mapping table, no rdf:type)_ | _bridge table_ |
| medical-device-kg | MAUDEReport, MedicalDevice | _FDA product codes (island)_ |
| nasa-gesdisc-kg | Publication, Dataset, Instrument | _GeoNames/lat-long, science keywords (island)_ |
| ncipidkg | Statement (INDRA), pathway | UniProt, **GO** |
| nde | Dataset, Person, DefinedTerm | DOID, MONDO, NCBITaxon, **HP** |
| nikg | Incident, Location, CensusTract | FIPS, KWG, **MeSH** (2 descriptors), **Wikidata** |
| oard-kg | Disease association _(types not enumerated — timeout)_ | MONDO, HP, DOID, OMIM, Orphanet |
| pankgraph | Gene, Statement, SO sequence | Ensembl |
| phaseskg | Class, Axiom (ontology only) | _GO etc. = OBO scaffolding, no instance data (island)_ |
| prokn | Statement, Site_Annotation | UniProt, HGNC, MONDO, DOID, HP, OMIM, Orphanet, **DrugBank**, **GO**, **Ensembl**, **NCBIGene**, **MeSH**, NCIT, EFO |
| rdkg | Disease, Drug, Gene, PhenotypicFeature | DOID, MONDO, NCBIGene, **DrugBank** |
| ruralkg | NSDUH, TreatmentProvider, CountyStatus | FIPS, ZIP, **DrugBank** (7), **Wikidata** (~23) |
| sawgraph | sample/Quantifiable | S2 L13, NCBITaxon, **FIPS**, KWG, **UBERON** |
| scales | Court Party/CaseParty | FIPS, KWG |
| securechainkg | Software, Vulnerability, Hardware | NAICS |
| sockg | Measurement, GHGFlux, WeatherObs | FIPS, S2 L13, **ZIP**, KWG |
| spatialkg | Region, Feature, SpatialObject | FIPS, S2 L13, KWG |
| spoke-genelab | Gene, MethylationRegion | NCBIGene, NCBITaxon, **CL** |
| spoke-okn | OrganismTaxon, Gene, AdministrativeArea | DOID, MeSH, Ensembl, NCBIGene, HGNC, CHEBI, PubChem, FIPS, ZIP, NCBITaxon, **DrugBank** |
| sudokn | MaterialProduct, GeospatialSite | NAICS, ZIP |
| ufokn | S2Cell, GeoCoordinates | S2 L13, KWG |
| wikidata | Article, Dataset | _bridge: Wikidata Q, Orphanet_ |
| wildlifekn | Bird_name, Amphibian_name, Location | _species as label strings; no IRIs (island)_ |
| **bio101** | **— (0 triples)** | **unmaterialized at endpoint** |
| **digcfdekg** | **— (0 triples)** | **unmaterialized at endpoint** |

---

## C. Unexplored crosswalk candidates (ranked)

### Tier 1 — Clear gap, validated

**1. DrugBank — a join key never used in the table.** Four KGs carry DrugBank drug
IDs and none are linked on them:

| KG | DrugBank IRIs | Form |
|---|---|---|
| rdkg | 1,263 | `http://identifiers.org/drugbank/DB…` |
| spoke-okn | 471 | `http://identifiers.org/drugbank/DB…` |
| ruralkg | 7 | `https://go.drugbank.com/drugs/DB…` |
| prokn | present (count timed out) | (object) |

- **rdkg ↔ spoke-okn** is the prize: identical `identifiers.org/drugbank/` form → a
  direct, no-rewrite join (~471 shared candidates), linking rdkg's disease–drug graph to
  spoke-okn's chemical layer.
- ruralkg joins by bare `DB#####` normalization (`go.drugbank.com` → identifiers.org).
- This **confirms and extends** the unverified DrugBank thin-thread note (ruralkg↔rdkg).
- _Suggested probe:_ `COUNT(DISTINCT ?db)` over `?x ?p ?db FILTER(STRENDS(STR(?db),…DB…))`
  with bare-id `REPLACE` to bridge the two IRI forms.

### Tier 2 — Real, smaller, worth verifying

**2. GO (Gene Ontology) — never a join key.** `ncipidkg`, `prokn`, `biobricks-aopwiki`
carry GO terms (gene-function / pathway annotations). An unmapped functional dimension
linking pathways (ncipidkg) to curated proteins (prokn) and AOP events (aopwiki).
(`phaseskg`'s GO is OBO *scaffolding*, not data — excluded.)

**3. biomarkerkg into the disease + chemical clusters.** biomarkerkg is in the table on
a single DOID link, but also carries **CHEBI** (21 terms, e.g. `CHEBI_15377`) and **CL**.
Candidate crosswalks: biomarkerkg ↔ `spoke-okn`/`biobricks-toxcast` on CHEBI, and direct
biomarkerkg ↔ `nde`/`rdkg` on DOID (beyond the oard-kg hub).

**4. Gene-cluster extensions.** New gene-id carriers surfaced: `gene-expression-atlas-okn`
also carries **NCBI Gene** (was Ensembl-only), and `prokn` carries Ensembl/NCBI Gene
xrefs. Candidate pairs not in the table: `pankgraph ↔ biobricks-aopwiki` (Ensembl),
`gene-expression-atlas-okn ↔ prokn/rdkg` (Entrez), `pankgraph ↔ prokn` (Ensembl).

**5. climatemodelskg `equivalent_fips_code`.** A FIPS **literal** predicate exists — the
recorded non-join only checked S2/admin-region **IRIs** and missed it. Worth a targeted
retry to join climatemodelskg geography to `spoke-okn`/`spatialkg` county FIPS.

### Tier 3 — Marginal or already hub-covered

- **nikg MeSH** (only 2 descriptors) and **Wikidata** bridge (nikg, ruralkg ~23) — low
  cardinality.
- **CL / UBERON / NCIT / EFO** — niche ontologies or property fields (e.g. prokn's NCIT
  "Gene Name"), not instance join keys.
- **Geographic FIPS/S2/KWG leaf pairs and disease MONDO/HP/DOID pairs** flagged by the
  raw pair math are **hub-mediated** (spatialkg / oard-kg / ubergraph) — not genuine gaps.

---

## D. Corrections, islands, and limits

- **bio101 & digcfdekg return 0 triples** — unmaterialized at the endpoint, *not*
  overlooked crosswalks. Recommend recording bio101 as a `known_non_join` (unmaterialized),
  matching digcfdekg.
- **prokn is NOT a taxon-hub candidate** — `up:organism` is the string
  `"Homo sapiens (Human)"`, not an NCBITaxon IRI (an initial sampled signal was a false
  positive; corrected by spot-check).
- **phaseskg** GO/OBO terms are ontology scaffolding (no instance data) — island.
- **Islands / no public key:** medical-device-kg (FDA product codes), nasa-gesdisc-kg
  (GeoNames/keywords), wildlifekn (species as label strings), evoweb (custom gene IRIs).
  *(Superseded in part: medical-device-kg was de-islanded on ZIP5 2026-09-01, and
  nasa-gesdisc-kg / wildlifekn are thin threads rather than islands — DOI + GCMD labels
  and label-bridged NCBITaxon + county FIPS respectively. evoweb remains the one
  confirmed island.)*
- **Meta / bridge graphs** excluded as data endpoints: ubergraph (ontology backbone),
  okn-void (VOID metadata), identifier-mappings, wikidata.
- **Sampling limit:** `biomarkerkg` and `oard-kg` class lists timed out (data present,
  types not enumerated); large graphs (prokn DrugBank count, full taxon scans) were probed
  with bounded queries. A rare scheme not in the sample could be missed.

### Bottom line

Yes — there are unexplored crosswalks. The highest-value is **DrugBank**
(rdkg ↔ spoke-okn, identical IRI form; + prokn, ruralkg), an entire join key the table
never used. Secondary opportunities: **GO** (gene function), **biomarkerkg** into the
disease/chemical clusters, **gene-cluster Ensembl/Entrez extensions**, and the
**climatemodelskg FIPS literal**. Everything else is either hub-mediated (already
reachable), an island, or an empty graph.

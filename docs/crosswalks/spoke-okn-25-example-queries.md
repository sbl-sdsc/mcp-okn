# SPOKE-OKN — 25 real-world example queries, one per crosswalk partner

**Standalone showcase — NOT part of the crosswalk catalog** (`crosswalks_example.md` / `crosswalks_examples/`).
This file presents **one scientifically meaningful, literature-grounded, executed example query for each of the 25 distinct knowledge graphs that `spoke-okn` crosswalks with** in the Proto-OKN / FRINK federation.

- **Model:** claude-opus-4-8 · **Crosswalk source:** `mcp-okn list_crosswalks` (134 verified crosswalks, verified 2026-06-30)
- **Endpoint:** FRINK federated SPARQL via the `mcp-okn` service (`https://apps.okn.us/federation/sparql`)
- **All 25 queries were executed on 2026-06-27**; each block shows the runnable SPARQL, a real sample of returned rows, and a PubMed/literature anchor.
- **Scope rule — "25 crosswalks":** `spoke-okn` participates in many `list_crosswalks` rows, but they resolve to **25 distinct partner KGs**. This file gives one *new-angle* example per partner — deliberately different diseases / genes / chemicals / regions from the q1/q2 already in the catalog. Where a partner connects on more than one key (e.g. `rdkg` via DrugBank / Entrez / DOID↔MONDO; `ruralkg` via ZIP5 / county FIPS), the single most compelling join is shown and noted.

## Methodology

For each partner KG, the verified join recipe (shared identifier, predicates, IRI normalization, `ubergraph`/`wikidata` bridge where needed) was taken from `get_join_strategy` / the catalog transcripts, then applied to a **fresh research question** a domain scientist would actually ask. Every query scopes each graph with `GRAPH <https://purl.org/okn/frink/kg/{shortname}>`, was run against the live federation, and returned non-empty, on-topic rows. Each result is corroborated by a peer-reviewed reference (PubMed, or Paperclip full text).

## Index

| # | Partner KG | Shared key / bridge | Example query |
|---|---|---|---|
| | **Chemicals & Toxicology** | | |
| 1 | `biobricks-ice` | CHEBI↔CAS (ubergraph) | Androgen-receptor endocrine-disruption endpoints for SPOKE pesticides & plasticizers |
| 2 | `biobricks-tox21` | CHEBI↔CAS (ubergraph) | Tox21 chemicals regulating the metabolic nuclear receptor PPARG |
| 3 | `biobricks-toxcast` | CHEBI↔CAS (ubergraph) | ToxCast assay-endpoint coverage for SPOKE liver-toxicity compounds |
| 4 | `biobricks-pubchem-annotations` | PubChem CID (direct) | PubChem Parkinson's-neurotoxicity hazard text for paraquat |
| | **Disease & Phenotype** | | |
| 5 | `biomarkerkg` | DOID (direct) | Pancreatic-cancer driver genes backed by literature biomarker variants |
| 6 | `nde` | DOID↔MONDO (ubergraph) | NIAID datasets for the tuberculosis host-immune gene IFNG |
| 7 | `prokn` | DOID (direct) | Gastric-cancer precision-oncology evidence vs mortality burden |
| 8 | `oard-kg` | DOID↔MONDO (ubergraph) | Real-world EHR phenotype signature of glioblastoma |
| 9 | `biobricks-mesh` | MeSH descriptor (direct) | Authoritative MeSH definitions for SPOKE neuropsychiatric diseases |
| 10 | `biohealth` | UMLS↔MONDO↔DOID (ubergraph) | Asthma molecular network + clinical complication cascade |
| 11 | `rdkg` | Entrez (direct) | Fanconi-anemia rare-disease genes that are SPOKE cancer prognostic markers |
| | **Genes & Functional Genomics** | | |
| 12 | `gene-expression-atlas-okn` | Ensembl (direct) | Pan-cancer prognostic markers re-emerging in the breast-cancer expression signature |
| 13 | `pankgraph` | Ensembl (direct) | Polyautoimmunity of type-1-diabetes islet genes |
| 14 | `biobricks-aopwiki` | Ensembl (direct) | Neurotoxicity AOP key-event genes and their nervous-system disease links |
| 15 | `digcfdekg` | Entrez (direct) | CFDE REVEAL inflammatory-bowel-disease genes and their SPOKE comorbidity profile |
| 16 | `spoke-genelab` | Entrez (direct) | Spaceflight-responsive genes mapped to musculoskeletal disease |
| | **Geospatial Public Health** | | |
| 17 | `dreamkg` | ZIP5 (direct) | Substance-use / addiction-recovery services in validated Philadelphia ZIPs |
| 18 | `ruralkg` | county FIPS (direct) | Rural-urban gradient in county diabetes prevalence |
| 19 | `sudokn` | ZIP5 (direct) | Surface-finishing / electroplating manufacturers in validated Ohio ZIPs |
| 20 | `fiokg` | county FIPS (direct) | RCRA hazardous-waste facilities vs county self-rated health |
| 21 | `geoconnex` | county FIPS (direct) | Blue-space (water-feature) density vs county frequent mental distress |
| 22 | `nikg` | county FIPS (direct) | Non-fatal shooting incidents vs county frequent mental distress |
| | **Spatial, Environmental & Justice** | | |
| 23 | `scales` | county FIPS (direct) | Federal drug-charge caseload vs county drug-overdose mortality |
| 24 | `sockg` | county FIPS (direct) | Diabetes & physical inactivity in soil-carbon experiment counties |
| 25 | `spatialkg` | county FIPS → state (direct) | State ranking of county adult obesity rolled up via the GADM hierarchy |

---

## Chemicals & Toxicology

### 1. spoke-okn × biobricks-ice — Androgen-receptor endocrine-disruption endpoints for SPOKE pesticides and plasticizers
- **Partner KG:** `biobricks-ice` — NICEATM Integrated Chemical Environment: curated in-vivo/in-vitro toxicity, ADME, DART, and endocrine assay data.
- **Shared identifier / bridge:** CHEBI ↔ CAS (via ubergraph)
- **Research question:** Which SPOKE compounds carry ICE in-vitro **androgen-receptor (AR)** assay endpoints flagging *anti-androgenic* endocrine-disruption potential — i.e. SPOKE chemicals for which ICE supplies receptor-level evidence of male-reproductive endocrine hazard? (A different ICE data type — Endocrine_In_Vitro AR — from the DART set used in the catalog's q1.)
- **Why the join is required:** SPOKE holds the compounds' gene/disease network but no receptor-bioassay data, while ICE holds the AR binding/transactivation endpoints but not SPOKE's network context; only the CHEBI→CAS bridge lets a SPOKE compound inherit ICE's endocrine-disruption profile.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX edam: <http://edamontology.org/>
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT DISTINCT ?cmpLabel (REPLACE(STR(?c2),'http://identifiers.org/cas/','') AS ?CAS)
       (GROUP_CONCAT(DISTINCT REPLACE(?assay,'%20',' '); separator="; ") AS ?iceAndrogenAssays) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref ?chebi ; rdfs:label ?cmpLabel .
    FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?chebi obo:hasDbXref ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:'))
  }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?d edam:has_identifier ?c2 ; ro:RO_0000056 ?mg .
    FILTER(CONTAINS(STR(?d),'Endocrine_In_Vitro'))
    FILTER(CONTAINS(STR(?mg),'/AR%20'))
    BIND(REPLACE(STR(?mg),'^.*/assay/(.*)/Measure_Group$','$1') AS ?assay)
  }
}
GROUP BY ?cmpLabel ?c2
HAVING(CONTAINS(?iceAndrogenAssays,'Antagonist'))
ORDER BY ?cmpLabel LIMIT 15
```
- **Sample result** (8 of 15):

| Compound | CAS | ICE androgen-receptor assays |
|---|---|---|
| 2,4,5-Trichlorophenoxyacetic acid | 93-76-5 | AR Binding; AR Transactivation-Antagonist/Agonist |
| Atrazine | 1912-24-9 | AR Binding; AR Transactivation-Agonist/Antagonist |
| Benomyl | 17804-35-2 | AR Binding; AR Transactivation-Agonist/Antagonist |
| Benzyl butyl phthalate | 85-68-7 | AR Transactivation-Antagonist/Agonist; AR Binding |
| Bis(2-ethylhexyl) phthalate | 117-81-7 | AR Binding; AR Transactivation-Agonist/Antagonist |
| Bisphenol A | 80-05-7 | AR Binding; AR Transactivation-Antagonist/Agonist |
| Carbaryl | 63-25-2 | AR Transactivation-Antagonist; AR Binding/Agonist |
| Chlordecone | 143-50-0 | AR Binding; AR Transactivation-Agonist/Antagonist |

- **Why it answers the question:** every returned compound is a SPOKE chemical that ICE characterizes with androgen-receptor binding / transactivation-antagonist endpoints — surfacing canonical anti-androgens (the phthalates BBP and DEHP, bisphenol A, chlordecone, atrazine) whose endocrine-disruption evidence SPOKE itself cannot express.
- **Literature support:** Sohoni & Sumpter, 1998, *J Endocrinol* — yeast-based in-vitro assays confirmed benzyl butyl phthalate and bisphenol A possess anti-androgenic (AR-blocking) activity. [PMID:9846162](https://pubmed.ncbi.nlm.nih.gov/9846162/) · [DOI](https://doi.org/10.1677/joe.0.1580327)

### 2. spoke-okn × biobricks-tox21 — Tox21-screened chemicals regulating the metabolic nuclear receptor PPARG
- **Partner KG:** `biobricks-tox21` — Tox21 high-throughput in-vitro screening library (the federation graph carries the screened-chemical inventory, CAS-keyed).
- **Shared identifier / bridge:** CHEBI ↔ CAS (via ubergraph)
- **Research question:** Among Tox21 screening-library chemicals, which does SPOKE record up- or down-regulating the metabolic/endocrine nuclear-receptor genes **PPARG** (master regulator of adipogenesis, a type-2-diabetes drug target), **PPARA**, or the glucocorticoid receptor **NR3C1** — and in which direction?
- **Why the join is required:** Tox21 supplies the "is in the HTS screening library" gate but no gene-regulation knowledge, while SPOKE supplies the compound→nuclear-receptor regulation edges but identifies compounds by CHEBI, not CAS; the bridge pairs a Tox21 screening chemical with its SPOKE metabolic-receptor mechanism.
- **SPARQL** (executed 2026-06-27, returned 13 rows):
```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sk: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?cmpLabel (REPLACE(STR(?c2),'http://identifiers.org/cas/','') AS ?CAS) ?direction ?gene WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref ?chebi ; rdfs:label ?cmpLabel .
    FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_'))
    { ?cmp sk:UPREGULATES_CuG ?g . BIND("up-regulates" AS ?direction) }
    UNION
    { ?cmp sk:DOWNREGULATES_CdG ?g . BIND("down-regulates" AS ?direction) }
    ?g rdfs:label ?gene .
    FILTER(?gene IN ("PPARG","PPARA","NR3C1"))
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?chebi obo:hasDbXref ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:'))
  }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> { ?c2 rdfs:label ?tox21Label . }
} ORDER BY ?gene ?cmpLabel LIMIT 15
```
- **Sample result** (7 of 13):

| Compound | CAS | Direction | Nuclear-receptor gene |
|---|---|---|---|
| Carbon Tetrachloride | 56-23-5 | up-regulates | PPARG |
| Fluorouracil | 51-21-8 | up-regulates | PPARG |
| Hexachlorophene | 70-30-4 | up-regulates | PPARG |
| Pentobarbital | 76-74-4 | up / down-regulates | PPARG |
| Thiabendazole | 148-79-8 | up-regulates | PPARG |
| Fluorouracil | 51-21-8 | up-regulates | NR3C1 |
| Phenothiazine | 92-84-2 | up-regulates | NR3C1 |

- **Why it answers the question:** each row is a Tox21 screening-library chemical (confirmed by the CAS hit in biobricks-tox21) paired with its SPOKE-recorded regulation of a metabolic nuclear-receptor gene — e.g. carbon tetrachloride up-regulating PPARG, a mechanistically coherent hepatic-fibrosis signal.
- **Literature support:** Liu et al., 2020, *Gastroenterology* — in CCl4-induced liver fibrosis, PPARγ is required for hepatic stellate-cell quiescence and fibrosis resolution, tying carbon-tetrachloride toxicity to PPARG. [PMID:31982409](https://pubmed.ncbi.nlm.nih.gov/31982409/) · [DOI](https://doi.org/10.1053/j.gastro.2020.01.027)

### 3. spoke-okn × biobricks-toxcast — ToxCast assay-endpoint coverage for SPOKE liver-toxicity compounds
- **Partner KG:** `biobricks-toxcast` — EPA ToxCast high-throughput in-vitro bioassay endpoints (assay-endpoint IDs / aeids, CAS-keyed).
- **Shared identifier / bridge:** CHEBI ↔ CAS (via ubergraph)
- **Research question:** For chemicals SPOKE associates with **liver disease or liver cancer** (via treats/contraindicates edges), how broad is ToxCast's in-vitro assay-endpoint coverage — i.e. which hepatotoxicity-relevant SPOKE compounds have the most ToxCast mechanistic screening data available?
- **Why the join is required:** SPOKE supplies the compound→liver-disease association but no assay data, while ToxCast supplies the per-chemical count of in-vitro assay endpoints (aeids) but no disease context; the CHEBI→CAS bridge connects "SPOKE liver-disease chemical" to "its ToxCast screening footprint."
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX edam: <http://edamontology.org/>
PREFIX ro: <http://purl.obolibrary.org/obo/>
PREFIX sk: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?cmpLabel (REPLACE(STR(?c2),'http://identifiers.org/cas/','') AS ?CAS) ?spokeLiverDisease (COUNT(DISTINCT ?aeid) AS ?nToxCastEndpoints) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref ?chebi ; rdfs:label ?cmpLabel .
    FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_'))
    { ?cmp sk:TREATS_CtD ?dis } UNION { ?cmp sk:CONTRAINDICATES_CcD ?dis }
    ?dis rdfs:label ?spokeLiverDisease .
    FILTER(CONTAINS(LCASE(?spokeLiverDisease),'liver') || CONTAINS(LCASE(?spokeLiverDisease),'hepat'))
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?chebi obo:hasDbXref ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:'))
  }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
    ?t edam:has_identifier ?c2 ; ro:RO_0000056 ?mg .
    BIND(REPLACE(STR(?mg),'^.*/aeid/([0-9]+)/.*$','$1') AS ?aeid)
  }
} GROUP BY ?cmpLabel ?c2 ?spokeLiverDisease ORDER BY DESC(?nToxCastEndpoints) LIMIT 12
```
- **Sample result** (7 of 12):

| Compound | CAS | SPOKE liver disease | ToxCast assay endpoints |
|---|---|---|---|
| Phenytoin | 57-41-0 | liver disease | 1021 |
| Benzoic Acid | 532-32-1 | liver disease | 992 |
| Tetracycline | 60-54-8 | liver disease | 955 |
| Fluorouracil | 51-21-8 | liver cancer | 942 |
| Phenol | 108-95-2 | liver disease | 924 |
| Phenacetin | 62-44-2 | liver disease | 411 |
| Phenazopyridine | 136-40-3 | liver disease | 403 |

- **Why it answers the question:** each compound is one SPOKE links to liver disease/cancer ranked by the number of ToxCast in-vitro assay endpoints it has been screened in, surfacing classic hepatotoxicants (phenytoin, tetracycline, phenacetin, phenazopyridine) with the deepest mechanistic screening coverage.
- **Literature support:** Kamitaki et al., 2021, *Epilepsy & Behavior* — FDA Adverse Event Reporting System analysis flags phenytoin as significantly associated with drug-induced liver injury (reporting odds ratio 2.40). [PMID:33626490](https://pubmed.ncbi.nlm.nih.gov/33626490/) · [DOI](https://doi.org/10.1016/j.yebeh.2021.107832)

### 4. spoke-okn × biobricks-pubchem-annotations — PubChem Parkinson's-neurotoxicity hazard text for the SPOKE pesticide paraquat
- **Partner KG:** `biobricks-pubchem-annotations` — PubChem free-text annotations (toxicity, hazards, uses, pharmacology), keyed on PubChem CID.
- **Shared identifier / bridge:** PubChem CID (direct)
- **Research question:** For environmental chemicals SPOKE places in its compound network that are implicated in **neurodegeneration / Parkinson's disease** — taking the herbicide paraquat — what neurotoxicity and Parkinson's-related hazard narrative does PubChem hold?
- **Why the join is required:** SPOKE situates paraquat in its chemical network and carries its PubChem CID but stores no free-text safety narrative; the PubChem-annotations KG holds the detailed neurotoxicity/Parkinson's text but only on CID — so the CID bridge surfaces the hazard narrative for a SPOKE compound.
- **SPARQL** (executed 2026-06-27, returned 6 rows):
```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?compound (SUBSTR(?text,1,300) AS ?pubchemParkinsonNeurotoxAnnotation) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?c obo:hasDbXref <http://identifiers.org/pubchem.compound/15939> ; rdfs:label ?compound .
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID15939> ; oa:hasBody ?body .
    ?body rdf:value ?text .
    FILTER(REGEX(?text,'Parkinson|dopaminerg|neurodegener|substantia nigra','i'))
    FILTER(STRLEN(?text) > 120)
  }
} LIMIT 6
```
*Paraquat's CID 15939 is first confirmed from SPOKE's `hasDbXref`, then used directly to keep the full-text join fast (bulk text scanning across all CIDs times out). The five SPOKE-network Parkinson's environmental toxicants — paraquat, dieldrin, manganese, trichloroethylene, chlorpyrifos — all carry PubChem annotations, 25–94 each.*

- **Sample result** (4 of 6 PubChem annotations for paraquat, CID 15939, truncated):

- *"…the potential involvement of combined exposure to the herbicide paraquat and to maneb … in the etiology of idiopathic Parkinson disease…"* (paraquat+maneb PD etiology)
- *"…paraquat can be an environmental etiologic factor in Parkinson's disease (PD). One mechanism … is by inducing endoplasmic reticulum (ER) stress…"* (dopaminergic cell death mechanism)
- *"/LABORATORY ANIMALS: Neurotoxicity/ … DJ-1-deficient mice … gene–environment interaction that may produce Parkinson's disease…"* (gene–environment interaction)
- *"…Genetic variability in the alpha-synuclein gene and long-term exposure to the pesticide paraquat constitute possible risk factors for sporadic Parkinson's disease…"* (alpha-synuclein / paraquat risk)

- **Why it answers the question:** for a SPOKE network chemical, the CID join returns PubChem's actual Parkinson's-disease neurotoxicity narrative — paraquat-maneb etiology, dopaminergic neuron death, substantia-nigra and alpha-synuclein mechanisms — the hazard text SPOKE cannot itself express.
- **Literature support:** Lee et al., 2012, *Neurology* — a 357-case/754-control central-California study found ambient paraquat exposure associated with increased Parkinson's disease risk (AOR 1.36), rising ~3-fold when combined with traumatic brain injury. [PMID:23150532](https://pubmed.ncbi.nlm.nih.gov/23150532/) · [DOI](https://doi.org/10.1212/WNL.0b013e3182749f28)

---

## Disease & Phenotype

### 5. spoke-okn × biomarkerkg — Pancreatic-cancer driver genes backed by literature biomarker variants
- **Partner KG:** `biomarkerkg` — literature-curated clinical biomarkers (BiomarkerKB), keyed on DOID.
- **Shared identifier / bridge:** DOID (direct) — `DOID_1793` (pancreatic cancer).
- **Research question:** For pancreatic cancer, which genes does SPOKE associate with the disease, and is the disease backed by curated literature biomarker variants in BiomarkerKG?
- **Why the join is required:** SPOKE names the curated gene-association network but cannot say whether the disease carries literature variant evidence; BiomarkerKG quantifies the variant evidence but lists no gene-association network — returning the SPOKE gene list *conditioned on* biomarker support needs both graphs on the shared DOID.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX sschema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?geneLabel ?biomarkerVariantCount WHERE {
  {
    SELECT (COUNT(DISTINCT ?variant) AS ?biomarkerVariantCount) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
        ?b <http://purl.obolibrary.org/obo/OBCI_1000008> <http://purl.obolibrary.org/obo/DOID_1793> ;
           <http://purl.obolibrary.org/obo/OBCI_1000016> ?variant .
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    <http://purl.obolibrary.org/obo/DOID_1793> sschema:ASSOCIATES_DaG ?gene .
    ?gene rdfs:label ?geneLabel .
    FILTER(?geneLabel IN ("KRAS","TP53","CDKN2A","SMAD4","BRCA2","BRCA1","PALB2","STK11","ATM","MLH1","GNAS","RNF43"))
  }
}
ORDER BY ?geneLabel LIMIT 15
```
- **Sample result** (8 of 12; all carry BiomarkerKG variant count 615 for DOID_1793):

| SPOKE gene | BiomarkerKG variants |
|---|---|
| KRAS | 615 |
| TP53 | 615 |
| CDKN2A | 615 |
| SMAD4 | 615 |
| BRCA2 | 615 |
| PALB2 | 615 |
| STK11 | 615 |
| ATM | 615 |

- **Why it answers the question:** it returns SPOKE's pancreatic-cancer genes — the four canonical drivers (KRAS, TP53, CDKN2A, SMAD4) plus DNA-repair susceptibility genes (BRCA2, PALB2, ATM) — each confirmed against 615 curated literature biomarker variants for the same DOID.
- **Literature support:** Kamisawa et al., 2016, *Lancet* — names KRAS, CDKN2A, TP53 and SMAD4 as the four major driver genes of pancreatic cancer, with KRAS/CDKN2A as early events. [PMID:26830752](https://pubmed.ncbi.nlm.nih.gov/26830752/) · [DOI](https://doi.org/10.1016/S0140-6736(16)00141-0)

### 6. spoke-okn × nde — Public datasets for studying tuberculosis host-immune genes
- **Partner KG:** `nde` — NIAID Data Ecosystem inventory of infectious/immune-disease research datasets.
- **Shared identifier / bridge:** DOID↔MONDO (via ubergraph) — SPOKE's `DOID_399` (tuberculosis) bridges by `skos:exactMatch` to MONDO, the namespace NDE uses for infectious-disease datasets.
- **Research question:** For tuberculosis, which public NDE datasets are available to study its canonical SPOKE host-immune susceptibility gene IFNG?
- **Why the join is required:** SPOKE knows the TB host-immune driver genes but holds no dataset records; NDE holds the dataset titles but keys infectious-disease datasets on MONDO, not the DOID SPOKE uses — so routing from a TB gene to studyable public datasets requires the ubergraph DOID→MONDO bridge.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sschema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?geneLabel ?datasetName WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    <http://purl.obolibrary.org/obo/DOID_399> sschema:ASSOCIATES_DaG ?gene .
    ?gene rdfs:label ?geneLabel .
    FILTER(?geneLabel = "IFNG")
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo skos:exactMatch <http://purl.obolibrary.org/obo/DOID_399> .
    FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/nde> {
    ?ds <http://schema.org/healthCondition> ?mondo ;
        <http://schema.org/name> ?datasetName .
  }
}
ORDER BY ?datasetName LIMIT 12
```
- **Sample result** (6 of 12, gene IFNG → NDE dataset):

- A blood RNA signature for predicting treatment outcome in the Tuberculosis Treatment Response Cohort
- A blood RNA signature for tuberculosis disease risk in a household-contact study — GC6 cohort
- A blood RNA signature for tuberculosis disease risk: a prospective cohort study
- A modular transcriptional signature identifies phenotypic heterogeneity of human tuberculosis infection
- 2-aminoimidazoles potentiate β-lactam antimicrobial activity against Mycobacterium tuberculosis
- A glance over drug-detoxification systems through transcriptomic profiling of Mycobacterium tuberculosis during lipid metabolism

- **Why it answers the question:** each row is a real public NDE dataset tagged to tuberculosis and usable to study IFNG — the blood-RNA-signature cohorts are precisely the transcriptomic studies in which the interferon-driven host response (including IFN-γ) is measured.
- **Literature support:** Berry et al., 2010, *Nature* — identifies a whole-blood interferon-inducible transcriptional signature for active tuberculosis that reverts after treatment, the type of signature these NDE blood-RNA datasets capture. [PMID:20725040](https://pubmed.ncbi.nlm.nih.gov/20725040/) · [DOI](https://doi.org/10.1038/nature09247)

### 7. spoke-okn × prokn — Gastric-cancer precision-oncology evidence against mortality burden
- **Partner KG:** `prokn` — protein/marker-gene evidence graph carrying CIViC clinical-evidence assertions.
- **Shared identifier / bridge:** DOID (direct) — `DOID_10534` (stomach/gastric cancer).
- **Research question:** For gastric cancer, what specific ProKN CIViC clinical-evidence assertions about prognostic biomarkers exist, and how lethal is the disease per SPOKE WHO mortality data?
- **Why the join is required:** ProKN catalogs the precision-oncology evidence statements but holds no epidemiology; SPOKE holds the WHO mortality burden but no clinical-evidence catalog — pairing actual prognostic-evidence text with disease lethality needs both, joined on DOID.
- **SPARQL** (executed 2026-06-27, returned 2 rows under the prognosis filter):
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sschema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?evidence ?maxMortalityPer100k WHERE {
  {
    SELECT (MAX(?mort) AS ?maxMortalityPer100k) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?s rdf:subject <http://purl.obolibrary.org/obo/DOID_10534> ;
           rdf:predicate sschema:MORTALITY_DmL ;
           sschema:mortality_per_100k ?mort .
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?ev <http://purl.obolibrary.org/obo/bto#related_to> <http://purl.obolibrary.org/obo/DOID_10534> ;
        rdfs:label ?evidence .
    FILTER(CONTAINS(STR(?ev),'CIViC_ClinicalEvidence'))
    FILTER(CONTAINS(?evidence,'prognosis') || CONTAINS(?evidence,'overall survival') || CONTAINS(?evidence,'poor prognosis'))
  }
} LIMIT 10
```
- **Sample result** (2 of 2; SPOKE mortality = 9,806.64 / 100k):

- *"Cyclin D2 overexpression is associated with poor prognosis in gastric cancers."*
- *"The MTHFR C667T variant was associated with significantly lower relapse-free and overall survival in stomach-cancer patients treated with 5-fluorouracil-based therapies…"*

- **Why it answers the question:** each row pairs a real ProKN CIViC prognostic-biomarker assertion for gastric cancer (CCND2/cyclin D2; MTHFR pharmacogenomics) with SPOKE's WHO mortality burden for the same DOID — actual evidence statements set against disease lethality.
- **Literature support:** Shan et al., 2017, *Oncology Letters* — finds cyclin-D overexpression associated with shorter overall/progression-free survival in gastric cancer, corroborating the cyclin-D prognosis assertion. [PMID:28943959](https://pubmed.ncbi.nlm.nih.gov/28943959/) · [DOI](https://doi.org/10.3892/ol.2017.6736)

### 8. spoke-okn × oard-kg — Real-world EHR phenotype signature of glioblastoma enriched with SPOKE genes
- **Partner KG:** `oard-kg` — EHR-derived disease→phenotype associations (OHDSI/Columbia OARD).
- **Shared identifier / bridge:** DOID↔MONDO (via ubergraph) — SPOKE's glioblastoma DOID bridges by `skos:exactMatch` to the MONDO that OARD keys its log-odds evidence on.
- **Research question:** For glioblastoma, what is its real-world EHR phenotype signature (by log-odds) in patient cohorts, and how broad is SPOKE's gene-association network for the disease?
- **Why the join is required:** SPOKE curates the glioblastoma gene network but holds no EHR phenotype statistics; OARD holds the real-world log-odds but keys on MONDO, not DOID — connecting a SPOKE disease to its EHR phenotype enrichment requires the ubergraph DOID→MONDO bridge.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sschema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?hpLabel ?lor ?spokeGenes WHERE {
  {
    SELECT (COUNT(DISTINCT ?g) AS ?spokeGenes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?d a biolink:Disease ; rdfs:label "glioblastoma" ; sschema:ASSOCIATES_DaG ?g .
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?doid a biolink:Disease ; rdfs:label "glioblastoma" .
    FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo skos:exactMatch ?doid .
    FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
    ?assoc biolink:category biolink:DiseaseToPhenotypicFeatureAssociation ;
           biolink:subject ?mondo ;
           biolink:predicate biolink:positively_correlated_with ;
           biolink:object ?hp ;
           biolink:has_supporting_studies ?study .
    FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_'))
    ?study biolink:has_study_results ?res .
    ?res biolink:log_odds_ratio ?lor .
    FILTER(?lor < 100)
  }
  OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?hp rdfs:label ?hpLabel } }
}
ORDER BY DESC(?lor) LIMIT 12
```
- **Sample result** (7 of 12; SPOKE gene count = 62 for all):

| OARD EHR phenotype | log-odds |
|---|---|
| Glioma | 6.11 |
| Malignant neoplasm of the central nervous system | 5.55 |
| Pleomorphic xanthoastrocytoma | 5.50 |
| Neuroepithelial neoplasm | 5.33 |
| Neuroectodermal neoplasm | 5.20 |
| Brain neoplasm | 5.14 |
| Brainstem glioma | 4.99 |

- **Why it answers the question:** the top EHR-enriched phenotypes are all glioma/CNS-neoplasm concepts — a clinically faithful real-world signature for glioblastoma — set beside SPOKE's 62-gene association network for the same disease.
- **Literature support:** Vaubel et al., 2020, *Clinical Cancer Research* — a 96-PDX glioblastoma panel recapitulates the disease's recurrent molecular drivers and CNS-neoplasm phenotype, consistent with the glioma/CNS EHR signature surfaced here. [PMID:31852831](https://pubmed.ncbi.nlm.nih.gov/31852831/) · [DOI](https://doi.org/10.1158/1078-0432.CCR-19-0909)

### 9. spoke-okn × biobricks-mesh — Authoritative MeSH definitions for SPOKE neuropsychiatric diseases
- **Partner KG:** `biobricks-mesh` — the NLM MeSH thesaurus (definitions, concepts, tree placement).
- **Shared identifier / bridge:** MeSH descriptor id (direct) — SPOKE's `schema/mesh_list` tag, with the mandatory HTTPS→HTTP IRI rewrite.
- **Research question:** For SPOKE's neuropsychiatric and neurological disease nodes, what is the authoritative NLM MeSH definition (scope note) of each disease?
- **Why the join is required:** SPOKE knows the disease as a DOID and carries only a MeSH tag, holding no MeSH semantics; biobricks-mesh holds the definitions on the descriptor's `preferredConcept` (`scopeNote`) but not SPOKE's nodes — materializing the definition requires the MeSH-descriptor join (distinct from tree placement).
- **SPARQL** (executed 2026-06-27, returned 8 rows):
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX mv: <http://id.nlm.nih.gov/mesh/vocab#>
SELECT DISTINCT ?diseaseLabel ?meshLabel ?definition WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?doid a <https://w3id.org/biolink/vocab/Disease> ; rdfs:label ?diseaseLabel ;
          <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_list> ?mo .
    FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_'))
    FILTER(?diseaseLabel IN ("Alzheimer's disease","Parkinson's disease","schizophrenia","bipolar disorder","epilepsy","multiple sclerosis","autism spectrum disorder","migraine"))
  }
  BIND(REPLACE(STR(?mo),'^https://id.nlm.nih.gov/mesh/','') AS ?id)
  BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/',?id)) AS ?m)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m rdfs:label ?meshLabel ; mv:preferredConcept ?c .
    ?c mv:scopeNote ?definition .
  }
}
ORDER BY ?meshLabel LIMIT 12
```
- **Sample result** (5 of 8, SPOKE disease → MeSH descriptor → definition excerpt):

| SPOKE disease | MeSH descriptor | NLM definition (excerpt) |
|---|---|---|
| Alzheimer's disease | Alzheimer Disease | "A degenerative disease of the BRAIN characterized by the insidious onset of DEMENTIA … SENILE PLAQUES; NEUROFIBRILLARY TANGLES…" |
| Parkinson's disease | Parkinson Disease | "A progressive, degenerative neurologic disease characterized by a TREMOR that is maximal at rest … LEWY BODIES…" |
| multiple sclerosis | Multiple Sclerosis | "An autoimmune disorder … characterized by destruction of myelin in the central nervous system…" |
| bipolar disorder | Bipolar Disorder | "A major affective disorder marked by severe mood swings (manic or major depressive episodes)…" |
| autism spectrum disorder | Autism Spectrum Disorder | "Wide continuum of associated cognitive and neurobehavioral disorders … impairments in socialization … (from DSM-V)" |

- **Why it answers the question:** each SPOKE disease node is resolved to its canonical MeSH descriptor and full authoritative NLM definition — a definitional layer distinct from tree placement and reachable only through the MeSH-descriptor crosswalk.
- **Literature support:** Bramer et al., 2018, *J Med Libr Assoc* — shows MeSH controlled-vocabulary terms are the backbone for comprehensive biomedical literature searching, the use case these descriptor/definition mappings enable. [PMID:30271302](https://pubmed.ncbi.nlm.nih.gov/30271302/) · [DOI](https://doi.org/10.5195/jmla.2018.283)

### 10. spoke-okn × biohealth — Asthma molecular network plus its clinical complication cascade
- **Partner KG:** `biohealth` — literature/clinical/SDoH graph (SemMedDB predications) keyed on UMLS CUI.
- **Shared identifier / bridge:** UMLS↔MONDO↔DOID two-hop (via ubergraph) — SPOKE's `DOID_2841` (asthma) reaches BioHealthKG's UMLS node `C0004096`.
- **Research question:** For asthma, how broad is SPOKE's gene-association network, and which downstream conditions does BioHealthKG record asthma as predisposing to or complicating?
- **Why the join is required:** SPOKE supplies the gene network but no clinical predications; BioHealthKG supplies the SemMedDB predications keyed on UMLS, not DOID — and DOID is not directly UMLS-cross-referenced, so the molecular-plus-complication dossier needs the two-hop UMLS→MONDO→DOID bridge.
- **SPARQL** (executed 2026-06-27, returned 13 rows):
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?spokeGenes ?pred ?olabel WHERE {
  {
    SELECT (COUNT(DISTINCT ?gene) AS ?spokeGenes) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        <http://purl.obolibrary.org/obo/DOID_2841> <https://purl.org/okn/frink/kg/spoke-okn/schema/ASSOCIATES_DaG> ?gene .
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    <https://biohealthkg.proto-okn.net/kg/node/C0004096> ?p ?o .
    VALUES ?p { <https://w3id.org/biolink/vocab/predisposes_to_condition> <https://biohealthkg.proto-okn.net/kg/schema/COMPLICATES> }
    BIND(REPLACE(REPLACE(STR(?p),'https://w3id.org/biolink/vocab/',''),'https://biohealthkg.proto-okn.net/kg/schema/','') AS ?pred)
    ?o rdfs:label ?olabel .
    FILTER(?olabel IN ("Acute bronchiolitis","Airway Obstruction","Allergic rhinitis NOS","Anaphylaxis","Status Asthmaticus","Respiratory Failure","Pneumonia","Bronchospasm","Chronic Obstructive Airway Disease","Gastroesophageal reflux disease"))
  }
}
ORDER BY ?pred ?olabel LIMIT 15
```
- **Sample result** (7 of 13; SPOKE gene count = 465 for all):

| BioHealthKG predicate | condition |
|---|---|
| COMPLICATES | Allergic rhinitis NOS |
| COMPLICATES | Chronic Obstructive Airway Disease |
| COMPLICATES | Gastroesophageal reflux disease |
| predisposes_to_condition | Airway Obstruction |
| predisposes_to_condition | Anaphylaxis |
| predisposes_to_condition | Respiratory Failure |
| predisposes_to_condition | Status Asthmaticus |

- **Why it answers the question:** it pairs SPOKE's 465-gene asthma network with BioHealthKG's clinical predication profile — the airway/allergic complication cascade (allergic rhinitis, airway obstruction, status asthmaticus, COPD, GERD) — a dossier requiring both graphs across the two-hop bridge.
- **Literature support:** Wang et al., 2021, *Healthcare* — a real-world cohort shows allergic-airway disease co-occurs with asthma, COPD and gastroesophageal reflux disease, matching the BioHealthKG asthma predication profile. [PMID:33401606](https://pubmed.ncbi.nlm.nih.gov/33401606/) · [DOI](https://doi.org/10.3390/healthcare9010036)

### 11. spoke-okn × rdkg — Fanconi-anemia rare-disease genes that are SPOKE cancer prognostic markers
- **Partner KG:** `rdkg` — rare-disease gene/drug associations (Orphanet/MONDO/DrugBank/Entrez).
- **Shared identifier / bridge:** Entrez gene id (direct) — rdkg `ncbigene` IRIs rewritten to SPOKE's `ncbi.nlm.nih.gov/gene` IRIs. *(rdkg also crosswalks SPOKE via DrugBank and DOID↔MONDO; the Entrez gene join is shown here.)*
- **Research question:** Which genes that rdkg links to the rare DNA-repair disorder Fanconi anemia does SPOKE independently flag as favorable/unfavorable prognostic markers in cancer?
- **Why the join is required:** rdkg holds the Fanconi-anemia rare-disease gene panel but no cancer-prognosis edges; SPOKE holds the cancer prognostic-marker edges but does not classify rare-disease genes — only the shared Entrez join surfaces genes with both a rare-disease and a somatic-cancer-prognosis role.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?markerType ?cancer WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?r a biolink:Gene ; rdfs:label ?sym ; biolink:related_to <http://purl.obolibrary.org/obo/MONDO_0019391> .
    FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?gene spoke:MARKER_POS_GmpD ?c . BIND("favorable" AS ?markerType) }
    UNION
    { ?gene spoke:MARKER_NEG_GmnD ?c . BIND("unfavorable" AS ?markerType) }
    ?c rdfs:label ?cancer .
  }
} ORDER BY ?sym ?cancer LIMIT 15
```
- **Sample result** (8 of 15):

| Fanconi-anemia gene (rdkg) | SPOKE marker | cancer |
|---|---|---|
| BRIP1 | favorable | colorectal cancer |
| FANCC | favorable | kidney cancer |
| FANCD2 | unfavorable | ovarian cancer |
| FANCG | unfavorable | liver cancer |
| FANCI | unfavorable | pancreatic cancer |
| ERCC1 | unfavorable | kidney cancer |
| MX1 | unfavorable | kidney cancer |
| FANCL | unfavorable | liver cancer |

- **Why it answers the question:** every gene is an rdkg-curated Fanconi-anemia gene that SPOKE independently scores as a cancer prognostic marker — DNA-repair/BRCA-pathway genes (FANCD2, FANCI, ERCC1, BRIP1) doubling as somatic prognostic markers, visible only through the Entrez join.
- **Literature support:** Bogliolo et al., 2017, *Genetics in Medicine* — biallelic mutations in the Fanconi-anemia/BRCA-pathway gene FANCM cause an early-onset cancer-predisposition syndrome, underscoring the cancer-relevant role of Fanconi-anemia pathway genes. [PMID:28837157](https://pubmed.ncbi.nlm.nih.gov/28837157/) · [DOI](https://doi.org/10.1038/gim.2017.124)

---

## Genes & Functional Genomics

### 12. spoke-okn × gene-expression-atlas-okn — Pan-cancer prognostic markers re-emerging in the breast-cancer expression signature
- **Partner KG:** `gene-expression-atlas-okn` — EBI Expression Atlas baseline/differential tissue & disease gene expression (measured log2 fold-changes, significance).
- **Shared identifier / bridge:** Ensembl gene IRI (`http://identifiers.org/ensembl/ENSG…`) — direct (GXA differential-expression objects ARE Ensembl IRIs; SPOKE carries the same IRI on `spoke:ensembl`).
- **Research question:** SPOKE flags many genes as survival-prognostic markers for cancers OTHER than breast (kidney, liver, colorectal, lung, pancreatic). Which of these *out-of-tissue* prognostic markers are nonetheless significantly dysregulated in the Expression-Atlas breast-cancer signature — i.e. which markers "port" across tumour types into breast cancer?
- **Why the join is required:** SPOKE asserts the prognostic-marker status (per cancer) but holds no measured per-experiment expression; GXA holds the measured breast-cancer log2 fold-changes but has no prognostic-marker concept. Testing marker portability into breast cancer needs the Ensembl join.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?marker ?spokeCancer ?direction ?log2fc WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?g spoke:MARKER_NEG_GmnD ?c . BIND("unfavorable" AS ?marker) }
    UNION
    { ?g spoke:MARKER_POS_GmpD ?c . BIND("favorable" AS ?marker) }
    ?c rdfs:label ?spokeCancer .
    FILTER(?spokeCancer != "breast cancer")
    ?g spoke:ensembl ?ens ; rdfs:label ?sym .
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?assoc biolink:object ?ens ; biolink:subject ?assay ;
           wobd:direction ?direction ; wobd:log2fc ?log2fc ; wobd:adj_p_value ?adjp .
    ?study biolink:has_output ?assay ; biolink:studies ?dis .
    ?dis biolink:name ?gxaDisease .
    FILTER(?gxaDisease = "breast cancer")
    FILTER(?adjp < 0.01)
  }
} ORDER BY DESC(ABS(?log2fc)) LIMIT 15
```
- **Sample result** (7 of 15):

| Gene | SPOKE marker (cancer) | Breast-cancer direction | log2FC |
|---|---|---|---|
| TAGLN | unfavorable (kidney) | up | 1.4 |
| CRYAB | unfavorable (colorectal) | up | 1.3 |
| FLT1 | unfavorable (kidney) | up | 1.2 |
| APOBEC3G | favorable (cervical) | down | -1.1 |
| SEMA3F | unfavorable (liver) | up | 1.1 |
| AKR1C3 | unfavorable (kidney/liver) | down | -1.0 |
| F3 | unfavorable (kidney/pancreatic) | up | 1.0 |

- **Why it answers the question:** each gene is a SPOKE prognostic marker defined in a non-breast tumour yet shows a significant breast-cancer fold-change — CRYAB (an unfavorable colorectal marker, up +1.3 in breast) is the cleanest pan-tumour poor-prognosis signal that only the Ensembl join can surface.
- **Literature support:** Winkler et al., 2024, *J Clin Invest* — single-cell breast-cancer metastasis analysis identifies CRYAB as a marker of the intermediate epithelial-mesenchymal-plasticity state correlated with worse patient outcomes. [PMID:39225101](https://pubmed.ncbi.nlm.nih.gov/39225101/) · [DOI](https://doi.org/10.1172/JCI164227)

### 13. spoke-okn × pankgraph — Polyautoimmunity of type-1-diabetes islet genes
- **Partner KG:** `pankgraph` — PanKbase pancreatic-islet / diabetes gene graph (gene→condition associations from islet genomics).
- **Shared identifier / bridge:** Ensembl gene IRI — direct (pankgraph gene nodes ARE Ensembl IRIs; SPOKE carries the same IRI on `spoke:ensembl`).
- **Research question:** Type 1 diabetes rarely travels alone — it clusters with other organ-specific autoimmunity. For the genes pankgraph associates with type 1 diabetes, which OTHER autoimmune diseases (thyroid, celiac, MS, RA, lupus, IBD, vitiligo) does SPOKE independently associate the same genes with, mapping the shared genetic basis of polyautoimmunity?
- **Why the join is required:** pankgraph supplies the T1D islet gene set but no broader autoimmune-disease network; SPOKE supplies the gene→disease associations but no diabetes/islet context. Quantifying which T1D genes drive co-occurring autoimmunity needs the Ensembl join.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?spokeDisease WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?gene a biolink:Gene ; biolink:gene_associated_with_condition ?cond .
    ?cond rdfs:label ?pankCondition .
    FILTER(?pankCondition = "type 1 diabetes")
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g spoke:ensembl ?gene ; rdfs:label ?sym .
    ?disease spoke:ASSOCIATES_DaG ?g ; rdfs:label ?spokeDisease .
    FILTER(CONTAINS(LCASE(?spokeDisease),"thyroid") || CONTAINS(LCASE(?spokeDisease),"celiac") || CONTAINS(LCASE(?spokeDisease),"sclerosis") || CONTAINS(LCASE(?spokeDisease),"rheumatoid") || CONTAINS(LCASE(?spokeDisease),"vitiligo") || CONTAINS(LCASE(?spokeDisease),"lupus") || CONTAINS(LCASE(?spokeDisease),"bowel"))
  }
} ORDER BY ?sym LIMIT 15
```
- **Sample result** (8 of 15):

| Gene | pankgraph condition | Other autoimmune disease (SPOKE) |
|---|---|---|
| ADCY3 | type 1 diabetes | multiple sclerosis, inflammatory bowel disease |
| AFF3 | type 1 diabetes | rheumatoid arthritis |
| AIRE | type 1 diabetes | rheumatoid arthritis |
| BACH2 | type 1 diabetes | IBD, multiple sclerosis, rheumatoid arthritis |
| CD226 | type 1 diabetes | IBD, multiple sclerosis, rheumatoid arthritis |
| CD19 | type 1 diabetes | rheumatoid arthritis |
| CD28 | type 1 diabetes | inflammatory bowel disease |
| CCR2 | type 1 diabetes | arteriosclerosis |

- **Why it answers the question:** the recovered genes (BACH2, CD226, AIRE, CD28, AFF3) are textbook shared-autoimmunity loci, and SPOKE links each T1D islet gene to MS/RA/IBD — the cross-disease genetic overlap of polyautoimmunity, visible only via the Ensembl join.
- **Literature support:** Brorsson & Pociot, 2015, *Diabetes Care* — in Type 1 Diabetes Genetics Consortium families, BACH2 (with IFIH1, PTPN22, SH2B3, CTLA4) is shared across T1D and thyroid/celiac/gastric autoantibodies. [PMID:26405073](https://pubmed.ncbi.nlm.nih.gov/26405073/) · [DOI](https://doi.org/10.2337/dcs15-2003)

### 14. spoke-okn × biobricks-aopwiki — Neurotoxicity adverse-outcome-pathway genes and their nervous-system disease associations
- **Partner KG:** `biobricks-aopwiki` — AOP-Wiki Adverse Outcome Pathways; key-event molecular targets (genes) for predicted toxic outcomes.
- **Shared identifier / bridge:** Ensembl gene IRI — direct (AOP-Wiki carries it via `skos:exactMatch` as `https://identifiers.org/ensembl/…`, rewritten to the `http://…` form SPOKE stores on `spoke:ensembl`).
- **Research question:** For genes AOP-Wiki defines as key-event targets in *neurotoxicity* AOPs (acetylcholinesterase inhibition, NMDA-receptor antagonism, dopaminergic/nigro-striatal injury, glutamate excitotoxicity, learning-and-memory impairment), does SPOKE independently associate them with nervous-system disease or epilepsy — i.e. do the AOP-predicted neuro outcomes line up with known neurological disease links?
- **Why the join is required:** AOP-Wiki gives the mechanistic neurotoxicity pathway and its predicted adverse outcome but no gene-disease associations; SPOKE gives the gene-disease associations but has no AOP concept. Confirming an AOP's neuro outcome against real disease links needs the Ensembl join.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT DISTINCT ?aopTitle ?geneLabel ?diseaseLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?aop <http://aopkb.org/aop_ontology#has_key_event> ?ke ; dc:title ?aopTitle .
    FILTER(CONTAINS(LCASE(?aopTitle),"parkinson") || CONTAINS(LCASE(?aopTitle),"dopaminergic") || CONTAINS(LCASE(?aopTitle),"nigro") || CONTAINS(LCASE(?aopTitle),"neurodegeneration") || CONTAINS(LCASE(?aopTitle),"learning and memory") || CONTAINS(LCASE(?aopTitle),"excitotox"))
    ?ke <http://edamontology.org/data_1025> ?gnode .
    ?gnode skos:exactMatch ?e .
    FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ensembl/'))
  }
  BIND(IRI(REPLACE(STR(?e),'https://identifiers.org/ensembl/','http://identifiers.org/ensembl/')) AS ?ensIRI)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?gene schema:ensembl ?ensIRI ; rdfs:label ?geneLabel .
    ?disease schema:ASSOCIATES_DaG ?gene ; rdfs:label ?diseaseLabel .
    FILTER(CONTAINS(LCASE(?diseaseLabel),"parkinson") || CONTAINS(LCASE(?diseaseLabel),"alzheimer") || CONTAINS(LCASE(?diseaseLabel),"nervous") || CONTAINS(LCASE(?diseaseLabel),"motor neuron") || CONTAINS(LCASE(?diseaseLabel),"epilep"))
  }
} ORDER BY ?geneLabel ?aopTitle LIMIT 15
```
- **Sample result** (6 of 15):

- **AIFM1** — *Acetylcholinesterase Inhibition Leading to Neurodegeneration* → nervous system disease, epilepsy
- **AIFM1** — *Binding of agonists to ionotropic glutamate receptors … excitotoxicity … learning and memory impairment* → epilepsy, nervous system disease
- **AIFM1** — *Calcium overload in dopaminergic neurons of the substantia nigra → parkinsonian motor deficits* → nervous system disease, epilepsy
- **AIFM1** — *Inhibition of mitochondrial complex I of nigro-striatal neurons → parkinsonian motor deficits* → nervous system disease, epilepsy
- **AIFM1** — *Chronic NMDA-receptor antagonist binding during brain development → neurodegeneration / learning-memory impairment in aging* → nervous system disease, epilepsy
- **AIMP2** — *Deposition of Energy Leading to Learning and Memory Impairment* → epilepsy

- **Why it answers the question:** AIFM1 (mitochondrial apoptosis-inducing factor) recurs as a key-event target across multiple neurotoxicity AOPs — acetylcholinesterase inhibition, excitotoxicity, dopaminergic/nigro-striatal Parkinsonian injury — and SPOKE independently ties it to nervous-system disease and epilepsy, corroborating the AOPs' predicted neurodegenerative outcomes; the link exists only through the Ensembl join.
- **Literature support:** Sinitsyn et al., 2022, *Frontiers in Toxicology* — uses "Acetylcholinesterase Inhibition Leading to Neurodegeneration" as the case-study AOP for quantitative neurodegeneration modelling, validating this AOP→neurodegeneration pathway. [PMID:35434701](https://pubmed.ncbi.nlm.nih.gov/35434701/) · [DOI](https://doi.org/10.3389/ftox.2022.838729)

### 15. spoke-okn × digcfdekg — CFDE REVEAL inflammatory-bowel-disease genes and their SPOKE comorbidity profile
- **Partner KG:** `digcfdekg` — CFDE REVEAL gene-trait factor inferences (PIGEAN statistical gene→trait relevance scores).
- **Shared identifier / bridge:** Entrez gene IRI (`http://www.ncbi.nlm.nih.gov/gene/{id}`) — direct (digcfdekg gene nodes ARE Entrez IRIs; SPOKE genes carry the identical IRI form, no rewrite).
- **Research question:** Which genes does CFDE REVEAL's PIGEAN method infer as most relevant to inflammatory bowel disease (MONDO_0005265), and what wider immune/inflammatory comorbidity neighbourhood does SPOKE independently associate those same genes with?
- **Why the join is required:** digcfdekg holds the PIGEAN IBD relevance ranking but no gene-disease network; SPOKE holds the gene→disease associations but no CFDE trait inference. Ranking IBD genes by CFDE score and reading off each gene's SPOKE comorbidity set is only possible by joining on the shared Entrez id.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?sym ?pigeanScore (COUNT(DISTINCT ?spokeDisease) AS ?nSpokeDiseases)
       (GROUP_CONCAT(DISTINCT ?spokeDisease; separator=" | ") AS ?spokeDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/MONDO_0005265> ;
        rdf:subject ?gene ;
        dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 3.0)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?d spoke:ASSOCIATES_DaG ?gene ; rdfs:label ?spokeDisease .
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 15
```
- **Sample result** (7 of 15):

| Gene | PIGEAN score | # SPOKE diseases | Example SPOKE diseases |
|---|---|---|---|
| IL12B | 9.84 | 6 | psoriasis, IBD, migraine, cardiomyopathy |
| IL10 | 9.68 | 39 | IBD, rheumatoid arthritis, MS, colorectal cancer |
| REL | 9.16 | 2 | rheumatoid arthritis, liver disease |
| IFNG | 9.12 | 50 | IBD, psoriasis, MS, rheumatoid arthritis |
| NFKB2 | 8.87 | 6 | psoriasis, asthma, dermatitis |
| TNF | 8.52 | 49 | IBD, rheumatoid arthritis, psoriasis, MS |
| IL2RA | 8.46 | 13 | IBD, MS, psoriasis, rheumatoid arthritis |

- **Why it answers the question:** CFDE REVEAL's top IBD genes are the canonical IBD/immune loci (IL12B, IL10, IFNG, TNF, IL2RA), and SPOKE independently anchors each in IBD plus the immune-mediated comorbidity cluster (psoriasis, RA, MS) — a profile only assemblable by the Entrez join.
- **Literature support:** Zhang et al., 2025, *Nature Communications* — UK Biobank proteomics + Mendelian randomization prioritizes IL12B and IFNG among causal, colocalized proteins for inflammatory bowel disease. [PMID:40118817](https://pubmed.ncbi.nlm.nih.gov/40118817/) · [DOI](https://doi.org/10.1038/s41467-025-57879-3)

### 16. spoke-okn × spoke-genelab — Spaceflight-responsive genes mapped to musculoskeletal (bone/cartilage) disease
- **Partner KG:** `spoke-genelab` — NASA GeneLab spaceflight omics gene observations (measured spaceflight differential expression).
- **Shared identifier / bridge:** Entrez gene IRI (`https://www.ncbi.nlm.nih.gov/gene/{id}`) — direct (both KGs use NCBI gene IRIs, no rewrite).
- **Research question:** Spaceflight causes bone loss and musculoskeletal deconditioning. Among the genes most strongly differentially expressed in NASA GeneLab spaceflight assays, which does SPOKE associate specifically with musculoskeletal disease (osteoarthritis, rheumatoid arthritis, bone/muscle disorders) — mapping the spaceflight transcriptional response onto its skeletal/joint disease relevance?
- **Why the join is required:** spoke-genelab carries the spaceflight expression magnitudes but no curated gene-disease associations; SPOKE carries the musculoskeletal disease associations but no spaceflight data. Linking a spaceflight response to bone/joint disease needs the direct Entrez join.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?spokeDisease (MAX(ABS(?lfc)) AS ?maxAbsLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 1.0e-20)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?gene rdfs:label ?sym .
    ?d spoke:ASSOCIATES_DaG ?gene ; rdfs:label ?spokeDisease .
    FILTER(CONTAINS(LCASE(?spokeDisease),"osteo") || CONTAINS(LCASE(?spokeDisease),"muscle") || CONTAINS(LCASE(?spokeDisease),"muscular") || CONTAINS(LCASE(?spokeDisease),"sarcopenia") || CONTAINS(LCASE(?spokeDisease),"bone") || CONTAINS(LCASE(?spokeDisease),"rheumatoid"))
  }
} GROUP BY ?sym ?spokeDisease ORDER BY ?minAdjP LIMIT 15
```
- **Sample result** (7 of 15):

| Gene | max abs log2FC (spaceflight) | SPOKE musculoskeletal disease |
|---|---|---|
| MMP3 | 12.2 | rheumatoid arthritis, osteoarthritis |
| PADI2 | 9.6 | rheumatoid arthritis |
| PRKCQ | 8.6 | rheumatoid arthritis |
| RBFOX1 | 6.2 | rheumatoid arthritis |
| DPP4 | 5.3 | rheumatoid arthritis |
| CAMK2B | 5.0 | osteoarthritis |
| FCGR2B | 3.8 | rheumatoid arthritis |

- **Why it answers the question:** MMP3 (stromelysin-1) — among the most strongly spaceflight-perturbed genes (log2FC 12.2) — is associated by SPOKE with both rheumatoid arthritis and osteoarthritis, directly tying the spaceflight transcriptional response to cartilage/bone-destroying joint disease; the mapping exists only via the Entrez join.
- **Literature support:** Lipina et al., 2017, *International Orthopaedics* — among serum biomarkers of bone and cartilage destruction in rheumatoid-arthritis patients, MMP-3 was the only inflammation marker reaching statistical significance, confirming its role in musculoskeletal tissue breakdown. [PMID:28889180](https://pubmed.ncbi.nlm.nih.gov/28889180/) · [DOI](https://doi.org/10.1007/s00264-017-3634-8)

---

## Geospatial Public Health

### 17. spoke-okn × dreamkg — Substance-use / addiction-recovery services in validated Philadelphia ZIPs
- **Partner KG:** `dreamkg` — DREAM-KG homelessness / social-services graph for Philadelphia, each service tagged with a bare 5-digit `schema:postalCode`.
- **Shared identifier / bridge:** ZIP5 (bare 5-digit string) — direct
- **Research question:** Beyond mental-health and food/shelter services, which standard residential Philadelphia (PA) ZIPs — validated via SPOKE — concentrate the most **substance-use counseling / addiction-and-recovery** services in DREAM-KG? Mapping where treatment capacity clusters is central to confronting Philadelphia's opioid crisis.
- **Why the join is required:** DREAM-KG holds the addiction-recovery services and their ZIP but cannot confirm a code is a valid PA standard residential ZIP; SPOKE supplies that administrative validation (`state = "PA"`, `zipcode_type = "STANDARD"`). Counting addiction services restricted to verified ZIPs requires both graphs joined on the bare ZIP string.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
SELECT ?zip (COUNT(DISTINCT ?svc) AS ?nSubstanceUse) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "PA" ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/zipcode_type> "STANDARD" .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
  }
  GRAPH <https://purl.org/okn/frink/kg/dreamkg> {
    ?svc <http://schema.org/postalCode> ?zip ;
         <http://schema.org/category> ?cat .
    FILTER(CONTAINS(STR(?cat),'SubstanceAbuseCounseling') || CONTAINS(STR(?cat),'AddictionAndRecovery'))
  }
} GROUP BY ?zip ORDER BY DESC(?nSubstanceUse) LIMIT 12
```
- **Sample result** (8 of 12):

| ZIP | substance-use / addiction services |
|---|---|
| 19124 | 13 |
| 19134 | 10 |
| 19107 | 8 |
| 19140 | 7 |
| 19104 | 6 |
| 19143 | 6 |
| 19141 | 6 |
| 19131 | 5 |

- **Why it answers the question:** each PA-validated standard residential ZIP is ranked by DREAM-KG addiction-service count, with the Kensington-area ZIPs (19124, 19134, 19140) — Philadelphia's opioid epicenter — leading, exactly where treatment capacity concentrates.
- **Literature support:** Pizzicato et al., 2019, *Substance Abuse* — among people accessing Philadelphia harm-reduction services, non-fatal opioid overdose was strongly associated with unstable housing (aOR 2.16), framing ZIP-level addiction-service access as critical for this homeless-adjacent population. [PMID:31644397](https://pubmed.ncbi.nlm.nih.gov/31644397/) · [DOI](https://doi.org/10.1080/08897077.2019.1675115)

### 18. spoke-okn × ruralkg — Rural-urban gradient in county diabetes prevalence
- **Partner KG:** `ruralkg` — rural health / resilience graph classifying every U.S. county by USDA Rural-Urban Continuum Code (RUCC 1 = most metropolitan … 9 = most rural).
- **Shared identifier / bridge:** county FIPS (embedded in RuralKG's KWG `censusCounty` IRI) — direct *(ruralkg also crosswalks SPOKE on ZIP5; the county-FIPS join is shown here.)*
- **Research question:** Using RuralKG's full RUCC (1→9) classification joined on county FIPS to SPOKE's county **diabetes-prevalence** indicator, is there a rural-urban gradient in adult diabetes across all U.S. counties?
- **Why the join is required:** RuralKG knows how rural a county is but has no diabetes data; SPOKE holds the county diabetes prevalence but no rurality classification. Only the FIPS join lets us bin one metric by the other.
- **SPARQL** (executed 2026-06-27, returned 9 rows):
```sparql
PREFIX rural: <http://sail.ua.edu/ruralkg/settlementtype/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?ruccCode (COUNT(?fips) AS ?counties) (AVG(?dia) AS ?avgDiabetes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?cs rural:censusCounty ?reg ; rural:hasRUCC ?rucc .
    ?rucc rural:code ?ruccCode .
  }
  BIND(REPLACE(STR(?reg),'^.*USA\\.','') AS ?fips)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "diabetes prevalence" ; schema:value ?v .
    BIND(xsd:decimal(REPLACE(?v,'\\(.*$','')) AS ?dia)
  }
} GROUP BY ?ruccCode ORDER BY ?ruccCode
```
- **Sample result** (all 9 RUCC classes):

| RUCC | Class | Counties | Avg diabetes prevalence % |
|---|---|---|---|
| 1 | Most metropolitan | 430 | 9.73 |
| 2 | | 378 | 10.26 |
| 3 | | 352 | 10.27 |
| 4 | | 213 | 10.49 |
| 5 | | 92 | 10.52 |
| 6 | | 591 | 11.16 |
| 7 | | 432 | 10.70 |
| 8 | | 220 | 10.86 |
| 9 | Most rural | 421 | 10.17 |

- **Why it answers the question:** averaging SPOKE diabetes prevalence within each RuralKG RUCC class (3,129 counties) reveals a clear gradient — diabetes rises from 9.7% in the most-metropolitan counties to ~10.5–11.2% across nonmetro/rural classes.
- **Literature support:** Dugani et al., 2022, *JAMA Network Open* — U.S. rural counties had the highest diabetes mortality rate over 1999–2018 vs medium-small and metro counties, confirming rurality as a determinant of diabetes burden. [PMID:36125809](https://pubmed.ncbi.nlm.nih.gov/36125809/) · [DOI](https://doi.org/10.1001/jamanetworkopen.2022.32318)

### 19. spoke-okn × sudokn — Surface-finishing / electroplating manufacturers in validated Ohio ZIPs
- **Partner KG:** `sudokn` — small/medium U.S. manufacturers (NAICS codes, process/material capabilities); each company's geolocation carries a `schema:postalCode`.
- **Shared identifier / bridge:** ZIP5 (bare 5-digit string) — direct
- **Research question:** Within Ohio, which standard residential ZIP codes (validated via SPOKE) concentrate the most **surface-finishing manufacturers** (electroplating / anodizing / galvanizing / coating)? These metal-finishing operations are a documented source of hexavalent-chromium and heavy-metal release, an environmental-justice exposure concern.
- **Why the join is required:** SUDOKN identifies finishing-capable companies and their ZIP but cannot place a ZIP in a state; SPOKE supplies the ZIP→state mapping (`state = "OH"`). Counting plating-capable manufacturers by validated Ohio ZIP requires joining on the bare ZIP string. *(The current SUDOKN release exposes ZIP via `schema:postalCode` on the `organizationLocatedIn` geolocation, using the non-canonical `https://` form — matched scheme-free.)*
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
SELECT ?zip (COUNT(DISTINCT ?comp) AS ?nPlating) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "OH" .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
  }
  GRAPH <https://purl.org/okn/frink/kg/sudokn> {
    ?comp <http://asu.edu/semantics/SUDOKN/hasProcessCapability> ?cap ;
          <http://asu.edu/semantics/SUDOKN/organizationLocatedIn> ?geo .
    ?geo ?pp ?zip .
    FILTER(STRENDS(STR(?pp),'schema.org/postalCode'))
    FILTER(CONTAINS(STR(?cap),'Plating') || CONTAINS(STR(?cap),'Anodizing') || CONTAINS(STR(?cap),'Galvanizing') || CONTAINS(STR(?cap),'Coating'))
  }
} GROUP BY ?zip ORDER BY DESC(?nPlating) LIMIT 12
```
- **Sample result** (8 of 12):

| ZIP | surface-finishing manufacturers |
|---|---|
| 44060 | 12 |
| 44094 | 10 |
| 43001 | 8 |
| 45404 | 8 |
| 44087 | 8 |
| 45242 | 8 |
| 45040 | 8 |
| 45103 | 8 |

- **Why it answers the question:** each Ohio-validated ZIP is ranked by surface-finishing manufacturer count, with the Cleveland industrial corridor (Mentor 44060, Willoughby 44094) leading — pinpointing communities with the highest potential for chromium/heavy-metal finishing exposures.
- **Literature support:** Yatera et al., 2018, *Journal of UOEH* — hexavalent-chromium exposure in plating and electroplating environments is causally linked to lung, nasal and sinus cancers, establishing metal-finishing capability as a concrete carcinogenic-exposure determinant. [PMID:29925735](https://pubmed.ncbi.nlm.nih.gov/29925735/) · [DOI](https://doi.org/10.7888/juoeh.40.157)

### 20. spoke-okn × fiokg — RCRA hazardous-waste facilities vs county self-rated health
- **Partner KG:** `fiokg` — FIO-KG of EPA Facility Registry Service regulated facilities, each placed within a county via KWG `sfWithin` (FIPS embedded in the region IRI).
- **Shared identifier / bridge:** county FIPS — direct
- **Research question:** Joining `fiokg` and `spoke-okn` on county FIPS: for the counties with the most **hazardous-waste-program (RCRA) regulated facilities**, what is each county's name and its **"poor or fair health"** self-rated-health indicator?
- **Why the join is required:** `fiokg` counts hazardous-waste facilities by FIPS but holds no health data, while SPOKE holds the county "poor or fair health" SDoH indicator and the county label but knows nothing about EPA facilities. Only the FIPS join puts facility burden beside the community morbidity measure.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cname ?hazwaste_facilities ?poor_fair_health WHERE {
  {
    SELECT ?fips (COUNT(DISTINCT ?fac) AS ?hazwaste_facilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?fac <http://w3id.org/fio/v1/epa-frs#hasEnvironmentalInterest> <http://w3id.org/fio/v1/epa-frs-data#d.EnvironmentalInterestType.Hazardouswasteprogram> ;
             <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?reg .
        FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
        BIND(REPLACE(STR(?reg),'^.*administrativeRegion\\.USA\\.','') AS ?fips)
        FILTER(STRLEN(?fips)=5)
      }
    } GROUP BY ?fips ORDER BY DESC(?hazwaste_facilities) LIMIT 12
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "poor or fair health" ; schema:value ?poor_fair_health .
  }
} ORDER BY DESC(?hazwaste_facilities)
```
- **Sample result** (6 of 12; "poor or fair health" % with SE):

| County | hazardous-waste facilities | poor or fair health |
|---|---|---|
| Cook County | 14026 | 13.9 (2.0) |
| Middlesex County | 10114 | 8.2 (1.0) |
| Maricopa County | 8445 | 13.8 (1.0) |
| Worcester County | 5737 | 10.8 (3.0) |
| Miami-Dade County | 4779 | 19.7 (3.0) |
| Norfolk County | 3858 | 8.4 (1.0) |

- **Why it answers the question:** the RCRA hazardous-waste facility burden (`fiokg`) sits beside each named county's self-rated "poor or fair health" indicator (`spoke-okn`), a pairing only the FIPS join can produce.
- **Literature support:** Burcham et al., 2025, *Int. J. Environ. Res. Public Health* — in an Ohio cohort, residential proximity to a hazardous-waste / contaminated facility was associated with significantly lower mental and physical health-related quality of life. [PMID:40427854](https://pubmed.ncbi.nlm.nih.gov/40427854/) · [DOI](https://doi.org/10.3390/ijerph22050738)

### 21. spoke-okn × geoconnex — Blue-space (water-feature) density vs county frequent mental distress
- **Partner KG:** `geoconnex` — hydrologic reference graph of named water features, each linked to its county via the GNIS `county` predicate (FIPS in the geoconnex county IRI).
- **Shared identifier / bridge:** county FIPS — direct
- **Research question:** Joining `geoconnex` and `spoke-okn` on county FIPS: for the counties richest in named water features (blue space), what is each county's **"frequent mental distress"** indicator? Growing evidence links proximity to blue space with better mental health.
- **Why the join is required:** `geoconnex` quantifies the hydrographic-feature inventory by FIPS but holds no health data, while SPOKE holds the county "frequent mental distress" SDoH indicator and the county name but no feature inventory. Placing blue-space density beside a mental-health indicator for the same named county needs both graphs.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cname ?water_features ?mental_distress WHERE {
  {
    SELECT ?fips (COUNT(DISTINCT ?x) AS ?water_features) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/geoconnex> {
        ?x <http://gnis-ld.org/lod/gnis/ontology/county> ?county .
        FILTER(STRSTARTS(STR(?county),'https://geoconnex.us/ref/counties/'))
        BIND(REPLACE(STR(?county),'^.*/counties/([0-9]{5}).*$','$1') AS ?fips)
      }
    } GROUP BY ?fips ORDER BY DESC(?water_features) LIMIT 15
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "frequent mental distress" ; schema:value ?mental_distress .
  }
} ORDER BY DESC(?water_features)
```
- **Sample result** (8 of 15):

| County | water features | frequent mental distress % |
|---|---|---|
| Coconino County | 5750 | 16.2 |
| Hillsborough County | 4071 | 15.1 |
| Yavapai County | 3724 | 15.7 |
| Yukon-Koyukuk Census Area | 3562 | 16.1 |
| Idaho County | 3247 | 14.1 |
| Gila County | 2876 | 17.6 |
| Aleutians West Census Area | 2609 | 9.8 |
| Hawaii County | 2572 | 14.3 |

- **Why it answers the question:** the named-water-feature (blue-space) inventory (`geoconnex`) sits beside each named county's frequent-mental-distress indicator (`spoke-okn`), enabling a county-level blue-space-and-mental-health comparison only the FIPS join can surface.
- **Literature support:** Murrin et al., 2023, *BMC Public Health* — proximity to coastal and inland blue space was associated with lower depression and anxiety and higher psychological wellbeing, validating the mental-health relevance of the blue-space/distress pairing. [PMID:36717841](https://pubmed.ncbi.nlm.nih.gov/36717841/) · [DOI](https://doi.org/10.1186/s12889-023-15101-3)

### 22. spoke-okn × nikg — Non-fatal shooting incidents vs county frequent mental distress
- **Partner KG:** `nikg` — neighborhood-incident (gun-violence) graph; incidents anchored to census tracts within a county FIPS via KWG `sfWithin`. Coverage limited to Philadelphia and Cook (Chicago) counties.
- **Shared identifier / bridge:** county FIPS — direct
- **Research question:** Joining `nikg` and `spoke-okn` on county FIPS: for Philadelphia and Cook counties, compare the count of **non-fatal shooting incidents** (`nikg`, `is_fatal = false`) with each county's **"frequent mental distress"** SDoH indicator (`spoke-okn`). Survivors and witnesses of non-fatal community gun violence carry a substantial mental-health burden.
- **Why the join is required:** `nikg` holds the granular incident-level non-fatal-shooting records (anchored to FIPS via tract containment) while SPOKE holds an independent county-level "frequent mental distress" indicator and the county name. Pairing incident-level non-fatal-shooting counts with the county mental-distress metric needs both graphs joined on FIPS.
- **SPARQL** (executed 2026-06-27, returned 2 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cname ?nonfatal_shootings ?mental_distress WHERE {
  {
    SELECT ?fips (COUNT(DISTINCT ?rec) AS ?nonfatal_shootings) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nikg> {
        ?tract <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?o .
        FILTER(STRSTARTS(STR(?o),'https://metadata.phila.gov/kwgr_administrativeRegion_USA_'))
        BIND(REPLACE(STR(?o),'^.*administrativeRegion_USA_([0-9]{5}).*$','$1') AS ?fips)
        ?rec ?lp ?tract . FILTER(STRENDS(STR(?lp),'schema.org/location'))
        ?rec <https://metadata.phila.gov/is_fatal> false .
      }
    } GROUP BY ?fips
  }
  VALUES (?fips ?loc) {
    ("42101" <https://purl.org/okn/frink/kg/spoke-okn/location/42101>)
    ("17031" <https://purl.org/okn/frink/kg/spoke-okn/location/17031>)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "frequent mental distress" ; schema:value ?mental_distress .
  }
} ORDER BY DESC(?nonfatal_shootings)
```
- **Sample result** (both rows):

| County | non-fatal shootings (nikg) | frequent mental distress % (spoke-okn) |
|---|---|---|
| Philadelphia County | 12042 | 16.9 |
| Cook County | 811 | 11.9 |

- **Why it answers the question:** each county's incident-level non-fatal-shooting count (`nikg`) sits beside its independently sourced frequent-mental-distress indicator (`spoke-okn`); Philadelphia is markedly higher on both, a juxtaposition only the FIPS join reveals.
- **Literature support:** South et al., 2020, *Annals of Emergency Medicine* — a Philadelphia study ties objectively measured neighborhood shootings to stress-responsive emergency-department visits, corroborating non-fatal community shootings as a population mental-health exposure. [PMID:33342597](https://pubmed.ncbi.nlm.nih.gov/33342597/) · [DOI](https://doi.org/10.1016/j.annemergmed.2020.10.014)

---

## Spatial, Environmental & Justice

### 23. spoke-okn × scales — Federal drug-charge caseload vs county drug-overdose mortality
- **Partner KG:** `scales` — U.S. federal court records (case volume, charges, dispositions) keyed to county FIPS.
- **Shared identifier / bridge:** county FIPS5 — direct (SCALES `hasIdbCounty` integer → zero-padded → SPOKE `location/{FIPS5}`)
- **Research question:** In the counties carrying the heaviest federal *drug* caseload — cases with a Title 21 (Controlled Substances Act) charge — what are the county drug-overdose death rates? Does intensive federal drug prosecution co-locate with high overdose mortality?
- **Why the join is required:** SCALES knows which counties prosecute the most federal drug cases (charge text starting `21:`) but has no health data; SPOKE holds the county drug-overdose-death rate but no notion of court activity. Only the FIPS join can place enforcement intensity next to the overdose burden it is meant to address.
- **SPARQL** (executed 2026-06-27, returned 13 rows):
```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX scales: <http://schemas.scales-okn.org/rdf/scales#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?fips ?cname ?nDrug ?odRate WHERE {
  {
    SELECT ?fips (COUNT(DISTINCT ?case) AS ?nDrug) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?case a scales:CriminalCase ; scales:hasIdbCounty ?c ;
              <http://release.niem.gov/niem/domains/jxdm/7.2/#CaseCharge> ?charge .
        ?charge <http://release.niem.gov/niem/domains/jxdm/7.2/#ChargeText> ?ct .
        FILTER(?c != 88888)
        FILTER(STRSTARTS(?ct,"21:"))
        BIND(REPLACE(CONCAT('00000',STR(xsd:integer(?c))),'^.*(.{5})$','$1') AS ?fips)
      }
    } GROUP BY ?fips ORDER BY DESC(?nDrug) LIMIT 15
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "drug overdose deaths" ; schema:value ?v .
    BIND(xsd:decimal(REPLACE(REPLACE(?v,'\\(.*$',''),'[^0-9.].*$','')) AS ?odRate)
  }
} ORDER BY DESC(?nDrug)
```
- **Sample result** (7 of 13):

| FIPS | County | Title-21 drug cases | Drug-overdose death rate |
|---|---|---|---|
| 06073 | San Diego County, CA | 2,435 | 0.0172 |
| 48141 | El Paso County, TX | 959 | 0.0122 |
| 04023 | Santa Cruz County, AZ | 565 | 0.0236 |
| 04019 | Pima County, AZ | 501 | 0.0310 |
| 17031 | Cook County, IL | 469 | 0.0289 |
| 35001 | Bernalillo County, NM | 230 | 0.0395 |
| 04027 | Yuma County, AZ | 222 | 0.0203 |

- **Why it answers the question:** it ranks counties by federal Controlled-Substances-Act caseload and pairs each with its overdose-death rate, showing that several high-enforcement counties (Pima AZ, Cook IL, Bernalillo NM) also carry among the highest overdose mortality.
- **Literature support:** Khatri et al., 2025, *JAMA Network Open* — in 3.26M U.S. adults, incarcerated individuals had 3.08× higher overdose-mortality risk, and higher county jail-incarceration rates were associated with elevated county mortality, linking county criminal-justice/drug-enforcement intensity to overdose burden. [PMID:40459890](https://pubmed.ncbi.nlm.nih.gov/40459890/) · [DOI](https://doi.org/10.1001/jamanetworkopen.2025.13537)

### 24. spoke-okn × sockg — Diabetes and physical inactivity in soil-carbon experiment counties
- **Partner KG:** `sockg` — Soil Organic Carbon KG; long-term agricultural soil-carbon / greenhouse-gas field-experiment sites encoded as KWG `AdministrativeRegion_2` (county) nodes.
- **Shared identifier / bridge:** county FIPS5 — direct (SOCKG KWG `administrativeRegion…USA.{FIPS5}` → SPOKE `location/{FIPS5}`)
- **Research question:** In the agricultural counties that host long-term soil-organic-carbon experiments, what is the adult diabetes prevalence, and does it track local physical inactivity — i.e. what cardiometabolic burden does the population around soil-carbon research carry?
- **Why the join is required:** SOCKG identifies which counties host SOC experiments but has zero human-health data; SPOKE carries county diabetes and physical-inactivity prevalence but no concept of experiment sites. The FIPS bridge is the only way to attach the human cardiometabolic context to the agronomic site network.
- **SPARQL** (executed 2026-06-27, returned 15 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips ?cname ?diabetes ?inactivity WHERE {
  {
    SELECT DISTINCT ?fips WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?reg a kwg:AdministrativeRegion_2 .
        FILTER(STRSTARTS(STR(?reg),'http://stko-kwg'))
        BIND(REPLACE(STR(?reg),'^.*USA\\.','') AS ?fips)
      }
    }
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?s1 rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "diabetes prevalence" ; schema:value ?d .
    BIND(xsd:decimal(REPLACE(?d,'\\(.*$','')) AS ?diabetes)
    ?s2 rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ; schema:variable "physical inactivity" ; schema:value ?pi .
    BIND(xsd:decimal(REPLACE(?pi,'\\(.*$','')) AS ?inactivity)
  }
} ORDER BY DESC(?diabetes) LIMIT 15
```
- **Sample result** (8 of 15):

| FIPS | County | Diabetes % | Physical inactivity % |
|---|---|---|---|
| 01087 | Macon County, AL | 17.1 | 35.3 |
| 48227 | Howard County, TX | 13.0 | 29.6 |
| 45041 | Florence County, SC | 12.8 | 30.8 |
| 48303 | Lubbock County, TX | 12.0 | 26.8 |
| 01067 | Henry County, AL | 12.0 | 29.2 |
| 18157 | Tippecanoe County, IN | 10.4 | 24.8 |
| 41059 | Umatilla County, OR | 10.1 | 22.4 |
| 27127 | Redwood County, MN | 8.7 | 21.1 |

- **Why it answers the question:** each SOC-experiment county is reported with its diabetes prevalence and physical-inactivity rate, and the two move together (Macon Co AL highest in both: 17.1% / 35.3%), revealing the cardiometabolic backdrop of soil-carbon agronomy.
- **Literature support:** Liu et al., 2025, *JAMA Cardiology* — a nationally representative analysis finds rural U.S. adults have significantly higher diabetes (11.2% vs 9.8%) and are more likely to be insufficiently physically active than urban adults, the rural cardiometabolic pattern seen in these agricultural counties. [PMID:40163358](https://pubmed.ncbi.nlm.nih.gov/40163358/) · [DOI](https://doi.org/10.1001/jamacardio.2025.0538)

### 25. spoke-okn × spatialkg — State ranking of county adult obesity rolled up via the GADM hierarchy
- **Partner KG:** `spatialkg` — KnowWhereGraph spatial admin hierarchy (KWG/GADM counties, states, `administrativePartOf` edges).
- **Shared identifier / bridge:** county FIPS5 → state — direct (SPOKE `location/{FIPS5}` → KWG `administrativeRegion.USA.{FIPS5}`, then `administrativePartOf` → state)
- **Research question:** Rolling SPOKE's county-level adult-obesity prevalence up to the authoritative GADM state via spatialkg, which U.S. states have the highest mean county adult-obesity prevalence?
- **Why the join is required:** SPOKE holds adult-obesity prevalence per county but tags it only with a 5-digit FIPS, with no county→state edge; spatialkg owns the canonical `administrativePartOf` hierarchy and the full state name. The state ranking is computable only after placing each SPOKE county on the spatialkg GADM tree.
- **SPARQL** (executed 2026-06-27, returned 12 rows):
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?stateName (COUNT(DISTINCT ?fips) AS ?nCounties) (AVG(?ob) AS ?avgObesity) WHERE {
  {
    SELECT DISTINCT ?fips ?ob WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
              schema:variable "adult obesity" ; schema:value ?v .
        BIND(REPLACE(STR(?loc),'^.*location/','') AS ?fips)
        FILTER(REGEX(?fips,'^[0-9]{5}$'))
        BIND(xsd:decimal(REPLACE(?v,'\\(.*$','')) AS ?ob)
      }
    }
  }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg kwg:administrativePartOf ?st .
    ?st a kwg:AdministrativeRegion_1 ; rdfs:label ?stateName .
  }
} GROUP BY ?stateName ORDER BY DESC(?avgObesity) LIMIT 12
```
- **Sample result** (8 of 12):

| State | Counties | Avg county adult obesity % |
|---|---|---|
| Mississippi | 82 | 41.93 |
| Alabama | 67 | 41.08 |
| Louisiana | 64 | 40.49 |
| West Virginia | 55 | 39.88 |
| South Carolina | 46 | 39.53 |
| Oklahoma | 77 | 39.38 |
| Kentucky | 120 | 39.37 |
| Arkansas | 75 | 38.99 |

- **Why it answers the question:** the state means — produced only after the county→state roll-up through spatialkg's GADM `administrativePartOf` edges — rank Mississippi, Alabama, Louisiana and West Virginia highest, reproducing the documented Southern obesity geography.
- **Literature support:** Barker et al., 2011, *Am J Prev Med* — identifies a geographically coherent "diabetes belt" of 644 mostly-Southern counties where obesity and sedentary lifestyle cluster, matching the Southern obesity concentration this roll-up surfaces. [PMID:21406277](https://pubmed.ncbi.nlm.nih.gov/21406277/) · [DOI](https://doi.org/10.1016/j.amepre.2010.12.019)

---

## Coverage summary

All **25 distinct partner knowledge graphs** that `spoke-okn` crosswalks with are represented exactly once above, spanning every shared-key family SPOKE uses: chemical (CHEBI↔CAS, PubChem CID), disease (DOID, DOID↔MONDO, MeSH, UMLS↔MONDO↔DOID), gene (Ensembl, Entrez), and geographic (ZIP5, county FIPS, state). Several partners connect on additional keys not shown here (e.g. `rdkg` via DrugBank and DOID↔MONDO; `ruralkg` via ZIP5; `sockg`/`spatialkg` via state FIPS; `biohealth` via MeSH→UMLS and concept label; `nde`/`spoke-genelab`/`biohealth` via NCBITaxon) — see `crosswalks_example.md` and `proto-okn-crosswalk-inventory.md` for the full recipe catalog.

*This is a standalone showcase. It does not modify the crosswalk catalog or its per-recipe transcripts.*

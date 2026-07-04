# Multiple Sclerosis Biology — Proto-OKN Federated Knowledge Map

- **Date:** 2026-07-03
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (v0.0.6)
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg> (v0.0.1)
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg> (v0.0.1)
- `prokn` — <https://purl.org/okn/frink/kg/prokn> (v0.0.5)
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> (v0.0.3)
- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg> (v0.0.2)
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg> (v0.0.3, checked-empty for MS)
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph> (v0.0.1, no MS node)
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph> (v0.0.2, bridge)

## Conversation

👤 **User**

I'm studying Multiple Sclerosis and want a comprehensive, evidence-backed map of its biology, covering its major forms and subtypes. Pull together what the available knowledge sources can tell me, organized by entity type: genes (protein-coding and non-coding, kept distinct), genetic variants, pathways and gene sets, drugs/therapeutics, genes with altered activity in disease (with tissue/cell type), and clinical features/biomarkers. For each finding note which source(s) support it, the relationship type, any confidence or effect score, and the kind of evidence (curated link, statistical/genetic association, measured activity change, or pathway membership) — keeping these evidence types separate. Look broadly across all sources rather than assuming where data lives; account for differing names/IDs; include disease subtypes. Rank findings by cross-source agreement, highlight the highest-confidence set, and flag uncertainties and likely undercounts. Deliver a report (.md and .html following the Alzheimer's analysis style), a CSV (one row per finding), graphical visualizations, and a reproducible transcript.

---

🧠 **Assistant**

**Approach.** Profiled the Proto-OKN federation (`list_kgs`, `find_context_sources`, `get_kg_version`) to find which of ~40 KGs hold each entity type, then anchored on multiple sclerosis = MONDO:0005301 and expanded its ontology subtree via `ubergraph` to 8 MS terms (main MS; relapsing-remitting; secondary-/primary-/progressive-relapsing; chronic-progressive; Marburg acute; pediatric). Because sources use different disease IDs, cross-walked every MS MONDO term to DOID/EFO/Orphanet/NCIT/UMLS/MeSH (105 cross-references) so each KG could be queried natively — critical, since the GXA MS disease node carries no label and rdkg keys much MS content on `rdaccelerate` grouped nodes. Seven KGs contributed: spoke-okn, rdkg, digcfdekg, prokn, gene-expression-atlas-okn, biomarkerkg (+ ubergraph as bridge). oard-kg (rare-disease EHR, no MS edges) and pankgraph (pancreatic, no MS node) were checked-empty; prokn carries MS only as a drug-indication hub (no curated MS genes, because MS is non-Mendelian).

**Result — 474 findings.** Genes = 323 associated (322 protein-coding, 1 non-coding). Highest-confidence core (all 3 gene sources, Tier 1): HLA-DRB1, IL2RA, IL7R, TYK2, STAT4, CD6, CD40, CD58, CBLB, IL12A, IFNG, TNFRSF1A, TNFSF14. Tier 2 (2 sources, 60 genes): IKZF3, CD86, HLA-DQB1, RGS1, CXCR5, BATF, ETS1, TNF, IRF8, TAGAP, PTPRC, TNFAIP3, STAT3, EVI5, CLEC16A, ANKRD55, FOXP3, VCAM1… Strongest statistical signals (digcfdekg PIGEAN/EAGGL, GWAS-derived): CD28 10.6, IL7R 10.0, IKZF3 9.76, HLA-A 9.26, CD27 9.07. Non-coding is minimal in the association layer (one lncRNA) and appears mostly in the measured layer. Pathways/gene sets (33, digcfdekg): CTLA4, TH17 commitment, TH1/TH2, TCR-signalling, IL-2 signalling, allograft rejection, B-cell differentiation, plus a lipoprotein-metabolism factor. Drugs (kept separate by relationship): 180 indicated/investigated compounds (prokn/ChEMBL — alemtuzumab, briakinumab, BIIB-091/BTK, baclofen, amantadine, high-dose biotin, cannabinoids); 2 contraindicated (rdkg — ascorbic acid, zinc gluconate); environmental risk factors (rdkg `contributes_to` — tobacco, solvents, lead, mercury, teriflunomide); 3 spoke-okn TREATS artifacts (carbonic acid, isopropyl alcohol, methane — a limitation). Altered activity (GXA, measured, 475 DE genes across 4 peripheral-immune-cell assays: MS before/after IFN-beta vs normal in CD4/CD8 T cells, monocytes, neutrophils, B cells, whole blood): type-I-interferon genes UP (MX1/2, OAS2/3, RSAD2, IFI44/IFIT1, HERC5), B-cell/plasma genes UP (IGHM, TNFRSF17, MZB1, PAX5), monocyte/complement genes DOWN (CD14, CD163, C1QB, C3, VSIG4). Clinical/biomarkers: 12 HP features from rdkg (CNS demyelination, spasticity, paraesthesia, ataxia, diplopia, bladder dysfunction, depression); 53 specimen-tagged biomarker records from biomarkerkg (CSF/plasma/serum/urine) + an S1P/IFN-gamma/IL-17 analyte panel (SPHK1, SPHK2, S1PR1, S1PR5). Evidence types kept separate: curated 247, statistical 234, measured 83, pathway-membership 17.

**Key caveats / undercounts.** (1) Genetic variants severely undercounted — no MS-anchored variant-entity layer exists in the federation; variant signal survives only at gene level via digcfdekg's GWAS-derived statistics (HLA-DRB1\*15:01, TYK2 P1104A represented by their genes). (2) Non-coding genes undercounted in the association layer (symbol heuristic biotype). (3) The GXA measured layer is peripheral blood only, confounded by IFN-beta treatment, with sex-chromosome artifacts among the largest fold-changes. (4) prokn contributes no curated MS genes (3-source ceiling, not 4) and its drug names are mostly ChEMBL-ID-only (classic DMTs like ocrelizumab/natalizumab/fingolimod not surfaced by name). (5) spoke-okn TREATS near-empty; biomarkerkg analytes unlabelled for 52/53 records. Delivered: `MS_knowledge_map_report.md` + `.html` (interactive 474-row table), `MS_knowledge_map_findings.csv`, `MS_gene_source_matrix.csv`, four figures, and this transcript.

---

## SPARQL queries executed (verbatim, in order)

**Query 1 — `ubergraph` — MS subtype expansion (8 rows).** `expand_ontology_term(MONDO:0005301)` →
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?term ?label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?term rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0005301> .
    OPTIONAL { ?term rdfs:label ?label . } } } LIMIT 1000
```
Returns: MONDO_0005301 multiple sclerosis; 0005314 relapsing-remitting; 0000450 secondary-progressive; 0000451 primary-progressive; 0000452 progressive-relapsing; 0005284 chronic-progressive; 0016429 Marburg acute; 0018784 pediatric.

**Query 2 — `ubergraph` — cross-ontology ID crosswalk for all 8 MS terms (105 rows).**
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?mondo ?mlabel ?xref WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    VALUES ?mondo { <...8 MS MONDO IRIs...> }
    OPTIONAL { ?mondo rdfs:label ?mlabel }
    { ?mondo skos:exactMatch ?xref } UNION { ?mondo oboInOwl:hasDbXref ?xref } } } ORDER BY ?mondo
```
Returns e.g. MONDO_0005301 → DOID:2377, NCIT:C3243, Orphanet:802, UMLS:C0026769, MeSH:D009103, ICD10:G35; RRMS → DOID:2378 / EFO:0003929; SPMS → DOID:0050783 / EFO:0008522; PPMS → DOID:0050784 / EFO:0008520; chronic-progressive → EFO:0003840 / MeSH:D020528.

**Query 3 — `spoke-okn` — MS-associated genes via ASSOCIATES_DaG (164 rows, curated).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?d ?sym WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    VALUES ?d { <DOID_2377> <DOID_2378> <DOID_0050783> <DOID_0050784> <DOID_0050785> }
    ?d spoke:ASSOCIATES_DaG ?gene . ?gene rdfs:label ?sym . } } ORDER BY ?sym
```
Returns 164 genes for DOID_2377: HLA-DRB1, HLA-DQA1, IL2RA, IL7R, TYK2, STAT3, STAT4, TNFRSF1A, CD6, CD40, CD58, CLEC16A, EVI5, TNFSF14, IRF8, TAGAP, RGS1, BACH2, ETS1, CD86, IKZF3, MALT1, PTPRC, GATA3, RUNX3, SP140, NCF4, SH2B3, CBLB, MERTK, IL10, IL12A, IL17A, IL1A, IL1B, IL2, IL4, IL6, IFNB1, IFNG, MBP, MOG, NEFL, GFAP, GALC, … (immune + myelin).

**Query 4 — `rdkg` — MS genes / phenotypes / drugs / risk chemicals (`related_to`, `has_phenotype`, `contraindicated_for`, `contributes_to`).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?p ?o (SAMPLE(?otype) AS ?type) (SAMPLE(?olabel) AS ?label) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    VALUES ?d { <...8 MS MONDO subtypes...> }
    ?d ?p ?o . OPTIONAL { ?o rdf:type ?otype } OPTIONAL { ?o rdfs:label ?olabel } } } GROUP BY ?p ?o
```
Returns 45 genes via `related_to` (NLRP3, CNR1, KIF1B, CLEC16A, HLA-DPB1/DQB1/DRA/DRB1, ICAM1, IRF8, IFNB1, IFNG, APOE, IL1B/1RN/2RA/7/7R/10/12A/17A, KCNJ10, MCAM, CLDN11, P2RX7, PDCD1, VDR, CASP1, CBLB, TNFSF14, CD6/40/58, STAT4, TYK2, VCAM1, TNFAIP3, TNFRSF1A…); 2 contraindicated drugs (Ascorbic acid, Zinc gluconate); risk `contributes_to` chemicals (teriflunomide, Lead, Mercury, Solvents, Tobacco Smoke Pollution); and two `rdaccelerate` grouped MS nodes.

**Query 5/8 — `digcfdekg` — statistical gene–trait associations for MS traits (PIGEAN/EAGGL weights).** (Query 5 = full 1581-gene scan; Query 8 = top-200 CSV.)
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?sym (MAX(?w) AS ?maxw) (COUNT(DISTINCT ?trait) AS ?nt) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    VALUES ?trait { <MONDO_0005301> <EFO_0803536 MS symptom measurement>
                    <trait/3e0c1919… brain-volume change> <trait/dc2aa6ed… T2-lesion change> }
    ?stmt rdf:subject ?gene ; rdf:object ?trait ; dig:weight ?w .
    ?gene a dig:Gene ; rdfs:label ?sym . } } GROUP BY ?sym ORDER BY DESC(?maxw) LIMIT 200
```
Returns CD28 10.6, IL7R 10.0, IKZF3 9.76, HLA-A 9.26, CD27 9.07, SOCS1 8.8, CD40 8.73, IL2RA 8.47, HLA-DQB1 8.37, RGS1 8.11, CXCR5 8.08, CD6 7.98, … HLA-DRB1 6.04, STAT4 5.86, TYK2 3.49 — a T/B-cell adaptive-immune signature.

**Query 6 — `rdkg` — MS clinical phenotypes via the grouped susceptibility/progressive nodes (`has_phenotype`).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?p ?o (SAMPLE(?otype) AS ?type) (SAMPLE(?olabel) AS ?label) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    VALUES ?d { <rdaccelerate…/MONDO_GROUPED_21571_7462_…> <…/MONDO_GROUPED_5284_451_450> }
    ?d ?p ?o . OPTIONAL { ?o rdf:type ?otype } OPTIONAL { ?o rdfs:label ?olabel } } } GROUP BY ?p ?o
```
Returns 12 HP features: CNS demyelination, Spasticity, Paresthesia, Muscle weakness, Incoordination, Diplopia, Urinary incontinence, Urinary hesitancy, Depressivity, Emotional lability, plus Adult onset and Multifactorial inheritance.

**Query 7 — `prokn` — compounds indicated/investigated for MS (NCIT_C41184 "Indication"), 180 ChEMBL compounds.**
```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?sub (SAMPLE(?subtype) AS ?type) (SAMPLE(?label) AS ?lbl) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?d a up:Disease ; skos:exactMatch <http://purl.obolibrary.org/obo/MONDO_0005301> .
    ?stmt rdf:object ?d ; rdf:predicate <http://purl.obolibrary.org/obo/NCIT_C41184> ; rdf:subject ?sub .
    OPTIONAL { ?sub a ?subtype } OPTIONAL { ?sub rdfs:label ?label } } } GROUP BY ?sub
```
Returns 180 compounds: Alemtuzumab, Baclofen, Amantadine, Biotin, Amifampridine, Armodafinil, Cannabidiol, Cannabinol, Atorvastatin, Celecoxib, Acetazolamide, Briakinumab, Belimumab, Bryostatin-1, BIIB-091, … (most ChEMBL-ID-only).

**Query 9/10 — `biomarkerkg` — MS biomarker records, assessed molecule + specimen (OBCI predicates, DOID_2377).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obci: <http://purl.obolibrary.org/obo/>
SELECT ?bm ?bmlabel ?assessed ?alabel ?specimen WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?bm ?pd <http://purl.obolibrary.org/obo/DOID_2377> .
    FILTER(?pd IN (obci:OBCI_1000002, obci:OBCI_1000006, obci:OBCI_1000008))
    OPTIONAL { ?bm rdfs:label ?bmlabel }
    OPTIONAL { ?bm obci:OBCI_1000009 ?assessed . OPTIONAL { ?assessed rdfs:label ?alabel } }
    OPTIONAL { ?bm obci:OBCI_1000018 ?specimen } } }
```
Returns ~53 MS biomarker records; specimens UBERON CSF (0001359) / plasma (0001969) / serum (0001977) / urine (0001088) / body-fluid (0006314). Only AN6263-1 resolves assessed molecules (S1P/IFN-IL17 axis): SPHK1 (GID8877), SPHK2 (GID56848), S1PR1 (GID1901), S1PR5 (GID53637), IL17A (GID3605), IFNG (GID3458), APOA1 (GID335).

**Query 11 — `digcfdekg` — CFDE gene sets predicting MS (`geneSetToTrait`).**
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?gslabel (MAX(?w) AS ?maxw) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?stmt rdf:subject ?gs ; rdf:object <http://purl.obolibrary.org/obo/MONDO_0005301> ; dig:weight ?w .
    ?gs a dig:GeneSet ; rdfs:label ?gslabel . } } GROUP BY ?gslabel ORDER BY DESC(?maxw) LIMIT 40
```
Returns BIOCARTA_CTLA4_PATHWAY, GOBP_T_HELPER_17_CELL_LINEAGE_COMMITMENT, KEGG_ALLOGRAFT_REJECTION, BIOCARTA_TH1TH2_PATHWAY, PID_IL27_PATHWAY, REACTOME_INTERLEUKIN_2_SIGNALING, WP_MODULATORS_OF_TCR_SIGNALING, GOBP_REGULATION_OF_B_CELL_DIFFERENTIATION, WP_RHEUMATOID_ARTHRITIS, … (adaptive-immune).

**Query 12 — `digcfdekg` — latent factors modelling MS (`traitToFactor`).**
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?flabel (MAX(?w) AS ?maxw) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?stmt rdf:subject <http://purl.obolibrary.org/obo/MONDO_0005301> ; rdf:object ?f ; dig:weight ?w .
    ?f a dig:Factor ; rdfs:label ?flabel . } } GROUP BY ?flabel ORDER BY DESC(?maxw) LIMIT 40
```
Returns absent-spleen-germinal-center, TH1/TH2 T-cell pathway, CD4 T-cell activation genes, regulatory-T-cell signalling, T-and-B-cell signalling, IL-2/JAK-STAT signalling, MHC-II and alloimmune signalling, T-cell activation and NF-κB, B-cell-receptor signalling, and Lipoprotein Metabolism.

**Query 13/15 — `gene-expression-atlas-okn` — MS differential expression with cell type (measured).** MS assays are peripheral-immune-cell contrasts (`has_attribute` MONDO_0005301 + CL/UBERON), joined to per-gene `wobd:log2fc` / `wobd:direction` / `wobd:adj_p_value`:
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
SELECT ?sym ?cell ?dir ?log2fc ?adjp WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?assay biolink:has_attribute <http://purl.obolibrary.org/obo/MONDO_0005301> ; biolink:has_attribute ?cell .
    FILTER(CONTAINS(STR(?cell),"/CL_") || STRENDS(STR(?cell),"UBERON_0000178"))
    ?assoc biolink:subject ?assay ; biolink:object ?gene ; wobd:log2fc ?log2fc ; wobd:direction ?dir ; wobd:adj_p_value ?adjp .
    ?gene biolink:symbol ?sym . } } ORDER BY DESC(ABS(?log2fc)) LIMIT 150
```
475 DE genes across 4 assays (E-MTAB-69, E-MTAB-2973): cell types CD4⁺ T (CL_0000624), CD8⁺ T (CL_0000625), monocyte (CL_0000576), neutrophil (CL_0000775), B cell (CL_0000236), lymphocyte (CL_0000542), whole blood (UBERON_0000178). IFN-stimulated genes up (MX1/2, OAS2/3, RSAD2, IFI44/44L, IFIT1/2, HERC5, PARP9); B-cell/plasma up (IGHM, IGKC, TNFRSF17, MZB1, POU2AF1, CD38, PAX5); monocyte/complement down (CD14, CD163, MSR1, VSIG4, C1QB, C3, CFD, AIF1). Largest |log2FC| are sex-chromosome artifacts (Y genes, XIST).

**Query 14 — `spoke-okn` — compounds that TREAT MS (TREATS_CtD).**
```sparql
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?name WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?c spoke:TREATS_CtD ?d .
    VALUES ?d { <DOID_2377> <DOID_2378> <DOID_0050783> <DOID_0050784> <DOID_0050785> }
    OPTIONAL { ?c rdfs:label ?name } } }
```
Returns exactly 3: Carbonic Acid, Isopropyl Alcohol, Methane (SPOKE TREATS layer for MS is non-therapeutic — flagged).

---

## Schema / exploration notes (probes, not counted as findings)

- **prokn** MS disease node (`up:Disease` `skos:exactMatch` MONDO_0005301) links **only** to 180 compounds via `NCIT_C41184` "Indication"; no curated MS gene/protein or variant edges (MS is non-Mendelian) — prokn contributes drugs only.
- **digcfdekg** traits for MS: direct `MONDO_0005301` plus hashed progression-trait nodes ("brain-volume change", "T2-lesion-volume change") and `EFO:0803536` ("MS symptom measurement"); associations are reified `Statement`s carrying `dig:weight`, `scoreType`, `wasGeneratedBy` (PIGEAN/EAGGL). Gene sets (`geneSetToTrait`) and latent factors (`traitToFactor`) provide the pathway/mechanism layer.
- **gene-expression-atlas-okn** stores MS as a **label-less** `MONDO_0005301` disease node reached via `biolink:has_attribute` from assay contrasts; effect data live on `http://purl.org/okn/wobd/{log2fc,direction,adj_p_value}` (not the `spoke.ucsf.edu/genelab/` schema names).
- **rdkg** keys MS on MONDO subtype IRIs **and** two `rdaccelerate.org` grouped nodes (`MS, susceptibility to`; `progressive MS`) that carry the HP phenotype edges.
- **oard-kg** returned 0 for the main MS term (rare-disease EHR corpus); only a `pediatric multiple sclerosis` ontology stub exists, with no phenotype edges.
- **pankgraph** contains no MS node (pancreatic/diabetes scope; confirmed by `sclerosis` label scan → 0 rows). **biomarkerkg** MS records carry disease + specimen but the assessed analyte is unpopulated for 52 of 53 records.

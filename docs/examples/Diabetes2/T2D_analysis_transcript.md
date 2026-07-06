# Type 2 Diabetes Biology — Proto-OKN Federated Knowledge Map

- **Date:** 2026-07-05
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

I'm studying Diabetes Type 2 and want a comprehensive, evidence-backed map of its biology, covering its major forms and subtypes, organized by entity type: genes (protein-coding and non-coding kept distinct), genetic variants, pathways/gene sets, drugs/therapeutics, genes with altered activity in disease (with tissue/cell type), clinical features/biomarkers, and prevalence at geolocations with correlations to social determinants of health. For each finding note which source(s) support it, the relationship type, any confidence/effect score, and the evidence kind (curated link, statistical/genetic association, measured activity change, or pathway membership) — kept separate. Look broadly across all sources; account for differing names/IDs; include subtypes. Rank by cross-source agreement, highlight the highest-confidence set, and flag uncertainties/undercounts. Deliver a report (html + md), a CSV (one row per finding), graphical visualizations, an OpenStreetMap-based prevalence map, and a reproducible transcript.

---

🧠 **Assistant**

**Approach.** Profiled the FRINK federation (list_kgs, find_context_sources, list_crosswalks, get_join_strategy) to find which of ~40 KGs hold each entity type for T2D, then anchored on type 2 diabetes mellitus = MONDO:0005148 and expanded its ontology subtree via ubergraph to 7 terms (T2D; lipoatrophic diabetes; non-insulin-dependent diabetes 1–5). Cross-walked every term to DOID/OMIM/EFO/UMLS/MeSH/SNOMED (75 cross-refs) so each KG could be queried natively — spoke-okn keys diabetes only at the PARENT term DOID:9351, and EFO:0004541 turned out to be HbA1c (not T2D) and was excluded. Nine KGs: spoke-okn, rdkg, digcfdekg, prokn, pankgraph, gene-expression-atlas-okn, biomarkerkg (+ oard-kg checked-empty, ubergraph as bridge).

**Result — 1,327 findings.** Genes = 966 (905 coding, 61 non-coding). Tier 1 (all 4 gene sources): ABCC8, GCK, HNF1A, HNF1B, HNF4A, IRS1, KCNJ11, PDX1, PPARG, SLC2A2, WFS1 — the β-cell K-ATP / glucokinase / MODY core. Tier 2 (3 sources): TCF7L2, SLC30A8, KCNQ1, CDKAL1, IGF2BP2, INS, GLIS3, ADCY5, JAZF1, FTO, GLP1R, ADIPOQ, LEP, LEPR, IRS2, INSR, AKT2, PAX4, SLC2A4, ENPP1, PPARGC1A. Strongest statistical signal (digcfdekg PIGEAN, GWAS): INS 10.3, LEP 9.77, GCK 9.73, WFS1 8.62, HNF1A 8.6, TCF7L2 7.85. Non-coding: islet microRNAs (MIR375, MIR29 family). Pathways/gene sets (26): KEGG_MODY, REACTOME_beta_cell_gene_expression, KEGG_type_II_diabetes, WP_adipogenesis, WP_ceramides_insulin_resistance, REACTOME_leptin. Drugs: 295 indicated (prokn/ChEMBL — metformin, SGLT2i, DPP-4i, GLP-1, sulfonylureas, TZDs); 20 contraindicated (rdkg). Altered activity: pankgraph islet β-cell (CL:0000169) — loss of HNF1A/MTNR1B/FFAR4/GPR119, gain of NUPR1/IRF8/RETN; GXA — islet (66 up), retina (13 up), liver (5 up). Variants: ~19,400 pankgraph islet cis-eQTLs. Clinical/biomarkers: insulin resistance, waist-to-hip ratio, late onset (rdkg); 27 biomarker records (biomarkerkg). Environmental: 44 exposures (rdkg — arsenic, BPA, PFOA/PFOS, PCBs). Evidence separated: curated 1,032, statistical 284, measured 43, pathway 26, geospatial 50.

**Geo + SDoH.** Diabetes belt: Mississippi 14.2%, Louisiana 12.8% → Massachusetts 7.3%. County SDoH correlations (Pearson r, ~3,100 counties): poor/fair health 0.94, physical inactivity 0.87, child poverty 0.82, food insecurity 0.74, obesity 0.74; protective: education −0.77, life expectancy −0.65.

**Delivered:** T2D_knowledge_map_report.md + .html (interactive OpenStreetMap / Leaflet prevalence map + ranked state-prevalence bar + searchable 1,327-row table), a standalone full-screen OpenStreetMap (T2D_prevalence_map.html), T2D_knowledge_map_findings.csv, T2D_gene_source_matrix.csv, six figures, and this transcript. Caveats flagged: spoke-okn is parent-term (T2D proxy); variants undercounted (islet eQTLs, not disease-anchored); pankgraph curated gene–condition layer is type-1; EFO HbA1c excluded; SDoH/prevalence ecological.

## SPARQL queries executed

#### Query 1

_2026-07-05T23:08:57+00:00 · `ubergraph`_ — T2D subtype expansion (7 terms)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?term ?label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?term rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0005148> .
    OPTIONAL { ?term rdfs:label ?label . }
  }
} LIMIT 1000
```

_7 rows_ — MONDO_0005148 type 2 diabetes mellitus; MONDO_0005827 lipoatrophic diabetes; MONDO_0011027/0011072/0011363/0011955/0014488 non-insulin-dependent diabetes mellitus 1–5.

#### Query 2

_2026-07-05T23:09:36+00:00 · `ubergraph`_ — cross-ontology ID crosswalk (75 rows)

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?mondo ?mlabel ?xref WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    VALUES ?mondo { <MONDO_0005148> <MONDO_0005827> <MONDO_0011027> <MONDO_0011072> <MONDO_0011363> <MONDO_0011955> <MONDO_0014488> }
    OPTIONAL { ?mondo rdfs:label ?mlabel }
    { ?mondo skos:exactMatch ?xref } UNION { ?mondo oboInOwl:hasDbXref ?xref }
  }
} ORDER BY ?mondo
```

_75 rows_ — MONDO_0005148 → DOID:9352, OMIM:125853, ICD10CM:E11, UMLS:C0011860, MeSH:D003924, NCIT:C26747, SNOMED:44054006; NIDDM1–5 → OMIM 601283/601407/603694/608036/616087; lipoatrophic → DOID:11712, EFO:0007346.

#### Query 3 / 7

_`rdkg`_ — T2D-subtype genes / microRNAs / contraindicated drugs / environmental contributors (related_to, contributes_to, has_phenotype, contraindicated_for)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT DISTINCT ?p ?olabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    VALUES ?d { <MONDO_0005148> <MONDO_0005827> <MONDO_0011027> <MONDO_0011072> <MONDO_0011363> <MONDO_0011955> <MONDO_0014488> }
    VALUES ?p { biolink:related_to biolink:contributes_to biolink:has_phenotype biolink:contraindicated_for }
    ?d ?p ?o . OPTIONAL { ?o rdfs:label ?olabel }
  }
}
```

_298 rows_ — ~180 genes (ABCC8, TCF7L2, KCNJ11, KCNQ1, HNF1A/1B/4A, GCK, WFS1, SLC30A8, PPARG, IRS1/2, MTNR1B, IGF2BP2, THADA, JAZF1, NOTCH2…) + islet microRNAs (MIR375, MIR29 family, MIR126…); 5 phenotypes (insulin resistance, increased waist-to-hip ratio, late onset…); 20 contraindicated drugs (thiazides, β-blockers, reserpine); 44 environmental contributors (arsenic, cadmium, BPA, PFOA/PFOS, PCBs, air pollutants).

#### Query 4

_2026-07-05T23:14:34+00:00 · `digcfdekg`_ — statistical gene weights, T2D (MONDO:0005148) + EFO:0004541 (later found = HbA1c and dropped)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?sym (MAX(?w) AS ?maxw) (COUNT(DISTINCT ?trait) AS ?nt) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    VALUES ?trait { <MONDO_0005148> <http://www.ebi.ac.uk/efo/EFO_0004541> }
    ?stmt rdf:subject ?gene ; rdf:object ?trait ; dig:weight ?w . ?gene rdfs:label ?sym .
  }
} GROUP BY ?sym ORDER BY DESC(?maxw) LIMIT 300
```

_300 rows_ — mixed T2D + HbA1c (erythrocyte genes flagged this trait as HbA1c).

#### Query 9

_2026-07-05T23:16:38+00:00 · `digcfdekg`_ — CLEAN T2D-only statistical gene weights (MONDO:0005148)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?sym (MAX(?w) AS ?maxw) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?stmt rdf:subject ?gene ; rdf:object <MONDO_0005148> ; dig:weight ?w . ?gene rdfs:label ?sym .
  }
} GROUP BY ?sym ORDER BY DESC(?maxw) LIMIT 250
```

_250 rows_ — INS 10.3, LEP 9.77, GCK 9.73, GCKR 8.97, WFS1 8.62, HNF1A 8.6, GIPR 8.34, IRS1 8.29, SLC2A2 8.18, KCNJ11 8.13, PPARG 8.06, TCF7L2 7.85, SLC30A8 7.67, HNF4A 7.54, GLP1R 7.32, FTO 6.92, HNF1B 6.9, CDKAL1 6.55, GLIS3 6.43 …

#### Query 5 / 8

_`prokn`_ — T2D relationship distribution: 295 ChEMBL "Indication" (NCIT_C41184) + 13 genes/proteins (associated_with)

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?rel (COUNT(DISTINCT ?s) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?d a up:Disease ; skos:exactMatch <MONDO_0005148> .
    ?stmt rdf:object ?d ; rdf:subject ?s ; rdf:predicate ?relx . BIND(STR(?relx) AS ?rel)
  }
} GROUP BY ?rel ORDER BY DESC(?n)
```

#### Query 16

_2026-07-05T23:23:27+00:00 · `prokn`_ — named T2D drug indications (ChEMBL labels)

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?lbl WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?d a up:Disease ; skos:exactMatch <MONDO_0005148> .
    ?stmt rdf:object ?d ; rdf:predicate <http://purl.obolibrary.org/obo/NCIT_C41184> ; rdf:subject ?s . ?s rdfs:label ?lbl .
  }
} ORDER BY ?lbl
```

Named agents: metformin; SGLT2 inhibitors (canagliflozin, dapagliflozin, empagliflozin, ertugliflozin, bexagliflozin, sotagliflozin); DPP-4 inhibitors (sitagliptin, saxagliptin, linagliptin, alogliptin, vildagliptin); sulfonylureas (glimepiride, glipizide, glyburide, gliclazide); meglitinides (repaglinide, nateglinide); TZDs (pioglitazone, rosiglitazone); α-glucosidase inhibitors (acarbose, miglitol, voglibose); glucokinase activators (dorzagliatin); imeglimin; bromocriptine; GLP-1-axis small molecules (orforglipron, danuglipron).

#### Query 25

_2026-07-05T23:31:12+00:00 · `prokn`_ — curated T2D genes (associated_with, 13)

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?s ?lbl WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?d a up:Disease ; skos:exactMatch <MONDO_0005148> .
    ?stmt rdf:object ?d ; rdf:predicate <https://biolink.github.io/biolink-model/associated_with> ; rdf:subject ?s . OPTIONAL { ?s rdfs:label ?lbl }
  }
}
```

_13 rows_ — ABCC8, HNF4A, GCK, WFS1, PPARG, HNF1A, PDX1, SLC2A2, RBPJ, IRS1, KCNJ11, ENPP1, HNF1B.

#### Query 10

_2026-07-05T23:18:00+00:00 · `spoke-okn`_ — diabetes-associated genes (ASSOCIATES_DaG, parent DOID_9351, 678)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?sym WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    <http://purl.obolibrary.org/obo/DOID_9351> spoke:ASSOCIATES_DaG ?gene . ?gene rdfs:label ?sym .
  }
} ORDER BY ?sym
```

#### Query 11

_2026-07-05T23:18:02+00:00 · `spoke-okn`_ — TREATS / CONTRAINDICATES for diabetes (flagged unreliable — spurious chemical entries only; prokn indications used instead)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?rel ?name WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?c spoke:TREATS_CtD <http://purl.obolibrary.org/obo/DOID_9351> . BIND("treats" AS ?rel) }
    UNION { ?c spoke:CONTRAINDICATES_CcD <http://purl.obolibrary.org/obo/DOID_9351> . BIND("contraindicated" AS ?rel) }
    ?c rdfs:label ?name .
  }
} ORDER BY ?rel ?name
```

#### Query 6 / 18 / 19

_`pankgraph`_ — islet β-cell (CL_0000169) T2D-vs-non-diabetic open-chromatin gene-activity (measured). Up in T2D β-cells: NUPR1, IRF8, IL27, FABP5, RETN. Down: HNF1A, MTNR1B, FFAR4, GPR119, HCN4, MC4R, TTR, RASGRP1, A1CF, FOXE1.

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX pank: <https://purl.org/okn/frink/kg/pankgraph/schema/>
SELECT ?sym (AVG(?t2d) AS ?t2dm) (AVG(?nd) AS ?ndm) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?stmt rdf:subject ?ocr ; rdf:predicate biolink:associated_with ; rdf:object <http://purl.obolibrary.org/obo/CL_0000169> ;
          pank:type_2_diabetes__OCR_GeneActivityScore_mean ?t2d ; pank:non_diabetic__OCR_GeneActivityScore_mean ?nd .
    ?ocr biolink:located_in ?gene . ?gene rdfs:label ?sym .
  }
} GROUP BY ?sym HAVING(AVG(?nd) > 15) ORDER BY (AVG(?t2d)/AVG(?nd)) LIMIT 35
```

#### Query 24

_2026-07-05T23:31:09+00:00 · `pankgraph`_ — islet cis-eQTL variant layer (variant affects_expression_of gene; ~19,400 dbSNP SNPs). Top eQTL-targeted genes: HLA-F, MTRF1L, HLA-A, FN3KRP, ACHE, NDUFV3, NDUFAF1.

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?sym (COUNT(DISTINCT ?snp) AS ?neqtl) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?snp a <http://purl.obolibrary.org/obo/SO_0000694> ; biolink:affects_expression_of ?gene . ?gene rdfs:label ?sym .
  }
} GROUP BY ?sym ORDER BY DESC(?neqtl) LIMIT 25
```

#### Query 20 / 21

_`gene-expression-atlas-okn`_ — measured T2D differential expression by tissue (UBERON). Islet of Langerhans (UBERON_0000006): 66 up (inflammatory — IL8/CXCL8, IL1B, CCL20, ICAM1), 6 down; retina (UBERON_0000966): 13 up; liver (UBERON_0002107): 5 up.

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
SELECT ?tissue ?dir (COUNT(*) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?assay biolink:has_attribute <MONDO_0005148> ; biolink:has_attribute ?tissue .
    FILTER(STRSTARTS(STR(?tissue),"http://purl.obolibrary.org/obo/UBERON"))
    ?an biolink:subject ?assay ; wobd:direction ?dir .
  }
} GROUP BY ?tissue ?dir
```

#### Query 22

_2026-07-05T23:30:06+00:00 · `digcfdekg`_ — T2D gene sets / pathways / mouse-phenotype factors (PIGEAN weights)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?label (MAX(?w) AS ?maxw) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?stmt rdf:subject ?f ; rdf:object <MONDO_0005148> ; dig:weight ?w . ?f rdfs:label ?label .
    FILTER(REGEX(STR(?label),"^(KEGG_|REACTOME_|WP_|BIOCARTA_|GOBP_|GOCC_|GOMF_|HP_|mp_|PID_)"))
  }
} GROUP BY ?label ORDER BY DESC(?maxw) LIMIT 40
```

_40 rows_ — KEGG_MATURITY_ONSET_DIABETES_OF_THE_YOUNG (2.77), WP_TRANSCRIPTION_FACTOR_REGULATION_IN_ADIPOGENESIS (2.77), REACTOME_REGULATION_OF_GENE_EXPRESSION_IN_BETA_CELLS (2.71), WP_ROLES_OF_CERAMIDES_IN_DEVELOPMENT_OF_INSULIN_RESISTANCE (2.06), KEGG_TYPE_II_DIABETES_MELLITUS (1.93), REACTOME_SIGNALING_BY_LEPTIN (1.84), GOBP_CARBOHYDRATE_HOMEOSTASIS, GOBP_POSITIVE_REGULATION_OF_INSULIN_SECRETION.

#### Query 23

_2026-07-05T23:31:06+00:00 · `biomarkerkg`_ — curated T2D biomarker records (OBCI_1000002 → DOID_9352, 27 records + specimen UBERON: blood, plasma, serum, urine, CSF, urinary bladder)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obci: <http://purl.obolibrary.org/obo/>
SELECT ?bm ?label ?assessed ?specimen WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?bm obci:OBCI_1000002 <http://purl.obolibrary.org/obo/DOID_9352> .
    OPTIONAL { ?bm rdfs:label ?label } OPTIONAL { ?bm obci:OBCI_1000009 ?assessed } OPTIONAL { ?bm obci:OBCI_1000018 ?specimen }
  }
}
```

#### Query 12

_2026-07-05T23:20:50+00:00 · `spoke-okn`_ — diabetes prevalence by state (CDC PLACES age-adjusted %, PREVALENCE_DpL). Mississippi 14.17, Louisiana 12.84, South Carolina 12.80, Georgia 12.65 … Massachusetts 7.26.

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?state ?sdesc (AVG(xsd:double(?val)) AS ?mean_prev) (COUNT(*) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?stmt rdf:subject <http://purl.obolibrary.org/obo/DOID_9351> ; rdf:predicate spoke:PREVALENCE_DpL ;
          spoke:state_abbr ?state ; spoke:state_desc ?sdesc ; spoke:data_value ?val ;
          spoke:data_value_type "Age-adjusted prevalence" .
  }
} GROUP BY ?state ?sdesc ORDER BY DESC(?mean_prev)
```

#### Query 13 / 14 / 17

_`spoke-okn`_ — SDoH correlation with county diabetes prevalence (PREVALENCEIN_SpL; County Health Rankings; Pearson components computed server-side, values de-parenthesized to strip the margin-of-error suffix). r: poor/fair health 0.94, physical inactivity 0.87, children in poverty 0.82, insufficient sleep 0.76, food insecurity 0.74, adult obesity 0.74, premature death 0.70; protective: high-school completion −0.77, life expectancy −0.65, food-environment index −0.64, broadband −0.61.

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?var (COUNT(*) AS ?n) (SUM(?d) AS ?sx) (SUM(?s) AS ?sy) (SUM(?prod) AS ?sxy) (SUM(?dd) AS ?sxx) (SUM(?ss) AS ?syy) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?st1 rdf:predicate spoke:PREVALENCEIN_SpL ; rdf:object ?loc ; spoke:variable "diabetes prevalence" ; spoke:value ?dstr0 .
    ?st2 rdf:predicate spoke:PREVALENCEIN_SpL ; rdf:object ?loc ; spoke:variable ?var ; spoke:value ?sstr0 .
    VALUES ?var { "adult obesity" "physical inactivity" "adult smoking" "children in poverty" "unemployment" "uninsured"
      "food insecurity" "limited access to healthy foods" "food environment index" "income inequality" "high school completion"
      "some college" "rural" "severe housing cost burden" "broadband access" "premature death" "life expectancy"
      "children in single-parent households" "poor or fair health" "insufficient sleep" "excessive drinking" }
    BIND(xsd:double(REPLACE(STR(?dstr0),"\\(.*$","")) AS ?d)
    BIND(xsd:double(REPLACE(STR(?sstr0),"\\(.*$","")) AS ?s)
    BIND(?d*?s AS ?prod) BIND(?d*?d AS ?dd) BIND(?s*?s AS ?ss)
  }
} GROUP BY ?var
```

## Schema / exploration notes (probes, not counted as findings)

- **spoke-okn** has **no T2D-specific disease node**; diabetes is stored at the PARENT term `DOID_9351` "diabetes mellitus" (28,248 edges). Gene/prevalence (CDC PLACES)/SDoH (County Health Rankings) layers therefore describe all diagnosed diabetes (≈90–95% T2D). Prevalence statements carry `geo:asWKT` POINT coordinates + `state_abbr` + `data_value`; SDoH values embed a margin of error as "value(SE)" needing de-parenthesizing before numeric casting.
- **pankgraph** curated `gene_associated_with_condition` is **type-1** diabetes only (176 genes → MONDO:0005147). Its T2D signal is the type-2-specific *measured* layer: OCR gene-activity per islet cell type (α, β, δ, acinar, ductal, endothelial, macrophage) and ~19,400 dbSNP islet cis-eQTLs. Gene symbols resolve via `rdfs:label` on the Ensembl node (not `gene_name`).
- **digcfdekg** `EFO_0004541` is **HbA1c measurement**, not T2D — mixing it injected erythrocyte genetics (SPTA1, ANK1, HBB…); the T2D layer uses `MONDO_0005148` only.
- **oard-kg** returned 0 rows for T2D (rare-disease EHR corpus, as for Alzheimer's).
- **gene-expression-atlas-okn** anchors T2D contrasts via `biolink:has_attribute MONDO_0005148`; differential expression on `GeneExpressionMixin` nodes carries `wobd:log2fc`, `wobd:adj_p_value`, `wobd:direction`, tissue via UBERON.

# Alzheimer's Disease Biology — Proto-OKN Federated Knowledge Map

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
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg> (v0.0.3)
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph> (v0.0.2)

## Conversation

👤 **User** — I'm studying Alzheimer's disease and want a comprehensive, evidence-backed map of its biology, covering its major forms and subtypes, organized by entity type (genes coding/non-coding kept distinct, genetic variants, pathways/gene sets, drugs, altered-activity genes with tissue/cell type, clinical features/biomarkers). For each finding note source(s), relationship type, confidence/effect score, and evidence kind (curated link, statistical/genetic association, measured activity change, pathway membership) — kept separate. Look broadly across sources; account for differing names/IDs; include subtypes. Rank by cross-source agreement; highlight the highest-confidence set; flag uncertainties/undercounts. Deliver a report, a CSV (one row per finding), visualizations, and a reproducible transcript.

🧠 **Assistant** — **Approach.** Profiled the Proto-OKN federation (`list_kgs`, `find_context_sources`, `list_crosswalks`) to find which of ~40 KGs hold each entity type, then anchored on Alzheimer disease = MONDO:0004975 and expanded its ontology subtree via `ubergraph` to **22 AD terms** (main AD; AD1–AD19; early-onset autosomal-dominant AD; familial AD). Because sources use different disease IDs, cross-walked every AD MONDO term to DOID/OMIM/Orphanet/EFO/UMLS/MeSH (235 cross-references) so each KG could be queried natively — critical, since the plain MONDO IRI returns **0 rows** in rdkg and digcfdekg (which key AD on subtypes / EFO). Eight KGs contributed: spoke-okn, rdkg, digcfdekg, prokn, gene-expression-atlas-okn, biomarkerkg (+ oard-kg checked-empty for main AD, ubergraph as bridge).

**Result — 491 findings.** Genes = 316 (289 protein-coding, 27 non-coding). Highest-confidence core (all 4 gene sources, Tier 1): **PSEN1, APP, SORL1, PSEN2**. Tier 2 (≥3 sources): APOE, CLU, ABCA7, PICALM, CR1, CD2AP, BACE1, ADAM10, TREM2, TNF, PLCG2, PRNP, NCSTN, MS4A4A, ACE, ACHE, CASP3, HFE, MPO, UNC5C. Strongest statistical signal (digcfdekg PIGEAN/EAGGL, GWAS-derived): APOE 10.2, CLU 9.38, PSEN1 9.32, ABCA7 9.13, BIN1 9.04. Non-coding = BACE1-regulating miRNAs (MIR29 family, MIR107) + others. Drugs (kept separate by relationship): 268 indicated/investigated compounds (prokn/ChEMBL — anti-amyloid antibodies, secretase inhibitors, cholinergics); 2 spoke-okn TREATS edges (Carbonic acid, Copper — a limitation); 56 contraindicated drugs (rdkg — antipsychotics/anticholinergics/opioids). Altered activity (GXA, measured): up-regulation of mitochondrial OXPHOS/translation, synaptic-vesicle, and proteasome programs in hippocampal formation, temporal cortex/gyrus/lobe, posterior cingulate cortex (adj-p to 7.6×10⁻¹⁴). Clinical/biomarkers: 70 HP hallmarks (neurofibrillary tangles, senile plaques, cerebral amyloid angiopathy, hippocampal atrophy, FDG-PET hypometabolism…) from rdkg; a neuroinflammation biomarker panel (GFAP, TREM2, YKL-40/CHI3L1, S100B, ICAM1, VCAM1, CCL2, TSPO) + VSNL1 in CSF/blood from biomarkerkg. Evidence types kept separate: curated 393, statistical 121, measured 19.

**Key caveats / undercounts.** (1) Genetic variants severely undercounted — no AD-anchored variant-entity layer exists in the federation; variant signal survives only at gene level via digcfdekg's GWAS-derived statistics. (2) Non-coding genes undercounted (symbol heuristic biotype). (3) GXA is enrichment-level, not per-gene fold-changes. (4) prokn gene layer is familial-only here (9 genes), under-corroborating common-form genes like APOE (3/4 not 4/4). (5) spoke-okn TREATS near-empty. Delivered: `AD_knowledge_map_report.md` + `.html` (interactive 491-row table), `AD_knowledge_map_findings.csv`, `AD_gene_source_matrix.csv`, four figures, and this transcript.

👤 **User** — In addition to the .md file, also create an html document.

🧠 **Assistant** — Created `AD_knowledge_map_report.html`: a self-contained report with the four figures embedded and a live, searchable/sortable/filterable table of all 491 findings (filter by entity type, evidence type, and confidence tier; click headers to sort).

---

## SPARQL queries executed (verbatim, in order)

**Query 1 — `ubergraph` — AD subtype expansion (22 rows).** `expand_ontology_term(MONDO:0004975)` →
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?term ?label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?term rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0004975> .
    OPTIONAL { ?term rdfs:label ?label . } } } LIMIT 1000
```
Returns: MONDO_0004975 Alzheimer disease; MONDO_0007088 AD type 1; MONDO_0007089 AD 2; … (22 terms).

**Query 2 — `ubergraph` — cross-ontology ID crosswalk for all 22 AD terms (235 rows).**
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?mondo ?mlabel ?xref WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    VALUES ?mondo { <...22 AD MONDO IRIs...> }
    OPTIONAL { ?mondo rdfs:label ?mlabel }
    { ?mondo skos:exactMatch ?xref } UNION { ?mondo oboInOwl:hasDbXref ?xref } } } ORDER BY ?mondo
```
Returns e.g. MONDO_0004975 → DOID:10652, UMLS:C0002395, MeSH:D000544, NCIT:C2866, Orphanet:238616, ICD10:G30; subtypes → OMIM 104300 (AD1), 104310 (AD2), 607822 (AD3), 606889 (AD4)… and DOID_0110035–0110051.

**Query 3 — `spoke-okn` — AD-associated genes via ASSOCIATES_DaG (180 rows, curated).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?sym WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    VALUES ?d { <DOID_10652> <DOID_0080348> <DOID_0110035..0110051> }
    ?d spoke:ASSOCIATES_DaG ?gene . ?gene rdfs:label ?sym . } } ORDER BY ?sym
```
Returns A2M, ABCA1, ABCA7, …, APOE, APP, …, PSEN1, PSEN2, SORL1, TREM2, … (180 genes).

**Query 4/7 — `rdkg` — AD-subtype genes (related_to), clinical features (has_phenotype), contraindicated drugs (contraindicated_for).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?p ?o (SAMPLE(?otype) AS ?type) (SAMPLE(?olabel) AS ?label) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    VALUES ?d { <...AD MONDO subtypes + rdaccelerate grouped nodes...> }
    VALUES ?p { biolink:related_to biolink:has_phenotype biolink:contraindicated_for }
    ?d ?p ?o . OPTIONAL { ?o rdf:type ?otype } OPTIONAL { ?o rdfs:label ?olabel } } } GROUP BY ?p ?o
```
Returns ~105 genes (incl. non-coding MIR100/146A/296/375/505/708/766, SNAR-I), 70 HP phenotypes (Dementia, Neurofibrillary tangles, Senile plaques, Hippocampal atrophy, Cerebral amyloid angiopathy…), 56 contraindicated drugs (DrugBank; antipsychotics, anticholinergics, opioids).

**Query 5/6 — `digcfdekg` — statistical gene–trait associations for AD traits (PIGEAN/EAGGL weights).**
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT ?sym (MAX(?w) AS ?maxw) (COUNT(DISTINCT ?trait) AS ?nt) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    VALUES ?trait { <EFO_1001870 LOAD> <Orphanet_1020 EOAD> <trait/81ade4…> <trait/e02132…> <trait/6839c5…> }
    ?stmt rdf:subject ?gene ; rdf:object ?trait ; dig:weight ?w .
    ?gene a dig:Gene ; rdfs:label ?sym . } } GROUP BY ?sym ORDER BY DESC(?maxw) LIMIT 120
```
Returns APOE 10.2, CLU 9.38, PSEN1 9.32, ABCA7 9.13, BIN1 9.04, PICALM 8.72, APP 8.65, SORL1 8.59, … incl. miRNAs MIR29A/B1/C, MIR107, MIR15B, MIR186 (~3.7).

**Query 8 — `prokn` — compounds indicated/investigated for AD (NCIT_C41184 = "Indication"), 268 ChEMBL compounds.**
```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?sub (SAMPLE(?subtype) AS ?type) (SAMPLE(?label) AS ?lbl) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?d a up:Disease ; skos:exactMatch <http://purl.obolibrary.org/obo/MONDO_0004975> .
    ?stmt rdf:object ?d ; rdf:predicate <http://purl.obolibrary.org/obo/NCIT_C41184> ; rdf:subject ?sub .
    OPTIONAL { ?sub a ?subtype } OPTIONAL { ?sub rdfs:label ?label } } } GROUP BY ?sub
```
Returns 268 compounds: Bexarotene, Avagacestat, Aducanumab, Bapineuzumab, Bepranemab, Atabecestat, Begacestat, Benzgalantamine, Celecoxib, Azeliragon, Buntanetap, Blarcamesine, … (mostly ChEMBL-ID-only).

**Query 9 — `biomarkerkg` — AD biomarkers, assessed molecule + specimen (OBCI predicates, DOID_10652).**
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obci: <http://purl.obolibrary.org/obo/>
SELECT ?bm ?label ?assessed ?specimen WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?bm ?pd <http://purl.obolibrary.org/obo/DOID_10652> .
    FILTER(?pd IN (obci:OBCI_1000002, obci:OBCI_1000006, obci:OBCI_1000008))
    OPTIONAL { ?bm rdfs:label ?label } OPTIONAL { ?bm obci:OBCI_1000009 ?assessed }
    OPTIONAL { ?bm obci:OBCI_1000018 ?specimen } } }
```
Returns neuroinflammation panel (CHI3L1/GID1116, GFAP/GID2670, ICAM1/GID3383, TREM2/GID54209, S100B/GID6285, CCL2/GID6347, TSPO/GID706, VCAM1/GID7412) + VSNL1 (UniProt P62760, CSF); specimens UBERON CSF/plasma/serum/blood/urine.

**Query 10 — `prokn` — familial-AD subtype gene/protein associations (biolink:associated_with).**
```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?dm ?rel ?s (SAMPLE(?stype) AS ?type) (SAMPLE(?slabel) AS ?lbl) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?d a up:Disease ; skos:exactMatch ?dm .
    VALUES ?dm { <OMIM 104300/607822/606889/104310> <MONDO_0007088/0011913/0011743/0007089> }
    { ?s <https://biolink.github.io/biolink-model/associated_with> ?d . BIND("associated_with" AS ?rel) }
    UNION { ?stmt rdf:object ?d ; rdf:subject ?s ; rdf:predicate ?relx . BIND(STR(?relx) AS ?rel) }
    OPTIONAL { ?s a ?stype } OPTIONAL { ?s rdfs:label ?slabel } } } GROUP BY ?dm ?rel ?s
```
Returns APP (P05067), SORL1 (Q92673), UNC5C (O95185), DBN1 (Q16643), TM2D3 (Q9BRN9), MPO, HFE (AD1); PSEN1 (ENSG…080815), PSEN2 (ENSG…143801, P49810) (AD4).

**Query 11 — `spoke-okn` — compounds that TREAT AD (TREATS_CtD).**
```sparql
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?name WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?c spoke:TREATS_CtD <http://purl.obolibrary.org/obo/DOID_10652> .
    OPTIONAL { ?c rdfs:label ?name } } }
```
Returns exactly 2: Carbonic Acid, Copper (SPOKE TREATS layer for AD is near-empty — flagged).

**GXA (measured activity, enrichment).** AD differential-expression contrasts (`biolink:has_attribute MONDO_0004975`) joined to Reactome/GO enrichment (`wobd:enrichment_source`, `effect_size`, `adj_p_value`, `direction`) with anatomy (`UBERON`). Top: R-HSA-163200 Respiratory electron transport ↑ adj-p 7.6e-14 (hippocampal formation); GO:0032981 Complex I assembly; GO:0008021 synaptic vesicle; GO:0000502 proteasome — across hippocampus, temporal cortex/gyrus/lobe, posterior cingulate cortex.

---

## Schema/exploration notes (probes, not counted as findings)

- **prokn** disease nodes are `up:Disease` cross-referenced to MONDO/OMIM/Orphanet/DOID via `skos:exactMatch` (not `rdfs:seeAlso`); the main AD node links **only** to 268 compounds (`NCIT_C41184` "Indication") — genes/proteins attach to familial subtype nodes; `up:Protein` nodes carry no UniProt natural-variant annotations for APP/PSEN1/PSEN2, so no variant layer.
- **rdkg** keys AD on MONDO subtype IRIs + `rdaccelerate.org` grouped nodes (rare-disease emphasis; lacks the common-form main term as a connected node).
- **digcfdekg** traits use EFO/Orphanet/MONDO + hashed trait nodes; associations are reified `Statement`s carrying `dig:weight`, `scoreType`, `wasGeneratedBy` (PIGEAN/EAGGL).
- **oard-kg** returned 0 for the main AD term (rare-disease-only corpus).

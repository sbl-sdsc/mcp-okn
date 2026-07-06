# Bisphenol Chemical Exposome — Proto-OKN Evidence Map (Reproducible Transcript)

- **Date:** 2026-07-05
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** FRINK federation (`https://purl.org/okn/frink/kg/…` named graphs)

## Knowledge graphs used (with release versions)

| KG | Version | KG | Version |
|---|---|---|---|
| biobricks-aopwiki | v0.0.4 | spoke-okn | v0.0.6 |
| biobricks-toxcast | v0.0.2 | rdkg | v0.0.1 |
| biobricks-tox21 | v0.0.3 | prokn | v0.0.5 |
| biobricks-ice | v0.0.3 | oard-kg | v0.0.3 |
| biobricks-pubchem-annotations | v0.0.2 | ubergraph | v0.0.2 |
| gene-expression-atlas-okn | v0.0.3 | sudokn | v0.0.10 |
| sawgraph | v0.0.15 | fiokg | v0.0.11 |

## Summary of analysis

Thirteen bisphenols were resolved and cross-walked (CAS anchor + PubChem CID, DTXSID, ChEBI): all 13 present in ICE, 11 in ToxCast & Tox21, and only **BPA** (CAS 80-05-7) and **TBBPA** (79-94-7) present as AOP-Wiki chemical stressors.

**AOP backbone.** BPA drives three curated AOPs, *all* initiating at an estrogen receptor: AOP 314 (ERα binding in immune cells → exacerbation of systemic lupus erythematosus), AOP 522 (ER antagonism → autism-like behavior), AOP 535 (GPER activation → learning & memory impairment). TBBPA drives AOP 152 (transthyretin binding → decreased cognitive function; thyroid axis).

**Molecular targets.** 16 targets (ESR1, ESR2, ESRRA/G, AR, GPER1, PGR, THRA/B, NR1I2/3, NR3C1, PPARG, AHR, GATA3, TTR) with verified Ensembl/Entrez/UniProt IDs. AOP-Wiki's automated key-event→gene links proved unreliable (the ERα-binding MIE maps to MDK/MVK/PPIB, ER antagonism to EREG/GCNT2 — none is ESR1; downstream KEs each pull in thousands of genes), so targets were taken from the curated MIE biology, not those links. TTR was the one correctly captured.

**Assay.** ToxCast hitcalls are binary; BPAF most active (484/1189 endpoints), then TBBPA (377/1138), BPB (309/991), TCBPA (297/808), BPA (375/1414); BPS (72/558) and BPF (51/665) least active. Tox21 is a chemical registry only.

**Expression.** All 16 targets significantly differentially expressed across GXA disease contrasts (PPARG 399, GATA3 374, AHR 290, GPER1 284; TTR max |log2FC| 17.1).

**Disease.** SPOKE-OKN: 92 gene→disease associations across 45 DOID diseases. RDKG: rare-disease genetics (ESR1 124, PPARG 104, ESR2 73 MONDO). ProKN: protein GO/Reactome (ESR1: 15 Reactome, 31 GO). Ubergraph bridged all 45 DOID→MONDO. OARD: EHR phenotypes for precocious puberty (1,639) and prostate cancer (1,218). PubChem hazards for BPA: 'Reproductive toxicity category 2', 'Suspected of damaging fertility (H361f)', 'Potential endocrine disrupting compound', 'Mutagen'.

**Corroboration.** 234 chemical→disease links scored by independent agreeing sources (max 7). 26 reach 7/7 — all BPA — led by **breast cancer**, uniquely supported by three converging targets (ERα, ERβ, GATA3). TBBPA thyroid-axis links score 6/7; the 11 analogues share ERα/ERβ→disease evidence at 5/7, further ranked by assay potency.

**Industry.** SUDOKN lists many US manufacturers of BPA-derived polycarbonate and epoxy-resin products (material-based link, no CAS). SAWGraph (PFAS) and FIOKG (facilities/NAICS) carry no bisphenol identifiers.

**Key caveats:** AOP coverage is sparse (only BPA/TBBPA); assay activity is in-vitro, not in-vivo effect; joins are ontology-bridged; AOP-Wiki gene links are unreliable.

---

## SPARQL queries executed (verbatim, finding-producing only)

### Query 1 — Bisphenols in AOP-Wiki with identifiers (`biobricks-aopwiki`)
```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sio: <http://semanticscience.org/resource/>
SELECT DISTINCT ?cas ?title ?casnum ?cid ?dtxsid WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?cas a sio:CHEMINF_000000 ; dc:title ?title .
    FILTER( CONTAINS(LCASE(?title),'bisphenol') )
    OPTIONAL { ?cas sio:CHEMINF_000446 ?casnum }
    OPTIONAL { ?cas skos:exactMatch ?cid . FILTER(CONTAINS(STR(?cid),'pubchem.compound')) }
    OPTIONAL { ?cas sio:CHEMINF_000568 ?dtxsid }
  }
} ORDER BY ?title
```
→ 2 rows: TBBPA (CAS 79-94-7, CID 6618, DTXSID1026081); Bisphenol A (CAS 80-05-7, CID 6623, DTXSID7020182).

### Query 2 — BPA AOP backbone: MIE → KE → AO (`biobricks-aopwiki`)
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
SELECT DISTINCT ?aop ?aopTitle ?relLabel ?ke ?keTitle WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    <https://identifiers.org/cas/80-05-7> dcterms:isPartOf ?stressor .
    ?aop <http://purl.obolibrary.org/obo/NCIT_C54571> ?stressor .
    OPTIONAL { ?aop dc:title ?aopTitle }
    ?aop ?rel ?ke .
    VALUES ?rel { aop:has_molecular_initiating_event aop:has_key_event aop:has_adverse_outcome }
    BIND(REPLACE(STR(?rel),'.*#','') AS ?relLabel)
    OPTIONAL { ?ke dc:title ?keTitle }
  }
} ORDER BY ?aop ?relLabel ?keTitle
```
→ 26 rows across AOP 314 (ERα → SLE), AOP 522 (ER antagonism → autism-like behavior), AOP 535 (GPER activation → learning/memory impairment).

### Query 3 — TBBPA AOP backbone (`biobricks-aopwiki`)
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
SELECT DISTINCT ?aop ?aopTitle ?relLabel ?ke ?keTitle WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    <https://identifiers.org/cas/79-94-7> dcterms:isPartOf ?stressor .
    ?aop <http://purl.obolibrary.org/obo/NCIT_C54571> ?stressor .
    OPTIONAL { ?aop dc:title ?aopTitle }
    ?aop ?rel ?ke .
    VALUES ?rel { aop:has_molecular_initiating_event aop:has_key_event aop:has_adverse_outcome }
    BIND(REPLACE(STR(?rel),'.*#','') AS ?relLabel)
    OPTIONAL { ?ke dc:title ?keTitle }
  }
} ORDER BY ?aop ?relLabel ?keTitle
```
→ 13 rows: AOP 152 (Binding, Transthyretin in serum → Cognitive function decreased; 11 KEs, thyroid axis).

### Query 4 — Verified molecular-target identifiers from AOP-Wiki HGNC nodes (`biobricks-aopwiki`)
```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?symbol ?ensembl ?entrez WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    VALUES ?symbol { "ESR1" "ESR2" "GPER1" "AR" "TTR" "THRA" "THRB"
                     "ESRRA" "ESRRG" "NR1I2" "NR1I3" "PPARG" "NR3C1" "AHR" "GATA3" "PGR" }
    BIND(IRI(CONCAT('https://identifiers.org/hgnc/',?symbol)) AS ?gene)
    OPTIONAL { ?gene skos:exactMatch ?ensembl . FILTER(CONTAINS(STR(?ensembl),'ensembl')) }
    OPTIONAL { ?gene skos:exactMatch ?entrez . FILTER(CONTAINS(STR(?entrez),'ncbigene')) }
  }
} ORDER BY ?symbol
```
→ ESR1 ENSG00000091831/2099; ESR2 ENSG00000140009/2100; AR ENSG00000169083/367; TTR ENSG00000118271/7276; etc. (GPER1/ESRRA/ESRRG absent from AOP-Wiki HGNC set — resolved via GXA/ProKN by symbol/Entrez).

### Query 5 — MIE-only gene targets, demonstrating unreliable KE→gene links (`biobricks-aopwiki`)
```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?aop ?keTitle ?symbol ?ensembl ?entrez ?uniprot WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    VALUES ?aop { <https://identifiers.org/aop/314> <https://identifiers.org/aop/522>
                  <https://identifiers.org/aop/535> <https://identifiers.org/aop/152> }
    ?aop aop:has_molecular_initiating_event ?ke .
    OPTIONAL { ?ke dc:title ?keTitle }
    ?ke <http://edamontology.org/data_1025> ?gene .
    BIND(REPLACE(STR(?gene),'.*/hgnc/','') AS ?symbol)
    OPTIONAL { ?gene skos:exactMatch ?ensembl . FILTER(CONTAINS(STR(?ensembl),'ensembl')) }
    OPTIONAL { ?gene skos:exactMatch ?entrez . FILTER(CONTAINS(STR(?entrez),'ncbigene')) }
    OPTIONAL { ?gene skos:exactMatch ?uniprot . FILTER(CONTAINS(STR(?uniprot),'uniprot')) }
  }
} ORDER BY ?aop ?symbol
```
→ 51 rows. The ERα-binding MIE (AOP 314) maps to MDK/MVK/PPIB/PTGDR/TBXT; ER antagonism (AOP 522) to EREG/GCNT2 — **none is ESR1** (documents the data-quality caveat). Only AOP 152 correctly returns TTR (plus ALB/SERPINA7 thyroxine-binding proteins).

### Query 6 — ToxCast assay coverage & activity per bisphenol (`biobricks-toxcast`)
```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?casnum (COUNT(DISTINCT ?mg) AS ?tested)
       (SUM(IF(xsd:decimal(?hit) > 0, 1, 0)) AS ?active)
       (MAX(xsd:decimal(?hit)) AS ?maxhit) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
    ?chem <http://edamontology.org/has_identifier> ?cas ;
          <http://purl.obolibrary.org/obo/RO_0000056> ?mg .
    VALUES ?cas { <http://identifiers.org/cas/80-05-7> <http://identifiers.org/cas/80-09-1>
      <http://identifiers.org/cas/620-92-8> <http://identifiers.org/cas/1478-61-1>
      <http://identifiers.org/cas/77-40-7> <http://identifiers.org/cas/1571-75-1>
      <http://identifiers.org/cas/2081-08-5> <http://identifiers.org/cas/79-97-0>
      <http://identifiers.org/cas/843-55-0> <http://identifiers.org/cas/79-94-7>
      <http://identifiers.org/cas/79-95-8> }
    BIND(REPLACE(STR(?cas),'.*/cas/','') AS ?casnum)
    ?mg <http://purl.obolibrary.org/obo/OBI_0000299> ?hc .
    ?hc <http://semanticscience.org/resource/SIO_000300> ?hit .
  }
} GROUP BY ?casnum ORDER BY DESC(?tested)
```
→ 11 rows: BPA 375/1414 · BPAF 484/1189 · TBBPA 377/1138 · BPB 309/991 · TCBPA 297/808 · BPF 51/665 · BPC 229/662 · BPS 72/558 · BPE 62/398 · BPAP 80/273 · BPZ 119/238.

### Query 7 — Target gene → disease associations (`spoke-okn`)
```sparql
PREFIX s: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?symbol ?disease ?dlabel WHERE {
  VALUES (?symbol ?entrez) {
    ("ESR1" "2099") ("ESR2" "2100") ("ESRRA" "2101") ("ESRRG" "2104")
    ("GPER1" "2852") ("AR" "367") ("TTR" "7276") ("THRA" "7067") ("THRB" "7068")
    ("NR1I2" "8856") ("NR1I3" "9970") ("NR3C1" "2908") ("PGR" "5241")
    ("PPARG" "5468") ("AHR" "196") ("GATA3" "2625") }
  BIND(IRI(CONCAT("http://www.ncbi.nlm.nih.gov/gene/",?entrez)) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?disease s:ASSOCIATES_DaG ?gene .
    OPTIONAL { ?disease rdfs:label ?dlabel }
  }
} ORDER BY ?symbol ?dlabel
```
→ 92 rows / 45 DOID diseases. ESR1 → breast/ovarian/uterine/prostate/colorectal/liver/lung cancer, endometriosis, PCOS, obesity, diabetes, depression, migraine. PPARG → obesity, diabetes, coronary artery disease, cardiomyopathy. AR → prostate/testicular cancer, male infertility.

### Query 8 — Differential expression of targets (`gene-expression-atlas-okn`)
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?symbol (COUNT(*) AS ?nSig)
   (SUM(IF(?dir="up",1,0)) AS ?nUp) (SUM(IF(?dir="down",1,0)) AS ?nDown)
   (MAX(ABS(xsd:decimal(?lfc))) AS ?maxAbsLog2fc) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?gene a biolink:Gene ; biolink:symbol ?symbol .
    VALUES ?symbol { "ESR1" "ESR2" "ESRRA" "ESRRG" "GPER1" "AR" "TTR" "THRA" "THRB"
                     "NR1I2" "NR1I3" "NR3C1" "PGR" "PPARG" "AHR" "GATA3" }
    ?gem biolink:object ?gene ; wobd:direction ?dir ; wobd:log2fc ?lfc ; wobd:adj_p_value ?p .
    FILTER(xsd:decimal(?p) < 0.05)
  }
} GROUP BY ?symbol ORDER BY DESC(?nSig)
```
→ 16 rows: PPARG 399, GATA3 374, AHR 290, GPER1 284, PGR 280, THRB 268, NR3C1 258, AR 244, ESR1 195, ESRRG 193, THRA 187, TTR 109 (maxLog2FC 17.1), ESR2 107, NR1I2 103, ESRRA 89, NR1I3 88.

### Query 9 — ICE functional-use categories per bisphenol (`biobricks-ice`)
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?casnum ?useType ?category WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?chem <http://edamontology.org/has_identifier> ?cas ;
          <http://purl.obolibrary.org/obo/RO_0000056> ?mg .
    VALUES ?cas { <http://identifiers.org/cas/80-05-7> … (13 bisphenol CAS IRIs) }
    BIND(REPLACE(STR(?cas),'.*/cas/','') AS ?casnum)
    FILTER(CONTAINS(STR(?mg),'Functional_Use_Categories'))
    ?mg <http://purl.obolibrary.org/obo/OBI_0000299> ?ep .
    ?ep rdfs:label ?useType ; <http://semanticscience.org/resource/SIO_000300> ?category .
  }
} ORDER BY ?casnum
```
→ 19 rows: BPA = Binder/Catalyst/Hardener (OECD) + Antioxidant/UV-absorber (predicted); TBBPA/TCBPA = Flame retardant; analogues = Antioxidant/UV-absorber/Colorant.

### Query 10 — Rare-disease genetics per target (`rdkg`)
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?symbol (COUNT(DISTINCT ?mondo) AS ?nRareDisease) WHERE {
  VALUES (?symbol ?entrez) { ("ESR1" "2099") … (16 targets) }
  BIND(IRI(CONCAT("http://identifiers.org/ncbigene/",?entrez)) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?gene biolink:related_to ?mondo . FILTER(CONTAINS(STR(?mondo),"MONDO"))
  }
} GROUP BY ?symbol ORDER BY DESC(?nRareDisease)
```
→ ESR1 124, PPARG 104, ESR2 73, AR 59, PGR 52, AHR 48, GATA3 35, NR3C1 29, TTR 21, NR1I2 20, THRA 11, GPER1 10, ESRRA 9, THRB 9, NR1I3 8.

### Query 11 — Protein GO/Reactome annotations + UniProt (`prokn`)
```sparql
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT ?symbol (SAMPLE(?prot) AS ?uniprot)
   (COUNT(DISTINCT ?reactome) AS ?nReactome) (COUNT(DISTINCT ?go) AS ?nGO) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?prot <http://purl.obolibrary.org/obo/NCIT_C164806> ?symbol .
    VALUES ?symbol { "ESR1" … (16 targets) }
    FILTER(STRSTARTS(STR(?prot),"http://purl.uniprot.org/uniprot/"))
    OPTIONAL { ?prot ro:RO_0000056 ?reactome . FILTER(CONTAINS(STR(?reactome),"reactome")) }
    OPTIONAL { ?prot ro:RO_0002327 ?go . FILTER(CONTAINS(STR(?go),"GO_")) }
  }
} GROUP BY ?symbol ORDER BY DESC(?nReactome)
```
→ ESR1 P03372 (15 Reactome, 31 GO); PPARG P37231 (8/29); NR3C1 P04150 (8/25); AR P10275 (6/29); TTR P02766 (6/6); + UniProt IDs for all 16 targets.

### Query 12 — Bisphenol compounds in SPOKE (`spoke-okn`)
```sparql
PREFIX s: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?cmp ?label (COUNT(DISTINCT ?g) AS ?nRegGenes) (COUNT(DISTINCT ?d) AS ?nDisease) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp a biolink:ChemicalEntity ; rdfs:label ?label .
    FILTER(CONTAINS(LCASE(?label),"bisphenol"))
    OPTIONAL { { ?cmp s:UPREGULATES_CuG ?g } UNION { ?cmp s:DOWNREGULATES_CdG ?g } }
    OPTIONAL { { ?cmp s:TREATS_CtD ?d } UNION { ?cmp s:CONTRAINDICATES_CcD ?d } }
  }
} GROUP BY ?cmp ?label
```
→ BPA & TBBPA present as PubChem-InChIKey chemical nodes but with **0** regulatory/disease edges (bisphenols carry no compound→gene/disease links in SPOKE; the chain runs through target genes instead).

### Query 13 — DOID ↔ MONDO disease bridge (`ubergraph`)
```sparql
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?doidCurie ?mondo ?mlabel WHERE {
  VALUES ?doidCurie { "DOID:9351" "DOID:1612" "DOID:10283" … (45 SPOKE DOIDs) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo oboInOwl:hasDbXref ?doidCurie .
    FILTER(STRSTARTS(STR(?mondo),"http://purl.obolibrary.org/obo/MONDO"))
    OPTIONAL { ?mondo rdfs:label ?mlabel }
  }
} ORDER BY ?doidCurie
```
→ 45/45 DOID diseases bridged to MONDO (breast cancer DOID:1612→MONDO:0007254; obesity DOID:9970→MONDO:0011122; etc.).

### Query 14 — EHR disease → phenotype (`oard-kg`)
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?dLabel (COUNT(DISTINCT ?pheno) AS ?nPhenotypes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
    ?assoc a biolink:DiseaseToPhenotypicFeatureAssociation ;
           biolink:subject ?d ; biolink:object ?pheno .
    VALUES ?d { <…/MONDO_0000088> <…/MONDO_0008315> <…/MONDO_0007254>
                <…/MONDO_0011122> <…/MONDO_0005015> <…/MONDO_0005133> <…/MONDO_0008487> }
    OPTIONAL { ?d rdfs:label ?dLabel }
  }
} GROUP BY ?dLabel ORDER BY DESC(?nPhenotypes)
```
→ precocious puberty 1,639 phenotypes; prostate cancer 1,218 (OARD covers the rare-disease subset; common diseases like breast cancer/obesity are not in OARD).

### Query 15 — BPA hazard/safety annotations (`biobricks-pubchem-annotations`)
```sparql
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?val WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID6623> ; oa:hasBody ?b .
    ?b rdf:value ?val .
    FILTER(REGEX(?val,"GHS|hazard|carcinog|endocrine|mutagen|reproductive|H3[0-9][0-9]|irritat","i"))
    FILTER(STRLEN(?val) < 320)
  }
} LIMIT 12
```
→ H361f "Suspected of damaging fertility"; "Reproductive toxicity - category 2"; "Potential endocrine disrupting compound"; "Mutagen"; H317/H318/H335; NTP Carcinogenesis study.

### Query 16 — Industrial use, BPA-derived materials (`sudokn`)
```sparql
SELECT DISTINCT ?s ?label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sudokn> {
    ?s <http://www.w3.org/2000/01/rdf-schema#label> ?label .
    FILTER(CONTAINS(LCASE(?label),"polycarbonate") || CONTAINS(LCASE(?label),"epoxy resin"))
  }
} LIMIT 50
```
→ Many US manufacturers of BPA-derived polycarbonate & epoxy products (abcomolds TUFFAK sheets, 3acindustry IMPEX panels, 3erp polycarbonate filament, 1proline epoxy work surfaces). Material-based link (no CAS).

### Negative controls
- `sawgraph` `coso:casNumber` filtered to 7 bisphenol CAS → **0 rows** (PFAS-only KG).
- `fiokg` carries EPA facilities + NAICS + geospatial only — no chemical identifiers to join bisphenols.

---

## Structural / schema-probing queries (exploratory, not shown)

Additional exploratory queries characterized graph structure prior to the finding queries above: AOP-Wiki chemical-node identifier layout (`CHEMINF_*`, `skos:exactMatch`, stressor `isPartOf`); the KE→gene predicate `edam:data_1025` and its HGNC crosswalk hub; ToxCast `Measure_Group`→`HitcallEndpoint` (`SIO_000300`) hitcall structure; ICE `Functional_Use_Categories` endpoints; PubChem `oa:Annotation` body structure; GXA `GeneExpressionMixin` (`wobd:log2fc`/`direction`/`adj_p_value`); SPOKE gene node (Entrez-IRI + `ensembl` property) and `ASSOCIATES_DaG`; rdkg `related_to`→MONDO; prokn `NCIT_C164806`→UniProt; oard MONDO diseases; and join-strategy lookups for every KG pair.

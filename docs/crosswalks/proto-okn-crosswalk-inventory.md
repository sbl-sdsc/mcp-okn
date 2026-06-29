# Proto-OKN Crosswalk Inventory

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- _None queried._

## Conversation

👤 **User**

list crosswalks with examples

---

🧠 **Assistant**

Here are all 134 precomputed cross-KG crosswalks (verified through 2026-06-29), grouped by domain. Each shows the knowledge graphs joined, the shared identifier, the verified overlap count, and an example question the join answers.

## Anatomy & Cell Type

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biomarkerkg ↔ gene-expression-atlas-okn | CL | 8 | Which immune/blood cell types are used as biomarkers in BiomarkerKB and also assayed at single-cell resolution in GXA? |
| biomarkerkg ↔ prokn | CL | 3 | For an immune cell type used as a biomarker in BiomarkerKB, what tissue-specific marker genes does ProKN record (HuBMAP)? |
| gene-expression-atlas-okn ↔ prokn | CL | 31 | For a cell type GXA has single-cell expression for (CL), what marker genes / proteins does ProKN record for that same cell type? |
| spoke-genelab ↔ gene-expression-atlas-okn | CL | 4 | For a cell type examined in a NASA GeneLab spaceflight assay (spoke-genelab, CL), what terrestrial single-cell expression data does GXA hold for the same cell type? |
| spoke-genelab ↔ prokn | CL | 1 | For a cell type examined in a NASA GeneLab spaceflight assay (spoke-genelab, CL), what marker genes/proteins does ProKN record for that same cell type? |
| spoke-genelab ↔ gene-expression-atlas-okn | UBERON | 27 | For an anatomical entity assayed in NASA GeneLab spaceflight studies (spoke-genelab Anatomy, UBERON), what terrestrial differential-expression data does GXA hold for the same tissue? |
| biohealth → ubergraph → gene-expression-atlas-okn | UMLS↔UBERON | 249 | For a tissue/organ GXA profiles expression in (UBERON), what does biohealth know about that anatomical entity (UMLS CUI) and its disease/SDoH associations, bridged through ubergraph UMLS->UBERON? |
| biohealth → ubergraph → spoke-genelab | UMLS↔UBERON | 35 | For a tissue/organ a NASA GeneLab spaceflight assay examined (spoke-genelab Anatomy, UBERON), what does biohealth know about that anatomical entity (UMLS CUI), bridged through ubergraph UMLS->UBERON? |

## Chemicals

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biobricks-aopwiki ↔ biobricks-toxcast | CAS | 290 | Chemical stressors of Adverse Outcome Pathways (AOP-Wiki) that are also assayed in ToxCast / Tox21 / ICE. |
| biobricks-ice ↔ biobricks-toxcast | CAS | 9,421 | ToxCast-screened chemicals (CAS) with Integrated Chemical Environment safety/curation data. |
| biobricks-tox21 ↔ biobricks-ice | CAS | 8,916 | Tox21-screened chemicals (CAS) tied to Integrated Chemical Environment safety/curation data. |
| biobricks-tox21 ↔ biobricks-toxcast | CAS | 8,909 | Tox21 high-throughput screening hits (CAS) for chemicals also covered by EPA ToxCast assays. |
| spoke-okn → ubergraph → biobricks-ice | CHEBI↔CAS | 712 | Tie an ICE curated-toxicity chemical (CAS) to spoke-okn gene/pathway/disease associations for the same compound via CHEBI. |
| spoke-okn → ubergraph → biobricks-tox21 | CHEBI↔CAS | 480 | Tie a Tox21-screened chemical (CAS) to spoke-okn gene/pathway/disease associations for the same compound via CHEBI. |
| spoke-okn → ubergraph → biobricks-toxcast | CHEBI↔CAS | 496 | Tie a ToxCast chemical (CAS) to spoke-okn gene/pathway/disease associations for the same compound via CHEBI. |
| rdkg ↔ spoke-okn | DrugBank | 43 | For drugs SPOKE tracks as chemicals, what disease contraindications or associations does rdkg record? |
| ruralkg ↔ rdkg | DrugBank | 2 | Do the substance-use treatment drugs in ruralkg appear in rdkg's drug-disease graph? |
| biobricks-pubchem-annotations ↔ spoke-okn | PubChem CID | 762 | What PubChem free-text annotations (toxicity, hazards, uses) exist for the chemicals SPOKE links to diseases and genes? |

## Disease & phenotype

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biomarkerkg ↔ nde | DOID | 54 | Infectious/immune-mediated disease datasets (NDE) for a disease biomarkerkg also tracks, joined directly on DOID. |
| biomarkerkg ↔ prokn | DOID | 388 | Literature biomarkers for a disease (BiomarkerKG) cross-referenced to protein/marker-gene evidence (ProKN). |
| spoke-okn ↔ biomarkerkg | DOID | 79 | Biomarkers for a disease (BiomarkerKB) alongside that disease's spoke-okn gene/compound associations, joined on DOID. |
| spoke-okn ↔ nde | DOID | 20 | Infectious/immune-mediated disease datasets (NDE) for a disease, with that disease's spoke-okn associations, joined on DOID. |
| spoke-okn ↔ prokn | DOID | 96 | spoke-okn disease associations (genes/compounds/prevalence/mortality) for diseases ProKN also describes, joined on DOID. |
| biomarkerkg → ubergraph → oard-kg | DOID↔MONDO | 247 | EHR-derived disease-phenotype associations (OARD, MONDO) for a biomarkerkg disease (DOID), bridged through ubergraph. |
| biomarkerkg → ubergraph → rdkg | DOID↔MONDO | 595 | Rare-disease gene/drug associations (rdkg, MONDO) for a biomarkerkg disease (DOID), bridged through ubergraph DOID->MONDO. |
| gene-expression-atlas-okn → ubergraph → spoke-okn | DOID↔MONDO | 54 | spoke-okn gene/compound/prevalence associations for diseases GXA profiles by differential expression, bridged EFO->MONDO->DOID. |
| spoke-okn → ubergraph → oard-kg | DOID↔MONDO | 40 | EHR-derived disease-phenotype associations (OARD, MONDO) for a spoke-okn disease (DOID), bridged through ubergraph. |
| spoke-okn → ubergraph → rdkg | DOID↔MONDO | 149 | Rare-disease gene/drug associations (rdkg, MONDO) for a spoke-okn disease (DOID), bridged through ubergraph DOID->MONDO. |
| biomarkerkg → ubergraph → digcfdekg | DOID↔MONDO (+ EFO/Orphanet→MONDO) | 123 | Biomarker-disease associations (biomarkerkg, DOID) for diseases CFDE REVEAL has gene-trait factor inferences on, bridged DOID->MONDO through ubergraph. |
| spoke-okn → ubergraph → digcfdekg | DOID↔MONDO (+ EFO/Orphanet→MONDO) | 50 | spoke-okn disease associations (genes/compounds/prevalence) for diseases CFDE REVEAL has factor inferences on, bridged DOID->MONDO through ubergraph. |
| digcfdekg ↔ gene-expression-atlas-okn | EFO / Orphanet / MONDO (direct, multi-vocabulary) | 33 | Differential-expression studies (GXA) for diseases CFDE REVEAL has gene-trait factor inferences on, matched on EFO/Orphanet/MONDO. |
| gene-expression-atlas-okn → ubergraph → nde | EFO↔MONDO | 325 | NIAID infectious/immune-disease datasets (nde) for diseases GXA profiles by differential expression, via the EFO->MONDO bridge. |
| gene-expression-atlas-okn → ubergraph → oard-kg | EFO↔MONDO | 159 | EHR-derived disease-phenotype associations (OARD) for diseases GXA profiles by differential expression, via the EFO->MONDO bridge. |
| gene-expression-atlas-okn → ubergraph → rdkg | EFO↔MONDO | 414 | Rare-disease gene/drug associations (rdkg) for diseases GXA has differential-expression studies on, via the EFO->MONDO bridge. |
| gene-expression-atlas-okn ↔ oard-kg | HP | 13 | EHR-derived phenotype co-occurrences (OARD) for the phenotypes GXA studies, joined on HP. |
| gene-expression-atlas-okn ↔ prokn | HP | 12 | ProKN protein/marker-gene evidence for the phenotypes GXA studies, joined on HP. |
| oard-kg ↔ prokn | HP | 4,876 | Phenotypes clinically associated with rare diseases (OARD) that also have protein/marker-gene evidence (ProKN). |
| nde ↔ oard-kg | MONDO | 889 | NIAID datasets for a disease (NDE) plus its EHR phenotype signature (OARD). |
| oard-kg ↔ prokn | MONDO | 445 | Diseases with both EHR phenotype associations (OARD) and marker-gene/protein evidence (ProKN). |
| rdkg ↔ oard-kg | MONDO | 2,014 | Rare-disease EHR phenotype profile (OARD) combined with contraindicated/treating drugs (RDKG, DrugBank). |
| digcfdekg → ubergraph → oard-kg | MONDO (+ EFO/Orphanet→MONDO bridged) | 402 | Rare-disease EHR phenotype profile (OARD) combined with the gene-trait factor inferences CFDE REVEAL records for the same disease. |
| digcfdekg → ubergraph → rdkg | MONDO (+ EFO/Orphanet→MONDO bridged) | 1,045 | For a rare disease (rdkg, MONDO) with its gene/drug associations, what disease-mechanism factors and gene-trait probabilities does CFDE REVEAL infer? |
| oard-kg → ubergraph → prokn | MONDO↔DOID | 111 | Join OARD disease associations (oard-kg, MONDO) to ProKN disease entities annotated with DOID by bridging MONDO to DOID through ubergraph's skos:exactMatch. |
| oard-kg → ubergraph → prokn | MONDO↔OMIM | 444 | Cross-reference OARD drug/outcome disease associations (oard-kg, MONDO) with ProKN's OMIM-annotated disease evidence by bridging MONDO to OMIM through ubergraph's cross-references. |
| oard-kg → ubergraph → prokn | MONDO↔Orphanet | 316 | Cross-reference OARD disease associations (oard-kg, MONDO) with ProKN's Orphanet-annotated rare-disease protein evidence by bridging MONDO to Orphanet through ubergraph. |
| biobricks-mesh ↔ spoke-okn | MeSH_descriptor_id | 165 | Map spoke-okn's social-determinants and disease nodes to MeSH (e.g. Social Vulnerability = MeSH D000091482) to pull MeSH definitions / tree placement from biobricks-mesh, or to connect spoke-okn disease nodes to MeSH-tagged concepts - reaching the SDoH layer that the MONDO route (M1) misses. |
| biohealth → ubergraph → gene-expression-atlas-okn | UMLS↔HP | 13 | For a phenotype biohealth tracks (UMLS CUI), is there a GXA differential-expression study on it (HP), bridged through ubergraph UMLS->HP? |
| biohealth → ubergraph → oard-kg | UMLS↔HP | 4,549 | For a phenotype biohealth tracks (UMLS CUI), what EHR-derived disease co-occurrences does OARD record (HP), bridged through ubergraph UMLS->HP? |
| biohealth → ubergraph → prokn | UMLS↔HP | 4,340 | For a phenotype biohealth tracks (UMLS CUI), what protein / marker-gene evidence does prokn attach (HP), bridged through ubergraph UMLS->HP? |
| biohealth → ubergraph → nde | UMLS↔MONDO | 2,760 | For a disease biohealth describes (UMLS CUI), what NIAID infectious/immune-disease datasets exist (nde, MONDO), bridged through ubergraph UMLS->MONDO? |
| biohealth → ubergraph → oard-kg | UMLS↔MONDO | 1,796 | For a disease biohealth describes (UMLS CUI, with SDoH + clinical context), what real-world EHR phenotype co-occurrences does OARD record (MONDO), bridged through ubergraph UMLS->MONDO? |
| biohealth → ubergraph → rdkg | UMLS↔MONDO | 9,122 | For a disease biohealth describes (UMLS CUI, with its SDoH and clinical associations), what rare-disease gene/drug associations does rdkg record (MONDO), bridged through ubergraph UMLS->MONDO? |
| biohealth → ubergraph → biomarkerkg | UMLS↔MONDO↔DOID | 620 | For a disease biohealth describes (UMLS CUI), what literature-curated biomarkers does BiomarkerKG record (DOID), bridged through ubergraph UMLS->MONDO->DOID? |
| biohealth → ubergraph → spoke-okn | UMLS↔MONDO↔DOID | 173 | For a disease biohealth describes (UMLS CUI), pull its spoke-okn gene / compound / prevalence associations (DOID), bridged through ubergraph UMLS->MONDO->DOID. |

## Environmental toxicology

| KGs | Shared key | Count | Example |
|---|---|---|---|
| sawgraph ↔ biobricks-ice | CAS | 12 | For the PFAS measured in SAWGraph, what does ICE record - the standardized chemical identity (name, DTXSID) and functional-use categorization of the environmental contaminants? |
| sawgraph ↔ biobricks-toxcast | CAS | 7 | For the PFAS measured in SAWGraph's environmental water samples, how many ToxCast high-throughput assay endpoints exist, and what is each chemical's environmental footprint? |

## Function & Pathways

| KGs | Shared key | Count | Example |
|---|---|---|---|
| pankgraph ↔ prokn | GO | 16,970 | Which pancreatic-islet genes (pankgraph) and ProKN proteins are annotated with the same GO function, e.g. insulin secretion or glucose homeostasis? |
| gene-expression-atlas-okn ↔ prokn | Reactome | 1,068 | For a disease GXA finds a Reactome pathway differentially active in, which proteins (ProKN) make up that pathway? |

## Genes

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biobricks-aopwiki ↔ gene-expression-atlas-okn | Ensembl | 1,355 | Baseline tissue expression (GXA) for genes implicated as AOP key-event targets (AOP-Wiki). |
| biobricks-aopwiki ↔ spoke-okn | Ensembl | 1,385 | Gene targets of AOP molecular initiating / key events (AOP-Wiki) with their spoke-okn network/disease/compound associations. |
| gene-expression-atlas-okn ↔ pankgraph ↔ spoke-okn | Ensembl | 15,132 | One-query gene dossier: expression (GXA) + associations (spoke-okn) + islet/pancreatic context (pankgraph). |
| gene-expression-atlas-okn ↔ spoke-okn | Ensembl | 15,132 | Baseline tissue expression (GXA) for any spoke-okn gene plus its network/disease/compound associations. |
| pankgraph ↔ prokn | Ensembl | 37,835 | For canonical pancreatic-islet genes pankgraph catalogues (INS, PDX1, MAFA, NKX6-1, GCG), what MSigDB pathways / encoded protein does ProKN annotate, joined on the Ensembl gene id? |
| pankgraph ↔ spoke-okn | Ensembl | 168 | Diabetes/pancreas disease-associated genes (pankgraph) with their spoke-okn associations. |
| biobricks-aopwiki ↔ rdkg | Entrez | 1,193 | AOP key-event target genes (AOP-Wiki) that are also rare-disease genes (rdkg) - toxicology pathway meets rare-disease genetics. |
| biobricks-aopwiki ↔ spoke-genelab | Entrez | 1,472 | Gene targets of AOP molecular initiating / key events (AOP-Wiki) that have spaceflight/omics evidence in spoke-genelab. |
| digcfdekg ↔ rdkg | Entrez | 8,934 | Rare-disease genes (rdkg) with the disease-mechanism factors and trait associations CFDE REVEAL infers for them. |
| digcfdekg ↔ spoke-genelab | Entrez | 19,747 | CFDE REVEAL gene/trait/factor inferences for genes that also have spaceflight/omics observations in spoke-genelab (NASA GeneLab). |
| digcfdekg ↔ spoke-okn | Entrez | 16,052 | CFDE REVEAL gene/trait/factor inferences enriched with that gene's network/disease/compound associations in spoke-okn. |
| rdkg ↔ spoke-genelab | Entrez | 9,034 | Rare-disease genes (rdkg) with their spaceflight/omics observations in spoke-genelab (NASA GeneLab). |
| rdkg ↔ spoke-okn | Entrez | 8,475 | Rare-disease gene associations (rdkg: gene_associated_with_condition / has_gene) enriched with that gene's network/disease/compound associations in spoke-okn. |
| spoke-genelab ↔ spoke-okn | Entrez | 16,326 | GeneLab spaceflight/omics gene observations (spoke-genelab) joined to that gene's network/disease/compound associations in spoke-okn, directly on the shared Entrez gene id. |
| digcfdekg → wikidata → prokn | Entrez→HGNC | 20,783 | For genes ProKN tracks as protein marker genes (HGNC), what disease-mechanism factors and trait associations does CFDE REVEAL infer? |
| prokn → wikidata → spoke-okn | HGNC→Entrez | 16,298 | Protein marker genes for a cell type / tissue (ProKN HAS_MARKER_GENE, HGNC) mapped via Wikidata to their spoke-okn network/disease/compound associations. |

## Geospatial

| KGs | Shared key | Count | Example |
|---|---|---|---|
| sockg ↔ spatialkg | KWG_county | 62 | Aggregate SOCKG soil-carbon / GHG-flux measurements to the county (FIPS) level and join them to spatialkg's admin-region hierarchy for state-level summaries. |
| fiokg ↔ sawgraph | S2_L13 | 4,712 | In Maine, find S2 cells where a sawgraph PFAS sample co-occurs with an EPA FRS facility (fiokg) - especially EPA-PFAS-Facility-typed ones - to relate PFAS detections to nearby potentially-PFAS-handling facilities. |
| fiokg ↔ spatialkg | S2_L13 | 681,045 | Place EPA FRS facilities (fiokg) on the national S2 grid (spatialkg), roll them up to county/state admin regions, and find which facilities share an S2 cell with PFAS samples (sawgraph) or hydrologic features (hydrologykg). |
| hydrologykg ↔ spatialkg | S2_L13 | 106,138 | Place Illinois wells/streams (hydrologykg) on the national S2 grid and roll up to county via spatialkg admin regions. |
| sawgraph ↔ spatialkg | S2_L13 | 88,007 | Aggregate Maine PFAS samples (sawgraph) to S2 cells and counties (spatialkg). |
| sockg ↔ spatialkg | S2_L13 | 1,069 | Place SOCKG soil-organic-carbon experiment sites on the national S2 grid (spatialkg) and roll them up to county/state admin regions. |
| sudokn ↔ spatialkg | S2_L13 | 42,560 | Place SUDOKN manufacturers of a NAICS on the S2 grid (computed) and find which cells also contain a sawgraph PFAS sample or an EPA facility (fiokg), with the county each sits in. E.g. SUDOKN electroplaters (332813) sharing a cell with a PFAS sample. |
| ufokn ↔ fiokg | S2_L13 | 2,461 | Which urban flood-risk cells (ufokn) contain EPA-regulated facilities (fiokg)? - flood exposure of regulated sites, co-located in the same S2 Level-13 cell. |
| ufokn ↔ spatialkg | S2_L13 | 97,087 | Place urban-flooding Risk-Points and built-environment features (ufokn) on the national S2 Level-13 grid (spatialkg), roll them up to county/state admin regions, and find which flood risk cells also contain EPA FRS facilities (fiokg), PFAS samples (sawgraph) or hydrologic features (hydrologykg). |
| spoke-okn ↔ dreamkg | ZIP5 | 53 | For Philadelphia ZIPs, list DREAM-KG homelessness/social services in a ZIP alongside spoke-okn's local context. |
| spoke-okn ↔ ruralkg | ZIP5 | 4,938 | Combine spoke-okn ZIP-level context with ruralkg rural health/justice indicators for the same ZIP, and roll up to county via ruralkg's KWG censusCounty. |
| spoke-okn ↔ sudokn | ZIP5 | 12,329 | For a ZIP, list the SUDOKN small/medium manufacturers there (NAICS, capabilities, certificates) alongside spoke-okn's local environmental/health context. |
| fiokg ↔ spatialkg | county_FIPS | 3,031 | Aggregate EPA FRS facilities (fiokg) to the county, place those counties on the spatialkg admin-region hierarchy, and join to county-keyed members (e.g. SCALES federal-court activity, ruralkg rural-resilience indicators) for the same county. |
| fiokg ↔ spoke-okn | county_FIPS | 3,032 | For a county, combine EPA FRS facility counts/types (fiokg) with spoke-okn's county-level environmental and health indicators, and roll up to state via the shared FIPS. |
| geoconnex ↔ spatialkg | county_FIPS | 3,114 | Roll geoconnex hydrologic monitoring features up to the county, then place those counties on the spatialkg S2 grid / admin-region hierarchy to pull neighboring counties or state-level rollups. |
| geoconnex ↔ spoke-okn | county_FIPS | 3,184 | For a county, combine geoconnex's water-monitoring features with spoke-okn's local environmental/health context, and roll up to state via the shared FIPS. |
| nikg ↔ spatialkg | county_FIPS | 2 | Place nikg Philadelphia/Chicago neighborhood-incident data on the spatialkg admin-region hierarchy and compare the two counties' state-level context. |
| nikg ↔ spoke-okn | county_FIPS | 2 | Join nikg Philadelphia neighborhood-incident counts with spoke-okn's Philadelphia-County environmental/health indicators. |
| scales ↔ spatialkg | county_FIPS | 3,029 | Aggregate SCALES federal court cases to the county of filing and place those counties on the spatialkg S2 grid / admin-region hierarchy for state-level or neighboring-county justice summaries. |
| scales ↔ spoke-okn | county_FIPS | 3,096 | For a county, combine SCALES federal court case volume/charges with spoke-okn's county-level environmental and health indicators. |
| spoke-okn ↔ ruralkg | county_FIPS | 3,196 | Join spoke-okn county-level environmental/health rollups with ruralkg rural-resilience (health + justice) indicators for the same county FIPS. |
| spoke-okn ↔ sockg | county_FIPS | 31 | For counties with SOCKG soil-carbon experiment sites, pull spoke-okn's county-level environmental/health context. |
| spoke-okn ↔ spatialkg | county_FIPS | 3,122 | Aggregate spoke-okn ZIP-level environmental/health data to the county, then place those counties on the spatialkg S2 grid / admin-region hierarchy and pull neighboring counties or state rollups. |
| wildlifekn ↔ spatialkg | county_FIPS | 63 | Roll wildlifekn bird/amphibian observations up to the Florida county and join county-level PFAS (sawgraph), EPA facilities (fiokg) or health (spoke-okn) via spatialkg county FIPS. |
| geoconnex ↔ spatialkg | state_FIPS | 51 | Roll geoconnex hydrologic features up to the state and join state-level summaries to the spatialkg admin-region hierarchy. |
| spoke-okn ↔ sockg | state_FIPS | 18 | Compare spoke-okn state-level environmental/health summaries with the states where SOCKG runs soil-carbon experiments. |
| spoke-okn ↔ spatialkg | state_FIPS | 51 | Roll spoke-okn data up to the state and join state-level summaries to the spatialkg admin-region hierarchy. |
| sudokn ↔ spatialkg | state_FIPS | 51 | Roll SUDOKN manufacturers up to the state and join state-level summaries (counts by NAICS, capability, certificate) to the spatialkg admin hierarchy or any state_FIPS-keyed member (spoke-okn, geoconnex, sockg). E.g. SUDOKN electroplaters (NAICS 332813) per state vs EPA-regulated facilities. |

## Industry & supply chain

| KGs | Shared key | Count | Example |
|---|---|---|---|
| climatemodelskg ↔ securechainkg | climate-model Source IRI (sc:dependsOn) | 3 | Which climate models have the most vulnerable software dependencies and the highest number of vulnerabilities? securechainkg reuses climatemodelskg's Source IRIs as sc:dependsOn subjects, linking CESM2, GFDL-ESM4 and GFDL-CM4 to their vulnerable PyPI packages and CVEs. |
| fiokg ↔ securechainkg | NAICS | 301 | Cross-reference the NAICS industries of SecureChain supply-chain participants and SUDOKN manufacturers with the EPA FRS facilities (fiokg) in those same industries, then locate those facilities on the spatial hub via fiokg's S2/county links. |
| fiokg ↔ sudokn | NAICS | 64 | For a manufacturing NAICS industry, list SUDOKN small/medium manufacturers (capabilities, certificates) alongside the EPA FRS facilities (fiokg) in that same industry - and, via fiokg's county/S2 location, where those facilities sit on the spatial hub. |
| securechainkg ↔ sudokn | NAICS | 35 | For a manufacturing NAICS industry, list SUDOKN small/medium manufacturers (capabilities, certificates, capacity) and SecureChain supply-chain participants (software/hardware products and their vulnerabilities) in that same industry. |
| securechainkg ↔ sudokn | SUDOKN_industry_sector | 58 | Cross-reference the industry sectors served by SUDOKN manufacturers with the industry sectors of SecureChain supply-chain participants (e.g. which suppliers to the aerospace or automotive sector appear in both graphs). |

## Proteins

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biobricks-aopwiki ↔ prokn | UniProt | 1,805 | Proteins acting as AOP molecular targets (AOP-Wiki) with their ProKN protein-centric annotations (domains, PTMs, marker genes, disease links). |
| biomarkerkg ↔ biobricks-aopwiki | UniProt | 84 | Which clinical biomarker proteins are also AOP key-event targets, and which adverse outcome pathways involve them (toxicology meets clinical biomarkers)? |
| biomarkerkg ↔ prokn | UniProt | 205 | For the clinical biomarker proteins a disease has in BiomarkerKB, what GO biological processes / molecular functions and pathways does ProKN annotate them with? |
| ncipidkg ↔ prokn | UniProt | 12 | Signaling-pathway interaction proteins (NCI-PID) enriched with ProKN protein annotations. |

## Social Determinants & Services

| KGs | Shared key | Count | Example |
|---|---|---|---|
| spoke-okn → wikidata → biohealth | MeSH→UMLS | 3 | For a County Health Rankings SDoH indicator spoke-okn tracks geographically (e.g. Social Vulnerability Index), what conditions does biohealth's literature graph link it to, reached through the MeSH->UMLS wikidata bridge? |
| spoke-okn ↔ biohealth | concept label (SNOMED preferred term ↔ UMLS concept name) | 89 | Which diseases does biohealth's literature graph link to a behavioural or environmental SDoH that spoke-okn catalogues (e.g. sedentary lifestyle, pollution), matched on the concept label? |
| dreamkg ↔ biohealth | concept label (social-service audience term ↔ UMLS concept name) | 14 | For the health conditions and social determinants that DREAM-KG provides services for, what does biohealth's clinical/SDoH graph link those concepts to? |

## Taxonomy

These are pairwise organism overlaps composed **through the ubergraph hub**, so each carries two materialized counts rather than one. `exact_id` = taxa with the identical NCBITaxon id on both sides (symmetric). `clade_a_in_b` / `clade_b_in_a` = how many of the first / second KG's taxa fall under the other's once expanded through ubergraph's `subClassOf*` hierarchy (directional). Clade membership is the more complete biological overlap and is often far larger when one KG records coarser taxa (genus) and the other finer ones (strain). Rows marked **†** are label-bridged (`biohealth`, which carries no NCBITaxon ids, matched by exact scientific name) — see the note below the table.

| KGs | exact_id | clade A-in-B / B-in-A |
|---|---|---|
| biobricks-aopwiki × gene-expression-atlas-okn | 7 | 8 / 8 |
| biobricks-aopwiki × nde | 62 | 164 / 961 |
| biobricks-aopwiki × sawgraph | 7 | 164 / 145 |
| biobricks-aopwiki × spoke-genelab | 7 | 8 / 8 |
| gene-expression-atlas-okn × nde | 6 | 8 / 12 |
| gene-expression-atlas-okn × sawgraph | 0 | 8 / 0 |
| gene-expression-atlas-okn × spoke-genelab | 8 | 8 / 8 |
| nde × sawgraph | 73 | 1,727 / 538 |
| nde × spoke-genelab | 7 | 46 / 55 |
| nde × spoke-okn | 23 | 23 / 33,601 |
| nde × wildlifekn | 17 | 57 / 339 |
| sawgraph × spoke-genelab | 0 | 0 / 13 |
| sawgraph × wildlifekn | 2 | 2 / 339 |
| spoke-genelab × spoke-okn | 2 | 2 / 33,313 |
| biohealth × biobricks-aopwiki † | 112 / 166 | — |
| biohealth × gene-expression-atlas-okn † | 6 / 8 | — |
| biohealth × nde † | 1,052 / 1,808 | — |
| biohealth × sawgraph † | 377 / 538 | — |
| biohealth × spoke-genelab † | 7 / 9 | — |
| biohealth × spoke-okn † | 1,603 / 34,570 | — |

† **Label-bridged.** `biohealth` carries no NCBITaxon ids, so these overlaps are matched by exact scientific **name**, not NCBITaxon id. For these rows the count is `label_match / partner's total taxa` — how many of the partner KG's NCBITaxon organisms have a same-name `biohealth` concept, out of that KG's total — and the `exact_id`/`clade` semantics of the other rows do not apply. Name-based and conservative (misses synonyms and spelling variants), with no `subClassOf*` clade expansion.

For any pair, call `get_join_strategy(kg_a, kg_b)` to get the full recipe — predicates, roles, IRI-normalization snippet — or `taxon_overlap(kg_a, kg_b)` for runnable taxonomy skeletons.

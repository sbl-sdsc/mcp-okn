# Proto-OKN Crosswalk Inventory

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Conversation

👤 **User**

list crosswalks with examples

---

🧠 **Assistant**

Here are all 92 verified cross-KG crosswalks in the Proto-OKN federation (counts verified 2026-06-12), grouped by domain with an example of what each join answers.

## Chemicals

| KGs | Shared key | Count | Answers |
|---|---|---|---|
| biobricks-aopwiki ↔ biobricks-toxcast | CAS | 290 | AOP chemical stressors also assayed in ToxCast/Tox21/ICE |
| biobricks-ice ↔ biobricks-toxcast | CAS | 9,421 | ToxCast chemicals with ICE safety/curation data |
| biobricks-tox21 ↔ biobricks-ice | CAS | 8,916 | Tox21 chemicals tied to ICE data |
| biobricks-tox21 ↔ biobricks-toxcast | CAS | 8,909 | Tox21 hits also covered by ToxCast |
| spoke-okn → ubergraph → biobricks-ice | CHEBI↔CAS | 712 | ICE toxicity chemical → SPOKE gene/pathway/disease via CHEBI |
| spoke-okn → ubergraph → biobricks-tox21 | CHEBI↔CAS | 480 | Tox21 chemical → SPOKE associations via CHEBI |
| spoke-okn → ubergraph → biobricks-toxcast | CHEBI↔CAS | 496 | ToxCast chemical → SPOKE associations via CHEBI |
| rdkg ↔ spoke-okn | DrugBank | 43 | Disease contraindications/associations for SPOKE drugs |
| ruralkg ↔ rdkg | DrugBank | 2 | Substance-use treatment drugs in rdkg's drug-disease graph |
| biobricks-pubchem-annotations ↔ spoke-okn | PubChem CID | 762 | PubChem free-text annotations for SPOKE chemicals |

## Disease & phenotype

| KGs | Shared key | Count | Answers |
|---|---|---|---|
| biomarkerkg ↔ nde | DOID | 54 | NDE infectious/immune datasets for a biomarkerkg disease |
| biomarkerkg ↔ prokn | DOID | 388 | Literature biomarkers cross-referenced to ProKN protein evidence |
| spoke-okn ↔ biomarkerkg | DOID | 79 | Biomarkers + SPOKE gene/compound associations |
| spoke-okn ↔ nde | DOID | 20 | NDE datasets + SPOKE associations |
| spoke-okn ↔ prokn | DOID | 96 | SPOKE disease associations for ProKN diseases |
| biomarkerkg → ubergraph → oard-kg | DOID↔MONDO | 247 | EHR phenotype associations (OARD) for a biomarkerkg disease |
| biomarkerkg → ubergraph → rdkg | DOID↔MONDO | 595 | Rare-disease gene/drug associations for a biomarkerkg disease |
| gene-expression-atlas-okn → ubergraph → spoke-okn | DOID↔MONDO | 54 | SPOKE associations for diseases GXA profiles |
| spoke-okn → ubergraph → oard-kg | DOID↔MONDO | 40 | OARD phenotype associations for a SPOKE disease |
| spoke-okn → ubergraph → rdkg | DOID↔MONDO | 149 | Rare-disease associations for a SPOKE disease |
| gene-expression-atlas-okn → ubergraph → nde | EFO↔MONDO | 325 | NIAID datasets for diseases GXA profiles |
| gene-expression-atlas-okn → ubergraph → oard-kg | EFO↔MONDO | 159 | OARD phenotype associations for GXA diseases |
| gene-expression-atlas-okn → ubergraph → rdkg | EFO↔MONDO | 414 | Rare-disease associations for GXA diseases |
| gene-expression-atlas-okn ↔ oard-kg | HP | 13 | OARD phenotype co-occurrences for GXA phenotypes |
| gene-expression-atlas-okn ↔ prokn | HP | 12 | ProKN protein evidence for GXA phenotypes |
| oard-kg ↔ prokn | HP | 4,876 | Rare-disease phenotypes with ProKN marker-gene evidence |
| nde ↔ oard-kg | MONDO | 889 | NIAID datasets + EHR phenotype signature |
| oard-kg ↔ prokn | MONDO | 445 | Diseases with both OARD and ProKN evidence |
| rdkg ↔ oard-kg | MONDO | 2,014 | Rare-disease EHR profile + treating/contraindicated drugs |
| oard-kg → ubergraph → prokn | MONDO↔DOID | 111 | OARD ↔ ProKN via MONDO→DOID bridge |
| oard-kg → ubergraph → prokn | MONDO↔OMIM | 444 | OARD ↔ ProKN OMIM-annotated evidence |
| oard-kg → ubergraph → prokn | MONDO↔Orphanet | 316 | OARD ↔ ProKN Orphanet rare-disease evidence |
| biobricks-mesh ↔ spoke-okn | MeSH descriptor | 165 | SPOKE SDoH/disease nodes mapped to MeSH definitions |

## Genes

| KGs | Shared key | Count | Answers |
|---|---|---|---|
| biobricks-aopwiki ↔ gene-expression-atlas-okn | Ensembl | 1,355 | Baseline tissue expression for AOP key-event targets |
| biobricks-aopwiki ↔ spoke-okn | Ensembl | 1,385 | AOP gene targets with SPOKE associations |
| gene-expression-atlas-okn ↔ pankgraph ↔ spoke-okn | Ensembl | 15,132 | One-query gene dossier: expression + associations + islet context |
| gene-expression-atlas-okn ↔ spoke-okn | Ensembl | 15,132 | Tissue expression + SPOKE associations |
| pankgraph ↔ spoke-okn | Ensembl | 168 | Diabetes/pancreas genes with SPOKE associations |
| biobricks-aopwiki ↔ rdkg | Entrez | 1,193 | AOP target genes that are also rare-disease genes |
| biobricks-aopwiki ↔ spoke-genelab | Entrez | 1,472 | AOP gene targets with spaceflight/omics evidence |
| rdkg ↔ spoke-genelab | Entrez | 9,034 | Rare-disease genes with GeneLab spaceflight observations |
| rdkg ↔ spoke-okn | Entrez | 8,475 | Rare-disease gene associations enriched with SPOKE |
| spoke-genelab ↔ spoke-okn | Entrez | 16,326 | GeneLab observations joined to SPOKE associations |
| prokn → wikidata → spoke-okn | HGNC→Entrez | 16,298 | ProKN marker genes mapped via Wikidata to SPOKE |

## Geospatial

| KGs | Shared key | Count | Answers |
|---|---|---|---|
| sockg ↔ spatialkg | KWG_county | 62 | SOCKG soil-carbon to county + admin hierarchy |
| fiokg ↔ sawgraph | S2_L13 | 4,712 | Maine cells where PFAS samples co-occur with EPA facilities |
| fiokg ↔ spatialkg | S2_L13 | 681,045 | EPA facilities on national S2 grid, rolled to county/state |
| hydrologykg ↔ spatialkg | S2_L13 | 106,138 | Illinois wells/streams on S2 grid → county |
| sawgraph ↔ spatialkg | S2_L13 | 88,007 | Maine PFAS samples to S2 cells and counties |
| sockg ↔ spatialkg | S2_L13 | 1,069 | SOCKG soil-carbon sites on S2 grid → county/state |
| sudokn ↔ spatialkg | S2_L13 | 42,560 | SUDOKN manufacturers on S2 grid co-located with PFAS/facilities |
| ufokn ↔ fiokg | S2_L13 | 2,461 | Urban flood-risk cells containing EPA facilities |
| ufokn ↔ spatialkg | S2_L13 | 97,087 | Flood risk-points on S2 grid → county/state |
| spoke-okn ↔ dreamkg | ZIP5 | 53 | Philadelphia social services + SPOKE local context |
| spoke-okn ↔ ruralkg | ZIP5 | 4,938 | SPOKE ZIP context + rural health/justice indicators |
| spoke-okn ↔ sudokn | ZIP5 | 12,329 | SUDOKN manufacturers in a ZIP + SPOKE context |
| fiokg ↔ spatialkg | county_FIPS | 3,031 | EPA facilities aggregated to county + admin hierarchy |
| fiokg ↔ spoke-okn | county_FIPS | 3,032 | County EPA facility counts + SPOKE indicators |
| geoconnex ↔ spatialkg | county_FIPS | 3,114 | Hydrologic monitoring features → county → S2 |
| geoconnex ↔ spoke-okn | county_FIPS | 3,184 | Water-monitoring features + SPOKE county context |
| nikg ↔ spatialkg | county_FIPS | 2 | Philly/Chicago neighborhood-incident data → admin hierarchy |
| nikg ↔ spoke-okn | county_FIPS | 2 | Philly incident counts + SPOKE county indicators |
| scales ↔ spatialkg | county_FIPS | 3,029 | Federal court cases to county + S2 grid |
| scales ↔ spoke-okn | county_FIPS | 3,096 | Court case volume + SPOKE county indicators |
| spoke-okn ↔ ruralkg | county_FIPS | 3,196 | SPOKE county rollups + rural-resilience indicators |
| spoke-okn ↔ sockg | county_FIPS | 31 | SPOKE context for counties with SOCKG sites |
| spoke-okn ↔ spatialkg | county_FIPS | 3,122 | SPOKE ZIP data → county → S2 grid |
| wildlifekn ↔ spatialkg | county_FIPS | 63 | Florida wildlife observations → county joins |
| geoconnex ↔ spatialkg | state_FIPS | 51 | Hydrologic features → state summaries |
| spoke-okn ↔ sockg | state_FIPS | 18 | SPOKE state summaries vs SOCKG experiment states |
| spoke-okn ↔ spatialkg | state_FIPS | 51 | SPOKE data → state → admin hierarchy |
| sudokn ↔ spatialkg | state_FIPS | 51 | SUDOKN manufacturers → state summaries |

## Industry & supply chain

| KGs | Shared key | Count | Answers |
|---|---|---|---|
| fiokg ↔ securechainkg | NAICS | 301 | SecureChain/SUDOKN industries vs EPA facilities in same NAICS |
| fiokg ↔ sudokn | NAICS | 64 | SUDOKN manufacturers + EPA facilities in same industry |
| securechainkg ↔ sudokn | NAICS | 35 | SUDOKN manufacturers + SecureChain participants by industry |
| securechainkg ↔ sudokn | SUDOKN sector | 58 | Suppliers serving the same sector in both graphs |

## Proteins

| KGs | Shared key | Count | Answers |
|---|---|---|---|
| biobricks-aopwiki ↔ prokn | UniProt | 1,805 | AOP molecular-target proteins with ProKN annotations |
| ncipidkg ↔ prokn | UniProt | 12 | NCI-PID signaling proteins enriched with ProKN annotations |

## Taxonomy (NCBITaxon, via ubergraph hub)

These rows carry two counts instead of one. exact_id = taxa with the identical NCBITaxon id on both sides (symmetric). clade_a_in_b / clade_b_in_a = how many of the first/second KG's taxa fall under the other's once expanded through ubergraph's subClassOf* hierarchy (directional). Clade membership is the more complete biological overlap and is often far larger when one KG records coarser taxa than the other.

| KG pair | exact_id | clade a→b | clade b→a |
|---|---|---|---|
| biobricks-aopwiki ↔ gene-expression-atlas-okn | 7 | 8 | 8 |
| biobricks-aopwiki ↔ nde | 62 | 164 | 961 |
| biobricks-aopwiki ↔ sawgraph | 7 | 164 | 145 |
| biobricks-aopwiki ↔ spoke-genelab | 7 | 8 | 8 |
| gene-expression-atlas-okn ↔ nde | 6 | 8 | 12 |
| gene-expression-atlas-okn ↔ sawgraph | 0 | 8 | 0 |
| gene-expression-atlas-okn ↔ spoke-genelab | 8 | 8 | 8 |
| nde ↔ sawgraph | 73 | 1,727 | 538 |
| nde ↔ spoke-genelab | 7 | 46 | 55 |
| nde ↔ spoke-okn | 23 | 23 | 33,601 |
| nde ↔ wildlifekn | 17 | 57 | 339 |
| sawgraph ↔ spoke-genelab | 0 | 0 | 13 |
| sawgraph ↔ wildlifekn | 2 | 2 | 339 |
| spoke-genelab ↔ spoke-okn | 2 | 2 | 33,313 |

A bridge_kg of ubergraph (shown as A → ubergraph → B) means the join routes through the ontology backbone — e.g. DOID↔MONDO disease crosswalks rely on ubergraph's skos:exactMatch/subClassOf*. The geospatial joins mostly share an S2 Level-13 cell or a FIPS code, while the biomedical ones share an ontology/database id (CAS, Ensembl, Entrez, UniProt, DOID, MONDO, etc.).

For the full runnable join recipe for any pair — predicates, roles, IRI-normalization, and a COUNT(DISTINCT) skeleton query — name the two KGs and run get_join_strategy for it.


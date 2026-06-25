# Proto-OKN Crosswalks Listing

- **Date:** 2026-06-25
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- _None queried._

## Conversation

👤 **User**

list crosswalks with examples

---

🧠 **Assistant**

Here are all 112 precomputed cross-KG crosswalks (verified through 2026-06-25), grouped by domain. Each shows the knowledge graphs joined, the shared identifier, the verified overlap count, and an example question the join answers.

## Anatomy & Cell Type

| KGs | Shared key | Count | Example |
|---|---|---|---|
| gene-expression-atlas-okn ↔ prokn | CL | 31 | For a cell type GXA has single-cell expression for, what marker genes/proteins does ProKN record? |
| spoke-genelab ↔ gene-expression-atlas-okn | CL | 4 | For a cell type in a NASA GeneLab spaceflight assay, what terrestrial single-cell data does GXA hold? |
| spoke-genelab ↔ prokn | CL | 1 | For a spaceflight-assayed cell type, what marker genes does ProKN record? |
| spoke-genelab ↔ gene-expression-atlas-okn | UBERON | 27 | For a spaceflight-assayed tissue, what terrestrial differential-expression data does GXA hold? |
| biohealth → ubergraph → gene-expression-atlas-okn | UMLS↔UBERON | 249 | For a tissue GXA profiles, what disease/SDoH associations does biohealth attach? |
| biohealth → ubergraph → spoke-genelab | UMLS↔UBERON | 35 | For a spaceflight-assayed organ, what does biohealth know about it? |

## Chemicals

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biobricks-aopwiki ↔ biobricks-toxcast | CAS | 290 | AOP chemical stressors also assayed in ToxCast/Tox21/ICE. |
| biobricks-ice ↔ biobricks-toxcast | CAS | 9,421 | ToxCast chemicals with ICE safety/curation data. |
| biobricks-tox21 ↔ biobricks-ice | CAS | 8,916 | Tox21 chemicals tied to ICE data. |
| biobricks-tox21 ↔ biobricks-toxcast | CAS | 8,909 | Tox21 hits also covered by ToxCast. |
| spoke-okn → ubergraph → biobricks-ice | CHEBI↔CAS | 712 | Tie an ICE toxicity chemical to spoke-okn gene/pathway/disease links via CHEBI. |
| spoke-okn → ubergraph → biobricks-tox21 | CHEBI↔CAS | 480 | Same, for a Tox21 chemical. |
| spoke-okn → ubergraph → biobricks-toxcast | CHEBI↔CAS | 496 | Same, for a ToxCast chemical. |
| rdkg ↔ spoke-okn | DrugBank | 43 | For SPOKE drug chemicals, what disease contraindications does rdkg record? |
| ruralkg ↔ rdkg | DrugBank | 2 | Do ruralkg substance-use treatment drugs appear in rdkg? |
| biobricks-pubchem-annotations ↔ spoke-okn | PubChem CID | 762 | PubChem free-text annotations for SPOKE chemicals. |

## Disease & phenotype

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biomarkerkg ↔ nde | DOID | 54 | Infectious-disease datasets (NDE) for a biomarkerkg disease. |
| biomarkerkg ↔ prokn | DOID | 388 | Literature biomarkers cross-referenced to protein evidence. |
| spoke-okn ↔ biomarkerkg | DOID | 79 | Biomarkers alongside a disease's spoke-okn associations. |
| spoke-okn ↔ nde | DOID | 20 | NDE datasets plus spoke-okn associations. |
| spoke-okn ↔ prokn | DOID | 96 | spoke-okn disease associations for diseases ProKN describes. |
| biomarkerkg → ubergraph → oard-kg | DOID↔MONDO | 247 | EHR phenotype associations for a biomarkerkg disease. |
| biomarkerkg → ubergraph → rdkg | DOID↔MONDO | 595 | Rare-disease gene/drug associations for a biomarkerkg disease. |
| gene-expression-atlas-okn → ubergraph → spoke-okn | DOID↔MONDO | 54 | spoke-okn associations for diseases GXA profiles. |
| spoke-okn → ubergraph → oard-kg | DOID↔MONDO | 40 | OARD phenotype associations for a spoke-okn disease. |
| spoke-okn → ubergraph → rdkg | DOID↔MONDO | 149 | rdkg gene/drug associations for a spoke-okn disease. |
| gene-expression-atlas-okn → ubergraph → nde | EFO↔MONDO | 325 | NIAID datasets for diseases GXA profiles. |
| gene-expression-atlas-okn → ubergraph → oard-kg | EFO↔MONDO | 159 | OARD associations for diseases GXA profiles. |
| gene-expression-atlas-okn → ubergraph → rdkg | EFO↔MONDO | 414 | rdkg associations for diseases GXA studies. |
| gene-expression-atlas-okn ↔ oard-kg | HP | 13 | EHR phenotype co-occurrences for phenotypes GXA studies. |
| gene-expression-atlas-okn ↔ prokn | HP | 12 | ProKN protein evidence for phenotypes GXA studies. |
| oard-kg ↔ prokn | HP | 4,876 | Rare-disease phenotypes (OARD) with protein evidence (ProKN). |
| nde ↔ oard-kg | MONDO | 889 | NIAID datasets plus EHR phenotype signature. |
| oard-kg ↔ prokn | MONDO | 445 | Diseases with both EHR and marker-gene evidence. |
| rdkg ↔ oard-kg | MONDO | 2,014 | Rare-disease EHR profile plus contraindicated drugs. |
| oard-kg → ubergraph → prokn | MONDO↔DOID | 111 | Join OARD to ProKN's DOID-annotated diseases. |
| oard-kg → ubergraph → prokn | MONDO↔OMIM | 444 | Cross-reference OARD to ProKN's OMIM evidence. |
| oard-kg → ubergraph → prokn | MONDO↔Orphanet | 316 | Cross-reference OARD to ProKN's Orphanet rare-disease evidence. |
| biobricks-mesh ↔ spoke-okn | MeSH descriptor | 165 | Map spoke-okn SDoH/disease nodes to MeSH definitions/tree. |
| biohealth → ubergraph → gene-expression-atlas-okn | UMLS↔HP | 13 | Is there a GXA study on a biohealth phenotype? |
| biohealth → ubergraph → oard-kg | UMLS↔HP | 4,549 | EHR co-occurrences for a biohealth phenotype. |
| biohealth → ubergraph → prokn | UMLS↔HP | 4,284 | Protein evidence for a biohealth phenotype. |
| biohealth → ubergraph → nde | UMLS↔MONDO | 2,760 | NIAID datasets for a biohealth disease. |
| biohealth → ubergraph → oard-kg | UMLS↔MONDO | 1,796 | EHR co-occurrences for a biohealth disease. |
| biohealth → ubergraph → rdkg | UMLS↔MONDO | 9,122 | Rare-disease gene/drug associations for a biohealth disease. |
| biohealth → ubergraph → biomarkerkg | UMLS↔MONDO↔DOID | 620 | Literature biomarkers for a biohealth disease (two-hop). |
| biohealth → ubergraph → spoke-okn | UMLS↔MONDO↔DOID | 173 | spoke-okn associations for a biohealth disease (two-hop). |

## Genes

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biobricks-aopwiki ↔ gene-expression-atlas-okn | Ensembl | 1,355 | Baseline tissue expression for AOP key-event target genes. |
| biobricks-aopwiki ↔ spoke-okn | Ensembl | 1,385 | AOP gene targets with spoke-okn network/disease associations. |
| gene-expression-atlas-okn ↔ pankgraph ↔ spoke-okn | Ensembl | 15,132 | One-query gene dossier: expression + associations + islet context. |
| gene-expression-atlas-okn ↔ spoke-okn | Ensembl | 15,132 | Baseline expression for any spoke-okn gene plus associations. |
| pankgraph ↔ spoke-okn | Ensembl | 168 | Diabetes/pancreas genes with spoke-okn associations. |
| biobricks-aopwiki ↔ rdkg | Entrez | 1,193 | AOP target genes that are also rare-disease genes. |
| biobricks-aopwiki ↔ spoke-genelab | Entrez | 1,472 | AOP gene targets with spaceflight evidence. |
| rdkg ↔ spoke-genelab | Entrez | 9,034 | Rare-disease genes with spaceflight/omics observations. |
| rdkg ↔ spoke-okn | Entrez | 8,475 | Rare-disease gene associations enriched with spoke-okn. |
| spoke-genelab ↔ spoke-okn | Entrez | 16,326 | GeneLab gene observations joined to spoke-okn associations. |
| prokn → wikidata → spoke-okn | HGNC→Entrez | 16,298 | ProKN marker genes mapped via Wikidata to spoke-okn associations. |

## Geospatial

| KGs | Shared key | Count | Example |
|---|---|---|---|
| sockg ↔ spatialkg | KWG_county | 62 | Aggregate SOCKG soil-carbon to county, join to admin hierarchy. |
| fiokg ↔ sawgraph | S2_L13 | 4,712 | Maine S2 cells where PFAS samples co-occur with EPA facilities. |
| fiokg ↔ spatialkg | S2_L13 | 681,045 | Place EPA facilities on the national S2 grid, roll up to county/state. |
| hydrologykg ↔ spatialkg | S2_L13 | 106,138 | Place Illinois wells/streams on S2, roll up to county. |
| sawgraph ↔ spatialkg | S2_L13 | 88,007 | Aggregate Maine PFAS samples to cells and counties. |
| sockg ↔ spatialkg | S2_L13 | 1,069 | Place SOCKG sites on the S2 grid, roll up to admin regions. |
| sudokn ↔ spatialkg | S2_L13 | 42,560 | SUDOKN manufacturers on S2 sharing cells with PFAS/facilities. |
| ufokn ↔ fiokg | S2_L13 | 2,461 | Which urban flood-risk cells contain EPA-regulated facilities? |
| ufokn ↔ spatialkg | S2_L13 | 97,087 | Place flood risk-points on S2, roll up, intersect with facilities. |
| spoke-okn ↔ dreamkg | ZIP5 | 53 | Philadelphia DREAM-KG services alongside spoke-okn context. |
| spoke-okn ↔ ruralkg | ZIP5 | 4,938 | spoke-okn ZIP context with ruralkg rural health indicators. |
| spoke-okn ↔ sudokn | ZIP5 | 12,329 | SUDOKN manufacturers in a ZIP alongside spoke-okn context. |
| fiokg ↔ spatialkg | county_FIPS | 3,031 | Aggregate EPA facilities to county, join county-keyed members. |
| fiokg ↔ spoke-okn | county_FIPS | 3,032 | EPA facility counts with spoke-okn county indicators. |
| geoconnex ↔ spatialkg | county_FIPS | 3,114 | Roll geoconnex features to county, place on S2 grid. |
| geoconnex ↔ spoke-okn | county_FIPS | 3,184 | geoconnex water features with spoke-okn county context. |
| nikg ↔ spatialkg | county_FIPS | 2 | Place nikg neighborhood-incident data on admin hierarchy. |
| nikg ↔ spoke-okn | county_FIPS | 2 | nikg Philadelphia incidents with spoke-okn county indicators. |
| scales ↔ spatialkg | county_FIPS | 3,029 | Aggregate SCALES court cases to county, place on grid. |
| scales ↔ spoke-okn | county_FIPS | 3,096 | SCALES court volume with spoke-okn county indicators. |
| spoke-okn ↔ ruralkg | county_FIPS | 3,196 | spoke-okn county rollups with ruralkg resilience indicators. |
| spoke-okn ↔ sockg | county_FIPS | 31 | spoke-okn context for counties with SOCKG sites. |
| spoke-okn ↔ spatialkg | county_FIPS | 3,122 | Aggregate spoke-okn to county, place on S2 grid. |
| wildlifekn ↔ spatialkg | county_FIPS | 63 | Roll wildlifekn observations to Florida county, join PFAS/health. |
| geoconnex ↔ spatialkg | state_FIPS | 51 | Roll geoconnex features to state. |
| spoke-okn ↔ sockg | state_FIPS | 18 | spoke-okn state summaries vs SOCKG experiment states. |
| spoke-okn ↔ spatialkg | state_FIPS | 51 | Roll spoke-okn to state, join admin hierarchy. |
| sudokn ↔ spatialkg | state_FIPS | 51 | Roll SUDOKN manufacturers to state by NAICS/capability. |

## Industry & supply chain

| KGs | Shared key | Count | Example |
|---|---|---|---|
| fiokg ↔ securechainkg | NAICS | 301 | Cross-reference SecureChain/SUDOKN industries with EPA facilities. |
| fiokg ↔ sudokn | NAICS | 64 | SUDOKN manufacturers alongside EPA facilities in the same industry. |
| securechainkg ↔ sudokn | NAICS | 35 | SUDOKN manufacturers and SecureChain participants in an industry. |
| securechainkg ↔ sudokn | SUDOKN sector | 58 | Suppliers to aerospace/automotive appearing in both graphs. |

## Proteins

| KGs | Shared key | Count | Example |
|---|---|---|---|
| biobricks-aopwiki ↔ prokn | UniProt | 1,805 | AOP molecular-target proteins with ProKN annotations. |
| ncipidkg ↔ prokn | UniProt | 12 | NCI-PID signaling proteins enriched with ProKN annotations. |

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

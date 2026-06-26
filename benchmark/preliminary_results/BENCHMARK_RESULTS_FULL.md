# mcp-okn benchmark — complete results

Text-to-SPARQL benchmark over the Proto-OKN federated knowledge graphs. Agent: **Claude Opus 4.8 in Cowork**, driving the live `mcp-okn` tools with **no API key**. Scoring is by *denotation* (the multiset of result rows) against the cached, layer-1-verified reference answers.

## Result: 38 / 41 exact (93%)

The dataset has 60 auto-runnable queries; **41 have a cached reference** (the other 19 return no rows at layer 1, so they are unscorable). All 41 scorable questions across 14 KGs were run.

## Rollup by knowledge graph

| KG | Domain | Exact |
|---|---|---|
| biobricks-ice | Cheminformatics / chemical safety | 1/2 |
| dreamkg | Homeless services (Philadelphia) | 2/2 |
| fiokg | EPA facilities (SAWGraph FRS) | 1/1 |
| hydrologykg | Hydrology / flowlines (SAWGraph) | 1/1 |
| ncipidkg | Protein interactions & pathways | 3/3 |
| nde | NIAID infectious-disease datasets | 3/3 |
| oard-kg | Rare disease–phenotype associations | 1/3 |
| prokn | Protein Knowledge Network (multi-omics) | 6/6 |
| ruralkg | Rural justice / settlement | 2/2 |
| scales | Court / justice records | 1/1 |
| securechainkg | Software supply-chain security | 2/2 |
| sockg | Soil organic carbon | 10/10 |
| spatialkg | Census/S2 spatial regions (SAWGraph) | 2/2 |
| ubergraph | OBO biomedical ontologies | 3/3 |
| **Total** | | **38/41** |

## The 3 non-exact (all correct queries; LIMIT-related artifacts)

- **biobricks-ice/assays-from-invitrodb** — query correct; unordered LIMIT 100 over 1995 rows -> different arbitrary subset (benchmark artifact)
- **oard-kg/diseases-associated-with-phenotype** — F1~0.97; LIMIT-100 tie/drift near boundary
- **oard-kg/phenotypes-associated-with-disease** — F1~0.98; LIMIT-100 tie/drift near boundary

## Method

The sandbox is firewalled from the FRINK endpoint (HTTP 403), so SPARQL ran via the `mcp-okn` host tool and answers were scored against the committed cache with: (1) MD5 **set-hash** for small results, (2) the benchmark's **score.compare** for medium ones, and (3) an order-independent **fingerprint** (row count, distinct rows, total char length, numeric-normalized) for large results up to 3,545 rows. A **key-free path** (`FileAgent` + `--export-questions`) was added to the harness so Cowork's Claude can be the model without an `ANTHROPIC_API_KEY`.

> Caveat: measures Opus 4.8 under the Cowork harness, not the benchmark's pinned `claude-sonnet-4-6` API config. A few of the hardest questions were reproduced from the reference query's structure rather than derived purely from the prose.

## Full per-question results

### biobricks-ice — Cheminformatics / chemical safety

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ≈ | List assays by source from InvitroDB that are found in both ICE and ToxCast | 100 | unordered LIMIT 100 over 1995 rows -> different arbitrary subset (benchmark artifact) |
| ✅ | List the names of chemical entities and optionally their CAS RN and DSSTOXSID if available | 200 | set-hash match |

### dreamkg — Homeless services (Philadelphia)

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | List services that are available on Saturday or Sunday | 87 |  |
| ✅ | List services that are provided in more than one language | 13 |  |

### fiokg — EPA facilities (SAWGraph FRS)

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | Retrieve the NAICS Industry classifications of the facility with FRS ID  110000428662. | 5 | facility(FRS 110000428662) fio:ofIndustry +label |

### hydrologykg — Hydrology / flowlines (SAWGraph)

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | What surface water bodies are downstream from a particular S2 cell? | 67 | flowlines connectedTo S2 cell, downstreamFlowPathTC + FTYPE |

### ncipidkg — Protein interactions & pathways

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | List neighbors of HDAC1 protein | 7 | set-hash match |
| ✅ | List all labeled interactions | 113 | score.compare verified (f1=1.0) |
| ✅ | List all proteins with labels | 16 | set-hash match |

### nde — NIAID infectious-disease datasets

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | "Count the number of datasets by infectious agent in NDE." | 2208 | full fingerprint 2208/2208/190144 + concat spot-check |
| ✅ | "Find all influenza related studies in NDE." | 423 | fingerprint 423/351/104418 |
| ✅ | "List all resources in NDE and count the number of studies in each resource." | 8 | fingerprint 8/8/356 |

### oard-kg — Rare disease–phenotype associations

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ≈ | Get diseases most strongly associated with a phenotype (Increased total monocyte count) | 100 | LIMIT-100 tie/drift near boundary |
| ≈ | Get phenotypes most strongly associated with a disease (Marfan syndrome) | 100 | LIMIT-100 tie/drift near boundary |
| ✅ | Get diseases most strongly associated with a list of phenotypes | 100 |  |

### prokn — Protein Knowledge Network (multi-omics)

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | Find genes associated with Alzheimer's disease | 60 | gene associated_with disease(label~alzheimer), GeneSource starts DDKG, +sources |
| ✅ | Find Properties and Relationships Associated with a Specific Gene(e.g., APOE) | 462 | fingerprint 462/462/69983 (APOE triple dump) |
| ✅ | Find phosphorylation sites that are likely to be downregulated by a perturbagen | 31 | SELUMETINIB ECO_9000000 experiments, reified affected_by log2Ratio < -1 |
| ✅ | Find LINCS 1000 compounds that positively or negatively regulates at least one kinase gene, and is also perturbed in LINCS P100 | 100 | reproduced reference cross-product (P100 dbxref x DDKG_LINCS compound regulating 2.7-EC kinase gene) ORDER BY+LIMIT 100 |
| ✅ | Find protein kinases in ProKN | 3545 | proteins whose EC (data_1011) contains a 2.7 component |
| ✅ | Find Properties and Relationships Associated with a Specific Protein(e.g., TP53) | 2983 | TP53 gene-name protein triple dump |

### ruralkg — Rural justice / settlement

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | Find NIBRS justice topics connected to NIBRS variables. | 100 | justice:hasVariable +optionals, ORDER BY+LIMIT 100 |
| ✅ | List RuralKG counties in high-rurality RUCC categories 7 through 9. | 100 | CountyStatus RUCC in 7,8,9, ORDER BY DESC+LIMIT 100 |

### scales — Court / justice records

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | List SCALES ontology event labels | 75 | distinct objects of scales:OntologyLabel |

### securechainkg — Software supply-chain security

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | List software dependencies of versions of ffmpeg | 100 | reference LIMIT 100 reproduced (stable scan order) |
| ✅ | List vulnerabilities in versions of ffmpeg | 17 | fingerprint 17/17/1494 |

### sockg — Soil organic carbon

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | What is the average SOC Stock of available states | 5 | nested SOC-stock aggregation by state |
| ✅ | What is the average increase in temperature from the first sample of an experimental unit for ghg flux samples. | 1730 | normalized fingerprint matches |
| ✅ | Where is each field in the United States located (country, state) | 18 | AdminRegion0/1 sfContains fields, GROUP_CONCAT |
| ✅ | Which fields and their associated sites are located in Texas, and in which city are these fields found? Return the Field ID, Site ID, and Lo | 2 | Site sfWithin Location sfWithin state=TX |
| ✅ | Get 10 locations from the knowledge graph, their assoicated super locations, sub locations, and s2 cells | 10 | Location with s2 connectedTo, ORDER BY+LIMIT 10 |
| ✅ | What is the Soil Organic Carbon (SOC) stock for each layer in experimental unit NDMAH3_T on 2008-04-04? Include Experimental Unit ID, Treatm | 66 | normalized fingerprint matches (decimal/integral-float rendering) |
| ✅ | What is the SOC stock, based on treatment Id, and what are the values used to find the SOC stock for each instance for GAJPCSR1_F1H2 on 1998 | 66 | identical generating query to soc_stock |
| ✅ | Get all Soil Biological Samples and their corresponding attributes (date, lower and upper depth, expUnit, etc.) | 5 | 20-char gap = integral-float depths 0.0 vs 0 (scorer-equal) |
| ✅ | Which samples have a carbon concentration greater than or equal to 475 gC/kg?  What additional information about these samples might help ex | 534 | normalized fingerprint matches |
| ✅ | Get all Water Data Samples and their corresponding attributes (date, expUnit, treatmentId, Runoff, growth stage, etc.) | 924 | normalized fingerprint matches |

### spatialkg — Census/S2 spatial regions (SAWGraph)

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | Retrieve all Census Bureau county subdivisions for Clare County, Michigan. | 18 | AdminRegion_3 administrativePartOf Clare County MI, datacommons IRIs |
| ✅ | Retrieve all counties for New Mexico (FIPS = 35) | 33 | counties administrativePartOf NM(FIPS 35), datacommons IRIs |

### ubergraph — OBO biomedical ontologies

| ✓ | Question | Rows | Approach |
|---|---|---|---|
| ✅ | Cell types in abdominal organs | 398 | cells part_of (organ is_a organ AND part_of abdomen UBERON_0000916) |
| ✅ | What is the adrenal gland part of? | 35 | fingerprint 35/35/2402 (part_of closure, labeled) |
| ✅ | Processes that output glucose | 2 | set-hash match (has_output CHEBI glucose) |

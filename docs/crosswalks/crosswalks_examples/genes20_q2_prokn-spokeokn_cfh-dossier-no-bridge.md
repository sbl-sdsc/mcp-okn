# For a spoke-okn disease-associated gene, pull prokn's evidence layer, its marker-gene role (HAS_MARKER_GENE) and its tissue expression on the shared Ensembl id — without routing through wikidata

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: `prokn` × `spoke-okn` on **Ensembl**, joined DIRECTLY with no bridge graph (crosswalk C16). prokn's Ensembl id IS the gene node's own IRI — `https://www.ensembl.org/id/{ENSG}` — and prokn's entire gene-level relation set (reified source-attributed evidence via `rdf:subject`/`rdf:object` + `dcterms:source`, `HAS_MARKER_GENE`, `RO_0002206` expressed-in) hangs off that node. spoke-okn stores the same ENSG as an object of `spoke:ensembl` in the `http://identifiers.org/ensembl/{ENSG}` form, so the join is: strip spoke-okn's object to the bare ENSG, rebuild prokn's node IRI, bind it by type (`a up:Gene`).

Research question: Take **CFH** (complement factor H), a gene spoke-okn associates with disease. Pull prokn's evidence layer for it, the cell types it is flagged as a marker gene of (`HAS_MARKER_GENE`), and its tissue expression — all on the shared Ensembl id, without routing through wikidata.

Why the join is required: spoke-okn knows *which diseases CFH is associated with* but holds none of prokn's cell-type marker signatures, tissue-expression profile, or source-attributed evidence statements; prokn holds all of that but no disease-association layer of its own for this gene. And here the direct route is not merely convenient but *mandatory*: CFH is one of the 16 genes the wikidata HGNC→Entrez bridge cannot reach at all — Wikidata's item for Entrez 3075 (`Q14911975`) carries no `wdt:P354` (HGNC) statement, so the bridge dead-ends. Only the direct Ensembl join connects spoke-okn's CFH to prokn's.

---

🧠 **Assistant**

**CFH joins cleanly on the Ensembl node IRI, and prokn's payload lands on the disease that spoke-okn associates it with.** This is the crosswalk's sharpest case: the gene is *unreachable* through the wikidata bridge, so without the direct Ensembl route these two graphs have nothing to say to each other about it.

## The join, and what spoke-okn contributes

spoke-okn's gene node `.../gene/3075` carries `spoke:ensembl → ENSG00000000971`; rebuilding that as `https://www.ensembl.org/id/ENSG00000000971` binds directly to prokn's `up:Gene` node, labelled **CFH**. spoke-okn's disease-association layer for it:

| spoke-okn disease (ASSOCIATES_DaG) | spoke-okn gene node | prokn gene node (Ensembl) |
| --- | --- | --- |
| blindness | .../gene/3075 | ENSG00000000971 (CFH) |
| epilepsy | .../gene/3075 | ENSG00000000971 (CFH) |
| hypertension | .../gene/3075 | ENSG00000000971 (CFH) |
| liver disease | .../gene/3075 | ENSG00000000971 (CFH) |
| nervous system disease | .../gene/3075 | ENSG00000000971 (CFH) |

## What prokn adds: the evidence layer

prokn's reified statements about this gene node, grouped by the source that asserted them and the relation they assert — 486 statements in all, across 7 evidence sources:

| Evidence source | prokn relation | Statements |
| --- | --- | --- |
| DDKG_HGNCHPO | biolink:associated_with (phenotype) | 190 |
| DDKG_GTEXEXP | RO_0002206 (expressed in) | 89 |
| DDKG_MSIGDB | RO_0002431 (involved in / gene-set membership) | 78 |
| DDKG_LINCS | RO_0002213 (positively regulates) | 40 |
| DDKG_LINCS | RO_0002212 (negatively regulates) | 31 |
| DDKG_MSIGDB | **HAS_MARKER_GENE** | 23 |
| DDKG_CLINVAR | biolink:associated_with (variant–disease) | 16 |
| DDKG_MSIGDB | biolink:target_for | 13 |
| DDKG_MSIGDB | BCGO_0000177 | 4 |
| DDKG_HGNCUNIPROT | SIO_010078 (encodes protein) | 1 |
| DDKG_HMAZ | **HAS_MARKER_GENE_IN_KIDNEY** | 1 |

Every statement is source-attributed — GTEx for expression, MSigDB for cell-type signatures, LINCS for perturbational regulation, ClinVar for variant–disease evidence, HPO for phenotype.

## What prokn adds: the marker-gene role

**24 marker-gene assertions**, and they are not scattered noise — they concentrate exactly on the tissues spoke-okn's disease labels point at:

| prokn relation | Marker signature |
| --- | --- |
| HAS_MARKER_GENE | AIZARANI_LIVER_C11_HEPATOCYTES_1 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C14_HEPATOCYTES_2 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C17_HEPATOCYTES_3 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C21_STELLATE_CELLS_1 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C30_HEPATOCYTES_4 |
| HAS_MARKER_GENE | LAKE_ADULT_KIDNEY_C29_UNKNOWN_NOVEL_PT_**CFH_POS**_SUBPOPULATION_S2 |
| HAS_MARKER_GENE | CUI_DEVELOPING_HEART_C6_EPICARDIAL_CELL |
| HAS_MARKER_GENE | CUI_DEVELOPING_HEART_SMOOTH_MUSCLE_CELL |
| HAS_MARKER_GENE | CUI_DEVELOPING_HEART_VASCULAR_ENDOTHELIAL_CELL |
| HAS_MARKER_GENE | DESCARTES_FETAL_CEREBRUM_VASCULAR_ENDOTHELIAL_CELLS |
| HAS_MARKER_GENE | FAN_EMBRYONIC_CTX_BRAIN_ENDOTHELIAL_2 |
| HAS_MARKER_GENE | MANNO_MIDBRAIN_NEUROTYPES_HPERIC |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_ADVENTITIAL_FIBROBLAST_CELL |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_MYOFIBROBLAST_CELL |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_BASAL_CELL |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_LYMPHATIC_CELL |
| HAS_MARKER_GENE | HAY_BONE_MARROW_STROMAL |
| HAS_MARKER_GENE | MURARO_PANCREAS_DUCTAL_CELL |
| HAS_MARKER_GENE | RUBENSTEIN_SKELETAL_MUSCLE_FAP_CELLS |
| HAS_MARKER_GENE | GAO_LARGE_INTESTINE_ADULT_CJ_IMMUNE_CELLS |
| HAS_MARKER_GENE | GAO_STOMACH_24W_C4_PARIETAL_PROGENITOR |
| HAS_MARKER_GENE | FAN_OVARY_CL1_GPRC5A_TNFRS12A_HIGH_SELECTABLE_FOLLICLE_STROMAL_CELL |
| HAS_MARKER_GENE | FAN_OVARY_CL6_PUTATIVE_EARLY_ATRETIC_FOLLICLE_THECAL_CELL_2 |
| **HAS_MARKER_GENE_IN_KIDNEY** | **Epithelial cell of parietal layer of glomerular capsule** |

Five of the 23 MSigDB signatures are **liver** — four hepatocyte clusters plus stellate cells — which is the mechanistic counterpart of spoke-okn's *liver disease* association: the liver is where plasma complement factor H is made. Independently, prokn's kidney-specific relation flags CFH as a marker of the **parietal epithelial cell of the glomerular capsule**, and MSigDB flags a **CFH-positive proximal-tubule subpopulation** — a renal compartment spoke-okn's disease labels for this gene do not mention at all.

## What prokn adds: tissue expression

**44 tissues** on `RO_0002206` (GTEx-sourced), including *Right lobe of liver*, *Structure of cortex of kidney*, *Set of outer region of renal pyramids*, *Coronary artery*, *Ascending aorta structure*, *Tibial Arteries*, *Portion of venous blood*, *Spleen*, *Cerebellum*, *Hippocampus (Brain)*, *Substantia nigra structure*, *Amygdaloid structure*, *Cortex of frontal lobe*, and *Structure of left upper lobe of lung*. The liver + kidney-cortex + vasculature axis is the expression backbone of the marker-gene story; the brain-region set is the expression counterpart of spoke-okn's *nervous system disease* / *epilepsy* labels.

## Why it answers the question

One rewrite — spoke-okn's `identifiers.org/ensembl/ENSG00000000971` → prokn's `ensembl.org/id/ENSG00000000971` — turns a bare disease-association edge into a mechanistic dossier: **5 spoke-okn diseases, 486 source-attributed prokn statements across 7 evidence sources, 24 marker-gene assertions, 44 expression tissues**. spoke-okn says *CFH is associated with liver disease and blindness*; prokn says *CFH is a hepatocyte and stellate-cell marker, a glomerular parietal-epithelial marker, expressed in liver and kidney cortex, with ClinVar variant evidence and HPO phenotype links*. Neither graph holds the other's half.

And the two halves can only be joined *directly*. CFH is one of the 16 genes in the C16-only set: the wikidata bridge that C9 relies on has no HGNC statement on Wikidata's Entrez-3075 item, so the HGNC→Entrez hop returns nothing for this gene. This is the concrete payoff of the corrected crosswalk — under the old catalog, which listed only the wikidata-bridged route for this pair, **this dossier was not retrievable at all**.

## Literature validation (PubMed)

- **spoke-okn's *blindness* association — supported.** CFH is the canonical age-related macular degeneration risk gene, and AMD is a leading cause of blindness: PubMed returns **93** records for CFH + AMD + blindness (e.g. PMIDs 41604455, 41542493, 41278837, 41278702).
- **prokn's liver hepatocyte marker signatures — supported.** Hepatocyte synthesis of complement factor H is established: **15** records for complement factor H + liver synthesis + hepatocytes (e.g. PMIDs 37481826, 32849636, 27899485, 25805734). This corroborates *both* prokn's five liver signatures and spoke-okn's *liver disease* association.
- **prokn's kidney marker role — supported.** CFH dysfunction is central to C3 glomerulopathy and atypical hemolytic uremic syndrome, both glomerular diseases: **9** records for CFH mutation + C3 glomerulopathy + aHUS + kidney (e.g. PMIDs 40356067, 32553244, 30714990, 30595568). This independently supports prokn's `HAS_MARKER_GENE_IN_KIDNEY → epithelial cell of the parietal layer of the glomerular capsule` and the CFH-positive proximal-tubule signature — a disease axis spoke-okn does **not** annotate for this gene, and therefore a genuine cross-graph gain.
- **Not claimed:** spoke-okn's *hypertension* and *epilepsy* associations for CFH were not corroborated against the literature here, and no mechanistic claim is made for them. Note also that prokn's GTEx expression set contains no ocular tissue (GTEx does not sample retina), so the *blindness* association is supported by literature and by spoke-okn's own edge, not by prokn's expression profile.

**Maintainer caveat.** The C16 catalog entry describes prokn's reified layer as "INDRA `rdf:subject`/`rdf:object`". There is **no INDRA source anywhere in prokn** — an exhaustive `dcterms:source` scan of the graph returns 47 sources (DDKG_GTEXEXP, DDKG_MSIGDB, IMEx, UniProtKB, GO, iPTMnet, ChEMBL, CIViC, Reactome, DDKG_CLINVAR, …) and INDRA is not among them. The reification pattern the crosswalk describes is real and works exactly as documented; only the attribution of it to INDRA is wrong. The `example_questions` entry and the `verified_count_note` should say "reified, source-attributed evidence statements" rather than "INDRA evidence".

#### Query 1 — CFH: spoke-okn's disease associations, joined to prokn's gene node directly on the Ensembl id

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?spoke_disease ?spoke_gene_node ?prokn_gene_node ?prokn_label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g rdfs:label "CFH" ; spoke:ensembl ?e .
    ?d spoke:ASSOCIATES_DaG ?g ; rdfs:label ?spoke_disease .
  }
  BIND(?g AS ?spoke_gene_node)
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?prokn_gene_node)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?prokn_gene_node a up:Gene ; rdfs:label ?prokn_label .
  }
} ORDER BY ?spoke_disease
```

_5 row(s)_

| spoke_disease | spoke_gene_node | prokn_gene_node | prokn_label |
| --- | --- | --- | --- |
| blindness | http://www.ncbi.nlm.nih.gov/gene/3075 | https://www.ensembl.org/id/ENSG00000000971 | CFH |
| epilepsy | http://www.ncbi.nlm.nih.gov/gene/3075 | https://www.ensembl.org/id/ENSG00000000971 | CFH |
| hypertension | http://www.ncbi.nlm.nih.gov/gene/3075 | https://www.ensembl.org/id/ENSG00000000971 | CFH |
| liver disease | http://www.ncbi.nlm.nih.gov/gene/3075 | https://www.ensembl.org/id/ENSG00000000971 | CFH |
| nervous system disease | http://www.ncbi.nlm.nih.gov/gene/3075 | https://www.ensembl.org/id/ENSG00000000971 | CFH |

#### Query 2 — prokn's reified evidence layer for the joined CFH gene node, by asserting source and relation

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?evidence_source ?prokn_relation (COUNT(DISTINCT ?stmt) AS ?statements) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g rdfs:label "CFH" ; spoke:ensembl ?e . }
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    { ?stmt rdf:subject ?gene . } UNION { ?stmt rdf:object ?gene . }
    ?stmt dct:source ?evidence_source ; rdf:predicate ?prokn_relation .
  }
} GROUP BY ?evidence_source ?prokn_relation ORDER BY DESC(?statements)
```

_11 row(s)_

| evidence_source | prokn_relation | statements |
| --- | --- | --- |
| DDKG_HGNCHPO | https://biolink.github.io/biolink-model/associated_with | 190 |
| DDKG_GTEXEXP | http://purl.obolibrary.org/obo/RO_0002206 | 89 |
| DDKG_MSIGDB | http://purl.obolibrary.org/obo/RO_0002431 | 78 |
| DDKG_LINCS | http://purl.obolibrary.org/obo/RO_0002213 | 40 |
| DDKG_LINCS | http://purl.obolibrary.org/obo/RO_0002212 | 31 |
| DDKG_MSIGDB | https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE | 23 |
| DDKG_CLINVAR | https://biolink.github.io/biolink-model/associated_with | 16 |
| DDKG_MSIGDB | https://biolink.github.io/biolink-model/target_for | 13 |
| DDKG_MSIGDB | http://purl.obolibrary.org/obo/BCGO_0000177 | 4 |
| DDKG_HGNCUNIPROT | http://semanticscience.org/resource/SIO_010078 | 1 |
| DDKG_HMAZ | https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_KIDNEY | 1 |

#### Query 3 — The cell types and tissues prokn flags CFH as a marker gene of

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX prokn: <https://research.bioinformatics.udel.edu/ProKN/rdf/>
SELECT DISTINCT ?prokn_relation ?marker_signature WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g rdfs:label "CFH" ; spoke:ensembl ?e . }
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    { ?sig prokn:HAS_MARKER_GENE ?gene . BIND("HAS_MARKER_GENE" AS ?prokn_relation) }
    UNION
    { ?sig prokn:HAS_MARKER_GENE_IN_KIDNEY ?gene . BIND("HAS_MARKER_GENE_IN_KIDNEY" AS ?prokn_relation) }
    ?sig rdfs:label ?marker_signature .
  }
} ORDER BY ?prokn_relation ?marker_signature
```

_24 row(s)_

| prokn_relation | marker_signature |
| --- | --- |
| HAS_MARKER_GENE | AIZARANI_LIVER_C11_HEPATOCYTES_1 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C14_HEPATOCYTES_2 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C17_HEPATOCYTES_3 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C21_STELLATE_CELLS_1 |
| HAS_MARKER_GENE | AIZARANI_LIVER_C30_HEPATOCYTES_4 |
| HAS_MARKER_GENE | CUI_DEVELOPING_HEART_C6_EPICARDIAL_CELL |
| HAS_MARKER_GENE | CUI_DEVELOPING_HEART_SMOOTH_MUSCLE_CELL |
| HAS_MARKER_GENE | CUI_DEVELOPING_HEART_VASCULAR_ENDOTHELIAL_CELL |
| HAS_MARKER_GENE | DESCARTES_FETAL_CEREBRUM_VASCULAR_ENDOTHELIAL_CELLS |
| HAS_MARKER_GENE | FAN_EMBRYONIC_CTX_BRAIN_ENDOTHELIAL_2 |
| HAS_MARKER_GENE | FAN_OVARY_CL1_GPRC5A_TNFRS12A_HIGH_SELECTABLE_FOLLICLE_STROMAL_CELL |
| HAS_MARKER_GENE | FAN_OVARY_CL6_PUTATIVE_EARLY_ATRETIC_FOLLICLE_THECAL_CELL_2 |
| HAS_MARKER_GENE | GAO_LARGE_INTESTINE_ADULT_CJ_IMMUNE_CELLS |
| HAS_MARKER_GENE | GAO_STOMACH_24W_C4_PARIETAL_PROGENITOR |
| HAS_MARKER_GENE | HAY_BONE_MARROW_STROMAL |
| HAS_MARKER_GENE | LAKE_ADULT_KIDNEY_C29_UNKNOWN_NOVEL_PT_CFH_POS_SUBPOPULATION_S2 |
| HAS_MARKER_GENE | MANNO_MIDBRAIN_NEUROTYPES_HPERIC |
| HAS_MARKER_GENE | MURARO_PANCREAS_DUCTAL_CELL |
| HAS_MARKER_GENE | RUBENSTEIN_SKELETAL_MUSCLE_FAP_CELLS |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_ADVENTITIAL_FIBROBLAST_CELL |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_BASAL_CELL |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_LYMPHATIC_CELL |
| HAS_MARKER_GENE | TRAVAGLINI_LUNG_MYOFIBROBLAST_CELL |
| HAS_MARKER_GENE_IN_KIDNEY | Epithelial cell of parietal layer of glomerular capsule |

#### Query 4 — prokn's tissue expression (RO_0002206, GTEx-sourced) for the joined CFH gene node

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT DISTINCT ?tissue ?tissue_label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g rdfs:label "CFH" ; spoke:ensembl ?e . }
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?gene <http://purl.obolibrary.org/obo/RO_0002206> ?tissue .
    OPTIONAL { ?tissue rdfs:label ?tissue_label }
  }
} ORDER BY ?tissue_label
```

_44 row(s) — showing first 24_

| tissue | tissue_label |
| --- | --- |
| http://purl.obolibrary.org/obo/UBERON_0002369 | Adrenal Glands |
| http://purl.obolibrary.org/obo/UBERON_0001876 | Amygdaloid structure |
| http://purl.obolibrary.org/obo/UBERON_0006330 | anterior lingual gland |
| http://purl.obolibrary.org/obo/UBERON_0001496 | Ascending aorta structure |
| http://purl.obolibrary.org/obo/UBERON_0001150 | Body of pancreas |
| http://purl.obolibrary.org/obo/UBERON_0008367 | breast epithelium |
| http://purl.obolibrary.org/obo/UBERON_0002037 | Cerebellum |
| http://purl.obolibrary.org/obo/UBERON_0001621 | Coronary artery |
| http://purl.obolibrary.org/obo/UBERON_0001870 | Cortex of frontal lobe |
| http://purl.obolibrary.org/obo/UBERON_0000458 | Endocervix |
| http://purl.obolibrary.org/obo/UBERON_0006920 | Esophageal Squamous Epithelium |
| http://purl.obolibrary.org/obo/UBERON_0012249 | Exocervix |
| http://purl.obolibrary.org/obo/UBERON_0003889 | Fallopian Tubes |
| http://www.ebi.ac.uk/efo/EFO_0002009 | fibroblast derived cell line |
| http://purl.obolibrary.org/obo/UBERON_0001954 | Hippocampus (Brain) |
| http://purl.obolibrary.org/obo/UBERON_0001898 | Hypothalamic structure |
| http://purl.obolibrary.org/obo/UBERON_0004550 | Inferior esophageal sphincter structure |
| http://purl.obolibrary.org/obo/UBERON_0004648 | Lamina muscularis of esophageal mucous membrane |
| http://purl.org/sig/ont/fma/fma83030 | lymphoblast |
| http://purl.obolibrary.org/obo/UBERON_0006566 | Myocardium of left ventricle |
| http://purl.obolibrary.org/obo/UBERON_0000992 | Ovary |
| http://purl.obolibrary.org/obo/UBERON_0001211 | Peyer's patch |
| http://purl.obolibrary.org/obo/UBERON_0000007 | Pituitary Gland |
| http://purl.obolibrary.org/obo/UBERON_0013756 | Portion of venous blood |
| http://purl.obolibrary.org/obo/UBERON_0002367 | Prostate |
| http://purl.obolibrary.org/obo/UBERON_0006631 | Right auricular appendage |
| http://purl.obolibrary.org/obo/UBERON_0001114 | Right lobe of liver |
| http://purl.obolibrary.org/obo/UBERON_0001293 | Set of outer region of renal pyramids |
| http://purl.obolibrary.org/obo/UBERON_0001159 | Sigmoid Flexure |
| http://purl.obolibrary.org/obo/UBERON_0002106 | Spleen |
| http://purl.obolibrary.org/obo/UBERON_0000945 | Stomach |
| http://purl.obolibrary.org/obo/UBERON_0001225 | Structure of cortex of kidney |
| http://purl.obolibrary.org/obo/UBERON_0008952 | Structure of left upper lobe of lung |
| http://purl.obolibrary.org/obo/UBERON_0011907 | Structure of medial head of gastrocnemius muscle |
| http://purl.obolibrary.org/obo/UBERON_0001323 | Structure of tibial nerve |
| http://purl.obolibrary.org/obo/UBERON_0002190 | Subcutaneous Fat |
| http://purl.obolibrary.org/obo/UBERON_0002038 | Substantia nigra structure |
| http://purl.obolibrary.org/obo/UBERON_0000473 | Testis |
| http://purl.obolibrary.org/obo/UBERON_0002046 | Thyroid Gland |
| http://purl.obolibrary.org/obo/UBERON_0007610 | Tibial Arteries |
| http://purl.obolibrary.org/obo/UBERON_0001157 | Transverse colon |
| http://purl.obolibrary.org/obo/UBERON_0001255 | Urinary Bladder |
| http://purl.obolibrary.org/obo/UBERON_0000995 | Uterus |
| http://purl.obolibrary.org/obo/UBERON_0000996 | Vagina |

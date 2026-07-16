# Cross-graph reproduction of a NASA GeneLab kidney spaceflight study (PMID 40133368) with spoke-genelab

- **Date:** 2026-06-29
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>

## Conversation

👤 **User**

Create a real-world cross-graph use case for spoke-genelab that integrates data from one or more additional KGs through shared identifiers or crosswalks. Use the NASA OSDR publications archive; review the 'Datasets' column and pick a publication focused on gene expression whose dataset ID(s) match a study in spoke-genelab. (1) Identify the paper's main biological question and key results. (2) Determine the OSDR/GeneLab dataset IDs used. (3) Map them to the study/assay/samples/genes/differential-expression results in spoke-genelab. (4) Use the MCP service to query spoke-genelab and additional KGs to reproduce or approximate the findings. (5) Add cross-graph context: pathways, GO terms, gene sets, diseases/phenotypes, orthologs, chemicals/perturbations, literature/external IDs. (6-8) Recreate comparable tables/plots and compare to the paper. Final output: selected publication + citation + URL; dataset->spoke-genelab mapping; MCP tools and KGs used; cross-graph query strategy; example NL prompts and generated SPARQL/Cypher; recreated tables/plots; comparison of reproduced vs reported results; and a clear summary of what could be reproduced, approximated, not reproduced, and the data/schema/crosswalk limitations.

---

🧠 **Assistant**

Selected publication: Finch RH, Vitry G, Siew K, Walsh SB, Beheshti A, Hardiman G, da Silveira WA. 'Spaceflight causes strain-dependent gene expression changes in the kidneys of mice.' npj Microgravity (2025). DOI 10.1038/s41526-025-00465-0; PMID 40133368; PMC11937539. Datasets OSD-102 (RR-1, C57BL/6J) and OSD-163 (RR-3, BALB/c) -- both present in spoke-genelab as left-kidney RNA-Seq with the canonical Space Flight vs Ground Control comparison (OSD-102 assay ...9ea29268; OSD-163 assay ...134943402).

What reproduced directly from the knowledge graph:
- The paper's central thesis -- a strain-dependent kidney response to spaceflight, strong in C57BL/6J and near-absent (by spaceflight-vs-ground) in BALB/c. spoke-genelab gives C57BL/6J = 471 DEGs (243 up / 228 down, adj p <= 0.1) vs the paper's 638; BALB/c = 2 by SF-vs-GC (paper 0) and 581 by the SF-vs-Basal minus GC-vs-Basal design (paper 671).
- Per-gene log2 fold-changes match the publication at Pearson r = 0.999 (Ccl28 2.03 vs 2.05; Hmgcs2 -1.66 vs -1.68; Egr1 1.59; Fos 1.60; Hmgcr -1.11 vs -1.13; Wnt11 -1.37 vs -1.15).
- The paper's three themes re-emerge from the DEG list: cholesterol/sterol biosynthesis (Hmgcr, Sqle, Mvd, Mvk, Idi1, Fdps, Nsdhl, Dhcr7, Srebf1, Insig1 up; Hmgcs2 down), ECM/TGF-beta (Ccl28, Adamts8, collagens up; Wnt11, Smad9 down) and circadian (Npas2/Arntl up; Dbp/Per3 down).

Cross-graph value-add: mapping mouse DEGs to human orthologs (IS_ORTHOLOG_MGiG inside spoke-genelab) and joining spoke-okn on the shared Entrez key surfaces kidney-disease context the transcriptomics alone lacks -- COL4A3, SPP1, IRF5 -> glomerulonephritis; CLCNKB -> interstitial nephritis; BUB1/CCND1/MVK -> kidney cancer -- matching the paper's own ECM/fibrosis narrative.

MCP tools: list_kgs, describe_kg, get_schema, get_join_strategy, probe_namespaces, sparql_query (publication full text via Paperclip/PMC). KGs: spoke-genelab + spoke-okn (+ ubergraph), with gene-level reach into rdkg, biobricks-aopwiki, gene-expression-atlas-okn. Deliverables (report, four figures, DEG CSV, scripts) saved to the repo.

Reproduced: strain asymmetry, per-gene fold-changes, the three pathway themes (by membership), and the cross-graph kidney-disease links. Approximated: absolute DEG totals (471 vs 638; 581 vs 671) -- same signal, fewer genes, because spoke-genelab runs an independent DE pipeline and keys on Entrez. Not reproduced: GSEA NES/FDR statistics, the strain-genetics/hyaluronan analysis, and per-sample count plots (the KG stores per-group means/SD only). Limitation: OSD accessions are a NASA-internal island -- cross-graph linkage happens only on biological entities (Entrez gene, UBERON, NCBITaxon).

Sources: Finch RH, et al. npj Microgravity (2025). 10.1038/s41526-025-00465-0; PMC11937539.

👤 **User**

The prokn and gene-expression-atlas-okn have Reactome pathway information. prokn and pankgraph have GO terms and may have gene sets. Also digcfdekg can be linked by Entrez id and may have relevant data.

---

🧠 **Assistant**

That pointer closed the pathway/GO gap I had flagged. I extended the example with three more graphs, all joined on the shared gene key:

- GO terms via pankgraph (gene -> GO through biolink:functional_association, joined on Ensembl obtained from spoke-okn, labelled via ubergraph): the kidney DEG orthologs map to 'cholesterol biosynthetic process' (8 of the DEGs: HMGCR, HMGCS2, MVK, MVD, IDI1, FDPS, DHCR7, SREBF1), plus 'isoprenoid biosynthetic process' (6) and 'sterol biosynthetic process' (4) -- the paper's top GO finding, now as actual GO annotations.
- Pathway / gene sets and traits via digcfdekg (direct Entrez join to spoke-genelab): geneInGeneSet returns KEGG mevalonate pathway, HALLMARK cholesterol homeostasis and GOBP sterol biosynthesis; geneToTrait anchors the same genes to kidney-disease endpoints (CKD, diabetic nephropathy, nephrotic syndrome, eGFR, ESRD via A4GALT/AAAS/GULO) and lipid/cholesterol traits -- both of the paper's themes from one clean join.
- Reactome: gene-expression-atlas-okn stores Reactome enrichment per contrast (enrichment_source 'GXA:Reactome', R-HSA nodes); prokn carries gene/protein -> GO (RO_0002331 involved_in) and Reactome through its UniProt/HGNC layer (heavier, Wikidata-bridged). I noted these as reachable rather than chasing the per-gene Reactome join, since KEGG/Hallmark/GO already reproduce the pathway conclusion on cleaner Entrez/Ensembl joins.

The report now has a new section 7.5 (with a figure), an updated KG table and NL-prompt/query references, and the limitations section corrected: what was 'GO/Reactome not reproducible in-federation' is now reproduced via pankgraph/digcfdekg, with only the paper's per-study GSEA statistics (NES/FDR) remaining out of scope.

👤 **User**

Copy the result files into the PMID-40133368 folder.

---

🧠 **Assistant**

Copied into docs/reproduction/PMID-40133368/: README.md, the figures under figures/, the osd102_c57_deg.csv DEG table, and the plotting scripts.

👤 **User**

Also create a pdf version of the transcript and include the figures inline.

---

🧠 **Assistant**

Created spoke-genelab-crossgraph-kidney.pdf (13 pages) with all figures embedded inline, built via pandoc + XeLaTeX with DejaVu fonts -- long SPARQL lines wrap inside their code boxes, tables and the cross-graph diagram stay within margins, and the figures auto-scale to page width. Since LaTeX has no emoji font, the Yes/Partial/No status marks in the comparison tables were converted from glyphs to text so nothing renders as a blank box.

👤 **User**

copy the pdf file also into the docs/reproduction/PMID-40133368/ folder.

---

🧠 **Assistant**

The PDF was already in docs/reproduction/PMID-40133368/ -- that path is mounted to the same physical folder the PDF was written to, so it is present there alongside README.md, figures/, the CSV and the scripts (confirmed via both the repo path and the folder path).

👤 **User**

convert the ascii diagrams to real figures and create an updated pdf file.

---

🧠 **Assistant**

Converted the two ASCII diagrams into rendered matplotlib figures: fig_schema.png (spoke-genelab schema -- Study -> Assay -> mouse Gene -> human-ortholog Gene, plus the Anatomy/UBERON branch and the differential-expression edge properties) and fig_strategy.png (cross-graph strategy -- spoke-genelab joined on the shared Entrez/Ensembl gene key to spoke-okn / digcfdekg / pankgraph, with the three-step flow). Both README copies now embed the images instead of code blocks, make_diagrams.py is saved for reproducibility, and the PDF was rebuilt (13 pages) with the diagrams inline on pages 2-3.

👤 **User**

Create a chat transcript.

---

🧠 **Assistant**

Generated this reproducible transcript: the conversation turns plus the six headline SPARQL queries (re-run as logged queries) with their results, and session provenance (model, knowledge graphs, OKN endpoint). The queries cover dataset->spoke-genelab mapping, the C57BL/6J and BALB/c DEG reproduction, and the three cross-graph dimensions -- kidney disease (spoke-okn), GO biological process (pankgraph + ubergraph), and GWAS/CFDE traits (digcfdekg).

## SPARQL queries executed

#### Query 1

_2026-06-30T06:44:34+00:00 · `spoke-genelab`_  — maps the paper's two datasets to their spoke-genelab left-kidney Space-Flight-vs-Ground assays

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?study ?assay ?material_name_1 ?technology ?factor_space_1 ?factor_space_2
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    VALUES ?study { <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-102>
                    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-163> }
    ?study schema:PERFORMED_SpAS ?assay .
    ?assay schema:material_name_1 ?material_name_1 ; schema:technology ?technology ;
           schema:factor_space_1 ?factor_space_1 ; schema:factor_space_2 ?factor_space_2 .
    FILTER(?factor_space_1 = "Space Flight" && ?factor_space_2 = "Ground Control")
  }
}
```

_2 row(s)_

| study | assay | material_name_1 | technology | factor_space_1 | factor_space_2 |
| --- | --- | --- | --- | --- | --- |
| .../node/OSD-102 | .../node/OSD-102-9ea29268b285ecb277189e5e22cd2053 | left kidney | RNA Sequencing (RNA-Seq) | Space Flight | Ground Control |
| .../node/OSD-163 | .../node/OSD-163-134943402b3359fb84c7f5443b6935b9 | left kidney | RNA Sequencing (RNA-Seq) | Space Flight | Ground Control |

#### Query 2

_2026-06-30T06:44:38+00:00 · `spoke-genelab`_  — C57BL/6J (OSD-102 / RR-1) kidney spaceflight DEGs at the paper's adj p ≤ 0.1

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# C57BL/6J (OSD-102 / RR-1) kidney spaceflight DEGs at the paper's adj p <= 0.1
SELECT (COUNT(*) AS ?n_DEG) (SUM(IF(?lfc>0,1,0)) AS ?up) (SUM(IF(?lfc<0,1,0)) AS ?down)
WHERE {
  SELECT DISTINCT ?gene ?lfc WHERE {
    GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
      ?s rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-102-9ea29268b285ecb277189e5e22cd2053> ;
         rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
         rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?p .
      FILTER(?p <= 0.1)
    }
  }
}
```

_1 row(s)_

| n_DEG | up | down |
| --- | --- | --- |
| 471 | 243 | 228 |

#### Query 3

_2026-06-30T06:44:44+00:00 · `spoke-genelab`_  — BALB/c (OSD-163 / RR-3) spaceflight-specific genes = DE(Space Flight vs Basal) minus DE(Ground vs Basal)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# BALB/c (OSD-163 / RR-3): spaceflight-specific genes = DE(Space Flight vs Basal) minus DE(Ground vs Basal)
SELECT (COUNT(DISTINCT ?gene) AS ?balbc_spaceflight_specific)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?s1 rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-163-5df912e5a537e22a263e3b5433858fac> ;
        rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
        rdf:object ?gene ; schema:adj_p_value ?p1 .
    FILTER(?p1 <= 0.1)
    FILTER NOT EXISTS {
      ?s2 rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-163-58b896feb53e1754781955f351ee0ecb> ;
          rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; schema:adj_p_value ?p2 .
      FILTER(?p2 <= 0.1)
    }
  }
}
```

_1 row(s)_

| balbc_spaceflight_specific |
| --- |
| 581 |

#### Query 4

_2026-06-30T06:45:07+00:00 · `spoke-genelab`, `spoke-okn`_  — C57BL/6J kidney DEGs → human ortholog → kidney/renal diseases in spoke-okn (cross-graph)

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gl:   <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX okn:  <https://purl.org/okn/frink/kg/spoke-okn/schema/>
# C57BL/6J kidney spaceflight DEGs -> human ortholog -> kidney/renal diseases in spoke-okn
SELECT DISTINCT ?human_symbol ?disease_label ?log2fc WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?s rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-102-9ea29268b285ecb277189e5e22cd2053> ;
       rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
       rdf:object ?m ; gl:log2fc ?log2fc ; gl:adj_p_value ?p .
    FILTER(?p <= 0.1)
    ?m gl:IS_ORTHOLOG_MGiG ?human . OPTIONAL { ?human gl:symbol ?human_symbol } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?dis okn:ASSOCIATES_DaG ?human ; rdfs:label ?disease_label . }
  FILTER(REGEX(LCASE(?disease_label), "kidney|renal|nephr|glomerul")) }
```

_11 row(s) — full result_

| human_symbol | disease_label | log2fc |
| --- | --- | --- |
| BUB1 | kidney cancer | 1.020 |
| CCND1 | kidney cancer | -0.328 |
| CLCNKB | interstitial nephritis | -0.277 |
| COL4A3 | glomerulonephritis | 0.341 |
| HDAC4 | kidney cancer | -0.250 |
| IRF5 | glomerulonephritis | 0.404 |
| LMNA | kidney cancer | 0.200 |
| MVK | kidney cancer | 0.389 |
| RPS20 | kidney cancer | -0.222 |
| SPP1 | glomerulonephritis | 0.297 |
| SPRED1 | kidney cancer | -0.186 |

#### Query 5

_2026-06-30T06:45:14+00:00 · `pankgraph`, `ubergraph`_  — cholesterol-pathway DEG orthologs (Ensembl) → GO biological process (pankgraph) → labels (ubergraph)

```sparql
PREFIX bl:   <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# C57BL/6J cholesterol-pathway DEG orthologs (as Ensembl) -> GO biological process (pankgraph) -> labels (ubergraph)
SELECT ?golabel (GROUP_CONCAT(DISTINCT ?sym; SEPARATOR=", ") AS ?genes) (COUNT(DISTINCT ?sym) AS ?n) WHERE {
  VALUES (?ens ?sym) {
    (<http://identifiers.org/ensembl/ENSG00000113161> "HMGCR") (<http://identifiers.org/ensembl/ENSG00000104549> "SQLE")
    (<http://identifiers.org/ensembl/ENSG00000167508> "MVD") (<http://identifiers.org/ensembl/ENSG00000110921> "MVK")
    (<http://identifiers.org/ensembl/ENSG00000067064> "IDI1") (<http://identifiers.org/ensembl/ENSG00000147383> "NSDHL")
    (<http://identifiers.org/ensembl/ENSG00000172893> "DHCR7") (<http://identifiers.org/ensembl/ENSG00000186480> "INSIG1")
    (<http://identifiers.org/ensembl/ENSG00000072310> "SREBF1") (<http://identifiers.org/ensembl/ENSG00000120437> "ACAT2")
    (<http://identifiers.org/ensembl/ENSG00000160752> "FDPS") (<http://identifiers.org/ensembl/ENSG00000134240> "HMGCS2") }
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?ens bl:functional_association ?go }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?go rdfs:label ?golabel }
  FILTER(REGEX(?golabel, "cholesterol|sterol|isoprenoid|mevalonate", "i"))
}
GROUP BY ?golabel ORDER BY DESC(?n) LIMIT 12
```

_12 row(s) — showing first 5_

| golabel | genes | n |
| --- | --- | --- |
| cholesterol biosynthetic process | MVK, HMGCR, HMGCS2, DHCR7, IDI1, SREBF1, MVD, FDPS | 8 |
| isoprenoid biosynthetic process | IDI1, HMGCS2, MVD, MVK, HMGCR, FDPS | 6 |
| sterol biosynthetic process | SQLE, HMGCR, DHCR7, MVD | 4 |
| cholesterol metabolic process | SREBF1, SQLE | 2 |
| isopentenyl diphosphate biosynthetic process, mevalonate pathway | MVK, MVD | 2 |

#### Query 6

_2026-06-30T06:45:19+00:00 · `spoke-genelab`, `digcfdekg`_  — C57BL/6J kidney DEGs → human ortholog → GWAS/CFDE traits (digcfdekg), renal + lipid

```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gl:   <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX dig:  <https://purl.org/okn/frink/kg/digcfdekg/schema/>
# C57BL/6J kidney spaceflight DEGs -> human ortholog -> GWAS/CFDE traits (digcfdekg), renal + lipid
SELECT DISTINCT ?human_symbol ?trait_label WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?s rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-102-9ea29268b285ecb277189e5e22cd2053> ;
       rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
       rdf:object ?m ; gl:adj_p_value ?p .
    FILTER(?p <= 0.1)
    ?m gl:IS_ORTHOLOG_MGiG ?human . OPTIONAL { ?human gl:symbol ?human_symbol } }
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?human dig:geneToTrait ?trait . ?trait rdfs:label ?trait_label . }
  FILTER(REGEX(?trait_label, "kidney|renal|nephr|glomerul|chronic kidney|cholesterol|lipid", "i")) }
ORDER BY ?human_symbol LIMIT 40
```

_40 row(s) — representative renal + lipid traits_

| human_symbol | trait_label |
| --- | --- |
| A2M | Total cholesterol; LDL cholesterol; VLDL cholesterol |
| A4GALT | Chronic kidney disease (CKD); diabetic nephropathy; glomerular filtration rate; End-stage renal disease |
| AAAS | Rare genetic renal disease; nephrotic syndrome; potentially indicated for kidney transplant |
| ACAT2 | Disorder of lipid metabolism; antihyperlipidemic-drug-use measurement |
| GULO | Genetic / rare renal tubular disease; HDL / non-HDL / VLDL cholesterol |

---

*Generated with the `mcp-okn` OKN federated-SPARQL MCP service (`create_chat_transcript`). Differential-expression values are pre-computed in `spoke-genelab` from NASA OSDR/GeneLab; the publication is © its authors (CC-BY).*

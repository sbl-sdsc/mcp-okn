# Reproducibility Appendix — SANS Ocular Spaceflight-Omics Study

- **Date:** 2026-07-04 · **Model:** claude-opus-4-8
- **Endpoint:** OKN federated SPARQL (`https://apps.okn.us/federation/sparql`)
- **KG versions (pinned via `get_kg_version`):** spoke-genelab **v0.0.2** (2026-03-13) · spoke-okn **v0.0.6** · rdkg **v0.0.1** · digcfdekg **v0.0.1** · prokn **v0.0.5** · biobricks-aopwiki **v0.0.4** · gene-expression-atlas-okn **v0.0.3** · ubergraph **v0.0.2**

A machine-generated transcript of all queries logged after the analysis-phase log scope (14 cross-KG / specificity / fluid-shift / disease / drug / trait queries, verbatim with sampled results) was produced with `create_chat_transcript`. This appendix additionally records the **cohort-construction queries** (run in the first analysis phase) so the full pipeline is reproducible end-to-end.

## Rules, thresholds and joins used

- **Direction rule:** keep an assay only when `factor_space_1 = "Space Flight"` AND `factor_space_2 = "Ground Control"` (group 1 = spaceflight ⇒ `log2fc > 0` = up in flight). Reversed / Basal / Vivarium / SF-vs-SF contrasts dropped.
- **Comparability rule:** pool/compare assays only within identical `(material_id_1, material_id_2, cleaned factors_1, cleaned factors_2)` after stripping condition labels and anchored group codes `^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$`. OSD-758/759 gravity levels (`uG`, `0.33G`, `0.66G`, `1G by centrifugation` vs `1G on Earth`) are separate groups; `uG` is the primary microgravity contrast.
- **Ortholog collapsing:** mouse→human via `IS_ORTHOLOG_MGiG`; keep max |log2fc| for 1:many/many:1 with ambiguity flag. Mean-rule sensitivity: 14 genes differ, 0 sign flips.
- **Thresholds:** significance `adj_p ≤ 0.05` (primary); effect size `|log2fc| ≥ 1` reported alongside. `|log2fc| ≥ 10` flagged as near-zero-count artifact and down-weighted.
- **Cross-KG joins (integration only on biological entities; OSD accessions are a federation island):** spoke-okn / digcfdekg on Entrez node-IRI (**direct**, verified 16,326 / 19,747); rdkg on Entrez via `identifiers.org/ncbigene` normalization (**direct**, verified 9,034); aopwiki on Entrez `skos:exactMatch` (direct, 1,472, key-event path sparse); prokn via Wikidata Entrez→HGNC (**bridged, lower confidence — avoided**; digcfdekg used for trait/function instead).

## Cohort-construction queries (phase 1)

**Q-A1 — Comparability signature (Step A) for the eye cohort** (returns one row per valid SF-vs-GC eye assay with its `(material_id_1, material_id_2, sig1, sig2)` key):

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?study ?assay ?material_id_1 ?material_id_2
       (GROUP_CONCAT(DISTINCT ?f1clean; SEPARATOR="|") AS ?sig1)
       (GROUP_CONCAT(DISTINCT ?f2clean; SEPARATOR="|") AS ?sig2)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?study gl:PERFORMED_SpAS ?assay .
    ?assay gl:INVESTIGATED_ASiA ?anatomy ;
           schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
           schema:material_id_1 ?material_id_1 ; schema:material_id_2 ?material_id_2 .
    VALUES ?anatomy { <http://purl.obolibrary.org/obo/UBERON_0000966> <http://purl.obolibrary.org/obo/UBERON_0004904>
                      <http://purl.obolibrary.org/obo/UBERON_0000970> <http://purl.obolibrary.org/obo/UBERON_0004548> }
    OPTIONAL { ?assay schema:factors_1 ?f1 .
      FILTER(LCASE(STR(?f1)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f1), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) BIND(?f1 AS ?f1clean) }
    OPTIONAL { ?assay schema:factors_2 ?f2 .
      FILTER(LCASE(STR(?f2)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f2), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) BIND(?f2 AS ?f2clean) }
  }
} GROUP BY ?study ?assay ?material_id_1 ?material_id_2 ORDER BY ?material_id_1 ?study ?assay
```
Result: 13 valid SF-vs-GC eye assays — OSD-758/759 each split into uG / 0.33G / 0.66G / 1G-by-centrifugation (sig2 = "1G on Earth"); OSD-100/162/194/255/397 empty sig.

**Q-A2 — Cohort DE + ortholog counts per study** (rebuilds "Model DE genes" and "Human orthologs"; reproduced anchors exactly):

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?study (COUNT(DISTINCT ?gene) AS ?deGenes) (COUNT(DISTINCT ?h) AS ?humanOrthologs)
WHERE {
  VALUES ?assay { <…13 valid SF-vs-GC eye assay IRIs…> }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?study gl:PERFORMED_SpAS ?assay .
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene .
    OPTIONAL { ?gene gl:IS_ORTHOLOG_MGiG ?h }
  }
} GROUP BY ?study
```
Result (rebuilt = anchor): OSD-100 360/373 · OSD-162 14/12 · OSD-194 3/1 · OSD-255 478/489 · OSD-397 208/214 · OSD-758 1461/1366 · OSD-759 4333/4021.

**Q-A3 — Per-assay significant DE projected to human ortholog (Step B, run once per primary assay)** — subquery form to avoid the reified+ortholog internal-sort timeout:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mEntrez ?symbol ?hEntrez ?humanSymbol ?log2fc ?adj_p_value WHERE {
  { SELECT ?mgene ?log2fc ?adj_p_value WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject <…ASSAY_IRI…> ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ;
              schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value . FILTER(?adj_p_value <= 0.05) } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    OPTIONAL { ?mgene schema:symbol ?symbol }
    OPTIONAL { ?mgene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } BIND(REPLACE(STR(?h),'^.*/gene/','') AS ?hEntrez) } }
  BIND(REPLACE(STR(?mgene),'^.*/gene/','') AS ?mEntrez)
}
```
Run for the 7 primary assays (retina OSD-758-uG/255/397/194, optic-nerve OSD-759-uG, left-eye OSD-100, eye OSD-162), the 3 non-irradiated OSD-203 HLU assays, and the OSD-758 1G-by-centrifugation control.

## Analysis-phase queries (phase 2 — auto-logged)

Captured verbatim by `create_chat_transcript` (14 queries): the non-eye tissue landscape; eye-selectivity (per-gene non-eye tissue recurrence); OSD-203 HLU loading-effect enumeration and DE; OSD-758 1G-centrifugation DE; spoke-okn disease associations, compound→gene regulation, and TREATS_CtD for glaucoma/hypertension; rdkg neuro-ocular phenotype queries (per-candidate and the 208-gene universe); and digcfdekg gene→trait enrichment.

## Downstream computation (Python / pandas / scipy)

Ortholog collapsing (max|log2fc| + mean-rule sensitivity), per-tissue and cross-study consensus, eye-selectivity categorisation, fluid-shift overlap + Spearman/Pearson, 1G-centrifugation overlap, neuro-ocular over-representation (hypergeometric: 20 observed vs 12.8 expected, 1.56×, p = 0.032), and the integrated priority score. All intermediate CSVs and scripts are retained in the working directory.

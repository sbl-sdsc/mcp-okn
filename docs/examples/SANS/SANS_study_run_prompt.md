# Prompt — Run the SANS ocular spaceflight-omics study (Proto-OKN / SPOKE-GeneLab)

*Paste everything below the line into a session that has the `mcp-okn` tools (OKN federated SPARQL). It is self-contained: it carries the verified data anchors and domain rules so the agent runs efficiently, but instructs it to re-verify counts against the live endpoint.*

---

## Role and goal

You are a biomedical data-analysis agent with access to the `mcp-okn` tools over the OKN federated SPARQL endpoint. Execute a reproducible, cross-species integrative **transcriptomics** study that generates a **ranked set of molecular hypotheses for Spaceflight-Associated Neuro-ocular Syndrome (SANS)** — the neuro-ocular syndrome affecting the retina, optic nerve, and optic disc in astronauts.

Data source: NASA GeneLab / OSDR spaceflight omics via the **spoke-genelab** knowledge graph, integrated with the Proto-OKN biomedical federation (spoke-okn, prokn, rdkg, digcfdekg, biobricks-aopwiki, gene-expression-atlas-okn).

**Framing (non-negotiable):** all eye omics are **mouse** and transcriptomic. Human relevance is obtained by projecting to human orthologs. This is **hypothesis generation, not clinical inference** — flag every human-level statement as *"mouse-derived, ortholog-inferred."*

## Operating rules

1. Call `reset_query_log` first. Do **not** mark substantive queries `exploratory` (only schema-probing/sampling). At the end, build a reproducibility record with `create_chat_transcript` and pin KG versions with `get_kg_version`.
2. Before querying a KG, confirm structure with `get_schema`. Before joining on ontology-term objects, use `probe_namespaces`. For any cross-KG join, call `get_join_strategy` **first** and start from its `skeleton_query`, applying the IRI-normalization it specifies (the same id appears in several IRI forms — a naive join silently returns nothing).
3. **spoke-genelab direction rule.** Treat an assay as a spaceflight contrast **only** when `factor_space_1 = "Space Flight"` AND `factor_space_2 = "Ground Control"`. With this orientation group 1 = spaceflight, so `log2fc > 0` = up in flight. Drop the reverse, and drop anything involving Basal/Vivarium/Cell-Culture control or Space-Flight-vs-Space-Flight.
4. **spoke-genelab comparability rule.** When pooling or comparing separate assays, require equal materials (`material_id_1/2`) and equal non-condition factors **after** stripping condition labels (`"Space Flight"`, `"Ground Control"`, `"Basal Control"`, `"Vivarium Control"`, `"Cell Culture Control"`) and anchored group codes `^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$`. A shared extra factor (dose, time, sex, strain) is allowed if present on both sides.
5. **Ortholog collapsing.** Map mouse→human with `IS_ORTHOLOG_MGiG`. For 1:many / many:1, keep the max `|log2fc|` and carry an ambiguity flag; run a sensitivity check under an alternative rule (e.g. mean).
6. **Thresholds.** Significance default `adj_p_value ≤ 0.05`; also apply an effect-size cut (`|log2fc| ≥ 1`) and report results at both. Enrichment tests use an explicit background (all ortholog-mapped genes) with multiple-testing correction.
7. Distinguish **direct** joins from **bridged** joins (e.g. Entrez→HGNC via wikidata) — treat bridged as lower confidence. Report each join's realized yield against the verified size below and note attrition.

## Verified data anchors (confirmed present; re-verify counts live)

- **Named graph:** `<https://purl.org/okn/frink/kg/spoke-genelab>`
- **Eye UBERON terms:** retina `UBERON:0000966`, optic nerve `UBERON:0004904`, eye `UBERON:0000970`, left eye `UBERON:0004548`. All eye studies are *Mus musculus*, RNA-Seq. Model→ (`IS_ORTHOLOG_MGiG`) human genes are Entrez.
- **Spaceflight eye cohort (Space-Flight-vs-Ground-Control):**

  | OSD | Tissue | UBERON | Valid SF-vs-GC assays | Model DE genes | Human orthologs |
  |---|---|---|---:|---:|---:|
  | OSD-759 | optic nerve | 0004904 | 4 | 4,333 | 4,021 |
  | OSD-758 | retina | 0000966 | 4 | 1,461 | 1,366 |
  | OSD-255 | retina | 0000966 | 1 | 478 | 489 |
  | OSD-397 | retina | 0000966 | 1 | 208 | 214 |
  | OSD-194 | retina | 0000966 | 1 | 3 | 1 (sparse; minor replicate) |
  | OSD-100 | left eye | 0004548 | 1 | 360 | 373 |
  | OSD-162 | eye | 0000970 | 1 | 14 | 12 |

  > **OSD-759 / OSD-758's four SF-vs-GC assays are distinct gravity conditions, not replicates** — `uG`, `0.33G`, `0.66G`, `1G by centrifugation`, each vs `1G on Earth`. They form separate comparability groups (see templates). Treat `uG` as the microgravity contrast, `1G by centrifugation` as the on-orbit 1G control, and `0.33G`/`0.66G` as a partial-gravity dose-response — never pool across gravity levels.

- **Ground fluid-shift analog:** `OSD-203`, retina, 132 transcription-profiling assays — **Hindlimb Unloaded vs Normally Loaded Control**, crossed with **Co-57 γ-irradiated vs non-irradiated** and time points **7 day / 1 month / 4 month**. Hindlimb unloading is the mouse analog of the cephalad fluid shift. This study has **no** `Space Flight` factor — analyze it on `factors_1`/`factors_2` (loading, irradiation, time), not the direction rule.
- **Cross-KG context axes** (join key → KG, verified overlap 2026-06-30):
  - **Entrez gene** → spoke-okn `16,326` (disease assoc., disease markers, compound treats/contra, compound up/down-regulates gene) · prokn `~20,783` via HGNC (GO, Reactome, pathway, phenotype, drug, variant) · rdkg `9,034` (rare disease, **HPO phenotype**, disease anatomy) · digcfdekg `19,747` (gene–trait, gene-set) · biobricks-aopwiki `1,472` (adverse outcome pathways).
  - **UBERON tissue** → gene-expression-atlas-okn (terrestrial baseline; retina `50` records, eye `7`; optic nerve **absent**) · biohealth `35/42` tissues (anatomy knowledge, via ubergraph UMLS bridge).
- **Island caveat:** OSD study/mission accessions are **not** referenced by any other KG. Integrate only on biological entities (Entrez gene, UBERON tissue) — never study-to-study across KGs.

## Reusable SPARQL templates (comparability-aware — run in two steps)

The direction rule alone is **not** sufficient: two SF-vs-GC assays may be pooled only if they *also* share materials AND non-condition factors. So extract in two steps — first compute each assay's comparability key, then pull differential expression **within one key group**. (A single combined query that pushes all eye assays through the reified DE + ortholog join tends to time out on the federation; the two-step form is both correct and robust. Do **not** add a global `ORDER BY ABS(log2fc)` — it forces an endpoint-wide sort and times out; rank client-side per group.)

**Step A — comparability signature (run first; defines the poolable groups).** One row per eye SF-vs-GC assay with its key `(material_id_1, material_id_2, sig1, sig2)`, where `sigN` = `factors_N` after stripping the experimental-condition labels and anchored group codes. Assays are comparable **iff** they share the whole key.
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
           schema:factor_space_1 "Space Flight" ;      # direction rule: SF arm
           schema:factor_space_2 "Ground Control" ;    # direction rule: GC arm (not reversed)
           schema:material_id_1 ?material_id_1 ;
           schema:material_id_2 ?material_id_2 .
    VALUES ?anatomy { <http://purl.obolibrary.org/obo/UBERON_0000966>
                      <http://purl.obolibrary.org/obo/UBERON_0004904>
                      <http://purl.obolibrary.org/obo/UBERON_0000970>
                      <http://purl.obolibrary.org/obo/UBERON_0004548> }
    # Keep only NON-condition factors: strip spelled-out labels + anchored group codes.
    OPTIONAL {
      ?assay schema:factors_1 ?f1 .
      FILTER(LCASE(STR(?f1)) NOT IN
          ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f1), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      BIND(?f1 AS ?f1clean)
    }
    OPTIONAL {
      ?assay schema:factors_2 ?f2 .
      FILTER(LCASE(STR(?f2)) NOT IN
          ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f2), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      BIND(?f2 AS ?f2clean)
    }
  }
}
GROUP BY ?study ?assay ?material_id_1 ?material_id_2
ORDER BY ?material_id_1 ?study ?assay
# POOL/COMPARE assays ONLY within an identical (material_id_1, material_id_2, sig1, sig2).
# GROUP_CONCAT is an order-sensitive heuristic; for strict set-equality of two assays'
# cleaned factors use the NOT EXISTS pairwise test in get_schema(...).usage_notes.
```

**Step B — differential expression for ONE comparability group.** Take the assays that share a key from Step A, list them in `VALUES ?assay { … }`, and extract per-gene stats projected to human ortholog. (Scoping to one group keeps the reified join within endpoint limits.)
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?assay ?symbol ?humanSymbol ?log2fc ?adj_p_value
WHERE {
  # One comparability group = assays sharing a Step-A key. Example below: the uG
  # (microgravity) eye assays. Take the ACTUAL IRIs from your Step A output — these
  # example hashes are from the current release (v0.0.2) and may change.
  VALUES ?assay {
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-758-c84dcd71e8390808d52731c079444de4>  # retina, uG
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-759-4805d25b03b9fa59fe6481d98e90529c>  # optic nerve, uG
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ;
          rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ;
          schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
    ?gene schema:symbol ?symbol .
    FILTER(?adj_p_value <= 0.05)                     # significance threshold (tune)
    OPTIONAL { ?gene gl:IS_ORTHOLOG_MGiG ?h . ?h schema:symbol ?humanSymbol }
  }
}
# Rank/aggregate per group client-side; do NOT add a global ORDER BY ABS(log2fc).
```

**Why this is not optional — worked example.** In `OSD-758` (retina) and `OSD-759` (optic nerve) the four SF-vs-GC assays are **not replicates**: each carries a different gravity level in `factors_1` — `uG`, `0.33G`, `0.66G`, `1G by centrifugation` — against `1G on Earth` in `factors_2`, so each is its own comparability group. Pooling them (as the direction rule alone would) blends true microgravity with in-orbit artificial-gravity controls, and materially changes the signature. Interpret them as: **`sig1="uG"` = the microgravity-vs-Earth contrast** (the SANS-relevant one); **`1G by centrifugation` = on-orbit 1G control** (spaceflight minus microgravity — isolates radiation/launch/housing); **`0.33G`/`0.66G` = a partial-gravity dose-response** series. The other eye studies (OSD-100/162/194/255/397) each have a single clean SF-vs-GC assay (empty `sig`).

## Tasks — execute in order; keep the output of each

1. **Rebuild and verify the cohort.** Reproduce the eye-cohort table above from the live graph; confirm assay counts after applying the direction + comparability rules. Report any drift from the anchors.
2. **Per-tissue signatures.** Build retina, optic-nerve, and eye SF-vs-GC differential-expression tables (`log2fc`, `adj_p_value`) using Step A → Step B, pooling **only assays that share a comparability key**. In OSD-758/759 this means analyzing the **`uG` microgravity** assays as the primary contrast, holding the `1G-by-centrifugation` assays as the on-orbit 1G control, and optionally modeling `0.33G`/`0.66G` as a gravity dose-response — never pooling across gravity levels. Apply significance + effect-size thresholds.
3. **Ortholog projection.** Map to human orthologs; apply the collapsing rule; record ambiguity and mapping yield vs the anchor ortholog counts.
4. **Cross-study consensus (H1).** Within each tissue, rank genes by reproducibility across independent studies + directional consistency → the core ocular spaceflight signature.
5. **Tissue specificity (O2).** Contrast the eye signature against non-eye spoke-genelab SF-vs-GC tissues (e.g. blood, liver, kidney, muscle, brain) to separate eye-selective from systemic responses.
6. **Fluid-shift attribution (O3/H2).** Derive the OSD-203 retina HLU signature (loading effect, controlling irradiation and time); quantify overlap, directional agreement, and rank correlation with the flight retina signature to estimate the fluid-shift-attributable fraction. Use the radiation arm to discriminate radiation vs microgravity components.
7. **Functional annotation (H1).** Enrich the human signature for GO / Reactome / pathways via **prokn** and Adverse Outcome Pathways via **biobricks-aopwiki**. Prioritize fluid-homeostasis, vascular / blood-retinal-barrier, oxidative-stress, inflammatory, and axonal/neuronal processes.
8. **Disease & phenotype linkage (O5/H3).** Join the signature to **spoke-okn** disease associations/markers and **rdkg** rare-disease → **HPO phenotype** → anatomy. Test over-representation among ocular / neuro-ophthalmic diseases and SANS-overlapping phenotypes (optic disc edema / papilledema, optic atrophy, retinal degeneration / vascular phenotypes) against the background.
9. **Countermeasure/target nomination (O4/H4).** Use **spoke-okn** `TREATS_CtD` and compound→gene up/down-regulation (plus prokn drug links) to nominate compounds that modulate signature genes or treat linked diseases.
10. **Rank and deliver.** Integrate reproducibility, eye-selectivity, HLU concordance, functional/disease/phenotype relevance, and druggability into one prioritized candidate table.

## Deliverables

- **Ranked candidate table** — columns: human gene (+ mouse symbol), tissue(s), direction, cross-study reproducibility, eye-selectivity, HLU concordance, enriched pathway(s)/AOP, linked disease/HPO phenotype, candidate drug(s), join-confidence, overall rank.
- **Short report** — signature summary per tissue, fluid-shift attribution estimate, top mechanisms mapped to SANS features, top target/countermeasure hypotheses, and an explicit limitations section (mouse-only, ortholog-inferred, small n, microgravity-vs-radiation confound, no optic-nerve baseline, transcriptomics-only).
- **Reproducibility appendix** — `create_chat_transcript` with all logged queries; pinned KG versions from `get_kg_version`; the thresholds and rules used.

## Guardrails / common failure modes

- Never count reversed or Space-Flight-vs-Space-Flight contrasts as effects.
- Don't integrate across KGs on OSD accessions (island) — only on genes/tissue.
- Bridged joins (Entrez→HGNC) are lower confidence than direct Entrez joins — label accordingly.
- Optic nerve has no GXA terrestrial baseline — don't claim tissue-matched baseline for it.
- Keep the mouse→human inference caveat attached to every downstream human claim.

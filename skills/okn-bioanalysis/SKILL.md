---
name: okn-bioanalysis
description: >-
  Methodology for biomedical knowledge-graph analysis and cross-KG hypothesis generation over the
  OKN federated SPARQL endpoint via the mcp-okn tools. Works across the federation's bio graphs
  (spoke-okn, prokn, rdkg, digcfdekg, gene-expression-atlas-okn, the biobricks chemical/tox graphs,
  biobricks-aopwiki, biomarkerkg, ncipidkg, oard-kg, pankgraph, spoke-genelab, ubergraph),
  integrating on shared identifiers — gene, protein, disease (MONDO/DOID), phenotype (HP),
  GO/Reactome, chemical/drug — and can LINK bio entities to place-based data (exposure, facilities,
  social determinants) via geography (county FIPS / ZIP / S2 cells). Use whenever a task involves
  genes, proteins, diseases, phenotypes, pathways, chemicals, drugs, exposures, differential
  expression, enrichment, ortholog projection, or mapping these across KGs or onto locations.
  Triggers: "analyze these genes", "map genes to diseases / drugs", "GO / Reactome enrichment",
  "link a disease or chemical to exposure / geography", or naming a bio KG.
---

# OKN bio-analysis

A repeatable methodology for turning the OKN federation's **biomedical** knowledge graphs into a
ranked, defensible set of hypotheses — and, where the question calls for it, **linking bio entities
to place-based data** (environmental exposure, facilities, social determinants). Output is
*hypothesis generation*; carry the appropriate caveat — species / ortholog-inferred for
model-organism sources, observational-not-causal for association data — into every downstream claim.

This is **domain-general within biomedicine**: the federation carries genes, proteins, diseases,
phenotypes, pathways, chemicals, drugs, cell types and tissues across a dozen bio KGs, plus
geospatial / environmental / social layers you can bridge into. There is **no single "primary"
source** — pick the KGs the question needs and **integrate on shared entity identifiers** (never on
study / dataset accessions).

**Two references (progressive disclosure):**
- **`references/mcp-okn-workflow.md`** — how to let the mcp-okn **server tools** drive discovery and
  joins (`list_crosswalks` / `get_join_strategy` / `find_context_sources` / `find_crosswalks` /
  `get_valid_contrasts`), the identifier types you join on, the **bio↔geography bridge**, and the
  endpoint quirks that shape your code. **Read this first.**
- **`references/enrichment-methods.md`** — over-representation (GO, Reactome, disease / trait /
  phenotype / chemical sets) done right: explicit background, hypergeometric + FDR, interpretation.

**Two scripts:**
- **`scripts/enrichment.py`** — hypergeometric over-representation + Benjamini–Hochberg FDR against
  an explicit background; reuse for any category → gene / entity set.
- **`scripts/collapse_orthologs.py`** — *optional*: when a source is a **model organism** (e.g.
  spoke-genelab mouse), collapse to human orthologs (max |effect| + ambiguity flag + mean-rule).

## Operating rules (non-negotiable — details in the workflow reference)

1. `reset_query_log` at the start; `create_chat_transcript` + `get_kg_version` at the end (pin
   versions + dates). Don't mark substantive queries `exploratory`.
2. Before querying a KG: `get_schema`. For cross-KG joins use the **precomputed crosswalk catalog**
   first — `list_crosswalks` (the whole verified join map in one call) and `get_join_strategy(a, b)`
   (one pair's recipe; respect `known_non_join`); `find_context_sources(want, join_key)` for the
   reverse ("who annotates this entity?"). If a KG *seems* to lack an id you need, run
   `find_crosswalks(kg)` before giving up — the id is usually just encoded non-obviously (a buried
   mapping predicate, the node's own IRI, or an arbitrary domain predicate). Before joining on
   ontology-term objects: `probe_namespaces` — pick the richest id scheme, don't guess.
3. **Integrate only on shared entities** — gene, protein, disease, phenotype, chemical, tissue, cell
   type, taxon, or **geography**; get each join recipe from `get_join_strategy` / `list_crosswalks`.
   Study / dataset / mission accessions (e.g. OSD / GLDS) are a federation island — never join across
   KGs on them.
4. **Endpoint reliability:** no global `ORDER BY` (endpoint-wide sort → timeout) — rank client-side;
   pull one contrast / one big pattern at a time; large results auto-save to a file — process with
   pandas / jq, don't read them inline.

## Integrating across KGs — ask the join tools, don't plan from a table

**Get the join recipe from the tools, not from memory.** `list_crosswalks` returns every verified
cross-KG join the federation ships (grouped by domain + shared id); `get_join_strategy(a, b)` returns
a specific pair's recipe — the exact predicates, the IRI-normalization rewrite, a verified count, and
a runnable `skeleton_query` to copy; `find_context_sources(want, join_key)` finds *which* KGs can
annotate an entity. These are **live and versioned — treat them as the source of truth** (raw keys
drift across KG releases; don't hard-code them).

The federation joins **mostly on shared identifiers** (Entrez, UniProt, MONDO, …), but **some joins
are exact name / label matches** — a gene **symbol** on `rdfs:label`, a SNOMED / UMLS **concept
name**, an organism **label** where a KG has no taxon id. Label matches are more fragile (exact,
case-sensitive); `get_join_strategy` tells you which key a given pair actually uses. The recurring
join keys — so you know what to ask the tools for:

| Entity | Join key(s) |
|---|---|
| Gene | Entrez / Ensembl (+ HGNC symbol) |
| Protein | UniProt |
| Disease | MONDO / DOID |
| Phenotype | HP (HPO) |
| Pathway / function | Reactome `R-HSA`, GO |
| Chemical / drug | CHEBI / CAS / PubChem CID / MeSH / DrugBank |
| Cell type / tissue | CL / UBERON |
| Social determinants (SDoH) | UMLS concept |
| Geography *(to reach place-based data)* | S2 L13 cell · county / state FIPS · ZIP |

To reach **place-based data**, join on a geographic key (S2 / FIPS / ZIP). Several bio-carrying KGs
also carry geography — e.g. spoke-okn (gene / disease / chemical + geo / SDoH / environmental),
biohealth (disease + SDoH), sawgraph (chemical + environmental) — so ask `find_context_sources` /
`get_join_strategy` which bridge fits your entity rather than assuming one.

## Analysis menu (run the ones the question needs)

1. **Frame + scope.** Identify the entity type(s) and target KGs; `find_context_sources` to see who
   supplies the context you want and on which key.
2. **Retrieve the entity set.** Pull the genes / proteins / diseases / chemicals of interest (a
   curated set, a disease's genes, a pathway's members, an exposure's targets) as raw rows.
3. **Cross-KG annotation.** Add context by joining on shared IDs — get each recipe from
   `get_join_strategy`, and `find_context_sources` to list *all* suppliers of an annotation (don't
   privilege one KG). Typical annotations (with example suppliers): disease↔gene, gene↔trait
   (digcfdekg), gene / protein↔pathway & GO (prokn, ncipidkg), chemical↔gene / adverse-outcome
   (biobricks tox + aopwiki), disease↔phenotype (rdkg / oard-kg, HPO), gene↔drug & disease↔drug
   (rdkg `treats`).
4. **Differential expression / omics (optional).** Where a source has it: spoke-genelab
   (model-organism DE, reified) or gene-expression-atlas baselines. Apply that source's selection
   rules; threshold adj_p ≤ 0.05 and |log2FC| ≥ 1. See the workflow appendix for spoke-genelab.
5. **Cross-species projection (optional).** If the source is a model organism, project to human
   orthologs and collapse with `collapse_orthologs.py`; carry the *ortholog-inferred* caveat.
6. **Functional enrichment.** GO / Reactome / disease / trait / chemical-set over-representation with
   `enrichment.py` (explicit background, hypergeometric + BH FDR). See enrichment-methods.
7. **Disease / phenotype / trait linkage.** Test the entity set for over-representation of disease /
   phenotype / trait genes; distinguish a **broad** (GWAS) set (null by construction) from a
   **curated** (Mendelian) set (the discriminating test).
8. **Drug / target / exposure linkage.**
   - **Known & candidate treatments for a target (therapeutic hypotheses).** For each known or
     top-ranked target, find drugs / compounds that act on it: on a **protein (UniProt)** target,
     **prokn** links approved / investigational **drugs** and **probe compounds** (measured
     bioactivity) to the protein; and chain **target → its diseases → drugs that treat them** for a
     **repurposing** angle (disease↔gene, then a drug→disease layer — **rdkg `treats`** is the clean
     curated source; **spoke-okn** also carries DrugBank drugs + a `TREATS_CtD` drug→disease layer,
     though sparser). Map every hit back onto the target; `find_context_sources(want=["drug"],
     join_key=…)` confirms the suppliers. spoke-okn can also tie a drug to **place / SDoH** (step 9).
   - **Label the evidence layer honestly:** approved therapeutic > investigational > medicinal-
     chemistry probe (potential, unvalidated) > toxicogenomic perturbation — e.g. **spoke-okn's
     compound→gene layer is a toxicogenomic perturbation, not a treatment**, so check what a
     compound→gene predicate means.
   - **Exposure / toxicology (environmental questions):** chemical↔gene tox screens (biobricks tox)
     and adverse outcome pathways (aopwiki) — the harmful-exposure direction, distinct from therapy.
9. **Place-based linkage (bio ↔ geography).** When the question is spatial, get the bio entity onto a
   **geographic key** (county FIPS / ZIP / S2) via whichever KG carries both your entity and geography
   (use `find_context_sources` / `get_join_strategy` to pick it — e.g. spoke-okn for a gene / disease,
   sawgraph for a chemical exposure), then join the spatial hub: environmental measurements (sawgraph,
   hydrology), facilities (fiokg), social services (dreamkg / ruralkg), neighborhood / justice
   (nikg / scales), soil / flood (sockg / ufokn). This turns a gene / disease / chemical result into
   an exposure- or place-aware map.
10. **Ranking & tiering.** Integrate the evidence axes (recurrence, effect size, disease / phenotype
    support, **druggability — a known or candidate drug acts on it**, curated role, specificity,
    number of corroborating KGs) into one score + A / B / C tiers.
11. **Literature comparison (optional).** PubMed + Paperclip: supported / novel / contradicted;
    verify central claims against full text.

## Statistical rigor

- Over-representation uses an **explicit** background (all entities annotated in the target KG,
  restricted to real ids of the right scheme) — never an implicit "all genes / all of the genome".
- Hypergeometric test + **Benjamini–Hochberg FDR**; report fold = observed / expected, k / K, and FDR.
- A **broad, permissive** set (e.g. a GWAS set covering ~15 % of the genome) will look null even for
  a real signal — expected, not a negative result. A **small, curated** set is the discriminating
  test. Report both and interpret accordingly.
- Enrichment is **descriptive, not causal.** Verify counts live (re-run; expect zero drift), and keep
  the appropriate caveat (species / ortholog for model-organism data; observational for associations)
  attached to every claim.

## Common failure modes

- Joining across KGs on study / dataset accessions (island) → integrate on entity IDs / geography.
- Enrichment against an implicit / all-genome background → inflated significance.
- Reaching place-based data by name instead of a geographic key → join on FIPS / ZIP / S2 (find the
  bridge KG with `find_context_sources` / `get_join_strategy`).
- A single combined query pushing a big reified pattern + OPTIONAL joins → timeout; go one piece at a
  time, no global ORDER BY.

---
name: okn-bioanalysis
description: >-
  Methodology for biomedical knowledge-graph analysis and cross-KG hypotheses over the
  OKN federated SPARQL endpoint via the mcp-okn tools. Works across the federation's bio graphs
  (spoke-okn, prokn, rdkg, digcfdekg, gene-expression-atlas-okn, biobricks-aopwiki, biomarkerkg,
  ncipidkg, oard-kg, pankgraph, spoke-genelab, ubergraph),
  integrating on shared identifiers — gene, protein, disease (MONDO/DOID), phenotype (HP),
  taxon (NCBITaxon), GO/Reactome, chemical/drug — and can LINK bio entities to place-based data (exposure, facilities,
  social determinants) via geography (FIPS / ZIP / S2). Use whenever a task involves
  genes, proteins, diseases, phenotypes, organisms / taxa, pathways, chemicals, drugs, exposures, differential
  expression, enrichment, ortholog projection, or mapping these across KGs or onto locations.
  Triggers: "analyze these genes", "map genes / proteins / diseases to drugs / phenotypes",
  "GO / Reactome enrichment", "link a disease or chemical to exposure / geography", or naming a bio KG.
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

**Three references (progressive disclosure):**
- **`references/mcp-okn-workflow.md`** — how to let the mcp-okn **server tools** drive discovery and
  joins (`list_crosswalks` / `get_join_strategy` / `find_context_sources` / `find_crosswalks` /
  `get_valid_contrasts`), the identifier types you join on, the **bio↔geography bridge**, and the
  endpoint quirks that shape your code. **Read this first.**
- **`references/enrichment-methods.md`** — over-representation (GO, Reactome, disease / trait /
  phenotype / chemical sets) done right: explicit background, hypergeometric + FDR, interpretation.
- **`references/mechanistic-map.md`** — *when the question is "map the biology of X":* how to build the
  **anchor → module → gene → drug mechanistic map** (the synthesis network figure) honestly.

**Three scripts:**
- **`scripts/enrichment.py`** — hypergeometric over-representation + Benjamini–Hochberg FDR against
  an explicit background; reuse for any category → gene / entity set.
- **`scripts/collapse_orthologs.py`** — *optional*: when a source is a **model organism** (e.g.
  spoke-genelab mouse), collapse to human orthologs (max |effect| + ambiguity flag + mean-rule).
- **`scripts/mechanistic_map.py`** — *optional*: render the radial anchor → module → gene → drug
  mechanistic map from `modules={label:[genes]}` + `drugs={label:[drugs]}` (see the reference).

## Preflight — optional literature connectors (PubMed + Paperclip)

The **literature comparison** (workflow step 13; report §8 *Comparison with prior work*) needs two MCP
connectors — **PubMed** (`https://pubmed.mcp.claude.com/mcp`) and **Paperclip**
(`https://paperclip.gxl.ai/mcp`). They are **user-managed configuration — a skill cannot enable or
install them.** Check for them at the **START of a run**, not at step 13 — otherwise the gap only
surfaces after the whole analysis is done and there's no time left to turn them on.

- **Detect.** Look in your available tools for names containing `pubmed` and `paperclip` (the server
  prefix varies by host). Both present → literature comparison is on; proceed normally.
- **If either is missing → surface it once, up front; never silently skip §8 / §13.** Name the missing
  connector, show how to enable it, and **ask the user** whether to **(a) pause** while they enable it
  and reconnect, or **(b) proceed** and mark the literature comparison **"skipped — `<connector>` not
  enabled"** — an explicit declared skip, exactly like an un-run enrichment family (step 6); a silent
  omission reads as "covered everything." **Never fabricate citations** to paper over the gap.
- **How to enable (hand these to the user — you cannot do it for them, and a newly added server is not
  live until reconnect):**
  - **claude.ai:** Settings → Connectors → add a custom connector for each missing URL above, then retry.
  - **Claude Code:** `claude mcp add --transport http pubmed https://pubmed.mcp.claude.com/mcp` and
    `claude mcp add --transport http paperclip https://paperclip.gxl.ai/mcp`, then reconnect (`/mcp`)
    or restart the session so the tools load.

## Operating rules (non-negotiable — details in the workflow reference)

1. `reset_query_log` at the start; `create_reproducibility_record` + `get_kg_version` at the end (pin
   versions + dates). `create_reproducibility_record` emits the lean deliverable — header + the
   verbatim supporting queries + row counts — which fits inline and saves directly (use
   `create_chat_transcript` only when you also need the conversation prose + result tables). **If it
   comes back as a stub (log too large to return inline), that is NOT a stopping point:** you know how
   many queries there are, so re-call with `supporting=[1, 5, 9, …]` (bare 1-based indices from
   `get_query_log`) to curate to the findings-supporting queries, or batch them — never leave the
   transcript missing. **A frequent cause of the stub/spill is the per-query mermaid diagrams** (each
   duplicates its SPARQL and they are 25–50%+ of the bytes): pass **`include_query_diagrams=False`**
   for a lean return, then **re-add** the diagrams as a postprocessing step (do BOTH halves — generating
   lean and not re-adding silently drops them). Use report-style's one-command front door
   **`scripts/readd_query_diagrams.py <transcript.md>`**: in a report session (where the
   `sparql-to-mermaid` package isn't importable) it emits a work-list of the un-diagrammed queries —
   generate each with the **`sparql_to_mermaid` TOOL** on the verbatim logged query, save
   `[{sparql, mermaid}, …]` as `diagrams.json`, then re-run with `--diagrams diagrams.json --max-chars
   4000` (see report-style for the full recipe). **Completeness gate — the transcript is not delivered
   until `readd_query_diagrams.py --check <transcript.md>` prints `PASS`** (every ```sparql block has a
   diagram); `--check` verifies without modifying and needs no package, so a FAIL is your tripwire that
   the re-add was skipped — treat it as blocking. The re-add applies only when you still want them in
   the final file; if the user asks for **no** diagrams, pass the flag and skip re-add. Don't mark
   substantive queries `exploratory` — least of all the query that establishes a cross-KG bridge; that
   one is the point of the analysis and MUST be logged.
2. Before querying a KG: `get_schema`. For cross-KG joins use the **precomputed crosswalk catalog**
   first — `list_crosswalks` (the whole verified join map in one call) and `get_join_strategy(a, b)`
   (one pair's recipe; respect `known_non_join`); `find_context_sources(want, join_key)` for the
   reverse ("who annotates this entity?"). **Reconcile with what these tools RETURN — don't just call
   them.** `find_context_sources` is a capability index, not a single-answer lookup: for each `want`,
   enumerate EVERY supplier it names and state why each was used or dropped (coverage, id scheme,
   redundancy). Using one and ignoring the rest complies with "call the tools" while defeating their
   purpose — a dropped supplier needs a reason, exactly like a skipped enrichment family (step 6). If a KG *seems* to lack an id you need, run
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
cross-KG join the federation ships; `get_join_strategy(a, b)` returns a pair's recipe — exact
predicates, IRI-normalization rewrite, a verified count, and a runnable `skeleton_query` to copy;
`find_context_sources(want, join_key)` finds *which* KGs annotate an entity. Treat them as the source
of truth — raw keys drift across releases, so don't hard-code them.

**Establish the join by RUNNING the `skeleton_query`, not by looking it up.** Copy it and extend it
with your payload. Do NOT decompose the join into exploratory lookups, read an id (e.g. a MONDO IRI)
off one, and paste it in as a constant — that hard-codes the very bridge the cross-KG claim depends on
and leaves it out of the transcript. A bridge-graph equivalence (e.g. `ubergraph` DOID→MONDO) must
come from a **logged** query.

The federation joins mostly on shared identifiers, but **some joins are exact name / label matches** (a
gene symbol on `rdfs:label`, a SNOMED / UMLS concept name, an organism label) — more fragile, and
`get_join_strategy` tells you which key a pair uses. The recurring join keys per entity, the
label-match cases, and the bio↔geography bridges are tabulated in **`references/mcp-okn-workflow.md`**
("What to integrate on" + "Bio ↔ place-based data") — ask the tools for the actual recipe.

## Analysis menu (run the ones the question needs)

1. **Frame + scope.** Identify the entity type(s) and target KGs; `find_context_sources` to see who
   supplies the context you want and on which key.
2. **Retrieve the entity set.** Pull the genes / proteins / diseases / chemicals of interest (a
   curated set, a disease's genes, a pathway's members, an exposure's targets) as raw rows.
3. **Cross-KG annotation.** Add context by joining on shared IDs — get each recipe from
   `get_join_strategy`, and `find_context_sources` to list *all* suppliers of an annotation (don't
   privilege one KG). Typical annotations (with example suppliers): disease↔gene;
   **gene↔trait / gene-set — `digcfdekg`** (GWAS-style trait associations; the broad-set supplier for
   enrichment in step 9 — easy to miss, so check it explicitly); gene / protein↔pathway & GO (prokn,
   ncipidkg), chemical↔gene / adverse-outcome
   (biobricks tox + aopwiki), disease / gene / protein↔phenotype (HP — see step 7), gene↔drug &
   disease↔drug (rdkg `treats`), disease / concept↔SDoH (`biohealth` is the UMLS-keyed SDoH hub;
   `dreamkg` social-service audiences and `phaseskg` healthy-aging / loneliness / social-isolation
   constructs **label-bridge** into it — fragile, `list_crosswalks` cluster SS/BH).
4. **Differential expression / omics (optional).** Where a source has it: spoke-genelab
   (model-organism DE, reified) or gene-expression-atlas baselines. Apply that source's selection
   rules; threshold adj_p ≤ 0.05 and |log2FC| ≥ 1. See the workflow appendix for spoke-genelab.
5. **Cross-species projection (optional).** If the source is a model organism, project to human
   orthologs and collapse with `collapse_orthologs.py`; carry the *ortholog-inferred* caveat.
6. **Functional enrichment.** Over-representation with `enrichment.py` (explicit background,
   hypergeometric + BH FDR). **GO and Reactome are two SEPARATE families — run BOTH; doing GO does not
   cover Reactome** (see the two standalone prokn recipes in the workflow reference). Add disease /
   trait / chemical-set enrichment where the question calls for it. **Declare, in the report, which
   enrichment families you RAN and which you deliberately SKIPPED, each with a one-line reason** — a
   silently omitted family is a bug, not a choice; if you'd have to write "Reactome: skipped — no
   reason", you should have run it. See enrichment-methods.
7. **Map entities to phenotypes (HP).** Phenotype = **HP**; route by entity — **disease→HP** richest
   via `oard-kg`, **gene→HP** has **no direct edge** (go gene→disease→HP), **protein→HP** only `prokn` —
   with **MONDO** the disease hub (DOID / EFO / OMIM / Orphanet / UMLS bridge via ubergraph). **`oard-kg`
   is reified — the HP term sits on `biolink:subject` OR `biolink:object`, so UNION both or you silently
   drop half.** These are observational, not causal. Full 5-supplier routing + recipes:
   **`references/mcp-okn-workflow.md`** "Mapping to phenotypes"; `find_context_sources(want=
   ["phenotype"], …)` lists every supplier.
8. **Map / align organisms (taxon).** Taxon = **NCBITaxon**; use the **`taxon_overlap(kg_a, kg_b)`**
   tool (returns exact-id + clade-membership skeletons + a verified overlap). **Exact-id match badly
   understates real overlap** (coarse genus vs fine strain) — always **clade-expand** with ubergraph
   `rdfs:subClassOf*` (e.g. spoke-genelab's 46 microbiome taxa reach spoke-okn as **2 by exact-id but
   33,313 by clade expansion**). **Distinct from ortholog projection (step 5)** — here you map the
   *organisms themselves*, not genes, and the result is taxonomic containment, not identity. 8-KG hub +
   per-pair recipes: **`references/mcp-okn-workflow.md`** "Mapping / aligning organisms".
9. **Disease / phenotype / trait linkage.** Test the entity set for over-representation of disease /
   phenotype / trait genes (see enrichment-methods, *Disease / trait / phenotype gene-set*). Pair each
   set type with its supplier so the choice is forced, not left to notice: **broad** (GWAS / polygenic)
   sets — **`digcfdekg`** `geneToTrait` / gene_set, PIGEAN — are null by construction; **curated**
   (rare / Mendelian) sets — **`rdkg`** disease→gene — are the discriminating test. Run both and name
   which supplier fed each; `find_context_sources(want=["trait","disease"], join_key="gene")` lists
   all suppliers to reconcile against (rule 2).
10. **Drug / target / exposure linkage.**
    - **Known & candidate treatments for a target (therapeutic hypotheses).** For each known or
      top-ranked target, find drugs / compounds that act on it: on a **protein (UniProt)** or **gene**
      (Ensembl; Entrez / HGNC symbol via a bridge) target, **prokn** links approved / investigational
      **drugs** and **probe compounds** (measured bioactivity) to the target; and chain
      **target → its diseases → drugs that treat them** for a
      **repurposing** angle (disease↔gene, then a drug→disease layer — **rdkg `treats`** is the clean
      curated source; **spoke-okn** also carries DrugBank drugs + a `TREATS_CtD` drug→disease layer,
      though sparser). Map every hit back onto the target; `find_context_sources(want=["drug"],
      join_key=…)` confirms the suppliers. spoke-okn can also tie a drug to **place / SDoH** (step 11).
    - **Label the evidence layer honestly:** approved therapeutic > investigational > medicinal-
      chemistry probe (potential, unvalidated) > toxicogenomic perturbation — e.g. **spoke-okn's
      compound→gene layer is a toxicogenomic perturbation, not a treatment**, so check what a
      compound→gene predicate means. The payload label is the fastest evidence cue: a **`drug`**
      payload is a DrugBank therapeutic (approved / investigational); a **`chemical`** payload is a
      CAS / CHEBI / PubChem *substance* — a med-chem probe or tox-screen chemical, i.e. a lower rung.
    - **Exposure / toxicology (environmental questions):** chemical↔gene tox screens (biobricks tox)
      and adverse outcome pathways (aopwiki) — the harmful-exposure direction, distinct from therapy.
11. **Place-based linkage (bio ↔ geography).** When the question is spatial, get the bio entity onto a
    **geographic key** (county FIPS / ZIP / S2) — never a name — via whichever KG carries both your
    entity and geography (pick it with `find_context_sources` / `get_join_strategy` — e.g. spoke-okn for
    a gene / disease, sawgraph for a chemical), then join the spatial hub (environmental, facilities,
    social services, neighborhood / justice, soil / flood). For **climate / Earth-observation** context,
    a place chains spoke-okn → climatemodelskg → nasa-gesdisc-kg (indirect, non-bio provenance). Bridges,
    spatial hubs + the climate chain: **`references/mcp-okn-workflow.md`** "Bio ↔ place-based data".
12. **Ranking & tiering.** Integrate the evidence axes (recurrence, effect size, disease / phenotype
    support, **druggability — a known or candidate drug acts on it**, curated role, specificity,
    number of corroborating KGs) into one score + A / B / C tiers.
13. **Literature comparison (optional — gated on the Preflight).** PubMed + Paperclip: supported /
    novel / contradicted; verify central claims against full text. If the preflight found a connector
    missing and the user chose to proceed, state the comparison was **skipped — `<connector>` not
    enabled** rather than dropping it silently.
14. **Mechanistic map (synthesis — when the question is "map the biology of X").** When the analysis
    yields a tiered gene/protein core (step 12) that groups into a few mechanistic themes (enrichment,
    step 6, or curated pathway membership) plus a drug/target layer (step 10), synthesize them into a
    **radial anchor → module → gene → drug map** — the payoff figure that shows the mechanism at a
    glance (T2D example: `docs/examples/Diabetes`, report §7). Render it with
    `scripts/mechanistic_map.py`; **`references/mechanistic-map.md`** has the structure and the honesty
    rules (every node was actually retrieved; modules are a declared synthesis; label the drug evidence
    layer; carry the standing caveats). Skip it for a purely geospatial or module-less result.

## Statistical rigor

- Over-representation uses an **explicit** background (all entities annotated in the target KG, right
  id scheme) — never an implicit "all genes / whole genome". Hypergeometric + **Benjamini–Hochberg
  FDR**; report fold = observed / expected, k / K, and FDR.
- A **broad, permissive** set (e.g. a GWAS set covering ~15% of the genome) looks null even for a real
  signal — expected, not a negative; a **small, curated** set is the discriminating test. Report both.
- Enrichment is **descriptive, not causal.** Verify counts live (expect zero drift) and carry the
  right caveat (species / ortholog for model-organism data; observational for associations).
- Full method — backgrounds, disease / trait gene-set enrichment, interpretation:
  **`references/enrichment-methods.md`**.

## Common failure modes

- Joining across KGs on study / dataset accessions (island) → integrate on entity IDs / geography.
- Enrichment against an implicit / all-genome background → inflated significance.
- Doing GO enrichment and silently skipping Reactome (or half of any compound deliverable) → they are
  separate families; run both and declare run-vs-skipped with reasons. A missing analysis has no
  loud tripwire (unlike an absurd result), so the report must make the omission explicit.
- Using only the KGs with prominent write-ups here and missing one named in a parenthetical (e.g.
  `digcfdekg`) → that is pattern-matching on this doc's layout, not reading the capability index.
  Reconcile against what `find_context_sources` RETURNS: list every supplier per `want`, use-or-drop
  each with a reason.
- Reaching place-based data by name instead of a geographic key → join on FIPS / ZIP / S2 (find the
  bridge KG with `find_context_sources` / `get_join_strategy`).
- A single combined query pushing a big reified pattern + OPTIONAL joins → timeout; go one piece at a
  time, no global ORDER BY.

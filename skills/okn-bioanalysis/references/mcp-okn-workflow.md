# mcp-okn workflow (analysis-level) — let the server tools drive discovery

The `mcp-okn` server already encodes the querying mechanics you'd otherwise memorise: the tool
**order** (its server instructions), the **live, versioned join recipes** (`list_crosswalks` /
`get_join_strategy`), each KG's **schema and query-time rules** (`get_schema`, incl. `usage_notes`),
namespace discovery (`probe_namespaces`), domain vetting (`get_valid_contrasts`), and endpoint
behaviour. **Call those tools — don't hard-code their answers here**: recipes drift across KG versions,
so a static copy goes stale. This reference covers only what the tools *don't* decide for you — which
analyses to run, what to integrate on, and how to interpret.

## Need → tool (call these; treat their output as the source of truth)

- **What KGs exist / what's in one** → `list_kgs`, `describe_kg`, `get_schema` (`get_schema` also
  returns `usage_notes` with any query-time domain rules — e.g. spoke-genelab's contrast rules).
- **How two KGs join** → `list_crosswalks` (the whole verified map in one call) →
  `get_join_strategy(a, b)` (a pair's recipe + a runnable `skeleton_query` to copy; respect
  `known_non_join`). **Do not hard-code join keys.**
- **A KG *seems* to lack an id** → `find_crosswalks(kg)` before giving up: it profiles the three
  places an id hides — mapping predicates (`seeAlso` / `sameAs` / SKOS `*Match` / `hasDbXref`), the
  node's **own IRI**, or an arbitrary domain predicate. Never conclude "lacks id" from `get_schema`
  alone (`sample=N` on huge KGs).
- **Who annotates an entity** → `find_context_sources(want, join_key)`.
- **Which id scheme populates a predicate** → `probe_namespaces` (MONDO vs DOID, Entrez vs Ensembl,
  CHEBI vs CAS…). Pick the richest; don't infer from the name.
- **Clean model-organism contrasts** (spoke-genelab) → `get_valid_contrasts`.
- **Logging / versions / transcript** → `reset_query_log` (start); `get_kg_version` +
  `create_chat_transcript` (end).

Dedicated bridge graphs the tools route through: **`ubergraph`** (ontology `skos:exactMatch` +
`subClassOf*` closure) and **`identifier-mappings` / `wikidata`** (Wikidata ↔ external-id, e.g.
HGNC ↔ Entrez behind prokn).

## What to integrate on (identifier types — get the recipe from the tools)

The federation joins **mostly on shared identifiers** (Entrez, UniProt, MONDO, …), but **some joins
are exact name / label matches** — a gene **symbol** (`rdfs:label`), a SNOMED / UMLS **concept
name**, an organism **label** where a KG has no taxon id; these are more fragile (exact,
case-sensitive). Use `list_crosswalks` / `get_join_strategy` / `find_context_sources` to get the
actual join (predicates, IRI normalization, verified count, `skeleton_query`) and which KGs supply it
— **don't plan or hard-code from this list**; it just names the recurring join keys so you know what
to ask the tools for.

| Entity | Join key(s) |
|---|---|
| Gene | Entrez / Ensembl (+ HGNC symbol) |
| Protein | UniProt |
| Disease | MONDO / DOID (bridged via ubergraph `skos:exactMatch`) |
| Phenotype | HP (HPO) |
| Pathway / function | Reactome `R-HSA`, GO |
| Chemical / drug | CHEBI / CAS / PubChem CID / MeSH / DrugBank |
| Cell type / tissue | CL / UBERON |
| Taxon / organism | NCBITaxon (ubergraph `subClassOf*` clade closure; some KGs organism-label only) |
| Social determinants (SDoH) | UMLS concept |
| Geography *(to reach place-based data)* | S2 L13 cell · county / state FIPS · ZIP |

Study / dataset / mission accessions (OSD, GLDS…) are a **federation island** — never join on them.

## Bio ↔ place-based data (the analytical pattern)

To connect a molecular result to a **place**, get the bio entity onto a **geographic key** (S2 /
county FIPS / ZIP), never a name — through whichever KG carries **both** your entity and geography.
Ask `find_context_sources(want=["geospatial"], join_key=…)` / `get_join_strategy` which bridge fits,
and build on the returned `skeleton_query`. Common bridges: **spoke-okn** (gene / disease / chemical +
geo / SDoH / environmental), **biohealth** (disease + SDoH), **sawgraph** (chemical + environmental).
Useful chains:

- **disease / gene → place → exposure / services**: entity → county FIPS → sawgraph (PFAS,
  environment), fiokg (facilities), dreamkg / ruralkg (services), nikg / scales (neighborhood /
  justice), sockg / ufokn (soil / flood).
- **chemical → adverse outcome → gene / disease**: chemical (CHEBI / CAS / PubChem) → biobricks tox →
  biobricks-aopwiki key-event targets → disease.
- **chemical exposure → place**: the same chemical id → sawgraph observations located on S2 / county
  (no bio hub needed).
- **gene / disease → SDoH**: social-determinant layers (spoke-okn / biohealth) by disease or geography.
- **social / psychosocial concept → SDoH**: `biohealth` is the **UMLS-keyed SDoH hub**; other domain
  vocabularies attach to it by **exact concept-name LABEL match** (fragile, curated lower bound) —
  `dreamkg` social-service audience terms (SS1) and `phaseskg`'s healthy-aging ontology (SS2:
  loneliness, social isolation, social withdrawal, social detachment, shyness, alienation,
  reminiscence therapy, self-efficacy → biohealth UMLS concepts). Use these to pull biohealth's
  clinical / SDoH associations for an aging / social-connection construct; get the recipe from
  `get_join_strategy` / `list_crosswalks` (cluster SS/BH), and note these are OBSERVATIONAL literature
  associations, not causal.
- **place → climate → Earth-observation / literature** *(indirect, non-bio context)*: a location in
  **spoke-okn** tagged with a **GeoNames** id bridges to **climatemodelskg** climate-model output for
  that place (`climatemodelskg × spoke-okn` on GeoNames, cluster GN), which in turn bridges to
  **nasa-gesdisc-kg** — NASA GES DISC's Earth-observation + bibliometric graph — on **DOI** (PB1, 651
  shared publications) and on **GCMD instrument / platform name** (EO1/EO2). Use it to surface, for a
  place or climate topic, the NASA **satellite datasets, instruments/platforms**, and the
  **publication / citation graph** (465k publications with DOI + author **ORCID** + institution
  **ROR** + OpenAlex). **Caveat:** nasa-gesdisc-kg has **no direct join to any bio KG** — this is
  climate / Earth-observation context and literature provenance reached *indirectly* (GeoNames is a
  place-id bridge; DOI and instrument/platform names are the climatemodelskg↔nasa keys, the latter a
  label match). Not a molecular data source; use for environmental / climate-health framing, not for
  gene / disease evidence.

## Mapping to phenotypes (HP)

Phenotype = **HP** terms (`obo/HP_`); **5 suppliers** — `oard-kg`, `prokn`, `rdkg`,
`gene-expression-atlas-okn`, `biohealth`. spoke-okn and pankgraph carry **disease but no phenotype** —
reach HP by bridging their disease. Disease is the pivot: **MONDO** is the hub, and DOID / EFO / OMIM /
Orphanet / UMLS all bridge to MONDO (and onward to HP) through **ubergraph**. Route by source entity:

- **disease → HP**: `oard-kg` is richest (EHR disease↔phenotype associations) but **reified** — the HP
  (or MONDO) term can sit on `biolink:subject` *or* `biolink:object`, so **UNION both positions** or you
  silently drop half the matches. `rdkg` gives a cleaner, more direct disease→phenotype edge.
- **gene → HP**: **no direct edge** — route gene → disease → HP (intra-KG in `rdkg`, or get the gene's
  diseases in pankgraph / spoke-okn / prokn / rdkg, then bridge disease → HP to `oard-kg` / `rdkg`).
- **protein → HP**: only `prokn`, and only via reified marker-gene / clinical-evidence statements (no
  labelled `protein has_phenotype` predicate) — HP sits in object position of those statements.
- **biohealth → HP**: its entities are UMLS-CUI node IRIs; it reaches HP only through the ubergraph
  **UMLS↔HP** (`oboInOwl:hasDbXref`) bridge.

For a **disease category** ("all cardiovascular", "any asthma"), expand with ubergraph
`rdfs:subClassOf*` and join to the phenotype KG in the same query (the disease-subtype expansion note
below applies unchanged). The concrete cross-KG recipes — exact predicates, IRI normalization, verified
counts, a runnable `skeleton_query` — are the crosswalk catalog's **disease / phenotype cluster A** and
**biohealth BH cluster**: copy them from `list_crosswalks` / `get_join_strategy`; **don't hard-code the
predicates here** (they drift across releases). `find_context_sources(want=["phenotype"], join_key=…)`
lists every supplier and its key. oard-kg disease↔phenotype is EHR **co-occurrence — observational, not
causal**.

## Mapping / aligning organisms (taxon)

Taxon = **NCBITaxon**; **8 KGs attach as a star hub through `ubergraph`** — spoke-okn, spoke-genelab,
nde, sawgraph, biobricks-aopwiki, gene-expression-atlas-okn carry **real NCBITaxon ids**; wildlifekn
(authority-stripped scientific binomial) and biohealth (UMLS concept name) are **label-only — fragile,
and cannot clade-expand**. (`biobricks-mesh` has an organism payload but is MeSH, *not* a taxon-hub
member.) Each KG encodes taxa differently — a node-IRI id, a string-literal IRI, a `biolink:in_taxon` /
`schema:species` object, or a bare label — so **don't hard-code the per-KG shape**; the
**`taxon_overlap(kg_a, kg_b)`** tool returns the normalization for both sides as two runnable skeletons
(`exact_id_skeleton` and `clade_membership_skeleton`) plus a verified `materialized_overlap`.

**The trap: an exact NCBITaxon-id match badly understates real overlap** (one side is often coarse —
genus / family — the other fine strains). **Always clade-expand** with ubergraph `rdfs:subClassOf*`
(the tool's clade skeleton does this; it is directional — swap args to flip the parent side).

- **spoke-genelab is a dual spoke**: 9 model-organism taxa (on `Gene.taxonomy`) + **46 microbiome taxa**
  (bacteria / fungi; NCBITaxon id embedded in the Organism node IRI, e.g. `node/286` = Pseudomonas).
- **spoke-genelab microbiome → spoke-okn**: only **2 by exact-id**, but **33,313 by clade expansion**
  (96% of spoke-okn's 34,570 strain taxa) — because the microbiome set includes broad clades (e.g.
  `NCBITaxon_2` Bacteria) that contain most spoke-okn strains. This is the canonical example of the trap.

This is **distinct from ortholog projection** (the spoke-genelab appendix / `collapse_orthologs.py`),
which collapses model-organism *genes* to human genes — a gene-lane operation. Taxon mapping joins the
*organisms themselves*. Verified recipes / counts are the crosswalk catalog's **cluster D + `taxon_hub`**
(`hub_kg: ubergraph`, per-pair `exact_id / clade_a_in_b / clade_b_in_a`): read them via `taxon_overlap`
/ `list_crosswalks`; `find_context_sources(want=["organism"], join_key=…)` lists suppliers. A
clade-expanded overlap is **taxonomic containment (a coarse taxon covering many finer ones), not 1:1
identity** — carry that caveat.

## Within-KG recipe worth keeping: prokn GO / Reactome enrichment

Cross-KG joins come from `get_join_strategy`; this is a *within-prokn traversal* the tools don't hand
you. prokn genes are HGNC-keyed with the **symbol on `rdfs:label`**; GO / Reactome sit on the encoded
UniProt protein:

```
?gene rdfs:label ?sym ;                                             # match your gene symbol
      <http://semanticscience.org/resource/SIO_010078> ?prot .      # encodes -> UniProt protein
?prot <http://purl.obolibrary.org/obo/RO_0002331> ?go .             # involved in -> GO (BP)
#  or <http://purl.obolibrary.org/obo/RO_0002327> ?go               # enables -> GO (MF)
#  or <http://purl.uniprot.org/core/partOf> ?go                     # part of -> GO (CC)
?prot <http://purl.obolibrary.org/obo/RO_0000056> ?pw .             # participates in -> pathway
?pw a <http://purl.uniprot.org/core/Pathway> . FILTER(CONTAINS(STR(?pw),"R-HSA"))  # human Reactome
```

For disease **subtype** expansion ("any asthma", "all cardiovascular disease"), expand inline with
ubergraph's `rdfs:subClassOf*` closure and join it to the target KG in the SAME query.

## Endpoint quirks that shape your analysis code

Most reliability behaviour is handled by the tools; two things still change how you write code:
- **No global `ORDER BY`** (an endpoint-wide sort on a big pattern → timeout) — rank client-side in
  pandas.
- **Large results auto-save to a file** (`tool-results/*.txt`, JSON `{vars, rows}`) — process with
  `jq` / pandas from the bash mount; don't read big results inline. This is the intended path for full
  signatures / backgrounds.

Also: go one heavy pattern at a time, and don't fire many concurrent heavy queries.

## Reproducibility

Don't mark substantive queries `exploratory`; pin KG versions + dates with `get_kg_version`; keep
intermediate extracts + scripts; re-verify headline counts live at the end (expect zero drift).

## spoke-genelab (one optional model-organism DE source)

Its query-time contrast rules are returned by `get_schema` (`usage_notes`) and enforced by
`get_valid_contrasts` — **use those, don't re-derive them**. In brief: reified DE
`?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object
?gene ; schema:log2fc ?l ; schema:adj_p_value ?p` (methylation `…_ASmMR` / microbial abundance
`…_ASmO` analogous); call a gene differentially expressed at **adj_p ≤ 0.05 and |log2FC| ≥ 1**
(`FILTER(?p <= 0.05 && ABS(?l) >= 1)`). Then ortholog `?gene gl:IS_ORTHOLOG_MGiG ?humanGene` →
collapse with `scripts/collapse_orthologs.py`; then integrate on Entrez like any other gene source.

Microbial-abundance (`…_ASmO`) rows carry an **organism identity** — spoke-genelab's 46 microbiome
taxa (bacteria / fungi) — not just an abundance value. Don't discard the taxon: map those organisms
across KGs via the taxon route ("Mapping / aligning organisms" above / `taxon_overlap`), e.g. onto
spoke-okn's strains by ubergraph clade expansion.

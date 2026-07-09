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
`…_ASmO` analogous); ortholog `?gene gl:IS_ORTHOLOG_MGiG ?humanGene` → collapse with
`scripts/collapse_orthologs.py`; then integrate on Entrez like any other gene source.

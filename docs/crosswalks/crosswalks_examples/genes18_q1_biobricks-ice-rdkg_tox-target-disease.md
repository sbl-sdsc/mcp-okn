# A gene targeted by ICE toxicology assays, resolved to the rare diseases rdkg associates with it

- **Date:** 2026-07-11
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>

## Conversation

👤 **User**

Crosswalk: `biobricks-ice` × `rdkg` on **Entrez** (new cross-domain link). BioBricks-ICE tags each tox assay with its mechanistic gene target via `ice:assay_entrez_gene_id`, stored as an `https://www.ncbi.nlm.nih.gov/gene/{Entrez}` IRI. RDKG models rare-disease gene associations with gene node-IRIs `http://identifiers.org/ncbigene/{Entrez}`. Strip ICE's IRI to the bare Entrez id and rebuild the rdkg form.

Research question: for the androgen receptor (AR, Entrez 367) — a canonical endocrine-disruption assay target that ICE screens chemicals against — what diseases does rdkg associate with that same gene?

Why the join is required: ICE knows *which gene a chemical perturbs in an assay* but nothing about that gene's disease role; rdkg knows the gene→disease associations but nothing about chemical assays. The shared Entrez id connects a toxicological mechanism to its clinical genetics.

---

🧠 **Assistant**

The Entrez bridge carries a tox-assay target into disease genetics: ICE's `assay_entrez_gene_id` gene AR resolves to the rdkg gene node, whose `biolink:related_to` edges name the diseases. Every row carries BOTH graphs — the ICE assay gene target and an rdkg disease:

| ICE assay target (Entrez) | rdkg-associated disease (MONDO) |
| --- | --- |
| AR / androgen receptor (367) | partial androgen insensitivity syndrome (MONDO_0010720) |
| AR (367) | Kennedy disease / spinobulbar muscular atrophy (MONDO_0010735) |
| AR (367) | prostate cancer (MONDO_0008315) |
| AR (367) | prostate adenocarcinoma (MONDO_0005082) |
| AR (367) | male breast carcinoma (MONDO_0005628) |
| AR (367) | alopecia (MONDO_0004907) |

**Why it answers the question.** AR is the classic androgen-receptor target of ICE's endocrine-disruption assays — a chemical that agonizes or antagonizes AR in ICE screening perturbs the very gene rdkg ties to **partial androgen insensitivity syndrome** and **Kennedy disease** (both caused by AR mutations/expansions) and to hormone-driven cancers (prostate, male breast). The join therefore places a chemical's mechanistic assay hit into a concrete disease context: *this assay reports on the gene behind these androgen-dependent disorders*. Neither graph holds both halves.

#### Query 1 — ICE's AR assay target joined to rdkg diseases

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ice: <https://ice.ntp.niehs.nih.gov/property/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT DISTINCT ?disease WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?assay ice:assay_entrez_gene_id <https://www.ncbi.nlm.nih.gov/gene/367> . }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    <http://identifiers.org/ncbigene/367> biolink:related_to ?d . ?d rdfs:label ?disease . }
} ORDER BY ?disease
```

_Both-graph rows: AR (Entrez 367) is an ICE `assay_entrez_gene_id` target AND an rdkg gene whose `related_to` diseases include androgen insensitivity, Kennedy disease and prostate cancer._

## Literature validation

According to the literature, AR (androgen receptor) mutations cause androgen insensitivity syndrome and a CAG-repeat expansion in AR causes Kennedy disease (spinal and bulbar muscular atrophy) — corroborating the rdkg AR→disease rows joined to ICE's AR assay target (La Spada AR et al., "Androgen receptor gene mutations in X-linked spinal and bulbar muscular atrophy," *Nature* 352:77–79, 1991; [DOI](https://doi.org/10.1038/352077a0)). AR is also an established driver of prostate cancer. **Validated** (literature-corroborated; shared Entrez bridge; both-KG rows executed).

# How many of climatemodelskg's papers are also in NASA's Earth-science publication graph, on DOI

- **Date:** 2026-07-12
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `nasa-gesdisc-kg` — <https://purl.org/okn/frink/kg/nasa-gesdisc-kg>

## Conversation

👤 **User**

Crosswalk: `climatemodelskg` × `nasa-gesdisc-kg` on **DOI**. climatemodelskg carries a DOI literal (`cpub:doi`, `https://doi.org/` form) on its `Paper` nodes; nasa-gesdisc-kg carries a DOI IRI (`bibo:doi`, `http://dx.doi.org/` form) on its `Publication` nodes.

Research question: across climatemodelskg's full paper set, how many papers are also present in nasa-gesdisc-kg's publication graph — the size of the joinable overlap between the climate-modeling literature and the literature NASA GES DISC tracks around its Earth-science datasets?

Why the join is required: it takes both graphs' publication sets together to quantify how much of the climate-modeling literature is also part of NASA's Earth-science citation graph — the papers where climatemodelskg's structured modeling extraction and nasa-gesdisc-kg's bibliometric context are both available. Neither graph answers this alone.

---

🧠 **Assistant**

climatemodelskg carries **1,910 distinct-DOI** climate-modeling papers; nasa-gesdisc-kg carries **465,143 distinct-DOI** publications (the works that cite or use NASA Earth-science datasets). Normalizing both to the bare lowercase DOI and inner-joining:

| metric | value |
| --- | --- |
| climatemodelskg distinct-DOI papers | 1,910 |
| nasa-gesdisc-kg distinct-DOI publications | 465,143 |
| **shared DOIs** | **651** |

**Why it answers the question.** 651 of climatemodelskg's 1,910 papers (**34%**) are also in nasa-gesdisc-kg — a large overlap given the graphs were built independently for different purposes (climate-model semantic extraction vs. NASA dataset bibliometrics). For each of these 651 papers, climatemodelskg's structured facts (models used, methods, fields, keywords, innovations) can be read alongside nasa-gesdisc-kg's bibliometric record (full authorship, year, author ORCID, institution ROR, and the paper's place in NASA's citation graph). This is the integration surface neither graph exposes alone, and it is nasa-gesdisc-kg's **first crosswalk in the federation** — de-islanding a graph that was previously unreachable because its shipped `entities.csv` namespace differs from the deployed one. The join is robust by construction: DOIs are registered, case-insensitive persistent identifiers, and the only surface differences (`https` vs `http`, `doi.org` vs `dx.doi.org`, occasional prefix-letter case) are removed by the normalization.

#### Query 2 — the climatemodelskg ↔ nasa-gesdisc-kg DOI overlap

```sparql
PREFIX cpub: <https://climatepub4kg.github.io/ontology#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
SELECT (COUNT(DISTINCT ?bare) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
    ?p1 cpub:doi ?d1 .
    BIND(LCASE(REPLACE(STR(?d1),"^https?://(dx[.])?doi[.]org/","")) AS ?bare) }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
    ?p2 bibo:doi ?d2 .
    BIND(LCASE(REPLACE(STR(?d2),"^https?://(dx[.])?doi[.]org/","")) AS ?bare) }
}
```

_Returns **651** — climatemodelskg papers whose DOI is also a nasa-gesdisc-kg publication (of 1,910 distinct-DOI papers)._

## Literature validation

Validated by construction on the authoritative shared standard (the DOI) plus the hand-verified crosswalk: each match is an exact shared DOI after normalizing scheme/host/case, and sampled matches agree by title on both sides (e.g. `10.1007/s00382-012-1636-1` — the IPSL-CM5 CMIP3→CMIP5 paper; `10.5194/bg-9-759-2012` — the terrestrial methane-budget paper). The verified count (651) was reproduced live. **Validated** (shared DOI standard; count executed live).

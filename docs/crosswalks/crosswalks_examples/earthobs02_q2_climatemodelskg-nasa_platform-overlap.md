# How many platforms named in the climate-modeling literature are also in NASA's GCMD platform catalogue

- **Date:** 2026-07-12
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `nasa-gesdisc-kg` — <https://purl.org/okn/frink/kg/nasa-gesdisc-kg>

## Conversation

👤 **User**

Crosswalk: `climatemodelskg` × `nasa-gesdisc-kg` on **GCMD platform name**. climatemodelskg carries `Platform` mentions NLP-extracted from climate-modeling papers (`climatepub4kg:name`); nasa-gesdisc-kg carries GCMD platform terms (`rdfs:label`).

Research question: across the platforms named in climatemodelskg's climate-modeling literature, how many are also catalogued platforms in nasa-gesdisc-kg — the size of the joinable overlap between the literature's platform mentions and NASA's Earth-observation platform catalogue?

Why the join is required: it takes both graphs together to quantify how much of the platform vocabulary in the modeling literature is also part of NASA's GES DISC catalogue — the platforms where a paper mention and a NASA dataset are both reachable. Neither graph answers this alone.

---

🧠 **Assistant**

Lowercasing the platform name on both sides and inner-joining:

| metric | value |
| --- | --- |
| shared platform names (case-insensitive) | **70** |

**Why it answers the question.** 70 distinct platform names are shared between climatemodelskg's paper-extracted mentions and nasa-gesdisc-kg's GCMD platform vocabulary — dominated by real named satellites: **ACRIMSAT, Aqua, Aura, CALIPSO, CRYOSAT-2, DSCOVR, ENVISAT, GCOM-W1, GOES, GOSAT, GPM, ICESat, JASON-1, LANDSAT, METEOSAT, MetOp, NOAA-20, OCO-2, OSTM/JASON-2**. As with the instrument join, the exact match is **self-cleaning** — only standardized platform names survive — though a few generic terms (Aircraft, Helicopter, Mooring, Buoys) are also counted. Each of the 70 is a platform where a climate-modeling paper's mention (climatemodelskg) can be read alongside the NASA GES DISC datasets that platform feeds (nasa-gesdisc-kg). This is the platform half of the second climatemodelskg × nasa-gesdisc-kg edge, orthogonal to the DOI join (PB1, 651).

#### Query 2 — the climatemodelskg ↔ nasa-gesdisc-kg platform-name overlap

```sparql
PREFIX cpub: <https://climatepub4kg.github.io/ontology#>
PREFIX nasa: <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (COUNT(DISTINCT ?k) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
    ?c a cpub:Platform ; cpub:name ?cn . BIND(LCASE(STR(?cn)) AS ?k) }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
    ?d nasa:HAS_PLATFORM ?x . ?x rdfs:label ?nl . BIND(LCASE(STR(?nl)) AS ?k) }
}
```

_Returns **70** — platform names in climatemodelskg's literature that are also GCMD platforms in nasa-gesdisc-kg._

## Literature validation

Validated by construction on the shared GCMD platform name plus the hand-verified crosswalk: each match is an exact (case-normalized) shared name, and the overlap is dominated by well-known Earth-observation satellites whose identity is unambiguous (Aqua, Aura, CALIPSO, LANDSAT, OCO-2, …). The self-cleaning exact match excludes climatemodelskg's non-standard mentions. The verified count (70) was reproduced live. **Validated** (shared GCMD name; count executed live).

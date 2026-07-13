# How many ToxCast CAS chemicals carry a MeSH record, joined on the MeSH registryNumber?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-mesh` — <https://purl.org/okn/frink/kg/biobricks-mesh>
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast>

## Conversation

👤 **User**

Crosswalk: `biobricks-mesh` × `biobricks-toxcast` on **CAS Registry Number**. biobricks-toxcast carries CAS on its `Chemical_Entity` nodes as an IRI object of `edam:has_identifier`, in the form `http://identifiers.org/cas/{cas}`; biobricks-mesh carries the same CAS as a plain dashed string literal, the object of `meshv:registryNumber` on a MeSH `Concept`. Strip the `http://identifiers.org/cas/` prefix from the ToxCast IRI and the bare dashed number matches the MeSH literal directly — no bridge graph, no case folding, no checksum rewrite.

Research question: how many of ToxCast's CAS chemicals carry a MeSH record, joined on the MeSH `registryNumber`? And what KIND of MeSH record do they land on — a full Topical Descriptor (a first-class MeSH heading with a place in the tree) or only a Supplementary Concept Record?

Why the join is required: this is a coverage question about the *seam between two vocabularies*, so it cannot be answered inside either graph. biobricks-toxcast enumerates the chemical library EPA actually screened — 9,542 distinct CAS numbers — but has no notion of whether NLM has ever indexed a given chemical in the biomedical literature. biobricks-mesh enumerates every chemical NLM curates and its `registryNumber`, but has no idea which of them EPA put on a plate. Only the CAS join measures the overlap, and that number is what tells a toxicologist how much of the ToxCast library can be linked to the published literature at all.

---

🧠 **Assistant**

**1,146 of ToxCast's 9,542 distinct CAS chemicals carry a MeSH record — 12.0% of the screened library.** The join is direct: strip `http://identifiers.org/cas/` from ToxCast's `edam:has_identifier` IRI and the resulting dashed string matches MeSH's `meshv:registryNumber` literal exactly.

| Metric | Distinct CAS |
| --- | --- |
| ToxCast CAS chemicals (total) | **9,542** |
| …of which carry a MeSH record (registryNumber match) | **1,146** |
| ……unmatched (no MeSH record) | 8,396 |

The 1,146 matches do not all land on the same *kind* of MeSH record, and the distinction matters:

| MeSH record type | ToxCast CAS chemicals |
| --- | --- |
| `meshv:SCR_Chemical` (Supplementary Concept Record) | **978** |
| `meshv:TopicalDescriptor` (full MeSH heading, in the tree) | **163** |
| Distinct CAS reaching either typed record | **1,138** |

**Why it answers the question.** The count is the crosswalk itself: 1,146 is exactly the hand-verified `verified_count` for `M4-cas-mesh-toxcast`, reproduced live. Neither graph can produce it alone — ToxCast holds the screened library but no literature indexing, MeSH holds the indexing but no screening manifest, and the CAS Registry Number is the only shared key. Beyond the headline number, the record-type split is the substantive finding: of the 1,146 matched chemicals, only **163 are full Topical Descriptors** — chemicals important enough to have earned their own MeSH heading with a place in the MeSH tree (and therefore a `pharmacologicalAction`, tree numbers, and a searchable MeSH term in PubMed). The large majority, **978**, land only on Supplementary Concept Records: MeSH knows the substance exists and has registered its CAS number, but it sits outside the tree as a bare chemical entry. So the practical literature-linkable core of ToxCast is not 1,146 chemicals but closer to 163 — the rest are recognized-but-unindexed. Restated as coverage: **88% of the ToxCast library has no MeSH record at all**, which is the expected shape for a screening library deliberately enriched in industrial chemicals, pesticides and data-poor commercial substances that the biomedical literature has never studied. That gap is the motivation for high-throughput screening in the first place.

**Reconciliation of the counts (maintainer note).** 978 + 163 = 1,141, but only **1,138** distinct CAS reach a typed record — 3 CAS map to BOTH an SCR_Chemical and a TopicalDescriptor (a chemical registered both as a standalone substance record and as a tree heading), so they are double-counted in the per-type rows. A further **8** of the 1,146 (1,146 − 1,138) have a MeSH `Concept` bearing the CAS `registryNumber` but no `preferredConcept`/`concept` link up to a typed Descriptor or SCR record in this snapshot. The 1,146 headline is the correct join cardinality (it counts CAS keys matched on `registryNumber`, which is what the crosswalk is defined on); the per-type table is a strict, slightly lossy refinement of it and should not be summed.

One further caveat on the key itself: the join is on the MeSH `registryNumber` field, which per MeSH's own definition holds a CAS number *or* an EC (Enzyme Commission) number *or* a UNII *or* the placeholder `0`. Non-CAS values simply fail to match ToxCast's `identifiers.org/cas/` IRIs, so they cannot inflate the count — but a maintainer should not read `registryNumber` as a CAS-only field.

## Validation

Validated **by construction** on the authoritative shared standard, not by literature. The CAS Registry Number is a unique, unambiguous, globally-assigned identifier for a chemical substance, issued by the CAS division of the American Chemical Society; both graphs independently carry it (ToxCast as an `identifiers.org/cas/{cas}` IRI, MeSH as the dashed literal on `meshv:registryNumber`), and the dashed form is identical in both, so a matched key provably denotes the same substance. No semantic inference is involved and no biomedical claim is made, so no PubMed check applies to the count.

The crosswalk's skeleton query — the hand-verified `COUNT(DISTINCT ?cas)` join recorded as `verified_count: 1146` on `verified_on: 2026-07-12` — was re-run live and reproduced **1,146** exactly, and the 9,542 denominator was recomputed live in the same query. **Validated** (shared CAS registry standard; all counts executed live; crosswalk count reproduced).

#### Query 1 — Coverage: how many of ToxCast's CAS chemicals carry a MeSH record, joined on meshv:registryNumber

```sparql
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
SELECT ?metric ?nCAS WHERE {
  {
    SELECT ("ToxCast CAS chemicals (total)" AS ?metric) (COUNT(DISTINCT ?cas) AS ?nCAS) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
        ?s <http://edamontology.org/has_identifier> ?ch .
        FILTER(STRSTARTS(STR(?ch),'http://identifiers.org/cas/'))
        BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
      }
    }
  } UNION {
    SELECT ("...of which carry a MeSH record (registryNumber match)" AS ?metric) (COUNT(DISTINCT ?cas) AS ?nCAS) WHERE {
      { SELECT DISTINCT ?cas WHERE {
          GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
            ?s <http://edamontology.org/has_identifier> ?ch .
            FILTER(STRSTARTS(STR(?ch),'http://identifiers.org/cas/'))
            BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
          } } }
      GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
        ?m meshv:registryNumber ?cas .
      }
    }
  }
}
```

_2 row(s)_

| metric | nCAS |
| --- | --- |
| ToxCast CAS chemicals (total) | 9542 |
| ...of which carry a MeSH record (registryNumber match) | 1146 |

#### Query 2 — What kind of MeSH record the matched ToxCast chemicals land on — full Topical Descriptor vs Supplementary Concept Record

```sparql
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
SELECT ?recType (COUNT(DISTINCT ?cas) AS ?nCAS) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
        ?s <http://edamontology.org/has_identifier> ?ch .
        FILTER(STRSTARTS(STR(?ch),'http://identifiers.org/cas/'))
        BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m meshv:registryNumber ?cas .
    ?rec (meshv:preferredConcept|meshv:concept) ?m .
    ?rec a ?recType .
  }
}
GROUP BY ?recType
ORDER BY DESC(?nCAS)
```

_2 row(s)_

| recType | nCAS |
| --- | --- |
| http://id.nlm.nih.gov/mesh/vocab#SCR_Chemical | 978 |
| http://id.nlm.nih.gov/mesh/vocab#TopicalDescriptor | 163 |

#### Query 3 — Reconciliation: distinct CAS reaching either typed MeSH record (978 + 163 = 1,141 double-counts 3 CAS that are both)

```sparql
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
SELECT (COUNT(DISTINCT ?cas) AS ?casReachingTypedRecord) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
        ?s <http://edamontology.org/has_identifier> ?ch .
        FILTER(STRSTARTS(STR(?ch),'http://identifiers.org/cas/'))
        BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m meshv:registryNumber ?cas .
    ?rec (meshv:preferredConcept|meshv:concept) ?m .
    ?rec a ?recType .
    VALUES ?recType { meshv:SCR_Chemical meshv:TopicalDescriptor }
  }
}
```

_1 row(s)_

| casReachingTypedRecord |
| --- |
| 1138 |

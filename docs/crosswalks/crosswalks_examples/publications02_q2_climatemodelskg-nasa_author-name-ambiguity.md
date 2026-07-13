# How many climatemodelskg author names also appear as NASA GES DISC authors — and how ambiguous is that match?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `nasa-gesdisc-kg` — <https://purl.org/okn/frink/kg/nasa-gesdisc-kg>

## Conversation

👤 **User**

Crosswalk: `climatemodelskg` × `nasa-gesdisc-kg` on **author name** — a plain STRING literal on both sides (`climatepub4kg:name` on a `cm:Author` node; `rdfs:label` on a nasa-gesdisc `schema:Author` node). Both sides store 'First Last', neither uses 'Last, First', so they match exactly with no normalization rewrite — but the join must be driven from the small side (climatemodelskg's 10,029 names) into NASA's 905,086 Author nodes, binding the SAME ?nm variable in both GRAPH blocks; a cross-graph FILTER or a BIND/LCASE over NASA's author pool times out.

THE CAVEAT IS THE QUESTION HERE: this is a NAME join, NOT an ORCID join. An ORCID join is *impossible* — NASA carries orcid on ~60% of its authors (plus openalexId on 100% and ROR affiliations), but climatemodelskg's Author nodes carry only `#name` and `#uuid`: no orcid, no openalexId, no ror anywhere in the graph. So the shared key is a human name, and human names are not identifiers.

Research question: how many climatemodelskg author names also appear as NASA GES DISC author names — and, crucially, HOW AMBIGUOUS is that match? Measure it: of the matched names, how many resolve to more than one distinct ORCID on the NASA side (i.e. provably denote several different human beings)?

Why the join is required: this is the only edge between the two graphs' author populations, and the only way to size it is to run it. But its trustworthiness cannot be taken on faith — it has to be audited against an external identity anchor. NASA's ORCID is that anchor: it is the one identifier in either graph that pins a name to a distinct real person, so it can be used as ground truth to *quantify the false-positive rate of the join itself*. The point of this exercise is to state, with a number, exactly how far this crosswalk can be trusted.

---

🧠 **Assistant**

**8,391 of climatemodelskg's 10,029 distinct author names (83.7%) match a NASA GES DISC author name — and 11.3% of the checkable matches are provably wrong at the person level.** The match rate is high; the *identity* it implies is not trustworthy.

### The match

| Measure | Count | Share |
| --- | --- | --- |
| Distinct author names in climatemodelskg | 10,029 | — |
| ...matching a NASA GES DISC `schema:Author` label | **8,391** | **83.7%** |

This reproduces the crosswalk's `verified_count` exactly. It is **not** a quality score: NASA's author pool is 905,086 nodes, large enough that ordinary names match by chance alone. So the 83.7% is an upper bound on overlap, inflated by collisions.

### The ambiguity, measured against NASA's ORCID as ground truth for "distinct real human"

| Measure | Value |
| --- | --- |
| Matched names reaching ≥1 ORCID-bearing NASA author (the checkable subset) | 6,983 |
| ...resolving to exactly ONE distinct ORCID (1:1, defensible) | 6,196 (88.7%) |
| ...resolving to **MORE THAN ONE** distinct ORCID (provably ≥2 different people) | **787 (11.3%)** |
| Distinct ORCIDs sitting behind those 6,983 names | 14,288 — a **2.05×** fan-out |
| Worst single name | **179 distinct ORCIDs** |

### The tail is catastrophic, and it is not random

| climatemodelskg author name | Distinct NASA ORCIDs behind it |
| --- | --- |
| Yang Liu | **179** |
| Wei Wang | 164 |
| Wei Li | 127 |
| Lei Wang | 122 |
| Yan Li | 115 |
| Yang Li | 109 |
| Hao Wang | 104 |
| Yu Wang | 102 |

**Why it answers the question.** The first query sizes the crosswalk: 8,391 shared name strings. The second and third audit it — not by restating the catalog's caveat, but by recomputing it live against the only identity anchor available anywhere in this KG pair. NASA mints an Author node per paper, so a *node*-level count would inflate the apparent ambiguity; counting DISTINCT ORCIDs per name instead gives the honest figure. The verdict: ~89% of ORCID-checkable matches are one-name-one-person and defensible, but 787 names (11.3%) each collapse two or more real, distinct researchers into a single join key — and the fan-out on those is not a rounding error but an avalanche. "Yang Liu" in climatemodelskg is a single `cm:Author` node; on the NASA side that string is 179 different human beings. Any query that follows the name from one graph to the other and speaks about "this author" is, for that row, wrong 178 times over.

**Validation — and what this join does NOT license.** Validated by construction on the shared string key plus the hand-verified crosswalk (the join reproduces `verified_count` = 8,391), with the false-positive rate **measured, not assumed**. But validation of the *count* is not validation of the *identity*: the key is a name, and a name is not a person. **No person-level claim is licensed by this join.** It cannot be used to assert that any specific individual authored both a climate-modeling paper and a NASA GES DISC paper — not even for the 88.7% that happen to be 1:1, because climatemodelskg supplies no identifier with which to confirm that its "Yang Liu" is the unambiguous one. It is safe only in aggregate: cohort overlap, community-level comparisons, population sizing. Two further maintainer caveats: (1) the ambiguity is concentrated in Chinese-origin names, so it does not merely add noise — it *biases* any naive per-author aggregate against that population; (2) the 40% of NASA authors with no ORCID are outside this audit entirely, so 11.3% is a floor, not a ceiling. To harden a specific author claim you must disambiguate on the NASA side (orcid + a co-author or institution/ROR check) — climatemodelskg contributes nothing to that. Where the question can be asked about *papers* rather than *people*, prefer the sibling DOI crosswalk (PB1) on this same KG pair: it is an exact identifier join. **Validated as a cohort-level edge; explicitly invalid for person-level inference.**

#### Query 1 — How many climatemodelskg author names also appear as a NASA GES DISC author name

```sparql
SELECT ?cmAuthorNames ?matchedNames WHERE {
  { SELECT (COUNT(DISTINCT ?nm1) AS ?cmAuthorNames) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
        ?a1 a <https://climatepub4kg.github.io/ontology#Author> ;
            <https://climatepub4kg.github.io/ontology#name> ?nm1 . } } }
  { SELECT (COUNT(DISTINCT ?nm2) AS ?matchedNames) WHERE {
      { SELECT DISTINCT ?nm2 WHERE {
          GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
            ?a2 a <https://climatepub4kg.github.io/ontology#Author> ;
                <https://climatepub4kg.github.io/ontology#name> ?nm2 . } } }
      GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
        ?b2 a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
            <http://www.w3.org/2000/01/rdf-schema#label> ?nm2 . } } }
}
```

_1 row(s)_

| cmAuthorNames | matchedNames |
| --- | --- |
| 10029 | 8391 |

#### Query 2 — The ambiguity rate: matched names that resolve to more than one distinct NASA ORCID

```sparql
SELECT (COUNT(*) AS ?matchedNamesWithOrcid)
       (SUM(IF(?k > 1, 1, 0)) AS ?ambiguousNames)
       (SUM(?k) AS ?distinctOrcidsBehindThem)
       (MAX(?k) AS ?worstCaseOrcidsForOneName)
WHERE {
  { SELECT ?nm (COUNT(DISTINCT ?orcid) AS ?k) WHERE {
      { SELECT DISTINCT ?nm WHERE {
          GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
            ?a a <https://climatepub4kg.github.io/ontology#Author> ;
               <https://climatepub4kg.github.io/ontology#name> ?nm . } } }
      GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
        ?b a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
           <http://www.w3.org/2000/01/rdf-schema#label> ?nm ;
           <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/orcid> ?orcid . }
    } GROUP BY ?nm }
}
```

_1 row(s)_

| matchedNamesWithOrcid | ambiguousNames | distinctOrcidsBehindThem | worstCaseOrcidsForOneName |
| --- | --- | --- | --- |
| 6983 | 787 | 14288 | 179 |

#### Query 3 — The worst offenders: matched author names hiding the most distinct real people

```sparql
SELECT ?nm (COUNT(DISTINCT ?orcid) AS ?distinctOrcids) WHERE {
  { SELECT DISTINCT ?nm WHERE {
      GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
        ?a a <https://climatepub4kg.github.io/ontology#Author> ;
           <https://climatepub4kg.github.io/ontology#name> ?nm . } } }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
    ?b a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
       <http://www.w3.org/2000/01/rdf-schema#label> ?nm ;
       <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/orcid> ?orcid . }
}
GROUP BY ?nm
ORDER BY DESC(?distinctOrcids)
LIMIT 8
```

_8 row(s)_

| nm | distinctOrcids |
| --- | --- |
| Yang Liu | 179 |
| Wei Wang | 164 |
| Wei Li | 127 |
| Lei Wang | 122 |
| Yan Li | 115 |
| Yang Li | 109 |
| Hao Wang | 104 |
| Yu Wang | 102 |

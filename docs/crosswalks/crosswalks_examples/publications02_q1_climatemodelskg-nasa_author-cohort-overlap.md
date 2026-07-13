# Is the climate-modeling author community also the NASA Earth-observation data-using community? (a cohort-level name join)

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `nasa-gesdisc-kg` — <https://purl.org/okn/frink/kg/nasa-gesdisc-kg>

## Conversation

👤 **User**

Crosswalk: `climatemodelskg` × `nasa-gesdisc-kg` on **author name** (a STRING, not an identifier). climatemodelskg carries a free-text author name on its `cm:Author` nodes (`climatepub4kg:name`); nasa-gesdisc-kg carries the same free-text name as `rdfs:label` on its `schema:Author` nodes. Both sides are plain 'First Last' string literals, so they match exactly with no rewrite — but the join MUST be driven from the small side (climatemodelskg's 10,029 names) into NASA's 905,086 Author nodes, binding the SAME ?nm variable in both GRAPH blocks; a BIND/LCASE over NASA's author pool times out.

THE CAVEAT, UP FRONT: this is a NAME join, NOT an ORCID join. climatemodelskg publishes no author identifier at all — its Author nodes carry only `#name` and `#uuid`, with no orcid, openalexId or ror anywhere in the graph — so there is nothing to disambiguate against. NASA does carry orcid (on ~60% of its authors), and measured against it, 11.3% of the matched names provably belong to more than one distinct real person. The join is therefore safe for COHORT/AGGREGATE questions ONLY, and can NEVER be used to assert that a specific person authored on both sides.

Research question (deliberately posed at the cohort level): how much overlap is there between the authors of climate-modeling papers (climatemodelskg) and the authors of papers citing NASA GES DISC Earth-observation datasets — i.e. is the climate-modeling community also the EO-data-using community? And which NASA EO datasets does the overlapping cohort actually work with?

Why the join is required: climatemodelskg knows *what the climate-modeling literature does* (which models, experiments, fields and keywords a paper uses) but nothing about who uses NASA's observational data. nasa-gesdisc-kg knows *which authors cite which GES DISC Earth-observation datasets* but extracts no modeling semantics. Nothing but the author name connects the two author populations — the sibling crosswalk PB1 joins these same two graphs on DOI, but a DOI join can only speak about the 651 shared *papers*, and cannot express a question about *people*.

---

🧠 **Assistant**

**Yes — at the cohort level the two author populations overlap almost completely, and the overlap is broad rather than a niche intersection. But read every number below as a statement about NAMES, not about PEOPLE.**

### Cohort overlap

| Measure | Count | Share |
| --- | --- | --- |
| Distinct author names in climatemodelskg | 10,029 | — |
| ...that also appear as a NASA GES DISC author name | **8,391** | **83.7%** |
| climatemodelskg papers with ≥1 author | 1,965 | — |
| ...with ≥1 author name matching a NASA GES DISC author | **1,802** | **91.7%** |

### How ambiguous is that overlap? (measured against NASA's ORCID as ground truth)

| Measure | Count |
| --- | --- |
| Matched names that reach ≥1 ORCID-bearing NASA author | 6,983 |
| ...of those, names resolving to MORE THAN ONE distinct ORCID | **787 (11.3%)** |
| Distinct ORCIDs sitting behind those 6,983 names | 14,288 (2.05× fan-out) |
| Worst single name ("Yang Liu") | **179 distinct ORCIDs** |

### What the overlapping cohort actually works on

Restricted to the 6,196 *unambiguous* matched names (exactly one distinct ORCID on the NASA side), the GES DISC datasets most used by the overlapping cohort:

| NASA GES DISC dataset | Cohort authors working with it |
| --- | --- |
| NSIDC-0051 (sea-ice concentration, passive microwave) | 428 |
| MCD12Q1 (MODIS land-cover type, annual) | 295 |
| MOD15A2H (MODIS LAI/FPAR) | 240 |
| NSIDC-0079 (sea-ice concentration, bootstrap) | 195 |
| MCD12C1 (MODIS land-cover, climate modeling grid) | 173 |
| CIESIN_SEDAC_GPWv4_POPDENS_R11 (gridded population density) | 165 |
| MOD13Q1 (MODIS vegetation indices) | 165 |
| M2T1NXSLV (MERRA-2 single-level diagnostics) | 164 |

**Why it answers the question.** The two graphs describe two author populations that were never linked: climatemodelskg's authors are the people writing the climate-*modeling* literature; nasa-gesdisc-kg's authors are the people whose papers cite NASA GES DISC Earth-*observation* datasets. Joining them on the shared name string shows the populations are not two communities but largely one: 83.7% of climate-modeling author names, and 91.7% of climate-modeling *papers*, land in NASA's EO-citing author pool. The dataset breakdown says what that shared cohort reaches for — sea ice (NSIDC-0051/0079), MODIS land-cover and vegetation (MCD12Q1, MOD15A2H, MOD13Q1), and MERRA-2 reanalysis (M2T1NXSLV): exactly the boundary-condition, land-surface and evaluation data a modeling community would use. That is a cohort-level claim about a *community*, and it is the only kind of claim this edge licenses.

**Validation — and the hard limit on it.** Validated by construction on the shared string key plus the hand-verified crosswalk: the join reproduces the crosswalk's `verified_count` of 8,391 exactly, and the ambiguity figures were *recomputed live* here rather than restated. But the key is a NAME, not an identifier. Measured against NASA's ORCID, 787 of the 6,983 ORCID-checkable matched names (11.3%) provably denote more than one different human being, with a catastrophic tail — "Yang Liu" alone is 179 distinct ORCIDs. So the 83.7% is an upper bound inflated by chance collisions against NASA's 905,086-node author pool, and the ambiguity is concentrated in Chinese-origin names, which biases any naive per-author aggregate. **No person-level claim is licensed by this join**: nothing here says that any individual authored both a climatemodelskg paper and a NASA GES DISC paper, and it must never be used that way. climatemodelskg publishes no ORCID, openalexId or ROR, so it supplies nothing to disambiguate against; to harden any specific author claim you would have to pin it on the NASA side with orcid plus a co-author or institution (AFFILIATED_WITH → ROR) check. Where a question can be asked about *papers* instead of *people*, use the sibling DOI crosswalk (PB1) — it is an exact identifier join and does not carry this risk. **Validated at cohort level only** (shared string key; ambiguity measured, not assumed).

#### Query 1 — Cohort overlap: how many climatemodelskg author names (and papers) reach a NASA GES DISC author

```sparql
SELECT ?cmAuthorNames ?matchedNames ?cmPapers ?papersWithMatchedAuthor WHERE {
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
  { SELECT (COUNT(DISTINCT ?p1) AS ?cmPapers) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
        ?p1 a <https://climatepub4kg.github.io/ontology#Paper> ;
            <https://climatepub4kg.github.io/ontology#PAPER_AUTHORED_BY> ?ax . } } }
  { SELECT (COUNT(DISTINCT ?p2) AS ?papersWithMatchedAuthor) WHERE {
      { SELECT DISTINCT ?p2 ?nm3 WHERE {
          GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
            ?p2 a <https://climatepub4kg.github.io/ontology#Paper> ;
                <https://climatepub4kg.github.io/ontology#PAPER_AUTHORED_BY> ?a3 .
            ?a3 <https://climatepub4kg.github.io/ontology#name> ?nm3 . } } }
      GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
        ?b3 a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
            <http://www.w3.org/2000/01/rdf-schema#label> ?nm3 . } } }
}
```

_1 row(s)_

| cmAuthorNames | matchedNames | cmPapers | papersWithMatchedAuthor |
| --- | --- | --- | --- |
| 10029 | 8391 | 1965 | 1802 |

#### Query 2 — How ambiguous the name match is: matched names resolving to more than one distinct NASA ORCID

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

#### Query 3 — NASA GES DISC Earth-observation datasets most used by the overlapping cohort (unambiguous names only)

```sparql
SELECT ?dsLabel (COUNT(DISTINCT ?nm) AS ?cohortAuthors) WHERE {
  { SELECT ?nm WHERE {
      { SELECT DISTINCT ?nm WHERE {
          GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
            ?a a <https://climatepub4kg.github.io/ontology#Author> ;
               <https://climatepub4kg.github.io/ontology#name> ?nm . } } }
      GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
        ?b a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
           <http://www.w3.org/2000/01/rdf-schema#label> ?nm ;
           <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/orcid> ?orcid . }
    } GROUP BY ?nm HAVING (COUNT(DISTINCT ?orcid) = 1) }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
    ?b2 a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
        <http://www.w3.org/2000/01/rdf-schema#label> ?nm ;
        <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/WORKS_WITH_DATASET> ?ds .
    ?ds <http://www.w3.org/2000/01/rdf-schema#label> ?dsLabel . }
}
GROUP BY ?dsLabel
ORDER BY DESC(?cohortAuthors)
LIMIT 8
```

_8 row(s)_

| dsLabel | cohortAuthors |
| --- | --- |
| NSIDC-0051 | 428 |
| MCD12Q1 | 295 |
| MOD15A2H | 240 |
| NSIDC-0079 | 195 |
| MCD12C1 | 173 |
| CIESIN_SEDAC_GPWv4_POPDENS_R11 | 165 |
| MOD13Q1 | 165 |
| M2T1NXSLV | 164 |

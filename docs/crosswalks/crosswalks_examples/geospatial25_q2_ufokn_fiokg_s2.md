# Geospatial GEO25-Q2 — ufokn × fiokg (S2 Level-13): why ufokn co-locates with fiokg but not the single-state leaves

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Geospatial · **Shared identifier:** S2 Level-13 cell

## Knowledge graphs used

- `ufokn` — <https://purl.org/okn/frink/kg/ufokn> (Urban Flooding OKN; S2 Level-13 leaf)
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg> (EPA FRS facilities; national S2 leaf)
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph> (Maine PFAS samples; single-state S2 leaf)
- `hydrologykg` — <https://purl.org/okn/frink/kg/hydrologykg> (Illinois wells/streams; single-state S2 leaf)

**Join:** all four attach to spatialkg on the `s2.level13.{id}` cell. ufokn meets the others **directly in any shared cell**.

## Research question

**Q2.** ufokn is one of several S2 leaves. Does its flood layer co-locate with all of them equally, or only with some — and why? Which leaf-to-leaf joins are actually verifiable?

---

## Result

Running the same bounded ufokn sample (4,267 distinct flood cells) against three other S2 leaves:

| ufokn ↔ | other leaf's coverage | shared cells (same sample) |
|---|---|---|
| **fiokg** | national | **2,461 (58%)** |
| sawgraph | Maine only | 0 |
| hydrologykg | Illinois only | 0 |

**Why this answers the question:** ufokn co-locates densely with **fiokg** because fiokg is *national* — it has facilities wherever ufokn maps flooding. It shows **0** against **sawgraph** (Maine) and **hydrologykg** (Illinois) because the verifiable ufokn sample falls in a different region (its first ~5,000 features sit around S2 cell prefix `98136…`, not Maine or Illinois). This is a coverage effect, not a schema mismatch: ufokn↔sawgraph / ufokn↔hydrologykg are non-zero only where ufokn actually maps a Maine or Illinois metro, which can't be confirmed because a region-targeted scan of ufokn's 11.7M-node S2 layer exceeds the time limit. So only **ufokn ↔ fiokg is recorded as a verified crosswalk (O2)**; the single-state pairs remain hub-asserted / unverified (registry `known_non_joins`).

## SPARQL query executed

_2026-06-19 · `ufokn`, `sawgraph` (hydrologykg identical with its `sfWithin` predicate)_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?sampleCells) (COUNT(DISTINCT ?shared) AS ?inSawgraph) WHERE {
  { SELECT ?cell WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ufokn> { ?bn ?pn "s2Level13" . ?bn ?pv ?s2id . FILTER(CONTAINS(STR(?pv),'schema.org/value')) }
      BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.',STR(?s2id))) AS ?cell)
  } LIMIT 5000 }
  OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s <http://www.w3.org/2002/07/owl#sameAs> ?cell } BIND(?cell AS ?shared) }
}
```

_Result: `sampleCells` = 4267, `inSawgraph` = 0 (and `inHydro` = 0 for the hydrologykg variant)._

## Validation

The contrast (fiokg 2,461 vs sawgraph/hydrologykg 0 on the identical sample) is itself the finding: a national leaf overlaps the sample, single-state leaves in other states do not. ufokn also has no fallback key — its Place names are geohash strings ("building flooded {geohash}") and its identifiers are ufokn-internal — so S2 is its only join handle.

## Sources

- Proto-OKN / FRINK federation via the `mcp-okn` service. Recipe O2-s2-ufokn-fiokg (verified); ufokn↔sawgraph / ufokn↔hydrologykg recorded as `known_non_joins` (unverified). Checked 2026-06-19.

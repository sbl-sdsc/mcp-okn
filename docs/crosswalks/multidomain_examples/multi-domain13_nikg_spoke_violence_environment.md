# UC13 — Neighborhood Gun Violence × County Environmental Burden (NIKG + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Public safety / community gun violence (NIKG) × Environmental monitoring (SPOKE)
- **Knowledge graphs:** `nikg` <https://purl.org/okn/frink/kg/nikg> · `spoke-okn` <https://purl.org/okn/frink/kg/spoke-okn>
- **Shared join key:** county FIPS (NIKG census tracts `sfWithin` → `…administrativeRegion_USA_{FIPS5}`; SPOKE `/location/{FIPS5}`)

## Question
For the counties NIKG covers, how many **gun-violence-tracked neighborhoods** (census tracts flagged with the Gun Violence MeSH descriptor, D000091368) are there, and what is the **environmental burden** SPOKE records for that same county (distinct ambient pollutants detected)? This frames violence and environmental exposure as co-located neighborhood-health burdens (a syndemic view).

## Result

| county | gun-violence census tracts (NIKG) | ambient pollutants detected (SPOKE) |
| --- | --- | --- |
| Cook County (17031) | 801 | 154 |
| Philadelphia County (42101) | 361 | 142 |

## Why it answers the question
NIKG contributes the neighborhood gun-violence geography (census tracts flagged with the Gun Violence MeSH descriptor, rolled up to county), and SPOKE contributes the county's environmental-monitoring footprint (distinct chemical pollutants detected via `FOUNDIN_CfL`). Both Cook and Philadelphia — the two counties NIKG covers — carry substantial gun-violence-tracked neighborhood counts and broad ambient-pollutant burdens, the kind of overlapping structural disadvantage that environmental-justice and syndemic research examines. NIKG has no environmental data; SPOKE has no neighborhood-violence data; the county FIPS key joins them.

## Validation
According to PubMed, firearm/gun violence has well-documented **neighborhood and social-determinant** structure and is treated as a public-health problem with strong place-based clustering (e.g. firearm-violence neighborhood-determinants literature; 59 indexed articles on firearm violence × neighborhood social determinants). The co-location of high neighborhood gun-violence counts with substantial environmental burden in dense urban counties is consistent with that literature. (NIKG covers only Cook and Philadelphia counties, so the join is intentionally limited to those two; stated transparently.)

## SPARQL
```sparql
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?county ?gun_violence_tracts ?pollutants_detected WHERE {
  { SELECT ?fips (COUNT(DISTINCT ?ct) AS ?gun_violence_tracts) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nikg> {
        ?ct a <https://metadata.phila.gov/mesh_D000091368> ; kwgo:sfWithin ?reg .
        FILTER(STRSTARTS(STR(?reg),'https://metadata.phila.gov/kwgr_administrativeRegion_USA_')) }
      BIND(REPLACE(STR(?reg),'^.*_USA_([0-9]{5}).*$','$1') AS ?fips)
    } GROUP BY ?fips }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  { SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants_detected) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc rdfs:label ?county . OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc } }
    } GROUP BY ?loc ?county }
}
ORDER BY DESC(?gun_violence_tracts)
```

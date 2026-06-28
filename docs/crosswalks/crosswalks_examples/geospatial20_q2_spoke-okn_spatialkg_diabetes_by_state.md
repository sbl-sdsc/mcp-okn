# Adult diabetes prevalence rolled up to spatialkg-named states (with county count)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**

Using the same reified CDC PLACES prevalence data in SPOKE-OKN (`PREVALENCE_DpL`, place-level, tagged only by 2-letter state abbreviation), **crosswalk on STATE_FIPS (2-digit)** to spatialkg's administrative hierarchy: aggregate adult **diabetes** prevalence to the state, name each state, and report how many counties it contains (spatialkg `AdministrativeRegion_2` nodes). Diabetes shows one of the strongest documented geographic gradients in U.S. chronic disease — the "Diabetes Belt." Which states carry the highest aggregated burden?

---
🧠 **Assistant**

**Why the join is required.** As with CHD, spoke-okn's diabetes prevalence lives in place-level reified statements tagged only with a state abbreviation; it has no canonical state name and no internal administrative structure. spatialkg owns both the full state name (`AdministrativeRegion_1`) and the constituent counties (`AdministrativeRegion_2` via `administrativePartOf`). A ranked, named state diabetes table with county structure requires aggregating in spoke-okn and naming/structuring through spatialkg on the shared 2-digit FIPS.

**Join mechanics.** Identical pattern to Q1, swapping `short_question_text` to `"Diabetes"`: AVG `data_value` by `state_abbr` in a subquery, abbr→FIPS via the spoke-okn state node, then in spatialkg read the state `rdfs:label` and COUNT its `AdministrativeRegion_2` counties. **Both KGs populate every row:** the state name + county count come from spatialkg's admin hierarchy; the prevalence is the spoke value.

| state (spatialkg) | avg diabetes prevalence % (spoke) | spatialkg counties |
| --- | --- | --- |
| Mississippi | 14.17 | 164 |
| Louisiana | 12.84 | 128 |
| South Carolina | 12.80 | 92 |
| Georgia | 12.65 | 318 |
| New Mexico | 12.53 | 66 |
| Alabama | 12.46 | 134 |

**Why it answers the question.** Each row is a canonically-named spatialkg state carrying its admin-hierarchy county count and its spoke-derived mean adult diabetes prevalence, ranked by burden. Mississippi, Louisiana, South Carolina, Georgia and Alabama leading reproduces the well-known Southeastern "Diabetes Belt," demonstrating the join surfaces an epidemiologically coherent geography. (County counts include census county-equivalents; spatialkg covers the contiguous 48 + DC.)

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?sname ?avgPrev ?nCounties WHERE {
  {
    SELECT ?abbr (AVG(?dv) AS ?avgPrev) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?stmt rdf:predicate schema:PREVALENCE_DpL ;
              schema:short_question_text "Diabetes" ;
              schema:data_value ?dv ;
              schema:state_abbr ?abbr .
      }
    } GROUP BY ?abbr
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?sloc schema:abbr ?abbr .
    FILTER(REGEX(STR(?sloc),'/location/[0-9]{2}$'))
    BIND(REPLACE(STR(?sloc),'^.*/location/','') AS ?fips)
  }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
         <http://www.w3.org/2000/01/rdf-schema#label> ?sname .
    {
      SELECT ?reg2 (COUNT(DISTINCT ?cty) AS ?nCounties) WHERE {
        ?cty a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> ;
             <http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf> ?reg2 .
      } GROUP BY ?reg2
    }
    FILTER(?reg2 = ?reg)
  }
} ORDER BY DESC(?avgPrev) LIMIT 6
```

## Literature validation

According to PubMed, Liu et al. (2022, *World J Diabetes*) describe the application of spatial epidemiology to U.S. chronic disease and explicitly use it "to cluster and identify stroke belt and diabetes belt across the states and counties in the United States," confirming a strong, geographically clustered state/county gradient in diabetes burden. The spoke-okn ranking (Mississippi, Louisiana, South Carolina, Georgia, Alabama) recovers exactly this Southeastern Diabetes-Belt geography. [PMID:36051429](https://pubmed.ncbi.nlm.nih.gov/36051429/) · [DOI](https://doi.org/10.4239/wjd.v13.i7.584)

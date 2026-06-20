# UC3 — PFAS Sampling, EPA Facilities & Ambient Pollutants by County (SAWGraph + fiokg + SPOKE)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph> (PFAS contamination science — water/soil sampling)
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg> (EPA Facility Registry Service — industrial/regulatory)
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (environmental + health)

**Shared join key:** 5-digit county FIPS code (SAWGraph derives it from each sample point's Data Commons geoId).

## Conversation

👤 **User**

Research question (3-KG cross-domain join, shared key = county FIPS): Which counties have the most intensive PFAS sampling, and how does that PFAS-contamination burden line up with the number of EPA-regulated facilities and the diversity of ambient pollutants detected there? This integrates three independent domain knowledge graphs on the 5-digit county FIPS code: SAWGraph (PFAS contamination science — water/soil sampling) supplies the count of PFAS sample points per county (each sample point carries a Data Commons geoId whose first 5 digits are the county FIPS); fiokg (EPA Facility Registry Service — industrial/regulatory) supplies the number of EPA-regulated facilities per county; and spoke-okn (environmental + health) supplies the county name and the number of distinct ambient pollutants detected there (FOUNDIN_CfL).

> **Engineering note:** an initial design routed SAWGraph's S2 cells through spatialkg's administrative hierarchy, but the S2-cell federation (spatialkg's `connectedTo` has very high per-cell fan-out) timed out repeatedly. Resolving each SAWGraph sample point to its county directly via its Data Commons geoId made the three-graph join tractable.

---

🧠 **Assistant**

Result: 12 counties returned, all three layers populated. Highlights:
- Somerset County, ME (23025): 830 PFAS sample points; 146 ambient pollutants; 486 EPA facilities.
- Cumberland County, ME (23005): 671; 147; 2,549 facilities (Portland metro).
- Aroostook (23003): 615; 146; 823. Kennebec (23011): 592; 146; 1,012. Waldo (23027): 560. York (23031): 539; 149; 1,359.
- Washington County, MN (27163): 454 PFAS points; 185 pollutants; 5,906 EPA facilities — the Twin Cities county that includes 3M's Cottage Grove plant and the well-documented east-metro PFAS groundwater plume.
- Penobscot (23019), Androscoggin (23001), Washington ME (23029), Hancock (23009), and Pima County, AZ (04019: 147 PFAS points, 7,850 facilities) round out the list.

Why this answers the question and is plausible: the ranking is dominated by Maine, which runs one of the most aggressive statewide PFAS testing programs in the country (following discovery of contamination from land-applied sludge/biosolids), so Maine counties legitimately top a 'PFAS sampling intensity' ranking; and the single non-Maine standout, Washington County MN, is exactly where 3M manufactured PFAS and created a multi-decade drinking-water contamination case. Each county is simultaneously characterized by its EPA-regulated facility count (fiokg) and its ambient pollutant diversity (spoke-okn). No single graph supports this: SAWGraph has PFAS sampling but no facility registry or broader pollutant inventory; fiokg has facilities but no contamination measurements; spoke-okn has ambient pollutants but neither the PFAS sampling campaign nor the facility inventory. The county FIPS key fuses a contamination-science layer, an industrial-regulatory layer, and an environmental-monitoring layer.

Literature validation (Paperclip full-text corpus + PubMed): a national spatial analysis found that industrial sites, military fire-training areas, and wastewater-treatment plants predict PFAS detection frequency and concentration in U.S. drinking water — Hu et al., *Environ Sci Technol Lett* 2016 ([DOI](https://doi.org/10.1021/acs.estlett.6b00260)) — directly supporting the SAWGraph(PFAS)×fiokg(facilities) coupling that this query operationalizes. A 'presumptive contamination' framework maps tens of thousands of likely PFAS source sites, predominantly industrial facilities and airports (Salvatore et al., 2022, PMC9648201), and PFAS contamination is associated with industrial activity in U.S. water systems (Khanal & Elbakidze, 2024, PMC10994316). On the health side, according to PubMed, gestational PFOA exposure (a PFAS contaminant of drinking water) produces developmental and placental toxicity in mice — Blake et al., *Environ Health Perspect* 2020 ([DOI](https://doi.org/10.1289/EHP6233)). The facility-as-PFAS-source premise and the toxicity of the contaminant class are both supported, so the joined result is retained as valid.

## SPARQL query executed

```sparql
PREFIX kwgo: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>

SELECT ?county ?fips ?pfas_sample_points ?pollutants_detected (COUNT(DISTINCT ?facility) AS ?epa_facilities) WHERE {
  # sawgraph: PFAS sampling intensity per county (Data Commons geoId -> 5-digit county FIPS)
  {
    SELECT ?fips (COUNT(DISTINCT ?sp) AS ?pfas_sample_points) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?sp kwgo:sfWithin ?geo .
        FILTER(STRSTARTS(STR(?geo),'https://datacommons.org/browser/geoId/'))
        BIND(REPLACE(STR(?geo),'^.*/geoId/','') AS ?gid)
        FILTER(STRLEN(?gid)=10)
        BIND(SUBSTR(?gid,1,5) AS ?fips)
      }
    } GROUP BY ?fips ORDER BY DESC(?pfas_sample_points) LIMIT 12
  }
  # fiokg: EPA-regulated facilities operating in that same county
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?facility kwgo:sfWithin ?reg .
  }
  # spoke-okn: county name + number of distinct ambient pollutants detected there
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  {
    SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants_detected) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?loc rdfs:label ?county .
        OPTIONAL { ?cmp sp:FOUNDIN_CfL ?loc }
      }
    } GROUP BY ?loc ?county
  }
}
GROUP BY ?county ?fips ?pfas_sample_points ?pollutants_detected
ORDER BY DESC(?pfas_sample_points)
```

_12 rows — full result_

| county | fips | pfas_sample_points | pollutants_detected | epa_facilities |
| --- | --- | --- | --- | --- |
| Somerset County | 23025 | 830 | 146 | 486 |
| Cumberland County | 23005 | 671 | 147 | 2549 |
| Aroostook County | 23003 | 615 | 146 | 823 |
| Kennebec County | 23011 | 592 | 146 | 1012 |
| Waldo County | 23027 | 560 | 144 | 327 |
| York County | 23031 | 539 | 149 | 1359 |
| Washington County (MN) | 27163 | 454 | 185 | 5906 |
| Penobscot County | 23019 | 420 | 149 | 1424 |
| Androscoggin County | 23001 | 285 | 147 | 1139 |
| Washington County (ME) | 23029 | 192 | 148 | 513 |
| Hancock County | 23009 | 172 | 145 | 596 |
| Pima County (AZ) | 04019 | 147 | 148 | 7850 |

## Literature validation (Paperclip + PubMed)

- Industrial sites / fire-training areas / wastewater plants predict PFAS in U.S. drinking water — Hu XC, et al. *Environ Sci Technol Lett.* 2016. [DOI](https://doi.org/10.1021/acs.estlett.6b00260) (Paperclip PMC5062567)
- Presumptive PFAS contamination from industrial/airport sources — Salvatore D, et al. 2022. Paperclip PMC9648201
- PFAS contamination linked to industrial activity in U.S. water systems — Khanal NB, Elbakidze L. 2024. Paperclip PMC10994316
- Gestational PFOA exposure → developmental/placental toxicity — Blake BE, et al. *Environ Health Perspect.* 2020. [DOI](https://doi.org/10.1289/EHP6233) (PubMed)

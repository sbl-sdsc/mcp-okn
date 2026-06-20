# UC2 — Pollution, Environmental Monitoring & Federal Litigation by County (fiokg + SPOKE + SCALES)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `fiokg` — <https://purl.org/okn/frink/kg/fiokg> (EPA Facility Registry Service — industrial/regulatory)
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (environmental + health)
- `scales` — <https://purl.org/okn/frink/kg/scales> (federal judiciary)

**Shared join key:** 5-digit county FIPS code.

## Conversation

👤 **User**

Research question (3-KG cross-domain join, shared key = county FIPS): Which U.S. counties carry the heaviest EPA Toxic Release Inventory (TRI) facility burden, what chemical pollutants are actually detected in those counties, and what is their federal court caseload? This requires three knowledge graphs from three different domains, all joined on the 5-digit county FIPS code: fiokg (EPA Facility Registry Service — industrial/regulatory) supplies the count of TRI-reporting facilities per county; spoke-okn (environmental + health) supplies the chemical pollutants detected in each county via FOUNDIN_CfL; and scales (federal judiciary) supplies the number of federal court cases filed per county. fiokg ties facilities to counties via kwg:sfWithin → administrativeRegion.USA.{FIPS5}; spoke-okn county nodes are /location/{FIPS5}; scales links cases via scales:hasIdbCounty (numeric FIPS).

---

🧠 **Assistant**

Result: 15 counties returned, every one populated on all three layers. The top rows:
- Los Angeles County (06037): 1,525 TRI facilities; 171 distinct pollutants detected (e.g., toluene-2,4-diisocyanate); 15,439 federal cases.
- Cook County (17031): 1,285 TRI facilities; 154 pollutants (e.g., o-xylene); 113,188 federal cases (Northern District of Illinois).
- Harris County / Houston (48201): 650 TRI facilities; 182 pollutants (e.g., vinyl chloride); 6,086 federal cases.
- Maricopa (04013), Cuyahoga (39035), Orange CA (06059), Dallas (48113), Middlesex MA (25017), Santa Clara (06085), Wayne MI (26163), Milwaukee (55079), and others follow.

Why this answers the question and is plausible: the ranking is dominated by the largest industrial metropolitan counties, exactly where TRI-reporting facilities concentrate; the pollutants surfaced from spoke-okn are canonical TRI / criteria chemicals (vinyl chloride, xylene, selenium, phthalates such as bis(2-ethylhexyl) phthalate and dibutyl phthalate, the PAH pyrene, ozone, nitrogen oxides); and the federal-case counts track known court workloads (Cook County's Northern District of Illinois is one of the busiest in the nation at 113k cases). No single graph could produce this: fiokg knows facilities but not what is measured in the ambient environment or the legal context; spoke-okn knows detected pollutants but not the regulated-facility inventory or court activity; scales knows cases but nothing environmental. The county FIPS key fuses an industrial-regulatory layer, an environmental-monitoring layer, and a judicial layer into one environmental-justice screening table.

Literature validation (according to PubMed): proximity to TRI-reporting facilities is associated with worse chronic physical-health outcomes in an environmental-justice community in Galena Park, Texas (Harris County, one of the counties returned) — Sansom et al., Clim Risk Manag 2023 ([DOI](https://doi.org/10.1016/j.crm.2023.100507)). The example pollutant surfaced for Harris County, vinyl chloride, is causally related to liver angiosarcoma in pooled occupational cohorts of >20,000 workers — Bosetti et al., Eur J Cancer Prev 2003 ([DOI](https://doi.org/10.1097/00008469-200310000-00012)). Both the facility-proximity health premise and the toxicity of a specific detected pollutant are supported in the literature, so the joined result is retained as valid.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX epa: <http://w3id.org/fio/v1/epa-frs#>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX scales: <http://schemas.scales-okn.org/rdf/scales#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?county ?fips ?tri_facilities ?pollutants_detected ?example_pollutant ?federal_cases WHERE {
  # fiokg: EPA Toxic Release Inventory (TRI) facilities per county (industrial pollution burden)
  {
    SELECT ?fips (COUNT(DISTINCT ?f) AS ?tri_facilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?f epa:hasEnvironmentalInterest <http://w3id.org/fio/v1/epa-frs-data#d.EnvironmentalInterestType.Trireporter> ;
           kwg:sfWithin ?reg .
        FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
      }
      BIND(REPLACE(STR(?reg),'^.*administrativeRegion\\.USA\\.','') AS ?fips)
      FILTER(STRLEN(?fips)=5)
    } GROUP BY ?fips ORDER BY DESC(?tri_facilities) LIMIT 15
  }
  # spoke-okn: chemical pollutants actually detected in that county (environmental monitoring layer)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  {
    SELECT ?loc ?county (COUNT(DISTINCT ?cmp) AS ?pollutants_detected) (SAMPLE(?clab) AS ?example_pollutant) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?cmp sp:FOUNDIN_CfL ?loc .
        ?loc rdfs:label ?county .
        OPTIONAL { ?cmp rdfs:label ?clab }
      }
    } GROUP BY ?loc ?county
  }
  # scales: federal court caseload per county (judicial-activity layer)
  {
    SELECT ?fips2 (COUNT(DISTINCT ?x) AS ?federal_cases) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?x scales:hasIdbCounty ?c . FILTER(?c != 88888)
      }
      BIND(REPLACE(CONCAT('00000',STR(xsd:integer(?c))),'^.*(.{5})$','$1') AS ?fips2)
    } GROUP BY ?fips2
  }
  FILTER(?fips = ?fips2)
}
ORDER BY DESC(?tri_facilities)
```

_15 rows — full result_

| county | fips | tri_facilities | pollutants_detected | example_pollutant | federal_cases |
| --- | --- | --- | --- | --- | --- |
| Los Angeles County | 06037 | 1525 | 171 | 2,4-Diisocyanato-1-methylbenzene | 15439 |
| Cook County | 17031 | 1285 | 154 | O-Xylene | 113188 |
| Harris County | 48201 | 650 | 182 | Vinyl Chloride | 6086 |
| Maricopa County | 04013 | 593 | 153 | 2-Phenoxyethyl propionate | 6014 |
| Cuyahoga County | 39035 | 512 | 148 | Selenium | 2579 |
| Orange County | 06059 | 502 | 154 | octyl group | 3912 |
| Dallas County | 48113 | 427 | 149 | Selenium | 5355 |
| Middlesex County | 25017 | 397 | 151 | Selenium | 983 |
| Santa Clara County | 06085 | 363 | 153 | Bis(2-ethylhexyl) phthalate | 2274 |
| Wayne County | 26163 | 359 | 151 | Ozone | 3730 |
| Milwaukee County | 55079 | 319 | 150 | Pyrene | 1387 |
| Worcester County | 25027 | 313 | 148 | nitrogen oxide | 470 |
| Hamilton County | 39061 | 300 | 152 | Dibutyl Phthalate | 1026 |
| King County | 53033 | 288 | 146 | nitrogen oxide | 3006 |
| San Bernardino County | 06071 | 284 | 170 | Vinyl Chloride | 2656 |

## Literature validation (PubMed)

- TRI facility proximity → worse chronic health outcomes (Harris County, TX) — Sansom GT, et al. Clim Risk Manag. 2023. [DOI](https://doi.org/10.1016/j.crm.2023.100507)
- Vinyl chloride → liver angiosarcoma (occupational cohorts) — Bosetti C, et al. Eur J Cancer Prev. 2003. [DOI](https://doi.org/10.1097/00008469-200310000-00012)

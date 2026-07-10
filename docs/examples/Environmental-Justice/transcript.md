# Reproducible Transcript — Cumulative Environmental-Justice Burden (Proto-OKN)

- **Date:** 2026-07-06
- **Model:** claude-opus-4-8
- **Federation endpoint:** OKN federated SPARQL — `https://apps.okn.us/federation/sparql`
- **Method:** each knowledge graph was queried in its own named `GRAPH <…>` block; county rollups use verified join keys (county FIPS, S2 Level-13, ZIP5, NIBRS category). Extraction queries returned per-county aggregates written to CSV, then joined and analyzed in Python (pandas/scipy). All schema-probing queries were run in exploratory mode and are excluded here; only the finding-producing queries are listed.

## Knowledge graphs & versions used

| shortname | version | last updated | role |
|---|---|---|---|
| spoke-okn | v0.0.6 | 2026-03-16 | SDoH, SVI, CDC PLACES disease prevalence, geography |
| fiokg | v0.0.11 | 2026-03-18 | EPA FRS facilities, PFAS flag, enforcement records |
| scales | v0.0.22 | 2026-03-18 | federal court case volume; NIBRS offense categories |
| ruralkg | v0.2.7 | 2026-06-08 | RUCC, substance-use treatment, county population |
| sawgraph | v0.0.15 | 2026-03-16 | PFAS water-sample measurements |
| geoconnex | v0.0.4 | 2026-04-02 | hydrologic water-monitoring features |
| spatialkg | v0.0.6 | 2026-05-07 | S2 grid, county/state geometry, admin hierarchy |
| ufokn | v0.0.3 | 2026-03-19 | urban-flood-risk S2 cells (not resolved to county) |
| dreamkg | v0.0.5 | 2026-05-13 | Philadelphia homelessness/social services |
| nikg | v0.0.6 | 2026-03-16 | neighborhood incident / gun-violence counts |
| hydrologykg | v0.0.9 | 2026-03-16 | streams/wells (spatial hub support) |
| ubergraph | v0.0.2 | 2026-05-01 | ontology backbone |

## User request

> Study cumulative environmental-justice burden across U.S. counties using ONLY Proto-OKN knowledge graphs, organized by entity type; join spoke-okn/fiokg/scales/ruralkg/geoconnex/spatialkg on county FIPS, sawgraph via S2, dreamkg/ruralkg on ZIP, scales/ruralkg on NIBRS category; build a per-county cumulative-burden profile, rank counties by cross-source agreement, and correlate environmental/justice indicators with health/SDoH outcomes. Keep source/relationship/value/geo-level/evidence-kind per finding. Highlight the highest-burden/lowest-service set and flag uncertainties. Deliver report (html+md), findings CSV, visualizations, an OpenStreetMap choropleth, and this transcript.

## Assistant result (summary)

Integrated 12 Proto-OKN graphs into a county-level burden dataset for 3,158 counties (50 states + DC), 70,839 findings. Cross-source agreement distribution 0/1/2/3/4/5 = 301/874/1,197/635/147/4. Four maximal-burden counties: Williamsburg SC, Lea NM, Pike KY, Sullivan NY. Highest-burden/lowest-service set dominated by Great Plains reservation counties (Buffalo/Dewey/Corson SD, Blaine MT, Benson ND, Thurston NE) and TX/NM oil-and-border counties. PFAS Maine-only (16 counties, means to 1,192 ng/L). SVI is the dominant ecological correlate of adverse outcomes (diabetes r=0.71, poverty 0.70, food insecurity 0.70); rurality carries a moderate health penalty; per-capita facility density correlates negatively with disease (ecological artifact). Full narrative in `report.md`.

---

## SPARQL queries executed (canonical, one per layer)

### Q1 — EPA-regulated facilities per county (fiokg → county via `sfWithin`)
*Evidence kind: regulatory record · 3,107 counties · national total 3.6 M facility-county records.*
> Note: in fiokg a facility's `owl:sameAs` is self-referential (its own FRS IRI); the county link is `kwg:sfWithin` to `administrativeRegion.USA.{FIPS5}`.
```sparql
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX fio: <http://w3id.org/fio/v1/fio#>
SELECT ?fips (COUNT(DISTINCT ?f) AS ?epa_fac) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?f a fio:Facility ; kwg:sfWithin ?reg .
    FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
    FILTER(STRLEN(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]',''))=5)
  }
  BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q2 — EPA-PFAS-flagged facilities per county (fiokg)
*Evidence kind: regulatory record · 3,091 counties · national total 162,254.*
```sparql
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
SELECT ?fips (COUNT(DISTINCT ?f) AS ?pfas_fac) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?f a <http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility> ; kwg:sfWithin ?reg .
    FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
    FILTER(STRLEN(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]',''))=5)
  }
  BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q3 — Enforcement/compliance records per county (fiokg)
*Evidence kind: regulatory record · 3,052 counties · national total 643,975.*
```sparql
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX epa: <http://w3id.org/fio/v1/epa-frs#>
SELECT ?fips (COUNT(DISTINCT ?rec) AS ?enforce_records) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?f kwg:sfWithin ?reg .
    FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
    FILTER(STRLEN(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]',''))=5)
    ?f (epa:hasSupplementalRecord|epa:hasRecord|epa:hasMonitoringRecord) ?rec .
    ?rec a epa:EnforcementActivity .
  }
  BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q4 — Water-monitoring features per county (geoconnex → GNIS county)
*Evidence kind: monitoring feature · 3,222 counties · national total 964,897.*
```sparql
SELECT ?fips (COUNT(DISTINCT ?x) AS ?water_features) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?x <http://gnis-ld.org/lod/gnis/ontology/county> ?county . }
  BIND(REPLACE(STR(?county),'^.*/counties/([0-9]{5}).*$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q5 — PFAS water concentration per county (sawgraph → S2 → spatialkg county; Maine)
*Evidence kind: measured environmental sample · 16 Maine counties · 117,320 ng/L water measurements.*
> Spatial path: `ContaminantObservation → coso:observedAtSamplePoint → samplePoint → (me-egad associatedSite) → site → kwg:sfWithin → S2 cell`, then in spatialkg the S2 cell `kwg:sfWithin` its county; the numeric value is on the result via `coso:hasResult / coso:measurementValue` (filtered to unit NanoGM-PER-L). sawgraph's own `owl:sameAs → s2.level13.*` links are S2-cell self-references, not the sample→cell join.
```sparql
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX kwg:  <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips (AVG(xsd:double(?v)) AS ?pfas_mean_ngL) (MAX(xsd:double(?v)) AS ?pfas_max_ngL)
             (COUNT(?v) AS ?pfas_measurements) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?obs coso:hasResult ?r ; coso:observedAtSamplePoint ?sp .
    ?r coso:measurementValue ?v ; coso:measurementUnit ?u .
    ?sp ?assoc ?site . ?site kwg:sfWithin ?cell .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
    FILTER(CONTAINS(STR(?u),'NanoGM-PER-L')) FILTER(isNumeric(?v))
  }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell kwg:sfWithin ?county . ?county a kwg:AdministrativeRegion_2 . }
  BIND(REPLACE(STR(?county),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q6 — SDoH prevalence per county (spoke-okn reification; template shown for poverty)
*Evidence kind: survey/ranking indicator · 3,130–3,192 counties. Run once per label: `SAIPE_PCT_POV`, `ACS_PCT_LT_HS`, `Food insecurity (finding)`, `ACS_PCT_UNEMPLOY`, `ACS_PCT_UNINSURED`, `Social Vulnerability Index` (SVI value parsed from a compound string `idx(theme1,…)`).*
```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ss:   <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips (AVG(xsd:double(?value)) AS ?poverty_pct) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?stmt rdf:predicate ss:PREVALENCEIN_SpL ; rdf:subject ?sdoh ; rdf:object ?loc ; ss:value ?value .
    ?sdoh rdfs:label "SAIPE_PCT_POV" .
    FILTER(REGEX(STR(?loc),'/location/[0-9]{5}$'))
  }
  BIND(REPLACE(STR(?loc),'^.*/location/([0-9]{5})$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q7 — Chronic-disease prevalence per county (spoke-okn CDC PLACES place→county via `PARTOF_LpL`; template shown for diabetes)
*Evidence kind: survey/ranking indicator · 3,057 counties. Run once per label across 9 conditions (diabetes mellitus, coronary artery disease, asthma, chronic obstructive pulmonary disease, cerebrovascular disease, depressive disorder, obesity, arteriosclerosis, hypertension). Numeric prevalence is on `ss:data_value`.*
```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ss:   <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips (AVG(xsd:double(?dv)) AS ?diabetes_prev) (COUNT(DISTINCT ?place) AS ?nplaces) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?stmt rdf:predicate ss:PREVALENCE_DpL ; rdf:subject ?d ; rdf:object ?place ;
          ss:data_value_type "Age-adjusted prevalence" ; ss:data_value ?dv .
    ?d rdfs:label "diabetes mellitus" .
    ?p2 rdf:subject ?place ; rdf:predicate ss:PARTOF_LpL ; rdf:object ?county .
    FILTER(REGEX(STR(?county),'/location/[0-9]{5}$'))
  }
  BIND(REPLACE(STR(?county),'^.*/location/([0-9]{5})$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q8 — Federal court case volume per county (scales `hasIdbCounty`)
*Evidence kind: court record · 3,122 counties · national total 684,069 cases.*
```sparql
PREFIX scales: <http://schemas.scales-okn.org/rdf/scales#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips (COUNT(DISTINCT ?x) AS ?court_cases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/scales> { ?x scales:hasIdbCounty ?c . FILTER(?c != 88888) }
  BIND(REPLACE(CONCAT('00000',STR(xsd:integer(?c))),'^.*(.{5})$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q9 — National NIBRS offense-category charge volumes (scales)
*Evidence kind: court record · 111 offense categories (national only; disjoint from the court-county key).*
```sparql
PREFIX fbi: <http://fbi.gov/cjis/nibrs/2023.0/>
SELECT ?offense (COUNT(*) AS ?charges) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/scales> { ?ch fbi:OffenseUCRCode ?offense . }
} GROUP BY ?offense ORDER BY DESC(?charges)
```

### Q10 — Rural-Urban Continuum Code per county (ruralkg)
*Evidence kind: survey/ranking indicator · 3,221 counties (1,985 nonmetro, RUCC ≥ 4).*
```sparql
PREFIX st: <http://sail.ua.edu/ruralkg/settlementtype/>
SELECT ?fips ?rucc WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?s st:censusCounty ?reg ; st:hasRUCC ?r . ?r st:code ?rucc . }
  BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
}
```

### Q11 — Substance-use treatment providers per county (ruralkg × spoke-okn, ZIP→place→county 2-hop) — *auto-logged*
*Evidence kind: service listing · 2,144 counties · 8,820 providers mapped (of 9,037). ruralkg ZIPs are normalized (strip non-digits, left-pad to 5) before matching spoke-okn ZIP nodes; the 2-hop `PARTOF_LpL` resolves ZIP→place→county.*
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ss: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX tr: <http://sail.ua.edu/ruralkg/treatment/>
SELECT ?fips (COUNT(DISTINCT ?p) AS ?sud_providers) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?p a tr:TreatmentProvider ; ?zp ?zipraw . FILTER(STRENDS(STR(?zp),'schema.org/postalCode'))
  }
  BIND(REPLACE(CONCAT('00000',REPLACE(STR(?zipraw),'[^0-9]','')),'^.*([0-9]{5})$','$1') AS ?zip5)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?zip5 . FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]'))
    ?s1 rdf:subject ?loc ; rdf:predicate ss:PARTOF_LpL ; rdf:object ?place .
    ?s2 rdf:subject ?place ; rdf:predicate ss:PARTOF_LpL ; rdf:object ?county .
    FILTER(REGEX(STR(?county),'/location/[0-9]{5}$'))
  }
  BIND(REPLACE(STR(?county),'^.*/location/([0-9]{5})$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q12 — County population (ruralkg `st:population`, MAX across years) — *auto-logged*
*Used for per-capita normalization · 3,234 counties.*
```sparql
PREFIX st: <http://sail.ua.edu/ruralkg/settlementtype/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?fips (MAX(xsd:integer(?popraw)) AS ?pop) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?s st:censusCounty ?reg ; st:population ?popraw . }
  BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
} GROUP BY ?fips
```

### Q13 — County names (spoke-okn) — *auto-logged* · 3,195 counties
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?fips ?name WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?name . FILTER(REGEX(STR(?loc),'/location/[0-9]{5}$'))
  }
  BIND(REPLACE(STR(?loc),'^.*/location/([0-9]{5})$','$1') AS ?fips)
}
```

### Q14 — Neighborhood gun-violence counts per county (nikg; 2 counties)
*Evidence kind: incident record. Incidents link `schema.org/location → Location → kwg:sfWithin → administrativeRegion.USA.{FIPS}`; gun violence flagged by `is_fatal`. Results — Cook 17031: 89,367 incidents / 1,019 shootings / 208 fatal; Philadelphia 42101: 16,282 / 15,205 / 3,163.*
```sparql
SELECT ?fips (COUNT(DISTINCT ?i) AS ?incidents) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/nikg> {
    ?i ?locp ?loc . FILTER(STRENDS(STR(?locp),'schema.org/location'))
    ?loc <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?reg .
    FILTER(CONTAINS(STR(?reg),'administrativeRegion'))
  }
  BIND(REPLACE(STR(?reg),'^.*[_.]([0-9]{5})$','$1') AS ?fips)
} GROUP BY ?fips
```

---

## Analysis pipeline (post-extraction, deterministic)

1. Clean FIPS to 5-digit; drop state aggregates and sentinels; restrict national ranking to the 50 states + DC.
2. Per-capita rates for count stressors using ruralkg population.
3. National percentile ranks → worst-tertile burden flags for facilities, SVI, court, rurality (RUCC ≥ 4), and service scarcity.
4. Cross-source agreement (0–5) = flag count; composite burden index = mean of the 5 stressor percentiles.
5. Pearson correlations (scipy) between exposure/vulnerability predictors and 14 health/SDoH outcomes across counties (ecological).
6. Outputs: `master_county.csv`, `findings_long.csv` (70,839 rows), `burden_ranking.csv`, `correlations.csv`, `corr_matrix.csv`, four figures, and `choropleth_burden.html`.

*Reproduce by running each query above against the OKN federation (versions in the table), then the pipeline in `build_master.py` / `make_figs.py` / `make_map.py`.*

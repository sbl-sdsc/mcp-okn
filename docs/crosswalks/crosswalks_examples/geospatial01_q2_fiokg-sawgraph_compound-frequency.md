# geo01_q2_fiokg-sawgraph_compound-frequency

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>

## Conversation

👤 **User**

Geospatial crosswalk fiokg × sawgraph, shared key = S2 Level-13 cell. Q2: Across all S2 cells that contain an EPA PFAS-relevant facility, which individual PFAS compounds are detected most often in co-located water samples, and at what maximum concentration?

---

🧠 **Assistant**

This aggregates the same facility↔measurement join over every co-occupied cell to profile *which* PFAS dominate near regulated PFAS-relevant facilities. It requires both graphs: the EPA-PFAS-Facility flag and cell location come only from fiokg; the per-compound concentrations come only from sawgraph.

Results (per compound: number of distinct co-located cells, max ng/L; SUM/aggregate parameters excluded):

| PFAS compound | Co-located cells | Max (ng/L) |
|---|---|---|
| Perfluorobutanoic acid (PFBA) | 85 | 12,700 |
| Perfluorooctanesulfonic acid (PFOS) | 80 | 20,000 |
| Perfluorooctanoic acid (PFOA) | 76 | 8,030 |
| Perfluorooctane sulfonic acid (alt label) | 70 | 20,000 |
| Perfluorohexanoic acid (PFHxA) | 55 | 28,100 |
| Perfluoroheptanoic acid (PFHpA) | 55 | 9,630 |

Why these rows answer the question: each row is a distinct PFAS compound with the count of S2 cells where it co-occurs with an EPA PFAS-relevant facility and its peak concentration there. The profile is dominated by the legacy long-chain perfluoroalkyl acids PFOS and PFOA plus short-chain PFBA/PFHxA — the canonical mixture found near PFAS sources.

Literature validation (strict). According to PubMed, Kulkarni et al. 2025 (Water Research) report that at AFFF-impacted sites PFOS, PFOA and PFHxS account for ~99% of groundwater screening-level exceedances, with short-chain PFBA/PFHxA/PFBS also consistently present — matching this compound ranking ([DOI](https://doi.org/10.1016/j.watres.2025.124124)). da Silva et al. 2026 (ACS Omega) likewise detect the PFOS/PFOA/PFHxS suite plus short-chain congeners in AFFF-impacted groundwater ([DOI](https://doi.org/10.1021/acsomega.5c08713)). **Validated.**

## SPARQL queries executed

#### Query 1

_`fiokg`, `sawgraph` · 12 rows (showing first 6)_

```sparql
SELECT ?subLabel (COUNT(DISTINCT ?cell) AS ?cells) (MAX(?val) AS ?maxNgL) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a <http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility> ;
         <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?cell .
    FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.'))
  }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?sawcell <http://www.w3.org/2002/07/owl#sameAs> ?cell .
    ?sp <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?sawcell .
    ?obs <http://w3id.org/coso/v1/contaminoso#observedAtSamplePoint> ?sp ;
         <http://w3id.org/coso/v1/contaminoso#ofSubstance> ?sub ;
         <http://w3id.org/coso/v1/contaminoso#hasResult> ?r .
    ?r <http://w3id.org/coso/v1/contaminoso#measurementValue> ?val .
    ?sub <http://www.w3.org/2000/01/rdf-schema#label> ?subLabel .
    FILTER(isNumeric(?val))
    FILTER(!CONTAINS(STR(?subLabel),'SUM'))
  }
} GROUP BY ?subLabel ORDER BY DESC(?cells) LIMIT 12
```

| subLabel | cells | maxNgL |
| --- | --- | --- |
| Perfluorobutanoic acid | 85 | 12700.0 |
| Perfluorooctanesulfonic acid | 80 | 20000.0 |
| TOTAL PFOA AND PFOS | 77 | 24930.0 |
| Perfluorooctanoic acid | 76 | 8030.0 |
| PERFLUOROOCTANE SULFONIC ACID | 70 | 20000.0 |
| Perfluorohexanoic acid | 55 | 28100.0 |

**Literature:** PubMed — Kulkarni 2025 Water Res [10.1016/j.watres.2025.124124](https://doi.org/10.1016/j.watres.2025.124124); da Silva 2026 ACS Omega [10.1021/acsomega.5c08713](https://doi.org/10.1021/acsomega.5c08713).

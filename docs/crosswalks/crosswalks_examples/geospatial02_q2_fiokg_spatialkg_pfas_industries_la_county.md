# geo02_q2_fiokg_spatialkg_pfas_industries_la_county

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>

## Conversation
👤 **User**
Joining on the S2 Level-13 grid, within a single named county (Los Angeles County, California) what NAICS industries do the EPA-flagged potential-PFAS facilities belong to? This tells us which industrial sectors drive PFAS exposure risk locally.

---
🧠 **Assistant**
This requires the join because the *county name* "Los Angeles County, California" lives only in spatialkg (as a GADM `AdministrativeRegion_2` label over S2 cells), while the *industry classification* of each PFAS facility lives only in fiokg (the `fio#ofIndustry` link to a NAICS node with an `rdfs:label`). To restrict facilities to LA County I must translate the county name → its S2 cells (spatialkg) → match those cell IRIs against fiokg facilities, then break the facilities down by their NAICS label.

The mechanics: I anchor on spatialkg's LA County, gather its `s2.level13` cells via `kwg:sfWithin`, hand each cell to fiokg's `EPA-PFAS-Facility` nodes (`kwg:sfWithin ?cell`), follow `fio#ofIndustry → ?industry → rdfs:label`, and `COUNT(DISTINCT)` facilities per industry label.

| industry | facilities |
| --- | --- |
| Manufacturing | 356 |
| Fabricated Metal Product Manufacturing | 103 |
| Chemical Manufacturing | 94 |
| Coating, Engraving, Heat Treating, and Allied Activities | 85 |
| Electroplating, Plating, Polishing, Anodizing, and Coloring | 76 |

These rows answer the question: within the named county, the PFAS-relevant facilities cluster in metal-finishing, electroplating, chemical and general manufacturing — precisely the sectors that use PFAS surfactants (mist suppressants in plating baths, fluoropolymer processing).

Literature validation (strict): According to PubMed, these are documented PFAS point-source industries. Joerss et al. (2020, *Environmental Pollution*) identified the electroplating industry as a specific PFAS source in river water (PFOS-replacement 6:2 FTSA fingerprint from electroplating discharges) and fluoropolymer/chemical manufacturing as dominant emitters ([DOI](https://doi.org/10.1016/j.envpol.2020.115567)). The human health stakes of such PFAS exposure are established by Wang et al. (2021, *Environment International*) ([DOI](https://doi.org/10.1016/j.envint.2021.106408)). The specific industry breakdown returned here (electroplating/plating, chemical manufacturing, metal coating) matches the source sectors named in that literature. **Validated.**

## SPARQL queries executed
#### Query 1
_`fiokg`, `spatialkg` · 10 rows (showing first 5)_
```sparql
SELECT ?indLabel (COUNT(DISTINCT ?fac) AS ?nfac) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?kwgcell <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?county .
    ?county a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> ;
            <http://www.w3.org/2000/01/rdf-schema#label> "Los Angeles County, California" .
    FILTER(STRSTARTS(STR(?county),'http://stko-kwg'))
  }
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a <http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility> ;
         <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?kwgcell ;
         <http://w3id.org/fio/v1/fio#ofIndustry> ?industry .
    ?industry <http://www.w3.org/2000/01/rdf-schema#label> ?indLabel .
  }
}
GROUP BY ?indLabel ORDER BY DESC(?nfac) LIMIT 10
```
| indLabel | nfac |
| --- | --- |
| Manufacturing | 356 |
| Fabricated Metal Product Manufacturing | 103 |
| Chemical Manufacturing | 94 |
| Coating, Engraving, Heat Treating, and Allied Activities | 85 |
| Electroplating, Plating, Polishing, Anodizing, and Coloring | 76 |

**Literature:** PubMed — Joerss et al. 2020, *Environmental Pollution* [DOI](https://doi.org/10.1016/j.envpol.2020.115567); Wang et al. 2021, *Environment International* [DOI](https://doi.org/10.1016/j.envint.2021.106408).

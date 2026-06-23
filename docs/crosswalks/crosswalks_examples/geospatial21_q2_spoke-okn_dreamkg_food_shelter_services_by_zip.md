# geo21_q2_spoke-okn_dreamkg_food_shelter_services_by_zip

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>

## Conversation
👤 **User**

Beyond mental health, DreamKG tags services as Food or Shelter. **Crosswalk on ZIP5:** Which Philadelphia (PA) standard residential ZIPs — validated via SPOKE-OKN — concentrate the most **food + shelter** services? Food insecurity and unstable housing are tightly coupled health risks for people experiencing homelessness.

---
🧠 **Assistant**

**Why the join is required.** DreamKG holds the food/shelter services and their ZIP, but cannot confirm the ZIP is a valid PA standard residential ZIP. SPOKE-OKN supplies the administrative validation via its `state = "PA"` and `zipcode_type = "STANDARD"` ZIP nodes. Counting food/shelter services restricted to verified standard PA residential ZIPs requires both graphs joined on the bare ZIP string.

**Join mechanics.** Shared key = bare 5-digit ZIP literal. spoke-okn supplies `state = "PA"` AND `zipcode_type = "STANDARD"` ZIP nodes whose `rdfs:label` is the ZIP; dreamkg `schema:postalCode` matches that literal with `category` filtered to `/service_type/Shelter` or `/service_type/Food`; COUNT distinct services per ZIP.

| ZIP | food + shelter services |
| --- | --- |
| 19104 | 12 |
| 19143 | 11 |
| 19139 | 10 |
| 19123 | 9 |
| 19144 | 8 |

The rows answer the question by ranking validated standard PA ZIPs on combined food/shelter service density — the ZIPs (19104, 19143, 19139 in West/Southwest Philadelphia) where these coupled basic-needs services cluster.

**Literature validation (strict).** According to PubMed, Loftus et al. (2020, *Public Health Nutr*) — a scoping review of food insecurity among homeless adults — found a consistent association between food insecurity and adverse mental-health conditions (especially depression and symptom severity) in this population, establishing that food and housing/shelter supports address tightly coupled health risks [DOI](https://doi.org/10.1017/S1368980020001998). This corroborates the public-health rationale for mapping where DreamKG's food + shelter services concentrate. **Validated** (homelessness, food insecurity & health).

## SPARQL queries executed
#### Query 1
_`spoke-okn`, `dreamkg` · 30+ rows (showing first 5)_
```sparql
SELECT ?zip (COUNT(DISTINCT ?svc) AS ?nShelterFood) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "PA" ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/zipcode_type> "STANDARD" .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
  }
  GRAPH <https://purl.org/okn/frink/kg/dreamkg> {
    ?svc <http://schema.org/postalCode> ?zip ;
         <http://schema.org/category> ?cat .
    FILTER(CONTAINS(STR(?cat),'/service_type/Shelter') || CONTAINS(STR(?cat),'/service_type/Food'))
  }
} GROUP BY ?zip ORDER BY DESC(?nShelterFood) LIMIT 10
```
| zip | nShelterFood |
| --- | --- |
| 19104 | 12 |
| 19143 | 11 |
| 19139 | 10 |
| 19123 | 9 |
| 19144 | 8 |

**Literature:** PubMed — Loftus EI et al. 2020, *Public Health Nutr* [DOI](https://doi.org/10.1017/S1368980020001998).

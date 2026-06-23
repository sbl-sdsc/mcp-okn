# geo22_q1_spoke-okn_ruralkg_treatment_providers_by_zip

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>

## Conversation
👤 **User**

RuralKG catalogs rural mental-health / substance-use **treatment providers**, each carrying a `schema:postalCode` (bare 5-digit ZIP) but no validation of whether the ZIP is a real standard residential ZIP in a given state. SPOKE-OKN holds U.S. ZIP administrative nodes with state context. **Crosswalk on ZIP5:** Within Alabama, which residential ZIP codes (validated via SPOKE-OKN) have the most behavioral-health treatment providers in RuralKG?

---
🧠 **Assistant**

**Why the join is required.** RuralKG gives the providers and their ZIP, but cannot place a ZIP in a state or confirm it is a residential ZIP. SPOKE-OKN supplies the ZIP→state mapping (`state = "AL"`). Counting providers by validated Alabama ZIP requires joining the two graphs on the bare 5-digit ZIP string.

**Join mechanics.** Shared key = the bare ZIP literal. spoke-okn selects `/location/AL-…` ZIP nodes (`state = "AL"`) whose `rdfs:label` is the ZIP. RuralKG stores postalCode under the non-canonical `https://schema.org/postalCode` form (which FRINK canonicalizes), so I bind the predicate as a variable and match scheme-free with `STRENDS(...,'schema.org/postalCode')`, restricting to `TreatmentProvider`; then COUNT distinct providers per ZIP.

| ZIP | treatment providers |
| --- | --- |
| 35650 | 4 |
| 35802 | 4 |
| 36732 | 4 |
| 36049 | 3 |
| 36301 | 3 |

The rows answer the question: each Alabama-validated ZIP is ranked by RuralKG provider count, surfacing where behavioral-health treatment capacity concentrates (and, by absence, where rural gaps lie).

**Literature validation (strict).** According to PubMed, Heitkamp & Fox (2022, *J Addict Nurs*) review the documented barriers to substance-use intervention and treatment in rural communities — limited accessibility, availability, affordability, and acceptability, plus provider shortages — establishing that the geographic distribution of treatment providers (exactly what this join maps) is a central rural-health-disparity concern [DOI](https://doi.org/10.1097/JAN.0000000000000483). **Validated** (rural behavioral-health access disparities).

## SPARQL queries executed
#### Query 1
_`spoke-okn`, `ruralkg` · 100+ rows (showing first 5)_
```sparql
SELECT ?zip (COUNT(DISTINCT ?prov) AS ?nProviders) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "AL" .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
  }
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?prov a <http://sail.ua.edu/ruralkg/treatment/TreatmentProvider> ; ?pp ?zip .
    FILTER(STRENDS(STR(?pp),'schema.org/postalCode'))
  }
} GROUP BY ?zip ORDER BY DESC(?nProviders) LIMIT 10
```
| zip | nProviders |
| --- | --- |
| 35650 | 4 |
| 35802 | 4 |
| 36732 | 4 |
| 36049 | 3 |
| 36301 | 3 |

**Literature:** PubMed — Heitkamp TL, Fox LF 2022, *J Addict Nurs* [DOI](https://doi.org/10.1097/JAN.0000000000000483).

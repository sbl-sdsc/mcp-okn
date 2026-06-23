# geo22_q2_spoke-okn_ruralkg_telehealth_providers_by_zip

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>

## Conversation
👤 **User**

RuralKG records which specific services each treatment provider offers, including `MHS_TELE` (telemedicine/telehealth therapy) — a key strategy for overcoming distance barriers in rural behavioral-health care. **Crosswalk on ZIP5:** Within Mississippi, which residential ZIP codes (validated via SPOKE-OKN) have the most providers offering telehealth therapy?

---
🧠 **Assistant**

**Why the join is required.** RuralKG identifies which providers offer telehealth and their ZIP, but cannot confirm the ZIP is a Mississippi residential ZIP. SPOKE-OKN supplies the ZIP→state mapping. Counting telehealth-offering providers by validated MS ZIP requires both graphs joined on the bare ZIP string.

**Join mechanics.** Shared key = bare ZIP literal. spoke-okn selects MS ZIP nodes (`state = "MS"`); RuralKG selects `TreatmentProvider`s that `providesService MHS_TELE`, matching `schema.org/postalCode` scheme-free; COUNT distinct providers per ZIP.

| ZIP | telehealth providers |
| --- | --- |
| 39648 | 7 |
| 39216 | 5 |
| 39232 | 3 |
| 39401 | 3 |
| 38863 | 2 |

The rows answer the question by ranking validated Mississippi ZIPs on telehealth-provider availability — the specific service modality most relevant to bridging rural access gaps. 39648 (McComb) and 39216 (Jackson medical district) leading reflects where telehealth-capable behavioral-health infrastructure sits.

**Literature validation (strict).** According to PubMed, Heitkamp & Fox (2022, *J Addict Nurs*) explicitly recommend "expanding the use of technology to deliver telehealth services" as a core, evidence-based strategy to address the disparities rural residents face in securing substance-use and mental-health treatment [DOI](https://doi.org/10.1097/JAN.0000000000000483). This directly corroborates the health relevance of mapping where rural telehealth-capable providers are concentrated. **Validated** (rural telehealth & behavioral-health access).

## SPARQL queries executed
#### Query 1
_`spoke-okn`, `ruralkg` · 40+ rows (showing first 5)_
```sparql
SELECT ?zip (COUNT(DISTINCT ?prov) AS ?nTele) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "MS" .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
  }
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?prov a <http://sail.ua.edu/ruralkg/treatment/TreatmentProvider> ;
          <http://sail.ua.edu/ruralkg/treatment/providesService> <http://sail.ua.edu/ruralkg/treatment/MHS_TELE> ;
          ?pp ?zip .
    FILTER(STRENDS(STR(?pp),'schema.org/postalCode'))
  }
} GROUP BY ?zip ORDER BY DESC(?nTele) LIMIT 10
```
| zip | nTele |
| --- | --- |
| 39648 | 7 |
| 39216 | 5 |
| 39232 | 3 |
| 39401 | 3 |
| 38863 | 2 |

**Literature:** PubMed — Heitkamp TL, Fox LF 2022, *J Addict Nurs* [DOI](https://doi.org/10.1097/JAN.0000000000000483).

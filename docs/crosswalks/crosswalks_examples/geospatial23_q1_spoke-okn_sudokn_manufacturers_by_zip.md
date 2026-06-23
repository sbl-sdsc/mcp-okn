# geo23_q1_spoke-okn_sudokn_manufacturers_by_zip

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>

## Conversation
👤 **User**

SUDOKN catalogs U.S. small/medium manufacturers (NAICS codes, process/material capabilities), each geosite carrying a `hasZipcodeValue` (bare ZIP) but no state context or residential-ZIP validation. SPOKE-OKN holds U.S. ZIP administrative nodes with state. **Crosswalk on ZIP5:** Within Ohio, which residential ZIP codes (validated via SPOKE-OKN) host the greatest concentration of manufacturers? Manufacturing density is a determinant of community-level occupational and environmental health exposure.

---
🧠 **Assistant**

**Why the join is required.** SUDOKN gives manufacturer geosites and their ZIP, but cannot place a ZIP in a state. SPOKE-OKN supplies the ZIP→state mapping (`state = "OH"`). Counting manufacturers by validated Ohio ZIP requires joining on the bare 5-digit ZIP string.

**Join mechanics.** Shared key = the bare ZIP literal. spoke-okn selects `/location/OH-…` ZIP nodes (`state = "OH"`); in SUDOKN, `company → organizationLocatedIn → geosite → hasZipcodeValue` yields the same ZIP literal; COUNT distinct companies per ZIP.

| ZIP | manufacturers |
| --- | --- |
| 44060 | 40 |
| 43001 | 39 |
| 44094 | 32 |
| 44035 | 24 |
| 45414 | 20 |

The rows answer the question by ranking validated Ohio ZIPs on manufacturer concentration (Mentor 44060, Willoughby 44094 in the Cleveland industrial corridor), identifying communities with the densest manufacturing footprint.

**Literature validation (strict).** According to PubMed, Bau et al. (2019, *J Occup Environ Hyg*) characterize airborne particle and hexavalent-chromium emissions from metal manufacturing processes and the resulting occupational exposure, documenting that manufacturing operations are a quantifiable source of health-relevant airborne contaminants and that proximity/density drives exposure risk [DOI](https://doi.org/10.1080/15459624.2019.1696969). This corroborates treating manufacturer density (what this join maps) as an occupational/community-health exposure determinant. **Validated** (manufacturing & occupational/community-health exposure).

## SPARQL queries executed
#### Query 1
_`spoke-okn`, `sudokn` · 200+ rows (showing first 5)_
```sparql
SELECT ?zip (COUNT(DISTINCT ?comp) AS ?nMfrs) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "OH" .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
  }
  GRAPH <https://purl.org/okn/frink/kg/sudokn> {
    ?comp <http://asu.edu/semantics/SUDOKN/organizationLocatedIn> ?geo .
    ?geo <http://asu.edu/semantics/SUDOKN/hasZipcodeValue> ?zip .
  }
} GROUP BY ?zip ORDER BY DESC(?nMfrs) LIMIT 10
```
| zip | nMfrs |
| --- | --- |
| 44060 | 40 |
| 43001 | 39 |
| 44094 | 32 |
| 44035 | 24 |
| 45414 | 20 |

**Literature:** PubMed — Bau S et al. 2019, *J Occup Environ Hyg* [DOI](https://doi.org/10.1080/15459624.2019.1696969).

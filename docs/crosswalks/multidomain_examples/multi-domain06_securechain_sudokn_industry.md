# UC6 — Software Supply-Chain Participants × Small/Medium Manufacturers by Industry (SecureChainKG + SUDOKN)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Cybersecurity / software supply chain × Advanced manufacturing (small/medium manufacturers)
- **Knowledge graphs:** `securechainkg` <https://purl.org/okn/frink/kg/securechainkg> · `sudokn` <https://purl.org/okn/frink/kg/sudokn>
- **Shared join key:** NAICS industry code (3-digit subsector)

## Question
For each manufacturing industry, how do the **software/hardware supply-chain participants** tracked by SecureChainKG (with their products and 28,559 catalogued vulnerabilities) line up against the **small/medium manufacturers (SMMs)** catalogued by SUDOKN (with their physical process capabilities and quality certifications such as ISO 9001, AS9100, ITAR)? This connects the digital supply-chain risk surface to the physical manufacturing base in the same industry.

## Result (top 12 subsectors by SUDOKN manufacturers)

| NAICS subsector | Industry | SecureChain participants | SUDOKN manufacturers |
| --- | --- | --- | --- |
| 332 | Fabricated Metal Product Manufacturing | 5,809 | 15,954 |
| 333 | Machinery Manufacturing | 223 | 38 |
| 323 | Printing and Related Support Activities | 163 | 38 |
| 326 | Plastics and Rubber Products Manufacturing | 86 | 35 |
| 339 | Miscellaneous Manufacturing | 439 | 32 |
| 325 | Chemical Manufacturing | 199 | 24 |
| 321 | Wood Product Manufacturing | 104 | 21 |
| 313 | Textile Mills | 20 | 21 |
| 311 | Food Manufacturing | 97 | 21 |
| 315 | Apparel Manufacturing | 23 | 19 |
| 337 | Furniture and Related Product Manufacturing | 84 | 19 |
| 335 | Electrical Equipment, Appliance & Component Mfg | 121 | 18 |

## Why it answers the question
Each subsector is populated on both sides: SecureChainKG participant counts (software supply-chain footprint) and SUDOKN SMM counts (physical manufacturing base, which carry capabilities such as CNC machining, additive manufacturing, welding, and certifications AS9100/ITAR for aerospace-defense work). Fabricated Metal (332) dominates both. The two graphs share no company instance IRIs — SecureChain mints DHS/D&B-sourced company nodes, SUDOKN mints its own — so they can only meet on the authoritative NAICS classification, exactly the cross-domain join demonstrated here.

## Validation
Integration validated **by construction** on the NAICS standard (verified `securechainkg↔sudokn` crosswalk, 35 shared codes, and the industry-sector crosswalk, 58 shared sectors). A manufacturing/cyber-supply-chain data-integration use case; biomedical literature validation is not applicable. Correctness rests on the shared authoritative classification and the verified crosswalk.

## SPARQL
```sparql
PREFIX sudokn: <http://asu.edu/semantics/SUDOKN/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?subsector ?subLabel ?securechain_participants ?smm_count WHERE {
  { SELECT ?sub (COUNT(DISTINCT ?p) AS ?securechain_participants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?p sudokn:hasPrimaryNAICSClassifier ?z . }
      BIND(SUBSTR(REPLACE(STR(?z),'^.*/naics-([0-9]+)\\.0-inst$','$1'),1,3) AS ?sub)
    } GROUP BY ?sub }
  { SELECT ?sub (COUNT(DISTINCT ?m) AS ?smm_count) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?m sudokn:hasPrimaryNAICSClassifier ?z . }
      BIND(SUBSTR(REPLACE(STR(?z),'^.*/NAICS%20([0-9]+)-individual$','$1'),1,3) AS ?sub)
    } GROUP BY ?sub }
  FILTER(STRLEN(?sub)=3)
  BIND(?sub AS ?subsector)
  BIND(IRI(CONCAT('http://w3id.org/fio/v1/naics#NAICS-',?sub)) AS ?subIRI)
  OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?subIRI rdfs:label ?subLabel } }
}
ORDER BY DESC(?smm_count) LIMIT 12
```

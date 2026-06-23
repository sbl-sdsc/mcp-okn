# UC5 — EPA Facilities × Software Supply-Chain Participants by Industry (fiokg + SecureChainKG)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Environmental regulation (EPA Facility Registry) × Cybersecurity / software supply chain
- **Knowledge graphs:** `fiokg` <https://purl.org/okn/frink/kg/fiokg> · `securechainkg` <https://purl.org/okn/frink/kg/securechainkg>
- **Shared join key:** NAICS industry code (joined at the 3-digit subsector level; fiokg uses `naics#NAICS-{code}`, SecureChain uses `SUDOKN/naics-{code}.0-inst`)

## Question
Which industries host **both** EPA-regulated facilities (an environmental-compliance footprint) **and** software/hardware supply-chain participants (a cyber-supply-chain risk surface)? SecureChainKG additionally catalogs 28,559 software vulnerabilities across 803,769 products and 13,921 manufacturer-participants; aligning its participants to EPA's facility inventory by NAICS shows where physical industrial regulation and digital supply-chain exposure coincide.

## Result (top 12 manufacturing subsectors by SecureChain participants)

| NAICS subsector | Industry | EPA facilities (fiokg) | SecureChain participants |
| --- | --- | --- | --- |
| 332 | Fabricated Metal Product Manufacturing | 43,317 | 5,809 |
| 339 | Miscellaneous Manufacturing | 15,262 | 439 |
| 334 | Computer and Electronic Product Manufacturing | 9,137 | 308 |
| 333 | Machinery Manufacturing | 19,992 | 223 |
| 325 | Chemical Manufacturing | 31,341 | 199 |
| 336 | Transportation Equipment Manufacturing | 20,984 | 170 |
| 323 | Printing and Related Support Activities | 10,346 | 163 |
| 335 | Electrical Equipment, Appliance & Component Mfg | 6,492 | 121 |
| 327 | Nonmetallic Mineral Product Manufacturing | 27,400 | 109 |
| 321 | Wood Product Manufacturing | 16,367 | 104 |
| 311 | Food Manufacturing | 21,489 | 97 |
| 326 | Plastics and Rubber Products Manufacturing | 17,239 | 86 |

## Why it answers the question
Every returned subsector is simultaneously an EPA-regulated industry (facility counts from fiokg) and a populated node of the software supply-chain graph (participant counts from SecureChainKG). Computer & Electronic Product Manufacturing (334) and Fabricated Metal (332) — both heavy on embedded/industrial software — show the largest cyber-supply-chain footprints, while still carrying thousands of environmentally regulated facilities. Neither graph can produce this alone: fiokg has no notion of software products or vulnerabilities, and SecureChainKG has no environmental-facility inventory. The authoritative NAICS classification is the only bridge.

## Validation
Integration validated **by construction** on the standard NAICS classification (the verified `fiokg↔securechainkg` crosswalk, 301 shared codes, complete containment of SecureChain's industry codes in fiokg). This is an industrial/cyber data-integration use case rather than a biomedical claim, so PubMed/Paperclip literature validation is not applicable; correctness rests on the shared authoritative coding standard and the verified crosswalk counts.

## SPARQL
```sparql
PREFIX epa: <http://w3id.org/fio/v1/epa-frs#>
PREFIX sudokn: <http://asu.edu/semantics/SUDOKN/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?subsector ?subLabel ?fiokg_facilities ?securechain_participants WHERE {
  { SELECT ?sub (COUNT(DISTINCT ?p) AS ?securechain_participants) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?p sudokn:hasPrimaryNAICSClassifier ?z . }
      BIND(SUBSTR(REPLACE(STR(?z),'^.*/naics-([0-9]+)\\.0-inst$','$1'),1,3) AS ?sub)
    } GROUP BY ?sub }
  { SELECT ?sub (COUNT(DISTINCT ?f) AS ?fiokg_facilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f epa:ofPrimaryIndustry ?ind . FILTER(STRSTARTS(STR(?ind),'http://w3id.org/fio/v1/naics#NAICS-')) }
      BIND(SUBSTR(REPLACE(STR(?ind),'^.*naics#NAICS-([0-9]+)$','$1'),1,3) AS ?sub)
    } GROUP BY ?sub }
  FILTER(STRLEN(?sub)=3)
  BIND(?sub AS ?subsector)
  BIND(IRI(CONCAT('http://w3id.org/fio/v1/naics#NAICS-',?sub)) AS ?subIRI)
  OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?subIRI rdfs:label ?subLabel } }
}
ORDER BY DESC(?securechain_participants) LIMIT 12
```

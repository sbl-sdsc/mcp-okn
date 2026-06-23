# I1-Q1 — Industries shared by SecureChain supply-chain firms and EPA-regulated facilities (fiokg × securechainkg)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Crosswalk:** securechainkg ↔ fiokg (verified, 301 shared NAICS codes)
- **Shared identifier:** NAICS 6-digit industry code (fiokg `naics#NAICS-{code}` ↔ securechainkg `SUDOKN/naics-{code}.0-inst`)

## Knowledge graphs used

- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>

## Conversation

👤 **User**

Which manufacturing industries (NAICS 6-digit) contain BOTH SecureChain supply-chain manufacturers AND EPA-regulated physical facilities, and which of those shared industries carry the largest EPA-regulated facility footprint?

---

🧠 **Assistant**

Joining SecureChain manufacturers (`hasPrimaryNAICSClassifier`) to EPA FRS facilities (`ofPrimaryIndustry`/`ofSecondaryIndustry`) on the shared 6-digit NAICS code returns the industries present in both graphs, ranked by EPA facility count. Ready-Mix Concrete (327320) leads with 14,261 EPA facilities, followed by Asphalt Paving (324121, 11,943) and the metal/plastics fabrication cluster. Machine Shops (332710) carry the largest *supply-chain* footprint — 1,624 SecureChain manufacturers alongside 3,202 EPA facilities. The result genuinely requires the join: fiokg has no notion of supply-chain firms and securechainkg has no environmental facility inventory; only the shared NAICS classification links them.

#### Query — Industries shared by SecureChain manufacturers and EPA FRS facilities, ranked by EPA facility count

```sparql
SELECT ?code ?nSecureChainMfrs ?nEpaFacilities WHERE {
  {
    SELECT ?code (COUNT(DISTINCT ?a) AS ?nSecureChainMfrs) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/securechainkg> {
        ?a <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?sn .
      }
      BIND(REPLACE(STR(?sn),'^.*/naics-([0-9]+)\\.0-inst$','$1') AS ?code)
    } GROUP BY ?code
  }
  {
    SELECT ?code (COUNT(DISTINCT ?f) AS ?nEpaFacilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?f <http://w3id.org/fio/v1/epa-frs#ofPrimaryIndustry>|<http://w3id.org/fio/v1/epa-frs#ofSecondaryIndustry> ?ind .
      }
      BIND(REPLACE(STR(?ind),'^.*naics#NAICS-([0-9]+)$','$1') AS ?code)
    } GROUP BY ?code
  }
}
ORDER BY DESC(?nEpaFacilities) LIMIT 15
```

_15 row(s) returned_

| NAICS | industry | SecureChain mfrs | EPA facilities |
| --- | --- | --- | --- |
| 327320 | Ready-Mix Concrete Mfg | 19 | 14261 |
| 324121 | Asphalt Paving Mixture & Block Mfg | 10 | 11943 |
| 339999 | All Other Misc. Mfg | 128 | 7095 |
| 326199 | All Other Plastics Product Mfg | 56 | 6780 |
| 332813 | Electroplating, Plating, Polishing, Anodizing & Coloring | 311 | 6753 |
| 332312 | Fabricated Structural Metal Mfg | 235 | 4559 |
| 332999 | All Other Misc. Fabricated Metal Product Mfg | 500 | 4385 |
| 321113 | Sawmills | 2 | 4255 |
| 332812 | Metal Coating, Engraving & Allied Services | 166 | 4146 |
| 323111 | Commercial Printing (ex Screen/Books) | 126 | 3643 |
| 325998 | All Other Misc. Chemical Product & Prep Mfg | 17 | 3297 |
| 332710 | Machine Shops | 1624 | 3202 |
| 311119 | Other Animal Food Mfg | 6 | 3134 |
| 325211 | Plastics Material & Resin Mfg | 9 | 3090 |
| 337110 | Wood Kitchen Cabinet & Countertop Mfg | 28 | 2928 |

## Validation

Join correct by construction on the authoritative NAICS standard and the hand-verified `fiokg↔securechainkg` crosswalk (301 shared codes, complete containment of SecureChain's codes in fiokg). EPA classifies all FRS facilities by NAICS (EPA ECHO/FRS). The dominance of Machine Shops (NAICS 332710) as the most populous manufacturing industry is corroborated by BLS/IBISWorld (~13,000–22,000 U.S. establishments). Web sources: EPA ECHO/FRS facility classification; IBISWorld/BLS NAICS 332710.

# I4-Q1 — Industry sectors served by manufacturers in both KGs (securechainkg × sudokn, industry sector)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Crosswalk:** securechainkg ↔ sudokn (verified, 58 shared SUDOKN industry sectors)
- **Shared identifier:** SUDOKN industry sector (`suppliesToIndustry`)

## Knowledge graphs used

- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>

## Conversation

👤 **User**

Which downstream industry sectors (aerospace, automotive, defense, healthcare, etc.) are SUPPLIED BY manufacturers in BOTH the SUDOKN and SecureChain graphs, and how many suppliers does each graph contribute per sector? (Joins on the `suppliesToIndustry` sector key rather than NAICS.)

---

🧠 **Assistant**

Using the `suppliesToIndustry` sector relation, the two graphs overlap on 58 of ~60 sectors. Aerospace is the largest shared market (6,963 SUDOKN suppliers, 4,407 SecureChain suppliers), followed by Automotive (7,358 / 4,321), Healthcare (5,749 / 3,973), Construction (7,768 / 3,392) and Defense (4,166 / 2,499). This is a different join from the NAICS crosswalks — it links the two supplier bases by the *market they serve* rather than their own industry classification, which only the shared sector vocabulary makes possible.

#### Query — Supplier counts per shared industry sector, SUDOKN vs SecureChain

```sparql
SELECT ?sec ?nSudoknMfrs ?nSecureChainMfrs WHERE {
  {
    SELECT ?sec (COUNT(DISTINCT ?b) AS ?nSudoknMfrs) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sudokn> {
        ?b <http://asu.edu/semantics/SUDOKN/suppliesToIndustry> ?di .
      }
      BIND(LCASE(REPLACE(REPLACE(STR(?di),'^.*/SUDOKN/(.*)-industry-individual$','$1'),'%20','')) AS ?sec)
    } GROUP BY ?sec
  }
  {
    SELECT ?sec (COUNT(DISTINCT ?a) AS ?nSecureChainMfrs) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/securechainkg> {
        ?a <http://asu.edu/semantics/SUDOKN/suppliesToIndustry> ?si .
      }
      BIND(LCASE(REPLACE(STR(?si),'^.*/SUDOKN/(.*)-inst$','$1')) AS ?sec)
    } GROUP BY ?sec
  }
}
ORDER BY DESC(?nSecureChainMfrs) LIMIT 20
```

_20 row(s) returned_

| sector | SUDOKN suppliers | SecureChain suppliers |
| --- | --- | --- |
| aerospace | 6963 | 4407 |
| automotive | 7358 | 4321 |
| healthcare | 5749 | 3973 |
| construction | 7768 | 3392 |
| defense | 4166 | 2499 |
| energy | 4155 | 2294 |
| agriculture | 3562 | 2083 |
| oilandgas | 3402 | 1837 |
| food | 3063 | 1792 |
| transportation | 3370 | 1699 |
| military | 2930 | 1651 |
| machineryandequipment | 1702 | 1559 |
| marineandshipbuilding | 2395 | 1155 |
| chemicalandpetrochemical | 2118 | 1061 |
| mining | 1741 | 1047 |
| electronicproduct | 1504 | 937 |
| metalproduction | 1518 | 887 |
| pharmaceutical | 1705 | 815 |
| sportsandleisure | 1455 | 778 |
| telecommunications | 1224 | 755 |

## Validation

Join correct by construction on the shared SUDOKN industry-sector vocabulary and the verified `securechainkg↔sudokn` sector crosswalk (58 shared sectors). The ranking (aerospace, automotive, healthcare, defense leading U.S. advanced-manufacturing supply chains) is consistent with national manufacturing supply-chain structure. Industrial integration; not a biomedical claim.

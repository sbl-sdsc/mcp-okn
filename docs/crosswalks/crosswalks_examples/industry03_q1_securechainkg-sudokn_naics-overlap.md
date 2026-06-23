# I3-Q1 — Manufacturer overlap between SUDOKN and SecureChain by industry (securechainkg × sudokn, NAICS)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Crosswalk:** securechainkg ↔ sudokn (verified, 35 shared NAICS codes)
- **Shared identifier:** NAICS 6-digit industry code

## Knowledge graphs used

- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>

## Conversation

👤 **User**

Which NAICS manufacturing industries are represented in BOTH the SUDOKN small/medium-manufacturer directory and the SecureChain supply-chain graph, and how many distinct manufacturers does each graph contribute per industry? (This measures how well the two independent manufacturing datasets overlap by sector.)

---

🧠 **Assistant**

Joining the two manufacturer directories on the shared 6-digit NAICS code shows strong overlap across the fabricated-metal sector. Machine Shops (332710) dominate both: 4,869 SUDOKN SMMs and 1,624 SecureChain manufacturers. Sheet Metal Work (332322, 1,263 / 535), All Other Misc. Fabricated Metal (332999, 570 / 500), and Electroplating (332813, 634 / 311) follow. The two graphs mint disjoint company IRIs (a direct firm-level join is zero), so the NAICS classification is the only bridge — which is exactly what makes this a true crosswalk query.

#### Query — Manufacturer counts per shared NAICS industry, SUDOKN vs SecureChain

```sparql
SELECT ?code ?nSudoknMfrs ?nSecureChainMfrs WHERE {
  {
    SELECT ?code (COUNT(DISTINCT ?b) AS ?nSudoknMfrs) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sudokn> {
        ?b <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?dn .
      }
      BIND(REPLACE(STR(?dn),'^.*NAICS%20([0-9]+)-individual$','$1') AS ?code)
    } GROUP BY ?code
  }
  {
    SELECT ?code (COUNT(DISTINCT ?a) AS ?nSecureChainMfrs) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/securechainkg> {
        ?a <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?sn .
      }
      BIND(REPLACE(STR(?sn),'^.*/naics-([0-9]+)\\.0-inst$','$1') AS ?code)
    } GROUP BY ?code
  }
}
ORDER BY DESC(?nSecureChainMfrs) LIMIT 20
```

_20 row(s) returned_

| NAICS | industry | SUDOKN SMMs | SecureChain mfrs |
| --- | --- | --- | --- |
| 332710 | Machine Shops | 4869 | 1624 |
| 332322 | Sheet Metal Work Mfg | 1263 | 535 |
| 332999 | All Other Misc. Fabricated Metal Product Mfg | 570 | 500 |
| 332813 | Electroplating, Plating, Polishing, Anodizing & Coloring | 634 | 311 |
| 332312 | Fabricated Structural Metal Mfg | 2208 | 235 |
| 332618 | Other Fabricated Wire Product Mfg | 360 | 199 |
| 332321 | Metal Window & Door Mfg | 330 | 193 |
| 332812 | Metal Coating, Engraving & Allied Services | 870 | 166 |
| 332323 | Ornamental & Architectural Metal Work Mfg | 512 | 128 |
| 332919 | Other Metal Valve & Pipe Fitting Mfg | 136 | 125 |
| 332996 | Fabricated Pipe & Pipe Fitting Mfg | 200 | 119 |
| 332311 | Prefab Metal Building & Component Mfg | 414 | 119 |
| 332510 | Hardware Mfg | 272 | 116 |
| 332722 | Bolt/Nut/Screw/Rivet/Washer Mfg | 148 | 100 |
| 332410 | Power Boiler & Heat Exchanger Mfg | 106 | 83 |
| 332420 | Metal Tank (Heavy Gauge) Mfg | 254 | 80 |
| 332811 | Metal Heat Treating | 165 | 80 |
| 332911 | Industrial Valve Mfg | 176 | 74 |
| 332912 | Fluid Power Valve & Hose Fitting Mfg | 90 | 71 |
| 332111 | Iron & Steel Forging | 193 | 69 |

## Validation

Join correct by construction on NAICS and the verified `securechainkg↔sudokn` crosswalk (35 shared codes; company-level IRIs are disjoint, confirming the join must be at the industry-classification level). Both datasets' concentration in NAICS 332 (fabricated metal / machine shops) is consistent with their published scope. Industrial data-integration; not a biomedical claim.

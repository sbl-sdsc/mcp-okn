# I2-Q2 — SUDOKN manufacturers operating in EPA PFAS-handling industries (fiokg × sudokn)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Crosswalk:** fiokg ↔ sudokn (verified, 64 shared NAICS codes)
- **Shared identifier:** NAICS 6-digit industry code (fiokg PFAS facilities via `fio#ofIndustry`)

## Knowledge graphs used

- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>

## Conversation

👤 **User**

Which NAICS industries contain SUDOKN small/medium manufacturers AND EPA facilities flagged as potentially PFAS-handling (EPA-PFAS-Facility)? In other words, which SMMs in the SUDOKN directory operate in PFAS-exposed industrial sectors?

---

🧠 **Assistant**

Joining EPA `EPA-PFAS-Facility` industries to SUDOKN SMMs on NAICS pinpoints the metal-finishing sectors where small/medium manufacturers operate amid intense PFAS-handling activity. Electroplating/Plating/Anodizing (332813) shows 3,777 PFAS facilities alongside 634 SUDOKN SMMs; Metal Coating & Engraving (332812) shows 2,181 PFAS facilities and 870 SMMs. Machine Shops (332710) and Fabricated Structural Metal (332312) have large SMM counts but comparatively fewer PFAS facilities, indicating lower PFAS exposure. This targeting requires both the PFAS flag (fiokg) and the SMM directory (sudokn).

#### Query — EPA PFAS-handling facilities and SUDOKN SMMs sharing a NAICS industry

```sparql
SELECT ?code ?nPfasFacilities ?nSudoknMfrs WHERE {
  {
    SELECT ?code (COUNT(DISTINCT ?f) AS ?nPfasFacilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/fiokg> {
        ?f a <http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility> ;
           <http://w3id.org/fio/v1/fio#ofIndustry> ?ind .
      }
      BIND(REPLACE(STR(?ind),'^.*naics#NAICS-([0-9]+)$','$1') AS ?code)
      FILTER(STRLEN(?code) = 6)
    } GROUP BY ?code
  }
  {
    SELECT ?code (COUNT(DISTINCT ?b) AS ?nSudoknMfrs) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sudokn> {
        ?b <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?dn .
      }
      BIND(REPLACE(STR(?dn),'^.*NAICS%20([0-9]+)-individual$','$1') AS ?code)
    } GROUP BY ?code
  }
}
ORDER BY DESC(?nSudoknMfrs) LIMIT 15
```

_15 row(s) returned_

| NAICS | industry | PFAS facilities | SUDOKN SMMs |
| --- | --- | --- | --- |
| 332710 | Machine Shops | 145 | 4869 |
| 332312 | Fabricated Structural Metal Mfg | 237 | 2208 |
| 332322 | Sheet Metal Work Mfg | 192 | 1263 |
| 332812 | Metal Coating, Engraving & Allied Services | 2181 | 870 |
| 332813 | Electroplating, Plating, Polishing, Anodizing & Coloring | 3777 | 634 |
| 332119 | Metal Crown/Closure & Stamping | 68 | 600 |
| 332999 | All Other Misc. Fabricated Metal Product Mfg | 2086 | 570 |
| 332323 | Ornamental & Architectural Metal Work Mfg | 55 | 512 |
| 332311 | Prefab Metal Building & Component Mfg | 27 | 414 |
| 332618 | Other Fabricated Wire Product Mfg | 107 | 360 |
| 332321 | Metal Window & Door Mfg | 80 | 330 |
| 332216 | Saw Blade & Handtool Mfg | 29 | 281 |
| 332510 | Hardware Mfg | 84 | 272 |
| 332313 | Plate Work Mfg | 95 | 259 |
| 332420 | Metal Tank (Heavy Gauge) Mfg | 47 | 254 |

## Validation

Literature-validated. EPA PFAS Analytic Tools flag PFAS-handling industries by NAICS (~120,000 facilities; EPA ECHO). The two leading SMM-PFAS overlap industries — electroplating (332813) and metal coating (332812) — are exactly the metal-finishing sectors documented to use PFAS mist suppressants in plating baths (EPA fume-suppressant sampling; NESHAP PFOS phase-out). According to PubMed, Göen et al., *Chemosphere* 2023 found elevated PFOS in chrome-plating workers from mist-suppressant use ([DOI](https://doi.org/10.1016/j.chemosphere.2023.140613)) — direct occupational-health relevance for SMMs in these NAICS codes.

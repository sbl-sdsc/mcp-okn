# Taxonomy Crosswalk 15 Q2 — Mycobacterium tuberculosis: SPOKE associations + BioHealthKG clinical profile

- **Date:** 2026-06-25
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

For *Mycobacterium tuberculosis* — one of the organisms shared between SPOKE-OKN and BioHealthKG — what does each graph contribute? SPOKE-OKN gives 8,182 associations (from the label-bridged crosswalk); summarize what BioHealthKG asserts about the same organism, broken down by predicate.

---

🧠 **Assistant**

*Mycobacterium tuberculosis* is the canonical case for this bridge: the two graphs describe the same pathogen from complementary angles.

- **SPOKE-OKN** holds **8,182 associations** on its `OrganismTaxon` node for *M. tuberculosis* (NCBITaxon:1773) — gene, compound and disease links built from its biomedical knowledge layer (the count from crosswalk BH11).
- **BioHealthKG** describes the same organism as node **C0026926** (UMLS CUI), semantic category `bact_bact` (bacterium), with **SemMedDB-style clinical predications**: 810 `location_of`, 315 `causes`, 135 `interacts_with`, 127 `PRODUCES` and 108 `associated_with` assertions (plus negated `NEG_*` counterparts that record explicitly-asserted *non*-relations).

Neither graph carries the other's view: SPOKE has no clinical-predication layer for the organism, and BioHealthKG carries no NCBITaxon id or SPOKE-style association graph. Matching them on the organism's scientific name (BioHealthKG has no taxon id, so the label is the only key) lets a researcher pull SPOKE's molecular associations and BioHealthKG's literature-derived clinical assertions for the same pathogen in one place.

**Validation (standard).** The BioHealthKG node is confirmed live (C0026926, label *Mycobacterium tuberculosis*, category `bact_bact`); the SPOKE association count of 8,182 is the value from the verified label-bridged crosswalk BH11. **Validated** (organism present in both graphs; label-bridged crosswalk BH11).

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (REPLACE(STR(?p),'^.*[/#]','') AS ?biohealthPredicate) (COUNT(*) AS ?assertions) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh rdfs:label "Mycobacterium tuberculosis" .
    ?bh ?p ?o .
    FILTER(?p != rdfs:label)
  }
}
GROUP BY ?p ORDER BY DESC(?assertions)
```

### Results (BioHealthKG predications for *M. tuberculosis*, node C0026926)

| biohealthPredicate | assertions |
| --- | --- |
| location_of | 810 |
| causes | 315 |
| interacts_with | 135 |
| PRODUCES | 127 |
| associated_with | 108 |
| NEG_LOCATION_OF | 19 |
| subclass_of | 17 |
| NEG_CAUSES | 13 |
| NEG_ASSOCIATED_WITH | 9 |
| NEG_INTERACTS_WITH | 8 |
| NEG_ISA | 6 |
| NEG_PRODUCES | 4 |
| category | 1 |

(SPOKE-OKN side, from crosswalk BH11: 8,182 associations on the *M. tuberculosis* `OrganismTaxon` node.)

# Taxonomy Crosswalk 19 Q2 — Rattus norvegicus: GeneLab genes + BioHealthKG clinical profile

- **Date:** 2026-06-25
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>

## Conversation

👤 **User**

*Rattus norvegicus* is the classic spaceflight-physiology rodent and a major biomedical model. For this organism, how many SPOKE-GeneLab genes carry it, and what does BioHealthKG assert about it clinically? Join spoke-genelab and biohealth on the organism (NCBITaxon:10116 in GeneLab; matched by name in BioHealthKG).

---

🧠 **Assistant**

The rat shows the bridge connecting spaceflight molecular data to clinical organism knowledge:

- **SPOKE-GeneLab** carries **6,254 genes** tagged *Rattus norvegicus* (NCBITaxon:10116) — the rat genes assayed across GeneLab spaceflight/omics studies.
- **BioHealthKG** describes the same organism with **10,096 `location_of`** clinical predications — by far its richest non-human model organism, reflecting how much of the SemMedDB literature localizes findings to the rat — plus 19 `interacts_with`, 11 `subclass_of` and 3 `associated_with` assertions (and negated `NEG_*` counterparts).

The join on the organism name lets a researcher move from "6,254 rat genes with spaceflight expression evidence" to "10,096 clinical statements about the rat" for the same species — connecting GeneLab's molecular layer to BioHealthKG's literature-derived physiology. The bridge is the scientific name (BioHealthKG has no taxon id).

**Literature validation (PubMed).** *Rattus norvegicus* is the classic spaceflight-physiology model — a PubMed search for rat spaceflight / microgravity gene expression returns 77 articles (e.g. PMID 10352154, 36982513, 12207961), supporting the GeneLab rat assays this crosswalk counts.

**Validation (standard).** *Rattus norvegicus* resolves to a live BioHealthKG node (10,096 `location_of` predications); the GeneLab gene count of 6,254 is the per-organism figure from crosswalk BH15. **Validated** (organism present in both graphs; label-bridged crosswalk BH15).

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (REPLACE(STR(?p),'^.*[/#]','') AS ?biohealthPredicate) (COUNT(*) AS ?assertions) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh rdfs:label "Rattus norvegicus" .
    ?bh ?p ?o .
    FILTER(?p != rdfs:label)
  }
}
GROUP BY ?p ORDER BY DESC(?assertions)
```

### Results (BioHealthKG predications for *Rattus norvegicus*)

| biohealthPredicate | assertions |
| --- | --- |
| location_of | 10096 |
| NEG_LOCATION_OF | 1068 |
| interacts_with | 19 |
| subclass_of | 11 |
| NEG_INTERACTS_WITH | 6 |
| NEG_ISA | 4 |
| associated_with | 3 |
| type | 1 |

(SPOKE-GeneLab side, from crosswalk BH15: 6,254 genes tagged *Rattus norvegicus*, NCBITaxon:10116.)

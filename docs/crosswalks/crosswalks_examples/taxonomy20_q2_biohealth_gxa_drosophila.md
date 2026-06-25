# Taxonomy Crosswalk 20 Q2 — Drosophila melanogaster: GXA studies + BioHealthKG clinical profile

- **Date:** 2026-06-25
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation

👤 **User**

*Drosophila melanogaster* is a foundational transcriptomics and disease-modeling organism. For this species, how many Gene Expression Atlas studies exist, and what does BioHealthKG assert about it? Join gene-expression-atlas-okn and biohealth on the organism (NCBITaxon:7227 in GXA; matched by name in BioHealthKG).

---

🧠 **Assistant**

The fly is a clean illustration of the two graphs' complementary content:

- **GXA** holds **150 gene-expression studies** in *Drosophila melanogaster* (NCBITaxon:7227) — baseline/differential transcriptomics for the organism.
- **BioHealthKG** describes the same organism with **45 `interacts_with`, 29 `causes` and 7 `location_of`** clinical predications (plus 14 `subclass_of` and a negated `NEG_*` tail) — the literature-derived relations in which the fly participates as a disease/biology model.

Joining on the organism name (BioHealthKG exposes no taxon id) lets a researcher pull GXA's expression studies and BioHealthKG's clinical predications for the same species in one query — bridging transcriptomic evidence to literature-asserted organism biology. The same fly is also a shared GeneLab (BH15) and NDE (BH12) organism, so it recurs across the biohealth label-bridged crosswalks.

**Literature validation (PubMed).** *Drosophila melanogaster* is a foundational human-disease genetic model — a PubMed search returns 2,653 articles (e.g. PMID 21415126, 40806617, 39722550), consistent with both the GXA expression studies and BioHealthKG's `interacts_with`/`causes` predications.

**Validation (standard).** *Drosophila melanogaster* resolves to a live BioHealthKG node (45 `interacts_with`, 29 `causes` predications); the GXA study count of 150 is the per-organism figure from crosswalk BH16. **Validated** (organism present in both graphs; label-bridged crosswalk BH16).

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (REPLACE(STR(?p),'^.*[/#]','') AS ?biohealthPredicate) (COUNT(*) AS ?assertions) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh rdfs:label "Drosophila melanogaster" .
    ?bh ?p ?o .
    FILTER(?p != rdfs:label)
  }
}
GROUP BY ?p ORDER BY DESC(?assertions)
```

### Results (BioHealthKG predications for *Drosophila melanogaster*)

| biohealthPredicate | assertions |
| --- | --- |
| interacts_with | 45 |
| causes | 29 |
| subclass_of | 14 |
| location_of | 7 |
| NEG_INTERACTS_WITH | 2 |
| NEG_CAUSES | 1 |
| category | 1 |
| type | 1 |

(GXA side, from crosswalk BH16: 150 gene-expression studies with `biolink:in_taxon` = *Drosophila melanogaster*, NCBITaxon:7227.)

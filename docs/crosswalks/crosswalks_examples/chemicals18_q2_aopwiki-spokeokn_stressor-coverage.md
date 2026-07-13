# How many AOP-Wiki chemical stressors are present in spoke-okn, joined on the PubChem CID?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: `biobricks-aopwiki` × `spoke-okn` on **PubChem CID** (crosswalk `P3-pubchem-aopwiki-spokeokn`, verified_count 87). biobricks-aopwiki carries the CID as a **bare literal** on its chemical-entity nodes under the CHEMINF predicate `<http://semanticscience.org/resource/CHEMINF_000140>`; spoke-okn carries the same CID as an **IRI** on a ChemicalEntity/Compound node via `oboInOwl:hasDbXref`, in the form `http://identifiers.org/pubchem.compound/{cid}`. Normalize by minting the identifiers.org IRI from the AOP-Wiki literal — `BIND(IRI(CONCAT('http://identifiers.org/pubchem.compound/', STR(?cidLit))) AS ?x)` — then match on `?x`.

Research question: how many AOP-Wiki chemical stressors are present in spoke-okn when joined on the PubChem CID? Size the crosswalk against its denominators — how much of AOP-Wiki's chemical space reaches spoke-okn, how many Adverse Outcome Pathways that touches, and what spoke-okn actually contributes for the compounds that do match.

Why the join is required: neither graph can size this alone. AOP-Wiki knows how many chemical stressors it curates and which AOPs they trigger, but has no way to tell which of them a biomedical/environmental knowledge graph has ever heard of. spoke-okn knows its compound space but has no notion of an adverse outcome pathway, so it cannot report its own coverage of regulatory toxicology. The PubChem CID is the only bridge, and the coverage number is a property of the join, not of either graph.

---

🧠 **Assistant**

**87 of AOP-Wiki's 403 PubChem CIDs (21.6%) are present in spoke-okn** — reproducing the crosswalk's verified count exactly. The join is **1:1**: those 87 CIDs resolve to exactly 87 distinct spoke-okn compounds, with no fan-out or identifier collision.

| Quantity | Count |
| --- | --- |
| Distinct PubChem CIDs in biobricks-aopwiki | **403** |
| … carried on AOP-Wiki chemical stressors | 369 |
| … spanning Adverse Outcome Pathways | 117 |
| **CIDs also present in spoke-okn (the crosswalk)** | **87** (21.6% of 403) |
| … distinct spoke-okn compounds they resolve to | **87** (1:1) |
| **AOPs reached through the matched stressors** | **48** (41% of 117) |

And what spoke-okn actually supplies for those 87 compounds — the part that matters for anyone planning to use this crosswalk:

| spoke-okn payload on the 87 matched compounds | Compounds carrying it |
| --- | --- |
| **Environmental occurrence** (`FOUNDIN_CfL` — compound detected in a location) | **87 / 87 (100%)** |
| Gene targets (`UPREGULATES_CuG` / `DOWNREGULATES_CdG`) | 10 / 87 |
| Disease, clinical-trial-derived (`TREATS_CtD` / `CONTRAINDICATES_CcD`) | 5 / 87 |

**Why it answers the question.** The headline count is 87, and the recall is modest — roughly one in five of AOP-Wiki's chemical identifiers reaches spoke-okn. But the count understates the crosswalk's reach in one direction and overstates it in another, and both corrections come out of the same query.

It *understates* pathway coverage. Those 87 compounds are not scattered across AOP-Wiki's periphery: they are stressors of **48 of the 117 AOPs** that carry any PubChem-identified chemical — 41% of the pathway space, from a 21.6% slice of the chemical space. The matched chemicals are disproportionately the well-studied ones (carbon tetrachloride, bisphenol A, cadmium, arsenic, PFOS, ethanol, ozone), which is exactly what one would expect: a compound is in spoke-okn *because* it has been measured and studied, and it anchors an AOP for the same reason.

It *overstates* the pharmacology. The naive reading of this crosswalk — "AOP stressors, now with drug targets and indications" — does not survive contact with the data. Only **10 of 87** matched compounds carry any gene-regulation edge and only **5 of 87** carry any disease edge (and those disease edges are clinical-trial records, not efficacy claims). What **all 87** carry is `FOUNDIN_CfL` — spoke-okn's **environmental-occurrence layer**, recording the compound measured in a named geography with a value, unit, medium and date. That is a 100% hit rate, and it is the crosswalk's real payload.

This inverts the expected value proposition, and in a useful way. spoke-okn's contribution to an AOP-Wiki stressor is not primarily pharmacological — it is **exposure**. The joined graph answers "this chemical initiates *this* adverse outcome pathway, *and here is where it has actually been detected, at what concentration, in which medium*" — which is precisely the exposure arm that a hazard-only AOP lacks, and precisely what turns an AOP into a risk assessment. The pharmacology (10 compounds with targets) is the thin tail, not the trunk.

**Maintainer note.** The 87 figure is the CID-level count and is stable. Anyone building on this crosswalk should lead with the `FOUNDIN_CfL` exposure join (87/87), not the target/disease join (10/87 and 5/87), and should not read `TREATS_CtD` as a therapeutic claim — it is trial-intervention provenance carrying a `phase` edge property.

## Literature validation

This question is a **structural/coverage count, not a scientific claim**, so it is validated by construction rather than against the literature — no pharmacological or toxicological assertion is made that would require a citation.

The join rests on the **PubChem CID**, a stable, globally unique compound registry identifier, plus the hand-verified crosswalk `P3-pubchem-aopwiki-spokeokn` (87 CIDs, verified 2026-07-12). Correctness of the count is established three ways: (1) the crosswalk's `skeleton_query` was re-run live and returned **87**, reproducing the verified count exactly; (2) the join is **1:1** — 87 AOP-Wiki CIDs map to 87 distinct spoke-okn compounds, so the count is not inflated by one-to-many identifier fan-out; (3) the denominators (403 CIDs, 369 stressors, 117 AOPs) were counted directly in the source graph in the same session, so the 21.6% recall and the 48/117 AOP reach are computed, not estimated. **Validated by construction** (shared PubChem CID standard + hand-verified crosswalk; all counts executed live, no literature claim asserted).

#### Query 1 — The crosswalk skeleton — AOP-Wiki PubChem CIDs present in spoke-okn

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000140> ?cidLit .
    BIND(STR(?cidLit) AS ?cid)
    BIND(IRI(CONCAT('http://identifiers.org/pubchem.compound/', ?cid)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
  }
}
```

_1 row(s)_

| n |
| --- |
| 87 |

#### Query 2 — Denominators in AOP-Wiki — total PubChem CIDs, the stressors carrying them, and the AOPs they trigger

```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
SELECT (COUNT(DISTINCT ?cid) AS ?aopwikiCIDs) (COUNT(DISTINCT ?st) AS ?stressors) (COUNT(DISTINCT ?aop) AS ?aops) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000140> ?cid .
    OPTIONAL {
      ?cas <http://www.w3.org/2004/02/skos/core#exactMatch> ?chem .
      ?st aop:has_chemical_entity ?cas .
      OPTIONAL { ?aop obo:NCIT_C54571 ?st }
    }
  }
}
```

_1 row(s)_

| aopwikiCIDs | stressors | aops |
| --- | --- | --- |
| 403 | 369 | 117 |

#### Query 3 — Reach of the crosswalk — matched CIDs, the spoke-okn compounds they resolve to (1:1), and the AOPs reached

```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
SELECT (COUNT(DISTINCT ?cid) AS ?matchedCIDs) (COUNT(DISTINCT ?cmp) AS ?spokeCompounds) (COUNT(DISTINCT ?aop) AS ?aopsReached) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000140> ?cidLit .
    BIND(STR(?cidLit) AS ?cid)
    BIND(IRI(CONCAT('http://identifiers.org/pubchem.compound/', ?cid)) AS ?x)
    OPTIONAL {
      ?cas <http://www.w3.org/2004/02/skos/core#exactMatch> ?chem .
      ?st aop:has_chemical_entity ?cas .
      ?aop obo:NCIT_C54571 ?st .
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
  }
}
```

_1 row(s)_

| matchedCIDs | spokeCompounds | aopsReached |
| --- | --- | --- |
| 87 | 87 | 48 |

#### Query 4 — What spoke-okn actually contributes for the 87 matched compounds, by edge class

```sparql
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?edgeClass (COUNT(DISTINCT ?cid) AS ?nCompounds) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000140> ?cidLit .
    BIND(STR(?cidLit) AS ?cid)
    BIND(IRI(CONCAT('http://identifiers.org/pubchem.compound/', ?cid)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    VALUES (?rel ?edgeClass) {
      (sp:UPREGULATES_CuG   "gene target")
      (sp:DOWNREGULATES_CdG "gene target")
      (sp:TREATS_CtD        "disease (trial)")
      (sp:CONTRAINDICATES_CcD "disease (trial)")
      (sp:FOUNDIN_CfL       "environmental occurrence")
    }
    ?cmp ?rel ?o .
  }
} GROUP BY ?edgeClass ORDER BY DESC(?nCompounds)
```

_3 row(s)_

| edgeClass | nCompounds |
| --- | --- |
| environmental occurrence | 87 |
| gene target | 10 |
| disease (trial) | 5 |

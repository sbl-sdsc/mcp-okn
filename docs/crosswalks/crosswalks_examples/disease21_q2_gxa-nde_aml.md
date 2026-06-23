# disease21_q2_gxa-nde_aml

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `nde` — <https://purl.org/okn/frink/kg/nde>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

Acute myeloid leukemia (AML) is one of the diseases GXA profiles by expression (q1). **Crosswalk on EFO↔MONDO:** how many NDE datasets/records target AML, so its expression studies can be paired with NIAID dataset resources? Join on MONDO = acute myeloid leukemia.

---
🧠 **Assistant**

**Why the join is required.** GXA confirms AML has expression studies; only NDE knows how many dataset resources target AML. Pairing them requires resolving AML's MONDO term and counting NDE records keyed on it.

**Join mechanics.** Resolve `?mondo` whose ubergraph label is "acute myeloid leukemia", then count NDE `schema:healthCondition` records pointing at it.

AML carries **2,449 NDE records** — one of the most dataset-rich diseases in the join. Combined with GXA's AML differential-expression studies, this makes AML a well-resourced disease for cross-referencing expression signatures against NIAID dataset holdings.

**Validation (standard + literature).** Join on the MONDO identifier; the count is a direct `schema:healthCondition` aggregation. According to PubMed, AML is a paradigm expression-profiled malignancy — whole-transcriptome RNA-seq is used for its diagnosis, classification, risk assessment and targeted therapy (Arindrarto et al., *Leukemia* 2020, [DOI](https://doi.org/10.1038/s41375-020-0762-8)) — so pairing GXA's AML expression studies with NDE's 2,449 AML dataset records is well-motivated. **Validated** (shared MONDO identifier; PubMed-corroborated).

## SPARQL queries executed
#### Query 1
_`nde`, `ubergraph` · 1 row_
```sparql
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (COUNT(DISTINCT ?x) AS ?ndeRecords) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo rdfs:label "acute myeloid leukemia" . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x schema:healthCondition ?mondo . }
}
```
| ndeRecords |
| --- |
| 2449 |

**Validation:** shared MONDO identifier; NDE `schema:healthCondition` aggregation. PubMed — Arindrarto 2020 [DOI](https://doi.org/10.1038/s41375-020-0762-8).

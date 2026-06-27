# D35-Q2: CFDE-inferred vs SPOKE-curated inflammatory bowel disease genes — concordance via DOID↔MONDO

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × spoke-okn, joined on the DISEASE entity via the DOID↔MONDO ubergraph bridge. spoke "inflammatory bowel disease" (DOID) bridges to the CFDE MONDO node.

Research question: For inflammatory bowel disease, which genes do BOTH spoke-okn curate and CFDE REVEAL infer (concordance of curated vs statistically inferred disease genes)?

Why the join is required: spoke keys disease–gene curation on DOID; digcfdekg keys inferred genes on MONDO. The concordance for the same disease needs the DOID↔MONDO bridge plus the shared Entrez gene IRI.

---

🧠 **Assistant**

Top genes that both spoke-okn curates (ASSOCIATES_DaG) and CFDE REVEAL infers for inflammatory bowel disease, after bridging spoke's DOID node to CFDE's MONDO (199 concordant genes total):

| Gene | PIGEAN score |
|---|---|
| IL12B | 9.84 |
| IL10 | 9.68 |
| IFNG | 9.12 |
| TNF | 8.52 |
| IL2RA | 8.46 |
| PTPRC | 8.32 |
| STAT3 | 8.21 |
| TNFAIP3 | 8.19 |
| MAP3K8 | 7.89 |
| PTPN2 | 7.73 |
| SMAD3 | 7.34 |
| IKZF3 | 7.22 |

Why this answers the question: the concordant set is the canonical IBD immune-susceptibility programme — the IL-23/IL-12 axis (IL12B), the regulatory cytokine IL10 (whose loss causes very-early-onset IBD), the effector cytokines IFNG/TNF (the anti-TNF drug-target), the JAK–STAT node STAT3, the NF-κB brake TNFAIP3 (A20), and the phosphatases PTPN2/PTPRC. Curated knowledge (spoke-okn) and statistical inference (CFDE REVEAL) agree on these across 199 genes, computable only by bridging spoke's DOID node to CFDE's MONDO node.

Literature validation (PubMed): "(IL12B OR IL23 OR IL10 OR STAT3 OR TNFAIP3) inflammatory bowel disease susceptibility gene" returns 460 records (e.g. PMIDs 42353858, 42298187), confirming the IBD immune-gene programme.

#### Query 1 — Genes both SPOKE curates and CFDE infers for IBD (DOID↔MONDO bridge)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
# digcfdekg x spoke-okn, DISEASE bridge: spoke "inflammatory bowel disease" (DOID) <-> CFDE MONDO via ubergraph.
SELECT DISTINCT ?sym ?pigeanScore WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?doid a biolink:Disease ; rdfs:label "inflammatory bowel disease" ; spoke:ASSOCIATES_DaG ?gene .
    FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_'))
    ?gene rdfs:label ?sym .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo skos:exactMatch ?doid . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?st rdf:predicate dig:geneToTrait ; rdf:object ?mondo ; rdf:subject ?gene ; dig:weight ?pigeanScore . }
} ORDER BY DESC(?pigeanScore) LIMIT 16
```

_199 concordant genes — showing first 5_

| sym | pigeanScore |
| --- | --- |
| IL12B | 9.84 |
| IL10 | 9.68 |
| IFNG | 9.12 |
| TNF | 8.52 |
| IL2RA | 8.46 |

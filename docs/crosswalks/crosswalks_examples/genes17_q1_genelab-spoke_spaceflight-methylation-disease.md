# G17-Q1: Spaceflight differentially-methylated genes that are SPOKE disease genes

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: spoke-genelab × spoke-okn on the Entrez gene id. spoke-genelab carries spaceflight **DNA-methylation** data — assays measure differential methylation of 1 kb regions (`MEASURED_DIFFERENTIAL_METHYLATION_ASmMR`, with `methylation_diff`), and a model-organism gene is `METHYLATED_IN` that region. The model-organism gene bridges to its human ortholog (`IS_ORTHOLOG_MGiG`, Entrez↔Entrez), which spoke-okn associates with disease (`ASSOCIATES_DaG`). This exercises spoke-genelab's epigenetics layer, which no recorded crosswalk yet demonstrates.

Research question: Which genes are most strongly differentially methylated in spaceflight, and — via their human orthologs — which diseases does SPOKE associate them with?

Why the join is required: spoke-genelab has the spaceflight methylation but no disease context; spoke-okn has the gene–disease associations but no spaceflight/epigenetics data. Connecting an epigenetically-altered spaceflight gene to its disease relevance needs the Entrez ortholog join.

---

🧠 **Assistant**

Genes most strongly differentially methylated in spaceflight (model organism), with their human ortholog and the diseases SPOKE associates them with:

| Gene (mouse→human) | max methylation Δ% | SPOKE disease(s) |
|---|---|---|
| Ttn → TTN | 83.3 | **cardiomyopathy** |
| Prkcsh → PRKCSH | 81.8 | liver disease; gastroesophageal reflux disease |
| Cilk1 → CILK1 | 81.8 | epilepsy |
| Obscn → OBSCN | 76.9 | liver disease |
| H2-Q2 → HLA-B / HLA-C / HLA-DRB | 72.7 | psoriasis; asthma; epilepsy; dermatitis; endocarditis |

Why this answers the question: the join surfaces a striking, spaceflight-relevant signal. The single most strongly methylated gene, **TTN (titin)**, is the central **cardiomyopathy** gene — and cardiac remodeling/deconditioning is a recognised spaceflight health risk, so an epigenetic hit on TTN is mechanistically meaningful. The MHC locus (mouse H2-Q2 → human HLA-B/C/DRB) maps to autoimmune/inflammatory disease (psoriasis, asthma, dermatitis), consistent with spaceflight immune dysregulation. This epigenetics→disease view is only assembled by bridging spoke-genelab's methylation data to spoke-okn's disease graph on the Entrez ortholog.

Literature validation (PubMed): spaceflight/microgravity DNA-methylation and epigenetic alterations are documented (9 records, e.g. PMIDs 42151678, 34589093 — the NASA Twins Study); TTN is the established titin-cardiomyopathy gene.

#### Query 1 — Spaceflight differentially-methylated genes → SPOKE disease (Entrez ortholog)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?humanGene ?disease (MAX(ABS(?mdiff)) AS ?maxMethylDiff) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?st rdf:predicate sg:MEASURED_DIFFERENTIAL_METHYLATION_ASmMR ; rdf:object ?mr ; sg:methylation_diff ?mdiff .
    ?gene sg:METHYLATED_IN_MGmMR ?mr ; sg:symbol ?sym ; sg:IS_ORTHOLOG_MGiG ?humanGene .
    FILTER(ABS(?mdiff) > 25)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?d <https://purl.org/okn/frink/kg/spoke-okn/schema/ASSOCIATES_DaG> ?humanGene ; rdfs:label ?disease .
  }
} GROUP BY ?sym ?humanGene ?disease ORDER BY DESC(?maxMethylDiff) LIMIT 15
```

_15 row(s) — showing first 5_

| sym | humanGene | disease | maxMethylDiff |
| --- | --- | --- | --- |
| Ttn | http://www.ncbi.nlm.nih.gov/gene/7273 | cardiomyopathy | 83.3333 |
| Prkcsh | http://www.ncbi.nlm.nih.gov/gene/5589 | gastroesophageal reflux disease | 81.8182 |
| Cilk1 | http://www.ncbi.nlm.nih.gov/gene/22858 | epilepsy | 81.8182 |
| Prkcsh | http://www.ncbi.nlm.nih.gov/gene/5589 | liver disease | 81.8182 |
| Obscn | http://www.ncbi.nlm.nih.gov/gene/84033 | liver disease | 76.875 |

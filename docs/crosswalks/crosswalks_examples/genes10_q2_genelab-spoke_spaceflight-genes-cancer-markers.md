# CW10-Q2: Spaceflight-DE genes that are SPOKE cancer prognostic markers

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: spoke-genelab × spoke-okn on the shared Entrez gene id (direct join, both use NCBI gene IRIs).

Research question: Which genes strongly differentially expressed in spaceflight (spoke-genelab) are also SPOKE cancer prognostic markers (MARKER_POS_GmpD / MARKER_NEG_GmnD)? This is relevant to spaceflight cancer-risk assessment (e.g. radiation-driven dysregulation of prognostic genes).

Why the join is required: spoke-genelab has the spaceflight expression; spoke-okn has the cancer prognostic-marker edges. Only the Entrez join links a spaceflight transcriptional change to a gene's cancer-prognostic role.

---

🧠 **Assistant**

Spaceflight-DE genes (adj. p < 1e-50) that SPOKE flags as cancer prognostic markers:

| Gene | max abs log2FC | SPOKE marker | Cancer |
|---|---|---|---|
| MT2A | 6.7 | unfavorable | kidney, pancreatic, lung cancer |
| S100A1 | 8.4 | unfavorable | kidney cancer |
| MYL3 | 9.0 | favorable | kidney cancer |
| RRAGD | 4.9 | favorable / unfavorable | kidney / liver cancer |
| INPP5A | 3.7 | favorable / unfavorable | kidney / breast cancer |

Why this answers the question: MT2A (metallothionein-2A), a metal/oxidative-stress response gene, is among the most strongly spaceflight-perturbed genes and is an unfavorable prognostic marker across kidney, pancreatic and lung cancer in SPOKE — exactly the kind of stress-responsive, prognosis-relevant gene a spaceflight cancer-risk analysis cares about. The link is only visible by joining GeneLab spaceflight expression to SPOKE prognostic markers on the Entrez id.

Literature validation (PubMed): MT2A/metallothionein in cancer prognosis returns 32 records (e.g. PMIDs 35817020, 34572779). The MT2A-cancer-prognosis role is literature-supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `spoke-genelab`, `spoke-okn`_

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?markerType ?cancer (MAX(ABS(?lfc)) AS ?maxAbsLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?gene ; sg:log2fc ?lfc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 1.0e-50)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?gene rdfs:label ?sym .
    { ?gene spoke:MARKER_POS_GmpD ?c . BIND("favorable" AS ?markerType) }
    UNION
    { ?gene spoke:MARKER_NEG_GmnD ?c . BIND("unfavorable" AS ?markerType) }
    ?c rdfs:label ?cancer .
  }
} GROUP BY ?sym ?markerType ?cancer ORDER BY ?minAdjP LIMIT 25
```

_25 row(s) — showing first 5_

| sym | markerType | cancer | maxAbsLog2fc | minAdjP |
| --- | --- | --- | --- | --- |
| PLCL1 | favorable | kidney cancer | 5.76 | 1.46e-305 |
| TMEM38A | favorable | kidney cancer | 4.54 | 6.79e-305 |
| TMEM38A | favorable | lung cancer | 4.54 | 6.79e-305 |
| TMEM38A | unfavorable | ovarian cancer | 4.54 | 6.79e-305 |
| PPP2R3B | favorable | pancreatic cancer | 5.78 | 1.24e-304 |

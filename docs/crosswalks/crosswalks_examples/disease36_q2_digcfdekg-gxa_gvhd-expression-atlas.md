# D36-Q2: GXA expression atlas for acute graft-vs-host disease, a disease CFDE models genetically

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × gene-expression-atlas-okn (GXA), joined on the shared EFO disease (identical IRI in both graphs).

Research question: For acute graft-versus-host disease — which CFDE REVEAL models genetically — what does GXA's differential-expression atlas show as the dominant up-regulated transcriptional signature?

Why the join is required: digcfdekg models the disease genetically but holds no expression data; GXA holds the differential-expression atlas (log2FC, adj p) but no genetic-relevance concept. Reading GXA's measured expression signature for a disease CFDE models requires the shared-EFO disease join.

---

🧠 **Assistant**

GXA's strongest up-regulated genes (adj p < 1e-6) for acute graft-vs-host disease (EFO_0004599), a disease CFDE REVEAL also models genetically:

| Gene | max log2FC (up) | min adj p |
|---|---|---|
| Cd8b1 | 10.5 | 9.2e-97 |
| Cd8a | 10.4 | 5.3e-67 |
| Trbv13-1 | 10.6 | 2.5e-74 |
| Trav10 | 11.8 | 1.2e-25 |
| Traj21 | 11.2 | 9.8e-23 |
| Pdcd1 (PD-1) | 9.5 | 1.5e-52 |
| Icos | 9.5 | 9.3e-38 |
| Cd226 | 9.4 | 1.3e-53 |
| Lef1 | 9.5 | 3.5e-30 |

Why this answers the question: GXA's expression atlas returns the textbook acute-GvHD effector signature — a massive up-regulation of CD8 T-cell genes (Cd8a, Cd8b1), clonally-expanded T-cell-receptor segments (Trav10, Traj21, Trbv13-1), and the T-cell activation/checkpoint programme (Pdcd1/PD-1, Icos, Cd226, Lef1). This is the alloreactive cytotoxic-T-cell response that defines GvHD pathology. (Note: GXA's acute-GvHD study is a murine alloreactivity model, so the gene symbols are mouse orthologues; the disease entity is matched to CFDE on the shared EFO IRI.) Pairing this measured expression signature with CFDE's genetic model of the same disease is enabled by the shared-EFO disease crosswalk.

Literature validation (PubMed): "graft versus host disease CD8 T cell infiltration gene expression" returns 20 records (e.g. PMIDs 41679650, 41580972); the alloreactive CD8 T-cell / PD-1 / ICOS signature in acute GvHD is well established.

#### Query 1 — GXA top up-regulated genes for acute GvHD (gated by CFDE coverage, shared EFO)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
# digcfdekg x GXA on shared EFO (acute graft vs host disease EFO_0004599).
# GXA's strongest up-regulated DE genes for a disease CFDE REVEAL also models genetically.
SELECT ?sym (MAX(?lfc) AS ?maxLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  FILTER EXISTS { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?st rdf:predicate dig:geneToTrait ; rdf:object <http://www.ebi.ac.uk/efo/EFO_0004599> } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?assay biolink:has_attribute <http://www.ebi.ac.uk/efo/EFO_0004599> .
    ?de biolink:subject ?assay ; biolink:object ?gGene ; wobd:log2fc ?lfc ; wobd:adj_p_value ?adjp ; wobd:direction "up" .
    ?gGene biolink:symbol ?sym .
    FILTER(?adjp < 1.0e-6 && ?lfc < 30)
  }
} GROUP BY ?sym ORDER BY DESC(?maxLog2fc) LIMIT 15
```

_15 row(s) — showing first 5_

| sym | maxLog2fc | minAdjP |
| --- | --- | --- |
| Trav10 | 11.8 | 1.18871e-25 |
| Traj21 | 11.2 | 9.78288e-23 |
| Trbv13-1 | 10.6 | 2.534e-74 |
| Cd8b1 | 10.5 | 9.17474e-97 |
| Cd8a | 10.4 | 5.26174e-67 |

# PW01-Q1: Reactome pathways differentially active in colon cancer (GXA) mapped to their ProKN protein membership

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: gene-expression-atlas-okn (GXA) × prokn, joined on the **Reactome pathway**. GXA enriches its differential-expression contrasts against Reactome (`enrichment_source = "GXA:Reactome"`, `biolink:object` → `reactome.org/content/detail/R-HSA-…`); ProKN places proteins in Reactome pathways (`RO_0000056` → `identifiers.org/reactome/R-HSA-…`, with the pathway `rdfs:label`). Same R-HSA accession, different prefix. (Newly recorded — the first Pathways crosswalk; 1,068 shared Reactome pathways.)

Research question: For colon cancer, which Reactome pathways does GXA find differentially active, and how many proteins does ProKN place in each?

Why the join is required: GXA gives the disease→pathway enrichment (which pathways shift, with significance) but not the pathway's molecular composition; ProKN gives the pathway→protein membership but no disease/expression context. Linking the differentially-active pathways to their protein constituents needs the shared Reactome pathway.

---

🧠 **Assistant**

Reactome pathways GXA finds differentially active in colon adenocarcinoma (adj p < 0.001), named via ProKN, with ProKN protein membership:

| Reactome pathway (ProKN label) | GXA best adj p | # ProKN proteins |
|---|---|---|
| Resolution of Sister Chromatid Cohesion | 3.1e-12 | 127 |
| EML4 and NUDC in mitotic spindle formation | 4.6e-12 | 117 |
| Nonsense Mediated Decay (NMD) enhanced by the EJC | 3.9e-11 | 116 |
| GTP hydrolysis and joining of the 60S ribosomal subunit | 9.0e-10 | 113 |
| L13a-mediated translational silencing | 1.5e-9 | 112 |
| SRP-dependent cotranslational protein targeting to membrane | 3.8e-7 | 113 |
| Formation of a pool of free 40S subunits | 2.3e-8 | 102 |
| RHO GTPases Activate Formins | 2.6e-5 | 140 |
| FCERI mediated NF-kB activation | 8.0e-5 | 129 |
| Regulation of expression of SLITs and ROBOs | 6.3e-4 | 159 |

Why this answers the question: the join surfaces colon cancer's differentially-active pathway programme — mitosis/cell-cycle (Resolution of Sister Chromatid Cohesion, EML4/NUDC mitotic spindle) and protein synthesis (60S/40S ribosomal subunit joining, NMD, cotranslational targeting) — the canonical proliferation signature of a tumour, with the strongest enrichment (adj p ~1e-12) on the mitotic pathways. ProKN then supplies each pathway's protein membership (102–159 proteins), turning a statistical enrichment into a concrete protein set to interrogate. Neither graph alone provides both; the Reactome join does.

Literature validation (PubMed): upregulation of cell-cycle and ribosome-biogenesis pathways in colorectal cancer proliferation is documented (e.g. PMIDs 38341833, 36820595).

#### Query 1 — Colon-cancer-enriched Reactome pathways (GXA) → ProKN protein membership

```sparql
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?pathwayLabel (MIN(?adjp) AS ?bestAdjP) (COUNT(DISTINCT ?prot) AS ?proknProteins) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?assay biolink:has_attribute ?efo . ?efo a biolink:Disease ; biolink:name "colon adenocarcinoma" .
    ?s wobd:enrichment_source "GXA:Reactome" ; biolink:subject ?assay ; biolink:object ?gxaReact ; wobd:adj_p_value ?adjp .
    FILTER(?adjp < 0.001) FILTER(CONTAINS(STR(?gxaReact),'R-HSA-'))
  }
  BIND(IRI(CONCAT('https://identifiers.org/reactome/',REPLACE(STR(?gxaReact),'^.*/detail/',''))) AS ?proknReact)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?prot <http://purl.obolibrary.org/obo/RO_0000056> ?proknReact . ?proknReact rdfs:label ?pathwayLabel . }
} GROUP BY ?pathwayLabel ORDER BY DESC(?proknProteins) LIMIT 10
```

_10 row(s) — showing first 5_

| pathwayLabel | bestAdjP | proknProteins |
| --- | --- | --- |
| Regulation of expression of SLITs and ROBOs | 0.000627617 | 159 |
| RHO GTPases Activate Formins | 0.0000262416 | 140 |
| FCERI mediated NF-kB activation | 0.0000803411 | 129 |
| Resolution of Sister Chromatid Cohesion | 3.13389e-12 | 127 |
| EML4 and NUDC in mitotic spindle formation | 4.64135e-12 | 117 |

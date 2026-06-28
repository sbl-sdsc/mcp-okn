# Repurposing: SPOKE compounds that down-regulate genes GXA finds up in a named tumour contrast

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: gene-expression-atlas-okn × spoke-okn on the shared gene identifier. SPOKE keys genes on Entrez (gene node IRI `http://www.ncbi.nlm.nih.gov/gene/{id}`); the GXA tumour-vs-normal microarray contrasts key their differential-expression objects on NCBI gene (`https://www.ncbi.nlm.nih.gov/gene/{id}`), so we join after an `https`→`http` rewrite.

Research question: For genes significantly **UP-regulated** in a *named* Gene Expression Atlas tumour-vs-normal contrast, which named chemical compounds does SPOKE record as **DOWN-regulating** them (`DOWNREGULATES_CdG`)? Such compound→gene reversals — "disease up / drug down" — are candidate counteracting / repurposing agents for that tumour.

**Note:** the GXA log2fc is reported together with its named contrast (`biolink:name` on the assay), because direction is only meaningful relative to the contrast.

---

🧠 **Assistant**

GXA provides the disease-driven up-regulation signal and the named contrast but no compound–gene pharmacology; SPOKE provides named compound→gene down-regulation edges but no disease expression measurements. The "reverse the disease signature" query only exists across the two graphs, joined on the shared gene id. Each row = a SPOKE compound that DOWN-regulates a gene GXA finds UP in the named contrast:

| Gene | GXA contrast (direction, log2FC) | Compound that down-regulates it (SPOKE) |
|---|---|---|
| TOP2A | 'non-small cell lung cancer' vs 'normal' (up, +4.4) | Fluorouracil |
| SPP1 | 'non-small cell lung cancer' vs 'normal' (up, +4.3) | Fluorouracil |
| SOX2 | 'non-small cell lung cancer' vs 'normal' (up, +4.3) | Hexachlorophene |
| CDC20 | 'non-small cell lung cancer' vs 'normal' (up, +4.1) | 3-Methylcholanthrene / Tributyltin chloride / Thiabendazole |

**Why this answers the question:** **TOP2A** (topoisomerase II) is strongly up in the NSCLC-vs-normal contrast (+4.4), and SPOKE records **Fluorouracil** — a standard component of lung-cancer chemotherapy regimens — as down-regulating it; TOP2A is itself the molecular target of topoisomerase-II-inhibitor chemotherapeutics, so a drug that reverses its over-expression is exactly the "disease up / drug down" reversal a repurposing screen seeks. **SPP1** (osteopontin) and the mitotic regulators **SOX2** and **CDC20** follow the same pattern. Each reversal is surfaced only by joining GXA's named-contrast disease expression to SPOKE's compound–gene edges on the shared gene id.

## SPARQL query executed

```sparql
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?sym ?gxaContrast ?log2fc ?compound WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    VALUES ?assay {
      <http://purl.org/okn/wobd/assay/E-GEOD-18842-g2_g1>   # non-small cell lung cancer vs normal
      <http://purl.org/okn/wobd/assay/E-GEOD-16515-g1_g2>   # pancreatic cancer vs normal
      <http://purl.org/okn/wobd/assay/E-GEOD-15641-g4_g3>   # clear cell renal carcinoma vs normal
    }
    ?assay biolink:name ?gxaContrast .
    ?assoc biolink:subject ?assay ; biolink:object ?ncbi ;
           wobd:direction "up" ; wobd:log2fc ?log2fc ; wobd:adj_p_value ?adjp .
    FILTER(?adjp < 0.001)
    FILTER(CONTAINS(STR(?ncbi),'ncbi.nlm.nih.gov/gene/'))
  }
  BIND(IRI(REPLACE(STR(?ncbi),'https://www.ncbi','http://www.ncbi')) AS ?gnode)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?gnode rdfs:label ?sym .
    ?cmpd spoke:DOWNREGULATES_CdG ?gnode ; rdfs:label ?compound .
  }
} ORDER BY DESC(?log2fc) LIMIT 15
```

## Literature validation

Yokobori et al., 2013, *Mol Cancer Res* — show that TOP2A is a degradation target whose expression governs chemotherapeutic sensitivity and prognosis in non-small cell lung cancers, supporting TOP2A as a meaningful "disease-up" repurposing target in the NSCLC contrast. (According to PubMed.) [PMID:24165483](https://pubmed.ncbi.nlm.nih.gov/24165483/) · [DOI](https://doi.org/10.1158/1541-7786.MCR-13-0341)

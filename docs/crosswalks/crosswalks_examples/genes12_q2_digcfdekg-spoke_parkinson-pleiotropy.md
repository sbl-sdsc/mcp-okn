# CFDE REVEAL Parkinson-disease PIGEAN genes and their SPOKE-OKN pleiotropy

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × spoke-okn, joined on the shared Entrez gene IRI (identical IRI form in both graphs, direct join, no rewrite).

Research question: For the genes CFDE REVEAL infers as most relevant to Parkinson disease (with what PIGEAN weight), how pleiotropic are they — i.e. which *other* named diseases does SPOKE-OKN associate each with — and does SPOKE independently corroborate the Parkinson link?

Why the join is required: digcfdekg supplies the PIGEAN Parkinson-relevance weights; spoke-okn supplies the full per-gene named disease-association set. Reading each CFDE Parkinson gene's PIGEAN weight alongside its named SPOKE disease set (its pleiotropy, and whether SPOKE also names Parkinson's disease) needs the Entrez join.

---

🧠 **Assistant**

Top PIGEAN Parkinson-disease (MONDO_0005180) genes from CFDE REVEAL, each with the named SPOKE-OKN diseases it is associated with (CFDE gene+weight AND named SPOKE diseases in the same row; SPOKE's own Parkinson's-disease association bolded):

| Gene | PIGEAN weight | SPOKE diseases (named) |
|---|---|---|
| SNCA | 5.61 | **Parkinson's disease**, Alzheimer's disease, motor neuron disease, schizophrenia, depressive disorder, nervous system disease |
| BAG3 | 5.31 | **Parkinson's disease**, cardiomyopathy, chronic obstructive pulmonary disease, nervous system disease |
| WNT3 | 4.79 | **Parkinson's disease**, Alzheimer's disease, breast carcinoma |
| GCH1 | 4.65 | **Parkinson's disease**, depressive disorder, epilepsy, rheumatoid arthritis, hypertension, nervous system disease |
| MAP3K14 | 4.56 | dermatitis, asthma |
| IGSF9B | 4.51 | **Parkinson's disease**, migraine, schizophrenia, nervous system disease |
| ARHGAP27 | 4.38 | **Parkinson's disease**, breast carcinoma |
| ELOVL7 | 4.35 | **Parkinson's disease** |
| MAPT | 4.30 | **Parkinson's disease**, Alzheimer's disease, motor neuron disease, brain cancer, breast carcinoma, osteoarthritis, depressive disorder, epilepsy, nervous system disease |
| UBAP2 | 4.18 | **Parkinson's disease** |

Why this answers the question: CFDE REVEAL's top Parkinson genes are the established PD genes — SNCA (α-synuclein, the defining PD gene), MAPT (tau, the H1-haplotype risk locus), GCH1 (dopa-responsive dystonia / PD), plus replicated GWAS loci (BAG3, WNT3, ELOVL7, UBAP2, ARHGAP27, IGSF9B). SPOKE independently *names* the Parkinson's-disease association for almost every gene (bolded) and reveals their pleiotropy: MAPT (9 diseases) and SNCA (6) sit at the centre of a neurodegeneration cluster (Alzheimer's disease, motor neuron disease), GCH1 spreads into depression/epilepsy/rheumatoid arthritis, while ELOVL7/UBAP2 are PD-specific. The PIGEAN weight + the named SPOKE pleiotropy set together require the Entrez join.

## SPARQL query executed

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
# digcfdekg x spoke-okn on Entrez (identical IRI form, no rewrite).
# Top PIGEAN genes for Parkinson disease (MONDO_0005180), each listed with the
# NAMED diseases SPOKE-OKN co-associates the gene with (pleiotropy + Parkinson corroboration).
SELECT ?sym ?pigeanScore (COUNT(DISTINCT ?spokeDisease) AS ?nSpokeDiseases)
       (GROUP_CONCAT(DISTINCT ?spokeDisease; separator=" | ") AS ?spokeDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/MONDO_0005180> ;
        rdf:subject ?gene ;
        dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 3.0)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?d spoke:ASSOCIATES_DaG ?gene ; rdfs:label ?spokeDisease .
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 12
```

_12 row(s) — showing first 5_

| sym | pigeanScore | nSpokeDiseases | spokeDiseases |
| --- | --- | --- | --- |
| SNCA | 5.61 | 6 | nervous system disease \| schizophrenia \| motor neuron disease \| depressive disorder \| Parkinson's disease \| Alzheimer's disease |
| BAG3 | 5.31 | 4 | cardiomyopathy \| Parkinson's disease \| chronic obstructive pulmonary disease \| nervous system disease |
| WNT3 | 4.79 | 3 | breast carcinoma \| Parkinson's disease \| Alzheimer's disease |
| GCH1 | 4.65 | 6 | depressive disorder \| epilepsy \| Parkinson's disease \| rheumatoid arthritis \| hypertension \| nervous system disease |
| MAP3K14 | 4.56 | 2 | dermatitis \| asthma |

## Literature validation

According to PubMed, Kukkle et al., 2025, *Mov Disord Clin Pract* — a global review of progressive supranuclear palsy identifies the **MAPT H1 haplotype** as the principal genetic risk factor across the Parkinson/tauopathy spectrum, corroborating CFDE REVEAL's high PIGEAN Parkinson weight for MAPT and the SPOKE neurodegeneration pleiotropy (Parkinson's, Alzheimer's, motor neuron disease) this crosswalk surfaces. [PMID:40898879](https://pubmed.ncbi.nlm.nih.gov/40898879/) · [DOI](https://doi.org/10.1002/mdc3.70338)

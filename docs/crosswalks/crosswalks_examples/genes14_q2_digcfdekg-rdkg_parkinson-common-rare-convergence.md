# G14-Q2: CFDE common-variant Parkinson genes that are rdkg monogenic movement-disorder genes

- **Date:** 2026-06-26
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × rdkg (Rare Disease KG), joined on the shared Entrez gene id (rewritten ncbi.nlm.nih.gov/gene ↔ identifiers.org/ncbigene). rdkg disease labels via ubergraph.

Research question: For Parkinson disease — a common neurodegenerative trait — which CFDE REVEAL-inferred genes are also rare/monogenic disease genes in rdkg, and which Mendelian movement disorders do they cause?

Why the join is required: digcfdekg has the PIGEAN Parkinson gene relevance; rdkg has the Mendelian gene→rare-disease causation. Mapping the common Parkinson genes onto their monogenic counterparts needs the Entrez join.

---

🧠 **Assistant**

CFDE REVEAL's top Parkinson-disease (MONDO_0005180) genes that rdkg lists as rare/monogenic disease genes:

| Gene | PIGEAN score | Convergent rdkg rare disease(s) |
|---|---|---|
| SNCA | 5.61 | hereditary late-onset Parkinson disease, juvenile-onset Parkinson disease, **Lewy body dementia**, parkinsonian-pyramidal syndrome, atypical juvenile parkinsonism |
| GCH1 | 4.65 | **dopa-responsive dystonia**, GTP cyclohydrolase I deficiency with hyperphenylalaninemia |
| MAPT | 4.30 | **progressive supranuclear palsy** (multiple subtypes), **frontotemporal dementia**, **Pick disease**, semantic dementia, corticobasal syndrome |
| BAG3 | 5.31 | familial dilated cardiomyopathy |
| PKP2 | 4.12 | arrhythmogenic right ventricular cardiomyopathy, sick sinus syndrome |
| WNT3 | 4.79 | tetra-amelia / tetraamelia-multiple malformations syndrome |

Why this answers the question: CFDE's top common-PD genes converge on the canonical Mendelian movement-disorder/neurodegeneration genes in rdkg — SNCA (α-synuclein, familial PD and Lewy body dementia), MAPT (the defining tauopathy gene: PSP, FTD, Pick disease), and GCH1 (dopa-responsive dystonia / Segawa syndrome). The result also exposes pleiotropy where the CFDE "PD-relevant" signal reflects a cardiac gene (BAG3 → dilated cardiomyopathy, PKP2 → arrhythmogenic cardiomyopathy). The common→rare neurodegeneration convergence is only visible by joining CFDE and rdkg on the shared Entrez id.

Literature validation (PubMed): "(SNCA AND familial Parkinson) OR (MAPT AND progressive supranuclear palsy) OR (GCH1 AND dopa-responsive dystonia)" returns 1,488 records (e.g. PMIDs 42254865, 42204920, 42202611), confirming each gene's established monogenic role.

#### Query 1 — CFDE Parkinson genes with their rdkg rare-disease associations

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
# digcfdekg x rdkg on Entrez. CFDE Parkinson-disease genes that rdkg lists as rare/monogenic disease genes.
SELECT ?sym ?pigeanScore (GROUP_CONCAT(DISTINCT ?rareDisease; separator=" | ") AS ?rdkgRareDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/MONDO_0005180> ;
        rdf:subject ?gene ;
        dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 4.0)
  }
  BIND(IRI(REPLACE(STR(?gene),'http://www.ncbi.nlm.nih.gov/gene/','http://identifiers.org/ncbigene/')) AS ?rd)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?rd biolink:related_to ?mondo .
    FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo rdfs:label ?rareDisease . }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 12
```

_9 row(s) — showing first 5_

| sym | pigeanScore | rdkgRareDiseases (excerpt) |
| --- | --- | --- |
| SNCA | 5.61 | parkinsonian disorder \| hereditary late onset Parkinson disease \| Lewy body dementia \| juvenile onset Parkinson disease 19A |
| BAG3 | 5.31 | familial dilated cardiomyopathy \| HIV infectious disease |
| WNT3 | 4.79 | tetraamelia-multiple malformations syndrome \| tetra-amelia \| atrial fibrillation |
| GCH1 | 4.65 | dopa-responsive dystonia \| GTP cyclohydrolase I deficiency with hyperphenylalaninemia \| paraplegia |
| MAPT | 4.30 | progressive supranuclear palsy \| frontotemporal dementia \| Pick disease \| semantic dementia |

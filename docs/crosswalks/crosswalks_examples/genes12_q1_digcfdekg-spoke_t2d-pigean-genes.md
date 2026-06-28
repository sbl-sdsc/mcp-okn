# CFDE REVEAL type-2-diabetes PIGEAN genes and their named SPOKE disease neighbourhoods

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: digcfdekg (CFDE REVEAL KG) × spoke-okn, joined on the shared Entrez gene IRI. digcfdekg gene nodes ARE `http://www.ncbi.nlm.nih.gov/gene/{entrez}`; spoke-okn genes carry the identical IRI form, so this is a direct shared-variable join with no rewrite.

Research question: Which genes does CFDE REVEAL's PIGEAN method infer as most relevant to type 2 diabetes (with what weight), and exactly which *named* diseases does SPOKE-OKN independently associate those same genes with?

Why the join is required: digcfdekg holds the PIGEAN gene→trait relevance weights but no broader gene–disease network; spoke-okn holds the named gene→disease associations but no CFDE trait-relevance inference. Listing each top type-2-diabetes gene's PIGEAN weight *and* its named SPOKE comorbidity set is only possible by joining the two graphs on the shared Entrez id.

---

🧠 **Assistant**

Top genes CFDE REVEAL (PIGEAN combined weight) infers as relevant to type 2 diabetes (MONDO_0005148), each annotated with the *named* diseases SPOKE-OKN independently associates the same Entrez gene with (CFDE gene+weight AND named SPOKE diseases in the same row):

| Gene | PIGEAN weight | SPOKE diseases (named) |
|---|---|---|
| INS | 10.30 | diabetes mellitus, diabetic ketoacidosis, obesity, polycystic ovary syndrome, liver disease, liver cancer, coronary artery disease, chronic kidney disease, pancreatitis, … (24 total) |
| LEP | 9.77 | obesity, anorexia nervosa, eating disorder, polycystic ovary syndrome, coronary artery disease, diabetes mellitus, liver disease (13 total) |
| GCK | 9.73 | diabetes mellitus, diabetic ketoacidosis, obesity, liver disease, liver cancer, epilepsy |
| GCKR | 8.97 | gout, urolithiasis, chronic kidney disease, inflammatory bowel disease, liver disease |
| WFS1 | 8.62 | diabetes mellitus, glaucoma, cataract, schizophrenia, epilepsy, cardiomyopathy, … (9 total) |
| HNF1A | 8.60 | diabetes mellitus, diabetic ketoacidosis, obesity, kidney cancer, liver cancer, coronary artery disease, polycystic ovary syndrome (9 total) |
| GIPR | 8.34 | obesity, breast carcinoma |
| IRS1 | 8.29 | diabetes mellitus, obesity, nutrition disease |
| SLC2A2 | 8.18 | diabetes mellitus, obesity, liver disease, liver cancer, nutrition disease |
| KCNJ11 | 8.13 | diabetes mellitus, diabetic ketoacidosis, obesity, pancreatic cancer, cardiomyopathy, liver cancer, epilepsy (8 total) |
| PPARG | 8.06 | diabetes mellitus, obesity, polycystic ovary syndrome, coronary artery disease, hypertension, cardiomyopathy, pancreatitis (12 total) |
| CEBPA | 7.91 | acute myeloid leukemia, leukemia, obesity, nutrition disease |

Why this answers the question: the genes CFDE REVEAL ranks highest for type 2 diabetes are the canonical T2D genes — the MODY panel (GCK, HNF1A, INS, KCNJ11, SLC2A2/GLUT2), the master adipogenic/insulin-sensitising regulators (PPARG, IRS1), and the incretin/energy-balance axis (GIPR, LEP, GCKR, WFS1). SPOKE then independently names each gene's disease neighbourhood — diabetes mellitus and diabetic ketoacidosis for the MODY genes, plus the recognised metabolic-syndrome cluster (obesity, PCOS, coronary artery disease, chronic kidney disease, liver disease/cancer, gout). Neither graph alone gives both the CFDE relevance weight and the named comorbidity set; the Entrez join does.

## SPARQL query executed

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dig: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
# digcfdekg x spoke-okn, shared key = Entrez gene IRI (identical form, no rewrite).
# Genes CFDE REVEAL (PIGEAN) infers as relevant to type 2 diabetes (MONDO_0005148),
# each listed with the NAMED diseases SPOKE-OKN associates the same gene with.
SELECT ?sym ?pigeanScore (COUNT(DISTINCT ?spokeDisease) AS ?nSpokeDiseases)
       (GROUP_CONCAT(DISTINCT ?spokeDisease; separator=" | ") AS ?spokeDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?st rdf:predicate dig:geneToTrait ;
        rdf:object <http://purl.obolibrary.org/obo/MONDO_0005148> ;
        rdf:subject ?gene ;
        dig:weight ?pigeanScore .
    ?gene rdfs:label ?sym .
    FILTER(?pigeanScore >= 7.0)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?d spoke:ASSOCIATES_DaG ?gene ; rdfs:label ?spokeDisease .
  }
} GROUP BY ?sym ?pigeanScore ORDER BY DESC(?pigeanScore) LIMIT 12
```

_12 row(s) — showing first 5_

| sym | pigeanScore | nSpokeDiseases | spokeDiseases |
| --- | --- | --- | --- |
| INS | 10.3 | 24 | diabetes mellitus \| diabetic ketoacidosis \| obesity \| polycystic ovary syndrome \| liver disease \| … |
| LEP | 9.77 | 13 | obesity \| anorexia nervosa \| eating disorder \| polycystic ovary syndrome \| diabetes mellitus \| … |
| GCK | 9.73 | 6 | diabetes mellitus \| diabetic ketoacidosis \| obesity \| liver disease \| liver cancer \| epilepsy |
| GCKR | 8.97 | 5 | gout \| urolithiasis \| chronic kidney disease \| inflammatory bowel disease \| liver disease |
| WFS1 | 8.62 | 9 | diabetes mellitus \| glaucoma \| cataract \| schizophrenia \| epilepsy \| cardiomyopathy \| … |

## Literature validation

According to PubMed, Zagaroli et al., 2026, *Diabetes Ther* — a systematic review of maturity-onset diabetes of the young (MODY) confirms **GCK, HNF1A, HNF4A, KCNJ11 and INS** as the established monogenic-diabetes genes with genotype-guided treatment, corroborating CFDE REVEAL's high PIGEAN type-2-diabetes weights for these same genes that this crosswalk pairs with SPOKE's named disease neighbourhoods. [PMID:42295651](https://pubmed.ncbi.nlm.nih.gov/42295651/) · [DOI](https://doi.org/10.1007/s13300-026-01884-2)

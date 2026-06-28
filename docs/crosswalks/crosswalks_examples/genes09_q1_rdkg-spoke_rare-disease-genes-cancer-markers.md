# Rare-disease genes (rdkg) that SPOKE flags as cancer prognostic markers

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: rdkg (Rare Disease KG) × spoke-okn, joined on the shared Entrez gene id. rdkg gene nodes are `http://identifiers.org/ncbigene/{entrez}` IRIs; spoke-okn gene nodes are `http://www.ncbi.nlm.nih.gov/gene/{entrez}` IRIs — same Entrez integer, different IRI prefix, so the join needs a one-line rewrite.

Research question: For genes that rdkg curates as the causative gene of a named rare (monogenic) disorder, does SPOKE independently flag that same gene as a favorable or unfavorable cancer prognostic marker — and in which cancer? This surfaces rare-disease genes with a second, prognostic role in common cancers.

Why the join is required: rdkg holds the curated rare-disease gene→condition edges (`genetic_association`, with MONDO/Orphanet rare-disease labels) but no cancer-prognosis data; spoke-okn holds the Human-Protein-Atlas-derived prognostic-marker edges (`MARKER_POS_GmpD` / `MARKER_NEG_GmnD`) but no rare-disease context. Only the Entrez join shows a gene that is BOTH a rare-disease gene (rdkg) AND a cancer prognostic marker (SPOKE).

---

🧠 **Assistant**

Genes that rdkg curates as causative for a named rare disorder, each paired with the cancer prognostic-marker role SPOKE independently records for the same Entrez gene (rdkg rare disease AND SPOKE marker+cancer in the same row):

| Gene | rdkg rare disease (genetic_association) | SPOKE marker | SPOKE cancer |
|---|---|---|---|
| ABCB6 | coloboma of optic disc | unfavorable | liver cancer; kidney cancer |
| ACTB | actinomyopathy-associated syndromic thrombocytopenia | unfavorable | kidney cancer |
| ACTG2 | megacystis-microcolon-intestinal hypoperistalsis syndrome | unfavorable | kidney cancer |
| ADK | hypermethioninemia-encephalopathy (adenosine kinase deficiency) | favorable | liver cancer |
| AGGF1 | capillary-lymphatic-venous malformation | favorable | colorectal cancer |
| AGRN | presynaptic congenital myasthenic syndrome | unfavorable | liver cancer |
| AKAP9 | Romano-Ward (long-QT) syndrome | favorable | kidney cancer |
| ALG2 | congenital myasthenic syndrome with glycosylation defect | favorable | kidney cancer |
| AMMECR1 | midface-hypoplasia / elliptocytosis / nephrocalcinosis syndrome | favorable | ovarian cancer; thyroid cancer |
| ANGPT2 | Milroy disease | unfavorable | cervical; kidney; liver; stomach cancer |

Why this answers the question: each gene is curated by rdkg as the cause of a *named* rare monogenic disorder — the visceral-myopathy gene ACTG2 (megacystis-microcolon-intestinal hypoperistalsis syndrome), the angiopoietin gene ANGPT2 (the lymphedema disorder Milroy disease), the A-kinase scaffold AKAP9 (Romano-Ward long-QT syndrome), and congenital-myasthenic-syndrome genes AGRN/ALG2 — and SPOKE independently flags the *same* Entrez gene as a Human-Protein-Atlas cancer prognostic marker, giving a direction (favorable/unfavorable) and a cancer (ANGPT2 is unfavorable across four cancers; ACTG2 unfavorable in kidney cancer; ADK favorable in liver cancer). The dual rare-disease/cancer-prognosis role is only visible by joining rdkg's rare-disease gene set with SPOKE's prognostic-marker edges on the shared Entrez id.

## SPARQL query executed

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# rdkg x spoke-okn on Entrez. rdkg rare-disease genes (Disease --genetic_association--> Gene)
# that SPOKE independently flags as cancer prognostic markers (favorable / unfavorable).
# Join key: Entrez integer; rewrite rdkg ncbigene IRI -> spoke-okn www.ncbi.nlm.nih.gov/gene IRI.
SELECT DISTINCT ?sym ?rareDisease ?markerType ?cancer WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?dis a biolink:Disease ; rdfs:label ?rareDisease ;
         biolink:genetic_association ?r .
    ?r a biolink:Gene ; rdfs:label ?sym .
    FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
    FILTER(!CONTAINS(?rareDisease,'OBSOLETE') && !CONTAINS(?rareDisease,'Non-specific'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?gene spoke:MARKER_POS_GmpD ?c . BIND("favorable" AS ?markerType) }
    UNION
    { ?gene spoke:MARKER_NEG_GmnD ?c . BIND("unfavorable" AS ?markerType) }
    ?c rdfs:label ?cancer .
  }
} ORDER BY ?sym LIMIT 15
```

_15 row(s) — showing the joined gene set (rows with the same gene/cancer differing only by cancer site collapsed)_

| sym | rareDisease | markerType | cancer |
| --- | --- | --- | --- |
| ABCB6 | coloboma of optic disc | unfavorable | liver cancer |
| ACTB | actinomyopathy-associated syndromic thrombocytopenia | unfavorable | kidney cancer |
| ACTG2 | megacystis-microcolon-intestinal hypoperistalsis syndrome | unfavorable | kidney cancer |
| ADK | hypermethioninemia encephalopathy (adenosine kinase deficiency) | favorable | liver cancer |
| ANGPT2 | Milroy disease | unfavorable | stomach cancer |

## Literature validation

According to PubMed, Hilberath et al., 2025, *Orphanet J Rare Dis* — a genotype-phenotype cohort of megacystis-microcolon-intestinal hypoperistalsis syndrome (MMIHS) confirms **ACTG2** as the most common causative gene (15/19 molecularly diagnosed patients), corroborating rdkg's ACTG2→MMIHS rare-disease edge that this crosswalk pairs with SPOKE's kidney-cancer prognostic-marker role. [PMID:41387873](https://pubmed.ncbi.nlm.nih.gov/41387873/) · [DOI](https://doi.org/10.1186/s13023-025-04154-9)

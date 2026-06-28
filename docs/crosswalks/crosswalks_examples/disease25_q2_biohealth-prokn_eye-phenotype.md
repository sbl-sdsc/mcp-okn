# Ocular phenotypes BioHealthKG tracks (UMLS) beside their ProKN marker genes (HP), bridged UMLS↔HP

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

Focus on the eye. For several specific ocular abnormality phenotypes that BioHealthKG tracks (UMLS CUI), show me in the same rows the named ProKN marker genes that evidence each phenotype. Bridge UMLS↔HP through ubergraph. Why the join?

---
🧠 **Assistant**

**Why the join is required.** ProKN holds the marker-gene panel for each ocular HP phenotype but no clinical concept identity; BioHealthKG holds the UMLS concept (with its clinical label) but no genes. Only the ubergraph `oboInOwl:hasDbXref 'UMLS:{cui}'` edge on each HP term ties the molecular panel to the clinical concept.

**Join mechanics.** For each ocular HP term, ubergraph gives a `UMLS:{cui}` cross-reference; rebuilding `.../kg/node/{cui}` confirms it is a live BioHealthKG concept, and ProKN's reified `biolink:associated_with` statements (`rdf:object` = HP term, `rdf:subject` = Ensembl gene) supply the named marker genes. Each row carries a BioHealthKG ocular phenotype **and** named ProKN marker genes.

**Result (verified, 4 rows; gene lists trimmed to named representatives):**

| Ocular phenotype (BioHealthKG label) · HP | ProKN marker genes (named) |
| --- | --- |
| Retinal dystrophy · HP_0000556 | ABCA4, RHO, RPE65, PRPH2, USH2A, CRB1, EYS, CEP290, AIPL1, GUCY2D, RPGR, CRX |
| Choroid Diseases · HP_0000610 | CHM, ABCA4, BEST1, RPE65, EYS, CEP290, CRB1, MFRP |
| Abnormal cornea morphology · HP_0000481 | COL18A1, ZNF469, TGFBI, PAX6, FOXC1, PITX2, CHST6, KRT12, COL4A5, LCAT |
| Abnormal eye morphology · HP_0012372 | PAX6, FOXC1, PITX2, BCOR, OTX2, SOX2, CYP1B1, FBN1, COL2A1, MYOC |

**Why these rows answer the question.** Each panel is the recognized molecular basis of the ocular phenotype BioHealthKG records clinically: ABCA4, RHO, RPE65, USH2A, EYS, CEP290 and RPGR for retinal dystrophy; the choroideremia gene CHM plus BEST1 and MFRP for choroidal disease; the keratoconus/dystrophy set COL18A1, ZNF469, TGFBI and CHST6 for corneal abnormality; and the developmental master regulators PAX6, FOXC1, PITX2, SOX2 and OTX2 for abnormal eye morphology. The clinical concept identity comes only from BioHealthKG, the marker genes only from ProKN, and the UMLS↔HP bridge is what puts them in one row.

## SPARQL query executed
#### Query 1
_2026-06-27 · `biohealth`, `prokn`, `ubergraph` · ocular phenotypes paired with named ProKN marker genes_
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX pbl: <https://biolink.github.io/biolink-model/>
PREFIX oio: <http://www.geneontology.org/formats/oboInOwl#>
# CW D25-Q2 (biohealth x prokn, UMLS<->HP via ubergraph): eye deep dive. Each row pairs a
# specific ocular HP phenotype (tracked by biohealth via UMLS CUI -> clinical label) with the
# named ProKN marker genes evidencing that HP term.
SELECT ?phenotype ?bhLabel (GROUP_CONCAT(DISTINCT ?markerGene; SEPARATOR=", ") AS ?markerGenes) WHERE {
  VALUES ?hp {
    <http://purl.obolibrary.org/obo/HP_0000556>   # Retinal dystrophy
    <http://purl.obolibrary.org/obo/HP_0000610>   # Abnormal choroid morphology (Choroid Diseases)
    <http://purl.obolibrary.org/obo/HP_0000481>   # Abnormal cornea morphology
    <http://purl.obolibrary.org/obo/HP_0012372>   # Abnormal eye morphology
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?hp rdfs:label ?phenotype ; oio:hasDbXref ?x .
    FILTER(STRSTARTS(STR(?x),'UMLS:'))
    BIND(STRAFTER(STR(?x),'UMLS:') AS ?cui)
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh rdfs:label ?bhLabel }
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?stmt rdf:object ?hp ; rdf:predicate pbl:associated_with ; rdf:subject ?g .
    ?g rdfs:label ?markerGene .
    FILTER(STRSTARTS(STR(?g),'https://www.ensembl.org/id/'))
  }
}
GROUP BY ?phenotype ?bhLabel LIMIT 10
```
_4 row(s) — marker-gene lists abbreviated above to named representatives_

| phenotype | bhLabel | markerGenes (representative) |
| --- | --- | --- |
| Retinal dystrophy | Retinal dystrophy | ABCA4, RHO, RPE65, PRPH2, USH2A, CRB1, EYS, CEP290, AIPL1, GUCY2D, RPGR, CRX, … |
| Abnormal choroid morphology | Choroid Diseases | CHM, ABCA4, BEST1, RPE65, EYS, CEP290, TIMP3, NR2E3, CRB1, MFRP, … |
| Abnormal cornea morphology | Abnormal cornea morphology | COL18A1, ZNF469, TGFBI, PAX6, FOXC1, PITX2, CHST6, KRT12, COL4A5, LCAT, … |
| Abnormal eye morphology | Abnormal eye morphology | PAX6, FOXC1, PITX2, BCOR, OTX2, SOX2, CYP1B1, FBN1, COL2A1, MYOC, … |

## Literature validation

According to PubMed, Fabian-Morales et al., *Am J Med Genet A* 2025, on inherited retinal dystrophies note that mutations in more than 300 genes cause these monogenic diseases and report causal variants in USH2A and EYS in retinitis-pigmentosa / Usher probands — corroborating the ProKN retinal-dystrophy marker panel (ABCA4, RHO, RPE65, USH2A, EYS, CEP290 …) this UMLS↔HP join pairs with the BioHealthKG "Retinal dystrophy" concept. [PMID:40454438](https://pubmed.ncbi.nlm.nih.gov/40454438/) · [DOI](https://doi.org/10.1002/ajmg.a.64139)

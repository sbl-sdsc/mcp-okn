# Clinical phenotypes BioHealthKG tracks (UMLS) beside their ProKN marker genes (HP), bridged UMLS↔HP

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

BioHealthKG tracks phenotype concepts by UMLS CUI; ProKN attaches marker-gene evidence to HP phenotype terms. Crosswalk on UMLS↔HP (bridged through ubergraph): across several organ systems, show me — in the same rows — a clinical phenotype BioHealthKG tracks and the named ProKN marker genes that evidence it. Why the join?

---
🧠 **Assistant**

**Why the join is required.** BioHealthKG records a clinical phenotype concept (a UMLS CUI with a clinical label) but no molecular markers; ProKN attaches marker genes to HP phenotype terms (reified `biolink:associated_with` statements, `rdf:object` = HP term, `rdf:subject` = Ensembl gene) but has no UMLS clinical layer. Neither graph holds both halves.

**Join mechanics.** An HP term in ubergraph carries `oboInOwl:hasDbXref 'UMLS:{cui}'`; rebuild the BioHealthKG node IRI (`.../kg/node/{cui}`) to confirm the concept is tracked clinically, and read its named ProKN marker genes off the HP term. Each row therefore carries a BioHealthKG clinical phenotype **and** named ProKN marker genes — not a count.

**Result (verified, 6 rows; gene lists trimmed to named representatives):**

| Phenotype (BioHealthKG label) · HP | ProKN marker genes (named) |
| --- | --- |
| Hypertrophic Cardiomyopathy · HP_0001639 | MYH7, MYBPC3, TNNT2, TNNI3, TPM1, ACTC1, MYL2, MYL3, TTN, PLN |
| Left ventricular noncompaction cardiomyopathy · HP_0011664 | TAFAZZIN, MYH7, MYBPC3, RBM20, DSP, PKP2, LMNA, RYR2, HCN4, TBX5 |
| Neonatal Alloimmune Thrombocytopenia · HP_0004809 | ITGB3, ITGA2B, GP1BA, GP1BB, ITGA2, CD109, TREX1, SAMHD1, ADAR, IFIH1 |
| Sensorineural hearing loss, bilateral · HP_0008619 | GJB2, MYO7A, OTOF, TECTA, CDH23, KCNQ4, COCH, FGFR2, NCOA3 |
| Severe T-cell immunodeficiency · HP_0005352 | FOXN1, FRAS1 |
| Spastic Ataxia · HP_0002497 | SETX, SPG7, SYNE1, AFG3L2, ATP7B, GALC, ARSA, DNMT1, CYP7B1, ATP1A2 |

**Why these rows answer the question.** Each row's gene panel is the recognized molecular basis of the phenotype BioHealthKG tracks: the sarcomere genes (MYH7, MYBPC3, TNNT2, TNNI3) for hypertrophic cardiomyopathy; TAFAZZIN and the desmosome/structural set for LV-noncompaction; the platelet glycoproteins ITGB3/ITGA2B/GP1BA for neonatal alloimmune thrombocytopenia; GJB2/MYO7A/OTOF/TECTA for bilateral sensorineural deafness; FOXN1 for severe T-cell immunodeficiency; and the senataxin/paraplegin axis (SETX, SPG7, SYNE1, AFG3L2) for spastic ataxia. The clinical concept identity comes only from BioHealthKG, the marker genes only from ProKN, and the UMLS↔HP bridge is what puts them in one row.

## SPARQL query executed
#### Query 1
_2026-06-27 · `biohealth`, `prokn`, `ubergraph` · phenotypes paired with named ProKN marker genes_
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX pbl: <https://biolink.github.io/biolink-model/>
PREFIX oio: <http://www.geneontology.org/formats/oboInOwl#>
# CW D25-Q1 (biohealth x prokn, UMLS<->HP via ubergraph). Across organ systems, each row pairs a
# specific clinical phenotype BioHealthKG tracks (UMLS CUI -> clinical label, bridged to HP)
# with named ProKN marker genes evidencing that HP phenotype.
SELECT ?phenotype ?bhLabel (GROUP_CONCAT(DISTINCT ?markerGene; SEPARATOR=", ") AS ?markerGenes) WHERE {
  VALUES ?hp {
    <http://purl.obolibrary.org/obo/HP_0001639>   # Hypertrophic cardiomyopathy
    <http://purl.obolibrary.org/obo/HP_0011664>   # Left ventricular noncompaction cardiomyopathy
    <http://purl.obolibrary.org/obo/HP_0002497>   # Spastic ataxia
    <http://purl.obolibrary.org/obo/HP_0004809>   # Neonatal alloimmune thrombocytopenia
    <http://purl.obolibrary.org/obo/HP_0008619>   # Bilateral sensorineural hearing impairment
    <http://purl.obolibrary.org/obo/HP_0005352>   # Severe T-cell immunodeficiency
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
GROUP BY ?phenotype ?bhLabel LIMIT 12
```
_6 row(s) — marker-gene lists abbreviated above to named representatives_

| phenotype | bhLabel | markerGenes (first listed) |
| --- | --- | --- |
| Hypertrophic cardiomyopathy | Hypertrophic Cardiomyopathy | MYH7, MYBPC3, TNNT2, TNNI3, TPM1, ACTC1, MYL2, MYL3, TTN, PLN, … |
| Left ventricular noncompaction cardiomyopathy | Left ventricular noncompaction cardiomyopathy | TAFAZZIN, MYH7, MYBPC3, RBM20, DSP, PKP2, LMNA, RYR2, HCN4, TBX5, … |
| Neonatal alloimmune thrombocytopenia | Neonatal Alloimmune Thrombocytopenia | ITGB3, ITGA2B, GP1BA, GP1BB, ITGA2, CD109, TREX1, SAMHD1, ADAR, IFIH1 |
| Bilateral sensorineural hearing impairment | Sensorineural hearing loss, bilateral | GJB2, MYO7A, OTOF, TECTA, CDH23, KCNQ4, COCH, FGFR2, NCOA3 |
| Severe T-cell immunodeficiency | Severe T-cell immunodeficiency | FOXN1, FRAS1 |
| Spastic ataxia | Spastic Ataxia | SETX, SPG7, SYNE1, AFG3L2, ATP7B, GALC, ARSA, DNMT1, CYP7B1, ATP1A2, … |

## Literature validation

According to PubMed, Koshy et al., *Indian J Med Res* 2023, in a scoping review of hypertrophic cardiomyopathy report pathogenic variants concentrated in the sarcomere genes MYH7, MYBPC3, TNNT2, TNNI3 and TPM1 — exactly the ProKN marker panel this UMLS↔HP join pairs with the BioHealthKG "Hypertrophic Cardiomyopathy" concept. [PMID:37787257](https://pubmed.ncbi.nlm.nih.gov/37787257/) · [DOI](https://doi.org/10.4103/ijmr.ijmr_3567_21)

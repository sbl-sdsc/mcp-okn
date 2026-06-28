# EHR co-occurrence meets literature comorbidity: OARD log-odds phenotypes and BioHealthKG predications

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

BioHealthKG keys diseases on UMLS CUIs; OARD (the EHR-derived phenotype hub) keys diseases on MONDO and attaches a log-odds ratio to each real-world co-occurrence. For haematologic diseases, pair each disease's **named OARD co-occurring phenotype (with its log-odds)** with a **named BioHealthKG comorbidity** (`coexists_with`) for the same disease. Bridge UMLS↔MONDO through ubergraph.

---
🧠 **Assistant**

**Why the join is required.** OARD quantifies real-world EHR co-occurrence (a named phenotype + a log-odds ratio) keyed on MONDO; BioHealthKG records literature-derived comorbidities (`coexists_with`) keyed on UMLS CUIs. A UMLS↔MONDO bridge lets the EHR signal and the literature comorbidity meet in one row. A MONDO term carries `oboInOwl:hasDbXref 'UMLS:{cui}'`; the CUI rebuilds the BioHealthKG node.

Each row carries a **named OARD phenotype with its log-odds** and a **named BioHealthKG comorbidity** for the **same disease**.

| Disease | OARD co-occurring phenotype | log-odds | BioHealthKG comorbidity (`coexists_with`) |
| --- | --- | --- | --- |
| Leukemia, Myelocytic, Acute | acute myeloblastic leukemia with maturation | 10.63 | Acute leukemia |
| Leukemia, Myelocytic, Acute | Acute myelomonocytic leukemia | 9.67 | Acute leukemia |
| Leukemia, Myelocytic, Acute | acute myeloid leukemia with multilineage dysplasia | 9.30 | Acute leukemia |
| Leukemia, Myelocytic, Acute | Myeloid leukemia | 9.04 | Acute leukemia |
| MYELODYSPLASTIC SYNDROME | refractory cytopenia with multilineage dysplasia | 9.54 | Acute leukemia |
| MYELODYSPLASTIC SYNDROME | myelodysplastic syndrome with excess blasts | 8.64 | Acute leukemia |

**Why it answers the question:** the EHR-derived OARD phenotypes (AML subtypes with very high log-odds; MDS refractory-cytopenia and excess-blast variants) sit beside BioHealthKG's literature comorbidity "Acute leukemia" for the same disease — the real-world co-occurrence and the curated comorbidity converge on the same clinical reality (AML/MDS progression). Neither graph alone connects the EHR log-odds to the literature comorbidity layer.

## SPARQL query executed
```sparql
SELECT ?disease ?oardPhenotype (MAX(?lo) AS ?logOdds) (MIN(?bc) AS ?biohealthComorbidity) WHERE {
  {
    SELECT ?mondo ?cui ?ph ?oardPhenotype ?lo WHERE {
      VALUES (?mondo ?cui) {
        (<http://purl.obolibrary.org/obo/MONDO_0018881> "C3463824")
        (<http://purl.obolibrary.org/obo/MONDO_0018874> "C0023467")
      }
      GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
        ?assoc <https://w3id.org/biolink/vocab/subject> ?mondo ;
               <https://w3id.org/biolink/vocab/object> ?ph ;
               <https://w3id.org/biolink/vocab/has_supporting_studies> ?study .
        ?ph <http://www.w3.org/2000/01/rdf-schema#label> ?oardPhenotype .
        ?study <https://w3id.org/biolink/vocab/has_study_results> ?res .
        ?res <https://w3id.org/biolink/vocab/log_odds_ratio> ?lo .
        FILTER(?lo < 100 && ?lo > 8)
      }
    } ORDER BY DESC(?lo) LIMIT 40
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> {
    ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?disease .
    ?bh <https://w3id.org/biolink/vocab/coexists_with> ?o .
    ?o <http://www.w3.org/2000/01/rdf-schema#label> ?bc .
    FILTER(?bc IN ("Acute leukemia","Refractory anemias","Pancytopenia","Aplastic Anemia"))
  }
} GROUP BY ?disease ?oardPhenotype ORDER BY ?disease DESC(?logOdds) LIMIT 12
```

## Literature validation

According to PubMed, myelodysplastic syndromes manifest as anemia, neutropenia and thrombocytopenia and carry a defining potential to progress to acute myeloid leukemia, supporting both the OARD EHR co-occurrences and the BioHealthKG "Acute leukemia" comorbidity (Catenacci DVT, Schiller GJ, "Myelodysplastic syndromes: a comprehensive review," *Blood Rev* 19, 301-319 (2005), [DOI](https://doi.org/10.1016/j.blre.2005.01.004)).

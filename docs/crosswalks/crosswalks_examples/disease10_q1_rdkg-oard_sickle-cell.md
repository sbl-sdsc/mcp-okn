# CW10-Q1 rdkg×oard-kg (MONDO) — sickle cell disease OARD phenotypes + rdkg treating drugs

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>

## Conversation

👤 **User**

CW10 (rdkg × oard-kg, shared key MONDO), Q1: For sickle cell disease (MONDO_0011382), what are the strongest OARD EHR phenotypes and the number of rdkg DrugBank treating agents? Why the join?

---

🧠 **Assistant**

**Crosswalk:** rdkg × oard-kg · **Shared identifier:** MONDO (MONDO_0011382 = sickle cell disease). rdkg attaches DrugBank `treats` drugs to the MONDO; OARD attaches EHR `log_odds_ratio` phenotypes to the same MONDO.

**Why the join is required:** rdkg holds the drug layer (treating agents) but no EHR phenotype enrichment; OARD holds the phenotype log-odds but no drug list. Pairing a rare disease's real-world phenotype signature with its treating-drug count needs both on MONDO.

**Result (verified):** 8 rows, non-empty, hematologically specific. Sample (phenotype | log-odds | treating drugs):

| OARD EHR phenotype | log-odds | rdkg treating drugs |
|---|---|---|
| Sickled erythrocytes | 8.83 | 11 |
| Persistence of hemoglobin F | 6.97 | 11 |
| Howell-Jolly bodies | 5.98 | 11 |
| Reticulocytopenia | 5.10 | 11 |
| Renal papillary necrosis | 4.62 | 11 |

**Why these rows answer the question:** the phenotypes are pathognomonic sickle-cell findings (sickled erythrocytes, persistence of HbF, Howell-Jolly bodies from functional asplenia, renal papillary necrosis), and they sit beside the count of rdkg treating agents (11) — exactly the phenotype-plus-therapy view requested.

**Literature validation (PubMed, thorough):** According to PubMed, Kavanagh et al., *JAMA* 2022 ([10.1001/jama.2022.10233](https://doi.org/10.1001/jama.2022.10233)) confirm hydroxyurea (which increases fetal hemoglobin and reduces red-cell sickling) is first-line SCD therapy, with L-glutamine, crizanlizumab and voxelotor as additional agents — validating both the 'Persistence of hemoglobin F' phenotype mechanism and rdkg's multi-drug treating set. **Kept.**

## SPARQL queries executed

#### Query 1

_2026-06-17 · `rdkg`, `oard-kg`_

```sparql
SELECT ?hp ?hpLabel ?logOddsRatio ?rdkgTreatingDrugCount WHERE {
  BIND(<http://purl.obolibrary.org/obo/MONDO_0011382> AS ?mondo)
  {
    SELECT (COUNT(DISTINCT ?drug) AS ?rdkgTreatingDrugCount) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/rdkg> {
        ?drug <https://w3id.org/biolink/vocab/treats> <http://purl.obolibrary.org/obo/MONDO_0011382> .
        FILTER(STRSTARTS(STR(?drug),'http://identifiers.org/drugbank/'))
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
    ?assoc <https://w3id.org/biolink/vocab/subject> ?mondo ;
           <https://w3id.org/biolink/vocab/object> ?hp ;
           <https://w3id.org/biolink/vocab/has_supporting_studies> ?study .
    FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_'))
    OPTIONAL { ?hp <http://www.w3.org/2000/01/rdf-schema#label> ?hpLabel }
    ?study <https://w3id.org/biolink/vocab/has_study_results> ?res .
    ?res <https://w3id.org/biolink/vocab/log_odds_ratio> ?logOddsRatio .
    FILTER(?logOddsRatio < 100)
  }
}
ORDER BY DESC(?logOddsRatio)
LIMIT 8
```

_8 row(s) — showing first 5_

| hp | hpLabel | logOddsRatio | rdkgTreatingDrugCount |
| --- | --- | --- | --- |
| http://purl.obolibrary.org/obo/HP_0030058 | Sickled erythrocytes | 8.833032 | 11 |
| http://purl.obolibrary.org/obo/HP_0011904 | Persistence of hemoglobin F | 6.96927 | 11 |
| http://purl.obolibrary.org/obo/HP_0020081 | Pappenheimer bodies | 6.470198 | 11 |
| http://purl.obolibrary.org/obo/HP_0032550 | Howell-Jolly bodies | 5.982856 | 11 |
| http://purl.obolibrary.org/obo/HP_0001896 | Reticulocytopenia | 5.101584 | 11 |

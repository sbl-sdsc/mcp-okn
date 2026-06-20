# Taxonomy Crosswalk 10 Q2 — N. gonorrhoeae AMR (SPOKE) + gonorrhea datasets (NDE)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `nde` — <https://purl.org/okn/frink/kg/nde>

## Conversation

👤 **User**

For Neisseria gonorrhoeae (NCBITaxon:485), what antimicrobial-resistance phenotypes does SPOKE-OKN record at strain level, and how many NDE gonorrhea datasets exist? Join spoke-okn and nde on NCBITaxon:485.

---

🧠 **Assistant**

Joining on NCBITaxon:485 links strain-level antimicrobial-resistance data to the infectious-disease dataset for the same pathogen. SPOKE-OKN records tetracycline susceptibility phenotypes across *N. gonorrhoeae* strains: **4 strains classified Tetracycline-Susceptible and 3 strains Tetracycline-Resistant**. NDE holds **1 gonorrhea dataset** for the species.

The rows answer the question and show the integration value: for a single WHO priority pathogen, SPOKE-OKN supplies the strain-level AMR phenotype (tetracycline resistant vs susceptible) while NDE supplies the disease dataset, joined on the shared NCBITaxon id. This is exactly the bridge needed to connect resistance surveillance to disease-dataset discovery — neither KG provides both.

**Literature validation (PubMed):** antimicrobial (incl. tetracycline) resistance in *Neisseria gonorrhoeae* is extensively documented — a PubMed search returns 4,050 articles (e.g. PMID 37192385, 33528603, 8994786, 35818315). Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?drug ?resistantPhenotype (COUNT(DISTINCT ?ot) AS ?gonorrhoeaeStrains) ?gonorrheaNDEdatasets WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?ot a biolink:OrganismTaxon . FILTER(REGEX(STR(?ot),'/organism/485\\.'))
    ?stmt rdf:subject ?ot ; rdf:predicate spoke:RESPONDS_TO_OrC ; rdf:object ?chem ; spoke:resistant_phenotype ?resistantPhenotype .
    OPTIONAL { ?chem rdfs:label ?drug }
  }
  { SELECT (COUNT(DISTINCT ?ds) AS ?gonorrheaNDEdatasets) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nde> { ?ds schema:species ?sp . FILTER(REGEX(STR(?sp),'/taxonomy/485($|[^0-9])')) } } }
}
GROUP BY ?drug ?resistantPhenotype ?gonorrheaNDEdatasets
ORDER BY DESC(?gonorrhoeaeStrains)
```

### Result (2 rows)

| drug | resistantPhenotype | gonorrhoeaeStrains | gonorrheaNDEdatasets |
| --- | --- | --- | --- |
| Tetracycline | Susceptible | 4 | 1 |
| Tetracycline | Resistant | 3 | 1 |

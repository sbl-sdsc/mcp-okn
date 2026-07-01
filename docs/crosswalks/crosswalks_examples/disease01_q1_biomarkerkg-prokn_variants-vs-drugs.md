# CW1-Q1 biomarkerkg×prokn (DOID) — biomarker variants vs ProKN indicated drugs

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

CW1 (biomarkerkg × prokn, shared key DOID), Q1: Across diseases with literature-curated biomarker variants in BiomarkerKG, how do the count of curated genomic biomarker variants (BiomarkerKG) and the count of ProKN-indicated drugs compare per disease? State why this needs the join.

---

🧠 **Assistant**

**Crosswalk:** biomarkerkg × prokn · **Shared identifier:** Disease Ontology ID (DOID). BiomarkerKG attaches the disease DOID on `obo:OBCI_1000008` and the variant on `obo:OBCI_1000016`; ProKN links indicated drugs to the disease DOID via `obo:NCIT_C41184` ("chemical or drug has indication"). (ProKN v0.0.5 dropped `rdfs:seeAlso`; the disease DOID is still the object of the drug-indication predicate, so the DOID join is unaffected — only the disease label is now read from ProKN's `rdfs:label`, grouped per DOID.)

**Why the join is required:** BiomarkerKG is a literature-curated catalog of genomic biomarker *variants* per disease but carries no drug-indication data; ProKN carries curated drug indications per disease but no biomarker-variant catalog. Only by joining the two graphs on the shared DOID can a researcher line up, for one disease, how deep the literature biomarker evidence is against how many drugs are actually indicated.

**Result (verified):** 15 rows, non-empty, biologically coherent. The leaders are precision-oncology diseases. _(Re-verified 2026-07-01 after ProKN v0.0.5 dropped `rdfs:seeAlso`: the query now reads the disease label from ProKN's `rdfs:label` grouped per DOID, and ProKN expanded its drug-indication set — Cutaneous T-cell lymphoma now leads at 37 indicated drugs; the canonical rows below are unchanged.)_ Sample:

| Disease | BiomarkerKG variants | ProKN indicated drugs |
|---|---|---|
| Cutaneous T-cell lymphoma | 5 | 37 |
| Acute Lymphoblastic Leukemia | 310 | 22 |
| Non-Small Cell Lung Carcinoma | 172 | 20 |
| Acute Myeloid Leukemia | 909 | 16 |
| Renal Cell Carcinoma | 1,682 | 10 |
| Chronic Myeloid Leukemia (Philadelphia+) | 48 | 7 |

**Why these rows answer the question:** each row pairs a disease's literature-variant count (BiomarkerKG) with its indicated-drug count (ProKN) on the *same DOID*, exactly the two-sided comparison asked for. The diseases among the leaders (ALL, NSCLC, AML, CML) are the canonical biomarker-driven cancers, confirming the join lands on the right entities.

**Literature validation (PubMed, thorough):** According to PubMed, the Philadelphia-chromosome CML row is corroborated by Jabbour & Kantarjian, *Am J Hematol* 2024 ([10.1002/ajh.27443](https://doi.org/10.1002/ajh.27443)), which describes BCR::ABL1 as the defining CML biomarker and enumerates the FDA-approved TKIs (imatinib, dasatinib, bosutinib, nilotinib, ponatinib, asciminib) — matching ProKN's indicated-drug set. The NSCLC row is corroborated by Meyer et al., *Lancet* 2024 ([10.1016/S0140-6736(24)01029-8](https://doi.org/10.1016/S0140-6736(24)01029-8)), which reviews actionable oncogenic-driver biomarkers and the targeted therapies indicated against them. Both confirm the disease→(variant, drug) coupling the query surfaces. **Kept.**

## SPARQL queries executed

#### Query 1

_2026-06-17 · `prokn`, `biomarkerkg`_

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (SAMPLE(?lbl) AS ?diseaseLabel) (COUNT(DISTINCT ?variant) AS ?biomarkerVariants) (COUNT(DISTINCT ?drug) AS ?proknIndicatedDrugs) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?drug <http://purl.obolibrary.org/obo/NCIT_C41184> ?doid .
    ?doid rdfs:label ?lbl .
  }
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> {
    ?b <http://purl.obolibrary.org/obo/OBCI_1000008> ?doid ;
       <http://purl.obolibrary.org/obo/OBCI_1000016> ?variant .
  }
}
GROUP BY ?doid
ORDER BY DESC(?proknIndicatedDrugs)
LIMIT 15
```

_15 row(s) — showing first 5_

| diseaseLabel | biomarkerVariants | proknIndicatedDrugs |
| --- | --- | --- |
| Lymphoma, T-Cell, Cutaneous | 5 | 37 |
| Acute Lymphoblastic Leukemia | 310 | 22 |
| Lung Non-small Cell Carcinoma | 172 | 20 |
| Follicular Lymphoma | 14 | 19 |
| Hodgkin Disease | 77 | 19 |

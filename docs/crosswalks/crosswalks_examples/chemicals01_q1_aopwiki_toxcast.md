# Chemicals Use Case 1 — AOP-Wiki × ToxCast (CAS)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Domain:** Chemicals · **Shared identifier:** CAS Registry Number

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki> (AOP-Wiki: Adverse Outcome Pathways and their chemical stressors)
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast> (EPA ToxCast high-throughput in-vitro screening)

**Join:** AOP-Wiki stressor `aop:has_chemical_entity` → CAS  JOIN  ToxCast `edam:has_identifier` → CAS (290 shared chemicals; verified 2026-06-12). AOP-Wiki encodes CAS as `https://identifiers.org/cas/...`, ToxCast as `http://identifiers.org/cas/...`, so the join applies an `http(s)` IRI rewrite.

## Research questions

- **Q1.** Which chemical stressors of Adverse Outcome Pathways (AOP-Wiki) are also screened in EPA ToxCast, and in how many ToxCast assay endpoints is each tested?
- **Q2.** Among those AOP-stressor chemicals, which show the most *active* ToxCast hit calls (hitcall = 1.0)?

Both questions genuinely require the join: AOP-Wiki alone says *which* chemicals are AOP stressors but has no assay data; ToxCast alone has assay/activity data but does not know which chemicals are AOP stressors. Only the CAS join connects "is an AOP stressor" to "ToxCast assay coverage / activity."

---

## Q1 — AOP stressors ranked by ToxCast assay-endpoint coverage

```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX edam: <http://edamontology.org/>
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT ?chem (REPLACE(STR(?cas2),'http://identifiers.org/cas/','') AS ?CAS) (COUNT(DISTINCT ?mg) AS ?nAssayEndpoints) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?s aop:has_chemical_entity ?cas ; dc:title ?chem .
  }
  BIND(IRI(REPLACE(STR(?cas),'https://identifiers.org/cas/','http://identifiers.org/cas/')) AS ?cas2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
    ?t edam:has_identifier ?cas2 ;
       ro:RO_0000056 ?mg .
  }
}
GROUP BY ?chem ?cas2
ORDER BY DESC(?nAssayEndpoints)
LIMIT 12
```

**Result (12 rows, top 8 shown):**

| Chemical | CAS | ToxCast assay endpoints |
|---|---|---|
| Perfluorooctanesulfonic acid (PFOS) | 1763-23-1 | 1510 |
| Bisphenol A | 80-05-7 | 1414 |
| Mancozeb | 8018-01-7 | 1351 |
| Triclosan | 3380-34-5 | 1316 |
| Cypermethrin | 52315-07-8 | 1274 |
| Maneb | 12427-38-2 | 1269 |
| Prochloraz | 67747-09-5 | 1258 |
| Diethylstilbestrol | 56-53-1 | 1237 |

**Why this answers the question:** every row is a chemical that AOP-Wiki records as an Adverse Outcome Pathway stressor *and* that ToxCast has assayed; the count is the number of distinct ToxCast assay-endpoint measure-groups the chemical participates in. The top of the list — PFOS, Bisphenol A, dithiocarbamate fungicides, triclosan, synthetic estrogens, pyrethroids — is exactly the set of endocrine-disrupting / pesticide stressors one expects to be both AOP-relevant and exhaustively screened.

---

## Q2 — most active in ToxCast (hitcall = 1.0)

Restricted to six top endocrine-disruptor stressors (via `VALUES`) so the hit-call expansion stays performant.

```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX edam: <http://edamontology.org/>
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT ?chem ?casNum (COUNT(DISTINCT ?hit) AS ?nActiveEndpoints) WHERE {
  VALUES ?casNum { "1763-23-1" "80-05-7" "3380-34-5" "56-53-1" "115-29-7" "67747-09-5" }
  BIND(IRI(CONCAT('https://identifiers.org/cas/',?casNum)) AS ?casA)
  BIND(IRI(CONCAT('http://identifiers.org/cas/',?casNum)) AS ?casT)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?s aop:has_chemical_entity ?casA ; dc:title ?chem .
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
    ?t edam:has_identifier ?casT ;
       ro:RO_0000056 ?mg .
    ?mg <http://purl.obolibrary.org/obo/OBI_0000299> ?hit .
    ?hit <http://semanticscience.org/resource/SIO_000300> ?v .
    FILTER(STR(?v) = "1.0")
  }
}
GROUP BY ?chem ?casNum
ORDER BY DESC(?nActiveEndpoints)
```

**Result (6 rows):**

| Chemical | CAS | Active ToxCast endpoints |
|---|---|---|
| Triclosan | 3380-34-5 | 537 |
| Perfluorooctanesulfonic acid (PFOS) | 1763-23-1 | 480 |
| Diethylstilbestrol | 56-53-1 | 470 |
| Endosulfan | 115-29-7 | 393 |
| Prochloraz | 67747-09-5 | 391 |
| Bisphenol A | 80-05-7 | 375 |

**Why this answers the question:** each count is the number of ToxCast endpoints in which the AOP stressor returned a positive hit call (`hitcall = 1.0`) — i.e. *measured bioactivity*, not just assay coverage. Diethylstilbestrol (a potent synthetic estrogen) and triclosan showing several hundred active endpoints is biologically coherent.

---

## Literature validation

According to PubMed, Ehrlich D, Krishna S, Kleinstreuer N (2024). "Data-driven derivation of an adverse outcome pathway linking vascular endothelial growth factor receptor (VEGFR), endocrine disruption, and atherosclerosis." *ALTEX* 41(4):617–632. [DOI: 10.14573/altex.2403211](https://doi.org/10.14573/altex.2403211).

The paper explicitly builds an Adverse Outcome Pathway from **ToxCast/Tox21** high-throughput screening bioprofiles and names **bisphenols, triclosan, DDT and PCBs** as the relevant chemical stressors — directly confirming (a) that AOP chemical stressors are ToxCast-screened and (b) that Bisphenol A and Triclosan are bioactive endocrine-disruptor stressors, matching the join output. ToxCast estrogen-receptor bioactivity models (e.g. PubMed 26066997) further support the activity scoring used in Q2.

**Verdict:** both queries run without error, return non-empty and biologically plausible results, and are corroborated by the literature. PASS - Retained.

## Sources

- PubMed via mcp-okn federation. Ehrlich et al. 2024, ALTEX. [DOI: 10.14573/altex.2403211](https://doi.org/10.14573/altex.2403211)

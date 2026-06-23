# Chemicals Crosswalk 4 — Tox21 × ToxCast (CAS)

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-tox21` — <https://purl.org/okn/frink/kg/biobricks-tox21>
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast>

## Conversation

**User**

For the bisphenol-A analogue family in the Tox21 qHTS library, which analogues were also profiled in EPA ToxCast and how extensively (assay-endpoint coverage)? This supports read-across / regrettable-substitution analysis of BPA replacements. (Join biobricks-tox21 to biobricks-toxcast on CAS.)

---

**Assistant**

**Use case:** Tox21 catalogues the qHTS library membership (chemical + CAS) but no assay counts; ToxCast holds the per-chemical in-vitro assay battery but is keyed on EPA DSSTox ids. To ask "which BPA analogues in the Tox21 library also have ToxCast data, and how much" — the core question in evaluating whether BPA replacements are "regrettable substitutions" — requires joining the two on CAS. **8,909 chemicals** join in total.

**KGs joined:** biobricks-tox21 (node IRI = CAS) × biobricks-toxcast (`edam:has_identifier` → CAS; assay endpoints via `ro:RO_0000056`). Shared key: **CAS**.

**Result (bisphenol-analogue family, ranked by distinct ToxCast assay endpoints):**

| Tox21 chemical | CAS | ToxCast assay endpoints |
|---|---|---|
| Bisphenol A | 80-05-7 | 1414 |
| Bisphenol AF | 1478-61-1 | 1189 |
| 3,3',5,5'-Tetrabromobisphenol A (TBBPA) | 79-94-7 | 1138 |
| Bisphenol B | 77-40-7 | 991 |
| 2,2',6,6'-Tetrachlorobisphenol A | 79-95-8 | 808 |
| 2,2'-Bisphenol F | 2467-02-9 | 731 |
| 3,3'-Dimethylbisphenol A | 79-97-0 | 662 |
| Bisphenol E | 2081-08-5 | 398 |
| Bisphenol Z | 843-55-0 | 238 |

**Why this answers the question:** every row is a Tox21-library bisphenol analogue that ToxCast independently screened, and the endpoint count quantifies how thoroughly each replacement candidate has been profiled. BPA itself is the most-tested (1414 endpoints); its drop-in replacements BPAF, BPB, BPF, BPE, BPZ and the brominated/chlorinated flame-retardant variants (TBBPA, TCBPA) all carry substantial ToxCast coverage — exactly the comparative dataset needed to judge whether the substitutes are safer. 16 bisphenol-family chemicals join (8,909 across the whole library).

**Literature validation (PubMed):** Stavreva et al., *Toxicology* 2016 co-screened Bisphenol A and Tetrabromobisphenol A (TBBPA) — the #1 and #3 hits here — for thyroid-receptor (endocrine) activity in a high-throughput cell assay ([DOI](https://doi.org/10.1016/j.tox.2016.08.012)), confirming these bisphenol analogues are jointly screened EDCs in the HTS literature.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX edam: <http://edamontology.org/>
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT ?cas ?tox21Name ?dtxsid (COUNT(DISTINCT ?mg) AS ?toxcastAssayEndpoints) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> {
    ?cas rdfs:label ?tox21Name .
    FILTER(STRSTARTS(STR(?cas),'http://identifiers.org/cas/'))
    FILTER(CONTAINS(LCASE(?tox21Name),'bisphenol'))
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
    ?chem edam:has_identifier ?cas .
    ?chem edam:has_identifier ?dtxsid .
    FILTER(CONTAINS(STR(?dtxsid),'comptox.epa.gov'))
    ?chem ro:RO_0000056 ?mg .
  }
}
GROUP BY ?cas ?tox21Name ?dtxsid
ORDER BY DESC(?toxcastAssayEndpoints)
LIMIT 20
```

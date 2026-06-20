# Chemicals Use Case 3 — Tox21 × ICE (CAS)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Chemicals · **Shared identifier:** CAS Registry Number

## Knowledge graphs used

- `biobricks-tox21` — <https://purl.org/okn/frink/kg/biobricks-tox21> (Tox21 ~10K screening-library chemicals; CAS-keyed nodes with names)
- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice> (NICEATM Integrated Chemical Environment: curated HTS, ADME/toxicokinetics, DART, endocrine)

**Join:** Tox21 keys each chemical as its own node IRI `http://identifiers.org/cas/...`, which is exactly the value ICE carries as the object of `edam:has_identifier` — a direct CAS join, no rewrite (8,916 shared chemicals; verified 2026-06-12).

## Research questions

- **Q1.** How many chemicals in the Tox21 screening library are also covered by each ICE curated-data domain?
- **Q2.** Which Tox21-library chemicals have human in-vitro toxicokinetic (httk) ADME parameters in ICE — the unbound-plasma-fraction and hepatic-clearance values needed for in-vitro-to-in-vivo extrapolation (IVIVE)?

Both require the join: Tox21 supplies only library membership + chemical identity; ICE supplies the curated toxicokinetic/toxicity data. Connecting "is in the Tox21 library" to "has ICE httk parameters" is only possible via the shared CAS.

---

## Q1 — ICE data-domain coverage of the Tox21 library

```sparql
PREFIX edam: <http://edamontology.org/>
SELECT ?iceDomain (COUNT(DISTINCT ?cas) AS ?nSharedChem) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> {
    ?cas a <http://purl.obolibrary.org/obo/CHEMINF_000446> .
    FILTER(STRSTARTS(STR(?cas),'http://identifiers.org/cas/'))
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?s edam:has_identifier ?cas .
    BIND(REPLACE(STR(?s),'^http://example.com/ice/([^/]+)\\.parquet.*$','$1') AS ?iceDomain)
  }
}
GROUP BY ?iceDomain
ORDER BY DESC(?nSharedChem)
```

**Result (6 rows):**

| ICE data domain | Tox21-library chemicals covered |
|---|---|
| cHTS2022 (curated high-throughput screening) | 8913 |
| Chemical Functional Use Categories | 4299 |
| ADME Parameters (toxicokinetics) | 1410 |
| DART (developmental & reproductive toxicity) | 508 |
| Endocrine — In Vivo | 193 |
| Endocrine — In Vitro | 157 |

**Why this answers the question:** each row is the number of Tox21-library chemicals carrying that class of ICE curation. Almost the entire Tox21 library is represented in ICE's curated HTS (8,913), and ICE adds toxicokinetic parameters for 1,410 of them and in-vivo reproductive/endocrine data for several hundred.

---

## Q2 — Tox21 chemicals with ICE human httk (IVIVE) parameters

```sparql
PREFIX edam: <http://edamontology.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ro: <http://purl.obolibrary.org/obo/>
SELECT DISTINCT ?label (REPLACE(STR(?cas),'http://identifiers.org/cas/','') AS ?CAS)
       (REPLACE(REPLACE(?raw,'%20',' '),'%2C',',') AS ?admeAssay) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> {
    ?cas a <http://purl.obolibrary.org/obo/CHEMINF_000446> ; rdfs:label ?label .
    FILTER(STRSTARTS(STR(?cas),'http://identifiers.org/cas/'))
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
    ?ch edam:has_identifier ?cas ; ro:RO_0000056 ?mg .
    FILTER(CONTAINS(STR(?ch),'ADME_Parameters'))
    BIND(REPLACE(STR(?mg),'^.*/assay/([^/]+)/Measure_Group$','$1') AS ?raw)
    FILTER(CONTAINS(?raw,'Human'))
  }
}
ORDER BY ?label
LIMIT 15
```

**Result (first rows):**

| Chemical | CAS | ICE human httk parameter |
|---|---|---|
| (+)-Diltiazem | 42399-41-7 | httk, Human Plasma Fraction Unbound |
| (+)-Diltiazem | 42399-41-7 | httk, Human Hepatic Intrinsic Clearance |
| (+/-)-Fluoxetine | 54910-89-3 | httk, Human Hepatic Intrinsic Clearance |
| (-)-Epigallocatechin gallate | 989-51-5 | httk, Human Hepatic Intrinsic Clearance |
| (-)-Gossypol | 303-45-7 | httk, Human Plasma Fraction Unbound |
| (RS)-(+/-)-sulpiride | 15676-16-1 | httk, Human Plasma Fraction Unbound |
| (+)-Tubocurarine chloride hydrochloride | 57-94-3 | httk, Human Plasma Fraction Unbound |

**Why this answers the question:** each row pairs a Tox21-library chemical with a specific ICE human toxicokinetic measurement — unbound fraction in plasma (fup) or intrinsic hepatic clearance (Clint) — the two parameters reverse-dosimetry IVIVE requires to turn an in-vitro Tox21 hit into a human-equivalent dose. The hits are recognizable drugs (diltiazem, fluoxetine, sulpiride, tubocurarine) and bioactive natural products (EGCG, gossypol), confirming relevance.

---

## Literature validation

According to PubMed, Wambaugh JF, Wetmore BA, Ring CL, et al. (2019). "Assessing Toxicokinetic Uncertainty and Variability in Risk Prioritization." *Toxicol Sci* 172(2):235–251. [DOI: 10.1093/toxsci/kfz205](https://doi.org/10.1093/toxsci/kfz205).

The paper defines high-throughput toxicokinetics (HTTK) as in-vitro measures of **unbound fraction in plasma (fup) and intrinsic hepatic clearance (Clint)** used for **IVIVE** over the **ToxCast Phase I and II libraries** (raising HTTK coverage to 57%) — i.e. precisely the two ICE httk parameters returned by Q2, applied to the same chemical libraries Tox21 screens. This confirms both the existence and the intended IVIVE use of the joined data.

**Verdict:** both queries run without error, return non-empty results, and the httk parameters and their IVIVE purpose are directly corroborated by the literature. PASS - Retained.

## Sources

- PubMed via mcp-okn federation. Wambaugh, Wetmore, Ring et al. 2019, Toxicol Sci. [DOI: 10.1093/toxsci/kfz205](https://doi.org/10.1093/toxsci/kfz205)

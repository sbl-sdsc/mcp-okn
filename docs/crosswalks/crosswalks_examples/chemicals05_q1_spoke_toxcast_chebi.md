# Chemicals Use Case 5 — SPOKE × ToxCast via CHEBI↔CAS (ubergraph bridge)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Chemicals · **Shared identifier:** CHEBI ↔ CAS (bridged through ubergraph)

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (SPOKE: compound–gene–disease associations; compounds carry CHEBI xrefs)
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph> (ontology bridge: CHEBI `oboInOwl:hasDbXref` → CAS)
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast> (EPA ToxCast in-vitro screening)

**Join (3 graphs):** SPOKE compound `oboInOwl:hasDbXref` → CHEBI  →  ubergraph CHEBI `oboInOwl:hasDbXref` → `cas:` CURIE  →  rewritten to `http://identifiers.org/cas/...`  →  ToxCast `edam:has_identifier`. 496 chemicals bridge (verified 2026-06-12). The CHEBI↔CAS step is essential: SPOKE speaks CHEBI, ToxCast speaks CAS, and only ubergraph carries the cross-reference between them.

## Research questions

- **Q1.** Which ToxCast-screened chemicals (reached from SPOKE via CHEBI) regulate the most genes in SPOKE — i.e. which screened compounds have the broadest transcriptional signature?
- **Q2.** For the iconic PAH carcinogen Benzo[a]pyrene (ToxCast-screened), which specific genes does SPOKE record it up- and down-regulating?

Both require the full three-graph bridge: SPOKE supplies the compound→gene regulation, ubergraph supplies the CHEBI→CAS mapping, and ToxCast supplies the "is screened" gate. No single KG answers either question.

---

## Q1 — ToxCast chemicals ranked by SPOKE regulated-gene count

```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX sk: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX edam: <http://edamontology.org/>
SELECT ?cmpLabel (COUNT(DISTINCT ?gene) AS ?nRegulatedGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref ?chebi .
    FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_'))
    { ?cmp sk:UPREGULATES_CuG ?gene } UNION { ?cmp sk:DOWNREGULATES_CdG ?gene }
    OPTIONAL { ?cmp rdfs:label ?cmpLabel }
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?chebi obo:hasDbXref ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:'))
  }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t edam:has_identifier ?c2 . }
}
GROUP BY ?cmpLabel
ORDER BY DESC(?nRegulatedGenes)
LIMIT 12
```

**Result (top 12):**

| Compound | Genes regulated (SPOKE) |
|---|---|
| Pentobarbital | 969 |
| Fluorouracil (5-FU) | 827 |
| Hexachlorophene | 729 |
| Thiabendazole | 288 |
| Tributyltin chloride | 222 |
| Phenytoin | 211 |
| Resorcinol | 168 |
| Phenolphthalein | 114 |
| Phenothiazine | 83 |
| Phenacetin | 26 |
| 3-Methylcholanthrene | 20 |
| Benzo[a]pyrene | 14 |

**Why this answers the question:** each compound is ToxCast-screened (verified through the CHEBI→CAS bridge) and the count is its number of distinct SPOKE up/down-regulated genes. The list is dominated by pharmacologically and toxicologically potent agents — the chemotherapeutic 5-FU, the antiseptic hexachlorophene, the organotin tributyltin, and the PAH carcinogens 3-methylcholanthrene and benzo[a]pyrene — exactly the compounds expected to carry rich transcriptional signatures.

---

## Q2 — Benzo[a]pyrene's SPOKE gene-regulation profile

```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX sk: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX edam: <http://edamontology.org/>
SELECT DISTINCT ?dir ?geneLabel (REPLACE(STR(?c2),'http://identifiers.org/cas/','') AS ?CAS) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp obo:hasDbXref ?chebi ; rdfs:label ?cmpLabel .
    FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_'))
    FILTER(?cmpLabel = "Benzo[a]pyrene")
    { ?cmp sk:UPREGULATES_CuG ?gene . BIND("up-regulates" AS ?dir) }
    UNION
    { ?cmp sk:DOWNREGULATES_CdG ?gene . BIND("down-regulates" AS ?dir) }
    ?gene rdfs:label ?geneLabel .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?chebi obo:hasDbXref ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:'))
  }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t edam:has_identifier ?c2 . }
}
ORDER BY ?dir ?geneLabel
```

**Result (14 rows; CAS 50-32-8):**

- **Up-regulates:** ALAS1, INPP1, PAK1, **TIPARP**
- **Down-regulates:** BNIP3, CCNB2, DCK, DDIT4, ENOPH1, KDM3A, OXA1L, TUBB6, UBE3C, VDAC1

**Why this answers the question:** the rows are the specific genes SPOKE records benzo[a]pyrene regulating, for a chemical confirmed to be ToxCast-screened. The standout is the up-regulation of **TIPARP** (TCDD-inducible poly-ADP-ribose polymerase) — a canonical aryl-hydrocarbon-receptor (AhR) battery gene. Benzo[a]pyrene is a prototypical AhR agonist, so inducing TIPARP is precisely the expected, mechanism-correct signal, confirming the rows are meaningful rather than arbitrary.

---

## Literature validation

According to PubMed, Grimaldi G, Rajendra S, Matthews J (2017). "The aryl hydrocarbon receptor regulates the expression of TIPARP and its cis long non-coding RNA, TIPARP-AS1." *Biochem Biophys Res Commun* 495(3):2356–2362. [DOI: 10.1016/j.bbrc.2017.12.113](https://doi.org/10.1016/j.bbrc.2017.12.113).

The paper demonstrates that the **aryl hydrocarbon receptor (AHR) is recruited to the TIPARP promoter and induces TIPARP expression**. Because benzo[a]pyrene is a classic AHR agonist, SPOKE's record of benzo[a]pyrene up-regulating TIPARP (Q2) is directly mechanistically corroborated. This confirms the three-graph CHEBI↔CAS bridge surfaces a true compound→gene relationship for a ToxCast-screened chemical.

**Verdict:** both queries run without error, return non-empty results through the 3-KG bridge, and the headline gene-regulation signal (B[a]P → TIPARP via AhR) is corroborated by the literature. PASS - Retained.

## Sources

- PubMed via mcp-okn federation. Grimaldi, Rajendra, Matthews 2017, Biochem Biophys Res Commun. [DOI: 10.1016/j.bbrc.2017.12.113](https://doi.org/10.1016/j.bbrc.2017.12.113)

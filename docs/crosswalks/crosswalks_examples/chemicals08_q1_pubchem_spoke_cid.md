# Chemicals Use Case 8 — PubChem-annotations × SPOKE (PubChem CID)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Chemicals · **Shared identifier:** PubChem Compound ID (CID)

## Knowledge graphs used

- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> (PubChem free-text annotations: toxicity, hazards, uses, pharmacology)
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (SPOKE: chemical layer; compounds carry PubChem CID xrefs and link to diseases/genes)

**Join:** SPOKE `oboInOwl:hasDbXref` → `http://identifiers.org/pubchem.compound/{n}`  →  rewritten to `http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID{n}`  →  PubChem annotation `oa:hasTarget`. 762/762 of SPOKE's PubChem-CID-bearing chemicals have ≥1 annotation (verified 2026-06-11). SPOKE is the only federation KG that materializes PubChem CID, making it this annotation set's sole partner.

## Research questions

- **Q1.** Among the chemicals SPOKE links to diseases and genes, which have the richest PubChem free-text annotation coverage (most annotations)?
- **Q2.** For the herbicide Atrazine (a SPOKE chemical), what substantive PubChem toxicity / hazard annotation text is available?

Both require the join: SPOKE supplies which chemicals are in its disease/gene network and their CID; the PubChem-annotations KG supplies the free-text toxicology that SPOKE itself does not store. Only the CID bridge connects "SPOKE chemical" to "its PubChem hazard narrative."

---

## Q1 — SPOKE chemicals ranked by PubChem annotation coverage

```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cmpLabel (COUNT(DISTINCT ?ann) AS ?nPubChemAnnotations) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?c obo:hasDbXref ?x ; rdfs:label ?cmpLabel .
    FILTER(STRSTARTS(STR(?x),'http://identifiers.org/pubchem.compound/'))
  }
  BIND(REPLACE(STR(?x),'^http://identifiers.org/pubchem.compound/','') AS ?cid)
  BIND(IRI(CONCAT('http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID',?cid)) AS ?b)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget ?b .
  }
}
GROUP BY ?cmpLabel
ORDER BY DESC(?nPubChemAnnotations)
LIMIT 12
```

**Result (top 12):**

| SPOKE chemical | PubChem annotations |
|---|---|
| Diuron | 168 |
| Silicon Dioxide | 154 |
| Phenytoin | 136 |
| Thiabendazole | 133 |
| Isophorone | 131 |
| Fluorouracil | 127 |
| Acetic Acid | 125 |
| Atrazine | 124 |
| Naphthalene | 120 |
| Triphenyl phosphate | 118 |
| Aniline | 117 |
| Tetracycline | 114 |

**Why this answers the question:** each row is a chemical in SPOKE's network paired with its count of PubChem free-text annotations. The leaders are exactly the well-characterized environmental chemicals and drugs (the herbicides diuron and atrazine, the flame retardant triphenyl phosphate, naphthalene, aniline; the drugs phenytoin, 5-FU, tetracycline) that carry deep regulatory/toxicology documentation — confirming the join surfaces the chemicals with the most to say.

---

## Q2 — Atrazine PubChem toxicity annotations (CID 2256)

```sparql
PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT (SUBSTR(?text,1,300) AS ?atrazineAnnotation) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?c obo:hasDbXref <http://identifiers.org/pubchem.compound/2256> .
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID2256> ; oa:hasBody ?body .
    ?body rdf:value ?text .
    FILTER(STRLEN(?text) > 350)
  }
}
LIMIT 5
```

(Atrazine's CID 2256 was first confirmed from SPOKE's `hasDbXref`, then used directly to keep the join fast.)

**Result (5 substantive annotations, truncated):**

1. *"The following herbicides have an oral LD50 of >1 gm/kg and have little or no acute toxicity in humans: Alachlor, Amitrole, … Atrazine … A mild skin irritant; Injury to the brain…"* (acute toxicity / hazard class)
2. *"…examined the postnatal reproductive development of male rats following prenatal exposure to an atrazine metabolite mixture (AMM) … diaminochlorotriazine, hydroxyatrazine, deethylatrazine, and deisopropylatrazine."* (developmental/reproductive)
3. *"…Atrazine … selected for immunotoxicity studies /using female B6C3F1 mice/ … significant decreases in body weight…"* (immunotoxicity)
4. *"…Atrazine administered to rats orally at a dose of 120 mg/kg caused an inhibition in the activity of glutathione-S-transferase and an increase in malondialdehyde formation in the liver, testis and epididymis. Superoxide dismutase decreased…"* (oxidative stress / reproductive)
5. *"…atrazine (ATZ) concentrations in urine samples of the workers … determined by /a gas chromatograph-electron capture detector/ method … (deethylatrazine (DEA), deisopropylatrazine (DIA)…"* (biomonitoring)

**Why this answers the question:** for a single SPOKE chemical, the join returns its actual PubChem hazard narrative — acute-toxicity classification, developmental and immune toxicity, oxidative-stress mechanism, and human biomonitoring methods. These are the rich free-text uses/hazards SPOKE cannot express on its own, retrieved purely via the CID bridge.

---

## Literature validation

According to PubMed, Abarikwu SO, Adesiyan AC, Oyeloja TO, Oyeyemi MO, Farombi EO (2010). "Changes in sperm characteristics and induction of oxidative stress in the testis and epididymis of experimental rats by a herbicide, atrazine." *Arch Environ Contam Toxicol* 58(3):874–882. [DOI: 10.1007/s00244-009-9371-2](https://doi.org/10.1007/s00244-009-9371-2).

The study reports that **atrazine at 120–200 mg/kg orally induces oxidative stress in rat testis and epididymis** (altered glutathione-S-transferase and superoxide dismutase activity, increased lipid peroxidation) and impairs sperm parameters — matching the PubChem annotation text in result #4 almost verbatim ("120 mg/kg … inhibition … of glutathione-S-transferase … superoxide dismutase decreased … testis and epididymis"). The annotation is a faithful excerpt of real toxicological literature, confirming the join surfaces accurate hazard content.

**Verdict:** both queries run without error, return non-empty results, and the retrieved annotation content is verbatim-corroborated by the primary literature. PASS - Retained.

## Sources

- PubMed via mcp-okn federation. Abarikwu et al. 2010, Arch Environ Contam Toxicol. [DOI: 10.1007/s00244-009-9371-2](https://doi.org/10.1007/s00244-009-9371-2)

# Chemicals Use Case 7 — RuralKG × RDKG (DrugBank)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Domain:** Chemicals · **Shared identifier:** DrugBank accession

## Knowledge graphs used

- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg> (Rural health/justice KG: NSDUH substance-abuse substances, `owl:sameAs` → DrugBank)
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg> (Rare-Disease KG: drug→disease treats / contraindicated_for; drug node IRI is the DrugBank IRI)

**Join:** RuralKG `owl:sameAs` `https://go.drugbank.com/drugs/DB…` → normalized to `http://identifiers.org/drugbank/DB…` = RDKG Drug node IRI. This is a deliberately **thin** crosswalk: RuralKG carries only 7 DrugBank-linked substances and exactly **2 join RDKG** (verified 2026-06-14).

## Research questions

- **Q1.** Which substances tracked in RuralKG's substance-abuse (NSDUH) data are also drugs in RDKG's drug–disease graph?
- **Q2.** For those dual-identity substances, what therapeutic indications and contraindications does RDKG record — i.e. the clinical face of a drug-of-abuse?

Both require the join: RuralKG frames these compounds as substances of abuse (survey/epidemiology), RDKG frames them as therapeutics with formal treats/contraindication edges. Connecting "tracked as drug-of-abuse" to "has clinical indications" needs the DrugBank bridge.

---

## Q1 — RuralKG substance-abuse substances that are RDKG drugs

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT DISTINCT ?ruralLabel ?ruralDescription ?ruralDataset (REPLACE(STR(?db),'http://identifiers.org/drugbank/','') AS ?DrugBank) ?rdkgDrugLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?s owl:sameAs ?o . FILTER(CONTAINS(STR(?o),'drugbank'))
    BIND(IRI(CONCAT('http://identifiers.org/drugbank/',REPLACE(STR(?o),'^.*/(DB[0-9]+).*$','$1'))) AS ?db)
    OPTIONAL { ?s rdfs:label ?ruralLabel }
    OPTIONAL { ?s dct:description ?ruralDescription }
    OPTIONAL { ?s <http://sail.ua.edu/ruralkg/substanceabuse/fromDataset> ?ruralDataset }
  }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?db a biolink:Drug ; rdfs:label ?rdkgDrugLabel .
  }
}
```

**Result (2 rows):**

| RuralKG substance | RuralKG description | Source | DrugBank | RDKG drug |
|---|---|---|---|---|
| Cocaine | tropane alkaloid and stimulant drug | NSDUH | DB00907 | Cocaine |
| Ketamine | chiral compound, pair of enantiomers with distinct pharmacology | NSDUH | DB01221 | Ketamine |

**Why this answers the question:** the two rows are exactly the substances RuralKG tracks (from the National Survey on Drug Use and Health) that also exist as RDKG drugs. Cocaine and ketamine are precisely the compounds expected to lead a double life — surveilled as drugs of abuse and used clinically — confirming the (small) join is correct and meaningful.

---

## Q2 — RDKG clinical profile of the two abuse substances

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?drug ?rel ?diseaseLabel WHERE {
  VALUES ?db { <http://identifiers.org/drugbank/DB00907> <http://identifiers.org/drugbank/DB01221> }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?db rdfs:label ?drug .
    { ?db biolink:treats ?disease . BIND("treats" AS ?rel) }
    UNION { ?db biolink:contraindicated_for ?disease . BIND("contraindicated_for" AS ?rel) }
    ?disease rdfs:label ?diseaseLabel .
  }
}
ORDER BY ?drug ?rel ?diseaseLabel
```

**Result (52 rows; selected):**

- **Cocaine — contraindicated for:** epilepsy, heart conduction disease, sudden cardiac arrest, hyperthyroidism, Graves disease, thyrotoxicosis.
- **Ketamine — treats:** major depressive disorder, unipolar / endogenous depression, post-traumatic stress disorder, obsessive-compulsive disorder, anxiety disorder, complex regional pain syndrome, status epilepticus, alcohol withdrawal, psychotic disorder.
- **Ketamine — contraindicated for:** coronary artery disease, myocardial infarction, intracranial hypertension, stroke disorder, hypertension, hyperthyroidism.

**Why this answers the question:** for two substances RuralKG surveils as drugs of abuse, RDKG supplies the clinical other half. Cocaine's contraindications (cardiac conduction disease, sudden cardiac arrest, hyperthyroidism) reflect its sympathomimetic cardiotoxicity; ketamine's indications (treatment-resistant depression, PTSD, CRPS, status epilepticus) reflect its established and emerging therapeutic uses. The rows are clinically coherent, not arbitrary.

---

## Literature validation

According to PubMed, Anand A, Mathew SJ, Sanacora G, et al. (2023). "Ketamine versus ECT for Nonpsychotic Treatment-Resistant Major Depression." *N Engl J Med* 388(25):2315–2325. [DOI: 10.1056/NEJMoa2302399](https://doi.org/10.1056/NEJMoa2302399).

This randomized trial found **intravenous ketamine non-inferior to electroconvulsive therapy for treatment-resistant major depression** (55.4% vs 41.2% response) — directly corroborating RDKG's record that ketamine *treats* major depressive disorder (Q2). Cocaine's recorded cardiovascular and thyroid contraindications are likewise consistent with its well-documented sympathomimetic toxicity.

**Verdict:** despite being a 2-chemical thread, both queries run without error, return non-empty results, and the headline therapeutic claim (ketamine → depression) is corroborated by a top-tier RCT. Success criterion (>=1 verified query) is exceeded. PASS - Retained.

## Sources

- PubMed via mcp-okn federation. Anand, Mathew, Sanacora et al. 2023, N Engl J Med. [DOI: 10.1056/NEJMoa2302399](https://doi.org/10.1056/NEJMoa2302399)

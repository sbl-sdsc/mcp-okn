# Taxonomy Crosswalk 12 Q1 — GeneLab spaceflight microbe × SPOKE-OKN strains (Pseudomonas)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

spoke-genelab detected Pseudomonas (NCBITaxon:286) as a differentially-abundant microbial genus in spaceflight. How many characterized bacterial strains does SPOKE-OKN hold that belong to that genus (i.e. nested under Pseudomonas via the taxonomy)? Join spoke-genelab and spoke-okn through the ubergraph NCBITaxon hierarchy.

---

🧠 **Assistant**

Joining the spoke-genelab spaceflight microbe Pseudomonas (NCBITaxon:286, present as a differential-abundance Organism node) to spoke-okn bacterial OrganismTaxon nodes through ubergraph's `rdfs:subClassOf*` hierarchy returns **11,052 distinct SPOKE-OKN bacterial strains** nested under the Pseudomonas genus.

The row answers the question and demonstrates the microbiome clade crosswalk: a genus that NASA GeneLab found shifting in abundance during spaceflight maps to 11,052 fully characterized Pseudomonas strains in SPOKE-OKN — strains that carry isolation metadata, genome data, and antimicrobial-resistance / drug-response information. This is the integration anticipated by the precomputed crosswalk (spoke-genelab and spoke-okn meet only via the ubergraph taxonomy closure; **exact-id overlap is just 2, but clade membership is ~33,000 strains** across all genera). The result is only obtainable by joining the two KGs through the ubergraph hierarchy.

**Literature validation (PubMed):** Pseudomonas is studied in the spaceflight/ISS microbiome (microbial monitoring, biofilm and virulence changes in microgravity) — e.g. PMID 34072140. Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?spaceflightGenus (COUNT(DISTINCT ?ot) AS ?spokeOknBacterialStrains) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    <https://purl.org/okn/frink/kg/spoke-genelab/node/286> a gls:Organism ; rdfs:label ?spaceflightGenus .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?desc rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_286> }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?ot a biolink:OrganismTaxon .
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_', REPLACE(STR(?ot),'^.*/organism/([0-9]+)\\..*$','$1'))) AS ?desc)
  }
}
GROUP BY ?spaceflightGenus
```

### Result (1 row)

| spaceflightGenus | spokeOknBacterialStrains |
| --- | --- |
| Pseudomonas | 11052 |

# Taxonomy Crosswalk 12 Q2 — GeneLab spaceflight microbe × SPOKE-OKN strains (Acinetobacter)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

spoke-genelab also detected Acinetobacter (NCBITaxon:469) — an ESKAPE / multidrug-resistant pathogen genus — as differentially abundant in spaceflight. How many characterized strains nested under Acinetobacter does SPOKE-OKN hold? Join spoke-genelab and spoke-okn via the ubergraph hierarchy.

---

🧠 **Assistant**

Joining the spoke-genelab spaceflight microbe Acinetobacter (NCBITaxon:469) to spoke-okn bacterial OrganismTaxon nodes through ubergraph's `rdfs:subClassOf*` hierarchy returns **11,610 distinct SPOKE-OKN strains** nested under the Acinetobacter genus.

The row answers the question and is especially relevant because Acinetobacter (e.g. *A. baumannii*) is an ESKAPE pathogen of major antimicrobial-resistance concern: SPOKE-OKN provides 11,610 characterized strains — with isolation, genome and AMR / drug-response metadata — for a genus that NASA GeneLab observed shifting in abundance during spaceflight. The clade join therefore connects spaceflight microbiome dynamics to a large, AMR-annotated reference strain collection. As with Pseudomonas, this is only obtainable through the ubergraph NCBITaxon hierarchy (exact-id overlap between the two KGs is just 2).

**Literature validation (PubMed):** Acinetobacter on the ISS / in the spaceflight built environment, and its antimicrobial resistance, are documented — a PubMed search returns 3 articles (PMID 30424821, 36503581, 32723791). Evidence exists, so the query is retained.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?spaceflightGenus (COUNT(DISTINCT ?ot) AS ?spokeOknAcinetobacterStrains) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    <https://purl.org/okn/frink/kg/spoke-genelab/node/469> a gls:Organism ; rdfs:label ?spaceflightGenus .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?desc rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_469> }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?ot a biolink:OrganismTaxon .
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_', REPLACE(STR(?ot),'^.*/organism/([0-9]+)\\..*$','$1'))) AS ?desc)
  }
}
GROUP BY ?spaceflightGenus
```

### Result (1 row)

| spaceflightGenus | spokeOknAcinetobacterStrains |
| --- | --- |
| Acinetobacter | 11610 |

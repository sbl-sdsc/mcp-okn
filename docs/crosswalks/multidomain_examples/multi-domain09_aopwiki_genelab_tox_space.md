# UC9 — Toxicology AOP Targets × Spaceflight Expression (AOP-Wiki + NASA GeneLab)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Predictive toxicology (Adverse Outcome Pathways) × Space biology (NASA GeneLab)
- **Knowledge graphs:** `biobricks-aopwiki` <https://purl.org/okn/frink/kg/biobricks-aopwiki> · `spoke-genelab` <https://purl.org/okn/frink/kg/spoke-genelab>
- **Shared join key:** Entrez gene id (AOP-Wiki `skos:exactMatch` → ncbigene; GeneLab via model→human ortholog `IS_ORTHOLOG_MGiG`)

## Question
Which genes that serve as **molecular targets in Adverse Outcome Pathways** (chemical-toxicity key events) are also **differentially expressed under spaceflight** in NASA GeneLab data? This asks whether the genes that mediate chemical adverse outcomes are the same genes stressed by the spaceflight environment.

## Result (top 20 AOP target genes by AOP key-event count, with spaceflight evidence)

| gene | AOP key events | spaceflight DE measurements |
| --- | --- | --- |
| ROS1 | 126 | 1,178 |
| PPIB | 113 | 2,492 |
| TBXT | 105 | 3,540 |
| GCNT2 | 103 | 5,256 |
| TH | 63 | 1,482 |
| IL6 | 61 | 574 |
| SLC25A5 | 56 | 1,308 |
| TNF | 44 | 736 |
| TP53 | 44 | 1,988 |
| OCA2 | 34 | 3,798 |
| AR | 32 | 1,894 |
| VEGFA | 30 | 1,546 |
| BCL2 | 28 | 884 |
| CA1 | 28 | 8,860 |

## Why it answers the question and is coherent
Every gene is a curated AOP molecular target **and** carries spaceflight differential-expression evidence. The overlap is mechanistically sensible: spaceflight imposes oxidative stress, genotoxic/DNA-damage stress and immune dysregulation, so AOP hubs for apoptosis/DNA damage (TP53, BCL2), inflammation (IL6, TNF), angiogenesis (VEGFA) and CO₂/acid–base and bone physiology (CA1 carbonic anhydrase, 8,860 spaceflight measurements) are exactly the genes that light up in orbit. AOP-Wiki supplies the toxicological pathway membership; GeneLab supplies the spaceflight expression — neither alone connects chemical adverse-outcome biology to the spaceflight stressor.

## Validation
According to PubMed, spaceflight drives broad, clock-dependent transcriptomic dysregulation and stress responses in mammalian tissue — Malhan et al., *NPJ Microgravity* 2023, [DOI](https://doi.org/10.1038/s41526-023-00273-4) — supporting the premise that canonical stress/apoptosis/inflammation genes (the AOP targets returned here) are differentially expressed in spaceflight. The AOP target genes themselves (TP53, AR, IL6, TNF, VEGFA) are well-established toxicological key-event molecules. Use case retained as valid.

## SPARQL
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?sym ?aop_key_events ?spaceflight_DE_measurements WHERE {
  { SELECT ?gene ?sym (COUNT(DISTINCT ?ke) AS ?aop_key_events) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?ke <http://edamontology.org/data_1025> ?hgnc .
        ?hgnc skos:exactMatch ?e . FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/')) }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?e),'^.*/ncbigene/',''))) AS ?gene)
      BIND(REPLACE(STR(?hgnc),'^.*/hgnc/','') AS ?sym)
    } GROUP BY ?gene ?sym }
  { SELECT ?hg (COUNT(DISTINCT ?stmt) AS ?spaceflight_DE_measurements) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mg . ?mg gl:IS_ORTHOLOG_MGiG ?hg . }
    } GROUP BY ?hg }
  FILTER(?gene = ?hg)
}
ORDER BY DESC(?aop_key_events) LIMIT 20
```

# UC10 — Rare-Disease Genes × Spaceflight Expression (RDKG + NASA GeneLab)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domains bridged:** Rare-disease genetics (RDKG) × Space biology (NASA GeneLab)
- **Knowledge graphs:** `rdkg` <https://purl.org/okn/frink/kg/rdkg> · `spoke-genelab` <https://purl.org/okn/frink/kg/spoke-genelab>
- **Shared join key:** Entrez gene id (RDKG `ncbigene` node IRIs; GeneLab via model→human ortholog)

## Question
Which **rare-disease genes** (RDKG, linked to MONDO rare diseases) show the strongest **spaceflight differential-expression** signal in NASA GeneLab — i.e., which Mendelian/rare-disease genes are also environmentally perturbed by spaceflight?

## Result (top 20 by spaceflight differential-expression measurements)

| gene | rare diseases (RDKG, MONDO) | spaceflight DE measurements |
| --- | --- | --- |
| UGT2B17 | 11 | 35,668 |
| UGT2B7 | 5 | 35,642 |
| UGT2B15 | 3 | 35,554 |
| NR1D1 | 4 | 35,276 |
| NR1D2 | 3 | 35,122 |
| RORA | 12 | 35,094 |
| PPARG | 82 | 35,052 |
| PPARD | 5 | 35,002 |
| RARB | 36 | 34,896 |
| PPARA | 26 | 34,836 |
| THRA | 9 | 34,828 |
| RARA | 21 | 33,964 |
| NR1I2 (PXR) | 19 | 33,774 |
| VDR | 30 | 33,730 |

## Why it answers the question and is coherent
The result couples each gene's **rare-disease burden** (RDKG MONDO count) with its **spaceflight responsiveness** (GeneLab). The leaders are biologically apt: the **UGT** drug-metabolism family (xenobiotic clearance, altered in microgravity), the nuclear receptors **PPARG** (linked to 82 rare metabolic/lipodystrophy conditions), **RARA** (acute promyelocytic leukemia), **NR1I2/PXR** (drug metabolism), and especially **VDR** — the vitamin-D receptor, tied to 30 rare diseases and central to the bone demineralization that is a hallmark of spaceflight. RDKG provides the rare-disease genetics; GeneLab provides the spaceflight expression; the Entrez key joins them.

## Validation
According to PubMed, simulated microgravity **down-regulates VDR mRNA** in human osteoblasts (to ~52% of control) and suppresses osteoblastic phenotypes, implicating reduced vitamin-D-receptor signaling in gravity-unloading-induced osteopenia — Nakamura et al., *J Med Dent Sci* 2003 (PMID 12968638). This directly supports the VDR × spaceflight link surfaced by the join; the use case is retained as valid.

## SPARQL
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?sym ?rare_disease_count ?spaceflight_DE_measurements WHERE {
  { SELECT ?gene ?sym (COUNT(DISTINCT ?mondo) AS ?rare_disease_count) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/rdkg> {
        ?gene a biolink:Gene ; rdfs:label ?sym ; biolink:related_to ?mondo .
        FILTER(STRSTARTS(STR(?gene),'http://identifiers.org/ncbigene/'))
        FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
    } GROUP BY ?gene ?sym }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?gene),'^.*/ncbigene/',''))) AS ?hg)
  { SELECT ?hg2 (COUNT(DISTINCT ?stmt) AS ?spaceflight_DE_measurements) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mg . ?mg gl:IS_ORTHOLOG_MGiG ?hg2 . }
    } GROUP BY ?hg2 }
  FILTER(?hg = ?hg2)
}
ORDER BY DESC(?spaceflight_DE_measurements) LIMIT 20
```

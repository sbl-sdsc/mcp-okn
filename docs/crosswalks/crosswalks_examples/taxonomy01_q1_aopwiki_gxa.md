# Taxonomy Crosswalk 1 Q1 — AOP-Wiki × Gene Expression Atlas (shared species)

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation

👤 **User**

Across the species shared by AOP-Wiki (toxicology adverse outcome pathways) and the Gene Expression Atlas (GXA), how many AOP key events apply to each organism and how many gene-expression studies exist for it? Give an example of each. This requires joining biobricks-aopwiki and gene-expression-atlas-okn on their shared NCBITaxon organism identifier (via the ubergraph hub for the species label).

---

🧠 **Assistant**

Joining AOP-Wiki (key-event taxonomic applicability, predicate `obo:NCBITaxon_131567` → `dc:identifier` NCBITaxon) to the Gene Expression Atlas (`biolink:in_taxon` NCBITaxon) on the shared NCBITaxon id returns **7 organisms present in BOTH knowledge graphs**, matching the precomputed exact-id overlap of 7. For each, the join reports the number of AOP key events whose taxonomic applicability includes that species and the number of GXA gene-expression studies performed in it:

- **Homo sapiens** — 94 AOP key events (e.g. *Motile Cilia Number/Length, Decreased*); 1,671 GXA studies (e.g. *Genomic Collaboration of Estrogen Receptor-α and ERK2…*).
- **Mus musculus** — 207 AOP key events (e.g. *Increase, Adenomas/carcinomas (follicular cell)*); 1,322 GXA studies.
- **Rattus norvegicus** — 182 AOP key events (e.g. *Endocytotic lysosomal uptake*); 187 GXA studies.
- **Danio rerio** (zebrafish) — 8 AOP key events (e.g. *Activation, AhR*); 27 GXA studies.
- **Caenorhabditis elegans** — 3 AOP key events (e.g. *Decrease of GABAergic interneurons*); 34 GXA studies.
- **Saccharomyces cerevisiae** — 3 AOP key events (e.g. *Binding of antagonist, PPAR alpha*); 54 GXA studies.
- **Arabidopsis thaliana** — 1 AOP key event (*Deposition of Energy*); 638 GXA studies.

The rows directly answer the question: each shared organism is a genuine integration point where toxicological adverse-outcome-pathway evidence (AOP-Wiki) can be combined with baseline/differential transcriptomic evidence (GXA). The query depends entirely on the NCBITaxon join — neither KG contains the other's payload.

**Literature validation:** the highlighted integration point — aryl hydrocarbon receptor (AhR) activation as an AOP key event in zebrafish (*Danio rerio*), one of the 7 shared species — is corroborated by the peer-reviewed literature (PubMed PMIDs recorded in `examples.md`).

## SPARQL query executed

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?taxName (COUNT(DISTINCT ?ke) AS ?aopKeyEvents) (SAMPLE(?keTitle) AS ?exampleKeyEvent) (COUNT(DISTINCT ?study) AS ?gxaStudies) (SAMPLE(?gxaTitle) AS ?exampleGxaStudy)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ke a aop:KeyEvent ; <http://purl.obolibrary.org/obo/NCBITaxon_131567> ?te ; dc:title ?keTitle .
    ?te dc:identifier ?tax .
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?study biolink:in_taxon ?tax ; wobd:project_title ?gxaTitle .
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?tax rdfs:label ?taxName . }
}
GROUP BY ?tax ?taxName ORDER BY ?taxName
```

### Results (7 rows)

| taxName | aopKeyEvents | exampleKeyEvent | gxaStudies | exampleGxaStudy |
| --- | --- | --- | --- | --- |
| Arabidopsis thaliana | 1 | Deposition of Energy | 638 | Acclimation of photosynthesis… in Arabidopsis thaliana |
| Caenorhabditis elegans | 3 | Decrease of GABAergic interneurons | 34 | RNA-seq of C. elegans control vs SKN-1b mutant |
| Danio rerio | 8 | Activation, AhR | 27 | 3' mRNA-seq of sfpq-/- zebrafish embryos at 24 hpf |
| Homo sapiens | 94 | Motile Cilia Number/Length, Decreased | 1671 | Genomic Collaboration of Estrogen Receptor-α and ERK2… |
| Mus musculus | 207 | Increase, Adenomas/carcinomas (follicular cell) | 1322 | Expression data from draining lymph node and muscle of mice… |
| Rattus norvegicus | 182 | Endocytotic lysosomal uptake | 187 | Dietary zinc status reversibly alters… gene expression in rats |
| Saccharomyces cerevisiae | 3 | Binding of antagonist, PPAR alpha | 54 | Yeast genomic expression patterns in response to deoxynivalenol |

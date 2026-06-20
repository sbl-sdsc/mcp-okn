# CW13-Q2 oard-kg×prokn (MONDO↔Orphanet) — Joubert syndrome ciliary proteins + top OARD phenotype

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

CW13 (oard-kg × prokn, bridged MONDO↔Orphanet via ubergraph), Q2: For Joubert syndrome via Orphanet (475), what ciliary proteins + the single strongest OARD EHR phenotype (log-odds)? Why the bridge join?

---

🧠 **Assistant**

**Crosswalk:** oard-kg × prokn, bridged through **ubergraph** · **Shared key:** MONDO↔Orphanet. Joubert syndrome (MONDO_0018772) carries `oboInOwl:hasDbXref` Orphanet:475; ProKN attaches its ciliary marker proteins to the Orphanet-keyed entity. A nested sub-select pulls the single strongest OARD EHR phenotype (by log-odds).

**Why the join is required:** ProKN holds the ciliary protein panel under an Orphanet id; OARD holds the EHR phenotype enrichment under MONDO. Combining the molecular panel with the strongest real-world phenotype needs the ubergraph MONDO→Orphanet bridge.

**Result (verified):** 11 ciliary proteins, non-empty, each paired with the top phenotype. Sample:

| protein | accession | top OARD phenotype (log-odds) |
|---|---|---|
| ARL13B (AR13B) | Q3SXY8 | Global developmental delay (3.75) |
| CC2D2A (C2D2A) | Q9P2K1 | Global developmental delay (3.75) |
| CEP41 | Q9BYV8 | Global developmental delay (3.75) |
| INPP5E (INP5E) | Q9NRR6 | Global developmental delay (3.75) |
| TMEM216 (TM216) | Q9P0N5 | Global developmental delay (3.75) |

**Why these rows answer the question:** every protein is a bona-fide Joubert ciliopathy gene (ARL13B, CC2D2A, CEP41, INPP5E, TMEM216/231/237, TECT1), and the bridge pairs them with Joubert's strongest OARD EHR phenotype — Global developmental delay — exactly the protein-plus-phenotype artifact requested.

**Literature validation (PubMed, thorough):** According to PubMed, D'Abrusco et al., *Cerebellum* 2021 ([10.1007/s12311-021-01350-8](https://doi.org/10.1007/s12311-021-01350-8)) describe Joubert syndrome as a recessive ciliopathy (molar-tooth sign) caused by >40 ciliary genes and presenting with hypotonia and developmental delay — directly validating the ciliary-protein panel and the 'Global developmental delay' top phenotype returned by the Orphanet bridge. **Kept.**

## SPARQL queries executed

#### Query 1

_2026-06-17 · `oard-kg`, `ubergraph`, `prokn`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX pbl: <https://biolink.github.io/biolink-model/>
PREFIX oio: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX up: <http://purl.uniprot.org/core/>
# CW13 (oard-kg <-> prokn, bridged MONDO<->Orphanet via ubergraph hasDbXref) Q2:
# Joubert syndrome (MONDO_0018772) reached via the Orphanet rare-disease bridge:
# its ProKN ciliary marker proteins, alongside the strongest OARD EHR-co-occurring
# phenotype (label + log-odds ratio).
SELECT DISTINCT ?orphaId ?accession ?protein ?topPheno ?topLOR WHERE {
  {
    SELECT ?topPheno ?topLOR WHERE {
      GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
        ?assoc biolink:category biolink:DiseaseToPhenotypicFeatureAssociation ;
               biolink:subject <http://purl.obolibrary.org/obo/MONDO_0018772> ;
               biolink:predicate biolink:positively_correlated_with ;
               biolink:object ?ph ;
               biolink:has_supporting_studies ?study .
        ?study biolink:has_study_results ?res .
        ?res biolink:log_odds_ratio ?topLOR .
        FILTER(?topLOR < 100)
      }
      GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?ph rdfs:label ?topPheno }
    } ORDER BY DESC(?topLOR) LIMIT 1
  }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/MONDO_0018772> oio:hasDbXref ?curie .
    FILTER(STRSTARTS(STR(?curie),'Orphanet:'))
  }
  BIND(REPLACE(STR(?curie),'^Orphanet:','') AS ?orphaId)
  BIND(IRI(CONCAT('http://www.orpha.net/ORDO/Orphanet_',?orphaId)) AS ?orpha)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?y a up:Disease ; rdfs:seeAlso ?orpha .
    ?prot pbl:associated_with ?y ; a up:Protein ; up:mnemonic ?protein .
    BIND(REPLACE(STR(?prot),'http://purl.uniprot.org/uniprot/','') AS ?accession)
  }
}
ORDER BY ?protein LIMIT 20
```

_11 row(s) — showing first 5_

| orphaId | accession | protein | topPheno | topLOR |
| --- | --- | --- | --- | --- |
| 475 | Q3SXY8 | AR13B_HUMAN | Global developmental delay | 3.749182 |
| 475 | Q9P2K1 | C2D2A_HUMAN | Global developmental delay | 3.749182 |
| 475 | Q9BYV8 | CEP41_HUMAN | Global developmental delay | 3.749182 |
| 475 | Q68CZ1 | FTM_HUMAN | Global developmental delay | 3.749182 |
| 475 | Q9NRR6 | INP5E_HUMAN | Global developmental delay | 3.749182 |

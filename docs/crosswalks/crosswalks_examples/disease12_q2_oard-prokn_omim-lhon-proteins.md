# CW12-Q2 oard-kg×prokn (MONDO↔OMIM) — Leber hereditary optic neuropathy mtDNA proteins via OMIM bridge

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>

## Conversation

👤 **User**

CW12 (oard-kg × prokn, bridged MONDO↔OMIM via ubergraph), Q2: For Leber hereditary optic neuropathy via MONDO→OMIM (535000), what ProKN marker proteins? Why the bridge join?

---

🧠 **Assistant**

**Crosswalk:** oard-kg × prokn, bridged through **ubergraph** · **Shared key:** MONDO↔OMIM. LHON (MONDO_0010788) carries `oboInOwl:hasDbXref` OMIM:535000; ProKN's marker proteins attach to the OMIM-keyed entity. A `FILTER EXISTS` confirms LHON also appears in OARD, anchoring the disease in EHR data.

**Why the join is required:** ProKN keys the LHON protein panel on OMIM, while OARD anchors the disease on MONDO. The ubergraph MONDO→OMIM bridge is the only path from the OARD disease to ProKN's protein set.

**Result (verified):** 10 proteins, non-empty, all mitochondrial-DNA-encoded OXPHOS subunits (OMIM 535000):

| protein | accession |
|---|---|
| ATP6 | P00846 |
| COX1 | P00395 |
| COX3 | P00414 |
| CYB | P00156 |
| ND1 (NU1M) | P03886 |
| ND4 (NU4M) | P03905 |
| ND6 (NU6M) | P03923 |

**Why these rows answer the question:** every protein is an mtDNA-encoded respiratory-chain subunit, and ND1/ND4/ND6 (NU1M/NU4M/NU6M) are precisely the genes harboring the three primary LHON mutations — exactly the marker proteins requested, reached only via the OMIM bridge.

**Literature validation (PubMed, thorough):** According to PubMed, McDonald et al., *Can J Neurol Sci* 2022 ([10.1017/cjn.2022.279](https://doi.org/10.1017/cjn.2022.279)) report that LHON is caused by point mutations in the mitochondrially-encoded MT-ND1, MT-ND4 and MT-ND6 subunits (the three classic mutations m.3460G>A, m.11778G>A, m.14484T>C) — directly validating ND1/ND4/ND6 (and the broader OXPHOS panel) returned by the OMIM bridge. **Kept.**

## SPARQL queries executed

#### Query 1

_2026-06-17 · `ubergraph`, `prokn`, `oard-kg`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX pbl: <https://biolink.github.io/biolink-model/>
PREFIX oio: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX up: <http://purl.uniprot.org/core/>
# CW12 (oard-kg <-> prokn, bridged MONDO<->OMIM via ubergraph hasDbXref) Q2:
# Leber hereditary optic neuropathy (MONDO_0010788) reached via the OMIM bridge:
# its ProKN marker proteins with the bridging OMIM id, gated on OARD EHR evidence.
SELECT DISTINCT ?omimId ?accession ?protein WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/MONDO_0010788> oio:hasDbXref ?curie .
    FILTER(STRSTARTS(STR(?curie),'OMIM:'))
  }
  BIND(REPLACE(STR(?curie),'^OMIM:','') AS ?omimId)
  BIND(IRI(CONCAT('https://www.omim.org/entry/',?omimId)) AS ?omim)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?y a up:Disease ; rdfs:seeAlso ?omim .
    ?prot pbl:associated_with ?y ; a up:Protein ; up:mnemonic ?protein .
    BIND(REPLACE(STR(?prot),'http://purl.uniprot.org/uniprot/','') AS ?accession)
  }
  FILTER EXISTS {
    GRAPH <https://purl.org/okn/frink/kg/oard-kg> {
      { ?a biolink:subject <http://purl.obolibrary.org/obo/MONDO_0010788> } UNION { ?b biolink:object <http://purl.obolibrary.org/obo/MONDO_0010788> }
    }
  }
}
ORDER BY ?protein LIMIT 20
```

_10 row(s) — showing first 5_

| omimId | accession | protein |
| --- | --- | --- |
| 535000 | P00846 | ATP6_HUMAN |
| 535000 | P00395 | COX1_HUMAN |
| 535000 | P00414 | COX3_HUMAN |
| 535000 | P00156 | CYB_HUMAN |
| 535000 | P03886 | NU1M_HUMAN |

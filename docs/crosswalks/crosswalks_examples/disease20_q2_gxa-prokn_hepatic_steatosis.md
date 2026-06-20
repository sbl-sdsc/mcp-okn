# disease20_q2_gxa-prokn_hepatic_steatosis

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

Hepatic steatosis is a phenotype GXA profiles and the one with the most ProKN entities (q1). **Crosswalk on HP:** which ProKN disease entities carry the Hepatic steatosis phenotype, and how are they identified? Join gene-expression-atlas-okn and prokn on HP = Hepatic steatosis.

---
🧠 **Assistant**

**Why the join is required.** GXA flags hepatic steatosis as studied; ProKN holds the cross-referenced disease entities. Naming them requires resolving GXA's HP term and pulling the ProKN entities that `seeAlso` it.

**Join mechanics.** Resolve `?hp` whose ubergraph label is "Hepatic steatosis", then `?entity rdfs:seeAlso ?hp` in ProKN, with the entity's `rdf:type`.

| ProKN entity | type |
| --- | --- |
| `…/mesh/?term=D005234` | up:Disease (UniProt core Disease) |
| `…/omim.org/entry/MTHU008981` | EFO_0000651 (disease/phenotype) |

The rows answer the question: GXA's hepatic-steatosis phenotype maps to two ProKN disease entities — a MeSH-indexed UniProt disease node (D005234, "Fatty Liver") and an OMIM-anchored EFO disease entity — each a handle into ProKN's protein/marker evidence. The result depends on the HP join.

**Validation (shared standard + literature).** Join on the HP identifier; ProKN entities are identified by MeSH/OMIM and typed as UniProt/EFO disease nodes. According to PubMed, hepatic steatosis / NASH is an active protein-biomarker target — proteomic panels for steatohepatitis and fibrosis (Vali et al., LITMUS, *Lancet Gastroenterol Hepatol* 2023, [DOI](https://doi.org/10.1016/S2468-1253(23)00017-1)) and osteopontin as a NASH biomarker (Remmerie et al., *Immunity* 2020, [DOI](https://doi.org/10.1016/j.immuni.2020.08.004)) — supporting the value of linking this phenotype to ProKN's protein evidence. **Validated** (shared HP identifier; PubMed-corroborated).

## SPARQL queries executed
#### Query 1
_`gene-expression-atlas-okn`, `prokn`, `ubergraph` · 2 rows_
```sparql
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?proknEntity ?type WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?hp a bl:Disease . FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?hp rdfs:label "Hepatic steatosis" }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?proknEntity <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?hp . OPTIONAL { ?proknEntity a ?type } }
} LIMIT 10
```
| proknEntity | type |
| --- | --- |
| https://www.ncbi.nlm.nih.gov/mesh/?term=D005234 | http://purl.uniprot.org/core/Disease |
| https://www.omim.org/entry/MTHU008981 | http://www.ebi.ac.uk/efo/EFO_0000651 |

**Validation:** shared HP ontology identifier; MeSH/OMIM disease IDs. PubMed — Vali 2023 [DOI](https://doi.org/10.1016/S2468-1253(23)00017-1); Remmerie 2020 [DOI](https://doi.org/10.1016/j.immuni.2020.08.004).

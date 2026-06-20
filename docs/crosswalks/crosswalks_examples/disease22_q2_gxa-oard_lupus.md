# disease22_q2_gxa-oard_lupus

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

Systemic lupus erythematosus (SLE) is one of the GXA-profiled diseases reaching OARD (q1). **Crosswalk on EFO↔MONDO:** how rich is SLE's EHR phenotype profile in OARD — how many distinct phenotypes is it correlated with? Join on MONDO = systemic lupus erythematosus.

---
🧠 **Assistant**

**Why the join is required.** GXA establishes SLE has expression studies; OARD supplies its real-world phenotype breadth. Quantifying that requires resolving SLE's MONDO term and counting OARD phenotype associations.

**Join mechanics.** Resolve `?mondo` whose ubergraph label is "systemic lupus erythematosus", then count distinct OARD `biolink:object` HP phenotypes on its associations.

SLE is correlated with **766 distinct HP phenotypes** in OARD's EHR data — a very broad multi-system signature, consistent with lupus being a systemic autoimmune disease. Pairing this clinical phenotype breadth with GXA's SLE expression studies supports molecular-to-phenotype analyses.

**Validation (standard + literature).** Join on the MONDO identifier; count is a direct OARD association aggregation. According to PubMed, SLE is "a complex autoimmune disease with multisystem involvement" presenting "a broad spectrum of clinical manifestations" (Ameer et al., *Cureus* 2022, [DOI](https://doi.org/10.7759/cureus.30330)) — directly consistent with its 766-phenotype OARD breadth. **Validated** (shared MONDO identifier; PubMed-corroborated).

## SPARQL queries executed
#### Query 1
_`oard-kg`, `ubergraph` · 1 row_
```sparql
PREFIX bl: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT (COUNT(DISTINCT ?hp) AS ?oardPhenotypes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo rdfs:label "systemic lupus erythematosus" . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { ?a bl:subject ?mondo ; bl:object ?hp . FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_')) }
}
```
| oardPhenotypes |
| --- |
| 766 |

**Validation:** shared MONDO identifier; OARD association aggregation; clinically coherent. PubMed — Ameer 2022 [DOI](https://doi.org/10.7759/cureus.30330).

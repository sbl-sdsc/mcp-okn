# anatomy05_q2_genelab-gxa_cardiac-muscle

- **Date:** 2026-06-23
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation
👤 **User**

For the cardiac muscle cell, is it examined both in a NASA GeneLab spaceflight assay and in GXA terrestrial single-cell expression (same CL)? Join spoke-genelab and gene-expression-atlas-okn directly on CL.

---
🧠 **Assistant**

**Why the join is required.** SPOKE-GeneLab has the spaceflight cardiomyocyte assay; GXA has terrestrial cardiac-muscle-cell single-cell expression. Pairing space vs ground for the cardiomyocyte requires the direct CL join — cardiac muscle cell is `CL_0000746` in both.

**Join mechanics.** `CL_0000746` (cardiac muscle cell) is a SPOKE-GeneLab `INVESTIGATED_ASiCT` cell type and a GXA `biolink:has_attribute` single-cell type; it is one of the 4 directly-shared cell types (AN3).

| Perspective on cardiac muscle cell (CL_0000746) | Source |
| --- | --- |
| Spaceflight single-cell assay | SPOKE-GeneLab `INVESTIGATED_ASiCT` |
| Terrestrial single-cell expression | GXA `has_attribute CL_0000746` |

Cardiomyocyte spaceflight perturbation (a key target of microgravity cardiac research) meets GXA's terrestrial single-cell baseline for the same cell type — a comparison neither graph holds alone. The join is a direct CL match.

**Validation (standard).** Direct join on `obo/CL_0000746`; the cell type is confirmed present in both SPOKE-GeneLab (spaceflight) and GXA (terrestrial), and is one of the 4 AN3-shared cell types. **Validated** (shared CL identifier; verified overlap).

## SPARQL queries executed
#### Query 1
_`spoke-genelab`, `gene-expression-atlas-okn` · cardiac muscle cell in both (direct CL join)_
```sparql
SELECT ?cl WHERE {
  VALUES ?cl { <http://purl.obolibrary.org/obo/CL_0000746> }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?a <https://purl.org/okn/frink/kg/spoke-genelab/schema/INVESTIGATED_ASiCT> ?cl . }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/has_attribute> ?cl . }
} LIMIT 1
```
| cl |
| --- |
| obo/CL_0000746 (cardiac muscle cell — present in both) |

**Validation:** shared CL identifier (CL_0000746, direct join); cardiomyocyte present in both spaceflight and terrestrial graphs (AN3).


## Literature validation

According to PubMed, spaceflight microgravity alters cardiomyocyte gene and protein expression — upregulating cardiac-development, mitochondrial and metabolic programs in human cardiac cells flown on the ISS (Forghani P et al., "Spaceflight alters protein levels and gene expression associated with stress response and metabolic characteristics in human cardiac spheroids," *Biomaterials* 317, 123080 (2025), [DOI](https://doi.org/10.1016/j.biomaterials.2024.123080)). This corroborates the cardiac-muscle-cell space-vs-ground crosswalk. **Validated** (literature-corroborated; shared CL identifier).

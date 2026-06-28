# Spaceflight zebrafish lineage joined to the PFAS panel SAWGraph measured in white perch

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

NASA's spaceflight fish model is the zebrafish (*Danio rerio*); SAWGraph monitors a fish of the same ray-finned lineage (white perch, *Morone americana*). Which **specific PFAS chemicals** has SAWGraph measured in that lineage-sharing fish — the real environmental contaminant panel a spaceflight zebrafish toxicology study could anchor to?

---
🧠 **Assistant**

spoke-genelab supplies the spaceflight organism (zebrafish) but no contaminant data; SAWGraph supplies the monitored organism + PFAS panel but no spaceflight context; only the ubergraph Actinopterygii clade links them. Each row therefore contains both a GeneLab organism and a SAWGraph organism + PFAS chemical.

**Spaceflight contrast:** n/a — organism-level (clade) join; no differential values read.

**Sample result** (8 of 12) — each row shows GeneLab + sawgraph data:

| GeneLab spaceflight organism | Shared clade (ubergraph) | SAWGraph organism | PFAS chemical (sawgraph) |
|---|---|---|---|
| *Danio rerio* | Actinopterygii | *Morone americana* | 2-(N-Ethylperfluorooctanesulfonamido)acetic acid (EtFOSAA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | 2-(N-Methylperfluorooctanesulfonamido)acetic acid (MeFOSAA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | 3:3 Fluorotelomer carboxylic acid |
| *Danio rerio* | Actinopterygii | *Morone americana* | 6:2 Fluorotelomer sulfonic acid |
| *Danio rerio* | Actinopterygii | *Morone americana* | 8:2 Fluorotelomer sulfonic acid |
| *Danio rerio* | Actinopterygii | *Morone americana* | N-Ethylperfluorooctane sulfonamide (EtFOSA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | N-Methylperfluorooctanesulfonamide (MeFOSA) |
| *Danio rerio* | Actinopterygii | *Morone americana* | Perfluoro-2-ethoxyethanesulfonic acid |

**Why it answers the question:** every row pairs the GeneLab spaceflight organism (*Danio rerio*) with the SAWGraph-monitored organism (*Morone americana*) and a real named PFAS chemical measured in it, linked only through the shared Actinopterygii clade — the concrete contaminant panel a spaceflight zebrafish study could anchor to.

## SPARQL query executed
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# GeneLab spaceflight zebrafish + SAWGraph fish + PFAS, joined via the shared Actinopterygii clade.
SELECT DISTINCT ?geneLabOrganism ?sharedClade ?sawOrganism ?pfasChemical WHERE {
  # GeneLab spaceflight zebrafish (Danio rerio, NCBITaxon_7955)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?g gls:taxonomy <http://purl.obolibrary.org/obo/NCBITaxon_7955> ; gls:organism ?geneLabOrganism .
  }
  BIND("Actinopterygii (ray-finned fishes)" AS ?sharedClade)
  # zebrafish + SAWGraph fish both descend from Actinopterygii (7898)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_7955> rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_7898> .
    ?sawTax rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_7898> ; rdfs:label ?sawOrganism .
  }
  # the PFAS chemicals SAWGraph actually measured in that fish
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?mat <http://purl.obolibrary.org/obo/RO_0002162> ?sawTax .
    ?samp coso:sampleOfMaterialType ?mat . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst .
    ?subst rdfs:label ?pfasChemical . FILTER(STRSTARTS(STR(?subst),'http://w3id.org/DSSTox/'))
  }
} ORDER BY ?pfasChemical LIMIT 12
```

## Literature validation

Rericha et al., 2023, *Toxicological Sciences* — review establishing the zebrafish as a primary in-vivo model for PFAS toxicokinetics and toxicity, validating use of the spaceflight zebrafish model to interpret PFAS exposure in lineage-related wild fish. [PMID:37220906](https://pubmed.ncbi.nlm.nih.gov/37220906/) · [DOI](https://doi.org/10.1093/toxsci/kfad051)

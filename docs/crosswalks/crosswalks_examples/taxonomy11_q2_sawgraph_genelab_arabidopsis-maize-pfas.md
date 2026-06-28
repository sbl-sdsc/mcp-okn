# Spaceflight Arabidopsis lineage joined to the PFAS panel SAWGraph measured in maize

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

NASA's spaceflight plant model is *Arabidopsis thaliana*; SAWGraph monitors a flowering-plant crop of the same green-plant lineage — maize (*Zea mays*). Which **specific PFAS chemicals** has SAWGraph measured in that crop — the real contaminant panel relevant to space-agriculture and food-crop safety?

---
🧠 **Assistant**

spoke-genelab supplies the spaceflight plant model (*Arabidopsis*) but no contaminant data; SAWGraph supplies the monitored crop + PFAS panel but no spaceflight context; the two share no exact taxon (one eudicot model, one monocot crop), so only clade expansion through the ubergraph Viridiplantae node links them. Each row therefore contains both a GeneLab organism and a SAWGraph crop + PFAS chemical.

**Spaceflight contrast:** n/a — organism-level (clade) join; no differential values read.

**Sample result** (8 of 12) — each row shows GeneLab + sawgraph data:

| GeneLab spaceflight organism | Shared clade (ubergraph) | SAWGraph crop | PFAS chemical (sawgraph) |
|---|---|---|---|
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 11-Chloroperfluoro-3-oxaundecanesulfonic acid (11Cl-PF3OUdS) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 2-(N-Ethylperfluorooctanesulfonamido)acetic acid (EtFOSAA) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 2-(N-Methylperfluorooctanesulfonamido)acetic acid (MeFOSAA) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 4,8-Dioxa-3H-perfluorononanoic acid (ADONA) |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 4:2 Fluorotelomer sulfonic acid |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 6:2 Fluorotelomer sulfonic acid |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | 8:2 Fluorotelomer sulfonic acid |
| *Arabidopsis thaliana* | Viridiplantae | *Zea mays* subsp. *mays* | N-Ethylperfluorooctane sulfonamide (EtFOSA) |

**Why it answers the question:** every row pairs the GeneLab spaceflight plant model (*Arabidopsis thaliana*) with the SAWGraph-monitored crop (*Zea mays*) and a real named PFAS chemical measured in it — including replacement PFAS (ADONA, 11Cl-PF3OUdS) and fluorotelomer sulfonic acids — linked only through the shared Viridiplantae clade, the concrete crop-contamination panel relevant to space-agriculture food safety.

## SPARQL query executed
```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX coso: <http://w3id.org/coso/v1/contaminoso#>
PREFIX gls: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# GeneLab spaceflight Arabidopsis + SAWGraph crop (maize) + PFAS, joined via the shared Viridiplantae clade.
SELECT DISTINCT ?geneLabOrganism ?sharedClade ?sawCrop ?pfasChemical WHERE {
  # GeneLab spaceflight Arabidopsis (Arabidopsis thaliana, NCBITaxon_3702)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?g gls:taxonomy <http://purl.obolibrary.org/obo/NCBITaxon_3702> ; gls:organism ?geneLabOrganism .
  }
  BIND("Viridiplantae (green plants)" AS ?sharedClade)
  # Arabidopsis + SAWGraph maize both descend from Viridiplantae (33090)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    <http://purl.obolibrary.org/obo/NCBITaxon_3702> rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_33090> .
    ?sawTax rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_33090> ; rdfs:label ?sawCrop .
  }
  # the PFAS chemicals SAWGraph actually measured in that crop (maize)
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
    ?mat <http://purl.obolibrary.org/obo/RO_0002162> ?sawTax .
    ?samp coso:sampleOfMaterialType ?mat . ?obs coso:analyzedSample ?samp ; coso:ofSubstance ?subst .
    ?subst rdfs:label ?pfasChemical . FILTER(STRSTARTS(STR(?subst),'http://w3id.org/DSSTox/'))
  }
} ORDER BY ?pfasChemical LIMIT 12
```

## Literature validation

Just et al., 2022, *J Agric Food Chem* — soil-plant pot experiments with maize (*Zea mays* L.) showed fluorotelomer precursors degrade to perfluoroalkyl carboxylic acids that are translocated into maize shoots, demonstrating real PFAS uptake into the crop. [PMID:35840126](https://pubmed.ncbi.nlm.nih.gov/35840126/) · [DOI](https://doi.org/10.1021/acs.jafc.1c06838)

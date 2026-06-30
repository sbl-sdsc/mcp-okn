# Spaceflight-enriched Gammaproteobacteria bridged by clade to NIAID Gammaproteobacterial pathogens

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `nde` — <https://purl.org/okn/frink/kg/nde>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>

## Conversation
👤 **User**

The class Gammaproteobacteria becomes strongly more abundant in NASA's spaceflight crop microbiome (VEG-01). Although no spaceflight-enriched microbe matches NDE at the species level, do any NIAID-tracked infectious-disease pathogens fall *within* that spaceflight-enriched clade — i.e. can the spaceflight microbial-ecology signal be connected, by clade, to concrete terrestrial pathogens and their diseases?

---
🧠 **Assistant**

spoke-genelab measures which microbial clade shifts in spaceflight (with the abundance value) but has no pathogen-surveillance context; NDE catalogs which pathogen species anchor infectious-disease datasets (and their diseases) but has no spaceflight data; the ubergraph NCBITaxon hierarchy supplies the clade link. Each row pairs a GeneLab spaceflight abundance value with an NDE pathogen + disease under the same clade.

**Spaceflight contrast:** Space Flight vs Ground Control under the `mcp-okn` server's `spoke-genelab` Rule 1 (direction via `factor_space_1/2`) + Rule 2 (comparability — arms differ only in the condition after stripping balanced shared factors). These VEG-01 differential-abundance assays carry no `material_id` and bundle a plant-compartment factor (root / leaf), so the first edition fell back to direction-only and inadvertently included confounded *cross-compartment* contrasts (root-flight vs leaf-ground). Rule 2 resolves that cleanly without a fallback: enforcing comparability on the factor arrays alone keeps the balanced **root-vs-root** contrast and drops the cross-compartment ones. Gammaproteobacteria is **up in spaceflight** (lnfc +8.20, log2fc +11.84) in that balanced contrast.

**Sample result** (8 of 11) — each row shows GeneLab + nde data:

| Spaceflight-enriched clade (GeneLab) | lnfc / log2fc (SF vs GC, up) | NDE pathogen under that clade | NIAID disease (nde) |
|---|---|---|---|
| Gammaproteobacteria | +8.20 / +11.84 | *Escherichia coli* | escherichia coli infection |
| Gammaproteobacteria | +8.20 / +11.84 | *Escherichia coli* O157:H7 | escherichia coli infection |
| Gammaproteobacteria | +8.20 / +11.84 | *Salmonella* | salmonellosis |
| Gammaproteobacteria | +8.20 / +11.84 | *Salmonella* Typhi | typhoid fever |
| Gammaproteobacteria | +8.20 / +11.84 | *Shigella* | shigellosis |
| Gammaproteobacteria | +8.20 / +11.84 | *Vibrio cholerae* | cholera |
| Gammaproteobacteria | +8.20 / +11.84 | *Haemophilus influenzae* | haemophilus infectious disease |
| Gammaproteobacteria | +8.20 / +11.84 | *Legionella* | legionellosis |

**Why it answers the question:** every row carries a real GeneLab spaceflight differential-abundance value for the Gammaproteobacteria clade AND a real NIAID pathogen species (verified `subClassOf*` descendant of that clade) with its named disease — turning the species-level coverage gap into a meaningful clade-level bridge from spaceflight microbial ecology to terrestrial Gammaproteobacterial pathogens.

## SPARQL query executed
```sparql
PREFIX schema: <http://schema.org/>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# GeneLab spaceflight-enriched Gammaproteobacteria (differential abundance, Rule 2 balanced contrast)
# bridged via ubergraph clade to NDE pathogen species under Gammaproteobacteria (1236) and their NIAID disease.
SELECT ?sfClade (MAX(?sfLnfc) AS ?maxLnfc) (MAX(?sfLog2fc) AS ?maxLog2fc) ?ndePathogen ?ndeDisease WHERE {
  # GeneLab: Gammaproteobacteria differential abundance, Space Flight vs Ground Control
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_ABUNDANCE_ASmO ;
          rdf:object ?gorg ; sg:lnfc ?sfLnfc ; sg:log2fc ?sfLog2fc .
    ?gorg rdfs:label ?sfClade .
    ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" .
    FILTER(STRENDS(STR(?gorg),'/node/1236'))
    # Rule 2 comparability: arms differ ONLY in the condition — keeps the balanced root-vs-root (and leaf-vs-leaf)
    # contrasts and drops the confounded cross-compartment ones (root-flight vs leaf-ground). These abundance
    # assays carry no material_id, so comparability is enforced on the factor arrays alone.
    FILTER NOT EXISTS { ?assay sg:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay sg:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay sg:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay sg:factors_1 ?y } }
  }
  # NDE pathogen species (uniprot taxonomy IRI) + its ubergraph obo IRI for clade membership
  VALUES (?sp ?spTax ?ndePathogen) {
    (<https://www.uniprot.org/taxonomy/562>   <http://purl.obolibrary.org/obo/NCBITaxon_562>   "Escherichia coli")
    (<https://www.uniprot.org/taxonomy/83334> <http://purl.obolibrary.org/obo/NCBITaxon_83334> "Escherichia coli O157:H7")
    (<https://www.uniprot.org/taxonomy/590>   <http://purl.obolibrary.org/obo/NCBITaxon_590>   "Salmonella")
    (<https://www.uniprot.org/taxonomy/90370> <http://purl.obolibrary.org/obo/NCBITaxon_90370> "Salmonella Typhi")
    (<https://www.uniprot.org/taxonomy/620>   <http://purl.obolibrary.org/obo/NCBITaxon_620>   "Shigella")
    (<https://www.uniprot.org/taxonomy/666>   <http://purl.obolibrary.org/obo/NCBITaxon_666>   "Vibrio cholerae")
    (<https://www.uniprot.org/taxonomy/727>   <http://purl.obolibrary.org/obo/NCBITaxon_727>   "Haemophilus influenzae")
    (<https://www.uniprot.org/taxonomy/445>   <http://purl.obolibrary.org/obo/NCBITaxon_445>   "Legionella")
  }
  # ubergraph: confirm the NDE pathogen descends from the spaceflight-enriched clade
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?spTax rdfs:subClassOf* <http://purl.obolibrary.org/obo/NCBITaxon_1236> .
  }
  # NDE: the NIAID disease for that pathogen
  GRAPH <https://purl.org/okn/frink/kg/nde> {
    ?ds schema:species ?sp ; schema:healthCondition ?hc .
    ?hc schema:name ?ndeDisease .
  }
} GROUP BY ?sfClade ?ndePathogen ?ndeDisease ORDER BY ?ndePathogen ?ndeDisease
```

## Literature validation

Singh et al., 2018, *BMC Microbiology* — multidrug-resistant *Enterobacter bugandensis* (an Enterobacteriaceae, i.e. Gammaproteobacteria) isolated from the ISS carried virulence and antibiotic-resistance genes and a high predicted pathogenic probability, confirming ISS-enriched Gammaproteobacteria overlap human pathogens. [PMID:30466389](https://pubmed.ncbi.nlm.nih.gov/30466389/) · [DOI](https://doi.org/10.1186/s12866-018-1325-2)

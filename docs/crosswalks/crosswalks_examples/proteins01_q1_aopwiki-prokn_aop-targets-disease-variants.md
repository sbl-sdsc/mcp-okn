# Protein Use Case Q1 — AOP-Wiki x ProKN — AOP target proteins with disease variants

- **Date:** 2026-06-16
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Which proteins that serve as molecular targets of Key Events in AOP-Wiki Adverse Outcome Pathways also carry disease-causing natural sequence variants recorded in ProKN, and which AOP key events and diseases are involved? (Crosswalk: biobricks-aopwiki x prokn; shared identifier: UniProt accession.)

---

🧠 **Assistant**

I joined biobricks-aopwiki and prokn on the shared UniProt accession. In AOP-Wiki, a Key Event points (edamontology:data_1025) to a gene/protein node that carries skos:exactMatch links to identifiers.org/uniprot IRIs; I normalized each to the purl.uniprot.org/uniprot form used as the node IRI in ProKN, then required that the same protein in ProKN carry a natural sequence variant (biolink:has_sequence_variant) that is causally related (obo:RO_0002410) to a UniProt Disease with a label. This returns proteins that are simultaneously (a) molecular targets within toxicological Adverse Outcome Pathways and (b) carriers of disease-causing germline/somatic variants.

The query returned 100 rows. Representative results:

- P05067 (APP) — AOP key events 'Systemic acute phase response' and 'Transcription of genes encoding acute phase proteins, Increased' — disease: Alzheimer's disease (also anxiety disorder).
- P49768 (PSEN1 / AD3) — AOP key event 'Succinate dehydrogenase, inhibited' — disease: Alzheimer's disease.
- O00206 (TLR4) — AOP key events including 'Toll Like Receptor (TLR) Dysregulation', 'Tissue resident cell activation' — disease: Alzheimer's disease.
- P23560 (BDNF) — AOP key events 'Reduced levels of BDNF', 'Neurodegeneration', 'Glutamate dyshomeostasis' — disease: Alzheimer's disease.
- P49841 (GSK3B) — AOP key event 'GSK3beta inactivation' — disease: Alzheimer's disease.
- P10909 (CLU/APOJ) — AOP key event 'Occurrence, Kidney toxicity' — disease: Alzheimer's disease.

Why these answer the question: each row pairs an AOP Key Event (the toxicological/mechanistic context contributed by AOP-Wiki) with a disease that ProKN ties to a curated sequence variant of the SAME protein. The join is essential — neither KG alone links an AOP key event to a curated protein-variant-disease assertion. APP, PSEN1, CLU, BDNF and GSK3B are all bona fide Alzheimer's-associated proteins, so the integration surfaces toxicological pathways converging on established neurodegeneration genes.

Literature validation (according to PubMed): APP/PSEN1/PSEN2 mutations cause autosomal-dominant early-onset Alzheimer disease — Lanoiselee et al., PLoS Medicine 2017, [DOI](https://doi.org/10.1371/journal.pmed.1002270) (PubMed returned 819 matching articles). TLR4/NLRP3 microglial signaling drives Alzheimer's neuroinflammation — Li et al., J Alzheimers Dis 2024, [DOI](https://doi.org/10.3233/JAD-230273) (241 matching articles). The protein-disease associations surfaced by the join are therefore well supported in the literature. Query retained as valid.

## SPARQL queries executed

#### Query 1

_`biobricks-aopwiki`, `prokn`_

```sparql
PREFIX aop:  <http://aopkb.org/aop_ontology#>
PREFIX dc:   <http://purl.org/dc/elements/1.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX edam: <http://edamontology.org/>
PREFIX biolink: <https://biolink.github.io/biolink-model/>
PREFIX obo:  <http://purl.obolibrary.org/obo/>
PREFIX ncit: <http://purl.obolibrary.org/obo/NCIT_>

SELECT DISTINCT ?uniprot ?geneName ?keTitle ?disease WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?ke a aop:KeyEvent ; edam:data_1025 ?gene .
    OPTIONAL { ?ke dc:title ?keTitle }
    ?gene skos:exactMatch ?u .
    FILTER(STRSTARTS(STR(?u),'https://identifiers.org/uniprot/'))
  }
  BIND(REPLACE(STR(?u),'^.*/uniprot/','') AS ?uniprot)
  BIND(IRI(CONCAT('http://purl.uniprot.org/uniprot/',?uniprot)) AS ?p2)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    OPTIONAL { ?p2 ncit:C164806 ?geneName }
    ?p2 biolink:has_sequence_variant ?var .
    ?var obo:RO_0002410 ?d .
    ?d rdfs:label ?disease .
  }
}
ORDER BY ?disease ?uniprot ?keTitle
LIMIT 100
```

_100 row(s) — sample_

| uniprot | geneName | keTitle | disease |
| --- | --- | --- | --- |
| P05067 | APP | Systemic acute phase response | Alzheimer's disease |
| P49768 | PSEN1 | Succinate dehydrogenase, inhibited | Alzheimer's disease |
| O00206 | TLR4 | Toll Like Receptor (TLR) Dysregulation | Alzheimer's disease |
| P23560 | BDNF | Reduced levels of BDNF | Alzheimer's disease |
| P49841 | GSK3B | GSK3beta inactivation | Alzheimer's disease |

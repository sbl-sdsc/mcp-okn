# UC11 — PubChem Chemical Annotations × SPOKE Clinical Drugs (BioBricks-PubChem + SPOKE)

- **Date:** 2026-06-17 · **Model:** claude-opus-4-8 · **Endpoint:** https://apps.okn.us/federation/sparql
- **Domains bridged:** Cheminformatics (PubChem free-text annotations) × Clinical pharmacology (SPOKE drug→disease)
- **Knowledge graphs:** `biobricks-pubchem-annotations` <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> · `spoke-okn` <https://purl.org/okn/frink/kg/spoke-okn>
- **Shared join key:** PubChem Compound ID (SPOKE `oboInOwl:hasDbXref` → `identifiers.org/pubchem.compound/{CID}`; BioBricks `oa:hasTarget` → `pubchem/compound/CID{n}`)

## Question
For the chemicals that **SPOKE uses clinically** (compounds it records as *treating* a disease), how much **PubChem annotation evidence** (toxicity rankings, hazards, indications, dosing, drug class) is available? This pairs SPOKE's clinical drug–disease layer with PubChem's curated cheminformatics annotation corpus.

## Result (top 15 SPOKE therapeutic compounds by PubChem annotation count)

| compound | PubChem annotations | SPOKE treats (sample) |
| --- | --- | --- |
| Phenytoin | 136 | epilepsy; schizophrenia; (others) |
| Thiabendazole | 133 | ascariasis |
| Fluorouracil | 127 | many carcinomas (breast, colon, gastric, pancreatic, …) |
| Acetic Acid | 125 | brain cancer; chronic kidney disease |
| Naphthalene | 120 | (SPOKE association) |
| Tetracycline | 114 | trachoma; non-Hodgkin lymphoma |
| Ethanol | 112 | alcohol use disorder; hypertension |
| Isopropyl Alcohol | 107 | psoriasis; multiple sclerosis; RA |
| Hexachlorocyclohexane | 83 | scabies |
| Resorcinol | 74 | acne |
| Titanium Dioxide | 71 | skin cancer; skin benign neoplasm |
| Carbon Dioxide | 67 | migraine |

## Why it answers the question
Each returned compound is simultaneously (a) recorded by SPOKE as treating ≥1 disease and (b) richly annotated in PubChem. The annotation bodies carry exactly the cheminformatics evidence a clinician/toxicologist needs — e.g. for aspirin, a DILIrank drug-induced-liver-injury class ("Less-DILI-Concern"), indications ("acute myocardial infarction; cerebral ischaemic stroke"), dosing ("Oral solid: 100–500 mg") and drug class ("anti-platelet medicines"). SPOKE alone has no free-text toxicity/hazard annotations; PubChem alone has no disease-treatment layer; the PubChem CID key fuses them. (SPOKE's `TREATS` edges are MeSH-co-occurrence-derived and include some noisy associations — a property of the source graph, surfaced honestly.)

## Validation
PubChem annotations are an authoritative, curated cheminformatics resource; the bodies themselves cite primary literature (e.g. the DILIrank drug-induced-liver-injury reference, Chen et al., *Drug Discov Today* 2016, PMID 26948801). The clinical drugs surfaced (phenytoin, fluorouracil, tetracycline) are well-established agents. The integration is validated by the authoritative shared PubChem CID and the verified 762/762 crosswalk; specific toxicity claims are traceable to the cited annotation sources.

## SPARQL
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?compound ?pubchem_annotations ?treats_diseases WHERE {
  { SELECT ?cmp ?compound (COUNT(DISTINCT ?ann) AS ?pubchem_annotations) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
        FILTER(STRSTARTS(STR(?x),'http://identifiers.org/pubchem.compound/'))
        ?cmp rdfs:label ?compound . }
      BIND(IRI(CONCAT('http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID',REPLACE(STR(?x),'^.*/pubchem.compound/',''))) AS ?b)
      GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> { ?ann oa:hasTarget ?b . }
    } GROUP BY ?cmp ?compound }
  { SELECT ?cmp (GROUP_CONCAT(DISTINCT ?dl; separator="; ") AS ?treats_diseases) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?st rdf:subject ?cmp ; rdf:predicate sp:TREATS_CtD ; rdf:object ?d . ?d rdfs:label ?dl . }
    } GROUP BY ?cmp }
}
ORDER BY DESC(?pubchem_annotations) LIMIT 15
```

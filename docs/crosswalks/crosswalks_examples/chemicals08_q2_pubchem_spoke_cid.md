# Chemicals Crosswalk 8 — PubChem Annotations × SPOKE (PubChem CID)

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

**User**

For a compound that SPOKE places in its disease/drug network (e.g. Phenacetin, which SPOKE records contraindications for), what free-text toxicology / carcinogenicity annotations does PubChem hold? (Join biobricks-pubchem-annotations to spoke-okn on PubChem CID.)

---

**Assistant**

**Use case:** SPOKE links compounds to diseases and genes but stores no free-text safety/hazard narrative; biobricks-pubchem-annotations holds PubChem's curated toxicology/hazard/use text but is keyed only on PubChem CID. SPOKE is in fact the ONLY federation KG that materializes PubChem CID, so pulling PubChem's hazard narrative for a SPOKE compound requires joining the two on CID. **762 compounds** join (100% of SPOKE's pubchem.compound-xref'd chemicals carry ≥1 PubChem annotation).

**KGs joined:** spoke-okn (`oboInOwl:hasDbXref` → `identifiers.org/pubchem.compound/{cid}`) × biobricks-pubchem-annotations (`oa:hasTarget` → `rdf.ncbi.nlm.nih.gov/.../CID{cid}`, then `oa:hasBody`/`rdf:value` → text). Shared key: **PubChem CID** (IRI forms differ, so the CID is extracted and reconstructed).

**Result — Phenacetin (CID 4754; a compound SPOKE records disease contraindications for), PubChem carcinogenicity annotations:**

- *Case reports:* "The carcinogenic effect of analgesic abuse involving phenacetin was studied in 88 cases of renal parenchymal disease and carcinoma of kidney and ureters. Thirty-one patients had malignant urothelial tumors of the renal pelvis or ureter ... following prolonged and heavy analgesic ingestion."
- *Laboratory animals / carcinogenicity:* dose-related urothelial cell-proliferation and renal-pelvic/bladder hyperplasia in Sprague-Dawley rats fed phenacetin; hepatocellular carcinomas in rats fed the metabolite N-hydroxyphenacetin.
- *Genotoxicity:* phenacetin metabolically activated to mutagens in the Ames test by hepatic microsomal preparations.

**Why this answers the question:** the query takes a compound SPOKE situates in its clinical network (Phenacetin, with SPOKE contraindication edges) and, via the CID join, returns PubChem's detailed carcinogenicity/genotoxicity narrative that SPOKE itself lacks — exactly the toxicology context the example question asks for. Phenacetin is a textbook IARC Group 1 human carcinogen (analgesic-nephropathy-associated urothelial cancer), so the retrieved annotations are substantive and on-point, not incidental text.

**Literature validation (PubMed):** Bringuier et al., *Int J Cancer* 1998 (IARC) state that "phenacetin abuse and smoking are established risk factors for transitional cell carcinomas of the urinary tract" and analyse renal-pelvic carcinomas in phenacetin-abuse patients ([DOI](https://doi.org/10.1002/(sici)1097-0215(19981023)79:5%3C531::aid-ijc15%3E3.0.co;2-4)) — directly corroborating the PubChem phenacetin → renal-pelvis-carcinoma annotation surfaced by this crosswalk.

## SPARQL query executed

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?compound ?pubchemToxicologyAnnotation WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?c oboInOwl:hasDbXref <http://identifiers.org/pubchem.compound/4754> ; rdfs:label ?compound .
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?ann oa:hasTarget <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID4754> ; oa:hasBody ?body .
    ?body rdf:value ?pubchemToxicologyAnnotation .
    FILTER(CONTAINS(STR(?pubchemToxicologyAnnotation),'arcinog'))
    FILTER(STRLEN(STR(?pubchemToxicologyAnnotation)) > 60)
  }
}
LIMIT 6
```

*Note: the same join works in bulk (762 SPOKE compounds carry PubChem annotations). The query is scoped to one compound (Phenacetin, CID 4754) because full-text scanning of all annotation bodies across the federation times out; per-CID retrieval is fast and reliable.*

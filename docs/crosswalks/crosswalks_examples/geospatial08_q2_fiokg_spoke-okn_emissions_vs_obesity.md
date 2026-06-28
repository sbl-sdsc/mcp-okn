# Named EPA PFAS air-major facilities in Cook County beside the county's adult-obesity indicator

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation
👤 **User**

Joining `fiokg` and `spoke-okn` on **county_FIPS**: for Cook County, IL, name the individual EPA PFAS-relevant facilities that hold an **"Air major"** environmental-interest registration, and place each beside the county's adult-obesity SDoH indicator from `spoke-okn`.

---
🧠 **Assistant**

The join is required because `fiokg` supplies the *named* industrial facilities (EPA Facility Registry Service records: facility `rdfs:label`, `hasEnvironmentalInterest` program type, and county `sfWithin`) while `spoke-okn` supplies the behavioral/metabolic health indicator (`variable = "adult obesity"`, a `PREVALENCEIN_SpL` statement) plus the county name. Neither graph alone can put a specific PFAS-emitting facility next to a county metabolic-health figure; the FIPS join (`17031`) does.

Join mechanics: I restrict `fiokg` to `EPA-PFAS-Facility` nodes that `sfWithin` `administrativeRegion.USA.17031` and carry `EnvironmentalInterestType.Airmajor`, read each facility's `rdfs:label`, then bind the `spoke-okn` `…/location/17031` node and read the "adult obesity" value and county name.

| EPA PFAS facility (fiokg, "Air major") | county (spoke-okn) | adult obesity % (spoke-okn) |
| --- | --- | --- |
| 3M CO | Cook County | 29.9(1.0) |
| ARCELORMITTAL RIVERDALE, INC. - RIVERDALE FACILITY | Cook County | 29.9(1.0) |
| ACME FINISHING CO LLC | Cook County | 29.9(1.0) |
| AARGUS PLASTICS INC | Cook County | 29.9(1.0) |
| 31ST STREET ENERGY LLC | Cook County | 29.9(1.0) |
| ALCO GRAVURE INC | Cook County | 29.9(1.0) |

The rows answer the question: each row pairs a real, *named* Clean-Air-Act major-source PFAS facility (`fiokg`) — including 3M (a historic PFAS manufacturer), the ArcelorMittal Riverdale steel facility, and metal-finishing/plastics/coating plants — with the named county and its real adult-obesity prevalence of 29.9% (`spoke-okn`). Naming the facilities ties a metabolic-health metric to specific industrial PFAS sources rather than to an anonymous count.

## SPARQL query executed
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?facName ?cname ?adult_obesity WHERE {
  BIND("17031" AS ?fips)
  BIND(<http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.17031> AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/fiokg> {
    ?fac a <http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility> ;
         <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?reg ;
         rdfs:label ?facName ;
         <http://w3id.org/fio/v1/epa-frs#hasEnvironmentalInterest>
           <http://w3id.org/fio/v1/epa-frs-data#d.EnvironmentalInterestType.Airmajor> .
  }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc rdfs:label ?cname .
    ?stmt rdf:predicate schema:PREVALENCEIN_SpL ; rdf:object ?loc ;
          schema:variable "adult obesity" ; schema:value ?adult_obesity .
  }
} ORDER BY ?facName LIMIT 12
```

## Literature validation

According to PubMed, several PFAS compounds act as metabolic "obesogens" — endocrine-disrupting chemicals that alter lipid homeostasis, promote adipogenesis and disrupt metabolic regulation. Jaskulak et al. (2025, *Ecotoxicol Environ Saf*) systematically reviewed a decade of human epidemiological studies on endocrine-disrupting chemicals (including PFAS) as environmental obesogens and document associations between such exposures and obesity/metabolic outcomes, validating that placing named PFAS-emitting facilities beside a county adult-obesity indicator reflects a biologically plausible exposure-outcome pairing. [PMID:40412253](https://pubmed.ncbi.nlm.nih.gov/40412253/) · [DOI](https://doi.org/10.1016/j.ecoenv.2025.118401)

# Named SUDOKN metal surface-finishing manufacturers by ZIP, with SPOKE county air-quality & care context

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>

## Conversation
👤 **User**

SUDOKN catalogs U.S. small/medium manufacturers (company name via `rdfs:label`, process capabilities, address node with `schema:postalCode`), but no state context or local environmental/health background for the ZIP. SPOKE-OKN holds U.S. ZIP administrative nodes that roll up through their city to a county carrying County-Health-Rankings indicators. **Crosswalk on ZIP5:** within Ohio, list **named surface-finishing manufacturers** (coating / plating / galvanizing — capabilities that handle metals, solvents and particulates) with their specific capability, each row contextualized by the SPOKE county's **air-pollution (PM2.5)** level and **primary-care-physician** ratio. Surface-finishing density is a determinant of community-level occupational and environmental exposure.

---
🧠 **Assistant**

**Why the join is required.** SUDOKN names the company and its capability and ZIP but cannot place the ZIP in a state or describe its environmental/health setting. SPOKE-OKN supplies the ZIP→state mapping (`state="OH"`) and, by walking the ZIP node up through its city to its county, the County-Health-Rankings **air pollution – particulate matter** (PM2.5, µg/m³) and **primary care physicians** ratio. Only the join pairs a *named* surface-finishing manufacturer with the SPOKE air-quality and healthcare-access context of its county.

**Join mechanics.** Shared key = bare 5-digit ZIP literal. In sudokn, `company → organizationLocatedIn → address` with the address's `schema:postalCode` (https form) giving the ZIP, the company name via `rdfs:label`, and the process-capability name parsed from the `hasProcessCapability` IRI (filtered to Coating / Plating / Galvanizing / Anodizing). spoke-okn matches `/location/OH-{ZIP}` nodes (`state="OH"`), walks `PARTOF_LpL` to the county FIPS, and reads two county `PREVALENCEIN_SpL` values (`air pollution - particulate matter`, `primary care physicians`). **Both KGs populate every row:** the named company + capability are sudokn entities; PM2.5 and the physician ratio are real spoke county values.

| ZIP | named manufacturer (SUDOKN) | capability | SPOKE county PM2.5 (µg/m³) | SPOKE primary-care ratio |
| --- | --- | --- | --- | --- |
| 43001 | LFS Coatings | Powder Coating | 9.8 | 2508:1 |
| 43001 | Technibus, Inc. | Silver Plating | 9.8 | 2508:1 |
| 43001 | Short Run Pro | Zinc Plating | 9.8 | 2508:1 |
| 43001 | Pinnacle Metal Products | Mechanical Coating | 9.8 | 2508:1 |
| 43001 | Construction Services, Inc. | Powder Coating | 9.8 | 2508:1 |
| 43001 | Induspray | Coating | 9.8 | 2508:1 |

**Why it answers the question.** Each row is a concrete, named Ohio surface-finishing manufacturer with its specific finishing capability (powder coating, silver/zinc plating, mechanical coating), placed against the SPOKE county's measured PM2.5 (9.8 µg/m³) and primary-care scarcity (≈2,508 residents per physician). This pairs *who does metal-finishing where* (SUDOKN) with *the surrounding county's air-quality and healthcare-access burden* (SPOKE) — the community-exposure determinant the question targets.

## SPARQL query executed
```sparql
SELECT DISTINCT ?zip ?company ?capability ?airPM ?primCare WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sudokn> {
    ?comp <http://asu.edu/semantics/SUDOKN/organizationLocatedIn> ?addr ;
          <http://www.w3.org/2000/01/rdf-schema#label> ?company ;
          <http://asu.edu/semantics/SUDOKN/hasProcessCapability> ?cap .
    ?addr ?pz ?zip .
    FILTER(STRENDS(STR(?pz),'schema.org/postalCode'))
    FILTER(CONTAINS(STR(?cap),'Coating') || CONTAINS(STR(?cap),'Plating') || CONTAINS(STR(?cap),'Galvanizing') || CONTAINS(STR(?cap),'Anodizing'))
    BIND(REPLACE(REPLACE(STR(?cap),'^.*com-',''),'-process-capability-instance$','') AS ?capRaw)
    BIND(REPLACE(?capRaw,'%20',' ') AS ?capability)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "OH" ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/PARTOF_LpL> ?city .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
    ?city <https://purl.org/okn/frink/kg/spoke-okn/schema/PARTOF_LpL> ?county .
    FILTER(REGEX(STR(?county),'/location/[0-9]{5}$'))
    ?s1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> <https://purl.org/okn/frink/kg/spoke-okn/schema/PREVALENCEIN_SpL> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?county ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/variable> "air pollution - particulate matter" ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/value> ?airPM .
    ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> <https://purl.org/okn/frink/kg/spoke-okn/schema/PREVALENCEIN_SpL> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?county ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/variable> "primary care physicians" ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/value> ?primCare .
  }
} ORDER BY ?zip LIMIT 12
```

## Literature validation

According to PubMed, Adachi (1987, *Sangyo Igaku*) demonstrated that long-term inhalation of chromic-acid mist generated in **electroplating** caused nasal-septum perforation, tracheal proliferation, emphysema and lung neoplasia in exposed animals, concluding that hexavalent-chromium surface-finishing aerosols are a respiratory-carcinogen risk for electroplating/metal-finishing workers — corroborating treating named surface-finishing (coating/plating) manufacturers as concrete community/occupational-exposure sources. [PMID:3613247](https://pubmed.ncbi.nlm.nih.gov/3613247/) · [DOI](https://doi.org/10.1539/joh1959.29.17)

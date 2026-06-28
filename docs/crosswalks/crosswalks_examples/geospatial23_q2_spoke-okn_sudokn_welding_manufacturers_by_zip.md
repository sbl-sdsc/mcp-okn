# Named SUDOKN welding-capable manufacturers by ZIP, with SPOKE county PM2.5 (environmental-justice framing)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>

## Conversation
👤 **User**

SUDOKN records each manufacturer's specific **process capabilities**, including welding — an operation tied to documented occupational exposures (welding fume, metal particulates, hexavalent chromium, manganese). **Crosswalk on ZIP5:** within Ohio, list **named welding-capable manufacturers** with their welding capability, each row contextualized by the SPOKE county's **air-pollution (PM2.5)** level. Pinpointing which named companies operate where ambient particulate burden is already measured supports an environmental-justice reading of cumulative exposure.

---
🧠 **Assistant**

**Why the join is required.** SUDOKN names the welding-capable company, its capability and ZIP; it has no state context and no ambient air-quality measure. SPOKE-OKN supplies the ZIP→state mapping (`state="OH"`) and, via the ZIP→city→county walk, the County-Health-Rankings **air pollution – particulate matter** (PM2.5, µg/m³) for the county. Only the join places a *named* welding manufacturer next to the SPOKE-measured ambient particulate burden of its county — a cumulative-exposure (occupational fume + ambient PM) framing.

**Join mechanics.** Shared key = bare 5-digit ZIP literal. In sudokn, `company → organizationLocatedIn → address` with the address `schema:postalCode` (https form) giving the ZIP, the company name via `rdfs:label`, and `hasProcessCapability` filtered to capability IRIs containing "Welding". spoke-okn matches `/location/OH-{ZIP}` nodes (`state="OH"`), walks `PARTOF_LpL` to the county FIPS, and reads the county `PREVALENCEIN_SpL` PM2.5 value. **Both KGs populate every row:** the named welding manufacturer is the sudokn entity; the PM2.5 figure is a real spoke county value.

| ZIP | named welding manufacturer (SUDOKN) | SPOKE county PM2.5 (µg/m³) |
| --- | --- | --- |
| 43001 | Technibus, Inc. | 9.8 |
| 43001 | Pinnacle Metal Products | 9.8 |
| 43001 | Norman Noble | 9.8 |
| 43004 | Action Group, Inc. | 10.0 |
| 43016 | Alpha ProTech Engineered Products, Inc. | 10.0 |
| 43017 | Holaday-Parks | 10.0 |

**Why it answers the question.** Each row is a concrete, named Ohio welding-capable manufacturer set against the SPOKE-measured ambient PM2.5 of its county (9.8–10.0 µg/m³). Because welders bear an occupational fume burden *on top of* this ambient particulate load, the join surfaces specific companies and locations where cumulative respiratory exposure — the environmental-justice concern — is plausibly highest, naming exactly which facilities they are rather than a bare count.

## SPARQL query executed
```sparql
SELECT DISTINCT ?zip ?company ?airPM WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sudokn> {
    ?comp <http://asu.edu/semantics/SUDOKN/organizationLocatedIn> ?addr ;
          <http://www.w3.org/2000/01/rdf-schema#label> ?company ;
          <http://asu.edu/semantics/SUDOKN/hasProcessCapability> ?cap .
    ?addr ?pz ?zip .
    FILTER(STRENDS(STR(?pz),'schema.org/postalCode'))
    FILTER(CONTAINS(STR(?cap),'Welding'))
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
  }
} ORDER BY ?zip LIMIT 12
```

## Literature validation

According to PubMed, Fikayo et al. (2023, *Ethiop J Health Sci*) measured chromium, nickel and manganese in arc-welding fumes above recommended limits and found significantly reduced lung function (lower FEV1 and FEV1/FVC) in welders versus controls — confirming welding capability as a concrete occupational respiratory-exposure determinant that, layered on the ambient PM2.5 this join attaches, supports the cumulative-exposure environmental-justice reading. [PMID:37484188](https://pubmed.ncbi.nlm.nih.gov/37484188/) · [DOI](https://doi.org/10.4314/ejhs.v33i2.23)

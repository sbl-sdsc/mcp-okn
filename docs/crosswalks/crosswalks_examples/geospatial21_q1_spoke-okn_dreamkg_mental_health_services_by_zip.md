# Named DREAM-KG mental-health / substance-use services by ZIP, with SPOKE county mental-health context

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>

## Conversation
👤 **User**

DreamKG catalogs Philadelphia homelessness / social-service offerings, each tagged with a `schema:postalCode` (bare 5-digit ZIP) and a human-readable service identifier (organization + program), but no information on whether that ZIP is a real PA standard residential ZIP or any local health context. SPOKE-OKN holds U.S. ZIP administrative nodes (`/location/{STATE}-{ZIP}`, `state`, `zipcode_type`) that roll up through their city to a county carrying County-Health-Rankings indicators (`PREVALENCEIN_SpL`, `schema:variable`/`schema:value`). **Crosswalk on ZIP5:** list **named mental-health / substance-use services** from DreamKG in validated PA standard residential ZIPs, each row contextualized by the SPOKE county's mental-health-provider ratio and frequent-mental-distress rate.

---
🧠 **Assistant**

**Why the join is required.** DreamKG names the service and its ZIP but cannot confirm the ZIP is a valid PA standard residential code nor say anything about the surrounding county's mental-health capacity. SPOKE-OKN supplies the ZIP validation (`state = "PA"`, `zipcode_type = "STANDARD"`) and — by following the ZIP node up through its city to its county — the County-Health-Rankings **mental health providers** ratio and **frequent mental distress** rate. Only the join puts a *named* DreamKG service next to the SPOKE health context of the place it sits in.

**Join mechanics.** Shared key = the bare 5-digit ZIP literal. spoke-okn selects `/location/PA-{ZIP}` nodes (`state="PA"`, `zipcode_type="STANDARD"`) and walks `PARTOF_LpL` (ZIP→city→county FIPS); for that county it reads two `PREVALENCEIN_SpL` statements (`variable = "mental health providers"` and `"frequent mental distress"`). In dreamkg the service matches `schema:postalCode` with `schema:category` filtered to `/service_type/Mental` and its name taken from `schema:identifier`. **Both KGs populate every row:** the named service is the dreamkg entity; the provider ratio and distress rate are real spoke county values.

| ZIP | named service (DREAM-KG) | SPOKE county mental-health providers | SPOKE frequent mental distress % |
| --- | --- | --- | --- |
| 19102 | Mental Health Counseling (The Attic Youth Center) | 313:1 | 16.9 |
| 19102 | Substance Use Disorder Treatment (ETHOS Treatment, LLC) | 313:1 | 16.9 |
| 19102 | Mother Baby Connections (Drexel University) | 313:1 | 16.9 |
| 19102 | Behavioral Health Services (Dr. Robin Lowey & Associates LLC) | 313:1 | 16.9 |
| 19102 | Outpatient Behavioral Health (Tower Health – Tower-Drexel Academic Medical Group) | 313:1 | 16.9 |
| 19047 | HIV/AIDS Program HAP – Medical Case Management (Family Service Association of Bucks County) | 352:1 | 14.6 |

**Why it answers the question.** Each row is a concrete, named DreamKG mental-health / substance-use service in a SPOKE-validated PA standard residential ZIP, set against the SPOKE county's mental-health-provider scarcity (e.g. 313 residents per provider in Philadelphia County) and frequent-mental-distress burden (16.9%). This pairs *where help exists* (DreamKG) with *how strained the surrounding county is* (SPOKE) — exactly the service-to-need mapping the question asks for.

## SPARQL query executed
```sparql
SELECT DISTINCT ?zip ?service ?mhProviders ?mentalDistress WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/state> "PA" ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/zipcode_type> "STANDARD" ;
         <https://purl.org/okn/frink/kg/spoke-okn/schema/PARTOF_LpL> ?city .
    FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+'))
    ?city <https://purl.org/okn/frink/kg/spoke-okn/schema/PARTOF_LpL> ?county .
    FILTER(REGEX(STR(?county),'/location/[0-9]{5}$'))
    ?s1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> <https://purl.org/okn/frink/kg/spoke-okn/schema/PREVALENCEIN_SpL> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?county ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/variable> "mental health providers" ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/value> ?mhProviders .
    ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> <https://purl.org/okn/frink/kg/spoke-okn/schema/PREVALENCEIN_SpL> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?county ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/variable> "frequent mental distress" ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/value> ?mentalDistress .
  }
  GRAPH <https://purl.org/okn/frink/kg/dreamkg> {
    ?svc <http://schema.org/postalCode> ?zip ;
         <http://schema.org/category> ?cat ;
         <http://schema.org/identifier> ?id .
    FILTER(CONTAINS(STR(?cat),'/service_type/Mental'))
    BIND(REPLACE(STR(?id),'_[0-9]+$','') AS ?service)
  }
} ORDER BY ?zip LIMIT 12
```

## Literature validation

According to PubMed, Poulin et al. (2010, *Psychiatr Serv*) studied a population-based sample of 2,703 chronically homeless persons in Philadelphia and found that 81% of the highest-cost service users carried a serious mental-illness diagnosis, with psychiatric care driving most service costs — establishing the acute, geographically concentrated demand for the mental-health and substance-use services this join maps to validated Philadelphia ZIPs. [PMID:21041347](https://pubmed.ncbi.nlm.nih.gov/21041347/) · [DOI](https://doi.org/10.1176/ps.2010.61.11.1093)

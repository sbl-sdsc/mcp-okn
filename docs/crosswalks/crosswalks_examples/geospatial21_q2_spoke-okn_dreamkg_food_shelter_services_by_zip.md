# Named DREAM-KG food / shelter services by ZIP, with SPOKE county food-insecurity & housing context

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>

## Conversation
👤 **User**

Beyond mental health, DreamKG tags services as **Food** or **Shelter**, each with a human-readable identifier (organization + program) and a `schema:postalCode`. **Crosswalk on ZIP5:** list **named food and shelter services** from DreamKG in SPOKE-validated PA standard residential ZIPs, each row contextualized by the SPOKE county's **food insecurity** rate and **severe housing problems** rate. Food insecurity and unstable housing are tightly coupled health risks for people experiencing homelessness — which named services sit where the surrounding county need is highest?

---
🧠 **Assistant**

**Why the join is required.** DreamKG holds the named food/shelter services and their ZIPs but cannot confirm a ZIP is a valid PA standard residential code nor describe the local food/housing hardship. SPOKE-OKN supplies the ZIP validation (`state="PA"`, `zipcode_type="STANDARD"`) and, via the ZIP→city→county walk, the County-Health-Rankings **food insecurity** and **severe housing problems** rates for the county. Only the join places a *named* service next to the SPOKE county hardship context.

**Join mechanics.** Shared key = bare 5-digit ZIP literal. spoke-okn selects `/location/PA-{ZIP}` STANDARD nodes, walks `PARTOF_LpL` (ZIP→city→county FIPS), and for that county reads two `PREVALENCEIN_SpL` statements (`variable = "food insecurity"` and `"severe housing problems"`). In dreamkg the service matches `schema:postalCode`, with `schema:category` filtered to `/service_type/Food` or `/service_type/Shelter` and its name from `schema:identifier`. **Both KGs populate every row:** the named service is the dreamkg entity; the food-insecurity and housing rates are real spoke county values.

| ZIP | named service (DREAM-KG) | type | SPOKE county food insecurity % | SPOKE severe housing problems % |
| --- | --- | --- | --- | --- |
| 19102 | Code Blue (Project HOME) | Shelter | 15.8 | 22.7 |
| 19103 | St. Mark's Food Cupboard (Saint Mark's Church) | Food | 15.8 | 22.7 |
| 19104 | Our Closet in Your Neighborhood (Jewish Family and Children's Service of Greater Philadelphia) | Food | 15.8 | 22.7 |
| 19023 | Residential Maternity Shelter (Mother's Home) | Shelter | 9.1 | 15.5 |
| 19079 | Food Cupboard (Neighbor to Neighbor Community Development Corporation Inc) | Food | 9.1 | 15.5 |
| 19013 | Community Support Services (Better Living Center) | Food | 9.1 | 15.5 |

**Why it answers the question.** Each row is a concrete, named DreamKG food or shelter service in a SPOKE-validated PA standard residential ZIP, set against the SPOKE county's food-insecurity and severe-housing-problem rates. The values track county: central-Philadelphia ZIPs (19102–19104) carry the highest food insecurity (15.8%) and housing burden (22.7%), while suburban Delaware-County ZIPs (19013/19023/19079) sit lower (9.1% / 15.5%) — surfacing where these coupled basic-needs services align with the greatest measured hardship.

## SPARQL query executed
```sparql
SELECT DISTINCT ?zip ?service ?serviceType ?foodInsecurity ?severeHousing WHERE {
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
        <https://purl.org/okn/frink/kg/spoke-okn/schema/variable> "food insecurity" ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/value> ?foodInsecurity .
    ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> <https://purl.org/okn/frink/kg/spoke-okn/schema/PREVALENCEIN_SpL> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?county ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/variable> "severe housing problems" ;
        <https://purl.org/okn/frink/kg/spoke-okn/schema/value> ?severeHousing .
  }
  GRAPH <https://purl.org/okn/frink/kg/dreamkg> {
    ?svc <http://schema.org/postalCode> ?zip ;
         <http://schema.org/category> ?cat ;
         <http://schema.org/identifier> ?id .
    FILTER(CONTAINS(STR(?cat),'/service_type/Shelter') || CONTAINS(STR(?cat),'/service_type/Food'))
    BIND(IF(CONTAINS(STR(?cat),'Shelter'),'Shelter','Food') AS ?serviceType)
    BIND(REPLACE(STR(?id),'_[0-9]+$','') AS ?service)
  }
} ORDER BY ?zip LIMIT 12
```

## Literature validation

According to PubMed, Ra et al. (2021, *J Soc Distress Homeless*) found that unsheltered and unstably housed adults used fewer shelter-based health services and had significantly **higher food insecurity** than sheltered adults — empirically tying together food insecurity, shelter-service access, and health risk in the homeless population, the coupled basic-needs hardship this food + shelter join maps. [PMID:37346936](https://pubmed.ncbi.nlm.nih.gov/37346936/) · [DOI](https://doi.org/10.1080/10530789.2021.1961990)

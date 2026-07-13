# Where Philadelphia substance-use treatment facilities and homelessness social services co-locate — and the three ZIPs with treatment but no shelter/food/medical listing

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>

## Conversation

👤 **User**

Crosswalk: `dreamkg` × `ruralkg` on **ZIP5**. dreamkg carries the ZIP of each Philadelphia social-service listing on `schema:postalCode` in the HTTP-scheme form (`<http://schema.org/postalCode>`); ruralkg carries the ZIP of each substance-use `TreatmentProvider` on the HTTPS-scheme form (`<https://schema.org/postalCode>`). Normalize both to a bare 5-digit ZIP (strip non-digits, left-pad a 4-digit value with `0`, truncate ZIP+4 to the first five) and match.

Research question: in Philadelphia ZIPs, where do dreamkg's social services (shelter, food, medical care) co-locate with ruralkg's substance-use treatment facilities — i.e. which neighborhoods have treatment access but a social-service desert, or vice versa?

Why the join is required: dreamkg is a Philadelphia homelessness/social-service catalog — it knows *what basic-needs and behavioral-health help is offered where* (temporary shelter, food pantries, medical care, counseling), but it holds no inventory of licensed substance-use treatment facilities. ruralkg — despite its name — carries a **national** SAMHSA-derived facility list, so it knows *where treatment capacity sits*, but nothing about whether a person walking out of that facility can find a bed or a meal in the same neighborhood. Neither graph can see the other's provision. The ZIP is the only shared key, and it is precisely what makes the access gap visible: recovery depends on treatment AND on the wraparound services that keep someone housed and fed.

---

🧠 **Assistant**

The ZIP5 key joins the two graphs across **30 shared ZIP codes**, linking **456 dreamkg service listings** to **52 ruralkg treatment facilities**. Because dreamkg is Philadelphia-scoped and ruralkg's ZIP set is national (5,420 ZIPs), the intersection *is* the Philadelphia-area subset of ruralkg. Every row below carries BOTH graphs — the facility count is ruralkg, the service counts are dreamkg:

| ZIP | ruralkg treatment facilities | dreamkg service listings (all) | dreamkg shelter / food / medical-care listings |
| --- | --- | --- | --- |
| 19104 | 4 | 55 | 20 |
| 19141 | 4 | 20 | 4 |
| 19124 | 3 | 22 | 7 |
| 19128 | 3 | 14 | 3 |
| 19131 | 3 | 27 | 9 |
| 17602 | 2 | 1 | 1 |
| **19047** | **2** | **1** | **0** |
| 19107 | 2 | 37 | 9 |
| 19110 | 2 | 1 | 1 |
| 19123 | 2 | 17 | 9 |
| 19125 | 2 | 12 | 4 |
| 19129 | 2 | 4 | 1 |
| 19132 | 2 | 22 | 8 |
| 19140 | 2 | 16 | 7 |
| 19153 | 2 | 11 | 2 |
| 19102 | 1 | 19 | 3 |
| 19106 | 1 | 8 | 3 |
| **19114** | **1** | **6** | **0** |
| 19121 | 1 | 12 | 8 |
| 19122 | 1 | 13 | 7 |
| 19126 | 1 | 2 | 1 |
| 19133 | 1 | 21 | 6 |
| 19134 | 1 | 22 | 8 |
| 19139 | 1 | 29 | 12 |
| 19143 | 1 | 23 | 12 |
| 19144 | 1 | 23 | 10 |
| 19146 | 1 | 20 | 5 |
| 19148 | 1 | 4 | 1 |
| 19149 | 1 | 7 | 5 |
| **19152** | **1** | **2** | **0** |

**Treatment access, no basic-needs listing (3 ZIPs).** Three of the thirty shared ZIPs hold a ruralkg treatment facility but **zero** dreamkg listings in the shelter / food / medical-care categories. Naming them from ruralkg:

| ZIP | ruralkg treatment facility | dreamkg shelter/food/medical listings |
| --- | --- | --- |
| 19047 | Penndel Mental Health Center | 0 |
| 19047 | Family Service Assoc of Bucks County | 0 |
| 19114 | JEVS Human Services | 0 |
| 19152 | People Acting to Help (PATH) Inc | 0 |

All three sit on the metropolitan edge — 19047 is Penndel/Langhorne in Bucks County, 19114 and 19152 are Far Northeast Philadelphia. Within the coverage of these two graphs, a person in treatment at any of these four facilities has no co-located shelter bed, food pantry or medical-care listing in dreamkg's catalog; the nearest such support is in another ZIP.

**The inverse — services, no treatment facility (23 ZIPs).** dreamkg covers 53 ZIPs; 23 of them have social services but no ruralkg treatment facility at all. The largest:

| ZIP | dreamkg service listings | ruralkg treatment facilities |
| --- | --- | --- |
| 19103 | 17 | 0 |
| 19136 | 16 | 0 |
| 19147 | 11 | 0 |
| 19145 | 9 | 0 |
| 19151 | 9 | 0 |
| 19111 | 8 | 0 |
| 19120 | 7 | 0 |
| 19130 | 7 | 0 |
| 19138 | 7 | 0 |
| 19142 | 6 | 0 |

**Why it answers the question.** The two ends of the recovery pathway are held in different graphs, and the ZIP is what puts them on the same row. The strong co-location cases are unambiguous: **19104** (University City / West Philadelphia) pairs 4 treatment facilities with 55 dreamkg listings, 20 of them shelter/food/medical — the densest service-and-treatment cluster in the join. **19107** (Center City East) and **19131** (Overbrook) are similar. Against that, the join surfaces the asymmetries a single graph cannot see: the three edge ZIPs (19047, 19114, 19152) with treatment capacity but no basic-needs listing in dreamkg, and the 23 dreamkg ZIPs — led by 19103, 19136 and 19147 — where social services exist but ruralkg lists no substance-use treatment facility. Those are the two directions of the access gap the question asks for, and neither is visible without the crosswalk.

**Coverage caveat — read the zeros as graph coverage, not ground truth.** A zero here means *absent from that graph*, not *absent from the world*. dreamkg is a curated Philadelphia homelessness-services catalog, not a census of every food pantry; ruralkg's facility list is SAMHSA-derived and its Philadelphia coverage is a byproduct of a national ZIP set, not a targeted urban survey. A ZIP with treatment but no dreamkg basic-needs listing is a **desert within the coverage of these two graphs** — a hypothesis worth field-checking, not an established service desert. The ZIP is also a coarse unit: adjacent ZIPs are often a short walk apart, so a strict same-ZIP test overstates isolation.

**Validation.** Validated by construction on the authoritative shared standard — the USPS 5-digit ZIP code — plus the hand-verified crosswalk `J6-zip-dreamkg-ruralkg` (verified_count 30). The only obstacle is representational, not semantic: dreamkg stores `postalCode` under the HTTP schema.org namespace and ruralkg under the HTTPS one, so the predicate must be bound scheme-aware on each side before the literals can be normalized and matched. Once normalized, the 30-ZIP intersection reproduces the crosswalk's verified count exactly, and the entity counts (456 dreamkg services, 52 ruralkg facilities) match the recipe's recorded values. **Validated** (shared ZIP5 standard; all rows executed live).

#### Query 1 — The 30 shared ZIPs: ruralkg treatment facilities alongside dreamkg service listings, with shelter/food/medical-care listings broken out

```sparql
SELECT ?zip ?nFacilities ?nServices ?nBasicNeeds WHERE {
  { SELECT ?zip (COUNT(DISTINCT ?r) AS ?nFacilities) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
        BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?p)
        ?r a <http://sail.ua.edu/ruralkg/treatment/TreatmentProvider> ; ?p ?z1 . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5)) AS ?zip)
    } GROUP BY ?zip }
  { SELECT ?zip (COUNT(DISTINCT ?d) AS ?nServices) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?d <http://schema.org/postalCode> ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip)
    } GROUP BY ?zip }
  OPTIONAL {
    SELECT ?zip (COUNT(DISTINCT ?d2) AS ?nBasicNeeds) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> {
        ?d2 <http://schema.org/postalCode> ?z2 ; <http://schema.org/category> ?cat .
        FILTER(CONTAINS(STR(?cat),'service_type/Shelter') || CONTAINS(STR(?cat),'service_type/Food') || CONTAINS(STR(?cat),'service/main/MedicalCare')) }
      BIND(REPLACE(STR(?z2),"[^0-9]","") AS ?b)
      BIND(IF(STRLEN(?b)=4, CONCAT("0",?b), SUBSTR(?b,1,5)) AS ?zip)
    } GROUP BY ?zip }
} ORDER BY DESC(?nFacilities) ?zip
```

_30 row(s) — showing first 5_

| zip | nFacilities | nServices | nBasicNeeds |
| --- | --- | --- | --- |
| 19104 | 4 | 55 | 20 |
| 19141 | 4 | 20 | 4 |
| 19124 | 3 | 22 | 7 |
| 19128 | 3 | 14 | 3 |
| 19131 | 3 | 27 | 9 |

#### Query 2 — Named ruralkg treatment facilities in the three shared ZIPs that have no dreamkg shelter, food or medical-care listing

```sparql
SELECT ?zip ?name WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?p)
    BIND(IRI(CONCAT('https://schema.org/','name')) AS ?pn)
    ?r a <http://sail.ua.edu/ruralkg/treatment/TreatmentProvider> ; ?p ?z1 ; ?pn ?name . }
  BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
  BIND(IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5)) AS ?zip)
  FILTER(?zip IN ("19047","19114","19152"))
} ORDER BY ?zip
```

_4 row(s)_

| zip | name |
| --- | --- |
| 19047 | Penndel Mental Health Center |
| 19047 | Family Service Assoc of Bucks County |
| 19114 | JEVS Human Services |
| 19152 | People Acting to Help (PATH) Inc |

#### Query 3 — The inverse gap: dreamkg ZIPs with social services but no ruralkg substance-use treatment facility

```sparql
SELECT ?zip ?nServices WHERE {
  { SELECT ?zip (COUNT(DISTINCT ?d) AS ?nServices) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?d <http://schema.org/postalCode> ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip)
    } GROUP BY ?zip }
  MINUS {
    SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
        BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?p)
        ?r a <http://sail.ua.edu/ruralkg/treatment/TreatmentProvider> ; ?p ?z1 . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5)) AS ?zip) } }
} ORDER BY DESC(?nServices) ?zip
```

_23 row(s) — showing first 5_

| zip | nServices |
| --- | --- |
| 19103 | 17 |
| 19136 | 16 |
| 19147 | 11 |
| 19145 | 9 |
| 19151 | 9 |

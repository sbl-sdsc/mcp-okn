# Which federal district court has jurisdiction over the ZIPs where Philadelphia social services sit, and what case activity does SCALES record there?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>
- `scales` — <https://purl.org/okn/frink/kg/scales>

## Conversation

👤 **User**

Crosswalk: `dreamkg` × `scales` on **ZIP5** (verified count 53). dreamkg carries a `schema:postalCode` on every Philadelphia social-service location (the plain HTTP schema.org IRI, so a bracketed `<http://schema.org/postalCode>` works). scales carries `niem-core:AddressPostalCode` on its `jxdm:Court` entities — and that ZIP is NOT a court's street address: 100 Court entities carry ~41k ZIPs, i.e. the predicate enumerates each court's ZIP JURISDICTION TERRITORY, making scales a ZIP → federal-district-court resolver. Normalization: strip non-digits and left-pad both sides to 5 digits (scales mixes plain integers with zero-padded strings), then intersect two DISTINCT sub-SELECTs on a shared ?zip variable — never a cross-graph FILTER(STR(?a)=STR(?b)).

Research question: which federal district court has jurisdiction over the ZIPs where Philadelphia social services (shelter, food, medical/mental-health care) are located, and what case activity does scales record in that court?

Why the join is required: dreamkg knows *where help is* — named shelters, food pantries and mental-health/medical providers, each tagged with a ZIP — but holds nothing about courts, jurisdiction, or litigation. scales knows *which federal district court's territory a ZIP falls in* and the full docket of cases filed there (docket ID, nature-of-suit code, filing/termination dates, judge, parties) — but holds no social services and no idea what sits inside its ZIPs. The 5-digit ZIP is the only bridge between the service map and the court map.

---

🧠 **Assistant**

**All 53 of dreamkg's ZIPs resolve to a single federal district court: the U.S. District Court for the Eastern District of Pennsylvania (E.D. Pa.), in the Third Circuit.** Every Philadelphia social service dreamkg catalogs — shelter, food, and mental-health care alike — sits inside that one court's ZIP jurisdiction territory.

**Join mechanics.** Shared key = the normalized 5-digit ZIP. dreamkg supplies the service side (`schema:postalCode` + `schema:category` → `/service_type/{Shelter,Food,Mental Health}`); scales supplies the court side (`niem-core:AddressPostalCode` on a `jxdm:Court`, plus `jxdm:CourtName` and `scales:isInCircuit`). Both sides are stripped to digits and left-padded to 5, then intersected as two DISTINCT sub-SELECTs on `?zip`. **Both KGs populate every row:** the service type and counts are dreamkg entities; the court name and circuit are real scales values.

### The court with jurisdiction, by dreamkg service type

| dreamkg service type | services | dreamkg ZIPs | scales court with jurisdiction | circuit |
| --- | --- | --- | --- | --- |
| Mental Health | 412 | 45 | District Court, E.D. Pennsylvania | Third |
| Food | 137 | 45 | District Court, E.D. Pennsylvania | Third |
| Shelter | 35 | 22 | District Court, E.D. Pennsylvania | Third |

No second court appears in any row — the join is a clean 53 → 1 resolution.

### The case activity scales records in that court

scales holds **13,751 federal cases** in E.D. Pa., filed between **2002-05-06** and **2017-12-29**. The dominant nature-of-suit categories are:

| scales case subcategory (nature of suit) | cases in E.D. Pa. |
| --- | --- |
| 442 Employment | 1,369 |
| 440 Other Civil Rights | 914 |
| 510 Motions To Vacate Sentence | 909 |
| 110 Insurance | 700 |
| 530 General (habeas corpus) | 685 |
| 360 Other Personal Injury | 652 |

**Why it answers the question.** The question has two halves and the ZIP join supplies both. First, *which court*: dreamkg's 53 service ZIPs (all 190xx–191xx) each fall inside exactly one scales court ZIP territory, and that territory belongs to `District Court, E.D. Pennsylvania` (Third Circuit) — so the federal forum for any suit arising where these 584 shelter/food/mental-health services operate is E.D. Pa., unambiguously and with no split. Second, *what case activity*: having resolved the ZIPs to a court, scales' docket for that same court is directly readable — 13,751 cases over 2002–2017, led by civil-rights-adjacent litigation (442 Employment at 1,369 cases and 440 Other Civil Rights at 914 are the two largest categories, ahead of the prisoner-petition pair 510/530 at 909 and 685). That is a legally meaningful pairing for a homelessness/social-services graph: the court that would hear a §1983 or ADA claim brought by or on behalf of the populations dreamkg's services serve is the same court whose two heaviest civil dockets are employment and other civil-rights actions. Neither graph can state this alone — dreamkg has no court, scales has no services.

**Validation.** Validated by construction on the authoritative shared standard (the USPS 5-digit ZIP code) plus the hand-verified crosswalk (`J5-zip-dreamkg-scales`, verified_count 53, reproduced live). The named court is independently corroborated: 28 U.S.C. § 118(a) places Philadelphia County in the Eastern District of Pennsylvania, and E.D. Pa. sits in the Third Circuit — exactly what the join returns from scales' own `CourtName`/`isInCircuit` values, with no court hard-coded on either side of the query. **Validated.**

#### Query 1 — dreamkg's Philadelphia shelter / food / mental-health services, resolved through their ZIP to the scales federal district court whose jurisdiction territory contains them

```sparql
PREFIX jxdm: <http://release.niem.gov/niem/domains/jxdm/7.2/#>
PREFIX nc: <http://release.niem.gov/niem/niem-core/5.0/#>
PREFIX scales: <http://schemas.scales-okn.org/rdf/scales#>
SELECT ?serviceType (COUNT(DISTINCT ?svc) AS ?services) (COUNT(DISTINCT ?zip) AS ?zips) ?courtName ?circuit WHERE {
  { SELECT DISTINCT ?zip ?svc ?serviceType WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> {
        ?svc <http://schema.org/postalCode> ?z0 ; <http://schema.org/category> ?cat .
        FILTER(CONTAINS(STR(?cat),'/service_type/')) }
      BIND(REPLACE(REPLACE(STR(?cat),'^.*/service_type/',''),'%20',' ') AS ?serviceType)
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip) } }
  { SELECT DISTINCT ?zip ?courtName ?circuit WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?court nc:AddressPostalCode ?z1 ; jxdm:CourtName ?courtName ; scales:isInCircuit ?circuit . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=3, CONCAT("00",?e),
           IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5))) AS ?zip) } }
} GROUP BY ?serviceType ?courtName ?circuit ORDER BY DESC(?services)
```

_3 row(s)_

| serviceType | services | zips | courtName | circuit |
| --- | --- | --- | --- | --- |
| Mental Health | 412 | 45 | District Court, E.D. Pennsylvania | Third |
| Food | 137 | 45 | District Court, E.D. Pennsylvania | Third |
| Shelter | 35 | 22 | District Court, E.D. Pennsylvania | Third |

#### Query 2 — Total case volume and filing-date span scales records for the court reached from dreamkg's service ZIPs

```sparql
PREFIX jxdm: <http://release.niem.gov/niem/domains/jxdm/7.2/#>
PREFIX nc: <http://release.niem.gov/niem/niem-core/5.0/#>
SELECT (COUNT(DISTINCT ?case) AS ?totalCases) (MIN(?start) AS ?earliestFiling) (MAX(?start) AS ?latestFiling) WHERE {
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?d <http://schema.org/postalCode> ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip) } }
  { SELECT DISTINCT ?zip ?court WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?court nc:AddressPostalCode ?z1 ; jxdm:CourtName ?cn . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=3, CONCAT("00",?e),
           IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5))) AS ?zip) } }
  GRAPH <https://purl.org/okn/frink/kg/scales> {
    ?case jxdm:CaseCourt ?court ; nc:StartDate ?start .
  }
}
```

_1 row(s)_

| totalCases | earliestFiling | latestFiling |
| --- | --- | --- |
| 13751 | 2002-05-06 | 2017-12-29 |

#### Query 3 — The leading nature-of-suit categories among the cases scales records in the court that has jurisdiction over dreamkg's service ZIPs

```sparql
PREFIX jxdm: <http://release.niem.gov/niem/domains/jxdm/7.2/#>
PREFIX nc: <http://release.niem.gov/niem/niem-core/5.0/#>
SELECT ?courtName ?subCategory (COUNT(DISTINCT ?case) AS ?cases) WHERE {
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?d <http://schema.org/postalCode> ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip) } }
  { SELECT DISTINCT ?zip ?court ?courtName WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?court nc:AddressPostalCode ?z1 ; jxdm:CourtName ?courtName . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=3, CONCAT("00",?e),
           IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5))) AS ?zip) } }
  GRAPH <https://purl.org/okn/frink/kg/scales> {
    ?case jxdm:CaseCourt ?court ; nc:CaseSubCategoryText ?subCategory .
  }
} GROUP BY ?courtName ?subCategory ORDER BY DESC(?cases) LIMIT 6
```

_6 row(s)_

| courtName | subCategory | cases |
| --- | --- | --- |
| District Court, E.D. Pennsylvania | 442 Employment | 1369 |
| District Court, E.D. Pennsylvania | 440 Other Civil Rights | 914 |
| District Court, E.D. Pennsylvania | 510 Motions To Vacate Sentence | 909 |
| District Court, E.D. Pennsylvania | 110 Insurance | 700 |
| District Court, E.D. Pennsylvania | 530 General | 685 |
| District Court, E.D. Pennsylvania | 360 Other Personal Injury | 652 |

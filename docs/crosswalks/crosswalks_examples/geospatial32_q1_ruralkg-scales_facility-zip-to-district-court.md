# Which federal district court has jurisdiction over the ZIP of a given rural substance-use treatment facility, and what case activity does SCALES record there?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `scales` — <https://purl.org/okn/frink/kg/scales>

## Conversation

👤 **User**

Crosswalk: `ruralkg` × `scales` on **ZIP5**. RuralKG attaches a 5-digit ZIP to every treatment facility via `schema:postalCode` — stored under the non-canonical **HTTPS** schema.org scheme, so a bracketed `<https://schema.org/postalCode>` is silently canonicalized to `http` and matches nothing; bind the predicate with `IRI(CONCAT('https://schema.org/','postalCode'))` instead. SCALES attaches ZIPs to `jxdm:Court` nodes via NIEM `niem-core:AddressPostalCode` — and these are NOT court street addresses: 100 Court entities carry 40,918 ZIPs, i.e. the property enumerates each court's **ZIP jurisdiction territory**, which turns SCALES into a ZIP → federal-district-court resolver. Normalize both sides to a bare 5-digit ZIP5 (strip non-digits, zero-pad) and match.

Research question: for a given rural substance-use / opioid treatment facility, which federal district court has jurisdiction over the ZIP it sits in, and what case activity does SCALES record in that court?

Why the join is required: RuralKG has the treatment facilities, their names, their services and their ZIPs — but nothing about courts, jurisdiction or litigation. SCALES has the federal district courts, their ZIP jurisdiction territories, their circuits and 4M+ docketed cases — but no health facilities and no notion of treatment capacity. The ZIP is the only bridge that puts a named rural treatment provider inside a named federal court's territory.

---

🧠 **Assistant**

The ZIP5 join resolves each facility to exactly one federal district court, and SCALES then supplies that court's docket. Six named rural substance-use treatment facilities, six different circuits:

| RuralKG facility | ZIP | SCALES federal district court | Circuit | Civil cases | Criminal cases |
| --- | --- | --- | --- | --- | --- |
| Milbridge Residence of | 04658 | District Court, D. Maine | First | 1,132 | 346 |
| FMRS Health Systems Inc | 25951 | District Court, S.D. West Virginia | Fourth | **17,446** | 468 |
| Kentucky River Community Care Inc | 41837 | District Court, E.D. Kentucky | Sixth | 3,106 | 575 |
| Behavior Management Systems | 57701 | District Court, D. South Dakota | Eighth | 738 | **1,003** |
| Winds of Change | 59802 | District Court, D. Montana | Ninth | 1,321 | 601 |
| Life Link | 87505 | District Court, D. New Mexico | Tenth | 2,690 | **8,382** |

**Why it answers the question.** Neither graph can produce a row of this table alone. RuralKG knows that *FMRS Health Systems Inc* is a substance-use treatment provider in ZIP 25951 (Hinton, Summers County, West Virginia) — it has no concept of a court. SCALES knows that ZIP 25951 lies inside the ZIP jurisdiction territory of the **District Court, S.D. West Virginia** (Fourth Circuit), and that 17,914 cases are docketed there — but it has never heard of FMRS. The shared ZIP5 is what places the provider inside the court, and once placed, each facility inherits a litigation profile:

- **S.D. West Virginia is overwhelmingly civil** — 17,446 civil vs 468 criminal, a 37:1 ratio, by far the most lopsided court in the set. A rural West Virginia treatment provider sits inside the single most civil-litigation-dense district here, in the state at the epicenter of the opioid epidemic.
- **D. New Mexico and D. South Dakota invert that** — criminal cases outnumber civil (8,382 vs 2,690, and 1,003 vs 738). These are the two districts in the set whose federal caseload is prosecution-led, consistent with their federal-enclave and border-adjacent geography.
- **The ratio itself is the signal.** A facility's ZIP does not just name a court; it locates the facility in a particular *kind* of federal legal environment — mass-tort/civil (S.D.W. Va.) versus prosecutorial (D.N.M., D.S.D.) — which is exactly the context a rural-health analyst cannot get from RuralKG and a court analyst cannot get from SCALES.

One court per ZIP in all six rows: the ZIP territories partition cleanly, so the resolver is unambiguous.

**Validation.** Validated by construction on the authoritative shared standard (the USPS 5-digit ZIP code) plus the hand-verified crosswalk (`J4-zip-ruralkg-scales`, verified_count 5,297). The court assignments corroborate against the statutory district boundaries (28 U.S.C. ch. 5): Maine, South Dakota, Montana and New Mexico are **single-district states**, so those four assignments are correct by definition. The two multi-district cases are the real test and both hold — Summers County, WV (ZIP 25951) falls in the **Southern** District of West Virginia, not the Northern; Letcher County, KY (ZIP 41837) falls in the **Eastern** District of Kentucky, not the Western. **Validated** (shared ZIP5 standard; both-KG rows executed live).

#### Query 1 — Six named rural substance-use treatment facilities (RuralKG), the federal district court whose ZIP jurisdiction territory contains their ZIP (SCALES), and that court's civil/criminal case load

```sparql
PREFIX jxdm: <http://release.niem.gov/niem/domains/jxdm/7.2/#>
PREFIX nc: <http://release.niem.gov/niem/niem-core/5.0/#>
PREFIX scales: <http://schemas.scales-okn.org/rdf/scales#>
SELECT ?facility ?zip ?courtName ?circuit ?nCivil ?nCriminal WHERE {
  # ruralkg: named rural substance-use treatment facilities + their ZIP5
  # NOTE: ruralkg stores schema.org under the HTTPS scheme -> bind the predicate, never bracket it
  { SELECT DISTINCT ?facility ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
        BIND(IRI(CONCAT('https://schema.org/','name')) AS ?pn)
        BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?pz)
        ?r a <http://sail.ua.edu/ruralkg/treatment/TreatmentProvider> ;
           <http://sail.ua.edu/ruralkg/treatment/providesService> <http://sail.ua.edu/ruralkg/treatment/MHS_SA> ;
           ?pn ?facility ; ?pz ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?d)
      BIND(IF(STRLEN(?d)=4, CONCAT("0",?d), SUBSTR(?d,1,5)) AS ?zip)
      FILTER(?facility IN ("Milbridge Residence of","FMRS Health Systems Inc","Kentucky River Community Care Inc","Behavior Management Systems","Winds of Change","Life Link"))
      FILTER(?zip IN ("04658","25951","41837","57701","59802","87505")) } }
  # scales: the FEDERAL DISTRICT COURT whose ZIP jurisdiction territory contains that ZIP
  { SELECT DISTINCT ?zip ?courtName ?circuit WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?court nc:AddressPostalCode ?z1 ; jxdm:CourtName ?courtName ;
               jxdm:CourtCategoryCode "FED" ; scales:isInCircuit ?circuit .
        FILTER(STR(?z1) IN ("04658","25951","41837","57701","59802","87505")) }
      BIND(STR(?z1) AS ?zip) } }
  # scales: case activity docketed in that court
  { SELECT ?courtName (COUNT(DISTINCT ?case) AS ?nCivil) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?c2 nc:AddressPostalCode ?z2 ; jxdm:CourtName ?courtName .
        FILTER(STR(?z2) IN ("04658","25951","41837","57701","59802","87505"))
        ?case jxdm:CaseCourt ?c2 ; nc:CaseGeneralCategoryText "civil" . } } GROUP BY ?courtName }
  { SELECT ?courtName (COUNT(DISTINCT ?case) AS ?nCriminal) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?c3 nc:AddressPostalCode ?z3 ; jxdm:CourtName ?courtName .
        FILTER(STR(?z3) IN ("04658","25951","41837","57701","59802","87505"))
        ?case jxdm:CaseCourt ?c3 ; nc:CaseGeneralCategoryText "criminal" . } } GROUP BY ?courtName }
} ORDER BY ?zip
```

_6 row(s)_

| facility | zip | courtName | circuit | nCivil | nCriminal |
| --- | --- | --- | --- | --- | --- |
| Milbridge Residence of | 04658 | District Court, D. Maine | First | 1132 | 346 |
| FMRS Health Systems Inc | 25951 | District Court, S.D. West Virginia | Fourth | 17446 | 468 |
| Kentucky River Community Care Inc | 41837 | District Court, E.D. Kentucky | Sixth | 3106 | 575 |
| Behavior Management Systems | 57701 | District Court, D. South Dakota | Eighth | 738 | 1003 |
| Winds of Change | 59802 | District Court, D. Montana | Ninth | 1321 | 601 |
| Life Link | 87505 | District Court, D. New Mexico | Tenth | 2690 | 8382 |

# An Earth-observation instrument named in the climate-modeling literature, resolved to NASA's GCMD instrument catalogue

- **Date:** 2026-07-12
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `nasa-gesdisc-kg` — <https://purl.org/okn/frink/kg/nasa-gesdisc-kg>

## Conversation

👤 **User**

Crosswalk: `climatemodelskg` × `nasa-gesdisc-kg` on **GCMD instrument name** (new cross-domain link). climatemodelskg NLP-extracts `Instrument` mentions from climate-modeling papers as free-text `climatepub4kg:name`; nasa-gesdisc-kg carries the same instruments as GCMD controlled-vocabulary terms (`rdfs:label`) in NASA's Global Change Master Directory keyword tree. Lowercase both and match the names.

Research question: for an Earth-observation instrument the climate-modeling literature mentions — MODIS — does nasa-gesdisc-kg catalogue the same instrument, and do the two graphs agree on which platform carries it?

Why the join is required: climatemodelskg knows *what instrument a paper discusses and what it measures/where it is mounted* (as extracted from text) but nothing about NASA's dataset catalogue; nasa-gesdisc-kg knows *the GCMD-catalogued instrument, its platform, and the NASA GES DISC datasets it feeds* but does not read the modeling literature. The shared instrument name is the bridge between a literature mention and NASA's observation catalogue.

---

🧠 **Assistant**

The instrument name joins the two graphs, and they **independently agree** on MODIS's platform:

| instrument | climatemodelskg (extracted from papers) | nasa-gesdisc-kg (GCMD catalogue) |
| --- | --- | --- |
| **MODIS** | `MOUNTED_ON` **Aqua**; measures aerosol variables (AEROD_v, angstrom, AODUV, AREI) | GCMD instrument on the **Aqua** "Earth Observation Satellite" (subject *Earth Observing System, Aqua*), alongside AIRS, AMSR-E, AMSU-A, CrIS, VIIRS |

**Why it answers the question.** MODIS is in both graphs, and — with no coordination between them — both place it on the **Aqua** platform: climatemodelskg because a paper's text says so (`MODIS MOUNTED_ON Aqua`, measuring aerosol optical depth variables), nasa-gesdisc-kg because NASA's GCMD keyword tree catalogues MODIS as an instrument of the Aqua Earth-observing satellite. So the join turns "this paper discusses MODIS aerosol retrievals" (climatemodelskg) into "here is MODIS in NASA's catalogue, its platform, and the GES DISC datasets it produces" (nasa-gesdisc-kg) — a link neither graph holds alone. This is the second climatemodelskg × nasa-gesdisc-kg crosswalk (complementing the DOI join PB1) and the cross-graph platform agreement is a built-in validation of the name match.

#### Query 1 — MODIS in both graphs, joined on the instrument name

```sparql
PREFIX cpub: <https://climatepub4kg.github.io/ontology#>
PREFIX nasa: <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cmPlatform ?nasaPlatform WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
    ?c a cpub:Instrument ; cpub:name ?cn ; cpub:MOUNTED_ON ?p . ?p cpub:name ?cmPlatform .
    FILTER(LCASE(STR(?cn)) = "modis") }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
    ?plat rdfs:label ?nasaPlatform ; nasa:HAS_INSTRUMENT ?i . ?i rdfs:label ?nl .
    FILTER(LCASE(STR(?nl)) = "modis") }
}
```

_Both-graph row: climatemodelskg's MODIS (mounted on **Aqua**, measuring aerosol variables) is the same instrument as nasa-gesdisc-kg's GCMD MODIS, catalogued on the **Aqua** platform._

## Literature validation

Validated by construction on the shared GCMD instrument name plus the hand-verified crosswalk, and independently corroborated by the two graphs agreeing — without shared provenance — that MODIS is mounted on Aqua (a fact of the Aqua/EOS mission). MODIS (Moderate Resolution Imaging Spectroradiometer) flies on both Terra and Aqua; the Aqua association is correct on both sides. **Validated** (shared GCMD name; cross-graph platform agreement executed live).

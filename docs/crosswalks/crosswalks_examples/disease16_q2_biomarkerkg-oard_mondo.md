# Disease D16-Q2 — biomarkerkg × oard-kg (DOID↔MONDO): total disease overlap with the OARD EHR hub

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Disease & phenotype · **Shared identifier:** DOID ↔ MONDO (ubergraph bridge)

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg> (BiomarkerKB: literature biomarkers/variants linked to diseases (DOID), chemicals (CHEBI), cell types (CL))
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph> (OBO ontology hub; supplies the CHEBI↔CAS / DOID↔MONDO bridge mappings — carries no domain data of its own)
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg> (Open Annotations for Rare Diseases: EHR-derived disease↔phenotype co-occurrence, keyed on MONDO)

**Join:** biomarkerkg keys diseases on DOID (object of its `obo:OBCI_*` predicates); oard-kg keys on MONDO. Bridge through ubergraph `skos:exactMatch` (MONDO ⟶ DOID), then match the MONDO term in oard-kg. 247 shared diseases (verified 2026-06-18).

## Research question

**Q2.** How many BiomarkerKG diseases can be enriched with an OARD EHR phenotype signature via the DOID→MONDO bridge?

---

## Result

Count over the bridge (DISTINCT diseases):

| shared diseases (biomarkerkg DOID ↔ oard-kg MONDO) |
|---|
| 247 |

**Why this answers the question:** 247 distinct BiomarkerKG DOID diseases map to a MONDO term present in OARD. This is the size of the newly available join surface that lets any BiomarkerKG biomarker question inherit an OARD EHR phenotype profile — previously biomarkerkg only joined prokn/spoke-okn on DOID.

## SPARQL query executed

_2026-06-18 · biomarkerkg, ubergraph, oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?sharedDiseases) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?p ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

## Validation

Validated by construction on the disease ontology bridge: DOID (biomarkerkg) ⟶ MONDO (oard-kg) via ubergraph `skos:exactMatch`, the same bridge route used by the verified A10/A11 spoke-okn disease crosswalks. Every returned disease is a real MONDO/DOID term present in both graphs. Literature spot-checks are recommended as a further step.

## Sources

- Proto-OKN / FRINK federation via the `mcp-okn` service. Join verified with `get_join_strategy`; counts are exact `COUNT(DISTINCT)` verified 2026-06-18.

# Chemicals C10-Q1 — Tox21 × SPOKE (CHEBI↔CAS): Tox21-screened chemicals with SPOKE associations

- **Date:** 2026-06-18
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Domain:** Chemicals · **Shared identifier:** CHEBI ↔ CAS (ubergraph bridge)

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn> (SPOKE Open Knowledge Network: gene/compound/disease/anatomy associations)
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph> (OBO ontology hub; supplies the CHEBI↔CAS / DOID↔MONDO bridge mappings — carries no domain data of its own)
- `biobricks-tox21` — <https://purl.org/okn/frink/kg/biobricks-tox21> (Tox21 high-throughput in-vitro screening library)

**Join:** spoke-okn attaches CHEBI via `oboInOwl:hasDbXref`; ubergraph maps that CHEBI term to a `cas:` CURIE via `oboInOwl:hasDbXref`; rebuild the biobricks CAS IRI as `IRI(CONCAT('http://identifiers.org/cas/', SUBSTR(STR(?casCurie),5)))`. **NOTE:** biobricks-tox21 keys chemicals as its OWN node IRIs (`identifiers.org/cas/{CAS}`), so the rebuilt CAS IRI is matched in subject position (`?c2 ?p ?o`) — a naive `edam:has_identifier` join returns 0. 480 shared chemicals (verified 2026-06-18).

## Research question

**Q1.** Which Tox21 high-throughput-screened chemicals are also SPOKE compounds (and thus carry SPOKE gene/disease/compound associations)? Why does this require the join?

---

## Result

The join links Tox21's in-vitro bioactivity to SPOKE's mechanistic associations; neither graph carries the other's content. Sample (12 of 480):

| Chemical (Tox21 label) | CAS |
|---|---|
| Acetaldehyde | 75-07-0 |
| Acrylamide | 79-06-1 |
| Acrylonitrile | 107-13-1 |
| Aniline | 62-53-3 |
| Atrazine | 1912-24-9 |
| Benzene | 71-43-2 |
| Benzo(a)pyrene | 50-32-8 |
| Bisphenol A | 80-05-7 |
| 1,3-Butadiene | 106-99-0 |
| Caprolactam | 105-60-2 |
| Acrolein | 107-02-8 |
| 1,4-Dioxane | 123-91-1 |

**Why this answers the question:** each chemical is in the Tox21 screening library AND is a SPOKE compound node — benzene, benzo(a)pyrene, bisphenol A, atrazine, acrylamide, butadiene. A Tox21 bioactivity profile can now be read alongside the chemical's SPOKE gene-regulation and disease links.

## SPARQL query executed

_2026-06-18 · spoke-okn, ubergraph, biobricks-tox21_

```sparql
SELECT DISTINCT ?label (REPLACE(STR(?c2),'http://identifiers.org/cas/','') AS ?CAS) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?chebi . FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?chebi <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:')) }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> { ?c2 <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
} ORDER BY ?label
```

## Validation

Validated by construction on the authoritative shared standard: the CHEBI↔CAS mapping is taken from ubergraph's curated `oboInOwl:hasDbXref` cross-references (the same bridge used by the verified C05 spoke-okn×ToxCast crosswalk), and every returned chemical carries a real CAS Registry Number present in both graphs. The returned set is dominated by canonical, well-characterised toxicants, consistent with biological expectation. Literature (PubMed/PaperClip) spot-checks are recommended as a further step.

## Sources

- Proto-OKN / FRINK federation via the `mcp-okn` service. Join verified with `get_join_strategy`; counts are exact `COUNT(DISTINCT)` verified 2026-06-18.

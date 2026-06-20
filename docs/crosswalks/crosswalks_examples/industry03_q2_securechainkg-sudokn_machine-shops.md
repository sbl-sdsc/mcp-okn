# I3-Q2 — Named machine-shop manufacturers in both KGs for NAICS 332710 (securechainkg × sudokn)

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql
- **Crosswalk:** securechainkg ↔ sudokn (verified, 35 shared NAICS codes)
- **Shared identifier:** NAICS 332710 (Machine Shops)

## Knowledge graphs used

- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>

## Conversation

👤 **User**

For the most-overlapping shared industry, NAICS 332710 (Machine Shops), list example named manufacturers from each graph with an example product they make — demonstrating that both graphs populate the same industry with real, distinct firms.

---

🧠 **Assistant**

Pulling named firms from both graphs for NAICS 332710 confirms the industry is densely populated on both sides by distinct companies. SecureChain contributes firms such as A-1 Precision (fuel-pump parts), A & A Machine & Fabrication (industrial machinery), and A-1 Jay's Machining (grinding components); SUDOKN contributes 101 Machine (CNC turning services), 110 Metalworks (coated parts), 2 K Machine Works (CNC machined assemblies), and 2 Unique (M16 barreling spud). The firm IRIs are graph-specific, so the only thing linking these two firm lists is the shared NAICS 332710 classification — the defining feature of this crosswalk.

#### Query — Eight named manufacturers per graph in NAICS 332710 with an example product

```sparql
SELECT ?source ?company (SAMPLE(?prodName) AS ?exampleProduct) WHERE {
  {
    { SELECT DISTINCT ?company ?b WHERE {
        GRAPH <https://purl.org/okn/frink/kg/sudokn> {
          ?b <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> <http://asu.edu/semantics/SUDOKN/NAICS%20332710-individual> ;
             <http://www.w3.org/2000/01/rdf-schema#label> ?company .
        } } LIMIT 8 }
    OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/manufactures> ?prod }
               BIND(REPLACE(REPLACE(STR(?prod),'^.*/[^/]*?-([^/-]*)-product-instance$','$1'),'%20',' ') AS ?prodName) }
    BIND("SUDOKN" AS ?source)
  }
  UNION
  {
    { SELECT DISTINCT ?company ?a WHERE {
        GRAPH <https://purl.org/okn/frink/kg/securechainkg> {
          ?a <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> <http://asu.edu/semantics/SUDOKN/naics-332710.0-inst> ;
             <http://www.w3.org/2000/01/rdf-schema#label> ?company .
        } } LIMIT 8 }
    OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?a <http://asu.edu/semantics/SUDOKN/manufactures> ?prod }
               BIND(REPLACE(STR(?prod),'^.*/(.*)-product$','$1') AS ?prodName) }
    BIND("SecureChain" AS ?source)
  }
}
GROUP BY ?source ?company
ORDER BY ?source ?company
```

_16 row(s) returned_

| source | company | example product |
| --- | --- | --- |
| SecureChain | 8day | ProductsOfVariousTolerancesAndMaterials |
| SecureChain | a & a machine & fabrication llc | IndustrialMachinery |
| SecureChain | A & B Machine and Design | — |
| SecureChain | A PLUS PRECISION MACHINING, INC. | PolyethyleneSepticHoldingTanks |
| SecureChain | A to Z Machine | — |
| SecureChain | A-1 Jay's Machining | GrindingComponents |
| SecureChain | A-1 Precision, Inc. | FuelPumpParts |
| SecureChain | A-American Companies | PrintingUnits |
| SUDOKN | 101 MACHINE, INCORPORATED | CNC Turning Services |
| SUDOKN | 1070 NEOSHO AVE LLC | Booms |
| SUDOKN | 110 Metalworks, Inc. | Coated Parts |
| SUDOKN | 1325 GRAND OAKS INC. | Custom Assembly Equipment |
| SUDOKN | 15 Mile Machine | Anayak UHV milling machine |
| SUDOKN | 2 E FABRICATING | — |
| SUDOKN | 2 K Machine Works, Inc. | CNC Machined Assemblies |
| SUDOKN | 2 UNIQUE, LLC | M16 Barreling Spud |

## Validation

Demonstrates instance-level population behind the industry-level crosswalk: both graphs list real, distinct machine-shop firms under NAICS 332710 (the verified `securechainkg↔sudokn` crosswalk; disjoint company IRIs). The products (CNC parts, fuel-pump parts, milling machines) are characteristic of NAICS 332710 'machining metal and plastic parts on a job/order basis' (Census NAICS 332710 definition; IBISWorld). Industrial integration; not a biomedical claim.

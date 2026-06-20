# CW11-Q2: SPOKE liver-cancer prognostic markers linked to ProKN via Wikidata bridge

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>

## Conversation

👤 **User**

Crosswalk: prokn × wikidata × spoke-okn, bridged HGNC<->Entrez via Wikidata (P351 Entrez, P354 HGNC).

Research question: Which genes that SPOKE flags as liver-cancer prognostic markers (favorable/unfavorable) are present in ProKN's protein knowledge graph, reached through the Wikidata HGNC<->Entrez bridge? This lets a researcher pull ProKN protein-level context for SPOKE's prognostic-marker genes.

Why the join is required: SPOKE prognostic-marker genes are keyed by Entrez; ProKN references genes by HGNC. The two are only connectable through the Wikidata Entrez<->HGNC mapping, so the prognostic-marker-to-protein link requires the three-graph bridge.

---

🧠 **Assistant**

SPOKE liver-cancer prognostic-marker genes bridged (Entrez -> Wikidata -> HGNC) to their ProKN protein entries:

| Gene | SPOKE marker (liver cancer) | HGNC | ProKN protein (Ensembl) |
|---|---|---|---|
| ABCC1 (MRP1) | unfavorable | 51 | ENSG00000103222 |
| ABCB6 | unfavorable | 47 | ENSG00000115657 |
| ABCC5 | unfavorable | 56 | ENSG00000114770 |
| AATF | unfavorable | 19235 | ENSG00000275700 |
| ABAT | favorable | 23 | ENSG00000183044 |
| AASS | favorable | 17366 | ENSG00000008311 |

Why this answers the question: each gene is a SPOKE liver-cancer prognostic marker, and the query maps its Entrez id through Wikidata to its HGNC id and into ProKN's protein graph, returning the matching ProKN protein. ABCC1 (MRP1, the multidrug-resistance transporter) is an unfavorable liver-cancer marker in SPOKE and is retrieved with its ProKN protein entry — exactly the prognostic-marker-to-protein link the crosswalk enables, and impossible without the Wikidata HGNC<->Entrez bridge.

Literature validation (PubMed): ABCC1/MRP1 in hepatocellular carcinoma prognosis / multidrug resistance is supported (e.g. PMIDs 21182225, 32010961). The prognostic-marker biology is literature-attested.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `spoke-okn`, `wikidata`, `prokn`_

```sparql
PREFIX spoke: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT ?sym ?markerType ?hgnc ?proknProtein WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?gene spoke:MARKER_NEG_GmnD ?c . BIND("unfavorable" AS ?markerType) }
    UNION
    { ?gene spoke:MARKER_POS_GmpD ?c . BIND("favorable" AS ?markerType) }
    ?c rdfs:label "liver cancer" .
    ?gene rdfs:label ?sym .
  }
  BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> {
    ?item wdt:P351 ?entrez ; wdt:P354 ?hgnc .
  }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?proknProtein rdfs:seeAlso ?h .
  }
} ORDER BY ?sym LIMIT 20
```

_20 row(s) — showing first 5_

| sym | markerType | hgnc | proknProtein |
| --- | --- | --- | --- |
| A1BG | favorable | 5 | https://www.ensembl.org/id/ENSG00000121410 |
| AAMP | unfavorable | 18 | https://www.ensembl.org/id/ENSG00000127837 |
| AAR2 | unfavorable | 15886 | https://www.ensembl.org/id/ENSG00000131043 |
| AASS | favorable | 17366 | https://www.ensembl.org/id/ENSG00000008311 |
| AATF | unfavorable | 19235 | https://www.ensembl.org/id/ENSG00000275700 |

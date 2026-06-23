# Joining SPOKE and ProKN — Verified Recipes

- **Date:** 2026-06-19
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>

## Conversation

👤 **User**

How do I join SPOKE and ProKN? Show the verified recipe and shared identifier.

---

🧠 **Assistant**

There are two verified ways to join SPOKE (`spoke-okn`) and ProKN (`prokn`), depending on whether you're connecting on diseases or genes. Both were verified on 2026-06-12.

**Recipe 1 — join on disease (DOID).** This is the direct, simplest join, no bridge graph needed.

- Shared identifier: **DOID** (namespace `http://purl.obolibrary.org/obo/DOID_`)
- spoke-okn side: the DOID *is* the disease node's own IRI (a `biolink:Disease` node) — join directly on it
- prokn side: the same DOID appears in object position under any predicate
- Verified overlap: **96 distinct DOID diseases** shared (out of spoke-okn's 180 disease nodes)

Verified skeleton query (run this first to confirm the key still joins, then extend with your payload):

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?doid a <https://w3id.org/biolink/vocab/Disease> .
    FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?q ?doid . }
}
```

**Recipe 2 — join on gene (HGNC → Entrez, bridged through Wikidata).** Use this if you're connecting marker genes / gene associations rather than diseases.

- Shared identifier: **HGNC on the ProKN side → Entrez on the SPOKE side**, bridged via Wikidata (`P354` HGNC → `P351` Entrez)
- prokn side: gene as an HGNC IRI (`http://identifiers.org/hgnc/{N}`), appearing under `rdf:subject` / `rdf:object` (reified INDRA statements), `rdfs:seeAlso`, `HAS_MARKER_GENE`, or `biolink:target_for` — you must include those reified predicates to capture the full set, since most of ProKN's ~38,328 HGNC ids ride on them rather than the direct relations
- spoke-okn side: gene node IRI is the Entrez id (`http://www.ncbi.nlm.nih.gov/gene/{entrez}`)
- Bridge graph: **wikidata**
- Verified overlap: **16,298 distinct spoke-okn Entrez genes** reached (of spoke-okn's 16,346 genes)

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
  BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> {
    ?item <http://www.wikidata.org/prop/direct/P351> ?entrez ;
          <http://www.wikidata.org/prop/direct/P354> ?hgnc .
  }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
}
```

Which one you want depends on the question: use the DOID join (Recipe 1) for disease-level associations — genes, compounds, prevalence, mortality for diseases both graphs describe — and the HGNC→Entrez join (Recipe 2) for gene-level work like mapping ProKN marker genes to their SPOKE network/disease/compound associations.

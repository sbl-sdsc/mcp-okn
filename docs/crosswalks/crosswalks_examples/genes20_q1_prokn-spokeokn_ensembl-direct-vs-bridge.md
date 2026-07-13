# How many genes do prokn and spoke-okn share on the Ensembl id, joined DIRECTLY with no bridge graph — and how does that compare with the wikidata-bridged HGNC→Entrez route?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>

## Conversation

👤 **User**

Crosswalk: `prokn` × `spoke-okn` on **Ensembl**, joined DIRECTLY with no bridge graph (crosswalk C16). The load-bearing detail is that prokn's Ensembl id IS the gene node's own IRI: 38,001 of prokn's 38,372 `up:Gene` nodes are `https://www.ensembl.org/id/{ENSG}` IRIs, and the full relation set (marker genes, tissue expression, reified source-attributed evidence) hangs off those nodes. spoke-okn carries the same ENSG on its gene nodes as an object of `spoke:ensembl`, but in the `http://identifiers.org/ensembl/{ENSG}` form — so a naive join on the term returns 0. Strip spoke-okn's object to the bare ENSG, rebuild prokn's node IRI, and bind it by TYPE (`a up:Gene`) rather than scanning it.

Research question: How many genes do prokn and spoke-okn share on the Ensembl id, joined DIRECTLY with no bridge graph — and how does that compare with the wikidata-bridged HGNC→Entrez route (crosswalk C9)? Which genes does each route uniquely reach?

Why the join is required: this pair was long catalogued ONLY as the wikidata-bridged route, on the mistaken premise that prokn has no Ensembl or Entrez of its own. If prokn does carry native Ensembl, the two graphs join with no third graph in the query at all — which is cheaper, has no bridge-coverage dependency, and (the open question) may reach a different slice of spoke-okn's gene layer. Settling this requires computing BOTH routes' spoke-okn gene sets and their set difference in SPARQL, not restating the catalog.

---

🧠 **Assistant**

**prokn and spoke-okn join directly on Ensembl — no bridge graph — over 16,140 distinct ENSG ids, and the wikidata route is not a superset of it.** The two routes are genuinely complementary: each reaches genes the other misses.

## The direct join (C16)

Rebuilding prokn's gene node IRI from spoke-okn's `spoke:ensembl` object and binding it as a `up:Gene` returns **16,140 distinct shared Ensembl ids** — reproducing the catalogued `verified_count` exactly. Those 16,140 ids correspond to **16,148 spoke-okn gene nodes** (a few spoke-okn genes share an ENSG). No third graph appears anywhere in the query.

## Route comparison, computed as a set difference in SPARQL

Unioning both routes' spoke-okn gene sets and grouping each gene by which route(s) reached it:

| Reached by | spoke-okn gene nodes |
| --- | --- |
| C16 direct Ensembl (no bridge) **+** C9 wikidata HGNC→Entrez bridge | **16,132** |
| C9 wikidata HGNC→Entrez bridge **only** | **166** |
| C16 direct Ensembl (no bridge) **only** | **16** |

So, derived from the returned rows:

- **C16 (direct Ensembl):** 16,132 + 16 = **16,148** spoke-okn genes
- **C9 (wikidata bridge):** 16,132 + 166 = **16,298** spoke-okn genes
- **Union of both routes:** **16,314** spoke-okn genes — confirmed by a separate count

Neither route contains the other. The wikidata bridge has the better single-route coverage (16,298 vs 16,148), but it is **not** a superset: 16 spoke-okn genes are reachable *only* without it.

## The 16 genes only the direct route reaches

| Symbol | Ensembl (prokn gene node IRI) | spoke-okn gene node (Entrez) |
| --- | --- | --- |
| C3orf85 | ENSG00000241224 | 401081 |
| **CFH** | **ENSG00000000971** | **3075** |
| CIROP | ENSG00000283654 | 100128908 |
| ERV3-1-ZNF117 | ENSG00000152926 | 109504726 |
| ERVK3-1 | ENSG00000142396 | 105372481 |
| GPR75-ASB3 | ENSG00000115239 | 100302652 |
| GUCA1A | ENSG00000048545 | 2978 |
| LOC124904942 | ENSG00000215440 | 124904942 |
| MIA2 | ENSG00000150527 | 4253 |
| NIN | ENSG00000100503 | 51199 |
| NPIPB2 | ENSG00000234719 | 729978 |
| PHOSPHO2-KLHL23 | ENSG00000213160 | 100526832 |
| TBC1D7-LOC100130357 | ENSG00000145979 | 107080638 |
| TNFAIP8L2-SCNM1 | ENSG00000163156 | 100534012 |
| UPK3B | ENSG00000243566 | 105375355 |
| ZNF664-RFLNA | ENSG00000178882 | 100533183 |

The list is diagnostic of *why* the bridge drops them. Six are **readthrough / fusion loci** (GPR75-ASB3, PHOSPHO2-KLHL23, TNFAIP8L2-SCNM1, ZNF664-RFLNA, TBC1D7-LOC100130357, ERV3-1-ZNF117), and several more are endogenous-retroviral or uncharacterized loci (ERVK3-1, NPIPB2, LOC124904942, C3orf85) — exactly the classes of locus that carry an Entrez id and an ENSG but *no* HGNC-linked Wikidata item, so the P351→P354 hop dead-ends. But the set is not only obscure loci: it also contains **CFH** (complement factor H), **GUCA1A**, **NIN**, **MIA2** and **UPK3B** — well-characterized, disease-relevant genes. For CFH the failure is precisely locatable: Wikidata's item for Entrez 3075 is `Q14911975`, and in the federation's wikidata snapshot that item carries **no `wdt:P354` (HGNC ID) statement at all**, so the bridge has nothing to hand off. The direct Ensembl join reaches it without difficulty.

## Why it answers the question

The first query settles the count: **16,140 shared Ensembl ids / 16,148 spoke-okn genes, joined with prokn and spoke-okn as the only two graphs in the query**. The bridge is therefore optional, not required — the premise that made C9 the sole catalogued route for this pair ("prokn has no Entrez/Ensembl of its own") is false.

The second query settles the comparison, and it does so by *computing* both gene sets and partitioning them, not by comparing two catalogued totals — which is the only way to distinguish "16,148 ⊂ 16,298" from genuine complementarity. The answer is complementarity: 16,132 genes are common ground, 166 are bridge-only, 16 are direct-only. Practically: **use C16 when you want a two-graph join with no bridge dependency and no wikidata coverage risk; add C9 when you want maximum recall; UNION them (16,314 genes) when completeness matters.** The union covers 16,314 of spoke-okn's 16,346 `biolink:Gene` nodes — 99.8%.

## Validation

- **Self-consistency:** query 1 returns 16,140 distinct ENSG ids, matching the crosswalk's independently recorded `verified_count` of 16,140 exactly. The route-partition query's cells (16,132 / 166 / 16) sum to per-route totals of 16,148 and 16,298 — reproducing the catalogued counts for C16 and C9 respectively — and to a union of 16,314, which the separate union query (query 4) returns independently. The same numbers derived two different ways, all agreeing.
- **Structural:** the direct route is an identity join on a registered persistent identifier (Ensembl gene ENSG). Both graphs store the same bare accession, differing only in IRI form (`https://www.ensembl.org/id/{ENSG}` as prokn's node IRI vs `http://identifiers.org/ensembl/{ENSG}` as spoke-okn's object), so the rewrite is lossless and the join is exact, not approximate.
- **Failure mode confirmed, not assumed:** the claim that the wikidata bridge *cannot* reach CFH was verified by querying wikidata directly — `?item wdt:P351 "3075"` returns `Q14911975`, with no `wdt:P354` value.

**Maintainer caveat.** The C16 catalog entry states that the union of the two routes "is spoke-okn's ENTIRE Ensembl-annotated gene set." That is close but not exact. spoke-okn has **16,346** `biolink:Gene` nodes, of which **16,324** carry a `spoke:ensembl` annotation; the two-route union is **16,314** genes, of which only **16,294** carry a `spoke:ensembl` annotation. So **30** Ensembl-annotated spoke-okn genes are reached by *neither* route (their ENSG is simply absent from prokn's gene layer), and **20** genes in the union carry no Ensembl annotation at all (they are bridge-only, reached by Entrez). The union is 99.8% of spoke-okn's gene layer, not a clean equality with its Ensembl-annotated subset.

#### Query 1 — Genes shared by prokn and spoke-okn on the Ensembl id, joined directly with no bridge graph

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
SELECT (COUNT(DISTINCT ?ens) AS ?shared_ensembl_ids) WHERE {
  { SELECT DISTINCT ?e WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?x <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e . } } }
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens a up:Gene . }
}
```

_1 row(s)_

| shared_ensembl_ids |
| --- |
| 16140 |

#### Query 2 — Every spoke-okn gene reachable in prokn, partitioned by which route reached it: the direct Ensembl join, the wikidata HGNC-Entrez bridge, or both

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?routes (COUNT(DISTINCT ?g) AS ?spoke_genes) WHERE {
  { SELECT ?g (GROUP_CONCAT(DISTINCT ?route; separator=" + ") AS ?routes) WHERE {
      { SELECT DISTINCT ?g ?route WHERE {
          { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e . }
            BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?ens)
            GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens a up:Gene . }
            BIND("C16 direct Ensembl (no bridge)" AS ?route) }
          UNION
          { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g a biolink:Gene . }
            BIND(REPLACE(STR(?g),'^.*/gene/','') AS ?entrez)
            GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item wdt:P351 ?entrez ; wdt:P354 ?hgnc . }
            BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
            GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
            BIND("C9 wikidata HGNC->Entrez bridge" AS ?route) }
        } }
    } GROUP BY ?g }
} GROUP BY ?routes ORDER BY DESC(?spoke_genes)
```

_3 row(s)_

| routes | spoke_genes |
| --- | --- |
| C16 direct Ensembl (no bridge) + C9 wikidata HGNC->Entrez bridge | 16132 |
| C9 wikidata HGNC->Entrez bridge | 166 |
| C16 direct Ensembl (no bridge) | 16 |

#### Query 3 — The 16 spoke-okn genes the direct Ensembl join reaches that the wikidata bridge cannot

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT ?symbol ?ensembl ?spoke_gene_node WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e . OPTIONAL { ?g rdfs:label ?symbol } }
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?ensembl)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ensembl a up:Gene . }
  BIND(?g AS ?spoke_gene_node)
  MINUS {
    GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g a biolink:Gene . }
    BIND(REPLACE(STR(?g),'^.*/gene/','') AS ?entrez)
    GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item wdt:P351 ?entrez ; wdt:P354 ?hgnc . }
    BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
    GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
  }
} ORDER BY ?symbol
```

_16 row(s)_

| symbol | ensembl | spoke_gene_node |
| --- | --- | --- |
| C3orf85 | https://www.ensembl.org/id/ENSG00000241224 | http://www.ncbi.nlm.nih.gov/gene/401081 |
| CFH | https://www.ensembl.org/id/ENSG00000000971 | http://www.ncbi.nlm.nih.gov/gene/3075 |
| CIROP | https://www.ensembl.org/id/ENSG00000283654 | http://www.ncbi.nlm.nih.gov/gene/100128908 |
| ERV3-1-ZNF117 | https://www.ensembl.org/id/ENSG00000152926 | http://www.ncbi.nlm.nih.gov/gene/109504726 |
| ERVK3-1 | https://www.ensembl.org/id/ENSG00000142396 | http://www.ncbi.nlm.nih.gov/gene/105372481 |
| GPR75-ASB3 | https://www.ensembl.org/id/ENSG00000115239 | http://www.ncbi.nlm.nih.gov/gene/100302652 |
| GUCA1A | https://www.ensembl.org/id/ENSG00000048545 | http://www.ncbi.nlm.nih.gov/gene/2978 |
| LOC124904942 | https://www.ensembl.org/id/ENSG00000215440 | http://www.ncbi.nlm.nih.gov/gene/124904942 |
| MIA2 | https://www.ensembl.org/id/ENSG00000150527 | http://www.ncbi.nlm.nih.gov/gene/4253 |
| NIN | https://www.ensembl.org/id/ENSG00000100503 | http://www.ncbi.nlm.nih.gov/gene/51199 |
| NPIPB2 | https://www.ensembl.org/id/ENSG00000234719 | http://www.ncbi.nlm.nih.gov/gene/729978 |
| PHOSPHO2-KLHL23 | https://www.ensembl.org/id/ENSG00000213160 | http://www.ncbi.nlm.nih.gov/gene/100526832 |
| TBC1D7-LOC100130357 | https://www.ensembl.org/id/ENSG00000145979 | http://www.ncbi.nlm.nih.gov/gene/107080638 |
| TNFAIP8L2-SCNM1 | https://www.ensembl.org/id/ENSG00000163156 | http://www.ncbi.nlm.nih.gov/gene/100534012 |
| UPK3B | https://www.ensembl.org/id/ENSG00000243566 | http://www.ncbi.nlm.nih.gov/gene/105375355 |
| ZNF664-RFLNA | https://www.ensembl.org/id/ENSG00000178882 | http://www.ncbi.nlm.nih.gov/gene/100533183 |

#### Query 4 — Union of the two routes: total spoke-okn genes reached, and how many of them carry a spoke:ensembl annotation

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT (COUNT(DISTINCT ?g) AS ?union_genes) (COUNT(DISTINCT ?ga) AS ?union_genes_with_ensembl) WHERE {
  { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e . }
    BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?ens)
    GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens a up:Gene . } }
  UNION
  { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g a biolink:Gene . }
    BIND(REPLACE(STR(?g),'^.*/gene/','') AS ?entrez)
    GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item wdt:P351 ?entrez ; wdt:P354 ?hgnc . }
    BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
    GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . } }
  OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e2 . } BIND(?g AS ?ga) }
}
```

_1 row(s)_

| union_genes | union_genes_with_ensembl |
| --- | --- |
| 16314 | 16294 |

#### Query 5 — spoke-okn's gene-layer denominators: total biolink:Gene nodes and how many carry an Ensembl annotation

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT (COUNT(DISTINCT ?g) AS ?spoke_gene_nodes) (COUNT(DISTINCT ?ga) AS ?spoke_genes_with_ensembl) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?g a biolink:Gene .
    OPTIONAL { ?g <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e . BIND(?g AS ?ga) }
  }
}
```

_1 row(s)_

| spoke_gene_nodes | spoke_genes_with_ensembl |
| --- | --- |
| 16346 | 16324 |

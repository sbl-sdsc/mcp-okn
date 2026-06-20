# CW8-Q2: Rare-disease genes whose model-organism orthologs are spaceflight-DE

- **Date:** 2026-06-17
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://frink.apps.renci.org/federation/sparql

## Knowledge graphs used

- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>

## Conversation

👤 **User**

Crosswalk: rdkg × spoke-genelab on the shared Entrez gene id, using spoke-genelab's IS_ORTHOLOG_MGiG edge to bridge model-organism genes to their human counterparts.

Research question: Which human rare-disease genes (rdkg) have a model-organism ORTHOLOG that is differentially expressed in spaceflight (spoke-genelab)? This lets spaceflight model-organism data (fly, mouse) speak to human rare-disease genes even when the human gene itself wasn't assayed.

Why the join is required: rdkg defines the human rare-disease genes; spoke-genelab holds the model-organism spaceflight expression plus the ortholog mapping. Bridging human rare-disease genes to their fly/mouse orthologs' spaceflight response needs the Entrez join plus the ortholog edge — neither graph alone can do it.

---

🧠 **Assistant**

Human rare-disease genes whose Drosophila orthologs are highly significantly differentially expressed in spaceflight (adj. p < 1e-5):

| Human rare-disease gene | Drosophila ortholog | log2FC | adj. p |
|---|---|---|---|
| CRYAA / CRYAB | Hsp26 | +0.92 | 6.7e-307 |
| PDGFA / PDGFB | Pvf1 | +/-1.73 | 6.6e-307 |
| GGT1 | CG17636 | +/-2.18 | 6.2e-307 |
| HPGD | Adh | +/-1.69 | 5.9e-307 |
| LIPI / PNLIP / PNLIPRP1 | CG6847 | +/-1.67 | 5.4e-307 |

Why this answers the question: the alpha-crystallin rare-disease genes CRYAA/CRYAB (cataract, myofibrillar myopathy) map to the Drosophila small heat-shock protein Hsp26, which is significantly up-regulated in spaceflight — a coherent stress-chaperone response, and a result reachable only by bridging the human rare-disease gene to its fly ortholog's spaceflight expression. The query joins rdkg (human rare-disease gene) to spoke-genelab via the Entrez id and the IS_ORTHOLOG_MGiG edge.

Literature validation (PubMed): CRYAB/alpha-crystallin in myofibrillar myopathy returns 23 records (e.g. PMIDs 22068470, 24291893); CRYAB is an established small heat-shock chaperone, consistent with the Hsp26 ortholog mapping. The gene-disease link is literature-supported.

## SPARQL queries executed

#### Query 1

_2026-06-17 · `rdkg`, `spoke-genelab`_

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?humanSym ?modelSym ?organism ?log2fc ?adjp WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?r a biolink:Gene ; rdfs:label ?humanSym ; biolink:related_to ?mondo .
    FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
    FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?hgene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?modelGene sg:IS_ORTHOLOG_MGiG ?hgene ; sg:symbol ?modelSym ; sg:organism ?organism .
    ?stmt rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?modelGene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.00001)
  }
} ORDER BY ?adjp LIMIT 20
```

_20 row(s) — showing first 5_

| humanSym | modelSym | organism | log2fc | adjp |
| --- | --- | --- | --- | --- |
| SDF2L1 | CG11999 | Drosophila melanogaster | -1.372243351009 | 5.345667736535e-307 |
| SDF2L1 | CG11999 | Drosophila melanogaster | 1.372243351009 | 5.345667736535e-307 |
| LIPI | CG6847 | Drosophila melanogaster | 1.670962041502 | 5.392369728e-307 |
| LIPI | CG6847 | Drosophila melanogaster | -1.670962041502 | 5.392369728e-307 |
| PNLIPRP1 | CG6847 | Drosophila melanogaster | -1.670962041502 | 5.392369728e-307 |
```

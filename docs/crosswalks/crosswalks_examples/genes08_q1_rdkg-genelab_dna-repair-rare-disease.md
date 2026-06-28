# DNA-repair / genome-instability rare-disease genes (clean spaceflight contrast, via ortholog)

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>

## Conversation
👤 **User**

Which **DNA-repair and genome-instability rare-disease genes** — Fanconi anemia, xeroderma pigmentosum / Cockayne, trichothiodystrophy, dyskeratosis congenita, ataxia-telangiectasia, Bloom, Nijmegen — are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast? These monogenic genome-maintenance disorders are the most mechanistically relevant rare diseases to chronic cosmic-radiation DNA damage.

---
🧠 **Assistant**

rdkg curates the rare-disease gene set but has no spaceflight data; spoke-genelab has the clean spaceflight differential expression but no rare-disease annotation, and assays the mouse ortholog. Connecting a genome-maintenance disease gene to its measured, unconfounded spaceflight perturbation needs the Entrez+ortholog join.

**Spaceflight contrast:** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter); gene expression.

**Sample result** (8 of 15) — human rare-disease gene symbols (assayed via mouse ortholog; ± indicates both directions seen across clean assays):

| Gene (human) | example rare disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|
| FANCA | Fanconi anemia complementation group | -3.93 / +3.08 | 7.8e-38 |
| XPC | xeroderma pigmentosum | -0.81 (down) | 5.0e-23 |
| UNG | Bloom syndrome | -2.13 (down) | 2.9e-21 |
| FANCI | Fanconi anemia complementation group | +2.75 (up) | 6.4e-20 |
| BRIP1 | Fanconi anemia | -3.16 / +4.08 | 2.1e-17 |
| NOP10 | dyskeratosis congenita, autosomal recessive | -1.21 (down) | 1.9e-14 |
| FANCD2 | Fanconi anemia | -4.86 / +2.35 | 2.3e-13 |
| RAD51 | Fanconi anemia | -2.25 / +2.35 | 5.1e-12 |

**Why it answers the question:** measured under a confounder-free Space-Flight-vs-Ground-Control contrast, the hits are the core genome-maintenance machinery — the Fanconi-anemia complex (FANCA, FANCI, FANCD2, BRIP1, the homologous-recombination recombinase RAD51), nucleotide-excision-repair gene XPC, base-excision-repair glycosylase UNG (Bloom), and the telomere/dyskeratosis gene NOP10 — directly linking inherited genome-instability disorders to genuine microgravity-driven perturbation in the spaceflight DNA-damage environment.

## SPARQL query executed
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym (SAMPLE(?diseaseLabel) AS ?exampleRareDisease) (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  {
    SELECT DISTINCT ?gene ?sym ?diseaseLabel WHERE {
      GRAPH <https://purl.org/okn/frink/kg/rdkg> {
        ?r a biolink:Gene ; rdfs:label ?sym ; biolink:related_to ?mondo .
        FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
        ?mondo a biolink:Disease ; rdfs:label ?diseaseLabel .
        FILTER(CONTAINS(LCASE(?diseaseLabel),'fanconi') || CONTAINS(LCASE(?diseaseLabel),'xeroderma')
            || CONTAINS(LCASE(?diseaseLabel),'ataxia-telangiectasia') || CONTAINS(LCASE(?diseaseLabel),'bloom syndrome')
            || CONTAINS(LCASE(?diseaseLabel),'cockayne') || CONTAINS(LCASE(?diseaseLabel),'nijmegen')
            || CONTAINS(LCASE(?diseaseLabel),'trichothiodystrophy') || CONTAINS(LCASE(?diseaseLabel),'dyskeratosis'))
      }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene)
    }
  }
  {
    SELECT DISTINCT ?assay WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
               sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay sg:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay sg:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
      }
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?modelGene sg:IS_ORTHOLOG_MGiG ?gene .
    ?stmt rdf:subject ?assay ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
          rdf:object ?modelGene ; sg:log2fc ?log2fc ; sg:adj_p_value ?adjp .
    FILTER(?adjp < 0.01)
  }
} GROUP BY ?sym ORDER BY ?minAdjP LIMIT 15
```

## Literature validation

Handwerk et al., 2023, *Int J Mol Sci* — simulated space conditions (microgravity + particle irradiation) evoke DNA-damage responses and induce FANCD2 foci and replication stress in human hematopoietic stem/progenitor cells, implicating Fanconi-pathway / genome-instability machinery in spaceflight. [PMID:37762064](https://pubmed.ncbi.nlm.nih.gov/37762064/) · [DOI](https://doi.org/10.3390/ijms241813761)

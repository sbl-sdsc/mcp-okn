# Bone Health Spaceflight-Omics Study — SPARQL Reproducibility Transcript

- **Date:** 2026-07-08 · **Model:** claude-opus-4-8
- **Endpoint:** OKN federated SPARQL (https://apps.okn.us/federation/sparql)
- **Substantive SPARQL queries logged:** 42 (merged across log scopes; a create_chat_transcript reset the log mid-run)

KG versions (get_kg_version): spoke-genelab v0.0.2 · spoke-okn v0.0.6 · rdkg v0.0.1 · digcfdekg v0.0.1 · prokn v0.0.5 · biobricks-aopwiki v0.0.4 · gene-expression-atlas-okn v0.0.3 · biohealth v0.0.4 · ubergraph v0.0.2

Rules: Space-Flight-vs-Ground direction; genotype-clean comparability (WT and Nrf2-KO); adj_p<=0.05 primary, |log2FC|>=1 effect cut; ortholog collapse max|log2FC| via IS_ORTHOLOG_MGiG; cross-KG joins on Entrez (direct) and, for GO enrichment, prokn via the Entrez->HGNC gene-symbol bridge (lower-confidence).

---

### Query 1 — 2026-07-08T07:23:42+00:00
Graphs: spoke-genelab · rows returned: 42

```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?anatomy (SAMPLE(?nm) AS ?name) (COUNT(DISTINCT ?assay) AS ?nAssays) (COUNT(DISTINCT ?study) AS ?nStudies) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?study gl:PERFORMED_SpAS ?assay .
    ?assay gl:INVESTIGATED_ASiA ?anatomy .
    OPTIONAL { ?assay schema:material_name_1 ?nm }
  }
} GROUP BY ?anatomy ORDER BY DESC(?nAssays)
```

### Query 2 — 2026-07-08T07:24:29+00:00
Graphs: spoke-genelab · rows returned: 6

```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?study ?anatomy ?fs1 ?fs2 ?mid1 ?mid2
       (GROUP_CONCAT(DISTINCT ?f1;SEPARATOR="; ") AS ?factors1)
       (GROUP_CONCAT(DISTINCT ?f2;SEPARATOR="; ") AS ?factors2)
       ?tech (COUNT(DISTINCT ?assay) AS ?nAssays)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?study gl:PERFORMED_SpAS ?assay .
    ?assay gl:INVESTIGATED_ASiA ?anatomy .
    VALUES ?anatomy { <http://purl.obolibrary.org/obo/UBERON_0001439> <http://purl.obolibrary.org/obo/UBERON_0002371> }
    OPTIONAL { ?assay schema:factor_space_1 ?fs1 }
    OPTIONAL { ?assay schema:factor_space_2 ?fs2 }
    OPTIONAL { ?assay schema:material_id_1 ?mid1 }
    OPTIONAL { ?assay schema:material_id_2 ?mid2 }
    OPTIONAL { ?assay schema:factors_1 ?f1 }
    OPTIONAL { ?assay schema:factors_2 ?f2 }
    OPTIONAL { ?assay schema:technology ?tech }
  }
} GROUP BY ?study ?anatomy ?fs1 ?fs2 ?mid1 ?mid2 ?tech
ORDER BY ?anatomy ?study ?fs1 ?fs2
```

### Query 3 — 2026-07-08T07:28:27+00:00
Graphs: spoke-genelab · rows returned: 58

```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?study ?assay
       (GROUP_CONCAT(DISTINCT ?f1;SEPARATOR=" | ") AS ?factors1)
       (GROUP_CONCAT(DISTINCT ?f2;SEPARATOR=" | ") AS ?factors2)
WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    VALUES ?study { <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-467> <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214> }
    ?study gl:PERFORMED_SpAS ?assay .
    OPTIONAL { ?assay schema:factors_1 ?f1 }
    OPTIONAL { ?assay schema:factors_2 ?f2 }
  }
} GROUP BY ?study ?assay ORDER BY ?study ?factors1 ?factors2
```

### Query 4 — 2026-07-08T07:28:53+00:00
Graphs: spoke-genelab · rows returned: 2

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?assay (COUNT(DISTINCT ?gene) AS ?measuredGenes) (COUNT(DISTINCT ?h) AS ?humanOrthologs)
WHERE {
  VALUES ?assay { <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d>
                  <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-d89cbb20c4b7855f3f955e4adbb6515d> }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene .
    OPTIONAL { ?gene gl:IS_ORTHOLOG_MGiG ?h }
  }
} GROUP BY ?assay
```

### Query 5 — 2026-07-08T07:30:23+00:00
Graphs: spoke-genelab · rows returned: 7

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?assay (COUNT(DISTINCT ?gene) AS ?sigGenes) (COUNT(DISTINCT ?h) AS ?sigOrthologs)
WHERE {
  VALUES ?assay {
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-d89cbb20c4b7855f3f955e4adbb6515d>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-467-4d3703d7504fd48caceedadb36799194>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214-0092f94d01682ca951bc130ab667111a>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214-57219cf6724867bb82d3b5c011489470>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214-035c1a8b314bbf8638d8d9f9317c3874>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214-dc387c53e41e0950118929a06eac4329>
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          schema:adj_p_value ?p .
    FILTER(?p <= 0.05)
    OPTIONAL { ?gene gl:IS_ORTHOLOG_MGiG ?h }
  }
} GROUP BY ?assay
```

### Query 6 — 2026-07-08T07:30:24+00:00
Graphs: spoke-genelab · rows returned: 30

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?symbol ?humanSymbol ?log2fc ?adj_p_value WHERE {
  { SELECT ?mgene ?log2fc ?adj_p_value WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d> ;
              rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ;
              schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
        FILTER(?adj_p_value <= 0.05 && ABS(?log2fc) >= 1) } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    OPTIONAL { ?mgene schema:symbol ?symbol }
    OPTIONAL { ?mgene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } } }
} ORDER BY DESC(ABS(?log2fc)) LIMIT 30
```

### Query 7 — 2026-07-08T07:32:40+00:00
Graphs: spoke-genelab · rows returned: 4

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?assay
  (COUNT(*) AS ?nMeasured)
  (SUM(IF(?p <= 0.05 && ABS(?lfc) >= 1, 1, 0)) AS ?n_p05_lfc1)
  (SUM(IF(?p <= 0.05 && ABS(?lfc) >= 2, 1, 0)) AS ?n_p05_lfc2)
  (SUM(IF(?p <= 0.01, 1, 0)) AS ?n_p01)
WHERE {
  VALUES ?assay {
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-d89cbb20c4b7855f3f955e4adbb6515d>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-467-4d3703d7504fd48caceedadb36799194>
    <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214-0092f94d01682ca951bc130ab667111a>
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          schema:log2fc ?lfc ; schema:adj_p_value ?p .
  }
} GROUP BY ?assay
```

### Query 8 — 2026-07-08T07:35:20+00:00
Graphs: spoke-genelab · rows returned: 5

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?symbol ?log2fc ?adj_p_value WHERE {
  VALUES ?symbol { "Tnfsf11" "Tnfrsf11b" "Tnfrsf11a" "Sost" "Ctsk" "Acp5" "Spp1" "Bglap" "Bglap2" "Runx2" "Sp7" "Alpl" "Col1a1" "Dkk1" "Lrp5" "Lrp4" "Wnt16" "Wnt10b" "Ctnnb1" "Csf1" "Nfatc1" "Mmp9" "Calcr" "Car2" "Oscar" "Dcstamp" "Sfrp1" "Sfrp4" "Ibsp" "Mepe" "Phex" "Fam20a" "Fam20c" "Cxcl2" "Nfe2l2" }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene schema:symbol ?symbol .
    ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d> ;
          rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
  }
}
```

### Query 9 — 2026-07-08T07:35:24+00:00
Graphs: spoke-genelab · rows returned: 8

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?symbol ?log2fc ?adj_p_value WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-467-4d3703d7504fd48caceedadb36799194> ;
          rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
    OPTIONAL { ?gene schema:symbol ?symbol }
  }
}
```

### Query 10 — 2026-07-08T07:36:22+00:00
Graphs: spoke-genelab · rows returned: 10

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?symbol ?log2fc ?adj_p_value WHERE {
  VALUES ?symbol { "Tnfsf11" "Tnfrsf11b" "Tnfrsf11a" "Sost" "Ctsk" "Acp5" "Spp1" "Bglap" "Bglap2" "Runx2" "Sp7" "Alpl" "Col1a1" "Dkk1" "Lrp5" "Lrp4" "Wnt16" "Wnt10b" "Ctnnb1" "Csf1" "Nfatc1" "Mmp9" "Calcr" "Car2" "Oscar" "Dcstamp" "Sfrp1" "Sfrp4" "Ibsp" "Mepe" "Phex" "Fam20a" "Fam20c" "Cxcl2" "Nfe2l2" }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?gene schema:symbol ?symbol .
    ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-d89cbb20c4b7855f3f955e4adbb6515d> ;
          rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
  }
}
```

### Query 11 — 2026-07-08T07:36:26+00:00
Graphs: spoke-genelab · rows returned: 7

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?symbol ?humanSymbol ?log2fc ?adj_p_value WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-214-0092f94d01682ca951bc130ab667111a> ;
          rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?gene ;
          schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
    OPTIONAL { ?gene schema:symbol ?symbol }
    OPTIONAL { ?gene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } }
  }
}
```

### Query 12 — 2026-07-08T07:37:20+00:00
Graphs: spoke-genelab · rows returned: 256

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mEntrez ?symbol ?hEntrez ?humanSymbol ?log2fc ?adj_p_value WHERE {
  { SELECT ?mgene ?log2fc ?adj_p_value WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d> ;
              rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ;
              schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
        FILTER(?adj_p_value <= 0.05 && ABS(?log2fc) >= 1) } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    OPTIONAL { ?mgene schema:symbol ?symbol }
    OPTIONAL { ?mgene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } BIND(REPLACE(STR(?h),'^.*/gene/','') AS ?hEntrez) } }
  BIND(REPLACE(STR(?mgene),'^.*/gene/','') AS ?mEntrez)
}
```

### Query 13 — 2026-07-08T07:38:47+00:00
Graphs: spoke-genelab · rows returned: 322

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mEntrez ?symbol ?hEntrez ?humanSymbol ?log2fc ?adj_p_value WHERE {
  { SELECT ?mgene ?log2fc ?adj_p_value WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-d89cbb20c4b7855f3f955e4adbb6515d> ;
              rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ;
              schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
        FILTER(?adj_p_value <= 0.05 && ABS(?log2fc) >= 1) } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    OPTIONAL { ?mgene schema:symbol ?symbol }
    OPTIONAL { ?mgene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } BIND(REPLACE(STR(?h),'^.*/gene/','') AS ?hEntrez) } }
  BIND(REPLACE(STR(?mgene),'^.*/gene/','') AS ?mEntrez)
}
```

### Query 14 — 2026-07-08T07:40:08+00:00
Graphs: spoke-genelab · rows returned: 3465

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mEntrez ?symbol ?hEntrez ?humanSymbol ?log2fc ?adj_p_value WHERE {
  { SELECT ?mgene ?log2fc ?adj_p_value WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-f82a89dc82f2903149d2d11cbd6a130d> ;
              rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ;
              schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
        FILTER(?adj_p_value <= 0.05) } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    OPTIONAL { ?mgene schema:symbol ?symbol }
    OPTIONAL { ?mgene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } BIND(REPLACE(STR(?h),'^.*/gene/','') AS ?hEntrez) } }
  BIND(REPLACE(STR(?mgene),'^.*/gene/','') AS ?mEntrez)
}
```

### Query 15 — 2026-07-08T07:40:24+00:00
Graphs: spoke-genelab · rows returned: 3782

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mEntrez ?symbol ?hEntrez ?humanSymbol ?log2fc ?adj_p_value WHERE {
  { SELECT ?mgene ?log2fc ?adj_p_value WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject <https://purl.org/okn/frink/kg/spoke-genelab/node/OSD-690-d89cbb20c4b7855f3f955e4adbb6515d> ;
              rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ;
              schema:log2fc ?log2fc ; schema:adj_p_value ?adj_p_value .
        FILTER(?adj_p_value <= 0.05) } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    OPTIONAL { ?mgene schema:symbol ?symbol }
    OPTIONAL { ?mgene gl:IS_ORTHOLOG_MGiG ?h . OPTIONAL { ?h schema:symbol ?humanSymbol } BIND(REPLACE(STR(?h),'^.*/gene/','') AS ?hEntrez) } }
  BIND(REPLACE(STR(?mgene),'^.*/gene/','') AS ?mEntrez)
}
```

### Query 16 — 2026-07-08T07:43:04+00:00
Graphs: spoke-genelab · rows returned: 34

```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?anatomy (SAMPLE(?nm) AS ?name) (COUNT(DISTINCT ?assay) AS ?nSFGC) (COUNT(DISTINCT ?study) AS ?nStudies) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?study gl:PERFORMED_SpAS ?assay .
    ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
           schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ; gl:INVESTIGATED_ASiA ?anatomy .
    FILTER(?m1=?m2)
    OPTIONAL { ?assay schema:material_name_1 ?nm }
  }
} GROUP BY ?anatomy ORDER BY DESC(?nSFGC)
```

### Query 17 — 2026-07-08T07:44:39+00:00
Graphs: spoke-genelab · rows returned: 50767

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT ?mEntrez (COUNT(DISTINCT ?assay) AS ?nOther) (COUNT(DISTINCT ?anatomy) AS ?nTissues) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
           schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ; gl:INVESTIGATED_ASiA ?anatomy .
    FILTER(?m1=?m2 && ?anatomy != <http://purl.obolibrary.org/obo/UBERON_0002371>)
    ?stmt rdf:subject ?assay ; rdf:predicate gl:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:object ?mgene ; schema:adj_p_value ?p .
    FILTER(?p <= 0.05)
    BIND(REPLACE(STR(?mgene),'^.*/gene/','') AS ?mEntrez)
  }
} GROUP BY ?mEntrez
```

### Query 18 — 2026-07-08T07:45:06+00:00
Graphs: spoke-genelab · rows returned: 1

```sparql
PREFIX gl: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
SELECT (COUNT(DISTINCT ?assay) AS ?nComparatorAssays) (COUNT(DISTINCT ?anatomy) AS ?nComparatorTissues) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
           schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ; gl:INVESTIGATED_ASiA ?anatomy .
    FILTER(?m1=?m2 && ?anatomy != <http://purl.obolibrary.org/obo/UBERON_0002371>)
  }
}
```

### Query 19 — 2026-07-08T07:47:19+00:00
Graphs: spoke-okn · rows returned: 90

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?dlabel ?geneEntrez WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?disease rdfs:label ?dlabel .
    FILTER(REGEX(STR(?dlabel), "osteoporo|osteopen|bone mineral|bone densit|osteomalacia|osteopetro|osteogenesis imperfecta|osteonecros|osteodystroph|rickets|Paget|skeletal|osteosarcoma|osteoarthr", "i"))
    ?disease schema:ASSOCIATES_DaG ?gene .
    BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?geneEntrez)
  }
} ORDER BY ?dlabel
```

### Query 20 — 2026-07-08T07:47:53+00:00
Graphs: spoke-okn · rows returned: 1

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?dlabel (COUNT(DISTINCT ?gene) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?disease rdfs:label ?dlabel .
    FILTER(REGEX(STR(?dlabel), "osteoporo|osteopen|bone mineral|bone densit|osteomalacia|osteopetro|osteogenesis imperfecta|osteonecros|osteodystroph|rickets|Paget|osteosarcoma|osteoarthr|osteochondro|skelet|bone|chondrodys", "i"))
    ?disease schema:ASSOCIATES_DaG ?gene .
  }
} GROUP BY ?dlabel ORDER BY DESC(?nGenes)
```

### Query 21 — 2026-07-08T07:48:26+00:00
Graphs: digcfdekg · rows returned: 90

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?tlabel (COUNT(DISTINCT ?gene) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?gene schema:geneToTrait ?trait .
    ?trait rdfs:label ?tlabel .
    FILTER(REGEX(STR(?tlabel), "bone mineral|bone densit|osteoporo|osteopen|fracture|osteo|skelet|osteoblast|osteoclast|bone", "i"))
  }
} GROUP BY ?tlabel ORDER BY DESC(?nGenes)
```

### Query 22 — 2026-07-08T07:48:27+00:00
Graphs: rdkg · rows returned: 10

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?plabel (COUNT(DISTINCT ?gene) AS ?nGenes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?disease biolink:has_phenotype ?pheno .
    ?pheno rdfs:label ?plabel .
    FILTER(REGEX(STR(?plabel), "bone mineral|osteoporo|osteopen|fracture|bone densit|osteolys|bone resorption|reduced bone", "i"))
    ?disease biolink:genetic_association ?gene .
  }
} GROUP BY ?plabel ORDER BY DESC(?nGenes)
```

### Query 23 — 2026-07-08T07:49:10+00:00
Graphs: digcfdekg · rows returned: 10382

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?geneEntrez ?tlabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?gene schema:geneToTrait ?trait .
    ?trait rdfs:label ?tlabel .
    FILTER(REGEX(STR(?tlabel), "bone mineral|bone densit|osteoporo|osteopen|fracture|osteocalcin|osteoprotegerin|osteogenesis imperfecta|osteopetro|osteolys|osteonecros", "i"))
    BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?geneEntrez)
  }
}
```

### Query 24 — 2026-07-08T07:49:11+00:00
Graphs: rdkg · rows returned: 293

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?plabel ?geneEntrez WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?disease biolink:has_phenotype ?pheno .
    ?pheno rdfs:label ?plabel .
    FILTER(REGEX(STR(?plabel), "osteoporo|osteopen|fracture|reduced bone mineral|bone mineral|osteolys", "i"))
    ?disease biolink:genetic_association ?gene .
    BIND(REPLACE(STR(?gene),'^.*/ncbigene/','') AS ?geneEntrez)
  }
} ORDER BY ?plabel
```

### Query 25 — 2026-07-08T07:49:11+00:00
Graphs: digcfdekg · rows returned: 1

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT (COUNT(DISTINCT ?gene) AS ?nGenesTotal) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?gene schema:geneToTrait ?trait . }
}
```

### Query 26 — 2026-07-08T07:50:11+00:00
Graphs: rdkg · rows returned: 9

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?plabel (GROUP_CONCAT(DISTINCT ?geneEntrez;SEPARATOR=",") AS ?genes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?disease biolink:has_phenotype ?pheno .
    ?pheno rdfs:label ?plabel .
    FILTER(REGEX(STR(?plabel), "osteoporo|osteopen|fracture|reduced bone mineral|osteolys", "i"))
    ?disease biolink:genetic_association ?gene .
    BIND(REPLACE(STR(?gene),'^.*/ncbigene/','') AS ?geneEntrez)
  }
} GROUP BY ?plabel
```

### Query 27 — 2026-07-08T07:51:07+00:00
Graphs: digcfdekg · rows returned: 21710

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/digcfdekg/schema/>
SELECT DISTINCT ?geneEntrez WHERE {
  GRAPH <https://purl.org/okn/frink/kg/digcfdekg> {
    ?gene schema:geneToTrait ?trait .
    BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?geneEntrez)
  }
}
```

### Query 28 — 2026-07-08T07:53:18+00:00
Graphs: spoke-okn · rows returned: 21

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?dir ?clabel ?geneEntrez WHERE {
  VALUES ?geneIRI {
    <http://www.ncbi.nlm.nih.gov/gene/249> <http://www.ncbi.nlm.nih.gov/gene/11197> <http://www.ncbi.nlm.nih.gov/gene/8549>
    <http://www.ncbi.nlm.nih.gov/gene/5166> <http://www.ncbi.nlm.nih.gov/gene/133121> <http://www.ncbi.nlm.nih.gov/gene/8038>
    <http://www.ncbi.nlm.nih.gov/gene/6710> <http://www.ncbi.nlm.nih.gov/gene/721> <http://www.ncbi.nlm.nih.gov/gene/54716>
    <http://www.ncbi.nlm.nih.gov/gene/3488> <http://www.ncbi.nlm.nih.gov/gene/2277> <http://www.ncbi.nlm.nih.gov/gene/25925>
    <http://www.ncbi.nlm.nih.gov/gene/25975> <http://www.ncbi.nlm.nih.gov/gene/56302> <http://www.ncbi.nlm.nih.gov/gene/2920>
    <http://www.ncbi.nlm.nih.gov/gene/6347> <http://www.ncbi.nlm.nih.gov/gene/1277> <http://www.ncbi.nlm.nih.gov/gene/4772>
    <http://www.ncbi.nlm.nih.gov/gene/4041> <http://www.ncbi.nlm.nih.gov/gene/4318> <http://www.ncbi.nlm.nih.gov/gene/1435>
    <http://www.ncbi.nlm.nih.gov/gene/3381> <http://www.ncbi.nlm.nih.gov/gene/760> <http://www.ncbi.nlm.nih.gov/gene/7849>
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    { ?compound schema:UPREGULATES_CuG ?geneIRI . BIND("up" AS ?dir) }
    UNION
    { ?compound schema:DOWNREGULATES_CdG ?geneIRI . BIND("down" AS ?dir) }
    ?compound rdfs:label ?clabel .
    BIND(REPLACE(STR(?geneIRI),'^.*/gene/','') AS ?geneEntrez)
  }
}
```

### Query 29 — 2026-07-08T07:54:35+00:00
Graphs: spoke-okn · rows returned: 8

```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?form ?dlabel ?clabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?disease rdfs:label ?dlabel . FILTER(REGEX(STR(?dlabel),"osteoarthritis|rheumatoid arthritis","i"))
    { ?disease ^schema:TREATS_CtD ?compound . ?compound rdfs:label ?clabel . BIND("direct" AS ?form) }
    UNION
    { ?stmt rdf:subject ?compound ; rdf:predicate schema:TREATS_CtD ; rdf:object ?disease . ?compound rdfs:label ?clabel . BIND("reified" AS ?form) }
  }
} LIMIT 15
```

### Query 30 — 2026-07-08T17:24:27+00:00
Graphs: prokn · rows returned: 12

```sparql
SELECT ?p (COUNT(*) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?s ?p ?go . ?go a <https://research.bioinformatics.udel.edu/ProKN/rdf/GOTerm> .
  }
} GROUP BY ?p ORDER BY DESC(?n) LIMIT 12
```

### Query 31 — 2026-07-08T17:24:56+00:00
Graphs: prokn · rows returned: 50

```sparql
SELECT ?gene ?p ?o WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?gene a <http://purl.uniprot.org/core/Gene> ; ?p ?o .
  }
} LIMIT 50
```

### Query 32 — 2026-07-08T17:26:07+00:00
Graphs: prokn · rows returned: 15

```sparql
SELECT ?gene ?prot WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?gene <http://semanticscience.org/resource/SIO_010078> ?prot .
  }
} LIMIT 15
```

### Query 33 — 2026-07-08T17:26:41+00:00
Graphs: prokn · rows returned: 40

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?goLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    VALUES ?sym { "ALPL" "LRP5" "NFATC1" "COL1A1" "CXCL2" "CSF1" }
    ?gene rdfs:label ?sym ;
          <http://semanticscience.org/resource/SIO_010078> ?prot .
    ?prot <http://purl.obolibrary.org/obo/RO_0002331> ?go .
    ?go rdfs:label ?goLabel .
  }
} LIMIT 40
```

### Query 34 — 2026-07-08T17:27:41+00:00
Graphs: prokn · rows returned: 71917

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?go WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?gene rdfs:label ?sym ;
          <http://semanticscience.org/resource/SIO_010078> ?prot .
    ?prot <http://purl.obolibrary.org/obo/RO_0002331> ?go .
  }
}
```

### Query 35 — 2026-07-08T17:29:25+00:00
Graphs: prokn · rows returned: 69

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?go ?label WHERE {
  VALUES ?go { <http://purl.obolibrary.org/obo/GO_0002181> <http://purl.obolibrary.org/obo/GO_1901740> <http://purl.obolibrary.org/obo/GO_0006412> <http://purl.obolibrary.org/obo/GO_0006941> <http://purl.obolibrary.org/obo/GO_0160165> <http://purl.obolibrary.org/obo/GO_0071357> <http://purl.obolibrary.org/obo/GO_0042776> <http://purl.obolibrary.org/obo/GO_0045063> <http://purl.obolibrary.org/obo/GO_0045061> <http://purl.obolibrary.org/obo/GO_0043374> <http://purl.obolibrary.org/obo/GO_0010499> <http://purl.obolibrary.org/obo/GO_0072539> <http://purl.obolibrary.org/obo/GO_0045590> <http://purl.obolibrary.org/obo/GO_0043161> <http://purl.obolibrary.org/obo/GO_0009060> <http://purl.obolibrary.org/obo/GO_0042274> <http://purl.obolibrary.org/obo/GO_0022904> <http://purl.obolibrary.org/obo/GO_0061136> <http://purl.obolibrary.org/obo/GO_2000045> <http://purl.obolibrary.org/obo/GO_0006779> <http://purl.obolibrary.org/obo/GO_0006785> <http://purl.obolibrary.org/obo/GO_1902600> <http://purl.obolibrary.org/obo/GO_0032743> <http://purl.obolibrary.org/obo/GO_0007283> <http://purl.obolibrary.org/obo/GO_0051321> <http://purl.obolibrary.org/obo/GO_1901798> <http://purl.obolibrary.org/obo/GO_0006979> <http://purl.obolibrary.org/obo/GO_0006915> <http://purl.obolibrary.org/obo/GO_0006511> <http://purl.obolibrary.org/obo/GO_0010498> <http://purl.obolibrary.org/obo/GO_0070585> <http://purl.obolibrary.org/obo/GO_0006119> <http://purl.obolibrary.org/obo/GO_0015986> <http://purl.obolibrary.org/obo/GO_0006120> <http://purl.obolibrary.org/obo/GO_0006782> <http://purl.obolibrary.org/obo/GO_0015670> <http://purl.obolibrary.org/obo/GO_0008286> <http://purl.obolibrary.org/obo/GO_0044597> <http://purl.obolibrary.org/obo/GO_0006784> <http://purl.obolibrary.org/obo/GO_0044598> <http://purl.obolibrary.org/obo/GO_0032729> <http://purl.obolibrary.org/obo/GO_0034314> <http://purl.obolibrary.org/obo/GO_0000278> <http://purl.obolibrary.org/obo/GO_0032760> <http://purl.obolibrary.org/obo/GO_0034341> <http://purl.obolibrary.org/obo/GO_0008654> <http://purl.obolibrary.org/obo/GO_0038094> <http://purl.obolibrary.org/obo/GO_0006783> <http://purl.obolibrary.org/obo/GO_0002715> <http://purl.obolibrary.org/obo/GO_0002477> <http://purl.obolibrary.org/obo/GO_0010591> <http://purl.obolibrary.org/obo/GO_0044839> <http://purl.obolibrary.org/obo/GO_0071395> <http://purl.obolibrary.org/obo/GO_0098901> <http://purl.obolibrary.org/obo/GO_0007051> <http://purl.obolibrary.org/obo/GO_0051301> <http://purl.obolibrary.org/obo/GO_0045333> <http://purl.obolibrary.org/obo/GO_0051604> <http://purl.obolibrary.org/obo/GO_0030317> <http://purl.obolibrary.org/obo/GO_0006099> <http://purl.obolibrary.org/obo/GO_1901796> <http://purl.obolibrary.org/obo/GO_0098869> <http://purl.obolibrary.org/obo/GO_0031146> <http://purl.obolibrary.org/obo/GO_0000070> <http://purl.obolibrary.org/obo/GO_0007059> <http://purl.obolibrary.org/obo/GO_0051988> <http://purl.obolibrary.org/obo/GO_1901750> <http://purl.obolibrary.org/obo/GO_0006123> <http://purl.obolibrary.org/obo/GO_0031204> }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?go rdfs:label ?label }
}
```

### Query 36 — 2026-07-08T18:03:07+00:00
Graphs: prokn · rows returned: 25

```sparql
SELECT ?pw ?p ?o WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?pw a <http://purl.uniprot.org/core/Pathway> ; ?p ?o .
  }
} LIMIT 25
```

### Query 37 — 2026-07-08T18:03:10+00:00
Graphs: rdkg · rows returned: 60

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?dlabel ?druglabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?disease rdfs:label ?dlabel .
    FILTER(REGEX(STR(?dlabel), "osteoporo|osteopen|bone mineral|osteogenesis imperfecta|osteopetro|Paget|bone frag|hypophosphat", "i"))
    ?drug biolink:treats ?disease ; rdfs:label ?druglabel .
  }
} LIMIT 60
```

### Query 38 — 2026-07-08T18:04:06+00:00
Graphs: prokn · rows returned: 5

```sparql
SELECT DISTINCT ?p WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?s ?p ?pw .
    ?pw a <http://purl.uniprot.org/core/Pathway> .
    FILTER(CONTAINS(STR(?pw),"R-HSA"))
  }
} LIMIT 15
```

### Query 39 — 2026-07-08T18:04:09+00:00
Graphs: rdkg · rows returned: 411

```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?dlabel ?druglabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?disease rdfs:label ?dlabel .
    FILTER(REGEX(STR(?dlabel), "osteoporo|osteopen|osteogenesis|osteopetro|Paget|bone|rickets|hypophosphat|osteomalac|skeletal", "i"))
    ?drug biolink:treats ?disease ; rdfs:label ?druglabel .
  }
} ORDER BY ?dlabel ?druglabel
```

### Query 40 — 2026-07-08T18:05:17+00:00
Graphs: prokn · rows returned: 40

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?pwLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    VALUES ?sym { "ALPL" "COL1A1" "LRP5" "NFATC1" "CSF1" }
    ?gene rdfs:label ?sym ; <http://semanticscience.org/resource/SIO_010078> ?prot .
    ?prot <http://purl.obolibrary.org/obo/RO_0000056> ?pw .
    ?pw a <http://purl.uniprot.org/core/Pathway> ; rdfs:label ?pwLabel .
    FILTER(CONTAINS(STR(?pw),"R-HSA"))
  }
} LIMIT 40
```

### Query 41 — 2026-07-08T18:05:51+00:00
Graphs: prokn · rows returned: 30017

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?pw ?pwLabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?gene rdfs:label ?sym ; <http://semanticscience.org/resource/SIO_010078> ?prot .
    ?prot <http://purl.obolibrary.org/obo/RO_0000056> ?pw .
    ?pw a <http://purl.uniprot.org/core/Pathway> ; rdfs:label ?pwLabel .
    FILTER(CONTAINS(STR(?pw),"R-HSA"))
  }
}
```

### Query 42 — 2026-07-08T18:06:35+00:00
Graphs: prokn · rows returned: 40

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?sym ?clabel WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    VALUES ?sym { "ALPL" "LRP5" "NFATC1" "CSF1" "MMP9" "CXCL2" "CA2" "COL1A1" }
    ?gene rdfs:label ?sym ; <http://semanticscience.org/resource/SIO_010078> ?prot .
    ?cmpd <http://purl.uniprot.org/core/activity> ?prot ; rdfs:label ?clabel .
  }
} LIMIT 40
```

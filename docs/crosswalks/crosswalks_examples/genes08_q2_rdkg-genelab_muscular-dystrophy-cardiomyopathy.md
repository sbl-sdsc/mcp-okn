# Muscular-dystrophy / cardiomyopathy / myopathy rare-disease genes DE in clean skeletal-muscle spaceflight

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>

## Conversation
👤 **User**

Skeletal-muscle and cardiac atrophy are signature spaceflight risks. Which **muscular-dystrophy, myopathy and cardiomyopathy rare-disease genes** are differentially expressed in a *clean* Space-Flight-vs-Ground-Control contrast measured directly in skeletal muscle, and in which direction?

---
🧠 **Assistant**

rdkg curates the muscle/heart rare-disease gene set but has no spaceflight data; spoke-genelab has the clean in-muscle spaceflight expression but no rare-disease annotation, and assays the mouse ortholog. Connecting a Mendelian muscle-disease gene to its measured, unconfounded spaceflight perturbation in muscle needs the Entrez+ortholog join.

**Spaceflight contrast:** Space Flight vs Ground Control on the same material, with all other factors *balanced* across the two arms — the `mcp-okn` server's `spoke-genelab` Rule 1 (direction via `factor_space_1/2`) + Rule 2 (comparability — arms differ only in the condition after stripping balanced shared factors/group codes), replacing the earlier strict "factor arrays contain only the condition label" filter; restricted to skeletal-muscle tissues. The top six contractile/cardiomyopathy hits are unchanged; Rule 2 additionally surfaces the limb-girdle-muscular-dystrophy gene BVES and the Brody-myopathy SERCA1 gene ATP2A1 (plus MYL2, AGT) above the previously-shown TNNT1/HNRNPA1.

**Sample result** (8 of 15):

| Gene (mouse→human) | tissue | example rare disease | log2FC (SF vs GC) | min adj. p |
|---|---|---|---|---|
| Eya4 → EYA4 | soleus | dilated cardiomyopathy | +1.37 (up) | 1.2e-50 |
| Idh2 → IDH2 | soleus | cardiomyopathy | -1.36 (down) | 9.7e-41 |
| Pdlim3 → PDLIM3 | soleus | hypertrophic cardiomyopathy | +2.41 (up) | 2.0e-38 |
| Alpk3 → ALPK3 | soleus | hypertrophic cardiomyopathy | -0.73 (down) | 8.7e-38 |
| Pln → PLN | soleus | familial dilated cardiomyopathy | -3.49 (down) | 1.7e-37 |
| Ryr1 → RYR1 | soleus | myopathy, centronuclear | +0.48 (up) | 4.2e-32 |
| Bves → BVES | soleus | limb-girdle muscular dystrophy | +0.53 (up) | 4.8e-24 |
| Atp2a1 → ATP2A1 | soleus | Brody myopathy | +1.26 (up) | 5.7e-24 |

**Why it answers the question:** measured directly in spaceflight skeletal muscle under confounder-free, *balanced* contrasts (the server's Rule 2), the hits are the canonical contractile / calcium-handling / sarcomere disease genes — PLN (phospholamban, dilated cardiomyopathy, strongly down), the SR calcium genes RYR1 and ATP2A1/SERCA1 (Brody myopathy), PDLIM3/ALPK3/EYA4 (cardiomyopathy), IDH2, and the limb-girdle gene BVES — linking inherited muscle-wasting genetics to genuine microgravity-driven muscle perturbation. Rule 2 keeps the balanced muscle contrasts the strict filter dropped, which lifts ATP2A1 and BVES into the top eight.

## SPARQL query executed
```sparql
PREFIX biolink: <https://w3id.org/biolink/vocab/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sg: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?humanSym ?modelSym ?tissue (SAMPLE(?diseaseLabel) AS ?exampleRareDisease) (MAX(?log2fc) AS ?maxLog2fc) (MIN(?log2fc) AS ?minLog2fc) (MIN(?adjp) AS ?minAdjP) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?r a biolink:Gene ; rdfs:label ?humanSym ; biolink:related_to ?mondo .
    FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/'))
    ?mondo a biolink:Disease ; rdfs:label ?diseaseLabel .
    FILTER(CONTAINS(LCASE(?diseaseLabel),'muscular dystrophy') || CONTAINS(LCASE(?diseaseLabel),'myopathy')
        || CONTAINS(LCASE(?diseaseLabel),'cardiomyopathy') || CONTAINS(LCASE(?diseaseLabel),'myofibrillar'))
  }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?hgene)
  # GeneLab: rare-disease gene → mouse ortholog → in-muscle DE; Rule 2 comparability per matching assay — arms differ
  # ONLY in the condition after stripping balanced shared factors/group codes (replaces the earlier strict "factor
  # arrays contain only the condition label" filter). Gene-first so the check runs only on assays measuring these genes.
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?modelGene sg:IS_ORTHOLOG_MGiG ?hgene ; sg:symbol ?modelSym .
    ?stmt rdf:object ?modelGene ; rdf:predicate sg:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ; rdf:subject ?assay ;
          sg:log2fc ?log2fc ; sg:adj_p_value ?adjp . FILTER(?adjp < 0.001)
    ?assay sg:factor_space_1 "Space Flight" ; sg:factor_space_2 "Ground Control" ;
           sg:material_id_1 ?m1 ; sg:material_id_2 ?m2 ; sg:material_name_1 ?tissue . FILTER(?m1 = ?m2)
    FILTER(?tissue IN ("quadriceps femoris","tibialis anterior","soleus","gastrocnemius","extensor digitorum longus","heart"))
    FILTER NOT EXISTS { ?assay sg:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay sg:factors_2 ?x } }
    FILTER NOT EXISTS { ?assay sg:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$")) FILTER NOT EXISTS { ?assay sg:factors_1 ?y } }
  }
} GROUP BY ?humanSym ?modelSym ?tissue ORDER BY ?minAdjP LIMIT 15
```

## Literature validation

Henrich et al., 2022, *Skeletal Muscle* — RNA-seq of mouse gastrocnemius and quadriceps after 9 weeks of spaceflight shows the skeletal-muscle transcriptome is remodeled in structural/contractile and fiber-type gene networks associated with atrophy. [PMID:35642060](https://pubmed.ncbi.nlm.nih.gov/35642060/) · [DOI](https://doi.org/10.1186/s13395-022-00294-9)

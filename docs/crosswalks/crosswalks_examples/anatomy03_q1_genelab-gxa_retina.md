# Retina / SANS: spaceflight DE genes vs named terrestrial retinal-disease contrasts

- **Date:** 2026-06-27
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>

## Conversation
👤 **User**

SANS makes the eye a priority organ. For genes DE in the retina under a *clean* Space-Flight-vs-Ground-Control contrast, how does each gene move in EBI Expression Atlas's terrestrial retinal **disease/injury** models — and, crucially, **in which named GXA contrast** (so the terrestrial log2fc is interpretable, not a bare number)?

---
🧠 **Assistant**

GeneLab holds the confounder-free spaceflight retinal log2fc but no terrestrial/disease data; GXA holds terrestrial retinal differential expression but only as a named *test-vs-reference* contrast, with no spaceflight data. Each row pairs the GeneLab spaceflight log2fc with the GXA log2fc **and the named GXA contrast that produced it** for the same gene — reporting, per gene, its most-significant retina contrast.

**Spaceflight contrast (GeneLab side):** Space Flight vs Ground Control, same material, all other factors identical (factor_space_1/2 + factors_1/2 + material_id filter). **GXA side:** the named disease/injury contrast shown per row (e.g. *Nrl*-null photoreceptor degeneration, retinal ischemia–reperfusion injury, optic-nerve transection).

**Sample result** (8 of 15) — each row pairs the GeneLab spaceflight value with the GXA value **and its named contrast**:

| Gene | GeneLab log2FC (SF vs GC, retina) | GeneLab adj. p | GXA contrast (test vs reference) | GXA log2FC | GXA adj. p |
|---|---|---|---|---|---|
| Drd4 | +0.80 (up) | 3.2e-58 | *Nrl*-null vs wild type (60 d) — photoreceptor degeneration | -1.3 | 3.9e-8 |
| Pdzph1 | -0.84 (down) | 4.8e-22 | *Nrl*−/− vs wild type — photoreceptor degeneration | -3.6 | 1.3e-40 |
| Sag | -0.64 (down) | 6.9e-21 | *Nrl*-null vs wild type (10 d) — photoreceptor degeneration | -2.0 | 4.7e-12 |
| Irf7 | +1.42 (up) | 7.2e-19 | 5,9-endoperoxy-cholestenediol (oxysterol) vs vehicle | -1.2 | 8.3e-5 |
| Glmn | -0.68 (down) | 4.1e-14 | intraorbital nerve transection (48 h) vs none | -1.2 | 5.6e-3 |
| Vgf | -0.84 (down) | 2.2e-11 | intraorbital nerve transection (48 h) vs none | +1.6 | 6.4e-6 |
| Med13l | -0.49 (down) | 3.1e-10 | *Nrl*−/− vs wild type — photoreceptor degeneration | -1.5 | 8.7e-46 |
| Dscaml1 | -0.45 (down) | 4.8e-10 | retinal ischemia–reperfusion injury vs sham surgery (1 d) | -1.0 | 5.2e-8 |

**Why it answers the question:** each GXA log2fc is now attributed to a **named retinal contrast** — so the terrestrial number is interpretable, not bare. Spaceflight-perturbed retinal genes line up with concrete eye pathologies: the photoreceptor arrestin **Sag** and **Pdzph1** are down in both spaceflight and the *Nrl*-null photoreceptor-degeneration retina; **Vgf** rises after optic-nerve transection (an optic-nerve injury directly relevant to SANS); **Dscaml1** moves in retinal ischemia–reperfusion injury.

## SPARQL query executed
```sparql
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wobd: <http://purl.org/okn/wobd/>
PREFIX biolink: <https://w3id.org/biolink/vocab/>
SELECT ?symbol ?glLog2fc ?glAdjp ?gxaContrast ?gxaLog2fc ?gxaAdjp WHERE {
  # GeneLab: clean SF-vs-GC retina DE genes
  { SELECT ?symbol (SAMPLE(?lfc) AS ?glLog2fc) (MIN(?adjp) AS ?glAdjp) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
        ?stmt rdf:subject ?assay ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
              rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?adjp .
        ?gene schema:symbol ?symbol .
        ?assay schema:factor_space_1 "Space Flight" ; schema:factor_space_2 "Ground Control" ;
               schema:material_id_1 ?m1 ; schema:material_id_2 ?m2 ;
               schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0000966> .
        FILTER(?m1 = ?m2)
        FILTER NOT EXISTS { ?assay schema:factors_1 ?f1 . FILTER(?f1 != "Space Flight") }
        FILTER NOT EXISTS { ?assay schema:factors_2 ?f2 . FILTER(?f2 != "Ground Control") }
        FILTER(?adjp < 1.0e-3)
      } } GROUP BY ?symbol }
  # GXA: the most significant retina contrast for that gene ...
  { SELECT ?symbol (MIN(?gap) AS ?gxaAdjp) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
        ?g biolink:symbol ?symbol . ?as biolink:object ?g ; biolink:subject ?a ; wobd:adj_p_value ?gap .
        ?a biolink:has_attribute <http://purl.obolibrary.org/obo/UBERON_0000966> .
      } } GROUP BY ?symbol }
  # ... and the contrast name + log2fc of that most-significant association
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?as2 biolink:object ?g2 ; biolink:subject ?a2 ; wobd:adj_p_value ?gxaAdjp ; wobd:log2fc ?gxaLog2fc .
    ?g2 biolink:symbol ?symbol .
    ?a2 biolink:has_attribute <http://purl.obolibrary.org/obo/UBERON_0000966> ; biolink:name ?gxaContrast .
  }
} ORDER BY ?glAdjp LIMIT 15
```

## Literature validation

Kremsky et al., 2024, *Int J Mol Sci* — RNA-seq of ISS mice shows microgravity induces oxidative-stress, inflammation and apoptosis transcriptomic changes in the optic nerve and retina, central to SANS. [PMID:39596110](https://pubmed.ncbi.nlm.nih.gov/39596110/) · [DOI](https://doi.org/10.3390/ijms252212041)

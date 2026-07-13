# An AOP-Wiki chemical stressor resolved by ChEMBL id into spoke-okn's drug record: lindane's seizure AOP meets its approved-drug context

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: `biobricks-aopwiki` × `spoke-okn` on the **ChEMBL compound id** (crosswalk `CB1-chembl-aopwiki-spokeokn`, verified count 75). biobricks-aopwiki hangs a ChEMBL identity off its chemical entities: the CAS-keyed chemical node carries `skos:exactMatch` to an `https://identifiers.org/chembl.compound/{id}` node, which in turn asserts the bare id as a literal on `CHEMINF_000412` (`<http://semanticscience.org/resource/CHEMINF_000412>`). spoke-okn keys its ChemicalEntity nodes on a PubChem InChIKey IRI and carries the ChEMBL id as an `oboInOwl:hasDbXref` in the `http://identifiers.org/chembl.compound/{id}` form. Normalization: take the bare literal from AOP-Wiki and rebuild it as `IRI(CONCAT('http://identifiers.org/chembl.compound/', ?id))` — that is the exact string spoke-okn stores.

Research question: for an AOP-Wiki chemical stressor with a ChEMBL identity — lindane (γ-hexachlorocyclohexane), CHEMBL15891 — what bioactivity and drug context does spoke-okn attach to the same compound, and does that context line up with the adverse outcome pathway AOP-Wiki files it under?

Why the join is required: AOP-Wiki knows *why a chemical is toxic* — the molecular initiating event it triggers, the causal chain of key events, and the adverse outcome at the end of it — but it holds no pharmacology whatsoever: no clinical phase, no indication, no contraindication. spoke-okn knows *the compound as a drug* — its maximum clinical phase, the diseases it treats, the diseases it is contraindicated for, all sourced from ChEMBL — but it carries no adverse outcome pathway and no mechanistic toxicology narrative. Neither graph can state the pairing that matters here — that a molecule filed as a *stressor* for epileptic seizures is simultaneously a *phase-4 approved drug*. The ChEMBL id is the only thing the two graphs share on this compound.

---

🧠 **Assistant**

The ChEMBL id joins cleanly, and the two graphs turn out to be describing the same molecule from opposite ends. AOP-Wiki files lindane as a chemical stressor of an adverse outcome pathway that ends in seizures; spoke-okn files the identical compound as a **phase-4 approved drug**.

| ChEMBL id | biobricks-aopwiki (stressor → AOP / MIE → adverse outcome) | spoke-okn (compound / max clinical phase) |
| --- | --- | --- |
| CHEMBL15891 | **Lindane** → AOP 10 *Binding to the picrotoxin site of ionotropic GABA receptors leading to epileptic seizures in adult brain*; MIE **Binding at picrotoxin site, iGABAR chloride channel**; adverse outcome **Occurrence, Epileptic seizure** | **Hexachlorocyclohexane** — `max_phase` **4.0** (approved) |

And the drug context spoke-okn attaches to that same ChEMBL id:

| ChEMBL id | spoke-okn relation | Disease | Disease id | Activity source |
| --- | --- | --- | --- | --- |
| CHEMBL15891 | TREATS_CtD | scabies | DOID_8295 | CHEMBL |
| CHEMBL15891 | CONTRAINDICATES_CcD | atopic dermatitis | DOID_3310 | CHEMBL |
| CHEMBL15891 | CONTRAINDICATES_CcD | psoriasis | DOID_8893 | CHEMBL |

**Why it answers the question.** The join produces a fact neither graph states on its own: the molecule AOP-Wiki catalogues as the stressor of a *seizure* pathway is the very molecule spoke-okn catalogues as an approved (max_phase 4) topical antiparasitic for **scabies**, contraindicated in **atopic dermatitis** and **psoriasis**. Read together, the two halves are mechanistically coherent rather than merely coincidental: AOP-Wiki supplies the mechanism — lindane binds the picrotoxin site of the ionotropic GABA-A receptor chloride channel (the MIE), which blocks inhibitory chloride flux and ends in the adverse outcome *Occurrence, Epileptic seizure*; spoke-okn supplies the exposure route — a lotion applied to the skin. The contraindications are the two graphs shaking hands: atopic dermatitis and psoriasis are exactly the conditions in which the skin barrier is compromised and percutaneous absorption rises, which is what converts a topical scabicide into a systemic dose at the GABA-A receptor. AOP-Wiki cannot tell you lindane is a licensed drug or that it is contraindicated in eczema; spoke-okn cannot tell you *why* those contraindications exist. The ChEMBL id is what lets the AOP explain the label.

One structural note for a maintainer: spoke-okn's compound node is keyed on the stereochemistry-free InChIKey (`JLYXXMFPNIAWKQ-UHFFFAOYSA-N`, label *Hexachlorocyclohexane*), so it collapses the HCH isomers — its `synonyms` list carries `lindane`, `gamma-HCH`, `Kwell`, DrugBank `DB00431` and `CHEMBL15891` together with the α/β/δ isomers. The AOP-Wiki side is specifically γ-HCH (CAS 58-89-9). The ChEMBL id CHEMBL15891 is what disambiguates: it is lindane's, and it is stored on both sides.

#### Query 1 — Lindane (CHEMBL15891): AOP-Wiki's stressor → AOP → molecular initiating event → adverse outcome, joined to spoke-okn's compound and its maximum clinical phase on the ChEMBL id

```sparql
PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?id ?stressorName ?aop ?aopTitle ?mieTitle ?adverseOutcome ?spokeLabel ?maxPhase WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?cas skos:exactMatch ?chembl ; dc:title ?stressorName .
    ?chembl <http://semanticscience.org/resource/CHEMINF_000412> ?lit .
    ?stressor aop:has_chemical_entity ?cas .
    ?aop <http://purl.obolibrary.org/obo/NCIT_C54571> ?stressor ;
         dc:title ?aopTitle ;
         aop:has_molecular_initiating_event ?mie ;
         aop:has_adverse_outcome ?ao .
    ?mie dc:title ?mieTitle .
    ?ao dc:title ?adverseOutcome .
    FILTER(STR(?lit) = "CHEMBL15891")
    BIND(STR(?lit) AS ?id)
    BIND(IRI(CONCAT('http://identifiers.org/chembl.compound/', ?id)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x ;
         rdfs:label ?spokeLabel ;
         sp:max_phase ?maxPhase .
  }
}
```

_1 row(s)_

| id | stressorName | aop | aopTitle | mieTitle | adverseOutcome | spokeLabel | maxPhase |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHEMBL15891 | Lindane | https://identifiers.org/aop/10 | Binding to the picrotoxin site of ionotropic GABA receptors leading to epileptic seizures in adult brain | Binding at picrotoxin site, iGABAR chloride channel | Occurrence, Epileptic seizure | Hexachlorocyclohexane | 4 |

#### Query 2 — The drug context spoke-okn attaches to the same ChEMBL id: diseases treated and contraindicated, with the ChEMBL activity source

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sp: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
SELECT ?id ?stressorName ?relation ?disease ?diseaseId ?actSource WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?cas skos:exactMatch ?chembl ; dc:title ?stressorName .
    ?chembl <http://semanticscience.org/resource/CHEMINF_000412> ?lit .
    FILTER(STR(?lit) = "CHEMBL15891")
    BIND(STR(?lit) AS ?id)
    BIND(IRI(CONCAT('http://identifiers.org/chembl.compound/', ?id)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x ; ?p ?d .
    FILTER(?p IN (sp:TREATS_CtD, sp:CONTRAINDICATES_CcD))
    ?d rdfs:label ?disease .
    BIND(REPLACE(STR(?p), "^.*schema/", "") AS ?relation)
    BIND(REPLACE(STR(?d), "^.*obo/", "") AS ?diseaseId)
    OPTIONAL { ?st rdf:subject ?cmp ; rdf:predicate ?p ; rdf:object ?d ; sp:act_sources ?actSource }
  }
}
```

_3 row(s)_

| id | stressorName | relation | disease | diseaseId | actSource |
| --- | --- | --- | --- | --- | --- |
| CHEMBL15891 | Lindane | CONTRAINDICATES_CcD | psoriasis | DOID_8893 | CHEMBL |
| CHEMBL15891 | Lindane | TREATS_CtD | scabies | DOID_8295 | CHEMBL |
| CHEMBL15891 | Lindane | CONTRAINDICATES_CcD | atopic dermatitis | DOID_3310 | CHEMBL |

## Literature validation

Both halves of the pairing are literature-supported. According to PubMed, Fishman & Gianutsos (*Arch Toxicol* 1987) showed that γ-hexachlorocyclohexane inhibits ³H-TBOB binding at the GABA-A receptor-linked chloride channel with an IC₅₀ of 4.6 μM — more potently than picrotoxin itself (9.4 μM) — and modulates picrotoxin- and pentylenetetrazol-induced seizure activity, which is precisely AOP 10's molecular initiating event and adverse outcome ([DOI](https://doi.org/10.1007/BF00316204)). On the drug side, Sudakin (*Arch Environ Occup Health* 2007) describes lindane lotion as "approved by the US Food and Drug Administration for treatment of scabies and lice" and reports a fatality with seizures after a single dermal application, noting the 2003 FDA public health advisory ([DOI](https://doi.org/10.3200/AEOH.62.4.201-203)). Solomon et al. (*J Fam Pract* 1995) report a new-onset generalized seizure two hours after a single topical lindane application for scabies, attributing it in part to percutaneous absorption factors — the barrier-integrity mechanism behind the dermatitis/psoriasis contraindications spoke-okn records. **Validated.**

The identifier join itself is validated by construction, on the ChEMBL compound-id standard plus the hand-verified crosswalk `CB1-chembl-aopwiki-spokeokn` (75 shared ids, verified 2026-07-12): biobricks-aopwiki asserts the literal `CHEMBL15891` on `CHEMINF_000412` and spoke-okn independently asserts `http://identifiers.org/chembl.compound/CHEMBL15891` on `oboInOwl:hasDbXref`, so both provably denote the same ChEMBL compound.

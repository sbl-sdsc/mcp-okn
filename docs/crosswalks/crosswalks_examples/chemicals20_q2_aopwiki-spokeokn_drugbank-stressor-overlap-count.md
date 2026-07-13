# How many AOP-Wiki chemical stressors carry a DrugBank id present in spoke-okn?

- **Date:** 2026-07-13
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>

## Conversation

👤 **User**

Crosswalk: `biobricks-aopwiki` × `spoke-okn` on **DrugBank id** (crosswalk `DB1-drugbank-aopwiki-spokeokn`, verified_count 27). biobricks-aopwiki carries the DrugBank accession as a bare literal via CHEMINF_000406 (`http://semanticscience.org/resource/CHEMINF_000406`) on a dedicated chemical-identity node; spoke-okn carries the same accession on its Compound nodes as an IRI via `oboInOwl:hasDbXref` in the `http://identifiers.org/drugbank/{id}` form. Normalize by wrapping AOP-Wiki's bare literal — `IRI(CONCAT('http://identifiers.org/drugbank/', ?id))` — then match.

Research question: how many AOP-Wiki chemical stressors carry a DrugBank id that is present in spoke-okn? Size the crosswalk against its denominators — how many DrugBank ids does AOP-Wiki hold at all, how many reach a spoke-okn compound, how many of those are approved drugs (`max_phase` 4), and how many actually sit on an AOP stressor — and name them.

Why the join is required: sizing this axis is what tells a user whether the pharmacology in spoke-okn can be brought to bear on AOP-Wiki's toxicology at all. A drug's adverse-outcome mechanism (molecular initiating event → key events → adverse outcome) lives only in AOP-Wiki; its approved indications, development phase and regulated genes live only in spoke-okn. Neither graph can report its own overlap with the other — only the federated join on the shared DrugBank accession can.

---

🧠 **Assistant**

**27** AOP-Wiki DrugBank ids are present in spoke-okn — reproducing the crosswalk's verified count exactly. Set against its denominators, the axis is thin but chemically rich:

| Measure | Count |
| --- | --- |
| DrugBank ids held by biobricks-aopwiki | **210** |
| … of which present in spoke-okn (the crosswalk) | **27** |
| … of those, approved drugs in spoke-okn (`max_phase` 4) | **10** |
| … of those, attached to at least one AOP stressor in AOP-Wiki | **15** |

The 27 shared compounds, named on both sides, with spoke-okn's development phase and the number of AOPs each triggers in AOP-Wiki:

| DrugBank | Compound (spoke-okn) | max_phase | AOPs |
| --- | --- | --- | --- |
| DB14085 | Cadmium | — | 4 |
| DB07392 | Atrazine | — | 3 |
| DB06973 | Bisphenol A | — | 3 |
| DB11496 | 2-Mercaptobenzothiazole | — | 2 |
| DB00898 | Ethanol | 4 | 2 |
| DB12510 | Ozone | 3 | 2 |
| DB03138 | Perchlorate | — | 2 |
| DB04528 | 2,4-Dinitrophenol | 2 | 1 |
| DB02736 | Acetamide | — | 1 |
| DB13716 | Dibutyl Phthalate | — | 1 |
| DB00431 | Hexachlorocyclohexane | 4 | 1 |
| DB09526 | Hydroquinone | 4 | 1 |
| DB14049 | Nitrate | — | 1 |
| DB09350 | Piperonyl butoxide | 4 | 1 |
| DB13245 | Thiram | — | 1 |
| DB01370 | Aluminum | — | 0 |
| DB15056 | Bifenthrin | — | 0 |
| DB11387 | Chloroform | 4 | 0 |
| DB11136 | Chromium | — | 0 |
| DB13828 | Cyfluthrin | — | 0 |
| DB03843 | Formaldehyde | 4 | 0 |
| DB04930 | Permethrin | 4 | 0 |
| DB11085 | Resorcinol | 4 | 0 |
| DB12965 | Silver | — | 0 |
| DB00730 | Thiabendazole | 4 | 0 |
| DB04827 | Urethane | 4 | 0 |
| DB01593 | Zinc | — | 0 |

**Why it answers the question.** The count is the join. AOP-Wiki holds 210 DrugBank accessions across its chemical-identity nodes; wrapping each bare literal into spoke-okn's `http://identifiers.org/drugbank/{id}` xref IRI and matching against spoke-okn's Compound nodes returns **27** — a 12.9% hit rate, and an exact reproduction of the hand-verified crosswalk count. The two further cuts are what make the number actionable rather than merely descriptive. **10 of the 27 are approved drugs** in spoke-okn (`max_phase` 4: Ethanol, Hexachlorocyclohexane, Hydroquinone, Piperonyl butoxide, Chloroform, Formaldehyde, Permethrin, Resorcinol, Thiabendazole, Urethane) — i.e. molecules that a clinician prescribes and a toxicologist also files as an environmental stressor. **15 of the 27 are attached to at least one AOP stressor**, led by Cadmium (4 AOPs), Atrazine and Bisphenol A (3 each) — these are the compounds for which the crosswalk actually delivers a mechanism, and they are overwhelmingly the *environmental* end of the DrugBank catalogue (metals, pesticides, plasticizers), not the therapeutic end. The two cuts overlap in only **4** compounds (Ethanol, Hexachlorocyclohexane, Hydroquinone, Piperonyl butoxide), which is the effective size of the approved-drug-with-a-mechanism question. Neither graph could produce any of these numbers alone: AOP-Wiki has no notion of approval phase, and spoke-okn has no notion of an adverse outcome pathway.

**Maintainer caveat.** Twelve of the 27 shared compounds trigger **zero** AOPs — including six approved drugs (Chloroform, Formaldehyde, Permethrin, Resorcinol, Thiabendazole, Urethane). These carry a DrugBank id in AOP-Wiki's *chemical* table without being wired to an AOP stressor node: AOP-Wiki catalogues chemicals independently of whether any AOP cites them as a stressor. So `verified_count = 27` measures **identifier overlap**, not mechanism coverage; the mechanism-bearing subset is 15, and the approved-and-mechanism-bearing subset is 4. Also note this axis is the thinnest of the three chemical routes into spoke-okn from AOP-Wiki (PubChem CID: 87; ChEMBL: 75; DrugBank: 27) — DrugBank is the right key only when the question is specifically about *drugs*.

## Literature validation

**Validated by construction**, and no literature claim is made. This is a pure identifier-overlap count: the DrugBank accession (`DB\d{5}`) is a registered, exact-string primary key, and the only transformation applied is the IRI wrap that reconciles AOP-Wiki's bare-literal form with spoke-okn's `identifiers.org` xref IRI form. Both graphs independently assert the same accession for the same molecule — no fuzzy, name-based or structure-based matching is involved, so the count is exact rather than estimated. The result (27) reproduces the hand-verified crosswalk `DB1-drugbank-aopwiki-spokeokn` (`verified_count` 27, `skeleton_verified: true`) exactly, and the 27 compound names returned from spoke-okn (Cadmium, Atrazine, Bisphenol A, Ethanol, …) are chemically coherent with AOP-Wiki's stressor catalogue, which is an independent sanity check on the identifier mapping. **Validated** (shared DrugBank id standard; count executed live and matching the hand-verified crosswalk).

#### Query 1 — Sizing the DrugBank axis: AOP-Wiki's total DrugBank ids, how many reach a spoke-okn compound, how many of those are approved (max_phase 4), and how many sit on an AOP stressor

```sparql
SELECT ?aopwiki_drugbank_ids ?shared_with_spokeokn ?shared_approved_max_phase4 ?shared_on_an_aop_stressor WHERE {
  { SELECT (COUNT(DISTINCT ?id) AS ?aopwiki_drugbank_ids) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?chem <http://semanticscience.org/resource/CHEMINF_000406> ?lit .
        BIND(STR(?lit) AS ?id) } } }
  { SELECT (COUNT(DISTINCT ?id) AS ?shared_with_spokeokn) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?chem <http://semanticscience.org/resource/CHEMINF_000406> ?lit .
        BIND(STR(?lit) AS ?id)
        BIND(IRI(CONCAT('http://identifiers.org/drugbank/', ?id)) AS ?x) }
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . } } }
  { SELECT (COUNT(DISTINCT ?id) AS ?shared_approved_max_phase4) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?chem <http://semanticscience.org/resource/CHEMINF_000406> ?lit .
        BIND(STR(?lit) AS ?id)
        BIND(IRI(CONCAT('http://identifiers.org/drugbank/', ?id)) AS ?x) }
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x ;
             <https://purl.org/okn/frink/kg/spoke-okn/schema/max_phase> ?mp .
        FILTER(?mp >= 4) } } }
  { SELECT (COUNT(DISTINCT ?id) AS ?shared_on_an_aop_stressor) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?chem <http://semanticscience.org/resource/CHEMINF_000406> ?lit .
        BIND(STR(?lit) AS ?id)
        BIND(IRI(CONCAT('http://identifiers.org/drugbank/', ?id)) AS ?x)
        ?cas <http://www.w3.org/2004/02/skos/core#exactMatch> ?chem .
        ?st  <http://aopkb.org/aop_ontology#has_chemical_entity> ?cas .
        ?aop <http://purl.obolibrary.org/obo/NCIT_C54571> ?st . }
      GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
        ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . } } }
}
```

_1 row(s)_

| aopwiki_drugbank_ids | shared_with_spokeokn | shared_approved_max_phase4 | shared_on_an_aop_stressor |
| --- | --- | --- | --- |
| 210 | 27 | 10 | 15 |

#### Query 2 — The 27 shared compounds named, with spoke-okn's development phase and the number of AOPs each triggers in AOP-Wiki

```sparql
SELECT ?id ?name ?max_phase (COUNT(DISTINCT ?aop) AS ?nAOPs) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000406> ?lit .
    BIND(STR(?lit) AS ?id)
    BIND(IRI(CONCAT('http://identifiers.org/drugbank/', ?id)) AS ?x)
    OPTIONAL {
      ?cas <http://www.w3.org/2004/02/skos/core#exactMatch> ?chem .
      ?st  <http://aopkb.org/aop_ontology#has_chemical_entity> ?cas .
      ?aop <http://purl.obolibrary.org/obo/NCIT_C54571> ?st .
    }
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x ;
         <http://www.w3.org/2000/01/rdf-schema#label> ?name .
    OPTIONAL { ?cmp <https://purl.org/okn/frink/kg/spoke-okn/schema/max_phase> ?max_phase }
  }
} GROUP BY ?id ?name ?max_phase ORDER BY DESC(?nAOPs) ?name
```

_27 row(s)_

| id | name | max_phase | nAOPs |
| --- | --- | --- | --- |
| DB14085 | Cadmium |  | 4 |
| DB07392 | Atrazine |  | 3 |
| DB06973 | Bisphenol A |  | 3 |
| DB11496 | 2-Mercaptobenzothiazole |  | 2 |
| DB00898 | Ethanol | 4 | 2 |
| DB12510 | Ozone | 3 | 2 |
| DB03138 | Perchlorate |  | 2 |
| DB04528 | 2,4-Dinitrophenol | 2 | 1 |
| DB02736 | Acetamide |  | 1 |
| DB13716 | Dibutyl Phthalate |  | 1 |
| DB00431 | Hexachlorocyclohexane | 4 | 1 |
| DB09526 | Hydroquinone | 4 | 1 |
| DB14049 | Nitrate |  | 1 |
| DB09350 | Piperonyl butoxide | 4 | 1 |
| DB13245 | Thiram |  | 1 |
| DB01370 | Aluminum |  | 0 |
| DB15056 | Bifenthrin |  | 0 |
| DB11387 | Chloroform | 4 | 0 |
| DB11136 | Chromium |  | 0 |
| DB13828 | Cyfluthrin |  | 0 |
| DB03843 | Formaldehyde | 4 | 0 |
| DB04930 | Permethrin | 4 | 0 |
| DB11085 | Resorcinol | 4 | 0 |
| DB12965 | Silver |  | 0 |
| DB00730 | Thiabendazole | 4 | 0 |
| DB04827 | Urethane | 4 | 0 |
| DB01593 | Zinc |  | 0 |

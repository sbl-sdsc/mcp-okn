# OKN / Proto-OKN Crosswalk Reference — Join Keys & SPARQL Skeletons

- **Date:** 2026-07-12
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

> **GENERATED FILE — do not edit by hand.** Rebuilt from the crosswalk table (`metadata/crosswalks.json`) by `scripts/build_skeleton_reference.py`; a test fails if it drifts. Edit the table (and its `skeleton_query`), then regenerate.

## Knowledge graphs used

- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice>
- `biobricks-mesh` — <https://purl.org/okn/frink/kg/biobricks-mesh>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations>
- `biobricks-tox21` — <https://purl.org/okn/frink/kg/biobricks-tox21>
- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `geoconnex` — <https://purl.org/okn/frink/kg/geoconnex>
- `hydrologykg` — <https://purl.org/okn/frink/kg/hydrologykg>
- `ncipidkg` — <https://purl.org/okn/frink/kg/ncipidkg>
- `nde` — <https://purl.org/okn/frink/kg/nde>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `nikg` — <https://purl.org/okn/frink/kg/nikg>
- `wildlifekn` — <https://purl.org/okn/frink/kg/wildlifekn>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>
- `scales` — <https://purl.org/okn/frink/kg/scales>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `sockg` — <https://purl.org/okn/frink/kg/sockg>
- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>
- `ufokn` — <https://purl.org/okn/frink/kg/ufokn>
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `phaseskg` — <https://purl.org/okn/frink/kg/phaseskg>
- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `nasa-gesdisc-kg` — <https://purl.org/okn/frink/kg/nasa-gesdisc-kg>

## Conversation

👤 **User**

For each crosswalk, list the join key and the SPARQL skeleton

---

🧠 **Assistant**

The OKN federation has **161 crosswalks**, which collapse into **54 join-key families** (a domain + a shared identifier). They are grouped below by domain and key family — each entry lists every KG pair sharing that key (with its verified `COUNT(DISTINCT)`), the identifier scheme/namespace, and a runnable `COUNT(DISTINCT)` skeleton with the IRI normalization already applied (a naive join on the raw id usually returns 0 rows).

**Pairs in one family often need different SPARQL**, so where a family's members diverge, every distinct skeleton is shown and labelled with the pairs it applies to. The CAS family is the clearest case: the biobricks graphs hang the id off `edam:has_identifier`, MeSH exposes it as `meshv:registryNumber`, and SAWGraph/SOCKG store it as a bare literal that must be rebuilt into an IRI. Copy the skeleton for YOUR pair, then extend it with your payload.

Counts verified 2026-07-12. For any pair, `get_join_strategy(kg_a, kg_b)` returns the same skeleton plus the full recipe (predicates, roles, normalization); `taxon_overlap(kg_a, kg_b)` returns runnable skeletons for the NCBITaxon hub, whose overlaps are two-valued (exact id vs clade membership) and therefore not a single count.

### ANATOMY & CELL TYPE

**UMLS↔UBERON** — `https://biohealthkg.proto-okn.net/kg/node/C{cui} (biohealth; node IRI IS the UMLS CUI) ; http://purl.obolibrary.org/obo/UBERON_ (gene-expression-atlas-okn) — bridged on ubergraph oboInOwl:hasDbXref 'UMLS:{cui}'`: biohealth → ubergraph → gene-expression-atlas-okn(249), biohealth → ubergraph → spoke-genelab(35).

_biohealth → ubergraph → gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/has_attribute> ?t . FILTER(STRSTARTS(STR(?t), 'http://purl.obolibrary.org/obo/UBERON_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?t <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

_biohealth → ubergraph → spoke-genelab_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE {
      GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?s <https://purl.org/okn/frink/kg/spoke-genelab/schema/INVESTIGATED_ASiA> ?t } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?t <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**UBERON** — `http://purl.obolibrary.org/obo/UBERON_ (both KGs use the raw OBO IRI directly — DIRECT join, no bridge)`: spoke-genelab × gene-expression-atlas-okn(27).

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?s <https://purl.org/okn/frink/kg/spoke-genelab/schema/INVESTIGATED_ASiA> ?t } } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s2 <https://w3id.org/biolink/vocab/has_attribute> ?t . }
}
```

**CL** — `http://purl.obolibrary.org/obo/CL_ (both KGs use the raw Cell Ontology IRI — DIRECT join, no bridge)`: gene-expression-atlas-okn × prokn(31), spoke-genelab × gene-expression-atlas-okn(4), spoke-genelab × prokn(1), biomarkerkg × gene-expression-atlas-okn(8), biomarkerkg × prokn(3).

_gene-expression-atlas-okn × prokn_

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/has_attribute> ?t . FILTER(STRSTARTS(STR(?t), 'http://purl.obolibrary.org/obo/CL_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?t . }
}
```

_spoke-genelab × gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?s <https://purl.org/okn/frink/kg/spoke-genelab/schema/INVESTIGATED_ASiCT> ?t } } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s2 <https://w3id.org/biolink/vocab/has_attribute> ?t . }
}
```

_spoke-genelab × prokn_

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?s <https://purl.org/okn/frink/kg/spoke-genelab/schema/INVESTIGATED_ASiCT> ?t } } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?t . }
}
```

_biomarkerkg × gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?cl) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?cl . FILTER(STRSTARTS(STR(?cl),'http://purl.obolibrary.org/obo/CL_')) }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?a <https://w3id.org/biolink/vocab/has_attribute> ?cl . }
}
```

_biomarkerkg × prokn_

```sparql
SELECT (COUNT(DISTINCT ?cl) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?cl . FILTER(STRSTARTS(STR(?cl),'http://purl.obolibrary.org/obo/CL_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?st <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?cl . }
}
```

### CHEMICALS

**CAS** — `https://identifiers.org/cas/ ; http://identifiers.org/cas/`: biobricks-aopwiki × biobricks-toxcast(290), biobricks-ice × biobricks-toxcast(9,421), biobricks-tox21 × biobricks-ice(8,916), biobricks-tox21 × biobricks-toxcast(8,909), biobricks-mesh × biobricks-ice(6,924), biobricks-mesh × biobricks-toxcast(1,146), biobricks-mesh × biobricks-aopwiki(26), biobricks-mesh × sawgraph(6), biobricks-mesh × sockg(5).

_biobricks-aopwiki × biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?c2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://aopkb.org/aop_ontology#has_chemical_entity> ?cas . }
  BIND(IRI(REPLACE(STR(?cas),'https://identifiers.org/cas/','http://identifiers.org/cas/')) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t <http://edamontology.org/has_identifier> ?c2 . }
}
```

_biobricks-ice × biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?a <http://edamontology.org/has_identifier> ?cas . }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?b <http://edamontology.org/has_identifier> ?cas . }
  FILTER(STRSTARTS(STR(?cas),'http://identifiers.org/cas/'))
}
```

_biobricks-tox21 × biobricks-ice_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?b <http://edamontology.org/has_identifier> ?cas . }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> { ?cas ?p ?o . }
}
```

_biobricks-tox21 × biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?b <http://edamontology.org/has_identifier> ?cas . }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> { ?cas ?p ?o . }
}
```

_biobricks-mesh × biobricks-ice_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> {
        ?s <http://edamontology.org/has_identifier> ?ch .
        FILTER(STRSTARTS(STR(?ch),'http://identifiers.org/cas/'))
        BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m <http://id.nlm.nih.gov/mesh/vocab#registryNumber> ?cas .
  }
}
```

_biobricks-mesh × biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> {
        ?s <http://edamontology.org/has_identifier> ?ch .
        FILTER(STRSTARTS(STR(?ch),'http://identifiers.org/cas/'))
        BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m <http://id.nlm.nih.gov/mesh/vocab#registryNumber> ?cas .
  }
}
```

_biobricks-mesh × biobricks-aopwiki_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
        ?s <http://aopkb.org/aop_ontology#has_chemical_entity> ?ch .
        FILTER(STRSTARTS(STR(?ch),'https://identifiers.org/cas/'))
        BIND(REPLACE(STR(?ch),'^https?://identifiers.org/cas/','') AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m <http://id.nlm.nih.gov/mesh/vocab#registryNumber> ?cas .
  }
}
```

_biobricks-mesh × sawgraph_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?c <http://w3id.org/coso/v1/contaminoso#casNumber> ?cn .
        FILTER(REGEX(STR(?cn),'^[0-9]{5,10}$'))
        BIND(REPLACE(STR(?cn),'^([0-9]+)([0-9]{2})([0-9])$','$1-$2-$3') AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m <http://id.nlm.nih.gov/mesh/vocab#registryNumber> ?cas .
  }
}
```

_biobricks-mesh × sockg_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sockg> {
        ?c <http://w3id.org/coso/v1/contaminoso#casNumber> ?cn .
        FILTER(REGEX(STR(?cn),'^[0-9]{2,7}-[0-9]{2}-[0-9]$'))
        BIND(STR(?cn) AS ?cas)
      } } }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> {
    ?m <http://id.nlm.nih.gov/mesh/vocab#registryNumber> ?cas .
  }
}
```

**PubChem CID** — `http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID{n} (biobricks) ; http://identifiers.org/pubchem.compound/{n} (spoke-okn)`: biobricks-pubchem-annotations × spoke-okn(762), biobricks-aopwiki × biobricks-pubchem-annotations(401), biobricks-aopwiki × spoke-okn(87).

_biobricks-pubchem-annotations × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?c <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?x),'http://identifiers.org/pubchem.compound/')) }
  BIND(REPLACE(STR(?x),'^http://identifiers.org/pubchem.compound/','') AS ?cid)
  BIND(IRI(CONCAT('http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID',?cid)) AS ?b)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> { ?ann <http://www.w3.org/ns/oa#hasTarget> ?b . }
}
```

_biobricks-aopwiki × biobricks-pubchem-annotations_

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000140> ?cidLit .
    BIND(STR(?cidLit) AS ?cid)
    BIND(IRI(CONCAT('http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID', ?cid)) AS ?t)
  }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> {
    ?anno <http://www.w3.org/ns/oa#hasTarget> ?t .
  }
}
```

_biobricks-aopwiki × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000140> ?cidLit .
    BIND(STR(?cidLit) AS ?cid)
    BIND(IRI(CONCAT('http://identifiers.org/pubchem.compound/', ?cid)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
  }
}
```

**CHEBI↔CAS** — `http://purl.obolibrary.org/obo/CHEBI_ ; http://identifiers.org/cas/`: spoke-okn → ubergraph → biobricks-toxcast(496), spoke-okn → ubergraph → biobricks-ice(712), spoke-okn → ubergraph → biobricks-tox21(480).

_spoke-okn → ubergraph → biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?c2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?chebi . FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?chebi <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:')) }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t <http://edamontology.org/has_identifier> ?c2 . }
}
```

_spoke-okn → ubergraph → biobricks-ice_

```sparql
SELECT (COUNT(DISTINCT ?c2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?chebi . FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?chebi <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:')) }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?t <http://edamontology.org/has_identifier> ?c2 . }
}
```

_spoke-okn → ubergraph → biobricks-tox21_

```sparql
SELECT (COUNT(DISTINCT ?c2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?chebi . FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?chebi <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:')) }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-tox21> { ?c2 ?p ?o . }
}
```

**DrugBank** — `http://identifiers.org/drugbank/DB{n}`: rdkg × spoke-okn(43), ruralkg × rdkg(2), biobricks-aopwiki × spoke-okn(27).

_rdkg × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?db) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?db a <https://w3id.org/biolink/vocab/Drug> . FILTER(STRSTARTS(STR(?db),'http://identifiers.org/drugbank/')) }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?c <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?db . }
}
```

_ruralkg × rdkg_

```sparql
SELECT (COUNT(DISTINCT ?db) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?s <http://www.w3.org/2002/07/owl#sameAs> ?o . FILTER(CONTAINS(STR(?o),'drugbank'))
    BIND(IRI(CONCAT('http://identifiers.org/drugbank/',REPLACE(STR(?o),'^.*/(DB[0-9]+).*$','$1'))) AS ?db) }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?db a <https://w3id.org/biolink/vocab/Drug> . }
}
```

_biobricks-aopwiki × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?id) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000406> ?lit .
    BIND(STR(?lit) AS ?id)
    BIND(IRI(CONCAT('http://identifiers.org/drugbank/', ?id)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
  }
}
```

**InChIKey** — `spoke-okn ChemicalEntity node IRI .../pubchem/inchikey/{InChIKey} -> bare InChIKey <-> prokn <https://chemkg.github.io/chemrof/inchi_key_string> (InChIKey literal on ChEMBL compounds)`: spoke-okn × prokn(143).

```sparql
SELECT (COUNT(DISTINCT ?ik) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?c a <https://w3id.org/biolink/vocab/ChemicalEntity> . FILTER(CONTAINS(STR(?c),'/inchikey/'))
    BIND(REPLACE(STR(?c),'.*/inchikey/','') AS ?ik) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?p <https://chemkg.github.io/chemrof/inchi_key_string> ?ik . }
}
```

**ChEMBL** — `biobricks-aopwiki <http://semanticscience.org/resource/CHEMINF_000412> (bare ChEMBL id literal) -> http://identifiers.org/chembl.compound/{id} (spoke-okn oboInOwl:hasDbXref)`: biobricks-aopwiki × spoke-okn(75).

```sparql
SELECT (COUNT(DISTINCT ?id) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> {
    ?chem <http://semanticscience.org/resource/CHEMINF_000412> ?lit .
    BIND(STR(?lit) AS ?id)
    BIND(IRI(CONCAT('http://identifiers.org/chembl.compound/', ?id)) AS ?x)
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
  }
}
```

### DISEASE & PHENOTYPE

**MeSH_descriptor_id** — `http://id.nlm.nih.gov/mesh/{ID} (biobricks-mesh node IRI, HTTP) ; https://id.nlm.nih.gov/mesh/{ID} IRIs on spoke-okn mesh_ids / mesh_list (HTTPS)`: biobricks-mesh × spoke-okn(165), biobricks-mesh × ubergraph(9,883).

_biobricks-mesh × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?id) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s ?p ?mo .
    VALUES ?p { <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_list> <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_ids> } }
  BIND(REPLACE(STR(?mo),'^https://id.nlm.nih.gov/mesh/','') AS ?id)
  BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/',?id)) AS ?m)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> { ?m ?bp ?bo . }
}
```

_biobricks-mesh × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?m) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?t <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?curie . FILTER(STRSTARTS(STR(?curie),'MESH:')) }
  BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/',REPLACE(STR(?curie),'^MESH:',''))) AS ?m)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> { ?m ?p ?o . }
}
```

**MONDO** — `biomarkerkg obo:OBCI_1000008 / obo:OBCI_1000002 -> http://purl.obolibrary.org/obo/MONDO_{id} (891 distinct MONDO diseases)`: biomarkerkg × prokn(263), nde × oard-kg(889), oard-kg × prokn(470), rdkg × oard-kg(2,014), biomarkerkg × nde(601), biomarkerkg × rdkg(754), biomarkerkg × oard-kg(290), ubergraph × oard-kg(212).

_biomarkerkg × prokn_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?mondo . }
}
```

_nde × oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?s <http://schema.org/healthCondition> ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

_oard-kg × prokn_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?s <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?ss <https://w3id.org/biolink/vocab/subject> ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?mondo . }
}
```

_rdkg × oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?mondo ?p ?o . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

_biomarkerkg × nde_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { SELECT DISTINCT ?mondo WHERE { GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x <http://schema.org/healthCondition> ?mondo . }
}
```

_biomarkerkg × rdkg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?mondo ?q ?o . }
}
```

_biomarkerkg × oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

_ubergraph × oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?disease) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?disease <http://www.w3.org/2000/01/rdf-schema#subClassOf>* <http://purl.obolibrary.org/obo/MONDO_0004995> . }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/subject> ?disease } UNION { ?xo <https://w3id.org/biolink/vocab/object> ?disease } }
}
```

**HP** — `http://purl.obolibrary.org/obo/HP_`: oard-kg × prokn(4,941), gene-expression-atlas-okn × oard-kg(13), gene-expression-atlas-okn × prokn(12).

_oard-kg × prokn_

```sparql
SELECT (COUNT(DISTINCT ?hp) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?s <https://w3id.org/biolink/vocab/object> ?hp } UNION { ?ss <https://w3id.org/biolink/vocab/subject> ?hp } FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?hp . }
}
```

_gene-expression-atlas-okn × oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?hp) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?hp a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_')) }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?hp } UNION { ?y <https://w3id.org/biolink/vocab/subject> ?hp } }
}
```

_gene-expression-atlas-okn × prokn_

```sparql
SELECT (COUNT(DISTINCT ?hp) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?hp a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?c ?p ?hp . }
}
```

**MONDO↔DOID (bridged)** — `biomarkerkg obo:OBCI_1000008 / obo:OBCI_1000002 -> http://purl.obolibrary.org/obo/MONDO_{id} (891 distinct MONDO diseases)`: spoke-okn → ubergraph → biomarkerkg(107).

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
}
```

**DOID** — `http://purl.obolibrary.org/obo/DOID_`: spoke-okn × nde(20).

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x <http://schema.org/healthCondition> ?doid . }
}
```

**EFO↔MONDO (bridged)** — `EFO (ebi.ac.uk/efo/EFO_) + Orphanet (orpha.net/ORDO/Orphanet_) -> obo/MONDO_ (ubergraph); + direct obo/MONDO_`: gene-expression-atlas-okn → ubergraph → rdkg(414), gene-expression-atlas-okn → ubergraph → nde(325), gene-expression-atlas-okn → ubergraph → oard-kg(159).

_gene-expression-atlas-okn → ubergraph → rdkg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?mondo a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?efo a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?efo),'/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?orph a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?mondo ?pr ?o . }
}
```

_gene-expression-atlas-okn → ubergraph → nde_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?mondo a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?efo a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?efo),'/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?orph a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x <http://schema.org/healthCondition> ?mondo . }
}
```

_gene-expression-atlas-okn → ubergraph → oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?mondo a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?efo a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?efo),'/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?orph a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

**DOID↔MONDO** — `EFO (ebi.ac.uk/efo/EFO_) + Orphanet (orpha.net/ORDO/Orphanet_) -> obo/MONDO_ (ubergraph); + direct obo/MONDO_ -> obo/DOID_ (spoke-okn)`: gene-expression-atlas-okn → ubergraph → spoke-okn(54), spoke-okn → ubergraph → oard-kg(40), spoke-okn → ubergraph → prokn(115), spoke-okn → ubergraph → rdkg(149).

_gene-expression-atlas-okn → ubergraph → spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  { { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?mondo a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?efo a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?efo),'/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?orph a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . }
}
```

_spoke-okn → ubergraph → oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

_spoke-okn → ubergraph → prokn_

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d <http://www.w3.org/2004/02/skos/core#exactMatch> ?mondo . }
}
```

_spoke-okn → ubergraph → rdkg_

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?x ?q ?mondo . }
}
```

**MONDO↔OMIM (bridged)** — `http://purl.obolibrary.org/obo/MONDO_ (oard-kg) ; https://www.omim.org/entry/{id} (prokn) — bridged on OMIM:{id} via ubergraph oboInOwl:hasDbXref`: oard-kg → ubergraph → prokn(11).

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?curie . FILTER(STRSTARTS(STR(?curie),'OMIM:')) }
  BIND(IRI(CONCAT('https://www.omim.org/entry/',REPLACE(STR(?curie),'^OMIM:',''))) AS ?omim)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?y a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?omim . }
}
```

**MONDO↔Orphanet (bridged)** — `http://purl.obolibrary.org/obo/MONDO_ (oard-kg) ; http://www.orpha.net/ORDO/Orphanet_{id} (prokn up:Disease) — bridged on Orphanet:{id} via ubergraph oboInOwl:hasDbXref`: oard-kg → ubergraph → prokn(316).

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?curie . FILTER(STRSTARTS(STR(?curie),'Orphanet:')) }
  BIND(IRI(CONCAT('http://www.orpha.net/ORDO/Orphanet_',REPLACE(STR(?curie),'^Orphanet:',''))) AS ?orpha)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?y a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?orpha . }
}
```

**UMLS↔MONDO** — `https://biohealthkg.proto-okn.net/kg/node/C{cui} (biohealth; the node IRI IS the UMLS CUI) ; http://purl.obolibrary.org/obo/MONDO_ (rdkg) — bridged on ubergraph oboInOwl:hasDbXref 'UMLS:{cui}'`: biohealth → ubergraph → rdkg(9,122), biohealth → ubergraph → oard-kg(1,796), biohealth → ubergraph → nde(2,760), biohealth → ubergraph → biomarkerkg(835).

_biohealth → ubergraph → rdkg_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?mondo), 'http://purl.obolibrary.org/obo/MONDO_'))
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?mondo ?p ?o . }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

_biohealth → ubergraph → oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?mondo), 'http://purl.obolibrary.org/obo/MONDO_'))
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?z <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?z2 <https://w3id.org/biolink/vocab/subject> ?mondo } }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

_biohealth → ubergraph → nde_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?mondo WHERE {
      GRAPH <https://purl.org/okn/frink/kg/nde> { ?s <http://schema.org/healthCondition> ?mondo . FILTER(STRSTARTS(STR(?mondo), 'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

_biohealth → ubergraph → biomarkerkg_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?mondo WHERE { GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?x),'UMLS:')) BIND(STRAFTER(STR(?x),'UMLS:') AS ?cui) }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp2 ?bo . }
}
```

**UMLS↔HP** — `https://biohealthkg.proto-okn.net/kg/node/C{cui} (biohealth; the node IRI IS the UMLS CUI) ; http://purl.obolibrary.org/obo/HP_ (prokn) — bridged on ubergraph oboInOwl:hasDbXref 'UMLS:{cui}'`: biohealth → ubergraph → prokn(4,340), biohealth → ubergraph → oard-kg(4,549), biohealth → ubergraph → gene-expression-atlas-okn(13).

_biohealth → ubergraph → prokn_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?hp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?hp), 'http://purl.obolibrary.org/obo/HP_'))
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s ?p ?hp . }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

_biohealth → ubergraph → oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?hp WHERE {
      GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?z <https://w3id.org/biolink/vocab/object> ?hp } UNION { ?z2 <https://w3id.org/biolink/vocab/subject> ?hp } FILTER(STRSTARTS(STR(?hp), 'http://purl.obolibrary.org/obo/HP_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?hp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

_biohealth → ubergraph → gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?hp WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?hp a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?hp), 'http://purl.obolibrary.org/obo/HP_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?hp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
  }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**UMLS↔MONDO↔DOID (two-hop)** — `https://biohealthkg.proto-okn.net/kg/node/C{cui} (biohealth) ; http://purl.obolibrary.org/obo/DOID_ (spoke-okn biolink:Disease) — bridged through ubergraph: MONDO oboInOwl:hasDbXref 'UMLS:{cui}' AND MONDO skos:exactMatch DOID`: biohealth → ubergraph → spoke-okn(173).

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
    ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x .
    FILTER(STRSTARTS(STR(?mondo), 'http://purl.obolibrary.org/obo/MONDO_'))
    FILTER(STRSTARTS(STR(?x), 'UMLS:'))
    BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui)
    ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid .
    FILTER(STRSTARTS(STR(?doid), 'http://purl.obolibrary.org/obo/DOID_'))
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**MONDO (+ EFO/Orphanet→MONDO bridged)** — `http://purl.obolibrary.org/obo/MONDO_ ; bridged from http://www.ebi.ac.uk/efo/EFO_ and http://www.orpha.net/ORDO/Orphanet_ via ubergraph skos:exactMatch`: digcfdekg → ubergraph → rdkg(1,045), digcfdekg → ubergraph → oard-kg(402), biomarkerkg → ubergraph → digcfdekg(193).

_digcfdekg → ubergraph → rdkg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { SELECT DISTINCT ?mondo WHERE {
    { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?efo . FILTER(STRSTARTS(STR(?efo),'http://www.ebi.ac.uk/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?orph . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } } }
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?mondo ?p ?o . }
}
```

_digcfdekg → ubergraph → oard-kg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { SELECT DISTINCT ?mondo WHERE {
    { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?efo . FILTER(STRSTARTS(STR(?efo),'http://www.ebi.ac.uk/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?orph . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } } }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?a <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?b <https://w3id.org/biolink/vocab/subject> ?mondo } }
}
```

_biomarkerkg → ubergraph → digcfdekg_

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { SELECT DISTINCT ?mondo WHERE { GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?bp ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  { SELECT DISTINCT ?mondo WHERE {
    { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?efo . FILTER(STRSTARTS(STR(?efo),'http://www.ebi.ac.uk/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?orph . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } } }
}
```

**DOID↔MONDO (+ EFO/Orphanet→MONDO)** — `http://purl.obolibrary.org/obo/DOID_ (spoke-okn) <-> http://purl.obolibrary.org/obo/MONDO_ (digcfdekg, direct+bridged)`: spoke-okn → ubergraph → digcfdekg(50).

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  { SELECT DISTINCT ?mondo WHERE {
    { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?mondo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?efo . FILTER(STRSTARTS(STR(?efo),'http://www.ebi.ac.uk/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?orph . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } } }
}
```

**EFO / Orphanet / MONDO (direct, multi-vocabulary)** — `http://www.ebi.ac.uk/efo/EFO_ , http://www.orpha.net/ORDO/Orphanet_ , http://purl.obolibrary.org/obo/MONDO_`: digcfdekg × gene-expression-atlas-okn(33).

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . FILTER(STRSTARTS(STR(?t),'http://www.ebi.ac.uk/efo/EFO_') || STRSTARTS(STR(?t),'http://purl.obolibrary.org/obo/MONDO_') || CONTAINS(STR(?t),'Orphanet_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?t a <https://w3id.org/biolink/vocab/Disease> . }
}
```

**UMLS** — `biobricks-ice throughMechanisticTarget_NCIm identifiers.org/umls:...C{cui} -> C{cui} -> https://biohealthkg.proto-okn.net/kg/node/C{cui} (biohealth UMLS node-IRI)`: biobricks-ice × biohealth(46).

```sparql
SELECT (COUNT(DISTINCT ?bh) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?a <https://ice.ntp.niehs.nih.gov/property/throughMechanisticTarget_NCIm> ?u . FILTER(CONTAINS(STR(?u),'umls'))
    BIND(REPLACE(STR(?u),'^.*?(C[0-9]{6,}).*$','$1') AS ?cui) }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?p ?o . }
}
```

### EARTH OBSERVATION

**GCMD instrument** — `climatemodelskg <https://climatepub4kg.github.io/ontology#name> on a climatepub4kg:Instrument node <-> nasa-gesdisc-kg <http://www.w3.org/2000/01/rdf-schema#label> on a GCMD Instrument node (reached via nasa <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/HAS_INSTRUMENT>). Match on the case-normalized instrument name.`: climatemodelskg × nasa-gesdisc-kg(115).

```sparql
SELECT (COUNT(DISTINCT ?k) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> { ?c a <https://climatepub4kg.github.io/ontology#Instrument> ; <https://climatepub4kg.github.io/ontology#name> ?cn .
    BIND(LCASE(STR(?cn)) AS ?k) }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> { ?d <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/HAS_INSTRUMENT> ?x . ?x <http://www.w3.org/2000/01/rdf-schema#label> ?nl .
    BIND(LCASE(STR(?nl)) AS ?k) }
}
```

**GCMD platform** — `climatemodelskg <https://climatepub4kg.github.io/ontology#name> on a climatepub4kg:Platform node <-> nasa-gesdisc-kg <http://www.w3.org/2000/01/rdf-schema#label> on a GCMD Platform node (reached via nasa <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/HAS_PLATFORM>). Match on the case-normalized platform name.`: climatemodelskg × nasa-gesdisc-kg(70).

```sparql
SELECT (COUNT(DISTINCT ?k) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> { ?c a <https://climatepub4kg.github.io/ontology#Platform> ; <https://climatepub4kg.github.io/ontology#name> ?cn .
    BIND(LCASE(STR(?cn)) AS ?k) }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> { ?d <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/HAS_PLATFORM> ?x . ?x <http://www.w3.org/2000/01/rdf-schema#label> ?nl .
    BIND(LCASE(STR(?nl)) AS ?k) }
}
```

### ENVIRONMENTAL TOXICOLOGY

**CAS** — `sawgraph coso:casNumber (undashed OR dashed literal; dashes must be reconstructed) -> http://identifiers.org/cas/{cas} (biobricks-toxcast edam:has_identifier IRI)`: sawgraph × biobricks-toxcast(32), sawgraph × biobricks-ice(39), sockg × biobricks-ice(68), sockg × biobricks-toxcast(59).

_sawgraph × biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?s <http://w3id.org/coso/v1/contaminoso#casNumber> ?raw .
        BIND(IF(REGEX(STR(?raw),'^[0-9]{5,10}$'),
                REPLACE(STR(?raw),'^([0-9]+)([0-9]{2})([0-9])$','$1-$2-$3'),
                STR(?raw)) AS ?cas)
        FILTER(REGEX(?cas,'^[0-9]{2,7}-[0-9]{2}-[0-9]$'))
      } } }
  BIND(IRI(CONCAT('http://identifiers.org/cas/', ?cas)) AS ?casIri)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?t <http://edamontology.org/has_identifier> ?casIri . }
}
```

_sawgraph × biobricks-ice_

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  { SELECT DISTINCT ?cas WHERE {
      GRAPH <https://purl.org/okn/frink/kg/sawgraph> {
        ?s <http://w3id.org/coso/v1/contaminoso#casNumber> ?raw .
        BIND(IF(REGEX(STR(?raw),'^[0-9]{5,10}$'),
                REPLACE(STR(?raw),'^([0-9]+)([0-9]{2})([0-9])$','$1-$2-$3'),
                STR(?raw)) AS ?cas)
        FILTER(REGEX(?cas,'^[0-9]{2,7}-[0-9]{2}-[0-9]$'))
      } } }
  BIND(IRI(CONCAT('http://identifiers.org/cas/', ?cas)) AS ?casIri)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?d <http://edamontology.org/has_identifier> ?casIri . }
}
```

_sockg × biobricks-ice_

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sockg> { ?s <http://w3id.org/coso/v1/contaminoso#casNumber> ?cas . }
  BIND(IRI(CONCAT('http://identifiers.org/cas/', STR(?cas))) AS ?cid)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?x <http://edamontology.org/has_identifier> ?cid . }
}
```

_sockg × biobricks-toxcast_

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sockg> { ?s <http://w3id.org/coso/v1/contaminoso#casNumber> ?cas . }
  BIND(IRI(CONCAT('http://identifiers.org/cas/', STR(?cas))) AS ?cid)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?x <http://edamontology.org/has_identifier> ?cid . }
}
```

### FUNCTION & PATHWAYS

**GO** — `http://purl.obolibrary.org/obo/GO_{n} (prokn) ; pankgraph carries GO as https://www.ebi.ac.uk/QuickGO/term/GO:{n} (literal, on rdfs:seeAlso) AND http://purl.obolibrary.org/obo/GO_{n} (on biolink:functional_association)`: pankgraph × prokn(16,970).

```sparql
SELECT (COUNT(DISTINCT ?go) AS ?n) WHERE {
  { SELECT DISTINCT ?go WHERE {
      GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?s <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?lit . FILTER(STRSTARTS(STR(?lit),'https://www.ebi.ac.uk/QuickGO/term/GO:')) }
      BIND(IRI(REPLACE(STR(?lit),'^.*/term/GO:','http://purl.obolibrary.org/obo/GO_')) AS ?go)
  } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?p ?pred ?go . }
}
```

**Reactome** — `R-HSA-{n} - GXA stores it as https://reactome.org/content/detail/R-HSA-{n}; ProKN as https://identifiers.org/reactome/R-HSA-{n}. Extract the R-HSA accession and rebuild the identifiers.org form.`: gene-expression-atlas-okn × prokn(1,068).

```sparql
SELECT (COUNT(DISTINCT ?proknReact) AS ?n) WHERE {
  { SELECT DISTINCT ?proknReact WHERE {
      GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <http://purl.org/okn/wobd/enrichment_source> "GXA:Reactome" ; <https://w3id.org/biolink/vocab/object> ?gxaReact . FILTER(CONTAINS(STR(?gxaReact),'R-HSA-')) }
      BIND(IRI(CONCAT('https://identifiers.org/reactome/',REPLACE(STR(?gxaReact),'^.*/detail/',''))) AS ?proknReact)
  } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?prot <http://purl.obolibrary.org/obo/RO_0000056> ?proknReact . }
}
```

### GENES

**Ensembl** — `https://identifiers.org/ensembl/ ; http://identifiers.org/ensembl/`: biobricks-aopwiki × gene-expression-atlas-okn(1,355), biobricks-aopwiki × spoke-okn(1,385), gene-expression-atlas-okn × spoke-okn(15,132), pankgraph × spoke-okn(16,314), pankgraph × gene-expression-atlas-okn(60,581), pankgraph × prokn(37,835), prokn × spoke-okn(16,140).

_biobricks-aopwiki × gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://www.w3.org/2004/02/skos/core#exactMatch> ?e . FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ensembl/')) }
  BIND(IRI(REPLACE(STR(?e),'https://identifiers.org/ensembl/','http://identifiers.org/ensembl/')) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?gene ?p ?o . }
}
```

_biobricks-aopwiki × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://www.w3.org/2004/02/skos/core#exactMatch> ?e . FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ensembl/')) }
  BIND(IRI(REPLACE(STR(?e),'https://identifiers.org/ensembl/','http://identifiers.org/ensembl/')) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?x ?p ?gene . }
}
```

_gene-expression-atlas-okn × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  { SELECT DISTINCT ?gene WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?x <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?gene . } } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
}
```

_pankgraph × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  { SELECT DISTINCT ?gene WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?x <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?gene . } } }
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
}
```

_pankgraph × gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?ens) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/pankgraph> {
    ?pg a <https://w3id.org/biolink/vocab/Gene> .
    BIND(STRAFTER(STR(?pg), "ensembl/") AS ?ens)
    FILTER(STRSTARTS(?ens, "ENS"))
  }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> {
    ?gx <https://w3id.org/biolink/vocab/id> ?ens .
  }
}
```

_pankgraph × prokn_

```sparql
SELECT (COUNT(DISTINCT ?ens) AS ?n) WHERE {
  { SELECT DISTINCT ?lit WHERE { GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?s <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?lit . FILTER(STRSTARTS(STR(?lit),'https://www.ensembl.org/id/ENSG')) } } }
  BIND(IRI(STR(?lit)) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens ?p ?o . }
}
```

_prokn × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?ens) AS ?n) WHERE {
  { SELECT DISTINCT ?e WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?x <https://purl.org/okn/frink/kg/spoke-okn/schema/ensembl> ?e . } } }
  BIND(IRI(CONCAT('https://www.ensembl.org/id/', REPLACE(STR(?e),'^.*/',''))) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens a <http://purl.uniprot.org/core/Gene> . }
}
```

**Entrez** — `https://identifiers.org/ncbigene/ (aopwiki) ; http://identifiers.org/ncbigene/ (rdkg)`: biobricks-aopwiki × rdkg(1,193), biobricks-aopwiki × spoke-genelab(1,472), rdkg × spoke-genelab(9,034), rdkg × spoke-okn(8,475), spoke-genelab × spoke-okn(16,326), digcfdekg × spoke-okn(16,052), digcfdekg × spoke-genelab(19,747), digcfdekg × rdkg(8,934), biobricks-ice × rdkg(358).

_biobricks-aopwiki × rdkg_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://www.w3.org/2004/02/skos/core#exactMatch> ?e . FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/')) }
  BIND(IRI(REPLACE(STR(?e),'https://identifiers.org/ncbigene/','http://identifiers.org/ncbigene/')) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?gene ?p ?o . }
}
```

_biobricks-aopwiki × spoke-genelab_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://www.w3.org/2004/02/skos/core#exactMatch> ?e . FILTER(STRSTARTS(STR(?e),'https://identifiers.org/ncbigene/')) }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?e),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?gene ?p ?o . }
}
```

_rdkg × spoke-genelab_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  { SELECT DISTINCT ?gene WHERE {
      GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?r a <https://w3id.org/biolink/vocab/Gene> .
        FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/')) }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene) } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?gene ?q ?r2 . }
}
```

_rdkg × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  { SELECT DISTINCT ?gene WHERE {
      GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?r a <https://w3id.org/biolink/vocab/Gene> .
        FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/')) }
      BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?r),'^.*/ncbigene/',''))) AS ?gene) } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?gene ?q ?r2 . }
}
```

_spoke-genelab × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
}
```

_digcfdekg × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?g) AS ?n) WHERE {
  { SELECT DISTINCT ?g WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?g <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?g ?p ?o . }
}
```

_digcfdekg × spoke-genelab_

```sparql
SELECT (COUNT(DISTINCT ?g) AS ?n) WHERE {
  { SELECT DISTINCT ?g WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?g <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . } } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?g ?p ?o . }
}
```

_digcfdekg × rdkg_

```sparql
SELECT (COUNT(DISTINCT ?ng) AS ?n) WHERE {
  { SELECT DISTINCT ?g WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?g <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . } } }
  BIND(IRI(REPLACE(STR(?g),'http://www.ncbi.nlm.nih.gov/gene/','http://identifiers.org/ncbigene/')) AS ?ng)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?ng ?p ?o . }
}
```

_biobricks-ice × rdkg_

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?a <https://ice.ntp.niehs.nih.gov/property/assay_entrez_gene_id> ?g .
    BIND(REPLACE(STR(?g),'.*/gene/','') AS ?bare) FILTER(?bare != 'None') }
  BIND(IRI(CONCAT('http://identifiers.org/ncbigene/', ?bare)) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?gene ?p ?o . }
}
```

**HGNC→Entrez (bridged)** — `http://identifiers.org/hgnc/{N} (prokn) -> http://www.ncbi.nlm.nih.gov/gene/{entrez} (spoke-okn)`: prokn → wikidata → spoke-okn(16,298).

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
  BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item <http://www.wikidata.org/prop/direct/P351> ?entrez ;
                                  <http://www.wikidata.org/prop/direct/P354> ?hgnc . }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
}
```

**Entrez→HGNC (bridged)** — `http://www.ncbi.nlm.nih.gov/gene/{entrez} (digcfdekg) -> http://identifiers.org/hgnc/{n} (prokn)`: digcfdekg → wikidata → prokn(20,783).

```sparql
SELECT (COUNT(DISTINCT ?h) AS ?n) WHERE {
  { SELECT DISTINCT ?g WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?g <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . } } }
  BIND(REPLACE(STR(?g),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item <http://www.wikidata.org/prop/direct/P351> ?entrez ; <http://www.wikidata.org/prop/direct/P354> ?hgnc . }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
}
```

### GEOSPATIAL

**S2_L13** — `http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.`: fiokg × sawgraph(4,712), fiokg × spatialkg(681,045), hydrologykg × spatialkg(106,138), sawgraph × spatialkg(88,007), sockg × spatialkg(1,069), sockg × sawgraph(2), ufokn × spatialkg(97,087), ufokn × fiokg(2,461), sudokn × spatialkg(42,560).

_fiokg × sawgraph_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://www.w3.org/2002/07/owl#sameAs> ?cell . FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.')) }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s <http://www.w3.org/2002/07/owl#sameAs> ?cell . }
}
```

_fiokg × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://www.w3.org/2002/07/owl#sameAs> ?cell . FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.')) }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
}
```

_hydrologykg × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/hydrologykg> { ?h <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?cell . FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.')) }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
}
```

_sawgraph × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s <http://www.w3.org/2002/07/owl#sameAs> ?cell . FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.')) }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
}
```

_sockg × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sockg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
}
```

_sockg × sawgraph_

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sockg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?s <http://www.w3.org/2002/07/owl#sameAs> ?cell . }
}
```

_ufokn × spatialkg_ (skeleton not re-verified)

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  { SELECT DISTINCT ?cell WHERE {
    GRAPH <https://purl.org/okn/frink/kg/ufokn> {
      ?bn ?pn "s2Level13" .
      ?bn ?pv ?s2id .
      FILTER(CONTAINS(STR(?pv),'schema.org/value'))
    }
    BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.',STR(?s2id))) AS ?cell)
  } }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
}
```

_ufokn × fiokg_ (skeleton not re-verified)

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?sampleCells) (COUNT(DISTINCT ?shared) AS ?inFiokg) WHERE {
  { SELECT ?cell WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ufokn> { ?bn ?pn "s2Level13" . ?bn ?pv ?s2id . FILTER(CONTAINS(STR(?pv),'schema.org/value')) }
      BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.',STR(?s2id))) AS ?cell)
  } LIMIT 5000 }
  OPTIONAL { GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://www.w3.org/2002/07/owl#sameAs> ?cell } BIND(?cell AS ?shared) }
}
```

_sudokn × spatialkg_ — no static skeleton: the key is COMPUTED at query time (call the `spatial_bridge` tool, which derives the S2 cell from the KG's lat/long).

**county_FIPS** — `http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.{FIPS5}`: fiokg × spatialkg(3,031), fiokg × spoke-okn(3,032), geoconnex × spatialkg(3,114), geoconnex × spoke-okn(3,184), nikg × spatialkg(2), nikg × spoke-okn(2), wildlifekn × spatialkg(63), scales × spatialkg(3,029), scales × spoke-okn(3,096), spoke-okn × ruralkg(3,196), spoke-okn × sockg(31), spoke-okn × spatialkg(3,122), climatemodelskg → spoke-okn → spatialkg(947).

_fiokg × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?reg) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://www.w3.org/2002/07/owl#sameAs> ?reg . FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.')) }
  FILTER(STRLEN(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]',''))=5)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
}
```

_fiokg × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://www.w3.org/2002/07/owl#sameAs> ?reg . FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.')) }
  BIND(REPLACE(STR(?reg),'^.*administrativeRegion\\.USA\\.','') AS ?fips)
  FILTER(STRLEN(?fips)=5)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_geoconnex × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?x <http://gnis-ld.org/lod/gnis/ontology/county> ?county . }
  BIND(REPLACE(STR(?county),'^.*/counties/([0-9]{5}).*$','$1') AS ?fips)
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
}
```

_geoconnex × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?x <http://gnis-ld.org/lod/gnis/ontology/county> ?county . }
  BIND(REPLACE(STR(?county),'^.*/counties/([0-9]{5}).*$','$1') AS ?fips)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_nikg × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/nikg> { ?x <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?o . FILTER(STRSTARTS(STR(?o),'https://metadata.phila.gov/kwgr_administrativeRegion_USA_')) }
  BIND(REPLACE(STR(?o),'^.*administrativeRegion_USA_([0-9]{5}).*$','$1') AS ?fips)
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg ?p ?o2 . }
}
```

_nikg × spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/nikg> { ?x <http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin> ?o . FILTER(STRSTARTS(STR(?o),'https://metadata.phila.gov/kwgr_administrativeRegion_USA_')) }
  BIND(REPLACE(STR(?o),'^.*administrativeRegion_USA_([0-9]{5}).*$','$1') AS ?fips)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o2 . }
}
```

_wildlifekn × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips5) AS ?n) WHERE {
  { SELECT DISTINCT ?county WHERE { GRAPH <https://purl.org/okn/frink/kg/wildlifekn> { ?loc a <https://wildlife.proto-okn.net/kg/Location> ; <http://www.w3.org/2000/01/rdf-schema#label> ?county . FILTER(STRENDS(STR(?county),'County')) } } }
  { SELECT DISTINCT ?county ?fips5 WHERE { GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg <http://www.w3.org/2000/01/rdf-schema#label> ?rl . FILTER(CONTAINS(STR(?rl),' County, Florida')) BIND(REPLACE(STR(?rl),'^.*?([^,]+ County), Florida.*$','$1') AS ?county) BIND(SUBSTR(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]',''),1,5) AS ?fips5) } } }
}
```

_scales × spatialkg_

```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/scales> { ?x <http://schemas.scales-okn.org/rdf/scales#hasIdbCounty> ?c . FILTER(?c != 88888) }
  BIND(REPLACE(CONCAT('00000',STR(xsd:integer(?c))),'^.*(.{5})$','$1') AS ?fips)
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
}
```

_scales × spoke-okn_

```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/scales> { ?x <http://schemas.scales-okn.org/rdf/scales#hasIdbCounty> ?c . FILTER(?c != 88888) }
  BIND(REPLACE(CONCAT('00000',STR(xsd:integer(?c))),'^.*(.{5})$','$1') AS ?fips)
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/',?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_spoke-okn × ruralkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?fips WHERE { GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
      ?x <http://sail.ua.edu/ruralkg/settlementtype/censusCounty> ?reg . }
      FILTER(STRSTARTS(STR(?reg),'http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.'))
      BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
      FILTER(REGEX(?fips,'^[0-9]{5}$')) } }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/', ?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_spoke-okn × sockg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?fips WHERE { GRAPH <https://purl.org/okn/frink/kg/sockg> {
      ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
      BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{5}).*$','$1') AS ?fips)
      FILTER(REGEX(?fips,'^[0-9]{5}$')) } }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/', ?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_spoke-okn × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?fips WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
      BIND(IRI(CONCAT('https://schema.org/','AdministrativeArea')) AS ?ty)
      ?loc a ?ty . FILTER(REGEX(STR(?loc),'/location/[0-9]{5}$')) }
      BIND(REPLACE(STR(?loc),'^.*/location/([0-9]{5})$','$1') AS ?fips) } }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.', ?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg ?q ?r . }
}
```

_climatemodelskg → spoke-okn → spatialkg_

```sparql
PREFIX cm: <https://climatepub4kg.github.io/ontology#>
PREFIX so: <https://purl.org/okn/frink/kg/spoke-okn/schema/>
PREFIX kwg: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
SELECT (COUNT(DISTINCT ?fips5) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
    ?city cm:country_code "US" ; cm:admin1_code ?a1 ; cm:admin2_code ?a2 .
  }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?st so:abbr ?a1 . }
  BIND(CONCAT(REPLACE(STR(?st), "^.*/location/", ""), ?a2) AS ?fips5)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?ar kwg:hasFIPS ?fips5 ; a kwg:AdministrativeRegion_2 .
  }
}
```

**state_FIPS** — `https://geoconnex.us/ref/states/{FIPS2} (geoconnex) ; http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.{FIPS2} (spatialkg)`: geoconnex × spatialkg(51), spoke-okn × sockg(18), spoke-okn × spatialkg(51), sudokn × spatialkg(51).

_geoconnex × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?x <http://gnis-ld.org/lod/gnis/ontology/state> ?st . }
  BIND(REPLACE(STR(?st),'^.*/states/([0-9]{2}).*$','$1') AS ?fips)
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> . }
}
```

_spoke-okn × sockg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?fips WHERE { GRAPH <https://purl.org/okn/frink/kg/sockg> {
      ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> . }
      BIND(REPLACE(STR(?reg),'^.*administrativeRegion[.]USA[.]([0-9]{2}).*$','$1') AS ?fips)
      FILTER(REGEX(?fips,'^[0-9]{2}$')) } }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/', ?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_spoke-okn × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?fips WHERE { GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
      ?reg <http://stko-kwg.geog.ucsb.edu/lod/ontology/hasFIPS> ?fips ;
           a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> . } } }
  BIND(IRI(CONCAT('https://purl.org/okn/frink/kg/spoke-okn/location/', ?fips)) AS ?loc)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . }
}
```

_sudokn × spatialkg_

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?state WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> {
      ?a <http://asu.edu/semantics/SUDOKN/locatedInState>/<http://www.w3.org/2000/01/rdf-schema#label> ?state . } } }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> {
    ?r a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
       <http://www.w3.org/2000/01/rdf-schema#label> ?state ;
       <http://stko-kwg.geog.ucsb.edu/lod/ontology/hasFIPS> ?fips . }
}
```

**KWG_county** — `http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.`: sockg × spatialkg(62).

```sparql
SELECT (COUNT(DISTINCT ?reg) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sockg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
}
```

**ZIP5** — `bare 5-digit U.S. ZIP code, xsd:string literal (no IRI namespace)`: spoke-okn × dreamkg(53), spoke-okn × ruralkg(5,390), ruralkg × scales(5,297), dreamkg × scales(53), dreamkg × ruralkg(30), spoke-okn × sudokn(13,647).

_spoke-okn × dreamkg_

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip . FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+')) }
  GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?b <http://schema.org/postalCode> ?zip . }
}
```

_spoke-okn × ruralkg_

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  { SELECT DISTINCT ?zip WHERE { GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
      BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?pp)
      ?b ?pp ?z0 . }
      BIND(REPLACE(STR(?z0),'[^0-9]','') AS ?d)
      BIND(IF(STRLEN(?d)=4, CONCAT('0',?d), SUBSTR(?d,1,5)) AS ?zip) } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip .
      FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+')) }
}
```

_ruralkg × scales_

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
        BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?p)
        ?r ?p ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?d)
      BIND(IF(STRLEN(?d)=4, CONCAT("0",?d), SUBSTR(?d,1,5)) AS ?zip) } }
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?court <http://release.niem.gov/niem/niem-core/5.0/#AddressPostalCode> ?z1 . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=3, CONCAT("00",?e),
           IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5))) AS ?zip) } }
}
```

_dreamkg × scales_

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?d <http://schema.org/postalCode> ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip) } }
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?court <http://release.niem.gov/niem/niem-core/5.0/#AddressPostalCode> ?z1 . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=3, CONCAT("00",?e),
           IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5))) AS ?zip) } }
}
```

_dreamkg × ruralkg_

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?d <http://schema.org/postalCode> ?z0 . }
      BIND(REPLACE(STR(?z0),"[^0-9]","") AS ?a)
      BIND(IF(STRLEN(?a)=4, CONCAT("0",?a), SUBSTR(?a,1,5)) AS ?zip) } }
  { SELECT DISTINCT ?zip WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
        BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?p)
        ?r ?p ?z1 . }
      BIND(REPLACE(STR(?z1),"[^0-9]","") AS ?e)
      BIND(IF(STRLEN(?e)=4, CONCAT("0",?e), SUBSTR(?e,1,5)) AS ?zip) } }
}
```

_spoke-okn × sudokn_

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  { SELECT DISTINCT ?zip WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> {
      BIND(IRI(CONCAT('https://schema.org/','postalCode')) AS ?pp)
      ?addr ?pp ?z0 . }
      BIND(REPLACE(STR(?z0),'[^0-9]','') AS ?d)
      BIND(IF(STRLEN(?d)=4, CONCAT('0',?d), SUBSTR(?d,1,5)) AS ?zip) } }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip .
      FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+')) }
}
```

**GeoNames** — `climatemodelskg <https://climatepub4kg.github.io/ontology#geonameid> (bare GeoNames integer) <-> spoke-okn <https://purl.org/okn/frink/kg/spoke-okn/schema/code> (GeoNames code on schema:AdministrativeArea)`: climatemodelskg × spoke-okn(106).

```sparql
SELECT (COUNT(DISTINCT ?g) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> { ?c <https://climatepub4kg.github.io/ontology#geonameid> ?g . }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s <https://purl.org/okn/frink/kg/spoke-okn/schema/code> ?g . }
}
```

### HYDROLOGY

**COMID** — `https://geoconnex.us/nhdplusv2/comid/{COMID} - the SAME IRI on both sides (geoconnex as the object of wd:P885/P403; hydrologykg as its reach subject IRI)`: geoconnex × hydrologykg(11,392).

```sparql
PREFIX nhd: <http://nhdplusv2.spatialai.org/v1/nhdplusv2#>
PREFIX wd: <https://www.wikidata.org/wiki/Property:>
SELECT (COUNT(DISTINCT ?reach) AS ?n) WHERE {
  {
    { SELECT DISTINCT ?reach WHERE {
        GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?ms wd:P885 ?reach . } } }
    UNION
    { SELECT DISTINCT ?reach WHERE {
        GRAPH <https://purl.org/okn/frink/kg/geoconnex> { ?ms wd:P403 ?reach . } } }
  }
  GRAPH <https://purl.org/okn/frink/kg/hydrologykg> { ?reach nhd:hasCOMID ?c . }
}
```

### INDUSTRY & SUPPLY CHAIN

**NAICS** — `http://w3id.org/fio/v1/naics#NAICS-{code} (fiokg) ; http://asu.edu/semantics/SUDOKN/naics-{code}.0-inst (securechainkg)`: fiokg × securechainkg(301), fiokg × sudokn(60), securechainkg × sudokn(35).

_fiokg × securechainkg_

```sparql
SELECT (COUNT(DISTINCT ?code) AS ?n) WHERE {
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://w3id.org/fio/v1/epa-frs#ofPrimaryIndustry>|<http://w3id.org/fio/v1/epa-frs#ofSecondaryIndustry> ?ind . } BIND(REPLACE(STR(?ind),'^.*naics#NAICS-([0-9]+)$','$1') AS ?code) } }
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?a <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?sn . } BIND(REPLACE(STR(?sn),'^.*/naics-([0-9]+)\\.0-inst$','$1') AS ?code) } }
}
```

_fiokg × sudokn_

```sparql
SELECT (COUNT(DISTINCT ?code) AS ?n) WHERE {
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://w3id.org/fio/v1/epa-frs#ofPrimaryIndustry>|<http://w3id.org/fio/v1/epa-frs#ofSecondaryIndustry> ?ind . } BIND(REPLACE(STR(?ind),'^.*naics#NAICS-([0-9]+)$','$1') AS ?code) } }
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?dn . } BIND(REPLACE(STR(?dn),'^.*NAICS%20([0-9]+)-individual$','$1') AS ?code) } }
}
```

_securechainkg × sudokn_

```sparql
SELECT (COUNT(DISTINCT ?code) AS ?n) WHERE {
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?a <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?sn . } BIND(REPLACE(STR(?sn),'^.*/naics-([0-9]+)\\.0-inst$','$1') AS ?code) } }
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?dn . } BIND(REPLACE(STR(?dn),'^.*NAICS%20([0-9]+)-individual$','$1') AS ?code) } }
}
```

**SUDOKN_industry_sector** — `http://asu.edu/semantics/SUDOKN/{sector}-inst ; http://asu.edu/semantics/SUDOKN/{Sector}-industry-individual`: securechainkg × sudokn(58).

```sparql
SELECT (COUNT(DISTINCT ?sec) AS ?n) WHERE {
  { SELECT DISTINCT ?sec WHERE { GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?a <http://asu.edu/semantics/SUDOKN/suppliesToIndustry> ?si . } BIND(LCASE(REPLACE(STR(?si),'^.*/SUDOKN/(.*)-inst$','$1')) AS ?sec) } }
  { SELECT DISTINCT ?sec WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/suppliesToIndustry> ?di . } BIND(LCASE(REPLACE(REPLACE(STR(?di),'^.*/SUDOKN/(.*)-industry-individual$','$1'),'%20','')) AS ?sec) } }
}
```

**climatemodelskg Source IRI** — `https://climatepub4kg.github.io/id/Source/`: climatemodelskg × securechainkg(3).

```sparql
SELECT (COUNT(DISTINCT ?model) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> { ?model a <https://climatepub4kg.github.io/ontology#Source> . }
  GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?model <https://w3id.org/secure-chain/dependsOn> ?dep . }
}
```

### JUSTICE & PUBLIC SAFETY

**NIBRS_offense_category** — `FBI NIBRS/UCR offense-category NAME as a plain string literal, identical on both sides (e.g. 'Aggravated Assault', 'Drug/Narcotic Violations', 'Robbery'). scales attaches it to jxdm:Charge nodes via fbi:OffenseUCRCode; ruralkg attaches it to NIBRSAnswer nodes via variable/answerContent (which also carry the matching NIBRS variable/answerCode, e.g. 131 = Aggravated Assault, 351 = Drug/Narcotic Violations). Both sides ingest the FBI NIBRS crime taxonomy, so this is a CONTROLLED-vocabulary match, not fuzzy label collision.`: scales × ruralkg(37).

```sparql
PREFIX fbi: <http://fbi.gov/cjis/nibrs/2023.0/>
PREFIX rk: <http://sail.ua.edu/ruralkg/variable/>
SELECT (COUNT(DISTINCT ?off) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/scales> { ?ch fbi:OffenseUCRCode ?off . }
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?ans rk:answerContent ?off . }
}
```

### PROTEINS

**UniProt** — `https://identifiers.org/uniprot/ ; http://purl.uniprot.org/uniprot/`: biobricks-aopwiki × prokn(1,805), ncipidkg × prokn(12), biomarkerkg × prokn(209), biomarkerkg × biobricks-aopwiki(86).

_biobricks-aopwiki × prokn_

```sparql
SELECT (COUNT(DISTINCT ?p2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?u ?pa ?oa . FILTER(STRSTARTS(STR(?u),'https://identifiers.org/uniprot/')) }
  BIND(IRI(CONCAT('http://purl.uniprot.org/uniprot/',REPLACE(STR(?u),'^.*/uniprot/',''))) AS ?p2)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?p2 ?pp ?op . }
}
```

_ncipidkg × prokn_

```sparql
SELECT (COUNT(DISTINCT ?p2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ncipidkg> { ?s <http://www.w3.org/2002/07/owl#sameAs> ?u . FILTER(STRSTARTS(STR(?u),'http://identifiers.org/uniprot/')) }
  BIND(IRI(CONCAT('http://purl.uniprot.org/uniprot/',REPLACE(STR(?u),'^.*/uniprot/',''))) AS ?p2)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?p2 ?pp ?op . }
}
```

_biomarkerkg × prokn_

```sparql
SELECT (COUNT(DISTINCT ?up) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?up . FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?up ?p ?o . }
}
```

_biomarkerkg × biobricks-aopwiki_

```sparql
SELECT (COUNT(DISTINCT ?acc) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?up . FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/')) }
  BIND(REPLACE(STR(?up),'^.*/uniprot/','') AS ?acc)
  BIND(IRI(CONCAT('https://identifiers.org/uniprot/',?acc)) AS ?u2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?y <http://www.w3.org/2004/02/skos/core#exactMatch> ?u2 . }
}
```

### PUBLICATIONS

**DOI** — `climatemodelskg <https://climatepub4kg.github.io/ontology#doi> (DOI as string literal, https://doi.org/ form) <-> nasa-gesdisc-kg <http://purl.org/ontology/bibo/doi> (DOI as IRI, http://dx.doi.org/ form)`: climatemodelskg × nasa-gesdisc-kg(651).

```sparql
SELECT (COUNT(DISTINCT ?bare) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> { ?p1 <https://climatepub4kg.github.io/ontology#doi> ?d1 .
    BIND(LCASE(REPLACE(STR(?d1),"^https?://(dx[.])?doi[.]org/","")) AS ?bare) }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> { ?p2 <http://purl.org/ontology/bibo/doi> ?d2 .
    BIND(LCASE(REPLACE(STR(?d2),"^https?://(dx[.])?doi[.]org/","")) AS ?bare) }
}
```

**author name (string; NOT an ORCID — see the entry's caveat)** — `climatemodelskg <https://climatepub4kg.github.io/ontology#name> <-> nasa-gesdisc-kg <http://www.w3.org/2000/01/rdf-schema#label>, both plain string literals. NOT an identifier join — there is no shared ORCID.`: climatemodelskg × nasa-gesdisc-kg(8,391).

```sparql
SELECT (COUNT(DISTINCT ?nm) AS ?n) WHERE {
  { SELECT DISTINCT ?nm WHERE {
      GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> {
        ?a a <https://climatepub4kg.github.io/ontology#Author> ;
           <https://climatepub4kg.github.io/ontology#name> ?nm . } } }
  GRAPH <https://purl.org/okn/frink/kg/nasa-gesdisc-kg> {
    ?b a <https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author> ;
       <http://www.w3.org/2000/01/rdf-schema#label> ?nm . }
}
```

### SOCIAL DETERMINANTS & SERVICES

**MeSH→UMLS (bridged)** — `spoke-okn spoke:mesh_ids https://id.nlm.nih.gov/mesh/D{n} -> wikidata P486 (MeSH descriptor) -> P2892 (UMLS CUI) -> https://biohealthkg.proto-okn.net/kg/node/C{cui} (biohealth)`: spoke-okn → wikidata → biohealth(3).

```sparql
SELECT (COUNT(DISTINCT ?bh) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s a <https://purl.org/okn/frink/kg/spoke-okn/schema/SDoH> ; <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_ids> ?meshIri . }
  BIND(REPLACE(STR(?meshIri),'^.*/mesh/','') AS ?meshId)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item <http://www.wikidata.org/prop/direct/P486> ?meshId ; <http://www.wikidata.org/prop/direct/P2892> ?cui . }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**concept label (SNOMED preferred term ↔ UMLS concept name)** — `spoke-okn SDoH node IRI = SNOMED CT concept id, rdfs:label = 'Preferred term (semantic tag)'; biohealth node IRI = UMLS CUI, rdfs:label = UMLS concept name. Matched on the LABEL after stripping the SNOMED ' (finding)/(event)/(occupation)/...' suffix.`: spoke-okn × biohealth(89).

```sparql
SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s a <https://purl.org/okn/frink/kg/spoke-okn/schema/SDoH> ; <http://www.w3.org/2000/01/rdf-schema#label> ?sl . }
  BIND(IF(CONTAINS(?sl,' ('), STRBEFORE(?sl,' ('), STR(?sl)) AS ?clean)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?clean . }
}
```

**concept label (social-service audience term ↔ UMLS concept name)** — `dreamkg schema:audienceType free-text term (e.g. 'anxiety', 'veterans', 'uninsured') <-> biohealth rdfs:label (UMLS concept name, Title-case)`: dreamkg × biohealth(14).

```sparql
SELECT (COUNT(DISTINCT ?aud) AS ?n) WHERE {
  { SELECT DISTINCT ?aud WHERE { GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?s <http://schema.org/audienceType> ?aud } } }
  BIND(CONCAT(UCASE(SUBSTR(?aud,1,1)), SUBSTR(?aud,2)) AS ?cap)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?cap . }
}
```

**concept label (psychosocial / SDoH term ↔ UMLS concept name)** — `phaseskg rdfs:label (OBO class label) <-> biohealth rdfs:label (UMLS concept name, Title-case). Curated 8-concept equivalence on the social-connection / aging axis.`: phaseskg × biohealth(8).

```sparql
SELECT (COUNT(*) AS ?n) WHERE {
  VALUES (?p ?bh) {
    (<http://purl.obolibrary.org/obo/PHASES_0002002> <https://biohealthkg.proto-okn.net/kg/node/C0037421>)
    (<http://purl.obolibrary.org/obo/PHASES_0002003> <https://biohealthkg.proto-okn.net/kg/node/C0023974>)
    (<http://purl.obolibrary.org/obo/PHASES_0000011> <https://biohealthkg.proto-okn.net/kg/node/C0424095>)
    (<http://purl.obolibrary.org/obo/PHASES_0000027> <https://biohealthkg.proto-okn.net/kg/node/C0700137>)
    (<http://purl.obolibrary.org/obo/PHASES_0000028> <https://biohealthkg.proto-okn.net/kg/node/C0037020>)
    (<http://purl.obolibrary.org/obo/PHASES_0000000> <https://biohealthkg.proto-okn.net/kg/node/C0150321>)
    (<http://purl.obolibrary.org/obo/PHASES_0000007> <https://biohealthkg.proto-okn.net/kg/node/C0600564>)
    (<http://humanbehaviourchange.org/ontology/BCIO_006014> <https://biohealthkg.proto-okn.net/kg/node/C0870124>)
  }
  GRAPH <https://purl.org/okn/frink/kg/phaseskg> { ?p <http://www.w3.org/2000/01/rdf-schema#label> ?pl }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?bl }
}
```

### TAXONOMY

**NCBITaxon** — `http://purl.obolibrary.org/obo/NCBITaxon_`: sawgraph × ubergraph(538), spoke-genelab × ubergraph(9), spoke-okn × ubergraph(33,602), gene-expression-atlas-okn × ubergraph(8), biobricks-aopwiki × ubergraph(164), nde × ubergraph(1,797), spoke-genelab → ubergraph → spoke-okn(33,313), spoke-genelab × ubergraph(46), wildlifekn → ubergraph → nde(17), wildlifekn → ubergraph → sawgraph(2), wildlifekn × ubergraph(339).

_sawgraph × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?sup . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_spoke-genelab × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?gene <https://purl.org/okn/frink/kg/spoke-genelab/schema/taxonomy> ?ts . FILTER(STRSTARTS(STR(?ts),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  BIND(IRI(STR(?ts)) AS ?taxon)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_spoke-okn × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  { SELECT DISTINCT ?taxon WHERE {
    GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?o a <https://w3id.org/biolink/vocab/OrganismTaxon> . }
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?o),'^.*/organism/([0-9]+).*$','$1'))) AS ?taxon)
  } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_gene-expression-atlas-okn × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/in_taxon> ?taxon . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_biobricks-aopwiki × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://purl.org/dc/elements/1.1/identifier> ?taxon . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_nde × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  { SELECT DISTINCT ?taxon WHERE {
    GRAPH <https://purl.org/okn/frink/kg/nde> { ?s <http://schema.org/species> ?o . FILTER(CONTAINS(STR(?o),'/taxonomy/')) }
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?o),'^.*/taxonomy/([0-9]+).*$','$1'))) AS ?taxon)
  } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_spoke-genelab → ubergraph → spoke-okn_ (skeleton not re-verified)

```sparql
SELECT (COUNT(DISTINCT ?desc) AS ?n) WHERE {
  { SELECT DISTINCT ?genus WHERE {
    GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?node a <https://purl.org/okn/frink/kg/spoke-genelab/schema/Organism> . }
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?node),'^.*/node/([0-9]+).*$','$1'))) AS ?genus)
  } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?desc <http://www.w3.org/2000/01/rdf-schema#subClassOf>* ?genus . }
  { SELECT DISTINCT ?desc WHERE {
    GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?ot a <https://w3id.org/biolink/vocab/OrganismTaxon> }
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?ot),'^.*/organism/([0-9]+).*$','$1'))) AS ?desc)
  } }
}
```

_spoke-genelab × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?node a <https://purl.org/okn/frink/kg/spoke-genelab/schema/Organism> . }
  BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?node),'^.*/node/([0-9]+).*$','$1'))) AS ?taxon)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?u . }
}
```

_wildlifekn → ubergraph → nde_

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?shared) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/wildlifekn> { VALUES ?_tc { <https://wildlife.proto-okn.net/kg/Bird_name> <https://wildlife.proto-okn.net/kg/Amphibian_name> } ?_t1 a ?_tc ; <http://www.w3.org/2000/01/rdf-schema#label> ?_t2 . BIND(REPLACE(STR(?_t2),'^([^ ]+ [^ ]+).*$','$1') AS ?_t3) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?t <http://www.w3.org/2000/01/rdf-schema#label> ?_t3 . FILTER(STRSTARTS(STR(?t),'http://purl.obolibrary.org/obo/NCBITaxon_')) } } }
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/nde> { ?_n1 <http://schema.org/species> ?_n2 . FILTER(CONTAINS(STR(?_n2),'/taxonomy/')) } BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?_n2),'^.*/taxonomy/([0-9]+).*$','$1'))) AS ?t) } }
}
```

_wildlifekn → ubergraph → sawgraph_

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?shared) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/wildlifekn> { VALUES ?_tc { <https://wildlife.proto-okn.net/kg/Bird_name> <https://wildlife.proto-okn.net/kg/Amphibian_name> } ?_t1 a ?_tc ; <http://www.w3.org/2000/01/rdf-schema#label> ?_t2 . BIND(REPLACE(STR(?_t2),'^([^ ]+ [^ ]+).*$','$1') AS ?_t3) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?t <http://www.w3.org/2000/01/rdf-schema#label> ?_t3 . FILTER(STRSTARTS(STR(?t),'http://purl.obolibrary.org/obo/NCBITaxon_')) } } }
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?t <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?_s1 . FILTER(STRSTARTS(STR(?t),'http://purl.obolibrary.org/obo/NCBITaxon_')) } } }
}
```

_wildlifekn × ubergraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/wildlifekn> { VALUES ?cls { <https://wildlife.proto-okn.net/kg/Bird_name> <https://wildlife.proto-okn.net/kg/Amphibian_name> } ?s a ?cls ; <http://www.w3.org/2000/01/rdf-schema#label> ?l . BIND(REPLACE(?l,'^(\\S+\\s+\\S+).*$','$1') AS ?binom) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?binom . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
}
```

**NCBITaxon (biohealth label)** — `biohealth rdfs:label (the UMLS-CUI node's concept name) <-> ubergraph NCBITaxon rdfs:label <-> http://purl.obolibrary.org/obo/NCBITaxon_ (spoke-okn); exact scientific-name match (approximate lower bound; misses synonyms/spelling variants; no subClassOf* clade expansion)`: biohealth → ubergraph → spoke-okn(1,603), biohealth → ubergraph → nde(1,052), biohealth → ubergraph → sawgraph(377), biohealth → ubergraph → biobricks-aopwiki(112), biohealth → ubergraph → spoke-genelab(7), biohealth → ubergraph → gene-expression-atlas-okn(6).

_biohealth → ubergraph → spoke-okn_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  { SELECT DISTINCT ?taxon WHERE {
    GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?ot a <https://w3id.org/biolink/vocab/OrganismTaxon> }
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?ot),'^.*/organism/([0-9]+).*$','$1'))) AS ?taxon)
  } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

_biohealth → ubergraph → nde_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  { SELECT DISTINCT ?taxon WHERE {
    GRAPH <https://purl.org/okn/frink/kg/nde> { ?s <http://schema.org/species> ?o . FILTER(CONTAINS(STR(?o),'/taxonomy/')) }
    BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?o),'^.*/taxonomy/([0-9]+).*$','$1'))) AS ?taxon)
  } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

_biohealth → ubergraph → sawgraph_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sawgraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?sup . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

_biohealth → ubergraph → biobricks-aopwiki_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-aopwiki> { ?s <http://purl.org/dc/elements/1.1/identifier> ?taxon . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

_biohealth → ubergraph → spoke-genelab_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?gene <https://purl.org/okn/frink/kg/spoke-genelab/schema/taxonomy> ?ts . FILTER(STRSTARTS(STR(?ts),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  BIND(IRI(STR(?ts)) AS ?taxon)
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

_biohealth → ubergraph → gene-expression-atlas-okn_

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/in_taxon> ?taxon . FILTER(STRSTARTS(STR(?taxon),'http://purl.obolibrary.org/obo/NCBITaxon_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

### NOTES

- **Skeletons are COUNT queries by design.** Each proves the key still joins and reproduces the table's `verified_count`; run it first, then extend it with your payload rather than rebuilding the normalization boilerplate.
- **The identifier, not the entity, is what matches.** Counts are `COUNT(DISTINCT <shared key>)` — shared identifiers, not shared rows. A KG may mint several nodes carrying the same id.
- **Sources:** the crosswalk table served by `list_crosswalks` / `get_join_strategy` (verified 2026-07-12).

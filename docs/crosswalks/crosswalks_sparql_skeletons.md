# FRINK / Proto-OKN Crosswalk Reference — Join Keys & SPARQL Skeletons

- **Date:** 2026-07-07
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used

- `biomarkerkg` — <https://purl.org/okn/frink/kg/biomarkerkg>
- `gene-expression-atlas-okn` — <https://purl.org/okn/frink/kg/gene-expression-atlas-okn>
- `prokn` — <https://purl.org/okn/frink/kg/prokn>
- `spoke-genelab` — <https://purl.org/okn/frink/kg/spoke-genelab>
- `biohealth` — <https://purl.org/okn/frink/kg/biohealth>
- `ubergraph` — <https://purl.org/okn/frink/kg/ubergraph>
- `biobricks-ice` — <https://purl.org/okn/frink/kg/biobricks-ice>
- `biobricks-toxcast` — <https://purl.org/okn/frink/kg/biobricks-toxcast>
- `biobricks-tox21` — <https://purl.org/okn/frink/kg/biobricks-tox21>
- `biobricks-aopwiki` — <https://purl.org/okn/frink/kg/biobricks-aopwiki>
- `sawgraph` — <https://purl.org/okn/frink/kg/sawgraph>
- `spoke-okn` — <https://purl.org/okn/frink/kg/spoke-okn>
- `biobricks-pubchem-annotations` — <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations>
- `rdkg` — <https://purl.org/okn/frink/kg/rdkg>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>
- `nde` — <https://purl.org/okn/frink/kg/nde>
- `oard-kg` — <https://purl.org/okn/frink/kg/oard-kg>
- `digcfdekg` — <https://purl.org/okn/frink/kg/digcfdekg>
- `biobricks-mesh` — <https://purl.org/okn/frink/kg/biobricks-mesh>
- `pankgraph` — <https://purl.org/okn/frink/kg/pankgraph>
- `ncipidkg` — <https://purl.org/okn/frink/kg/ncipidkg>
- `wikidata` — <https://purl.org/okn/frink/kg/wikidata>
- `sockg` — <https://purl.org/okn/frink/kg/sockg>
- `spatialkg` — <https://purl.org/okn/frink/kg/spatialkg>
- `fiokg` — <https://purl.org/okn/frink/kg/fiokg>
- `hydrologykg` — <https://purl.org/okn/frink/kg/hydrologykg>
- `sudokn` — <https://purl.org/okn/frink/kg/sudokn>
- `ufokn` — <https://purl.org/okn/frink/kg/ufokn>
- `geoconnex` — <https://purl.org/okn/frink/kg/geoconnex>
- `nikg` — <https://purl.org/okn/frink/kg/nikg>
- `scales` — <https://purl.org/okn/frink/kg/scales>
- `wildlifekn` — <https://purl.org/okn/frink/kg/wildlifekn>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>
- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `dreamkg` — <https://purl.org/okn/frink/kg/dreamkg>

## Conversation

👤 **User**

For each crosswalk, list the join key and the SPARQL skeleton

---

🧠 **Assistant**

The FRINK federation has 134 crosswalks, which collapse into ~39 distinct join-key families. Rather than repeat near-identical SPARQL 134 times, they are grouped by domain and key family — each entry lists every KG pair sharing that key (with verified COUNT(DISTINCT) counts), the identifier scheme/namespace, and a runnable COUNT(DISTINCT) skeleton (with the IRI normalization already applied, since naive joins on the raw id usually return 0). Counts verified 2026-06-30 (taxonomy 2026-06-14).

### ANATOMY & CELL TYPE

**CL** (Cell Ontology, direct — `obo/CL_`): biomarkerkg×gene-expression-atlas-okn(8), biomarkerkg×prokn(3), gene-expression-atlas-okn×prokn(31), spoke-genelab×gene-expression-atlas-okn(4), spoke-genelab×prokn(1). Predicates vary: GXA `biolink:has_attribute`; prokn `rdf:subject`; spoke-genelab `schema/INVESTIGATED_ASiCT`; biomarkerkg `obo:OBCI_1000009`.

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/has_attribute> ?t . FILTER(STRSTARTS(STR(?t), 'http://purl.obolibrary.org/obo/CL_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?t . }
}
```

**UBERON** (anatomy, direct — `obo/UBERON_`): spoke-genelab×gene-expression-atlas-okn(27).

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?s <https://purl.org/okn/frink/kg/spoke-genelab/schema/INVESTIGATED_ASiA> ?t } } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s2 <https://w3id.org/biolink/vocab/has_attribute> ?t . }
}
```

**UMLS↔UBERON** (bridged via ubergraph `hasDbXref UMLS:`): biohealth×gene-expression-atlas-okn(249), biohealth×spoke-genelab(35).

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <https://w3id.org/biolink/vocab/has_attribute> ?t . FILTER(STRSTARTS(STR(?t), 'http://purl.obolibrary.org/obo/UBERON_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?t <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?x), 'UMLS:')) BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui) }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

### CHEMICALS

**CAS** (direct — `identifiers.org/cas/`, `edam:has_identifier`): biobricks-aopwiki×biobricks-toxcast(290), biobricks-ice×biobricks-toxcast(9421), biobricks-tox21×biobricks-ice(8916), biobricks-tox21×biobricks-toxcast(8909), sawgraph×biobricks-ice(12), sawgraph×biobricks-toxcast(7).

```sparql
SELECT (COUNT(DISTINCT ?cas) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?a <http://edamontology.org/has_identifier> ?cas . }
  GRAPH <https://purl.org/okn/frink/kg/biobricks-toxcast> { ?b <http://edamontology.org/has_identifier> ?cas . }
  FILTER(STRSTARTS(STR(?cas),'http://identifiers.org/cas/'))
}
```

**CHEBI↔CAS** (bridged via ubergraph): spoke-okn×biobricks-ice(712), spoke-okn×biobricks-tox21(480), spoke-okn×biobricks-toxcast(496).

```sparql
SELECT (COUNT(DISTINCT ?c2) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?cmp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?chebi . FILTER(STRSTARTS(STR(?chebi),'http://purl.obolibrary.org/obo/CHEBI_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?chebi <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?casCurie . FILTER(STRSTARTS(STR(?casCurie),'cas:')) }
  BIND(IRI(CONCAT('http://identifiers.org/cas/',SUBSTR(STR(?casCurie),5))) AS ?c2)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-ice> { ?t <http://edamontology.org/has_identifier> ?c2 . }
}
```

**DrugBank** (direct — `identifiers.org/drugbank/DB{n}`; rdkg node IRI is the DrugBank IRI, spoke-okn on `oboInOwl:hasDbXref`): rdkg×spoke-okn(43), ruralkg×rdkg(2).

```sparql
SELECT (COUNT(DISTINCT ?db) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?db a <https://w3id.org/biolink/vocab/Drug> . FILTER(STRSTARTS(STR(?db),'http://identifiers.org/drugbank/')) }
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?c <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?db . }
}
```

**PubChem CID** (direct w/ rewrite — spoke-okn `identifiers.org/pubchem.compound/{n}` → biobricks `rdf.ncbi.nlm.nih.gov/.../CID{n}`): biobricks-pubchem-annotations×spoke-okn(762).

```sparql
SELECT (COUNT(DISTINCT ?cid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?c <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?x),'http://identifiers.org/pubchem.compound/')) }
  BIND(REPLACE(STR(?x),'^http://identifiers.org/pubchem.compound/','') AS ?cid)
  BIND(IRI(CONCAT('http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID',?cid)) AS ?b)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-pubchem-annotations> { ?ann <http://www.w3.org/ns/oa#hasTarget> ?b . }
}
```

### DISEASE & PHENOTYPE

**DOID** (direct — `obo/DOID_`; spoke-okn node IRI is the DOID): biomarkerkg×nde(54), spoke-okn×biomarkerkg(79), spoke-okn×nde(20).

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?x ?q ?doid . }
}
```

**DOID↔MONDO** (bridged, ubergraph `skos:exactMatch`): biomarkerkg×oard-kg(247), biomarkerkg×prokn(344), biomarkerkg×rdkg(595), gene-expression-atlas-okn×spoke-okn(54), spoke-okn×oard-kg(40), spoke-okn×prokn(115), spoke-okn×rdkg(149). *(prokn v0.0.5 migrated disease xrefs to skos:exactMatch/MONDO, hence the bridge.)*

```sparql
SELECT (COUNT(DISTINCT ?doid) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?doid a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?doid),'http://purl.obolibrary.org/obo/DOID_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?d <http://www.w3.org/2004/02/skos/core#exactMatch> ?mondo . }
}
```

**DOID↔MONDO (+EFO/Orphanet→MONDO)**: biomarkerkg×digcfdekg(123), spoke-okn×digcfdekg(50). Same DOID↔MONDO ubergraph bridge plus digcfdekg `geneToTrait` EFO/Orphanet folded into MONDO via ubergraph `skos:exactMatch`.

**EFO/Orphanet/MONDO** (direct multi-vocab — `efo/EFO_`, `ORDO/Orphanet_`, `obo/MONDO_`): digcfdekg×gene-expression-atlas-okn(33).

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?x <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . FILTER(STRSTARTS(STR(?t),'http://www.ebi.ac.uk/efo/EFO_') || STRSTARTS(STR(?t),'http://purl.obolibrary.org/obo/MONDO_') || CONTAINS(STR(?t),'Orphanet_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?t a <https://w3id.org/biolink/vocab/Disease> . }
}
```

**EFO↔MONDO** (bridged): gene-expression-atlas-okn×nde(325), gene-expression-atlas-okn×oard-kg(159), gene-expression-atlas-okn×rdkg(414). UNION direct MONDO + EFO→MONDO + Orphanet→MONDO (ubergraph `skos:exactMatch`).

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  { { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?mondo a <https://w3id.org/biolink/vocab/Disease> . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?efo a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?efo),'/efo/EFO_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?efo . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } }
    UNION { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?orph a <https://w3id.org/biolink/vocab/Disease> . FILTER(CONTAINS(STR(?orph),'Orphanet_')) } GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?orph . FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/nde> { ?x <http://schema.org/healthCondition> ?mondo . }
}
```

**HP** (direct — `obo/HP_`; oard-kg uses both subject/object roles): gene-expression-atlas-okn×oard-kg(13), gene-expression-atlas-okn×prokn(12), oard-kg×prokn(4941).

```sparql
SELECT (COUNT(DISTINCT ?hp) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?s <https://w3id.org/biolink/vocab/object> ?hp } UNION { ?ss <https://w3id.org/biolink/vocab/subject> ?hp } FILTER(STRSTARTS(STR(?hp),'http://purl.obolibrary.org/obo/HP_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?hp . }
}
```

**MONDO** (direct — `obo/MONDO_`; prokn side scoped to `up:Disease`): nde×oard-kg(889), oard-kg×prokn(470), rdkg×oard-kg(2014).

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?s <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?ss <https://w3id.org/biolink/vocab/subject> ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?mondo . }
}
```

**MONDO (+EFO/Orphanet→MONDO)**: digcfdekg×oard-kg(402), digcfdekg×rdkg(1045).

**MONDO↔OMIM** (bridged via ubergraph `hasDbXref OMIM:`): oard-kg×prokn(11). Complementary to direct MONDO.

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?curie . FILTER(STRSTARTS(STR(?curie),'OMIM:')) }
  BIND(IRI(CONCAT('https://www.omim.org/entry/',REPLACE(STR(?curie),'^OMIM:',''))) AS ?omim)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?y a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?omim . }
}
```

**MONDO↔Orphanet** (bridged via ubergraph `hasDbXref Orphanet:`): oard-kg×prokn(316). Largest complementary bridge (+278 prokn diseases beyond direct MONDO).

```sparql
SELECT (COUNT(DISTINCT ?mondo) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?x <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?xs <https://w3id.org/biolink/vocab/subject> ?mondo } FILTER(STRSTARTS(STR(?mondo),'http://purl.obolibrary.org/obo/MONDO_')) }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?curie . FILTER(STRSTARTS(STR(?curie),'Orphanet:')) }
  BIND(IRI(CONCAT('http://www.orpha.net/ORDO/Orphanet_',REPLACE(STR(?curie),'^Orphanet:',''))) AS ?orpha)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?y a <http://purl.uniprot.org/core/Disease> ; <http://www.w3.org/2004/02/skos/core#exactMatch> ?orpha . }
}
```

**MeSH descriptor id** (direct, http/https rewrite): biobricks-mesh×spoke-okn(165).

```sparql
SELECT (COUNT(DISTINCT ?id) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s ?p ?mo . VALUES ?p { <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_list> <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_ids> } }
  BIND(REPLACE(STR(?mo),'^https://id.nlm.nih.gov/mesh/','') AS ?id)
  BIND(IRI(CONCAT('http://id.nlm.nih.gov/mesh/',?id)) AS ?m)
  GRAPH <https://purl.org/okn/frink/kg/biobricks-mesh> { ?m ?bp ?bo . }
}
```

**UMLS↔HP** (bridged): biohealth×gene-expression-atlas-okn(13), biohealth×oard-kg(4549), biohealth×prokn(4340).

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?hp WHERE { GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?z <https://w3id.org/biolink/vocab/object> ?hp } UNION { ?z2 <https://w3id.org/biolink/vocab/subject> ?hp } FILTER(STRSTARTS(STR(?hp), 'http://purl.obolibrary.org/obo/HP_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?hp <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?x), 'UMLS:')) BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui) }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**UMLS↔MONDO** (bridged): biohealth×nde(2760), biohealth×oard-kg(1796), biohealth×rdkg(9122).

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?mondo), 'http://purl.obolibrary.org/obo/MONDO_')) FILTER(STRSTARTS(STR(?x), 'UMLS:')) BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui) }
  GRAPH <https://purl.org/okn/frink/kg/oard-kg> { { ?z <https://w3id.org/biolink/vocab/object> ?mondo } UNION { ?z2 <https://w3id.org/biolink/vocab/subject> ?mondo } }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**UMLS↔MONDO↔DOID** (two-hop bridged): biohealth×biomarkerkg(620), biohealth×spoke-okn(173).

```sparql
SELECT (COUNT(DISTINCT ?cui) AS ?n) WHERE {
  { SELECT DISTINCT ?doid WHERE { GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s ?p ?doid . FILTER(STRSTARTS(STR(?doid), 'http://purl.obolibrary.org/obo/DOID_')) } } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?mondo <http://www.w3.org/2004/02/skos/core#exactMatch> ?doid . ?mondo <http://www.geneontology.org/formats/oboInOwl#hasDbXref> ?x . FILTER(STRSTARTS(STR(?x), 'UMLS:')) BIND(STRAFTER(STR(?x), 'UMLS:') AS ?cui) }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

### FUNCTION & PATHWAYS

**GO** (direct, QuickGO literal → `obo/GO_`): pankgraph×prokn(16970).

```sparql
SELECT (COUNT(DISTINCT ?go) AS ?n) WHERE {
  { SELECT DISTINCT ?go WHERE { GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?s <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?lit . FILTER(STRSTARTS(STR(?lit),'https://www.ebi.ac.uk/QuickGO/term/GO:')) } BIND(IRI(REPLACE(STR(?lit),'^.*/term/GO:','http://purl.obolibrary.org/obo/GO_')) AS ?go) } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?p ?pred ?go . }
}
```

**Reactome** (direct, R-HSA accession rewrite): gene-expression-atlas-okn×prokn(1068).

```sparql
SELECT (COUNT(DISTINCT ?proknReact) AS ?n) WHERE {
  { SELECT DISTINCT ?proknReact WHERE { GRAPH <https://purl.org/okn/frink/kg/gene-expression-atlas-okn> { ?s <http://purl.org/okn/wobd/enrichment_source> "GXA:Reactome" ; <https://w3id.org/biolink/vocab/object> ?gxaReact . FILTER(CONTAINS(STR(?gxaReact),'R-HSA-')) } BIND(IRI(CONCAT('https://identifiers.org/reactome/',REPLACE(STR(?gxaReact),'^.*/detail/',''))) AS ?proknReact) } }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?prot <http://purl.obolibrary.org/obo/RO_0000056> ?proknReact . }
}
```

### GENES

**Ensembl** (direct, literal/IRI + http/https rewrite — `ensembl/ENSG{n}`): biobricks-aopwiki×gene-expression-atlas-okn(1355), biobricks-aopwiki×spoke-okn(1385), gene-expression-atlas-okn×spoke-okn(15132), pankgraph×prokn(37835), pankgraph×spoke-okn(168).

```sparql
SELECT (COUNT(DISTINCT ?ens) AS ?n) WHERE {
  { SELECT DISTINCT ?lit WHERE { GRAPH <https://purl.org/okn/frink/kg/pankgraph> { ?s <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?lit . FILTER(STRSTARTS(STR(?lit),'https://www.ensembl.org/id/ENSG')) } } }
  BIND(IRI(STR(?lit)) AS ?ens)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?ens ?p ?o . }
}
```

**Entrez** (direct, ncbigene/gene rewrite): biobricks-aopwiki×rdkg(1193), biobricks-aopwiki×spoke-genelab(1472), digcfdekg×rdkg(8934), digcfdekg×spoke-genelab(19747), digcfdekg×spoke-okn(16052), rdkg×spoke-genelab(9034), rdkg×spoke-okn(8475), spoke-genelab×spoke-okn(16326).

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> { ?r ?p ?o . FILTER(STRSTARTS(STR(?r),'http://identifiers.org/ncbigene/')) BIND(?r AS ?src) }
  BIND(IRI(CONCAT('http://www.ncbi.nlm.nih.gov/gene/',REPLACE(STR(?src),'^.*/ncbigene/',''))) AS ?gene)
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?gene ?q ?r2 . }
}
```

**Entrez→HGNC** (bridged via wikidata P351→P354): digcfdekg×prokn(20783).

```sparql
SELECT (COUNT(DISTINCT ?h) AS ?n) WHERE {
  { SELECT DISTINCT ?g WHERE { GRAPH <https://purl.org/okn/frink/kg/digcfdekg> { ?g <https://purl.org/okn/frink/kg/digcfdekg/schema/geneToTrait> ?t . } } }
  BIND(REPLACE(STR(?g),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item <http://www.wikidata.org/prop/direct/P351> ?entrez ; <http://www.wikidata.org/prop/direct/P354> ?hgnc . }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
}
```

**HGNC→Entrez** (bridged via wikidata P354→P351): prokn×spoke-okn(16298). prokn carries HGNC on `rdf:subject`/`rdf:object`/`rdfs:seeAlso`/`HAS_MARKER_GENE`/`biolink:target_for`.

```sparql
SELECT (COUNT(DISTINCT ?gene) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?gene a <https://w3id.org/biolink/vocab/Gene> . }
  BIND(REPLACE(STR(?gene),'^.*/gene/','') AS ?entrez)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item <http://www.wikidata.org/prop/direct/P351> ?entrez ; <http://www.wikidata.org/prop/direct/P354> ?hgnc . }
  BIND(IRI(CONCAT('http://identifiers.org/hgnc/',?hgnc)) AS ?h)
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?x ?p ?h . }
}
```

### PROTEINS

**UniProt** (direct — `purl.uniprot.org/uniprot/{acc}`, no rewrite; biomarkerkg on `obo:OBCI_1000009`): biobricks-aopwiki×prokn(1805), biomarkerkg×biobricks-aopwiki(84), biomarkerkg×prokn(205), ncipidkg×prokn(12).

```sparql
SELECT (COUNT(DISTINCT ?up) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/biomarkerkg> { ?s <http://purl.obolibrary.org/obo/OBCI_1000009> ?up . FILTER(STRSTARTS(STR(?up),'http://purl.uniprot.org/uniprot/')) }
  GRAPH <https://purl.org/okn/frink/kg/prokn> { ?up ?p ?o . }
}
```

### GEOSPATIAL

**S2_L13** (direct — KWG `s2.level13` IRI; spatialkg types `S2Cell_Level13`, others link via `owl:sameAs`): fiokg×sawgraph(4712), fiokg×spatialkg(681045), hydrologykg×spatialkg(106138), sawgraph×spatialkg(88007), sockg×spatialkg(1069), sudokn×spatialkg(42560), ufokn×fiokg(2461), ufokn×spatialkg(97087).

```sparql
SELECT (COUNT(DISTINCT ?cell) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/fiokg> { ?f <http://www.w3.org/2002/07/owl#sameAs> ?cell . FILTER(STRSTARTS(STR(?cell),'http://stko-kwg.geog.ucsb.edu/lod/resource/s2.level13.')) }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?cell a <http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13> . }
}
```

**county_FIPS** (direct — KWG `administrativeRegion.USA.{FIPS5}`, `AdministrativeRegion_2`): fiokg×spatialkg(3031), fiokg×spoke-okn(3032), geoconnex×spatialkg(3114), geoconnex×spoke-okn(3184), nikg×spatialkg(2), nikg×spoke-okn(2), scales×spatialkg(3029), scales×spoke-okn(3096), spoke-okn×ruralkg(3196), spoke-okn×sockg(31), spoke-okn×spatialkg(3122), wildlifekn×spatialkg(63).

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  { SELECT DISTINCT ?fips WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . FILTER(REGEX(STR(?loc),'/location/[0-9]{5}$')) } BIND(REPLACE(STR(?loc),'^.*/location/([0-9]{5})$','$1') AS ?fips) } }
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a ?t . }
}
```

**state_FIPS** (direct — FIPS2, `AdministrativeRegion_1`): geoconnex×spatialkg(51), spoke-okn×sockg(18), spoke-okn×spatialkg(51), sudokn×spatialkg(51).

```sparql
SELECT (COUNT(DISTINCT ?fips) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc ?p ?o . FILTER(REGEX(STR(?loc),'/location/[0-9]{2}$')) }
  BIND(REPLACE(STR(?loc),'^.*/location/([0-9]{2})$','$1') AS ?fips)
  BIND(IRI(CONCAT('http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.',?fips)) AS ?reg)
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> . }
}
```

**KWG_county** (direct shared node IRI, `AdministrativeRegion_2`): sockg×spatialkg(62).

```sparql
SELECT (COUNT(DISTINCT ?reg) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/sockg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
  GRAPH <https://purl.org/okn/frink/kg/spatialkg> { ?reg a <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> . }
}
```

**ZIP5** (direct literal, bare 5-digit ZIP): spoke-okn×dreamkg(53), spoke-okn×ruralkg(4938), spoke-okn×sudokn(12329).

```sparql
SELECT (COUNT(DISTINCT ?zip) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?loc <http://www.w3.org/2000/01/rdf-schema#label> ?zip . FILTER(REGEX(STR(?loc),'/location/[A-Z]{2}-[0-9]+')) }
  GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/hasZipcodeValue> ?zip . }
}
```

### INDUSTRY & SUPPLY CHAIN

**NAICS** (direct, per-KG suffix normalization): fiokg×securechainkg(301), fiokg×sudokn(64), securechainkg×sudokn(35).

```sparql
SELECT (COUNT(DISTINCT ?code) AS ?n) WHERE {
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?a <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?sn . } BIND(REPLACE(STR(?sn),'^.*/naics-([0-9]+)\\.0-inst$','$1') AS ?code) } }
  { SELECT DISTINCT ?code WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier> ?dn . } BIND(REPLACE(STR(?dn),'^.*NAICS%20([0-9]+)-individual$','$1') AS ?code) } }
}
```

**SUDOKN_industry_sector** (direct, label normalization on `suppliesToIndustry`): securechainkg×sudokn(58).

```sparql
SELECT (COUNT(DISTINCT ?sec) AS ?n) WHERE {
  { SELECT DISTINCT ?sec WHERE { GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?a <http://asu.edu/semantics/SUDOKN/suppliesToIndustry> ?si . } BIND(LCASE(REPLACE(STR(?si),'^.*/SUDOKN/(.*)-inst$','$1')) AS ?sec) } }
  { SELECT DISTINCT ?sec WHERE { GRAPH <https://purl.org/okn/frink/kg/sudokn> { ?b <http://asu.edu/semantics/SUDOKN/suppliesToIndustry> ?di . } BIND(LCASE(REPLACE(REPLACE(STR(?di),'^.*/SUDOKN/(.*)-industry-individual$','$1'),'%20','')) AS ?sec) } }
}
```

**climatemodelskg Source IRI** (direct shared node IRI, `sc:dependsOn`): climatemodelskg×securechainkg(3).

```sparql
SELECT (COUNT(DISTINCT ?model) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/climatemodelskg> { ?model a <https://climatepub4kg.github.io/ontology#Source> . }
  GRAPH <https://purl.org/okn/frink/kg/securechainkg> { ?model <https://w3id.org/secure-chain/dependsOn> ?dep . }
}
```

### JUSTICE & PUBLIC SAFETY

**NIBRS_offense_category** (direct controlled-vocabulary literal): scales×ruralkg(37).

```sparql
PREFIX fbi: <http://fbi.gov/cjis/nibrs/2023.0/>
PREFIX rk: <http://sail.ua.edu/ruralkg/variable/>
SELECT (COUNT(DISTINCT ?off) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/scales> { ?ch fbi:OffenseUCRCode ?off . }
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> { ?ans rk:answerContent ?off . }
}
```

### SOCIAL DETERMINANTS & SERVICES

**MeSH→UMLS** (bridged via wikidata P486→P2892): spoke-okn×biohealth(3).

```sparql
SELECT (COUNT(DISTINCT ?bh) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s a <https://purl.org/okn/frink/kg/spoke-okn/schema/SDoH> ; <https://purl.org/okn/frink/kg/spoke-okn/schema/mesh_ids> ?meshIri . }
  BIND(REPLACE(STR(?meshIri),'^.*/mesh/','') AS ?meshId)
  GRAPH <https://purl.org/okn/frink/kg/wikidata> { ?item <http://www.wikidata.org/prop/direct/P486> ?meshId ; <http://www.wikidata.org/prop/direct/P2892> ?cui . }
  BIND(IRI(CONCAT('https://biohealthkg.proto-okn.net/kg/node/', ?cui)) AS ?bh)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh ?bp ?bo . }
}
```

**concept label SNOMED↔UMLS** (direct label bridge, strip SNOMED suffix): spoke-okn×biohealth(89).

```sparql
SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?s a <https://purl.org/okn/frink/kg/spoke-okn/schema/SDoH> ; <http://www.w3.org/2000/01/rdf-schema#label> ?sl . }
  BIND(IF(CONTAINS(?sl,' ('), STRBEFORE(?sl,' ('), STR(?sl)) AS ?clean)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?clean . }
}
```

**concept label social-service↔UMLS** (direct label bridge, first-letter cap): dreamkg×biohealth(14).

```sparql
SELECT (COUNT(DISTINCT ?aud) AS ?n) WHERE {
  { SELECT DISTINCT ?aud WHERE { GRAPH <https://purl.org/okn/frink/kg/dreamkg> { ?s <http://schema.org/audienceType> ?aud } } }
  BIND(CONCAT(UCASE(SUBSTR(?aud,1,1)), SUBSTR(?aud,2)) AS ?cap)
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?cap . }
}
```

### TAXONOMY (NCBITaxon hub through ubergraph)

Two-valued overlaps: **exact_id** (same NCBITaxon id both sides) and **clade membership** (`subClassOf*` closure, directional, often far larger). Key `obo/NCBITaxon_`. Id-matched pairs: biobricks-aopwiki×{gene-expression-atlas-okn,nde,sawgraph,spoke-genelab}, gene-expression-atlas-okn×{nde,sawgraph,spoke-genelab}, nde×{sawgraph,spoke-genelab,spoke-okn,wildlifekn}, sawgraph×{spoke-genelab,wildlifekn}, spoke-genelab×spoke-okn. Label-bridged (biohealth by scientific name, no NCBITaxon id): biohealth×{biobricks-aopwiki,gene-expression-atlas-okn,nde,sawgraph,spoke-genelab,spoke-okn}. Example spoke-genelab×spoke-okn: exact_id=2, clade(spoke-okn under spoke-genelab)=33313.

**Exact-id skeleton** (spoke-genelab×spoke-okn):

```sparql
SELECT (COUNT(DISTINCT ?t) AS ?shared) WHERE {
  { SELECT DISTINCT ?t WHERE { { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?_t1 <https://purl.org/okn/frink/kg/spoke-genelab/schema/taxonomy> ?_t2 . FILTER(STRSTARTS(STR(?_t2),'http://purl.obolibrary.org/obo/NCBITaxon_')) } BIND(IRI(STR(?_t2)) AS ?t) } UNION { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?_t3 a <https://purl.org/okn/frink/kg/spoke-genelab/schema/Organism> . } BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?_t3),'^.*/node/([0-9]+).*$','$1'))) AS ?t) } } }
  { SELECT DISTINCT ?t WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?_o a <https://w3id.org/biolink/vocab/OrganismTaxon> } BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?_o),'^.*/organism/([0-9]+).*$','$1'))) AS ?t) } }
}
```

**Clade-membership skeleton** (spoke-okn strains under spoke-genelab clades):

```sparql
SELECT (COUNT(DISTINCT ?desc) AS ?n) WHERE {
  { SELECT DISTINCT ?genus WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> { ?node a <https://purl.org/okn/frink/kg/spoke-genelab/schema/Organism> . } BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?node),'^.*/node/([0-9]+).*$','$1'))) AS ?genus) } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?desc <http://www.w3.org/2000/01/rdf-schema#subClassOf>* ?genus . }
  { SELECT DISTINCT ?desc WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?ot a <https://w3id.org/biolink/vocab/OrganismTaxon> } BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?ot),'^.*/organism/([0-9]+).*$','$1'))) AS ?desc) } }
}
```

**Label-bridged skeleton** (biohealth×spoke-okn by scientific name):

```sparql
SELECT (COUNT(DISTINCT ?taxon) AS ?n) WHERE {
  { SELECT DISTINCT ?taxon WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-okn> { ?ot a <https://w3id.org/biolink/vocab/OrganismTaxon> } BIND(IRI(CONCAT('http://purl.obolibrary.org/obo/NCBITaxon_',REPLACE(STR(?ot),'^.*/organism/([0-9]+).*$','$1'))) AS ?taxon) } }
  GRAPH <https://purl.org/okn/frink/kg/ubergraph> { ?taxon <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
  GRAPH <https://purl.org/okn/frink/kg/biohealth> { ?bh <http://www.w3.org/2000/01/rdf-schema#label> ?name . }
}
```

### NOTES

Bridged joins (ubergraph, wikidata) are federated 3-graph queries and heavier than direct joins. Complementary linkages (e.g. oard-kg↔prokn on MONDO + OMIM + Orphanet) should be UNIONed for complete coverage. IRI normalization matters: the same id commonly appears in 2–3 IRI/literal forms across KGs; each skeleton handles its case.

**Sources:** FRINK federation `list_crosswalks` / `get_join_strategy` / `taxon_overlap`, verified 2026-06-30 (taxonomy 2026-06-14).

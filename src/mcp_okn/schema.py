"""Schema discovery for Proto-OKN knowledge graphs.

Each KG's schema (classes, predicates, edge properties, node properties) comes from
its ``<kg>_entities.csv`` in ``metadata/void_entities``, which ships with the server.
``scripts/build_void_schema.py`` builds those files from each graph's VoID description
in ``okn-void``, or by querying the served graph when its VoID is stale. A KG with no
file is probed live on the federation endpoint for the distinct classes and
predicates in its named graph.

Set ``MCP_OKN_ENTITY_METADATA_BASE`` to a URL or directory of ``<kg>_entities.csv``
files to read those instead of the shipped files.

The shortnames are the ones used as federation named graphs
(``https://purl.org/okn/frink/kg/{shortname}``).
"""

from __future__ import annotations

import asyncio
import csv
import os
import re
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

from .bundled import metadata_dir
from .contrasts import (
    SPOKE_GENELAB_CONTRAST_GUIDANCE,
    SPOKE_GENELAB_CONTRAST_SNIPPET,
)
from .sparql import SparqlError, named_graph, run_sparql

#: Where the per-KG ``<kg>_entities.csv`` files live: the shipped copy of
#: ``metadata/void_entities``, built by ``scripts/build_void_schema.py``. The builder
#: counts a stale-VoID KG from the served graph, so every file describes the release
#: being served.
_VOID_ENTITIES = metadata_dir("void_entities")
ENTITY_METADATA_BASE = str(_VOID_ENTITIES) if _VOID_ENTITIES else ""

#: Optional override: a URL or local directory of ``<kg>_entities.csv`` files. When
#: set it replaces :data:`ENTITY_METADATA_BASE` entirely, and a KG the override lacks
#: is probed live.
ENTITY_METADATA_OVERRIDE = os.environ.get("MCP_OKN_ENTITY_METADATA_BASE", "").strip()


def schema_file_count() -> int | None:
    """How many ``<kg>_entities.csv`` files the schema source holds.

    ``None`` when the source is a URL (it cannot be listed). A deployment that lost
    the shipped files reports 0, and every KG's schema is then probed live, which is
    slow and less complete; ``get_server_info`` exposes the count so
    ``scripts/check_deployment.py`` can catch that.
    """
    base = ENTITY_METADATA_OVERRIDE or ENTITY_METADATA_BASE
    if base.startswith(("http://", "https://")):
        return None
    folder = Path(base) if base else None
    return len(list(folder.glob("*_entities.csv"))) if folder and folder.is_dir() else 0


_RDF_STATEMENT = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"

#: Source/target pairs listed per predicate besides the top one.
MAX_EXTRA_PAIRS = 3

#: Provenance / dataset-summary vocabularies (VOID and friends) that some upstream
#: ``*_entities.csv`` files now embed as schema rows. These describe the dataset
#: (triple counts, class/property partitions, last-updated timestamps) rather than
#: the KG's queryable *domain* schema, so surfacing them in ``get_schema`` would
#: mislead a client into writing SPARQL against ``void:triples`` and the like. We
#: expose that provenance properly via ``get_kg_version`` / the ``okn-void`` graph,
#: so drop these rows at the CSV-parsing layer — that keeps both ``get_schema`` and
#: the drift-check fingerprint (:mod:`scripts.check_payload_drift`) domain-only.
_PROVENANCE_NAMESPACES = (
    "http://rdfs.org/ns/void#",  # VOID
    "http://ldf.fi/void-ext#",  # VOID-ext
    "http://purl.org/pav/",  # PAV provenance (e.g. pav:lastUpdatedOn)
)
_PROVENANCE_URIS = frozenset(
    {
        "http://purl.org/dc/terms/modified",
        "https://research.bioinformatics.udel.edu/ProKN/rdf/topClassName",
    }
)


def _is_provenance_uri(uri: str) -> bool:
    """True for provenance/dataset-summary vocabulary (VOID, PAV, …).

    Such terms describe the dataset rather than its queryable domain schema, so
    they are filtered out of the returned schemas.
    """
    return uri in _PROVENANCE_URIS or uri.startswith(_PROVENANCE_NAMESPACES)


#: ncipidkg no longer has a deployment gap. Upstream commit 422b460 (2026-09-02)
#: realigned ``ncipidkg_entities.csv`` with the served graph: the uninstantiated
#: classes and absent predicates were dropped, and the SIO_010043 typing flaw and
#: ``owl:sameAs`` semantics are now documented in the CSV itself.
#:
#: THE EDGE-METADATA NAMESPACE MOVED, and an earlier version of this comment named
#: the wrong one. ncipidkg served placeholder ``http://example.org/okn/`` predicates
#: as recently as 2026-09-01; it now serves ``https://www.ndexbio.org/vocab/ncipid/``
#: (evidenceCount, evidenceUrl, inPathway, processType). The CSV tracks the new
#: namespace correctly, so ``get_schema`` is right — but any query written against
#: the old one returns ZERO ROWS rather than an error, which is how it hides. That
#: is exactly how the proteins07_q1 worked example broke: it went from 18 rows to 0
#: with no other change, and the substantive results were identical once repointed.
#: A live census on 2026-09-02 counts 21 distinct deployed predicates against the
#: CSV's 20 (the extra is ``rdf:type``), so the curated schema matches the graph.
#:
#: THE PATHWAY AXIS ARRIVED AFTERWARDS. On 2026-09-02 ``biolink:Pathway`` had 0
#: instances and both ``obo:RO_0000056`` and ``inPathway`` were absent, and this
#: note said so. The graph served on 2026-10-13 (v0.0.3) has all three — 207
#: pathways, 8,055 participation edges, 169,104 statement-to-pathway links — and the
#: CSV rebuilt for that release (upstream 36162dc) lists them; all 26 of its rows
#: are populated. Chemicals are also typed properly now (``obo:CHEBI_23367``, 44
#: nodes) instead of as ``sio:SIO_010043`` proteins.
SPOKE_OKN_GUIDANCE = """\
LOCATION KIND IS ON A MALFORMED PREDICATE (verified live 2026-10-16). Every
spoke-okn location (113,882 nodes under .../spoke-okn/location/) is typed
rdf:type <https://schema.org/AdministrativeArea>; WHAT KIND of place it is sits
only on the bare RDF namespace used as a predicate,
<http://www.w3.org/1999/02/22-rdf-syntax-ns#> (no local name - a mangled
rdf:type). Its values:
  https://schema.org/City                         58,441
  http://www.wikidata.org/entity/Q37447            42,724  (postal code / ZIP)
  .../spoke-okn/node/SubDivision                    5,402
  http://www.wikidata.org/entity/Q5284423           3,816  (division)
  http://www.wikidata.org/entity/Q28575             3,196  (county)
  https://schema.org/Country                          251
  https://schema.org/State                             52
So "which counties / states / cities" filters on that predicate; rdf:type alone
cannot tell a county from a ZIP code. Locations also carry rdfs:label and
spoke-okn schema properties state_fips, state_name, county_fips, city_fips.

THE schema.org KINDS ARE https. City, State and Country are stored as
https://schema.org/..., and this server rewrites a bracketed
<https://schema.org/...> IRI to http before sending it, so
`?loc <http://www.w3.org/1999/02/22-rdf-syntax-ns#> <https://schema.org/State>`
silently returns 0 rows. Build the IRI instead -
BIND(IRI(CONCAT("https://schema.org/", "State")) AS ?kind) - or compare
STR(?kind). The same applies to schema:AdministrativeArea in rdf:type. The
Wikidata kinds (http://www.wikidata.org/entity/...) are unaffected.\
"""

#: Companion snippet: counties of one state, via the malformed kind predicate.
#: Verified 2026-10-16: California returns 58 rows.
SPOKE_OKN_SNIPPET = """\
# spoke-okn counties in a state. The kind is on the bare rdf: namespace
# predicate, not rdf:type; Wikidata Q28575 = county. For City / State /
# Country use BIND(IRI(CONCAT("https://schema.org/", "State")) AS ?kind) and
# ?loc <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ?kind (https, see notes).
SELECT ?county ?name ?state_fips ?county_fips WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-okn> {
    ?county <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
              <http://www.wikidata.org/entity/Q28575> ;
            <https://purl.org/okn/frink/kg/spoke-okn/schema/state_name> "California" ;
            <http://www.w3.org/2000/01/rdf-schema#label> ?name ;
            <https://purl.org/okn/frink/kg/spoke-okn/schema/state_fips> ?state_fips ;
            <https://purl.org/okn/frink/kg/spoke-okn/schema/county_fips> ?county_fips .
  }
}
ORDER BY ?county_fips\
"""

PROKN_NEGATED_PREDICATES = (
    "https://w3id.org/biolink/vocab/actively_involved_in",
    "https://w3id.org/biolink/vocab/catalyzes",
    "http://purl.uniprot.org/core/partOf",
    "https://w3id.org/biolink/vocab/part_of",
    "https://w3id.org/biolink/vocab/colocalizes_with",
    "https://w3id.org/biolink/vocab/contributes_to",
    "https://w3id.org/biolink/vocab/acts_upstream_of_or_within",
    "https://w3id.org/biolink/vocab/active_in",
    "https://w3id.org/biolink/vocab/acts_upstream_of_or_within_negative_effect",
)

PROKN_GUIDANCE = """\
NEGATED GO ANNOTATIONS ARE ALSO STORED AS POSITIVE TRIPLES (verified live
2026-10-16). prokn holds 1,370 GO annotations with GO's NOT qualifier (e.g.
uniprot:P61106 is NOT partOf GO:0005929, ECO_IDA, UniProt). Each is a reified
rdf:Statement additionally typed
<https://www.w3.org/2002/07/owl#NegativePropertyAssertion> - AND each is also
asserted as a plain triple `?protein <pred> ?go`, indistinguishable from a
positive annotation. Affected predicates (negated / all direct triples):
  biolink:actively_involved_in       570 / 121,057
  biolink:catalyzes                  535 /  90,713
  uniprot core:partOf                212 /  77,072
  biolink:part_of                     19 /  14,571
  biolink:colocalizes_with            12 /     858
  biolink:contributes_to              12 /     933
  biolink:acts_upstream_of_or_within   6 /   2,433
  biolink:active_in                    3 /   5,196
  biolink:acts_upstream_of_or_within_negative_effect 1 / 11
For these, do NOT use the plain triple when correctness matters (GO enrichment,
"is protein X in compartment Y"): it returns the NOT annotations as positive.
Use the statement pattern and drop negated statements:
  FILTER NOT EXISTS { ?st rdf:type <https://www.w3.org/2002/07/owl#NegativePropertyAssertion> }
This overrides the pattern_guidance advice to prefer the direct triple, for
these predicates in prokn only. To LIST the negated annotations, use FILTER
EXISTS instead.

THE OWL IRIs ARE https. prokn writes OWL's namespace as https://www.w3.org/2002/07/owl#
(wrong scheme): NegativePropertyAssertion (1,370 statements), Class (1,436
nodes, mostly Bridge2AI cell-image crops .../ProKN/rdf/CellMedioid_...) and
annotatedProperty. The standard http form (owl:Class, PREFIX owl:
<http://www.w3.org/2002/07/owl#>) matches NOTHING here - write the https IRI
in full.\
"""

#: Companion snippet: a protein's GO annotations without the NOT ones.
#: Verified 2026-10-16: P61106 returns 232 rows and leaves out its NOT partOf
#: GO:0005929, which the plain partOf triples include.
PROKN_SNIPPET = """\
# prokn GO annotations of one protein, EXCLUDING GO NOT-qualified (negated)
# annotations, which are also present as plain ?protein <pred> ?go triples.
SELECT ?pred ?go WHERE {
  GRAPH <https://purl.org/okn/frink/kg/prokn> {
    ?st <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> <http://purl.uniprot.org/uniprot/P61106> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> ?pred ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?go .
    FILTER NOT EXISTS {
      ?st <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
          <https://www.w3.org/2002/07/owl#NegativePropertyAssertion>
    }
  }
}\
"""

#: Per-KG replacements for the one-line edge_properties ``usage`` note, where the
#: generic "use the direct triple" advice would give wrong answers.
_EDGE_USAGE_OVERRIDES: dict[str, dict[str, str]] = {
    "prokn": dict.fromkeys(
        PROKN_NEGATED_PREDICATES,
        "The direct triple ALSO holds GO NOT (negated) annotations: to exclude "
        "them use this template with FILTER NOT EXISTS { ?stmt rdf:type "
        "<https://www.w3.org/2002/07/owl#NegativePropertyAssertion> } (see "
        "usage_notes).",
    ),
}

NCIPIDKG_GUIDANCE = """\
IDENTIFIER AND JOIN NOTES (the schema matches the deployed graph as of
2026-10-13; these are the things it still does not tell you).

TWO UNIPROT LEGS, AND THEY ARE NOT THE SAME KIND OF THING. ncipidkg's own
sio:SIO_010043-typed <http://purl.uniprot.org/uniprot/{acc}> node IRIs (2,527)
ARE the entities - the things that hold a reified-statement role. owl:sameAs
(11,760 triples, 11,736 distinct objects) is an outward accession ALIAS TABLE
hung off those entities: secondary, isoform and merged-away accessions. Only 5
of the 11,736 alias objects ever play a statement role, so an alias is a ROUTE
to another graph, never a participant in this one.

WHICH LEG YOU WANT DEPENDS ON THE UNIT OF THE ANSWER.
  * Counting or listing the IDENTIFIERS two graphs SHARE - UNION both legs.
    Against prokn, sameAs matches 1,979 accessions and the node-IRI leg 537, of
    which 514 are unreachable via sameAs: 2,493 together (crosswalk G2). Either
    leg alone understates that overlap by about a quarter.
  * Answering about ncipidkg PROTEINS - who interacts, who participates, one row
    per protein - the PARTICIPANT is the answer's identity. Bind it from
    rdf:subject / rdf:object (or the typed node IRI), keep THAT in the SELECT,
    and use owl:sameAs only as the join key, aggregating the far graph back onto
    the participant (the snippet below). Projecting the alias instead swaps a
    merged-away accession in for the protein and multiplies the rows: the 462
    participants of GO_0016567 ubiquitination statements expand to 2,382 alias
    accessions.
  Whether to follow the alias at all is a modelling CHOICE, not a correctness
  rule - it attributes a canonical entry's data to a participant recorded under
  a different accession. It is often what you want here, because ncipidkg
  records many participants under TrEMBL accessions: of those 462 participants,
  73 carry prokn sequence variants under their own accession and a further 319
  only under an alias. Say which reading you took.

NON-CANONICAL UNIPROT ACCESSIONS. Four accession strings carry a GenBank-style
sequence-version suffix that UniProt IRIs never use: P29353.1 (with owl:sameAs
to P29353.2 and P29353.3) labelled SHC1, and Q05397.1 labelled PTK2. All are
ORPHANS - no RO_* edges, no reified-statement roles - and the canonical P29353 /
Q05397 appear NOWHERE in the graph. The live SHC1 and PTK2 data hangs off
unreviewed TrEMBL accessions instead, B5BU19 (321 statement roles) and B4E2N6
(760), so a join on the reviewed Swiss-Prot accession silently misses two major
signalling hubs the graph does contain.

NAMED PATHWAYS ARE LIVE (new in v0.0.3; absent before, when this note said the
graph had no pathway axis). 207 biolink:Pathway nodes
<https://www.ndexbio.org/identifiers/pathway/{slug}> carry the NCI-PID pathway
name on rdfs:label, version suffix included ("Direct p53 effectors (v2.0)").
Two routes reach them, and they answer different questions:
  * MEMBERSHIP - ?participant obo:RO_0000056 ?pathway (8,055 triples, 2,608
    participants: proteins, gene families, chemicals, ncRNAs). "Which pathways
    is TP53 in?" is this edge, from the node labelled "TP53".
  * CONTEXT OF AN INTERACTION - ?statement ncipid:inPathway ?pathway (169,104
    triples on 80,819 of the 83,704 reified INDRA statements, about two pathways
    per statement). Use it to scope the interaction topology (obo:RO_0002436 /
    RO_0002578 / RO_0002629 / RO_0002630 / RO_0002211) to one pathway.
The pathway IRIs are ndexbio slugs with no Reactome, GO or WikiPathways
cross-reference, so they join another graph only through their participants
(UniProt, above), never pathway-to-pathway. Match a pathway by its label.\
"""

#: Companion snippet: the entity-preserving UniProt join. The thing most callers
#: get wrong on this KG is projecting the owl:sameAs alias as if it were the
#: protein; ``owl:sameAs?`` (zero-or-one) keeps the participant as the identity
#: and folds the alias route into the same key. Do NOT write this as
#: ``{ BIND(?protein AS ?key) } UNION { ?protein owl:sameAs ?key }`` - ?protein
#: is out of scope inside the BIND branch, so ?key comes back unbound and the
#: far-graph pattern scans the whole relation.
NCIPIDKG_SNIPPET = """\
# ncipidkg UniProt, per-protein: the PARTICIPANT is the answer's identity and the
# owl:sameAs alias is only the join key. SELECT ?protein, aggregate onto it.
SELECT ?symbol ?protein (COUNT(DISTINCT ?far) AS ?n) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/ncipidkg> {
    ?st <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>|
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?protein .
    ?protein <http://www.w3.org/2000/01/rdf-schema#label> ?symbol .
    FILTER(STRSTARTS(STR(?protein),'http://purl.uniprot.org/uniprot/'))
    # zero-or-one: ?key is the participant itself, or one of its aliases.
    # To answer on the participant's OWN accession only, drop this line and
    # join the other graph on ?protein directly.
    ?protein <http://www.w3.org/2002/07/owl#sameAs>? ?key .
  }
  GRAPH <OTHER_KG> { ?key <SOME_PREDICATE> ?far . }
}
GROUP BY ?symbol ?protein
# For the different question "how many accessions do the two graphs SHARE?",
# count the keys instead: UNION the sameAs leg and the SIO_010043 node-IRI leg
# (crosswalk G2's skeleton_query).\
"""

BABEL_GUIDANCE = """\
IDENTIFIER-MAPPING BRIDGE (verified live 2026-09-26). babel is the Translator
Babel equivalence dataset: it groups identifiers from different vocabularies
that name the same concept into a CLIQUE, and picks one member as the clique's
preferred id. It has no domain data of its own - use it only as the middle hop
of a join between two other KGs that key the same concept on different schemes.

SHAPE. Every member points at its clique's preferred id with skos:exactMatch
(the preferred id points at itself). Only the preferred id carries rdfs:label
and biolink:category. So mapping an id ?a to scheme B is two hops through the
shared preferred id: ?a skos:exactMatch ?pref . ?b skos:exactMatch ?pref .
Gene cliques (NCBIGene, Ensembl, HGNC) and protein cliques (UniProt, PR) are
SEPARATE - babel does not map a gene to its protein.

IRI FORMS babel uses (rewrite your KG's ids to these, and back):
  NCBIGene   http://identifiers.org/ncbigene/{n}
  Ensembl    http://identifiers.org/ensembl/{ENSG...}
  HGNC       http://identifiers.org/hgnc/{n}            (numeric, no "HGNC:")
  UniProt    http://purl.uniprot.org/uniprot/{acc}
  OBO terms  http://purl.obolibrary.org/obo/{MONDO|DOID|HP|NCIT|CHEBI}_{n}
  OMIM       http://purl.obolibrary.org/obo/OMIM_{n}    (NOT omim.org/entry/)
  MeSH       http://id.nlm.nih.gov/mesh/{D...}
  UMLS       http://identifiers.org/umls/{C...}
  MedGen     https://www.ncbi.nlm.nih.gov/medgen/{n}
  SNOMED CT  http://snomed.info/id/{n}
  chemicals  http://identifiers.org/{drugbank|chembl.compound|pubchem.compound|
             cas|inchikey|unii|hmdb|kegg.compound}/{id}
Probe one known id before relying on a scheme not listed here.

QUERY SHAPE - OR IT TIMES OUT. babel is far too large for a flat two-hop
join. Nest the hops (see the snippet): resolve ?pref for YOUR KG's ids in a
SELECT DISTINCT subquery, wrap the second hop (?target skos:exactMatch ?pref)
in its own SELECT DISTINCT subquery around that, and only then test the target
scheme with a FILTER outside both. Left in the same group as the second hop,
the FILTER can be planned first and scans the whole relation; that already
fails at ~9k input ids. A flat join, an OPTIONAL on ?pref, or any COUNT over
the whole graph returns HTTP 429, and so does an input set in the hundreds of
thousands (biobricks-ice's ~200k CAS numbers) however the query is shaped.

AN ID CAN SIT IN TWO CLIQUES. babel stores more than one grouping side by
side - e.g. DrugBank DB00002 belongs to a UMLS-preferred clique AND a
UNII-preferred one - so one input id can fan out to several preferred ids and
several target ids. Your KG's node is the answer's identity and the babel id is
only the join key: COUNT DISTINCT the endpoint entities, never the cliques.

babel also holds PubMed nodes whose rdfs:label is a lone byte-order mark;
patterns scoped to skos:exactMatch never see them. Verified example: crosswalk
DB2 (rdkg DrugBank -> ChEMBL -> prokn, 1,816 drugs).\
"""

#: Companion snippet: the staged two-hop lookup. The inner subquery binds the
#: preferred id from the small side; the outer one keeps the second
#: skos:exactMatch hop apart from the scheme FILTER, so the planner cannot run
#: the FILTER against the whole relation first.
BABEL_SNIPPET = """\
# Map YOUR KG's ids to another scheme through babel (here DrugBank -> ChEMBL).
SELECT (COUNT(DISTINCT ?mine) AS ?n) WHERE {
  { SELECT DISTINCT ?mine ?target WHERE {
    { SELECT DISTINCT ?mine ?pref WHERE {
        GRAPH <https://purl.org/okn/frink/kg/YOUR_KG> { ?mine a <YOUR_CLASS> }
        # rewrite ?mine to babel's IRI form here if it differs
        GRAPH <https://purl.org/okn/frink/kg/babel> {
          ?mine <http://www.w3.org/2004/02/skos/core#exactMatch> ?pref } } }
    GRAPH <https://purl.org/okn/frink/kg/babel> {
      ?target <http://www.w3.org/2004/02/skos/core#exactMatch> ?pref } } }
  FILTER(STRSTARTS(STR(?target), 'http://identifiers.org/chembl.compound/'))
  # rewrite ?target to the other KG's IRI form, then join it:
  BIND(IRI(CONCAT('https://www.ebi.ac.uk/chembl/explore/compound/',
                  STRAFTER(STR(?target), 'chembl.compound/'))) AS ?theirs)
  GRAPH <https://purl.org/okn/frink/kg/OTHER_KG> { ?theirs ?p ?o }
}\
"""

BIO101_GUIDANCE = """\
ONTOLOGY, NOT INSTANCE DATA (verified live 2026-10-05). KB Bio 101 encodes an
introductory biology textbook as OWL2 axioms: every concept (aura:Mitochondrion,
aura:Glycolysis, aura:Ribosome) is an owl:Class. The aura relations in this
schema (has-part, agent, raw-material, result, site, subevent, has-function,
...) are NEVER asserted as direct triples - `?s aura:has-part ?o` returns ZERO
rows. They occur only as owl:onProperty of anonymous owl:Restriction nodes.

READING A CONCEPT. A concept's axioms hang off rdfs:subClassOf, usually through
an anonymous owl:Class whose owl:intersectionOf RDF list holds its named
parent(s) and its restrictions; the lists nest. Walk them with the path
  rdfs:subClassOf/(owl:intersectionOf/rdf:rest*/rdf:first)*
then keep IRIs (named parents) or nodes with owl:onProperty (restrictions).
A restriction's filler is on owl:someValuesFrom, owl:onClass (with a
qualified cardinality) or owl:hasValue, and is itself usually an intersection:
follow (owl:intersectionOf/rdf:rest*/rdf:first)* from it to its classes.

ONE FILLER, SEVERAL CLASSES. A filler node is conjoined with all its types
(e.g. Glucose & Monosaccharide & Aldose & Chemical-Entity), so group the
classes PER RESTRICTION (see the snippet) - listing them flat turns one raw
material into six. The most specific class names the slot. The same node can
also appear under several restrictions (existential plus cardinality), so
expect repeated rows; count distinct specific classes, not restriction rows.

aura:ID-N CLASSES ARE BOOKKEEPING. ~21,000 aura:ID-N classes mark shared nodes
of a concept's prototype graph (two fillers with the same ID-N are the same
node). Exclude them with FILTER(!STRSTARTS(STR(?x),
"http://www.projecthalo.com/aura#ID-")), or join on them to follow
co-references.

FINDING A CONCEPT. There is no rdfs:label: concepts are named only by their
IRI local name (hyphenated, e.g. aura:Citric-Acid-Cycle-In-Eukaryote,
aura:NAD-Plus, aura:MRNA), and aura:concept2words is declared but unpopulated.
Match on STR(?c) or on the textbook definition in aura:user-description
(present on 5,722 concepts).

NO EXTERNAL IDENTIFIERS - JOIN BY NAME. Nothing in the graph is outside the
aura:, RDF, RDFS or OWL namespaces (no GO/CHEBI/UBERON ids, no xrefs, no
sameAs), so bio101 joins other KGs only through the concept NAME: hyphens to
spaces, matched as a bound literal against ubergraph rdfs:label /
oboInOwl:hasExactSynonym (GO, UBERON, CL, MONDO, CHEBI) or biohealth's UMLS
names. Call get_join_strategy("bio101", <kg>) for the verified recipes
(crosswalks KB1-KB7). Names are homonym-prone (Lens is an optical device, not
the eye lens), so scope by bio101's class hierarchy as those recipes do.\
"""

#: Companion snippet: what a concept is made of / takes in / produces, one row
#: per restriction with the filler's classes grouped. Verified 2026-10-05:
#: Glycolysis returns 27 rows in ~4s (raw-material Glucose, ADP, NAD-Plus;
#: result ATP, Pyruvate, NADH; two subevent phases; site Cytosol).
BIO101_SNIPPET = """\
# Every relation axiom on one concept (swap aura:Glycolysis for any concept).
PREFIX aura: <http://www.projecthalo.com/aura#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?relation
       (GROUP_CONCAT(DISTINCT STRAFTER(STR(?cls), "#"); separator=" & ") AS ?filler)
WHERE { GRAPH <https://purl.org/okn/frink/kg/bio101> {
  aura:Glycolysis rdfs:subClassOf/(owl:intersectionOf/rdf:rest*/rdf:first)* ?r .
  ?r owl:onProperty ?relation .
  { ?r owl:someValuesFrom ?f } UNION { ?r owl:onClass ?f } UNION { ?r owl:hasValue ?f }
  ?f (owl:intersectionOf/rdf:rest*/rdf:first)* ?cls .
  FILTER(isIRI(?cls) && !STRSTARTS(STR(?cls), "http://www.projecthalo.com/aura#ID-"))
} }
GROUP BY ?r ?relation
ORDER BY ?relation ?filler
# Named parents only: keep the path, drop the other lines, and FILTER
# isIRI(?r) with the same aura#ID- exclusion.\
"""

#: Query-time rules for ``glygenkg`` (GlyGen: human protein glycosylation). The
#: graph reads like a protein KG but its central class is a glycosylation RECORD,
#: and nothing links a record to its protein. Verified live 2026-10-13.
GLYGENKG_GUIDANCE = """\
A gly:Glycoprotein IS A RECORD, NOT A PROTEIN. Each of the 74,722
gly:Glycoprotein nodes is one reported glycosylation observation (one paper,
at most one site) for one of 8,112 human proteins. Counting gly:Glycoprotein
nodes counts observations; count DISTINCT gly:has_pro_entry values to count
glycoproteins.

RECORD -> PROTEIN NEEDS AN IRI REWRITE. No triple connects a record to its
up:Protein node. The record's only protein key is gly:has_pro_entry, an untyped
Protein Ontology IRI http://purl.obolibrary.org/obo/PR_<accession>; swap that
prefix for http://purl.uniprot.org/uniprot/ to get the up:Protein IRI (all
8,112 resolve), which carries the name, mnemonic, gene (up:encodedBy) and
organism. Do not use up:sequence for this: on a record it points to an isoform
IRI that is untyped for 90% of records.

TWO FALDO NAMESPACES. Glycosylation-site coordinates use
http://www.biohackathon.org/resource/faldo# (WITH www); gene-locus coordinates
use the standard http://biohackathon.org/resource/faldo# (no www). The wrong
prefix returns 0 rows without an error.

SITE AND GLYCAN. record -gco:glycosylated_at-> site -faldo:location-> position
node, which holds faldo:position (1-based residue number on the record's
isoform) and glycan:has_amino_acid (IRI local name Asn, Ser, Thr ...; a few use
one-letter N, S, T). 7,212 records have no site, and 4,778 sites have no
glycan. A glycan is http://glygen.org/glycan/<GlyTouCan accession>; the graph
holds no structure, mass or composition property, only an rdfs:label such as
"Hex5HexNAc4 (N-linked, Biantennary)". Read N-linked or O-linked from that
label (923 and 89 of the 1,248 glycans say so; the rest carry neither word) or
from the residue. For 180 glycans, biobricks-pubchem-annotations supplies the
mass, WURCS structure, motifs and the organisms each is reported in (GT1).

OTHER SITE DATA IS UNTYPED AND PARTIAL. SNVs (7,482, with gly:glycoeffect on
3,969), phosphorylation sites (302) and a second glycosylation-site annotation
(102, on the misspelled predicate gco:glycoylationsite) hang off untyped nodes
reached through gly:has_site -> www-faldo Region; one region per isoform, so
they are a sample. gly:keywords says only "disease", "germline", "cancer",
"somatic" or "ebi": no disease is named anywhere in the graph and there is no
dbSNP rsID.

JOIN KEYS. All human (one taxon, NCBITaxon_9606). UniProt: the up:Protein node
IRI. Ensembl: the gly:hasLocus object http://rdf.ebi.ac.uk/resource/ensembl/
<ENSG>, a form no other graph uses, so rebuild the partner's form from the
bare id. PubMed: the id is inside the evidence IRI
http://glygen.org/evidence/PubMed_<PMID>. GlyTouCan: inside the glycan IRI;
biobricks-pubchem-annotations holds it as a plain rdf:value string.
Call get_join_strategy("glygenkg", <kg>) for the verified recipe before
writing a cross-graph query.\
"""

#: Companion snippet: every glycosylation site of one protein with its residue,
#: glycans and supporting papers. Verified 2026-10-13: P02743 (APCS) returns
#: Asn51 with 16 glycans from 4 papers and Thr195 with one O-linked glycan.
GLYGENKG_SNIPPET = """\
# Glycosylation sites of one protein (swap the UniProt accession).
PREFIX gly:    <https://sparql.glygen.org/ontology/>
PREFIX gco:    <http://purl.jp/bio/12/glyco/conjugate#>
PREFIX glycan: <http://purl.jp/bio/12/glyco/glycan#>
PREFIX faldo:  <http://www.biohackathon.org/resource/faldo#>
PREFIX up:     <http://purl.uniprot.org/core/>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>
SELECT ?symbol ?position ?aa (COUNT(DISTINCT ?glycan) AS ?glycans)
       (COUNT(DISTINCT ?ev) AS ?papers) (SAMPLE(?glabel) AS ?example_glycan)
WHERE { GRAPH <https://purl.org/okn/frink/kg/glygenkg> {
  VALUES ?protein { <http://purl.uniprot.org/uniprot/P02743> }
  ?protein up:encodedBy/skos:prefLabel ?symbol .
  # record -> protein: rewrite the UniProt IRI to the record's PR_ key
  BIND(IRI(REPLACE(STR(?protein), "http://purl.uniprot.org/uniprot/",
                   "http://purl.obolibrary.org/obo/PR_")) AS ?pr)
  ?rec gly:has_pro_entry ?pr ; glycan:has_evidence ?ev ;
       gco:glycosylated_at ?site .
  ?site faldo:location ?loc .
  ?loc faldo:position ?position ; glycan:has_amino_acid ?aaNode .
  BIND(REPLACE(STR(?aaNode), "^.*/", "") AS ?aa)
  OPTIONAL { ?site gco:has_saccharide ?glycan .
             OPTIONAL { ?glycan rdfs:label ?glabel } }
} }
GROUP BY ?symbol ?position ?aa
ORDER BY ?position
# The PMID is STRAFTER(STR(?ev), "PubMed_"); the GlyTouCan accession is
# REPLACE(STR(?glycan), "^.*/", "").\
"""

RDKG_GUIDANCE = """\
biolink:subclass_of IS MATERIALIZED TRANSITIVELY (verified live 2026-11-09).
Every disease links to EVERY MONDO ancestor, not just its parent: 1,832
diseases carry `bl:subclass_of <MONDO_0002081>` (musculoskeletal system
disorder) directly, and SLE (MONDO_0007915) links to all 7 of its MONDO
ancestors. There is no reflexive edge (a term is not subclass_of itself).
So:
  - `?d bl:subclass_of <X>` already means "a descendant of X" - no `*` path
    needed, and adding one only repeats rows. Add X itself if you want it.
  - "Diseases rdkg links to X", "using X exactly" or "not expanded" means
    edges that name X itself (has_phenotype, related_to, treats, ...), NOT
    subclass_of: reading the subclass_of rows answers the expanded question.
  - Parent/child structure (immediate parent, depth) is not recoverable
    here; use ubergraph's non-transitive rdfs:subClassOf for that.
  - The subjects include rdaccelerate disease groups
    (https://rdaccelerate.org/resource/MONDO_GROUPED_...) besides MONDO terms:
    104 of the 1,832 under MONDO_0002081. Say which you count; keep MONDO only
    with FILTER(STRSTARTS(STR(?d), "http://purl.obolibrary.org/obo/MONDO_")).

biolink:has_phenotype IS ALSO STORED IN REVERSE. Besides disease ->
phenotype (328,805 edges) rdkg holds 151,304 phenotype -> disease edges
(subject an HP term), and every one of them mirrors a forward edge. Match
the forward direction only (disease as subject, HP term as object): it is
complete, and an undirected pattern or a UNION of both directions counts a
mirrored pair twice.\
"""

#: Companion snippet: the diseases under a category, without a property path.
RDKG_SNIPPET = """\
# rdkg diseases under musculoskeletal system disorder and their phenotype
# counts. subclass_of is already transitive: no `*`, one hop reaches every
# descendant. has_phenotype is read forward only (disease -> HP). The FILTER
# keeps MONDO terms and drops rdaccelerate's MONDO_GROUPED_ disease groups.
PREFIX bl: <https://w3id.org/biolink/vocab/>
SELECT ?disease (COUNT(DISTINCT ?hp) AS ?phenotypes) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/rdkg> {
    ?disease bl:subclass_of <http://purl.obolibrary.org/obo/MONDO_0002081> ;
             bl:has_phenotype ?hp .
  }
  FILTER(STRSTARTS(STR(?disease), "http://purl.obolibrary.org/obo/MONDO_"))
} GROUP BY ?disease ORDER BY DESC(?phenotypes) LIMIT 20\
"""

#: Per-KG usage notes surfaced on ``get_schema`` (attached by the tool wrapper in
#: :mod:`mcp_okn.tools.schema_tools`), delivered exactly when a client is about to
#: write SPARQL for that KG. Only KGs with domain rules that the schema alone does
#: not convey are listed.
_KG_USAGE_NOTES: dict[str, dict[str, str]] = {
    "babel": {
        "title": "Identifier-mapping notes",
        "guidance": BABEL_GUIDANCE,
        "query_snippet": BABEL_SNIPPET,
    },
    "bio101": {
        "title": "Ontology-reading notes",
        "guidance": BIO101_GUIDANCE,
        "query_snippet": BIO101_SNIPPET,
    },
    "glygenkg": {
        "title": "Glycosylation-record notes",
        "guidance": GLYGENKG_GUIDANCE,
        "query_snippet": GLYGENKG_SNIPPET,
    },
    "spoke-genelab": {
        "guidance": SPOKE_GENELAB_CONTRAST_GUIDANCE,
        "query_snippet": SPOKE_GENELAB_CONTRAST_SNIPPET,
    },
    "prokn": {
        "title": "Negated GO annotation notes",
        "guidance": PROKN_GUIDANCE,
        "query_snippet": PROKN_SNIPPET,
    },
    "spoke-okn": {
        "title": "Location-kind notes",
        "guidance": SPOKE_OKN_GUIDANCE,
        "query_snippet": SPOKE_OKN_SNIPPET,
    },
    "rdkg": {
        "title": "Disease-hierarchy notes",
        "guidance": RDKG_GUIDANCE,
        "query_snippet": RDKG_SNIPPET,
    },
    "ncipidkg": {
        "guidance": NCIPIDKG_GUIDANCE,
        "query_snippet": NCIPIDKG_SNIPPET,
    },
}


def usage_notes(shortname: str) -> dict[str, str] | None:
    """Return curated usage notes for a KG, or None if it has none."""
    return _KG_USAGE_NOTES.get(shortname)


#: Schema namespace template used inside generated edge-property templates.
_SCHEMA_NS = "https://purl.org/okn/frink/kg/{shortname}/schema/"

#: KGs too large to enumerate a schema for via brute-force SPARQL probing. `wikidata`
#: was measured: its probe spends ~62s hitting the endpoint's operation timeout twice
#: and learns nothing, so the caller is better served by the message below immediately.
#: `babel` is the same size class (even a COUNT(*) over it exceeds the endpoint's
#: operation limit), and its one-predicate shape is fully described by its usage notes.
_TOO_LARGE = {"babel", "ubergraph", "wikidata"}

#: Mermaid `style` declarations distinguishing the two kinds of class box. Node
#: (entity) classes are light blue; edge (relationship) classes are orange. The
#: per-class `style` statement is the form that actually renders fills in
#: `classDiagram` (a `classDef` + `:::` assignment parses but emits no fill in
#: current Mermaid).
_NODE_CLASS_STYLE = "fill:#BBDEFB,stroke:#1565C0,color:#000"
_EDGE_CLASS_STYLE = "fill:#FFE0B2,stroke:#E65100,color:#000"

# Process-lifetime cache of parsed entity metadata, keyed by shortname.
_metadata_cache: dict[str, dict[str, dict[str, Any]]] = {}


def parse_entity_metadata(content: str) -> dict[str, dict[str, Any]]:
    """Parse an ``*_entities.csv`` into ``{uri: {label, description, type, …}}``.

    Reads both layouts. The curated proto-okn files have one row per URI and types
    Class / Predicate / EdgeProperty / NodeProperty. The VoID-built files add a
    ``Triples`` column and repeat a predicate once per (source, target) pair; those
    rows are collected into ``pairs``. The primary pair (``source_class`` /
    ``target_class``) is the largest when counts exist; otherwise it is the LAST row,
    as the previous last-row-wins read chose, and the others follow in file order.
    Curated files repeat URIs too (one row per domain/range, e.g. 47 in
    climatemodelskg); that read kept only one of them.

    One URI can also carry several kinds: scales' ``jxdm#Arrest`` is a Class and a
    Predicate, wildlifekn's ``date`` an EdgeProperty and a NodeProperty. The first
    kind seen is the entry; the others ride along in its ``also`` list, so neither
    is lost (the old read kept only the last row, dropping the Class and erasing
    ``date``'s edge parent).

    A row with ``EdgePropertyOf`` is an edge property when its Type says so or when
    it sits on a reified statement (SourceClass ``rdf:Statement`` or empty) — the
    VoID files, and several curated ones (pankgraph, ncipidkg, prokn), type those
    Predicate and name the parent by IRI. oard-kg's rows name a result-node class
    instead: they are plain properties of that node, with no ``rdf:predicate`` for
    a reification template to match, so they stay predicates. Parents accumulate
    semicolon-separated and deduplicated.
    """
    by_uri: dict[str, dict[str, dict[str, Any]]] = {}
    for row in csv.DictReader(StringIO(content)):
        uri = (row.get("URI") or "").strip()
        if not uri or _is_provenance_uri(uri):
            continue
        edge_property_of = (row.get("EdgePropertyOf") or "").strip()
        source = (row.get("SourceClass") or "").strip()
        target = (row.get("TargetClass") or "").strip()
        row_type = (row.get("Type") or "").strip()
        if edge_property_of and source not in ("", _RDF_STATEMENT):
            if row_type.lower() != "edgeproperty":
                edge_property_of = ""
        elif edge_property_of:
            row_type = "EdgeProperty"
        raw_triples = (row.get("Triples") or "").strip()
        triples = int(raw_triples) if raw_triples.isdigit() else None
        label = (row.get("Label") or "").strip()
        description = (row.get("Description") or "").strip()
        patterns = [p for p in (row.get("Pattern") or "").strip().split(";") if p]

        kinds = by_uri.setdefault(uri, {})
        entry = kinds.get(row_type.lower())
        if entry is None:
            entry = kinds[row_type.lower()] = {
                "label": label,
                "description": description,
                "type": row_type,
                "edge_property_of": "",
                "source_class": source,
                "target_class": target,
                "pairs": [],
                "patterns": [],
            }
        elif not edge_property_of:
            # Last row wins, as before; a repeated edge-property row only adds a
            # parent (its per-relationship description is not the property's own).
            entry["label"] = label or entry["label"]
            entry["description"] = description or entry["description"]
        if edge_property_of:
            # A single edge-property URI can belong to several relationships
            # (e.g. adj_p_value on both EXPRESSION and ABUNDANCE). Accumulate
            # the parents semicolon-separated so the join below finds them all.
            parents = [p for p in entry["edge_property_of"].split(";") if p]
            if edge_property_of not in parents:
                parents.append(edge_property_of)
            entry["edge_property_of"] = ";".join(parents)
        if source or target or triples is not None:
            entry["pairs"].append((source, target, triples))
        entry["patterns"] += [p for p in patterns if p not in entry["patterns"]]

    metadata: dict[str, dict[str, Any]] = {}
    for uri, kinds in by_uri.items():
        entries = list(kinds.values())
        for entry in entries:
            _set_primary_pair(entry)
        metadata[uri] = entries[0]
        if len(entries) > 1:
            entries[0]["also"] = entries[1:]
    return metadata


#: Canonical order of ``Pattern`` values (see ``void_schema.PATTERNS``).
_PATTERN_ORDER = ("direct", "reified", "axiom", "declared")


def _set_primary_pair(entry: dict[str, Any]) -> None:
    """Order ``pairs`` primary-first and copy the primary into source/target.

    Also joins the entry's ``Pattern`` values across its rows (``direct;reified``).
    """
    found = entry.pop("patterns", [])
    entry["pattern"] = ";".join(
        [p for p in _PATTERN_ORDER if p in found]
        + [p for p in found if p not in _PATTERN_ORDER]
    )
    pairs = entry["pairs"]
    if not pairs:
        entry["triples"] = None
        return
    counts = [n for _s, _t, n in pairs]
    if None in counts:
        entry["triples"] = None
        pairs.insert(0, pairs.pop())
    else:
        entry["triples"] = sum(c or 0 for c in counts)
        pairs.sort(key=lambda p: -(p[2] or 0))
    entry["source_class"], entry["target_class"] = pairs[0][0], pairs[0][1]


async def _read_csv(base: str, shortname: str, client: httpx.AsyncClient) -> str | None:
    """One ``<kg>_entities.csv`` from a URL base or a local directory."""
    name = f"{shortname}_entities.csv"
    if not base.startswith(("http://", "https://")):
        path = Path(base) / name
        return path.read_text() if path.exists() else None
    try:
        resp = await client.get(f"{base}/{name}")
    except httpx.HTTPError:
        return None
    return resp.text if resp.status_code == 200 else None


#: The base each cached KG's metadata was loaded from.
_metadata_source: dict[str, str] = {}


def metadata_source(shortname: str) -> str | None:
    """Where :func:`fetch_entity_metadata` loaded a KG's metadata from, if anywhere."""
    return _metadata_source.get(shortname)


async def fetch_entity_metadata(
    shortname: str,
    client: httpx.AsyncClient | None = None,
    refresh: bool = False,
    override: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Fetch and parse the entity metadata CSV for a KG (cached).

    Reads :data:`ENTITY_METADATA_OVERRIDE` (or ``override``) when set, else the
    shipped VoID-built file — never both. Returns an empty dict when the source lacks
    the KG (the caller then falls back to probing). See
    :func:`parse_entity_metadata`.
    """
    if shortname in _metadata_cache and not refresh:
        return _metadata_cache[shortname]

    override = ENTITY_METADATA_OVERRIDE if override is None else override
    owns = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
    content, used = None, None
    try:
        for base in [b for b in [override or ENTITY_METADATA_BASE] if b]:
            content = await _read_csv(base, shortname, client)
            if content is not None:
                used = base
                break
    finally:
        if owns:
            await client.aclose()

    metadata = parse_entity_metadata(content) if content is not None else {}
    _metadata_cache[shortname] = metadata
    if used:
        _metadata_source[shortname] = used
    else:
        _metadata_source.pop(shortname, None)
    return metadata


def _class_word(cls: str) -> str:
    """A class's local name when it is an IRI, else the label as given."""
    return _local_name(cls) if cls.startswith(("http://", "https://")) else cls


def _generate_query_template(
    shortname: str,
    relationship_label: str,
    source_class: str,
    target_class: str,
    properties: list[dict[str, Any]],
    relationship_uri: str = "",
) -> str:
    """Generate a SPARQL template for a reified relationship with edge properties.

    Each edge property is wrapped in its own OPTIONAL: properties are sparse
    (e.g. spoke-genelab abundance edges carry adj_p_value on 54 of 193
    statements), so requiring all of them silently drops most rows. Predicates
    and variables come from the property URI's local name, not its display
    label, which may be prose ("Activity Sources").
    """
    # VoID-built files give classes as IRIs; name the variable after the local
    # name (?disease), not the whole IRI (?httpsw3idorgbiolinkvocabdisease).
    source_var = _sparql_var(_class_word(source_class)) or "source"
    target_var = _sparql_var(_class_word(target_class)) or "target"
    if source_var == target_var:
        source_var, target_var = f"{source_var}_1", f"{target_var}_2"
    schema_ns = _SCHEMA_NS.format(shortname=shortname)
    rel_pred = (
        f"<{relationship_uri}>"
        if relationship_uri and not relationship_uri.startswith(schema_ns)
        else f"schema:{relationship_label}"
    )

    prop_selects: list[str] = []
    prop_patterns: list[str] = []
    for p in properties:
        uri = p.get("uri") or ""
        local = _local_name(uri) if uri else p.get("label", "")
        var = _sparql_var(local)
        if not var:
            continue
        pred = (
            f"schema:{local}"
            if uri.startswith(schema_ns) and local == _sparql_var(local)
            else f"<{uri}>"
        )
        prop_selects.append(f"?{var}")
        prop_patterns.append(f"    OPTIONAL {{ ?stmt {pred} ?{var} }}")

    return (
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
        f"PREFIX schema: <{schema_ns}>\n\n"
        f"SELECT ?{source_var} ?{target_var} {' '.join(prop_selects)}\n"
        "WHERE {\n"
        f"  GRAPH <{named_graph(shortname)}> {{\n"
        f"    ?stmt rdf:subject ?{source_var} ;\n"
        f"          rdf:predicate {rel_pred} ;\n"
        f"          rdf:object ?{target_var} .\n"
        "    # Edge properties are sparse: keep OPTIONAL except on ones you filter by.\n"
        f"{chr(10).join(prop_patterns)}\n"
        "  }\n"
        "}"
    )


#: What each ``Pattern`` value means for the query, shown once per pattern present.
#: Plain ``direct`` needs no note. Each is scoped to its own predicates: guidance is
#: an instruction to the model, so it must not read as a rule for the whole KG.
PATTERN_GUIDANCE = {
    "direct;reified": (
        "Stored twice, one-to-one: as a direct triple `?s <p> ?o` AND as an "
        "rdf:Statement (rdf:subject / rdf:predicate / rdf:object). Use the direct "
        "triple to traverse or test the link; use the relationship's "
        "edge_properties query_template only to read or filter its edge "
        "properties, which exist only on the statement."
    ),
    "reified": (
        "Stored ONLY as rdf:Statements: `?s <p> ?o` returns nothing. Use the "
        "relationship's edge_properties query_template."
    ),
    "axiom": (
        "Never asserted as a triple: `?s <p> ?o` returns nothing. These appear only "
        "as owl:onProperty of OWL restrictions inside class definitions. Read one "
        "with query_template (substitute the predicate); each row is a class-level "
        "statement (every <subject> has some <filler> via <p>), not an instance link."
    ),
    "direct;axiom": (
        "Asserted as triples AND used in OWL class definitions: `?s <p> ?o` returns "
        "the asserted links; the axiom query_template returns the class-level "
        "restrictions."
    ),
    "declared": (
        "Declared in the schema but used in no triple or class axiom: any query on "
        "these returns nothing."
    ),
}


#: The one-line form of PATTERN_GUIDANCE shown on each edge_properties entry.
_EDGE_USAGE = {
    "direct;reified": (
        "Also a direct triple: use `?s <{uri}> ?o` unless you need edge properties."
    ),
    "reified": "Only reified: `?s <{uri}> ?o` returns nothing; use this template.",
}


def _axiom_query_template(shortname: str, predicate: str) -> str:
    """Read the OWL restrictions on one predicate: one row per restriction.

    Two shapes cover 8,153 of 8,163 restrictions on the 28 axiom-only predicates of
    bio101, phaseskg, sawgraph, hydrologykg and fiokg (2026-10-16): the restriction
    sits in a named class's own definition (``rdfs:subClassOf`` or, OBO-style,
    ``owl:equivalentClass``, through nested ``owl:intersectionOf`` lists), or it is
    nested in another restriction's filler, where the named classes beside it in
    that inner intersection are its subject (bio101: Process ⊑ ∃has-participant.
    (NADH ⊓ ∃has-oxidized-form.NAD-Plus)). Fillers are usually intersections, so
    their named members (and ``unionOf`` alternatives) are unpacked; literal
    ``owl:hasValue`` fillers (bio101's ``"*green"``) are kept, and cardinalities go
    in ``?constraints`` (a plain ``owl:maxCardinality 1`` has no filler at all).
    ``GROUP_CONCAT`` takes ``STR()``: QLever silently drops IRI values from it.
    """
    return (
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
        "PREFIX owl: <http://www.w3.org/2002/07/owl#>\n\n"
        "# One row per restriction: the named classes it describes, its filler(s)\n"
        '# (named classes or literal values) and any cardinality, each " | "-joined.\n'
        'SELECT ?r (GROUP_CONCAT(DISTINCT STR(?subject); SEPARATOR=" | ") AS ?subjects)\n'
        '       (GROUP_CONCAT(DISTINCT STR(?filler); SEPARATOR=" | ") AS ?fillers)\n'
        '       (GROUP_CONCAT(DISTINCT ?card; SEPARATOR=" | ") AS ?constraints)\n'
        "WHERE {\n"
        f"  GRAPH <{named_graph(shortname)}> {{\n"
        f"    ?r owl:onProperty <{predicate}> .\n"
        "    { # in a named class's own definition\n"
        "      ?subject (rdfs:subClassOf|owl:equivalentClass)/"
        "(owl:intersectionOf/rdf:rest*/rdf:first)* ?r .\n"
        "    } UNION { # nested in another restriction's filler\n"
        "      ?outer owl:someValuesFrom ?inner .\n"
        "      ?inner owl:intersectionOf/rdf:rest*/rdf:first ?r , ?subject .\n"
        "    }\n"
        "    FILTER(isIRI(?subject))\n"
        "    OPTIONAL {\n"
        "      ?r owl:someValuesFrom|owl:allValuesFrom|owl:onClass|owl:hasValue"
        "|owl:onDataRange ?f .\n"
        "      ?f ((owl:intersectionOf|owl:unionOf)/rdf:rest*/rdf:first)* ?filler .\n"
        "      FILTER(!isBlank(?filler))\n"
        "    }\n"
        "    OPTIONAL {\n"
        "      ?r ?cp ?n .\n"
        "      FILTER(?cp IN (owl:cardinality, owl:minCardinality, owl:maxCardinality,\n"
        "                     owl:qualifiedCardinality, owl:minQualifiedCardinality,\n"
        "                     owl:maxQualifiedCardinality))\n"
        '      BIND(CONCAT(STRAFTER(STR(?cp), "#"), " ", STR(?n)) AS ?card)\n'
        "    }\n"
        "  }\n"
        "}\n"
        "GROUP BY ?r"
    )


def _pattern_guidance(
    shortname: str,
    predicates: list[dict[str, Any]],
    collapsed: list[str],
) -> dict[str, Any]:
    """``{pattern: {guidance, count, …}}`` for each non-``direct`` pattern present."""
    by_pattern: dict[str, list[str]] = {}
    for p in predicates:
        if p["pattern"] and p["pattern"] != "direct":
            by_pattern.setdefault(p["pattern"], []).append(p["uri"])
    for uri in collapsed:
        by_pattern.setdefault("declared", []).append(uri)
    out: dict[str, Any] = {}
    for pattern, uris in by_pattern.items():
        entry: dict[str, Any] = {
            "guidance": PATTERN_GUIDANCE.get(pattern, ""),
            "count": len(uris),
        }
        if pattern == "reified" or (pattern == "declared" and collapsed):
            entry["predicates"] = uris
        if "axiom" in pattern:
            entry["query_template"] = _axiom_query_template(shortname, uris[0])
            if usage_notes(shortname):
                entry["guidance"] += " See usage_notes for this KG's own rules."
        if pattern == "declared" and collapsed:
            entry["guidance"] += " Left out of the predicates table (compact view)."
        out[pattern] = entry
    return out


def _sparql_var(name: str) -> str:
    """Lowercase-safe SPARQL variable name: keep [A-Za-z0-9_], drop the rest."""
    return re.sub(r"[^A-Za-z0-9_]", "", name.replace(" ", "_")).lower()


def _pair_summary(pairs: list[tuple[str, str, int | None]]) -> str:
    """The pairs after the top one, by local name: ``A → B (12); … (+N more)``."""
    rest = pairs[1:]
    parts = [
        f"{_local_name(s) or '?'} → {_local_name(t) or '?'}"
        + (f" ({n:,})" if n is not None else "")
        for s, t, n in rest[:MAX_EXTRA_PAIRS]
    ]
    if len(rest) > MAX_EXTRA_PAIRS:
        parts.append(f"+{len(rest) - MAX_EXTRA_PAIRS} more")
    return "; ".join(parts)


def _build_schema_from_metadata(
    shortname: str, entity_metadata: dict[str, dict[str, Any]], compact: bool
) -> dict[str, Any]:
    """Build the schema response from a KG's entity metadata file."""
    classes: list[dict[str, Any]] = []
    predicates: list[dict[str, Any]] = []
    edge_properties_dict: dict[str, list[dict[str, str]]] = {}
    node_properties: list[dict[str, str]] = []

    entries = [
        (uri, m)
        for uri, meta in entity_metadata.items()
        for m in (meta, *meta.get("also", ()))
    ]
    for uri, meta in entries:
        entity_type = (meta.get("type") or "").lower()
        if entity_type == "class":
            classes.append(
                {
                    "uri": uri,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                    "instances": meta.get("triples"),
                }
            )
        elif entity_type == "predicate":
            short_name = uri.split("/")[-1] if "/" in uri else uri
            predicates.append(
                {
                    "uri": uri,
                    "short_name": short_name,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                    "source_class": meta.get("source_class", ""),
                    "target_class": meta.get("target_class", ""),
                    "has_edge_properties": False,
                    "pattern": meta.get("pattern", ""),
                    "triples": meta.get("triples"),
                    "other_pairs": _pair_summary(meta.get("pairs") or []),
                }
            )
        elif entity_type == "edgeproperty":
            parents = meta.get("edge_property_of", "")
            for parent in (p.strip() for p in parents.split(";") if p.strip()):
                edge_properties_dict.setdefault(parent, []).append(
                    {
                        "uri": uri,
                        "label": meta.get("label", ""),
                        "description": meta.get("description", ""),
                        "type": meta.get("type", ""),
                    }
                )
        elif entity_type == "nodeproperty":
            node_properties.append(
                {
                    "uri": uri,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                    "class": meta.get("source_class", ""),
                }
            )

    # Edge-property parents are short names (curated files) or IRIs (VoID files).
    edge_properties_output: dict[str, Any] = {}
    for parent, props in edge_properties_dict.items():
        rel = next(
            (p for p in predicates if parent in (p["short_name"], p["uri"])), None
        )
        if rel is None:
            continue
        rel["has_edge_properties"] = True
        relationship_label = _local_name(parent) if parent == rel["uri"] else parent
        taken = edge_properties_output.get(relationship_label)
        if taken is not None and taken["uri"] != rel["uri"]:
            # Same local name, another namespace (prokn: biolink.github.io and
            # w3id.org catalyzes): keep both rather than overwrite one.
            host = urlsplit(rel["uri"]).netloc or "other"
            relationship_label = f"{relationship_label} ({host})"
        edge_properties_output[relationship_label] = {
            "uri": rel["uri"],
            "label": relationship_label,
            "description": rel["description"],
            "source_class": rel["source_class"],
            "target_class": rel["target_class"],
            "properties": props,
            "query_template": _generate_query_template(
                shortname,
                relationship_label,
                rel["source_class"],
                rel["target_class"],
                props,
                relationship_uri=rel["uri"],
            ),
        }
        if rel["pattern"]:
            # One line beside the template it qualifies; the full text is once in
            # pattern_guidance (repeating it cost prokn 29 KB over 68 edges).
            entry = edge_properties_output[relationship_label]
            entry["pattern"] = rel["pattern"]
            if rel["pattern"] in _EDGE_USAGE:
                entry["usage"] = _EDGE_USAGE[rel["pattern"]].format(uri=rel["uri"])
            override = _EDGE_USAGE_OVERRIDES.get(shortname, {}).get(rel["uri"])
            if override:
                entry["usage"] = override

    # Pattern (how a predicate is stored: direct / reified / axiom / declared), counts
    # and extra source/target pairs exist only in the VoID-built files; the
    # columns appear only then, so curated-file output is unchanged.
    # Compact view: declared-only predicates hold no data, so list them once in
    # pattern_guidance instead of as table rows (79 in bio101, 67 in phaseskg).
    collapsed = [p["uri"] for p in predicates if compact and p["pattern"] == "declared"]
    if collapsed:
        predicates = [p for p in predicates if p["pattern"] != "declared"]

    class_cols = ["uri", "label", "description", "type"]
    if any(c["instances"] is not None for c in classes):
        class_cols.append("instances")
    pred_cols = [
        "uri",
        "label",
        "description",
        "type",
        "source_class",
        "target_class",
        "has_edge_properties",
    ]
    if any(p["pattern"] for p in predicates):
        pred_cols.append("pattern")
    if any(p["triples"] is not None for p in predicates):
        pred_cols.append("triples")
    if any(p["other_pairs"] for p in predicates):
        pred_cols.append("other_pairs")

    result: dict[str, Any] = {
        "classes": {
            "columns": class_cols,
            "data": [[c[k] for k in class_cols] for c in classes],
            "count": len(classes),
        },
        "predicates": {
            "columns": pred_cols,
            "data": [[p[k] for k in pred_cols] for p in predicates],
            "count": len(predicates),
        },
        "edge_properties": edge_properties_output,
        "node_properties": {
            "columns": ["uri", "label", "description", "type", "class"],
            "data": [
                [n["uri"], n["label"], n["description"], n["type"], n["class"]]
                for n in node_properties
            ],
            "count": len(node_properties),
        },
    }

    guidance = _pattern_guidance(shortname, predicates, collapsed)
    if guidance:
        result["pattern_guidance"] = guidance

    if not compact and edge_properties_output:
        result = {
            "edge_property_summary": {
                "CRITICAL_NOTE": (
                    "Some relationships have edge properties (data stored on the "
                    "relationship itself). To query these, use the RDF reification "
                    "pattern shown in each edge's query_template."
                ),
                "edges_with_properties": [
                    {
                        "relationship": label,
                        "uri": info["uri"],
                        "properties": [
                            {
                                "name": p.get("label", ""),
                                "type": p.get("description", "")
                                .split("(")[-1]
                                .rstrip(")"),
                            }
                            for p in info.get("properties", [])
                        ],
                        "example_query": info.get("query_template", ""),
                    }
                    for label, info in edge_properties_output.items()
                ],
            },
            **result,
        }

    return result


def _should_exclude_uri(uri: str) -> bool:
    """Filter out RDF-syntax-namespace URIs (e.g. container props rdf:_1, rdf:_2)."""
    return uri.startswith(
        (
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "https://www.w3.org/1999/02/22-rdf-syntax-ns#",
        )
    )


async def _probe_schema(shortname: str) -> dict[str, Any]:
    """Discover classes and predicates by probing the federation endpoint.

    Used when no entity metadata file exists for the KG. Scopes each query to
    the KG's named graph via a ``GRAPH`` block.
    """
    graph = named_graph(shortname)
    # Classes are probed by TWO separate queries, not one UNION. Combining the
    # unbound `?s a ?class` with the declared-class branches made QLever's planner
    # try to allocate 37.9 GB and fail with HTTP 500 — instantly, for EVERY graph,
    # so this whole path was dead. Split, each part runs fine (measured on
    # identifier-mappings: ~5s for the instance types, ~0.1s for the declarations).
    instance_class_query = f"""\
SELECT DISTINCT ?class WHERE {{
  GRAPH <{graph}> {{
    ?s a ?class .
  }}
}}"""

    # Classes DECLARED but possibly never instantiated. (`a` already IS rdf:type, so
    # the old query's separate rdf:type branch was a duplicate of the one above.)
    declared_class_query = f"""\
SELECT DISTINCT ?class WHERE {{
  GRAPH <{graph}> {{
    {{ ?class a <http://www.w3.org/2000/01/rdf-schema#Class> . }}
    UNION {{ ?class a <http://www.w3.org/2002/07/owl#Class> . }}
  }}
}}"""

    predicate_query = f"""\
SELECT DISTINCT ?predicate WHERE {{
  GRAPH <{graph}> {{
    ?s ?predicate ?o .
  }}
}}"""

    # Independent probes of the same graph — run them together rather than paying
    # every round trip in series (the same pattern as probe.find_crosswalks).
    # `return_exceptions=True` so ALL results are consumed before we raise: a bare
    # gather would surface the first failure and leave a sibling's exception
    # unretrieved. Ordering is done below rather than by the endpoint — the results
    # are merged anyway, so an ORDER BY would just be work the server repeats.
    probed: list[Any] = await asyncio.gather(
        run_sparql(instance_class_query),
        run_sparql(declared_class_query),
        run_sparql(predicate_query),
        return_exceptions=True,
    )
    for outcome in probed:
        if isinstance(outcome, BaseException):
            raise outcome
    instance_classes, declared_classes, predicates = probed

    class_uris = {
        r["class"]
        for result in (instance_classes, declared_classes)
        for r in result.get("rows", [])
        if r.get("class") and not _should_exclude_uri(r["class"])
    }
    class_data = [[uri] for uri in sorted(class_uris)]
    predicate_data = [
        [r["predicate"]]
        for r in sorted(
            predicates.get("rows", []), key=lambda r: r.get("predicate") or ""
        )
        if r.get("predicate") and not _should_exclude_uri(r["predicate"])
    ]

    return {
        "classes": {"columns": ["uri"], "data": class_data, "count": len(class_data)},
        "predicates": {
            "columns": ["uri"],
            "data": predicate_data,
            "count": len(predicate_data),
        },
        "edge_properties": {},
        "node_properties": {"columns": ["uri"], "data": [], "count": 0},
    }


async def get_schema(shortname: str, compact: bool = True) -> dict[str, Any]:
    """Return the schema (classes, predicates, edge/node properties) for a KG.

    Prefers the KG's entity metadata file; falls back to probing the federation
    endpoint for distinct classes and predicates.

    Args:
        shortname: The KG shortname (e.g. ``prokn``, ``spoke``), as returned by
            ``list_kgs``.
        compact: If True (default), omit the prepended ``edge_property_summary``
            section. Set False for the richer summary.
    """
    if shortname in _TOO_LARGE:
        return {
            "shortname": shortname,
            "error": (
                f"`{shortname}` is too large to enumerate a schema for; query it "
                "directly with known ontology terms instead."
            ),
        }

    entity_metadata = await fetch_entity_metadata(shortname)
    if entity_metadata:
        schema = _build_schema_from_metadata(shortname, entity_metadata, compact)
    else:
        schema = await _probe_schema(shortname)

    result: dict[str, Any] = {"shortname": shortname, "schema": schema}
    source = metadata_source(shortname)
    if ENTITY_METADATA_OVERRIDE and source:
        # Testing aid: which entity files answered.
        result["metadata_source"] = source
    return result


# ── Mermaid class-diagram generation ─────────────────────────────────────────


def _local_name(uri: str) -> str:
    """Return the last path/fragment segment of a URI."""
    return re.split(r"[/#]", uri.rstrip("/#"))[-1] if uri else uri


def _mermaid_id(name: str) -> str:
    """Sanitize a label or URI into a Mermaid-safe class identifier."""
    if name.startswith(("http://", "https://")):
        name = _local_name(name)
    ident = re.sub(r"\W+", "_", name or "").strip("_")
    # Mermaid 12 turns `style <id>` into a CSS class selector, which may not start
    # with a digit (prokn's SNOMED class http://snomed.info/id/276239002).
    if ident[:1].isdigit():
        ident = f"n_{ident}"
    return ident or "Node"


def _member_type(description: str) -> str:
    """Extract a field type from a trailing ``(type)`` in a property description.

    Returns "" when the description has no such marker — we deliberately do NOT
    fall back to the entity ``type`` (which is always "EdgeProperty"/
    "NodeProperty" and useless as a data type).
    """
    m = re.search(r"\(([^()]+)\)[.\s]*$", (description or "").strip())
    if m:
        candidate = m.group(1).strip()
        if candidate and " " not in candidate and len(candidate) <= 20:
            return candidate.lower()
    return ""


def _clean_edge_label(label: str) -> str:
    """Strip characters that would break a Mermaid relationship label.

    A colon ends the label in Mermaid 12 (``geo:hasGeometry`` failed geoconnex,
    hydrologykg, nikg, sockg and spatialkg), so it becomes the entity ``#58;``,
    which Mermaid draws as ``:``.
    """
    text = (label or "").replace("|", " ").replace("\n", " ").replace(":", "#58;")
    return re.sub(r"\s+", " ", text).strip()


def _col(table: dict[str, Any], name: str) -> int | None:
    cols = table.get("columns", [])
    return cols.index(name) if name in cols else None


def _row_value(row: list[Any], idx: int | None) -> str:
    return row[idx] if idx is not None and len(row) > idx and row[idx] else ""


async def infer_curated_edges(
    shortname: str,
    class_uris: list[str],
    pred_uris: list[str],
    limit: int = 400,
) -> list[tuple[str, str, str]]:
    """Infer ``(predicate, domain, range)`` URI triples from declared domain/range.

    Read from the graph's ``rdfs:domain``/``rdfs:range``, restricted to the given
    curated class and predicate URIs.

    Used when a KG's curated metadata names predicates but not their endpoints
    (e.g. ``sawgraph``): the graph itself often declares domain/range, and
    scoping both ends to curated classes keeps the result bounded and aligned
    with the schema. Returns ``[]`` on error or when nothing matches.
    """
    if not class_uris or not pred_uris:
        return []
    graph = named_graph(shortname)
    values_d = " ".join(f"<{u}>" for u in class_uris)
    values_p = " ".join(f"<{u}>" for u in pred_uris)
    query = f"""\
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?p ?d ?r WHERE {{
  GRAPH <{graph}> {{
    ?p rdfs:domain ?d ; rdfs:range ?r .
    VALUES ?p {{ {values_p} }}
    VALUES ?d {{ {values_d} }}
    VALUES ?r {{ {values_d} }}
  }}
}} LIMIT {int(limit)}"""
    try:
        rows = (await run_sparql(query)).get("rows", [])
    except SparqlError:
        return []
    return [
        (r["p"], r["d"], r["r"])
        for r in rows
        if r.get("p") and r.get("d") and r.get("r")
    ]


async def infer_edge_labels(
    shortname: str, schema: dict[str, Any]
) -> list[tuple[str, str, str]]:
    """Return inferred ``(source_label, predicate_label, target_label)`` edges.

    No-op (returns ``[]``) when the schema already has curated predicate
    endpoints — we only fill the gap, never override curated relationships.
    """
    classes_tbl = schema.get("classes", {})
    predicates_tbl = schema.get("predicates", {})
    p_src, p_tgt = (
        _col(predicates_tbl, "source_class"),
        _col(predicates_tbl, "target_class"),
    )

    # If any curated predicate already declares both endpoints, don't infer.
    if p_src is not None and p_tgt is not None:
        for row in predicates_tbl.get("data", []):
            if _row_value(row, p_src) and _row_value(row, p_tgt):
                return []

    cls_label = _col(classes_tbl, "label")
    pred_label = _col(predicates_tbl, "label")
    class_rows = [r for r in classes_tbl.get("data", []) if r]
    pred_rows = [r for r in predicates_tbl.get("data", []) if r]
    uri_to_class = {
        r[0]: (_row_value(r, cls_label) or _local_name(r[0])) for r in class_rows
    }
    uri_to_pred = {
        r[0]: (_row_value(r, pred_label) or _local_name(r[0])) for r in pred_rows
    }

    triples = await infer_curated_edges(
        shortname, list(uri_to_class), list(uri_to_pred)
    )
    edges: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for p, d, r in triples:
        src, tgt, label = uri_to_class.get(d), uri_to_class.get(r), uri_to_pred.get(p)
        if not (src and tgt and label):
            continue
        key = (src, label, tgt)
        if key not in seen:
            seen.add(key)
            edges.append(key)
    return edges


#: Vocabularies whose classes describe how a schema is encoded (owl:Class,
#: owl:Restriction, owl:ObjectProperty, …), not what it is about.
_META_NAMESPACES = tuple(
    scheme + ns
    for ns in (
        "www.w3.org/2002/07/owl#",
        "www.w3.org/1999/02/22-rdf-syntax-ns#",
        "www.w3.org/2000/01/rdf-schema#",
    )
    # prokn types 1,436 nodes https://www.w3.org/2002/07/owl#Class (wrong scheme).
    for scheme in ("http://", "https://")
)

#: Above this many node classes a diagram keeps only the most-connected ones:
#: bio101 rendered 246 classes in one 36,000 px row.
MAX_DIAGRAM_CLASSES = 60
#: …and at most this many arrows between them: sawgraph's 60 most-connected classes
#: still had 1,741 arrows (overlapping FoodOn material types), which Mermaid 12
#: could not lay out in three minutes.
MAX_DIAGRAM_ARROWS = 100
#: Labels shown on one merged arrow; the rest become "+N more" (hydrologykg packed
#: a 498-character label of spatial predicates onto one arrow).
MAX_ARROW_LABELS = 4
#: Edge classes sharing source, target and edge properties are drawn as one box
#: (listing their names) from this many on: spoke-genelab's three MEASURED_*
#: relationships stay separate, biohealth's 66 Entity -> Entity ones merge.
MIN_EDGE_GROUP = 4

_ARROW = re.compile(r"^  (\S+) --> (\S+)(?: : (.*))?$")


def _cap_classes(
    declared: dict[str, list[str]],
    relationships: list[str],
    edge_class_ids: list[str],
    limit: int,
    max_arrows: int = MAX_DIAGRAM_ARROWS,
) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """Keep the most-connected node classes within both limits; drop the rest.

    Classes are taken in order of degree (every arrow end counts; ties keep
    declaration order) while at most ``limit`` classes and ``max_arrows`` arrows
    among them result. Edge classes survive only while both their endpoints do.
    Returns ``(declared, relationships, omitted node classes)``.
    """
    nodes = [c for c in declared if c not in edge_class_ids]
    if len(nodes) <= limit and len(relationships) <= max_arrows:
        return declared, relationships, []
    degree = dict.fromkeys(nodes, 0)
    for line in relationships:
        m = _ARROW.match(line)
        if m:
            for end in m.group(1, 2):
                if end in degree:
                    degree[end] += 1
    order = {c: i for i, c in enumerate(nodes)}
    ranked = sorted(nodes, key=lambda c: (-degree[c], order[c]))
    # Links between node classes: a plain arrow is one, and so is a relationship
    # drawn through an edge class (source --> edge --> target). Counting the two
    # hops separately let prokn's 65 edge classes use up the whole budget.
    edge_set = set(edge_class_ids)
    ends_of: dict[str, list[str]] = {e: [] for e in edge_class_ids}
    links: list[tuple[str, str]] = []
    for line in relationships:
        m = _ARROW.match(line)
        if not m:
            continue
        a, b = m.group(1, 2)
        if a in edge_set:
            ends_of[a].append(b)
        elif b in edge_set:
            ends_of[b].append(a)
        else:
            links.append((a, b))
    links += [(e[0], e[1]) for e in ends_of.values() if len(e) == 2]
    keep: set[str] = set()
    for cand in ranked:
        if len(keep) >= limit:
            break
        trial = keep | {cand}
        if keep and sum(1 for a, b in links if a in trial and b in trial) > max_arrows:
            continue
        keep = trial
    ends: dict[str, set[str]] = {e: set() for e in edge_class_ids}
    for line in relationships:
        m = _ARROW.match(line)
        if m:
            a, b = m.group(1, 2)
            if a in ends:
                ends[a].add(b)
            if b in ends:
                ends[b].add(a)
    keep |= {e for e in edge_class_ids if ends[e] and ends[e] <= keep}
    kept_rel = []
    for line in relationships:
        m = _ARROW.match(line)
        if not m or set(m.group(1, 2)) <= keep:
            kept_rel.append(line)
    omitted = [c for c in nodes if c not in keep]
    return {c: m for c, m in declared.items() if c in keep}, kept_rel, omitted


def _merge_parallel(relationships: list[str]) -> list[str]:
    """One labelled arrow per (source, target): labels joined, first position kept.

    At most :data:`MAX_ARROW_LABELS` labels are shown, then ``+N more``.

    spoke-genelab's Assay reaches Anatomy by INVESTIGATED_ASiA, material_id_1 and
    material_id_2; three parallel arrows overlap their labels when rendered.
    Unlabelled arrows (the hops into and out of an edge class) are kept as is.
    """
    merged: dict[tuple[str, str], list[str]] = {}
    order: list[tuple[str, str] | str] = []
    for line in relationships:
        m = _ARROW.match(line)
        if not m or m.group(3) is None:
            if line not in order:
                order.append(line)
            continue
        key = (m.group(1), m.group(2))
        if key not in merged:
            merged[key] = []
            order.append(key)
        if m.group(3) not in merged[key]:
            merged[key].append(m.group(3))

    def joined(labels: list[str]) -> str:
        shown = ", ".join(labels[:MAX_ARROW_LABELS])
        extra = len(labels) - MAX_ARROW_LABELS
        return f"{shown}, +{extra} more" if extra > 0 else shown

    return [
        item
        if isinstance(item, str)
        else f"  {item[0]} --> {item[1]} : " + joined(merged[item])
        for item in order
    ]


def build_mermaid_diagram(
    shortname: str,
    schema: dict[str, Any],
    inferred_edges: list[tuple[str, str, str]] | None = None,
    max_classes: int = MAX_DIAGRAM_CLASSES,
    info: dict[str, Any] | None = None,
    max_arrows: int = MAX_DIAGRAM_ARROWS,
) -> str:
    """Render a KG's schema as a Mermaid ``classDiagram`` (deterministic).

    Node classes become class boxes (with node properties as members), edge
    predicates with source/target metadata become labeled arrows, and predicates
    carrying edge properties become intermediary classes with typed fields
    wired ``source --> edge --> target``. ``inferred_edges`` (optional
    ``(source_label, predicate_label, target_label)`` triples recovered from the
    graph's domain/range) are drawn as labeled arrows for KGs whose curated
    metadata lacks endpoints. Predicates that remain without endpoints are listed
    as ``%%`` comments rather than guessed at.

    OWL/RDF/RDFS classes (owl:Class, owl:Restriction, …) and every arrow touching
    them are left out, as are classes that only those arrows reached (bio101's
    ``*-Constant`` value classes). Above ``max_classes`` node classes, only the
    most-connected are drawn; ``info`` (if given) receives the totals and the
    omitted class names.
    """
    classes_tbl = schema.get("classes", {})
    predicates_tbl = schema.get("predicates", {})
    node_props_tbl = schema.get("node_properties", {})
    edge_properties = schema.get("edge_properties", {}) or {}

    declared: dict[str, list[str]] = {}  # class id -> member lines (insertion order)
    relationships: list[str] = []
    undrawn: list[str] = []
    edge_class_ids: list[str] = []  # intermediary classes (styled distinctly)

    # Node classes (column layout: [uri, label, ...] for metadata, [uri] for probe).
    cls_cols = classes_tbl.get("columns", [])
    label_idx = cls_cols.index("label") if "label" in cls_cols else None
    meta_ids: set[str] = set()
    class_names = []
    #: Class IRI -> its label, so an endpoint given as an IRI (some curated rows,
    #: all VoID rows) lands on the same box as one given as the label.
    iri_label: dict[str, str] = {}
    for row in classes_tbl.get("data", []):
        if not row:
            continue
        label = row[label_idx] if label_idx is not None and len(row) > label_idx else ""
        name = label or _local_name(row[0])
        iri_label[str(row[0])] = name
        if str(row[0]).startswith(_META_NAMESPACES):
            meta_ids.add(_mermaid_id(name))
        else:
            class_names.append(name)
    touched_by_meta: set[str] = set()

    def ensure_class(label: str) -> str:
        cid = _mermaid_id(iri_label.get(label, label))
        if cid not in meta_ids:
            declared.setdefault(cid, [])
        return cid

    def arrow(src: str, tgt: str, label: str = "") -> None:
        s_id = _mermaid_id(iri_label.get(src, src))
        t_id = _mermaid_id(iri_label.get(tgt, tgt))
        if s_id in meta_ids or t_id in meta_ids:
            touched_by_meta.update({s_id, t_id} - meta_ids)
            return
        ensure_class(src), ensure_class(tgt)
        relationships.append(f"  {s_id} --> {t_id}" + (f" : {label}" if label else ""))

    for name in class_names:
        ensure_class(name)

    # Node properties become members of their owning class.
    np_cols = node_props_tbl.get("columns", [])
    np_label = np_cols.index("label") if "label" in np_cols else None
    np_desc = np_cols.index("description") if "description" in np_cols else None
    np_class = np_cols.index("class") if "class" in np_cols else None
    for row in node_props_tbl.get("data", []):
        if not row or np_label is None or np_class is None:
            continue
        owner = row[np_class] if len(row) > np_class else ""
        name = row[np_label] if len(row) > np_label else ""
        if (
            not owner
            or not name
            or _mermaid_id(iri_label.get(owner, owner)) in meta_ids
        ):
            continue
        cid = ensure_class(owner)
        desc = row[np_desc] if np_desc is not None and len(row) > np_desc else ""
        member = f"{_member_type(desc)} {_mermaid_id(name)}".strip()
        if member not in declared[cid]:
            declared[cid].append(member)

    # Edge predicates with properties → intermediary classes. Relationships that
    # share source, target and edge properties are drawn as ONE box listing their
    # names (biohealth: 66 Entity -> Entity relationships, each with only
    # `source`, made a fan of 132 arrows into one box).
    edges: list[tuple[str, list[str], str, str]] = []
    for rel_label, edge_info in edge_properties.items():
        members = []
        for prop in edge_info.get("properties", []):
            mtype = _member_type(prop.get("description", ""))
            member = f"{mtype} {_mermaid_id(prop.get('label', ''))}".strip()
            if member and member not in members:
                members.append(member)
        src, tgt = edge_info.get("source_class", ""), edge_info.get("target_class", "")
        edges.append((rel_label, members, src, tgt))
    groups: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
    for rel_label, members, src, tgt in edges:
        groups.setdefault((src, tgt, tuple(sorted(members))), []).append(rel_label)
    drawn_groups: set[tuple[str, str, tuple[str, ...]]] = set()
    for rel_label, members, src, tgt in edges:
        key = (src, tgt, tuple(sorted(members)))
        names = groups[key]
        if len(names) >= MIN_EDGE_GROUP:
            if key in drawn_groups:
                continue
            drawn_groups.add(key)
            src_name = _mermaid_id(iri_label.get(src, src)) if src else "Any"
            tgt_name = _mermaid_id(iri_label.get(tgt, tgt)) if tgt else "Any"
            edge_id = f"{src_name}_to_{tgt_name}_{len(names)}_relationships"
            members = members + [_mermaid_id(n) for n in sorted(names)]
        else:
            edge_id = _mermaid_id(rel_label)
        declared[edge_id] = members
        if edge_id not in edge_class_ids:
            edge_class_ids.append(edge_id)
        if src:
            relationships.append(f"  {ensure_class(src)} --> {edge_id}")
        if tgt:
            relationships.append(f"  {edge_id} --> {ensure_class(tgt)}")

    # Edges inferred from the graph's domain/range (when curated metadata lacks
    # endpoints). Their predicate labels are excluded from the "undrawn" list.
    inferred_labels: set[str] = set()
    for src, pred, tgt in inferred_edges or []:
        arrow(src, tgt, _clean_edge_label(pred))
        inferred_labels.add(pred)

    # Plain predicates (no edge properties) with source/target → labeled arrows.
    pred_cols = predicates_tbl.get("columns", [])
    p_label = pred_cols.index("label") if "label" in pred_cols else None
    p_src = pred_cols.index("source_class") if "source_class" in pred_cols else None
    p_tgt = pred_cols.index("target_class") if "target_class" in pred_cols else None
    p_has = (
        pred_cols.index("has_edge_properties")
        if "has_edge_properties" in pred_cols
        else None
    )
    for row in predicates_tbl.get("data", []):
        if not row:
            continue
        if p_has is not None and len(row) > p_has and row[p_has]:
            continue  # already drawn as an intermediary class
        if str(row[0]).startswith(_META_NAMESPACES):
            # owl:sameAs, rdfs:subClassOf, …: identity and modelling links, not
            # domain relationships. sawgraph's sameAs between multi-typed samples
            # tied every FoodOn material class to every other. Classes only these
            # reached are dropped below, like those only OWL constructs reached.
            for end in (p_src, p_tgt):
                name = row[end] if end is not None and len(row) > end else ""
                if name:
                    touched_by_meta.add(_mermaid_id(iri_label.get(name, name)))
            continue
        label = row[p_label] if p_label is not None and len(row) > p_label else ""
        label = label or _local_name(row[0])
        src = row[p_src] if p_src is not None and len(row) > p_src else ""
        tgt = row[p_tgt] if p_tgt is not None and len(row) > p_tgt else ""
        if src and tgt:
            arrow(src, tgt, _clean_edge_label(label))
        elif label not in inferred_labels:
            undrawn.append(_clean_edge_label(label))

    relationships = _merge_parallel(relationships)
    in_arrows: set[str] = set()
    for line in relationships:
        m = _ARROW.match(line)
        if m:
            in_arrows.update(m.group(1, 2))
    # Classes only OWL constructs pointed at, with nothing else to show.
    for cid in touched_by_meta:
        if cid in declared and not declared[cid] and cid not in in_arrows:
            del declared[cid]
    declared, relationships, omitted = _cap_classes(
        declared, relationships, edge_class_ids, max_classes, max_arrows
    )
    if info is not None:
        node_total = len([c for c in declared if c not in edge_class_ids]) + len(
            omitted
        )
        info.update(classes_total=node_total, classes_drawn=node_total - len(omitted))
        if omitted:
            info["omitted_classes"] = omitted

    lines = ["classDiagram", "  direction TB"]
    for cid, members in declared.items():
        if members:
            lines.append(f"  class {cid} {{")
            lines += [f"    {m}" for m in members]
            lines.append("  }")
        else:
            lines.append(f"  class {cid}")
    lines += relationships

    node_class_ids = [cid for cid in declared if cid not in edge_class_ids]

    # Legend: one labelled box per class type actually present in the diagram.
    legend: list[tuple[str, str, str]] = []  # (class id, label, style)
    if declared:
        legend.append(("LegendNodeClass", "Node class", _NODE_CLASS_STYLE))
        if edge_class_ids:
            legend.append(
                ("LegendEdgeClass", "Edge (relationship) class", _EDGE_CLASS_STYLE)
            )
    if legend:
        lines.append("  %% Legend")
        lines += [f'  class {lid}["{label}"]' for lid, label, _ in legend]

    # Styling: node classes light blue, edge classes orange (per-class `style`
    # is the form that actually renders fills in classDiagram).
    lines += [f"  style {cid} {_NODE_CLASS_STYLE}" for cid in node_class_ids]
    lines += [f"  style {cid} {_EDGE_CLASS_STYLE}" for cid in edge_class_ids]
    lines += [f"  style {lid} {style}" for lid, _, style in legend]

    if omitted:
        drawn = len([c for c in declared if c not in edge_class_ids])
        lines.append(
            f"  %% Showing the {drawn} most-connected of "
            f"{drawn + len(omitted)} classes; omitted:"
        )
        lines += [f"  %%   - {c}" for c in omitted]
    if undrawn:
        lines.append("  %% Predicates without source/target metadata (not drawn):")
        lines += [f"  %%   - {p}" for p in undrawn]

    return "\n".join(lines)


_RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
#: Reification wiring: the edge classes already draw what these connect.
_REIFICATION = frozenset(
    {_RDF_NS + "subject", _RDF_NS + "predicate", _RDF_NS + "object", _RDF_NS + "type"}
)
_LITERAL_TYPES = ("http://www.w3.org/2001/XMLSchema#", _RDF_NS)


def _is_void_metadata(entity_metadata: dict[str, dict[str, Any]]) -> bool:
    """True for a VoID-built file (counts or Pattern present), not a curated one."""
    return any(
        m.get("pattern") or m.get("triples") is not None
        for m in entity_metadata.values()
    )


def diagram_schema(
    shortname: str, entity_metadata: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """A label-keyed schema for :func:`build_mermaid_diagram` from a VoID-built file.

    The compact get_schema view keeps one source/target pair per predicate and
    names endpoints by IRI, while the diagram matches classes by label. This walks
    every pair instead: class IRIs map to their labels; a literal-typed target
    (xsd:*, rdf:langString) makes the predicate a typed member of the source class;
    an empty target (untyped IRIs, e.g. NCBITaxon) an ``iri`` member; reification
    wiring and the rdf:Statement class are left out.
    """
    entries = [
        (uri, m)
        for uri, meta in entity_metadata.items()
        for m in (meta, *meta.get("also", ()))
    ]
    labels = {
        uri: m.get("label") or _local_name(uri)
        for uri, m in entries
        if (m.get("type") or "").lower() == "class"
    }
    labels.pop(_RDF_STATEMENT, None)

    def name(uri: str) -> str:
        return labels.get(uri) or _local_name(uri)

    classes = [[uri, label] for uri, label in labels.items()]
    predicates: list[list[Any]] = []
    node_props: list[list[str]] = []
    for uri, m in entries:
        kind = (m.get("type") or "").lower()
        if kind != "predicate" or uri in _REIFICATION:
            continue
        label = m.get("label") or _local_name(uri)
        pairs = m.get("pairs") or [
            (m.get("source_class", ""), m.get("target_class", ""), None)
        ]
        drawn = False
        for src, tgt, _n in pairs:
            if not src or src == _RDF_STATEMENT:
                continue
            if not tgt or tgt.startswith(_LITERAL_TYPES):
                dtype = _local_name(tgt) if tgt else "iri"
                node_props.append([uri, label, f"({dtype})", "NodeProperty", name(src)])
            else:
                predicates.append([uri, label, name(src), name(tgt), False])
            drawn = True
        if not drawn:
            predicates.append([uri, label, "", "", False])

    meta_schema = _build_schema_from_metadata(shortname, entity_metadata, compact=True)
    edges = {}
    for rel, info in meta_schema.get("edge_properties", {}).items():
        props = []
        for prop in info.get("properties", []):
            desc = prop.get("description", "")
            if not _member_type(desc):
                target = entity_metadata.get(prop.get("uri", ""), {})
                for cand in (target, *target.get("also", ())):
                    if (cand.get("type") or "").lower() == "edgeproperty":
                        tgt = cand.get("target_class", "")
                        if tgt.startswith(_LITERAL_TYPES):
                            desc = f"({_local_name(tgt)})"
            props.append({**prop, "description": desc})
        src, tgt = info.get("source_class", ""), info.get("target_class", "")
        edges[rel] = {
            **info,
            # A literal-typed end (prokn's wasAttributedTo -> xsd:string) is a
            # value, not a class box.
            "source_class": "" if src.startswith(_LITERAL_TYPES) else name(src),
            "target_class": "" if tgt.startswith(_LITERAL_TYPES) else name(tgt),
            "properties": props,
        }
    edge_rel_uris = {info.get("uri") for info in edges.values()}
    predicates = [p for p in predicates if p[0] not in edge_rel_uris]
    return {
        "classes": {"columns": ["uri", "label"], "data": classes},
        "predicates": {
            "columns": [
                "uri",
                "label",
                "source_class",
                "target_class",
                "has_edge_properties",
            ],
            "data": predicates,
        },
        "node_properties": {
            "columns": ["uri", "label", "description", "type", "class"],
            "data": node_props,
        },
        "edge_properties": edges,
    }


async def visualize_schema(shortname: str) -> dict[str, Any]:
    """Build a Mermaid ``classDiagram`` of a KG's schema, server-side.

    Returns ``{"shortname", "mermaid"}`` on success, or ``{"shortname",
    "error"}`` when the KG has no enumerable schema (e.g. ``ubergraph``).
    """
    result = await get_schema(shortname, compact=True)
    if "error" in result:
        return {"shortname": shortname, "error": result["error"]}
    schema = result["schema"]
    metadata = await fetch_entity_metadata(shortname)
    if metadata and _is_void_metadata(metadata):
        schema = diagram_schema(shortname, metadata)
    inferred = await infer_edge_labels(shortname, schema)
    info: dict[str, Any] = {}
    diagram = build_mermaid_diagram(
        shortname, schema, inferred_edges=inferred, info=info
    )
    result = {"shortname": shortname, "mermaid": diagram}
    if not info.get("classes_total") and not schema.get("edge_properties"):
        result["note"] = (
            "No classes to draw: the schema lists none with source/target "
            "information. Use get_schema."
        )
    elif info.get("omitted_classes"):
        result["note"] = (
            f"Large schema: drawing the {info['classes_drawn']} most-connected of "
            f"{info['classes_total']} classes ({len(info['omitted_classes'])} omitted, "
            "listed as comments at the end of the diagram). Use get_schema for the "
            "full list."
        )
    return result

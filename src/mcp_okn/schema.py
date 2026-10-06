"""Schema discovery for Proto-OKN knowledge graphs.

For each KG we prefer a curated entity metadata CSV (classes, predicates, edge
properties, node properties) published in the ``sbl-sdsc/mcp-proto-okn`` repo.
When no curated metadata exists we fall back to probing the federation endpoint
for the distinct classes and predicates used in the KG's named graph.

The shortnames are the same ones used as federation named graphs
(``https://purl.org/okn/frink/kg/{shortname}``), so the curated CSVs port over
directly from the proto-okn server.
"""

from __future__ import annotations

import asyncio
import csv
import re
from io import StringIO
from typing import Any

import httpx

from .contrasts import (
    SPOKE_GENELAB_CONTRAST_GUIDANCE,
    SPOKE_GENELAB_CONTRAST_SNIPPET,
)
from .sparql import SparqlError, named_graph, run_sparql

#: Where the curated per-KG entity metadata CSVs live.
ENTITY_METADATA_BASE = (
    "https://raw.githubusercontent.com/sbl-sdsc/mcp-proto-okn/main/metadata/entities"
)

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


#: Template for KGs whose curated ``*_entities.csv`` runs AHEAD of the graph the
#: federation actually serves. ``get_schema`` reads those CSVs live from the
#: upstream repo, so when a KG's metadata is refreshed before (or without) a
#: redeploy, the schema advertises predicates and classes that return 0 rows — a
#: silent failure the client reads as "no data" rather than "not deployed yet".
#: Counts are from a live per-predicate census; re-run
#: ``scripts/check_payload_drift.py`` and re-census after a redeploy.
SCHEMA_AHEAD_OF_DEPLOY_GUIDANCE = """\
DEPLOYMENT LAG — this schema is AHEAD of the served graph. {absent} of the
{total} predicates in {shortname}'s curated schema have ZERO triples in the
deployed named graph (censused {checked}). Querying one returns an empty result
that looks like missing data, not like a missing release.

{detail}

Before building on any predicate from this schema, confirm it is populated:
run the ASK below (or a COUNT) for it. Treat a 0 as "not deployed yet", and
prefer a predicate you have confirmed live.\
"""

#: Companion snippet: the cheapest live/not-live check for a single predicate.
SCHEMA_AHEAD_OF_DEPLOY_SNIPPET = """\
# Is this predicate actually deployed? false => in the schema, not in the graph.
ASK {{ GRAPH <https://purl.org/okn/frink/kg/{shortname}> {{
  ?s <{predicate}> ?o . }} }}\
"""

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
NCIPIDKG_GUIDANCE = """\
IDENTIFIER AND JOIN NOTES (the curated schema matches the deployed graph as of
2026-09-02; these are the things it still does not tell you).

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

NO NAMED-PATHWAY AXIS. Despite the KG's name, nothing links an interaction to
an NCI-PID pathway: biolink:Pathway has 0 instances and both obo:RO_0000056 and
the ndexbio inPathway predicate are absent (the realigned CSV simply omits them,
so their absence is easy to miss). Ask about the interaction topology - 83,704
reified INDRA statements over obo:RO_0002436 / RO_0002578 / RO_0002629 /
RO_0002630 / RO_0002211 - not about pathway names.\
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
    "spoke-genelab": {
        "guidance": SPOKE_GENELAB_CONTRAST_GUIDANCE,
        "query_snippet": SPOKE_GENELAB_CONTRAST_SNIPPET,
    },
    "medical-device-kg": {
        "guidance": SCHEMA_AHEAD_OF_DEPLOY_GUIDANCE.format(
            shortname="medical-device-kg",
            absent=152,
            total=296,
            checked="2026-09-01",
            detail=(
                "The curated schema describes a LATER release than the federation "
                "serves. Live and queryable: 510(k) (mdo:k510Number, 175,299), PMA "
                "(mdo:pmaNumber, 111,720), De Novo, HDE, recalls (mdo:recallNumber, "
                "39,223), MAUDE events (mdo:eventType, 15,279), FDA establishment "
                "registration (mdo:feiNumber, 964,478), X-ray assembler sites, MQSA "
                "mammography facilities, 522 postmarket studies, product codes, "
                "regulation numbers and the address block (mdo:zip / mdo:postalCode / "
                "city / state / country — the ZIP5 join surface behind crosswalks "
                "J7-J11). NOT in the deployed graph, though the schema lists them: the "
                "whole AccessGUDID / UDI block (device identifiers, brand names, "
                "packaging, implant and sterility status), CLIA test systems and "
                "waived analytes, GMDN terms, device materials and components, "
                "software features, design changes, patient outcomes, safety signals "
                "and MedSun reports."
            ),
        ),
        "query_snippet": SCHEMA_AHEAD_OF_DEPLOY_SNIPPET.format(
            shortname="medical-device-kg",
            predicate="http://medicaldevice.com/ontology/hasDeviceIdentifier",
        ),
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
_metadata_cache: dict[str, dict[str, dict[str, str]]] = {}


async def fetch_entity_metadata(
    shortname: str,
    client: httpx.AsyncClient | None = None,
    refresh: bool = False,
) -> dict[str, dict[str, str]]:
    """Fetch and parse the curated entity metadata CSV for a KG (cached).

    Returns a dict mapping each URI to ``{label, description, type,
    edge_property_of, source_class, target_class}``. Returns an empty dict when
    no curated CSV exists for the KG (the caller then falls back to probing).
    """
    if shortname in _metadata_cache and not refresh:
        return _metadata_cache[shortname]

    url = f"{ENTITY_METADATA_BASE}/{shortname}_entities.csv"
    owns = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            _metadata_cache[shortname] = {}
            return {}
        content = resp.text
    except httpx.HTTPError:
        _metadata_cache[shortname] = {}
        return {}
    finally:
        if owns:
            await client.aclose()

    metadata: dict[str, dict[str, str]] = {}
    for row in csv.DictReader(StringIO(content)):
        uri = (row.get("URI") or "").strip()
        if not uri or _is_provenance_uri(uri):
            continue
        edge_property_of = (row.get("EdgePropertyOf") or "").strip()
        if uri in metadata and edge_property_of:
            # A single edge-property URI can belong to several relationships
            # (e.g. adj_p_value on both EXPRESSION and ABUNDANCE). Accumulate
            # the parents semicolon-separated so the join below finds them all.
            existing = metadata[uri].get("edge_property_of", "")
            metadata[uri]["edge_property_of"] = (
                f"{existing};{edge_property_of}" if existing else edge_property_of
            )
        else:
            metadata[uri] = {
                "label": (row.get("Label") or "").strip(),
                "description": (row.get("Description") or "").strip(),
                "type": (row.get("Type") or "").strip(),
                "edge_property_of": edge_property_of,
                "source_class": (row.get("SourceClass") or "").strip(),
                "target_class": (row.get("TargetClass") or "").strip(),
            }

    _metadata_cache[shortname] = metadata
    return metadata


def _generate_query_template(
    shortname: str,
    relationship_label: str,
    source_class: str,
    target_class: str,
    properties: list[dict[str, Any]],
) -> str:
    """Generate a SPARQL template for a reified relationship with edge properties."""
    source_var = source_class.lower() if source_class else "source"
    target_var = target_class.lower() if target_class else "target"
    schema_ns = _SCHEMA_NS.format(shortname=shortname)

    prop_selects = [f"?{p['label']}" for p in properties]
    prop_patterns = [f"        schema:{p['label']} ?{p['label']} ;" for p in properties]
    if prop_patterns:
        prop_patterns[-1] = prop_patterns[-1].rstrip(" ;") + " ."

    return (
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
        f"PREFIX schema: <{schema_ns}>\n\n"
        f"SELECT ?{source_var} ?{target_var} {' '.join(prop_selects)}\n"
        "WHERE {\n"
        f"  ?stmt rdf:subject ?{source_var} ;\n"
        f"        rdf:predicate schema:{relationship_label} ;\n"
        f"        rdf:object ?{target_var} ;\n"
        f"{chr(10).join(prop_patterns)}\n"
        "}"
    )


def _build_schema_from_metadata(
    shortname: str, entity_metadata: dict[str, dict[str, str]], compact: bool
) -> dict[str, Any]:
    """Build the schema response from curated entity metadata."""
    classes: list[dict[str, str]] = []
    predicates: list[dict[str, Any]] = []
    edge_properties_dict: dict[str, list[dict[str, str]]] = {}
    node_properties: list[dict[str, str]] = []

    for uri, meta in entity_metadata.items():
        entity_type = (meta.get("type") or "").lower()
        if entity_type == "class":
            classes.append(
                {
                    "uri": uri,
                    "label": meta.get("label", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
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

    # Flag predicates that carry edge properties (match on short name).
    for pred in predicates:
        if pred["short_name"] in edge_properties_dict:
            pred["has_edge_properties"] = True

    edge_properties_output: dict[str, Any] = {}
    for relationship_label, props in edge_properties_dict.items():
        rel = next(
            (p for p in predicates if p["short_name"] == relationship_label), None
        )
        if rel is None:
            continue
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
            ),
        }

    result: dict[str, Any] = {
        "classes": {
            "columns": ["uri", "label", "description", "type"],
            "data": [
                [c["uri"], c["label"], c["description"], c["type"]] for c in classes
            ],
            "count": len(classes),
        },
        "predicates": {
            "columns": [
                "uri",
                "label",
                "description",
                "type",
                "source_class",
                "target_class",
                "has_edge_properties",
            ],
            "data": [
                [
                    p["uri"],
                    p["label"],
                    p["description"],
                    p["type"],
                    p["source_class"],
                    p["target_class"],
                    p["has_edge_properties"],
                ]
                for p in predicates
            ],
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

    Used when no curated entity metadata exists for the KG. Scopes each query to
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

    Prefers curated entity metadata; falls back to probing the federation
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

    return {"shortname": shortname, "schema": schema}


# ── Mermaid class-diagram generation ─────────────────────────────────────────


def _local_name(uri: str) -> str:
    """Return the last path/fragment segment of a URI."""
    return re.split(r"[/#]", uri.rstrip("/#"))[-1] if uri else uri


def _mermaid_id(name: str) -> str:
    """Sanitize a label or URI into a Mermaid-safe class identifier."""
    if name.startswith(("http://", "https://")):
        name = _local_name(name)
    ident = re.sub(r"\W+", "_", name or "").strip("_")
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
    """Strip characters that would break a Mermaid relationship label."""
    return re.sub(
        r"\s+", " ", (label or "").replace("|", " ").replace("\n", " ")
    ).strip()


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


def build_mermaid_diagram(
    shortname: str,
    schema: dict[str, Any],
    inferred_edges: list[tuple[str, str, str]] | None = None,
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
    """
    classes_tbl = schema.get("classes", {})
    predicates_tbl = schema.get("predicates", {})
    node_props_tbl = schema.get("node_properties", {})
    edge_properties = schema.get("edge_properties", {}) or {}

    declared: dict[str, list[str]] = {}  # class id -> member lines (insertion order)
    relationships: list[str] = []
    undrawn: list[str] = []
    edge_class_ids: list[str] = []  # intermediary classes (styled distinctly)

    def ensure_class(label: str) -> str:
        cid = _mermaid_id(label)
        declared.setdefault(cid, [])
        return cid

    # Node classes (column layout: [uri, label, ...] for metadata, [uri] for probe).
    cls_cols = classes_tbl.get("columns", [])
    label_idx = cls_cols.index("label") if "label" in cls_cols else None
    for row in classes_tbl.get("data", []):
        if not row:
            continue
        label = row[label_idx] if label_idx is not None and len(row) > label_idx else ""
        ensure_class(label or _local_name(row[0]))

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
        if not owner or not name:
            continue
        cid = ensure_class(owner)
        desc = row[np_desc] if np_desc is not None and len(row) > np_desc else ""
        member = f"{_member_type(desc)} {_mermaid_id(name)}".strip()
        if member not in declared[cid]:
            declared[cid].append(member)

    # Edge predicates with properties → intermediary classes.
    for rel_label, info in edge_properties.items():
        edge_id = _mermaid_id(rel_label)
        members = []
        for prop in info.get("properties", []):
            mtype = _member_type(prop.get("description", ""))
            member = f"{mtype} {_mermaid_id(prop.get('label', ''))}".strip()
            if member and member not in members:
                members.append(member)
        declared[edge_id] = members
        if edge_id not in edge_class_ids:
            edge_class_ids.append(edge_id)
        src, tgt = info.get("source_class", ""), info.get("target_class", "")
        if src:
            relationships.append(f"  {ensure_class(src)} --> {edge_id}")
        if tgt:
            relationships.append(f"  {edge_id} --> {ensure_class(tgt)}")

    # Edges inferred from the graph's domain/range (when curated metadata lacks
    # endpoints). Their predicate labels are excluded from the "undrawn" list.
    inferred_labels: set[str] = set()
    for src, pred, tgt in inferred_edges or []:
        relationships.append(
            f"  {ensure_class(src)} --> {ensure_class(tgt)} : {_clean_edge_label(pred)}"
        )
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
        label = row[p_label] if p_label is not None and len(row) > p_label else ""
        label = label or _local_name(row[0])
        src = row[p_src] if p_src is not None and len(row) > p_src else ""
        tgt = row[p_tgt] if p_tgt is not None and len(row) > p_tgt else ""
        if src and tgt:
            relationships.append(
                f"  {ensure_class(src)} --> {ensure_class(tgt)} : {_clean_edge_label(label)}"
            )
        elif label not in inferred_labels:
            undrawn.append(_clean_edge_label(label))

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

    if undrawn:
        lines.append("  %% Predicates without source/target metadata (not drawn):")
        lines += [f"  %%   - {p}" for p in undrawn]

    return "\n".join(lines)


async def visualize_schema(shortname: str) -> dict[str, Any]:
    """Build a Mermaid ``classDiagram`` of a KG's schema, server-side.

    Returns ``{"shortname", "mermaid"}`` on success, or ``{"shortname",
    "error"}`` when the KG has no enumerable schema (e.g. ``ubergraph``).
    """
    result = await get_schema(shortname, compact=True)
    if "error" in result:
        return {"shortname": shortname, "error": result["error"]}
    schema = result["schema"]
    inferred = await infer_edge_labels(shortname, schema)
    diagram = build_mermaid_diagram(shortname, schema, inferred_edges=inferred)
    return {"shortname": shortname, "mermaid": diagram}

"""Identifier/namespace probing tools: probe_namespaces, find_crosswalks."""

from __future__ import annotations

import asyncio
from typing import Any

from .. import crosswalks as crosswalk_table
from ..app import mcp
from ..sparql import (
    SparqlError,
    canonicalize_schema_org_iri,
    named_graph,
    run_sparql,
)
from ._shared import _to_uri

# Common non-OBO prefixes we can expand so a caller may pass a CURIE predicate
# (e.g. `schema:healthCondition`) rather than the full IRI.
_PREDICATE_PREFIXES = {
    "schema": "http://schema.org/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "owl": "http://www.w3.org/2002/07/owl#",
}


# Per-term namespace classification, applied inside the GROUP BY below.
#  * Literal terms (e.g. `oboInOwl:hasDbXref` values like `OMIM:143100`,
#    `GC_ID:1`, `GOC:TermGenie`) are CURIE strings: report the prefix before the
#    first `:` (`OMIM`, `GC_ID`, `GOC`), else the whole literal.
#  * IRI terms: take the local part (after the last `/`/`#`); if it looks like
#    an ontology id — alpha prefix, `_`/`:`, then an alphanumeric id containing a
#    digit (`MONDO_0005240`, `NCIT_C3137`) — report the prefix, else fall back to
#    the base IRI namespace. Requiring a digit avoids splitting `foo_bar` locals.
def _ns_classify(var: str = "o") -> str:
    """BIND block classifying ?<var> into ?namespace (an ontology/CURIE prefix or
    base IRI namespace). Parameterized on the term variable so the same logic
    profiles a predicate's OBJECTS (?o) or an arbitrary NODE IRI (?n) — the latter
    needed when an id is encoded as the node itself, not via a mapping predicate.
    """
    s, loc = f"{var}str", f"{var}local"
    return f"""\
  BIND(STR(?{var}) AS ?{s})
  BIND(REPLACE(?{s}, "^.*[/#]", "") AS ?{loc})
  BIND(
    IF(isLiteral(?{var}),
       IF(REGEX(?{s}, "^[A-Za-z][A-Za-z0-9_.]*:"),
          REPLACE(?{s}, "^([A-Za-z][A-Za-z0-9_.]*):.*$", "$1"),
          ?{s}),
       IF(REGEX(?{loc}, "^[A-Za-z][A-Za-z0-9]*[_:][A-Za-z0-9]*[0-9]"),
          REPLACE(?{loc}, "^([A-Za-z][A-Za-z0-9]*)[_:].*$", "$1"),
          REPLACE(?{s}, "[^/#]*$", ""))) AS ?namespace
  )"""


_NS_CLASSIFY = _ns_classify("o")


def _namespace_query(ng: str, pred: str, sample: int = 0) -> str:
    """Build the namespace-distribution query for a predicate's objects.

    Grouped + counted server-side so one query answers "which vocabularies
    populate this edge". When ``sample > 0`` the objects are first capped by an
    inner ``LIMIT`` subquery — a fast, representative profile for huge predicates
    where a full scan would time out — otherwise every object is counted exactly.
    """
    triple = f"GRAPH <{ng}> {{ ?s <{pred}> ?o . }}"
    inner = (
        triple
        if sample <= 0
        else f"{{ SELECT ?o WHERE {{ {triple} }} LIMIT {sample} }}"
    )
    return (
        "SELECT ?namespace (COUNT(*) AS ?count) WHERE {\n"
        f"  {inner}\n"
        f"{_NS_CLASSIFY}\n"
        "}\n"
        "GROUP BY ?namespace\n"
        "ORDER BY DESC(?count)\n"
    )


def _undercount_note(namespaces: list[dict[str, Any]]) -> str | None:
    """Warn when objects span 2+ identifier namespaces, so a single-namespace
    join (or only-direct-ontology-links) silently UNDERCOUNTS — the partial-result
    failure that looks like success. None when there's only one namespace."""
    names = [n["namespace"] for n in namespaces if n.get("namespace")]
    if len(names) < 2:
        return None
    return (
        f"Objects span {len(names)} identifier namespaces ({', '.join(names[:6])}"
        f"{', …' if len(names) > 6 else ''}). Entities are SPLIT across them, so "
        "joining on just one — or on only the direct ontology links — UNDERCOUNTS "
        "and looks like a complete answer. To capture them all, UNION the "
        "per-namespace joins, or bridge non-ontology ids to MONDO via ubergraph "
        "(oboInOwl:hasDbXref / skos:exactMatch)."
    )


def _split_predicate_note(carriers: list[dict[str, Any]]) -> str | None:
    """Warn when one identifier namespace is reachable through 2+ predicates with
    DIFFERING distinct-id counts, so a recipe that joins on a single predicate
    silently UNDERCOUNTS — the predicate-position analogue of the cross-namespace
    split (`_undercount_note`). The trap case: a disease IRI that is the object of
    BOTH ``biolink:subject`` and ``biolink:object`` (oard-kg), where joining on
    one position drops the rest. ``carriers`` is one entry per namespace, each
    ``{"namespace", "predicates": [(predicate, count), ...]}`` busiest first; only
    those with 2+ predicates of diverging counts are a true split. None when none
    qualify."""
    split = [
        c
        for c in carriers
        if c.get("namespace")
        and len(c.get("predicates", [])) >= 2
        and c["predicates"][0][1] > c["predicates"][-1][1]
    ]
    if not split:
        return None
    examples = [
        f"{c['namespace']} via "
        + ", ".join(f"{p} ({n})" for p, n in c["predicates"][:3])
        for c in split[:3]
    ]
    return (
        f"{len(split)} identifier namespace(s) are carried by MULTIPLE "
        f"predicates with differing counts ({'; '.join(examples)}). The entity is "
        "SPLIT across predicate positions, so joining on just one UNDERCOUNTS and "
        "looks like a complete answer. UNION the per-predicate joins "
        "(`{ ?x p1 ?id } UNION { ?y p2 ?id }`) to capture them all."
    )


def _crosswalk_note(
    crosswalks: list[dict[str, Any]],
    ontology_ids: list[dict[str, Any]],
    flat: list[dict[str, Any]],
    node_scan_failed: bool = False,
    sample: int = 0,
    split_carriers: list[dict[str, Any]] | None = None,
) -> str | None:
    """Compose the find_crosswalks note. Leads with the headline that ids exist
    only as node IRIs / domain objects when no mapping predicate carries them
    (the case that used to read as empty), then any incomplete-scan warning, then
    the cross-namespace undercount warning. None when nothing noteworthy."""
    parts: list[str] = []
    if node_scan_failed:
        retry = max(sample // 2, 20000) if sample > 0 else 100000
        parts.append(
            "The node-IRI / domain-predicate scan timed out, so `ontology_ids` is "
            f"INCOMPLETE — this KG is large. Retry with sample={retry} (or smaller) "
            "to profile a representative slice."
        )
    subj = [o for o in ontology_ids if o.get("role") == "subject"]
    if subj and not crosswalks:
        ns = ", ".join(dict.fromkeys(o["namespace"] for o in subj if o["namespace"]))
        parts.append(
            f"No mapping predicates, but this KG's OWN nodes are ontology IRIs "
            f"({ns}) — there is nothing to 'cross-walk': join another graph "
            "DIRECTLY on the node IRI (?s already equals the ontology term)."
        )
    elif ontology_ids and not crosswalks:
        parts.append(
            "No mapping predicates, but ontology ids ARE present (see "
            "`ontology_ids`) on domain predicates / node IRIs — join on those."
        )
    undercount = _undercount_note(flat)
    if undercount:
        parts.append(undercount)
    split = _split_predicate_note(split_carriers or [])
    if split:
        parts.append(split)
    return " ".join(parts) or None


def _predicate_to_iri(predicate: str) -> str | None:
    """Resolve a predicate (full IRI or known CURIE) to a full IRI, else None."""
    p = predicate.strip().strip("<>")
    if p.startswith(("http://", "https://")):
        return canonicalize_schema_org_iri(p)
    prefix, sep, local = p.partition(":")
    if sep and prefix in _PREDICATE_PREFIXES:
        return _PREDICATE_PREFIXES[prefix] + local
    expanded = _to_uri(p)  # OBO CURIE (e.g. MONDO:0005240) -> purl IRI
    return expanded if expanded.startswith("http") else None


@mcp.tool()
async def probe_namespaces(
    shortname: str, predicate: str, sample: int = 0
) -> dict[str, Any]:
    """Report which identifier/ontology namespaces populate a predicate's objects.

    Schema introspection (`get_schema`) tells you a KG's predicates but NOT which
    controlled vocabularies fill their object values — so it's easy to assume a
    single ontology (e.g. DOID) and miss a richer one (e.g. MONDO) that is also
    present. Call this BEFORE writing the main query whenever a predicate's
    objects are ontology terms (diseases, chemicals, genes, anatomy) to see the
    actual namespace distribution and pick the best identifier to join on.

    Args:
        shortname: The KG shortname (e.g. `nde`), as returned by `list_kgs`.
        predicate: The predicate whose objects to profile, as a full IRI or a
            known CURIE (`schema:healthCondition`, `rdfs:seeAlso`, `MONDO:...`).
            Get the exact predicate from `get_schema`.
        sample: 0 (default) counts every object exactly. Set a positive N to
            profile only the first N objects via an inner `LIMIT` — a fast,
            representative distribution for very large predicates where a full
            scan would time out. Counts are then over the sample, not the graph.

    Returns:
        `{"shortname", "predicate", "namespaces": [{"namespace", "count"}, ...]
        sorted by count desc, "total", "sampled"}`. A `namespace` is an ontology
        prefix (`MONDO`, `DOID`, `MeSH`) when objects are CURIE-style, else the
        base IRI namespace; an OBO prefix (MONDO/DOID/HP/CHEBI/…) can then be
        joined to ubergraph's `rdfs:subClassOf*` hierarchy for category
        expansion. `sampled` is the `LIMIT` used, or null for an exact full scan.

    This is an exploratory probe — it is NOT recorded in the session/transcript.
    """
    iri = _predicate_to_iri(predicate)
    if iri is None:
        return {
            "error": (
                f"Could not resolve predicate {predicate!r}. Pass a full IRI, or "
                f"a known CURIE ({', '.join(sorted(_PREDICATE_PREFIXES))}, or an "
                f"OBO prefix like MONDO:). Get the predicate IRI from get_schema."
            )
        }
    query = _namespace_query(named_graph(shortname), iri, sample=sample)
    try:
        result = await run_sparql(query, fmt="json")
    except SparqlError as exc:
        return {"error": str(exc)}
    namespaces = [
        {"namespace": r.get("namespace"), "count": int(r.get("count", 0))}
        for r in result.get("rows", [])
    ]
    return {
        "shortname": shortname,
        "predicate": iri,
        "namespaces": namespaces,
        "total": sum(n["count"] for n in namespaces),
        "sampled": sample if sample > 0 else None,
        "note": _undercount_note(namespaces),
    }


# Standard predicates that cross-reference external ontology / database ids.
# These generic RDF/SKOS/OWL/schema.org terms are where ontology ids most often
# hide — and being generic, a KG's curated schema either omits them or buries
# them among hundreds of domain predicates, so they're easy to overlook.
# `oboInOwl:hasDbXref` is the key OBO bridge: ubergraph's MONDO/HP/CHEBI terms
# carry CURIE-form cross-refs there (OMIM:143100, UMLS:C0020179, MESH:D006816,
# DOID:12858, …), so it links an ontology term to the many db ids a target KG
# might store in IRI form (e.g. ProKN's `https://www.omim.org/entry/143100`).
_CROSSWALK_PREDICATES = {
    "rdfs:seeAlso": "http://www.w3.org/2000/01/rdf-schema#seeAlso",
    "owl:sameAs": "http://www.w3.org/2002/07/owl#sameAs",
    "schema:sameAs": "http://schema.org/sameAs",
    "skos:exactMatch": "http://www.w3.org/2004/02/skos/core#exactMatch",
    "skos:closeMatch": "http://www.w3.org/2004/02/skos/core#closeMatch",
    "skos:relatedMatch": "http://www.w3.org/2004/02/skos/core#relatedMatch",
    "skos:narrowMatch": "http://www.w3.org/2004/02/skos/core#narrowMatch",
    "skos:broadMatch": "http://www.w3.org/2004/02/skos/core#broadMatch",
    "oboInOwl:hasDbXref": "http://www.geneontology.org/formats/oboInOwl#hasDbXref",
}


def _crosswalk_query(ng: str, sample: int = 0) -> str:
    """Build a query profiling every crosswalk predicate's object namespaces.

    One query over all mapping predicates (via ``VALUES``), grouped by predicate
    and namespace. ``sample > 0`` caps objects with an inner ``LIMIT`` for KGs
    where a mapping predicate (e.g. ``rdfs:seeAlso``) is very large.
    """
    values = " ".join(f"<{iri}>" for iri in _CROSSWALK_PREDICATES.values())
    pattern = f"VALUES ?pred {{ {values} }}\n  GRAPH <{ng}> {{ ?s ?pred ?o . }}"
    inner = (
        pattern
        if sample <= 0
        else f"{{ SELECT ?pred ?o WHERE {{ {pattern} }} LIMIT {sample} }}"
    )
    return (
        "SELECT ?pred ?namespace (COUNT(*) AS ?count) WHERE {\n"
        f"  {inner}\n"
        f"{_NS_CLASSIFY}\n"
        "}\n"
        "GROUP BY ?pred ?namespace\n"
        "ORDER BY DESC(?count)\n"
    )


# Id-bearing IRI namespaces a node can live in DIRECTLY — not via a mapping
# predicate. OBO purl terms cover the case where a KG's entities ARE ontology
# IRIs (rdkg's diseases are `obo/MONDO_…`); identifiers.org covers database ids
# in IRI form (NCBI Gene, Ensembl, …). A `STRSTARTS` prefilter lets the store
# skip every non-id triple, keeping the all-predicate scan tractable.
_NODE_ID_IRI_PREFIXES = (
    "http://purl.obolibrary.org/obo/",
    "http://identifiers.org/",
    "https://identifiers.org/",
)


def _ontology_id_query(ng: str, role: str, sample: int = 0) -> str:
    """Build a query finding ids encoded AS node IRIs or domain-predicate objects.

    The mapping-predicate scan (`_crosswalk_query`) is blind to ids that aren't
    hung off `rdfs:seeAlso` / `skos:exactMatch` / … — namely ids baked into the
    node IRI itself (rdkg's diseases are `obo/MONDO_…` IRIs) or carried by an
    arbitrary DOMAIN predicate. This scans the triples whose ``role`` end
    (``subject`` or ``object``) is an id-bearing IRI, classifies its namespace,
    and groups by ``(predicate, namespace)`` — surfacing the join key regardless
    of which predicate (if any) it rides on. The predicate is incidental for a
    node-IRI (subject) join — you join on the IRI itself — but names the edge for
    a domain-predicate (object) join; `find_crosswalks` collapses the
    per-predicate rows back to one row per namespace. Counts are ``DISTINCT``
    nodes — i.e. how many join keys exist. ``sample > 0`` caps the scan via an
    inner ``LIMIT``.

    The two roles are deliberately SEPARATE queries (run concurrently by
    `find_crosswalks`): a KG often has ids in only one position, so the other
    role's scan finds nothing and, on a large KG, runs the store to a timeout —
    splitting them means that fruitless scan can't take the productive one down
    with it. Grouping is kept explicit per predicate rather than via
    ``GROUP_CONCAT``, which the FRINK federation engine leaves unbound.
    """
    triple = "?n ?pred ?x ." if role == "subject" else "?x ?pred ?n ."
    prefixes = " || ".join(f'STRSTARTS(STR(?n), "{p}")' for p in _NODE_ID_IRI_PREFIXES)
    # The id-bearing FILTER lives INSIDE the scan so that, when sampling, the
    # LIMIT caps already-filtered id triples — not arbitrary triples that may all
    # be filtered away (oard-kg's first rows are reified-association nodes, so a
    # filter-after-LIMIT scan finds nothing). `?n` is the id node in either role.
    body = f"GRAPH <{ng}> {{ {triple} }} FILTER(isIRI(?n)) FILTER({prefixes})"
    if sample > 0:
        body = f"{{ SELECT ?n ?pred WHERE {{ {body} }} LIMIT {sample} }}"
    return (
        "SELECT ?pred ?namespace (COUNT(DISTINCT ?n) AS ?count) WHERE {\n"
        f"  {body}\n"
        f"{_ns_classify('n')}\n"
        "}\n"
        "GROUP BY ?pred ?namespace\n"
        "ORDER BY DESC(?count)\n"
    )


@mcp.tool()
async def find_crosswalks(shortname: str, sample: int = 0) -> dict[str, Any]:
    """Find ontology/database ids in a KG, however they are encoded.

    Ontology ids (MONDO, CHEBI, NCBI Gene, …) hide in THREE places, and a KG that
    "lacks" the id you need usually just encodes it somewhere non-obvious. This
    profiles all three at once:

    1. MAPPING predicates — `rdfs:seeAlso`, `owl:sameAs`, `schema:sameAs`, the
       SKOS `*Match` predicates, `oboInOwl:hasDbXref`. Generic, so `get_schema`
       often omits them or buries them among hundreds of predicates. Returned
       under `crosswalks`, per predicate.
    2. NODE IRIs — the entity's OWN IRI is the ontology term (rdkg's diseases ARE
       `obo/MONDO_…` IRIs; ids may also be `identifiers.org/…`). No mapping
       predicate exists; you join DIRECTLY on the node IRI. Returned under
       `ontology_ids` with `role="subject"`.
    3. DOMAIN predicates — the id is the object of an arbitrary, KG-specific
       predicate (not one of the mapping set). Returned under `ontology_ids`
       with `role="object"` and the carrying predicate.

    Cases 2 and 3 are invisible to a mapping-predicate-only scan — they are
    exactly why `find_crosswalks` used to return empty for KGs (rdkg, oard-kg,
    biobricks-ice, biomarkerkg) that in fact carry rich ontology ids. Use this
    whenever a KG seems to lack the identifier you need on its obvious predicates.

    Args:
        shortname: KG shortname (e.g. `prokn`), as returned by `list_kgs`.
        sample: 0 (default) counts exactly; a positive N caps each scan via an
            inner `LIMIT` for KGs where a predicate or the node-IRI scan is very
            large. Counts are then over the sample, not the graph.

    Returns:
        `{"shortname", "crosswalks": [{"predicate", "predicate_iri", "namespaces":
        [{"namespace", "count"}, ...], "total"}, ...], "ontology_ids": [{"role",
        "namespace", "count", "predicates": [...]}, ...], "sampled"}`.
        `crosswalks` lists mapping predicates (busiest first; namespaces by count
        desc). `ontology_ids` lists ids encoded as node IRIs (`role="subject"`) or
        as domain-predicate objects (`role="object"`), one row per id family,
        busiest first; `count` is DISTINCT ids — i.e. how many join keys — and
        `predicates` are the edges they ride on. Any OBO prefix (MONDO/CHEBI/…) can
        be joined to ubergraph's `rdfs:subClassOf*`. When `ontology_ids` shows a
        `subject`-role namespace, the join is direct: the KG's nodes ARE those
        IRIs, so `?s` already equals the ontology term in the other graph.

    CROSS-KG BRIDGING: when a KG stores ids in an EXTERNAL IRI form that no
    ontology shares directly (e.g. ProKN's diseases as `https://www.omim.org/
    entry/100100`), two bridges through `ubergraph` work:
      1. `oboInOwl:hasDbXref` — MONDO/HP/CHEBI terms hold CURIE cross-refs
         (`OMIM:100100`, `UMLS:C...`, `MESH:D...`). Extract the bare id from the
         KG's IRI, rebuild the CURIE, and join `?mondo oboInOwl:hasDbXref
         "OMIM:100100"`. PREFERRED — CURIEs sidestep IRI-form mismatches.
      2. `skos:exactMatch` — MONDO terms link to OMIM as IRIs, BUT ubergraph uses
         `https://omim.org/entry/100100` while ProKN uses `https://www.omim.org/
         entry/100100` (note the missing `www.`). A direct join silently matches
         nothing; rewrite at query time, e.g. `BIND(IRI(REPLACE(STR(?omim),
         "://www\\.omim", "://omim")) AS ?ug_omim)`, then join on `?ug_omim`.
    Either way ubergraph also gives you the `subClassOf*` hierarchy. Beware IRI-
    form drift across graphs generally (subdomain, http/https, trailing slash).

    This is an exploratory probe — it is NOT recorded in the session/transcript.
    """
    iri_to_curie = {v: k for k, v in _CROSSWALK_PREDICATES.items()}
    ng = named_graph(shortname)
    # Three independent scans run concurrently: mapping predicates, plus id-bearing
    # node IRIs in the SUBJECT and OBJECT positions (separate so a fruitless scan
    # of one role can't time out the other). Each degrades on its own — a slow
    # node scan never hides the crosswalks, nor one role the other.
    gathered = await asyncio.gather(
        run_sparql(_crosswalk_query(ng, sample=sample), fmt="json"),
        run_sparql(_ontology_id_query(ng, "subject", sample=sample), fmt="json"),
        run_sparql(_ontology_id_query(ng, "object", sample=sample), fmt="json"),
        return_exceptions=True,
    )
    map_res, subj_res, obj_res = gathered
    # Surface only SparqlError as a soft error; let unexpected exceptions bubble.
    for res in (map_res, subj_res, obj_res):
        if isinstance(res, Exception) and not isinstance(res, SparqlError):
            raise res
    if all(isinstance(r, SparqlError) for r in (map_res, subj_res, obj_res)):
        return {"error": str(map_res)}

    crosswalks: list[dict[str, Any]] = []
    if not isinstance(map_res, BaseException):
        by_pred: dict[str, list[dict[str, Any]]] = {}
        for r in map_res.get("rows", []):
            by_pred.setdefault(r.get("pred"), []).append(
                {"namespace": r.get("namespace"), "count": int(r.get("count", 0))}
            )
        crosswalks = [
            {
                "predicate": iri_to_curie.get(pred, pred),
                "predicate_iri": pred,
                "namespaces": sorted(ns, key=lambda n: n["count"], reverse=True),
                "total": sum(n["count"] for n in ns),
            }
            for pred, ns in by_pred.items()
        ]
        crosswalks.sort(key=lambda c: c["total"], reverse=True)

    # Collapse each role's per-(predicate, namespace) rows to one row per
    # namespace. The same id appears under several predicates, so distinct counts
    # can't be summed — take the max (a node carrying every predicate is counted
    # once) and list the carrying predicates, busiest first (the edge to join on
    # for an object-role id).
    ontology_ids: list[dict[str, Any]] = []
    # Per namespace, the distinct-id count each predicate carries (across BOTH
    # roles) — feeds the split-predicate undercount warning below.
    ns_preds: dict[str, dict[str, int]] = {}
    for role, res in (("subject", subj_res), ("object", obj_res)):
        if isinstance(res, BaseException):
            continue
        by_ns: dict[str, dict[str, Any]] = {}
        for r in res.get("rows", []):
            ns = r.get("namespace")
            cnt = int(r.get("count", 0))
            pred = iri_to_curie.get(r.get("pred"), r.get("pred"))
            entry = by_ns.setdefault(
                ns, {"role": role, "namespace": ns, "count": 0, "_preds": {}}
            )
            entry["count"] = max(entry["count"], cnt)
            if pred:
                entry["_preds"][pred] = max(entry["_preds"].get(pred, 0), cnt)
                pc = ns_preds.setdefault(ns, {})
                pc[pred] = max(pc.get(pred, 0), cnt)
        ontology_ids.extend(
            {
                "role": e["role"],
                "namespace": e["namespace"],
                "count": e["count"],
                "predicates": sorted(e["_preds"], key=e["_preds"].get, reverse=True),
            }
            for e in by_ns.values()
        )
    ontology_ids.sort(key=lambda o: o["count"], reverse=True)

    # Flatten distinct namespaces across BOTH scans for the undercount note.
    seen: dict[str, int] = {}
    for c in crosswalks:
        for n in c["namespaces"]:
            if n["namespace"]:
                seen[n["namespace"]] = seen.get(n["namespace"], 0) + n["count"]
    for o in ontology_ids:
        if o["namespace"]:
            seen[o["namespace"]] = seen.get(o["namespace"], 0) + o["count"]
    flat = [{"namespace": k, "count": v} for k, v in seen.items()]
    # Per namespace, the predicates that carry it (busiest first). A namespace
    # carried by 2+ predicates with differing counts is split across predicate
    # positions — joining on one undercounts (the oard-kg MONDO case). The
    # divergence filter lives in `_split_predicate_note`.
    split_carriers = [
        {
            "namespace": ns,
            "predicates": sorted(preds.items(), key=lambda kv: kv[1], reverse=True),
        }
        for ns, preds in ns_preds.items()
    ]
    split_carriers.sort(key=lambda c: c["predicates"][0][1], reverse=True)
    note = _crosswalk_note(
        crosswalks,
        ontology_ids,
        flat,
        node_scan_failed=isinstance(subj_res, SparqlError)
        or isinstance(obj_res, SparqlError),
        sample=sample,
        split_carriers=split_carriers,
    )
    # Point at the verified precomputed table when it covers this KG — those join
    # recipes are reliable where this live scan is not.
    precomputed = crosswalk_table.verified_for(shortname)
    if precomputed:
        hint = (
            f"{len(precomputed)} VERIFIED precomputed join(s) exist for "
            f"'{shortname}' — call `get_join_strategy('{shortname}')` for "
            "ready-to-use recipes instead of relying on this live scan."
        )
        note = f"{hint} {note}" if note else hint
    return {
        "shortname": shortname,
        "crosswalks": crosswalks,
        "ontology_ids": ontology_ids,
        "sampled": sample if sample > 0 else None,
        "note": note,
    }

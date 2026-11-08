"""Check a SPARQL query before it is sent: scan shapes, scoping slips, prefixes.

In the v0.3.0 benchmark (2,005 queries, 360 episodes), about 5% of queries took
roughly 38% of all endpoint time. Most of them ran into the 120 s client timeout,
and each wasted two minutes of the agent's run. A later run on this branch showed
which failures were still left: in about 850 queries, 28 QLever "Tried to allocate
235 GB" errors, 18 timeouts and 16 undeclared prefixes. Each costs the agent a turn
and often several, and each comes from one of a few shapes, checked here:

1. **All-variable scan** (:func:`scan_problem`): a triple ``?s ?p ?o`` with nothing
   anchoring it, constrained only by a string FILTER, e.g.
   ``?s ?p ?o FILTER(CONTAINS(STR(?o), "E-MTAB-5477"))``. The engine has to read
   every triple in the graph to apply the filter.
2. **Label scan**: ``?t rdfs:label ?l FILTER(LCASE(STR(?l)) = "autoimmune
   disease")``. An exact literal (``?t rdfs:label "autoimmune disease"``) is an
   index lookup, and ``lookup_term`` does exactly that.
3. **An anchor that cannot reach inside a group** (:func:`isolated_scan`). QLever
   evaluates each UNION branch, MINUS and EXISTS on its own, before joining it to
   the rest of the query. ``VALUES ?u {…} { ?u ?p ?o } UNION { ?o ?p ?u }`` looks
   anchored, but inside the second branch ``?o ?p ?u`` is a scan of the whole
   store, and QLever fails at once ("Tried to allocate 235.1 GB") or times out.
   Repeating the anchor inside each branch runs in under a second. These fail
   every time, so they are not sent.
4. **Scoping slips** (:func:`scope_warnings`). ``{ BIND(?s AS ?x) } UNION
   { BIND(?o AS ?x) }`` binds nothing: a group's BIND sees only that group, so
   ``?x`` stays unbound and the query silently matches everything. The same goes
   for a FILTER inside a branch that names a variable bound outside it. These
   queries run, and the reply carries a warning.
5. **Undeclared standard prefixes** (:func:`add_missing_prefixes`): ``xsd:`` above
   all (52 of 71 such errors across the recorded runs). The declaration is added
   and the reply says so.

Shapes 1 and 2 are not refused: a short time limit (:data:`SCAN_TIMEOUT`) keeps the
ones that finish (21 of 85 flagged in the v0.3.0 replay, some of them cached) and
stops the rest after seconds instead of minutes. A variable is *anchored* when a
triple ties it to a constant subject or object, when VALUES binds it, or when a
triple links it to an anchored variable. A query rdflib cannot parse is never
flagged: the endpoint reports its own errors.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from rdflib.paths import Path
from rdflib.term import Literal, URIRef, Variable

#: rdflib names of the builtins that make a FILTER a string match.
_STRING_BUILTINS = frozenset(
    {
        "Builtin_CONTAINS",
        "Builtin_REGEX",
        "Builtin_STRSTARTS",
        "Builtin_STRENDS",
        "Builtin_LCASE",
        "Builtin_UCASE",
        "Builtin_STR",
    }
)

#: Label-like predicates; a string filter over their objects in ubergraph (or
#: under ``GRAPH ?g``) is shape 2. Other graphs are left alone: replayed over the
#: recorded runs, a 15 s limit there would have stopped 22 label filters that
#: succeeded in 15-54 s to save 16 that failed.
_LABEL_PREDICATES = frozenset(
    {
        "http://www.w3.org/2000/01/rdf-schema#label",
        "http://www.w3.org/2004/02/skos/core#prefLabel",
        "http://www.w3.org/2004/02/skos/core#altLabel",
        "http://www.geneontology.org/formats/oboInOwl#hasExactSynonym",
        "http://www.geneontology.org/formats/oboInOwl#hasRelatedSynonym",
        "http://www.geneontology.org/formats/oboInOwl#hasNarrowSynonym",
        "http://www.geneontology.org/formats/oboInOwl#hasBroadSynonym",
    }
)

_UBERGRAPH_SUFFIX = "/kg/ubergraph"

#: Seconds a flagged query may run. Every flagged query in the benchmark that
#: succeeded did so in under 5 s.
SCAN_TIMEOUT = 15.0

ALL_VARIABLE_ADVICE = (
    "This query was stopped after {seconds}s: `{triple}` has no anchor (no constant subject or "
    "object, no VALUES, no link to an anchored variable), so the string FILTER on "
    "{vars} would read every triple in the graph and time out. Instead: bind the "
    'value exactly (`?s ?p "E-MTAB-5477"` or `?s rdfs:label "asthma"@en`); anchor '
    "the subject to a class (`?s a <Class> ; ?p ?o`); or, to find a predicate by "
    "name, call `get_schema(kg, match='term')`. If you really mean to scan, call "
    "again with `allow_scan=True` (full time limit)."
)

UBERGRAPH_LABEL_ADVICE = (
    "This query was stopped after {seconds}s: a string FILTER over {vars} in "
    "{where} compares every label there, which times out. Use "
    '`lookup_term("<name>")` (an exact-name index lookup), or bind the label '
    'exactly: `?t rdfs:label "autoimmune disease"` (try `"…"@en` too). Restricting '
    "?t first (e.g. `?t a <Class>` or `?t rdfs:subClassOf* <root>`) also works. To "
    "scan anyway, call again with `allow_scan=True` (full time limit)."
)

ISOLATED_ADVICE = (
    "Not run: QLever evaluates each {kind} on its own before joining it to the "
    "rest of the query, so what binds {vars} outside it does not reach inside, and "
    "`{triple}` there would read every triple in the store (QLever fails with "
    '"Tried to allocate 235 GB", times out, or takes minutes). Repeat the anchor '
    "inside the "
    "{kind}: `{{ VALUES ?u {{…}} ?u ?p ?o }} UNION {{ VALUES ?u {{…}} ?o ?p ?u }}`, "
    "or `{{ ?u a <Class> . ?u ?p ?o }} UNION {{ ?u a <Class> . ?o ?p ?u }}`; or run "
    "each direction as its own query. (`allow_scan=True` sends it anyway.)"
)

BIND_SCOPE_WARNING = (
    "`BIND(… AS ?{target})` uses {vars}, which is bound only outside the group "
    "the BIND sits in (its {{ }}, GRAPH block, UNION branch or OPTIONAL). A BIND "
    "sees only its own group, so {vars} is unbound there and ?{target} comes out "
    "unbound or wrong (e.g. `{{ BIND(?s AS ?x) }} UNION {{ BIND(?o AS ?x) }}` binds "
    "nothing, and the query then matches far too much). Move the BIND to where "
    "{vars} is bound, or bind inside each branch, e.g. `{{ ?st rdf:subject ?x }} "
    "UNION {{ ?st rdf:object ?x }}`."
)

FILTER_SCOPE_WARNING = (
    "A FILTER inside a GRAPH block, nested {{ }} group or UNION branch uses "
    "{vars}, which is bound only outside that group. The group is evaluated on "
    "its own, so the variable is unbound there and the FILTER drops every row of "
    "the group (often the whole result). Move the FILTER outside, after both "
    "GRAPH blocks, e.g. `GRAPH <a> {{ … ?x … }} GRAPH <b> {{ … ?y … }} "
    "FILTER(?x = ?y)`."
)


# ── standard prefixes ────────────────────────────────────────────────────────

#: Prefixes whose meaning is unambiguous, added when a query uses one without
#: declaring it. ``schema:`` (http vs https), ``biolink:`` (two namespaces in the
#: federation) and ``kg:`` (one per graph) are deliberately absent.
STANDARD_PREFIXES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "dct": "http://purl.org/dc/terms/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "prov": "http://www.w3.org/ns/prov#",
    "bibo": "http://purl.org/ontology/bibo/",
    "obo": "http://purl.obolibrary.org/obo/",
    "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
    "sio": "http://semanticscience.org/resource/",
    "up": "http://purl.uniprot.org/core/",
    "geo": "http://www.opengis.net/ont/geosparql#",
    "sosa": "http://www.w3.org/ns/sosa/",
    "time": "http://www.w3.org/2006/time#",
    "qudt": "http://qudt.org/schema/qudt/",
}

#: Strings, IRIs and comments, which can contain text that looks like a prefixed name.
_OPAQUE = re.compile(
    r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\''
    r"|<[^<>\"{}|^`\\\s]*>|#[^\n]*"
)
_DECLARED = re.compile(r"(?i)\bPREFIX\s+([A-Za-z][\w.\-]*)?\s*:")
_USED = re.compile(r"(?<![\w?$:.\-])([A-Za-z][\w\-]*):(?=[A-Za-z0-9_%(])")


def undeclared_prefixes(query: str) -> list[str]:
    """Prefix names the query uses without a PREFIX declaration, in order of use."""
    bare = _OPAQUE.sub(" ", query)
    declared = {m.group(1) or "" for m in _DECLARED.finditer(bare)}
    names: list[str] = []
    for m in _USED.finditer(_DECLARED.sub(" ", bare)):
        name = m.group(1)
        if name not in declared and name not in names:
            names.append(name)
    return names


def add_missing_prefixes(
    query: str, graph_prefixes: Mapping[str, str] | None = None
) -> tuple[str, list[str]]:
    """Declare any standard prefix the query uses but doesn't declare.

    ``graph_prefixes`` adds names that are unambiguous for the graphs the query
    names (``biolink:``, ``wobd:`` as ``get_schema`` printed them); a standard
    prefix wins on a clash. Returns the (possibly) extended query and the names
    added, in order of use.
    """
    known = {**(graph_prefixes or {}), **STANDARD_PREFIXES}
    added = [n for n in undeclared_prefixes(query) if n in known]
    if not added:
        return query, []
    head = "".join(f"PREFIX {n}: <{known[n]}>\n" for n in added)
    return head + query, added


_GRAPH_KG = re.compile(r"<https?://purl\.org/okn/frink/kg/([A-Za-z0-9_.\-]+)>")


def named_kgs(query: str) -> list[str]:
    """Shortnames of the federation graphs a query names, in order of use."""
    seen: list[str] = []
    for m in _GRAPH_KG.finditer(query):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def unambiguous_prefixes(per_kg: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Prefix names that mean one namespace in every named graph that defines them.

    ``per_kg`` maps each graph to the ``{name: namespace}`` that ``get_schema``
    prints for its full schema. A name is dropped when two graphs disagree, and
    when its graph also has a numbered sibling (``vocab`` beside ``vocab2``): a
    ``match=`` view of that schema may have numbered them the other way round.
    """
    out: dict[str, str] = {}
    clash: set[str] = set()
    for prefixes in per_kg.values():
        for name, ns in prefixes.items():
            base = re.sub(r"\d+$", "", name)
            if base != name or any(
                other != name and re.fullmatch(re.escape(name) + r"\d+", other)
                for other in prefixes
            ):
                clash.add(name)
                clash.add(base)
            elif out.setdefault(name, ns) != ns:
                clash.add(name)
    return {n: ns for n, ns in out.items() if n not in clash}


_GRAPH_OPEN = re.compile(
    r"(?i)\bGRAPH\s*(?:<https?://purl\.org/okn/frink/kg/([A-Za-z0-9_.\-]+)>|[?$]\w+)\s*\{"
)


def _graph_spans(query: str) -> list[tuple[int, int, str | None]]:
    """``(start, end, kg)`` for every GRAPH block; ``kg`` is None for ``GRAPH ?g``.

    Strings and comments are blanked first (keeping offsets), so a brace or the
    word GRAPH inside them is not read as syntax.
    """
    texts = _OPAQUE.sub(
        lambda m: m.group() if m.group().startswith("<") else " " * len(m.group()),
        query,
    )
    bare = _OPAQUE.sub(lambda m: " " * len(m.group()), query)
    spans: list[tuple[int, int, str | None]] = []
    for m in _GRAPH_OPEN.finditer(texts):
        depth, i = 0, m.end() - 1
        while i < len(bare):
            if bare[i] == "{":
                depth += 1
            elif bare[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        spans.append((m.end(), i, m.group(1)))
    return spans


def graph_scoped_prefixes(
    query: str, per_kg: Mapping[str, Mapping[str, str]]
) -> dict[str, str]:
    """Undeclared prefixes resolved by the GRAPH blocks they are used in.

    A name used only inside ``GRAPH <…/kg/spoke-okn>`` blocks means what
    spoke-okn's ``get_schema`` printed, even when another named graph prints the
    same name for its own namespace (``kg:`` is one per graph). A use outside
    every named-graph block, or inside ``GRAPH ?g``, falls back to all the graphs
    in ``per_kg``, which must agree. Either way :func:`unambiguous_prefixes`
    decides over the graphs consulted.
    """
    bare = _OPAQUE.sub(lambda m: " " * len(m.group()), query)
    declared = {m.group(1) or "" for m in _DECLARED.finditer(bare)}
    bare = _DECLARED.sub(lambda m: " " * len(m.group()), bare)
    spans = _graph_spans(query)
    users: dict[str, set[str]] = {}
    unscoped: set[str] = set()
    for m in _USED.finditer(bare):
        name = m.group(1)
        if name in declared:
            continue
        inner = [s for s in spans if s[0] <= m.start() < s[1]]
        kg = min(inner, key=lambda s: s[1] - s[0])[2] if inner else None
        users.setdefault(name, set())
        if kg is None or kg not in per_kg:
            unscoped.add(name)
        else:
            users[name].add(kg)
    out: dict[str, str] = {}
    for name, kgs in users.items():
        consulted = per_kg if name in unscoped else {k: per_kg[k] for k in kgs}
        ns = unambiguous_prefixes(consulted).get(name)
        if ns:
            out[name] = ns
    return out


# ── algebra helpers ──────────────────────────────────────────────────────────


def _algebra(query: str) -> Any | None:
    try:
        from rdflib.plugins.sparql.algebra import translateQuery
        from rdflib.plugins.sparql.parser import parseQuery

        return translateQuery(parseQuery(query)).algebra
    except Exception:
        return None


def _exists_pattern(node: Any) -> Any | None:
    """The translated pattern of an EXISTS / NOT EXISTS expression."""
    try:
        from rdflib.plugins.sparql.algebra import translateGroupGraphPattern

        graph = node.get("graph")
        if getattr(graph, "name", None) == "GroupGraphPatternSub":
            return translateGroupGraphPattern(graph)
        return graph
    except Exception:
        return None


def _walk(node: Any, graph: Any, out: dict[str, list[Any]]) -> None:
    """Collect BGP triples (with their GRAPH term), filters and VALUES variables."""
    name = getattr(node, "name", None)
    if name == "Graph":
        _walk(node.get("p"), node.get("term"), out)
        return
    if name == "BGP":
        out["triples"] += [(t, graph) for t in node.get("triples") or []]
        return
    if name == "Filter":
        out["filters"].append(node.get("expr"))
    if name == "values":
        for row in node.get("res") or []:
            out["values"] += [v for v in row if isinstance(v, Variable)]
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "expr" and name == "Filter":
                continue
            _walk(value, graph, out)
    elif isinstance(node, list | tuple):
        for value in node:
            _walk(value, graph, out)


def _string_filter_vars(expr: Any) -> set[Variable]:
    """Variables used inside a string builtin anywhere in ``expr``."""
    found: set[Variable] = set()

    def visit(node: Any, inside: bool) -> None:
        if isinstance(node, Variable):
            if inside:
                found.add(node)
            return
        name = getattr(node, "name", None)
        now = inside or name in _STRING_BUILTINS
        if isinstance(node, dict):
            for value in node.values():
                visit(value, now)
        elif isinstance(node, list | tuple):
            for value in node:
                visit(value, now)

    visit(expr, False)
    return found


def _expr_vars(expr: Any) -> set[Variable]:
    """Variables an expression reads, leaving out EXISTS patterns."""
    found: set[Variable] = set()

    def visit(node: Any) -> None:
        if isinstance(node, Variable):
            found.add(node)
            return
        if getattr(node, "name", None) in ("Builtin_EXISTS", "Builtin_NOTEXISTS"):
            return
        if isinstance(node, dict):
            for key, value in node.items():
                if key != "_vars":
                    visit(value)
        elif isinstance(node, list | tuple):
            for value in node:
                visit(value)

    visit(expr)
    return found


def _is_constant(term: Any) -> bool:
    return isinstance(term, URIRef | Literal)


def _anchored(triples: list[tuple[Any, Any]], seeds: set[Variable]) -> set[Variable]:
    """Variables tied to a constant subject/object, VALUES, or each other."""
    anchored = set(seeds)
    for (s, _p, o), _g in triples:
        if _is_constant(s) or _is_constant(o):
            anchored |= {t for t in (s, o) if isinstance(t, Variable)}
    changed = True
    while changed:
        changed = False
        for (s, p, o), _g in triples:
            terms = {t for t in (s, p, o) if isinstance(t, Variable)}
            if terms & anchored and not terms <= anchored:
                # A link through a path or predicate variable still bounds the far
                # end by the anchored end.
                anchored |= terms
                changed = True
    return anchored


def _scope(node: Any) -> set[Variable]:
    """Variables a graph pattern can bind (its in-scope variables)."""
    name = getattr(node, "name", None)
    if name == "BGP":
        out: set[Variable] = set()
        for s, p, o in node.get("triples") or []:
            out |= {t for t in (s, p, o) if isinstance(t, Variable)}
        return out
    if name == "values":
        return {v for row in node.get("res") or [] for v in row}
    if name == "Extend":
        return _scope(node.get("p")) | {node.get("var")}
    if name == "Graph":
        term = node.get("term")
        return _scope(node.get("p")) | ({term} if isinstance(term, Variable) else set())
    if name == "Project":
        return set(node.get("PV") or [])
    if name == "Minus":
        return _scope(node.get("p1"))
    out = set()
    if isinstance(node, dict):
        for key in ("p", "p1", "p2"):
            if key in node:
                out |= _scope(node[key])
    return out


#: Algebra nodes QLever evaluates on their own: (node name, child key, label).
_ISOLATING = (
    ("Union", "p1", "UNION branch"),
    ("Union", "p2", "UNION branch"),
    ("Minus", "p2", "MINUS group"),
)


def _own_triples(node: Any, graph: Any = None) -> tuple[list[Any], set[Variable]]:
    """Triples and VALUES variables of a group, minus its isolated sub-groups.

    UNION branches, MINUS and OPTIONAL right sides are left out; a subquery
    adds the variables it projects and anchors, as VALUES would.
    """
    name = getattr(node, "name", None)
    if name == "Graph":
        return _own_triples(node.get("p"), node.get("term"))
    if name == "BGP":
        return [(t, graph) for t in node.get("triples") or []], set()
    if name == "values":
        return [], {v for row in node.get("res") or [] for v in row}
    if name == "Union":
        return [], set()
    if name == "Project":
        # A subquery joins like a VALUES block: the variables it projects and
        # anchors (`{ SELECT ?v { ?v a up:Disease } LIMIT 2 }`) are bound.
        body, seeds = _own_triples(_main_pattern(node))
        return [], _anchored(body, seeds) & set(node.get("PV") or [])
    if name in ("Minus", "LeftJoin"):
        return _own_triples(node.get("p1"), graph)
    triples: list[Any] = []
    values: set[Variable] = set()
    if isinstance(node, dict):
        for key in ("p", "p1", "p2"):
            if key in node:
                t, v = _own_triples(node[key], graph)
                triples += t
                values |= v
    return triples, values


def _groups(node: Any, out: list[tuple[str, Any, Any]], parent: Any = None) -> None:
    """Collect every isolated group, with a label and the group enclosing it.

    The enclosing group is the nearest UNION branch, MINUS / OPTIONAL / EXISTS
    group or subquery body around the node (None for the query's main group).
    """
    name = getattr(node, "name", None)
    if name == "Project":
        parent = _main_pattern(node)  # a subquery: its body is a group of its own
    for owner, key, label in _ISOLATING:
        if name == owner and key in node:
            out.append((label, node[key], parent))
    if name in ("Builtin_EXISTS", "Builtin_NOTEXISTS"):
        pattern = _exists_pattern(node)
        if pattern is not None:
            out.append(("EXISTS group", pattern, parent))
            _groups(pattern, out, pattern)
        return
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "_vars":
                continue
            child_parent = parent
            if (name == "Union" and key in ("p1", "p2")) or (
                name in ("Minus", "LeftJoin") and key == "p2"
            ):
                child_parent = value
            _groups(value, out, child_parent)
    elif isinstance(node, list | tuple):
        for value in node:
            _groups(value, out, parent)


#: The wrappers a query's own WHERE pattern sits in (not subqueries).
_WRAPPERS = frozenset(
    {
        "SelectQuery",
        "ConstructQuery",
        "AskQuery",
        "DescribeQuery",
        "Project",
        "Distinct",
        "Reduced",
        "Slice",
        "OrderBy",
        "Group",
        "AggregateJoin",
    }
)


def _main_pattern(algebra: Any) -> Any:
    """The query's WHERE pattern, below SELECT / DISTINCT / LIMIT / GROUP BY."""
    node = algebra
    while getattr(node, "name", None) in _WRAPPERS and "p" in node:
        node = node["p"]
    return node


def isolated_scan(algebra: Any) -> str | None:
    """Shape 3: an all-variable triple an outside anchor cannot reach."""
    # Anchors in the query's main group and in the group directly around the
    # isolated one: what the agent meant to reach inside.
    main_triples, main_values = _own_triples(_main_pattern(algebra))
    main_outside = _anchored(main_triples, main_values)
    groups: list[tuple[str, Any, Any]] = []
    _groups(_main_pattern(algebra), groups)
    for label, group, parent in groups:
        outside = main_outside
        if parent is not None:
            # Anchors in the group around this one (a subquery body, say).
            parent_triples, parent_values = _own_triples(parent)
            outside = outside | _anchored(parent_triples, parent_values)
        triples, values = _own_triples(group)
        inside = _anchored(triples, values)
        for (s, p, o), _graph in triples:
            terms = (s, p, o)
            if not all(isinstance(t, Variable) for t in terms):
                continue
            if set(terms) & inside:
                continue
            reached = sorted(set(terms) & outside)
            if reached:
                return ISOLATED_ADVICE.format(
                    kind=label,
                    vars=", ".join(f"?{v}" for v in reached),
                    triple=f"?{s} ?{p} ?{o}",
                )
    return None


def _all_vars(algebra: Any) -> set[Variable]:
    found: set[Variable] = set()

    def visit(node: Any) -> None:
        if isinstance(node, Variable):
            found.add(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key != "_vars":
                    visit(value)
        elif isinstance(node, list | tuple):
            for value in node:
                visit(value)

    visit(algebra)
    return found


def scope_warnings(algebra: Any) -> list[str]:
    """Shape 4: a BIND or FILTER naming a variable its group cannot see."""
    bindable = _bindable_vars(algebra)
    warnings: list[str] = []

    def visit(node: Any, nested: bool) -> None:
        name = getattr(node, "name", None)
        if name == "Extend":
            missing = sorted(
                (_expr_vars(node.get("expr")) & bindable) - _scope(node.get("p"))
            )
            if missing:
                warnings.append(
                    BIND_SCOPE_WARNING.format(
                        target=node.get("var"),
                        vars=", ".join(f"?{v}" for v in missing),
                    )
                )
        if name == "Filter" and nested:
            missing = sorted(
                (_expr_vars(node.get("expr")) & bindable) - _scope(node.get("p"))
            )
            if missing:
                warnings.append(
                    FILTER_SCOPE_WARNING.format(
                        vars=", ".join(f"?{v}" for v in missing)
                    )
                )
        for key in ("p", "p1", "p2"):
            if isinstance(node, dict) and key in node:
                # The operands of a join, a union and a MINUS are groups of their
                # own; a FILTER at their top only sees what they bind.
                child_nested = (
                    nested
                    or name in ("Union", "Join", "Minus")
                    or (name == "LeftJoin" and key == "p2")
                )
                visit(node[key], child_nested)

    visit(algebra, False)
    # One of each kind is enough to point at the slip.
    return list(dict.fromkeys(warnings))[:3]


def _bindable_vars(algebra: Any) -> set[Variable]:
    """Variables some triple, VALUES or BIND in the query can bind."""
    found: dict[str, list[Any]] = {"triples": [], "filters": [], "values": []}
    _walk(algebra, None, found)
    out = set(found["values"])
    for (s, p, o), _g in found["triples"]:
        out |= {t for t in (s, p, o) if isinstance(t, Variable)}

    def extends(node: Any) -> None:
        if getattr(node, "name", None) == "Extend":
            out.add(node.get("var"))
        if isinstance(node, dict):
            for key, value in node.items():
                if key != "_vars":
                    extends(value)
        elif isinstance(node, list | tuple):
            for value in node:
                extends(value)

    extends(algebra)
    return out


def _scan_from_algebra(algebra: Any) -> str | None:
    found: dict[str, list[Any]] = {"triples": [], "filters": [], "values": []}
    _walk(algebra, None, found)
    filtered: set[Variable] = set()
    for expr in found["filters"]:
        filtered |= _string_filter_vars(expr)
    if not filtered:
        return None
    anchored = _anchored(found["triples"], set(found["values"]))
    loose = filtered - anchored
    if not loose:
        return None

    for (s, p, o), _graph in found["triples"]:
        terms = (s, p, o)
        if all(isinstance(t, Variable) for t in terms) and set(terms) & loose:
            return ALL_VARIABLE_ADVICE.format(
                seconds=f"{SCAN_TIMEOUT:g}",
                triple=f"?{s} ?{p} ?{o}",
                vars=", ".join(f"?{v}" for v in sorted(set(terms) & loose)),
            )
    for (_s, p, o), graph in found["triples"]:
        if isinstance(graph, URIRef) and str(graph).endswith(_UBERGRAPH_SUFFIX):
            where = "ubergraph, the federation's largest graph,"
        elif isinstance(graph, Variable):
            where = f"every graph ?{graph} ranges over"
        else:
            continue
        if (
            not isinstance(p, Path)
            and str(p) in _LABEL_PREDICATES
            and isinstance(o, Variable)
            and o in loose
        ):
            return UBERGRAPH_LABEL_ADVICE.format(
                seconds=f"{SCAN_TIMEOUT:g}", vars=f"?{o}", where=where
            )
    return None


def scan_problem(query: str) -> str | None:
    """A rewrite message if ``query`` has a known full-scan shape, else None."""
    algebra = _algebra(query)
    return None if algebra is None else _scan_from_algebra(algebra)


@dataclass
class QueryCheck:
    """Everything the pre-flight check found in one query."""

    #: Shapes 1/2: run with the short limit; this is the rewrite if it hits it.
    scan: str | None = None
    #: Shape 3: don't send; this is the rewrite.
    blocked: str | None = None
    #: Shape 4: send, and pass these along with the result.
    warnings: list[str] = field(default_factory=list)


def check_query(query: str) -> QueryCheck:
    """Run every pre-flight check on ``query`` (parsed once)."""
    algebra = _algebra(query)
    if algebra is None:
        return QueryCheck()
    try:
        blocked = isolated_scan(algebra)
    except Exception:  # pragma: no cover - a lint bug must never block a query
        blocked = None
    try:
        warnings = scope_warnings(algebra)
    except Exception:  # pragma: no cover
        warnings = []
    return QueryCheck(
        scan=_scan_from_algebra(algebra), blocked=blocked, warnings=warnings
    )

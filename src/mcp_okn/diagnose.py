"""Say why a query returned no rows, by testing its parts on the endpoint.

An empty result tells an agent nothing about where the rows were lost, so it
spends its next turns finding out: in the benchmark, most zero-row queries were
followed by one to three probes (describe the IRI, count each side of the join,
sample a join variable). The usual answers are mechanical: one triple pattern
matches nothing in its graph (an IRI in the wrong namespace, a predicate the graph
doesn't use, a literal stored as ``"x"@en`` rather than ``"x"``); or every part
matches and the rows vanish where two GRAPH blocks join, because the two graphs
write the shared identifier differently.

:func:`diagnose_empty` runs those probes itself, briefly, and returns one line per
finding:

1. Each triple pattern with a constant subject or object (a VALUES-bound variable
   counts) is tested alone in its GRAPH with ``LIMIT 1``. A pattern that matches
   nothing is reported, and its constants are looked up: does the IRI occur in
   that graph at all, and as what; is the predicate used there; does the literal
   exist with a language tag or in another case (and, failing that, what its
   stored values look like). A UNION is tested branch by branch and blamed only
   when every branch matches nothing.
2. If those all match, each GRAPH block is tested whole. In a block that is empty,
   the patterns with only a constant predicate are tested next; if they match too,
   the variables the block's patterns share are named.
3. If every block matches, the variables two blocks share (or that a FILTER
   compares across blocks) are sampled from each side, which shows a namespace
   mismatch directly, and the blocks are joined without their FILTERs, which
   tells "the blocks share no value" from "a FILTER removes the rows".

Each probe is an indexed lookup with a short time limit, run one at a time (the
federation answers concurrent bursts with 429s, which would read as empties). A
probe that fails is left out rather than reported as empty. The whole diagnosis is
capped at :data:`MAX_PROBES` queries and :data:`TOTAL_SECONDS` seconds. Parts it
does not test (OPTIONAL, MINUS, NOT EXISTS, a UNION branch with no constant) are
never blamed, and the closing note names them.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from rdflib.term import Literal, URIRef, Variable

from .query_lint import _algebra, _exists_pattern, _expr_vars
from .sparql import run_sparql

MAX_PROBES = 12
PROBE_SECONDS = 6.0
TOTAL_SECONDS = 12.0

_XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"

Triple = tuple[Any, Any, Any]


@dataclass
class _Block:
    graph: str
    triples: list[Triple] = field(default_factory=list)


@dataclass
class _Shape:
    blocks: dict[str, _Block] = field(default_factory=dict)
    values: dict[Variable, list[Any]] = field(default_factory=dict)
    filter_vars: list[set[Variable]] = field(default_factory=list)
    #: Each required UNION, as its branches; a branch is a shape of its own.
    unions: list[list[_Shape]] = field(default_factory=list)
    #: True when a FILTER, MINUS or NOT EXISTS could remove rows.
    filters: bool = False
    #: Parts of the query the diagnosis leaves untested (OPTIONAL, …).
    untested: set[str] = field(default_factory=set)


def _branches(node: Any) -> list[Any]:
    """The branches of a UNION, nested unions flattened."""
    if getattr(node, "name", None) == "Union":
        return _branches(node.get("p1")) + _branches(node.get("p2"))
    return [node]


def _collect(node: Any, graph: str | None, shape: _Shape) -> None:
    """Gather the required parts: patterns every solution must match."""
    name = getattr(node, "name", None)
    if name is None:
        return
    if name == "Graph":
        term = node.get("term")
        if not isinstance(term, URIRef):
            shape.untested.add("GRAPH ?g")
        _collect(node.get("p"), str(term) if isinstance(term, URIRef) else None, shape)
        return
    if name == "BGP":
        if graph is not None:
            block = shape.blocks.setdefault(graph, _Block(graph))
            block.triples += list(node.get("triples") or [])
        elif node.get("triples"):
            shape.untested.add("patterns outside any GRAPH block")
        return
    if name == "values":
        for row in node.get("res") or []:
            for var, value in row.items():
                if isinstance(value, URIRef | Literal):
                    shape.values.setdefault(var, [])
                    if value not in shape.values[var]:
                        shape.values[var].append(value)
        return
    if name == "Filter":
        expr = node.get("expr")
        shape.filter_vars.append(_expr_vars(expr))
        # FILTER EXISTS { … } is a requirement like any pattern; test it too.
        if getattr(expr, "name", None) == "Builtin_EXISTS":
            pattern = _exists_pattern(expr)
            if pattern is not None:
                _collect(pattern, graph, shape)
        else:
            shape.filters = True
    if name == "Union":
        # A union is empty only if every branch is: each branch is tested on
        # its own, and the union blamed only when all of them match nothing.
        branches = []
        for branch in _branches(node):
            sub = _Shape()
            _collect(branch, graph, sub)
            shape.filters |= sub.filters
            branches.append(sub)
        shape.unions.append(branches)
        return
    if name in ("LeftJoin", "Minus"):
        shape.filters |= name == "Minus"
        _collect(node.get("p1"), graph, shape)
        return
    for key in ("p", "p1", "p2"):
        if key in node:
            _collect(node[key], graph, shape)


def _short(graph: str) -> str:
    return graph.rsplit("/kg/", 1)[-1]


def _n3(term: Any) -> str:
    return str(term.n3())


def _vars(triples: list[Triple]) -> set[Variable]:
    return {t for tr in triples for t in tr if isinstance(t, Variable)}


def _is_constant(term: Any) -> bool:
    return isinstance(term, URIRef | Literal)


class _Query:
    """Builds probe queries with the query's VALUES applied."""

    def __init__(self, values: dict[Variable, list[Any]]) -> None:
        self.values = values

    def term(self, term: Any) -> Any:
        if isinstance(term, Variable) and len(self.values.get(term, [])) == 1:
            return self.values[term][0]
        return term

    def pattern(self, triple: Triple) -> str:
        return " ".join(_n3(self.term(t)) for t in triple)

    def shown(self, triple: Triple) -> str:
        """A pattern as reported, naming any VALUES list it uses."""
        text = f"`{self.pattern(triple)}`"
        lists = [
            f"?{v} from its VALUES list ({len(self.values[v])})"
            for v in sorted(_vars([triple]))
            if len(self.values.get(v, [])) > 1
        ]
        return text + (f" with {', '.join(lists)}" if lists else "")

    def clause(self, triples: list[Triple]) -> str:
        return " ".join(
            f"VALUES ?{v} {{ {' '.join(x.n3() for x in self.values[v])} }}"
            for v in sorted(_vars(triples))
            if len(self.values.get(v, [])) > 1
        )

    def select(self, blocks: list[tuple[str, list[Triple]]], head: str = "*") -> str:
        triples = [t for _, ts in blocks for t in ts]
        body = " ".join(
            f"GRAPH <{g}> {{ {' . '.join(self.pattern(t) for t in ts)} }}"
            for g, ts in blocks
        )
        return f"SELECT {head} WHERE {{ {self.clause(triples)} {body} }}"

    def anchored(self, triple: Triple) -> bool:
        s, _p, o = triple
        return any(
            _is_constant(self.term(t)) or (isinstance(t, Variable) and t in self.values)
            for t in (s, o)
        )


class _Prober:
    def __init__(self) -> None:
        self.used = 0
        self.deadline = time.monotonic() + TOTAL_SECONDS

    async def rows(self, query: str) -> list[dict[str, Any]] | None:
        """Rows of a probe, or None when it could not be run."""
        if self.used >= MAX_PROBES or time.monotonic() >= self.deadline:
            return None
        self.used += 1
        limit = min(PROBE_SECONDS, max(1.0, self.deadline - time.monotonic()))
        try:
            result = await run_sparql(query, timeout=limit, max_retries=0)
        except Exception:
            return None
        return list(result.get("rows") or [])


def _literal_text(row: dict[str, Any]) -> str:
    text = Literal(str(row.get("text", ""))).n3()
    if row.get("lang"):
        return f"{text}@{row['lang']}"
    dt = row.get("dt")
    if dt and dt != _XSD_STRING:
        return f"{text}^^<{dt}>"
    return text


def _candidates(q: _Query, term: Any) -> list[Any]:
    """The constants a pattern position stands for: itself or its VALUES list."""
    if _is_constant(term):
        return [term]
    if isinstance(term, Variable):
        return list(q.values.get(term, []))
    return []


def _variants(text: str) -> list[str]:
    return sorted({text, text.lower(), text.capitalize(), text.title()})


async def _explain_iris(
    prober: _Prober, graph: str, iris: list[URIRef], done: set[Any]
) -> list[str]:
    kg = _short(graph)
    if len(iris) == 1:
        (term,) = iris
        rows = await prober.rows(
            f"SELECT ?p ?dir (COUNT(*) AS ?n) WHERE {{ GRAPH <{graph}> {{ "
            f'{{ <{term}> ?p ?x BIND("subject" AS ?dir) }} UNION '
            f'{{ ?x ?p <{term}> BIND("object" AS ?dir) }} }} }} GROUP BY ?p ?dir '
            "ORDER BY DESC(?n) LIMIT 5"
        )
        if rows is None:
            return []
        done.add(term)
        if not rows:
            return [
                f"<{term}> occurs nowhere in {kg}: that graph may write this id in "
                "another namespace or form (see get_join_strategy's "
                "iri_normalization, or probe_namespaces)."
            ]
        uses = ", ".join(
            f"{r.get('dir')} of <{r.get('p')}> ({r.get('n')})" for r in rows
        )
        return [f"<{term}> does occur in {kg}, as {uses}."]
    listed = " ".join(f"<{t}>" for t in iris[:20])
    rows = await prober.rows(
        f"SELECT DISTINCT ?t WHERE {{ VALUES ?t {{ {listed} }} GRAPH <{graph}> {{ "
        "{ ?t ?p ?x } UNION { ?x ?p ?t } } }"
    )
    if rows is None:
        return []
    done.update(iris)
    if not rows:
        return [
            f"None of the {len(iris)} IRIs in the VALUES list (e.g. <{iris[0]}>) "
            f"occurs anywhere in {kg}: that graph may write these ids in another "
            "namespace or form (see get_join_strategy's iri_normalization, or "
            "probe_namespaces)."
        ]
    present = ", ".join(f"<{r.get('t')}>" for r in rows[:3])
    return [
        f"{len(rows)} of the {len(iris)} IRIs in the VALUES list occur in {kg} "
        f"(e.g. {present}), but not in this position."
    ]


async def _explain(
    prober: _Prober,
    q: _Query,
    graph: str,
    triple: Triple,
    done: set[Any] | None = None,
) -> list[str]:
    """Look up the constants of a pattern that matched nothing."""
    done = set() if done is None else done
    notes: list[str] = []
    kg = _short(graph)
    s, p, o = (q.term(t) for t in triple)
    for term in (s, o):
        iris = [t for t in _candidates(q, term) if isinstance(t, URIRef)]
        iris = [t for t in iris if t not in done]
        if iris:
            notes += await _explain_iris(prober, graph, iris, done)
    if not isinstance(p, URIRef) or p in done:
        return notes
    done.add(p)
    rows = await prober.rows(
        f"SELECT ?s WHERE {{ GRAPH <{graph}> {{ ?s <{p}> ?o }} }} LIMIT 1"
    )
    if rows == []:
        notes.append(f"<{p}> is not used in {kg} at all.")
        return notes
    literals = [t for t in _candidates(q, o) if isinstance(t, Literal)][:10]
    if not rows or not literals:
        return notes
    forms = " ".join(
        f"{Literal(v).n3()} {Literal(v, lang='en').n3()}"
        for lit in literals
        for v in _variants(str(lit))
    )
    found = await prober.rows(
        "SELECT DISTINCT (STR(?o) AS ?text) (LANG(?o) AS ?lang) "
        f"(STR(DATATYPE(?o)) AS ?dt) WHERE {{ VALUES ?o {{ {forms} }} "
        f"GRAPH <{graph}> {{ ?s <{p}> ?o }} }} LIMIT 3"
    )
    asked = literals[0].n3() if len(literals) == 1 else "the listed values"
    if found:
        shown = ", ".join(_literal_text(r) for r in found)
        notes.append(
            f"{asked} is not stored as an object of <{p}>, but {shown} is "
            "(the language tag or the case differs)."
        )
    elif found == []:
        sample = await prober.rows(
            "SELECT (STR(?o) AS ?text) (LANG(?o) AS ?lang) "
            f"(STR(DATATYPE(?o)) AS ?dt) WHERE {{ GRAPH <{graph}> {{ ?s <{p}> ?o }} "
            "FILTER(ISLITERAL(?o)) } LIMIT 3"
        )
        like = (
            f" Its objects look like: {', '.join(_literal_text(r) for r in sample)}."
            if sample
            else ""
        )
        notes.append(
            f"No object of <{p}> in {kg} equals {asked} in any common case or "
            f"language-tag form.{like}"
        )
    return notes


def _shared_within(triples: list[Triple]) -> list[Variable]:
    seen: dict[Variable, int] = {}
    for triple in triples:
        for v in {t for t in triple if isinstance(t, Variable)}:
            seen[v] = seen.get(v, 0) + 1
    return sorted(v for v, n in seen.items() if n > 1)


def _ties(shape: _Shape) -> list[list[tuple[Variable, str]]]:
    """What ties the blocks together, as (variable, block) pairs to sample.

    That is each variable two blocks share, and each FILTER that compares
    variables from different blocks.
    """
    where: dict[Variable, list[str]] = {}
    for graph, block in shape.blocks.items():
        for v in _vars(block.triples):
            where.setdefault(v, []).append(graph)
    groups = [
        [(v, g) for g in gs]
        for v, gs in where.items()
        if len(gs) > 1 and v not in shape.values
    ]
    for used in shape.filter_vars:
        pairs = [(v, where[v][0]) for v in sorted(used) if len(where.get(v, [])) == 1]
        if len({g for _, g in pairs}) > 1:
            groups.append(pairs)
    return groups


def _connected(shape: _Shape) -> bool:
    """True when shared variables link every GRAPH block to the others.

    A VALUES variable counts: two blocks that both use it meet on its values.
    """
    graphs = list(shape.blocks)
    seen = {graphs[0]}
    frontier = [graphs[0]]
    while frontier:
        here = _vars(shape.blocks[frontier.pop()].triples)
        for g in graphs:
            if g not in seen and here & _vars(shape.blocks[g].triples):
                seen.add(g)
                frontier.append(g)
    return len(seen) == len(graphs)


def _caveat(shape: _Shape) -> str:
    if not shape.untested:
        return ""
    return f" (Not tested: {', '.join(sorted(shape.untested))}.)"


def _union_vars(shape: _Shape) -> set[Variable]:
    return {
        v
        for branches in shape.unions
        for branch in branches
        for block in branch.blocks.values()
        for v in _vars(block.triples)
    }


async def _probe_patterns(
    prober: _Prober, q: _Query, shape: _Shape
) -> list[tuple[str, Triple]] | None:
    """The anchored patterns of ``shape`` that match nothing (None: a probe failed)."""
    empty: list[tuple[str, Triple]] = []
    for graph, block in shape.blocks.items():
        for triple in block.triples:
            if not q.anchored(triple):
                continue
            rows = await prober.rows(q.select([(graph, [triple])]) + " LIMIT 1")
            if rows is None:
                return None
            if not rows:
                empty.append((graph, triple))
    return empty


async def _dead_union(
    prober: _Prober, values: dict[Variable, list[Any]], branches: list[_Shape]
) -> tuple[list[tuple[str, Triple, _Query]], bool]:
    """One empty pattern per branch when every branch of a UNION is empty.

    The flag says whether the union was tested: False when a branch has no
    constant to probe, or a probe failed.
    """
    misses = []
    for branch in branches:
        q = _Query({**values, **branch.values})
        if not any(q.anchored(t) for b in branch.blocks.values() for t in b.triples):
            return [], False
        empty = await _probe_patterns(prober, q, branch)
        if empty is None:
            return [], False
        if not empty:
            return [], True  # this branch matches
        misses.append((*empty[0], q))
    return misses, True


async def _sample(
    prober: _Prober, q: _Query, blocks: dict[str, _Block], var: Variable
) -> str | None:
    """A few values of ``var`` from the blocks that bind it, as text."""
    parts = [(g, b.triples) for g, b in blocks.items() if var in _vars(b.triples)]
    if not parts:
        return None
    rows = await prober.rows(q.select(parts, f"DISTINCT ?{var}") + " LIMIT 2")
    if not rows:
        return None
    return ", ".join(str(r.get(str(var))) for r in rows)


async def _sample_union_join(
    prober: _Prober, q: _Query, shape: _Shape, var: Variable
) -> list[str]:
    """Values of ``var`` from a UNION branch and from the rest, side by side."""
    rest = await _sample(prober, q, shape.blocks, var)
    for branches in shape.unions:
        for branch in branches:
            inside = await _sample(
                prober, _Query({**q.values, **branch.values}), branch.blocks, var
            )
            if inside and rest:
                return [f"?{var} from the UNION: {inside}; from the rest: {rest}."]
            if inside is not None:
                return []
    return []


async def diagnose_empty(query: str) -> list[str]:
    """Findings that locate where a zero-row query lost its rows (may be empty)."""
    algebra = _algebra(query)
    if algebra is None:
        return []
    shape = _Shape()
    _collect(algebra, None, shape)
    if not shape.blocks and not shape.unions:
        return []
    prober = _Prober()
    q = _Query(shape.values)

    # 1. Each pattern with a constant subject or object, alone in its graph; then
    #    each UNION, which is empty only when every branch is.
    empty = await _probe_patterns(prober, q, shape)
    if empty is None:
        return []
    if empty:
        notes: list[str] = []
        done: set[Any] = set()
        for graph, triple in empty[:2]:
            notes.append(f"No match in {_short(graph)} for {q.shown(triple)}.")
            notes += await _explain(prober, q, graph, triple, done)
        return notes
    for branches in shape.unions:
        misses, tested = await _dead_union(prober, shape.values, branches)
        if not tested:
            shape.untested.add("UNION")
        if not misses:
            continue
        shown = " / ".join(bq.shown(t) for _, t, bq in misses)
        graphs = sorted({_short(g) for g, _, _ in misses})
        notes = [f"No branch of the UNION matches in {', '.join(graphs)}: {shown}."]
        done = set()
        for graph, triple, bq in misses:
            notes += await _explain(prober, bq, graph, triple, done)
        return notes
    if not shape.blocks:
        return []

    # 2. Each GRAPH block whole; in an empty one, its predicate-only patterns.
    for graph, block in shape.blocks.items():
        if len(block.triples) < 2:
            continue
        rows = await prober.rows(q.select([(graph, block.triples)]) + " LIMIT 1")
        if rows is None:
            return []
        if rows:
            continue
        for triple in block.triples:
            if q.anchored(triple):
                continue
            alone = await prober.rows(q.select([(graph, [triple])]) + " LIMIT 1")
            if alone == []:
                return [
                    f"No match in {_short(graph)} for {q.shown(triple)}.",
                    *await _explain(prober, q, graph, triple),
                ]
        shared = ", ".join(f"?{v}" for v in _shared_within(block.triples))
        return [
            f"In {_short(graph)} each pattern matches on its own, but not all "
            f"together: check how they connect through {shared} (a wrong "
            "direction, or a predicate that links other node types)."
        ]

    # 3. What ties the blocks together.
    notes = []
    ties = _ties(shape)
    for group in ties[:2]:
        samples = []
        for var, graph in group:
            rows = await prober.rows(
                q.select([(graph, shape.blocks[graph].triples)], f"DISTINCT ?{var}")
                + " LIMIT 2"
            )
            if rows:
                shown = ", ".join(str(r.get(str(var))) for r in rows)
                samples.append(f"?{var} in {_short(graph)}: {shown}")
        if len(samples) >= 2:
            notes.append("Where the GRAPH blocks meet, " + "; ".join(samples) + ".")
    if len(shape.blocks) > 1 and not _connected(shape):
        if any(len(g) > 1 and g[0][0] != g[1][0] for g in ties):
            notes.append(
                "The GRAPH blocks share no variable, so only a FILTER relates them. "
                "Put that FILTER outside and after the GRAPH blocks, and check it "
                "compares like with like (the values above); or give both blocks "
                "one shared variable, e.g. BIND(IRI(CONCAT('<namespace>', ?id)) AS "
                "?x) on one side." + _caveat(shape)
            )
        else:
            kgs = ", ".join(_short(g) for g in shape.blocks)
            notes.append(
                f"No variable of the triple patterns is shared by the GRAPH blocks "
                f"({kgs}). If a BIND or subquery variable is meant to link them, "
                "check that it is bound where it is used: a BIND sees only its own "
                "group." + _caveat(shape)
            )
        return notes
    joined = None
    if len(shape.blocks) > 1:
        joined = await prober.rows(
            q.select([(g, b.triples) for g, b in shape.blocks.items()]) + " LIMIT 1"
        )
    if joined == []:
        notes.append(
            "Every GRAPH block matches on its own, but they share no value: compare "
            "the forms above and rewrite one side, e.g. BIND(IRI(REPLACE(STR(?x), "
            "'^old', 'new')) AS ?y), comparing outside the GRAPH blocks."
            + _caveat(shape)
        )
        return notes
    if joined is None and len(shape.blocks) > 1:
        return notes
    where = "the GRAPH blocks join" if joined else "every pattern matches"
    if shape.filters:
        notes.append(
            f"Without the FILTERs {where}, so a FILTER (or NOT EXISTS / MINUS / "
            "HAVING) removes the rows: check its value forms and that it sits where "
            "its variables are bound." + _caveat(shape)
        )
    elif shape.unions and "UNION" not in shape.untested:
        linked = sorted(
            _union_vars(shape)
            & {v for b in shape.blocks.values() for v in _vars(b.triples)}
        )
        via = ", ".join(f"?{v}" for v in linked) or "no shared variable"
        notes.append(
            f"Outside the UNION {where}, and every UNION has a branch that matches, "
            f"so the rows are lost where the UNION meets the rest ({via}): check "
            "that the branches bind those variables to the same kind of node."
        )
        if linked:
            notes += await _sample_union_join(prober, q, shape, linked[0])
    elif shape.untested:
        notes.append(
            f"Every part tested matches ({where}), so the rows are lost in a part "
            "not tested." + _caveat(shape)
        )
    return notes

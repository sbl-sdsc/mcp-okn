"""Exact rewrites of group shapes that QLever plans badly.

The federation is one QLever index over every graph. A pattern that is not tied
to a constant is a scan of its whole relation in every graph, filtered to the
named one afterwards, and QLever evaluates some groups on their own before
joining them to the rest of the query. Once such a scan is cached it costs
milliseconds, but the cache is shared with every other user of the endpoint, and
in the v0.6.3 benchmark it was evicted between attempts: the same agent query
took 0.7 s in one attempt and 8.8 s in the next. Four shapes from those runs are
rewritten here, each only where the result is provably the same: the two below,
:func:`delay_comparison_filters` and :func:`filter_equality_to_join` (each
documented on its function).

**FILTER NOT EXISTS → MINUS** (:func:`not_exists_to_minus`). QLever's planning
time for a ``FILTER NOT EXISTS`` grows with the size of the group around it: in a
ten-triple group (spoke-genelab differential expression) one such filter kept
the planner busy past the 60 s limit, and the endpoint went on planning after
the client gave up, slowing the agent's next query too. As ``MINUS`` the same
query planned in 0.4 s and ran in 1.2 s; a prokn GO count with two negation
filters went from 4.9 s (4.7 s of it planning, on a warm cache) to 0.5 s.

``FILTER NOT EXISTS { P }`` keeps a row μ of its group when P, with μ's values
substituted, has no solution; ``MINUS { P }`` keeps μ when no solution of P
(evaluated alone) is compatible with μ and shares a variable with it. The two
agree when:

* P holds only triple patterns, FILTERs and MINUS groups (no OPTIONAL, UNION,
  BIND, VALUES, GRAPH, subquery, property path or blank node), so substituting a
  value for a variable is the same as joining on it;
* every variable used anywhere in P is bound by P's own triples, so a FILTER in P
  never reads a value only the outer row could supply;
* at least one of P's variables also occurs in the rest of the query, and every
  such variable is certainly bound in the group holding the FILTER (by one of
  its triples, a GRAPH or plain group it joins, or a VALUES block without
  UNDEF), so the "shares a variable" condition of MINUS always holds.

The FILTER applies to its whole group wherever it is written, so the MINUS goes
at the end of the group. A nested ``FILTER NOT EXISTS`` inside P is rewritten
first.

**The anchor, repeated inside an OPTIONAL** (:func:`anchor_optionals`). QLever
computes an OPTIONAL's right side on its own. ``?y skos:exactMatch <uniprot/P>
OPTIONAL { ?ke ?p ?y }`` therefore scans every triple in the store (16 s cold
for biobricks-aopwiki's 184 thousand) before keeping the few that meet ``?y``,
and ``OPTIONAL { ?y a ?t }`` reads every rdf:type triple in the federation (4 s).
Copying the triple that pins ``?y`` into the OPTIONAL turns each into an index
lookup: 24.4 s → 4.9 s for that probe, cold.

``A OPTIONAL { B }`` equals ``A OPTIONAL { A' B }`` when A' is a set of triple
patterns from A's own top level written before the OPTIONAL: every solution μ of
A binds all of A''s variables and satisfies A', so exactly one solution of A' is
compatible with μ, and the solutions of ``A' B`` compatible with μ are those of
B, one for one. In standard SPARQL a FILTER inside the OPTIONAL sees the merged
row too; QLever, however, scopes it to the OPTIONAL's own group, so where such a
FILTER or BIND reads a variable only A binds, the rewrite would change QLever's
answer and is skipped. The rewrite copies, for each variable B shares with A, the
shortest chain of A's triples that links it to an identifying constant (see
:func:`_anchor_kind`; an ``rdf:type`` class counts only when B reads a whole
relation, as ``?s ?p ?o`` or ``?s a ?t`` do), and only when B's own triples have no
such constant: those are index lookups already. A triple with a variable
predicate is never copied: inside the OPTIONAL it is a scan of its own.

Replayed live on 2026-11-09 against the 570 logged benchmark queries that these
rewrites and single-value VALUES inlining change, the order of the two forms
alternating: 2,469 s to 1,441 s where both forms finished, and 9 queries that
had failed returned rows. The guards on FILTER scope and on variable predicates
came from that replay. :func:`filter_equality_to_join` changes 5 of the 4,300
distinct logged queries, all 58-60 s timeouts; each now takes 0.6-1.8 s.
"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass

from .query_rewrite import _enclosing_brace, _mask, _matching_brace, _matching_paren

_VAR = re.compile(r"[?$](\w+)")
_KEYWORD = re.compile(
    r"(FILTER|BIND|VALUES|OPTIONAL|MINUS|GRAPH|SERVICE|UNION)\b", re.I
)
_NOT_EXISTS = re.compile(r"NOT\s+EXISTS\s*\{", re.I)
_EXISTS = re.compile(r"EXISTS\s*\{", re.I)
_CALL = re.compile(r"(?:[A-Za-z_][\w\-.]*)?:?[A-Za-z_][\w\-.]*\s*\(")
_FILTER_NOT_EXISTS = re.compile(r"\bFILTER\s+NOT\s+EXISTS\s*\{", re.I)
_OPTIONAL = re.compile(r"\bOPTIONAL\s*\{", re.I)
_NEGATION_GROUP = re.compile(r"\b(?:NOT\s+EXISTS|EXISTS|MINUS)\s*\{", re.I)

_RDF_TYPE = frozenset(
    {"a", "rdf:type", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"}
)

#: Triples copied into one OPTIONAL at most; a longer chain is left alone.
MAX_ANCHOR_TRIPLES = 4

#: Predicates whose object names a kind of thing, not one thing.
_CATEGORY_PREDICATES = frozenset(
    {
        "type",
        "predicate",
        "category",
        "additionaltype",
        "inscheme",
        "hasobonamespace",
        "taxonomy",
        "taxon",
        "in_taxon",
        "intaxon",
        "organism",
        "species",
        "unit",
        "datatype",
        "scoretype",
        "status",
    }
)

#: Predicates whose literal object identifies one thing.
_NAME_PREDICATES = frozenset(
    {
        "label",
        "preflabel",
        "altlabel",
        "name",
        "title",
        "id",
        "identifier",
        "symbol",
        "accession",
        "notation",
        "hasexactsynonym",
    }
)

_LANG_OR_TYPE = r"(?:@[A-Za-z]+(?:-[A-Za-z0-9]+)*|\^\^(?:<[^<>\"{}|^`\\\x00-\x20]*>|(?:[A-Za-z][\w\-.]*)?:[\w\-.%]*))?"
_TOKEN = re.compile(
    r"(?P<ws>\s+)"
    r"|(?P<comment>#[^\n]*)"
    r"|(?P<iri><[^<>\"{}|^`\\\x00-\x20]*>)"
    r'|(?P<lit>(?:"""(?:[^"\\]|\\.|"(?!""))*"""'
    r"|'''(?:[^'\\]|\\.|'(?!''))*'''"
    r'|"(?:[^"\\\n]|\\.)*"'
    r"|'(?:[^'\\\n]|\\.)*')" + _LANG_OR_TYPE + ")"
    r"|(?P<var>[?$]\w+)"
    r"|(?P<num>[+-]?(?:\d+\.\d+|\.\d+|\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<pname>(?:[A-Za-z][\w\-.]*)?:(?:[\w\-%:]|\.(?=[\w\-%:]))*)"
    r"|(?P<a>a\b)"
    r"|(?P<bool>(?:true|false)\b)"
    r"|(?P<punct>[.;,])"
)
_TERM = frozenset({"iri", "lit", "var", "num", "pname", "bool"})

Triple = tuple[str, str, str]


@dataclass
class _Item:
    """One element of a group: a run of triples, a FILTER, a sub-group."""

    kind: str
    start: int
    end: int
    open: int | None = None
    close: int | None = None


def _is_var(term: str) -> bool:
    return term[:1] in "?$"


def _var(term: str) -> str:
    return term[1:]


def _items(mask: str, lo: int, hi: int) -> list[_Item] | None:
    """The elements of the group body ``mask[lo:hi]``, or None if unrecognized."""
    items: list[_Item] = []
    i = lo
    tstart: int | None = None

    def flush(upto: int) -> None:
        nonlocal tstart
        if tstart is not None and mask[tstart:upto].strip(" \t\r\n."):
            items.append(_Item("triples", tstart, upto))
        tstart = None

    def group_at(j: int) -> tuple[int, int] | None:
        while j < hi and mask[j].isspace():
            j += 1
        if j >= hi or mask[j] != "{":
            return None
        close = _matching_brace(mask, j)
        if close is None or close >= hi:
            return None
        return j, close

    while i < hi:
        c = mask[i]
        if c.isspace():
            i += 1
            continue
        if c == "{":
            flush(i)
            span = group_at(i)
            if span is None:
                return None
            kind = (
                "subquery"
                if re.match(r"\s*SELECT\b", mask[i + 1 : span[1]], re.I)
                else "group"
            )
            items.append(_Item(kind, i, span[1] + 1, *span))
            i = span[1] + 1
            continue
        if c == "}":
            return None
        boundary = i == lo or not (mask[i - 1].isalnum() or mask[i - 1] in "_?$:")
        m = _KEYWORD.match(mask, i) if boundary else None
        if m is None:
            if tstart is None:
                tstart = i
            i += 1
            continue
        flush(i)
        kw = m.group(1).upper()
        j = m.end()
        while j < hi and mask[j].isspace():
            j += 1
        if kw == "UNION":
            items.append(_Item("union", i, m.end()))
            i = m.end()
            continue
        if kw == "FILTER":
            neg = _NOT_EXISTS.match(mask, j)
            pos = None if neg else _EXISTS.match(mask, j)
            if neg or pos:
                found = neg or pos
                assert found is not None
                span = group_at(found.end() - 1)
                if span is None:
                    return None
                kind = "not_exists" if neg else "exists"
                items.append(_Item(kind, i, span[1] + 1, *span))
                i = span[1] + 1
                continue
            call = _CALL.match(mask, j)
            paren = j if mask[j : j + 1] == "(" else (call.end() - 1 if call else None)
            if paren is None:
                return None
            close = _matching_paren(mask, paren)
            if close is None or close >= hi:
                return None
            items.append(_Item("filter", i, close + 1))
            i = close + 1
            continue
        if kw == "BIND":
            if mask[j : j + 1] != "(":
                return None
            close = _matching_paren(mask, j)
            if close is None or close >= hi:
                return None
            items.append(_Item("bind", i, close + 1))
            i = close + 1
            continue
        # VALUES, OPTIONAL, MINUS, GRAPH, SERVICE: whatever precedes a { … }
        brace = mask.find("{", j, hi)
        if brace < 0:
            return None
        span = group_at(brace)
        if span is None:
            return None
        items.append(_Item(kw.lower(), i, span[1] + 1, *span))
        i = span[1] + 1
    flush(hi)
    return items


def _triples(text: str, lo: int, hi: int) -> list[Triple] | None:
    """The triple patterns written in ``text[lo:hi]``, or None if not plain triples.

    Plain means IRIs, prefixed names, literals and variables in ``s p o`` form
    with ``;`` and ``,`` -- no property paths, collections or blank nodes.
    """
    toks: list[tuple[str, str]] = []
    pos = lo
    while pos < hi:
        m = _TOKEN.match(text, pos)
        if m is None or m.end() > hi or m.end() == pos:
            return None
        pos = m.end()
        kind = m.lastgroup or ""
        if kind in ("ws", "comment"):
            continue
        toks.append((kind, m.group(0)))
    out: list[Triple] = []
    i, n = 0, len(toks)
    while i < n:
        if toks[i] == ("punct", "."):
            i += 1
            continue
        if toks[i][0] not in ("iri", "var", "pname"):
            return None
        subject = toks[i][1]
        i += 1
        while True:
            if i >= n or toks[i][0] not in ("iri", "var", "pname", "a"):
                return None
            predicate = toks[i][1]
            i += 1
            while True:
                if i >= n or toks[i][0] not in _TERM:
                    return None
                out.append((subject, predicate, toks[i][1]))
                i += 1
                if i < n and toks[i] == ("punct", ","):
                    i += 1
                    continue
                break
            if i < n and toks[i] == ("punct", ";"):
                while i < n and toks[i] == ("punct", ";"):
                    i += 1
                if i >= n or toks[i] == ("punct", "."):
                    break
                continue
            break
        if i < n and toks[i] != ("punct", "."):
            return None
    return out


def _vars_of(triples: list[Triple]) -> set[str]:
    return {_var(t) for triple in triples for t in triple if _is_var(t)}


def _certain_vars(mask: str, lo: int, hi: int) -> set[str]:
    """Variables bound in every solution of the group body ``mask[lo:hi]``."""
    items = _items(mask, lo, hi)
    if items is None:
        return set()
    out: set[str] = set()
    for k, it in enumerate(items):
        union_side = (k > 0 and items[k - 1].kind == "union") or (
            k + 1 < len(items) and items[k + 1].kind == "union"
        )
        if it.kind == "triples":
            # Every variable of a triple or path pattern is bound in its solutions.
            out |= set(_VAR.findall(mask[it.start : it.end]))
        elif it.kind == "group" and not union_side:
            assert it.open is not None and it.close is not None
            out |= _certain_vars(mask, it.open + 1, it.close)
        elif it.kind == "graph":
            assert it.open is not None and it.close is not None
            out |= _certain_vars(mask, it.open + 1, it.close)
            out |= set(_VAR.findall(mask[it.start : it.open]))
        elif it.kind == "values":
            assert it.open is not None and it.close is not None
            if not re.search(r"\bUNDEF\b", mask[it.open : it.close], re.I):
                out |= set(_VAR.findall(mask[it.start : it.open]))
    return out


def _blank(mask: str, spans: list[tuple[int, int]]) -> str:
    chars = list(mask)
    for lo, hi in spans:
        for k in range(lo, hi):
            if chars[k] != "\n":
                chars[k] = " "
    return "".join(chars)


def _drop_span(query: str, mask: str, lo: int, hi: int) -> str:
    """``query`` without ``[lo, hi)``, keeping the triples around it well formed."""
    after = hi
    while after < len(mask) and mask[after].isspace():
        after += 1
    before = lo - 1
    while before >= 0 and mask[before].isspace():
        before -= 1
    if (
        after < len(mask)
        and mask[after] == "."
        and (before < 0 or mask[before] in ".{}")
    ):
        hi = after + 1
    return query[:lo] + query[hi:]


def _minus_one(query: str, mask: str, m: re.Match[str]) -> str | None:
    """``query`` with the ``FILTER NOT EXISTS`` at ``m`` as a MINUS, or None."""
    p_open = m.end() - 1
    p_close = _matching_brace(mask, p_open)
    g_open = _enclosing_brace(mask, m.start())
    if p_close is None or g_open is None:
        return None
    g_close = _matching_brace(mask, g_open)
    if g_close is None or g_close < p_close:
        return None

    items = _items(mask, p_open + 1, p_close)
    if items is None or any(
        it.kind not in ("triples", "filter", "minus") for it in items
    ):
        return None
    own: list[Triple] = []
    for it in items:
        if it.kind == "triples":
            triples = _triples(query, it.start, it.end)
            if triples is None:
                return None
            own += triples
    own_vars = _vars_of(own)
    if not own_vars or not set(_VAR.findall(mask[p_open : p_close + 1])) <= own_vars:
        return None

    # Where else the query names P's variables: not in P, nor in another negation
    # (those bind nothing outside themselves).
    spans = [(m.start(), p_close + 1)]
    for neg in _NEGATION_GROUP.finditer(mask):
        close = _matching_brace(mask, neg.end() - 1)
        encloses = neg.start() < m.start() and close is not None and close > p_close
        if close is not None and not encloses:
            spans.append((neg.start(), close + 1))
    elsewhere = set(_VAR.findall(_blank(mask, spans)))
    shared = own_vars & elsewhere
    if not shared or not shared <= _certain_vars(mask, g_open + 1, g_close):
        return None

    body = query[p_open : p_close + 1]
    tail = _drop_span(query, mask, m.start(), p_close + 1)
    shift = len(query) - len(tail)
    at = g_close - shift
    return tail[:at].rstrip() + f"\n  MINUS {body}\n" + tail[at:]


def not_exists_to_minus(query: str) -> str:
    """Write each ``FILTER NOT EXISTS { P }`` that allows it as ``MINUS { P }``.

    See the module docstring for when the two are the same. Innermost first, so a
    negation nested in another is rewritten before the one around it.
    """
    for _ in range(64):
        mask = _mask(query)
        for m in reversed(list(_FILTER_NOT_EXISTS.finditer(mask))):
            out = _minus_one(query, mask, m)
            if out is not None:
                query = out
                break
        else:
            return query
    return query


def _local_name(term: str) -> str:
    """The part of an IRI or prefixed name after its last ``#``, ``/`` or ``:``."""
    return re.split(r"[#/:]", term.strip("<>"))[-1].lower()


def _is_type(predicate: str) -> bool:
    return predicate in _RDF_TYPE


def _anchor_kind(t: Triple) -> str | None:
    """How a triple pins its variables: ``entity``, ``class`` or not at all (None).

    A constant subject, an IRI object (``skos:exactMatch <uniprot/P00533>``) and
    an identifier-like literal (a label, name, title or symbol) pick out a few
    rows: an index lookup. A class (``a <Class>``), a category (``rdf:predicate
    <p>``, ``biolink:category …``) or any other literal (``"Space Flight"``) may
    pick out millions.
    """
    s, p, o = t
    if not _is_var(s):
        return "entity"
    if _is_var(o):
        return None
    if _is_var(p):
        return "entity"
    if _is_type(p) or _local_name(p) in _CATEGORY_PREDICATES:
        return "class"
    if o[:1] in "<" or re.match(r"(?:[A-Za-z][\w\-.]*)?:", o):
        return "entity"
    if _local_name(p) in _NAME_PREDICATES:
        return "entity"
    return "class"


def _is_broad(t: Triple) -> bool:
    """A pattern that reads a relation shared by every graph, or all of them."""
    _s, p, o = t
    return _is_var(p) or (_is_type(p) and _is_var(o))


def _anchor_chain(left: list[Triple], start: str, allow_class: bool) -> list[Triple]:
    """The shortest chain of ``left`` triples tying ?start to an anchor."""
    prev: dict[str, tuple[str, Triple] | None] = {start: None}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for t in left:
            ends = {_var(x) for x in (t[0], t[2]) if _is_var(x)}
            if v not in ends:
                continue
            kind = _anchor_kind(t)
            if kind == "entity" or (kind == "class" and allow_class):
                chain = [t]
                at = v
                while prev[at] is not None:
                    step = prev[at]
                    assert step is not None
                    at, link = step
                    chain.append(link)
                return chain
            for w in ends - {v}:
                if w not in prev:
                    prev[w] = (v, t)
                    queue.append(w)
    return []


def _is_iri(term: str) -> bool:
    return term.startswith("<") or bool(re.match(r"(?:[A-Za-z][\w\-.]*)?:", term))


def _bind_targets(mask: str, item: _Item) -> set[str]:
    """The variable a BIND item assigns (empty for a FILTER)."""
    m = re.search(r"\bAS\s+[?$](\w+)\s*\)\s*$", mask[item.start : item.end], re.I)
    return {m.group(1)} if item.kind == "bind" and m else set()


def _anchor_one(query: str, mask: str, m: re.Match[str]) -> str | None:
    """``query`` with an anchor copied into the OPTIONAL at ``m``, or None."""
    o_open = m.end() - 1
    o_close = _matching_brace(mask, o_open)
    g_open = _enclosing_brace(mask, m.start())
    if o_close is None or g_open is None:
        return None
    g_close = _matching_brace(mask, g_open)
    if g_close is None:
        return None
    g_items = _items(mask, g_open + 1, g_close)
    o_items = _items(mask, o_open + 1, o_close)
    if g_items is None or o_items is None:
        return None

    left: list[Triple] = []
    for it in g_items:
        if it.start >= m.start():
            break
        if it.kind == "triples":
            # A block with a path or a blank node is not copied (but is still
            # part of the left side, so nothing else changes).
            left += _triples(query, it.start, it.end) or []
    own: list[Triple] = []
    for it in o_items:
        if it.kind == "triples":
            triples = _triples(query, it.start, it.end)
            if triples is None:
                return None
            own += triples
    if not own or any(_anchor_kind(t) == "entity" for t in own):
        return None
    # QLever lets a FILTER or BIND see only its own group, so one inside the
    # OPTIONAL that reads a variable bound only outside it sees that variable
    # unbound. Copying the anchor in would bind it there and change the rows.
    for it in o_items:
        if it.kind in ("filter", "bind") and not set(
            _VAR.findall(mask[it.start : it.end])
        ) <= _vars_of(own) | _bind_targets(mask, it):
            return None
    # A variable predicate is copied only next to a constant IRI subject or
    # object (an index lookup); otherwise it is a scan of its own.
    left = [t for t in left if not _is_var(t[1]) or _is_iri(t[0]) or _is_iri(t[2])]
    shared = _vars_of(own) & _vars_of(left)
    if not shared:
        return None
    allow_class = any(_is_broad(t) for t in own)

    chains = [c for v in sorted(shared) if (c := _anchor_chain(left, v, allow_class))]
    if not chains:
        return None
    copied: list[Triple] = []
    for chain in sorted(chains, key=len):
        extra = [t for t in chain if t not in copied and t not in own]
        if len(copied) + len(extra) > MAX_ANCHOR_TRIPLES:
            continue
        copied += extra
    if not copied:
        return None
    anchor = " ".join(f"{s} {p} {o} ." for s, p, o in copied)
    return query[: o_open + 1] + " " + anchor + query[o_open + 1 :]


def anchor_optionals(query: str) -> str:
    """Repeat the outer anchor inside each OPTIONAL that allows it.

    See the module docstring. Outermost first, so a nested OPTIONAL can be
    anchored by what was copied into the one around it.
    """
    k = 0
    while True:
        mask = _mask(query)
        heads = list(_OPTIONAL.finditer(mask))
        if k >= len(heads):
            return query
        out = _anchor_one(query, mask, heads[k])
        if out is not None:
            query = out
        k += 1


_FILTER_PAREN = re.compile(r"\bFILTER\s*\(", re.I)
_COMPARISON = re.compile(r"[<>]=?|!=|=|\bIN\b", re.I)


def _delay_one(query: str, mask: str, m: re.Match[str]) -> str | None:
    """``query`` with the FILTER at ``m`` tied to a variable of the anchored side."""
    paren = m.end() - 1
    close = _matching_paren(mask, paren)
    g_open = _enclosing_brace(mask, m.start())
    if close is None or g_open is None:
        return None
    g_close = _matching_brace(mask, g_open)
    if g_close is None:
        return None
    expr = mask[paren + 1 : close]
    if (
        not _COMPARISON.search(expr)
        or re.search(r"\b(?:BOUND|EXISTS)\b", expr, re.I)
        or "{" in expr
    ):
        return None
    filtered = set(_VAR.findall(expr))
    if not filtered:
        return None
    items = _items(mask, g_open + 1, g_close)
    if items is None:
        return None
    triples: list[Triple] = []
    for it in items:
        if it.kind == "triples":
            parsed = _triples(query, it.start, it.end)
            if parsed is None:
                return None
            triples += parsed
    if not filtered <= _vars_of(triples):
        return None
    binding = [t for t in triples if filtered & _vars_of([t])]
    if any(_anchor_kind(t) == "entity" for t in binding):
        return None  # the filtered triple is an index lookup already
    bound_there = _vars_of(binding)
    anchors = [t for t in triples if t not in binding and _anchor_kind(t) == "entity"]
    # The variable nearest an anchor that the filtered triples do not bind. A
    # join key the query computes outside the group (``BIND(IRI(…) AS ?gene)``
    # from another graph's rows) is a small side too.
    seen = {v for t in anchors for v in _vars_of([t])}
    outside = mask[:g_open] + mask[g_close:]
    seen |= {
        v
        for v in re.findall(r"\bAS\s+[?$](\w+)", outside, re.I)
        if v in _vars_of(triples) and v not in bound_there
    }
    queue = deque(sorted(seen))
    while queue:
        v = queue.popleft()
        if v not in bound_there:
            text = query[paren + 1 : close]
            return query[: paren + 1] + f"({text}) && BOUND(?{v})" + query[close:]
        for t in triples:
            if v in _vars_of([t]):
                for w in sorted(_vars_of([t]) - seen):
                    seen.add(w)
                    queue.append(w)
    return None


def delay_comparison_filters(query: str) -> str:
    """Make each comparison FILTER wait for the anchored side of its group.

    QLever applies a FILTER as soon as its variables are bound. For
    ``?st kg:adj_p_value ?p FILTER(?p <= 0.05)`` that is the scan of the whole
    ``adj_p_value`` relation, 41 million rows in spoke-genelab, filtered and
    sorted before it is joined to the 820 statements of the one assay the query
    asks about: 4.4 s cold. Naming in the FILTER a variable that only the
    anchored side binds (``&& BOUND(?gene)``) makes QLever join first, and the
    join reads only the blocks it needs: 0.45 s. Likewise ``?st rdf:object
    <GO_…> ; ?p ?o FILTER(?p IN (…))`` filtered all 16 million prokn triples
    first (7.5 s cold, 2.5 s delayed).

    ``BOUND(?v)`` is true in every row of the group when ?v is the subject or
    object of one of its own triples, so ``(e) && BOUND(?v)`` keeps exactly the
    rows ``e`` keeps (an error in ``e`` still drops the row). The rewrite applies
    only where the group has a triple with a constant subject or an identifying
    constant object (see :func:`_anchor_kind`) other than the filtered triples:
    without a small side to start from, filtering early is the better plan.
    """
    k = 0
    while True:
        mask = _mask(query)
        heads = list(_FILTER_PAREN.finditer(mask))
        if k >= len(heads):
            return query
        out = _delay_one(query, mask, heads[k])
        if out is not None:
            query = out
        k += 1


_IRI_CALL = re.compile(r"(?:IRI|URI)\s*\(", re.I)
_LONE_VAR = re.compile(r"[?$](\w+)")


def _strip_parens(mask: str, lo: int, hi: int) -> tuple[int, int]:
    """``[lo, hi)`` without surrounding whitespace and redundant outer parentheses."""
    while True:
        while lo < hi and mask[lo].isspace():
            lo += 1
        while hi > lo and mask[hi - 1].isspace():
            hi -= 1
        if lo < hi and mask[lo] == "(" and _matching_paren(mask, lo) == hi - 1:
            lo, hi = lo + 1, hi - 1
            continue
        return lo, hi


def _top_level_equals(mask: str, lo: int, hi: int) -> int | None:
    """The offset of the one ``=`` at depth 0 of ``mask[lo:hi]``, if it is all."""
    depth = 0
    found: int | None = None
    for k in range(lo, hi):
        c = mask[k]
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        elif depth == 0:
            if mask.startswith(("&&", "||"), k) or c in "<>!":
                return None
            if c == "=":
                if found is not None:
                    return None
                found = k
    return found


def _side(mask: str, lo: int, hi: int) -> str | None:
    """``var`` for ``?v``, ``iri`` for ``IRI(…)``/``URI(…)``, else None."""
    lo, hi = _strip_parens(mask, lo, hi)
    if _LONE_VAR.fullmatch(mask, lo, hi):
        return "var"
    m = _IRI_CALL.match(mask, lo)
    if m and m.end() <= hi and _matching_paren(mask, m.end() - 1) == hi - 1:
        return "iri"
    return None


def _deep_triples(query: str, mask: str, lo: int, hi: int) -> list[Triple]:
    """The plain triples of a group body, its GRAPH blocks and its plain groups."""
    items = _items(mask, lo, hi) or []
    out: list[Triple] = []
    for k, it in enumerate(items):
        union_side = (k > 0 and items[k - 1].kind == "union") or (
            k + 1 < len(items) and items[k + 1].kind == "union"
        )
        if it.kind == "triples":
            out += _triples(query, it.start, it.end) or []
        elif it.kind in ("graph", "group") and not union_side:
            assert it.open is not None and it.close is not None
            out += _deep_triples(query, mask, it.open + 1, it.close)
    return out


def _equality_one(query: str, mask: str, m: re.Match[str]) -> str | None:
    """``query`` with the equality FILTER at ``m`` turned into a join, or None."""
    paren = m.end() - 1
    close = _matching_paren(mask, paren)
    g_open = _enclosing_brace(mask, m.start())
    if close is None or g_open is None:
        return None
    g_close = _matching_brace(mask, g_open)
    if g_close is None:
        return None
    lo, hi = _strip_parens(mask, paren + 1, close)
    eq = _top_level_equals(mask, lo, hi)
    if eq is None:
        return None
    items = _items(mask, g_open + 1, g_close)
    if items is None or not any(
        it.kind == "filter" and it.start == m.start() for it in items
    ):
        return None
    certain = _certain_vars(mask, g_open + 1, g_close)
    sides = [(lo, eq), (eq + 1, hi)]
    for (xl, xh), (el, eh) in (sides, sides[::-1]):
        xl, xh = _strip_parens(mask, xl, xh)
        el, eh = _strip_parens(mask, el, eh)
        if _side(mask, xl, xh) != "var":
            continue
        kind = _side(mask, el, eh)
        if kind is None:
            continue
        x = mask[xl + 1 : xh]
        expr = query[el:eh]
        e_vars = set(_VAR.findall(mask[el:eh]))
        if x in e_vars or x not in certain:
            continue
        if kind == "var":
            # ``=`` compares literals by value; a join compares terms. Equal
            # only when one side is an IRI or blank node: a subject or predicate.
            y = mask[el + 1 : eh]
            positioned = {
                _var(t)
                for s, p, _o in _deep_triples(query, mask, g_open + 1, g_close)
                for t in (s, p)
                if _is_var(t)
            }
            if not {x, y} & positioned:
                continue
        out = _equality_join(query, mask, items, m, close, x, expr, e_vars)
        if out is not None:
            return out
    return None


def _equality_join(
    query: str,
    mask: str,
    items: list[_Item],
    m: re.Match[str],
    close: int,
    x: str,
    expr: str,
    e_vars: set[str],
) -> str | None:
    """Move ``FILTER(?x = expr)`` into the block that binds ``expr``, as a BIND."""

    def mentions(it: _Item) -> bool:
        return x in set(_VAR.findall(mask[it.start : it.end]))

    def union_side(k: int) -> bool:
        return (k > 0 and items[k - 1].kind == "union") or (
            k + 1 < len(items) and items[k + 1].kind == "union"
        )

    for ka, a in enumerate(items):
        if a.kind not in ("graph", "group") or union_side(ka) or mentions(a):
            continue
        assert a.open is not None and a.close is not None
        if not e_vars <= _certain_vars(mask, a.open + 1, a.close):
            continue
        ok = True
        binders_end = a.end
        for k, it in enumerate(items):
            if it is a or it.start == m.start() or not mentions(it):
                continue
            if union_side(k) or it.kind == "service":
                ok = False
            elif it.kind in ("triples", "graph", "group", "values", "subquery"):
                binders_end = max(binders_end, it.end)
        if not ok:
            continue
        # An OPTIONAL, MINUS or BIND that reads ?x sees it bound in both forms
        # only if it comes after every pattern that binds it.
        if any(
            it.kind in ("optional", "minus", "bind")
            and mentions(it)
            and it.start < binders_end
            for it in items
        ):
            continue
        bind = f" BIND({expr} AS ?{x}) FILTER(BOUND(?{x})) "
        edits = sorted(
            [(a.close, a.close, bind), (m.start(), close + 1, None)],
            key=lambda e: e[0],
            reverse=True,
        )
        out = query
        for lo, hi, text in edits:
            if text is None:
                out = _drop_span(out, _mask(out), lo, hi)
            else:
                out = out[:lo] + text + out[hi:]
        return out
    return None


def filter_equality_to_join(query: str) -> str:
    """Turn a cross-block ``FILTER(?x = IRI(…))`` into a join on ``?x``.

    QLever has no join for an equality written as a FILTER: in
    ``GRAPH <a> { … ?ens } GRAPH <b> { ?s rdf:subject ?pg … }
    FILTER(?pg = IRI(CONCAT("…/ensembl/", ?ens)))`` it builds every pairing of
    the two blocks' rows and then filters them, which timed out after 90 s on a
    GXA × PanKgraph query that, as a join, takes 0.7 s. Nine such queries in the
    v0.5-v0.6 benchmark logs spent 388 s, most of it in timeouts.

    The rewrite computes the key where its inputs are bound:
    ``GRAPH <a> { … BIND(IRI(…) AS ?pg) FILTER(BOUND(?pg)) }``, so the two
    blocks share ``?pg`` and QLever joins them. It is exact when:

    * the right side is ``IRI(…)``/``URI(…)`` (an IRI or an error), or a variable
      where one of the two variables is a subject or predicate somewhere in the
      group (an IRI or blank node), so ``=`` is term equality, which is what a
      join tests;
    * every variable of the expression is certainly bound in one GRAPH block or
      plain group A that does not mention ``?x``, and ``?x`` is certainly bound in
      the group (so the FILTER never saw it unbound);
    * no UNION branch or SERVICE mentions ``?x``, and an OPTIONAL, MINUS or BIND
      that does comes after every pattern binding ``?x``, A included, so it sees
      ``?x`` bound in both forms.

    A row of A whose expression is an error is dropped by ``FILTER(BOUND(?x))``,
    as the original FILTER dropped every pairing made from it.
    """
    k = 0
    while True:
        mask = _mask(query)
        heads = list(_FILTER_PAREN.finditer(mask))
        if k >= len(heads):
            return query
        out = _equality_one(query, mask, heads[k])
        if out is not None:
            query = out
            continue
        k += 1

"""Rewrite IRI-prefix FILTERs so QLever can skip index blocks.

Agents and catalog skeletons constantly test an IRI's namespace with
``FILTER(STRSTARTS(STR(?x), "http://purl.obolibrary.org/obo/MONDO_"))``. QLever
answers that by reading every row of the scan that binds ``?x`` and building a
string for each: ``STR()`` hides the variable from the planner. A range test on
the variable itself, ``?x >= <lo> && ?x < <hi>``, maps onto QLever's sorted
vocabulary instead, so the scan reads only the blocks that can hold the prefix.
On the federation endpoint (measured November 2026) that turned 14 s into 0.07 s for
``rdf:type`` subjects in spoke-okn, 2.7 s into 0.08 s for prokn's HP cross-
references, and a 120 s timeout into 11 s for CHEBI subclasses in ubergraph.

:func:`prefilter_prefix_tests` adds that range IN FRONT of the original test and
keeps the test, so the result is exactly the same:

    STRSTARTS(STR(?x), "P")
    → (((?x >= <L> && ?x < <P+U+EFFFD>) || isLiteral(?x)) && STRSTARTS(STR(?x), "P"))

Why each part is needed:

* **The original test stays.** QLever orders IRIs by ICU collation, which is
  case-insensitive at its first level, so the range also admits ``…/mondo_1`` and
  other near neighbours. The range only has to be a superset; the exact,
  case-sensitive test then decides.
* **The lower bound ``L`` is ``P`` cut just before its last ASCII letter**
  (``…/MOND`` for ``…/MONDO_``). QLever compares IRIs WITH their closing ``>``,
  and in ICU order punctuation sorts below ``>``: ``<P>`` itself sorts after
  ``<P-x>``, so ``P`` would wrongly exclude an IRI whose remainder starts with
  punctuation. ``L`` ends before a letter, and ``>`` sorts below every letter in
  ICU order, in byte order, and with punctuation ignored (QLever compares IRIs
  that are not in its index, from BIND or VALUES, in a different order from
  indexed ones; the bound must hold in all of them).
* **The upper bound is ``P`` followed by U+EFFFD**, an unassigned code point
  that sorts after every assigned character in each of those orders.
* **``|| isLiteral(?x)``** keeps literals, whose lexical form ``STR()`` also
  tests (a literal ``"http://…"`` is not an IRI and fails the range). QLever
  still prefilters on the disjunction.

The rewrite is applied only where a FILTER can only keep or drop rows: an
``STRSTARTS(STR(?v), "…")`` that is the whole FILTER, or a leaf of a tree of
``&&`` / ``||`` under it. There the added conjunct can turn an error into
``false`` at most (an unbound or blank-node ``?v``), which a FILTER treats the
same. Under ``!``, ``IF``, ``BIND``, ``COALESCE`` or a comparison the test is left
alone, as are prefixes that do not look like an IRI (``"MESH:"`` is a literal's
prefix: write ``STRSTARTS(?x, "MESH:")`` without ``STR`` for that, which QLever
prefilters directly).

One shape is left alone because the range makes it slower: a variable that a
babel triple binds. There ``?member skos:exactMatch ?pref`` usually gets a small
set of clique leaders ``?pref`` from a subquery, and QLever answers it by reading
only the blocks of those leaders. Given a range on ``?member`` it reads every
babel row in that namespace instead: in the 2026-11 A/B over the catalog's 143
rewritable skeletons, the six that got slower (up to 12x) were all of this shape,
and none of this shape got faster.

**It is opt-in, per query.** A query asks for it with a comment line
``# okn:prefilter`` (:data:`PRAGMA`); :func:`mcp_okn.sparql.run_sparql` then
rewrites it. The range helps when the filtered variable drives the scan: 52
catalog skeletons take 421 s without it and 69 s with it (cold, November 2026),
and those carry the line. It hurts when the variable is already pinned by a
selective join, because QLever then range-scans the namespace instead of
following the join: over the 230 slowest rewritable queries in the worked-example
transcripts, mostly written that way, it saved about 1% in total, made a few
queries 5-20x slower (1.7 s to 19 s) and pushed two past the time limit. Nothing
in the query text tells the two apart, so the default leaves queries alone.
"""

from __future__ import annotations

import re

#: The comment line that asks for the rewrite (see the module docstring).
PRAGMA = "# okn:prefilter"
_PRAGMA = re.compile(r"^[ \t]*#[ \t]*okn:prefilter\b", re.M | re.I)

#: Sorts after every assigned character (see the module docstring).
_HIGH = "\U000efffd"

#: A string, an IRI or a comment: regions where keywords and operators are text.
_OPAQUE = re.compile(
    r'"""(?:[^"\\]|\\.|"(?!""))*"""'
    r"|'''(?:[^'\\]|\\.|'(?!''))*'''"
    r'|"(?:[^"\\\n]|\\.)*"'
    r"|'(?:[^'\\\n]|\\.)*'"
    r'|<[^<>"{}|^`\\\x00-\x20]*>'
    r"|#[^\n]*",
)

#: ``STRSTARTS(STR(?v), "P")`` as a whole atom. No escapes in ``P``.
_PREFIX_TEST = re.compile(
    r"\s*STRSTARTS\s*\(\s*STR\s*\(\s*([?$]\w+)\s*\)\s*,\s*"
    r"(?:\"([^\"\\\n]*)\"|'([^'\\\n]*)')\s*\)\s*",
    re.I,
)

#: An absolute IRI prefix: a scheme, then only characters an IRIREF allows. ASCII
#: only, so the collation arguments above hold.
_IRI_PREFIX = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*:[\x21-\x7e]*")
_IRIREF_FORBIDDEN = set('<>"{}|^`\\')

_FILTER = re.compile(r"\bFILTER\b", re.I)
_GRAPH = re.compile(r"\bGRAPH\b", re.I)
_VAR = re.compile(r"[?$](\w+)")

#: Graphs whose triples are better driven by a join than by a range (see the
#: module docstring).
_JOIN_DRIVEN_GRAPHS = ("/kg/babel>",)


def _mask(query: str) -> str:
    """``query`` with every string, IRI and comment blanked to ``_``.

    Positions are preserved, so a match in the mask indexes the original text.
    """
    return _OPAQUE.sub(lambda m: "_" * len(m.group(0)), query)


def _matching_paren(mask: str, start: int) -> int | None:
    """Index of the ``)`` closing the ``(`` at ``start``, or None."""
    depth = 0
    for i in range(start, len(mask)):
        c = mask[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
    return None


def _split_top(mask: str, lo: int, hi: int, op: str) -> list[tuple[int, int]]:
    """Spans of ``mask[lo:hi]`` separated by ``op`` at parenthesis depth 0."""
    parts = []
    depth = 0
    start = lo
    i = lo
    while i < hi:
        c = mask[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and mask.startswith(op, i):
            parts.append((start, i))
            i += len(op)
            start = i
            continue
        i += 1
    parts.append((start, hi))
    return parts


def _range_for(prefix: str) -> tuple[str, str] | None:
    """(lower, upper) IRI bounds around every IRI starting with ``prefix``."""
    if len(prefix) < 10 or not _IRI_PREFIX.fullmatch(prefix):
        return None
    if _IRIREF_FORBIDDEN.intersection(prefix):
        return None
    # A prefix that stops inside the host ("http://stko-kwg") matches most of a
    # graph, so the range selects nothing and QLever range-scans it all instead
    # of joining (2.8 s -> 51 s on the spatialkg county joins in the A/B).
    authority = prefix.find("//")
    if authority != -1 and prefix.find("/", authority + 2) == -1:
        return None
    letters = [i for i, c in enumerate(prefix) if c.isascii() and c.isalpha()]
    # The scheme always has a letter; a bound cut inside it would admit nearly
    # every IRI, which is correct but useless.
    if not letters or letters[-1] < prefix.index(":"):
        return None
    return prefix[: letters[-1]], prefix + _HIGH


def _join_driven_vars(query: str, mask: str) -> set[str]:
    """Names of the variables used inside a GRAPH block of a join-driven graph."""
    names: set[str] = set()
    for m in _GRAPH.finditer(mask):
        i = m.end()
        while i < len(mask) and mask[i].isspace():
            i += 1
        if i >= len(mask) or query[i] != "<":
            continue
        end = query.find(">", i)
        if end == -1 or not query[i : end + 1].endswith(_JOIN_DRIVEN_GRAPHS):
            continue
        open_ = mask.find("{", end)
        close = _matching_brace(mask, open_) if open_ != -1 else None
        if close is None:
            continue
        names.update(_VAR.findall(mask[open_:close]))
    return names


def _matching_brace(mask: str, start: int) -> int | None:
    """Index of the ``}`` closing the ``{`` at ``start``, or None."""
    depth = 0
    for i in range(start, len(mask)):
        if mask[i] == "{":
            depth += 1
        elif mask[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return None


def _rewrite_atom(text: str, skip: set[str]) -> str:
    m = _PREFIX_TEST.fullmatch(text)
    if not m or m.group(1)[1:] in skip:
        return text
    var = m.group(1)
    prefix = m.group(2) if m.group(2) is not None else m.group(3)
    bounds = _range_for(prefix)
    if bounds is None:
        return text
    lo, hi = bounds
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()) :]
    return (
        f"{lead}((({var} >= <{lo}> && {var} < <{hi}>) || isLiteral({var})) "
        f"&& {text.strip()}){trail}"
    )


def _rewrite_expr(query: str, mask: str, lo: int, hi: int, skip: set[str]) -> str:
    """Rewrite the boolean expression ``query[lo:hi]``; return its new text."""
    seg = mask[lo:hi]
    stripped_lo = lo + (len(seg) - len(seg.lstrip()))
    stripped_hi = hi - (len(seg) - len(seg.rstrip()))
    # A fully parenthesized expression: recurse inside the parentheses.
    if stripped_lo < stripped_hi and mask[stripped_lo] == "(":
        close = _matching_paren(mask, stripped_lo)
        if close == stripped_hi - 1:
            inner = _rewrite_expr(query, mask, stripped_lo + 1, close, skip)
            return f"{query[lo:stripped_lo]}({inner}){query[close + 1 : hi]}"
    for op in ("||", "&&"):
        parts = _split_top(mask, lo, hi, op)
        if len(parts) > 1:
            return op.join(_rewrite_expr(query, mask, a, b, skip) for a, b in parts)
    return _rewrite_atom(query[lo:hi], skip)


def wants_prefilter(query: str) -> bool:
    """True when ``query`` carries the :data:`PRAGMA` comment line."""
    return bool(_PRAGMA.search(query))


def prefilter_prefix_tests(query: str) -> str:
    """Add a block-skipping IRI range to each FILTER's ``STRSTARTS(STR(?v), …)``.

    Returns ``query`` unchanged when there is nothing to rewrite. See the module
    docstring for why the result is identical.
    """
    # The upper bound's code point never appears in a hand-written query, so its
    # presence means the query was already rewritten.
    if "strstarts" not in query.lower() or _HIGH in query:
        return query
    mask = _mask(query)
    skip = _join_driven_vars(query, mask)
    out = []
    pos = 0
    for m in _FILTER.finditer(mask):
        i = m.end()
        while i < len(mask) and mask[i].isspace():
            i += 1
        if i >= len(mask):
            break
        if mask[i] == "(":
            close = _matching_paren(mask, i)
            if close is None:
                break
            new = _rewrite_expr(query, mask, i + 1, close, skip)
            out.append(query[pos : i + 1])
            out.append(new)
            pos = close
        elif mask[i : i + 9].upper() == "STRSTARTS":
            # FILTER STRSTARTS(...) with no outer parentheses.
            open_ = mask.find("(", i)
            close = _matching_paren(mask, open_) if open_ != -1 else None
            if close is None:
                break
            new = _rewrite_atom(query[i : close + 1], skip)
            if new != query[i : close + 1]:
                out.append(query[pos:i])
                out.append(f"({new})")
                pos = close + 1
    if not out:
        return query
    out.append(query[pos:])
    return "".join(out)


#: A prefix that names a literal's form rather than an IRI: ``UMLS:``, ``cas:``,
#: ``WURCS=``. No ``/``, so it is not a URL, and short enough to be a CURIE prefix.
_CURIE_PREFIX = re.compile(r"[A-Za-z][A-Za-z0-9_.\-]{0,30}[:=_]")
_SCHEMES = frozenset({"http:", "https:", "urn:", "ftp:", "file:", "mailto:"})


def literal_prefix_hint(query: str) -> str | None:
    """Advice for a slow query that tests a literal's prefix through ``STR()``.

    ``STRSTARTS(STR(?x), "UMLS:")`` makes QLever build and test a string for
    every row of the scan that binds ``?x``; ``STRSTARTS(?x, "UMLS:")`` on a
    literal lets it skip index blocks instead (17.7 s against 0.17 s for the
    MESH cross-references in ubergraph). The server cannot make that rewrite
    itself, because the two differ when ``?x`` is an IRI, so it is offered as
    advice when such a query runs out of time.
    """
    mask = _mask(query)
    for m in _PREFIX_TEST.finditer(query):
        # Only real code, not text inside a string, IRI or comment.
        if mask[m.start(1)] != query[m.start(1)]:
            continue
        prefix = m.group(2) if m.group(2) is not None else m.group(3)
        if _CURIE_PREFIX.fullmatch(prefix) and prefix.lower() not in _SCHEMES:
            var = m.group(1)
            return (
                f'STRSTARTS(STR({var}), "{prefix}") reads every row that binds '
                f"{var}. If {var} holds literals (a CURIE string), write "
                f'STRSTARTS({var}, "{prefix}") without STR(): the engine then '
                "skips index blocks and the filter is often 10-100x faster."
            )
    return None


# --- VALUES feeding an open predicate ----------------------------------------
#
# ``VALUES ?x { <a> <b> }`` joined with ``?s ?p ?x`` -- the predicate left open --
# is a QLever planning trap. With the IRI written in place, ``?s ?p <a>`` is an
# index lookup; with it supplied by VALUES, QLever plans the open-predicate scan
# first and joins the VALUES afterwards, so it reads the whole graph. On the
# federation endpoint (November 2026), an agent's probe
#
#     VALUES ?cond { <MONDO_0007179> <NCIT_C2889> }
#     GRAPH <…/oard-kg> { ?a ?p ?cond . ?a a ?cls }
#
# took 179 s, and with one IRI in the VALUES block it ran past 180 s; written as
# a UNION of the same group with each IRI in place it took 0.6 s. In the
# benchmark logs, this shape was 158 of 4,013 agent queries and 1,020 s of their
# 16,577 s of endpoint time.
#
# :func:`inline_values_for_open_predicates` makes that rewrite. For a group G
# that holds ``VALUES ?x { v1 … vk }`` it produces
#
#     { G' [?x := v1]  BIND(v1 AS ?x) } UNION … UNION { G' [?x := vk]  BIND(vk AS ?x) }
#
# where G' is G without the VALUES clause. A VALUES clause joins its rows with
# the rest of the group, so G is the union over i of (G' joined with ?x = vi),
# and substituting a variable fixed to vi by vi itself is the same pattern. Each
# VALUES clause is rewritten on its own, and only where the substitution is
# exact:
#
# * the clause is on one variable, with 1 to :data:`MAX_INLINE_VALUES` IRIs or
#   prefixed names (no literals, no UNDEF), and sits inside a group (not
#   trailing the query); the rest of the group holds no other VALUES clause,
#   subquery or SERVICE, and nothing in it assigns ?x (``AS ?x``);
# * every use of ?x is a join. Plain and GRAPH groups and UNION branches pass:
#   a join distributes over UNION (and QLever evaluates each branch alone, so
#   there the rewrite matters most). An OPTIONAL passes only as a direct child
#   of G written after the VALUES clause: a left join evaluated before ?x is
#   fixed keeps rows that the substitution would drop. MINUS, EXISTS and
#   deeper OPTIONALs fail;
# * a use inside an expression is in G itself, in a FILTER (scoped to the whole
#   group) or a BIND after the VALUES clause. A nested group's FILTER or BIND
#   cannot see the outer ?x, so the substitution would change it;
# * with two or more values, ?x is the subject or object of a triple whose
#   predicate is a variable -- the shape that is slow -- and no all-variable
#   triple (``?a ?b ?c``) without ?x would run on its own -- inside a nested
#   group, or sharing no variable with a triple using ?x: every branch repeats
#   the group, so such a scan would run once per value. Other VALUES blocks
#   with several values are left as written;
# * a single value is always written in place (no branches, nothing repeated).
#   In the v0.6.3 benchmark, ``VALUES ?d { <MONDO_…> }`` outside a UNION over
#   oard-kg associations took 8.5-12.5 s cold: QLever computed the branches over
#   all 5.2 million associations before joining the one disease. With the
#   constant in each branch the same query took 2.0 s cold.

#
# Replayed live on 2026-11-09 against every logged benchmark query it would have
# changed under looser rules (207), each form run separately: the 98 these rules
# still rewrite went from 541 s to 57 s where both forms finished, 18 that had
# failed (timeouts, out-of-memory) returned rows, none got slower, and every
# result matched up to what SPARQL leaves open (SAMPLE, GROUP_CONCAT order, a
# LIMIT without ORDER BY). The 109 the guards leave alone held every case the
# rewrite made slower -- VALUES feeding a predicate, an OPTIONAL scan repeated
# per branch -- and the one it made time out.

#: More values than this are left as a VALUES block: each value copies the group.
MAX_INLINE_VALUES = 20

_VALUES = re.compile(r"\bVALUES\b", re.I)
_VALUES_HEAD = re.compile(r"\s*[?$](\w+)\s*\{")
#: One VALUES datum: an IRI or a prefixed name.
_DATUM = re.compile(
    r'<[^<>"{}|^`\\\x00-\x20]*>|(?:[A-Za-z][\w\-.]*)?:[\w\-%]+(?:[\w\-.%]*[\w\-%])?'
)
#: Text before a group's ``{`` that makes it a negation, a subquery or remote:
#: a use of ?x there is never substituted.
_BLOCKING_GROUP_HEAD = re.compile(
    r"(?:\bMINUS|\bEXISTS|\bSERVICE\b[^{]*|\bWHERE|\bSELECT\b[^{]*)$", re.I
)
_OPTIONAL_HEAD = re.compile(r"\bOPTIONAL$", re.I)
_EXPRESSION_HEAD = re.compile(r"\b(FILTER|BIND)\s*$", re.I)
_SUBQUERY_OR_REMOTE = re.compile(r"\b(?:SELECT|VALUES|SERVICE)\b", re.I)
#: Three variables in a row: a triple pattern with nothing bound.
_ALL_VARIABLE_TRIPLE = re.compile(r"[?$]\w+\s+[?$]\w+\s+[?$]\w+\b")


def _enclosing_brace(mask: str, pos: int) -> int | None:
    """Index of the ``{`` of the innermost group around ``pos``, or None."""
    depth = 0
    for i in range(pos - 1, -1, -1):
        if mask[i] == "}":
            depth += 1
        elif mask[i] == "{":
            if depth == 0:
                return i
            depth -= 1
    return None


def _open_groups(mask: str, pos: int) -> list[int]:
    """The ``{`` of every group around ``pos`` in ``mask``, outermost first."""
    stack: list[int] = []
    for i in range(pos):
        if mask[i] == "{":
            stack.append(i)
        elif mask[i] == "}" and stack:
            stack.pop()
    return stack


def _expression_head(mask: str, start: int, pos: int) -> str | None:
    """The expression keyword ``pos`` sits under, between ``start`` and ``pos``.

    ``""`` if ``pos`` is outside parentheses, else the keyword (FILTER or BIND)
    before the outermost open one, or None if there is none.
    """
    opened: list[int] = []
    for i in range(start, pos):
        if mask[i] == "(":
            opened.append(i)
        elif mask[i] == ")" and opened:
            opened.pop()
    if not opened:
        return ""
    head = _EXPRESSION_HEAD.search(mask[: opened[0]])
    return head.group(1).upper() if head else None


def _uses_are_joins(mask: str, uses: list[int], values_at: int) -> bool:
    """True if substituting each use in ``mask`` by a constant keeps the result exact.

    ``mask`` is the group without its VALUES clause, which stood at ``values_at``.
    """
    for u in uses:
        groups = _open_groups(mask, u)
        for depth, b in enumerate(groups):
            head = mask[:b].rstrip()
            if _BLOCKING_GROUP_HEAD.search(head):
                return False
            if _OPTIONAL_HEAD.search(head) and (depth > 0 or b < values_at):
                return False
        expression = _expression_head(mask, groups[-1] + 1 if groups else 0, u)
        if expression == "":
            continue
        if groups or expression is None:
            return False
        if expression == "BIND" and u < values_at:
            return False
    return True


def _evaluated_alone(mask: str, brace: int) -> bool:
    """Is the group opened at ``brace`` evaluated apart from its siblings?

    True for OPTIONAL, MINUS, EXISTS and UNION branches; plain and GRAPH groups
    are joins with what surrounds them.
    """
    head = mask[:brace].rstrip()
    if (
        _OPTIONAL_HEAD.search(head)
        or _BLOCKING_GROUP_HEAD.search(head)
        or head[-5:].upper() == "UNION"
    ):
        return True
    close = _matching_brace(mask, brace)
    return close is not None and mask[close + 1 :].lstrip()[:5].upper() == "UNION"


def _repeats_a_scan(mask: str, var: str) -> bool:
    """Would each branch repeat a full scan that does not involve ?x?

    Every branch repeats the rest of the group, so a triple of three variables
    evaluated on its own runs once per value: an ``OPTIONAL { ?o ?p2 ?o2 }``
    took 109 s once and ran past 180 s twice. One inside an OPTIONAL, MINUS,
    EXISTS or UNION branch is evaluated on its own, and so is one that shares no
    variable with a triple using ?x. One that
    joins such a triple -- ``?a ?p ?x . ?b ?q ?a`` -- is a further hop from
    the bound value, which the rewrite speeds up too (past 180 s to 8 s).
    """
    x = re.compile(rf"[?$]{var}\b")
    # Statements (between braces and dots) that use ?x, and their variables.
    near = {
        v
        for stmt in re.findall(r"[^{}.]+", mask)
        if x.search(stmt)
        for v in re.findall(r"[?$](\w+)", stmt)
    }
    for triple in _ALL_VARIABLE_TRIPLE.finditer(mask):
        if x.search(triple.group(0)):
            continue
        if any(_evaluated_alone(mask, b) for b in _open_groups(mask, triple.start())):
            return True
        if not near & set(re.findall(r"[?$](\w+)", triple.group(0))):
            return True
    return False


def _inline_one(query: str, mask: str, values: re.Match[str]) -> str | None:
    """The query with one VALUES clause inlined, or None if that is not exact."""
    head = _VALUES_HEAD.match(mask, values.end())
    if head is None:
        return None
    var = head.group(1)
    data_open = head.end() - 1
    data_close = _matching_brace(mask, data_open)
    if data_close is None:
        return None
    body = query[data_open + 1 : data_close]
    data = _DATUM.findall(body)
    if not data or len(data) > MAX_INLINE_VALUES or _DATUM.sub("", body).strip():
        return None

    group_open = _enclosing_brace(mask, values.start())
    group_close = _matching_brace(mask, group_open) if group_open is not None else None
    if group_open is None or group_close is None or group_close < data_close:
        return None

    # The group without its VALUES clause, as text and as mask, aligned.
    values_at = values.start() - group_open - 1
    rest = query[group_open + 1 : values.start()] + query[data_close + 1 : group_close]
    rest_mask = (
        mask[group_open + 1 : values.start()] + mask[data_close + 1 : group_close]
    )
    if _SUBQUERY_OR_REMOTE.search(rest_mask) or re.search(
        rf"\bAS\s+[?$]{var}\b", rest_mask, re.I
    ):
        return None
    uses = [m.start() for m in re.finditer(rf"[?$]{var}\b", rest_mask)]
    if not uses or not _uses_are_joins(rest_mask, uses, values_at):
        return None
    # ?x as the object, or (starting a triple) the subject, of a variable predicate.
    open_predicate = re.search(
        rf"(?:[?$]\w+|_+|[\w\-.]*:[\w\-.%]*|;)\s+[?$]\w+\s+[?$]{var}\b", rest_mask
    ) or re.search(rf"(?:^|[{{}}.])\s*[?$]{var}\s+[?$]\w+\s+\S", rest_mask)
    # One value needs no branches, so nothing is repeated: the constant in place
    # is an index lookup whatever the predicate, where QLever otherwise computes
    # a group the VALUES row cannot reach (a UNION branch, say) over the whole
    # relation first. Two or more values copy the group, which pays only where
    # the predicate is open.
    if len(data) > 1 and (not open_predicate or _repeats_a_scan(rest_mask, var)):
        return None

    def branch(datum: str) -> str:
        out, last = [], 0
        for u in uses:
            out.append(rest[last:u])
            out.append(datum)
            last = u + 1 + len(var)
        out.append(rest[last:])
        return "".join(out).strip() + f"\n    BIND({datum} AS ?{var})"

    if len(data) == 1:
        inner = "  " + branch(data[0])
    else:
        inner = "\n  UNION\n".join("  {\n    " + branch(d) + "\n  }" for d in data)
    return query[: group_open + 1] + "\n" + inner + "\n" + query[group_close:]


def inline_values_for_open_predicates(query: str) -> str:
    """Write VALUES blocks' IRIs into the groups where open predicates meet them.

    See the comment above :data:`MAX_INLINE_VALUES` for why and when. A VALUES
    clause is left as written whenever any condition for an exact rewrite fails.
    """
    skip = 0
    while True:
        mask = _mask(query)
        heads = list(_VALUES.finditer(mask))
        if skip >= len(heads):
            return query
        # Each success removes one clause, so this ends; after one, retry all
        # (an enclosing clause may qualify once the inner one is inlined).
        out = _inline_one(query, mask, heads[len(heads) - 1 - skip])
        if out is None:
            skip += 1
        else:
            query, skip = out, 0

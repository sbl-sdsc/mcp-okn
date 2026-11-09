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
"""

from __future__ import annotations

import re

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

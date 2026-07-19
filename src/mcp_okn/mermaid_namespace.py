"""Give each embedded query diagram a unique node-id namespace.

`sparql_to_mermaid` renders every `graph TD` query diagram with the SAME node ids
(``graph0``, ``v1``, ``bind0``, ``optionalgraph00`` …) because it names ids from a
per-query scope that always starts empty. That is fine for a lone diagram, but a
transcript embeds many of them in ONE document/page: those ids become DOM/SVG
element ids and `style graph0 …` targets, so once several diagrams share ``graph0``
the collisions make later diagrams fail to render ("renders fine for a while, then
stops"). :func:`namespace_document` walks a markdown document's ```mermaid blocks and
prefixes the ids of each `graph TD` diagram with a per-block ``q<N>`` namespace, so
no two collide.

The rewrite is a text transform (the diagrams arrive already-rendered — from the
server's ``try_to_mermaid`` loop or from the ``sparql_to_mermaid`` tool via the
report-style re-add scripts — so re-generating with a scoped prefix is not an
option on every path). It is label-safe: double-quoted label spans are masked before
any id is rewritten, so a literal that merely LOOKS like an id (a URI segment
``…/v1``) is preserved. Only `graph TD` diagrams are touched; a `classDiagram` schema
diagram (different grammar, semantically-named ids that don't collide) passes through
unchanged. An empty prefix is a no-op, so the transform is byte-identical to the
input when disabled.
"""

from __future__ import annotations

import re

_QUOTED = re.compile(r'"(?:[^"\\]|\\.)*"')
# An id is INTRODUCED by a declaration line: ``  <id>(`` / ``  <id>[`` / ``  <id>{``
# (a node), ``subgraph <id>[…]``, or ``style <id> …``. Ids are ``[A-Za-z]\w*``.
_NODE_DECL = re.compile(r"^\s*([A-Za-z]\w*)(?:\(|\[|\{)")
_SUBGRAPH_DECL = re.compile(r"^\s*subgraph\s+([A-Za-z]\w*)")
_STYLE_DECL = re.compile(r"^\s*style\s+([A-Za-z]\w*)")
# Line-leading words that are Mermaid keywords, never node ids.
_KEYWORDS = frozenset({"subgraph", "end", "style", "classDef", "graph", "linkStyle", "click"})


def _first_directive(mermaid: str) -> str:
    """The diagram's opening directive (first non-blank line), e.g. ``graph TD``."""
    for line in mermaid.split("\n"):
        s = line.strip()
        if s:
            return s
    return ""


def _collect_ids(mermaid: str) -> set[str]:
    """Every node/subgraph id declared in the diagram.

    Edges only ever reference ids that are declared elsewhere, so the declaration
    sites are the full id set.
    """
    ids: set[str] = set()
    for line in mermaid.split("\n"):
        for pat in (_SUBGRAPH_DECL, _STYLE_DECL):
            m = pat.match(line)
            if m:
                ids.add(m.group(1))
        m = _NODE_DECL.match(line)
        if m and m.group(1) not in _KEYWORDS:
            ids.add(m.group(1))
    return ids


def namespace_diagram(mermaid: str, prefix: str) -> str:
    """Prefix every node id in a `graph TD` diagram with ``prefix``.

    Returns ``mermaid`` unchanged when ``prefix`` is empty or the diagram is not a
    `graph TD` (e.g. a `classDiagram`). Label text (double-quoted spans) is never
    altered.
    """
    if not prefix or _first_directive(mermaid) != "graph TD":
        return mermaid
    ids = _collect_ids(mermaid)
    if not ids:
        return mermaid
    # Longest id first, plus word-boundary lookarounds, so ``graph0`` is never
    # rewritten inside ``graph0bind0`` (which is matched as its own token).
    alt = "|".join(re.escape(i) for i in sorted(ids, key=len, reverse=True))
    id_re = re.compile(rf"(?<![A-Za-z0-9])(?:{alt})(?![A-Za-z0-9])")
    sub = lambda m: prefix + m.group(0)  # noqa: E731

    def rewrite(line: str) -> str:
        # Rewrite ids only in the gaps BETWEEN quoted label spans.
        out: list[str] = []
        pos = 0
        for m in _QUOTED.finditer(line):
            out.append(id_re.sub(sub, line[pos : m.start()]))
            out.append(m.group(0))
            pos = m.end()
        out.append(id_re.sub(sub, line[pos:]))
        return "".join(out)

    result = []
    for line in mermaid.split("\n"):
        s = line.strip()
        if s == "graph TD" or s.startswith("classDef "):
            result.append(line)  # header / classDef carry no node ids
        else:
            result.append(rewrite(line))
    return "\n".join(result)


def namespace_document(markdown: str, prefix: str = "q") -> str:
    """Namespace every ```mermaid `graph TD` block in a markdown document.

    The k-th mermaid block is given the id namespace ``<prefix><k>`` so no two query
    diagrams on the page collide. Fence lines are preserved exactly (block counts are
    unchanged); non-`graph TD` blocks pass through untouched.
    """
    lines = markdown.split("\n")
    out: list[str] = []
    i, n, k = 0, len(lines), 0
    while i < n:
        if lines[i].strip() == "```mermaid":
            body: list[str] = []
            j = i + 1
            while j < n and lines[j].strip() != "```":
                body.append(lines[j])
                j += 1
            block = namespace_diagram("\n".join(body), f"{prefix}{k}")
            k += 1
            out.append(lines[i])
            out.extend(block.split("\n"))
            if j < n:  # closing fence (absent only on a truncated document)
                out.append(lines[j])
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)

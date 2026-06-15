# Verification: schema.org http/https normalization

Confirms that `normalize_schema_org` (in `src/mcp_okn/sparql.py`) fixes the
`http://schema.org/` vs `https://schema.org/` mismatch that otherwise causes
queries to silently return no rows.

## Setup

The DREAM-KG (`dreamkg`) named graph stores schema.org terms under the canonical
`http://schema.org/` form. `http://schema.org/Rating` has **3762** instances.

## Result

Running a count of `schema.org/Rating` instances against `dreamkg`, written with
the `https://` form a model commonly produces:

| Path | Rows |
| --- | --- |
| `<https://schema.org/Rating>` sent verbatim (no normalization) | **0** |
| Same query via `run_sparql` (normalization applied) | **3762** |
| Ground truth: `<http://schema.org/Rating>` instance count | 3762 |

The unmodified `https://` query silently matches nothing because it is a distinct
IRI from the `http://` form the data uses. `normalize_schema_org` rewrites it to
`http://` and recovers all 3762 matches.

## Reproduce

```python
import asyncio
from mcp_okn.sparql import run_sparql, named_graph

g = named_graph("dreamkg")
q = f'SELECT (COUNT(*) AS ?n) WHERE {{ GRAPH <{g}> {{ ?s a <https://schema.org/Rating> }} }}'
print(asyncio.run(run_sparql(q)))  # -> 3762 rows, despite the https:// IRI
```

## Graphs that store the non-canonical `https` form

The canonicalization is **scoped to bracketed IRIs** (`<https://schema.org/…>`), so
string literals and `IRI(CONCAT("https://schema.org/", …))` are left untouched. That
matters because a few graphs store schema.org predicates under the `https` form, where
a bracketed IRI (either scheme) matches nothing — the `https` form is canonicalized to
`http`, and the plain `http` form is what the data isn't. They are reachable by binding
the predicate as a variable, or by rebuilding the IRI from a (preserved) string literal.

Verified live against the federation:

| Graph (predicate) | `<https://schema.org/X>` bracketed | `IRI(CONCAT('https://schema.org/','X'))` | `STRENDS(STR(?p),'schema.org/X')` |
| --- | --- | --- | --- |
| `nikg` (`location`) | 0 | 296,189 | 296,189 |
| `ruralkg` (`postalCode`) | 0 | 9,037 | 9,037 |
| `ufokn` (`value`, level-13 sample) | 0 | 5/5 (`LIMIT 5`) | 5/5 |

The `IRI(CONCAT)` and `STRENDS` forms agree in every case (for `ufokn`, the same 64-bit
decimal S2 ids, e.g. `9813806808853118976`), while the bracketed IRI returns 0.

```python
import asyncio
from mcp_okn.sparql import run_sparql, named_graph

g = named_graph("ruralkg")
# bracketed https IRI -> canonicalized to http -> 0
q0 = f'SELECT (COUNT(*) AS ?n) WHERE {{ GRAPH <{g}> {{ ?b <https://schema.org/postalCode> ?z }} }}'
# rebuild the IRI from a string literal (not rewritten) -> 9037
q1 = (f'SELECT (COUNT(*) AS ?n) WHERE {{ GRAPH <{g}> {{ ?b ?p ?z . '
      f'FILTER(?p = IRI(CONCAT("https://schema.org/","postalCode"))) }} }}')
print(asyncio.run(run_sparql(q0)), asyncio.run(run_sparql(q1)))  # -> 0 , 9037
```

`ufokn` has ~11.7M S2-cell nodes, so scope the value pull to level-13 blank nodes and
bound it with `LIMIT` (an unbounded scan times out at 120s):

```python
g = named_graph("ufokn")
q = f'''SELECT ?s2id WHERE {{ GRAPH <{g}> {{
  ?bn ?pn "s2Level13" . ?bn ?pv ?s2id .
  FILTER(?pv = IRI(CONCAT("https://schema.org/","value")))
}} }} LIMIT 5'''
print(asyncio.run(run_sparql(q)))  # -> 5 decimal S2 ids
```

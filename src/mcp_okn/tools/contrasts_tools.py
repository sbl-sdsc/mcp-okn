"""spoke-genelab contrast vetting tool: get_valid_contrasts."""

from __future__ import annotations

from typing import Any

from ..app import mcp
from ..contrasts import classify_contrast
from ..sparql import SparqlError, named_graph, run_sparql
from ._shared import _to_uri

#: Separator for GROUP_CONCAT-ed factor lists. spoke-genelab factor values are
#: short strings (e.g. "WildType", "Day 30", "Hardware 1G Ground Control") and
#: never contain a pipe, so it round-trips cleanly.
_SEP = "|"

_GRAPH = named_graph("spoke-genelab")
_SCHEMA_NS = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"

_RULE = (
    "Clean contrast = Space Flight (arm 1) vs Ground Control (arm 2) AND the two "
    "arms match on every covariate (genotype, sex, dose, time point, hardware) "
    "AND material_id_1 = material_id_2. log2fc/lnfc/methylation_diff > 0 means UP "
    "in spaceflight."
)


def _split_factors(value: str | None) -> list[str]:
    """Split a GROUP_CONCAT-ed factor string into a de-duplicated ordered list."""
    if not value:
        return []
    seen: dict[str, None] = {}
    for part in value.split(_SEP):
        p = part.strip()
        if p:
            seen.setdefault(p, None)
    return list(seen)


def _build_query(tissue_uri: str | None) -> str:
    """Canonical Space-Flight-vs-Ground-Control assay query (Rule 1 pinned)."""
    tissue_pattern = (
        f"    ?assay schema:INVESTIGATED_ASiA <{tissue_uri}> .\n" if tissue_uri else ""
    )
    return f"""\
PREFIX schema: <{_SCHEMA_NS}>
SELECT ?assay
       (SAMPLE(?m1) AS ?material_id_1)
       (SAMPLE(?m2) AS ?material_id_2)
       (SAMPLE(?meas) AS ?measurement)
       (SAMPLE(?tech) AS ?technology)
       (GROUP_CONCAT(DISTINCT STR(?tissue); SEPARATOR="{_SEP}") AS ?tissues)
       (GROUP_CONCAT(DISTINCT ?f1; SEPARATOR="{_SEP}") AS ?factors_1)
       (GROUP_CONCAT(DISTINCT ?f2; SEPARATOR="{_SEP}") AS ?factors_2)
WHERE {{
  GRAPH <{_GRAPH}> {{
    ?assay schema:factor_space_1 "Space Flight" ;
           schema:factor_space_2 "Ground Control" .
{tissue_pattern}    OPTIONAL {{ ?assay schema:material_id_1 ?m1 }}
    OPTIONAL {{ ?assay schema:material_id_2 ?m2 }}
    OPTIONAL {{ ?assay schema:measurement ?meas }}
    OPTIONAL {{ ?assay schema:technology ?tech }}
    OPTIONAL {{ ?assay schema:factors_1 ?f1 }}
    OPTIONAL {{ ?assay schema:factors_2 ?f2 }}
    OPTIONAL {{ ?assay schema:INVESTIGATED_ASiA ?tissue }}
  }}
}}
GROUP BY ?assay
ORDER BY ?assay"""


@mcp.tool()
async def get_valid_contrasts(
    tissue: str | None = None,
    include_confounded: bool = False,
) -> dict[str, Any]:
    """Return VETTED spaceflight differential-expression contrasts for spoke-genelab.

    USE THIS before reading any spoke-genelab differential value (expression,
    methylation, abundance) as a "spaceflight effect". It resolves a request like
    "spaceflight DEGs in bone marrow" to a list of assays that already pass the
    two contrast rules, so you never hand-write the comparability self-join (the
    step LLMs skip, which lets a confounded assay slip through).

    The server computes, per assay:
      - Rule 1 (direction): kept only when factor_space_1 = "Space Flight" and
        factor_space_2 = "Ground Control". With this orientation group 1 = Space
        Flight, group 2 = Ground Control, so log2fc/lnfc/methylation_diff > 0
        means UP in spaceflight.
      - Rule 2 (within-assay comparability): `is_clean_contrast` is True only when
        the flight arm (factors_1) and ground arm (factors_2) carry the SAME
        covariates after the condition labels/codes are stripped, AND
        material_id_1 = material_id_2. A WildType-flight-vs-knockout-ground assay
        (or one differing in sex/dose/time point/hardware) is `is_clean_contrast`
        False with a `confound_reason` — its differential values reflect that
        covariate, not spaceflight. Do NOT read those as a spaceflight effect.

    Then read differential expression for the returned `assay` IRIs via the
    reified relationship, e.g.::

        ?stmt rdf:subject ?assay ;
              rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
              rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?p .

    Args:
        tissue: Optional UBERON tissue to scope to (IRI or CURIE, e.g.
            `UBERON:0002371` or the full purl), matched on `INVESTIGATED_ASiA`.
        include_confounded: False (default) returns only clean contrasts plus a
            `confounded_count` of those excluded. True returns every Space-Flight-
            vs-Ground-Control assay, each carrying `is_clean_contrast` and
            `confound_reason` so confounded ones are visible for inspection.

    Returns:
        `{"shortname", "tissue", "rule", "clean_count", "confounded_count",
        "contrasts": [{assay, material_id_1, material_id_2, measurement,
        technology, tissues, factors_1, factors_2, flight_covariates,
        control_covariates, is_clean_contrast, confound_reason, contrast_label}]}`.
        Contrasts are ordered clean-first. On endpoint failure: `{"error": ...}`.
    """
    tissue_uri = _to_uri(tissue) if tissue else None
    query = _build_query(tissue_uri)
    try:
        result = await run_sparql(query, fmt="json")
    except SparqlError as exc:
        return {"error": str(exc)}

    contrasts: list[dict[str, Any]] = []
    for row in result.get("rows", []):
        assay = row.get("assay")
        if not assay:
            continue
        factors_1 = _split_factors(row.get("factors_1"))
        factors_2 = _split_factors(row.get("factors_2"))
        verdict = classify_contrast(
            {
                "factors_1": factors_1,
                "factors_2": factors_2,
                "material_id_1": row.get("material_id_1"),
                "material_id_2": row.get("material_id_2"),
            }
        )
        contrasts.append(
            {
                "assay": assay,
                "material_id_1": row.get("material_id_1"),
                "material_id_2": row.get("material_id_2"),
                "measurement": row.get("measurement"),
                "technology": row.get("technology"),
                "tissues": _split_factors(row.get("tissues")),
                "factors_1": factors_1,
                "factors_2": factors_2,
                **verdict,
            }
        )

    clean = [c for c in contrasts if c["is_clean_contrast"]]
    confounded = [c for c in contrasts if not c["is_clean_contrast"]]
    shown = clean if not include_confounded else clean + confounded

    out: dict[str, Any] = {
        "shortname": "spoke-genelab",
        "tissue": tissue_uri,
        "rule": _RULE,
        "clean_count": len(clean),
        "confounded_count": len(confounded),
        "contrasts": shown,
    }
    if not include_confounded and confounded:
        out["note"] = (
            f"{len(confounded)} confounded assay(s) excluded (arms differ in a "
            "covariate or material). Call with include_confounded=True to inspect "
            "them with their confound_reason."
        )
    return out

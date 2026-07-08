"""Domain rules for comparing ``spoke-genelab`` (NASA GeneLab) assays.

``spoke-genelab`` models each differential measurement as an ``Assay`` with two
arms: ``factor_space_1`` vs ``factor_space_2`` (the experimental-condition
labels) and ``factors_1`` vs ``factors_2`` (lists that bundle the condition
label *plus* extra factors — dose, time, sex, strain, genotype…). Reading any
assay as a "spaceflight effect" is wrong on two counts:

* DIRECTION (Rule 1): most assays are not Space-Flight-vs-Ground-Control at all.
* COMPARABILITY (Rule 2): even a Space-Flight-vs-Ground-Control assay is only a
  clean contrast when its two arms differ *only* in the condition. The critical,
  easily-missed case is the **within-assay** confound — the flight arm and the
  ground arm carry different covariates (e.g. ``factors_1`` has WildType while
  ``factors_2`` has Nrf2KO). Any differential value from such an assay reflects
  that covariate, not spaceflight. This is orthogonal to the assay-to-assay
  comparison (whether two separate assays may be pooled), which is the secondary
  facet of Rule 2.

:func:`strip_condition_factors` and :func:`classify_contrast` implement the test
deterministically; the ``get_valid_contrasts`` tool (see
:mod:`mcp_okn.tools.contrasts_tools`) uses them to hand back a vetted contrast
list so a client never has to hand-write the self-join. These constants are the
single source of truth for the rule prose. They are interpolated into the server
``INSTRUCTIONS`` (see :mod:`mcp_okn.app`) and surfaced as ``usage_notes`` on
``get_schema("spoke-genelab")`` (see :mod:`mcp_okn.schema`) so a client gets them
exactly when writing SPARQL for this KG. This module is a leaf — it imports
nothing from the package, so both ``app`` and ``schema`` can import it without a
cycle.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

#: The experimental-condition labels that appear in ``factor_space_1`` /
#: ``factor_space_2`` and inside the ``factors_1`` / ``factors_2`` lists. They
#: must be removed from the factor lists before two assays are compared (so an
#: assay is not deemed different merely because one arm literally carries
#: "Space Flight" and the other "Ground Control"). Matched case-insensitively
#: (the data also stores "Ground control" / "Vivarium control"). "Cell Culture
#: Control" is the in-vitro counterpart of the same condition axis and appears
#: alongside the coded studies below, so it is stripped too.
SPOKE_GENELAB_CONDITION_LABELS = (
    "Space Flight",
    "Ground Control",
    "Basal Control",
    "Vivarium Control",
    "Cell Culture Control",
)

#: Some studies encode the same conditions as short GROUP CODES in the factor
#: lists instead of (or in addition to) the spelled-out labels, with an optional
#: ``_C<n>`` cohort suffix: GC (Ground Control), FLT (Space Flight / Flight), VIV
#: (Vivarium Control), BSL (Basal Control), CC (Cell Culture Control) — e.g.
#: ``GC``, ``FLT_C1``, ``VIV_C2``, ``BSL_C1``, ``CC_C2``. This pattern is ANCHORED
#: so it strips only these exact code families and never real experimental
#: conditions that merely contain a control word (e.g. "Hardware 1G Ground
#: Control", "HLU_IR" hindlimb-unloading + irradiation, "Euth_C_DI" processing
#: codes), which stay in the factor lists as legitimate distinguishing factors.
SPOKE_GENELAB_CONDITION_CODE_REGEX = "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"

# Precompiled for the classification helpers below. The labels are matched
# case-insensitively; the codes with the anchored pattern above.
_CONDITION_LABELS_LOWER = frozenset(s.lower() for s in SPOKE_GENELAB_CONDITION_LABELS)
_CONDITION_CODE_RE = re.compile(SPOKE_GENELAB_CONDITION_CODE_REGEX)


def strip_condition_factors(factors: Iterable[str]) -> set[str]:
    """Drop experimental-condition labels/codes from a factor list.

    Removes any factor whose value is one of the spelled-out condition labels
    (case-insensitively, e.g. "Space Flight", "Ground Control") or matches the
    anchored short-code pattern (``GC``, ``FLT_C1``, …). What remains is the set
    of *covariates* (dose, time point, sex, strain, hardware) that must match
    between an assay's two arms for a clean spaceflight contrast. Real factors
    that merely contain a control word ("Hardware 1G Ground Control", "HLU_IR")
    are kept. This is the single implementation shared by the tool and tests.
    """
    kept: set[str] = set()
    for raw in factors:
        f = (raw or "").strip()
        if not f:
            continue
        if f.lower() in _CONDITION_LABELS_LOWER or _CONDITION_CODE_RE.match(f):
            continue
        kept.add(f)
    return kept


def classify_contrast(row: dict[str, Any]) -> dict[str, Any]:
    """Classify one Space-Flight-vs-Ground-Control assay as clean or confounded.

    ``row`` must supply ``factors_1``/``factors_2`` (each an iterable of factor
    strings) and optionally ``material_id_1``/``material_id_2``. A contrast is
    clean only when, after stripping the condition labels/codes, the flight-arm
    and ground-arm covariate SETS are equal AND the two material ids match (when
    both are present). Genotype/sex/dose/timepoint/hardware differing between the
    arms — e.g. flight=WildType vs control=Nrf2KO — makes the assay confounded:
    any differential expression it reports is attributable to that covariate, not
    to spaceflight.

    Returns ``flight_covariates``/``control_covariates`` (sorted lists),
    ``is_clean_contrast`` (bool), ``confound_reason`` (str or None), and a human
    ``contrast_label``.
    """
    flight = strip_condition_factors(row.get("factors_1") or [])
    control = strip_condition_factors(row.get("factors_2") or [])
    m1 = (row.get("material_id_1") or "").strip()
    m2 = (row.get("material_id_2") or "").strip()

    covariates_match = flight == control
    materials_differ = bool(m1) and bool(m2) and m1 != m2

    reasons: list[str] = []
    if not covariates_match:
        reasons.append(
            f"covariates differ: flight={sorted(flight) or ['(none)']}, "
            f"control={sorted(control) or ['(none)']}"
        )
    if materials_differ:
        reasons.append(f"materials differ: {m1} != {m2}")

    is_clean = covariates_match and not materials_differ

    if is_clean:
        shared = ", ".join(sorted(flight)) if flight else "baseline"
        label = f"{shared}: Space Flight vs Ground Control"
    else:
        fl = ", ".join(sorted(flight)) or "(none)"
        ct = ", ".join(sorted(control)) or "(none)"
        label = f"Space Flight [{fl}] vs Ground Control [{ct}] — CONFOUNDED"

    return {
        "flight_covariates": sorted(flight),
        "control_covariates": sorted(control),
        "is_clean_contrast": is_clean,
        "confound_reason": "; ".join(reasons) if reasons else None,
        "contrast_label": label,
    }


SPOKE_GENELAB_CONTRAST_GUIDANCE = """\
Comparing spoke-genelab assays — TWO rules (apply BOTH before reading any
differential expression / methylation / abundance value as a spaceflight effect):

1. DIRECTION — Space Flight vs Ground Control ONLY. Keep an assay only when
   `factor_space_1 = "Space Flight"` AND `factor_space_2 = "Ground Control"`.
   DROP the reverse (`factor_space_1 = "Ground Control"`, `factor_space_2 =
   "Space Flight"`) and every other pairing (Space-Flight-vs-Space-Flight,
   Ground-vs-Ground, and anything involving "Basal Control" or "Vivarium
   Control"). Direction matters for sign: with this orientation group 1 = Space
   Flight and group 2 = Ground Control, so log2fc/methylation_diff/lnfc > 0 means
   UP in spaceflight relative to ground.

2. COMPARABILITY — the two ARMS of an assay must match on everything but the
   condition. PRIMARY (within-assay, easy to miss): a single assay is a clean
   spaceflight contrast only if its flight arm (`factors_1`) and ground arm
   (`factors_2`) carry the SAME covariates once the condition labels/codes are
   removed, AND `material_id_1 = material_id_2`. If the flight arm is WildType and
   the ground arm is a knockout (or they differ in sex, dose, time point, or
   hardware), the assay is CONFOUNDED — its differential values reflect that
   covariate, not spaceflight — so drop it. Do NOT collapse `factors_1` into "the
   genotype"; the comparator lives in `factors_2` and the two are separate axes.
   SECONDARY (assay-to-assay): two separate clean assays may be pooled/compared
   only if they share the SAME materials AND the SAME stripped covariate sets.
   In both cases strip first: remove the spelled-out labels ("Space Flight",
   "Ground Control", "Basal Control", "Vivarium Control", "Cell Culture Control")
   case-insensitively, and the short GROUP CODES — GC (Ground Control), FLT
   (Space Flight), VIV (Vivarium), BSL (Basal), CC (Cell Culture Control), with an
   optional "_C<n>" cohort suffix (e.g. GC_C2, FLT_C1, VIV_C2) — with the anchored
   pattern ^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$ so you DO NOT strip real factors that
   merely contain a control word (e.g. "Hardware 1G Ground Control", "HLU_IR").
   Then test the remaining factors for set equality — a shared extra factor is
   allowed as long as it is present on BOTH arms. Prefer calling
   `get_valid_contrasts(kg="spoke-genelab", tissue=…)`, which returns only the
   assays that pass these rules (each flagged `is_clean_contrast`), instead of
   hand-writing the test below."""

SPOKE_GENELAB_CONTRAST_SNIPPET = """\
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# Clean single-assay Space-Flight-vs-Ground-Control contrast filter for spoke-genelab.
# PREFER the get_valid_contrasts tool, which returns these assays already vetted and
# flagged (is_clean_contrast). This query is the equivalent test, spelled out:
#  - Rule 1 (direction): keep ONLY Space Flight (arm 1) vs Ground Control (arm 2);
#    the reverse and every Basal/Vivarium pairing are excluded by pinning both
#    factor_space values. So log2fc/methylation_diff/lnfc > 0 means UP in flight.
#  - Rule 2 (WITHIN-assay comparability): the flight arm and the ground arm must
#    carry the SAME covariates. Keep an assay only if material_id_1 = material_id_2
#    AND, after stripping the condition labels/codes, factors_1 and factors_2 hold
#    the SAME set — i.e. NEITHER arm has a covariate the other lacks. This is what
#    catches a WildType-flight-vs-knockout-ground assay (its factors_1/factors_2
#    covariate sets differ), which naive filters miss. Strip BEFORE comparing:
#      labels (case-insensitive): Space/Ground/Basal/Vivarium/Cell-Culture Control
#      codes (anchored): ^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$  e.g. GC, FLT_C1, VIV_C2
#    The anchored code pattern keeps real factors like "Hardware 1G Ground Control"
#    or "HLU_IR" (hindlimb-unloading) in the list.
SELECT DISTINCT ?assay ?material_id_1 ?material_id_2 WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay schema:factor_space_1 "Space Flight" ;       # direction: SF arm
           schema:factor_space_2 "Ground Control" ;     # direction: GC arm (not reversed)
           schema:material_id_1 ?material_id_1 ;
           schema:material_id_2 ?material_id_2 .
    FILTER(?material_id_1 = ?material_id_2)              # same biological material
    # no covariate in the flight arm that the ground arm lacks ...
    FILTER NOT EXISTS {
      ?assay schema:factors_1 ?x .
      FILTER(LCASE(STR(?x)) NOT IN
          ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay schema:factors_2 ?x }
    }
    # ... and none in the ground arm that the flight arm lacks (symmetric).
    FILTER NOT EXISTS {
      ?assay schema:factors_2 ?y .
      FILTER(LCASE(STR(?y)) NOT IN
          ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?y), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      FILTER NOT EXISTS { ?assay schema:factors_1 ?y }
    }
  }
}
# Then read differential expression for these ?assay via the reified relationship:
#   ?stmt rdf:subject ?assay ; rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG ;
#         rdf:object ?gene ; schema:log2fc ?lfc ; schema:adj_p_value ?p .
# For pooling TWO separate clean assays ?a and ?b, additionally require their
# material ids equal and run the same symmetric NOT EXISTS across ?a/?b factors."""

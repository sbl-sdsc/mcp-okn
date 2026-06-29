"""Domain rules for comparing ``spoke-genelab`` (NASA GeneLab) assays.

``spoke-genelab`` models each differential measurement as an ``Assay`` with two
arms: ``factor_space_1`` vs ``factor_space_2`` (the experimental-condition
labels) and ``factors_1`` vs ``factors_2`` (lists that bundle the condition
label *plus* extra factors — dose, time, sex, strain…). Reading any assay as a
"spaceflight effect" is wrong: most assays are not a clean Space-Flight-vs-
Ground-Control contrast, and two assays are only legitimately comparable when
their materials and non-condition factors match.

These constants are the single source of truth for the two rules. They are
interpolated into the server ``INSTRUCTIONS`` (see :mod:`mcp_okn.app`) and
surfaced as ``usage_notes`` on ``get_schema("spoke-genelab")`` (see
:mod:`mcp_okn.schema`) so a client gets them exactly when writing SPARQL for
this KG. This module is a leaf — it imports nothing from the package, so both
``app`` and ``schema`` can import it without a cycle.
"""

from __future__ import annotations

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

2. COMPARABILITY — two assays must match on materials AND non-condition factors.
   When comparing two separate Assay records, they are comparable only if they
   share the SAME materials (prefer `material_id_1`/`material_id_2`) AND the SAME
   `factors_1`/`factors_2` lists AFTER the experimental-condition labels
   ("Space Flight", "Ground Control", "Basal Control", "Vivarium Control",
   "Cell Culture Control") have been REMOVED from those lists. Some studies encode
   these conditions as short GROUP CODES instead — GC (Ground Control), FLT
   (Space Flight), VIV (Vivarium), BSL (Basal), CC (Cell Culture Control), with an
   optional "_C<n>" cohort suffix (e.g. GC_C2, FLT_C1, VIV_C2) — and those must be
   stripped too. Match the spelled-out labels case-insensitively and the codes
   with the anchored pattern ^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$ so you DO NOT strip
   real factors that merely contain a control word (e.g. "Hardware 1G Ground
   Control", "HLU_IR"). Strip the condition labels/codes first, then test the
   remaining factors for equality — a shared extra factor (dose, time point, sex,
   strain) is allowed as long as it is present on BOTH sides. This replaces the
   older strict filter that required `factors_1` to contain only "Space Flight"
   (which wrongly rejected assays carrying a legitimate shared factor)."""

SPOKE_GENELAB_CONTRAST_SNIPPET = """\
PREFIX schema: <https://purl.org/okn/frink/kg/spoke-genelab/schema/>
# Per-assay comparability signature for spoke-genelab.
#  - Rule 1 (direction): keep ONLY Space Flight vs Ground Control; the reverse and
#    every Basal/Vivarium pairing are excluded by pinning the two factor_space values.
#  - Rule 2 (comparability): two assays are comparable iff they agree on
#    (material_id_1, material_id_2, sig1, sig2), where sigN is factors_N with the
#    experimental-condition labels AND short group codes removed. Strip BEFORE comparing:
#      labels (case-insensitive): Space/Ground/Basal/Vivarium/Cell-Culture Control
#      codes (anchored): ^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$  e.g. GC, FLT_C1, VIV_C2
#    The anchored code pattern keeps real factors like "Hardware 1G Ground Control"
#    or "HLU_IR" (hindlimb-unloading) in the list.
SELECT ?assay ?material_id_1 ?material_id_2
       (GROUP_CONCAT(DISTINCT ?f1clean; SEPARATOR="|") AS ?sig1)
       (GROUP_CONCAT(DISTINCT ?f2clean; SEPARATOR="|") AS ?sig2) WHERE {
  GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> {
    ?assay schema:factor_space_1 "Space Flight" ;       # direction: SF arm
           schema:factor_space_2 "Ground Control" ;     # direction: GC arm (not reversed)
           schema:material_id_1 ?material_id_1 ;
           schema:material_id_2 ?material_id_2 .
    OPTIONAL {
      ?assay schema:factors_1 ?f1 .
      FILTER(LCASE(STR(?f1)) NOT IN
          ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f1), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      BIND(?f1 AS ?f1clean)
    }
    OPTIONAL {
      ?assay schema:factors_2 ?f2 .
      FILTER(LCASE(STR(?f2)) NOT IN
          ("space flight","ground control","basal control","vivarium control","cell culture control")
        && !REGEX(STR(?f2), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
      BIND(?f2 AS ?f2clean)
    }
  }
} GROUP BY ?assay ?material_id_1 ?material_id_2
# The GROUP_CONCAT signature is a lightweight heuristic (order-sensitive). For a
# robust set comparison of two assays ?a and ?b, require their materials equal and
# test each direction with NOT EXISTS, applying the SAME label+code strip filter,
# e.g.:
#   FILTER NOT EXISTS { ?a schema:factors_1 ?x .
#     FILTER(LCASE(STR(?x)) NOT IN
#         ("space flight","ground control","basal control","vivarium control","cell culture control")
#       && !REGEX(STR(?x), "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$"))
#     FILTER NOT EXISTS { ?b schema:factors_1 ?x } }
# (and the symmetric ?b-into-?a check, plus the same for factors_2)."""

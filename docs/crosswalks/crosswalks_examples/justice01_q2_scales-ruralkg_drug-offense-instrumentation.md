# justice01_q2_scales-ruralkg — federal drug prosecutions aligned to RuralKG's crime-reporting variables

- **Date:** 2026-07-01
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql

## Knowledge graphs used
- `scales` — <https://purl.org/okn/frink/kg/scales>
- `ruralkg` — <https://purl.org/okn/frink/kg/ruralkg>

## Conversation
👤 **User**
Drug enforcement is a large share of the federal docket. Using the NIBRS offense vocabulary shared by SCALES (`fbi:OffenseUCRCode` on charges) and RuralKG (`variable/answerContent` on NIBRS answer nodes), how many federal charges does SCALES record for the two drug offense categories, and which RuralKG rural crime-reporting **variables** instrument those same categories (with an example)?

---
🧠 **Assistant**
I restrict the shared offense key to the two NIBRS drug categories, count SCALES federal charges for each, and follow RuralKG's `hasAnswer` link from the matching answer node up to its parent codebook **variable** (`generatedDescription` gives a human-readable variable summary). The join is on the offense name bound as the same literal variable across both graphs.

| NIBRS offense | NIBRS code | Federal charges (SCALES) | RuralKG variables | Example RuralKG variable |
| --- | --- | --- | --- | --- |
| Drug/Narcotic Violations | 351 | 86,454 | 5 | *UCR ARREST OFFENSE CODE - 1 … identifies the primary offense for which an arrest was made* |
| Drug Equipment Violations | 352 | 10,536 | 5 | *UCR ARREST OFFENSE CODE … a categorical variable that identifies specific offenses associated with arrests* |

The two graphs meet cleanly on the NIBRS drug codes (351 = Drug/Narcotic Violations, 352 = Drug Equipment Violations). SCALES supplies the federal *volume* — 86,454 narcotic-violation charges and 10,536 drug-equipment charges — while RuralKG supplies the *instrumentation*: each drug category is a response value in 5 rural crime-reporting codebook variables, headed by the NIBRS "UCR ARREST OFFENSE CODE" family that records the primary arrest offense. The crosswalk lets an analyst place federal drug-charge counts alongside the rural arrest-reporting variables that capture the same offense taxonomy — a categorical, offense-type alignment (not a case-level link), complementary to the county-FIPS geography on which SCALES already joins the spatial graphs.

## SPARQL queries executed
#### Query 1
_`scales`, `ruralkg` · 2 rows_
```sparql
PREFIX fbi: <http://fbi.gov/cjis/nibrs/2023.0/>
PREFIX rk: <http://sail.ua.edu/ruralkg/variable/>
SELECT ?offense ?nibrsCode ?federalCharges
       (COUNT(DISTINCT ?parent) AS ?ruralkgVariables)
       (SAMPLE(?desc) AS ?exampleVariable) WHERE {
  VALUES ?offense { "Drug/Narcotic Violations" "Drug Equipment Violations" }
  {
    SELECT ?offense (COUNT(?charge) AS ?federalCharges) WHERE {
      GRAPH <https://purl.org/okn/frink/kg/scales> {
        ?charge fbi:OffenseUCRCode ?offense .
      }
    } GROUP BY ?offense
  }
  GRAPH <https://purl.org/okn/frink/kg/ruralkg> {
    ?ans rk:answerContent ?offense ; rk:answerCode ?nibrsCode .
    ?parent rk:hasAnswer ?ans .
    OPTIONAL { ?parent rk:generatedDescription ?desc }
  }
} GROUP BY ?offense ?nibrsCode ?federalCharges ORDER BY DESC(?federalCharges)
```
| NIBRS offense | NIBRS code | Federal charges | RuralKG variables | Example RuralKG variable |
| --- | --- | --- | --- | --- |
| Drug/Narcotic Violations | 351 | 86454 | 5 | UCR ARREST OFFENSE CODE - 1 is a variable that identifies the primary offense for which an arrest was made, aiding in comprehensive crime data analysis and reporting. |
| Drug Equipment Violations | 352 | 10536 | 5 | UCR ARREST OFFENSE CODE is a categorical variable that identifies specific offenses associated with arrests, aiding in standardized crime reporting and analysis. |

**Crosswalk:** `CJ1-nibrs-offense-scales-ruralkg` — shared key: FBI NIBRS offense-category name. Controlled-vocabulary join; no bridge graph.

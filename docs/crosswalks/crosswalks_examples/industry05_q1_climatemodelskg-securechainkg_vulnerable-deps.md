# I5-Q1 — Climate models ranked by software vulnerabilities (climatemodelskg × securechainkg)

- **Date:** 2026-06-29
- **Model:** claude-opus-4-8
- **SPARQL endpoint:** https://apps.okn.us/federation/sparql
- **Crosswalk:** climatemodelskg ↔ securechainkg (verified, P1-climate-deps; 3 climate models with dependency edges)
- **Shared identifier:** climate-model Source IRI (`https://climatepub4kg.github.io/id/Source/{model}`), reused by securechainkg as the subject of `sc:dependsOn`

## Knowledge graphs used

- `climatemodelskg` — <https://purl.org/okn/frink/kg/climatemodelskg>
- `securechainkg` — <https://purl.org/okn/frink/kg/securechainkg>

## Conversation

👤 **User**

Which climate models have the most vulnerable dependencies and the highest number of vulnerabilities?

---

🧠 **Assistant**

Three climate-model Sources in climatemodelskg are wired into securechainkg's software-supply-chain graph: securechainkg reuses each model's verbatim Source IRI (e.g. `…/id/Source/CESM2`) as the subject of `sc:dependsOn` edges into its PyPI packages, and each package version links to its CVEs via `sc:vulnerableTo`. Joining on that shared IRI and counting distinct dependencies and distinct CVEs per model, **CESM2** leads by a wide margin — 18 dependencies and 35 distinct vulnerabilities — followed by **GFDL-ESM4** (3 deps, 14 CVEs) and **GFDL-CM4** (2 deps, 11 CVEs). The dependencies are the scientific-Python stack (numpy, lxml, torch, scipy, setuptools, ujson, …), so the CVEs are inherited supply-chain risk rather than flaws in the climate code itself.

#### Query — Climate models by dependency count and distinct vulnerability count

```sparql
PREFIX cp: <https://climatepub4kg.github.io/ontology#>
PREFIX cpsource: <https://climatepub4kg.github.io/id/Source/>
PREFIX sc: <https://w3id.org/secure-chain/>
SELECT ?model ?modelName (COUNT(DISTINCT ?dep) AS ?depCount) (COUNT(DISTINCT ?v) AS ?vulnCount)
FROM <https://purl.org/okn/frink/kg/securechainkg>
FROM <https://purl.org/okn/frink/kg/climatemodelskg>
WHERE {
  ?model a cp:Source ;
         cp:name ?modelName .
  ?model sc:dependsOn ?dep .
  OPTIONAL {
    ?dep sc:hasSoftwareVersion ?ver .
    ?ver sc:vulnerableTo ?v .
  }
}
GROUP BY ?model ?modelName
ORDER BY DESC(?vulnCount)
```

_3 row(s) returned_

| model | modelName | depCount | vulnCount |
| --- | --- | --- | --- |
| https://climatepub4kg.github.io/id/Source/CESM2 | CESM2 | 18 | 35 |
| https://climatepub4kg.github.io/id/Source/GFDL-ESM4 | GFDL-ESM4 | 3 | 14 |
| https://climatepub4kg.github.io/id/Source/GFDL-CM4 | GFDL-CM4 | 2 | 11 |

## Validation

Validated by construction on the verified `climatemodelskg ↔ securechainkg` crosswalk (P1-climate-deps): the join key is the climate-model Source IRI, which securechainkg reuses verbatim as the subject of `sc:dependsOn`, so no rewrite is needed. The `FROM … FROM …` clauses merge both named graphs into the default graph for the cross-graph join. Counts are distinct dependencies and distinct CVEs (`https://nvd.nist.gov/vuln/detail/CVE-…`) per model, reproducible at COUNT(DISTINCT ?model)=3. Software-supply-chain integration; not a biomedical claim.

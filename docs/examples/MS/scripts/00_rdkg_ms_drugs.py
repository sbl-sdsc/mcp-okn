"""STEP 0 — materialise the rdkg × ubergraph MS-drug federated query result (93 rows).

Query (run via mcp-okn sparql_query, non-exploratory, no scope argument):

    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX biolink: <https://w3id.org/biolink/vocab/>
    SELECT DISTINCT ?mondo ?mondoLabel ?rel ?drug ?drugLabel ?drugPref ?drugCat ?drugId WHERE {
      GRAPH <https://purl.org/okn/frink/kg/ubergraph> {
        ?mondo rdfs:subClassOf* <http://purl.obolibrary.org/obo/MONDO_0005301> . }
      GRAPH <https://purl.org/okn/frink/kg/rdkg> {
        { ?drug biolink:treats ?mondo . BIND("treats" AS ?rel) }
        UNION { ?drug biolink:contraindicated_for ?mondo . BIND("contraindicated_for" AS ?rel) }
        UNION { ?mondo biolink:associated_with ?drug . BIND("associated_with_treatment" AS ?rel) }
        UNION { ?mondo biolink:prevented_by ?drug . BIND("prevented_by" AS ?rel) }
        OPTIONAL { ?drug rdfs:label ?drugLabel } OPTIONAL { ?drug skos:prefLabel ?drugPref }
        OPTIONAL { ?drug biolink:category ?drugCat } OPTIONAL { ?drug biolink:id ?drugId }
        OPTIONAL { ?mondo rdfs:label ?mondoLabel } } }

Returned 93 rows; every row had drugPref == drugLabel and drugCat == "biolink:Drug", and only the
`treats` / `contraindicated_for` arms matched (no associated_with / prevented_by rows).
Writes data/rdkg_ms_drugs.json and data/rdkg_ms_drugs.csv.
"""
import csv
import json
import os

WD = "/sessions/vibrant-kind-heisenberg/mnt/outputs/ms_work"
MLAB = {
    "MONDO_0000452": "progressive relapsing multiple sclerosis",
    "MONDO_0005301": "multiple sclerosis",
    "MONDO_0005314": "relapsing-remitting multiple sclerosis",
    "MONDO_0018784": "pediatric multiple sclerosis",
}

# (mondo, rel, drugLabel, drugId) as returned by the endpoint
R = [
    ("MONDO_0000452", "treats", "Rituximab", "DrugBank:DB00073"),
    ("MONDO_0000452", "treats", "Biotin", "DrugBank:DB00121"),
    ("MONDO_0000452", "treats", "Liothyronine", "DrugBank:DB00279"),
    ("MONDO_0000452", "treats", "Cyclophosphamide", "DrugBank:DB00531"),
    ("MONDO_0000452", "treats", "Teriflunomide", "DrugBank:DB08880"),
    ("MONDO_0000452", "treats", "Acth", "CTDRUG:acth"),
    ("MONDO_0000452", "treats", "Biib041 (fampridine)", "CTDRUG:biib041_fampridine_"),
    ("MONDO_0000452", "treats", "Cc-97540", "CTDRUG:cc_97540"),
    ("MONDO_0000452", "treats", "Clemastine Fumarate", "CTDRUG:clemastine_fumarate"),
    ("MONDO_0000452", "treats", "Diroximel Fumarate", "CTDRUG:diroximel_fumarate"),
    ("MONDO_0000452", "treats", "Disease-modifying Therapies", "CTDRUG:disease_modifying_therapies"),
    ("MONDO_0000452", "treats", "Elnd002", "CTDRUG:elnd002"),
    ("MONDO_0000452", "treats", "Extended-release Quetiapine Fumarate", "CTDRUG:extended_release_quetiapine_fumarate"),
    ("MONDO_0000452", "treats", "Fludarabine", "CTDRUG:fludarabine"),
    ("MONDO_0000452", "treats", "Glatiramer Acetate", "CTDRUG:glatiramer_acetate"),
    ("MONDO_0000452", "treats", "Insulin", "CTDRUG:insulin"),
    ("MONDO_0000452", "treats", "Interferon Beta-1b (betaseron, Bay86-5046)", "CTDRUG:interferon_beta_1b_betaseron_bay86_5046_"),
    ("MONDO_0000452", "treats", "Nbi-5788", "CTDRUG:nbi_5788"),
    ("MONDO_0000452", "treats", "Ocrelizumab Dose 1", "CTDRUG:ocrelizumab_dose_1"),
    ("MONDO_0000452", "treats", "Ocrelizumab Dose 2 And Dose 3", "CTDRUG:ocrelizumab_dose_2_and_dose_3"),
    ("MONDO_0000452", "treats", "Remibrutinib", "CTDRUG:remibrutinib"),
    ("MONDO_0000452", "treats", "Tolebrutinib", "CTDRUG:tolebrutinib"),
    ("MONDO_0005301", "contraindicated_for", "Ascorbic acid", "DrugBank:DB00126"),
    ("MONDO_0005301", "contraindicated_for", "Zinc gluconate", "DrugBank:DB11248"),
    ("MONDO_0005301", "treats", "Natalizumab", "DrugBank:DB00108"),
    ("MONDO_0005301", "treats", "Betamethasone", "DrugBank:DB00443"),
    ("MONDO_0005301", "treats", "Triamcinolone", "DrugBank:DB00620"),
    ("MONDO_0005301", "treats", "Prednisone", "DrugBank:DB00635"),
    ("MONDO_0005301", "treats", "Hydrocortisone", "DrugBank:DB00741"),
    ("MONDO_0005301", "treats", "Prednisolone", "DrugBank:DB00860"),
    ("MONDO_0005301", "treats", "Methylprednisolone", "DrugBank:DB00959"),
    ("MONDO_0005301", "treats", "Dexamethasone", "DrugBank:DB01234"),
    ("MONDO_0005301", "treats", "Cortisone acetate", "DrugBank:DB01380"),
    ("MONDO_0005301", "treats", "Dalfampridine", "DrugBank:DB06637"),
    ("MONDO_0005301", "treats", "Teriflunomide", "DrugBank:DB08880"),
    ("MONDO_0005301", "treats", "Ozanimod", "DrugBank:DB12612"),
    ("MONDO_0005301", "treats", "Hydrocortisone acetate", "DrugBank:DB14539"),
    ("MONDO_0005314", "treats", "Interferon beta-1a", "DrugBank:DB00060"),
    ("MONDO_0005314", "treats", "Interferon beta-1b", "DrugBank:DB00068"),
    ("MONDO_0005314", "treats", "Alemtuzumab", "DrugBank:DB00087"),
    ("MONDO_0005314", "treats", "Daclizumab", "DrugBank:DB00111"),
    ("MONDO_0005314", "treats", "Cladribine", "DrugBank:DB00242"),
    ("MONDO_0005314", "treats", "Clemastine", "DrugBank:DB00283"),
    ("MONDO_0005314", "treats", "Methylprednisolone", "DrugBank:DB00959"),
    ("MONDO_0005314", "treats", "Mitoxantrone", "DrugBank:DB01204"),
    ("MONDO_0005314", "treats", "Ofatumumab", "DrugBank:DB06650"),
    ("MONDO_0005314", "treats", "Raltegravir", "DrugBank:DB06817"),
    ("MONDO_0005314", "treats", "Fingolimod", "DrugBank:DB08868"),
    ("MONDO_0005314", "treats", "Belimumab", "DrugBank:DB08879"),
    ("MONDO_0005314", "treats", "Dimethyl fumarate", "DrugBank:DB08908"),
    ("MONDO_0005314", "treats", "Peginterferon beta-1a", "DrugBank:DB09122"),
    ("MONDO_0005314", "treats", "Bg00012", "CTDRUG:bg00012"),
    ("MONDO_0005314", "treats", "Continued Ocrelizumab", "CTDRUG:continued_ocrelizumab"),
    ("MONDO_0005314", "treats", "Copaxone®", "CTDRUG:copaxone_"),
    ("MONDO_0005314", "treats", "Dietary Supplement: Vitamin A", "CTDRUG:dietary_supplement_vitamin_a"),
    ("MONDO_0005314", "treats", "Glatiramer Acetate", "CTDRUG:glatiramer_acetate"),
    ("MONDO_0005314", "treats", "Gnbac1", "CTDRUG:gnbac1"),
    ("MONDO_0005314", "treats", "Imu-838 (10 Mg/day)", "CTDRUG:imu_838_10_mg_day_"),
    ("MONDO_0005314", "treats", "Imu-838 (30 Mg/day)", "CTDRUG:imu_838_30_mg_day_"),
    ("MONDO_0005314", "treats", "Imu-838 (45 Mg/day)", "CTDRUG:imu_838_45_mg_day_"),
    ("MONDO_0005314", "treats", "Peg-liposomal Prednisolone Sodium Phosphate", "CTDRUG:peg_liposomal_prednisolone_sodium_phosphate"),
    ("MONDO_0005314", "treats", "Perfusion Of Treatment Ocrelizumab", "CTDRUG:perfusion_of_treatment_ocrelizumab"),
    ("MONDO_0005314", "treats", "Perfusion Of Treatment Rituximab", "CTDRUG:perfusion_of_treatment_rituximab"),
    ("MONDO_0005314", "treats", "Rebif®", "CTDRUG:rebif_"),
    ("MONDO_0005314", "treats", "Rg2077 (ctla4-igg4m)", "CTDRUG:rg2077_ctla4_igg4m_"),
    ("MONDO_0005314", "treats", "Short-course Ocrelizumab", "CTDRUG:short_course_ocrelizumab"),
    ("MONDO_0005314", "treats", "Tysabri", "CTDRUG:tysabri"),
    ("MONDO_0005314", "treats", "Ublituximab", "CTDRUG:ublituximab"),
    ("MONDO_0005314", "treats", "Vay736", "CTDRUG:vay736"),
    ("MONDO_0018784", "treats", "Interferon beta-1a", "DrugBank:DB00060"),
    ("MONDO_0018784", "treats", "Natalizumab", "DrugBank:DB00108"),
    ("MONDO_0018784", "treats", "Ranitidine", "DrugBank:DB00863"),
    ("MONDO_0018784", "treats", "Methylprednisolone", "DrugBank:DB00959"),
    ("MONDO_0018784", "treats", "Ofatumumab", "DrugBank:DB06650"),
    ("MONDO_0018784", "treats", "Fingolimod", "DrugBank:DB08868"),
    ("MONDO_0018784", "treats", "Teriflunomide", "DrugBank:DB08880"),
    ("MONDO_0018784", "treats", "Dimethyl fumarate", "DrugBank:DB08908"),
    ("MONDO_0018784", "treats", "Peginterferon beta-1a", "DrugBank:DB09122"),
    ("MONDO_0018784", "treats", "Ocrelizumab", "DrugBank:DB11988"),
    ("MONDO_0018784", "treats", "Alemtuzumab Gz402673", "CTDRUG:alemtuzumab_gz402673"),
    ("MONDO_0018784", "treats", "Beta-interferon", "CTDRUG:beta_interferon"),
    ("MONDO_0018784", "treats", "Biib017 (peginterferon Beta-1a)", "CTDRUG:biib017_peginterferon_beta_1a_"),
    ("MONDO_0018784", "treats", "Bioactivated Gra For Adult Patients", "CTDRUG:bioactivated_gra_for_adult_patients"),
    ("MONDO_0018784", "treats", "Bioactivated Gra For Pediatric Patients", "CTDRUG:bioactivated_gra_for_pediatric_patients"),
    ("MONDO_0018784", "treats", "Fenebrutinib", "CTDRUG:fenebrutinib"),
    ("MONDO_0018784", "treats", "Fingolimod 0.5mg", "CTDRUG:fingolimod_0_5mg"),
    ("MONDO_0018784", "treats", "Glatiramer Acetate", "CTDRUG:glatiramer_acetate"),
    ("MONDO_0018784", "treats", "Interferon Β-1a", "CTDRUG:interferon_1a"),
    ("MONDO_0018784", "treats", "Interferon Beta-1b (betaseron, Bay86-5046)", "CTDRUG:interferon_beta_1b_betaseron_bay86_5046_"),
    ("MONDO_0018784", "treats", "Interferon Beta Type 1a", "CTDRUG:interferon_beta_type_1a"),
    ("MONDO_0018784", "treats", "Rebif®", "CTDRUG:rebif_"),
    ("MONDO_0018784", "treats", "Siponimod", "CTDRUG:siponimod"),
    ("MONDO_0018784", "treats", "Ublituximab", "CTDRUG:ublituximab"),
]


def drug_iri(did):
    pfx, loc = did.split(":", 1)
    if pfx == "DrugBank":
        return f"http://identifiers.org/drugbank/{loc}"
    return f"https://rdaccelerate.org/resource/CTDRUG_{loc}"


VARS = ["mondo", "mondoLabel", "rel", "drug", "drugLabel", "drugPref", "drugCat", "drugId"]
rows = [
    {
        "mondo": f"http://purl.obolibrary.org/obo/{m}",
        "mondoLabel": MLAB[m],
        "rel": rel,
        "drug": drug_iri(did),
        "drugLabel": lab,
        "drugPref": lab,
        "drugCat": "biolink:Drug",
        "drugId": did,
    }
    for m, rel, lab, did in R
]
assert len(rows) == 93, len(rows)

os.makedirs(f"{WD}/data", exist_ok=True)
with open(f"{WD}/data/rdkg_ms_drugs.json", "w") as fh:
    json.dump({"vars": VARS, "rows": rows, "row_count": len(rows)}, fh, indent=1, ensure_ascii=False)
with open(f"{WD}/data/rdkg_ms_drugs.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["mondo", "mondoLabel", "rel", "drugLabel", "drugId"])
    for r in rows:
        w.writerow([r["mondo"].rsplit("/", 1)[-1], r["mondoLabel"], r["rel"], r["drugLabel"], r["drugId"]])

print("rows", len(rows), "| distinct drugId", len({r["drugId"] for r in rows}),
      "| distinct label", len({r["drugLabel"] for r in rows}),
      "| subtypes", sorted({r["mondoLabel"] for r in rows}))

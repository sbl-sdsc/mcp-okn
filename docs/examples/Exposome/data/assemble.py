"""Assemble the findings-master and related CSVs from the base exposome data."""

import csv
from pathlib import Path

D = "/sessions/nifty-festive-gauss/mnt/outputs/exposome/data"


def load(fn):
    """Load a CSV file from the data directory as a list of dict rows."""
    with Path(f"{D}/{fn}").open() as f:
        return list(csv.DictReader(f))


chem = load("chemicals.csv")
targets = load("targets.csv")
aop = load("aop_backbone.csv")
tox = load("chemicals.csv")
gxa = {r["symbol"]: r for r in load("gxa_expression.csv")}
spoke = load("spoke_gene_disease.csv")
rdkg = {
    r["symbol"]: int(r["n_rare_disease_mondo"]) for r in load("rdkg_rare_disease.csv")
}
prokn = {r["symbol"]: r for r in load("prokn_protein.csv")}
fuse = load("ice_functional_use.csv")
haz = load("pubchem_hazards.csv")
bridge = {
    r["doid"].replace("DOID:", "DOID_"): r
    for r in load("disease_bridge_doid_mondo.csv")
}
oard = load("oard_disease_phenotype.csv")

cas2ab = {r["cas"]: r["abbrev"] for r in chem}
ab2cas = {r["abbrev"]: r["cas"] for r in chem}

# ---------- 1. FINDINGS MASTER (one row per finding) ----------
F = []
fid = 0


def add(**k):
    """Append a finding row with an auto-incremented finding id."""
    global fid
    fid += 1
    k["finding_id"] = f"F{fid:04d}"
    F.append(k)


COLS = [
    "finding_id",
    "layer",
    "chemical",
    "entity",
    "related_entity",
    "source_kg",
    "relationship_type",
    "effect_or_score",
    "evidence_kind",
    "notes",
]

# chemical identity
for r in chem:
    add(
        layer="chemical-identity",
        chemical=r["abbrev"],
        entity=r["cas"],
        related_entity=f"CID:{r['pubchem_cid'] or 'NA'}; {r['dtxsid']}",
        source_kg="aopwiki/ice/toxcast",
        relationship_type="has-identifier",
        effect_or_score="",
        evidence_kind="curated identity",
        notes=r["name"],
    )
# AOP backbone
for r in aop:
    add(
        layer="aop",
        chemical=r["chemical"],
        entity=f"AOP {r['aop_id']}",
        related_entity=r["adverse_outcome"],
        source_kg="biobricks-aopwiki",
        relationship_type="has-adverse-outcome",
        effect_or_score="",
        evidence_kind="curated AOP link",
        notes=f"MIE: {r['mie_title']}; {r['n_key_events']} KEs; target {r['curated_target']}",
    )
# assay coverage (ToxCast)
for r in chem:
    if r["toxcast_tested"]:
        add(
            layer="assay",
            chemical=r["abbrev"],
            entity="ToxCast HTS panel",
            related_entity="multiple endpoints",
            source_kg="biobricks-toxcast",
            relationship_type="assayed-in",
            effect_or_score=f"{r['toxcast_active']}/{r['toxcast_tested']} active",
            evidence_kind="HTS assay measurement",
            notes="binary hitcall; not in-vivo effect",
        )
# functional use
for r in fuse:
    add(
        layer="functional-use",
        chemical=cas2ab.get(r["cas"], r["cas"]),
        entity=r["category"],
        related_entity=r["use_type"],
        source_kg="biobricks-ice",
        relationship_type="functional-use-of",
        effect_or_score="",
        evidence_kind="ICE functional-use curation",
        notes="",
    )
# hazards
for r in haz:
    add(
        layer="hazard",
        chemical=r["chemical"],
        entity=r["category"],
        related_entity=r["hazard_annotation"],
        source_kg="biobricks-pubchem-annotations",
        relationship_type="hazard-annotation",
        effect_or_score="",
        evidence_kind="literature/safety annotation",
        notes="",
    )
# target genes (molecular targets)
for r in targets:
    add(
        layer="molecular-target",
        chemical="(bisphenol class)",
        entity=r["symbol"],
        related_entity=f"Ensembl:{r['ensembl']}; Entrez:{r['entrez']}; UniProt:{r['uniprot']}",
        source_kg="biobricks-aopwiki",
        relationship_type="target-gene-of",
        effect_or_score="",
        evidence_kind="curated target ID",
        notes=r["role_in_bisphenol_MoA"],
    )
# expression (GXA)
for s, r in gxa.items():
    add(
        layer="expression",
        chemical="(via target)",
        entity=s,
        related_entity="GXA disease/tissue contrasts",
        source_kg="gene-expression-atlas-okn",
        relationship_type="differentially-expressed-in",
        effect_or_score=f"{r['n_sig_contrasts']} sig contrasts (up {r['n_up']}/dn {r['n_down']}); maxLog2FC {r['max_abs_log2fc']}",
        evidence_kind="measured differential expression",
        notes="",
    )
# gene->disease (spoke)
for r in spoke:
    add(
        layer="disease-assoc",
        chemical="(via target)",
        entity=r["symbol"],
        related_entity=f"{r['disease']} ({r['doid']})",
        source_kg="spoke-okn",
        relationship_type="associated-with-disease",
        effect_or_score="",
        evidence_kind="curated/statistical disease association",
        notes="gene-disease",
    )
# gene->rare disease (rdkg)
for s, n in rdkg.items():
    add(
        layer="rare-disease",
        chemical="(via target)",
        entity=s,
        related_entity=f"{n} MONDO rare diseases",
        source_kg="rdkg",
        relationship_type="associated-with-disease",
        effect_or_score=str(n),
        evidence_kind="curated rare-disease association",
        notes="",
    )
# protein annotation (prokn)
for s, r in prokn.items():
    add(
        layer="protein-annotation",
        chemical="(via target)",
        entity=s,
        related_entity=f"UniProt:{r['uniprot']}",
        source_kg="prokn",
        relationship_type="protein-annotation",
        effect_or_score=f"{r['n_reactome_pathways']} Reactome; {r['n_go_terms']} GO",
        evidence_kind="curated protein annotation",
        notes="",
    )
# disease->phenotype (oard)
for r in oard:
    add(
        layer="disease-phenotype",
        chemical="(outcome)",
        entity=r["disease"],
        related_entity=f"{r['n_ehr_phenotypes']} EHR phenotypes",
        source_kg="oard-kg",
        relationship_type="disease-phenotype",
        effect_or_score=r["n_ehr_phenotypes"],
        evidence_kind="EHR disease-phenotype association",
        notes=r["mondo"],
    )
# industry
for r in load("industry_context.csv"):
    add(
        layer="industry",
        chemical="(bisphenol class)",
        entity=r["kg"],
        related_entity=r["finding"],
        source_kg=r["kg"],
        relationship_type="manufactured-used-by",
        effect_or_score="",
        evidence_kind=r["evidence_kind"],
        notes=r["detail"],
    )

with Path(f"{D}/../findings_master.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in F:
        w.writerow({c: r.get(c, "") for c in COLS})
print(f"findings_master.csv: {len(F)} findings")

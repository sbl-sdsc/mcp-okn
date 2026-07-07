#!/usr/bin/env python3
"""Integrate MS knowledge-graph findings across Proto-OKN sources."""

import csv
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/sessions/stoic-charming-ride/mnt/MS/msbuild")
from data_genes import DIGCFDE_CSV, RDKG_GENES, SPOKE_GENES
from data_other import (
    BIOMARKER_ANALYTES,
    BIOMARKER_SPECIMENS,
    BIOMARKER_TOTAL_RECORDS,
    CL_LABELS,
    DIGCFDE_FACTORS,
    DIGCFDE_GENESETS,
    GXA_CSV,
    GXA_TOTAL_ASSAYS,
    GXA_TOTAL_GENES,
    PROKN_DRUG_TOTAL,
    PROKN_DRUGS_NAMED,
    RDKG_CLINICAL,
    RDKG_CONTRA,
    RDKG_RISK,
    SPOKE_TREATS,
)
from gxa_all import GXA_ALL_SYMBOLS

OUT = "/sessions/stoic-charming-ride/mnt/MS"

# ---- parse digcfdekg weights ----
digcfde = {}
for row in csv.DictReader(io.StringIO(DIGCFDE_CSV)):
    digcfde[row["sym"]] = float(row["maxw"])

# ---- parse GXA differential expression ----
gxa_rows = list(csv.DictReader(io.StringIO(GXA_CSV)))
gxa_genes = {}
for r in gxa_rows:
    sym = r["sym"]
    cell = CL_LABELS.get(r["cell"], r["cell"])
    d = r["dir"]
    lfc = float(r["log2fc"])
    adjp = float(r["adjp"])
    rec = gxa_genes.setdefault(
        sym, {"cells": set(), "dir": d, "lfc": lfc, "adjp": adjp}
    )
    rec["cells"].add(cell)
    if abs(lfc) > abs(rec["lfc"]):
        rec["lfc"] = lfc
        rec["dir"] = d
        rec["adjp"] = adjp

# ---- biotype heuristic ----
NONCODING = re.compile(
    r"^(MIR|LINC|SNOR|SNAR|LOC\d|TTTY|XIST|TSIX|.*-AS\d+$|.*-DT$|H1-\d|HIST)"
)


def biotype(sym):
    """Infer a gene biotype label from its symbol naming convention."""
    if (
        sym.endswith("-AS1")
        or sym.endswith("-DT")
        or sym.startswith(("MIR", "LINC", "LOC1", "TTTY", "SNOR"))
        or sym
        in {
            "XIST",
            "TSIX",
            "ANOS2P",
            "OR1F2P",
            "NFYC-AS1",
            "USP6NL-AS1",
            "DTNB-AS1",
            "ANKRD13C-DT",
            "RPSAP8",
            "ANKRD36BP2",
            "IGKV1OR2-108",
        }
    ):
        return "non-coding"
    return "protein-coding"


# ---- integrate association genes ----
all_assoc = set(SPOKE_GENES) | set(RDKG_GENES) | set(digcfde)
gene_recs = []
for g in sorted(all_assoc):
    srcs = []
    if g in SPOKE_GENES:
        srcs.append("spoke-okn")
    if g in RDKG_GENES:
        srcs.append("rdkg")
    if g in digcfde:
        srcs.append("digcfdekg")
    n = len(srcs)
    w = digcfde.get(g, "")
    ev = []
    if ("spoke-okn" in srcs) or ("rdkg" in srcs):
        ev.append("curated_link")
    if "digcfdekg" in srcs:
        ev.append("statistical_association")
    gxa_note = ""
    if g in gxa_genes:
        cells = ", ".join(sorted(gxa_genes[g]["cells"]))
        gxa_note = f"also DE in MS blood ({gxa_genes[g]['dir']} in {cells})"
        ev.append("measured_activity_change")
    elif g in GXA_ALL_SYMBOLS:
        gxa_note = "also differentially expressed in MS blood (GXA)"
        ev.append("measured_activity_change")
    # tier
    if n >= 3:
        tier = "T1 very-high"
    elif n == 2:
        tier = "T2 high"
    elif n == 1 and (isinstance(w, float) and w >= 7):
        tier = "T3 medium"
    else:
        tier = "T4 low"
    gene_recs.append(
        {
            "entity_type": "gene",
            "entity": g,
            "entity_id": "",
            "biotype": biotype(g),
            "relationship": "associated_with_MS",
            "sources": ";".join(srcs),
            "n_sources": n,
            "evidence_types": ";".join(ev),
            "best_score": (w if w != "" else ""),
            "score_type": ("PIGEAN/EAGGL_weight" if w != "" else "source_count"),
            "tissue_celltype": "",
            "confidence_tier": tier,
            "notes": gxa_note,
        }
    )

# gene tier distribution & top
by_n = {}
for r in gene_recs:
    by_n[r["n_sources"]] = by_n.get(r["n_sources"], 0) + 1
tier1 = sorted([r["entity"] for r in gene_recs if r["n_sources"] >= 3])
tier2 = sorted([r["entity"] for r in gene_recs if r["n_sources"] == 2])


# top genes by (n_sources, weight)
def sortkey(r):
    """Sort key: most sources first, then highest best score."""
    w = r["best_score"] if isinstance(r["best_score"], float) else -1
    return (-r["n_sources"], -(w if w != "" else -1))


top_genes = [
    (r["entity"], r["n_sources"], (r["best_score"] if r["best_score"] != "" else ""))
    for r in sorted(gene_recs, key=sortkey)
][:45]

# genes with all THREE evidence flavors (curated + statistical + measured)
triple = sorted(
    [
        r["entity"]
        for r in gene_recs
        if ("spoke-okn" in r["sources"] or "rdkg" in r["sources"])
        and "digcfdekg" in r["sources"]
        and r["entity"] in GXA_ALL_SYMBOLS
    ]
)
# association genes also measured DE (any flavor overlap)
assoc_and_measured = sorted(
    [r["entity"] for r in gene_recs if r["entity"] in GXA_ALL_SYMBOLS]
)

noncoding_assoc = sorted(
    [r["entity"] for r in gene_recs if r["biotype"] == "non-coding"]
)

# ---- GXA altered-activity findings (measured) ----
gxa_findings = []
SEX = {
    "RPS4Y1",
    "DDX3Y",
    "KDM5D",
    "UTY",
    "TXLNGY",
    "EIF1AY",
    "PRKY",
    "ZFY",
    "USP9Y",
    "TTTY15",
    "TTTY14",
    "XIST",
    "TSIX",
    "TMSB4Y",
    "ANOS2P",
}
for sym, rec in sorted(gxa_genes.items(), key=lambda kv: -abs(kv[1]["lfc"])):
    note = (
        "sex-chromosome/XIST artifact (case-control sex imbalance)"
        if sym in SEX
        else ""
    )
    gxa_findings.append(
        {
            "entity_type": "gene_altered_activity",
            "entity": sym,
            "entity_id": "",
            "biotype": biotype(sym),
            "relationship": f"differentially_expressed_{rec['dir']}",
            "sources": "gene-expression-atlas-okn",
            "n_sources": 1,
            "evidence_types": "measured_activity_change",
            "best_score": rec["lfc"],
            "score_type": "log2FC",
            "tissue_celltype": ", ".join(sorted(rec["cells"])),
            "confidence_tier": ("T4 low" if sym in SEX else "T2 high"),
            "notes": note,
        }
    )

# ---- pathway / gene set findings ----
path_findings = []
for label, w in DIGCFDE_GENESETS:
    path_findings.append(
        {
            "entity_type": "pathway_or_geneset",
            "entity": label,
            "entity_id": "",
            "biotype": "",
            "relationship": "gene_set_predicts_MS",
            "sources": "digcfdekg",
            "n_sources": 1,
            "evidence_types": "pathway_membership;statistical_association",
            "best_score": w,
            "score_type": "EAGGL_weight",
            "tissue_celltype": "",
            "confidence_tier": "T3 medium",
            "notes": "CFDE gene set (geneSetToTrait)",
        }
    )
for label, w in DIGCFDE_FACTORS:
    path_findings.append(
        {
            "entity_type": "pathway_or_geneset",
            "entity": f"[factor] {label}",
            "entity_id": "",
            "biotype": "",
            "relationship": "latent_factor_models_MS",
            "sources": "digcfdekg",
            "n_sources": 1,
            "evidence_types": "statistical_association",
            "best_score": w,
            "score_type": "EAGGL_probability",
            "tissue_celltype": "",
            "confidence_tier": "T4 low",
            "notes": "latent disease-mechanism factor (traitToFactor)",
        }
    )

# ---- drug findings ----
drug_findings = []
for d in PROKN_DRUGS_NAMED:
    drug_findings.append(
        {
            "entity_type": "drug",
            "entity": d,
            "entity_id": "",
            "biotype": "",
            "relationship": "indicated_or_investigated_for_MS",
            "sources": "prokn",
            "n_sources": 1,
            "evidence_types": "curated_link",
            "best_score": "",
            "score_type": "",
            "tissue_celltype": "",
            "confidence_tier": "T3 medium",
            "notes": "ChEMBL Indication (NCIT_C41184); 180 compounds total, most ChEMBL-ID-only",
        }
    )
for d in RDKG_CONTRA:
    drug_findings.append(
        {
            "entity_type": "drug",
            "entity": d,
            "entity_id": "",
            "biotype": "",
            "relationship": "contraindicated_for_MS",
            "sources": "rdkg",
            "n_sources": 1,
            "evidence_types": "curated_link",
            "best_score": "",
            "score_type": "",
            "tissue_celltype": "",
            "confidence_tier": "T3 medium",
            "notes": "rdkg biolink:contraindicated_for (DrugBank)",
        }
    )
for d in RDKG_RISK:
    drug_findings.append(
        {
            "entity_type": "drug",
            "entity": d,
            "entity_id": "",
            "biotype": "",
            "relationship": "environmental_risk_or_modifier (contributes_to)",
            "sources": "rdkg",
            "n_sources": 1,
            "evidence_types": "curated_link",
            "best_score": "",
            "score_type": "",
            "tissue_celltype": "",
            "confidence_tier": "T4 low",
            "notes": "rdkg biolink:contributes_to (ChemicalExposure); risk factor/modifier",
        }
    )
for d in SPOKE_TREATS:
    drug_findings.append(
        {
            "entity_type": "drug",
            "entity": d,
            "entity_id": "",
            "biotype": "",
            "relationship": "treats_MS (spoke TREATS_CtD)",
            "sources": "spoke-okn",
            "n_sources": 1,
            "evidence_types": "curated_link",
            "best_score": "",
            "score_type": "",
            "tissue_celltype": "",
            "confidence_tier": "T4 low",
            "notes": "spoke-okn TREATS layer near-empty for MS (non-therapeutic artifact)",
        }
    )

# ---- clinical feature findings ----
clin_findings = []
for label, hp in RDKG_CLINICAL:
    clin_findings.append(
        {
            "entity_type": "clinical_feature",
            "entity": label,
            "entity_id": hp,
            "biotype": "",
            "relationship": "phenotype_of_MS",
            "sources": "rdkg",
            "n_sources": 1,
            "evidence_types": "curated_link",
            "best_score": "",
            "score_type": "",
            "tissue_celltype": "",
            "confidence_tier": "T3 medium",
            "notes": "rdkg has_phenotype/has_onset (HP)",
        }
    )

# ---- biomarker findings ----
bm_findings = []
for a in BIOMARKER_ANALYTES:
    bm_findings.append(
        {
            "entity_type": "biomarker",
            "entity": a,
            "entity_id": "",
            "biotype": "",
            "relationship": "biomarker_for_MS",
            "sources": "biomarkerkg",
            "n_sources": 1,
            "evidence_types": "curated_link",
            "best_score": "",
            "score_type": "",
            "tissue_celltype": "blood/serum",
            "confidence_tier": "T3 medium",
            "notes": "assessed molecule of biomarker record AN6263-1 (S1P / IFN-IL17 axis)",
        }
    )
bm_findings.append(
    {
        "entity_type": "biomarker",
        "entity": f"[{BIOMARKER_TOTAL_RECORDS} specimen-tagged records]",
        "entity_id": "",
        "biotype": "",
        "relationship": "biomarker_records_for_MS",
        "sources": "biomarkerkg",
        "n_sources": 1,
        "evidence_types": "curated_link",
        "best_score": "",
        "score_type": "",
        "tissue_celltype": "; ".join(sorted(set(BIOMARKER_SPECIMENS.values()))),
        "confidence_tier": "T3 medium",
        "notes": "biomarker records defined by specimen+disease; analyte unlabeled for most (undercount)",
    }
)

# ---- variant (flagged undercount) ----
var_findings = [
    {
        "entity_type": "genetic_variant",
        "entity": "(gene-level GWAS signal; no variant nodes)",
        "entity_id": "",
        "biotype": "",
        "relationship": "variant-derived (digcfdekg PIGEAN uses GWAS summary stats)",
        "sources": "digcfdekg",
        "n_sources": 1,
        "evidence_types": "statistical_association",
        "best_score": "",
        "score_type": "",
        "tissue_celltype": "",
        "confidence_tier": "n/a",
        "notes": "UNDERCOUNT: no MS-anchored variant-entity layer in federation (checked prokn/rdkg/pankgraph); HLA-DRB1*15:01 and other risk alleles represented only at gene level",
    }
]

# ---- assemble & write findings CSV ----
COLS = [
    "entity_type",
    "entity",
    "entity_id",
    "biotype",
    "relationship",
    "sources",
    "n_sources",
    "evidence_types",
    "best_score",
    "score_type",
    "tissue_celltype",
    "confidence_tier",
    "notes",
]
all_findings = (
    gene_recs
    + gxa_findings
    + path_findings
    + drug_findings
    + clin_findings
    + bm_findings
    + var_findings
)
with Path(f"{OUT}/MS_knowledge_map_findings.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in all_findings:
        w.writerow(r)

# ---- gene source matrix CSV ----
with Path(f"{OUT}/MS_gene_source_matrix.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(
        [
            "gene",
            "biotype",
            "spoke-okn",
            "rdkg",
            "digcfdekg",
            "gxa_DE",
            "n_assoc_sources",
            "digcfdekg_weight",
            "confidence_tier",
        ]
    )
    for r in sorted(gene_recs, key=sortkey):
        g = r["entity"]
        w.writerow(
            [
                g,
                r["biotype"],
                int("spoke-okn" in r["sources"]),
                int("rdkg" in r["sources"]),
                int("digcfdekg" in r["sources"]),
                int(g in GXA_ALL_SYMBOLS),
                r["n_sources"],
                (r["best_score"] if r["best_score"] != "" else ""),
                r["confidence_tier"],
            ]
        )

# ---- evidence-type counts ----
ev_counts = {
    "curated_link": 0,
    "statistical_association": 0,
    "measured_activity_change": 0,
    "pathway_membership": 0,
}
for r in all_findings:
    for e in str(r["evidence_types"]).split(";"):
        if e in ev_counts:
            ev_counts[e] += 1

entity_counts = {}
for r in all_findings:
    entity_counts[r["entity_type"]] = entity_counts.get(r["entity_type"], 0) + 1

stats = {
    "n_findings": len(all_findings),
    "n_genes_assoc": len(gene_recs),
    "n_genes_noncoding_assoc": len(noncoding_assoc),
    "n_gxa_altered_activity_shown": len(gxa_findings),
    "gxa_total_de_genes": GXA_TOTAL_GENES,
    "gxa_total_assays": GXA_TOTAL_ASSAYS,
    "n_pathways_genesets": len(path_findings),
    "n_drugs": len(drug_findings),
    "prokn_drug_total": PROKN_DRUG_TOTAL,
    "n_clinical": len(clin_findings),
    "n_biomarkers": len(bm_findings),
    "biomarker_total_records": BIOMARKER_TOTAL_RECORDS,
    "gene_by_nsources": by_n,
    "source_gene_totals": {
        "spoke-okn": len(SPOKE_GENES),
        "rdkg": len(RDKG_GENES),
        "digcfdekg": len(digcfde),
    },
    "evidence_counts": ev_counts,
    "entity_counts": entity_counts,
    "tier1_genes_3sources": tier1,
    "tier2_genes_2sources": tier2,
    "triple_evidence_genes": triple,
    "assoc_and_measured_genes": assoc_and_measured,
    "noncoding_assoc_genes": noncoding_assoc,
    "top_genes": top_genes,
}
with Path(f"{OUT}/ms_stats.json").open("w") as f:
    json.dump(stats, f, indent=2)

print("findings:", len(all_findings))
print("assoc genes:", len(gene_recs), "| by n_sources:", by_n)
print("T1 (3 sources):", len(tier1), tier1)
print("T2 (2 sources):", len(tier2))
print("triple-evidence (curated+stat+measured):", len(triple), triple)
print("assoc genes also measured DE:", len(assoc_and_measured))
print("noncoding assoc:", noncoding_assoc)
print("evidence counts:", ev_counts)
print("entity counts:", entity_counts)
print("top 12 genes:", top_genes[:12])

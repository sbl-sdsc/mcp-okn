"""Tests for spoke-genelab contrast classification and the get_valid_contrasts tool."""

from __future__ import annotations

from typing import Any

import pytest

from mcp_okn.contrasts import (
    SPOKE_GENELAB_CONTRAST_GUIDANCE,
    SPOKE_GENELAB_CONTRAST_SNIPPET,
    classify_contrast,
    strip_condition_factors,
)
from mcp_okn.tools import contrasts_tools

# ── strip_condition_factors ──────────────────────────────────────────────────


def test_strip_removes_spelled_out_labels_case_insensitively():
    assert strip_condition_factors(
        ["Space Flight", "Ground control", "Basal Control", "WildType"]
    ) == {"WildType"}


def test_strip_removes_short_group_codes():
    assert strip_condition_factors(["GC", "FLT_C1", "VIV_C2", "Day 30"]) == {"Day 30"}


def test_strip_keeps_real_factors_that_contain_a_control_word():
    kept = strip_condition_factors(
        ["Hardware 1G Ground Control", "HLU_IR", "Euth_C_DI", "Nrf2KO"]
    )
    assert kept == {"Hardware 1G Ground Control", "HLU_IR", "Euth_C_DI", "Nrf2KO"}


def test_strip_drops_blanks():
    assert strip_condition_factors(["", "  ", "Space Flight"]) == set()


# ── classify_contrast ────────────────────────────────────────────────────────


def _row(f1: list[str], f2: list[str], m1: str = "GLDS-1", m2: str = "GLDS-1") -> dict:
    return {
        "factors_1": f1,
        "factors_2": f2,
        "material_id_1": m1,
        "material_id_2": m2,
    }


def test_confounded_when_genotype_differs_between_arms():
    # The incident: WildType in flight, knockout on the ground.
    v = classify_contrast(
        _row(["Space Flight", "WildType"], ["Ground Control", "Nrf2KO"])
    )
    assert v["is_clean_contrast"] is False
    assert "WildType" in v["confound_reason"] and "Nrf2KO" in v["confound_reason"]
    assert v["flight_covariates"] == ["WildType"]
    assert v["control_covariates"] == ["Nrf2KO"]


def test_clean_when_arms_match_on_genotype():
    v = classify_contrast(
        _row(["Space Flight", "WildType"], ["Ground Control", "WildType"])
    )
    assert v["is_clean_contrast"] is True
    assert v["confound_reason"] is None


def test_clean_with_a_shared_extra_covariate_on_both_arms():
    v = classify_contrast(
        _row(["Space Flight", "Day 30"], ["Ground Control", "Day 30"])
    )
    assert v["is_clean_contrast"] is True


def test_confounded_when_materials_differ():
    v = classify_contrast(
        _row(["Space Flight"], ["Ground Control"], m1="GLDS-1", m2="GLDS-2")
    )
    assert v["is_clean_contrast"] is False
    assert "materials differ" in v["confound_reason"]


def test_clean_when_material_ids_absent_and_covariates_match():
    # Some studies (e.g. microbiome) carry no material_id — absence must not fail.
    v = classify_contrast(_row(["Space Flight"], ["Ground Control"], m1="", m2=""))
    assert v["is_clean_contrast"] is True
    assert "baseline" in v["contrast_label"]


# ── snippet / guidance content ───────────────────────────────────────────────


def test_snippet_tests_cross_arm_covariate_equality():
    s = SPOKE_GENELAB_CONTRAST_SNIPPET
    assert 'schema:factor_space_1 "Space Flight"' in s
    assert 'schema:factor_space_2 "Ground Control"' in s
    # The within-assay test cross-references factors_1 against factors_2 (both ways).
    assert "FILTER NOT EXISTS { ?assay schema:factors_2 ?x }" in s
    assert "FILTER NOT EXISTS { ?assay schema:factors_1 ?y }" in s
    assert "get_valid_contrasts" in s


def test_guidance_leads_with_within_assay_test():
    g = SPOKE_GENELAB_CONTRAST_GUIDANCE
    assert "within-assay" in g.lower()
    assert "PRIMARY" in g


# ── get_valid_contrasts tool (run_sparql mocked) ─────────────────────────────


def _fake_rows() -> dict[str, Any]:
    return {
        "rows": [
            {  # clean: arms match on WildType
                "assay": "assay/clean",
                "material_id_1": "GLDS-1",
                "material_id_2": "GLDS-1",
                "measurement": "transcription",
                "technology": "RNA-seq",
                "tissues": "UBERON_0002371",
                "factors_1": "Space Flight|WildType",
                "factors_2": "Ground Control|WildType",
            },
            {  # confounded: WT flight vs KO ground
                "assay": "assay/confounded",
                "material_id_1": "GLDS-2",
                "material_id_2": "GLDS-2",
                "measurement": "transcription",
                "technology": "RNA-seq",
                "tissues": "UBERON_0002371",
                "factors_1": "Space Flight|WildType",
                "factors_2": "Ground Control|Nrf2KO",
            },
        ],
        "row_count": 2,
    }


@pytest.fixture
def _mock_run_sparql(monkeypatch):
    async def fake(query: str, fmt: str = "json") -> dict[str, Any]:
        return _fake_rows()

    monkeypatch.setattr(contrasts_tools, "run_sparql", fake)


async def test_tool_excludes_confounded_by_default(_mock_run_sparql):
    out = await contrasts_tools.get_valid_contrasts()
    assert out["clean_count"] == 1
    assert out["confounded_count"] == 1
    assert [c["assay"] for c in out["contrasts"]] == ["assay/clean"]
    assert "note" in out  # loud pointer to include_confounded


async def test_tool_includes_confounded_when_asked(_mock_run_sparql):
    out = await contrasts_tools.get_valid_contrasts(include_confounded=True)
    assert len(out["contrasts"]) == 2
    confounded = next(c for c in out["contrasts"] if c["assay"] == "assay/confounded")
    assert confounded["is_clean_contrast"] is False
    assert "Nrf2KO" in confounded["confound_reason"]
    # clean-first ordering
    assert out["contrasts"][0]["assay"] == "assay/clean"


async def test_tool_resolves_tissue_curie(monkeypatch):
    captured: dict[str, str] = {}

    async def fake(query: str, fmt: str = "json") -> dict[str, Any]:
        captured["query"] = query
        return {"rows": [], "row_count": 0}

    monkeypatch.setattr(contrasts_tools, "run_sparql", fake)
    out = await contrasts_tools.get_valid_contrasts(tissue="UBERON:0002371")
    assert out["tissue"] == "http://purl.obolibrary.org/obo/UBERON_0002371"
    assert (
        "schema:INVESTIGATED_ASiA <http://purl.obolibrary.org/obo/UBERON_0002371>"
        in captured["query"]
    )

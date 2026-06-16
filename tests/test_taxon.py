"""Unit tests for the NCBITaxon hub module (mcp_okn.taxon).

These exercise the skeleton builders and per-KG normalization fragments directly,
complementing the tool-level coverage of taxon_overlap in test_probe.py.
"""

import pytest

from mcp_okn import taxon
from mcp_okn.taxon import (
    TAXON_HUB_KGS,
    _sub,
    _taxon_source,
    build_clade_skeleton,
    build_exact_skeleton,
    in_taxon_hub,
)

_NCBITAXON = "http://purl.obolibrary.org/obo/NCBITaxon_"


# --- membership --------------------------------------------------------------


@pytest.mark.parametrize("kg", TAXON_HUB_KGS)
def test_in_taxon_hub_true_for_every_member(kg):
    assert in_taxon_hub(kg) is True
    assert _taxon_source(kg, "a") is not None


@pytest.mark.parametrize("kg", ["prokn", "oard-kg", "ubergraph", "dreamkg"])
def test_in_taxon_hub_false_for_non_members(kg):
    assert in_taxon_hub(kg) is False
    assert _taxon_source(kg, "a") is None


# --- per-KG normalization fragments -----------------------------------------


@pytest.mark.parametrize("kg", TAXON_HUB_KGS)
def test_every_source_targets_ncbitaxon_and_its_named_graph(kg):
    frag = _taxon_source(kg, "t")
    assert _NCBITAXON in frag
    assert f"https://purl.org/okn/frink/kg/{kg}" in frag
    # the requested variable is the one bound/matched as the taxon
    assert "?t" in frag


def test_spoke_okn_extracts_taxid_from_organism_iri():
    frag = _taxon_source("spoke-okn", "t")
    assert "OrganismTaxon" in frag
    assert "/organism/([0-9]+)" in frag
    assert "BIND(IRI(CONCAT(" in frag  # constructed from the embedded id


def test_nde_extracts_taxid_from_uniprot_taxonomy_iri():
    frag = _taxon_source("nde", "t")
    assert "http://schema.org/species" in frag
    assert "/taxonomy/([0-9]+)" in frag


def test_sawgraph_uses_subclassof_subject_no_bind():
    frag = _taxon_source("sawgraph", "t")
    assert "subClassOf" in frag
    assert f"STRSTARTS(STR(?t),'{_NCBITAXON}')" in frag
    # sawgraph's taxa already ARE NCBITaxon IRIs — no id reconstruction
    assert "CONCAT" not in frag


def test_aopwiki_uses_dc_identifier():
    frag = _taxon_source("biobricks-aopwiki", "t")
    assert "http://purl.org/dc/elements/1.1/identifier" in frag


def test_gene_expression_atlas_uses_in_taxon():
    frag = _taxon_source("gene-expression-atlas-okn", "t")
    assert "https://w3id.org/biolink/vocab/in_taxon" in frag


def test_spoke_genelab_unions_model_and_microbiome_representations():
    frag = _taxon_source("spoke-genelab", "t")
    assert "UNION" in frag
    assert "schema/taxonomy" in frag  # model-organism Gene.taxonomy literals
    assert "schema/Organism" in frag  # microbiome Organism node IRIs
    assert "/node/([0-9]+)" in frag  # taxid embedded in the node IRI


# --- _sub wrapping -----------------------------------------------------------


def test_sub_wraps_source_in_distinct_subquery():
    out = _sub("sawgraph", "a")
    assert out.startswith("{ SELECT DISTINCT ?a WHERE {")
    assert _taxon_source("sawgraph", "a") in out


# --- skeleton builders -------------------------------------------------------


def test_build_exact_skeleton_intersects_on_shared_var():
    sk = build_exact_skeleton("nde", "sawgraph")
    # both sides collapse to DISTINCT subqueries on the SAME var ?t, then count it
    assert sk.count("SELECT DISTINCT ?t") == 2
    assert "COUNT(DISTINCT ?t)" in sk
    assert "https://purl.org/okn/frink/kg/nde" in sk
    assert "https://purl.org/okn/frink/kg/sawgraph" in sk
    # exact-id is a strict intersection — no clade walk
    assert "subClassOf>*" not in sk
    assert "kg/ubergraph" not in sk


def test_build_clade_skeleton_is_directional_through_ubergraph():
    sk = build_clade_skeleton("nde", "sawgraph")
    # kg_a bound to ?a, kg_b to ?b, joined by kg_b nested under kg_a's clade
    assert "SELECT DISTINCT ?a" in sk
    assert "SELECT DISTINCT ?b" in sk
    assert "COUNT(DISTINCT ?b)" in sk
    assert "kg/ubergraph" in sk
    assert "?b <http://www.w3.org/2000/01/rdf-schema#subClassOf>* ?a" in sk


def test_clade_skeleton_flips_with_argument_order():
    ab = build_clade_skeleton("nde", "sawgraph")
    ba = build_clade_skeleton("sawgraph", "nde")
    # the directional clade differs by argument order; exact-id does not
    assert ab != ba
    assert build_exact_skeleton("nde", "sawgraph") == build_exact_skeleton(
        "nde", "sawgraph"
    )


def test_named_graph_used_for_ubergraph_in_clade():
    sk = build_clade_skeleton("nde", "sawgraph")
    assert f"<{taxon.named_graph('ubergraph')}>" in sk

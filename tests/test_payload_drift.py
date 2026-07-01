import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_payload_drift", ROOT / "scripts" / "check_payload_drift.py"
)
assert _spec and _spec.loader
drift = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drift)


def _fp(classes, predicates=()):
    return {"classes": sorted(classes), "predicates": sorted(predicates)}


def test_no_diff_when_identical():
    base = {"prokn": _fp(["Protein", "Gene"])}
    assert drift.diff_fingerprints(base, dict(base)) == {}


def test_removed_class_is_flagged():
    # The biomarkerkg scenario: a class disappears upstream.
    base = {"biomarkerkg": _fp(["Disease", "Phenotypic Feature", "Dataset"])}
    current = {"biomarkerkg": _fp(["Dataset"])}
    report = drift.diff_fingerprints(base, current)
    assert report["biomarkerkg"]["reason"] == "changed"
    assert report["biomarkerkg"]["removed"]["classes"] == ["Disease", "Phenotypic Feature"]
    assert report["biomarkerkg"]["added"]["classes"] == []


def test_added_predicate_is_flagged():
    base = {"kg": _fp(["A"], ["p1"])}
    current = {"kg": _fp(["A"], ["p1", "p2"])}
    report = drift.diff_fingerprints(base, current)
    assert report["kg"]["added"]["predicates"] == ["p2"]


def test_new_kg_without_baseline_is_flagged():
    report = drift.diff_fingerprints({}, {"newkg": _fp(["A"])})
    assert report["newkg"]["reason"] == "new"


def test_csv_removed_is_flagged():
    report = drift.diff_fingerprints({"gone": _fp(["A"])}, {})
    assert report["gone"]["reason"] == "csv_removed"


def test_committed_baseline_matches_current_payload_kgs():
    # Every fingerprinted KG must carry payload tags (they are what drift protects).
    from mcp_okn import payloads

    baseline = json.loads(
        (ROOT / "metadata" / "schema_fingerprints.json").read_text(encoding="utf-8")
    )
    assert baseline
    for sn in baseline:
        assert payloads.payloads_for(sn), f"{sn} fingerprinted but has no payload tags"

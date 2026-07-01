"""Flag KGs whose upstream entity schema changed since their payload tags were curated.

The per-KG payload tags in ``metadata/kg_payloads.json`` are curated partly from
each KG's entity schema — the ``*_entities.csv`` files in the
``sbl-sdsc/mcp-proto-okn`` repo that ``get_schema`` fetches live. Those CSVs can
change upstream and silently invalidate tags that were derived from a class or
predicate that later disappeared (as happened when ``biomarkerkg`` dropped its
``Disease`` / ``Phenotypic Feature`` classes). Since the tags are the only artifact
in this repo that leans on those CSVs — ``get_schema`` reads them live — a change is
otherwise invisible until someone notices a wrong answer.

This check fingerprints each KG's live schema (its class + predicate labels) and
diffs it against a committed baseline (``metadata/schema_fingerprints.json``). A
changed fingerprint doesn't mean the tags are wrong — it means "re-review this KG's
payload tags against its new schema, then accept the new baseline with ``--update``".

Only KGs that have a curated ``*_entities.csv`` are fingerprinted; KGs whose schema
is discovered live by SPARQL probing have no upstream-CSV drift vector of this kind.

Usage:
    uv run python scripts/check_payload_drift.py            # report drift; exit 1 if any
    uv run python scripts/check_payload_drift.py --update   # accept current schemas as the baseline
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

import httpx

from mcp_okn import payloads, registry, schema

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "metadata" / "schema_fingerprints.json"


async def _fingerprint(shortname: str, client: httpx.AsyncClient) -> dict[str, list[str]]:
    """Live schema fingerprint for a KG: its sorted class and predicate labels.

    Empty (``{}``) when the KG has no curated entity CSV — nothing to diff.
    """
    meta = await schema.fetch_entity_metadata(shortname, client=client, refresh=True)
    classes = sorted(
        {
            v["label"]
            for v in meta.values()
            if v.get("type") == "Class" and v.get("label")
        }
    )
    predicates = sorted(
        {
            v["label"]
            for v in meta.values()
            if v.get("type") != "Class" and v.get("label")
        }
    )
    return {"classes": classes, "predicates": predicates} if meta else {}


async def compute_fingerprints() -> dict[str, dict[str, list[str]]]:
    """Fingerprint every servable KG that exposes a curated entity CSV."""
    names = [k["shortname"] for k in registry.load_snapshot()]
    out: dict[str, dict[str, list[str]]] = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        for sn in names:
            fp = await _fingerprint(sn, client)
            if fp:
                out[sn] = fp
    return out


def diff_fingerprints(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Report KGs whose fingerprint differs from the baseline.

    Each reported entry is ``{reason, added, removed}`` where ``added``/``removed``
    are ``{"classes": [...], "predicates": [...]}`` deltas (live minus baseline and
    vice versa). ``reason`` is ``new`` (no baseline yet), ``changed`` (schema moved),
    or ``csv_removed`` (KG had a baseline CSV that no longer resolves).
    """
    report: dict[str, dict[str, Any]] = {}
    for sn, fp in current.items():
        base = baseline.get(sn)
        if base is None:
            report[sn] = {"reason": "new", "added": fp, "removed": {}}
            continue
        added = {
            kind: sorted(set(fp.get(kind, [])) - set(base.get(kind, [])))
            for kind in ("classes", "predicates")
        }
        removed = {
            kind: sorted(set(base.get(kind, [])) - set(fp.get(kind, [])))
            for kind in ("classes", "predicates")
        }
        if any(added.values()) or any(removed.values()):
            report[sn] = {"reason": "changed", "added": added, "removed": removed}
    for sn in baseline:
        if sn not in current:
            report[sn] = {"reason": "csv_removed", "added": {}, "removed": baseline[sn]}
    return report


def _fmt_delta(label: str, delta: dict[str, list[str]]) -> list[str]:
    lines = []
    for kind in ("classes", "predicates"):
        items = delta.get(kind) or []
        if items:
            lines.append(f"    {label} {kind}: {', '.join(items)}")
    return lines


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update",
        action="store_true",
        help="accept the current live schemas as the new committed baseline",
    )
    args = parser.parse_args()

    current = await compute_fingerprints()

    if args.update:
        with BASELINE.open("w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        print(f"wrote schema fingerprints for {len(current)} KGs to {BASELINE}")
        return 0

    if not BASELINE.exists():
        print(
            f"no baseline at {BASELINE}; run with --update to create it once you've "
            "reviewed the current payload tags."
        )
        return 1

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    report = diff_fingerprints(baseline, current)
    if not report:
        print(f"no schema drift: {len(current)} KG fingerprints match the baseline.")
        return 0

    print(f"SCHEMA DRIFT in {len(report)} KG(s) — re-review their payload tags:\n")
    for sn in sorted(report):
        entry = report[sn]
        tags = payloads.payloads_for(sn)
        print(f"  {sn}  [{entry['reason']}]  current tags: {tags}")
        for line in _fmt_delta("+", entry["added"]):
            print(line)
        for line in _fmt_delta("-", entry["removed"]):
            print(line)
    print(
        "\nRe-ground the affected tags in metadata/kg_payloads.json, then run "
        "scripts/refresh_snapshot.py and this script with --update to accept the new "
        "baseline."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

"""Regenerate the bundled KG snapshot from the live okn-registry, and sync the
precomputed crosswalk table from its editable source.

Run when the registry changes or `metadata/crosswalks.json` is edited:

    uv run python scripts/refresh_snapshot.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from mcp_okn import registry

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "mcp_okn" / "data"
OUT = DATA / "kgs.json"
CROSSWALK_SRC = ROOT / "metadata" / "crosswalks.json"
CROSSWALK_OUT = DATA / "crosswalks.json"
PAYLOAD_SRC = ROOT / "metadata" / "kg_payloads.json"
PAYLOAD_OUT = DATA / "kg_payloads.json"


def sync_crosswalks(known: set[str]) -> None:
    """Copy metadata/crosswalks.json into the package and validate it.

    The editable source of record lives in metadata/; the bundled copy is what
    ships in the wheel. Every KG the table names (bridges included) must be a
    real, servable shortname, or a join recipe would point at nothing.
    """
    if not CROSSWALK_SRC.exists():
        print(f"no crosswalk source at {CROSSWALK_SRC}; skipping")
        return
    data = json.loads(CROSSWALK_SRC.read_text(encoding="utf-8"))
    referenced: set[str] = set()
    for e in data.get("verified_crosswalks", []):
        for key in ("left_kg", "right_kg", "bridge_kg"):
            if e.get(key):
                referenced.add(e[key])
        referenced.update(e.get("members", []))
    # The NCBITaxon hub names its members and per-pair counts on real KGs too.
    hub = data.get("taxon_hub", {})
    referenced.update(hub.get("members", []))
    for rec in hub.get("pairwise", []):
        referenced.update(k for k in (rec.get("kg_a"), rec.get("kg_b")) if k)
    unknown = referenced - known
    assert not unknown, f"crosswalk table names unknown KGs: {sorted(unknown)}"
    with CROSSWALK_OUT.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(
        f"synced {len(data.get('verified_crosswalks', []))} crosswalks to "
        f"{CROSSWALK_OUT}"
    )


def sync_payloads(known: set[str]) -> None:
    """Copy metadata/kg_payloads.json into the package and validate it.

    The editable source of record lives in metadata/; the bundled copy is what
    ships in the wheel. Every tagged KG must be a real, servable shortname, every
    servable KG must carry a payload entry, and every tag must be a defined
    vocabulary term — or the reverse capability index would point at nothing.
    """
    if not PAYLOAD_SRC.exists():
        print(f"no payload source at {PAYLOAD_SRC}; skipping")
        return
    data = json.loads(PAYLOAD_SRC.read_text(encoding="utf-8"))
    vocab = set(data.get("vocabulary", {}))
    payloads = data.get("payloads", {})
    unknown_kgs = set(payloads) - known
    assert not unknown_kgs, f"payload table names unknown KGs: {sorted(unknown_kgs)}"
    missing = known - set(payloads)
    assert not missing, f"servable KGs missing a payload entry: {sorted(missing)}"
    bad_tags = {t for tags in payloads.values() for t in tags if t not in vocab}
    assert not bad_tags, f"payload tags not in vocabulary: {sorted(bad_tags)}"
    with PAYLOAD_OUT.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"synced {len(payloads)} KG payload entries to {PAYLOAD_OUT}")


async def main() -> None:
    kgs = await registry.list_kgs(refresh=True)
    kgs.sort(key=lambda k: k["shortname"])
    assert all("sparql" not in k and "tpf" not in k for k in kgs), "endpoint leaked!"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(kgs, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(kgs)} KGs to {OUT}")
    known = {k["shortname"] for k in kgs}
    sync_crosswalks(known)
    sync_payloads(known)


if __name__ == "__main__":
    asyncio.run(main())

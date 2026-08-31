"""KG discovery tools: list_kgs, describe_kg, get_server_info."""

from __future__ import annotations

from typing import Any

from .. import __version__, payloads, registry, schema, void
from ..app import mcp
from ..build_info import build_id
from ..sparql import FEDERATION_ENDPOINT, SparqlError


def _display_profile_value(value: Any) -> str:
    """Format one compact VoID profile value for Markdown."""
    return f"{value:,}" if isinstance(value, int) else str(value or "not recorded")


@mcp.tool()
async def get_server_info() -> dict[str, Any]:
    """Identify THIS server: `{service, version, build, sparql_endpoint}`.

    `build` is the deployed commit (`unknown` if unidentifiable). The version alone
    can't tell two deployments apart, so call this when a tool or argument seems to
    be missing — a hosted server can lag the repo — or to record exactly which build
    produced a result.
    """
    return {
        "service": mcp.name,
        "version": __version__,
        "build": build_id(),
        "sparql_endpoint": FEDERATION_ENDPOINT,
    }


@mcp.tool()
async def list_kgs() -> list[dict[str, Any]]:
    """List all Proto-OKN knowledge graphs available on the OKN federation.

    Returns one entry per KG with its `shortname`, `title`, `description`,
    `homepage`, the `named_graph` URI to use inside `GRAPH <...> { ... }` blocks,
    and a `payload` list — the curated context types that KG SUPPLIES (e.g.
    `digcfdekg` → `["gene", "gene_set", "trait", "disease"]`, `prokn` → `["protein",
    "gene", "GO", "Reactome", "pathway", ...]`). The `payload` tags say what a graph
    adds, not just how it joins — judge a graph by them, NOT by its name (a graph
    named for one thing often carries much more). To go the other way — "which KGs
    SUPPLY pathway/GO/trait for a gene I can join on Entrez?" — call
    `find_context_sources(want=[...], join_key=...)`.

    Use the descriptions to decide which graph(s) to query. If these one-line
    descriptions are too terse to tell which KG a question targets, call
    `describe_kg(shortname, long_description=True)` on the candidates for the
    registry's ~150-word prose description before choosing.
    """
    kgs = await registry.list_kgs()
    # Enrich at serve time rather than baking into the snapshot: kgs.json is
    # regenerated from the live registry, which would wipe a hand-curated field.
    return [{**kg, "payload": payloads.payloads_for(kg["shortname"])} for kg in kgs]


@mcp.tool()
async def describe_kg(
    shortname: str,
    long_description: bool = False,
    include_profile: bool = False,
) -> str:
    """Return registry documentation for one KG.

    Args:
        shortname: The KG shortname (e.g. `prokn`, `sawgraph`, `ubergraph`),
            as returned by `list_kgs`.
        long_description: If True, return ONLY the registry's free-text
            description — the ~150-word prose below the YAML frontmatter — instead
            of the full markdown. Reach for this when the one-line `list_kgs`
            descriptions are too terse to tell which KG a question belongs to:
            the longer prose usually names the entities, sources, and scope that
            disambiguate near-overlapping graphs.
        include_profile: If True, append a compact LIVE dataset profile from the
            `okn-void` graph: version, last load time, total triples, and observed
            class/property counts. False by default so registry-only discovery
            stays instant and independent of the federation endpoint.

    Returns the registry markdown (title, description, and prose) for deeper
    context before writing a query — or just the long description when
    `long_description` is set. For KGs with query-time domain rules the registry
    prose does not cover (e.g. `spoke-genelab`'s spaceflight assay-comparison
    rules), the relevant guidance is appended to the returned text.
    """
    if long_description:
        doc = await registry.fetch_kg_long_description(shortname)
    else:
        doc = await registry.fetch_kg_doc(shortname)

    if include_profile:
        try:
            profile = await void.fetch_profile(shortname)
        except SparqlError as exc:
            profile_text = f"Dataset profile unavailable: {str(exc).splitlines()[0]}"
        else:
            if profile is None:
                profile_text = "No VoID dataset profile is recorded for this graph."
            else:
                profile_text = "\n".join(
                    [
                        (
                            "- **Version:** "
                            f"{_display_profile_value(profile.get('version'))}"
                        ),
                        (
                            "- **Last updated:** "
                            f"{_display_profile_value(profile.get('last_updated'))}"
                        ),
                        (
                            "- **Triples:** "
                            f"{_display_profile_value(profile.get('triple_count'))}"
                        ),
                        (
                            "- **Observed classes:** "
                            f"{_display_profile_value(profile.get('class_count'))}"
                        ),
                        (
                            "- **Observed predicates:** "
                            f"{_display_profile_value(profile.get('predicate_count'))}"
                        ),
                    ]
                )
        doc = f"{doc}\n\n## Dataset profile (VoID)\n\n{profile_text}"

    notes = schema.usage_notes(shortname)
    if notes is not None:
        doc = (
            f"{doc}\n\n## Assay-comparison rules ({shortname})\n\n"
            f"{notes['guidance']}\n\n"
            f"(A reusable comparability-signature SPARQL query is returned as "
            f'`usage_notes.query_snippet` by `get_schema("{shortname}")`.)'
        )
    return doc


@mcp.tool()
async def get_kg_version(shortname: str | None = None) -> dict[str, Any]:
    """Return a KG's release version and last-updated date (from the VoID metadata).

    The `okn-void` meta-graph records provenance for each loaded KG. This tool
    reads it live and returns, per KG:
      * `version` — the release string, e.g. `"v0.0.5"` (`pav:version`);
      * `last_updated` — an ISO-8601 timestamp of the last load
        (`pav:lastUpdatedOn`), e.g. `"2026-06-23T14:26:02.126+00:00"`;
      * `named_graph` — the KG's federation named-graph URI.

    Use it to check how current a graph is, cite the exact version behind an
    analysis, or compare release freshness across graphs.

    Args:
        shortname: a KG shortname (as from `list_kgs`). Omit to return the
            provenance for EVERY KG that records it, sorted by shortname.

    Returns (shortname given) a single record dict, or `{"shortname", "version":
    None, "note": ...}` when that KG records no VoID provenance (a few, e.g.
    `bio101` and `wikidata`, do not). Returns (shortname omitted) `{"count",
    "versions": [record, ...]}`.
    """
    records = await void.fetch_versions(shortname)
    if shortname is not None:
        if records:
            return records[0]
        return {
            "shortname": shortname,
            "version": None,
            "note": (
                f"No VoID provenance recorded for '{shortname}' in the okn-void "
                "graph (some KGs, e.g. bio101 and wikidata, do not publish version "
                "metadata). Check the shortname with `list_kgs` if unexpected."
            ),
        }
    return {"count": len(records), "versions": records}

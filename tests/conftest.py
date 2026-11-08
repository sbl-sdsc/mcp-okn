"""Shared test setup."""

import pytest

from mcp_okn import diagnose


@pytest.fixture(autouse=True)
def no_live_diagnosis(monkeypatch):
    """Keep the zero-row diagnosis off the network.

    ``sparql_query`` diagnoses every empty result by probing the endpoint. Tests
    that stub ``run_sparql`` for the query itself would otherwise send those probes
    for real. Each probe here fails, so the diagnosis comes back empty; tests of
    the diagnosis patch ``diagnose.run_sparql`` themselves.
    """

    async def offline(*args, **kwargs):
        raise RuntimeError("no network in tests")

    monkeypatch.setattr(diagnose, "run_sparql", offline)

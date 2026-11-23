"""The endpoint handed to users must be reachable outside the server's cluster."""

from __future__ import annotations

import pytest

from mcp_okn import sparql

PUBLIC = "https://apps.okn.us/federation/sparql"


@pytest.mark.parametrize(
    ("internal", "explicit", "expected"),
    [
        # Hosted deployment: in-cluster service name → public endpoint.
        ("http://frink-federation-qlever-server:7001", "", PUBLIC),
        ("http://localhost:7001", "", PUBLIC),
        # A public endpoint is passed through unchanged.
        (PUBLIC, "", PUBLIC),
        ("https://other.example.org/sparql", "", "https://other.example.org/sparql"),
        # OKN_PUBLIC_ENDPOINT always wins.
        (
            "http://frink-federation-qlever-server:7001",
            "https://x.org/q",
            "https://x.org/q",
        ),
    ],
)
def test_public_endpoint(monkeypatch, internal, explicit, expected):
    monkeypatch.setattr(sparql, "FEDERATION_ENDPOINT", internal)
    monkeypatch.setenv("OKN_PUBLIC_ENDPOINT", explicit)
    assert sparql._public_endpoint() == expected

import httpx
import pytest

from mcp_okn import sparql as sparql_mod
from mcp_okn.server import _to_uri
from mcp_okn.sparql import (
    SparqlError,
    _flatten_bindings,
    _shared_client,
    aclose_shared_client,
    canonicalize_schema_org_iri,
    named_graph,
    normalize_schema_org,
    run_sparql,
)

_OK_BODY = '{"head":{"vars":[]},"results":{"bindings":[]}}'


class _Resp:
    """Minimal stand-in for an httpx.Response."""

    def __init__(self, status_code=200, text=_OK_BODY, headers=None):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def json(self):
        return {"head": {"vars": []}, "results": {"bindings": []}}


class _CaptureClient:
    """Fake httpx client that records the query sent to the endpoint."""

    def __init__(self):
        self.query = None

    async def post(self, url, data=None, headers=None, timeout=None):
        self.query = data["query"]
        return _Resp()


class _ScriptedClient:
    """Fake client that replays a scripted sequence of responses/exceptions.

    Counts calls so a test can assert how many times a query was actually sent.
    """

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = 0
        self.closed = False

    async def post(self, url, data=None, headers=None, timeout=None):
        self.calls += 1
        item = self.responses[min(self.calls, len(self.responses)) - 1]
        if isinstance(item, Exception):
            raise item
        return item

    async def aclose(self):
        self.closed = True


@pytest.fixture(autouse=True)
def no_real_sleep(monkeypatch):
    """Retry backoff must not slow the suite; record what it would have waited."""
    waits = []

    async def fake_sleep(seconds):
        waits.append(seconds)

    monkeypatch.setattr(sparql_mod, "_sleep", fake_sleep)
    return waits


JSON_RESULT = {
    "head": {"vars": ["s", "n", "active"]},
    "results": {
        "bindings": [
            {
                "s": {"type": "uri", "value": "http://example.org/x"},
                "n": {
                    "type": "literal",
                    "value": "42",
                    "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                },
                "active": {
                    "type": "literal",
                    "value": "false",
                    "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                },
            }
        ]
    },
}


def test_flatten_bindings_casts_types():
    rows = _flatten_bindings(JSON_RESULT)
    assert rows == [{"s": "http://example.org/x", "n": 42, "active": False}]


def test_flatten_bindings_empty():
    assert _flatten_bindings({"results": {"bindings": []}}) == []


def test_named_graph():
    assert named_graph("prokn") == "https://purl.org/okn/frink/kg/prokn"


def test_normalize_schema_org_rewrites_bracketed_iris():
    q = "SELECT ?x WHERE { ?x a <https://schema.org/Person> ; <https://schema.org/name> ?n }"
    out = normalize_schema_org(q)
    assert "https://schema.org/" not in out
    assert out.count("http://schema.org/") == 2


def test_normalize_schema_org_preserves_literals_and_concat():
    # The escape hatches for reaching https-stored schema.org data (nikg etc.) must
    # NOT be rewritten: only angle-bracketed IRIs are canonicalized.
    q = (
        "SELECT ?o WHERE { ?s ?p ?o . "
        'FILTER(STR(?p) = "https://schema.org/location") . '
        'BIND(IRI(CONCAT("https://schema.org/", "location")) AS ?pred) }'
    )
    assert normalize_schema_org(q) == q  # no bracketed IRI -> untouched
    # a bracketed predicate alongside a literal: only the bracket form flips
    q2 = '{ ?s <https://schema.org/location> ?o . FILTER(STRENDS(STR(?o),"https://schema.org/x")) }'
    out = q2.replace("<https://schema.org/location>", "<http://schema.org/location>")
    assert normalize_schema_org(q2) == out
    assert '"https://schema.org/x"' in normalize_schema_org(q2)  # literal kept


def test_normalize_schema_org_leaves_http_and_other_uris_untouched():
    q = (
        "SELECT ?x WHERE { ?x a <http://schema.org/Person> ; "
        "<https://purl.org/okn/frink/kg/x> ?y }"
    )
    # Already-http schema.org and the unrelated https purl.org URI are unchanged.
    assert normalize_schema_org(q) == q


async def test_run_sparql_normalize_schema_toggle():
    q = "SELECT ?x WHERE { ?x <https://schema.org/name> ?n }"

    on = _CaptureClient()
    await run_sparql(q, client=on, normalize_schema=True)
    assert "<http://schema.org/name>" in on.query  # canonicalized by default

    off = _CaptureClient()
    await run_sparql(q, client=off, normalize_schema=False)
    assert "<https://schema.org/name>" in off.query  # left as written for https KGs


async def test_retries_transient_status_then_succeeds(no_real_sleep):
    """A 429 is the endpoint's operation limit — transient, and the same query
    commonly succeeds moments later (crosswalks.json records skeletons that failed
    two runs in three). Retry rather than handing back an unactionable failure."""
    client = _ScriptedClient(_Resp(429), _Resp(200))
    out = await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client)
    assert out["row_count"] == 0  # the successful second attempt's result
    assert client.calls == 2
    assert len(no_real_sleep) == 1  # backed off once, between the two attempts


async def test_retries_are_bounded_and_report_the_attempts():
    """Retries stop at their budget, and the error says how many times we tried —
    so "endpoint still overloaded" reads differently from "your query is wrong".
    A quick gateway failure (an endpoint restart) gets the longer gateway budget."""
    client = _ScriptedClient(*[_Resp(503)] * 8)
    with pytest.raises(SparqlError) as excinfo:
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client)
    assert client.calls == 5  # the initial attempt + 4 gateway retries
    assert "after 5 attempts" in str(excinfo.value)


async def test_max_retries_zero_disables_gateway_retries():
    client = _ScriptedClient(_Resp(503), _Resp(200))
    with pytest.raises(SparqlError):
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client, max_retries=0)
    assert client.calls == 1


async def test_gateway_html_is_reduced_to_its_title():
    body = "<html><head><title>502 Bad Gateway</title></head><body>nginx</body></html>"
    client = _ScriptedClient(*[_Resp(502, text=body)] * 8)
    with pytest.raises(SparqlError) as excinfo:
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client)
    assert "502 Bad Gateway" in str(excinfo.value)
    assert "<html>" not in str(excinfo.value)


def test_error_summary_drops_the_echoed_query():
    from mcp_okn.sparql import error_summary

    exc = SparqlError("SPARQL endpoint returned HTTP 400: bad\nQuery:\nSELECT 1")
    assert error_summary(exc) == "SPARQL endpoint returned HTTP 400: bad"


def test_all_unbound_row_is_an_empty_row():
    from mcp_okn.sparql import _flatten_bindings

    payload = {
        "results": {"bindings": [None, {"x": {"type": "literal", "value": "1"}}]}
    }
    assert _flatten_bindings(payload) == [{}, {"x": "1"}]


async def test_429_gets_a_single_retry_however_high_max_retries_is():
    """429 is QLever's "Operation timed out" and takes ~30s to come back (measured
    against the live endpoint), so its retry budget is 1 — enough to rescue a query
    sitting right at the limit, without spending 90s on one that never fits."""
    client = _ScriptedClient(_Resp(429), _Resp(429), _Resp(429), _Resp(429))
    with pytest.raises(SparqlError):
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client, max_retries=5)
    assert client.calls == 2  # the initial attempt + exactly one retry
    # A gateway status returns immediately, so it keeps the full budget.
    gateway = _ScriptedClient(_Resp(502), _Resp(502), _Resp(502), _Resp(502))
    with pytest.raises(SparqlError):
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=gateway, max_retries=3)
    assert gateway.calls == 5  # a quick gateway failure gets at least 4 retries


async def test_query_error_is_not_retried():
    """QLever reports query errors as 400 with an `exception` body. That is
    deterministic, so retrying only doubles the wait before the same failure."""
    body = '{"exception": "Read-only file system"}'
    client = _ScriptedClient(_Resp(400, body), _Resp(200))
    with pytest.raises(SparqlError) as excinfo:
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client)
    assert client.calls == 1
    assert "Read-only file system" in str(excinfo.value)
    assert "attempts" not in str(excinfo.value)  # no retries happened, so none named


async def test_timeout_is_not_retried():
    """A timeout means the scan was too broad; a retry burns another `timeout`
    seconds to fail identically. The message points at narrowing the query."""
    client = _ScriptedClient(httpx.ReadTimeout("too slow"), _Resp(200))
    with pytest.raises(SparqlError) as excinfo:
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client, timeout=1.0)
    assert client.calls == 1
    assert "scanned too much" in str(excinfo.value)
    assert "lookup_term" in str(excinfo.value)


class _DataClient(_CaptureClient):
    async def post(self, url, data=None, headers=None, timeout=None):
        self.data, self.http_timeout = data, timeout
        return _Resp()


async def test_server_side_timeout_is_sent():
    """QLever stops the scan itself when the request carries `timeout=<n>s`."""
    client = _DataClient()
    await run_sparql("SELECT * {}", client=client, timeout=42)
    assert client.data["timeout"] == "42s"
    assert client.http_timeout > 42  # the HTTP wait outlasts the server limit


async def test_default_timeout_is_below_common_client_limits():
    client = _DataClient()
    await run_sparql("SELECT * {}", client=client)
    assert client.data["timeout"] == f"{round(sparql_mod.DEFAULT_TIMEOUT)}s"
    assert client.http_timeout < 120


async def test_429_at_the_limit_is_not_retried(monkeypatch):
    """A 429 arriving after the full limit is QLever enforcing OUR timeout; the
    same query would hit it again, so fail fast with the rewrite advice."""
    clock = iter([0.0, 50.0])
    monkeypatch.setattr(sparql_mod, "_now", lambda: next(clock))
    client = _ScriptedClient(_Resp(429), _Resp(200))
    with pytest.raises(SparqlError) as excinfo:
        await run_sparql("SELECT * {}", client=client, timeout=50)
    assert client.calls == 1
    assert "Operation timed out" in str(excinfo.value)
    assert "scanned too much" in str(excinfo.value)


async def test_max_retries_zero_disables_retrying():
    client = _ScriptedClient(_Resp(429), _Resp(200))
    with pytest.raises(SparqlError):
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client, max_retries=0)
    assert client.calls == 1


async def test_retry_after_header_is_honoured_and_capped(no_real_sleep):
    """A server-supplied Retry-After wins over the backoff schedule, but is capped so
    one absurd value can't stall a tool call for minutes."""
    client = _ScriptedClient(_Resp(429, headers={"retry-after": "3"}), _Resp(200))
    await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=client)
    assert no_real_sleep == [3.0]

    no_real_sleep.clear()
    huge = _ScriptedClient(_Resp(429, headers={"retry-after": "9999"}), _Resp(200))
    await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=huge)
    assert no_real_sleep == [sparql_mod._MAX_RETRY_AFTER]


async def test_shared_client_is_reused_and_callers_client_is_not_closed():
    """Each query used to build its own AsyncClient — a TLS handshake per query, and
    find_crosswalks alone fires three at once. One client per loop, kept open."""
    try:
        first = _shared_client(30.0)
        assert _shared_client(30.0) is first  # same loop -> same client
        assert not first.is_closed

        mine = _ScriptedClient(_Resp(200))
        await run_sparql("SELECT * WHERE { ?s ?p ?o }", client=mine)
        assert not mine.closed  # a caller-supplied client is the caller's to close
        assert not first.is_closed  # ...and the shared one survives a query
    finally:
        await aclose_shared_client()


def test_canonicalize_schema_org_iri_rewrites_bare_iri():
    assert (
        canonicalize_schema_org_iri("https://schema.org/about")
        == "http://schema.org/about"
    )
    # non-schema.org IRIs and the already-http form are untouched
    assert (
        canonicalize_schema_org_iri("http://schema.org/about")
        == "http://schema.org/about"
    )
    assert canonicalize_schema_org_iri("https://w3id.org/x") == "https://w3id.org/x"


@pytest.mark.parametrize(
    "term,expected",
    [
        ("MONDO:0003847", "http://purl.obolibrary.org/obo/MONDO_0003847"),
        ("CHEBI:24431", "http://purl.obolibrary.org/obo/CHEBI_24431"),
        (
            "http://purl.obolibrary.org/obo/GO_0008150",
            "http://purl.obolibrary.org/obo/GO_0008150",
        ),
        ("up:Disease", "up:Disease"),  # non-OBO prefix passes through unchanged
    ],
)
def test_to_uri(term, expected):
    assert _to_uri(term) == expected


def test_tsv_accept_header_is_the_registered_media_type():
    # The endpoint rejects the unregistered `text/tsv` with HTTP 406; the IANA
    # type is text/tab-separated-values (PR #7).
    assert sparql_mod._ACCEPT["tsv"] == "text/tab-separated-values"


async def test_ask_answer_is_one_row_not_an_empty_result():
    class _AskResp(_Resp):
        def json(self):
            return {"head": {}, "boolean": True}

    out = await run_sparql("ASK { ?s ?p ?o }", client=_ScriptedClient(_AskResp()))
    assert out == {"vars": ["boolean"], "rows": [{"boolean": True}], "row_count": 1}


async def test_run_sparql_prefilters_iri_prefix_tests_by_default():
    q = (
        "SELECT ?x WHERE { ?s ?p ?x "
        "FILTER(STRSTARTS(STR(?x), 'http://purl.obolibrary.org/obo/MONDO_')) }"
    )
    on = _CaptureClient()
    await run_sparql(q, client=on)
    assert "isLiteral(?x)" in on.query  # the block-skipping range was added

    off = _CaptureClient()
    await run_sparql(q, client=off, prefilter=False)
    assert off.query == q

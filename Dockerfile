# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv for fast dependency resolution + build.
# git: uv.lock pins sparql-to-mermaid to a git tag (see [tool.uv.sources]).
RUN pip install --no-cache-dir uv \
 && apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only what is needed to install the package.
# README.md is required by hatchling (declared as readme in pyproject.toml).
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY metadata/ ./metadata

# Install the project + locked deps system-wide.
# `uv sync` (not build-a-wheel-then-pip-install) because wheel metadata drops
# [tool.uv.sources] — the git-pinned sparql-to-mermaid would resolve from PyPI and 404.
# --no-editable so the install doesn't point back at /build, which stage 2 never copies.
ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN uv sync --frozen --no-dev --no-editable --no-cache

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="mcp-okn" \
      org.opencontainers.image.description="MCP server for the FRINK federated SPARQL endpoint over Proto-OKN knowledge graphs" \
      org.opencontainers.image.source="https://github.com/sbl-sdsc/mcp-okn"

# curl for the HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --shell /bin/bash mcp

# Copy installed packages + console script from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin/mcp-okn /usr/local/bin/mcp-okn

USER mcp
WORKDIR /home/mcp

# ── Configuration ──────────────────────────────────────────────────────────────
# FastMCP's FASTMCP_* env vars don't reliably bind host; set it on the settings
# object in CMD instead. Override host/port via MCP_HOST / MCP_PORT.
ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    # Trust forwarded headers from any upstream (ingress/gateway/nginx/traefik).
    UVICORN_FORWARDED_ALLOW_IPS="*"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8000/mcp || exit 1

# The console script `mcp-okn` runs stdio only; start the HTTP transport directly.
# ponytail: host/port set inline because FASTMCP_HOST env doesn't take; DNS-rebinding
# protection disabled because the gateway/ingress sets a real Host (else MCP SDK 421s).
CMD ["python", "-c", "import os; from mcp_okn.server import mcp; from mcp.server.transport_security import TransportSecuritySettings; mcp.settings.host=os.environ.get('MCP_HOST','0.0.0.0'); mcp.settings.port=int(os.environ.get('MCP_PORT','8000')); mcp.settings.transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False); mcp.run(transport='streamable-http')"]

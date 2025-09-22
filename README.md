WeatherAgent MCP Server (production-ready basics)

Quickstart

```bash
# Windows PowerShell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run (dev)
$env:RELOAD="true"; $env:LOG_LEVEL="INFO"; python server.py

# Or run via uvicorn directly
uvicorn server:app --host 0.0.0.0 --port 8000 --log-level info
```

Environment variables

- LOG_LEVEL: debug|info|warning|error (default: info)
- REQUEST_TIMEOUT_SECONDS: outbound HTTP timeout (default: 10.0)
- HTTP_MAX_RETRIES: retry attempts excluding the first try (default: 2)
- HTTP_BACKOFF_SECONDS: base backoff seconds for exponential backoff (default: 0.5)
- GEOCODE_CACHE_TTL_SECONDS: seconds to cache geocoding results (default: 3600)
- FORECAST_CACHE_TTL_SECONDS: seconds to cache forecast results (default: 300)
- SERVICE_VERSION: service version string (default: 1.0.0)
- HOST/PORT: binding for the __main__ runner (defaults: 0.0.0.0:8000)

Tools exposed

- weather(query, units): returns current weather for a location
- health(): readiness/liveness with version and timestamp

Production notes

- Process-local in-memory caches are provided; for multi-instance deployments use Redis or Memcached.
- Retries with exponential backoff and request timeouts are configured.
- Add HTTP proxy and TLS settings as needed via environment or httpx client options.
- For containerization, expose port 8000 and run with: uvicorn server:app --workers 2 --host 0.0.0.0 --port 8000
# hello-mcp (Weather Agent)

Minimal Model Context Protocol (MCP) project with a FastMCP server exposing a `weather` tool that fetches current conditions from Open-Meteo, plus a simple HTTP client.

## Prerequisites

- Python 3.13 (see `.python-version`)
- On Windows PowerShell

## Install

Create and activate a virtual environment (optional) and install dependencies via uv:

```powershell
uv venv .venv
./.venv/Scripts/Activate.ps1
uv sync
```

This uses `pyproject.toml` with dependencies: `mcp`, `httpx`, `uvicorn`.

## Run the MCP server

Start the ASGI server with uvicorn:

```powershell
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

You should see uvicorn start. The MCP stateless HTTP endpoint is served under `/mcp/`.

## Try the client

In a separate terminal (with the same venv activated):

```powershell
python client.py
```

You should see the list of tools and the result from calling the `weather` tool for Karachi.

## Project layout

- `server.py`: FastMCP server exposing a `weather` tool, exported as ASGI `app`.
- `client.py`: Simple HTTP client demonstrating `tools/list` and `tools/call`.
- `pyproject.toml`: Project metadata and dependencies.

## Notes

- If you get import errors for `mcp` or `httpx`, ensure the virtual environment is active and run `uv sync` again.
- The client uses the MCP stateless HTTP transport which streams responses as Server-Sent Events (SSE).


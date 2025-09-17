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


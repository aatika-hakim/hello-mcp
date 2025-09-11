# hello-mcp

Minimal Model Context Protocol (MCP) project with a FastMCP server and a simple async client.

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

You should see the list of tools and a call to the `greet` tool returning a greeting.

## Project layout

- `server.py`: FastMCP server with a `greet` tool, exported as ASGI `app`.
- `client.py`: Async httpx client demonstrating `tools/list` and `tools/call`.
- `main.py`: Simple entry for packaging examples.
- `pyproject.toml`: Project metadata and dependencies.

## Notes

- If you get import errors for `mcp` or `httpx`, ensure the virtual environment is active and run `uv sync` again.
- The client uses the MCP stateless HTTP transport which streams responses as Server-Sent Events (SSE).


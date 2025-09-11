from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from mcp.types import TextContent  # pyright: ignore[reportMissingImports]

# Initialize FastMCP server with enhanced metadata for 2025-06-18 spec
mcp = FastMCP(
    name="hello-server",
    stateless_http=True
)


@mcp.tool()
async def greet(name: str) -> list[TextContent]:
    """Return a friendly greeting for the provided name."""
    return [TextContent(type="text", text=f"Hello, {name}!")]


# Expose ASGI app for uvicorn
mcp_app = mcp.streamable_http_app()
app = mcp_app
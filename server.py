from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Initialize FastMCP server with enhanced metadata for 2025-06-18 spec
mcp = FastMCP(
    name="hello-server",
    stateless_http=True
)


mcp_app = mcp.streamable_http_app()
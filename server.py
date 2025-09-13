from mcp.server.fastmcp import FastMCP

# Create MCP sever
mcp = FastMCP(name ="Calculator" ,stateless_http=True)

mcp_app = mcp.streamable_http_app()

# # tool
# @mcp.tool()
# def add(a: int, b: int) -> int:
#     """Return the sum of two integers."""
#     return a + b

# # dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def greet(name: str) -> str:
#     """Return a friendly greeting for the provided name."""
#     return f"Hello, {name}!"




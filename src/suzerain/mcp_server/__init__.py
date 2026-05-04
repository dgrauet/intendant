"""Suzerain MCP server — expose audit/explain/report tools to MCP clients.

The handler functions in :mod:`suzerain.mcp_server.handlers` are plain Python
that returns JSON-serializable dicts. The :mod:`suzerain.mcp_server.server`
module wraps them with FastMCP for stdio transport.
"""

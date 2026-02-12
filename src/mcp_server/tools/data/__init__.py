"""Data processing plugin."""

import importlib
from typing import Any

from mcp_server.tools.registry import _TOOL_REGISTRY


def register_tools(mcp: Any) -> None:
    """Register all data tools to an MCP server instance."""
    module_path = f"{__package__}.handlers"
    importlib.import_module(module_path)
    for tool_func in _TOOL_REGISTRY.get(module_path, []):
        mcp.tool()(tool_func)

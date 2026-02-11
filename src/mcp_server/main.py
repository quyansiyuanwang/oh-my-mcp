"""
Comprehensive MCP Server with Practical Tools

This MCP server provides 74+ tools across multiple categories.
Tool counts and descriptions are dynamically loaded from each plugin.

Author: MCP Server Project
"""

import sys
from pathlib import Path
from typing import Any
from fastmcp import FastMCP

# Import tomllib for Python 3.11+ or fall back to tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

from mcp_server.tools import load_all_plugins
from mcp_server.utils import logger


def get_version() -> str:
    """Read version from pyproject.toml"""
    if tomllib is None:
        return "0.1.0"

    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.1.0")
    except Exception:
        return "0.1.0"


# Create the comprehensive MCP server
mcp = FastMCP("Comprehensive MCP Server with Practical Tools")

# Log startup
version = get_version()
logger.info("=" * 60)
logger.info(f"Starting Comprehensive MCP Server v{version}")
logger.info("=" * 60)

# Load and register all tool plugins
plugins = load_all_plugins()
logger.info(f"Discovered {len(plugins)} tool plugins")

for plugin in plugins:
    logger.info(f"Registering {plugin.category_name} plugin ({len(plugin.tools)} tools)...")
    plugin.register_to_mcp(mcp)


# Helper functions for resources
def get_all_tools_info() -> dict[str, Any]:
    """Get all tools information as a dictionary."""
    plugins = load_all_plugins()
    categories = {}
    total_tools = 0

    for plugin in plugins:
        category_key = plugin.name
        categories[category_key] = {
            "name": plugin.category_name,
            "description": plugin.category_description,
            "tool_count": len(plugin.tools),
            "tools": [tool.__name__ for tool in plugin.tools],
        }
        total_tools += len(plugin.tools)

    return {
        "server": {
            "name": "Comprehensive MCP Server",
            "version": get_version(),
            "description": f"MCP server with {total_tools}+ practical tools",
        },
        "categories": categories,
        "total_tools": total_tools,
    }


# Add server information resource
@mcp.resource("config://tools")
def list_all_tools() -> str:
    """List all available tools organized by category."""
    import json

    return json.dumps(get_all_tools_info(), indent=2)


def get_version_info() -> dict[str, Any]:
    """Get server version information as a dictionary."""
    plugins = load_all_plugins()
    total_tools = sum(len(plugin.tools) for plugin in plugins)

    # Build features list from plugin descriptions
    features = [plugin.category_description for plugin in plugins if plugin.category_description]

    return {
        "name": "Comprehensive MCP Server",
        "version": get_version(),
        "description": f"MCP server with {total_tools}+ practical tools across {len(plugins)} categories",
        "features": features,
        "total_tools": total_tools,
        "total_categories": len(plugins),
        "total_resources": 4,
    }


@mcp.resource("config://version")
def get_server_version() -> str:
    """Get server version and information."""
    import json

    return json.dumps(get_version_info(), indent=2)


logger.info("=" * 60)
logger.info("All tools and resources registered successfully!")
logger.info("Server ready to accept connections.")
logger.info("=" * 60)


def main() -> None:
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

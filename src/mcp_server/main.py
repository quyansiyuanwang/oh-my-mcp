"""
Comprehensive MCP Server with Practical Tools

This MCP server provides 74+ tools across 7 categories.
Tool counts and descriptions are dynamically loaded from each module.

Author: MCP Server Project
Version: 0.1.0
"""

from fastmcp import FastMCP

# Import all tool modules
from mcp_server.tools import (
    compression,
    web,
    file,
    data,
    text,
    system,
    utility,
    python,
    uv,
    pylance,
)
from mcp_server.utils import logger

# Define module registry with metadata
TOOL_MODULES = [
    {
        "module": compression,
        "category_key": "compression",
    },
    {
        "module": web,
        "category_key": "web_network",
    },
    {
        "module": file,
        "category_key": "file_system",
    },
    {
        "module": data,
        "category_key": "data_processing",
    },
    {
        "module": text,
        "category_key": "text_processing",
    },
    {
        "module": system,
        "category_key": "system",
    },
    {
        "module": utility,
        "category_key": "utilities",
    },
    {
        "module": python,
        "category_key": "python_development",
    },
    {
        "module": uv,
        "category_key": "uv_package_manager",
    },
    {
        "module": pylance,
        "category_key": "pylance_pyright",
    },
]

# Create the comprehensive MCP server
mcp = FastMCP("Comprehensive MCP Server")

# Log startup
logger.info("=" * 60)
logger.info("Starting Comprehensive MCP Server v0.1.0")
logger.info("=" * 60)

# Register all tools from each module dynamically
for module_info in TOOL_MODULES:
    module = module_info["module"]
    category_name = getattr(module, "CATEGORY_NAME", "Unknown")
    tool_count = len(getattr(module, "TOOLS", []))

    logger.info(f"Registering {category_name} tools ({tool_count} tools)...")
    module.register_tools(mcp)


# Helper functions for resources
def get_all_tools_info() -> dict:
    """Get all tools information as a dictionary."""
    # Build categories dynamically from module metadata
    categories = {}
    total_tools = 0

    for module_info in TOOL_MODULES:
        module = module_info["module"]
        category_key = module_info["category_key"]

        # Get metadata from module
        category_name = getattr(module, "CATEGORY_NAME", "Unknown")
        category_desc = getattr(module, "CATEGORY_DESCRIPTION", "")
        tools_list = getattr(module, "TOOLS", [])

        categories[category_key] = {
            "name": category_name,
            "description": category_desc,
            "count": len(tools_list),
            "tools": tools_list,
        }

        total_tools += len(tools_list)

    return {
        "server": {
            "name": "Comprehensive MCP Server",
            "version": "0.1.0",
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


def get_version_info() -> dict:
    """Get server version information as a dictionary."""
    # Calculate total tools dynamically
    total_tools = sum(len(getattr(m["module"], "TOOLS", [])) for m in TOOL_MODULES)

    # Build features list from module descriptions
    features = []
    for module_info in TOOL_MODULES:
        module = module_info["module"]
        category_desc = getattr(module, "CATEGORY_DESCRIPTION", "")
        if category_desc:
            features.append(category_desc)

    return {
        "name": "Comprehensive MCP Server",
        "version": "0.1.0",
        "description": f"MCP server with {total_tools}+ practical tools across {len(TOOL_MODULES)} categories",
        "features": features,
        "total_tools": total_tools,
        "total_categories": len(TOOL_MODULES),
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


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

"""
MCP Server Tools Package

This package provides automatic plugin discovery and loading for tool modules.
Each tool module is a self-contained plugin with its own configuration.
"""

import sys
from pathlib import Path
from typing import List

from mcp_server.utils import logger

from .registry import ToolPlugin, load_plugin_config


def _get_tools_dir() -> Path:
    """Get the tools directory, handling both normal and frozen (PyInstaller) modes."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as a PyInstaller bundle
        return Path(sys._MEIPASS) / "mcp_server" / "tools"
    else:
        return Path(__file__).parent


def discover_tool_plugins() -> List[Path]:
    """
    Discover all tool plugin directories.

    Scans the tools directory for subdirectories containing a config.yaml file.

    Returns:
        List of Path objects representing plugin directories
    """
    tools_dir = _get_tools_dir()
    plugin_dirs = []

    for item in tools_dir.iterdir():
        # Skip non-directories and special directories
        if not item.is_dir():
            continue
        if item.name.startswith("_") or item.name.startswith("."):
            continue

        # Check if this directory contains a config.yaml
        config_file = item / "config.yaml"
        if config_file.exists():
            plugin_dirs.append(item)
            logger.debug(f"Discovered plugin: {item.name}")

    return plugin_dirs


def load_all_plugins() -> List[ToolPlugin]:
    """
    Load all enabled tool plugins.

    Discovers plugins, loads their configurations, and initializes ToolPlugin instances.
    Disabled plugins (enabled: false in config) are skipped.

    Returns:
        List of loaded and enabled ToolPlugin instances
    """
    plugin_dirs = discover_tool_plugins()
    plugins = []

    for plugin_dir in plugin_dirs:
        try:
            # Load plugin configuration
            config = load_plugin_config(plugin_dir)

            # Check if plugin is enabled
            if not config.get("enabled", True):
                logger.info(f"Skipping disabled plugin: {plugin_dir.name}")
                continue

            # Create plugin instance
            plugin = ToolPlugin(plugin_dir, config)

            # Load tool handlers
            plugin.load_handlers()

            plugins.append(plugin)
            logger.info(f"Loaded plugin: {plugin.category_name} ({len(plugin.tools)} tools)")

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
            # Continue loading other plugins even if one fails
            continue

    return plugins


__all__ = ["load_all_plugins", "ToolPlugin"]

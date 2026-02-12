"""
Tool plugin registration framework.

This module provides the infrastructure for automatic tool discovery and registration.
"""

import importlib
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from mcp_server.utils import logger

# Global registry for tool handlers
_TOOL_REGISTRY: Dict[str, List[Callable[..., Any]]] = {}


def tool_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to mark a function as a tool handler.

    This decorator registers the function in the global tool registry,
    allowing it to be automatically discovered and registered with MCP.

    Args:
        func: The tool handler function to register

    Returns:
        The original function unchanged
    """
    module_name = func.__module__
    if module_name not in _TOOL_REGISTRY:
        _TOOL_REGISTRY[module_name] = []
    _TOOL_REGISTRY[module_name].append(func)
    return func


class ToolPlugin:
    """
    Represents a single tool plugin with its configuration and handlers.
    """

    def __init__(self, plugin_dir: Path, config: Dict[str, Any]):
        """
        Initialize a tool plugin.

        Args:
            plugin_dir: Path to the plugin directory
            config: Plugin configuration dictionary from config.yaml
        """
        self.plugin_dir = plugin_dir
        self.name = plugin_dir.name
        self.category_name = config.get("category_name", "Unknown")
        self.category_description = config.get("category_description", "")
        self.enabled = config.get("enabled", True)
        self.tools: List[Callable[..., Any]] = []
        self._handlers_module: Optional[Any] = None

    def load_handlers(self) -> None:
        """
        Dynamically import the handlers module and extract tool functions.
        """
        try:
            # Import the handlers module
            module_path = f"mcp_server.tools.{self.name}.handlers"
            self._handlers_module = importlib.import_module(module_path)

            # Extract tools from the global registry
            if module_path in _TOOL_REGISTRY:
                self.tools = _TOOL_REGISTRY[module_path]
                logger.debug(f"Loaded {len(self.tools)} tools from {self.name}")
            else:
                logger.warning(f"No tools found in {self.name}")

        except ImportError as e:
            logger.error(f"Failed to import handlers for {self.name}: {e}")
            raise

    def register_to_mcp(self, mcp: Any) -> None:
        """
        Register all tool handlers to the MCP server instance.

        Args:
            mcp: The FastMCP server instance
        """
        if not self.tools:
            logger.warning(f"No tools to register for {self.name}")
            return

        for tool_func in self.tools:
            # Register the tool with MCP using the decorator
            _decorated_func = mcp.tool()(tool_func)
            logger.debug(f"Registered tool: {tool_func.__name__}")


def load_plugin_config(plugin_dir: Path) -> Dict[str, Any]:
    """
    Load and parse the plugin configuration file.

    Args:
        plugin_dir: Path to the plugin directory

    Returns:
        Dictionary containing the plugin configuration

    Raises:
        FileNotFoundError: If config.yaml does not exist
        yaml.YAMLError: If config.yaml is invalid
    """
    config_path = plugin_dir / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError(f"Invalid config format in {config_path}")

        return config

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse config for {plugin_dir.name}: {e}")
        raise


def get_plugin_tools(module: Any) -> List[Callable[..., Any]]:
    """
    Extract all tool handler functions from a module.

    This function looks up the module in the global tool registry.

    Args:
        module: The imported module object

    Returns:
        List of tool handler functions
    """
    module_name = module.__name__
    return _TOOL_REGISTRY.get(module_name, [])

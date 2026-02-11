#!/usr/bin/env python3
"""Test configuration file tools"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import data_tools

class MockMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_config_tools():
    print("=" * 60)
    print("Testing Configuration File Tools (5 tools)")
    print("=" * 60)

    mcp = MockMCP()
    data_tools.register_tools(mcp)

    # Test YAML tools
    yaml_data = """
name: Test Project
version: 1.0.0
dependencies:
  - python>=3.12
  - fastmcp>=2.14.5
settings:
  debug: true
  port: 8080
"""

    print("\n1. Testing parse_yaml:")
    result = mcp.tools['parse_yaml'](yaml_data)
    print(f"   Result: {result[:120]}...")

    print("\n2. Testing yaml_to_json:")
    result = mcp.tools['yaml_to_json'](yaml_data, 2)
    print(f"   Result: {result[:120]}...")

    # Test JSON to YAML
    json_data = '{"name": "Test", "version": "1.0", "items": [1, 2, 3]}'

    print("\n3. Testing json_to_yaml:")
    result = mcp.tools['json_to_yaml'](json_data)
    print(f"   Result: {result[:100]}...")

    # Test TOML tools
    toml_data = """
[project]
name = "test-project"
version = "1.0.0"

[dependencies]
python = ">=3.12"
fastmcp = ">=2.14.5"

[settings]
debug = true
port = 8080
"""

    print("\n4. Testing parse_toml:")
    result = mcp.tools['parse_toml'](toml_data)
    print(f"   Result: {result[:120]}...")

    print("\n5. Testing toml_to_json:")
    result = mcp.tools['toml_to_json'](toml_data, 2)
    print(f"   Result: {result[:120]}...")

    print("\n[OK] Configuration file tools test completed")

if __name__ == "__main__":
    test_config_tools()

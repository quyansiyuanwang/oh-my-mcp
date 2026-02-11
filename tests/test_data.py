#!/usr/bin/env python3
"""Test remaining UV and Pylance tools"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.tools import uv, pylance

class MockMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_uv_tools():
    print("=" * 60)
    print("Testing UV Tools")
    print("=" * 60)

    mcp = MockMCP()
    uv_tools.register_tools(mcp)

    # Test 1: uv_init_project
    print("\n1. Test uv_init_project:")
    result = mcp.tools['uv_init_project']("./test_uv_project", "test-project")
    data = json.loads(result)
    print(f"   Success: {data.get('success')}")
    if 'error' in data:
        print(f"   Error: {data['error']}")
    else:
        print(f"   Project: {data.get('project_path')}")

    # Test 2: uv_run_command
    print("\n2. Test uv_run_command:")
    result = mcp.tools['uv_run_command']("python", ["--version"])
    data = json.loads(result)
    print(f"   Success: {data.get('success')}")
    if 'stdout' in data:
        print(f"   Output: {data['stdout'].strip()}")

def test_pylance_tools():
    print("\n" + "=" * 60)
    print("Testing Pylance Tools")
    print("=" * 60)

    mcp = MockMCP()
    pylance_tools.register_tools(mcp)

    # Create a test Python file
    test_file = Path("test_type_check.py")
    test_file.write_text("""
def add(x: int, y: int) -> int:
    return x + y

result = add(1, "2")  # Type error: should be int
""")

    # Test 1: pylance_check_file
    print("\n1. Test pylance_check_file:")
    result = mcp.tools['pylance_check_file'](str(test_file))
    data = json.loads(result)
    print(f"   Success: {data.get('success')}")
    if 'error' in data:
        print(f"   Error: {data['error']}")
    elif 'diagnostics' in data:
        print(f"   Found diagnostics")

    # Test 2: pylance_get_version
    print("\n2. Test pylance_get_version:")
    result = mcp.tools['pylance_get_version']()
    data = json.loads(result)
    print(f"   Success: {data.get('success')}")
    if 'version' in data:
        print(f"   Version: {data['version']}")
    if 'error' in data:
        print(f"   Error: {data['error']}")

    # Cleanup
    test_file.unlink(missing_ok=True)

if __name__ == "__main__":
    test_uv_tools()
    test_pylance_tools()
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

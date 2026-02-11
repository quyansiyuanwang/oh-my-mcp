#!/usr/bin/env python3
"""Test python_execute_code after stdin fix"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import python_tools

class MockMCP:
    """Mock MCP server for testing"""
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_python_execute_code():
    """Test python_execute_code with simple code"""
    print("=" * 60)
    print("Testing python_execute_code")
    print("=" * 60)

    mcp = MockMCP()
    python_tools.register_tools(mcp)

    # Test 1: Simple print statement
    print("\n1. Test simple print:")
    code1 = "print('Hello from Python!')"
    result1 = mcp.tools['python_execute_code'](code1, timeout=10, safe_mode=True)
    data1 = json.loads(result1)
    print(f"   Success: {data1.get('success')}")
    print(f"   Stdout: {data1.get('stdout', '').strip()}")
    print(f"   Execution time: {data1.get('execution_time', 0):.2f}s")

    # Test 2: Math calculation
    print("\n2. Test math calculation:")
    code2 = """
result = 2 + 2
print(f'2 + 2 = {result}')
"""
    result2 = mcp.tools['python_execute_code'](code2, timeout=10, safe_mode=True)
    data2 = json.loads(result2)
    print(f"   Success: {data2.get('success')}")
    print(f"   Stdout: {data2.get('stdout', '').strip()}")
    print(f"   Execution time: {data2.get('execution_time', 0):.2f}s")

    # Test 3: Safe mode blocking
    print("\n3. Test safe mode (should block os import):")
    code3 = "import os\nprint(os.getcwd())"
    result3 = mcp.tools['python_execute_code'](code3, timeout=10, safe_mode=True)
    data3 = json.loads(result3)
    print(f"   Has error: {'error' in data3}")
    if 'error' in data3:
        print(f"   Error: {data3['error']}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_python_execute_code()

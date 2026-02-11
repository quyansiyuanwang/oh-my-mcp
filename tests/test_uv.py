#!/usr/bin/env python3
"""Test python_format_code"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import python_tools

class MockMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_format_code():
    print("=" * 60)
    print("Testing python_format_code")
    print("=" * 60)

    mcp = MockMCP()
    python_tools.register_tools(mcp)

    # Test with unformatted code
    code = """
def hello(  x,y  ):
    return x+y
"""

    print("\nOriginal code:")
    print(code)

    print("\nTesting black formatter...")
    result = mcp.tools['python_format_code'](code, style="black")
    data = json.loads(result)

    if 'error' in data:
        print(f"   Error: {data['error']}")
    elif 'warning' in data:
        print(f"   Warning: {data['warning']}")
        print(f"   (black not installed, returned original code)")
    else:
        print(f"   Formatted code:")
        print(data.get('formatted_code', ''))

if __name__ == "__main__":
    test_format_code()

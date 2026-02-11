#!/usr/bin/env python3
"""Test security tools"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import utility_tools

class MockMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_security_tools():
    print("=" * 60)
    print("Testing Security Tools (2 tools)")
    print("=" * 60)

    mcp = MockMCP()
    utility_tools.register_tools(mcp)

    print("\n1. Testing generate_password:")
    result = mcp.tools['generate_password'](16, True, True, True)
    print(f"   Result preview: {result[:150]}...")

    print("\n2. Testing check_password_strength (weak password):")
    result = mcp.tools['check_password_strength']("123456")
    print(f"   Result preview: {result[:200]}...")

    print("\n3. Testing check_password_strength (strong password):")
    result = mcp.tools['check_password_strength']("MyP@ssw0rd!2024")
    print(f"   Result preview: {result[:200]}...")

    print("\n[OK] Security tools test completed")

if __name__ == "__main__":
    test_security_tools()

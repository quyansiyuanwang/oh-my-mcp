#!/usr/bin/env python3
"""Test file comparison tools"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import file

class MockMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_file_diff_tools():
    print("=" * 60)
    print("Testing File Comparison Tools (2 tools)")
    print("=" * 60)

    mcp = MockMCP()
    file_tools.register_tools(mcp)

    # Create test files
    file1 = Path("test_old.txt")
    file2 = Path("test_new.txt")

    file1.write_text("Line 1\nLine 2\nLine 3\nLine 4\n")
    file2.write_text("Line 1\nLine 2 modified\nLine 3\nLine 5\n")

    print("\n1. Testing diff_files:")
    result = mcp.tools['diff_files'](str(file1), str(file2), 3, "unified")
    print(f"   Result preview: {result[:200]}...")

    print("\n2. Testing diff_text:")
    text1 = "Hello World\nThis is a test\nLine 3"
    text2 = "Hello Universe\nThis is a test\nLine 3 modified"
    result = mcp.tools['diff_text'](text1, text2, "unified")
    print(f"   Result preview: {result[:200]}...")

    # Cleanup
    file1.unlink()
    file2.unlink()

    print("\n[OK] File comparison tools test completed")

if __name__ == "__main__":
    test_file_diff_tools()

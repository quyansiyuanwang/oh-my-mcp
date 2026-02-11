#!/usr/bin/env python3
"""Test text similarity tool"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import text_tools

class MockMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_text_similarity():
    print("=" * 60)
    print("Testing Text Similarity Tool (1 tool)")
    print("=" * 60)

    mcp = MockMCP()
    text_tools.register_tools(mcp)

    print("\n1. Testing calculate_text_similarity (Levenshtein):")
    text1 = "Hello World"
    text2 = "Hello Universe"
    result = mcp.tools['calculate_text_similarity'](text1, text2, "levenshtein")
    print(f"   Result: {result[:200]}...")

    print("\n2. Testing calculate_text_similarity (Jaccard):")
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "The quick brown cat jumps over the lazy dog"
    result = mcp.tools['calculate_text_similarity'](text1, text2, "jaccard")
    print(f"   Result: {result[:200]}...")

    print("\n3. Testing with identical texts:")
    text1 = "Same text"
    text2 = "Same text"
    result = mcp.tools['calculate_text_similarity'](text1, text2, "levenshtein")
    print(f"   Result: {result[:150]}...")

    print("\n[OK] Text similarity tool test completed")

if __name__ == "__main__":
    test_text_similarity()

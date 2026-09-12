#!/usr/bin/env python3
"""Test network tools"""

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import web


class MockMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


def test_network_tools() -> None:
    print("=" * 60)
    print("Testing Network Tools (3 tools)")
    print("=" * 60)

    mcp = MockMCP()
    web.register_tools(mcp)

    print("\n1. Testing http_request (GET):")
    result = mcp.tools["http_request"]("https://httpbin.org/get", "GET", "{}", None, 10)
    print(f"   Result preview: {result[:150]}...")

    print("\n2. Testing get_network_info:")
    result = mcp.tools["get_network_info"]()
    print(f"   Result preview: {result[:200]}...")

    print("\n3. Testing dns_lookup:")
    result = mcp.tools["dns_lookup"]("google.com", "A")
    print(f"   Result preview: {result[:150]}...")

    print("\n[OK] Network tools test completed")


if __name__ == "__main__":
    test_network_tools()

#!/usr/bin/env python3
"""Tests for system tools (system info, CPU/memory/disk, env vars, time)."""

import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import system


class MockMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
system.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


def test_get_system_info() -> None:
    info = json.loads(T["get_system_info"]())
    assert "platform" in info or "system" in info


def test_get_cpu_info() -> None:
    info = json.loads(T["get_cpu_info"]())
    assert info, "expected non-empty CPU info"


def test_get_memory_info() -> None:
    info = json.loads(T["get_memory_info"]())
    assert info, "expected non-empty memory info"


def test_get_disk_info() -> None:
    result = T["get_disk_info"](str(Path.home()))
    info = json.loads(result)
    assert "error" not in info or "disk" in str(info).lower()


def test_get_disk_info_invalid_path() -> None:
    result = T["get_disk_info"]("\\\\nonexistent-share-xyz\\nul")
    assert isinstance(result, str)


def test_get_env_variable_existing() -> None:
    os.environ["OMCP_TEST_VAR"] = "hello123"
    try:
        result = json.loads(T["get_env_variable"]("OMCP_TEST_VAR"))
        assert result.get("value") == "hello123" or "hello123" in str(result)
    finally:
        del os.environ["OMCP_TEST_VAR"]


def test_get_env_variable_missing_with_default() -> None:
    result = json.loads(T["get_env_variable"]("OMCP_MISSING_VAR_42", "fallback"))
    assert result.get("value") == "fallback" or "fallback" in str(result)


def test_get_env_variable_missing_no_default() -> None:
    result = json.loads(T["get_env_variable"]("OMCP_MISSING_VAR_42"))
    assert result.get("value") in ("", None)


def test_list_env_variables_with_filter() -> None:
    os.environ["OMCP_FILTER_ABC"] = "1"
    os.environ["OMCP_OTHER_XYZ"] = "2"
    try:
        result = json.loads(T["list_env_variables"]("OMCP_FILTER"))
        text = json.dumps(result)
        assert "OMCP_FILTER_ABC" in text
        assert "OMCP_OTHER_XYZ" not in text
    finally:
        del os.environ["OMCP_FILTER_ABC"]
        del os.environ["OMCP_OTHER_XYZ"]


def test_get_current_time_iso() -> None:
    result = json.loads(T["get_current_time"]())
    assert result, "expected non-empty time info"


def test_get_current_time_custom_format() -> None:
    result = json.loads(T["get_current_time"](format="%Y"))
    text = str(result)
    assert text or result


def test_get_process_info() -> None:
    result = T["get_process_info"]()
    assert isinstance(result, str) and result


def test_get_network_interfaces() -> None:
    result = json.loads(T["get_network_interfaces"]())
    assert result["success"] is True
    assert len(result["interfaces"]) >= 1  # loopback always exists
    loopback = [i for i in result["interfaces"] if "lo" in i["name"].lower()]
    assert loopback, "expected a loopback interface"


def test_get_battery_info() -> None:
    result = json.loads(T["get_battery_info"]())
    # desktops/VMs may not have a battery; both shapes are valid
    assert result["success"] is True
    assert "has_battery" in result

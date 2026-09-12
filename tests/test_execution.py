#!/usr/bin/env python3
"""Tests for the command execution plugin (allowlist-based run_command)."""

import json
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Callable, Dict
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import execution


class MockMCP:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
execution.register_tools(MOCK_MCP)
T = MOCK_MCP.tools
LIB = "mcp_server.tools.execution.handlers"


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path) -> Iterator[Path]:
    """Point the persistent allowlist at a temp file and reset state."""
    config_path = tmp_path / "execution_config.json"
    with (
        patch(f"{LIB}._CONFIG_PATH", config_path),
        patch("mcp_server.command_executor.CommandValidator.ALLOWED_COMMANDS", set()),
    ):
        yield config_path


def _fake_run(returncode: int = 0, stdout: str = "out", stderr: str = "") -> Any:
    proc = subprocess.CompletedProcess(
        args=["cmd"], returncode=returncode, stdout=stdout, stderr=stderr
    )
    return patch("subprocess.run", return_value=proc)


class TestAllowlist:
    def test_starts_empty(self) -> None:
        result = json.loads(T["list_allowed_commands"]())
        assert result["allowed_commands"] == []
        assert result["count"] == 0

    def test_add_and_list_persists(self, isolated_config: Path) -> None:
        result = json.loads(T["add_allowed_commands"](["git", "python"]))
        assert result["success"] is True
        assert result["allowed_commands"] == ["git", "python"]

        # persisted to disk
        data = json.loads(isolated_config.read_text(encoding="utf-8"))
        assert data["allowed_commands"] == ["git", "python"]

        # a fresh load (simulating restart) sees the same list
        result = json.loads(T["list_allowed_commands"]())
        assert result["allowed_commands"] == ["git", "python"]

    def test_add_rejects_empty(self) -> None:
        assert "error" in json.loads(T["add_allowed_commands"]([]))
        assert "error" in json.loads(T["add_allowed_commands"](["", "  "]))

    def test_add_rejects_oversized_allowlist(self, isolated_config: Path) -> None:
        big = [f"cmd{i}" for i in range(105)]
        result = json.loads(T["add_allowed_commands"](big))
        assert "error" in result

    def test_remove(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["git", "python", "npm"])
        result = json.loads(T["remove_allowed_commands"](["python", "not-there"]))
        assert result["removed"] == ["python"]
        assert result["allowed_commands"] == ["git", "npm"]


class TestRunCommand:
    def test_rejects_non_allowlisted_command(self) -> None:
        result = json.loads(T["run_command"]("curl", args='["http://evil.example"]'))
        assert "error" in result
        assert "not allowed" in result["error"]

    def test_rejects_dangerous_arguments(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["echo"])
        result = json.loads(T["run_command"]("echo", args='["a; rm -rf /"]'))
        assert "error" in result

    def test_rejects_invalid_timeout(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["echo"])
        assert "error" in json.loads(T["run_command"]("echo", timeout=0))
        assert "error" in json.loads(T["run_command"]("echo", timeout=9999))

    def test_rejects_malformed_args_json(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["echo"])
        result = json.loads(T["run_command"]("echo", args="not-json"))
        assert "error" in result
        assert "JSON array" in result["error"]

    def test_successful_execution(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["echo"])
        with _fake_run(returncode=0, stdout="hello"):
            result = json.loads(T["run_command"]("echo", args='["hello"]'))
        assert result["success"] is True
        assert result["returncode"] == 0
        assert result["stdout"] == "hello"
        assert result["execution_time"] >= 0

    def test_nonzero_returncode_is_reported(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["false"])
        with _fake_run(returncode=2, stderr="boom"):
            result = json.loads(T["run_command"]("false"))
        assert result["success"] is False
        assert result["returncode"] == 2
        assert result["stderr"] == "boom"

    def test_exe_suffix_matches_allowlist(self, isolated_config: Path) -> None:
        # ".exe" suffix is stripped before the allowlist comparison; the
        # command-existence check is mocked so the test is platform-neutral
        T["add_allowed_commands"](["git"])
        with _fake_run(), patch(
            "mcp_server.command_executor.CommandExecutor._check_command_exists",
            return_value=True,
        ):
            result = json.loads(T["run_command"]("git.exe", args='["status"]'))
        assert "error" not in result

    def test_command_not_found(self, isolated_config: Path) -> None:
        T["add_allowed_commands"](["definitely-not-installed-xyz"])
        with patch(
            "mcp_server.command_executor.CommandExecutor._check_command_exists",
            return_value=False,
        ):
            result = json.loads(T["run_command"]("definitely-not-installed-xyz"))
        assert "error" in result
        assert "not found" in result["error"]

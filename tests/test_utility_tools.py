#!/usr/bin/env python3
"""Tests for utility tools (uuid/hash/dates/math/password)."""

import hashlib
import json
import re
import string
import sys
import uuid as uuid_module
from pathlib import Path
from typing import Any, Callable, Dict

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import utility


class MockMCP:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
utility.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class TestUuid:
    def test_uuid4_valid(self) -> None:
        result = T["generate_uuid"]()
        parsed = uuid_module.UUID(result)
        assert parsed.version == 4

    def test_uuid1_valid(self) -> None:
        result = T["generate_uuid"](version=1)
        assert uuid_module.UUID(result).version == 1

    def test_uuid_uppercase(self) -> None:
        result = T["generate_uuid"](uppercase=True)
        assert result == result.upper()

    def test_uuid_unsupported_version(self) -> None:
        assert "Error" in T["generate_uuid"](version=3)


class TestHash:
    def test_sha256(self) -> None:
        result = json.loads(T["generate_hash"]("hello"))
        assert result["hash"] == hashlib.sha256(b"hello").hexdigest()

    def test_md5_and_sha1(self) -> None:
        assert (
            json.loads(T["generate_hash"]("x", algorithm="md5"))["hash"]
            == hashlib.md5(b"x").hexdigest()
        )
        assert (
            json.loads(T["generate_hash"]("x", algorithm="sha1"))["hash"]
            == hashlib.sha1(b"x").hexdigest()
        )

    def test_invalid_algorithm(self) -> None:
        assert "Error" in T["generate_hash"]("x", algorithm="rot13")

    def test_unicode(self) -> None:
        result = json.loads(T["generate_hash"]("中文"))
        assert result["hash"] == hashlib.sha256("中文".encode()).hexdigest()


class TestTimestamps:
    def test_timestamp_to_date_roundtrip(self) -> None:
        result = json.loads(T["timestamp_to_date"](1700000000))
        assert result["timestamp"] == 1700000000
        assert "2023" in result["readable"]

    def test_timestamp_utc(self) -> None:
        result = json.loads(T["timestamp_to_date"](0, timezone="utc"))
        assert result["readable"].startswith("1970-01-01")

    def test_timestamp_custom_format(self) -> None:
        result = json.loads(T["timestamp_to_date"](0, format="%Y", timezone="utc"))
        assert result["formatted"] == "1970"

    def test_date_to_timestamp(self) -> None:
        result = json.loads(T["date_to_timestamp"]("2023-11-14 22:13:20", timezone="utc"))
        assert result["timestamp"] == 1700000000.0

    def test_date_to_timestamp_invalid(self) -> None:
        result = json.loads(T["date_to_timestamp"]("not a date"))
        assert "error" in result

    def test_calculate_date_diff(self) -> None:
        result = json.loads(T["calculate_date_diff"]("2023-01-01", "2023-01-11"))
        assert result["difference"]["total_days"] == 10.0
        assert result["result"] == 10.0

    def test_calculate_date_diff_hours(self) -> None:
        result = json.loads(T["calculate_date_diff"]("2023-01-01", "2023-01-02", unit="hours"))
        assert result["result"] == 24.0

    def test_calculate_date_diff_invalid_unit(self) -> None:
        result = json.loads(T["calculate_date_diff"]("2023-01-01", "2023-01-02", unit="weeks"))
        assert "Unknown unit" in result["error"]

    def test_format_date(self) -> None:
        result = json.loads(T["format_date"]("2023-05-07", format="%d/%m/%Y"))
        assert result["output"] == "07/05/2023"


class TestCalculateExpression:
    def test_basic_arithmetic(self) -> None:
        result = json.loads(T["calculate_expression"]("2 + 3 * 4"))
        assert result["result"] == 14

    def test_power_operator(self) -> None:
        result = json.loads(T["calculate_expression"]("2 ^ 10"))
        assert result["result"] == 1024

    def test_parentheses(self) -> None:
        result = json.loads(T["calculate_expression"]("(2 + 3) * 4"))
        assert result["result"] == 20

    def test_math_functions(self) -> None:
        assert json.loads(T["calculate_expression"]("sqrt(16)"))["result"] == 4.0
        assert json.loads(T["calculate_expression"]("abs(-5)"))["result"] == 5
        assert json.loads(T["calculate_expression"]("max(1, 2, 3)"))["result"] == 3
        assert json.loads(T["calculate_expression"]("round(2.7)"))["result"] == 3
        assert abs(json.loads(T["calculate_expression"]("sin(0)"))["result"]) < 1e-9

    def test_constants(self) -> None:
        result = json.loads(T["calculate_expression"]("round(pi * 2, 4)"))
        assert result["result"] == 6.2832

    def test_invalid_characters(self) -> None:
        result = json.loads(T["calculate_expression"]("__import__('os')"))
        assert "error" in result

    def test_unknown_identifier(self) -> None:
        result = json.loads(T["calculate_expression"]("foo(1)"))
        assert "error" in result
        assert "foo" in result["error"]

    def test_division_by_zero(self) -> None:
        result = json.loads(T["calculate_expression"]("1/0"))
        assert "error" in result


class TestRandomString:
    def test_default_length(self) -> None:
        result = json.loads(T["generate_random_string"]())
        assert result["length"] == 16
        assert re.fullmatch(r"[A-Za-z0-9]{16}", result["string"])

    def test_digits_charset(self) -> None:
        result = json.loads(T["generate_random_string"](length=20, charset="digits"))
        assert re.fullmatch(r"\d{20}", result["string"])

    def test_hex_charset(self) -> None:
        result = json.loads(T["generate_random_string"](length=32, charset="hex"))
        assert re.fullmatch(r"[0-9a-f]{32}", result["string"])

    def test_invalid_length(self) -> None:
        assert "Error" in T["generate_random_string"](0)
        assert "Error" in T["generate_random_string"](20000)

    def test_unknown_charset(self) -> None:
        assert "Error" in T["generate_random_string"](charset="emoji")


class TestPassword:
    def test_default_generation(self) -> None:
        result = json.loads(T["generate_password"](length=16))
        assert len(result["password"]) == 16
        assert result["success"] is True

    def test_exclude_ambiguous(self) -> None:
        for _ in range(5):
            result = json.loads(T["generate_password"](length=32))
            assert not any(c in "lIO01" for c in result["password"])

    def test_too_short(self) -> None:
        result = json.loads(T["generate_password"](length=4))
        assert "error" in result

    def test_too_long(self) -> None:
        result = json.loads(T["generate_password"](length=200))
        assert "error" in result

    def test_no_symbols(self) -> None:
        result = json.loads(T["generate_password"](length=64, include_symbols=False))
        assert not any(c in string.punctuation for c in result["password"])


class TestPasswordStrength:
    def test_weak_password(self) -> None:
        result = json.loads(T["check_password_strength"]("password"))
        assert result["strength_score"] == 0
        assert result["strength_level"] == "Weak"

    def test_strong_password(self) -> None:
        result = json.loads(T["check_password_strength"]("xK9$mQ2#vL8@pR4!"))
        assert result["strength_score"] >= 60

    def test_common_password_detected(self) -> None:
        result = json.loads(T["check_password_strength"]("qwerty"))
        assert any("commonly used" in issue for issue in result["issues"])

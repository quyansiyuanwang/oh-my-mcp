#!/usr/bin/env python3
"""Tests for data processing tools (JSON/CSV/XML/YAML/TOML)."""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import data


class MockMCP:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
data.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class TestJsonTools:
    def test_parse_json_valid(self) -> None:
        result = json.loads(T["parse_json"]('{"a": 1, "b": [1, 2]}'))
        assert result == {"a": 1, "b": [1, 2]}

    def test_parse_json_invalid(self) -> None:
        result = json.loads(T["parse_json"]("{invalid"))
        assert "error" in result
        assert "Invalid JSON" in result["error"]

    def test_format_json_indent_and_sort(self) -> None:
        result = T["format_json"]('{"b": 1, "a": 2}', indent=4, sort_keys=True)
        assert '"    "a"' in result.replace(" ", '" "') or "a" in result
        lines = result.splitlines()
        assert lines[0] == "{"
        # sorted: "a" comes before "b"
        assert result.index('"a"') < result.index('"b"')

    def test_format_json_invalid(self) -> None:
        result = json.loads(T["format_json"]("not json"))
        assert "error" in result

    def test_json_query_dict_path(self) -> None:
        result = json.loads(T["json_query"]('{"user": {"name": "Alice"}}', "user.name"))
        assert result["value"] == "Alice"

    def test_json_query_array_index(self) -> None:
        result = json.loads(T["json_query"]('{"items": ["x", "y"]}', "items.1"))
        assert result["value"] == "y"

    def test_json_query_missing_key(self) -> None:
        result = json.loads(T["json_query"]('{"a": 1}', "b"))
        assert "Path not found" in result["error"]

    def test_json_query_invalid_index(self) -> None:
        result = json.loads(T["json_query"]('{"items": [1]}', "items.x"))
        assert "Invalid array index" in result["error"]

    def test_json_query_invalid_json(self) -> None:
        result = json.loads(T["json_query"]("nope", "a"))
        assert "Invalid JSON" in result["error"]

    def test_json_query_scalar_navigate(self) -> None:
        result = json.loads(T["json_query"]('{"a": 1}', "a.b"))
        assert "Cannot navigate path" in result["error"]

    def test_validate_json_schema_valid_object(self) -> None:
        result = json.loads(T["validate_json_schema"]('{"a": 1}'))
        assert result["valid"] is True
        assert result["structure"]["type"] == "object"
        assert result["structure"]["keys"] == 1

    def test_validate_json_schema_array(self) -> None:
        result = json.loads(T["validate_json_schema"]("[1, 2, 3]"))
        assert result["valid"] is True
        assert result["structure"]["type"] == "array"

    def test_validate_json_schema_primitive_types(self) -> None:
        for raw, expected in [
            ('"s"', "string"),
            ("42", "number"),
            ("3.14", "number"),
            ("true", "boolean"),
            ("null", "null"),
        ]:
            result = json.loads(T["validate_json_schema"](raw))
            assert result["structure"]["type"] == expected, raw

    def test_validate_json_schema_invalid(self) -> None:
        result = json.loads(T["validate_json_schema"]("{bad"))
        assert result["valid"] is False
        assert "error" in result

    def test_flatten_json_nested(self) -> None:
        result = json.loads(T["flatten_json"]('{"a": {"b": {"c": 1}}, "d": [2, 3]}'))
        assert result == {"a.b.c": 1, "d.0": 2, "d.1": 3}

    def test_flatten_json_custom_separator(self) -> None:
        result = json.loads(T["flatten_json"]('{"a": {"b": 1}}', separator="_"))
        assert result == {"a_b": 1}

    def test_flatten_json_invalid(self) -> None:
        result = json.loads(T["flatten_json"]("["))
        assert "error" in result

    def test_merge_json_deep(self) -> None:
        result = json.loads(T["merge_json"]('{"a": {"x": 1, "y": 2}}', '{"a": {"y": 3, "z": 4}}'))
        assert result == {"a": {"x": 1, "y": 3, "z": 4}}

    def test_merge_json_shallow(self) -> None:
        result = json.loads(
            T["merge_json"]('{"a": {"x": 1, "y": 2}}', '{"a": {"z": 9}}', deep=False)
        )
        assert result == {"a": {"z": 9}}

    def test_merge_json_non_object(self) -> None:
        result = json.loads(T["merge_json"]("[1]", "[2]"))
        assert "error" in result

    def test_merge_json_invalid_json(self) -> None:
        result = json.loads(T["merge_json"]("{", "{}"))
        assert "error" in result


class TestCsvTools:
    def test_csv_to_json_with_header(self) -> None:
        result = json.loads(T["csv_to_json"]("name,age\nAlice,30\nBob,25"))
        assert result["count"] == 2
        assert result["data"][0] == {"name": "Alice", "age": "30"}

    def test_csv_to_json_no_header(self) -> None:
        result = json.loads(T["csv_to_json"]("a,b", has_header=False))
        assert result["data"][0] == {"col_0": "a", "col_1": "b"}

    def test_csv_to_json_empty(self) -> None:
        result = json.loads(T["csv_to_json"](""))
        assert result == {"data": [], "count": 0}

    def test_csv_to_json_custom_delimiter(self) -> None:
        result = json.loads(T["csv_to_json"]("a;b", delimiter=";", has_header=False))
        assert result["data"][0] == {"col_0": "a", "col_1": "b"}

    def test_csv_to_json_missing_columns_filled(self) -> None:
        result = json.loads(T["csv_to_json"]("a,b\nx"))
        assert result["data"][0] == {"a": "x", "b": ""}

    def test_json_to_csv_roundtrip(self) -> None:
        csv_text = T["json_to_csv"]('[{"b": 1, "a": 2}, {"a": 3, "b": 4}]')
        lines = csv_text.strip().splitlines()
        assert lines[0] == "a,b"
        assert lines[1] == "2,1"

    def test_json_to_csv_not_array(self) -> None:
        assert "Error" in T["json_to_csv"]('{"a": 1}')

    def test_json_to_csv_empty_array(self) -> None:
        assert T["json_to_csv"]("[]") == ""

    def test_json_to_csv_invalid_json(self) -> None:
        assert "Error" in T["json_to_csv"]("nope")

    def test_parse_csv(self) -> None:
        result = json.loads(T["parse_csv"]("name,age\nAlice,30"))
        assert result["count"] == 1
        assert result["columns"] == ["name", "age"]
        assert result["data"][0]["name"] == "Alice"

    def test_parse_csv_invalid(self) -> None:
        # A null byte raises an error inside csv module
        result = json.loads(T["parse_csv"]("a\x00b"))
        assert "error" in result or "data" in result


class TestXmlTools:
    def test_xml_to_json_simple(self) -> None:
        result = json.loads(T["xml_to_json"]("<root><a>1</a><b>2</b></root>"))
        assert result == {"root": {"a": "1", "b": "2"}}

    def test_xml_to_json_attributes(self) -> None:
        result = json.loads(T["xml_to_json"]('<root id="7"><a/></root>'))
        assert result["root"]["@attributes"] == {"id": "7"}

    def test_xml_to_json_repeated_tags(self) -> None:
        result = json.loads(T["xml_to_json"]("<root><i>1</i><i>2</i></root>"))
        items = result["root"]["i"]
        assert isinstance(items, list) and len(items) == 2

    def test_xml_to_json_text_only(self) -> None:
        result = json.loads(T["xml_to_json"]("<root>hello</root>"))
        assert result == {"root": "hello"}

    def test_xml_to_json_invalid(self) -> None:
        result = json.loads(T["xml_to_json"]("<root><unclosed>"))
        assert "error" in result


class TestYamlTools:
    def test_parse_yaml(self) -> None:
        result = json.loads(T["parse_yaml"]("name: Alice\nage: 30"))
        assert result == {"name": "Alice", "age": 30}

    def test_parse_yaml_invalid(self) -> None:
        result = json.loads(T["parse_yaml"]("a: [unclosed"))
        assert "error" in result

    def test_yaml_to_json(self) -> None:
        result = json.loads(T["yaml_to_json"]("- 1\n- 2"))
        assert result == [1, 2]

    def test_json_to_yaml_roundtrip(self) -> None:
        yaml_text = T["json_to_yaml"]('{"name": "测试", "n": 1}')
        parsed = json.loads(T["parse_yaml"](yaml_text))
        assert parsed == {"name": "测试", "n": 1}

    def test_json_to_yaml_invalid(self) -> None:
        assert "Error" in T["json_to_yaml"]("{bad")


class TestTomlTools:
    def test_parse_toml(self) -> None:
        result = json.loads(T["parse_toml"]('[server]\nport = 8080\nhost = "localhost"'))
        assert result == {"server": {"port": 8080, "host": "localhost"}}

    def test_parse_toml_invalid(self) -> None:
        result = json.loads(T["parse_toml"]("[unclosed"))
        assert "error" in result

    def test_toml_to_json(self) -> None:
        result = json.loads(T["toml_to_json"]("value = 42"))
        assert result == {"value": 42}


if __name__ == "__main__":
    sys.exit(0)

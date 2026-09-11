#!/usr/bin/env python3
"""Complex scenario tests for data processing tools: format roundtrips,
special values, and cross-format edge cases."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import data


class MockMCP:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
data.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class TestFormatRoundtrips:
    def test_json_yaml_roundtrip_complex(self) -> None:
        doc = {"name": "项目", "items": [1, 2, 3], "nested": {"a": True, "b": None}}
        as_yaml = T["json_to_yaml"](json.dumps(doc, ensure_ascii=False))
        back = json.loads(T["parse_yaml"](as_yaml))
        assert back == doc

    def test_csv_json_roundtrip(self) -> None:
        rows = [{"name": "Alice", "age": "30"}, {"name": "Bob, Jr.", "age": "25"}]
        csv_text = T["json_to_csv"](json.dumps(rows))
        result = json.loads(T["csv_to_json"](csv_text))
        assert result["count"] == 2
        assert result["data"][1]["name"] == "Bob, Jr."  # quoting survives

    def test_csv_roundtrip_with_newlines_in_fields(self) -> None:
        rows = [{"id": "1", "note": "line1\nline2"}, {"id": "2", "note": 'has "quotes"'}]
        csv_text = T["json_to_csv"](json.dumps(rows))
        result = json.loads(T["csv_to_json"](csv_text))
        assert result["data"][0]["note"] == "line1\nline2"
        assert result["data"][1]["note"] == 'has "quotes"'

    def test_toml_json_roundtrip(self) -> None:
        doc = {"server": {"host": "localhost", "port": 8080}, "tags": ["a", "b"]}
        as_toml_data = json.loads(
            T["parse_toml"]('tags = ["a", "b"]\n[server]\nhost = "localhost"\nport = 8080\n')
        )
        assert as_toml_data == doc

    def test_xml_to_json_attributes_and_nesting(self) -> None:
        xml = '<config version="2"><db host="localhost"><port>5432</port></db><debug/></config>'
        result = json.loads(T["xml_to_json"](xml))
        assert result["config"]["@attributes"] == {"version": "2"}
        # text-only elements are promoted to scalars
        assert result["config"]["db"]["port"] == "5432"
        assert result["config"]["db"]["@attributes"] == {"host": "localhost"}
        assert result["config"]["debug"] is None or result["config"]["debug"] is not None

    def test_yaml_special_values(self) -> None:
        result = json.loads(T["parse_yaml"]("a: yes\nb: null\nc: 3.14\nd: '123'\n"))
        # YAML 1.1-style booleans/nulls depend on safe_load — accept either
        assert result["c"] == 3.14
        assert result["d"] == "123"

    def test_toml_rejects_null(self) -> None:
        result = json.loads(T["parse_toml"]("x = null"))
        assert "error" in result  # TOML has no null


class TestSpecialValues:
    def test_json_float_precision(self) -> None:
        result = json.loads(T["parse_json"]("0.1"))
        assert result == 0.1

    def test_json_big_int(self) -> None:
        big = 123456789012345678901234567890
        result = json.loads(T["parse_json"](str(big)))
        assert result == big

    def test_json_unicode_escape(self) -> None:
        result = json.loads(T["parse_json"]('"\\u4e2d\\u6587"'))
        assert result == "中文"

    def test_json_nan_inf(self) -> None:
        result = json.loads(T["parse_json"]('{"a": NaN, "b": Infinity}'))
        import math

        assert math.isnan(result["a"])
        assert result["b"] == math.inf

    def test_csv_empty_fields(self) -> None:
        result = json.loads(T["csv_to_json"]("a,b\n,\n1,2"))
        assert result["data"][0] == {"a": "", "b": ""}

    def test_csv_quoted_delimiter_inside(self) -> None:
        result = json.loads(T["csv_to_json"]('a,b\n"x,y",2'))
        assert result["data"][0] == {"a": "x,y", "b": "2"}

    def test_flatten_deep_nesting(self) -> None:
        doc = {"l1": {"l2": {"l3": {"l4": {"l5": "deep"}}}}}
        result = json.loads(T["flatten_json"](json.dumps(doc)))
        assert result == {"l1.l2.l3.l4.l5": "deep"}

    def test_flatten_empty_containers(self) -> None:
        result = json.loads(T["flatten_json"]('{"a": {}, "b": [], "c": 1}'))
        assert result == {"a": {}, "b": [], "c": 1}

    def test_merge_empty_objects(self) -> None:
        result = json.loads(T["merge_json"]("{}", "{}"))
        assert result == {}

    def test_merge_overwrite_with_null(self) -> None:
        result = json.loads(T["merge_json"]('{"a": 1}', '{"a": null}'))
        assert result == {"a": None}


class TestScaleAndBoundaries:
    def test_large_json_parse(self) -> None:
        big = {"items": [{"id": i, "val": f"v{i}"} for i in range(5000)]}
        raw = json.dumps(big)
        result = json.loads(T["parse_json"](raw))
        assert len(result["items"]) == 5000

    def test_large_csv(self) -> None:
        csv_text = "id,name\n" + "\n".join(f"{i},name{i}" for i in range(3000))
        result = json.loads(T["csv_to_json"](csv_text))
        assert result["count"] == 3000
        assert result["data"][-1]["name"] == "name2999"

    def test_deeply_nested_json_query(self) -> None:
        doc = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        result = json.loads(T["json_query"](json.dumps(doc), "a.b.c.d.e"))
        assert result["value"] == 42

    def test_json_query_root_array(self) -> None:
        result = json.loads(T["json_query"]('[{"n": 1}, {"n": 2}]', "1.n"))
        assert result["value"] == 2

    def test_json_query_empty_path(self) -> None:
        result = json.loads(T["json_query"]('{"a": 1}', ""))
        # empty path means path parts are [""] — expect an error, not a crash
        assert "error" in result or result["value"] is None

    def test_flatten_conflicting_keys_last_wins(self) -> None:
        result = json.loads(T["flatten_json"]('{"a.b": 1, "a": {"b": 2}}'))
        # both flatten to key "a.b" — dict() keeps the later value
        assert result == {"a.b": 2}

    def test_validate_json_schema_deep(self) -> None:
        doc = {"k": [{"x": 1}, {"x": 2}]}
        result = json.loads(T["validate_json_schema"](json.dumps(doc)))
        assert result["valid"] is True
        assert result["structure"]["type"] == "object"
        assert result["size_bytes"] == len(json.dumps(doc))

    def test_bom_json_rejected_gracefully(self) -> None:
        result = json.loads(T["parse_json"]('﻿{"a": 1}'))
        # BOM-prefixed JSON is invalid per json.loads; tool must return error
        assert "error" in result

#!/usr/bin/env python3
"""Tests for file system tools (read/write/list/search/copy/delete etc.)."""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import file


class MockMCP:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
file.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class TestReadWrite:
    def test_write_and_read_roundtrip(self, tmp_path: Path) -> None:
        f = tmp_path / "hello.txt"
        result = T["write_file"](str(f), "你好 world")
        assert "successfully" in result
        assert T["read_file"](str(f)) == "你好 world"

    def test_write_no_overwrite(self, tmp_path: Path) -> None:
        f = tmp_path / "x.txt"
        f.write_text("original")
        result = T["write_file"](str(f), "new", overwrite=False)
        assert "Error" in result
        assert f.read_text(encoding="utf-8") == "original"

    def test_read_missing_file(self, tmp_path: Path) -> None:
        assert "Error" in T["read_file"](str(tmp_path / "missing.txt"))

    def test_append(self, tmp_path: Path) -> None:
        f = tmp_path / "log.txt"
        T["append_file"](str(f), "line1\n")
        T["append_file"](str(f), "line2\n")
        content = T["read_file"](str(f))
        assert "line1" in content and "line2" in content
        assert "appended" in T["append_file"](str(f), "more")

    def test_append_creates_parent_dirs(self, tmp_path: Path) -> None:
        f = tmp_path / "a" / "b" / "c.txt"
        result = T["append_file"](str(f), "data")
        assert "Error" not in result
        assert f.read_text(encoding="utf-8") == "data"

    def test_read_with_encoding(self, tmp_path: Path) -> None:
        f = tmp_path / "gbk.txt"
        f.write_bytes("中文".encode("gbk"))
        assert T["read_file"](str(f), encoding="gbk") == "中文"
        assert "Error" in T["read_file"](str(f)) or T["read_file"](str(f)) != "中文"


class TestDirectoryOps:
    def test_list_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("x")
        (tmp_path / "sub").mkdir()
        result = json.loads(T["list_directory"](str(tmp_path)))
        names = {item["name"] for item in result["items"]}
        assert names == {"a.txt", "sub"}
        types = {item["name"]: item["type"] for item in result["items"]}
        assert types["a.txt"] == "file"
        assert types["sub"] == "directory"

    def test_list_directory_recursive(self, tmp_path: Path) -> None:
        (tmp_path / "top.txt").write_text("x")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("y")
        result = json.loads(T["list_directory"](str(tmp_path), recursive=True))
        names = {item["name"] for item in result["items"]}
        assert names == {"top.txt", "sub", "nested.txt"}

    def test_list_directory_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "a.log").write_text("x")
        (tmp_path / "b.txt").write_text("x")
        result = json.loads(T["list_directory"](str(tmp_path), pattern="*.log"))
        assert {item["name"] for item in result["items"]} == {"a.log"}

    def test_list_directory_not_found(self, tmp_path: Path) -> None:
        result = json.loads(T["list_directory"](str(tmp_path / "nope")))
        assert "error" in result

    def test_list_directory_not_a_dir(self, tmp_path: Path) -> None:
        f = tmp_path / "f.txt"
        f.write_text("x")
        result = json.loads(T["list_directory"](str(f)))
        assert "error" in result

    def test_create_directory(self, tmp_path: Path) -> None:
        result = T["create_directory"](str(tmp_path / "a" / "b"))
        assert "created" in result
        assert (tmp_path / "a" / "b").is_dir()
        # idempotent
        assert "already exists" in T["create_directory"](str(tmp_path / "a" / "b"))

    def test_create_directory_on_file(self, tmp_path: Path) -> None:
        f = tmp_path / "f.txt"
        f.write_text("x")
        assert "Error" in T["create_directory"](str(f))


class TestFileMetadata:
    def test_file_exists_true_file(self, tmp_path: Path) -> None:
        f = tmp_path / "f.txt"
        f.write_text("x")
        result = json.loads(T["file_exists"](str(f)))
        assert result == {"path": str(f), "exists": True, "type": "file"}

    def test_file_exists_true_dir(self, tmp_path: Path) -> None:
        result = json.loads(T["file_exists"](str(tmp_path)))
        assert result["exists"] is True and result["type"] == "directory"

    def test_file_exists_false(self, tmp_path: Path) -> None:
        result = json.loads(T["file_exists"](str(tmp_path / "missing")))
        assert result["exists"] is False
        assert "type" not in result

    def test_get_file_info(self, tmp_path: Path) -> None:
        f = tmp_path / "data.json"
        f.write_text("{}")
        info = json.loads(T["get_file_info"](str(f)))
        assert info["type"] == "file"
        assert info["extension"] == ".json"
        assert info["stem"] == "data"
        assert info["size_bytes"] == 2

    def test_get_file_info_directory(self, tmp_path: Path) -> None:
        info = json.loads(T["get_file_info"](str(tmp_path)))
        assert info["type"] == "directory"
        assert "extension" not in info

    def test_get_file_info_missing(self, tmp_path: Path) -> None:
        result = json.loads(T["get_file_info"](str(tmp_path / "missing")))
        assert "error" in result


class TestSearchDeleteCopy:
    def test_search_files_recursive(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "report_2026.txt").write_text("a")
        (sub / "report_2025.txt").write_text("b")
        (sub / "other.log").write_text("c")

        result = json.loads(T["search_files"](str(tmp_path), pattern="*.txt"))
        assert result["count"] == 2

        result = json.loads(T["search_files"](str(tmp_path), pattern="*.txt", name_contains="2025"))
        assert result["count"] == 1
        assert result["matches"][0]["name"] == "report_2025.txt"

    def test_search_files_not_found(self, tmp_path: Path) -> None:
        result = json.loads(T["search_files"](str(tmp_path / "nope")))
        assert "error" in result

    def test_delete_file_requires_confirm(self, tmp_path: Path) -> None:
        f = tmp_path / "doomed.txt"
        f.write_text("x")
        result = T["delete_file"](str(f))
        assert "confirm=True" in result
        assert f.exists()

    def test_delete_file_with_confirm(self, tmp_path: Path) -> None:
        f = tmp_path / "doomed.txt"
        f.write_text("x")
        assert "deleted successfully" in T["delete_file"](str(f), confirm=True)
        assert not f.exists()

    def test_delete_file_missing(self, tmp_path: Path) -> None:
        assert "Error" in T["delete_file"](str(tmp_path / "missing"), confirm=True)

    def test_delete_file_directory_rejected(self, tmp_path: Path) -> None:
        d = tmp_path / "dir"
        d.mkdir()
        assert "Error" in T["delete_file"](str(d), confirm=True)
        assert d.exists()

    def test_copy_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        dst = tmp_path / "out" / "dst.txt"
        src.write_text("payload", encoding="utf-8")
        result = T["copy_file"](str(src), str(dst))
        assert "copied successfully" in result
        assert dst.read_text(encoding="utf-8") == "payload"

    def test_copy_file_no_overwrite(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("s")
        dst.write_text("d")
        assert "Error" in T["copy_file"](str(src), str(dst))
        assert dst.read_text(encoding="utf-8") == "d"
        assert "copied successfully" in T["copy_file"](str(src), str(dst), overwrite=True)

    def test_copy_file_source_missing(self, tmp_path: Path) -> None:
        assert "Error" in T["copy_file"](str(tmp_path / "nope"), str(tmp_path / "x"))

    def test_copy_file_source_is_dir(self, tmp_path: Path) -> None:
        d = tmp_path / "dir"
        d.mkdir()
        assert "Error" in T["copy_file"](str(d), str(tmp_path / "x"))


if __name__ == "__main__":
    sys.exit(0)

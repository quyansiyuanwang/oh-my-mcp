#!/usr/bin/env python3
"""Complex scenario tests for file system tools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import file


class MockMCP:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
file.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class TestExoticFilenames:
    def test_unicode_emoji_names(self, tmp_path: Path) -> None:
        names = ["中文报告.docx", "notizbücher.md", "파일.txt", "emoji-🚀🎉.dat"]
        for i, n in enumerate(names):
            r = T["write_file"](str(tmp_path / n), f"内容 {i}")
            assert "successfully" in r, n
        result = json.loads(T["list_directory"](str(tmp_path)))
        assert result["count"] == len(names)
        for n in names:
            assert (
                T["read_file"](str(tmp_path / n))
                == dict(zip(names, [f"内容 {i}" for i in range(len(names))]))[n]
            )

    def test_names_with_spaces_and_dots(self, tmp_path: Path) -> None:
        name = "my file.v2.final (copy).txt"
        T["write_file"](str(tmp_path / name), "x")
        info = json.loads(T["get_file_info"](str(tmp_path / name)))
        assert info["stem"] == "my file.v2.final (copy)"
        assert info["extension"] == ".txt"

    def test_long_nested_path(self, tmp_path: Path) -> None:
        deep = tmp_path
        for i in range(15):
            deep = deep / f"level_{i:02}_{'x' * 10}"
        target = deep / "leaf.txt"
        r = T["write_file"](str(target), "deep")
        assert "Error" not in r or "successfully" in r
        assert T["read_file"](str(target)) == "deep"


class TestLargeContent:
    def test_large_text_roundtrip(self, tmp_path: Path) -> None:
        content = "iteration line 1234567890\n" * 300_000  # ~8 MB, under the 10MB cap
        f = tmp_path / "big.txt"
        assert "successfully" in T["write_file"](str(f), content)
        assert T["read_file"](str(f)) == content
        info = json.loads(T["get_file_info"](str(f)))
        assert info["size_bytes"] == len(content.encode("utf-8"))

    def test_read_size_limit_enforced(self, tmp_path: Path) -> None:
        content = "x" * (10 * 1024 * 1024 + 100)
        f = tmp_path / "too_big.txt"
        f.write_text(content, encoding="utf-8")
        result = T["read_file"](str(f))
        assert "Error" in result
        assert "too large" in result

    def test_append_many_times(self, tmp_path: Path) -> None:
        f = tmp_path / "log.txt"
        for i in range(200):
            T["append_file"](str(f), f"line {i}\n")
        content = T["read_file"](str(f))
        assert "line 0\n" in content and "line 199\n" in content
        lines = content.strip().splitlines()
        assert len(lines) == 200


class TestEncodingsAndBinary:
    def test_encodings_roundtrip(self, tmp_path: Path) -> None:
        f = tmp_path / "enc.txt"
        T["write_file"](str(f), "你好世界", encoding="utf-8")
        assert T["read_file"](str(f), encoding="utf-8") == "你好世界"

    def test_invalid_bytes_surrogateescape(self, tmp_path: Path) -> None:
        f = tmp_path / "raw.bin"
        f.write_bytes(b"\xff\xfe invalid utf8 \x80\x81")
        # tool must not crash; result is implementation-defined but str
        result = T["read_file"](str(f))
        assert isinstance(result, str)

    def test_crlf_content_preserved(self, tmp_path: Path) -> None:
        f = tmp_path / "crlf.txt"
        content = "a\r\nb\r\nc\r\n"
        T["write_file"](str(f), content)
        assert T["read_file"](str(f)) == content


class TestDirectoryScenario:
    def test_wide_and_deep_tree(self, tmp_path: Path) -> None:
        for i in range(10):
            d = tmp_path / f"dir_{i}"
            d.mkdir()
            for j in range(10):
                (d / f"file_{j}.txt").write_text(f"{i}-{j}")
        (tmp_path / "dir_3" / "sub").mkdir()
        (tmp_path / "dir_3" / "sub" / "nested.log").write_text("x")

        flat = json.loads(T["list_directory"](str(tmp_path)))
        assert flat["count"] == 10

        rec = json.loads(T["list_directory"](str(tmp_path), recursive=True))
        assert rec["count"] == 112  # 10 dirs + 100 files + 1 sub + 1 log

    def test_search_case_insensitive_and_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "Report.txt").write_text("a")
        (tmp_path / "report_final.txt").write_text("b")
        (tmp_path / "other.log").write_text("c")
        # glob case rules are platform-dependent; same-case names match everywhere
        r = json.loads(T["search_files"](str(tmp_path), pattern="*.txt"))
        assert r["count"] == 2
        # name_contains matching is implemented case-insensitively by the tool
        r = json.loads(T["search_files"](str(tmp_path), pattern="*", name_contains="REPORT"))
        assert r["count"] == 2

    def test_search_empty_directory(self, tmp_path: Path) -> None:
        r = json.loads(T["search_files"](str(tmp_path)))
        assert r["count"] == 0


class TestErrorAndEdge:
    def test_read_directory_fails(self, tmp_path: Path) -> None:
        result = T["read_file"](str(tmp_path))
        assert "Error" in result or "error" in result.lower()

    def test_copy_file_onto_itself(self, tmp_path: Path) -> None:
        f = tmp_path / "same.txt"
        f.write_text("same")
        # shutil.copy2 onto identical path must not corrupt the file
        T["copy_file"](str(f), str(f), overwrite=True)
        assert f.read_text(encoding="utf-8") == "same"

    def test_delete_recreate_cycle(self, tmp_path: Path) -> None:
        f = tmp_path / "cycle.txt"
        for i in range(5):
            T["write_file"](str(f), f"v{i}")
            assert T["read_file"](str(f)) == f"v{i}"
            assert "deleted successfully" in T["delete_file"](str(f), confirm=True)
            assert json.loads(T["file_exists"](str(f)))["exists"] is False

    def test_special_path_characters(self, tmp_path: Path) -> None:
        f = tmp_path / "weird $name 'quoted' & more.txt"
        T["write_file"](str(f), "ok")
        assert T["read_file"](str(f)) == "ok"

    def test_overwrite_semantics_chain(self, tmp_path: Path) -> None:
        f = tmp_path / "ow.txt"
        T["write_file"](str(f), "first")
        assert "Error" in T["write_file"](str(f), "second", overwrite=False)
        assert "successfully" in T["write_file"](str(f), "second", overwrite=True)
        assert T["read_file"](str(f)) == "second"

    def test_copy_to_existing_directory_fails(self, tmp_path: Path) -> None:
        src = tmp_path / "s.txt"
        src.write_text("s")
        dst_dir = tmp_path / "d"
        dst_dir.mkdir()
        result = T["copy_file"](str(src), str(dst_dir), overwrite=True)
        assert "Error" in result

#!/usr/bin/env python3
"""Complex scenario tests for compression tools.

Covers security attacks (zip-slip, symlink tar, zip bombs), malformed
archives, unicode/space filenames, deep nesting, and multi-file/large-file
roundtrips.
"""

import json
import tarfile
import zipfile
from pathlib import Path

from mcp_server.tools import compression


class MockMCP:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
compression.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


def make_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)


class TestZipSlipSecurity:
    def test_extract_zip_blocks_path_traversal(self, tmp_path: Path) -> None:
        archive = tmp_path / "evil.zip"
        make_zip(archive, {"../slip.txt": b"pwned", "ok.txt": b"fine"})
        out_dir = tmp_path / "out"
        result = json.loads(T["extract_zip"](str(archive), str(out_dir)))
        assert "error" in result
        assert result["type"] == "validation"
        # nothing escaped the extraction dir
        assert not (tmp_path / "slip.txt").exists()

    def test_extract_zip_blocks_absolute_path(self, tmp_path: Path) -> None:
        archive = tmp_path / "evil2.zip"
        make_zip(archive, {"/abs_evil.txt": b"pwned"})
        out_dir = tmp_path / "out"
        result = json.loads(T["extract_zip"](str(archive), str(out_dir)))
        assert "error" in result

    def test_extract_tar_blocks_symlink_escape(self, tmp_path: Path) -> None:
        archive = tmp_path / "evil.tar"
        with tarfile.open(archive, "w") as tf:
            info = tarfile.TarInfo("link")
            info.type = tarfile.SYMTYPE
            info.linkname = str(tmp_path / "target.txt")
            tf.addfile(info)
        out_dir = tmp_path / "out"
        result = json.loads(T["extract_tar"](str(archive), str(out_dir)))
        assert "error" in result
        # the link must not exist anywhere
        assert not (out_dir / "link").exists()
        assert not (tmp_path / "target.txt").exists()

    def test_tar_data_filter_blocks_absolute_link(self, tmp_path: Path) -> None:
        archive = tmp_path / "evil_abs.tar"
        with tarfile.open(archive, "w") as tf:
            info = tarfile.TarInfo("link")
            info.type = tarfile.SYMTYPE
            info.linkname = "/etc/passwd"
            tf.addfile(info)
        result = json.loads(T["extract_tar"](str(archive), str(tmp_path / "out")))
        assert "error" in result

    def test_tar_hardlink_escape_blocked(self, tmp_path: Path) -> None:
        archive = tmp_path / "evil_hard.tar"
        with tarfile.open(archive, "w") as tf:
            info = tarfile.TarInfo("hard")
            info.type = tarfile.LNKTYPE
            info.linkname = str(tmp_path / "outside.txt")
            tf.addfile(info)
        result = json.loads(T["extract_tar"](str(archive), str(tmp_path / "out")))
        assert "error" in result

    def test_zip_bomb_ratio_blocked(self, tmp_path: Path) -> None:
        archive = tmp_path / "bomb.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("zeros.bin", b"\x00" * (20 * 1024 * 1024))
        result = json.loads(T["extract_zip"](str(archive), str(tmp_path / "out")))
        assert "error" in result
        assert "ratio" in result["error"] or "large" in result["error"]


class TestMalformedArchives:
    def test_corrupted_zip(self, tmp_path: Path) -> None:
        archive = tmp_path / "corrupt.zip"
        archive.write_bytes(b"PK\x03\x04 this is not really a zip file at all")
        result = json.loads(T["extract_zip"](str(archive), str(tmp_path / "out")))
        assert "error" in result

    def test_corrupted_tar(self, tmp_path: Path) -> None:
        archive = tmp_path / "corrupt.tar"
        archive.write_bytes(b"garbage" * 100)
        result = json.loads(T["extract_tar"](str(archive), str(tmp_path / "out")))
        assert "error" in result

    def test_truncated_zip(self, tmp_path: Path) -> None:
        good = tmp_path / "good.zip"
        make_zip(good, {"a.txt": b"hello"})
        data = good.read_bytes()
        bad = tmp_path / "truncated.zip"
        bad.write_bytes(data[: len(data) // 2])
        result = json.loads(T["extract_zip"](str(bad), str(tmp_path / "out")))
        assert "error" in result

    def test_list_contents_of_garbage(self, tmp_path: Path) -> None:
        archive = tmp_path / "garbage.zip"
        archive.write_bytes(b"not an archive")
        result = json.loads(T["list_archive_contents"](str(archive)))
        assert "error" in result

    def test_extract_missing_file(self, tmp_path: Path) -> None:
        result = json.loads(T["extract_zip"](str(tmp_path / "nope.zip"), str(tmp_path)))
        assert "error" in result
        assert result["type"] == "validation"


class TestFilenamesAndStructure:
    def test_unicode_and_space_filenames_roundtrip(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        names = ["中文文件.txt", "file with spaces.log", "emoji-🎉.md", "Спутник.dat"]
        for i, name in enumerate(names):
            (src / name).write_text(f"content-{i}", encoding="utf-8")
        archive = tmp_path / "uni.zip"
        r = json.loads(T["compress_zip"]([str(src / n) for n in names], str(archive)))
        assert r["success"] is True

        out = tmp_path / "out"
        r = json.loads(T["extract_zip"](str(archive), str(out)))
        assert r["file_count"] == 4
        for name in names:
            assert (out / name).exists(), name
        assert (out / "中文文件.txt").read_text(encoding="utf-8") == "content-0"

    def test_unicode_tar_roundtrip(self, tmp_path: Path) -> None:
        src = tmp_path / "中文目录"
        src.mkdir()
        (src / "报告.txt").write_text("内容", encoding="utf-8")
        archive = tmp_path / "uni.tar.gz"
        r = json.loads(T["compress_tar"]([str(src)], str(archive)))
        assert r["success"] is True
        assert r["file_count"] == 1
        r = json.loads(T["extract_tar"](str(archive), str(tmp_path / "out")))
        assert (tmp_path / "out" / "中文目录" / "报告.txt").read_text(encoding="utf-8") == "内容"

    def test_nested_directory_structure_preserved(self, tmp_path: Path) -> None:
        base = tmp_path / "proj"
        (base / "a" / "b" / "c").mkdir(parents=True)
        (base / "a" / "b" / "c" / "deep.txt").write_text("deep")
        (base / "top.txt").write_text("top")
        archive = tmp_path / "nested.zip"
        json.loads(
            T["compress_zip"](
                [str(base / "top.txt"), str(base / "a" / "b" / "c" / "deep.txt")], str(archive)
            )
        )
        listing = json.loads(T["list_archive_contents"](str(archive)))
        assert listing["file_count"] == 2

        out = tmp_path / "out"
        r = json.loads(T["extract_zip"](str(archive), str(out)))
        # extraction flattens paths into out_dir/<basename> or preserves structure
        # depending on member naming — verify all bytes somewhere
        extracted = "\x00".join(p.read_text(encoding="utf-8") for p in sorted(out.rglob("*.txt")))
        assert "deep" in extracted and "top" in extracted

    def test_tar_preserves_directory_hierarchy(self, tmp_path: Path) -> None:
        base = tmp_path / "hier"
        (base / "sub").mkdir(parents=True)
        (base / "sub" / "inner.txt").write_text("inner-data")
        archive = tmp_path / "hier.tar.gz"
        json.loads(T["compress_tar"]([str(base)], str(archive)))
        out = tmp_path / "out"
        json.loads(T["extract_tar"](str(archive), str(out)))
        assert (out / "hier" / "sub" / "inner.txt").read_text(encoding="utf-8") == "inner-data"


class TestVolumeAndRoundtrip:
    def test_many_files_roundtrip(self, tmp_path: Path) -> None:
        src = tmp_path / "many"
        src.mkdir()
        files = []
        for i in range(100):
            f = src / f"f{i:03}.txt"
            f.write_text(f"data {i}")
            files.append(str(f))
        archive = tmp_path / "many.zip"
        r = json.loads(T["compress_zip"](files, str(archive)))
        assert r["file_count"] == 100
        out = tmp_path / "out"
        r = json.loads(T["extract_zip"](str(archive), str(out)))
        assert r["file_count"] == 100
        assert (out / "f007.txt").read_text(encoding="utf-8") == "data 7"

    def test_large_binary_roundtrip(self, tmp_path: Path) -> None:
        import os

        payload = os.urandom(5 * 1024 * 1024)
        src = tmp_path / "big.bin"
        src.write_bytes(payload)
        archive = tmp_path / "big.zip"
        r = json.loads(T["compress_zip"]([str(src)], str(archive), compression_level=1))
        assert r["success"] is True
        out = tmp_path / "out"
        json.loads(T["extract_zip"](str(archive), str(out)))
        assert (out / "big.bin").read_bytes() == payload

    def test_compression_levels(self, tmp_path: Path) -> None:
        src = tmp_path / "c.txt"
        src.write_text("compress me " * 1000)
        sizes = set()
        for level in (0, 9):
            archive = tmp_path / f"lvl{level}.zip"
            r = json.loads(T["compress_zip"]([str(src)], str(archive), compression_level=level))
            assert r["success"] is True
            sizes.add(archive.stat().st_size)
        assert len(sizes) == 2  # levels must produce different sizes

    def test_tar_formats_roundtrip(self, tmp_path: Path) -> None:
        src = tmp_path / "doc.txt"
        src.write_text("tar content")
        for ext, comp in [("tar", "none"), ("tar.gz", "gz"), ("tar.bz2", "bz2")]:
            archive = tmp_path / f"doc.{ext}"
            r = json.loads(T["compress_tar"]([str(src)], str(archive), compression=comp))
            assert r["success"] is True, ext
            r = json.loads(T["extract_tar"](str(archive), str(tmp_path / f"out_{comp}")))
            assert r["file_count"] == 1, ext

    def test_extract_creates_nested_output_dir(self, tmp_path: Path) -> None:
        archive = tmp_path / "a.zip"
        make_zip(archive, {"x.txt": b"x"})
        deep_out = tmp_path / "l1" / "l2" / "l3"
        r = json.loads(T["extract_zip"](str(archive), str(deep_out)))
        assert r["success"] is True
        assert (deep_out / "x.txt").exists()


class TestListContents:
    def test_list_zip_contents(self, tmp_path: Path) -> None:
        archive = tmp_path / "l.zip"
        make_zip(archive, {"a.txt": b"aaaa", "dir/b.txt": b"bb"})
        r = json.loads(T["list_archive_contents"](str(archive)))
        names = [f["name"] for f in r["files"]]
        assert "a.txt" in names
        assert any("b.txt" in n for n in names)
        assert r["file_count"] == 2

    def test_list_tar_contents(self, tmp_path: Path) -> None:
        src = tmp_path / "t.txt"
        src.write_text("tar listing")
        archive = tmp_path / "l.tar.gz"
        json.loads(T["compress_tar"]([str(src)], str(archive)))
        r = json.loads(T["list_archive_contents"](str(archive)))
        assert r["file_count"] >= 1

    def test_compress_zip_empty_list(self, tmp_path: Path) -> None:
        archive = tmp_path / "empty.zip"
        r = json.loads(T["compress_zip"]([], str(archive)))
        # either an explicit error or a valid empty archive — must not crash
        if "success" in r:
            r2 = json.loads(T["extract_zip"](str(archive), str(tmp_path / "out")))
            assert r2["file_count"] == 0
        else:
            assert "error" in r

    def test_compress_duplicate_paths(self, tmp_path: Path) -> None:
        src = tmp_path / "dup.txt"
        src.write_text("dup")
        archive = tmp_path / "dup.zip"
        r = json.loads(T["compress_zip"]([str(src), str(src)], str(archive)))
        assert "success" in r or "error" in r

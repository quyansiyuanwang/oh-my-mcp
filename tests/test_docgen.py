#!/usr/bin/env python3
"""Smoke tests for the documentation generator (scripts/docs/generate_docs.py)."""

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "docs" / "generate_docs.py"
spec = importlib.util.spec_from_file_location("generate_docs", SCRIPT)
assert spec is not None and spec.loader is not None
docgen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docgen)


class TestParseHandlers:
    def test_extracts_tool_handler_functions(self, tmp_path: Path) -> None:
        source = '''"""Module doc."""
from mcp_server.tools.registry import tool_handler


@tool_handler
def my_tool(path: str, count: int = 3) -> str:
    """Do something useful.

    Args:
        path: A path.
    """
    return ""
'''
        f = tmp_path / "handlers.py"
        f.write_text(source, encoding="utf-8")
        tools = docgen.parse_handlers(f)
        assert len(tools) == 1
        assert tools[0].name == "my_tool"
        assert tools[0].description == "Do something useful."
        assert "count: int = 3" in tools[0].signature

    def test_ignores_undecorated_functions(self, tmp_path: Path) -> None:
        source = '''
def helper(x: int) -> int:
    """Not a tool."""
    return x


@tool_handler
def real_tool() -> str:
    """A real tool."""
    return ""
'''
        f = tmp_path / "handlers.py"
        f.write_text(source, encoding="utf-8")
        tools = docgen.parse_handlers(f)
        assert [t.name for t in tools] == ["real_tool"]

    def test_missing_docstring_yields_empty_description(self, tmp_path: Path) -> None:
        source = """
@tool_handler
def undocumented() -> str:
    return ""
"""
        f = tmp_path / "handlers.py"
        f.write_text(source, encoding="utf-8")
        tools = docgen.parse_handlers(f)
        assert tools[0].description == ""


class TestReplaceBlock:
    def test_replaces_between_markers(self) -> None:
        text = "before\n<!-- DOCGEN:foo:start -->\nold content\n<!-- DOCGEN:foo:end -->\nafter\n"
        result = docgen.replace_block(text, "foo", "new content", "fake.md")
        assert "new content" in result
        assert "old content" not in result
        assert "before" in result and "after" in result

    def test_missing_markers_raise(self) -> None:
        import pytest

        with pytest.raises(SystemExit):
            docgen.replace_block("no markers here", "foo", "x", "fake.md")


class TestRenderers:
    def _sample(self) -> list:
        cats = [
            docgen.CategoryInfo(
                dir_name="alpha",
                category_name="Alpha Things",
                category_name_zh="阿尔法",
                emoji="🅰️",
                description="Do alpha: with details here",
                tools=[
                    docgen.ToolInfo("alpha_one", "First tool.", "(x: int)"),
                    docgen.ToolInfo("alpha_two", "Second tool.", "()"),
                ],
            ),
            docgen.CategoryInfo(
                dir_name="beta",
                category_name="Beta Things",
                category_name_zh="贝塔",
                emoji="🅱️",
                description="Do beta",
                tools=[docgen.ToolInfo("beta_one", "Only tool.", "(y: str = 'z')")],
            ),
        ]
        return cats

    def test_counts_rendered(self) -> None:
        cats = self._sample()
        text = docgen.render_docs_index_categories(cats)
        assert "3 practical tools across 2 categories:" in text
        assert "**Alpha Things** (2 tools): Do alpha" in text

    def test_tool_reference_sections(self) -> None:
        cats = self._sample()
        text = docgen.render_tool_reference(cats)
        assert "## 🅰️ Alpha Things (Tools) (2)" in text
        assert "### `alpha_one`" in text
        assert "First tool." in text
        assert "alpha_one(x: int)" in text
        assert "---" in text  # separator between categories

    def test_short_description_strips_details(self) -> None:
        cats = self._sample()
        assert docgen.short_description(cats[0]) == "Do alpha"
        assert docgen.short_description(cats[1]) == "Do beta"


class TestBilingual:
    def test_render_tool_reference_zh_localizes_headings(self) -> None:
        cats = [
            docgen.CategoryInfo(
                dir_name="alpha",
                category_name="Alpha Things",
                category_name_zh="阿尔法",
                emoji="A",
                description="Do alpha",
                tools=[docgen.ToolInfo("t1", "Tool one.", "(x: int)")],
            )
        ]
        zh = docgen.render_tool_reference(cats, locale="zh")
        assert "## A 阿尔法 (工具) (1)" in zh
        assert "docstring" in zh
        assert "### `t1`" in zh
        en = docgen.render_tool_reference(cats)
        assert "## A Alpha Things (Tools) (1)" in en

    def test_render_docs_index_zh(self) -> None:
        cats = [
            docgen.CategoryInfo(
                dir_name="alpha",
                category_name="Alpha Things",
                category_name_zh="阿尔法",
                emoji="A",
                description="Do alpha",
                tools=[docgen.ToolInfo("t1", "Tool one.", "()")],
            )
        ]
        zh = docgen.render_docs_index_categories(cats, locale="zh")
        assert "1 个类别" in zh
        assert "阿尔法" in zh

    def test_check_bilingual_pairs_reports_missing(self) -> None:
        problems = docgen.check_bilingual_pairs()
        # the real repo must have every topic in both languages
        assert problems == []

    def test_check_doc_links_reports_broken(self, tmp_path: Path) -> None:
        # simulate by pointing ROOT at a temp tree
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "A.md").write_text("[broken](MISSING.md)", encoding="utf-8")
        (docs / "A.zh.md").write_text("x", encoding="utf-8")
        orig_root = docgen.ROOT
        try:
            docgen.ROOT = tmp_path  # type: ignore[assignment]
            problems = docgen.check_doc_links()
            assert any("MISSING.md" in p for p in problems)
        finally:
            docgen.ROOT = orig_root  # type: ignore[assignment]


class TestRealRepo:
    def test_load_categories_finds_all_plugins(self) -> None:
        categories = docgen.load_categories()
        assert len(categories) == 11
        assert all(c.tools for c in categories)
        assert docgen.total_tools(categories) == 153
        assert all(c.category_name_zh for c in categories)

    def test_check_mode_passes_on_fresh_checkout(self) -> None:
        # The committed docs must be in sync with the code
        assert docgen.run(check=True) == 0

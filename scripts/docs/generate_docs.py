#!/usr/bin/env python3
"""
Generate documentation fragments from tool metadata.

Single source of truth: each tool plugin directory under
``src/mcp_server/tools/<name>/`` provides:

- ``config.yaml``  — category_name, emoji, category_description, enabled
- ``handlers.py``  — functions decorated with ``@tool_handler`` whose
  docstrings (first line) are the tool descriptions

This script AST-parses the handlers (no imports executed) and regenerates
the count/description fragments inside the markdown docs between
``<!-- DOCGEN:<key>:start -->`` / ``<!-- DOCGEN:<key>:end -->`` markers,
plus the tool-count lines in ``pyproject.toml`` and ``main.py``.

Usage:
    python scripts/docs/generate_docs.py --write   # regenerate and write
    python scripts/docs/generate_docs.py --check   # exit 1 if out of date (CI)
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC_TOOLS = ROOT / "src" / "mcp_server" / "tools"

MARKER_PATTERN = "<!-- DOCGEN:{key}:{bound} -->"


@dataclass
class ToolInfo:
    """One @tool_handler function extracted from a plugin's handlers.py."""

    name: str
    description: str
    signature: str


@dataclass
class CategoryInfo:
    """One tool plugin directory and its aggregated metadata."""

    dir_name: str
    category_name: str
    emoji: str
    description: str
    tools: list[ToolInfo] = field(default_factory=list)


def _decorator_names(node: ast.FunctionDef) -> list[str]:
    names: list[str] = []
    for deco in node.decorator_list:
        if isinstance(deco, ast.Name):
            names.append(deco.id)
        elif isinstance(deco, ast.Attribute):
            names.append(deco.attr)
    return names


def _signature(node: ast.FunctionDef) -> str:
    """Render a compact signature like (files: List[str], output_path: str)."""
    parts: list[str] = []
    args = node.args
    pos = args.posonlyargs + args.args
    defaults: list[ast.expr | None] = [None] * (len(pos) - len(args.defaults))
    defaults += list(args.defaults)

    def render(arg: ast.arg, default: ast.expr | None) -> str:
        ann = ast.unparse(arg.annotation) if arg.annotation else ""
        piece = arg.arg
        if ann:
            piece += f": {ann}"
        if default is not None:
            piece += f" = {ast.unparse(default)}"
        return piece

    for arg, default in zip(pos, defaults):
        parts.append(render(arg, default))
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(render(arg, default))
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return f"({', '.join(parts)})"


def parse_handlers(handlers_py: Path) -> list[ToolInfo]:
    """AST-extract @tool_handler functions from a handlers.py file."""
    tree = ast.parse(handlers_py.read_text(encoding="utf-8"))
    tools: list[ToolInfo] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if "tool_handler" not in _decorator_names(node):
            continue
        docstring = (ast.get_docstring(node) or "").strip()
        description = docstring.splitlines()[0].strip() if docstring else ""
        tools.append(ToolInfo(name=node.name, description=description, signature=_signature(node)))
    return tools


def load_categories() -> list[CategoryInfo]:
    """Load all enabled plugin categories in directory order."""
    categories: list[CategoryInfo] = []
    for plugin_dir in sorted(SRC_TOOLS.iterdir()):
        config = plugin_dir / "config.yaml"
        handlers = plugin_dir / "handlers.py"
        if not plugin_dir.is_dir() or not config.exists() or not handlers.exists():
            continue
        meta = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
        if not meta.get("enabled", True):
            continue
        categories.append(
            CategoryInfo(
                dir_name=plugin_dir.name,
                category_name=str(meta["category_name"]),
                emoji=str(meta.get("emoji", "🔧")),
                description=str(meta.get("category_description", "")),
                tools=parse_handlers(handlers),
            )
        )
    return categories


def short_description(category: CategoryInfo) -> str:
    """First clause of the category description (before ':'), for compact lists."""
    return category.description.split(":")[0].strip()


def total_tools(categories: list[CategoryInfo]) -> int:
    return sum(len(c.tools) for c in categories)


# ---------------------------------------------------------------------------
# Fragment renderers
# ---------------------------------------------------------------------------


def render_readme_features(categories: list[CategoryInfo]) -> str:
    return "\n".join(
        f"- **{c.emoji} {c.category_name}** ({len(c.tools)} tools): {c.description}"
        for c in categories
    )


def render_claude_bullets(categories: list[CategoryInfo]) -> str:
    lines = []
    for c in categories:
        lines.append(f"- **{c.category_name}** ({len(c.tools)} tools): {c.description}")
    return "\n".join(lines)


def render_docs_index_categories(categories: list[CategoryInfo]) -> str:
    lines = [
        f"**{total_tools(categories)} practical tools across {len(categories)} categories:**",
        "",
    ]
    for c in categories:
        lines.append(f"- **{c.category_name}** ({len(c.tools)} tools): {short_description(c)}")
    return "\n".join(lines)


def render_tool_reference(categories: list[CategoryInfo]) -> str:
    blocks = []
    for c in categories:
        lines = [f"## {c.emoji} {c.category_name} Tools ({len(c.tools)})", ""]
        for tool in c.tools:
            lines.append(f"### `{tool.name}`")
            lines.append(tool.description or "No description.")
            lines.append("")
            lines.append(f"```python\n{tool.name}{tool.signature}\n```")
            lines.append("")
        blocks.append("\n".join(lines))
    return "\n---\n\n".join(blocks) + "\n"


# ---------------------------------------------------------------------------
# File update machinery
# ---------------------------------------------------------------------------


def replace_block(text: str, key: str, content: str, source_file: str) -> str:
    """Replace the content between DOCGEN markers, failing loudly if absent."""
    start = MARKER_PATTERN.format(key=key, bound="start")
    end = MARKER_PATTERN.format(key=key, bound="end")
    if start not in text or end not in text:
        raise SystemExit(
            f"error: {source_file} is missing DOCGEN markers for '{key}'.\n"
            f"Expected: {start} ... {end}"
        )
    pattern = re.compile(re.escape(start) + r"\n.*?" + re.escape(end), re.DOTALL)
    return pattern.sub(start + "\n" + content + "\n" + end, text)


def read_text(path: Path) -> str:
    """Read a text file preserving its content; returns LF-normalized text."""
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def write_text(path: Path, text: str, original_crlf: bool) -> None:
    if original_crlf:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def update_markdown(path: Path, blocks: dict[str, str], changed: list[str], check: bool) -> None:
    original = read_text(path)
    crlf = b"\r\n" in path.read_bytes()
    updated = original
    for key, content in blocks.items():
        updated = replace_block(updated, key, content, str(path.relative_to(ROOT)))
    if updated != original:
        changed.append(str(path.relative_to(ROOT)))
        if not check:
            write_text(path, updated, crlf)


def update_counts(
    path: Path, pattern: str, replacement: str, changed: list[str], check: bool
) -> None:
    original = read_text(path)
    crlf = b"\r\n" in path.read_bytes()
    if not re.search(pattern, original):
        raise SystemExit(
            f"error: tool-count pattern not found in {path.relative_to(ROOT)}: {pattern!r}"
        )
    updated = re.sub(pattern, replacement, original)
    if updated != original:
        rel = str(path.relative_to(ROOT))
        if rel not in changed:
            changed.append(rel)
        if not check:
            write_text(path, updated, crlf)


def update_tree_counts(
    path: Path, categories: list[CategoryInfo], changed: list[str], check: bool
) -> None:
    """Refresh per-category tool counts in ASCII project trees.

    A tree line looks like ``└── 📂 computer/  # 🖥️ Computer Use (25 tools)``.
    Any line containing ``<dir_name>/`` has its last number replaced with the
    category's real tool count, so both English and Chinese labels work.
    """
    if not path.exists():
        return
    original = read_text(path)
    crlf = b"\r\n" in path.read_bytes()
    lines = original.split("\n")
    changed_any = False
    for i, line in enumerate(lines):
        for cat in categories:
            token = f"{cat.dir_name}/"
            if token not in line or "(" not in line:
                continue
            numbers = list(re.finditer(r"\d+", line))
            if not numbers:
                continue
            last = numbers[-1]
            if int(last.group()) != len(cat.tools):
                lines[i] = line[: last.start()] + str(len(cat.tools)) + line[last.end() :]
                changed_any = True
    updated = "\n".join(lines)
    if updated != original and not changed_any:
        # defensive: no explicit change detected but bytes differ (line endings)
        changed_any = True
    if changed_any:
        rel = str(path.relative_to(ROOT))
        if rel not in changed:
            changed.append(rel)
        if not check:
            write_text(path, updated, crlf)


def run(check: bool) -> int:
    categories = load_categories()
    total = total_tools(categories)
    changed: list[str] = []

    # 1. README.md — features bullet list
    update_markdown(
        ROOT / "README.md",
        {"readme-features": render_readme_features(categories)},
        changed,
        check,
    )

    # 2. CLAUDE.md — counts line + category bullets.
    # CLAUDE.md is gitignored (local guidance file), so it is only updated
    # when present; CI checkouts skip it.
    claude_md = ROOT / "CLAUDE.md"
    if claude_md.exists():
        update_markdown(
            claude_md,
            {
                "claude-counts": f"This is a comprehensive Model Context Protocol (MCP) server built with FastMCP that provides **{total} practical tools** across **{len(categories)} categories**:",
                "claude-bullets": render_claude_bullets(categories),
            },
            changed,
            check,
        )

    # 3. docs/README.md — tool categories section
    update_markdown(
        ROOT / "docs" / "README.md",
        {"docs-categories": render_docs_index_categories(categories)},
        changed,
        check,
    )

    # 4. docs/en/TOOL_REFERENCE.md — full per-category tool sections
    update_markdown(
        ROOT / "docs" / "en" / "TOOL_REFERENCE.md",
        {"tool-reference": render_tool_reference(categories)},
        changed,
        check,
    )

    # 5. pyproject.toml description count
    update_counts(
        ROOT / "pyproject.toml",
        r"\d+ practical tools across \d+ categories",
        f"{total} practical tools across {len(categories)} categories",
        changed,
        check,
    )

    # 6. main.py docstring count
    update_counts(
        ROOT / "src" / "mcp_server" / "main.py",
        r"This MCP server provides \d+ tools across \d+ categories\.",
        f"This MCP server provides {total} tools across {len(categories)} categories.",
        changed,
        check,
    )

    # 7. Per-category counts inside ASCII project trees (en + zh)
    for rel in [
        "README.md",
        "docs/zh/ARCHITECTURE.md",
        "docs/zh/PROJECT_STRUCTURE.md",
        "docs/en/ARCHITECTURE.md",
        "docs/en/PROJECT_STRUCTURE.md",
    ]:
        update_tree_counts(ROOT / rel, categories, changed, check)
    if claude_md.exists():
        update_tree_counts(claude_md, categories, changed, check)

    # 8. Free-form count references in guides (Chinese & English phrasings)
    for rel, pattern, template in [
        ("docs/zh/BUILD.md", r"\d+ 个工具", "{total} 个工具"),
        ("docs/zh/CONFIGURATION_GUIDE_CN.md", r"\d+ 个工具", "{total} 个工具"),
        ("docs/zh/CONFIGURATION_GUIDE_CN.md", r"\d+ practical tools", "{total} practical tools"),
        ("docs/zh/COMPUTER_USE_GUIDE.md", r"共 \*\*\d+ 个工具\*\*", "共 **{total} 个工具**"),
        ("docs/en/COMPUTER_USE_GUIDE.md", r"\d+ tools\*\* in total", "{total} tools** in total"),
        ("README.md", r"Tool plugins \(\d+ categories\)", f"Tool plugins ({len(categories)} categories)"),
        ("CLAUDE.md", r"Tool plugins \(\d+ categories\)", f"Tool plugins ({len(categories)} categories)"),
    ]:
        path = ROOT / rel
        if not path.exists():
            continue
        update_counts(
            path,
            pattern,
            template.format(total=total, categories=len(categories)),
            changed,
            check,
        )

    if check:
        if changed:
            print("Documentation is out of date for:")
            for f in changed:
                print(f"  - {f}")
            print("\nRun: python scripts/docs/generate_docs.py --write")
            return 1
        print(f"Documentation is up to date ({total} tools, {len(categories)} categories).")
        return 0

    if changed:
        print("Updated:")
        for f in changed:
            print(f"  - {f}")
    else:
        print("Documentation already up to date.")
    print(f"Total: {total} tools across {len(categories)} categories.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate documentation fragments from tool metadata"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="regenerate and write documentation")
    group.add_argument("--check", action="store_true", help="verify docs are up to date (CI mode)")
    args = parser.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    sys.exit(main())

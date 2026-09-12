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

# Topics that must exist in BOTH languages: docs/<Topic>.md (English default)
# and docs/<Topic>.zh.md (Chinese).
BILINGUAL_TOPICS = [
    "README",
    "INSTALLATION",
    "SETUP_GUIDE",
    "CONFIGURATION",
    "TOOL_REFERENCE",
    "COMPUTER_USE_GUIDE",
    "SUBAGENT_GUIDE",
    "SUBAGENT_CONFIG",
    "BROWSER_CONFIG",
    "BROWSER_CONFIG_QUICKSTART",
    "SEARCH_ADVANCED",
    "ARCHITECTURE",
    "PROJECT_STRUCTURE",
    "BUILD",
    "CONTRIBUTING",
    "CHANGELOG",
]


def check_bilingual_pairs() -> list[str]:
    """Every topic must have both the English and the Chinese version."""
    problems: list[str] = []
    for topic in BILINGUAL_TOPICS:
        for rel in (f"docs/{topic}.md", f"docs/{topic}.zh.md"):
            if not (ROOT / rel).exists():
                problems.append(f"missing bilingual doc: {rel}")
    return problems


def check_doc_links() -> list[str]:
    """All relative .md links inside docs/*.md must resolve to real files."""
    problems: list[str] = []
    for md in sorted((ROOT / "docs").glob("*.md")):
        text = read_text(md)
        for target in re.findall(r"\]\(([^)#\s]+\.md)\)", text):
            if target.startswith(("http://", "https://")):
                continue
            if not (md.parent / target).resolve().exists():
                problems.append(f"{md.relative_to(ROOT)}: broken link -> {target}")
    return problems


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
    category_name_zh: str
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

    for arg, default in zip(pos, defaults, strict=False):
        parts.append(render(arg, default))
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=False):
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
                category_name_zh=str(meta.get("category_name_zh", meta["category_name"])),
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


def render_docs_index_categories(categories: list[CategoryInfo], locale: str = "en") -> str:
    if locale == "zh":
        lines = [
            f"**共 {total_tools(categories)} 个实用工具,涵盖 {len(categories)} 个类别:**",
            "",
        ]
        for c in categories:
            lines.append(
                f"- **{c.emoji} {c.category_name_zh}**({len(c.tools)} 个工具):{c.description}"
            )
        return "\n".join(lines)
    lines = [
        f"**{total_tools(categories)} practical tools across {len(categories)} categories:**",
        "",
    ]
    for c in categories:
        lines.append(f"- **{c.category_name}** ({len(c.tools)} tools): {short_description(c)}")
    return "\n".join(lines)


def render_tool_reference(categories: list[CategoryInfo], locale: str = "en") -> str:
    """Render the full tool reference. Descriptions come from the English
    docstrings (single source of truth) in both locales; the zh version
    localizes headings via category_name_zh and says so explicitly."""
    blocks = []
    for c in categories:
        display = c.category_name_zh if locale == "zh" else c.category_name
        suffix = "工具" if locale == "zh" else "Tools"
        lines = [f"## {c.emoji} {display} ({suffix}) ({len(c.tools)})", ""]
        if locale == "zh":
            lines.append("> 工具描述取自代码 docstring(英文为单一事实源)。")
            lines.append("")
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

    # 3. docs/README.md — English tool categories section
    update_markdown(
        ROOT / "docs" / "README.md",
        {"docs-categories": render_docs_index_categories(categories)},
        changed,
        check,
    )

    # 3b. docs/README.zh.md — Chinese tool categories section
    update_markdown(
        ROOT / "docs" / "README.zh.md",
        {"docs-categories": render_docs_index_categories(categories, locale="zh")},
        changed,
        check,
    )

    # 4. docs/TOOL_REFERENCE.md + docs/TOOL_REFERENCE.zh.md — full sections
    update_markdown(
        ROOT / "docs" / "TOOL_REFERENCE.md",
        {"tool-reference": render_tool_reference(categories)},
        changed,
        check,
    )
    update_markdown(
        ROOT / "docs" / "TOOL_REFERENCE.zh.md",
        {"tool-reference": render_tool_reference(categories, locale="zh")},
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
        "docs/ARCHITECTURE.zh.md",
        "docs/PROJECT_STRUCTURE.zh.md",
        "docs/ARCHITECTURE.md",
        "docs/PROJECT_STRUCTURE.md",
    ]:
        update_tree_counts(ROOT / rel, categories, changed, check)
    if claude_md.exists():
        update_tree_counts(claude_md, categories, changed, check)

    # 8. Free-form count references in guides (Chinese & English phrasings)
    for rel, pattern, template in [
        ("docs/BUILD.zh.md", r"\d+ 个工具", "{total} 个工具"),
        ("docs/CONFIGURATION.zh.md", r"\d+ 个工具", "{total} 个工具"),
        ("docs/CONFIGURATION.zh.md", r"\d+ practical tools", "{total} practical tools"),
        # these guides describe a single category, not the whole server
        ("docs/COMPUTER_USE_GUIDE.zh.md", r"共 \*\*\d+ 个工具\*\*", "共 **{computer} 个工具**"),
        ("docs/COMPUTER_USE_GUIDE.md", r"\d+ tools\*\* in total", "{computer} tools** in total"),
        (
            "README.md",
            r"\*\*\d+ practical tools\*\*",
            f"**{total} practical tools**",
        ),
        ("README.md", r"across \d+ categories", f"across {len(categories)} categories"),
        (
            "CLAUDE.md",
            r"Tool plugins \(\d+ categories\)",
            f"Tool plugins ({len(categories)} categories)",
        ),
        (
            "README.zh.md",
            r"\*\*\d+ 个实用工具\*\*",
            f"**{total} 个实用工具**",
        ),
        (
            "README.zh.md",
            r"\*\*\d+ 个类别\*\*",
            f"**{len(categories)} 个类别**",
        ),
    ]:
        path = ROOT / rel
        if not path.exists():
            continue
        computer = next(len(c.tools) for c in categories if c.dir_name == "computer")
        update_counts(
            path,
            pattern,
            template.format(total=total, categories=len(categories), computer=computer),
            changed,
            check,
        )

    if check:
        problems = check_bilingual_pairs() + check_doc_links()
        if changed or problems:
            if changed:
                print("Documentation is out of date for:")
                for f in changed:
                    print(f"  - {f}")
            if problems:
                print("Documentation structure problems:")
                for p in problems:
                    print(f"  - {p}")
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

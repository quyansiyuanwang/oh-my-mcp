# Contributing to oh-my-mcp

English | [中文](../zh/CONTRIBUTING.md)

Thanks for your interest in contributing! This project is an MCP server with
141 tools across 10 plugin categories.

## Development setup

```bash
git clone https://github.com/quyansiyuanwang/oh-my-mcp.git
cd oh-my-mcp
uv sync --all-extras
```

## Code style

The CI (`.github/workflows/lint.yml`) enforces all of the following:

```bash
uv run isort src/ tests/          # import order
uv run black src/ tests/          # formatting
uv run ruff check src/ tests/     # linting
uv run mypy src/ --strict         # type checking
```

Tests run on ubuntu/windows/macos × Python 3.12/3.13:

```bash
uv run pytest tests/ -v
```

## Adding or changing tools

1. Add the tool to the plugin's `handlers.py` with the `@tool_handler`
   decorator and a docstring (the first line becomes its description).
2. Add tests following the existing `MockMCP` pattern in `tests/`.
3. **Regenerate the documentation** — tool counts and descriptions are
   generated from code, and CI fails if they are stale:

   ```bash
   python scripts/docs/generate_docs.py --write
   ```

## Adding a new category

1. Create `src/mcp_server/tools/<name>/` with `config.yaml`
   (`category_name`, `emoji`, `category_description`, `enabled`), an
   `__init__.py` exposing `register_tools(mcp)`, and `handlers.py`.
2. The plugin is discovered automatically — no changes to `main.py`.
3. Update the docs trees (`docs/zh/ARCHITECTURE.md`,
   `docs/zh/PROJECT_STRUCTURE.md`) and run the doc generator.

## Commit style

Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:`).

## Pull requests

- Keep each PR focused; split unrelated changes.
- All CI checks must pass (lint incl. docs freshness, test matrix).
- Update `docs/en/CHANGELOG.md` under **Unreleased**.

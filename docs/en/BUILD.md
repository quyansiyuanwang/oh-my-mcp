# Build Guide

English | [中文](../zh/BUILD.md)

Package oh-my-mcp into a standalone executable with PyInstaller. The packaged
binary contains **all 141 tools across 10 categories** — plugin directories and
their `config.yaml` files are discovered and bundled automatically.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Platform: Windows / Linux / macOS

## Quick start

### Windows

```bash
# Option 1: batch script (if present in scripts/build/)
uv run python scripts/build/build.py
```

### Linux / macOS

```bash
uv run python scripts/build/build.py
```

The build script:

1. Removes stale artifacts (`*.spec`, old output).
2. Regenerates the PyInstaller command from `pyproject.toml` dependencies and
   auto-discovers every plugin (hidden imports + `config.yaml` data files).
3. Produces the packaged application.

## Packaging options

### 1. Directory mode (recommended — faster startup)

```bash
uv run python scripts/build/build.py --onedir
```

### 2. Single-file mode (easier distribution)

```bash
uv run python scripts/build/build.py --onefile
```

### 3. Clean build

```bash
uv run python scripts/build/build.py --clean
```

Options can be combined. See `uv run python scripts/build/build.py --help`
for the full list.

## What gets bundled

- All plugin `handlers.py` modules and `config.yaml` files (auto-discovered,
  required for plugin discovery in frozen mode via `sys._MEIPASS`).
- Core runtime packages collected from `pyproject.toml` dependencies
  (fastmcp, selenium, pyautogui, mss, pillow, ...).
- Excludes: tkinter, matplotlib, numpy, pandas, IPython, jupyter
  (PIL/Pillow is deliberately **not** excluded — computer-use screenshots
  require it).

## CI releases

`.github/workflows/build-release.yml` builds on `v*.*.*` tags and manual
dispatch across a 4-platform matrix (windows-x64, linux-x64, macos-x64,
macos-arm64), runs the test suite first, then attaches artifacts to a GitHub
Release with release notes generated from the plugin metadata
(`{{TOTAL_TOOLS}}`, `{{TOTAL_CATEGORIES}}`, per-category tool lines).

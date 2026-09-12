# Architecture Overview

English | [中文](../zh/ARCHITECTURE.md)

This document describes the architecture and design of oh-my-mcp, a FastMCP-based
MCP server providing 141 tools across 10 plugin categories.

## Project layout

```
oh-my-mcp/
├── src/mcp_server/              # Source code
│   ├── main.py                  # Server entry point
│   ├── utils.py                 # Shared infrastructure (errors, paths, IO, retry)
│   ├── command_executor.py      # Hardened subprocess execution (standalone)
│   ├── tools/                   # Tool plugins (auto-discovered)
│   │   ├── __init__.py          # Plugin discovery
│   │   ├── registry.py          # @tool_handler decorator & ToolPlugin
│   │   ├── search_engine.py     # Web search backend
│   │   ├── subagent_config.py   # Subagent credentials manager
│   │   ├── compression/         # 📦 Compression (5 tools)
│   │   ├── web/                 # 🌐 Web & Network (18 tools)
│   │   ├── file/                # 📁 File System (13 tools)
│   │   ├── data/                # 📊 Data Processing (15 tools)
│   │   ├── text/                # 📝 Text Processing (9 tools)
│   │   ├── system/              # 💻 System (8 tools)
│   │   ├── utility/             # 🛠️ Utilities (10 tools)
│   │   ├── subagent/            # 🤖 Subagent AI Orchestration (6 tools)
│   │   ├── browser/             # 🌐 Browser Automation (33 tools)
│   │   ├── computer/            # 🖥️ Computer Use (25 tools)
│   │   └── execution/           # Command Execution (4 tools)
│   └── cli/                     # Configuration generator CLI
├── scripts/                     # Build & doc generation scripts
└── tests/                       # Pytest suite (per category + scenarios)
```

## Core components

### 1. FastMCP server (`main.py`)

Creates the `FastMCP("oh-my-mcp")` instance, loads all plugins via
`load_all_plugins()` and registers every tool handler. Also exposes
`config://tools` and `config://version` resources whose counts are computed
**dynamically** from the loaded plugins — adding a category needs no entry-point
changes.

### 2. Plugin framework (`tools/registry.py`)

- `@tool_handler` marks a function and records it in a module-keyed registry.
- `ToolPlugin` is built from a plugin directory + its `config.yaml`
  (`category_name`, `emoji`, `category_description`, `enabled`), imports the
  plugin's `handlers` module and registers all recorded tools with
  `mcp.tool()`.
- A failing plugin is logged and skipped — one broken plugin cannot take the
  server down.

### 3. Tool plugins (`tools/*/handlers.py`)

Every handler follows the same conventions:

- Plain primitive parameters (they become the MCP tool schema).
- JSON-string return values (`json.dumps(..., indent=2, ensure_ascii=False)`).
- Three-tier exception handling: validation/security errors (warning log) →
  domain errors → blanket catch, so handlers never raise to the transport.
- Error payloads are built with `utils.error_json()` to guarantee valid JSON
  (raw interpolation of Windows paths would produce invalid escapes).
- Heavy hardware/external libraries are imported lazily behind availability
  flags, so a missing dependency degrades to an actionable error message.

### 4. Plugin discovery (`tools/__init__.py`)

Any subdirectory of `tools/` containing a `config.yaml` is a plugin. Discovery
also works in PyInstaller frozen mode via `sys._MEIPASS`. `enabled: false` in
`config.yaml` disables a plugin without deleting it.

### 5. Stateful resources

Stateful categories keep a module-level singleton, mirroring each other:

- `browser/session_manager.py` — Selenium sessions (UUID-keyed, `atexit`
  cleanup, max-5 cap, driver auto-fallback Chrome→Edge).
- `computer/computer_manager.py` — hardware library access with safety
  defaults (FAILSAFE on, action pause) and availability guards.

### 6. Infrastructure (`utils.py`)

Exception hierarchy (`ValidationError`, `SecurityError`, `BrowserError`,
`ComputerUseError`, ...), path sanitization, size-capped file IO with verbatim
newline handling, retry decorator, archive-safety validation, logging setup.

## Design principles

1. **Plugin architecture** — drop a directory with `config.yaml` + `handlers.py`
   and it is discovered, registered, documented (via `scripts/docs/generate_docs.py`)
   and packaged automatically.
2. **Safety by default** — path traversal protection, confirmation flags for
   destructive operations, size limits on extraction and reads, URL scheme
   blocking, FAILSAFE for desktop control, character whitelisting for the math
   evaluator.
3. **Errors as data** — tools return JSON error payloads instead of raising,
   so clients always get parseable results.
4. **Single source of truth** — tool metadata lives in the code (`docstrings`)
   and `config.yaml`; all count/description fragments in the docs are generated.

## Data flow

```
MCP client → FastMCP transport → ToolPlugin handler
    → validation (utils) → handler logic (stateful manager if needed)
    → JSON string result → client
```

Documentation counts/descriptions:

```
handlers.py + config.yaml ─AST→ scripts/docs/generate_docs.py
    → README.md / CLAUDE.md / docs/README.md / docs/en/TOOL_REFERENCE.md
    → CI --check gate
```

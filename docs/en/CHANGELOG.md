# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Command Execution category** (4 tools): the previously unwired
  `command_executor` infrastructure is now exposed as secure MCP tools
  - `run_command` executes allowlisted commands with shell=False, argument
    sanitization, timeout caps and output size limits; the allowlist starts
    EMPTY so nothing runs until explicitly trusted
  - `list_allowed_commands` / `add_allowed_commands` / `remove_allowed_commands`
    manage the persistent allowlist (~/.oh-my-mcp/execution_config.json)
- `grep_files` (File System, now 13 tools): content search across a directory
  tree with regex or plain text, line numbers, binary-file skipping
  (extension + NUL sniffing) and a 2MB per-file cap
- Documentation bilingual reorganization: Chinese-content docs moved from
  docs/en/ to docs/zh/, fresh English versions written; docgen now also
  refreshes per-category counts in project trees and guide references

### Changed

- Tool count 141 -> 146 across 11 categories
- **Computer Use category** (now 25 tools): AI-driven desktop control via pyautogui/mss/pyperclip/pygetwindow
  - Screen capture: `computer_screenshot` (region/monitor, file or base64), `computer_get_screen_size`,
    `computer_get_monitors`, `computer_get_pixel_color`, `computer_locate_on_screen`
  - Mouse: move, click, drag, scroll, position
  - Keyboard: `computer_type_text`, `computer_press_key`, `computer_hotkey`
  - Clipboard: read/write via pyperclip
  - Window management: list, focus, info, resize, move, minimize, maximize
  - Pacing: `computer_wait` (0-60s) between UI actions
  - Safety: FAILSAFE on by default, adjustable action pause, `computer_config_get/set`
  - Guides: `docs/zh/COMPUTER_USE_GUIDE.md` + `docs/en/COMPUTER_USE_GUIDE.md`
- **Documentation generation system** (`scripts/docs/generate_docs.py`):
  - AST-extracts tool names/descriptions/signatures from `@tool_handler` docstrings
    and category metadata from each plugin's `config.yaml` (new `emoji` field)
  - Regenerates count/description fragments between `<!-- DOCGEN:... -->` markers in
    README.md, CLAUDE.md, docs/README.md, docs/en/TOOL_REFERENCE.md, plus counts in
    pyproject.toml, main.py and per-category counts in project trees and guides
  - `--check` mode fails CI when docs are stale
- **Complex scenario test suites** (67 cases): zip-slip/symlink/zip-bomb security,
  malformed archives, unicode filenames, large roundtrips (compression); CRLF
  preservation, deep nesting, size limits (file); cross-format roundtrips,
  special values (data)
- English versions of core docs: INSTALLATION, CONTRIBUTING, BUILD, ARCHITECTURE,
  PROJECT_STRUCTURE, COMPUTER_USE_GUIDE

### Changed

- Tool count 116 -> 141 across 10 categories (README, docs, package description)
- `compress_zip`/`compress_tar` accept directories and pack them recursively with
  hierarchy preserved (previously flattened to basenames / rejected directories)
- Documentation reorganized into true bilingual layout: Chinese-content docs moved
  from `docs/en/` to `docs/zh/` (ARCHITECTURE, BUILD, INSTALLATION, CONTRIBUTING,
  PROJECT_STRUCTURE); README resource lists consolidated
- `uv.lock` is now committed — it was gitignored, which let CI re-resolve to newer
  tool versions (ruff 0.16) that failed the build
- Build: removed PIL from PyInstaller excludes (required for computer-use screenshots)
- Added `computer` optional dependency group and core dependencies for desktop control

### Fixed

- `read_file`/`write_file`/`append_file`: newline translation corrupted `\r\n`
  content on Windows (now byte-faithful via `newline=""`)
- `copy_file` silently placed files inside an existing destination directory
- `flatten_json` dropped empty dict/list values
- `validate_json_schema` reported booleans as numbers
- 51 error responses interpolated paths into JSON templates producing invalid
  JSON on Windows paths (now use shared `error_json()` helper)
- `extract_tar` hardening: `filter="data"` (Python 3.14 compat, symlink escapes)
- `calculate_expression` rejected documented math functions; identifier whitelist
  now allows sqrt/sin/abs/max/... while keeping eval sandboxed
- `date_to_timestamp` ignored `timezone="utc"`
- `locate_on_screen` unusable without OpenCV (graceful exact-match fallback)

## [0.1.1] - 2026-02-11

### Added

- **Persistent Configuration Management**: New configuration system for API credentials
  - `SubagentConfig` class for persistent credential storage (~/.subagent_config.json)
  - Three new MCP tools: `subagent_config_set`, `subagent_config_get`, `subagent_config_list`
  - Automatic file permissions (600) for config file on Unix/Linux/macOS
  - Configuration priority: Environment Variables > Config File > Defaults
  - Sensitive data masking in all output
  - Support for custom config file paths
  - Per-project configuration support

### Changed

- Updated Subagent tools from 3 to 6 total tools
- Enhanced all AI client classes (OpenAI, Anthropic) to use config manager
- Updated SUBAGENT_GUIDE.md with persistent configuration examples
- Updated README.md tool count from 74+ to 77+ tools

### Documentation

- New guide: `docs/SUBAGENT_CONFIG.md` - Complete configuration management guide
- New example: `examples/subagent_config_example.py` - 8 configuration examples
- Updated existing guides with configuration management information

## [0.1.0] - 2026-02-11

### Added

- Initial release of MCP Server
- 95+ practical tools across 10 categories (later consolidated to 83 tools across 8 categories):
  - Compression (5 tools): ZIP/TAR compression and extraction
  - Web & Network (15 tools): web search, page fetching, HTML parsing, downloads
  - File System (12 tools): read, write, search files and directories
  - Data Processing (15 tools): JSON, CSV, XML, YAML, TOML parsing
  - Text Processing (9 tools): regex, encoding, email/URL extraction
  - System (8 tools): system info, CPU/memory monitoring
  - Utilities (10 tools): UUID, hashing, date/time, passwords
  - Python Development (8 tools): code execution, syntax validation
  - UV Package Manager (9 tools): fast package management
  - Pylance/Pyright (4 tools): type checking and diagnostics
- Modular architecture with separate tool modules
- Comprehensive error handling and logging
- Configuration generator for Claude Desktop
- HTTP server for configuration management
- Complete test suite
- Documentation and examples

[0.1.1]: https://github.com/quyansiyuanwang/oh-my-mcp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/quyansiyuanwang/oh-my-mcp/releases/tag/v0.1.0

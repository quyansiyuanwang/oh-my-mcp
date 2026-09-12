# oh-my-mcp

English | [中文](README.zh.md)

A powerful Model Context Protocol (MCP) server with **154 practical tools**
across 11 categories, built using [FastMCP](https://github.com/jlowin/fastmcp).

[![Build and Release](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/build-release.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/build-release.yml)
[![Tests](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/tests.yml)
[![Lint](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/lint.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/lint.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/quyansiyuanwang/oh-my-mcp)

## 🚀 Features

oh-my-mcp provides tools for:

<!-- DOCGEN:readme-features:start -->
- **🌐 Browser Automation** (33 tools): Selenium-based browser automation: navigation, interaction, screenshots, JS execution, console logs, cookies, network monitoring, form filling, multi-tab management
- **📦 Compression** (5 tools): ZIP/TAR compression and extraction with security features
- **🖥️ Computer Use** (26 tools): AI desktop control: screen capture (multi-monitor, base64/file), mouse control (move/click/drag/scroll), keyboard input (typing/keys/hotkeys), clipboard access, window management, safety failsafe configuration
- **📊 Data Processing** (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- **⚡ Command Execution** (5 tools): Secure allowlist-based command execution: run whitelisted commands with argument sanitization, timeout protection, output size limits and audit logging; manage the persistent command allowlist
- **📁 File System** (16 tools): Read, write, search files and directories, file comparison
- **🤖 Subagent AI Orchestration** (6 tools): Delegate subtasks to external AI models with parallel execution and cost tracking
- **💻 System** (11 tools): System info, CPU/memory monitoring, environment variables
- **📝 Text Processing** (9 tools): Regex, encoding, email/URL extraction, text similarity
- **🛠️ Utilities** (10 tools): UUID, hashing, date/time operations, math, password generation
- **🌐 Web & Network** (18 tools): Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup
<!-- DOCGEN:readme-features:end -->

## 📚 Documentation

The full index lives in **[docs/README.md](docs/README.md)** — every topic is
available in English (`X.md`, default) and Chinese (`X.zh.md`). Highlights:

| Document | |
|---|---|
| Installation | [INSTALLATION.md](docs/INSTALLATION.md) / [中文](docs/INSTALLATION.zh.md) |
| Tool Reference (all 146 tools) | [TOOL_REFERENCE.md](docs/TOOL_REFERENCE.md) / [中文](docs/TOOL_REFERENCE.zh.md) |
| Computer Use Guide | [COMPUTER_USE_GUIDE.md](docs/COMPUTER_USE_GUIDE.md) / [中文](docs/COMPUTER_USE_GUIDE.zh.md) |
| Setup Guide (Claude Desktop) | [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) / [中文](docs/SETUP_GUIDE.zh.md) |
| Command Execution | [CONFIGURATION.md](docs/CONFIGURATION.md) · see Tool Reference |
| Build Guide | [BUILD.md](docs/BUILD.md) / [中文](docs/BUILD.zh.md) |
| Architecture | [ARCHITECTURE.md](docs/ARCHITECTURE.md) / [中文](docs/ARCHITECTURE.zh.md) |
| Subagent Guide | [SUBAGENT_GUIDE.md](docs/SUBAGENT_GUIDE.md) / [中文](docs/SUBAGENT_GUIDE.zh.md) |
| Contributing | [CONTRIBUTING.md](docs/CONTRIBUTING.md) / [中文](docs/CONTRIBUTING.zh.md) |
| Changelog | [CHANGELOG.md](docs/CHANGELOG.md) / [中文](docs/CHANGELOG.zh.md) |

Tool counts and descriptions in the docs are generated from code — see
[Documentation Generation](#documentation-generation).

## 📦 Installation

```bash
git clone https://github.com/quyansiyuanwang/oh-my-mcp.git
cd oh-my-mcp
pip install -e .            # or: uv sync --all-extras
```

Configure Claude Desktop:

```bash
python -m mcp_server.cli.config --claude
```

Start the server:

```bash
python -m mcp_server.main
```

Details: [Installation Guide](docs/INSTALLATION.md) and
[Setup Guide](docs/SETUP_GUIDE.md).

## 🔧 Configuration

### Logging

Logs are configured in `mcp_server/utils.py` — level, destinations and format.

### Security Features

- **Path validation**: prevents path traversal attacks
- **Safe evaluation**: math expressions only allow whitelisted operations
- **Masked values**: sensitive environment variables are masked
- **Confirmation required**: file deletion requires `confirm=True`
- **Allowlisted execution**: commands only run after explicit trust
- **Retry logic**: network operations retry up to 3 times

## 🛡️ Error Handling

All tools return JSON with descriptive messages instead of raising:

- **ValidationError** — invalid input parameters
- **NetworkError** — network request failures
- **FileOperationError** — file system errors
- **DataProcessingError** — data parsing/conversion errors

## 📝 Development

### Project Structure

```
oh-my-mcp/
├── pyproject.toml               # Dependencies & tool config
├── configure.py                 # Interactive setup wizard
└── src/
    └── mcp_server/
        ├── main.py              # Server entry point
        ├── utils.py             # Infrastructure & utilities
        ├── command_executor.py  # Secure command execution
        ├── cli/config.py        # Configuration generator
        └── tools/               # Tool plugins (11 categories, auto-discovered)
```

Full layout: [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md).

### Adding New Tools

```python
from mcp_server.tools.registry import tool_handler

@tool_handler
def your_tool(param: str) -> str:
    """Tool description.

    Args:
        param: Parameter description

    Returns:
        Return value description
    """
    ...
```

### Documentation Generation

Tool counts and descriptions in the docs are **generated from code** (AST
analysis of `@tool_handler` docstrings + each plugin's `config.yaml`). After
adding, removing, or renaming tools run:

```bash
python scripts/docs/generate_docs.py --write
```

CI verifies docs are fresh with `--check` and fails if they are out of date.
Generated fragments live between `<!-- DOCGEN:...:start/end -->` markers; do
not edit inside them.

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md). Client configuration details:
[SETUP_GUIDE.md](docs/SETUP_GUIDE.md).

## 📄 License

This project is provided as-is for educational and practical use.

## 🔗 Links

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

Enjoy oh-my-mcp! 🚀

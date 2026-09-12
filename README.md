# oh-my-mcp

A powerful Model Context Protocol (MCP) server with **141 practical tools** across 10 categories, built using [FastMCP](https://github.com/jlowin/fastmcp).

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
- **🖥️ Computer Use** (25 tools): AI desktop control: screen capture (multi-monitor, base64/file), mouse control (move/click/drag/scroll), keyboard input (typing/keys/hotkeys), clipboard access, window management, safety failsafe configuration
- **📊 Data Processing** (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- **⚡ Command Execution** (4 tools): Secure allowlist-based command execution: run whitelisted commands with argument sanitization, timeout protection, output size limits and audit logging; manage the persistent command allowlist
- **📁 File System** (13 tools): Read, write, search files and directories, file comparison
- **🤖 Subagent AI Orchestration** (6 tools): Delegate subtasks to external AI models with parallel execution and cost tracking
- **💻 System** (8 tools): System info, CPU/memory monitoring, environment variables
- **📝 Text Processing** (9 tools): Regex, encoding, email/URL extraction, text similarity
- **🛠️ Utilities** (10 tools): UUID, hashing, date/time operations, math, password generation
- **🌐 Web & Network** (18 tools): Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup
<!-- DOCGEN:readme-features:end -->

## 📚 Documentation

The full index lives in **[docs/README.md](docs/README.md)**. Highlights:

| Document | English | 中文 |
|---|---|---|
| Installation | [docs/en/INSTALLATION.md](docs/en/INSTALLATION.md) | [docs/zh/INSTALLATION.md](docs/zh/INSTALLATION.md) |
| Tool Reference (all 141 tools) | [docs/en/TOOL_REFERENCE.md](docs/en/TOOL_REFERENCE.md) | — |
| Computer Use Guide | [docs/en/COMPUTER_USE_GUIDE.md](docs/en/COMPUTER_USE_GUIDE.md) | [docs/zh/COMPUTER_USE_GUIDE.md](docs/zh/COMPUTER_USE_GUIDE.md) |
| Setup Wizard Guide | — | [docs/zh/SETUP_GUIDE.md](docs/zh/SETUP_GUIDE.md) |
| Build Guide | [docs/en/BUILD.md](docs/en/BUILD.md) | [docs/zh/BUILD.md](docs/zh/BUILD.md) |
| Architecture | [docs/en/ARCHITECTURE.md](docs/en/ARCHITECTURE.md) | [docs/zh/ARCHITECTURE.md](docs/zh/ARCHITECTURE.md) |
| Project Structure | [docs/en/PROJECT_STRUCTURE.md](docs/en/PROJECT_STRUCTURE.md) | [docs/zh/PROJECT_STRUCTURE.md](docs/zh/PROJECT_STRUCTURE.md) |
| Subagent Guide | — | [docs/zh/SUBAGENT_GUIDE.md](docs/zh/SUBAGENT_GUIDE.md) |
| Contributing | [docs/en/CONTRIBUTING.md](docs/en/CONTRIBUTING.md) | [docs/zh/CONTRIBUTING.md](docs/zh/CONTRIBUTING.md) |
| Changelog | [docs/en/CHANGELOG.md](docs/en/CHANGELOG.md) | — |

Tool counts and descriptions in the docs are generated from code — see
[Documentation Generation](#documentation-generation).


### ⚡ 快速安装与配置

1. 安装依赖并开发模式安装：

  ```bash
  pip install -e .
  ```

2. 运行交互式配置向导（推荐）：

  ```bash
  uv run configure.py
  ```

  或直接为Claude Desktop生成配置：

  ```bash
  python -m mcp_server.cli.config --claude
  ```

  或启动HTTP配置服务：

  ```bash
  python -m mcp_server.cli.config --http-server --port 8765
  ```

  详细配置说明见：[docs/zh/SETUP_GUIDE.md](docs/zh/SETUP_GUIDE.md)

3. 启动MCP服务：

  ```bash
  python -m mcp_server.main
  ```

  启动后可通过Claude Desktop或MCP客户端连接使用。

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager


---


---

## 📚 Tool Reference

For the full list of tools, usage examples, and API details, see [docs/en/TOOL_REFERENCE.md](docs/en/TOOL_REFERENCE.md).

## 🔧 Configuration

### Logging

Logs are configured in `mcp_server/utils.py`. You can adjust:

- Log level (INFO, DEBUG, WARNING, ERROR)
- Output destinations (console, file)
- Log format

### File Size Limits

File operations have safety limits:

- `read_file`: 10MB max file size
- `safe_write_file`: Creates parent directories automatically

### Security Features

- **Path validation**: Prevents path traversal attacks
- **Safe evaluation**: Math expressions only allow safe operations
- **Masked values**: Sensitive environment variables are masked
- **Confirmation required**: File deletion requires `confirm=True`
- **Retry logic**: Network operations retry up to 3 times

---

## 🛡️ Error Handling

All tools include comprehensive error handling:

- **ValidationError**: Invalid input parameters
- **NetworkError**: Network request failures
- **FileOperationError**: File system errors
- **DataProcessingError**: Data parsing/conversion errors

Errors are returned as JSON with descriptive messages.

---

## 📝 Development

### Project Structure

```
oh-my-mcp/
├── pyproject.toml               # Dependencies
├── configure.py                 # Interactive setup wizard
├── README.md                    # Documentation
└── src/
    └── mcp_server/
        ├── __init__.py              # Package init
        ├── main.py                  # Server entry point
        ├── utils.py                 # Infrastructure & utilities
        ├── command_executor.py      # Secure command execution
        ├── cli/
        │   └── config.py            # Configuration generator
        └── tools/                   # Tool plugins (11 categories)
            ├── __init__.py          # Plugin auto-discovery
            ├── registry.py          # @tool_handler & ToolPlugin
            ├── search_engine.py     # Web search backend
            ├── subagent_config.py   # Subagent config manager
            ├── compression/         # Compression tools (5)
            ├── web/                 # Web & Network tools (18)
            ├── file/                # File System tools (13)
            ├── data/                # Data Processing tools (15)
            ├── text/                # Text Processing tools (9)
            ├── system/              # System tools (8)
            ├── utility/             # Utility tools (10)
            ├── subagent/            # AI Orchestration tools (6)
            ├── browser/             # Browser Automation tools (33)
            ├── computer/            # Computer Use tools (25)
            └── execution/           # Command Execution tools (4)
```

### Adding New Tools

Create a new tool in the appropriate plugin's `handlers.py`:

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
    try:
        # Your implementation
        return result
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return f"Error: {str(e)}"
```

### Testing

Start the server and test tools using an MCP client or the FastMCP testing utilities.

### Documentation Generation

Tool counts and descriptions in the docs are **generated from code** (AST analysis of
`@tool_handler` docstrings + each plugin's `config.yaml`). After adding, removing, or
renaming tools — or editing their docstrings / `config.yaml` metadata — run:

```bash
python scripts/docs/generate_docs.py --write
```

CI verifies docs are fresh with `--check` and fails if they are out of date. Generated
fragments live between `<!-- DOCGEN:...:start/end -->` markers; do not edit inside them.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional tool categories
- Enhanced error handling
- Performance optimizations
- More comprehensive tests
- Additional external API integrations

---

## 📄 License

This project is provided as-is for educational and practical use.

---

## 🔗 Links

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/)

---

## 🔧 Configuration Management

### Configuration Generator Tool

The `python -m mcp_server.cli.config` command provides multiple ways to configure MCP clients:

```bash
# Quick install to Claude Desktop
python -m mcp_server.cli.config --claude

# Run HTTP server on custom port
python -m mcp_server.cli.config --http-server --port 9000

# Generate config file with custom server name
python -m mcp_server.cli.config --server-name my-tools --output config.json

# Show configuration in console
python -m mcp_server.cli.config --show-config
```

### Configuration Server Endpoints

When running with `--http-server`:

| Endpoint      | Description                          |
| ------------- | ------------------------------------ |
| `GET /config` | Returns MCP configuration JSON       |
| `GET /info`   | Returns server information and paths |
| `GET /health` | Health check endpoint                |

Example usage:

```bash
# Start server on port 8765
python -m mcp_server.cli.config --http-server

# Get configuration
curl http://localhost:8765/config

# Get server info
curl http://localhost:8765/info
```

---

Enjoy oh-my-mcp! 🚀

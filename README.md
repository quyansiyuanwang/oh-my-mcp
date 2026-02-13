# Comprehensive MCP Server

A powerful Model Context Protocol (MCP) server with **116 practical tools** across 9 categories, built using [FastMCP](https://github.com/jlowin/fastmcp).

[![Build and Release](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/build-release.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/build-release.yml)
[![Tests](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/tests.yml)
[![Lint](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/lint.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/lint.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/quyansiyuanwang/oh-my-mcp)

## 🚀 Features

This comprehensive MCP server provides tools for:

- **📦 Compression** (5 tools): ZIP/TAR compression and extraction with security features
- **🌐 Web & Network** (18 tools): Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup
- **📁 File System** (12 tools): Read, write, search files and directories, file comparison
- **📊 Data Processing** (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- **📝 Text Processing** (9 tools): Regex, encoding, email/URL extraction, text similarity
- **💻 System** (8 tools): System info, CPU/memory monitoring, environment variables
- **🛠️ Utilities** (10 tools): UUID, hashing, date/time operations, math, password generation
- **🤖 Subagent AI** (6 tools): Delegate subtasks to external AI models (OpenAI/Anthropic), parallel execution, conditional branching, persistent config
- **🌐 Browser Automation** (33 tools): Selenium-based browser control, page navigation, element interaction, screenshots, JavaScript execution, multi-tab management

> **Note:** Python Development, UV Package Manager, and Pylance/Pyright tools have been removed from the packaged version as they require external Python interpreters and package managers. All remaining tools work completely standalone.

## 📚 Documentation

- **[📖 Documentation Index](docs/README.md)** - Complete documentation hub (中文)
- **[🏗️ Project Structure](docs/en/PROJECT_STRUCTURE.md)** - Detailed project organization
- **[🎯 Setup Guide](docs/zh/SETUP_GUIDE.md)** - Interactive configuration wizard guide
- **[📦 Build Guide](docs/en/BUILD.md)** - Package for Windows/Linux distribution
- **[🏛️ Architecture Guide](docs/en/ARCHITECTURE.md)** - System architecture and design
- **[🧪 Subagent Guide](docs/zh/SUBAGENT_GUIDE.md)** - AI orchestration features


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
        └── tools/                   # Tool plugins (9 categories)
            ├── __init__.py          # Plugin auto-discovery
            ├── registry.py          # @tool_handler & ToolPlugin
            ├── search_engine.py     # Web search backend
            ├── subagent_config.py   # Subagent config manager
            ├── compression/         # Compression tools (5)
            ├── web/                 # Web & Network tools (18)
            ├── file/                # File System tools (12)
            ├── data/                # Data Processing tools (15)
            ├── text/                # Text Processing tools (9)
            ├── system/              # System tools (8)
            ├── utility/             # Utility tools (10)
            └── subagent/            # AI Orchestration tools (6)
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

## 📖 Additional Resources

### Documentation

- [📚 Documentation Hub](docs/README.md) - Complete documentation index (中文)
- [🏗️ Project Structure](docs/en/PROJECT_STRUCTURE.md) - Project organization guide
- [🏛️ Architecture](docs/en/ARCHITECTURE.md) - System architecture and design
- [📋 Test Report](tests/) - Test suite

### Configuration & Setup

- [⚙️ Configuration Guide (CN)](docs/zh/CONFIGURATION_GUIDE_CN.md) - Complete configuration reference
- [🎯 Setup Guide](docs/zh/SETUP_GUIDE.md) - Step-by-step setup instructions

### Build & Deploy

- [📦 Build Guide](docs/en/BUILD.md) - Package for Windows/Linux
- [🚀 Installation Guide](docs/en/INSTALLATION.md) - Installation details

### Advanced Features

- [🤖 Subagent Configuration](docs/zh/SUBAGENT_CONFIG.md) - AI task delegation setup
- [🧠 Subagent Guide](docs/zh/SUBAGENT_GUIDE.md) - AI orchestration features
- [🔍 Advanced Search](docs/zh/SEARCH_ADVANCED.md) - Search functionality details

### Developer Resources

- [🏛️ Architecture Guide](docs/en/ARCHITECTURE.md) - System architecture and design
- [🤝 Contributing Guide](docs/en/CONTRIBUTING.md) - How to contribute
- [📝 Changelog](docs/en/CHANGELOG.md) - Version history



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

Enjoy your comprehensive MCP server! 🚀

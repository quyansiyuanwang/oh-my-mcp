# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Model Context Protocol (MCP) server built with FastMCP that provides 95+ practical tools across 10 categories:
- Compression (5 tools): ZIP/TAR compression and extraction
- Web & Network (15 tools): web search, page fetching, HTML parsing, downloads, HTTP API client
- File System (12 tools): read, write, search files and directories, file comparison
- Data Processing (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- Text Processing (9 tools): regex, encoding, email/URL extraction, text similarity
- System (8 tools): system info, CPU/memory monitoring, environment variables
- Utilities (10 tools): UUID, hashing, date/time operations, math, password generation
- Python Development (8 tools): code execution, syntax validation, AST analysis, module introspection
- UV Package Manager (9 tools): fast package management, virtual environments, dependency management
- Pylance/Pyright (4 tools): type checking, code analysis, diagnostics

## Setup and Installation

```bash
# Install dependencies (requires Python 3.12+)
pip install -e .

# Quick setup for Claude Desktop
python generate_config.py --claude

# Run the MCP server directly
python main.py

# Run HTTP configuration server
python generate_config.py --http-server --port 8765
```

## Architecture

### Modular Tool Organization

The codebase follows a modular architecture where each tool category is in a separate module:

```
mcp_server/
├── __init__.py
├── utils.py              # Infrastructure: logging, errors, validation, retry logic
├── command_executor.py   # Secure command execution infrastructure
├── compression_tools.py  # File compression (ZIP, TAR)
├── web_tools.py          # Web & network tools
├── file_tools.py         # File system operations
├── data_tools.py         # JSON/CSV/XML/YAML/TOML processing
├── text_tools.py         # Text processing and regex
├── system_tools.py       # System monitoring and info
├── utility_tools.py      # UUID, hashing, date/time, math, passwords
├── python_tools.py       # Python development tools
├── uv_tools.py           # UV package manager tools
└── pylance_tools.py      # Pylance/Pyright type checking tools
```

### Tool Registration Pattern

Each tool module exports a `register_tools(mcp)` function that registers tools with the FastMCP server:

```python
def register_tools(mcp):
    """Register all tools in this module."""

    @mcp.tool()
    def tool_name(param: str) -> str:
        """Tool description.

        Args:
            param: Parameter description

        Returns:
            JSON string with results or error
        """
        try:
            # Implementation
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Tool failed: {e}")
            return json.dumps({"error": str(e)})
```

The main.py entry point imports all modules and calls their `register_tools()` functions to build the complete server.

### Infrastructure (utils.py)

The utils module provides shared infrastructure:
- **Logging**: Dual output to console and mcp_server.log
- **Custom Exceptions**: ValidationError, NetworkError, FileOperationError, DataProcessingError, CommandExecutionError, CommandValidationError, CommandTimeoutError, SecurityError
- **Retry Logic**: `@retry` decorator for network operations (3 attempts)
- **Validation**: URL validation, path sanitization, safe file operations, command path validation
- **Safety Limits**: File size limits (10MB for read_file, 500MB for archive extraction)
- **Archive Security**: ZIP bomb protection, path traversal prevention
- **Command Execution**: Constants and utilities for secure command execution

### Command Execution Infrastructure (command_executor.py)

The command_executor module provides secure command execution for Python development tools:

**CommandValidator Class**:
- **Command Whitelist**: Only allows python, python3, uv, pyright, pyright-python
- **Argument Validation**: Checks for dangerous characters, path traversal, argument length
- **Dangerous Pattern Detection**: Blocks shell injection attempts, dangerous operations
- **Sanitization**: Removes null bytes, trims whitespace

**CommandExecutor Class**:
- **Secure Execution**: Uses subprocess.run() with shell=False to prevent injection
- **Timeout Protection**: Default 30s, max 300s
- **Output Limits**: Maximum 10MB output, automatically truncated
- **Working Directory Isolation**: Validates and restricts working directories
- **Audit Logging**: Records all command executions with timestamps
- **Error Handling**: Comprehensive error handling with specific exception types

**Security Features**:
- Command whitelist enforcement
- No shell=True usage (prevents shell injection)
- Path traversal prevention
- Sensitive information filtering in output
- Resource limits (timeout, output size)
- Comprehensive audit trail

### Configuration System

The `generate_config.py` script provides multiple configuration methods:
- `--claude`: Auto-install to Claude Desktop config (merges with existing)
- `--http-server`: Run HTTP server with /config, /info, /health endpoints
- `--output`: Generate JSON config file
- `--show-config`: Display configuration in console

## Adding New Tools

To add a new tool:

1. Choose the appropriate module (or create a new one for a new category)
2. Add the tool function inside the `register_tools(mcp)` function
3. Use the `@mcp.tool()` decorator
4. Follow the error handling pattern (try/except with logger.error)
5. Return JSON strings for structured data
6. Import the module in main.py if it's new
7. Call `your_module.register_tools(mcp)` in main.py

## Key Dependencies

- **fastmcp**: MCP server framework (>=2.14.5)
- **requests**: HTTP operations
- **beautifulsoup4**: HTML parsing
- **duckduckgo-search**: Free web search (no API key)
- **psutil**: System monitoring
- **python-dateutil**: Date/time utilities
- **lxml**: XML processing
- **pyyaml**: YAML configuration file support (>=6.0)
- **tomli**: TOML configuration file support (>=2.0.0, Python 3.11+ uses built-in tomllib)

## Resources

The server exposes MCP resources:
- `config://tools`: List all tools by category
- `config://version`: Server version and features
- `system://info`: Real-time system information
- `system://stats`: Real-time system statistics

## Logging

Logs are written to:
- Console (stdout)
- `mcp_server.log` file

Log level is INFO by default, configured in utils.py.

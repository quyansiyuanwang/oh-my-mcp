# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Model Context Protocol (MCP) server built with FastMCP that provides **116 practical tools** across **9 categories**:

- **Compression** (5 tools): ZIP/TAR compression and extraction with security features
- **Web & Network** (18 tools): Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup
- **File System** (12 tools): Read, write, search files and directories, file comparison
- **Data Processing** (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- **Text Processing** (9 tools): Regex, encoding, email/URL extraction, text similarity
- **System** (8 tools): System info, CPU/memory monitoring, environment variables
- **Utilities** (10 tools): UUID, hashing, date/time operations, math, password generation
- **Subagent AI Orchestration** (6 tools): Delegate subtasks to external AI models (OpenAI/Anthropic), parallel execution, conditional branching, persistent config
- **Browser Automation** (33 tools): Selenium-based browser control, page navigation, element interaction, screenshots, JavaScript execution, console logs, cookies, network monitoring, form filling, multi-tab management, configuration management

## Setup and Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager
- Optional: uv for faster package management

### Installation Methods

**Method 1: Interactive Configuration Wizard (Recommended)**

```bash
uv run configure.py
```

This wizard will guide you through:

- Environment verification
- Dependencies installation
- Subagent API configuration (OpenAI/Anthropic)
- Claude Desktop integration

**Method 2: Quick Setup**

```bash
# Install dependencies
pip install -e .

# Configure Claude Desktop automatically
python -m mcp_server.cli.config --claude

# Or run HTTP configuration server on port 8765
python -m mcp_server.cli.config --http-server --port 8765
```

**Method 3: Manual Setup**

```bash
# Install package
pip install -e .

# Run the MCP server directly
python -m mcp_server.main

# Or if installed as package
oh-my-mcp
```

## Architecture

### Project Structure

```
oh-my-mcp/
├── src/
│   └── mcp_server/
│       ├── main.py                  # Server entry point
│       ├── utils.py                 # Shared infrastructure & utilities
│       ├── command_executor.py      # Secure command execution
│       ├── cli/
│       │   ├── __init__.py
│       │   └── config.py           # Configuration generator CLI
│       └── tools/                  # Tool plugins (9 categories)
│           ├── __init__.py         # Plugin auto-discovery
│           ├── registry.py         # @tool_handler decorator & ToolPlugin class
│           ├── search_engine.py    # Web search backend
│           ├── subagent_config.py  # Subagent configuration manager
│           ├── compression/        # ZIP/TAR compression (5 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── web/                # Web & network operations (18 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── file/               # File system operations (12 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── data/               # Data processing (15 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── text/               # Text processing (9 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── system/             # System utilities (8 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── utility/            # General utilities (10 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── subagent/           # AI orchestration (6 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           └── browser/            # Browser automation (33 tools)
│               ├── __init__.py
│               ├── config.yaml
│               ├── session_manager.py
│               └── handlers.py
├── tests/                          # Comprehensive test suite
├── docs/                           # Documentation
├── examples/                       # Usage examples
├── configure.py                    # Interactive setup wizard
├── pyproject.toml                  # Project configuration
└── README.md                       # User documentation
```

### Plugin-Based Tool Organization

Each tool category is implemented as a **plugin subdirectory** under `src/mcp_server/tools/`. Each plugin contains:

- `config.yaml` — Plugin metadata (category name, description, enabled flag)
- `handlers.py` — Tool handler functions decorated with `@tool_handler`
- `__init__.py` — Package marker

This plugin architecture provides:

- **Auto-Discovery**: Plugins are automatically found by scanning for `config.yaml` files
- **Separation of Concerns**: Each plugin is self-contained
- **Easy Maintenance**: Tools can be added/modified without affecting others
- **Hot Toggle**: Plugins can be disabled via `enabled: false` in `config.yaml`
- **Scalability**: New categories are added as new plugin directories — no changes to `main.py` needed

### Tool Registration Pattern

Each plugin uses the `@tool_handler` decorator from `registry.py`:

```yaml
# config.yaml
category_name: "Category Name"
category_description: "Brief description of the category"
enabled: true
```

```python
# handlers.py
from mcp_server.tools.registry import tool_handler

@tool_handler
def tool_name(param: str) -> str:
    """Tool description.

    Args:
        param: Parameter description

    Returns:
        JSON string with results or error
    """
    try:
        result = {"status": "success", "data": "..."}
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return json.dumps({"error": str(e)})
```

The `main.py` entry point uses auto-discovery to load and register all plugins:

```python
from mcp_server.tools import load_all_plugins

plugins = load_all_plugins()
for plugin in plugins:
    plugin.register_to_mcp(mcp)
```

The `load_all_plugins()` function in `tools/__init__.py`:
1. Scans the `tools/` directory for subdirectories containing `config.yaml`
2. Loads plugin configuration from `config.yaml`
3. Skips disabled plugins (`enabled: false`)
4. Dynamically imports `handlers.py` via `importlib`
5. Collects functions decorated with `@tool_handler` from the global registry
6. Returns `ToolPlugin` instances ready to register with MCP

### Infrastructure (utils.py)

The `utils.py` module provides shared infrastructure used across all tool modules:

**Logging System**:

- Dual output to console (stdout) and `mcp_server.log` file
- INFO level logging by default
- Structured format with timestamps

**Custom Exception Hierarchy**:

- `MCPServerError` - Base exception class
- `ValidationError` - Input validation failures
- `NetworkError` - Network operation failures
- `FileOperationError` - File operation failures
- `DataProcessingError` - Data processing failures
- `CommandExecutionError` - Command execution failures
- `CommandValidationError` - Command validation failures
- `CommandTimeoutError` - Command timeout errors
- `SecurityError` - Security validation failures

**Retry Logic**:

- `@retry` decorator for automatic retry with exponential backoff
- Default: 3 attempts for network operations
- Configurable retry count and delay

**Validation Utilities**:

- `validate_url()` - URL format validation
- `sanitize_path()` - Path sanitization and validation
- `validate_command_path()` - Command path validation
- Safe file operation wrappers

**Safety Limits**:

- File read size limit: 10MB (configurable)
- Archive extraction size limit: 500MB
- Command output size limit: 10MB
- Command timeout: 30s default, 300s maximum

**Archive Security**:

- ZIP bomb detection and prevention
- Path traversal attack prevention
- Size validation before extraction
- Suspicious pattern detection

### Command Execution Infrastructure (command_executor.py)

The `command_executor.py` module provides secure command execution with comprehensive security measures:

**CommandValidator Class**:

- **Command Whitelist**: Only allows `python`, `python3`, `uv`, `pyright`, `pyright-python`
- **Argument Validation**:
  - Checks for dangerous characters (`;`, `|`, `&`, `$`, `` ` ``, `\n`, `\r`)
  - Validates argument length (max 4KB per argument)
  - Limits argument count (max 50 arguments)
- **Dangerous Pattern Detection**: Blocks patterns like:
  - `rm -rf`, `eval()`, `exec()`, `__import__`
  - `subprocess`, `os.system`
- **Path Traversal Prevention**: Detects and blocks `..` in paths
- **Sanitization**: Removes null bytes, trims whitespace

**CommandExecutor Class**:

- **Secure Execution**:
  - Uses `subprocess.run()` with `shell=False` to prevent injection
  - Never uses `shell=True` which would enable shell injection
- **Timeout Protection**:
  - Default timeout: 30 seconds
  - Maximum timeout: 300 seconds (5 minutes)
  - Raises `CommandTimeoutError` on timeout
- **Output Limits**:
  - Maximum output size: 10MB
  - Automatically truncated with notification
- **Working Directory Isolation**:
  - Validates working directories
  - Restricts to safe paths only
- **Audit Logging**:
  - Records all command executions
  - Includes timestamps and results
  - Logs to `mcp_server.log`

**Security Features**:

- ✅ Command whitelist enforcement
- ✅ No `shell=True` usage (prevents shell injection)
- ✅ Path traversal prevention
- ✅ Output size limits (prevents DoS)
- ✅ Timeout protection (prevents hanging)
- ✅ Dangerous pattern detection
- ✅ Comprehensive audit trail
- ✅ Working directory isolation

### Subagent AI Orchestration

The `subagent/` plugin provides advanced AI delegation capabilities:

**Supported Providers**:

- **OpenAI**: GPT-3.5-turbo, GPT-4, GPT-4-turbo, GPT-4o, GPT-4o-mini
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku), Claude 3.5 (Sonnet, Haiku)

**Key Features**:

- **Stateless Delegation**: Each call is independent, no session state
- **Parallel Execution**: Execute multiple subtasks concurrently with `subagent_parallel`
- **Conditional Branching**: Make decisions with `subagent_conditional`
- **Token Tracking**: Automatic token counting and cost calculation
- **Cost Estimation**: Real-time pricing for all supported models
- **Persistent Config**: Store API credentials in `~/.subagent_config.json`

**Available Tools**:

1. `subagent_call` - Delegate a single task to an AI model
2. `subagent_parallel` - Execute multiple tasks in parallel
3. `subagent_conditional` - Make decisions based on AI evaluation
4. `subagent_config_set` - Configure API credentials
5. `subagent_config_get` - Retrieve current configuration
6. `subagent_config_list` - List all configured providers

**Token Counter**:

- Character-based approximation algorithm
- CJK characters: ~2 chars per token
- Other characters: ~4 chars per token
- Supports all text encodings

**Model Pricing** (per 1K tokens):

```python
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    # ... and more
}
```

**Configuration**:

```bash
# Using the interactive wizard
uv run configure.py

# Or set manually via tool
subagent_config_set provider=openai api_key=sk-xxx base_url=https://api.openai.com
```

Configuration is stored at `~/.subagent_config.json` and persists between sessions.

### Configuration System

The project provides multiple configuration methods:

**1. Interactive Wizard (`configure.py`)**:

- Guided setup process
- Environment verification
- Dependency installation
- Subagent API configuration
- Claude Desktop integration
- Usage: `uv run configure.py`

**2. CLI Tools (`src/mcp_server/cli/config.py`)**:

- `--claude`: Auto-install to Claude Desktop config (merges with existing)
- `--http-server`: Run HTTP server with endpoints:
  - `/config` - Get MCP configuration JSON
  - `/info` - Get server information
  - `/health` - Health check endpoint
- `--output <file>`: Generate JSON config file
- `--show-config`: Display configuration in console

**3. Manual Configuration**:

- Edit `~/.subagent_config.json` for subagent settings
- Edit Claude Desktop config: `~/AppData/Roaming/Claude/claude_desktop_config.json` (Windows)
- Or: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

## Tool Categories Overview

### 1. Compression (compression/)

ZIP and TAR compression/extraction with security features:

- `compress_zip`, `extract_zip` - ZIP operations
- `compress_tar`, `extract_tar` - TAR operations
- `list_archive_contents` - View archive contents
- Security: ZIP bomb protection, path traversal prevention

### 2. Web & Network (web/)

Web interactions and network operations:

- `web_search`, `web_search_advanced`, `web_search_news` - DuckDuckGo search
- `fetch_webpage`, `fetch_webpage_text` - Fetch web content
- `parse_html` - HTML parsing with CSS selectors
- `download_file` - File downloads
- `get_page_title`, `get_page_links` - Page metadata extraction
- `check_url_status`, `get_headers` - HTTP status checks
- `validate_url_format`, `parse_url_components` - URL utilities
- `http_request` - Generic HTTP client (GET/POST/PUT/DELETE/PATCH)
- `get_network_info` - Network interface info
- `dns_lookup` - DNS record queries
- `clear_search_cache`, `get_search_stats` - Search cache management

### 3. File System (file/)

Complete file and directory management:

- `read_file`, `write_file`, `append_file` - File I/O
- `list_directory`, `create_directory` - Directory ops
- `copy_file`, `delete_file` - File management
- `search_files` - Glob pattern searching
- `diff_files`, `diff_text` - File/text comparison
- `get_file_info`, `file_exists` - Metadata

### 4. Data Processing (data/)

Parse and convert data formats:

- JSON: `parse_json`, `format_json`, `json_query`, `flatten_json`, `merge_json`
- CSV: `parse_csv`, `csv_to_json`, `json_to_csv`
- XML: `xml_to_json`
- YAML: `parse_yaml`, `yaml_to_json`, `json_to_yaml`
- TOML: `parse_toml`, `toml_to_json`
- Plus: `validate_json_schema`

### 5. Text Processing (text/)

Text manipulation and analysis:

- `text_summary` - Summarize/truncate text
- `regex_match`, `regex_replace` - Regex operations
- `extract_emails`, `extract_urls` - Pattern extraction
- `calculate_text_similarity` - Compare text similarity
- `encode_base64`, `decode_base64` - Base64 encoding/decoding
- `count_words` - Word and character counting

### 6. System (system/)

System monitoring and information:

- `get_system_info` - OS, CPU, memory info
- `get_cpu_info`, `get_memory_info`, `get_disk_info` - Resource monitoring
- `get_env_variable`, `list_env_variables` - Environment access
- `get_current_time` - Time information
- `get_process_info` - Current process info

### 7. Utilities (utility/)

General-purpose utilities:

- `generate_uuid`, `generate_random_string`, `generate_password` - Random generation
- `generate_hash` - MD5, SHA1, SHA256, SHA512 hashing
- `calculate_expression` - Math evaluation
- `check_password_strength` - Password analysis
- `timestamp_to_date`, `date_to_timestamp`, `calculate_date_diff`, `format_date` - Date/time operations

### 8. Subagent AI (subagent/)

AI task delegation and orchestration:

- `subagent_call` - Single task delegation
- `subagent_parallel` - Parallel task execution
- `subagent_conditional` - Conditional branching
- `subagent_config_set/get/list` - Configuration management
- Supports: OpenAI, Anthropic
- Features: Token tracking, cost estimation, persistent config

### 9. Browser Automation (browser/)

Selenium-based browser automation for AI-assisted web development:

**Session Management**:
- `browser_open` - Open browser and navigate to URL (Chrome/Edge, headless optional)
- `browser_close` - Close browser session
- `browser_list_sessions` - List all active browser sessions

**Navigation**:
- `browser_navigate` - Navigate to URL
- `browser_back`, `browser_forward` - History navigation
- `browser_refresh` - Refresh page

**Page Information**:
- `browser_get_page_source` - Get HTML source (with truncation)
- `browser_get_text` - Get element text content
- `browser_get_url` - Get current URL and title

**Element Interaction**:
- `browser_click` - Click element (with wait)
- `browser_type` - Type text into input
- `browser_select` - Select dropdown option
- `browser_wait_for` - Wait for element condition
- `browser_scroll` - Scroll page or to element

**Screenshots**:
- `browser_screenshot` - Capture viewport/element/full-page screenshot

**JavaScript**:
- `browser_execute_js` - Execute JavaScript in page context

**Console Logs**:
- `browser_get_console_logs` - Capture console.log/error/warn output

**Cookies**:
- `browser_get_cookies`, `browser_set_cookie`, `browser_delete_cookies` - Cookie CRUD

**Network Monitoring**:
- `browser_enable_network_log` - Start capturing network requests
- `browser_get_network_logs` - Get captured request/response logs

**Form Filling**:
- `browser_fill_form` - Fill multiple form fields at once (JSON input)

**Multi-Tab Management**:
- `browser_new_tab` - Open new tab
- `browser_switch_tab` - Switch to tab by index
- `browser_close_tab` - Close tab
- `browser_list_tabs` - List all tabs

**Element Query**:
- `browser_find_elements` - Find multiple elements
- `browser_get_element_attribute` - Get element attribute value

**Configuration Management**:
- `browser_config_get` - Get browser configuration settings (driver paths, defaults, proxy)
- `browser_config_set` - Set configuration and save to file (~/oh-my-mcp/browser_config.json)
- `browser_config_reset` - Reset configuration to defaults

**Configuration System**:
- Config file: `~/oh-my-mcp/browser_config.json` (auto-created)
- Priority: Environment variables > Config file > Auto-download
- Settings: driver paths, default browser, headless mode, proxy, auto-fallback
- Interactive wizard: `python examples/browser_config_wizard.py`

**Security Features**:
- URL scheme blocking (`file://`, `chrome://`, `javascript:`, etc.)
- Maximum 5 concurrent sessions
- Automatic session cleanup on exit
- Page load timeouts

**Driver Management**:
- Auto-fallback: Chrome → Edge when driver download fails (network issues)
- 3-strategy driver resolution: Custom path → Selenium Manager → webdriver-manager
- Environment variables: `CHROME_DRIVER_PATH`, `EDGE_DRIVER_PATH`, `HTTPS_PROXY`
- Useful in China/firewall environments where driver downloads may fail

## Adding New Tools

### To an existing category:

1. **Locate the plugin** in `src/mcp_server/tools/<category>/`
2. **Add the tool** in `handlers.py` using the `@tool_handler` decorator:
   ```python
   from mcp_server.tools.registry import tool_handler

   @tool_handler
   def new_tool_name(param: str) -> str:
       """Tool description."""
       try:
           result = {"status": "success", "data": "..."}
           return json.dumps(result)
       except Exception as e:
           logger.error(f"Tool failed: {e}")
           return json.dumps({"error": str(e)})
   ```
3. **Follow the error handling pattern** (try/except with logger.error)
4. **Return JSON strings** for structured data
5. **Test the tool** thoroughly

### To create a new category:

1. **Create plugin directory** `src/mcp_server/tools/new_category/`
2. **Create `__init__.py`** (empty file)
3. **Create `config.yaml`**:
   ```yaml
   category_name: "New Category"
   category_description: "Brief description"
   enabled: true
   ```
4. **Create `handlers.py`** with tool functions using `@tool_handler`
5. **No changes needed in `main.py`** — the plugin is auto-discovered!

## Key Dependencies

**Core Framework**:

- **fastmcp** (>=2.14.5) - MCP server framework and protocol implementation

**Web & Network**:

- **requests** (>=2.31.0) - HTTP operations
- **beautifulsoup4** (>=4.12.0) - HTML parsing
- **ddgs** (>=1.0.0) - DuckDuckGo search (no API key required)
- **lxml** (>=5.0.0) - XML/HTML processing

**System & Utilities**:

- **psutil** (>=5.9.0) - System monitoring and process management
- **python-dateutil** (>=2.8.2) - Date/time utilities

**Data Formats**:

- **pyyaml** (>=6.0) - YAML configuration and data support
- **tomli** (>=2.0.0, Python <3.11) - TOML parsing (Python 3.11+ uses built-in `tomllib`)

**Browser Automation**:

- **selenium** (>=4.15.0) - Browser automation framework
- **webdriver-manager** (>=4.0.0) - Automatic ChromeDriver/EdgeDriver management

**Build**:

- **pyinstaller** (>=6.18.0) - Executable packaging

**Development Tools** (optional):

- **pytest** (>=7.0) - Testing framework
- **pytest-cov** (>=4.0) - Code coverage
- **black** (>=23.0) - Code formatting
- **ruff** (>=0.1.0) - Linting
- **isort** (>=5.12.0) - Import sorting
- **mypy** (>=1.0.0) - Static type checking

All dependencies are automatically installed via `pip install -e .`

## MCP Resources

The server exposes the following MCP resources:

- **`config://tools`** - List all available tools organized by category
  - Returns JSON with complete tool catalog
  - Includes tool counts per category
  - Total tool count

- **`config://version`** - Server version and feature information
  - Server name and version
  - Total categories and tools
  - Feature descriptions

Access resources via MCP protocol from any MCP client.

## Logging

**Log Outputs**:

- **Console** (stdout) - Real-time logging during execution
- **File** (`mcp_server.log`) - Persistent log file in project root

**Log Configuration**:

- Default level: `INFO`
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Encoding: UTF-8
- Configured in `utils.py`

**Log Contents**:

- Server startup and initialization
- Tool registration and counts
- All tool executions and results
- Error messages with stack traces
- Command executions (audit trail)
- Network operations and retries
- Security validation events

**Accessing Logs**:

```python
from mcp_server.utils import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

## Development Guidelines

### Code Style

- Follow PEP 8 conventions
- Use type hints for function parameters and returns
- Maximum line length: 100 characters (configured in `pyproject.toml`)
- Use `black` for automatic formatting
- Use `ruff` for linting

### Error Handling Best Practices

1. **Use specific exceptions** from `utils.py`
2. **Always log errors** with `logger.error()`
3. **Return JSON error format**: `{"error": "Description"}`
4. **Include context** in error messages
5. **Don't expose sensitive data** in errors

Example:

```python
try:
    result = dangerous_operation()
    return json.dumps({"status": "success", "data": result})
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    return json.dumps({"error": f"Invalid input: {str(e)}"})
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return json.dumps({"error": "Internal server error"})
```

### Testing

- Write tests for all new tools in `tests/`
- Test both success and failure cases
- Use fixtures from `tests/fixtures/`
- Run tests: `pytest tests/`
- Check coverage: `pytest --cov=src/mcp_server tests/`

### Security Considerations

- ✅ Validate all user inputs
- ✅ Sanitize file paths
- ✅ Use command whitelisting
- ✅ Never use `shell=True` in subprocess
- ✅ Implement size limits
- ✅ Set timeouts on operations
- ✅ Check for path traversal
- ✅ Validate archive contents
- ✅ Filter sensitive data from logs

## Project Files

**Core Implementation**:

- `src/mcp_server/main.py` - Server entry point
- `src/mcp_server/utils.py` - Shared utilities and infrastructure
- `src/mcp_server/command_executor.py` - Secure command execution
- `src/mcp_server/tools/*/handlers.py` - Tool plugin handler modules
- `src/mcp_server/tools/registry.py` - Plugin registration framework
- `src/mcp_server/tools/search_engine.py` - Web search backend
- `src/mcp_server/tools/subagent_config.py` - Subagent credential manager

**Configuration**:

- `pyproject.toml` - Python project configuration and dependencies
- `pytest.ini` - pytest configuration
- `configure.py` - Interactive setup wizard
- `~/.subagent_config.json` - Subagent API credentials (user home)

**Documentation**:

- `README.md` - User-facing documentation
- `CLAUDE.md` - This file (developer guidance)
- `docs/en/ARCHITECTURE.md` - Architecture details
- `docs/en/PROJECT_STRUCTURE.md` - Project structure
- `docs/en/CHANGELOG.md` - Version history
- `docs/en/CONTRIBUTING.md` - Contribution guidelines
- `docs/en/BUILD.md` - Build guide
- `docs/en/INSTALLATION.md` - Installation guide
- `docs/zh/SETUP_GUIDE.md` - Setup wizard guide (Chinese)
- `docs/zh/SUBAGENT_GUIDE.md` - Subagent usage guide (Chinese)
- `docs/zh/SUBAGENT_CONFIG.md` - Subagent config guide (Chinese)
- `docs/zh/CONFIGURATION_GUIDE_CN.md` - Configuration guide (Chinese)
- `docs/zh/SEARCH_ADVANCED.md` - Advanced search (Chinese)

**Testing**:

- `tests/` - Test suite
- `tests/conftest.py` - pytest configuration and fixtures
- `tests/fixtures/` - Test data files
- `examples/` - Usage examples

**Build & Distribution**:

- `LICENSE` - MIT License
- `scripts/build/` - Build scripts (build.py, build.bat, build.sh)
- `oh-my-mcp.spec` - PyInstaller spec file

## Quick Reference

**Start Server**:

```bash
oh-my-mcp
# or
python -m mcp_server.main
```

**Configure**:

```bash
# Interactive wizard
uv run configure.py

# Claude Desktop auto-config
python -m mcp_server.cli.config --claude

# HTTP config server
python -m mcp_server.cli.config --http-server --port 8765
```

**Run Tests**:

```bash
pytest tests/
pytest --cov=src/mcp_server tests/  # with coverage
```

**Format Code**:

```bash
black src/ tests/
ruff check src/ tests/
isort src/ tests/
```

**View Tools**:

```bash
# Access config://tools resource via MCP client
# Or check README.md for tool listing
```

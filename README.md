# Comprehensive MCP Server

A powerful Model Context Protocol (MCP) server with **95+ practical tools** across 10 categories, built using [FastMCP](https://github.com/jlowin/fastmcp).

## 🚀 Features

This comprehensive MCP server provides tools for:

- **📦 Compression** (5 tools): ZIP/TAR compression and extraction with security features
- **🌐 Web & Network** (15 tools): Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup
- **📁 File System** (12 tools): Read, write, search files and directories, file comparison
- **📊 Data Processing** (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- **📝 Text Processing** (9 tools): Regex, encoding, email/URL extraction, text similarity
- **💻 System** (8 tools): System info, CPU/memory monitoring, environment variables
- **🛠️ Utilities** (10 tools): UUID, hashing, date/time operations, math, password generation
- **🐍 Python Development** (8 tools): Code execution, syntax validation, AST analysis, module introspection
- **📦 UV Package Manager** (9 tools): Fast package management, virtual environments, dependency management
- **🔍 Pylance/Pyright** (4 tools): Type checking, code analysis, diagnostics

### ⚡ Quick Configuration

**One-command setup for Claude Desktop:**

```bash
python generate_config.py --claude
```

**Or run an HTTP configuration server on port 8765:**

```bash
python generate_config.py --http-server
```

Access configuration at: `http://localhost:8765/config`

📖 **[中文配置指南 (Chinese Configuration Guide)](CONFIGURATION_GUIDE_CN.md)**

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Install

```bash
# Clone or navigate to the project directory
cd mcp-server

# Install the package in development mode
pip install -e .
```

This will install all dependencies including:

- FastMCP (MCP server framework)
- requests & beautifulsoup4 (web operations)
- duckduckgo-search (free web search)
- psutil (system monitoring)
- python-dateutil (date/time utilities)
- pyyaml (YAML configuration support)
- tomli (TOML configuration support, Python 3.11+ uses built-in tomllib)

## 🎯 Usage

### Quick Configuration Setup

The easiest way to configure MCP clients (like Claude Desktop):

#### Option 1: Automatic Installation (Recommended)

```bash
# Install configuration directly to Claude Desktop
python generate_config.py --claude
```

This will automatically:

- Detect your Claude Desktop configuration file
- Add the MCP server to your configuration
- Preserve any existing MCP servers

#### Option 2: HTTP Configuration Server

```bash
# Run a configuration server on port 8765
python generate_config.py --http-server

# With custom port
python generate_config.py --http-server --port 9000
```

Then access the configuration at:

- `http://localhost:8765/config` - Get configuration JSON
- `http://localhost:8765/info` - Server information
- `http://localhost:8765/health` - Health check

#### Option 3: Generate Configuration File

```bash
# Generate mcp_config.json
python generate_config.py

# Custom output file
python generate_config.py --output my_config.json

# Show configuration in console
python generate_config.py --show-config
```

### Manual Configuration

For Claude Desktop, add to your `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "comprehensive-mcp": {
      "command": "path/to/python.exe",
      "args": ["path/to/mcp-server/main.py"],
      "env": {},
      "description": "Comprehensive MCP Server with 74+ practical tools"
    }
  }
}
```

Use `python generate_config.py --show-config` to get the exact paths for your system.

### Start the Server Directly

```bash
python main.py
```

The server will start and register all 74+ tools, ready to accept MCP connections.

### Server Logs

Logs are written to:

- Console (stdout)
- `mcp_server.log` file

## 📚 Tool Catalog

### 📦 Compression Tools (5)

#### `compress_zip`

Create a ZIP archive from files.

```python
compress_zip(files=["file1.txt", "file2.txt"], output_path="archive.zip", compression_level=6)
# Returns: JSON with compression statistics (original size, compressed size, ratio)
```

#### `extract_zip`

Extract files from a ZIP archive with security checks.

```python
extract_zip(zip_path="archive.zip", extract_to="./extracted", password=None)
# Returns: JSON with list of extracted files
# Security: ZIP bomb protection, path traversal prevention
```

#### `compress_tar`

Create a TAR archive (optionally compressed with gzip or bzip2).

```python
compress_tar(files=["file1.txt", "file2.txt"], output_path="archive.tar.gz", compression="gz")
# Returns: JSON with compression statistics
# Compression options: "none", "gz", "bz2"
```

#### `extract_tar`

Extract files from a TAR archive.

```python
extract_tar(tar_path="archive.tar.gz", extract_to="./extracted")
# Returns: JSON with list of extracted files
```

#### `list_archive_contents`

List contents of a ZIP or TAR archive without extracting.

```python
list_archive_contents(archive_path="archive.zip")
# Returns: JSON with file list, sizes, and compression ratios
```

---

### 🌐 Web & Network Tools (15)

#### `web_search`

Search the web using DuckDuckGo (no API key required).

```python
# Example
web_search(query="Python tutorials", max_results=10)
# Returns: JSON with title, link, and snippet for each result
```

#### `fetch_webpage`

Fetch the HTML content of a webpage.

```python
fetch_webpage(url="https://example.com", timeout=10)
# Returns: HTML content
```

#### `fetch_webpage_text`

Extract clean text content from a webpage.

```python
fetch_webpage_text(url="https://example.com")
# Returns: Clean text without HTML tags
```

#### `parse_html`

Parse HTML using CSS selectors.

```python
parse_html(html="<div>...</div>", selector="div.content")
# Returns: JSON with matched elements
```

#### `download_file`

Download a file from URL.

```python
download_file(url="https://example.com/file.pdf", save_path="./file.pdf")
# Returns: Success message with file size
```

#### `get_page_title`

Extract the title from a webpage.

```python
get_page_title(url="https://example.com")
# Returns: Page title
```

#### `get_page_links`

Extract all links from a webpage.

```python
get_page_links(url="https://example.com", absolute=True)
# Returns: JSON with all links and their text
```

#### `check_url_status`

Check HTTP status of a URL.

```python
check_url_status(url="https://example.com")
# Returns: JSON with status code and accessibility
```

#### `get_headers`

Get HTTP headers from a URL.

```python
get_headers(url="https://example.com")
# Returns: JSON with all HTTP headers
```

#### `validate_url_format`

Validate URL format.

```python
validate_url_format(url="https://example.com")
# Returns: JSON with validation result and URL components
```

#### `parse_url_components`

Parse URL into components.

```python
parse_url_components(url="https://user:pass@example.com:8080/path?query=1#anchor")
# Returns: JSON with scheme, netloc, path, query, etc.
```

#### `web_search_news`

Search for news articles using DuckDuckGo News.

```python
web_search_news(query="technology", max_results=10)
# Returns: JSON with news articles
```

#### `http_request`

Generic REST API client for HTTP requests.

```python
http_request(url="https://api.example.com/data", method="GET", headers='{"Authorization": "Bearer token"}', body=None, timeout=10)
# Returns: JSON with status code, headers, and response body
# Supports: GET, POST, PUT, DELETE, PATCH
# Security: Response size limit (10MB), sensitive headers filtered
```

#### `get_network_info`

Get network interface information.

```python
get_network_info()
# Returns: JSON with network interfaces, IP addresses, MAC addresses
```

#### `dns_lookup`

Perform DNS lookup for a hostname.

```python
dns_lookup(hostname="example.com", record_type="A")
# Returns: JSON with DNS records
# Record types: A, AAAA, MX, NS, TXT
```

---

### 📁 File System Tools (10)

#### `read_file`

Read file contents with size limit (10MB max).

```python
read_file(path="./file.txt", encoding="utf-8")
# Returns: File contents
```

#### `write_file`

Write content to a file.

```python
write_file(path="./file.txt", content="Hello World", overwrite=True)
# Returns: Success message
```

#### `append_file`

Append content to a file.

```python
append_file(path="./file.txt", content="New line\n")
# Returns: Success message
```

#### `list_directory`

List directory contents with filtering.

```python
list_directory(path="./", pattern="*.py", recursive=False)
# Returns: JSON with files and directories
```

#### `file_exists`

Check if a file or directory exists.

```python
file_exists(path="./file.txt")
# Returns: JSON with existence status and type
```

#### `get_file_info`

Get detailed file metadata.

```python
get_file_info(path="./file.txt")
# Returns: JSON with size, dates, type, etc.
```

#### `search_files`

Search for files recursively.

```python
search_files(directory="./", pattern="*.py", name_contains="test")
# Returns: JSON with matching files
```

#### `create_directory`

Create a directory.

```python
create_directory(path="./new_dir", parents=True)
# Returns: Success message
```

#### `delete_file`

Delete a file (requires confirmation).

```python
delete_file(path="./file.txt", confirm=True)
# Returns: Success message
```

#### `copy_file`

Copy a file.

```python
copy_file(source="./file.txt", destination="./backup.txt", overwrite=False)
# Returns: Success message
```

#### `diff_files`

Compare two files and show differences.

```python
diff_files(file1="./old.txt", file2="./new.txt", context_lines=3, format="unified")
# Returns: JSON with diff output and statistics (lines added/removed)
# Formats: "unified", "context", "ndiff"
# File size limit: 10MB
```

#### `diff_text`

Compare two text strings and show differences.

```python
diff_text(text1="Hello World", text2="Hello Universe", format="unified")
# Returns: JSON with diff output and statistics
```

---

### 📊 Data Processing Tools (10)

#### `parse_json`

Parse and validate JSON.

```python
parse_json(json_string='{"key": "value"}')
# Returns: Formatted JSON
```

#### `format_json`

Format JSON with custom indentation.

```python
format_json(json_string='{"key":"value"}', indent=4, sort_keys=True)
# Returns: Formatted JSON
```

#### `json_query`

Extract value from JSON using dot notation.

```python
json_query(json_string='{"user":{"name":"John"}}', path="user.name")
# Returns: JSON with extracted value
```

#### `csv_to_json`

Convert CSV to JSON.

```python
csv_to_json(csv_string="name,age\nJohn,30", has_header=True)
# Returns: JSON array of objects
```

#### `json_to_csv`

Convert JSON array to CSV.

```python
json_to_csv(json_string='[{"name":"John","age":30}]')
# Returns: CSV string
```

#### `parse_csv`

Parse CSV data.

```python
parse_csv(csv_string="name,age\nJohn,30", delimiter=",")
# Returns: JSON with parsed data
```

#### `validate_json_schema`

Validate JSON structure.

```python
validate_json_schema(json_string='{"key": "value"}')
# Returns: JSON with validation result
```

#### `flatten_json`

Flatten nested JSON.

```python
flatten_json(json_string='{"a":{"b":{"c":1}}}', separator=".")
# Returns: Flattened JSON
```

#### `merge_json`

Merge two JSON objects.

```python
merge_json(json_string1='{"a":1}', json_string2='{"b":2}', deep=True)
# Returns: Merged JSON
```

#### `xml_to_json`

Convert XML to JSON.

```python
xml_to_json(xml_string='<root><item>value</item></root>')
# Returns: JSON representation
```

#### `parse_yaml`

Parse YAML string to JSON.

```python
parse_yaml(yaml_string='key: value\nlist:\n  - item1\n  - item2')
# Returns: JSON representation of YAML data
```

#### `yaml_to_json`

Convert YAML to formatted JSON.

```python
yaml_to_json(yaml_string='key: value', indent=2)
# Returns: Formatted JSON string
```

#### `json_to_yaml`

Convert JSON to YAML.

```python
json_to_yaml(json_string='{"key": "value", "list": [1, 2, 3]}')
# Returns: YAML string
```

#### `parse_toml`

Parse TOML configuration string.

```python
parse_toml(toml_string='[section]\nkey = "value"')
# Returns: JSON representation of TOML data
```

#### `toml_to_json`

Convert TOML to formatted JSON.

```python
toml_to_json(toml_string='[section]\nkey = "value"', indent=2)
# Returns: Formatted JSON string
```

---

### 📝 Text Processing Tools (8)

#### `count_words`

Count words and text statistics.

```python
count_words(text="Hello world", detailed=True)
# Returns: JSON with word count, characters, lines, etc.
```

#### `extract_emails`

Extract email addresses from text.

```python
extract_emails(text="Contact: john@example.com or jane@example.com")
# Returns: JSON with list of emails
```

#### `extract_urls`

Extract URLs from text.

```python
extract_urls(text="Visit https://example.com for more info")
# Returns: JSON with list of URLs
```

#### `regex_match`

Find regex matches in text.

```python
regex_match(text="Hello World", pattern=r"\w+", flags="i")
# Returns: JSON with all matches
```

#### `regex_replace`

Replace text using regex.

```python
regex_replace(text="Hello World", pattern=r"World", replacement="Universe")
# Returns: Modified text
```

#### `text_summary`

Summarize or truncate text.

```python
text_summary(text="Long text...", max_length=100, method="truncate")
# Returns: Summarized text
```

#### `encode_base64`

Encode text to Base64.

```python
encode_base64(text="Hello World", encoding="utf-8")
# Returns: Base64 encoded string
```

#### `decode_base64`

Decode Base64 to text.

```python
decode_base64(encoded="SGVsbG8gV29ybGQ=", encoding="utf-8")
# Returns: Decoded text
```

#### `calculate_text_similarity`

Calculate similarity between two text strings.

```python
calculate_text_similarity(text1="Hello World", text2="Hello Universe", method="levenshtein")
# Returns: JSON with similarity score (0-1), distance, and method info
# Methods: "levenshtein" (edit distance), "jaccard" (set-based similarity)
# Performance: Long texts truncated to 10000 characters
```

---

### 💻 System Tools (8)

#### `get_system_info`

Get comprehensive system information.

```python
get_system_info()
# Returns: JSON with OS, platform, Python version, etc.
```

#### `get_cpu_info`

Get CPU information and usage.

```python
get_cpu_info()
# Returns: JSON with CPU usage, cores, frequency
```

#### `get_memory_info`

Get memory (RAM) usage statistics.

```python
get_memory_info()
# Returns: JSON with memory usage details
```

#### `get_disk_info`

Get disk space information.

```python
get_disk_info(path="/")
# Returns: JSON with disk usage and partitions
```

#### `get_env_variable`

Get environment variable value.

```python
get_env_variable(name="PATH", default="")
# Returns: JSON with variable value
```

#### `list_env_variables`

List all environment variables.

```python
list_env_variables(filter_pattern="PYTHON")
# Returns: JSON with filtered env variables (sensitive values masked)
```

#### `get_current_time`

Get current date and time.

```python
get_current_time(timezone="local", format="iso")
# Returns: JSON with time in multiple formats
```

#### `get_process_info`

Get current process information.

```python
get_process_info()
# Returns: JSON with PID, memory, CPU usage, etc.
```

---

### 🛠️ Utility Tools (8)

#### `generate_uuid`

Generate a UUID.

```python
generate_uuid(version=4, uppercase=False)
# Returns: UUID string
```

#### `generate_hash`

Generate hash of text.

```python
generate_hash(text="Hello World", algorithm="sha256")
# Returns: JSON with hash
```

#### `timestamp_to_date`

Convert Unix timestamp to date.

```python
timestamp_to_date(timestamp=1234567890, format="iso", timezone="local")
# Returns: JSON with formatted date
```

#### `date_to_timestamp`

Convert date string to timestamp.

```python
date_to_timestamp(date_string="2024-01-01 12:00:00")
# Returns: JSON with Unix timestamp
```

#### `calculate_date_diff`

Calculate difference between two dates.

```python
calculate_date_diff(date1="2024-01-01", date2="2024-12-31", unit="days")
# Returns: JSON with difference in various units
```

#### `format_date`

Format date with custom pattern.

```python
format_date(date_string="2024-01-01", format="%B %d, %Y")
# Returns: JSON with formatted date
```

#### `calculate_expression`

Safely evaluate mathematical expressions.

```python
calculate_expression(expression="2 + 2 * 3")
# Returns: JSON with result (8)
```

#### `generate_random_string`

Generate random string.

```python
generate_random_string(length=16, charset="alphanumeric")
# Returns: JSON with random string
```

#### `generate_password`

Generate a cryptographically secure password.

```python
generate_password(length=16, include_symbols=True, include_numbers=True, exclude_ambiguous=True)
# Returns: JSON with password and strength score
# Security: Uses secrets module for cryptographic randomness
# Options: Exclude ambiguous characters (0/O, 1/l/I)
```

#### `check_password_strength`

Check password strength and get recommendations.

```python
check_password_strength(password="MyP@ssw0rd123")
# Returns: JSON with strength score (0-100), level, issues, and recommendations
# Checks: Length, complexity, common passwords, repeated/sequential characters
```

---

## 📖 Resources

### `config://tools`

List all available tools organized by category.

### `config://version`

Get server version and feature information.

### `system://info`

Real-time system information.

### `system://stats`

Real-time system statistics (CPU, memory, disk).

---

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
mcp-server/
├── main.py                      # Entry point
├── pyproject.toml               # Dependencies
├── README.md                    # Documentation
├── mcp_server/
│   ├── __init__.py              # Package init
│   ├── utils.py                 # Infrastructure & utilities
│   ├── compression_tools.py     # Compression tools (ZIP, TAR)
│   ├── web_tools.py             # Web & network tools
│   ├── file_tools.py            # File system tools
│   ├── data_tools.py            # Data processing tools
│   ├── text_tools.py            # Text processing tools
│   ├── system_tools.py          # System tools
│   └── utility_tools.py         # Utility tools
└── mcp_server.log               # Log file (generated)
```

### Adding New Tools

Create a new tool in the appropriate module:

```python
@mcp.tool()
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

## 🎉 Quick Start

```bash
# 1. Install dependencies
pip install -e .

# 2. Auto-configure for Claude Desktop
python generate_config.py --claude

# 3. Restart Claude Desktop and start using the tools!
```

**Alternative: Run with HTTP configuration server**

```bash
# Generate configuration via HTTP
python generate_config.py --http-server --port 8765
```

**Or start the MCP server directly:**

```bash
python main.py
```

The server provides 74+ tools across 7 categories! Check the logs for startup confirmation.

---

## 🔧 Configuration Management

### Configuration Generator Tool

The `generate_config.py` script provides multiple ways to configure MCP clients:

```bash
# Quick install to Claude Desktop
python generate_config.py --claude

# Run HTTP server on custom port
python generate_config.py --http-server --port 9000

# Generate config file with custom server name
python generate_config.py --server-name my-tools --output config.json

# Show configuration in console
python generate_config.py --show-config
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
python generate_config.py --http-server

# Get configuration
curl http://localhost:8765/config

# Get server info
curl http://localhost:8765/info
```

---

Enjoy your comprehensive MCP server! 🚀

# MCP Server - Usage Guide | 使用指南

## Quick Start | 快速开始

### 1. Extract the Archive | 解压文件

**Windows:**

```powershell
Expand-Archive -Path mcp-server-windows-x64.zip -DestinationPath C:\mcp-server
```

**Linux/macOS:**

```bash
tar -xzf mcp-server-*.tar.gz
cd mcp-server
```

### 2. Verify Installation | 验证安装

Run the executable to ensure it works:

**Windows:**

```powershell
cd C:\mcp-server\mcp-server
.\mcp-server.exe
```

**Linux/macOS:**

```bash
cd mcp-server
./mcp-server
```

You should see the MCP server start and display available tools.

## Available Tools | 可用工具

This MCP server includes tools across multiple categories. Ask your AI assistant *"What MCP tools are available?"* to see the full list.
本 MCP 服务器包含多个类别的工具。向你的 AI 助手提问 *"有哪些可用的 MCP 工具？"* 查看完整列表。

### 📁 File Operations | 文件操作

- Read, write, append, delete files
- File information and existence checks
- Directory operations
- File comparison

### 🗜️ Compression | 压缩操作

- Create and extract TAR archives
- Create and extract ZIP archives
- List archive contents

### 📊 Data Processing | 数据处理

- JSON: parse, validate, merge, extract
- CSV: convert to/from JSON
- XML: convert to JSON
- YAML: convert to/from JSON
- TOML: convert to JSON

### 📝 Text Processing | 文本处理

- Word count, regex, text similarity
- Base64 encoding/decoding
- URL and email extraction

### 🌐 Web Operations | Web操作

- HTTP requests (GET, POST, PUT, DELETE)
- Web scraping and HTML parsing
- URL validation and DNS lookup
- Web search via DuckDuckGo

### 💻 System Monitoring | 系统监控

- CPU, memory, disk, process info
- Network statistics
- Environment variables and uptime

### 🔧 Utility Tools | 实用工具

- UUID, hash, password generation
- Date/time and timestamp operations
- Mathematical expression evaluation

### 🤖 Subagent | 子代理

- AI task delegation to OpenAI and Anthropic
- Parallel and conditional task execution
- Token usage tracking

## Configuration | 配置

This MCP server can be used with multiple MCP-compatible clients:

### Claude Desktop

**Configuration File Location:**

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**Configuration Example:**

Windows:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "C:\\mcp-server\\mcp-server\\mcp-server.exe"
    }
  }
}
```

macOS/Linux:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/absolute/path/to/mcp-server/mcp-server"
    }
  }
}
```

**Important:** Always use absolute paths to the executable!

**Restart:** After updating configuration, completely quit (Cmd+Q on macOS, Exit from system tray on Windows) and restart Claude Desktop.

### Claude Code (VS Code / CLI)

The fastest way is via CLI:
最快的方式是通过命令行：

```bash
# Add this server | 添加此服务器
claude mcp add mcp-server /absolute/path/to/mcp-server/mcp-server

# Windows example | Windows 示例
claude mcp add mcp-server C:\mcp-server\mcp-server\mcp-server.exe

# Verify | 验证
claude mcp list
```

Or edit VS Code `settings.json`:
或编辑 VS Code `settings.json`：

```json
{
  "claude.mcpServers": {
    "mcp-server": {
      "command": "/absolute/path/to/mcp-server/mcp-server"
    }
  }
}
```

### Cursor

Edit `~/.cursor/mcp.json` (global) or `<project>/.cursor/mcp.json` (project-level):
编辑 `~/.cursor/mcp.json`（全局）或 `<project>/.cursor/mcp.json`（项目级）：

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/absolute/path/to/mcp-server/mcp-server"
    }
  }
}
```

Windows:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "C:\\mcp-server\\mcp-server\\mcp-server.exe"
    }
  }
}
```

**Restart:** After saving, restart Cursor to apply changes.
**重启：** 保存后重启 Cursor 以生效。

### ccswitch (MCP Server Manager)

[ccswitch](https://github.com/modelcontextprotocol/ccswitch) is a convenient tool for managing multiple MCP servers:

**Installation:**

```bash
npm install -g ccswitch
```

**Add this server:**

```bash
ccswitch add mcp-server /path/to/mcp-server/mcp-server
```

**Switch between servers:**

```bash
ccswitch use mcp-server
```

**List all servers:**

```bash
ccswitch list
```

### Other MCP Clients

This server follows the [Model Context Protocol](https://modelcontextprotocol.io/) specification and should work with any MCP-compatible client. Generally, you'll need to:

1. Provide the path to the executable
2. Configure any required environment variables (if applicable)
3. Restart the client application

## FAQ | 常见问题

### Q: How do I verify the MCP server is working?

**A:** In your MCP client (Claude Desktop, Claude Code, etc.), ask: "What MCP tools are available?" or "List all available MCP server tools". The response should include tools from this server.

### Q: Why are Python/UV/Pylance tools not available?

**A:** These tools have been removed because they require external Python interpreters and package managers that are not bundled with the executable. All remaining tools work completely standalone without any external dependencies.

### Q: Can I run multiple MCP servers simultaneously?

**A:** Yes! Most MCP clients support multiple servers. Add each server with a unique name in the configuration file. For Claude Desktop:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/path/to/mcp-server/mcp-server"
    },
    "another-server": {
      "command": "/path/to/another-server"
    }
  }
}
```

### Q: How do I update to a new version?

**A:**

1. Download the new release from GitHub
2. Extract to a new directory (or replace the old one)
3. Update the path in your MCP client configuration if changed
4. Restart your MCP client

### Q: The server isn't showing up in my client

**A:** Check these common issues:

- Verify the path to the executable is absolute and correct
- Ensure the executable has execute permissions (Linux/macOS: `chmod +x mcp-server`)
- Check if your MCP client requires a restart after configuration changes
- Look for error messages in your client's logs

### Q: Where can I get help?

**A:**

1. Check the [Documentation](https://github.com/quyansiyuanwang/mcp-server/tree/main/docs)
2. Search [existing issues](https://github.com/quyansiyuanwang/mcp-server/issues)
3. Create a new [Bug Report](https://github.com/quyansiyuanwang/mcp-server/issues/new?template=bug_report.yml)

## Advanced Usage | 高级用法

### Command Line Arguments

The server supports various command-line arguments for advanced configuration:

```bash
# Show help
./mcp-server --help

# Run with custom configuration
./mcp-server --config /path/to/config.json

# Enable debug logging
./mcp-server --debug
```

### Environment Variables

Configure behavior using environment variables:

- `MCP_SERVER_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_SERVER_PORT`: Custom port (if applicable)
- `OPENAI_API_KEY`: OpenAI API key for subagent tools
- `ANTHROPIC_API_KEY`: Anthropic API key for subagent tools

### Using with Development Tools

For development and testing, you can run the server from Python source:

```bash
# Activate your Python environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows

# Run from source
python -m mcp_server.main
```

## Support | 支持

- **Documentation:** [Project Documentation](https://github.com/quyansiyuanwang/mcp-server/tree/main/docs)
- **Issues:** [GitHub Issues](https://github.com/quyansiyuanwang/mcp-server/issues)
- **Discussions:** [GitHub Discussions](https://github.com/quyansiyuanwang/mcp-server/discussions)
- **MCP Specification:** [Model Context Protocol](https://modelcontextprotocol.io/)

## License | 许可证

This project is licensed under the MIT License.

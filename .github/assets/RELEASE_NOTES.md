## Oh My MCP Release {{VERSION}}

### 📦 Available Downloads | 可用下载

Choose the appropriate package for your platform:
为您的平台选择合适的包：

- **Windows (x64)**: `oh-my-mcp-windows-x64.zip`
- **Linux (x64)**: `oh-my-mcp-linux-x64.tar.gz`
- **macOS (Intel)**: `oh-my-mcp-macos-x64.tar.gz`
- **macOS (Apple Silicon)**: `oh-my-mcp-macos-arm64.tar.gz`

Each package includes:
每个包包含：
- Pre-built executable | 预构建的可执行文件
- USAGE.md with setup instructions | 包含设置说明的USAGE.md

### ✨ Features | 功能

This release includes **{{TOTAL_TOOLS}} tools** across {{TOTAL_CATEGORIES}} categories:
此版本包含{{TOTAL_CATEGORIES}}个类别的**{{TOTAL_TOOLS}}个工具**：
{{TOOL_LINES}}

### 🚀 Quick Start | 快速开始

#### 1. Download & Extract | 下载解压

Download the package for your platform and extract it:
下载适合您平台的包并解压：

**Windows:**
```powershell
Expand-Archive -Path oh-my-mcp-windows-x64.zip -DestinationPath C:\oh-my-mcp
```

**Linux/macOS:**
```bash
tar -xzf oh-my-mcp-*.tar.gz
```

#### 2. Configure MCP Client | 配置 MCP 客户端

<details>
<summary><b>Claude Desktop</b></summary>

Edit your config file (create if not exists):
编辑配置文件（不存在则创建）：

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**Windows example:**
```json
{
  "mcpServers": {
    "oh-my-mcp": {
      "command": "C:\\oh-my-mcp\\oh-my-mcp\\oh-my-mcp.exe"
    }
  }
}
```

**macOS/Linux example:**
```json
{
  "mcpServers": {
    "oh-my-mcp": {
      "command": "/path/to/oh-my-mcp/oh-my-mcp"
    }
  }
}
```

> ⚠️ Use **absolute paths** only. After saving, fully quit and restart Claude Desktop.
> ⚠️ 必须使用**绝对路径**。保存后完全退出并重启 Claude Desktop。

</details>

<details>
<summary><b>Claude Code (VS Code / CLI)</b></summary>

```bash
claude mcp add oh-my-mcp /absolute/path/to/oh-my-mcp/oh-my-mcp
```

Or add to VS Code `settings.json`:
或添加到 VS Code `settings.json`：

```json
{
  "claude.mcpServers": {
    "oh-my-mcp": {
      "command": "/absolute/path/to/oh-my-mcp/oh-my-mcp"
    }
  }
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

Edit `~/.cursor/mcp.json` (global) or `<project>/.cursor/mcp.json` (project-level):
编辑 `~/.cursor/mcp.json`（全局）或 `<project>/.cursor/mcp.json`（项目级）：

```json
{
  "mcpServers": {
    "oh-my-mcp": {
      "command": "/absolute/path/to/oh-my-mcp/oh-my-mcp"
    }
  }
}
```

</details>

<details>
<summary><b>Other MCP Clients | 其他客户端</b></summary>

Any MCP-compatible client can use this server. You typically need to provide the **absolute path** to the executable as the `command` field.
任何兼容 MCP 的客户端都可以使用此服务器，只需将可执行文件的**绝对路径**作为 `command` 字段。

</details>

#### 3. Verify | 验证

Ask your AI assistant: *"What MCP tools are available?"*
向你的 AI 助手提问：*"有哪些可用的 MCP 工具？"*

### 📚 Documentation | 文档

- [Complete Documentation]({{REPO_URL}}/tree/main/docs)
- [Build Guide]({{REPO_URL}}/blob/main/docs/BUILD.md)
- [Architecture]({{REPO_URL}}/blob/main/docs/ARCHITECTURE.md)

### 🐛 Bug Reports | Bug报告

Found an issue? Please [create a bug report]({{REPO_URL}}/issues/new?template=bug_report.yml).
发现问题？请[创建bug报告]({{REPO_URL}}/issues/new?template=bug_report.yml)。
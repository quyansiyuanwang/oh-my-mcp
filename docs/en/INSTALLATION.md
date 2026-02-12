# 安装指南

本指南将帮助您安装和配置 MCP Server。

## 系统要求

- Python 3.12 或更高版本
- pip 或 UV 包管理器
- 操作系统：Windows、macOS 或 Linux

## 安装方法

### 方法 1：使用 pip（推荐）

```bash
# 从 PyPI 安装（发布后）
pip install mcp-server

# 或从源码安装
git clone https://github.com/quyansiyuanwang/mcp-server.git
cd mcp-server
pip install -e .
```

### 方法 2：使用 UV（更快）

```bash
# 克隆仓库
git clone https://github.com/quyansiyuanwang/mcp-server.git
cd mcp-server

# 使用 UV 安装
uv pip install -e .
```

## 验证安装

安装完成后，验证是否成功：

```bash
# 检查版本
python -c "import mcp_server; print(mcp_server.__version__)"

# 运行服务器
mcp-server
```

## 配置 Claude Desktop

### 自动配置（推荐）

```bash
python -m mcp_server.cli.config --claude
```

这将自动将 MCP Server 添加到 Claude Desktop 配置中。

### 手动配置

编辑 Claude Desktop 配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加以下内容：

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server.main"]
    }
  }
}
```

## 开发环境安装

如果您想参与开发：

```bash
# 克隆仓库
git clone https://github.com/quyansiyuanwang/mcp-server.git
cd mcp-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/
```

## 故障排除

### 导入错误

如果遇到导入错误，确保：

1. Python 版本 >= 3.12
2. 所有依赖已安装：`pip install -e .`

### 权限问题

在 Linux/macOS 上，可能需要使用 `sudo` 或虚拟环境。

### 依赖冲突

使用虚拟环境隔离依赖：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install mcp-server
```

## 下一步

- 查看[示例代码](../../examples/)学习常见用例
- 阅读[设置指南](../zh/SETUP_GUIDE.md)了解配置向导
- 参考[架构文档](ARCHITECTURE.md)了解系统设计

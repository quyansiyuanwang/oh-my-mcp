# MCP 服务器快速配置指南

[English](CONFIGURATION.md) | 中文

## 🚀 三种快速配置方法

### 方法 1：自动安装到 Claude Desktop（推荐）⭐

这是最简单的方法，一键配置：

```bash
python -m mcp_server.cli.config --claude
```

**功能：**

- ✓ 自动检测 Claude Desktop 配置文件位置
- ✓ 自动添加 MCP 服务器配置
- ✓ 保留现有的其他 MCP 服务器
- ✓ 自动创建目录（如果不存在）

**配置文件位置：**

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

**使用后：**
重启 Claude Desktop，MCP 服务器就可以使用了！

---

### 方法 2：HTTP 配置服务器 🌐

启动一个简单的 HTTP 服务器，提供配置信息：

```bash
# 在端口 8765 上启动服务器
python -m mcp_server.cli.config --http-server

# 或使用自定义端口
python -m mcp_server.cli.config --http-server --port 9000
```

**可用端点：**

| 端点          | 功能                 | 示例                                |
| ------------- | -------------------- | ----------------------------------- |
| `GET /config` | 获取 MCP 配置 JSON   | `curl http://localhost:8765/config` |
| `GET /info`   | 获取服务器信息和路径 | `curl http://localhost:8765/info`   |
| `GET /health` | 健康检查             | `curl http://localhost:8765/health` |

**使用场景：**

- 需要通过 HTTP 动态获取配置
- 在多台机器上共享配置
- 与配置管理工具集成

**示例：**

```bash
# 启动服务器
python -m mcp_server.cli.config --http-server --port 8765

# 获取配置（在另一个终端）
curl http://localhost:8765/config

# 或在浏览器中访问
# http://localhost:8765/config
```

---

### 方法 3：生成配置文件 📄

生成标准的 JSON 配置文件：

```bash
# 生成默认配置文件 mcp_config.json
python -m mcp_server.cli.config

# 自定义输出文件名
python -m mcp_server.cli.config --output my_config.json

# 在终端显示配置
python -m mcp_server.cli.config --show-config

# 自定义服务器名称
python -m mcp_server.cli.config --server-name my-mcp-tools --output config.json
```

**生成的配置示例：**

```json
{
  "mcpServers": {
    "oh-my-mcp": {
      "command": "D:\\path\\to\\python.exe",
      "args": ["-m", "mcp_server.main"],
      "env": {},
      "description": "oh-my-mcp - MCP Server with 154 practical tools"
    }
  }
}
```

**使用配置文件：**

1. 复制生成的配置内容
2. 添加到你的 MCP 客户端配置文件中
3. 重启客户端应用

---

## 📋 完整使用流程

### 1. 基本安装

```bash
# 克隆或进入项目目录
cd oh-my-mcp

# 安装依赖
pip install -e .
```

### 2. 快速配置（选择一种方法）

```bash
# 方法 1：一键安装到 Claude Desktop
python -m mcp_server.cli.config --claude

# 方法 2：启动 HTTP 配置服务器
python -m mcp_server.cli.config --http-server --port 8765

# 方法 3：生成配置文件
python -m mcp_server.cli.config --show-config
```

### 3. 启动服务器（如果需要测试）

```bash
# 直接运行 MCP 服务器
python -m mcp_server.main
```

---

## 🔧 高级选项

### 命令行参数

```bash
python -m mcp_server.cli.config [选项]

选项：
  --server-name NAME    自定义服务器名称（默认：oh-my-mcp）
  --output FILE, -o     输出文件路径（默认：mcp_config.json）
  --claude              安装到 Claude Desktop 配置
  --http-server         运行 HTTP 配置服务器
  --port PORT           HTTP 服务器端口（默认：8765）
  --show-config         在终端显示配置
  --help, -h            显示帮助信息
```

### 组合使用

```bash
# 生成配置并显示
python -m mcp_server.cli.config --output config.json --show-config

# 使用自定义服务器名称安装到 Claude
python -m mcp_server.cli.config --server-name my-tools --claude

# 在特定端口运行配置服务器
python -m mcp_server.cli.config --http-server --port 9999
```

---

## 🎯 配置验证

### 验证配置是否正确

```bash
# 1. 生成配置并查看
python -m mcp_server.cli.config --show-config

# 2. 检查 Python 和服务器路径
curl http://localhost:8765/info  # 如果运行了 HTTP 服务器

# 3. 测试服务器启动
python -m mcp_server.main
```

### 预期输出

成功启动后，你应该看到：

```
============================================================
Starting oh-my-mcp v0.1.0
============================================================
Registering Web & Network tools...
Registering File System tools...
Registering Data Processing tools...
Registering Text Processing tools...
Registering System tools...
Registering Utility tools...
============================================================
All tools and resources registered successfully!
Server ready to accept connections.
============================================================
```

---

## 🛠️ 故障排除

### 问题：找不到 Claude Desktop 配置

**解决方案：**

```bash
# 手动生成配置
python -m mcp_server.cli.config --show-config

# 复制输出，手动添加到 Claude Desktop 配置文件
```

### 问题：端口被占用

**解决方案：**

```bash
# 使用不同端口
python -m mcp_server.cli.config --http-server --port 9000
```

### 问题：Python 路径不正确

**解决方案：**

```bash
# 配置文件会自动检测当前虚拟环境的 Python 路径
# 如果需要手动修改，编辑生成的 JSON 文件中的 "command" 字段
```

---

## 📚 相关文档

- [完整功能文档](../README.md) - 查看所有 154 个工具的详细说明
- [MCP 协议文档](https://modelcontextprotocol.io/) - 了解 MCP 协议
- [Claude Desktop](https://claude.ai/download) - 下载 Claude Desktop

---

## ✨ 总结

**最快开始方式：**

```bash
# 1. 安装
pip install -e .

# 2. 配置
python -m mcp_server.cli.config --claude

# 3. 重启 Claude Desktop
# 完成！开始使用 154 个工具！
```

**HTTP 服务器方式：**

```bash
# 1. 启动配置服务器
python -m mcp_server.cli.config --http-server --port 8765

# 2. 访问 http://localhost:8765/config 获取配置
# 3. 将配置添加到你的 MCP 客户端
```

享受使用功能丰富的 MCP 服务器！🎉

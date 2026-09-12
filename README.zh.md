# oh-my-mcp

中文 | [English](README.md)

一个功能强大的模型上下文协议(MCP)服务器,内置 **151 个实用工具**、覆盖
**11 个类别**,基于 [FastMCP](https://github.com/jlowin/fastmcp) 构建。

[![Build and Release](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/build-release.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/build-release.yml)
[![Tests](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/tests.yml)
[![Lint](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/lint.yml/badge.svg)](https://github.com/quyansiyuanwang/oh-my-mcp/actions/workflows/lint.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/quyansiyuanwang/oh-my-mcp)

## 🚀 功能概览

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

> 完整的中文文档索引见 **[docs/README.zh.md](docs/README.zh.md)**——
> 每个主题均有中英两个版本(英文 `X.md` 为默认,中文统一 `X.zh.md`)。

## 📦 安装

```bash
git clone https://github.com/quyansiyuanwang/oh-my-mcp.git
cd oh-my-mcp
pip install -e .            # 或:uv sync --all-extras
```

## ⚡ 快速配置

```bash
# 交互式配置向导(推荐)
uv run configure.py

# 直接为 Claude Desktop 安装配置
python -m mcp_server.cli.config --claude

# 启动 HTTP 配置服务
python -m mcp_server.cli.config --http-server --port 8765
```

详细说明见:[安装指南](docs/INSTALLATION.zh.md) 与
[配置向导指南](docs/SETUP_GUIDE.zh.md)。

## ▶️ 启动服务

```bash
python -m mcp_server.main
```

启动后可通过 Claude Desktop 或任意 MCP 客户端连接使用。

## 📚 文档

| 文档 | 链接 |
|---|---|
| 工具参考(全部 146 个工具) | [TOOL_REFERENCE.zh.md](docs/TOOL_REFERENCE.zh.md) |
| 桌面控制指南 | [COMPUTER_USE_GUIDE.zh.md](docs/COMPUTER_USE_GUIDE.zh.md) |
| Subagent 指南 | [SUBAGENT_GUIDE.zh.md](docs/SUBAGENT_GUIDE.zh.md) |
| 构建指南 | [BUILD.zh.md](docs/BUILD.zh.md) |
| 架构概述 | [ARCHITECTURE.zh.md](docs/ARCHITECTURE.zh.md) |
| 更新日志 | [CHANGELOG.zh.md](docs/CHANGELOG.zh.md) |

## 🛡️ 安全特性

- **路径校验**:防止路径遍历攻击
- **安全求值**:数学表达式仅允许白名单操作
- **脱敏输出**:敏感环境变量自动掩码
- **确认删除**:删除文件需要 `confirm=True`
- **白名单执行**:命令需显式信任后才能运行
- **重试逻辑**:网络操作最多自动重试 3 次

## 📝 开发

工具数量与描述由 `scripts/docs/generate_docs.py` 从代码生成(AST 解析
`@tool_handler` docstring + 各插件 `config.yaml`)。增删工具后运行:

```bash
python scripts/docs/generate_docs.py --write
```

CI 使用 `--check` 校验文档是否最新。生成内容位于
`<!-- DOCGEN:...:start/end -->` 标记之间,请勿手改。

贡献指南见 [CONTRIBUTING.zh.md](docs/CONTRIBUTING.zh.md)。

## 📄 许可证

本项目按"原样"提供,供教育与实用用途。

---

Enjoy oh-my-mcp! 🚀
